# Web 应用测试

为了测试本地 Web 应用，编写原生 Python Playwright 脚本。

**可用辅助脚本**：
- `scripts/with_server.py` - 管理服务器生命周期（支持多个服务器）

**始终先运行带有 `--help` 参数的脚本**查看用法。DO NOT 在未先尝试运行脚本并确认确实绝对需要定制解决方案之前读取源代码。这些脚本可能非常大，因此会污染你的上下文窗口。它们存在的目的是作为黑盒脚本直接调用，而不是被摄入到你的上下文窗口中。

## 决策树：选择方法

```
用户任务 → 是否为静态 HTML？
    ├─ 是 → 直接读取 HTML 文件以识别选择器
    │         ├─ 成功 → 编写使用选择器的 Playwright 脚本
    │         └─ 失败/不完整 → 将其视为动态应用（见下方）
    │
    └─ 否（动态 Web 应用）→ 服务器是否已经在运行？
        ├─ 否 → 运行：python scripts/with_server.py --help
        │       然后使用辅助脚本并编写简化的 Playwright 脚本
        │
        └─ 是 → 先侦察后执行：
            1. 导航并等待 networkidle
            2. 截图或检查 DOM
            3. 从渲染状态识别选择器
            4. 使用发现的选择器执行操作
```

## 示例：使用 with_server.py

启动服务器时，先运行 `--help`，然后使用辅助脚本：

**单个服务器**：
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**多个服务器（例如后端 + 前端）**：
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd fronten && npm run dev" --port 5173 \
  -- python your_automation.py
```

创建自动化脚本时，仅包含 Playwright 逻辑（服务器由系统自动管理）：
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # 始终以无头模式启动 chromium
    page = browser.new_page()
    page.goto('http://localhost:5173') # 服务器已运行并就绪
    page.wait_for_load_state('networkidle') # 关键：等待 JS 执行完成
    # ... 你的自动化逻辑
    browser.close()
```

## 先侦察后执行模式

1. **检查渲染后的 DOM**：
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **从检查结果中识别选择器**

3. **使用发现的选择器执行操作**

## 常见陷阱

❌ **不要**在动态应用等待 `networkidle` 之前检查 DOM
✅ **应该**在检查之前等待 `page.wait_for_load_state('networkidle')`

## 最佳实践

- **将内置脚本作为黑盒使用** - 为完成任务，考虑 `scripts/` 目录下的哪个脚本能提供帮助。这些脚本能够可靠地处理常见的复杂工作流，而不会污染上下文窗口。使用 `--help` 查看用法，然后直接调用。
- 使用 `sync_playwright()` 编写同步脚本
- 完成任务后始终关闭浏览器
- 使用描述性选择器：`test=`、`role=`、CSS 选择器或 ID
- 添加适当的等待：`page.wait_for_selector()` 或 `page.wait_for_timeout()`

## 参考文件

- **examples/** - 展示常见模式的示例：
  - `element_discovery.py` - 在页面上发现按钮、链接和输入框
  - `static_html_automation.py` - 使用 `file://` URL 进行本地 HTML 自动化
  - `console_logging.py` - 在自动化过程中捕获控制台日志
