import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

# 设置中文字体支持
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]

# 纽约市的10个地点
locations = [
    "Pier 61 at Chelsea Piers, New York, NY",
    "West Drive & Prospect Park West, Brooklyn, NY",
    "E 33 St & 1 Ave, New York, NY",
    "Cleveland Pl & Spring St, New York, NY",
    "N 7 St & Driggs Ave, Brooklyn, NY",
    "West End Ave & W 60 St, New York, NY",
    "N 6 St & Bedford Ave, Brooklyn, NY",
    "Hanson Pl & Ashland Pl, Brooklyn, NY",
    "Bergen St & Vanderbilt Ave, Brooklyn, NY",
    "Franklin St & Dupont St, Brooklyn, NY"
]

# 预定义的经纬度（使用预定义值确保能生成完整的距离矩阵）
# 这些是从公开地理数据获取的近似坐标
predefined_coords = {
    "Pier 61 at Chelsea Piers": (40.7492, -74.0085),
    "West Drive & Prospect Park West": (40.6665, -73.9761),
    "E 33 St & 1 Ave": (40.7475, -73.9750),
    "Cleveland Pl & Spring St": (40.7226, -73.9900),
    "N 7 St & Driggs Ave": (40.7150, -73.9595),
    "West End Ave & W 60 St": (40.7673, -73.9822),
    "N 6 St & Bedford Ave": (40.7150, -73.9610),
    "Hanson Pl & Ashland Pl": (40.6805, -73.9705),
    "Bergen St & Vanderbilt Ave": (40.6796, -73.9687),
    "Franklin St & Dupont St": (40.7356, -73.9587)
}

# 创建地理编码器
geolocator = Nominatim(user_agent="nyc_bike_distance_calculator", timeout=10)

# 获取每个地点的经纬度
coordinates = []
location_names = []

print("正在获取每个地点的经纬度...")
for loc in locations:
    # 提取地点的简短名称（用于表格显示和匹配预定义坐标）
    short_name = loc.split(',')[0]
    location_names.append(short_name)
    
    try:
        # 尝试通过API获取经纬度
        location = geolocator.geocode(loc)
        if location:
            coord = (location.latitude, location.longitude)
            coordinates.append(coord)
            print(f"API获取成功 - {short_name}: ({coord[0]}, {coord[1]})")
        else:
            # 如果API获取失败，使用预定义坐标
            if short_name in predefined_coords:
                coord = predefined_coords[short_name]
                coordinates.append(coord)
                print(f"使用预定义坐标 - {short_name}: ({coord[0]}, {coord[1]})")
            else:
                coordinates.append(None)
                print(f"无法找到 {short_name} 的位置")
        
        # 添加延迟以避免请求过于频繁
        time.sleep(2)
    except Exception as e:
        # 如果发生异常，使用预定义坐标
        if short_name in predefined_coords:
            coord = predefined_coords[short_name]
            coordinates.append(coord)
            print(f"API请求异常，使用预定义坐标 - {short_name}: ({coord[0]}, {coord[1]})")
        else:
            coordinates.append(None)
            print(f"获取 {loc} 位置时出错: {e}")
        
        # 发生异常后增加延迟时间
        time.sleep(3)

# 创建距离矩阵
n = len(locations)
distance_matrix = np.zeros((n, n))

print("\n正在计算两两之间的距离...")
for i in range(n):
    if coordinates[i] is None:
        continue
    for j in range(n):
        if coordinates[j] is None:
            continue
        # 计算两点之间的地理距离（公里）
        distance = geodesic(coordinates[i], coordinates[j]).km
        distance_matrix[i, j] = round(distance, 2)

# 创建数据框并保存为Excel文件
df = pd.DataFrame(distance_matrix, index=location_names, columns=location_names)

# 保存到Excel文件
excel_file = "nyc_bike_station_distances.xlsx"
df.to_excel(excel_file, index=True)

print(f"\n距离矩阵已保存到 {excel_file}")
print("\n前5行前5列的距离矩阵预览:")
print(df.iloc[:5, :5])