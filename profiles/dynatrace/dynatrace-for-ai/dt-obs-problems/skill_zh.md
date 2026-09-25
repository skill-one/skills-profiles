# 问题分析能力

分析 Dynatrace AI 检测到的问题，包括根本原因识别、影响评估以及与日志和指标的相关性。

---

## 应用场景

### 1. 活跃问题筛选
- **目标**：列出并优先处理当前活跃的问题
- **触发条件**："活跃问题"、"有哪些问题处于打开状态"、"当前问题"、"可用性问题"
- **完成**：包含类别、用户影响和显示 ID 的活跃问题优先级列表

### 2. 根本原因调查
- **目标**：识别特定问题的根本原因实体
- **触发条件**："P-12345 的根本原因"、"是什么导致了这个问题"、"哪个实体是根本原因"
- **完成**：识别出的根本原因实体，包含受影响实体列表和影响范围

### 3. 问题趋势分析
- **目标**：分析随时间变化的问题模式，以识别重复出现的问题
- **触发条件**："重复问题"、"问题历史"、"过去 30 天的问题趋势"
- **完成**：显示问题频率、重复根本原因和解决时间的趋势数据

---

## 概述

Dynatrace 自动检测环境中的异常、性能下降和故障，创建 **问题**，这些问题聚合相关的告警、警告和 info 级别事件，并提供根本原因和影响洞察。

### 什么是问题？

问题是自动检测到的、软件和基础设施健康和弹性问题，它们：

- **自动关联**跨服务、基础设施、前端应用程序和用户会话的相关告警、警告和 info 级别事件
- **使用 Smartscape 依赖关系的因果分析来识别根本原因**
- **通过跟踪受影响的用户和服务来评估业务影响**
- **通过将相关症状分组为具有相同根本原因和影响的单个问题来减少告警噪音**
- **从早期检测到解决跟踪问题生命周期**

### 事件类型

`event.kind` 字段（稳定、权限）标识高级事件类型：

| `event.kind` 值 | 描述 |
|---|---|
| `DAVIS_EVENT` | Davis 检测到的基础设施/应用程序事件 |
| `BIZ_EVENT` | 业务事件（通过 API 输入或从跟踪捕获） |
| `RUM_EVENT` | 实际用户监控事件 |
| `AUDIT_EVENT` | 管理员/安全审计事件 |

`event.provider`（稳定、权限）标识事件来源。

## 问题类别

常见的 `event.category` 值：

| 类别 | 描述 | 示例 |
|----------|-------------|---------|
| **可用性** | 基础设施或服务不可用 | Web 服务返回无数据、合成测试主动失败、数据库连接丢失 |
| **错误** | 错误率超出基线 | API 错误率从 0.1% 跳升至 15% |
| **性能下降** | 性能下降 | 响应时间从 200ms 增加到 5000ms |
| **资源** | 资源饱和 | 容器内存达到 95%，导致 OOM 杀死 |
| **自定义** | 自定义异常检测 | 业务 KPI（每分钟订单数）低于阈值 |

## 问题生命周期

```text
检测 → 活跃 → 调查中 → 已关闭
```

- **活跃**：当前需要关注的问题
- **已关闭**：已解决的问题，用于历史分析

## 关键字段

### 常见字段名称错误

| ❌ 错误 | ✅ 正确 | 描述 |
|---------|-----------|-------------|
| `title` | `event.name` | 问题标题/描述 |
| `status` | `event.status` | 问题生命周期状态 |
| `severity` | `event.category` | 问题类型/类别 |
| `start` | `event.start` | 问题开始时间 |

### 正确的状态值

```dql
// ✅ 正确：使用这些状态值
fetch dt.davis.problems
| filter event.status == "ACTIVE"   // 当前活跃的问题
//     or event.status == "CLOSED"  // 已解决的问题
// ❌ 错误：event.status == "OPEN" 不存在！
| limit 1
```

### 关键字段参考

```dql
fetch dt.davis.problems, from:now() - 1h
| filter not(dt.davis.is_duplicate)
| fields
    event.start,                          // 问题开始时间戳
    event.end,                            // 问题结束时间戳（如果已关闭）
    display_id,                           // 人类可读的问题 ID（P-XXXXX）
    event.name,                           // 问题标题
    event.description,                    // 详细描述
    event.category,                       // 问题类型
    event.status,                         // 活跃或已关闭
    dt.smartscape_source.id,              // 受影响资源的 Smartscape ID
    dt.davis.affected_users_count,        // 受影响的用户数量
    affected_entity_ids = smartscape.affected_entities[][id],  // 受影响实体 ID 数组
    dt.smartscape.service,                // 受影响服务（可能是数组）
    dt.davis.root_cause_entity,           // 被识别为根本原因的实体
    root_cause_entity_id,                 // 根本原因实体 ID
    root_cause_entity_name,               // 人类可读的根本原因名称
    dt.davis.is_duplicate,                // 是否重复检测
    dt.davis.is_rootcause                 // 根本原因与症状
| limit 10
```

