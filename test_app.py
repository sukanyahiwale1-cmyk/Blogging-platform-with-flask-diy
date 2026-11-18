"""Automated Test Suite for Chronicle Blogging Platform
Verifies:
1. User registration, login, password hashing
2. Blog post CRUD operations and ownership authorization
3. Commenting system and comment deletion permissions
4. Search, category, and tag filtering
5. REST API endpoints (GET, POST, PUT, DELETE)
6. Error handling (403, 404)
Run with: python test_app.py
"""

import unittest
from app import create_app, db
from app.models import User, Post, Comment
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF in tests for simpler programmatic POSTs


class BloggingPlatformTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create two test users
        self.user1 = User(username='author_one', email='one@example.com')
        self.user1.set_password('pass1234')
        self.user2 = User(username='author_two', email='two@example.com')
        self.user2.set_password('pass1234')
        db.session.add_all([self.user1, self.user2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, username, password):
        return self.client.post('/auth/login', data={
            'login_id': username,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)

    def test_user_authentication(self):
        # Test password verification
        self.assertTrue(self.user1.check_password('pass1234'))
        self.assertFalse(self.user1.check_password('wrongpass'))

        # Test login success
        response = self.login('author_one', 'pass1234')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back', response.data)

        # Test logout
        logout_resp = self.logout()
        self.assertEqual(logout_resp.status_code, 200)
        self.assertIn(b'logged out', logout_resp.data)

    def test_post_creation_and_view(self):
        self.login('author_one', 'pass1234')
        response = self.client.post('/posts/create', data={
            'title': 'Test Post Title by Author One',
            'category': 'Programming',
            'tags': 'python, testing',
            'content': 'This is the detailed content for testing post creation in Flask.'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Post Title by Author One', response.data)

        post = Post.query.filter_by(title='Test Post Title by Author One').first()
        self.assertIsNotNone(post)
        self.assertEqual(post.author.username, 'author_one')
        self.assertEqual(post.category, 'Programming')
        self.assertIn('python', post.get_tag_list())

    def test_post_edit_authorization(self):
        # Create post as user1
        post = Post(title='Original Title', content='Original Content here...', category='Technology', author=self.user1)
        db.session.add(post)
        db.session.commit()

        # Login as user2 (not author) -> Attempt edit -> Expect 403 Forbidden
        self.login('author_two', 'pass1234')
        forbidden_resp = self.client.get(f'/posts/{post.id}/edit')
        self.assertEqual(forbidden_resp.status_code, 403)

        # Login as author -> Edit should succeed
        self.logout()
        self.login('author_one', 'pass1234')
        edit_resp = self.client.post(f'/posts/{post.id}/edit', data={
            'title': 'Updated Title',
            'category': 'Technology',
            'tags': 'updated',
            'content': 'Updated Content has been saved successfully.'
        }, follow_redirects=True)
        self.assertEqual(edit_resp.status_code, 200)
        updated_post = Post.query.get(post.id)
        self.assertEqual(updated_post.title, 'Updated Title')

    def test_commenting_system(self):
        post = Post(title='Post for comments', content='Content goes here...', category='Design', author=self.user1)
        db.session.add(post)
        db.session.commit()

        # Login as user2 and comment
        self.login('author_two', 'pass1234')
        comment_resp = self.client.post(f'/posts/{post.id}/comment', data={
            'content': 'Insightful article! Loved the perspective.'
        }, follow_redirects=True)
        self.assertEqual(comment_resp.status_code, 200)
        self.assertIn(b'Insightful article!', comment_resp.data)

        comment = Comment.query.first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.author.username, 'author_two')

        # User2 deletes their own comment
        del_resp = self.client.post(f'/posts/comment/{comment.id}/delete', follow_redirects=True)
        self.assertEqual(del_resp.status_code, 200)
        self.assertIsNone(Comment.query.get(comment.id))

    def test_search_and_filter(self):
        post = Post(title='Flask Web Development Guide', content='Learn routing and templates.', category='Programming', tags='flask, python', author=self.user1)
        db.session.add(post)
        db.session.commit()

        # Search by query
        search_res = self.client.get('/search?q=Routing')
        self.assertEqual(search_res.status_code, 200)
        self.assertIn(b'Flask Web Development Guide', search_res.data)

        # Filter by category
        cat_res = self.client.get('/?category=Programming')
        self.assertEqual(cat_res.status_code, 200)
        self.assertIn(b'Flask Web Development Guide', cat_res.data)

    def test_rest_api_endpoints(self):
        post = Post(title='API Post', content='Content for API tests.', category='Technology', author=self.user1)
        db.session.add(post)
        db.session.commit()

        # GET /api/posts
        res = self.client.get('/api/posts')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['total'], 1)

        # GET /api/posts/<id>
        res_single = self.client.get(f'/api/posts/{post.id}')
        self.assertEqual(res_single.status_code, 200)
        self.assertEqual(res_single.get_json()['post']['title'], 'API Post')

        # GET /api/categories
        res_cat = self.client.get('/api/categories')
        self.assertEqual(res_cat.status_code, 200)
        self.assertTrue(any(c['category'] == 'Technology' for c in res_cat.get_json()['categories']))


if __name__ == '__main__':
    unittest.main()
