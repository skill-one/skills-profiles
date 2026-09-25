# 案例管理

通过 Kibana 案例API管理 SOC案例。所有案例都属于`securitySolution`范围——此技能仅限于在 Elastic Security 内运行。案例会出现在 Kibana 安全界面中，可以分配给分析师、与告警关联，并通过连接器推送到外部事件管理系统。

## 前置条件

在使用前从`skills/security`目录安装依赖项：

```bash
cd skills/security && npm install
```

设置所需的环境变量（或将其添加到工作区根目录下的`.env`文件中）：

```bash
export KIBANA_URL="https://your-cluster.kb.cloud.example.com:443"
export KIBANA_API_KEY="your-kibana-api-key"
```

## 何时使用

- 告警分派后创建案例（分类、IOCs、发现）
- 搜索现有案例以关联相关告警
- 向现有案例添加调查备注或附加告警
- 更新案例状态或严重性
- 列出近期案例以供审核

## 何时不应使用

- 不要使用此技能处理可观测性或 Elasticsearch案例——它会硬编码`owner: securitySolution`
- 不要用于 Security 解决方案空间之外的案例

## 执行规则

- 立即开始执行工具——不要先读取 SKILL.md、浏览工作区或列出文件。
- 忠实报告工具输出。精确复制案例ID、标题、标签、严重性和数量，如API返回的值。不要缩写案例ID、截断标题、编造细节或四舍五入数字。
- 当API返回零结果时，明确说明——不要猜测可能的结果。
- 在列出或查找案例时，报告API响应中的**精确总数**，并以原文呈现每个案例的标题、严重性和状态。

## 快速入门

所有命令从工作区根目录运行。所有输出都是JSON。直接调用工具——不要先读取技能文件或探索工作区。对于`attach-alert/attach-alerts`，`--rule-id`和`--rule-name`是Kibana API必需的（如果未知，请使用`--rule-id unknown --rule-name unknown`）。使用`attach-alerts`进行批量操作，具有自动速率限制重试和API调用之间2秒的间隔。

## 常见多步骤工作流

| 任务                        | 按顺序调用的工具                                                     |
| --------------------------- | ---------------------------------------------------------------------------- |
| **创建案例**           | `case_manager` create (标题、描述、标签、严重性)                   |
| **查找主机案例**   | `case_manager` find --tags "agent_id:<id>" 或 find --search "\<hostname\>" |
| **将告警附加到案例**    | `case_manager` attach-alert (案例ID、告警ID、告警索引、规则ID/名称)   |
| **添加调查备注** | `case_manager` add-comment (案例ID、备注文本)                           |
| **列出近期开放案例**  | `case_manager` list --status open --per-page \<n\>                           |
| **更新案例**             | `case_manager` update (案例ID、状态/严重性/标签变更)                |

**查找主机案例：** 使用`find --search "<hostname>"`按主机名搜索标题、描述和备注。如果知道代理ID，也可以使用`find --tags "agent_id:<agent_id>"`。始终添加`--status open`以仅筛选活动案例。从API响应中报告精确的`total`计数和每个案例的原文标题。

```bash
# 创建（默认启用syncAlerts；使用--sync-alerts false禁用）
node skills/security/case-management/scripts/case-manager.js create --title "主机1上的恶意DLL侧加载" --description "通过DLL侧加载检测到的加密剪辑器恶意软件..." --tags "分类:恶意" "置信度:88" "mitre:T1574.002" --severity critical --yes

# 查找、列出、获取
node skills/security/case-management/scripts/case-manager.js find --tags "agent_id:550888e5-357d-4bc1-a154-486eb7b4e076"
node skills/security/case-management/scripts/case-manager.js find --search "DLL侧加载" --status open
node skills/security/case-management/scripts/case-manager.js list --status open --per-page 10
node skills/security/case-management/scripts/case-manager.js get --case-id <case_id>

# 附加单个告警
node skills/security/case-management/scripts/case-manager.js attach-alert --case-id <case_id> --alert-id <alert_doc_id> --alert-index .ds-.alerts-security.alerts-default-2025.12.01-000013 --rule-id <rule_uuid> --rule-name "恶意软件检测告警"

# 批量附加多个告警
node skills/security/case-management/scripts/case-manager.js attach-alerts --case-id <case_id> --alert-ids <id1> <id2> <id3> --alert-index .ds-.alerts-security.alerts-default-2026.02.16-000016 --rule-id <rule_uuid> --rule-name "恶意软件检测告警"

# 添加备注，更新（--tags与现有标签合并，不会替换）
node skills/security/case-management/scripts/case-manager.js add-comment --case-id <case_id> --comment "进程树分析显示..."
node skills/security/case-management/scripts/case-manager.js update --case-id <case_id> --status closed --severity low --yes
```

