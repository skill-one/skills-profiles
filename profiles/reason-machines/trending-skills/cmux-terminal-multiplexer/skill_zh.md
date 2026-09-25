# cmux — AI原生终端复用器

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合

cmux 是一个具有可编程套接字API的终端复用器，专为AI编码代理设计。它提供完整的Playwright等效浏览器自动化、实时终端分割管理、侧边栏状态报告和代理团队协作 — 所有这些都通过简单的CLI实现。

---

## cmux的功能

- **终端分割** — 创建并排或堆叠的窗格，发送命令，捕获输出
- **浏览器自动化** — 完整的无头Chromium，基于快照的元素引用（无需CSS选择器）
- **状态侧边栏** — 用户可见的实时进度条、日志消息和图标徽章
- **通知** — 代理工作流中的原生操作系统通知
- **代理团队** — 协调并行子代理，每个子代理都有自己的可见分割

---

## 快速入门

```bash
cmux identify --json          # 当前窗口/工作区/窗格/表面的上下文
cmux list-panes               # 当前工作区中的所有窗格
cmux list-pane-surfaces --pane pane:1  # 窗格内的表面
cmux list-workspaces          # 当前窗口中的所有工作区（标签页）
```

环境变量会自动设置：
- `$CMUX_SURFACE_ID` — 您当前的表面引用
- `$CMUX_WORKSPACE_ID` — 您当前的工作区引用

使用简短引用：`surface:N`，`pane:N`，`workspace:N`，`window:N`。

---

## 终端分割

### 创建分割

```bash
cmux --json new-split right   # 并排（适用于并行工作）
cmux --json new-split down    # 堆叠（适用于日志）
```

始终捕获返回的 `surface_ref`：

```bash
WORKER=$(cmux --json new-split right | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
```

### 发送命令和读取输出

```bash
cmux send-surface --surface surface:22 "npm run build\n"
cmux capture-pane --surface surface:22              # 当前屏幕
cmux capture-pane --surface surface:22 --scrollback  # 带有完整历史记录

cmux send-key-surface --surface surface:22 ctrl-c  # 发送按键
cmux send-key-surface --surface surface:22 enter
```

**黄金法则：永远不要窃取焦点。** 始终使用 `--surface` 目标。

### 工作者分割模式

```bash
WORKER=$(cmux --json new-split right | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
cmux send-surface --surface "$WORKER" "make test 2>&1; echo EXIT_CODE=\$?\n"
sleep 3
cmux capture-pane --surface "$WORKER"
cmux close-surface --surface "$WORKER"   # 完成后清理
```

### 窗格管理

```bash
cmux focus-pane --pane pane:2
cmux close-surface --surface surface:22
cmux swap-pane --pane pane:1 --target-pane pane:2
cmux move-surface --surface surface:7 --pane pane:2 --focus true
cmux reorder-surface --surface surface:7 --before surface:3
```

---

## 浏览器自动化

cmux嵌入了一个完整的无头Chromium引擎，具有Playwright风格的API。无需外部Chrome。每个命令都通过引用指向浏览器表面。

### 工作流模式

```
导航 → 等待加载 → 基于快照的交互式引用 → 执行引用 → 重新快照
```

### 打开和导航

```bash
cmux --json browser open https://example.com        # 打开浏览器分割，返回表面引用
cmux browser surface:23 goto https://other.com
cmux browser surface:23 back
cmux browser surface:23 forward
cmux browser surface:23 reload
cmux browser surface:23 get url
cmux browser surface:23 get title
```

捕获表面引用：

```bash
BROWSER=$(cmux --json browser open https://docs.example.com | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
```

### 快照和元素引用

使用快照获取稳定的元素引用（`e1`，`e2`，...），而不是CSS选择器：

```bash
cmux browser surface:23 snapshot --interactive              # 完全交互式快照
cmux browser surface:23 snapshot --interactive --compact     # 紧凑输出
cmux browser surface:23 snapshot --selector "form#login" --interactive  # 范围内
```

引用在DOM变更后会失效 — 导航或点击后始终重新快照。使用 `--snapshot-after` 自动获取最新快照：

```bash
cmux --json browser surface:23 click e1 --snapshot-after
```

### 与元素交互

```bash
# 点击和悬停
cmux browser surface:23 click e1
cmux browser surface:23 dblclick e2
cmux browser surface:23 hover e3
cmux browser surface:23 focus e4

# 文本输入
cmux browser surface:23 fill e5 "hello@example.com"   # 清空并输入
cmux browser surface:23 fill e5 ""                      # 清空输入
cmux browser surface:23 type e6 "search query"          # 输入而不清空

# 按键
cmux browser surface:23 press Enter
cmux browser surface:23 press Tab
cmux browser surface:23 keydown Shift

# 表单
cmux browser surface:23 check e7          # 复选框
cmux browser surface:23 uncheck e7
cmux browser surface:23 select e8 "option-value"

# 滚动
cmux browser surface:23 scroll --dy 500
cmux browser surface:23 scroll --selector ".container" --dy 300
cmux browser surface:23 scroll-into-view e9
```

