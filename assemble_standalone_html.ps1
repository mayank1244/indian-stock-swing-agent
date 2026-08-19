$jsonPath = "web\data\latest.json"
$standalonePath = "web\standalone.html"
$indexPath = "web\index.html"
$otherStandalone = "..\indian-stock-agent\web\standalone.html"
$otherIndex = "..\indian-stock-agent\web\index.html"
$otherData = "..\indian-stock-agent\web\data\latest.json"

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)

# Read latest.json
$jsonText = [System.IO.File]::ReadAllText((Resolve-Path $jsonPath), $utf8NoBom)

# Read HTML up to <script>
$htmlFull = [System.IO.File]::ReadAllText((Resolve-Path $standalonePath), $utf8NoBom)
$scriptTagIdx = $htmlFull.IndexOf("<script>")
if ($scriptTagIdx -lt 0) {
    Write-Host "Could not find <script> tag" -ForegroundColor Red
    exit 1
}

$htmlHeadAndBody = $htmlFull.Substring(0, $scriptTagIdx)

# Update nav bar & horizon bar in HTML Head to reflect Daily/Weekly schedule
$htmlHeadAndBody = $htmlHeadAndBody.Replace(
    '<span class="tag-sub">5 Today</span>',
    '<span class="tag-sub">🔄 Daily Rotation</span>'
)
$htmlHeadAndBody = $htmlHeadAndBody.Replace(
    '<span class="tag-sub">5 Swings</span>',
    '<span class="tag-sub">📅 Weekly Swings</span>'
)
$htmlHeadAndBody = $htmlHeadAndBody.Replace(
    '<span class="tag-sub">5 Positional</span>',
    '<span class="tag-sub">📅 Weekly Positional</span>'
)

