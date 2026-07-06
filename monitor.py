import requests
import json
import os
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

STORES = [
    {
        "name": "Delhi Watch Company",
        "url": "https://delhiwatchcompany.com/products.json",
        "site": "https://delhiwatchcompany.com",
    },
    {
        "name": "Kala Watches",
        "url": "https://kalawatches.com/products.json",
        "site": "https://kalawatches.com",
    },
    {
        "name": "Coromandel Watch Co",
        "url": "https://coromandelwatchco.com/products.json",
        "site": "https://coromandelwatchco.com",
    },
]

STATE_FILE = "stock_state.json"


def get_telegram_config():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        print("WARNING: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set. Notifications disabled.")
    return token, chat_id


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def fetch_products(store):
    products = []
    page = 1
    while True:
        resp = requests.get(
            store["url"],
            params={"limit": 250, "page": page},
            headers={"User-Agent": "WatchStockMonitor/1.0"},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("products", [])
        if not batch:
            break
        products.extend(batch)
        page += 1
        if len(batch) < 250:
            break
    return products


ACCESSORY_KEYWORDS = [
    "strap", "bracelet", "buckle", "tool", "box", "cap", "shirt",
    "t-shirt", "tee", "merchandise", "merch", "poster", "print",
    "sticker", "mug", "keychain", "pin", "hat", "hoodie", "coaster",
    "card", "notebook", "tote", "nato", "mesh", "sailcloth",
    "paratrooper", "suede", "nappa", "denim", "canvas", "leather",
    "saffiano", "bonklip", "rubber", "silicone",
]


def is_likely_watch(product):
    product_type = (product.get("product_type") or "").lower()
    tags = [t.lower() for t in (product.get("tags") or [])]
    title = product.get("title", "").lower()
    handle = (product.get("handle") or "").lower()

    if any(kw in title for kw in ACCESSORY_KEYWORDS):
        return False
    if any(kw in product_type for kw in ACCESSORY_KEYWORDS):
        return False

    if "watch" in title or "watch" in product_type:
        return True
    if any("watch" in t for t in tags):
        return True
    if "edition" in title or "chronograph" in title:
        return True

    max_price = 0
    for v in product.get("variants", []):
        try:
            max_price = max(max_price, float(v.get("price", "0")))
        except ValueError:
            pass
    if max_price >= 3000:
        return True

    return False


def check_store(store):
    in_stock = []
    products = fetch_products(store)
    for product in products:
        if not is_likely_watch(product):
            continue

        for variant in product.get("variants", []):
            if variant.get("available"):
                in_stock.append({
                    "store": store["name"],
                    "product": product["title"],
                    "variant": variant.get("title", "Default"),
                    "price": variant.get("price", "N/A"),
                    "url": f"{store['site']}/products/{product.get('handle', '')}",
                })
                break
    return in_stock


def send_telegram(message, token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, json=payload, timeout=30)
    if resp.status_code == 200:
        print("Telegram notification sent successfully")
    else:
        print(f"Telegram send failed: {resp.status_code} - {resp.text}")


def send_daily_summary(token, chat_id, all_in_stock):
    if not token or not chat_id:
        return

    message = "\U0001f4cb <b>Daily Stock Summary (12 PM IST)</b>\n\n"

    if all_in_stock:
        message += f"{len(all_in_stock)} watch(es) currently in stock:\n\n"
        for item in all_in_stock:
            message += f"• <b>{item['product']}</b> ({item['variant']})\n"
            message += f"  ₹{item['price']} - {item['store']}\n"
            message += f"  <a href=\"{item['url']}\">Buy Now</a>\n\n"
    else:
        message += "No watches in stock across all 3 stores.\n\n"
        message += "• Delhi Watch Company - all sold out\n"
        message += "• Kala Watches - all sold out\n"
        message += "• Coromandel Watch Co - all sold out\n\n"
        message += "You'll be notified instantly when something restocks."

    send_telegram(message, token, chat_id)


def main():
    daily_summary = os.environ.get("DAILY_SUMMARY", "false") == "true"
    print(f"[{datetime.now().isoformat()}] Watch stock monitor running...")

    token, chat_id = get_telegram_config()
    prev_state = load_state()
    current_state = {}
    new_in_stock = []
    all_in_stock = []

    for store in STORES:
        print(f"  Checking {store['name']}...")
        try:
            items = check_store(store)
            all_in_stock.extend(items)
            for item in items:
                key = f"{item['store']}|{item['product']}|{item['variant']}"
                current_state[key] = item
                if key not in prev_state:
                    new_in_stock.append(item)
            print(f"    Found {len(items)} in-stock items")
        except Exception as e:
            print(f"    Error checking {store['name']}: {e}")
            for key, val in prev_state.items():
                if val.get("store") == store["name"]:
                    current_state[key] = val

    if new_in_stock:
        print(f"\n  NEW IN STOCK: {len(new_in_stock)} items!")
        message = f"\U0001f6a8 <b>WATCH ALERT!</b> {len(new_in_stock)} new item(s) in stock:\n\n"
        for item in new_in_stock:
            message += f"• <b>{item['product']}</b> ({item['variant']})\n"
            message += f"  ₹{item['price']} - {item['store']}\n"
            message += f"  <a href=\"{item['url']}\">Buy Now</a>\n\n"
        message += f"Checked at {datetime.now().strftime('%H:%M %d-%b-%Y')}"

        if token and chat_id:
            send_telegram(message, token, chat_id)
        else:
            print(f"\n  Message (not sent - no config):\n{message}")
    else:
        print(f"\n  No new items in stock.")

    if daily_summary:
        print("  Sending daily summary...")
        send_daily_summary(token, chat_id, all_in_stock)

    save_state(current_state)
    print("Done.")


if __name__ == "__main__":
    main()
