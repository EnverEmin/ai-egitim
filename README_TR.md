# 🧠 Monoque Intelligence - Adaptive Learning Core

İki fazlı adaptif öğrenme yapay zeka sistemi.

## 🚀 Hızlı Başlangıç

### Linux/Mac (Emergent Platformu)

```bash
# Başlat
./start.sh

# Durdur
./stop.sh

# Yeniden başlat
./restart.sh

# Durum kontrol
./status.sh
```

### Windows (Yerel Kurulum)

1. **Kurulum** (İlk kez):
   ```
   INSTALL_WINDOWS.bat
   ```

2. **Başlatma**:
   ```
   START_WINDOWS.bat
   ```

## 📋 Gereksinimler

- Python 3.8+
- Node.js 16+
- MongoDB 4.4+
- Yarn (opsiyonel, npm de kullanılabilir)

## 🎯 Özellikler

### Faz 1: Kapalı Sistem (Offline)
- Sadece sizden öğrenir
- Her bilgi onaylanır ve kaydedilir
- Otomatik kavram çıkarımı

### Faz 2: Açık Sistem (Online)
- İnternetten bilgi toplayabilir
- Bilgileri sizin onayınıza sunar
- Güven puanı sistemi

## 🔧 API Endpoints

### Chat
```bash
POST /api/chat
{
  "message": "Merhaba",
  "session_id": "optional-session-id"
}
```

### İstatistikler
```bash
GET /api/stats
```

### Kavramlar
```bash
GET /api/concepts
```

### Faz Değiştirme
```bash
POST /api/phase
{
  "phase": "online"  // veya "offline"
}
```

## 📊 Mimari

```
┌─────────────┐
│   Frontend  │  React + Tailwind CSS
│  (Port 3000)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Backend   │  FastAPI + MongoDB
│  (Port 8001)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   MongoDB   │  Database
│ (Port 27017)│
└─────────────┘
       │
       ▼
┌─────────────┐
│ Emergent LLM│  GPT-4o
│     Key     │
└─────────────┘
```

## 🗂️ Veritabanı Yapısı

### Collections:
- `knowledge` - Öğrenilen bilgiler
- `concepts` - Kavramlar
- `messages` - Chat mesajları
- `versions` - Model versiyonları

## 🔐 Güvenlik

- `.env` dosyasını asla paylaşmayın
- `EMERGENT_LLM_KEY` gizli tutulmalıdır
- MongoDB bağlantı string'i korunmalıdır

## 🐛 Sorun Giderme

### Backend başlamıyor:
```bash
tail -f /var/log/supervisor/backend.*.log
```

### Frontend başlamıyor:
```bash
tail -f /var/log/supervisor/frontend.*.log
```

### MongoDB bağlantı hatası:
```bash
sudo supervisorctl restart mongodb
```

## 📝 Lisans

Bu proje özel kullanım içindir.

## 👨‍💻 Geliştirici

Enver (Monoque) tarafından geliştirilmiştir.
