"""Entry point script for running the Telegram bot as a standalone process."""

import asyncio
import logging
import sys

from app.bot.telegram_bot import create_bot_application
from app.config import get_settings

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Run the Telegram bot."""
    settings = get_settings()

    if not settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
        sys.exit(1)

    logger.info(f"Starting FilterBets Telegram bot (@{settings.telegram_bot_username})...")

    # Create and start the bot application
    application = create_bot_application()

    # Start the bot using long polling
    await application.initialize()
    await application.start()

    if application.updater:
        await application.updater.start_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True,
        )

    logger.info("Bot is running. Press Ctrl+C to stop.")

    # Keep the bot running
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping bot...")
    finally:
        if application.updater:
            await application.updater.stop()
        await application.stop()
        await application.shutdown()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
