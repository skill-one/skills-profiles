# Mapbox 地理空间操作技能

为 AI 助手提供选择 Mapbox MCP 服务器中合适地理空间工具的专业指导。重点在于根据**问题需求**选择工具——几何计算与路由、直线与道路网络、以及精度需求。

## 核心原则：问题类型决定工具选择

Mapbox MCP 服务器提供两类地理空间工具：

1. **离线几何工具** - 使用 Turf.js 进行纯几何/空间计算
2. **路由与导航 API** - 当您需要现实世界路由、交通或旅行时间时使用 Mapbox API

**关键问题：问题实际需要什么？**

### 决策框架

| 问题特征                                 | 工具类别     | 原因                                      |
| -------------------------------------- | ----------------- | ---------------------------------------- |
| **直线距离**（鸟飞距离）         | 离线几何     | 准确的几何距离                          |
| **道路/路径距离**（鸟驾车距离）            | 路由 API       | 只有路由 API 知道道路网络             |
| **旅行时间**                                        | 路由 API       | 需要带速度/交通数据的路由              |
| **点包含**（X 是否在 Y 内？）                 | 离线几何     | 纯几何操作                             |
| **地理形状**（缓冲区、中心点、区域）      | 离线几何     | 数学/几何操作                          |
| **交通感知路由**                              | 路由 API       | 需要实时交通数据                      |
| **路径优化**（最佳访问顺序）           | 路由 API       | 复杂的路由算法                          |
| **高频检查**（例如，实时地理围栏） | 离线几何     | 即时响应，无延迟                     |

## 按用例划分的决策矩阵

### 距离计算

**用户询问：“X 和 Y 之间的距离是多少？”**

| 他们实际想表达的意思                            | 工具选择                         | 原因                                      |
| -------------------------------------------------- | ----------------------------------- | ---------------------------------------- |
| 直线距离（鸟飞距离）         | `distance_tool`                     | 准确的几何距离，即时                    |
| 驾车距离（鸟驾车距离）              | `directions_tool`                   | 只有路由知道实际道路距离                  |
| 步行/骑行距离（鸟步行/骑行） | `directions_tool`                   | 需要特定的路径网络                     |
| 旅行时间                                        | `directions_tool` 或 `matrix_tool`  | 需要带速度数据的路由                    |
| 带当前交通的距离                      | `directions_tool` (driving-traffic) | 需要实时交通考虑                       |

**示例：“这 5 个仓库之间的距离是多少？”**

- 鸟飞距离 → `distance_tool`（10 次计算，即时）
- 鸟驾车距离 → `matrix_tool`（5×5 矩阵，一个 API 调用，返回实际路线距离）

**关键洞察：** 使用与“距离”在上下文中含义匹配的工具。始终澄清：鸟飞还是鸟驾车？

### 邻近性和包含

**用户询问：“哪些点靠近/在这个区域内？”**

| 查询类型                   | 工具选择                                           | 原因                                                           |
| ---------------------------- | ----------------------------------------------------- | ------------------------------------------------------------- |
| “X 米半径内”     | `distance_tool` + 过滤                              | 简单几何半径                                                   |
| “X 分钟车程内”     | `isochrone_tool` → `point_in_polygon_tool`            | 需要路由的旅行时间区域，然后几何包含                         |
| “在这个多边形内”        | `point_in_polygon_tool`                               | 纯几何包含测试                                               |
| “驾车 30 分钟可达” | `isochrone_tool`                                      | 需要路由 + 交通                                              |
| “最近的点”      | `distance_tool` (几何) 或 `matrix_tool` (路由) | 取决于“最近”的定义                                            |

**示例：“这 200 个地址是否在我们的 30 分钟配送区内？”**

1. 创建区域 → `isochrone_tool`（路由 API - 需要旅行时间）
2. 检查地址 → `point_in_polygon_tool`（几何 - 200 次即时检查）

**关键洞察：** 路由用于创建旅行时间区域，几何用于包含检查

### 路由与导航

**用户询问：“最佳路线是什么？”**

| 情景                            | 工具选择                         | 原因                               |
| ----------------------------------- | ----------------------------------- | --------------------------------- |
| A 到 B 路线指示                   | `directions_tool`                   | 转向导航                          |
| 多个停靠点的最佳顺序             | `optimization_tool`                 | 解决旅行商问题                    |
| 干净的 GPS 轨迹                   | `map_matching_tool`                 | 锚定到道路网络                   |
| 只需要朝向/指南针方向             | `bearing_tool`                      | 简单几何计算                      |
| 带交通的路由                      | `directions_tool` (driving-traffic) | 实时交通感知                      |
| 固定顺序航点                     | `directions_tool` with waypoints    | 路由通过特定点                   |

