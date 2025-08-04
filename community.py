
from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_login import current_user, login_required
from flask_wtf.csrf import validate_csrf
from models import db, CommunityInfo
from forms import CategoryForm, DeleteForm
from functools import wraps

# Admin decorator'ı
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.can_add_user or current_user.can_edit or current_user.can_delete or current_user.is_admin):
            flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
            return redirect(url_for('community.index'))
        return f(*args, **kwargs)
    return decorated_function

# Topluluk erişim decorator'ı
def community_access_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_admin or current_user.is_community_member):
            flash('Bu sayfaya erişim için admin veya topluluk üyesi olmanız gerekiyor.', 'danger')
            return redirect(url_for('community.index'))
        return f(*args, **kwargs)
    return decorated_function

# Forum okuma erişimi (herkese açık)
def community_read_access_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Bu sayfaya erişim için giriş yapmanız gerekiyor.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Blueprint oluşturma
community_bp = Blueprint('community', __name__,
                        static_folder='static')

# --- Modeller ---
class ForumCategory(db.Model):
    __bind_key__ = 'community'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    threads = db.relationship('ForumThread', backref='category', lazy=True)

class ForumThread(db.Model):
    __bind_key__ = 'community'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, nullable=False) # Ana kullanıcı sistemindeki user.id ile eşleşecek
    user_username = db.Column(db.String(80), nullable=False) # Ana kullanıcı sistemindeki user.username
    category_id = db.Column(db.Integer, db.ForeignKey('forum_category.id'), nullable=False)
    posts = db.relationship('ForumPost', backref='thread', lazy=True, cascade="all, delete-orphan")

class ForumPost(db.Model):
    __bind_key__ = 'community'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, nullable=False) # Ana kullanıcı sistemindeki user.id
    user_username = db.Column(db.String(80), nullable=False) # Ana kullanıcı sistemindeki user.username
    thread_id = db.Column(db.Integer, db.ForeignKey('forum_thread.id'), nullable=False)


# --- Rotalar ---
@community_bp.route('/')
@login_required
@community_read_access_required
def index():
    categories = ForumCategory.query.all()
    info = CommunityInfo.query.first()
    return render_template('community_index.html', categories=categories, info=info)

@community_bp.route('/category/<int:category_id>')
@login_required
@community_read_access_required
def view_category(category_id):
    category = ForumCategory.query.get_or_404(category_id)
    threads = ForumThread.query.filter_by(category_id=category_id).order_by(ForumThread.timestamp.desc()).all()
    return render_template('community_category.html', category=category, threads=threads)

@community_bp.route('/thread/<int:thread_id>')
@login_required
@community_read_access_required
def view_thread(thread_id):
    thread = ForumThread.query.get_or_404(thread_id)
    posts = ForumPost.query.filter_by(thread_id=thread_id).order_by(ForumPost.timestamp.asc()).all()
    return render_template('community_thread.html', thread=thread, posts=posts)

@community_bp.route('/new_thread/<int:category_id>', methods=['GET', 'POST'])
@login_required
@community_access_required
def new_thread(category_id):
    category = ForumCategory.query.get_or_404(category_id)
    if request.method == 'POST':
        try:
            # CSRF token doğrulaması
            validate_csrf(request.form.get('csrf_token'))
        except Exception:
            flash('Güvenlik hatası. Lütfen tekrar deneyin.', 'danger')
            return redirect(url_for('community.new_thread', category_id=category_id))
        
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if not title or not content:
            flash('Başlık ve içerik boş olamaz.', 'warning')
            return redirect(url_for('community.new_thread', category_id=category_id))
        
        new_thread = ForumThread(
            title=title, 
            content=content, 
            user_id=current_user.id, 
            user_username=current_user.username,
            category_id=category.id
        )
        db.session.add(new_thread)
        db.session.commit()
        flash('Konu başarıyla oluşturuldu!', 'success')
        return redirect(url_for('community.view_thread', thread_id=new_thread.id))
        
    return render_template('community_new_thread.html', category=category)

