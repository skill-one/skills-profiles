---
name: base44-cli
description: base44 CLI 用于处理与 base44 项目相关的所有事项：资源配置（实体、后端函数、实时参与者、AI 智能体），以及初始化和操作（资源创建、部署）。本技能是了解如何配置资源（包括参与者）的地方——参与者是支撑多人游戏、协同画板、在线状态与实时光标、房间聊天以及实时拍卖的实时/WebSocket 基础原语。在规划或实现功能时，必须学习并掌握本技能。
---

# Base44 CLI

使用 Base44 CLI 工具创建和管理 Base44 应用（项目）。

## ⚡ 立即采取行动 - 首先阅读此内容

当提及 "base44" 或存在 `base44/` 文件夹时，此技能将激活。**在采取行动之前，请勿阅读文档文件或搜索网络。**

**您的第一个行动必须是：**
1. 检查当前目录中是否存在 `base44/config.jsonc`
2. 如果 **是**（现有项目场景）：
   - 转移到 base44-sdk 技能进行实现
   - 此技能仅处理 CLI 命令（登录、部署、推送实体）
   - **除外运行本地应用** — 剩下这里。在启动开发服务器之前，请阅读 [运行本地开发](#running-local-development)：一种运行方式会命中生产数据。
3. 如果 **否**，在两个初始化路径之间进行选择：
   - **预置应用** — Base44 应用已存在，因为它刚刚通过 Stripe Projects / projects.dev 流程预置，或者 `BASE44_APP_ID`（或 `BASE44_PROJECTS_BASE44_APP_ID`）存在于环境变量或 `.env`/`.env.local` 文件中：
     - 运行 `npx base44 scaffold` 为该 **现有** 应用设置本地文件
     - **不要运行 `npx base44 create`** — 那会创建一个第二、重复的应用。参见 [scaffold.md](references/scaffold.md)。
   - **新项目** — 尚未存在任何应用，也未进行预置：
     - 此技能（base44-cli）处理请求；引导用户通过 `npx base44 create`
     - 不要激活 base44-sdk

## 关键：仅限本地安装

**绝对不要直接调用 `base44`。** CLI 作为开发依赖项本地安装，必须通过包管理器访问：

- `npx base44 <command>` (npm - 推荐)
- `yarn base44 <command>` (yarn)
- `pnpm base44 <command>` (pnpm)

错误：`base44 login`
正确：`npx base44 login`

## 必须在会话开始时进行身份验证检查

**关键**：在每次 AI 会话开始且此技能被激活时，您**必须**：

1. **通过运行以下命令检查身份验证状态**：
   ```bash
   npx base44 whoami
   ```

2. **如果用户已登录**（命令成功并显示电子邮件）：
   - 继续执行请求的任务

3. **如果用户未登录**（命令失败或显示错误）：
   - **立即停止**
   - **不要**继续任何 CLI 操作
   - **要求用户手动登录**，通过运行：
     ```bash
     npx base44 login
   ```
   - 等待用户确认已登录后再继续

**此检查是强制性的，必须在执行任何其他 Base44 CLI 命令之前进行。**

**通过 Stripe Projects / projects.dev 预置？** 当应用通过该流程预置时，CLI 从它注入的 `BASE44_ACCESS_TOKEN` / `BASE44_REFRESH_TOKEN` 环境变量中种子身份验证（`BASE44_PROJECTS_*`-前缀的名称会自动规范化）。在这种情况下，`npx base44 whoami` 已经成功，您**不需要**交互式 `npx base44 login`。

**已设置工作区 API 密钥？** 如果 `BASE44_API_KEY` 环境变量设置为工作区 API 密钥（前缀为 `b44k_`），CLI 直接使用它进行身份验证 — `npx base44 whoami` 和其他命令无需交互式登录即可成功。

## 概述

Base44 CLI 提供用于身份验证、创建项目、管理实体和部署 Base44 应用的命令行工具。它是框架无关的，可与流行的前端框架（如 Vite、Next.js、Create React App、Svelte、Vue 等）一起使用。

## 何时使用此技能与 base44-sdk

**使用 base44-cli 时：**
- 从零开始创建 **新** Base44 项目
- 在空目录中初始化项目
- 为外部预置的**现有**应用（例如，通过 Stripe Projects / projects.dev 流程）设置本地文件 → 使用 `scaffold`
- 目录中缺少 `base44/config.jsonc`
- 用户提及："创建一个新项目"、"初始化项目"、"设置一个项目"、"开始一个新的 Base44 应用"
- 通过 CLI 部署、推送实体或进行身份验证
- 使用 CLI 命令 (`npx base44 ...`)

**使用 base44-sdk 时：**
- 在**现有** Base44 项目中构建功能
- `base44/config.jsonc` 已存在
- 使用 JavaScript/TypeScript 代码编写 Base44 SDK
- 实现功能、组件或特性
- 用户提及："实现"、"构建一个功能"、"添加功能"、"编写代码"

**技能依赖关系：**
- `base44-cli` 是新项目中 `base44-sdk` 的**先决条件**
- 如果用户想要"创建一个应用"且不存在 Base44 项目，则首先使用 `base44-cli`
- `base44-sdk` 假设 Base44 项目已初始化

**状态检查逻辑：**
在选择技能之前，检查：
- IF (用户提及 "创建/构建应用" 或 "制作项目")：
  - IF (`base44/config.jsonc` 存在)：
    → 使用 **base44-sdk**（项目存在，构建功能）
  - ELSE IF (应用外部预置 — `BASE44_APP_ID`/`BASE44_PROJECTS_BASE44_APP_ID` 设置，或刚刚运行了 Stripe Projects / projects.dev 流程)：
    → 使用 **base44-cli** → `npx base44 scaffold`（为现有应用设置本地文件；不要 `create`）
  - ELSE：
    → 使用 **base44-cli** → `npx base44 create`（需要初始化新项目）

## 项目结构

Base44 项目结合了标准前端项目和一个 `base44/` 配置文件夹：

```
my-app/
├── base44/                      # Base44 配置（由 CLI 创建）
│   ├── config.jsonc             # 项目设置、站点配置
│   ├── .types/                  # 自动生成的 TypeScript 类型（由 `types generate` 创建）
│   │   └── types.d.ts           # 为 @base44/sdk 的模块增强
│   ├── entities/                # 实体模式定义
│   │   ├── task.jsonc
│   │   └── board.jsonc
│   ├── functions/               # 后端函数（可选）
│   │   └── my-function/
│   │       └── entry.ts
│   ├── actors/                  # 实时演员（可选）
│   │   └── ChatRoom/
│   │       └── entry.ts
│   ├── agents/                  # 代理配置（可选）
│   │   └── support_agent.jsonc
│   ├── agent-skills/            # 代理技能说明（可选）
│   │   └── pdf-export.md
│   └── connectors/              # OAuth 连接器配置（可选）
│       └── googlecalendar.jsonc
├── src/                         # 前端源代码
│   ├── api/
│   │   └── base44Client.js      # Base44 SDK 客户端
│   ├── pages/
│   ├── components/
│   └── main.jsx
├── index.html                   # SPA 入口点
├── package.json
└── vite.config.js               # 或您的框架的配置文件
```

**关键文件：**
- `base44/config.jsonc` - 项目名称、描述、站点构建设置
- `base44/entities/*.jsonc` - 数据模型模式（参见实体模式部分）
- `base44/functions/*/entry.ts` - 后端函数入口点
- `base44/actors/*/entry.ts` - 实时演员入口点（可选）
- `base44/agents/*.jsonc` - 代理配置（可选）
- `base44/agent-skills/*.md` - 代理技能说明（可选）
- `base44/.types/types.d.ts` - 自动生成的实体、函数和代理的 TypeScript 类型（由 `npx base44 types generate` 创建）
- `base44/connectors/*.jsonc` - OAuth 连接器配置（可选）
- `src/api/base44Client.js` - 前端使用的预配置 SDK 客户端

**config.jsonc 示例：**
```jsonc
{
  "name": "My App",                    // 必须的：项目名称
  "description": "App description",    // 可选的：项目描述
  "visibility": "public",              // 可选的："public" | "private" | "workspace"
  "entitiesDir": "./entities",         // 可选的：默认 "entities"
  "functionsDir": "./functions",       // 可选的：默认 "functions"
  "actorsDir": "./actors",             // 可选的：默认 "actors"
  "agentsDir": "./agents",             // 可选的：默认 "agents"
  "agentSkillsDir": "./agent-skills",  // 可选的：默认 "agent-skills"
  "connectorsDir": "./connectors",     // 可选的：默认 "connectors"
  "site": {                            // 可选的：站点部署配置
    "installCommand": "npm install",   // 可选的：安装依赖项
    "buildCommand": "npm run build",   // 可选的：构建命令
    "serveCommand": "npm run dev",     // 可选的：本地开发服务器
    "outputDirectory": "./dist"        // 可选的：构建输出目录
  }
}
```

**配置属性：**

| 属性 | 描述 | 默认值 |
|----------|-------------|---------|
| `name` | 项目名称（必须） | - |
| `description` | 项目描述 | - |
| `visibility` | 应用可见性：`public`、`private` 或 `workspace` | - |
| `entitiesDir` | 实体模式所在的目录 | `"entities"` |
| `functionsDir` | 后端函数所在的目录 | `"functions"` |
| `actorsDir` | 实时演员所在的目录 | `"actors"` |
| `agentsDir` | 代理配置所在的目录 | `"agents"` |
| `agentSkillsDir` | 代理技能说明所在的目录 | `"agent-skills"` |
| `connectorsDir` | 连接器配置所在的目录 | `"connectors"` |
| `site.installCommand` | 安装依赖项的命令 | - |
| `site.buildCommand` | 构建项目的命令 | - |
| `site.serveCommand` | 运行开发服务器的命令 | - |
| `site.outputDirectory` | 部署的构建输出目录 | - |

## 安装

将 Base44 CLI 作为开发依赖项安装到您的项目中：

```bash
npm install --save-dev base44
```

**重要**：永远不要假设或硬编码 `base44` 包版本。始终无版本指定地安装以获取最新版本。

然后使用 `npx` 运行命令：

```bash
npx base44 <command>
```

**注意**：此文档中的所有命令都使用 `npx base44`。您也可以使用 `yarn base44`，或者如果更喜欢，使用 `pnpm base44`。

## 全局 `--app-id` 选项

CLI 具有全局 `--app-id <id>` 选项，用于仅需要应用上下文而不需要本地项目文件的命令。

**解析顺序**：`--app-id` 标志 → `BASE44_APP_ID` 环境变量 → 本地 `base44/.app.jsonc`

当您想要在不切换到链接的项目目录的情况下检查或操作应用时，这很有用。常见示例：

```bash
# 对特定应用运行一次性脚本
cat ./script.ts | npx base44 exec --app-id app_123

# 获取已部署应用的日志，而无需本地签出
npx base44 logs --app-id app_123 --level error
```

使用 `--app-id` 进行应用范围的命令，如 `exec` 和 `logs`。

**不要**使用 `--app-id` 用于需要本地项目文件的命令：
- `base44 create` 创建新应用，因此它拒绝 `--app-id`
- `base44 dev` 从链接的本地项目运行，因此它拒绝 `--app-id`
- `base44 deploy` 仍然需要本地项目目录，因为它读取本地资源

## 全局 `--json` 选项

CLI 具有全局 `--json` 选项，使命令发出机器可读的 JSON 文档到 stdout 而不是面向人类的输出。它还强制非交互模式（旋转器/状态消息/日志移动到 stderr），因此 stdout 保持纯 JSON — 安全地可以管道到 `jq` 或其他程序。

```bash
npx base44 connectors list-available --json
npx base44 logs --app-id app_123 --json
```

## 可用命令

### 身份验证

| 命令         | 描述                                     | 参考                                   |
| --------------- | ----------------------------------------------- | ------------------------------------------- |
| `base44 login`  | 使用设备代码流程通过 Base44 进行身份验证 | [auth-login.md](references/auth-login.md)   |
| `base44 logout` | 从当前设备注销                          | [auth-logout.md](references/auth-logout.md) |
| `base44 whoami` | 显示当前已认证用户                      | [auth-whoami.md](references/auth-whoami.md) |

### 项目管理

| 命令 | 描述 | 参考 |
|---------|-------------|-----------|
| `base44 create` | 从模板创建新的 Base44 项目 | [create.md](references/create.md) ⚠️ **必须阅读** |
| `base44 scaffold` | 为现有 Base44 应用（通过应用 ID）搭建本地项目 | [scaffold.md](references/scaffold.md) |
| `base44 link` | 将现有本地项目链接到 Base44 | [link.md](references/link.md) |
| `base44 eject` | 下载现有 Base44 项目的代码 | [eject.md](references/eject.md) |
| `base44 dashboard open` | 在浏览器中打开应用仪表板 | [dashboard.md](references/dashboard.md) |
| `base44 visibility <level>` | 在服务器上设置应用的可见性 (`public`、`private` 或 `workspace`) | [visibility.md](references/visibility.md) |

### 工作区管理

工作区（又名组织）将应用分组在共享成员下。默认情况下 `base44 create`/`base44 link --create` 使用您的个人工作区；传递 `-w, --workspace <id>` 可指定另一个。

| 命令 | 描述 | 参考 |
|---------|-------------|-----------|
| `base44 workspace list` | 列出您所属的工作区 | [workspace-list.md](references/workspace-list.md) |
| `base44 workspace get <workspace-id>` | 通过 ID 显示单个工作区的详细信息 | [workspace-get.md](references/workspace-get.md) |
| `base44 workspace move [workspace-id]` | 将当前应用移动到另一个工作区 | [workspace-move.md](references/workspace-move.md) |

### 开发

| 命令 | 描述 | 参考 |
|---------|-------------|-----------|
| `base44 dev` | 启动您的 Base44 后端本地开发，当 `site.serveCommand` 配置时，也启动前端 | [dev.md](references/dev.md) |
| `base44 dev --remote` | 在本地本地服务器上提供前端，对**生产**后端 | [dev.md](references/dev.md) |

### 部署

| 命令 | 描述 | 参考 |
|---------|-------------|-----------|
| `base44 build` | 构建站点并注入其应用 ID — 取代裸 `npm run build` | — |
| `base44 deploy` | 部署所有资源（实体、函数、演员、代理、代理技能、连接器、身份验证配置和站点）；询问是否先构建，或传递 `--build` / `--no-build` | [deploy.md](references/deploy.md) |

### 实体管理

| 操作 / 命令       | 描述                                 | 参考                                           |
| ---------------------- | ------------------------------------------- | --------------------------------------------------- |
| 创建实体        | 在 `base44/entities` 文件夹中定义实体 | [entities-create.md](references/entities-create.md) |
| `base44 entities push` | 将本地实体推送到 Base44               | [entities-push.md](references/entities-push.md)     |
| RLS 模式           | 行级安全示例和操作符                   | [rls-examples.md](references/rls-examples.md) ⚠️ **阅读 RLS** |

#### 实体模式（快速参考）

创建实体文件时**始终**遵循此确切结构：

**文件命名**：`base44/entities/{kebab-case-name}.jsonc`（例如，`team-member.jsonc` 用于 `TeamMember`）

**模式模板**：
```jsonc
{
  "name": "EntityName",
  "type": "object",
  "properties": {
    "field_name": {
      "type": "string",
      "description": "字段描述"
    }
  },
  "required": ["field_name"]
}
```

**字段类型**：`string`、`number`、`integer`、`boolean`、`array`、`object`、`binary`
**字符串格式**：`date`、`date-time`、`time`、`email`、`uri`、`hostname`、`ipv4`、`ipv6`、`uuid`、`file`、`regex`、`richtext`
**对于枚举**：添加 `"enum": ["value1", "value2"]`，并可选地 `"default": "value1"`
**实体名称**：必须仅包含字母数字（模式：`/^[a-zA-Z0-9]+$/`）

有关完整文档，请参阅 [entities-create.md](references/entities-create.md)。

### 函数管理

| 操作 / 命令          | 描述                                   | 参考                                               |
| --------------------- | -------------------------------------- | ------------------------------------------------- |
| 创建函数             | 在 `base44/functions` 中定义函数       | [functions-create.md](references/functions-create.md) |
| `base44 functions deploy [names...] [--force]` | 将本地函数部署到 Base44；可选择针对特定函数或清理已移除的函数 | [functions-deploy.md](references/functions-deploy.md)   |
| `base44 functions delete <names...>` | 从 Base44 删除一个或多个已部署的函数     | [functions-delete.md](references/functions-delete.md) |
| `base44 functions list`   | 列出 Base44 远程上所有已部署的函数      | [functions-list.md](references/functions-list.md)       |
| `base44 functions pull [name]` | 将已部署的函数从 Base44 拉取到本地文件 | [functions-pull.md](references/functions-pull.md)  |

### 工作流运行

工作流是自动化系统（计划任务、实体触发器、连接器事件、应用内代理操作）。这些命令是只读的：它们回答“存在哪些工作流”以及“我的计划任务是否失败，原因是什么”。

| 命令 | 描述 | 参考 |
|------|------|------|
| `base44 workflows list` | 列出此应用的具有状态和运行摘要的工作流 | [workflows-list.md](references/workflows-list.md) |
| `base44 workflows runs [--status <s>] [--since <t>]` | 列出工作流运行，最新优先；失败的运行包括底层错误 | [workflows-runs.md](references/workflows-runs.md) |

### 代理管理

代理是具有状态的实时服务器房间，通过 WebSocket 实现——每个房间 ID 有一个实时实例，由所有连接到该 ID 的客户端共享。用于多人会话、协作板、在线状态和光标、房间内聊天和实时拍卖。

代理使用 SDK 管理的认证进行直接连接。使用验证的 `conn.identity` 进行用户归属，使用 `this.client.asServiceRole` 持久化验证的房间结果。代理不会接收应用密钥；将依赖于密钥的操作放在后端函数中。参见 [actors-create.md](references/actors-create.md) 了解编写合同。

| 操作 / 命令 | 描述 | 参考 |
| ------------ | ---- | ---- |
| 创建代理     | 在 `base44/actors` 中定义代理 | [actors-create.md](references/actors-create.md) |
| `base44 actors deploy [names...]` | 将本地代理部署到 Base44；可选择针对特定代理 | [actors-deploy.md](references/actors-deploy.md) |
| `base44 actors delete <names...>` | 拆除已部署的代理（销毁发布的脚本） | [actors-deploy.md](references/actors-deploy.md#deleting-a-deployed-actor) |

#### 代理布局（快速参考）

**文件命名：** `base44/actors/{ActorName}/entry.ts` — 文件夹是代理的身份。

```javascript
// base44/actors/ChatRoom/entry.ts
import { Actor } from "base44:runtime/actors";

export default class ChatRoom extends Actor {
  handleConnect(conn) { conn.send({ type: "welcome" }); }   // 仅此客户端
  handleMessage(conn, msg) {
    // 始终验证：有效负载受攻击者控制，msg 甚至可能为 null。
    if (msg?.type !== "message" || typeof msg.text !== "string") return;
    this.broadcast({ type: "message", text: msg.text.slice(0, 2000) });   // 整个房间
  }
  handleClose(conn) {}
}
```

**命名规则：** 代理名称成为 JavaScript 类绑定和 WebSocket 连接处理程序——它们必须匹配 `[A-Za-z_][A-Za-z0-9_]*`（最大 128 个字符，不能包含 `/`、`-`、`.` 或 `:`），不能是 JS 保留字，不能与后端函数名称冲突，并且不能嵌套在子文件夹中。CLI 在上传前本地检查所有这些内容；带有点的文件夹会被跳过（所以 `ChatRoom.bak/` 是安全的临时空间）。
- 有效：`ChatRoom`，`BoardRoom`，`Lobby`
- 无效：`chat-room`，`games/Arena`，`class`

**必需：** `entry.ts`（或 `entry.js`）默认导出一个扩展自 `base44:runtime/actors` 的 `Actor` 类。在 TypeScript 中，还声明 `handleTick() {}`——它是 `Actor` 的抽象成员。

**与函数的区别：** 仅上传代理自己的文件夹（没有 `base44/shared/`），没有 `--force` 清理，没有 `list`/`pull` 命令，没有本地 `base44 dev` 运行时，名称不能是路径形式，不支持自动化。

有关完整文档，参见 [actors-create.md](references/actors-create.md)。

### 代理管理

代理是会话式 AI 助手，可以与用户交互、访问应用实体并调用后端函数。使用这些命令管理代理配置。

| 操作 / 命令        | 描述                             | 参考                                       |
| ------------------- | -------------------------------- | ------------------------------------------ |
| 创建代理           | 在 `base44/agents` 文件夹中定义代理 | 见代理模式下方                          |
| `base44 agents pull`    | 将远程代理拉取到本地文件         | [agents-pull.md](references/agents-pull.md)     |
| `base44 agents push`    | 将本地代理推送到 Base44             | [agents-push.md](references/agents-push.md)     |

**注意：** 代理命令执行完全同步——推送用本地代理替换所有远程代理，拉取用远程代理替换所有本地代理。

#### 代理模式（快速参考）

**文件命名：** `base44/agents/{agent_name}.jsonc`（例如，`support_agent.jsonc`）

**模式模板：**
```jsonc
{
  "name": "agent_name",
  "description": "简要描述此代理的作用",
  "instructions": "详细说明代理的行为",
  "tool_configs": [
    // 实体工具 - 给代理访问实体操作权限
    { "entity_name": "tasks", "allowed_operations": ["read", "create", "update", "delete"] },
    // 后端函数工具 - 给代理访问一个函数
    { "function_name": "send_email", "description": "发送电子邮件通知" }
  ],
  "memory_config": {                 // 可选：让代理记住跨会话的事实
    "enabled": true,
    "scope": "both",                 // "global" | "user" | "both"
    "include_other_conversation_context": false,
    "instructions": null
  },
  "whatsapp_greeting": "你好！今天我能帮你什么？"
}
```

**命名规则：** 代理名称必须匹配模式：`/^[a-z0-9_]+$/`（小写字母数字和下划线，1-100 个字符）
- 有效：`support_agent`，`order_bot`
- 无效：`Support-Agent`，`OrderBot`

**必需字段：** `name`，`description`，`instructions`
**可选字段：** `tool_configs`（默认为 `[]`），`memory_config`，`whatsapp_greeting`

**工具配置类型：**
- **实体工具**：`entity_name` + `allowed_operations`（数组：`read`，`create`，`update`，`delete`）
- **后端函数工具**：`function_name` + `description`

**内存配置字段**（全部可选，参见 [agents-push.md](references/agents-push.md#memory-configuration) 了解详情）：`enabled`（布尔值，默认 `true`），`scope`（`global`|`user`|`both`，默认 `both`），`include_other_conversation_context`（布尔值，默认 `false`），`instructions`（字符串|null，默认 `null`）

### 代理技能管理

代理技能是可重用的 Markdown 指令，扩展了应用 AI 代理知道如何做的事情。使用这些命令管理它们。

| 操作 / 命令             | 描述                                    | 参考                                                     |
| ----------------------- | --------------------------------------- | -------------------------------------------------------- |
| 创建代理技能          | 在 `base44/agent-skills` 文件夹中定义技能   | [agent-skills-push.md](references/agent-skills-push.md#agent-skill-file-format) |
| `base44 agent-skills pull`   | 将远程代理技能拉取到本地文件         | [agent-skills-pull.md](references/agent-skills-pull.md)       |
| `base44 agent-skills push`   | 将本地代理技能推送到 Base44               | [agent-skills-push.md](references/agent-skills-push.md)       |

**注意：** 代理技能命令执行完全同步——推送用本地技能替换所有远程技能，拉取用远程技能替换所有本地技能。

#### 代理技能模式（快速参考）

**文件命名：** `base44/agent-skills/{skill-name}.md`（例如，`pdf-export.md`）

**模式模板：**
```markdown
---
description: 将当前报告导出为 PDF 并附加到会话中。
---

当用户要求导出、下载或分享报告为 PDF 时使用此技能。

1. 调用 `generate_report_pdf` 函数，传入当前报告的实体 ID。
2. 在回复中附加返回的文件 URL。
```

**命名规则：** 技能名称（文件名减 `.md`）必须匹配模式 `/^[a-z0-9]+(-[a-z0-9]+)*$/`（小写字母数字和连字符，1-64 个字符）
- 有效：`pdf-export`，`order-lookup`
- 无效：`PdfExport`，`pdf_export`

**必需字段：** `description`（前文，1-1024 个字符），正文（Markdown 内容，1-15000 个字符）

有关完整文档，参见 [agent-skills-push.md](references/agent-skills-push.md)。

### 连接器管理

连接器让应用连接到外部服务（Google Calendar、Slack、Stripe 等）。大多数连接器使用 OAuth 提供访问令牌，供后端函数调用外部 API。Stripe 是例外——它在服务器端自动配置，没有 OAuth 浏览器流程。

| 操作 / 命令                   | 描述                                          | 参考                                                           |
| ---------------------------- | --------------------------------------------- | ---------------------------------------------------------------- |
| 创建连接器                  | 在 `base44/connectors` 文件夹中定义连接器      | [connectors-create.md](references/connectors-create.md)             |
| `base44 connectors list-available` | 列出 Base44 提供的所有集成类型     | [connectors-list-available.md](references/connectors-list-available.md) |
| `base44 connectors initiate --integration-type <t> [--scopes <s...>]` | 初始化连接器并开始其 OAuth 流程；使用 `--app-id` 可无项目运行 | [connectors-initiate.md](references/connectors-initiate.md) |
| `base44 connectors pull`           | 将远程连接器拉取到本地文件                | [connectors-pull.md](references/connectors-pull.md)                 |
| `base44 connectors push`           | 将本地连接器推送到 Base44                      | [connectors-push.md](references/connectors-push.md)                 |

**注意：** 连接器命令执行完全同步——推送用本地连接器替换所有远程连接器（并触发 OAuth 新的 OAuth 连接器），拉取用远程连接器替换所有本地连接器。

#### 连接器模式（快速参考）

**文件命名：** `base44/connectors/{type}.jsonc`（例如，`googlecalendar.jsonc`，`slack.jsonc`）

**模式模板：**
```jsonc
{
  "type": "googlecalendar",
  "scopes": [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events"
  ]
}
```

**必需字段：** `type`
**可选字段：** `scopes`（默认为 `[]`）

**可用的连接器类型：** 运行 `npx base44 connectors list-available` 查看所有支持的集成类型。

**注意：** `stripe` 也是一个有效的连接器类型，但不会返回 `list-available`。将其视为支持类型——它由 Base44 自动配置，没有 OAuth 浏览器流程。参见 [connectors-create.md](references/connectors-create.md) 了解详情。

有关完整文档，参见 [connectors-create.md](references/connectors-create.md)。

### 认证配置

管理应用的认证设置（例如，用户名和密码登录）。认证配置存储在 `base44/auth/` 中，通过 `auth push`/`auth pull` 与 Base44 同步。

| 命令 | 描述 | 参考 |
|------|------|------|
| `base44 auth password-login <enable\|disable>` | 启用或禁用用户名和密码认证 | [auth-password-login.md](references/auth-password-login.md) |
| `base44 auth social-login <provider> <enable\|disable>` | 启用或禁用社交登录（google、microsoft、facebook、apple） | [auth-social-login.md](references/auth-social-login.md) |
| `base44 auth sso <enable\|disable>` | 配置 SSO 身份提供者（google、microsoft、github、okta、自定义） | [auth-sso.md](references/auth-sso.md) |
| `base44 auth pull` | 将认证配置从 Base44 拉取到本地文件 | [auth-pull.md](references/auth-pull.md) |
| `base44 auth push` | 将本地认证配置推送到 Base44 | [auth-push.md](references/auth-push.md) |

**注意：** 认证配置作为 `base44 deploy` 的一部分进行部署。

### 密钥管理

管理项目密钥（安全存储在 Base44 中的环境变量）。这些命令不在 `--help` 输出中显示，但完全可用。

| 命令 | 描述 | 参考 |
|------|------|------|
| `base44 secrets list` | 列出所有密钥的名称 | [secrets-list.md](references/secrets-list.md) |
| `base44 secrets set` | 设置一个或多个密钥（KEY=VALUE 或 --env-file） | [secrets-set.md](references/secrets-set.md) |
| `base44 secrets delete <key>` | 通过名称删除密钥 | [secrets-delete.md](references/secrets-delete.md) |

### 脚本执行

使用预认证的 Base44 SDK 对应用运行一次性脚本。用于对实体执行 CRUD 操作（`base44.entities.MyEntity.list/create/update/delete`）、调用后端函数（`base44.functions.invoke("myFunction", args)`）、调用代理或访问 SDK 暴露的任何其他资源——无需部署完整函数。适用于数据迁移、批量操作、调试和脚本化工作流。

| 命令 | 描述 | 参考 |
|------|------|------|
| `base44 exec` | 通过 stdin 运行脚本，使用预认证的 Base44 SDK | [exec.md](references/exec.md) |

### 类型生成

| 命令 | 描述 | 参考 |
|------|------|------|
| `base44 types generate` | 从实体、函数、代理、代理和连接器生成 TypeScript 类型（`types.d.ts`） | [types-generate.md](references/types-generate.md) |

**输出：** `base44/.types/types.d.ts` — 增强 `@base44/sdk` 模块，添加了类型化注册表（`EntityTypeRegistry`，`FunctionNameRegistry`，`AgentNameRegistry`，`ConnectorTypeRegistry`，`ActorNameRegistry`）。

**无需认证。** 完全在本地运行。自动更新 `tsconfig.json` 以包含生成的类型。

### 网站管理

| 命令              | 描述                               | 参考                                   |
| ----------------- | ---------------------------------- | ------------------------------------- |
| `base44 site deploy` | 将构建的网站文件部署到 Base44 托管 | [site-deploy.md](references/site-deploy.md) |
| `base44 site open`   | 在浏览器中打开已部署的网站    | [site-open.md](references/site-open.md)     |

**仅限 SPA**：Base44 托管支持单页应用程序，具有单个 `index.html` 入口点。所有路由都从 `index.html` 提供（客户端路由）。

## 快速入门

1. 在项目中安装 CLI：
   ```bash
   npm install --save-dev base44
   ```

2. 使用 Base44 进行认证：
   ```bash
   npx base44 login
   ```

3. 创建新项目（始终提供名称和 `--path` 标志）：
   ```bash
   npx base44 create my-app --path .
   ```

4. 运行本地开发：
   ```bash
   npx base44 dev
   ```

5. 构建并部署所有内容：
   ```bash
   npx base44 deploy --build -y
   ```

或部署单个资源：
- `npx base44 entities push` - 仅推送实体
- `npx base44 functions deploy` - 仅部署函数
- `npx base44 functions delete <name>` - 删除已部署的函数
- `npx base44 functions list` - 列出所有已部署的函数
- `npx base44 functions pull` - 将已部署的函数拉取到本地文件
- `npx base44 actors deploy` - 仅部署实时演员
- `npx base44 actors delete <name>` - 拆卸已部署的演员
- `npx base44 agents push` - 仅推送代理
- `npx base44 agent-skills push` - 仅推送代理技能
- `npx base44 connectors pull` - 从 Base44 拉取连接器
- `npx base44 connectors push` - 仅推送连接器
- `npx base44 auth pull` - 从 Base44 拉取认证配置
- `npx base44 auth push` - 仅推送认证配置
- `npx base44 site deploy -y` - 仅部署站点

## 常见工作流

### 创建新项目

**⚠️ 必须执行：在运行 `base44 create` 之前，你必须阅读 [create.md](references/create.md) 以了解：**
- **模板选择** - 选择正确的模板（`backend-and-client` 对比 `backend-only`）
- **正确的工作流** - 不同的模板需要不同的设置步骤
- **常见陷阱** - 避免导致失败的文件夹创建错误

不遵循 create.md 说明会导致项目脚手架损坏。

### 关联现有项目
```bash
# 如果你拥有 base44/config.jsonc 但没有 .app.jsonc
npx base44 link --create --name my-app
```

### 运行本地开发

始终通过 CLI 运行——两种模式：

| 命令 | 后端 + 数据 |
|------|------------|
| `npx base44 dev` | **本地**——一次性，每次启动时清空，停止时消失 |
| `npx base44 dev --remote` | **生产**——真实应用的实时数据 |

`base44 dev` 启动本地后端（实体、函数、认证）并在 `base44/config.jsonc` 设置 `site.serveCommand` 时提供前端服务；纯后端项目不需要其他任何东西。`--remote` 仅运行前端对真实后端，因此需要关联的项目和 `site.serveCommand`。

不要自己运行 `npm run dev`：没有 CLI 注入的环境变量，应用没有后端可连接——开发服务器会打印出应使用的命令。

**默认使用 `npx base44 dev`。** 在 `--remote` 下每次写入都会命中真实应用。无论哪种方式，vite 启动行都会命名后端：`[base44] 代理已启用：/api -> <目标>`。说明你启动了什么。选项：[dev.md](references/dev.md)。

### 部署所有更改
```bash
# 生成类型（可选，用于 TypeScript 项目）
npx base44 types generate

# 部署所有内容（实体、函数和站点），先构建站点
npx base44 deploy --build -y
```

通过 CLI 构建，而不是用 `npm run build`：`npx base44 build` 注入 `VITE_BASE44_APP_ID`，而裸 `npm run build` 会留空——打包后无法解析自己的应用，部署站点的每个 API 调用都会失败。`npx base44 deploy` 会询问是否先构建；`--build` / `--no-build` 会提前回答（非交互式默认为仅上传，因此 CI 不变）。

### 生成 TypeScript 类型
```bash
# 从实体、函数、演员、代理和连接器生成类型
npx base44 types generate
```

这会创建 `base44/.types/types.d.ts`，其中包含 `@base44/sdk` 模块的类型化注册表。更改实体、函数、演员、代理或连接器后运行此命令以保持类型同步。无需认证。

### 部署单个资源
```bash
# 仅推送实体
npx base44 entities push

# 仅部署函数（全部）
npx base44 functions deploy
# 部署特定函数
npx base44 functions deploy my-function other-function
# 部署并删除已移除的函数
npx base44 functions deploy --force

# 仅部署演员（全部）
npx base44 actors deploy
# 部署特定演员
npx base44 actors deploy ChatRoom BoardRoom
# 拆卸已部署的演员
npx base44 actors delete ChatRoom

# 仅推送代理
npx base44 agents push

# 仅推送代理技能
npx base44 agent-skills push

# 从 Base44 拉取连接器
npx base44 connectors pull

# 仅推送连接器
npx base44 connectors push

# 仅部署站点
npx base44 site deploy -y
```

### 打开仪表盘
```bash
# 在浏览器中打开应用仪表盘
npx base44 dashboard
```

## 认证

大多数命令需要认证。如果你未登录，CLI 会自动提示你登录。你的会话存储在本地，并在 CLI 会话之间持续存在。

## 故障排除

| 错误                       | 解决方案                                                                            |
|---------------------------|----------------------------------------------------------------------------------- |
| 未认证                    | 先运行 `npx base44 login`                                                          |
| 未找到实体                | 确保 `base44/entities/` 目录中存在实体                                             |
| 实体未识别                | 确保文件使用连字符命名（例如，`team-member.jsonc` 而不是 `TeamMember.jsonc`）         |
| 未找到函数                | 确保 `base44/functions/` 目录中存在函数，并包含 `entry.ts` 或 `entry.js`             |
| 未找到演员                | 确保 `base44/actors/<ActorName>/entry.ts` 中存在演员（永远不会直接在 `base44/actors/` 中） |
| 无效的演员名称            | 演员名称必须匹配 `[A-Za-z_][A-Za-z0-9_]*`（不能包含 `/`、`-`、`.` 或 `:`），避免 JS 保留字，且不能嵌套。在上传前本地捕获 |
| `actors cannot be nested` | 展平为 `base44/actors/<ActorName>/entry.ts`，或重命名你称为 `entry.ts` 的辅助文件——`base44/actors/` 下每个入口文件都计为演员 |
| 演员和函数共享名称        | 它们部署到一个命名空间——重命名其中一个                                                 |
| 演员文件在函数桶中被拒绝   | 导入 `base44:runtime/actors` 的文件必须位于 `base44/actors/<ActorName>/entry.ts`——将其从 `base44/functions/` 中移出 |
| 未找到代理                | 确保 `base44/agents/` 目录中存在代理，并包含有效的 `.jsonc` 配置                      |
| 无效的代理名称            | 代理名称必须为小写字母数字，仅包含下划线                                             |
| 未找到代理技能            | 确保技能文件存在于 `base44/agent-skills/` 目录，并包含有效的 `.md` 文件                |
| 无效的技能文件            | 技能文件名必须为小写连字符，并在其 frontmatter 中包含 `description`                   |
| 推送取消 / 需要 --yes      | `agents push`、`agent-skills push`、`entities push` 和 `connectors push` 是破坏性全同步——交互式确认或 CI/非交互式模式下传递 `-y`/`--yes` |
| 未找到连接器              | 确保 `base44/connectors/` 目录中存在连接器，并包含有效的 `.jsonc` 配置                  |
| 无效的连接器类型          | 运行 `npx base44 connectors list-available` 查看有效类型                             |
| 重复的连接器类型          | 每个连接器类型在一个项目中只能定义一次                                             |
| 连接器授权超时            | 重新运行 `npx base44 connectors push` 并在浏览器中完成 OAuth 流程                   |
| 未找到站点配置            | 检查项目配置中是否配置了 `site.outputDirectory`                                     |
| 站点部署失败              | 确保站点已先构建（`npx base44 build`，或 `npx base44 deploy --build`）且构建成功        |
| 部署站点的 API 调用全部失败 | 打包时未包含其应用 ID——使用 `npx base44 build` 重新构建，而不是裸 `npm run build`，然后重新部署 |
| 更新可用消息              | 如果提示更新，运行 `npm install -g base44@latest`（或使用 npx 进行本地安装）         |
