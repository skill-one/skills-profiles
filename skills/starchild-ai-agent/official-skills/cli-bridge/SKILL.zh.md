---
name: cli-bridge
description: '管理短码包，授权本地 starchild CLI 与此代理进行通信，包括代理-shell 本地执行通道和本地 MCP 代理（用户机器上的 stdio MCP 服务器）。


  在连接或断开 starchild CLI 时使用（例如：生成 CLI 桥接码、列出我的 CLI 包、撤销旧的 CLI 会话、让代理在用户自己的机器上运行 shell 命令，或通过 stdio MCP 服务器驱动本地应用——Blender、Figma、Godot、电脑使用等）。'
---

# cli-bridge — 为用户的 `starchild` 二进制发布 CLI 套件

这项技能在本地 clawd 上铸造一个新的 AKM 密钥（`scope=chat:bridge:cli`），然后向 sc-chatroom 注册以换取一个短促的晦涩代码（``sc_xxxxxxxx``）。交给用户的套件只包含那个短代码——绝不包含 AKM 秘密，绝不包含 Fly 机器 ID。

```
+----------------+   POST /agent/chat/stream   +-----------------+
| starchild CLI  |   Bearer sc_xxxxxxxx        | sc-chatroom     |
| (用户笔记本电脑) | --------------------------> | (网关)       |
+----------------+                             +--------+--------+
                                                        |
                            解析 sc_… → AKM + 容器 ID
                                                        |
                                                        v
                                          POST /chat/stream (Bearer sk_…
                                          + fly-force-instance-id)
                                          +----------------------+
                                          | 用户自己的 clawd     |
                                          | (Fly 内部)       |
                                          +----------------------+
```

## 为什么使用短代码而不是原始 AKM？

早期版本直接将 AKM 秘密 + Fly 机器 ID 烘焙到套件中。这能工作，但有两大缺点——解码套件时会泄露路由元数据，任何曾经持有套件的方都持有一个永久 AKM 秘密。短代码形式修复了这两个问题：

- 套件 base64 解码为 ``{d, c:"", k:"sc_…", s, exp, l}`` — 没有秘密，没有 Fly 机器 ID。
- ``cli-revoke <sc_…>`` 仅删除短代码；底层的 AKM 仍然存活（使用 ``cli-revoke --akm <prefix>`` 来彻底删除它）。
- sc-chatroom 现在将其 AKM 秘密保存在其数据库中。这是一个故意的信任转移——AKM 保留在 Fly 的内部网络中，而不是在用户笔记本电脑上四处游荡。

## 范围边界 — 首先阅读此部分

`cli-bridge` 涵盖**恰好一条路径**：用户的本地 CLI 与用户自己的 clawd 进行一对一通信。它**不是**聊天室成员资格凭证。

| 用例       | 正确的凭证          | 错误的 |
|---|---|---|
| 个人 CLI ↔ 自己的 clawd（此项技能） | `chat:bridge:cli` AKM，由 `sc_…` 代码前端 | — |
| 加入 sc-chatroom 房间 | 通过 `chatroom join` 的 `chat:thread:chatroom-{room_id}` AKM | `chat:bridge:cli` AKM |
| 作为访客浏览公共房间 | 无需凭证          | 任何 AKM |

## 安装 CLI

本技能的其余部分假设 `starchild` 在用户的 `$PATH` 上——如果不在，请先安装它。

### 一行命令（自动检测操作系统 + 架构）

```bash
curl -fsSL https://workroom.iamstarchild.com/install/cli | bash
```

