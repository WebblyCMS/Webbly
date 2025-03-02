import os
import json
import importlib
import inspect
from flask import Blueprint
from .models import Plugin, db
from .utils.decorators import admin_required

class PluginManager:
    """Manage Webbly CMS plugins."""
    
    def __init__(self, app=None):
        self.app = app
        self.plugins = {}
        self.hooks = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize plugin system with Flask application."""
        self.app = app
        
        # Create plugins directory if it doesn't exist
        plugins_dir = os.path.join(app.root_path, 'plugins')
        if not os.path.exists(plugins_dir):
            os.makedirs(plugins_dir)
        
        # Load all installed plugins
        self.load_plugins()
        
        # Register plugin admin views
        self.register_admin_views()

    def load_plugins(self):
        """Load all installed and active plugins."""
        plugins = Plugin.query.filter_by(active=True).all()
        for plugin in plugins:
            try:
                self.load_plugin(plugin)
            except Exception as e:
                self.app.logger.error(f"Error loading plugin {plugin.name}: {str(e)}")

    def load_plugin(self, plugin):
        """Load a single plugin."""
        plugin_dir = os.path.join(self.app.root_path, 'plugins', plugin.directory)
        
        # Load plugin metadata
        with open(os.path.join(plugin_dir, 'plugin.json')) as f:
            metadata = json.load(f)
        
        # Import plugin module
        spec = importlib.util.spec_from_file_location(
            f"webbly.plugins.{plugin.directory}",
            os.path.join(plugin_dir, '__init__.py')
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Store plugin instance
        self.plugins[plugin.directory] = {
            'module': module,
            'metadata': metadata,
            'instance': plugin
        }
        
        # Register plugin blueprint if it exists
        if hasattr(module, 'bp'):
            self.app.register_blueprint(module.bp)
        
        # Register plugin hooks
        self.register_hooks(module)
        
        # Initialize plugin
        if hasattr(module, 'init_app'):
            module.init_app(self.app)

    def register_hooks(self, module):
        """Register all hooks defined in a plugin module."""
        for name, func in inspect.getmembers(module):
            if hasattr(func, '_webbly_hook'):
                hook_name = getattr(func, '_webbly_hook')
                if hook_name not in self.hooks:
                    self.hooks[hook_name] = []
                self.hooks[hook_name].append(func)

    def register_admin_views(self):
        """Register admin views for all plugins."""
        for plugin_info in self.plugins.values():
            module = plugin_info['module']
            if hasattr(module, 'admin_views'):
                for view in module.admin_views:
                    self.register_admin_view(view)

    def register_admin_view(self, view):
        """Register a plugin's admin view."""
        # Create blueprint for plugin admin views
        bp_name = f"plugin_{view.plugin_name}_admin"
        bp = Blueprint(
            bp_name,
            __name__,
            url_prefix=f'/webb-admin/plugins/{view.plugin_name}',
            template_folder='templates'
        )
        
        # Add view routes to blueprint
        view.register(bp)
        
        # Register blueprint with app
        self.app.register_blueprint(bp)

    def execute_hook(self, hook_name, *args, **kwargs):
        """Execute all registered functions for a hook."""
        results = []
        if hook_name in self.hooks:
            for func in self.hooks[hook_name]:
                try:
                    result = func(*args, **kwargs)
                    if result is not None:
                        results.append(result)
                except Exception as e:
                    self.app.logger.error(
                        f"Error executing hook {hook_name} in function {func.__name__}: {str(e)}"
                    )
        return results

    def install_plugin(self, directory):
        """Install a plugin from a directory."""
        plugin_dir = os.path.join(self.app.root_path, 'plugins', directory)
        if not os.path.exists(plugin_dir):
            raise ValueError(f"Plugin directory {directory} does not exist")
        
        # Read plugin metadata
        try:
            with open(os.path.join(plugin_dir, 'plugin.json')) as f:
                metadata = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            raise ValueError("Invalid plugin.json file")
        
        # Check if plugin already exists
        existing = Plugin.query.filter_by(directory=directory).first()
        if existing:
            # Update existing plugin
            existing.name = metadata.get('name', directory)
            existing.version = metadata.get('version', '1.0.0')
            existing.author = metadata.get('author', 'Unknown')
            existing.description = metadata.get('description', '')
        else:
            # Create new plugin
            plugin = Plugin(
                name=metadata.get('name', directory),
                directory=directory,
                version=metadata.get('version', '1.0.0'),
                author=metadata.get('author', 'Unknown'),
                description=metadata.get('description', ''),
                active=False
            )
            db.session.add(plugin)
        
        db.session.commit()
        return True

    def uninstall_plugin(self, directory):
        """Uninstall a plugin."""
        plugin = Plugin.query.filter_by(directory=directory).first()
        if not plugin:
            raise ValueError(f"Plugin {directory} not found")
        
        # Deactivate plugin first
        if plugin.active:
            self.deactivate_plugin(directory)
        
        # Remove plugin files
        plugin_dir = os.path.join(self.app.root_path, 'plugins', directory)
        if os.path.exists(plugin_dir):
            import shutil
            shutil.rmtree(plugin_dir)
        
        # Remove from database
        db.session.delete(plugin)
        db.session.commit()

    def activate_plugin(self, directory):
        """Activate a plugin."""
        plugin = Plugin.query.filter_by(directory=directory).first()
        if not plugin:
            raise ValueError(f"Plugin {directory} not found")
        
        plugin.active = True
        db.session.commit()
        
        # Load the plugin
        self.load_plugin(plugin)

    def deactivate_plugin(self, directory):
        """Deactivate a plugin."""
        plugin = Plugin.query.filter_by(directory=directory).first()
        if not plugin:
            raise ValueError(f"Plugin {directory} not found")
        
        plugin.active = False
        db.session.commit()
        
        # Remove plugin from loaded plugins
        if directory in self.plugins:
            # Call cleanup if available
            module = self.plugins[directory]['module']
            if hasattr(module, 'cleanup'):
                module.cleanup()
            
            # Remove plugin hooks
            for hook_list in self.hooks.values():
                hook_list[:] = [f for f in hook_list 
                              if not inspect.getmodule(f).__name__.startswith(
                                  f"webbly.plugins.{directory}"
                              )]
            
            # Remove plugin from loaded plugins
            del self.plugins[directory]

def hook(name):
    """Decorator to register a function as a hook."""
    def decorator(f):
        f._webbly_hook = name
        return f
    return decorator

# Initialize plugin manager
plugin_manager = PluginManager()
