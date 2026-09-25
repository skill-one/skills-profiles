# WorkOS 技能路由器

## 使用方法

**此文件是一个路由器，不是答案。** 在回复用户之前：

1. 使用下面的决策树和规则 0 将请求匹配到参考文件。
2. **在生成任何答案、URL 或代码之前，你必须使用读取工具阅读匹配的参考文件。** 如果你还没有阅读参考文件，你就没有遵循这个技能。
3. 按照参考文件中的说明进行操作（它会告诉你使用 WebFetch 获取哪些实时文档以及要避免哪些陷阱）。

**例外**：小部件请求通过技能工具使用 `workos-widgets` 技能——它有自己的多框架编排。

## 指导方针（适用于每个回复）

这些规则无论哪个路由规则触发都适用。它们的存在是因为过去 WorkOS 代理交互的最常见故障模式是 plausible-shaped fabrication of CLI 命令和 Dashboard 路径。

- **在 workspace-management 任务中，在转向 CLI 之前检查 WorkOS MCP 服务器。** 如果会话连接了 WorkOS MCP 工具（一个暴露 `whoami`、`list_operations`、`query` 和 `mutate` 的服务器——工具名称可能带有客户端特定的前缀），请优先使用这些工具来读取和更改工作区资源：它们已经以登录的 Dashboard 用户身份运行，无需安装 CLI 也无需 API 密钥。CLI 仍然是 bootstrap、seeding、本地项目配置和诊断的正确界面。完整的决策指南是 `references/workos-management.md` 的“Choosing a surface”部分。
- **在依赖 WorkOS MCP 连接之前，先恢复损坏的 WorkOS MCP 连接——但永远不要将 MCP 设置视为 CLI 工作的先决条件。** 当用户要求设置 WorkOS MCP 服务器，或者期望的 MCP 工具缺失、未认证或在启动过程中中断时，请先阅读 `references/workos-mcp.md`：确定 MCP 客户端和请求的配置范围，并且不要在没有明确意图的情况下修改用户全局代理配置。依赖于浏览器、凭证存储或主机证书的认证必须在用户的正常主机 shell 中完成。如果未配置 MCP 服务器并且用户没有要求配置一个，不要将请求转移到 MCP 设置——`references/workos-management.md` 中的 CLI 路径完全支持它。
- **永远不要凭空发明 `workos` CLI 命令。** 使用 `WORKOS_MODE=agent workos --help --json` 验证命名命令。在声明操作不受支持之前，还要检查 `WORKOS_MODE=agent workos api ls --json` 以查找可通过 `workos api` 使用的 REST 端点。不要假设存在 `create` 子命令，因为 `list`/`get`/`delete` 存在，或者 GraphQL 操作是 REST 端点。参见 `references/workos-management.md`。
- **每个 AuthKit 集成都必须配置和验证应用程序 URL。** 对于设置和迁移，请与框架或语言参考一起阅读 `references/workos-authkit-setup.md`。它涵盖了回调、Sign-out URI 和 Initiate login URI。通过构建并不证明这些设置或流程有效。
- **在从 coding-agent 会话中调用 `workos` CLI 时，优先使用 `WORKOS_MODE=agent`。** CLI 自动检测大多数代理环境（`CLAUDECODE`、`CLAUDE_CODE`、`CURSOR_AGENT`、`CODEX_SANDBOX`、非 TTY），但显式的环境变量在沙盒配置中更可靠。见下文“WorkOS CLI in Coding-Agent Sessions”部分。
- **永远不要凭空发明 Dashboard 点击路径。** 像“Dashboard > Organizations > X > Roles > Map Groups”或 `dashboard.workos.com/some/specific/path` 这样的短语，除非你已将其与刚获取的文档页面进行验证，否则不应出现。Dashboard UI 会重新组织；文档页面是稳定的。引用文档 URL 并概念性地描述目的地（“授权页面”、“目录的设置”），而不是承诺点击路径。
- **当用户想要做 CLI 不支持的事情时，要明确地说出来。** 用户最好得到“这不是在 CLI 中；这是如何做它的文档 URL”而不是一个会失败的凭空编造的命令。参见 `references/workos-management.md` 的“Not in the CLI”部分。
- **在编写配方时，优先使用文档 URL 而不是散文。** 如果参考文件告诉你要引用一个特定的文档 URL，请直接引用它；不要释义 URL 的 slug。

