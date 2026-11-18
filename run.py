import os
from app import create_app, db
from app.models import User, Post, Comment

# Create app instance using development config
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Make models available in `flask shell` without manual imports."""
    return {
        'db': db,
        'User': User,
        'Post': Post,
        'Comment': Comment
    }


if __name__ == '__main__':
    # Run development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 'yes']
    print("=" * 60)
    print(f" * Starting Chronicle Blogging Platform on http://127.0.0.1:{port}")
    print(f" * Debug mode: {'on' if debug else 'off'}")
    print("=" * 60)
    app.run(host='127.0.0.1', port=port, debug=debug)
