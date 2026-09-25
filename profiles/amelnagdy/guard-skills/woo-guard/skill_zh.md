# Woo Guard

你正在审查在发布前生成或更改的 WooCommerce 代码。在第一次实现检查后，将以下规则作为守门检查步骤应用。WooCommerce 是一个不断发展的平台——订单存储引擎已更改，结账框架已更改——而内存中编写的代码目标是三年前的 WooCommerce。由于涉及金钱，"在我的演示商店上可以运行" 并不是一个标准。

这些规则的存在是因为 AI 代理生成的 WooCommerce 代码存在系统性错误：通过 `get_post_meta()` 读取订单元数据（在 HPOS 商店上损坏），通过直接元数据写入更新产品（跳过查找表和钩子），仅在 JavaScript 中验证结账，价格计算为浮点数，以及 `woocommerce_*` 钩子在确认 WooCommerce 活动之前注册。

## 如何使用此技能

**守门检查模式**（推荐）：在 WooCommerce 代码生成或编辑后，将规则应用于差异或目标文件，然后在交付前运行自我检查。

**实时模式**（显式）：当用户在编写 WooCommerce 代码之前调用此技能时，在编写时应用相同的规则，然后在交付前运行自我检查。

**审查模式**（用户要求你审查或审计 WooCommerce 代码）：浏览 [references/review-checklist.md](references/review-checklist.md) 并生成结构化的发现报告。除非被要求，否则在审查模式下不要编辑代码。

**安全底线**——这些规则在所有 WooCommerce 代码中均以最大严重性级别保留，因为涉及金钱：

- 使用上下文正确的 `esc_*` 函数转义所有输出。
- 在逻辑接触之前，使用 `wp_unslash()` 对所有请求数据进行清理。
- 每次状态更改时进行权限检查并使用 nonce。
- 每个包含变量的查询都使用 `$wpdb->prepare()`。

如果安装了 wp-guard，请与其一起运行以覆盖完整的 WordPress 层。

## 首先适应项目

1. 阅读项目的代理指令和扩展声明的 WooCommerce 版本范围。项目约定在冲突时优先。
2. 确定此代码必须支持的订单存储模式：HPOS、传统帖子或两者（默认假设为两者）。
3. 确定正在使用的结账：Blocks/Store API、传统短代码结账或两者。一个的钩子不会在另一个中触发。
4. 检查 WooCommerce 活动是否受保护：功能检查或在任何 `wc_*` 调用或 `woocommerce_*` 钩子之前使用 `class_exists( 'WooCommerce' )`。

## 规则

### 订单和产品数据——必须修复

1. **订单不是帖子。** 仅通过 CRUD API 访问订单：`wc_get_order()`、`wc_get_orders()`、`$order->get_meta()`、`$order->update_meta_data()` + `$order->save()`。禁止的订单数据：`get_post_meta()`、`update_post_meta()`、`WP_Query`/`get_posts()` 使用 `post_type => shop_order`，以及直接 `$wpdb` 对 postmeta 的连接。这些在传统商店中有效，并在 HPOS 商店中静默损坏。详情：[references/hpos-and-crud.md](references/hpos-and-crud.md)。

2. **CRUD 对象、获取器/设置器，然后保存。** 产品、客户和优惠券通过它们的 CRUD 对象（`wc_get_product()`、设置器、`->save()`）进行操作。直接元数据写入跳过查找表同步，跳过其他扩展依赖的钩子，并跳过缓存失效。库存更改通过 `wc_update_product_stock()` 语义进行；订单状态更改通过 `$order->update_status()`——这会触发商店期望的电子邮件和钩子。

3. **声明功能兼容性。** 任何触摸订单的扩展声明 HPOS 兼容性（`FeaturesUtil::declare_compatibility( 'custom_order_tables', … )`）；任何触摸结账的扩展声明 `cart_checkout_blocks` 兼容性（或在说实话的情况下不兼容）。缺少声明会在每个商店所有者面前显示一个带有你的插件名称的警告横幅。

### 结账和金钱——必须修复

