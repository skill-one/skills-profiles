# 选择 Zoom 方案

为任务选择最小的正确 Zoom 表面，然后仅分层添加实际所需的支撑组件。

## 决策框架

| 问题类型 | 主要 Zoom 表面 |
|---|---|
| 确定性后端自动化、账户管理、报告、计划任务 | [rest-api](../rest-api/SKILL.md) |
| 将事件传递到您的后端 | [webhooks](../webhooks/SKILL.md) 或 [websockets](../websockets/SKILL.md) |
| 将 Zoom 会议嵌入到您的应用中 | [meeting-sdk](../meeting-sdk/SKILL.md) |
| 构建完全定制的视频体验 | [video-sdk](../video-sdk/SKILL.md) |
| 在 Zoom 客户端内构建 | [zoom-apps-sdk](../zoom-apps-sdk/SKILL.md) |
| 基于 Zoom 数据的 AI 代理工具工作流 | [zoom-mcp](../zoom-mcp/SKILL.md) |
| 实时媒体提取或会议机器人 | [rtms](../rtms/SKILL.md)，当需要时加上 [meeting-sdk](../meeting-sdk/SKILL.md) |
| 电话工作流 | [phone](../phone/SKILL.md) |
| 联系中心或虚拟代理流程 | [contact-center](../contact-center/SKILL.md) 或 [virtual-agent](../virtual-agent/SKILL.md) |

## 指导原则

- 当用户实际需要 Zoom 会议语义时，不要推荐视频 SDK。
- 当用户需要一个完全定制的会话产品时，不要推荐会议 SDK。
- 不要用仅限 MCP 的指导来替代确定性后端自动化。
- 当用户需要既稳定的系统操作又需要 AI 驱动的发现时，优先推荐混合 `rest-api + zoom-mcp` 方案。

## 应产出内容

- 一条推荐路径
- 最小支撑组件
- 严格的约束条件和权衡
- 立即的下一步实施步骤