@community_bp.route('/new_post/<int:thread_id>', methods=['POST'])
@login_required
@community_access_required
def new_post(thread_id):
    try:
        # CSRF token doğrulaması
        validate_csrf(request.form.get('csrf_token'))
    except Exception:
        flash('Güvenlik hatası. Lütfen tekrar deneyin.', 'danger')
        return redirect(url_for('community.view_thread', thread_id=thread_id))
    
    thread = ForumThread.query.get_or_404(thread_id)
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Mesaj içeriği boş olamaz.', 'warning')
        return redirect(url_for('community.view_thread', thread_id=thread_id))
    
    new_post = ForumPost(
        content=content, 
        user_id=current_user.id,
        user_username=current_user.username,
        thread_id=thread.id
    )
    db.session.add(new_post)
    db.session.commit()
    flash('Cevabınız eklendi.', 'success')
    return redirect(url_for('community.view_thread', thread_id=thread_id))

# --- Admin Rotaları ---
@community_bp.route('/admin/manage_categories', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_categories():
    form = CategoryForm()
    
    if form.validate_on_submit():
        name = form.name.data.strip()
        description = form.description.data.strip() if form.description.data else ''
        
        if not ForumCategory.query.filter_by(name=name).first():
            new_category = ForumCategory(name=name, description=description)
            db.session.add(new_category)
            db.session.commit()
            flash('Yeni kategori eklendi.', 'success')
            return redirect(url_for('community.manage_categories'))
        else:
            flash('Bu isimde bir kategori zaten var.', 'warning')
    
    categories = ForumCategory.query.all()
    return render_template('admin_manage_categories.html', categories=categories, form=form)

@community_bp.route('/admin/delete_category/<int:category_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    try:
        # CSRF token doğrulaması
        validate_csrf(request.form.get('csrf_token'))
        
        category = ForumCategory.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        flash('Kategori silindi.', 'success')
    except Exception as e:
        flash('Güvenlik hatası. Lütfen tekrar deneyin.', 'danger')
    
    return redirect(url_for('community.manage_categories'))

@community_bp.route('/admin/delete_thread/<int:thread_id>', methods=['POST'])
@login_required
@admin_required
def delete_thread(thread_id):
    try:
        # CSRF token doğrulaması
        validate_csrf(request.form.get('csrf_token'))
    except Exception:
        flash('Güvenlik hatası. Lütfen tekrar deneyin.', 'danger')
        return redirect(url_for('community.index'))
    
    thread = ForumThread.query.get_or_404(thread_id)
    category_id = thread.category_id
    db.session.delete(thread)
    db.session.commit()
    flash('Konu silindi.', 'success')
    return redirect(url_for('community.view_category', category_id=category_id))

@community_bp.route('/admin/delete_post/<int:post_id>', methods=['POST'])
@login_required
@admin_required
def delete_post(post_id):
    try:
        # CSRF token doğrulaması
        validate_csrf(request.form.get('csrf_token'))
    except Exception:
        flash('Güvenlik hatası. Lütfen tekrar deneyin.', 'danger')
        return redirect(url_for('community.index'))
    
    post = ForumPost.query.get_or_404(post_id)
    thread_id = post.thread_id
    db.session.delete(post)
    db.session.commit()
    flash('Mesaj silindi.', 'success')
    return redirect(url_for('community.view_thread', thread_id=thread_id))

@community_bp.route('/admin/community_info', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_community_info():
    info = CommunityInfo.query.first()
    if request.method == 'POST':
        if not info:
            info = CommunityInfo(
                title=request.form['title'],
                content=request.form['content'],
                image_url=request.form['image_url']
            )
            db.session.add(info)
        else:
            info.title = request.form['title']
            info.content = request.form['content']
            info.image_url = request.form['image_url']
        db.session.commit()
        flash('Topluluk bilgileri güncellendi.', 'success')
        return redirect(url_for('community.admin_community_info'))
    
    return render_template('admin_community_info.html', info=info)
