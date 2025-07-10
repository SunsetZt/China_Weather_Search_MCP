import sqlite3
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from api import get_forecast_api

# Create an MCP server
mcp = FastMCP("China Weather")

@mcp.tool(
    name="get_grid_location",
    description="获取中国气象局API所需的网格坐标(nx, ny)。根据用户输入的省/市/区信息，在数据库中查找并返回相应的气象网格坐标。这是调用气象局API以获取准确坐标值所必需的工具。"
)
def get_grid_location(province: str, city: str, district: str) -> str:
    """Get grid location(nx, ny) for China Weather
    
    Args:
        province: Province Name (e.g. 北京市)
        city: City Name (e.g. 朝阳区)
        district: District Name (e.g. 三里屯街道)
    """
    try:
        # Connect to SQLite database
        db_path = Path(__file__).parent.parent / "data" / "weather_grid.db"
        
        if not db_path.exists():
            return f"Error: Database not found at {db_path}"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query the database for the grid coordinates
        query = """
        SELECT province, city, district, grid_x, grid_y 
        FROM weather_grid 
        WHERE province LIKE ? AND city LIKE ? AND district LIKE ?
        """
        cursor.execute(query, (f"%{province}%", f"%{city}%", f"%{district}%"))
        result = cursor.fetchone()
        
        if not result:
            return f"No location found for Province: {province}, City: {city}, District: {district}"
        
        province, city, district, nx, ny = result
        
        # Close the connection
        conn.close()
        
        # Return formatted string
        return f"Province(省): {province}, City(市): {city}, District(区): {district}, Nx: {nx}, Ny: {ny}"
    
    except Exception as e:
        return f"Error retrieving grid location: {str(e)}"


@mcp.tool(
    name="get_forecast",
    description="调用中国气象局的短期预报API，提供特定地区的天气预报信息。根据用户输入的地区信息和网格坐标，查询当前时间点的气象信息。该工具包含温度、降水量、天空状况、湿度、风向、风速等详细气象信息，并提供6小时内的短期预报。"
)
async def get_forecast(province: str, city: str, district: str, nx: int, ny: int) -> str:
    """Get weather forecast for a location.
    
    Args:
        province: Province Name (e.g. 北京市)
        city: City Name (e.g. 朝阳区)
        district: District Name (e.g. 三里屯街道)
        nx: Grid X coordinate
        ny: Grid Y coordinate
    """
    return await get_forecast_api(province, city, district, nx, ny)


@mcp.resource(
    uri="weather://instructions",
    name="China Weather Service Instructions", 
    description="提供关于如何使用中国气象服务工具的详细指南。此资源包括工具使用方法、工作流程、响应格式等所有必要的信息，以便LLM能够有效地利用天气工具。"
)
def get_weather_instructions() -> str:
    """Resource that provides detailed instructions on how to use the weather service tools."""
    return """
    # China Weather Service Instructions
    
    This service provides tools to get weather information for locations in China.
    
    ## Available Tools
    
    1. `get_grid_location(province, city, district)` - Get grid coordinates (nx, ny) for a location
      - Example: get_grid_location(province="北京市", city="朝阳区", district="三里屯街道")
    
    2. `get_forecast(province, city, district, nx, ny)` - Get weather forecast for a location
      - Example: get_forecast(province="北京市", city="朝阳区", district="三里屯街道", nx=61, ny=125)
    
    ## Workflow
    
    1. First, use `get_grid_location` to obtain the grid coordinates (nx, ny) for your location
    2. Then, use those coordinates with `get_forecast` to get the weather forecast
    
    ## Response Format
    
    The forecast includes information such as:
    - Temperature (°C)
    - Precipitation (mm)
    - Sky condition (clear, cloudy, etc.)
    - Humidity (%)
    - Wind speed and direction
    """

@mcp.prompt(
    name="weather-query",
    description="用于查询中国地区天气信息的交互式提示模板。此提示指导用户与LLM之间的结构化对话，提供适当的工具使用顺序和响应格式。收集用户所需的信息，并清晰地提供天气预报。"
)
def weather_query_prompt() -> str:
    """A prompt template for querying weather information for Chinese locations."""
    return """
    # China Weather Query
    
    You are a helpful weather information assistant for China. 
    Use the tools available to provide accurate weather information.
    
    ## Instructions
    
    1. Help the user find the weather forecast for their location in China.
    2. First use the `get_grid_location` tool to find the grid coordinates (nx, ny) for the specified location.
    3. Then use the `get_forecast` tool with those coordinates to get the detailed weather forecast.
    4. Present the weather information in a clear, organized format.
    5. If the user doesn't specify a complete location (province, city, and district), ask for clarification.
    
    ## Example Interaction
    
    User: What's the weather like in 朝阳区 三里屯街道?
    
    Assistant: I need to know the province as well. Could you please provide the complete location (province, city, district)?
    
    User: 北京市 朝阳区 三里屯街道
    
    Assistant: Let me check the weather for 北京市 朝阳区 三里屯街道.
    [Uses get_grid_location to get coordinates]
    [Uses get_forecast with those coordinates]
    Here's the current weather and forecast for 北京市 朝阳区 三里屯街道...
    
    ## Response Format
    
    When providing weather information, include:
    1. Current conditions (temperature, precipitation, sky condition)
    2. Short-term forecast (next few hours)
    3. Any relevant weather warnings or advisories
    """

if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport='stdio')
