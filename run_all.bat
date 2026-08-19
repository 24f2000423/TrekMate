@echo off
echo ========================================================
echo Launching Trekking Management Application (TMA - V2)
echo ========================================================

start "TMA Backend API (Flask)" cmd /k "cd backend && .\venv\Scripts\python.exe app.py"
timeout /t 2 /nobreak >nul

start "TMA Frontend (Vue 3 + Vite)" cmd /k "cd frontend && npm.cmd run dev"

echo Both services launched in separate windows!
echo Frontend: http://localhost:5173
echo Backend:  http://127.0.0.1:5000
pause
