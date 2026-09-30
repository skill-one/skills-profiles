---
name: zoom-general
description: 交叉产品缩放参考技能。在流程清晰且需要共享平台指导、应用模型比较、认证上下文、作用域、市场考虑或API与MCP路由时使用。
---

# Zoom 常规（跨产品技能）

跨产品 Zoom 问题的背景参考。建议先掌握工作流技能，然后使用此文件进行共享平台指导和路由细节。

## `zoom-general` 如何路由复杂的开发者查询

将 `zoom-general` 作为分类器和链式层使用：

1.  在查询中检测产品信号
2.  选择一个主要技能
3.  为认证、事件或部署边缘附加次要技能
4.  仅当两个路由具有相似置信度时，才询问一个简短的澄清

最小实现：

```ts
type SkillId =
  | 'zoom-general'
  | 'zoom-rest-api'
  | 'zoom-webhooks'
  | 'zoom-oauth'
  | 'zoom-meeting-sdk-web-component-view'
  | 'zoom-video-sdk'
  | 'zoom-mcp';

const hasAny = (q: string, words: string[]) => words.some((w) => q.includes(w));

function detectSignals(rawQuery: string) {
  const q = rawQuery.toLowerCase();
  return {
    meetingCustomUi: hasAny(q, ['zoom meeting', 'custom ui', 'component view', 'embed meeting']),
    customVideo: hasAny(q, ['video sdk', 'custom video session', 'peer-video-state-change']),
    restApi: hasAny(q, ['rest api', '/v2/', 'create meeting', 'list users', 's2s oauth']),
    webhooks: hasAny(q, ['webhook', 'x-zm-signature', 'event subscription', 'crc']),
    oauth: hasAny(q, ['oauth', 'pkce', 'token refresh', 'account_credentials']),
    mcp: hasAny(q, ['zoom mcp', 'agentic retrieval', 'tools/list', 'semantic meeting search']),
  };
}

function pickPrimarySkill(s: ReturnType<typeof detectSignals>): SkillId {
  if (s.meetingCustomUi) return 'zoom-meeting-sdk-web-component-view';
  if (s.mcp) return 'zoom-mcp';
  if (s.restApi) return 'zoom-rest-api';
  if (s.customVideo) return 'zoom-video-sdk';
  return 'zoom-general';
}

function buildChain(primary: SkillId, s: ReturnType<typeof detectSignals>): SkillId[] {
  const chain = [primary];
  if (s.oauth && !chain.includes('zoom-oauth')) chain.push('zoom-oauth');
  if (s.webhooks && !chain.includes('zoom-webhooks')) chain.push('zoom-webhooks');
  return chain;
}
```

示例：

- `创建会议、配置 webhooks 并处理 OAuth token 刷新` ->
  `zoom-rest-api -> zoom-oauth -> zoom-webhooks`
- `为 Web 上的 Zoom 会议构建自定义视频 UI` ->
  `zoom-meeting-sdk-web-component-view`

有关完整的 TypeScript 实现和交接合同，请使用
[references/routing-implementation.md](references/routing-implementation.md)。

## 选择您的路径

