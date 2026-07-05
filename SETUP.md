# Watch Stock Monitor - Setup Guide

Monitors Delhi Watch Company, Kala Watches, and Coromandel Watch Co for stock changes.
Sends WhatsApp notifications to +91 8016564766 when watches come in stock.

## Step 1: Set up CallMeBot WhatsApp API (free, 2 minutes)

1. Save the phone number `+34 644 31 89 43` in your phone contacts (name it "CallMeBot")
2. Send this WhatsApp message to that number: `I allow callmebot to send me messages`
3. Wait for a reply — you'll receive your **API key** (a number like `123456`)
4. Save that API key for Step 3

## Step 2: Create GitHub Repository

```bash
cd watch-stock-monitor
git init
git add .
git commit -m "Initial commit: watch stock monitor"
```

Then create a repo on GitHub:
```bash
gh repo create watch-stock-monitor --private --source=. --push
```

## Step 3: Add the API Key as a GitHub Secret

```bash
gh secret set CALLMEBOT_API_KEY --body "YOUR_API_KEY_HERE"
```

Replace `YOUR_API_KEY_HERE` with the key from Step 1.

## Step 4: Enable GitHub Actions

The workflow runs automatically every 10 minutes. To trigger manually:
```bash
gh workflow run monitor.yml
```

## How It Works

- Uses Shopify's JSON API (all 3 stores are Shopify-based) to check product availability
- Tracks state between runs using GitHub Actions cache
- Only notifies on NEW items coming in stock (not repeated alerts)
- Filters out accessories (straps, bracelets, t-shirts) to focus on watches

## Testing Locally

```bash
pip install -r requirements.txt
export CALLMEBOT_API_KEY=your_key_here
python monitor.py
```

## Cost

- **Free** — GitHub Actions free tier gives 2,000 minutes/month
- At ~10 seconds per run, 6 runs/hour = ~44 minutes/month total usage
- CallMeBot WhatsApp API is free

## Adjusting Frequency

Edit `.github/workflows/monitor.yml` cron schedule:
- Every 5 min: `*/5 * * * *`
- Every 10 min: `*/10 * * * *` (default)
- Every 30 min: `*/30 * * * *`

Note: GitHub Actions cron has ~1-5 min delay, so actual interval may vary slightly.
