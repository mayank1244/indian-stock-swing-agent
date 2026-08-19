"""
Indian Stock Market Swing Trading Technical Scanner
Scans high-liquidity NSE stocks for candlestick patterns, EMA trends, RSI momentum, and volume breakouts.
"""

import sys
import datetime
import pandas as pd
import numpy as np

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    import yfinance as yf
except ImportError:
    yf = None

# Default candidate pool: Liquid large & mid-cap stocks across key sectors
DEFAULT_TICKERS = [
    # Auto & Ancillaries
    "TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "BHARATFORG.NS",
    # Banking & Financials
    "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "FEDERALBNK.NS", "BAJFINANCE.NS",
    # IT & Tech
    "TCS.NS", "INFY.NS", "HCLTECH.NS", "PERSISTENT.NS", "COFORGE.NS", "KPITTECH.NS",
    # Pharma & Healthcare
    "SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "LUPIN.NS", "APOLLOHOSP.NS", "MANKIND.NS",
    # Energy, Oil & Power
    "RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "TATAPOWER.NS", "ONGC.NS", "COALINDIA.NS",
    # Metals & Mining
    "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "JINDALSTEL.NS", "VEDL.NS",
    # Capital Goods, Defence & Infra
    "LT.NS", "BEL.NS", "HAL.NS", "BHEL.NS", "SIEMENS.NS", "ABB.NS",
    # FMCG & Consumption
    "ITC.NS", "HINDUNILVR.NS", "TATACONSUM.NS", "VARUN.NS", "TITAN.NS", "TRENT.NS"
]

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line
    return macd, signal_line, hist

def detect_candlestick_patterns(df: pd.DataFrame) -> dict:
    """Identifies key daily candlestick reversal and breakout patterns."""
    if len(df) < 5:
        return {}
    
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    prev2 = df.iloc[-3]
    
    open_c, high_c, low_c, close_c = curr['Open'], curr['High'], curr['Low'], curr['Close']
    open_p, high_p, low_p, close_p = prev['Open'], prev['High'], prev['Low'], prev['Close']
    
    body = abs(close_c - open_c)
    total_range = high_c - low_c if high_c != low_c else 0.001
    lower_shadow = min(open_c, close_c) - low_c
    upper_shadow = high_c - max(open_c, close_c)
    
    patterns = []
    
    # 1. Hammer / Bullish Pin Bar
    if (lower_shadow >= 2 * body) and (upper_shadow <= 0.2 * body) and (close_c >= open_c):
        patterns.append("Hammer / Bullish Pin Bar (Reversal)")
        
    # 2. Bullish Engulfing
    if (close_p < open_p) and (close_c > open_c) and (open_c <= close_p) and (close_c >= open_p):
        patterns.append("Bullish Engulfing (Strong Reversal)")
        
    # 3. Morning Star (3-bar pattern)
    if (prev2['Close'] < prev2['Open']) and (abs(prev['Close'] - prev['Open']) < (prev2['Open'] - prev2['Close']) * 0.4) and (close_c > open_c) and (close_c > (prev2['Open'] + prev2['Close']) / 2):
        patterns.append("Morning Star (High Conviction Reversal)")
        
    # 4. Multi-week Consolidation Breakout (20-day High Breakout with High Close)
    high_20d = df['High'].iloc[-21:-1].max() if len(df) >= 21 else df['High'].max()
    if close_c > high_20d:
        patterns.append("20-Day Range Breakout (Momentum Continuation)")

    # 5. Pullback to 20 EMA bounce
    if 'EMA_20' in df.columns:
        ema20 = curr['EMA_20']
        if (low_c <= ema20 * 1.01) and (close_c > ema20) and (close_c > open_c):
            patterns.append("20 EMA Support Bounce (Trend Pullback)")

    return {
        "patterns": patterns,
        "is_bullish": len(patterns) > 0
    }

