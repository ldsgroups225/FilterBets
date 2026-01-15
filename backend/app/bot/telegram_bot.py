"""Telegram bot implementation for FilterBets."""

import logging
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config import get_settings
from app.models.filter import Filter
from app.models.user import User
from app.services.telegram_service import TelegramService

logger = logging.getLogger(__name__)
settings = get_settings()


# Create async database session factory for bot
async_engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """Get database session for bot handlers."""
    session = AsyncSessionLocal()
    return session  # type: ignore[return-value]  # noqa: PGH003


async def start_with_token(
    update: Update, _context: ContextTypes.DEFAULT_TYPE, token: str
) -> None:
    """Handle /start command with token for account linking.

    Args:
        update: Telegram update object
        _context: Bot context (unused but required by framework)
        token: Link token from deep link
    """
    if not update.effective_chat:
        return

    chat_id = str(update.effective_chat.id)
    username = update.effective_user.username if update.effective_user else None

    db = await get_db()
    telegram_service = TelegramService(db)

    try:
        user = await telegram_service.link_telegram_account(token, chat_id, username)

        if user and update.message:
            await update.message.reply_text(
                f"✅ *Account Linked Successfully!*\n\n"
                f"Your Telegram account is now linked to FilterBets.\n"
                f"Email: {user.email[:3]}***@{user.email.split('@')[1]}\n\n"
                f"You can now enable alerts on your filters to receive notifications here.\n\n"
                f"Use /help to see available commands.",
                parse_mode="Markdown",
            )
            logger.info(f"Successfully linked Telegram account for user {user.id}")
        elif update.message:
            await update.message.reply_text(
                "❌ *Link Failed*\n\n"
                "The link code is invalid or has expired.\n"
                "Please generate a new link from the FilterBets app settings.",
                parse_mode="Markdown",
            )
            logger.warning(f"Failed to link Telegram account with token: {token}")
    finally:
        await telegram_service.close()
        await db.close()


