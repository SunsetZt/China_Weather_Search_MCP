from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio

# 创建服务器参数，使用标准输入输出连接到 MCP 服务
server_params = StdioServerParameters(
    command=".venv/bin/python",  # Python 可执行文件路径
    args=["src/server.py"],       # MCP 服务端脚本路径
    env=None                      # 可选环境变量
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()

            # 列出可用的提示词（prompts）
            prompts = await session.list_prompts()
            print(f"Available prompts: {prompts}")

            # 获取天气相关的提示词
            weather_prompt = await session.get_prompt("weather-query")
            print(f"Weather prompt: {weather_prompt}")

            # 列出可用资源（resources）
            resources = await session.list_resources()
            print(f"Available resources: {resources}")

            # 读取天气说明文档（可选）
            instructions, mime_type = await session.read_resource("weather://instructions")
            print(f"Weather instructions: {instructions}")

            # 列出可用工具（tools）
            tools = await session.list_tools()
            print(f"Available tools: {tools}")

            # 示例：调用 get_grid_location 工具获取网格坐标
            province = "北京市"
            city = "北京市"
            district = "朝阳区"

            grid_result = await session.call_tool(
                "get_grid_location",
                arguments={
                    "province": province,
                    "city": city,
                    "district": district
                }
            )
            print(f"Grid location result: {grid_result}")

            # 解析返回结果中的 Nx 和 Ny 值
            nx, ny = None, None
            try:
                if grid_result.content and len(grid_result.content) > 0:
                    result_text = grid_result.content[0].text
                    if not result_text.startswith("No location") and not result_text.startswith("Error"):
                        parts = result_text.split(", ")
                        for part in parts:
                            if part.startswith("Grid X:"):
                                nx = int(part.split(": ")[1])
                            elif part.startswith("Grid Y:"):
                                ny = int(part.split(": ")[1])
            except Exception as e:
                print(f"解析网格坐标时出错: {e}")

            if nx is None or ny is None:
                print("无法获取有效的网格坐标，请检查输入地区是否正确。")
                return

            print(f"获取到网格坐标: Grid X={nx}, Grid Y={ny}")

            # 调用 get_forecast 工具获取天气预报
            forecast_result = await session.call_tool(
                "get_forecast",
                arguments={
                    "province": province,
                    "city": city,
                    "district": district,
                    "nx": nx,
                    "ny": ny
                }
            )

            # 输出天气预报结果
            if forecast_result.content:
                print("=== 天气预报结果 ===")
                for content in forecast_result.content:
                    print(content.text)
            else:
                print("未返回天气预报数据。")

if __name__ == "__main__":
    asyncio.run(run())