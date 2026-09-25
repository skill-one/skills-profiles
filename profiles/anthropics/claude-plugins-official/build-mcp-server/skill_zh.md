# 构建MCP服务器

你正在指导一位开发者设计和构建一个与Claude无缝协作的MCP服务器。MCP服务器有多种形式——早期选择错误形状会导致后期痛苦的改写。你的首要任务是**发现，而非编码**。

**首先加载Claude特定的上下文。** MCP规范是通用的；Claude具有额外的认证类型、审查标准和限制。在回答问题或搭建框架之前，获取`https://claude.com/docs/llms-full.txt`（Claude连接器文档的完整导出）以确保你的指导反映Claude的实际约束。

在获得Phase 1中问题的答案之前，不要开始搭建框架。如果用户的开启消息已经回答了这些问题，请直接承认并跳转到推荐部分。

---

## Phase 1 — 调查用例

以对话方式提问（将它们批量到一个消息中，不要逐一提问）。根据用户已经告诉你的内容调整措辞。

### 1. 它连接到什么？

| 如果它连接到… | 可能的方向 |
|---|---|
| 云API（SaaS、REST、GraphQL） | 远程HTTP服务器 |
| 本地进程、文件系统或桌面应用程序 | MCPB或本地stdio |
| 硬件、操作系统级API或用户特定状态 | MCPB |
| 无外部连接——纯逻辑/计算 | 任何——默认为远程 |

### 2. 谁会使用它？

- **只有我/我的团队，在我们的机器上** → 本地stdio可以接受（原型最简单）
- **任何安装它的人** → 远程HTTP（强烈推荐）或MCPB（如果必须为本地）
- **Claude桌面用户，需要UI小部件** → MCP应用程序（远程或MCPB）

### 3. 它暴露了多少个不同的操作？

这决定了工具设计模式——见Phase 3。

- **少于15个操作** → 每个操作一个工具
- **几十到几百个操作**（例如封装大型API表面）→ 搜索+执行模式

### 4. 工具是否需要在通话期间需要用户输入或丰富的显示？

- **简单的结构化输入**（从列表中选择、输入值、确认）→ **Elicitation**——规范原生，无需UI代码。*主机支持正在逐步推出*（Claude Code ≥2.1.76）——始终与能力检查和回退配对。见`references/elicitation.md`。
- **丰富的/可视化UI**（图表、带搜索的自定义选择器、实时仪表板）→ **MCP应用程序小部件**——基于iframe，需要`@modelcontextprotocol/ext-apps`。见`build-mcp-app`技能。
- **两者都不是** → 返回文本/JSON的普通工具。

### 5. 上游服务使用什么认证？

- 无/API密钥 → 直接明了
- OAuth 2.0 → 你将需要一个带有CIMD（推荐）或DCR支持的远程服务器；见`references/auth.md`

---

## Phase 2 — 推荐部署模型

根据答案，推荐**一个**路径。要明确表达意见。排名选项：

### ⭐ 远程流式传输HTTP MCP服务器（默认推荐）

一个托管服务，通过流式传输HTTP进行MCP通信。这是**推荐路径**，用于封装云API的任何内容。

**为什么它胜出：**
- 无安装摩擦——用户添加一个URL，搞定
- 一个部署服务所有用户；你可以控制升级
- OAuth流程工作正常（服务器可以处理重定向、DCR、令牌存储）
- 兼容Claude桌面、Claude Code、Claude.ai和第三方MCP主机

**除非**服务器*必须*接触用户的本地机器。

→ **最快部署：** Cloudflare Workers — `references/deploy-cloudflare-workers.md`（两行命令即可上线）
→ **便携式Node/Python：** `references/remote-http-scaffold.md`（Express或FastMCP，可在任何主机上运行）

### Elicitation（结构化输入，无需UI构建）

