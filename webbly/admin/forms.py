from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, URL
from ..utils.theme import get_available_templates

class PostForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=1, max=200)
    ])
    content = TextAreaField('Content', validators=[DataRequired()])
    excerpt = TextAreaField('Excerpt', validators=[
        Optional(),
        Length(max=300)
    ])
    featured_image = FileField('Featured Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    published = BooleanField('Published')
    submit = SubmitField('Save Post')

class PageForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=1, max=200)
    ])
    content = TextAreaField('Content', validators=[DataRequired()])
    template = SelectField('Template', choices=[
        ('default', 'Default Template'),
        ('full-width', 'Full Width'),
        ('sidebar', 'With Sidebar'),
        ('landing', 'Landing Page')
    ])
    published = BooleanField('Published')
    submit = SubmitField('Save Page')

    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        # Update template choices from available theme templates
        templates = get_available_templates()
        if templates:
            self.template.choices = templates

class SettingsForm(FlaskForm):
    site_title = StringField('Site Title', validators=[
        DataRequired(),
        Length(min=1, max=100)
    ])
    site_description = TextAreaField('Site Description', validators=[
        Optional(),
        Length(max=300)
    ])
    posts_per_page = StringField('Posts Per Page', validators=[DataRequired()])
    enable_comments = BooleanField('Enable Comments')
    comment_moderation = BooleanField('Enable Comment Moderation')
    site_logo = FileField('Site Logo', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    favicon = FileField('Favicon', validators=[
        Optional(),
        FileAllowed(['ico', 'png'], 'ICO or PNG only!')
    ])
    analytics_id = StringField('Google Analytics ID', validators=[Optional()])
    social_twitter = StringField('Twitter URL', validators=[
        Optional(),
        URL()
    ])
    social_facebook = StringField('Facebook URL', validators=[
        Optional(),
        URL()
    ])
    social_instagram = StringField('Instagram URL', validators=[
        Optional(),
        URL()
    ])
    footer_text = TextAreaField('Footer Text', validators=[Optional()])
    custom_css = TextAreaField('Custom CSS', validators=[Optional()])
    custom_js = TextAreaField('Custom JavaScript', validators=[Optional()])
    submit = SubmitField('Save Settings')

class ThemeForm(FlaskForm):
    name = StringField('Theme Name', validators=[
        DataRequired(),
        Length(min=1, max=100)
    ])
    directory = StringField('Directory Name', validators=[
        DataRequired(),
        Length(min=1, max=100)
    ])
    version = StringField('Version', validators=[
        DataRequired(),
        Length(min=1, max=20)
    ])
    author = StringField('Author', validators=[
        DataRequired(),
        Length(min=1, max=100)
    ])
    description = TextAreaField('Description', validators=[Optional()])
    screenshot = FileField('Screenshot', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    submit = SubmitField('Save Theme')

class PluginForm(FlaskForm):
    name = StringField('Plugin Name', validators=[
        DataRequired(),
        Length(min=1, max=100)
    ])
    directory = StringField('Directory Name', validators=[
        DataRequired(),
        Length(min=1, max=100)
    ])
    version = StringField('Version', validators=[
        DataRequired(),
        Length(min=1, max=20)
    ])
    author = StringField('Author', validators=[
        DataRequired(),
        Length(min=1, max=100)
    ])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Plugin')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Length(min=6, max=120)
    ])
    is_admin = BooleanField('Admin Privileges')
    submit = SubmitField('Save User')
