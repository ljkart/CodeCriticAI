"""Test configuration and shared fixtures.

This module contains shared fixtures and configuration for all tests.
"""

import os
import pytest
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from datetime import timedelta

from app import create_app
from app.models.user import User
from app.models.review import CodeReviewHistory, Review
from app import db


@pytest.fixture
def app():
    """Create and configure a test Flask application instance."""
    # Use test configuration
    os.environ["FLASK_ENV"] = "testing"

    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "test-secret-key",
            "JWT_ACCESS_TOKEN_EXPIRES": timedelta(hours=1),
            "AI_API_KEY": "test",
        }
    )

    # Create tables in test database
    with app.app_context():
        db.create_all()

    yield app

    # Clean up
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def test_user_id(app):
    """Create a test user."""
    hashed_pw = generate_password_hash("password123")
    with app.app_context():
        user = User(username="testuser", password_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def auth_headers(app, test_user_id):
    """Create authentication headers with JWT token."""
    with app.app_context():
        db_test_user = User.query.get(test_user_id)
        access_token = create_access_token(identity=str(db_test_user.id))
        return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_review(sample_code):
    """Sample code review."""
    sample_code_line = sample_code.split("\n")[2]
    return Review(
        review_history_id=1,
        line_number=2,
        code=sample_code_line,
        review="test review",
    )


@pytest.fixture
def sample_code():
    """Sample code for test suite."""
    return """
    import os

    def fn(a, b):
        # This function adds two numbers and prints the result
        c = a + b
        print("Result is: " + str(c))
        return c

    def makefolder(path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except Exception as e:
                print("Error creating directory: %s" % (str(e)))

    class calc:
        def __init__(self, val):
            self.val = val

        def mul(self, x):
            return self.val * x

        def div(self, x):
            if x == 0:
                print("Can't divide by zero")
                return None
            return self.val / x

    def main():
        f = fn(3, 5)
        makefolder("data/output")
        c = calc(10)
        print("Multiplication:", c.mul(2))
        print("Division:", c.div(0))

    if __name__ == '__main__':
        main()
    """
