@echo off
chcp 65001 >nul
echo ========================================
echo 🧠 Monoque Intelligence - Windows Başlatma
echo ========================================
echo.

echo 📦 MongoDB başlatılıyor...
start "MongoDB" cmd /c "cd backend && mongod --dbpath=./data/db"
timeout /t 3 >nul

echo.
echo 🔧 Backend başlatılıyor...
start "Backend" cmd /c "cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && python server.py"
timeout /t 5 >nul

echo.
echo 🎨 Frontend başlatılıyor...
start "Frontend" cmd /c "cd frontend && yarn install && yarn start"
timeout /t 3 >nul

echo.
echo ========================================
echo ✅ Tüm servisler başlatıldı!
echo ========================================
echo.
echo Backend:  http://localhost:8001/api
echo Frontend: http://localhost:3000
echo.
echo Kapatmak için pencereleri kapatın.
echo.
pause
