import json
import time
import telegram
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import sys
from pathlib import Path
from dotenv import load_dotenv
import os 

load_dotenv()
TOKEN= os.getenv('TOKEN')

sys.path.append("/home/teknikal/Desktop/HC EVENTS/telegram bot")

#path directory
DATA_DIR = Path("./data")
FILES = {
    "general": DATA_DIR / "general.json",
    "cultural": DATA_DIR / "cultural.json",
    "technical": DATA_DIR / "technical.json",
    "results": DATA_DIR / "results.json",
    "stats": DATA_DIR / "bot_stats.json"
}  

def initialize_files():
    initialize_stats_file()

    # Initialize issues file
    issues_file = DATA_DIR / "issues.json"
    if not issues_file.exists():
        with open(issues_file, 'w') as f:
            json.dump([], f)

def initialize_stats_file():
    stats_file = FILES["stats"]
    if not stats_file.exists():
        default_stats = {
            "total_users": 0,
            "unique_users": set(),  
            "start_time": time.time(),
            "downtime_periods": [],
            "commands_used": {
                "start": 0,
                "event_details": 0,
                "contact_team": 0,
                "results": 0,
                "bot_status": 0
            }
        }
        with open(stats_file, 'w') as f:
            stats_copy = default_stats.copy()
            stats_copy["unique_users"] = list(stats_copy["unique_users"])
            json.dump(stats_copy, f)
    return


# Update bot stats
def update_stats(user_id, command, username=None):
    try:
        stats_file = FILES["stats"]
        with open(stats_file, 'r') as f:
            stats = json.load(f)
        
        # Convert existing list to dictionary if needed
        if isinstance(stats["unique_users"], list):
            stats["unique_users"] = {str(uid): "Anonymous" for uid in stats["unique_users"]}
        
        user_id_str = str(user_id)
        username = username or "Anonymous"
        
        # Update unique users
        if user_id_str not in stats["unique_users"]:
            stats["total_users"] += 1
        stats["unique_users"][user_id_str] = username
        
        # Update command count
        if command in stats["commands_used"]:
            stats["commands_used"][command] += 1
        
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=4)
            
    except Exception as e:
        print(f"Error updating stats: {e}")

WELCOME_MESSAGE = """
🎉 *Brahma'25 helpline Bot!* 🎉

I'm here to assist you with Brahma'25😊.
How can I help you today?
"""

COORDINATOR_MESSAGE = """
👥 *Brahma'25 Organizing Committee*

Select a team to view their details:
"""

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    update_stats(user_id, "start")
    
    keyboard = [
        [InlineKeyboardButton("📅 Event Details", callback_data='day_selection')],
        [InlineKeyboardButton("🕗 Event Timeline", callback_data='event_timeline')],
        [InlineKeyboardButton("👥 Contact Team", callback_data='coordinators')],
        [InlineKeyboardButton("🏆 Event Results", callback_data='results')],
        [InlineKeyboardButton("📊 Bot Status", callback_data='bot_status')],
        [InlineKeyboardButton("👨‍💻 Developer Info", callback_data='developers')],
        [InlineKeyboardButton("⚠️ Report Issue", callback_data='report_issue')]

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=reply_markup, parse_mode='Markdown')

async def timeline_day_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle day selection for timeline view."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🗓️ Day 1 (Feb 28)", callback_data='timeline_Day 1')],
        [InlineKeyboardButton("🗓️ Day 2 (Mar 01)", callback_data='timeline_Day 2')],
        [InlineKeyboardButton("🗓️ Day 3 (Mar 02)", callback_data='timeline_Day 3')],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("📅 *SELECT THE DAY OF THE EVENT:*", reply_markup=reply_markup, parse_mode='Markdown')

def get_all_events_by_time(day: str) -> dict:
    """Fetch and combine events from all categories for a specific day, sorted by time."""
    all_events = {}
    
    # Categories to check
    categories = ['general', 'cultural', 'technical']
    
    for category in categories:
        file_path = FILES.get(category)
        if file_path and file_path.exists():
            try:
                with open(file_path, "r") as file:
                    events = json.load(file)
                    day_events = [event for event in events if event["EVENT DATE"] == day]
                    
                    # Group events by time
                    for event in day_events:
                        time_slot = event["EVENT TIMES"]
                        if time_slot not in all_events:
                            all_events[time_slot] = []
                        all_events[time_slot].append(event["EVENT NAME"])
            except (json.JSONDecodeError, FileNotFoundError):
                continue
    
    def time_to_24hr(time_str):
        try:
            time_obj = time.strptime(time_str, "%I:%M %p")
            return time.strftime("%H:%M", time_obj)
        except:
            return "00:00"  
    
    sorted_events = dict(sorted(all_events.items(), 
                              key=lambda x: time_to_24hr(x[0])))
    
    return sorted_events

