---
name: clerk-cli
description: 操作Clerk CLI（`clerk`二进制文件）用于身份验证、用户/组织/会话管理、模拟、本地webhook测试、部署验证、实例配置、环境密钥、功能开关，以及任何Clerk后端、平台或前端API调用。当用户提及Clerk管理任务，如“列出Clerk用户”、“模拟用户”、“本地测试webhooks”、“启用组织”、“启用计费”、“Clerk环境拉取”、“Clerk医生”、“Clerk部署”、“Clerk API”或任何临时的Clerk API请求时，请使用CLI。优先选择CLI而非原始HTTP：它自动处理身份验证、密钥解析、应用/实例目标定位和格式化。
---

# Clerk CLI

`clerk` 二进制文件是 Clerk 后端 API 和平台 API 的预认证网关，以及项目级别的工具（认证、链接、环境拉取、实例配置）。当用户需要任何与 Clerk 资源相关的操作时，请优先使用 `clerk` 而不是手动编写 `curl`。

对于设置或 `init` 请求，请使用 [`clerk-setup`](../clerk-setup/SKILL.md) 技能作为权威来源。它的包运行器、无账户、迁移和无账户优先初始化指南优先于以下通用操作先决条件。

> 此技能针对 clerk `latest` 版本。如果 `clerk --version` 与最新可用的 CLI 不一致，请使用 `clerk update` 刷新它，或通过 `bunx clerk@latest` 等包运行器调用最新版本。二进制文件始终是权威来源，因此运行 `clerk <命令> --help` 以验证此技能声称的内容。

## 执行环境（优先使用主机，理解沙盒警告）

大多数 AI 编码代理默认在沙盒中运行 shell 命令，其中用户的家目录、操作系统密钥链、浏览器启动、本地主机回调绑定或网络访问可能被阻止。Clerk CLI 依赖于所有这些主机功能：

- **操作系统凭证存储**：`clerk auth login` 将 OAuth 令牌存储在系统密钥链中。没有密钥链访问权限的沙盒即使主机已认证也会报告“未登录”。
- **家目录 Clerk 状态**：保存的配置、缓存的元数据和备用凭证位于用户 Clerk 配置/数据目录下。
- **链接项目元数据**：从仓库的 git 远程和 Clerk 配置解析。具有剥离仓库状态或阻止家目录读取的沙盒可能会错误报告“未链接”。
- **本地 `.env*` 文件**：由 `clerk env pull` 生成的可发布和秘密密钥。
- **出站网络访问到 Clerk**：每个后端和平台 API 调用。
- **浏览器 + 本地主机 OAuth 回调**：`clerk auth login` 需要两者。

在代理模式下，CLI 现在在主机敏感的库边界执行**最佳努力单次警告检查**。当它检测到主机专用的 Clerk 状态或系统功能不可用时，它会发出：

```text
在代理模式下，主机专用的 Clerk 状态或系统功能可能不可用。这可能是一次沙盒运行。
在主机 shell 上重新运行此命令，然后再信任认证、链接、环境或 API 失败。
```

将此警告视为权威。命令可以继续，但任何来自该调用的认证、链接、环境、配置、API、浏览器或 OAuth 回调失败都不可信，直到您在主机上重新运行相同的命令。

**优先在用户的主机 shell 上运行这些命令，而不是在沙盒中：**

`clerk doctor`, `clerk whoami`, `clerk auth login`, `clerk link`, `clerk env pull`,
`clerk apps ...`, `clerk config ...`, `clerk api ...`。

如果命令意外地在沙盒中运行，并且报告“未登录”、“auth_required”、“未链接”、缺失环境、密钥链/文件权限错误或网络故障，**不要将结果视为权威**。在执行操作或向用户报告之前，在主机上重新运行它。

## 调用 CLI

在运行任何 `clerk` 命令之前，确定要调用的二进制文件并绑定该选择以供会话其余部分使用：

```sh
# 1. 优先使用与技能目标版本匹配的全局安装二进制文件。
command -v clerk >/dev/null 2>&1 && clerk --version
```

如果它打印 `latest` 或任何您信任的版本，请在会话其余部分使用裸 `clerk`。

否则，按以下顺序回退到包运行器（与 CLI 自己的 `preferredRunner` 逻辑匹配，该逻辑优先选择与项目锁文件匹配的运行器）：

