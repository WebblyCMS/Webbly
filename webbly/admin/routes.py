from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import Post, Page, User, Comment, Theme, Plugin, Setting
from . import admin_bp
from .forms import PostForm, PageForm, SettingsForm, ThemeForm, PluginForm
from ..utils.decorators import admin_required
from ..utils.media import save_image

@admin_bp.route('/dash')
@login_required
@admin_required
def dashboard():
    # Get counts for dashboard stats
    post_count = Post.query.count()
    page_count = Page.query.count()
    comment_count = Comment.query.count()
    user_count = User.query.count()
    
    # Get recent activity
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         post_count=post_count,
                         page_count=page_count,
                         comment_count=comment_count,
                         user_count=user_count,
                         recent_posts=recent_posts,
                         recent_comments=recent_comments,
                         recent_users=recent_users)

@admin_bp.route('/posts')
@login_required
@admin_required
def posts():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/posts.html', posts=posts)

@admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            excerpt=form.excerpt.data,
            published=form.published.data,
            author=current_user
        )
        if form.featured_image.data:
            image_path = save_image(form.featured_image.data)
            post.featured_image = image_path
            
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('admin.posts'))
    
    return render_template('admin/post_editor.html', form=form, title="New Post")

@admin_bp.route('/post/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    form = PostForm(obj=post)
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.excerpt = form.excerpt.data
        post.published = form.published.data
        
        if form.featured_image.data:
            image_path = save_image(form.featured_image.data)
            post.featured_image = image_path
            
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('admin.posts'))
        
    return render_template('admin/post_editor.html', form=form, post=post, title="Edit Post")

@admin_bp.route('/pages')
@login_required
@admin_required
def pages():
    pages = Page.query.order_by(Page.title).all()
    return render_template('admin/pages.html', pages=pages)

@admin_bp.route('/page/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_page():
    form = PageForm()
    if form.validate_on_submit():
        page = Page(
            title=form.title.data,
            content=form.content.data,
            template=form.template.data,
            published=form.published.data,
            author=current_user
        )
        db.session.add(page)
        db.session.commit()
        flash('Page created successfully!', 'success')
        return redirect(url_for('admin.pages'))
    
    return render_template('admin/page_editor.html', form=form, title="New Page")

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        for field in form:
            if field.name != 'submit':
                setting = Setting.query.filter_by(key=field.name).first()
                if setting:
                    setting.value = field.data
                else:
                    setting = Setting(key=field.name, value=field.data)
                    db.session.add(setting)
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.settings'))
        
    # Load current settings
    settings = Setting.query.all()
    for setting in settings:
        if hasattr(form, setting.key):
            getattr(form, setting.key).data = setting.value
            
    return render_template('admin/settings.html', form=form)

@admin_bp.route('/themes')
@login_required
@admin_required
def themes():
    themes = Theme.query.all()
    return render_template('admin/themes.html', themes=themes)

@admin_bp.route('/theme/<int:id>/activate', methods=['POST'])
@login_required
@admin_required
def activate_theme(id):
    # Deactivate current theme
    Theme.query.filter_by(active=True).update({Theme.active: False})
    
    # Activate new theme
    theme = Theme.query.get_or_404(id)
    theme.active = True
    db.session.commit()
    
    flash(f'Theme "{theme.name}" activated successfully!', 'success')
    return redirect(url_for('admin.themes'))

@admin_bp.route('/plugins')
@login_required
@admin_required
def plugins():
    plugins = Plugin.query.all()
    return render_template('admin/plugins.html', plugins=plugins)

@admin_bp.route('/plugin/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_plugin(id):
    plugin = Plugin.query.get_or_404(id)
    plugin.active = not plugin.active
    db.session.commit()
    
    status = 'activated' if plugin.active else 'deactivated'
    flash(f'Plugin "{plugin.name}" {status} successfully!', 'success')
    return redirect(url_for('admin.plugins'))

@admin_bp.route('/comments')
@login_required
@admin_required
def comments():
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.order_by(Comment.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/comments.html', comments=comments)

@admin_bp.route('/comment/<int:id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.approved = True
    db.session.commit()
    flash('Comment approved successfully!', 'success')
    return redirect(url_for('admin.comments'))

@admin_bp.route('/comment/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully!', 'success')
    return redirect(url_for('admin.comments'))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.order_by(User.username).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/user/<int:id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(id):
    if current_user.id == id:
        flash('You cannot modify your own admin status!', 'error')
        return redirect(url_for('admin.users'))
        
    user = User.query.get_or_404(id)
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin privileges {status} for user "{user.username}"', 'success')
    return redirect(url_for('admin.users'))
