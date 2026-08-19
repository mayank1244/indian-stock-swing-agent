param(
    [int]$Port = 8080,
    [string]$WebRoot = (Join-Path $PSScriptRoot "web")
)

$ipObj = Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi*", "Ethernet*" | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object -First 1
$ip = if ($ipObj) { $ipObj.IPAddress } else { "127.0.0.1" }
$url = "http://${ip}:${Port}/standalone.html"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " [ONLINE] SWINGPULSE MOBILE LIVE SERVER" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Mobile URL: $url" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan

$endpoint = New-Object System.Net.IPEndPoint([System.Net.IPAddress]::Any, $Port)
$listener = New-Object System.Net.Sockets.TcpListener($endpoint)
$listener.Start()

$mimeTypes = @{
    ".html" = "text/html; charset=utf-8"
    ".css"  = "text/css; charset=utf-8"
    ".js"   = "application/javascript; charset=utf-8"
    ".json" = "application/json; charset=utf-8"
    ".png"  = "image/png"
    ".jpg"  = "image/jpeg"
    ".svg"  = "image/svg+xml"
    ".ico"  = "image/x-icon"
}

try {
    while ($true) {
        $client = $listener.AcceptTcpClient()
        $stream = $client.GetStream()
        $buffer = New-Object byte[] 4096
        $bytesRead = $stream.Read($buffer, 0, $buffer.Length)
        $requestText = [System.Text.Encoding]::ASCII.GetString($buffer, 0, $bytesRead)

        if (-not [string]::IsNullOrWhiteSpace($requestText)) {
            $firstLine = $requestText.Split("`r`n")[0]
            $tokens = $firstLine.Split(" ")
            $rawPath = if ($tokens.Length -gt 1) { $tokens[1] } else { "/" }
            $cleanPath = $rawPath.TrimStart("/").Split("?")[0]
            if ([string]::IsNullOrWhiteSpace($cleanPath)) {
                $cleanPath = "standalone.html"
            }

            $targetFile = Join-Path $WebRoot $cleanPath
            if (-not (Test-Path $targetFile)) {
                $targetFile = Join-Path $WebRoot "standalone.html"
            }

            if (Test-Path $targetFile) {
                $ext = [System.IO.Path]::GetExtension($targetFile).ToLower()
                $contentType = if ($mimeTypes.ContainsKey($ext)) { $mimeTypes[$ext] } else { "text/html; charset=utf-8" }
                $fileBytes = [System.IO.File]::ReadAllBytes($targetFile)

                $header = "HTTP/1.1 200 OK`r`n" +
                          "Content-Type: $contentType`r`n" +
                          "Content-Length: $($fileBytes.Length)`r`n" +
                          "Access-Control-Allow-Origin: *`r`n" +
                          "Connection: close`r`n`r`n"
                
                $headerBytes = [System.Text.Encoding]::ASCII.GetBytes($header)
                $stream.Write($headerBytes, 0, $headerBytes.Length)
                $stream.Write($fileBytes, 0, $fileBytes.Length)
                $stream.Flush()
            }
        }
        $client.Close()
    }
} finally {
    $listener.Stop()
}
