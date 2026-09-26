> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# Agentic Browser

通过 [inference.sh](https://inference.sh) 实现的 AI 代理浏览器自动化。底层使用 Playwright，并带有简单的 `@e` 引用系统用于元素交互。

![Agentic Browser](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kgjw8atdxgkrsr8a2t5peq7b.jpeg)

## 快速入门

> 需要 inference.sh CLI (`belt`)。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# 打开页面并获取交互元素
belt app run agent-browser --function open --input '{"url": "https://example.com"}' --session new
```

## 核心工作流

每个浏览器自动化都遵循此模式：

1. **打开** - 导航到 URL，获取元素的 `@e` 引用
2. **交互** - 使用引用点击、填充、拖动等
3. **重新快照** - 导航/更改后，获取新的引用
4. **关闭** - 结束会话（如果正在录制，则返回视频）

```bash
# 1. 开始会话
RESULT=$(belt app run agent-browser --function open --session new --input '{
  "url": "https://example.com/login"
}')
SESSION_ID=$(echo $RESULT | jq -r '.session_id')
# 元素：@e1 [a] "Home" href="/", @e2 [input type="text"] placeholder="Search", @e3 [button] "Submit", @e4 [select] "Choose option", @e5 [input type="checkbox"] name="agree"

# 2. 填充并提交
belt app run agent-browser --function interact --session $SESSION_ID --input '{
  "action": "fill", "ref": "@e1", "text": "user@example.com"
}'
belt app run agent-browser --function interact --session $SESSION_ID --input '{
  "action": "fill", "ref": "@e2", "text": "password123"
}'
belt app run agent-browser --function interact --session $SESSION_ID --input '{
  "action": "click", "ref": "@e3"
}'

# 3. 导航后重新快照
belt app run agent-browser --function snapshot --session $SESSION_ID --input '{}'

# 4. 完成时关闭
belt app run agent-browser --function close --session $SESSION_ID --input '{}'
```

## 功能

| 功能 | 描述 |
|----------|-------------|
| `open` | 导航到 URL，配置浏览器（视口、代理、视频录制） |
| `snapshot` | DOM 变更后重新获取页面状态，带有 `@e` 引用 |
| `interact` | 使用 `@e` 引用执行操作（点击、填充、拖动、上传等） |
| `screenshot` | 拍摄页面截图（视口或全页） |
| `execute` | 在页面运行 JavaScript 代码 |
| `close` | 关闭会话，如果录制已启用，则返回视频 |

## 交互操作

| 操作 | 描述 | 必填字段 |
|--------|-------------|-----------------|
| `click` | 点击元素 | `ref` |
| `dblclick` | 双击元素 | `ref` |
| `fill` | 清除并输入文本 | `ref`, `text` |
| `type` | 输入文本（不清除） | `text` |
| `press` | 按键（Enter、Tab 等） | `text` |
| `select` | 选择下拉选项 | `ref`, `text` |
| `hover` | 悬停在元素上 | `ref` |
| `check` | 勾选复选框 | `ref` |
| `uncheck` | 取消勾选复选框 | `ref` |
| `drag` | 拖动 | `ref`, `target_ref` |
| `upload` | 上传文件 | `ref`, `file_paths` |
| `scroll` | 滚动页面 | `direction` (up/down/left/right), `scroll_amount` |
| `back` | 历史记录后退 | - |
| `wait` | 等待毫秒 | `wait_ms` |
| `goto` | 导航到 URL | `url` |

## 元素引用

元素使用 `@e` 引用返回：

```
@e1 [a] "Home" href="/"
@e2 [input type="text"] placeholder="Search"
@e3 [button] "Submit"
@e4 [select] "Choose option"
@e5 [input type="checkbox"] name="agree"
```

**重要提示：** 导航后引用会失效。以下情况后必须重新快照：
- 点击导航链接/按钮
- 表单提交
- 动态内容加载

## 功能特性

### 视频录制

录制浏览器会话用于调试或文档：

```bash
# 启动时启用录制（可选显示光标指示器）
SESSION=$(belt app run agent-browser --function open --session new --input '{
  "url": "https://example.com",
  "record_video": true,
  "show_cursor": true
}' | jq -r '.session_id')

# ... 执行操作 ...

