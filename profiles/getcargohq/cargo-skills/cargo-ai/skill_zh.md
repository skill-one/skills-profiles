# Cargo CLI — AI

代理资源管理：创建和配置代理、附加知识以用于检索增强生成（RAG）、连接MCP服务器以及管理代理记忆。

> 要使用代理（发送消息、多轮聊天、轮询），请使用 `cargo-orchestration`。
> 要上传知识**文件**并构建知识**库**（`content` 域），请使用 [`cargo-content`](../cargo-content/SKILL.md)。此技能涵盖了知识如何附加到代理。
> 要进行工作区管理——文件夹（用于组织代理和文件）、用户、API令牌、角色以及在CLI失败时提交报告，请使用 [`cargo-workspace-management`](../cargo-workspace-management/SKILL.md)。

> 请参阅 `references/response-shapes.md` 获取完整的JSON响应结构。
> 请参阅 `references/troubleshooting.md` 获取常见错误及其解决方法。
> 请参阅 `references/examples/agents.md` 获取代理CRUD和配置示例。
> 请参阅 `references/examples/mcp-servers.md` 获取MCP服务器创建和管理示例。

## Bootstrap

已经登录 (`cargo-ai whoami` 返回工作区)？跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令前缀 `npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 通过邮件验证，无需浏览器；首次使用时创建账户
                                        # 替代方案：--oauth（浏览器） · --token <api-token>（CI）
cargo-ai whoami                         # 在任何写入操作之前确认活动工作区
```

每个命令都向stdout打印JSON；失败时以非零状态退出并打印 `{"errorMessage": "..."}`。创建运行或批处理操作都是异步的——传递 `--wait-until-finished` 或轮询匹配的 `get`。当完整技能包安装后，[`../cargo/references/prerequisites.md`](../cargo/references/prerequisites.md) 会添加CLI版本锁定、令牌范围和管理员专用的界面。

## 首先发现资源

```bash
cargo-ai ai agent list                     # 所有代理（uuid、名称、描述）
cargo-ai ai template list                  # 所有AI代理模板（slug、名称）
cargo-ai ai mcp-server list                # 所有MCP服务器（uuid、名称）
cargo-ai ai memory list --scope agent --agent-uuid <uuid>  # 代理记忆
# 知识文件和库位于 content 域——请参阅 cargo-content：
#   cargo-ai content file list   /   cargo-ai content library list
```

**在UI中检索：** 代理位于 `app.getcargo.io/workspaces/<WORKSPACE_UUID>/agents/<AGENT_UUID>`。从 `cargo-ai whoami` 下的 `workspace.uuid` 获取 `<WORKSPACE_UUID>`。

## 快速参考

```bash
cargo-ai ai agent list
cargo-ai ai agent get <agent-uuid>
cargo-ai ai agent create --name <name> --icon-color blue --icon-face 🤖
cargo-ai ai agent update --uuid <agent-uuid> --name <name>
cargo-ai ai agent remove <agent-uuid>
cargo-ai ai release list --agent-uuid <uuid>
cargo-ai ai release get <release-uuid>
cargo-ai ai release get-draft --agent-uuid <uuid>
cargo-ai ai release update-draft --agent-uuid <uuid> --language-model-slug gpt-4o
cargo-ai ai release deploy-draft --agent-uuid <uuid>
cargo-ai ai template list                  # 完整详细信息；没有 `template get`
cargo-ai ai mcp-server list
cargo-ai ai mcp-server create --name "Internal Tools"
cargo-ai ai mcp-server update --uuid <mcp-server-uuid> --name "Updated Name"
cargo-ai ai mcp-server remove <mcp-server-uuid>
cargo-ai ai mcp-client connect --name "My MCP" --url https://mcp.example.com/sse
cargo-ai mcp                               # 通过stdio提供平台MCP
cargo-ai mcp --server <mcp-server-uuid>    # 提供一个精选的工作区MCP服务器
cargo-ai ai memory list --scope agent --agent-uuid <uuid>
cargo-ai ai memory update --mem0-id <id> --scope agent --agent-uuid <uuid> --content "Updated memory"
cargo-ai ai memory remove --mem0-id <id> --scope agent --agent-uuid <uuid>
```

## 代理

代理是具有配置指令、语言模型、操作和可选资源的AI资源。