$jsLogic = @"
<script>
    const staticData = $jsonText;

    let activeSector = 'ALL';
    let activeTimeframe = 'ALL';
    let activeRiskFilter = 'ALL';
    let activeFOFilter = 'ALL';
    let lastRefreshTime = new Date();

    async function fetchDynamicMarketData(isUserAction = false) {
      const btn = document.getElementById('manualRefreshBtn');
      if (btn) btn.classList.add('spinning');

      try {
        const timestamp = new Date().getTime();
        const response = await fetch('data/latest.json?t=' + timestamp, {
          cache: 'no-store',
          headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
        });

        if (response.ok) {
          const freshData = await response.json();
          if (freshData && freshData.recommendations) {
            staticData.recommendations = freshData.recommendations;
            if (freshData.watchlist) staticData.watchlist = freshData.watchlist;
            if (freshData.stock_fo_setups) staticData.stock_fo_setups = freshData.stock_fo_setups;
            if (freshData.commodities_fo) staticData.commodities_fo = freshData.commodities_fo;
            if (freshData.backtest_3m_ago) staticData.backtest_3m_ago = freshData.backtest_3m_ago;
            if (freshData.date) staticData.date = freshData.date;
            if (freshData.asian_markets_macro) staticData.asian_markets_macro = freshData.asian_markets_macro;
          }
        }
      } catch (err) {
        // Fallback
      } finally {
        lastRefreshTime = new Date();
        updateSyncTimeBadge();
        renderAllViews();
        if (btn) btn.classList.remove('spinning');
        if (isUserAction) showToast("✅ Refreshed live!");
        syncLiveExchangeQuotes();
      }
    }

    async function syncLiveExchangeQuotes() {
      const liveTickers = [
        'SUZLON.NS','TATASTEEL.NS','SBIN.NS','RELIANCE.NS','JSWSTEEL.NS',
        'HDFCBANK.NS','BEL.NS','TATAMOTORS.NS','SUNPHARMA.NS','COALINDIA.NS',
        'ICICIBANK.NS','LT.NS','TATAPOWER.NS','TRENT.NS','BHARTIARTL.NS',
        'RVNL.NS','PAYTM.NS'
      ];

      for (const ticker of liveTickers) {
        try {
          const res = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/` + ticker + `?interval=1d&range=1d`, { cache: 'no-store' });
          if (res.ok) {
            const data = await res.json();
            const price = data.chart?.result?.[0]?.meta?.regularMarketPrice;
            const prev = data.chart?.result?.[0]?.meta?.chartPreviousClose;
            if (price && typeof price === 'number') {
              const chg = prev ? (((price - prev) / prev) * 100).toFixed(2) : 0;
              
              if (staticData.recommendations) {
                staticData.recommendations.forEach(r => {
                  if (r.ticker === ticker) r.cmp = price;
                });
              }
              if (staticData.watchlist) {
                staticData.watchlist.forEach(w => {
                  if (w.ticker === ticker) {
                    w.cmp = price;
                    w.change_1d = (chg >= 0 ? '+' : '') + chg + '%';
                    w.is_positive = chg >= 0;
                  }
                });
              }
              if (staticData.stock_fo_setups) {
                staticData.stock_fo_setups.forEach(f => {
                  if (f.ticker === ticker) f.cmp = price;
                });
              }
            }
          }
        } catch (e) {}
      }
      renderAllViews();
    }

    function updateSyncTimeBadge() {
      const badge = document.getElementById('reportDate');
      if (!badge) return;
      const timeStr = lastRefreshTime.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
      const dateStr = staticData.date || new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
      badge.innerHTML = `🟢 Live Sync: ` + dateStr + `, ` + timeStr;
    }

    function manualRefreshData() {
      fetchDynamicMarketData(true);
    }

    function renderAllViews() {
      const sectors = ['ALL', ...new Set(staticData.recommendations.map(r => r.sector))];
      const sectorContainer = document.getElementById('sectorFilters');
      if (sectorContainer) {
        sectorContainer.innerHTML = sectors.map(sec => `
          <button class="filter-pill ` + (sec === activeSector ? 'active' : '') + `" onclick="setSectorFilter('` + sec + `', this)">
            ` + (sec === 'ALL' ? 'All Sectors' : sec) + `
          </button>
        `).join('');
      }

      filterCards();
      renderStockFO();
      renderWatchlist();
      renderCommoditiesFO();
      renderBacktest();
      recalculatePortfolio();
    }

    function init() {
      renderAllViews();
      updateSyncTimeBadge();
      fetchDynamicMarketData(false);

      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
          fetchDynamicMarketData(false);
        }
      });

      setInterval(() => {
        fetchDynamicMarketData(false);
      }, 60000);
    }

    function switchMainTab(tab, btn) {
      document.querySelectorAll('.nav-tab-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');

      document.getElementById('liveViewSection').style.display = tab === 'live' ? 'block' : 'none';
      document.getElementById('foStockViewSection').style.display = tab === 'stock_fo' ? 'block' : 'none';
      document.getElementById('watchlistViewSection').style.display = tab === 'watchlist' ? 'block' : 'none';
      document.getElementById('commoditiesViewSection').style.display = tab === 'commodities' ? 'block' : 'none';
      document.getElementById('portfolioViewSection').style.display = tab === 'portfolio' ? 'block' : 'none';
      document.getElementById('backtestViewSection').style.display = tab === 'backtest' ? 'block' : 'none';

      if (tab === 'stock_fo') renderStockFO();
      if (tab === 'portfolio') recalculatePortfolio();
      if (tab === 'watchlist') renderWatchlist();
      if (tab === 'backtest') renderBacktest();
    }

    /* STOCK F&O */
    function setFOInstrumentFilter(filterType, btn) {
      activeFOFilter = filterType;
      document.querySelectorAll('#foInstrumentFilters .filter-pill').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      filterStockFO();
    }

    function filterStockFO() {
      const query = (document.getElementById('foSearchInput')?.value || '').toLowerCase();
      const list = staticData.stock_fo_setups || [];
      const filtered = list.filter(item => {
        return item.stock_name.toLowerCase().includes(query) || 
               item.ticker.toLowerCase().includes(query) || 
               item.futures.contract.toLowerCase().includes(query) || 
               item.options_call.contract.toLowerCase().includes(query);
      });

      document.getElementById('foCount').textContent = filtered.length + ` F&O Setups`;
      const feed = document.getElementById('foStockCardsFeed');
      if (!feed) return;

      feed.innerHTML = filtered.map(item => {
        const fut = item.futures;
        const opt = item.options_call;
        const showFut = activeFOFilter === 'ALL' || activeFOFilter === 'FUT';
        const showOpt = activeFOFilter === 'ALL' || activeFOFilter === 'OPT';

        return `
        <article class="fo-stock-card">
          <div class="card-top">
            <div class="stock-identity">
              <h3>
                ` + item.stock_name + `
                <span class="ticker-tag">` + item.ticker.replace('.NS', '') + `</span>
                <span class="fo-badge badge-fut">Lot: ` + item.lot_size + `</span>
                <span class="fo-badge badge-opt">Expiry: ` + item.expiry + `</span>
              </h3>
              <p class="sector-tag">🏢 ` + item.sector + ` • 🛑 Exit Before: <strong>` + item.mandatory_exit_date + `</strong></p>
            </div>
            <div class="cmp-badge">
              <div class="cmp-val">₹` + item.cmp.toFixed(2) + `</div>
              <div class="cmp-label">Cash CMP</div>
            </div>
          </div>

          <div class="fo-dual-container">
            ` + (showFut ? `
            <div class="fo-block fut-block">
              <div class="fo-block-title">
                <span>⚡ STOCK FUTURES (FUT)</span>
                <span class="fo-badge badge-fut">` + fut.contract + `</span>
              </div>
              <div class="fo-rates-grid">
                <div class="fo-rate-row">
                  <span class="fo-r-lbl">Buy Price Zone</span>
                  <span class="fo-r-val" style="color:var(--accent-cyan);">` + fut.buy_range + `</span>
                  <span class="fo-r-sub" style="color:var(--text-muted);">Margin: ` + fut.approx_margin + `</span>
                </div>
                <div class="fo-rate-row">
                  <span class="fo-r-lbl">Stop Loss Rate</span>
                  <span class="fo-r-val danger-text">` + fut.stop_loss_sell + `</span>
                  <span class="fo-r-sub danger-text">` + fut.stop_loss_risk + `</span>
                </div>
                <div class="fo-rate-row">
                  <span class="fo-r-lbl">Target 1 Sell Rate</span>
                  <span class="fo-r-val success-text">` + fut.sell_target_1 + `</span>
                  <span class="fo-r-sub success-text">` + fut.sell_target_1_profit + `</span>
                </div>
                <div class="fo-rate-row">
                  <span class="fo-r-lbl">Target 2 Sell Rate</span>
                  <span class="fo-r-val accent-text">` + fut.sell_target_2 + `</span>
                  <span class="fo-r-sub accent-text">` + fut.sell_target_2_profit + `</span>
                </div>
              </div>
            </div>
            ` : '') + `

            ` + (showOpt ? `
            <div class="fo-block opt-block">
              <div class="fo-block-title">
                <span>📞 CALL OPTION (CE)</span>
                <span class="fo-badge badge-opt">` + opt.contract + `</span>
              </div>
              <div class="fo-rates-grid">
                <div class="fo-rate-row">
                  <span class="fo-r-lbl">Buy Premium Rate</span>
                  <span class="fo-r-val" style="color:var(--accent-purple);">` + opt.buy_rate + `</span>
                  <span class="fo-r-sub" style="color:var(--text-muted);">Capital: ` + opt.premium_required + `</span>
                </div>
                <div class="fo-rate-row">
                  <span class="fo-r-lbl">Stop Loss Rate</span>
                  <span class="fo-r-val danger-text">` + opt.stop_loss_sell + `</span>
                  <span class="fo-r-sub danger-text">` + opt.stop_loss_risk + `</span>
                </div>
                <div class="fo-rate-row">
                  <span class="fo-r-lbl">Target 1 Sell Rate</span>
                  <span class="fo-r-val success-text">` + opt.sell_target_1 + `</span>
                  <span class="fo-r-sub success-text">` + opt.sell_target_1_return + `</span>
                </div>
                <div class="fo-rate-row">
                  <span class="fo-r-lbl">Target 2 Sell Rate</span>
                  <span class="fo-r-val accent-text">` + opt.sell_target_2 + `</span>
                  <span class="fo-r-sub accent-text">` + opt.sell_target_2_return + `</span>
                </div>
              </div>
            </div>
            ` : '') + `
          </div>

          <div class="zero-risk-shield" style="font-size:0.75rem;">
            ` + item.zero_risk_protocol + `
          </div>

          <div class="news-box">
            <span class="news-box-title">📊 Open Interest (OI) & Technical Confluence</span>
            <p class="news-item">• ` + item.derivatives_confluence + `</p>
          </div>

          <div class="card-actions">
            <a href="https://api.whatsapp.com/send?phone=919894360810&text=🎯%20*F%26O%20SETUP:*%20` + encodeURIComponent(item.stock_name) + `%20(` + item.ticker + `)%0AFUT%20Buy:%20` + encodeURIComponent(fut.buy_range) + `%20%7C%20T1:%20` + encodeURIComponent(fut.sell_target_1) + `%20%7C%20SL:%20` + encodeURIComponent(fut.stop_loss_sell) + `%0AOPT%20(` + encodeURIComponent(opt.contract) + `):%20Buy%20` + encodeURIComponent(opt.buy_rate) + `%20%7C%20T1:%20` + encodeURIComponent(opt.sell_target_1) + `%20%7C%20SL:%20` + encodeURIComponent(opt.stop_loss_sell) + `" target="_blank" class="btn-secondary" style="border-color:#25D366; color:#25D366;">
              💬 WhatsApp Alert
            </a>
            <button class="btn-primary" onclick="copyStockFOSetup('` + item.id + `')">
              Copy F&O Rates
            </button>
          </div>
        </article>
        `;
      }).join('');
    }

    function renderStockFO() {
      filterStockFO();
    }

    function copyStockFOSetup(id) {
      const item = (staticData.stock_fo_setups || []).find(s => s.id === id);
      if (!item) return;
      const fut = item.futures;
      const opt = item.options_call;
      const text = `🎯 [NSE F&O TRADE] ` + item.stock_name + ` (` + item.ticker.replace('.NS','') + `) | Lot: ` + item.lot_size + `\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n⚡ FUTURES (` + fut.contract + `):\n• BUY: ` + fut.buy_range + `\n• SELL T1: ` + fut.sell_target_1 + ` (` + fut.sell_target_1_profit + `)\n• SELL T2: ` + fut.sell_target_2 + ` (` + fut.sell_target_2_profit + `)\n• STOP LOSS: ` + fut.stop_loss_sell + ` (` + fut.stop_loss_risk + `)\n\n📞 OPTIONS (` + opt.contract + `):\n• BUY PREMIUM: ` + opt.buy_rate + ` (Capital: ` + opt.premium_required + `)\n• SELL T1: ` + opt.sell_target_1 + ` (` + opt.sell_target_1_return + `)\n• SELL T2: ` + opt.sell_target_2 + ` (` + opt.sell_target_2_return + `)\n• STOP LOSS: ` + opt.stop_loss_sell + ` (` + opt.stop_loss_risk + `)\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🛡️ PROTOCOL: ` + item.zero_risk_protocol;
      navigator.clipboard.writeText(text).then(() => showToast(`Copied ` + item.stock_name + ` F&O rates!`)).catch(() => showToast("Copied!"));
    }

    /* WATCHLIST */
    function setRiskFilter(risk, btn) {
      activeRiskFilter = risk;
      document.querySelectorAll('#riskFilters .filter-pill').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      filterWatchlist();
    }

    function filterWatchlist() {
      const query = (document.getElementById('wlSearchInput')?.value || '').toLowerCase();
      const filtered = staticData.watchlist.filter(item => {
        const matchesRisk = activeRiskFilter === 'ALL' || item.risk_rating === activeRiskFilter;
        const matchesQuery = item.stock_name.toLowerCase().includes(query) || item.ticker.toLowerCase().includes(query) || item.sector.toLowerCase().includes(query) || item.latest_news.toLowerCase().includes(query);
        return matchesRisk && matchesQuery;
      });

      document.getElementById('wlCount').textContent = filtered.length + ` Stocks Tracked`;
      const feed = document.getElementById('watchlistCardsFeed');
      if (!feed) return;

      feed.innerHTML = filtered.map(item => {
        const isPos = item.is_positive;
        const riskBorderClass = item.risk_rating === 'LOW' ? 'risk-border-low' : (item.risk_rating === 'MODERATE' ? 'risk-border-moderate' : 'risk-border-high');
        const riskBadgeClass = item.risk_rating === 'LOW' ? 'risk-low' : (item.risk_rating === 'MODERATE' ? 'risk-moderate' : 'risk-high');
        const riskBoxClass = item.risk_rating === 'LOW' ? 'low-risk' : (item.risk_rating === 'MODERATE' ? 'mod-risk' : '');

        return `
        <article class="watchlist-card ` + riskBorderClass + `">
          <div class="card-top">
            <div class="stock-identity">
              <h3>
                ` + item.stock_name + `
                <span class="ticker-tag">` + item.ticker.replace('.NS', '') + `</span>
                <span class="risk-badge ` + riskBadgeClass + `">` + item.risk_badge + `</span>
              </h3>
              <p class="sector-tag">🏢 ` + item.sector + ` • Market Cap: ` + item.market_cap + `</p>
            </div>
            <div class="cmp-badge">
              <div class="cmp-val">₹` + item.cmp.toFixed(2) + `</div>
              <div class="cmp-label ` + (isPos ? 'success-text' : 'danger-text') + `" style="font-weight:700;">` + item.change_1d + ` Today</div>
            </div>
          </div>

          <div class="risk-summary-box ` + riskBoxClass + `">
            <strong>⚠️ Risk Profile & Volatility:</strong> ` + item.risk_summary + `
          </div>

          <div class="news-box">
            <span class="news-box-title">📰 Latest Breaking News (Live Sentiment)</span>
            <p class="news-item">• ` + item.latest_news + `</p>
          </div>

          <div class="action-plan-box">
            <p><strong>🎯 Bias:</strong> ` + item.technical_bias + `</p>
            <p style="margin-top:2px;"><strong>💡 Action:</strong> ` + item.action_plan + `</p>
          </div>

          <div class="card-actions">
            <a href="https://api.whatsapp.com/send?phone=919894360810&text=🚨%20RISK%20CHECK:%20` + encodeURIComponent(item.stock_name) + `%20(` + item.ticker + `)%20CMP:%20₹` + item.cmp + `%20Risk:%20` + encodeURIComponent(item.risk_badge) + `" target="_blank" class="btn-secondary" style="border-color:#25D366; color:#25D366;">💬 WhatsApp Alert</a>
            <button class="btn-primary" onclick="copyWatchlistTrade('` + item.id + `')">Copy Stock Pulse</button>
          </div>
        </article>
        `;
      }).join('');
    }

    function renderWatchlist() {
      filterWatchlist();
    }

    function copyWatchlistTrade(id) {
      const item = staticData.watchlist.find(w => w.id === id);
      if (!item) return;
      const text = `👁️ [WATCHLIST PULSE] ` + item.stock_name + ` (` + item.ticker.replace('.NS','') + `)\n• CMP: ₹` + item.cmp + ` (` + item.change_1d + `)\n• RISK: ` + item.risk_badge + `\n• RISK PROFILE: ` + item.risk_summary + `\n• LATEST NEWS: ` + item.latest_news + `\n• ACTION: ` + item.action_plan;
      navigator.clipboard.writeText(text).then(() => showToast(`Copied ` + item.stock_name + ` pulse!`)).catch(() => showToast("Copied!"));
    }

    /* COMMODITIES */
    function renderCommoditiesFO() {
      const feed = document.getElementById('commoditiesCardsFeed');
      if (!feed || !staticData.commodities_fo) return;

      feed.innerHTML = staticData.commodities_fo.map(item => `
        <article class="fo-card">
          <div class="card-top">
            <div class="stock-identity">
              <h3>` + item.instrument + ` <span class="ticker-tag">` + item.category + `</span></h3>
              <p class="sector-tag">🏢 ` + item.exchange + ` • 📜 Broker Code: <strong>` + item.broker_contract + `</strong> • 🎯 RRR ` + item.rrr + `</p>
            </div>
            <div class="cmp-badge"><div class="cmp-val">₹` + item.cmp.toFixed(2) + `</div><div class="cmp-label">CMP</div></div>
          </div>
          <div class="timing-box">📅 <strong>Entry Date:</strong> ` + item.entry_date + ` (` + item.entry_time_window + `)</div>
          <div class="targets-box">
            <div class="target-col sl"><span class="t-lbl">Stop Loss</span><span class="t-val danger-text">` + item.stop_loss + `</span><span class="t-gain red">` + item.stop_loss_pct + `</span></div>
            <div class="target-col entry"><span class="t-lbl">Buy Price</span><span class="t-val" style="font-size:0.75rem;">` + item.buy_price_range + `</span><span class="t-gain" style="color:var(--accent-yellow)">Execution Zone</span></div>
            <div class="target-col t1"><span class="t-lbl">Target 1</span><span class="t-val success-text">` + item.target_1 + `</span><span class="t-gain green">` + item.target_1_gain + `</span></div>
            <div class="target-col t2"><span class="t-lbl">Target 2</span><span class="t-val accent-text">` + item.target_2 + `</span><span class="t-gain cyan">` + item.target_2_gain + `</span></div>
          </div>
          <div class="dates-grid">
            <div class="date-item"><span class="date-lbl">🎯 Target 1 Exit Date</span><strong class="date-val success-text">` + item.target_1_date + `</strong></div>
            <div class="date-item"><span class="date-lbl">🚀 Target 2 Exit Date</span><strong class="date-val accent-text">` + item.target_2_date + `</strong></div>
            <div class="date-item" style="grid-column: span 2;"><span class="date-lbl">🛑 Mandatory Final Exit Date</span><strong class="date-val danger-text">` + item.mandatory_exit_date + `</strong></div>
          </div>
          <div class="zero-risk-shield">` + item.zero_risk_protocol + `</div>
          <div class="news-box"><span class="news-box-title">🌏 Asian Sentiment & Macro Drivers</span><p class="news-item">• ` + item.asian_confluence + `</p></div>
          <div class="card-actions"><button class="btn-primary" style="grid-column: span 2;" onclick="copyFOTrade('` + item.id + `')">Copy MCX India Order Setup</button></div>
        </article>
      `).join('');
    }

    function copyFOTrade(id) {
      const item = staticData.commodities_fo.find(c => c.id === id);
      if (!item) return;
      const text = `🪙 MCX INDIA COMMODITY: ` + item.instrument + `\n• BROKER CODE: ` + item.broker_contract + `\n• ENTRY DATE: ` + item.entry_date + ` (` + item.entry_time_window + `)\n• BUY PRICE: ` + item.buy_price_range + `\n• TARGET 1: ` + item.target_1 + ` (Exit by ` + item.target_1_date + `)\n• TARGET 2: ` + item.target_2 + ` (Exit by ` + item.target_2_date + `)\n• MANDATORY EXIT: ` + item.mandatory_exit_date + `\n• ZERO-RISK SHIELD: ` + item.zero_risk_protocol;
      navigator.clipboard.writeText(text).then(() => showToast(`Copied ` + item.instrument + ` order!`)).catch(() => showToast("Copied!"));
    }

    /* PORTFOLIO PLAN */
    function setCapitalPreset(amount, btn) {
      document.querySelectorAll('.preset-chip').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      document.getElementById('portfolioCapitalInput').value = amount;
      recalculatePortfolio();
    }

    function recalculatePortfolio() {
      const capital = parseFloat(document.getElementById('portfolioCapitalInput').value) || 200000;
      const basketType = document.getElementById('portfolioBasketSelect').value || '1_month';
      const stocks = staticData.recommendations.filter(r => r.horizon === basketType);
      if (stocks.length === 0) return;

      const capitalPerStock = capital / stocks.length;
      let totalDeployed = 0, totalRisk = 0, totalProfitT1 = 0, totalProfitT2 = 0;

      const allocated = stocks.map(s => {
        const shares = Math.max(1, Math.floor(capitalPerStock / s.cmp));
        const deployed = shares * s.cmp;
        const riskAmt = shares * Math.abs(s.cmp - s.stop_loss);
        const profitT1 = shares * (s.target_1 - s.cmp);
        const profitT2 = shares * (s.target_2 - s.cmp);

        totalDeployed += deployed;
        totalRisk += riskAmt;
        totalProfitT1 += profitT1;
        totalProfitT2 += profitT2;

        return { stock: s, shares, deployed, riskAmt, profitT1, profitT2, half: Math.ceil(shares / 2), rem: Math.floor(shares / 2) };
      });

      const cashBuffer = Math.max(0, capital - totalDeployed);
      document.getElementById('portDeployed').textContent = `₹` + totalDeployed.toLocaleString('en-IN', { maximumFractionDigits: 0 });
      document.getElementById('portCashBuffer').textContent = `Cash Buffer: ₹` + cashBuffer.toLocaleString('en-IN', { maximumFractionDigits: 0 });
      document.getElementById('portRisk').textContent = `₹` + totalRisk.toLocaleString('en-IN', { maximumFractionDigits: 0 });
      document.getElementById('portRiskPct').textContent = ((totalRisk/capital)*100).toFixed(1) + `% of Capital`;
      document.getElementById('portProfitT1').textContent = `+₹` + totalProfitT1.toLocaleString('en-IN', { maximumFractionDigits: 0 });
      document.getElementById('portReturnT1').textContent = `+` + ((totalProfitT1/capital)*100).toFixed(1) + `% Portfolio Gain`;
      document.getElementById('portProfitT2').textContent = `+₹` + totalProfitT2.toLocaleString('en-IN', { maximumFractionDigits: 0 });
      document.getElementById('portReturnT2').textContent = `+` + ((totalProfitT2/capital)*100).toFixed(1) + `% Portfolio Gain`;

      document.getElementById('portfolioCardsFeed').innerHTML = allocated.map(item => `
        <article class="portfolio-item-card">
          <div class="port-card-top">
            <div class="stock-identity">
              <h3>` + item.stock.stock_name + ` <span class="ticker-tag">` + item.stock.ticker.replace('.NS', '') + `</span></h3>
              <p class="sector-tag">🏢 ` + item.stock.sector + ` • CMP: ₹` + item.stock.cmp + ` • Entry: ` + item.stock.entry_range + `</p>
            </div>
            <div class="port-shares-badge">🛒 ` + item.shares + ` Shares</div>
          </div>
          <div class="port-details-grid">
            <div class="target-col entry"><span class="t-lbl">Capital Invested</span><span class="t-val">₹` + item.deployed.toLocaleString('en-IN', {maximumFractionDigits:0}) + `</span></div>
            <div class="target-col sl"><span class="t-lbl">Max Risk (SL ₹` + item.stock.stop_loss + `)</span><span class="t-val danger-text">-₹` + item.riskAmt.toLocaleString('en-IN', {maximumFractionDigits:0}) + `</span></div>
            <div class="target-col t1"><span class="t-lbl">Target 1 (₹` + item.stock.target_1 + `)</span><span class="t-val success-text">+₹` + item.profitT1.toLocaleString('en-IN', {maximumFractionDigits:0}) + `</span></div>
            <div class="target-col t2"><span class="t-lbl">Target 2 (₹` + item.stock.target_2 + `)</span><span class="t-val accent-text">+₹` + item.profitT2.toLocaleString('en-IN', {maximumFractionDigits:0}) + `</span></div>
          </div>
          <div class="verdict-box">
            <strong>🎯 Execution Plan:</strong> Buy <strong>` + item.shares + ` shares</strong> in range ` + item.stock.entry_range + `. Sell <strong>` + item.half + ` shares</strong> at Target 1 (₹` + item.stock.target_1 + `) and trail SL to Entry. Sell remaining <strong>` + item.rem + ` shares</strong> at Target 2 (₹` + item.stock.target_2 + `).
          </div>
        </article>
      `).join('');
    }

    function shareBasketToWhatsApp() {
      const capital = parseFloat(document.getElementById('portfolioCapitalInput').value) || 200000;
      const basketType = document.getElementById('portfolioBasketSelect').value || '1_month';
      const stocks = staticData.recommendations.filter(r => r.horizon === basketType);
      const capitalPerStock = capital / stocks.length;

      let text = `💼 *SWINGPULSE 5-SHARE PLAN (Capital: ₹` + capital.toLocaleString('en-IN') + `)*\n`;
      text += `━━━━━━━━━━━━━━━━━━━━━\n`;
      stocks.forEach((s, idx) => {
        const shares = Math.max(1, Math.floor(capitalPerStock / s.cmp));
        text += (idx+1) + `. *` + s.stock_name + `* (` + s.ticker.replace('.NS', '') + `)\n   • BUY: ` + shares + ` shares @ CMP ₹` + s.cmp + `\n   • SL: ₹` + s.stop_loss + ` | T1: ₹` + s.target_1 + ` | T2: ₹` + s.target_2 + `\n`;
      });
      text += `━━━━━━━━━━━━━━━━━━━━━\n`;
      text += `✅ Max Risk Capped at 4.6% | 50% Profit Booking Rule`;

      const url = `https://api.whatsapp.com/send?phone=919894360810&text=` + encodeURIComponent(text);
      window.open(url, '_blank');
    }

    function copyOrderBasket() {
      const capital = parseFloat(document.getElementById('portfolioCapitalInput').value) || 200000;
      const basketType = document.getElementById('portfolioBasketSelect').value || '1_month';
      const stocks = staticData.recommendations.filter(r => r.horizon === basketType);
      const capitalPerStock = capital / stocks.length;

      let text = `💼 SWINGPULSE 5-STOCK BASKET (Capital: ₹` + capital.toLocaleString('en-IN') + `)\n`;
      text += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
      stocks.forEach(s => {
        const shares = Math.max(1, Math.floor(capitalPerStock / s.cmp));
        text += `• ` + s.ticker.replace('.NS', '') + `: BUY ` + shares + ` Qty @ CMP ₹` + s.cmp + ` | SL: ₹` + s.stop_loss + ` | T1: ₹` + s.target_1 + ` | T2: ₹` + s.target_2 + `\n`;
      });
      text += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
      text += `Total Invested: ₹` + (capital * 0.99).toLocaleString('en-IN', {maximumFractionDigits:0}) + ` | 50/50 Profit Booking`;

      navigator.clipboard.writeText(text).then(() => showToast("Copied Order Basket!")).catch(() => showToast("Copied!"));
    }

    /* EQUITIES */
    function setTimeframeFilter(tf, btn) {
      activeTimeframe = tf;
      document.querySelectorAll('.horizon-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');

      const headingText = document.getElementById('sectionHeadingText');
      if (headingText) {
        if (tf === 'intraday') headingText.textContent = '⚡ High-Probability Intraday Setups (Daily Rotation)';
        else if (tf === '1_month') headingText.textContent = '⚡ 1-Month Stock Swings (Weekly Cycle)';
        else if (tf === '3_month') headingText.textContent = '🚀 3-Month Positional Swings (Weekly Cycle)';
        else headingText.textContent = '🔥 High-Conviction Stock Setups (Intraday + Swings)';
      }
      filterCards();
    }

    function setSectorFilter(sec, btn) {
      activeSector = sec;
      document.querySelectorAll('.filter-pill').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      filterCards();
    }

    function filterCards() {
      const q = (document.getElementById('searchInput').value || '').toLowerCase();
      const filtered = staticData.recommendations.filter(r => {
        const mTf = activeTimeframe === 'ALL' || r.horizon === activeTimeframe;
        const mSec = activeSector === 'ALL' || r.sector === activeSector;
        const mQ = r.stock_name.toLowerCase().includes(q) || r.ticker.toLowerCase().includes(q);
        return mTf && mSec && mQ;
      });

      document.getElementById('tradeCount').textContent = filtered.length + ` Setups`;
      document.getElementById('cardsFeed').innerHTML = filtered.map(item => {
        const isIntra = item.horizon === 'intraday';
        const is3M = item.horizon === '3_month';
        const cardClass = isIntra ? 'trade-card horizon-intraday' : (is3M ? 'trade-card horizon-3m' : 'trade-card horizon-1m');
        const pillClass = isIntra ? 'horizon-pill pill-intraday' : (is3M ? 'horizon-pill pill-3m' : 'horizon-pill pill-1m');
        const pillText = isIntra ? '⚡ Daily Intraday' : (is3M ? '🚀 Weekly 3-Month' : '⚡ Weekly 1-Month');

        return `
        <article class="` + cardClass + `">
          <div class="card-top">
            <div class="stock-identity">
              <h3>
                ` + item.stock_name + `
                <span class="ticker-tag">` + item.ticker.replace('.NS', '') + `</span>
                <span class="` + pillClass + `">` + pillText + `</span>
              </h3>
              <p class="sector-tag">🏢 ` + item.sector + ` • ⏱️ ` + item.timeframe + ` • 🎯 RRR ` + item.rrr + `</p>
            </div>
            <div class="cmp-badge">
              <div class="cmp-val">₹` + item.cmp.toFixed(2) + `</div>
              <div class="cmp-label">CMP</div>
            </div>
          </div>

          <div class="targets-box">
            <div class="target-col sl"><span class="t-lbl">Stop Loss</span><span class="t-val">₹` + item.stop_loss + `</span><span class="t-gain red">` + item.stop_loss_pct + `</span></div>
            <div class="target-col entry"><span class="t-lbl">Entry Range</span><span class="t-val" style="font-size:0.75rem;">` + item.entry_range + `</span><span class="t-gain" style="color:var(--text-muted)">Ideal Buy</span></div>
            <div class="target-col t1"><span class="t-lbl">Target 1</span><span class="t-val">₹` + item.target_1 + `</span><span class="t-gain green">` + item.target_1_return + `</span></div>
            <div class="target-col t2"><span class="t-lbl">Target 2</span><span class="t-val">₹` + item.target_2 + `</span><span class="t-gain cyan">` + item.target_2_return + `</span></div>
          </div>

          <div class="patterns-list">
            ` + item.technical_confluence.patterns.map(p => `<span class="pattern-badge ` + (isIntra ? 'pattern-intra' : (is3M ? 'pattern-weekly' : '')) + `">🕯️ ` + p + `</span>`).join('') + `
            <span class="indicator-badge">📊 RSI: ` + item.technical_confluence.rsi + `</span>
            <span class="indicator-badge">⚡ ` + item.technical_confluence.volume_spike + `</span>
          </div>

          <div class="news-box">
            <span class="news-box-title">📰 Key Catalysts & Drivers</span>
            ` + item.news_catalysts.map(n => `<p class="news-item">• ` + n + `</p>`).join('') + `
          </div>

          <div class="card-actions">
            <a href="https://in.tradingview.com/chart/?symbol=NSE:` + item.ticker.replace('.NS', '') + `" target="_blank" rel="noopener" class="btn-secondary">Live Chart</a>
            <button class="btn-primary" onclick="copyTrade('` + item.id + `')">Copy Setup</button>
          </div>
        </article>
      `}).join('');
    }

    /* SCORECARD (BACKTEST REALITY) */
    function renderBacktest() {
      const feed = document.getElementById('backtestCardsFeed');
      if (!feed || !staticData.backtest_3m_ago) return;

      const bt = staticData.backtest_3m_ago;
      const winRateEl = document.getElementById('btWinRate');
      if (winRateEl && bt.win_rate) winRateEl.textContent = bt.win_rate;

      feed.innerHTML = bt.setups.map(item => {
        const r = item.reality;
        let cardClass = 'reality-card ' + (r.status === 'TARGET_2_HIT' ? 'hit-t2' : (r.status === 'TARGET_1_HIT' ? 'hit-t1' : 'stopped-out'));
        let statusClass = r.status === 'TARGET_2_HIT' ? 'status-hit-t2' : (r.status === 'TARGET_1_HIT' ? 'status-hit-t1' : 'status-sl');
        const isPos = !r.actual_return.startsWith('-');

        return `
        <article class="` + cardClass + `">
          <div class="card-top">
            <div class="stock-identity">
              <h3>` + item.stock_name + ` <span class="ticker-tag">` + item.ticker.replace('.NS', '') + `</span> <span class="reality-status-badge ` + statusClass + `">` + r.status_badge + `</span></h3>
              <p class="sector-tag">🏢 ` + item.sector + ` • 📅 Entry: ` + item.signal_date + ` • ⏱️ ` + r.days_taken + ` Days</p>
            </div>
            <div class="cmp-badge"><div class="cmp-val ` + (isPos ? 'success-text' : 'danger-text') + `">` + r.actual_return + `</div><div class="cmp-label">Realized Return</div></div>
          </div>
          <div class="reality-comparison-grid">
            <div class="proj-col"><span class="col-header">📌 Projected 3M Ago</span><div class="detail-line"><span>Entry:</span> <strong>₹` + item.entry_price + `</strong></div><div class="detail-line"><span>Target 1:</span> <strong class="success-text">₹` + item.projected_t1 + ` (` + item.projected_t1_gain + `)</strong></div><div class="detail-line"><span>Target 2:</span> <strong class="accent-text">₹` + item.projected_t2 + ` (` + item.projected_t2_gain + `)</strong></div><div class="detail-line"><span>Stop Loss:</span> <strong class="danger-text">₹` + item.projected_sl + ` (` + item.projected_sl_risk + `)</strong></div></div>
            <div class="real-col"><span class="col-header">🎯 Actual Reality (Today)</span><div class="detail-line"><span>Current Price:</span> <strong>₹` + r.cmp_today + `</strong></div><div class="detail-line"><span>Peak Price:</span> <strong>₹` + r.peak_price + `</strong></div><div class="detail-line"><span>Holding Days:</span> <strong>` + r.days_taken + ` Days</strong></div><div class="detail-line"><span>Outcome:</span> <strong class="` + (isPos ? 'success-text' : 'danger-text') + `">` + (isPos ? 'Profit Taken' : 'SL Triggered') + `</strong></div></div>
          </div>
          <div class="verdict-box"><strong>💡 Verdict:</strong> ` + r.verdict + `</div>
          <div class="card-actions"><a href="https://in.tradingview.com/chart/?symbol=NSE:` + item.ticker.replace('.NS', '') + `" target="_blank" rel="noopener" class="btn-secondary" style="grid-column: span 2;">View Chart on TradingView</a></div>
        </article>
        `;
      }).join('');
    }

    function copyTrade(id) {
      const stock = staticData.recommendations.find(r => r.id === id);
      if (!stock) return;
      const tag = stock.horizon === 'intraday' ? 'INTRADAY SCALP' : (stock.horizon === '3_month' ? '3-MONTH POSITIONAL' : '1-MONTH SWING');
      const text = `🎯 [` + tag + `] SIGNAL: ` + stock.stock_name + ` (` + stock.ticker.replace('.NS', '') + `)\nCMP: ₹` + stock.cmp + ` | Entry: ` + stock.entry_range + `\nTarget 1: ₹` + stock.target_1 + ` (` + stock.target_1_return + `) | Target 2: ₹` + stock.target_2 + ` (` + stock.target_2_return + `)\nStop Loss: ₹` + stock.stop_loss + ` (` + stock.stop_loss_pct + `)\nSetup: ` + stock.technical_confluence.patterns.join(', ');
      navigator.clipboard.writeText(text).then(() => showToast(`Copied ` + stock.stock_name + ` setup!`)).catch(() => showToast("Copied!"));
    }

    function showToast(msg) {
      const t = document.getElementById('toast');
      t.textContent = msg;
      t.classList.add('show');
      setTimeout(() => t.classList.remove('show'), 2500);
    }

    window.onload = init;
</script>
</body>
</html>
"@

$completeHtml = $htmlHeadAndBody + $jsLogic

[System.IO.File]::WriteAllText((Resolve-Path $standalonePath), $completeHtml, $utf8NoBom)
[System.IO.File]::WriteAllText((Resolve-Path $indexPath), $completeHtml, $utf8NoBom)

if (Test-Path "..\indian-stock-agent\web") {
    [System.IO.File]::WriteAllText((Resolve-Path $otherStandalone), $completeHtml, $utf8NoBom)
    [System.IO.File]::WriteAllText((Resolve-Path $otherIndex), $completeHtml, $utf8NoBom)
    [System.IO.File]::WriteAllText((Resolve-Path $otherData), $jsonText, $utf8NoBom)
}

Write-Host "Assembled standalone.html, index.html & synced all targets successfully!" -ForegroundColor Green
