import logging
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import config
from scraper import DivarScraper
from excel_generator import ExcelGenerator
import os

# Enable logging with configuration
log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=log_level,
    filename=config.LOG_FILE if config.LOG_FILE != '/app/logs/bot.log' or os.path.exists('/app/logs') else None
)
logger = logging.getLogger(__name__)

class DivarSearchBot:
    def __init__(self):
        self.scraper = DivarScraper()
        self.excel_generator = ExcelGenerator()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        welcome_message = """
🤖 *Divar Search Bot*

Send me a search term and I'll search divar.ir and create an Excel file with the results!

*How to use:*
1. Just type any search term (e.g., "iPhone", "car", "apartment")
2. I'll search divar.ir for advertisements matching your term
3. I'll create an Excel file with names, descriptions, and phone numbers
4. You'll receive the Excel file with all the results

*Note:* Phone numbers are extracted when available from the advertisement details.

Send me a search term to get started!
        """

        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        help_text = """
*Divar Search Bot Help*

*Commands:*
/start - Start the bot and see welcome message
/help - Show this help message

*Usage:*
Simply send any text as your search term, and I'll search divar.ir for matching advertisements.

*Example:*
- "iPhone 13"
- "Toyota Corolla"
- "آپارتمان تهران" (Persian text also works)

The bot will send you an Excel file (.xlsx) containing:
- Advertisement titles
- Descriptions
- Prices
- Phone numbers (when available)
- Direct links to advertisements
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages (search terms)."""
        search_term = update.message.text.strip()

        if not search_term:
            await update.message.reply_text("Please send a valid search term!")
            return

        # Send searching message
        searching_message = await update.message.reply_text(
            f"🔍 Searching divar.ir for: *{search_term}*\n\nPlease wait...",
            parse_mode='Markdown'
        )

        try:
            # Perform search
            logger.info(f"Searching for: {search_term}")
            results = self.scraper.search_divar(search_term)

            if not results:
                await searching_message.edit_text(
                    f"❌ No results found for: *{search_term}*\n\n"
                    "Try different keywords or check your spelling.",
                    parse_mode='Markdown'
                )
                return

            # Generate Excel file
            logger.info(f"Found {len(results)} results, creating Excel file")
            await searching_message.edit_text(
                f"📊 Found {len(results)} results!\n\n"
                "Creating Excel file..."
            )

            excel_file = self.excel_generator.create_excel(search_term, results)

            # Send Excel file
            await update.message.reply_document(
                document=open(excel_file, 'rb'),
                filename=os.path.basename(excel_file),
                caption=f"📄 Excel file with {len(results)} search results for: {search_term}"
            )

            # Clean up the file after sending
            os.remove(excel_file)

            # Update the searching message
            await searching_message.edit_text(
                f"✅ Search completed!\n\n"
                f"Found {len(results)} results for: *{search_term}*\n"
                "Excel file has been sent above.",
                parse_mode='Markdown'
            )

            logger.info(f"Successfully sent Excel file for search: {search_term}")

        except Exception as e:
            logger.error(f"Error processing search '{search_term}': {str(e)}")
            await searching_message.edit_text(
                f"❌ Sorry, an error occurred while searching for: *{search_term}*\n\n"
                f"Error: {str(e)}\n\n"
                "Please try again later or contact the administrator.",
                parse_mode='Markdown'
            )

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log the error and send a telegram message to notify the developer."""
        logger.error(msg="Exception while handling an update:", exc_info=context.error)

        # Send error message to user if possible
        try:
            if update and hasattr(update, 'message'):
                await update.message.reply_text(
                    "❌ An unexpected error occurred. Please try again later."
                )
        except:
            pass

def main() -> None:
    """Start the bot."""
    # Check if bot token is configured
    if config.BOT_TOKEN == 'YOUR_BOT_TOKEN':
        print("ERROR: Please set your bot token in config.py")
        print("Get a token from @BotFather on Telegram")
        return

    # Create the Application and pass it your bot's token
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Create bot instance
    bot_instance = DivarSearchBot()

    # Add handlers
    application.add_handler(CommandHandler("start", bot_instance.start))
    application.add_handler(CommandHandler("help", bot_instance.help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_instance.handle_message))

    # Add error handler
    application.add_error_handler(bot_instance.error_handler)

    # Start the Bot
    print("Bot is starting... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
