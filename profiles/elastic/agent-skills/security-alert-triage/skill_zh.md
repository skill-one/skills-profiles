# 警报分诊

逐个分析 Elastic Security 警报：收集上下文、分类、创建案例并确认。这项技能依赖于 `case-management` 技能进行案例创建。

## 前置条件

在首次使用前，从 `skills/security` 目录安装依赖项：

```bash
cd skills/security && npm install
```

设置所需的环境变量（或将其添加到工作区根目录下的 `.env` 文件中）：

```bash
export ELASTICSEARCH_URL="https://your-cluster.es.cloud.example.com:443"
export ELASTICSEARCH_API_KEY="your-api-key"
export KIBANA_URL="https://your-cluster.kb.cloud.example.com:443"
export KIBANA_API_KEY="your-kibana-api-key"
```

## 快速入门

从工作区根目录执行所有命令。始终执行：获取 → 调查 → 记录 → 确认。直接调用工具——不要先读取技能文件或探索工作区。

```bash
node skills/security/alert-triage/scripts/fetch-next-alert.js
node skills/security/case-management/scripts/case-manager.js find --tags "agent_id:<id>"
node skills/security/alert-triage/scripts/run-query.js --query-file query.esql --type esql
node skills/security/case-management/scripts/case-manager.js create --title "..." --description "..." --tags "classification:..." "agent_id:<id>" --severity <level> --yes
node skills/security/case-management/scripts/case-manager.js attach-alert --case-id <id> --alert-id <id> --alert-index <index> --rule-id <uuid> --rule-name "<name>" --yes
node skills/security/alert-triage/scripts/acknowledge-alert.js --related --agent <id> --timestamp <ts> --window 60 --yes
```

## 常见多步骤工作流

| 任务                                 | 按顺序调用的工具                                                                                             |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| **端到端分诊**                      | `fetch_next_alert` → `run_query` (上下文) → `case_manager` create (案例) → `acknowledge_alert`              |
| **收集上下文**                     | `run_query` (进程树、网络、相关警报)                                                                          |
| **分类后创建案例**                 | `case_manager` create → `case_manager` attach-alert                                                           |
| **分诊后确认**                     | `acknowledge_alert` (批量相关模式)                                                                            |

始终完成完整工作流：获取 → 调查 → 记录 → 确认。不要在收集上下文后停止——在确认前创建或更新案例。

**关键执行规则：**

- 立即执行工具——不要先读取 SKILL.md、浏览工作区或列出文件。
- 对于 ES|QL 查询，将查询写入临时 `.esql` 文件，然后通过 `--query-file` 传递。不要使用 `edit_file` —— 使用单个 `shell` 调用 `echo "..." > query.esql && node ... --query-file query.esql`。
- 保持上下文收集集中：运行 2-4 个针对性查询（进程树、网络、相关警报），而不是 10+。
- 仅报告工具返回的内容。逐字复制标识符——不要转述 ID、时间戳或主机名。

## 关键原则

- **不要过早分类。** 在决定良性/未知/恶意之前，收集所有上下文。
- **大多数警报都是误报**，即使它们看起来很严重。名为 "恶意行为" 的规则或严重性 "critical" 不是证据。
- **"未知" 是可接受的**，并且通常正确，当证据不足时。
- **"恶意" 需要强有力的佐证证据**：持久化 + C2、凭证窃取、横向移动——而不仅仅是可疑的 API 调用。
- **逐字报告工具输出。** 逐字复制 ID、主机名、时间戳和计数，正如工具返回的那样。不要四舍五入数字、缩写 ID 或转述错误消息。

## 工作流

当分诊多个警报时，**先分组，然后分诊每个组**：

```text
- [ ] 第 0 步：按代理/主机和时间窗口分组警报
- [ ] 第 1 步：检查现有案例
- [ ] 第 2 步：收集完整上下文（不要跳过）
- [ ] 第 3 步：创建或更新案例（仅收集上下文后）
- [ ] 第 4 步：确认警报和相关警报
- [ ] 第 5 步：获取下一个警报组并重复
```

### 第 0 步：分诊前分组警报

