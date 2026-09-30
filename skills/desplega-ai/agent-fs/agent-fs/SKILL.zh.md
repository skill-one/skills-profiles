---
name: agent-fs
description: 当用户希望存储、检索、搜索或管理 agent-fs 中的文件时使用——agent-fs 是一个以 S3 为后端的、以代理优先的文件系统。触发条件包括："保存到 agent-fs"、"查找该文件"、"存储此文档"、"搜索 agent-fs"、"列出我的文件"、"显示版本历史"、"还原文件"、"设置 agent-fs"、"获取签名 URL"、"分享此文件"、"分享链接"、"公开链接"、"一次性链接"、"撤销分享链接"、"管理成员"、"邀请用户"、"列出成员"、"移除成员"、"更新角色"、"重置 API 密钥"、"旋转 API 密钥"、"丢失我的 API 密钥"、"代理文件持久化"、"共享代理文件系统"或任何提及 agent-fs 命令行的内容。当用户需要管理驱动器、管理组织/驱动器成员、生成预签名 URL、检查近期活动或在存储的文件中使用语义搜索时，也使用此技能。当用户希望对存储的数据文件运行 SQL（例如："查询这个 csv"、"对我的文件运行 SQL"、"duckdb"、"聚合这个 parquet 文件"、"查询这个 sqlite 数据库"、"连接这些电子表格"）时，也使用此技能。当用户希望将 agent-fs 挂载或卸载为 Linux FUSE 文件系统（例如："挂载 agent-fs"、"fuse 挂载"、"fuse"、"远程挂载"、"沙盒挂载"、"将驱动器作为文件暴露"、"在我的 agent-fs 文件上使用 cat/grep/mv"、"卸载驱动器"、"挂载远程驱动器"、"从 sprite 挂载"、"从 e2b 挂载"、"从 hetzner 挂载"）时，也使用此技能。当用户希望将 agent-fs 作为 just-bash 文件系统使用时，也使用此技能。当用户希望在不使用 Docker 或 S3 的情况下设置 agent-fs（例如："本地文件系统后端"、"文件系统存储"、"无 docker"、"onboard --filesystem"、"将文件存储在磁盘上"）时，也使用此技能。如果用户在任何上下文中提及 agent-fs，请始终参考此技能。
---

# agent-fs 命令行界面

agent-fs 是一个以代理为中心的文件系统，具有完整版本控制、全文搜索（FTS5）和语义搜索功能。它提供了一个输出 JSON 的命令行界面，非常适合代理工作流程。文件按组织内的驱动器进行组织。

## 存储后端

agent-fs 将文件字节存储在可插拔的存储后端中。持久化值——版本历史记录、评论和搜索——存储在 SQLite 中，并且在每个后端上工作方式相同。

| 后端 | 设置 | 版本控制级别 | `signed-url` |
|------|------|--------------|--------------|
| **S3 / MinIO**（默认） | `agent-fs onboard -y`（本地 MinIO，需要 Docker）或 `--s3-*` 标志用于 AWS/R2 等。 | 完整——`revert` + 历史记录 `diff` 通过 S3 对象版本控制 | 真实的预签名 URL（公开，有时间限制） |
| **本地文件系统** | `agent-fs onboard --filesystem`（不需要 Docker，不需要 S3） | 完整——`revert` + 历史记录 `diff` 通过磁盘上的内容寻址 blob | 回退到应用程序内的认证链接（需要登录；不会过期） |

这两个后端都是**完整级别**：每个操作——包括 `revert` 和历史记录 `diff`——都可以正常工作。未来的后端可能是**基本级别**（没有对象版本控制）：在这些后端上，`revert` 和历史记录 `diff` 将不可用，并且会以 `UNSUPPORTED_OPERATION` 错误（HTTP 422）干净地失败，而不是原始存储错误——当前内容、列表、评论和搜索仍然可以正常工作。如果您不确定驱动器使用哪个后端，请在依赖版本控制之前检查后端的功能。

## 快速入门

```bash
# 1. 设置（本地 MinIO —— 需要 Docker）
agent-fs onboard -y

#    ...或者没有任何 Docker/S3 —— 将字节存储在本地文件系统中：
agent-fs onboard --filesystem            # 使用 ~/.agent-fs/storage
agent-fs onboard --filesystem --storage-root /data/agent-fs   # 自定义目录

# 2. 可选地启动守护进程（命令行界面自动检测，即使不启动守护进程也能工作）
agent-fs daemon start

# 3. 开始使用
echo "hello world" | agent-fs write docs/readme.txt -m "初始版本"
agent-fs cat docs/readme.txt
```

