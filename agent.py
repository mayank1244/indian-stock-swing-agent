"""
SwingPulse Autonomous Antigravity Agent
Coordinates technical scanning, live verified market quotes, 5-stock swing portfolios, ₹2L allocations, email dispatches, and WhatsApp alerts to +91 9894360810.
"""

import os
import sys
import json
import datetime
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from email_notifier import send_daily_email
from whatsapp_notifier import send_whatsapp_dispatch, build_risk_alert_message, generate_whatsapp_click_url

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "web" / "data" / "latest.json"

def run_daily_agent_cycle():
    print("\n" + "="*70)
    print(" 🚀 SWINGPULSE AUTONOMOUS AGENT RUNNING (5-STOCK RECALIBRATION)")
    print(f" Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    if not DATA_FILE.exists():
        print(f"[ERROR] Data file not found: {DATA_FILE}")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Verification of 5 stocks per horizon
    swings_1m = [r for r in data.get("recommendations", []) if r.get("horizon") == "1_month"]
    swings_3m = [r for r in data.get("recommendations", []) if r.get("horizon") == "3_month"]
    watchlist = data.get("watchlist", [])

    print(f"✅ Loaded 1-Month Setups: {len(swings_1m)} stocks")
    print(f"✅ Loaded 3-Month Setups: {len(swings_3m)} stocks")
    print(f"✅ Loaded Watchlist Items: {len(watchlist)} stocks")

    # 2. Trigger Daily Email to nareshofficial.kumar@gmail.com
    print("\n[STEP 1] Generating Email Dispatch...")
    send_daily_email(data)

    # 3. Trigger WhatsApp Dispatch to +91 9894360810
    print("\n[STEP 2] Generating WhatsApp Dispatch Payload (+919894360810)...")
    wa_url = send_whatsapp_dispatch(data)

    # 4. Check for high-risk alert triggers in watchlist
    print("\n[STEP 3] Running Automated Risk Radar & Alert Scanner...")
    for item in watchlist:
        if item.get("risk_rating") == "HIGH":
            alert_text = build_risk_alert_message(
                stock_name=item['stock_name'],
                ticker=item['ticker'],
                current_price=item['cmp'],
                trigger_type="HIGH RISK / VALUATION CAUTION",
                details=f"{item['risk_summary']}. Action: {item['action_plan']}"
            )
            alert_url = generate_whatsapp_click_url(alert_text)
            print(f"🚨 [RISK ALERT DETECTED] {item['stock_name']} ({item['ticker']}):")
            print(f"   Link: {alert_url[:80]}...")

    print("\n" + "="*70)
    print(" 🎯 DAILY AGENT CYCLE COMPLETE!")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_daily_agent_cycle()
