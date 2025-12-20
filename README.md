# Divar Search Telegram Bot 🤖

A Telegram bot that searches divar.ir (Iranian classifieds website) for user-specified terms and returns results in an Excel file.

## Features

- 🔍 Search divar.ir for any term
- 📊 Generate Excel files with search results
- 📞 Extract phone numbers from advertisements
- 🚀 Easy to use - just send a search term
- 💾 Automatic cleanup of old files

## Excel File Contents

The generated Excel file includes:
- **Title**: Advertisement title
- **Description**: Advertisement description
- **Price**: Price information
- **Phone Number**: Contact phone number (when available)
- **URL**: Direct link to the advertisement

## Prerequisites

### For Local Development
- Python 3.8 or higher
- A Telegram bot token (get one from [@BotFather](https://t.me/botfather))

### For Docker Deployment
- Docker and Docker Compose installed
- A Telegram bot token (get one from [@BotFather](https://t.me/botfather))

## Installation

### Method 1: Local Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a Telegram Bot Token:**
   - Go to [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` and follow the instructions
   - Copy the bot token

4. **Configure the bot:**
   - Open `config.py`
   - Replace `'YOUR_BOT_TOKEN'` with your actual bot token

### Method 2: Docker Installation

1. **Clone or download this repository**

2. **Get a Telegram Bot Token:**
   - Go to [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` and follow the instructions
   - Copy the bot token

3. **Create environment file:**
   ```bash
   python setup_env.py
   ```
   Or manually:
   ```bash
   cp env.example .env
   ```

4. **Configure the bot:**
   - Open `.env` file
   - Set your `BOT_TOKEN`

## Usage

### Running Locally

### Running the Bot

```bash
python bot.py
```

### Running with Docker

1. **Start the bot:**
   ```bash
   docker-compose up -d
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f divar-bot
   ```

3. **Stop the bot:**
   ```bash
   docker-compose down
   ```

4. **Rebuild after code changes:**
   ```bash
   docker-compose up -d --build
   ```

### Using the Bot

1. **Start the bot:** Send `/start` to get welcome message
2. **Search:** Simply type any search term (e.g., "iPhone", "car", "apartment")
3. **Receive results:** The bot will send you an Excel file with search results

### Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help information
- Any text message - Search term for divar.ir

### Examples

- "iPhone 13"
- "Toyota Corolla"
- "آپارتمان تهران" (Persian text works too)

## Configuration

### Local Configuration

Edit `config.py` to customize:

- `BOT_TOKEN`: Your Telegram bot token
- `MAX_RESULTS`: Maximum number of results to scrape (default: 50)
- `REQUEST_TIMEOUT`: Request timeout in seconds (default: 10)
- `EXCEL_FILENAME_TEMPLATE`: Template for Excel filenames

### Docker Configuration

For Docker deployment, use environment variables:

1. **Create `.env` file:**
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` file:**
   ```env
   BOT_TOKEN=your_actual_bot_token_here
   MAX_RESULTS=50
   REQUEST_TIMEOUT=10
   TZ=UTC
   LOG_LEVEL=INFO
   CHROME_HEADLESS=true
   ```

3. **Environment Variables:**
   - `BOT_TOKEN`: Your Telegram bot token (required - no default)
   - `MAX_RESULTS`: Maximum results to scrape (default: 50)
   - `REQUEST_TIMEOUT`: Request timeout in seconds (default: 10)
   - `TZ`: Timezone (default: UTC)
   - `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR) (default: INFO)
   - `LOG_FILE`: Log file path (default: /app/logs/bot.log)
   - `CHROME_HEADLESS`: Run Chrome in headless mode (default: true)
   - `CHROME_OPTIONS`: Additional Chrome options (comma-separated, default: --no-sandbox,--disable-dev-shm-usage,--disable-gpu)

### Docker Volumes

The Docker setup creates persistent volumes for:
- `excel_files/`: Generated Excel files
- `logs/`: Application logs

## How It Works

1. **User sends search term** → Bot receives the message
2. **Web scraping** → Bot searches divar.ir using the search term
3. **Data extraction** → Extracts title, description, price, and phone numbers
4. **Excel generation** → Creates formatted Excel file with results
5. **File delivery** → Sends Excel file to user via Telegram

## Troubleshooting

### Common Issues

1. **"No results found"**
   - Try different keywords
   - Check spelling
   - Use shorter search terms

2. **Bot not responding**
   - Check if bot token is correct in `config.py`
   - Ensure internet connection
   - Check console for error messages

3. **Phone numbers not showing**
   - Some advertisements don't display phone numbers publicly
   - Phone numbers are extracted from advertisement details when available

### Error Messages

- **Token Error**: Make sure you've set a valid bot token in `config.py`
- **Scraping Error**: divar.ir may have changed their website structure
- **Network Error**: Check your internet connection

### Docker Troubleshooting

1. **Chrome/Selenium issues:**
   ```bash
   docker-compose logs divar-bot
   ```
   Check for ChromeDriver version compatibility

2. **Permission issues:**
   ```bash
   sudo chown -R $USER:$USER excel_files/
   sudo chown -R $USER:$USER logs/
   ```

3. **Rebuild container:**
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

4. **Check container health:**
   ```bash
   docker ps
   docker-compose ps
   ```

## Legal Notice

⚠️ **Important**: This bot is for educational purposes only. Make sure to:
- Respect divar.ir's terms of service
- Use the bot responsibly
- Don't overload their servers with too many requests

## Development

### Project Structure

```
divar_searcher/
├── bot.py              # Main Telegram bot logic
├── scraper.py          # Web scraping functionality
├── excel_generator.py  # Excel file creation
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker container configuration
├── docker-compose.yml  # Docker Compose orchestration
├── env.example         # Environment variables template
├── setup_env.py        # Environment setup script
├── .dockerignore       # Docker ignore file
└── README.md           # This file
```

### Dependencies

- `python-telegram-bot`: Telegram bot framework
- `requests`: HTTP requests for web scraping
- `beautifulsoup4`: HTML parsing
- `openpyxl`: Excel file creation
- `selenium`: Browser automation (fallback scraping)
- `webdriver-manager`: Automatic webdriver management

### Adding New Features

1. **Modify scraper.py** for different websites or data extraction
2. **Update excel_generator.py** to change Excel formatting
3. **Edit bot.py** to add new commands or features

## Support

If you encounter issues:

1. Check the console output for error messages
2. Verify your bot token is correct
3. Ensure all dependencies are installed
4. Try running with different search terms

## License

This project is open source. Use at your own risk.

---

Made with ❤️ for educational purposes
