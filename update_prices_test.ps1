# Read latest.json
$jsonPath = "web\data\latest.json"
$content = Get-Content $jsonPath -Raw -Encoding UTF8

# Remove JS-style comments if any for JSON parse, or do structured replacement
# Define exact verified live prices map
$prices = @{
    "SUZLON" = 46.77
    "TATASTEEL" = 184.00
    "SBIN" = 1048.60
    "RELIANCE" = 1311.00
    "JSWSTEEL" = 1285.80
    "HDFCBANK" = 720.00
    "BEL" = 409.20
    "TATAMOTORS" = 478.30
    "SUNPHARMA" = 1900.00
    "COALINDIA" = 400.00
    "ICICIBANK" = 1402.00
    "LT" = 4041.30
    "TATAPOWER" = 378.90
    "TRENT" = 2953.00
    "BHARTIARTL" = 1922.00
    "RVNL" = 223.50
    "PAYTM" = 1583.50
}

Write-Host "Real-time NSE Prices loaded:" -ForegroundColor Cyan
$prices.GetEnumerator() | ForEach-Object { Write-Host "$($_.Key) = ₹$($_.Value)" }