**示例：“从酒店导航到机场”**

- 需要转向导航 → `directions_tool`
- 只需要知道“它在东北方向” → `bearing_tool`

**关键洞察：** 路由工具用于实际导航，几何工具用于方向信息

### 面积和形状操作

**用户询问：“围绕这个位置创建一个区域”**

| 需求               | 工具选择      | 原因                      |
| ------------------------- | ---------------- | ------------------------ |
| 简单圆形缓冲区    | `buffer_tool`    | 几何圆/半径              |
| 旅行时间区域          | `isochrone_tool` | 基于路由网络              |
| 计算区域大小       | `area_tool`      | 几何计算                  |
| 简化复杂边界       | `simplify_tool`  | 几何简化                  |
| 找到形状中心      | `centroid_tool`  | 几何中心                  |

**示例：“在每个商店周围显示 5 公里覆盖范围”**

- 5 公里半径 → `buffer_tool`（几何圆）
- “客户在 15 分钟内能到达什么？” → `isochrone_tool`（基于路由）

**关键洞察：** 几何工具用于距离型区域，路由工具用于时间型区域

## 性能和规模考虑

### 当数量影响工具选择时

**小操作（< 100 次计算）：**

- 几何工具：即时，可自由迭代
- 路由 API：足够快，适用于大多数用途

**中等操作（100-1,000 次计算）：**

- 几何工具：仍然快速，无需担忧
- 路由 API：考虑批量操作（matrix_tool）

**大操作（> 1,000 次计算）：**

- 几何工具：可能需要优化但仍然快速
- 路由 API：绝对使用批量工具（matrix_tool 处理高达 25×25）

**关键洞察：** 数量很少影响几何工具的选择，但路由 API 有批量工具以提高效率

### 实时与批量

| 用例                            | 方法             | 工具选择                              |
| ----------------------------------- | -------------------- | ---------------------------------------- |
| 实时地理围栏（每秒）             | 几何检查     | `point_in_polygon_tool` (即时)        |
| 路线规划（一次性）           | 全部路由         | `directions_tool` 或 `optimization_tool` |
| 定期邻近检查           | 几何距离   | `distance_tool`                          |
| 实时交通路由                | 路由与交通     | `directions_tool` (driving-traffic)      |

**架构说明：高频地理围栏** 如果应用程序以非常高的频率调用包含检查（例如，每 2 秒 50 辆车 = 每秒 25 次检查），通过网络调用 MCP 工具会增加代理推理开销，使其不切实际。在这种情况下，建议在进程内直接使用 Turf.js（`turf.booleanPointInPolygon`）处理热点路径，并将 MCP 工具保留用于外围任务，如区域定义（`isochrone_tool`）、重新路由（`directions_tool`）或可视化（`static_map_image_tool`）。

## 常见场景和最佳方法

### 场景 1：商店定位器

**用户：“找到最近的商店并显示 5 公里覆盖范围”**

**最佳方法：**

1. 搜索商店 → `category_search_tool`（自动返回距离）
2. 创建覆盖区域 → `buffer_tool`（5 公里几何圆）
3. 可视化 → `static_map_image_tool`

**原因：** 搜索已提供距离；几何缓冲区用于简单半径

### 场景 2：配送路线优化

**用户：“优化 8 个地址/停靠点的配送”**

**最佳方法：**

1. **地址地理编码（如果需要）** → 使用 `search_and_geocode_tool` 将任何街道地址转换为坐标。即使已提供坐标，也提及此为可选预处理步骤——现实世界的配送列表通常包含地址和坐标的混合。

2. **优化路线** → `optimization_tool`（旅行商问题求解器——重新排序停靠点以最小化总行驶时间）

**为什么 `optimization_tool` 而不是这些替代方案：**

- **`directions_tool`** 仅路由 A → B（或通过固定顺序的航点）。它**不**重新排序停靠点——如果您传递 8 个停靠点，它将按给定顺序路由它们，这几乎从不最优。
- **`matrix_tool`** 提供所有停靠点对之间的旅行时间（8×8 = 64 个值），但它**不**计算最佳排序。您需要在矩阵之上自己解决 TSP——`optimization_tool` 为您在单个调用中完成。

始终提及 `search_and_geocode_tool` 作为在优化配送地址之前进行地理编码的有用辅助工具。

### 场景 3：服务区域验证

**用户：“哪些地址可以在 30 分钟内配送？”**

**最佳方法：**

