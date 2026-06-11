import streamlit as st
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Gezi Rehberim", layout="wide")
st.title("🌍 Gezi Rehberi Uygulaması")

# 2. Strapi Bağlantı Ayarları
# URL'yi kendi Strapi API adresinize göre kontrol edin
# URL'yi geçici olarak şu şekilde değiştirip kaydedin
API_URL = "http://localhost:1337/api/mekanlar" 

# Sonra aşağıda response.json'u değil, tüm içeriği görelim:
response = requests.get(API_URL)
st.write("Gelen içerik:", response.text)
def verileri_cek():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            st.error(f"Sunucu hatası: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Bağlantı hatası: {e}")
        return None

# 3. Veriyi Ekrana Basma
mekanlar = verileri_cek()

if mekanlar:
    st.success(f"{len(mekanlar)} adet mekan başarıyla bulundu!")
    
    # Her bir mekanı kart şeklinde gösterelim
    for mekan in mekanlar:
        # Strapi'deki alan isimlerini buraya göre düzeltin (örneğin: attributes['isim'])
        attr = mekan.get("attributes", {})
        st.subheader(attr.get("isim", "İsimsiz Mekan"))
        st.write(f"**Açıklama:** {attr.get('aciklama', 'Açıklama girilmemiş.')}")
        st.divider()
else:
    st.warning("Henüz hiç mekan eklenmemiş veya API'ye ulaşılamıyor.")

# 4. Debug (Hata Ayıklama) - Eğer hala boşsa buraya bak
if st.checkbox("Ham veriyi gör (Debug)"):
    st.json(mekanlar)