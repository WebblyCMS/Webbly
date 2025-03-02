from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from .. import mail
import jwt
from time import time

def send_async_email(app, msg):
    """Send email asynchronously."""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Error sending email: {str(e)}")

def send_email(subject, recipients, text_body, html_body, sender=None):
    """Send an email."""
    if not sender:
        sender = current_app.config['MAIL_USERNAME']
    
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    
    # Send email asynchronously
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()

def send_password_reset_email(user):
    """Send password reset email to user."""
    token = user.get_reset_password_token()
    send_email(
        '[Webbly] Reset Your Password',
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt',
                                user=user, token=token),
        html_body=render_template('email/reset_password.html',
                                user=user, token=token)
    )

def send_comment_notification(comment):
    """Send notification when a new comment is posted."""
    # Get post author's email
    author_email = comment.post.author.email
    
    send_email(
        '[Webbly] New Comment on Your Post',
        recipients=[author_email],
        text_body=render_template('email/new_comment.txt',
                                comment=comment),
        html_body=render_template('email/new_comment.html',
                                comment=comment)
    )

def send_user_welcome_email(user):
    """Send welcome email to new user."""
    send_email(
        'Welcome to Webbly!',
        recipients=[user.email],
        text_body=render_template('email/welcome.txt',
                                user=user),
        html_body=render_template('email/welcome.html',
                                user=user)
    )

def send_contact_form_email(name, email, message):
    """Send contact form submission to admin."""
    admin_email = current_app.config.get('ADMIN_EMAIL')
    if not admin_email:
        current_app.logger.error("Admin email not configured")
        return
    
    send_email(
        'New Contact Form Submission',
        recipients=[admin_email],
        text_body=render_template('email/contact_form.txt',
                                name=name,
                                email=email,
                                message=message),
        html_body=render_template('email/contact_form.html',
                                name=name,
                                email=email,
                                message=message)
    )

def generate_confirmation_token(user, expires_in=3600):
    """Generate email confirmation token."""
    return jwt.encode(
        {
            'confirm': user.id,
            'exp': time() + expires_in
        },
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

def verify_confirmation_token(token):
    """Verify email confirmation token."""
    try:
        id = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )['confirm']
    except:
        return None
    return id

def send_confirmation_email(user):
    """Send email confirmation to user."""
    token = generate_confirmation_token(user)
    send_email(
        'Confirm Your Email',
        recipients=[user.email],
        text_body=render_template('email/confirm_email.txt',
                                user=user, token=token),
        html_body=render_template('email/confirm_email.html',
                                user=user, token=token)
    )
