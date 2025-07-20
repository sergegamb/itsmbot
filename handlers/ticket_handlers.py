import logging

from services import ticket_service, ticket_web_service
from telegram.ext import ConversationHandler
from handlers.auth_decorators import registered_user_required, roles_required
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config.settings import TICKETS_PER_PAGE


TITLE, DESCRIPTION = range(2)


async def create_ticket(update, context):
    user = update.message.from_user
    await update.message.reply_text("Введите заголовок тикета:")
    return TITLE


async def handle_ticket_title(update, context):
    title = update.message.text
    context.user_data['ticket_title'] = title
    await update.message.reply_text("Опишите проблему:")
    return DESCRIPTION


@registered_user_required
async def handle_ticket_description(update, context):
    description = update.message.text
    db_user = context.user_data.get('db_user')
    db = context.user_data.get('db_session')
    
    if not db_user or not db:
        logging.error("User or DB session not found in context after decorator.")
        await update.message.reply_text("Произошла системная ошибка. Попробуйте позже.")
        return ConversationHandler.END
    try:
        ticket = ticket_service.create_ticket(
            db=db,
            user_id=db_user.id,
            title=context.user_data['ticket_title'],
            description=description
        )
        context.user_data.clear()
        await update.message.reply_text(f"Тикет #{ticket.id} создан!")
        return ConversationHandler.END
    except Exception as e:
        logging.error(f"Error creating ticket: {e}")
        await update.message.reply_text("Произошла ошибка при создании тикета. Попробуйте позже.")
        return ConversationHandler.END


async def cancel_ticket_creation(update, context):
    context.user_data.clear()
    await update.message.reply_text("Создание тикета отменено.")
    return ConversationHandler.END


async def display_ticket_details(update, context, ticket_id: int, origin: str, page: int):
    """Displays ticket details and a back button."""
    db = context.user_data.get('db_session')
    ticket = ticket_web_service.get_ticket_by_id(ticket_id)

    if not ticket:
        await update.callback_query.answer("Тикет не найден.", show_alert=True)
        return

    text = f"Тикет #{ticket.id}\nЗаголовок: {ticket.subject}\nОписание: {ticket.description}\nСтатус: {ticket.status.name}"
    keyboard = [[InlineKeyboardButton("Назад к списку", callback_data=f"list_tickets:{origin}:{page}")]]
    await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))


async def _list_tickets_paginated(
    update, context, page: int, db_user, db,
    fetch_tickets_callable,
    callback_origin_slug: str, base_message_text: str,
    no_items_message: str, error_message_text: str,
    log_identifier: str
):
    """Helper function to display a paginated list of tickets."""
    query = update.callback_query
    if query:
        await query.answer()

    try:
        skip = page * TICKETS_PER_PAGE
        tickets_response = await fetch_tickets_callable(skip=skip, limit=TICKETS_PER_PAGE)
        tickets_on_page = tickets_response[2]
        total_tickets = tickets_response[1].get('total_count', 1000)

        if total_tickets == 0:
            if query:
                await query.edit_message_text(text=no_items_message)
            else:
                await update.message.reply_text(no_items_message)
            return

        keyboard_buttons = []
        for ticket in tickets_on_page:
            keyboard_buttons.append([InlineKeyboardButton(
                f"#{ticket.id} - {ticket.subject} ({ticket.status.name})",
                callback_data=f"view_ticket:{ticket.id}:{callback_origin_slug}:{page}"
            )])

        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(
                "⬅️ Пред.", callback_data=f"list_tickets:{callback_origin_slug}:{page-1}"
            ))
        if (page + 1) * TICKETS_PER_PAGE < total_tickets:
            nav_buttons.append(InlineKeyboardButton(
                "След. ➡️", callback_data=f"list_tickets:{callback_origin_slug}:{page+1}"
            ))

        if nav_buttons:
            keyboard_buttons.append(nav_buttons)

        reply_markup = InlineKeyboardMarkup(keyboard_buttons)
        message_text_with_page = f"{base_message_text} (Страница {page + 1} из {(total_tickets + TICKETS_PER_PAGE - 1) // TICKETS_PER_PAGE}):"

        if query:
            await query.edit_message_text(text=message_text_with_page, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text=message_text_with_page, reply_markup=reply_markup)

    except Exception as e:
        logging.error(f"Error listing tickets for {log_identifier}: {e}")
        if query:
            await query.edit_message_text(text=error_message_text)
        else:
            await update.message.reply_text(error_message_text)


@registered_user_required
async def list_my_tickets(update, context, page: int = 0):
    db_user = context.user_data.get('db_user')
    db = context.user_data.get('db_session')

    if not db_user or not db:
        logging.error("User or DB session not found in context for list_my_tickets.")
        await update.message.reply_text("Произошла системная ошибка. Попробуйте позже.")
        return

    async def fetch_user_tickets(skip, limit):
        return ticket_web_service.get_tickets_by_technician_id(technician_id=db_user.technician_id, skip=skip, limit=limit)

    await _list_tickets_paginated(
        update, context, page,
        db_user=db_user, db=db,
        fetch_tickets_callable=fetch_user_tickets,
        callback_origin_slug="my",
        base_message_text="Ваши тикеты",
        no_items_message="У вас пока нет созданных тикетов.",
        error_message_text="Произошла ошибка при получении списка ваших тикетов.",
        log_identifier=f"user {db_user.id}"
    )

@registered_user_required
@roles_required(['admin', 'support'])
async def list_all_tickets(update, context, page: int = 0):
    db_user = context.user_data.get('db_user')
    db = context.user_data.get('db_session')
    # db_user is retrieved here primarily for consistent logging in the helper,
    # even though it's not strictly needed for fetching all tickets.

    if not db:
        logging.error("DB session not found in context for list_all_tickets.")
        await update.message.reply_text("Произошла системная ошибка. Попробуйте позже.")
        return

    async def fetch_all_system_tickets(skip, limit):
        return ticket_web_service.get_all_tickets_service(skip=skip, limit=limit)

    await _list_tickets_paginated(
        update, context, page,
        db_user=db_user, db=db,
        fetch_tickets_callable=fetch_all_system_tickets,
        callback_origin_slug="all",
        base_message_text="Все тикеты в системе",
        no_items_message="В системе пока нет тикетов.",
        error_message_text="Произошла ошибка при получении списка всех тикетов.",
        log_identifier=f"admin/support user {db_user.username if db_user else 'Unknown'}"
    )