| 我想要... | 使用此技能 |
|--------------|----------------|
| 在真实的 Zoom 会议周围构建自定义 Web UI | **[zoom-meeting-sdk-web-component-view](../meeting-sdk/web/component-view/SKILL.md)** |
| 构建确定性自动化/配置/报告，具有显式请求控制 | **[zoom-rest-api](../rest-api/SKILL.md)** |
| 接收事件通知（HTTP 推送） | **[zoom-webhooks](../webhooks/SKILL.md)** |
| 接收事件通知（WebSocket，低延迟） | **[zoom-websockets](../websockets/SKILL.md)** |
| 将 Zoom 会议嵌入我的应用程序 | **[zoom-meeting-sdk](../meeting-sdk/SKILL.md)** |
| 构建自定义视频体验（Web、React Native、Flutter、Android、iOS、macOS、Unity、Linux） | **[zoom-video-sdk](../video-sdk/SKILL.md)** |
| 构建在 Zoom 客户端内运行的应用程序 | **[zoom-apps-sdk](../zoom-apps-sdk/SKILL.md)** |
| 使用 AI 服务 Scribe 转录上传或存储的媒体 | **[scribe](../scribe/SKILL.md)** |
| 访问会议的实时音频/视频/字幕 | **[zoom-rtms](../rtms/SKILL.md)** |
| 为支持启用协作浏览 | **[zoom-cobrowse-sdk](../cobrowse-sdk/SKILL.md)** |
| 构建联系中心应用程序和渠道集成 | **[contact-center](../contact-center/SKILL.md)** |
| 构建虚拟代理 Web/移动聊天机器人体验 | **[virtual-agent](../virtual-agent/SKILL.md)** |
| 构建 Zoom Phone 集成（智能嵌入、Phone API、webhooks、URI 流） | **[phone](../phone/SKILL.md)** |
| 构建团队聊天应用程序和集成 | **[zoom-team-chat](../team-chat/SKILL.md)** |
| 使用 Rivet（认证 + webhooks + API）构建服务器端集成 | **[rivet-sdk](../rivet-sdk/SKILL.md)** |
| 加入前进行浏览器/设备/网络预检 | **[probe-sdk](../probe-sdk/SKILL.md)** |
| 为视频 SDK 添加预构建的 UI 组件 | **[zoom-ui-toolkit](../ui-toolkit/SKILL.md)** |
| 实现 OAuth 认证（所有授权类型） | **[zoom-oauth](../oauth/SKILL.md)** |
| 构建基于 AI 的工具工作流（AI Companion/代理）以使用 Zoom 数据 | **[zoom-mcp](../zoom-mcp/SKILL.md)** |
| 构建基于 AI 的白板工作流以使用 Zoom Whiteboard MCP | **[zoom-mcp/whiteboard](../zoom-mcp/whiteboard/SKILL.md)** |
| 构建具有稳定 API 核心 + AI 工具层的_enterprise AI 系统 | **[zoom-rest-api](../rest-api/SKILL.md)** + **[zoom-mcp](../zoom-mcp/SKILL.md)** |

## 规划检查点：Rivet SDK（可选）

当用户开始规划结合认证 + webhooks + API 调用的服务器端集成时，首先询问：

- `Rivet SDK 是一个 Node.js 框架，捆绑了 Zoom 认证处理、webhooks 接收器和类型化的 API 包装器。`
- `您想使用 Rivet SDK 进行更快的脚手架，还是更喜欢没有 Rivet 的直接 OAuth + REST 实现？`

回答后的路由：

- 如果用户选择 Rivet：链式 `rivet-sdk` + `oauth` + `rest-api`。
- 如果用户拒绝 Rivet：链式 `oauth` + `rest-api` (+ `webhooks` 或产品技能按需)。

### SDK 与 REST 路由矩阵（硬停止）

| 用户意图 | 正确路径 | 不要路由到 |
|-------------|--------------|-----------------|
| 将 Zoom 会议嵌入应用程序 UI | `zoom-meeting-sdk` | 仅 REST 的 `join_url` 流 |
| 为真实的 Zoom 会议构建自定义 Web UI | `zoom-meeting-sdk-web-component-view` | `zoom-video-sdk` |
| 构建自定义视频 UI/会话应用程序 | `zoom-video-sdk` | 会议 SDK 或 REST 会议链接 |
| 获取浏览器加入链接/管理会议资源 | `zoom-rest-api` | 会议 SDK 加入实现 |

路由护栏：
- 如果用户请求 SDK 嵌入/加入行为，请保持在 SDK 路径中。
- 如果提示说 **会议** 加上 **自定义 UI/视频/布局/嵌入**，请优先选择 `zoom-meeting-sdk-web-component-view`。
- 仅在用户明确请求混合架构时，才使用 REST 路径。
- 对于可执行分类/链式逻辑和错误处理，请参阅 [references/routing-implementation.md](references/routing-implementation.md)。

