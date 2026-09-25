# /build-zoom-virtual-agent

背景参考适用于 Zoom 虚拟代理，涵盖：
- 网页活动/聊天嵌入。
- Android WebView 封装。
- iOS WKWebView 封装。
- 知识库同步和自定义 API 摄入。

官方文档：
- https://developers.zoom.us/docs/virtual-agent/
- https://developers.zoom.us/docs/virtual-agent/web/
- https://developers.zoom.us/docs/virtual-agent/android/
- https://developers.zoom.us/docs/virtual-agent/ios/

## 路由护栏

- 如果用户在 Zoom 客户端内实现 Contact Center 应用界面，请链接到 [../contact-center/SKILL.md](../contact-center/SKILL.md)。
- 如果用户需要后端知识库的 CRUD 或自动化脚本，请链接到 [../rest-api/SKILL.md](../rest-api/SKILL.md) 和 [../oauth/SKILL.md](../oauth/SKILL.md)。
- 如果用户仅需要网站机器人嵌入和活动控制，请停留在 [web/SKILL.md](web/SKILL.md)。
- 如果用户需要围绕网页聊天的原生封装，请路由到 [android/SKILL.md](android/SKILL.md) 或 [ios/SKILL.md](ios/SKILL.md)。

## 快速链接

1. [concepts/architecture-and-lifecycle.md](concepts/architecture-and-lifecycle.md)
2. [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)
3. [references/versioning-and-drift.md](references/versioning-and-drift.md)
4. [references/samples-validation.md](references/samples-validation.md)
5. [references/environment-variables.md](references/environment-variables.md)
6. [troubleshooting/common-drift-and-breaks.md](troubleshooting/common-drift-and-breaks.md)
7. [RUNBOOK.md](RUNBOOK.md)

平台技能：
- [web/SKILL.md](web/SKILL.md)
- [android/SKILL.md](android/SKILL.md)
- [ios/SKILL.md](ios/SKILL.md)

## 通用生命周期模式

1. 在虚拟代理管理后台配置活动或入口 ID。
2. 在网页或 WebView 容器中初始化 SDK。
3. 在调用 API 之前，等待就绪 (`zoomCampaignSdk:ready` 或 `waitForReady()`)。
4. 当需要原生编排时，注册桥接处理器 (`exitHandler`, `commonHandler`, `support_handoff`)。
5. 处理对话生命周期 (`engagement_started`, `engagement_ended`) 和 UI 状态。
6. 结束聊天 (`endChat`) 并清理监听器。

## 高级场景

- 带有上下文客户属性的网站活动启动器。
- 带有原生关闭/转接桥接的移动应用 WebView 聊天。
- 通过系统浏览器与应用内浏览器策略处理外部 URL。
- 使用自定义 API 连接器从外部系统同步知识库。
- 跨团队支持流程，从机器人升级到人工支持并附带转接负载。

## 链接

- Contact Center 应用/网页/移动模式：[../contact-center/SKILL.md](../contact-center/SKILL.md)
- OAuth 应用设置和令牌：[../oauth/SKILL.md](../oauth/SKILL.md)
- 知识库自动化 API 工作流：[../rest-api/SKILL.md](../rest-api/SKILL.md)
- 事件驱动后端跟进：[../webhooks/SKILL.md](../webhooks/SKILL.md)

## 运维

- [RUNBOOK.md](RUNBOOK.md) - 5 分钟预检和调试清单。