对于自定义 S3（AWS、R2 等），请使用标志：`agent-fs onboard --s3-endpoint <url> --s3-bucket <name> --s3-access-key <key> --s3-secret-key <key>`。

本地文件系统后端（`--filesystem`，等同于 `--storage local`）不需要 Docker，也不需要 S3——字节存储在 `--storage-root`（默认 `~/.agent-fs/storage`）下，每个版本都是内容寻址的，因此 `revert` 和历史记录 `diff` 与 S3 上的工作方式相同。

## just-bash 适配器

当 `just-bash` 环境需要通过 agent-fs 读取和写入作为其 `fs` 实现时，请使用 `@desplega.ai/agent-fs-just-bash`。

```ts
import { Bash } from "just-bash";
import { AgentFsFileSystem } from "@desplega.ai/agent-fs-just-bash";

const fs = new AgentFsFileSystem({
  baseUrl: process.env.AGENT_FS_API_URL,
  apiKey: process.env.AGENT_FS_API_KEY,
  orgId: "org_...",
  driveId: "drive_...",
});

const bash = new Bash({ fs, cwd: "/" });
```

适配器使用 `/raw` 进行安全的字节读取/写入，并使用 `/ops` 列出和元数据。空目录由隐藏的 `.agent-fs-dir` 标记表示；符号链接不受支持，会抛出 `EPERM`。

## 基本模式

1. **使用 JSON 进行机器输出**——解析命令行界面输出时传递 `--json`（`download` 不带 `-o` 除外，它将原始字节写入标准输出；`daemon status` 和 `auth register` 打印人类可读文本）。

2. **自动检测**——命令行界面自动检测守护进程是否正在运行。如果正在运行，命令通过 HTTP 发送；否则，它们直接使用嵌入式模式。不需要用户操作。

3. **默认组织/驱动器解析**——没有 `--org`/`--drive` 标志时，命令行界面按顺序解析：标志本身，然后本地配置（`org switch <id>` / `drive switch <id>`，对每台机器都是粘性的），然后 `AGENT_FS_DEFAULT_ORG_ID` / `AGENT_FS_DEFAULT_DRIVE_ID` 环境变量（部署级别的提示，例如代理群集工作容器被配置写入的共享组织），然后账户自己的默认组织/驱动器从 `GET /me`（自动创建的个人组织，除非更改）。如果写入位置出乎意料，请检查 `agent-fs org current` / `agent-fs drive current`（`source` 字段）——没有标志的写入始终写入个人组织/驱动器，除非设置了更早的级别。

4. **标准输入和文件上传**——`write` 接受来自标准输入或 `--file` 的原始字节，以及来自 `--content` 的文本；`append` 接受通过标准输入或 `--content` 的文本：
   ```bash
   # 多行文本的首选方式
   echo "content here" | agent-fs write path/to/file.txt

   # 短内容内联
   agent-fs write path/to/file.txt --content "short text"

   # 二进制安全的上传
   agent-fs write assets/screenshot.png --file ./screenshot.png
   ```

5. **路径**——使用正斜杠分隔，不需要开头斜杠。示例：`docs/notes/meeting.md`

6. **版本消息**——可选但推荐用于可审计性：
   ```bash
   agent-fs write docs/spec.md --content "..." -m "添加了 API 部分"
   ```

7. **乐观并发**——在 `write` 上使用 `--expected-version` 以防止冲突：
   ```bash
   agent-fs write config.json --content '{}' --expected-version 3
   # 如果文件不在版本 3，则失败
   ```

## 命令快速参考

### 文件操作

