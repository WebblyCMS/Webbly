import os
import re
import hashlib
from functools import wraps
from datetime import datetime, timedelta
from flask import current_app, request, abort, session
from flask_login import current_user
from werkzeug.security import safe_str_cmp
from .models import User, db
from .logging import log_security

class Security:
    """Security manager for Webbly CMS."""
    
    def __init__(self, app=None):
        self.app = app
        self.login_attempts = {}
        self.blocked_ips = set()
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize security with Flask application."""
        self.app = app
        
        # Security settings
        app.config.setdefault('MAX_LOGIN_ATTEMPTS', 5)
        app.config.setdefault('LOGIN_LOCKOUT_TIME', 15)  # minutes
        app.config.setdefault('PASSWORD_MIN_LENGTH', 8)
        app.config.setdefault('REQUIRE_PASSWORD_COMPLEXITY', True)
        app.config.setdefault('SESSION_LIFETIME', 24)  # hours
        app.config.setdefault('CSRF_TOKEN_VALID_TIME', 3600)  # seconds
        
        # Set secure headers
        @app.after_request
        def add_security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = self._build_csp_header()
            return response
        
        # Check for secure connection
        @app.before_request
        def force_secure():
            if not app.debug and not request.is_secure:
                url = request.url.replace('http://', 'https://', 1)
                return redirect(url, code=301)

    def _build_csp_header(self):
        """Build Content Security Policy header."""
        csp = {
            'default-src': ["'self'"],
            'script-src': ["'self'", "'unsafe-inline'", 'cdn.tailwindcss.com', 'code.jquery.com'],
            'style-src': ["'self'", "'unsafe-inline'", 'fonts.googleapis.com', 'cdn.tailwindcss.com'],
            'img-src': ["'self'", 'data:', 'www.gravatar.com'],
            'font-src': ["'self'", 'fonts.gstatic.com'],
            'connect-src': ["'self'"],
            'frame-src': ["'none'"],
            'object-src': ["'none'"]
        }
        
        return '; '.join(f"{key} {' '.join(values)}" for key, values in csp.items())

    def check_password_strength(self, password):
        """Check if password meets strength requirements."""
        if len(password) < self.app.config['PASSWORD_MIN_LENGTH']:
            return False
            
        if self.app.config['REQUIRE_PASSWORD_COMPLEXITY']:
            # Check for at least one lowercase letter
            if not re.search(r'[a-z]', password):
                return False
            # Check for at least one uppercase letter
            if not re.search(r'[A-Z]', password):
                return False
            # Check for at least one digit
            if not re.search(r'\d', password):
                return False
            # Check for at least one special character
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                return False
        
        return True

    def rate_limit(self, key='default', limit=60, per=60):
        """Decorator for rate limiting routes."""
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                # Get client IP
                ip = request.remote_addr
                
                # Create rate limit key
                rate_key = f'ratelimit:{key}:{ip}'
                
                # Check if IP is blocked
                if ip in self.blocked_ips:
                    abort(429)
                
                # Get current count
                count = session.get(rate_key, 0)
                
                # Check if limit exceeded
                if count >= limit:
                    # Block IP temporarily
                    self.blocked_ips.add(ip)
                    
                    # Log security event
                    log_security(
                        'rate_limit_exceeded',
                        f'IP {ip} exceeded rate limit for {key}'
                    )
                    
                    abort(429)
                
                # Increment count
                session[rate_key] = count + 1
                
                # Set expiry
                if count == 0:
                    session[f'{rate_key}_expires'] = datetime.utcnow() + timedelta(seconds=per)
                
                # Clear expired entries
                if datetime.utcnow() > session.get(f'{rate_key}_expires', datetime.min):
                    session.pop(rate_key, None)
                    session.pop(f'{rate_key}_expires', None)
                
                return f(*args, **kwargs)
            return wrapped
        return decorator

    def track_login_attempt(self, email, success=False):
        """Track login attempts for an email address."""
        now = datetime.utcnow()
        ip = request.remote_addr
        
        if email not in self.login_attempts:
            self.login_attempts[email] = []
        
        # Remove old attempts
        self.login_attempts[email] = [
            attempt for attempt in self.login_attempts[email]
            if now - attempt['time'] < timedelta(minutes=self.app.config['LOGIN_LOCKOUT_TIME'])
        ]
        
        # Add new attempt
        self.login_attempts[email].append({
            'time': now,
            'ip': ip,
            'success': success
        })
        
        # Check if account should be locked
        if not success and len(self.login_attempts[email]) >= self.app.config['MAX_LOGIN_ATTEMPTS']:
            user = User.query.filter_by(email=email).first()
            if user:
                user.locked = True
                user.locked_until = now + timedelta(minutes=self.app.config['LOGIN_LOCKOUT_TIME'])
                db.session.commit()
                
                log_security(
                    'account_locked',
                    f'Account {email} locked due to too many failed login attempts'
                )

    def check_account_lockout(self, email):
        """Check if an account is locked out."""
        user = User.query.filter_by(email=email).first()
        if not user:
            return False
            
        if user.locked and user.locked_until > datetime.utcnow():
            return True
            
        if user.locked:
            # Unlock account if lockout period has expired
            user.locked = False
            user.locked_until = None
            db.session.commit()
            
        return False

    def generate_csrf_token(self):
        """Generate a new CSRF token."""
        if 'csrf_token' not in session:
            session['csrf_token'] = hashlib.sha256(os.urandom(64)).hexdigest()
            session['csrf_token_time'] = datetime.utcnow()
        elif datetime.utcnow() - session['csrf_token_time'] > timedelta(seconds=self.app.config['CSRF_TOKEN_VALID_TIME']):
            # Regenerate token if expired
            session['csrf_token'] = hashlib.sha256(os.urandom(64)).hexdigest()
            session['csrf_token_time'] = datetime.utcnow()
        return session['csrf_token']

    def check_csrf_token(self, token):
        """Check if a CSRF token is valid."""
        return 'csrf_token' in session and safe_str_cmp(session['csrf_token'], token)

    def require_csrf(self, f):
        """Decorator to require CSRF token for routes."""
        @wraps(f)
        def wrapped(*args, **kwargs):
            if request.method == 'POST':
                token = request.form.get('csrf_token')
                if not token or not self.check_csrf_token(token):
                    log_security(
                        'csrf_validation_failed',
                        f'CSRF validation failed for {request.endpoint}'
                    )
                    abort(400)
            return f(*args, **kwargs)
        return wrapped

    def require_permission(self, permission):
        """Decorator to require specific permission for routes."""
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                if not current_user.has_permission(permission):
                    log_security(
                        'permission_denied',
                        f'User {current_user.id} denied access to {permission}'
                    )
                    abort(403)
                return f(*args, **kwargs)
            return wrapped
        return decorator

    def sanitize_filename(self, filename):
        """Sanitize a filename to prevent directory traversal."""
        return secure_filename(filename)

    def validate_redirect_url(self, url):
        """Validate a redirect URL to prevent open redirects."""
        if not url:
            return False
            
        # Check if URL is relative
        if url.startswith('/'):
            return True
            
        # Check if URL is for the same site
        parsed = urlparse(url)
        return parsed.netloc == request.host

# Initialize security
security = Security()
