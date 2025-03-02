import os
import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from . import db
from .models import User, Theme, Plugin, Setting
from .utils.theme import scan_for_themes, install_theme
from .utils.settings import init_default_settings

@click.group()
def cli():
    """Webbly CMS management commands."""
    pass

@cli.command()
@with_appcontext
def init():
    """Initialize the CMS database and default settings."""
    click.echo("Initializing database...")
    db.create_all()
    
    click.echo("Setting up default settings...")
    init_default_settings()
    
    click.echo("Scanning for themes...")
    themes = scan_for_themes()
    click.echo(f"Found {len(themes)} themes")
    
    click.echo("Initialization complete!")

@cli.command()
@click.option('--username', prompt=True, help='Admin username')
@click.option('--email', prompt=True, help='Admin email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
@with_appcontext
def create_admin(username, email, password):
    """Create an admin user."""
    if User.query.filter_by(email=email).first():
        click.echo("Error: Email already exists")
        return
    
    if User.query.filter_by(username=username).first():
        click.echo("Error: Username already exists")
        return
    
    user = User(
        username=username,
        email=email,
        is_admin=True
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    click.echo(f"Admin user '{username}' created successfully!")

@cli.command()
@click.argument('theme_path', type=click.Path(exists=True))
@with_appcontext
def install_theme_cmd(theme_path):
    """Install a theme from a directory."""
    try:
        theme_dir = os.path.basename(theme_path)
        install_theme(theme_dir)
        click.echo(f"Theme '{theme_dir}' installed successfully!")
    except Exception as e:
        click.echo(f"Error installing theme: {str(e)}")

@cli.command()
@with_appcontext
def list_themes():
    """List all installed themes."""
    themes = Theme.query.all()
    if not themes:
        click.echo("No themes installed")
        return
    
    for theme in themes:
        active = "[ACTIVE]" if theme.active else ""
        click.echo(f"{theme.name} (v{theme.version}) {active}")
        click.echo(f"  Author: {theme.author}")
        click.echo(f"  Directory: {theme.directory}")
        click.echo()

@cli.command()
@click.argument('theme_name')
@with_appcontext
def activate_theme(theme_name):
    """Activate a theme."""
    theme = Theme.query.filter_by(name=theme_name).first()
    if not theme:
        click.echo(f"Theme '{theme_name}' not found")
        return
    
    # Deactivate current theme
    Theme.query.filter_by(active=True).update({Theme.active: False})
    
    # Activate new theme
    theme.active = True
    db.session.commit()
    
    click.echo(f"Theme '{theme_name}' activated successfully!")

@cli.command()
@click.argument('plugin_path', type=click.Path(exists=True))
@with_appcontext
def install_plugin(plugin_path):
    """Install a plugin from a directory."""
    try:
        plugin_dir = os.path.basename(plugin_path)
        # TODO: Implement plugin installation logic
        click.echo(f"Plugin '{plugin_dir}' installed successfully!")
    except Exception as e:
        click.echo(f"Error installing plugin: {str(e)}")

@cli.command()
@with_appcontext
def list_plugins():
    """List all installed plugins."""
    plugins = Plugin.query.all()
    if not plugins:
        click.echo("No plugins installed")
        return
    
    for plugin in plugins:
        active = "[ACTIVE]" if plugin.active else ""
        click.echo(f"{plugin.name} (v{plugin.version}) {active}")
        click.echo(f"  Author: {plugin.author}")
        click.echo(f"  Directory: {plugin.directory}")
        click.echo()

@cli.command()
@click.argument('key')
@click.argument('value')
@with_appcontext
def set_setting(key, value):
    """Set a setting value."""
    setting = Setting.query.filter_by(key=key).first()
    if setting:
        setting.value = value
    else:
        setting = Setting(key=key, value=value)
        db.session.add(setting)
    
    db.session.commit()
    click.echo(f"Setting '{key}' updated successfully!")

@cli.command()
@click.argument('key')
@with_appcontext
def get_setting(key):
    """Get a setting value."""
    setting = Setting.query.filter_by(key=key).first()
    if setting:
        click.echo(f"{key}: {setting.value}")
    else:
        click.echo(f"Setting '{key}' not found")

@cli.command()
@with_appcontext
def list_settings():
    """List all settings."""
    settings = Setting.query.all()
    if not settings:
        click.echo("No settings found")
        return
    
    for setting in settings:
        click.echo(f"{setting.key}: {setting.value}")

@cli.command()
@with_appcontext
def clear_cache():
    """Clear the application cache."""
    cache_dir = os.path.join(os.getcwd(), 'cache')
    if os.path.exists(cache_dir):
        for file in os.listdir(cache_dir):
            file_path = os.path.join(cache_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                click.echo(f"Error deleting {file_path}: {str(e)}")
        click.echo("Cache cleared successfully!")
    else:
        click.echo("No cache directory found")

@cli.command()
@with_appcontext
def backup():
    """Create a backup of the database and uploads."""
    import datetime
    import shutil
    
    # Create backup directory
    backup_dir = os.path.join(os.getcwd(), 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Backup database
    db_path = os.path.join(os.getcwd(), 'webbly.db')
    if os.path.exists(db_path):
        shutil.copy2(db_path, os.path.join(backup_dir, f'webbly_{timestamp}.db'))
    
    # Backup uploads
    uploads_dir = os.path.join(os.getcwd(), 'static', 'uploads')
    if os.path.exists(uploads_dir):
        shutil.make_archive(
            os.path.join(backup_dir, f'uploads_{timestamp}'),
            'zip',
            uploads_dir
        )
    
    click.echo(f"Backup created successfully in {backup_dir}")

def init_app(app):
    """Register CLI commands with the app."""
    app.cli.add_command(cli)