如果工具只需要用户确认、选择选项或填写简短表单，**Elicitation**可以做到无需UI代码。服务器发送一个扁平的JSON模式；主机渲染原生表单。规范原生，无需额外包。

**注意事项：** 主机支持是新的（Claude Code在v2.1.76中提供了它；桌面未确认）。如果客户端未宣传该功能，SDK会抛出错误。始终检查`clientCapabilities.elicitation`并准备回退——见`references/elicitation.md`中的规范模式。这是正确的规范正确方法；主机覆盖将逐渐跟上。

升级到`build-mcp-app`小部件，当你需要：嵌套/复杂数据、可滚动/可搜索的列表、可视化预览、实时更新。

### MCP应用程序（远程HTTP + 交互式UI）

与上述相同，加上**UI资源**——在聊天中渲染的交互式小部件。带搜索的丰富选择器、图表、实时仪表板、可视化预览。一次构建，在Claude和ChatGPT中渲染。

**当**Elicitation的扁平表单限制不适用时选择——你需要自定义布局、大型可搜索列表、视觉内容或实时更新。

通常远程，但如果UI需要驱动本地应用程序，可以作为MCPB分发。

→ 转交**`build-mcp-app`**技能。

### MCPB（捆绑本地服务器）

一个本地MCP服务器**捆绑其运行时**，因此用户无需安装Node/Python。分发本地服务器的认可方式。

**当**服务器*必须*在用户的机器上运行——它读取本地文件、驱动桌面应用程序、与localhost服务通信或需要操作系统级访问时选择。

→ 转交**`build-mcpb`**技能。

### 本地stdio（npx / uvx）——*不推荐用于分发*

通过`npx` / `uvx`在用户的机器上启动的脚本。适合**个人工具和原型**。分发痛苦：用户需要正确的运行时，你无法推送更新，并且唯一的分发渠道是Claude Code插件。

仅作为过渡推荐。如果用户坚持，请搭建它，但注明MCPB升级路径。

---

## Phase 3 — 选择工具设计模式

每个MCP服务器都暴露工具。如何划分比大多数人预期的更重要——工具模式直接出现在Claude的上下文窗口中。

### 模式A：每个操作一个工具（小表面）

当操作空间较小时（< ~15个操作），为每个操作提供一个专门的工具，并具有紧密的描述和模式。

```
create_issue    — 创建新问题。参数：标题、正文、标签[]
update_issue    — 更新现有问题。参数：id、标题？、正文？、状态？
search_issues   — 通过查询字符串搜索问题。参数：查询、限制？
add_comment     — 向问题添加评论。参数：issue_id、正文
```

**为什么有效：** Claude一次性读取工具列表并确切知道可能是什么。无需发现往返。每个工具的模式的输入验证精确。

**特别适合**当一个或多个工具提供交互式小部件（MCP应用程序）时——每个小部件自然绑定到一个工具。

### 模式B：搜索+执行（大表面）

当封装大型API（几十到几百个端点）时，将每个操作作为工具列出会淹没上下文窗口并降低模型性能。相反，暴露**两个**工具：

```
search_actions  — 给定自然语言意图，返回匹配的操作及其ID、描述和参数模式。
execute_action  — 通过ID和params对象执行操作。
```

服务器在内部持有完整目录。Claude搜索、选择、执行。上下文保持简洁。

**混合：** 将最常用的3-5个操作提升为专用工具，将长尾保留在搜索/执行后面。

→ 见`references/tool-design.md`中的模式示例和描述编写指南。

---

## Phase 4 — 选择框架

推荐以下两者之一。其他框架存在，但这两个具有最佳的MCP规范覆盖和Claude兼容性。

| 框架 | 语言 | 使用场景 |
|---|---|---|
| **官方TypeScript SDK** (`@modelcontextprotocol/sdk`) | TS/JS | 默认选择。最佳规范覆盖，最先获得新功能。 |
| **FastMCP 3.x** (`fastmcp` on PyPI) | Python | 用户更喜欢Python，或封装Python库。基于装饰器，极低样板代码。这是jlowin的包——不是官方`mcp` SDK捆绑的冻结FastMCP 1.0。 |

