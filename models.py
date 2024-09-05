from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Anime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cover_image = db.Column(db.String(150), nullable=False)
    episodes = db.relationship('Episode', backref='anime', lazy=True)

class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    sources = db.Column(db.Text, nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)