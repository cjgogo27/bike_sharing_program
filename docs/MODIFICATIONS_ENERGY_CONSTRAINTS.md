# 能量约束和租用成本模型修改说明
# Modifications for Energy Constraints and Rental Time Cost Model

## 修改日期 (Modification Date)
2025年10月16日

## 修改概述 (Modification Overview)

根据提供的数学公式,对 `Intermodal_ALNS_0625.py` 进行了以下修改,以纳入:
1. 电池能量约束 (Battery energy constraints)
2. 租用时间成本 (Rental time cost)
3. 服务率约束 (Service rate constraints)

---

## 1. 新增/修改的参数 (New/Modified Parameters)

在车辆参数矩阵 `K` 中新增以下列(如果不存在则使用默认值):

| 列索引 | 参数 | 说明 | 单位 | 默认值 |
|--------|------|------|------|--------|
| K[k, 9] | B_k | 电池容量 | kWh | 100.0 |
| K[k, 10] | alpha_k | 时间能耗系数 | kWh/hour | 1.0 |
| K[k, 11] | beta_k | 距离能耗系数 | kWh/km | 0.2 |
| K[k, 12] | rental_rate | 租用费率 | currency/hour | 5.0 |

---

## 2. 修改的目标函数 (Modified Objective Function)

### 原目标函数:
```
cost = w1 * C_ops + w2 * C_delay + w3 * C_emission
```

### 新目标函数 (公式 1):
```
F = w1 * C_ops + w2 * C_delay + w3 * C_emission + w4 * C_rent_time + w5 * C_unserved
```

其中:
- `C_ops = vehicle_cost + request_cost + wait_cost + transshipment_cost + un_load_cost`
- `C_rent_time = r_k * T_k` (公式 3)
- `C_unserved = Σ p^un_r * (1 - z_r)` (公式 4)

新增权重:
- `w4 = 0.1` (租用时间成本权重)
- `w5 = 0.05` (未服务请求惩罚权重)

---

## 3. 能量消耗模型 (Energy Consumption Model)

### 公式 5: 能量消耗
```
E^cons_{k,ij} = alpha_k * tau_ij + beta_k * d_ij
```

实现:
```python
energy_consumption = alpha_k * travel_time_hours + beta_k * distance_km
```

### 公式 6: 能量平衡
```
e^k_j = e^k_i - E^cons_{k,ij} * y^k_{ij} + ch^k_j
```

实现:
- 每段行程后更新剩余电量
- 当电量低于30%时自动充电至满电

### 公式 7: 起飞可行性约束
```
e^k_i >= E^cons_{k,ij} => y^k_{ij} = 1
e^k_i < E^cons_{k,ij} => y^k_{ij} = 0
```

实现:
- 在每段行程前检查剩余电量是否足够
- 如果不足,返回高惩罚成本使该路径不可行

### 公式 8: 电池容量限制
```
0 <= e^k_i <= B_k
```

实现:
- 在每次更新电量后检查是否在范围内

---

## 4. 运营时间计算 (Operation Time Calculation)

### 公式 9: 总运营时间
```
T_k = Σ tau_ij * y^k_{ij} + Σ t^svc_{k,i}
```

实现:
```python
total_operation_time = Σ travel_time_hours + Σ service_time
```

- 旅行时间: `travel_time_hours = new_try[1, x] - new_try[3, x-1]`
- 服务时间: 默认为 0.1 小时/请求(可调整)

---

## 5. 服务率约束 (Service Rate Constraints)

### 公式 10: 服务率
```
S = Σ z_r / |R|
```

实现:
- 统计所有路径中服务的唯一请求数
- 未服务的请求产生惩罚成本
- 通过最小化 `C_unserved` 来最大化服务率

---

## 6. 新增函数 (New Functions)

### 6.1 `calculate_energy_consumption(k, distance_km, travel_time_hours)`
计算车辆 k 在给定距离和时间下的能量消耗

### 6.2 `check_battery_feasibility(k, route)`
检查路径是否满足电池约束,返回可行性和最小电量

### 6.3 `calculate_service_rate(routes_local)`
计算整体服务率和已服务请求数

### 6.4 `validate_energy_constraints_global(routes_local)`
全局验证所有车辆的能量约束

---

## 7. 修改的返回值 (Modified Return Values)

`objective_value_k` 函数的返回值从 16 个增加到 22 个:

原返回值(16个):
```python
(cost, time, vehicle_cost, request_cost, wait_cost, transshipment_cost, 
 un_load_cost, distance, profit, emission, emission_cost, storage_cost, 
 delay_penalty, number_transshipment, average_speed, average_time_ratio)
```

