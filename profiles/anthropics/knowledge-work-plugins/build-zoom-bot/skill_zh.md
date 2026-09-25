# /build-zoom-bot

使用此技能进行自动化，包括加入会议、捕获媒体或对实时会话数据进行响应。

## 涵盖内容

- 机器人架构
- 会议加入策略
- 实时媒体和字幕处理
- 后端编排
- 存储、后期处理和事件流设计

## 工作流程

1. 明确机器人是否需要加入、观察、转录、总结或采取行动。
2. 将 Meeting SDK 和 RTMS 作为核心实现路径进行路由。
3. 根据需要添加用于会议/资源管理的 REST API 和用于异步事件的 Webhooks。
4. 尽早明确环境和生命周期约束。

## 主要参考

- [meeting-sdk](../meeting-sdk/SKILL.md)
- [rtms](../rtms/SKILL.md)
- [scribe](../scribe/SKILL.md)
- [rest-api](../rest-api/SKILL.md)
- [webhooks](../webhooks/SKILL.md)

## 常见错误

- 将批量转录和实时媒体视为相同的工作流程
- 在定义加入权限和认证模型之前设计机器人
- 遗忘会议后的存储和重试行为
