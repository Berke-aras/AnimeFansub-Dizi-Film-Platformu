from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, AnimeForm, EpisodeForm, UserForm, EditUserForm, GenreForm, AnimeSearchForm, RegistrationForm
from models import db, User, Anime, Episode, Log, Genre, Rating
import re
import random
from functools import wraps
import requests

app = Flask(__name__)
application = app
app.config['SECRET_KEY'] = 'asd*fasd-dsdsaf+fa+fd,aadsf,af,.d,f.daf*f9d88asd7asdf68sdf567as47'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anime_site.db'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.can_add_user or current_user.can_edit or current_user.can_delete):
            flash('Bu sayfayı görüntüleme yetkiniz yok.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def update_mal_data(anime):
    try:
        response = requests.get(f'https://api.jikan.moe/v4/anime?q={anime.name}&limit=1')
        if response.status_code == 200:
            data = response.json().get('data')
            if data:
                mal_anime = data[0]
                anime.mal_id = mal_anime.get('mal_id')
                anime.mal_score = mal_anime.get('score')
                anime.mal_url = mal_anime.get('url')
    except requests.exceptions.RequestException as e:
        flash(f'MyAnimeList verileri alınamadı: {e}', 'warning')

def log_action(action, description):
    if current_user.is_authenticated:
        new_log = Log(action=action, description=description, user_id=current_user.id)
        db.session.add(new_log)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Hesabınız oluşturuldu! Şimdi giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Kayıt Ol', form=form)

@app.route('/')
def index():
    editor_picks = Anime.query.filter(Anime.genres.any(Genre.name == 'Oneri')).limit(6).all()
    user_genres = session.get('user_genres', {})
    personalized_recs = []
    if user_genres:
        sorted_genres = sorted(user_genres.items(), key=lambda x: x[1], reverse=True)
        top_genre_ids = [int(g[0]) for g in sorted_genres[:3]]
        if top_genre_ids:
            personalized_recs = Anime.query.filter(Anime.genres.any(Genre.id.in_(top_genre_ids))).limit(6).all()
    latest_animes = Anime.query.order_by(Anime.id.desc()).limit(6).all()
    random_animes = random.sample(Anime.query.all(), min(len(Anime.query.all()), 6))
    return render_template('index.html', editor_picks=editor_picks, personalized_recs=personalized_recs, latest_animes=latest_animes, random_animes=random_animes)

@app.route('/animes', methods=['GET', 'POST'])
def animes():
    form = AnimeSearchForm(request.values)
    form.genre.choices = [('', 'Tüm Türler')] + [(str(g.id), g.name) for g in Genre.query.order_by('name').all()]
    query = Anime.query
    if form.validate_on_submit() or request.method == 'GET':
        search_query = form.query.data or request.args.get('query')
        if search_query:
            query = query.filter(Anime.name.ilike(f"%{search_query}%"))
    if form.genre.data:
        query = query.filter(Anime.genres.any(id=int(form.genre.data)))
    if form.release_year.data:
        query = query.filter_by(release_year=form.release_year.data)
    if form.anime_type.data:
        query = query.filter_by(anime_type=form.anime_type.data)
    sort_option = form.sort_by.data or 'name_asc'
    if sort_option == 'name_asc':
        query = query.order_by(Anime.name.asc())
    elif sort_option == 'name_desc':
        query = query.order_by(Anime.name.desc())
    elif sort_option == 'rating_desc':
        query = query.order_by(Anime.average_rating.desc())
    elif sort_option == 'year_desc':
        query = query.order_by(Anime.release_year.desc())
    page = request.args.get('page', 1, type=int)
    animes = query.paginate(page=page, per_page=18, error_out=False)
    return render_template('all_animes.html', animes=animes, form=form)

@app.route('/episode/<int:episode_id>')
def episode(episode_id):
    episode = Episode.query.get_or_404(episode_id)
    sources = episode.sources.split(',')
    user_genres = session.get('user_genres', {})
    for genre in episode.anime.genres:
        user_genres[str(genre.id)] = user_genres.get(str(genre.id), 0) + 1
    session['user_genres'] = user_genres
    return render_template('episode.html', episode=episode, sources=sources)

@app.route('/admin/genres', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_genres():
    form = GenreForm()
    if form.validate_on_submit():
        new_genre = Genre(name=form.name.data)
        db.session.add(new_genre)
        db.session.commit()
        flash(f'"{form.name.data}" türü eklendi.', 'success')
        return redirect(url_for('manage_genres'))
    genres = Genre.query.all()
    return render_template('manage_genres.html', form=form, genres=genres)

@app.route('/admin/delete_genre/<int:genre_id>', methods=['POST'])
@login_required
@admin_required
def delete_genre(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    db.session.delete(genre)
    db.session.commit()
    flash(f'"{genre.name}" türü silindi.', 'success')
    return redirect(url_for('manage_genres'))

@app.route('/add_anime', methods=['GET', 'POST'])
@login_required
@admin_required
def add_anime():
    form = AnimeForm()
    if form.validate_on_submit():
        new_anime = Anime(name=form.name.data, description=form.description.data, cover_image=form.cover_image.data, release_year=form.release_year.data, status=form.status.data, anime_type=form.anime_type.data)
        if form.mal_score.data:
            new_anime.mal_score = float(form.mal_score.data)
        if form.mal_url.data:
            new_anime.mal_url = form.mal_url.data
        if not new_anime.mal_score:
            update_mal_data(new_anime)
        for genre in form.genres.data:
            new_anime.genres.append(genre)
        db.session.add(new_anime)
        db.session.commit()
        log_action('add', f'Anime "{new_anime.name}" eklendi.')
        return redirect(url_for('admin'))
    return render_template('add_anime.html', form=form)

@app.route('/edit_anime/<int:anime_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_anime(anime_id):
    anime = Anime.query.get_or_404(anime_id)
    form = AnimeForm(obj=anime)
    if form.validate_on_submit():
        anime.name = form.name.data
        anime.description = form.description.data
        anime.cover_image = form.cover_image.data
        anime.release_year = form.release_year.data
        anime.status = form.status.data
        anime.anime_type = form.anime_type.data
        if form.mal_score.data:
            anime.mal_score = float(form.mal_score.data)
        if form.mal_url.data:
            anime.mal_url = form.mal_url.data
        if not anime.mal_score:
            update_mal_data(anime)
        db.session.commit()
        log_action('update', f'Anime "{anime.name}" düzenlendi.')
        return redirect(url_for('admin'))
    assigned_genres = anime.genres
    unassigned_genres = [genre for genre in Genre.query.all() if genre not in assigned_genres]
    return render_template('edit_anime.html', form=form, anime=anime, assigned_genres=assigned_genres, unassigned_genres=unassigned_genres)

@app.route('/copyright')
def copyright():
    return render_template('copyright.html')

@app.route('/anime/<int:anime_id>')
def anime(anime_id):
    anime = Anime.query.get_or_404(anime_id)
    user_rating = None
    is_in_watchlist = False
    if current_user.is_authenticated:
        user_rating = Rating.query.filter_by(user_id=current_user.id, anime_id=anime.id).first()
        is_in_watchlist = anime in current_user.watchlist_animes
    return render_template('anime.html', anime=anime, user_rating=user_rating, is_in_watchlist=is_in_watchlist)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Giriş başarısız. Lütfen kullanıcı adınızı ve şifrenizi kontrol edin.', 'danger')
    return render_template('login.html', form=form)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def admin():
    animes = Anime.query.all()
    return render_template('admin.html', animes=animes)

@app.route('/add_episode/<int:anime_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def add_episode(anime_id):
    form = EpisodeForm()
    if form.validate_on_submit():
        episode = Episode(number=form.number.data, sources=form.sources.data, anime_id=anime_id)
        db.session.add(episode)
        db.session.commit()
        anime = Anime.query.get(anime_id)
        log_action('add', f'Anime "{anime.name}" için bölüm {form.number.data} eklendi.')
        flash('Bölüm başarıyla eklendi.', 'success')
        return redirect(url_for('anime', anime_id=anime_id))
    return render_template('add_episode.html', form=form)

@app.route('/delete_anime/<int:anime_id>', methods=['POST'])
@login_required
@admin_required
def delete_anime(anime_id):
    if not current_user.can_delete:
        flash('Silme yetkiniz yok!', 'danger')
        return redirect(url_for('admin'))
    anime = Anime.query.get_or_404(anime_id)
    if anime:
        anime_name = anime.name
        Episode.query.filter_by(anime_id=anime_id).delete()
        db.session.delete(anime)
        db.session.commit()
        log_action('delete', f'Anime "{anime_name}" silindi.')
        flash('Anime ve ilgili bölümler başarıyla silindi.', 'success')
    return redirect(url_for('admin'))

@app.route('/delete_episode/<int:episode_id>', methods=['POST'])
@login_required
@admin_required
def delete_episode(episode_id):
    if not current_user.can_delete:
        flash('Bu işlemi gerçekleştirme yetkiniz yok.', 'danger')
        return redirect(url_for('anime', anime_id=Episode.query.get_or_404(episode_id).anime_id))
    episode = Episode.query.get_or_404(episode_id)
    anime_id = episode.anime_id
    db.session.delete(episode)
    db.session.commit()
    log_action('delete', f'Bölüm {episode.number} silindi. Anime ID: {anime_id}')
    flash('Bölüm başarıyla silindi.', 'success')
    return redirect(url_for('anime', anime_id=anime_id))

@app.route('/edit_episode/<int:episode_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_episode(episode_id):
    if not current_user.can_edit:
        flash('Bu işlemi gerçekleştirme yetkiniz yok.', 'danger')
        return redirect(url_for('anime', anime_id=Episode.query.get_or_404(episode_id).anime_id))
    episode = Episode.query.get_or_404(episode_id)
    form = EpisodeForm()
    if form.validate_on_submit():
        old_number = episode.number
        old_sources = episode.sources
        episode.number = form.number.data
        episode.sources = form.sources.data
        db.session.commit()
        log_action('edit', f'Bölüm {old_number} güncellendi. Yeni numara: {form.number.data}, Eski kaynaklar: {old_sources}, Yeni kaynaklar: {form.sources.data}')
        flash('Bölüm başarıyla güncellendi.', 'success')
        return redirect(url_for('anime', anime_id=episode.anime_id))
    form.number.data = episode.number
    form.sources.data = episode.sources
    return render_template('edit_episode.html', form=form, episode=episode)

@app.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if not current_user.can_add_user:
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('admin'))
    form = UserForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, password=hashed_password, can_delete=form.can_delete.data, can_edit=form.can_edit.data, can_add_user=form.can_add_user.data)
        db.session.add(new_user)
        db.session.commit()
        log_action('add_user', f'Yeni kullanıcı eklendi: {form.username.data}, Silme yetkisi: {form.can_delete.data}, Düzenleme yetkisi: {form.can_edit.data}, Kullanıcı ekleme yetkisi: {form.can_add_user.data}')
        flash('Kullanıcı başarıyla eklendi!', 'success')
        return redirect(url_for('admin'))
    return render_template('add_user.html', form=form)

@app.route('/logs')
@login_required
@admin_required
def view_logs():
    if not current_user.can_add_user:
        flash('Bu sayfayı görüntüleme yetkiniz yok.', 'danger')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    logs = Log.query.order_by(Log.timestamp.desc()).paginate(page=page, per_page=10)
    return render_template('log.html', logs=logs)

@app.route('/users')
@login_required
@admin_required
def users():
    if not current_user.can_add_user:
        flash('Bu sayfayı görüntüleme yetkiniz yok.', 'danger')
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    if not current_user.can_add_user:
        flash('Bu işlemi gerçekleştirme yetkiniz yok.', 'danger')
        return redirect(url_for('admin'))
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.can_delete = form.can_delete.data
        user.can_edit = form.can_edit.data
        user.can_add_user = form.can_add_user.data
        db.session.commit()
        log_action('edit_user', f'Kullanıcı "{user.username}" güncellendi.')
        flash('Kullanıcı başarıyla güncellendi.', 'success')
        return redirect(url_for('admin'))
    return render_template('edit_user.html', form=form, user=user)

@app.route('/api/watchlist/<int:anime_id>', methods=['POST'])
@login_required
def toggle_watchlist(anime_id):
    anime = Anime.query.get_or_404(anime_id)
    if anime in current_user.watchlist_animes:
        current_user.watchlist_animes.remove(anime)
        status = 'removed'
    else:
        current_user.watchlist_animes.append(anime)
        status = 'added'
    db.session.commit()
    return jsonify({'status': status})

@app.route('/api/rate/<int:anime_id>', methods=['POST'])
@login_required
def rate_anime(anime_id):
    anime = Anime.query.get_or_404(anime_id)
    score = request.json.get('score')
    if not score or not 1 <= score <= 5:
        return jsonify({'status': 'error', 'message': 'Invalid score'}), 400
    rating = Rating.query.filter_by(user_id=current_user.id, anime_id=anime.id).first()
    if rating:
        rating.score = score
    else:
        rating = Rating(user_id=current_user.id, anime_id=anime.id, score=score)
        db.session.add(rating)
    total_ratings = db.session.query(db.func.sum(Rating.score)).filter(Rating.anime_id == anime.id).scalar()
    count_ratings = db.session.query(db.func.count(Rating.id)).filter(Rating.anime_id == anime.id).scalar()
    anime.average_rating = total_ratings / count_ratings
    anime.rating_count = count_ratings
    db.session.commit()
    return jsonify({'status': 'success', 'new_average': anime.average_rating, 'rating_count': anime.rating_count})

@app.route('/profile')
@login_required
def profile():
    watchlist = current_user.watchlist_animes
    user_ratings = Rating.query.filter_by(user_id=current_user.id).order_by(Rating.score.desc()).all()
    return render_template('profile.html', watchlist=watchlist, user_ratings=user_ratings)

@app.route('/api/anime/<int:anime_id>/genre/add/<int:genre_id>', methods=['POST'])
@login_required
@admin_required
def add_genre_to_anime(anime_id, genre_id):
    anime = Anime.query.get_or_404(anime_id)
    genre = Genre.query.get_or_404(genre_id)
    if genre not in anime.genres:
        anime.genres.append(genre)
        db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/api/anime/<int:anime_id>/genre/remove/<int:genre_id>', methods=['POST'])
@login_required
@admin_required
def remove_genre_from_anime(anime_id, genre_id):
    anime = Anime.query.get_or_404(anime_id)
    genre = Genre.query.get_or_404(genre_id)
    if genre in anime.genres:
        anime.genres.remove(genre)
        db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if not current_user.can_delete:
        flash('Bu sayfayı görüntüleme yetkiniz yok.', 'danger')
        return redirect(url_for('index'))
    logs = Log.query.filter_by(user_id=user_id).all()
    for log in logs:
        log.user_id = None
    db.session.commit()
    db.session.delete(user)
    db.session.commit()
    flash('Kullanıcı başarıyla silindi!', 'success')
    return redirect(url_for('users'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5400)