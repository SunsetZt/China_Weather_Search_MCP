# config.py

# API 配置
WEATHER_API_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
WEATHER_API_SERVICE_KEY_ENV_NAME = "CN_WEATHER_API_KEY"  # 环境变量名

# 默认请求参数
DEFAULT_REQUEST_PARAMS = {
    "dataType": "json",
    "numOfRows": 60,
    "pageNo": 1,
}

# 请求超时时间（秒）
REQUEST_TIMEOUT = 30.0

# 用户代理标识
USER_AGENT = "cn-weather-app/1.0"

# 支持的城市或地区示例（可选，用于前端或 CLI 命令选择）
SUPPORTED_LOCATIONS = {
    "北京市": {"province": "北京市", "city": "北京市", "district": "朝阳区", "nx": 61, "ny": 125},
    "上海市": {"province": "上海市", "city": "上海市", "district": "浦东新区", "nx": 65, "ny": 129},
    "广州市": {"province": "广东省", "city": "广州市", "district": "天河区", "nx": 77, "ny": 127},
    "深圳市": {"province": "广东省", "city": "深圳市", "district": "南山区", "nx": 78, "ny": 128},
    "成都市": {"province": "四川省", "city": "成都市", "district": "武侯区", "nx": 54, "ny": 105},
}

# 日志配置
LOG_LEVEL = "INFO"  # 可选: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"