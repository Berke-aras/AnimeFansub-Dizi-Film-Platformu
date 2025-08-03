from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Optional
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from models import Genre

def get_genres():
    return Genre.query.all()

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
    submit = SubmitField('Anime Ekle/Güncelle')

class GenreForm(FlaskForm):
    name = StringField('Tür Adı', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Tür Ekle')

from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectMultipleField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Optional

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
    submit = SubmitField('Kullanıcı Ekle')

class EditUserForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=1, max=50)])
    can_delete = BooleanField('Silme Yetkisi')
    can_edit = BooleanField('Düzenleme Yetkisi')
    can_add_user = BooleanField('Kullanıcı Ekleme Yetkisi')
    submit = SubmitField('Kullanıcıyı Güncelle')