## Coding-Agent 会话中的 WorkOS CLI

CLI 解决两个独立轴：**交互模式**（`human`/`agent`/`ci`）和**输出模式**（`human`/`json`）。CLI 通过已知的环境变量（`CLAUDECODE`、`CLAUDE_CODE`、`CURSOR_AGENT`、`CODEX_SANDBOX`、`CURSOR_TRACE_ID`）和非 TTY 检测来自动检测代理环境，但显式设置在沙盒配置中更可靠。

**任何设置或调试任务的推荐预检：**

```bash
WORKOS_MODE=agent workos doctor --json --skip-ai
```

`--skip-ai` 禁用医生的 AI 诊断传递，这需要 API 密钥和网络往返——在沙盒中两者都不保证。如果 `--skip-ai` 作为未知标志出错，则 CLI 已过时——参见 `references/workos-cli-upgrade.md`。结构化的 JSON 输出足以进行程序化排查。

这返回一个包含 `interactionMode`（`{ mode, source }`）和 `hostExecution`（`{ ok, failures[] }`）字段的结构化 JSON 报告。在建议修复之前阅读 JSON。

**规则：**

- 使用 `--json` 解析命令输出。它仅控制**格式化**——它不会改变 CLI 行为。
- 即使在传递人类可读消息时，也使用 `WORKOS_MODE=agent`。它控制**提示、浏览器启动和主机信任**。
- 将医生 `HOST_EXECUTION_UNTRUSTED` 问题视为一个硬信任边界。如果医生报告包含此问题（或 `hostExecution.ok` 为 `false`），**当前 shell 可能是沙盒**。从此 shell 发出的认证、配置、密钥链和 API 失败都不是权威的。请在得出结论之前，要求用户在其主机 shell 上重新运行主机敏感命令（`workos auth login`、`workos doctor`、`workos env add`）。
- 不要假设基于浏览器的认证（`workos auth login`）在沙盒中工作。如果需要认证，请显示 CLI 打印的手动 URL/代码回退，或者要求用户在其主机 shell 上运行 `workos auth login`。
- 对于破坏性或权限更改的 CLI 命令，在传递确认标志之前获得用户的批准。代理模式从不提示，因此省略必要的标志会导致 `confirmation_required` 错误。已知标志：`--yes` 用于修改 `workos api` 请求、角色/权限写入和成员资格角色更新；`--force` 用于 `workos connection delete`、`workos directory delete` 和 `workos debug reset`。检查已安装命令的标志：`workos --help --json`。确认标志不是进行未请求更改的权限。
- 结构化 CLI 错误（stderr 上的 JSON）包括一个可选的 `error.recovery.hints` 数组，其中每个提示都有 `description`、可选的 `command` 和可选的 `hostShellRequired`。优先使用这些提示而不是猜测下一步。

**可能遇到的遗留兼容性：**

- `WORKOS_NO_PROMPT=1` 是一个遗留别名，它设置代理交互行为和 JSON 输出。要迁移，请设置 `WORKOS_MODE=agent` 并向命令传递 `--json` 以保留两种行为。单独使用 `WORKOS_MODE=agent` 会丢弃隐式的 JSON 格式化。
- `WORKOS_FORCE_TTY=1` 仅影响输出格式；它不会改变交互模式。

## 主题 → 参考映射

> 术语查询——“X 是什么”、“X 的含义是什么”、“X 的文档 URL”、“X 的文档在哪里”、“X 的规范链接”、“在哪里在 Dashboard 中配置 X”——其中 X 是 WorkOS 特定的配置字段、端点、环境变量或术语。示例：`initiate_login_uri`、"Sign-in 端点"、"Redirect URI"、Dashboard 字段名、`WORKOS_*` 环境变量。

