from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update

import sys
sys.path.append("/home/teknikal/Desktop/HC EVENTS/telegram bot")

from config import TOKEN


#commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello!, How can I help you?')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Here is how I can help: /n The below mentioned are my commands: /n 1. /start : Start the bot')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command')


#responses

def handle_response(text: str): 
    processsed: str = text.lower()

    if 'hello' in processsed:
        return 'Hey! How can I help you?'

    return 'invalid input error'


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error} ')

if __name__ == '__main__':
    print("BOT STATUS: ON")
    app = Application.builder().token(TOKEN).build()

    #commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    print('polling...')
    app.run_polling(poll_interval=5)

