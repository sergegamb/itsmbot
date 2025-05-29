from services import ticket_service

async def handle_button_press(update, context):
    query = update.callback_query
    data = query.data
    
    if data.startswith('ticket_action'):
        ticket_id = int(data.split(':')[1])
        action = data.split(':')[2]
        
        if action == 'close':
            ticket_service.close_ticket(ticket_id) # Assuming close_ticket exists in ticket_service
            await query.edit_message_text(text=f"Тикет #{ticket_id} закрыт")