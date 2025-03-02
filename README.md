# Webbly CMS

Webbly is a modern, Flask-based Content Management System (CMS) that provides a flexible and user-friendly platform for creating and managing websites. It offers features similar to WordPress but with a modern Python-based architecture.

## Features

- User-friendly admin dashboard
- Post and page management
- Theme system with customization options
- Plugin architecture
- User management with roles
- Comment system
- Media management
- SEO-friendly URLs
- Mobile-responsive design
- Email notifications
- Custom templates
- Security features

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/webbly.git
cd webbly
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file:
```bash
cp .env.example .env
```
Edit the .env file with your configuration settings.

5. Initialize the database:
```bash
flask init-db
```

6. Create an admin user:
```bash
flask create-admin
```

7. Initialize default settings:
```bash
flask init-settings
```

8. Scan for themes:
```bash
flask scan-themes
```

9. Run the development server:
```bash
flask run
```

Visit http://localhost:5000 to access your Webbly site.
Admin dashboard is available at http://localhost:5000/webb-admin

## Project Structure

```
webbly/
├── webbly/                  # Main application package
│   ├── __init__.py         # Application factory
│   ├── models.py           # Database models
│   ├── auth/               # Authentication blueprint
│   ├── admin/              # Admin dashboard blueprint
│   ├── core/               # Core site functionality
│   ├── utils/              # Utility functions
│   └── templates/          # HTML templates
├── static/                 # Static files
├── themes/                 # Theme files
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
└── run.py                # Application entry point
```

## Creating Themes

Themes are stored in the `themes` directory. Each theme should have the following structure:

```
theme_name/
├── theme.json             # Theme metadata
├── templates/            # Theme templates
│   ├── index.html       # Homepage template
│   ├── post.html        # Single post template
│   ├── page.html        # Page template
│   └── ...
├── static/              # Theme assets
│   ├── css/
│   ├── js/
│   └── images/
└── screenshot.png       # Theme preview image
```

## Creating Plugins

Plugins are Python packages that extend Webbly's functionality. A basic plugin structure:

```
plugin_name/
├── __init__.py          # Plugin initialization
├── routes.py           # Plugin routes
├── models.py           # Plugin models
└── templates/          # Plugin templates
```

## Development

To set up the development environment:

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
python -m pytest
```

3. Check code style:
```bash
flake8 webbly
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on GitHub or contact the maintainers.
