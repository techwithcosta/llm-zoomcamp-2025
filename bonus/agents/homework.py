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
    "description": "Get city temperature in Celsius degrees from weather database",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city for which we want to get the temperature"
            }
        },
        "required": ["city"],
        "additionalProperties": False
    }
}

print("city")
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
    "description": "Add city temperature to weather database",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city for which we want to add the temperature"
            },
            "temp": {
                "type": "number",
                "description": "The city temperature in Celsius degrees"
            }
        },
        "required": ["city", "temp"],
        "additionalProperties": False
    }
}

print(set_weather_tool)
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

# Initialize Azure OpenAI client with key-based authentication
client = AzureOpenAI(
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)
#%%
# Test functions

import chat_assistant

tools = chat_assistant.Tools()
tools.add_tool(get_weather, get_weather_tool)
tools.add_tool(set_weather, set_weather_tool)

tools.get_tools()

developer_prompt = """
You're a weather assistant.
You have access to a database with current city temperatures in Celsius degrees.
You can also add new temperatures to the database if the user agrees.
""".strip()

chat_interface = chat_assistant.ChatInterface()

chat = chat_assistant.ChatAssistant(
    tools=tools,
    developer_prompt=developer_prompt,
    chat_interface=chat_interface,
    client=client,
    model=AZURE_OPENAI_DEPLOYMENT
)

chat.run()
#%%
# Question 3. FastMCP version (1 point)

# !pip install fastmcp

import fastmcp
print(fastmcp.__version__)
#%%
# Question 4. MCP Server transport (1 point)
#%%
# Question 5. MCP communication (1 point)
#%%
# Question 6. MCP Client tools (1 point)
