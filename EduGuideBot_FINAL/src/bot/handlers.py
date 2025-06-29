import logging
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(__name__)

# Conversation states
(START, LOCATION, BUDGET, MAJOR_FIELD, CAREER_GOAL, ENGLISH_PROFICIENCY, 
 CONFIRM_INFO, RESULTS, UNIVERSITY_DETAIL) = range(9)

# Cached user data
user_profiles = {}

# Common location options in Cambodia
LOCATIONS = ["Phnom Penh", "Siem Reap", "Battambang", "Any"]

# Major field categories
MAJOR_FIELDS = [
    "វិស្វកម្ម", "បច្ចេកវិទ្យា", "វេជ្ជសាស្ត្រ", "សុខភាព", "ច្បាប់",
    "ធុរកិច្ច", "អប់រំ", "ភាសា", "កសិកម្ម", "សេដ្ឋកិច្ច", "ទេសចរណ៍", 
    "សិល្បៈ", "វិទ្យាសាស្ត្រ", "សង្គមសាស្ត្រ", "ព័ត៌មានវិទ្យា"
]

# Career goals
CAREER_GOALS = [
    "វិស្វករ", "អ្នកគ្រប់គ្រង", "វេជ្ជបណ្ឌិត", "គ្រូបង្រៀន", "អ្នកកฎหមាយ"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask for location."""
    user_id = update.effective_user.id
    user_profiles[user_id] = {}
    
    await update.message.reply_text(
        "សួស្តី! ខ្ញុំជា EduGuideBot ជំនួយក្នុងការស្វែងរក និងផ្តល់អនុសាសន៍សាកលវិទ្យាល័យនៅកម្ពុជា។ "
        "សូមឆ្លើយនូវសំណួរមួយចំនួនដើម្បីទទួលបានការណែនាំល្អបំផុត។\n\n"
        "តើអ្នកចង់រៀននៅខេត្ត/ក្រុងមួយណា?"
    )
    
    keyboard = [[InlineKeyboardButton(loc, callback_data=loc)] for loc in LOCATIONS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("សូមជ្រើសរើសទីតាំង:", reply_markup=reply_markup)
    return LOCATION

async def location_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the location and ask for budget."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    location = query.data
    user_profiles[user_id]['location'] = location
    
    await query.message.edit_text(f"អ្នកបានជ្រើសរើសទីតាំង: {location}")
    await query.message.reply_text(
        "សូមបញ្ចូលថវិកាអតិបរមារបស់អ្នកសម្រាប់ការសិក្សាក្នុងមួយឆ្នាំ (គិតជា USD):"
    )
    
    return BUDGET

async def budget_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the budget and ask for major field."""
    user_id = update.effective_user.id
    
    try:
        budget = int(update.message.text)
        if budget <= 0:
            raise ValueError
        user_profiles[user_id]['max_budget'] = budget
    except ValueError:
        await update.message.reply_text("សូមបញ្ចូលលេខវិជ្ជមាន (ឧទា. 1000):")
        return BUDGET
    
    # Create a keyboard with major field options
    keyboard = []
    row = []
    for i, field in enumerate(MAJOR_FIELDS):
        row.append(InlineKeyboardButton(field, callback_data=field))
        if (i + 1) % 3 == 0:  # 3 buttons per row
            keyboard.append(row)
            row = []
    if row:  # Add any remaining buttons
        keyboard.append(row)
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "សូមជ្រើសរើសវិស័យសិក្សាដែលអ្នកចាប់អារម្មណ៍:",
        reply_markup=reply_markup
    )
    
    return MAJOR_FIELD

async def major_field_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the major field and ask for career goal."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    field = query.data
    user_profiles[user_id]['core_field'] = field
    
    await query.message.edit_text(f"អ្នកបានជ្រើសរើសវិស័យសិក្សា: {field}")
    
    # Create a keyboard for career goals
    keyboard = [[InlineKeyboardButton(goal, callback_data=goal)] for goal in CAREER_GOALS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "តើអ្នកមានគោលដៅអាជីពអ្វីក្នុងរយៈពេលវែង?",
        reply_markup=reply_markup
    )
    
    return CAREER_GOAL

