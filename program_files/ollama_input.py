from ollama import chat
from ollama import ChatResponse
import json
import time

def ask_sys_desc():
    """
        Asks user for a system description and uses an Ollama model to translate 
        that description to JSON. 
    """
    sys_desc = input("Input your system description:\n")
    response: ChatResponse = chat(model="nlip-test-model", messages=[
        {
            'role': 'user',
            'content': sys_desc
        }
    ])
    clean_output = response['message']['content'].replace("```json", "").replace("```", "").strip()
    data = clean_output.replace("NULL", "null")
    data = json.loads(data)
    json_file_path = "./data/system-description/" + str(time.strftime('%Y-%m-%d', time.localtime()) + ".json")
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=2)
    return response