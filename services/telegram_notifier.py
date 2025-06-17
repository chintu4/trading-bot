import asyncio
from telegram import Bot
from telegram.error import TelegramError
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID # Reads from .env
from utils.logger import logger

async def _send_message_async(bot_token: str, chat_id: str, message: str) -> bool:
    """Asynchronously sends a message using python-telegram-bot."""
    if not bot_token:
        logger.error("Telegram bot token is not configured. Cannot send notification.")
        return False
    if not chat_id:
        logger.error("Telegram chat ID is not configured. Cannot send notification.")
        return False

    bot = Bot(token=bot_token)
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown') # Added Markdown
        logger.info(f"Telegram notification sent successfully to chat ID {chat_id}.")
        return True
    except TelegramError as e:
        logger.error(f"Failed to send Telegram notification to chat ID {chat_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while sending Telegram notification: {e}", exc_info=True)
        return False

def send_trade_notification(message: str) -> bool:
    """
    Sends a trade notification message to the configured Telegram chat.
    This is a synchronous wrapper around the async sending function.
    """
    # These are loaded from .env when config.settings is imported
    token = TELEGRAM_BOT_TOKEN
    chat_id = TELEGRAM_CHAT_ID

    # For applications not already running an asyncio event loop,
    # asyncio.run() is a straightforward way to run an async function.
    try:
        return asyncio.run(_send_message_async(token, chat_id, message))
    except RuntimeError as e:
        # This can happen if asyncio.run() is called from an already running event loop.
        # For simplicity in this service, we'll log and fail.
        # A more complex app might need to handle loop management differently.
        logger.error(f"RuntimeError during asyncio.run for Telegram: {e}. This might happen if called from within an existing asyncio event loop.")
        return False


if __name__ == '__main__':
    # Example Usage:
    # Ensure your .env file has TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID set.
    logger.info("Attempting to send a test Telegram notification...")

    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        test_message = "Hello from the Trading Bot! This is a *test notification* from `telegram_notifier.py`."
        success = send_trade_notification(test_message)
        if success:
            logger.info("Test notification function executed. Check your Telegram for the message.")
        else:
            logger.error("Test notification function executed, but sending failed. Check logs above.")
    else:
        logger.warning("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not set in .env. Skipping test notification.")

    # Example of a failed scenario (e.g., invalid token to see error handling)
    # logger.info("Attempting to send a test notification with a bad token...")
    # bad_token_success = asyncio.run(_send_message_async("bad_token", TELEGRAM_CHAT_ID, "This should fail."))
    # logger.info(f"Bad token test send status: {bad_token_success}")