**在从零开始创建代理之前，请检查现有的模板——它们捕获了常见用例（如线索研究、分类、邮件起草）的成熟模式，并为您提供现成的系统提示、模型和温度以供开始：**

```bash
cargo-ai ai template list          # 浏览模式——完整详细信息，不是摘要
# 没有 `template get` 子命令：`list` 已经返回 systemPrompt、temperature、
# languageModelSlug、actions 和 resources，因此选择您想要的即可
cargo-ai ai template list | jq '.templates[] | select(.slug == "<slug>")' 
```

```bash
# 列出所有代理
cargo-ai ai agent list

# 获取单个代理（包括部署的发布详细信息）
cargo-ai ai agent get <agent-uuid>

# 创建代理
cargo-ai ai agent create \
  --name "Lead Researcher" \
  --icon-color blue --icon-face 🤖 \
  --description "Researches leads and enriches data"

# 更新代理
cargo-ai ai agent update --uuid <agent-uuid> \
  --name "Senior Lead Researcher" \
  --description "Updated description"

# 移动到文件夹（通过 cargo-workspace-management 找到文件夹UUID）
cargo-ai ai agent update --uuid <agent-uuid> --folder-uuid <folder-uuid>

# 删除代理
cargo-ai ai agent remove <agent-uuid>
```

**代理图标：** `--icon-color` 必须是以下之一：`grey`、`green`、`purple`、`yellow`、`blue`、`red`。`--icon-face` 是一个表情字符串。

**文件夹：** 文件夹的创建、列出和管理位于 [`cargo-workspace-management`](../cargo-workspace-management/SKILL.md) (`cargo-ai workspaceManagement folder list/create/...`)。使用该技能来发现或创建传递给 `--folder-uuid` 的 `<folder-uuid>`。

## 发布

发布是代理配置的版本化快照（系统提示、操作、资源、模型、温度）。代理针对其部署的发布执行。

```bash
# 列出代理的发布
cargo-ai ai release list --agent-uuid <uuid>

# 获取特定发布
cargo-ai ai release get <release-uuid>

# 获取当前草稿发布（可编辑）
cargo-ai ai release get-draft --agent-uuid <uuid>

# 更新草稿发布
cargo-ai ai release update-draft --agent-uuid <uuid> \
  --system-prompt "You are a lead research assistant..." \
  --language-model-slug gpt-4o \
  --temperature 0.3 \
  --max-steps 10

# 部署草稿发布（使其生效）
cargo-ai ai release deploy-draft --agent-uuid <uuid> \
  --integration-slug openai \
  --language-model-slug gpt-4o \
  --actions '[]' \
  --mcp-clients '[]' \
  --resources '[]' \
  --capabilities '[]' \
  --suggested-actions '[]' \
  --description "Added research actions"
```

### 结构化输出和心跳——尚未作为CLI标志公开

发布API的有效负载（`draft/update` 和 `draft/deploy`）接受两个字段，这些字段**`release update-draft` / `release deploy-draft` 不作为标志显示**（通过CLI源验证——没有 `--output` / `--output-schema` 或 `--heartbeat`）：

| 字段 | 形状 | 目的 |
|---|---|---|
| `output` | `{"type":"text"}` **或** `{"type":"jsonSchema","jsonSchema": <标准JSON Schema对象>}` | 强制代理返回匹配JSON Schema的结构化输出。 |
| `heartbeat` | `{"intervalMinutes": number, "maxMessages": number, "prompt": string \| null}` | 定期重新唤醒聊天（`intervalMinutes`），直到达到 `maxMessages`；`prompt` 是唤醒消息（null = 通用“继续”）。 |

通用 `--options` 标志**不**包含这些——API的 `options` 仅包含 `{connectorUuidsByIntegrationSlug, modelUuidsByIntegrationSlug}`。在标志推出之前，使用与CLI使用的相同端点的直接API调用设置这些：

```bash
# 草稿发布上的结构化（JSON Schema）输出
curl -sS -X PUT "$CARGO_API_BASE/v1/ai/releases/draft/update" \
  -H "Authorization: Bearer $CARGO_TOKEN" -H "Content-Type: application/json" \
  -d '{"agentUuid":"<uuid>","output":{"type":"jsonSchema","jsonSchema":{"type":"object","properties":{"score":{"type":"number"}},"required":["score"]}}}'
# 部署携带相同的字段——POST .../v1/ai/releases/draft/deploy
```

