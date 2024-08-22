from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler
import logging
import os
import requests

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)

# Bot setup
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BLOGSPOT_URL = os.getenv('BLOGSPOT_URL')
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# User verification
verified_users = {}

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in verified_users or not verified_users[user_id]:
        keyboard = [[{'text': 'Verify Now', 'callback_data': 'verify'}]]
        reply_markup = {'inline_keyboard': keyboard}
        update.message.reply_text(
            'Please verify your access by clicking the button below:',
            reply_markup=reply_markup
        )
    else:
        update.message.reply_text("Welcome back! How can I assist you today?")

def verify(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    verified_users[user_id] = True
    query.answer()
    query.edit_message_text("Verification successful! You can now use the bot.")
    query.message.reply_text(f"Please visit this link and wait for 30 seconds to complete the verification: {BLOGSPOT_URL}")

def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id in verified_users and verified_users[user_id]:
        text = update.message.text
        response = requests.get(f"https://chatgpt.darkhacker7301.workers.dev/?question={text}")
        data = response.json()
        answer = data.get('answer', 'Sorry, I could not understand your question.')
        update.message.reply_text(answer)
    else:
        update.message.reply_text("Please verify your access first by clicking the button below:")

# Handlers
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CallbackQueryHandler(verify, pattern='^verify$'))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Flask route for webhook
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, updater.bot)
    dispatcher.process_update(update)
    return jsonify({'status': 'ok'})

def set_webhook():
    webhook_url = os.getenv('WEBHOOK_URL') + TELEGRAM_TOKEN
    updater.bot.set_webhook(url=webhook_url)

if __name__ == '__main__':
    set_webhook()
    app.run(host='0.0.0.0', port=80)