# 关闭以获取视频文件
belt app run agent-browser --function close --session $SESSION --input '{}'
# 返回：{"success": true, "video": <File>}
```

### 光标指示器

在截图和视频中显示可见光标（用于演示）：

```bash
belt app run agent-browser --function open --session new --input '{
  "url": "https://example.com",
  "show_cursor": true,
  "record_video": true
}'
```

光标显示为红色圆点，跟随鼠标移动并显示点击反馈。

### 代理支持

通过代理服务器路由流量：

```bash
belt app run agent-browser --function open --session new --input '{
  "url": "https://example.com",
  "proxy_url": "http://proxy.example.com:8080",
  "proxy_username": "user",
  "proxy_password": "pass"
}'
```

### 文件上传

上传文件到文件输入：

```bash
belt app run agent-browser --function interact --session $SESSION --input '{
  "action": "upload",
  "ref": "@e5",
  "file_paths": ["/path/to/file.pdf"]
}'
```

### 拖放

拖动元素到目标：

```bash
belt app run agent-browser --function interact --session $SESSION --input '{
  "action": "drag",
  "ref": "@e1",
  "target_ref": "@e2"
}'
```

### JavaScript 执行

运行自定义 JavaScript：

```bash
belt app run agent-browser --function execute --session $SESSION --input '{
  "code": "document.querySelectorAll(\"h2\").length"
}'
# 返回：{"result": "5", "screenshot": <File>}
```

## 深入文档

| 参考 | 描述 |
|-----------|-------------|
| [references/commands.md](references/commands.md) | 完整功能参考，包含所有选项 |
| [references/snapshot-refs.md](references/snapshot-refs.md) | 引用生命周期、失效规则、故障排除 |
| [references/session-management.md](references/session-management.md) | 会话持久化、并行会话 |
| [references/authentication.md](references/authentication.md) | 登录流程、OAuth、双因素认证处理 |
| [references/video-recording.md](references/video-recording.md) | 用于调试的录制工作流 |
| [references/proxy-support.md](references/proxy-support.md) | 代理配置、地理测试 |

## 即用模板

| 模板 | 描述 |
|----------|-------------|
| [templates/form-automation.sh](templates/form-automation.sh) | 带验证的表单填写 |
| [templates/authenticated-session.sh](templates/authenticated-session.sh) | 登录一次，重用会话 |
| [templates/capture-workflow.sh](templates/capture-workflow.sh) | 带截图的内容提取 |

## 示例

### 表单提交

```bash
SESSION=$(belt app run agent-browser --function open --session new --input '{
  "url": "https://example.com/contact"
}' | jq -r '.session_id')

# 获取元素：@e1 [input] "Name", @e2 [input] "Email", @e3 [textarea], @e4 [button] "Send"

belt app run agent-browser --function interact --session $SESSION --input '{"action": "fill", "ref": "@e1", "text": "John Doe"}'
belt app run agent-browser --function interact --session $SESSION --input '{"action": "fill", "ref": "@e2", "text": "john@example.com"}'
belt app run agent-browser --function interact --session $SESSION --input '{"action": "fill", "ref": "@e3", "text": "Hello!"}'
belt app run agent-browser --function interact --session $SESSION --input '{"action": "click", "ref": "@e4"}'

belt app run agent-browser --function snapshot --session $SESSION --input '{}'
belt app run agent-browser --function close --session $SESSION --input '{}'
```

### 搜索和提取

```bash
SESSION=$(belt app run agent-browser --function open --session new --input '{
  "url": "https://google.com"
}' | jq -r '.session_id')

belt app run agent-browser --function interact --session $SESSION --input '{"action": "fill", "ref": "@e1", "text": "weather today"}'
belt app run agent-browser --function interact --session $SESSION --input '{"action": "press", "text": "Enter"}'
belt app run agent-browser --function interact --session $SESSION --input '{"action": "wait", "wait_ms": 2000}'

belt app run agent-browser --function snapshot --session $SESSION --input '{}'
belt app run agent-browser --function close --session $SESSION --input '{}'
```

### 带视频的截图

```bash
SESSION=$(belt app run agent-browser --function open --session new --input '{
  "url": "https://example.com",
  "record_video": true
}' | jq -r '.session_id')

# 拍摄全页截图
belt app run agent-browser --function screenshot --session $SESSION --input '{
  "full_page": true
}'

# 关闭并获取视频
RESULT=$(belt app run agent-browser --function close --session $SESSION --input '{}')
echo $RESULT | jq '.video'
```

## 会话

浏览器状态在会话内持续。始终：

1. 首次调用时使用 `--session new` 启动
2. 使用返回的 `session_id` 进行后续调用
3. 完成时关闭会话

## 相关技能

```bash
# 网络搜索（用于研究 + 浏览）
npx skills add inference-sh/skills@web-search

# 大语言模型（分析提取内容）
npx skills add inference-sh/skills@llm-models
```

## 文档

- [inference.sh 会话](https://inference.sh/docs/extend/sessions) - 会话管理
- [多功能应用](https://inference.sh/docs/extend/multi-function-apps) - 功能工作原理
