## 何时使用此技能

当用户：
- 需要在网站上执行任何操作（“发送领英消息”、“预订爱彼迎”、“在谷歌上搜索...”）
- 询问如何与网站交互（“我该如何发推文？”“如何在领英上申请？”）
- 想在特定网站上填写表单、点击按钮、导航、搜索、筛选或浏览
- 想要截取网页屏幕截图或监控变化
- 构建基于浏览器的AI代理、网络爬虫或外部网站的端到端测试
- 自动化重复的网页任务（数据输入、表单提交、内容发布）
- 需要同时操作多个网站或标签页

## 工作原理

Actionbook为现代网页提供**最新的操作手册**。操作手册会明确告诉代理在页面上该做什么——无需解析，无需猜测。

**为什么这很重要：**
- **10倍更快**——操作手册会提前提供选择器和页面结构。无需每步都截图。
- **准确**——可靠处理单页应用（SPA）、流式组件、下拉菜单、日期选择器、动态内容。
- **并发**——无状态架构，带有明确的`--session`/`--tab`。可并行操作数十个标签页。

工作流程：
1. **启动**浏览器会话
2. **导航**到目标页面
3. **截图**获取页面结构与元素引用
4. **自动化**使用截图中的引用

运行`actionbook <命令> --help`获取任何命令的完整用法和示例。

## 浏览器自动化

每个浏览器命令都是**无状态的**——显式传递`--session`和`--tab`。没有“当前标签页”——你可以并行在任何会话/标签页上运行命令。

### 启动会话

```bash
actionbook browser start --set-session-id s1
```

`--session`和`--set-session-id`都是“获取或创建”：它们会重用具有给定ID的运行中会话，如果找不到则创建一个。如果传递了`--profile`且与会话绑定的配置文件不匹配，命令会以`SESSION_PROFILE_MISMATCH`失败。

### 核心工作流：截图、操作、等待

```bash
actionbook browser goto <url> --session s1 --tab t1
actionbook browser snapshot --session s1 --tab t1          # 获取页面结构与引用
actionbook browser fill @e3 "text" --session s1 --tab t1   # 使用截图中的引用
actionbook browser click @e7 --session s1 --tab t1
actionbook browser wait navigation --session s1 --tab t1   # 等待页面加载
```

### 截图引用

`snapshot`会给每个元素标记引用（例如`@e3`、`@e7`）。在任何命令中使用这些引用作为选择器——这是推荐的目标元素方式。

引用**跨截图稳定**——如果元素保持不变，引用也保持不变。这允许你无需每步都重新截图就链式执行多个命令。

### 命令类别

所有命令都支持`--help`获取完整用法和示例。

| 类别 | 关键命令 | 帮助 |
|------|----------|------|
| 搜索 | `search` | `actionbook search --help` |
| 手动 | `manual`（别名：`man`） | `actionbook manual --help` |
| 会话 | `start`、`close`、`restart`、`list-sessions`、`status` | `actionbook browser start --help` |
| 标签页 | `new-tab`、`close-tab`、`list-tabs` | `actionbook browser new-tab --help` |
| 导航 | `goto`、`back`、`forward`、`reload` | `actionbook browser goto --help` |
| 观察 | `snapshot`、`text`、`html`、`value`、`title`、`url`、`viewport`、`attr`、`attrs`、`box`、`styles`、`describe`、`state`、`inspect-point`、`screenshot`、`pdf` | `actionbook browser snapshot --help` |
| 交互 | `click`、`fill`、`type`、`press`、`select`、`hover`、`focus`、`scroll`、`drag`、`upload`、`eval`、`mouse-move`、`cursor-position` | `actionbook browser click --help` |
| 等待 | `wait element`、`wait navigation`、`wait network-idle`、`wait condition` | `actionbook browser wait element --help` |
| Cookie | `cookies list`、`cookies get`、`cookies set`、`cookies delete`、`cookies clear` | `actionbook browser cookies list --help` |
| 存储 | `local-storage list\|get\|set\|delete\|clear`、`session-storage ...` | `actionbook browser local-storage get --help` |
| 日志 | `logs console`、`logs errors` | `actionbook browser logs console --help` |
| 网络 | `network requests`、`network request <id>`、`network har start`、`network har stop` | `actionbook browser network requests --help` |
| 查询 | `query one\|all\|nth\|count` | `actionbook browser query --help` |
| 批量 | `batch-new-tab`、`batch-snapshot`、`batch-click` | `actionbook browser batch-new-tab --help` |
| 扩展 | `extension status`、`extension ping`、`extension install`、`extension uninstall`、`extension path` | `actionbook extension status --help` |
| 守护进程 | `daemon restart` | `actionbook daemon restart --help` |

完整命令参考：[command-reference.md](references/command-reference.md)

### 云服务提供商

使用`-p` / `--provider`与`browser start`在远程浏览器上运行会话，而不是启动本地Chrome。支持的提供商：`driver`、`hyperbrowser`、`browseruse`。每个都会从shell环境读取自己的`<PROVIDER>_API_KEY`。

