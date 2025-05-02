"""File handling utilities."""

import logging
import os
import uuid
from pathlib import Path
from typing import Optional

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


logger = logging.getLogger(__name__)


class FileError(Exception):
    """Custom exception for file operation errors."""

    pass


def allowed_file(filename: str) -> bool:
    """Check if the file has a supported extension for code review.

    Args:
        filename: Name of the file to check

    Returns:
        True if the file extension is supported, False otherwise
    """
    try:
        if "." not in filename:
            return False

        extension = filename.rsplit(".", 1)[1].lower()
        return extension in current_app.config["ALLOWED_EXTENSIONS"]

    except Exception as e:
        logger.error(f"Error checking file extension: {str(e)}")
        return False


def save_file(file: FileStorage, filename: str) -> str:
    """Save an uploaded file securely with a unique name.

    Args:
        file: The uploaded file object
        filename: Original name of the file

    Returns:
        Path where the file has been saved

    Raises:
        FileError: If saving the file fails
    """
    try:
        # Create upload directory if it doesn't exist
        upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        unique_name = f"{uuid.uuid4()}_{secure_filename(filename)}"
        file_path = upload_dir / unique_name

        # Save file
        file.save(str(file_path))
        logger.info(f"Saved file {filename} as {unique_name}")

        return str(file_path)

    except Exception as e:
        logger.error(f"Error saving file {filename}: {str(e)}")
        raise FileError(f"Failed to save file: {str(e)}")


def read_file(filepath: str) -> str:
    """Read and return the contents of a file.

    Args:
        filepath: Path to the file to read

    Returns:
        Contents of the file as a string

    Raises:
        FileError: If reading the file fails
    """
    try:
        file_path = Path(filepath)
        if not file_path.exists():
            raise FileError(f"File not found: {filepath}")

        if not file_path.is_file():
            raise FileError(f"Not a file: {filepath}")

        with open(file_path, encoding="utf-8") as f:
            return f.read()

    except FileError:
        raise
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {str(e)}")
        raise FileError(f"Failed to read file: {str(e)}")


def delete_file(filepath: str) -> None:
    """Delete a file securely.

    Args:
        filepath: Path to the file to delete

    Raises:
        FileError: If deleting the file fails
    """
    try:
        file_path = Path(filepath)
        if not file_path.exists():
            return

        if not file_path.is_file():
            raise FileError(f"Not a file: {filepath}")

        file_path.unlink()
        logger.info(f"Deleted file {filepath}")

    except Exception as e:
        logger.error(f"Error deleting file {filepath}: {str(e)}")
        raise FileError(f"Failed to delete file: {str(e)}")
