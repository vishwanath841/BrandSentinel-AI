Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Starting BrandSentinel AI Enterprise Platform" -ForegroundColor Cyan
Write-Host "Developer: Vishwanath S A (GM Institute of Technology)" -ForegroundColor Gray
Write-Host "================================================================" -ForegroundColor Cyan

Set-Location -Path $PSScriptRoot

Write-Host "`n[1/2] Verifying backend dependencies..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\backend"
python -c "import fastapi, uvicorn, fitz, docx, cv2, PIL; print('All backend libraries loaded.')"

Write-Host "`n[2/2] Launching BrandSentinel AI full-stack server on http://localhost:8000..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server.`n" -ForegroundColor Gray
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

