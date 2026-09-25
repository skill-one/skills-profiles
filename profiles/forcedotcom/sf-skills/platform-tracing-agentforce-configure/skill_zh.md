# 平台追踪 — Agentforce 配置

生成 AgentforcePlatformTracingSettings 元数据以启用或禁用将 Agentforce 代理执行追踪跨度转发到 Data Cloud 的摄取管道。这是一个在 API v68.0（2025年春季）引入的单例 Settings 类型，包含一个布尔字段。

## 范围

- **在范围内**：生成 `AgentforcePlatformTracing.settings-meta.xml` 以启用或禁用 Agentforce 代理追踪。
- **超出范围**：TraceSpanEvent 的平台追踪（使用 `platform-tracing-configure`）。事件日志文件。变更数据捕获。组织权限配置。Data Cloud 配置。

---

## 前置条件

在生成之前，告知用户以下要求。该技能无法检查组织状态，但缺少这些前置条件会导致设置无效：

1. **必须在组织中配置 Data Cloud** — 追踪跨度将转发到 Data Cloud 的摄取管道。没有 Data Cloud，跨度没有目的地。
2. **必须激活 `PlatformObservability` 组织权限** — 此权限控制该功能。它由系统配置（不能通过元数据设置）。
3. **API 版本 68.0+** — `AgentforcePlatformTracingSettings` 类型在 2025年春季引入。使用旧 API 版本的组织将无法识别它。

如果用户报告部署后设置未生效，最可能的原因是缺少上述前置条件之一。

---

## 澄清问题

在生成之前，如果还不清楚，请向用户确认：

- 启用还是禁用？（您希望 Agentforce 代理追踪处于什么状态？）

无需其他澄清 — 这是一个单例类型，只有一个布尔字段。

---

## 必须输入的值

在继续之前收集或推断：

- **期望状态**：`true`（启用）或 `false`（禁用）

默认值（除非指定）：
- 如果用户说“启用”或“打开”：设置为 `true`
- 如果用户说“禁用”或“关闭”：设置为 `false`

如果用户提供明确的请求，立即生成，无需不必要的来回沟通。

---

## 工作流程

1. **警告前置条件** — 告知用户此功能需要 Data Cloud 和 `PlatformObservability` 组织权限。
2. **读取模板** — 加载 `assets/AgentforcePlatformTracing-template.xml`。
3. **生成设置文件** — 根据用户的期望状态，将 `{ENABLED}` 替换为 `true` 或 `false`。
4. **放置文件** — 输出到项目源目录中的 `settings/AgentforcePlatformTracing.settings-meta.xml`。

---

## 规则 / 约束

| 约束 | 理由 |
|---|---|
| 单例 — 每个组织只有一个文件，一个布尔字段 | 元数据类型只有一个实例。部署文件会设置组织范围的偏好设置。 |
| XML 命名空间必须为 `http://soap.sforce.com/2006/04/metadata` | 任何其他命名空间会导致部署失败。 |
| 文件必须命名为 `AgentforcePlatformTracing.settings-meta.xml` | SFDX 源格式约定用于此 Settings 类型。 |
| 仅包含 `enableAgentforcePlatformTracing` 字段 | 此类型上不存在其他字段。 |
| 需要 API v68.0+ | 旧版本组织将完全拒绝元数据类型。 |

---

## 注意事项

| 问题 | 解决方案 |
|---|---|
| 部署成功但追踪未激活 | 组织缺少 `PlatformObservability` 权限或 Data Cloud 未配置。这些由系统配置，不能通过元数据设置。 |
| 不识别 `AgentforcePlatformTracingSettings` 类型 | 组织或工具在 API 版本 < 68.0。更新 `sfdx-project.json` 的 sourceApiVersion。 |
| 用户将此功能与平台追踪（TraceSpanEvent）混淆 | 澄清：此功能将 Agentforce 代理执行跨度发送到 Data Cloud。用于发布 TraceSpanEvent 的，请使用 `platform-tracing-configure` 技能。 |

---

## 输出预期

交付物：
- `settings/AgentforcePlatformTracing.settings-meta.xml`

交付前验证：
- [ ] XML 命名空间正好是 `http://soap.sforce.com/2006/04/metadata`
- [ ] 文件名为 `AgentforcePlatformTracing.settings-meta.xml`
- [ ] 仅存在 `enableAgentforcePlatformTracing`（没有额外字段）

---

## 跨技能集成

| 需要 | 委托给 |
|---|---|
| 启用 TraceSpanEvent 发布（平台追踪） | `platform-tracing-configure` 技能 |
| 查询或分析 Data Cloud 中的现有 Agentforce 代理追踪数据 | `agentforce-observe` 技能 |
| 设置变更数据捕获 | `integration-eventing-cdc-configure` 技能 |
| 配置 ManagedEventSubscription | `integration-eventing-subscription-configure` 技能 |

---

## 参考文件索引

| 文件 | 何时读取 |
|---|---|
| `assets/AgentforcePlatformTracing-template.xml` | 第 2 步 — 生成设置文件的模板 |
