# 打开 Logfire UI

使用此技能进行直接的 Logfire UI、浏览器、实时视图、链接和 Explore 页面请求。

## 用户可见进度

保持进度更新安静。不要描述选择此技能的原因、重申路由规则、引用本地指令、解释令牌范围或宣布常规辅助调用。如果需要更新，请使用一个专注于操作的简短句子，例如“使用错误过滤器打开 Logfire”。

打开 Logfire 后，除非浏览器卡住、要求登录或用户明确要求您验证页面，否则不要运行或描述额外的页面状态检查。

## 浏览器目标

在 Codex 桌面版中，尽可能使用浏览器插件的 Codex 应用内浏览器 (`iab`) 和当前选定的标签页。

浏览器访问是间接的：不要期望一个名为浏览器的 MCP 工具。如果浏览器插件列为可用，加载 `browser:browser` 技能并使用其 Node REPL `js` / `mcp__node_repl__js` 启动程序来绑定 `agent.browsers.get("iab")`。如果 `js` 不可见，则在声明应用内浏览器不可用时，使用工具发现 `node_repl js`。

不要使用 `agent-browser`、`chrome-devtools`、`mcp__chrome_devtools__*`、`mcp__playwright__*`、macOS `open`、`xdg-open`、独立的 Playwright/Chromium、从 shell 启动的浏览器、网页预览卡片或新创建的外部浏览器窗口，除非用户明确要求外部浏览器。当 Logfire 实时视图已经选定并且可以就地更新时，不要创建新的应用内标签页。

仅在浏览器插件未列出或其技能无法加载、Node REPL `js` 执行工具在工具发现后不可用，或在导航开始前浏览器技能启动失败后，才报告应用内浏览器不可用。然后返回干净的 Logfire URL 并解释应用内浏览器无法控制。将 `chrome-devtools`、Playwright MCP、独立 Playwright 和网页预览卡片视为“浏览器不可用”，而不是备用方案。不要静默地回退到任何外部或专用浏览器窗口。

## 核心规则

对于项目级或聚合 UI 请求，直接通过 URL 打开或返回 Logfire。

不要先查询遥测数据：
- 不要调用 `query_run`。
- 不要说你将先查询 Logfire 或获取跨度。

仅在用户要求打开特定未知项且必须先找到它时才查询，例如“打开最慢的跟踪”或“打开最新的错误跟踪”。

如果请求是模糊的，例如“显示最近的错误”或“查看日志”，请询问用户是否希望 UI 中打开 Logfire 或在聊天中进行查询分析。除非用户明确要求两者都要做，否则不要同时做两者。

## 项目发现

对于没有明确组织/项目的 UI 请求，首先尝试通过 Logfire MCP 认证/当前项目元数据解析规范项目 URL。如果可用的 MCP 服务器暴露了项目链接或当前项目辅助程序，请使用它们。这是项目发现，不是遥测数据查询。

如果 MCP 可以解析确切一个当前项目，请使用该项目 URL。如果它无法解析项目、解析多个候选者或返回认证/错误状态，请询问用户组织/项目或完整的 Logfire 项目 URL。

不要从 `LOGFIRE_BASE_URL`、`LOGFIRE_URL`、导出器配置、存储库名称或本地主机可达性中推断项目 URL。环境/配置值可以标识 Logfire 平台/API 基，但它们本身不能标识目标组织/项目。

## URL 工作流程

1. 如果已知完整项目 URL，请直接使用它。
2. 如果用户省略了项目，请按照上述方法通过 MCP 解析当前项目。
3. 如果用户提供了项目名称但未提供组织/基本 URL，请调用 `project_logfire_ui_link(project=project)` 并使用默认的干净链接行为来派生规范项目 URL。这是一个 URL 发现辅助程序，不是遥测数据查询。
4. 对于项目实时视图/过滤器 URL，在 Codex 浏览器中立即打开链接时，调用 `project_logfire_ui_link(project=project, query=query, since=since, until=until, handoff=True)`。返回持久性或可共享 URL 时使用默认的干净链接行为。如果用户提供了一个现有的干净 Logfire 项目 URL 并要求转交，请解析其项目、`q`、`since` 和 `until` 值并通过此工具传递。
5. 如果用户提供了或查询工作流已经找到一个真实的 `trace_id`，在 Codex 浏览器中立即打开链接时，调用 `project_logfire_link(trace_id=trace_id, project=project, handoff=True)`。返回持久性或可共享 URL 时使用默认的干净链接行为。
6. 通过 `project_logfire_ui_link` 在有用时添加 `query`、`since` 和 `until`。如果手动组装干净 URL，请对 `q`、`since` 和 `until` 进行 URL 编码。
7. 如果用户要求打开 URL 且浏览器可用，请在 Codex 应用内浏览器中打开它。否则，返回 URL 而不是启动外部浏览器。

## 已打开的实时视图控制

如果 Logfire 项目实时视图已经在 Codex 浏览器中打开，请使用 JSON 命令桥。这是唯一支持的应用内交互模型，因为它在不重新加载完整文档的情况下更新视图，并显示代理正在积极更改页面。

不要尝试从 Codex 浏览器使用页面全局 JavaScript API。唯一支持的代理控制面是 JSON 命令输入。

对于 Codex 浏览器 / `iab`，在 `Logfire 实时视图代理命令` 输入中填写一个 JSON 补丁，例如 `{"q":"level='error'","last":"1h","since":null,"until":null}` 并按 Enter。隐藏的提交按钮只是一个表单目标；不要因为按钮不可见而跳过此路径。

