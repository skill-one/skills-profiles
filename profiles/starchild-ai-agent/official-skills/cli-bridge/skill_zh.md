# cli-bridge — 为用户自己的 `starchild` 二进制发行 CLI 绑定包

本技能在本地 clawd 上铸造一把全新的 AKM 密钥（`scope=chat:bridge:cli`），然后将其注册到 sc-chatroom，以换取一个短的不透明代码（``sc_xxxxxxxx``）。交付给用户的绑定包仅包含该短代码——绝不含 AKM 密钥，也绝不含 Fly 机器 ID。

```
+----------------+   POST /agent/chat/stream   +-----------------+
| starchild CLI  |   Bearer sc_xxxxxxxx        | sc-chatroom     |
| (用户笔记本)   | --------------------------> | (网关)          |
+----------------+                             +--------+--------+
                                                        |
                            解析 sc_… → AKM + container_id
                                                        |
                                                        v
                                          POST /chat/stream (Bearer sk_…
                                          + fly-force-instance-id)
                                          +----------------------+
                                          | 用户自己的 clawd     |
                                          | (Fly 内部)          |
                                          +----------------------+
```

## 为什么用短代码而不是原始 AKM？

早期版本直接将 AKM 密钥 + Fly 机器 ID 嵌入绑定包中。虽然可用，但有两个缺点——绑定包解码后会泄露路由元数据，且任何曾持有该绑定包的方都永久持有一把 AKM 密钥。短代码形式修复了这两个问题：

- 绑定包 base64 解码为 ``{d, c:"", k:"sc_…", s, exp, l}``——无密钥，无 Fly 机器 ID。
- ``cli-revoke <sc_…>`` 仅撤销短代码；底层 AKM 仍然存活（使用 ``cli-revoke --akm <prefix>`` 可一并撤销）。
- sc-chatroom 现在在其数据库中持有 AKM 密钥。这是有意为之的信任转移——AKM 保留在 Fly 内部网络中，而不是在用户笔记本上四处流转。

## 作用域边界 — 请先阅读

`cli-bridge` 仅覆盖**一条路径**：用户的本地 CLI 与该用户自己的 clawd 进行 1:1 通信。它**不是**聊天室成员凭证。

| 使用场景 | 正确凭证 | 错误 |
|---|---|---|
| 个人 CLI ↔ 自己的 clawd（本技能） | `chat:bridge:cli` AKM，由 `sc_…` 代码前置 | — |
| 加入 sc-chatroom 房间 | 通过 `chatroom join` 获取 `chat:thread:chatroom-{room_id}` AKM | `chat:bridge:cli` AKM |
| 以访客身份浏览公共房间 | 无需凭证 | 任何 AKM |

## 安装 CLI

本技能的其余部分假设 `starchild` 已在用户的 `$PATH` 中——如果尚未安装，请先安装。

### 一行命令（自动检测操作系统 + 架构）

```bash
curl -fsSL https://workroom.iamstarchild.com/install/cli | bash
```