写操作（`create`、`update`）默认会提示确认。传递`--yes`以跳过提示（当由代理调用时需要）。

## 列出和查找结果报告

当报告`list`或`find`结果时：

1. 说明JSON响应中的精确`total`计数（例如，"总共有12个开放案例"）。
2. 以紧凑的单行条目呈现每个案例：`<标题> | <严重性> | <案例ID简短> | <创建时间>`。从`title`字段中精确复制**原文标题**——不要改述、缩写或总结。
3. 如果用户要求N个案例，则呈现正好N条条目（如果更少则呈现更少）。除非用户明确要求，否则不要添加额外列（告警计数、描述、状态）。
4. 不要添加API返回之外的任何信息。如果字段为null或缺失，则省略它。
5. 呈现结果后停止。不要添加分析、评论或关于案例的观察。

## 标签规范

使用结构化标签进行机器可搜索的元数据：

| 标签模式              | 示例                             | 目的                                          |
| ------------------------ | ----------------------------------- | ------------------------------------------------ |
| `classification:<值>` | `classification:malicious`          | 分派分类（良性/未知/恶意）                    |
| `confidence:<分数>`     | `confidence:85`                     | 置信度分数0-100                               |
| `mitre:<技术>`      | `mitre:T1574.002`                   | MITRE ATT&CK技术ID                           |
| `agent_id:<ID>`          | `agent_id:550888e5-...`             | Elastic代理ID用于关联                         |
| `rule:<名称>`            | `rule:恶意行为检测`            | 检测规则名称                              |

## 案例严重性映射

| 分类           | Kibana严重性 |
| ------------------------ | --------------- |
| benign (分数 0-19)      | `低`           |
| unknown (分数 20-60)    | `中`        |
| malicious (分数 61-80)  | `高`          |
| malicious (分数 81-100) | `严重`      |

## 已知限制

### syncAlerts仅限安全

`syncAlerts`设置（默认启用）将案例状态与附加告警状态同步。此功能仅适用于 Security 解决方案案例。如果不需要告警同步，则在创建案例时传递`--sync-alerts false`。

### 速率限制

Kibana API执行速率限制。在附加多个告警时，`attach-alerts`批量命令会自动处理429响应并重试。如果使用`attach-alert`逐个调用，请间隔约10秒调用。

### Serverless上的`find --search`

`find --search`参数可能在Kibana Serverless部署中返回500错误。使用`find --tags`进行过滤，或使用`list`浏览近期案例。

### `find --tags`需要精确匹配

标签搜索仅支持精确匹配。`find --tags "agent_id:abc123"`有效，但部分匹配无效。

## Kibana案例API参考

有关详细的API端点、请求/响应格式和示例，请参阅
[references/kibana-cases-api.md](references/kibana-cases-api.md)。

## 示例

- "为我在高严重性下分派的钓鱼告警创建案例"
- "搜索与暴力破解攻击相关的开放案例"
- "将调查发现作为备注添加到案例ID abc-123"

## 指南

- 仅报告工具输出——不要编造ID、主机名、IP或工具响应中未出现的细节。
- 保留请求中的标识符——使用工具调用和响应中用户提供的精确值。
- 使用工具的返回数据简洁地确认操作。
- 区分事实与推断——将工具输出之外的结论标记为您的评估。
- 在呈现案例列表或搜索结果时，从每个案例复制**精确标题**。不要改述、缩写或总结标题。包括API `total`字段中的总数。
- 立即执行工具。在行动前不要读取SKILL.md、浏览目录或列出文件。

## 生产使用

- 写操作（`create`、`update`）会提示确认。当由代理调用时，传递`--yes`或`-y`以跳过。
- 在运行任何命令之前，验证`KIBANA_URL`和`KIBANA_API_KEY`指向预期的集群。
- 案例属于`securitySolution`范围——此技能不会影响可观测性或其他Kibana案例所有者。

## 环境变量

| 变量         | 是否必需 | 描述                                                      |
| ---------------- | -------- | ---------------------------------------------------------------- |
| `KIBANA_URL`     | 是      | Kibana基本URL（例如，`https://my-kibana.kb.cloud.example.com`) |
| `KIBANA_API_KEY` | 是      | 用于身份验证的Kibana API密钥                                |
