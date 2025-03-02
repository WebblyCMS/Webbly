from flask import render_template
from . import db

def init_error_handlers(app):
    """Initialize error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return render_template('errors/405.html'), 405

    @app.errorhandler(429)
    def too_many_requests_error(error):
        return render_template('errors/429.html'), 429

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()  # Roll back any failed database sessions
        app.logger.error(f'Server Error: {error}')
        return render_template('errors/500.html', error=error), 500

    @app.errorhandler(503)
    def service_unavailable_error(error):
        return render_template('errors/503.html'), 503

    # Custom error handler for maintenance mode
    @app.errorhandler('maintenance_mode')
    def maintenance_mode_error(error):
        return render_template('maintenance.html'), 503

    # Register error handlers with the application context
    app.register_error_handler(400, bad_request_error)
    app.register_error_handler(401, unauthorized_error)
    app.register_error_handler(403, forbidden_error)
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(405, method_not_allowed_error)
    app.register_error_handler(429, too_many_requests_error)
    app.register_error_handler(500, internal_error)
    app.register_error_handler(503, service_unavailable_error)

    # Log all errors in production
    if not app.debug:
        @app.errorhandler(Exception)
        def unhandled_exception(error):
            app.logger.error(f'Unhandled Exception: {error}', exc_info=True)
            return render_template('errors/500.html', error=error), 500

    # Add context processor for error pages
    @app.context_processor
    def error_context():
        """Add common variables to error page templates."""
        def get_error_code(error):
            """Get the HTTP status code from an error object."""
            if hasattr(error, 'code'):
                return error.code
            return 500

        def get_error_name(error):
            """Get a human-readable name for an error code."""
            error_names = {
                400: 'Bad Request',
                401: 'Unauthorized',
                403: 'Forbidden',
                404: 'Not Found',
                405: 'Method Not Allowed',
                429: 'Too Many Requests',
                500: 'Internal Server Error',
                503: 'Service Unavailable'
            }
            code = get_error_code(error)
            return error_names.get(code, 'Unknown Error')

        def get_error_description(error):
            """Get a human-readable description for an error code."""
            error_descriptions = {
                400: 'The server could not understand your request.',
                401: 'You need to be authenticated to access this resource.',
                403: 'You do not have permission to access this resource.',
                404: 'The requested resource could not be found.',
                405: 'The method used is not allowed for this resource.',
                429: 'You have made too many requests. Please try again later.',
                500: 'An unexpected error occurred on our servers.',
                503: 'The service is temporarily unavailable.'
            }
            code = get_error_code(error)
            return error_descriptions.get(code, 'An unknown error occurred.')

        return {
            'get_error_code': get_error_code,
            'get_error_name': get_error_name,
            'get_error_description': get_error_description
        }

def handle_error(error):
    """Generic error handler that can be used for custom error pages."""
    if hasattr(error, 'code'):
        return render_template(f'errors/{error.code}.html', error=error), error.code
    return render_template('errors/500.html', error=error), 500