async def show_timeline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display the timeline for the selected day."""
    query = update.callback_query
    await query.answer()
    
    day = query.data.split('_')[1]
    events_by_time = get_all_events_by_time(day)
    
    if events_by_time:
        message = f"📅 Timeline for {day}\n\n"
        
        for time_slot, events in events_by_time.items():
            message += f"`{time_slot}`\n"
            for event in events:
                message += f">> _{event}_\n"
            message += "\n"
    else:
        message = f"No events scheduled for {day} yet!"
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Days", callback_data='event_timeline')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def day_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    update_stats(user_id, "event_details")
    
    keyboard = [
        [InlineKeyboardButton("🗓️ Day 1 (Feb 28)", callback_data='Day 1')],
        [InlineKeyboardButton("🗓️ Day 2 (Mar 01)", callback_data='Day 2')],
        [InlineKeyboardButton("🗓️ Day 3 (Mar 02)", callback_data='Day 3')],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("📅 *SELECT THE DAY OF THE EVENT*", reply_markup=reply_markup, parse_mode='Markdown')

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
    await query.message.edit_text(
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
    
    try:
        if events:
            keyboard = [
                [InlineKeyboardButton(f"📌 {event['EVENT NAME']}", 
                callback_data=f'details_{category}_{event["EVENT NAME"]}')] 
                for event in events
            ]
            keyboard.append([InlineKeyboardButton("🔙 Back to Categories", callback_data=f'Day {day[-1]}')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.edit_text(
                f"🎪 *Available {category.capitalize()} Events - {day}:*",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.message.edit_text(
                "😅 No events scheduled for this day yet!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f'Day {day[-1]}')]])
            )
    except telegram.error.BadRequest as e:
        print(f"Error in show_events: {e}")
        if "There is no text in the message to edit" in str(e):
            try:
                # Delete old message if possible
                try:
                    await query.message.delete()
                except:
                    pass
                # Send as new message
                if events:
                    keyboard = [
                        [InlineKeyboardButton(f"📌 {event['EVENT NAME']}", 
                        callback_data=f'details_{category}_{event["EVENT NAME"]}')] 
                        for event in events
                    ]
                    keyboard.append([InlineKeyboardButton("🔙 Back to Categories", callback_data=f'Day {day[-1]}')])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=f"🎪 *Available {category.capitalize()} Events - {day}:*",
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                else:
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text="😅 No events scheduled for this day yet!",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f'Day {day[-1]}')]])
                    )
            except Exception as new_e:
                print(f"Failed to send new message: {new_e}")    


async def show_event_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    _, category, event_name = query.data.split('_', 2)
    
    file_path = FILES.get(category)
    if not file_path or not file_path.exists():
        try:
            await query.message.edit_text(
                "❌ Event details not available.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='day_selection')]])
            )
        except telegram.error.BadRequest:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="❌ Event details not available.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='day_selection')]])
            )
        return
    
    try:
        with open(file_path, "r") as file:
            events = json.load(file)
        
        event = next((e for e in events if e["EVENT NAME"] == event_name), None)
        
        if event:
            event_day = event["EVENT DATE"]
            
            response = f"""
<b>EVENT DETAILS</b>

<b>🎯 Event:</b> {event["EVENT NAME"]}
<b>📍 Venue:</b> {event["VENUE"]}
<b>⏰ Time:</b> {event["EVENT TIMES"]}


<b>REGISTRATION DETAILS</b>

🔗 <b>Link:</b> <a href="{event["LINK"]}">Register Here</a>  
💸 <b>Fees:</b> {event["FEES"]}  
🙋‍♂️ <b>Spot Registration:</b> {event["SR"]}  


