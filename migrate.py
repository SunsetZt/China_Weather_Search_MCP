#!/usr/bin/env python3
import os
import pandas as pd
import sqlite3
from pathlib import Path

def migrate_excel_to_sqlite():
    """
    将 nxy.xlsx 中的行政区划与网格坐标数据迁移至 SQLite 数据库。
    所需字段：省份, 城市, 区县, 网格X, 网格Y
    """

    # 定义路径
    base_dir = Path(__file__).parent.parent  # 项目根目录
    data_dir = base_dir / "data"             # 数据目录
    excel_file = data_dir / "nxy.xlsx"        # Excel 文件路径
    db_file = data_dir / "weather_grid.db"    # SQLite 数据库文件路径

    # 创建数据目录（如果不存在）
    os.makedirs(data_dir, exist_ok=True)

    # 检查 Excel 文件是否存在
    if not excel_file.exists():
        raise FileNotFoundError(f"未找到 Excel 文件: {excel_file}")

    # 读取 Excel 文件
    print(f"正在读取 Excel 文件: {excel_file}")
    df = pd.read_excel(excel_file)

    # 检查必需字段是否齐全
    required_columns = ["省份", "城市", "区县", "网格X", "网格Y"]
    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Excel 文件中缺少必要字段: '{column}'")

    # 连接 SQLite 数据库（如果不存在则自动创建）
    print(f"正在创建或连接数据库: {db_file}")
    conn = sqlite3.connect(db_file)

    # 创建表结构
    conn.execute('''
    CREATE TABLE IF NOT EXISTS weather_grid (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        province TEXT NOT NULL,
        city TEXT NOT NULL,
        district TEXT NOT NULL,
        grid_x INTEGER NOT NULL,
        grid_y INTEGER NOT NULL,
        UNIQUE(province, city, district)
    )
    ''')

    # 插入数据
    print("正在插入数据到数据库...")
    for _, row in df.iterrows():
        try:
            conn.execute(
                '''
                INSERT OR REPLACE INTO weather_grid 
                (province, city, district, grid_x, grid_y) 
                VALUES (?, ?, ?, ?, ?)
                ''',
                (
                    row["省份"],
                    row["城市"],
                    row["区县"],
                    int(row["网格X"]),
                    int(row["网格Y"])
                )
            )
        except Exception as e:
            print(f"插入记录时发生错误: {row.to_dict()}，错误信息: {e}")

    # 提交更改并关闭连接
    conn.commit()
    conn.close()

    print("数据迁移完成！")

    # 输出统计信息
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM weather_grid")
    count = cursor.fetchone()[0]
    print(f"数据库中共有 {count} 条记录")
    conn.close()


if __name__ == "__main__":
    migrate_excel_to_sqlite()