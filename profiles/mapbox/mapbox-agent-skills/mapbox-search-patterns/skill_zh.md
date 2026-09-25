# Mapbox 搜索模式技能

为 AI 助手使用 Mapbox 搜索工具提供专业指导。涵盖工具选择、参数优化以及地理编码、兴趣点搜索和位置发现的最佳实践。

## 可用搜索工具

### 1. search_and_geocode_tool

**最适合：** 具体地点、地址、品牌、命名位置

**在以下情况下使用：**

- 包含具体名称："星巴克在第五大道"、"帝国大厦"
- 品牌名称："麦当劳"、"全食超市"
- 地址："西雅图主街 123 号"、"时代广场 1 号"
- 连锁店："塔吉特"
- 城市/地点："旧金山"、"波特兰"

**不适用于：** 泛类目（"咖啡店"、"博物馆"）

### 2. category_search_tool

**最适合：** 泛类地点类型、类目、复数查询

**在以下情况下使用：**

- 泛类目："咖啡店"、"餐厅"、"加油站"
- 复数形式："博物馆"、"酒店"、"公园"
- "是"短语："任何咖啡店"、"所有餐厅"、"附近的药店"
- 行业术语："电动汽车充电器"、"自动取款机"

**不适用于：** 具体名称或品牌

### 3. reverse_geocode_tool

**最适合：** 将坐标转换为地址、城市、城镇、邮政编码

**在以下情况下使用：**

- 拥有 GPS 坐标，需要人类可读地址
- 需要识别特定位置有什么
- 将用户位置转换为地址

## 工具选择决策矩阵

| 用户查询                      | 工具                    | 理由                |
| ------------------------------- | ----------------------- | ------------------------ |
| "查找主街上的星巴克"          | search_and_geocode_tool | 具体品牌名称      |
| "查找附近的咖啡店"      | category_search_tool    | 泛类目，复数      |
| "37.7749, -122.4194" 处有什么 | reverse_geocode_tool    | 坐标到地址   |
| "帝国大厦"         | search_and_geocode_tool | 具体命名 POI       |
| "西雅图市中心酒店"    | category_search_tool    | 泛类型 + 位置  |
| "塔吉特商店位置"        | search_and_geocode_tool | 品牌名称（即使是复数） |
| "任何附近的餐厅"        | category_search_tool    | 泛 + "任何" 短语   |
| "波士顿主街 123 号"       | search_and_geocode_tool | 具体地址         |
| "电动汽车充电器"     | category_search_tool    | 行业类目        |
| "麦当劳"                    | search_and_geocode_tool | 品牌名称               |

## 参数指导

### Proximity vs Bbox vs Country

**三种空间约束搜索结果的方法：**

#### 1. proximity (强烈推荐)

**作用：** 倾向于某个位置的结果，但不排除远距离匹配

**在以下情况下使用：**

- 用户说 "near me"、"nearby"、"close to"
- 拥有参考点但希望有一定灵活性
- 希望按与点的相关性排序结果

**示例：**

```json
{
  "q": "pizza",
  "proximity": {
    "longitude": -122.4194,
    "latitude": 37.7749
  }
}
```

**为什么有效：** API 首先返回旧金山的披萨店，但如果与纽约市著名披萨店高度相关，可能会包含

**关键：** 拥有参考位置时，始终设置 proximity！没有它，结果是基于 IP 或全局的。

#### 2. bbox (边界框)

**作用：** 严格约束 - 仅返回框内的结果

**在以下情况下使用：**

- 用户指定区域："在市中心"、"在这个社区内"
- 拥有定义的服务区域
- 需要保证结果在边界内

**示例：**

```json
{
  "q": "hotel",
  "bbox": [-122.51, 37.7, -122.35, 37.83] // [minLon, minLat, maxLon, maxLat]
}
```

**为什么有效：** 保证所有酒店都在旧金山的市中心区域

**注意：** 太小 = 无结果；太大 = 无关结果

#### 3. country

**作用：** 限制结果到特定国家

**在以下情况下使用：**

- 用户指定国家："法国的餐厅"
- 构建国家特定功能
- 需要尊重区域边界
- 或明确表示希望特定国家的结果

