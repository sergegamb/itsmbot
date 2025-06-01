from telegram.ext import Application
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler
from telegram.ext import filters
from config.settings import BOT_TOKEN
from handlers import start, ticket_handlers, callback_handlers

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler for creating tickets
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("newticket", ticket_handlers.create_ticket)],
        states={
            ticket_handlers.TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_handlers.handle_ticket_title)],
            ticket_handlers.DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ticket_handlers.handle_ticket_description)],
        },
        fallbacks=[CommandHandler("cancel", ticket_handlers.cancel_ticket_creation)],
    )
    
    app.add_handler(conv_handler)
    
    # Регистрация других обработчиков команд
    app.add_handler(CommandHandler("start", start.handle_start))
    # app.add_handler(CommandHandler("newticket", ticket_handlers.create_ticket)) # Removed, as it's now an entry point for ConversationHandler
    app.add_handler(CommandHandler("mytickets", ticket_handlers.list_my_tickets))
    app.add_handler(CommandHandler("alltickets", ticket_handlers.list_all_tickets))

    # Регистрация обработчиков кнопок
    app.add_handler(CallbackQueryHandler(callback_handlers.handle_button_press))
    
    # Запуск бота
    app.run_polling()

if __name__ == "__main__":
    main()