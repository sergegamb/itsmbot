import logging
from services import ticket_service
from handlers.ticket_handlers import display_ticket_details, list_my_tickets, list_all_tickets
from handlers.auth_decorators import registered_user_required

@registered_user_required # Ensure db_user and db_session are in context
async def handle_button_press(update, context):
    query = update.callback_query
    await query.answer() # Answer callback query quickly
    data = query.data
    
    # Example: ticket_action:TICKET_ID:ACTION (e.g., ticket_action:123:close)
    # Example: view_ticket:TICKET_ID:ORIGIN:PAGE (e.g., view_ticket:123:my:7 or view_ticket:123:all:8)
    # Example: list_tickets:ORIGIN:PAGE (e.g., list_tickets:my:0 or list_tickets:all:1)

    parts = data.split(':')
    action_type = parts[0]

    if action_type == 'ticket_action':
        # This part remains for other ticket actions like 'close'
        ticket_id = int(data.split(':')[1])
        action = data.split(':')[2]
        
        if action == 'close':
            ticket_service.close_ticket(ticket_id) # Assuming close_ticket exists in ticket_service
            await query.edit_message_text(text=f"Тикет #{ticket_id} закрыт")
    elif action_type == 'view_ticket':
        # Format: view_ticket:TICKET_ID:ORIGIN:PAGE
        ticket_id = int(parts[1])
        origin = parts[2]  # 'my' or 'all'
        page = int(parts[3])
        await display_ticket_details(update, context, ticket_id, origin, page)
    elif action_type == 'list_tickets':  #TODO: убрать вложенное ветвление
        if len(parts) == 3: # Format: list_tickets:ORIGIN:PAGE
            origin = parts[1]
            page = int(parts[2])
            if origin == 'my':
                await list_my_tickets(update, context, page=page)
            elif origin == 'all':
                await list_all_tickets(update, context, page=page)
        else: # Fallback for old format or initial call (page 0)
            logging.warning(f"Legacy or malformed list_tickets callback: {data}. Assuming page 0.")
            # This part might need adjustment based on how initial list commands are triggered
            # If /listmytickets or /listalltickets are commands, they will call with page=0 by default.
            # This 'else' might be for unexpected callback data.
            await query.message.reply_text("Ошибка навигации по списку.")
    else:
        logging.warning(f"Unhandled callback data: {data}")
        await query.message.reply_text("Неизвестное действие.")