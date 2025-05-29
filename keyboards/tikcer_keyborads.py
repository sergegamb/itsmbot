from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_ticket_actions(ticket_id: int):
    keyboard = [
        [InlineKeyboardButton("Взять в работу", callback_data=f'ticket_action:{ticket_id}:assign')],
        [InlineKeyboardButton("Закрыть", callback_data=f'ticket_action:{ticket_id}:close')]
    ]
    return InlineKeyboardMarkup(keyboard)
