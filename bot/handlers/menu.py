from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

SETUP_GUIDE_LINK = "https://t.me/c/2544548450/3"

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = (
        "🤖 *Crypto Price Bot Menu*\n"
        "Zaɓi ɗaya daga cikin abubuwa masu zuwa:"
    )
    keyboard = [
        [InlineKeyboardButton("📚 Setup Guide", url=SETUP_GUIDE_LINK)],
        [InlineKeyboardButton("📈 Duba Farashin Cryptocurrency", callback_data="show_price_info")],
        [InlineKeyboardButton("🛎️ Saita Faɗakarwar Farashi", callback_data="show_alert_info")],
        [InlineKeyboardButton("📋 Duba Faɗakarwarka", callback_data="my_alerts_button")],
        [InlineKeyboardButton("📊 Chart na Cryptocurrency", callback_data="show_chart_info")],
    ]
    await update.callback_query.edit_message_text(menu_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown") \
        if update.callback_query else \
        await update.message.reply_text(menu_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# Similarly define show_price_info, show_alert_info, show_chart_info, start_command, help_command
# (I can send the rest if you want)
