# 使用 agent-browser 进行浏览器自动化

该 CLI 通过 CDP 直接使用 Chrome/Chromium。通过 `npm i -g agent-browser`、`brew install agent-browser` 或 `cargo install agent-browser` 安装。运行 `agent-browser install` 下载 Chrome。

## 核心工作流程

每个浏览器自动化都遵循此模式：

1. **导航**：`agent-browser open <url>`
2. **截图**：`agent-browser snapshot -i`（获取元素引用，如 `@e1`、`@e2`）
3. **交互**：使用引用进行点击、填充、选择
4. **重新截图**：在导航或 DOM 变化后，获取新的引用

```bash
agent-browser open https://example.com/form
agent-browser snapshot -i
# 输出：@e1 [input type="email"]、@e2 [input type="password"]、@e3 [button] "提交"

agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --load networkidle
agent-browser snapshot -i  # 检查结果
```

## 命令链式调用

在单个 shell 调用中可以使用 `&&` 链式调用命令。浏览器通过后台守护进程保持持久化，因此链式调用是安全的，比单独调用更高效。

```bash
# 在一个调用中链式执行打开 + 等待 + 截图
agent-browser open https://example.com && agent-browser wait --load networkidle && agent-browser snapshot -i

# 链式执行多个交互
agent-browser fill @e1 "user@example.com" && agent-browser fill @e2 "password123" && agent-browser click @e3

# 导航并捕获
agent-browser open https://example.com && agent-browser wait --load networkidle && agent-browser screenshot page.png
```

**何时链式调用**：当你不需要在继续之前读取中间命令的输出时使用 `&&`（例如，打开 + 等待 + 截图）。当你需要先解析输出再运行命令时（例如，截图以发现引用，然后使用这些引用进行交互）应单独运行命令。

## 处理身份验证

在自动化需要登录的网站时，选择适合的方法：

**选项 1：从用户的浏览器导入身份验证信息（一次性任务最快**）

```bash
# 连接到用户正在运行的 Chrome（他们已经登录）
agent-browser --auto-connect state save ./auth.json
# 使用该身份验证状态
agent-browser --state ./auth.json open https://app.example.com/dashboard
```

状态文件包含明文会话令牌——添加到 `.gitignore` 并在不再需要时删除。设置 `AGENT_BROWSER_ENCRYPTION_KEY` 以进行静态加密。

**选项 2：持久化配置文件（最简单的重复任务方法**）

```bash
# 首次运行：手动登录或通过自动化
agent-browser --profile ~/.myapp open https://app.example.com/login
# ... 填写凭证，提交 ...

# 所有后续运行：已认证
agent-browser --profile ~/.myapp open https://app.example.com/dashboard
```

**选项 3：会话名称（自动保存/恢复 Cookie + localStorage**）

```bash
agent-browser --session-name myapp open https://app.example.com/login
# ... 登录流程 ...
agent-browser close  # 状态自动保存

# 下次：状态自动恢复
agent-browser --session-name myapp open https://app.example.com/dashboard
```

**选项 4：身份验证保险库（凭证加密存储，按名称登录**）

```bash
echo "$PASSWORD" | agent-browser auth save myapp --url https://app.example.com/login --username user --password-stdin
agent-browser auth login myapp
```

**选项 5：状态文件（手动保存/加载**）

```bash
# 登录后：
agent-browser state save ./auth.json
# 在未来会话中：
agent-browser state load ./auth.json
agent-browser open https://app.example.com/dashboard
```

有关 OAuth、2FA、基于 Cookie 的身份验证和令牌刷新模式的参考，请参阅 [references/authentication.md](references/authentication.md)。

## 基本命令

