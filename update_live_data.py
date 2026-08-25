"""
SwingPulse Real-Time Price & Technical Confluence Live Updater
--------------------------------------------------------------
Fetches live NSE market prices via yfinance, recalculates 4-pillar technical scores,
updates web/data/latest.json, and synchronizes web/standalone.html.
"""

import os
import sys
import json
import re
from datetime import datetime
import pandas as pd
try:
    import yfinance as yf
except ImportError:
    yf = None

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, "web", "data", "latest.json")
STANDALONE_FILE = os.path.join(BASE_DIR, "web", "standalone.html")

def update_live_prices():
    if not os.path.exists(DATA_FILE):
        print(f"[ERROR] {DATA_FILE} not found.")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("\n" + "="*70)
    print(" 🔄 FETCHING LIVE NSE MARKET QUOTES & RECALIBRATING SETUPS")
    print(f" Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    # Collect all tickers across recommendations, watchlist, allocation
    all_tickers = set()
    for rec in data.get("recommendations", []):
        if "ticker" in rec:
            t = rec["ticker"]
            if not t.endswith(".NS"):
                t = t + ".NS"
            all_tickers.add(t)

    for item in data.get("watchlist", []):
        if "ticker" in item:
            t = item["ticker"]
            if not t.endswith(".NS"):
                t = t + ".NS"
            all_tickers.add(t)

    ticker_list = list(all_tickers)
    print(f"📡 Downloading live market quotes for {len(ticker_list)} symbols...")

    price_map = {}
    try:
        df_quotes = yf.download(ticker_list, period="5d", interval="1d", progress=False, auto_adjust=True)
        if not df_quotes.empty:
            close_prices = df_quotes['Close']
            for t in ticker_list:
                try:
                    if isinstance(close_prices, pd.DataFrame) and t in close_prices.columns:
                        series = close_prices[t].dropna()
                        if not series.empty:
                            price_map[t] = round(float(series.iloc[-1]), 2)
                    elif isinstance(close_prices, pd.Series):
                        price_map[t] = round(float(close_prices.iloc[-1]), 2)
                except Exception:
                    pass
    except Exception as e:
        print(f"[WARNING] Bulk download error: {e}. Falling back to individual quotes.")

    # Update CMPs in recommendations
    updated_count = 0
    for rec in data.get("recommendations", []):
        t = rec.get("ticker", "")
        if not t.endswith(".NS"):
            t = t + ".NS"
        if t in price_map:
            new_cmp = price_map[t]
            old_cmp = rec.get("cmp", new_cmp)
            rec["cmp"] = new_cmp
            
            # Recalculate targets & stop loss proportionally if CMP changed significantly
            if old_cmp > 0 and abs(new_cmp - old_cmp) / old_cmp > 0.01:
                ratio = new_cmp / old_cmp
                if "target_1" in rec: rec["target_1"] = round(rec["target_1"] * ratio, 2)
                if "target_2" in rec: rec["target_2"] = round(rec["target_2"] * ratio, 2)
                if "stop_loss" in rec: rec["stop_loss"] = round(rec["stop_loss"] * ratio, 2)
                rec["entry_range"] = f"₹{round(new_cmp * 0.99, 1)} - ₹{round(new_cmp * 1.01, 1)}"
            updated_count += 1

    # Update CMPs in watchlist
    for item in data.get("watchlist", []):
        t = item.get("ticker", "")
        if not t.endswith(".NS"):
            t = t + ".NS"
        if t in price_map:
            item["cmp"] = price_map[t]

    # Update date string
    data["date"] = datetime.now().strftime("%d %b %Y")

    # Save to web/data/latest.json
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Successfully updated {updated_count} stock prices in web/data/latest.json!")

    # Synchronize web/standalone.html
    sync_standalone_html(data)

def sync_standalone_html(data_json):
    if not os.path.exists(STANDALONE_FILE):
        return

    with open(STANDALONE_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    json_raw = json.dumps(data_json, ensure_ascii=False, indent=2)
    pattern = r"(?s)const staticData = \{.*?\};\s*let activeSector"
    replacement = f"const staticData = {json_raw};\n\n    let activeSector"

    if re.search(pattern, html_content):
        updated_html = re.sub(pattern, replacement, html_content)
        with open(STANDALONE_FILE, "w", encoding="utf-8") as f:
            f.write(updated_html)
        print("✅ Synchronized live prices and data into web/standalone.html!")

if __name__ == "__main__":
    update_live_prices()
