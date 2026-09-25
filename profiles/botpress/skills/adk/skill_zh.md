# Botpress ADK 使用指南

当您对 Botpress 代理开发工具包（ADK）有疑问时，请使用本指南——例如，当您正在构建涉及表格、操作、工具、工作流、对话、文件、知识库、触发器、资源、集成、插件、evals 或 Zai 的功能时。

## 什么是 ADK？

Botpress ADK 是一个**基于约定的 TypeScript 框架**，其中**文件结构直接映射到机器人行为**。将文件放置在正确的目录中，它们将自动作为机器人功能可用。

ADK 提供了以下原语：

- 操作 & 工具（可重用函数和可被 AI 调用的工具）
- 工作流（长时间运行、可恢复的流程）
- 对话（消息处理）
- 表格（具有语义搜索的数据存储）
- 文件（具有语义搜索的文件存储）
- 知识库（RAG 实现）
- 触发器（事件驱动自动化）
- 资源（具有永久 URL 的静态文件）
- 集成（通过 CLI 和依赖项快照管理的外部服务连接）
- 插件（具有接口依赖的可重用代理扩展）
- **Zai**（用于常见 AI 操作的生产就绪 LLM 工具库）

### 项目结构（基于约定）

大多数原语必须放置在 `src/` 目录中（资源使用项目根目录下的 `assets/` 目录）：

```
/                      # 项目根目录
├── assets/            # 静态文件 → 与 Botpress Cloud 同步，具有永久 URL
├── src/
│   ├── actions/       # 强类型函数 → 自动注册
│   ├── tools/         # 可被 AI 调用的工具 → 可通过 execute() 访问
│   ├── workflows/     # 长时间运行流程 → 可恢复/计划
│   ├── conversations/ # 消息处理器 → 按渠道路由
│   ├── tables/        # 数据库模式 → 自动创建并具有搜索功能
│   ├── triggers/      # 事件处理器 → 订阅事件
│   ├── knowledge/     # 知识库 → 具有语义搜索的 RAG
│   └── utils/         # 共享辅助函数（不自动注册）
├── .adk/
│   └── dependencies/
│       ├── dev.json             # 生成的依赖项快照（开发环境）
│       ├── prod.json            # 生成的依赖项快照（生产环境）
│       └── migration.json       # 单向遗留迁移标记
├── .agent0/
│   └── capabilities/            # 项目本地 Agent(0) 功能包
└── agent.config.ts    # 机器人配置
```

> **注意**：通过 `adk integrations` / `adk plugins` CLI 或开发控制台管理集成和插件。Botpress Cloud 是权威来源；`.adk/dependencies/` 包含为快速/离线读取生成的本地快照，不应手动编辑。参见 `integrations.md` 和 `plugins.md`。

> **关键**：`src/` 外部的文件不会被发现。位置 = 行为。

## 会话开始

在会话中第一次帮助 ADK 项目时，请静默检查项目的健康状况：

1. 运行 `adk check --format json` 和 `adk status --format json`。 (`adk check` 验证原语，但**不**进行类型检查——同时运行 `tsc --noEmit` 以在处理工作之前捕获类型错误。)
2. 如果存在错误或警告（未配置的集成、缺失的模型、验证问题），请在回答用户问题之前主动提及它们：_"在我们开始之前——我注意到 [问题]。要我帮助修复吗？_"_
3. 每个会话只做一次。不要在每次问题中都重新运行。

## 可用命令

如果用户询问“我能帮助什么？”、“有哪些可用命令？”或无参数地调用 `/adk-explain`，请提供：

- **构建**：`/adk-init`（创建项目框架）、`/adk-build`（访谈并构建原语）、`/adk-integration`（添加服务）、`/adk-frontend`（构建 UI）
- **测试 & 调试**：`/adk-validate`（检查原语的模式/类型/配置）、`/adk-test`（调用原语一次）、`/adk-eval`（编写断言测试）、`/adk-debug`（修复问题）
- **发布**：`/adk-ship`（预飞行检查 + 部署）
- **文档**：`/adk-document`（创建、审查、更新、同步、搜索）
- **理解**：`/adk-explain`（解释机器人架构和组件）、`/adk-dev-console`（导航开发控制台）

