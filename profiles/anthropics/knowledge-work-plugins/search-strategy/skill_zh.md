# 搜索策略

> 如果你看到不熟悉的占位符或需要检查哪些工具已连接，请参阅 [CONNECTORS.md](../../CONNECTORS.md)。

企业搜索背后的核心智能。将单个自然语言问题转换为针对特定来源的并行搜索，并生成排序后的去重结果。

## 目标

将这个：
```
"What did we decide about the API migration timeline?"
```

转换为针对每个已连接来源的定向搜索：
```
~~chat:  "API migration timeline decision" (语义) + "API migration" in:#engineering after:2025-01-01
~~知识库: 语义搜索 "API migration timeline decision"
~~项目追踪器:  文本搜索 "API migration" in 相关工作区
```

然后将结果综合为单个连贯的答案。

## 查询分解

### 第一步：识别查询类型

对用户的问题进行分类以确定搜索策略：

| 查询类型 | 示例 | 策略 |
|---------|---------|----------|
| **决策** | "What did we decide about X?" | 优先考虑对话 (~~chat, email)，寻找结论信号 |
| **状态** | "What's the status of Project Y?" | 优先考虑最近活动、任务追踪器、状态更新 |
| **文档** | "Where's the spec for Z?" | 优先考虑 Drive、wiki、共享文档 |
| **人员** | "Who's working on X?" | 搜索任务分配、消息作者、文档协作者 |
| **事实性** | "What's our policy on X?" | 优先考虑 wiki、官方文档，然后确认性对话 |
| **时间性** | "When did X happen?" | 使用宽泛的日期范围搜索，寻找时间戳 |
| **探索性** | "What do we know about X?" | 跨所有来源进行广泛搜索，综合 |

### 第二步：提取搜索组件

从查询中提取：

- **关键词**：必须出现在结果中的核心术语
- **实体**：人员、项目、团队、工具（如有可用，使用记忆系统）
- **意图信号**：决策词、状态词、时间标记
- **约束**：时间范围、来源提示、作者过滤器
- **否定词**：需要排除的内容

### 第三步：为每个来源生成子查询

针对每个可用来源，创建一个或多个定向查询：

**优先使用语义搜索**：
- 概念性问题 ("What do we think about...")
- 关键词未知的问题
- 探索性查询

**优先使用关键词搜索**：
- 已知术语、项目名称、缩写
- 用户引用的确切短语
- 过滤器密集型查询 (from:, in:, after:)

**当主题可能被不同方式提及时，生成多个查询变体**：
```
用户: "Kubernetes setup"
查询: "Kubernetes", "k8s", "cluster", "container orchestration"
```

## 来源特定查询翻译

### ~~chat

**语义搜索**（自然语言问题）：
```
query: "What is the status of project aurora?"
```

**关键词搜索**：
```
query: "project aurora status update"
query: "aurora in:#engineering after:2025-01-15"
query: "from:<@UserID> aurora"
```

**过滤器映射**：
| 企业过滤器 | ~~chat 语法 |
|------------------|--------------|
| `from:sarah` | `from:sarah` 或 `from:<@USERID>` |
| `in:engineering` | `in:engineering` |
| `after:2025-01-01` | `after:2025-01-01` |
| `before:2025-02-01` | `before:2025-02-01` |
| `type:thread` | `is:thread` |
| `type:file` | `has:file` |

### ~~知识库 (Wiki)

**语义搜索** — 用于概念查询：
```
descriptive_query: "API migration timeline and decision rationale"
```

**关键词搜索** — 用于确切术语：
```
query: "API migration"
query: "\"API migration timeline\""  (确切短语)
```

### ~~项目追踪器

**任务搜索**：
```
text: "API migration"
workspace: [workspace_id]
completed: false  (用于状态查询)
assignee_any: "me"  (用于 "my tasks" 查询)
```

**过滤器映射**：
| 企业过滤器 | ~~project tracker 参数 |
|------------------|----------------|
| `from:sarah` | `assignee_any` 或 `created_by_any` |
| `after:2025-01-01` | `modified_on_after: "2025-01-01"` |
| `type:milestone` | `resource_subtype: "milestone"` |

## 结果排序

### 相关性评分

根据以下因素对每个结果进行评分（根据查询类型加权）：

| 因素 | 决策权重 | 状态权重 | 文档权重 | 事实权重 |
|--------|-------------------|------------------|--------------------|-------------------|
| 关键词匹配 | 0.3 | 0.2 | 0.4 | 0.3 |
| 新鲜度 | 0.3 | 0.4 | 0.2 | 0.1 |
| 权威性 | 0.2 | 0.1 | 0.3 | 0.4 |
| 完整性 | 0.2 | 0.3 | 0.1 | 0.2 |

### 权威性层级

取决于查询类型：

**对于事实/政策问题**：
```
Wiki/官方文档 > 共享文档 > 邮件公告 > 聊天消息
```

**对于 "what happened" / 决策问题**：
```
会议笔记 > 线索结论 > 邮件确认 > 聊天消息
```

**对于状态问题**：
```
任务追踪器 > 最近聊天 > 状态文档 > 邮件更新
```

## 处理歧义

当查询存在歧义时，优先于猜测询问一个聚焦的澄清问题：

```
歧义: "search for the migration"
→ "我找到了关于几次迁移的参考。您是在寻找：
   1. 数据库迁移 (Project Phoenix)
   2. 云迁移 (AWS → GCP)
   3. 邮件迁移 (Exchange → O365)"
```

仅在以下情况下询问澄清：
- 存在真正不同的解释，会导致结果差异很大
- 歧义会显著影响搜索来源

**不要**在以下情况下询问澄清：
- 查询清晰到可以产生有用结果
- 轻微的歧义可以通过返回多个解释的结果来解决

## 备用策略

当来源不可用或返回无结果时：

1. **来源不可用**：跳过它，搜索剩余来源，记录缺失
2. **某个来源无结果**：尝试更广泛的查询术语，移除日期过滤器，尝试替代关键词
3. **所有来源都无结果**：向用户建议查询修改
4. **速率限制**：记录限制，返回其他来源的结果，建议稍后重试

### 查询扩展

如果初始查询返回结果过少：
```
原始: "PostgreSQL migration Q2 timeline decision"
更广泛:  "PostgreSQL migration"
更广泛:  "database migration"
最广泛: "migration"
```

按顺序移除约束：
1. 日期过滤器（搜索所有时间）
2. 来源/位置过滤器
3. 较不重要的关键词
4. 仅保留核心实体/主题术语

## 并行执行

始终跨来源并行执行搜索，切勿顺序执行。总搜索时间应大致等于最慢的单个来源，而不是所有来源的总和。

```
[用户查询]
     ↓ 分解
[~~chat 查询] [~~email 查询] [~~云存储查询] [Wiki 查询] [~~项目追踪器查询]
     ↓            ↓            ↓              ↓            ↓
  (并行执行)
     ↓
[合并 + 排序 + 去重]
     ↓
[综合答案]
```
