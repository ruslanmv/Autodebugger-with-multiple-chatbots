import streamlit as st
import subprocess
from utils import *

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

run_option = st.selectbox("Local Run Code:", ("Yes", "No"))

if st.button("Debug and Run"):
    if run_option == "Yes":
        code = code_input
        attempt = 1
        success = False
        while success == False and attempt < 3:
            output_zone.write(f"Attempt {attempt}: Running code...")
            success, output = run_code(code)
            if success:
                output_zone.write(f"Code executed successfully.\n Output: {output}")
                st.write("Suggested code:")
                st.code(code, language='python')
                
                break
            else:
                error = output
                suggestion = get_chatbot_suggestion(error, code)  # Use your chatbot API to get the suggestion
                code = suggestion  # Update the code with the fixed version from the chatbot
                #fixed_code.write(f"Suggested fix applied:\n")
                #st.code(code, language='python')
                output_zone.write(f"Trying again with the fixed code...")
                attempt += 1
    else:
        
        output_zone.write(f"Code execution skipped.")
        error=""
        code = code_input
        suggestion = get_chatbot_suggestion(error, code)  # Use your chatbot API to get the suggestion
        code = suggestion  # Update the code with the fixed version from the chatbot
        fixed_code.write(f"Suggested fix applied:\n")
        st.write("Suggested code:")
        st.code(code, language='python')
        