为 darwin/linux × arm64/amd64 选择正确的二进制文件，将其放在 `$PATH`（Apple Silicon 落在 `/opt/homebrew/bin`；Linux 落后于 `~/.local/bin`；只有在目录不是用户可写时才使用 `sudo`），如果安装目录不在 `$PATH` 中，则修补用户的 shell rc，并运行 `starchild --version` 作为自检。SHA256 etag 意味着重新运行是一个廉价的“已经当前”的无操作（HTTP 304，无下载）。审查源代码：[tools/install-cli.sh](https://workroom.iamstarchild.com/install/cli)（`__SERVER_URL__` 在请求时被重写）。

### Homebrew

```bash
brew tap starchild/tap https://github.com/Starchild-ai-agent/homebrew-tap
brew trust starchild/tap
brew install starchild
```

`starchild` 公式包含适用于 **macOS (arm64 / amd64) 和 Linux (arm64 / amd64)** 的二进制文件——`brew install` 为主机选择正确的文件。该公式没有 `bottle` 块，因此安装运行一个微小的 Ruby 脚本，从服务器（`workroom.iamstarchild.com`）下载预构建的二进制文件并将其放在 `$PATH` 上——没有本地编译步骤。稍后升级：`brew update && brew upgrade starchild`。

**Linux 注意事项**：Homebrew 本身可以在 Linux 上工作，但它期望 Ruby + 构建工具链（一次性 `apt install build-essential ruby` / 发行版等效项）。对于 Linux 主机，上面的命令行会跳过这些内容，并且功能上完全相同，因此除非用户已经是 brew 用户，否则请优先使用它。**`starchild-app`（桌面工作区）仅限 macOS**——该公式从源代码构建（rust + node），并且只有 macOS 构建有意义。

### 验证

```bash
starchild --version
```

如果您刚刚运行了命令行，而您的 shell 仍然显示 `command not found`，请打开一个新终端——PATH 更新在您的 rc 中，而不是当前会话中。

## 前置条件

与 `chatroom` 相同：

- AKM 在此 clawd 中安装（`POST /api/keys` 在回环上工作）
- AKM 接受 `scope="chat:bridge:cli"`，并且 `/chat/stream` 中间件允许该范围的任意 `thread_id`（已包含在 clawd 分支 `aladdin/feat/akm-chatroom` 中）
- sc-chatroom 在包含 `POST /cli-keys` 的构建上（迁移 007+）
- `FLY_MACHINE_ID`（或 `CONTAINER_ID`）环境变量已设置
- `CHATROOM_PUBLIC_URL` 环境变量指向 sc-chatroom 网关（默认为 `https://workroom.iamstarchild.com`）
- `CHATROOM_SERVER_URL` 环境变量指向 Fly 内部的 sc-chatroom（默认为 `http://sc-chatroom.internal:8080`）

## 命令

### `cli-login` — 铸造新套件

```bash
python3 skills/cli-bridge/scripts/cli_login.py --label "我的笔记本电脑"
python3 skills/cli-bridge/scripts/cli_login.py --label "codex-vm" --ttl-days 14
```

默认 TTL 为 90 天；最大为 365 天。输出是用户复制到 `starchild login` 的一行代码。套件是晦涩的——sc-chatroom 在每次调用时解析它。

### `cli-list` — 显示活动套件

```bash
python3 skills/cli-bridge/scripts/cli_list.py
python3 skills/cli-bridge/scripts/cli_list.py --include-revoked
```

列出此用户在 sc-chatroom 上铸造的每个 CLI 短代码。列：代码、发布、过期、使用、标签。

### `cli-revoke` — 删除套件

```bash
python3 skills/cli-bridge/scripts/cli_revoke.py sc_xxxxxxxx
python3 skills/cli-bridge/scripts/cli_revoke.py --akm sk_yyyyyy
```

默认：删除 sc-chatroom 中的短代码；底层的 AKM 仍然存活。使用 `--akm`：还将在本地 clawd 上撤销 AKM，删除它支持的每个套件。

## 通过 `agent-shell` 的本地 shell（CLI ≥ v0.2.0）

一个带有 `--enable-shell` 铸造的 `cli-login` 套件还授权代理在**用户自己的机器**上运行 shell 命令——用于“我的笔记本电脑上 nginx 是否在运行”、“组织 ~/Downloads”等。一个普通套件仅是聊天桥接，不授予任何 shell 访问权限（见下文“Shell 默认关闭”））。用户启动一个小型守护进程：

```bash
starchild agent-shell            # 守护化；持有一个到您的 clawd 的 WebSocket 打开
starchild agent-shell --foreground   # 连接到终端以进行调试
starchild agent-shell-stop       # 停止守护进程
```

`agent-shell` 如果登录的套件没有授予 shell，则拒绝启动——它告诉用户获取一个 `--enable-shell` 套件，而不是连接 clawd 会拒绝的通道。

守护进程是单实例（pidfile + flock）并且仅在 macOS/Linux 上运行。它在启动时和定期自我更新；下载的二进制文件在与嵌入式 Ed25519 发布密钥进行校验后才会替换，因此一个敌意或 MITM 的更新服务器无法向用户的机器推送任意代码。

它的工作原理：守护进程使用套件的 `sc_…` 代码拨打 `wss://<chatroom>/ws/cli-shell`。sc-chatroom 解析代码并将 WebSocket **反向代理**到用户的 clawd 机器——它接受笔记本电脑的升级，打开它自己的上游 WS 到带有 `fly-force-instance-id` 的 clawd，并在两者之间泵送字节（这**不是** `fly-replay`：聊天室和 clawd 是不同的 Fly 应用，跨应用重放被 403 拒绝）。AKM 在服务器端在上游跳跃时注入——它永远不会到达笔记本电脑。clawd 在其 `ShellHubService` 中保持连接；`local_shell` 工具仅在 shell 功能性笔记本电脑连接时暴露给 LLM，并将命令推送到套接字。

### Shell 默认关闭（能力门）

`cli-login` 除非传递了 `--enable-shell`，否则**不**授予 shell。AKM 是权威能力来源：clawd 在 `/ws/cli-shell` 握手时读取它，并拒绝不携带 `shell` 的连接（#264）。因此，一个泄露的普通套件是一个聊天凭证，永远不会是本地 RCE。

- 授予 shell：`cli_login.py --label … --enable-shell` → AKM
  `capabilities: ["shell"]`，套件携带 `x: ["shell"]`。
- 升级现有的无 shell 套件：你不能原地翻转它——铸造一个新的 `--enable-shell` 套件，`starchild login` 它，然后 `cli-revoke` 旧的。

权限升级始终通过新鲜发行。

### 代理一开始就知道的内容（能力清单）

连接时，守护进程发送一个 `hello` 帧来宣传：

- **平台** — `os`（darwin/linux）、`arch`（arm64/amd64）和活动的 `shell`。因此代理知道它是在与 BSD 还是 GNU 用户空间交谈，假设哪个包管理器，等等。——不再猜测 `ps` 标志或遇到 `ps: illegal option`。
- **策略摘要** — `mode`（当不存在允许规则时为 `default-deny`，否则为 `allowlist`）、用户的 `allowed` 规则、显式的 `denied-extra` 规则，以及始终开启的 `builtin_denied` 列表。
- **文件传输策略** — `transfer_dir`（始终允许的工作区）、`yolo` 标志，以及来自 `~/.config/starchild/file-policy.toml` 的 `read_allow` / `write_allow` 通配符。仅在套件携带 `files` 能力时存在。见下文“文件路径策略”的完整规则；这个要点只是让代理知道笔记本电脑宣布了文件传输。

clawd 将其渲染为代理的系统提示（仅在连接时），因此代理选择允许的命令——或者明确告诉用户本地策略禁止它——而不是盲目探测。

### 会话行为

- **连接级 cwd**。每个命令的结果工作目录都会回显（通过从 stdout 剥离的尾部 `pwd` 标记）并持久化以供下一个命令使用，因此 `cd` 在会话内跨调用具有实际意义——而没有完整 PTY 的成本/易碎性。显式的每调用 cwd 会覆盖它。
- **输出截断**。stdout/stderr 每个都限制在 200 行（加上字节限制），因此 `find /` 或日志转储不会淹没 LLM 上下文。报告完整的预截断行数（`stdout_lines` / `stderr_lines`），并设置 `truncated: true`——代理可以说“显示 N 行中的前 200 行”而不是无声截断。
- **心跳**。守护进程每 45 秒 ping 一次以保持空闲 WebSocket 活跃（Fly 的边缘在约 2.5 分钟时切断空闲套接字）。执行在 goroutine 中运行，因此长命令不会阻塞心跳。

### 本地执行策略（唯一的自动运行保护）

守护进程无头运行（没有 TTY 来提示），因此每个命令都由 `~/.config/starchild/exec-policy.toml`（解析为微小的 YAML `allow:`/`deny:` 行格式——没有 TOML 依赖，尽管名称如此）门控。规则默认为**子字符串**匹配；将规则用 `/ /` 包裹以进行正则表达式：

```yaml
allow:
  - "ls"
  - "cat "
  - "/^git (status|log|diff)/"
  - "ps"
deny:
  - "git push"
```

决策顺序：**内置拒绝（总是获胜）→ 文件 `deny` → 文件 `allow` → 默认拒绝**。两个硬规则无论文件如何都适用：

- 一个内置拒绝列表的交互式/TTY 阻塞和破坏性命令**总是**被拒绝：`vim`/`vi`/`nano`/`emacs`、`less`/`more`/`man`、`top`/`htop`/`btop`、`ssh`/`telnet`、`sudo`/`su`/`doas`、`tmux`/`screen`、`reboot`/`shutdown`/`halt`，以及形状 `rm -rf`、`mkfs`、`dd if=`、`… | sh`、`… | bash`、`> /dev/sd*`。
- **默认拒绝**：任何未通过 `allow` 规则匹配的内容都被拒绝。因此，如果没有策略文件，策略 `mode` 是 `default-deny`，并且直到用户选择命令之前什么都不会运行。

### 限制

- **仅未受监督的策略**。没有交互式批准提示；策略文件是唯一的保护。未来的版本添加了网络批准弹窗。
- **仅同步命令**。还没有后台作业/进度轮询。
- **仅 macOS/Linux**。守护进程拒绝在 Windows 上运行。
- **撤销**：`cli-revoke <sc_…>` 删除短代码；守护进程的下次重新连接会失败身份验证，并且通道关闭。

## 通过 `agent-shell` 的文件传输（CLI ≥ v0.3.0）

当套件带有 `--enable-files` 铸造时，相同的 `agent-shell` 守护进程还提供用户机器和代理工作区之间的**文件传输**。内容流磁盘→磁盘，永远不会通过聊天，因此**大/二进制文件（10MB+ PDF、图像、存档）可以工作**。

三个代理面朝工具 + 一个用户命令：
- `request_upload(laptop_path)` — 代理从笔记本电脑拉取文件到 `workspace/uploads/`（“拿我的 ~/big.pdf 并总结它”）。
- `write_local_file(src, dst)` — 代理将工作区文件发送到笔记本电脑（“将工作区/output/report.pdf 保存到我的 ~/Downloads”）。`src` 是工作区路径，而不是内联内容。
- `read_local_file(path)` — 读取一个**小文本**文件供代理查看（配置/日志片段）。大/二进制文件通过 `request_upload`。
- `starchild push <file>` — 用户主动将本地文件上传到代理的 `workspace/uploads/`；它在代理的提示中宣布。

```bash
python3 skills/cli-bridge/scripts/cli_login.py --label "笔记本电脑" --enable-files
# 如果您想要两者结合：
python3 skills/cli-bridge/scripts/cli_login.py --label "笔记本电脑" --enable-shell --enable-files
```

`files` 是一个**独立的能力**从 `shell`——一个套件可以拥有其中之一、两者或两者都没有。像 shell 一样，它默认关闭，并且在 AKM 上是权威的（clawd 拒绝没有它的传输帧）。

### 文件路径策略（笔记本电脑端，分层）

传输由笔记本电脑上的路径策略门控，最严格优先：

1. **内置受保护路径**始终被拒绝（即使在 `--yolo` 下）：`~/.ssh`、`~/.aws`、shell rc（`.zshrc`/`.bashrc`/…）、`.config/starchild`、launchd/systemd/cron、`.git/hooks`、浏览器 cookie 存储、`.env`、ssh 密钥。写入这些将是持久的 RCE；读取它们会泄露凭证。
2. **专用传输目录**（`~/starchild-transfer`，自动创建）——始终允许读取 + 写入。安全的工作区；优先使用它。
3. **在该目录外**——除非路径与 `~/.config/starchild/file-policy.toml` 中的 `read_allow` / `write_allow` 通配符匹配，**或者**守护进程使用 `--yolo` 启动：

   ```bash
   starchild agent-shell --yolo   # 允许任何路径（内置拒绝仍然适用）
   ```

   ```yaml
   # ~/.config/starchild/file-policy.toml  (YAML 允许通配符)
   read_allow:
     - "~/Documents/*.md"
   write_allow:
     - "~/exports/*.csv"
   ```

其他保证：写入文件的模式为 **0644**（永远不会可执行）；写入是原子的（临时文件 + 重命名，没有半完成的靶标）；逃逸传输目录的符号链接被拒绝；每个传输的限额为 100 MiB，分块流式传输，因此大文件不会导致 WebSocket 帧限制超限。

> **安全说明**：一个运行的 `agent-shell`（在 `--enable-shell` 套件上）加上宽松的策略实际上是在用户的机器上执行远程命令，受 AKM TTL、`sc_…` 代码的有效性和策略文件的约束。默认值是保守的：shell 是**关闭**的，除非明确授予，策略是**拒绝所有**，直到命令被选择，并且守护进程在替换二进制文件之前验证了**Ed25519 签名**。故意放宽。

这是从云端代理驱动本地应用程序（Blender、Godot、本地 Figma-bridge、计算机使用、浏览器使用、文件系统服务器等）的路径。代理无法以其他方式访问用户机器上的 `localhost`；clawd 自身的（直接）MCP 支持是为托管在其他地方的 REMOTE/HTTP/SSE 服务器，而不是必须运行在用户笔记本电脑上的进程。

### 工作原理（控制通道与 local_shell 相同是 WS）

```
clawd (云端代理)
  │  mcp_list / mcp_call 帧
  │  （通过现有的 /ws/cli-shell WebSocket）
  ▼
agent-shell 守护进程（笔记本电脑） ── MCPProxy
  │  stdio JSON-RPC（换行符分隔）
  ▼
blender-mcp / figma-mcp / 服务器一切 / … （每个服务器一个进程）
```

笔记本电脑端拥有 MCP 会话状态（初始化 → 初始化完成 → 工具列表，缓存）。clawd 只发送高级 `mcp_call`；它从不直接说 JSON-RPC。来自服务器的 `tools/list_changed` 通知会重新获取并重新注册该服务器的工具。

### 配置服务器

编辑 `~/.config/starchild/mcp-servers.toml`（YAML，尽管扩展名为 `.toml` — 与 exec/file-policy 相同的约定）。每个条目：

```yaml
servers:
  - id: blender
    command: uv
    args:
      - "--directory"
      - "/Users/aladdin/Workspace/StarChild/blender_mcp/mcp"
      - "run"
      - "blender-mcp"
    env:
      - "SOME_KEY=value"
    enabled: true
```

**仅使用绝对路径。** `$HOME` 和 `~` 不会被展开 — MCP 客户端直接启动命令，而不是通过 shell。使用 `/Users/<name>/...`，不要使用 `~/...` 或 `$HOME/...`。

`enabled` 默认为 `true`（没有 `enabled:` 的条目会运行）。该文件是热重载的，但 **运行会话只有在守护进程重新启动时才会改变** — 重载会更新解析的配置，它不会在会话中途启动/杀死服务器进程。应用程序的设置面板会为您写入此文件并重新启动 `agent-shell`。

### 重启 agent-shell 不会中断聊天

聊天流（您的回复给用户的）运行在 clawd 的 HTTP/SSE 路径上，**不是** 通过 `agent-shell`。重启 `agent-shell` 仅在重新连接所需的 ~2 秒内中断 `local_shell` / 文件传输 / `mcp_call` — 对话本身保持活跃。因此，您可以告诉用户（或通过 `local_shell` 自己）在配置更改后重新启动守护进程；您不会杀死对话。

重启后，守护进程会发送一个包含 `mcp_manifest` 的 `hello`，列出启用的服务器以及每个服务器的运行时状态（`ready`/`failed`/`not_started`）。clawd 會急切地 `mcp_list` 每个就绪的服务器并注册其工具。每回合的 `maybe_resync_local_mcp` 捕获也涵盖了在后续回合中未能获取 `hello` 的服务器（例如启动缓慢的服务器）。

### 动态注入 — `local_mcp_status` + `local_mcp_reload`

您不必重启 agent-shell 就能拾取配置编辑。有两个面向代理的工具驱动本地 MCP 运行时实时：

- **`local_mcp_status`** — 返回每个配置服务器的运行时状态（`ready` 带工具计数，`failed` 带错误，或 `not_started`）。当预期 `mcp__<server>__*` 工具缺失时调用此命令 — 服务器可能启动失败。
- **`local_mcp_reload`** — 要求 agent-shell 在运行时重新读取 `mcp-servers.toml`，启动新添加的服务器，停止已移除的服务器。**无需重启守护进程，无需中断聊天。** 重载后，添加的服务器的 `mcp__<server>__*` 工具会在 **下一回合** 出现（工具列表按请求重建）。编辑配置后使用此命令，以便在不要求用户重启任何内容的情况下提供新服务器。

当用户刚配置的服务器未显示工具时的典型流程：
1. 调用 `local_mcp_status` → 看到 `blender: not_started` 或 `failed: …`。
2. （如果 `failed` 则修复配置 — 路径错误、缺失依赖等。）
3. 调用 `local_mcp_reload` → agent-shell 启动新服务器。
4. 下一回合，`mcp__blender__*` 工具被注册。

### 代理看到的内容

- **工具** 出现为 `mcp__<server>__<tool>`（例如 `mcp__blender__get_scene`、`mcp__everything__echo`）。它们的 `description` 和 `input_schema` 来自服务器自己的 `tools/list` — 像任何原生工具一样调用它们。
- **提示清单**（`build_mcp_manifest_section`，在易失性尾部）列出了哪些本地 MCP 服务器已连接及其工具名称列表。如果服务器配置但启动失败，这里也会注明（配置存在，未加载）。
- 如果您看不到预期的 `mcp__<server>__*` 工具，服务器未启动。按以下顺序诊断：
  1. 它是否在 `~/.config/starchild/mcp-servers.toml` 中带有 `enabled: true`？
  2. `agent-shell` 是否在编辑后重新启动？（配置在启动时读取）
  3. 守护进程日志（`~/.starchild/sc-chatroom[-dev]/cli-shell/agent.log`）每行一个服务器：成功时显示 `agent-shell: mcp: <id> ready (N tools)`，失败时显示 `agent-shell: mcp: failed to start <id>: <reason>`。通过 `local_shell` 读取。
  4. 对于需要本地应用程序桥接的服务器（Blender 的 `127.0.0.1:9876` 插件、Figma 插件等），请确认桥接也在运行 — MCP 服务器进程可以启动，但直到后端应用程序可访问，其工具才会出错。

### 不要绕过 MCP 直接与本地应用程序通信

当 Blender 等服务器注册缓慢时，打开到应用程序自身桥接的原始套接字（`127.0.0.1:9876`）并发送 Python 直接，这很诱人。不要这样做 — 那会绕过 MCP 工具层（没有模式、没有策略、没有每次调用的验证），代理会失去结构化的 `mcp__blender__*` 接口。修复 MCP 服务器的启动问题（检查日志、确认桥接、重启 `agent-shell`）。原始桥接仅作为最后的紧急回退使用。

### 服务器注意事项（每个后端）

- **Blender MCP** (`blender-mcp`): 两部分 — stdio MCP 服务器 (`uv run`) 和 Blender 插件的桥接（监听 `127.0.0.1:9876`）。两者都必须运行。即使 Blender 关闭，MCP 服务器也会启动，但直到插件桥接启动，每个工具调用都会出错。`which blender` 即使 Blender.app 打开时也经常失败 — 那是正常的，桥接才是关键。
- **Figma**: 有两个不同的 Figma MCP。`figma-mcp-server`（REST-wrapper，只读画布）通过 `bunx` 本地运行；官方的 Figma 远程 MCP（写画布、SSE）是 REMOTE 服务器 — 在 clawd 端配置（`mcp_servers:` 在 agent.yaml 中），而不是这里。此文件仅用于在笔记本电脑上运行的服务器。
- **computer-use / browser-use**: 本质上是本地的（它们驱动用户的屏幕/浏览器）。在此处配置它们。

### 安全

本地 MCP 服务器可以在用户的机器上执行任意代码（Blender 的 `execute_code`、shell 服务器等）。将向 `mcp-servers.toml` 添加条目视为放宽执行策略一样严重：仅添加用户要求的服务器，优先选择只读服务器，并且永远不要在聊天中放入秘密（API 密钥） — 使用 `env:` 字段。`mcp-servers.toml` 路径默认不在文件策略允许列表中；如果用户希望代理直接写入配置，请将其添加到其中。

## 端到端冒烟测试

```bash
# 1. 在代理聊天中：
@agent 给我笔记本电脑的 CLI 密钥
# → 输出 `starchild login starchild_<base64>`（捆绑包包含 sc_… 代码）

# 2. 在笔记本电脑上：
starchild login starchild_xxx
starchild whoami
starchild "你好，你是谁？"
# → starchild 发送 Bearer sc_… 到 sc-chatroom；sc-chatroom 解析
# → 它到 AKM + 容器 ID 并转发给用户的 clawd

# 3. 从聊天中吊销短代码：
@agent 吊销 CLI 代码 sc_xxxxxxxx

# 4. 下一个 CLI 调用应在网关处失败：
starchild "你好？"
# → "网关拒绝（401）— 代码可能已被吊销；请向您的代理请求新的 CLI 捆绑包"
```

## 管道 / shell 组合（CLI ≥ v0.1.0）

配对后，`starchild` 对管道友好。当没有位置提示时，它会读取 stdin，将助手回复写入 stdout，并将诊断信息发送到 stderr — 因此它可以与任何 Unix 工具组合。

```bash
# stdin → 回复
echo "用三行解释单子" | starchild

# 回复 → 下游
starchild "OWASP 顶部 10 是什么？" | pbcopy

# 带有流式输出的三阶段管道
( echo "总结此 README:"; cat README.md ) | starchild --stream | tee summary.md

# 代码审查模式 — 上游连接上下文 + 问题
( echo "审查此差异，标记有风险的变化:"; git diff ) | starchild
```

**注意：** 当您传递位置提示时，stdin 会被 **忽略**。要发送上下文和指令，请使用 `( echo "<问题>"; cat <文件> )` 连接它们上游，而不是依赖 `cat <文件> | starchild "<问题>"`（这会静默丢弃文件内容）。

## SOUL.md 提示（推荐）

添加到您的代理的 SOUL.md，以便 LLM 在用户请求 CLI 密钥时选择正确的工具：

```markdown
## 为用户的自己的机器人/脚本颁发 CLI 捆绑包

当用户询问 "给我一个 CLI 密钥" / "创建 starchild 捆绑包" / "让我从我的终端与您交谈" 时，运行：

  python3 skills/cli-bridge/scripts/cli_login.py --label "<推断>"

这是一个聊天桥接 — 它不会让您在他们的机器上运行命令或触摸他们的文件。两个独立的可选功能，每个功能授予本地访问权限 — 只有在用户明确要求时才添加它们：

- `--enable-shell` → 运行命令（"在我的笔记本电脑上运行命令"、"使用 agent-shell"、"整理我的下载"). 远程命令执行。
- `--enable-files` → 读写文件（"保存到我的笔记本电脑" / "读取我的 ~/notes.md"）。读取/写入他们机器上的文件。

  python3 skills/cli-bridge/scripts/cli_login.py --label "<推断>" --enable-shell
  python3 skills/cli-bridge/scripts/cli_login.py --label "<推断>" --enable-files

将两者都视为授予对他们的机器的访问权限 — 永远不要默认添加任何一项或 "为了提供帮助" 而添加。如果他们后来想要一个功能，请使用标志 mint 一个新的捆绑包，并让他们吊销旧的捆绑包。

如果用户没有建议，请将标签默认设置为类似 "untitled-YYYY-MM-DD" 的内容。向他们展示结果捆绑包，并告诉他们如何吊销：`cli-list` 找到代码，然后 `cli-revoke sc_…`。

配对后，提及他们也可以从他们的 shell 管道到 CLI — 例如 `echo "..." | starchild`，`starchild "..." | pbcopy`，或 `( echo "审查:"; git diff ) | starchild`。stdout 是回复（管道安全），stderr 是诊断。注意：传递位置提示会使 stdin 被忽略，因此上下文 + 问题应该在上游连接。

## 通过 MCP 驱动本地应用程序（agent-shell ≥ v0.5.32）

一旦 `--enable-shell` 被授予并且 `agent-shell` 正在运行，您也可以通过 stdio MCP 服务器驱动本地应用程序（Blender、Godot、本地 Figma-bridge、computer-use 等）。代理-shell 守护进程是 MCP 主机：它读取 `~/.config/starchild/mcp-servers.toml`，启动服务器，并将它们的工具注册为 `mcp__<server>__<tool>` 到此对话中。无需单独的 MCP 客户端（Cursor/Claude Desktop）。

当用户询问 "控制 Blender" / "使用本地 Figma 插件" / "通过 MCP 驱动我的本地 <应用程序>" 时：
- 确认 `agent-shell` 已连接（`local_shell` 调用有效）。
- 将服务器添加到 `~/.config/starchild/mcp-servers.toml`（仅使用绝对路径 — 没有 `$HOME`，没有 `~`）。应用程序的设置 → 本地 MCP 服务器面板也可以这样做。
- 重启 `agent-shell` (`starchild agent-shell-stop && starchild agent-shell`，或通过应用程序的 RestartBanner）。这不会中断聊天 — 仅 `local_shell`/文件传输暂停约 2 秒。
- 重启后，`mcp__<server>__*` 工具会出现。如果没有，请通过 `local_shell` 读取守护进程日志（`~/.starchild/sc-chatroom[-dev]/cli-shell/agent.log` — 查找 `mcp: <id> ready` 或 `mcp: failed to start <id>: <reason>`）。
- 对于需要本地应用程序桥接的服务器（Blender 的 `127.0.0.1:9876` 插件），请确认桥接也在运行 — MCP 服务器进程可以启动，但直到后端应用程序启动，其工具才会出错。
- 优先选择 `mcp__<server>__*` 工具，而不是打开到应用程序桥接的原始套接字。MCP 层为您提供模式 + 验证；原始桥接是最后的紧急回退。

不要添加用户未要求的服务器 — 本地 MCP 服务器可以在他们的机器上执行任意代码。请参阅上面的 "Local MCP servers via agent-shell" 部分以获取完整的配置格式和每个后端的注意事项（Blender 两部分，Figma 本地与远程等）。
