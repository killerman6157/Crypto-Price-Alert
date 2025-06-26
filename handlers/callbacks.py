from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def show_price_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    info_text = (
        "📈 *Duba Farashin Coin*\n\n"
        "Don duba farashin coin, yi amfani da umarnin `/price` sannan ka rubuta sunan coin din.\n\n"
        "Misali: `/price bitcoin` ko `/price ethereum`"
    )
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(info_text, reply_markup=reply_markup, parse_mode="Markdown")


async def show_alert_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    info_text = (
        "🛎️ *Saita Faɗakarwar Farashi*\n\n"
        "Yi amfani da `/alert` sannan ka rubuta sunan coin, farashi, da `up/down`.\n"
        "Misali: `/alert bitcoin 30000 up`"
    )
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(info_text, reply_markup=reply_markup, parse_mode="Markdown")


async def show_chart_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    info_text = (
        "📊 *Duba Chart na Coin*\n\n"
        "Yi amfani da `/chart` sannan ka rubuta sunan coin din.\n"
        "Misali: `/chart ethereum`"
    )
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(info_text, reply_markup=reply_markup, parse_mode="Markdown")


async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from handlers.general import send_main_menu
    await send_main_menu(update, context)