```bash
# 导航
agent-browser open <url>              # 导航（别名：goto、navigate）
agent-browser close                   # 关闭浏览器

# 截图
agent-browser snapshot -i             # 交互式元素引用（推荐）
agent-browser snapshot -i -C          # 包含光标交互元素（带有 onclick、cursor:pointer 的 div）
agent-browser snapshot -s "#selector" # 限制到 CSS 选择器

# 交互（使用从截图获取的 @refs）
agent-browser click @e1               # 点击元素
agent-browser click @e1 --new-tab     # 在新标签页中点击
agent-browser fill @e2 "text"         # 清除并输入文本
agent-browser type @e2 "text"         # 输入而不清除
agent-browser select @e1 "option"     # 选择下拉选项
agent-browser check @e1               # 勾选复选框
agent-browser press Enter             # 按键
agent-browser keyboard type "text"    # 在当前焦点处输入（无需选择器）
agent-browser keyboard inserttext "text"  # 无按键事件插入
agent-browser scroll down 500         # 滚动页面
agent-browser scroll down 500 --selector "div.content"  # 在特定容器内滚动

# 获取信息
agent-browser get text @e1            # 获取元素文本
agent-browser get url                 # 获取当前 URL
agent-browser get title               # 获取页面标题
agent-browser get cdp-url             # 获取 CDP WebSocket URL

# 等待
agent-browser wait @e1                # 等待元素
agent-browser wait --load networkidle # 等待网络空闲
agent-browser wait --url "**/page"    # 等待 URL 模式
agent-browser wait 2000               # 等待毫秒
agent-browser wait --text "Welcome"    # 等待文本出现（子字符串匹配）
agent-browser wait --fn "!document.body.innerText.includes('Loading...')"  # 等待文本消失
agent-browser wait "#spinner" --state hidden  # 等待元素消失

# 下载
agent-browser download @e1 ./file.pdf          # 点击元素以触发下载
agent-browser wait --download ./output.zip     # 等待任何下载完成
agent-browser --download-path ./downloads open <url>  # 设置默认下载目录

# 视口 & 设备模拟
agent-browser set viewport 1920 1080          # 设置视口大小（默认：1280x720）
agent-browser set viewport 1920 1080 2        # 2x视网膜（相同的 CSS 大小，更高的分辨率截图）
agent-browser set device "iPhone 14"          # 模拟设备（视口 + 用户代理）

# 捕获
agent-browser screenshot              # 截图到临时目录
agent-browser screenshot --full       # 全页截图
agent-browser screenshot --annotate   # 带注释的截图，带有编号的元素标签
agent-browser screenshot --screenshot-dir ./shots  # 保存到自定义目录
agent-browser screenshot --screenshot-format jpeg --screenshot-quality 80
agent-browser pdf output.pdf          # 保存为 PDF

# 剪贴板
agent-browser clipboard read                      # 从剪贴板读取文本
agent-browser clipboard write "Hello, World!"     # 写入文本到剪贴板
agent-browser clipboard copy                      # 复制当前选择
agent-browser clipboard paste                     # 从剪贴板粘贴

# 差异比较（页面状态比较）
agent-browser diff snapshot                          # 比较当前与上次截图
agent-browser diff snapshot --baseline before.txt    # 比较当前与保存的文件
agent-browser diff screenshot --baseline before.png  # 视觉像素差异
agent-browser diff url <url1> <url2>                 # 比较两个页面
agent-browser diff url <url1> <url2> --wait-until networkidle  # 自定义等待策略
agent-browser diff url <url1> <url2> --selector "#main"  # 限制到元素
```

## 常见模式

### 表单提交

```bash
agent-browser open https://example.com/signup
agent-browser snapshot -i
agent-browser fill @e1 "Jane Doe"
agent-browser fill @e2 "jane@example.com"
agent-browser select @e3 "California"
agent-browser check @e4
agent-browser click @e5
agent-browser wait --load networkidle
```

### 使用身份验证保险库进行身份验证（推荐）