### API 与 MCP 路由矩阵（硬停止）

| 用户意图 | 正确路径 | 原因 |
|-------------|--------------|-----|
| 确定性后端自动化、账户/用户配置、报告、计划作业 | `zoom-rest-api` | 显式请求/响应控制和可重复行为 |
| AI 代理动态选择工具、跨平台 AI 工具互操作性 | `zoom-mcp` | MCP 专为动态工具发现和代理工作流优化 |
| 企业 AI 架构（稳定核心 + 自适应 AI 层） | `zoom-rest-api + zoom-mcp` | APIs 运行核心系统操作；MCP 暴露精选 AI 工具/上下文 |

路由护栏：
- 不要用仅 MCP 路由替换确定性后端 API。
- 不要在任务为 AI 代理工具编排时强制原始 REST 首先路由。
- 当用户需要稳定自动化和 AI 驱动交互时，请优先选择混合路由。
- MCP 远程服务器通过 Streamable HTTP/SSE 工作；当目标客户端/代理支持 MCP 传输时（例如 Claude 或 VS Code），使用此路径。
- 不要设计按租户自定义的 MCP 端点配置；Zoom MCP 端点在实例/集群级别共享。
- 来源：https://developers.zoom.us/docs/mcp/library/resources/apis-vs-mcp/

### 模糊性解决（路由前询问）

当提示与 API 和 MCP 路径具有相似置信度时，在执行前询问一个简短的澄清：

- `您想要确定性 REST API 自动化、AI 代理 MCP 工具，还是两者混合？`

然后路由为：
- REST 回答 → `zoom-rest-api`
- MCP 回答 → `zoom-mcp`
- 混合回答 → `zoom-rest-api + zoom-mcp`

### MCP 可用性和拓扑说明

- Zoom 托管的 MCP 访问正在发展；文档表明一个模型，Zoom 暴露产品范围的 MCP 服务器（例如会议、团队聊天、白板）。
- 将 `zoom-mcp` 作为 MCP 顶级入口点。
- 将白板特定 MCP 请求路由到 **[zoom-mcp/whiteboard](../zoom-mcp/whiteboard/SKILL.md)**。
- 当请求是产品特定且存在 MCP 覆盖时，首先路由到该 MCP 产品表面；否则使用 REST/SDK 技能进行确定性实现。

### Webhooks 与 WebSockets

两者都接收事件通知，但方法不同：

| 方面 | webhooks | zoom-websockets |
|--------|---------------|-----------------|
| 连接 | HTTP POST 到您的端点 | 持久 WebSocket |
| 延迟 | 较高 | 较低 |
| 安全性 | 需要公共端点 | 无暴露端点 |
| 设置 | 更简单 | 更复杂 |
| 最佳用途 | 大多数用例 | 实时、安全敏感 |

## 常见用例