当用户询问多个打开的警报时，**先分组**以避免重复调查：查询打开的警报，按 `agent.id` 分组，按时间窗口（~5 分钟 = 可能是一个事件）子分组，将每个组作为一个单元分诊。

使用 ES|QL 获取概述（先写入文件，用于 PowerShell）：

```esql
FROM .alerts-security.alerts-*
| WHERE kibana.alert.workflow_status == "open" AND @timestamp >= "<start>"
| STATS alert_count=COUNT(*), rules=VALUES(kibana.alert.rule.name) BY agent.id
| SORT alert_count DESC
```

完整查询模板，请参阅 [references/classification-guide.md](references/classification-guide.md)。

### 第 1 步：检查现有案例

在创建新案例之前，检查该警报是否属于现有案例。使用 `case-management` 技能：

```bash
node skills/security/case-management/scripts/case-manager.js find --tags "agent_id:<agent_id>"
node skills/security/case-management/scripts/case-manager.js cases-for-alert --alert-id <alert_id>
```

查找具有相同代理 ID、用户或相似时间窗口内的相关检测规则案例。

> **注意：** `find --search` 在 Serverless 上可能返回 500 错误。使用 `find --tags` 或 `list`。

### 第 2 步：收集上下文

**这是最重要的一步。不要跳过或简化。** 在形成任何分类意见之前，完成所有子步骤。

**时间范围警告：** 警报可能是几天或几周前的。**绝对不要使用相对时间**，如 `NOW() - 1 HOUR`。提取警报的 `@timestamp` 并围绕该时间构建查询，使用 +/- 1 小时窗口。

**子步骤：** (2a) 同一代理/用户上的相关警报； (2b) 环境中规则频率（高 = 易误报）； (2c) 实体上下文——进程树、网络、注册表、文件； (2d) 行为调查——持久化、C2、横向移动、凭证访问。

示例——进程树（使用 ES|QL 并 `KEEP`；避免 `--full`，它会产生 10K+ 行）：

```esql
FROM logs-endpoint.events.process-*
| WHERE agent.id == "<agent_id>" AND @timestamp >= "<alert_time - 5min>" AND @timestamp <= "<alert_time + 10min>"
  AND process.parent.name IS NOT NULL
  AND process.name NOT IN ("svchost.exe", "conhost.exe", "agentbeat.exe")
| KEEP @timestamp, process.name, process.command_line, process.pid, process.parent.name, process.parent.pid
| SORT @timestamp | LIMIT 80
```

| 数据类型 | 索引模式                    |
| --------- | --------------------------- |
| 警报    | `.alerts-security.alerts-*`      |
| 进程    | `logs-endpoint.events.process-*` |
| 网络    | `logs-endpoint.events.network-*` |
| 日志    | `logs-*`                     |

完整查询模板和分类标准，请参阅
[references/classification-guide.md](references/classification-guide.md)。

### 第 3 步：创建或更新案例

收集上下文后，创建案例并附加警报。使用 `--rule-id` 和 `--rule-name`（必需；没有它们会返回 400 错误）：

```bash
node skills/security/case-management/scripts/case-manager.js create \
  --title "<简洁摘要>" \
  --description "<发现、IOCs、攻击链、MITRE 技术>" \
  --tags "classification:<benign|unknown|malicious>" "confidence:<0-100>" "mitre:<technique>" "agent_id:<id>" \
  --severity <low|medium|high|critical>

node skills/security/case-management/scripts/case-manager.js attach-alert \
  --case-id <case_id> --alert-id <alert_id> --alert-index <index> \
  --rule-id <rule_uuid> --rule-name "<rule name>"

# 多个警报：attach-alerts --alert-ids <id1> <id2>
# 添加备注：add-comment --case-id <id> --comment "发现..."
```

**案例描述：** 摘要（1-2 句话）；攻击链；IOCs（哈希值、IP、路径）；MITRE 技术；行为发现；响应上下文（修复、有风险的凭证）。

### 第 4 步：确认警报

一起确认所有相关警报。首先使用 `--dry-run` 确认范围，然后运行：

