# Sent 模板构建器 UI

围绕 Sent 的 v3 `definition` 合约设计界面。UI 可导入 Meta 材料，但其规范保存和提交的模型绝不能是 Meta 的 `components[]` 负载。

## 产品模型

使用一个草稿对象，包含：

- 可选的 `category` 和 `language`；
- 必须的 `definition.body.multiChannel`；
- 可选的 `sms`、`whatsapp` 和 `rcs` 的完整身体覆盖；
- 可选的 `definition.header`、`footer`、`buttons`、`definitionVersion` 和 `authenticationConfig`；
- `creation_source`、`submit_for_review` 和 `sandbox` 的提交控制。

不要暴露名为 `name`、`channels`、`body`、`header` 或 `buttons` 的顶层创建字段。如果产品需要内部显示标签，请将其保留在 Sent 创建负载之外。

## 推荐的编辑顺序

1.  捕获意图和类别。
2.  编写 `multiChannel` 身体。
3.  将变量作为结构化实体插入。
4.  添加可选的每通道覆盖。
5.  在支持的地方添加页眉、页脚和按钮。
6.  审查实时预览和可访问性。
7.  本地验证并与 `sandbox: true` 验证。
8.  保存草稿，然后明确提交供提供商审核。

类别不应阻止第一个按键，但在提交之前必须可见，因为它会影响认证规则和 WhatsApp 政策审核。

## 变量 UX

插入变量会创建：

- 一个占位符，例如 `{{0:variable}}`；以及
- 一个匹配的实体，包含 `id`、`name`、`type` 和 `props.sample`。

当变量移动时重新编号。永远不要让用户独立于实体表编辑占位符语法。对于裸 `{{1}}` 或没有定义的 ID 显示清晰的错误。

## 验证矩阵

应用 [references/template-validation-matrix.md](references/template-validation-matrix.md) 中的确切规则，包括：

- 每个身体的最大长度为 1,024 个字符；
- 页眉和页脚为 60 个字符；
- 没有页脚变量；
- 总共 10 个按钮；
- 按钮类型 `QUICK_REPLY`、`URL`、`VOICE_CALL`、`PHONE_NUMBER` 和 `COPY_CODE` 及其每类型限制；
- 没有发明的快速回复与 CTA 排他性；
- `authenticationConfig` 和认证限制；
- 完整的、独立有效的通道覆盖。

运行捆绑的 `waba-template-author` 代码检查器对序列化的 JSON 进行检查。服务器验证仍然是权威的。

## 通道预览

### SMS

预览纯文本和估计的 GSM/UCS-2 段。明确说明段估计会影响计费，并且不是模板身体限制。

### WhatsApp

预览页眉、身体、页脚和按钮。显示示例值、类别、语言和提供商审核影响。

### RCS

当前的 Sent RCS 指南支持文本加上最多四个建议芯片。丰富卡片、轮播和媒体附件是路线图功能，而不是当前 Sent 构建器控制。不要为不可用功能生成功能声明。

通道路由属于发送流程，而不是模板编辑器。如果在模拟器中显示路由：

- 省略 `channel` 或 `["sent"]` 表示自动路由和回退；
- `["rcs"]` 固定 RCS 而没有跨通道回退；
- 多个显式值表示广播和单独计费的消息。

永远不要将显式的 RCS-plus-SMS 数组描述为有序回退。

## 保存和审核行为

使用 `sandbox: true` 进行验证。保存时 `submit_for_review: false`。在将其切换为 `true` 之前，显示：

- 类别和语言；
- 带有示例值的渲染预览；
- 通道覆盖；
- 按钮操作；
- 任何警告；
- 事实是提供商审核是一个外部状态变化。

保存时不自动提交。

## 生命周期 UX

资源状态值目前包括 `DRAFT`、`PENDING`、`APPROVED`、`REJECTED` 和 `PAUSED`。保留未知状态渲染器。

WhatsApp 模板 webhook 事件使用 `field: "templates"`，没有 `sub_type`，也没有 `event`；状态是 `payload.status`。提供商值可以包括 `CATEGORY_UPDATED`、`DISABLED` 和其他未来字符串。参见 [references/template-status-handling.md](references/template-status-handling.md)。

## 可访问性和失败恢复

- 将每个错误与字段和摘要关联。
- 不要仅依赖预览颜色。
- 在验证失败后保留用户编辑。
- 为高级用户提供原始 JSON 检查。
- 将导入的 Meta JSON 标记为“Meta Cloud API 源”，直到转换。
- 提供服务器规范和提供商驱动的类别/状态变化的差异。

使用 [references/template-ui-wireflows.md](references/template-ui-wireflows.md) 进行状态转换。使用 `waba-template-author` 进行复制和政策判断，`sent-templates` 用于现有资源操作，`rcs-agent-onboarding` 用于 RCS 启动就绪。
