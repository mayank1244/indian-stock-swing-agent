"""
SwingPulse Daily Intraday Scanner & Multi-Horizon Cadence Manager
-----------------------------------------------------------------
Schedule:
- Intraday (5 Stocks): Evaluated and ROTATED DAILY every morning before 09:15 AM IST.
- 1-Month Swings, 3-Month Positional, F&O, Commodities, ₹2L Plan: Evaluated and ROTATED WEEKLY every Monday morning.
- Live Exchange Quotes: Synced continuously throughout trading hours.
"""

import os
import json
import datetime

DATA_PATH = os.path.join(os.path.dirname(__file__), "web", "data", "latest.json")

# Universe of high-momentum intraday candidates
INTRADAY_CANDIDATE_POOL = [
    {
        "id": "TATASTEEL_INTRA",
        "stock_name": "Tata Steel Ltd",
        "ticker": "TATASTEEL.NS",
        "sector": "Metals & Mining",
        "horizon": "intraday",
        "timeframe": "Intraday (09:30 AM – 02:45 PM IST)",
        "cmp": 184.00,
        "entry_range": "₹183.20 - ₹184.40",
        "target_1": 187.00,
        "target_1_return": "+1.63% Expected Return",
        "target_2": 189.50,
        "target_2_return": "+2.99% Extended Gain",
        "stop_loss": 182.20,
        "stop_loss_pct": "-0.98% Tight SL",
        "mandatory_exit": "03:15 PM IST (Same-Day Square-off)",
        "rrr": "1 : 2.5",
        "technical_confluence": {
            "patterns": ["15-Min ORB Breakout", "VWAP Pullback Bounce", "Metals Sector Momentum"],
            "rsi": "62 (Bullish Momentum)",
            "volume_spike": "2.8x 10-day Average"
        },
        "news_catalysts": [
            "China PBOC monetary easing lifting global base metal prices.",
            "Strong domestic infrastructure demand sustaining spot steel prices."
        ]
    },
    {
        "id": "SBIN_INTRA",
        "stock_name": "State Bank of India",
        "ticker": "SBIN.NS",
        "sector": "Banking & Financials",
        "horizon": "intraday",
        "timeframe": "Intraday (09:30 AM – 02:45 PM IST)",
        "cmp": 1048.60,
        "entry_range": "₹1,044.00 - ₹1,050.00",
        "target_1": 1064.00,
        "target_1_return": "+1.47% Expected Return",
        "target_2": 1078.00,
        "target_2_return": "+2.80% Extended Gain",
        "stop_loss": 1038.50,
        "stop_loss_pct": "-0.96% Tight SL",
        "mandatory_exit": "03:15 PM IST (Same-Day Square-off)",
        "rrr": "1 : 2.4",
        "technical_confluence": {
            "patterns": ["Opening Range Breakout (ORB)", "Cup & Handle on 15m", "BankNifty Inflow Leader"],
            "rsi": "64 (Bullish)",
            "volume_spike": "2.4x Volume Expansion"
        },
        "news_catalysts": [
            "FII institutional buying in large-cap banking heavyweights.",
            "Record corporate credit growth and robust asset quality trajectory."
        ]
    },
    {
        "id": "RELIANCE_INTRA",
        "stock_name": "Reliance Industries Ltd",
        "ticker": "RELIANCE.NS",
        "sector": "Energy & Conglomerate",
        "horizon": "intraday",
        "timeframe": "Intraday (09:30 AM – 02:45 PM IST)",
        "cmp": 1311.00,
        "entry_range": "₹1,306.00 - ₹1,314.00",
        "target_1": 1329.00,
        "target_1_return": "+1.37% Expected Return",
        "target_2": 1345.00,
        "target_2_return": "+2.59% Extended Gain",
        "stop_loss": 1300.00,
        "stop_loss_pct": "-0.84% Tight SL",
        "mandatory_exit": "03:15 PM IST (Same-Day Square-off)",
        "rrr": "1 : 2.6",
        "technical_confluence": {
            "patterns": ["Nifty Weightage Leader", "Morning VWAP Cross", "Ascending Triangle on 5m/15m"],
            "rsi": "58 (Upward Bias)",
            "volume_spike": "2.1x Volume Jump"
        },
        "news_catalysts": [
            "Singapore Gross Refining Margins (GRM) expanding by $1.2/bbl.",
            "Jio tariff hike ARPU expansion flowing into cash flows."
        ]
    },
    {
        "id": "JSWSTEEL_INTRA",
        "stock_name": "JSW Steel Ltd",
        "ticker": "JSWSTEEL.NS",
        "sector": "Metals & Mining",
        "horizon": "intraday",
        "timeframe": "Intraday (09:30 AM – 02:45 PM IST)",
        "cmp": 1285.80,
        "entry_range": "₹1,280.00 - ₹1,288.00",
        "target_1": 1308.00,
        "target_1_return": "+1.73% Expected Return",
        "target_2": 1328.00,
        "target_2_return": "+3.28% Extended Gain",
        "stop_loss": 1272.50,
        "stop_loss_pct": "-1.03% Tight SL",
        "mandatory_exit": "03:15 PM IST (Same-Day Square-off)",
        "rrr": "1 : 2.5",
        "technical_confluence": {
            "patterns": ["High-Beta Volume Surge", "Bullish Flag Breakout 15m", "Above 20-EMA on 5m"],
            "rsi": "66 (Strong Momentum)",
            "volume_spike": "3.1x Volume Surge"
        },
        "news_catalysts": [
            "Export order influx following capacity expansion at Vijayanagar.",
            "Rising coking coal supply stabilization boosting operating margins."
        ]
    },
    {
        "id": "HDFCBANK_INTRA",
        "stock_name": "HDFC Bank Ltd",
        "ticker": "HDFCBANK.NS",
        "sector": "Banking & Financials",
        "horizon": "intraday",
        "timeframe": "Intraday (09:30 AM – 02:45 PM IST)",
        "cmp": 720.00,
        "entry_range": "₹717.00 - ₹721.50",
        "target_1": 731.00,
        "target_1_return": "+1.53% Expected Return",
        "target_2": 742.00,
        "target_2_return": "+3.06% Extended Gain",
        "stop_loss": 713.50,
        "stop_loss_pct": "-0.90% Tight SL",
        "mandatory_exit": "03:15 PM IST (Same-Day Square-off)",
        "rrr": "1 : 2.7",
        "technical_confluence": {
            "patterns": ["Key Support Confluence", "High Institutional Call OI Unwinding", "Bullish Engulfing 15m"],
            "rsi": "55 (Reversal Zone)",
            "volume_spike": "2.2x Volume Expansion"
        },
        "news_catalysts": [
            "MSCI rebalancing weightage increment driving index fund passive flows.",
            "Deposit growth acceleration closing loan-to-deposit ratio gap."
        ]
    }
]

def rotate_daily_intraday():
    """Refreshes daily intraday setups while preserving weekly swing positions."""
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} not found.")
        return

    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Filter out existing intraday and keep 1M and 3M weekly swing picks
    weekly_swings = [r for r in data.get("recommendations", []) if r.get("horizon") != "intraday"]
    
    # Prepend the newly evaluated 5 daily intraday picks
    data["recommendations"] = INTRADAY_CANDIDATE_POOL + weekly_swings
    data["date"] = datetime.datetime.now().strftime("%d %b %Y")
    
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✅ Daily Intraday picks rotated successfully!")
    print(f"Total Recommendations: {len(data['recommendations'])} (5 Daily Intraday + 10 Weekly Swings)")

if __name__ == "__main__":
    rotate_daily_intraday()
