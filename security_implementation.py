#!/usr/bin/env python3
"""
🔒 Güvenlik İyileştirmeleri - Pratik Uygulama
Bu dosya mevcut projenize entegre edilebilir güvenlik geliştirmelerini içerir.
"""

from flask import session, request, current_app
from flask_login import current_user
from functools import wraps
import time
import hashlib
from cryptography.fernet import Fernet
import os
import re
import bleach

# 1. VERİ ŞİFRELEME SİSTEMİ
class DataEncryption:
    """Hassas verileri şifrelemek için kullanılır"""
    
    def __init__(self):
        # Şifreleme anahtarını environment'tan al veya oluştur
        self.key = os.environ.get('ENCRYPTION_KEY')
        if not self.key:
            # Yeni anahtar oluştur (sadece development için)
            self.key = Fernet.generate_key()
            print(f"⚠️  Yeni şifreleme anahtarı oluşturuldu: {self.key.decode()}")
            print("Bu anahtarı .env dosyasına ENCRYPTION_KEY olarak ekleyin!")
        else:
            self.key = self.key.encode()
        
        self.cipher_suite = Fernet(self.key)
    
    def encrypt(self, data):
        """Veriyi şifrele"""
        if not data:
            return None
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data):
        """Veriyi çöz"""
        if not encrypted_data:
            return None
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

# Global şifreleme instance'ı
encryption = DataEncryption()

# 2. HASSAS VERİ KORUMA FONKSİYONLARI
def hash_sensitive_data(data):
    """Geri dönüştürülmesi gerekmeyen hassas verileri hash'le"""
    if not data:
        return None
    return hashlib.sha256(data.encode()).hexdigest()

def encrypt_phone_number(phone):
    """Telefon numarasını şifrele"""
    return encryption.encrypt(phone)

def decrypt_phone_number(encrypted_phone):
    """Şifrelenmiş telefon numarasını çöz"""
    return encryption.decrypt(encrypted_phone)

def encrypt_student_id(student_id):
    """Öğrenci numarasını şifrele"""
    return encryption.encrypt(student_id)

def decrypt_student_id(encrypted_student_id):
    """Şifrelenmiş öğrenci numarasını çöz"""
    return encryption.decrypt(encrypted_student_id)

# 3. GELİŞMİŞ GÜVENLİK DECORATORLERİ
def enhanced_admin_required(f):
    """Geliştirilmiş admin yetki kontrolü"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Temel kontroller
        if not current_user.is_authenticated:
            current_app.logger.warning(f'🚫 Kimlik doğrulanmamış admin erişim denemesi: {request.remote_addr}')
            return redirect(url_for('login'))
        
        if not current_user.is_admin:
            current_app.logger.warning(f'🚨 Yetkisiz admin erişim denemesi: {current_user.username} - {request.remote_addr} - {request.url}')
            flash('Admin yetkisi gerekli.', 'danger')
            return redirect(url_for('index'))
        
        # Session güvenlik kontrolü
        if not session.get('admin_session_verified'):
            session['admin_session_verified'] = True
            current_app.logger.info(f'🔐 Admin session başlatıldı: {current_user.username}')
        
        # IP loglaması
        current_app.logger.info(f'👤 Admin erişimi: {current_user.username} - {request.remote_addr} - {request.url}')
        
        return f(*args, **kwargs)
    return decorated_function

def rate_limit_enhanced(max_attempts=5, window_minutes=15):
    """Gelişmiş rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # IP bazlı rate limiting
            client_ip = request.remote_addr
            key = f"rate_limit:{f.__name__}:{client_ip}"
            
            # Basit cache yerine session kullan (demo amaçlı)
            attempts = session.get(key, 0)
            
            if attempts >= max_attempts:
                current_app.logger.warning(f'🚫 Rate limit aşıldı: {client_ip} - {f.__name__}')
                time.sleep(2)  # Yavaşlatma
                flash(f'Çok fazla deneme. {window_minutes} dakika bekleyin.', 'warning')
                return redirect(request.url)
            
            # Deneme sayısını artır
            session[key] = attempts + 1
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 4. GELİŞMİŞ INPUT SANİTİZASYONU
def super_sanitize_input(text, allow_html=False):
    """Gelişmiş input temizleme"""
    if not text:
        return text
    
    # XSS koruması
    if not allow_html:
        text = bleach.clean(text, tags=[], attributes={}, strip=True)
    
    # SQL Injection koruması - Genişletilmiş
    dangerous_patterns = [
        r'(?i)(union|select|insert|update|delete|drop|create|alter|truncate|exec|execute)\s',
        r'(?i)(script|javascript|vbscript|onload|onerror|onclick|onmouseover)',
        r'[<>"\';\\]|--|\*|/\*|\*/|xp_|sp_',
        r'(?i)(eval|expression|url|import|@)',
        r'(?i)(information_schema|sysobjects|syscolumns)'
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text)
    
    # Directory traversal koruması
    text = re.sub(r'\.\./', '', text)
    text = re.sub(r'\.\.\\', '', text)
    text = re.sub(r'%2e%2e%2f', '', text, flags=re.IGNORECASE)
    
    # Null byte injection koruması
    text = text.replace('\x00', '')
    
    return text.strip()

