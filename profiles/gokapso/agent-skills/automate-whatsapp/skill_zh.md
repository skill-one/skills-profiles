# 自动化 WhatsApp

## 使用场景

使用此技能构建和运行 WhatsApp 自动化：工作流 CRUD、图编辑、WhatsApp 和项目事件触发、项目事件发射、执行、函数管理、webhook 工具和 MCP 工具。

## 设置

首选路径：
- 已安装并认证 Kapso CLI (`kapso login`)
- 对于工作流和函数编辑，使用源代码控制的项目，并使用 `kapso link`、`kapso pull`、`kapso build` 和 `kapso push`
- 对于工作流代码，使用 `@kapso/workflows`，并从 `workflow.js` 或 `workflow.ts` 导出一个 `Workflow` 实例

备用路径：
环境变量：
- `KAPSO_API_BASE_URL`（仅主机，不包含 `/platform/v1`）
- `KAPSO_API_KEY`

## 使用方法

### 本地编辑工作流

当用户正在工作或可以创建本地存储库时，首先使用此路径。

```bash
npm install -g @kapso/cli
npm install --save-dev @kapso/workflows
kapso login
kapso link --project <project-id>
kapso pull
```

使用 `@kapso/workflows` 编辑 `workflows/<workflow-slug>/workflow.js` 或 `workflow.ts`：

```ts
import { START, Workflow } from "@kapso/workflows";

const workflow = new Workflow("inbound-support", {
  name: "Inbound Support",
  status: "draft",
});

workflow.addTrigger({
  type: "inbound_message",
  phoneNumberId: "<phone-number-id>",
});

workflow.addNode(START, {
  position: { x: 100, y: 100 },
});

workflow.addNode("reply", {
  type: "send_text",
  message: "Thanks for reaching out.",
});

workflow.addEdge(START, "reply");

export default workflow;
```

构建和推送：

```bash
kapso build
kapso push --dry-run
kapso push workflow <workflow-slug>
```

使用 `kapso push` 推送所有本地函数和工作流。有关存储库布局、源文件行为和仅 JSON 编辑的信息，请参阅 `references/local-workflow-source.md`。

### 首先发现电话号码

首选路径：
1. 检查项目状态：`kapso status`
2. 列出连接的号码：`kapso whatsapp numbers list --output json`
3. 在需要时解析显示号码：`kapso whatsapp numbers resolve --phone-number "<display-number>" --output json`

备用路径：
1. 列出触发器号码配置：`node scripts/list-whatsapp-phone-numbers.js`

### 通过 API 脚本编辑工作流图

优先本地源同步进行工作流编辑。在调试、直接图检查或仅 API 环境中，使用这些脚本作为备用。

1. 获取图：`node scripts/get-graph.js <workflow_id>`（注意 `lock_version`）
2. 编辑 JSON（见下文图规则）
3. 验证：`node scripts/validate-graph.js --definition-file <path>`
4. 更新：`node scripts/update-graph.js <workflow_id> --expected-lock-version <n> --definition-file <path>`
5. 重新获取以确认

对于小编辑，使用 `edit-graph.js` 并使用 `--old-file` 和 `--new-file`。

如果遇到 `lock_version` 冲突：重新获取，重新应用更改，使用新的 `lock_version` 重试。

### 管理触发器

1. 列出：`node scripts/list-triggers.js <workflow_id>`
2. 创建：`node scripts/create-trigger.js <workflow_id> --trigger-type <type> --phone-number-id <id>`
3. 切换：`node scripts/update-trigger.js --trigger-id <id> --active true|false`
4. 删除：`node scripts/delete-trigger.js --trigger-id <id>`

对于 `inbound_message` 触发器，优先使用 `kapso whatsapp numbers resolve --phone-number "<display-number>" --output json` 获取确切的 `phone_number_id`。当 CLI 不可用时，回退到 `node scripts/list-whatsapp-phone-numbers.js`。

对于 `project_event` 触发器，当用户定义事件类型/模式时，首先注册或更新项目事件定义：

