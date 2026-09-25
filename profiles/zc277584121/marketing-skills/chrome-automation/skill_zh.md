# 技能：Chrome 自动化 (agent-browser)

通过 [agent-browser](https://github.com/vercel-labs/agent-browser) CLI 在用户真实的 Chrome 会话中自动执行浏览器任务。

> **前提条件**：必须安装 agent-browser，并且 Chrome 必须启用远程调试。如有疑问，请参阅 `references/agent-browser-setup.md`。

---

## 核心原则：复用用户现有的 Chrome

此技能基于**单个 Chrome 进程**——即用户正在使用的真实浏览器。它不进行会话管理，不创建独立配置文件，也不启动新的 Playwright 浏览器。

### 始终先列出标签页

在打开任何新页面之前，**始终先列出现有标签页**：

```bash
agent-browser --auto-connect tab list
```

这将返回所有打开的标签页及其索引号、标题和 URL。检查您需要的页面是否已经打开：

- **如果目标页面已经打开** → 直接切换到该标签页，而不是打开新页面。用户可能已经打开该页面，因为他们已经登录，并且页面处于正确状态。
  ```bash
  agent-browser --auto-connect tab <索引号>
  ```
- **如果目标页面未打开** → 在当前标签页或新标签页中打开它。
  ```bash
  agent-browser --auto-connect open <URL>
  ```

### 这为何重要

- 用户的 Chrome 包含他们的 cookie、登录会话和浏览器状态
- 当一个页面已经可用时再打开新页面会浪费时间，并可能丢失登录状态
- 许多营销平台（社交媒体控制台、广告管理器、CMS 工具）需要登录——复用现有的已登录标签页可以避免重新认证

---

## 连接

始终使用 `--auto-connect` 连接到用户正在运行的 Chrome 实例：

```bash
agent-browser --auto-connect <命令>
```

这将自动发现已启用远程调试的 Chrome。如果连接失败，请指导用户启用远程调试（参见 `references/agent-browser-setup.md`）。

### Chrome 144+ 仅 WebSocket 回退

Chrome 144+ 可以将远程调试从 `chrome://inspect/#remote-debugging` 暴露为仅 WebSocket 的端点。在该状态下，页面显示 `Server running at: 127.0.0.1:9222`，但传统的发现 URL 会返回 404：

```bash
curl http://127.0.0.1:9222/json/version
curl http://127.0.0.1:9222/json/list
```

较旧的 `agent-browser` 版本（如 `0.27.x`）可能会失败并显示 `No running Chrome instance found`，即使 Chrome 已经准备好。首先尝试最新 CLI，而不更改全局安装：

```bash
npx -y agent-browser@latest connect "ws://127.0.0.1:9222/devtools/browser"
npx -y agent-browser@latest tab list
```

如果这可以工作，则对于其余的浏览器任务使用 `npx -y agent-browser@latest <命令>`。如果它因引擎警告或安装错误而失败，请升级 Node 到 24+ 或全局安装最新的 `agent-browser`。

---

## 常见工作流程

### 1. 导航和交互

```bash
# 列出标签页以查找现有页面
agent-browser --auto-connect tab list

# 切换到现有标签页（如果找到）
agent-browser --auto-connect tab <索引号>

# 或者打开新页面
agent-browser --auto-connect open https://example.com
agent-browser --auto-connect wait --load networkidle

# 拍摄快照以查看交互元素
agent-browser --auto-connect snapshot -i

# 点击、填写等
agent-browser --auto-connect click @e3
agent-browser --auto-connect fill @e5 "some text"
```

### 2. 从页面提取数据

```bash
# 获取所有文本内容
agent-browser --auto-connect get text body

# 拍摄屏幕截图以进行视觉检查
agent-browser --auto-connect screenshot

# 执行 JavaScript 以获取结构化数据
agent-browser --auto-connect eval "JSON.stringify(document.querySelectorAll('table tr').length)"
```

### 3. 重放 Chrome DevTools 录制

用户可能提供了从 Chrome DevTools Recorder 导出的录制（JSON、Puppeteer JS 或 @puppeteer/replay JS 格式）。参见下文的“重放录制”部分。

## 分步交互指南

### 拍摄快照

使用 `snapshot -i` 查看所有交互元素及其引用（`@e1`、`@e2`、...）：

```bash
agent-browser --auto-connect snapshot -i
```

输出将列出每个交互元素及其角色、文本和引用。使用这些引用进行后续操作。

### 步骤类型映射

| 操作 | 命令 |
|------|------|
| 导航 | `agent-browser --auto-connect open <URL>`（可选 `wait --load networkidle`，但某些网站如 Reddit 永远不会达到 networkidle——如果 `open` 已经显示页面标题则跳过） |
| 点击 | `snapshot -i` → 找到引用 → `click @eN` |
| 填写标准输入 | `click @eN` → `fill @eN "text"` |
| 填写富文本编辑器 | `click @eN` → `keyboard inserttext "text"` |
| 按键 | `press <key>`（Enter、Tab、Escape 等） |
| 滚动 | `scroll down <amount>` 或 `scroll up <amount>` |
| 等待元素 | `wait @eN` 或 `wait "<css-selector>"` |
| 屏幕截图 | `screenshot` 或 `screenshot --annotate` |
| 获取页面文本 | `get text body` |
| 获取当前 URL | `get url` |
| 运行 JavaScript | `eval <js>` |

### 如何区分输入类型

- **标准输入/textarea** → 使用 `fill`
- **可编辑 div / 富文本编辑器**（LinkedIn 消息框、Gmail 撰写、Slack、CMS 编辑器）→ 点击/聚焦第一个，然后使用 `keyboard inserttext`

### 引用生命周期

引用（`@e1`、`@e2`、...）在页面更改时**失效**。在以下情况下始终重新快照：
- 点击触发导航的链接或按钮
- 提交表单
- 触发动态内容加载（AJAX、SPA 导航）

### 验证

每次执行重要操作后，验证结果：
```bash
agent-browser --auto-connect snapshot -i   # 检查交互状态
agent-browser --auto-connect screenshot     # 视觉验证
```

---

## 重放录制

### 接受的格式

1. **JSON**（推荐）——结构化，可以逐步读取：
   ```bash
   # 计算步骤数量
   jq '.steps | length' recording.json

   # 读取前 5 步
   jq '.steps[0:5]' recording.json
   ```

2. **@puppeteer/replay JS** (`import { createRunner }`)
3. **Puppeteer JS** (`require('puppeteer')`, `page.goto`, `Locator.race`)

### 如何重放

1. **解析录制**——在执行操作之前理解完整意图。总结录制的作用。
2. **先列出标签页**——检查目标页面是否已经打开。
3. **导航**——执行 `navigate` 步骤，尽可能复用现有标签页。
4. **对于每个交互步骤**：
   - 拍摄快照 (`snapshot -i`) 以查看当前交互元素
   - 将录制的 `aria/...` 选择器与快照匹配
   - 如果需要，回退到 `text/...`，然后是 CSS 类提示，最后是屏幕截图
   - **不要依赖 ember ID、数字 ID 或精确的 XPATH**——这些每次页面加载都会变化
   - **验证**——屏幕截图或快照确认

---

## 嵌套 iframe 网站处理

`snapshot -i` 仅对主框架操作，**无法穿透 iframe**。LinkedIn、Gmail 和嵌入式编辑器等网站将内容渲染在 iframe 内。

### 检测 iframe 问题

- `snapshot -i` 返回意外的短或空结果
- 录制引用的元素未出现在快照输出中
- `get text body` 内容与屏幕截图显示的不符

### 解决方法

1. **使用 `eval` 访问 iframe 内容**：
   ```bash
   agent-browser --auto-connect eval --stdin <<'EVALEOF'
   const frame = document.querySelector('iframe[data-testid="interop-iframe"]');
   const doc = frame.contentDocument;
   const btn = doc.querySelector('button[aria-label="Send"]');
   btn.click();
   EVALEOF
   ```
   注意：仅适用于同源 iframe。

2. **使用 `keyboard` 进行盲输入**：如果 iframe 元素有焦点，`keyboard inserttext "..."` 会发送文本，而不管 iframe 边界如何。

3. **使用 `get text body`** 读取包括 iframe 在内的完整页面内容。

4. **使用 `screenshot`** 进行视觉验证，当快照不可靠时。

### 需要询问用户的情况

如果尝试相同步骤的解决方法失败 2 次，暂停并解释：
- 页面使用 iframe，无法通过快照访问
- 您需要哪个元素以及您的预期
- 请求用户手动执行该步骤，然后继续

---

## 处理意外情况

### 自动处理（不要停止）：

- 弹窗或横幅 → 关闭它们 (`find text "Dismiss" click` 或 `find text "Close" click`)
- Cookie 同意对话框 → 接受或关闭
- 提示框覆盖层 → 首先关闭它们
- 快照中未找到元素 → 尝试 `find text "..." click`，或使用 `scroll down 300` 滚动以显示

### 暂停并询问用户：

- 需要登录/认证
- 出现 CAPTCHA
- 页面结构与预期完全不同
- 即将执行破坏性操作（删除数据、发送真实内容）——先确认
- 在同一步骤上卡住超过 2 次
- 所有 iframe 解决方法都失败

暂停时，请清晰解释：您当前的步骤、预期结果以及实际看到的内容。

---

## 关键命令参考

| 命令 | 描述 |
|------|------|
| `tab list` | 列出所有打开的标签页及其索引号、标题和 URL |
| `tab <索引号>` | 通过索引号切换到现有标签页 |
| `tab new` | 打开一个新的空白标签页 |
| `tab close` | 关闭当前标签页 |
| `open <URL>` | 导航到 URL |
| `snapshot -i` | 列出交互元素及其引用 |
| `click @eN` | 通过引用点击元素 |
| `fill @eN "text"` | 清空并填写标准输入/textarea |
| `type @eN "text"` | 不清除地输入 |
| `keyboard inserttext "text"` | 插入文本（最适合可编辑内容） |
| `press <key>` | 按键盘键 |
| `scroll down/up <amount>` | 以像素为单位滚动页面 |
| `wait @eN` | 等待元素出现 |
| `wait --load networkidle` | 等待网络稳定 |
| `wait <ms>` | 等待一段时间 |
| `screenshot [路径]` | 拍摄屏幕截图 |
| `screenshot --annotate` | 带编号标签的屏幕截图 |
| `eval <js>` | 在页面中执行 JavaScript |
| `get text body` | 获取所有文本内容 |
| `get url` | 获取当前 URL |
| `set viewport <w> <h>` | 设置视口大小 |
| `find text "..." click` | 语义查找并点击 |
| `close` | 关闭浏览器会话 |

---

## 已知限制

1. **iframe 盲点**：`snapshot -i` 无法查看 iframe 内部。参见“嵌套 iframe 网站处理”部分。
2. **`find text` 严格模式**：当多个元素匹配时失败。使用 `snapshot -i` 定位特定引用。
3. **`fill` 与可编辑内容**：`fill` 仅适用于 `<input>` 和 `<textarea>`。对于富文本编辑器，使用 `keyboard inserttext`。
4. **`eval` 仅主框架**：要交互 iframe 内容，通过 `document.querySelector('iframe').contentDocument...` 遍历。

---

## 多平台操作

当用户请求跨**多个平台**的操作（例如，“将这篇文章发布到 Dev.to、LinkedIn 和 X”）时，**不要**在单个对话中尝试所有平台。相反，启动**顺序子代理/工作进程**，每个平台一个。选择此技能即表示允许使用子代理/工作进程进行此多平台工作流程。

### 使用子代理的原因

每个平台操作消耗约 25-40K token（参考文件 + 快照 + 交互）。在一个上下文中运行 3-5 个平台有风险超出上下文限制并降低后期平台的准确性。每个子代理/工作进程都有自己的新鲜上下文窗口。

### 如何执行

1. **准备内容**——与用户确认发布文本、标题、标签和任何平台特定调整。
2. **对于每个平台**，启动子代理/工作进程，其提示包括：
   - 要发布的完整内容
   - 指示读取相关参考文件（例如，`Read /path/to/skills/chrome-automation/references/x.md`）
   - 指示读取 agent-browser 技能文件以获取命令参考
   - 具体任务（发布、评论、回复等）
   - 任何平台特定指示（例如，“在 LinkedIn 上使用这些标签”）
3. **顺序运行子代理/工作进程**（一次一个），因为它们都通过 `--auto-connect` 共享同一个 Chrome 浏览器。并行子代理/工作进程会导致标签页冲突。
4. **每个子代理/工作进程完成后**，在启动下一个之前向用户报告结果。

### 子代理提示模板

```
您正在自动化 [平台] 上的浏览器任务。

首先，读取以下文件以获取上下文：
- /绝对路径/to/skills/chrome-automation/references/[平台].md
- 安装的 agent-browser 技能文件（如果可用）（agent-browser 命令参考）

然后使用 `agent-browser --auto-connect` 连接到用户的 Chrome 浏览器并执行以下任务：

[任务描述]

要发布的内容：
[内容]

重要：
- 始终先列出标签页 (`tab list`) 并复用现有的已登录标签页
- 每次导航或操作后重新快照
- 提交/发布前与用户确认（破坏性操作）
- 如果需要登录或出现 CAPTCHA，停止并解释
```

### 不应使用子代理的情况

- **单个平台**——直接在当前对话中处理。
- **只读任务**（浏览、搜索、提取数据）——上下文使用较轻；单个对话可以处理 2-3 个平台。

---

## 平台参考

在特定平台上自动化任务时，参考相关参考文档以获取页面结构细节、常见操作和已知问题：

| 平台 | 参考 | 关键备注 |
|------|------|------|
| Reddit | [`references/reddit.md`](./references/reddit.md) | 自定义 `faceplate-*` 组件；`networkidle` 永远不会达到；未标记的评论文本框；`find text` 因重复元素失败 |
| X (Twitter) | [`references/x.md`](./references/x.md) | `open` 常常超时（使用 `tab list` 复用现有标签页）；点击 **时间戳** 获取帖子详情（不是用户名）；DraftJS 富文本输入 (`data-testid="tweetTextarea_0"`)；避免 `networkidle` |
| LinkedIn | [`references/linkedin.md`](./references/linkedin.md) | Ember.js SPA；Enter 提交评论（使用 Shift+Enter 换行）；评论框和撰写框共享相同标签；避免 `networkidle`；消息覆盖层可能阻挡内容 |
| Dev.to | [`references/devto.md`](./references/devto.md) | 快速服务器渲染的 HTML（Forem/Rails）；标准 `<textarea>` 用于评论/帖子（Markdown）；5 种反应类型；Algolia 驱动的搜索；`networkidle` 正常工作 |
| Hacker News | [`references/hackernews.md`](./references/hackernews.md) | 最小化纯 HTML；所有表单字段均未标记；`link "reply"` 导航到单独页面；`networkidle` 瞬间完成；对帖子/评论有限制 |

---

> 关于安装和 Chrome 设置说明，请参阅 [`references/agent-browser-setup.md`](./references/agent-browser-setup.md)。
