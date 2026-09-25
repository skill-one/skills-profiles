# 浏览器自动化

使用 browse CLI 与 Claude 自动化浏览器交互。

## 环境检查

在运行任何浏览器命令之前，请验证 CLI 是否可用：

```bash
which browse || npm install -g browse
```

## 环境选择（本地 vs 远程）

CLI 支持每个命令的显式环境标志。如果你什么也不做，下一个会话在设置了 `BROWSERBASE_API_KEY` 时默认为 Browserbase，否则为本地。

### 本地模式
- `browse open <url> --local` 启动干净的隔离本地浏览器
- `browse open <url> --auto-connect` 连接到已运行的调试 Chrome；如果没有可调试的 Chrome，请使用 `--local`
- `browse open <url> --cdp <端口|url>` 连接到特定的 CDP 目标
- 最佳用途：开发、本地主机、可信网站和可重复运行

### 远程模式（Browserbase）
- `browse open <url> --remote` 启动 Browserbase 会话
- 没有本地标志时，当设置了 `BROWSERBASE_API_KEY` 时，Browserbase 也是默认值
- 提供：Browserbase 身份验证、验证浏览器、自动 CAPTCHA 解析、住宅代理、会话持久化
- **使用远程模式时**：当目标网站有机器人检测、CAPTCHA、IP 速率限制、Cloudflare 保护或需要特定地理位置访问时
- 在 https://browserbase.com/settings 获取凭证

### 何时选择哪种模式
- **可重复的本地测试/干净状态**：`browse open <url> --local`
- **重用本地登录/cookies**：`browse open <url> --auto-connect`
- **简单浏览**（文档、维基、公共 API）：本地模式即可
- **受保护的网站**（登录墙、CAPTCHA、反爬虫）：使用远程模式
- **如果本地模式失败**（机器人检测或访问被拒绝）：切换到远程模式

## 命令

大多数驱动程序命令在守护进程启动后可在本地、远程和 CDP 会话中工作。

### 导航
```bash
browse open <url>                        # 跳转到 URL
browse open <url> --local                # 在干净的本地浏览器中跳转到 URL
browse open <url> --remote               # 在 Browserbase 会话中跳转到 URL
browse reload                            # 刷新当前页面
browse back                              # 历史记录后退
browse forward                           # 历史记录前进
```

### 页面状态（优先使用快照而不是截图）
```bash
browse snapshot                          # 获取可访问性树和元素引用（快速、结构化）
browse screenshot --path <路径>          # 拍摄视觉截图（慢，使用视觉令牌）
browse get url                           # 获取当前 URL
browse get title                         # 获取页面标题
browse get text <选择器>                # 获取文本内容（使用 "body" 获取所有文本）
browse get html <选择器>                # 获取元素的 HTML 内容
browse get markdown [选择器]             # 将页面内容作为 markdown 获取（默认为 body）
browse get value <选择器>               # 获取表单字段值
```

将 `browse snapshot` 作为你的默认选项来理解页面状态——它返回可访问性树和你可以用来交互的元素引用。只有在需要视觉上下文（布局、图像、调试）时才使用 `browse screenshot`。

### 交互
```bash
browse click <ref>                       # 通过快照中的引用点击元素（例如，@0-5）
browse type <文本>                       # 在焦点元素中输入文本
browse fill <选择器> <值>               # 填充输入；如果需要按 Enter，请添加 --press-enter
browse select <选择器> <值...>           # 选择下拉选项（多个）
browse upload <选择器> <文件...>         # 上传文件到 <input type="file">
browse press <键>                       # 按键（Enter、Tab、Escape、Cmd+A 等）
browse mouse drag <fromX> <fromY> <toX> <toY>  # 从一点拖动到另一点
browse mouse scroll <x> <y> <deltaX> <deltaY>  # 在坐标处滚动
browse highlight <选择器>              # 在页面上突出显示元素
browse is visible <选择器>             # 检查元素是否可见
browse is checked <选择器>             # 检查元素是否被选中
browse wait <类型> [参数]                 # 等待：加载、选择器、超时
```

### CDP 事件跟踪
```bash
browse cdp <url|端口>                    # 从任何目标流式传输 CDP 事件作为 NDJSON
browse cdp 9222                          # 连接到本地 9222 端口的 Chrome
browse cdp ws://localhost:9222/devtools/browser/...  # 完整的 WebSocket URL
browse cdp <url> --domain Network        # 仅 Network 事件
browse cdp <url> --domain Network --domain Console  # 多个域
browse cdp <url> --pretty                # 人类可读的输出
browse cdp <url> > events.jsonl          # 管道到文件
browse cdp <url> | jq '.method'          # 使用 jq 过滤
```

