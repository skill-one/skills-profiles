# Kibana Agent Builder

创建、检查、更新、删除和测试 Agent Builder **工具**和**代理**。通过范围搜索工具、参数化 ES|QL 和工作流集成，将 LLM 响应与 Elasticsearch 数据相结合。

<!-- begin-partial: preamble -->

## 环境配置

此技能通过 `elastic` CLI 执行 Elasticsearch 操作。如果未安装 [`elastic` CLI](https://github.com/elastic/cli#configuration)，请告知用户其用途。不要猜测凭证、直接调用 HTTP API 或尝试其他变通方法。

此技能以 HTTP 简写形式引用操作（例如，`GET /`、`GET /_cat/indices`、`GET /{index}/_mapping`、`GET /{index}/_settings/index.mode`、`POST /_query`）。文档末尾的 [操作](#operations) 表将每个简写映射到等效的 `elastic` CLI 命令——始终使用 CLI 而不是直接调用 HTTP API。

<!-- end-partial: preamble -->

## 资源模型

Agent Builder 暴露三种不同的资源类型——不要混淆它们：

| 类型                    | 用途                                                                                            | 典型 API                                  |
| ----------------------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| **工具**                | 代理调用的可重用函数以检索或操作数据（`index_search`、`esql`、`workflow`） | `POST kbn:/api/agent_builder/tools`          |
| **代理**               | 具有指令和精选工具集的 LLM 实体                                                             | `POST kbn:/api/agent_builder/agents`         |
| **聊天 / 会话**        | 与现有代理的临时消息会话                                                                     | `POST kbn:/api/agent_builder/converse/async` |

创建工具**不会**创建代理。列出或与代理聊天**不会**创建工具。当用户要求“创建代理”或“创建工具”时，在调用写入 API 之前，先确定他们指的是哪种资源。

内置工具使用 `platform.core.*` 前缀（例如 `platform.core.search`）。自定义工具和代理由用户定义。阅读 [architecture-guide.md](references/architecture-guide.md) 了解内置工具清单、上下文工程和安全说明。

## 流程

1. **分类任务。** 判断用户需要**工具**、**代理**还是与现有代理**聊天**。如果他们询问已存在的内容（“有哪些代理？”、“列出代理”），将请求视为**只读发现**——在提出任何创建、更新或删除之前，从实时数据中回答。

2. **在写入前发现现有资源。** 创建或更新时：
   - 调用 `GET kbn:/api/agent_builder/tools` 列出可用工具（内置和自定义）。不要凭空编造工具 ID。
   - 调用 `GET kbn:/api/agent_builder/agents` 列出现有代理并避免重复 ID 或名称。

   当用户仅询问哪些代理存在时，在 `GET kbn:/api/agent_builder/agents` 后停止。枚举每个代理的 id 和名称。如果列表为空，请明确说明——不要编造代理。只有在用户明确要求创建且您已确认目标 ID 未被使用时，才继续创建。

3. **选择工具类型（针对工具任务）。** 将意图匹配到最窄的工具类型：
   - **对已知索引模式进行开放式搜索** → 使用 `index_search` 并提供**特定模式**（例如 `customer-feedback-*`），除非用户明确要求，否则永远不要使用 `*` 或所有索引范围。
   - **固定分析、聚合或参数化查询** → 使用 `esql` 并带有 `?param` 占位符和 `params` 对象（在没有参数时使用 `{}`）。
   - **超出检索的多步骤自动化** → 引用现有工作流 ID 的 `workflow`。

   对于 ES|QL 语法和查询设计，请遵循 `elasticsearch-esql` 技能。对于工作流 YAML，请遵循 `kibana-workflows` 技能。

4. **构建工具负载。** 必填字段：`id`、`type`、`description`、`configuration`。可选：`tags`。

   **API 限制**（违反将返回 400）：
   - POST 仅接受 `id`、`type`、`description`、`configuration`、`tags`。**`name` 在工具上无效**。
   - 索引搜索配置使用 `"pattern"`，**不是** `"index"`。
   - ES|QL 工具即使为空也要求 `"params"`：`"params": {}`。
   - 每个参数仅接受 `type` 和 `description`——不接受 `default` 或 `optional`。在查询中硬编码默认值。
   - PUT 在工具上仅接受 `description`、`configuration` 和 `tags`。`id` 和 `type` 是不可变的。

   **索引搜索示例**（范围模式）：

   ```json
   {
     "id": "customer_feedback_search",
     "type": "index_search",
     "description": "在 customer-feedback 索引中搜索客户反馈和支持工单。",
     "configuration": {
       "pattern": "customer-feedback-*"
     }
   }
   ```

   **ES|QL 示例**（参数化，带 LIMIT）：

   ```json
   {
     "id": "feedback_sentiment_trend",
     "type": "esql",
     "description": "返回按产品类别在回顾窗口期内正面与负面反馈计数。",
     "configuration": {
       "query": "FROM customer-feedback-* | WHERE @timestamp >= NOW() - ?lookback_days::integer * 1d | STATS positive = COUNT(*) WHERE sentiment == \"positive\", negative = COUNT(*) WHERE sentiment == \"negative\" BY product_category | SORT negative DESC | LIMIT 20",
       "params": {
         "lookback_days": {
           "type": "integer",
           "description": "回顾的天数，例如 7、30、90"
         }
       }
     }
   }
   ```

5. **创建并验证工具。** 调用 `POST kbn:/api/agent_builder/tools` 并提供负载。通过调用 `GET kbn:/api/agent_builder/tools/{toolId}` 并将创建的 id、type、description 和 configuration 报告给用户来确认成功——在没有实时 API 响应的情况下不要声称成功。

   可选地使用 `POST kbn:/api/agent_builder/tools/_execute` 验证 ES|QL 工具，传入 `tool_id` 和 `tool_params`。始终在 ES|QL 查询中包含 `| LIMIT N` 以控制 token 使用。

6. **构建代理负载（针对代理任务）。** 必填字段：`id`、`name`、`description`、`configuration`。配置必须包括 `instructions` 和一个 `tools` 数组，其中 `tool_ids` 来自步骤 2——仅使用 `GET kbn:/api/agent_builder/tools` 返回的 ID。

   从名称派生稳定的 `id`（小写、连字符、字母数字）。在发布前检查步骤 2 的代理列表是否存在冲突。

   ```json
   {
     "id": "customer-feedback-agent",
     "name": "Customer Feedback Analyst",
     "description": "分析客户情绪和反馈趋势。",
     "configuration": {
       "instructions": "始终使用工具检索数据。永远不要从记忆中回答数据问题。",
       "tools": [
         {
           "tool_ids": ["customer_feedback_search", "platform.core.search"]
         }
       ]
     }
   }
   ```

   **代理更新限制：** PUT 仅接受 `description`、`configuration` 和 `tags`（在适用情况下包括头像/标签）。不要在更新中发送不可变字段（如 `id`、`name` 或 `type`）——它们会导致 400 错误。

7. **创建并验证代理。** 调用 `POST kbn:/api/agent_builder/agents`。通过 `GET kbn:/api/agent_builder/agents` 或 `GET kbn:/api/agent_builder/agents/{agentId}` 确认，并报告实时响应。

8. **更新或删除（当被要求时）。** 在执行破坏性操作前先确认用户意图。
   - 更新工具：`PUT kbn:/api/agent_builder/tools/{toolId}`
   - 删除工具：`DELETE kbn:/api/agent_builder/tools/{toolId}`
   - 更新代理：`PUT kbn:/api/agent_builder/agents/{agentId}`
   - 删除代理：`DELETE kbn:/api/agent_builder/agents/{agentId}`

9. **聊天（当被要求时）。** 聊天不是创建代理或工具。使用 `POST kbn:/api/agent_builder/converse/async` 并传入现有 `agent_id` 和用户输入。预期多步骤推理和工具调用；允许足够的时间进行流式完成。

## 指南

- **先发现后创建。** 创建资源前始终列出代理（在相关情况下列出工具）。当被问及“有哪些代理？”时，先回答这个问题——只读——即使用户后来提到想要创建新代理。
- **狭义范围索引搜索。** 优先选择 `customer-feedback-*` 而不是 `*`。宽泛模式会增加噪声、token 成本和 RBAC 表面区域。
- **编写描述性工具描述。** 代理仅根据描述选择工具——包括何时使用每个工具和示例触发短语。
- **最小化工具集。** 每个分配的工具都会在每次回合向代理系统提示符添加 token。
- **部署前验证 ES|QL。** 创建后执行工具，当参数或查询形状非简单时。
- **使用聚合和 KEEP。** 对于分析问题，优先选择汇总统计数据而不是原始文档转储。

## 示例

### 创建索引搜索工具（评估模式）

用户："创建一个自定义 Agent Builder 工具，搜索 customer-feedback-\* 索引。使用工具 ID 'eval-feedback-search'。"

1. 列出工具——确认 `eval-feedback-search` 已存在。
2. 选择范围于 `customer-feedback-*` 的 `index_search`（不是 `*`）。
3. POST 工具并包含 id、description 和 `configuration.pattern`。
4. 通过 id 获取工具并确认创建给用户。

### 在创建前回答“哪些代理已存在？”

用户："我想在 Kibana Agent Builder 中创建一个新代理。哪些代理已存在？"

1. 调用 `GET kbn:/api/agent_builder/agents` —— 只读。
2. 列出现有代理的 id 和名称（或说明不存在）。
3. 在这一步**不要**创建、更新或删除任何内容。
4. 只有当用户随后要求创建时，才选择上述列表中未使用的 id。

### 创建发现后的代理

用户："使用 esql-sales-data 工具创建一个销售助手代理。"

1. 列出工具——确认 `esql-sales-data` 存在。
2. 列出代理——确认无冲突 id。
3. POST 代理并包含指令和选定的工具 ID。
4. 获取代理以验证并报告。

## 参考

- [architecture-guide.md](references/architecture-guide.md) — 内置工具、上下文工程、token 优化、MCP/A2A 集成、权限
- [use-cases.md](references/use-cases.md) — 客户反馈、营销活动、合同分析代理的剧本示例工具和代理负载

## 操作

| HTTP API (简写)                             | `elastic` CLI 命令                                                                                                              |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| `GET kbn:/api/agent_builder/tools`               | `elastic kb agent-builder get-agent-builder-tools`                                                                                 |
| `POST kbn:/api/agent_builder/tools`              | `elastic kb agent-builder post-agent-builder-tools --id '<id>' --type '<type>' --description '<desc>' --configuration '<json>'`    |
| `GET kbn:/api/agent_builder/tools/{toolId}`      | `elastic kb agent-builder get-agent-builder-tools-toolid --tool-id '<toolId>'`                                                     |
| `PUT kbn:/api/agent_builder/tools/{toolId}`      | `elastic kb agent-builder put-agent-builder-tools-toolid --tool-id '<toolId>' [--description '<desc>'] [--configuration '<json>']` |
| `DELETE kbn:/api/agent_builder/tools/{toolId}`   | `elastic kb agent-builder delete-agent-builder-tools-toolid --tool-id '<toolId>' [--force]`                                        |
| `POST kbn:/api/agent_builder/tools/_execute`     | `elastic kb agent-builder post-agent-builder-tools-execute --tool-id '<toolId>' --tool-params '<json>'`                            |
| `GET kbn:/api/agent_builder/agents`              | `elastic kb agent-builder get-agent-builder-agents`                                                                                |
| `POST kbn:/api/agent_builder/agents`             | `elastic kb agent-builder post-agent-builder-agents --id '<id>' --name '<name>' --description '<desc>' --configuration '<json>'`   |
| `GET kbn:/api/agent_builder/agents/{agentId}`    | `elastic kb agent-builder get-agent-builder-agents-id --id '<agentId>'`                                                            |
| `PUT kbn:/api/agent_builder/agents/{agentId}`    | `elastic kb agent-builder put-agent-builder-agents-id --id '<agentId>' [--description '<desc>'] [--configuration '<json>']`        |
| `DELETE kbn:/api/agent_builder/agents/{agentId}` | `elastic kb agent-builder delete-agent-builder-agents-id --id '<agentId>'`                                                         |
| `POST kbn:/api/agent_builder/converse/async`     | `elastic kb agent-builder post-agent-builder-converse-async --agent-id '<agentId>' --input '<message>'`                            |
