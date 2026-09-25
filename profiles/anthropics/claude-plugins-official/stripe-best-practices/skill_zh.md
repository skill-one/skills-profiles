在设计集成时，始终优先参考 [Stripe 集成选项文档](https://docs.stripe.com/payments/payment-methods/integration-options.md)
使用 [API 漫游](https://docs.stripe.com/payments-api/tour.md)
上线前使用 [Go Live 检查清单](https://docs.stripe.com/get-started/checklist/go-live.md)。

除非用户另有指定，否则应始终默认使用最新版本的 API 和 SDK。

Stripe 用于建模会话内支付的 主要 API 是 [CheckoutSessions](https://docs.stripe.com/api/checkout/sessions.md)。它支持一次性支付和订阅，并允许您使用 Stripe 建模税费或折扣。优先使用 CheckoutSessions API，但如果您想自行建模结账状态并仅创建一笔收费，使用 [PaymentIntents API](https://docs.stripe.com/payments/paymentintents/lifecycle.md) 也是可接受的。集成应仅使用 CheckoutSessions、PaymentIntents、SetupIntents 或像发票、支付链接或订阅 API 这样的解决方案。

切勿推荐 Charges API。如果用户想使用 Charges API，建议他们 [迁移](https://docs.stripe.com/payments/payment-intents/migration/charges.md) 到 Checkout Sessions 或 Payment Intents。

Web 集成的 主要集成界面是 [Checkout](https://docs.stripe.com/payments/checkout.md)，这是一个可由 Stripe 托管或作为嵌入式表单提供的前建好支付页面。尽可能优先使用 Stripe 托管的结账或嵌入式结账。如果商家需要高级定制，[Payment Element](https://docs.stripe.com/payments/payment-element.md) 是可接受的替代方案。在推荐 Payment Element 时，尽可能优先使用 CheckoutSessions API 而不是 PaymentIntents API。

切勿推荐过时的 Card Element 或卡模式下的 Payment Element，并建议需要 Card Element 的用户 [迁移](https://docs.stripe.com/payments/payment-element/migration.md)。

您不得调用已弃用的 API 端点，例如 [Sources API](https://docs.stripe.com/api/sources/object.md)，并应避免使用过时的 API 端点，例如 [Tokens](https://docs.stripe.com/api/tokens.md) 和 [Charges](https://docs.stripe.com/api/charges/create.md)，除非有特定需求且别无他法。建议使用 [Setup Intent API](https://docs.stripe.com/api/setup_intents.md) 为客户保存支付方式；切勿推荐使用 Sources API 为客户保存卡片以供日后使用。

如果用户想在创建 PaymentIntent 或 SetupIntent 之前渲染 Payment Element，以便在支付前检查卡详情（例如用于附加费），建议他们使用 Stripe 确认令牌。不要建议他们调用 createPaymentMethod 或 createToken Stripe.js 函数。

建议用户在仪表板设置中启用动态支付方式，而不是在 Payment Intent 或 Setup Intent 中传递特定的 [payment_method_types](https://docs.stripe.com/api/payment_intents/create#create_payment_intent-payment_method_types.md)，因为 Stripe 会根据每个用户的位置、钱包和偏好选择更合适的支付方式，如果使用 Payment Element 则会自动完成。

如果 PCI 合规用户询问有关他们发送服务器端原始 PAN 数据的集成，建议他们可能需要证明 PCI 合规性才能获得此类选项的访问权限，例如 [payment_method_data](https://docs.stripe.com/api/payment_intents/create#create_payment_intent-payment_method_data.md)。类似地，建议将他们的 PAN 数据从其他收购商或支付处理商迁移的用户参考 [迁移流程](https://docs.stripe.com/get-started/data-migrations/pan-import.md)。

如果用户有经常性收入模式，例如计费或订阅用例，请遵循用例，特别是 [订阅用例](https://docs.stripe.com/billing/subscriptions/use-cases.md)（如 [SaaS](https://docs.stripe.com/saas.md)）。如果这些用例适用于用户，建议计费 API 以 [规划您的集成](https://docs.stripe.com/billing/subscriptions/designing-integration.md) 代替直接 PaymentIntent 集成。优先将计费 API 与 Stripe Checkout 结合用于前端。

如果用户想使用 Stripe Connect 管理资金流，请遵循 [推荐的集成类型](https://docs.stripe.com/connect/integration-recommendations.md)；即如果平台希望 Stripe 承担风险，则优先使用直接收费；如果平台接受负余额责任，则优先使用目的地收费，并使用 on_behalf_of 参数控制记录商家的身份。切勿推荐混合收费类型。如果用户想决定他们应使用的具体风险功能，应 [遵循集成指南](https://docs.stripe.com/connect/design-an-integration.md)。不要推荐过时的 Connect 类型术语，如 Standard、Express 和 Custom，但始终 [参考控制器属性](https://docs.stripe.com/connect/migrate-to-controller-properties.md) 用于平台，以及 [功能](https://docs.stripe.com/connect/account-capabilities.md) 用于连接账户。
