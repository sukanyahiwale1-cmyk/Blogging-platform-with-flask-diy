import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Application configuration settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-dev-key-change-in-production-2025'
    
    # SQLite database configuration
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(instance_path, 'blog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Pagination
    POSTS_PER_PAGE = 6
    COMMENTS_PER_PAGE = 20
    
    # Categories available across the app
    CATEGORIES = [
        ('Technology', 'Technology'),
        ('Programming', 'Programming'),
        ('Web Development', 'Web Development'),
        ('Design', 'Design'),
        ('AI & Data', 'AI & Data'),
        ('Career & Productivity', 'Career & Productivity'),
        ('Lifestyle', 'Lifestyle'),
        ('General', 'General')
    ]