1. 创建配送区域 → `isochrone_tool`（30 分钟驾驶）
2. 检查每个地址 → `point_in_polygon_tool`（200 次几何检查）

**原因：** 路由用于准确旅行时间区域，几何用于快速包含检查

### 场景 4：GPS 轨迹分析

**用户：“这次骑行多长？”**

**最佳方法：**

1. 清理 GPS 轨迹 → `map_matching_tool`（锚定到自行车道）
2. 获取距离 → 使用 API 响应或使用 `distance_tool` 计算

**原因：** 需要道路/路径匹配；距离计算无论哪种方式都有效

### 场景 5：覆盖分析

**用户：“我们的总服务区域是什么？”**

**最佳方法：**

1. 围绕每个位置创建缓冲区 → `buffer_tool`
2. 计算总面积 → `area_tool`
3. 或者，如果基于时间 → `isochrone_tool` 为每个位置

**原因：** 几何用于距离型覆盖，路由用于时间型

## 反模式：使用错误类型的工具

### ❌ 不要：使用几何工具进行路由问题

```javascript
// 错误：用户询问“开车有多远？”
distance_tool({ from: A, to: B });
// 返回 10 公里鸟飞距离，但实际驾驶是 15 公里

// 正确：需要路由的实际驾驶距离
directions_tool({
  coordinates: [
    { longitude: A[0], latitude: A[1] },
    { longitude: B[0], latitude: B[1] }
  ],
  routing_profile: 'mapbox/driving'
});
// 返回实际道路距离和鸟驾车时间
```

**原因：** 鸟飞距离 ≠ 鸟驾车距离

### ❌ 不要：使用路由 API 进行几何操作

```javascript
// 错误：检查点是否在多边形内
// （路由 API 无法执行此操作）

// 正确：纯几何操作
point_in_polygon_tool({ point: location, polygon: boundary });
```

**原因：** 路由 API 不执行几何包含

### ❌ 不要：混淆“邻近”与“可达”

```javascript
// 用户询问： “什么可以 20 分钟内到达？”

// 错误：20 分钟距离按平均速度计算
distance_tool + 计算 20min * avg_speed

// 正确：实际路由与道路网络
isochrone_tool({
  coordinates: {longitude: startLng, latitude: startLat},
  contours_minutes: [20],
  profile: "mapbox/driving"
})
```

**原因：** 道路不是直线；交通变化

### ❌ 不要：当只需要方向时使用路由

```javascript
// 用户询问： “机场的方向是哪个？”

// 过于复杂：完整路由
directions_tool({
  coordinates: [
    { longitude: hotel[0], latitude: hotel[1] },
    { longitude: airport[0], latitude: airport[1] }
  ]
});

// 更好：只需要方向
bearing_tool({ from: hotel, to: airport });
// 返回： “东北 (45°)”
```

**原因：** 更简单，即时，回答实际问题

## 混合方法：组合工具类型

某些问题受益于同时使用几何和路由工具：

### 模式 1：路由 + 几何过滤

```
1. directions_tool → 获取路线几何
2. buffer_tool → 在路线周围创建走廊
3. category_search_tool → 在走廊中查找 POI
4. point_in_polygon_tool → 过滤到实际沿路线的 POI
```

**用例：** “沿我的路线查找加油站”

### 模式 2：路由 + 距离计算

```
1. category_search_tool → 查找 10 个附近位置
2. distance_tool → 计算直线距离（几何）
3. 对于前三名，使用 directions_tool → 获取实际驾驶时间
```

**用例：** 快速缩小范围，然后对最终候选者进行精确路由

### 模式 3：Isochrone + 包含

```
1. isochrone_tool → 创建旅行时间区域（路由）
2. point_in_polygon_tool → 检查数百个地址（几何）
```

**用例：** “哪些客户在我们的配送区内？”

## 决策算法

当用户询问地理空间问题时：

```
1. 它是否需要路由、道路或旅行时间？
   是 → 使用路由 API（directions, matrix, isochrone, optimization）
   否 → 继续

2. 它是否需要交通感知？
   是 → 使用 directions_tool 或 isochrone_tool 带交通配置文件
   否 → 继续

3. 它是否是几何/空间操作？
   - 点之间的距离（直线） → distance_tool
   - 点包含 → point_in_polygon_tool
   - 面积计算 → area_tool
   - 缓冲区/区域 → buffer_tool
   - 方向/指南针 → bearing_tool
   - 几何中心 → centroid_tool
   - 范围框 → bbox_tool
   - 简化 → simplify_tool

4. 它是否是搜索/发现操作？
   是 → 使用搜索工具（search_and_geocode, category_search）
```