| 命令 | 用法 | 描述 |
|------|------|------|
| `write` | `agent-fs write <path> [--content <text>] [--file <local-path>] [-m <msg>] [--expected-version <n>]` | 写入文本或二进制字节 |
| `cat` | `agent-fs cat <path> [--offset <n>] [--limit <n>] [--raw]` | 读取文本文件内容 |
| `edit` | `agent-fs edit <path> --old <text> --new <text> [-m <msg>]` | 在文件中查找并替换 |
| `append` | `agent-fs append <path> [--content <text>] [-m <msg>]` | 追加到文件（标准输入或 --content） |
| `tail` | `agent-fs tail <path> [--lines <n>]` | 最后 N 行（默认：20） |
| `ls` | `agent-fs ls [path]` | 列出目录内容（默认为 /） |
| `stat` | `agent-fs stat <path>` | 显示文件元数据（大小、版本、时间戳、当前字节的 `etag`：用于比较以判断内容是否更改） |
| `reveal` | `agent-fs reveal <path>` | 在一次调用中显示一个文件所需的所有信息，以在树中显示该文件：每个祖先的 `ls` 列表（根优先，作为 `listings: [{ path, entries }]`）加上该文件的 `stat`。权限与 `ls` 相同；缺失文件返回 `NOT_FOUND`。对于普通读取，请优先使用 `ls`/`stat`。 |
| `tree` | `agent-fs tree [path] [--depth <n>]` | 递归目录列表 |
| `glob` | `agent-fs glob <pattern> [--path <prefix>]` | 通过模式查找文件（`*.md`，`**/*.md`）跨所有存储页面 |
| `rm` | `agent-fs rm <path>` | 删除文件 |
| `mv` | `agent-fs mv <from> <to> [-m <msg>]` | 移动或重命名文件 |
| `cp` | `agent-fs cp <from> <to>` | 复制文件 |
| `signed-url` | `agent-fs signed-url <path> [--expires-in <seconds>] [--inline]` | 生成下载 URL。在 S3/MinIO 上：预签名 URL（默认 24 小时，最长 7 天，`kind: "presigned"`）。在本地文件系统上：应用程序内的认证链接（`kind: "app"`，需要登录，非过期）。默认情况下 URL 强制下载；`--inline` 使浏览器渲染文件（PDF、图像）。 |
| `share-create` | `agent-fs share-create <path> [--expires-in <seconds>] [--max-views <n>] [--one-off]` | 在 API 主机创建公共 `/share/<token>` 链接：一个只读页面，带有预览（Markdown、文本/代码、图像、PDF、音频、视频）和下载按钮。默认 24 小时，最长 7 天；`--one-off`（等于 `--max-views 1`）使其一次性使用。返回 `{ id, url, sharePath, expiresAt, maxViews }`。 |
| `share-revoke` | `agent-fs share-revoke [<id>] [--token <token-or-url>] [--path <path>]` | 立即终止共享链接。正好一个选择器：`share-create` 的 `id`、令牌/URL 或文件路径（指向该文件的每个链接）。只有创建者或驱动器管理员才能执行。 |
| `download` | `agent-fs download <path> [-o <local-path>]` | 下载原始字节 |

`cat` 是一个分页查看器，不是原始文件读取器：如果没有 `--limit`，它在 TTY 上默认为前 200 行，但在标准输出被管道或重定向时返回**整个文件**（管道/重定向几乎总是意味着“给我所有内容”）。任何时间 `cat` 返回的行数少于请求的行数，`truncated: showing N of M lines (use --limit)` 的注释都会发送到**标准错误**——永远不会发送到标准输出，因此永远不会损坏管道/重定向的输出。默认（非 `--raw`，TTY）视图还会为可读性在每一行前添加行号；该前缀**不是**存储的字节的一部分。对于完整的、字节精确的读取——在解析为 CSV/JSON 之前或任何时间行号或部分读取会损坏数据时——请使用 `agent-fs cat <path> --raw` 或更好的 `agent-fs download <path> -o <file>`。

### 版本控制

| 命令 | 用法 | 描述 |
|------|------|------|
| `log` | `agent-fs log <path> [--limit <n>]` | 显示版本历史记录 |
| `diff` | `agent-fs diff <path> --v1 <n> --v2 <n>` | 版本之间的差异 |
| `revert` | `agent-fs revert <path> --version <n>` | 恢复到以前的版本 |

`log` 适用于每个后端（版本元数据存储在 SQLite 中）。`revert` 和历史记录 `diff`（比较两个存储的版本）需要一个**完整级别**的后端——S3/MinIO 和本地文件系统都符合要求。在没有对象版本控制的基本级别后端上，`revert` 和历史记录 `diff` 会以 `UNSUPPORTED_OPERATION`（HTTP 422）干净地失败；`diff` 然后降级为存储的摘要，而不是完整内容。

### 搜索和发现

