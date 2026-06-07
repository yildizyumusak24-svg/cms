import requests
from deep_translator import GoogleTranslator

# ==========================================
# 1. API, PORT VE BAĞLANTI AYARLARI
# ==========================================
# Eğer Strapi portunu 1338 yaptıysan aşağıdaki adresi http://localhost:1338 yap
STRAPI_URL = "http://localhost:1337"  
STRAPI_TOKEN = "baef5bf6fe064580680b0fee4e4e4921a6a7f4ba574b0d8eec341c117bc160e19e9a584aeb3f70ff3cafa393dc665430d61204075ea1d4af56ee3f1e8038696f33eb0a71d0674f7fe6f9e3a87119cc97ee03b6520fc5f59d40dd17f528c4da72564f05e669ad67edc689811884710927c0eba34bc30f6a38bc5f21da4805eb32" 

headers = {
    "Authorization": f"Bearer {STRAPI_TOKEN}"
}

# ==========================================
# 2. ÇEVİRİ MOTORU (TR -> EN)
# ==========================================
def metni_ingilizceye_cevir(metin):
    print("Mekan açıklaması İngilizceye çevriliyor...")
    try:
        cevirilen_metin = GoogleTranslator(source='tr', target='en').translate(metin)
        print("✓ Çeviri başarıyla tamamlandı.")
        return cevirilen_metin
    except Exception as e:
        print(f"⚠ Çeviri hatası oluştu, orijinal metin kullanılacak: {e}")
        return metin

# ==========================================
# 3. GÜVENLİ YAPAY ZEKÂ GÖRSEL ÜRETİCİ (HATA KORUMALI)
# ==========================================
def yz_gorsel_uret(mekan_adi):
    print(f"{mekan_adi} için yapay zekâ görseli hazırlanıyor...")
    
    # URL uyumluluğu için Türkçe karakterleri temizleme
    temiz_isim = mekan_adi.lower()
    turkce_karakterler = str.maketrans("çğıöşü ", "cgiosu_")
    temiz_isim = temiz_isim.translate(turkce_karakterler)
    
    # Birincil kaynak: Yapay Zekâ Motoru
    gorsel_url = f"https://image.pollinations.ai/p/{temiz_isim}_historical_travel_scenery"
    
    headers_gorsel = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(gorsel_url, headers=headers_gorsel, timeout=20)
        
        # Eğer yapay zekâ sunucusu başarıyla yanıt verdiyse (Kod 200 ise)
        if response.status_code == 200:
            dosya_yolu = f"{temiz_isim}.jpg"
            with open(dosya_yolu, "wb") as f:
                f.write(response.content)
            print("✓ Görsel yapay zekâ tarafından başarıyla üretildi ve indirildi.")
            return dosya_yolu
            
        # Eğer yapay zekâ sunucusu hata verdiyse (Örn: 402 Kotası dolduysa)
        else:
            print(f"⚠ YZ Sunucusu kota/hata kodu verdi ({response.status_code}).")
            print("🔄 Otomasyonun aksamaması için yedek görsel mekanizması devreye giriyor...")
            
            # YEDEK MEKANİZMA: Unsplash üzerinden telifsiz seyahat görseli çekiyoruz
            yedek_url = "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=800&q=80"
            yedek_response = requests.get(yedek_url, headers=headers_gorsel, timeout=15)
            
            if yedek_response.status_code == 200:
                dosya_yolu = f"{temiz_isim}_yedek.jpg"
                with open(dosya_yolu, "wb") as f:
                    f.write(yedek_response.content)
                print("✓ Yedek manzara görseli başarıyla temin edildi.")
                return dosya_yolu
            else:
                print("❌ Yedek görsel de alınamadı.")
                return None
                
    except Exception as e:
        print(f"❌ Görsel motorunda beklenmeyen bağlantı hatası: {e}")
        return None