## 关键决策问题

选择工具之前，请询问：

1. **“距离”是指鸟飞还是鸟驾车？**
   - 鸟飞（直线）→ 几何工具
   - 鸟驾车（道路距离）→ 路由 API

2. **用户是否需要旅行时间？**
   - 是 → 路由 API（只有它们知道速度/交通）
   - 否 → 几何工具可能足够

3. **这是关于道路/路径还是纯空间关系？**
   - 道路/路径 → 路由 API
   - 空间关系 → 几何工具

4. **是否需要实时低延迟？**
   - 是 + 几何问题 → 离线工具（即时）
   - 是 + 路由问题 → 使用路由 API（仍然快速）

5. **精度是否关键，还是近似可以？**
   - 关键 + 路由 → 路由 API
   - 近似可以 → 几何工具可能有效

## 术语指南

理解用户的意思：

| 用户说             | 通常意味着                                      | 工具类型   |
| --------------------- | -------------------------------------------------- | ----------- |
| "距离"            | 上下文依赖！询问：鸟飞或鸟驾车？                | Varies      |
| "多远"             | 通常指鸟驾车（道路距离）                       | Routing API |
| "附近"              | 通常指鸟飞（直线半径）                       | Geometric   |
| "近"               | 可能是任何一种 - 澄清！                         | Ask         |
| "可达"           | 基于时间（鸟驾车带交通）                      | Routing API |
| "包含/在...内"     | 几何包含                                      | Geometric   |
| "导航/路线"         | 转向导航                                      | Routing API |
| "方向/指南针"   | 指南针方向（鸟飞）                           | Geometric   |

## 快速参考

### 几何操作（离线工具）

- `distance_tool` - 两点之间的直线距离
- `bearing_tool` - 从 A 到 B 的指南针方向
- `midpoint_tool` - 两点之间的中点
- `point_in_polygon_tool` - 点是否在多边形内？
- `area_tool` - 计算多边形面积
- `buffer_tool` - 创建圆形缓冲区/区域
- `centroid_tool` - 多边形的几何中心
- `bbox_tool` - 几何的最小/最大坐标
- `simplify_tool` - 减少几何复杂性

### 路由与导航（APIs）

- `directions_tool` - 转向导航
- `matrix_tool` - 多对多旅行时间
- `optimization_tool` - 路线优化（TSP）
- `isochrone_tool` - 旅行时间区域
- `map_matching_tool` - 锚定 GPS 到道路

### 每个类别何时使用

**使用几何工具时：**

- 问题具有空间/数学特性（包含、面积、指南针）
- 直线距离适用
- 需要即时结果用于实时检查
- 纯几何（不涉及道路/交通）

**使用路由 API 时：**

- 需要实际驾驶/步行/骑行距离
- 需要旅行时间
- 需要考虑道路网络
- 需要交通感知
- 需要路线优化
- 需要转向导航

## REST API 诚实（路线 / Isochrone）

在生成针对 Mapbox REST API 的浏览器演示（不仅是 MCP 工具）时：

### 路线 — 使用路线对象指标

```javascript
const route = data.routes[0];
// 好 — 来自 API 的米数 / 秒数
stats.textContent =
  `距离 ${(route.distance / 1000).toFixed(2)} 公里 · ` + `时长 ${Math.round(route.duration / 60)} 分钟`;

// 差 — 修饰性标签或硬编码的 ETA，看起来像工作演示
// "长度 0.00 公里 · 时间 2 分钟" / Math.round(120/60)
```

### Isochrone — 当提示要求多个轮廓时请求多个轮廓

```javascript
// 好 — 三个旅行时间带
`contours_minutes=15,30,60`;

// 差 — 当 UX 需要时使用单个轮廓
`contours_minutes=30`;
```

## 与其他技能的集成

**与：**

- **mapbox-search-patterns**：搜索位置，然后使用地理空间操作
- **mapbox-web-performance-patterns**：优化几何计算的渲染
- **mapbox-token-security**：确保请求使用正确范围的令牌

## 资源

- [Mapbox MCP 服务器](https://github.com/mapbox/mcp-server)
- [Turf.js 文档](https://turfjs.org/)（为几何工具提供支持）
- [Mapbox 路线 API](https://docs.mapbox.com/api/navigation/directions/)
- [Mapbox Isochrone API](https://docs.mapbox.com/api/navigation/isochrone/)
- [Mapbox Matrix API](https://docs.mapbox.com/api/navigation/matrix/)
- [Mapbox 优化 API](https://docs.mapbox.com/api/navigation/optimization/)
