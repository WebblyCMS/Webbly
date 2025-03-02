"""Test factories using factory_boy."""

import factory
from factory.faker import Faker
from datetime import datetime
from webbly.models import User, Post, Page, Theme, Plugin, Comment, Setting
from webbly import db

class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Base factory."""
    
    class Meta:
        abstract = True
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

class UserFactory(BaseFactory):
    """User factory."""
    
    class Meta:
        model = User
    
    username = Faker('user_name')
    email = Faker('email')
    password_hash = factory.LazyAttribute(lambda u: User.hash_password('password123'))
    is_admin = False
    active = True
    created_at = Faker('date_time_this_year')
    
    @factory.post_generation
    def posts(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            for post in extracted:
                self.posts.append(post)

class AdminFactory(UserFactory):
    """Admin user factory."""
    is_admin = True

class PostFactory(BaseFactory):
    """Post factory."""
    
    class Meta:
        model = Post
    
    title = Faker('sentence')
    content = Faker('text')
    excerpt = Faker('paragraph')
    slug = factory.LazyAttribute(lambda p: Post.generate_slug(p.title))
    published = True
    featured_image = None
    author = factory.SubFactory(UserFactory)
    created_at = Faker('date_time_this_year')
    updated_at = factory.LazyAttribute(lambda p: p.created_at)
    
    @factory.post_generation
    def comments(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            for comment in extracted:
                self.comments.append(comment)

class PageFactory(BaseFactory):
    """Page factory."""
    
    class Meta:
        model = Page
    
    title = Faker('sentence')
    content = Faker('text')
    slug = factory.LazyAttribute(lambda p: Page.generate_slug(p.title))
    template = 'default'
    published = True
    author = factory.SubFactory(UserFactory)
    created_at = Faker('date_time_this_year')
    updated_at = factory.LazyAttribute(lambda p: p.created_at)

class ThemeFactory(BaseFactory):
    """Theme factory."""
    
    class Meta:
        model = Theme
    
    name = Faker('word')
    directory = factory.LazyAttribute(lambda t: t.name.lower())
    version = '1.0.0'
    author = Faker('name')
    description = Faker('sentence')
    active = False
    
    @factory.post_generation
    def options(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            self.set_options(extracted)

class PluginFactory(BaseFactory):
    """Plugin factory."""
    
    class Meta:
        model = Plugin
    
    name = Faker('word')
    directory = factory.LazyAttribute(lambda p: p.name.lower())
    version = '1.0.0'
    author = Faker('name')
    description = Faker('sentence')
    active = False
    
    @factory.post_generation
    def settings(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            self.set_settings(extracted)

class CommentFactory(BaseFactory):
    """Comment factory."""
    
    class Meta:
        model = Comment
    
    content = Faker('paragraph')
    author = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
    approved = True
    created_at = Faker('date_time_this_year')

class SettingFactory(BaseFactory):
    """Setting factory."""
    
    class Meta:
        model = Setting
    
    key = Faker('word')
    value = Faker('sentence')

def create_test_data():
    """Create a set of test data."""
    # Create admin user
    admin = AdminFactory()
    
    # Create regular users
    users = UserFactory.create_batch(3)
    
    # Create posts
    posts = []
    for user in [admin] + users:
        user_posts = PostFactory.create_batch(3, author=user)
        posts.extend(user_posts)
    
    # Create comments
    for post in posts:
        CommentFactory.create_batch(2, post=post)
    
    # Create pages
    PageFactory.create_batch(3, author=admin)
    
    # Create theme
    theme = ThemeFactory(
        active=True,
        options={
            'primary_color': '#007bff',
            'font_family': 'Arial, sans-serif'
        }
    )
    
    # Create plugin
    plugin = PluginFactory(
        active=True,
        settings={
            'api_key': 'test_key',
            'enabled': True
        }
    )
    
    # Create settings
    settings = {
        'site_title': 'Test Site',
        'site_description': 'A test website',
        'posts_per_page': '10',
        'enable_comments': 'true',
        'comment_moderation': 'true'
    }
    for key, value in settings.items():
        SettingFactory(key=key, value=value)
    
    return {
        'admin': admin,
        'users': users,
        'posts': posts,
        'theme': theme,
        'plugin': plugin
    }

class CategoryFactory(BaseFactory):
    """Category factory."""
    
    class Meta:
        model = 'Category'  # Update with actual model name
    
    name = Faker('word')
    slug = factory.LazyAttribute(lambda c: c.name.lower())
    description = Faker('sentence')

class TagFactory(BaseFactory):
    """Tag factory."""
    
    class Meta:
        model = 'Tag'  # Update with actual model name
    
    name = Faker('word')
    slug = factory.LazyAttribute(lambda t: t.name.lower())

class MenuItemFactory(BaseFactory):
    """MenuItem factory."""
    
    class Meta:
        model = 'MenuItem'  # Update with actual model name
    
    title = Faker('word')
    url = Faker('url')
    order = factory.Sequence(lambda n: n)

class WidgetFactory(BaseFactory):
    """Widget factory."""
    
    class Meta:
        model = 'Widget'  # Update with actual model name
    
    type = 'text'
    title = Faker('word')
    content = Faker('paragraph')
    position = factory.Sequence(lambda n: n)
