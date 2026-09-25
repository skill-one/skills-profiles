# 日志分析技能

使用 DQL 查询、过滤和分析 Dynatrace 日志数据，用于故障排除和监控。

## 本技能涵盖内容

- 按严重程度、内容和实体获取和过滤日志
- 使用模式匹配搜索日志消息
- 计算错误率和统计数据
- 分析日志模式和趋势
- 按维度对日志数据进行分组和聚合

> **需要跨源连接**：如果查询必须将日志与主机属性（操作系统类型、主机名、IP 地址、云服务提供商）组合 → 在编写查询前，请也阅读
> `dt-dql-essentials/references/smartscape-topology-navigation.md`

---

## 应用场景
当用户想要时，使用此技能：
- 查找特定的日志条目（例如，“显示过去一小时的错误日志”）
- 按严重程度、进程组或内容过滤日志
- 搜索包含特定关键字或短语的日志
- 计算错误率或日志统计数据
- 识别常见的错误消息或模式
- 分析随时间变化的日志趋势
- 使用日志数据排除问题

## 核心概念

### 日志数据模型
- **timestamp**：日志条目创建时间
- **content**：日志消息文本
- **status**：日志级别（ERROR、FATAL、WARN、INFO 等）
- **dt.process_group.id**：关联的进程组实体
- **dt.process_group.detected_name**：将进程组 ID 解析为可读名称

### 查询模式
- **fetch logs**：获取日志数据的主要命令
- **时间范围**：使用 `from:now() - <持续时间>` 定义时间窗口
- **过滤**：应用严重程度、内容和实体过滤器
- **聚合**：分组和汇总日志数据
- **模式检测**：使用 `matchesPhrase()` 和 `contains()` 进行内容搜索

### 常见操作
- 严重程度过滤（单个或多个级别）
- 内容搜索（简单和全文）
- 基于实体的过滤（进程组）
- 时间序列分析（分桶、排序）
- 错误率计算
- 模式分析（异常、超时等）

## 核心工作流

### 1. 日志搜索
按时间、严重程度和内容查找特定日志条目。

**典型步骤**：
1. 定义时间范围
2. 按严重程度过滤（可选）
3. 搜索内容中的关键字
4. 选择相关字段
5. 排序和限制结果

**示例**：
```dql
fetch logs, from:now() - 1h
| filter status == "ERROR"
| fields timestamp, content, process_group = dt.process_group.detected_name
| sort timestamp desc
| limit 100
```

### 2. 日志过滤
使用多个标准（严重程度、实体、内容）缩小日志范围。

**典型步骤**：
1. 带时间范围获取日志
2. 应用严重程度过滤器
3. 按实体（process_group）过滤
4. 应用内容过滤器
5. 格式化和排序输出

**示例**：
```dql
fetch logs, from:now() - 2h
| filter in(status, {"ERROR", "FATAL", "WARN"})
| summarize count(), by: {dt.process_group.id, dt.process_group.detected_name}
| fieldsAdd process_group = dt.process_group.detected_name
| sort `count()` desc
```

### 3. 模式分析
在日志数据中识别模式、趋势和异常。

**典型步骤**：
1. 带时间范围获取日志
2. 添加模式检测字段
3. 按实体或时间聚合
4. 计算统计和比率
5. 按频率或率排序

**示例**：
```dql
fetch logs, from:now() - 2h
| filter status == "ERROR"
| fieldsAdd
    has_exception = if(matchesPhrase(content, "exception"), true, else: false),
    has_timeout = if(matchesPhrase(content, "timeout"), true, else: false)
| summarize
    count(),
    exception_count = countIf(has_exception == true),
    timeout_count = countIf(has_timeout == true),
    by: {process_group = dt.process_group.detected_name}
```

## 核心函数

### 过滤
- `filter status == "ERROR"` - 按状态级别过滤
- `in(status, {"ERROR", "FATAL", "WARN"})` - 多状态过滤器（使用花括号表示字面量集）
- `contains(content, "keyword")` - 简单子字符串搜索
- `matchesPhrase(content, "exact phrase")` - 全文短语搜索

### 实体操作
- `dt.process_group.detected_name` - 获取可读的进程组名称
- `filter process_group == "service-name"` - 按特定实体过滤

### 聚合
- `count()` - 计数所有日志条目
- `countIf(condition)` - 条件计数
- `by: {dimension}` - 按实体或时间分桶分组
- `bin(timestamp, 5m)` - 时间分桶用于趋势分析

### 字段操作
- `fields timestamp, content, status` - 选择特定字段
- `fieldsAdd name = expression` - 添加计算字段
- `if(condition, true_value, else: false_value)` - 条件逻辑

