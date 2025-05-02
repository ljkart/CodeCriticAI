"""
Blueprint for handling code review functionality.
Provides endpoints for uploading code for review and retrieving review history.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import code_review_service, task_manager_service
from app.utils import request_utils

review_bp = Blueprint("review_bp", __name__)


@review_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload():
    """
    Handle code upload for review.

    Accepts code either as JSON payload or as a file upload.
    Runs code review and stores the results in the database.

    Returns:
        JSON response with review results and status code
    """
    user_id = int(get_jwt_identity())

    # Extract code and filename based on content type
    code, filename, error_response = request_utils.extract_code_from_request()

    if error_response:
        return error_response
    try:
        service = code_review_service.CodeReviewerService()
        print("review started")

        result, is_new_version = service.create_or_update_review(
            user_id, filename, code
        )
        return jsonify(
            {
                "result": result,
                "is_new_version": is_new_version,
                "filename": filename,
                "message": (
                    "New version created"
                    if is_new_version
                    else "Using existing version (no changes detected)"
                ),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@review_bp.route("/history", methods=["GET"])
@jwt_required()
def get_file_history():
    """
    Retrieve review history for the authenticated user.

    Returns:
        JSON response with list of previous reviews
    """
    user_id = get_jwt_identity()
    service = code_review_service.CodeReviewerService()
    reviews = service.get_file_history(user_id)
    return (
        jsonify(reviews),
        200,
    )


@review_bp.route("/file", methods=["GET"])
@jwt_required()
def get_review_by_filename():
    """
    Get review of the given file and version.
    If version is not provided, returns the latest version.
    """
    filename = request.args.get("filename")
    version = request.args.get("version", type=int)

    if not filename or not version:
        return (
            jsonify({"error": "Both 'filename' and 'version' are required."}),
            400,
        )
    service = code_review_service.CodeReviewerService()
    try:
        file_review = service.get_review_by_filename(filename, version)
    except code_review_service.ReviewServiceError as e:
        return jsonify({"error": str(e.message)}), e.code
    if not file_review:
        return jsonify({"error": f"No reviews found for file: {filename}"})

    return jsonify(file_review), 200


@review_bp.route("/remove", methods=["POST"])
@jwt_required()
def remove_review():
    """
    Get review of the given file and version.
    If version is not provided, returns the latest version.
    """
    filename = request.args.get("filename")
    version = request.args.get("version", type=int)

    if not filename or not version:
        return (
            jsonify({"error": "Both 'filename' and 'version' are required."}),
            400,
        )
    service = code_review_service.CodeReviewerService()
    db_review, stat = service.remove_review_by_filename_version(
        filename, version
    )
    if not stat:
        return (
            jsonify(
                {
                    "error": f"No review found for `{filename}` with version `{version}`"
                }
            ),
            404,
        )

    return (
        jsonify(db_review),
        200,
    )
