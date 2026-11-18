from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from flask_login import current_user
from sqlalchemy import or_, func
from app import db
from app.models import Post, User, Comment

api_bp = Blueprint('api', __name__)


def get_authenticated_user():
    """Helper to detect authenticated user via session or Basic Auth/headers."""
    if current_user.is_authenticated:
        return current_user

    # Support HTTP Basic Auth for REST API clients / curl
    auth = request.authorization
    if auth and auth.username and auth.password:
        user = User.query.filter(
            (User.username == auth.username) | (User.email == auth.username.lower())
        ).first()
        if user and user.check_password(auth.password):
            return user

    return None


@api_bp.route('/posts', methods=['GET'])
def get_posts():
    """REST API: Get all blog posts with optional filters."""
    category = request.args.get('category', '').strip()
    search = request.args.get('search', '').strip()
    tag = request.args.get('tag', '').strip()
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    query = Post.query

    if search:
        query = query.filter(
            or_(
                Post.title.ilike(f'%{search}%'),
                Post.content.ilike(f'%{search}%')
            )
        )
    if category:
        query = query.filter(Post.category == category)
    if tag:
        query = query.filter(Post.tags.ilike(f'%{tag}%'))

    pagination = query.order_by(Post.created_at.desc()).paginate(
        page=page,
        per_page=min(limit, 50),
        error_out=False
    )

    return jsonify({
        'success': True,
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'per_page': pagination.per_page,
        'posts': [post.to_dict() for post in pagination.items]
    }), 200


@api_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """REST API: Get a specific blog post by ID with comments."""
    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({
            'success': False,
            'message': f'Post with ID {post_id} not found.'
        }), 404

    return jsonify({
        'success': True,
        'post': post.to_dict(include_comments=True)
    }), 200


@api_bp.route('/posts', methods=['POST'])
def create_post():
    """REST API: Create a new blog post."""
    user = get_authenticated_user()
    if not user:
        return jsonify({
            'success': False,
            'message': 'Authentication required. Log in via session or provide Basic Auth credentials.'
        }), 401

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON body.'}), 400

    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    category = data.get('category', 'General').strip()
    tags = data.get('tags', '').strip()

    if not title or not content:
        return jsonify({
            'success': False,
            'message': 'Both title and content are required.'
        }), 400

    post = Post(
        title=title,
        content=content,
        category=category or 'General',
        tags=tags,
        author=user
    )
    db.session.add(post)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Post created successfully.',
        'post': post.to_dict()
    }), 201


@api_bp.route('/posts/<int:post_id>', methods=['PUT', 'PATCH'])
def update_post(post_id):
    """REST API: Update a blog post (author only)."""
    user = get_authenticated_user()
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required.'}), 401

    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({'success': False, 'message': f'Post with ID {post_id} not found.'}), 404

    if post.author != user:
        return jsonify({
            'success': False,
            'message': 'Forbidden: You can only edit your own posts.'
        }), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON body.'}), 400

    if 'title' in data:
        title = data['title'].strip()
        if not title:
            return jsonify({'success': False, 'message': 'Title cannot be empty.'}), 400
        post.title = title

    if 'content' in data:
        content = data['content'].strip()
        if not content:
            return jsonify({'success': False, 'message': 'Content cannot be empty.'}), 400
        post.content = content

    if 'category' in data:
        post.category = data['category'].strip() or 'General'

    if 'tags' in data:
        post.tags = data['tags'].strip()

    post.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Post updated successfully.',
        'post': post.to_dict()
    }), 200


@api_bp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """REST API: Delete a blog post (author only)."""
    user = get_authenticated_user()
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required.'}), 401

    post = db.session.get(Post, post_id)
    if not post:
        return jsonify({'success': False, 'message': f'Post with ID {post_id} not found.'}), 404

    if post.author != user:
        return jsonify({
            'success': False,
            'message': 'Forbidden: You can only delete your own posts.'
        }), 403

    db.session.delete(post)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Post {post_id} deleted successfully.'
    }), 200


@api_bp.route('/categories', methods=['GET'])
def get_categories():
    """REST API: Get all categories with their post counts."""
    results = db.session.query(
        Post.category, func.count(Post.id)
    ).group_by(Post.category).all()

    categories = [{'category': r[0], 'post_count': r[1]} for r in results]
    return jsonify({
        'success': True,
        'categories': categories
    }), 200
