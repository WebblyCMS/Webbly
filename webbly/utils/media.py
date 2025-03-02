import os
import uuid
from datetime import datetime
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif'},
    'document': {'pdf', 'doc', 'docx', 'txt'},
    'video': {'mp4', 'webm'},
    'audio': {'mp3', 'wav'}
}

def allowed_file(filename, file_type='image'):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(file_type, set())

def get_unique_filename(filename):
    """Generate a unique filename with UUID and timestamp."""
    ext = filename.rsplit('.', 1)[1].lower()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}.{ext}"

def create_thumbnail(image_path, size=(300, 300)):
    """Create a thumbnail for an image."""
    thumb_path = image_path.rsplit('.', 1)[0] + '_thumb.' + image_path.rsplit('.', 1)[1]
    
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            img.thumbnail(size)
            img.save(thumb_path, quality=85, optimize=True)
            return os.path.basename(thumb_path)
    except Exception as e:
        current_app.logger.error(f"Error creating thumbnail: {str(e)}")
        return None

def save_image(file, directory='uploads/images'):
    """Save an uploaded image and create thumbnail."""
    if not file:
        return None
        
    filename = secure_filename(file.filename)
    if not allowed_file(filename, 'image'):
        raise ValueError('File type not allowed')
    
    # Create upload directory if it doesn't exist
    upload_path = os.path.join(current_app.root_path, 'static', directory)
    os.makedirs(upload_path, exist_ok=True)
    
    # Generate unique filename
    unique_filename = get_unique_filename(filename)
    file_path = os.path.join(upload_path, unique_filename)
    
    # Save original file
    file.save(file_path)
    
    # Create thumbnail
    create_thumbnail(file_path)
    
    return os.path.join(directory, unique_filename)

def save_file(file, directory='uploads/files'):
    """Save an uploaded file."""
    if not file:
        return None
        
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    # Determine file type and check if allowed
    file_type = next((t for t, exts in ALLOWED_EXTENSIONS.items() if ext in exts), None)
    if not file_type:
        raise ValueError('File type not allowed')
    
    # Create upload directory if it doesn't exist
    upload_path = os.path.join(current_app.root_path, 'static', directory)
    os.makedirs(upload_path, exist_ok=True)
    
    # Generate unique filename
    unique_filename = get_unique_filename(filename)
    file_path = os.path.join(upload_path, unique_filename)
    
    # Save file
    file.save(file_path)
    
    return os.path.join(directory, unique_filename)

def delete_file(filepath):
    """Delete a file and its thumbnail if it exists."""
    if not filepath:
        return False
    
    # Get full path
    full_path = os.path.join(current_app.root_path, 'static', filepath)
    
    # Delete thumbnail if it exists
    thumb_path = full_path.rsplit('.', 1)[0] + '_thumb.' + full_path.rsplit('.', 1)[1]
    if os.path.exists(thumb_path):
        try:
            os.remove(thumb_path)
        except OSError:
            current_app.logger.error(f"Error deleting thumbnail: {thumb_path}")
    
    # Delete original file
    try:
        os.remove(full_path)
        return True
    except OSError:
        current_app.logger.error(f"Error deleting file: {full_path}")
        return False

def get_media_list(directory='uploads', file_type=None):
    """Get list of uploaded media files."""
    media_path = os.path.join(current_app.root_path, 'static', directory)
    if not os.path.exists(media_path):
        return []
    
    media_files = []
    for root, _, files in os.walk(media_path):
        for file in files:
            if file.endswith('_thumb.jpg') or file.endswith('_thumb.png'):
                continue
                
            ext = file.rsplit('.', 1)[1].lower() if '.' in file else ''
            if file_type and ext not in ALLOWED_EXTENSIONS.get(file_type, set()):
                continue
                
            rel_path = os.path.relpath(os.path.join(root, file), 
                                     os.path.join(current_app.root_path, 'static'))
            
            media_files.append({
                'name': file,
                'path': rel_path,
                'type': next((t for t, exts in ALLOWED_EXTENSIONS.items() 
                            if ext in exts), 'unknown'),
                'size': os.path.getsize(os.path.join(root, file)),
                'modified': datetime.fromtimestamp(
                    os.path.getmtime(os.path.join(root, file))
                )
            })
    
    return sorted(media_files, key=lambda x: x['modified'], reverse=True)
