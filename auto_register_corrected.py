#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, date
import random

# Website URL'si
BASE_URL = "http://192.168.1.5:5008"
REGISTER_URL = f"{BASE_URL}/community/register"

def generate_user_data(index):
    """Her kayıt için benzersiz kullanıcı verisi oluştur"""
    
    names = ["Ahmet", "Mehmet", "Ali", "Veli", "Fatma", "Ayşe", "Zeynep", "Elif", "Emre", "Burak"]
    surnames = ["Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Özkan", "Arslan", "Doğan", "Kılıç", "Aydın"]
    cities = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Adana", "Konya", "Gaziantep", "Mersin", "Kayseri"]
    faculties = ["Mühendislik Fakültesi", "Tıp Fakültesi", "İktisadi ve İdari Bilimler Fakültesi", "Fen Fakültesi", "Edebiyat Fakültesi"]
    departments = ["Bilgisayar Mühendisliği", "Elektrik Mühendisliği", "Makine Mühendisliği", "İşletme", "Matematik", "Fizik", "Türk Dili ve Edebiyatı"]
    classes = ["1. Sınıf", "2. Sınıf", "3. Sınıf", "4. Sınıf"]
    units = [["drawing_unit"], ["cosplay_unit"], ["social_media_unit"], ["translation_fansub"], ["ninjutsu_unit"]]
    
    name = random.choice(names)
    surname = random.choice(surnames)
    username = f"{name.lower()}{surname.lower()}{index:03d}"
    
    # Rastgele doğum tarihi (18-25 yaş arası)
    birth_year = random.randint(1999, 2006)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    birth_date = date(birth_year, birth_month, birth_day)
    
    student_id = f"211{random.randint(10000, 99999)}"
    # Telefon numarası düzeltme - 13 haneli olmalı (+90 dahil)
    phone = f"+905{random.randint(100000000, 999999999)}"  # +90 + 5 + 9 haneli sayı = 13 haneli
    
    user_data = {
        'username': username,
        'password': 'Test123!',
        'password2': 'Test123!',
        'email': f"{username}@hacettepe.edu.tr",
        'name': name,
        'surname': surname,
        'place_of_birth': random.choice(cities),
        'date_of_birth': birth_date.strftime('%Y-%m-%d'),
        'current_residence': random.choice(cities),
        'student_id': student_id,
        'phone_number': phone,
        'student_class': random.choice(classes),
        'faculty': random.choice(faculties),
        'department': random.choice(departments),
        'preferred_units': random.choice(units)
    }
    
    return user_data