| 项目包管理器   | 调用方式                       |
| -------------- | ------------------------------ |
| bun (`bun.lock*`) | `bunx clerk@latest`     |
| npm (`package-lock.json`) | `npx -y clerk@latest`   |
| pnpm (`pnpm-lock.yaml`) | `pnpm dlx clerk@latest` |
| yarn >= 2 (`yarn.lock`)   | `yarn dlx clerk@latest` |

Yarn Classic (v1) 没有 `dlx`；将那些项目视为“没有首选运行器”，并回退到上面列表中第一个在 PATH 上的运行器。

发布的 npm 包是 **`clerk`**，而不是 `@clerk/cli`。切勿将 `npm install -g clerk` 作为主要路径。如果全局 CLI 已过时或与此技能行为不同，请升级全局安装或回退到上面 `latest` 运行器形式。

## 先决条件（在非设置操作会话开始时运行）

除了遵循 `clerk-setup`，请在会话中运行其他 Clerk 命令之前验证 CLI 已认证、链接且健康：

```sh
clerk --version               # 确认二进制文件在 PATH 上
clerk doctor --json           # 结构化健康检查；如果任何内容失败，则退出 1
```

**始终首先运行 `clerk doctor --json`。** 它捕获常见的设置失败（未登录、项目未链接、缺失密钥、CLI 版本过时），以便后续命令不会因令人困惑的错误而失败。在代理模式下，它还包括 `Host 执行` 检查，当 Clerk 的主机侧配置/凭证目录不可写时会发出警告，这是当前调用可能是沙盒的典型信号。

每个结果都有 `name`、`status`（`pass`/`warn`/`fail`）、`message`、可选的 `detail`、可选的 `remedy`（如何修复它）和可选的 `fix`（可自动修复问题的标签）。解析它并采取行动，或向用户展示它。如果 `Host 执行` 警告，在信任同一沙盒运行中任何认证/链接/环境/API 失败之前，在主机上重新运行该命令。每当后续命令开始行为异常时，重新运行 `clerk doctor --json`。

如果 `clerk --version` 报告比此技能涵盖的新 CLI，请首先信任 `clerk <命令> --help` 并从其来源刷新此技能包。反之亦然：`--accountless` 和 `accountless` JSON 键从 CLI 3.3+ 开始提供——在较旧的 CLI 上，使用 `--keyless` 别名或升级。

## 无账户设置

`clerk init` 不需要 `clerk auth login`：在具有无账户支持的框架上，未认证的引导（没有 `--app`），或未认证的代理运行（没有 `--app` 或现有项目链接），会生成一个未认领的无账户应用，带有临时开发密钥——没有账户，没有浏览器，没有标志。（一个已登出的人类在*现有*项目中重新运行它时会得到登录流程——`--accountless` 强制临时密钥路径。）大多数实例命令然后仅在该密钥上工作。

在使用它之前需要了解的两件事：无账户路径遵循本地任何 `sk_` 密钥——包括 `sk_live_`（无论是否已认领）——因此当您指一个真实应用时，请传递 `--app <id>`；`clerk open` 返回一个凭证等效的声明 URL，永远不会安全地粘贴到日志或 PR 中。