```bash
node scripts/project-event-definitions.js create \
  --name conversation.csat_scored \
  --description "Customer satisfaction score for a conversation" \
  --property-schema '{"score":{"type":"number"},"reason":{"type":"string"}}'
```

然后创建触发器：

```bash
node scripts/create-trigger.js <workflow_id> \
  --trigger-type project_event \
  --triggerable-attributes '{"event_name":"conversation.csat_scored","property_key":"score","operator":"gte","property_value":4}'
```

定义仅是元数据。除非用户明确接受副作用，否则不要仅为了注册名称而发射样本事件。

### 管理项目事件定义

使用定义来指定事件名称、描述和扁平标量属性模式。发射的事件是单独的记录，由 `POST /platform/v1/events`、`emit_event` 节点、Function 节点 `project_events` 或 Agent 节点 `emit_event` 创建。

1. 列出：`node scripts/project-event-definitions.js list`
2. 通过名称创建/更新：`node scripts/project-event-definitions.js create --name <event.name> [--description <text>] [--property-schema <json>]`
3. 通过 ID 更新：`node scripts/project-event-definitions.js update --definition-id <id> [--name <event.name>] [--description <text>] [--property-schema <json>]`

### 使用项目事件构建工作流

当工作流需要记住或对持久的业务事实做出反应时，使用此清单：

1. 当用户引入新的事件名称或模式时，首先定义事件。
2. 当工作流应响应发射的事件时，使用 `project_event` 触发器。
3. 使用 `emit_event` 节点进行确定性工作流步骤发射。
4. 当发射依赖于函数代码输出时，使用 Function 节点 `project_events`。
5. 仅当代理应决定是否/何时记录事实时，使用 Agent 节点 `emit_event`。在使用它之前，启用 `emit_event` 默认工具并配置允许的事件定义。

由项目事件触发的工工作是观察者，不能发射项目事件。不要向从项目事件触发开始的工作流添加事件发射。

### 调试执行

1. 当您有执行 ID 时，首先搜索工作流日志：`kapso logs search --query "<execution-id>" --source flow_event --filter flow_execution_id=<execution-id> --period 7d --limit 20 --output json`
2. 列出：`node scripts/list-executions.js <workflow_id>`
3. 检查：`node scripts/get-execution.js <execution-id>`
4. 获取值：`node scripts/get-context-value.js <execution-id> --variable-path vars.foo`
5. 事件：`node scripts/list-execution-events.js <execution-id>`

### 创建和部署函数

1. 使用处理程序签名编写代码（见下文函数规则）。
2. 创建：`node scripts/create-function.js --name <name> --code-file <path> [--public-endpoint true]`
3. 部署：`node scripts/deploy-function.js --function-id <id>`
4. 验证：`node scripts/get-function.js --function-id <id>`

当函数应通过 Kapso 托管的调用 URL 无需 `X-API-Key` 调用时，使用 `--public-endpoint true`。这仅适用于 Cloudflare 函数。
新函数默认为 `invoke_response_mode=passthrough`，在成功调用时直接返回函数正文。可以稍后使用 `update-function.js` 将旧包装函数迁移。

### 设置代理节点使用远程沙盒存储库

当代理需要在工作流运行期间需要一个远程临时工作区来检查或修改存储库文件时，使用此方法。

1. 阅读 `references/agent-remote-sandbox.md` 了解执行模型和字段规则。
2. 查找模型：`node scripts/list-provider-models.js`
3. 复制 `assets/agent-remote-sandbox-github-repo-example.json` 作为起点，或编辑 `data.config` 下的代理节点。
4. 设置 `sandbox_enabled: true`
5. 设置 `sandbox_network_mode` 为 `allow_all` 或 `allow_list`
6. 如果使用 `allow_list`，在 `sandbox_allowed_outbound_hosts` 中添加额外的出站主机。
7. 使用以下方式添加 GitHub 存储库到 `flow_agent_resources`：
   - `resource_type: "github_repository"`
   - `repo_url`
   - `branch`
   - `pat`