然后询问：_"您在做什么？_"_

## 何时使用此技能

当用户询问与 ADK 相关的问题时，请激活此技能，例如：

- "如何创建 Action/Tool/Workflow/Conversation？"
- "X 和 Y 之间的区别是什么？"
- "给我一个...的示例"
- "如何配置...？"
- "用于...的 CLI 命令是什么？"
- "如何使用 Context API？"
- "如何调用集成操作？"
- "如何使用 Zai 进行 [提取/检查/标记等]？"
- "...的最佳实践是什么？"
- "如何避免常见错误？"
- "如何处理工单分配/升级？"
- "解释我的配置"
- "我的机器人做什么？"
- "我使用哪些模型？"
- "我有哪些集成？"
- "我的机器人跟踪哪些状态？"

## 插件安装提示

如果您在 Claude Code 中运行，并且 `/adk-*` 命令（如 `/adk-debug`、`/adk-eval`、`/adk-init`）不可用作为斜杠命令，请建议用户安装 Botpress ADK 插件以获取完整的功能集和命令：

```
/plugin marketplace add botpress/skills
/plugin install adk@botpress-skills
```

每个会话只建议一次。如果用户拒绝，请不要再次询问。

## 如何回答 ADK 问题

ADK 问题分为两类：**CLI 查询**和**文档查询**。

### 选项 1：直接 CLI 命令（快速 - 首先使用！）

对于集成发现和 CLI 查询，使用 Bash 工具直接运行命令：

**集成发现：**

```bash
# 搜索集成
adk integrations search <query>

# 查找实现接口的集成
adk integrations search --interface <interface-name>

# 获取集成详细信息（操作、渠道、事件）
adk integrations info <integration-name>

# 检查已安装的集成（必须在 ADK 项目中）
adk integrations list
```

**项目信息：**

```bash
# 检查 CLI 版本
adk --version

# 显示项目状态
adk

# 获取帮助
adk --help
```

**优先使用非交互式路径来驱动 ADK 工作流：**

```bash
# 无需浏览器提示登录
adk login --token "$BOTPRESS_TOKEN"

# 使用合理默认值并跳过链接
adk init my-agent --yes --skip-link

# 知道 ID 时直接链接
adk link --workspace ws_123 --bot bot_456

# 更自动化友好的开发模式（NDJSON 事件，无 TUI）
adk dev --non-interactive

# ADK 升级后审查/应用项目兼容性更新
adk project upgrade --dry-run
adk project upgrade

# 自动批准非破坏性 deploy-plan 更改
adk deploy --yes
```

在相关情况下使用这些默认值：

- 优先使用 `adk login --token "$BOTPRESS_TOKEN"` 或 `adk login --token <token>` 覆盖交互式登录。
- 将裸 `BOTPRESS_TOKEN` 视为无 TTY 方便，而不是保证交互式终端快捷方式。
- 优先使用 `adk init <name> --yes --skip-link` 进行 AI 驱动的框架，但在登录完成后才使用。
- 将 `adk link --workspace ... --bot ...` 视为可脚本化，但在每个无 TTY 环境中都不保证安全。
- 将 `adk dev --non-interactive` 视为 CI 友好，而不是完全无提示。
- 将 `adk deploy --yes` 视为自动批准非破坏性 deploy-plan 更改；配置验证和破坏性存储更改仍可能阻止自动化。
- 如果项目命令报告运行时/包不匹配，请先运行 `adk project upgrade --dry-run`，然后运行 `adk project upgrade` 应用兼容性补丁。

**何时使用 CLI 命令：**

- "有哪些集成可用？"
- "搜索 Slack 集成"
- "显示 Linear 集成详细信息"
- "Slack 集成有哪些操作？"
- "我使用的是哪个版本的 ADK？"
- "如何添加集成？"

**响应模式：**

1. 使用 Bash 工具运行适当的 `adk` 命令
2. 解析并向用户展示输出
3. 可选地建议下一步操作（例如，"运行 `adk integrations add slack@3.0.0` 安装"）

