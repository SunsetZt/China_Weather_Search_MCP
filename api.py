import os
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv
from utils import make_api_request

load_dotenv()

USER_AGENT = "weather-app/1.0"

# 风向映射（中文）
wind_direction_cn = {
    'N': '北',
    'NNE': '东北偏北',
    'NE': '东北',
    'ENE': '东偏北',
    'E': '东',
    'ESE': '东偏南',
    'SE': '东南',
    'SSE': '西南偏南',
    'S': '南',
    'SSW': '西南偏南',
    'SW': '西南',
    'WSW': '西偏南',
    'W': '西',
    'WNW': '西偏北',
    'NW': '西北',
    'NNW': '北偏西'
}

# 度数到风向代码映射
deg_code = {
    0: 'N', 360: 'N', 180: 'S', 270: 'W', 90: 'E',
    22.5: 'NNE', 45: 'NE', 67.5: 'ENE',
    112.5: 'ESE', 135: 'SE', 157.5: 'SSE',
    202.5: 'SSW', 225: 'SW', 247.5: 'WSW',
    292.5: 'WNW', 315: 'NW', 337.5: 'NNW'
}

# 天气状态代码映射
sky_code = {
    1: '晴',
    3: '多云',
    4: '阴'
}

# 降水类型代码映射
rain_type_code = {
    0: '无降水',
    1: '雨',
    2: '雨夹雪',
    3: '雪',
    5: '毛毛雨',
    6: '冻雨',
    7: '阵雪'
}


def format_weather_features(features: dict) -> str:
    """格式化天气特征信息"""
    formatted_features = []
    for key, value in features.items():
        if key == 'sky':
            formatted_features.append(f"天空状况: {value}")
        elif key == 'rain':
            formatted_features.append(f"降水类型: {value}")
        elif key == 'rain_amount':
            formatted_features.append(f"降水量: {value}mm")
        elif key == 'temp':
            formatted_features.append(f"气温: {value}℃")
        elif key == 'humidity':
            formatted_features.append(f"湿度: {value}%")
        elif key == 'wind_direction':
            formatted_features.append(f"风向: {value}")
        elif key == 'wind_speed':
            formatted_features.append(f"风速: {value}m/s")
    return "\n".join(formatted_features)


def deg_to_dir(deg):
    """将风向角度转换为方向名称"""
    close_dir = ''
    min_abs = 360
    if deg not in deg_code.keys():
        for key in deg_code.keys():
            if abs(key - deg) < min_abs:
                min_abs = abs(key - deg)
                close_dir = deg_code[key]
    else:
        close_dir = deg_code[deg]
    return wind_direction_cn[close_dir]


async def get_forecast_api(province: str, city: str, district: str, nx: float, ny: float) -> str:
    """获取指定地区的天气预报"""
    try:
        serviceKey = os.environ.get("CN_WEATHER_API_KEY")
        if not serviceKey:
            raise ValueError("CN_WEATHER_API_KEY 环境变量未设置")

        # 获取当前时间并格式化为API需要的日期和时间
        base_date = datetime.now().strftime("%Y%m%d")  # 发布日期
        base_time = datetime.now().strftime("%H%M")  # 发布时间

        # 计算输入时间（当前时间减去一小时）
        input_d = datetime.strptime(base_date + base_time, "%Y%m%d%H%M") - timedelta(hours=1)
        input_datetime = datetime.strftime(input_d, "%Y%m%d%H%M")
        input_date = input_datetime[:8]
        input_time = input_datetime[8:]

        # 构建API请求URL
        url = f"http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst?serviceKey={serviceKey}&numOfRows=60&pageNo=1&dataType=json&base_date={input_date}&base_time={input_time}&nx={nx}&ny={ny}"

        # 发送API请求
        data = await make_api_request(url)

        if not data:
            raise ValueError("API 请求返回为空")

        if 'response' not in data:
            raise KeyError("API 响应中缺少 'response' 字段")

        if 'body' not in data['response']:
            raise KeyError("API 响应中缺少 'body' 字段")

        if 'items' not in data['response']['body']:
            raise KeyError("API 响应中缺少 'items' 字段")

        if 'item' not in data['response']['body']['items']:
            raise KeyError("API 响应中缺少 'item' 字段")

        res = data['response']['body']['items']['item']
        if not res:
            return [f"{province} {city} {district} 地区的 weather information could not be found."]

        informations = dict()
        for items in res:
            try:
                cate = items['category']
                fcstTime = items['fcstTime']
                fcstValue = items['fcstValue']

                if fcstTime not in informations.keys():
                    informations[fcstTime] = dict()

                informations[fcstTime][cate] = fcstValue
            except KeyError as e:
                print(f"Missing weather data field: {e}")
                continue

        if not informations:
            return [f"无法处理 {province} {city} {district} 地区的天气信息。"]

        forecasts = []
        for key, val in zip(informations.keys(), informations.values()):
            features = dict()
            try:
                template = f"""{base_date[:4]}年 {base_date[4:6]}月 {base_date[-2:]}日 {key[:2]}时 {key[2:]}分 {province} {city} {district} 地区的天气是 """

                # 天空状态
                if 'SKY' in val and val['SKY']:
                    try:
                        sky_temp = sky_code[int(val['SKY'])]
                        features['sky'] = sky_temp
                    except (ValueError, KeyError):
                        print(f"天空状态代码处理错误: {val['SKY']}")

                # 降水类型
                if 'PTY' in val and val['PTY']:
                    try:
                        pty_temp = rain_type_code[int(val['PTY'])]
                        features['rain'] = pty_temp
                        # 如果有降水
                        if 'RN1' in val and val['RN1'] != '无降水':
                            rn1_temp = val['RN1']
                            features['rain_amount'] = rn1_temp
                    except (ValueError, KeyError):
                        print(f"降水类型代码处理错误: {val['PTY']}")

                # 气温
                if 'T1H' in val and val['T1H']:
                    try:
                        t1h_temp = float(val['T1H'])
                        features['temp'] = t1h_temp
                    except ValueError:
                        print(f"温度值处理错误: {val['T1H']}")

                # 湿度
                if 'REH' in val and val['REH']:
                    try:
                        reh_temp = float(val['REH'])
                        features['humidity'] = reh_temp
                    except ValueError:
                        print(f"湿度值处理错误: {val['REH']}")

                # 风向/风速
                if 'VEC' in val and val['VEC'] and 'WSD' in val and val['WSD']:
                    try:
                        vec_temp = deg_to_dir(float(val['VEC']))
                        wsd_temp = val['WSD']
                        features['wind_direction'] = vec_temp
                        features['wind_speed'] = wsd_temp
                    except ValueError:
                        print(f"风向/风速值处理错误: VEC={val.get('VEC')}, WSD={val.get('WSD')}")

                forecasts.append(template + format_weather_features(features))
            except Exception as e:
                print(f"处理天气信息时出错: {e}")
                continue

        if not forecasts:
            return f"无法生成 {province} {city} {district} 地区的天气信息"

        return "\n---\n".join(forecasts)

    except Exception as e:
        print(f"天气 API 请求错误: {e}")
        return [f"获取天气信息时发生错误: {str(e)}"]


if __name__ == "__main__":
    asyncio.run(get_forecast_api("北京市", "朝阳区", "三里屯街道", 61, 125))