| 命令 | 用法 | 描述 |
|------|------|------|
| `grep` | `agent-fs grep <pattern> <path>` | 在文件内容中正则表达式搜索 |
| `fts` | `agent-fs fts <pattern> [--path <prefix>]` | 在活动驱动器中使用 FTS5 查询语法进行全文搜索 |
| `search` | `agent-fs search <query> [--limit <n>]` | 混合搜索（语义 + 关键字，最适合一般查询） |
| `vec-search` | `agent-fs vec-search <query> [--limit <n>]` | 在活动驱动器中不同文件上进行语义搜索 |
| `recent` | `agent-fs recent [path] [--since <duration>] [--limit <n>]` | 最近活动（例如，`--since 24h`） |
| `reindex` | `agent-fs reindex [path]` | 重新索引具有失败/缺失嵌入的文件 |

**何时使用哪个：**
- `grep` — 您知道确切的模式和路径（正则表达式）
- `fts` — 关键字搜索跨所有文件（快速，基于 FTS5）
- `search` — 结合关键字和含义的通用搜索（推荐默认）
- `vec-search` — 纯粹的语义搜索，当您只想获得概念匹配时

搜索使用活动组织和驱动器。检查 `org current` 和 `drive current`，或者传递显式的 `--org` 和 `--drive` 标志。
`glob`、`ls` 和 `tree` 读取每个 S3 列表页面。具有超过 1,000 个对象的驱动器仍然可搜索。
`search` 和 `vec-search` 在活动驱动器中选择语义候选者，并计算不同文件以限制数量。
语义结果需要嵌入。`vec-search` 在没有提供程序时返回一个提示，而 `search` 识别仅关键字的结果。

`fts` 接受原始 FTS5 语法。用 FTS 双引号在 shell 单引号内引用包含标点的术语：

```bash
agent-fs glob '**/*ai-tinkerers*'
agent-fs glob '**/*ai-tinkerers*' --path thoughts/research
agent-fs fts '"ai-tinkerers"'
agent-fs fts 'ai AND tinkerers'
```

在 FTS 引用术语中嵌入引号。转义不会转义 FTS 引号。
文件名模式区分大小写。全文匹配索引的标记，因此这两种模式都不会更正拼写错误。

### SQL 查询（DuckDB）

| 命令 | 用法 | 描述 |
|------|------|------|
| `sql` | `agent-fs sql <query> [-t name=path[:format]]... [--max-rows <n>]` | 在存储的文档上运行 DuckDB SQL |

支持的格式：csv、tsv、parquet、xlsx、json、ndjson/jsonl（每个格式也 `.gz` 除外，parquet/xlsx），sqlite（`.db`/`.sqlite`/`.sqlite3`），和 `.duckdb`。直接通过查询中带引号的驱动器路径引用文件格式文档，或将任何文档绑定到表名 `-t`。SQLite/DuckDB 数据库需要 `-t` 绑定，并将它们的表作为 `<name>.<table>` 暴露。将 `:format` 追加到绑定以查询具有非标准扩展名的文档（例如 `-t logs=/raw/data.txt:csv`）。查询是沙盒化的——没有主机文件系统或网络访问。结果限制在 `--max-rows`（默认 1000，最大 10000）；JSON 输出中的 `truncated: true` 指示存在更多行。

### 评论

| 命令 | 用法 | 描述 |
|------|------|------|
| `comment add` | `agent-fs comment add <path> --body <text> [--line-start <n>] [--line-end <n>] [--quote <text> [--quote-prefix <text>] [--quote-suffix <text>]]` | 向文件添加评论。`--quote` 将其锚定到编辑后 Web 应用程序重新找到的确切文本；前缀/后缀选择正确的出现，当文本重复时 |
| `comment reply` | `agent-fs comment reply <comment-id> --body <text>` | 回复评论 |
| `comment list` | `agent-fs comment list [path]` | 列出评论（带有内联回复） |
| `comment get` | `agent-fs comment get <id>` | 获取带有其回复的评论 |
| `comment update` | `agent-fs comment update <id> --body <text>` | 更新评论（仅作者） |
| `comment delete` | `agent-fs comment delete <id>` | 软删除评论（仅作者） |
| `comment resolve` | `agent-fs comment resolve <id>` | 解决评论 |
| `comment notifications` | `agent-fs comment notifications [--unread] [--limit <n>]` | 列出当前用户在活动驱动器中的评论通知 |
| `comment read` | `agent-fs comment read [ids...] [--all]` | 将选定的通知事件 ID 或所有活动驱动器通知标记为已读 |

