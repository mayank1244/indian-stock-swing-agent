$root = "C:\Users\jeevi\.gemini\antigravity\scratch\indian-stock-swing-agent"
$utf8 = [System.Text.UTF8Encoding]::new($false)

$jsonText = [System.IO.File]::ReadAllText("$root\web\data\latest.json", $utf8)
$appJsText = [System.IO.File]::ReadAllText("$root\web\app.js", $utf8)

$htmlTemplate = [System.IO.File]::ReadAllText("$root\web\standalone.html", $utf8)
$scriptIdx = $htmlTemplate.IndexOf("<script")
if ($scriptIdx -gt 0) {
    $htmlBody = $htmlTemplate.Substring(0, $scriptIdx)
} else {
    $htmlBody = $htmlTemplate
}

# Update Subtitle / Header badges for Daily Intraday vs Weekly Swings
$htmlBody = $htmlBody.Replace(
    '<span class="tag-sub">5 Today</span>',
    '<span class="tag-sub">🔄 Daily Rotation</span>'
)
$htmlBody = $htmlBody.Replace(
    '<span class="tag-sub">5 Swings</span>',
    '<span class="tag-sub">📅 Weekly Swings</span>'
)
$htmlBody = $htmlBody.Replace(
    '<span class="tag-sub">5 Positional</span>',
    '<span class="tag-sub">📅 Weekly Positional</span>'
)

# Replace count badge on scorecard
$htmlBody = $htmlBody.Replace(
    '<span class="count-badge">6 Case Studies</span>',
    '<span class="count-badge">5 Verified Studies</span>'
)
$htmlBody = $htmlBody.Replace(
    '<span class="bt-stat-value">6</span>',
    '<span class="bt-stat-value">5</span>'
)

$standaloneContent = $htmlBody + @"
<script>
window.staticData = $jsonText;
</script>
<script>
$appJsText
</script>
</body>
</html>
"@

$indexContent = $htmlBody + @"
<script>
window.staticData = $jsonText;
</script>
<script src="app.js"></script>
</body>
</html>
"@

[System.IO.File]::WriteAllText("$root\web\standalone.html", $standaloneContent, $utf8)
[System.IO.File]::WriteAllText("$root\web\index.html", $indexContent, $utf8)

# Sync to secondary workspace
$otherRoot = "C:\Users\jeevi\.gemini\antigravity\scratch\indian-stock-agent"
if (Test-Path "$otherRoot\web") {
    [System.IO.File]::WriteAllText("$otherRoot\web\standalone.html", $standaloneContent, $utf8)
    [System.IO.File]::WriteAllText("$otherRoot\web\index.html", $indexContent, $utf8)
    [System.IO.File]::WriteAllText("$otherRoot\web\app.js", $appJsText, $utf8)
    [System.IO.File]::WriteAllText("$otherRoot\web\data\latest.json", $jsonText, $utf8)
}

Write-Host "Build complete! Web files compiled cleanly." -ForegroundColor Green
