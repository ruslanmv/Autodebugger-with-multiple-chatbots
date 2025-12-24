"""
Pytest configuration and shared fixtures.

This module contains pytest fixtures that can be used across all test modules.
"""

import os
from typing import Generator

import pytest


@pytest.fixture(scope="session")
def mock_env_vars() -> Generator[None, None, None]:
    """
    Mock environment variables for testing.

    This fixture sets up test environment variables and cleans them up after tests.
    """
    original_api_key = os.environ.get("API_KEY")
    original_project_id = os.environ.get("PROJECT_ID")

    # Set test environment variables
    os.environ["API_KEY"] = "test_api_key_12345"
    os.environ["PROJECT_ID"] = "test_project_id_67890"

    yield

    # Restore original environment variables
    if original_api_key:
        os.environ["API_KEY"] = original_api_key
    else:
        os.environ.pop("API_KEY", None)

    if original_project_id:
        os.environ["PROJECT_ID"] = original_project_id
    else:
        os.environ.pop("PROJECT_ID", None)


@pytest.fixture
def sample_code() -> str:
    """
    Provide sample Python code for testing.

    Returns:
        str: A simple Python code snippet.
    """
    return "print('Hello, World!')"


@pytest.fixture
def sample_error() -> str:
    """
    Provide sample error message for testing.

    Returns:
        str: A sample Python error message.
    """
    return "NameError: name 'x' is not defined"
