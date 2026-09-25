`chrome-devtools-mcp` 命令行界面 (CLI) 允许您从终端与浏览器进行交互。

## 安装

_注意：如果您是首次使用此 CLI，请参阅 [references/installation.md](references/installation.md) 进行设置。安装是一次性的先决条件，**不**是常规 AI 工作流程的一部分。_

## AI 工作流程

1. **执行**：直接运行工具。如果您不知道目标页面的 ID，请运行 `chrome-devtools list_pages` 来查找它。后台服务器会隐式启动；**请勿**在每次使用前运行 `start`/`status`/`stop`。
2. **检查**：使用 `chrome-devtools take_snapshot <pageId>` 获取元素 `<uid>`。
3. **操作**：使用 `chrome-devtools click <pageId> <uid>`、`chrome-devtools fill <pageId> <uid> <value>` 等。状态跨命令持久化。

快照示例：

```
uid=1_0 RootWebArea "Example Domain" url="https://example.com/"
  uid=1_1 heading "Example Domain" level="1"
```

## 权限与文件访问

默认情况下，CLI 拥有完整的文件系统访问权限 (`--allowUnrestrictedPaths=true`)，允许文件保存参数 (`--filePath`、`--outputDirPath`) 和 `upload_file` 访问系统上的任何文件。如果您想将文件访问限制为操作系统临时目录，请传递 `--allowUnrestrictedPaths=false`。

## 命令用法

```sh
chrome-devtools <工具> [参数] [标志]
```

- 必填参数按位置传递；可选参数使用标志。
- 在任何命令上使用 `--help` 获取用法详情。
- 输出默认为纯 Markdown 格式文本；传递 `--output-format=json` 获取 JSON。

## 输入自动化（来自快照的 `<uid>`）

```bash
chrome-devtools take_snapshot 1 # 对页面进行文本快照以获取元素的 UID
chrome-devtools click 1 "id" # 点击提供的元素
chrome-devtools click 1 "id" --dblClick true --includeSnapshot true # 双击并返回快照
chrome-devtools drag 1 "src" "dst" # 将一个元素拖放到另一个元素上
chrome-devtools drag 1 "src" "dst" --includeSnapshot true # 拖动元素并返回快照
chrome-devtools fill 1 "id" "text" # 在输入、textarea 或选择选项中输入文本
chrome-devtools fill 1 "id" "text" --includeSnapshot true # 填充元素并返回快照
chrome-devtools handle_dialog 1 accept # 处理浏览器对话框（接受/取消）
chrome-devtools handle_dialog 1 dismiss --promptText "hi" # 使用提示文本取消对话框
chrome-devtools hover 1 "id" # 悬停于提供的元素
chrome-devtools hover 1 "id" --includeSnapshot true # 悬停于元素并返回快照
chrome-devtools press_key 1 "Enter" # 按下键或键组合（"Control+A"、"Escape"）
chrome-devtools press_key 1 "Control+A" --includeSnapshot true # 按下键并返回快照
chrome-devtools type_text 1 "hello" # 使用键盘在焦点输入中输入文本
chrome-devtools type_text 1 "hello" --submitKey "Enter" # 输入文本并按下提交键
chrome-devtools upload_file 1 "id" "file.txt" # 通过提供的元素上传文件
chrome-devtools upload_file 1 "id" "file.txt" --includeSnapshot true # 上传文件并返回快照
```

## 导航

```bash
chrome-devtools close_page 1 # 通过索引关闭页面
chrome-devtools list_pages # 获取浏览器中打开的页面列表
chrome-devtools navigate_page 1 --url "https://example.com" # 将当前选中的页面导航到 URL
chrome-devtools navigate_page 1 --type "reload" --ignoreCache true # 忽略缓存重新加载页面
chrome-devtools navigate_page 1 --url "https://example.com" --timeout 5000 # 带超时导航
chrome-devtools navigate_page 1 --handleBeforeUnload "accept" # 处理 before unload 对话框
chrome-devtools navigate_page 1 --type "back" --initScript "foo()" # 返回并运行初始化脚本
chrome-devtools new_page "https://example.com" # 创建新页面
chrome-devtools new_page "https://example.com" --background true --timeout 5000 # 在后台创建新页面
chrome-devtools new_page "https://example.com" --isolatedContext "ctx" # 使用隔离上下文创建新页面
chrome-devtools select_page 1 # 选择页面作为未来工具调用的上下文
chrome-devtools select_page 1 --bringToFront true # 选择页面并将其带到前台
```

