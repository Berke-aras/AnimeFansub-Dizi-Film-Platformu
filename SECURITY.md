# 🛡️ AnimeFansub Güvenlik Kılavuzu

## 🔐 **CSRF Koruması (Cross-Site Request Forgery)**

**Durum:** ✅ **TÜM FORMLARDA VE ROUTE'LARDA AKTİF**

### Frontend (Template) Korumaları:

-   ✅ Community thread formları (`community_thread.html`)
-   ✅ Yeni thread oluşturma (`community_new_thread.html`)
-   ✅ **Admin kategori yönetimi (`admin_manage_categories.html`) - WTF Form + CSRF**
-   ✅ Admin topluluk üye yönetimi (`admin_community_members.html`)
-   ✅ Topluluk üye onay/red formları (`view_community_member.html`)
-   ✅ Admin genre yönetimi (`manage_genres.html`)
-   ✅ Kullanıcı silme formları (`users.html`)
-   ✅ Anime silme formları (`admin.html`)
-   ✅ Episode silme formları (`anime.html`)
-   ✅ Event silme formları (`manage_events.html`)
-   ✅ Tüm WTF form'larda otomatik `{{ form.hidden_tag() }}`
-   ✅ Manuel formlarda `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>`

### Backend (Route) Korumaları:

-   ✅ Community route'ları (`community.py`) - tüm POST metodları
-   ✅ **Admin kategori yönetimi - WTF Form + validate_on_submit()**
-   ✅ Admin yönetim route'ları (`app.py`) - tüm kritik işlemler
-   ✅ Silme operasyonları (`delete_*`) - validate_csrf() eklendi
-   ✅ Onay/Red operasyonları (`approve_*`, `reject_*`) - validate_csrf() eklendi

### CSRF Token Kullanımı:

```python
# Backend doğrulama (Manuel formlar için)
from flask_wtf.csrf import validate_csrf
validate_csrf(request.form.get('csrf_token'))

# Backend doğrulama (WTF formlar için)
form = CategoryForm()
if form.validate_on_submit():  # CSRF otomatik doğrulanır
    # İşlemler...

# Template kullanım
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>  # Manuel formlar
{{ form.hidden_tag() }}  # WTF formlar için
```

### 2. **Rate Limiting**

-   Login: 5 deneme/dakika
-   Kayıt: 3 deneme/dakika
-   Topluluk kayıt: 2 deneme/dakika
-   Export: 1 deneme/dakika

### 3. **Input Sanitization**

-   Tüm kullanıcı girdileri temizleniyor
-   SQL injection koruması
-   XSS koruması (bleach kullanılıyor)

### 4. **Admin Yetki Kontrolü**

-   `strict_admin_required`: Sadece is_admin=True
-   `delete_permission_required`: Silme işlemleri için
-   Hassas rotalar ek koruma altında

### 5. **Session Güvenliği**

-   Session süresi: 15 dakika
-   HttpOnly cookies
-   SameSite=Strict (CSRF koruması)
-   Environment bazlı Secure flag

### 6. **Hassas Veri Koruması**

-   Export fonksiyonunda kişisel veriler çıkarıldı
-   Telefon, doğum tarihi, adres bilgileri korunuyor

## ⚠️ **Kritik Uyarılar**

### Production'da Mutlaka Yapılması Gerekenler:

1. **Environment Variables (.env)**

```bash
SECRET_KEY=your-super-secret-production-key-here
SESSION_COOKIE_SECURE=True
REMEMBER_COOKIE_SECURE=True
FLASK_DEBUG=False
```

2. **HTTPS Zorunlu**

-   SSL sertifikası kullanın
-   HTTP'den HTTPS'e yönlendirme

3. **Database Güvenliği**

-   Production'da SQLite yerine PostgreSQL/MySQL
-   Database şifreleme
-   Düzenli backup

4. **Server Güvenliği**

```bash
# Firewall kuralları
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Fail2ban (brute force koruması)
sudo apt install fail2ban
```

## 🔧 **Önerilen Ek Güvenlik Önlemleri**

