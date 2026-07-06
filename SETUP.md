# Watch Stock Monitor - Setup Guide

Monitors Delhi Watch Company, Kala Watches, and Coromandel Watch Co for stock changes.
Sends Telegram notifications when watches come in stock.

## Step 1: Create a Telegram Bot (2 minutes)

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Choose a name (e.g., "Watch Stock Alert")
4. Choose a username (e.g., "my_watch_stock_bot") — must end in `bot`
5. BotFather will give you a **token** like `7123456789:AAHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
6. Save that token for Step 3

## Step 2: Get Your Chat ID

1. Open your new bot in Telegram and send it any message (e.g., "hello")
2. Open this URL in your browser (replace TOKEN with your bot token):
   `https://api.telegram.org/botTOKEN/getUpdates`
3. Look for `"chat":{"id":XXXXXXXX}` — that number is your **Chat ID**
4. Save it for Step 3

## Step 3: Create GitHub Repository

```bash
cd ~/watch-stock-monitor
git init
git add .
git commit -m "Initial commit: watch stock monitor"
```

Then on GitHub.com:
1. Create a new private repository called `watch-stock-monitor`
2. Follow the instructions to push an existing repo:
```bash
git remote add origin https://github.com/YOUR_USERNAME/watch-stock-monitor.git
git branch -M main
git push -u origin main
```

## Step 4: Add Secrets on GitHub

Go to your repo → Settings → Secrets and variables → Actions → New repository secret

Add these two secrets:
- Name: `TELEGRAM_BOT_TOKEN` → Value: your bot token from Step 1
- Name: `TELEGRAM_CHAT_ID` → Value: your chat ID from Step 2

## Step 5: Enable GitHub Actions

The workflow runs automatically every 10 minutes after push. To trigger manually:
Go to your repo → Actions → "Watch Stock Monitor" → Run workflow

## How It Works

- Uses Shopify's JSON API (all 3 stores are Shopify-based) to check product availability
- Tracks state between runs using GitHub Actions cache
- Only notifies on NEW items coming in stock (not repeated alerts)
- Filters out accessories (straps, bracelets, t-shirts) to focus on watches

## Testing Locally

```bash
pip install -r requirements.txt
set TELEGRAM_BOT_TOKEN=your_token_here
set TELEGRAM_CHAT_ID=your_chat_id_here
python monitor.py
```

## Cost

- **Free** — GitHub Actions free tier gives 2,000 minutes/month
- At ~10 seconds per run, 6 runs/hour = ~44 minutes/month total usage
- Telegram Bot API is free with no limits for personal use

## Adjusting Frequency

Edit `.github/workflows/monitor.yml` cron schedule:
- Every 5 min: `*/5 * * * *`
- Every 10 min: `*/10 * * * *` (default)
- Every 30 min: `*/30 * * * *`

Note: GitHub Actions cron has ~1-5 min delay, so actual interval may vary slightly.
