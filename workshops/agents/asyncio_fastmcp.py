# asyncio_fastmcp.py

import os
import asyncio
from fastmcp import Client

# Server script name
server_script = "weather_server.py"

# Get the absolute path of the running script
script_path = os.path.dirname(os.path.realpath(__file__))

async def main():
    async with Client(f"{script_path}\\{server_script}") as mcp_client:
        tools = await mcp_client.list_tools()
        print(f"Available tools: {tools}")

if __name__ == "__main__":
    test = asyncio.run(main())


# Output:
# Available tools: [Tool(name='get_weather', title=None, description='Retrieves the temperature for a specified city.\n\nParameters:\n    city (str): The name of the city for which to retrieve weather data.\n\nReturns:\n    float: The temperature associated with the city.', inputSchema={'properties': {'city': {'title': 'City', 'type': 'string'}}, 'required': ['city'], 'type': 'object'}, outputSchema={'properties': {'result': {'title': 'Result', 'type': 'number'}}, 'required': ['result'], 'title': '_WrappedResult', 'type': 'object', 'x-fastmcp-wrap-result': True}, annotations=None, meta=None), Tool(name='set_weather', title=None, description="Sets the temperature for a specified city.\n\nParameters:\n    city (str): The name of the city for which to set the weather data.\n    temp (float): The temperature to associate with the city.\n\nReturns:\n    str: A confirmation string 'OK' indicating successful update.", inputSchema={'properties': {'city': {'title': 'City', 'type': 'string'}, 'temp': {'title': 'Temp', 'type': 'number'}}, 'required': ['city', 'temp'], 'type': 'object'}, outputSchema=None, annotations=None, meta=None)]
