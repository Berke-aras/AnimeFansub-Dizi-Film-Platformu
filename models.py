from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Many-to-many ilişki için yardımcı tablolar
anime_genres = db.Table('anime_genres',
    db.Column('anime_id', db.Integer, db.ForeignKey('anime.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

watchlist = db.Table('watchlist',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('anime_id', db.Integer, db.ForeignKey('anime.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    can_delete = db.Column(db.Boolean, default=False)
    can_edit = db.Column(db.Boolean, default=False)
    can_add_user = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_community_member = db.Column(db.Boolean, default=False)
    logs = db.relationship('Log', backref='user', lazy=True)
    watchlist_animes = db.relationship('Anime', secondary=watchlist, lazy='subquery',
        backref=db.backref('watchlisted_by', lazy=True))
    ratings = db.relationship('Rating', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade="all, delete-orphan")

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
    
    release_year = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), nullable=True)
    anime_type = db.Column(db.String(50), nullable=True)

    # Yeni Puanlama Alanları
    average_rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)

    # MyAnimeList Integration
    mal_id = db.Column(db.Integer, nullable=True)
    mal_score = db.Column(db.Float, nullable=True)
    mal_url = db.Column(db.String(200), nullable=True)

    genres = db.relationship('Genre', secondary=anime_genres, lazy='subquery',
        backref=db.backref('animes', lazy=True))
    ratings = db.relationship('Rating', backref='anime', lazy=True, cascade="all, delete-orphan")

class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    sources = db.Column(db.Text, nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=True) # Optional: link notification to an anime

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref='news_posts')
    is_pinned = db.Column(db.Boolean, default=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref='events')

class CommunityInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)

class CommunityMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    place_of_birth = db.Column(db.String(100), nullable=False)  # Doğum ili/ülke
    date_of_birth = db.Column(db.Date, nullable=False)
    current_residence = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(20), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    student_class = db.Column(db.String(50), nullable=False)
    faculty = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    preferred_units = db.Column(db.Text, nullable=True)  # JSON string for multiple selections
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Link to User after approval
    user = db.relationship('User', backref='community_profile')