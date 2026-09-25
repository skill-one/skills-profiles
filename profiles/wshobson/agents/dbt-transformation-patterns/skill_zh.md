# dbt 转换模式

适用于 dbt（数据构建工具）的生产就绪模式，包括模型组织、测试策略、文档和增量处理。

## 使用此技能的场景

- 使用 dbt 构建数据转换管道
- 将模型组织到 Staging、Intermediate 和 Marts 层
- 实施数据质量测试
- 为大型数据集创建增量模型
- 文档化数据模型和血缘关系
- 设置 dbt 项目结构

## 核心概念

### 1. 模型层（Medallion 架构）

```
sources/          原始数据定义
    ↓
staging/          与源 1:1，轻度清洗
    ↓
intermediate/     业务逻辑、连接、聚合
    ↓
marts/            最终分析表
```

### 2. 命名规范

| 层级        | 前缀         | 示例                       |
| ------------ | -------------- | ----------------------------- |
| Staging      | `stg_`         | `stg_stripe__payments`        |
| Intermediate | `int_`         | `int_payments_pivoted`        |
| Marts        | `dim_`, `fct_` | `dim_customers`, `fct_orders` |

## 快速入门

```yaml
# dbt_project.yml
name: "analytics"
version: "1.0.0"
profile: "analytics"

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]

vars:
  start_date: "2020-01-01"

models:
  analytics:
    staging:
      +materialized: view
      +schema: staging
    intermediate:
      +materialized: ephemeral
    marts:
      +materialized: table
      +schema: analytics
```

```
# 项目结构
models/
├── staging/
│   ├── stripe/
│   │   ├── _stripe__sources.yml
│   │   ├── _stripe__models.yml
│   │   ├── stg_stripe__customers.sql
│   │   └── stg_stripe__payments.sql
│   └── shopify/
│       ├── _shopify__sources.yml
│       └── stg_shopify__orders.sql
├── intermediate/
│   └── finance/
│       └── int_payments_pivoted.sql
└── marts/
    ├── core/
    │   ├── _core__models.yml
    │   ├── dim_customers.sql
    │   └── fct_orders.sql
    └── finance/
        └── fct_revenue.sql
```

## 详细模式和示例

详细模式文档位于 `references/details.md`。当上层的导航层级不足时，请阅读该文件。

## 最佳实践

### 应该做

- **使用 Staging 层** - 一次清洗数据，处处使用
- **积极测试** - 非空、唯一、关系
- **文档化所有内容** - 列描述、模型描述
- **使用增量** - 对于大于 1M 行的表
- **版本控制** - 将 dbt 项目放在 Git 中

### 不应该做

- **不要跳过 Staging** - 原始数据 → Mart 是技术债务
- **不要硬编码日期** - 使用 `{{ var('start_date') }}`
- **不要重复逻辑** - 提取到宏
- **不要在生产环境测试** - 使用开发目标
- **不要忽视新鲜度** - 监控源数据
