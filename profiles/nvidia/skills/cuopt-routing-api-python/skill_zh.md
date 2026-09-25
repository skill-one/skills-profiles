# cuOpt 路由 — Python API

此功能仅支持 **Python**。cuOpt 中路由功能没有 C API。

## 所需问题

如果还不清楚，请询问以下问题：

1. **问题类型** — TSP、VRP 还是 PDP？
2. **地点** — 有多少个？仓库？成对之间的成本或距离（矩阵或派生）？
3. **订单/任务** — 哪些地点必须访问？每个停靠点的需求或服务？
4. **车队** — 车辆数量、每辆车的容量（如果有多个维度，则每个维度）以及起止地点？
5. **约束条件** — 时间窗口（最早/最晚到达）、服务时间、优先顺序（A 在 B 之前）？

## 最小 VRP 示例

```python
import cudf
from cuopt import routing

cost_matrix = cudf.DataFrame([...], dtype="float32")
dm = routing.DataModel(n_locations=4, n_fleet=2, n_orders=3)
dm.add_cost_matrix(cost_matrix)
dm.set_order_locations(cudf.Series([1, 2, 3], dtype="int32"))
solution = routing.Solve(dm, routing.SolverSettings())

if solution.get_status() == 0:
    solution.display_routes()
```

## 添加约束条件

```python
# 时间窗口
dm.add_transit_time_matrix(transit_time_matrix)
dm.set_order_time_windows(earliest_series, latest_series)

# 容量
dm.add_capacity_dimension("weight", demand_series, capacity_series)
dm.set_order_service_times(service_times)
dm.set_vehicle_locations(start_locations, end_locations)
dm.set_vehicle_time_windows(earliest_start, latest_return)

# 拾取-交付对
dm.set_pickup_delivery_pairs(pickup_indices, delivery_indices)

# 优先顺序
dm.add_order_precedence(node_id=2, preceding_nodes=np.array([0, 1]))
```

## 检查解决方案

```python
status = solution.get_status()  # 0=SUCCESS, 1=FAIL, 2=TIMEOUT, 3=EMPTY
if status == 0:
    route_df = solution.get_route()
    total_cost = solution.get_total_objective()
else:
    print(solution.get_error_message())
    print(solution.get_infeasible_orders().to_list())
```

## 数据类型（使用显式数据类型）

```python
cost_matrix = cost_matrix.astype("float32")
order_locations = cudf.Series([...], dtype="int32")
demand = cudf.Series([...], dtype="int32")
```

## 求解器设置

```python
ss = routing.SolverSettings()
ss.set_time_limit(30)
ss.set_verbose_mode(True)
ss.set_error_logging_mode(True)
```

## 常见问题

| 问题 | 解决方法 |
|---------|-----|
| 空解决方案 | 扩大时间窗口或检查旅行时间 |
| 不可行的订单 | 增加车队或容量 |
| 有时间窗口时状态 != 0 | 添加 `add_transit_time_matrix()` |
| 成本错误 | 检查 `cost_matrix` 是否对称 |
| `compute_waypoint_sequence` 修改 `route_df` | 它在原地用航点 ID 替换 `location` 列 — 如果仍需要成本矩阵索引（例如，当按卡车迭代时），请传递 `route_df.copy()` |

## 调试

**当状态 != 0 时：** `print(solution.get_error_message())` 和 `print(solution.get_infeasible_orders().to_list())` 以查看哪些订单不可行。

**数据类型：** 使用显式数据类型（float32, int32）为矩阵和系列，以避免静默错误。

## 示例

- [examples.md](references/examples.md) — VRP、PDP、多仓库
- [server_examples.md](references/server_examples.md) — REST 客户端（curl、Python）
- **参考模型：** 此功能的 `assets/` — [vrp_basic](assets/vrp_basic/)、[pdp_basic](assets/pdp_basic/)。参见 [assets/README.md](assets/README.md)。

## 升级

对于贡献或从源代码构建，请参阅开发者功能。
