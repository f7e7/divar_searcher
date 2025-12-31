import logging
import asyncio
from telegram import Update, Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
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

# Iranian cities for Divar search
IRANIAN_CITIES = {
    'tehran': 'تهران',
    'mashhad': 'مشهد',
    'isfahan': 'اصفهان',
    'karaj': 'کرج',
    'shiraz': 'شیراز',
    'tabriz': 'تبریز',
    'ahvaz': 'اهواز',
    'qom': 'قم',
    'rasht': 'رشت',
    'zahedan': 'زاهدان',
    'hamedan': 'همدان',
    'kermanshah': 'کرمانشاه',
    'yazd': 'یزد',
    'ardabil': 'اردبیل',
    'bandarabbas': 'بندرعباس',
    'arak': 'اراک',
    'sari': 'ساری',
    'kerman': 'کرمان',
    'birjand': 'بیرجند',
    'ilam': 'ایلام'
}

class DivarSearchBot:
    def __init__(self):
        self.scraper = DivarScraper()
        self.excel_generator = ExcelGenerator()
        self.user_cities = {}  # Store selected city for each user

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user_id = update.effective_user.id

        # Create inline keyboard for city selection
        keyboard = []
        row = []
        for i, (city_code, city_name) in enumerate(IRANIAN_CITIES.items()):
            row.append(InlineKeyboardButton(city_name, callback_data=f"city_{city_code}"))
            if (i + 1) % 3 == 0:  # 3 buttons per row
                keyboard.append(row)
                row = []
        if row:  # Add remaining buttons
            keyboard.append(row)

        reply_markup = InlineKeyboardMarkup(keyboard)

        welcome_message = """
🤖 *Divar Search Bot*

ابتدا شهری که می‌خواهید در آن جستجو کنید را انتخاب کنید:

*How to use:*
1. روی نام شهر کلیک کنید
2. سپس عبارت جستجو را تایپ کنید (مثال: "سمند"، "آیفون"، "اپارتمان")
3. ربات در دیوار جستجو کرده و فایل اکسل نتایج را برایتان ارسال می‌کند

*نکته:* شماره تلفن‌ها در صورت موجود بودن استخراج می‌شوند.
        """

        await update.message.reply_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)

    async def handle_city_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle city selection from inline keyboard."""
        query = update.callback_query
        await query.answer()

        user_id = update.effective_user.id
        callback_data = query.data

        if callback_data.startswith("city_"):
            city_code = callback_data.replace("city_", "")
            city_name = IRANIAN_CITIES.get(city_code, "نامشخص")

            # Store selected city
            self.user_cities[user_id] = city_code

            await query.edit_message_text(
                f"✅ شهر *{city_name}* انتخاب شد!\n\n"
                "حالا عبارت جستجوی خود را تایپ کنید:\n"
                "مثال: `سمند سورن پلاس` یا `آیفون ۱۳` یا `اپارتمان ۳ خوابه`",
                parse_mode='Markdown'
            )

        elif callback_data == "search_selected_city":
            await self._perform_search(update, context, search_type="selected_city")

        elif callback_data == "search_all_cities":
            await self._perform_search(update, context, search_type="all_cities")

        elif callback_data == "change_city":
            # Show city selection keyboard again
            keyboard = []
            row = []
            for i, (city_code, city_name) in enumerate(IRANIAN_CITIES.items()):
                row.append(InlineKeyboardButton(city_name, callback_data=f"city_{city_code}"))
                if (i + 1) % 3 == 0:  # 3 buttons per row
                    keyboard.append(row)
                    row = []
            if row:  # Add remaining buttons
                keyboard.append(row)

            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "🏙️ شهر مورد نظر خود را انتخاب کنید:",
                reply_markup=reply_markup
            )

        elif callback_data == "cancel_search":
            # Clear search data
            if 'search_term' in context.user_data:
                del context.user_data['search_term']

            await query.edit_message_text(
                "❌ جستجو لغو شد.\n\n"
                "برای شروع مجدد، دستور /start را ارسال کنید.",
                parse_mode='Markdown'
            )

    async def _perform_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE, search_type: str) -> None:
        """Perform the actual search based on type."""
        query = update.callback_query
        user_id = update.effective_user.id

        # Get search term from context
        search_term = context.user_data.get('search_term')
        if not search_term:
            await query.edit_message_text("❌ عبارت جستجو یافت نشد. دوباره امتحان کنید.")
            return

        try:
            if search_type == "selected_city":
                city_code = self.user_cities.get(user_id)
                if not city_code:
                    await query.edit_message_text("❌ شهر انتخاب شده یافت نشد.")
                    return

                city_name = IRANIAN_CITIES.get(city_code, "نامشخص")

                # Update message
                await query.edit_message_text(
                    f"🔍 جستجو در *{city_name}* برای: *{search_term}*\n\n⏳ در حال جستجو...",
                    parse_mode='Markdown'
                )

                # Perform search
                results = self.scraper.search_divar(search_term, city=city_code)

            elif search_type == "all_cities":
                # Update message
                await query.edit_message_text(
                    f"🌍 جستجو در *همه شهرها* برای: *{search_term}*\n\n⏳ در حال جستجو...",
                    parse_mode='Markdown'
                )

                # Search in multiple cities (let's do top 5 cities for performance)
                top_cities = ['tehran', 'mashhad', 'isfahan', 'karaj', 'shiraz']
                all_results = []

                for city_code in top_cities:
                    try:
                        city_results = self.scraper.search_divar(search_term, city=city_code, max_results=10)
                        all_results.extend(city_results)
                    except Exception as e:
                        print(f"Error searching in {city_code}: {e}")
                        continue

                results = all_results[:50]  # Limit to 50 total results

            # Clear search term from context
            if 'search_term' in context.user_data:
                del context.user_data['search_term']

            # Process results
            if not results:
                await query.edit_message_text(
                    f"❌ نتیجه‌ای برای *{search_term}* یافت نشد.",
                    parse_mode='Markdown'
                )
                return

            # Update message
            await query.edit_message_text(
                f"📊 {len(results)} نتیجه یافت شد!\n\n⏳ در حال ایجاد فایل اکسل...",
                parse_mode='Markdown'
            )

            # Generate Excel file
            excel_file = self.excel_generator.create_excel(search_term, results)

            # Send Excel file
            await update.callback_query.message.reply_document(
                document=open(excel_file, 'rb'),
                filename=os.path.basename(excel_file),
                caption=f"📄 فایل اکسل با {len(results)} نتیجه جستجو برای: {search_term}"
            )

            # Clean up
            os.remove(excel_file)

            # Final message
            await update.callback_query.message.reply_text(
                f"✅ جستجو تکمیل شد!\n\n{len(results)} نتیجه در فایل اکسل ارسال شد.",
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error in search: {e}")
            await query.edit_message_text(
                f"❌ خطایی در جستجو رخ داد: {str(e)}",
                parse_mode='Markdown'
            )

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
        user_id = update.effective_user.id
        search_term = update.message.text.strip()

        if not search_term:
            await update.message.reply_text("لطفاً یک عبارت جستجو معتبر ارسال کنید!")
            return

        # Check if user has selected a city
        if user_id not in self.user_cities:
            await update.message.reply_text(
                "❌ ابتدا باید شهر مورد نظر خود را انتخاب کنید!\n\n"
                "برای انتخاب شهر، دستور /start را ارسال کنید.",
                parse_mode='Markdown'
            )
            return

        # Store search term in user context
        context.user_data['search_term'] = search_term
        city_code = self.user_cities[user_id]
        city_name = IRANIAN_CITIES.get(city_code, "نامشخص")

        # Show search options keyboard
        keyboard = [
            [InlineKeyboardButton(f"🔍 جستجو در {city_name}", callback_data="search_selected_city")],
            [InlineKeyboardButton("🌍 جستجو در همه شهرها", callback_data="search_all_cities")],
            [InlineKeyboardButton("🔄 تغییر شهر", callback_data="change_city")],
            [InlineKeyboardButton("❌ انصراف", callback_data="cancel_search")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"✅ عبارت جستجو: *{search_term}*\n\n"
            "گزینه مورد نظر خود را انتخاب کنید:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

        # Send searching message
        searching_message = await update.message.reply_text(
            f"🔍 جستجو در دیوار *{city_name}* برای: *{search_term}*\n\nلطفاً صبر کنید...",
            parse_mode='Markdown'
        )

        try:
            # Perform search
            logger.info(f"Searching for: {search_term} in city: {city_code}")
            results = self.scraper.search_divar(search_term, city=city_code)

            if not results:
                await searching_message.edit_text(
                    f"❌ نتیجه‌ای در *{city_name}* برای: *{search_term}* یافت نشد\n\n"
                    "کلمات کلیدی دیگری امتحان کنید یا املا را چک کنید.",
                    parse_mode='Markdown'
                )
                return

            # Generate Excel file
            logger.info(f"Found {len(results)} results, creating Excel file")
            await searching_message.edit_text(
                f"📊 {len(results)} نتیجه یافت شد!\n\n"
                "در حال ایجاد فایل اکسل..."
            )

            excel_file = self.excel_generator.create_excel(search_term, results)

            # Send Excel file
            await update.message.reply_document(
                document=open(excel_file, 'rb'),
                filename=os.path.basename(excel_file),
                caption=f"📄 فایل اکسل با {len(results)} نتیجه جستجو در {city_name} برای: {search_term}"
            )

            # Clean up the file after sending
            os.remove(excel_file)

            # Update the searching message
            await searching_message.edit_text(
                f"✅ جستجو تکمیل شد!\n\n"
                f"{len(results)} نتیجه در *{city_name}* برای: *{search_term}*\n"
                "فایل اکسل در بالا ارسال شد.",
                parse_mode='Markdown'
            )

            logger.info(f"Successfully sent Excel file for search: {search_term}")

        except Exception as e:
            logger.error(f"Error processing search '{search_term}': {str(e)}")
            await searching_message.edit_text(
                f"❌ متاسفانه خطایی در جستجوی *{search_term}* در *{city_name}* رخ داد\n\n"
                f"خطا: {str(e)}\n\n"
                "لطفاً دوباره امتحان کنید یا با مدیر تماس بگیرید.",
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
    if not config.BOT_TOKEN or config.BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("ERROR: Please set your bot token in .env file")
        print("Get a token from @BotFather on Telegram: https://t.me/botfather")
        return

    # Create the Application and pass it your bot's token
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Create bot instance
    bot_instance = DivarSearchBot()

    # Add handlers
    application.add_handler(CommandHandler("start", bot_instance.start))
    application.add_handler(CommandHandler("help", bot_instance.help_command))
    application.add_handler(CallbackQueryHandler(bot_instance.handle_city_selection))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_instance.handle_message))

    # Add error handler
    application.add_error_handler(bot_instance.error_handler)

    # Start the Bot
    print("Bot is starting... Press Ctrl+C to stop.")
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES, timeout=60, poll_interval=2.0, read_timeout=60, write_timeout=60)
    except Exception as e:
        print(f"❌ ERROR starting bot: {e}")
        raise

if __name__ == '__main__':
    main()
