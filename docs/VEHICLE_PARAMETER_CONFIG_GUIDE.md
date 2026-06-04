# 车辆参数配置说明
# Vehicle Parameter Configuration Guide

本文档说明如何配置车辆参数矩阵 K,以支持能量约束和租用成本模型。

## 车辆参数矩阵 K 的列定义

原有列(0-8):
- K[:, 0]: 车辆ID / Vehicle ID
- K[:, 1]: 速度 / Speed (km/h)
- K[:, 2]: 时间成本系数 / Time cost coefficient
- K[:, 3]: 距离成本系数 / Distance cost coefficient  
- K[:, 4]: 排放因子 / Emission factor
- K[:, 5]: 车辆类型 / Vehicle type
- K[:, 6]: 容量 / Capacity
- K[:, 7]: 固定成本 / Fixed cost
- K[:, 8]: 最大工作时间 / Max working time

新增列(9-12):
- K[:, 9]: 电池容量 B_k (kWh)
- K[:, 10]: 时间能耗系数 alpha_k (kWh/hour)
- K[:, 11]: 距离能耗系数 beta_k (kWh/km)
- K[:, 12]: 租用费率 r_k (currency/hour)

---

## 默认值设置

如果 K 矩阵不包含新增列,代码将使用以下默认值:
- B_k (电池容量): 100.0 kWh
- alpha_k (时间能耗系数): 1.0 kWh/hour
- beta_k (距离能耗系数): 0.2 kWh/km
- r_k (租用费率): 5.0 currency/hour

---

## 车辆类型推荐参数

### 1. 电动汽车 (Electric Vehicle - EV)
```python
vehicle_type = "EV"
B_k = 60.0          # 60 kWh 电池
alpha_k = 0.5       # 较低的时间能耗
beta_k = 0.15       # kWh/km
rental_rate = 8.0   # 中等租用费率
```

### 2. 电动无人机 (Electric Drone)
```python
vehicle_type = "Drone"
B_k = 5.0           # 5 kWh 小型电池
alpha_k = 2.0       # 较高的时间能耗(悬停)
beta_k = 0.3        # kWh/km (较高,空中阻力大)
rental_rate = 15.0  # 较高租用费率
```

### 3. 电动垂直起降飞行器 (eVTOL)
```python
vehicle_type = "eVTOL"
B_k = 150.0         # 150 kWh 大容量电池
alpha_k = 3.0       # 高时间能耗
beta_k = 0.5        # kWh/km
rental_rate = 50.0  # 高租用费率
```

### 4. 电动自行车 (E-bike)
```python
vehicle_type = "E-bike"
B_k = 0.5           # 0.5 kWh
alpha_k = 0.03      # 很低的时间能耗
beta_k = 0.01       # kWh/km
rental_rate = 2.0   # 低租用费率
```

### 5. 电动货车 (Electric Van)
```python
vehicle_type = "E-Van"
B_k = 80.0          # 80 kWh
alpha_k = 0.8       # 中等时间能耗
beta_k = 0.25       # kWh/km
rental_rate = 12.0  # 中高租用费率
```

---

## 参数估算方法

### 1. 电池容量 B_k
- 查阅车辆制造商规格表
- 典型范围: 
  - 小型: 0.5-10 kWh (自行车,小型无人机)
  - 中型: 30-100 kWh (汽车,货车)
  - 大型: 100-300 kWh (大型车辆,eVTOL)

### 2. 时间能耗系数 alpha_k (kWh/hour)
计算公式:
```
alpha_k = (P_idle + P_systems) / 1000
```
其中:
- P_idle: 怠速功率 (W)
- P_systems: 车载系统功率 (W)

典型值:
- 电动汽车: 0.3-1.0 kWh/h
- 无人机: 1.0-3.0 kWh/h (悬停功率高)
- eVTOL: 2.0-5.0 kWh/h

### 3. 距离能耗系数 beta_k (kWh/km)
计算公式:
```
beta_k = (能量消耗总量 / 行驶距离)
```

典型值:
- 电动汽车: 0.15-0.25 kWh/km
- 电动货车: 0.20-0.35 kWh/km
- 电动自行车: 0.01-0.02 kWh/km
- 无人机: 0.2-0.5 kWh/km
- eVTOL: 0.3-0.8 kWh/km

影响因素:
- 车辆重量
- 空气动力学
- 地形(坡度)
- 天气条件
- 载重

### 4. 租用费率 r_k (currency/hour)
考虑因素:
- 车辆采购/折旧成本
- 维护成本
- 保险成本
- 市场租赁价格
- 运营成本

---

## Python 配置示例

### 方法1: 扩展现有 K 矩阵

```python
import numpy as np

# 假设原有 K 矩阵为 9 列
K_original = np.array([
    # [id, speed, time_cost, dist_cost, emission, type, capacity, fixed_cost, max_time]
    [0, 40, 0.5, 0.3, 2.5, 1, 100, 50, 8],
    [1, 60, 0.6, 0.4, 3.0, 1, 80, 60, 8],
    [2, 30, 0.4, 0.2, 1.5, 2, 50, 40, 6],
])

# 添加新列: [battery_capacity, alpha_k, beta_k, rental_rate]
new_columns = np.array([
    # EV 参数
    [60.0, 0.5, 0.15, 8.0],
    # 另一辆 EV
    [60.0, 0.5, 0.15, 8.0],
    # E-bike
    [0.5, 0.03, 0.01, 2.0],
])

# 合并
K = np.hstack([K_original, new_columns])

print(f"扩展后的 K 矩阵形状: {K.shape}")  # (3, 13)
```

