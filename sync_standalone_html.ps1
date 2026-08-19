$standalonePath = "web\standalone.html"
$jsonPath = "web\data\latest.json"

$jsonRaw = Get-Content $jsonPath -Raw -Encoding UTF8
$htmlContent = Get-Content $standalonePath -Raw -Encoding UTF8

# Replace staticData inside standalone.html with the fresh calibrated JSON
# We find const staticData = { ... }; and replace its contents or inject clean JSON
$jsonCleanObj = ConvertFrom-Json $jsonRaw

# Convert to a clean JS object literal
$jsObjStr = @"
    const staticData = $jsonRaw;
"@

# Pattern to replace staticData in standalone.html
$pattern = '(?s)const staticData = \{.*?\};\s*let activeSector'
$replacement = "$jsObjStr`n`n    let activeSector"

if ($htmlContent -match $pattern) {
    $updatedHtml = [regex]::Replace($htmlContent, $pattern, $replacement)
    $updatedHtml | Set-Content -Path $standalonePath -Encoding UTF8
    Write-Host "Replaced staticData in standalone.html with calibrated latest.json!" -ForegroundColor Green
} else {
    Write-Host "Pattern did not match directly, let's do safe targeted update." -ForegroundColor Yellow
}
