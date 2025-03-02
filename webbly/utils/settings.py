from ..models import Setting, db
import json

def get_setting(key, default=None):
    """Get a setting value by key."""
    setting = Setting.query.filter_by(key=key).first()
    if setting is None:
        return default
    
    # Handle different setting types
    if setting.type == 'bool':
        return setting.value.lower() == 'true'
    elif setting.type == 'int':
        try:
            return int(setting.value)
        except (ValueError, TypeError):
            return default
    elif setting.type == 'json':
        try:
            return json.loads(setting.value)
        except json.JSONDecodeError:
            return default
    
    return setting.value

def set_setting(key, value, type='string'):
    """Set a setting value."""
    # Convert value based on type
    if type == 'bool':
        value = str(bool(value)).lower()
    elif type == 'int':
        value = str(int(value))
    elif type == 'json':
        value = json.dumps(value)
    else:
        value = str(value)
    
    setting = Setting.query.filter_by(key=key).first()
    if setting:
        setting.value = value
        setting.type = type
    else:
        setting = Setting(key=key, value=value, type=type)
        db.session.add(setting)
    
    db.session.commit()
    return True

def get_all_settings():
    """Get all settings as a dictionary."""
    settings = {}
    for setting in Setting.query.all():
        settings[setting.key] = get_setting(setting.key)
    return settings

def init_default_settings():
    """Initialize default settings if they don't exist."""
    defaults = {
        'site_title': ('Webbly Site', 'string'),
        'site_description': ('A Webbly powered website', 'string'),
        'posts_per_page': ('10', 'int'),
        'enable_comments': ('true', 'bool'),
        'comment_moderation': ('true', 'bool'),
        'theme_options': ('{}', 'json'),
        'menu_items': ('[]', 'json'),
        'footer_text': ('Powered by Webbly', 'string'),
        'social_links': ('{}', 'json'),
        'analytics_id': ('', 'string'),
        'custom_css': ('', 'string'),
        'custom_js': ('', 'string')
    }
    
    for key, (value, type) in defaults.items():
        if get_setting(key) is None:
            set_setting(key, value, type)

def delete_setting(key):
    """Delete a setting by key."""
    setting = Setting.query.filter_by(key=key).first()
    if setting:
        db.session.delete(setting)
        db.session.commit()
        return True
    return False

def clear_settings():
    """Delete all settings."""
    Setting.query.delete()
    db.session.commit()