8. 编写系统提示，使其在做出更改之前明确从 `/workspace/repos/<repo-slug>` 读取。
9. 验证并更新图

注意：
- 远程沙盒是 Beta 版，在 Beta 期间免费
- `sandbox_enabled` 控制远程工作区和沙盒工具是否可用
- 存储库资源即使在后来关闭沙盒访问后仍然配置
- v1 仅支持 GitHub 存储库
- 使用存储库根 URL，而不是 GitHub 文件 URL 或 `tree/...` URL
- 存储库在远程沙盒中挂载到 `/workspace/repos/<repo-slug>`
- 使用 `references/agent-remote-sandbox.md` 和 `references/node-types.md` 了解确切的结构

## 图规则

- 恰好有一个 `id` = `start` 的起始节点
- 不要更改现有节点 ID
- 使用 `{node_type}_{timestamp_ms}` 作为新节点 ID
- 非决策节点有 0 或 1 个出站 `next` 边
- 决策边标签必须匹配 `conditions[].label`
- 边键是 `source`/`target`/`label`（不是 `from`/`to`）

有关完整模式详细信息，请参阅 `references/graph-contract.md`。

## 函数规则

```js
async function handler(request, env) {
  // 解析输入
  const body = await request.json();
  // 按需使用 env.KV 和 secrets
  return new Response(JSON.stringify({ result: "ok" }));
}
```

- 不要使用 `export`、`export default` 或箭头函数
- 返回一个 `Response` 对象

## 执行上下文

始终使用此结构：
- `vars` - 用户定义的变量
- `system` - 系统变量
- `context` - 频道数据
- `metadata` - 请求元数据

## 脚本

### 工作流

| 脚本 | 目的 |
|------|------|
| `list-workflows.js` | 列出工作流（仅元数据） |
| `get-workflow.js` | 获取工作流元数据 |
| `create-workflow.js` | 创建工作流 |
| `update-workflow-settings.js` | 更新工作流设置 |

### 图

| 脚本 | 目的 |
|------|------|
| `get-graph.js` | 获取工作流图 + `lock_version` |
| `edit-graph.js` | 通过字符串替换修补图 |
| `update-graph.js` | 替换整个图 |
| `validate-graph.js` | 本地验证图结构 |

### 触发器

| 脚本 | 目的 |
|------|------|
| `list-triggers.js` | 列出工作流的触发器 |
| `create-trigger.js` | 创建触发器 |
| `update-trigger.js` | 启用/禁用触发器 |
| `delete-trigger.js` | 删除触发器 |
| `list-whatsapp-phone-numbers.js` | 列出触发器设置的电话号码 |

### 项目事件

| 脚本 | 目的 |
|------|------|
| `project-event-definitions.js` | 列出、创建或更新项目事件定义 |

### 执行

| 脚本 | 目的 |
|------|------|
| `list-executions.js` | 列出执行 |
| `get-execution.js` | 获取执行详细信息 |
| `get-context-value.js` | 从执行上下文读取值 |
| `update-execution-status.js` | 强制执行状态 |
| `resume-execution.js` | 恢复等待执行 |
| `list-execution-events.js` | 列出执行事件 |

### 函数

| 脚本 | 目的 |
|------|------|
| `list-functions.js` | 列出项目函数 |
| `get-function.js` | 获取函数详细信息 + 代码 |
| `create-function.js` | 创建函数，可选带有公共调用端点 |
| `update-function.js` | 更新函数代码、公共端点设置或迁移旧包装函数到 passthrough |
| `deploy-function.js` | 部署函数到运行时 |
| `invoke-function.js` | 使用负载调用函数 |
| `list-function-invocations.js` | 列出函数调用 |

### OpenAPI

| 脚本 | 目的 |
|------|------|
| `openapi-explore.mjs` | 探索 OpenAPI (search/op/schema/where) |

安装依赖（一次）：
```bash
npm i
```

示例：
```bash
node scripts/openapi-explore.mjs --spec workflows search "variables"
node scripts/openapi-explore.mjs --spec workflows op getWorkflowVariables
```

## 注意事项

