#%%
import os
import chat_assistant
import mcp_client
from mcp_client import convert_tools_list

# Server script name
server_script = "weather_server.py"

# Get the absolute path of the running script
script_path = os.path.dirname(os.path.realpath(__file__))

our_mcp_client = mcp_client.MCPClient(["python", f"{script_path}\\{server_script}"])

our_mcp_client.start_server()
our_mcp_client.initialize()
our_mcp_client.initialized()

our_mcp_client.get_tools()
our_mcp_client.call_tool('get_weather', {'city': 'Berlin'})

import json

class MCPTools:
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        self.tools = None
    
    def get_tools(self):
        if self.tools is None:
            mcp_tools = self.mcp_client.get_tools()
            self.tools = convert_tools_list(mcp_tools)
        return self.tools

    def function_call(self, tool_call_response):
        function_name = tool_call_response.name
        arguments = json.loads(tool_call_response.arguments)

        result = self.mcp_client.call_tool(function_name, arguments)

        return {
            "type": "function_call_output",
            "call_id": tool_call_response.call_id,
            "output": json.dumps(result, indent=2),
        }

our_mcp_client = mcp_client.MCPClient(["python", f"{script_path}\\{server_script}"])

our_mcp_client.start_server()
our_mcp_client.initialize()
our_mcp_client.initialized()

mcp_tools = mcp_client.MCPTools(mcp_client=our_mcp_client)


developer_prompt = """
You help users find out the weather in their cities. 
If they didn't specify a city, ask them. Make sure we always use a city.
""".strip()

chat_interface = chat_assistant.ChatInterface()

from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv(f"{script_path}\\dev.env")

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

chat = chat_assistant.ChatAssistant(
    tools=mcp_tools,
    developer_prompt=developer_prompt,
    chat_interface=chat_interface,
    client=client,
    model=AZURE_OPENAI_DEPLOYMENT
)

chat.run()