## 模拟

```bash
chrome-devtools emulate 1 --networkConditions "Offline" # 模拟网络条件
chrome-devtools emulate 1 --cpuThrottlingRate 4 --geolocation "0x0" # 模拟 CPU 节流和地理位置
chrome-devtools emulate 1 --colorScheme "dark" --viewport "1920x1080" # 模拟配色方案和视口
chrome-devtools emulate 1 --userAgent "Mozilla/5.0..." # 模拟用户代理
chrome-devtools resize_page 1 1920 1080 # 调整选中页面窗口的大小
```

## 性能

```bash
chrome-devtools performance_analyze_insight 1 "1" "LCPBreakdown" # 获取特定 Performance Insight 的更多详情（pageId、insightSetId、insightName）
chrome-devtools performance_start_trace 1 --reload true --autoStop false # 开始性能跟踪记录（reload、autoStop）
chrome-devtools performance_start_trace 1 --reload true --autoStop true --filePath "t.json.gz" # 开始跟踪并保存到文件
chrome-devtools performance_stop_trace 1 # 停止当前的性能跟踪
chrome-devtools performance_stop_trace 1 --filePath "t.json.gz" # 停止跟踪并保存到文件
```

## 内存

```bash
chrome-devtools take_heapsnapshot 1 "./snap.heapsnapshot" # 捕获内存堆快照
```

### 内存调试（需要 `--memoryDebugging=true`）

```bash
chrome-devtools get_heapsnapshot_summary "./snap.heapsnapshot" # 获取快照摘要统计信息
chrome-devtools compare_heapsnapshots "./base.heapsnapshot" "./target.heapsnapshot" # 比较两个快照
chrome-devtools get_heapsnapshot_class_nodes "./snap.heapsnapshot" "Array" # 检查类实例
chrome-devtools get_heapsnapshot_details "./snap.heapsnapshot" 123 # 详细对象属性
chrome-devtools get_heapsnapshot_dominators "./snap.heapsnapshot" 123 # 节点的支配树
chrome-devtools get_heapsnapshot_duplicate_strings "./snap.heapsnapshot" # 查找重复的字符串
chrome-devtools get_heapsnapshot_edges "./snap.heapsnapshot" 123 # 节点边/引用
chrome-devtools get_heapsnapshot_object_details "./snap.heapsnapshot" 123 # 通过节点 ID 获取对象详情
chrome-devtools get_heapsnapshot_retainers "./snap.heapsnapshot" 123 # 保持对象
chrome-devtools get_heapsnapshot_retaining_paths "./snap.heapsnapshot" 123 # 最短保持路径
chrome-devtools close_heapsnapshot "./snap.heapsnapshot" # 释放加载快照的内存
```

## 网络

```bash
chrome-devtools get_network_request 1 # 获取页面 1 当前选中的网络请求
chrome-devtools get_network_request 1 --reqid 1 --requestFilePath "req.md" # 通过 ID 获取请求并保存到文件
chrome-devtools get_network_request 1 --responseFilePath "res.md" # 将响应正文保存到文件
chrome-devtools list_network_requests 1 # 列出页面 1 的所有网络请求
chrome-devtools list_network_requests 1 --pageSize 50 --pageIdx 0 # 分页列出网络请求
chrome-devtools list_network_requests 1 --resourceTypes Fetch # 按资源类型过滤请求
chrome-devtools list_network_requests 1 --includePreservedRequests true # 包含保留的请求
```

## 调试与检查

