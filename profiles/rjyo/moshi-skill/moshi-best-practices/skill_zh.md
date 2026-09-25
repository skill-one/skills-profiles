# Moshi 最佳实践

使用此技巧使任何主机都感觉从 Moshi 使用起来很方便。

用于以下情况：

- 新建配置
- 验证现有配置

Moshi 将 **Herdr、tmux 和 Zellij** 视为一流的多路复用器。Herdr 支持在 iOS 3.1 中落地；以下工作流功能假定 **3.10 或更高版本**。对于代理工作，优先使用 **Herdr**：跳转、聊天视图、代理收件箱、深度链接、两指会话/空间/面板滑动以及打开终端都更干净地落在 Herdr 工作空间和代理选项卡上。即使在以 Herdr 为主的主机上，也要保留 **tmux** 的安装——打包的 `moshi DIR` 启动器和 Moshi 的最近目录一键流程仍然创建 tmux 会话。如果用户已经运行 Zellij，则支持 Zellij。

## 规则

- 在编辑前检查。
- 优先选择直接配置编辑，而不是平台特定的设置脚本。
- 更改后验证每个结果。
- 不要安装旧的 `moshi` shell 帮助程序或别名。当前安装暴露相同的二进制文件作为 `moshi`（`moshi-hook` 的便利别名）。
- 对于编码代理会话，优先使用 **Herdr** 而不是 tmux。仍然保留 tmux 的安装：`moshi DIR` 启动器和 Moshi 的最近目录一键会话都创建 tmux。当无法安装 Herdr 或用户已经在 tmux 中并希望继续使用时，默认使用 tmux 仅模式。
- 在 Herdr 主机上，`moshi-hook` 必须成对使用，并且必须运行 `moshi-hook install`。与 tmux 不同，Herdr 没有用于代理提示的屏幕抓取回退——钩子是唯一的提示源。

## 1. 主机就绪

对于新的 Moshi SSH/Mosh 设置，当 `moshi-hook` 可用时，优先使用 **Easy Pair**：

```bash
moshi-hook host setup
# 或: moshi host setup
```

告诉用户扫描 Moshi 上的 Easy Pair QR 码。这会创建保存的主机连接，生成手机端的私钥，并在主机上安装 Moshi 的公钥。强调安全边界：在 QR 码过期之前扫描它的人可以声明对主机的 SSH 访问权限，因此他们不应共享屏幕或设置链接。

不要将 Easy Pair 与 `moshi-hook pair --token` 混淆；令牌配对仅用于代理钩子、收件箱、Live Activities 和 Apple Watch 事件。

目标结果：

- 优先传输是 **Mosh** 加上多路复用器；备用是 SSH（在 Pro 可用时为 Eternal Terminal）加上多路复用器
- 主机有一个可工作的 SSH 入口点
- **Herdr 已安装**（首选）并且 **tmux 保持安装** 以用于启动器 / 最近项目流程；如果已经存在，Zellij 也可以
- 当用户想要 Mosh 时，安装 `mosh-server`
- 二进制文件在当前 shell 中解析，并且在登录 shell 的非交互模式下解析
- 至少存在一个多路复用器会话，以便 Moshi 会话选择器可以出现
- 当 Herdr 是选择的多路复用器时，`moshi-hook` 已成对使用并且钩子已安装

使用一小组实际检查进行检查。保持特定于 OS 的机制最小，但不要跳过验证。

有用的检查：

```bash
command -v herdr || true
command -v tmux || true
command -v zellij || true
command -v mosh-server || true
herdr session list --json 2>/dev/null || true
tmux list-sessions 2>/dev/null || true
LOGIN_SHELL="${SHELL:-/bin/sh}"
"$LOGIN_SHELL" -c 'command -v herdr'
"$LOGIN_SHELL" -c 'command -v tmux'
"$LOGIN_SHELL" -c 'command -v mosh-server'
```

当相关时，有用的 macOS 特定检查：

```bash
dscl . -read "/Users/$USER" UserShell
systemsetup -getremotelogin || true
```

更改后验证：

```bash
command -v herdr || command -v tmux
herdr session list --json 2>/dev/null || tmux list-sessions
"$LOGIN_SHELL" -c 'command -v herdr || command -v tmux'
"$LOGIN_SHELL" -c 'command -v mosh-server' || true
moshi-hook status || true   # 人类输出报告解析的 tmux/zellij/herdr 二进制文件；保留 stderr
```

然后要求用户从 Moshi 重新连接。预期结果：多路复用器选择器出现（Herdr 会话/工作空间和/或 tmux 会话），并且当配置为使用时，传输可以使用 Mosh 而不是纯 SSH。

## 2. 多路复用器：优先 Herdr

