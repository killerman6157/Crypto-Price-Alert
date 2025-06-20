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
    exit(1)

# Get price from CoinGecko
async def get_crypto_price(coin: str) -> str:
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    try:
        # Use asyncio.to_thread for blocking I/O (requests.get)
        # This prevents blocking the event loop
        res = await asyncio.to_thread(requests.get, url, timeout=10) # Added timeout
        res.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = res.json()

        if coin in data and "usd" in data[coin]:
            price = data[coin]["usd"]
            return f"💰 Current price of {coin.upper()}: ${price}"
        else:
            # More specific error for when coin data is missing
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
    # Inform the user that the request is being processed
    await update.message.reply_text(f"Neman farashin {coin}...")
    msg = await get_crypto_price(coin) # Await the async function
    await update.message.reply_text(msg)


# Main function to run the bot
def main():
    logger.info("🤖 Bot yana farawa...")

    # Build the Application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("price", price_command))

    logger.info("✅ Bot yana gudana.")

    # Run the bot
    # This will initialize, start, run polling, and handle shutdown internally.
    application.run_polling(drop_pending_updates=True)


# Entry point of the script
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot is shutting down due to user interrupt.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