`cdp` 命令直接连接到任何 Chrome DevTools Protocol 目标并流式传输事件。它**不**使用守护进程——它是一个独立的、长时间运行的进程。按 Ctrl+C 停止。默认域：Network、Console、Runtime、Log、Page。

### 会话管理
```bash
browse stop                              # 停止浏览器守护进程
browse status                            # 检查守护进程状态和解析模式
browse tab list                          # 列出所有打开的标签页
browse tab switch <索引或目标 ID>   # 通过索引或目标 ID 切换到标签页
browse tab close [索引或目标 ID]    # 关闭标签页
```

### 典型工作流程
如果环境很重要，请将 `--local`、`--remote`、`--auto-connect` 或 `--cdp <端口|url>` 放在第一个浏览器命令中。

1. `browse open <url> --local` 或 `browse open <url> --remote` — 导航到页面
2. `browse snapshot` — 读取可访问性树以了解页面结构和获取元素引用
3. `browse click <ref>` / `browse type <文本>` / `browse fill <选择器> <值>` — 使用快照中的引用进行交互
4. `browse snapshot` — 确认操作是否成功
5. 重复 3-4 步骤，按需
6. `browse stop` — 完成时关闭浏览器

## 快速示例

```bash
browse open https://example.com
browse snapshot                          # 查看页面结构 + 元素引用
browse click @0-5                        # 点击引用为 0-5 的元素
browse get title
browse stop
```

## 模式比较

| 功能 | 本地 | Browserbase |
|------|------|-------------|
| 速度 | 更快 | 稍慢 |
| 设置 | 需要 Chrome | 需要 API 密钥 |
| 重用现有的本地 cookies | 使用 `browse open <url> --auto-connect` | 不适用 |
| 验证浏览器 | 否 | 是（通过 Browserbase 身份验证的浏览器） |
| CAPTCHA 解析 | 否 | 是（自动 reCAPTCHA/hCaptcha） |
| 住宅代理 | 否 | 是（201 个国家，地理位置定向） |
| 会话持久化 | 否 | 是（通过上下文持久化 cookies/认证） |
| 最佳用途 | 开发/简单页面 | 受保护的网站，Browserbase 身份验证 + 验证访问，生产爬取 |

## 最佳实践

1. **有意选择本地策略**：使用 `browse open <url> --local` 获取干净状态，使用 `browse open <url> --auto-connect` 重用本地凭证，使用 `browse open <url> --remote` 处理受保护的网站
2. **始终先 `browse open`** 再交互
3. **使用 `browse snapshot`** 检查页面状态——它快速且提供元素引用
4. **仅在需要视觉上下文时截图**（布局检查、图像、调试）
5. **使用快照中的引用** 进行点击/交互——例如，`browse click @0-5`
6. **完成时 `browse stop`** 以清理浏览器会话和清除环境覆盖

## 故障排除

- **"没有活动页面"**：运行 `browse stop`，然后检查 `browse status`。如果它仍然显示正在运行，请使用 `pkill -f "browse.*daemon"` 杀死僵尸守护进程，然后重试 `browse open`
- **Chrome 未找到**：安装 Chrome，如果你已经有可调试的 Chrome 运行，请使用 `browse open <url> --auto-connect`，或者切换到 `browse open <url> --remote`
- **操作失败**：运行 `browse snapshot` 查看可用元素及其引用
- **Browserbase 失败**：验证 API 密钥是否已设置

## 切换到远程模式

当检测到：CAPTCHA（reCAPTCHA、hCaptcha、Turnstile）、机器人检测页面（"正在检查您的浏览器..."）、HTTP 403/429、空页面（在应该有内容的网站上）、或用户要求时，切换到远程模式。

不要为简单网站（文档、维基、公共 API、本地主机）切换。

```bash
browse open <url> --local          # 干净的隔离本地浏览器
browse open <url> --auto-connect   # 连接到已存在的可调试 Chrome
browse open <url> --remote         # Browserbase 会话
```

模式标志在会话启动时应用。在 `browse stop` 后，下一个启动将回退到基于环境变量的自动检测。使用 `browse status` 检查运行时守护进程的解析模式和目标。

有关详细示例，请参阅 [EXAMPLES.md](EXAMPLES.md)。
有关 API 参考，请参阅 [REFERENCE.md](REFERENCE.md)。
