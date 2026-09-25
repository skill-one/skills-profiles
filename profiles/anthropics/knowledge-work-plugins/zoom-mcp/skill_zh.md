# Zoom MCP

此 Claude 插件中捆绑的 Zoom MCP 连接器的使用指南。建议优先使用 `design-mcp-workflow` 或 [setup-zoom-mcp](../setup-zoom-mcp/SKILL.md)，然后在此处路由以获取工具界面细节、认证预期和 MCP 特定约束。

# Zoom MCP 服务器

此插件捆绑了 Zoom 的托管 MCP 服务器，位于 `mcp-us.zoom.us`，供 AI 代理访问：

- 语义会议搜索
- 会议相关资产检索
- 录音资源检索

Zoom 文档通过单独捆绑的服务器提供：

- `zoom-docs-mcp` 位于 `mcp.zoom.us`
- 专为 Zoom 文档的创建和检索而构建

主 Zoom MCP 服务器当前的工具名称：

- `get_meeting_assets`
- `search_meetings`
- `get_recording_resource`
- `recordings_list`

某些 MCP 客户端在 UI 中对服务器工具进行命名空间化，例如 `zoom-mcp:recordings_list`。
将上述原始工具名称视为权威。

Zoom 文档特定的 MCP 工作应使用专用的 `zoom-docs-mcp` 服务器。

白板特定的 MCP 工作由专用的技能 [whiteboard/SKILL.md](whiteboard/SKILL.md) 覆盖。

## 快速入门

**1. 导出捆绑连接器预期的令牌：**

```bash
export ZOOM_MCP_ACCESS_TOKEN="your_zoom_user_oauth_access_token"
```

**2. 启用或重新启动插件，以便 Claude 重新启动捆绑的 MCP 服务器定义。**

**3. 验证发现：**
- 确认客户端可以看到 `recordings_list`、`search_meetings`、`get_meeting_assets` 和 `get_recording_resource`。
- 如果客户端暴露了原始协议检查，`tools/list` 是权威的发现来源。
- 当前目录在 [references/tools.md](references/tools.md) 中记录。

**4. 运行第一个有用的调用：**
```text
recordings_list
  userId: "me"
  from: "2026-03-01"
  to: "2026-03-06"
  page_size: 10
```

## 重要提示

**1. 用户 OAuth 是文档中记录的执行路径**

使用 **通用应用** 和 **用户级 OAuth** 作为此插件中 Zoom MCP 工具使用的执行路径。在此处不要依赖服务器到服务器的 OAuth 作为受支持的 MCP 认证模型。

**2. Zoom MCP 使用 MCP 特定的粒度范围**

Zoom MCP 范围集与旧版的广泛 REST 范围不同。
主 Zoom MCP 服务器的关键范围包括：
- `ai_companion:read:search` — 在 Zoom 会议、Zoom 聊天和 Zoom 文档中搜索，根据查询返回最相关的结果
- `meeting:read:search` — 搜索和查看会议
- `meeting:read:assets` — 查看会议的资产
- `cloud_recording:read:list_user_recordings` — 列出用户的所有云录音。
- `cloud_recording:read:content` — 读取录音内容范围
- `docs:write:import` — 通过导入创建新文件
- `docs:read:export` — 以 Markdown 格式读取文件内容

对于 Zoom 文档 MCP 特定而言，官方文档页面显示了以下粒度范围，用于记录的工具：
- `docs:write:import` — 通过导入创建新文件
- `docs:read:export` — 以 Markdown 格式读取文件内容

**3. AI Companion 功能是功能先决条件，不是范围替代品**

语义会议搜索、会议资产和录音内容检索依赖于账户功能（如 **智能录音** 和 **会议摘要**）以获得有用结果。这些功能设置不会替代所需的 OAuth 范围。

**4. 白板是单独的 MCP 界面**

Zoom MCP 端点和白板 MCP 端点是分开的。将白板特定请求路由到 [whiteboard/SKILL.md](whiteboard/SKILL.md)。

**5. 使用 REST 进行确定性会议 CRUD**

当前的 Zoom MCP 工具界面没有暴露确定性会议创建、更新或删除工具。如果用户需要显式的会议 CRUD 操作，请路由到 [../rest-api/SKILL.md](../rest-api/SKILL.md)。

## 服务器端点

| 传输方式 | URL |
|-----------|-----|
| 可流式传输的 HTTP（推荐） | `https://mcp-us.zoom.us/mcp/zoom/streamable` |
| SSE（备用） | `https://mcp-us.zoom.us/mcp/zoom/sse` |

专用文档 MCP 服务器：

| 传输方式 | URL |
|-----------|-----|
| 可流式传输的 HTTP（推荐） | `https://mcp.zoom.us/mcp/docs/streamable` |
| SSE（备用） | `https://mcp.zoom.us/mcp/docs/sse` |