Herdr 是一个以代理为先的终端多路复用器。Moshi 对其提供一流的支持（会话卡片、工作空间选择器、带有代理图标的选项卡上的跳转、聊天视图、深度链接、滑动切换选项卡/空间/面板、滚动到底部、鼠标模式、代理收件箱重用打开的 Herdr 会话以及打开终端落在事件对应的 Herdr 选项卡上）。

**前提条件：** Herdr 在 Moshi 中的代理功能取决于 `moshi-hook` 已成对使用并且已运行 `moshi-hook install`。与 tmux 不同，Herdr 上没有用于代理提示的屏幕抓取回退——钩子捕获是唯一的提示源。

### 安装

```bash
curl -fsSL https://herdr.dev/install.sh | sh
# 或: brew install herdr
# 或: mise use -g herdr
```

验证：

```bash
command -v herdr
herdr --version
"$LOGIN_SHELL" -c 'command -v herdr'
```

守护进程从 PATH、Nix 配置文件目录、`~/.local/bin`、`/opt/homebrew/bin` 和 `/usr/local/bin` 解析 `herdr`。仅当安装非标准（Nix、自定义前缀）时设置覆盖：

```bash
# Linux: 将其放在 systemd 用户单元中
systemctl --user edit moshi-hook    # Environment=MOSHI_HERDR_PATH=/path/to/herdr
systemctl --user restart moshi-hook.service

# macOS: 将 MOSHI_HERDR_PATH 添加到 brew services plist，然后
brew services restart moshi-hook
```

使用 `moshi-hook status` 确认——其人类输出报告守护进程可以解析的 tmux、Zellij 和 Herdr 二进制文件（`--json` 会省略此诊断）。

### 启动项目会话

在包含工作的位置启动 Herdr：

```bash
cd ~/projects/app
herdr
```

对于编码代理的推荐布局（工作空间/选项卡，而不是固定的窗口名称）：

1. 在主机上保留 **一个 Herdr 会话**，每个项目 **一个工作空间**——当运行单个 Herdr 会话时，Moshi 仅在直接附加时显示工作空间
2. 选项卡用于主要代理、审查、测试、服务器和杂项
3. 让 Herdr 检测面板中的代理；在有用时安装匹配的集成：

```bash
herdr integration install claude
herdr integration install codex
# herdr integration install --help  # 完整目标列表
# herdr integration status
```

仅在主机确实需要一个以上时使用命名的会话（Moshi 然后显示会话列表而不是工作空间选择器）：

```bash
herdr --session app
```

Herdr 自己的集成和 `moshi-hook install` 都会写入代理钩子配置（例如写入 `~/.claude/settings.json`）。它们是非破坏性的，并且旨在共存——在使用 Herdr 与 Moshi 时运行两者。

在人类设置完成后，提供 Herdr 代理技能，以便会话中的代理可以驱动面板：

```bash
npx skills add ogulcancelik/herdr --skill herdr -g
```

使用 Herdr 的默认值（除非重新映射；Moshi 也暴露可配置的 Herdr 前缀，包括 Opt/Alt 修饰符）使用 `Ctrl+b q` 分离。使用 `herdr` 或 `herdr --session <name>` 重新连接。

然后要求用户从 Moshi 重新连接。预期结果：Herdr 会话出现在选择器中；如果主机只有一个会话，Moshi 可以直接附加工作空间。

### 为什么 Herdr 比 tmux 更适合 Moshi 代理

| Moshi 中的功能 | Herdr | tmux |
|---|---|---|
| 会话 / 空间 / 面板滑动 + 跳转 | 工作空间、选项卡、代理感知标签 | 窗口 / 面板 |
| 代理收件箱 → 打开终端 | 重用会话，聚焦工作空间 + 代理选项卡 | 附加会话 / 窗口 |
| 聊天视图 / 批准 / 图片粘贴 | 通过 `herdr` CLI 的完整桥接（需要钩子） | 通过 `tmux` 的完整桥接（钩子首选；存在屏幕/标题回退） |
| 代理感知 TUI | 内置代理生命周期 + 技能 | 通用面板 |
| 打包的单次项目启动器 | 在项目目录中启动 `herdr` | `moshi DIR` → tmux 会话 |
| 应用中的最近目录一键 | — | 创建一个 tmux 会话 |

默认建议：安装 Herdr 并将用户的代理工作放在那里，**并且保留 tmux 安装** 以用于 `moshi DIR` 启动器和最近目录一键会话。

## 3. tmux 回退

当 Herdr 不可用或用户更喜欢时，使用 tmux 作为主要的多路复用器。即使在以 Herdr 为主的主机上，也要保留 tmux 的安装以用于打包的启动器和最近目录流程。

