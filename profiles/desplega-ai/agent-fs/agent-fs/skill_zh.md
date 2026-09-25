# agent-fs 命令行界面

agent-fs 是一个以代理为中心的文件系统，具有完整版本控制、全文搜索（FTS5）和语义搜索功能。它提供了一个输出 JSON 的命令行界面，非常适合代理工作流程。文件按驱动器组织在组织中。

## 存储后端

agent-fs 将文件字节存储在可插拔的存储后端中。持久的值——版本历史记录、评论和搜索——存储在 SQLite 中，并在每个后端上以相同的方式工作。

| 后端 | 设置 | 版本控制级别 | `signed-url` |
|------|------|--------------|--------------|
| **S3 / MinIO**（默认） | `agent-fs onboard -y`（本地 MinIO，需要 Docker）或 `--s3-*` 标志用于 AWS/R2 等。 | 完整——`revert` + 历史记录 `diff` 通过 S3 对象版本控制 | 真实的预签名 URL（公开，有时间限制） |
| **本地文件系统** | `agent-fs onboard --filesystem`（不需要 Docker，不需要 S3） | 完整——`revert` + 历史记录 `diff` 通过磁盘上的内容寻址 blob | 回退到经过身份验证的应用内链接（需要登录；不会过期） |

这两个后端都是 **完整级别**：每个操作——包括 `revert` 和历史记录 `diff`——都可以工作。未来的后端可能是 **基本级别**（没有对象版本控制）：在这些后端上，`revert` 和历史记录 `diff` 会干净地失败并返回 `UNSUPPORTED_OPERATION` 错误（HTTP 422），而不是原始存储错误——当前内容、列表、评论和搜索仍然可以正常工作。如果您不确定驱动器使用哪个后端，请在依赖版本控制之前检查后端的功能。

## 快速入门

```bash
# 1. 设置（本地 MinIO — 需要 Docker）
agent-fs onboard -y

#    ...或者在没有 Docker/S3 的情况下——将字节存储在本地文件系统中：
agent-fs onboard --filesystem            # 使用 ~/.agent-fs/storage
agent-fs onboard --filesystem --storage-root /data/agent-fs   # 自定义目录

# 2. 可选地启动守护进程（CLI 自动检测，无需启动它）
agent-fs daemon start

# 3. 开始使用它
echo "hello world" | agent-fs write docs/readme.txt -m "初始版本"
agent-fs cat docs/readme.txt
```

对于自定义 S3（AWS、R2 等），请使用标志：`agent-fs onboard --s3-endpoint <url> --s3-bucket <name> --s3-access-key <key> --s3-secret-key <key>`。

本地文件系统后端（`--filesystem`，等效于 `--storage local`）不需要 Docker，也不需要 S3——字节存储在 `--storage-root`（默认 `~/.agent-fs/storage`）下，每个版本都是内容寻址的，因此 `revert` 和历史记录 `diff` 与 S3 上的工作方式相同。

## just-bash 适配器

当 `just-bash` 环境需要通过 agent-fs 作为其 `fs` 实现来读取和写入时，请使用 `@desplega.ai/agent-fs-just-bash`。

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

适配器使用 `/raw` 进行安全的字节读取/写入，并使用 `/ops` 进行列表和元数据。空目录由隐藏的 `.agent-fs-dir` 标记表示；符号链接不受支持，会抛出 `EPERM`。

## 基本模式

1. **使用 JSON 进行机器输出**——在解析 CLI 输出时传递 `--json`（`download` 不带 `-o` 除外，它将原始字节写入 stdout；`daemon status` 和 `auth register` 打印人类可读的文本）。

2. **自动检测**——CLI 会自动检测守护进程是否正在运行。如果正在运行，命令将通过 HTTP 发送；否则，它们将直接使用嵌入式模式。无需用户操作。

