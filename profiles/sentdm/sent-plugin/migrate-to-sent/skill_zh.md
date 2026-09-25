# 迁移至 Sent

从任何主要的 CPaaS 提供商迁移都会遇到五个相同的翻译问题。按顺序处理它们，因为第一个问题会无声地加倍成本，并且在测试中无法发现。

## 1. 有序回退变为自动路由

现有平台通过不同的调用端数组、故障转移对象、消息服务功能或应用程序级别的优先级配置来表示跨渠道交付。不要假设这些形状与 Sent 的请求字段有直接的等效关系。

**Sent 的 `channel` 数组是一个广播列表。** 迁移一个有序数组会产生每个接收者-渠道对的一条消息和一个费用，这会通过测试并增加生产支出。正确的翻译是自动路由——省略 `channel` 或发送 `["sent"]`——这允许平台选择路由并在同一个 `message_id` 上重新路由最多三个渠道和提供商对。细节属于 `sent-routing-strategist`；迁移规则很简单：**永远不要迁移有序的渠道列表。**

## 2. 状态词汇表不一致

现有状态映射到 Sent 的状态，但 Sent 增加了两个没有等效状态的状态，这会破坏简单的重试逻辑。

| Sent 状态 | 最接近的现有平台类比 | 迁移说明 |
| --- | --- | --- |
| `QUEUED` | Twilio `queued`，Sinch `QUEUED_ON_CHANNEL` | 已接受，未发送 |
| `ROUTED` | 无类比 | 已选择路由；在重新路由时再次触发 |
| `SENT` | Twilio `sent`，Sinch `MESSAGE_SUBMIT` | 提供商交接仅 |
| `DELIVERED` | 各处 `delivered` | 手持设备接收的第一个证明 |
| `READ` | Twilio `read`，Sinch `READ` | 仅限 WhatsApp 和 RCS |
| `FAILED` | `failed`，`undelivered` | 可能仍会重新路由；不一定是最终结果 |
| `FILTERED` | Twilio 错误 21610（选择退出） | **策略门。永远不要重试** |
| `BLOCKED` | 账户级错误 | **账户先决条件。修复账户，然后重新发送** |
| `SCHEDULED` | 无类比 | 安静时段停放；自动恢复 |

迁移代码的两个后果。将每个非交付终端状态视为可重试的处理程序将重试选择退出块，这是一种合规性失败而不是错误。基于数字提供商错误代码的处理程序——Twilio 的 `21610` 是经典案例——必须重写为 Sent 的字符串 `error.code` 系列。

## 3. Webhook 验证需要重写，而不是迁移

没有两个提供商使用相同的签名方式，并且没有 Sent SDK 提供验证器。

| 提供商 | 方案 |
| --- | --- |
| Twilio | `X-Twilio-Signature`，base64 HMAC-**SHA1** 加密完整 URL 加上排序的 POST 参数 |
| Sinch | HMAC-SHA256 加密 `body.nonce.timestamp`，四个 `x-sinch-webhook-signature*` 标头，或 OAuth 2.0 |
| Infobip | Basic，HMAC-SHA256 加密原始正文，或通知配置文件上的 OAuth；**标头名称是账户配置的** |
| Vonage | JWT 在 `Authorization: Bearer` 中，或遗留 `sig` 参数 |
| MessageBird/Bird | `messagebird-signature`，base64 HMAC-SHA256 加密时间戳、URL 和 SHA-256 正文哈希 |
| **Sent** | `x-webhook-signature: v1,{base64}`，HMAC-SHA256 加密 `{x-webhook-id}.{x-webhook-timestamp}.{raw_body}` |

Sent 的关键是签名密钥，去掉 `whsec_` 并进行 base64 解码，以恒定时间进行比较，时间戳超出 300 秒将被拒绝。由于 Sent 不提供每个事件的 ID，去重键必须从有效载荷语义中派生。使用 `sent-webhook-engineer` 构建接收器，而不是调整现有验证器。

## 4. 选择退出存储必须对账，而不是通过复制迁移

