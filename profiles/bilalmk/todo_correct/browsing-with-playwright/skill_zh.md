# 浏览器自动化

通过 Playwright MCP 服务器自动化浏览器交互。

## 服务器生命周期

### 启动服务器
```bash
# 使用辅助脚本（推荐）
bash scripts/start-server.sh

# 或手动
npx @playwright/mcp@latest --port 8808 --shared-browser-context &
```

### 停止服务器
```bash
# 使用辅助脚本（先关闭浏览器）
bash scripts/stop-server.sh

# 或手动
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_close -p '{}'
pkill -f "@playwright/mcp"
```

### 何时停止
- **任务结束**：浏览器工作完成后停止
- **长会话**：如果执行多个浏览器任务，保持运行
- **错误**：如果浏览器无响应，停止并重启

**重要提示**：`--shared-browser-context` 标志是必要的，用于在多个 mcp-client.py 调用之间保持浏览器状态。没有它，每次调用都会获得一个新的浏览器上下文。

## 快速参考

### 导航

```bash
# 跳转到 URL
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_navigate \
  -p '{"url": "https://example.com"}'

# 后退
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_navigate_back -p '{}'
```

### 获取页面状态

```bash
# 可访问性快照（返回用于点击/输入的元素引用）
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_snapshot -p '{}'

# 截图
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_take_screenshot \
  -p '{"type": "png", "fullPage": true}'
```

### 与元素交互

使用快照输出中的 `ref` 来定位元素：

```bash
# 点击元素
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_click \
  -p '{"element": "Submit button", "ref": "e42"}'

# 输入文本
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_type \
  -p '{"element": "Search input", "ref": "e15", "text": "hello world", "submit": true}'

# 填写表单（多个字段）
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_fill_form \
  -p '{"fields": [{"ref": "e10", "value": "john@example.com"}, {"ref": "e12", "value": "password123"}]}'

# 选择下拉菜单
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_select_option \
  -p '{"element": "Country dropdown", "ref": "e20", "values": ["US"]}'
```

### 等待条件

```bash
# 等待文本出现
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_wait_for \
  -p '{"text": "Success"}'

# 等待时间（毫秒）
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_wait_for \
  -p '{"time": 2000}'
```

### 执行 JavaScript

```bash
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_evaluate \
  -p '{"function": "return document.title"}'
```

### 多步 Playwright 代码

对于复杂的工作流程，使用 `browser_run_code` 在一个调用中运行多个操作：

```bash
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_run_code \
  -p '{"code": "async (page) => { await page.goto(\"https://example.com\"); await page.click(\"text=Learn more\"); return await page.title(); }"}'
```

**提示**：使用 `browser_run_code` 处理需要原子性（全有或全无）的复杂多步操作。

## 工作流：表单提交

1. 导航到页面
2. 获取快照以查找元素引用
3. 使用引用填写表单字段
4. 点击提交
5. 等待确认
6. 截图结果

## 工作流：数据提取

1. 导航到页面
2. 获取快照（包含文本内容）
3. 使用 browser_evaluate 进行复杂提取
4. 处理结果

## 验证

运行：`python3 scripts/verify.py`

预期：`✓ Playwright MCP 服务器运行中`

## 如果验证失败

1. 运行诊断：`pgrep -f "@playwright/mcp"`
2. 检查：服务器进程是否在 8808 端口运行
3. 尝试：`bash scripts/start-server.sh`
4. **停止并报告**如果仍然失败 - 不要继续执行后续步骤

## 工具参考

参见 [references/playwright-tools.md](references/playwright-tools.md) 获取完整工具文档。

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| 元素未找到 | 先运行 browser_snapshot 获取当前引用 |
| 点击失败 | 先尝试 browser_hover，然后点击 |
| 表单未提交 | 使用 `"submit": true` 与 browser_type |
| 页面未加载 | 增加等待时间或使用 browser_wait_for |
| 服务器无响应 | 停止并重启：`bash scripts/stop-server.sh && bash scripts/start-server.sh` |
