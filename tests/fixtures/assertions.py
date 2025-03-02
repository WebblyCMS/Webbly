"""Custom test assertions and validation helpers."""

from bs4 import BeautifulSoup
from flask import url_for
from webbly.models import User, Post, Page, Theme, Plugin, Setting

def assert_valid_html(html):
    """Assert that HTML is valid and well-formed."""
    soup = BeautifulSoup(html, 'html.parser')
    assert soup.find()  # Should have at least one tag

def assert_contains_elements(html, selectors):
    """Assert that HTML contains elements matching CSS selectors."""
    soup = BeautifulSoup(html, 'html.parser')
    for selector in selectors:
        assert soup.select(selector), f"Element not found: {selector}"

def assert_page_title(response, expected_title):
    """Assert that page has expected title."""
    soup = BeautifulSoup(response.data, 'html.parser')
    title = soup.title.string if soup.title else ''
    assert expected_title in title

def assert_flash_message(response, message, category='message'):
    """Assert that flash message exists."""
    soup = BeautifulSoup(response.data, 'html.parser')
    flashes = soup.find_all(class_=category)
    assert any(message in flash.text for flash in flashes)

def assert_form_errors(response, errors):
    """Assert that form has expected errors."""
    soup = BeautifulSoup(response.data, 'html.parser')
    for field, error in errors.items():
        error_element = soup.find(class_='invalid-feedback', string=error)
        assert error_element, f"Error not found for field {field}: {error}"

def assert_valid_pagination(response, current_page, total_pages):
    """Assert that pagination is correct."""
    soup = BeautifulSoup(response.data, 'html.parser')
    pagination = soup.find(class_='pagination')
    assert pagination
    
    # Check current page
    active_page = pagination.find(class_='active')
    assert active_page and str(current_page) in active_page.text
    
    # Check total pages
    page_items = pagination.find_all(class_='page-item')
    assert len(page_items) <= total_pages + 2  # +2 for prev/next buttons

def assert_valid_post(post, expected):
    """Assert that post has expected attributes."""
    assert post.title == expected['title']
    assert post.content == expected['content']
    if 'excerpt' in expected:
        assert post.excerpt == expected['excerpt']
    if 'published' in expected:
        assert post.published == expected['published']
    if 'author' in expected:
        assert post.author.username == expected['author']

def assert_valid_page(page, expected):
    """Assert that page has expected attributes."""
    assert page.title == expected['title']
    assert page.content == expected['content']
    if 'template' in expected:
        assert page.template == expected['template']
    if 'published' in expected:
        assert page.published == expected['published']

def assert_valid_user(user, expected):
    """Assert that user has expected attributes."""
    assert user.username == expected['username']
    assert user.email == expected['email']
    if 'is_admin' in expected:
        assert user.is_admin == expected['is_admin']

def assert_valid_theme(theme, expected):
    """Assert that theme has expected attributes."""
    assert theme.name == expected['name']
    assert theme.directory == expected['directory']
    if 'active' in expected:
        assert theme.active == expected['active']
    if 'options' in expected:
        for key, value in expected['options'].items():
            assert theme.get_option(key) == value

def assert_valid_plugin(plugin, expected):
    """Assert that plugin has expected attributes."""
    assert plugin.name == expected['name']
    assert plugin.directory == expected['directory']
    if 'active' in expected:
        assert plugin.active == expected['active']
    if 'settings' in expected:
        for key, value in expected['settings'].items():
            assert plugin.get_setting(key) == value

def assert_valid_settings(settings, expected):
    """Assert that settings have expected values."""
    for key, value in expected.items():
        assert settings.get(key) == value

def assert_valid_response(response, expected_status_code=200):
    """Assert that response is valid."""
    assert response.status_code == expected_status_code
    assert response.content_type == 'text/html; charset=utf-8'
    assert_valid_html(response.data)

def assert_valid_json_response(response, expected_status_code=200):
    """Assert that JSON response is valid."""
    assert response.status_code == expected_status_code
    assert response.content_type == 'application/json'
    assert response.is_json

def assert_valid_redirect(response, endpoint, **kwargs):
    """Assert that response is a valid redirect."""
    assert response.status_code in (301, 302)
    assert response.location == url_for(endpoint, **kwargs)

def assert_requires_login(client, endpoint, **kwargs):
    """Assert that endpoint requires login."""
    response = client.get(url_for(endpoint, **kwargs))
    assert_valid_redirect(response, 'auth.login')

def assert_requires_admin(client, endpoint, **kwargs):
    """Assert that endpoint requires admin privileges."""
    response = client.get(url_for(endpoint, **kwargs))
    assert response.status_code == 403

def assert_valid_csrf(response):
    """Assert that response contains CSRF token."""
    soup = BeautifulSoup(response.data, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})
    assert csrf_token and csrf_token.get('value')

def assert_valid_form(response, form_id):
    """Assert that form exists and is valid."""
    soup = BeautifulSoup(response.data, 'html.parser')
    form = soup.find('form', id=form_id)
    assert form
    assert form.get('method')
    assert form.get('action')
    assert form.find('input', {'name': 'csrf_token'})

def assert_menu_items(response, items):
    """Assert that menu contains expected items."""
    soup = BeautifulSoup(response.data, 'html.parser')
    menu = soup.find('nav')
    assert menu
    
    for item in items:
        link = menu.find('a', string=item['text'])
        assert link
        assert link['href'] == item['url']

def assert_sidebar_widgets(response, widgets):
    """Assert that sidebar contains expected widgets."""
    soup = BeautifulSoup(response.data, 'html.parser')
    sidebar = soup.find(class_='sidebar')
    assert sidebar
    
    for widget in widgets:
        widget_elem = sidebar.find(class_=f"widget-{widget['type']}")
        assert widget_elem
        assert widget_elem.find(class_='widget-title').text == widget['title']

def assert_valid_meta_tags(response, expected):
    """Assert that page has expected meta tags."""
    soup = BeautifulSoup(response.data, 'html.parser')
    for name, content in expected.items():
        meta = soup.find('meta', {'name': name})
        assert meta and meta.get('content') == content