将其他字段更新的有效负载与这些一起发送（端点替换草稿配置）。**提交 `workspaceManagement report`**（请参阅 [`../cargo-workspace-management/SKILL.md`](../cargo-workspace-management/SKILL.md)）以请求一流的 `--output` / `--heartbeat` 标志——这是CLI/UI差异的文档化反馈渠道。

**代理配置工作流：**

1. **浏览模板以获取灵感**：`cargo-ai ai template list` — 它返回每个模板的完整信息（系统提示、模型、温度、操作），因此直接从该响应中选择最接近您用例的模板
2. 创建代理：`cargo-ai ai agent create --name "..." --icon-color blue --icon-face 🤖`
3. 获取草稿发布：`cargo-ai ai release get-draft --agent-uuid <uuid>`
4. 使用配置的操作、资源、提示、模型更新草稿：`cargo-ai ai release update-draft --agent-uuid <uuid> ...`
5. 部署：`cargo-ai ai release deploy-draft --agent-uuid <uuid> ...`

## 模板

模板是预构建的代理配置，它们捕获了常见用例的成熟模式。**在从头开始设计代理之前，请始终检查模板**——它们为您提供现成的系统提示、推荐的模型、温度和工具配置，您可以照搬或进行修改。

```bash
# 列出可用的代理模板——每个条目都是完整的，因此这是您唯一需要的调用。没有 `template get` 子命令。
cargo-ai ai template list

# 通过slug检查一个：过滤相同的响应
cargo-ai ai template list | jq '.templates[] | select(.slug == "<slug>")' 
```

模板包括系统提示、操作、资源和推荐模型设置。将其用作起点，并通过 `release update-draft` 进行自定义。有关完整指南，包括从模板创建代理的端到端示例，请参阅 `references/examples/templates.md`。

## 模型和温度指南

| 用例 | 推荐模型 | 温度 |
|---|---|---|
| 分类、提取、评分 | `gpt-4o-mini` 或 `claude-3-5-haiku` | `0.0` – `0.2` |
| 研究、摘要、分析 | `gpt-4o` 或 `claude-3-5-sonnet` | `0.2` – `0.5` |
| 文案写作、个性化 | `gpt-4o` 或 `claude-3-5-sonnet` | `0.5` – `0.8` |
| 头脑风暴、创意构思 | `gpt-4o` 或 `claude-opus` | `0.7` – `1.0` |

低温度（`0.0`–`0.2`）= 确定性、一致的输出。高温度（`0.7`+）= 创造性、多样的输出。对于处理数千条记录的生产工作流，请优先选择低温度。

## 用于RAG的知识（文件和库）

用于锚定代理响应（检索增强生成，RAG）的知识来自**`content`** 域——请参阅 [`cargo-content`](../cargo-content/SKILL.md)：

- **文件**——上传的二进制文件（PDF、CSV、文本）。
- **库**——分组文件的集合，可以是 `native`（工作区管理）或 `connector`-支持的（通过非结构化数据提取器从外部源同步）。

> 文件和库从 `ai` 移动到顶级 **`content`** 域（CLI ≥ 1.0.19）（`cargo-ai content file …` / `cargo-ai content library …`）。旧的 `ai file …` 命令已删除。所有与内容相关的操作现在位于 [`cargo-content`](../cargo-content/SKILL.md)。

### 将知识附加到代理

文件或库在通过草稿发布的 `resources` 数组将其附加到代理并部署后才会生效。在 [`cargo-content`](../cargo-content/SKILL.md) 中上传文件/构建库，然后在此处使用 `release update-draft --resources …` 接着 `release deploy-draft` 进行连接。请参阅 [`../cargo-content/references/examples/files.md`](../cargo-content/references/examples/files.md) 获取完整的上传→连接→部署序列。

## MCP——两个方向，不要混淆它们

MCP（模型上下文协议）在Cargo中双向运行，且两个界面互不相关：

| | **发布** — `ai mcp-server` | **消费** — `ai mcp-client` |
|---|---|---|
| 它是什么 | 一个**您的**工作区暴露的服务器：您选择的可调用工具、代理和数据 | 一个**到**其他人的连接 |
| 谁调用它 | 任何MCP客户端——Claude Code、Claude Desktop、Cursor、ChatGPT | 您的Cargo代理，在聊天或工作流运行期间 |
| 通过什么连接 | `cargo-ai mcp --server <uuid>`（stdio桥接，下方） | `release update-draft --mcp-clients …` |