### 设置和认证

| 命令 | 用法 | 描述 |
|------|------|------|
| `onboard` | `agent-fs onboard [--local] [--filesystem] [--storage <minio\|local>] [--storage-root <dir>] [-y] [--embeddings <provider>]` | 设置 agent-fs（存储后端 + 数据库 + 用户）。`--filesystem`（或 `--storage local`）使用磁盘后端——不需要 Docker/S3；`--storage-root <dir>` 设置其目录。 |
| `init` | `agent-fs init [--local] [-y]` | `onboard` 的别名 |
| `auth register` | `agent-fs auth register <email>` | 注册新用户 |
| `auth whoami` | `agent-fs auth whoami` | 显示当前用户信息 |
| `auth reset-key` | `agent-fs auth reset-key` | 重置您自己的 API 密钥。旧密钥立即失效。 |

### 成员管理

| 命令 | 用法 | 描述 |
|------|------|------|
| `member list` | `agent-fs member list` | 列出组织成员（使用 `--drive <id>` 列出驱动器成员） |
| `member invite` | `agent-fs member invite <email> --role <role>` | 邀请用户加入组织（查看者/编辑者/管理员） |
| `member update-role` | `agent-fs member update-role <email> --role <role>` | 更新组织角色（使用 `--drive <id>` 更新驱动器角色） |
| `member remove` | `agent-fs member remove <email>` | 从组织中移除（使用 `--drive <id>` 仅用于驱动器） |
| `member reset-key` | `agent-fs member reset-key <email>` | 重置成员的 API 密钥（组织管理员仅限）。旧密钥立即失效。 |

`--drive` 标志是全局选项——将其放在子命令之前：`agent-fs --drive <id> member list`。

成员命令是管理员控制的：组织范围的命令需要组织 `admin`；驱动器范围的命令（`--drive <id>`）需要驱动器 `admin` 或所属组织的管理员，并且驱动器必须属于当前组织。非管理员会收到权限错误；组织/驱动器 ID 在您的成员资格之外会返回“未找到”。

### 驱动器管理

| 命令 | 用法 | 描述 |
|------|------|------|
| `drive list` | `agent-fs drive list` | 列出当前组织中的驱动器 |
| `drive create` | `agent-fs drive create <name>` | 创建新驱动器（需要组织管理员） |
| `drive current` | `agent-fs drive current` | 显示当前驱动器上下文 |
| `drive invite` | `agent-fs drive invite <email> --role <role>` | 邀请用户（查看者/编辑者/管理员） |

Drive 成员资格是明确的：`drive list` 仅显示您是成员的 drive。创建一个 drive 会自动授予您在该 drive 上的管理员成员资格；其他用户必须逐个 drive（或通过组织邀请，后者授予对默认 drive 的访问权限）被邀请。

### 配置与守护进程

| 命令 | 用法 | 描述 |
|------|------|------|
| `config get` | `agent-fs config get <key>` | 获取配置值（点表示法：`s3.bucket`） |
| `config set` | `agent-fs config set <key> <value>` | 设置配置值 |
| `config list` | `agent-fs config list` | 显示所有配置 |
| `config validate` | `agent-fs config validate` | 检查 S3、数据库、认证、嵌入的健康状况 |
| `daemon start` | `agent-fs daemon start` | 启动后台守护进程 |
| `daemon stop` | `agent-fs daemon stop` | 停止守护进程 |
| `daemon status` | `agent-fs daemon status` | 检查守护进程是否正在运行 |

### FUSE 挂载（仅限 Linux）

将所有组织 drive 暴露为 Linux FUSE 文件系统，以便代理可以使用普通的 shell 词汇（`cat`、`grep`、`mv`、`rm`）对 agent-fs 内容进行操作。需要 `/dev/fuse` 和 `SYS_ADMIN` 能力；在 macOS 或基于 gVisor 的沙盒中不可用。

支持两种拓扑结构：
- **本地模式**（默认）：助手通过 Unix 套接字与本地守护进程通信。守护进程必须正在运行并配置了 S3 后端。
- **远程模式** (`--remote`)：助手直接与远程 agent-fs HTTP API 通信。不需要本地守护进程——非常适合沙盒（sprite、E2B、Hetzner VMs、GitHub Actions runners）等可以访问托管 agent-fs 但无法本地运行完整守护进程和 S3 堆栈的环境。

