"""Tests for database models."""

import pytest
from app.models.user import User
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.review import CodeReviewHistory
from app import db
from sqlalchemy.exc import IntegrityError


class TestUserModel:
    """Test cases for User model."""

    def test_create_user(self, app):
        """Test user creation."""
        with app.app_context():
            user = User(
                username="testuser",
                password_hash=generate_password_hash("password123"),
            )
            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.username == "testuser"
            assert check_password_hash(user.password_hash, "password123")

    def test_password_hashing(self, app):
        """Test password hashing."""
        with app.app_context():
            user = User(
                username="testuser",
                password_hash=generate_password_hash("password123"),
            )
            assert check_password_hash(user.password_hash, "password123")
            assert not check_password_hash(user.password_hash, "wrongpass")


class TestReviewModel:
    """Test cases for Review model."""

    def test_create_review(self, app, test_review, sample_code):
        """Test review creation."""
        with app.app_context():
            sample_code_line = sample_code.split("\n")[2].strip()
            review = test_review
            db.session.add(review)
            db.session.commit()

            assert review.id is not None
            assert review.line_number == 2
            assert review.code == sample_code_line

    def test_review_user_relationship(self, app, test_user_id, sample_code):
        """Test review-user relationship."""
        with app.app_context():
            test_user = User.query.get(test_user_id)
            test_review_history = CodeReviewHistory(
                filename="testfile.py",
                language="python",
                original_code=sample_code,
                refactored_code=sample_code,
                content_hash=CodeReviewHistory.calculate_hash(sample_code),
                version=1,
                parent_id=1,
                user_id=test_user_id,
            )
            db.session.add(test_review_history)
            db.session.commit()

            review_user = User.query.get(test_review_history.user_id)
            test_user = User.query.get(test_user_id)
            assert review_user == test_user

    def test_review_cascade_delete(self, app, test_user_id, sample_code):
        """Test cascade deletion of reviews when user is deleted."""
        with app.app_context():
            test_review_history = CodeReviewHistory(
                filename="testfile.py",
                language="python",
                original_code=sample_code,
                refactored_code=sample_code,
                content_hash=CodeReviewHistory.calculate_hash(sample_code),
                version=1,
                parent_id=1,
                user_id=test_user_id,
            )
            db.session.add(test_review_history)
            db.session.commit()
            review_history = CodeReviewHistory.query.get(
                test_review_history.id
            )
            assert review_history is not None
            test_user = User.query.get(test_user_id)
            db.session.delete(test_user)
            db.session.commit()

            # Review should be deleted
            assert CodeReviewHistory.query.get(review_history.id) is None

    def test_review_validation(self, app, sample_code, test_user_id):
        """Test review validation."""
        with app.app_context():
            # Test invalid language
            test_user = User.query.get(test_user_id)
            with pytest.raises(ValueError):
                obj = CodeReviewHistory(
                    filename="testfile.py",
                    language="CPP",
                    original_code=sample_code,
                    refactored_code=sample_code,
                    content_hash=CodeReviewHistory.calculate_hash(sample_code),
                    version=1,
                    parent_id=1,
                    user_id=test_user_id,
                )
                db.session.add(obj)
                db.session.flush()

            # Test missing required fields
            with pytest.raises(IntegrityError):
                review = CodeReviewHistory(user_id=test_user.id)
                db.session.add(review)
                db.session.flush()


class TestModelIntegration:
    """Integration tests for models."""

    def test_user_review_workflow(self, app, sample_code):
        """Test complete user-review workflow."""
        with app.app_context():
            # Create user
            user = User(
                username="testuser",
                password_hash=generate_password_hash("password123"),
            )
            db.session.add(user)
            db.session.commit()

            assert user is not None

            # Create multiple reviews
            review = CodeReviewHistory(
                filename="testfile.py",
                language="python",
                original_code=sample_code,
                refactored_code=sample_code,
                content_hash=CodeReviewHistory.calculate_hash(sample_code),
                version=1,
                parent_id=1,
                user_id=user.id,
            )
            db.session.add(review)
            db.session.commit()

            # Verify relationships
            assert user.review_histories.count() == 1

            # Now add another version.
            updated_code = "\n".join(
                sample_code.split("\n") + ["print('Hello, World!')"]
            )
            review = CodeReviewHistory(
                filename="testfile.py",
                language="python",
                original_code=updated_code,
                refactored_code=sample_code,
                content_hash=CodeReviewHistory.calculate_hash(updated_code),
                version=2,
                parent_id=1,
                user_id=user.id,
            )
            db.session.add(review)
            db.session.commit()

            assert user.review_histories.count() == 2
            assert (
                user.review_histories.order_by(
                    CodeReviewHistory.version.desc()
                )
                .first()
                .version
                == 2
            )
            # Test getting the latest version
            latest_version = user.review_histories.order_by(
                CodeReviewHistory.version.desc()
            ).first()
            assert latest_version.version == 2
