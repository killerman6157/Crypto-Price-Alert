import os
import logging
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("⚠️ BOT_TOKEN bai da kyau ko bai samu ba daga .env file. Tabbatar ka saka BOT_TOKEN=... a cikin .env")

COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"
ALERTS_FILE = "alerts.json"

def load_alerts():
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_alerts(data):
    with open(ALERTS_FILE, "w") as f:
        json.dump(data, f, indent=2)

price_alerts = load_alerts()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Sannu! Ni ne bot dinka na Crypto Price Alert.\n"
        "Zan iya taimaka maka samun farashin cryptocurrency da kuma saita faɗakarwa.\n\n"
        "Amfani:\n"
        "/price <sunan_coin> - Don samun farashin wani coin misali: /price bitcoin\n"
        "/alert <sunan_coin> <farashi> <up/down> - Don saita faɗakarwa misali: /alert ethereum 3000 up\n"
        "/myalerts - Don ganin faɗakarwarku\n"
        "/cancelalert <sunan_coin> - Don soke faɗakarwa"
    )

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Don Allah ka bayar da sunan coin. Misali: /price bitcoin")
        return

    coin_name = " ".join(context.args).lower()
    try:
        search_url = f"https://api.coingecko.com/api/v3/search?query={coin_name}"
        search_response = requests.get(search_url).json()
        coin_id = None
        for coin in search_response.get('coins', []):
            if coin['symbol'].lower() == coin_name or coin['name'].lower() == coin_name:
                coin_id = coin['id']
                break
        if not coin_id:
            await update.message.reply_text(f"Ba a sami coin din '{coin_name}' ba. Don Allah tabbatar da sunan coin daidai ne.")
            return
        params = {"ids": coin_id, "vs_currencies": "usd"}
        response = requests.get(COINGECKO_API_URL, params=params).json()
        price = response.get(coin_id, {}).get('usd')
        if price is not None:
            await update.message.reply_text(f"Farashin {coin_name.capitalize()} a yanzu shine: ${price:,.2f}")
        else:
            await update.message.reply_text(f"Ba a sami farashin {coin_name} ba a yanzu. Gwada anjima.")
    except Exception as e:
        logger.error(f"Kuskure yayin samun farashi: {e}")
        await update.message.reply_text("An samu kuskure yayin kokarin samun farashin. Don Allah gwada anjima.")

async def set_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text("Don Allah ka bayar da sunan coin, farashi, da kuma shugabanci (up/down). Misali: /alert ethereum 3000 up")
        return
    coin_name = context.args[0].lower()
    try:
        target_price = float(context.args[1])
    except ValueError:
        await update.message.reply_text("Farashin da ka bayar ba lamba ba ce. Misali: /alert ethereum 3000 up")
        return
    direction = context.args[2].lower()
    if direction not in ['up', 'down']:
        await update.message.reply_text("Shugabancin dole ne ya zama 'up' ko 'down'. Misali: /alert ethereum 3000 up")
        return
    chat_id = update.effective_chat.id
    try:
        search_url = f"https://api.coingecko.com/api/v3/search?query={coin_name}"
        search_response = requests.get(search_url).json()
        coin_id = None
        for coin in search_response.get('coins', []):
            if coin['symbol'].lower() == coin_name or coin['name'].lower() == coin_name:
                coin_id = coin['id']
                break
        if not coin_id:
            await update.message.reply_text(f"Ba a sami coin din '{coin_name}' ba. Don Allah tabbatar da sunan coin daidai ne.")
            return
        if chat_id not in price_alerts:
            price_alerts[chat_id] = {}
        price_alerts[chat_id][coin_id] = {
            'target_price': target_price,
            'direction': direction,
            'original_coin_name': coin_name
        }
        save_alerts(price_alerts)
        await update.message.reply_text(
            f"An saita faɗakarwa don {coin_name.capitalize()}: lokacin da farashin ya kai ${target_price:,.2f} ({direction}).")
    except Exception as e:
        logger.error(f"Kuskure yayin saita faɗakarwa: {e}")
        await update.message.reply_text("An samu kuskure yayin saita faɗakarwa. Don Allah gwada anjima.")

async def my_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    alerts = price_alerts.get(chat_id, {})
    if not alerts:
        await update.message.reply_text("Ba ku da faɗakarwar farashi a yanzu.")
        return
    message = "Faɗakarwarku na farashin:\n"
    for coin_id, info in alerts.items():
        name = info.get('original_coin_name', coin_id)
        message += f"- {name.capitalize()}: ${info['target_price']:,.2f} ({info['direction']})\n"
    await update.message.reply_text(message)

async def cancel_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Don Allah ka bayar da sunan coin da zaka soke faɗakarwarsa. Misali: /cancelalert bitcoin")
        return
    coin_name = " ".join(context.args).lower()
    chat_id = update.effective_chat.id
    alerts = price_alerts.get(chat_id, {})
    to_remove = None
    for coin_id, info in alerts.items():
        if info.get('original_coin_name', coin_id).lower() == coin_name:
            to_remove = coin_id
            break
    if to_remove:
        del alerts[to_remove]
        save_alerts(price_alerts)
        await update.message.reply_text(f"An soke faɗakarwa don {coin_name.capitalize()}.")
    else:
        await update.message.reply_text(f"Ba a sami faɗakarwa don '{coin_name}' ba.")

async def check_alerts(context: ContextTypes.DEFAULT_TYPE):
    for chat_id, alerts in list(price_alerts.items()):
        for coin_id, info in list(alerts.items()):
            try:
                response = requests.get(COINGECKO_API_URL, params={"ids": coin_id, "vs_currencies": "usd"}).json()
                current_price = response.get(coin_id, {}).get('usd')
                if current_price is None:
                    continue
                target_price = info['target_price']
                direction = info['direction']
                name = info.get('original_coin_name', coin_id)
                if (direction == 'up' and current_price >= target_price) or (direction == 'down' and current_price <= target_price):
                    msg = f"📣 Faɗakarwa! Farashin {name.capitalize()} ya kai ${current_price:,.2f}, wanda ya kai ko ya wuce ${target_price:,.2f} da ka saita."
                    await context.bot.send_message(chat_id=chat_id, text=msg)
                    del alerts[coin_id]
            except Exception as e:
                logger.error(f"Kuskure yayin duba faɗakarwa don {coin_id}: {e}")
        if not alerts:
            del price_alerts[chat_id]
    save_alerts(price_alerts)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ban gane wannan umarnin ba. Don Allah gwada umarni kamar /start ko /help.")

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("✅ Ka dawo zuwa menu.", reply_markup=main_menu_keyboard())
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("✅ Ka dawo zuwa menu.", reply_markup=main_menu_keyboard())

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📈 Farashi", callback_data="price")],
        [InlineKeyboardButton("🛎️ Saita Faɗakarwa", callback_data="alert")],
        [InlineKeyboardButton("📚 Jagora", callback_data="guide")],
        [InlineKeyboardButton("🔙 Komawa Menu", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("price", get_price))
    app.add_handler(CommandHandler("alert", set_alert))
    app.add_handler(CommandHandler("myalerts", my_alerts))
    app.add_handler(CommandHandler("cancelalert", cancel_alert))
    app.add_handler(CommandHandler("back", back_to_menu))
    app.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back$"))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))
    app.job_queue.run_repeating(check_alerts, interval=300, first=10)
    logger.info("Bot yana farawa...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
