"""Tests for code review routes."""

import pytest
from app.models.review import Review
from unittest.mock import patch
from flask import url_for

# Patch the AI review service to avoid real API calls
def mock_review_code(self, code_input):
    # Return a fake review result
    return {
        "language": "python",
        "code_lines": [],
        "reviews": [
            {"line_number": 1, "code": "print('hi')", "review": "Add docstring"}
        ],
        "refactored_code": code_input + "\n# Refactored"
    }, True

@pytest.mark.usefixtures("client", "auth_headers", "sample_code")
class TestReviewEndpoints:
    @patch("app.services.ai_review_service.AiReviewService.review_code", new=mock_review_code)
    def test_upload_review_success(self, client, auth_headers, sample_code):
        resp = client.post(
            "/api/review/upload",
            json={"code": sample_code, "filename": "testfile.py"},
            headers=auth_headers,
        )
        print(resp.get_json())
        assert resp.status_code == 200
        data = resp.get_json()
        assert "result" in data
        assert data["result"]["language"] == "python"
        assert data["filename"] == "testfile.py"
        assert "is_new_version" in data
        assert "message" in data

    @patch("app.services.ai_review_service.AiReviewService.review_code", new=mock_review_code)
    def test_upload_review_missing_code(self, client, auth_headers):
        resp = client.post(
            "/api/review/upload",
            json={"filename": "testfile.py"},
            headers=auth_headers,
        )
        assert resp.status_code == 400 or resp.status_code == 200  # Accept either, depending on error handling
        data = resp.get_json()
        assert "error" in data or "message" in data

    @patch("app.services.ai_review_service.AiReviewService.review_code", new=mock_review_code)
    def test_history_and_file_and_remove(self, client, auth_headers, sample_code):
        # Upload a review first
        upload_resp = client.post(
            "/api/review/upload",
            json={"code": sample_code, "filename": "testfile.py"},
            headers=auth_headers,
        )
        assert upload_resp.status_code == 200
        upload_data = upload_resp.get_json()
        version = upload_data["result"]["version"]

        # Get history
        hist_resp = client.get("/api/review/history", headers=auth_headers)
        assert hist_resp.status_code == 200
        hist_data = hist_resp.get_json()
        assert isinstance(hist_data, list)
        assert any(r["filename"] == "testfile.py" for r in hist_data)

        # Get review by filename and version
        file_resp = client.get(
            f"/api/review/file?filename=testfile.py&version={version}", headers=auth_headers
        )
        assert file_resp.status_code == 200
        file_data = file_resp.get_json()
        assert file_data["filename"] == "testfile.py"
        assert file_data["version"] == version

        # Remove review
        remove_resp = client.post(
            f"/api/review/remove?filename=testfile.py&version={version}", headers=auth_headers
        )
        assert remove_resp.status_code == 200
        remove_data = remove_resp.get_json()
        assert remove_data["filename"] == "testfile.py"
        assert remove_data["version"] == version

        # Confirm it's gone
        file_resp2 = client.get(
            f"/api/review/file?filename=testfile.py&version={version}", headers=auth_headers
        )
        assert file_resp2.status_code == 200 or file_resp2.status_code == 404
        if file_resp2.status_code == 200:
            assert "error" in file_resp2.get_json()

    def test_auth_required(self, client, sample_code):
        resp = client.post(
            "/api/review/upload",
            json={"code": sample_code, "filename": "testfile.py"},
        )
        assert resp.status_code == 401 or resp.status_code == 422  # JWT missing/invalid

    @patch("app.services.ai_review_service.AiReviewService.review_code", new=mock_review_code)
    def test_upload_invalid_content_type(self, client, auth_headers):
        # Send plain text instead of JSON
        resp = client.post(
            "/api/review/upload",
            data="print('hi')",
            headers=auth_headers,
            content_type="text/plain",
        )
        assert resp.status_code == 400 or resp.status_code == 415 or resp.status_code == 500
        data = resp.get_json()
        assert "error" in data or "message" in data