仅在桥接表单输入不存在或无法提交时使用直接 URL/搜索参数更新。当桥接表单可用时，不要直接更新 URL。

使用直接 URL 备用方案时，如果浏览器控制面允许页面脚本 URL 更新，请更新 `window.history` 并派发一个 `popstate` 事件。使用 `pushState` 进行有意义的用户可见导航，使用 `replaceState` 进行清理或重试。如果页面内 URL 更新不可用，则回退到打开干净 URL。

不要修改 `/api/auth/handoff?ticket=...` URL。转交 URL 是单次使用的入口点；重定向后，控制最终的干净项目 URL。

实时视图搜索参数：

- `q`：类似 SQL 的 Logfire 过滤表达式，例如 `level='error'`、`kind='span'` 或 `service_name='api'`。在构造 URL 字符串时对它进行 URL 编码。
- `last`：滚动实时窗口，例如 `5m`、`1h`、`14d` 或毫秒数。用于实时模式并移除 `since`/`until`。
- `since` 和 `until`：固定历史窗口作为 ISO 8601 时间戳。用于有界时间范围并移除 `last`。
- `env`：部署环境过滤。使用重复的 `env` 参数用于多个环境。所有环境都省略它。
- `traceId` 和 `spanId`：在已知时聚焦特定的跟踪/跨度。在更改主查询或时间范围时清除过时的聚焦参数，例如 `traceId`、`spanId`、`focusTraceId` 和 `focusTraceTimestamp`，除非用户要求保留聚焦的记录。

## 浏览器转交 URL

当 MCP 链接工具支持 `handoff: bool = False` 时，仅对将在浏览器中立即打开的 URL 使用 `handoff=True`。转交 URL 是短寿命、单次使用且绑定到平台生成的目标。

- 如果转交结果是字符串，立即打开该确切 URL。它可能是 `/api/auth/handoff?ticket=...` URL。不要向其添加查询参数、重写它、持久化它、在文档中引用它或将其视为可共享。
- 如果转交结果是具有 `handoff: false` 的对象，使用其 `url` 值作为干净的备用 URL。仅在它有助于用户理解为什么浏览器可能仍然要求登录时才提及 `reason`，例如 API 密钥认证或需要重新认证。
- 如果原因说明需要重新认证 Logfire MCP 连接，请解释 MCP OAuth 刷新令牌缺少用于生成 UI 会话的元数据。不要将其描述为浏览器会话刷新；用户需要重新连接/认证 Logfire MCP 认证流程。
- 如果可用的 MCP 服务器未暴露 `handoff`，请正常调用链接工具并使用干净 URL。
- 不要手动向转交 URL 添加过滤器或时间参数。将最终项目过滤目标放入 `project_logfire_ui_link` 并让平台为该目标生成票证。

## Codex 浏览器打开稳定性

在 Codex 浏览器中打开 Logfire 转交 URL 时，为同一目标保留持久的干净 URL 作为备用。如有需要，在报告浏览器打开失败之前，调用相同的链接工具并使用 `handoff=False`。

使用浏览器技能的应用内浏览器工作流程并绑定导航尝试。不要等待 `networkidle`、websocket 完成或完全安静的实时视图页面。如果导航后等待，请仅等待 URL 提交、最终的干净项目 URL 或可见的 Logfire 页面信号。

如果浏览器仍然停留在灰色的 `about:blank` 屏幕上或浏览器导航调用超时，请停止等待并返回干净 URL。将其描述为浏览器在导航前卡住，而不是 Logfire 认证失败。不要暴露已消耗或过期的转交 URL。

不要通过启动单独的浏览器窗口来恢复 Codex 浏览器卡顿。除非用户明确要求您尝试外部浏览器，否则返回干净 URL。

## 常见过滤器

- 跨度：`q=kind%3D%27span%27`
- 日志：`q=kind%3D%27log%27`
- 异常：`q=is_exception%3Dtrue`
- 错误：`q=level%3D%27error%27`
- 服务：URL 编码一个过滤器，例如 `service_name='api'`

## 示例

对于“在 starter-project 中打开 Codex 的 Logfire 实时视图以查看跨度，持续一小时”：

1. 直接打开已知的或派生的 `starter-project` Logfire URL。
2. 添加 `q=kind%3D%27span%27`。
3. 添加 `since=<一小时前>` 和 `until=<现在>`。
4. 在 Codex 浏览器中打开 URL。
5. 不要先运行 SQL。

对于“找到最慢的跟踪并打开它”，仅使用查询工作流来识别跟踪，然后使用 `project_logfire_link(trace_id=trace_id, project=project, handoff=True)` 并打开该链接。

对于“将打开的实时视图更改为错误的一小时”，通过 `Logfire 实时视图代理命令` 输入提交 `{"q":"level='error'","last":"1h","since":null,"until":null}`；不要生成新的转交 URL。

## 认证边界

不要尝试将 MCP 认证令牌传递到浏览器或 Logfire UI。永远不要将承载、API、读取或写入令牌放在 URL 查询参数、片段、粘贴的浏览器指令、日志或笔记中。MCP/工具认证和浏览器 Web 会话是分离的安全上下文。

对于立即打开的 UI 链接，优先使用上述平台转交。如果转交不可用，则回退到干净 URL 并在有用时解释具体的回退原因。缺少浏览器 cookie 可能需要正常浏览器登录；过时的 MCP OAuth 连接需要 MCP 重新认证。