需要账户的命令以及完整规则：[auth.md](references/auth.md#accountless-operating-without-an-account)。

## 心智模型

| 层级                           | 它的作用                                                                                 | 命令                                                       |
| ------------------------------ | -------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| **会话 / 项目**               | 认证、将仓库链接到 Clerk 应用、拉取环境密钥                                              | `auth login`, `link`, `unlink`, `whoami`, `env pull`, `doctor` |
| **实例配置**                 | 管理特定实例的配置（社交提供者、会话生命周期等）                                           | `config pull`, `config schema`, `config patch`, `config put`   |
| **后端 API（默认）**       | 运行时数据：用户、组织、会话、邀请、JWT 模板、Webhooks                                      | `clerk api <path>`                                             |
| **平台 API (`--platform`)** | 账户级：应用、实例、计费                                              | `clerk api --platform <path>`                                  |
| **前端 API (`--fapi`)**     | 实例的公开面向用户的 API（clerk-js 调用的内容）                                        | `clerk api --fapi <path>`                                      |

一个项目通过 `clerk link` 链接到应用。一旦链接，大多数命令会自动从仓库的 git 远程解析目标应用和开发实例。要针对其他内容，请传递 `--app <id>` 和/或 `--instance dev|prod|<instance_id>`。有关完整解析顺序，请参阅 [references/auth.md](references/auth.md)。

## 发现端点 - 不要记忆它们

CLI 随附 Clerk OpenAPI 目录。始终动态发现端点而不是猜测路径：

```sh
clerk api ls                  # 列出所有后端 API 端点
clerk api ls users            # 通过关键字过滤（匹配路径、摘要、标签、operationId）
clerk api ls --platform apps  # 列出平台 API 端点
```

在运行 `clerk api <path>` 之前使用它。如果您看不到预期的端点，它可能没有被公开。

## `clerk api` 命令（工作horse）

`clerk api` 执行认证的 HTTP 调用。它会自动解析密钥，自动从存在 body 中检测方法，支持 stdin，并可以使用 `--dry-run` 预览变更。

```sh
# GET 请求
clerk api /users                                  # 列出用户
clerk api /users/user_abc123                      # 获取一个
clerk api /users?limit=5&order_by=-created_at     # 查询参数可以内联工作

# 变更请求
clerk api /users -d '{"email_address":["a@b.co"]}'          # POST（从 body 自动检测）
clerk api /users/user_abc123 -X PATCH -d '{"first_name":"A"}'
clerk api /users/user_abc123 -X DELETE

# 从文件或 stdin 获取 body
clerk api /users --file payload.json
cat payload.json | clerk api /users

# 始终首先预览变更
clerk api /users/user_abc123 -X DELETE --dry-run
clerk api /users/user_abc123 -X DELETE --yes      # 确认一次后跳过确认

# 针对特定应用/实例
clerk api /users --app app_abc123 --instance prod

# 调试时包含响应头
clerk api /users --include

# 平台 API（账户级，不是租户数据）
clerk api /v1/platform/applications --platform

# 前端 API（实例的公开面向用户的 API——clerk-js 调用的内容。
# 未认证；--fapi 和 --platform 不能组合，--secret-key 被忽略）
clerk api --fapi /environment
```

在人类模式下，没有参数的 `clerk api` 会打开一个交互式请求构建器；在代理模式下它会打印使用指南并退出 `0`——从脚本中始终显式传递端点（或 `ls`）。

对于实例配置，请优先使用专用的 `clerk config ...` 命令而不是原始平台 API `/config` 路径。它们比原始端点形式更干净地处理 dry-run、diffing 和确认。

**始终在真正运行之前进行 `--dry-run`。** 然后重新运行而不带 `--dry-run`（如果您确定，请添加 `--yes`）。在代理模式下，交互式确认被绕过，因此 `--dry-run` 是破坏性调用的唯一安全网。

**JSON body 必须是有效的 JSON。** CLI 验证并拒绝格式错误的负载。

**端点路径可以带或不带 `/v1/` 前缀**——两者对于后端 API 调用都有效。CLI 会规范化。

有关具体模式：列出/过滤用户、创建组织、模拟会话等，请参阅 [references/recipes.md](references/recipes.md)。

## 检查大型输出（不要淹没您的上下文）

`users list`、`apps list`、`config pull` 和大多数 `clerk api` GET 会返回可能为几 KB 或几 MB 的负载。生产租户通常有数千个用户；实例配置可以深几百个字段。将那些响应读入对话会浪费上下文窗口而没有任何好处。首先将响应保存到文件，然后使用 `jq` 查询您需要的部分：

```sh
# 1. 保存响应。使用 --limit 250 最大化用户列表的页面大小。
clerk users list --json --limit 250 > /tmp/users.json
clerk apps list --json                > /tmp/apps.json
clerk api /users/user_abc123          > /tmp/user.json

# 2. 仅检查您需要的部分。
jq '.data | length'                       /tmp/users.json   # 当前页面大小
jq '.hasMore'                             /tmp/users.json   # 是否有更多页面？
jq '.data[0] | keys'                      /tmp/users.json   # 一次性发现用户形状
jq '.data[] | {id, email_addresses}'      /tmp/users.json   # 投影到几个字段
jq '[.data[] | select(.banned)] | length' /tmp/users.json   # 聚合而不读取行
```

**如果 `jq` 不可用**，回退到 Python 或 Node——两者都可以流式传输文件而不打印整个文件：

```sh
python3 -c 'import json; d=json.load(open("/tmp/users.json")); print(len(d["data"]), d["hasMore"])'
node -e 'const d=require("/tmp/users.json"); console.log(d.data.length, d.hasMore)'
```

仅当您确实需要查看原始结构进行一次性调试时才使用 `cat` / `head` 文件。当逐页遍历时，将每一页写入其自己的文件（例如 `page-${offset}.json`），以便单个页面可以独立检查。

## 核心命令一览

| 命令                       | 用途                                                                                                                                                                                                                                                                                                             | 关键标志                                                                                                                                                                        |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `clerk init`                  | 将 Clerk 框架搭建到项目中。未经身份验证的引导不使用 `--app`，或者未经身份验证的代理运行不使用 `--app` 或现有链接，默认会写入临时开发密钥——无需登录（参见 [无身份验证设置](#accountless-setup)）。`--starter` 仅支持为 Next.js、React Router、Astro、Nuxt、TanStack Start、React、Vue 和 JavaScript 搭建引导。`--accountless` 与 `--app`/`--login` 一起使用，以及 `--template`/`--fresh` 与 `--login` 一起使用，在搭建任何内容之前都是使用错误。`--template`/`--fresh` 在一个 *解析* 为真实应用的运行中（包括仅在登录时）仅在策略解析后才会报错——因此一个 starter 运行会保留搭建的项目。 | `--framework`, `--pm`, `--name`（与 `--starter` 一起使用），`--app`, `--starter`, `--accountless`, `--login`, `--template`, `--fresh`, `-y`, `--no-skills`                                   |
| `clerk auth login`            | OAuth 浏览器登录（存储令牌）。对于引导或无身份验证实例配置不是必需的。代理模式：如果已经登录则无操作。没有存储的会话时它仍然会打开一个浏览器并绑定本地回调，因此它不是无人值守的；对于无头流程，请优先使用 `CLERK_PLATFORM_API_KEY`。别名：`signup`, `signin`, `sign-in`。顶层快捷方式：`clerk login`。 | -                                                                                                                                                                                |
| `clerk auth logout`           | 清除存储的凭证。别名：`signout`, `sign-out`。顶层快捷方式：`clerk logout`。                                                                                                                                                                                                                       | -                                                                                                                                                                                |
| `clerk whoami`                | 打印登录的邮箱。                                                                                                                                                                                                                                                                                          | -                                                                                                                                                                                |
| `clerk link` / `clerk unlink` | 将此仓库链接到 Clerk 应用，或解除链接。`unlink` 在代理模式下需要 `--yes`。                                                                                                                                                                                                                         | (参见 `--help`)                                                                                                                                                                   |
| `clerk env pull`              | 将可发布 + 秘密密钥写入框架的 env 文件（合并，而不是覆盖）。解析 `.env.development.local` → 框架首选文件 → `.env.local`；使用 `--file` 覆盖。                                                                                                                              | (参见 `--help`)                                                                                                                                                                   |
| `clerk config {pull,schema}`  | 获取实例配置 JSON，或其 JSON Schema。                                                                                                                                                                                                                                                                     | (参见 `--help`)                                                                                                                                                                   |
| `clerk config patch`          | 实例配置的部分更新（PATCH）。传递 `--destructive` 以实际删除受补丁影响的子资源，而不是将它们重置为默认值。                                                                                                                                                       | `--app`, `--instance`, `--file`, `--json`, `--dry-run`, `--yes`, `--destructive`                                                                                                 |
| `clerk config put`            | 实例配置的完全替换（PUT）。传递 `--destructive` 以实际删除已删除的子资源，而不是将它们重置为默认值。                                                                                                                                                                    | `--app`, `--instance`, `--file`, `--json`, `--dry-run`, `--yes`, `--destructive`                                                                                                 |
| `clerk apps {list,create}`    | 列出或创建 Clerk 应用。在代理模式下默认为 JSON。                                                                                                                                                                                                                                                  | (参见 `--help`)                                                                                                                                                                   |
| `clerk users`（无子命令）     | 在人类模式下 `users` 操作的交互式选择器；在代理模式下打印操作列表并退出 `2`。始终从代理传递明确的子命令。                                                                                                                                                           | `--app`, `--instance`, `--secret-key`                                                                                                                                            |
| `clerk users list`            | 通过精选的 BAPI 标志列出用户。JSON 输出（在管道或代理模式下默认）是 `{data, hasMore}`，以便调用者可以分页而无需 `/users/count`。`--limit` 默认为 100（最大 250）。                                                                                                                      | `--limit`, `--offset`, `--query`, `--email-address`, `--phone-number`, `--username`, `--user-id`, `--external-id`, `--order-by`, `--json`, `--app`, `--instance`, `--secret-key` |
| `clerk users create`          | 从精选标志或原始 BAPI 身体创建用户。**任何模式下都没有确认提示**——它会立即写入。`--yes` 被接受但没有效果。`--dry-run` 是唯一的保险；先用它预览。                                                                                                                                                                                                                            | `--email`, `--phone`, `--username`, `--password`, `--first-name`, `--last-name`, `--external-id`, `-d, --data`, `--file`, `--dry-run`, `--yes`, `--json`                         |
| `clerk users open [user-id]`  | 打开用户的仪表板页面。代理模式下需要 `user-id` 并打印 JSON 描述符而不是启动浏览器。                                                                                                                                                                                            | (参见 `--help`)                                                                                                                                                                   |
| `clerk impersonate [user]`    | 以用户身份登录进行调试：创建一个短期演员令牌并打印登录 URL。别名：`clerk imp`。需要 `clerk auth login`（没有 `--secret-key`-仅绕过）——每个令牌都标记为 `cli:<email>` 以便可审计。`[user]` 接受 `user_...` ID、确切的邮箱或模糊搜索词。在生产环境中它会绕过用户的 MFA，并且可能会计入模拟配额——先与用户确认。 | `--print`, `--open`, `--yes`, `--expires-in <seconds>`（默认 3600），`--actor <context>`，`--app`, `--instance`                                                                |
| `clerk impersonate revoke <actor-token-id>` | 撤销一个待处理的演员令牌。令牌 `id` 仅在创建时打印（后端 API 没有演员令牌列表端点），所以当时捕获它。                                                                                                                                                      | `--app`, `--instance`                                                                                                                                                            |
| `clerk open [subpath]`        | 在浏览器中打开链接应用的仪表板。代理模式：打印 JSON 描述符而不是打开。                                                                                                                                                                                                              | (参见 `--help`)                                                                                                                                                                   |
| `clerk deploy`                | 人类模式生产部署向导。代理模式：发出只读 JSON 交接，并告诉代理是否要询问人类运行向导、等待配置、完成 OAuth 或不做任何事。                                                                                                                 | `--mode agent`, `--mode human`, `--verbose`                                                                                                                                      |
| `clerk deploy status`         | 只读部署验证。触发 DNS 检查，报告聚合域名和 OAuth 准备情况，并且仅在完成时退出 `0`。代理模式默认执行一次快速检查；传递 `--wait` 以保持等待。                                                                                                     | `--mode agent`, `--wait`, `--verbose`                                                                                                                                            |
| `clerk webhooks listen`       | 第一方本地 webhook 隧道（类似于 `stripe listen`）：打开一个 Svix 中继收件箱 URL 并将每个交付转发到您的本地处理程序。无认证、无链接项目、无 Clerk API。完整流程在 [references/recipes.md](references/recipes.md#webhooks-local-testing) 中。                                                 | `--forward-to <url>`（必需），`--token <c_token>`，`-H, --header <k:v>`（可重复），`--json`（NDJSON）                                                                       |
| `clerk webhooks token`        | 矿一个中继令牌（`c_` + 10 基62字符）以跨机器固定稳定的 `listen` 收件箱 URL：`clerk webhooks listen --token "$(clerk webhooks token)" --forward-to ...`。                                                                                                                                          | `--json`                                                                                                                                                                         |
| `clerk webhooks verify`       | 离线验证 webhook 签名（纯本地 HMAC，无认证）：从一个保存的 `listen` 事件行（`--delivery @event.json`）或从四个原始值中。                                                                                                                                                             | `--secret <whsec>`（必需），`--delivery @file`, `--payload @file`, `--id`, `--timestamp`, `--signature`, `--json`                                                             |
| `clerk enable orgs` / `clerk disable orgs` | 在实例上切换 Organizations。有关组织功能、组件和 API 使用，请参阅 `clerk-orgs` 技能。                                                                                                                                                                                         | `--force-selection`, `--auto-create`, `--max-members <n>`，`--domains`, `--dry-run`, `--yes`, `--app`, `--instance`                                                              |
| `clerk enable billing` / `clerk disable billing` | 为用户和/或组织切换计费（默认为两者）。有关计划、定价组件和授权，请参阅 `clerk-billing` 技能。                                                                                                                                                         | `--for <orgs\|users>`，`--dry-run`, `--yes`, `--no-skills`（仅启用），`--app`, `--instance`                                                                                  |
| `clerk doctor`                | 健康检查（CLI 版本，登录、链接、env、配置、完成；在代理模式下还包括主机执行探测）。                                                                                                                                                                                                          | `--json`, `--spotlight`, `--verbose`, `--fix`                                                                                                                                    |
| `clerk api [path]`            | 经过身份验证的 HTTP 到后端/平台 API。                                                                                                                                                                                                                                                                         | `-X`, `-d`, `--file`, `--dry-run`, `--yes`, `--include`, `--app`, `--secret-key`, `--instance`, `--platform`                                                                     |
| `clerk api ls [filter]`       | 从捆绑的 OpenAPI 目录发现端点。                                                                                                                                                                                                                                                                | (参见 `--help`)                                                                                                                                                                   |
| `clerk completion [shell]`    | 打印一个 shell 完成脚本 (`bash`, `zsh`, `fish`, `powershell`)。                                                                                                                                                                                                                                              | -                                                                                                                                                                                |
| `clerk update`                | 将 CLI 更新到最新版本。                                                                                                                                                                                                                                                                               | `--channel`, `-y`, `--all`                                                                                                                                                       |

**`clerk <command> --help` 是标志的权威来源。** 这个表格只是一个提示，不是规范。在运行不熟悉的命令或标志组合之前，在每个会话中运行一次 `clerk <command> --help`。每个命令也在源代码中定义了 `setExamples([...])`，`--help` 会将其渲染为可复制粘贴的示例块，因此您很少需要猜测语法。

## 代理模式行为（重要）

当标准输出不是 TTY，或者设置了 `--mode agent` / `CLERK_MODE=agent` 时，CLI 会自动检测代理模式。在代理模式下：

- **交互式提示被禁用。** 通常会显示选择器的命令（`link` 没有 `--app`，`unlink` 没有 `--yes`，`users` 没有子命令）会自动解析或退出并显示使用错误。没有参数的 `clerk api` 会打印使用指南并退出 0；显式传递端点（或 `ls`）。在脚本调用中始终显式传递标志 (`--app`, `--yes`)。
- **对主机敏感的操作每次调用都会发出一次沙盒警告。** 主目录 Clerk 状态、密钥链访问、网络 Clerk 调用、浏览器启动和本地主机 OAuth 回调设置会触发上述警告。如果出现该警告，请在信任结果之前在同一主机上重新运行相同命令。
- **如果您的 harness 未能清晰地呈现为代理模式，请强制使用。** 当您希望 CLI 的非交互式行为和沙盒警告路径确定性地应用时，使用 `--mode agent` 或 `CLERK_MODE=agent`。
- **`link` 支持确定的代理流程。** 在代理模式下，`clerk link --app <id>` 会直接链接。没有 `--app`，CLI 会首先尝试静默密钥自动链接；如果它无法明确确定应用，它会退出并告诉您传递 `--app`。
- **对于 `init`，请遵循 `clerk-setup`。** 它拥有框架支持、无账户、应用链接、迁移和登录顺序指导，因此设置说明有一个权威来源。
- **`--fresh` 是破坏性的。** 它会替换临时应用并覆盖环境键和 `.clerk/keyless.json` 踪迹，没有任何提示，会遗弃之前的应用及其用户。切勿仅为了重新运行 `init` 而传递它。
- **在代理模式下，`unlink` 需要 `--yes`。** 它依赖于 `isAgent() && !options.yes`，如果没有它，会退出并显示使用错误。这是例外，不是模式——见下一个要点。
- **只有 `unlink` 实际上需要 `--yes`。** 其他所有确认门都是写成 `isHuman() && !options.yes`，因此代理模式会直接跳过它：变异会没有任何提示和错误地执行。传递 `--yes` 是无害的但不会改变任何内容。不要将其视为安全门——`--dry-run` 才是真正的。
- **`impersonate` 在代理模式下需要 `[user]` 位置参数。** 如果搜索词匹配多个用户，它会退出 `2` 并列出候选用户 ID——使用特定的 `user_...` ID 重试。输出是一个 JSON 对象 (`{url, id, userId, actor, ...}`)；将 `url` 显示给用户并捕获 `id`——它是记录撤销句柄的唯一机会。
- **`webhooks listen` 是长时间运行的。** 在后台运行它。在代理模式（或使用 `--json`）下，它会发出 NDJSON：一条 `ready` 行 (`{type:"ready", relay_url, forward_to}`)，然后每条交付一条 `event` 行——每条事件行都可以反馈给 `clerk webhooks verify --delivery`。
- **`doctor --fix` 被忽略。** 解析 `doctor --json` 输出的 `remedy` 字段并自行操作。
- **`apps list` 和 `apps create` 在管道时默认为 JSON**。  
- **`users` 在管道时默认为 JSON，与 `apps` 类似。** `clerk users list` 和 `clerk users create` 在代理模式下发出 JSON。没有子命令的 `clerk users` 在代理模式下是使用错误 - 显式传递 `list`、`create` 或 `open`。`clerk users open` 在代理模式下需要 `user-id` 位置参数，并打印 JSON 描述符而不是启动浏览器。
- **`deploy` 有一个代理交接和一个验证门。** 在代理模式下，裸 `clerk deploy` 是只读的，并发出 JSON 交接。它永远不会驱动交互式向导。不要告诉 Claude 或其他代理运行 `! clerk deploy`，因为向导需要交互式 stdin 提示。当需要时，请要求人类在一个新终端窗口中运行 `clerk deploy`，然后运行 `clerk deploy status --mode agent` 来验证完成。见 [references/agent-mode.md](references/agent-mode.md#deploy-handoff-and-verification)。
- **`--input-json <json|@file|->`** 会在任何命令上展开 JSON 为标志（例如 `clerk init --input-json '{"framework":"next","yes":true}'`）。Stdin 需要显式 `-` 标记 (`echo '{"yes":true}' | clerk init --input-json -`）；裸管道的 stdin 不会被自动检测，因此 shell 循环和自读命令 (`cat body.json | clerk api …`) 保持不变。在叶子子命令之后放置 `--input-json`。完整规则在 [references/agent-mode.md](references/agent-mode.md#passing-options-as-json---input-json)。

完整矩阵和沙盒详细信息在 [references/agent-mode.md](references/agent-mode.md)。

## 输出格式和错误

- **JSON 输出：** `apps list` 和 `doctor` 上的 `--json`。对于 `clerk api`，响应正文是原始 API JSON，因此可以自由地将其管道到 `jq`。
- **退出代码：** `0` 成功，`1` 运行时错误，`2` 使用/验证错误。`doctor` 如果任何检查失败则返回 `1`。
- **错误格式：** 用户界面错误会打印一行到 stderr 并设置非零退出代码。使用 `--verbose` 在调试时获取堆栈跟踪。

## 自主使用的安全规则

1. **在行动前发现：** `clerk api ls <keyword>` 之前 `clerk api <path>`。
2. **预览变异：** 每个的 `config patch`、`config put`、`api -X POST/PATCH/PUT/DELETE` 上使用 `--dry-run`。
3. **明确在生产环境中目标：** 传递 `--instance prod` 而不是依赖默认值，并在任何生产变异之前确认用户。
4. **永远不要提交密钥：** `env pull` 会写入 `.env.local`（应该被 git 忽略）。不要将密钥粘贴到代码或聊天中。
5. **使用 `doctor --json`** 在假设 CLI 出现故障之前进行诊断。

## 参考

- [references/auth.md](references/auth.md) - 认证流程、密钥解析顺序、主机与沙盒行为、`--app`/`--instance` 目标、后端与平台 API。
- [references/recipes.md](references/recipes.md) - 常见 Clerk 任务的复制粘贴式配方。
- [references/agent-mode.md](references/agent-mode.md) - 代理模式行为矩阵、沙盒警告语义、退出代码、错误格式。
