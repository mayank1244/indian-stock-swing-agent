$tickers = @(
    'SUZLON.NS',
    'TATASTEEL.NS',
    'SBIN.NS',
    'RELIANCE.NS',
    'JSWSTEEL.NS',
    'HDFCBANK.NS',
    'BEL.NS',
    'TATAMOTORS.NS',
    'SUNPHARMA.NS',
    'COALINDIA.NS',
    'ICICIBANK.NS',
    'LT.NS',
    'TATAPOWER.NS',
    'TRENT.NS',
    'BHARTIARTL.NS',
    'RVNL.NS',
    'PAYTM.NS'
)

$results = @{}

foreach ($ticker in $tickers) {
    try {
        $uri = "https://query1.finance.yahoo.com/v8/finance/chart/$ticker`?interval=1d&range=1d"
        $res = Invoke-RestMethod -Uri $uri -TimeoutSec 6 -Headers @{ "User-Agent" = "Mozilla/5.0" }
        $price = $res.chart.result[0].meta.regularMarketPrice
        $prev = $res.chart.result[0].meta.chartPreviousClose
        $changePct = [Math]::Round((($price - $prev) / $prev) * 100, 2)
        $results[$ticker] = @{
            "price" = $price
            "change" = $changePct
        }
        Write-Host "$ticker : Current = ₹$price ($changePct%)" -ForegroundColor Green
    } catch {
        Write-Host "$ticker : Failed to fetch ($($_))" -ForegroundColor Red
    }
}

$results | ConvertTo-Json | Set-Content -Path "live_quotes.json" -Encoding UTF8
