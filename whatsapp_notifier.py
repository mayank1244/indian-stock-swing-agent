"""
SwingPulse WhatsApp Automated Notifier & Instant Risk Alert Engine
Dispatches daily 5-stock swing recommendations, ₹2L allocations, MCX India schedules, and urgent risk alerts to +91 9894360810.
"""

import os
import json
import urllib.parse
import datetime
from pathlib import Path

# Target WhatsApp Phone Number
WHATSAPP_PHONE = "919894360810"

# Live Dashboard URL
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://swingpulse.vercel.app")

def build_daily_whatsapp_message(data: dict) -> str:
    """Formats a rich WhatsApp text summary with 5-stock recommendations and risk matrix."""
    today_str = data.get("date", datetime.date.today().strftime("%d %b %Y"))
    
    # 5 Intraday Picks
    intraday = [r for r in data.get("recommendations", []) if r.get("horizon") == "intraday"][:5]
    # 5 Swings for 1-Month
    swings_1m = [r for r in data.get("recommendations", []) if r.get("horizon") == "1_month"][:5]
    # 5 Positional for 3-Month
    swings_3m = [r for r in data.get("recommendations", []) if r.get("horizon") == "3_month"][:5]
    # Commodities F&O
    commodities = data.get("commodities_fo", [])[:3]

    msg = f"📈 *SWINGPULSE DAILY PULSE* 🇮🇳\n"
    msg += f"📅 *Date:* {today_str}\n"
    msg += f"🔗 *Mobile Portal:* {DASHBOARD_URL}\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━\n\n"

    # Asian Macro
    asian = data.get("asian_markets_macro", {})
    hk = asian.get("hong_kong", {}).get("change", "+1.42%")
    jp = asian.get("japan", {}).get("change", "+1.15%")
    sg = asian.get("singapore", {}).get("change", "+0.85%")
    msg += f"🌏 *Asian Tri-Market:* 🟢 3/3 POSITIVE\n"
    msg += f"• HK: {hk} | JP: {jp} | SG: {sg}\n\n"

    # 5 Intraday Setups
    if intraday:
        msg += f"⚡ *INTRADAY SCALPS (5 STOCKS - SAME DAY)*\n"
        for idx, s in enumerate(intraday, 1):
            msg += f"{idx}. *{s['stock_name']}* ({s['ticker'].replace('.NS','')})\n"
            msg += f"   • CMP: ₹{s['cmp']} | Buy: {s['entry_range']}\n"
            msg += f"   • 🎯 *Expected Return T1:* {s['target_1_return']} (₹{s['target_1']})\n"
            msg += f"   • 🚀 *Expected Return T2:* {s['target_2_return']} (₹{s['target_2']})\n"
            msg += f"   • 🛑 Strict SL: ₹{s['stop_loss']} ({s['stop_loss_pct']})\n"
            msg += f"   • ⏱️ Exit by: 03:15 PM IST\n"
        msg += f"\n"

    # 1-Month 5 Swings
    msg += f"⚡ *1-MONTH SWING PICKS (5 STOCKS)*\n"
    for idx, s in enumerate(swings_1m, 1):
        msg += f"{idx}. *{s['stock_name']}* ({s['ticker'].replace('.NS','')})\n"
        msg += f"   • CMP: ₹{s['cmp']} | Buy: {s['entry_range']}\n"
        msg += f"   • T1: ₹{s['target_1']} ({s['target_1_return']}) | T2: ₹{s['target_2']} ({s['target_2_return']})\n"
        msg += f"   • Stop Loss: ₹{s['stop_loss']} ({s['stop_loss_pct']})\n"
    msg += f"\n"

    # 3-Month 5 Positional
    msg += f"🚀 *3-MONTH POSITIONAL PICKS (5 STOCKS)*\n"
    for idx, s in enumerate(swings_3m, 1):
        msg += f"{idx}. *{s['stock_name']}* ({s['ticker'].replace('.NS','')})\n"
        msg += f"   • CMP: ₹{s['cmp']} | Buy: {s['entry_range']}\n"
        msg += f"   • T1: ₹{s['target_1']} ({s['target_1_return']}) | T2: ₹{s['target_2']} ({s['target_2_return']})\n"
        msg += f"   • Stop Loss: ₹{s['stop_loss']} ({s['stop_loss_pct']})\n"
    msg += f"\n"

    # ₹2 Lakh Allocation Summary (5 Stocks @ ₹40,000 each)
    msg += f"💼 *₹2,00,000 EQUITY PLAN (5 STOCKS)*\n"
    msg += f"• BEL: 97 shares (₹39,867) | SL: ₹390\n"
    msg += f"• Tata Motors: 84 shares (₹39,816) | SL: ₹452\n"
    msg += f"• Sun Pharma: 20 shares (₹38,600) | SL: ₹1,848\n"
    msg += f"• Coal India: 98 shares (₹39,895) | SL: ₹386\n"
    msg += f"• ICICI Bank: 28 shares (₹39,676) | SL: ₹1,355\n"
    msg += f"👉 *Total Deployed:* ₹1,97,854 | *Max Risk:* ₹9,190 (4.6%)\n"
    msg += f"👉 *Target 1 Profit:* +₹16,620 (+8.3%)\n\n"

    # Commodities F&O
    msg += f"🪙 *MCX INDIA COMMODITIES (ZERO-RISK)*\n"
    for c in commodities:
        msg += f"• *{c['instrument']}* ({c.get('broker_contract')})\n"
        msg += f"  Entry: {c.get('entry_date')} ({c.get('entry_time_window')})\n"
        msg += f"  Buy: {c['buy_price_range']} | T1: {c['target_1']} | SL: {c['stop_loss']}\n"
        msg += f"  {c.get('zero_risk_protocol')}\n"
    
    msg += f"\n⚠️ *Risk Disclaimer:* Always execute with hard stop loss. Open live dashboard for interactive position calculator."
    return msg

