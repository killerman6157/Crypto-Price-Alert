# main.py – gyaran asyncio event loop issue

import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import asyncio

# Load .env
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


async def start_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("price", price_command))
    print("🤖 Bot is running...")
    await app.run_polling()


# == Run safely inside existing asyncio event loop ==
if __name__ == '__main__':
    try:
        asyncio.run(start_bot())
    except RuntimeError as e:
        if str(e).startswith("This event loop is already running"):
            loop = asyncio.get_event_loop()
            loop.create_task(start_bot())
            loop.run_forever()
        else:
            raise
