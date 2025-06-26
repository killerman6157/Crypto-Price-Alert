from telegram import Update
from telegram.ext import CallbackContext

def show_price_info(update: Update, context: CallbackContext):
    update.callback_query.message.reply_text("📊 Price Info Section")

def show_alert_info(update: Update, context: CallbackContext):
    update.callback_query.message.reply_text("🔔 Alert Info Section")

def show_chart_info(update: Update, context: CallbackContext):
    update.callback_query.message.reply_text("🖼️ Chart Info Section")

def back_to_main_menu(update: Update, context: CallbackContext):
    update.callback_query.message.reply_text("⬅️ Back to Main Menu")
