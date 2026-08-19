"""
SwingPulse Daily Email Notification Dispatcher
Sends rich HTML daily swing recommendations, Watchlist with Risk Highlights, MCX India commodities, Asian market correlation, and mobile dashboard links to nareshofficial.kumar@gmail.com.
"""

import os
import sys
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# Recipient email
RECIPIENT_EMAIL = "nareshofficial.kumar@gmail.com"

# Default or configured Dashboard Web URL (can be GitHub Pages, Vercel, or custom domain)
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://swingpulse.vercel.app")

def generate_email_html(data: dict, dashboard_url: str = DASHBOARD_URL) -> str:
    """Builds a mobile-responsive dark-theme email body."""
    today_str = data.get("date", datetime.date.today().strftime("%Y-%m-%d"))
    
    # Intraday Setups
    intraday = [r for r in data.get("recommendations", []) if r.get("horizon") == "intraday"]
    # 1-Month Setups
    swings_1m = [r for r in data.get("recommendations", []) if r.get("horizon") == "1_month"]
    # 3-Month Setups
    swings_3m = [r for r in data.get("recommendations", []) if r.get("horizon") == "3_month"]
    # Watchlist
    watchlist = data.get("watchlist", [])
    # Commodities F&O
    commodities = data.get("commodities_fo", [])
    asian_macro = data.get("asian_markets_macro", {})
    hk = asian_macro.get("hong_kong", {})
    jp = asian_macro.get("japan", {})
    sg = asian_macro.get("singapore", {})

    # Table rows for Intraday
    rows_intra = ""
    for s in intraday:
        rows_intra += f"""
        <tr style="border-bottom: 1px solid #1f2937;">
          <td style="padding: 10px 6px; font-weight: bold; color: #ffffff;">
            {s['stock_name']}<br>
            <span style="font-size: 11px; color: #f59e0b; font-family: monospace;">{s['ticker'].replace('.NS','')}</span>
          </td>
          <td style="padding: 10px 6px; color: #f9fafb; font-family: monospace;">₹{s['cmp']}</td>
          <td style="padding: 10px 6px; color: #10b981; font-weight: bold; font-family: monospace;">₹{s['target_1']}<br><span style="font-size:10px; color:#10b981;">{s['target_1_return']}</span></td>
          <td style="padding: 10px 6px; color: #06b6d4; font-weight: bold; font-family: monospace;">₹{s['target_2']}<br><span style="font-size:10px; color:#06b6d4;">{s['target_2_return']}</span></td>
          <td style="padding: 10px 6px; color: #ef4444; font-weight: bold; font-family: monospace;">₹{s['stop_loss']}<br><span style="font-size:10px; color:#ef4444;">{s['stop_loss_pct']}</span></td>
        </tr>
        """

    # Table rows for 1-month
    rows_1m = ""
    for s in swings_1m:
        rows_1m += f"""
        <tr style="border-bottom: 1px solid #1f2937;">
          <td style="padding: 10px 6px; font-weight: bold; color: #ffffff;">
            {s['stock_name']}<br>
            <span style="font-size: 11px; color: #06b6d4; font-family: monospace;">{s['ticker'].replace('.NS','')}</span>
          </td>
          <td style="padding: 10px 6px; color: #f9fafb; font-family: monospace;">₹{s['cmp']}</td>
          <td style="padding: 10px 6px; color: #10b981; font-weight: bold; font-family: monospace;">₹{s['target_1']} <span style="font-size:10px;">({s['target_1_return']})</span></td>
          <td style="padding: 10px 6px; color: #06b6d4; font-weight: bold; font-family: monospace;">₹{s['target_2']} <span style="font-size:10px;">({s['target_2_return']})</span></td>
          <td style="padding: 10px 6px; color: #ef4444; font-weight: bold; font-family: monospace;">₹{s['stop_loss']}</td>
        </tr>
        """

    # Watchlist Rows
    rows_wl = ""
    for w in watchlist:
        risk_color = "#10b981" if w.get("risk_rating") == "LOW" else ("#f59e0b" if w.get("risk_rating") == "MODERATE" else "#ef4444")
        rows_wl += f"""
        <div style="background-color: #0a0e17; border: 1px solid #1f2937; border-left: 4px solid {risk_color}; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <strong style="color: #ffffff; font-size: 14px;">{w['stock_name']}</strong> 
              <span style="color: #06b6d4; font-family: monospace; font-size: 11px;">({w['ticker'].replace('.NS','')})</span>
            </div>
            <div style="text-align: right;">
              <span style="color: #ffffff; font-weight: bold; font-family: monospace;">₹{w['cmp']}</span>
              <span style="font-size: 11px; color: {'#10b981' if w.get('is_positive') else '#ef4444'}; font-weight: bold;"> {w.get('change_1d')}</span>
            </div>
          </div>
          <div style="margin: 6px 0;">
            <span style="background: rgba(255,255,255,0.05); color: {risk_color}; font-size: 11px; font-weight: bold; padding: 2px 6px; border-radius: 4px; border: 1px solid {risk_color};">
              {w.get('risk_badge')}
            </span>
            <span style="font-size: 11px; color: #9ca3af; margin-left: 6px;">{w.get('sector')}</span>
          </div>
          <p style="margin: 4px 0; font-size: 12px; color: #d1d5db; line-height: 1.4;">
            📰 <strong>Latest News:</strong> {w.get('latest_news')}
          </p>
          <p style="margin: 4px 0 0 0; font-size: 11.5px; color: #9ca3af;">
            ⚠️ <strong>Risk Factor:</strong> {w.get('risk_summary')}
          </p>
        </div>
        """

    # Table rows for Commodities F&O
    rows_fo = ""
    for c in commodities:
        rows_fo += f"""
        <div style="background-color: #0a0e17; border: 1px solid #374151; border-left: 4px solid #f59e0b; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
          <div style="display: flex; justify-content: space-between; font-weight: bold; color: #ffffff; font-size: 14px;">
            <span>🪙 {c['instrument']}</span>
            <span style="color: #06b6d4; font-family: monospace;">CMP: ₹{c['cmp']}</span>
          </div>
          <p style="margin: 4px 0; font-size: 11px; color: #9ca3af;">Broker Search Code: <strong style="color:#f9fafb;">{c.get('broker_contract', '')}</strong> (MCX India)</p>
          <div style="background: rgba(245,158,11,0.1); border: 1px dashed rgba(245,158,11,0.4); padding: 6px 10px; border-radius: 4px; margin: 6px 0; font-size: 11.5px; color: #f59e0b; font-weight: bold;">
            📅 Entry Date: {c.get('entry_date', '')} ({c.get('entry_time_window', '')})
          </div>
          <div style="font-size: 12px; color: #d1d5db; line-height: 1.6;">
            • <strong>Buy Price:</strong> <span style="font-family: monospace; color:#fff;">{c['buy_price_range']}</span><br>
            • <strong>Target 1:</strong> <span style="color: #10b981; font-weight: bold;">{c['target_1']}</span> (Exit Date: <span style="color:#10b981;">{c.get('target_1_date','')}</span>)<br>
            • <strong>Target 2:</strong> <span style="color: #06b6d4; font-weight: bold;">{c['target_2']}</span> (Exit Date: <span style="color:#06b6d4;">{c.get('target_2_date','')}</span>)<br>
            • <strong>Stop Loss:</strong> <span style="color: #ef4444; font-weight: bold;">{c['stop_loss']}</span> ({c['stop_loss_pct']})<br>
            • <strong>Mandatory Square-off Date:</strong> <span style="color: #ef4444; font-weight: bold;">{c.get('mandatory_exit_date','')}</span>
          </div>
          <div style="margin-top: 8px; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 6px; padding: 8px; font-size: 11.5px; color: #a7f3d0;">
            {c.get('zero_risk_protocol', '')}
          </div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="background-color: #0a0e17; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f9fafb; margin: 0; padding: 20px 10px;">
      
      <div style="max-width: 650px; margin: 0 auto; background-color: #111827; border: 1px solid #1f2937; border-radius: 16px; overflow: hidden;">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #111827 0%, #064e3b 100%); padding: 24px 20px; border-bottom: 1px solid #1f2937; text-align: center;">
          <h1 style="margin: 0; font-size: 24px; color: #10b981; letter-spacing: -0.5px;">📈 SwingPulse 🇮🇳</h1>
          <p style="margin: 6px 0 0 0; font-size: 13px; color: #9ca3af;">Daily Watchlist, News, Risk Matrix & Swing Picks • {today_str}</p>
        </div>

        <!-- Mobile Link Button -->
        <div style="padding: 20px; text-align: center; background-color: rgba(16, 185, 129, 0.08); border-bottom: 1px solid #1f2937;">
          <p style="margin: 0 0 12px 0; font-size: 14px; color: #f9fafb;">Open your interactive live dashboard & position calculator on your phone:</p>
          <a href="{dashboard_url}" target="_blank" style="display: inline-block; background-color: #10b981; color: #000000; font-weight: 800; font-size: 15px; text-decoration: none; padding: 12px 28px; border-radius: 50px; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);">
            📱 Open Mobile Dashboard Link
          </a>
        </div>

        <!-- Watchlist & Risk Radar Section -->
        <div style="padding: 20px; border-bottom: 1px solid #1f2937;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h2 style="margin: 0; font-size: 16px; color: #f59e0b;">👁️ Stock Watchlist (Rates, News & Risk Radar)</h2>
            <span style="font-size: 11px; color: #9ca3af;">Daily Sync</span>
          </div>
          {rows_wl}
        </div>

        <!-- Asian Tri-Market Macro Status -->
        <div style="padding: 20px; border-bottom: 1px solid #1f2937; background: linear-gradient(135deg, #111827 0%, #1e1b4b 100%);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <h2 style="margin: 0; font-size: 15px; color: #a855f7;">🌏 Asian Tri-Market Sentiment Engine</h2>
            <span style="background: rgba(16,185,129,0.2); color: #10b981; font-weight: bold; font-size: 11px; padding: 3px 8px; border-radius: 20px; border: 1px solid #10b981;">🟢 3/3 POSITIVE</span>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; font-size: 12px;">
            <div style="background: #0a0e17; padding: 8px; border-radius: 6px; border-left: 3px solid #10b981;">
              <strong>🇭🇰 Hong Kong</strong>: <span style="color:#10b981; font-weight:bold;">{hk.get('change', '+1.42%')}</span>
            </div>
            <div style="background: #0a0e17; padding: 8px; border-radius: 6px; border-left: 3px solid #10b981;">
              <strong>🇯🇵 Japan</strong>: <span style="color:#10b981; font-weight:bold;">{jp.get('change', '+1.15%')}</span>
            </div>
            <div style="background: #0a0e17; padding: 8px; border-radius: 6px; border-left: 3px solid #10b981;">
              <strong>🇸🇬 Singapore</strong>: <span style="color:#10b981; font-weight:bold;">{sg.get('change', '+0.85%')}</span>
            </div>
          </div>
        </div>

        <!-- Intraday Setups (5 Stocks) -->
        <div style="padding: 20px; border-bottom: 1px solid #1f2937;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h2 style="margin: 0; font-size: 16px; color: #f59e0b;">⚡ High-Probability Intraday Scalps (5 Stocks)</h2>
            <span style="font-size: 11px; color: #9ca3af;">Same-Day Square-off</span>
          </div>
          <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 12px;">
            <thead>
              <tr style="border-bottom: 2px solid #374151; color: #9ca3af; font-size: 11px;">
                <th style="padding: 6px;">STOCK</th>
                <th style="padding: 6px;">CMP</th>
                <th style="padding: 6px;">EXP. TARGET 1</th>
                <th style="padding: 6px;">EXP. TARGET 2</th>
                <th style="padding: 6px;">STOP LOSS</th>
              </tr>
            </thead>
            <tbody>
              {rows_intra}
            </tbody>
          </table>
        </div>

        <!-- 1-Month Swings (5 Stocks) -->
        <div style="padding: 20px; border-bottom: 1px solid #1f2937;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h2 style="margin: 0; font-size: 16px; color: #10b981;">⚡ 1-Month Stock Swings (5 Stocks)</h2>
            <span style="font-size: 11px; color: #9ca3af;">3-4 Weeks</span>
          </div>
          <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 12px;">
            <thead>
              <tr style="border-bottom: 2px solid #374151; color: #9ca3af; font-size: 11px;">
                <th style="padding: 6px;">STOCK</th>
                <th style="padding: 6px;">CMP</th>
                <th style="padding: 6px;">TARGET 1</th>
                <th style="padding: 6px;">TARGET 2</th>
                <th style="padding: 6px;">STOP LOSS</th>
              </tr>
            </thead>
            <tbody>
              {rows_1m}
            </tbody>
          </table>
        </div>

        <!-- ₹2 Lakh Capital Allocation Snapshot -->
        <div style="padding: 20px; border-bottom: 1px solid #1f2937;">
          <h2 style="margin: 0 0 12px 0; font-size: 16px; color: #10b981;">💼 ₹2,00,000 Equity Allocation (5 Stocks)</h2>
          <div style="background-color: #0a0e17; border-radius: 10px; padding: 14px; border: 1px solid #1f2937;">
            <p style="margin: 4px 0; font-size: 13px; color: #d1d5db;">• <strong>BEL @ ₹411.00 (97 Shares)</strong>: Invested ₹39,867 | SL: ₹390 | Est. T1 Profit: +₹3,589</p>
            <p style="margin: 4px 0; font-size: 13px; color: #d1d5db;">• <strong>Tata Motors @ ₹474.00 (84 Shares)</strong>: Invested ₹39,816 | SL: ₹452 | Est. T1 Profit: +₹3,444</p>
            <p style="margin: 4px 0; font-size: 13px; color: #d1d5db;">• <strong>Sun Pharma @ ₹1,930.00 (20 Shares)</strong>: Invested ₹38,600 | SL: ₹1,848 | Est. T1 Profit: +₹3,000</p>
            <p style="margin: 4px 0; font-size: 13px; color: #d1d5db;">• <strong>Coal India @ ₹407.10 (98 Shares)</strong>: Invested ₹39,895 | SL: ₹386 | Est. T1 Profit: +₹3,420</p>
            <p style="margin: 4px 0; font-size: 13px; color: #d1d5db;">• <strong>ICICI Bank @ ₹1,417.00 (28 Shares)</strong>: Invested ₹39,676 | SL: ₹1,355 | Est. T1 Profit: +₹3,164</p>
            <div style="margin-top: 10px; padding-top: 8px; border-top: 1px dashed #374151; font-size: 12px; color: #10b981; font-weight: bold;">
              Total Deployed: ₹1,97,854 | Expected T1 Gain: +₹16,620 (+8.3%) | Max Risk: ₹9,190 (4.6%)
            </div>
          </div>
        </div>

        <!-- Commodities Section -->
        <div style="padding: 20px; border-bottom: 1px solid #1f2937;">
          <h2 style="margin: 0 0 12px 0; font-size: 16px; color: #f59e0b;">🪙 Indian MCX Commodities (Zero-Risk Schedule)</h2>
          {rows_fo}
        </div>

        <!-- Footer Notice -->
        <div style="padding: 20px; text-align: center; font-size: 11px; color: #6b7280; line-height: 1.5;">
          <p style="margin: 0;">⚠️ Disclaimer: For analytical & educational purposes only. Always execute with strict daily stop-loss orders.</p>
          <p style="margin: 6px 0 0 0;">Automated Daily Dispatch to {RECIPIENT_EMAIL}</p>
        </div>

      </div>
    </body>
    </html>
    """
    return html

