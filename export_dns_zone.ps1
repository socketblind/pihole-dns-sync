$Zone = $args[0]
$TargetPath = $args[1]

Write-Host "Exporting zone: $Zone" -ForegroundColor "Yellow"

$DNSExportDirectory = "C:\Windows\System32\dns\"
$ZoneFileName = "$Zone.txt"
$DNSExportFilePath = $DNSExportDirectory + $ZoneFileName

Write-Host "Clear zone file: $ZoneFileName"
Remove-Item $DNSExportFilePath
Write-Host "Export zone file: $DNSExportFilePath"
Export-DnsServerZone -name $Zone -filename $ZoneFileName
Write-Host "Copy zone file: $DNSExportFilePath => $TargetPath\$ZoneFileName"
Copy-Item $DNSExportFilePath $TargetPath