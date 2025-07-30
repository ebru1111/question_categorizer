# AI Tabanlı Soru Kategorizasyon Sistemi

**Embedding tabanlı akıllı soru kategorizasyon API'si**

Bu proje, kullanıcı sorularını 9 farklı kategoriye ayıran gelişmiş bir AI sistemidir. Sentence Transformers ve cosine similarity algoritmaları kullanarak yüksek doğrulukla kategorizasyon yapar.

## Özellikler

- **9 farklı kategori** desteği
- **Embedding tabanlı** AI kategorizasyon


## Sistem Mimarisi

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HTTP Request  │────│   Flask API     │────│  AICategorizer  │
│   (JSON)        │    │   (main.py)     │    │ (ai_categorizer)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │ SentenceTransf. │
                                              │ + Cosine Sim.   │
                                              └─────────────────┘
```
<img width="2804" height="2024" alt="mermaid-diagram-2025-07-30-020241" src="https://github.com/user-attachments/assets/415d4709-11d2-4846-98a3-de941adcc242" />

## Kurulum

### Gereksinimler

- Python 3.8+
- pip
- Virtual environment (önerilen)

### 1. Projeyi İndirin
```bash
git clone <repo-url>
cd question-categorizer
```

### 2. Virtual Environment Oluşturun
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

**Not:** `sentence-transformers` kütüphanesi zorunludur.

### 4. Sistemi Başlatın
```bash
python main.py
```

**Sistem hazır!** http://localhost:5002

## Docker ile Çalıştırma

```bash
# Docker imajını oluştur
docker build -t question-categorizer .

# Container'ı çalıştır
docker run -d --name categorizer-app -p 5002:5002 question-categorizer

# Test et
curl http://localhost:5002/health
```

## Kullanım

### Hızlı Test
```bash
# Sağlık kontrolü
curl http://localhost:5002/health

# Test sorusu
curl -X POST http://localhost:5002/categorize \
  -H "Content-Type: application/json" \
  -d '{"question": "Bu ürün orijinal mi?"}'

# Tüm testleri çalıştır
curl http://localhost:5002/test
```

## API Dokümantasyonu

### Base URL
```
http://localhost:5002
```

### Endpoints

#### POST /categorize
Bir soruyu AI ile kategorize eder.

**Request:**
```json
{
    "question": "Bu ürün çok güzel, beğendim"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "category": "yorum",
        "category_name": "yorum",
        "confidence": 0.89,
        "method": "embedding",
        "similarities": {
            "yorum": 0.89,
            "teknik": 0.23,
            "stok": 0.15
        }
    }
}
```

#### GET /test
Sistem testini çalıştırır.

#### GET /health
API sağlık kontrolü.

#### GET /
API dokümantasyonu.

## Kategoriler

| Kategori ID | Görünen İsim | Açıklama | Örnek |
|-------------|--------------|----------|-------|
| `yorum` | Yorum | Ürün yorumları ve değerlendirmeler | "Bu ürün çok güzel" |
| `ozel_talep` | Özel Talep | Özelleştirme talepleri | "Özel bir renk istiyorum" |
| `teknik` | Teknik | Teknik destek ve arızalar | "Ürün çalışmıyor" |
| `yanlis_hasarli` | Yanlış/Hasarlı Ürün | Ürün sorunları | "Ürün hasarlı geldi" |
| `orijinallik` | Orijinallik | Sahtelik sorguları | "Bu ürün orijinal mi?" |
| `iade_degisim` | İade ve Değişim | İade/değişim talepleri | "İade etmek istiyorum" |
| `stok` | Stok | Stok durumu sorguları | "Bu ürün stokta var mı?" |
| `kargo_bilgileri` | Kargo Bilgileri | Kargo firma/takip | "Hangi kargo firması?" |
| `siparis_teslimat` | Sipariş Teslimat | Teslimat durumu | "Ne zaman teslim edilecek?" |

## Teknik Detaylar

### Kullanılan Teknolojiler
- **Framework:** Flask 2.3+
- **AI Model:** sentence-transformers/all-MiniLM-L6-v2
- **Algoritma:** Cosine Similarity
- **Dil:** Python 3.8+
- **Format:** JSON API

### Model Özellikleri
- **Embedding Boyutu:** 384
- **Model Tipi:** Transformer (MiniLM)
- **Dil Desteği:** Çok dilli
- **Hız:** Optimize edilmiş (CPU)
- **Boyut:** ~90MB

### Algoritma
1. **Soru embedding'i** hesaplanır
2. **Kategori embedding'leri** ile karşılaştırılır
3. **Cosine similarity** hesaplanır
4. **En yüksek skor** seçilir

### Performans Metrikleri
- **Doğruluk:** %85-95
- **Yanıt Süresi:** 100-200ms
- **Memory:** ~500MB
- **CPU:** Orta seviye

## Test

### API Testleri (Hızlı)
```bash
python simple_test.py
```

### Kapsamlı Testler
```bash
python test_categorizer.py
```

**Test özellikleri:**
- 27 test sorusu
- Her kategoriden örnek
- Doğruluk oranı hesaplama
- Performans analizi
- JSON rapor çıktısı

## Proje Yapısı

```
question-categorizer/
├── ai_categorizer.py       # Ana AI kategorizer sınıfı
├── main.py                 # Flask API servisi
├── requirements.txt        # Python bağımlılıkları
├── Dockerfile             # Docker yapılandırması
├── docker-commands.sh     # Docker yardımcı komutları
├── simple_test.py         # API testleri
├── test_categorizer.py    # Kapsamlı testler
├── README.md              # Bu dosya
└── venv/                  # Virtual environment
```

## Sorun Giderme

**Torch yüklenmiyor:** Python 3.11/3.12 kullanın, 3.13 ile uyumsuzluk var

**Port çakışması:** main.py'da port'u değiştirin

**Memory sorunu:** Docker container'ı daha fazla RAM ile çalıştırın


- **Proje:** AI Soru Kategorizasyon Sistemi
- **Versiyon:** 1.0.0
- **Lisans:** MIT

---

**Not:** BERT tabanlı alternatif sistem `question-categorizer-bert` projesinde mevcuttur.

