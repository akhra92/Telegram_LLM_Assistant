import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from llm import ask_llm
from products import load_products

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    bot_info = await context.bot.get_me()
    bot_username = f"@{bot_info.username}"

    is_group = message.chat.type in ("group", "supergroup")
    is_mentioned = bot_username.lower() in message.text.lower()

    # In groups, only respond when mentioned
    if is_group and not is_mentioned:
        return

    # Strip the bot mention from the question
    user_text = message.text.replace(bot_username, "").strip()
    if not user_text:
        await message.reply_text(
            "Hi! Ask me anything about our products — prices, availability, descriptions, and more."
        )
        return

    logger.info(
        "Question from %s in chat %s: %s",
        message.from_user.username or message.from_user.id,
        message.chat.id,
        user_text,
    )

    # Show typing indicator while LLM is responding
    await context.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        products = load_products()
        response = ask_llm(user_text, products)
    except Exception as e:
        logger.error("Error generating response: %s", e)
        response = "Sorry, I'm having trouble answering right now. Please try again later."

    await message.reply_text(response)


def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN not set in .env")

    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
