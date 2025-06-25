import requests
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from utils.alert_storage import price_alerts, save_alerts

logger = logging.getLogger(__name__)
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"

def get_coin_id(coin_name):
    """Search for a coin ID from CoinGecko based on name or symbol."""
    search_url = f"https://api.coingecko.com/api/v3/search?query={coin_name}"
    try:
        response = requests.get(search_url).json()
        for coin in response.get("coins", []):
            if coin["symbol"].lower() == coin_name or coin["name"].lower() == coin_name:
                return coin["id"]
    except Exception as e:
        logger.error(f"Kuskure yayin neman Coin ID: {e}")
    return None

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Don Allah saka sunan coin. Misali: `/price bitcoin`", parse_mode="Markdown")
        return

    await update.message.chat.send_action(action=ChatAction.TYPING)
    coin_name = " ".join(context.args).lower()
    coin_id = get_coin_id(coin_name)

    if not coin_id:
        await update.message.reply_text(f"Ba a samo coin '{coin_name}' ba. Tabbatar da sunan daidai ne.", parse_mode="Markdown")
        return

    try:
        params = {"ids": coin_id, "vs_currencies": "usd"}
        response = requests.get(COINGECKO_API_URL, params=params).json()
        price = response.get(coin_id, {}).get("usd")
        if price:
            text = f"Farashin {coin_name.capitalize()} a yanzu shine: ${price:,.2f}"
        else:
            text = f"Ba a samu farashin {coin_name} ba a yanzu."
    except Exception as e:
        logger.error(f"Kuskure wajen samun farashi: {e}")
        text = "An samu kuskure. Don Allah a gwada anjima."

    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def set_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text("Misali: `/alert ethereum 3000 up`", parse_mode="Markdown")
        return

    coin_name = context.args[0].lower()
    try:
        target_price = float(context.args[1])
    except ValueError:
        await update.message.reply_text("Farashin da ka saka bai dace ba. Misali: 3000", parse_mode="Markdown")
        return

    direction = context.args[2].lower()
    if direction not in ["up", "down"]:
        await update.message.reply_text("Shugabanci ya zama `up` ko `down` kawai.", parse_mode="Markdown")
        return

    coin_id = get_coin_id(coin_name)
    if not coin_id:
        await update.message.reply_text(f"Ba a samo coin '{coin_name}' ba.", parse_mode="Markdown")
        return

    chat_id = update.effective_chat.id
    if chat_id not in price_alerts:
        price_alerts[chat_id] = {}
    price_alerts[chat_id][coin_id] = {
        "target_price": target_price,
        "direction": direction,
        "original_coin_name": coin_name
    }
    save_alerts(price_alerts)

    msg = f"✅ An saita faɗakarwa don {coin_name.capitalize()} a ${target_price:,.2f} ({direction})"
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def my_alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    alerts = price_alerts.get(chat_id, {})

    if not alerts:
        msg = "Ba ku da faɗakarwa a yanzu."
    else:
        msg = "📋 *Faɗakarwarku:*\n"
        for coin_id, info in alerts.items():
            msg += f"- {info['original_coin_name'].capitalize()}: ${info['target_price']:,.2f} ({info['direction']})\n"

    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def cancel_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Misali: `/cancelalert bitcoin`", parse_mode="Markdown")
        return

    coin_name = " ".join(context.args).lower()
    chat_id = update.effective_chat.id
    alerts = price_alerts.get(chat_id, {})
    to_remove = None

    for coin_id, info in alerts.items():
        if info.get("original_coin_name", coin_id).lower() == coin_name:
            to_remove = coin_id
            break

    if to_remove:
        del alerts[to_remove]
        if not alerts:
            del price_alerts[chat_id]
        save_alerts(price_alerts)
        msg = f"❌ An soke faɗakarwa don {coin_name.capitalize()}."
    else:
        msg = f"Ba a sami faɗakarwa don '{coin_name}' ba."

    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