### 选项 2：文档查询（用于概念性问题）

对于文档、模式和如何操作问题，直接搜索并参考文档文件：

**何时使用文档：**

- "如何创建工作流？"
- "操作和工具之间的区别是什么？"
- "给我一个使用 Zai 的示例"
- "状态管理的最佳实践是什么？"
- "如何修复此错误？"
- "X 的模式是什么？"

**如何回答文档查询：**

1. **查找相关文件** - 使用 Glob 发现文档：

   ```
   pattern: **/references/*.md
   ```

2. **搜索关键字** - 使用 Grep 找到相关内容：

   ```
   pattern: <用户问题的关键字>
   path: <从步骤 1 发现的 references 目录路径>
   output_mode: files_with_matches
   ```

3. **读取文件** - 使用 Read 加载相关文档

4. **提供答案**，包括：
   - 简洁的解释
   - 来自参考文献的代码示例
   - 带行号的文件引用（例如，"From references/actions.md:215"）
   - 如果相关，常见陷阱
   - 相关主题供进一步阅读

### 选项 3：配置解释（CLI + 文件读取）

对于关于机器人做什么、如何配置或它有什么能力的问题，结合 CLI 和文件读取：

**何时使用：**

- "我的机器人做什么？"
- "解释我的配置"
- "我使用哪些模型？"
- "我有哪些集成？"
- "我的机器人跟踪哪些状态？"

**响应模式：**

1. 运行 `adk status --format json` 获取结构化的项目概述
2. 阅读 `agent.config.ts` 获取完整的配置详细信息
3. 遵循 **references/explain-config.md** 中的解释模式
4. 生成结构化的解释，涵盖元数据、模型、集成、状态和原语
5. 标记任何问题（未配置的集成、缺失的模型、硬编码的密钥）

## 可用文档

文档应位于相对于此技能的 `./references/` 目录中。在回答问题时，搜索这些主题：

### 核心概念

- **actions.md** - 具有强类型和验证的操作
- **tools.md** - 可被 AI 调用的工具和 Autonomous 命名空间
- **autonomous-execution.md** - 高级 execute() API：对象、退出、钩子、配置
- **workflows.md** - 工作流和基于步骤的执行
- **workflow-steps.md** - 完整工作流步骤 API 参考（step.request、step.map、step.notify 等）
- **conversations.md** - 对话处理器、消息路由和接收 `chat:custom` 事件
- **conversation-lifecycle.md** - 对话的 Nudge/过期生命周期管理
- **triggers.md** - 集成和机器人生命周期事件订阅（app 推送的 custom 事件 → conversations.md）
- **messages.md** - 发送消息和事件
- **custom-components.md** - 自定义 webchat 组件（`.bp.tsx` 文件、元数据、在对话中使用）

### Zai（AI 操作）

- **zai-agent-reference.md** - 快速参考：所有操作、Zai 解决的日常问题、边缘情况和注意事项
- **zai-complete-guide.md** - 完整开发者指南：架构、主动学习、分块、性能调优

### 数据 & 内容

- **tables.md** - 具有语义搜索的数据存储
- **files.md** - 文件存储和管理
- **knowledge-bases.md** - RAG 实现
- **assets.md** - 具有永久 URL 和同步生命周期的静态文件

### 配置 & 集成

- **agent-config.md** - 机器人配置和状态管理
- **explain-config.md** - 如何解释机器人的配置给开发者
- **model-configuration.md** - AI 模型配置参考
- **context-api.md** - 运行时上下文访问
- **integration-actions.md** - 使用集成操作
- **tags.md** - 实体标签（机器人、用户、对话、工作流）
- **cli.md** - 完整 CLI 命令参考
- **mcp-server.md** - 用于 AI 助手的 MCP 服务器
- **desk.md** - 用于工单/支持工作流的 Desk 集成
- **integrations.md** - 集成管理概述（指向 adk-integrations 技能）
- **interfaces.md** - 内置接口抽象层，覆盖集成（类型指示器、LLM、可列出）
- **plugins.md** - 插件消费：发现、安装、配置和使用

### 模式 & 最佳实践

