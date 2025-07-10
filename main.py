import argparse
from pathlib import Path
import sqlite3


def get_grid_location(province, city, district):
    """
    根据省、市、区获取对应的网格坐标 (grid_x, grid_y)

    Args:
        province (str): 省名，例如 "北京市"
        city (str): 市名，例如 "北京市"
        district (str): 区县名，例如 "朝阳区"

    Returns:
        tuple: (grid_x, grid_y) 网格坐标，如果未找到则返回 None
    """
    db_path = Path(__file__).parent / "data" / "weather_grid.db"

    if not db_path.exists():
        raise FileNotFoundError(f"数据库文件未找到: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT grid_x, grid_y 
            FROM weather_grid 
            WHERE province = ? AND city = ? AND district = ?
            """,
            (province, city, district)
        )
        result = cursor.fetchone()

        if result:
            return result[0], result[1]
        else:
            return None
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="查询指定地区的气象网格坐标")
    parser.add_argument("--province", type=str, help="省份名称（如：北京市）")
    parser.add_argument("--city", type=str, help="城市名称（如：北京市）")
    parser.add_argument("--district", type=str, help="区县名称（如：朝阳区）")

    args = parser.parse_args()

    # 如果参数未提供，则使用默认值进行演示
    if not (args.province and args.city and args.district):
        print("未提供完整地区信息，使用示例数据:")
        args.province = "北京市"
        args.city = "北京市"
        args.district = "朝阳区"

    try:
        grid = get_grid_location(args.province, args.city, args.district)

        if grid:
            nx, ny = grid
            print(f"{args.province} {args.city} {args.district} 的网格坐标为：X={nx}, Y={ny}")
        else:
            print(f"未在数据库中找到 {args.province} {args.city} {args.district} 的网格坐标")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    main()