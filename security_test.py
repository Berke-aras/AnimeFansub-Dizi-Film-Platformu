#!/usr/bin/env python3
"""
Güvenlik Test Scripti
Bu script sitenizin temel güvenlik kontrollerini test eder.
"""

import requests
import time
import json

def test_rate_limiting(base_url):
    """Rate limiting testleri"""
    print("🔍 Rate limiting testleri başlatılıyor...")
    
    # Login rate limiting testi
    login_url = f"{base_url}/login"
    
    print("  - Login rate limiting testi...")
    for i in range(7):  # 5'ten fazla deneme yap
        try:
            response = requests.post(login_url, data={
                'username': 'test_user',
                'password': 'wrong_password'
            }, timeout=5)
            
            if response.status_code == 429:
                print(f"    ✅ Rate limiting çalışıyor! {i+1}. denemede engellendi.")
                break
            elif i >= 5:
                print(f"    ⚠️  Rate limiting yeterince sıkı değil. {i+1} deneme yapıldı.")
        except requests.exceptions.RequestException as e:
            print(f"    ❌ Bağlantı hatası: {e}")
            break
        
        time.sleep(0.5)

def test_sql_injection(base_url):
    """SQL Injection testleri"""
    print("\n🔍 SQL Injection testleri başlatılıyor...")
    
    # Arama formunda SQL injection testi
    search_url = f"{base_url}/animes"
    
    sql_payloads = [
        "'; DROP TABLE users; --",
        "' OR 1=1 --",
        "' UNION SELECT * FROM users --",
        "<script>alert('xss')</script>",
        "' OR 'x'='x"
    ]
    
    for payload in sql_payloads:
        try:
            response = requests.get(search_url, params={'query': payload}, timeout=5)
            
            if "error" in response.text.lower() or "exception" in response.text.lower():
                print(f"    ⚠️  Potansiyel SQL injection zafiyeti: {payload[:20]}...")
            else:
                print(f"    ✅ Payload temizlendi: {payload[:20]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"    ❌ Bağlantı hatası: {e}")

def test_csrf_protection(base_url):
    """CSRF koruması testleri"""
    print("\n🔍 CSRF koruması testleri başlatılıyor...")
    
    # CSRF token olmadan POST isteği
    try:
        response = requests.post(f"{base_url}/register", data={
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'password123',
            'password2': 'password123'
        }, timeout=5)
        
        if "csrf" in response.text.lower() or response.status_code == 400:
            print("    ✅ CSRF koruması aktif!")
        else:
            print("    ⚠️  CSRF koruması eksik olabilir.")
            
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Bağlantı hatası: {e}")

def test_admin_access(base_url):
    """Admin sayfa erişim testleri"""
    print("\n🔍 Admin sayfa erişim testleri başlatılıyor...")
    
    admin_urls = [
        "/admin",
        "/admin/community_members",
        "/admin/community_members/export",
        "/users",
        "/logs"
    ]
    
    for url in admin_urls:
        try:
            response = requests.get(f"{base_url}{url}", timeout=5)
            
            if response.status_code == 401 or "login" in response.url:
                print(f"    ✅ {url} - Erişim engellendi (login gerekli)")
            elif response.status_code == 403:
                print(f"    ✅ {url} - Erişim engellendi (yetki yok)")
            elif response.status_code == 200:
                print(f"    ⚠️  {url} - Erişim sağlandı! (Güvenlik riski)")
            else:
                print(f"    ❓ {url} - Durum kodu: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"    ❌ {url} - Bağlantı hatası: {e}")

def test_session_security(base_url):
    """Session güvenlik testleri"""
    print("\n🔍 Session güvenlik testleri başlatılıyor...")
    
    try:
        response = requests.get(base_url, timeout=5)
        
        # Cookie güvenlik flag kontrolü
        cookies = response.cookies
        for cookie in cookies:
            if cookie.secure:
                print(f"    ✅ Cookie '{cookie.name}' güvenli (Secure flag)")
            else:
                print(f"    ⚠️  Cookie '{cookie.name}' güvenli değil (Secure flag eksik)")
                
            if cookie.has_nonstandard_attr('HttpOnly'):
                print(f"    ✅ Cookie '{cookie.name}' HttpOnly")
            else:
                print(f"    ⚠️  Cookie '{cookie.name}' HttpOnly değil")
                
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Bağlantı hatası: {e}")

def main():
    print("🛡️  AnimeFansub Güvenlik Test Scripti")
    print("=" * 50)
    
    base_url = input("Site URL'sini girin (örn: http://localhost:5008): ").strip()
    if not base_url:
        base_url = "http://localhost:5008"
    
    print(f"\n🎯 Test hedefi: {base_url}")
    print("-" * 50)
    
    try:
        # Basit bağlantı testi
        response = requests.get(base_url, timeout=10)
        print(f"✅ Site erişilebilir (Durum kodu: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Site erişilemiyor: {e}")
        return
    
    # Güvenlik testleri
    test_rate_limiting(base_url)
    test_sql_injection(base_url)
    test_csrf_protection(base_url)
    test_admin_access(base_url)
    test_session_security(base_url)
    
    print("\n" + "=" * 50)
    print("🏁 Güvenlik testleri tamamlandı!")
    print("\n📋 Öneriler:")
    print("- ⚠️  işaretli alanları gözden geçirin")
    print("- Production'da HTTPS kullanın")
    print("- Düzenli güvenlik taraması yapın")
    print("- Log dosyalarını monitör edin")

if __name__ == "__main__":
    main()