专用白板 MCP 技能：
- [whiteboard/SKILL.md](whiteboard/SKILL.md)

## 搜索和检索模型

`search_meetings` 使用 AI Companion 检索而不是纯元数据过滤。在此处使用实时 MCP 服务器作为响应模式和范围行为的权威来源。

最重要的两个结果系列：

- **总结导向的结果**：AI 摘要、会议相关文档、录音和相关资产
- **录音导向的结果**：云录音引用和能够生成文本的资源

使用 [examples/transcript-retrieval.md](examples/transcript-retrieval.md) 获取主要检索工作流。

## 工具目录

| 工具 | 关键参数 | 需要的范围 |
|------|---------------|----------------|
| `get_meeting_assets` | `meetingId`* | `meeting:read:assets` |
| `search_meetings` | `q`, `from`, `to`, `page_size`, `next_page_token` | `meeting:read:search` |
| `get_recording_resource` | `meetingId`*, `types`, `clip_num`, `play_time`, `raw_passcode`, `encode_passcode` | `cloud_recording:read:content` |
| `recordings_list` | `userId`*, `from`, `to`, `meeting_id`, `trash`, `trash_type`, `page_size`, `next_page_token` | `cloud_recording:read:list_user_recordings` |

\* 必要参数

完整参数和输出指南：[references/tools.md](references/tools.md)

## 关键工作流

**搜索会议内容，然后检索资产：**
```text
search_meetings
  q: "Q4 planning discussion"
  from: "2026-03-01"
  to: "2026-03-06"
→ 选择返回的会议
→ get_meeting_assets  meetingId: "MEETING_ID_OR_UUID"
```

**列出录音，然后检索录音资源：**
```text
recordings_list
  userId: "me"
  from: "2026-03-01"
  to: "2026-03-06"
→ 选择录音目标
→ get_recording_resource  meetingId: "MEETING_UUID_OR_RECORDING_ID"
```

**创建或获取 Zoom 文档：**
- 使用专用的 `zoom-docs-mcp` 服务器，而不是主 `zoom-mcp` 服务器
- Zoom 文档 MCP 页面上的官方记录工具是：
  - `create_file_with_content`
  - `get_file_content`

## 错误参考

| 代码 | 含义 | 解决方法 |
|------|---------|-----|
| `401 Unauthorized` | 在端点处缺少或被拒绝的 bearer 令牌 | 设置 `ZOOM_MCP_ACCESS_TOKEN`，然后重新启动 Claude 或重新启用插件 |
| `-32001 Invalid access token` | 令牌过期、格式错误或缺少所需范围 | 刷新 OAuth 令牌并验证 MCP 特定范围 |
| `-32602 Can not found tool` | 请求的工具名称未被活动的 MCP 服务器暴露 | 重新运行 `tools/list` 并使用该端点的当前工具名称 |
| `404` | 可能是下游资源未找到的响应 | 使用 `search_meetings` 或 `recordings_list` 重新发现目标 |

完整错误参考：[references/error-codes.md](references/error-codes.md)

## 文档

### 概念
- [concepts/mcp-architecture.md](concepts/mcp-architecture.md) — MCP 协议、托管端点、发现和功能模型
- [concepts/oauth-setup.md](concepts/oauth-setup.md) — OAuth 应用创建、MCP 特定范围、AI Companion 先决条件、令牌生命周期

### 示例
- [examples/transcript-retrieval.md](examples/transcript-retrieval.md) — 搜索/资产和录音资源工作流
- [examples/create-zoom-doc.md](examples/create-zoom-doc.md) — 经验证的 Zoom 文档创建流程
- [examples/search-and-act.md](examples/search-and-act.md) — 搜索、检查资产，并在需要时将 CRUD 工作委托给 REST
- [examples/meeting-lifecycle.md](examples/meeting-lifecycle.md) — 为什么会议 CRUD 属于 REST，以及 MCP 到 REST 的委托模式

### 参考
- [references/tools.md](references/tools.md) — 当前 Zoom MCP 工具参考
- [references/error-codes.md](references/error-codes.md) — MCP 和 Zoom API 错误及其解决方法
- [whiteboard/SKILL.md](whiteboard/SKILL.md) — 专用的白板 MCP 技能

### 故障排除
- [troubleshooting/common-errors.md](troubleshooting/common-errors.md) — 范围失败、端点混淆、搜索/录音问题

### 操作
- [RUNBOOK.md](RUNBOOK.md) — 5 分钟预检和调试清单

## 相关技能

- [zoom-rest-api](../rest-api/SKILL.md) — 确定性 REST API 访问，包括会议 CRUD
- [zoom-oauth](../oauth/SKILL.md) — OAuth 实现模式
- [zoom-webhooks](../webhooks/SKILL.md) — 事件驱动的录音和会议工作流
- [zoom-rtms](../rtms/SKILL.md) — 活动会议期间的实时媒体和文本流
