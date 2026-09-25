> [所有技能](../../SKILL_TREE.md)

# Sentry 功能设置

在基本 SDK 设置之外配置特定的 Sentry 功能 — OpenTelemetry 管道、警报和 Sentry 快照。本页面帮助您为您的任务找到正确的功能技能。

## 开始 — 在做任何事之前请阅读此部分

**不要跳过此部分。** 不要假设用户需要哪个功能。先询问。

1. 如果用户提到 **OpenTelemetry、OTel Collector 或多服务遥测路由** → `sentry-otel-exporter-setup`
2. 如果用户提到 **警报、通知、排班、Slack/PagerDuty/Discord 集成或工作流规则** → `sentry-create-alert`
3. 如果用户提到 **Apple/Cocoa 快照测试或 Apple 平台的 Sentry 快照** — SnapshotPreviews、Apple 快照、Cocoa 快照、Xcode 快照测试、Swift 预览用于 Sentry 快照、iOS、macOS、tvOS、watchOS 或 visionOS → `sentry-snapshots-cocoa`。

当不清楚时，**询问用户** 他们想要配置哪个功能。不要猜测。

> 信号注入 — 跟踪/跨度、日志记录、指标、AI/LLM 监控或决定要发出什么 — 是独立 `sentry-instrument` 技能的一部分。

---

## 功能技能

| 功能 | 技能 |
|---|---|
| Apple/Cocoa Sentry 快照 — 将 Apple 快照图像上传到 Sentry；当存在 Swift 预览时优先使用 SnapshotPreviews | [`sentry-snapshots-cocoa`](../sentry-snapshots-cocoa/SKILL.md) |
| Sentry 导出器的 OpenTelemetry Collector — 多项目路由、自动项目创建 | [`sentry-otel-exporter-setup`](../sentry-otel-exporter-setup/SKILL.md) |
| 通过工作流引擎 API 的警报 — 电子邮件、Slack、PagerDuty、Discord | [`sentry-create-alert`](../sentry-create-alert/SKILL.md) |

每个技能都包含其自身的检测逻辑、先决条件和分步说明。信任技能 — 仔细阅读并遵循它。不要即兴创作或走捷径。

---

寻找 SDK 设置或调试工作流？请参阅 [完整技能树](../../SKILL_TREE.md)。
