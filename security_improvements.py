#!/usr/bin/env python3
"""
Güvenlik İyileştirmeleri
Bu dosya, sitenizin güvenliğini artırmak için önerilen değişiklikleri içerir.
"""

from functools import wraps
from flask import current_app, request, abort
import logging
import re

# 1. GÜÇLÜ ADMİN YETKİ KONTROLÜ
def super_admin_required(f):
    """Çok katmanlı admin kontrolü"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Kullanıcı girişi kontrolü
        if not current_user.is_authenticated:
            abort(401)
        
        # Admin yetkisi kontrolü
        if not current_user.is_admin:
            current_app.logger.warning(f"Yetkisiz admin erişim denemesi: {current_user.username} - {request.remote_addr}")
            abort(403)
        
        # IP whitelist kontrolü (prod için)
        allowed_ips = current_app.config.get('ADMIN_ALLOWED_IPS', [])
        if allowed_ips and request.remote_addr not in allowed_ips:
            current_app.logger.critical(f"Güvenilmeyen IP'den admin erişimi: {request.remote_addr}")
            abort(403)
        
        # Session güvenlik kontrolü
        if not session.get('admin_verified'):
            # 2FA veya ekstra doğrulama gerekebilir
            abort(403)
            
        return f(*args, **kwargs)
    return decorated_function

# 2. GÜVENLİ EXPORT FONKSİYONU
def secure_export_community_members():
    """Hassas verileri çıkarılmış güvenli export"""
    try:
        # Sadece gerekli alanları al
        safe_fields = [
            "ID", "Kullanıcı Adı", "Ad", "Soyad", 
            "Fakülte", "Bölüm", "Sınıf", "Onay Durumu", "Başvuru Tarihi"
        ]
        
        # Hassas bilgileri çıkar
        # KALDIRILAN: E-posta, Telefon, Doğum Tarihi, Adres, Öğrenci No
        
        members = query.order_by(CommunityMember.registration_date.desc()).all()
        
        for row, member in enumerate(members, 2):
            ws.cell(row=row, column=1, value=member.id)
            ws.cell(row=row, column=2, value=member.username)
            ws.cell(row=row, column=3, value=member.name)
            ws.cell(row=row, column=4, value=member.surname)
            ws.cell(row=row, column=5, value=member.faculty)
            ws.cell(row=row, column=6, value=member.department)
            ws.cell(row=row, column=7, value=member.student_class)
            ws.cell(row=row, column=8, value="Onaylandı" if member.is_approved else "Beklemede")
            ws.cell(row=row, column=9, value=member.registration_date.strftime('%d.%m.%Y') if member.registration_date else '')
        
        # Export logunu güvenli tut
        log_action('safe_export_community_members', f'Güvenli export - Toplam: {len(members)}')
        
    except Exception as e:
        current_app.logger.error(f"Güvenli export hatası: {str(e)}")
        raise

# 3. GELIŞMIŞ INPUT SANİTİZASYONU
def advanced_sanitize_input(text, allow_html=False):
    """Gelişmiş input temizleme"""
    if not text:
        return text
    
    # XSS koruması
    if not allow_html:
        text = bleach.clean(text, tags=[], attributes={}, strip=True)
    
    # SQL Injection koruması
    dangerous_patterns = [
        r'(?i)(union|select|insert|update|delete|drop|create|alter)\s',
        r'(?i)(script|javascript|vbscript|onload|onerror)',
        r'[<>"\';\\]|--|\*|/\*|\*/'
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text)
    
    # Directory traversal koruması
    text = re.sub(r'\.\./', '', text)
    text = re.sub(r'\.\.\\', '', text)
    
    return text.strip()

# 4. VERİ ŞOKAĞI KONTROLÜ
def check_data_encryption():
    """Veritabanında şifrelenmesi gereken alanları kontrol et"""
    sensitive_fields = [
        'phone_number', 'date_of_birth', 'place_of_birth', 
        'current_residence', 'student_id'
    ]
    
    print("⚠️  Şifrelenmesi gereken hassas alanlar:")
    for field in sensitive_fields:
        print(f"   - CommunityMember.{field}")
    
    print("\nÖNERİ: Bu alanları şifreleyin veya hash'leyin!")

# 5. LOGİN GÜVENLİĞİ
def secure_login_attempt(username, password, ip_address):
    """Güvenli login denemesi"""
    
    # Brute force koruması
    failed_attempts = cache.get(f"failed_login:{ip_address}", 0)
    if failed_attempts >= 5:
        current_app.logger.warning(f"Çok fazla başarısız login: {ip_address}")
        time.sleep(2)  # Yavaşlatma
        return False
    
    # Kullanıcı adı/e-posta kontrolü
    user = User.query.filter(
        db.or_(User.username == username, User.email == username)
    ).first()
    
    if user and check_password_hash(user.password, password):
        # Başarılı login
        cache.delete(f"failed_login:{ip_address}")
        current_app.logger.info(f"Başarılı login: {user.username} - {ip_address}")
        return user
    else:
        # Başarısız login
        cache.set(f"failed_login:{ip_address}", failed_attempts + 1, timeout=300)
        current_app.logger.warning(f"Başarısız login: {username} - {ip_address}")
        return False

# 6. SESSION GÜVENLİĞİ
def secure_session_config():
    """Güvenli session konfigürasyonu"""
    return {
        'SESSION_COOKIE_SECURE': True,  # Sadece HTTPS
        'SESSION_COOKIE_HTTPONLY': True,  # JavaScript erişimi yok
        'SESSION_COOKIE_SAMESITE': 'Strict',  # CSRF koruması
        'PERMANENT_SESSION_LIFETIME': 900,  # 15 dakika
        'SESSION_REFRESH_EACH_REQUEST': True
    }

# 7. VERİTABANI GÜVENLİĞİ
def secure_database_queries():
    """Güvenli veritabanı sorguları"""
    
    # ❌ YANLIŞ - String interpolation
    # query = f"SELECT * FROM users WHERE username = '{username}'"
    
    # ✅ DOĞRU - Parametreli sorgu
    # user = User.query.filter_by(username=username).first()
    
    # ✅ DOĞRU - Raw SQL gerekirse
    # result = db.session.execute(
    #     text("SELECT * FROM users WHERE username = :username"), 
    #     {"username": username}
    # )
    
    pass

print("🔒 Güvenlik iyileştirmeleri yüklendi!")
print("⚠️  Bu dosyadaki önerileri projenize uygulayın.")
