"""
Unit tests for utility functions.

Tests for IBM WatsonX integration, bearer token retrieval,
and code generation functionality.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from autodebugger.utils import generate_code, get_bearer, get_chatbot_suggestion


class TestGetBearer:
    """Test suite for the get_bearer function."""

    @patch("autodebugger.utils.requests.post")
    def test_get_bearer_success(self, mock_post: MagicMock) -> None:
        """Test successful bearer token retrieval."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token_12345"}
        mock_post.return_value = mock_response

        token = get_bearer("test_api_key")

        assert token == "test_token_12345"
        mock_post.assert_called_once()

    @patch("autodebugger.utils.requests.post")
    def test_get_bearer_invalid_status(self, mock_post: MagicMock) -> None:
        """Test bearer token retrieval with invalid status code."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match="Failed to get token"):
            get_bearer("invalid_api_key")

    @patch("autodebugger.utils.requests.post")
    def test_get_bearer_empty_response(self, mock_post: MagicMock) -> None:
        """Test bearer token retrieval with empty JSON response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = None
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match="Failed to get token"):
            get_bearer("test_api_key")


class TestGenerateCode:
    """Test suite for the generate_code function."""

    @patch("autodebugger.utils.llm_model")
    def test_generate_code_with_error(self, mock_model: MagicMock) -> None:
        """Test code generation with an error message."""
        mock_model.generate.return_value = [
            {"results": [{"generated_text": "print('Fixed code')"}]}
        ]

        result = generate_code(
            code="print('broken code'",
            language="Python",
            message_error="SyntaxError: unexpected EOF",
        )

        assert result == "print('Fixed code')"
        mock_model.generate.assert_called_once()

    @patch("autodebugger.utils.llm_model")
    def test_generate_code_without_error(self, mock_model: MagicMock) -> None:
        """Test code generation without an error message."""
        mock_model.generate.return_value = [
            {"results": [{"generated_text": "print('Optimized code')"}]}
        ]

        result = generate_code(
            code="print('original code')",
            language="Python",
            message_error=None,
        )

        assert result == "print('Optimized code')"
        mock_model.generate.assert_called_once()

    @patch("autodebugger.utils.llm_model")
    def test_generate_code_custom_language(self, mock_model: MagicMock) -> None:
        """Test code generation with a custom programming language."""
        mock_model.generate.return_value = [
            {"results": [{"generated_text": "console.log('Fixed');"}]}
        ]

        result = generate_code(
            code="console.log('broken'",
            language="JavaScript",
            message_error="SyntaxError",
        )

        assert "console.log('Fixed');" in result


class TestGetChatbotSuggestion:
    """Test suite for the get_chatbot_suggestion function."""

    @patch("autodebugger.utils.generate_code")
    def test_get_chatbot_suggestion(self, mock_generate: MagicMock) -> None:
        """Test chatbot suggestion retrieval."""
        mock_generate.return_value = "fixed_code"

        result = get_chatbot_suggestion(
            error="NameError: name 'x' is not defined",
            code="print(x)",
        )

        assert result == "fixed_code"
        mock_generate.assert_called_once_with(
            code="print(x)",
            language="Python",
            message_error="NameError: name 'x' is not defined",
        )