```bash
# 按主机名——分诊主机时首选
node skills/security/alert-triage/scripts/acknowledge-alert.js --query --host <hostname> --dry-run
node skills/security/alert-triage/scripts/acknowledge-alert.js --query --host <hostname> --yes

# 按代理 ID——当 agent.id 已知时首选
node skills/security/alert-triage/scripts/acknowledge-alert.js --related --agent <id> --timestamp <ts> --window 60 --dry-run
node skills/security/alert-triage/scripts/acknowledge-alert.js --related --agent <id> --timestamp <ts> --window 60 --yes
```

增加 `--window` 以处理更长的攻击链（例如，`300` 为 5 分钟）。报告工具输出中确认的警报的确切数量。传递 `--yes` 以跳过确认提示（由代理调用时必需）。

### 第 5 步：重复

```bash
node skills/security/alert-triage/scripts/fetch-next-alert.js
```

## 工具参考

### fetch-next-alert.js

获取最旧的未确认 Elastic Security 警报。

```bash
node skills/security/alert-triage/scripts/fetch-next-alert.js [--days <n>] [--json] [--full] [--verbose]
```

### run-query.js

对 Elasticsearch 运行 KQL 或 ES|QL 查询。

**PowerShell 警告**：ES|QL 查询包含管道字符（`|`），PowerShell 将其解释为 shell 管道。**始终使用 `--query-file`**：

```bash
# 将查询写入文件，然后运行
node skills/security/alert-triage/scripts/run-query.js --query-file query.esql --type esql
```

没有管道的 KQL 查询可以直接传递：

```bash
node skills/security/alert-triage/scripts/run-query.js "agent.id:<id>" --index "logs-*" --days 7
```

| 参数                | 描述                                              |
| -------------------- | ------------------------------------------------ |
| `query`              | KQL 查询（位置参数）                                   |
| `--query-file`, `-q` | 从文件读取查询（ES\|QL 在 PowerShell 上必需） |
| `--type`, `-t`       | `kql` 或 `esql`（默认：kql）                           |
| `--index`, `-i`      | 索引模式（默认：`logs-*`）                        |
| `--size`, `-s`       | 最大结果（默认：100）                               |
| `--days`, `-d`       | 限制为最近 N 天                                     |
| `--json`             | 原始 JSON 输出                                      |
| `--full`             | 完整文档源                                        |

### acknowledge-alert.js

通过将 `workflow_status` 更新为 `acknowledged` 来确认警报。

| 模式    | 命令                                                                                                                                |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| 单个    | `node skills/security/alert-triage/scripts/acknowledge-alert.js <alert_id> --index <index> --yes`                                      |
| 相关    | `node skills/security/alert-triage/scripts/acknowledge-alert.js --related --agent <id> --timestamp <ts> [--window 60] --yes`           |
| 按主机  | `node skills/security/alert-triage/scripts/acknowledge-alert.js --query --host <hostname> [--time-start <ts>] [--time-end <ts>] --yes` |
| 查询    | `node skills/security/alert-triage/scripts/acknowledge-alert.js --query --agent <id> [--time-start <ts>] [--time-end <ts>] --yes`      |
| 干运行  | 在任何模式下添加 `--dry-run`（无需确认）                                                                                   |
| 确认    | 所有写入模式提示确认；传递 `--yes` 以跳过                                                                          |

## 示例

- "获取下一个未确认警报并分诊"
- "调查警报 ID abc-123——收集上下文、分类，如果恶意则创建案例"
- "处理过去 24 小时内的前 5 个严重警报"

## 指南

- 仅报告工具输出——不要凭空编造 ID、主机名、IP 或工具响应中未出现的详细信息。
- 保留请求中的标识符——使用工具调用和响应中用户提供的确切值。
- 使用工具的返回数据简洁地确认操作。
- 区分事实与推断——将工具输出之外的结论标记为您的评估。

## 生产使用

- 所有写入操作 (`acknowledge-alert.js`) 提示确认。由代理调用时，传递 `--yes` 或 `-y` 以跳过。
- 在批量确认前使用 `--dry-run` 预览范围，而无需修改数据。
- 确认脚本使用 Kibana 检测引擎 API，该 API 兼容自托管和 Serverless 部署。
- 运行任何脚本前，验证环境变量指向预期集群——确认无撤销。
