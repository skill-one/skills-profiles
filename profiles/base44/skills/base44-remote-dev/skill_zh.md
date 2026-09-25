<!--  
  从 base44-dev/apper PR #11608 衍生  
  (docs/features/bring-your-own-model/base44-remote-dev/SKILL.md)。  
  如果上游源代码发生变化，请保持同步。  
-->  

# 通过 MCP 远程开发 Base44 应用  

将您自己的编码代理连接到 Base44 应用的沙盒，并直接在其中进行开发  
—— 运行命令、读取和编辑文件、grep、列出目录 —— 同时 Base44 提供沙盒，您提供代理和 LLM。  

此方法适用于任何支持 MCP 的客户端。示例使用 Claude Code。  

> **最容易开始的方式：** 在 Base44 应用编辑器中，点击 **发送到编码代理**。对于本地代理  
> 它会为您提供可粘贴的提示（该提示会获取 README 并通过 MCP 或 `base44 sandbox` CLI — 第 10 节）驱动沙盒；  
> 对于网页它会提供一个提示粘贴到 **claude.ai** 聊天中（带有 Base44 MCP 连接器）  
> 加上一个 **打开 Claude** 按钮。按钮是发现界面 —— 本技能的其余部分是参考。  

> **两种传输方式：** 网页代理使用 **claude.ai** 并带有 Base44 **MCP 连接器**（第 1-9 节）——  
> 请注意这是常规的 claude.ai 聊天，*不是* 网络上的 Claude Code (`claude.ai/code`)，  
> 后者运行在自己的仓库支持的沙盒中。本地代理可以连接相同的 MCP 服务器，或使用 **`base44 sandbox` CLI**（Base44 CLI 令牌，第 10 节）  
> 相同的工具、相同的行为、相同的错误代码；CLI 只是使用较短的命令名暴露它们（`sandbox read`，`sandbox ls`，…）。  

---

## 1. 连接 MCP 服务器  

Base44 MCP 端点是：  

```
https://app.base44.com/mcp
```

使用 Claude Code（在任何文件夹中运行）注册它：  

```bash
claude mcp add --transport http base44 https://app.base44.com/mcp
```

如果希望它在每个项目中可用而不是仅在当前文件夹中，请添加 `--scope user`。  

`claude mcp add` 仅写入配置 —— 它尚未进行身份验证。  

## 2. 身份验证  

启动 Claude Code 并打开 MCP 菜单：  

```bash
claude
```

然后在 Claude Code 中：  

```
/mcp
```

选择 **base44** → **身份验证**。浏览器将打开 Base44 OAuth 流（PKCE）—— 登录并批准。成功后，`/mcp` 显示 **base44** 已连接并列出其工具。  

**纯 CLI / 无头客户端** 无法打开浏览器，则使用 OAuth 设备流（`/oauth/device/code`）——  
请求一个代码，在另一台设备上的浏览器中批准，客户端将接收令牌。  

### 权限范围  

| 工具 | 必需的权限范围 |  
|---|---|  
| `read_file`，`grep`，`list_directory`，`get_app_preview_url`，`get_app_status`，`list_user_apps` | `apps:read`（默认授予） |  
| `write_file`，`edit_file`，`run_command`，`create_checkpoint` | `sandbox:write` |  

`sandbox:write` **不是** 默认授予的 —— 命令行和文件修改需要明确授权。如果读取工具可以工作，但修改工具返回 `NOT_AUTHORIZED`，  
则您的令牌缺少 `sandbox:write`；重新连接并授予沙盒访问权限（设备流可以明确请求它）。  

---

## 3. 选择应用并熟悉环境  

每个工具都需要一个必需的 `appId`。使用 `list_user_apps` 找到您的应用，然后在请求中固定 id，以便代理在每次调用时传递它。  

在更改任何内容之前，先以 **只读** 方式构建心理模型：  

```
使用 base44 工具在 appId <APP_ID> 上：  
1. 在应用根目录上执行 list_directory（递归，深度 2）  
2. read_file src/App.jsx 和 src/pages.config.js  
3. grep 我要更改的组件  
在编辑前总结结构。  
```

> **冷启动：** 如果应用没有运行中的沙盒，第一个工具调用将透明地从您的最后一次提交中启动一个沙盒 —— 它只是需要稍长时间。后续调用很快。  