4. **结账验证是服务器端的。** 在 `woocommerce_checkout_process`（传统）或通过 Store API 扩展模式（Blocks）进行验证。JavaScript 验证是用户体验，永远不会是安全性。了解商店正在运行哪种结账，并在扩展声明通用兼容性时连接两者。

5. **金钱不是浮点数。** 价格和总计通过 `wc_format_decimal()` 进行存储安全值，`wc_price()` 进行显示，并通过 WooCommerce 自己的税/舍入设置进行算术。没有手工编写的货币符号，没有对价格使用 `number_format()`，没有对总计使用浮点数相等。

### 运行时纪律——应该修复

6. **保护运行时上下文。** `WC()->cart` 和 `WC()->session` 在 REST、cron、CLI 和管理上下文中为 null——在触摸它们之前进行检查。永远不要假设 webhook 或网关回调中的登录客户。在支持版本范围内验证每个 `woocommerce_*` 钩子和 `wc_*` 函数是否存在——WooCommerce 在主要版本中重命名和退役钩子。

7. **钩子优先于模板覆盖。** 优先顺序：现有的 WooCommerce 钩子/过滤器 → `woocommerce_locate_template` 过滤器 → 主题级别的覆盖。在插件中内嵌的模板覆盖会冻结一个复制文件在 WooCommerce 版本上，并在模板更新时损坏——在审查中始终标记它。

8. **后台工作随订单量扩展。** 批量作业、同步和 webhook 扩展通过 Action Scheduler（与 WooCommerce捆绑）进行，而不是原始 WP-Cron 循环。处理程序是幂等的——真实商店中的订单事件会触发多次。

## 交付前的自我检查

1. 使用 `grep` 在你的差异中搜索 `get_post_meta`、`update_post_meta`、`post_type => 'shop_order'`：它们是否触摸订单？（规则 1）
2. 任何绕过 CRUD 对象的 `save()` 的产品/订单/客户写入？（规则 2）
3. 扩展是否声明 HPOS（以及如果相关则结账块）兼容性？（规则 3）
4. 每个结账规则是否在服务器端强制，针对商店实际运行的结账？（规则 4）
5. 任何浮点数算术、硬编码的货币符号或对金钱使用 `number_format()`？（规则 5）
6. 任何可以在 REST/cron/CLI 中运行的 `WC()->cart`/`WC()->session` 访问？任何未验证的钩子名称？（规则 6）
7. 插件中是否包含任何模板文件？（规则 7）
8. 安全底线：所有输出转义，所有请求输入未转义然后清理，每个状态更改权限检查并验证 nonce，每个变量查询准备？

如果任何答案错误，在向用户展示之前修复它。

## 报告格式（审查模式）

```
**规则 N 违规** 在 `path/file.php:<行或函数>`
- 什么： <一句话>
- 风险： <HPOS 损坏 / 跳过钩子 / 金钱错误 / 结账绕过——一个短语>
- 修复： <一句话>
```

按文件分组，以规则 1–5 的发现开头。如果文件干净，不要提及它。

## 严重性指南

- **必须修复**：规则 1–5 —— 损坏的商店、跳过业务逻辑、错误的金钱
- **应该修复**：规则 6–8 —— 上下文崩溃、更新脆弱性、在规模上死亡的作业

## 参考

- [references/hpos-and-crud.md](references/hpos-and-crud.md) — HPOS 背景、CRUD 模式、兼容性声明、违规表格
- [references/checkout-and-money.md](references/checkout-and-money.md) — 传统与 Blocks 结账、Store API 验证、价格和货币处理
- [references/review-checklist.md](references/review-checklist.md) — 审查模式的结构化浏览
- [references/sources.md](references/sources.md) — WooCommerce 开发者文档 URL；仅在引用时阅读

## 此技能不做什么

- 超越安全底线覆盖完整的 WordPress 层——i18n 和资源/查询纪律在 wp-guard 安装时是 wp-guard 的管辖范围。
- 审查商店配置、主题样式或支付提供程序账户设置。
- 决定定价或业务逻辑——它保护 WooCommerce 代码的发布，而不是商店销售的内容。
