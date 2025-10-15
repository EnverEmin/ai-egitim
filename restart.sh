#!/bin/bash

# Monoque Intelligence - Yeniden Başlatma Script'i
# Tüm servisleri yeniden başlatır

echo "🔄 Monoque Intelligence Yeniden Başlatılıyor..."
echo "="
echo ""

# Tüm servisleri yeniden başlat
sudo supervisorctl restart all

echo ""
echo "Servisler yeniden başlatılıyor, lütfen bekleyin..."
sleep 5

echo ""
echo "="
echo "📊 Servis Durumu:"
echo "="
sudo supervisorctl status

echo ""
echo "✅ Yeniden başlatma tamamlandı!"
echo ""
