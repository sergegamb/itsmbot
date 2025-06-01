import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from database.session import SessionLocal
from database import crud
from database.models import User

def registered_user_required(func):
    """
    Decorator to ensure the user is registered in the system.
    If not registered, it creates a new user with 'user' role.
    Injects `db_user: User` and `db: Session` into `context.user_data`.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        telegram_user = update.effective_user
        if not telegram_user:
            # Should not happen in normal command/message handlers
            logging.warning("No effective_user found in update.")
            await update.effective_message.reply_text("Не удалось идентифицировать пользователя.")
            return

        telegram_id = telegram_user.id
        username = telegram_user.username or f"User{telegram_id}"

        db = SessionLocal()
        try:
            db_user = crud.get_user_by_telegram_id(db, telegram_id=telegram_id)
            if not db_user:
                new_user_data = User(telegram_id=telegram_id, username=username, role='user')
                db_user = crud.create_user(db, user=new_user_data)
                logging.info(f"Auto-registered new user: {db_user.username} (ID: {db_user.telegram_id}) with role {db_user.role}")
            
            context.user_data['db_user'] = db_user
            context.user_data['db_session'] = db # Pass the session for the handler to use

            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logging.error(f"Error in registered_user_required decorator for user {telegram_id}: {e}")
            await update.effective_message.reply_text("Произошла ошибка при проверке пользователя. Пожалуйста, попробуйте позже.")
        finally:
            if 'db_session' in context.user_data: # Ensure session is closed if it was opened
                context.user_data['db_session'].close()
                del context.user_data['db_session'] # Clean up
                if 'db_user' in context.user_data: # Clean up db_user as well
                    del context.user_data['db_user']
    return wrapper


def roles_required(allowed_roles: list[str]):
    """
    Decorator to ensure the user has one of the allowed roles.
    Must be used AFTER @registered_user_required or ensure db_user is in context.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            db_user = context.user_data.get('db_user')

            if not db_user:
                logging.error("roles_required: db_user not found in context. Ensure @registered_user_required is used first.")
                await update.effective_message.reply_text("Ошибка проверки прав: пользователь не идентифицирован.")
                return

            if db_user.role not in allowed_roles:
                logging.warning(f"User {db_user.username} (Role: {db_user.role}) attempted action requiring roles: {allowed_roles}")
                await update.effective_message.reply_text("У вас недостаточно прав для выполнения этого действия.")
                return
            
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator
