# MedBalance Web App Launcher
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "  Starting MedBalance Data Validator Web App..." -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

# Open index.html in the default browser
Start-Process "index.html"

# Run Python server
Write-Host "`nStarting local Python server on http://localhost:8000..." -ForegroundColor Green
python server.py

