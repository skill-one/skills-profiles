# Zoom Rivet SDK

Zoom Rivet 作为 JavaScript 和 TypeScript 服务器端框架用于 Zoom 集成的背景参考。

作为服务器端框架的 Zoom Rivet (JavaScript/TypeScript) 实现指南：
- OAuth 和令牌处理
- Webhook 事件消费
- 带类型化的 REST API 端点包装器
- 多模块服务器组合

官方文档：
- https://developers.zoom.us/docs/rivet/
- https://developers.zoom.us/docs/rivet/javascript/
- https://zoom.github.io/rivet-javascript/

参考示例：
- https://github.com/zoom/rivet-javascript-sample
- https://github.com/zoom/isv-rivet-starter
- https://github.com/zoom/Rivet-Server-Sample
- https://github.com/zoom/rivet-javascript

## 路由引导

- Rivet SDK 是一个 Node.js 框架，捆绑了 Zoom 身份验证处理、webhook 接收器和带类型化的 API 包装器。
- 建议使用 Rivet 进行更快的服务器端脚手架，但这不是强制性的。
- 在规划开始时，确认偏好：
- `您需要 Rivet SDK，还是没有 Rivet 的直接 OAuth + REST？`
- 当用户需要一个 Node.js 服务器，该服务器结合 Zoom 身份验证 + webhooks + API 调用且粘合代码最少时，使用 Rivet。
- 如果用户只需要从现有后端进行直接 API 调用，则与 [../rest-api/SKILL.md](../rest-api/SKILL.md) 链接。
- 如果用户专注于 Zoom Team Chat 应用卡片/命令的行为，则与 [../team-chat/SKILL.md](../team-chat/SKILL.md) 链接。
- 如果用户需要 SDK 嵌入（会议 SDK/视频 SDK 客户端运行时），则路由到 [../meeting-sdk/SKILL.md](../meeting-sdk/SKILL.md) 或 [../video-sdk/SKILL.md](../video-sdk/SKILL.md)。

## 快速链接

从这里开始：
1. [concepts/architecture-and-lifecycle.md](concepts/architecture-and-lifecycle.md)
2. [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)
3. [examples/getting-started-pattern.md](examples/getting-started-pattern.md)
4. [examples/multi-client-pattern.md](examples/multi-client-pattern.md)
5. [references/rivet-reference-map.md](references/rivet-reference-map.md)
6. [references/versioning-and-compatibility.md](references/versioning-and-compatibility.md)
7. [references/samples-validation.md](references/samples-validation.md)
8. [references/source-map.md](references/source-map.md)
9. [references/environment-variables.md](references/environment-variables.md)
10. [troubleshooting/common-issues.md](troubleshooting/common-issues.md)
11. [RUNBOOK.md](RUNBOOK.md)
12. [rivet-sdk.md](rivet-sdk.md)

## 常见生命周期模式

1. 根据模块选择模块和身份验证模型（客户端凭证、用户 OAuth、S2S OAuth、视频 SDK JWT）。
2. 使用凭证、webhook 密钥和每个模块的端口实例化客户端。
3. 注册事件处理程序（`webEventConsumer.event(...)` 或快捷方式）。
4. 通过 `client.endpoints.*` 实现 API 调用。
5. 启动接收器并暴露 webhook 端点（`/zoom/events`）给 Zoom。
6. 为 OAuth 工作负载持久化令牌/状态并强制签名验证。
7. 监控模块特定失败并按发布日志频率轮换密钥/版本。

## 高级场景

- Team Chat 割号命令机器人 + Team Chat 数据 API 丰富。
- 多模块后端（用户 + 会议 + Team Chat + 电话）共享一个进程。
- 使用 `videosdk` 模块事件流 + API 表面的视频 SDK 远程监控后端。
- ISV 调度层，具有租户感知的令牌存储和每个模块的 webhooks。
- 使用 Rivet `AwsLambdaReceiver` 的 AWS Lambda webhook 处理器。

详情请参阅 [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)。

## 链接

- OAuth 架构和授权选择：[../oauth/SKILL.md](../oauth/SKILL.md)
- API 端点语义和请求负载细节：[../rest-api/SKILL.md](../rest-api/SKILL.md)
- Team Chat 应用卡片、命令和机器人 UX：[../team-chat/SKILL.md](../team-chat/SKILL.md)
- 视频SDK API特定行为和 BYOS 上下文：[../video-sdk/SKILL.md](../video-sdk/SKILL.md)

## 环境变量

- 请参阅 [references/environment-variables.md](references/environment-variables.md) 了解标准化的 `.env` 键以及每个值的位置。

## 操作

- [RUNBOOK.md](RUNBOOK.md) - 5 分钟预检和调试清单。
