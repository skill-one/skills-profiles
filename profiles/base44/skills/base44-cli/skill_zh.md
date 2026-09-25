# Base44 CLI

使用 Base44 CLI 工具创建和管理 Base44 应用（项目）。

## ⚡ 立即采取行动 - 首先阅读此内容

当提及 "base44" 或存在 `base44/` 文件夹时，此技能将被激活。**在采取任何行动之前，请勿阅读文档文件或搜索网络。**

**您的第一个行动必须是：**
1. 检查当前目录中是否存在 `base44/config.jsonc`
2. 如果 **是**（现有项目场景）：
   - 转移到 base44-sdk 技能进行实现
   - 此技能仅处理 CLI 命令（登录、部署、实体推送）
   - **除本地运行应用程序外**——仍然在此处。在开始开发服务器之前，请阅读 [Running Local Development](#running-local-development)：一种运行方式会命中生产数据。
3. 如果 **否**，则决定在两个初始化路径之间进行选择：
   - **已配置的应用**——Base44 应用已经存在，因为它是通过 Stripe Projects / projects.dev 流程刚刚配置的，或者 `BASE44_APP_ID`（或 `BASE44_PROJECTS_BASE44_APP_ID`）存在于环境变量或 `.env`/`.env.local` 文件中：
     - 运行 `npx base44 scaffold` 以为此 **现有** 应用设置本地文件
     - **不要运行 `npx base44 create`**——那会创建一个第二个、重复的应用。参见 [scaffold.md](references/scaffold.md)。
   - **新项目**——尚不存在任何应用，也没有任何应用被配置：
     - 此技能（base44-cli）将处理请求；引导用户通过 `npx base44 create`
     - 不要激活 base44-sdk

## 关键：仅本地安装

**绝对不要直接调用 `base44`。** CLI 作为开发依赖项本地安装，必须通过包管理器访问：

- `npx base44 <command>` (npm - 推荐)
- `yarn base44 <command>` (yarn)
- `pnpm base44 <command>` (pnpm)

**错误：`base44 login`**
**正确：`npx base44 login`**

## 强制：会话开始时的身份验证检查

**关键**：每当此技能被激活时，在 AI 会话的**最开始**，您**必须**：

1. **通过运行以下命令检查身份验证状态**：
   ```bash
   npx base44 whoami
   ```

2. **如果用户已登录**（命令成功并显示电子邮件）：
   - 继续执行请求的任务

3. **如果用户未登录**（命令失败或显示错误）：
   - **立即停止**
   - **不要**执行任何 CLI 操作
   - **要求用户手动登录**，通过运行：
     ```bash
     npx base44 login
   ```
   - 等待用户确认他们已登录后再继续

**此检查是强制的，并且必须在执行任何其他 Base44 CLI 命令之前执行。**

**通过 Stripe Projects / projects.dev 配置？** 当应用程序通过该流程配置时，CLI 从它注入的环境变量 `BASE44_ACCESS_TOKEN` / `BASE44_REFRESH_TOKEN` 中种子身份验证（`BASE44_PROJECTS_*` 前缀的名称会自动规范化）。在这种情况下，`npx base44 whoami` 已经成功，您**不需要**交互式 `npx base44 login`。

**工作区 API 密钥已设置？** 如果 `BASE44_API_KEY` 环境变量设置为工作区 API 密钥（前缀 `b44k_`），CLI 将使用它进行身份验证——`npx base44 whoami` 和其他命令无需交互式登录即可成功。

## 概述

Base44 CLI 提供用于身份验证、创建项目、管理实体和部署 Base44 应用程序的命令行工具。它是框架无关的，并且可以与流行的前端框架（如 Vite、Next.js、Create React App、Svelte、Vue 等）一起使用。

## 何时使用此技能与 base44-sdk

**使用 base44-cli 时：**
- 从零开始创建 **新的** Base44 项目
- 在空目录中初始化项目
- 为已配置的外部应用（例如，通过 Stripe Projects / projects.dev 流程）设置本地文件（**现有的**应用）→ 使用 `scaffold`
- 目录中缺少 `base44/config.jsonc`
- 用户提及："创建一个新项目"、"初始化项目"、"设置一个项目"、"开始一个新的 Base44 应用"
- 通过 CLI 部署、推送实体或进行身份验证
- 使用 CLI 命令 (`npx base44 ...`)

**使用 base44-sdk 时：**
- 在**现有的** Base44 项目中构建功能
- `base44/config.jsonc` 已经存在
- 使用 JavaScript/TypeScript 代码使用 Base44 SDK
- 实现功能、组件或功能
- 用户提及："实现"、"构建一个功能"、"添加功能"、"编写代码"

**技能依赖项：**
- `base44-cli` 是新项目中 `base44-sdk` 的**先决条件**
- 如果用户想要"创建一个应用"且不存在 Base44 项目，则首先使用 `base44-cli`
- `base44-sdk` 假设 Base44 项目已经初始化

**状态检查逻辑：**
在选择技能之前，检查：
- 如果 (用户提及 "创建/构建应用" 或 "创建一个项目")：
  - 如果 (`base44/config.jsonc` 存在)：
    → 使用 **base44-sdk**（项目存在，构建功能）
  - 否则如果 (应用通过外部配置——`BASE44_APP_ID`/`BASE44_PROJECTS_BASE44_APP_ID` 设置，或者 Stripe Projects / projects.dev 流程刚刚运行)：
    → 使用 **base44-cli** → `npx base44 scaffold`（为此**现有**应用设置本地文件；不要 `create`）
  - 否则：
    → 使用 **base44-cli** → `npx base44 create`（需要初始化新项目）

## 项目结构

Base44 项目结合了标准前端项目和 `base44/` 配置文件夹：

```
my-app/
├── base44/                      # Base44 配置 (由 CLI 创建)
│   ├── config.jsonc             # 项目设置、站点配置
│   ├── .types/                  # 自动生成的 TypeScript 类型 (由 `types generate` 创建)
│   │   └── types.d.ts           # 为 @base44/sdk 增强的模块
│   ├── entities/                # 实体模式定义
│   │   ├── task.jsonc
│   │   └── board.jsonc
│   ├── functions/               # 后端函数 (可选)
│   │   └── my-function/
│   │       └── entry.ts
│   ├── actors/                  # 实时演员 (可选)
│   │   └── ChatRoom/
│   │       └── entry.ts
│   ├── agents/                  # 演员配置 (可选)
│   │   └── support_agent.jsonc
│   ├── agent-skills/            # 演员技能指令 (可选)
│   │   └── pdf-export.md
│   └── connectors/              # OAuth 连接器配置 (可选)
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
- `base44/entities/*.jsonc` - 数据模型模式 (参见实体模式部分)
- `base44/functions/*/entry.ts` - 后端函数入口点
- `base44/actors/*/entry.ts` - 实时演员入口点 (可选)
- `base44/agents/*.jsonc` - 演员配置 (可选)
- `base44/agent-skills/*.md` - 演员技能指令 (可选)
- `base44/.types/types.d.ts` - 自动生成的 TypeScript 类型 (为实体、函数和演员创建) (由 `npx base44 types generate` 创建)
- `base44/connectors/*.jsonc` - OAuth 连接器配置 (可选)
- `src/api/base44Client.js` - 前端使用的预配置 SDK 客户端

**config.jsonc 示例：**
```jsonc
{
  "name": "My App",                    // 必须的：项目名称
  "description": "App description",    // 可选：项目描述
  "visibility": "public",              // 可选："public" | "private" | "workspace"
  "entitiesDir": "./entities",         // 可选：默认 "entities"
  "functionsDir": "./functions",       // 可选：默认 "functions"
  "actorsDir": "./actors",             // 可选：默认 "actors"
  "agentsDir": "./agents",             // 可选：默认 "agents"
  "agentSkillsDir": "./agent-skills",  // 可选：默认 "agent-skills"
  "connectorsDir": "./connectors",     // 可选：默认 "connectors"
  "site": {                            // 可选：站点部署配置
    "installCommand": "npm install",   // 可选：安装依赖项
    "buildCommand": "npm run build",   // 可选：构建命令
    "serveCommand": "npm run dev",     // 可选：本地开发服务器
    "outputDirectory": "./dist"        // 可选：构建输出目录
  }
}
```

**配置属性：**

| 属性 | 描述 | 默认 |
|----------|-------------|---------|
| `name` | 项目名称 (必须) | - |
| `description` | 项目描述 | - |
| `visibility` | 应用可见性: `public`, `private`, 或 `workspace` | - |
| `entitiesDir` | 实体模式目录 | `"entities"` |
| `functionsDir` | 后端函数目录 | `"functions"` |
| `actorsDir` | 实时演员目录 | `"actors"` |
| `agentsDir` | 演员配置目录 | `"agents"` |
| `agentSkillsDir` | 演员技能指令目录 | `"agent-skills"` |
| `connectorsDir` | OAuth 连接器配置目录 | `"connectors"` |
| `site.installCommand` | 安装依赖项的命令 | - |
| `site.buildCommand` | 构建项目的命令 | - |
| `site.serveCommand` | 运行开发服务器的命令 | - |
| `site.outputDirectory` | 部署的构建输出目录 | - |

## 安装

将 Base44 CLI 作为开发依赖项安装到您的项目中：

```bash
npm install --save-dev base44
```

**重要**：永远不要假设或硬编码 `base44` 包版本。始终不带版本说明符进行安装以获取最新版本。

然后使用 `npx` 运行命令：

```bash
npx base44 <command>
```

**注意**：此文档中的所有命令都使用 `npx base44`。您也可以使用 `yarn base44`，或者如果需要，可以使用 `pnpm base44`。
