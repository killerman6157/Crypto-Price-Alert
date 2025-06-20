# main.py – Crypto Price Bot using CoinGecko API

import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

# === Load the BOT token from .env file ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


# === Function to get price from CoinGecko ===
def get_crypto_price(coin: str) -> str:
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        price = data[coin]['usd']
        return f"💰 Current price of {coin.upper()}: ${price}"
    except:
        return "❌ Coin not found or API error. Try again with another coin."


# === /price command handler ===
async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /price coin_name\nExample: /price bitcoin")
        return

    coin = context.args[0].lower()
    message = get_crypto_price(coin)
    await update.message.reply_text(message)


# === Main function to start the bot ===
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("price", price_command))

    print("🤖 Bot is running...")
    await app.run_polling()


# === Entry point ===
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
