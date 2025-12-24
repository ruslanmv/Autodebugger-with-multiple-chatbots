"""
Unit tests for the main Streamlit application.

Tests for code execution, download link creation, and debugging functionality.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from autodebugger.app import create_download_link, run_code


class TestRunCode:
    """Test suite for the run_code function."""

    @patch("autodebugger.app.subprocess.run")
    def test_run_code_success(self, mock_run: MagicMock) -> None:
        """Test successful code execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Hello World\n"
        mock_run.return_value = mock_result

        success, output = run_code("print('Hello World')")

        assert success is True
        assert output == "Hello World\n"

    @patch("autodebugger.app.subprocess.run")
    def test_run_code_failure(self, mock_run: MagicMock) -> None:
        """Test failed code execution with error."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "NameError: name 'x' is not defined"
        mock_run.return_value = mock_result

        success, output = run_code("print(x)")

        assert success is False
        assert "NameError" in output

    @patch("autodebugger.app.subprocess.run")
    def test_run_code_timeout(self, mock_run: MagicMock) -> None:
        """Test code execution timeout."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("python", 30)

        success, output = run_code("while True: pass")

        assert success is False
        assert "timed out" in output


class TestCreateDownloadLink:
    """Test suite for the create_download_link function."""

    def test_create_download_link_basic(self) -> None:
        """Test download link creation with basic DataFrame."""
        df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})

        link = create_download_link(df, "test.csv")

        assert '<a href="data:file/csv;base64,' in link
        assert 'download="test.csv"' in link
        assert "Download CSV</a>" in link

    def test_create_download_link_empty_dataframe(self) -> None:
        """Test download link creation with empty DataFrame."""
        df = pd.DataFrame()

        link = create_download_link(df)

        assert '<a href="data:file/csv;base64,' in link
        assert 'download="log.csv"' in link

    def test_create_download_link_custom_filename(self) -> None:
        """Test download link creation with custom filename."""
        df = pd.DataFrame({"data": [1, 2, 3]})

        link = create_download_link(df, "custom_name.csv")

        assert 'download="custom_name.csv"' in link