| 用例 | 描述 | 所需技能 |
|----------|-------------|---------------|
| [会议 + Webhooks + OAuth 刷新](references/meeting-webhooks-oauth-refresh-orchestration.md) | 创建会议、处理实时更新、安全刷新 OAuth token 在一个设计中 | [zoom-rest-api](../rest-api/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) + [zoom-webhooks](../webhooks/SKILL.md) |
| [Scribe 转录管道](use-cases/scribe-transcription-pipeline.md) | 使用 AI 服务 Scribe 转录上传的文件或 S3 存档，使用快速模式或批量作业 | [scribe](../scribe/SKILL.md) + 可选 [zoom-rest-api](../rest-api/SKILL.md) + 可选 [zoom-webhooks](../webhooks/SKILL.md) |
| [APIs 与 MCP 路由](use-cases/apis-vs-mcp-routing.md) | 决定是否路由到确定性 Zoom APIs、AI 驱动的 MCP 或混合设计 | [zoom-rest-api](../rest-api/SKILL.md) 和/或 [zoom-mcp](../zoom-mcp/SKILL.md) |
| [自定义会议 UI (Web)](use-cases/custom-meeting-ui-web.md) | 使用 Meeting SDK Component View 在 Web 应用程序中为真实 Zoom 会议构建自定义视频 UI | [zoom-meeting-sdk-web-component-view](../meeting-sdk/web/component-view/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) |
| [会议自动化](use-cases/meeting-automation.md) | 程序性安排、更新、删除会议 | [zoom-rest-api](../rest-api/SKILL.md) |
| [会议机器人](use-cases/meeting-bots.md) | 构建加入会议以进行 AI/转录/录音的机器人 | [meeting-sdk/linux](../meeting-sdk/linux/SKILL.md) + [zoom-rest-api](../rest-api/SKILL.md) + 可选 [zoom-webhooks](../webhooks/SKILL.md) |
| [高容量会议平台](use-cases/high-volume-meeting-platform.md) | 设计分布式会议创建和事件处理，具有重试、队列和协调 | [zoom-rest-api](../rest-api/SKILL.md) + [zoom-webhooks](../webhooks/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) |
| [录制与转录](use-cases/recording-transcription.md) | 下载录制内容，获取转录内容 | [zoom-webhooks](../webhooks/SKILL.md) + [zoom-rest-api](../rest-api/SKILL.md) |
| [录制下载管道](use-cases/recording-download-pipeline.md) | 自动下载录制内容到自己的存储（S3、GCS 等） | [zoom-webhooks](../webhooks/SKILL.md) + [zoom-rest-api](../rest-api/SKILL.md) |
| [实时媒体流](use-cases/real-time-media-streams.md) | 通过 WebSocket 访问实时音频、视频、转录内容 | [zoom-rtms](../rtms/SKILL.md) + [zoom-webhooks](../webhooks/SKILL.md) |
| [会议内应用程序](use-cases/in-meeting-apps.md) | 构建在 Zoom 会议内运行的应用程序 | [zoom-apps-sdk](../zoom-apps-sdk/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) |
| [React Native 会议嵌入](use-cases/react-native-meeting-embed.md) | 将会议嵌入 iOS/Android React Native 应用程序 | [zoom-meeting-sdk-react-native](../meeting-sdk/react-native/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) |
| [原生会议 SDK 多平台交付](use-cases/native-meeting-sdk-multi-platform.md) | 在一个认证/版本策略下对齐 Android、iOS、macOS 和 Unreal 会议 SDK 实现 | [zoom-meeting-sdk](../meeting-sdk/SKILL.md) + 平台技能 |
| [原生视频 SDK 多平台交付](use-cases/native-video-sdk-multi-platform.md) | 在一个认证/版本策略下对齐 Android、iOS、macOS 和 Unity 视频SDK实现 | [zoom-video-sdk](../video-sdk/SKILL.md) + 平台技能 |
| [Electron 会议嵌入](use-cases/electron-meeting-embed.md) | 将会议嵌入桌面 Electron 应用程序 | [zoom-meeting-sdk-electron](../meeting-sdk/electron/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) |
| [Flutter 视频会话](use-cases/flutter-video-sessions.md) | 在 Flutter 中构建自定义移动视频会话 | [zoom-video-sdk-flutter](../video-sdk/flutter/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) |
| [React Native 视频会话](use-cases/react-native-video-sessions.md) | 在 React Native 中构建自定义移动视频会话 | [zoom-video-sdk-react-native](../video-sdk/react-native/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) |
| [沉浸式体验](use-cases/immersive-experiences.md) | 使用 Layers API 构建自定义视频布局 | [zoom-apps-sdk](../zoom-apps-sdk/SKILL.md) |
| [协作应用程序](use-cases/collaborative-apps.md) | 会议中的实时共享状态 | [zoom-apps-sdk](../zoom-apps-sdk/SKILL.md) |
| [联系中心应用程序生命周期和上下文切换](use-cases/contact-center-app-lifecycle-and-context-switching.md) | 构建处理参与事件和多参与状态的联系中心应用程序 | [contact-center](../contact-center/SKILL.md) + [zoom-apps-sdk](../zoom-apps-sdk/SKILL.md) |
| [虚拟代理活动 Web 和移动包装器](use-cases/virtual-agent-campaign-web-mobile-wrapper.md) | 跨 Web 和原生移动包装器交付由活动驱动的机器人流程 | [virtual-agent](../virtual-agent/SKILL.md) + [contact-center](../contact-center/SKILL.md) |
| [虚拟代理知识库同步管道](use-cases/virtual-agent-knowledge-base-sync-pipeline.md) | 使用 Web 同步或自定义 API 连接器将外部知识内容同步到 Zoom 虚拟代理 | [virtual-agent](../virtual-agent/SKILL.md) + [zoom-rest-api](../rest-api/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) |
| [Zoom Phone 智能嵌入 CRM 集成](use-cases/zoom-phone-smart-embed-crm.md) | 使用智能嵌入和 Phone API 构建 CRM 拨号器和通话记录流程 | [phone](../phone/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) + [zoom-webhooks](../webhooks/SKILL.md) |
| [Rivet 事件驱动 API 编排器](use-cases/rivet-event-driven-api-orchestrator.md) | 构建一个 Node.js 后端，通过 Rivet 模块客户端组合 webhooks 和 API 操作 | [rivet-sdk](../rivet-sdk/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) + [zoom-rest-api](../rest-api/SKILL.md) |
| [Probe SDK 预检就绪门禁](use-cases/probe-sdk-preflight-readiness-gate.md) | 在加入 Meeting SDK 或 Video SDK 前添加浏览器/设备/网络诊断和就绪策略 | [probe-sdk](../probe-sdk/SKILL.md) + [zoom-meeting-sdk](../meeting-sdk/SKILL.md) 或 [zoom-video-sdk](../video-sdk/SKILL.md) |

