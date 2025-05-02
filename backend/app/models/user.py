"""User model definition.

This module defines the User model for storing user account information
and managing relationships with code reviews.
"""

from typing import List
from app import db


class User(db.Model):
    """User account model.
    
    Attributes:
        id: Unique identifier for the user
        username: Unique username for authentication
        password_hash: Hashed password for security
        review_histories: List of code review histories created by this user
    """

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash = db.Column(db.String(128), nullable=False)
    review_histories = db.relationship(
        "CodeReviewHistory",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of the User model.
        
        Returns:
            str: User representation with username
        """
        return f"<User {self.username}>"

    def to_dict(self) -> dict:
        """Convert user data to dictionary format.
        
        Returns:
            dict: User data excluding sensitive information
        """
        return {
            "id": self.id,
            "username": self.username,
        }
