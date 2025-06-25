import requests
import json
import urllib.parse
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def send_price_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
        await update.message.reply_text(
            "Don Allah ka bayar da sunan coin don ganin chart. Misali: `/chart bitcoin`",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    await update.message.chat.send_action(action=ChatAction.UPLOAD_PHOTO)

    coin_name = " ".join(context.args).lower()
    search_url = f"https://api.coingecko.com/api/v3/search?query={coin_name}"

    try:
        search_response = requests.get(search_url).json()
        coin_id = None
        for coin in search_response.get('coins', []):
            if coin['symbol'].lower() == coin_name or coin['name'].lower() == coin_name:
                coin_id = coin['id']
                break

        if not coin_id:
            await update.message.reply_text(
                f"Ba a samo coin '{coin_name}' ba. Don Allah tabbatar da sunan coin daidai ne.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]),
                parse_mode="Markdown"
            )
            return

        ohlc_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days=3"
        ohlc_response = requests.get(ohlc_url).json()

        if not ohlc_response:
            await update.message.reply_text(
                f"Ba a samo bayanan chart na '{coin_name}' ba a yanzu.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]),
                parse_mode="Markdown"
            )
            return

        # Tsara bayanan candlestick
        candlestick_data = [{
            "x": data[0],
            "o": data[1],
            "h": data[2],
            "l": data[3],
            "c": data[4]
        } for data in ohlc_response]

        chart_config = {
            "type": "candlestick",
            "data": {
                "datasets": [{
                    "label": f"{coin_name.capitalize()} Price",
                    "data": candlestick_data,
                    "borderColor": "rgba(75, 192, 192, 1)"
                }]
            },
            "options": {
                "scales": {
                    "x": {
                        "type": "time",
                        "time": {
                            "unit": "day"
                        },
                        "title": {
                            "display": True,
                            "text": "Kwanaki"
                        }
                    },
                    "y": {
                        "title": {
                            "display": True,
                            "text": "Farashi (USD)"
                        }
                    }
                },
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"{coin_name.capitalize()} Candlestick Chart (Kwana 3)"
                    }
                }
            }
        }

        encoded_config = urllib.parse.quote_plus(json.dumps(chart_config))
        quickchart_url = f"https://quickchart.io/chart?width=800&height=400&c={encoded_config}"

        keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
        await update.message.reply_photo(
            photo=quickchart_url,
            caption=f"Candlestick Chart na {coin_name.capitalize()} (Kwana 3)",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        logger.error(f"Kuskure yayin ƙirƙirar chart: {e}")
        await update.message.reply_text(
            "Kuskure ya faru yayin ƙirƙirar chart. Don Allah gwada anjima.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]),
            parse_mode="Markdown"
        )
