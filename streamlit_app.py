import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="SwingPulse 🇮🇳 - Indian Equity Swing Trading Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: #0f172a;
        color: #f8fafc;
    }

    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    
    .title-gradient {
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.2rem;
        margin: 0;
    }
    
    .card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .card:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
    }

    .badge-bullish {
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .badge-high-risk {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 1.4rem;
    }
    
    .entry-box {
        background: rgba(56, 189, 248, 0.1);
        border-left: 4px solid #38bdf8;
        padding: 10px 14px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    .target-box {
        background: rgba(34, 197, 94, 0.1);
        border-left: 4px solid #22c55e;
        padding: 10px 14px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    .sl-box {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
        padding: 10px 14px;
        border-radius: 4px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Load Data Function
@st.cache_data(ttl=60)
def load_market_data():
    data_path = os.path.join(os.path.dirname(__file__), "web", "data", "latest.json")
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

data = load_market_data()

# Header Banner
st.markdown("""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 class="title-gradient">SwingPulse 🇮🇳</h1>
            <p style="color: #94a3b8; margin-top: 6px; font-size: 1rem;">
                Autonomous AI Agent for Indian Equity Technical Analysis & Swing Trading (NSE)
            </p>
        </div>
        <div style="text-align: right;">
            <span class="badge-bullish">🟢 AI AGENT ACTIVE</span>
            <p style="color: #64748b; font-size: 0.85rem; margin-top: 8px;">
                Updated: """ + (data.get("date", datetime.now().strftime("%d %b %Y")) if data else datetime.now().strftime("%d %b %Y")) + """
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if not data:
    st.error("⚠️ Market data file (`latest.json`) not found. Please run `py generate_data.py` to generate initial dataset.")
    st.stop()

# Macro Indicator Bar
st.subheader("🌐 Market Regime & Macro Confluence")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

m_status = data.get("market_status", {})
asian_macro = data.get("asian_markets_macro", {})

with col_m1:
    st.metric(label="Nifty 50 Trend", value=m_status.get("nifty_trend", "N/A"))

with col_m2:
    st.metric(label="Bank Nifty Trend", value=m_status.get("bank_nifty_trend", "N/A"))

with col_m3:
    st.metric(label="Asian Macro Status", value=asian_macro.get("status", "BULLISH"), delta="Tri-Pillar Active")

with col_m4:
    st.metric(label="FII / DII Institutional Bias", value="Net Buyer", delta=m_status.get("fii_dii_bias", "+₹3,600 Cr"))

# Asian Markets Tri-Confirmation Expander
with st.expander("🌏 Asian Markets Tri-Confirmation Rule (F&O & Commodity Filter)", expanded=True):
    col_a1, col_a2, col_a3 = st.columns(3)
    hk = asian_macro.get("hong_kong", {})
    jp = asian_macro.get("japan", {})
    sg = asian_macro.get("singapore", {})
    
    with col_a1:
        st.markdown(f"**{hk.get('flag', '🇭🇰')} {hk.get('index', 'Hang Seng')}**: `{hk.get('value', '')}` ({hk.get('change', '')})")
        st.caption(f"Sentiment: {hk.get('sentiment', '')}")
        
    with col_a2:
        st.markdown(f"**{jp.get('flag', '🇯🇵')} {jp.get('index', 'Nikkei 225')}**: `{jp.get('value', '')}` ({jp.get('change', '')})")
        st.caption(f"Sentiment: {jp.get('sentiment', '')}")

    with col_a3:
        st.markdown(f"**{sg.get('flag', '🇸🇬')} {sg.get('index', 'GIFT Nifty')}**: `{sg.get('value', '')}` ({sg.get('change', '')})")
        st.caption(f"Sentiment: {sg.get('sentiment', '')}")

st.markdown("---")

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🚀 1-Month Swings",
    "📊 3-Month Positional",
    "⚡ Daily Intraday",
    "🛢️ Commodities & F&O",
    "💰 ₹2L Portfolio Allocator",
    "🚨 Watchlist Risk Radar",
    "🔍 Live Screener"
])

def render_trade_cards(recs, horizon_filter=None):
    if horizon_filter:
        recs = [r for r in recs if r.get("horizon") == horizon_filter]
        
    if not recs:
        st.info("No active trade setups found for this timeframe.")
        return

    for rec in recs:
        with st.container():
            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h3 style="margin:0; color:#38bdf8;">{rec.get('stock_name')} <span style="color:#94a3b8; font-size:1rem;">({rec.get('ticker')})</span></h3>
                        <span class="badge-bullish" style="margin-top:6px; display:inline-block;">{rec.get('sector')} • {rec.get('horizon', '').upper()}</span>
                    </div>
                    <div style="text-align:right;">
                        <div style="color:#64748b; font-size:0.8rem;">Current Market Price (CMP)</div>
                        <div class="metric-value" style="color:#f8fafc;">₹{rec.get('cmp'):,.2f}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**Entry Range**\n`{rec.get('entry_range')}`")
            with col2:
                st.markdown(f"**Target 1 (2-3 Weeks)**\n`₹{rec.get('target_1'):,.2f}` (`{rec.get('target_1_return', '')}`)")
            with col3:
                st.markdown(f"**Target 2 (4-5 Weeks)**\n`₹{rec.get('target_2'):,.2f}` (`{rec.get('target_2_return', '')}`)")
            with col4:
                st.markdown(f"**Hard Stop Loss**\n`₹{rec.get('stop_loss'):,.2f}` (`{rec.get('stop_loss_pct', '')}`)")

            st.markdown(f"**Risk-to-Reward Ratio (RRR)**: `{rec.get('rrr')}` | **Conviction**: `{rec.get('conviction', 'High')}`")
            
            with st.expander("📌 Technical & News Confluence Rationale"):
                tc = rec.get("technical_confluence", {})
                st.markdown(f"- **Candlestick & Patterns**: {', '.join(tc.get('patterns', []))}")
                st.markdown(f"- **RSI (14)**: {tc.get('rsi', 'N/A')} | **Volume Surge**: {tc.get('volume_spike', 'N/A')}")
                
                news = rec.get("news_catalysts", [])
                if news:
                    st.markdown("**Catalysts & News**:")
                    for n in news:
                        st.markdown(f"  - {n}")
            st.markdown("<br>", unsafe_allow_html=True)

with tab1:
    st.subheader("🚀 High-Conviction 1-Month Swing Trade Recommendations")
    render_trade_cards(data.get("recommendations", []), "1_month")

with tab2:
    st.subheader("📊 3-Month Positional Breakout Trades")
    render_trade_cards(data.get("recommendations", []), "3_month")

with tab3:
    st.subheader("⚡ Daily Intraday High-Momentum Setups")
    render_trade_cards(data.get("recommendations", []), "intraday")

with tab4:
    st.subheader("🛢️ Commodity & Index F&O Derivatives")
    commodities = data.get("commodities_and_derivatives", [])
    if commodities:
        for c in commodities:
            st.markdown(f"""
            **{c.get('name')} ({c.get('symbol')})** — `{c.get('type')}`
            - **CMP**: `₹{c.get('cmp')}` | **Target 1**: `₹{c.get('target_1')}` | **SL**: `₹{c.get('stop_loss')}`
            - **Trigger**: {c.get('trigger_condition')}
            """)
            st.divider()

with tab5:
    st.subheader("💰 ₹2,00,000 Portfolio Allocation Calculator")
    alloc = data.get("portfolio_allocation", {})
    st.info(f"**Total Capital**: ₹{alloc.get('total_capital', 200000):,} | **Position Size**: ₹{alloc.get('allocation_per_stock', 40000):,} per stock across 5 stocks")
    
    positions = alloc.get("positions", [])
    if positions:
        df_alloc = pd.DataFrame(positions)
        st.dataframe(
            df_alloc,
            column_config={
                "stock_name": "Stock",
                "allocated_amount": st.column_config.NumberColumn("Allocation (₹)", format="₹%d"),
                "allocated_shares": "Shares",
                "cmp": st.column_config.NumberColumn("CMP (₹)", format="₹%.2f"),
                "stop_loss": st.column_config.NumberColumn("SL (₹)", format="₹%.2f"),
                "max_risk_amount": st.column_config.NumberColumn("Max Risk (₹)", format="₹%d"),
                "risk_pct_of_capital": "Risk of Capital"
            },
            use_container_width=True,
            hide_index=True
        )

with tab6:
    st.subheader("🚨 Watchlist Automated Risk Radar")
    watchlist = data.get("watchlist", [])
    if watchlist:
        for item in watchlist:
            risk_class = "badge-high-risk" if item.get("risk_rating") == "HIGH" else "badge-bullish"
            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4>{item.get('stock_name')} ({item.get('ticker')})</h4>
                    <span class="{risk_class}">RATING: {item.get('risk_rating')}</span>
                </div>
                <p><b>CMP</b>: ₹{item.get('cmp')} | <b>Sector</b>: {item.get('sector')}</p>
                <p style="color:#f87171;">⚠️ <b>Risk Summary</b>: {item.get('risk_summary')}</p>
                <p style="color:#38bdf8;">👉 <b>Action Plan</b>: {item.get('action_plan')}</p>
            </div>
            """, unsafe_allow_html=True)

with tab7:
    st.subheader("🔍 Live NSE Technical Screener")
    st.markdown("Run the live 4-pillar technical screener on top liquid NSE stocks via `yfinance` & `pandas`:")
    
    if st.button("🚀 Run Live Technical Scan"):
        with st.spinner("Downloading 6-month price data & calculating 20/50/200 EMAs, RSI, and Volume breakouts..."):
            try:
                from scanner import run_screener
                results = run_screener()
                if results:
                    st.success(f"✅ Found {len(results)} high-probability candidates!")
                    st.dataframe(pd.DataFrame(results), use_container_width=True)
                else:
                    st.warning("No candidates met all 4-pillar criteria today.")
            except Exception as e:
                st.error(f"Screener Error: {str(e)}")

# Sidebar Footer
st.sidebar.title("🤖 SwingPulse Agent")
st.sidebar.markdown("Built with Google Antigravity & Streamlit.")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Download Reports")

json_str = json.dumps(data, indent=2)
st.sidebar.download_button(
    label="Download latest.json",
    data=json_str,
    file_name="latest.json",
    mime="application/json"
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip**: Deploy this app for free on [Streamlit Cloud](https://streamlit.io/cloud).")
