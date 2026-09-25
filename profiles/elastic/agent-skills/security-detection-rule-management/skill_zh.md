# 检测规则管理

为新兴威胁和覆盖范围空白创建新的检测规则，并调整现有规则以减少误报。
所有操作都通过 `rule-manager.js` 使用 Kibana 检测引擎 API 执行。

## 执行规则

- 立即开始执行工具 — 不要先读取 SKILL.md、浏览工作区或列出文件。
- 忠实报告工具输出。精确复制 API 返回的规则 ID、名称、警报计数、异常 ID 和错误消息。不要缩写规则 UUID，不要编造规则名称，也不要四舍五入警报计数。
- 当工具返回错误（规则未找到、API 失败）时，报告确切错误 — 不要猜测替代方案。

## 前提条件

在使用前从 `skills/security` 目录安装依赖项：

```bash
cd skills/security && npm install
```

设置所需的环境变量（或将其添加到工作区根目录中的 `.env` 文件）：

```bash
export ELASTICSEARCH_URL="https://your-cluster.es.cloud.example.com:443"
export ELASTICSEARCH_API_KEY="your-api-key"
export KIBANA_URL="https://your-cluster.kb.cloud.example.com:443"
export KIBANA_API_KEY="your-kibana-api-key"
```

## 常见的多步骤工作流

| 任务                                | 调用的工具（按顺序）                                                                                |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **调整噪声 SIEM 规则**            | `rule_manager` find/noisy-rules → `run_query` (调查误报) → `rule_manager` patch 或 add-exception |
| **添加端点行为异常**              | `fetch_endpoint_rule` (从 GitHub 获取规则定义) → `add_endpoint_exception` (限定于规则.id)          |
| **创建新的检测规则**               | `run_query` (在数据上测试查询) → `rule_manager` create                                           |
| **调查规则警报量**                 | `rule_manager` get → `run_query` (查询警报索引)                                                   |

对于端点行为规则，始终先获取规则定义，以了解查询逻辑和现有排除项，然后再添加异常。
对于 SIEM 规则，始终使用 `run_query` 调查警报模式，然后再进行调整。

**关键：** 对于端点行为规则，始终使用 `fetch_endpoint_rule`（而不是 `shell` 或直接脚本调用）获取规则定义，然后使用 `add_endpoint_exception` 添加异常。这些是专用工具 — 不要手动调用底层脚本。

## 工作流：为误报调整规则

### 步骤 1-2：识别噪声规则并分析误报

使用 `noisy-rules` 或 `find` 查找噪声规则，然后获取规则定义并调查警报：

```bash
node skills/security/detection-rule-management/scripts/rule-manager.js noisy-rules --days 7 --top 20
node skills/security/detection-rule-management/scripts/rule-manager.js find --filter "alert.attributes.name:*Suspicious*" --brief
node skills/security/detection-rule-management/scripts/rule-manager.js get --id <rule_uuid>
node skills/security/alert-triage/scripts/run-query.js "kibana.alert.rule.name:\"<rule_name>\"" --index ".alerts-security.alerts-*" --days 7 --full
```

寻找模式：相同进程/用户/主机 → 异常候选；宽泛模式 → 收紧查询；合法软件 → 异常；过于宽泛 → 重写或调整阈值。

### 步骤 3：选择调整策略

**按优先级顺序：**

1. **添加异常** — 适用于特定的已知良好进程、用户或主机。不会修改规则查询。当规则总体正确但在已知合法活动上触发时使用。
2. **收紧查询** — 修补规则的查询以排除误报模式。当误报源于查询过于宽泛时最佳。
3. **调整阈值/警报抑制** — 对于阈值规则，增加阈值值。对于任何规则类型，启用警报抑制以减少同一实体上的重复警报。
4. **降低风险分数/严重性** — 如果规则生成许多低价值警报但仍具有一些检测价值，则降级规则的优先级。
5. **禁用规则** — 最后手段。只有当规则没有价值或与另一条规则完全冗余时才禁用。

### 步骤 4-5：应用调整、验证和记录

**添加异常**（单条件/多条件，通过 `matches` 的通配符）：

```bash
node skills/security/detection-rule-management/scripts/rule-manager.js add-exception \
  --rule-uuid <rule_uuid> \
  --entries "process.executable:is:C:\\Program Files\\SCCM\\CcmExec.exe" "process.parent.name:is:CcmExec.exe" \
  --name "Exclude SCCM" --comment "FP: SCCM 部署" --tags "tuning:fp" "source:soc" --yes
```

**修补查询、阈值、严重性或禁用：**

```bash
node skills/security/detection-rule-management/scripts/rule-manager.js patch --id <rule_uuid> --query "process.name:powershell.exe AND NOT process.parent.name:CcmExec.exe" --yes
node skills/security/detection-rule-management/scripts/rule-manager.js patch --id <rule_uuid> --max-signals 50 --yes
node skills/security/detection-rule-management/scripts/rule-manager.js patch --id <rule_uuid> --severity low --risk-score 21 --yes
node skills/security/detection-rule-management/scripts/rule-manager.js disable --id <rule_uuid> --yes
```

