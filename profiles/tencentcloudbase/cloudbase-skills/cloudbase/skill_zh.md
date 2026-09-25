# 云开发开发指南

## 📁 参考文件位置

所有参考文档文件都位于与此文件相对的 `references/` 目录中。

**文件结构：**
```
cloudbase/
├── SKILL.md              # 此文件（主入口）
└── references/           # 所有参考文档
    ├── auth-web-cloudbase/SKILL.md              # Web 认证指南
    ├── auth-wechat-miniprogram/SKILL.md         # 微信认证指南
    ├── cloudbase-document-database-web-sdk/SKILL.md # Web 的 NoSQL 数据库
    ├── ui-design/        # UI 设计指南
    └── ...               # 其他参考文档
```

**如何使用：** 当此文档提到读取参考文件，如 `references/auth-web-cloudbase/SKILL.md` 时，只需从 `references/` 子目录中读取该文件。

---


## 第 0 步 — 确认站点（国内 vs 国际）

云开发有两个**独立的账号系统**：国内站（`cloud.tencent.com`）和国际站（`tencentcloud.com`）。环境、控制台、API 密钥和登录状态**不会**相互交叉。错误的站点登录通常看起来像“已登录，但看不到环境”而不是明确的错误——因此，在安装 MCP、登录或绑定环境**之前**要确定站点。

在可能的情况下进行推断（控制台域名、envId、现有错误）；否则**询问用户一次**。不要猜测。

| | 国内站 domestic | 国际站 international |
|---|---|---|
| 远程 MCP（推荐） | `https://tcb-api.cloud.tencent.com/mcp/v1` | `https://tcb-api.tencentcloud.com/mcp/v1` |
| 本地 stdio MCP | 默认 — 无需设置 | `TCB_SITE=intl` + `TCB_REGION=ap-singapore` |
| `tcb` 命令行工具 | 默认 | `TCB_IS_INTL=true`（或 `tcb config set isIntl true`） |
| 项目记录 `.cloudbase/project.json` | 省略 `site`，或 `"domestic"` | `"site": "intl"`, `"region": "ap-singapore"` |
| 控制台 | `tcb.cloud.tencent.com` | `tcb.tencentcloud.com` |
| 默认区域 | `ap-shanghai` | `ap-singapore` |
| NoSQL / 文档数据库工具 | 可用 | **不可用** |

- **国际用户：直接连接国际远程 MCP 端点** — `https://tcb-api.tencentcloud.com/mcp/v1`。这是一个一流的托管端点；OAuth 覆盖登录。站点由主机决定，因此没有 `site` 查询参数需要传递。
- 国内远程 MCP 形式相同，`https://tcb-api.cloud.tencent.com/mcp/v1` — 国内用户保持默认。
- `TCB_IS_INTL`（命令行工具）和 `TCB_SITE`（MCP）是**不同工具的不同变量名**。设置与当前使用的工具匹配的那个；设置错误的变量会静默无效果。
- 在首次运行时，**确定站点一次并持久化** — 命令行工具是机器全局的，MCP 切换是每个客户端的，只有 `.cloudbase/project.json` 在重启后对 MCP 可读。遵循 `references/site-onboarding.md`；不要在后续会话中重新询问。

详细信息和复制粘贴配置：`references/mcp-setup.md`。命令行工具细节：`references/tooling-fallback.md`。首次运行编排（触发/跳过、冲突仲裁、MCP-down 回退）：`references/site-onboarding.md`。

## 工作流

```
1. 探索  →  在编写任何代码之前，完整阅读匹配的技能。
                   使用 searchKnowledgeBase(mode="skill") 进行搜索，然后读取完整的 SKILL.md。
2. 实现
   ├── 2a. 资源准备 → 优先使用 MCP；如果此会话中缺少 MCP 工具，
   │     配置 MCP 用于下一个会话，现在使用 `tcb` 命令行工具（见 tooling-fallback.md）
   └── 2b. 前端实现 → 编写代码，安装依赖，启动服务器，测试
3. 结束  →  运行 cloudbase-code-review，修复错误，声明完成
                   （在验证部署后：可选提供一次 Deployment Share — 见 references/deployment-workflow.md §5）
```

