# Clerk CLI

`clerk` 二进制文件是 Clerk 后端 API 和平台 API 的预认证网关，以及项目级别的工具（认证、链接、环境拉取、实例配置）。当用户需要任何与 Clerk 资源交互的操作时，请优先使用 `clerk` 而不是手动编写 `curl`。

> 此技能针对 `clerk` 的 `latest` 版本。如果 `clerk --version` 与最新可用的 CLI 不一致，请使用 `clerk update` 刷新它，或通过 `bunx clerk@latest` 等包运行器调用最新版本。二进制文件始终是真相来源，因此运行 `clerk <命令> --help` 来验证此技能声称的任何内容。

## 执行环境（优先主机，理解沙盒警告）

大多数 AI 编码代理默认在沙盒中运行 shell 命令，其中用户的 home 目录、操作系统密钥链、浏览器启动、本地回调和网络访问可能会被阻止。Clerk CLI 依赖于所有这些主机功能：

- **操作系统凭证存储**：`clerk auth login` 将 OAuth 令牌存储在系统密钥链中。没有密钥链访问的沙盒报告“未登录”，即使主机已通过身份验证。
- **Home 目录 Clerk 状态**：保存的配置、缓存的元数据和备用凭证位于用户的 Clerk 配置/数据目录下。
- **链接项目元数据**：从仓库的 git 远程和 Clerk 配置解析。具有剥离的仓库状态或阻止 home 目录读取的沙盒可能会错误报告“未链接”。
- **本地 `.env*` 文件**：`clerk env pull` 生成的可发布和秘密密钥。
- **出站网络访问到 Clerk**：每个后端和平台 API 调用。
- **浏览器 + 本地主机 OAuth 回调**：`clerk auth login` 需要两者。

在代理模式下，CLI 现在在主机敏感的库边界处执行**最佳努力单次警告检查**。当它检测到仅主机可用的 Clerk 状态或系统功能不可用时，它会发出：

```text
在代理模式下，可能无法使用主机仅有的 Clerk 状态或系统功能。这可能是一次沙盒运行。
在主机 shell 上重新运行此命令，然后再信任认证、链接、环境或 API 失败。
```

将此警告视为权威。命令可以继续，但任何来自该调用的认证、链接、环境、配置、API、浏览器或 OAuth 回调失败都不受信任，直到您在主机上重新运行相同的命令。

**请在这些命令上用户的宿主机 shell 上运行，而不是在沙盒中运行：**

`clerk doctor`, `clerk whoami`, `clerk auth login`, `clerk link`, `clerk env pull`,
`clerk apps ...`, `clerk config ...`, `clerk api ...`。

如果命令意外地在沙盒中运行并报告 `Not logged in`、`auth_required`、`not linked`、缺少环境、密钥链/文件权限错误或网络故障，**不要将结果视为权威**。在执行它或向用户报告它之前，在主机上重新运行它。

## 调用 CLI

在运行任何 `clerk` 命令之前，确定要调用的二进制文件并绑定该选择以供会话其余时间使用：

```sh
# 1. 当它匹配技能的目标版本时，优先使用全局安装的二进制文件。
command -v clerk >/dev/null 2>&1 && clerk --version
```

如果它打印 `latest` 或任何您信任的版本，则对于会话的其余时间使用裸 `clerk`。

否则，按以下顺序回退到包运行器（与 CLI 自己的 `preferredRunner` 逻辑匹配，该逻辑优先考虑与项目锁文件匹配的运行器）：

| 项目包管理器   | 调用方式                       |
| -------------- | ------------------------------ |
| bun (`bun.lock*`) | `bunx clerk@latest`     |
| npm (`package-lock.json`) | `npx -y clerk@latest`   |
| pnpm (`pnpm-lock.yaml`) | `pnpm dlx clerk@latest` |
| yarn >= 2 (`yarn.lock`)   | `yarn dlx clerk@latest` |

Yarn Classic（v1）没有 `dlx`；将那些项目视为“没有首选运行器”，并回退到列表上方的第一个在 PATH 上的运行器。

发布的 npm 包是 **`clerk`**，而不是 `@clerk/cli`。切勿将 `npm install -g clerk` 作为主要路径。如果全局 CLI 过期或行为与此技能不同，请升级全局安装或回退到上面的 `latest` 运行器形式。

