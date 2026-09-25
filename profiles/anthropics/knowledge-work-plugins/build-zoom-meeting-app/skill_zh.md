# /build-zoom-meeting-app

使用此技能用于嵌入式会议体验和会议生命周期实现。

## 涵盖内容

- 会议SDK选择和平台路由
- 加入/认证实现规划
- 会议创建及加入流程设计
- 网页版与原生平台考虑因素
- 会议SDK与视频SDK边界决策

## 工作流程

1. 确认用户是否需要Zoom会议或自定义视频会话。
2. 如果用户需要实际的Zoom会议，则路由到Meeting SDK。
3. 引入相关平台参考。
4. 仅添加用于会议创建、资源管理或报告的REST API。
5. 仅在用例明确需要时添加webhooks或RTMS。

## 主要参考

- [meeting-sdk](../meeting-sdk/SKILL.md)
- [rest-api](../rest-api/SKILL.md)
- [webhooks](../webhooks/SKILL.md)
- [rtms](../rtms/SKILL.md)
- [video-sdk](../video-sdk/SKILL.md)

## 常见错误

- 使用Video SDK进行普通Zoom会议嵌入
- 没有理由将资源管理API混合到核心加入流程中
- 直到最后才跳过特定平台的SDK约束
