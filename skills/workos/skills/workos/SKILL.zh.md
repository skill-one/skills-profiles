---
name: workos
description: 当用户请求 WorkOS 文档 URL、术语或仪表板字段（登录端点、`initiate_login_uri`、重定向 URI、`WORKOS_*` 环境变量）、实施、调试或迁移 WorkOS — AuthKit、SSO/SAML、目录同步、RBAC、FGA、MFA、Vault、审计日志、管理员门户、管道（连接应用）、功能标志、Radar（机器人/欺诈检测）、Webhooks、自定义域名、在代理或沙盒会话中运行 `workos` CLI（`WORKOS_MODE`、`workos doctor`）或从 Auth0、Clerk、Cognito、Firebase、Supabase、Stytch、Descope 或 Better Auth 迁移时使用。此外，在 @workos-inc/* 导入时也会触发。
---

# WorkOS 技能路由器

## 如何使用

**此文件是一个路由器，而不是答案。** 在回复用户之前：

1. 使用规则 0 和下面的决策树，将请求匹配到参考文件。
2. **在生成任何答案、URL 或代码之前，你必须使用 Read 工具阅读匹配的参考文件。** 如果你还没有阅读参考文件，你就没有遵循这个技能。
3. 按照参考文件内的说明（它会告诉你使用 WebFetch 获取哪些实时文档以及要避免哪些陷阱）。

**例外**：小部件请求通过 Skill 工具使用 `workos-widgets` 技能——它有自己的多框架编排。

## 指导方针（适用于每个回复）

无论哪个路由规则触发，这些规则都适用。它们的存在是因为过去 WorkOS 代理交互中最常见的故障模式是看似合理的 CLI 命令和仪表板路径的虚构。

- **在处理工作区管理任务时，先检查 WorkOS MCP 服务器，再使用 CLI。** 如果会话连接了 WorkOS MCP 工具（一个暴露 `whoami`、`list_operations`、`query` 和 `mutate` 的服务器——工具名称可能带有客户端特定的前缀），请优先使用这些工具来读取和更改工作区资源：它们已经以登录的仪表板用户身份运行，无需安装 CLI 也无需 API 密钥。CLI 仍然是引导、播种、本地项目配置和诊断的正确界面。完整的决策指南是 `references/workos-management.md` 的“选择界面”部分。
- **在依赖 WorkOS MCP 连接之前，先恢复损坏的 WorkOS MCP 连接——但永远不要将 MCP 设置视为 CLI 工作的先决条件。** 当用户要求设置 WorkOS MCP 服务器，或期望的 MCP 工具缺失、未认证或启动中断时，先阅读 `references/workos-mcp.md`：确定 MCP 客户端和请求的配置范围，并且不要在明确意图的情况下修改用户全局代理配置。依赖于浏览器、凭证存储或主机证书的认证必须在用户的正常主机 shell 中完成。如果未配置 MCP 服务器且用户没有要求，不要将请求转移到 MCP 设置——`references/workos-management.md` 中的 CLI 路径完全支持它。
- **永远不要虚构 `workos` CLI 命令。** 使用 `WORKOS_MODE=agent workos --help --json` 验证命名命令。在声明操作不受支持之前，还要检查 `WORKOS_MODE=agent workos api ls --json` 以获取可通过 `workos api` 使用的 REST 端点。不要假设因为 `list`/`get`/`delete` 存在，`create` 子命令也存在，或者 GraphQL 操作是 REST 端点。参见 `references/workos-management.md`。
- **每个 AuthKit 集成都必须配置和验证应用程序 URL。** 对于设置和迁移，请与框架或语言参考一起阅读 `references/workos-authkit-setup.md`。它涵盖了回调、Sign-out URI 和 Initiate login URI。通过构建并不证明这些设置或流程有效。
- **在从 coding-agent 会话中调用 `workos` CLI 时，优先使用 `WORKOS_MODE=agent`。** CLI 自动检测大多数代理环境（`CLAUDECODE`、`CLAUDE_CODE`、`CURSOR_AGENT`、`CODEX_SANDBOX`、非 TTY），但显式的环境变量在沙盒配置中更可靠。见下文“WorkOS CLI 在 Coding-Agent 会话中”部分。
- **永远不要虚构仪表板点击路径。** 像“仪表板 > 组织 > X > 角色 > 映射组”或 `dashboard.workos.com/some/specific/path` 这样的短语，除非你已将其与刚获取的文档页面验证过，否则不应出现。仪表板 UI 会重新组织；文档页面是稳定的。引用文档 URL 并概念性地描述目的地（“授权页面”、“目录的设置”），而不是承诺点击路径。
- **当用户想要做 CLI 不支持的事情时，直截了当地说明。** 用户比虚构的命令失败要好，“这不是 CLI 的一部分；这是如何操作的文档 URL”比虚构的命令要好。参见 `references/workos-management.md` 的“不在 CLI 中”部分。
- **在编写配方时，优先使用文档 URL 而不是散文。** 如果参考文件告诉你引用特定的文档 URL，请直接引用它；不要释义 URL 的 slug。

## Coding-Agent 会话中的 WorkOS CLI

CLI 解决两个独立轴：**交互模式**（`human`/`agent`/`ci`）和**输出模式**（`human`/`json`）。CLI 通过已知环境变量（`CLAUDECODE`、`CLAUDE_CODE`、`CURSOR_AGENT`、`CODEX_SANDBOX`、`CURSOR_TRACE_ID`）和非 TTY 检测自动检测代理环境，但显式设置在沙盒配置中更可靠。

**任何设置或调试任务的推荐预检：**

```bash
WORKOS_MODE=agent workos doctor --json --skip-ai
```

`--skip-ai` 禁用医生的 AI 诊断传递，这需要 API 密钥和网络往返——在沙盒中两者都不保证。如果 `--skip-ai` 作为未知标志出错，CLI 已过时——见 `references/workos-cli-upgrade.md`。结构化的 JSON 输出足以进行程序化排查。

这返回一个包含 `interactionMode`（`{ mode, source }`）和 `hostExecution`（`{ ok, failures[] }`）字段的结构化 JSON 报告。在建议修复之前，先阅读 JSON。

**规则：**

- 使用 `--json` 解析命令输出。它仅控制**格式**——它不会改变 CLI 行为。
- 即使传递人类可读消息时，也使用 `WORKOS_MODE=agent`。它控制**提示、浏览器启动和主机信任**。
- 将医生 `HOST_EXECUTION_UNTRUSTED` 问题视为硬信任边界。如果医生报告包含此问题（或 `hostExecution.ok` 为 `false`），**当前 shell 可能是沙盒**。从此 shell 发出的认证、配置、密钥链和 API 失败不是权威的。在得出结论之前，要求用户在其主机 shell 上重新运行主机敏感命令（`workos auth login`、`workos doctor`、`workos env add`）。
- 不要假设基于浏览器的认证（`workos auth login`）在沙盒中有效。如果需要认证，显示 CLI 打印的手动 URL/代码回退，或要求用户在其主机 shell 上运行 `workos auth login`。
- 对于具有破坏性或权限更改的 CLI 命令，在传递确认标志之前获得用户的批准。代理模式从不提示，因此省略所需的标志会导致 `confirmation_required` 错误。已知标志：`--yes` 用于 `workos api` 请求的修改、角色/权限写入和成员资格角色更新；`--force` 用于 `workos connection delete`、`workos directory delete` 和 `workos debug reset`。检查 `workos --help --json` 获取已安装命令的标志。确认标志不是进行未请求更改的权限。
- 结构化的 CLI 错误（stderr 上的 JSON）包括一个可选的 `error.recovery.hints` 数组，其中每个提示都有 `description`、可选的 `command` 和可选的 `hostShellRequired`。优先使用这些提示而不是猜测下一步。

**可能遇到的遗留兼容性：**

- `WORKOS_NO_PROMPT=1` 是一个遗留别名，它设置代理交互行为和 JSON 输出。要迁移，请设置 `WORKOS_MODE=agent` 并将 `--json` 传递给命令以保留两种行为。单独使用 `WORKOS_MODE=agent` 会丢弃隐式的 JSON 格式化。
- `WORKOS_FORCE_TTY=1` 仅影响输出格式；它不会改变交互模式。

## 主题 → 参考映射

> 术语查找——“X 是什么”、“X 的文档 URL”——由**规则 0** 处理，而不是此主题映射。它们路由到 `references/workos-terms.md`。

### AuthKit 安装（阅读 `references/{name}.md`）

| 用户想要...                    | 阅读文件                                     |
| ----------------------------------- | --------------------------------------------- |
| 在 Next.js 中安装 AuthKit          | `references/workos-authkit-nextjs.md`         |
| 在 React SPA 中安装 AuthKit        | `references/workos-authkit-react.md`          |
| 在 React Router 中安装 AuthKit   | `references/workos-authkit-react-router.md`   |
| 在 TanStack Start 中安装 AuthKit | `references/workos-authkit-tanstack-start.md` |
| 在 SvelteKit 中安装 AuthKit      | `references/workos-authkit-sveltekit.md`      |
| 在原生 JS 中安装 AuthKit       | `references/workos-authkit-vanilla-js.md`     |
| AuthKit 架构参考              | `references/workos-authkit-base.md`           |
| 配置 AuthKit 应用程序 URL  | `references/workos-authkit-setup.md`          |
| 添加 WorkOS 小部件                  | 通过 Skill 工具加载 `workos-widgets` 技能    |

### 后端 SDK 安装（阅读 `references/{name}.md`）

| 用户想要...                   | 阅读文件                          |
| ---------------------------------- | ---------------------------------- |
| 在 Node.js 后端安装 AuthKit | `references/workos-node.md`        |
| 在 Python 中安装 AuthKit          | `references/workos-python.md`      |
| 在 .NET 中安装 AuthKit            | `references/workos-dotnet.md`      |
| 在 Go 中安装 AuthKit              | `references/workos-go.md`          |
| 在 Ruby 中安装 AuthKit            | `references/workos-ruby.md`        |
| 在 PHP 中安装 AuthKit             | `references/workos-php.md`         |
| 在 PHP Laravel 中安装 AuthKit     | `references/workos-php-laravel.md` |
| 在 Kotlin 中安装 AuthKit          | `references/workos-kotlin.md`      |
| 在 Elixir 中安装 AuthKit          | `references/workos-elixir.md`      |

### 功能（阅读 `references/{name}.md`）

| 用户想要...                   | 阅读文件                             |
| ---------------------------------- | ------------------------------------- |
| 配置单点登录           | `references/workos-sso.md`            |
| 设置目录同步              | `references/workos-directory-sync.md` |
| 实现RBAC / 角色             | `references/workos-rbac.md`           |
| 使用 Vault 加密数据            | `references/workos-vault.md`          |
| 处理 WorkOS 事件 / webhooks    | `references/workos-events.md`         |
| 设置审计日志                  | `references/workos-audit-logs.md`     |
| 启用管理员门户                | `references/workos-admin-portal.md`   |
| 添加多因素认证              | `references/workos-mfa.md`            |
| 配置电子邮件交付           | `references/workos-email.md`          |
| 设置自定义域名              | `references/workos-custom-domains.md` |
| 设置 IdP 集成             | `references/workos-integrations.md`   |
| 实现FGA / 细粒度授权z | `references/workos-fga.md`            |
| 设置 Pipes / 连接应用      | `references/workos-pipes.md`          |
| 配置功能标志            | `references/workos-feature-flags.md`  |
| 设置 Radar / 欺诈检测     | `references/workos-radar.md`          |

### API 参考（阅读 `references/{name}.md`）

上面的功能主题文件包含它们各自 API 的端点表。当没有功能主题时，使用这些 API 仅参考：

| 用户想要...           | 阅读文件                               |
| -------------------------- | --------------------------------------- |
| AuthKit API 参考      | `references/workos-api-authkit.md`      |
| 组织 API 参考            | `references/workos-api-organization.md` |

### 迁移（阅读 `references/{name}.md`）

| 用户想要...                    | 阅读文件                                             |
| ----------------------------------- | ----------------------------------------------------- |
| 从 Auth0 迁移                  | `references/workos-migrate-auth0.md`                  |
| 从 AWS Cognito 迁移            | `references/workos-migrate-aws-cognito.md`            |
| 从 Better Auth 迁移            | `references/workos-migrate-better-auth.md`            |
| 从 Clerk 迁移                  | `references/workos-migrate-clerk.md`                  |
| 从 Descope 迁移                | `references/workos-migrate-descope.md`                |
| 从 Firebase 迁移               | `references/workos-migrate-firebase.md`               |
| 从 Stytch 迁移                 | `references/workos-migrate-stytch.md`                 |
| 从 Supabase Auth 迁移          | `references/workos-migrate-supabase-auth.md`          |
| 从独立的 SSO API 迁移         | `references/workos-migrate-the-standalone-sso-api.md` |
| 从其他服务迁移                 | `references/workos-migrate-other-services.md`         |

### 管理 & CLI 生命周期（阅读 `references/{name}.md`）

| 用户想要...                            | 阅读文件                          |
| ------------------------------------------- | ---------------------------------- |
| 设置或恢复 WorkOS MCP 服务器     | `references/workos-mcp.md`         |
| 管理 WorkOS 资源（MCP 服务器或 CLI） | `references/workos-management.md`  |
| 将 `workos` CLI 升级到新版本 | `references/workos-cli-upgrade.md` |

## 路由决策树

按顺序应用这些规则。第一个匹配的规则获胜。

### 0. 术语 / 文档 URL 查找

**触发器**：查找形状的短语——“X 是什么”、“X 的含义是什么”、“X 的文档 URL”、“X 的文档在哪里”、“X 的规范链接”、“在哪里在仪表板中配置 X”——其中 X 是 WorkOS 特定的配置字段、端点、环境变量或术语。示例：`initiate_login_uri`、”登录端点“、”重定向 URI“、仪表板字段名称、`WORKOS_*` 环境变量。

**不要触发 Rule 0** 用于设置形状的短语，如“设置 Vault”、“启用管理员门户”、“配置 MFA”——这些路由到 Rule 3（功能特定）。

**操作**：

1. 阅读 `references/workos-terms.md`——一个映射 WorkOS 术语到规范文档 URL 的经过策划的表格。
2. 如果术语在表格中，使用摘要来回答；只有当用户想要更多细节时，才 WebFetch 列出的 URL。
3. 如果术语不在表格中，遵循该文件底部的“仍然找不到？”回退。当你找到规范 URL 时，回答用户并建议他们打开一个 PR 来添加一行。

**对于术语查找**，不要 WebFetch `llms.txt` 或在阅读术语文件之前猜测 `workos.com/docs/...` URL。（规则 8 和 9 使用 `llms.txt` 用于不同的目的——此禁令仅限于 Rule 0。）。

**为什么这个会赢**：术语查找独立于功能/框架/迁移上下文。它们需要短路路由，而不是“模糊或通用”（Rule 8）。

---

### 1. 迁移上下文

**触发器**：用户提到从另一个提供程序（Auth0、Clerk、Cognito、Firebase、Supabase、Stytch、Descope、Better Auth、独立的 SSO API）迁移。

**操作**：读取 `references/workos-migrate-[provider].md`，其中 `[provider]` 匹配源系统。如果提供程序不在表格中，读取 `references/workos-migrate-other-services.md`。

**为什么这个会赢**：迁移上下文覆盖功能特定路由，因为用户需要提供程序特定的数据导出和转换步骤。

---

### 2. API 参考请求

**触发器**：用户明确询问“API 端点”、“请求格式”、“响应模式”、“API 参考”，或提到检查 HTTP 详细信息。

**操作**：对于具有主题文件（SSO、目录同步、RBAC、Vault、事件、审计日志、管理员门户）的功能，读取功能主题文件——它包含端点表。对于 AuthKit 或组织 API，读取 `references/workos-api-[domain].md`。

**为什么这个会赢**：API 参考是低级别的；功能主题是高级别的，但包含端点表供快速参考。

---

### 3. 功能特定请求

**触发器**：用户按名称提到特定的 WorkOS 功能（SSO、MFA、目录同步、审计日志、Vault、RBAC、FGA、管理员门户、自定义域名、事件、集成、电子邮件、Pipes、功能标志、Radar）。

**操作**：阅读 `references/workos-[feature].md`，其中 `[feature]` 是小写的 slug（sso、mfa、directory-sync、audit-logs、vault、rbac、fga、admin-portal、custom-domains、events、integrations、email、pipes、feature-flags、radar）。

**例外**：小部件请求通过技能工具加载 `workos-widgets` 技能——它有自己的编排。

**消除歧义**：如果用户同时提到一个功能和使用“API”，则路由到功能主题文件（它包含端点）。如果他们提到多个功能，则首先路由到最具体的那个（例如，“SSO with MFA”→ 路由到 SSO；用户可以单独请求 MFA）。如果用户提到“FGA”或“细粒度授权”，则路由到 `workos-fga`——不是 `workos-rbac`。RBAC 是组织级别的角色；FGA 是基于 RBAC 的资源范围角色。

**特殊情况——IdP 组→角色映射**：如果用户询问将 Entra / Azure AD / Okta / Google Workspace / SCIM / 目录 / SSO 组映射到 WorkOS 角色（无论具体措辞如何），则读取 `workos-rbac.md` 和源特定参考：

- 目录同步 / SCIM / Google Workspace 组 → 还要读取 `workos-directory-sync.md`
- 仅 SSO 组 → 还要读取 `workos-sso.md`

这两个文件现在都有标准的配方。不要凭记忆或改述仪表板菜单路径——文档没有承诺确切的点击路径，你也不应该这样做。这种映射**不是** WorkOS CLI 操作；如果要求 CLI 命令，请说明它不在 CLI 中，并链接到文档。

---

### 4. AuthKit 安装

**触发条件**：用户提到身份验证设置、登录流程、注册、会话管理，或明确提到“AuthKit”而没有提到特定功能（如 SSO 或 MFA）。

**操作**：使用以下优先级顺序检查来检测框架和语言。读取相应的参考文件和 `references/workos-authkit-setup.md`。在报告集成完成之前，完成其应用设置和流程检查。

**消除歧义**：

- 如果用户说“通过 AuthKit 进行 SSO 登录”，则路由到 `workos-sso` (#3)——功能优先于框架。
- 如果用户说“使用 Google 进行 React 登录”，则路由到 AuthKit React (#4)——这是 AuthKit 级别的身份验证，不是 SSO API。
- 如果用户已经使用 AuthKit 并想添加一个功能（例如，“将 MFA 添加到我的 AuthKit 应用程序中”），则路由到功能参考 (#3)，而不是回到 AuthKit 安装。

#### 框架检测优先级（仅限 AuthKit）

按此确切顺序检查。第一个匹配项获胜：

```
1. `@tanstack/start` 在 package.json 依赖项中
   → 阅读：references/workos-authkit-tanstack-start.md

2. `@sveltejs/kit` 在 package.json 依赖项中
   → 阅读：references/workos-authkit-sveltekit.md

3. `react-router` 或 `react-router-dom` 在 package.json 依赖项中
   → 阅读：references/workos-authkit-react-router.md

4. `next.config.js` 或 `next.config.mjs` 或 `next.config.ts` 存在于项目根目录
   → 阅读：references/workos-authkit-nextjs.md

5. (`vite.config.js` 或 `vite.config.ts` 存在) AND `react` 在 package.json 依赖项中
   → 阅读：references/workos-authkit-react.md

6. 未检测到以上任何一项
   → 阅读：references/workos-authkit-vanilla-js.md
```

#### 语言检测（后端 SDK）

如果项目不是 JavaScript/TypeScript 前端框架，请检查：

```
1. `pyproject.toml` 或 `requirements.txt` 或 `setup.py` 存在
   → 阅读：references/workos-python.md

2. `go.mod` 存在
   → 阅读：references/workos-go.md

3. `Gemfile` 存在 或 `config/routes.rb` 存在
   → 阅读：references/workos-ruby.md

4. `composer.json` 存在 AND `laravel/framework` 在依赖项中
   → 阅读：references/workos-php-laravel.md

5. `composer.json` 存在（没有 Laravel）
   → 阅读：references/workos-php.md

6. `*.csproj` 或 `*.sln` 存在
   → 阅读：references/workos-dotnet.md

7. `build.gradle.kts` 或 `build.gradle` 存在
   → 阅读：references/workos-kotlin.md

8. `mix.exs` 存在
   → 阅读：references/workos-elixir.md

9. `package.json` 存在，包含 `express` / `fastify` / `hono` / `koa`（后端 JS）
   → 阅读：references/workos-node.md
```

**为什么按此顺序**：TanStack、SvelteKit 和 React Router 比 Next.js/Vite+React 更具体。一个项目可以同时具有 Next.js 和 React Router；在这种情况下，React Router 赢得，因为它更具体。当未检测到框架时，Vanilla JS 是回退选项。当未检测到前端框架时，会检查后端语言。

**边缘情况——检测到多个框架**：如果您检测到冲突信号（例如，同时存在 `next.config.js` 和 `@tanstack/start`），则询问用户他们想使用哪个。不要猜测。

**边缘情况——从上下文中无法确定框架**：如果用户说“添加登录”，但您无法扫描文件（远程仓库，无访问权限），则询问：“您使用哪个框架/语言？”不要在没有确认的情况下默认。

---

### 5. 集成设置

**触发条件**：用户提到连接到外部 IdP、配置第三方集成，或询问“如何与 [提供者] 集成”。

**操作**：读取 `references/workos-integrations.md`。

**为什么与 SSO 分开**：SSO 涵盖身份验证流程；集成涵盖 IdP 配置和连接设置。如果用户同时提到两者（“设置 Google SSO”），则路由到 SSO (#3)——它将在需要时参考集成。

---

### 6. MCP 设置或恢复

**触发条件**：用户询问安装或配置 WorkOS MCP 服务器、选择配置范围，或报告 WorkOS MCP 工具缺失、未认证、不可用或启动中断。

**操作**：读取 `references/workos-mcp.md`。它通过标准的 WorkOS MCP 文档路由设置和恢复，保护配置范围和 OAuth 凭据，并识别必须在用户正常主机 shell 中运行的认证步骤。

**为什么优先**：MCP 设置发生在 MCP 工具可调用之前。它需要配置范围和主机信任检查，这些是普通工作区管理指南不涵盖的。

---

### 7. 管理操作（MCP 服务器或 CLI）

**触发条件**：用户提到管理 WorkOS 资源（组织、用户、角色、权限）、播种数据或 CLI 管理命令。

**操作**：读取 `references/workos-management.md`。它以表面选择指南开头：优先使用连接的 WorkOS MCP 工具进行工作区读写，并使用 CLI 进行引导、播种、本地配置、CI 和诊断。即使 MCP 工具存在，也要读取它——它映射哪些操作位于哪个表面。

**子情况——CLI 升级**：如果用户报告过时的 `workos` CLI（`workos --version` 显示旧版本，遵循最新文档后出现 `unknown command` 错误，或询问“如何更新 workos CLI？”），则读取 `references/workos-cli-upgrade.md`。不要猜测最新版本——该文件告诉您要指示用户运行 `npm view workos version`。

---

### 8. 模糊或一般请求

**触发条件**：用户说“帮助 WorkOS”、“WorkOS 设置”、“WorkOS 能做什么”，或提供无功能特定上下文。

**操作**：

1. WebFetch https://workos.com/docs/llms.txt
2. 扫描索引以找到与用户可能意图最匹配的部分
3. WebFetch 具体部分的 URL
4. 总结功能并询问用户他们想完成什么

**不要猜测功能**——通过显示选项强制消除歧义。

---

### 9. 无匹配 / 含糊不清

**触发条件**：以上规则均不匹配，或请求确实含糊不清。

**操作**：

1. WebFetch https://workos.com/docs/llms.txt
2. 搜索索引以查找用户请求中的关键词
3. 如果找到匹配项，WebFetch 该部分 URL 并继续
4. 如果没有匹配项，回复：“我找不到与 “[用户术语]” 匹配的 WorkOS 功能。您能澄清吗？例如：身份验证、SSO、MFA、目录同步、审计日志等。”

---

## 边缘情况

### 用户提到多个功能

首先路由到最具体的参考。示例：“SSO with MFA and directory sync”→ 首先路由到 `workos-sso`。完成 SSO 设置后，用户可以单独请求 MFA 和 Directory Sync。

### 用户提到功能 + API 参考

路由到功能主题文件——它包含端点表。示例：“SSO API 端点”→ `workos-sso.md`。

### 用户想向现有的 AuthKit 设置添加功能

路由到功能参考 (#3)，而不是回到 AuthKit 安装。示例：“我在 Next.js 中使用 AuthKit 并想添加 SSO”→ `workos-sso.md`。

### 用户提到提供者但没有功能

路由到集成 (#5)。示例：“如何连接 Okta？”→ `workos-integrations.md`。

### 用户提到提供者 AND 功能

路由到功能参考 (#3)。示例：“设置 Okta SSO”→ `workos-sso.md`（它将参考 Okta 设置）。

### 未知 AuthKit 框架

如果您无法检测框架且用户没有指定，则询问：“您使用哪个框架/语言？”不要在没有确认的情况下默认。

### 框架冲突（检测到多个框架）

如果检测发现冲突信号（例如，同时存在 Next.js 和 TanStack Start 配置），则询问：“我看到 `[框架 A]` 和 `[框架 B]`。您想为 AuthKit 使用哪个？”

### 用户完全未提供上下文

遵循步骤 #8（模糊或一般请求）：获取 llms.txt，显示选项，并强制消除歧义。
