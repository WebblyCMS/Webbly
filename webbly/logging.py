import os
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
from flask import has_request_context, request
from datetime import datetime

class RequestFormatter(logging.Formatter):
    """Custom formatter that includes request information."""
    
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
            record.path = request.path
            if hasattr(request, 'user'):
                record.user = request.user.username
            else:
                record.user = 'Anonymous'
        else:
            record.url = None
            record.remote_addr = None
            record.method = None
            record.path = None
            record.user = None
            
        return super().format(record)

def init_logging(app):
    """Initialize logging configuration."""
    
    # Ensure logs directory exists
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Set up file logging
    file_handler = RotatingFileHandler(
        'logs/webbly.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(RequestFormatter(
        '[%(asctime)s] %(remote_addr)s - %(user)s %(method)s %(url)s\n'
        '%(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]\n'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    # Set up error logging via email in production
    if not app.debug and not app.testing:
        if app.config.get('MAIL_SERVER'):
            auth = None
            if app.config.get('MAIL_USERNAME') or app.config.get('MAIL_PASSWORD'):
                auth = (app.config.get('MAIL_USERNAME'),
                       app.config.get('MAIL_PASSWORD'))
            secure = None
            if app.config.get('MAIL_USE_TLS'):
                secure = ()
                
            mail_handler = SMTPHandler(
                mailhost=(app.config.get('MAIL_SERVER'),
                         app.config.get('MAIL_PORT', 25)),
                fromaddr=f"no-reply@{app.config.get('MAIL_SERVER')}",
                toaddrs=[app.config.get('ADMIN_EMAIL')],
                subject='Webbly Error',
                credentials=auth,
                secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            mail_handler.setFormatter(logging.Formatter('''
Time:               %(asctime)s
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:            %(module)s
Function:          %(funcName)s
Request URL:       %(url)s
Request Method:    %(method)s
Remote Address:    %(remote_addr)s
User:              %(user)s

Message:

%(message)s
'''))
            app.logger.addHandler(mail_handler)
    
    # Set general logging level
    app.logger.setLevel(logging.INFO)
    app.logger.info('Webbly startup')

def log_error(app, error, user=None):
    """Log an error with additional context."""
    error_id = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    context = {
        'error_id': error_id,
        'user': user.username if user else 'Anonymous',
        'timestamp': datetime.utcnow().isoformat(),
        'error_type': type(error).__name__,
        'error_message': str(error)
    }
    
    if has_request_context():
        context.update({
            'url': request.url,
            'method': request.method,
            'remote_addr': request.remote_addr,
            'user_agent': request.user_agent.string,
            'headers': dict(request.headers),
            'args': dict(request.args),
            'form': dict(request.form)
        })
    
    app.logger.error(
        f"Error {error_id}: {context['error_type']} - {context['error_message']}",
        extra={
            'error_context': context
        }
    )
    
    return error_id

def setup_audit_log(app):
    """Set up audit logging for administrative actions."""
    audit_logger = logging.getLogger('webbly.audit')
    
    # Create audit log handler
    audit_handler = RotatingFileHandler(
        'logs/audit.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    audit_handler.setFormatter(RequestFormatter(
        '[%(asctime)s] %(remote_addr)s - %(user)s\n'
        'Action: %(action)s\n'
        'Details: %(details)s\n'
    ))
    audit_logger.addHandler(audit_handler)
    audit_logger.setLevel(logging.INFO)
    
    return audit_logger

def log_audit(action, details, user=None):
    """Log an audit event."""
    audit_logger = logging.getLogger('webbly.audit')
    audit_logger.info(
        'Audit event',
        extra={
            'action': action,
            'details': details,
            'user': user.username if user else 'System',
            'remote_addr': request.remote_addr if has_request_context() else None
        }
    )

def setup_security_log(app):
    """Set up security logging for authentication and authorization events."""
    security_logger = logging.getLogger('webbly.security')
    
    # Create security log handler
    security_handler = RotatingFileHandler(
        'logs/security.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    security_handler.setFormatter(RequestFormatter(
        '[%(asctime)s] %(remote_addr)s - %(user)s\n'
        'Event: %(event)s\n'
        'Details: %(details)s\n'
    ))
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.INFO)
    
    return security_logger

def log_security(event, details, user=None):
    """Log a security event."""
    security_logger = logging.getLogger('webbly.security')
    security_logger.info(
        'Security event',
        extra={
            'event': event,
            'details': details,
            'user': user.username if user else 'Anonymous',
            'remote_addr': request.remote_addr if has_request_context() else None
        }
    )