# ==========================================
# 4. STRAPI MEDIA LIBRARY YÜKLEME MOTORU (DÜZELTİLDİ)
# ==========================================
def strapiye_gorsel_yukle(dosya_yolu):
    print("Görsel Strapi Media Library'ye aktarılıyor...")
    upload_url = f"{STRAPI_URL}/api/upload"
    
    try:
        # Dosyayı ikili (binary) modda açıyoruz
        with open(dosya_yolu, "rb") as f:
            # Strapi dosyayı mutlaka 'files' anahtarı altında bekler
            files = {
                "files": (dosya_yolu, f, "image/jpeg")
            }
            # Dosya gönderirken Content-Type başlığını requests kütüphanesi kendisi otomatik doldurmalıdır.
            # Bu yüzden sadece Authorization başlığını yalın olarak gönderiyoruz.
            upload_headers = {
                "Authorization": f"Bearer {STRAPI_TOKEN}"
            }
            
            response = requests.post(upload_url, headers=upload_headers, files=files)
            
        if response.status_code in [200, 201]:
            gorsel_id = response.json()[0]["id"]
            print(f"✓ Görsel Strapi'ye yüklendi. Medya ID: {gorsel_id}")
            return gorsel_id
        else:
            print(f"❌ Görsel Medya Kütüphanesine yüklenemedi. Durum Kodu: {response.status_code}")
            print(f"Sunucu Yanıtı: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Medya sunucusuna bağlanılamadı: {e}")
        return None

# ==========================================
# 5. STRAPI VERİ TABANINA KAYIT MOTORU
# ==========================================
def strapiye_mekan_ekle(mekan_adi, aciklama_tr, aciklama_en, puan, gorsel_id, sehir_id):
    print(f"{mekan_adi} tüm paket verileriyle Strapi'ye kaydediliyor...")
    places_url = f"{STRAPI_URL}/api/places"
    
    # Strapi Yapısına ve Alan İsimlerine Tam Uyumlu Veri Paketi
    veri_paketi = {
        "data": {
            "Mekan_Adi": mekan_adi,
            "Aciklama": aciklama_tr,       # Varsayılan Dil (TR)
            "Puan": puan,
            "Kapak_Resmi": gorsel_id,      # İlişkili Görsel ID'si
            "City": sehir_id,              # Bağlı Olduğu Şehir ID'si
            "localizations": [
                {
                    "locale": "en",        # İkinci Dil Desteği (EN)
                    "Aciklama": aciklama_en
                }
            ]
        }
    }
    
    try:
        response = requests.post(places_url, headers=headers, json=veri_paketi)
        if response.status_code in [200, 201]:
            print(f"\n✨ BAŞARILI: {mekan_adi} tüm dillerde ve görseliyle Strapi'ye kaydedildi!")
        else:
            print(f"❌ Veri tabanına kaydetme başarısız: {response.text}")
    except Exception as e:
        print(f"❌ Strapi API bağlantı hatası: {e}")

# ==========================================
# 6. TEK TUŞLA ÇALIŞTIRMA VE TEST ALANI
# ==========================================
if __name__ == "__main__":
    
    # ⚠️ DIKKAT: Strapi Yönetim Panelinde "Cities" (Şehirler) alanına eklediğin 
    # geçerli bir şehrin ID numarasını buraya yazmalısın. (Örn: 1 veya 2)
    HEDEF_SEHIR_ID = 3 
    
    # Eklenecek örnek mekan verileri
    ornek_mekan = "Ayasofya Camii"
    ornek_aciklama = "Istanbul'un tarihi ve en onemli sembol yapilarindan biridir."
    ornek_puan = 5

    print(f"=== OTO-MOTOR: {ornek_mekan} İçin Döngü Başlatıldı ===")
    
    # Adım 1: Çeviri Yapılıyor
    ingilizce_aciklama = metni_ingilizceye_cevir(ornek_aciklama)
    print(f"-> Çeviri Sonucu: {ingilizce_aciklama}\n")
    
    # Adım 2: Yapay Zekâ Görseli Üretiliyor ve İndiriliyor
    indirilen_gorsel_yolu = yz_gorsel_uret(ornek_mekan)
    
    # Adım 3 & 4: Görsel indirildiyse Strapi'ye yükle ve veriyi kaydet
    if indirilen_gorsel_yolu:
        medya_id = strapiye_gorsel_yukle(indirilen_gorsel_yolu)
        
        if medya_id:
            strapiye_mekan_ekle(
                mekan_adi=ornek_mekan,
                aciklama_tr=ornek_aciklama,
                aciklama_en=ingilizce_aciklama,
                puan=ornek_puan,
                gorsel_id=medya_id,
                sehir_id=HEDEF_SEHIR_ID
            )
        else:
            print("⚠ Görsel Strapi'ye yüklenemediği için işlem iptal edildi.")
    else:
        print("⚠ Görsel üretilemediği için veri tabanına kayıt adımına geçilemedi.")