### 默认值

除非用户想要不同：

```tmux
set -g history-limit 100000
set -g mouse on
set -g set-titles on
set -g set-titles-string "#I: #W"
set -g base-index 1
setw -g pane-base-index 1
set -g renumber-windows on
```

工作流：

- 检查现有的 tmux 配置
- 更新重叠的设置而不是追加重复的设置
- 编辑后重新加载 tmux

### 项目会话（`moshi DIR`）

当 `moshi-hook` 从 Homebrew 或 `install.sh` 安装时，打包的启动器仍然针对 **tmux**：

```bash
moshi .
moshi ~/projects/app
```

它从目录的基本名称解析目录并命名 tmux 会话（基本名称中的 `:` 变成 `_`）。在 tmux 外部它 `exec`s `tmux new-session -A -s <name> -c <dir>`（没有 Moshi 包装器保持活动）。当已经在 tmux 中时，如果需要，它会创建分离的会话并 `switch-client` 到它而不是 `exec`。

手动创建新会话时：

- 读取当前工作目录
- 问一个简洁的问题：会话应从这里开始吗？
- 如果答案是否定的，请输入目录
- 将会话名称默认为目录的基本名称
- 创建分离的会话
- 使用选择的目录为每个初始窗口使用 `tmux ... -c <dir>`

推荐的窗口：

1. `agent`
2. `review`
3. `tests`
4. `servers`
5. `misc`

然后要求用户从 Moshi 重新连接。预期结果：会话在 tmux 选择器中可见。

### 企业 Linux 10 注意事项

一些 RHEL/Alma/Rocky 10 `tmux-3.3a-12` 通过 `3.3a-14` RPM 可以在 `capture-pane` 时损坏服务器。不要单独信任 `tmux -V`（受影响的构建可以报告 `next-3.4`）。检查包：

```bash
rpm -q tmux
```

Moshi 在这些构建上自动禁用每个 `capture-pane` 功能而不是大声失败；基于钩子、标题和转录的状态仍然有效。在这些主机上优先使用 Herdr，或者安装上游 tmux 3.5a+ 并在替换二进制文件后重新启动 tmux 服务器。有关完整版本范围的详细信息，请参阅 `app-hook/docs/usage.md`。

## 4. MOSHI_CLIENT 信号

`MOSHI_CLIENT=1` 是 Moshi 客户端导出到远程 shell 的一个可选环境变量，以便 rc 文件、提示和多路复用器配置可以检测 Moshi 启动的会话并适应当前。用户在应用中通过 **设置 → 集成 → Shell → 导出 ENV**（默认关闭；启用需要 Pro；禁用保持免费）启用它。启用时，它在 Mosh 路径（通过 `mosh-server -l MOSHI_CLIENT=1`）和 SSH 回退（通过在 shell 启动时注入 `export`）上设置完全相同。

一个常见的用例是保持 **tmux** 状态处理在 Moshi 下可预测。Moshi 已经在它启动的会话上清除了 `status-right`，但一个自定义主题仍然可以重新填充 `status-left` / `status-right`。当 `MOSHI_CLIENT` 设置时条件清除它们，可以保持本地主题完整，同时保持 Moshi 的状态处理可预测。其他用途：更窄的提示、丢弃 nerd-font 图形符号、不同的键绑定。

Shell（在用户的 rc 文件中）：

```sh
if [ -n "$MOSHI_CLIENT" ]; then
  # 在 Moshi 下运行——修剪提示、跳过重型图形符号等
fi
```

tmux（在 `~/.tmux.conf` 中）：

```tmux
# 将变量传播到此 shell 附加的 tmux 会话中
set-option -ga update-environment " MOSHI_CLIENT"

# 当主题重新填充它们时，为 Moshi 客户端保持状态区域干净
if-shell '[ -n "$MOSHI_CLIENT" ]' {
  set -g status-left ''
  set -g status-right ''
}
```

编辑后重新加载 tmux (`tmux source-file ~/.tmux.conf`)。

在用户切换设置并从 Moshi 重新连接后验证：

```bash
echo "$MOSHI_CLIENT"                       # 预期：1
tmux show-environment | grep MOSHI_CLIENT  # 预期在新会话中（仅 tmux）有值
```

如果 `echo` 输出为空，应用中的切换是关闭的——在编辑主机配置前与用户确认。该变量仅在切换翻转后打开的会话中出现。

## 5. 代理钩子（`moshi-hook`）

Moshi 使用 `moshi-hook`（单数），一个便携式 Go 守护进程。守护进程持有一个到 Moshi 的持久 WebSocket，因此批准是**双向的**——用户可以从 iOS Live Activity 或 Apple Watch 批准或拒绝工具调用，并且答案会返回到代理。一个安装可以覆盖多个代理。

