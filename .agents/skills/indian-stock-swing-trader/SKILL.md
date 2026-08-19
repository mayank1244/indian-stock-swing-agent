---
name: indian-stock-swing-trader
description: "Identifies high-probability swing trade opportunities in the Indian Equity Market (NSE/BSE) for a 1-month holding period using multi-timeframe candlestick patterns, momentum, volume breakouts, and real-time news/sector catalysts."
---

# Indian Stock Market Swing Trading Agent (1-Month Horizon)

This skill equips Antigravity to act as an institutional-grade Indian Equity Technical Analyst and Swing Trader.

## Core Evaluation Protocol (1-Month vs 3-Month Horizons)

### 1. Candlestick & Price Action Filter
- **1-Month Fast Swings (3–4 Weeks)**:
  - Daily chart primary with weekly trend alignment.
  - Reversal: Daily Bullish Engulfing, Morning Star, Hammer at 20/50 EMA.
  - Continuation: 20-Day Range Breakout, Flag & Pole, Pullback retest.
  - Targets: Target 1 (+8% to +10%), Target 2 (+15% to +20%), Stop Loss (-4% to -5%).
- **3-Month Positional Swings (10–14 Weeks)**:
  - Weekly & Monthly multi-timeframe charts primary (Stan Weinstein Stage 2 expansion).
  - Patterns: Multi-month Base Breakouts, Weekly Cup & Handle, Weekly Ascending Triangle, 52-Week High Breakouts.
  - EMAs: 20 WEMA > 50 WEMA > 200 WEMA (Super-trend alignment).
  - Targets: Target 1 (+15% to +22%), Target 2 (+30% to +45%), Stop Loss (-6% to -7%).
  - Minimum RRR: **1 : 3.5 to 1 : 5**.

### 2. Indicator & Volume Confluence
- **Moving Averages**: Price > 20 EMA > 50 EMA (for 1M) and Price > 20 WEMA > 50 WEMA (for 3M).
- **Volume**: Minimum **1.5x to 2x** of 20-day Average Volume (or 20-week volume for 3M).
- **RSI (14)**: 50–68 range with strong relative strength vs Nifty 50.
- **MACD**: Weekly MACD positive expansion above signal line.

### 3. News & Fundamental Health Check
- Pillar 4: News Catalysts, Macro & Institutional Sentiment
- Cross-reference quarterly earnings surprises, order book wins, sector tailwinds, and FII/DII institutional positioning.
- Avoid stocks with active promoter de-pledging failures, SEBI forensic audits, or unresolved accounting investigations.

---

## 5. Asian Market Tri-Confirmation Rule for Commodities & F&O Derivatives

To filter out false breakouts and global head-fakes in Indian Commodity & Index F&O contracts (MCX Crude Oil, Gold Mini, Natural Gas, Silver, and NSE Index Call/Put Options):

### The 3 Asian Pillars Condition:
1. **🇭🇰 Hong Kong (Hang Seng Index - HSI)**: Must be in the **GREEN / Positive** (Indicates China liquidity, industrial metal demand, and regional emerging market risk appetite).
2. **🇯🇵 Japan (Nikkei 225)**: Must be in the **GREEN / Positive** (Indicates export resilience, global supply chain health, and currency carry-trade stability).
3. **🇸🇬 Singapore (SGX / GIFT Nifty)**: Must be in the **GREEN / Positive** (Indicates institutional FII overnight risk-on positioning into Indian assets).

### Execution Rules:
- **Condition Trigger**: **ONLY if all 3 Asian markets are positive**, execute high-conviction F&O and Commodity setups.
- **If Any Asian Market is Negative/Mixed**: **RISK-OFF MODE**. No F&O / Derivative buy recommendations are issued (cash capital protection).
- **Execution Timing**:
  - **NSE Index Options (Nifty / Bank Nifty)**: Enter between **09:15 AM – 09:35 AM** on 15-min range breakout.
  - **MCX Crude Oil & Natural Gas**: Enter between **05:00 PM – 05:30 PM** during US NYMEX session opening volume crossover.
  - **MCX Gold / Silver**: Enter during morning European open (01:30 PM) or US evening surge (05:00 PM).
- **Exit Strategy**:
  - **Intraday**: Book 50% profits at Target 1, trail Stop Loss to Entry Cost, square off before 11:15 PM MCX / 03:15 PM NSE.
  - **Positional Swing**: Maximum 2–4 days holding with strict trailing Stop Loss.

---

## Output Template

Always format the output into structured Trade Cards:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STOCK NAME: [Stock Name (NSE Ticker)] | SECTOR: [Sector]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Current Market Price (CMP): ₹[Price]
• Recommended Action: [Buy on Dip / Buy at CMP / Buy on Breakout above ₹X]
• Ideal Entry Range: ₹[Min] - ₹[Max]
• Target 1 (Conservative, 2-3 Weeks): ₹[Price] (~[X]% return)
• Target 2 (Extended, 4-5 Weeks): ₹[Price] (~[Y]% return)
• Hard Stop Loss (Strict Daily Closing Basis): ₹[Price] (~[Z]% risk)
• Risk-to-Reward Ratio: 1 : [X]

TECHNICAL CONFLUENCE:
- Candlestick Pattern: [Pattern name, timeframe, trigger candle confirmation]
- Moving Averages & Levels: [20/50/200 EMA status, support/resistance]
- Volume & Momentum: [Volume vs 20-day avg, RSI(14), MACD status]

NEWS & CATALYST CONFLUENCE:
- Key News/Developments: [Recent corporate developments, earnings, order wins]
- Sector & Institutional Bias: [Sector trend, FII/DII flow]

TRADE INVALIDATION CRITERIA:
- [Specific event or price violation triggering immediate exit]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
