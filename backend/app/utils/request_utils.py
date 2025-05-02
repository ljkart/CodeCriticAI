"""Request handling utilities.

This module provides utilities for handling HTTP requests, particularly for
extracting and validating code submissions in various formats (JSON, file upload).
"""

import logging
from dataclasses import dataclass
from typing import Optional, Tuple, Any, BinaryIO
from pathlib import Path

from flask import request, jsonify, current_app, Response
from werkzeug.datastructures import FileStorage


logger = logging.getLogger(__name__)


@dataclass
class RequestError(Exception):
    """Custom exception for request handling errors."""

    message: str
    status_code: int = 400


def create_error_response(
    message: str, status_code: int = 400
) -> Tuple[Response, int]:
    """Create a standardized error response.

    Args:
        message: Error message to return
        status_code: HTTP status code

    Returns:
        Tuple of (response, status_code)
    """
    return jsonify({"message": message}), status_code


def extract_code_from_request() -> (
    Tuple[Optional[str], Optional[str], Optional[Tuple[Response, int]]]
):
    """Extract code and filename from the request based on content type.

    The function handles both JSON requests and file uploads, validating
    the content and format of the submission.

    Returns:
        Tuple containing:
        - code: The extracted code content or None if error
        - filename: The filename or None if error
        - error_response: Tuple of (response, status_code) if error occurred, None otherwise
    """
    try:
        if request.is_json:
            return extract_code_from_json()

        if "multipart/form-data" in request.content_type:
            return extract_code_from_file()

        raise RequestError("Unsupported content type")

    except RequestError as e:
        return None, None, create_error_response(e.message, e.status_code)
    except Exception as e:
        logger.error("Error extracting code from request %s", str(e))
        return None, None, create_error_response("Internal server error", 500)


def extract_code_from_json() -> Tuple[str, str, None]:
    """Extract code and filename from JSON request.

    Expected JSON format:
    {
        "code": "source code content",
        "filename": "optional_filename.ext"
    }

    Returns:
        Tuple of (code, filename, None)

    Raises:
        RequestError: If code is missing or empty
    """
    try:
        data = request.get_json()
        if not data:
            raise RequestError("No JSON data provided")

        code = data.get("code", "").strip()
        if not code:
            raise RequestError("Code provided is empty")

        filename = data.get("filename", "unnamed_file.txt")
        return code, filename, None

    except RequestError:
        raise
    except Exception as e:
        logger.error(f"Error parsing JSON request: {str(e)}")
        raise RequestError("Invalid JSON format")


def extract_code_from_file() -> Tuple[str, str, None]:
    """Extract code and filename from file upload.

    Handles multipart/form-data file uploads, validates file type,
    and reads file content.

    Returns:
        Tuple of (code, filename, None)

    Raises:
        RequestError: If file is missing, invalid, or unreadable
    """
    try:
        if "filepath" not in request.files:
            raise RequestError("No file found to review")

        file_blob: FileStorage = request.files["filepath"]
        if not file_blob or not file_blob.filename:
            raise RequestError("Empty file submitted")

        filename = file_blob.filename
        file_extension = Path(filename).suffix[1:].lower()
        allowed_extensions = current_app.config["ALLOWED_EXTENSIONS"]

        if file_extension not in allowed_extensions:
            raise RequestError(
                f"Invalid file type. Allowed extensions: {', '.join(allowed_extensions)}"
            )

        try:
            code = read_file_in_chunks(file_blob)
            return code, filename, None
        except UnicodeDecodeError:
            raise RequestError("File could not be decoded as UTF-8 text")

    except RequestError:
        raise
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        raise RequestError("Failed to process file upload")


def read_file_in_chunks(file_obj: BinaryIO, chunk_size: int = 8192) -> str:
    """Read file content in chunks to handle large files efficiently.

    Args:
        file_obj: File-like object to read from
        chunk_size: Size of each chunk in bytes (default: 8KB)

    Returns:
        Complete file content as string

    Raises:
        UnicodeDecodeError: If file content cannot be decoded as UTF-8
        IOError: If reading the file fails

    Example:
        >>> with open('test.txt', 'rb') as f:
        ...     content = read_file_in_chunks(f)
    """
    try:
        content = []
        while True:
            chunk = file_obj.read(chunk_size)
            if not chunk:
                break
            content.append(chunk.decode("utf-8"))
        return "".join(content)

    except UnicodeDecodeError:
        raise
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        raise IOError(f"Failed to read file: {str(e)}")
