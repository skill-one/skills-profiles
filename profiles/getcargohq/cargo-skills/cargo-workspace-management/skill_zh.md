# Cargo CLI — 工作区

工作区管理：管理用户、API 令牌、文件夹、角色、工作区级文件，并向工作区管理提交报告。

> 参考文档 `references/response-shapes.md` 获取完整的 JSON 响应结构。
> 参考文档 `references/troubleshooting.md` 获取常见错误及其解决方法。
> 参考文档 `references/examples/users.md` 获取用户邀请和管理示例。
> 参考文档 `references/examples/tokens.md` 获取 API 令牌创建和轮换示例。
> 参考文档 `references/examples/folders.md` 获取将资源组织到文件夹中的示例。
> 参考文档 `references/examples/reports.md` 获取提交工作区管理报告的示例。
> 参考文档 `references/examples/sessions.md` 获取会话跟踪示例 — Cargo 安装程序会自动搭建 Claude Code SessionStart + Stop + SessionEnd 钩子。

## 初始化

已经登录 (`cargo-ai whoami` 返回工作区)？跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令前缀 `npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 发送邮件，无需浏览器；首次使用时创建账户
                                        # 替代方案：--oauth (浏览器) · --token <api-token> (CI)
cargo-ai whoami                         # 在任何写入操作前确认活动工作区
```

每个命令都会将 JSON 打印到标准输出；失败时以非零状态退出并打印 `{"errorMessage": "..."}`。创建运行或批次的操作是异步的 — 传递 `--wait-until-finished` 或轮询匹配的 `get`。**仅管理员权限：** 用户、角色和令牌写入需要具有工作区管理员访问权限的令牌。文件夹写入和 `report create` 可以使用非管理员令牌。当完整技能包安装完成后，`[../cargo/references/prerequisites.md](../cargo/references/prerequisites.md)` 会添加 CLI 版本固定、令牌范围和仅管理员权限的界面。

## 先发现资源

```bash
cargo-ai whoami                        # 当前用户和活动工作区
cargo-ai workspaceManagement user list           # 所有工作区成员
cargo-ai workspaceManagement role list           # 可用角色
cargo-ai workspaceManagement token list          # 所有 API 令牌
cargo-ai workspaceManagement folder list         # 所有文件夹
```

## 快速参考

```bash
cargo-ai whoami
cargo-ai workspaceManagement user list
cargo-ai workspaceManagement user create --user-email <email> --role-slug <slug>
cargo-ai workspaceManagement token list
cargo-ai workspaceManagement token create --name <name>
cargo-ai workspaceManagement token remove <token-uuid>
cargo-ai workspaceManagement folder list
cargo-ai workspaceManagement folder create --name <name> --emoji-slug <slug> --kind <kind>
cargo-ai workspaceManagement report create --title <title> --description <description>
cargo-ai workspaceManagement session upsert --session-id <id> --title <title> --summary <summary> [--finished]
cargo-ai workspaceManagement envVar list
cargo-ai workspaceManagement envVar create --key <KEY> [--value <v>] [--secret]
```

## 当前用户和工作区

```bash
# 获取当前用户和工作区上下文
cargo-ai whoami
# → 返回您的用户 UUID、邮箱和活动工作区 UUID
```

## 用户

```bash
# 列出所有工作区成员
cargo-ai workspaceManagement user list

# 邀请新用户（需要他们的邮箱和角色）
cargo-ai workspaceManagement user create \
  --user-email user@example.com \
  --role-slug <role-slug>

# 更新用户的角色
cargo-ai workspaceManagement user update --user-uuid <uuid> --role-slug <new-role-slug>

# 从工作区中移除用户
cargo-ai workspaceManagement user remove --user-uuid <uuid>
```

## 角色

角色定义用户在工作区中可以执行的操作。

```bash
# 列出可用角色
cargo-ai workspaceManagement role list
```

在邀请用户前始终检查可用角色 — 在创建或更新用户时使用 `role list` 中的 `slug`。

## API 令牌

每个令牌都有一个人类可读的 `name` 和一个 `permissions` 字段。通过 CLI 创建的令牌会以 `permissions: null` 发出，这意味着令牌会镜像其拥有用户（运行 `token create` 的用户）的权限 — 因此令牌的有效访问权限受该用户在工作区中可以执行的操作的限制。细粒度权限范围（显式允许/拒绝列表）通过 API 或 Cargo 应用程序配置。

