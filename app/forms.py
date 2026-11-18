import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models import User
from config import Config


class RegistrationForm(FlaskForm):
    """User registration form."""
    username = StringField('Username', validators=[
        DataRequired(message="Username is required."),
        Length(min=3, max=30, message="Username must be between 3 and 30 characters.")
    ])
    email = StringField('Email Address', validators=[
        DataRequired(message="Email address is required."),
        Email(message="Please enter a valid email address."),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required."),
        Length(min=6, message="Password must be at least 6 characters long.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password."),
        EqualTo('password', message="Passwords must match.")
    ])
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        if not re.match(r'^[a-zA-Z0-9_.]+$', username.data):
            raise ValidationError('Username can only contain letters, numbers, dots, and underscores.')
        user = User.query.filter_by(username=username.data.strip()).first()
        if user:
            raise ValidationError('That username is already taken. Please choose another.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.strip().lower()).first()
        if user:
            raise ValidationError('That email is already registered. Please log in instead.')


class LoginForm(FlaskForm):
    """User login form supporting login via username or email."""
    login_id = StringField('Username or Email', validators=[
        DataRequired(message="Please enter your username or email.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required.")
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class PostForm(FlaskForm):
    """Form to create and edit blog posts."""
    title = StringField('Post Title', validators=[
        DataRequired(message="Post title is required."),
        Length(min=5, max=200, message="Title must be between 5 and 200 characters.")
    ])
    category = SelectField('Category', choices=Config.CATEGORIES, validators=[
        DataRequired(message="Please select a category.")
    ])
    tags = StringField('Tags (comma-separated)', validators=[
        Optional(),
        Length(max=200, message="Tags string must not exceed 200 characters.")
    ])
    content = TextAreaField('Content', validators=[
        DataRequired(message="Post content cannot be empty."),
        Length(min=10, message="Content must be at least 10 characters long.")
    ])
    submit = SubmitField('Publish Post')


class CommentForm(FlaskForm):
    """Form to submit comments under a post."""
    content = TextAreaField('Add a thoughtful comment...', validators=[
        DataRequired(message="Comment text cannot be empty."),
        Length(min=2, max=1000, message="Comment must be between 2 and 1000 characters.")
    ])
    submit = SubmitField('Post Comment')


class ProfileUpdateForm(FlaskForm):
    """Form for users to edit their profile."""
    username = StringField('Username', validators=[
        DataRequired(message="Username is required."),
        Length(min=3, max=30)
    ])
    bio = TextAreaField('Bio / About Me', validators=[
        Optional(),
        Length(max=300, message="Bio must not exceed 300 characters.")
    ])
    submit = SubmitField('Save Profile')

    def __init__(self, original_username, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data.strip() != self.original_username:
            if not re.match(r'^[a-zA-Z0-9_.]+$', username.data):
                raise ValidationError('Username can only contain letters, numbers, dots, and underscores.')
            user = User.query.filter_by(username=username.data.strip()).first()
            if user:
                raise ValidationError('Username is already taken by another user.')
