#!/usr/bin/env python3
"""
Soru Kategorizasyon API Servisi
AI Tabanlı Kategorizasyon - Flask REST API

Bu Flask uygulaması, AI tabanlı soru kategorizasyon sistemini
HTTP API olarak sunar. Embedding tabanlı kategorizasyon
için ai_categorizer modülünü kullanır.

API Endpoints:
- POST /categorize: Soruyu kategorize et
- GET /test: Test sorularını çalıştır
- GET /health: Sağlık kontrolü
- GET /: API dokümantasyonu

Port: 5002 (geliştirme modu)
"""

from flask import Flask, request, jsonify
from ai_categorizer import AICategorizer
from datetime import datetime

# Flask uygulamasını oluştur
app = Flask(__name__)

# AI Categorizer instance - Uygulama başlatıldığında yüklenir
# Bu sayede her request'te model yeniden yüklenmez
categorizer = AICategorizer()

@app.route('/categorize', methods=['POST'])
def categorize():
    """
    Soruyu kategorize et - Ana API endpoint
    
    POST request'te gelen soruyu AI ile kategorize eder.
    JSON format'ta soru gönderilmeli.
    
    Request Body:
        {
            "question": "Hangi kargo firması kullanıyorsunuz?"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "category": "kargo_bilgileri",
                "category_name": "Kargo bilgileri", 
                "confidence": 0.89,
                "method": "embedding",
                "similarities": {...},
                "is_high_similarity": true
            }
        }
    
    Returns:
        JSON: Kategorizasyon sonucu veya hata mesajı
        HTTP 200: Başarılı kategorizasyon
        HTTP 400: Geçersiz request (boş soru vb.)
        HTTP 500: Sunucu hatası
    """
    try:
        # Request'ten JSON data'yı al
        data = request.get_json()
        question = data.get('question', '').strip()
        
        # Boş soru kontrolü
        if not question:
            return jsonify({
                'success': False,
                'message': 'Soru parametresi gerekli'
            }), 400
        
        # AI ile kategorizasyon yap
        result = categorizer.categorize_question(question)
        
        # Başarılı sonucu döndür
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        # Sunucu hatası durumunda
        return jsonify({
            'success': False,
            'message': f'Kategorizasyon hatası: {str(e)}'
        }), 500

@app.route('/test', methods=['GET'])
def test():
    """
    Test endpoint - Örnek sorularla sistem testi
    
    Önceden tanımlanmış test sorularını kategorize eder.
    Sistem performansını test etmek için kullanılır.
    
    Test soruları her kategoriden örnek içerir:
    - Yorum, özel talep, teknik, hasarlı ürün vb.
    
    Returns:
        JSON: Test sonuçları
        {
            "success": true,
            "test_results": [
                {
                    "question": "...",
                    "category": "...", 
                    "category_name": "...",
                    "confidence": 0.85
                }
            ]
        }
    """
    # Test için kullanılacak örnek sorular
    # Her kategoriden en az bir örnek
    test_questions = [
        'Bu ürün hakkında yorum yapabilir misiniz?',     # yorum
        'Özel bir sipariş vermek istiyorum',             # ozel_talep
        'Teknik destek alabilir miyim?',                 # teknik
        'Ürün hasarlı geldi',                           # yanlis_hasarli
        'Bu ürün orijinal mi?',                         # orijinallik
        'İade nasıl yapılır?',                          # iade_degisim
        'Bu ürün stokta var mı?',                       # stok
        'Hangi kargo firması kullanıyorsunuz?',         # kargo_bilgileri
        'Siparişim ne zaman teslim edilecek?'           # siparis_teslimat
    ]
    
    results = []
    
    # Her test sorusunu kategorize et
    for question in test_questions:
        try:
            result = categorizer.categorize_question(question)
            
            # Sadece önemli bilgileri test sonucuna ekle
            results.append({
                'question': question,
                'category': result['category'],
                'category_name': result['category_name'],
                'confidence': round(result['confidence'], 3)  # 3 ondalık basamak
            })
        except Exception as e:
            # Bireysel soru hatası - diğer testleri etkilemesin
            results.append({
                'question': question,
                'error': str(e)
            })
    
    return jsonify({
        'success': True,
        'test_results': results
    })

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint - Sistem sağlık kontrolü
    
    API'nin çalışır durumda olduğunu kontrol eder.
    Load balancer ve monitoring sistemleri tarafından kullanılır.
    
    Returns:
        JSON: Sağlık durumu bilgisi
        {
            "success": true,
            "status": "healthy",
            "service": "Question Categorization Service",
            "timestamp": "2025-01-30T01:45:30.123456"
        }
    """
    return jsonify({
        'success': True,
        'status': 'healthy',
        'service': 'Question Categorization Service',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def home():
    """
    Ana sayfa - API dokümantasyonu
    
    Mevcut endpoint'lerin listesini ve kısa açıklamalarını sunar.
    API keşfi için kullanılır.
    
    Returns:
        JSON: API bilgileri ve endpoint listesi
    """
    return jsonify({
        'service': 'Question Categorization API',
        'version': '1.0.0',
        'description': 'AI tabanlı soru kategorizasyon sistemi',
        'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
        'categories': list(categorizer.categories.keys()),
        'endpoints': {
            'POST /categorize': 'Soruyu kategorize et',
            'GET /test': 'Test sorularını çalıştır', 
            'GET /health': 'Sağlık kontrolü',
            'GET /': 'API dokümantasyonu (bu sayfa)'
        },
        'usage_example': {
            'url': 'POST /categorize',
            'request': {
                'question': 'Bu ürün orijinal mi?'
            },
            'response': {
                'success': True,
                'data': {
                    'category': 'orijinallik',
                    'confidence': 0.85,
                    'is_high_similarity': True
                }
            }
        }
    })

# Uygulama ana fonksiyonu
if __name__ == '__main__':
    """
    Flask uygulamasını başlat
    
    Development modu:
    - Debug aktif (kod değişikliklerinde otomatik restart)
    - Tüm IP adreslerinden erişilebilir (0.0.0.0)
    - Port 5002 (5000 ve 5001 çakışma riski nedeniyle)
    
    Production için:
    - Debug modunu kapat (debug=False)
    - WSGI server kullan (gunicorn, uWSGI vb.)
    - Güvenlik ayarları ekle
    """
    print("Soru Kategorizasyon API Servisi Başlatılıyor...")
    print("Servis hazır! http://localhost:5002")
    print("API dokümantasyonu: http://localhost:5002")
    print("Test endpoint: http://localhost:5002/test")
    print("Health check: http://localhost:5002/health")
    print()
    print("Bu development server'dır. Production için WSGI server kullanın!")
    
    # Flask development server'ı başlat
    app.run(
        host='0.0.0.0',    # Tüm network interface'lerden erişim
        port=5002,         # Port numarası
        debug=True         # Development modu (auto-reload)
    )