## 标准查询模式

始终以这个基础开始问题查询：

```dql
fetch dt.davis.problems, from:now() - 2h
| filter not(dt.davis.is_duplicate) and event.status == "ACTIVE"
| fields event.start, display_id, event.name, event.category
| sort event.start desc
| limit 20
```

**关键组件：**

- `fetch dt.davis.problems` - 问题数据源
- `not(dt.davis.is_duplicate)` - 过滤重复检测
- `event.status == "ACTIVE"` - 仅显示活跃问题
- 时间范围 - 始终指定一个合理的时间窗口

## 常见查询模式

### 按类别分类的活跃问题

```dql
fetch dt.davis.problems
| filter not(dt.davis.is_duplicate) and event.status == "ACTIVE"
| summarize problem_count = count(), by: {event.category}
| sort problem_count desc
```

### 高影响活跃问题（影响许多用户）

```dql
fetch dt.davis.problems
| filter not(dt.davis.is_duplicate) and event.status == "ACTIVE"
| filter dt.davis.affected_users_count > 100
| fields event.start, display_id, event.name, dt.davis.affected_users_count, event.category
| sort dt.davis.affected_users_count desc
```

### 高影响活跃问题（影响许多 Smartscape 实体）

```dql
fetch dt.davis.problems
| filter not(dt.davis.is_duplicate) and event.status == "ACTIVE"
| filter arraySize(affected_entity_ids) > 5
| fields event.start, display_id, event.name, affected_entity_ids, event.category, impacted_entity_count = arraySize(affected_entity_ids)
| sort impacted_entity_count desc
```

### 特定问题详情

```dql
fetch dt.davis.problems
| filter display_id == "P-XXXXXXXXXX"
| fields event.start, event.end, event.name, event.description, affected_entity_ids, dt.davis.affected_users_count, root_cause_entity_id, root_cause_entity_name
```

### 服务特定问题历史

```dql
fetch dt.davis.problems, from:now() - 7d
| filter not(dt.davis.is_duplicate)
| filter in(dt.smartscape.service, toSmartscapeId("SERVICE-XXXXXXXXX"))
| summarize problems = count(), by: {event.category, event.status}
```

## 根本原因分析模式

### 基本根本原因查询

```dql
fetch dt.davis.problems, from:now() - 24h
| filter not(dt.davis.is_duplicate) and event.status == "ACTIVE"
| fields
    display_id,
    event.name,
    event.description,
    root_cause_entity_id,
    root_cause_entity_name,
    affected_entity_ids = smartscape.affected_entities[][id]
```

### 按实体类型识别根本原因

识别最常导致问题的实体类型：

```dql
fetch dt.davis.problems, from:now() - 7d
| filter not(dt.davis.is_duplicate)
| filter isNotNull(root_cause_entity_id)
| summarize problem_count = count(), by:{root_cause_entity_name}
| sort problem_count desc
| limit 20
```

### 受影响的实体是 AWS 资源

```dql
fetch dt.davis.problems, from:now() - 24h
| filter not(dt.davis.is_duplicate) and event.status == "ACTIVE"
| filter iAny(startsWith(smartscape.affected_entities[][type], "AWS_"))
```

### 基础设施根本原因与服务影响

```dql
fetch dt.davis.problems, from:now() - 30m
| filter not(dt.davis.is_duplicate) and event.status == "ACTIVE"
| filter matchesPhrase(root_cause_entity_id, "HOST-")
| filter isNotNull(dt.smartscape.service)
| fields display_id, event.name, root_cause_entity_name, dt.smartscape.service
```

### 问题影响范围

计算每个根本原因的实体影响：

```dql
fetch dt.davis.problems, from:now() - 7d
| filter not(dt.davis.is_duplicate)
| filter isNotNull(root_cause_entity_id)
| fieldsAdd affected_count = arraySize(smartscape.affected_entities)
| summarize
    avg_affected = avg(affected_count),
    max_affected = max(affected_count),
    problem_count = count(),
    by:{root_cause_entity_name}
| sort avg_affected desc
```

