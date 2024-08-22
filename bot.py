import time
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import requests

# In-memory store for user tokens and verification status
user_tokens = {}
verification_times = {}

# Replace with your API endpoint
API_ENDPOINT = "https://chatgpt.darkhacker7301.workers.dev/?question="

# Replace with your Blogspot URL
BLOGSPOT_URL = "https://chatgptgiminiai.blogspot.com/2024/08/verification-page-please-wait-for-30_22.html"

# Initialize Flask app
app = Flask(__name__)

# Replace with your Telegram bot token
TELEGRAM_TOKEN = "7258041551:AAF81cY7a2kV72OUJLV3rMybTSJrj0Fm-fc"

# Initialize Updater globally
updater = Updater(TELEGRAM_TOKEN)

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    current_time = int(time.time())

    # Check if the user needs to verify
    if user_id in verification_times:
        last_verified = verification_times[user_id]
        if (current_time - last_verified) < 3600:  # 1 hour = 3600 seconds
            update.message.reply_text("You have already verified recently. Please try again later.")
            return

    token = f"{user_id}_{current_time}"
    user_tokens[token] = {"user_id": user_id, "verified": False}
    verification_times[user_id] = current_time

    # Button to verify by visiting Blogspot
    verify_button = InlineKeyboardButton(
        "Verify by visiting the site",
        url=f"{BLOGSPOT_URL}?token={token}"
    )
    keyboard = [[verify_button]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Please verify by visiting the following page:", reply_markup=reply_markup)

def verify(update: Update, context: CallbackContext) -> None:
    token = context.args[0] if context.args else None
    if token and token in user_tokens:
        user_id = user_tokens[token]["user_id"]
        user_tokens[token]["verified"] = True
        update.message.reply_text("You have been verified! You can now use the bot.")
    else:
        update.message.reply_text("Verification failed or incomplete. Please try again.")

def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    # Check if the user is verified
    token = next((t for t in user_tokens if user_tokens[t]["user_id"] == user_id), None)

    if token and user_tokens[token]["verified"]:
        # Send the user's message to the API
        user_message = update.message.text
        response = requests.get(f"{API_ENDPOINT}{user_message}").json()
        answer = response.get("answer", "Sorry, something went wrong.")
        update.message.reply_text(answer)
    else:
        update.message.reply_text("Please verify yourself first by clicking /start.")

def main() -> None:
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("verify", verify))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

# Flask route to handle webhook requests from Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, updater.bot)
    updater.dispatcher.process_update(update)
    return jsonify({'status': 'ok'})

# Set the webhook URL (make sure to replace with your actual domain)
def set_webhook():
    webhook_url = "https://chatgpt-1-8qb8.onrender.com/webhook"
    updater.bot.set_webhook(url=webhook_url)

if __name__ == '__main__':
    set_webhook()
    main()
    app.run(host='0.0.0.0', port=80)  # Run Flask on port 80 for web app deployment
