#!/bin/bash

# Monoque Intelligence - Durdurma Script'i
# Tüm servisleri durdurur

echo "🛑 Monoque Intelligence Durduruluyor..."
echo "="
echo ""

# Tüm servisleri durdur
sudo supervisorctl stop all

echo ""
echo "✅ Tüm servisler durduruldu."
echo ""