**不要**为像“设置 Vault”、“启用 Admin Portal”、“配置 MFA”这样的设置形状短语触发规则 0——它们路由到规则 3（特定于功能）。

**操作**：

1. 阅读 `references/workos-terms.md`——一个精心策划的表格，将 WorkOS 术语映射到规范文档 URL。
2. 如果术语在表中，请使用摘要来回答；仅当用户想要更多详细信息时才 WebFetch 列出的 URL。
3. 如果术语不在表中，请遵循该文件底部的“Still not here?”回退。当你找到规范 URL 时，回答用户并建议他们打开一个 PR 来添加一行。

**对于术语查询**，不要 WebFetch `llms.txt` 或在阅读术语文件之前猜测 `workos.com/docs/...` URL。（规则 8 和 9 使用 `llms.txt` 用于不同的目的——此禁令仅限于规则 0。）

**为什么这个会赢**：术语查询独立于功能/框架/迁移上下文。它们需要短路路由，而不是落入“模糊或通用”（规则 8）。

---

### 1. 迁移上下文

**触发**：用户提到从另一个提供程序（Auth0、Clerk、Cognito、Firebase、Supabase、Stytch、Descope、Better Auth、standalone SSO API）迁移。

**操作**：读取 `references/workos-migrate-[provider].md`，其中 `[provider]` 与源系统匹配。如果提供程序不在表中，请读取 `references/workos-migrate-other-services.md`。

**为什么这个会赢**：迁移上下文覆盖特定于功能的路由，因为用户需要提供程序特定的数据导出和转换步骤。

---

### 2. API 参考请求

**触发**：用户明确询问“API 端点”、“请求格式”、“响应模式”、“API 参考”，或提到检查 HTTP 详细信息。

**操作**：对于具有主题文件的功能（SSO、Directory Sync、RBAC、Vault、Events、Audit Logs、Admin Portal），请读取主题文件——它包括端点表。对于 AuthKit 或 Organization API，请读取 `references/workos-api-[domain].md`。

**为什么这个会赢**：API 参考是低级别的；功能主题是高级别的，但包括端点表供快速参考。

---

### 3. 特定于功能的请求

**触发**：用户通过名称提到特定的 WorkOS 功能（SSO、MFA、Directory Sync、Audit Logs、Vault、RBAC、FGA、Admin Portal、Custom Domains、Events、Integrations、Email、Pipes、Feature Flags、Radar）。

**操作**：读取 `references/workos-[feature].md`，其中 `[feature]` 是小写 slug（sso、mfa、directory-sync、audit-logs、vault、rbac、fga、admin-portal、custom-domains、events、integrations、email、pipes、feature-flags、radar）。

**例外**：小部件请求通过技能工具加载 `workos-widgets` 技能——它有自己的编排。

**歧义**：如果用户同时提到一个功能和“API”，则路由到主题文件——它包括端点。如果他们提到多个功能，则路由到**最具体的**一个（例如，“SSO with MFA and directory sync”→路由到 SSO；用户可以单独请求 MFA 和 Directory Sync）。如果用户提到“FGA”或“细粒度授权”，则路由到 `workos-fga`——不是 `workos-rbac`。RBAC 是组织级角色；FGA 是在 RBAC 之上的资源范围角色。

**特殊情况——IdP 组 → 角色映射**：如果用户询问将 Entra / Azure AD / Okta / Google Workspace / SCIM / 目录 / SSO 组映射到 WorkOS 角色（无论确切措辞如何），请同时读取 `workos-rbac.md` 和源特定参考：

- Directory Sync / SCIM / Google Workspace 组 → 还要读取 `workos-directory-sync.md`
- 仅 SSO 组 → 还要读取 `workos-sso.md`

这两个文件现在都有规范配方。不要凭记忆或释义 Dashboard 菜单路径——文档没有承诺确切的点击路径，所以你也应该这样做。这种映射**不是** WorkOS CLI 操作；如果要求 CLI 命令，请说明它不在 CLI 中，并链接到文档。

---

### 4. AuthKit 安装