```bash
# 一次性保存凭证（使用 AGENT_BROWSER_ENCRYPTION_KEY 加密）
# 推荐：通过 stdin 管道传递密码，避免 shell 历史记录暴露
echo "pass" | agent-browser auth save github --url https://github.com/login --username user --password-stdin

# 使用保存的配置文件登录（LLM 永远看不到密码）
agent-browser auth login github

# 列出/显示/删除配置文件
agent-browser auth list
agent-browser auth show github
agent-browser auth delete github
```

### 使用状态持久化进行身份验证

```bash
# 一次性登录并保存状态
agent-browser open https://app.example.com/login
agent-browser snapshot -i
agent-browser fill @e1 "$USERNAME"
agent-browser fill @e2 "$PASSWORD"
agent-browser click @e3
agent-browser wait --url "**/dashboard"
agent-browser state save auth.json

# 未来会话中重用
agent-browser state load auth.json
agent-browser open https://app.example.com/dashboard
```

### 会话持久化

```bash
# 自动保存/恢复 Cookie 和 localStorage，跨浏览器重启
agent-browser --session-name myapp open https://app.example.com/login
# ... 登录流程 ...
agent-browser close  # 状态自动保存

# 下次，状态自动加载
agent-browser --session-name myapp open https://app.example.com/dashboard

# 静态加密状态
export AGENT_BROWSER_ENCRYPTION_KEY=$(openssl rand -hex 32)
agent-browser --session-name secure open https://app.example.com

# 管理保存的状态
agent-browser state list
agent-browser state show myapp-default.json
agent-browser state clear myapp
agent-browser state clean --older-than 7
```

### 数据提取

```bash
agent-browser open https://example.com/products
agent-browser snapshot -i
agent-browser get text @e5           # 获取特定元素文本
agent-browser get text body > page.txt  # 获取所有页面文本

# JSON 输出用于解析
agent-browser snapshot -i --json
agent-browser get text @e1 --json
```

### 并发会话

```bash
agent-browser --session site1 open https://site-a.com
agent-browser --session site2 open https://site-b.com

agent-browser --session site1 snapshot -i
agent-browser --session site2 snapshot -i

agent-browser session list
```

### 连接到现有 Chrome

```bash
# 自动发现启用远程调试的运行中的 Chrome
agent-browser --auto-connect open https://example.com
agent-browser --auto-connect snapshot

# 或使用显式 CDP 端口
agent-browser --cdp 9222 snapshot
```

### 色彩方案（暗黑模式）

```bash
# 通过标志设置持久暗黑模式（适用于所有页面和新标签页）
agent-browser --color-scheme dark open https://example.com

# 或通过环境变量
AGENT_BROWSER_COLOR_SCHEME=dark agent-browser open https://example.com

# 或在会话期间设置（对后续命令持续有效）
agent-browser set media dark
```

### 视口 & 响应式测试

```bash
# 设置自定义视口大小（默认是 1280x720）
agent-browser set viewport 1920 1080
agent-browser screenshot desktop.png

# 测试移动宽度布局
agent-browser set viewport 375 812
agent-browser screenshot mobile.png

# Retina/HiDPI：相同的 CSS 布局，2x 像素密度
# 截图保持逻辑视口大小，但内容以更高 DPI 渲染
agent-browser set viewport 1920 1080 2
agent-browser screenshot retina.png

# 设备模拟（一步设置视口 + 用户代理）
agent-browser set device "iPhone 14"
agent-browser screenshot device.png
```

`scale` 参数（第三个参数）设置 `window.devicePixelRatio` 而不改变 CSS 布局。在测试视网膜渲染或捕获更高分辨率截图时使用它。

### 可视化浏览器（调试）

```bash
agent-browser --headed open https://example.com
agent-browser highlight @e1          # 高亮元素
agent-browser inspect                # 为当前页面打开 Chrome DevTools
agent-browser record start demo.webm # 录制会话
agent-browser profiler start         # 开始 Chrome DevTools 性能分析
agent-browser profiler stop trace.json # 停止并保存性能分析（路径可选）
```

