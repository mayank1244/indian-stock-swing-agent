param(
    [string]$Recipient = "nareshofficial.kumar@gmail.com",
    [string]$Sender = $env:SENDER_EMAIL,
    [string]$AppPassword = $env:SENDER_APP_PASSWORD
)

$reportFile = Join-Path $PSScriptRoot "reports\email_preview_latest.html"

if (-not (Test-Path $reportFile)) {
    Write-Host "[ERROR] HTML Report file not found at $reportFile" -ForegroundColor Red
    exit 1
}

$htmlBody = Get-Content $reportFile -Raw -Encoding UTF8

if ([string]::IsNullOrWhiteSpace($Sender) -or [string]::IsNullOrWhiteSpace($AppPassword)) {
    Write-Host "`n=======================================================" -ForegroundColor Cyan
    Write-Host " [STATUS] EMAIL REPORT READY FOR DISPATCH" -ForegroundColor Green
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-Host " Recipient : $Recipient"
    Write-Host " Subject   : SwingPulse Daily: 5 Intraday Scalps, Swings, Watchlist, MCX Setups"
    Write-Host " Report    : $reportFile"
    Write-Host ""
    Write-Host " [NOTE] Direct background SMTP requires SENDER_EMAIL and SENDER_APP_PASSWORD." -ForegroundColor Yellow
    Write-Host " To dispatch live via Gmail:"
    Write-Host " 1. Generate a 16-character Google App Password from: https://myaccount.google.com/apppasswords"
    Write-Host " 2. Set `$env:SENDER_EMAIL = 'your-email@gmail.com'"
    Write-Host " 3. Set `$env:SENDER_APP_PASSWORD = 'your-16-char-app-password'"
    Write-Host " 4. Re-run .\send_email.ps1"
    Write-Host "=======================================================`n" -ForegroundColor Cyan
    exit 0
}

try {
    Write-Host "Connecting to smtp.gmail.com:587..." -ForegroundColor Cyan
    $smtp = New-Object System.Net.Mail.SmtpClient("smtp.gmail.com", 587)
    $smtp.EnableSsl = $true
    $smtp.Credentials = New-Object System.Net.NetworkCredential($Sender, $AppPassword)

    $mail = New-Object System.Net.Mail.MailMessage
    $mail.From = New-Object System.Net.Mail.MailAddress($Sender, "SwingPulse Trader")
    $mail.To.Add($Recipient)
    $mail.Subject = "SwingPulse Daily Pulse: 5 Intraday Scalps, Swings, Watchlist, MCX Setups"
    $mail.Body = $htmlBody
    $mail.IsBodyHtml = $true

    $smtp.Send($mail)
    Write-Host "Email sent successfully to $Recipient!" -ForegroundColor Green
} catch {
    Write-Host "Failed to send email via SMTP: $_" -ForegroundColor Red
}
