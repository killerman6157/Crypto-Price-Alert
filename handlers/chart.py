import requests
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def send_price_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "🪙 Don Allah ka bayar da sunan coin. Misali: `/chart ethereum`"
        )
        return

    coin_name = " ".join(context.args).lower()

    try:
        # Nemi Coin ID daga CoinGecko
        search_url = f"https://api.coingecko.com/api/v3/search?query={coin_name}"
        search_response = requests.get(search_url).json()

        coin_id = None
        symbol = None
        full_name = None

        for coin in search_response.get("coins", []):
            if coin["symbol"].lower() == coin_name or coin["name"].lower() == coin_name:
                coin_id = coin["id"]
                symbol = coin["symbol"]
                full_name = coin["name"]
                break

        if not coin_id:
            await update.message.reply_text("❌ Ba a sami coin ɗin ba. Tabbatar da sunan.")
            return

        # Ƙirƙiri Links
        cmc_link = f"https://coinmarketcap.com/currencies/{coin_id}/"
        gecko_link = f"https://www.coingecko.com/en/coins/{coin_id}"
        tv_symbol = f"{symbol.upper()}USD"
        tv_link = f"https://www.tradingview.com/symbols/{tv_symbol}/"

        # Sakon da za'a tura
        message = (
            f"*{full_name} ({symbol.upper()})*\n\n"
            f"🔗 *Duba chart da cikakken bayani:*\n"
            f"• [CoinMarketCap]({cmc_link})\n"
            f"• [CoinGecko]({gecko_link})\n"
            f"• [TradingView]({tv_link})"
        )

        # Button na "Komawa Menu"
        keyboard = [[InlineKeyboardButton("🔙 Komawa Menu", callback_data="back_to_main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Kuskure yayin samun chart links: {e}")
        await update.message.reply_text("❌ An samu kuskure yayin kokarin samo chart. Don Allah a sake gwadawa.")
