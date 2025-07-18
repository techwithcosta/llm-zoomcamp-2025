#%%
import random

known_weather_data = {
    'berlin': 20.0
}

def get_weather(city: str) -> float:
    city = city.strip().lower()

    if city in known_weather_data:
        return known_weather_data[city]

    return round(random.uniform(-5, 35), 1)
#%%
# Question 1. Function description (1 point)

get_weather_tool = {
    "type": "function",
    "name": "get_weather",
    "description": "Get city temperature",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city for which we want to get its temperature"
            }
        },
        "required": ["city"],
        "additionalProperties": False
    }
}
#%%
def set_weather(city: str, temp: float) -> None:
    city = city.strip().lower()
    known_weather_data[city] = temp
    return 'OK'
#%%
# Question 2. Another tool description (1 point)

set_weather_tool = {
    "type": "function",
    "name": "set_weather",
    "description": "Set city temperature",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city for which we want to set its temperature"
            },
            "temp": {
                "type": "float",
                "description": "The city temperature in degrees Celsius"
            }
        },
        "required": ["city", "temp"],
        "additionalProperties": False
    }
}
#%%
# Get chat_assistant.py

# !wget https://raw.githubusercontent.com/alexeygrigorev/rag-agents-workshop/refs/heads/main/chat_assistant.py
#%%
# Install packages

# !pip install dotenv openai markdown
#%%
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv('dev.env')

AZURE_OPENAI_API_VERSION = os.environ.get('AZURE_OPENAI_API_VERSION')
AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_DEPLOYMENT = os.environ.get('AZURE_OPENAI_DEPLOYMENT')

# os.environ['AZURE_OPENAI_API_KEY'] = os.environ.get('AZURE_OPENAI_API_KEY')
# os.environ['AZURE_OPENAI_ENDPOINT'] = os.environ.get('AZURE_OPENAI_ENDPOINT')
# os.environ['AZURE_OPENAI_API_VERSION'] = os.environ.get('AZURE_OPENAI_API_VERSION')
# os.environ['AZURE_OPENAI_DEPLOYMENT'] = os.environ.get('AZURE_OPENAI_DEPLOYMENT')

# print(os.environ['AZURE_OPENAI_API_KEY'])
# print(os.environ['AZURE_OPENAI_ENDPOINT'])
# print(os.environ['AZURE_OPENAI_API_VERSION'])
# print(os.environ['AZURE_OPENAI_DEPLOYMENT'])

# Initialize Azure OpenAI client with key-based authentication
client = AzureOpenAI(
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)

# Prepare the chat prompt
messages = [
    {
        "role": "developer",
        "content": [
            {
                "type": "text",
                "text": "You are an AI assistant that helps people find information."
            }
        ]
    }
]

# Generate the completion
completion = client.chat.completions.create(
    model=AZURE_OPENAI_DEPLOYMENT,
    messages=messages,
    max_completion_tokens=100000,
    stop=None,
    stream=False
)

completion.choices[0].message.content
#%%
# Test functions

import chat_assistant

developer_prompt = """
You're a weather assistant. 
You're given a city and your task is to output its current temperature in degrees Celsius.

At the end of each response, ask the user a follow up question based on your answer.
""".strip()

# Use the known weather data if your own knowledge is not sufficient to answer.

chat_interface = chat_assistant.ChatInterface()

chat = chat_assistant.ChatAssistant(
    developer_prompt=developer_prompt,
    chat_interface=chat_interface,
    client=client
)

chat.run()
#%%
# Question 3. FastMCP version (1 point)
#%%
# Question 4. MCP Server transport (1 point)
#%%
# Question 5. MCP communication (1 point)
#%%
# Question 6. MCP Client tools (1 point)
