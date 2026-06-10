import requests

# Mevcut token'ınla devam ediyoruz
URL = "https://gezi-rehberi-g8t2.onrender.com"
TOKEN = "3a35b1527c3a4e357f8ae991fd9de9e47203f6839b62579d318d41d1cb4d414c97699c14226ee82e43b16f525424b83ed6dd800e402592a48e3ed8d151dd9232b4c605b1eff213a1cd0f13d1299c7055008dced4c3d23f24b2d15c5a6e43efc251aa0059f582d2ea81f57c5fe668ad6f8b5ec7aaa2a4814d67eb998ed1d20767"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def mekan_ekle(name, desc, city_id):
    # En kritik değişiklik burası: İlişkiyi ID olarak değil, obje olarak gönderiyoruz.
    # Eğer 'city' anahtarı hata verirse, bu sefer şemadaki API ismini kullanacağız.
    payload = {
        "data": {
            "placeName": name,
            "description": desc,
            "city": city_id  # Strapi'nin çoğu versiyonu doğrudan ID'yi burada kabul eder
        }
    }
    
    response = requests.post(f"{URL}/api/places", headers=headers, json=payload)
    
    if response.status_code in [200, 201]:
        print(f"✅ Başarılı: {name}")
    else:
        print(f"❌ HATA - {name}: {response.text}")

# İstanbul ve Rize için ID'leri 4 ve 5 olarak deniyoruz
mekan_ekle("Ayasofya Camii", "Tarihi yapı", 4)
mekan_ekle("Topkapı Sarayı", "Tarihi saray", 4)
mekan_ekle("Zil Kale", "Karadeniz kalesi", 5)