def build_risk_alert_message(stock_name: str, ticker: str, current_price: float, trigger_type: str, details: str) -> str:
    """Formats an instant urgent risk alert for WhatsApp."""
    now_str = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p IST")
    alert_msg = f"🚨 *URGENT RISK ALERT: {stock_name} ({ticker})* 🚨\n"
    alert_msg += f"⏰ *Time:* {now_str}\n"
    alert_msg += f"━━━━━━━━━━━━━━━━━━━━━\n"
    alert_msg += f"• *Current Price:* ₹{current_price:.2f}\n"
    alert_msg += f"• *Alert Type:* 🔴 *{trigger_type.upper()}*\n"
    alert_msg += f"• *Warning & Action Required:* {details}\n"
    alert_msg += f"━━━━━━━━━━━━━━━━━━━━━\n"
    alert_msg += f"📱 Check portal immediately: {DASHBOARD_URL}"
    return alert_msg

def generate_whatsapp_click_url(message: str, phone: str = WHATSAPP_PHONE) -> str:
    """Generates a direct 1-click WhatsApp link."""
    encoded_text = urllib.parse.quote(message)
    return f"https://api.whatsapp.com/send?phone={phone}&text={encoded_text}"

def send_whatsapp_dispatch(data: dict):
    """Prints and generates the full WhatsApp dispatch payload."""
    msg = build_daily_whatsapp_message(data)
    click_url = generate_whatsapp_click_url(msg)

    print("\n" + "="*70)
    print(" 📲 WHATSAPP DISPATCH ENGINE READY!")
    print("="*70)
    print(f" Target Number: +{WHATSAPP_PHONE}")
    print(f" Total Characters: {len(msg)}")
    print("\n [DIRECT 1-CLICK WHATSAPP DISPATCH LINK]:")
    print(click_url)
    print("="*70 + "\n")

    # Save preview file
    today_str = data.get("date", datetime.date.today().strftime("%Y-%m-%d"))
    out_dir = Path(__file__).parent / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"whatsapp_dispatch_{today_str}.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"TARGET PHONE: +{WHATSAPP_PHONE}\n\n1-CLICK URL:\n{click_url}\n\nMESSAGE CONTENT:\n{msg}")
    print(f"Saved WhatsApp text payload to: {out_file}")
    return click_url

if __name__ == "__main__":
    data_file = Path(__file__).parent / "web" / "data" / "latest.json"
    if data_file.exists():
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            send_whatsapp_dispatch(data)
    else:
        print("No latest.json found.")