> **CLI 名称：** 通过 `base44 sandbox` CLI（第 10 节）这些读取工具是  
> `list_directory` → `sandbox ls`，`read_file` → `sandbox read`，和  
> `grep` → `sandbox grep`。  

---

## 4. 进行更改  

- **`edit_file`**（CLI 中的 `sandbox edit`）—— 修改现有文件的首选方式。提供确切的  
  `old_text`→`new_text` 编辑。每个 `old_text` 在文件中必须唯一，除非您设置 `replace_all`。  
  每次调用中的所有编辑都是原子性的（全有或全无），并返回统一的差异。传递 `dry_run: true` 以预览差异而不写入。  
- **`write_file`**（CLI 中的 `sandbox write`）—— 创建新文件。要覆盖现有文件，必须传递 `overwrite: true`（它从不默默覆盖）。  
- **`run_command`**（CLI 中的 `sandbox run`）—— 在沙盒中运行任何 bash 命令（构建、安装、脚手架、代码修改）。工作目录默认为应用根目录；`cd`  
  在调用之间不会持久化，因此使用 `cwd` 参数或链式命令（`cd sub && cmd`）。超时默认为 120 秒（最大 600 秒）；输出限制在约 1 MB。  
- **`create_checkpoint`**（CLI 中的 `sandbox checkpoint`）—— 在构建的版本历史中保存一个恢复点。可以传递可选的 `name`（消息/标题；如果省略则自动生成——  
  变更的简短摘要有助于用户选择正确的版本）。任何待处理的更改都会**首先刷新并提交**，以便检查点锚定到您的最新代码；然后返回检查点 id、名称和 git 提交哈希。**在完成一个工作单元并停止之前调用它**——  
  第 6 节解释了为什么未检查点的工作可能会被回滚。  
  （如果最近的自动提交还不能确认是持久的，它将拒绝 `COMMIT_FLUSH_PENDING` 而不是检查点过时的状态——稍后重试。）  

示例：  

```
在 appId <APP_ID> 上，使用 edit_file 将 src/pages/Home.jsx 中的主页标题从 "Welcome" 改为 "Welcome back"。  
首先使用 dry_run 显示差异，然后应用它。  
```

---

## 5. 预览和验证（编辑→检查循环）  

没有实时日志流工具，但您可以关闭反馈循环：  

- **实时查看：** `get_app_preview_url` 启动开发服务器并返回预览 URL。Vite HMR 随您编辑实时反映您的更改。  
- **构建状态：** `get_app_status` 返回 `ready` / `processing` / `error`。  
- **按需显示构建/类型/语法错误：** 使用 `run_command`：  
  ```bash
  npm run build       # 打包/编译错误  
  npx tsc --noEmit    # 类型错误  
  npm run lint        # 语法错误  
  ```  
- **读取开发服务器（Vite）日志**—— 管理的开发服务器写入 `/tmp/vite.log`。通过 `run_command` 尾部查看 HMR/编译错误：  
  ```bash
  tail -c 32000 /tmp/vite.log
  ```  
  （这是在应用树之外，因此只能通过 `run_command` 访问，因此需要 `sandbox:write`。）  

一个可靠的循环：`edit_file` → `npm run build`（或尾部 `/tmp/vite.log`）→ 修复任何错误 → `get_app_preview_url` 以肉眼检查。  

> **浏览器运行时错误**（编译但渲染时抛出错误的组件、失败的客户端 API 调用）出现在浏览器控制台，而不是 `/tmp/vite.log`。  
> 打开预览 URL 捕获这些错误。  

---

## 6. 您的更改如何持久化  

您不需要“保存”。每次修改调用都会安排一个**防抖自动提交**（约 5 秒）：更改被提交并推送到 Base44 的代码存储，因此它：  

- 在沙盒死亡时生存（沙盒是从最后一次提交重新创建的），  
- 出现在构建器的 Library/Data 选项卡中，  
- 保持后端函数部署的一致性，  
- 在您发布应用时包含其中。  

实际影响：  

