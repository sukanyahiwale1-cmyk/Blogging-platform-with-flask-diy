from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_
from app.models import Post, User, Comment

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page displaying latest blog posts with search and category filtering."""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip()
    selected_category = request.args.get('category', '').strip()
    selected_tag = request.args.get('tag', '').strip()

    query = Post.query

    # Apply search filter across title and content
    if search_query:
        query = query.filter(
            or_(
                Post.title.ilike(f'%{search_query}%'),
                Post.content.ilike(f'%{search_query}%')
            )
        )

    # Apply category filter
    if selected_category:
        query = query.filter(Post.category == selected_category)

    # Apply tag filter
    if selected_tag:
        query = query.filter(Post.tags.ilike(f'%{selected_tag}%'))

    # Order newest first and paginate
    posts_pagination = query.order_by(Post.created_at.desc()).paginate(
        page=page,
        per_page=current_app.config.get('POSTS_PER_PAGE', 6),
        error_out=False
    )

    # Sidebar data: recent 5 posts and trending categories
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()

    return render_template(
        'index.html',
        posts=posts_pagination.items,
        pagination=posts_pagination,
        search_query=search_query,
        selected_category=selected_category,
        selected_tag=selected_tag,
        recent_posts=recent_posts
    )


@main_bp.route('/search')
def search():
    """Search and filter page."""
    search_query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    tag = request.args.get('tag', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Post.query
    if search_query:
        query = query.filter(
            or_(
                Post.title.ilike(f'%{search_query}%'),
                Post.content.ilike(f'%{search_query}%')
            )
        )
    if category:
        query = query.filter(Post.category == category)
    if tag:
        query = query.filter(Post.tags.ilike(f'%{tag}%'))

    pagination = query.order_by(Post.created_at.desc()).paginate(
        page=page,
        per_page=current_app.config.get('POSTS_PER_PAGE', 6),
        error_out=False
    )

    return render_template(
        'search.html',
        posts=pagination.items,
        pagination=pagination,
        search_query=search_query,
        selected_category=category,
        selected_tag=tag
    )


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing user stats, their articles, and platform metrics."""
    # User's own posts
    user_posts = current_user.posts.order_by(Post.created_at.desc()).all()

    # Platform metrics
    total_platform_posts = Post.query.count()
    total_platform_users = User.query.count()
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()

    # User's total received comments on their posts
    user_post_ids = [p.id for p in user_posts]
    received_comments_count = Comment.query.filter(Comment.post_id.in_(user_post_ids)).count() if user_post_ids else 0

    return render_template(
        'dashboard.html',
        user=current_user,
        user_posts=user_posts,
        total_platform_posts=total_platform_posts,
        total_platform_users=total_platform_users,
        recent_posts=recent_posts,
        received_comments_count=received_comments_count
    )
