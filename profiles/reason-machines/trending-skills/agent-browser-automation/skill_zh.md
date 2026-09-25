# agent-browser

> 由 [ara.so](https://ara.so) 开发的技能 — 2026每日技能集合。

`agent-browser` 是一个用 Rust 编写的无头浏览器自动化 CLI，专为 AI 代理设计。它通过 Chrome DevTools Protocol (CDP) 封装 Chrome，并提供了一个快速、便捷的命令行界面，用于导航、交互、可访问性快照、截图、网络拦截等操作，无需 Node.js 或 Playwright 运行时。

## 安装

### 推荐 (npm 全局)
```bash
npm install -g agent-browser
agent-browser install  # 首次下载 Chrome for Testing
```

### macOS (Homebrew)
```bash
brew install agent-browser
agent-browser install
```

### Rust / Cargo
```bash
cargo install agent-browser
agent-browser install
```

### 本地项目依赖
```bash
npm install agent-browser
# 添加到 package.json 脚本或通过 npx 调用
```

### Linux (带系统依赖)
```bash
agent-browser install --with-deps
```

## 快速入门

```bash
agent-browser open https://example.com
agent-browser snapshot                        # 可访问性树与 @refs (最佳用于 AI)
agent-browser click @e2                       # 通过快照中的 @ref 点击
agent-browser fill @e3 "hello@example.com"   # 通过 @ref 填写
agent-browser get text @e1                    # 获取文本内容
agent-browser screenshot page.png
agent-browser close
```

## 核心命令

### 导航
```bash
agent-browser open <url>           # 导航 (别名: goto, navigate)
agent-browser get url              # 获取当前 URL
agent-browser get title            # 获取页面标题
agent-browser close                # 关闭浏览器 (别名: quit, exit)
```

### 可访问性快照 (推荐用于 AI 代理)
```bash
agent-browser snapshot             # 返回包含 @ref ID 的可访问性树
agent-browser snapshot -i          # 交互式/紧凑模式
```

快照输出包含可直接使用的 `@eN` 引用：
```
@e1 [button] "Submit"
@e2 [textbox] "Email" value=""
@e3 [link] "Sign in"
```

然后对它们进行操作：
```bash
agent-browser fill @e2 "user@example.com"
agent-browser click @e1
```

### 交互
```bash
agent-browser click <sel>                     # 点击元素
agent-browser dblclick <sel>                  # 双击
agent-browser fill <sel> <text>               # 清除并填写输入
agent-browser type <sel> <text>               # 向元素输入
agent-browser press <key>                     # 按键 (Enter, Tab, Control+a)
agent-browser keyboard type <text>            # 在当前焦点处输入 (真实按键)
agent-browser keyboard inserttext <text>      # 无按键事件地插入文本
agent-browser hover <sel>                     # 悬停元素
agent-browser select <sel> <value>            # 选择下拉选项
agent-browser check <sel>                     # 勾选复选框
agent-browser uncheck <sel>                   # 取消勾选复选框
agent-browser scroll down 500                 # 滚动 (上/下/左/右, 可选 px)
agent-browser scroll down --selector "#feed"  # 在元素内滚动
agent-browser scrollintoview <sel>            # 将元素滚动到视图中
agent-browser drag <src> <target>             # 拖放
agent-browser upload <sel> /path/file.pdf     # 上传文件
```

### 截图 & PDF
```bash
agent-browser screenshot                          # 保存到临时目录, 打印路径
agent-browser screenshot page.png                 # 保存到路径
agent-browser screenshot --full page.png          # 全页截图
agent-browser screenshot --annotate               # 带编号元素标签覆盖
agent-browser screenshot --screenshot-dir ./shots # 自定义输出目录
agent-browser screenshot --screenshot-format jpeg --screenshot-quality 80
agent-browser pdf output.pdf                      # 保存页面为 PDF
```

### 获取元素信息
```bash
agent-browser get text <sel>           # 文本内容
agent-browser get html <sel>           # innerHTML
agent-browser get value <sel>          # 输入值
agent-browser get attr <sel> <attr>    # 属性值
agent-browser get count <sel>          # 匹配元素数量
agent-browser get box <sel>            # 边界框
agent-browser get styles <sel>         # 计算样式
agent-browser get cdp-url              # CDP WebSocket URL
```

### 状态检查
```bash
agent-browser is visible <sel>
agent-browser is enabled <sel>
agent-browser is checked <sel>
```

### 语义定位器 (find)
```bash
agent-browser find role button click --name "Submit"
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "test@example.com"
agent-browser find placeholder "Search..." fill "rust"
agent-browser find testid "login-btn" click
agent-browser find first ".item" click
agent-browser find nth 2 "a" text
agent-browser find role textbox fill "hello" --name "Username"
```

**操作:** `click`, `fill`, `type`, `hover`, `focus`, `check`, `uncheck`, `text`

### 等待
```bash
agent-browser wait "#modal"                          # 等待元素可见
agent-browser wait 2000                              # 等待 N 毫秒
agent-browser wait --text "Welcome back"             # 等待文本
agent-browser wait --url "**/dashboard"              # 等待 URL 模式
agent-browser wait --load networkidle                # 等待加载状态
agent-browser wait --fn "window.appReady === true"   # 等待 JS 条件
agent-browser wait "#spinner" --state hidden         # 等待元素消失
```

**加载状态:** `load`, `domcontentloaded`, `networkidle`

### JavaScript Eval
```bash
agent-browser eval "document.title"
agent-browser eval "JSON.stringify(window.__STATE__)"
agent-browser eval -b "BASE64_ENCODED_JS"
echo "return document.body.innerHTML" | agent-browser eval --stdin
```

### 批量执行 (高效多步)
```bash
echo '[
  ["open", "https://example.com"],
  ["snapshot", "-i"],
  ["fill", "@e2", "user@example.com"],
  ["click", "@e1"],
  ["screenshot", "result.png"]
]' | agent-browser batch --json

# 首次失败即停止
agent-browser batch --bail < commands.json
```

### 标签 & 帧页
```bash
agent-browser tab                    # 列出标签页
agent-browser tab new https://...    # 新建带 URL 的标签页
agent-browser tab 2                  # 切换到标签页 2
agent-browser tab close              # 关闭当前标签页
agent-browser frame "#my-iframe"     # 切换到 iframe
agent-browser frame main             # 返回主帧
```

### Cookies & 存储
```bash
agent-browser cookies
agent-browser cookies set session_id "abc123"
agent-browser cookies clear

agent-browser storage local
agent-browser storage local set theme dark
agent-browser storage local clear
agent-browser storage session set cart '{"items":[]}'
```

### 网络
```bash
agent-browser network route "**/api/users" --body '{"users":[]}'  # 模拟响应
agent-browser network route "**/ads/**" --abort                    # 阻止请求
agent-browser network unroute                                       # 移除所有路由
agent-browser network requests --filter api                        # 查看请求
agent-browser network har start
agent-browser network har stop recording.har
```

### 浏览器设置
```bash
agent-browser set viewport 1280 800
agent-browser set viewport 375 812 2        # 带设备像素比 (视网膜)
agent-browser set device "iPhone 14"
agent-browser set geo 37.7749 -122.4194
agent-browser set offline on
agent-browser set headers '{"X-Custom":"value"}'
agent-browser set credentials admin secret
agent-browser set media dark
```

### 认证状态
```bash
agent-browser state save ./auth.json    # 保存 cookies + localStorage
agent-browser state load ./auth.json    # 恢复认证状态
agent-browser state list                # 列出保存的状态
agent-browser state show auth.json      # 保存状态的摘要
```

### 对话框
```bash
agent-browser dialog accept             # 接受 alert/confirm/prompt
agent-browser dialog accept "My input"  # 接受 prompt 并带文本
agent-browser dialog dismiss
```

### 剪贴板
```bash
agent-browser clipboard read
agent-browser clipboard write "Hello, World!"
agent-browser clipboard copy           # Ctrl+C 当前选择
agent-browser clipboard paste          # Ctrl+V
```

### 差异 & 可视化测试
```bash
agent-browser diff snapshot                                  # 与上次快照对比
agent-browser diff snapshot --baseline before.txt            # 与保存文件对比
agent-browser diff snapshot --selector "#main" --compact
agent-browser diff screenshot --baseline before.png
agent-browser diff screenshot --baseline b.png -o diff.png
agent-browser diff url https://v1.example.com https://v2.example.com
agent-browser diff url https://v1.example.com https://v2.example.com --screenshot
agent-browser diff url https://v1.example.com https://v2.example.com --selector "#content"
```

### 调试 & 性能分析
```bash
agent-browser trace start trace.zip
agent-browser trace stop
agent-browser profiler start
agent-browser profiler stop profile.json
agent-browser console                  # 查看控制台消息
agent-browser errors                   # 查看未捕获的 JS 异常
agent-browser highlight "#button"      # 可视化高亮元素
agent-browser inspect                  # 打开 Chrome DevTools
agent-browser connect 9222             # 通过 CDP 端口连接到现有浏览器
```

## 常见模式

### 登录流程并保存会话
```bash
#!/bin/bash
agent-browser open https://app.example.com/login
agent-browser fill "#email" "$LOGIN_EMAIL"
agent-browser fill "#password" "$LOGIN_PASSWORD"
agent-browser click "[type=submit]"
agent-browser wait --url "**/dashboard"
agent-browser state save ./session.json
```

### 带快照驱动的交互的 AI 代理循环
```bash
#!/bin/bash
agent-browser open https://app.example.com
agent-browser state load ./session.json

# 获取快照, 解析 @refs, 执行
SNAPSHOT=$(agent-browser snapshot)
echo "$SNAPSHOT"

# 代理确定 @e5 是搜索框
agent-browser fill @e5 "quarterly report"
agent-browser press Enter
agent-browser wait --load networkidle
agent-browser snapshot
agent-browser screenshot results.png
```

### 从脚本中获取批量命令 (JSON)
```bash
cat > commands.json << 'EOF'
[
  ["open", "https://news.ycombinator.com"],
  ["wait", "--load", "networkidle"],
  ["get", "title"],
  ["snapshot"],
  ["screenshot", "hn.png"]
]
EOF

agent-browser batch --json < commands.json
```

### 带模拟网络的抓取
```bash
agent-browser open https://api-heavy-app.example.com
agent-browser network route "**/api/slow-endpoint" --body '{"data":"mocked"}'
agent-browser snapshot
agent-browser network unroute
```

### 带注释的全页截图
```bash
agent-browser open https://example.com
agent-browser wait --load networkidle
agent-browser screenshot --full --annotate annotated.png
```

### 连接到已运行的 Chrome
```bash
# 启动带远程调试的 Chrome
google-chrome --remote-debugging-port=9222 &

agent-browser connect 9222
agent-browser open https://example.com
agent-browser snapshot
```

### 模拟移动设备
```bash
agent-browser set device "iPhone 14"
agent-browser open https://example.com
agent-browser screenshot mobile.png
```

### HAR 录制用于网络分析
```bash
agent-browser open https://example.com
agent-browser network har start
agent-browser click "#load-data"
agent-browser wait --load networkidle
agent-browser network har stop session.har
```

## 选择器参考

| 格式 | 示例 | 备注 |
|------|------|------|
| `@ref` | `@e1`, `@e12` | 来自 `snapshot` 输出 — 推荐用于 AI |
| CSS | `#id`, `.class`, `[attr=val]` | 标准 CSS 选择器 |
| 文本 | `"Sign In"` | 精确文本匹配 |
| XPath | `//button[@type='submit']` | 完整 XPath |

## 故障排除

### Chrome 未找到
```bash
agent-browser install              # 下载 Chrome for Testing
agent-browser install --with-deps  # Linux: 也安装系统库
```

### 元素未找到 / 定时问题
```bash
agent-browser wait "#my-element"              # 首先等待可见性
agent-browser wait --load networkidle         # 等待页面稳定
agent-browser wait --fn "!!document.querySelector('#app')"
```

### 选择器问题 — 使用快照引用
```bash
# 替代脆弱的 CSS:
agent-browser click ".btn.btn-primary.submit-form"

# 使用快照引用:
agent-browser snapshot  # 找到 @e7 = [button] "Submit"
agent-browser click @e7
```

### 查看页面上的内容
```bash
agent-browser screenshot debug.png        # 可视化检查
agent-browser snapshot                    # 可访问性树
agent-browser console                     # JS 控制台输出
agent-browser errors                      # 未捕获的异常
agent-browser eval "document.readyState"
```

### 会话间认证问题
```bash
agent-browser state save ./auth.json   # 登录成功后
agent-browser state load ./auth.json   # 下一个会话开始时
```

### 处理警报/对话框
```bash
# 在触发对话框的操作之前设置处理器
agent-browser dialog accept
agent-browser click "#delete-button"
```

### 性能 — 使用批量处理多步工作流
```bash
# 慢: 每个命令一个进程
agent-browser open https://example.com
agent-browser fill "#q" "search"
agent-browser click "#submit"

# 快: 单个进程, 多个命令
echo '[["open","https://example.com"],["fill","#q","search"],["click","#submit"]]' \
  | agent-browser batch --json
```
