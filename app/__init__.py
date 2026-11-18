import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

# Configure Flask-Login
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    """Application factory pattern to configure and create the Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # User loader for Flask-Login
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.posts import posts_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(posts_bp, url_prefix='/posts')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Exempt API from CSRF if clients use standard REST headers (or use exempt for pure JSON API)
    csrf.exempt(api_bp)

    # Context processors to inject global variables in all Jinja templates
    @app.context_processor
    def inject_globals():
        from app.models import Post, User
        categories = [c[0] for c in app.config.get('CATEGORIES', [])]
        total_posts = Post.query.count()
        total_users = User.query.count()
        return dict(
            categories=categories,
            global_total_posts=total_posts,
            global_total_users=total_users
        )

    # Custom Jinja filters
    @app.template_filter('time_ago')
    def time_ago(dt):
        from datetime import datetime, timezone
        if not dt:
            return ''
        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            # Assume UTC if naive
            from datetime import timezone
            dt = dt.replace(tzinfo=timezone.utc)
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return 'just now'
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} min{'s' if minutes > 1 else ''} ago"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif seconds < 604800:
            days = seconds // 86400
            return f"{days} day{'s' if days > 1 else ''} ago"
        else:
            return dt.strftime('%b %d, %Y')

    # Custom Error Handlers
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Ensure database tables exist automatically on startup for development convenience
    with app.app_context():
        db.create_all()

    return app
