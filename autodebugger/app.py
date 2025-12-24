"""
Auto Error Debugger Assistant - Main Streamlit Application.

This module implements a Streamlit web application that automatically debugs
Python code using IBM WatsonX AI. It executes user-provided code, captures
errors, and uses AI to suggest fixes iteratively.

Author: Ruslan Magana
Website: ruslanmv.com
"""

import base64
import logging
import subprocess
from typing import List, Tuple

import pandas as pd
import streamlit as st

from autodebugger.utils import get_chatbot_suggestion

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_code(code: str) -> Tuple[bool, str]:
    """
    Execute Python code and capture the output or error.

    This function runs the provided Python code in a subprocess and returns
    whether it executed successfully along with the output or error message.

    Args:
        code: Python code string to execute.

    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True if execution was successful, False otherwise.
            - str: Standard output if successful, error message if failed.

    Example:
        >>> success, output = run_code("print('Hello World')")
        >>> print(f"Success: {success}, Output: {output}")
        Success: True, Output: Hello World
    """
    logger.info("Executing code in subprocess")

    try:
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout for safety
        )

        if result.returncode == 0:
            logger.info("Code executed successfully")
            return True, result.stdout
        else:
            logger.warning(f"Code execution failed with error: {result.stderr}")
            return False, result.stderr

    except subprocess.TimeoutExpired:
        error_msg = "Code execution timed out (30 seconds)"
        logger.error(error_msg)
        return False, error_msg

    except Exception as e:
        error_msg = f"Unexpected error during code execution: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def create_download_link(df: pd.DataFrame, filename: str = "log.csv") -> str:
    """
    Create an HTML download link for a DataFrame as CSV.

    Args:
        df: Pandas DataFrame to convert to CSV.
        filename: Name for the downloaded file (default: "log.csv").

    Returns:
        str: HTML anchor tag with base64-encoded CSV data.

    Example:
        >>> df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        >>> link = create_download_link(df)
    """
    csv_data = df.to_csv(index=False)
    b64_encoded = base64.b64encode(csv_data.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64_encoded}" download="{filename}">Download CSV</a>'
    return href


def display_log_data(log_data: List[List]) -> None:
    """
    Display execution log data in a formatted table with download option.

    Args:
        log_data: List of log entries, where each entry is a list containing:
            [attempt_number, initial_code, suggested_code, error, success_status]

    Returns:
        None
    """
    if not log_data:
        return

    log_df = pd.DataFrame(
        log_data,
        columns=["Attempt", "Initial Code", "Suggested Code", "Error", "Success Test"],
    )
    log_df = log_df.reset_index(drop=True)

    st.markdown("---")
    st.markdown("## 📊 Execution Log")
    st.dataframe(log_df, use_container_width=True)

    st.markdown("---")
    st.markdown("### 💾 Download Log")
    download_link = create_download_link(log_df, "autodebugger_log.csv")
    st.markdown(download_link, unsafe_allow_html=True)


