---
name: debug-zoom-integration
description: 快速调试有问题的 Zoom 实现。当身份验证、Webhooks、SDK 加入、MCP 传输或实时媒体工作流出现故障，且您需要隔离问题层以提出修复方案时使用。
---

# 调试 Zoom 集成

当用户已经构建了某些功能但出现故障时，使用此技能。

## 优先排查顺序

1. 身份验证和应用配置
2. 请求构建或事件验证
3. SDK 初始化或平台不匹配
4. Media/session 行为
5. MCP 传输和能力假设

## 需要收集的证据

- 精确的错误文本
- 平台和 SDK/运行时
- 相关请求或有效载荷样本
- 已成功的工作与失败的部分
- 问题是否可复现或间歇性出现

## 参考路由

- [oauth](../oauth/SKILL.md)
- [rest-api](../rest-api/SKILL.md)
- [webhooks](../webhooks/SKILL.md)
- [meeting-sdk](../meeting-sdk/SKILL.md)
- [video-sdk](../video-sdk/SKILL.md)
- [rtms](../rtms/SKILL.md)
- [zoom-mcp](../zoom-mcp/SKILL.md)

## 输出

- 最可能失败的层级
- 排序的假设
- 简短修复计划
- 验证步骤