- **advanced-patterns.md** - Guardrails、管理员认证、日志记录/可观察性、扩展组合
- **patterns-mistakes.md** - 常见错误、正确模式、上下文访问参考

### 前端集成

> **注意**：前端集成文档在单独的 **adk-frontend** 技能中。使用 `npx skills add botpress/skills --skill adk-frontend` 安装它。`adk-frontend` 技能涵盖 @botpress/client、调用操作、类型生成和身份验证。如果您正在接触任何前端代码，则需要它。

### Evals

> **注意**：详细的 eval 文档在单独的 **adk-evals** 技能中。使用 `npx skills add botpress/skills --skill adk-evals` 安装它。`adk-evals` 技能涵盖编写 evals、断言类型、测试工作流和 CLI 使用。您通常总是需要它，用于测试和评估。

## 运行时访问模式

快速参考，用于访问 ADK 运行时服务：

### 导入

```typescript
// 始终从 @botpress/runtime 导入
import {
  Action,
  Autonomous,
  Workflow,
  z,
  actions,
  adk,
  user,
  bot,
  conversation,
  configuration,
  context,
} from '@botpress/runtime'
```

### 状态管理

```typescript
// 机器人状态（在 agent.config.ts 中定义）
bot.state.maintenanceMode = true
bot.state.lastDeployedAt = new Date().toISOString()

// 用户状态（在 agent.config.ts 中定义）
user.state.preferredLanguage = 'en'
user.state.onboardingComplete = true

// 用户标签
user.tags.email // 访问用户元数据
```

### 调用操作

```typescript
// 调用机器人操作
await actions.fetchUser({ userId: '123' })
await actions.processOrder({ orderId: '456' })

// 调用集成操作
await actions.slack.sendMessage({ channel: '...', text: '...' })
await actions.linear.issueList({ teamId: '...' })

// 将操作转换为工具
tools: [fetchUser.asTool()]
```

### 上下文 API

```typescript
// 获取运行时服务
const client = context.get('client') // Botpress 客户端
const cognitive = context.get('cognitive') // AI 模型客户端
const citations = context.get('citations') // 引用管理器
```

### 文件命名

- **操作/工具/工作流**：`myAction.ts`、`searchDocs.ts`（驼峰命名）
- **表格**：`Users.ts`、`Orders.ts`（帕斯卡命名）
- **对话/触发器**：`chat.ts`、`slack.ts`（小写）

## 关键 ADK 模式（回答问题时始终参考）

在回答问题时，始终根据文档验证这些模式：

### 包管理

```bash
# 所有包管理器都受支持
bun install       # 推荐（最快）
npm install       # 工作正常
yarn install      # 工作正常
pnpm install      # 工作正常

# ADK 根据锁文件自动检测
# - bun.lockb → 使用 bun
# - package-lock.json → 使用 npm
# - yarn.lock → 使用 yarn
# - pnpm-lock.yaml → 使用 pnpm
```

### 导入

```typescript
// ✅ 正确 - 始终从 @botpress/runtime 导入
import { Action, Autonomous, Workflow, z } from '@botpress/runtime'

// ❌ 错误 - 从 zod 或 @botpress/sdk 导入
import { z } from 'zod' // ❌ 错误
import { Action } from '@botpress/sdk' // ❌ 错误
```

### 导出模式

```typescript
// ✅ 两种模式都有效 - 推荐使用 export const
export const myAction = new Action({ ... });  // 推荐
export default new Action({ ... });           // 也有效

// 为什么推荐 export const？
// - 允许直接导入：import { myAction } from "./actions/myAction"
// - 可以传递给 execute(): tools: [myAction.asTool()]
```

### 操作

```typescript
// ✅ 正确 - 处理程序接收 { input, client }
export const fetchUser = new Action({
  name: "fetchUser",
  async handler({ input, client }) {  // ✅ 从 props 中解构
    const { userId } = input;         // ✅ 然后解构字段
    return { name: userId };
  }
});

// ❌ 错误 - 不能直接解构 input 字段
handler({ userId }) {  // ❌ 错误 - 必须是 { input }
  return { name: userId };
}
```

