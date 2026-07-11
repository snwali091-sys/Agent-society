# Agent Society — Launch Script
# This file is called by the desktop shortcut. You should not need to
# run this directly, but you can double-click it too if you prefer.

$ProjectPath = $PSScriptRoot
Set-Location $ProjectPath

# Free up port 8000 if a previous session is still holding it —
# prevents the silent "connection refused" failure on a second launch
$existing = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($existing) {
    foreach ($conn in $existing) {
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 1
}

# Start the backend server completely hidden
Start-Process -FilePath "uvicorn" -ArgumentList "api.main:app --host 127.0.0.1 --port 8000" -WindowStyle Hidden

# Wait for it to finish booting before opening the browser
Start-Sleep -Seconds 4

# Open the app
Start-Process "http://localhost:8000"
