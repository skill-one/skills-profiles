# Web 应用测试

要测试本地 Web 应用，请编写原生 Python Playwright 脚本。

**辅助脚本可用**：
- `scripts/with_server.py` - 管理服务器生命周期（支持多个服务器）

**始终先用 `--help` 运行脚本**以查看用法。在尝试运行脚本后发现确实需要定制解决方案之前，**切勿**阅读源代码。这些脚本可能非常大，因此会污染您的上下文窗口。它们的存在是为了作为黑盒脚本直接调用，而不是被纳入您的上下文窗口。

## 决策树：选择您的方案

```
用户任务 → 它是静态 HTML 吗？
    ├─ 是 → 直接读取 HTML 文件以识别选择器
    │         ├─ 成功 → 使用选择器编写 Playwright 脚本
    │         └─ 失败/不完整 → 视为动态（下方）
    │
    └─ 否（动态 Web 应用）→ 服务器是否已经在运行？
        ├─ 否 → 运行：python scripts/with_server.py --help
        │        然后使用辅助脚本 + 编写简化的 Playwright 脚本
        │
        └─ 是 → 探测后执行：
            1. 导航并等待 networkidle
            2. 截屏或检查 DOM
            3. 从渲染状态识别选择器
            4. 使用发现的选择器执行操作
```

## 示例：使用 with_server.py

要启动服务器，请先用 `--help` 运行，然后使用辅助脚本：

**单个服务器：**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**多个服务器（例如，后端 + 前端）：**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

要创建自动化脚本，请仅包含 Playwright 逻辑（服务器将自动管理）：
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # 始终以无头模式启动 chromium
    page = browser.new_page()
    page.goto('http://localhost:5173') # 服务器已运行并准备就绪
    page.wait_for_load_state('networkidle') # 关键：等待 JS 执行完毕
    # ... 您的自动化逻辑
    browser.close()
```

## 探测后执行模式

1. **检查渲染后的 DOM**：
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **从检查结果中识别选择器**

3. **使用发现的选择器执行操作**

## 常见陷阱

❌ **不要**在动态应用上等待 `networkidle` 之前检查 DOM
✅ **要**在检查之前等待 `page.wait_for_load_state('networkidle')`

## 最佳实践

- **将捆绑脚本作为黑盒使用** - 要完成一项任务，请考虑 `scripts/` 中是否有可用的脚本可以提供帮助。这些脚本可靠地处理常见的复杂工作流，而不会污染上下文窗口。使用 `--help` 查看用法，然后直接调用。
- 使用 `sync_playwright()` 编写同步脚本
- 完成后始终关闭浏览器
- 使用描述性选择器：`text=`, `role=`, CSS 选择器或 ID
- 添加适当的等待：`page.wait_for_selector()` 或 `page.wait_for_timeout()`

## 参考文件

- **examples/** - 展示常见模式的示例：
  - `element_discovery.py` - 在页面上发现按钮、链接和输入
  - `static_html_automation.py` - 使用 file:// URL 测试本地 HTML
  - `console_logging.py` - 捕获自动化过程中的控制台日志