### 方法2: 从配置文件读取

```python
import pandas as pd

# CSV 配置文件示例
vehicle_config = pd.DataFrame({
    'vehicle_id': [0, 1, 2],
    'vehicle_type': ['EV', 'EV', 'E-bike'],
    'speed': [40, 60, 30],
    'time_cost': [0.5, 0.6, 0.4],
    'dist_cost': [0.3, 0.4, 0.2],
    'emission_factor': [2.5, 3.0, 1.5],
    'type': [1, 1, 2],
    'capacity': [100, 80, 50],
    'fixed_cost': [50, 60, 40],
    'max_time': [8, 8, 6],
    'battery_capacity': [60.0, 60.0, 0.5],
    'alpha_k': [0.5, 0.5, 0.03],
    'beta_k': [0.15, 0.15, 0.01],
    'rental_rate': [8.0, 8.0, 2.0]
})

# 转换为 numpy 数组
K = vehicle_config.iloc[:, 2:].values

# 保存配置
vehicle_config.to_csv('vehicle_config.csv', index=False)
```

### 方法3: 根据车辆类型自动设置

```python
def set_energy_parameters(vehicle_type):
    """
    根据车辆类型自动设置能量参数
    """
    params = {
        'EV': {'B_k': 60.0, 'alpha_k': 0.5, 'beta_k': 0.15, 'rental_rate': 8.0},
        'E-Van': {'B_k': 80.0, 'alpha_k': 0.8, 'beta_k': 0.25, 'rental_rate': 12.0},
        'E-bike': {'B_k': 0.5, 'alpha_k': 0.03, 'beta_k': 0.01, 'rental_rate': 2.0},
        'Drone': {'B_k': 5.0, 'alpha_k': 2.0, 'beta_k': 0.3, 'rental_rate': 15.0},
        'eVTOL': {'B_k': 150.0, 'alpha_k': 3.0, 'beta_k': 0.5, 'rental_rate': 50.0},
    }
    
    return params.get(vehicle_type, 
                     {'B_k': 100.0, 'alpha_k': 1.0, 'beta_k': 0.2, 'rental_rate': 5.0})

# 使用示例
vehicle_types = ['EV', 'E-Van', 'E-bike']
for v_type in vehicle_types:
    params = set_energy_parameters(v_type)
    print(f"{v_type}: {params}")
```

---

## 权重参数配置

在目标函数中使用的权重参数建议:

```python
# 成本组件权重 (总和应为1.0)
w1 = 0.30  # 运营成本权重 (vehicle, request, wait, transshipment, unload)
w2 = 0.30  # 延迟惩罚权重
w3 = 0.20  # 排放成本权重
w4 = 0.10  # 租用时间成本权重 ⭐ NEW
w5 = 0.10  # 未服务请求惩罚权重 ⭐ NEW

# 不同场景的权重配置
scenarios = {
    'cost_focused': {'w1': 0.50, 'w2': 0.20, 'w3': 0.10, 'w4': 0.10, 'w5': 0.10},
    'time_focused': {'w1': 0.20, 'w2': 0.40, 'w3': 0.10, 'w4': 0.20, 'w5': 0.10},
    'eco_focused': {'w1': 0.20, 'w2': 0.20, 'w3': 0.40, 'w4': 0.10, 'w5': 0.10},
    'service_focused': {'w1': 0.20, 'w2': 0.20, 'w3': 0.10, 'w4': 0.10, 'w5': 0.40},
    'balanced': {'w1': 0.25, 'w2': 0.25, 'w3': 0.20, 'w4': 0.15, 'w5': 0.15},
}
```

---

## 验证检查清单

在运行优化前,请确认:

- [ ] K 矩阵已扩展到至少 13 列
- [ ] 所有车辆的电池容量 B_k > 0
- [ ] 能耗系数 alpha_k, beta_k >= 0
- [ ] 租用费率 rental_rate > 0
- [ ] 权重 w1-w5 已设置且总和合理
- [ ] 距离矩阵 D 的单位已确认(米/公里)
- [ ] 时间单位统一为小时
- [ ] 充电策略参数已设置(充电阈值等)

---

## 故障排查

### 问题1: 所有路径都不可行
**原因**: 电池容量太小或能耗系数过大
**解决**: 
- 增加 B_k
- 降低 alpha_k 或 beta_k
- 检查距离单位是否正确

### 问题2: 成本异常高
**原因**: 租用费率设置过高
**解决**: 调整 rental_rate 或降低 w4 权重

### 问题3: 电量计算不准确
**原因**: 单位不统一
**解决**: 
- 确保距离单位为公里
- 确保时间单位为小时
- 检查能耗系数单位

### 问题4: 服务率很低
**原因**: w5 权重过低
**解决**: 增加 w5 权重,提高对未服务请求的惩罚

---

## 参考数据来源

1. **车辆能耗数据**:
   - US EPA: https://www.fueleconomy.gov/
   - European Environment Agency
   - 车辆制造商技术规格

2. **租赁价格**:
   - 本地租车公司价格
   - 共享出行平台价格
   - 行业报告和市场调研

3. **碳排放因子**:
   - IPCC Guidelines
   - 国家/地区能源局数据
   - 电网碳强度数据

---

## 更新日志

- 2025-10-16: 初始版本,添加能量约束和租用成本参数配置指南
