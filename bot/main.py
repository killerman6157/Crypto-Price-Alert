import os
import logging
import requests
import json
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from dotenv import load_dotenv

from handlers.menu import (
    send_main_menu,
    show_price_info,
    show_alert_info,
    show_chart_info,
    start_command,
    help_command
)
from handlers.price import get_price
from handlers.alerts import set_alert, my_alerts_command, cancel_alert
from handlers.chart import send_price_chart

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("⚠️ BOT_TOKEN bai da kyau ko bai samu ba.")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

handlers = [
    CommandHandler("start", start_command),
    CommandHandler("menu", send_main_menu),
    CommandHandler("help", help_command),
    CommandHandler("price", get_price),
    CommandHandler("alert", set_alert),
    CommandHandler("myalerts", my_alerts_command),
    CommandHandler("cancelalert", cancel_alert),
    CommandHandler("chart", send_price_chart),
    CallbackQueryHandler(show_price_info, pattern="^show_price_info$"),
    CallbackQueryHandler(show_alert_info, pattern="^show_alert_info$"),
    CallbackQueryHandler(show_chart_info, pattern="^show_chart_info$"),
    CallbackQueryHandler(send_main_menu, pattern="^back_to_main_menu$")
]

for handler in handlers:
    application.add_handler(handler)

if __name__ == "__main__":
    logger.info("Bot is starting...")
    application.run_polling()
