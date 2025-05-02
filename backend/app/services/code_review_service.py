"""Service for managing code review operations and persistence.

This module provides functionality for creating, updating, and retrieving code reviews,
including version tracking and history management.
"""

import logging
from typing import Any, Dict, Tuple, Optional, List, NoReturn
from dataclasses import dataclass

from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import review as review_model
from app.models import user as user_model
from app.services import ai_review_service


logger = logging.getLogger(__name__)


@dataclass
class ReviewServiceError(Exception):
    """Custom exception for review service errors."""

    message: str
    code: int = 500


class CodeReviewerService:
    """Service for managing code review operations.

    This class handles:
    - Creating and updating code reviews
    - Version tracking of reviews
    - Retrieving review history
    - Managing review persistence

    Attributes:
        _db: Database session
        _reviewer: AI review service instance
    """

    def __init__(self):
        """Initialize the service with database and AI reviewer."""
        self._db = db
        self._reviewer = ai_review_service.AiReviewService()

    def create_or_update_review(
        self,
        user_id: str,
        filename: str,
        code: str,
    ) -> Tuple[Dict[str, Any], bool]:
        """Create a new code review or update existing one if the file has changed.

        Args:
            user_id: ID of the user requesting the review
            filename: Name of the file being reviewed
            code: Code content to review

        Returns:
            Tuple containing:
            - Dictionary with review results and database record ID
            - Boolean indicating if this is a new version

        Raises:
            ReviewServiceError: If database operations fail
        """
        try:
            # Calculate content hash for version tracking
            content_hash = review_model.CodeReviewHistory.calculate_hash(code)
            latest_version = self.get_latest_version(filename)

            # Return existing review if content hasn't changed
            if latest_version and latest_version.content_hash == content_hash:
                return self.get_review_by_id(latest_version.id), False

            # Get AI review for the code
            review_result, success = self._reviewer.review_code(code)
            if not success:
                raise ReviewServiceError(
                    "Failed to generate AI review for the code", 500
                )

            # Prepare new version data
            version_number = (
                (latest_version.version + 1) if latest_version else 1
            )
            parent_id = latest_version.id if latest_version else None

            # Create database records
            db_user = user_model.User.query.get(user_id)
            if not db_user:
                raise ReviewServiceError(f"User {user_id} not found", 404)

            db_review = review_model.CodeReviewHistory(
                filename=filename,
                language=review_result["language"],
                original_code=code,
                refactored_code=review_result["refactored_code"],
                content_hash=content_hash,
                version=version_number,
                parent_id=parent_id,
                user=db_user,
            )

            # Add review and its comments
            self._db.session.add(db_review)
            self._db.session.flush()

            for review in review_result["reviews"]:
                db_review_comment = review_model.Review(
                    review_history_id=db_review.id,
                    line_number=review["line_number"],
                    code=review["code"],
                    review=review["review"],
                )
                self._db.session.add(db_review_comment)

            self._db.session.commit()
            self._db.session.refresh(db_review)

            # Return complete result
            return {
                **review_result,
                "id": db_review.id,
                "created_at": db_review.created_at,
                "version": version_number,
                "has_previous_version": bool(parent_id),
            }, True

        except SQLAlchemyError as e:
            self._db.session.rollback()
            logger.error(
                f"Database error in create_or_update_review: {str(e)}"
            )
            raise ReviewServiceError("Failed to save review to database", 500)
        except Exception as e:
            self._db.session.rollback()
            logger.error(f"Error in create_or_update_review: {str(e)}")
            raise ReviewServiceError(str(e), 500)

    def get_latest_version(
        self,
        filename: str,
    ) -> Optional[review_model.CodeReviewHistory]:
        """Get the latest version of a file's review.

        Args:
            filename: Name of the file to get latest review for

        Returns:
            Latest CodeReviewHistory instance or None if not found
        """
        try:
            return (
                review_model.CodeReviewHistory.query.filter_by(
                    filename=filename
                )
                .order_by(review_model.CodeReviewHistory.version.desc())
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_latest_version: {str(e)}")
            return None

    def get_review_by_id(self, review_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific review by its ID.

        Args:
            review_id: ID of the review to retrieve

        Returns:
            Review details dictionary or None if not found
        """
        try:
            db_review = review_model.CodeReviewHistory.query.get(review_id)
            return db_review.to_dict() if db_review else None
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_review_by_id: {str(e)}")
            return None

    def get_file_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all file reviews for a specific user.

        Args:
            user_id: ID of the user to get history for

        Returns:
            List of review history dictionaries

        Raises:
            ReviewServiceError: If user not found or database error occurs
        """
        try:
            db_user = user_model.User.query.get(user_id)
            if not db_user:
                raise ReviewServiceError(f"User {user_id} not found", 404)

            reviews = (
                review_model.CodeReviewHistory.query.filter_by(
                    user_id=db_user.id
                )
                .order_by(
                    review_model.CodeReviewHistory.filename,
                    review_model.CodeReviewHistory.version.desc(),
                )
                .all()
            )
            return [review.to_dict() for review in reviews]

        except SQLAlchemyError as e:
            logger.error(f"Database error in get_file_history: {str(e)}")
            raise ReviewServiceError("Failed to retrieve review history", 500)

    def get_review_by_filename(
        self, filename: str, version: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get review history for a specific file and optional version.

        Args:
            filename: Name of the file to get review for
            version: Optional specific version number to retrieve

        Returns:
            Review details dictionary

        Raises:
            ReviewServiceError: If review not found or database error occurs
        """
        try:
            if version is None:
                review = self.get_latest_version(filename)
            else:
                review = review_model.CodeReviewHistory.query.filter_by(
                    filename=filename, version=version
                ).first()

            if not review:
                raise ReviewServiceError(
                    f"Review not found for {filename} version {version}", 404
                )

            return review.to_dict()

        except SQLAlchemyError as e:
            logger.error(f"Database error in get_review_by_filename: {str(e)}")
            raise ReviewServiceError("Failed to retrieve review", 500)

    def remove_review_by_filename_version(
        self, filename: str, version: int
    ) -> Tuple[Dict[str, Any], bool]:
        """Remove a specific version of a file review.

        Args:
            filename: Name of the file to remove review for
            version: Version number to remove

        Returns:
            Tuple containing:
            - Dictionary with removed review details
            - Boolean indicating success

        Raises:
            ReviewServiceError: If review not found or database error occurs
        """
        try:
            db_review = review_model.CodeReviewHistory.query.filter_by(
                filename=filename, version=version
            ).first()

            if not db_review:
                return {}, False

            self._db.session.delete(db_review)
            self._db.session.commit()

            return {
                "id": db_review.id,
                "filename": filename,
                "version": version,
            }, True

        except SQLAlchemyError as e:
            self._db.session.rollback()
            logger.error(f"Database error in remove_review: {str(e)}")
            raise ReviewServiceError("Failed to remove review", 500)
