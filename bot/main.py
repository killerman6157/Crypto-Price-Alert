import os import logging from dotenv import load_dotenv from telegram.ext import ( Application, CommandHandler, CallbackQueryHandler, ) from handlers.general import start_command, help_command, send_main_menu from handlers.price import get_price, set_alert, my_alerts_command, cancel_alert from handlers.chart import send_price_chart from handlers.callbacks import ( show_price_info, show_alert_info, show_chart_info, back_to_main_menu, )

Load environment variables from .env file

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN") if not TELEGRAM_BOT_TOKEN: raise ValueError("⚠️ BOT_TOKEN bai samu ba daga .env file. Tabbatar ka saka BOT_TOKEN=... a ciki")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO) logger = logging.getLogger(name)

def main(): application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Commands
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("menu", send_main_menu))
application.add_handler(CommandHandler("price", get_price))
application.add_handler(CommandHandler("alert", set_alert))
application.add_handler(CommandHandler("myalerts", my_alerts_command))
application.add_handler(CommandHandler("cancelalert", cancel_alert))
application.add_handler(CommandHandler("chart", send_price_chart))

# Callback query handlers
application.add_handler(CallbackQueryHandler(show_price_info, pattern="^show_price_info$"))
application.add_handler(CallbackQueryHandler(show_alert_info, pattern="^show_alert_info$"))
application.add_handler(CallbackQueryHandler(show_chart_info, pattern="^show_chart_info$"))
application.add_handler(CallbackQueryHandler(back_to_main_menu, pattern="^back_to_main_menu$"))

logger.info("🤖 Bot is starting...")
application.run_polling()

if name == "main": main()

