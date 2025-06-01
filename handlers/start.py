import logging
from handlers.auth_decorators import registered_user_required

@registered_user_required
async def handle_start(update, context):
    """Handles the /start command, registers the user if not already registered."""
    db_user = context.user_data.get('db_user') # Получаем пользователя из context, установленного декоратором
    
    if update.callback_query: # Если это результат нажатия кнопки, например
        await update.callback_query.answer() # Отвечаем на callback, чтобы убрать "часики"
        await update.callback_query.message.reply_text(f"С возвращением, {db_user.username}! Ваша роль: {db_user.role}.")
    else:
        await update.message.reply_text(f"С возвращением, {db_user.username}! Ваша роль: {db_user.role}.")
