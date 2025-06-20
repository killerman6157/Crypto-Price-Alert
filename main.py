import logging import requests from telegram import Update from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

Saita logging don ganin abubuwan da ke faruwa

logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO ) logger = logging.getLogger(name)

Wannan shi ne Telegram bot token dinka da ka samu daga @BotFather

KA CANZA WANNAN DA TOKEN DINKA NA GASKIYA!

TELEGRAM_BOT_TOKEN = "KA_SA_TELEGRAM_BOT_TOKEN_ANAN"

CoinGecko API URL

COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"

Wannan zai adana faɗakarwar farashin ga kowane mai amfani

Tsarin: {chat_id: {coin_id: {'target_price': float, 'direction': 'up'/'down'}}}

price_alerts = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: await update.message.reply_text( "Sannu! Ni ne bot dinka na Crypto Price Alert.\n" "Zan iya taimaka maka samun farashin cryptocurrency da kuma saita faɗakarwa.\n\n" "Amfani:\n" "/price <sunan_coin> - Don samun farashin wani coin misali: /price bitcoin\n" "/alert <sunan_coin> <farashi> <up/down> - Don saita faɗakarwa misali: /alert ethereum 3000 up\n" "/myalerts - Don ganin faɗakarwarku\n" "/cancelalert <sunan_coin> - Don soke faɗakarwa" )

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: if not context.args: await update.message.reply_text("Don Allah ka bayar da sunan coin. Misali: /price bitcoin") return

coin_name = " ".join(context.args).lower()
try:
    search_url = f"https://api.coingecko.com/api/v3/search?query={coin_name}"
    search_response = requests.get(search_url).json()

    coin_id = None
    if search_response and 'coins' in search_response:
        for coin in search_response['coins']:
            if coin['symbol'].lower() == coin_name or coin['name'].lower() == coin_name:
                coin_id = coin['id']
                break

    if not coin_id:
        await update.message.reply_text(f"Ba a sami coin din '{coin_name}' ba. Don Allah tabbatar da sunan coin daidai ne.")
        return

    params = {
        "ids": coin_id,
        "vs_currencies": "usd"
    }
    response = requests.get(COINGECKO_API_URL, params=params)
    data = response.json()

    if coin_id in data and 'usd' in data[coin_id]:
        price = data[coin_id]['usd']
        await update.message.reply_text(f"Farashin {coin_name.capitalize()} a yanzu shine: ${price:,.2f}")
    else:
        await update.message.reply_text(f"Ba a sami farashin {coin_name} ba a yanzu. Gwada anjima.")
except Exception as e:
    logger.error(f"Kuskure yayin samun farashi: {e}")
    await update.message.reply_text("An samu kuskure yayin kokarin samun farashin. Don Allah gwada anjima.")

async def set_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: if len(context.args) < 3: await update.message.reply_text( "Don Allah ka bayar da sunan coin, farashi, da kuma shugabanci (up/down).\n" "Misali: /alert ethereum 3000 up" ) return

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
    if search_response and 'coins' in search_response:
        for coin in search_response['coins']:
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

    await update.message.reply_text(
        f"An saita faɗakarwa don {coin_name.capitalize()}: lokacin da farashin ya kai ${target_price:,.2f} ko kuma ya wuce shi ({direction})."
    )
except Exception as e:
    logger.error(f"Kuskure yayin saita faɗakarwa: {e}")
    await update.message.reply_text("An samu kuskure yayin saita faɗakarwa. Don Allah gwada anjima.")

async def my_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: chat_id = update.effective_chat.id if chat_id not in price_alerts or not price_alerts[chat_id]: await update.message.reply_text("Ba ku da faɗakarwar farashi a yanzu.") return

message = "Faɗakarwarku na farashin:\n"
for coin_id, alert_info in price_alerts[chat_id].items():
    original_coin_name = alert_info.get('original_coin_name', coin_id)
    message += (
        f"- {original_coin_name.capitalize()}: ${alert_info['target_price']:,.2f} ({alert_info['direction']})\n"
    )
await update.message.reply_text(message)

async def cancel_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: if not context.args: await update.message.reply_text("Don Allah ka bayar da sunan coin da zaka soke faɗakarwarsa. Misali: /cancelalert bitcoin") return

coin_name_to_cancel = " ".join(context.args).lower()
chat_id = update.effective_chat.id

if chat_id not in price_alerts or not price_alerts[chat_id]:
    await update.message.reply_text("Ba ku da faɗakarwar farashi da za a soke.")
    return

coin_id_to_remove = None
for coin_id, alert_info in price_alerts[chat_id].items():
    if alert_info.get('original_coin_name', coin_id).lower() == coin_name_to_cancel:
        coin_id_to_remove = coin_id
        break

if coin_id_to_remove and coin_id_to_remove in price_alerts[chat_id]:
    del price_alerts[chat_id][coin_id_to_remove]
    await update.message.reply_text(f"An soke faɗakarwa don {coin_name_to_cancel.capitalize()}.")
else:
    await update.message.reply_text(f"Ba a sami faɗakarwa don '{coin_name_to_cancel}' ba.")

async def check_alerts(context: ContextTypes.DEFAULT_TYPE) -> None: for chat_id, alerts_for_user in list(price_alerts.items()): for coin_id, alert_info in list(alerts_for_user.items()): try: params = { "ids": coin_id, "vs_currencies": "usd" } response = requests.get(COINGECKO_API_URL, params=params) data = response.json()

if coin_id in data and 'usd' in data[coin_id]:
                current_price = data[coin_id]['usd']
                target_price = alert_info['target_price']
                direction = alert_info['direction']
                original_coin_name = alert_info.get('original_coin_name', coin_id)

                send_alert = False
                if direction == 'up' and current_price >= target_price:
                    send_alert = True
                    message = (
                        f"📣 Faɗakarwa! Farashin {original_coin_name.capitalize()} ya kai "
                        f"${current_price:,.2f}, wanda ya kai ko ya wuce ${target_price:,.2f} da ka saita."
                    )
                elif direction == 'down' and current_price <= target_price:
                    send_alert = True
                    message = (
                        f"📣 Faɗakarwa! Farashin {original_coin_name.capitalize()} ya fado zuwa "
                        f"${current_price:,.2f}, wanda ya kai ko ya fado kasa da ${target_price:,.2f} da ka saita."
                    )

                if send_alert:
                    await context.bot.send_message(chat_id=chat_id, text=message)
                    del price_alerts[chat_id][coin_id]
                    if not price_alerts[chat_id]:
                        del price_alerts[chat_id]
            else:
                logger.warning(f"Ba a sami farashin {coin_id} ba yayin duba faɗakarwa.")
        except Exception as e:
            logger.error(f"Kuskure yayin duba faɗakarwa don {coin_id}: {e}")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: await update.message.reply_text("Ban gane wannan umarnin ba. Don Allah gwada umarni kamar /start ko /help.")

def main() -> None: application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", start))
application.add_handler(CommandHandler("price", get_price))
application.add_handler(CommandHandler("alert", set_alert))
application.add_handler(CommandHandler("myalerts", my_alerts))
application.add_handler(CommandHandler("cancelalert", cancel_alert))
application.add_handler(MessageHandler(filters.COMMAND, unknown))

job_queue = application.job_queue
job_queue.run_repeating(check_alerts, interval=300, first=10)

logger.info("Bot yana farawa...")
application.run_polling(allowed_updates=Update.ALL_TYPES)

if name == "main": main()