3. **默认组织/驱动器解析**——如果没有 `--org`/`--drive` 标志，CLI 将按顺序解析：标志本身，然后本地配置（`org switch <id>` / `drive switch <id>`，对每台机器都是粘性的），然后 `AGENT_FS_DEFAULT_ORG_ID` / `AGENT_FS_DEFAULT_DRIVE_ID` 环境变量（部署级别的提示，例如代理群集工作容器被配置写入的共享组织），然后账户自己的默认组织/驱动器从 `GET /me`（自动创建的个人组织，除非更改）。如果写入位置出乎意料，请检查 `agent-fs org current` / `agent-fs drive current`（`source` 字段）——没有标志的写入始终会落在个人组织/驱动器上，除非较早的级别已设置。

4. **Stdin 和文件上传**——`write` 接受来自 stdin 或 `--file` 的原始字节，以及来自 `--content` 的文本；`append` 接受通过 stdin 或 `--content` 的文本：
   ```bash
   # 推荐用于多行文本
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
| `edit` | `agent-fs edit <path> --old <text> --new <text> [-m <msg>]` | 在文件中查找和替换 |
| `append` | `agent-fs append <path> [--content <text>] [-m <msg>]` | 追加到文件（stdin 或 --content） |
| `tail` | `agent-fs tail <path> [--lines <n>]` | 最后 N 行（默认：20） |
| `ls` | `agent-fs ls [path]` | 列出目录内容（默认为 /） |
| `stat` | `agent-fs stat <path>` | 显示文件元数据（大小、版本、时间戳） |
| `tree` | `agent-fs tree [path] [--depth <n>]` | 递归目录列表 |
| `glob` | `agent-fs glob <pattern> [--path <prefix>]` | 通过模式查找文件（`*.md`，`**/*.md`）跨所有存储页面 |
| `rm` | `agent-fs rm <path>` | 删除文件 |
| `mv` | `agent-fs mv <from> <to> [-m <msg>]` | 移动或重命名文件 |
| `cp` | `agent-fs cp <from> <to>` | 复制文件 |
| `signed-url` | `agent-fs signed-url <path> [--expires-in <seconds>] [--inline]` | 生成下载 URL。在 S3/MinIO 上：预签名 URL（默认 24 小时，最长 7 天，`kind: "presigned"`）。在本地文件系统上：经过身份验证的应用内链接（`kind: "app"`，需要登录，非过期）。默认情况下，URL 强制下载；`--inline` 使浏览器渲染文件（PDF、图像）。 |
| `download` | `agent-fs download <path> [-o <local-path>]` | 下载原始字节 |

`cat` 是分页查看器，不是原始文件读取器：如果没有 `--limit`，它在 TTY 上默认为前 200 行，但如果 stdout 被管道或重定向，则会返回**整个文件**（管道/重定向几乎总是意味着“给我所有内容”。任何时候 `cat` 返回的行数少于请求的行数，`truncated: showing N of M lines (use --limit)` 的注释都会发送到 **stderr**——永远不会发送到 stdout，因此永远不会损坏管道/重定向的输出。默认视图（非 `--raw`，TTY）还会为每行添加行号以提高可读性；该前缀**不是**存储的字节的一部分。对于完整的、字节精确的读取——在解析为 CSV/JSON 之前或任何时间行号或部分读取会损坏数据时——请使用 `agent-fs cat <path> --raw` 或更好的 `agent-fs download <path> -o <file>`。

### 版本控制

| 命令 | 用法 | 描述 |
|------|------|------|
| `log` | `agent-fs log <path> [--limit <n>]` | 显示版本历史记录 |
| `diff` | `agent-fs diff <path> --v1 <n> --v2 <n>` | 版本之间的差异 |
| `revert` | `agent-fs revert <path> --version <n>` | 恢复到以前的版本 |

`log` 在每个后端上工作（版本元数据存储在 SQLite 中）。`revert` 和历史记录 `diff`（比较两个存储的版本）需要一个**完整级别**的后端——S3/MinIO 和本地文件系统都符合条件。在一个没有对象版本控制的基本级别后端上，`revert` 和历史记录 `diff` 会干净地失败并返回 `UNSUPPORTED_OPERATION`（HTTP 422）；`diff` 会降级为存储的摘要，而不是完整内容。

### 搜索和发现

| 命令 | 用法 | 描述 |
|------|------|------|
| `grep` | `agent-fs grep <pattern> <path>` | 在文件内容中正则搜索 |
| `fts` | `agent-fs fts <pattern> [--path <prefix>]` | 使用 FTS5 查询语法在活动驱动器中进行全文搜索 |
| `search` | `agent-fs search <query> [--limit <n>]` | 混合搜索（语义 + 关键字，最适合一般查询） |
| `vec-search` | `agent-fs vec-search <query> [--limit <n>]` | 在活动驱动器中不同文件上进行语义搜索 |
| `recent` | `agent-fs recent [path] [--since <duration>] [--limit <n>]` | 最近活动（例如，`--since 24h`） |
| `reindex` | `agent-fs reindex [path]` | 重新索引具有失败/缺失嵌入的文件 |

**何时使用哪个：**
- `grep` — 您知道确切的模式和路径（正则表达式）
- `fts` — 关键字搜索跨所有文件（快速，基于 FTS5）
- `search` — 通用搜索结合关键字和含义（推荐默认）
- `vec-search` — 纯语义搜索，当您只想获得概念匹配时

搜索使用活动组织驱动器。检查 `org current` 和 `drive current`，或者传递显式的 `--org` 和 `--drive` 标志。
`glob`、`ls` 和 `tree` 读取每个 S3 列表页面。一个包含超过 1,000 个对象的驱动器仍然可搜索。
`search` 和 `vec-search` 在活动驱动器中选择语义候选者，并计算不同文件以限制数量。
语义结果需要嵌入。`vec-search` 在没有提供程序的情况下返回一个提示，而 `search` 会识别仅关键字的结果。

`fts` 接受原始 FTS5 语法。使用 FTS 双引号在 shell 单引号内引用包含标点的术语：

```bash
agent-fs glob '**/*ai-tinkerers*'
agent-fs glob '**/*ai-tinkerers*' --path thoughts/research
agent-fs fts '"ai-tinkerers"'
agent-fs fts 'ai AND tinkerers'
```

在 FTS 引用术语中嵌入引号。反斜杠转义不会转义 FTS 引用。

文件名模式区分大小写。全文匹配索引的标记，因此这两种模式都不会更正拼写错误。

### SQL 查询（DuckDB）

| 命令 | 用法 | 描述 |
|------|------|------|
| `sql` | `agent-fs sql <query> [-t name=path[:format]]... [--max-rows <n>]` | 在存储的文档上运行 DuckDB SQL |

支持的格式：csv、tsv、parquet、xlsx、json、ndjson/jsonl（每种格式也 `.gz` 除外，除了 parquet/xlsx）、sqlite（`.db`/`.sqlite`/`.sqlite3`）和 `.duckdb`。直接引用带引号的驱动器路径来引用文件格式文档，或者将任何文档绑定到表名 `-t`。SQLite/DuckDB 数据库需要 `-t` 绑定，并将它们的表作为 `<name>.<table>` 暴露。将 `:format` 添加到绑定以查询具有非标准扩展名的文档（例如 `-t logs=/raw/data.txt:csv`）。查询是沙盒化的——没有主机文件系统或网络访问。结果限制在 `--max-rows`（默认 1000，最大 10000）；JSON 输出中的 `truncated: true` 指示存在更多行。

### 评论

| 命令 | 用法 | 描述 |
|------|------|------|
| `comment add` | `agent-fs comment add <path> --body <text> [--line-start <n>] [--line-end <n>]` | 向文件添加评论 |
| `comment reply` | `agent-fs comment reply <comment-id> --body <text>` | 回复评论 |
| `comment list` | `agent-fs comment list [path]` | 列出评论（包括内联回复） |
| `comment get` | `agent-fs comment get <id>` | 获取带有其回复的评论 |
| `comment update` | `agent-fs comment update <id> --body <text>` | 更新评论（仅作者） |
| `comment delete` | `agent-fs comment delete <id>` | 软删除评论（仅作者） |
| `comment resolve` | `agent-fs comment resolve <id>` | 解决评论 |
| `comment notifications` | `agent-fs comment notifications [--unread] [--limit <n>]` | 列出当前用户在活动驱动器中的评论通知 |
| `comment read` | `agent-fs comment read [ids...] [--all]` | 将选定的通知事件 ID 标记为已读，或标记活动驱动器中的所有通知为已读 |

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
| `member remove` | `agent-fs member remove <email>` | 从组织中移除（使用 `--drive <id>` 仅移除驱动器） |
| `member reset-key` | `agent-fs member reset-key <email>` | 重置成员的 API 密钥（组织管理员专有）。旧密钥立即失效。 |

`--drive` 标志是全局选项——将其放在子命令之前：`agent-fs --drive <id> member list`。

成员命令由管理员控制：组织范围的命令需要组织 `admin`；驱动器范围的命令（`--drive <id>`）需要驱动器 `admin` 或拥有组织的管理员，并且驱动器必须属于当前组织。非管理员会收到权限错误；组织/驱动器 ID 不在您的成员资格中会返回“未找到”。

### 驱动器管理

| 命令 | 用法 | 描述 |
|------|------|------|
| `drive list` | `agent-fs drive list` | 列出当前组织中的驱动器 |
| `drive create` | `agent-fs drive create <name>` | 创建新驱动器（需要组织管理员） |
| `drive current` | `agent-fs drive current` | 显示当前驱动器上下文 |
| `drive invite` | `agent-fs drive invite <email> --role <role>` | 邀请用户（查看者/编辑者/管理员） |

驱动器成员是显式的：`drive list` 只显示您是成员的驱动器。创建驱动器会自动授予您在该驱动器上的管理员成员资格；其他用户必须逐驱动器邀请（或通过组织邀请，这会授予默认驱动器的访问权限）。

### 配置和守护进程

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

将所有组织驱动器作为 Linux FUSE 文件系统公开，以便代理可以使用普通的 shell 词汇（`cat`，`grep`，`mv`，`rm`）针对 agent-fs 内容。需要 `/dev/fuse` 和 `SYS_ADMIN` 能力；在 macOS 或基于 gVisor 的沙盒中不可用。

支持两种拓扑结构：
- **本地模式**（默认）：助手通过 Unix 套接字与本地守护进程通信。守护进程必须正在运行并且配置了 S3 后端。
- **远程模式**（`--remote`）：助手直接与远程 agent-fs HTTP API 通信。不需要本地守护进程——非常适合沙盒（sprite、E2B、Hetzner VM、GitHub Actions 运行器）可以访问托管 agent-fs 但无法本地运行完整守护进程 + S3 堆栈的环境。

FUSE 写入需要驱动器上的 `editor` 角色或更高权限——在您是 `viewer` 的驱动器上，对于文件写入，挂载是只读的（写入失败 `EACCES`；检查 `<mount>/.agent-fs/errors.ndjson` 中的 `PERMISSION_DENIED` 记录）。

| 命令 | 用法 | 描述 |
|------|------|------|
| `mount` | `agent-fs mount <path> [--allow-other] [--foreground]` | 通过本地守护进程在 `<path>` 处挂载驱动器（例如 `/mnt/agent-fs/<drive>/`). |
| `mount --remote` | `agent-fs mount <path> --remote [--api-url <url>] [--api-key <key>]` | 对远程 agent-fs HTTP API 进行挂载。如果没有标志，则从 `~/.agent-fs/config.json` 或 `AGENT_FS_API_URL`/`AGENT_FS_API_KEY` 环境变量中读取 `apiUrl`/`apiKey`。优先使用环境变量而不是 `--api-key`（后者会在 `ps` 中暴露密钥）。当链接将被嵌入或打开以查看时，请使用 `--inline`（API: `"disposition": "inline"`）当链接将嵌入或打开以查看时，例如 `<iframe>` 中的 PDF；`<img>` 标签无论如何都不忽略 disposition。

在缺少预签名 URL 的后端（本地文件系统后端）上，`signed-url` 不会失败——它会回退到经过身份验证的应用内链接（`kind: "app"`，`expiresIn: 0`）的形式 `<appUrl>/file/~/<org>/<drive>/<path>`。与预签名 URL 不同，此链接**不是**公开的载体密钥：守护进程的 `/raw` 路径和 Web 查看器都需要登录，因此接收者必须是驱动器的经过身份验证的成员。设置 `AGENT_FS_APP_URL`（或 `appUrl` 在配置中）以便链接指向您的部署。

**上传时的 MIME 类型**：`write`、`edit`、`append` 和 `revert` 根据文件扩展名自动检测并设置 S3 对象的正确 `Content-Type`。内容类型也存储在数据库中，并通过 `stat` 输出中的 `contentType` 字段可见。原始 stdin 和 `--file` 上传保留字节精确；只有当有效、可索引的 UTF-1 文本有效时，才会应用文本搜索/索引。

### 响应中的 App URL

当 `AGENT_FS_APP_URL` 设置时（例如 `https://live.agent-fs.dev`），文件相关操作会自动包含一个 `appUrl` 字段，指向实时 Web 应用中的文件：