如果用户已经有了一个语言/堆栈，跟随它——两者都生成相同的线协议。

---

## Phase 5 — 搭建并转交

一旦你确定了四个决策（部署模型、工具模式、框架、认证），做**一个**：

1. **远程HTTP，无UI** → 使用`references/remote-http-scaffold.md`（便携式）或`references/deploy-cloudflare-workers.md`（最快部署）进行内联搭建。这个技能可以完成工作。
2. **MCP应用程序（UI小部件）** → 总结迄今为止的决策，然后加载**`build-mcp-app`**技能。
3. **MCPB（捆绑本地）** → 总结迄今为止的决策，然后加载**`build-mcpb`**技能。
4. **本地stdio原型** → 内联搭建（最简单的情况），标记MCPB升级路径。

转交时，用一句话重述设计简报，以便下一个技能不会重新提问。

---

## 工具之外的其他基础

工具是服务器基础中的三种之一。大多数服务器从工具开始，并且永远不会需要其他基础，但了解它们的存在可以防止重新发明轮子：

| 基础 | 触发者 | 使用场景 |
|---|---|---|
| **资源** | 主机应用程序（不是Claude） | 作为可浏览上下文暴露文档/文件/数据 |
| **提示** | 用户（斜杠命令） | 熟悉的工作流程（"/summarize-thread"） |
| **Elicitation** | 服务器，工具期间 | 在不构建UI的情况下向用户输入 |
| **采样** | 服务器，工具期间 | 在工具逻辑中需要LLM推理 |

→ `references/resources-and-prompts.md`、`references/elicitation.md`、`references/server-capabilities.md`

---

## Phase 6 — 在Claude中测试并发布

一旦服务器运行：

1. **通过在设置→连接器中添加服务器URL作为自定义连接器来测试真实Claude**（为本地服务器使用Cloudflare隧道）。Claude在初始化时使用`clientInfo.name: "claude-ai"`标识自己。→ https://claude.com/docs/connectors/building/testing
2. **运行提交前检查清单**——读写工具分割、必需的注释、名称限制、提示注入规则。→ https://claude.com/docs/connectors/building/review-criteria
3. **提交到Anthropic目录。** → https://claude.com/docs/connectors/building/submission
4. **推荐分发一个包装此MCP的技能插件**——大多数合作伙伴都会分发两者。→ https://claude.com/docs/connectors/building/what-to-build

---

## 快速参考：决策矩阵

| 场景 | 部署 | 工具模式 |
|---|---|---|
| 封装小型SaaS API | 远程HTTP | 每个操作一个 |
| 封装大型SaaS API（50+端点） | 远程HTTP | 搜索+执行 |
| SaaS API具有丰富的表单/选择器 | MCP应用程序（远程） | 每个操作一个 |
| 驱动本地桌面应用程序 | MCPB | 取决于表面 |
| 本地桌面应用程序具有聊天UI | MCP应用程序（MCPB） | 每个操作一个 |
| 读写本地文件系统 | MCPB | 取决于表面 |
| 个人原型 | 本地stdio | 最快的 |

---

## 参考文件

- `references/remote-http-scaffold.md` — TS SDK和FastMCP中的最小远程服务器
- `references/deploy-cloudflare-workers.md` — 最快部署路径（Workers原生搭建）
- `references/tool-design.md` — 编写Claude理解良好的工具描述和模式
- `references/auth.md` — OAuth、CIMD、DCR、令牌存储模式
- `references/resources-and-prompts.md` — 两个非工具基础
- `references/elicitation.md` — 规范原生工具期间用户输入（能力检查+回退）
- `references/server-capabilities.md` — 指令、采样、根源、日志记录、进度、取消
- `references/versions.md` — 版本敏感的声明账本（更新时检查）
