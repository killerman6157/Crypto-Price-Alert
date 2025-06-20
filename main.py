# main.py — Crypto Price Bot (Stable event loop version)

import os
import requests
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Load token
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


# Get price from CoinGecko
def get_crypto_price(coin: str) -> str:
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    try:
        res = requests.get(url)
        data = res.json()
        price = data[coin]["usd"]
        return f"💰 Current price of {coin.upper()}: ${price}"
    except:
        return "❌ Coin not found or API error."


# Bot command handler
async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /price coin_name\nExample: /price bitcoin")
        return
    coin = context.args[0].lower()
    msg = get_crypto_price(coin)
    await update.message.reply_text(msg)


# Manual asyncio approach (NO asyncio.run())
async def start():
    print("🤖 Bot is starting...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("price", price_command))

    await app.initialize()
    await app.start()
    print("✅ Bot is running.")
    await app.updater.start_polling()
    await app.updater.idle()


# Run inside existing loop or new one
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.create_task(start())
    loop.run_forever()