**关键约束：** 第 2a 步必须先于前端代码。第 3 步是强制性的。

## 激活契约

路由使用稳定的技能 ID（`auth-tool-cloudbase`、`auth-web-cloudbase`、`http-api-cloudbase`、…）跨源、生成物和安装。

### 独立技能回退

如果只暴露一个已发布的技能：

- 当工作区中存在这些文件时，优先使用本地相对路径（`references/<skill-id>/SKILL.md` 或兄弟技能目录）。
- **不要**将兄弟技能的 Markdown 从远程原始 URL 获取到代理上下文中。
- 如果本地缺少必需的兄弟技能，请要求用户安装完整的云开发技能包或 IDE 插件（`npx skills add tencentcloudbase/cloudbase-skills`），然后仅使用本地文件继续。

从当前技能跟随相对的 `references/...` 路径。如果本次会话中无法使用 MCP，请遵循 `references/tooling-fallback.md`：通过 `references/mcp-setup.md` 为下一个会话配置 MCP，并通过 `references/cloudbase-cli/SKILL.md` 技能（读取 `core.md` + 匹配的域参考 — **不是** `tcb deploy`）来完成登录/管理。如果缺少 `npm`/`npx`，请遵循 `tooling-fallback.md` 中的“缺少 npm/npx”部分。

### 行动前的全局规则

- 确定场景后，在编写代码或调用云开发 API 之前，阅读匹配的技能。
- 优先使用语义源进行工具包维护；在运行时路由中表达稳定的技能 ID。
- 当**本次会话**中可用时，优先使用 MCP 或 mcporter 进行管理任务；在执行前检查工具模式。如果它们尚未可用，不要停滞 — 使用 `references/tooling-fallback.md` 中的 CLI 回退。
- UI 任务：首先阅读 `ui-design` 并在界面代码之前输出设计规范。
- 认证任务：首先阅读 `auth-tool-cloudbase` 并在实现前端之前启用提供者。
- 保持认证域分离：管理登录使用 `auth`（或 `tcb login` 当 MCP 认证不可用时）；应用端认证使用 `queryAppAuth` / `manageAppAuth`。

### 通用护栏

- 在同一路径上尝试 2-3 次失败后，停止并重新路由（平台技能、运行时、认证域、权限模型、SDK 边界）。
- 始终明确指定 `EnvId`；不要依赖 CLI 选择或隐式环境状态。
- 当环境标识符是别名、昵称或其他简短形式时，**不要直接**将其传递给 `auth.set_env`、SDK 初始化、控制台 URL 或生成配置。首先使用 `queryEnv(action=list, alias=..., aliasExact=true)` 将其解析为规范的全 `EnvId`。如果多个环境匹配或不存在精确别名，请停止并澄清用户。
- 在将 MCP/工具结果写入文件时，传递序列化文本（`JSON.stringify(result, null, 2)`），而不是原始对象。如果写入工具说 `content` 期望字符串但收到对象，不要重试相同的原始对象。首先序列化对象，然后使用序列化文本重试一次，并确保重试调用实际传递了序列化字符串而不是原始对象。
- 将场景特定的陷阱保留在子技能中 — 不要扩展此入口文件。
- **首次前端部署必须使用 `manageApps(action="deployApp", ...)`。** 没有 `createApp` / `updateApp` 动作 — 首次部署和重新部署都使用 `deployApp`，重新部署重用相同的 `serviceName`。`manageHosting` 仅用于通过 hosting 部署的项目增量更新。

### 工程宪法（适用于每个场景）

这些规则优先于便利性。完整理由存在于 `web-development`。

