import logging
import os
import json
import joblib
import pandas as pd
from dotenv import load_dotenv
from telegram import (
    Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, ContextTypes, MessageHandler, 
    filters, CallbackQueryHandler, ConversationHandler
)
from telegram.constants import ParseMode
from src.core.data_loader import UniversityDataManager
from src.core.recommender import UniversityRecommender
from src.core.career_data import CAREER_PATHS

# --- Basic Setup ---
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

# --- URLs from Environment ---
BASE_URL = os.getenv("GITHUB_PAGES_URL")
QUIZ_WEB_APP_URL = f"{BASE_URL}/static/quiz/index.html"
BROWSER_WEB_APP_URL = f"{BASE_URL}/static/browser/index.html"
CALCULATOR_WEB_APP_URL = f"{BASE_URL}/static/calculator/index.html"

# --- HELPER FUNCTIONS ---

def build_main_menu_keyboard():
    """Creates the main menu with correct Khmer text."""
    keyboard = [
        [InlineKeyboardButton("🧬 វិភាគ DNA និស្សិត", callback_data='analyze')],
        [InlineKeyboardButton("📚 កាតាឡុកសាកលវិទ្យាល័យ", callback_data='browse')],
        [InlineKeyboardButton("🚀 ស្វែងយល់ពីអាជីព", callback_data='career_start')],
        [InlineKeyboardButton("💰 អ្នកគណនាថ្លៃសិក្សា", callback_data='calculator')],
    ]
    return InlineKeyboardMarkup(keyboard)

def format_university_details(uni: dict) -> str:
    """Helper function to format a university object into a nice string."""
    details = []
    details.append(f"*{uni['name_km']}* ({uni['name_en']})")
    details.append(f"📍 *ទីតាំង:* {uni['location']}")
    details.append(f"🏛️ *ប្រភេទ:* {uni['type']}")
    details.append(f"💰 *តម្លៃសិក្សា:* ${uni['tuition_fees']['range_min']} - ${uni['tuition_fees']['range_max']} /ឆ្នាំ")
    details.append(f"📞 *ទំនាក់ទំនង:* {', '.join(uni['contact']['phones'])}")
    details.append(f"🌐 *គេហទំព័រ:* {uni['contact']['website']}")
    return "\n".join(details)


# --- MAIN HANDLER FUNCTIONS ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the main menu hub."""
    user = update.effective_user
    logger.info(f"User {user.first_name} started the bot.")
    await update.message.reply_text("សូមស្វាគមន៍!", reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text(
        text="នេះគឺជាផ្ទាំងគ្រប់គ្រងរបស់អ្នក។\n\n**សូមជ្រើសរើសឧបករណ៍៖**",
        reply_markup=build_main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def all_button_press_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """A single, robust router for ALL button presses."""
    query = update.callback_query
    await query.answer()
    
    choice = query.data

    # --- Router Logic ---
    if choice in ['analyze', 'browse', 'calculator']:
        web_app_map = {
            'analyze': ('🔬 បើកការវិភាគ', QUIZ_WEB_APP_URL),
            'browse': ('📚 បើកកាតាឡុក', BROWSER_WEB_APP_URL),
            'calculator': ('💰 បើកការគណនា', CALCULATOR_WEB_APP_URL),
        }
        button_text, url = web_app_map[choice]
        await query.message.reply_text(
            "ចុចប៊ូតុងខាងក្រោមដើម្បីបើក៖",
            reply_markup=ReplyKeyboardMarkup.from_button(
                KeyboardButton(text=button_text, web_app=WebAppInfo(url=url)),
                resize_keyboard=True
            )
        )
    elif choice == 'career_start':
        major_keys = list(CAREER_PATHS.keys())
        keyboard = [[InlineKeyboardButton(major, callback_data=f"career_show:{major}")] for major in major_keys]
        await query.message.reply_text("សូមជ្រើសរើសវិស័យដែលអ្នកចាប់អារម្មណ៍៖", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif choice.startswith('career_show:'):
        selected_major = choice.split(':')[1]
        career_info = CAREER_PATHS.get(selected_major, {})
        if career_info:
            # Format the career path text...
            response_text = "..." # Formatted career info text goes here
            await query.message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)
        else:
            await query.message.reply_text("មិនមានព័ត៌មានទេ។")


async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """The router for data coming from ANY Web App."""
    data_str = update.message.web_app_data.data
    logger.info(f"Received Web App data: {data_str}")
    
    try:
        data = json.loads(data_str)
        source = data.get('source')
        if source == 'catalog':
            # Handle catalog selection
            uni_id = data.get('university_id')
            data_manager = context.bot_data['data_manager']
            university = data_manager.get_university_by_id(uni_id)
            if university:
                await update.message.reply_text(format_university_details(university), parse_mode=ParseMode.MARKDOWN, reply_markup=ReplyKeyboardRemove())
        else:
            # Handle quiz results
            # The full quiz processing logic goes here...
            await update.message.reply_text("...Processing quiz results...", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        logger.error(f"Error processing Web App data: {e}")
        await update.message.reply_text("មានបញ្ហាក្នុងការដំណើរការข้อមูល។")


def main() -> None:
    """Builds and runs the bot application."""
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN or not BASE_URL:
        logger.critical("FATAL: Environment variables (TOKEN, GITHUB_PAGES_URL) not set.")
        return

    application = Application.builder().token(TOKEN).build()
    
    # --- Initialize Services ---
    try:
        data_manager = UniversityDataManager(data_path='data/data.json')
        application.bot_data['data_manager'] = data_manager
        application.bot_data['recommender'] = UniversityRecommender(data_manager=data_manager)
        model_artifact = joblib.load('src/core/ml_models/admission_model.pkl')
        application.bot_data['ml_model'] = model_artifact['model']
        application.bot_data['model_columns'] = model_artifact['columns']
        logger.info("All services initialized successfully.")
    except Exception as e:
        logger.critical(f"FATAL: Failed to initialize a service. Error: {e}")
        return
    
    # --- Final, Simplified Handler Registration ---
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))
    # This ONE handler will now manage ALL button presses.
    application.add_handler(CallbackQueryHandler(all_button_press_router))
    
    logger.info("--- Starting Bot (Definitive Build) ---")
    application.run_polling()

if __name__ == "__main__":
    main() 