import json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import sys

sys.path.append("/home/teknikal/Desktop/HC EVENTS/telegram bot")
from config import TOKEN

# File paths
FILES = {
    "general": "./data/general.json",
    "cultural": "./data/cultural.json",
    "technical": "./data/technical.json"
}

# Function to show inline buttons
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("EVENTS", callback_data='day_selection')],
        [InlineKeyboardButton("COORDINATORS", callback_data='coordinators')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose an option:", reply_markup=reply_markup)

# Function to show event day selection
async def day_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📅 Day 1 (Feb 28)", callback_data='Day 1')],
        [InlineKeyboardButton("📅 Day 2 (Mar 01)", callback_data='Day 2')],
        [InlineKeyboardButton("📅 Day 3 (Mar 02)", callback_data='Day 3')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("📅 Select the day of the event:", reply_markup=reply_markup)

# Function to show event categories
async def events_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    day = query.data  # Store selected day
    
    keyboard = [
        [InlineKeyboardButton("🎭 Cultural", callback_data=f'cultural_{day}')],
        [InlineKeyboardButton("🌐 General", callback_data=f'general_{day}')],
        [InlineKeyboardButton("🔧 Technical", callback_data=f'technical_{day}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(f"Select an event category for {day}:", reply_markup=reply_markup)

# Function to read event details from JSON
def get_events(category, day):
    file_path = FILES.get(category)
    if not file_path:
        return []
    
    with open(file_path, "r") as file:
        events = json.load(file)
    
    # Filter events by day
    filtered_events = [event for event in events if event["EVENT DATE"] == day]
    
    return filtered_events

# Function to show events for selected day and category
async def show_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    category, day = query.data.split('_', 1)
    events = get_events(category, day)
    
    if events:
        keyboard = [[InlineKeyboardButton(event["EVENT NAME"], callback_data=f'details_{category}_{event["EVENT NAME"]}')] for event in events]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(f"📅 {category.capitalize()} Events - {day}:", reply_markup=reply_markup)
    else:
        await query.message.reply_text("No events found for this day.")

# Function to show event details
async def show_event_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    _, category, event_name = query.data.split('_', 2)
    
    file_path = FILES.get(category)
    if not file_path:
        await query.message.reply_text("Event details not available.")
        return
    
    with open(file_path, "r") as file:
        events = json.load(file)
    
    event = next((e for e in events if e["EVENT NAME"] == event_name), None)
    
    if event:
        response = f"""
        
        *EVENT DETAILS:*
        
        *Event Name:* {event["EVENT NAME"]}
        *Venue:* {event["VENUE"]}
        *Time:* {event["EVENT TIMES"]}
        
        """
        await query.message.reply_text(response, parse_mode='Markdown')
    else:
        await query.message.reply_text("Event details not available.")

# Main bot application
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CallbackQueryHandler(day_selection, pattern='^day_selection$'))  # Show day selection first
    app.add_handler(CallbackQueryHandler(events_menu, pattern='^Day [1-3]$'))  # Then show categories
    app.add_handler(CallbackQueryHandler(show_events, pattern='^(cultural|general|technical)_Day [1-3]$'))  # Show events
    app.add_handler(CallbackQueryHandler(show_event_details, pattern='^details_.*'))  # Show event details
    
    app.run_polling()