```bash
chrome-devtools evaluate_script "() => document.title" --pageId 1 # 在页面 1 上评估 JavaScript 函数
chrome-devtools evaluate_script "(a) => a.innerText" --pageId 1 --args 1_4 # 在页面 1 上使用 UID 参数评估 JS
chrome-devtools get_console_message 1 1 # 通过 ID 获取控制台消息
chrome-devtools get_css_styles 1 "1_4" # 在页面 1 上获取 CSS 样式（默认：10 条规则，pageIdx 0）
chrome-devtools get_css_styles 1 "1_4" --pageSize 20 --pageIdx 1 # 自定义页面大小和自定义 0 基页索引分页 CSS 规则
chrome-devtools lighthouse_audit 1 --mode "navigation" # 对导航运行 Lighthouse 审计
chrome-devtools lighthouse_audit 1 --mode "snapshot" --device "mobile" # 在移动设备上对快照运行 Lighthouse 审计
chrome-devtools lighthouse_audit 1 --outputDirPath ./out # 运行 Lighthouse 审计并保存报告
chrome-devtools list_console_messages 1 # 列出所有控制台消息
chrome-devtools list_console_messages 1 --pageSize 20 --pageIdx 1 # 分页列出控制台消息
chrome-devtools list_console_messages 1 --types error --types info # 按类型过滤控制台消息
chrome-devtools list_console_messages 1 --includePreservedMessages true # 包含保留的消息
chrome-devtools take_screenshot 1 # 对页面视口进行截图
chrome-devtools take_screenshot 1 --fullPage true --format "jpeg" --quality 80 # 作为 JPEG 全页截图，质量为 80
chrome-devtools take_screenshot 1 --uid "id" --filePath "s.png" # 对元素进行截图
chrome-devtools take_snapshot 1 # 从可访问性树对页面进行文本快照
chrome-devtools take_snapshot 1 --verbose true --filePath "s.txt" # 保存详细快照到文件
```

## 扩展

```bash
chrome-devtools list_extensions # 列出浏览器中安装的所有 Chrome 扩展
chrome-devtools install_extension "/path/to/extension" # 从给定路径安装 Chrome 扩展
chrome-devtools uninstall_extension "extension_id" # 通过 ID 卸载 Chrome 扩展
chrome-devtools reload_extension "extension_id" # 通过 ID 重新加载未打包的 Chrome 扩展
chrome-devtools trigger_extension_action "extension_id" # 通过 ID 触发扩展的默认操作
```

## 渐进式 Web 应用（需要 `--categoryPwa=true`）

```bash
chrome-devtools install_pwa "https://example.com/" # 通过清单 ID 或 URL 安装 PWA
chrome-devtools launch_pwa "https://example.com/" # 启动已安装的 PWA
chrome-devtools get_os_app_state "https://example.com/" # 获取 OS 应用安装状态
chrome-devtools uninstall_pwa "https://example.com/" # 卸载 PWA 并关闭窗口
```

## 实验性功能

实验性工具默认禁用。在 `start` 期间使用相应标志启用它们。

```bash
chrome-devtools click_at 1 100 200 # 在页面 1 的指定坐标处点击（需要 --experimentalVision=true）
chrome-devtools screencast_start 1 --filePath "screen.mp4" # 在页面 1 上开始屏幕录制（需要 --experimentalScreencast=true 和 ffmpeg）
chrome-devtools screencast_stop 1 # 停止页面 1 上的活动屏幕录制
chrome-devtools list_webmcp_tools 1 # 列出页面 1 上的所有 WebMCP 工具（需要 --categoryExperimentalWebmcp=true）
chrome-devtools execute_webmcp_tool 1 "tool_name" --input '{"arg":"val"}' # 在页面 1 上执行 WebMCP 工具（需要 --categoryExperimentalWebmcp=true）
chrome-devtools list_3p_developer_tools 1 # 列出页面 1 上的第三方开发者工具（需要 --categoryExperimentalThirdParty=true）
chrome-devtools execute_3p_developer_tool 1 "tool_name" --params '{"arg":"val"}' # 在页面 1 上执行第三方开发者工具（需要 --categoryExperimentalThirdParty=true）
```

## 服务管理

```bash
chrome-devtools start   # 启动或重新启动 chrome-devtools-mcp
chrome-devtools start --headless=false # 使用可见浏览器窗口启动
chrome-devtools status  # 检查 chrome-devtools-mcp 是否正在运行
chrome-devtools stop    # 如果有的话，停止 chrome-devtools-mcp
```
