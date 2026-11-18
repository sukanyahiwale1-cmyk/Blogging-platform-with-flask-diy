"""Database seeder script for Chronicle Blogging Platform.
Populates initial sample users, articles across diverse categories, and comments.
Run with: python seed.py
"""

from app import create_app, db
from app.models import User, Post, Comment

app = create_app()

with app.app_context():
    print("Resetting and initializing database...")
    db.create_all()

    # Check if data already exists
    if User.query.first():
        print("Database already contains data. Clear with db.drop_all() if you want a complete reset.")
    else:
        print("Creating demo users...")
        users_data = [
            {
                "username": "alex_dev",
                "email": "alex@example.com",
                "password": "password123",
                "bio": "Full-stack engineer, Python enthusiast, and open-source contributor."
            },
            {
                "username": "sarah_ai",
                "email": "sarah@example.com",
                "password": "password123",
                "bio": "AI researcher and data scientist writing on deep learning and neural models."
            },
            {
                "username": "elena_design",
                "email": "elena@example.com",
                "password": "password123",
                "bio": "Product designer focusing on accessible UI, typography, and micro-interactions."
            },
            {
                "username": "marcus_lead",
                "email": "marcus@example.com",
                "password": "password123",
                "bio": "Engineering leader sharing insights on system architecture and dev career growth."
            }
        ]

        created_users = []
        for u in users_data:
            user = User(username=u["username"], email=u["email"], bio=u["bio"])
            user.set_password(u["password"])
            db.session.add(user)
            created_users.append(user)

        db.session.commit()
        print(f"Created {len(created_users)} users.")

        print("Creating sample blog posts...")
        posts_data = [
            {
                "title": "Mastering Python 3.12: The Most Exciting Features & Performance Boosts",
                "category": "Programming",
                "tags": "python, backend, programming, performance",
                "author": created_users[0],
                "content": (
                    "Python 3.12 brings substantial performance enhancements, enhanced error diagnostics, "
                    "and a cleaner standard library. In this article, we break down what matters most for web developers.\n\n"
                    "1. More Intuitive Tracebacks and Error Messages\n"
                    "One of the biggest improvements in daily coding is how Python highlights precise syntax anomalies. "
                    "Misspelled variable names or missing colons now point directly to the offender rather than generic line numbers.\n\n"
                    "2. Faster Execution with PEP 709 (Inlined Comprehensions)\n"
                    "List, dict, and set comprehensions are now inlined instead of creating temporary frames. "
                    "In real-world benchmarks, comprehension loops execute up to two times faster.\n\n"
                    "3. Modern Typing Improvements\n"
                    "PEP 695 introduces a cleaner syntax for generic classes and functions using the `type` keyword, "
                    "reducing boilerplate typing code significantly."
                )
            },
            {
                "title": "Designing Scalable REST APIs with Flask and SQLAlchemy",
                "category": "Web Development",
                "tags": "flask, api, webdev, database, python",
                "author": created_users[0],
                "content": (
                    "Building robust web APIs requires more than just returning JSON. We must structure blueprints, "
                    "manage database migrations cleanly, and provide uniform error codes.\n\n"
                    "Why SQLite is Great for Prototyping and Local Testing\n"
                    "SQLite provides an zero-configuration, lightning fast embedded relational database. Coupled with "
                    "Flask-SQLAlchemy, models written in Python seamlessly translate to SQLite tables and queries.\n\n"
                    "Blueprints and Separation of Concerns\n"
                    "Rather than keeping all routes inside a single file, partitioning logic into auth, posts, and api blueprints "
                    "makes your codebase scalable and easy to test."
                )
            },
            {
                "title": "The Evolution of Transformer Architectures in 2025",
                "category": "AI & Data",
                "tags": "ai, machine-learning, transformers, data",
                "author": created_users[1],
                "content": (
                    "Over the past few years, transformer architectures have evolved beyond standard attention mechanisms. "
                    "State Space Models (SSMs), mixture of experts (MoE), and linear attention approximations are redefining speed.\n\n"
                    "Balancing Context Window Length and Memory Overhead\n"
                    "As modern language models expand to millions of tokens in context, KV-cache optimization is critical. "
                    "Techniques like grouped-query attention (GQA) reduce memory footprints while preserving reasoning depth."
                )
            },
            {
                "title": "Clean Typography and Visual Hierarchy in Modern Web Design",
                "category": "Design",
                "tags": "design, ui, ux, typography, css",
                "author": created_users[2],
                "content": (
                    "Great typography makes content easy to digest and creates an emotional connection with readers.\n\n"
                    "The Rule of Proportion\n"
                    "Establishing a mathematical scale for font sizes—such as a 1.25 major third scale—ensures that headers, "
                    "subtitles, and body paragraphs flow harmoniously.\n\n"
                    "Spacing and Line Heights\n"
                    "Optimal line height for continuous reading is between 1.5 and 1.8 times the font size. Give your content room to breathe!"
                )
            },
            {
                "title": "From Junior to Senior Engineer: The Shifts in Mindset That Matter",
                "category": "Career & Productivity",
                "tags": "career, mentorship, software-engineering, productivity",
                "author": created_users[3],
                "content": (
                    "Early in our development careers, we measure success by the lines of code written and tickets closed. "
                    "As we mature, true impact shifts toward simplicity, risk mitigation, and team enablement.\n\n"
                    "1. Code is a Liability, Value is an Asset\n"
                    "The best engineers often recommend writing less code. Choosing an existing library, simplifying a schema, "
                    "or avoiding premature abstractions saves hours of future maintenance.\n\n"
                    "2. Communication Over Tech Purity\n"
                    "A great architecture that no one understands is a failed architecture. Document decisions, write clear PR descriptions, "
                    "and review teammates' work with empathy."
                )
            },
            {
                "title": "Securing Web Applications Against Common Vulnerabilities",
                "category": "Technology",
                "tags": "security, csrf, owasp, auth, python",
                "author": created_users[3],
                "content": (
                    "Security should never be an afterthought. Integrating CSRF tokens, strict password hashing, and "
                    "authorization checks at every layer protects user data from day one.\n\n"
                    "Defense in Depth\n"
                    "Always validate user inputs on both client and server sides. Use password hashing mechanisms like scrypt or pbkdf2 "
                    "with adequate salt factors, and never store plaintext secrets in version control."
                )
            }
        ]

        created_posts = []
        for p in posts_data:
            post = Post(
                title=p["title"],
                category=p["category"],
                tags=p["tags"],
                content=p["content"],
                author=p["author"]
            )
            db.session.add(post)
            created_posts.append(post)

        db.session.commit()
        print(f"Created {len(created_posts)} blog posts.")

        print("Adding sample comments...")
        comments_data = [
            {
                "content": "Fantastic breakdown! The inline comprehensions in Python 3.12 made a measurable difference in our processing loops.",
                "author": created_users[1],
                "post": created_posts[0]
            },
            {
                "content": "Agreed. Also, the improved error messages have saved our team plenty of debugging time.",
                "author": created_users[3],
                "post": created_posts[0]
            },
            {
                "content": "Great architectural advice. Keeping blueprints modular makes testing endpoints isolated and straightforward.",
                "author": created_users[2],
                "post": created_posts[1]
            },
            {
                "content": "Spot on regarding communication over tech purity. Empathy in code reviews is underrated.",
                "author": created_users[0],
                "post": created_posts[4]
            }
        ]

        for c in comments_data:
            comment = Comment(
                content=c["content"],
                author=c["author"],
                post=c["post"]
            )
            db.session.add(comment)

        db.session.commit()
        print(f"Created {len(comments_data)} comments.")

    print("\n" + "=" * 60)
    print("Database seeding completed successfully!")
    print("Demo accounts available:")
    print("  1. Username: alex_dev    | Password: password123")
    print("  2. Username: sarah_ai    | Password: password123")
    print("  3. Username: elena_design| Password: password123")
    print("  4. Username: marcus_lead | Password: password123")
    print("=" * 60)
