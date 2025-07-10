# 中国天气 MCP 服务



本 MCP（多平台通信协议）服务提供了对中国气象局 API 的访问，允许 AI 智能体获取中国地区的天气预报信息。

## 概述

- 获取中国行政区划的精确网格坐标（省、市、区）
- 提供详细的短期天气预报
- 支持所有中国的行政划分（省份、城市、区县）
- 结构化文本响应，优化了大语言模型处理体验
- 包含完整的天气数据：气温、降水、天空状况、湿度、风向和风速

## 目录

- [安装前提](#安装前提)
- [安装步骤](#安装步骤)
- [配置 MCP 设置](#配置-mcp-设置)
- [API 参考](#api-参考)
- [致谢](#致谢)
- [许可证](#许可证)

## 安装说明

### 安装前提

- Python 3.12+
- 中国气象局 API 凭证
- 注册并申请[中国气象数据网](http://data.cma.cn/)提供的 API 访问权限

### 安装步骤

1. 克隆仓库：
```bash
git clone [https://github.com/jikime/py-mcp-cn-weather.git](https://github.com/SunsetZt/China_Weather_Search_MCP)
cd China_Weather_Search_MCP
```

2. 安装 uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. 创建虚拟环境并安装依赖：
```bash
uv venv -p 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

4. 创建 `.env` 文件并填写你的中国气象局 API 凭证：
```bash
cp env.example .env
vi .env

CN_WEATHER_API_KEY=your_api_key_here
```

5. 将 Excel 中的网格坐标数据迁移到 SQLite 数据库：
```bash
uv run src/migrate.py
```

#### 本地运行

1. 启动服务器：
```bash
mcp run src/server.py
```
2. 运行 MCP Inspector
```bash
mcp dev server.py
```

## 配置 MCP 设置

将以下服务器配置添加到你的 MCP 设置文件中：

#### Claude 桌面应用 
1. 通过 [Smithery](https://smithery.ai/server/@jikime/py-mcp-cn-weather) 自动安装：

```bash
npx -y @smithery/cli install @jikime/py-mcp-cn-weather --client claude
```

2. 手动安装
打开 `~/Library/Application Support/Claude/claude_desktop_config.json`

在 `mcpServers` 对象中添加如下内容：
```json
{
  "mcpServers": {
    "中国天气工具箱": {
      "command": "/path/to/bin/uv",
      "args": [
        "--directory",
        "/path/to/py-mcp-cn-weather",
        "run",
        "src/server.py"
      ]
    }
  }
}
```

#### Cursor IDE 
打开 `~/.cursor/mcp.json`

在 `mcpServers` 对象中添加如下内容：
```json
{
  "mcpServers": {
    "中国天气工具箱": {
      "command": "/path/to/bin/uv",
      "args": [
        "--directory",
        "/path/to/py-mcp-cn-weather",
        "run",
        "src/server.py"
      ]
    }
  }
}
```


## API 参考

### 工具

#### 获取网格位置
```
get_grid_location(province: str, city: str, district: str) -> dict
```
根据指定地区获取对应的网格坐标 (grid_x, grid_y)，用于调用中国气象局 API。
该工具会基于数据库中的省、市、区信息查询精确的坐标。

#### 获取天气预报
```
get_forecast(province: str, city: str, district: str, grid_x: int, grid_y: int) -> str
```
调用中国气象局的短期天气预报 API，提供特定地区的天气信息。
返回包含气温、降水、天空状况、湿度、风向和风速等全面的天气数据。

### 资源

#### 天气说明文档
```
GET weather://instructions
```
提供有关如何使用中国天气 MCP 服务的详细文档，包括工具工作流程和响应格式说明。

### 提示词

#### 天气查询
服务器包含一个结构化的天气查询提示模板，指导对话流程，确保高效的信息收集和清晰的预报结果展示。

## 响应格式

天气预报响应采用结构化文本格式，优化了大语言模型的处理效率：

```
北京市 朝阳区 的天气预报（坐标: grid_x=61, grid_y=125）
日期: 2025-05-01
时间: 15:00

当前状况:
气温: 22.3°C
天空状况: 晴
降水量: 无
降水概率: 0%
湿度: 45%
风向: 西北
风速: 2.3 m/s

小时预报:
16:00 - 气温: 21.8°C, 天空: 晴, 降水: 无
17:00 - 气温: 20.5°C, 天空: 晴, 降水: 无
18:00 - 气温: 19.2°C, 天空: 晴, 降水: 无
...
```

## 致谢

- [中国气象局](https://www.cma.gov.cn/)
- [中国气象数据网](http://data.cma.cn/)
- [MCP 协议](https://github.com/mcp-foundation/mcp-spec)

## 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件。
