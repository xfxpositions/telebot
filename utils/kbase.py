import os
from dotenv import load_dotenv
import re
import requests

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

def clean_prompt(text):
    cleaned_text = re.sub(r'\[doc\d+\]', '', text)
    return cleaned_text.strip()