## 完整用例索引

- [APIs与MCP路由](use-cases/apis-vs-mcp-routing.md)：根据官方Zoom标准选择仅API、仅MCP或混合路由。
- [AI助手集成](use-cases/ai-companion-integration.md)：将Zoom AI助手功能集成到您的应用工作流程中。
- [AI集成](use-cases/ai-integration.md)：使用Zoom数据接口添加摘要、转录或助手逻辑。
- [后端自动化（S2S OAuth）](use-cases/backend-automation-s2s-oauth.md)：使用账户级OAuth凭证运行服务器端任务。
- [协作应用](use-cases/collaborative-apps.md)：构建会议内共享的应用状态和交互。
- [呼叫中心集成](use-cases/contact-center-integration.md)：将Zoom呼叫中心信号连接到外部系统。
- [呼叫中心应用生命周期和上下文切换](use-cases/contact-center-app-lifecycle-and-context-switching.md)：在呼叫中心应用中实现事件驱动参与状态和安全上下文切换。
- [虚拟代理活动Web和移动封装](use-cases/virtual-agent-campaign-web-mobile-wrapper.md)：在网站和Android/iOS WebView封装中部署基于活动的虚拟代理聊天。
- [虚拟代理知识库同步管道](use-cases/virtual-agent-knowledge-base-sync-pipeline.md)：使用Web同步策略或自定义API连接器自动化知识库摄取。
- [Zoom Phone智能嵌入CRM集成](use-cases/zoom-phone-smart-embed-crm.md)：集成智能嵌入事件、Phone API和CRM工作流，并确保迁移安全的数据处理。
- [Rivet事件驱动API编排器](use-cases/rivet-event-driven-api-orchestrator.md)：构建一个Node.js后端，结合webhook处理和Rivet的API编排。
- [Probe SDK预运行就绪门禁](use-cases/probe-sdk-preflight-readiness-gate.md)：在启动会议或视频会话工作流程之前运行浏览器/设备/网络诊断。
- [自定义视频](use-cases/custom-video.md)：选择Video SDK及相关组件以实现自定义会话UX。
- [自定义会议UI（Web）](use-cases/custom-meeting-ui-web.md)：使用Meeting SDK组件视图围绕真实的Zoom会议构建自定义UI。
- [Scribe转录管道](use-cases/scribe-transcription-pipeline.md)：使用AI服务Scribe进行按需文件转录和批量存档处理。
- [视频SDK自带存储](use-cases/video-sdk-bring-your-own-storage.md)：配置Video SDK云录制直接写入您自己的S3存储桶。
- [客户支持协同浏览](use-cases/customer-support-cobrowsing.md)：实现客户代理协同浏览支持流程。
- [嵌入会议](use-cases/embed-meetings.md)：将Zoom会议体验嵌入到您的应用中。
- [表单完成助手](use-cases/form-completion-assistant.md)：构建用于表单填写和完成协助的引导流程。
- [高清视频分辨率](use-cases/hd-video-resolution.md)：启用和排错高清视频需求。
- [高容量会议平台](use-cases/high-volume-meeting-platform.md)：构建分布式会议创建和事件处理，并采用具体的回退模式。
- [沉浸式体验](use-cases/immersive-experiences.md)：使用Zoom应用层API实现会议内自定义视觉效果。
- [会议内应用](use-cases/in-meeting-apps.md)：构建直接在会议和研讨会环境中运行的Zoom应用。
- [应用市场发布](use-cases/marketplace-publishing.md)：准备并通过应用市场审核发布Zoom应用。
- [会议自动化](use-cases/meeting-automation.md)：以编程方式创建、更新和管理会议。
- [会议机器人](use-cases/meeting-bots.md)：构建用于会议加入、捕获和实时分析的机器人。
- [原生会议SDK多平台交付](use-cases/native-meeting-sdk-multi-platform.md)：标准化Android、iOS、macOS和Unreal会议SDK的交付，包括共享认证和版本控制。
- [原生视频SDK多平台交付](use-cases/native-video-sdk-multi-platform.md)：标准化Android、iOS、macOS和Unity视频SDK的交付，包括共享认证和版本控制。
- [会议详情与事件](use-cases/meeting-details-with-events.md)：结合REST检索和webhook事件流。
- [分钟计算](use-cases/minutes-calculation.md)：跨会议/会话计算使用量和分钟指标。
- [预制视频UI](use-cases/prebuilt-video-ui.md)：使用UI Toolkit加速基于Video SDK的UI交付。
- [QSS监控](use-cases/qss-monitoring.md)：监控Zoom质量统计和性能指标。
- [原始录制](use-cases/raw-recording.md)：捕获原始流以用于自定义录制和处理管道。
- [Electron会议嵌入](use-cases/electron-meeting-embed.md)：在Electron桌面应用中嵌入会议。
- [Flutter视频会话](use-cases/flutter-video-sessions.md)：在Flutter移动应用中构建Video SDK会话。
- [React Native会议嵌入](use-cases/react-native-meeting-embed.md)：将Meeting SDK嵌入到React Native应用中。
- [React Native视频会话](use-cases/react-native-video-sessions.md)：在React Native中构建自定义视频会话。
- [实时媒体流](use-cases/real-time-media-streams.md)：通过RTMS消费实时媒体/转录流。
- [录制下载管道](use-cases/recording-download-pipeline.md)：自动化录制检索和存储管道。
- [录制与转录](use-cases/recording-transcription.md)：管理会议后录制和转录工作流程。
- [检索会议和订阅事件](use-cases/retrieve-meeting-and-subscribe-events.md)：结合REST会议检索和事件订阅。
- [SaaS应用OAuth集成](use-cases/saas-app-oauth-integration.md)：在多租户SaaS应用中实现用户级OAuth。
- [SDK大小优化](use-cases/sdk-size-optimization.md)：减少SDK应用的捆绑包/运行时占用空间。
- [SDK封装和GUI](use-cases/sdk-wrappers-gui.md)：评估SDK封装模式和GUI框架。
- [团队聊天LLM机器人](use-cases/team-chat-llm-bot.md)：构建具有LLM驱动响应的团队聊天机器人。
- [测试与开发](use-cases/testing-development.md)：本地测试模式、模拟和安全的开发循环。
- [令牌和范围故障排除](use-cases/token-and-scope-troubleshooting.md)：调试OAuth范围和令牌不匹配问题。
- [转录机器人（Linux）](use-cases/transcription-bot-linux.md)：运行Linux会议机器人进行实时转录工作负载。
- [使用报告和分析](use-cases/usage-reporting-analytics.md)：收集和分析使用/报告数据。
- [用户和会议创建](use-cases/user-and-meeting-creation.md)：在一个流程中配置用户和安排会议。
- [Web SDK嵌入](use-cases/web-sdk-embedding.md)：在基于浏览器的Web应用中嵌入会议体验。
- [服务器到服务器OAuth与Webhooks](use-cases/server-to-server-oauth-with-webhooks.md)：结合账户OAuth和事件驱动的后端处理。
- [会议链接与嵌入](use-cases/meeting-links-vs-embedding.md)：选择`join_url`分发或SDK嵌入。
- [企业应用部署](use-cases/enterprise-app-deployment.md)：在企业规模上部署、管理和操作Zoom集成。

