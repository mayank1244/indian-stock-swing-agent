$tickers = @('TMPV.NS', 'TMCV.NS', 'M&M.NS', 'MARUTI.NS')
foreach ($t in $tickers) {
    try {
        $res = Invoke-RestMethod -Uri "https://query1.finance.yahoo.com/v8/finance/chart/$t`?interval=1d&range=1d" -TimeoutSec 5 -Headers @{ "User-Agent" = "Mozilla/5.0" }
        $p = $res.chart.result[0].meta.regularMarketPrice
        Write-Host "$t : $p" -ForegroundColor Green
    } catch {
        Write-Host "$t : Failed ($($_))" -ForegroundColor Red
    }
}
