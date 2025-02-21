import json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import sys
from pathlib import Path

from dotenv import load_dotenv
import os 

load_dotenv()

TOKEN= os.getenv('TOKEN')

sys.path.append("/home/teknikal/Desktop/HC EVENTS/telegram bot")
#from config import TOKEN

# File paths using Path for better cross-platform compatibility
DATA_DIR = Path("./data")
FILES = {
    "general": DATA_DIR / "general.json",
    "cultural": DATA_DIR / "cultural.json",
    "technical": DATA_DIR / "technical.json"
}

WELCOME_MESSAGE = """
🎉 *Welcome to Brahma'25 Navigation Bot!* 🎉

I'm here to help you navigate through Brahma'25 events and connect with the organizing team.
How can I assist you today?
"""

COORDINATOR_MESSAGE = """
👥 *Brahma'25 Organizing Team*

Select a team to view their details:
"""

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📅 Event Schedule", callback_data='day_selection')],
        [InlineKeyboardButton("👥 Contact Team", callback_data='coordinators')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=reply_markup, parse_mode='Markdown')

async def day_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🗓️ Day 1 (Feb 28)", callback_data='Day 1')],
        [InlineKeyboardButton("🗓️ Day 2 (Mar 01)", callback_data='Day 2')],
        [InlineKeyboardButton("🗓️ Day 3 (Mar 02)", callback_data='Day 3')],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("📅 *Which day would you like to explore?*", reply_markup=reply_markup, parse_mode='Markdown')

async def events_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    day = query.data
    
    keyboard = [
        [InlineKeyboardButton("🎭 Cultural Events", callback_data=f'cultural_{day}')],
        [InlineKeyboardButton("🌐 General Events", callback_data=f'general_{day}')],
        [InlineKeyboardButton("🔧 Technical Events", callback_data=f'technical_{day}')],
        [InlineKeyboardButton("🔙 Back to Days", callback_data='day_selection')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        f"🎯 *What type of events interest you for {day}?*", 
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def get_events(category: str, day: str) -> list:
    """Fetch events from JSON file based on category and day."""
    file_path = FILES.get(category)
    if not file_path or not file_path.exists():
        return []
    
    try:
        with open(file_path, "r") as file:
            events = json.load(file)
        return [event for event in events if event["EVENT DATE"] == day]
    except (json.JSONDecodeError, FileNotFoundError):
        return []

async def show_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    category, day = query.data.split('_', 1)
    events = get_events(category, day)
    
    if events:
        keyboard = [
            [InlineKeyboardButton(f"📌 {event['EVENT NAME']}", 
            callback_data=f'details_{category}_{event["EVENT NAME"]}')] 
            for event in events
        ]
        keyboard.append([InlineKeyboardButton("🔙 Back to Categories", callback_data=f'Day {day[-1]}')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            f"🎪 *Available {category.capitalize()} Events - {day}:*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await query.message.reply_text("😅 No events scheduled for this day yet!")

async def show_event_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    _, category, event_name = query.data.split('_', 2)
    
    file_path = FILES.get(category)
    if not file_path or not file_path.exists():
        await query.message.reply_text("❌ Event details not available.")
        return
    
    try:
        with open(file_path, "r") as file:
            events = json.load(file)
        
        event = next((e for e in events if e["EVENT NAME"] == event_name), None)
        
        if event:
            response = f"""
📋 *EVENT DETAILS*

🎯 *Event:* {event["EVENT NAME"]}
📍 *Venue:* {event["VENUE"]}
⏰ *Time:* {event["EVENT TIMES"]}

👥 *Event Coordinators:* 
• {event["C1"]}
• {event["C2"]}
            """
            
            if "IMAGE" in event and event["IMAGE"]:
                try:
                    await query.message.reply_photo(
                        photo=event["IMAGE"],
                        caption=response,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    print(f"Error sending image: {e}")
                    await query.message.reply_text(response, parse_mode='Markdown')
            else:
                await query.message.reply_text(response, parse_mode='Markdown')
        else:
            await query.message.reply_text("❌ Event details not available.")
    except Exception as e:
        print(f"Error processing event details: {e}")
        await query.message.reply_text("❌ An error occurred while fetching event details.")

async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the back to main menu button."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📅 Event Schedule", callback_data='day_selection')],
        [InlineKeyboardButton("👥 Contact Team", callback_data='coordinators')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(WELCOME_MESSAGE, reply_markup=reply_markup, parse_mode='Markdown')

async def show_coordinators(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the coordinators menu."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📝 Registration Team", callback_data='coord_registration')],
        [InlineKeyboardButton("🍽️ Refreshment Team", callback_data='coord_refreshment')],
        [InlineKeyboardButton("🏥 Medical Team", callback_data='coord_medical')],
        [InlineKeyboardButton("👮 Discipline Team", callback_data='coord_discipline')],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        COORDINATOR_MESSAGE,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_team_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display specific team details."""
    query = update.callback_query
    await query.answer()
    
    team_type = query.data.split('_')[1]
    
    team_messages = {
        'registration': """
📝 *Registration Team*

*Head Coordinators:*
• Name 1 - Contact
• Name 2 - Contact

For registration related queries, please contact the above team.
        """,
        'refreshment': """
🍽️ *Refreshment Team*

*Head Coordinators:*
• Name 1 - Contact
• Name 2 - Contact

For refreshment related queries, please contact the above team.
        """,
        'medical': """
🏥 *Medical Team*

*Emergency Contacts:*
• Name 1 - Contact
• Name 2 - Contact

Medical assistance is available 24/7 during the event.
        """,
        'discipline': """
👮 *Discipline Team*

*Head Coordinators:*
• Name 1 - Contact
• Name 2 - Contact

For any discipline related concerns, please contact the above team.
        """
    }
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Teams", callback_data='coordinators')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        team_messages.get(team_type, "Team details not available"),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def main():
    """Initialize and run the bot."""
    print("🤖 BRAHMA'25 BOT: ONLINE")
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CallbackQueryHandler(day_selection, pattern='^day_selection$'))
    app.add_handler(CallbackQueryHandler(events_menu, pattern='^Day [1-3]$'))
    app.add_handler(CallbackQueryHandler(show_events, pattern='^(cultural|general|technical)_Day [1-3]$'))
    app.add_handler(CallbackQueryHandler(show_event_details, pattern='^details_.*'))
    app.add_handler(CallbackQueryHandler(show_coordinators, pattern='^coordinators$'))
    app.add_handler(CallbackQueryHandler(show_team_details, pattern='^coord_.*'))
    app.add_handler(CallbackQueryHandler(back_to_start, pattern='^start$'))
    
    print("✅ BOT IS READY TO ASSIST WITH BRAHMA'25 NAVIGATION")
    app.run_polling()

if __name__ == '__main__':
    main()