## 前提条件（会话开始时运行）

在会话中运行任何其他 Clerk 命令之前，请验证 CLI 已通过身份验证、已链接且健康：

```sh
clerk --version               # 确认二进制文件在 PATH 上
clerk doctor --json           # 结构化健康检查；如果任何检查失败，则退出 1
```

**始终首先运行 `clerk doctor --json`。** 它捕获常见的设置失败（未登录、项目未链接、缺少密钥、CLI 版本过时），以便后续命令不会因令人困惑的错误而失败。在代理模式下，它还包括 `Host execution` 检查，当 Clerk 的主机端配置/凭证目录不可写时发出警告，这是当前调用可能是沙盒的经典信号。

每个结果都有 `name`、`status`（`pass`/`warn`/`fail`）、`message`、可选的 `detail`、可选的 `remedy`（如何修复它）和可选的 `fix`（可自动修复问题的标签）。解析它并采取行动，或向用户展示它。如果 `Host execution` 警告，请在同一沙盒运行中在主机上重新运行相同的命令，然后再信任任何认证/链接/环境/API 失败。当后续命令开始行为异常时，重新运行 `clerk doctor --json`。

如果 `clerk --version` 报告比此技能涵盖的新 CLI，请首先信任 `clerk <命令> --help` 并从其来源刷新此技能包。反过来也适用：`--accountless` 和 `accountless` JSON 键从 CLI 3.3+ 开始提供——在较旧的 CLI 上，使用 `--keyless` 别名或升级。

## 无账户设置

`clerk init` 不需要 `clerk auth login`：在一个支持无账户的框架上，无认证的引导程序没有 `--app`，或无认证的代理运行没有 `--app` 或现有的项目链接，会生成一个未认领的无账户应用和临时开发密钥——没有账户，没有浏览器，没有标志。 （一个注销的人类在*现有*项目中重新运行它会得到登录流程——`--accountless` 强制临时密钥路径。）然后大多数实例命令都在该密钥上工作。

有两件事在您使用它之前要知道：无账户路径遵循本地 whatever `sk_` 密钥——`sk_live_` 包括在内，无论是否已认领——所以当您指的是一个真实应用时，请传递 `--app <id>`；并且 `clerk open` 返回一个凭证等效的声明 URL，永远不会安全地粘贴到日志或 PR 中。