## 常见模式

### 内容搜索
简单子字符串搜索：
```dql
fetch logs, from:now() - 1h
| filter contains(content, "database")
| fields timestamp, content, status
```

全文短语搜索：
```dql
fetch logs, from:now() - 1h
| filter matchesPhrase(content, "connection timeout")
| fields timestamp, content, process_group = dt.process_group.detected_name
```

### 错误率计算
计算随时间的错误率：
```dql
fetch logs, from:now() - 2h
| summarize
    total_logs = count(),
    error_logs = countIf(status == "ERROR"),
    by: {time_bucket = bin(timestamp, 5m)}
| fieldsAdd error_rate = (error_logs * 100.0) / total_logs
| sort time_bucket asc
```

### 最常见的错误消息
查找最常见的错误：
```dql
fetch logs, from:now() - 24h
| filter status == "ERROR"
| summarize error_count = count(), by: {content}
| sort error_count desc
| limit 20
```

### 特定进程组的日志
按进程组过滤日志：
```dql
fetch logs, from:now() - 1h
| fieldsAdd process_group = dt.process_group.detected_name
| filter process_group == "payment-service"
| filter status == "ERROR"
| fields timestamp, content, status
| sort timestamp desc
```

### 结构化/JSON 日志解析
许多应用程序会发出 JSON 格式的日志行。使用 `parse` 提取字段，而不是转储原始内容：

```dql
fetch logs, from:now() - 1h
| filter status == "ERROR"
| parse content, "JSON:log"
| fieldsAdd level = log[level], message = log[msg], error = log[error]
| fields timestamp, level, message, error
| sort timestamp desc
| limit 50
```

按解析字段聚合：
```dql
fetch logs, from:now() - 4h
| filter status == "ERROR"
| parse content, "JSON:log"
| fieldsAdd message = log[msg]
| summarize error_count = count(), by: {message}
| sort error_count desc
| limit 20
```

**注意**：
- `parse content, "JSON:log"` 创建记录字段 `log` — 使用 `log[key]` 访问嵌套值
- 在 `parse` 之前使用 `contains()` 过滤日志以减少解析开销
- 适用于任何 JSON 结构化字段，而不仅仅是 `content`

## 最佳实践

1. **始终指定时间范围** - 使用 `from:now() - <持续时间>` 限制数据
2. **尽早应用过滤器** - 在聚合前按严重程度和实体过滤
3. **使用适当的搜索方法** - `contains()` 用于简单搜索，`matchesPhrase()` 用于精确搜索
4. **限制结果** - 添加 `| limit 100` 防止输出过载
5. **有意义地排序** - 按时间排序最近日志，按计数排序最常见错误
6. **命名实体** - 使用 `dt.process_group.detected_name` 或 `getNodeName()` 获取可读输出
7. **使用时间分桶进行趋势分析** - `bin(timestamp, 5m)` 用于时间序列分析

## 集成点

- **实体模型**：使用 `dt.process_group.id` 进行服务关联
- **时间序列**：支持 `bin()` 和时间范围进行时间分析
- **内容搜索**：通过 `matchesPhrase()` 实现全文搜索
- **聚合**：使用 `summarize` 和条件函数进行统计分析

## 限制和注意事项

- 日志可用性取决于 OneAgent 配置和日志摄取
- 全文搜索 (`matchesPhrase`) 在大型数据集上可能影响性能
- 实体名称需要正确的 OneAgent 监控才能解析
- 时间范围应合理（避免无界查询）

## 排错

| 问题 | 原因 | 解决方案 |
|-------|-------|----------|
| 未返回日志 | 缺少时间范围或范围过窄 | 扩展 `from:` 窗口；验证日志摄取是否激活 |
| `getNodeName()` 返回 null | OneAgent 未监控实体或实体尚未解析 | 验证 OneAgent 是否部署且实体已发现；使用 `dt.process_group.detected_name` 作为可靠替代方案 |
| `matchesPhrase()` 在大数据上缓慢 | 全文搜索未预过滤 | 在 `matchesPhrase()` 之前添加 `filter status == "ERROR"` |
| 错误字段名 `log.level` | 常见错误 | 使用 `loglevel`（无点）表示严重程度；参见 dt-dql-essentials |
| 空的 `content` 字段 | 日志行为空或未摄取 | 检查 OneAgent 中的日志源配置 |

## 相关技能

- **dt-dql-essentials** - 核心DQL语法和查询结构，用于日志查询
- **dt-obs-tracing** - 使用跟踪 ID 将日志与分布式跟踪关联
- **dt-obs-problems** - 将日志与 DAVIS 检测到的问题关联
