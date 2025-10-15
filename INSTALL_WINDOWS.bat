@echo off
chcp 65001 >nul
echo ========================================
echo 🧠 Monoque Intelligence - Kurulum
echo ========================================
echo.

echo Gereksinimler kontrol ediliyor...
echo.

echo 🐍 Python kontrol ediliyor...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python bulunamadı!
    echo Lütfen Python 3.8+ yükleyin: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python bulundu

echo.
echo 📦 Node.js kontrol ediliyor...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js bulunamadı!
    echo Lütfen Node.js yükleyin: https://nodejs.org/
    pause
    exit /b 1
)
echo ✅ Node.js bulundu

echo.
echo 🧶 Yarn kontrol ediliyor...
yarn --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Yarn bulunamadı, npm kullanılacak
    set USE_NPM=1
) else (
    echo ✅ Yarn bulundu
    set USE_NPM=0
)

echo.
echo 📦 MongoDB kontrol ediliyor...
mongod --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ MongoDB bulunamadı!
    echo Lütfen MongoDB yükleyin: https://www.mongodb.com/try/download/community
    pause
    exit /b 1
)
echo ✅ MongoDB bulundu

echo.
echo ========================================
echo 📦 Backend bağımlılıkları yükleniyor...
echo ========================================
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo.
echo ========================================
echo 🎨 Frontend bağımlılıkları yükleniyor...
echo ========================================
cd frontend
if %USE_NPM%==1 (
    npm install
) else (
    yarn install
)
cd ..

echo.
echo ========================================
echo ✅ Kurulum tamamlandı!
echo ========================================
echo.
echo Uygulamayı başlatmak için START_WINDOWS.bat dosyasını çalıştırın.
echo.
pause
