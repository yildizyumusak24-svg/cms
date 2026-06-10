import streamlit as st
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

# .env dosyasındaki değişkenleri yükle
load_dotenv()

# --- AYARLAR ---
# Token'ları çevresel değişkenlerden okuyoruz
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
STRAPI_TOKEN = os.getenv("STRAPI_API_TOKEN")
STRAPI_URL = "https://gezi-rehberi-g8t2.onrender.com/api"

# GROQ İstemci Kurulumu
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

st.set_page_config(page_title="YZ Destekli Gezi Rehberi", layout="wide")
st.markdown("<h1 style='text-align: center;'>🌍 YZ Destekli Gezi Rehberi</h1>", unsafe_allow_html=True)

# --- FONKSİYONLAR ---
def veri_hazirla_ve_kaydet(sehir, mekan):
    prompt = f"{sehir} şehrindeki {mekan} hakkında Türkçe ve İngilizce detaylı bilgi yaz."
    response = client.chat.completions.create(
        model="llama3-8b-8192", 
        messages=[{"role": "user", "content": prompt}]
    )
    icerik = response.choices[0].message.content
    
    headers = {"Authorization": f"Bearer {STRAPI_TOKEN}"}
    payload = {
        "data": {
            "Mekan_Adi": mekan,
            "Aciklama": icerik,
            "Gorsel_URL": f"https://image.pollinations.ai/prompt/{mekan.replace(' ', '%20')}"
        }
    }
    
    response = requests.post(f"{STRAPI_URL}/mekanlars", json=payload, headers=headers)
    return response.status_code, icerik

# --- ARAYÜZ ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Yeni Mekan Ekle")
    sehir_input = st.text_input("Şehir:")
    mekan_input = st.text_input("Mekan:")

    if st.button("Veriyi YZ ile İşle ve Kaydet"):
        if sehir_input and mekan_input:
            with st.spinner("YZ içeriği üretiliyor..."):
                status, sonuc = veri_hazirla_ve_kaydet(sehir_input, mekan_input)
                if status in [200, 201]:
                    st.success("Başarıyla Strapi'ye kaydedildi!")
                else:
                    st.error(f"Hata oluştu! Kod: {status}")
        else:
            st.warning("Lütfen alanları doldurun.")

with col2:
    st.subheader("Mekanları Listele")
    if st.button("Mekanları Strapi'den Çek"):
        headers = {"Authorization": f"Bearer {STRAPI_TOKEN}"}
        response = requests.get(f"{STRAPI_URL}/mekanlars?populate=*", headers=headers)
        if response.status_code == 200:
            for m in response.json().get('data', []):
                attr = m.get('attributes', {})
                st.write(f"### {attr.get('Mekan_Adi')}")
                st.image(attr.get('Gorsel_URL'), use_container_width=True)
                st.write(attr.get('Aciklama'))
                st.divider()
        else:
            st.error("Veriler çekilemedi.")