def register_single_user(user_data, max_retries=3):
    """Rate limiting ile baş etmek için retry mekanizması"""
    
    for attempt in range(max_retries):
        print(f"🔄 Deneme {attempt + 1}/{max_retries}")
        
        # Her deneme için yeni session
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        try:
            print("🔍 GET request ile form alınıyor...")
            
            # Daha uzun timeout
            response = session.get(REGISTER_URL, timeout=30)
            print(f"📡 GET Response: {response.status_code}")
            
            if response.status_code == 429:
                wait_time = (attempt + 1) * 60  # Her denemede bekleme süresini artır
                print(f"⏳ Rate limit! {wait_time} saniye bekleniyor...")
                time.sleep(wait_time)
                continue
            elif response.status_code != 200:
                print(f"❌ GET Request başarısız: {response.status_code}")
                continue
            
            # CSRF token bul
            soup = BeautifulSoup(response.content, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrf_token'})
            
            if not csrf_input:
                print("❌ CSRF token bulunamadı")
                continue
                
            csrf_token = csrf_input.get('value')
            print(f"🔑 CSRF token: {csrf_token[:20]}...")
            
            # Form verilerini hazırla
            form_data = {
                'csrf_token': csrf_token,
                'username': user_data['username'],
                'password': user_data['password'],
                'password2': user_data['password2'],
                'email': user_data['email'],
                'name': user_data['name'],
                'surname': user_data['surname'],
                'place_of_birth': user_data['place_of_birth'],
                'date_of_birth': user_data['date_of_birth'],
                'current_residence': user_data['current_residence'],
                'student_id': user_data['student_id'],
                'phone_number': user_data['phone_number'],
                'student_class': user_data['student_class'],
                'faculty': user_data['faculty'],
                'department': user_data['department'],
                'preferred_units': user_data['preferred_units'][0] if user_data['preferred_units'] else '',
                'submit': 'Topluluk Üyeliği İçin Başvur'
            }
            
            print(f"📞 Telefon: {user_data['phone_number']} (Uzunluk: {len(user_data['phone_number'])})")
            print("📤 POST request gönderiliyor...")
            
            # POST request
            post_response = session.post(REGISTER_URL, data=form_data, timeout=30)
            print(f"📡 POST Response: {post_response.status_code}")
            
            if post_response.status_code == 429:
                wait_time = (attempt + 1) * 60
                print(f"⏳ Rate limit! {wait_time} saniye bekleniyor...")
                time.sleep(wait_time)
                continue
            elif post_response.status_code == 200:
                response_text = post_response.text
                
                # Debug: Response'u kontrol et - sadece hata varsa kaydet
                if "başarıyla alındı" in response_text:
                    print("✅ Kayıt başarılı!")
                    return True, "Başarılı"
                elif "zaten kayıtlı" in response_text:
                    print("⚠️ Bu bilgiler zaten kayıtlı")
                    return False, "Zaten kayıtlı"
                elif "alert-danger" in response_text or "error" in response_text.lower():
                    # Hata ayrıntılarını kaydet
                    with open(f'debug_response_{user_data["username"]}.html', 'w', encoding='utf-8') as f:
                        f.write(response_text)
                    print(f"❌ Form hatası - debug dosyası kaydedildi")
                    return False, "Form validasyon hatası"
                else:
                    # Başarılı olabilir - kayıt sayfası geri dönüyor olabilir
                    print("✅ Muhtemelen başarılı (form sayfası döndü)")
                    return True, "Başarılı olabilir"
            else:
                print(f"❌ HTTP Hatası: {post_response.status_code}")
                continue
                
        except Exception as e:
            print(f"❌ İstek hatası: {str(e)}")
            if attempt < max_retries - 1:
                print("🔄 Tekrar deneniyor...")
                time.sleep(30)
            continue
        finally:
            session.close()
    
    return False, f"Maksimum deneme sayısı ({max_retries}) aşıldı"

def main():
    """Ana fonksiyon - Kalan 9 kayıtı tamamla"""
    
    print("🚀 Topluluk Üyeliği Otomatik Kayıt Sistemi - Final")
    print("Kalan 9 Kayıtı Tamamlama")
    print("=" * 60)
    
    successful_registrations = 0
    failed_registrations = 0
    
    # 2'den 10'a kadar (kalan 9 kayıt)
    for i in range(2, 11):
        print(f"\n📝 === Kayıt {i}/10 ===")
        
        # Kullanıcı verisi oluştur
        user_data = generate_user_data(i)
        print(f"👤 Kullanıcı: {user_data['username']} ({user_data['name']} {user_data['surname']})")
        print(f"📧 Email: {user_data['email']}")
        print(f"🆔 Öğrenci No: {user_data['student_id']}")
        print(f"📞 Telefon: {user_data['phone_number']}")
        
        # Kayıt yap
        success, message = register_single_user(user_data)
        
        if success:
            print(f"✅ {message}")
            successful_registrations += 1
            
            # Başarılı kayıtları dosyaya yaz
            with open('final_registrations.txt', 'a', encoding='utf-8') as f:
                f.write(f"Kayıt {i}:\n")
                for key, value in user_data.items():
                    f.write(f"  {key}: {value}\n")
                f.write("-" * 50 + "\n")
        else:
            print(f"❌ {message}")
            failed_registrations += 1
        
        # Kayıtlar arasında uzun bekleme (rate limiting için)
        if i < 10:
            wait_time = 120  # 2 dakika bekle
            print(f"⏳ Rate limiting için {wait_time} saniye bekleniyor...")
            time.sleep(wait_time)
    
    # Özet
    print("\n" + "=" * 60)
    print("📊 KAYIT ÖZETİ (KALAN 9 KAYIT)")
    print("=" * 60)
    print(f"✅ Başarılı kayıtlar: {successful_registrations}")
    print(f"❌ Başarısız kayıtlar: {failed_registrations}")
    print(f"📈 Toplam başarılı (1 + {successful_registrations}): {1 + successful_registrations}")
    if successful_registrations > 0:
        print(f"📁 Başarılı kayıtlar 'final_registrations.txt' dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
