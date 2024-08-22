import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests

# In-memory store for user tokens and verification status
user_tokens = {}

# Replace with your API endpoint
API_ENDPOINT = "https://chatgpt.darkhacker7301.workers.dev/?question="

# Replace with your Blogspot URL
BLOGSPOT_URL = "https://chatgptgiminiai.blogspot.com/2024/08/verification-page-please-wait-for-30_22.html"

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    token = f"{user_id}_{int(time.time())}"
    user_tokens[token] = {"user_id": user_id, "verified": False}

    # Button to verify by visiting Blogspot
    verify_button = InlineKeyboardButton(
        "Verify by visiting the site",
        url=f"{BLOGSPOT_URL}?token={token}"
    )
    keyboard = [[verify_button]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Please verify by visiting the following page:", reply_markup=reply_markup)

def verify(update: Update, context: CallbackContext) -> None:
    # Extract token from the command
    token = context.args[0] if context.args else None

    if token in user_tokens:
        user_tokens[token]["verified"] = True
        update.message.reply_text("You have been verified! You can now use the bot.")
    else:
        update.message.reply_text("Verification failed or incomplete. Please try again.")

def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
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
    TOKEN = "7258041551:AAF81cY7a2kV72OUJLV3rMybTSJrj0Fm-fc"
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("verify", verify))
    dp.add_handler(CommandHandler("ask", handle_message))
    dp.add_handler(CommandHandler("message", handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
