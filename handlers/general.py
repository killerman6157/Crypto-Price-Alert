from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

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
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup, parse_mode="Markdown")
        except Exception as e:
            logger.warning(f"Edit message failed: {e}")
            await update.callback_query.message.reply_text(menu_text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.message:
        await update.message.reply_text(menu_text, reply_markup=reply_markup, parse_mode="Markdown")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_main_menu(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = (
        "📚 *Taimako da Bayani*\n\n"
        "Ga jerin umarnoni da zaka iya amfani dasu:\n"
        "`/start` - 🤖 Fara amfani da bot (Zai nuna babban menu)\n"
        "`/menu` - 📋 Nuna babban menu\n"
        "`/price <coin>` - 📈 Duba farashin coin\n"
        "`/alert <coin> <price> <up/down>` - 🛎️ Saita faɗakarwa\n"
        "`/myalerts` - 📋 Duba faɗakarwa\n"
        "`/cancelalert <coin>` - ❌ Soke faɗakarwa\n"
        "`/chart <coin>` - 📊 Duba chart"
    )
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(help_message, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(help_message, reply_markup=reply_markup, parse_mode="Markdown")


async def show_price_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "📈 *Duba Farashin Coin*\n\n"
        "Yi amfani da `/price bitcoin` ko `/price ethereum`"
    )
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def show_alert_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "🛎️ *Saita Faɗakarwa*\n\n"
        "Misali: `/alert ethereum 3000 up` ko `/alert bitcoin 25000 down`"
    )
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def show_chart_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "📊 *Chart na Coin*\n\n"
        "Yi amfani da `/chart bitcoin` ko `/chart ethereum`"
    )
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
