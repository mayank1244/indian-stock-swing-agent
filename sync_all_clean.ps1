$jsonPath = "web\data\latest.json"
$targetStandalone = "web\standalone.html"
$targetIndex = "web\index.html"
$targetOtherStandalone = "..\indian-stock-agent\web\standalone.html"
$targetOtherIndex = "..\indian-stock-agent\web\index.html"
$targetOtherData = "..\indian-stock-agent\web\data\latest.json"

# Read JSON directly
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$jsonBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $jsonPath))
$jsonStr = $utf8NoBom.GetString($jsonBytes)

# Check if JSON is valid
try {
    $obj = ConvertFrom-Json $jsonStr
    Write-Host "JSON is valid! Stocks count:" $obj.recommendations.Count -ForegroundColor Green
} catch {
    Write-Host "JSON parse error: $_" -ForegroundColor Red
}

# Update staticData inside standalone.html
$standaloneStr = [System.IO.File]::ReadAllText((Resolve-Path $targetStandalone), $utf8NoBom)
$pattern = '(?s)const staticData = \{.*?\};\s*let activeSector'
$replacement = "const staticData = $jsonStr;`n`n    let activeSector"

if ($standaloneStr -match $pattern) {
    $standaloneStr = [regex]::Replace($standaloneStr, $pattern, $replacement)
    [System.IO.File]::WriteAllText((Resolve-Path $targetStandalone), $standaloneStr, $utf8NoBom)
    [System.IO.File]::WriteAllText((Resolve-Path $targetIndex), $standaloneStr, $utf8NoBom)
    
    if (Test-Path "..\indian-stock-agent\web") {
        [System.IO.File]::WriteAllText((Resolve-Path $targetOtherStandalone), $standaloneStr, $utf8NoBom)
        [System.IO.File]::WriteAllText((Resolve-Path $targetOtherIndex), $standaloneStr, $utf8NoBom)
        [System.IO.File]::WriteAllText((Resolve-Path $targetOtherData), $jsonStr, $utf8NoBom)
    }
    Write-Host "Synchronized all web files with pristine UTF-8!" -ForegroundColor Green
} else {
    Write-Host "Regex did not match in standalone.html" -ForegroundColor Yellow
}