```bash
AGENT_FS_APP_URL=https://live.agent-fs.dev agent-fs stat docs/report.pdf --json
# → { ..., "appUrl": "https://live.agent-fs.dev/file/~/org-id/drive-id/docs/report.pdf" }
```

这适用于任何返回 `path` 或 `to` 字段（写入、stat、edit、append、rm、cp、mv、signed-url 等）的操作。

### 验证您的设置

```bash
agent-fs config validate
```

### 从沙盒挂载远程驱动器

当代理在 Linux 沙盒（sprite、E2B、Hetzner VM、GitHub Actions 运行器等）中运行时，使用 `--remote`，这些沙盒可以访问托管 agent-fs HTTP API 但无法本地运行完整守护进程 + S3 堆栈的环境。

```bash
# Linux 前提条件（每个沙盒运行一次）
sudo apt-get install -y fuse3
sudo chmod 666 /dev/fuse
sudo ln -sf /proc/mounts /etc/mtab
echo user_allow_other | sudo tee -a /etc/fuse.conf

# 认证——使用环境变量或 ~/.agent-fs/config.json
export AGENT_FS_API_URL=https://agent-fs.example.com
export AGENT_FS_API_KEY=<key>

# 挂载——不需要本地守护进程
mkdir -p ~/mnt
agent-fs mount ~/mnt --remote

# 使用普通的 shell 词汇针对远程内容
ls ~/mnt
cat ~/mnt/current/docs/spec.md
echo "edit from sandbox $(date)" > ~/mnt/current/notes.txt

# 卸载
fusermount3 -u ~/mnt
```

有关每个环境的指南，请参阅 `docs/mounting/`（sprite、E2B、Hetzner）。

## 个人资料

`agent-fs profile get` 读取您的个人资料。`agent-fs profile set --name "Taras"`
设置您的显示名称。名称被修剪，1–100 个字符，并且显示给任何可以读取您的评论的人。只有您的经过身份验证的个人资料可以编辑。
HTTP: `GET /auth/profile`, `PATCH /auth/profile` with `{ "displayName": "Taras" }`（或 `null` 清除）。MCP: `profile-get`, `profile-set` with `displayName`。
Web 账户菜单中有 **编辑个人资料**。评论回复包括 `authorDisplayName` 当设置时；电子邮件和成员角色仍然是管理员专有的。