def scan_stock(ticker: str) -> dict:
    """Fetches daily data, calculates indicators, and filters swing opportunities."""
    try:
        data = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=True)
        if data.empty or len(data) < 50:
            return None
        
        # Flatten MultiIndex columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]
            
        data['EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()
        data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean()
        data['EMA_200'] = data['Close'].ewm(span=200, adjust=False).mean() if len(data) >= 200 else data['Close'].ewm(span=len(data), adjust=False).mean()
        data['RSI'] = calculate_rsi(data['Close'])
        data['Vol_SMA20'] = data['Volume'].rolling(window=20).mean()
        
        curr = data.iloc[-1]
        candle_info = detect_candlestick_patterns(data)
        
        cmp = float(curr['Close'])
        ema20 = float(curr['EMA_20'])
        ema50 = float(curr['EMA_50'])
        ema200 = float(curr['EMA_200'])
        rsi = float(curr['RSI'])
        vol = float(curr['Volume'])
        vol_avg = float(curr['Vol_SMA20']) if not pd.isna(curr['Vol_SMA20']) else vol
        
        vol_ratio = vol / (vol_avg + 1e-9)
        
        # Swing filter conditions:
        # 1. Price > 50 EMA & 20 EMA > 50 EMA (Uptrend)
        # 2. RSI between 45 and 70 (Healthy momentum zone)
        # 3. Volume ratio > 1.2 or Bullish Candlestick Pattern detected
        is_uptrend = cmp > ema50 and ema20 >= ema50 * 0.99
        is_rsi_valid = 45 <= rsi <= 72
        has_volume = vol_ratio >= 1.2 or candle_info['is_bullish']
        
        score = 0
        if is_uptrend: score += 30
        if is_rsi_valid: score += 20
        if vol_ratio >= 1.5: score += 25
        if candle_info['is_bullish']: score += 25
        
        if score >= 65:
            # Calculate preliminary swing trade levels (1:2.5 to 1:3 RRR)
            recent_low = float(data['Low'].iloc[-5:].min())
            stop_loss = round(min(recent_low * 0.985, cmp * 0.95), 2)
            risk = cmp - stop_loss
            target_1 = round(cmp + (risk * 2.0), 2)
            target_2 = round(cmp + (risk * 3.2), 2)
            
            return {
                "ticker": ticker.replace(".NS", ""),
                "full_ticker": ticker,
                "cmp": round(cmp, 2),
                "ema20": round(ema20, 2),
                "ema50": round(ema50, 2),
                "rsi": round(rsi, 1),
                "volume_ratio": round(vol_ratio, 2),
                "patterns": candle_info["patterns"],
                "score": score,
                "entry_range": f"₹{round(cmp*0.99, 1)} - ₹{round(cmp*1.01, 1)}",
                "target_1": target_1,
                "target_2": target_2,
                "stop_loss": stop_loss,
                "rrr": f"1 : {round((target_1 - cmp) / (risk + 1e-9), 1)}"
            }
    except Exception as e:
        # Ignore fetch errors for specific tickers
        return None
    return None

def run_screener(tickers=None):
    if yf is None:
        print("Please install yfinance: pip install yfinance")
        return []
    
    tickers = tickers or DEFAULT_TICKERS
    candidates = []
    print(f"Scanning {len(tickers)} Indian stocks for 1-month swing setups...")
    
    for t in tickers:
        res = scan_stock(t)
        if res:
            candidates.append(res)
            
    # Sort by technical confluence score
    candidates.sort(key=lambda x: (x['score'], x['volume_ratio']), reverse=True)
    return candidates

if __name__ == "__main__":
    results = run_screener()
    print(f"Found {len(results)} high-probability candidates:")
    for c in results[:5]:
        print(f"- {c['ticker']} (CMP: ₹{c['cmp']}) | Score: {c['score']} | Patterns: {c['patterns']} | Vol: {c['volume_ratio']}x | RSI: {c['rsi']}")