使用 `AGENT_BROWSER_HEADED=1` 通过环境变量启用 headed 模式。浏览器扩展在 headed 和 headless 模式下都可用。

### 本地文件（PDF、HTML）

```bash
# 使用 file:// URL 打开本地文件
agent-browser --allow-file-access open file:///path/to/document.pdf
agent-browser --allow-file-access open file:///path/to/page.html
agent-browser screenshot output.png
```

### iOS 模拟器（移动 Safari）

```bash
# 列出可用的 iOS 模拟器
agent-browser device list

# 在特定设备上启动 Safari
agent-browser -p ios --device "iPhone 16 Pro" open https://example.com

# 与桌面相同的工作流程 - 截图、交互、重新截图
agent-browser -p ios snapshot -i
agent-browser -p ios tap @e1          # 点击（别名：click）
agent-browser -p ios fill @e2 "text"
agent-browser -p ios swipe up         # 移动端特定手势

# 拍摄截图
agent-browser -p ios screenshot mobile.png

# 关闭会话（关闭模拟器）
agent-browser -p ios close
```

**要求**：macOS 配备 Xcode，Appium (`npm install -g appium && appium driver install xcuitest`)

**真实设备**：如果预先配置，则支持物理 iOS 设备。使用 `--device "<UDID>"`，其中 UDID 来自 `xcrun xctrace list devices`。

## 安全

所有安全功能都是可选的。默认情况下，agent-browser 对导航、操作或输出不施加任何限制。

### 内容边界（推荐用于 AI 代理）

启用 `--content-boundaries` 以将页面源输出包裹在标记中，帮助 LLM 区分工具输出和不可信的页面内容：

```bash
export AGENT_BROWSER_CONTENT_BOUNDARIES=1
agent-browser snapshot
# 输出：
# --- AGENT_BROWSER_PAGE_CONTENT nonce=<hex> origin=https://example.com ---
# [accessibility tree]
# --- END_AGENT_BROWSER_PAGE_CONTENT nonce=<hex> ---
```

### 域名白名单

限制导航到可信域名。通配符如 `*.example.com` 也匹配纯域名 `example.com`。子资源请求、WebSocket 和 EventSource 连接到非允许域也会被阻止。包括目标页面依赖的 CDN 域名：

```bash
export AGENT_BROWSER_ALLOWED_DOMAINS="example.com,*.example.com"
agent-browser open https://example.com        # OK
agent-browser open https://malicious.com       # 阻止
```

### 操作策略

使用策略文件来限制破坏性操作：

```bash
export AGENT_BROWSER_ACTION_POLICY=./policy.json
```

示例 `policy.json`：

```json
{
  "default": "deny",
  "allow": ["navigate", "snapshot", "click", "scroll", "wait", "get"]
}
```

身份验证保险库操作（`auth login` 等）绕过操作策略，但域名白名单仍然适用。

### 输出限制

防止大型页面导致上下文泛滥：

```bash
export AGENT_BROWSER_MAX_OUTPUT=50000
```

## 差异比较（验证更改）

在执行操作后使用 `diff snapshot` 来验证它是否产生了预期效果。这比较当前可访问性树与会话中上次拍摄的快照。

```bash
# 典型工作流程：快照 -> 操作 -> diff
agent-browser snapshot -i          # 拍摄基线快照
agent-browser click @e2            # 执行操作
agent-browser diff snapshot        # 查看发生了什么变化（自动与上次快照比较）
```

用于视觉回归测试或监控：

```bash
# 保存基线截图，稍后比较
agent-browser screenshot baseline.png
# ... 时间过去或进行了更改 ...
agent-browser diff screenshot --baseline baseline.png

# 比较暂存版与生产版
agent-browser diff url https://staging.example.com https://prod.example.com --screenshot
```

`diff snapshot` 输出使用 `+` 表示添加，`-` 表示删除，类似于 git diff。`diff screenshot` 生成一个差异图像，更改的像素以红色突出显示，并显示不匹配的百分比。