**示例：**

```json
{
  "q": "Paris",
  "country": ["FR"] // ISO 3166 alpha-2 代码
}
```

**为什么有效：** 查找法国巴黎（不是德克萨斯州巴黎）

**可以组合：** `proximity` + `country` + `bbox` 或任意三种的组合

### 空间过滤器决策矩阵

| 场景                           | 使用                                 | 原因                               |
| ---------------------------------- | ----------------------------------- | --------------------------------- |
| "查找附近的咖啡"              | proximity                           | 倾向于用户位置         |
| "市中心西雅图咖啡店"            | proximity + bbox                    | 中心在市中心，限制在区域 |
| "法国的酒店"                 | country                             | 严格的国界             |
| "旧金山的最佳披萨"            | proximity + country ["US"]          | 倾向于旧金山，限制在 US |
| "沿此路线的加油站"            | bbox around route                   | 严格约束到路线走廊 |
| "5 英里内的餐厅"       | proximity (然后按距离过滤)          | 倾向附近，过滤结果       |

### 设置 limit 参数

**category_search_tool 仅限** (1-25, 默认 10)

| 用例              | Limit | 理由               |
| --------------------- | ----- | ----------------------- |
| 快速建议     | 5     | 快速，专注的结果   |
| 标准列表         | 10    | 默认，良好平衡   |
| 全面搜索  | 25    | 最大允许         |
| 地图可视化     | 25    | 显示所有附近选项 |
| 下拉/自动完成 | 5     | 不要让 UI 混乱      |

**性能提示：** 较低的 limit = 更快的响应

### types 参数 (search_and_geocode_tool)

**按特征类型过滤：**

| 类型       | 包含内容                           | 使用时                          |
| ---------- | ------------------------------------------ | --------------------------------- |
| `poi`      | 兴趣点（企业、地标）                 | 查找兴趣点，不是地址           |
| `address`  | 街道地址                           | 需要具体地址             |
| `place`    | 城市、社区、地区             | 查找区域/地区           |
| `street`   | 不带数字的街道名称               | 需要街道，不是具体地址       |
| `postcode` | 邮政编码                               | 按邮编搜索             |
| `district` | 区、社区                           | 基于区域搜索                 |
| `locality` | 镇、村庄                            | 市镇搜索             |
| `country`  | 国家名称                              | 国家级搜索              |

**示例组合：**

```json
// 仅 POI 和地址，不包括城市
{"q": "Paris", "types": ["poi", "address"]}
// 返回巴黎酒店、巴黎街道，不包括巴黎，法国

// 仅城市
{"q": "Paris", "types": ["place"]}
// 返回巴黎，法国；巴黎，德克萨斯州；等
```

**默认行为：** 包含所有类型（通常是你想要的）

### auto_complete 参数 (search_and_geocode_tool)

**作用：** 启用部分/模糊匹配

| 设置           | 行为                     | 使用时                      |
| ----------------- | ---------------------------- | ----------------------------- |
| `true`            | 匹配部分单词、拼写错误 | 用户实时输入      |
| `false` (默认) | 精确匹配               | 最终查询，不是自动完成 |

**示例：**

<!-- cspell:disable -->

```json
// 用户输入 "starb"
{ "q": "starb", "auto_complete": true }
// 返回：星巴克，星港酒馆，等
```

**用于：**

- 搜索时输入界面
- 处理拼写错误（"mcdonalds" -> McDonald's）
<!-- cspell:enable -->
- 不完整的查询

**不用于：**

- 最终/提交的查询（不够精确）
- 需要精确匹配时

## 应避免的反模式

### 不要：使用 category_search for 品牌名称

```javascript
// BAD
category_search_tool({ category: 'starbucks' });
// "starbucks" 不是类目，返回错误

// GOOD
search_and_geocode_tool({ q: 'Starbucks' });
```

### 不要：使用 search_and_geocode for 泛类目

```javascript
// BAD
search_and_geocode_tool({ q: 'coffee shops' });
// 不够精确，可能返回无关结果

// GOOD
category_search_tool({ category: 'coffee_shop' });
```

### 不要：本地搜索时忘记 proximity

