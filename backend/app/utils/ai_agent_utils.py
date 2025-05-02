"""AI code review utilities using LangChain.

This module provides utilities for AI-powered code review using LangChain, including:
- Language detection
- Code review and analysis
- Code refactoring suggestions

"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.schema.runnable import Runnable
from langchain.schema import StrOutputParser
from langchain.schema.output_parser import OutputParserException
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, ValidationError


logger = logging.getLogger(__name__)


@dataclass
class AIReviewError(Exception):
    """Custom exception for AI review errors."""

    message: str
    details: Optional[Dict[str, Any]] = None


class CodeLine(BaseModel):
    """Model representing a single line of code with metadata.

    Attributes:
        line_number: Line number in the source code
        content: Actual code content
        has_review: Whether this line has review comments
    """

    line_number: int = Field(description="Line number in the source code")
    content: str = Field(description="Actual code content")
    has_review: bool = Field(
        description="Whether this line has review comments", default=False
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "line_number": 1,
                "content": "def hello_world():",
                "has_review": True,
            }
        }


class CodeReview(BaseModel):
    """Model for individual code review comments.

    Attributes:
        code: Code snippet being reviewed
        review: Review comment explaining issues/improvements
        line_number: Line number in the source code
    """

    code: str = Field(
        description="Code snippet being reviewed, including line number"
    )
    review: str = Field(
        description="Clear, actionable explanation of issues or improvements"
    )
    line_number: int = Field(description="Line number in the source code")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "code": "1: def hello_world():",
                "review": "Add function docstring to improve documentation",
                "line_number": 1,
            }
        }


class CodeReviewList(BaseModel):
    """Container model for multiple code reviews.

    Attributes:
        reviews: List of individual code reviews
    """

    reviews: List[CodeReview] = Field(
        description="List of code review comments"
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "reviews": [
                    {
                        "code": "1: def hello_world():",
                        "review": "Add function docstring",
                        "line_number": 1,
                    }
                ]
            }
        }


class CodeReviewResult(BaseModel):
    """Complete code review result including analysis and refactoring.

    Attributes:
        language: Detected programming language
        code_lines: Original code with line metadata
        reviews: List of review comments
        refactored_code: Improved code based on reviews
    """

    language: str = Field(description="Detected programming language")
    code_lines: List[CodeLine] = Field(
        description="Original code lines with metadata"
    )
    reviews: List[Dict[str, Any]] = Field(
        description="List of review comments"
    )
    refactored_code: str = Field(
        description="Improved code based on review comments"
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "language": "Python",
                "code_lines": [
                    {
                        "line_number": 1,
                        "content": "def hello_world():",
                        "has_review": True,
                    }
                ],
                "reviews": [
                    {
                        "code": "1: def hello_world():",
                        "review": "Add function docstring",
                        "line_number": 1,
                    }
                ],
                "refactored_code": 'def hello_world():\n    """Say hello to the world."""',
            }
        }


def create_language_detection_chain(llm: ChatOpenAI) -> Runnable:
    """Create a chain for detecting programming language from code.

    Args:
        llm: Language model instance to use

    Returns:
        Chain that takes code input and returns language name

    Example:
        >>> llm = ChatOpenAI()
        >>> chain = create_language_detection_chain(llm)
        >>> chain.invoke({"code": "def hello(): pass"})
        'Python'
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a programming language detection expert."),
            (
                "human",
                "Identify the programming language from the following code.\n"
                "Respond with ONLY the name of the language. No other text.\n"
                "```\n{code}\n```",
            ),
        ]
    )
    return prompt | llm | StrOutputParser()


def create_code_review_chain(llm: ChatOpenAI) -> Runnable:
    """Create a chain for performing code review and analysis.

    Args:
        llm: Language model instance to use

    Returns:
        Chain that takes code and returns structured review comments

    Example:
        >>> llm = ChatOpenAI()
        >>> chain = create_code_review_chain(llm)
        >>> result = chain.invoke({
        ...     "code": "def hello(): pass",
        ...     "language": "Python"
        ... })
    """
    base_parser = PydanticOutputParser(pydantic_object=CodeReviewList)
    fixing_parser = OutputFixingParser.from_llm(parser=base_parser, llm=llm)

    template = """
    You are a senior software engineer conducting a code review for {language} code.
    Focus on:
    - Code quality and best practices
    - Performance and efficiency
    - Security concerns
    - Documentation and readability
    - Error handling

    Review this code and provide specific, actionable feedback:
    ```{language}
    {code}
    ```

    Provide output in this exact JSON format:
    {{
      "reviews": [
        {{
            "code": "<line_number>: <code_snippet>",
            "review": "<clear_actionable_feedback>",
            "line_number": <number>
        }}
      ]
    }}

    Guidelines:
    - Be specific and actionable
    - Focus on important issues
    - Explain why changes are needed
    - Suggest how to fix issues
    - Use proper JSON format
    - No markdown or extra text

    {format_instructions}
    """

    prompt = PromptTemplate(
        template=template,
        input_variables=["code", "language"],
        partial_variables={
            "format_instructions": base_parser.get_format_instructions()
        },
    )

    return prompt | llm | fixing_parser


def create_code_refactor_chain(llm: ChatOpenAI) -> Runnable:
    """Create a chain for generating refactored code based on reviews.

    Args:
        llm: Language model instance to use

    Returns:
        Chain that takes code and reviews and returns improved code

    Example:
        >>> llm = ChatOpenAI()
        >>> chain = create_code_refactor_chain(llm)
        >>> result = chain.invoke({
        ...     "code": "def hello(): pass",
        ...     "language": "Python",
        ...     "reviews": "- Add function docstring"
        ... })
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a senior software engineer specializing in code improvement.\n"
                "Refactor the code based on the review feedback, focusing on:\n"
                "- Implementing all suggested improvements\n"
                "- Maintaining code functionality\n"
                "- Following language best practices\n"
                "- Improving readability and maintainability\n"
                "Return ONLY the refactored code in a code block.",
            ),
            (
                "human",
                "Refactor this {language} code based on these reviews:\n\n"
                "Original Code:\n```{language}\n{code}\n```\n\n"
                "Review Points:\n{reviews}\n\n"
                "Return the refactored code in a ```{language}``` block.",
            ),
        ]
    )
    return prompt | llm | StrOutputParser()


def safe_parse_review_output(output: str) -> CodeReviewList:
    """Safely parse model output into structured review format.

    Args:
        output: Raw output from the language model

    Returns:
        Structured CodeReviewList object

    Raises:
        OutputParserException: If parsing fails

    Example:
        >>> output = '{"reviews": [{"code": "1: def hello():", "review": "Add docstring", "line_number": 1}]}'
        >>> result = safe_parse_review_output(output)
        >>> len(result.reviews)
        1
    """
    try:
        # First try direct JSON validation
        return CodeReviewList.model_validate_json(output)
    except ValidationError as e:
        logger.warning(f"Initial parsing failed: {str(e)}")
        try:
            # Try cleaning up common formatting issues
            cleaned = (
                output.strip()
                .replace("```json", "")
                .replace("```", "")
                .replace("\n\n", "\n")
            )
            return CodeReviewList.model_validate_json(cleaned)
        except Exception as inner_e:
            logger.error(f"Failed to parse review output: {str(inner_e)}")
            raise OutputParserException(
                f"Failed to parse model output: {str(inner_e)}"
            ) from inner_e