### 重复的根本原因

识别反复导致问题的实体：

```dql
fetch dt.davis.problems, from:now() - 24h
| filter not(dt.davis.is_duplicate)
| filter isNotNull(root_cause_entity_id)
| summarize
    problem_count = count(),
    first_occurrence = min(event.start),
    last_occurrence = max(event.start),
    by:{root_cause_entity_id, root_cause_entity_name}
| filter problem_count > 3
| sort problem_count desc
```

### 原因类别与根本原因实体

这些问题是不同的——选择正确的方法：

- **"什么导致问题？"** / **"最常见的原因"** → 按事件类别汇总
  (SLOWDOWN, ERROR, RESOURCE, AVAILABILITY, CUSTOM)。解释每个类别触发的原因。
- **"哪个实体导致问题？"** / **"根本原因实体"** → 按 `root_cause_entity_name` 分组。列出特定的服务、主机或应用程序。

**原因类别分解**（用于询问常见原因、模式或类型）：

```dql
fetch dt.davis.problems, from:now() - 30d
| filter not(dt.davis.is_duplicate)
| summarize problem_count = count(), by: {event.category}
| sort problem_count desc
```

然后针对每个类别，使用问题类别表解释触发原因，并引用租户数据中的具体实体作为示例。

## 问题趋势与模式分析

跟踪问题随时间的变化趋势，识别重复出现的问题，并分析解决性能。

**主要文件：**
- `references/problem-trending.md` - 时间序列分析和模式检测

**常见用例：**
- 随时间变化的活跃问题与 `makeTimeseries`
- 按类别的问题创建率
- 按计划检测重复问题
- 解决时间趋势和 P95 持续时间分析

**关键技术：**
- **`makeTimeseries`** vs **`bin()`**：为生命周期跨度与离散事件选择正确方法
- **NULL 处理**：使用 `coalesce(event.end, now())` 用于活跃问题
- **峰值小时分析**：识别问题最频繁发生的时间
- **影响趋势**：跟踪用户影响随时间的变化

参考 `references/problem-trending.md` 获取完整的查询模式和最佳实践。

## 跨域问题查询

### 与 Kubernetes 集群相关的问题

使用 `affected_entity_ids` 或 `dt.smartscape_source.id` 查找与 Kubernetes 相关的问题：

```dql
fetch dt.davis.problems, from:now() - 7d
| filter not(dt.davis.is_duplicate)
| filter matchesPhrase(dt.smartscape_source.id, "KUBERNETES_CLUSTER")
    OR matchesPhrase(dt.smartscape_source.id, "K8S_")
| fields event.start, display_id, event.name, event.category, event.status,
    dt.smartscape_source.id, affected_entity_ids
| sort event.start desc
```

替代方法：扩展受影响实体并过滤 Kubernetes 实体类型：

```dql
fetch dt.davis.problems, from:now() - 7d
| filter not(dt.davis.is_duplicate)
| expand entity_id = affected_entity_ids
| filter matchesPhrase(entity_id, "KUBERNETES_CLUSTER")
    OR matchesPhrase(entity_id, "K8S_")
| fields event.start, display_id, event.name, event.category, entity_id
| sort event.start desc
```

### 简单问题列表

列出过去 24 小时内所有问题（常见请求）：

```dql
fetch dt.davis.problems, from:now() - 24h
| filter not(dt.davis.is_duplicate)
| fields event.start, event.end, display_id, event.name, event.category, event.status
| sort event.start desc
```

## 响应构建

### 问题原因总结

在总结问题原因、类别或模式时，提供跨越所有标准类别的**全面分解**：AVAILABILITY、ERROR、SLOWDOWN、RESOURCE 和 CUSTOM。对于每个类别：

1. **类别名称**和问题计数
2. **触发原因**——简要说明（例如，RESOURCE = CPU/内存/磁盘阈值超出；AVAILABILITY = 服务或实体变得无法访问）
3. **具体示例**来自租户数据（受影响实体名称、问题 ID）

不要在找到前两个类别后停止——用户期望完整的图景。参考上表中的问题类别以获取触发原因说明。

### 分析结果

在呈现查询结果时：
- 包含**实体名称**（而不仅仅是 ID）——但选择高效的方法：
  - **实体数量少（< 5）**：`get-entity-name` 调用可以
  - **实体数量多**：使用 `query-problems` 工具直接返回名称，或在 DQL 查询中内联解析名称，包括 `root_cause_entity_name` / `entityName()`。避免在 10+ 实体上循环调用 `get-entity-name`——这可能会耗尽工具调用限制并完全返回无答案。
