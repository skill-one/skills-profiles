# 平台追踪 — 配置

生成 EventSettings 元数据以启用或禁用平台追踪开关，该开关控制 TraceSpanEvent 是否以采样率发布。这会修改现有 EventSettings 元数据类型中的一个字段（`enablePlatformTracing`）。

## 范围

- **在范围内**：生成 `Event.settings-meta.xml` 并包含 `enablePlatformTracing` 字段以启用或禁用 TraceSpanEvent 发布。
- **超出范围**：Agentforce 代理追踪到数据云（使用 `platform-tracing-agentforce-configure`）。其他 EventSettings 字段（`enableDeleteMonitoringData`、`enableLoginForensics` 等）由其他团队拥有。事件日志文件。变更数据捕获。

---

## 前置条件

生成前，需告知用户以下要求：

1. **`PlatformTracing` 组织权限** 必须处于激活状态 — 此权限控制该功能。它由系统分配（不能通过元数据设置）。如果没有此权限，设置会部署，但 TraceSpanEvent 不会发布。
2. **API 版本 68.0+** — `enablePlatformTracing` 字段于 2025 年春季版本引入 EventSettings。较旧 API 版本的组织或工具将无法识别该字段。如果使用较旧工具版本，请将 `sfdx-project.json` 中的 `sourceApiVersion` 更新为 `68.0` 或更高。

如果用户报告部署后设置无效，最可能的原因是缺少上述前置条件。

---

## 需要澄清的问题

生成前，需与用户确认（如果尚未明确）：

- 启用还是禁用？（您希望平台追踪 / TraceSpanEvent 处于什么状态？）

无需其他澄清 — 这仅控制一个布尔字段。

---

## 必须输入的信息

进行下一步前，收集或推断：

- **期望状态**：`true`（启用）或 `false`（禁用）

默认值（除非指定）：
- 如果用户说“启用”或“打开”：设置为 `true`
- 如果用户说“禁用”或“关闭”：设置为 `false`

如果用户提供明确请求，立即生成，无需不必要的反复沟通。

---

## 工作流程

1. **警告前置条件** — 告知用户此功能需要 `PlatformTracing` 组织权限和 API 版本 68.0+。
2. **读取模板** — 加载 `assets/EventSettings-template.xml`。
3. **生成设置文件** — 根据用户的期望状态，将 `{ENABLED}` 替换为 `true` 或 `false`。
4. **放置文件** — 输出到项目源目录中的 `settings/Event.settings-meta.xml`。

---

## 规则 / 限制

| 限制 | 理由 |
|---|---|
| 仅在生成的元数据中包含 `enablePlatformTracing` | EventSettings 中的其他字段由其他团队拥有。包含它们可能导致部署期间覆盖无关设置。 |
| XML 命名空间必须为 `http://soap.sforce.com/2006/04/metadata` | 任何其他命名空间会导致部署失败。 |
| 文件必须命名为 `Event.settings-meta.xml` | SFDX 源格式规范 — EventSettings 的类型名称前缀为 `Event`。 |
| 需要 `PlatformTracing` 组织权限 | 没有此权限，设置会部署，但对 TraceSpanEvent 发布无影响。 |
| 需要 API v68.0+ | 较旧的组织/工具会完全拒绝该字段。 |

---

## 注意事项

| 问题 | 解决方案 |
|---|---|
| 部署成功但 TraceSpanEvent 未发布 | 组织缺少 `PlatformTracing` 权限。这是系统分配的，不能通过元数据设置。 |
| `enablePlatformTracing` 字段未被组织/工具识别 | 工具版本在 API < 68.0。将 `sfdx-project.json` 中的 `sourceApiVersion` 更新为 `68.0` 或更高。 |
| 用户将此功能与 Agentforce 追踪混淆 | 澄清：此功能发布平台操作的 TraceSpanEvent。要将 Agentforce 代理跨段发送到数据云，请使用 `platform-tracing-agentforce-configure` 技能。 |
| 用户想配置所有事件监控设置 | 仅 `enablePlatformTracing` 在范围内。其他 EventSettings 字段由其他团队拥有，不由此技能管理。 |

---

## 输出预期

交付物：
- `settings/Event.settings-meta.xml`

交付前验证：
- [ ] XML 命名空间必须为 `http://soap.sforce.com/2006/04/metadata`
- [ ] 文件名必须为 `Event.settings-meta.xml`
- [ ] 仅包含 `enablePlatformTracing`（无其他 EventSettings 字段）
- [ ] 项目 `sourceApiVersion` 在 `sfdx-project.json` 中为 `68.0` 或更高

---

## 跨技能集成

| 需求 | 委托给 |
|---|---|
| 启用 Agentforce 代理跨段发送到数据云 | `platform-tracing-agentforce-configure` 技能 |
| 设置变更数据捕获 | `integration-eventing-cdc-configure` 技能 |
| 配置 ManagedEventSubscription | `integration-eventing-subscription-configure` 技能 |

---

## 参考文件索引

| 文件 | 何时读取 |
|---|---|
| `assets/EventSettings-template.xml` | 第 2 步 — 生成设置文件的模板 |