- **在编写前端代码之前准备后端资源。** 优先使用 MCP 进行认证提供者、表格、存储域和安全规则；如果本次会话中缺少 MCP 工具，在为下一个会话配置 MCP 后（`references/tooling-fallback.md`）使用 `tcb` 命令行工具。
- **不要使用 `any` 来绕过类型错误。** 优先使用 `unknown` + 类型守卫 / 精确接口。
- **在声明完成之前进行自我验证。** 静态（`tsc` / linter / 构建测试）和运行时（`agent-browser` 用于用户可见流程）。如果某层无法运行，请明确命名间隙。
- **不要掩盖失败。** 没有空 `try/catch`，不要删除失败的测试以变绿。
- `ai.createModel(...)` / `wx.cloud.extend.AI.createModel(provider)` 接受一个 **GroupName**，而不是供应商/模型 ID。合法的：`"cloudbase"`、`"hunyuan-exp"` 或 `"custom-<name>"`。模型 ID 放在 `generateText` / `streamText` `model` 字段中。见 `ai-model-web` / `ai-model-nodejs` / `ai-model-wechat`。
- **低能力 STOP 卡：** 对于 PostgreSQL / CloudBase PG / `app.rdb()` / `queryPgDatabase` / `managePgDatabase`，路由到 `postgresql-development-cloudbase` — **不要**使用 NoSQL/`manageMysqlDatabase` 用于该路径。对于 Web 认证守卫，使用 `auth.getSession()` 并要求 `data.session`；**不要**使用已弃用的 `getLoginState()` / `auth.getUser()` 作为登录证明。

### 高优先级路由

<!-- DO NOT EDIT: 自动生成自 references/activation-map.yaml -->

| 场景 | 首先读取 | 然后读取 | 不要路由到第一个 | 行动前必须检查 |
|----------|------------|-----------|------------------------|--------------------------|
| Web 登录 / 注册 / 认证 UI | `auth-tool-cloudbase` | `auth-web-cloudbase`, `web-development` | `cloud-functions`, `http-api-cloudbase` | 提供者状态和可发布密钥 |
| 微信小程序 + 云开发 | `miniprogram-development` | `auth-wechat-miniprogram`, `cloudbase-document-database-in-wechat-miniprogram` | `auth-web-cloudbase`, `web-development` | 项目是否真正使用云开发 / `wx.cloud` |
| 原生 App / Flutter / React Native | `http-api-cloudbase` | `auth-tool-cloudbase`, `relational-database-mcp-cloudbase` | `auth-web-cloudbase`, `cloudbase-document-database-web-sdk`, `web-development` | SDK 边界，OpenAPI，认证方法 |
| Web 项目 + NoSQL 数据库 | `web-development` | `cloudbase-document-database-web-sdk`, `auth-web-cloudbase` | `relational-database-mcp-cloudbase`, `http-api-cloudbase` | 登录状态和数据库访问权限模型 |
| 云开发 PostgreSQL 最佳实践 | `postgresql-best-practices-cloudbase` | `postgresql-development-cloudbase` | `cloudbase-document-database-web-sdk` | 访问路径，索引决策，行授权，启动容量 |
| 云开发 PostgreSQL / PG | `postgresql-development-cloudbase` | `auth-tool-cloudbase`, `auth-web-cloudbase`, `web-development`, `miniprogram-development`, `cloud-storage-web`, `http-api-cloudbase` | `relational-database-mcp-cloudbase`, `cloudbase-document-database-web-sdk` | PG 模式，用户名密码登录，后端/RLS 权限模型 |
| MySQL 数据库（关系型） | `relational-database-mcp-cloudbase` | `relational-database-web-cloudbase`, `http-api-cloudbase` | `cloudbase-document-database-web-sdk`, `web-development` | 区分 MCP 管理与应用代码访问 |
| 云函数 | `cloud-functions` | `auth-tool-cloudbase`, `ai-model-nodejs` | `cloudrun-development`, `auth-web-cloudbase` | 事件 vs HTTP 函数，运行时，`scf_bootstrap` |
| CloudRun 后端 | `cloudrun-development` | `auth-tool-cloudbase`, `relational-database-mcp-cloudbase` | `cloud-functions` | 容器边界，Dockerfile，CORS |
| AI Agent（智能体开发） | `cloudbase-agent` | `cloud-functions`, `cloudrun-development` | `cloud-functions`, `cloudrun-development` | AG-UI 协议，scf_bootstrap，SSE 流 |
| 最小 Web BaaS 示例（快速路径） | `minimal-web-baas-demo` | `web-development`, `cloudbase-document-database-web-sdk`, `postgresql-development-cloudbase` | `cloud-functions`, `cloudrun-development`, `spec-workflow`, `ui-design` | BaaS-优先 Web SDK CRUD，仅 MCP 模式，除非是 secrets/cron/规则无法表达，否则零云函数 |
| UI 生成 | `ui-design` | `web-development`, `miniprogram-development` | `cloud-functions` | 首先输出设计规范 |
| AI 模型（Web） | `web-development` | `ai-model-web`, `ui-design` | `ai-model-wechat`, `http-api-cloudbase` | 平台和流式交互模式 |
| AI 模型调用（大模型调用 / 文本生成 / 图片生成 / 流式对话） | `ai-model-web` | `ai-model-nodejs`, `ai-model-wechat` | `cloudbase-agent`, `cloud-functions`, `cloudrun-development` | 先运行“调用前必须的资格检查”：`DescribeActivityInfo`（小程序成长计划） + `DescribeEnvPostpayPackage`（Token Credits 资源包） |
| 资源健康检查 / 故障排除 | `ops-inspector` | `cloud-functions`, `cloudrun-development` | `ui-design`, `spec-workflow` | CLS 启用，日志时间范围 |
| Spec 工作流 / 架构设计 | `spec-workflow` | `cloudbase` | `web-development`, `cloud-functions` | 需求，设计，确认任务 |

