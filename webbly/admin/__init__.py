from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/webb-admin')

from . import routes
