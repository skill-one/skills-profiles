# Zoom 探测器 SDK

在会议或会话工作流开始前，用于用户设备和网络的前置诊断背景参考。

官方文档：
- https://developers.zoom.us/docs/probe-sdk/
- https://marketplacefront.zoom.us/sdk/probe/index.html

参考示例：
- https://github.com/zoom/probesdk-web

## 路径引导

- 当用户需要客户端诊断和就绪评分（设备/网络/浏览器能力）时使用探测器 SDK，而不是用于会议/会话加入。
- 如果用户需要嵌入式会议流程，请路由到 [../meeting-sdk/SKILL.md](../meeting-sdk/SKILL.md)。
- 如果用户需要自定义实时会话 UX，请路由到 [../video-sdk/SKILL.md](../video-sdk/SKILL.md)。
- 如果用户需要事件/API 的后端编排，请与 [../rivet-sdk/SKILL.md](../rivet-sdk/SKILL.md)、[../oauth/SKILL.md](../oauth/SKILL.md) 和 [../rest-api/SKILL.md](../rest-api/SKILL.md) 链接。

## 快速链接

从这里开始：
1. [probe-sdk.md](probe-sdk.md)
2. [concepts/architecture-and-lifecycle.md](concepts/architecture-and-lifecycle.md)
3. [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)
4. [examples/diagnostic-page-pattern.md](examples/diagnostic-page-pattern.md)
5. [examples/comprehensive-network-pattern.md](examples/comprehensive-network-pattern.md)
6. [references/probe-reference-map.md](references/probe-reference-map.md)
7. [references/environment-variables.md](references/environment-variables.md)
8. [references/versioning-and-compatibility.md](references/versioning-and-compatibility.md)
9. [references/samples-validation.md](references/samples-validation.md)
10. [references/source-map.md](references/source-map.md)
11. [troubleshooting/common-issues.md](troubleshooting/common-issues.md)
12. [RUNBOOK.md](RUNBOOK.md)

## 常见生命周期模式

1. 初始化 `Prober` / `Reporter`。
2. 请求媒体权限并枚举设备。
3. 运行目标诊断 (`diagnoseAudio`, `diagnoseVideo`)。
4. 运行全面网络诊断 (`startToDiagnose`) 并将流统计信息传输到 UI。
5. 生成最终报告并应用就绪门禁。
6. 停止/清理 (`stopToDiagnose`, `stopToDiagnoseVideo`, `releaseMediaStream`, `cleanup`)。

## 高级场景

- 会议 SDK 加入操作前的预加入诊断页面。
- 支持捕获结构化报告以供客户故障排除的工作流。
- 机柜或受控端点环境的设备认证流程。
- 高级媒体功能的浏览器能力门禁。

详情请参阅 [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)。

## 链接

- 会议预加入门禁：[../meeting-sdk/web/SKILL.md](../meeting-sdk/web/SKILL.md)
- 视频会话就绪门禁：[../video-sdk/web/SKILL.md](../video-sdk/web/SKILL.md)
- 远程监测/报告摄入后端：[../rivet-sdk/SKILL.md](../rivet-sdk/SKILL.md) + [../rest-api/SKILL.md](../rest-api/SKILL.md)

## 环境变量

- 请参阅 [references/environment-variables.md](references/environment-variables.md) 了解可选的 `.env` 键以及如何获取值。

## 操作

- [RUNBOOK.md](RUNBOOK.md) - 5 分钟前置检查和调试清单。
