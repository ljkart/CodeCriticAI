"""Review models definition.

This module defines the models for storing code review history and individual review
comments. It includes functionality for versioning and tracking code changes.
"""

from datetime import datetime
import hashlib
from typing import Dict
from flask import current_app
from sqlalchemy.orm import validates

from app import db


class CodeReviewHistory(db.Model):
    """Model for storing code review history and versions.

    Attributes:
        id: Unique identifier for the review history
        filename: Name of the reviewed file
        language: Programming language of the code
        original_code: Original code content
        refactored_code: Code after refactoring/changes
        content_hash: SHA-256 hash of the code for version tracking
        version: Version number of this review
        parent_id: ID of the previous version if any
        user_id: ID of the user who created this review
        created_at: Timestamp of creation
    """

    __tablename__ = "code_review_history"

    id = db.Column(db.Integer, primary_key=True, index=True)
    filename = db.Column(db.String(255), index=True, nullable=False)
    language = db.Column(db.String(50), nullable=False)
    original_code = db.Column(db.Text, nullable=False)
    refactored_code = db.Column(db.Text)
    content_hash = db.Column(db.String(64), index=True, nullable=False)
    version = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    parent_id = db.Column(
        db.Integer, db.ForeignKey("code_review_history.id"), nullable=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, index=True
    )

    user = db.relationship("User", back_populates="review_histories")
    reviews = db.relationship(
        "Review",
        back_populates="review_history",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    @validates("language")
    def validate_language(self, key, value):
        """To validate language attribute."""
        mappings = current_app.config.get("LANGUAGE_MAPPING", {})
        allowed = mappings.keys()
        print(value not in allowed)
        if value.lower() not in allowed:
            raise ValueError(f"Invalid language: {value}. Allowed: {allowed}")
        return value

    @staticmethod
    def calculate_hash(code: str) -> str:
        """Calculate SHA-256 hash of the code content.

        Args:
            code: Code content to be hashed.

        Returns:
            SHA-256 hash string of the code.
        """
        return hashlib.sha256(code.encode()).hexdigest()

    def to_dict(self) -> Dict:
        """Convert review history to dictionary format.

        Returns:
            Dictionary containing review history data and associated reviews.
        """
        return {
            "id": self.id,
            "filename": self.filename,
            "language": self.language,
            "created_at": self.created_at.isoformat(),
            "version": self.version,
            "has_previous_version": self.parent_id is not None,
            "reviews": [review.to_dict() for review in self.reviews],
            "refactored_code": self.refactored_code,
        }


class Review(db.Model):
    """Model for storing individual review comments.

    Attributes:
        id: Unique identifier for the review
        review_history_id: ID of the associated code review history
        line_number: Line number in the code being reviewed
        code: The specific code being reviewed
        review: Review comment for the code
    """

    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True, index=True)
    review_history_id = db.Column(
        db.Integer,
        db.ForeignKey("code_review_history.id"),
        nullable=False,
        index=True,
    )
    line_number = db.Column(db.Integer, nullable=False)
    code = db.Column(db.Text, nullable=False)
    review = db.Column(db.Text, nullable=False)

    review_history = db.relationship(
        "CodeReviewHistory", back_populates="reviews"
    )

    def to_dict(self) -> Dict:
        """Convert review to dictionary format.

        Returns:
            Dictionary containing review data.
        """
        return {
            "line_number": self.line_number,
            "code": self.code,
            "review": self.review,
        }

    def __repr__(self) -> str:
        """String representation of the Review model.

        Returns:
            String representation with review ID and line number.
        """
        return f"<Review {self.id} for line {self.line_number}>"