哪些命令需要账户，以及完整规则：[auth.md](references/auth.md#accountless-operating-without-an-account)。

## 心智模型

| 层级                           | 它的作用                                                                                 | 命令                                                       |
| ------------------------------- | -------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| **会话 / 项目**               | 认证、将此仓库链接到 Clerk 应用，拉取环境密钥                                              | `auth login`, `link`, `unlink`, `whoami`, `env pull`, `doctor` |
| **实例配置**             | 管理特定实例的配置（社交提供程序、会话寿命等）                                                 | `config pull`, `config schema`, `config patch`, `config put`   |
| **后端 API (默认)**       | 运行时数据：用户、组织、会话、邀请、JWT 模板、Webhooks                    | `clerk api <path>`                                             |
| **平台 API (`--platform`)** | 账户级：应用、实例、计费                                              | `clerk api --platform <path>`                                  |
| **前端 API (`--fapi`)**     | 实例的公共面向客户端 API（clerk-js 调用的）                                                | `clerk api --fapi <path>`                                      |

通过 `clerk link` 将项目链接到应用。一旦链接，大多数命令会自动从仓库的 git 远程解析目标应用和开发实例。要针对其他内容，请传递 `--app <id>` 和/或 `--instance dev|prod|<instance_id>`。有关完整解析顺序，请参阅 [references/auth.md](references/auth.md)。

## 发现端点 - 不要记忆它们

CLI 随附 Clerk OpenAPI 目录。始终动态发现端点而不是猜测路径：

```sh
clerk api ls                  # 列出每个后端 API 端点
clerk api ls users            # 通过关键字过滤（匹配路径、摘要、标签、operationId）
clerk api ls --platform apps  # 列出平台 API 端点
```

在使用 `clerk api <path>` 之前使用此命令。如果您看不到预期的端点，它可能没有被公开。

## `clerk api` 命令（工作horse）

`clerk api` 执行认证的 HTTP 调用。它自动解析密钥，自动从正文存在中检测方法，支持 stdin，并且可以使用 `--dry-run` 预览突变。

```sh
# GET 请求
clerk api /users                                  # 列出用户
clerk api /users/user_abc123                      # 获取一个
clerk api /users?limit=5&order_by=-created_at     # 查询参数可以内联工作

# 可变请求
clerk api /users -d '{"email_address":["a@b.co"]}'          # POST (从正文自动检测)
clerk api /users/user_abc123 -X PATCH -d '{"first_name":"A"}'
clerk api /users/user_abc123 -X DELETE

# 正文来自文件或 stdin
clerk api /users --file payload.json
cat payload.json | clerk api /users

# 始终首先预览突变
clerk api /users/user_abc123 -X DELETE --dry-run
clerk api /users/user_abc123 -X DELETE --yes      # 确认后跳过确认

# 针对特定应用/实例
clerk api /users --app app_abc123 --instance prod

# 包含响应头进行调试
clerk api /users --include

# 平台 API (账户级，不是租户数据)
clerk api /v1/platform/applications --platform

# 前端 API (实例的公共面向客户端 API — clerk-js 调用的)
# 未认证；`--fapi` 和 `--platform` 不能组合，`--secret-key` 被忽略)
clerk api --fapi /environment
```

在人类模式下，不带参数的 `clerk api` 打开交互式请求构建器；在代理模式下它打印使用说明并退出 `0`——始终明确传递端点（或 `ls`）。

对于实例配置，请优先使用专用的 `clerk config ...` 命令而不是原始 Platform API `/config` 路径。它们比原始端点形式更干净地处理 dry-run、diffing 和确认。

**在运行真实操作之前始终 `--dry-run` 突变。** 然后重新运行而不带 `--dry-run`（如果确定，请添加 `--yes`）。在代理模式下，交互式确认被绕过，因此 `--dry-run` 是破坏性调用的唯一安全网。

**JSON 正文必须有效。** CLI 验证并拒绝格式不良的有效负载。

**端点路径可以带或不带 `/v1/` 前缀** - 两者都对 Backend API 调用有效。CLI 会规范化。

有关具体模式：列出/过滤用户、创建组织、模拟会话等，请参阅 [references/recipes.md](references/recipes.md)。

## 检查大型输出（不要淹没您的上下文）

`users list`、`apps list`、`config pull` 以及大多数 `clerk api` GET 返回的有效负载可能很大（可以是几千字节或兆字节）。生产租户通常有数千名用户；实例配置可以很深（几百个字段）。将那些响应读入对话会浪费上下文窗口而没有任何好处。首先将响应保存到文件中，然后使用 `jq` 查询您需要的内容：

```sh
# 1. 持久化响应。使用 `--limit 250` 来最大化 users list 的页面大小。
clerk users list --json --limit 250 > /tmp/users.json
clerk apps list --json                > /tmp/apps.json
clerk api /users/user_abc123          > /tmp/user.json

# 2. 仅检查您需要的内容。
jq '.data | length'                       /tmp/users.json   # 当前页面大小
jq '.hasMore'                             /tmp/users.json   # 是否有更多页面可用？
jq '.data[0] | keys'                      /tmp/users.json   # 一次性发现用户形状
jq '.data[] | {id, email_addresses}'      /tmp/users.json   # 投影到几个字段
jq '[.data[] | select(.banned)] | length' /tmp/users.json   # 不读取行进行聚合
```

**如果 `jq` 不可用**，回退到 Python 或 Node - 两者都可以在不打印整个文件的情况下流式传输文件：

```sh
python3 -c 'import json; d=json.load(open("/tmp/users.json")); print(len(d["data"]), d["hasMore"])'
node -e 'const d=require("/tmp/users.json"); console.log(d.data.length, d.hasMore)'
```

仅当您确实需要看到原始结构进行一次性调试时才使用 `cat` / `head` 文件。当遍历页面时，将每个页面写入其自己的文件（例如 `page-${offset}.json`），以便单个页面可以独立检查。

## 核心命令一览

| 命令                       | 目的                                                                                                                                                                                                                                                                                                             | 关键标志                                                                                                                                                                        |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `clerk init`                  | 在项目中构建 Clerk。无认证的引导程序没有 `--app`，或无认证的代理运行没有 `--app` 或现有的链接，默认写入临时开发密钥——无需标志、无需账户、无需浏览器。`--starter` 仅支持 Next.js、React Router、Astro、Nuxt、TanStack Start、React、Vue 和 JavaScript 的引导程序。`--accountless` 与 `--app`/`--login` 结合使用，以及 `--template`/`--fresh` 与 `--login` 结合使用，在构建任何内容之前是使用错误。`--template`/`--fresh` 在一个 *解析* 为真实应用的运行中（包括仅在登录时）仅在策略解析后出错——因此一个 starter 运行会保留构建的项目。 | `--framework`, `--pm`, `--name` (with `--starter`), `--app`, `--starter`, `--accountless`, `--login`, `--template`, `--fresh`, `-y`, `--no-skills`                                   |
| `clerk auth login`            | OAuth 浏览器登录（存储令牌）。引导程序或无账户实例配置不需要它。代理模式：如果已登录，则为无操作。如果没有存储的会话，它仍然会打开浏览器并绑定本地回调，因此它不是无监督的；请优先使用 `CLERK_PLATFORM_API_KEY` 进行无头流程。别名：`signup`, `signin`, `sign-in`。顶层快捷方式：`clerk login`。 | -                                                                                                                                                                                |
| `clerk auth logout`           | 清除存储的凭证。别名：`signout`, `sign-out`。顶层快捷方式：`clerk logout`。                                                                                                                                                                                                                       | -                                                                                                                                                                                |
| `clerk whoami`                | 打印登录的电子邮件。                                                                                                                                                                                                                                                                                          | -                                                                                                                                                                                |
| `clerk link` / `clerk unlink` | 将此仓库链接到 Clerk 应用，或删除链接。`unlink` 在代理模式下需要 `--yes`。                                                                                                                                                                                                                         | (see `--help`)                                                                                                                                                                   |
| `clerk env pull`              | 将可发布 + 秘密密钥写入框架的环境文件（合并，而不是覆盖）。解析 `.env.development.local` → 框架首选文件 → `.env.local`；使用 `--file` 覆盖。                                                                                                                              | (see `--help`)                                                                                                                                                                   |
| `clerk config {pull,schema}`  | 获取实例配置 JSON，或其 JSON Schema。                                                                                                                                                                                                                                                                     | (see `--help`)                                                                                                                                                                   |
| `clerk config patch`          | 部分更新（PATCH）实例配置。传递 `--destructive` 以实际删除补丁触发的子资源而不是将它们重置为默认值。                                                                                                                                                                                               | `--app`, `--instance`, `--file`, `--json`, `--dry-run`, `--yes`, `--destructive`                                                                                                 |
| `clerk config put`            | 完全替换（PUT）实例配置。传递 `--destructive` 以实际删除删除的子资源而不是将它们重置为默认值。                                                                                                                                                                                                        | `--app`, `--instance`, `--file`, `--json`, `--dry-run`, `--yes`, `--destructive`                                                                                                 |
| `clerk apps {list,create}`    | 列出或创建 Clerk 应用。默认为 JSON 在代理模式下。                                                                                                                                                                                                                                                  | (see `--help`)                                                                                                                                                                   |
| `clerk users` (no subcommand) | 在人类模式下 `users` 操作的交互式选择器；在代理模式下打印操作列表并退出 `2`。始终从代理中传递明确的子命令。                                                                                                                                                           | `--app`, `--instance`, `--secret-key`                                                                                                                                            |
| `clerk users list`            | 通过精心设计的 BAPI 标志列出用户。JSON 输出（在管道或代理模式下默认）是 `{data, hasMore}`，因此调用者可以分页而无需 `/users/count`。 `--limit` 默认为 100（最大 250）。                                                                                                                      | `--limit`, `--offset`, `--query`, `--email-address`, `--phone-number`, `--username`, `--user-id`, `--external-id`, `--order-by`, `--json`, `--app`, `--instance`, `--secret-key` |
| `clerk users create`          | 从精心设计的标志或原始 BAPI 正文创建用户。**任何模式下都不需要确认提示** - 它会立即写入。`--yes` 是接受的，但没有任何效果。`--dry-run` 是唯一的保险；首先预览它。                                                                                                                                                                                                                            | `--email`, `--phone`, `--username`, `--password`, `--first-name`, `--last-name`, `--external-id`, `-d, --data`, `--file`, `--dry-run`, `--yes`, `--json`                         |
| `clerk users open [user-id]`  | 打开用户的仪表板页面。代理模式需要 `user-id` 并打印 JSON 描述符而不是启动浏览器。                                                                                                                                                                                            | (see `--help`)                                                                                                                                                                   |
| `clerk impersonate [user]`    | 作为用户进行调试：创建一个短期演员令牌并打印登录 URL。别名：`clerk imp`。需要 `clerk auth login`（没有 `--secret-key` 仅绕过）——每个令牌都标记为 `cli:<email>` 以便进行审计。`[user]` 接受 `user_...` ID、确切的电子邮件或模糊搜索词。在生产中，它会绕过用户的 MFA 并可能计入模拟配额——在执行任何生产突变之前，请先与用户确认。 | `--print`, `--open`, `--yes`, `--expires-in <seconds>` (默认 3600), `--actor <context>`, `--app`, `--instance`                                                                |
| `clerk impersonate revoke <actor-token-id>` | 撤销一个挂起的演员令牌。演员令牌 `id` 仅在创建时打印（后端 API 没有演员令牌列表端点），因此请在此处捕获它。                                                                                                                                                      | `--app`, `--instance`                                                                                                                                                            |
| `clerk open [subpath]`        | 在浏览器中打开链接应用的仪表板。代理模式：打印 JSON 描述符而不是打开。                                                                                                                                                                                                              | (see `--help`)                                                                                                                                                                   |
| `clerk deploy`                | 人类模式生产部署向导。代理模式：发出只读 JSON 手交，并告诉代理是否要询问人类运行向导、等待配置、完成 OAuth 或不做任何事。                                                                                                                 | `--mode agent`, `--mode human`, `--verbose`                                                                                                                                      |
| `clerk deploy status`         | 只读部署验证。触发 DNS 检查，报告聚合域和 OAuth 准备情况，并且仅在完成时退出 `0`。代理模式默认执行一次快速检查；传递 `--wait` 以保持等待。                                                                                                     | `--mode agent`, `--wait`, `--verbose`                                                                                                                                            |
| `clerk webhooks listen`       | 第一方本地 webhook 隧道（类似于 `stripe listen`）：打开一个 Svix 中继收件箱 URL 并将每个交付转发到您的本地处理程序。无需认证、无需链接项目、无需 Clerk API。完整流程在 [references/recipes.md](references/recipes.md#webhooks-local-testing)。                                                 | `--forward-to <url>` (required), `--token <c_token>`, `-H, --header <k:v>` (repeatable), `--json` (NDJSON)                                                                       |
| `clerk webhooks token`        | 生成一个中继令牌（`c_` + 10 base62 字符），以跨机器固定稳定的 `listen` 收件箱 URL：`clerk webhooks listen --token "$(clerk webhooks token)" --forward-to ...`.                                                                                                                                          | `--json`                                                                                                                                                                         |
| `clerk webhooks verify`       | 纯粹本地 HMAC 离线验证 webhook 签名（无需认证）：从保存的 `listen` 事件行（`--delivery @event.json`）或从四个原始值中。                                                                                                                                                             | `--secret <whsec>` (required), `--delivery @file`, `--payload @file`, `--id`, `--timestamp`, `--signature`, `--json`                                                             |
| `clerk enable orgs` / `clerk disable orgs` | 切换实例上的组织。对于组织功能、组件和 API 使用，请参阅 `clerk-orgs` 技能。                                                                                                                                                                                         | `--force-selection`, `--auto-create`, `--max-members <n>`, `--domains`, `--dry-run`, `--yes`, `--app`, `--instance`                                                              |
| `clerk enable billing` / `clerk disable billing` | 为用户和/或组织切换计费（默认为两者）。对于计划、定价组件和许可，请参阅 `clerk-billing` 技能。                                                                                                                                                         | `--for <orgs\|users>`, `--dry-run`, `--yes`, `--no-skills` (仅启用), `--app`, `--instance`                                                                                  |
| `clerk doctor`                | 健康检查（CLI 版本、登录、链接、环境、完成；在代理模式下还包括 `Host execution` 检查）。                                                                                                                                                                                                          | `--json`, `--spotlight`, `--verbose`, `--fix`                                                                                                                                    |
| `clerk api [path]`            | 认证的 HTTP 到 Backend/Platform API.                                                                                                                                                                                                                                                                         | `-X`, `-d`, `--file`, `--dry-run`, `--yes`, `--include`, `--app`, `--secret-key`, `--instance`, `--platform`                                                                     |
| `clerk api ls [filter]`       | 从捆绑的 OpenAPI 目录发现端点。                                                                                                                                                                                                                                                                                | (see `--help`)                                                                                                                                                                   |
| `clerk completion [shell]`    | 打印 shell 完成脚本 (`bash`, `zsh`, `fish`, `powershell`).                                                                                                                                                                                                                                              | -                                                                                                                                                                                |
| `clerk update`                | 将 CLI 更新到最新版本。                                                                                                                                                                                                                                                                                           | `--channel`, `-y`, `--all`                                                                                                                                                       |

**`clerk <命令> --help` 是此技能声明的真相来源。此表只是一个提示，不是规范。在运行不熟悉的命令或标志组合之前，在每个会话中运行一次 `clerk <命令> --help`。每个命令也在源代码中定义了 `setExamples([...])`，`--help` 会将其渲染为可复制粘贴的 Examples 块，因此您很少需要猜测语法。

## 代理模式行为（重要）

CLI 在 stdout 不是 TTY 或设置 `--mode agent` / `CLERK_MODE=agent` 时自动检测代理模式。在代理模式下：

- **交互式提示被禁用。** 原本会显示选择器的命令（`link` 没有 `--app`, `unlink` 没有 `--yes`, `users` 没有 subcommand）要么自动解析，要么退出使用用法错误。`clerk api` 带无参数打印使用说明并退出 0；明确传递端点（或 `ls`）。始终在脚本调用中传递明确的标志 (`--app`, `--yes`)。
- **主机敏感的操作在主机敏感的库边界处发出一次警告。** Home 目录 Clerk 状态、密钥链访问、到 Clerk 的出站网络访问、浏览器启动和本地主机 OAuth 回调设置可以触发上述警告。如果出现警告，请在主机上重新运行相同的命令，然后再信任结果。
- **如果您的托管程序没有明确呈现为代理模式，请强制执行它。** 当您想要 CLI 的非交互行为和沙盒警告路径确定性地应用时，请使用 `--mode agent` 或 `CLERK_MODE=agent`。
- **`link` 支持确定的代理流程。** 在代理模式下，`clerk link --app <id>` 直接链接。如果没有 `--app`, CLI 将首先尝试静默密钥自动链接；如果它无法明确确定应用，它将退出并告诉您传递 `--app`。
- **`init` 无需登录——不要首先登录。** 无认证的代理运行会生成一个未认领的无账户应用和临时开发密钥：没有标志，没有账户，没有浏览器。`--app <id>` 或预先链接会针对真实应用；`--accountless` 强制临时密钥路径而不是会话和现有链接。`--keyless` 仍然是兼容性别名。一个没有临时密钥支持且没有应用目标的框架会打印手动指导并干净退出。
标志排他性在上述命令表中。
- **`--fresh` 是破坏性的。** 它会替换临时应用并覆盖 env 密钥和 `.clerk/keyless.json` 踪迹，无需提示，会遗弃先前应用及其用户。切勿仅为了重新运行 `init` 而传递它。
- **`unlink` 在代理模式下需要 `--yes`。** 它基于 `isAgent() && !options.yes` 并在没有它的情况下退出使用用法错误。这是例外，不是模式 - 请参阅下一个要点。
- **只有 `unlink` 实际上需要 `--yes`。** 其他确认门是作为 `isHuman() && !options.yes` 编写的，因此代理模式会直接执行而无需提示和错误。传递 `--yes` 无害但不会改变任何内容。不要将其视为安全门 - `--dry-run` 是真正的安全网。
- **`impersonate` 需要在代理模式下传递 `[user]` 位置参数。** 如果搜索词匹配多个用户，它将退出 `2` 并列出候选用户 ID — 重试时使用特定的 `user_...` ID。输出是一个 JSON 对象 (`{url, id, userId, actor, ...}`); 将 `url` 展示给用户并捕获 `id` — 它是记录撤销句柄的唯一机会。
- **`webhooks listen` 是长时间运行的。** 在后台运行它。在代理模式（或使用 `--json`）它会发出 NDJSON：一条 `ready` 行 (`{type:"ready", relay_url, forward_to}`), 然后每交付一条 `event` 行——每条事件行都可以反馈到 `clerk webhooks verify --delivery`.
- **`doctor --fix` 被忽略。** 解析 `doctor --json` 输出的 `remedy` 字段并自行采取行动。
- **`apps list` 和 `apps create` 在管道时默认为 JSON**，就像 `users` 一样。`clerk users list` 和 `clerk users create` 在代理模式下发出 JSON。裸 `clerk users`（无 subcommand）在代理模式下是使用错误 - 明确传递 `list`, `create` 或 `open` 显式地。`clerk users open` 在代理模式下需要 `user-id` 位置参数并打印 JSON 描述符而不是启动浏览器。
- **`deploy` 有代理手交加上验证门。** 在代理模式下，裸 `clerk deploy` 是只读的并发出 JSON 手交。它永远不会驱动交互式向导。不要告诉 Claude 或其他代理运行 `! clerk deploy`，因为向导需要交互式 stdin 提示。当需要时，请在新终端窗口中让人类运行 `clerk deploy`，然后运行 `clerk deploy status --mode agent` 以验证完成。请参阅 [references/agent-mode.md](references/agent-mode.md#deploy-handoff-and-verification).
- **`--input-json <json|@file|->`** 将 JSON 扩展为标志，适用于任何命令（例如 `clerk init --input-json '{"framework":"next","yes":true}'`). Stdin 需要明确的 `-` 标记 (`echo '{"yes":true}' | clerk init --input-json -`); 裸管道 stdin **不会**自动检测，因此 shell 循环和自我读取命令 (`cat body.json | clerk api …`) 保持不变。在 `--input-json` 后面放置 `--input-json`。完整规则在 [references/agent-mode.md](references/agent-mode.md#passing-options-as-json---input-json).

完整矩阵和沙盒详细信息在 [references/agent-mode.md](references/agent-mode.md).

## 输出格式和错误

- **JSON 输出:** `--json` 在 `apps list` 和 `doctor` 上。对于 `clerk api`, 响应正文是原始 API JSON, 因此可以自由地管道到 `jq`。
- **退出代码:** `0` 成功, `1` 运行时错误, `2` 使用/验证错误。`doctor` 返回 `1` 如果任何检查失败。
- **错误格式:** 用户面错误的打印一行到 stderr 并设置非零退出代码。调试时使用 `--verbose` 获取堆栈跟踪。

## 自主使用的安全规则

1. **在行动之前发现:** `clerk api ls <keyword>` 在 `clerk api <path>` 之前。
2. **预览突变:** 在每个 `config patch`, `config put`, `api -X POST/PATCH/PUT/DELETE` 上 `--dry-run`。
3. **在生产的明确目标:** 传递 `--instance prod` 而不是依赖默认值，并在执行任何生产突变之前与用户确认。
4. **永远不要提交密钥:** `env pull` 写入到 `.env.local`（应该被 git 忽略）。不要将密钥粘贴到代码或聊天中。
5. **使用 `doctor --json`** 在假设 CLI 出现故障之前进行诊断。

## 参考

- [references/auth.md](references/auth.md) - 认证流程、密钥解析顺序、主机与沙盒行为、`--app`/`--instance` 目标、Backend vs Platform API。
- [references/recipes.md](references/recipes.md) - 可复制粘贴的常见 Clerk 任务配方。
- [references/agent-mode.md](references/agent-mode.md) - 代理模式行为矩阵、沙盒警告语义、退出代码、错误格式。
