import logging

from services import ticket_service
from telegram.ext import ConversationHandler
from handlers.auth_decorators import registered_user_required, roles_required
# from database.session import SessionLocal # Больше не нужно здесь, если декоратор управляет сессией
# from database import crud                 # Аналогично
# from database.models import User          # Аналогично

# Define states for the conversation
TITLE, DESCRIPTION = range(2)

async def create_ticket(update, context):
    """Starts the conversation and asks for the ticket title."""
    user = update.message.from_user
    await update.message.reply_text("Введите заголовок тикета:")
    return TITLE

async def handle_ticket_title(update, context):
    """Stores the title and asks for the description."""
    title = update.message.text
    context.user_data['ticket_title'] = title
    await update.message.reply_text("Опишите проблему:")
    return DESCRIPTION

@registered_user_required # Применяем декоратор
async def handle_ticket_description(update, context):
    """Stores the description, creates the ticket, and ends the conversation."""
    description = update.message.text
    db_user = context.user_data.get('db_user') # Получаем пользователя из декоратора
    db = context.user_data.get('db_session')   # Получаем сессию из декоратора
    
    if not db_user or not db: # Дополнительная проверка, хотя декоратор должен это обеспечить
        logging.error("User or DB session not found in context after decorator.")
        await update.message.reply_text("Произошла системная ошибка. Попробуйте позже.")
        return ConversationHandler.END
    try:
        # Сохраняем тикет в БД, passing the session and internal user ID
        ticket = ticket_service.create_ticket(
            db=db,
            user_id=db_user.id, # Use the internal ID from the users table
            title=context.user_data['ticket_title'],
            description=description
        )
        
        # Сброс состояния
        context.user_data.clear()
        await update.message.reply_text(f"Тикет #{ticket.id} создан!")
        return ConversationHandler.END
    except Exception as e:
        logging.error(f"Error creating ticket: {e}")
        await update.message.reply_text("Произошла ошибка при создании тикета. Попробуйте позже.")
        return ConversationHandler.END # Or another appropriate state
    # finally: # Блок finally теперь в декораторе
        # db.close() # Сессия закрывается в декораторе

async def cancel_ticket_creation(update, context):
    """Cancels the ticket creation process."""
    context.user_data.clear()
    await update.message.reply_text("Создание тикета отменено.")
    return ConversationHandler.END

@registered_user_required
async def list_my_tickets(update, context):
    """Lists all tickets created by the user."""
    db_user = context.user_data.get('db_user')
    db = context.user_data.get('db_session')

    if not db_user or not db:
        logging.error("User or DB session not found in context for list_my_tickets.")
        await update.message.reply_text("Произошла системная ошибка. Попробуйте позже.")
        return

    try:
        user_tickets = ticket_service.get_tickets_by_user_id(db, user_id=db_user.id)
        if not user_tickets:
            await update.message.reply_text("У вас пока нет созданных тикетов.")
            return

        message = "Ваши тикеты:\n"
        for ticket in user_tickets:
            message += f"\nID: {ticket.id} - {ticket.title} (Статус: {ticket.status})"
        await update.message.reply_text(message)
    except Exception as e:
        logging.error(f"Error listing tickets for user {db_user.id}: {e}")
        await update.message.reply_text("Произошла ошибка при получении списка ваших тикетов.")


@registered_user_required
@roles_required(['admin', 'support'])
async def list_all_tickets(update, context):
    """Lists all tickets in the system (for admin/support users)."""
    db_user = context.user_data.get('db_user') # For logging or context, though not strictly needed for query
    db = context.user_data.get('db_session')

    if not db: # db_user is checked by roles_required
        logging.error("DB session not found in context for list_all_tickets.")
        await update.message.reply_text("Произошла системная ошибка. Попробуйте позже.")
        return

    try:
        all_tickets = ticket_service.get_all_tickets_service(db) # We'll add this to ticket_service
        if not all_tickets:
            await update.message.reply_text("В системе пока нет тикетов.")
            return

        message = "Все тикеты в системе:\n"
        for ticket in all_tickets:
            message += f"\nID: {ticket.id} - {ticket.title} (Статус: {ticket.status}, Пользователь ID: {ticket.user_id})"
        await update.message.reply_text(message)
    except Exception as e:
        logging.error(f"Error listing all tickets by admin {db_user.username if db_user else 'Unknown'}: {e}")
        await update.message.reply_text("Произошла ошибка при получении списка всех тикетов.")
