from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, BooleanField, SelectField, IntegerField, DateTimeField, DateField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional, EqualTo, ValidationError, Email
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from models import Genre, User, CommunityMember

def get_genres():
    return Genre.query.all()

class RegistrationForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Şifreyi Onayla', validators=[DataRequired(), EqualTo('password', message='Şifreler uyuşmuyor.')])
    submit = SubmitField('Kayıt Ol')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Bu kullanıcı adı zaten alınmış. Lütfen farklı bir kullanıcı adı seçin.')

class LoginForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired()])
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
    email = StringField('E-posta Adresi', validators=[DataRequired(), Email()])
    name = StringField('Adınız (Name)', validators=[DataRequired(), Length(min=2, max=100)])
    surname = StringField('Soyadınız (Surname)', validators=[DataRequired(), Length(min=2, max=100)])
    place_of_birth = StringField('Doğum İliniz (Place of Birth, for international students: Country)', validators=[DataRequired(), Length(min=2, max=100)])
    date_of_birth = DateField('Doğum Tarihiniz (Date of Birth)', validators=[DataRequired()])
    current_residence = StringField('Mevcut Oturduğunuz Yer (Current Residence)', validators=[DataRequired(), Length(min=2, max=100)])
    student_id = StringField('Öğrenci Numaranız (Student ID)', validators=[DataRequired(), Length(min=1, max=20)])
    phone_number = StringField('Telefon Numaranız, boşluksuz, ülke alan kodlu Örn: +905123456789 (Phone No., without whitespace and country code)', validators=[DataRequired(), Length(min=10, max=20)])
    student_class = StringField('Sınıfınız (Class)', validators=[DataRequired(), Length(min=1, max=50)])
    faculty = StringField('Fakülteniz (Faculty/School/Institute)', validators=[DataRequired(), Length(min=2, max=100)])
    department = StringField('Bölümünüz (Department)', validators=[DataRequired(), Length(min=2, max=100)])
    preferred_units = SelectMultipleField('Hangi birimde çalışmak istersiniz? (Which unit do you want to participate to?)', 
                                        choices=[
                                            ('anime_dubbing', 'Anime Dublaj'),
                                            ('translation', 'Çeviri'),
                                            ('editing', 'Editörlük'),
                                            ('timing', 'Timing'),
                                            ('quality_control', 'Kalite Kontrolü'),
                                            ('social_media', 'Sosyal Medya'),
                                            ('graphic_design', 'Grafik Tasarım'),
                                            ('web_development', 'Web Geliştirme'),
                                            ('project_management', 'Proje Yönetimi')
                                        ], 
                                        validators=[Optional()])
    submit = SubmitField('Topluluk Üyeliği İçin Başvur')

    def validate_email(self, email):
        member = CommunityMember.query.filter_by(email=email.data).first()
        if member:
            raise ValidationError('Bu e-posta adresi zaten kayıtlı.')

    def validate_student_id(self, student_id):
        member = CommunityMember.query.filter_by(student_id=student_id.data).first()
        if member:
            raise ValidationError('Bu öğrenci numarası zaten kayıtlı.')

    def validate_phone_number(self, phone_number):
        if not phone_number.data.startswith('+'):
            raise ValidationError('Telefon numarası ülke kodu ile başlamalıdır (örn: +905123456789)')
        member = CommunityMember.query.filter_by(phone_number=phone_number.data).first()
        if member:
            raise ValidationError('Bu telefon numarası zaten kayıtlı.')