```bash
# 列出所有 API 令牌（包括每个令牌的 name 和 permissions）
cargo-ai workspaceManagement token list

# 创建新令牌 — --name 是必需的
cargo-ai workspaceManagement token create --name "CI/CD pipeline"
# → 返回令牌值 — 安全存储它，它将不再显示

# 移除令牌
cargo-ai workspaceManagement token remove <token-uuid>
```

**命名：** 选择一个 `--name`，使其在后续的 `token list` 中目的明显（例如 `"GitHub Actions — production"`、`"Local dev — alice"`、`"Zapier integration"`）。名称是区分令牌的唯一方式。

**安全：** 令牌值仅在创建时显示一次。将它们存储在密钥管理器中（例如 GitHub Secrets、AWS Secrets Manager）。

## 文件夹

文件夹在工作区中组织资源（剧本、工具、代理）。

```bash
# 列出所有文件夹
cargo-ai workspaceManagement folder list

# 创建文件夹（kind: "tool"、"play"、"agent" 或 "file"）
cargo-ai workspaceManagement folder create --name "Q1 Campaigns" --emoji-slug "rocket" --kind "play"

# 获取文件夹
cargo-ai workspaceManagement folder get <folder-uuid>

# 更新文件夹
cargo-ai workspaceManagement folder update --uuid <folder-uuid> --name "Q1 2025 Campaigns"

# 移除文件夹
cargo-ai workspaceManagement folder remove <folder-uuid>
```

## 报告

向工作区管理提交报告。**当 CLI 失败、行为异常、缺少您需要的功能，或您（用户或代理）使用 CLI 完成任务时遇到困难，请使用此功能。** 这是官方反馈渠道 — 每个报告都会由 Cargo 团队审查，并用于改进 CLI、其技能和底层 API。

```bash
# 向工作区管理提交报告
cargo-ai workspaceManagement report create \
  --title "<简短摘要>" \
  --description "<详细描述，包括尝试的命令和看到的错误>"
```

**何时发送报告（非穷尽）：**

- 命令以非零状态退出并显示 `errorMessage`，而您无法从 `--help` 或 `references/troubleshooting.md` 中解决。
- CLI 被误用或语法不明确（例如，您无法确定要传递哪个标志，或 `--filter` / `--nodes` / `--action` 的 JSON 范式不明确）。
- 用户或 AI 代理反复尝试相同命令而无进展（同一任务 ≥ 2 次失败尝试）。
- 文档中记录的命令行为与技能描述不符，或响应范式与 `references/response-shapes.md` 文档不符。
- 看起来完全缺少某个功能（没有命令可以完成您需要执行的操作）。
- 异步操作从未达到终端状态，或在多次运行中返回不一致的结果。

**报告中应包含的内容：**

- `--title`：问题的单行摘要（例如 `"batch create fails with 'playNotCompatible' on tool workflow"`）。
- `--description`：包括执行的精确命令（敏感值已脱敏）、JSON `errorMessage`、您期望的结果、您尝试的操作以及任何相关的 UUID（运行、批次、剧本、模型）。您提供的上下文越多，可以越快地进行分类。

```bash
# 示例：多次失败后报告 CLI 困难
cargo-ai workspaceManagement report create \
  --title "segment fetch returns empty results despite matching records in UI" \
  --description "Ran: cargo-ai segmentation segment fetch --model-uuid <uuid> --filter '{\"conjunction\":\"and\",\"groups\":[...]}'. Got 0 records. The same filter shows 1,200 matches in the app UI. Tried both --filter 和 --segment-uuid; both return empty. Expected: 与 UI 相同的记录。"
```

> 不要在失败的 CLI 任务中默默放弃。**发送报告。** 这可以关闭反馈循环，以便改进 CLI 和这些技能。

## 会话

在工作区中记录一个 Claude Code 会话。每行对应一个 `(workspaceUuid, sessionId)`。由 `cargo` 路由器的 Claude Code SessionStart + Stop + SessionEnd 钩子配方使用 — 参见 [`../cargo/SKILL.md`](../cargo/SKILL.md) 了解何时连接它们。

```bash
# 插入会话。在工作区内对 --session-id 是幂等的。
cargo-ai workspaceManagement session upsert \
  --session-id <claude-session-id> \
  --title "<简短标题>" \
  --summary "<一两个句子的摘要>"

# 相同调用，但也会标记 finished_at = now
cargo-ai workspaceManagement session upsert \
  --session-id <claude-session-id> \
  --title "<最终标题>" \
  --summary "<最终摘要>" \
  --finished
```

