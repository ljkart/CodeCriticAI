"""Service for AI-powered code review and analysis.

This module provides functionality for automated code review using language models,
including language detection, code analysis, and refactoring suggestions.
"""

import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

from flask import current_app
from langchain_openai import ChatOpenAI

from app.utils import ai_agent_utils
from app.services import task_manager_service


logger = logging.getLogger(__name__)


@dataclass
class ReviewError(Exception):
    """Custom exception for review-related errors."""

    message: str
    code: str = ""
    line: int = 1


def format_code_with_line_numbers(code: str) -> List[ai_agent_utils.CodeLine]:
    """Format code into lines with line numbers and metadata.

    Args:
        code: Raw code string to format.

    Returns:
        List of CodeLine objects containing line number and content.
    """
    if not code:
        return []

    lines = code.splitlines()
    return [
        ai_agent_utils.CodeLine(
            line_number=i + 1, content=line, has_review=False
        )
        for i, line in enumerate(lines)
    ]


def format_code_with_line_tags(code: str) -> str:
    """Format code by prepending line numbers.

    Args:
        code: Raw code string to format.

    Returns:
        Code string with line numbers prepended to each line.
    """
    return "\n".join(
        f"{i + 1}: {line}" for i, line in enumerate(code.splitlines())
    )


def clean_refactored_code(code: str, language: str) -> str:
    """Clean up refactored code by removing markdown and language tags.

    Args:
        code: Raw refactored code that may contain markdown.
        language: Programming language of the code.

    Returns:
        Clean code string without markdown formatting.
    """
    if "```" not in code:
        return code.strip()

    # Remove markdown code block
    code = code.split("```")[1]

    # Remove language identifier if present
    if language.lower() in code.lower():
        code = code.split("\n", 1)[1]

    return code.strip()


class AiReviewService:
    """Service class for AI-powered code review and refactoring.

    This class handles the complete workflow of code review:
    1. Language detection
    2. Code analysis and review
    3. Refactoring suggestions

    Attributes:
        _api_key: OpenAI API key for authentication
        _llm: Language model instance
        _language_chain: Chain for language detection
        _review_chain: Chain for code review
        _refactor_chain: Chain for code refactoring
    """

    def __init__(self):
        """Initialize the service with required API keys and models."""
        self._api_key = current_app.config.get("AI_API_KEY")
        if not self._api_key:
            raise ValueError(
                "OpenAI API key not found. Please set the AI_API_KEY "
                "environment variable in your .env file."
            )

        try:
            # Initialize language model
            self._llm = ChatOpenAI(
                model_name=current_app.config.get("AI_MODEL", "gpt-3.5-turbo"),
                temperature=0.0,
                openai_api_key=self._api_key,
            )

            # Initialize processing chains
            self._language_chain = (
                ai_agent_utils.create_language_detection_chain(self._llm)
            )
            self._review_chain = ai_agent_utils.create_code_review_chain(
                self._llm
            )
            self._refactor_chain = ai_agent_utils.create_code_refactor_chain(
                self._llm
            )

        except Exception as e:
            logger.error(f"Failed to initialize AI service: {str(e)}")
            raise

    def review_code(self, code_input: str) -> Tuple[Dict[str, Any], bool]:
        """Review code, detect language, and provide refactoring suggestions.

        Args:
            code_input: The code to review.

        Returns:
            Tuple containing:
            - Dictionary with review results (language, code lines, reviews, refactored code)
            - Boolean indicating success status

        Raises:
            ReviewError: If an error occurs during the review process.
        """
        if not code_input.strip():
            return {
                "language": "",
                "code_lines": [],
                "reviews": [],
                "refactored_code": "",
            }, True

        try:
            # Step 1: Detect language
            logger.info("Detecting programming language...")
            language = self._language_chain.invoke(
                {"code": code_input}
            ).strip()
            logger.info(f"Detected language: {language}")

            # Step 2: Review code
            logger.info("Analyzing code for review...")
            review_result = self._review_chain.invoke(
                {
                    "code": format_code_with_line_tags(code_input),
                    "language": language,
                }
            )

            # Step 3: Process review results
            code_lines = format_code_with_line_numbers(code_input)
            reviews = []

            for review_obj in review_result.reviews:
                review_dict = review_obj.model_dump()
                reviews.append(review_dict)

                # Mark lines that have reviews
                if 0 < review_obj.line_number <= len(code_lines):
                    code_lines[review_obj.line_number - 1].has_review = True

            # Step 4: Generate refactoring suggestions
            logger.info("Generating refactoring suggestions...")
            reviews_text = "\n".join(
                f"- {r.review}" for r in review_result.reviews
            )

            refactored_code = self._refactor_chain.invoke(
                {
                    "code": code_input,
                    "language": language,
                    "reviews": reviews_text,
                }
            )

            # Clean up refactored code
            refactored_code = clean_refactored_code(refactored_code, language)

            # Prepare final result
            result = ai_agent_utils.CodeReviewResult(
                language=language,
                code_lines=code_lines,
                reviews=reviews,
                refactored_code=refactored_code,
            )

            return result.model_dump(), True

        except Exception as e:
            logger.error(f"Error during code review: {str(e)}")
            error_review = {
                "code": f"1: {code_input.splitlines()[0] if code_input else ''}",
                "review": str(e),
                "line_number": 1,
            }

            return {
                "language": "unknown",
                "code_lines": format_code_with_line_numbers(code_input),
                "reviews": [error_review],
                "refactored_code": code_input,
            }, False
