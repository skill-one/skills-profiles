# 1Password 命令行界面

请遵循官方 CLI 入门步骤。不要猜测安装命令。

## 参考

- `references/get-started.md` (安装 + 应用集成 + 登录流程)
- `references/cli-examples.md` (真实的 `op` 示例)

## 工作流程

1. 检查操作系统 + shell。
2. 验证 CLI 是否存在：`op --version`。
3. 检测用户设置的认证模式：
   - **服务账户：** `OP_SERVICE_ACCOUNT_TOKEN` 被设置（适用于无头设置、CI、网关）。
   - **桌面应用集成：** 1Password 桌面应用正在运行且启用了 CLI 集成（适用于 macOS / Windows / Linux 桌面）。
   - **独立登录：** 以上均不满足 — `op signin` 每次会提示输入账户密码。
4. 根据认证模式运行 `op`（见下文）。
5. 验证访问权限：在读取任何密钥之前，`op whoami` 应成功。
6. 如果有多个账户：使用 `--account` 或 `OP_ACCOUNT`。

## 按认证模式运行 `op`

### 服务账户（推荐用于无头 / 网关使用）

直接执行。无需 tmux，无需登录步骤。

```bash
export OP_SERVICE_ACCOUNT_TOKEN="ops_..."
op vault list
op read op://app-prod/db/password
```

### 桌面应用集成

直接执行。**不要用 tmux 包裹** — 桌面应用集成使用的是每个用户的 IPC 通道，该通道为网关的执行环境建立，但并非总是可靠地从 tmux 子 shell 中可达，子 shell 运行在不同的环境上下文中。传输方式因平台而异（macOS 通过 1Password 浏览器助手使用 XPC，Linux 使用 Unix 域套接字，Windows 使用命名管道）；对代理的实际规则在所有三个平台上都相同：直接运行 `op`。在 macOS 上，一个有用的症状指示器是 1Password 集成组容器位于 `~/Library/Group Containers/2BUA8C4S2C.com.1password/t/`。

```bash
op vault list      # 第一次调用可能会触发 Touch ID / Windows Hello / 系统认证
op whoami
```

如果调用返回 `1Password CLI 无法连接到 1Password 桌面应用`，不要切换到 tmux。确认桌面应用正在运行且已解锁，然后重试直接执行。

### 独立登录（无应用，交互式密码）

这是唯一 tmux 有帮助的模式。`op signin` 会打印类似 `eval` 的导出设置，为 POSIX shell 设置 `OP_SESSION_*` 令牌；同一 shell 中的后续命令通过该环境变量进行认证。网关的每个命令 shell 在调用之间会丢失该状态，因此一个持久的 tmux 窗口会保持会话令牌活跃 — 但前提是使用 `eval` 在 POSIX shell 中实际应用了导出。将 `op signin` 作为普通命令发送会将 stdout 打印到窗口中，`op whoami` 将会失败。

tmux 流程仅在 macOS/Linux 主机上可用，且 `tmux` 技能可用时才可操作。示例故意打开 `/bin/sh`，以便 POSIX `eval "$(op signin ...)"` 输出即使在用户正常 shell 为 fish 时也有效。在 Windows 上，优先使用桌面应用集成或服务账户认证。如果用户在 Windows 上只有独立交互式登录，停止并要求他们提供持久的 PowerShell 会话机制或切换到桌面集成/服务账户认证；不要直接翻译 tmux 命令。

```bash
SOCKET_DIR="${OPENCLAW_TMUX_SOCKET_DIR:-${TMPDIR:-/tmp}/openclaw-tmux-sockets}"
mkdir -p "$SOCKET_DIR"
chmod 700 "$SOCKET_DIR"
SOCKET="$SOCKET_DIR/openclaw-op.sock"
SESSION="op-auth-$(date +%Y%m%d-%H%M%S)"

tmux -S "$SOCKET" new -d -s "$SESSION" -n shell /bin/sh
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- 'eval "$(op signin --account my.1password.com)"' Enter
tmux -S "$SOCKET" capture-pane -t "$SESSION":0.0 -p -S - | tail -40
```

登录提示时不要排队后续命令。使用 `capture-pane` 检查窗口，直到登录完成且 shell 提示符返回，或者明显正在等待用户输入。如果提示符需要密码、MFA 或账户选择，暂停并要求用户在自己的终端中完成登录；给他们提供套接字和会话值，以便他们本地连接。代理不应从执行中运行 `tmux attach`，因为 `attach` 会消耗当前 TTY 并阻止脚本化的 `send-keys` / `capture-pane` 控制。

shell 提示符返回后，通过将检查发送到同一窗口来验证：

```bash
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- 'op whoami' Enter
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- 'op vault list' Enter
tmux -S "$SOCKET" capture-pane -t "$SESSION":0.0 -p -S - | tail -80
```

保持 tmux 会话运行，以便后续的 `op read` / `op run` 命令重用相同的已认证 shell。

在此独立登录流程中，对每个后续命令使用相同的 `SOCKET` 和 `SESSION` 值。`-S "$SOCKET"` 标志选择 tmux 服务器套接字；将其保存在用户拥有的 `0700` 目录中，不要在用户之间共享，并为每个新的登录尝试选择一个新的会话名称。

## 浏览器登录（1Password for Claude）

如果会话在 Chrome 凭据工具中暴露 Claude (`request_credentials`, `autofill_credential`, `enter_verification_code`)，优先使用它们而不是 `op` 登录网站：1Password 直接填充页面，密钥永远不会进入上下文。规则：

- 在导航之前，通过一次 `request_credentials` 调用请求任务所需的每个凭据。
- 授权是在网关主机上的 1Password 提示。如果它保持挂起状态，告诉用户在哪个主机上解锁（"1Password 正在等待此 Mac 的授权"）而不是重试。
- 不要通过聊天发送密码或一次性代码；代码仅通过 `enter_verification_code` 传输。
- 不要因为浏览器流程需要授权就回退到 `op read` 来获取网站密码；那会破坏无暴露设计。使用 `op` 来获取命令和配置消耗的密钥，而不是在存在浏览器流程时的网页登录。

## 安全约束

- 不要将密钥粘贴到日志、聊天或代码中。
- 优先使用 `op run` / `op inject` 而不是将密钥写入磁盘。
- 如果需要无应用集成登录，请先使用 `op account add`。
- 如果命令返回 "账户未登录"：
  - 服务账户：重新导出 `OP_SERVICE_ACCOUNT_TOKEN`
  - 桌面应用：确认应用正在运行且集成已启用
  - 独立：在同一 tmux 会话中重新运行 `op signin` 并授权