在 **Herdr** 上，本节是必需的，不是可选的：交互式提示和 Moshi 中的代理状态仅来自钩子。

支持的钩子目标（截至当前 `moshi-hook install`）：Claude Code、Codex CLI、OpenCode、Gemini CLI、Antigravity、Cursor、Kimi、Qwen Code、Grok Build、OMP（Oh My Pi）、Pi 和 Hermes Agent。Moshi Pro 中的聊天视图也显示其中几个（包括 Grok、Kimi、Pi/OMP、OpenCode、Codex），当钩子和转录健康时。

使用 `moshi-hook` / `moshi` 而不是手写的配置，除非用户明确想要手动编辑。

通过 Homebrew tap（macOS）安装，然后配对并安装钩子：

```bash
brew tap rjyo/moshi
brew install moshi-hook
moshi-hook pair --token <YOUR_TOKEN>   # 令牌来自 Moshi 移动应用
moshi-hook install                     # 为安装的代理写入钩子配置
brew services start moshi-hook         # 在重新启动时保持守护进程活动
```

Linux / 手动：

```bash
curl -fsSL https://getmoshi.app/install.sh | sh
moshi-hook pair --token <YOUR_TOKEN>
moshi-hook install
moshi-hook service install             # systemd 用户单元
```

当 Easy Pair 已经运行 `host setup` 时，守护进程通常作为该流程的一部分成对使用；仍然运行 `moshi-hook install` 以确保代理配置指向守护进程。

在 macOS 上，`moshi-hook pair` 默认使用 Keychain。如果通过 SSH 配对失败是因为 Keychain 锁定或不可用，请优先使用以下显式路径：

```bash
security unlock-keychain ~/Library/Keychains/login.keychain-db
moshi-hook pair --token <YOUR_TOKEN>
```

对于没有 Keychain 访问或不希望不可靠的头部主机：

```bash
moshi-hook pair --token <YOUR_TOKEN> --store file
```

`--store file` 将主机密钥写入 `~/.config/moshi/secrets.json`，权限为 `0600`，并记住未来的 `serve`、`status`、`usage --sync` 和 `pair` 命令的存储选择。不要无声使用它；指出这会将密钥存储在 Keychain 外部。

`moshi-hook install` 是非破坏性的——它将 Moshi 条目写入它找到的代理配置（例如 `~/.claude/settings.json`、`~/.codex/config.toml`、OpenCode 插件、Grok 钩子、Pi/OMP 扩展、Hermes 插件），保留用户拥有的钩子。除非您使用 `--target` 强制目标，否则会跳过缺失的代理。当两者都存在时，它与 `herdr integration install …` 共存。

有用的附加命令：

```bash
moshi-hook status              # 配对、套接字、WS、解析的 tmux/zellij/herdr 二进制文件
moshi-hook logs -f             # 尾随守护进程日志
moshi-hook usage --sync        # 推送 Claude / Codex / OpenCode / Kimi / Grok 使用量
moshi diff .                   # 本地 git 差分查看器（主机网关）
moshi-hook servers             # 发现本地 Web 服务器以用于应用内浏览器 / serve-sim
```

验证：

```bash
moshi-hook status
moshi-hook logs -f
```

然后运行一个简短的实时代理任务并确认 Moshi 接收推送通知或 Live Activity 更新，并且从 Live Activity / Watch 解锁代理。在 Herdr 主机上，还确认 Agents → Open Terminal 聚焦正确的 workspace/选项卡。

有关完整 CLI 参考（每个子命令、标志、环境变量和路径），请参阅 monorepo 中的 `app-hook/docs/usage.md`，或镜像文档在 [`rjyo/homebrew-moshi`](https://github.com/rjyo/homebrew-moshi) tap 中。

## 6. 快速验证清单

设置后，主机应满足：

1. Easy Pair 或 SSH 密钥工作；从 Moshi 重新连接成功
2. 当 `mosh-server` 存在时，优先使用 Mosh
3. **Herdr**（首选）、**tmux** 或 Zellij 在登录非交互式 shell 的 PATH 上——即使 Herdr 是主要的主机也要保留 tmux 安装
4. 至少存在一个 Herdr 会话/工作空间、tmux 会话或 Zellij 会话供选择器使用
5. `moshi-hook status` 显示已配对 + 连接；为使用的代理安装钩子（**当 Herdr 是选择的多路复用器时必需**）
6. 可选：仅当非标准 Herdr 安装位置无法由守护进程解析时，才使用 `MOSHI_HERDR_PATH`
7. 可选：仅当用户启用了 Export ENV（Pro）并需要 rc/tmux 适应时，才使用 `MOSHI_CLIENT`