新返回值(22个):
```python
(cost, time, vehicle_cost, request_cost, wait_cost, transshipment_cost, 
 un_load_cost, distance, profit, emission, emission_cost, storage_cost, 
 delay_penalty, number_transshipment, average_speed, average_time_ratio,
 rental_time_cost, unserved_cost, total_operation_time, remaining_energy,
 total_energy_consumption, charging_energy)
```

新增的返回值:
- `rental_time_cost`: 租用时间成本
- `unserved_cost`: 未服务请求惩罚
- `total_operation_time`: 总运营时间(小时)
- `remaining_energy`: 路径结束时的剩余电量
- `total_energy_consumption`: 总能量消耗
- `charging_energy`: 总充电量

---

## 8. 充电策略 (Charging Strategy)

当前实现的充电策略:
- **充电触发条件**: 剩余电量 < 30% * B_k
- **充电方式**: 充电至满电 (B_k)
- **充电位置**: 所有节点均可充电
- **充电时间**: 当前未显式建模(可在未来版本中添加)

**可扩展方向**:
1. 添加充电时间约束
2. 添加充电功率限制
3. 区分充电站和普通节点
4. 实现部分充电策略

---

## 9. 使用示例 (Usage Example)

### 调用修改后的函数:
```python
k = 0  # 车辆索引
route = routes_local[k]

# 获取完整的目标函数值和指标
(cost, time, vehicle_cost, request_cost, wait_cost, transshipment_cost, 
 un_load_cost, distance, profit, emission, emission_cost, storage_cost, 
 delay_penalty, number_transshipment, average_speed, average_time_ratio,
 rental_time_cost, unserved_cost, total_operation_time, remaining_energy,
 total_energy_consumption, charging_energy) = objective_value_k(k, route)

print(f"Total cost: {cost}")
print(f"Rental time cost: {rental_time_cost}")
print(f"Operation time: {total_operation_time} hours")
print(f"Remaining energy: {remaining_energy} kWh")
print(f"Energy consumed: {total_energy_consumption} kWh")
```

### 检查电池可行性:
```python
feasible, min_energy = check_battery_feasibility(k, route)
if feasible:
    print(f"Route is feasible. Minimum energy: {min_energy} kWh")
else:
    print("Route is infeasible due to battery constraints")
```

### 计算服务率:
```python
service_rate, served, total = calculate_service_rate(routes_local)
print(f"Service rate: {service_rate:.2%} ({served}/{total})")
```

### 全局验证:
```python
all_feasible, infeasible = validate_energy_constraints_global(routes_local)
if all_feasible:
    print("All routes satisfy energy constraints")
else:
    print(f"Infeasible vehicles: {infeasible}")
```

---

## 10. 注意事项 (Important Notes)

1. **距离单位转换**: 代码中假设 `D[k][i, j]` 的单位是米,转换为公里时除以1000
   - 请根据实际数据单位调整

2. **时间单位**: 所有时间相关计算使用小时(hour)为单位

3. **权重调优**: 新增的权重 `w4` 和 `w5` 可根据实际需求调整:
   ```python
   w4 = 0.1   # 租用时间成本权重
   w5 = 0.05  # 未服务请求惩罚权重
   ```

4. **兼容性**: 如果车辆参数矩阵 `K` 中没有新增列,代码会使用默认值,保持向后兼容

5. **调用更新**: 所有调用 `objective_value_k` 的地方都需要更新以接收新的返回值

---

## 11. 未来扩展 (Future Extensions)

1. **动态充电策略**: 
   - 根据后续路径需求决定充电量
   - 考虑充电时间和成本

2. **充电站网络**:
   - 区分充电站和普通节点
   - 添加充电站容量约束

3. **电池老化模型**:
   - 考虑电池随使用次数的衰减
   - 深度放电对电池的影响

4. **再生制动**:
   - 在下坡或减速时回收能量

5. **温度影响**:
   - 考虑环境温度对电池性能的影响

---

## 12. 测试建议 (Testing Recommendations)

1. **单元测试**:
   - 测试能量消耗计算的准确性
   - 验证电池约束检查逻辑
   - 测试边界情况(满电、空电)

2. **集成测试**:
   - 在实际路径规划中验证能量约束
   - 检查租用成本计算的正确性
   - 验证服务率计算

3. **性能测试**:
   - 评估新增约束对计算时间的影响
   - 大规模实例的可行性验证

---

## 13. 参考文献 (References)

本修改基于提供的数学公式 (Mathematical Formulations - Modified Version):
- Section 3.1: Notation and Decision Variables
- Section 3.2: Modified Objective Function
- Section 3.3: Energy Consumption and Battery Constraints
- Section 3.4: Vehicle Rental Time Definition
- Section 3.5: Service Rate Constraints
- Section 3.6: Model Integration

---

## 联系方式 (Contact)
如有问题或建议,请联系开发团队。
