#!/bin/bash

# Monoque Intelligence - Başlatma Script'i
# Tüm servisleri başlatır

echo "🧠 Monoque Intelligence Başlatılıyor..."
echo "="
echo ""

# Renk kodları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# MongoDB'nin çalıştığından emin ol
echo -e "${YELLOW}📦 MongoDB kontrol ediliyor...${NC}"
sudo supervisorctl start mongodb
sleep 2

if sudo supervisorctl status mongodb | grep -q "RUNNING"; then
    echo -e "${GREEN}✅ MongoDB çalışıyor${NC}"
else
    echo -e "${YELLOW}⚠️  MongoDB başlatılamadı, tekrar deneniyor...${NC}"
    sudo supervisorctl restart mongodb
    sleep 3
fi

# Backend'i başlat
echo ""
echo -e "${YELLOW}🔧 Backend başlatılıyor...${NC}"
sudo supervisorctl start backend
sleep 3

if sudo supervisorctl status backend | grep -q "RUNNING"; then
    echo -e "${GREEN}✅ Backend çalışıyor (Port 8001)${NC}"
else
    echo -e "${YELLOW}⚠️  Backend başlatılamadı${NC}"
fi

# Frontend'i başlat
echo ""
echo -e "${YELLOW}🎨 Frontend başlatılıyor...${NC}"
sudo supervisorctl start frontend
sleep 5

if sudo supervisorctl status frontend | grep -q "RUNNING"; then
    echo -e "${GREEN}✅ Frontend çalışıyor (Port 3000)${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend başlatılamadı${NC}"
fi

# Nginx'i başlat
echo ""
echo -e "${YELLOW}🌐 Nginx başlatılıyor...${NC}"
sudo supervisorctl start nginx-code-proxy
sleep 2

if sudo supervisorctl status nginx-code-proxy | grep -q "RUNNING"; then
    echo -e "${GREEN}✅ Nginx çalışıyor${NC}"
else
    echo -e "${YELLOW}⚠️  Nginx başlatılamadı${NC}"
fi

# Tüm servislerin durumunu göster
echo ""
echo "="
echo -e "${GREEN}📊 Tüm Servisler:${NC}"
echo "="
sudo supervisorctl status

echo ""
echo "="
echo -e "${GREEN}🚀 Monoque Intelligence Hazır!${NC}"
echo "="
echo ""
echo -e "Backend API: ${GREEN}http://localhost:8001/api${NC}"
echo -e "Frontend:    ${GREEN}http://localhost:3000${NC}"
echo ""
echo "Logları görmek için:"
echo "  Backend:  tail -f /var/log/supervisor/backend.*.log"
echo "  Frontend: tail -f /var/log/supervisor/frontend.*.log"
echo ""
