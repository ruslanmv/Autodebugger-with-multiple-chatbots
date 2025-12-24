"""
Auto Error Debugger Assistant with WatsonX.

An AI-powered automatic code debugger using IBM WatsonX and Streamlit
for intelligent code analysis and error resolution.

Author: Ruslan Magana
Website: ruslanmv.com
License: Apache 2.0
"""

__version__ = "1.0.0"
__author__ = "Ruslan Magana"
__email__ = "contact@ruslanmv.com"
__license__ = "Apache-2.0"

from autodebugger.utils import generate_code, get_bearer, get_chatbot_suggestion

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "get_bearer",
    "generate_code",
    "get_chatbot_suggestion",
]