## 超时和慢速页面

默认超时为 25 秒。这可以通过 `AGENT_BROWSER_DEFAULT_TIMEOUT` 环境变量（以毫秒为单位的值）覆盖。对于慢速网站或大型页面，使用显式等待而不是依赖默认超时：

```bash
# 等待网络活动稳定（慢速页面的最佳选择）
agent-browser wait --load networkidle

# 等待特定元素出现
agent-browser wait "#content"
agent-browser wait @e1

# 等待特定 URL 模式（重定向后有用）
agent-browser wait --url "**/dashboard"

# 等待 JavaScript 条件
agent-browser wait --fn "document.readyState === 'complete'"

# 作为最后手段等待固定持续时间（毫秒）
agent-browser wait 5000
```

在处理始终慢速的网站时，在 `open` 后使用 `wait --load networkidle` 确保页面完全加载后再拍摄截图。如果特定元素加载缓慢，使用 `wait <selector>` 或 `wait @ref` 直接等待它。

## 会话管理和清理

在运行多个代理或自动化时，始终使用命名会话以避免冲突：

```bash
# 每个代理都有自己的隔离会话
agent-browser --session agent1 open site-a.com
agent-browser --session agent2 open site-b.com

# 检查活动会话
agent-browser session list
```

完成时始终关闭浏览器会话以避免泄漏进程：

```bash
agent-browser close                    # 关闭默认会话
agent-browser --session agent1 close   # 关闭特定会话
```

如果之前的会话未正确关闭，守护进程可能仍在运行。使用 `agent-browser close` 在开始新工作前清理它。

要自动在一段时间不活动后关闭守护进程（对临时/CI 环境很有用）：

```bash
AGENT_BROWSER_IDLE_TIMEOUT_MS=60000 agent-browser open example.com
```

## 引用生命周期（重要）

引用（`@e1`、`@e2` 等）在页面更改时失效。在以下情况下始终重新截图：

- 点击链接或按钮导致导航
- 表单提交
- 动态内容加载（下拉列表、模态框）

```bash
agent-browser click @e5              # 导航到新页面
agent-browser snapshot -i            # 必须重新截图
agent-browser click @e1              # 使用新的引用
```

## 带注释的截图（视觉模式）

使用 `--annotate` 拍摄带有编号标签的截图，标签覆盖在交互式元素上。每个标签 `[N]` 对应引用 `@eN`。这也缓存了引用，因此您可以在不单独拍摄截图的情况下立即与元素交互。

```bash
agent-browser screenshot --annotate
# 输出包括图像路径和图例：
#   [1] @e1 按钮 "提交"
#   [2] @e2 链接 "主页"
#   [3] @e3 文本框 "电子邮件"
agent-browser click @e2              # 使用带注释截图的引用点击
```

在以下情况下使用带注释的截图：

- 页面有未标记的图标按钮或仅视觉元素
- 需要验证视觉布局或样式
- Canvas 或图表元素存在（文本截图无法检测到）
- 需要关于元素位置的空间推理

## 语义定位器（引用的替代方案）

当引用不可用或不可靠时，使用语义定位器：

```bash
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "user@test.com"
agent-browser find role button click --name "Submit"
agent-browser find placeholder "Search" type "query"
agent-browser find testid "submit-btn" click
```

## JavaScript 评估（eval）

在浏览器上下文中运行 JavaScript。**Shell 引用会破坏复杂的表达式**——使用 `--stdin` 或 `-b` 避免问题。

```bash
# 简单表达式可以用常规引用工作
agent-browser eval 'document.title'
agent-browser eval 'document.querySelectorAll("img").length'

# 复杂的 JS：使用 heredoc（推荐）
agent-browser eval --stdin <<'EVALEOF'
JSON.stringify(
  Array.from(document.querySelectorAll("img"))
    .filter(i => !i.alt)
    .map(i => ({ src: i.src.split("/").pop(), width: i.width }))
)
EVALEOF

# 替代方案：base64 编码（避免所有 shell 逃逸问题）
agent-browser eval -b "$(echo -n 'Array.from(document.querySelectorAll("a")).map(a => a.href)' | base64)"
```

