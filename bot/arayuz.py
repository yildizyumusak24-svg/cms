import streamlit as str_ui
import requests

# API Ayarları
STRAPI_URL = "http://localhost:1337"  # Portun 1338 ise burayı 1338 yap

# Sayfa Tasarımı ve Başlık
str_ui.set_page_config(page_title=" Gezi Rehberi", page_icon="🌍", layout="wide")
str_ui.title("🌍 Gezi Rehberi")
str_ui.write("Şehirler ve tarihi yerleri ile zenginleştirilmiş mekan rehberi.")

# ==========================================
# STRAPI'DEN VERİ ÇEKME FONKSİYONLARI
# ==========================================
def sehirleri_getir():
    try:
        response = requests.get(f"{STRAPI_URL}/api/cities")
        if response.status_code == 200:
            return response.json().get("data", [])
    except Exception as e:
        str_ui.error(f"Şehirler çekilirken hata oluştu: {e}")
    return []

def sehir_mekanlarini_getir(sehir_id):
    try:
        # Sonuna eklediğimiz ?populate=* sayesinde Strapi mekanın içindeki şehir bağını ve görselleri dışarıya açar
        response = requests.get(f"{STRAPI_URL}/api/places?populate=*")
        if response.status_code == 200:
            tum_mekanlar = response.json().get("data", [])
            
            # Mekanları seçilen şehre göre filtreleme (v4 ve v5 uyumlu güvenli kontrol)
            sehir_mekanlari = []
            for mekan in tum_mekanlar:
                attr = mekan["attributes"] if "attributes" in mekan else mekan
                
                # Mekanın bağlı olduğu şehir bilgisini kontrol et
                sehir_verisi = attr.get("city", {})
                if isinstance(sehir_verisi, dict) and "data" in sehir_verisi and sehir_verisi["data"]:
                    # v4 yapısı için ilişki kontrolü
                    if sehir_verisi["data"]["id"] == sehir_id:
                        sehir_mekanlari.append(mekan)
                elif isinstance(sehir_verisi, dict) and sehir_verisi.get("id") == sehir_id:
                    # v5 yapısı için doğrudan ilişki kontrolü
                    sehir_mekanlari.append(mekan)
                    
            return sehir_mekanlari
    except Exception as e:
        print(f"Mekanlar çekilirken hata: {e}")
    return []
# ==========================================
# ARAYÜZ OLUŞTURMA VE LİSTELEME (STRAPI v5 UYUMLU)
# ==========================================
sehirler = sehirleri_getir()

if sehirler:
    try:
        # Strapi v5 doğrudan veriyi döndürdüğü için ["attributes"] kısmını kaldırdık
        sehir_secenekleri = {}
        for sehir in sehirler:
            # Hem v4 hem v5 uyumlu olması için güvenli kontrol yapıyoruz
            if "attributes" in sehir:
                adi = sehir["attributes"].get("cityName", "İsimsiz")
            else:
                adi = sehir.get("cityName", "İsimsiz")
            
            sehir_secenekleri[adi] = sehir["id"]
            
        secilen_sehir_adi = str_ui.selectbox("Keşfetmek istediğiniz şehri seçin:", list(sehir_secenekleri.keys()))
        secilen_sehir_id = sehir_secenekleri[secilen_sehir_adi]
        
        str_ui.subheader(f"📍 {secilen_sehir_adi} Gezi Noktaları")
        
        # Seçilen şehre ait mekanları veri tabanından getir
        mekanlar = sehir_mekanlarini_getir(secilen_sehir_id)
        
        if mekanlar:
            for mekan in mekanlar:
                # Mekan verisi için de v4/v5 güvenlik kontrolü
                if "attributes" in mekan:
                    attr = mekan["attributes"]
                else:
                    attr = mekan
                
                with str_ui.container():
                    col1, col2 = str_ui.columns([1, 2])
                    
                    with col1:
                        try:
                            # Strapi'ye yeni eklediğimiz düz metin alanını okuyoruz
                            gorsel_linki = attr.get("Gorsel_Link") or attr.get("gorsel_link")
                            
                            # Eğer kutuya bir link yapıştırıldıysa onu kullan
                            if gorsel_linki and isinstance(gorsel_linki, str) and gorsel_linki.startswith("http"):
                                str_ui.image(gorsel_linki, use_container_width=True)
                            else:
                                # Eğer kutu boş bırakıldıysa varsayılan manzara resmini göster
                                str_ui.image("https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=500", use_container_width=True)
                                
                        except Exception as e:
                            str_ui.image("https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=500", use_container_width=True)
                            
                    with col2:
                        # Strapi'deki olası tüm alan adı varyasyonlarını (büyük/küçük harf) yakalıyoruz
                        mekan_ismi = attr.get('placeName') or attr.get('placeName') or attr.get('Name') or attr.get('name') or 'İsimsiz Mekan'
                        mekan_puani = attr.get('Puan') or attr.get('puan') or attr.get('Rating') or '-'
                        mekan_aciklama = attr.get('Aciklama') or attr.get('aciklama') or attr.get('Description') or 'Açıklama bulunmuyor.'
                        
                        str_ui.markdown(f"### {mekan_ismi}")
                        str_ui.write(f"⭐ **Puan:** {mekan_puani}/5")
                        str_ui.write(mekan_aciklama)
                    
                    str_ui.markdown("---")
        else:
            str_ui.info("Bu şehre ait henüz bir mekan kaydı bulunamadı. Strapi panelinden ekleyebilirsiniz!")
            
    except Exception as e:
        str_ui.error(f"Arayüz render hatası: {e}")
else:
    str_ui.warning("Veri tabanında henüz kayıtlı şehir bulunamadı. Lütfen önce Strapi panelinden manuel olarak bir şehir ekleyin.")