- 存在一个小的丢失窗口（~5 秒）—— 不要在最后一个编辑后立即终止会话；给它一点时间提交。  
- **提交不是检查点。** 只有检查点出现在构建器的版本历史中。当用户点击**恢复**一个较早的版本或在构建器消息中点击**撤销此操作**时，  
  应用的代码回滚到该检查点的提交，并且所有在最后一个检查点之后写入的内容都会被丢弃，没有恢复点可以将其恢复。  
  在完成一个工作单元并停止之前调用 `create_checkpoint`（`sandbox checkpoint`），  
  这样用户的下一个恢复会落在您的工作上而不是将其擦除。  
- 对实体、代理、工作流、后端函数和页面路由的编辑会自动提交到 Base44。  
  普通的页面/组件/CSS 编辑存储在 git 中，无需额外操作。  

---

## 7. 并发：您与 Base44 构建器  

您和内置的 Base44 构建器不能同时修改同一应用：  

- **当您正在使用沙盒工具时**，Base44 构建器聊天被阻塞（“外部代理当前正在处理此应用”）。  
  您的会话是隐式的——最近的工具调用就是会话；它会在短空闲期（~10 分钟）后结束。  
- **如果 Base44 构建器正在构建中**，您的修改工具返回 `BUILDER_BUSY`。轮询 `get_app_status` 并在 `ready` 后重试。  
  读取工具在构建期间仍然可以工作。  

---

## 8. 安全限制和限制  

- **路径仅限于应用内。** 文件工具仅在应用目录内操作；拒绝遍历/绝对路径（`PATH_OUTSIDE_SANDBOX`）。  
- **`.agents/` 对文件工具不可用**（`PROTECTED_PATH`）—— 它包含代理管理的配置和密钥（`.agents/.env`）。  
  不要尝试通过文件工具读取或编辑它。  
- **速率限制** 按应用应用：读取 ~120/分钟，修改 ~60/分钟，命令 ~30/分钟。如果您遇到 `RATE_LIMITED`，请放慢速度。  
- **`delete_file` 不是专用工具** — 通过 `run_command rm` 删除。  

### 您可能遇到的错误代码  

`NOT_AUTHORIZED`（缺少范围/标志） · `APP_NOT_FOUND`（错误的 id 或无访问权限）  
· `PATH_OUTSIDE_SANDBOX` · `PROTECTED_PATH` · `NOT_FOUND` · `BINARY_FILE` ·  
`EDIT_TEXT_NOT_FOUND` · `EDIT_TEXT_NOT_UNIQUE`（使 `old_text` 唯一或使用 `replace_all`）  
· `OVERWRITE_NOT_ALLOWED`（传递 `overwrite: true`） · `TIMEOUT` · `OUTPUT_TRUNCATED` ·  
`BUILDER_BUSY` · `COMMIT_FLUSH_PENDING`（待处理的自动提交尚未持久化；稍后重试——  
例如在 `create_checkpoint`） · `RATE_LIMITED` · `BACKEND_ERROR`。  

消息编写得使代理可以自我纠正——阅读它们并调整。  

---

## 9. 小技巧和窍门  

- **在写入之前先读取。** 快速 `list_directory` + `read_file`（或 `grep`）遍历成本不高，但能显著提高编辑准确性。  
- **在 `edit_file` 上使用 `dry_run`** 以在提交更改之前确认差异，特别是对于多编辑调用。  
- **优先使用 `edit_file` 覆盖 `write_file`** 对于现有文件——外科手术式编辑避免覆盖并产生可审查的差异。  
- **使用 `read_file` 的 `offset`/`limit` 读取行范围** 在大文件上，而不是将整个内容拉入上下文中。  
- **当某事“看起来出错了”时，先尾部 `/tmp/vite.log`** 在猜测之前——它通常会指出确切的文件和行。  
- **让它提交。** 在最后一个编辑后暂停几秒钟，以便自动提交在您断开连接或发布之前落地。  
- **检查点您的工作——每次。** 在完成一个工作单元并停止之前调用 `create_checkpoint`（`sandbox checkpoint`），  
  在进行有风险的编辑块之前再调用一次。它首先刷新待处理的更改。没有它，您的编辑已提交但无法在版本历史中看到，  
  并且构建器中的下一个恢复或撤销会丢弃它们（第 6 节）。  