**触发**：用户提到身份验证设置、登录流程、注册或会话管理，或者明确说“AuthKit”而不提及特定功能，如 SSO 或 MFA。

**操作**：使用下面的优先级排序检查检测框架和语言。读取相应的参考文件和 `references/workos-authkit-setup.md`。在报告集成完成之前，完成其应用程序设置和流程检查。

**歧义**：

- 如果用户说“通过 AuthKit 进行 SSO 登录”，则路由到 `workos-sso` (#3)——功能胜过框架。
- 如果用户说“使用 Google 进行 React 登录”，则路由到 AuthKit React (#4)——这是 AuthKit 级别的身份验证，不是 SSO API。
- 如果用户已经使用 AuthKit 并想添加功能（例如，“将 MFA 添加到我的 AuthKit 应用程序”），则路由到功能参考 (#3)，而不是回到 AuthKit 安装。

#### AuthKit 框架检测优先级（仅限 AuthKit）

按此顺序检查。第一个匹配项获胜：

```
1. `@tanstack/start` 在 package.json 依赖项中
   → 读取：references/workos-authkit-tanstack-start.md

2. `@sveltejs/kit` 在 package.json 依赖项中
   → 读取：references/workos-authkit-sveltekit.md

3. `react-router` 或 `react-router-dom` 在 package.json 依赖项中
   → 读取：references/workos-authkit-react-router.md

4. `next.config.js` 或 `next.config.mjs` 或 `next.config.ts` 存在于项目根目录
   → 读取：references/workos-authkit-nextjs.md

5. (`vite.config.js` 或 `vite.config.ts` 存在) AND `react` 在 package.json 依赖项中
   → 读取：references/workos-authkit-react.md

6. 以上都没有检测到
   → 读取：references/workos-authkit-vanilla-js.md
```

#### 语言检测（后端 SDK）

如果项目不是 JavaScript/TypeScript 前端框架，请检查：

```
1. `pyproject.toml` 或 `requirements.txt` 或 `setup.py` 存在
   → 读取：references/workos-python.md

2. `go.mod` 存在
   → 读取：references/workos-go.md

3. `Gemfile` 存在 或 `config/routes.rb` 存在
   → 读取：references/workos-ruby.md

4. `composer.json` 存在 AND `laravel/framework` 在依赖项中
   → 读取：references/workos-php-laravel.md

5. `composer.json` 存在（没有 Laravel）
   → 读取：references/workos-php.md

6. `*.csproj` 或 `*.sln` 存在
   → 读取：references/workos-dotnet.md

7. `build.gradle.kts` 或 `build.gradle` 存在
   → 读取：references/workos-kotlin.md

8. `mix.exs` 存在
   → 读取：references/workos-elixir.md

9. `package.json` 存在，带有 `express` / `fastify` / `hono` / `koa`（后端 JS）
   → 读取：references/workos-node.md
```

**为什么这个顺序**：TanStack、SvelteKit 和 React Router 比 Next.js/Vite+React 更具体。一个项目可以同时具有 Next.js 和 React Router；在这种情况下，React Router 赢得，因为它更具体。Vanilla JS 是在未检测到框架时的回退。在未检测到前端框架时检查后端语言。

**边缘情况——检测到多个框架**：如果你检测到冲突信号（例如，Next.js 和 TanStack Start 配置都存在），请**询问用户他们想要使用哪个框架**。不要猜测。

**边缘情况——从上下文中不清楚框架**：如果用户说“添加登录”但无法扫描文件（远程存储库、无访问权限），请**询问**：“您使用的是哪个框架/语言？”不要默认，除非得到确认。

---

### 5. 集成设置

**触发**：用户提到连接到外部 IdP、配置第三方集成，或询问“如何与 [提供程序] 集成”。

**操作**：读取 `references/workos-integrations.md`。

**为什么与 SSO 分开**：SSO 涵盖身份验证流程；集成涵盖 IdP 配置和连接设置。如果用户同时提到 SSO 和集成（例如，“设置 Google SSO”），则路由到 SSO (#3)——它将参考集成，在需要时。
