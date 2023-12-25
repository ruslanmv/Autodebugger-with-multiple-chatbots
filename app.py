import streamlit as st
import subprocess
import pandas as pd
from utils import *
import base64

def run_code(code):
    try:
        output = subprocess.check_output(["python", "-c", code])
        return True, output.decode("utf-8")
    except subprocess.CalledProcessError as e:
        return False, e.output.decode("utf-8")

st.title("Auto Error Debugger Assistant with WatsonX")

code_input = st.text_area("Paste your code here:", height=200)
fixed_code = st.empty()
output_zone = st.empty()

max_attempts = st.slider("Select maximum number of attempts", 1, 10, 3)

run_option = st.selectbox("Local Run Code:", ("Yes", "No"))

log_data = []

if st.button("Debug and Run"):
    if run_option == "Yes":
        code = code_input
        attempt = 1
        success = False
        while success == False and attempt <= max_attempts:
            output_zone.write(f"Attempt {attempt}: Running code...")
            success, output = run_code(code)
            if success:
                output_zone.write(f"Code executed successfully.\nOutput: {output}")
                fixed_code.write("Suggested code:")
                st.markdown("### Code suggested")
                st.code(code, language='python')
                log_data.append([attempt, code_input, code, "", success])
                break
            else:
                error = output
                suggestion = get_chatbot_suggestion(error, code)  # Use your chatbot API to get the suggestion
                code = suggestion  # Update the code with the fixed version from the chatbot
                output_zone.write("Trying again with the fixed code...")
                success, output = run_code(code)
                output_zone.write(f"Code executed successfully.\nOutput: {output}")
                log_data.append([attempt, code_input, code, error, success])
                attempt += 1
    else:
        output_zone.write("Code execution skipped.")
        error = ""
        code = code_input
        suggestion = get_chatbot_suggestion(error, code)  # Use your chatbot API to get the suggestion
        code = suggestion  # Update the code with the fixed version from the chatbot
        fixed_code.write("Suggested fix applied:")
        st.markdown("### Code suggested")
        st.code(code, language='python')
        attempt = 1
        log_data.append([attempt, code_input, code, "", ""])

log_df = pd.DataFrame(log_data, columns=["Attempt", "Initial Code", "Suggested Code", "Error", "Success Test"])
log_df = log_df.reset_index(drop=True)

if len(log_data) > 0:
    st.markdown("---")
    st.markdown("## Log File")
    st.dataframe(log_df)
    st.markdown("---")
    st.markdown("### Download Log")
    csv = log_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="log.csv">Download CSV</a>'
    st.markdown(href, unsafe_allow_html=True)
