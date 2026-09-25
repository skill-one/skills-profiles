# Google Flights 搜索

通过代理浏览器搜索 Google Flights，查找航班价格、时刻表和可用性。

## 使用场景

- 用户询问搜索/查找/比较航班或机票
- 用户想了解城市间的航班价格
- 用户询问航班时刻表或可用性
- 用户想为特定日期找到最便宜的航班

## 不适用场景

- **完成购买**：此技能查找航班并提取预订链接，但不要尝试在预订网站上完成购买。
- **酒店/租车**：使用其他工具进行非航班旅行搜索。
- **历史价格数据**：Google Flights 显示当前价格，不显示历史价格。

## 会话约定

- **经济舱仅限**（国内默认）：`--session flights`
- **经济舱+商务舱比较**（国际或用户请求）：`--session econ` 和 `--session biz`
- **交互式回退**：`--session flights`

## 国内与国际检测

**国内航班默认仅经济舱。** 美国国内航线上的商务舱通常价格是经济舱的 3-5 倍，除非询问，否则通常不值得显示。

如果起点和终点都是美国机场，则航班为**国内航班**。常见的美国 IATA 代码：ATL、BOS、BWI、CLT、DEN、DFW、DTW、EWR、FLL、HNL、IAD、IAH、JFK、LAS、LAX、LGA、MCO、MDW、MIA、MSP、OAK、ORD、PHL、PHX、PDX、SAN、SEA、SFO、SJC、SLC、TPA。

**何时显示商务舱：**
- 国际航班（始终显示经济舱+商务舱比较）
- 用户明确要求“商务舱”或“商务”
- 用户询问“比较舱位”或“显示所有舱位”

**何时跳过商务舱：**
- 美国国内航班（默认仅经济舱）
- 用户明确要求“经济舱”或“最便宜”

## 快速路径：基于 URL 的搜索（首选）

使用自然语言的 `?q=` 参数构建 URL。直接加载结果 — **总共 3 个命令**。

### URL 模板

```
https://www.google.com/travel/flights?q=Flights+from+{ORIGIN}+to+{DEST}+on+{DATE}[+returning+{DATE}][+one+way][+business+class][+N+passengers]
```

### 默认：经济舱仅限（国内）

对于国内航班，运行单个会话 - **总共 2 个工具调用**：

```bash
# 在一个调用中打开并等待
agent-browser --session flights open "https://www.google.com/travel/flights?q=Flights+from+MIA+to+SFO+on+2026-04-28+returning+2026-04-30" && agent-browser --session flights wait --load networkidle

# 快照结果
agent-browser --session flights snapshot -i
# 保持会话活动以获取预订链接
```

然后以**紧凑列表格式**呈现结果（见输出格式部分）。

### 经济舱+商务舱比较（国际）

对于国际航班，运行两个并行会话以显示价格差异：

```bash
# 并行打开并等待
(agent-browser --session econ open "https://www.google.com/travel/flights?q=Flights+from+BKK+to+NRT+on+2026-03-20+returning+2026-03-27" && agent-browser --session econ wait --load networkidle) &
(agent-browser --session biz open "https://www.google.com/travel/flights?q=Flights+from+BKK+to+NRT+on+2026-03-20+returning+2026-03-27+business+class" && agent-browser --session biz wait --load networkidle) &
wait

# 并行快照
agent-browser --session econ snapshot -i &
agent-browser --session biz snapshot -i &
wait

# 关闭 biz（仅用于差异）；保持 econ 活动以获取预订链接
agent-browser --session biz close
```

**匹配逻辑**：通过航空公司名称和出发时间匹配航班。并非所有经济舱航班都有商务舱对应（廉价航空公司如 ZIPAIR、Air Japan 不提供商务舱）。商务舱不存在时显示 "-"。

**提示**：当航空公司出现在商务舱结果中但不在经济舱中（例如，菲律宾航空）时，该航线可能仅提供商务舱定价。经济舱中包含 "-"。

### 单程

