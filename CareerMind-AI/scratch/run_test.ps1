$vite = Start-Process -FilePath "cmd.exe" -ArgumentList "/c","npm run dev -- --port 5199 --strictPort" -WorkingDirectory "c:\Users\ASUS\Videos\CareerAI\CareerMind-AI\frontend" -PassThru
Start-Sleep -Seconds 5
try {
    & "c:\Users\ASUS\Videos\CareerAI\CareerMind-AI\backend\.venv\Scripts\python.exe" "c:\Users\ASUS\Videos\CareerAI\CareerMind-AI\scratch\verify_ui_flows.py" "5199"
} finally {
    Stop-Process -Id $vite.Id -Force -ErrorAction SilentlyContinue
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*5199*" } | Stop-Process -Force -ErrorAction SilentlyContinue
}

