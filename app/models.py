import hashlib
import math
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


def utc_now():
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    """User model representing registered authors and commenters."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    bio = db.Column(db.String(300), default='Passionate reader and contributor.')
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    posts = db.relationship(
        'Post',
        backref='author',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    comments = db.relationship(
        'Comment',
        backref='author',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        """Hash and store user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify hashed password."""
        return check_password_hash(self.password_hash, password)

    def avatar(self, size=100):
        """Return URL for user avatar using Gravatar with UI-Avatars fallback."""
        clean_email = self.email.strip().lower()
        digest = hashlib.md5(clean_email.encode('utf-8')).hexdigest()
        fallback = f"https://ui-avatars.com/api/{self.username}/{size}/4f46e5/ffffff"
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"

    @property
    def total_posts(self):
        return self.posts.count()

    @property
    def total_comments(self):
        return self.comments.count()

    def to_dict(self):
        """Serialize user object to dictionary for API responses."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'bio': self.bio,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'total_posts': self.total_posts,
            'total_comments': self.total_comments
        }

    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    """Blog post model representing articles published by users."""
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='General', index=True)
    tags = db.Column(db.String(200), default='')
    created_at = db.Column(db.DateTime, default=utc_now, index=True)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Relationship to comments
    comments = db.relationship(
        'Comment',
        backref='post',
        lazy='dynamic',
        cascade='all, delete-orphan',
        order_by='Comment.created_at.desc()'
    )

    def get_tag_list(self):
        """Return tags as clean list of strings."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def reading_time(self):
        """Calculate estimated reading time in minutes (based on 200 wpm)."""
        word_count = len(self.content.split())
        return max(1, math.ceil(word_count / 200))

    def excerpt(self, length=180):
        """Generate a short preview snippet of post content."""
        clean_text = ' '.join(self.content.split())
        if len(clean_text) <= length:
            return clean_text
        return clean_text[:length].rsplit(' ', 1)[0] + '...'

    def to_dict(self, include_comments=False):
        """Serialize post to dictionary for API responses."""
        data = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'tags': self.get_tag_list(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'reading_time_minutes': self.reading_time(),
            'author': {
                'id': self.author.id,
                'username': self.author.username
            } if self.author else None,
            'comments_count': self.comments.count()
        }
        if include_comments:
            data['comments'] = [c.to_dict() for c in self.comments.all()]
        return data

    def __repr__(self):
        return f'<Post {self.title[:30]}>'


class Comment(db.Model):
    """Comment model representing replies under blog posts."""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)

    def to_dict(self):
        """Serialize comment to dictionary for API responses."""
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'post_id': self.post_id,
            'author': {
                'id': self.author.id,
                'username': self.author.username
            } if self.author else None
        }

    def __repr__(self):
        return f'<Comment on Post {self.post_id} by User {self.user_id}>'