#### 激活触发器（派生于 `references/activation-map.yaml`）

- **Web 登录 / 注册 / 认证 UI** — 云开发 Web 登录, Web 注册, auth login page, 可发布密钥, 短信登录, 邮箱登录
- **微信小程序 + 云开发** — 小程序 云开发, wx.cloud, mini program cloudbase, OPENID, 小程序数据库
- **原生 App / Flutter / React Native** — Android 云开发, iOS 云开发, Flutter 云开发, React Native 云开发, 原生 App 接入
- **Web 项目 + NoSQL 数据库** — Web 文档数据库, CloudBase collection, 前端查库, NoSQL Web SDK
- **云开发 PostgreSQL 最佳实践** — PG 访问模式，数据库访问路径，N+1 查询，批量查询，慢查询，EXPLAIN ANALYZE，缺索引，活动数据库容量
- **云开发 PostgreSQL / PG** — CloudBase PG, PostgreSQL, Postgres, PG 模式，JS SDK v3 PostgreSQL, app.rdb(), queryPgDatabase, managePgDatabase, mysqldb OpenAPI, PostgREST, RLS, service_role, auth schema, storage schema, pgvector
- **MySQL 数据库（关系型）** — MySQL 建表, executeWriteSQL, 安全规则, CloudBase 关系型数据库管理
- **云函数** — 创建云函数, HTTP 云函数, getFunctionLogs, scf_bootstrap, 运行时
- **CloudRun 后端** — CloudRun 部署, 云托管, container backend, Dockerfile
- **AI Agent（智能体开发）** — AI Agent, 智能体, 智能体开发, AG-UI 协议, LangGraph, LangChain, CrewAI, streaming agent, agent UI
- **最小 Web BaaS 示例（快速路径）** — 最小前后端, 最小可用 demo, 最小 fullstack, 搭一套 demo, 带云数据库的 demo, 带云函数+云数据库, 留言板, Todo 应用, todo app, Notes app, Kanban, Lovable, BaaS demo, minimal web baas, 快速 demo
- **UI 生成** — 设计页面, 登录页 UI, frontend interface, 组件样式, prototype
- **AI 模型（Web）** — Web AI 对话, CloudBase AI 流式输出, Web 集成模型
- **AI 模型调用（大模型调用 / 文本生成 / 图片生成 / 流式对话）** — 大模型调用, AI 模型调用, generateText, streamText, generateImage, 文本生成, 图片生成, 流式对话, hunyuan-exp, deepseek-v4-flash, Token Credits 资源包, 小程序成长计划, ai_miniprogram_inspire_plan, callCloudApi AI 模型, CreateAIModel
- **资源健康检查 / 故障排除** — 巡检, 诊断, health check, 资源健康, 异常日志, error inspection, troubleshooting, 错误排查
- **Spec 工作流 / 架构设计** — 需求文档, 技术方案, tasks.md, Spec 工作流