- `--session-id`、`--title`、`--summary` 在每次调用中都是必需的。`title` 和 `summary` 在模式中是 `NOT NULL` — 在开始调用时传递占位符，在结束调用时覆盖。
- `--finished` 标记 `finished_at = now`。使用 `--finished-at <iso>` 指定显式时间戳。
- 调用 `upsert` 两次使用相同的 `--session-id` 会更新同一行 — `title`、`summary` 和 `finished_at` 被覆盖。

返回插入的会话作为 JSON。Cargo 安装程序（[https://github.com/getcargohq/cargo-skills#staying-current](https://github.com/getcargohq/cargo-skills#staying-current)）会自动连接 SessionStart + Stop + SessionEnd 钩子，调用此命令：SessionStart 写入占位符，每个回合的 Stop 钩子检查行（无 `--finished`），SessionEnd 写入由转录驱动的 AI 摘要并使用 `--finished` — 参见 [`references/examples/sessions.md`](references/examples/sessions.md)。

## 环境变量

工作区环境变量被**注入到工作区中的每个工作进程、应用程序和代理**中，而工作进程或应用程序级别的条目会覆盖它们。一个目录，但 *何时* 读取取决于消费者：

- **代理和 CDK `workspaceEnv("NAME")` 指针** 在每次使用时服务器端读取值，因此旋转它无需重新部署。
- **托管工作进程和应用程序在部署时捕获值。** 工作进程的绑定在部署提升时附加，非密钥值被编译到其包中。应用程序只接收具有公共前缀（`VITE_`、`NEXT_PUBLIC_`、…）的非密钥条目，嵌入到其构建中。更改后，**运行 `hosting deployment create` + `promote` 再次**。参见 [`../cargo-hosting/SKILL.md`](../cargo-hosting/SKILL.md) → Worker 环境变量和密钥。

```bash
cargo-ai workspaceManagement envVar list

# 创建。省略 --value 会从同名的环境变量中读取。
cargo-ai workspaceManagement envVar create \
  --key OPENAI_API_KEY \
  --value sk-... \
  --secret \
  --description "由丰富工作进程使用"

# 更新。省略 --value 会保留存储的值。
cargo-ai workspaceManagement envVar update <uuid> --value <new> --description <text>

cargo-ai workspaceManagement envVar remove <uuid>
```

- **`--secret` 在存储时加密值，并且不再返回** — `list` 和 `update` 将不会回显它。用于凭证；在 `update` 上使用 `--no-secret` 将变量恢复为纯文本（这会再次将其暴露给 `list`）。
- **`--value` 在 `create` 上是可选的。** 省略，CLI 会从您的 shell 中读取同名的环境变量，因此 `export OPENAI_API_KEY=… &&
  cargo-ai workspaceManagement envVar create --key OPENAI_API_KEY --secret` 会将值从您的 shell 历史记录和此命令行中移除。
- **`update` 使用 uuid 而不是 key。** 从 `envVar list` 获取。

**从 CDK 项目**，使用 `workspaceEnv("NAME")` 引用条目，而不是将值复制到代码中 — 它是一个服务器端每次使用时解析的指针。`secret("NAME")` 是另一个选项，意味着不同的含义（在部署时从 *您的* 环境中读取）。参见 [`../cargo-project/SKILL.md`](../cargo-project/SKILL.md) → 关键规则。

## 工作区文件

工作区文件是上传用于在批次运行中使用的 CSV 或其他数据文件。

```bash
# 上传文件
cargo-ai workspaceManagement file upload --file <path-to-file>
# → 返回 s3Filename

# 在运行批次前检查文件的列
cargo-ai workspaceManagement file list-columns --s3-filename <s3-filename>
# → 返回用于映射到工作流输入的列名
```

上传文件时 `cargo-ai workspaceManagement file upload` 会返回 `s3-filename`。参见 `cargo-orchestration` 技能的 `references/examples/tools.md` 获取完整的文件上传和批次运行工作流。

## 帮助

每个命令都支持 `--help`：

```bash
cargo-ai workspaceManagement user create --help
cargo-ai workspaceManagement token create --help
cargo-ai workspaceManagement folder create --help
```