### 等待状态

```bash
cmux browser surface:23 wait --load-state complete --timeout-ms 15000
cmux browser surface:23 wait --selector "#ready" --timeout-ms 10000
cmux browser surface:23 wait --text "Success" --timeout-ms 10000
cmux browser surface:23 wait --url-contains "/dashboard" --timeout-ms 10000
cmux browser surface:23 wait --function "document.readyState === 'complete'" --timeout-ms 10000
```

### 读取页面内容

```bash
cmux browser surface:23 get text body        # 可见文本
cmux browser surface:23 get html body        # 原始HTML
cmux browser surface:23 get value "#email"   # 输入值
cmux browser surface:23 get attr "#link" --attr href
cmux browser surface:23 get count ".items"   # 元素计数
cmux browser surface:23 get box "#button"    # 边界框
cmux browser surface:23 get styles "#el" --property color

# 状态检查
cmux browser surface:23 is visible "#modal"
cmux browser surface:23 is enabled "#submit"
cmux browser surface:23 is checked "#agree"
```

### 定位器（Playwright风格）

```bash
cmux browser surface:23 find role button
cmux browser surface:23 find text "Sign In"
cmux browser surface:23 find label "Email"
cmux browser surface:23 find placeholder "Enter email"
cmux browser surface:23 find testid "submit-btn"
cmux browser surface:23 find first ".item"
cmux browser surface:23 find last ".item"
cmux browser surface:23 find nth ".item" 3
```

### JavaScript评估

```bash
cmux browser surface:23 eval "document.title"
cmux browser surface:23 eval "document.querySelectorAll('.item').length"
cmux browser surface:23 eval "window.scrollTo(0, document.body.scrollHeight)"
```

### 帧和对话框

```bash
cmux browser surface:23 frame "#iframe-selector"   # 切换到iframe
cmux browser surface:23 frame main                  # 返回主帧
cmux browser surface:23 dialog accept
cmux browser surface:23 dialog dismiss
cmux browser surface:23 dialog accept "prompt text"
```

### Cookie、存储和状态

```bash
# Cookie
cmux browser surface:23 cookies get
cmux browser surface:23 cookies set session_token "abc123"
cmux browser surface:23 cookies clear

# Local/session存储
cmux browser surface:23 storage local get
cmux browser surface:23 storage local set myKey "myValue"
cmux browser surface:23 storage session clear

# 保存/恢复完整浏览器状态（Cookie + 存储 + 标签页）
cmux browser surface:23 state save ./auth-state.json
cmux browser surface:23 state load ./auth-state.json
```

### 认证流程

```bash
BROWSER=$(cmux --json browser open https://app.example.com/login | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
cmux browser $BROWSER wait --load-state complete --timeout-ms 15000
cmux browser $BROWSER snapshot --interactive
cmux browser $BROWSER fill e1 "user@example.com"
cmux browser $BROWSER fill e2 "my-password"
cmux browser $BROWSER click e3
cmux browser $BROWSER wait --url-contains "/dashboard" --timeout-ms 20000

# 保存认证以复用
cmux browser $BROWSER state save ./auth-state.json

# 在新表面中复用
BROWSER2=$(cmux --json browser open https://app.example.com | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
cmux browser $BROWSER2 state load ./auth-state.json
cmux browser $BROWSER2 goto https://app.example.com/dashboard
```

### 诊断

```bash
cmux browser surface:23 console list     # JS控制台输出
cmux browser surface:23 console clear
cmux browser surface:23 errors list      # JS错误
cmux browser surface:23 errors clear
cmux browser surface:23 highlight "#el"  # 视觉高亮
cmux browser surface:23 screenshot       # 捕获屏幕截图
```

### 脚本和样式注入

```bash
cmux browser surface:23 addscript "console.log('injected')"
cmux browser surface:23 addstyle "body { background: red; }"
cmux browser surface:23 addinitscript "window.__injected = true"  # 每次导航时运行
```

---

## 侧边栏状态和进度

在不打断用户流程的情况下显示实时状态：

```bash
cmux set-status agent "working" --icon hammer --color "#ff9500"
cmux set-status agent "done" --icon checkmark --color "#34c759"
cmux clear-status agent

cmux set-progress 0.3 --label "Running tests..."
cmux set-progress 1.0 --label "Complete"
cmux clear-progress

cmux log "Starting build"
cmux log --level success "All tests passed"
cmux log --level error --source build "Compilation failed"
```

---

## 通知