在 URL 中添加 `+one+way`。对于国际航班，并行运行经济舱和商务舱：

```bash
# 国内（经济舱仅限）
agent-browser --session flights open "https://www.google.com/travel/flights?q=Flights+from+LAX+to+JFK+on+2026-04-15+one+way" && agent-browser --session flights wait --load networkidle

# 国际（经济舱+商务舱比较）
(agent-browser --session econ open "https://www.google.com/travel/flights?q=Flights+from+LAX+to+LHR+on+2026-04-15+one+way" && agent-browser --session econ wait --load networkidle) &
(agent-browser --session biz open "https://www.google.com/travel/flights?q=Flights+from+LAX+to+LHR+on+2026-04-15+one+way+business+class" && agent-browser --session biz wait --load networkidle) &
wait
```

### 用户要求仅商务舱

如果用户明确要求商务舱（不是比较），运行仅商务舱会话：

```bash
agent-browser --session flights open "https://www.google.com/travel/flights?q=Flights+from+JFK+to+CDG+on+2026-06-01+returning+2026-06-15+business+class"
agent-browser --session flights wait --load networkidle
agent-browser --session flights snapshot -i
# 保持会话活动以获取预订链接
```

### 头等舱/多个乘客

```bash
agent-browser --session flights open "https://www.google.com/travel/flights?q=Flights+from+JFK+to+CDG+on+2026-06-01+returning+2026-06-15+first+class+2+adults+1+child"
agent-browser --session flights wait --load networkidle
agent-browser --session flights snapshot -i
# 保持会话活动以获取预订链接
```

### URL 支持的功能

| 功能 | URL 语法 | 状态 |
|------|---------|------|
| 往返 | `+returning+YYYY-MM-DD` | 支持 |
| 单程 | `+one+way` | 支持 |
| 商务舱 | `+business+class` | 支持 |
| 头等舱 | `+first+class` | 支持 |
| N 位乘客（成人） | `+N+passengers` | 支持 |
| 成人+儿童 | `+2+adults+1+child` | 支持 |
| IATA 代码 | `BKK`, `NRT`, `LAX` | 支持 |
| 城市名称 | `Bangkok`, `Tokyo` | 支持 |
| 日期格式为 YYYY-MM-DD | `2026-03-20` | 支持（最佳） |
| 自然日期 | `March+20` | 支持 |
| **高级经济舱** | `+premium+economy` | **不支持** |
| **多点往返** | N/A | **不支持** |

### 需要交互式回退的功能

- **高级经济舱**舱位等级
- **多点往返**旅行（3 趟以上）
- **婴儿乘客**（座位与抱膝区别）
- **URL 未加载结果**（同意横幅、验证码、区域问题）

### 从快照中读取结果

每个航班都显示为带有完整描述的 `link` 元素：

```
link "From 20508 泰铢往返总价。直飞航班，由 Air Japan 执飞。
     周五凌晨 12:10 从素万那普机场出发，抵达成田国际机场的时间为周五上午 8:15。
     总飞行时间 6 小时 5 分钟。选择航班"
```

将经济舱+商务舱快照解析为**紧凑列表格式**：

```
1. JAL — 直飞 · 5h 55m
   8:05 AM → 4:00 PM
   经济舱: THB 23,255 · 商务舱: THB 65,915 (+183%)

2. THAI — 直飞 · 5h 50m
   10:30 PM → 6:20 AM+1
   经济舱: THB 28,165 · 商务舱: THB 75,000 (+166%)

3. Air Japan — 直飞 · 6h 05m
   12:10 AM → 8:15 AM
   经济舱: THB 20,515 · 商务舱:—

4. ZIPAIR — 直飞 · 5h 45m
   11:45 PM → 7:30 AM+1
   经济舱: THB 21,425 · 商务舱: —
```

**匹配**：通过航空公司+出发时间匹配经济舱和商务舱结果。没有商务舱的廉价航空公司显示 "—"。包含来自 Google 的 "最佳"/"最便宜" 标签。