### 路由提醒

- Web 认证失败：通常是跳过了提供者配置，而不是缺少前端片段。
- 原生 App 失败：通常是 Web SDK 路径，而不是缺少 HTTP API 知识。
- 小程序失败：将 `wx.cloud` 像Web认证/SDK一样对待。
- 云开发 PG 失败：退回到 MySQL/NoSQL，跳过用户名密码就绪，或猜测原始 HTTP 而不是 `app.rdb()` / 文档 OpenAPI。
- AI 模型失败：通常是缺少 Token Credits / Growth Plan — 在更改代码之前运行 `DescribeEnvPostpayPackage` / `DescribeActivityInfo`。

## MCP + CLI 前置条件

当工具在当前会话中加载时，优先使用云开发 MCP 进行管理/部署。设置：`references/mcp-setup.md`。首次运行/不可用路径：`references/tooling-fallback.md`。

- **推荐安装：** `npx plugins add TencentCloudBase/cloudbase-plugin -y --scope user`。支持的 `--target` ID：`claude-code`, `cursor`, `codex`, `grok`, `kimi`, `github-copilot`, `vscode`。见 `references/mcp-setup.md`。
- 使用 `npx mcporter list | grep cloudbase` 或 IDE MCP 面板进行验证。如果缺少 `npm`/`npx`，请参见 `references/tooling-fallback.md`（安装 Node LTS 或使用 IDE 市场place MCP）。如果 MCP 缺失或配置后未可见，**仍然继续**：完成安装/配置，告诉用户重启下次解锁 MCP，现在通过 `cloudbase-cli` 域技能使用 `tcb` 命令行工具 — **不要**建议 `tcb deploy`。
- 优先使用 MCP `auth` 的设备码登录；否则 `tcb login`。不要硬编码密钥。

## 按需参考

仅在需要时加载（不要扩展此入口）：

- `references/tooling-fallback.md` — MCP vs `tcb` CLI 首次会话/缺失工具决策树
- `references/site-onboarding.md` — 首次运行站点引导：触发/跳过，持久化，冲突仲裁，MCP-down 回退
- `references/deployment-workflow.md` — 部署后端/前端，`manageApps` vs hosting，URL/文档更新，可选的部署后 Deployment Share 提供机会（§5）
- `references/console-links.md` — 创建资源后的控制台哈希路径
- `references/scenarios.md` — 用户需求 → 云开发能力映射
- `references/mcp-setup.md` — 插件安装（全局默认 + 目标），IDE MCP / mcporter 配置和认证示例
- `references/activation-map.yaml` — 规范路由契约源

## 参考索引

所有打包的参考文件（需要技能 lint 可达性）：

- [activation-map.yaml](references/activation-map.yaml)
- [console-links.md](references/console-links.md)
- [deployment-workflow.md](references/deployment-workflow.md)
- [mcp-setup.md](references/mcp-setup.md)
- [scenarios.md](references/scenarios.md)
- [site-onboarding.md](references/site-onboarding.md)
- [tooling-fallback.md](references/tooling-fallback.md)
