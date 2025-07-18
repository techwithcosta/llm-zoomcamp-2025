# weather_server.py

from fastmcp import FastMCP
import random

mcp = FastMCP("Demo 🚀")

known_weather_data = {
    'berlin': 20.0
}

@mcp.tool
def get_weather(city: str) -> float:
    """
    Retrieves the temperature for a specified city.

    Parameters:
        city (str): The name of the city for which to retrieve weather data.

    Returns:
        float: The temperature associated with the city.
    """
    city = city.strip().lower()

    if city in known_weather_data:
        return known_weather_data[city]

    return round(random.uniform(-5, 35), 1)

@mcp.tool
def set_weather(city: str, temp: float) -> None:
    """
    Sets the temperature for a specified city.

    Parameters:
        city (str): The name of the city for which to set the weather data.
        temp (float): The temperature to associate with the city.

    Returns:
        str: A confirmation string 'OK' indicating successful update.
    """
    city = city.strip().lower()
    known_weather_data[city] = temp
    return 'OK'

if __name__ == "__main__":
    mcp.run()


# When the server is running, send the following requests

# First, we send an initialization request -- this way, we register our client with the server:
# {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"roots": {"listChanged": true}, "sampling": {}}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}

# We should get back something like that, which is an acknowledgement of the request:
# {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":true}},"serverInfo":{"name":"Demo 🚀","version":"1.12.0"}}}

# Next, we reply back, confirming the initialization:
# {"jsonrpc": "2.0", "method": "notifications/initialized"}
# We don't expect to get anything in response

# Now we can ask for a list of available methods:
# {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}

# Output:
# {"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"get_weather","description":"Retrieves the temperature for a specified city.\n\nParameters:\n    city (str): The name of the city for which to retrieve weather data.\n\nReturns:\n    float: The temperature associated with the city.","inputSchema":{"properties":{"city":{"title":"City","type":"string"}},"required":["city"],"type":"object"},"outputSchema":{"properties":{"result":{"title":"Result","type":"number"}},"required":["result"],"title":"_WrappedResult","type":"object","x-fastmcp-wrap-result":true}},{"name":"set_weather","description":"Sets the temperature for a specified city.\n\nParameters:\n    city (str): The name of the city for which to set the weather data.\n    temp (float): The temperature to associate with the city.\n\nReturns:\n    str: A confirmation string 'OK' indicating successful update.","inputSchema":{"properties":{"city":{"title":"City","type":"string"},"temp":{"title":"Temp","type":"number"}},"required":["city","temp"],"type":"object"}}]}}

# Let's ask the temperature in Berlin:
# {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "<TODO>", "arguments": {<TODO>}}}

# Implementation:
# {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_weather", "arguments": {"city": "Berlin"}}}

# Response:
# {"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"20.0"}],"structuredContent":{"result":20.0},"isError":false}}
