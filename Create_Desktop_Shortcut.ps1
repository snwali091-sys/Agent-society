# Create Desktop Shortcut for Agent Society
# Run this ONCE: right-click this file -> Run with PowerShell

$ProjectPath = $PSScriptRoot
$Desktop = [Environment]::GetFolderPath("Desktop")
$IconPath = Join-Path $ProjectPath "agent_society.ico"
$LaunchScript = Join-Path $ProjectPath "Launch_Silent.ps1"

# Build the quote character separately to avoid fragile backtick-escaping
$q = [char]34

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut((Join-Path $Desktop "Agent Society.lnk"))
$Shortcut.TargetPath = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
$Shortcut.Arguments = "-WindowStyle Hidden -ExecutionPolicy Bypass -File " + $q + $LaunchScript + $q
$Shortcut.WorkingDirectory = $ProjectPath
$Shortcut.Description = "Agent Society - Multi-Agent AI System"
$Shortcut.IconLocation = $IconPath
$Shortcut.Save()

Write-Host ""
Write-Host "Desktop shortcut created successfully." -ForegroundColor Green
Write-Host "Look for Agent Society on your Desktop." -ForegroundColor Green
Write-Host "Double-click it to launch." -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to close"