FUSE 写入需要 drive 上的 `editor` 角色或更高权限——在您是 `viewer` 的 drive 上，文件写入挂载是只读的（写入会失败，错误为 `EACCES`；检查 `<mount>/.agent-fs/errors.ndjson` 中的 `PERMISSION_DENIED` 记录）。

| 命令 | 用法 | 描述 |
|------|------|------|
| `mount` | `agent-fs mount <path> [--allow-other] [--foreground]` | 通过本地守护进程在 `<path>` 处挂载 drives（例如 `/mnt/agent-fs/<drive>/`）。 |
| `mount --remote` | `agent-fs mount <path> --remote [--api-url <url>] [--api-key <key>]` | 对远程 agent-fs HTTP API 进行挂载。如果省略标志，则从 `~/.agent-fs/config.json` 或 `AGENT_FS_API_URL`/`AGENT_FS_API_KEY` 环境变量中读取 `apiUrl`/`apiKey`。优先使用环境变量而不是 `--api-key`（后者会在 `ps` 中暴露密钥）。 |
| `umount` | `agent-fs umount <path>` | 卸载 FUSE 挂载点。 |
| `mount status` | `agent-fs mount status` | 显示挂载是否活动以及位置。 |

## 常见工作流

### 存储和检索文档

```bash
# 写入文档（多行通过 stdin）
cat <<'EOF' | agent-fs write reports/q1-summary.md -m "Q1 摘要草稿"
# Q1 摘要
收入环比增长了 15%。
EOF

# 读取它
agent-fs cat reports/q1-summary.md

# 检查元数据
agent-fs stat reports/q1-summary.md
```

### 跨文件搜索

```bash
# 在特定路径内进行正则表达式搜索
agent-fs grep "revenue|growth" reports/

# 跨所有文件进行全文搜索（FTS5——快速关键词匹配）
agent-fs fts "季度收入"

# 混合搜索（组合关键词 + 语义匹配——推荐默认）
agent-fs search "财务绩效指标" --limit 5

# 仅向量语义搜索（仅概念匹配）
agent-fs vec-search "财务绩效指标" --limit 5
```

### 使用 SQL 查询数据文件

```bash
# 直接通过路径查询 CSV
agent-fs sql "SELECT category, sum(amount) AS total FROM '/finance/2026.csv' GROUP BY category" --json

# 连接不同格式的文档
agent-fs sql "SELECT s.name, t.tag FROM sales s JOIN tags t ON s.id = t.id" \
  -t sales=/data/sales.csv -t tags=/data/tags.parquet

# 查询存储的 SQLite 数据库（表作为 app.<table> 暴露）
agent-fs sql "SELECT count(*) FROM app.users" -t app=/backups/app.db

# 通过 stdin 管道查询
echo "SELECT count(*) FROM '/data/events.ndjson'" | agent-fs sql
```

### 审查和撤销更改

```bash
# 查看版本历史记录
agent-fs log docs/spec.md --limit 10

# 比较两个版本
agent-fs diff docs/spec.md --v1 2 --v2 5

# 撤销到版本 2
agent-fs revert docs/spec.md --version 2
```

### 评论和协作

```bash
# 向文件添加评论
agent-fs comment add docs/spec.md --body "需要更多关于认证的细节"

# 将评论锚定到确切文本（在它上面的编辑中保持不变；MCP/API 参数是引用：{ exact, prefix, suffix }）
agent-fs comment add docs/spec.md --body "哪个提供者？" --quote "OAuth 登录" --quote-suffix " 流程"

# 回复评论
agent-fs comment reply <comment-id> --body "v3 中已添加"

# 列出评论
agent-fs comment list docs/spec.md

# 检查未读通知（返回的 ID 是通知事件 ID）
agent-fs comment notifications --unread --limit 20

# 将选定的通知标记为已读
agent-fs comment read <notification-id> [<notification-id>...]

# 或者承认活动 drive 中的所有通知
agent-fs comment read --all

# 解决评论
agent-fs comment resolve <comment-id>
```

### 设置新的 drive 并邀请用户

```bash
# 创建共享 drive
agent-fs drive create "team-docs"

# 邀请队友
agent-fs drive invite alice@company.com --role editor

# 检查当前 drive 上下文
agent-fs drive current
```

### 管理成员

