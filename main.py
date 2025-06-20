import os
import requests
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load token
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Check if BOT_TOKEN is loaded
if not BOT_TOKEN:
    logger.error("BOT_TOKEN not found in environment variables. Please set it in your .env file.")
    exit(1) # Exit if no token

# Get price from CoinGecko
async def get_crypto_price(coin: str) -> str:
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    try:
        res = await asyncio.to_thread(requests.get, url, timeout=10)
        res.raise_for_status()
        data = res.json()

        if coin in data and "usd" in data[coin]:
            price = data[coin]["usd"]
            return f"💰 Current price of {coin.upper()}: ${price}"
        else:
            return f"❌ Ba a sami bayanan farashin {coin} ba."
    except requests.exceptions.Timeout:
        logger.error(f"Timeout error when fetching price for {coin}: API took too long to respond.")
        return "❌ API ya ɗauki lokaci mai tsawo don amsawa. Da fatan za a sake gwadawa daga baya."
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching price for {coin}: {e}")
        return "❌ An sami kuskure yayin haɗi zuwa API. Da fatan za a gwada daga baya."
    except KeyError:
        logger.error(f"KeyError: Coin '{coin}' not found in API response data: {data}")
        return "❌ Ba a sami Coin ba ko kuma an sami kuskure a API. Ka tabbata sunan coin ɗin daidai ne."
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return "❌ An sami kuskure da ba zato ba tsammani."


# Bot command handler
async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Yadda ake amfani: `/price sunan_coin`\nMisali: `/price bitcoin`")
        return
    coin = context.args[0].lower()
    await update.message.reply_text(f"Neman farashin {coin}...")
    msg = await get_crypto_price(coin)
    await update.message.reply_text(msg)


# Main async function to start the bot
async def start():
    logger.info("🤖 Bot yana farawa...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("price", price_command))

    # Initialize the application
    await app.initialize()
    logger.info("✅ Bot yana gudana.")

    # Start polling for updates. This function blocks until the bot is stopped.
    await app.run_polling()


# Entry point of the script
if __name__ == "__main__":
    try:
        # Use asyncio.run() for simpler execution and proper loop management
        asyncio.run(start())
    except KeyboardInterrupt:
        logger.info("Bot is shutting down due to user interrupt.")
    except Exception as e:
        logger.error(f"An error occurred in the main event loop: {e}")