每个提供商都保留自己的屏蔽列表——Twilio 高级选择退出，Infobip 屏蔽列表，Sinch OPT_IN/OPT_OUT 事件。Sent 在事件到达应用程序之前在平台级别执行同意，将其存储为联系人的 `opt_out`，并**无渠道地**应用：SMS 上的 `STOP` 会屏蔽 WhatsApp 和 RCS。

对账规则：在切换之前导出现有平台的屏蔽列表，将任何现有渠道上的选择退出视为全局 Sent 选择退出，并且永远不要清除 `opt_out` 以“清理”迁移的数据。Sent 的十个默认关键字是 `STOP`，`CANCEL`，`UNSUBSCRIBE`，`QUIT`，`END`，`START`，`UNSTOP`，`SUBSCRIBE`，`HELP`，`INFO`，仅在全部修剪后的正文等于关键字时匹配——因此现有平台特定的关键字需要自定义关键字条目。将任何现有关键字匹配器重写为精确的本地同意镜像和审计机制；匹配器不应再次将同意写入 Sent。同意语义属于 `sent-two-way-messaging`。

## 5. 模板和租户需要重新注册，而不是转移

WhatsApp 模板与 WABA 一起存在，因此迁移问题是 WABA 是否移动。位置占位符（`{{1}}`，`{{2}}`）变为 Sent 中的**命名**参数，这意味着每个传递有序数组的调用站点必须传递一个命名映射。批准是异步的，并作为 `templates` webhook 事件到达，因此请在切换之前构建模板库存，而不是在切换期间。

租户映射如下，边界决策由 `sender-profile-architect` 拥有，API 工作由 `sent-profile-provisioning` 完成：

| 现有平台结构 | Sent 等效项 |
| --- | --- |
| Twilio 子账户 | 发送配置文件 |
| Twilio 消息服务 | 路由加上配置文件配置，而不是调用端池 |
| Infobip 应用程序或实体 | 发送配置文件 |
| Sinch 对话 API 应用程序 | 发送配置文件 |
| 每个租户的提供商 API 凭据 | 配置文件范围的 API 密钥，或组织密钥带有 `x-profile-id` |

## 迁移顺序

1. **列出**每个发送调用站点、webhook 处理程序、状态分支、模板、屏蔽列表和凭据。使用 `scripts/inventory_scan.py` 机械地查找它们。
2. **映射**每个项目使用 [references/provider-mapping.md](references/provider-mapping.md)，标记有序回退数组和数字错误代码作为需要重写的项目。
3. **并行启动 Sent**：凭据、每个环境一个 webhook、验证接收器、模板重新注册并批准。
4. **在沙盒中证明等效性**，使用 `"sandbox": true`，然后使用一个小型实时群组确认 `DELIVERED`。
5. **分流运行**，比较相同消息类别的交付率、延迟和每条消息的成本。
6. **切换**按消息类别——最低风险事务首先，营销最后——保持现有接收器在线。
7. **仅在完整计费周期内数据干净后**才停用，然后撤销现有凭据。

顺序细节、验证门和回滚触发器在 [references/cutover-playbook.md](references/cutover-playbook.md) 中。

## 测试中幸存的错误

- 迁移有序渠道数组。加倍成本，永远不报错。
- 将 `FILTERED` 视为可重试。合规性风险。
- 重用现有签名验证器。每次交付返回 401。
- 假设 `202` 表示已交付。Sent 仅确认接受。
- 保留位置模板占位符。参数无声不匹配。
- 在 `401` 上重试。连续十次身份验证失败会锁定凭据，锁定会升级。
- 在双运行期间省略 `Idempotency-Key`。超时重试会发送两次。
- 使用配置文件范围密钥发送 `x-profile-id`。返回 `403`。
- 复制现有平台的 `Authorization: Bearer` 模式。Sent 使用 `x-api-key` 进行身份验证。

## 边界

这项技能拥有提供商映射和逐行迁移规划。将生成的 Sent 客户端和弹性工作交给 `sent-integration-starter`，信道语义交给 `sent-routing-strategist`，接收器构建交给 `sent-webhook-engineer`，WhatsApp 导入交给 `waba-embedded-signup`，美国活动注册交给 `sms-10dlc-registration`。
