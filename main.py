# === BTC Full MM Terminal → Telegram ===
# Coded for tracking BTC sentiment, MM behavior, and key metrics snapshot
# Safe: No trading actions, just data feed & Telegram notification

import requests
import time
from datetime import datetime

# ==== CONFIGURATION ====
TG_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TG_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"
GLASSNODE_API_KEY = "YOUR_GLASSNODE_API_KEY"

# ==== DATA SOURCES ====
BINANCE_API = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
COINGLASS_FUNDING_API = "https://open-api.coinglass.com/api/futures/funding_rate_chart?symbol=BTC"
COINGLASS_HEADERS = {"coinglassSecret": "YOUR_COINGLASS_API_KEY"}

# ==== FUNCTIONS ====

def get_btc_price():
    try:
        res = requests.get(BINANCE_API, timeout=10)
        data = res.json()
        return float(data["price"])
    except Exception as e:
        return None

def get_funding_rate():
    try:
        res = requests.get(COINGLASS_FUNDING_API, headers=COINGLASS_HEADERS, timeout=10)
        data = res.json()
        rate = data["data"]["Binance"][-1]["fundingRate"]
        return round(rate * 100, 4)
    except Exception:
        return None

def get_open_interest():
    try:
        url = f"https://api.glassnode.com/v1/metrics/derivatives/open_interest_perpetual_future?api_key={GLASSNODE_API_KEY}&symbol=BTC"
        res = requests.get(url, timeout=10)
        data = res.json()
        oi = float(data[-1]["v"])
        return round(oi / 1_000_000_000, 3)  # In billions
    except Exception:
        return None

def get_sentiment():
    try:
        url = "https://api.alternative.me/fng/"
        res = requests.get(url, timeout=10)
        data = res.json()
        return data["data"][0]["value_classification"]
    except Exception:
        return None

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Telegram send error:", e)

# ==== MAIN SNAPSHOT ====
def run_snapshot():
    btc_price = get_btc_price()
    funding_rate = get_funding_rate()
    open_interest = get_open_interest()
    sentiment = get_sentiment()

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    message = (
        f"📊 <b>BTC – Full MM Terminal Snapshot</b>\n"
        f"🕒 {now}\n\n"
        f"💰 <b>Price:</b> ${btc_price:,.2f}\n"
        f"📈 <b>Funding Rate:</b> {funding_rate}%\n"
        f"🏦 <b>Open Interest:</b> {open_interest}B\n"
        f"🧠 <b>Sentiment:</b> {sentiment}\n\n"
        f"⚙️ Data: Binance | Coinglass | Glassnode | Alt.me\n"
        f"🛰 Status: Active feed ✅"
    )

    send_to_telegram(message)

# ==== LOOP / AUTO RUN ====
if __name__ == "__main__":
    while True:
        run_snapshot()
        time.sleep(4 * 60 * 60)  # every 4 hours
