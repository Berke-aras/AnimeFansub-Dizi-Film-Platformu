from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Many-to-many ilişki için yardımcı tablo
anime_genres = db.Table('anime_genres',
    db.Column('anime_id', db.Integer, db.ForeignKey('anime.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    can_delete = db.Column(db.Boolean, default=False)
    can_edit = db.Column(db.Boolean, default=False)
    can_add_user = db.Column(db.Boolean, default=False)
    logs = db.relationship('Log', backref='user', lazy=True)

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

class Anime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cover_image = db.Column(db.String(200), nullable=False)
    episodes = db.relationship('Episode', backref='anime', lazy=True, cascade="all, delete-orphan")
    
    # Yeni eklenen alanlar
    release_year = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), nullable=True) # Örn: 'Devam Ediyor', 'Bitti'
    anime_type = db.Column(db.String(50), nullable=True) # Örn: 'TV', 'Film', 'OVA'

    # İlişki
    genres = db.relationship('Genre', secondary=anime_genres, lazy='subquery',
        backref=db.backref('animes', lazy=True))

class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    sources = db.Column(db.Text, nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