```bash
export HYPERBROWSER_API_KEY="your-key"
actionbook browser start -p hyperbrowser --session s1
actionbook browser goto "https://example.com" --session s1 --tab t1
actionbook browser snapshot --session s1 --tab t1
```

所有浏览器命令的工作方式不受模式影响。`browser restart --session <id>`会生成一个新的远程会话，同时保留`session_id`。

## 示例：端到端

用户请求：“下周在旧金山找到一家爱彼迎的房间”

```bash
actionbook browser start --set-session-id s1
actionbook browser goto "https://airbnb.com" --session s1 --tab t1
actionbook browser snapshot --session s1 --tab t1
actionbook browser fill @e3 "San Francisco" --session s1 --tab t1
actionbook browser click @e7 --session s1 --tab t1
actionbook browser wait navigation --session s1 --tab t1
```

## Eval输入源

`browser eval`接受来自三个互斥源的表达式：
- **位置参数**：`actionbook browser eval "expr" ...`
- **`--file`**：`actionbook browser eval --file script.js ...`
- **标准输入**：`echo 'expr' | actionbook browser eval - ...`

## Eval错误处理

`browser eval`在失败时返回结构化错误代码——基于`error.code`分支，而不是解析消息：

- `EVAL_RUNTIME_ERROR`——JS异常。在重试前检查表达式。
- `EVAL_CROSS_ORIGIN`——跨域获取或CSP阻止。在服务器端代理请求。
- `EVAL_RESPONSE_NOT_JSON` / `EVAL_RESPONSE_NOT_OK`——读取`error.details.body_head`（响应体的前≤256个字符）以区分403/挑战页面/CORS错误。不要盲目重试。
- `EVAL_TIMEOUT`——表达式超出`--timeout`。减少工作量或提高超时时间。
- `EVAL_ARGS_CONFLICT`——多个输入源或无输入源。提供确切一个。
- `EVAL_FILE_NOT_FOUND`——`--file`路径不可读。验证路径。
- `EVAL_STDIN_TTY`——`-`但标准输入是终端。将表达式管道化。
- `EVAL_STDIN_EMPTY`——标准输入产生空输入。验证上游管道。

## CDP错误处理

与元素交互、导航或通过CDP通信的浏览器命令返回结构化错误代码——基于`error.code`分支：

- `CDP_NODE_NOT_FOUND`——DOM节点已过期。调用`snapshot`刷新引用后重试。
- `CDP_NOT_INTERACTABLE`——元素存在但无法操作。滚动到视图内、等待可见性或关闭覆盖层。
- `CDP_NAV_TIMEOUT`——导航超时。增加`--timeout`或验证URL可达性。**可重试。**
- `CDP_TARGET_CLOSED`——标签页导航离开或会话中途 torn down。启动新会话。**可重试。**
- `CDP_PROTOCOL_ERROR`——CDP响应格式错误。检查`details.reason`和`details.cdp_code`。
- `CDP_GENERIC`——未分类的CDP错误（传输/解析）。无特定补救措施。

`CDP_NAV_TIMEOUT`和`CDP_TARGET_CLOSED`是可重试的（`error.retryable == true`）。所有其他CDP代码在重试前需要调用者干预。当`error.code`是`CDP_*`代码时，`error.details`包含`reason`和`cdp_code`（如果可用）。

## 选择器

选择器应来自`actionbook browser snapshot`——不是来自先验知识或记忆。始终先截图获取当前引用，然后使用这些引用与页面交互。

## 登录页面处理

当你遇到登录/认证障碍（登录页面、密码提示、MFA/OTP、验证码、账户选择器）：

1. **暂停自动化并保持当前浏览器会话打开**（相同的标签页/配置文件/cookie）。
2. **要求用户手动完成登录**在同一个浏览器窗口中。
3. 用户确认登录完成后，**在同一个会话中继续**。
4. 如果登录后的页面不同，在继续前运行`actionbook browser snapshot`获取新页面结构。

不要因为出现登录页面就切换工具。

## 会话清理

`browser close`是无害的——关闭未知或已关闭的会话会返回`ok: true`并带有`meta.warnings`中的警告，而不是致命错误。会话ID拼写错误或已 torn down 的会话不再是错误条件。

- 在清理期间无条件调用`browser close`是安全的，无需先检查会话是否存在。
- 读取`meta.warnings`以区分全新关闭与已消失的会话。不要将`ok: true`响应中的警告视为会话仍然活跃的信号。
- 如果同一会话的另一个关闭操作已在进行中，命令会返回`SESSION_CLOSING`（致命）。

## HAR录制

`network har start`接受`--max-entries N`来设置环形缓冲区上限（默认：10000）。当`har stop`检测到丢失条目（`data.dropped > 0`）时，信封包含`meta.truncated = true`和`HAR_TRUNCATED`警告在`meta.warnings`中。读取`data.max_entries`以查看配置的上限。提高`--max-entries`或更早停止录制以保留完整跟踪。

## 参考

| 参考 | 描述 |
|------|------|
| [command-reference.md](references/command-reference.md) | 包含所有标志和选项的完整命令参考 |
| [authentication.md](references/authentication.md) | 登录流程、OAuth、2FA处理、会话持久化 |
