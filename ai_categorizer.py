#!/usr/bin/env python3
"""
AI Tabanlı Soru Kategorizasyon Sistemi
Embedding Tabanlı Kategorizasyon (sentence-transformers kütüphanesi gerekli)

Bu modül, kullanıcı sorularını 9 farklı kategoriye ayıran
gelişmiş bir AI sistemi sağlar. Embedding tabanlı benzerlik
algoritması kullanarak yüksek doğrulukla kategorizasyon yapar.

Kategoriler:
- yorum: Ürün yorumları ve değerlendirmeler
- ozel_talep: Özel sipariş talepleri
- teknik: Teknik destek ve arıza bildirimleri
- yanlis_hasarli: Hasarlı/yanlış ürün şikayetleri
- orijinallik: Ürün orijinallik sorguları
- iade_degisim: İade ve değişim talepleri
- stok: Stok durumu sorguları
- kargo_bilgileri: Kargo firma ve takip bilgileri
- siparis_teslimat: Sipariş ve teslimat durum sorguları
"""

import json
import os
import re
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from collections import Counter, deque

# sentence-transformers kütüphanesini kontrol et
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False

class AICategorizer:
    """
    AI Tabanlı Soru Kategorizasyon Sistemi
    
    Bu sınıf, sentence-transformers kütüphanesini kullanarak
    kullanıcı sorularını kategorize eder. Embedding tabanlı
    cosine similarity algoritması ile çalışır.
    
    Attributes:
        model: SentenceTransformer modeli
        categories: Kategori ID'leri ve isimleri
        category_examples: Her kategori için örnek sorular
        category_embeddings: Önceden hesaplanmış kategori embedding'leri
    """
    
    def __init__(self):
        """
        AICategorizer sınıfını başlatır
        
        - sentence-transformers kontrolü yapar
        - Embedding modelini yükler
        - Kategori tanımlarını yükler
        - Kategori embedding'lerini hesaplar
        
        Raises:
            ImportError: sentence-transformers bulunamazsa
            RuntimeError: Model yüklenemezse veya embedding hesaplanamazsa
        """
        print("AI Tabanlı Embedding Kategorizasyon Sistemi Başlatılıyor...")
        
        # sentence-transformers zorunlu kontrol
        if not EMBEDDING_AVAILABLE:
            error_msg = "HATA: sentence-transformers kütüphanesi bulunamadı!"
            print(error_msg)
            print("Yüklemek için: pip install sentence-transformers")
            raise ImportError("sentence-transformers kütüphanesi gerekli!")
        
        # Embedding modeli yükle (CPU optimized model)
        try:
            print("Embedding modeli yükleniyor...")
            # all-MiniLM-L6-v2: Hafif, hızlı, çok dilli destek
            self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            print("Embedding modeli yüklendi")
        except Exception as e:
            error_msg = f"HATA: Embedding modeli yüklenemedi: {e}"
            print(error_msg)
            raise RuntimeError(f"Embedding modeli yükleme hatası: {e}")
        
        # Kategori tanımları - ID ve görünen isim eşleşmesi
        self.categories = {
            'yorum': 'yorum',                                    
            'ozel_talep': 'özel talep',                       
            'teknik': 'teknik',                                
            'yanlis_hasarli': 'Yanlış veya hasarlı ürün',     
            'orijinallik': 'Orijinallik',                     
            'iade_degisim': 'İade ve değişim',            
            'stok': 'stok',                                   
            'kargo_bilgileri': 'Kargo bilgileri',             
            'siparis_teslimat': 'Sipariş teslimat bilgileri'  
        }
        
        # Her kategori için eğitim örnekleri
        # Bu örnekler embedding hesaplamasında kullanılır
        # Türkçe ve İngilizce karışık destek
        self.category_examples = {
        'yorum': [
            'Bu ürün çok güzel, beğendim',
            'Ürün hakkında yorum yapabilir misiniz?',
            'Bu ürün kaliteli mi?',
            'Kullanıcı değerlendirmeleri nasıl?',
            'Ürün performansı nasıl?',
            'Bu ürünü tavsiye eder misiniz?',
            'Ürün beklentilerimi karşıladı mı?',
            'Başka kullanıcıların görüşleri nedir?',
            'Ürün hakkındaki genel yorumlar nelerdir?',
            'Ürün hakkında olumlu ve olumsuz yorumlar neler?',
            'Kullanıcıların genel memnuniyeti nedir?'
        ],
        'ozel_talep': [
            'Özel bir renk istiyorum',
            'Farklı boyutta sipariş verebilir miyim?',
            'Özel paketleme yapabilir misiniz?',
            'Kişiselleştirilmiş ürün alabilir miyim?',
            'Özel sipariş verebilir miyim?',
            'Farklı model istiyorum',
            'Ürün üzerinde değişiklik yapılabilir mi?',
            'Kişiye özel tasarım mümkün mü?',
            'Ürünü istediğim şekilde özelleştirebilir miyim?',
            'Ekstra aksesuar ekleyebilir miyim?',
            'Ürün üzerinde isim yazdırabilir miyim?'
        ],
        'teknik': [
            'Ürün çalışmıyor, yardım edin',
            'Teknik destek alabilir miyim?',
            'Garanti kapsamında mı?',
            'Servis merkezi nerede?',
            'Ürün arızalı',
            'Teknik sorun yaşıyorum',
            'Ürünün özellikleri hakkında detaylı bilgi alabilir miyim?',
            'Ürün güncelleme veya yazılım desteği var mı?',
            'Cihaz açılmıyor, ne yapmalıyım?',
            'Ürünün garantisi ne kadar?',
            'Teknik kullanım kılavuzu var mı?',
            'Ürünle ilgili sık karşılaşılan teknik sorunlar nelerdir?'
        ],
        'yanlis_hasarli': [
            'Ürün hasarlı geldi',
            'Yanlış ürün gönderildi',
            'Ürün kırık geldi',
            'Eksik parça var',
            'Ürün bozuk geldi',
            'Hatalı ürün aldım',
            'Paketleme yeterli değildi, ürün zarar gördü',
            'Yanlış model gönderilmiş',
            'Ürün beklediğimden farklı ve hasarlı',
            'Ürün tesliminde problem yaşadım',
            'Paket teslim edilirken zarar görmüş'
        ],
        'orijinallik': [
            'Bu ürün orijinal mi?',
            'Sahte ürün mü?',
            'Gerçek ürün mü?',
            'Orijinal değil mi?',
            'Bu ürün sahte mi?',
            'Orijinal ürün mü?',
            'Ürünün garantisi var mı?',
            'Markanın lisanslı ürünü mü?',
            'Ürün sertifikalı mı?',
            'Ürünle ilgili sahtecilik şüphesi var mı?',
            'Ürünün üreticisi kimdir?'
        ],
        'iade_degisim': [
            'İade etmek istiyorum',
            'Değiştirmek istiyorum',
            'Para iadesi alabilir miyim?',
            'İade şartları neler?',
            'Ürünü değiştirmek istiyorum',
            'İade nasıl yapılır?',
            'Ürünü iade etmek için ne yapmalıyım?',
            'Ürün değişimi mümkün mü?',
            'İade süreci ne kadar sürüyor?',
            'Ürün teslim aldıktan sonra iade edebilir miyim?',
            'İade kargo kodu nereden alınır?'
        ],
        'stok': [
            'Bu ürün stokta var mı?',
            'Kaç tane kaldı?',
            'Stok durumu nasıl?',
            'Ne zaman gelir?',
            'Bu ürün mevcut mu?',
            'Stokta kaç tane var?',
            'Ürün tekrar stoklara ne zaman gelecek?',
            'Sipariş vermek için stok yeterli mi?',
            'Stok durumu hakkında bilgi alabilir miyim?',
            'Ürün stokta kalmadı mı?',
            'Stok yenileme süresi nedir?'
        ],
        'kargo_bilgileri': [
            'Hangi kargo firması?',
            'kargo', 'kargo firması', 'kargo ile gönderiyorsunuz',
            # Kargo firmaları - çok detaylı
            'mng', 'mng kargo', 'mng ile', 'mng kargo ile gönderim',
            'yurtiçi', 'yurtiçi kargo', 'yurtici', 'yurtiçi ile',
            'hepsijet', 'hepsijet kargo', 'hepsijet ile',
            'aras', 'aras kargo', 'aras ile gönderim',
            'dpd', 'dpd kargo', 'dpd ile',
            'dhl', 'dhl kargo', 'dhl ile gönderim',
            'kargoist', 'kargoist ile', 'kargoist kargo',
            'ptt', 'ptt kargo', 'ptt ile',
            'kargomsende', 'kargomsende kargo', 'kargomsende ile',
            'Kargo takip numarası nedir?',
            'Kargo durumu nasıl?',
            'Kargo bilgisi alabilir miyim?',
            'Kargo firması hangisi?',
            'Kargo takibi yapabilir miyim?',
            'Kargom ne zaman teslim edilir?',
            'Gönderim süresi nedir?',
            'Kargo teslimatında sorun yaşadım',
            'Kargo ile ilgili detaylı bilgi verebilir misiniz?',
            'Kargo teslimat adresini değiştirebilir miyim?',
            'Kargo gecikmesi ile ilgili bilgi almak istiyorum'
        ],
        'siparis_teslimat': [
            'Siparişim ne zaman teslim edilecek?',
            'Ne zaman gelir?',
            'Teslimat süresi nedir?',
            'Sipariş durumu nasıl?',
            'Siparişim ne zaman gelir?',
            'Teslimat ne zaman?',
            'Siparişimin durumu hakkında bilgi verir misiniz?',
            'Sipariş teslimatı gecikiyor',
            'Ürün teslimat adresimi değiştirebilir miyim?',
            'Siparişimin kargoya verilme süresi nedir?',
            'Siparişle ilgili gecikme yaşanıyor mu?'
        ]
    }

        
        # Kategori embedding'lerini önceden hesapla
        # Bu işlem performans için kritik
        self.category_embeddings = {}
        self._calculate_category_embeddings()
        
        print(f"{len(self.categories)} kategori tanımlandı")
    
    def _calculate_category_embeddings(self):
        """
        Her kategori için örnek cümlelerin embedding'lerini hesaplar
        
        Bu metod:
        1. Her kategorideki örnek cümlelerin embedding'ini hesaplar
        2. Ortalama embedding alarak kategori temsilcisi oluşturur
        3. Bu embedding'leri cache'de saklar (self.category_embeddings)
        
        Cache sayesinde her soru için sadece soru embedding'i hesaplanır,
        kategori embedding'leri tekrar hesaplanmaz.
        
        Raises:
            RuntimeError: Embedding hesaplama hatası durumunda
        """
        print("Kategori embedding'leri hesaplanıyor...")
        try:
            for category_id, examples in self.category_examples.items():
                # Her örnek cümle için 384 boyutlu embedding hesapla
                embeddings = self.model.encode(examples)
                
                # Tüm örneklerin ortalamasını al -> kategori temsilcisi
                avg_embedding = np.mean(embeddings, axis=0)
                
                # Cache'e kaydet
                self.category_embeddings[category_id] = avg_embedding
                
            print("Embedding'ler hesaplandı")
        except Exception as e:
            error_msg = f"HATA: Embedding hesaplama hatası: {e}"
            print(error_msg)
            raise RuntimeError(f"Embedding hesaplama hatası: {e}")
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        İki vektör arasındaki cosine similarity hesaplar
        
        Cosine similarity, iki vektör arasındaki açının kosinüsünü
        hesaplayarak benzerlik ölçer. -1 ile 1 arasında değer alır:
        -  1: Tamamen benzer (aynı yön)
        -  0: Hiç benzer değil (dik açı) 
        - -1: Tamamen zıt (ters yön)
        
        Formül: cos(θ) = (A·B) / (||A|| × ||B||)
        
        Args:
            vec1: İlk vektör (numpy array)
            vec2: İkinci vektör (numpy array)
            
        Returns:
            float: -1 ile 1 arasında benzerlik skoru
        """
        # Dot product (nokta çarpım)
        dot_product = np.dot(vec1, vec2)
        
        # Vektör uzunlukları (L2 norm)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        # Sıfır vektör kontrolü
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Cosine similarity hesapla
        return dot_product / (norm1 * norm2)
    
    def categorize_question(self, question: str) -> Dict:
        """
        Soruyu kategorize eder - Ana fonksiyon
        
        Bu fonksiyon:
        1. Boş soru kontrolü yapar
        2. Sorunun embedding'ini hesaplar
        3. Her kategori ile cosine similarity hesaplar
        4. En yüksek skorlu kategoriyi seçer
        6. Sonucu structured format'ta döndürür
        
        Args:
            question (str): Kategorize edilecek soru
            
        Returns:
            Dict: Kategorizasyon sonucu
                {
                    "category": str,           # Kategori ID
                    "category_name": str,      # Kategori görünen ismi
                    "confidence": float,       # Güven skoru (0-1)
                    "method": str,             # Kullanılan metod
                    "similarities": Dict,      # Tüm kategorilerle benzerlik
                    "is_high_similarity": bool # Yüksek benzerlik flag (≥0.7)
                }
                
        Raises:
            RuntimeError: Embedding hesaplama veya kategorizasyon hatası
        """
        # Boş soru kontrolü
        if not question.strip():
            return {
                'category': 'genel',
                'category_name': 'Genel Soru',
                'confidence': 0.1,
                'method': 'empty',
                'is_high_similarity': False
            }
        
        try:
            # Sorunun embedding'ini hesapla (384 boyutlu vektör)
            question_embedding = self.model.encode([question])[0]
            
            # Her kategori ile benzerlik hesapla
            similarities = {}
            for category_id, category_embedding in self.category_embeddings.items():
                # Cosine similarity hesapla (-1 ile 1 arası)
                similarity = self.cosine_similarity(question_embedding, category_embedding)
                similarities[category_id] = similarity
            
            # Benzerlik skorları varsa en iyisini seç
            if similarities:
                # En yüksek skorlu kategoriyi bul
                best_category = max(similarities, key=similarities.get)
                confidence = similarities[best_category]
                
                return {
                    'category': best_category,
                    'category_name': self.categories[best_category],
                    'confidence': float(confidence),
                    'method': 'embedding',
                    'similarities': {k: float(v) for k, v in similarities.items()},
                }
            else:
                # Hiç benzerlik bulunamazsa genel kategori döndür
                return {
                    'category': 'genel',
                    'category_name': 'Genel Soru',
                    'confidence': 0.1,
                    'method': 'embedding',
                    'similarities': {},
                }
                
        except Exception as e:
            error_msg = f"HATA: Kategorizasyon hatası: {e}"
            print(error_msg)
            raise RuntimeError(f"Kategorizasyon hatası: {e}") 