```javascript
// BAD - 结果可能全球任何地方
category_search_tool({ category: 'restaurant' });

// GOOD - 倾向于用户位置
category_search_tool({
  category: 'restaurant',
  proximity: { longitude: -122.4194, latitude: 37.7749 }
});
```

### 不要：没有 proximity 就地理编码模糊位置名称（REST too）

这适用于 Mapbox 地理编码 API v5 / 浏览器应用中的搜索框 — 不仅是 MCP 工具。

```javascript
// BAD — limit=1 没有proximity 可能将 "林肯纪念堂" 解析为伊利诺伊州
fetch(`https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(q)}.json?access_token=${token}&limit=1`);

// GOOD — 倾向于地图中心（可选 bbox）
fetch(
  `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(q)}.json` +
    `?access_token=${token}&proximity=-77.0369,38.9072&bbox=-77.15,38.79,-76.90,38.99&limit=1`
);
```

还应该对搜索输入进行防抖（`clearTimeout` + `setTimeout`），这样每个按键不会触发一次地理编码。

### 不要：使用 bbox 而不是 proximity

```javascript
// BAD - 严格边界可能排除好的附近结果
search_and_geocode_tool({
  q: 'pizza',
  bbox: [-122.42, 37.77, -122.41, 37.78] // 微小的框
});

// GOOD - 倾向于点，但灵活
search_and_geocode_tool({
  q: 'pizza',
  proximity: { longitude: -122.4194, latitude: 37.7749 }
});
```

### 不要：不必要地请求 ETA

```javascript
// BAD - 花费 API 配额进行路线计算
search_and_geocode_tool({
  q: 'museums',
  eta_type: 'navigation',
  navigation_profile: 'driving'
});
// 用户没有要求旅行时间！

// GOOD - 只有在需要时才添加 ETA
search_and_geocode_tool({ q: 'museums' });
// 如果用户问"去那里要多长时间"，然后添加 ETA
```

### 不要：为 UI 显示设置过高的 limit

```javascript
// BAD - 对简单的下拉列表过于庞大
category_search_tool({
  category: 'restaurant',
  limit: 25
});
// 返回 25 家餐厅，用于 5 项下拉列表

// GOOD - 满足 UI 需求
category_search_tool({
  category: 'restaurant',
  limit: 5
});
```

## 快速参考

### 工具选择流程图

```
用户查询包含...

-> 具体名称/品牌 (Starbucks, Empire State Building)
  -> search_and_geocode_tool

-> 泛类/复数 (coffee shops, museums, any restaurant)
  -> category_search_tool

-> 坐标 -> 地址
  -> reverse_geocode_tool

-> 地址 -> 坐标
  -> search_and_geocode_tool with types: ["address"]
```

### 基本参数检查清单

**对于本地搜索，始终设置：**

- `proximity` (或 bbox 如果需要严格边界)

**对于类目搜索，考虑：**

- `limit` (匹配 UI 需求)
- `format` (json_string 如果要在地图上绘制)

**对于歧义，使用：**

- `country` (当地理上下文重要时)
- `types` (当特征类型重要时)

**对于旅行时间排序：**

- `eta_type`, `navigation_profile`, `origin` (花费 API 配额)

## 常见错误

1. **忘记 proximity** -> 结果是全球/IP-based（或模糊纪念堂/公园名称的错误州）
2. **使用错误工具** -> category_search for "Starbucks" (使用 search_and_geocode)
3. **无效类目** -> 首先检查 category_list
4. **bbox 太小** -> 无结果；使用 proximity 代替
5. **不必要地请求 ETA** -> 增加API成本
6. **limit 太高 for UI** -> 让用户不知所措
7. **不过滤类型** -> 获取城市时你想要兴趣点
8. **没有防抖 typeahead** -> 配额消耗和竞争性 UI

## 参考文件

加载这些以获取特定主题的更深入指导：

- **`references/advanced-params.md`** — poi_category, ETA, format, 和语言参数
- **`references/workflows.md`** — 常见模式：Near Me, 品牌化, 地理编码, 类目+区域, 反向, 基于路线, 多语言
- **`references/optimization-combining.md`** — 性能优化, 组合工具, 处理无结果, 类目列表资源
