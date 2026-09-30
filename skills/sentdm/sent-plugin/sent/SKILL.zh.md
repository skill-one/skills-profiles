---
name: sent
description: 当路由是宽泛或模糊时，将请求发送到正确的由MCP支持的操作或专业技能。在用户询问Sent能做什么、说“帮帮我使用Sent”或“设置消息传递”、需要多个Sent工作流，或未明确说明频道、任务或期望操作以选择更具体的技能时使用。
---

# Sent 元调度器

## 概述

这项技能是一个路由器，而不是一个工作器。当请求没有明确标识一个清晰的 Sent 工作流时，检查意图，仅询问选择路由所需的澄清信息，并调用匹配的技能。

Sent 通过其 MCP 服务器执行直接账户操作，并为 SMS、WhatsApp、RCS、发送者配置文件、模板和投递分析提供专家指导。对于实时 Sent 数据或变更，优先选择直接操作技能；对于规划、合规性、诊断或产品设计，优先选择专家技能。

## 何时使用

在以下情况下使用：
- 用户泛泛地提到“Sent”而没有指明渠道（“帮我处理一下 Sent 的问题”、“我想用 Sent 进行消息发送”）
- 用户提出开放式问题，例如“Sent 能帮你做什么？”或“我该从哪里开始？”
- 请求可能涉及多个目标技能（例如，“消息发送不工作”——可能是账户准备情况、10DLC 审核流程、WABA 模板拒绝、RBM 功能或 MDR 管道）
- 渠道不明确（未说明 SMS、WhatsApp 还是 RCS；地理位置很重要，因为 10DLC 仅限美国）
- 表面不明确（API 集成与仪表板 UX、合规性文件）
- 用户粘贴了 Sent 仪表板 URL 或 API 路径但没有进一步上下文

**不**在以下情况下使用：
- 用户已经指定了一个支持的操作或专家工作流；直接调用该技能。
- 问题是关于定价、合同或不受支持的产品政策；将用户指向 `https://docs.sent.dm` 或 Sent 支持。

## 路由规则

### MCP 支持的操作

| 用户意图 | 目标技能 |
|---|---|
| 预览或发送模板消息；检查一条消息及其活动 | `sent-messaging` |
| 列出、检查、创建、总结或删除 Sent 联系人 | `sent-contacts` |
| 查找、检查或删除现有的 Sent 模板 | `sent-templates` |
| 查询仪表板消息发送指标或查询号码功能 | `sent-analytics` |
| 检查所选账户、余额、上线状态或发送准备情况 | `sent-account-readiness` |

### 专家指导

| 用户意图 | 目标技能 |
|---|---|
| SMS 合规性、10DLC、品牌或活动注册、TCR 审核流程或运营商拒绝 | `sms-10dlc-registration` |
| 编写 WhatsApp 模板内容、选择类别或修复 Meta 拒绝 | `waba-template-author` |
| 通过嵌入式注册、回调、令牌交换或电话号码映射连接 WABA | `waba-embedded-signup` |
| 启动 RCS、准备 RBM 代理或决定功能与回退方案 | `rcs-agent-onboarding` |
| 设计多租户发送者配置文件边界、路由或速率限制所有权 | `sender-profile-architect` |
| 从 MDR 导出、管道、群体或跨渠道失败代码诊断投递 | `messaging-performance-analyzer` |
| 设计或审核面向租户的模板构建器 UI | `template-builder-ui` |

### 工程与集成

| 用户意图 | 目标技能 |
|---|---|
| 将 Sent 添加到代码库、选择 SDK 或在发布前加固重试、幂等性和错误处理 | `sent-integration-starter` |
| 构建或调试 webhook 接收器、签名验证、去重或自动禁用端点 | `sent-webhook-engineer` |
| 选择渠道字段、预期跨渠道回退或解释路由、重路由或投递结果 | `sent-routing-strategist` |
| 处理传入消息、退订关键词、同意状态、WhatsApp 24 小时窗口或对话历史 | `sent-two-way-messaging` |
| 通过 API 执行发送者配置文件生命周期，包括完成回调、活动和用户角色 | `sent-profile-provisioning` |
| 用 Sent 替换 Twilio、Sinch、Infobip、Vonage 或 Bird，包括切换和回滚计划 | `migrate-to-sent` |

在此组中，请注意两个频繁的交接：`sender-profile-architect` 决定租户边界，`sent-profile-provisioning` 实施它；`migrate-to-sent` 计划供应商替换，`sent-integration-starter` 加固结果集成。

如果请求与某一行完全匹配，则调用该技能并停止。如果涉及多行，则说明建议顺序并从先决条件开始。例如，在实时发送前检查 `sent-account-readiness`，在 `sent-messaging` 之前使用 `sent-templates` 定位现有模板，并在用户提供导出而不是请求实时仪表板指标时使用 `messaging-performance-analyzer`。

## 路由前需要询问的澄清问题

仅询问选择路线所需的信息。一旦渠道 + 工作流变得明确，就停止。

1. **渠道** — SMS、WhatsApp、RCS 还是未确定？
2. **工作流阶段** — 新建、集成过程中还是调试已工作的功能？
3. **地理位置** — 仅限美国、国际或两者？（对于 SMS 很重要——10DLC / TCR 仅限美国。）
4. **表面** — 实时账户操作、API/后端集成、仪表板 UX 或合规性文件？
5. **受众** — 您是 Sent 的最终租户，还是正在构建多租户 Sent 平台？（发送者配置文件与单租户上线。）
6. **症状**（如果调试）— 错误代码、拒绝原因、低审核分数或纯投递率下降？
7. **手头上的工件** — 您有联系人、模板或消息 ID、模板草稿、MDR 导出、RBM 代理 ID 或 `config_id` 吗？

每次一个问题是合适的；一次不要问所有七个问题。

## 无需路由的情况

这项技能不是一般问题的回退。如果用户询问：
- **余额、上线状态或所选账户是否可以发送** — 使用 `sent-account-readiness`。
- **合同、计划定价、发票或可用操作无法回答的账户访问权限** — 指导用户联系 Sent 支持或 `https://docs.sent.dm`。
- **通用工程**，如重试、队列或没有特定于 Sent 的工作的可观察性 — 正常回答；一旦问题涉及 Sent 自身的重试、幂等性或速率限制合同，再路由到 `sent-integration-starter`。
- **Meta、Google、TCR 或运营商政策超出专家技能范围** — 使用当前上游文档。

如果在澄清问题后，请求仍然不适合任何目标技能，请明确说明。不要强行路由。

## 共享术语

当路由决策取决于 Sent、SMS、WhatsApp、RCS 或 MCP 术语时，请阅读 `references/sent-glossary.md`。将操作细节保留在目标技能中，而不是在此处重复。