```bash
cmux notify --title "Task Complete" --body "All tests passing"
cmux notify --title "Need Input" --subtitle "Permission" --body "Approve deployment?"
```

---

## cmux中的代理团队

使用cmux分割为每个代理队友分配一个可见的工作区。通过 `SendMessage` 和任务列表进行协调 — 永远不要通过阅读彼此的终端输出来协调。

### 模式

1. 为每个队友创建分割
2. 通过代理工具启动队友 — 将每个队友的cmux表面引用传递给他们
3. 队友通过 `cmux send-surface` 在其分割中运行命令
4. 队友通过 `cmux set-status` 和 `cmux log` 报告状态
5. 用户并排查看所有工作

### 示例：3人团队

```bash
# 为每个队友创建可见分割
SPLIT_1=$(cmux --json new-split right | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
SPLIT_2=$(cmux --json new-split down | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
SPLIT_3=$(cmux --json new-split down | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
```

然后在每个队友的提示符中：
```
您有一个cmux终端分割在 surface:42。
运行命令：  cmux send-surface --surface surface:42 "command\n"
读取输出：   cmux capture-pane --surface surface:42
设置状态：    cmux set-status myagent "working" --icon hammer
记录进度：  cmux log "message"
永远不要窃取焦点 — 始终使用 --surface 目标。
```

### 混合布局：终端 + 浏览器

```bash
BUILD=$(cmux --json new-split right | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
DOCS=$(cmux --json browser open https://docs.example.com | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
TEST=$(cmux --json new-split down | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
```

### 关键规则

- **永远不要在分割中启动 `claude -p`** — 使用带有 `team_name` 的代理工具
- **在启动队友前创建分割** — 在他们的提示符中传递引用
- **每个队友一个分割** — 每个队友拥有自己的可见工作区
- **通过 SendMessage 协调**，而不是读取彼此的终端输出
- **清理**: `cmux close-surface --surface <ref>` 完成时

---

## 快速参考

| 任务 | 命令 |
|------|------|
| 我在哪里？ | `cmux identify --json` |
| 向右分割 | `cmux --json new-split right` |
| 向下分割 | `cmux --json new-split down` |
| 发送命令 | `cmux send-surface --surface <ref> "cmd\n"` |
| 读取输出 | `cmux capture-pane --surface <ref>` |
| 打开浏览器 | `cmux --json browser open <url>` |
| 页面快照 | `cmux browser <ref> snapshot --interactive` |
| 点击元素 | `cmux browser <ref> click e1` |
| 填充输入 | `cmux browser <ref> fill e1 "text"` |
| 等待加载 | `cmux browser <ref> wait --load-state complete --timeout-ms 15000` |
| 读取页面文本 | `cmux browser <ref> get text body` |
| 评估JS | `cmux browser <ref> eval "expression"` |
| 通过角色定位 | `cmux browser <ref> find role button` |
| 保存认证 | `cmux browser <ref> state save ./auth.json` |
| 加载认证 | `cmux browser <ref> state load ./auth.json` |
| 设置状态 | `cmux set-status <key> "text" --icon <name>` |
| 进度条 | `cmux set-progress 0.5 --label "Working..."` |
| 日志消息 | `cmux log "message"` |
| 通知 | `cmux notify --title "T" --body "B"` |
| 关闭分割 | `cmux close-surface --surface <ref>` |
| 屏幕截图 | `cmux browser <ref> screenshot` |

---

## 常见模式

### 在背景分割中运行构建，尾随日志

```bash
LOG=$(cmux --json new-split down | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
cmux send-surface --surface "$LOG" "cargo build --release 2>&1 | tee /tmp/build.log\n"
# ... 做其他工作 ...
cmux capture-pane --surface "$LOG" --scrollback | tail -20
```

### QA测试流程

```bash
BROWSER=$(cmux --json browser open https://myapp.vercel.app | python3 -c "import sys,json; print(json.load(sys.stdin)['surface_ref'])")
cmux browser $BROWSER wait --load-state complete --timeout-ms 15000
cmux browser $BROWSER snapshot --interactive
# 使用e1、e2、e3引用交互...
cmux browser $BROWSER screenshot
cmux browser $BROWSER errors list
cmux close-surface --surface $BROWSER
```

### 状态驱动的长任务

```bash
cmux set-status task "starting" --icon clock --color "#ff9500"
cmux set-progress 0.0 --label "Initializing..."

# ... 步骤1 ...
cmux set-progress 0.33 --label "Building..."

# ... 步骤2 ...
cmux set-progress 0.66 --label "Testing..."

# ... 步骤3 ...
cmux set-progress 1.0 --label "Done"
cmux set-status task "complete" --icon checkmark --color "#34c759"
cmux clear-progress
cmux notify --title "Task complete" --body "All steps passed"
```