def debug_and_run_code(
    code_input: str,
    max_attempts: int,
    run_option: str,
    fixed_code_placeholder: st.delta_generator.DeltaGenerator,
    output_zone_placeholder: st.delta_generator.DeltaGenerator,
) -> List[List]:
    """
    Debug and run code with automatic error correction.

    This function attempts to execute the provided code, and if errors occur,
    uses AI to suggest fixes and retries execution up to max_attempts times.

    Args:
        code_input: Original Python code provided by the user.
        max_attempts: Maximum number of debugging attempts.
        run_option: Whether to run code locally ("Yes") or just suggest fixes ("No").
        fixed_code_placeholder: Streamlit placeholder for displaying suggested code.
        output_zone_placeholder: Streamlit placeholder for displaying execution output.

    Returns:
        List[List]: Log data containing attempt history with codes, errors, and results.
    """
    log_data: List[List] = []

    if run_option == "Yes":
        logger.info(f"Starting code debugging with max {max_attempts} attempts")
        code = code_input
        attempt = 1
        success = False
        error = ""

        while not success and attempt <= max_attempts:
            output_zone_placeholder.write(f"🔄 Attempt {attempt}: Running code...")
            success, output = run_code(code)

            if success:
                output_zone_placeholder.success(
                    f"✅ Code executed successfully!\n\n**Output:**\n```\n{output}\n```"
                )
                fixed_code_placeholder.write("**Suggested code:**")
                st.markdown("### 💡 Final Working Code")
                st.code(code, language="python")
                log_data.append([attempt, code_input, code, "", success])
                logger.info(f"Code succeeded on attempt {attempt}")
                break
            else:
                error = output
                logger.info(f"Attempt {attempt} failed, requesting AI fix")
                output_zone_placeholder.warning(f"❌ Error encountered:\n```\n{error}\n```")

                with st.spinner("🤖 AI is analyzing and fixing the code..."):
                    suggestion = get_chatbot_suggestion(error, code)

                code = suggestion
                output_zone_placeholder.info("🔄 Trying again with the fixed code...")

                success, output = run_code(code)

                if success:
                    output_zone_placeholder.success(
                        f"✅ Code executed successfully!\n\n**Output:**\n```\n{output}\n```"
                    )
                else:
                    output_zone_placeholder.warning(
                        f"⚠️ Still has errors:\n```\n{output}\n```"
                    )

                fixed_code_placeholder.write("**Suggested code:**")
                st.markdown(f"### 💡 Attempt {attempt}")
                st.code(code, language="python")

                log_data.append([attempt, code_input, code, error, success])
                attempt += 1

        if not success:
            output_zone_placeholder.error(
                f"❌ Failed to fix code after {max_attempts} attempts. Please review manually."
            )
            logger.warning(f"Code debugging failed after {max_attempts} attempts")

    else:
        # Skip execution, just get AI suggestion
        logger.info("Skipping execution, requesting AI code review")
        output_zone_placeholder.info("⏭️ Code execution skipped.")

        with st.spinner("🤖 AI is analyzing and optimizing your code..."):
            code = code_input
            error = ""
            suggestion = get_chatbot_suggestion(error, code)
            code = suggestion

        fixed_code_placeholder.write("**Suggested fix applied:**")
        st.markdown("### 💡 AI-Optimized Code")
        st.code(code, language="python")

        log_data.append([1, code_input, code, "", "Not Executed"])

    return log_data


def main() -> None:
    """
    Main entry point for the Streamlit application.

    This function sets up the Streamlit UI and handles user interactions
    for the Auto Error Debugger Assistant.
    """
    # Page configuration
    st.set_page_config(
        page_title="Auto Error Debugger Assistant",
        page_icon="🐛",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Title and description
    st.title("🐛 Auto Error Debugger Assistant with WatsonX")
    st.markdown(
        """
        **AI-powered code debugging assistant** that automatically fixes Python code errors
        using IBM WatsonX. Simply paste your code and let AI handle the debugging!
        """
    )

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.markdown("---")

        max_attempts = st.slider(
            "Maximum Debug Attempts",
            min_value=1,
            max_value=10,
            value=3,
            help="Number of times to attempt fixing the code",
        )

        run_option = st.selectbox(
            "Execute Code Locally",
            options=("Yes", "No"),
            help="Choose 'Yes' to run and debug, 'No' for code review only",
        )

        st.markdown("---")
        st.markdown(
            """
            ### 📖 How it works:
            1. Paste your Python code
            2. Set maximum attempts
            3. Choose execution mode
            4. Click "Debug and Run"
            5. AI will fix errors iteratively

            ### 👨‍💻 Author
            **Ruslan Magana**
            - Website: [ruslanmv.com](https://ruslanmv.com)

            ### 📜 License
            Apache 2.0
            """
        )

    # Main content area
    code_input = st.text_area(
        "📝 Paste your Python code here:",
        height=300,
        placeholder="# Enter your Python code here\nprint('Hello, World!')",
    )

    # Placeholders for dynamic content
    fixed_code_placeholder = st.empty()
    output_zone_placeholder = st.empty()

    # Debug button
    if st.button("🚀 Debug and Run", type="primary"):
        if not code_input.strip():
            st.error("⚠️ Please enter some code to debug!")
            logger.warning("Empty code submitted")
            return

        logger.info("Starting debug process")

        log_data = debug_and_run_code(
            code_input,
            max_attempts,
            run_option,
            fixed_code_placeholder,
            output_zone_placeholder,
        )

        # Display log data
        display_log_data(log_data)

        logger.info("Debug process completed")


if __name__ == "__main__":
    main()
