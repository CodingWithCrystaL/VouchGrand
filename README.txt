
# GrandX Discord Vouch Bot

This bot allows users to give vouches (feedback) for services/products with a rating system.

## Features
- /vouch command
- Dropdown for product selection
- Dropdown for rating (e.g. ✅ Legit, ⭐⭐⭐⭐)
- Vouches are logged with thumbnails, footers, and database storage

## Setup

1. Install requirements:
```
pip install discord.py aiosqlite flask
```

2. In `main_final_clean.py`, replace the following values at the top:
```
TOKEN = "YOUR_DISCORD_BOT_TOKEN"
LOG_CHANNEL_ID = 123456789012345678
GUILD_ID = 123456789012345678
```

3. Run your bot:
```
python main_final_clean.py
```

## Optional
- You may use uptime pingers for hosting platforms like Replit or Railway using the keep_alive route.
