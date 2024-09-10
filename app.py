from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, AnimeForm, EpisodeForm, UserForm, EditUserForm
from models import db, User, Anime, Episode, Log
import re


# Uygulamanızın diğer başlangıç kodları...


app = Flask(__name__)
application = app
app.config['SECRET_KEY'] = 'asd*fasd-dsdsaf+fa+fd,aadsf,af,.d,f.daf*f9d88asd7asdf68sdf567as47'
#https bağlantısı yoksa sorun çıkartıyor dikkat et
# app.config['SESSION_COOKIE_SECURE'] = True 
# app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anime_site.db'
db.init_app(app)



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'




def log_action(action, description):
    new_log = Log(action=action, description=description, user_id=current_user.id)
    db.session.add(new_log)
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)  # URL'den sayfa numarasını al
    animes = Anime.query.order_by().paginate(page=page, per_page=15)  # 15 animeyi getir
    return render_template('index.html', animes=animes)

@app.route('/copyright')
def copyright():
    return render_template('copyright.html')


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
        genres = form.genres.data if form.genres.data else 'Unknown'  # Boşsa varsayılan bir değer ata
        anime = Anime(name=form.name.data, description=form.description.data, cover_image=form.cover_image.data, genres=genres)
        db.session.add(anime)
        db.session.commit()
        
        # Log kaydı ekle
        log_action('add', f'Anime "{form.name.data}" eklendi.')
        
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
        anime = Anime.query.get(anime_id)
        log_action('add', f'Anime "{anime.name}" için bölüm {form.number.data} eklendi.')
        flash('Bölüm başarıyla eklendi.', 'success')
        return redirect(url_for('anime', anime_id=anime_id))
    return render_template('add_episode.html', form=form)


@app.route('/delete_anime/<int:anime_id>', methods=['POST'])
@login_required
def delete_anime(anime_id):
    if not current_user.can_delete:
        flash('Silme yetkiniz yok!', 'danger')
        return redirect(url_for('admin'))

    anime = Anime.query.get_or_404(anime_id)
    if anime:
        anime_name = anime.name  # Log için anime adını kaydediyoruz
        Episode.query.filter_by(anime_id=anime_id).delete()
        db.session.delete(anime)
        db.session.commit()
        log_action('delete', f'Anime "{anime_name}" silindi.')
        flash('Anime ve ilgili bölümler başarıyla silindi.', 'success')
    return redirect(url_for('admin'))

@app.route('/delete_episode/<int:episode_id>', methods=['POST'])
@login_required
def delete_episode(episode_id):
    if not current_user.can_delete:
        flash('Bu işlemi gerçekleştirme yetkiniz yok.', 'danger')
        return redirect(url_for('anime', anime_id=Episode.query.get_or_404(episode_id).anime_id))
    
    episode = Episode.query.get_or_404(episode_id)
    anime_id = episode.anime_id
    db.session.delete(episode)
    db.session.commit()

    # Log kaydı ekle
    log_action('delete', f'Bölüm {episode.number} silindi. Anime ID: {anime_id}')

    flash('Bölüm başarıyla silindi.', 'success')
    return redirect(url_for('anime', anime_id=anime_id))


@app.route('/edit_episode/<int:episode_id>', methods=['GET', 'POST'])
@login_required
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

        # Log kaydı ekle
        log_action('edit', f'Bölüm {old_number} güncellendi. Yeni numara: {form.number.data}, Eski kaynaklar: {old_sources}, Yeni kaynaklar: {form.sources.data}')

        flash('Bölüm başarıyla güncellendi.', 'success')
        return redirect(url_for('anime', anime_id=episode.anime_id))

    form.number.data = episode.number
    form.sources.data = episode.sources
    return render_template('edit_episode.html', form=form, episode=episode)




@app.route('/edit_anime/<int:anime_id>', methods=['GET', 'POST'])
@login_required
def edit_anime(anime_id):
    if not current_user.can_edit:
        flash('Düzenleme yetkiniz yok!', 'danger')
        return redirect(url_for('admin'))

    anime = Anime.query.get_or_404(anime_id)
    form = AnimeForm(obj=anime)
    
    if form.validate_on_submit():
        anime_name_before = anime.name
        anime.name = form.name.data
        anime.description = form.description.data
        anime.cover_image = form.cover_image.data
        anime.genres = form.genres.data
        db.session.commit()
        log_action('update', f'Anime "{anime_name_before}" düzenlendi.')
        flash('Anime başarıyla güncellendi.', 'success')
        return redirect(url_for('admin'))
    
    return render_template('edit_anime.html', form=form, anime=anime)



@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    # Basic input validation, for example, restricting certain special characters.
    if not re.match("^[A-Za-z0-9 ]*$", query):
        flash('Invalid search query', 'danger')
        return redirect(url_for('index'))

    # Use ORM to prevent SQL injection
    results = Anime.query.filter(Anime.name.like(f"%{query}%")).all()
    return render_template('search_results.html', query=query, results=results)


@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.can_add_user:
        flash('Yetkiniz yok!', 'danger')
        return redirect(url_for('admin'))

    form = UserForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, 
                        password=hashed_password,
                        can_delete=form.can_delete.data,
                        can_edit=form.can_edit.data,
                        can_add_user=form.can_add_user.data)
        db.session.add(new_user)
        db.session.commit()

        # Log kaydı ekle
        log_action('add_user', f'Yeni kullanıcı eklendi: {form.username.data}, Silme yetkisi: {form.can_delete.data}, Düzenleme yetkisi: {form.can_edit.data}, Kullanıcı ekleme yetkisi: {form.can_add_user.data}')

        flash('Kullanıcı başarıyla eklendi!', 'success')
        return redirect(url_for('admin'))
    return render_template('add_user.html', form=form)



@app.route('/logs')
@login_required
def view_logs():
    if not current_user.can_add_user:
        flash('Bu sayfayı görüntüleme yetkiniz yok.', 'danger')
        return redirect(url_for('index'))
    
    
    page = request.args.get('page', 1, type=int)  # URL'den sayfa numarasını al
    logs = Log.query.order_by(Log.timestamp.desc()).paginate(page=page, per_page=10) 
    return render_template('log.html', logs=logs)


@app.route('/users')
@login_required
def users():
    if not current_user.can_add_user:
        flash('Bu sayfayı görüntüleme yetkiniz yok.', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
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

        # Log kaydı ekle
        log_action('edit_user', f'Kullanıcı "{user.username}" güncellendi.')

        flash('Kullanıcı başarıyla güncellendi.', 'success')
        return redirect(url_for('admin'))

    return render_template('edit_user.html', form=form, user=user)



@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if not current_user.can_delete:
        flash('Bu sayfayı görüntüleme yetkiniz yok.', 'danger')
        return redirect(url_for('index'))
    
    # Kullanıcıya ait log kayıtlarını güncelleyin
    logs = Log.query.filter_by(user_id=user_id).all()
    for log in logs:
        log.user_id = None
    
    db.session.commit()
    
    # Kullanıcıyı sil
    db.session.delete(user)
    db.session.commit()
    
    flash('Kullanıcı başarıyla silindi!', 'success')
    return redirect(url_for('users'))





@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))




# @app.after_request
# def add_security_headers(response):
#     response.headers['X-Frame-Options'] = 'DENY'
#     response.headers['X-Content-Type-Options'] = 'nosniff'
#     return response

# import os
# app.secret_key = os.urandom(24)  
# Rastgele güçlü bir anahtar

if __name__ == '__main__':
    # app.run(debug=False, host='0.0.0.0')
    app.run(debug=True, host='0.0.0.0', port=5000)