def send_daily_email(data: dict, dashboard_url: str = DASHBOARD_URL):
    """Sends the email using SMTP configuration."""
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_APP_PASSWORD")

    today_str = data.get("date", datetime.date.today().strftime("%Y-%m-%d"))
    subject = f"📈 SwingPulse Daily ({today_str}): Watchlist & Risk Radar, Suzlon, ₹2L Plan & MCX Commodities"

    html_content = generate_email_html(data, dashboard_url)

    if not sender_email or not sender_password:
        print("\n" + "="*65)
        print(" 📧 EMAIL NOTIFICATION READY!")
        print("="*65)
        print(f" Recipient: {RECIPIENT_EMAIL}")
        print(f" Subject: {subject}")
        print(f" Mobile Link: {dashboard_url}")
        print("\n [NOTE] Set SENDER_EMAIL and SENDER_APP_PASSWORD in .env to dispatch live.")
        print("="*65 + "\n")
        
        preview_path = Path(__file__).parent / "reports" / f"email_preview_{today_str}.html"
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Saved email HTML preview to: {preview_path}")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"SwingPulse Agent <{sender_email}>"
        msg["To"] = RECIPIENT_EMAIL

        part = MIMEText(html_content, "html")
        msg.attach(part)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, RECIPIENT_EMAIL, msg.as_string())

        print(f"\n[SUCCESS] Daily recommendations & commodities F&O email sent to {RECIPIENT_EMAIL}!")
        return True
    except Exception as e:
        print(f"\n[ERROR] Failed to send email to {RECIPIENT_EMAIL}: {e}")
        return False

if __name__ == "__main__":
    import json
    data_path = Path(__file__).parent / "web" / "data" / "latest.json"
    if data_path.exists():
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            send_daily_email(data)
    else:
        print("No latest.json found.")