操作（`patch`、`enable`、`disable`、`delete`、`add-exception`、`bulk-action`）默认提示确认。传递 `--yes` 以跳过提示（由代理调用时需要）。

使用 `rule-manager.js get --id <rule_uuid>` 验证。通过 `case-management` 技能更新分派案例。

---

## 工作流：创建新的检测规则

### 步骤 1-2：定义威胁、数据源和字段

指定 MITRE ATT&CK 技巧、所需数据源（端点、网络、云）以及恶意与合法行为。常见索引：`logs-endpoint.events.process-*`、`logs-endpoint.events.network-*`、`.alerts-security.alerts-*`、`logs-windows.*`、`logs-aws.*`。关键字段：`process.name`、`process.command_line`、`process.parent.name`、`destination.ip`、`winlog.event_id`、`event.action`。使用 `run-query.js` 验证数据：

```bash
node skills/security/alert-triage/scripts/run-query.js "process.name:certutil.exe" --index "logs-endpoint.events.process-*" --days 30 --size 5
```

### 步骤 3：编写和测试查询

规则类型：`query`（KQL 字段匹配）、`eql`（事件序列）、`esql`（聚合）、`threshold`（基于量的）、`threat_match`（IOC 关联）、`new_terms`（首次出现）。在创建前对 Elasticsearch 进行测试：

```bash
node skills/security/alert-triage/scripts/run-query.js "process.name:certutil.exe AND process.command_line:(*urlcache* OR *decode*)" \
  --index "logs-endpoint.events.process-*" --days 30
```

对于 EQL，使用 `--query-file` 以避免 shell 脚本转义问题。

**在创建或修补规则前验证查询语法。** `validate-query` 命令在本地捕获常见错误 — 转义的反斜杠、不匹配的括号、不平衡的引号和重复的逻辑运算符：

```bash
node skills/security/detection-rule-management/scripts/rule-manager.js validate-query \
  --query "process.name:taskkill.exe AND process.command_line:(*chrome.exe* OR *msedge.exe*)" --language kuery
```

`create` 和 `patch` 命令也会自动运行验证并拒绝无效查询。仅当您确定查询正确且尽管触发检查也如此时，才传递 `--skip-validation`。

常见的 KQL 语法错误：

- **转义的斜杠** — KQL 通配符使用纯文本。编写 `*/IM chrome.exe*`，而不是 `*\/IM chrome.exe*`。
- **不匹配的括号** — 每个 `(` 都必须有匹配的 `)`。
- **不平衡的引号** — 每个 `"` 都必须成对出现。
- **重复运算符** — `AND AND` 或 `OR OR` 总是错误。

### 步骤 4：创建规则

```bash
node skills/security/detection-rule-management/scripts/rule-manager.js create \
  --name "Certutil URL 下载或解码" \
  --description "检测 certutil.exe 用于下载文件或解码 Base64 负载，这是一种常见的 LOLBin 技术。" \
  --type query \
  --query "process.name:certutil.exe AND process.command_line:(*urlcache* OR *decode*)" \
  --index "logs-endpoint.events.process-*" \
  --severity medium --risk-score 47 \
  --tags "OS:Windows" "Tactic:防御规避" "Tactic:命令与控制" \
  --false-positives "IT 管理员使用 certutil 进行合法证书操作" \
  --references "https://attack.mitre.org/techniques/T1140/" \
  --interval 5m --disabled
```

对于复杂规则（EQL 序列、MITRE 映射、警报抑制），使用 `create --from-file rule_definition.json` 和 `--threat-file`。有关架构，请参阅 [references/detection-api-reference.md](references/detection-api-reference.md)。

### 步骤 5：监控和迭代

使用 `noisy-rules --days 3 --top 10` 监控警报量，并根据需要调整误报。

---

## 工作流：端点行为规则调整

通过为特定规则添加 **端点异常** 来调整 **Elastic Endpoint 行为规则**。端点异常位于 **安全 → 异常 → 端点安全异常列表** 中，而不是在单个 SIEM 规则下。

**关键原则：** 始终从 protections-artifacts 首先获取规则定义。始终将异常限定于规则（`rule.id` 或 `rule.name`）。使用完整路径而不是进程名称。在添加任何异常前运行强制性的实体交叉检查（步骤 4b）。模拟影响（步骤 5b），并目标是 ≥60% 的噪声减少。

**脚本：** `fetch-endpoint-rule-from-github.js`（通过 id 获取规则 TOML）、`add-endpoint-exception.js`（添加到端点异常列表；需要 rule.id/rule.name）、`check-exclusion-best-practices.js`。

