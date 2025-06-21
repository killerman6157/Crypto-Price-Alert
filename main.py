import os
import logging
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
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
    """Loads alerts from the JSON file."""
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # Handle empty or malformed JSON file
                logger.warning("alerts.json is empty or malformed, initializing with empty dictionary.")
                return {}
    return {}

def save_alerts(data):
    """Saves alerts to the JSON file."""
    with open(ALERTS_FILE, "w") as f:
        json.dump(data, f, indent=2)

price_alerts = load_alerts()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends or edits the main menu message."""
    menu_text = (
        "🤖 *Crypto Price Bot Menu*\n"
        "Zaɓi ɗaya daga cikin abubuwa masu zuwa:"
    )
    # Changed the main menu buttons as per requirements
    keyboard = [
        [InlineKeyboardButton("📈 Duba Farashin Cryptocurrency", callback_data="show_price_info")],
        [InlineKeyboardButton("🛎️ Saita Faɗakarwar Farashi", callback_data="show_alert_info")],
        [InlineKeyboardButton("📋 Duba Faɗakarwarka", callback_data="my_alerts_button")], # Changed callback_data
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(menu_text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup, parse_mode="Markdown")

async def show_price_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provides information on how to use the /price command."""
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
    """Provides information on how to use the /alert command."""
    query = update.callback_query
    await query.answer()
    info_text = (
        "🛎️ *Saita Faɗakarwar Farashi*\n\n"
        "Don saita faɗakarwa, yi amfani da umarnin `/alert` sannan ka rubuta sunan coin, adadin, da kuma 'up' ko 'down'.\n\n"
        "Misali: `/alert ethereum 3000 up` (Idan farashin Ethereum ya kai $3000 ko sama, ka fada min)\n"
        "Misali: `/alert bitcoin 25000 down` (Idan farashin Bitcoin ya faɗi kasa da $25000, ka fada min)"
    )
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(info_text, reply_markup=reply_markup, parse_mode="Markdown")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command and provides the initial welcome message."""
    welcome_message = (
        "🤖 *Barka da zuwa Crypto Price Bot!* 🤖\n\n"
        "Ni ne bot din da zai taimaka maka duba farashin cryptocurrencies da kuma saita faɗakarwar farashi.\n\n"
        "Ga yadda zaka yi amfani da ni:\n"
        "`/start` - 🤖 Fara amfani da bot\n"
        "`/menu` - 📋 Nuna babban menu\n"
        "`/price <coin_name>` - 📈 Duba farashin coin (misali: `/price bitcoin`)\n"
        "`/alert <coin_name> <price> <up/down>` - 🛎️ Saita faɗakarwa (misali: `/alert ethereum 3000 up`)\n"
        "`/myalerts` - 📋 Duba faɗakarwar da aka saita\n"
        "`/cancelalert <coin_name>` - ❌ Soke faɗakarwa (misali: `/cancelalert bitcoin`)\n"
        "`/help` - 📚 Taimako da bayani"
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provides help information."""
    help_message = (
        "📚 *Taimako da Bayani*\n\n"
        "Ga jerin umarnoni da zaka iya amfani dasu:\n"
        "`/start` - 🤖 Fara amfani da bot\n"
        "`/menu` - 📋 Nuna babban menu\n"
        "`/price <coin_name>` - 📈 Duba farashin coin (misali: `/price bitcoin`)\n"
        "`/alert <coin_name> <price> <up/down>` - 🛎️ Saita faɗakarwa (misali: `/alert ethereum 3000 up`)\n"
        "`/myalerts` - 📋 Duba faɗakarwar da aka saita\n"
        "`/cancelalert <coin_name>` - ❌ Soke faɗakarwa (misali: `/cancelalert bitcoin`)"
    )
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(help_message, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(help_message, reply_markup=reply_markup, parse_mode="Markdown")

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetches and displays the price of a given cryptocurrency."""
    if not context.args:
        keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Don Allah ka bayar da sunan coin. Misali: `/price bitcoin`",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    await update.message.chat.send_action(action=ChatAction.TYPING)

    coin_name = " ".join(context.args).lower()
    price_message = ""
    try:
        search_url = f"https://api.coingecko.com/api/v3/search?query={coin_name}"
        search_response = requests.get(search_url).json()
        coin_id = None
        for coin in search_response.get('coins', []):
            if coin['symbol'].lower() == coin_name or coin['name'].lower() == coin_name:
                coin_id = coin['id']
                break
        if not coin_id:
            price_message = f"Ba a sami coin din '{coin_name}' ba. Don Allah tabbatar da sunan coin daidai ne."
        else:
            params = {"ids": coin_id, "vs_currencies": "usd"}
            response = requests.get(COINGECKO_API_URL, params=params).json()
            price = response.get(coin_id, {}).get('usd')
            if price is not None:
                price_message = f"Farashin {coin_name.capitalize()} a yanzu shine: ${price:,.2f}"
            else:
                price_message = f"Ba a sami farashin {coin_name} ba a yanzu. Gwada anjima."
    except Exception as e:
        logger.error(f"Kuskure yayin samun farashi: {e}")
        price_message = "An samu kuskure yayin kokarin samun farashin. Don Allah gwada anjima."
    
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(price_message, reply_markup=reply_markup, parse_mode="Markdown")

async def set_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sets a price alert for a cryptocurrency."""
    if len(context.args) < 3:
        keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Don Allah ka bayar da sunan coin, farashi, da kuma shugabanci (up/down). Misali: `/alert ethereum 3000 up`",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    coin_name = context.args[0].lower()
    try:
        target_price = float(context.args[1])
    except ValueError:
        keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Farashin da ka bayar ba lamba ba ce. Misali: `/alert ethereum 3000 up`",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    direction = context.args[2].lower()
    if direction not in ['up', 'down']:
        keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Shugabancin dole ne ya zama 'up' ko 'down'. Misali: `/alert ethereum 3000 up`",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    chat_id = update.effective_chat.id
    alert_message = ""
    try:
        search_url = f"https://api.coingecko.com/api/v3/search?query={coin_name}"
        search_response = requests.get(search_url).json()
        coin_id = None
        for coin in search_response.get('coins', []):
            if coin['symbol'].lower() == coin_name or coin['name'].lower() == coin_name:
                coin_id = coin['id']
                break
        if not coin_id:
            alert_message = f"Ba a sami coin din '{coin_name}' ba. Don Allah tabbatar da sunan coin daidai ne."
        else:
            if chat_id not in price_alerts:
                price_alerts[chat_id] = {}
            price_alerts[chat_id][coin_id] = {
                'target_price': target_price,
                'direction': direction,
                'original_coin_name': coin_name
            }
            save_alerts(price_alerts)
            alert_message = f"An saita faɗakarwa don {coin_name.capitalize()}: lokacin da farashin ya kai ${target_price:,.2f} ({direction})."
    except Exception as e:
        logger.error(f"Kuskure yayin saita faɗakarwa: {e}")
        alert_message = "An samu kuskure yayin saita faɗakarwa. Don Allah gwada anjima."

    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(alert_message, reply_markup=reply_markup, parse_mode="Markdown")


async def my_alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the list of active price alerts for the user."""
    chat_id = update.effective_chat.id
    alerts = price_alerts.get(chat_id, {})
    message_text = ""
    if not alerts:
        message_text = "Ba ku da faɗakarwar farashi a yanzu."
    else:
        message_text = "📋 *Faɗakarwarku na farashin:*\n"
        for coin_id, info in alerts.items():
            name = info.get('original_coin_name', coin_id)
            message_text += f"- {name.capitalize()}: ${info['target_price']:,.2f} ({info['direction']})\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(message_text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode="Markdown")


async def cancel_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels a specific price alert."""
    if not context.args:
        keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Don Allah ka bayar da sunan coin da zaka soke faɗakarwarsa. Misali: `/cancelalert bitcoin`",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    coin_name = " ".join(context.args).lower()
    chat_id = update.effective_chat.id
    alerts = price_alerts.get(chat_id, {})
    to_remove = None
    cancel_message = ""
    for coin_id, info in alerts.items():
        if info.get('original_coin_name', coin_id).lower() == coin_name:
            to_remove = coin_id
            break
    
    if to_remove:
        del alerts[to_remove]
        if not alerts: # If no alerts left for the user, remove their entry
            del price_alerts[chat_id]
        save_alerts(price_alerts)
        cancel_message = f"An soke faɗakarwa don {coin_name.capitalize()}."
    else:
        cancel_message = f"Ba a sami faɗakarwa don '{coin_name}' ba."
    
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(cancel_message, reply_markup=reply_markup, parse_mode="Markdown")

async def check_alerts(context: ContextTypes.DEFAULT_TYPE):
    """Periodically checks current prices against set alerts and notifies users."""
    for chat_id, alerts in list(price_alerts.items()):
        for coin_id, info in list(alerts.items()):
            try:
                response = requests.get(COINGECKO_API_URL, params={"ids": coin_id, "vs_currencies": "usd"}).json()
                current_price = response.get(coin_id, {}).get('usd')
                if current_price is None:
                    continue # Skip if price not available for some reason
                
                target_price = info['target_price']
                direction = info['direction']
                name = info.get('original_coin_name', coin_id)

                alert_triggered = False
                if direction == 'up' and current_price >= target_price:
                    alert_triggered = True
                elif direction == 'down' and current_price <= target_price:
                    alert_triggered = True
                
                if alert_triggered:
                    msg = f"📣 Faɗakarwa! Farashin {name.capitalize()} ya kai ${current_price:,.2f}, wanda ya kai ko ya wuce ${target_price:,.2f} da ka saita."
                    await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")
                    # Remove the alert after it's triggered
                    del alerts[coin_id]
            except Exception as e:
                logger.error(f"Kuskure yayin duba faɗakarwa don {coin_id}: {e}")
        
        # If no alerts left for this chat, remove the chat entry
        if not alerts:
            del price_alerts[chat_id]
    save_alerts(price_alerts)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles unknown commands."""
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Ban gane wannan umarnin ba. Don Allah gwada umarni kamar `/menu` ko `/price bitcoin`.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles all callback queries from inline keyboard buttons."""
    query = update.callback_query
    await query.answer()

    if query.data == "back_to_main_menu":
        await send_main_menu(update, context)
    elif query.data == "show_price_info":
        await show_price_info(update, context)
    elif query.data == "show_alert_info":
        await show_alert_info(update, context)
    elif query.data == "my_alerts_button": # This will now call my_alerts_command
        await my_alerts_command(update, context)
    # The 'guide' callback_data is now handled by help_command
    elif query.data == "guide":
        await help_command(update, context)


def main():
    """Starts the bot."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command Handlers
    app.add_handler(CommandHandler("start", start_command)) # Changed to start_command for initial message
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", send_main_menu))
    app.add_handler(CommandHandler("price", get_price))
    app.add_handler(CommandHandler("alert", set_alert))
    app.add_handler(CommandHandler("myalerts", my_alerts_command)) # Changed to my_alerts_command
    app.add_handler(CommandHandler("cancelalert", cancel_alert))

    # Message Handler for unknown commands
    app.add_handler(MessageHandler(filters.COMMAND, unknown))
    
    # Callback Query Handler for inline keyboard buttons
    app.add_handler(CallbackQueryHandler(button_handler)) # Single handler for all button clicks

    # Job Queue for checking alerts
    app.job_queue.run_repeating(check_alerts, interval=300, first=10) # Checks every 5 minutes (300 seconds)

    logger.info("Bot is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
    
