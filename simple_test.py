#!/usr/bin/env python3
"""
Basit Test Dosyası - API Endpoint Testleri
sentence-transformers gerektirmez
"""

import requests
import json
from datetime import datetime

def test_api_endpoints():
    """API endpoint'lerini test et"""
    base_url = "http://localhost:5002"
    
    print("API Endpoint Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test soruları
    test_questions = [
        "Bu ürün çok güzel, beğendim",
        "Özel bir renk istiyorum", 
        "Ürün çalışmıyor, yardım edin",
        "Ürün hasarlı geldi",
        "Bu ürün orijinal mi?",
        "İade etmek istiyorum",
        "Bu ürün stokta var mı?",
        "Hangi kargo firması?",
        "Siparişim ne zaman teslim edilecek?",
        "",  # Boş soru
        "Merhaba nasılsın?"  # İlgisiz soru
    ]
    
    print("1. Health Check Testi:")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("Health check başarılı")
            print(f"   Response: {response.json()}")
        else:
            print(f"Health check başarısız: {response.status_code}")
    except Exception as e:
        print(f"Health check hatası: {e}")
    
    print("\n2. Kategorization Testleri:")
    print("-" * 50)
    print(f"{'Soru':<35} {'Kategori':<15} {'Confidence':<10} {'Yüksek':<8}")
    print("-" * 50)
    
    results = []
    for question in test_questions:
        try:
            response = requests.post(
                f"{base_url}/categorize",
                json={"question": question},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    result = data["data"]
                    category = result["category"]
                    confidence = result["confidence"]
                    is_high = "Yüksek" if result["is_high_similarity"] else "Düşük"
                    
                    print(f"{question[:34]:<35} {category:<15} {confidence:<10.3f} {is_high:<8}")
                    
                    results.append({
                        "question": question,
                        "category": category,
                        "confidence": confidence,
                        "is_high_similarity": result["is_high_similarity"]
                    })
                else:
                    print(f"{question[:34]:<35} HATA: {data['message']}")
            else:
                print(f"{question[:34]:<35} HTTP ERROR: {response.status_code}")
                
        except Exception as e:
            print(f"{question[:34]:<35} EXCEPTION: {e}")
    
    print("\n3. Test Endpoint Testi:")
    try:
        response = requests.get(f"{base_url}/test")
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                print("Test endpoint başarılı")
                print(f"   Test sonuçları: {len(data['test_results'])} soru")
                
                # İlk 3 sonucu göster
                for i, result in enumerate(data["test_results"][:3]):
                    if "error" not in result:
                        print(f"   {i+1}. {result['question'][:30]}... → {result['category']} ({result['confidence']})")
                    else:
                        print(f"   {i+1}. {result['question'][:30]}... → HATA: {result['error']}")
            else:
                print(f"Test endpoint başarısız: {data['message']}")
        else:
            print(f"Test endpoint HTTP hatası: {response.status_code}")
    except Exception as e:
        print(f"Test endpoint hatası: {e}")
    
    print("\n4. İstatistikler:")
    if results:
        total = len(results)
        high_similarity = sum(1 for r in results if r["is_high_similarity"])
        avg_confidence = sum(r["confidence"] for r in results) / total
        
        print(f"Toplam test: {total}")
        print(f"Yüksek benzerlik: {high_similarity} ({high_similarity/total:.1%})")
        print(f"Ortalama confidence: {avg_confidence:.3f}")
        
        # En yüksek confidence skorları
        sorted_results = sorted(results, key=lambda x: x["confidence"], reverse=True)
        print(f"\nEn yüksek skorlar:")
        for i, result in enumerate(sorted_results[:3]):
            print(f"   {i+1}. {result['confidence']:.3f} - '{result['question'][:40]}...'")
    
    # Ana sayfa testi
    print("\n5. Ana Sayfa Testi:")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            data = response.json()
            print("Ana sayfa başarılı")
            print(f"   Servis: {data.get('service', 'N/A')}")
            print(f"   Versiyon: {data.get('version', 'N/A')}")
            print(f"   Endpoint sayısı: {len(data.get('endpoints', {}))}")
        else:
            print(f"Ana sayfa hatası: {response.status_code}")
    except Exception as e:
        print(f"Ana sayfa hatası: {e}")
    
    print("\nTüm testler tamamlandı!")

def test_error_cases():
    """Hata durumlarını test et"""
    base_url = "http://localhost:5002"
    
    print("\nHata Durumları Testi:")
    print("-" * 30)
    
    error_cases = [
        # Geçersiz JSON
        ("Geçersiz JSON", "invalid json"),
        # Eksik question parametresi  
        ("Eksik question", {}),
        # Yanlış endpoint
        ("Yanlış endpoint", "/nonexistent"),
    ]
    
    for case_name, test_data in error_cases:
        try:
            if case_name == "Yanlış endpoint":
                response = requests.get(f"{base_url}{test_data}")
            else:
                if case_name == "Geçersiz JSON":
                    response = requests.post(
                        f"{base_url}/categorize",
                        data=test_data,
                        headers={"Content-Type": "application/json"}
                    )
                else:
                    response = requests.post(
                        f"{base_url}/categorize",
                        json=test_data,
                        headers={"Content-Type": "application/json"}
                    )
            
            print(f"{case_name:<20}: Status {response.status_code}")
            
            if response.status_code == 400:
                print(f"                     Beklenen hata alındı")
            elif response.status_code == 404 and case_name == "Yanlış endpoint":
                print(f"                     Beklenen 404 hatası")
            else:
                print(f"                     Beklenmeyen durum")
                
        except Exception as e:
            print(f"{case_name:<20}: Exception {e}")

if __name__ == "__main__":
    print("Flask API'sinin çalıştığından emin olun!")
    print("Komut: python main.py")
    input("\nAPI çalışıyor mu? Devam etmek için Enter'a basın...")
    
    # Ana testleri çalıştır
    test_api_endpoints()
    
    # Hata durumlarını test et
    test_error_cases()
    
    print("\nTüm testler bitti!") 