**在构建之前，请检查平台MCP是否已经覆盖了它。** Cargo现在在 `https://mcp.getcargo.io/mcp` 提供一个第一方MCP——每个工作区成员，无需部署——带有用于操作工作区的固定小工具集（`whoami`、`get_usage`、`search_actions`、`get_action_schema`、`autocomplete_action`、`execute_action`、`execute_action_batch`、`get_run`、`get_batch`、`list_runs`、`list_models`、`describe_model`、`query_models`）。托管客户端（ChatGPT连接器、Claude.ai、Cursor over HTTP）指向该URL并使用OAuth登录；当用户属于多个工作区时，同意屏幕会选择工作区。`ai mcp-server` 用于其他工作：一个**精选的、命名的**子集——这个工具、那个代理、这个过滤模型——用于应该看到确切内容且不包含任何其他内容的客户端。

### 发布工作区MCP服务器

```bash
cargo-ai ai mcp-server list
cargo-ai ai mcp-server create --name "CRM tools" \
  --actions '[{"slug":"<tool-uuid>","kind":"tool","name":null,"description":null,"isBulkAllowed":false,"config":{}}]' \
  --resources '[{"kind":"model","slug":"<slug>","name":"Accounts","description":null,"integrationSlug":"hubspot","modelUuid":null,"filter":null,"selectedColumnSlugs":null,"limit":null,"prompt":null,"isReadOnly":true}]'
cargo-ai ai mcp-server update --uuid <mcp-server-uuid> --name "Updated name"
cargo-ai ai mcp-server remove <mcp-server-uuid>
```

- **操作**接受 `kind: "tool"` **或** `kind: "agent"`——代理可以作为可调用的MCP工具暴露，而不仅仅是工具。`waitUntilFinished` 控制调用是否在运行时阻塞。
- **资源**接受 `kind: "model"`（模型的过滤、列选择的视图——保持 `isReadOnly: true`，除非客户端意味着要写入）或 `kind: "file"`（工作区文件通过UUID，请参阅 [`../cargo-content/SKILL.md`](../cargo-content/SKILL.md)）。
- **功能**（`--capabilities`，CLI ≥ 1.0.86）在服务器上暴露Cargo自己的内置工具，以及您的操作和资源。JSON数组 `{slug, config}`：
  ```bash
  cargo-ai ai mcp-server create --name "Research" \
    --capabilities '[{"slug":"webSearch","config":{}}]'
  ```
  九个slugs是 `sandbox`、`memory`、`context`、`app`、`document`、`webSearch`、`model`、`file` 和 `documentationSearch`——与**代理**发布接受的相同集，这就是为什么上面的示例传递 `'[]'` 而不是省略它的原因。在CDK项目中，相同的字段接受一个裸slug（`capabilities: ["webSearch"]`）。
- `update` 整体替换 `--actions` / `--resources` / `--capabilities` 而不是合并——使用 `mcp-server list` 当前服务器并传递完整的数组回。

### 为编码代理提供服务——`cargo-ai mcp`

任何服务器都可以通过CLI到达任何stdio MCP客户端，使用机器上已有的凭证。**不会将令牌复制到客户端配置中。**

```bash
claude mcp add cargo -- cargo-ai mcp                     # 平台MCP（无需设置）
cargo-ai ai mcp-server list                              # 找到一个精选服务器的UUID
claude mcp add cargo -- cargo-ai mcp --server <uuid>     # 那个精选服务器
# Cursor、Windsurf 和其他stdio客户端：与服务器条目相同的命令
```

如果没有 `--server`，桥接使用 `CARGO_MCP_SERVER_UUID`（如果设置），否则使用平台 `/mcp`。**这改变了：** 旧的CLI解析“工作区的唯一MCP服务器”，当工作区没有或多个时失败，裸 `cargo-ai mcp` 现在始终有东西要提供。stdout 承载MCP协议和所有日志发送到stderr，因此在其周围不要打印任何内容。

**何时选择此方案而不是技能：** 技能向代理提供整个CLI；MCP界面向其提供有界的集合并没有shell。用于会话中的查找和一次性操作，而CLI用于批处理、工作流、模式更改和任何有成本门禁的内容。完整路由规则：[`../cargo/SKILL.md`](../cargo/SKILL.md) → "这些技能与Cargo的MCP界面"。
