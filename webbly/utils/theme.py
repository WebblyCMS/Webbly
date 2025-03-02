import os
import json
from flask import current_app
from ..models import Theme, db

def get_active_theme():
    """Get the currently active theme."""
    return Theme.query.filter_by(active=True).first()

def get_theme_template(theme_directory, template_name):
    """Get the template path for a theme."""
    return f'themes/{theme_directory}/{template_name}'

def get_available_templates():
    """Get list of available templates from active theme."""
    theme = get_active_theme()
    if not theme:
        return [('default', 'Default Template')]
    
    template_dir = os.path.join(current_app.root_path, 'themes', theme.directory)
    templates = []
    
    try:
        for file in os.listdir(template_dir):
            if file.endswith('.html'):
                name = file[:-5]  # Remove .html extension
                if name.startswith('page-'):
                    template_name = name[5:]  # Remove page- prefix
                    templates.append((name, template_name.replace('-', ' ').title()))
    except OSError:
        return [('default', 'Default Template')]
    
    templates.insert(0, ('default', 'Default Template'))
    return templates

def install_theme(directory):
    """Install a theme from a directory."""
    theme_dir = os.path.join(current_app.root_path, 'themes', directory)
    
    if not os.path.exists(theme_dir):
        raise ValueError(f"Theme directory {directory} does not exist")
    
    # Read theme.json
    try:
        with open(os.path.join(theme_dir, 'theme.json')) as f:
            theme_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        raise ValueError("Invalid theme.json file")
    
    # Check if theme already exists
    existing_theme = Theme.query.filter_by(directory=directory).first()
    if existing_theme:
        # Update existing theme
        existing_theme.name = theme_data.get('name', directory)
        existing_theme.version = theme_data.get('version', '1.0.0')
        existing_theme.author = theme_data.get('author', 'Unknown')
        existing_theme.description = theme_data.get('description', '')
        existing_theme.screenshot = theme_data.get('screenshot', '')
    else:
        # Create new theme
        theme = Theme(
            name=theme_data.get('name', directory),
            directory=directory,
            version=theme_data.get('version', '1.0.0'),
            author=theme_data.get('author', 'Unknown'),
            description=theme_data.get('description', ''),
            screenshot=theme_data.get('screenshot', ''),
            active=False
        )
        db.session.add(theme)
    
    db.session.commit()
    return True

def scan_for_themes():
    """Scan themes directory for new themes."""
    themes_dir = os.path.join(current_app.root_path, 'themes')
    
    if not os.path.exists(themes_dir):
        os.makedirs(themes_dir)
        return []
    
    installed_themes = []
    for directory in os.listdir(themes_dir):
        theme_dir = os.path.join(themes_dir, directory)
        if os.path.isdir(theme_dir) and os.path.exists(os.path.join(theme_dir, 'theme.json')):
            try:
                install_theme(directory)
                installed_themes.append(directory)
            except ValueError:
                continue
    
    return installed_themes