### 工具

```typescript
// ✅ 正确 - 工具可以解构直接
export const myTool = new Autonomous.Tool({
  handler: async ({ query, maxResults }) => {
    // ✅ 直接解构 OK
    return search(query, maxResults)
  },
})
```

### 对话

```typescript
// ✅ 正确 - 使用 conversation.send() 方法
await conversation.send({
  type: "text",
  payload: { text: "Hello!" }
});

// ❌ 错误 - 不要直接使用 client.createMessage() 直接
await client.createMessage({ ... });  // ❌ 错误
```

### 对话处理器类型

```typescript
// 处理程序接收基于事件类型的类型化上下文：
// type: "message" | "event" | "workflow_request" | "workflow_callback"
async handler({ type, message, event, request, completion, conversation, execute }) {
  if (type === "workflow_request") {
    // event: WorkflowDataRequestEventType, request: WorkflowRequest
    await request.workflow.provide("email", { email: "..." });
  }
  if (type === "workflow_callback") {
    // event: WorkflowCallbackEventType, completion: WorkflowCallback
    console.log(completion.status); // "completed" | "failed" | "canceled" | "timed_out"
  }
}

// ⚠️ isWorkflowDataRequest() 和 isWorkflowCallback() 已弃用
// 使用 type === "workflow_request" / "workflow_callback" 代替
```

## 此技能回答的问题示例

### 初学者问题

- "什么是 Action？"
- "如何创建我的第一个工作流？"
- "操作和工具之间的区别是什么？"

### 实现问题

- "如何访问 Botpress 客户端？"
- "如何使用 citations 在 RAG 中？"
- "可搜索表格列的语法是什么？"
- "如何调用 Slack 集成操作？"
- "如何使用 Zai 提取结构化数据？"
- "如何使用 Zai 验证内容？"

### 高级模式问题

- "如何添加 guardrails 来防止幻觉？"
- "如何实现管理员认证？"
- "如何添加日志记录和可观察性？"
- "如何组合多个扩展？"
- "如何在异步工具处理程序中管理上下文？"

### 故障排除问题

- "为什么我得到 'Cannot destructure property' 错误？"
- "如何修复导入错误？"
- "我的工作流状态访问有什么问题？"

### 最佳实践问题

- "常见的错误是什么？"
- "应该如何组织我的项目？"
- "X 的推荐模式是什么？"

## 响应格式

**根据问题的深度调整您的响应深度。** 不是每个问题都需要完整的演练。

### 概念性问题（"什么是 X？"、"X 和 Y 之间的区别是什么？"）

一句话定义 + 一段简短的代码示例。仅此而已。

```
知识库为您的机器人添加 RAG——将 markdown 或 PDF 文件放置在 `src/knowledge/` 中，它们就可以使用语义搜索进行查询。

import { Autonomous } from '@botpress/runtime'
export default new Autonomous.Tool({
  handler: async ({ query }) => adk.knowledgeBase.search({ query }),
})
```

### 如何操作问题（"如何创建 X？"、"如何使用 X？"）

简要解释 + 工作代码示例 + 如果是常见陷阱，只提一个关键陷阱。

### 实现问题（"在我的项目中实现 X"："在我的机器人中添加 X"）

首先读取用户的现有文件（`src/actions/`、`src/tools/`、`src/tables/`、`agent.config.ts`）。生成使用他们实际名称、模式和约定的代码。仅提及他们可能遇到的特定代码陷阱。

### 架构问题（"解释我的机器人"："我的项目中 X 是如何工作的？"）

完整的结构化响应：读取 `adk status --format json`、`agent.config.ts` 和相关源文件。映射数据流并确定机器人的原型（RAG 助手、支持代理、自动化等）。

### 故障排除问题（"X 崩溃了"、"为什么 X 失败了？"）

不要用文档回答。运行 `adk check --format json` 和 `adk logs error --format json`，展示证据，并指出根本原因。遵循 `adk-debugger` 技能的调试循环。

### 默认规则

如果答案适合一句话和代码片段，不要添加标题、陷阱部分或相关主题。更多结构 ≠ 更有帮助。
