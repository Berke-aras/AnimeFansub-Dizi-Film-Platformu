from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, AnimeForm, EpisodeForm
from models import db, User, Anime, Episode


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anime_site.db'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    animes = Anime.query.all()
    return render_template('index.html', animes=animes)

@app.route('/anime/<int:anime_id>')
def anime(anime_id):
    anime = Anime.query.get_or_404(anime_id)
    return render_template('anime.html', anime=anime)

@app.route('/episode/<int:episode_id>')
def episode(episode_id):
    episode = Episode.query.get_or_404(episode_id)
    sources = episode.sources.split(',')
    return render_template('episode.html', episode=episode, sources=sources)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    animes = Anime.query.all()
    return render_template('admin.html', animes=animes)

@app.route('/add_anime', methods=['GET', 'POST'])
@login_required
def add_anime():
    form = AnimeForm()
    if form.validate_on_submit():
        anime = Anime(name=form.name.data, description=form.description.data, cover_image=form.cover_image.data)
        db.session.add(anime)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('add_anime.html', form=form)

@app.route('/add_episode/<int:anime_id>', methods=['GET', 'POST'])
@login_required
def add_episode(anime_id):
    form = EpisodeForm()
    if form.validate_on_submit():
        episode = Episode(number=form.number.data, sources=form.sources.data, anime_id=anime_id)
        db.session.add(episode)
        db.session.commit()
        return redirect(url_for('anime', anime_id=anime_id))
    return render_template('add_episode.html', form=form)
@app.route('/delete_anime/<int:anime_id>', methods=['POST'])
@login_required
def delete_anime(anime_id):
    anime = Anime.query.get_or_404(anime_id)
    if anime:
        # Önce animeye bağlı tüm bölümleri sil
        Episode.query.filter_by(anime_id=anime_id).delete()
        db.session.delete(anime)
        db.session.commit()
        flash('Anime ve ilgili bölümler başarıyla silindi.', 'success')
    return redirect(url_for('admin'))

@app.route('/delete_episode/<int:episode_id>', methods=['POST'])
@login_required
def delete_episode(episode_id):
    episode = Episode.query.get_or_404(episode_id)
    anime_id = episode.anime_id
    db.session.delete(episode)
    db.session.commit()
    return redirect(url_for('anime', anime_id=anime_id))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)