## 前置条件

1. Zoom账户（专业版、商业版或企业版）
2. 在[Zoom应用市场](https://marketplace.zoom.us/)中创建的应用
3. OAuth凭证（客户端ID和密钥）

## 参考

- [已知限制和特性](references/known-limitations.md)

## 快速入门

1. 前往[marketplace.zoom.us](https://marketplace.zoom.us/)
2. 点击**开发** → **构建应用**
3. 选择应用类型（参见[references/app-types.md](references/app-types.md)）
4. 配置OAuth和范围
5. 将凭证复制到您的应用

## 详细参考

- **[references/authentication.md](references/authentication.md)** - OAuth 2.0、S2S OAuth、JWT模式
- **[references/app-types.md](references/app-types.md)** - 应用类型的决策指南
- **[references/scopes.md](references/scopes.md)** - OAuth范围参考
- **[references/marketplace.md](references/marketplace.md)** - 应用市场门户导航
- **[references/query-routing-playbook.md](references/query-routing-playbook.md)** - 将复杂查询路由到正确的专业技能
- **[references/interview-answer-routing.md](references/interview-answer-routing.md)** - 为zoom-general路由准备的简短面试答案模式
- **[references/routing-implementation.md](references/routing-implementation.md)** - 具体的TypeScript查询分类和技能交接合同
- **[references/automatic-skill-chaining-rest-webhooks.md](references/automatic-skill-chaining-rest-webhooks.md)** - REST + webhook链式工作流的可执行流程
- **[references/meeting-webhooks-oauth-refresh-orchestration.md](references/meeting-webhooks-oauth-refresh-orchestration.md)** - 会议创建 + webhook更新 + OAuth令牌刷新的具体设计
- **[references/distributed-meeting-fallback-architecture.md](references/distributed-meeting-fallback-architecture.md)** - 具有重试、断路器和协调回退的高容量分布式架构
- **[references/community-repos.md](references/community-repos.md)** - 产品团队整理的官方Zoom示例代码库

## SDK维护

- **[references/sdk-upgrade-guide.md](references/sdk-upgrade-guide.md)** - 版本策略、升级步骤
- **[references/sdk-upgrade-workflow.md](references/sdk-upgrade-workflow.md)** - 更新日志 + RSS，可重用的版本级升级工作流程
- **[references/sdk-logs-troubleshooting.md](references/sdk-logs-troubleshooting.md)** - 收集SDK日志

## 资源

- **官方文档**：https://developers.zoom.us/
- **应用市场**：https://marketplace.zoom.us/
- **开发者论坛**：https://devforum.zoom.us/

## 环境变量

- 参见[references/environment-variables.md](references/environment-variables.md)了解标准化的`.env`键和每个值的来源。

## 操作

- [RUNBOOK.md](RUNBOOK.md) - 5分钟预运行和调试检查清单。
