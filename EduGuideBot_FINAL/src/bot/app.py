import logging
import os
import json
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

# --- FINAL URL FIX ---
# This new structure correctly accounts for the "double folder" problem on GitHub Pages.
BASE_URL = os.getenv("GITHUB_PAGES_URL", "https://your-github-username.github.io")
PROJECT_FOLDER_NAME = "EduGuideBot_FINAL" # The name of the root folder you uploaded

QUIZ_WEB_APP_URL = f"{BASE_URL}/{PROJECT_FOLDER_NAME}/static/quiz/index.html"
BROWSER_WEB_APP_URL = f"{BASE_URL}/{PROJECT_FOLDER_NAME}/static/browser/index.html"
CALCULATOR_WEB_APP_URL = f"{BASE_URL}/{PROJECT_FOLDER_NAME}/static/calculator/index.html"

# --- State for Career Planner Conversation ---
SELECTING_CAREER_MAJOR = 0

# --- Utility Functions ---
def format_university_details(uni: dict) -> str:
    """Formats university details into a readable string."""
    details = f"🏫 *{uni.get('name_km', uni.get('name_en'))} ({uni.get('name_en', '')})*\n"
    details += f"📍 _{uni.get('location', 'N/A')}_\n\n"
    details += f"• *ប្រភេទ:* {uni.get('type', 'N/A')}\n"
    details += f"• *ឆ្នាំបង្កើត:* {uni.get('established_year', 'N/A')}\n"
    
    tuition = uni.get('tuition_fees', {})
    details += f"• *ថ្លៃសិក្សា:* ${tuition.get('range_min', 'N/A')} - ${tuition.get('range_max', 'N/A')} /ឆ្នាំ\n"
    
    if uni.get('faculties'):
        details += "\n*មហាវិទ្យាល័យសំខាន់ៗ:*\n"
        for faculty in uni['faculties'][:3]:
            details += f"- {faculty.get('name_km', 'N/A')}\n"
    
    contact = uni.get('contact', {})
    if contact:
        details += "\n*ទំនាក់ទំនង:*\n"
        if contact.get('website'):
            details += f"  - [គេហទំព័រ]({contact['website']})\n"
        if contact.get('phones'):
            details += f"  - ទូរស័ព្ទ: {', '.join(contact['phones'])}\n"
    
    return details

