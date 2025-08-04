# GÜVENLİK DÜZELTMELERİ - Bu dosyayı app.py'ye entegre edin

# 1. CSRF Koruması Ekleme
from flask_wtf.csrf import CSRFProtect

# app.py'nin başına ekleyin:
csrf = CSRFProtect(app)

# 2. Daha Güvenli Admin Decorator
def strict_admin_required(f):
    """Sadece is_admin=True olan kullanıcılar için"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Bu sayfaya sadece adminler erişebilir.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def specific_permission_required(permission):
    """Belirli bir yetki için"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Giriş yapmanız gerekiyor.', 'danger')
                return redirect(url_for('login'))
            
            if not getattr(current_user, permission, False) and not current_user.is_admin:
                flash(f'Bu işlem için {permission} yetkisi gerekiyor.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 3. Güvenli Export Fonksiyonu
def sanitize_export_data(member):
    """Export edilecek verileri temizle/anonimleştir"""
    return {
        'id': member.id,
        'name': member.name[:1] + "*" * (len(member.name) - 1),  # Sadece ilk harf
        'surname': member.surname[:1] + "*" * (len(member.surname) - 1),
        'faculty': member.faculty,
        'department': member.department,
        'student_class': member.student_class,
        'registration_date': member.registration_date.strftime('%Y-%m-%d'),
        'is_approved': member.is_approved,
        # Telefon, doğum tarihi gibi hassas bilgileri çıkar
    }

# 4. Rate Limiting (Flask-Limiter ile)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Admin rotalarına özel limitler
@limiter.limit("10 per minute")
def admin_routes_limiter():
    pass

# 5. Input Validation
import bleach

def sanitize_input(text):
    """Kullanıcı girdilerini temizle"""
    if not text:
        return text
    return bleach.clean(text, tags=[], attributes={}, strip=True)

# 6. Logging Güvenliği
import logging
from logging.handlers import RotatingFileHandler

def setup_secure_logging():
    """Güvenli log ayarları"""
    if not app.debug:
        file_handler = RotatingFileHandler('logs/anime_fansub.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

# 7. Database Query Güvenliği
def safe_search_filter(query_text, model):
    """SQL Injection'a karşı güvenli arama"""
    if not query_text:
        return None
    
    # Sadece alfanumerik karakterler ve boşluk
    safe_query = re.sub(r'[^a-zA-Z0-9\s]', '', query_text)
    
    return (
        model.name.ilike(f'%{safe_query}%') |
        model.surname.ilike(f'%{safe_query}%') |
        model.faculty.ilike(f'%{safe_query}%') |
        model.department.ilike(f'%{safe_query}%') |
        model.student_id.ilike(f'%{safe_query}%')
    )

# 8. Session Güvenliği Artırma
app.config.update(
    SESSION_COOKIE_SECURE=True,  # HTTPS zorunlu
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',
    PERMANENT_SESSION_LIFETIME=900,  # 15 dakika
)