- **一次一个代理。** 该功能设计为每个应用一个外部代理；不要针对同一应用运行并行会话。  

---

## 10. 通过 `base44 sandbox` CLI 的本地代理  

如果您的代理在您的机器上运行，它可以通过 Base44 CLI 而不是 MCP 驱动相同的沙盒，  
并通过 Base44 CLI 而不是 OAuth 进行身份验证。相同的工具、相同的行为、相同的错误代码（第 8 节）——  
只有界面和身份验证不同。  

**身份验证。** 使用 Base44 CLI 登录（`base44 login`）——  
与 `base44 functions deploy` 使用的相同凭证。与 `base44 connectors` 命令一样，  
沙盒子命令从 `--app-id`、`BASE44_APP_ID`、本地 `.app.jsonc` 中解析应用 id；  
不需要 `config.jsonc`。  

**命令名称。** CLI 将每个沙盒工具暴露在较短的名称下：  

| MCP 工具 | CLI 命令 |  
|---|---|  
| `list_directory` | `base44 sandbox ls` |  
| `read_file` | `base44 sandbox read` |  
| `write_file` | `base44 sandbox write` |  
| `edit_file` | `base44 sandbox edit` |  
| `run_command` | `base44 sandbox run` |  
| `grep` | `base44 sandbox grep` |  
| `create_checkpoint` | `base44 sandbox checkpoint` |  

```bash
npx base44 sandbox read --app-id <APP_ID> src/App.jsx
```

`base44 sandbox checkpoint` 接受可选的 `--name`（消息/标题）并保存一个恢复点。  
在完成一个工作单元并停止之前调用它——CLI 写入被提交但未检查点，  
并且构建器中的恢复或撤销会丢弃最后一个检查点之后的所有内容（第 6 节）：  

```bash
npx base44 sandbox checkpoint --app-id <APP_ID> --name "before refactor"
```

**向代理提供特定应用的完整参考**（说明、公开、无需身份验证即可获取）：  

```
https://app.base44.com/api/sandbox/<APP_ID>/local-agent/readme.md
```

（云/MCP 对应的是 `.../api/sandbox/<APP_ID>/claude-web/readme.md`。）  

此技能中的其他内容——编辑→预览→验证循环（第 5 节）、持久化（第 6 节）、并发（第 7 节）和限制（第 8 节）——  
完全相同适用；只有界面和身份验证不同。  

---

## 11. 连接器（OAuth 集成）  

除了沙盒文件/命令行工具外，Base44 MCP 服务器还暴露了两个工具来管理第三方 OAuth 连接器（Google Calendar、Gmail、Slack、…）。  
它们不接触沙盒文件系统——它们直接操作应用的连接器状态。两者都需要 `appId`。  

| 工具 | 权限范围 | 目的 |  
|---|---|---|  
| `list_connectors` | `apps:read` | 列出应用的连接器。如果没有 `integrationTypes`，则返回完整目录（名称、描述、连接？——如果连接——状态和授予的范围）。传递 `integrationTypes` 获取特定连接器的详细信息。 |  
| `initiate_connector_connection` | `apps:write` | 连接（或重新范围）连接器。输入：`appId`，`integrationType`，`scopes`，可选的 `connectionConfig`。 |  

需要正确理解两种语义：  

- **声明性范围（替换，而不是合并）。** `initiate_connector_connection` 将连接器设置为**完全**您传递的 `scopes`。  
  省略的范围将被移除，并提示用户重新同意。**始终先调用 `list_connectors`**，  
  然后传递完整的期望集（您想要保留的现有范围**加上**任何新范围）。  
- **OAuth 需要人类。** 工具返回 `already_authorized: true`（无事可做）或一个 `redirect_url`，**用户**必须  
  在浏览器中打开以登录并同意——您无法自行完成。  
  完成后，再次调用 `list_connectors` 以验证并读取**授予**的范围（提供者可能授予的范围少于请求的）。  

这些只需要 `apps:read` / `apps:write` —— **不是** `sandbox:write`。  
在 CLI 界面（第 10 节）中，等效的是无项目的 `base44 connectors` 命令  
（`list-available`，`initiate --integration-type <t> --scopes <s...> --app-id <id>`，`pull`），  
它们打印相同的授权 URL。
