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
import urllib.parse # Muhimmi: An ƙara wannan import din don URL encoding

# Load environment variables from .env file
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("⚠️ BOT_TOKEN bai da kyau ko bai samu ba daga .env file. Tabbatar ka saka BOT_TOKEN=... a cikin .env")

# SAITA ID DIN ADMIN ANAN!
# Ka canja '0000000000' zuwa naka Telegram User ID na gaske.
# Zaka iya samun ID din ka ta hanyar aika sako ga @userinfobot a Telegram.
ADMIN_USER_ID = 1234567890 # <-- CANJA WANNAN ZUWA NAKA ID NA TELEGRAM!

# URLs da sauran constants
COINGECKO_API_URL = "https://api.coingecko.com/api/v3" # An canja zuwa babban API URL
ALERTS_FILE = "alerts.json"
SETUP_GUIDE_LINK = "https://t.me/c/2544548450/3" # Link din Jagora

# ---- Functions for managing alerts (loading/saving) ----
def load_alerts():
    """Loads alerts from the JSON file."""
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logger.warning("alerts.json is empty or malformed, initializing with empty dictionary.")
                return {}
    return {}

def save_alerts(data):
    """Saves alerts to the JSON file."""
    with open(ALERTS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Load existing alerts when the bot starts
price_alerts = load_alerts()

# ---- Configure logging ----
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- Command Handlers ----

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends or edits the main menu message."""
    menu_text = (
        "🤖 *Crypto Price Bot Menu*\n"
        "Zaɓi ɗaya daga cikin abubuwa masu zuwa:"
    )
    keyboard = [
        [InlineKeyboardButton("📚 Setup Guide", url=SETUP_GUIDE_LINK)],
        [InlineKeyboardButton("📈 Duba Farashin Cryptocurrency", callback_data="show_price_info")],
        [InlineKeyboardButton("🛎️ Saita Faɗakarwar Farashi", callback_data="show_alert_info")],
        [InlineKeyboardButton("📋 Duba Faɗakarwarka", callback_data="my_alerts_button")],
        [InlineKeyboardButton("📊 Chart na Cryptocurrency", callback_data="show_chart_info")], # Sabon button din chart
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(menu_text, reply_markup=reply_markup, parse_mode="Markdown")
        except Exception as e:
            logger.warning(f"Failed to edit message for main menu: {e}. Sending new message.")
            await update.callback_query.message.reply_text(menu_text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.message:
        await update.message.reply_text(menu_text, reply_markup=reply_markup, parse_mode="Markdown")


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

async def show_chart_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provides information on how to use the /chart command."""
    query = update.callback_query
    await query.answer()
    info_text = (
        "📊 *Duba Chart na Cryptocurrency*\n\n"
        "Don ganin chart na coin, yi amfani da umarnin `/chart` sannan ka rubuta sunan coin din.\n\n"
        "Misali: `/chart bitcoin` ko `/chart ethereum`\n\n"
        "⚠️ *Lura:* Aikin chart yana fuskantar matsala a halin yanzu kuma bazai yi aiki ba." # Sabon bayani game da matsalar chart
    )
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(info_text, reply_markup=reply_markup, parse_mode="Markdown")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command and provides the initial welcome message with main menu buttons."""
    await send_main_menu(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provides help information."""
    help_message = (
        "📚 *Taimako da Bayani*\n\n"
        "Ga jerin umarnoni da zaka iya amfani dasu:\n"
        "`/start` - 🤖 Fara amfani da bot (Zai nuna babban menu)\n"
        "`/menu` - 📋 Nuna babban menu\n"
        "`/price <coin_name>` - 📈 Duba farashin coin (misali: `/price bitcoin`)\n"
        "`/alert <coin_name> <price> <up/down>` - 🛎️ Saita faɗakarwa (misali: `/alert ethereum 3000 up`)\n"
        "`/myalerts` - 📋 Duba faɗakarwar da aka saita\n"
        "`/cancelalert <coin_name>` - ❌ Soke faɗakarwa (misali: `/cancelalert bitcoin`)\n"
        "`/chart <coin_name>` - 📊 Duba chart na coin (misali: `/chart bitcoin`)\n\n"
        "⚠️ *Lura:* Aikin chart yana fuskantar matsala a halin yanzu kuma bazai yi aiki ba." # Sabon bayani
    )
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(help_message, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(help_message, reply_markup=reply_markup, parse_mode="Markdown")

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetches and displays detailed price information of a given cryptocurrency."""
    if not context.args:
        keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        sent_message = await update.message.reply_text(
            "Don Allah ka bayar da sunan coin. Misali: `/price bitcoin`",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        context.user_data['last_editable_message_id'] = sent_message.message_id
        context.user_data['last_editable_chat_id'] = sent_message.chat_id
        return

    await update.message.chat.send_action(action=ChatAction.TYPING)

    coin_query = " ".join(context.args).lower()
    price_message = ""
    coin_id = None
    coin_symbol = None
    coin_name_proper = None

    try:
        # Mataki 1: Sami coin_id da symbol daga CoinGecko search
        search_url = f"{COINGECKO_API_URL}/search?query={coin_query}"
        search_response = requests.get(search_url).json()
        
        for coin in search_response.get('coins', []):
            if coin['symbol'].lower() == coin_query or coin['name'].lower() == coin_query:
                coin_id = coin['id']
                coin_symbol = coin['symbol'].upper()
                coin_name_proper = coin['name']
                break
        
        if not coin_id:
            price_message = f"Ba a sami coin din '{coin_query}' ba. Don Allah tabbatar da sunan coin daidai ne."
        else:
            # Mataki 2: Sami cikakken bayani game da coin
            coin_details_url = f"{COINGECKO_API_URL}/coins/{coin_id}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false"
            coin_details_response = requests.get(coin_details_url).json()

            market_data = coin_details_response.get('market_data', {})
            
            current_price_usd = market_data.get('current_price', {}).get('usd')
            current_price_btc = market_data.get('current_price', {}).get('btc')
            
            # Canje-canje na yini ɗaya
            price_change_24h_percent = market_data.get('price_change_percentage_24h')
            
            # Canje-canje na awa ɗaya (ba koyaushe ake samunsu ba daga CoinGecko simple API)
            # Idan kuna buƙatar awa 1, zai iya buƙatar wani API call daban ko kuma ƙidaya da kanku idan kuna da data na baya.
            # A yanzu, zan sa "N/A"
            price_change_1h_percent = market_data.get('price_change_percentage_1h_in_currency', {}).get('usd') # Yana iya zama baya nan
            
            total_volume_usd = market_data.get('total_volume', {}).get('usd')
            market_cap_usd = market_data.get('market_cap', {}).get('usd')
            circulating_supply = market_data.get('circulating_supply')
            total_supply = market_data.get('total_supply')

            if current_price_usd is not None:
                # Tsarin sakon yadda kake so
                price_message = (
                    f"*{coin_name_proper} ({coin_symbol})*\n\n"
                    f"Farashi: ${current_price_usd:,.2f} USD\n"
                )
                if current_price_btc is not None:
                    price_message += f"Farashi: {current_price_btc:.8f} BTC\n"
                
                if price_change_1h_percent is not None:
                     price_message += f"Canji 1hr: {price_change_1h_percent:+.2f}%\n"
                else:
                     price_message += "Canji 1hr: N/A\n" # Idan babu bayanai
                
                if price_change_24h_percent is not None:
                    price_message += f"Canji 24hr: {price_change_24h_percent:+.2f}%\n"
                else:
                    price_message += "Canji 24hr: N/A\n"

                price_message += "\n" # Layi fanko

                if total_volume_usd is not None:
                    price_message += f"Volume: ${total_volume_usd:,.2f}\n"
                if market_cap_usd is not None:
                    price_message += f"Market Cap: ${market_cap_usd:,.2f}\n"
                if circulating_supply is not None:
                    price_message += f"Circulating Supply: {circulating_supply:,.0f}\n"
                if total_supply is not None:
                    price_message += f"Total Supply: {total_supply:,.0f}\n"
                
                # Link zuwa CoinMarketCap da CoinGecko
                coinmarketcap_link = f"https://coinmarketcap.com/currencies/{coin_id}/"
                coingecko_link = f"https://www.coingecko.com/en/coins/{coin_id}"

                price_message += (
                    f"\n🚀 [Duba a CoinMarketCap]({coinmarketcap_link})\n"
                    f"🦎 [Duba a CoinGecko]({coingecko_link})"
                )
            else:
                price_message = f"Ba a sami farashin {coin_name_proper} ba a yanzu. Gwada anjima."
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Kuskure yayin samun farashi (Network Error): {req_err}")
        price_message = "An samu kuskure ta hanyar sadarwa. Don Allah gwada anjima."
    except Exception as e:
        logger.error(f"Kuskure yayin samun farashi: {e}")
        price_message = "An samu kuskure yayin kokarin samun farashin. Don Allah gwada anjima."
    
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_message = await update.message.reply_text(price_message, reply_markup=reply_markup, parse_mode="Markdown")
    context.user_data['last_editable_message_id'] = sent_message.message_id
    context.user_data['last_editable_chat_id'] = sent_message.chat_id


async def set_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sets a price alert for a cryptocurrency."""
    alert_message = ""
    if len(context.args) < 3:
        alert_message = "Don Allah ka bayar da sunan coin, farashi, da kuma shugabanci (up/down). Misali: `/alert ethereum 3000 up`"
    else:
        coin_name = context.args[0].lower()
        try:
            target_price = float(context.args[1])
        except ValueError:
            alert_message = "Farashin da ka bayar ba lamba ba ce. Misali: `/alert ethereum 3000 up`"
        else:
            direction = context.args[2].lower()
            if direction not in ['up', 'down']:
                alert_message = "Shugabancin dole ne ya zama 'up' ko 'down'. Misali: `/alert ethereum 3000 up`"
            else:
                chat_id = update.effective_chat.id
                try:
                    search_url = f"{COINGECKO_API_URL}/search?query={coin_name}"
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
    
    sent_message = await update.message.reply_text(alert_message, reply_markup=reply_markup, parse_mode="Markdown")
    context.user_data['last_editable_message_id'] = sent_message.message_id
    context.user_data['last_editable_chat_id'] = sent_message.chat_id


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

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode="Markdown")
    else: # For direct command usage
        sent_message = await update.message.reply_text(message_text, reply_markup=reply_markup, parse_mode="Markdown")
        context.user_data['last_editable_message_id'] = sent_message.message_id
        context.user_data['last_editable_chat_id'] = sent_message.chat_id


async def cancel_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels a specific price alert."""
    cancel_message = ""
    if not context.args:
        cancel_message = "Don Allah ka bayar da sunan coin da zaka soke faɗakarwarsa. Misali: `/cancelalert bitcoin`"
    else:
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
            if not alerts:
                del price_alerts[chat_id]
            save_alerts(price_alerts)
            cancel_message = f"An soke faɗakarwa don {coin_name.capitalize()}."
        else:
            cancel_message = f"Ba a sami faɗakarwa don '{coin_name}' ba."
    
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_message = await update.message.reply_text(cancel_message, reply_markup=reply_markup, parse_mode="Markdown")
    context.user_data['last_editable_message_id'] = sent_message.message_id
    context.user_data['last_editable_chat_id'] = sent_message.chat_id


# === Aikin Chart (an ajiye shi na ɗan lokaci saboda matsalar) ===
async def send_price_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder function for chart, as it's currently problematic."""
    keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    sent_message = await update.message.reply_text(
        "⚠️ *Aikin chart yana fuskantar matsala a halin yanzu kuma bazai yi aiki ba.* Don Allah gwada anjima.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    context.user_data['last_editable_message_id'] = sent_message.message_id
    context.user_data['last_editable_chat_id'] = sent_message.chat_id
    return

    # Aikin chart na asali wanda muka ajiye na ɗan lokaci
    # Idan kana so ka sake gwadawa nan gaba, ka cire comment a ƙasan nan
    # (Sai ka cire wannan 'return' da ke sama kafin waɗannan)

    # if not context.args:
    #     keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
    #     reply_markup = InlineKeyboardMarkup(keyboard)
    #     sent_message = await update.message.reply_text(
    #         "Don Allah ka bayar da sunan coin don ganin chart. Misali: `/chart bitcoin`",
    #         reply_markup=reply_markup,
    #         parse_mode="Markdown"
    #     )
    #     context.user_data['last_editable_message_id'] = sent_message.message_id
    #     context.user_data['last_editable_chat_id'] = sent_message.chat_id
    #     return

    # await update.message.chat.send_action(action=ChatAction.UPLOAD_PHOTO)

    # coin_name = " ".join