async def start_without_token(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command without token - show welcome message.

    Args:
        update: Telegram update object
        context: Bot context
    """
    if not update.message:
        return

    await update.message.reply_text(
        "👋 *Welcome to FilterBets!*\n\n"
        "I'm your betting analytics assistant. To get started:\n\n"
        "1️⃣ Create an account at filterbets.com\n"
        "2️⃣ Go to Settings and click 'Link Telegram'\n"
        "3️⃣ You'll be redirected here with your account linked\n\n"
        "Once linked, you'll receive notifications when matches meet your filter criteria.\n\n"
        "Use /help to see all available commands.",
        parse_mode="Markdown",
    )


async def start_command(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - with or without token.

    Args:
        update: Telegram update object
        _context: Bot context
    """
    if not update.message:
        return

    # Check if there's a token in the command args
    if _context.args and len(_context.args) > 0:
        token = _context.args[0]
        await start_with_token(update, _context, token)
    else:
        await start_without_token(update, _context)


async def status_command(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command - show linked account info.

    Args:
        update: Telegram update object
        context: Bot context
    """
    if not update.effective_chat or not update.message:
        return

    chat_id = str(update.effective_chat.id)
    db = await get_db()

    try:
        # Find user by telegram_chat_id
        result = await db.execute(
            select(User).where(User.telegram_chat_id == chat_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await update.message.reply_text(
                "❌ *Not Linked*\n\n"
                "Your Telegram account is not linked to FilterBets.\n"
                "Use /start to see how to link your account.",
                parse_mode="Markdown",
            )
            return

        # Count active filters with alerts enabled
        filter_count_result = await db.execute(
            select(func.count(Filter.id))
            .where(Filter.user_id == user.id)
            .where(Filter.is_active == True)  # noqa: E712
            .where(Filter.alerts_enabled == True)  # noqa: E712
        )
        active_filter_count = filter_count_result.scalar() or 0

        # Mask email for privacy
        email_parts = user.email.split("@")
        masked_email = f"{email_parts[0][:3]}***@{email_parts[1]}"

        await update.message.reply_text(
            f"✅ *Account Status*\n\n"
            f"📧 Email: {masked_email}\n"
            f"🔔 Active Filters: {active_filter_count}\n"
            f"📊 Scan Frequency: {user.scan_frequency.value}\n\n"
            f"Use /filters to see your active filters.",
            parse_mode="Markdown",
        )
    finally:
        await db.close()


async def filters_command(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /filters command - list user's active filters.

    Args:
        update: Telegram update object
        context: Bot context
    """
    if not update.effective_chat or not update.message:
        return

    chat_id = str(update.effective_chat.id)
    db = await get_db()

    try:
        # Find user by telegram_chat_id
        result = await db.execute(
            select(User).where(User.telegram_chat_id == chat_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await update.message.reply_text(
                "❌ Your Telegram account is not linked. Use /start to link.",
                parse_mode="Markdown",
            )
            return

        # Get user's filters
        filters_result = await db.execute(
            select(Filter)
            .where(Filter.user_id == user.id)
            .where(Filter.is_active == True)  # noqa: E712
            .order_by(Filter.created_at.desc())
        )
        filters = list(filters_result.scalars().all())

        if not filters:
            await update.message.reply_text(
                "📭 *No Active Filters*\n\n"
                "You don't have any active filters yet.\n"
                "Create filters at filterbets.com to start receiving alerts!",
                parse_mode="Markdown",
            )
            return

        # Build filter list message
        message_lines = ["🎯 *Your Active Filters*\n"]

        for i, filter_obj in enumerate(filters, 1):
            alert_status = "🔔 ON" if filter_obj.alerts_enabled else "🔕 OFF"
            message_lines.append(
                f"{i}. *{filter_obj.name}*\n"
                f"   Alerts: {alert_status}\n"
            )

        message_lines.append(
            "\n💡 Enable/disable alerts from the FilterBets app."
        )

        await update.message.reply_text(
            "\n".join(message_lines),
            parse_mode="Markdown",
        )
    finally:
        await db.close()


async def unlink_command(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /unlink command - unlink Telegram account.

    Args:
        update: Telegram update object
        context: Bot context
    """
    if not update.effective_chat or not update.message:
        return

    chat_id = str(update.effective_chat.id)
    db = await get_db()
    telegram_service = TelegramService(db)

    try:
        # Find user by telegram_chat_id
        result = await db.execute(
            select(User).where(User.telegram_chat_id == chat_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await update.message.reply_text(
                "❌ Your Telegram account is not linked.",
                parse_mode="Markdown",
            )
            return

        # Unlink account
        success = await telegram_service.unlink_telegram_account(user.id)

        if success:
            await update.message.reply_text(
                "✅ *Account Unlinked*\n\n"
                "Your Telegram account has been unlinked from FilterBets.\n"
                "You will no longer receive notifications.\n\n"
                "You can link again anytime from the FilterBets app settings.",
                parse_mode="Markdown",
            )
            logger.info(f"Unlinked Telegram account for user {user.id}")
        else:
            await update.message.reply_text(
                "❌ Failed to unlink account. Please try again later.",
                parse_mode="Markdown",
            )
    finally:
        await telegram_service.close()
        await db.close()


async def help_command(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command - show available commands.

    Args:
        update: Telegram update object
        context: Bot context
    """
    if not update.message:
        return

    await update.message.reply_text(
        "🤖 *FilterBets Bot Commands*\n\n"
        "/start - Link your Telegram account\n"
        "/status - Check your account status\n"
        "/filters - List your active filters\n"
        "/unlink - Unlink your Telegram account\n"
        "/help - Show this help message\n\n"
        "📱 Manage your filters and settings at filterbets.com",
        parse_mode="Markdown",
    )


def create_bot_application() -> Application[Any, Any, Any, Any, Any, Any]:
    """Create and configure the Telegram bot application.

    Returns:
        Configured Application instance
    """
    if not settings.telegram_bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

    # Create application
    application = Application.builder().token(settings.telegram_bot_token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("filters", filters_command))
    application.add_handler(CommandHandler("unlink", unlink_command))
    application.add_handler(CommandHandler("help", help_command))

    logger.info("Telegram bot application created successfully")
    return application