**为什么这很重要**：当 shell 处理你的命令时，内部双引号、`!` 字符（历史扩展）、反引号和 `$()` 都可能破坏传递给 agent-browser 的 JavaScript。`--stdin` 和 `-b` 标志完全绕过 shell 解释。

**经验法则**：

- 单行，无嵌套引号 -> 使用单引号 `eval 'expression'` 是安全的
- 嵌套引号、箭头函数、模板文字或多行 -> 使用 `eval --stdin <<'EVALEOF'`
- 程序化/生成脚本 -> 使用 `eval -b` 与 base64

## 配置文件

在项目根目录中创建 `agent-browser.json` 以进行持久设置：

```json
{
  "headed": true,
  "proxy": "http://localhost:8080",
  "profile": "./browser-data"
}
```

优先级（从低到高）：`~/.agent-browser/config.json` < `./agent-browser.json` < 环境变量 < CLI 标志。使用 `--config <path>` 或 `AGENT_BROWSER_CONFIG` 环境变量指定自定义配置文件（如果缺失/无效则退出错误）。所有 CLI 选项映射到 camelCase 键（例如，`--executable-path` -> `"executablePath"`）。布尔标志接受 `true`/`false` 值（例如，`--headed false` 覆盖配置）。用户和项目配置文件中的扩展被合并，而不是替换。

## 深入文档

| 参考                                                            | 使用场景                                               |
| -------------------------------------------------------------------- | --------------------------------------------------------- |
| [references/commands.md](references/commands.md)                     | 完整命令参考，包含所有选项                   |
| [references/snapshot-refs.md](references/snapshot-refs.md)           | 引用生命周期、失效规则、故障排除        |
| [references/session-management.md](references/session-management.md) | 并发会话、状态持久化、并发抓取 |
| [references/authentication.md](references/authentication.md)         | 登录流程、OAuth、2FA 处理、状态重用             |
| [references/video-recording.md](references/video-recording.md)       | 录制工作流程，用于调试和文档       |
| [references/profiling.md](references/profiling.md)                   | Chrome DevTools 性能分析                               |
| [references/proxy-support.md](references/proxy-support.md)           | 代理配置、地理测试、轮换代理        |

## 浏览器引擎选择

使用 `--engine` 选择本地浏览器引擎。默认是 `chrome`。

```bash
# 使用 Lightpanda（快速 headless 浏览器，需要单独安装）
agent-browser --engine lightpanda open example.com

# 通过环境变量
export AGENT_BROWSER_ENGINE=lightpanda
agent-browser open example.com

# 使用自定义二进制路径
agent-browser --engine lightpanda --executable-path /path/to/lightpanda open example.com
```

支持的引擎：

- `chrome`（默认）-- Chrome/Chromium via CDP
- `lightpanda` -- Lightpanda headless browser via CDP (10x faster, 10x less memory than Chrome)

Lightpanda 不支持 `--extension`、`--profile`、`--state` 或 `--allow-file-access`。从 https://lightpanda.io/docs/open-source/installation 安装 Lightpanda。

## 即用模板

| 模板                                                                 | 描述                         |
| ------------------------------------------------------------------------ | ---------------------------- |
| [templates/form-automation.sh](templates/form-automation.sh)             | 带验证的表单填写             |
| [templates/authenticated-session.sh](templates/authenticated-session.sh) | 登录一次，重用状态             |
| [templates/capture-workflow.sh](templates/capture-workflow.sh)           | 内容提取与截图工作流程         |

```bash
./templates/form-automation.sh https://example.com/form
./templates/authenticated-session.sh https://app.example.com/login
./templates/capture-workflow.sh https://example.com ./output
```
