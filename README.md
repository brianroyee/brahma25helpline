# Brahma'25 Telegram Bot

## About the Project
Brahma'25 Helpline Bot is a Telegram bot designed to assist users with event details, schedules, results, and contact information for the Brahma'25 festival. The bot provides an interactive menu-based interface using inline buttons.

## Features
- 📅 View Event Details (General, Cultural, and Technical)
- 🕗 Check Event Timeline
- 👥 Contact Organizing Team
- 🏆 View Event Results
- 📊 Track Bot Statistics (Admin Feature)
- 📢 Admin Notifications & Broadcasts
- ⚠️ Report Issues

## Technologies Used
- **Python**
- **Telegram Bot API** (using `python-telegram-bot`)
- **Flask** (for keeping the bot alive)
- **dotenv** (for managing environment variables)

## Project Structure
```
├── main.py             # Main bot script
├── keep_alive.py       # Flask server to keep the bot running
├── requirements.txt    # Python dependencies
├── data/               # Stores event details and bot statistics
│   ├── general.json
│   ├── cultural.json
│   ├── technical.json
│   ├── results.json
│   ├── bot_stats.json
```

## Installation & Setup

### 1️ Prerequisites
- Python 3.7+
- Telegram Bot Token (from BotFather)

### 2️ Clone the repository
```bash
git clone https://github.com/your-repo/brahma25-telegram-bot.git
cd brahma25-telegram-bot
```

### 3️ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️ Setup Environment Variables
Create a `.env` file and add:
```
TOKEN=your_telegram_bot_token
ADMINS=12345678,98765432  # Admin Telegram IDs (comma-separated)
```

### 5️ Run the Bot
```bash
python main.py
```

## 📡 Deployment
To keep the bot running continuously, you can:
- Deploy on **Render**
- Keep Flask server alive (`keep_alive.py` helps with this)

## 🤝 Developers & Contributors

### Dev Team
- **Brian Roy Mathew** - Lead Developer
- **Sreeramachandran S Menon** - DevOps & Deployment

### Contributors
- **Ashwin P Shine**
- **Chandra Rajesh**
- **Deepak M.R.**
- **Anandhakrishnan**
- **Ceeya Sarah Varghese** 

## License
This project is licensed under the MIT License.