# 5. GÜVENLİ EXPORT FONKSİYONU
def secure_community_export(search_query=None, status_filter=None):
    """Güvenli topluluk üyesi export fonksiyonu"""
    try:
        # Sadece gerekli alanları define et
        safe_fields = {
            'id': 'ID',
            'username': 'Kullanıcı Adı', 
            'name': 'Ad',
            'surname': 'Soyad',
            'faculty': 'Fakülte',
            'department': 'Bölüm',
            'student_class': 'Sınıf',
            'is_approved': 'Onay Durumu',
            'registration_date': 'Başvuru Tarihi'
        }
        
        # ❌ EXPORT EDİLMEYEN HASSAS BİLGİLER:
        # - email (e-posta)
        # - phone_number (telefon)
        # - student_id (öğrenci numarası)
        # - date_of_birth (doğum tarihi)
        # - place_of_birth (doğum yeri)
        # - current_residence (adres)
        
        return safe_fields
        
    except Exception as e:
        current_app.logger.error(f"Güvenli export hatası: {str(e)}")
        raise

# 6. LOGİN GÜVENLİK SİSTEMİ
class LoginSecurity:
    """Login güvenliği için helper class"""
    
    @staticmethod
    def log_login_attempt(username, success, ip_address):
        """Login denemelerini logla"""
        status = "✅ BAŞARILI" if success else "❌ BAŞARISIZ"
        current_app.logger.info(f'{status} LOGIN: {username} - {ip_address} - {time.strftime("%Y-%m-%d %H:%M:%S")}')
    
    @staticmethod
    def check_suspicious_activity(ip_address, max_fails=3):
        """Şüpheli aktivite kontrolü"""
        # Basit implementation - production'da Redis/Database kullanın
        key = f"failed_login_{ip_address}"
        fails = session.get(key, 0)
        
        if fails >= max_fails:
            current_app.logger.warning(f'🚨 ŞÜPHELİ AKTİVİTE: {ip_address} - {fails} başarısız deneme')
            return True
        return False
    
    @staticmethod
    def record_failed_login(ip_address):
        """Başarısız login kaydet"""
        key = f"failed_login_{ip_address}"
        session[key] = session.get(key, 0) + 1
    
    @staticmethod
    def clear_failed_logins(ip_address):
        """Başarılı login sonrası temizle"""
        key = f"failed_login_{ip_address}"
        session.pop(key, None)

# 7. SECURITY HEADERS
def add_security_headers(response):
    """Güvenlik başlıklarını ekle"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    return response

# 8. PRODUCTION GÜVENLİK KONFİGÜRASYONU
def get_production_security_config():
    """Production ortamı için güvenlik ayarları"""
    return {
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'change-me-in-production'),
        'SESSION_COOKIE_SECURE': True,
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Strict',
        'PERMANENT_SESSION_LIFETIME': 900,  # 15 dakika
        'WTF_CSRF_TIME_LIMIT': 3600,  # 1 saat
        'UPLOAD_FOLDER': '/secure/uploads',  # Güvenli upload dizini
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max file size
    }

# 9. VERİTABANI GÜVENLİK KONTROLLERI
def validate_database_query(query_string):
    """Veritabanı sorgu güvenlik kontrolü"""
    dangerous_keywords = [
        'drop', 'delete', 'truncate', 'alter', 'create',
        'exec', 'execute', 'xp_', 'sp_', 'information_schema'
    ]
    
    query_lower = query_string.lower()
    for keyword in dangerous_keywords:
        if keyword in query_lower:
            current_app.logger.error(f'🚨 Tehlikeli SQL sorgu engellendi: {query_string[:100]}...')
            return False
    return True

# 10. KULLANIMA HAZIR INTEGRATION
def integrate_security_features(app):
    """Bu fonksiyonu app.py'nizde çağırın"""
    
    # Security headers'ı her response'a ekle
    app.after_request(add_security_headers)
    
    # Production ayarlarını uygula
    if not app.debug:
        app.config.update(get_production_security_config())
    
    print("🔒 Güvenlik özellikleri entegre edildi!")
    print("✅ Security headers aktif")
    print("✅ Production konfigürasyonu yüklendi")
    print("✅ Veri şifreleme hazır")

if __name__ == "__main__":
    print("🛡️  Güvenlik modülü test ediliyor...")
    
    # Test şifreleme
    test_data = "05551234567"
    encrypted = encryption.encrypt(test_data)
    decrypted = encryption.decrypt(encrypted)
    
    print(f"Original: {test_data}")
    print(f"Encrypted: {encrypted[:20]}...")
    print(f"Decrypted: {decrypted}")
    print(f"✅ Şifreleme çalışıyor: {test_data == decrypted}")
    
    # Test sanitization
    dangerous_input = "<script>alert('xss')</script>'; DROP TABLE users; --"
    sanitized = super_sanitize_input(dangerous_input)
    print(f"\nDangerous input: {dangerous_input}")
    print(f"Sanitized: {sanitized}")
    
    print("\n🔒 Güvenlik modülü hazır!")