- 优先使用文件路径而不是内联 JSON (`--definition-file`, `--code-file`)
- 使用 `observe-whatsapp` 进行跨源日志搜索，当您在调试工作流时，同时进行 API 调用、Meta 事件或 webhook 交付。
- 变量 CRUD (`variables-set.js`, `variables-delete.js`) 被阻塞 - 平台 API 不支持它

## 参考

阅读您正在更改的操作的参考：
- [references/local-workflow-source.md](references/local-workflow-source.md) - 本地工作流源编辑和 CLI 同步
- [references/graph-contract.md](references/graph-contract.md) - 图编辑：模式、计算字段与可编辑字段、`lock_version`
- [references/node-types.md](references/node-types.md) - 添加或更改节点配置
- [references/workflow-overview.md](references/workflow-overview.md) - 执行行为、状态变化和恢复

对于仅函数的工作，请阅读下文的函数参考；如果工作流也更改，则需要图/源参考。其他任务特定参考：
- [references/execution-context.md](references/execution-context.md) - 上下文结构和变量替换
- [references/triggers.md](references/triggers.md) - 触发器类型和设置
- [references/agent-remote-sandbox.md](references/agent-remote-sandbox.md) - 远程沙盒行为、存储库资源、挂载路径
- [references/functions-reference.md](references/functions-reference.md) - 函数管理
- [references/functions-payloads.md](references/functions-payloads.md) - 函数的负载形状

## 资源

| 文件 | 描述 |
|------|------|
| `workflow-linear.json` | 最小线性工作流 |
| `workflow-decision.json` | 最小分支工作流 |
| `workflow-agent-simple.json` | 最小代理工作流 |
| `workflow-customer-support-intake-agent.json` | 客户支持摄入 |
| `workflow-interactive-buttons-decide-function.json` | 交互按钮 + 决策（函数） |
| `workflow-interactive-buttons-decide-ai.json` | 交互按钮 + 决策（AI） |
| `workflow-api-template-wait-agent.json` | API 触发器 + 模板 + 代理 |
| `function-decide-route-interactive-buttons.json` | 用于按钮路由的函数 |
| `agent-remote-sandbox-github-repo-example.json` | 带有远程沙盒和 GitHub 存储库资源的代理节点 |

## 相关技能

- `integrate-whatsapp` - Onboarding、webhooks、messaging、templates、flows
- `observe-whatsapp` - Debugging、logs、health checks

<!-- FILEMAP:BEGIN -->
```text
[automate-whatsapp file map]|root: .
|.:{package.json,SKILL.md}
|assets:{agent-remote-sandbox-github-repo-example.json,function-decide-route-interactive-buttons.json,functions-example.json,workflow-agent-simple.json,workflow-api-template-wait-agent.json,workflow-customer-support-intake-agent.json,workflow-decision.json,workflow-interactive-buttons-decide-ai.json,workflow-interactive-buttons-decide-function.json,workflow-linear.json}
|references:{agent-remote-sandbox.md,execution-context.md,function-contracts.md,functions-payloads.md,functions-reference.md,graph-contract.md,local-workflow-source.md,node-types.md,triggers.md,workflow-overview.md,workflow-reference.md}
|scripts:{create-function.js,create-trigger.js,create-workflow.js,delete-trigger.js,deploy-function.js,edit-graph.js,get-context-value.js,get-execution-event.js,get-execution.js,get-function.js,get-graph.js,get-workflow.js,invoke-function.js,list-execution-events.js,list-executions.js,list-function-invocations.js,list-functions.js,list-provider-models.js,list-triggers.js,list-whatsapp-phone-numbers.js,list-workflows.js,openapi-explore.mjs,project-event-definitions.js,resume-execution.js,update-execution-status.js,update-function.js,update-graph.js,update-trigger.js,update-workflow-settings.js,validate-graph.js,variables-delete.js,variables-list.js,variables-set.js}
|scripts/lib/functions:{args.js,kapso-api.js}
|scripts/lib/workflows:{args.js,kapso-api.js,result.js}
```
<!-- FILEMAP:END -->