<b>👥 EVENT COORDINATORS</b>  
{event["C1"]}  
{event["C2"]}

            """
            
            #back button to return to events list
            back_callback = f'{category}_{event_day}'
            keyboard = [[InlineKeyboardButton("🔙 Back to Events", callback_data=back_callback)],
            [InlineKeyboardButton("⚠️ Report Issue", callback_data='report_issue')]] #temporary 
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            #delete old message and send new one
            try:
                await query.message.delete()
            except Exception as del_e:
                print(f"Could not delete message: {del_e}")
            
            if "IMAGE" in event and event["IMAGE"]:
                try:
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=event["IMAGE"],
                        caption=response,
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
                except Exception as img_e:
                    print(f"Error sending image: {img_e}")
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=response,
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
            else:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=response,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
        else:
            try:
                await query.message.edit_text(
                    "❌ Event not found.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='day_selection')]])
                )
            except telegram.error.BadRequest:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="❌ Event not found.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='day_selection')]])
                )
    except Exception as e:
        print(f"Error in show_event_details: {e}")
        try:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="❌ An error occurred while retrieving event details.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data='start')]])
            )
        except Exception as inner_e:
            print(f"Failed to send error message: {inner_e}")


async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the back to main menu button."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📅 Event Details", callback_data='day_selection')],
        [InlineKeyboardButton("🕗 Event Timeline", callback_data='event_timeline')],
        [InlineKeyboardButton("👥 Contact Team", callback_data='coordinators')],
        [InlineKeyboardButton("🏆 Event Results", callback_data='results')],
        [InlineKeyboardButton("📊 Bot Status", callback_data='bot_status')],
        [InlineKeyboardButton("👨‍💻 Developer Info", callback_data='developers')],
        [InlineKeyboardButton("⚠️ Report Issue", callback_data='report_issue')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(WELCOME_MESSAGE, reply_markup=reply_markup, parse_mode='Markdown')

async def show_coordinators(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the coordinators menu."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    update_stats(user_id, "contact_team")
    
    keyboard = [
        [InlineKeyboardButton("👥 Student Coordination", callback_data='coord_student')],
        [InlineKeyboardButton("📝 Registration Team", callback_data='coord_registration')],
        [InlineKeyboardButton("🍽️ Refreshment Team", callback_data='coord_refreshment')],
        [InlineKeyboardButton("🏥 Medical Team", callback_data='coord_medical')],
        [InlineKeyboardButton("👮 Discipline Team", callback_data='coord_discipline')],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(
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
        #student coordination team
                'student': """
*Student Coordination Team* 👥 

_Coordinators:_
 ```Nandhitha```  +917304396216
```Vyshak```  +919745913185

For student related queries, please contact the above team.
        """,

    #registeration team
        'registration': """
*Registration Team* 📝

_Coordinators:_
```Alen``` +919744134203
```Devanandha``` +919037604721

For registration related queries, please contact the above team.
        """,

    #refreshments team
        'refreshment': """
*Refreshment Team* 🍽️ 

_Coordinators:_
```Harikrishnan``` +919446990681
```Vivek``` +919747737337

For refreshment related queries, please contact the above team.
        """,

    #medical team    
        'medical': """
🏥 *Medical Team*

_Emergency Contacts:_ 
```Aleena``` +9181039026386
```Devika``` +918590282983

For any medical assistance/emergency during the event, please contact the above team.
        """,

        #discipline team
        'discipline': """
*Discipline Team*👮 

_Coordinators:_
```Dhrupath``` +919400941004
```Yadhu``` +918138835700

