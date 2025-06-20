# main.py – Crypto Price Bot (Termux & Python 3.12 compatible)

import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load token from .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


def get_crypto_price(coin: str) -> str:
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        price = data[coin]['usd']
        return f"💰 Current price of {coin.upper()}: ${price}"
    except:
        return "❌ Coin not found or API error. Try again with another coin."


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /price coin_name\nExample: /price bitcoin")
        return

    coin = context.args[0].lower()
    message = get_crypto_price(coin)
    await update.message.reply_text(message)


# == Direct run style, no asyncio.run() ==
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("price", price_command))

    print("🤖 Bot is running...")
    app.run_polling()  # this works without asyncio.run()


if __name__ == "__main__":
    main()
