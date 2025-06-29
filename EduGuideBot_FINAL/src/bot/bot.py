import os
import logging
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ConversationHandler, MessageHandler, filters
)
from dotenv import load_dotenv

from src.bot.handlers import (
    start, location_choice, budget_input,
    major_field_choice, career_goal_choice, english_proficiency_choice,
    confirm_info, cancel, LOCATION, BUDGET, MAJOR_FIELD,
    CAREER_GOAL, ENGLISH_PROFICIENCY, CONFIRM_INFO
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Get logger for this module
logger = logging.getLogger(__name__)

def setup_bot():
    """Setup and return the Telegram bot application"""
    # Load environment variables
    load_dotenv()
    
    # Get the token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        raise ValueError("No token provided. Set the TELEGRAM_BOT_TOKEN environment variable.")
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LOCATION: [CallbackQueryHandler(location_choice)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, budget_input)],
            MAJOR_FIELD: [CallbackQueryHandler(major_field_choice)],
            CAREER_GOAL: [CallbackQueryHandler(career_goal_choice)],
            ENGLISH_PROFICIENCY: [CallbackQueryHandler(english_proficiency_choice)],
            CONFIRM_INFO: [CallbackQueryHandler(confirm_info)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    
    return application

def run_bot():
    """Run the bot"""
    application = setup_bot()
    
    logger.info("EduGuideBot is starting up...")
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=["message", "callback_query"])
    
    logger.info("EduGuideBot has been stopped.")

if __name__ == "__main__":
    run_bot() 