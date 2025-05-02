"""Tests for AI review service."""

import pytest
from unittest.mock import Mock, patch
from langchain_openai import ChatOpenAI
from app.services.ai_review_service import AiReviewService

# 1. Initialization fails without API key
def test_init_fails_without_api_key(app, monkeypatch):
    app.config["AI_API_KEY"] = None
    with app.app_context():
        with pytest.raises(ValueError):
            AiReviewService()

# 2. review_code returns empty result for blank input
def test_review_code_empty(app):
    with app.app_context():
        svc = AiReviewService()
        result, success = svc.review_code("")
        assert success is True
        assert result["language"] == ""
        assert result["reviews"] == []
        assert result["refactored_code"] == ""

# 3. review_code happy path (mock chains)
def test_review_code_happy(app):
    with app.app_context():
        with patch("app.services.ai_review_service.ChatOpenAI") as mock_llm:
            svc = AiReviewService()
            svc._language_chain = Mock()
            svc._language_chain.invoke.return_value = "Python"
            svc._review_chain = Mock()
            review_obj = Mock()
            review_obj.model_dump.return_value = {"line_number": 1, "code": "1: print('hi')", "review": "Good"}
            review_obj.line_number = 1
            svc._review_chain.invoke.return_value = Mock(reviews=[review_obj])
            svc._refactor_chain = Mock()
            svc._refactor_chain.invoke.return_value = "print('hi')\n# Refactored"
            result, success = svc.review_code("print('hi')")
            assert success is True
            assert result["language"] == "Python"
            assert result["refactored_code"].startswith("print('hi')")
            assert result["reviews"][0]["review"] == "Good"

# 4. review_code handles exceptions gracefully
def test_review_code_handles_exception(app):
    with app.app_context():
        with patch("app.services.ai_review_service.ChatOpenAI") as mock_llm:
            svc = AiReviewService()
            svc._language_chain = Mock()
            svc._language_chain.invoke.side_effect = Exception("fail")
            result, success = svc.review_code("print('hi')")
            assert success is False
            assert result["language"] == "unknown"
            assert "fail" in result["reviews"][0]["review"]
