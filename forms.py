from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, BooleanField, SelectField, IntegerField, DateTimeField, DateField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional, EqualTo, ValidationError, Email
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from models import Genre, User, CommunityMember

def get_genres():
    return Genre.query.all()

class RegistrationForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Şifre Tekrar', validators=[DataRequired(), EqualTo('password', message='Şifreler eşleşmiyor')])
    submit = SubmitField('Kayıt Ol')

    def validate_username(self, username):
        # Kullanıcı adı sadece harf, rakam ve alt çizgi içermeli
        if not all(c.isalnum() or c == '_' for c in username.data):
            raise ValidationError('Kullanıcı adı sadece harf, rakam ve alt çizgi (_) içermelidir.')
            
        # Kullanıcı adı rakamla başlamamalı
        if username.data[0].isdigit():
            raise ValidationError('Kullanıcı adı rakamla başlayamaz.')
            
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Bu kullanıcı adı zaten kullanılıyor. Lütfen farklı bir kullanıcı adı seçin.')

    def validate_email(self, email):
        # E-posta format kontrolü (büyük/küçük harf duyarsız)
        email_lower = email.data.lower()
        
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Bu e-posta adresi zaten kayıtlı. Lütfen farklı bir e-posta adresi kullanın.')

    def validate_password(self, password):
        # Şifre en az bir büyük harf içermeli
        if not any(c.isupper() for c in password.data):
            raise ValidationError('Şifre en az bir büyük harf içermelidir.')
            
        # Şifre en az bir rakam içermeli
        if not any(c.isdigit() for c in password.data):
            raise ValidationError('Şifre en az bir rakam içermelidir.')
            
        # Şifre en az bir küçük harf içermeli
        if not any(c.islower() for c in password.data):
            raise ValidationError('Şifre en az bir küçük harf içermelidir.')

class LoginForm(FlaskForm):
    username = StringField('Kullanıcı Adı veya E-posta', validators=[DataRequired()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    submit = SubmitField('Giriş Yap')

class EpisodeForm(FlaskForm):
    number = StringField('Bölüm Numarası', validators=[DataRequired()])
    sources = TextAreaField("Kaynaklar (virgülle ayrılmış URL'ler)", validators=[DataRequired()])
    submit = SubmitField('Bölüm Ekle')

class AnimeForm(FlaskForm):
    name = StringField('Anime Adı', validators=[DataRequired(), Length(min=1, max=150)])
    description = TextAreaField('Açıklama', validators=[DataRequired()])
    cover_image = StringField('Kapak Resmi URL', validators=[DataRequired()])
    release_year = IntegerField('Çıkış Yılı', validators=[Optional()])
    status = SelectField('Durum', choices=[
        ('Bitti', 'Bitti'),
        ('Devam Ediyor', 'Devam Ediyor')
    ], validators=[Optional()])
    anime_type = SelectField('Tip', choices=[
        ('TV', 'TV'),
        ('Film', 'Film'),
        ('OVA', 'OVA')
    ], validators=[Optional()])
    genres = QuerySelectMultipleField('Türler', query_factory=get_genres, get_label='name', allow_blank=True)
    mal_score = StringField('MyAnimeList Puanı', validators=[Optional()])
    mal_url = StringField('MyAnimeList URL', validators=[Optional()])
    submit = SubmitField('Anime Ekle/Güncelle')

class GenreForm(FlaskForm):
    name = StringField('Tür Adı', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Tür Ekle')

class AnimeSearchForm(FlaskForm):
    query = StringField('Arama', validators=[Optional(), Length(min=1, max=100)])
    genre = SelectField('Tür', choices=[], validators=[Optional()])
    release_year = IntegerField('Yıl', validators=[Optional()])
    anime_type = SelectField('Tip', choices=[('', 'Tümü'), ('TV', 'TV'), ('Film', 'Film'), ('OVA', 'OVA')], validators=[Optional()])
    sort_by = SelectField('Sırala', choices=[
        ('name_asc', 'İsme Göre (A-Z)'),
        ('name_desc', 'İsme Göre (Z-A)'),
        ('rating_desc', 'Puana Göre (En Yüksek)'),
        ('year_desc', 'Yıla Göre (En Yeni)'),
    ], default='name_asc', validators=[Optional()])
    submit = SubmitField('Filtrele')

class UserForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=1, max=50)])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=4)])
    can_delete = BooleanField('Silme Yetkisi')
    can_edit = BooleanField('Düzenleme Yetkisi')
    can_add_user = BooleanField('Kullanıcı Ekleme Yetkisi')
    is_admin = BooleanField('Admin Yetkisi')
    is_community_member = BooleanField('Topluluk Üyesi')
    submit = SubmitField('Kullanıcı Ekle')

class EditUserForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=1, max=50)])
    can_delete = BooleanField('Silme Yetkisi')
    can_edit = BooleanField('Düzenleme Yetkisi')
    can_add_user = BooleanField('Kullanıcı Ekleme Yetkisi')
    is_admin = BooleanField('Admin Yetkisi')
    is_community_member = BooleanField('Topluluk Üyesi')
    submit = SubmitField('Kullanıcıyı Güncelle')

class NewsForm(FlaskForm):
    title = StringField('Başlık', validators=[DataRequired()])
    content = TextAreaField('İçerik', validators=[DataRequired()])
    image_url = StringField("Resim URL'si")
    is_pinned = BooleanField('Başa Sabitle')
    submit = SubmitField('Yayınla')

class EventForm(FlaskForm):
    title = StringField('Etkinlik Başlığı', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Açıklama', validators=[Optional()])
    start_time = StringField('Başlangıç Zamanı', validators=[DataRequired()])
    end_time = StringField('Bitiş Zamanı', validators=[Optional()])
    submit = SubmitField('Etkinlik Oluştur')

class CommunityRegistrationForm(FlaskForm):
    # Giriş bilgileri
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Şifre Tekrar', validators=[DataRequired(), EqualTo('password', message='Şifreler eşleşmiyor')])
    
    # Kişisel bilgiler
    email = StringField('E-posta Adresi', validators=[DataRequired(), Email()])
    name = StringField('Adınız (Name)', validators=[DataRequired(), Length(min=2, max=100)])
    surname = StringField('Soyadınız (Surname)', validators=[DataRequired(), Length(min=2, max=100)])
    place_of_birth = StringField('Doğum İliniz (Place of Birth, for international students: Country)', validators=[DataRequired(), Length(min=2, max=100)])
    date_of_birth = DateField('Doğum Tarihiniz (Date of Birth)', validators=[DataRequired()])
    current_residence = StringField('Mevcut Oturduğunuz Yer (Current Residence)', validators=[DataRequired(), Length(min=2, max=100)])
    
    # Akademik bilgiler
    student_id = StringField('Öğrenci Numaranız (Student ID)', validators=[DataRequired(), Length(min=1, max=20)])
    phone_number = StringField('Telefon Numaranız, boşluksuz, ülke alan kodlu Örn: +905123456789 (Phone No., without whitespace and country code)', validators=[DataRequired(), Length(min=10, max=20)])
    student_class = StringField('Sınıfınız (Class)', validators=[DataRequired(), Length(min=1, max=50)])
    faculty = StringField('Fakülteniz (Faculty/School/Institute)', validators=[DataRequired(), Length(min=2, max=100)])
    department = StringField('Bölümünüz (Department)', validators=[DataRequired(), Length(min=2, max=100)])
    
    # Birim seçimi
    preferred_units = SelectMultipleField('Hangi birimde çalışmak istersiniz? (Which unit do you want to participate to?)', 
                                        choices=[
                                            ('drawing_unit', 'Çizim Birimi'),
                                            ('cosplay_unit', 'Cosplay Birimi'),
                                            ('social_media_unit', 'Sosyal Medya Birimi'),
                                            ('translation_fansub', 'Çeviri Birimi / Fansub'),
                                            ('ninjutsu_unit', 'Ninjutsu Birimi')
                                        ], 
                                        validators=[Optional()])
    submit = SubmitField('Topluluk Üyeliği İçin Başvur')

    def validate_username(self, username):
        # Kullanıcı adı sadece harf, rakam ve alt çizgi içermeli
        if not all(c.isalnum() or c == '_' for c in username.data):
            raise ValidationError('Kullanıcı adı sadece harf, rakam ve alt çizgi (_) içermelidir.')
            
        # Kullanıcı adı rakamla başlamamalı
        if username.data[0].isdigit():
            raise ValidationError('Kullanıcı adı rakamla başlayamaz.')
            
        # Mevcut kullanıcı kontrolü
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Bu kullanıcı adı zaten kullanılıyor. Lütfen farklı bir kullanıcı adı seçin.')
            
        # Topluluk üyesi başvuruları arasında da kontrol et
        member = CommunityMember.query.filter_by(username=username.data).first()
        if member:
            raise ValidationError('Bu kullanıcı adı zaten kullanılıyor. Lütfen farklı bir kullanıcı adı seçin.')

    def validate_email(self, email):
        # E-posta format kontrolü
        if not email.data.lower().endswith('@hacettepe.edu.tr') and not email.data.lower().endswith('@gmail.com') and not email.data.lower().endswith('@outlook.com'):
            # Sadece uyarı, engelleme yok
            pass
        
        member = CommunityMember.query.filter_by(email=email.data).first()
        if member:
            raise ValidationError('Bu e-posta adresi zaten kayıtlı.')

    def validate_student_id(self, student_id):
        # Öğrenci numarası format kontrolü (sadece rakam olmalı)
        if not student_id.data.isdigit():
            raise ValidationError('Öğrenci numarası sadece rakamlardan oluşmalıdır.')
        
        # Hacettepe öğrenci numarası genelde 9 haneli
        if len(student_id.data) < 7 or len(student_id.data) > 10:
            raise ValidationError('Öğrenci numarası 7-10 haneli olmalıdır.')
            
        member = CommunityMember.query.filter_by(student_id=student_id.data).first()
        if member:
            raise ValidationError('Bu öğrenci numarası zaten kayıtlı.')

    def validate_phone_number(self, phone_number):
        # Ülke kodu kontrolü
        if not phone_number.data.startswith('+'):
            raise ValidationError('Telefon numarası ülke kodu ile başlamalıdır (örn: +905123456789)')
        
        # Sadece rakam ve + içermeli
        if not all(c.isdigit() or c == '+' for c in phone_number.data):
            raise ValidationError('Telefon numarası sadece rakam ve + işareti içermelidir.')
            
        # Türkiye numarası format kontrolü
        if phone_number.data.startswith('+90') and len(phone_number.data) != 13:
            raise ValidationError('Türkiye telefon numarası +90 ile başlayıp 13 haneli olmalıdır.')
            
        member = CommunityMember.query.filter_by(phone_number=phone_number.data).first()
        if member:
            raise ValidationError('Bu telefon numarası zaten kayıtlı.')
    
    def validate_name(self, name):
        # İsim sadece harf içermeli
        if not all(c.isalpha() or c.isspace() for c in name.data):
            raise ValidationError('İsim sadece harf ve boşluk içermelidir.')
    
    def validate_surname(self, surname):
        # Soyisim sadece harf içermeli
        if not all(c.isalpha() or c.isspace() for c in surname.data):
            raise ValidationError('Soyisim sadece harf ve boşluk içermelidir.')

class CommunityMemberSearchForm(FlaskForm):
    query = StringField('Ara (Ad, Soyad, Fakülte, Bölüm, Öğrenci No)', validators=[Optional()])
    status = SelectField('Onay Durumu', 
                        choices=[('', 'Tümü'), ('pending', 'Beklemede'), ('approved', 'Onaylandı')],
                        default='')
    submit = SubmitField('Ara')
