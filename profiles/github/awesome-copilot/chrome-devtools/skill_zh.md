# Chrome DevTools Agent

## 概述

一种专门用于控制和检查实时 Chrome 浏览器的技能。该技能利用 `chrome-devtools` MCP 服务器执行广泛的浏览器相关任务，从简单的导航到复杂的性能分析。

## 使用场景

在以下情况下使用此技能：

- **浏览器自动化**：导航页面、点击元素、填写表单和处理对话框。
- **视觉检查**：对网页进行截图或文本快照。
- **调试**：检查控制台消息、在页面上下文中评估 JavaScript 以及分析网络请求。
- **性能分析**：记录和分析性能跟踪以识别瓶颈和 Core Web Vital 问题。
- **模拟**：调整视口大小或模拟网络/CPU 条件。

## 工具类别

### 1. 导航与页面管理

- `new_page`：打开新标签页/页面。
- `navigate_page`：访问特定 URL、重新加载或导航历史记录。
- `select_page`：在打开的页面之间切换上下文。
- `list_pages`：查看所有打开的页面及其 ID。
- `close_page`：关闭特定页面。
- `wait_for`：等待页面出现特定文本。

### 2. 输入与交互

- `click`：点击元素（使用快照中的 `uid`）。
- `fill` / `fill_form`：在输入框中输入文本或一次性填写多个字段。
- `hover`：将鼠标悬停在元素上。
- `press_key`：发送键盘快捷键或特殊键（例如，“Enter”、“Control+C”）。
- `drag`：拖放元素。
- `handle_dialog`：接受或关闭浏览器警告/提示。
- `upload_file`：通过文件输入上传文件。

### 3. 调试与检查

- `take_snapshot`：获取基于文本的可访问性树（最佳用于识别元素）。
- `take_screenshot`：捕获页面或特定元素的视觉表示。
- `list_console_messages` / `get_console_message`：检查页面控制台输出。
- `evaluate_script`：在页面上下文中运行自定义 JavaScript。
- `list_network_requests` / `get_network_request`：分析网络流量和请求详情。

### 4. 模拟与性能

- `resize_page`：更改视口尺寸。
- `emulate`：限制 CPU/网络或模拟地理位置。
- `performance_start_trace`：开始记录性能分析。
- `performance_stop_trace`：停止记录并保存跟踪数据。
- `performance_analyze_insight`：从记录的性能数据中获取详细分析。

## 工作流模式

### 模式 A：识别元素（先快照）

始终优先使用 `take_snapshot` 而不是 `take_screenshot` 来查找元素。快照提供 `uid` 值，这是交互工具所需的。

```markdown
1. 使用 `take_snapshot` 获取当前页面结构。
2. 找到目标元素的 `uid`。
3. 使用 `click(uid=...)` 或 `fill(uid=..., value=...)`。
```

### 模式 B：解决错误

当页面出错时，检查控制台日志和网络请求。

```markdown
1. 使用 `list_console_messages` 检查 JavaScript 错误。
2. 使用 `list_network_requests` 识别失败的（4xx/5xx）资源。
3. 使用 `evaluate_script` 检查特定 DOM 元素或全局变量的值。
```

### 模式 C：性能分析

识别页面为何缓慢。

```markdown
1. `performance_start_trace(reload=true, autoStop=true)`
2. 等待页面加载/跟踪完成。
3. 使用 `performance_analyze_insight` 找到 LCP 问题或布局偏移。
```

## 最佳实践

- **上下文感知**：如果不确定当前活动标签页，始终运行 `list_pages` 和 `select_page`。
- **快照**：在主要导航或 DOM 变更后获取新的快照，因为 `uid` 值可能会变化。
- **超时**：为 `wait_for` 使用合理的超时，以避免在慢速加载元素上卡住。
- **截图**：仅在需要视觉验证时使用 `take_screenshot`，但依赖 `take_snapshot` 进行逻辑操作。
