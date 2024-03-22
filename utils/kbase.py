import os
from dotenv import load_dotenv
import re
import requests
import json
from tkinter import messagebox

openai_config_file_path = os.path.join("openai_config.json")

def list_openai_indexs(config_file_path):
    openai_config = read_config_file(config_file_path)
    if type(openai_config) != list:
        if openai_config["error"]:
            return openai_config
    
    indexs = []
    
    for i in  range(0, len(openai_config)):
        name = openai_config[i]["name"]
        indexs.append(name)
    
    return indexs

def make_openai_request(question: str, index_name: str) -> str:
    prompt = ""
    return prompt
def make_openai_request_with_question(question):
    """
    Makes a request to the specified API with the given question and returns the raw data, prompt, and usage.
    
    Parameters:
    - question (str): The question to be asked.
    
    Returns:
    - dict: A dictionary containing raw data, prompt, and usage if successful, else error info.
    """
    # Load environment variables from .env file
    load_dotenv()

    # API URL and keys
    BASE_URL = os.getenv("OPENAI_BASE_URL")
    SEARCH_KEY = os.getenv("SEARCH_KEY")
    OPENAI_KEY = os.getenv("OPENAI_KEY")

    # Headers for the request
    headers = {
        'Content-Type': 'application/json',
        'api-key': OPENAI_KEY
    }

    # Content and data for the request
    content = f"sen Logo Yazılım şirketinde çalışan yardımcı bir botsun, sorulara her zaman Türkçe yanıt ver. Soru: {question}"
    json_data = {
        "messages": [
            {"role": "system", "content": "Yardımsever botsun"},
            {"role": "user", "content": content}
        ],
        "temperature": 0,
        "dataSources": [
            {
                "type": "AzureCognitiveSearch",
                "parameters": {
                    "endpoint": "https://openaidemosearchservice.search.windows.net",
                    "key": SEARCH_KEY,
                    "indexName": "indexbuluterpdys"
                }
            }
        ]
    }

    # Perform the request
    response = requests.post(url=BASE_URL, headers=headers, json=json_data)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        prompt = data['choices'][0]['message']['content']
        usage = data['usage']
        prompt = clean_prompt(prompt)
        return {"raw_data": data, "prompt": prompt, "usage": usage}
    else:
        return {"error": f"Request failed! Status code: {response.status_code}, err: {response.content}"}



# A function for cleaning the [doc1] [doc2].. tags in prompt
def clean_prompt(text):
    cleaned_text = re.sub(r'\[doc\d+\]', '', text)
    return cleaned_text.strip()

# This function loads the openai_config.json file
def read_config_file(config_file_path: str):
    try:
        with open(config_file_path, mode="r", encoding="utf-8") as file:
            openai_config = json.load(file)
            return openai_config
    except Exception as err:
        error_message = f"An error occurred while reading {config_file_path}: {err}"
        print(error_message)
        return {"error": True, "err": err}
        
def make_openai_request(question: str, config_file_path: str, index_name: str) -> str:
    print(config_file_path, index_name)

    openai_config = read_config_file(config_file_path)
    if type(openai_config) != list:
        if openai_config["error"]:
            return openai_config
    selected_service = {}
    data_sources = []
    
    # Find the indexname
    for index in openai_config:  # iterate over each dictionary in the list
        # if index["dataSources"][0]["parameters"]["indexName"] == index_name:
        if index["name"] == index_name:
            selected_service = index  # assign the whole dictionary to selected_service
            data_sources = selected_service["dataSources"]
            

    # Make request
    
    # Headers for the request
    headers = {"Content-Type": "application/json", "api-key": selected_service["apiKey"]}

    # Content and data for the request
    content = u"sen Logo Yazılım şirketinde çalışan yardımcı bir botsun, sorulara her zaman Türkçe yanıt ver. Soru:" + question
    json_data = {
        "messages": [
            {"role": "system", "content": "Yardımsever botsun"},
            {"role": "user", "content": content},
        ],
        "temperature": 0,
        "dataSources": data_sources,
    }
    
    print(json.dumps(json_data, indent=4, ensure_ascii=False))  # Print JSON data in a pretty format without escaping Unicode characters

    #url = data_sources[0]["parameters"]["embeddingEndpoint"]
    url = selected_service["url"]
    # Perform the request
    response = requests.post(url=url, headers=headers, json=json_data)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        prompt = data["choices"][0]["message"]["content"]
        usage = data["usage"]
        prompt = clean_prompt(prompt)
        return {"error": False, "raw_data": data, "prompt": prompt, "usage": usage}
    else:
        error_message = f"Request failed! Status code: {response.status_code}, err: {response.content}"
        print(error_message)
        messagebox.showerror("Error", error_message)
        return {
            "error": True, "err": error_message
        }


# Just a test
def make_openai_request_test():
    config_file_path = "openai_config.json"
    question = "Logo erp nedir?"
    index_name = "logowebdataindex"

    prompt = make_openai_request(question, config_file_path, index_name)
    if type(prompt) != list:
        if not prompt["error"]:
            print(json.dumps(prompt, indent=4, ensure_ascii=False))  # Print the response JSON data in a pretty format without escaping Unicode characters
        else:
            error_message = f"An error occurred while sending openai request: {prompt['err']}"
            print(error_message)
            messagebox.showerror("Error", error_message)

