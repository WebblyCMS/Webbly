import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from webbly.tasks import TaskManager
from webbly.models import Post, Page, User, Comment, db

def test_task_manager_initialization(app):
    """Test task manager initialization."""
    with app.app_context():
        task_manager = TaskManager(app)
        
        # Check default tasks are registered
        assert 'cleanup_old_drafts' in task_manager.tasks
        assert 'cleanup_expired_sessions' in task_manager.tasks
        assert 'cleanup_old_media' in task_manager.tasks
        assert 'send_digest_emails' in task_manager.tasks
        assert 'update_search_index' in task_manager.tasks
        assert 'update_sitemap' in task_manager.tasks
        assert 'backup_database' in task_manager.tasks

def test_task_registration(app):
    """Test task registration."""
    with app.app_context():
        task_manager = TaskManager(app)
        
        # Register new task
        def test_task():
            return "Task executed"
        
        task_manager.register_task('test_task', test_task)
        assert 'test_task' in task_manager.tasks
        
        # Test task execution
        result = task_manager.tasks['test_task']()
        assert result == "Task executed"

def test_task_scheduling(app):
    """Test task scheduling."""
    with app.app_context():
        task_manager = TaskManager(app)
        
        # Schedule task
        task_manager.schedule_task('cleanup_old_drafts', hours=24)
        
        # Check task is scheduled
        scheduled = next(t for t in task_manager.scheduled_tasks 
                       if t['name'] == 'cleanup_old_drafts')
        assert scheduled['interval'] == 24 * 3600  # 24 hours in seconds

def test_task_execution(app):
    """Test task execution."""
    with app.app_context():
        task_manager = TaskManager(app)
        
        # Create mock task
        mock_task = MagicMock()
        task_manager.register_task('mock_task', mock_task)
        
        # Run task
        task_manager.run_task('mock_task')
        
        # Wait for task to complete
        import time
        time.sleep(0.1)
        
        # Check task was called
        mock_task.assert_called_once()

def test_cleanup_old_drafts(app, test_user):
    """Test cleanup of old draft posts."""
    with app.app_context():
        task_manager = TaskManager(app)
        
        # Create old draft post
        old_draft = Post(
            title='Old Draft',
            content='Draft content',
            author=test_user,
            published=False,
            updated_at=datetime.utcnow() - timedelta(days=31)
        )
        db.session.add(old_draft)
        db.session.commit()
        
        # Run cleanup task
        task_manager.tasks['cleanup_old_drafts']()
        
        # Check draft was deleted
        assert Post.query.filter_by(title='Old Draft').first() is None

def test_cleanup_expired_sessions(app):
    """Test cleanup of expired sessions."""
    with app.app_context():
        task_manager = TaskManager(app)
        
        # Create expired session file
        session_dir = app.config['SESSION_FILE_DIR']
        os.makedirs(session_dir, exist_ok=True)
        expired_session = os.path.join(session_dir, 'expired_session')
        with open(expired_session, 'w') as f:
            f.write('session data')
        
        # Set old modification time
        os.utime(expired_session, 
                 (datetime.now() - timedelta(days=8)).timestamp())
        
        # Run cleanup task
        task_manager.tasks['cleanup_expired_sessions']()
        
        # Check session was deleted
        assert not os.path.exists(expired_session)

def test_cleanup_old_media(app):
    """Test cleanup of old media files."""
    with app.app_context():
        task_manager = TaskManager(app)
        
        # Create test media file
        uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        test_file = os.path.join(uploads_dir, 'test.jpg')
        with open(test_file, 'w') as f:
            f.write('test data')
        
        # Set old modification time
        os.utime(test_file, 
                 (datetime.now() - timedelta(days=8)).timestamp())
        
        # Run cleanup task
        task_manager.tasks['cleanup_old_media']()
        
        # Check file was deleted
        assert not os.path.exists(test_file)

@patch('webbly.tasks.send_email')
def test_send_digest_emails(mock_send_email, app, test_user):
    """Test sending of digest emails."""
    with app.app_context():
        task_manager = TaskManager(app)
        
        # Create test post
        post = Post(
            title='Test Post',
            content='Test content',
            author=test_user,
            published=True,
            created_at=datetime.utcnow()
        )
        db.session.add(post)
        
        # Create subscribed user
        user = User(
            username='subscriber',
            email='sub@example.com',
            subscribed_to_digest=True
        )
        db.session.add(user)
        db.session.commit()
        
        # Run digest task
        task_manager.tasks['send_digest_emails']()
        
        # Check email was sent
        mock_send_email.assert_called_once()
        assert mock_send_email.call_args[1]['recipients'] == ['sub@example.com']

def test_database_backup(app):
    """Test database backup task."""
    with app.app_context():
        task_manager = TaskManager(app)
        
        # Run backup task
        task_manager.tasks['backup_database']()
        
        # Check backup was created
        backup_dir = os.path.join(app.root_path, 'backups')
        assert os.path.exists(backup_dir)
        assert any(f.endswith('.db') for f in os.listdir(backup_dir))

def test_scheduler_thread(app):
    """Test scheduler thread."""
    with app.app_context():
        task_manager = TaskManager(app)
        
        # Create mock task
        mock_task = MagicMock()
        task_manager.register_task('mock_task', mock_task)
        
        # Schedule task with short interval
        task_manager.schedule_task('mock_task', minutes=1)
        
        # Start scheduler
        task_manager.start_scheduler()
        
        # Wait for scheduler to run
        import time
        time.sleep(65)  # Wait just over a minute
        
        # Check task was called
        assert mock_task.call_count >= 1

def test_error_handling(app):
    """Test task error handling."""
    with app.app_context():
        task_manager = TaskManager(app)
        
        # Create failing task
        def failing_task():
            raise Exception("Task failed")
        
        task_manager.register_task('failing_task', failing_task)
        
        # Run task and check it doesn't crash the application
        task_manager.run_task('failing_task')
        
        # Check error was logged
        with open('logs/webbly.log') as f:
            log_content = f.read()
            assert "Task failed" in log_content
