import pytest
from flask import g, session
from webbly.models import User, db

def test_register(client, app):
    """Test user registration."""
    # Test GET request
    assert client.get('/auth/register').status_code == 200
    
    # Test successful registration
    response = client.post(
        '/auth/register',
        data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Password123!',
            'password2': 'Password123!'
        }
    )
    assert response.headers["Location"] == "/auth/login"
    
    # Test user was created
    with app.app_context():
        user = User.query.filter_by(email='new@example.com').first()
        assert user is not None
        assert user.username == 'newuser'
        assert not user.is_admin

def test_register_validation(client):
    """Test registration validation."""
    # Test duplicate email
    response = client.post(
        '/auth/register',
        data={
            'username': 'another',
            'email': 'test@example.com',  # Already exists
            'password': 'Password123!',
            'password2': 'Password123!'
        }
    )
    assert b'Email already registered' in response.data
    
    # Test password mismatch
    response = client.post(
        '/auth/register',
        data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Password123!',
            'password2': 'DifferentPass123!'
        }
    )
    assert b'Passwords must match' in response.data
    
    # Test weak password
    response = client.post(
        '/auth/register',
        data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'weak',
            'password2': 'weak'
        }
    )
    assert b'Password must be at least 8 characters' in response.data

def test_login(client, auth):
    """Test user login."""
    # Test GET request
    assert client.get('/auth/login').status_code == 200
    
    # Test successful login
    response = auth.login()
    assert response.headers["Location"] == "/"
    
    # Test user is logged in
    with client:
        client.get('/')
        assert session['user_id'] is not None
        assert g.user.email == 'test@example.com'

def test_login_validation(client):
    """Test login validation."""
    # Test invalid email
    response = client.post(
        '/auth/login',
        data={
            'email': 'wrong@example.com',
            'password': 'password'
        }
    )
    assert b'Invalid email or password' in response.data
    
    # Test invalid password
    response = client.post(
        '/auth/login',
        data={
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
    )
    assert b'Invalid email or password' in response.data

def test_logout(client, auth):
    """Test user logout."""
    auth.login()
    
    with client:
        auth.logout()
        assert 'user_id' not in session

def test_password_reset_request(client, app):
    """Test password reset request."""
    # Test GET request
    assert client.get('/auth/reset_password_request').status_code == 200
    
    # Test with valid email
    response = client.post(
        '/auth/reset_password_request',
        data={'email': 'test@example.com'}
    )
    assert response.headers["Location"] == "/auth/login"
    
    # Test with invalid email
    response = client.post(
        '/auth/reset_password_request',
        data={'email': 'nonexistent@example.com'}
    )
    assert b'No account found with that email address' in response.data

def test_password_reset(client, app):
    """Test password reset."""
    # Create a user and generate reset token
    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        token = user.get_reset_password_token()
    
    # Test GET request with valid token
    assert client.get(f'/auth/reset_password/{token}').status_code == 200
    
    # Test successful password reset
    response = client.post(
        f'/auth/reset_password/{token}',
        data={
            'password': 'NewPassword123!',
            'password2': 'NewPassword123!'
        }
    )
    assert response.headers["Location"] == "/auth/login"
    
    # Test login with new password
    response = client.post(
        '/auth/login',
        data={
            'email': 'test@example.com',
            'password': 'NewPassword123!'
        }
    )
    assert response.headers["Location"] == "/"

def test_change_password(client, auth, app):
    """Test password change."""
    auth.login()
    
    # Test GET request
    assert client.get('/auth/change_password').status_code == 200
    
    # Test successful password change
    response = client.post(
        '/auth/change_password',
        data={
            'current_password': 'password',
            'new_password': 'NewPassword123!',
            'new_password2': 'NewPassword123!'
        }
    )
    assert response.headers["Location"] == "/auth/login"
    
    # Test login with new password
    response = client.post(
        '/auth/login',
        data={
            'email': 'test@example.com',
            'password': 'NewPassword123!'
        }
    )
    assert response.headers["Location"] == "/"

def test_admin_required(client, auth):
    """Test admin-only access."""
    # Test unauthenticated access
    response = client.get('/webb-admin/')
    assert response.headers["Location"].startswith("/auth/login")
    
    # Test non-admin access
    auth.login()
    response = client.get('/webb-admin/')
    assert response.status_code == 403
    
    # Test admin access
    auth.login('admin@example.com', 'password')
    response = client.get('/webb-admin/')
    assert response.status_code == 200
