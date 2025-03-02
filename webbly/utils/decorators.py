from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """Decorator to require admin privileges for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def setup_required(f):
    """Decorator to ensure CMS is set up before accessing route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from ..models import User
        if not User.query.first():
            return redirect(url_for('auth.register'))
        return f(*args, **kwargs)
    return decorated_function

def theme_required(f):
    """Decorator to ensure an active theme exists."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from ..models import Theme
        if not Theme.query.filter_by(active=True).first():
            if current_user.is_authenticated and current_user.is_admin:
                return redirect(url_for('admin.themes'))
            abort(500, description="No active theme found")
        return f(*args, **kwargs)
    return decorated_function

def maintenance_mode(f):
    """Decorator to handle maintenance mode."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from ..utils.settings import get_setting
        maintenance_mode = get_setting('maintenance_mode', 'false').lower() == 'true'
        if maintenance_mode and not (current_user.is_authenticated and current_user.is_admin):
            return render_template('maintenance.html')
        return f(*args, **kwargs)
    return decorated_function

def cache_control(max_age=0, private=False, no_store=False):
    """Decorator to set cache control headers."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            if private:
                response.cache_control.private = True
            if no_store:
                response.cache_control.no_store = True
            response.cache_control.max_age = max_age
            return response
        return decorated_function
    return decorator

def plugin_enabled(plugin_name):
    """Decorator to check if a plugin is enabled."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from ..models import Plugin
            plugin = Plugin.query.filter_by(name=plugin_name, active=True).first()
            if not plugin:
                abort(404)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