## 预订选项交接

在呈现结果表格后，**始终提供预订链接**： "需要这些航班的预订链接吗？只需说哪个航班。"

当用户选择航班时，通过点击快照中航班的 `link` 元素提取预订选项。Google Flights 显示一个包含预订提供商（航空公司、OTA）的面板，每个提供商都有价格和指向预订网站的“继续”链接。

### 工作流程

```bash
# 用户选择第 N 个航班 — 点击结果快照中的相应链接
# 使用 --session flights（国内）或 --session econ（国际比较）
agent-browser --session flights click @eN
agent-browser --session flights wait 3000
agent-browser --session flights snapshot -i
```

预订面板快照将显示 `link` 元素，例如：

```
link "预订 Emirates THB 28,960" → href="https://..."
link "预订 Booking.com THB 29,512" → href="https://..."
link "预订 Teaflight THB 28,171" → href="https://..."
```

从每个链接中提取提供商名称、价格和 `href` URL。

### 输出格式

```
📋 JAL BKK→NRT (5h 55m, 直飞) 的预订选项

| 提供商 | 价格 | 继续 |
|--------|------|------|
| Emirates | THB 28,960 | [继续](https://...) |
| Booking.com | THB 29,512 | [继续](https://...) |
| Teaflight | THB 28,171 | [继续](https://...) |
```

### 注意事项

- **会话生命周期**：保持结果会话（`flights` 或 `econ`）活动以获取预订链接。对于国际比较，立即关闭 `--session biz`。在用户获取预订链接或拒绝后关闭结果会话。
- **如果预订面板加载失败**：重新快照并稍后重试。

## 交互式工作流程（回退）

用于多点往返、高级经济舱或 URL 路径失败时。

### 打开和快照

```bash
agent-browser --session flights open "https://www.google.com/travel/flights"
agent-browser --session flights wait 3000
agent-browser --session flights snapshot -i
```

如果出现同意横幅，首先点击“接受所有”或“拒绝所有”。

### 设置旅行类型（如果不是往返）

```bash
agent-browser --session flights click @eN   # 旅行类型下拉框（"往返"）
agent-browser --session flights snapshot -i
agent-browser --session flights click @eN   # "单程"或"多点往返"
agent-browser --session flights wait 1000
agent-browser --session flights snapshot -i
```

### 设置舱位等级/乘客（如果非默认）

**舱位等级：**
```bash
agent-browser --session flights click @eN   # 舱位等级下拉框
agent-browser --session flights snapshot -i
agent-browser --session flights click @eN   # 选择等级
agent-browser --session flights wait 1000
agent-browser --session flights snapshot -i
```

**乘客：**
```bash
agent-browser --session flights click @eN   # 乘客按钮
agent-browser --session flights snapshot -i
agent-browser --session flights click @eN   # "+"用于成人/儿童/婴儿
agent-browser --session flights snapshot -i
agent-browser --session flights click @eN   # "完成"
agent-browser --session flights wait 1000
agent-browser --session flights snapshot -i
```

### 输入机场（起点或终点）

```bash
agent-browser --session flights click @eN   # 下拉框字段
agent-browser --session flights wait 1000
agent-browser --session flights snapshot -i
agent-browser --session flights fill @eN "BKK"
agent-browser --session flights wait 2000   # 关键：等待自动完成
agent-browser --session flights snapshot -i
agent-browser --session flights click @eN   # 点击建议（永远不要按 Enter）
agent-browser --session flights wait 1000
agent-browser --session flights snapshot -i
```

### 设置日期

```bash
agent-browser --session flights click @eN   # 日期文本框
agent-browser --session flights wait 1000
agent-browser --session flights snapshot -i
# 日历显示日期为按钮："周五，2026年3月20日"
agent-browser --session flights click @eN   # 点击目标日期
agent-browser --session flights wait 500
agent-browser --session flights snapshot -i
# 点击“完成”关闭日历
agent-browser --session flights click @eN   # “完成”按钮
agent-browser --session flights wait 1000
agent-browser --session flights snapshot -i
```