有关完整分步工作流（步骤 1-6）、查询和模拟模板的详细信息，请参阅
[references/endpoint-behavior-tuning-workflow.md](references/endpoint-behavior-tuning-workflow.md)。有关排除最佳实践，请参阅
[references/endpoint-rule-exclusion-best-practices.md](references/endpoint-rule-exclusion-best-practices.md)。

---

## 工具参考

### rule-manager.js

所有命令都从工作区根目录运行。所有输出都是 JSON，除非另有说明。

| 命令              | 描述                                   |
| -------------------- | --------------------------------------------- |
| `find`               | 搜索/列出带有可选 KQL 过滤的规则    |
| `get`                | 通过 `--id` 或 `--rule-id` 获取规则     |
| `create`             | 创建规则（内联标志或 `--from-file`） |
| `patch`              | 在规则上修补特定字段                 |
| `enable`             | 启用规则                                 |
| `disable`            | 禁用规则                                |
| `delete`             | 删除规则                                 |
| `export`             | 导出规则为 NDJSON                        |
| `bulk-action`        | 批量启用/禁用/删除/复制/编辑         |
| `add-exception`      | 向规则添加异常项                       |
| `list-exceptions`    | 列出异常列表中的项                     |
| `create-shared-list` | 创建共享异常列表                |
| `noisy-rules`        | 通过警报量查找最噪声的规则           |
| `validate-query`     | 在创建/修补前检查查询语法        |

**端点行为调整：** `fetch-endpoint-rule-from-github.js`（通过 id 获取规则 TOML）、`add-endpoint-exception.js`
（添加到端点异常列表；需要 rule.id/rule.name）、`check-exclusion-best-practices.js`。

### 异常条目格式

作为 `field:operator:value` 传递条目。运算符：`is`、`is_not`、`is_one_of`、`is_not_one_of`、`exists`、
`does_not_exist`、`matches`、`does_not_match`。示例：`process.name:is:svchost.exe`,
`file.path:matches:C:\\Program Files\\*`。

## 其他资源

- 有关完整 API 架构详细信息，请参阅 [references/detection-api-reference.md](references/detection-api-reference.md)
- 对于 **端点行为** 调整：[references/endpoint-exceptions-guide.md](references/endpoint-exceptions-guide.md)、
  [references/endpoint-rule-exclusion-best-practices.md](references/endpoint-rule-exclusion-best-practices.md)
- 在调整期间调查警报，请使用 `alert-triage` 技能
- 在案例中记录调整操作，请使用 `case-management` 技能

## 示例

- "查找过去 7 天最噪声的检测规则并帮助我调整一个"
- "向可疑 PowerShell 规则添加 SCCM 排除"
- "创建 certutil URL 下载或解码的检测规则"

## 指南

- **仅报告工具输出。** 当总结结果时，仅引用或释义工具返回的内容。不要编造 ID、主机名、IP、分数、进程树或其他工具响应中未出现的详细信息。
- **保留请求中的标识符。** 如果用户提供了特定主机名、代理 ID、案例 ID 或其他值，请在工具调用和响应中使用这些确切值 — 不要替换不同的标识符。
- **简洁地确认操作。** 执行工具后，使用工具的返回数据确认已执行的操作。不要编造内部 ID、元数据或状态详细信息，除非它们出现在工具响应中。
- **区分事实与推断。** 如果您得出工具返回内容之外的结论（例如，根据观察到的行为建议 MITRE 技巧），请明确标记这些为您的评估，而不是将其作为工具输出呈现。
- **立即执行工具。** 不要在行动前读取 SKILL.md、浏览目录或列出文件。
- **逐字报告工具输出。** 精确复制规则 ID、名称、警报计数和错误消息。不要缩写 UUID 或四舍五入数字。

## 生产使用

- 所有写入操作（`create`、`patch`、`enable`、`disable`、`delete`、`add-exception`、`bulk-action`、
  `add-endpoint-exception`）默认提示确认。传递 `--yes` 或 `-y` 以跳过提示（由代理调用时需要）。
- **端点异常全局抑制检测。** 始终使用 `rule.id` 或 `rule.name` 在条目中将异常限定于特定规则。宽泛的未限定异常可能会无声地减少检测覆盖范围。
- 在运行任何脚本前，验证环境变量指向预期的集群。
- 使用 `--dry-run` 与 `bulk-action` 在执行批量更改前预览影响。

## 环境变量

| 变量                | 需要 | 描述                                     |
| ----------------------- | -------- | ----------------------------------------------- |
| `ELASTICSEARCH_URL`     | 是      | Elasticsearch URL（用于 noisy-rules 聚合） |
| `ELASTICSEARCH_API_KEY` | 是      | Elasticsearch API 密钥                           |
| `KIBANA_URL`            | 是      | Kibana URL（用于规则 API）                      |
| `KIBANA_API_KEY`        | 是      | Kibana API 密钥                                  |