```bash
# 列出组织成员
agent-fs member list

# 列出 drive 成员
agent-fs --drive <driveId> member list

# 邀请用户
agent-fs member invite alice@company.com --role editor

# 更改角色
agent-fs member update-role alice@company.com --role admin

# 从组织中移除（级联到所有 drive）
agent-fs member remove alice@company.com

# 仅从特定 drive 中移除（保留组织成员资格）
agent-fs --drive <driveId> member remove alice@company.com
```

### 检查最近活动

```bash
# 最后一小时发生了什么变化？
agent-fs recent --since 1h

# 特定路径下的最近更改
agent-fs recent docs/ --since 24h --limit 20
```

### 生成可共享的下载链接

```bash
# 默认过期时间（24 小时）
agent-fs signed-url docs/report.pdf

# 自定义过期时间（1 小时）
agent-fs signed-url docs/report.pdf --expires-in 3600

# 在浏览器中渲染而不是下载（PDF 查看器、图像标签）
agent-fs signed-url docs/report.pdf --inline

# JSON 输出（对代理很有用）
agent-fs signed-url docs/report.pdf --json
# → { "url": "https://...", "path": "/docs/report.pdf", "expiresIn": 86400, "expiresAt": "2026-03-20T..." }
```

在 S3/MinIO 后端（`kind: "presigned"`）的 URL 不需要认证——任何拥有链接的人都可以在过期之前下载文件。访问权限仅在生成时进行 RBAC 检查（drive 上的 viewer 或更高权限）；之后 URL 是一个受信任的密钥。不要记录它或将其粘贴到您不会粘贴凭证的地方，并优先使用最短的工作 `--expires-in`。已签名 URL 根据文件扩展名提供正确的 `Content-Type` 头（例如，`.pdf` 为 `application/pdf`，`.png` 为 `image/png`）。默认情况下，它们还携带 `Content-Disposition: attachment`，因此打开链接会以真实名称保存文件。当链接将嵌入或用于查看时（例如 `<iframe>` 中的 PDF），请传递 `--inline`（API：`"disposition": "inline"`）；`<img>` 标签无论如何都不考虑 disposition。

在没有预签名 URL 的后端（本地文件系统后端）上，`signed-url` 不会失败——它会回退到经过认证的应用内链接（`kind: "app"`，`expiresIn: 0`）的形式 `<appUrl>/file/~/<org>/<drive>/<path>`。与预签名 URL 不同，此链接**不是**一个公开的受信任密钥：守护进程的 `/raw` 路线和网络查看器都需要登录，因此接收者必须是 drive 的经过认证的成员。设置 `AGENT_FS_APP_URL`（或 `config` 中的 `appUrl`）以便链接指向您的部署。

### 与没有账户的人共享文件

```bash
# 24h 链接，可以按需多次打开
agent-fs share-create docs/report.md

# 单次使用链接：页面打开一次，然后显示“链接过期”
agent-fs share-create docs/report.pdf --one-off

# 最多 5 次查看，有效期为 1 小时
agent-fs share-create docs/report.pdf --max-views 5 --expires-in 3600

# 取消链接（来自 share-create），或取消文件的所有链接
agent-fs share-revoke <id>
agent-fs share-revoke --path docs/report.pdf
```

`share-create` 返回 API 主机上的 URL（`https://<server>/share/<token>`），而不是网络应用，因此它适用于任何没有登录的人。与 `signed-url` 不同，接收者会获得渲染的页面：Markdown 转换为清理后的 HTML，文本和代码显示为转义，图像、PDF、音频和视频被嵌入，其他类型显示为无预览卡片。每个页面都有文件名、大小、过期时间和一个下载按钮。HTML 和 SVG 文件永远不会渲染，只会下载。

在共享之前值得知道的事情：

