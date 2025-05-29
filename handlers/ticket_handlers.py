import logging

from services import ticket_service
from telegram.ext import ConversationHandler
from database.session import SessionLocal # To create a DB session
from database import crud                 # For user CRUD operations
from database.models import User          # To create User model instance

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

async def handle_ticket_description(update, context):
    """Stores the description, creates the ticket, and ends the conversation."""
    description = update.message.text
    telegram_user_id = update.message.from_user.id

    db = SessionLocal()
    try:
        # Get or create the user in the database
        db_user = crud.get_user_by_telegram_id(db, telegram_id=telegram_user_id)
        if not db_user:
            # If user doesn't exist, create a new one.
            # Adjust role or other fields as necessary for your application logic.
            new_user_data = User(telegram_id=telegram_user_id, role='user')
            db_user = crud.create_user(db, user=new_user_data)

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
    finally:
        db.close() # Always close the session

async def cancel_ticket_creation(update, context):
    """Cancels the ticket creation process."""
    context.user_data.clear()
    await update.message.reply_text("Создание тикета отменено.")
    return ConversationHandler.END
