# Saleor Storefront

Saleor 电子商务平台的通用前端构建指南。涵盖 Saleor GraphQL API 数据模型、权限系统、结账生命周期、渠道架构以及产品和变体模式。框架无关性——无论您使用 Next.js、Remix、Nuxt 还是自定义设置，这些规则都适用。

## 适用场景

在以下情况下参考这些指南：

- 查询 Saleor 的 GraphQL API 获取产品、分类或集合
- 构建带变体选择的商品详情页
- 实现结账和支付流程
- 处理多渠道和多货币设置
- 调试“商品不可购买”或权限错误
- 使用 Saleor 3.23+ 库存可用性模式 (`useLegacyShippingZoneStockAvailability`)
- 通过源代码调查 Saleor API 行为

## 规则类别

| 优先级 | 类别   | 影响   | 前缀       |
| ------ | ------ | ------ | ---------- |
| 1      | API    | 关键   | `api-`     |
| 2      | 产品   | 高     | `products-` |
| 3      | 结账   | 高     | `checkout-` |
| 4      | 渠道   | 中     | `channels-` |

## 快速参考

### 1. API (关键)

- `api-data-model` — 可空字段、定价结构、自动前端过滤
- `api-permissions` — 令牌类型、权限错误、双层查询模式
- `api-graphql-patterns` — 渠道范围查询、变体属性、过滤、代码生成
- `api-investigation` — 如何通过类型和源代码调查 Saleor API 行为

### 2. 产品 (高)

- `products-variants` — 变体模型、选择与非选择属性、定价、用户体验模式

### 3. 结账 (高)

- `checkout-lifecycle` — 会话生命周期、常见错误、调试支付问题

### 4. 渠道 (中)

- `channels-purchasability` — 库存可用性模式（传统与直接、3.23+）、可购买与可配送、履行三角、模式感知清单、渠道范围查询、库存 webhook

## 如何使用

阅读单个规则文件获取详细解释和代码示例：

```
rules/api-data-model.md
rules/products-variants.md
```

每个规则文件包含：

- 解释其重要性的简要说明
- 代码示例（正确和错误的模式）
- 需要避免的反模式

## 完整编译文档

获取包含所有规则展开的完整指南：`AGENTS.md`