- **链接是一个受信任的密钥。** 拥有它的人可以在过期之前打开它，直到它过期、被撤销或用完查看次数。它只显示一次，并且只存储其 SHA-256，因此无法恢复；如果您可能需要撤销它，请保留 `id`。
- **它显示文件当前的内容**，而不是一个快照。如果文件被编辑，链接会显示新版本；如果它被删除或移动，链接会显示“文件不可用”。
- **`--one-off` / `--max-views` 计算页面查看次数，并且字节数随查看次数一起计算。** 限制查看次数的链接永远不会单独在 URL 上提供文件：花费查看次数的页面会获得一个私有的、短命的凭证（最多一小时，永远不会超过链接的过期时间），其嵌入和下载按钮使用该凭证。一旦用完查看次数，持有链接的任何人都不再能获取文件，并且撤销或过期链接会立即切断每个凭证。无限制链接不需要凭证。链接预览爬虫（Slack、WhatsApp、...）和 `HEAD` 请求不会消耗查看次数。
- **路径必须保持在 drive 内部。** `share-create` 会拒绝任何包含 `.` 或 `..` 段（任一斜杠方向）而不是解析它的路径。
- **viewer 角色足以创建链接**，并且创建者（或 drive 管理员）可以撤销它。每个计数的查看次数都会写入 `share_viewed` 事件。
- 当服务器位于不转发 `Host` / `X-Forwarded-*` 的代理后面时，请设置 `AGENT_FS_PUBLIC_URL`，以便返回的链接指向正确的地址。

**上传时的 MIME 类型：** `write`、`edit`、`append` 和 `revert` 会根据文件扩展名自动检测并设置 S3 对象的正确 `Content-Type`。内容类型也存储在数据库中，并通过 `contentType` 字段在 `stat` 输出中可见。原始 stdin 和 `--file` 上传会保留字节精确；只有在有效且可索引的 UTF-8 文本有效负载时才会应用文本搜索/索引。

### 响应中的 App URL

当 `AGENT_FS_APP_URL` 被设置（例如 `https://live.agent-fs.dev`）时，与文件相关的操作会自动包含一个指向实时网络应用的 `appUrl` 字段：

```bash
AGENT_FS_APP_URL=https://live.agent-fs.dev agent-fs stat docs/report.pdf --json
# → { ..., "appUrl": "https://live.agent-fs.dev/file/~/org-id/drive-id/docs/report.pdf" }
```

这适用于任何返回 `path` 或 `to` 字段的操作（写入、stat、编辑、追加、rm、cp、mv、signed-url、等）。

### 验证您的设置

```bash
agent-fs config validate
```

### 从沙盒挂载远程 drive

当代理在无法本地运行完整守护进程和 S3 堆栈的 Linux 沙盒（sprite、E2B、Hetzner VM、GitHub Actions runner 等）中运行时，请使用 `--remote`，这些沙盒可以访问托管的 agent-fs HTTP API 但无法本地运行。

```bash
# Linux 前置条件（每个沙盒运行一次）
sudo apt-get install -y fuse3
sudo chmod 666 /dev/fuse
sudo ln -sf /proc/mounts /etc/mtab
echo user_allow_other | sudo tee -a /etc/fuse.conf

# 认证——环境变量或 ~/.agent-fs/config.json
export AGENT_FS_API_URL=https://agent-fs.example.com
export AGENT_FS_API_KEY=<key>

# 挂载——不需要本地守护进程
mkdir -p ~/mnt
agent-fs mount ~/mnt --remote

# 使用普通的 shell 词汇对远程内容进行操作
ls ~/mnt
cat ~/mnt/current/docs/spec.md
echo "从沙盒编辑 $(date)" > ~/mnt/current/notes.txt

# 卸载
fusermount3 -u ~/mnt
```

有关每个环境的指南，请参阅 `docs/mounting/`（sprite、E2B、Hetzner）。

### 上传限制配置

原始 HTTP 上传默认为 50 MiB。在服务器上设置 `AGENT_FS_MAX_UPLOAD_BYTES`（例如 `104857600` 为 100 MiB）并重启守护进程以更改限制。无效值会回退到 50 MiB。网络 UI 从 `/health` 发现限制。JSON/MCP `write` 保持为 10 MiB。FUSE 保留 64 MiB 编码 IPC 帧上限，包括协议开销；对于大文件，请使用 HTTP 原始上传。

## 自有配置文件

`agent-fs profile get` 读取您的配置文件。`agent-fs profile set --name "Taras"` 设置您的显示名称。名称会被修剪，长度为 1–100 个字符，并且会向任何可以读取您的评论的人显示。只有您的经过认证的配置文件可以编辑。HTTP：`GET /auth/profile`，`PATCH /auth/profile` 使用 `{ "displayName": "Taras" }`（或 `null` 清除）。MCP：`profile-get`，`profile-set` 使用 `displayName`。网络账户菜单有 **编辑配置文件**。评论回复包括 `authorDisplayName` 当它被设置时；电子邮件和成员角色仍然是管理员专用的。