### 搜索

**“完成”仅关闭日历。你必须单独点击“搜索”。**

```bash
agent-browser --session flights click @eN   # “搜索”按钮
agent-browser --session flights wait --load networkidle
agent-browser --session flights snapshot -i
# 保持会话活动以获取预订链接
```

### 多点往返特定细节

选择“多点往返”旅行类型后，表单显示每趟航程的一行：

- 每趟航程都有：起点下拉框、终点下拉框、出发日期文本框
- 每趟航程的起点自动填充为上一趟航程的终点
- 点击“添加航程”按钮添加更多航程（默认显示 2 趟航程）
- 点击“删除 X 到 Y 的航程”按钮删除航程
- 结果显示第一趟航程的航班，价格反映**整个多点往返的总成本**

按顺序填写每趟航程的终点+日期，然后点击“搜索”。

## 输出格式

**始终使用紧凑列表格式** — 永远不要使用 Markdown 表格。输出通常在聊天机器人界面（如 Telegram 等）中显示，表格渲染效果不佳。

### 经济舱+商务舱比较（默认）

```
1. JAL — 直飞 · 5h 55m
   8:05 AM → 4:00 PM
   经济舱: THB 23,255 · 商务舱: THB 65,915 (+183%)

2. THAI — 直飞 · 5h 50m
   10:30 PM → 6:20 AM+1
   经济舱: THB 28,165 · 商务舱: THB 75,000 (+166%)

3. Air Japan — 直飞 · 6h 05m
   12:10 AM → 8:15 AM
   经济舱: THB 20,515 · 商务舱: —
```

### 经济舱仅限

```
1. JAL — 直飞 · 5h 55m
   8:05 AM → 4:00 PM · THB 23,255

2. THAI — 直飞 · 5h 50m
   10:30 PM → 6:20 AM+1 · THB 28,165
```

### 格式规则

- 每个航班一个编号块，航班之间空一行
- 行 1：航空公司 — 停靠点 · 飞行时间
- 行 2：出发 → 到达时间
- 行 3：价格（经济舱，商务舱差异如果适用）
- 不要在航班列表周围使用代码块 — 纯文本阅读最佳
- 保留“最佳价值”建议为纯文本段落，列表之后

## 关键规则

| 规则 | 原因 |
|------|------|
| 优先使用 URL 快速路径 | 2 个工具调用（国内）或 3 个（国际）vs 15+ 交互式 |
| 使用 `&&` 链接 open+wait | 消除工具调用之间的往返 |
| 国内航班跳过商务舱 | 美国国内商务舱是经济舱的 3-5 倍，除非询问，否则通常不值得显示 |
| 使用 `&` + `wait` 并行快照 | 两个快照并行运行国际航班 |
| `wait --load networkidle` | 比固定 `wait 5000` 更智能 - 当网络稳定时返回 |
| 使用 `fill` 而不是 `type` 输入机场 | 首先清除现有文本 |
| 输入机场代码后等待 2 秒 | 自动完成需要 API 循环 |
| 始终点击建议，永远不要按 Enter | Enter 对于自动完成不可靠 |
| 每次交互后重新快照 | DOM 变化使引用失效 |
| “完成”≠ 搜索 | 日历“完成”仅关闭选择器 |
| 呈现结果后，提供预订链接 | 用户几乎总是想预订 - 提示他们 |
| 保持结果会话活跃；关闭 `biz` 后呈现结果 | 结果会话需要预订点击；biz 仅用于差异 |

## 故障排除

**同意横幅**：在快照中点击“接受所有”或“拒绝所有”。

**URL 快速路径未工作**：回退到交互式。某些地区/区域处理 `?q=` 不同。

**无结果**：验证机场（检查下拉框标签）、日期在未来或等待更长时间。

**机器人检测 / 验证码**：通知用户。不要解决验证码。稍后重试。
