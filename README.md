# Indian Stock Market Swing Trading Agent 🇮🇳 📈

Autonomous AI Agent built with Google Antigravity to screen, analyze, and generate **1-month swing trading recommendations** on the National Stock Exchange of India (NSE).

---

## 🏗️ How the Agent Works (4-Pillar Confluence Engine)

1. **Candlestick & Price Action**: Identifies daily/weekly patterns (Hammer, Bullish Engulfing, Morning Star, 20-Day Breakouts, EMA pullbacks).
2. **Moving Averages & Momentum**: Confirms 20/50/200 EMA alignment, RSI (50–65 sweet spot), and 1.5x–2x volume surges.
3. **News & Market Catalysts**: Searches recent corporate announcements, earnings reports, order wins, and FII/DII institutional sentiment.
4. **Institutional Risk Management**: Enforces strict minimum **1 : 2.5 Risk-to-Reward Ratio (RRR)**, Entry Range, Target 1 (~6-10%), Target 2 (~12-20%), and Stop-Loss.

---

## 🚀 Ways to Run & Schedule Daily

### Option 1: Trigger Daily via Antigravity Schedule (Recommended)
You can schedule Antigravity to run this scan every weekday morning before the Indian market opens:

```text
/schedule cron: "30 8 * * 1-5" prompt: "Run the daily Indian Stock Market swing trading scanner, check latest news and sector catalysts, and generate today's top 1-month swing trade recommendations."
```
*(Or post-market close at 16:00 IST: `0 16 * * 1-5`)*

---

### Option 2: Ask the In-Session Antigravity Subagent Directly
The subagent `indian_swing_trader` is pre-configured. In your Antigravity chat, simply type:
> *"Run today's swing trade scan for Nifty 100 stocks and provide top 3 recommendations."*

---

### Option 3: Run via Python CLI / Standalone Runner

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Set your Gemini API Key** (if not already set in environment):
   ```bash
   set GEMINI_API_KEY="your-api-key"
   ```
3. **Execute the Agent**:
   ```bash
   python agent.py
   ```
   Reports will automatically be saved under `./reports/YYYY-MM-DD_recommendations.md`.
