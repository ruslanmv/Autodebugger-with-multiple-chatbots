"""
Utility functions for IBM WatsonX integration and code generation.

This module provides functions for authenticating with IBM Watson Machine Learning
and generating code fixes using WatsonX foundation models.

Author: Ruslan Magana
Website: ruslanmv.com
"""

import logging
import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def get_bearer(apikey: str) -> str:
    """
    Obtain a bearer token from IBM Cloud IAM using an API key.

    This function exchanges an API key for an OAuth 2.0 bearer token that can be
    used to authenticate with IBM Cloud services.

    Args:
        apikey: IBM Cloud API key for authentication.

    Returns:
        str: Bearer access token for IBM Cloud services.

    Raises:
        Exception: If token retrieval fails due to invalid credentials or network issues.

    Example:
        >>> token = get_bearer("your-api-key-here")
        >>> print(f"Token: {token[:20]}...")
    """
    form_data: Dict[str, str] = {
        "apikey": apikey,
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
    }

    logger.info("Requesting bearer token from IBM Cloud IAM")

    try:
        response = requests.post(
            "https://iam.cloud.ibm.com/oidc/token",
            data=form_data,
            timeout=30,
        )

        if response.status_code != 200:
            logger.error(
                f"Failed to retrieve token. Status code: {response.status_code}"
            )
            raise Exception(
                f"Failed to get token. Invalid status: {response.status_code}"
            )

        json_response = response.json()

        if not json_response:
            logger.error("Empty JSON response when retrieving token")
            raise Exception("Failed to get token, invalid response")

        access_token = json_response.get("access_token")

        if not access_token:
            logger.error("No access_token in response")
            raise Exception("Failed to get token, missing access_token")

        logger.info("Bearer token retrieved successfully")
        return access_token

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while retrieving token: {e}")
        raise Exception(f"Network error: {e}") from e


def _initialize_watsonx_model() -> Model:
    """
    Initialize and configure the WatsonX foundation model.

    This function sets up the IBM Watson Machine Learning model with appropriate
    parameters and credentials from environment variables.

    Returns:
        Model: Configured WatsonX foundation model instance.

    Raises:
        ValueError: If required environment variables are not set.
        Exception: If model initialization fails.

    Note:
        Required environment variables:
        - API_KEY: IBM Cloud API key
        - PROJECT_ID: WatsonX project ID
    """
    api_key = os.getenv("API_KEY")
    project_id = os.getenv("PROJECT_ID")

    if not api_key:
        raise ValueError("API_KEY environment variable is not set")

    if not project_id:
        raise ValueError("PROJECT_ID environment variable is not set")

    parameters = {
        GenParams.DECODING_METHOD: "greedy",
        GenParams.MAX_NEW_TOKENS: 1000,
        GenParams.STOP_SEQUENCES: ["\n\n\n"],
    }

    credentials = {
        "url": "https://us-south.ml.cloud.ibm.com",
        "apikey": api_key,
    }

    # Obtain bearer token
    credentials["token"] = get_bearer(api_key)

    model_id = ModelTypes.LLAMA_2_70B_CHAT

    logger.info(f"Initializing WatsonX model: {model_id}")

    try:
        llm_model = Model(
            model_id=model_id,
            params=parameters,
            credentials=credentials,
            project_id=project_id,
        )
        logger.info("WatsonX model initialized successfully")
        return llm_model

    except Exception as e:
        logger.error(f"Failed to initialize WatsonX model: {e}")
        raise


# Initialize the model at module load time
llm_model = _initialize_watsonx_model()


def generate_code(
    code: str,
    language: str = "Python",
    message_error: Optional[str] = None,
) -> str:
    """
    Generate fixed code using WatsonX foundation model.

    This function takes problematic code and an optional error message, then uses
    the WatsonX AI model to generate a corrected version of the code.

    Args:
        code: The code snippet that needs to be fixed.
        language: Programming language of the code (default: "Python").
        message_error: Optional error message to help guide the fix.

    Returns:
        str: The generated fixed code as a string.

    Raises:
        Exception: If code generation fails or the model returns an error.

    Example:
        >>> buggy_code = "print('Hello World'"
        >>> error_msg = "SyntaxError: unexpected EOF while parsing"
        >>> fixed_code = generate_code(buggy_code, "Python", error_msg)
        >>> print(fixed_code)
    """
    logger.info(f"Generating code fix for {language}")
    logger.debug(f"Input code length: {len(code)} characters")
    logger.debug(f"Error message: {message_error}")

    code_prompt = f"""You are given a code snippet in {language} that contains syntax errors and logical issues.
Your task is to fix the code and provide the corrected version as the final result.
You should not provide any explanation or additional information; only the fixed code should be included in your response."""

    if message_error:
        logger.info("Generating code fix with error context")
        inst_prompt = f"""<s>[INST] <<SYS>>
{code_prompt}
<</SYS>>
The following is input code: {code}.
[/INST]
The error is: {message_error}.
Answer only in {language} code:"""
    else:
        logger.info("Generating code fix without error context")
        inst_prompt = f"""<s>[INST] <<SYS>>
{code_prompt}
<</SYS>>
The following is input code: {code}.
[/INST] Answer only in {language} code: """

    code_prompts = [inst_prompt]

    try:
        logger.info("Sending prompt to WatsonX model")
        result = llm_model.generate(code_prompts)

        generated_code = ""
        for item in result:
            generated_code += item["results"][0]["generated_text"]

        logger.info("Code generation completed successfully")
        logger.debug(f"Generated code length: {len(generated_code)} characters")

        return generated_code.strip()

    except Exception as e:
        logger.error(f"Error during code generation: {e}")
        raise Exception(f"Failed to generate code: {e}") from e


def get_chatbot_suggestion(error: str, code: str) -> str:
    """
    Get code fix suggestion from the chatbot.

    This is a high-level wrapper function that uses the code generation
    functionality to provide a fixed version of problematic code.

    Args:
        error: The error message encountered during code execution.
        code: The code snippet that produced the error.

    Returns:
        str: Suggested fixed code.

    Example:
        >>> error = "NameError: name 'x' is not defined"
        >>> code = "print(x)"
        >>> suggestion = get_chatbot_suggestion(error, code)
    """
    logger.info("Getting chatbot suggestion for code fix")
    return generate_code(code=code, language="Python", message_error=error)
