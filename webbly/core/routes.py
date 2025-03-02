from flask import render_template, redirect, url_for, request, current_app, abort
from ..models import Post, Page, Theme, Setting, Comment
from . import core_bp
from ..utils.theme import get_active_theme, get_theme_template
from ..utils.settings import get_setting

@core_bp.route('/')
def index():
    # Get site settings
    site_title = get_setting('site_title', 'Webbly Site')
    posts_per_page = int(get_setting('posts_per_page', '10'))
    
    # Get active theme
    theme = get_active_theme()
    if not theme:
        return "No active theme found. Please activate a theme in the admin panel."
    
    # Get posts with pagination
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(published=True)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=posts_per_page, error_out=False)
    
    template = get_theme_template(theme.directory, 'index.html')
    return render_template(template,
                         title=site_title,
                         posts=posts,
                         theme=theme)

@core_bp.route('/post/<string:slug>')
def post(slug):
    post = Post.query.filter_by(slug=slug, published=True).first_or_404()
    theme = get_active_theme()
    
    if not theme:
        return "No active theme found. Please activate a theme in the admin panel."
    
    template = get_theme_template(theme.directory, 'post.html')
    return render_template(template,
                         title=post.title,
                         post=post,
                         theme=theme)

@core_bp.route('/page/<string:slug>')
def page(slug):
    page = Page.query.filter_by(slug=slug, published=True).first_or_404()
    theme = get_active_theme()
    
    if not theme:
        return "No active theme found. Please activate a theme in the admin panel."
    
    # Use custom template if specified, otherwise use default page template
    if page.template and page.template != 'default':
        template = get_theme_template(theme.directory, f'page-{page.template}.html')
    else:
        template = get_theme_template(theme.directory, 'page.html')
    
    return render_template(template,
                         title=page.title,
                         page=page,
                         theme=theme)

@core_bp.route('/post/<string:slug>/comment', methods=['POST'])
def add_comment(slug):
    post = Post.query.filter_by(slug=slug, published=True).first_or_404()
    
    # Check if comments are enabled
    if not get_setting('enable_comments', 'true').lower() == 'true':
        abort(403)
    
    # Create comment (implement user authentication check here)
    comment = Comment(
        content=request.form.get('content'),
        post=post,
        approved=False  # Set to True if auto-approve is enabled
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return redirect(url_for('core.post', slug=slug))

@core_bp.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('core.index'))
    
    # Search in posts and pages
    posts = Post.query.filter(
        Post.published == True,
        (Post.title.contains(query) | Post.content.contains(query))
    ).all()
    
    pages = Page.query.filter(
        Page.published == True,
        (Page.title.contains(query) | Page.content.contains(query))
    ).all()
    
    theme = get_active_theme()
    template = get_theme_template(theme.directory, 'search.html')
    
    return render_template(template,
                         title=f'Search: {query}',
                         query=query,
                         posts=posts,
                         pages=pages,
                         theme=theme)

@core_bp.route('/feed')
def feed():
    # Implement RSS feed
    posts = Post.query.filter_by(published=True)\
        .order_by(Post.created_at.desc())\
        .limit(10)\
        .all()
    
    # Generate RSS feed (implement proper RSS generation)
    return "RSS Feed - To be implemented"

@core_bp.route('/sitemap.xml')
def sitemap():
    # Implement XML sitemap
    return "Sitemap - To be implemented"
