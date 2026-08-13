# Run this script in PowerShell as Administrator

$cfgPath = "C:\Program Files\MongoDB\Server\8.3\bin\mongod.cfg"
$content = Get-Content $cfgPath -Raw

if ($content -notmatch "replSetName:\s*rs0") {
    Add-Content -Path $cfgPath -Value "`nreplication:`n  replSetName: rs0`n"
    Write-Host "Added replication config to mongod.cfg" -ForegroundColor Green
} else {
    Write-Host "Replication config already present in mongod.cfg" -ForegroundColor Yellow
}

Write-Host "Restarting MongoDB Service..." -ForegroundColor Cyan
Restart-Service MongoDB

Start-Sleep -Seconds 3

Write-Host "Initiating replica set rs0..." -ForegroundColor Cyan
mongosh --eval "rs.initiate()"

Write-Host "Checking replica set status..." -ForegroundColor Cyan
mongosh --eval "rs.status().ok"