# --- Main Command and Button Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends the main menu."""
    keyboard = [
        [InlineKeyboardButton("🧬 វិភាគ DNA និស្សិត", callback_data='analyze')],
        [InlineKeyboardButton("📚 កាតាឡុកសាកលវិទ្យាល័យ", callback_data='browse')],
        [InlineKeyboardButton("🚀 ស្វែងយល់ពីអាជីព", callback_data='career')],
        [InlineKeyboardButton("💰 អ្នកគណនាថ្លៃសិក្សា", callback_data='calculator')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # If the command is triggered via a message, reply. Otherwise, if from a callback, edit.
    if update.message:
        await update.message.reply_text("សូមស្វាគមន៍!", reply_markup=ReplyKeyboardRemove())
        await update.message.reply_text(
            "នេះគឺជាផ្ទាំងគ្រប់គ្រងរបស់អ្នក។\n\n**សូមជ្រើសរើសឧបករណ៍៖**",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "នេះគឺជាផ្ទាំងគ្រប់គ្រងរបស់អ្នក។\n\n**សូមជ្រើសរើសឧបករណ៍៖**",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

async def launch_web_app(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles inline button presses to launch web apps."""
    query = update.callback_query
    if not query:
        return
    await query.answer()
    choice = query.data
    url = ""
    button_text = ""

    if choice == 'analyze':
        url = QUIZ_WEB_APP_URL
        button_text = "🔬 បើកការវិភាគ"
    elif choice == 'browse':
        url = BROWSER_WEB_APP_URL
        button_text = "📚 បើកកាតាឡុក"
    elif choice == 'calculator':
        url = CALCULATOR_WEB_APP_URL
        button_text = "💰 បើកការគណនា"

    if url and button_text and query.message:
        await query.message.reply_text(
            text="ចុចប៊ូតុងខាងក្រោមដើម្បីបើក៖",
            reply_markup=ReplyKeyboardMarkup.from_button(
                KeyboardButton(text=button_text, web_app=WebAppInfo(url=url)),
                resize_keyboard=True
            )
        )

# --- Career Planner Conversation Handlers ---

async def plan_career_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the career planning conversation."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END
        
    await query.answer()
    keyboard = [
        [InlineKeyboardButton(key, callback_data=f'career:{key}')] for key in CAREER_PATHS.keys()
    ]
    keyboard.append([InlineKeyboardButton("« ត្រលប់ទៅមឺនុយមេ", callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "សូមជ្រើសរើសវិស័យអាជីពដែលអ្នកចាប់អារម្មណ៍ដើម្បីស្វែងយល់បន្ថែម៖",
        reply_markup=reply_markup
    )
    return SELECTING_CAREER_MAJOR

async def show_career_path(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows details for a selected career path."""
    query = update.callback_query
    if not query or not query.data:
        return SELECTING_CAREER_MAJOR
        
    await query.answer()
    field = query.data.split(':', 1)[1]
    path_info = CAREER_PATHS.get(field)
    
    if not path_info:
        await query.edit_message_text("ขออภัย ไม่พบข้อมูลสำหรับสายอาชีพนี้")
        return SELECTING_CAREER_MAJOR

    text = f"*{path_info['title']}*\n\n"
    for level in ['entry_level', 'mid_level', 'senior_level']:
        text += f"*{path_info[level]['title']}:*\n"
        text += f"  - *តួនាទី:* {path_info[level]['roles']}\n"
        text += f"  - *ប្រាក់ខែ:* {path_info[level]['salary']}\n\n"
    text += f"Trend: _{path_info['future_trend']}_"

    keyboard = [[InlineKeyboardButton("« ត្រលប់ទៅការជ្រើសរើសអាជីព", callback_data='career')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    return SELECTING_CAREER_MAJOR

# --- Web App Data Handler ---

async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles data received from the web apps."""
    if not update.message or not update.message.web_app_data:
        return
    data = json.loads(update.message.web_app_data.data)
    action = data.get('action')

    if action == 'university_recommendations':
        await handle_quiz_results(update, context, data)
    elif action == 'share_university':
        await handle_catalog_selection(update, context, data)
    elif action == 'share_calculation':
        await handle_calculator_results(update, context, data)

async def handle_quiz_results(update: Update, context: ContextTypes.DEFAULT_TYPE, data: dict):
    """Processes recommendations from the quiz."""
    user_profile = data.get('user_profile')
    if not user_profile or not update.message: return
    
    await update.message.reply_text("ទទួលបានចម្លើយរបស់អ្នក! កំពុងដំណើរការអនុសាសន៍...", reply_markup=ReplyKeyboardRemove())
    
    recommender: UniversityRecommender = context.bot_data['recommender']
    recommendations = recommender.recommend(user_profile, top_n=3)
    
    if not recommendations:
        await update.message.reply_text("ขออภัย ไม่พบมหาวิทยาลัยที่ตรงกับเกณฑ์ของคุณ ลองปรับเปลี่ยนเกณฑ์ของคุณดู")
        return
        
    response = "🎉 *នេះគឺជាអនុសាសន៍កំពូលទាំង 3 សម្រាប់អ្នក:*\n\n"
    for i, rec in enumerate(recommendations):
        uni = rec['university']
        response += f"*{i+1}. {uni.get('name_km', uni.get('name_en'))}*\n"
        response += f"  - ពិន្ទុត្រូវគ្នា: {rec['total_score']}\n"
        response += f"  - ទីតាំង: {uni.get('location', 'N/A')}\n"
        tuition = uni.get('tuition_fees', {})
        response += f"  - ថ្លៃសិក្សា: ${tuition.get('range_min', 'N/A')} - ${tuition.get('range_max', 'N/A')}\n\n"

    response += "អ្នកអាចស្វែងរកព័ត៌មានបន្ថែមនៅក្នុង *កាតាឡុកសាកលវិទ្យាល័យ*។"
    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

async def handle_catalog_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, data: dict):
    """Handles a university shared from the catalog web app."""
    uni_id = data.get('id')
    if not uni_id or not update.message: return
    
    data_manager: UniversityDataManager = context.bot_data['data_manager']
    university = data_manager.get_university_by_id(uni_id)
    
    if not university: return
    
    details = format_university_details(university)
    await update.message.reply_text(details, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

async def handle_calculator_results(update: Update, context: ContextTypes.DEFAULT_TYPE, data: dict):
    """Handles calculation results shared from the calculator web app."""
    if not update.message: return
    response = "📊 *លទ្ធផលគណនាថ្លៃសិក្សា:*\n\n"
    response += f"• *សាកលវិទ្យាល័យ:* {data.get('university_name', 'N/A')}\n"
    response += f"• *ជំនាញ:* {data.get('major', 'N/A')}\n"
    response += f"• *រយៈពេលសិក្សា:* {data.get('years', 'N/A')} ឆ្នាំ\n"
    response += f"• *ចំណាយសរុបប្រចាំឆ្នាំ (ប៉ាន់ស្មាន):* `{data.get('yearly_cost', '$0')}`\n"
    response += f"• *ចំណាយសរុបសម្រាប់កម្មវិធីសិក្សា (ប៉ាន់ស្មាន):* `{data.get('total_cost', '$0')}`\n\n"
    response += "_ចំណាំ: នេះគឺជាការប៉ាន់ស្មានប៉ុណ្ណោះ។_"
    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

def main() -> None:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logger.critical("FATAL: TELEGRAM_BOT_TOKEN not set.")
        return

    application = Application.builder().token(TOKEN).build()
    
    data_manager = UniversityDataManager(data_path="data/data.json")
    recommender = UniversityRecommender(data_manager)
    application.bot_data['data_manager'] = data_manager
    application.bot_data['recommender'] = recommender
    
    career_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(plan_career_start, pattern="^career$")],
        states={
            SELECTING_CAREER_MAJOR: [CallbackQueryHandler(show_career_path, pattern="^career:")]
        },
        fallbacks=[CallbackQueryHandler(start_command, pattern="^main_menu$")]
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))
    application.add_handler(CallbackQueryHandler(launch_web_app, pattern="^(analyze|browse|calculator)$"))
    application.add_handler(career_conv)
    
    logger.info("--- Starting Bot (Final Production Build) ---")
    application.run_polling()


if __name__ == "__main__":
    main() 