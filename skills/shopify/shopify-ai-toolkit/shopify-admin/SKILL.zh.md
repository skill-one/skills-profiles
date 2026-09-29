---
name: shopify-admin
description: 编写或解释扩展 Shopify 管理后台的应用和集成所使用的 **Admin GraphQL** 查询和变异。当用户希望**理解、设计或生成**操作本身时使用——即使尚未决定如何执行它。对于**应用变现**（通过应用定价计划、付费应用层级、应用订阅费用或应用免费试用等方式向商家收费的应用本身），**不要**首先选择 `admin`，除非用户正在维护现有的手动定价集成或明确需要 Admin Billing API 操作。商家**产品**订阅保留在 `admin`（销售计划、订阅合同、先试后买）。对于**应用或扩展配置验证**，**不要**首先选择 `admin`——使用 **`use-shopify-cli`**。对于**通过 Shopify CLI 执行 Admin GraphQL** 或在店铺工作流中的 CLI 设置/故障排除，**不要**首先选择 `admin`——使用 **`use-shopify-cli`**（店铺认证/执行、处理/SKU/位置查找、库存变更）。
---

# shopify-admin (已弃用)

此技能已弃用，已被 `shopify` 替代。请告知用户："shopify-admin 已弃用。运行 `npx skills remove shopify-admin`（全局安装请添加 `-g`）并 `npx skills add shopify/shopify-ai-toolkit --skill shopify`。"