For any discipline related concerns, please contact the above team.
        """
    }
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Teams", callback_data='coordinators')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        team_messages.get(team_type, "Team details not available"),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def results_day_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    update_stats(user_id, "results")
    
    keyboard = [
        [InlineKeyboardButton("🗓️ Day 1 (Feb 28)", callback_data='results_Day 1')],
        [InlineKeyboardButton("🗓️ Day 2 (Mar 01)", callback_data='results_Day 2')],
        [InlineKeyboardButton("🗓️ Day 3 (Mar 02)", callback_data='results_Day 3')],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("🏆 *Select the day to view event results:*", reply_markup=reply_markup, parse_mode='Markdown')

async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display results for the selected day."""
    query = update.callback_query
    await query.answer()
    
    day = query.data.split('_')[1]
    results_file = FILES["results"]
    
    try:
        with open(results_file, 'r') as f:
            results_data = json.load(f)
        
        day_results = [result for result in results_data if result["EVENT DATE"] == day]
        
        if day_results:
            message = f"🏆 *Results for {day}*\n\n"
            for result in day_results:
                message += f" ```{result['EVENT NAME']}```\n"
                message += f"🥇 1st: {result['WINNER 1']}\n"
                if result['WINNER 2'].strip():
                    message += f"🥈 2nd: {result['WINNER 2']}\n"
                if result['WINNER 3'].strip():
                    message += f"🥉 3rd: {result['WINNER 3']}\n"
                message += "\n"
        else:
            message = f"No results available for {day} yet!"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Days", callback_data='results')],
            [InlineKeyboardButton("🏠 Main Menu", callback_data='start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        print(f"Error showing results: {e}")
        await query.message.edit_text(
            "❌ Could not retrieve results. Please try again later.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='results')]])
        )

async def show_bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display bot status and statistics."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    update_stats(user_id, "bot_status")
    
    try:
        with open(FILES["stats"], 'r') as f:
            stats = json.load(f)
        
        # Calculate uptime
        current_time = time.time()
        uptime_seconds = current_time - stats["start_time"]
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Format uptime
        uptime_str = f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
        
        # Get downtime
        downtime_count = len(stats["downtime_periods"])
        total_downtime = sum([period["end"] - period["start"] for period in stats["downtime_periods"]], 0)
        downtime_hours = total_downtime / 3600 if total_downtime else 0
        
        #status message
        status_message = f"""
📊 *BOT STATUS REPORT*

👥 *Usage Statistics:*
• Total Interactions: {stats["total_users"]}
• Unique Users: {len(stats["unique_users"])}

⏱️ *Uptime:*
• Bot Running Since: {uptime_str}
• Downtime Incidents: {downtime_count}
• Total Downtime: {downtime_hours:.2f} hours

📈 *Command Usage:*
• Start: {stats["commands_used"]["start"]}
• Event Details: {stats["commands_used"]["event_details"]}
• Contact Team: {stats["commands_used"]["contact_team"]}
• Results: {stats["commands_used"]["results"]}
• Status Checks: {stats["commands_used"]["bot_status"]}

⚡ *Current Status:* ONLINE
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data='start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            status_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Error displaying bot status: {e}")
        await query.message.edit_text(
            "❌ Error retrieving bot statistics. Please try again later.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='start')]]),
            parse_mode='Markdown'
        )

def record_downtime(is_down=True):
    """Record bot downtime periods."""
    try:
        with open(FILES["stats"], 'r') as f:
            stats = json.load(f)
        
        current_time = time.time()
        
        if is_down:
            # Start recording downtime
            stats["downtime_periods"].append({"start": current_time, "end": None})
        else:
            # End the latest downtime period if it exists
            if stats["downtime_periods"] and stats["downtime_periods"][-1]["end"] is None:
                stats["downtime_periods"][-1]["end"] = current_time
        
        with open(FILES["stats"], 'w') as f:
            json.dump(stats, f)
    except Exception as e:
        print(f"Error recording downtime: {e}")
async def show_developers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    dev_message = """

*DEVELOPERS:*
 `Brian Roy Mathew`

*CONTRIBUTORS*
 `Ashwin P Shine`
 `Chandra Rajesh`
 `Deepak M.R.`
 `Anandhakrishnan`
 `Ceeya Sarah Varghese`


_Developed & Handled with ❤️ by HackClub ASIET_
    """
    
    keyboard = [
        [InlineKeyboardButton("Connect with Team", callback_data='connection')],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(dev_message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    dev_message = """
    Connect With Us:

📍[BRIAN ROY MATHEW](https://www.linkedin.com/in/brianroymathew/)
📍[ASHWIN P SHINE](https://www.linkedin.com/in/ashwin-p-shine/)
📍[CHANDRA RAJESH](https://www.linkedin.com/in/chandra-rajesh/)
📍[DEEPAK M.R.](https://www.linkedin.com/in/deepak-m-r-ab601a291/)
📍[ANANTHAKRISHNAN](https://)
📍[CEEYA SARAH VARGHESE](https://www.linkedin.com/in/ceeya-sarah-varghese-38280632a/)

    For issues/conflicts:
    WhatsApp : [Developer Team](https://wa.me/+919995965621)
    """

    keyboard = [[InlineKeyboardButton("🔙 Back to Developer Info", callback_data='developers')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(dev_message, reply_markup=reply_markup, parse_mode='Markdown')

async def prompt_report_issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt user to describe the issue"""
    query = update.callback_query
    await query.answer()
    context.user_data['reporting_issue'] = True
    await query.message.reply_text("📝 Please describe the issue you're experiencing:")

async def handle_issue_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save user's issue report"""
    if context.user_data.get('reporting_issue'):
        user = update.message.from_user
        issue_data = {
            "user_id": user.id,
            "username": user.username or user.first_name,
            "issue": update.message.text,
            "timestamp": time.time(),
            "resolved": False
        }
        
        try:
            # Ensure data directory exists
            DATA_DIR.mkdir(exist_ok=True)
            
            issues_file = DATA_DIR / "issues.json"
            
            # Initialize with empty list if file is empty/corrupted
            if not issues_file.exists() or issues_file.stat().st_size == 0:
                with open(issues_file, 'w') as f:
                    json.dump([], f)
            
            # Load existing issues safely
            with open(issues_file, 'r') as f:
                try:
                    issues = json.load(f)
                except json.JSONDecodeError:
                    issues = []
            
            # Append new issue
            issues.append(issue_data)
            
            # Save back to file
            with open(issues_file, 'w') as f:
                json.dump(issues, f, indent=4)
            
            await update.message.reply_text("✅ Thank you for reporting the issue! We'll review it shortly.")
            
        except Exception as e:
            print(f"Error saving issue: {e}")
            await update.message.reply_text(
                "❌ Failed to save your report. Please try again later.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔙 Contact Developers", callback_data='developers')]]
                )
            )
        finally:
            # Clear reporting state
            if 'reporting_issue' in context.user_data:
                del context.user_data['reporting_issue']

async def toggle_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle user's notification preference"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    notifications_file = FILES["notifications"]
    
    try:
        with open(notifications_file, 'r') as f:
            data = json.load(f)
        
        if str(user_id) in data["subscribed_users"]:
            data["subscribed_users"].remove(str(user_id))
            response = "🔕 Notifications disabled. You'll miss important updates!"
        else:
            data["subscribed_users"].append(str(user_id))
            response = "🔔 Notifications enabled! You'll receive important updates."
        
        with open(notifications_file, 'w') as f:
            json.dump(data, f)
            
        await query.message.edit_text(response)
        
    except Exception as e:
        print(f"Notification error: {e}")
        await query.message.reply_text("❌ Could not update preferences. Please try again.")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin-only broadcast command"""
    ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMINS', '').split(',') if id.strip()]
    
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Unauthorized access.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
        
    message = ' '.join(context.args)
    
    try:
        with open(FILES["stats"], 'r') as f:
            stats = json.load(f)
        
        success = 0
        failures = 0
        
        # Handle legacy list format
        if isinstance(stats["unique_users"], list):
            # Convert old list format to dictionary
            stats["unique_users"] = {str(uid): "Anonymous" for uid in stats["unique_users"]}
            
        for user_id in stats["unique_users"].keys():
            try:
                await context.bot.send_message(
                    chat_id=int(user_id),
                    text=f"📢 Important Announcement!\n\n{message}",
                    parse_mode='Markdown'
                )
                success += 1
            except Exception as e:
                username = stats["unique_users"].get(user_id, "Unknown")
                print(f"Failed to send to {username} ({user_id}): {e}")
                failures += 1
                
        await update.message.reply_text(
            f"✅ Broadcast completed!\n"
            f"Total users: {len(stats['unique_users'])}\n"
            f"Success: {success}\n"
            f"Failures: {failures}"
        )
                
    except Exception as e:
        print(f"Broadcast error: {e}")
        await update.message.reply_text("❌ Failed to send broadcast.")


def main():
    print("🤖 BRAHMA'25 BOT: ONLINE")
    
    # Initialize the stats file if it doesn't exist
    initialize_stats_file()
    
    # Record that the bot is online (end any previous downtime)
    record_downtime(is_down=False)
    
    # Create the application
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
    app.add_handler(CallbackQueryHandler(results_day_selection,pattern='^results$'))
    app.add_handler(CallbackQueryHandler(show_results, pattern='^results_Day [1-3]$'))
    app.add_handler(CallbackQueryHandler(show_bot_status, pattern='^bot_status$'))
    app.add_handler(CallbackQueryHandler(timeline_day_selection, pattern='^event_timeline$'))
    app.add_handler(CallbackQueryHandler(show_timeline, pattern='^timeline_Day [1-3]$'))
    app.add_handler(CallbackQueryHandler(prompt_report_issue, pattern='^report_issue$'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_issue_report))
    app.add_handler(CallbackQueryHandler(show_developers, pattern='^developers$'))
    app.add_handler(CallbackQueryHandler(show_connection, pattern='^connection$'))
    app.add_handler(CallbackQueryHandler(toggle_notifications, pattern='^toggle_notifications$'))
    app.add_handler(CommandHandler('broadcast', broadcast_command))

    
    print("✅ BOT IS READY TO ASSIST WITH BRAHMA'25")
    
    try:
        app.run_polling()
    except Exception as e:
        print(f"Bot crashed with error: {e}")
        # Record that the bot is down
        record_downtime(is_down=True)
        raise e

if __name__ == '__main__':
    main()