### 1. **WAF (Web Application Firewall)**

-   CloudFlare, AWS WAF veya benzer
-   Bot koruması
-   DDoS koruması

### 2. **Monitoring ve Logging**

```python
# Log ayarları (app.py'ye ekle)
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/anime_fansub.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

### 3. **Database Migration Güvenliği**

-   Migration dosyalarını versiyon kontrolünde tutun
-   Production migration'ları dikkatli yapın

### 4. **Backup Stratejisi**

```bash
# Günlük database backup
0 2 * * * /path/to/backup_script.sh
```

## 🧪 **Güvenlik Testleri**

### Test Script Çalıştırma:

```bash
python security_test.py
```

## 📋 **Güvenlik Checklist - SON DURUM**

### ✅ **TAMAMLANAN GÜVENLİK ÖNLEMLERİ:**

-   [x] **Admin Access Control** - Sıkı yetki kontrolleri (`strict_admin_required`, `delete_permission_required`)
-   [x] **CSRF Protection** - Tüm form ve route'larda aktif (56+ form ve route korundu)
-   [x] **Rate Limiting** - Brute force koruması (login, register, kritik API'lar)
-   [x] **Input Sanitization** - XSS ve SQL injection koruması (bleach entegrasyonu)
-   [x] **Sensitive Data Export** - Admin export'larda hassas veri gizleme
-   [x] **Environment Security** - `.env` dosyası ve secret key koruması
-   [x] **Session Security** - Güvenli session yapılandırması
-   [x] **Error Handling** - Güvenli hata yönetimi
-   [x] **Security Documentation** - Kapsamlı güvenlik dökümanları
-   [x] **Automated Security Testing** - `security_test.py` scripti

### 🔍 **GÜVENLİK TEST SONUÇLARI:**

-   ✅ Admin sayfalar yetkisiz erişime kapalı
-   ✅ CSRF token'ları tüm formlarda mevcut
-   ⚠️ Rate limiting ayarları ince ayar gerektirebilir (production'da)
-   ✅ Input sanitization aktif
-   ✅ Hassas veri export'larda gizli

### 🚨 **ÖNEMLİ PRODUCTION ÖNERİLERİ:**

-   [ ] HTTPS zorunlu hale getirin
-   [ ] WAF (Web Application Firewall) kullanın
-   [ ] Database backup stratejisi oluşturun
-   [ ] Log monitoring sistemi kurun
-   [ ] Düzenli güvenlik taraması yapın

### 📊 **KORUNAN ALANLAR ÖZETİ:**

-   **Admin Paneli:** 15+ korumalı route
-   **Community Forum:** 8+ korumalı form/route
-   **User Management:** 5+ korumalı işlem
-   **Content Management:** 10+ korumalı form
-   **API Endpoints:** Rate limiting + input validation

## 🚨 **Acil Durum Protokolü**

### Güvenlik İhlali Durumunda:

1. **Hemen yapılacaklar:**

    - Siteyi geçici olarak kapatın
    - Database backup'ı alın
    - Log dosyalarını kaydedin

2. **İnceleme:**

    - Saldırı vektörünü belirleyin
    - Etkilenen kullanıcıları tespit edin
    - Hasar değerlendirmesi yapın

3. **Düzeltme:**
    - Güvenlik açığını kapatın
    - Etkilenen verilen temizleyin
    - Kullanıcıları bilgilendirin

## 📊 **Güvenlik Monitoring**

### Monitör Edilecek Log'lar:

-   Başarısız login denemeleri
-   Admin sayfa erişimleri
-   SQL hataları
-   Rate limit aşımları
-   Büyük export işlemleri

### Alarm Kuralları:

-   5 dakikada 10+ başarısız login
-   Bilinmeyen IP'den admin erişimi
-   SQL injection pattern'ları
-   Büyük veri export'ları

## 📞 **İletişim**

Güvenlik ile ilgili sorular için:

-   GitHub Issues

---

**Son güncellenme:** 5 Ağustos 2025
