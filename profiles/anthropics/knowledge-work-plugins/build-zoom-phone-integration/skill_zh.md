# /build-zoom-phone-integration

Zoom Phone 集成背景参考，涵盖 API、webhook、Smart Embed 和 URI 启动工作流。

Zoom Phone 集成实施指南，涵盖 API、webhook/事件、Smart Embed 和 URI 启动工作流。

官方文档：
- https://developers.zoom.us/docs/phone/
- CRM 示例参考：https://github.com/zoom/CRM-Sample

## 路由守卫

- 如果用户需要在 Web 应用中嵌入软电话功能，请使用 Smart Embed ([examples/smart-embed-postmessage-bridge.md](examples/smart-embed-postmessage-bridge.md))。
- 如果用户需要通话记录、分析或自动化，请使用 Phone REST API 和 webhooks ([references/deprecations-and-migrations.md](references/deprecations-and-migrations.md))。
- 如果用户需要从外部 UI 进行点击拨号/SMS 启动，请使用 URI 方案 (`zoomphonecall://`，`zoomphonesms://`)。
- 如果用户混合使用 Zoom Phone 和联络中心，请使用 [../contact-center/SKILL.md](../contact-center/SKILL.md) 进行链式操作。

## 快速链接

从这里开始：
1. [concepts/architecture-and-lifecycle.md](concepts/architecture-and-lifecycle.md)
2. [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)
3. [references/deprecations-and-migrations.md](references/deprecations-and-migrations.md)
4. [references/forum-top-questions.md](references/forum-top-questions.md)
5. [references/smart-embed-event-contract.md](references/smart-embed-event-contract.md)
6. [references/call-handling-patterns.md](references/call-handling-patterns.md)
7. [references/environment-variables.md](references/environment-variables.md)
8. [references/crm-sample-validation.md](references/crm-sample-validation.md)
9. [troubleshooting/common-issues.md](troubleshooting/common-issues.md)
10. [RUNBOOK.md](RUNBOOK.md)
11. [examples/smart-embed-postmessage-bridge.md](examples/smart-embed-postmessage-bridge.md)
12. [examples/phone-api-service-pattern.md](examples/phone-api-service-pattern.md)
13. [references/source-map.md](references/source-map.md)

## 常见生命周期模式

1. 准备账户先决条件（Zoom Phone 许可证、管理员设置、SMS 准备就绪）。
2. 在 Marketplace 中创建 OAuth 应用和范围。
3. 选择集成界面：
- Smart Embed (iframe + postMessage)
- REST + webhooks
- URI 启动 (`callto`，`tel`，`zoomphonecall`，`zoomphonesms`)
4. 捕获实时事件（Smart Embed 事件和/或 webhooks）。
5. 持久化通话标识符并关联记录 (`call_id`，`call_history_uuid`，`call_element_id`)。
6. 应用迁移安全的数映射 (v1 -> v2 -> v3) 并处理重命名的字段。
7. 加强安全性（origin 验证、webhook 签名验证、最小权限范围）。

## 高级场景

- 使用 Smart Embed + 联系人搜索/匹配回调的 CRM 软电话面板。
- 通过 `zp-make-call` 从账户/联系人表格进行点击拨号。
- 使用 `zp-save-log-event` 和自定义备注页面进行通话处理工作流。
- 使用 `zoomphonesms://` 和 `zp-sms-log-event` 进行 SMS 参与工作流。
- 由 `phone.*` webhook 事件驱动的实时运营面板。
- 从传统通话记录迁移到通话历史/通话元素中的通话分析。
- 管理员自动化用于用户/自动接待员/呼叫队列的通话处理设置。

详细内容请参阅 [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)。

## 链式操作

- OAuth 设置/令牌生命周期：[../oauth/SKILL.md](../oauth/SKILL.md)
- 通过 REST 访问电话和账户资源：[../rest-api/SKILL.md](../rest-api/SKILL.md)
- 事件传递和签名验证：[../webhooks/SKILL.md](../webhooks/SKILL.md)
- 联络中心混合旅程：[../contact-center/SKILL.md](../contact-center/SKILL.md)

## 环境变量

- 请参阅 [references/environment-variables.md](references/environment-variables.md) 了解标准化的 `.env` 键以及每个值的来源。
