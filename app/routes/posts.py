from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Post, Comment
from app.forms import PostForm, CommentForm

posts_bp = Blueprint('posts', __name__)


@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create a new blog post."""
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data.strip(),
            category=form.category.data,
            tags=form.tags.data.strip() if form.tags.data else '',
            content=form.content.data.strip(),
            author=current_user
        )
        db.session.add(post)
        db.session.commit()

        flash('Your blog post has been published successfully!', 'success')
        return redirect(url_for('posts.post_detail', post_id=post.id))

    return render_template('create_post.html', form=form)


@posts_bp.route('/<int:post_id>', methods=['GET'])
def post_detail(post_id):
    """View a single blog post along with its comments."""
    post = db.get_or_404(Post, post_id)
    comment_form = CommentForm()
    comments = post.comments.all()

    # Related articles in the same category
    related_posts = Post.query.filter(
        Post.category == post.category,
        Post.id != post.id
    ).order_by(Post.created_at.desc()).limit(3).all()

    return render_template(
        'post_detail.html',
        post=post,
        comments=comments,
        comment_form=comment_form,
        related_posts=related_posts
    )


@posts_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit an existing blog post (author only)."""
    post = db.get_or_404(Post, post_id)

    # Ownership check
    if post.author != current_user:
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data.strip()
        post.category = form.category.data
        post.tags = form.tags.data.strip() if form.tags.data else ''
        post.content = form.content.data.strip()
        post.updated_at = datetime.now(timezone.utc)
        db.session.commit()

        flash('Your post has been updated successfully!', 'success')
        return redirect(url_for('posts.post_detail', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.category.data = post.category
        form.tags.data = post.tags
        form.content.data = post.content

    return render_template('edit_post.html', form=form, post=post)


@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete a blog post (author only)."""
    post = db.get_or_404(Post, post_id)

    # Ownership check
    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash('The post has been deleted successfully.', 'info')
    return redirect(url_for('main.dashboard'))


@posts_bp.route('/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """Add a new comment to a post."""
    post = db.get_or_404(Post, post_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data.strip(),
            author=current_user,
            post=post
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment was posted!', 'success')
    else:
        for error in form.content.errors:
            flash(f'Comment error: {error}', 'danger')

    return redirect(url_for('posts.post_detail', post_id=post.id))


@posts_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Delete a comment (comment author or post author only)."""
    comment = db.get_or_404(Comment, comment_id)
    post_id = comment.post_id

    # Check permission: either comment author or blog post author can remove
    if comment.author != current_user and comment.post.author != current_user:
        abort(403)

    db.session.delete(comment)
    db.session.commit()
    flash('Comment removed successfully.', 'info')
    return redirect(url_for('posts.post_detail', post_id=post_id))
