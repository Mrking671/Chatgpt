import requests
import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Your API endpoint
API_ENDPOINT = "https://chatgpt.darkhacker7301.workers.dev/?question="

# Define the command /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! I am your AI bot. Ask me anything!')

# Handle messages
def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    response = requests.get(API_ENDPOINT + user_message)
    
    if response.status_code == 200:
        data = response.json()
        answer = data.get('answer', 'Sorry, I could not process your request.')
        join_link = data.get('join', '')

        # Send the response back to the user
        update.message.reply_text(answer)
        
        if join_link:
            update.message.reply_text(f"Join us here: {join_link}")
    else:
        update.message.reply_text("Sorry, something went wrong. Please try again later.")

# Error handler
def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    # Telegram bot token
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # On different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))

    # On non-command i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