async def career_goal_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the career goal and ask for English proficiency."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    goal = query.data
    user_profiles[user_id]['career_goal'] = goal
    
    await query.message.edit_text(f"អ្នកបានជ្រើសរើសគោលដៅអាជីព: {goal}")
    
    # Create a keyboard for English proficiency
    keyboard = []
    row = []
    for i in range(1, 11):  # Scale from 1-10
        row.append(InlineKeyboardButton(str(i), callback_data=str(i)))
        if i % 5 == 0:  # 5 buttons per row
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        "វាយតម្លៃជំនាញភាសាអង់គ្លេសរបស់អ្នកពី 1 ដល់ 10 (1 = ទាបបំផុត, 10 = ល្អបំផុត):",
        reply_markup=reply_markup
    )
    
    return ENGLISH_PROFICIENCY

async def english_proficiency_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the English proficiency and show summary."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    proficiency = int(query.data)
    user_profiles[user_id]['english_proficiency'] = proficiency
    
    user_data = user_profiles[user_id]
    
    # Show summary of collected information
    summary = (
        "សូមពិនិត្យព័ត៌មានរបស់អ្នក:\n\n"
        f"📍 ទីតាំង: {user_data['location']}\n"
        f"💰 ថវិកាអតិបរមាក្នុងមួយឆ្នាំ: ${user_data['max_budget']}\n"
        f"📚 វិស័យសិក្សា: {user_data['core_field']}\n"
        f"🎯 គោលដៅអាជីព: {user_data['career_goal']}\n"
        f"🔤 កម្រិតភាសាអង់គ្លេស: {user_data['english_proficiency']}/10\n\n"
        "តើព័ត៌មានខាងលើត្រឹមត្រូវឬទេ?"
    )
    
    keyboard = [
        [InlineKeyboardButton("ត្រឹមត្រូវ", callback_data="confirm_yes")],
        [InlineKeyboardButton("ចាប់ផ្តើមម្តងទៀត", callback_data="confirm_no")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(f"អ្នកបានជ្រើសរើសកម្រិតភាសាអង់គ្លេស: {proficiency}/10")
    await query.message.reply_text(summary, reply_markup=reply_markup)
    
    return CONFIRM_INFO

async def confirm_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process confirmation and show recommendations or restart."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_no":
        await query.message.edit_text("សូមចាប់ផ្តើមម្តងទៀត...")
        await query.message.reply_text(
            "សួស្តី! ខ្ញុំជា EduGuideBot ជំនួយក្នុងការស្វែងរក និងផ្តល់អនុសាសន៍សាកលវិទ្យាល័យនៅកម្ពុជា។ "
            "សូមឆ្លើយនូវសំណួរមួយចំនួនដើម្បីទទួលបានការណែនាំល្អបំផុត។\n\n"
            "តើអ្នកចង់រៀននៅខេត្ត/ក្រុងមួយណា?"
        )
        
        keyboard = [[InlineKeyboardButton(loc, callback_data=loc)] for loc in LOCATIONS]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("សូមជ្រើសរើសទីតាំង:", reply_markup=reply_markup)
        
        return LOCATION
    
    # Confirm and fetch recommendations
    await query.message.edit_text("កំពុងស្វែងរកសាកលវិទ្យាល័យដែលសមស្របសម្រាប់អ្នក...")
    
    # This is where we would call the recommendation engine
    # For now, let's return to the main conversation handler
    user_id = query.from_user.id
    
    # Get recommendations using the recommender
    # This would be properly initialized in the main app
    github_pages_url = os.environ.get('GITHUB_PAGES_URL', 'https://example.com')
    
    await query.message.reply_text(
        "ឥឡូវនេះអ្នកអាចមើលអនុសាសន៍របស់អ្នកតាមរយៈគេហទំព័រខាងក្រោម:\n\n"
        f"{github_pages_url}/results.html?id={user_id}"
    )
    
    # In a real implementation, we'd save the user profile and generate results
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel and end the conversation."""
    await update.message.reply_text(
        "អរគុណ! បើអ្នកចង់ស្វែងរកសាកលវិទ្យាល័យម្តងទៀត សូមចុច /start"
    )
    return ConversationHandler.END 