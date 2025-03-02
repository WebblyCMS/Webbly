import os
import pytest
from click.testing import CliRunner
from webbly.cli import cli
from webbly.models import User, Theme, Plugin, Setting, db

def test_init_command(app, runner):
    """Test database initialization command."""
    with app.app_context():
        # Clear database
        db.drop_all()
        
        # Run init command
        result = runner.invoke(cli, ['init'])
        assert result.exit_code == 0
        assert 'Initialization complete!' in result.output
        
        # Check database was created
        assert User.query.count() == 0
        assert Setting.query.filter_by(key='site_title').first() is not None

def test_create_admin_command(app, runner):
    """Test admin user creation command."""
    with app.app_context():
        # Run command with arguments
        result = runner.invoke(cli, ['create-admin',
            '--username', 'admin',
            '--email', 'admin@example.com',
            '--password', 'Password123!'
        ])
        assert result.exit_code == 0
        assert 'Admin user' in result.output
        
        # Check admin was created
        admin = User.query.filter_by(email='admin@example.com').first()
        assert admin is not None
        assert admin.is_admin
        
        # Test duplicate email
        result = runner.invoke(cli, ['create-admin',
            '--username', 'another',
            '--email', 'admin@example.com',
            '--password', 'Password123!'
        ])
        assert result.exit_code != 0
        assert 'Email already exists' in result.output

def test_install_theme_command(app, runner, tmp_path):
    """Test theme installation command."""
    # Create test theme directory
    theme_dir = tmp_path / "test_theme"
    theme_dir.mkdir()
    (theme_dir / "theme.json").write_text("""
    {
        "name": "Test Theme",
        "version": "1.0.0",
        "author": "Test Author"
    }
    """)
    
    with app.app_context():
        # Run command
        result = runner.invoke(cli, ['install-theme', str(theme_dir)])
        assert result.exit_code == 0
        assert 'Theme installed successfully' in result.output
        
        # Check theme was installed
        theme = Theme.query.filter_by(name='Test Theme').first()
        assert theme is not None
        
        # Test invalid theme directory
        result = runner.invoke(cli, ['install-theme', 'nonexistent'])
        assert result.exit_code != 0
        assert 'Error' in result.output

def test_list_themes_command(app, runner, test_theme):
    """Test theme listing command."""
    with app.app_context():
        db.session.add(test_theme)
        db.session.commit()
        
        result = runner.invoke(cli, ['list-themes'])
        assert result.exit_code == 0
        assert test_theme.name in result.output
        assert test_theme.version in result.output

def test_activate_theme_command(app, runner, test_theme):
    """Test theme activation command."""
    with app.app_context():
        db.session.add(test_theme)
        db.session.commit()
        
        result = runner.invoke(cli, ['activate-theme', test_theme.name])
        assert result.exit_code == 0
        assert 'activated successfully' in result.output
        
        # Check theme was activated
        theme = Theme.query.filter_by(name=test_theme.name).first()
        assert theme.active

def test_install_plugin_command(app, runner, tmp_path):
    """Test plugin installation command."""
    # Create test plugin directory
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()
    (plugin_dir / "plugin.json").write_text("""
    {
        "name": "Test Plugin",
        "version": "1.0.0",
        "author": "Test Author"
    }
    """)
    
    with app.app_context():
        # Run command
        result = runner.invoke(cli, ['install-plugin', str(plugin_dir)])
        assert result.exit_code == 0
        assert 'Plugin installed successfully' in result.output
        
        # Check plugin was installed
        plugin = Plugin.query.filter_by(name='Test Plugin').first()
        assert plugin is not None

def test_list_plugins_command(app, runner, test_plugin):
    """Test plugin listing command."""
    with app.app_context():
        db.session.add(test_plugin)
        db.session.commit()
        
        result = runner.invoke(cli, ['list-plugins'])
        assert result.exit_code == 0
        assert test_plugin.name in result.output
        assert test_plugin.version in result.output

def test_set_setting_command(app, runner):
    """Test setting management commands."""
    with app.app_context():
        # Test setting a value
        result = runner.invoke(cli, ['set-setting', 'test_key', 'test_value'])
        assert result.exit_code == 0
        assert 'updated successfully' in result.output
        
        # Test getting the value
        result = runner.invoke(cli, ['get-setting', 'test_key'])
        assert result.exit_code == 0
        assert 'test_value' in result.output
        
        # Test listing settings
        result = runner.invoke(cli, ['list-settings'])
        assert result.exit_code == 0
        assert 'test_key' in result.output

def test_clear_cache_command(app, runner):
    """Test cache clearing command."""
    # Create some cache files
    cache_dir = os.path.join(app.root_path, 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    open(os.path.join(cache_dir, 'test.cache'), 'w').close()
    
    result = runner.invoke(cli, ['clear-cache'])
    assert result.exit_code == 0
    assert 'Cache cleared successfully' in result.output
    assert not os.path.exists(os.path.join(cache_dir, 'test.cache'))

def test_backup_command(app, runner):
    """Test backup command."""
    with app.app_context():
        result = runner.invoke(cli, ['backup'])
        assert result.exit_code == 0
        assert 'Backup created successfully' in result.output
        
        # Check backup file was created
        backup_dir = os.path.join(app.root_path, 'backups')
        assert len(os.listdir(backup_dir)) > 0

def test_error_handling(runner):
    """Test CLI error handling."""
    # Test invalid command
    result = runner.invoke(cli, ['nonexistent'])
    assert result.exit_code != 0
    
    # Test missing required argument
    result = runner.invoke(cli, ['set-setting'])
    assert result.exit_code != 0
    assert 'Missing argument' in result.output