- 提供**可操作的推荐**与识别的原因对齐
- 按频率或影响组织，便于优先处理

## 最佳实践

### 基本规则

1. **始终过滤重复项**：使用 `not(dt.davis.is_duplicate)` 避免多次计数同一问题
2. **使用正确状态值**：`"ACTIVE"` 或 `"CLOSED"`，从不 `"OPEN"`
3. **指定时间范围**：始终包含时间边界以优化性能
4. **包含 display_id**：识别问题和链接的关键
5. **逐步测试**：构建查询时逐个添加过滤器和字段
6. **尽早过滤**：在 fetch 后立即应用 `not(dt.davis.is_duplicate)`

### 查询开发

- **从简单开始**：从基本过滤开始，然后添加复杂性
- **先测试字段**：使用 `| limit 1` 验证字段名称是否存在
- **使用有意义的时间范围**：太宽浪费资源，太窄错过数据
- **记录问题 ID**：始终捕获和存储 `display_id` 以供参考

### 根本原因验证

- 始终过滤 `isNotNull(root_cause_entity_id)` 当需要时
- 使用 `dt.davis.event_ids` 交叉引用事件
- 考虑时间延迟：根本原因可能在日志中提前几分钟出现

### 时间范围指南

```dql
// ✅ 好 - 具体时间范围
fetch dt.davis.problems, from:now() - 4h
```

```dql
// ❌ 坏 - 扫描所有历史数据
fetch dt.davis.problems
```

### 绝对时间范围需要双引号

在 DQL 查询中使用绝对 ISO 8601 时间戳作为 `from` 和 `to` 时，**始终用双引号括起来**。未加引号的时间戳是语法错误。

```dql
// ✅ 正确 - 绝对时间戳加引号
fetch dt.davis.problems, from: "2026-05-18T22:50:00Z", to: "2026-05-18T23:35:00Z"
| filter not(dt.davis.is_duplicate)
| fields event.start, display_id, event.name, event.category, event.status
| sort event.start desc
```

## 故障排除

| 问题 | 原因 | 解决方案 |
|---------|-------|----------|
| 未返回问题 | 使用 `event.status == "OPEN"` | 使用 `"ACTIVE"` 或 `"CLOSED"` —— `"OPEN"` 不存在 |
| 结果中存在重复问题 | 缺少去重过滤器 | 在 fetch 后立即添加 `filter not(dt.davis.is_duplicate)` |
| 错误字段名称 (`title`, `status`, `severity`) | 类似 SQL 的命名 | 使用 `event.name`, `event.status`, `event.category` —— 参考上表中的字段名称 |
| `root_cause_entity_id` 为 null | 并非所有问题都有识别出的根本原因 | 添加 `filter isNotNull(root_cause_entity_id)` 当查询根本原因时 |
| 查询扫描过多数据/超时 | 缺少时间范围 | 始终在 fetch 命令上指定 `from:now() - <duration>` |
| `affected_entity_ids` 是空数组 | 问题没有映射的受影响实体 | 检查 `dt.smartscape.service` 或 `dt.smartscape_source.id` 作为替代 |

## 何时加载参考

### 加载 [problem-trending.md](references/problem-trending.md) 当：

- 分析问题随时间的变化频率
- 检测按计划重复出现的问题
- 计算解决时间趋势和 P95 持续时间
- 比较按类别的问题创建率

### 加载 [problem-correlation.md](references/problem-correlation.md) 当：

- 将问题与日志或其他遥测相关联
- 调查导致问题的事件
- 将问题与部署或配置更改链接

### 加载 [impact-analysis.md](references/impact-analysis.md) 当：

- 评估业务影响（受影响的用户、服务）
- 计算根本原因实体的影响范围
- 按技术和用户影响优先处理问题

## 参考

- [problem-trending.md](references/problem-trending.md) — 问题趋势和时间序列分析模式
- [problem-correlation.md](references/problem-correlation.md) — 将问题与日志和遥测相关联
- [impact-analysis.md](references/impact-analysis.md) — 业务和技术影响评估
- [problem-merging.md](references/problem-merging.md) — 何时以及为何 DAVIS 将事件合并为问题

## 相关技能

- **dt-dql-essentials** - 核心 DQL 语法和问题查询的查询结构
- **dt-obs-logs** - 将问题与应用程序和基础设施日志相关联
- **dt-obs-tracing** - 通过分布式跟踪分析调查问题
