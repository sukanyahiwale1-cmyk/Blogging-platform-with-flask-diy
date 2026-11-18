from urllib.parse import urlsplit
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, Post
from app.forms import RegistrationForm, LoginForm, ProfileUpdateForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user account."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Your account has been created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Log in an existing user via username or email."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        login_input = form.login_id.data.strip()
        # Find user by username or email
        user = User.query.filter(
            (User.username == login_input) | (User.email == login_input.lower())
        ).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.username}!', 'success')

            # Prevent open redirect vulnerability
            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('main.dashboard')
            return redirect(next_page)
        else:
            flash('Invalid username/email or password. Please try again.', 'danger')

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out current user."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    """View user profile, author's posts, and edit profile if owner."""
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.created_at.desc()).all()

    form = None
    if current_user.is_authenticated and current_user.id == user.id:
        form = ProfileUpdateForm(original_username=current_user.username)
        if form.validate_on_submit():
            current_user.username = form.username.data.strip()
            current_user.bio = form.bio.data.strip()
            db.session.commit()
            flash('Your profile has been updated successfully!', 'success')
            return redirect(url_for('auth.profile', username=current_user.username))
        elif request.method == 'GET':
            form.username.data = current_user.username
            form.bio.data = current_user.bio

    return render_template(
        'profile.html',
        user=user,
        posts=posts,
        form=form
    )
