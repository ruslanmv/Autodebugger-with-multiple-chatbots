import os
import logging
import requests
from dotenv import load_dotenv
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes

load_dotenv()
def getBearer(apikey):
    form = {
        'apikey': apikey,
        'grant_type': "urn:ibm:params:oauth:grant-type:apikey"
    }
    logging.info("About to create bearer")
    response = requests.post(
        "https://iam.cloud.ibm.com/oidc/token",
        data=form
    )
    if response.status_code != 200:
        logging.error("Bad response code retrieving token")
        raise Exception("Failed to get token, invalid status")
    json = response.json()
    if not json:
        logging.error("Invalid/no JSON retrieving token")
        raise Exception("Failed to get token, invalid response")
    logging.info("Bearer retrieved")
    return json.get("access_token")


load_dotenv()
parameters = {
    GenParams.DECODING_METHOD: "greedy",
    GenParams.MAX_NEW_TOKENS: 1000,
    GenParams.STOP_SEQUENCES: ["\n\n\n"]
}
project_id = os.getenv("PROJECT_ID", None)
credentials = {
    #"url": "https://eu-de.ml.cloud.ibm.com",
    "url": "https://us-south.ml.cloud.ibm.com",
    "apikey": os.getenv("API_KEY", None)
}
credentials["token"] = getBearer(credentials["apikey"])
model_id = ModelTypes.LLAMA_2_70B_CHAT
# Initialize the Watsonx foundation model
llm_model = Model(
    model_id=model_id,
    params=parameters,
    credentials=credentials,
    project_id=project_id
)


def generate_code(code, language):
    code_prompts = []
    code_prompt = f"""You are really good at debugging in {language} and fixing {language} code. The result is only the code. 
    """
    inst_prompt = f"""<s>[INST] <<SYS>> 
        {code_prompt}
        <</SYS>> 
        Print a fixed code in {language} from the following input code: {code}
        [/INST]"""
    code_prompts.append(inst_prompt)

    logging.info("Sending prompt for code")

    result = llm_model.generate(
        code_prompts
    )

    code = ""
    for item in result:
        code += item['results'][0]['generated_text']

    logging.info("Obtained result")
    return code

def get_chatbot_suggestion(error, code):
    # Generate code fix using CodeGenerator
    generated_code = generate_code(code, "Python")
    # Append the generated code to the suggestion
    suggestion = f"\n\nGenerated Code Fix:\n{generated_code}\n"
    return suggestion