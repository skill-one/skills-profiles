# 记忆搜索

跨所有会话搜索过往工作。工作流程简单：搜索 -> 筛选 -> 获取 -> （极少情况下）披露原始工具 I/O。

## 何时使用

当用户询问关于先前会话（而非当前对话）时使用：

- "我们已经修复过这个问题了吗？"
- "上次我们是如何解决 X 的？"
- "上周发生了什么？"

## 分层工作流程（必须始终遵循）

**绝不能在筛选之前获取完整详情。节省 10 倍的 token。**

### 第 1 步：搜索 - 获取带 ID 的索引

使用 `search` MCP 工具：

```
search(query="authentication", limit=20, project="my-project")
```

**返回：** 包含 ID、时间戳、类型、标题的表格 (~50-100 tokens/结果)

```
| ID | 时间 | T | 标题 | 已读 |
|----|------|---|-------|------|
| #11131 | 下午 3:48 | 🟣 | 添加 JWT 认证 | ~75 |
| #10942 | 下午 2:15 | 🔴 | 修复认证令牌过期 | ~50 |
```

**参数：**

- `query` (字符串) - 搜索词
- `limit` (数字) - 最大结果数，默认 20，最大 100
- `project` (字符串) - 项目名称筛选
- `type` (字符串，可选) - "observations"、"sessions" 或 "prompts"
- `obs_type` (字符串，可选) - 逗号分隔：bugfix、feature、decision、discovery、change
- `dateStart` (字符串，可选) - YYYY-MM-DD 或 epoch ms
- `dateEnd` (字符串，可选) - YYYY-MM-DD 或 epoch ms
- `offset` (数字，可选) - 跳过 N 个结果
- `orderBy` (字符串，可选) - "date_desc"（默认）、"date_asc"、"relevance"

### 第 2 步：时间线 - 获取围绕有趣结果的上下文

使用 `timeline` MCP 工具：

```
timeline(anchor=11131, depth_before=3, depth_after=3, project="my-project")
```

或自动从查询中找到锚点：

```
timeline(query="authentication", depth_before=3, depth_after=3, project="my-project")
```

**返回：** 按时间顺序排列的 `depth_before + 1 + depth_after` 个项目，其中包含围绕锚点的 observations、sessions 和 prompts 交错排列。

**参数：**

- `anchor` (数字，可选) - 中心化的 Observation ID
- `query` (字符串，可选) - 如果未提供锚点，则自动查找锚点
- `depth_before` (数字，可选) - 锚点前的项目数，默认 5，最大 20
- `depth_after` (数字，可选) - 锚点后的项目数，默认 5，最大 20
- `project` (字符串) - 项目名称筛选

### 第 3 步：获取 - 仅针对筛选后的 ID 获取完整详情

从第 1 步的标题和第 2 步的上下文中进行审查。选择相关 ID。丢弃其余部分。

使用 `get_observations` MCP 工具：

```
get_observations(ids=[11131, 10942])
```

**始终使用 `get_observations` 获取 2 个或更多 observations - 单个请求 vs 多个请求。**

**参数：**

- `ids` (数字数组，必需) - 要获取的 Observation ID
- `orderBy` (字符串，可选) - "date_desc"（默认）、"date_asc"
- `limit` (数字，可选) - 返回的最大 observations 数
- `project` (字符串，可选) - 项目名称筛选

**返回：** 包含标题、副标题、叙述、事实、概念、文件 (~500-1000 tokens/每个) 的完整 observation 对象

### 第 4 步：披露原始工具 I/O - 仅当第 3 步不够用时

Observations 是*摘要*。当答案需要工具返回的原始字节数据时——精确的 diff、精确的命令输出、精确的 API 响应——使用 `get_tool_uses` MCP 工具：

```
get_tool_uses(ids=["toolu_01ABC..."], project="my-project")
```

**不要从这里开始。** 原始工具体未摘要，每个可能长达数千个 tokens；这就是 claude-mem 将其压缩成 observations 的原因。仅在搜索 / 时间线 / get_observations 指向特定工具调用时才使用这一层。

**参数：**

- `ids` (数组，必需) - 数字 `tool_uses` ids 或不透明的 `tool_use_id` 字符串
- `limit` (数字，可选) - 返回的最大行数
- `project` (字符串，可选) - 项目名称筛选
- `contentSessionId` (字符串，可选) - 限制为单个会话

**返回：** 这些调用的存储的 `tool_input` / `tool_response`，以及工具名称、会话 IDs 和每个 observation 中的折叠信息。写入时超过 64 KB 的有效负载会被截断，并带有 `…[截断：N 字节]` 标记。

## 示例

**查找最近的 bug 修复：**

```
search(query="bug", type="observations", obs_type="bugfix", limit=20, project="my-project")
```

**查找上周发生的事情：**

```
search(type="observations", dateStart="2025-11-11", limit=20, project="my-project")
```

**理解某个发现的上下文：**

```
timeline(anchor=11131, depth_before=5, depth_after=5, project="my-project")
```

**批量获取详情：**

```
get_observations(ids=[11131, 10942, 10855], orderBy="date_desc")
```

**恢复上周运行的命令的精确输出：**

```
search(query="migration failed", limit=20, project="my-project")
get_observations(ids=[11131])            # 首先阅读摘要
get_tool_uses(ids=["toolu_01ABC..."])    # 仅当摘要遗漏了详细信息时
```

## 为什么使用这个工作流程？

- **搜索索引：** 每个结果 ~50-100 tokens
- **完整 observation：** 每个 ~500-1000 tokens
- **原始工具体：** 每个最多 64 KB —— 你 95% 的时间会跳过这一层
- **批量获取：** 1 个 HTTP 请求 vs 多个单独请求
- **通过筛选获取前节省 10 倍的 tokens**

## 知识代理

想要合成答案而不是原始记录？使用 `/knowledge-agent` 从你的 observation 历史中构建可查询的语料库。知识代理读取所有匹配的 observations 并以对话方式回答问题。
