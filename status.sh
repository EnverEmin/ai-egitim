#!/bin/bash

# Monoque Intelligence - Durum Kontrol Script'i
# Tüm servislerin durumunu gösterir

echo "📊 Monoque Intelligence - Servis Durumu"
echo "="
echo ""

sudo supervisorctl status

echo ""
echo "API Test:"
echo "="

# Backend API'yi test et
if curl -s http://localhost:8001/api/ > /dev/null 2>&1; then
    echo "✅ Backend API çalışıyor"
    curl -s http://localhost:8001/api/ | python3 -m json.tool 2>/dev/null || echo "API yanıtı alındı"
else
    echo "❌ Backend API'ye erişilemiyor"
fi

echo ""
echo "İstatistikler:"
echo "="
curl -s http://localhost:8001/api/stats | python3 -m json.tool 2>/dev/null || echo "İstatistikler alınamadı"

echo ""