根据 darwin/linux × arm64/amd64 选择正确的二进制文件，将其放置到 `$PATH`（Apple Silicon 落在 `/opt/homebrew/bin`；Linux 回退到 `~/.local/bin`；仅当目标目录不可写时才使用 `sudo`），如果安装目录原本不在 `$PATH` 中则修补用户的 shell rc 文件，并运行 `starchild --version` 作为自检。SHA256 etag 意味着重新运行是廉价的"已是最新"空操作（HTTP 304，无下载）。审查源代码：[tools/install-cli.sh](https://workroom.iamstarchild.com/install/cli)（`__SERVER_URL__` 在请求时会被重写）。

### Homebrew

```bash
brew tap starchild/tap https://github.com/Starchild-ai-agent/homebrew-tap
brew trust starchild/tap
brew install starchild
```

`starchild` formula 提供 **macOS (arm64 / amd64) 和 Linux (arm64 / amd64)** 的二进制文件——`brew install` 会为宿主选择正确的版本。该 formula 没有 `bottle` 块，因此安装过程会运行一个小型 Ruby 脚本，从服务器（`workroom.iamstarchild.com`）下载预构建二进制并放到 `$PATH`——没有本地编译步骤。日后升级：`brew update && brew upgrade starchild`。

**Linux 注意事项：** Homebrew 本身在 Linux 上可用，但需要 Ruby + 构建工具链（一次性执行 `apt install build-essential ruby` / 发行版等价命令）。对于 Linux 主机，上述一行命令可跳过这些依赖且功能完全相同，除非用户已是 brew 用户，否则建议优先使用一行命令。**`starchild-app`（桌面工作区）仅限 macOS**——该 formula 从源码构建（rust + node），仅 macOS 构建有意义。

### 验证

```bash
starchild --version
```

如果刚运行了一行命令而 shell 仍提示 `command not found`，请打开新终端——PATH 更新在 rc 文件中，而非当前会话。

## 前置条件

与 `chatroom` 相同：

- 此 clawd 已安装 AKM（`POST /api/keys` 在回环地址上可用）
- AKM 接受 `scope="chat:bridge:cli"`，且 `/chat/stream` 中间件对该 scope 允许任意 `thread_id`（已在 clawd 分支 `aladdin/feat/akm-chatroom` 中发布）
- sc-chatroom 运行在包含 `POST /cli-keys` 的构建版本上（migration 007+）
- `FLY_MACHINE_ID`（或 `CONTAINER_ID`）环境变量已设置
- `CHATROOM_PUBLIC_URL` 环境变量指向 sc-chatroom 网关（默认为 `https://workroom.iamstarchild.com`）
- `CHATROOM_SERVER_URL` 环境变量指向 Fly 内部 sc-chatroom（默认为 `http://sc-chatroom.internal:8080`）

## 命令

### `cli-login` — 铸造新绑定包

```bash
python3 skills/cli-bridge/scripts/cli_login.py --label "my laptop"
python3 skills/cli-bridge/scripts/cli_login.py --label "codex-vm" --ttl-days 14
```

默认 TTL 为 90 天；最大 365 天。输出是一行文本，用户复制到 `starchild login`。绑定包是不透明的——sc-chatroom 在每次调用时解析它。

### `cli-list` — 查看活跃绑定包

```bash
python3 skills/cli-bridge/scripts/cli_list.py
python3 skills/cli-bridge/scripts/cli_list.py --include-revoked
```

列出该用户在 sc-chatroom 上铸造的所有 CLI 短代码。列：code、issued、expires、uses、label。

### `cli-revoke` — 撤销绑定包

```bash
python3 skills/cli-bridge/scripts/cli_revoke.py sc_xxxxxxxx
python3 skills/cli-bridge/scripts/cli_revoke.py --akm sk_yyyyyy
```

默认：仅撤销 sc-chatroom 上的短代码；底层 AKM 仍然存活。使用 `--akm`：同时撤销本地 clawd 上的 AKM，彻底清除所有由它支撑的绑定包。

## 通过 `agent-shell` 使用本地 shell（CLI ≥ v0.2.0）

使用 `--enable-shell` 铸造的 `cli-login` 绑定包还会授权代理在**用户自己的机器**上运行 shell 命令——适用于"我的笔记本上 nginx 是否在运行"、"整理 ~/Downloads"等场景。普通绑定包仅为聊天桥接，不授予 shell 访问权限（见下方"Shell 默认关闭"）。用户启动一个小守护进程：

```bash
starchild agent-shell            # 守护进程化；保持与 clawd 的 WS 连接
starchild agent-shell --foreground   # 附加到终端用于调试
starchild agent-shell-stop       # 停止守护进程
```

如果登录的绑定包未授予 shell 权限，`agent-shell` 会拒绝启动——它会提示用户获取 `--enable-shell` 绑定包，而不是连接到一个 clawd 会拒绝的通道。

守护进程为单实例（pidfile + flock），仅支持 macOS/Linux。启动时和运行中会自检更新；下载的二进制在替换前对照内置的 Ed25519 发布密钥进行校验，因此恶意或被中间人劫持的更新服务器无法向用户机器推送任意代码。

工作原理：守护进程使用绑定包的 `sc_…` 代码拨号连接 `wss://<chatroom>/ws/cli-shell`。sc-chatroom 解析该代码并**反向代理** WebSocket 到用户的 clawd 机器——它接受笔记本的 upgrade 请求，用 `fly-force-instance-id` 钉住自己到 clawd 的上游 WS 连接，并在两者之间中转字节（这*不是* `fly-replay`：chatroom 和 clawd 是不同的 Fly 应用，跨应用 replay 会被 403 拒绝）。AKM 在上游跳中由服务端注入——它永远不会到达笔记本。clawd 在其 `ShellHubService` 中持有该连接；`local_shell` 工具**仅在 shell 能力的笔记本已连接时**才对 LLM 可见，并通过套接字向下推送命令。

### Shell 默认关闭（能力门控）

`cli-login` **不会**授予 shell，除非传入 `--enable-shell`。AKM 是权威能力来源：clawd 在 `/ws/cli-shell` 握手时读取它，并拒绝所有不携带 `shell` 连接的 exec（#264）。因此泄露的普通绑定包仅是聊天凭证，绝非本地 RCE。

- 授予 shell：`cli_login.py --label … --enable-shell` → AKM `capabilities: ["shell"]`，绑定包携带 `x: ["shell"]`。
- 升级已有的无 shell 绑定包：无法就地翻转——需铸造新的 `--enable-shell` 绑定包，`starchild login` 它，然后 `cli-revoke` 旧的。权限升级始终通过新发行完成。

### 代理预先获知的信息（能力清单）

连接时，守护进程发送一个 `hello` 帧，公布：

- **平台** — `os`（darwin/linux）、`arch`（arm64/amd64）以及当前活动的 `shell`。这让代理知道它与 BSD 还是 GNU 用户态交互、应假设哪个包管理器等——不再需要猜测 `ps` 参数或遭遇 `ps: illegal option`。
- **策略摘要** — `mode`（无 allow 规则时为 `default-deny`，否则为 `allowlist`）、用户的 `allowed` 规则、显式的 `denied_extra` 规则，以及始终生效的 `builtin_denied` 列表。
- **文件传输策略** — `transfer_dir`（始终允许的共享工作区）、`yolo` 标志，以及来自 `~/.config/starchild/file-policy.toml` 的 `read_allow` / `write_allow` glob。仅当绑定包携带 `files` 能力时出现。完整规则见下方"文件路径策略"；此条目仅为让代理知道该笔记本已公布了文件传输。

clawd 将此渲染到代理的系统提示中（仅在连接时），使代理选择被许可的命令——或明确告知用户本地策略禁止该操作——而不是盲目探测。

### 会话行为

- **连接级 cwd。** 每条命令执行后的工作目录会通过回显（通过从 stdout 中去除末尾的 `pwd` 哨兵值）返回，并为下一条命令持久化，使 `cd` 在会话内的多次调用中具有实际意义——而无完整 PTY 的代价/脆弱性。显式的每次调用 cwd 可覆盖它。
- **输出截断。** stdout/stderr 各上限 200 行（外加字节上限），防止 `find /` 或日志转储淹没 LLM 上下文。截断前的完整行数会被报告（`stdout_lines` / `stderr_lines`），并设置 `truncated: true`——代理可以说"显示前 200 / N 行"而非静默截断。
- **心跳。** 守护进程每 45 秒发送 ping 以保持空闲 WebSocket 存活（Fly 边缘在约 2.5 分钟时切断空闲套接字）。Exec 在 goroutine 中运行，因此长时间命令不会阻塞心跳。

### 本地执行策略（唯一的自动运行守卫）

守护进程无头运行（无 TTY 用于提示），因此每条命令都由 `~/.config/starchild/exec-policy.toml` 门控（解析为小型 YAML `allow:`/`deny:` 行格式——尽管文件名含 .toml，但无 TOML 依赖）。规则默认为**子串**匹配；用 `/ /` 包裹规则可变为正则：

```yaml
allow:
  - "ls"
  - "cat "
  - "/^git (status|log|diff)/"
  - "ps"
deny:
  - "git push"
```

判定顺序：**内置 deny（始终优先）→ 文件 `deny` → 文件 `allow` → 默认拒绝。** 无论文件内容如何，有两条硬性规则：

- 内置 deny 列表中的交互式/TTY 阻塞和破坏性命令**始终**被拒绝：`vim`/`vi`/`nano`/`emacs`、`less`/`more`/`man`、`top`/`htop`/`btop`、`ssh`/`telnet`、`sudo`/`su`/`doas`、`tmux`/`screen`、`reboot`/`shutdown`/`halt`，以及 `rm -rf`、`mkfs`、`dd if=`、`… | sh`、`… | bash`、`> /dev/sd*` 等形式。
- **默认拒绝：** 未被任何 `allow` 规则匹配的内容一律拒绝。因此无策略文件时策略 `mode` 为 `default-deny`，用户未显式放行前什么都不会执行。

### 限制

- **仅无人值守策略。** 无交互式审批提示；策略文件是唯一守卫。未来版本将增加 Web 审批弹窗。
- **仅同步命令。** 暂不支持后台任务 / 进度轮询。
- **仅 macOS/Linux。** 守护进程拒绝在 Windows 上运行。
- **撤销：** `cli-revoke <sc_…>` 撤销短代码；守护进程下次重连时认证失败，通道关闭。

## 通过 `agent-shell` 进行文件传输（CLI ≥ v0.3.0）

当绑定包使用 `--enable-files` 铸造时，同一个 `agent-shell` 守护进程还提供用户机器与代理工作区之间的**文件传输**。内容以磁盘→磁盘流式传输，绝不经过聊天，因此**大/二进制文件（10MB+ 的 PDF、图片、归档）均可正常工作**。

三个代理侧工具 + 一个用户命令：
- `request_upload(laptop_path)` — 代理从笔记本拉取文件到 `workspace/uploads/`（"帮我取 ~/big.pdf 并总结"）。
- `write_local_file(src, dst)` — 代理将工作区文件发送到笔记本（"把 workspace/output/report.pdf 存到我的 ~/Downloads"）。`src` 是工作区路径，非内联内容。
- `read_local_file(path)` — 读取**小型文本**文件供代理查看（配置/日志片段）。大/二进制文件通过 `request_upload` 处理。
- `starchild push <file>` — 用户主动上传本地文件到代理的 `workspace/uploads/`；会在其提示中通知代理。

```bash
python3 skills/cli-bridge/scripts/cli_login.py --label "laptop" --enable-files
# 如需同时启用 shell：
python3 skills/cli-bridge/scripts/cli_login.py --label "laptop" --enable-shell --enable-files
```

`files` 是**独立于** `shell` 的能力——绑定包可以仅有其一、两者兼有、或两者皆无。与 shell 相同，默认关闭，且在 AKM 上具有权威性（clawd 拒绝无此能力的连接的传输帧）。

### 文件路径策略（笔记本侧，分层）

传输由笔记本侧的路径策略门控，从最严格开始：

1. **内置保护路径始终被拒绝**（即使在 `--yolo` 下）：`~/.ssh`、`~/.aws`、shell rc（`.zshrc`/`.bashrc`/…）、`.config/starchild`、launchd/systemd/cron、`.git/hooks`、浏览器 cookie 存储、`.env`、ssh 密钥。写入这些将导致持久 RCE；读取它们会泄露凭据。
2. **专用传输目录**（`~/starchild-transfer`，自动创建）— 始终允许读 + 写。安全默认工作区；优先使用。
3. **该目录之外** — 拒绝，除非路径匹配 `~/.config/starchild/file-policy.toml` 中的 `read_allow` / `write_allow` glob，**或**守护进程以 `--yolo` 启动：

   ```bash
   starchild agent-shell --yolo   # 允许任意路径（内置 deny 仍生效）
   ```

   ```yaml
   # ~/.config/starchild/file-policy.toml  (YAML allow-globs)
   read_allow:
     - "~/Documents/*.md"
   write_allow:
     - "~/exports/*.csv"
   ```

其他保证：写入文件权限为 **0644**（绝不可执行）；写入是原子的（临时文件 + rename，无半写目标）；逃离传输目录的符号链接被拒绝；每次传输上限 100 MiB，分块流式传输以防止大文件超出 WS 帧限制。

> **安全提示：** 正在运行的 `agent-shell`（配合 `--enable-shell` 绑定包）加上宽松策略，实质上等价于在用户机器上的远程命令执行，受限于 AKM TTL、`sc_…` 代码有效性和策略文件。默认值保守：shell **关闭**除非显式授予，策略**全拒绝**直到命令被放行，守护进程自检更新在替换二进制前验证 **Ed25519 签名**。有意再放宽。

## 通过 `agent-shell` 使用本地 MCP 服务器（CLI ≥ v0.5.32）

`agent-shell` **就是**用户机器的 MCP Host。运行 `local_shell` 和文件传输的同一守护进程还读取 `~/.config/starchild/mcp-servers.toml`，将每个已启用的 stdio MCP 服务器作为长生命周期子进程启动，执行 MCP `initialize` → `tools/list` 握手，并通过现有 WebSocket 代理 `tools/call` 到 clawd。clawd 然后将每个远程工具注册为 `mcp__<server>__<tool>` 并注入到**当前**对话中——无需新会话。

这是从云端代理驱动本地应用（Blender、Godot、本地 Figma-bridge、computer-use、browser-use、文件系统服务器等）的路径。代理无法通过其他方式访问用户机器上的 `localhost`；clawd 自身的（直接）MCP 支持是为托管在别处的 REMOTE/HTTP/SSE 服务器设计的，而非必须运行在用户笔记本上的进程。

### 工作原理（控制通道与 local_shell 使用同一个 WS）

```
clawd (云端代理)
  │  mcp_list / mcp_call 帧
  │  (通过现有 /ws/cli-shell WebSocket)
  ▼
agent-shell 守护进程 (笔记本) ── MCPProxy
  │  stdio JSON-RPC (换行分隔)
  ▼
blender-mcp / figma-mcp / server-everything / … (每个服务器一个进程)
```

笔记本侧拥有 MCP 会话状态（initialize → initialized → tools/list，有缓存）。clawd 仅发送高层 `mcp_call`；绝不直接说 JSON-RPC。服务器发出的 `tools/list_changed` 通知会重新获取并重新注册该服务器的工具。

### 配置服务器

编辑 `~/.config/starchild/mcp-servers.toml`（YAML，尽管扩展名为 `.toml`——与 exec/file-policy 同一约定）。每个条目：

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

**仅绝对路径。** `$HOME` 和 `~` 不会被展开——MCP 客户端直接生成命令，不经过 shell。使用 `/Users/<name>/...`，绝不用 `~/...` 或 `$HOME/...`。

`enabled` 默认为 `true`（无 `enabled:` 字段的条目会运行）。文件支持热重载，但**运行中的会话仅在守护进程重启时变更**——重载更新解析后的配置，不会在会话中途启动/终止服务器进程。应用的设置面板会写入此文件并为你重启 `agent-shell`。

### 重启 agent-shell 不会中断聊天

聊天流（你给用户的回复）走的是 clawd 的 HTTP/SSE 路径，而非 `agent-shell`。重启 `agent-shell` 仅中断 `local_shell` / 文件传输 / `mcp_call` 约 2 秒（重连时间）——对话本身保持存活。因此你**可以**告诉用户（或通过 `local_shell` 自行执行）在配置变更后重启守护进程；不会杀死对话。

重启后，守护进程发送新的 `hello` 附带 `mcp_manifest`，列出已启用服务器及各自的运行时状态（`ready`/`failed`/`not_started`）。clawd 对每个 ready 的服务器执行 `mcp_list` 并注册工具。每轮的 `maybe_resync_local_mcp` 追赶逻辑也覆盖在 hello 时未成功获取的服务器（例如启动慢的服务器），在后续轮次中生效。

### 动态注入 — `local_mcp_status` + `local_mcp_reload`

无需重启 agent-shell 即可拾取配置编辑。两个代理侧工具实时驱动本地 MCP 运行时：

- **`local_mcp_status`** — 返回每个已配置服务器的运行时状态（`ready` 附工具数、`failed` 附错误、或 `not_started`）。当预期的 `mcp__<server>__*` 工具缺失时调用——服务器可能启动失败。
- **`local_mcp_reload`** — 请求 agent-shell 在运行时重新读取 `mcp-servers.toml`，启动新添加的服务器，停止已移除的。**无需守护进程重启，无聊天中断。** 重载后，新添加服务器的 `mcp__<server>__*` 工具在**下一轮**出现（工具列表每次请求时重建）。编辑配置后使用此工具让新服务器可用，无需让用户重启任何东西。

当用户刚配置的服务器未显示工具时的典型流程：
1. 调用 `local_mcp_status` → 看到 `blender: not_started` 或 `failed: …`。
2. （若 `failed`，修复配置——路径错误、缺少依赖等。）
3. 调用 `local_mcp_reload` → agent-shell 启动新服务器。
4. 下一轮，`mcp__blender__*` 工具被注册。

### 代理看到的

- **工具**以 `mcp__<server>__<tool>` 形式出现（如 `mcp__blender__get_scene`、`mcp__everything__echo`）。其 `description` 和 `input_schema` 来自服务器自身的 `tools/list`——像任何原生工具一样调用。
- **提示清单**（`build_mcp_manifest_section`，在易变尾部）列出哪些本地 MCP 服务器已连接及其工具名清单。若服务器已配置但启动失败，也会在此注明（配置存在，未加载）。
- 若看不到预期的 `mcp__<server>__*` 工具，说明服务器未启动。按以下顺序诊断：
  1. 它是否在 `~/.config/starchild/mcp-servers.toml` 中且 `enabled: true`？
  2. `agent-shell` 是否在编辑**之后**重启了？（配置在启动时读取）
  3. 守护进程日志（`~/.starchild/sc-chatroom[-dev]/cli-shell/agent.log`）每个服务器有一行：成功为 `agent-shell: mcp: <id> ready (N tools)`，失败为 `agent-shell: mcp: failed to start <id>: <reason>`。通过 `local_shell` 读取。
  4. 对于需要本地应用桥接的服务器（Blender 的 addon 在 `127.0.0.1:9876`、Figma 插件等），确认该桥接也在运行——MCP 服务器进程可以启动，但其工具在后端应用可达之前会报错。

### 不要绕过 MCP 直接访问本地应用

当类似 Blender 的服务器注册缓慢时，很容易想直接打开到应用桥接（`127.0.0.1:9876`）的原始套接字并发送 Python。不要——那绕过了 MCP 工具层（无 schema、无策略、无逐调用验证），代理将失去结构化的 `mcp__blender__*` 接口。应修复 MCP 服务器的启动（查看日志、确认桥接、重启 `agent-shell`）。原始桥接仅作最后手段的回退。

### 服务器注意事项（按后端）

- **Blender MCP**（`blender-mcp`）：两部分——stdio MCP 服务器（`uv run`）和 Blender addon 的桥接（监听 `127.0.0.1:9876`）。两者都必须运行。即使 Blender 关闭，MCP 服务器也会启动，但每个工具调用在 addon 桥接上线前都会报错。即使 Blender.app 已打开，`which blender` 也常失败——没关系，桥接才是关键。
- **Figma**：有两种不同的 Figma MCP。`figma-mcp-server`（REST 封装、只读画布）通过 `bunx` 在本地运行；官方 Figma 远程 MCP（写画布、SSE）是远程服务器——在 clawd 侧配置（agent.yaml 中的 `mcp_servers:`），而非此处。此文件仅用于运行在笔记本上的服务器。
- **computer-use / browser-use**：本质上是本地的（驱动用户的屏幕/浏览器）。在此处配置。

### 安全

本地 MCP 服务器可在用户机器上执行任意代码（Blender 的 `execute_code`、shell 服务器等）。向 `mcp-servers.toml` 添加条目应与放宽执行策略同等重视：仅添加用户要求的服务器，优先选择只读服务器，绝不在聊天中放入密钥（API key）——使用 `env:` 字段。`mcp-servers.toml` 路径默认不在文件策略允许列表中；若用户希望代理直接写入配置，请将其加入。

## 端到端冒烟测试

```bash
# 1. 在代理聊天中：
@agent give me a cli key for my laptop
# → 输出 `starchild login starchild_<base64>`（绑定包含 sc_… 代码）

# 2. 在笔记本上：
starchild login starchild_xxx
starchild whoami
starchild "hello, who are you?"
# → starchild 向 sc-chatroom 发送 Bearer sc_…；sc-chatroom 解析
# → 为 AKM + container_id 并转发到用户的 clawd

# 3. 从聊天中撤销短代码：
@agent revoke cli code sc_xxxxxxxx

# 4. 下次 CLI 调用应在网关失败：
starchild "hello?"
# → "gateway rejected (401) — code may be revoked; ask your agent for a fresh CLI bundle"
```

## 管道 / shell 组合（CLI ≥ v0.1.0）

配对完成后，`starchild` 支持管道。无位置参数提示时读取 stdin，将助手回复写入 stdout，诊断信息发送到 stderr——因此可与任何 Unix 工具组合。

```bash
# stdin → 回复
echo "explain monads in 3 lines" | starchild

# 回复 → 下游
starchild "what is the OWASP top 10?" | pbcopy

# 完整三段管道，带流式输出
( echo "summarize this README:"; cat README.md ) | starchild --stream | tee summary.md

# 代码审查模式 — 上游拼接上下文 + 问题
( echo "review this diff, flag risky changes:"; git diff ) | starchild
```

**陷阱：** 传入位置参数提示时，stdin 被**忽略**。若需同时发送上下文和指令，在上游用 `( echo "<question>"; cat <file> )` 拼接，而非依赖 `cat <file> | starchild "<question>"`（后者会静默丢弃文件内容）。

## SOUL.md 提示（推荐）

在代理的 SOUL.md 中添加以下内容，使 LLM 在用户请求 CLI 密钥时选择正确的工具：

```markdown
## 为用户自己的 bots/脚本发行 CLI 绑定包

当用户说"给我个 cli key" / "创建一个 starchild bundle" /
"让我从终端跟你聊天"时，运行：

  python3 skills/cli-bridge/scripts/cli_login.py --label "<推断>"

这只是聊天桥接——它**不能**让你在他们的机器上运行命令或访问他们的文件。两个独立的可选能力，各授予本地访问权限——仅在用户明确要求时添加：

- `--enable-shell` → 运行命令（"在我的笔记本上运行命令"、"用
  agent-shell"、"整理我的 Downloads"）。远程命令执行。
- `--enable-files` → 读写文件（"把这个存到我的笔记本"、"读我的
  ~/notes.md"）。在其机器上读写文件。

  python3 skills/cli-bridge/scripts/cli_login.py --label "<推断>" --enable-shell
  python3 skills/cli-bridge/scripts/cli_login.py --label "<推断>" --enable-files

将两者都视为授予其机器访问权限——绝不默认添加或"为了帮忙"而添加。
若用户日后想要某能力，带该标志铸造新绑定包并让他们撤销旧的。

若用户未建议标签，默认使用类似 "untitled-YYYY-MM-DD"。展示生成的
绑定包并告诉他们如何撤销：用 `cli-list` 查找代码，然后 `cli-revoke sc_…`。

配对后，告知他们还可以从 shell 管道输入 CLI——例如 `echo "..." | starchild`、
`starchild "..." | pbcopy`，或 `( echo "review:"; git diff ) | starchild`。
Stdout 是回复（管道安全），stderr 是诊断。注意陷阱：传入位置参数
会使 stdin 被忽略，因此上下文 + 问题应在上游拼接。

## 通过 MCP 驱动本地应用（agent-shell ≥ v0.5.32）

一旦授予 `--enable-shell` 且 `agent-shell` 正在运行，你还可以通过
stdio MCP 服务器驱动本地应用（Blender、Godot、本地 Figma-bridge、
computer-use 等）。agent-shell 守护进程就是 MCP Host：它读取
`~/.config/starchild/mcp-servers.toml`，启动服务器，并将它们的工具注册为
`mcp__<server>__<tool>` 注入此对话。无需单独的 MCP 客户端
（Cursor/Claude Desktop）。

当用户说"控制 Blender" / "用本地 figma 插件" /
"通过 MCP 驱动我的本地 <app>"：
- 确认 `agent-shell` 已连接（`local_shell` 调用正常）。
- 将服务器添加到 `~/.config/starchild/mcp-servers.toml`（仅绝对
  路径——无 `$HOME`，无 `~`）。应用的设置 → 本地 MCP 服务器面板
  也可以做到。
- 重启 `agent-shell`（`starchild agent-shell-stop && starchild
  agent-shell`，或通过应用的 RestartBanner）。这不会中断聊天
  ——仅 `local_shell`/文件传输暂停约 2 秒。
- 重启后 `mcp__<server>__*` 工具出现。若未出现，
  读取守护进程日志（`~/.starchild/sc-chatroom[-dev]/cli-shell/
  agent.log`——查找 `mcp: <id> ready` 或 `mcp: failed to start
  <id>: <reason>`）通过 `local_shell`。
- 对于有本地应用桥接的服务器（Blender addon 在
  127.0.0.1:9876），确认该桥接也在运行——MCP 服务器
  进程可以启动，但工具在后端应用上线前会报错。
- 优先使用 `mcp__<server>__*` 工具而非打开到应用桥接的原始
  套接字。MCP 层提供 schema + 验证；原始桥接仅最后手段回退。

不要添加用户未要求的服务器——本地 MCP 服务器可在其机器上
执行任意代码。完整配置格式和按后端的注意事项（Blender 两部分、
Figma 本地 vs 远程等）见上方"通过 agent-shell 使用本地 MCP 服务器"
章节。
```
