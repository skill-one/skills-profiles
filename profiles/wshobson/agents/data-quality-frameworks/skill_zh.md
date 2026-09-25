# 数据质量框架

使用 Great Expectations、dbt 测试和数据合约来实现数据质量，以确保可靠的数据管道。

## 使用此技能的场景

- 在管道中实施数据质量检查
- 设置 Great Expectations 验证
- 构建全面的 dbt 测试套件
- 在团队之间建立数据合约
- 监控数据质量指标
- 在 CI/CD 中自动化数据验证

## 核心概念

### 1. 数据质量维度

| 维度        | 描述              | 示例检查                                      |
| ----------- | ----------------- | ------------------------------------------- |
| **完整性**   | 无缺失值          | `expect_column_values_to_not_be_null`          |
| **唯一性**   | 无重复值          | `expect_column_values_to_be_unique`            |
| **有效性**   | 值在预期范围内    | `expect_column_values_to_be_in_set`            |
| **准确性**   | 数据与现实相符     | 交叉验证                                      |
| **一致性**   | 无矛盾            | `expect_column_pair_values_A_to_be_greater_than_B` |
| **及时性**   | 数据是最新的       | `expect_column_max_to_be_between`              |

### 2. 数据测试金字塔

```
          /\
         /  \     集成测试（跨表）
        /────\
       /      \   单元测试（单列）
      /────────\
     /          \ 模式测试（结构）
    /────────────\
```

## 快速入门

### Great Expectations 设置

```bash
# 安装
pip install great_expectations

# 初始化项目
great_expectations init

# 创建数据源
great_expectations datasource new
```

```python
# great_expectations/checkpoints/daily_validation.yml
import great_expectations as gx

# 创建上下文
context = gx.get_context()

# 创建期望套件
suite = context.add_expectation_suite("orders_suite")

# 添加期望
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(column="order_id")
)
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeUnique(column="order_id")
)

# 验证
results = context.run_checkpoint(checkpoint_name="daily_orders")
```

## 详细模式和工作示例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 总结：{total_passed}/{total_tables} 表格通过")
        report.append("")

        for table, result in results.items():
            status = "✅" if result.passed else "❌"
            report.append(f"### {status} {table}")
            report.append(f"- 期望：{result.total_expectations}")
            report.append(f"- 失败：{result.failed_expectations}")

            if not result.passed:
                report.append("- 失败检查：")
                for detail in result.details:
                    if not detail["success"]:
                        report.append(f"  - {detail['expectation']}: {detail['observed_value']}")
            report.append("")

        return "\n".join(report)

# 使用
context = gx.get_context()
pipeline = DataQualityPipeline(context)

要验证的表格 = {
    "orders": "orders_suite",
    "customers": "customers_suite",
    "products": "products_suite",
}

results = pipeline.run_all(tables_to_validate)
report = pipeline.generate_report(results)

# 如果任何表格失败，则失败管道
if not all(r.passed for r in results.values()):
    print(report)
    raise ValueError("数据质量检查失败！")
```

## 最佳实践

### 应做

- **早期测试** - 在转换前验证源数据
- **增量测试** - 发现问题后添加测试
- **记录期望** - 每个测试的清晰描述
- **失败时报警** - 与监控集成
- **版本合约** - 跟踪模式变更

### 不应做

- **不要测试所有内容** - 聚焦于关键列
- **不要忽略警告** - 它们通常预示着失败
- **不要忽略新鲜度** - 陈旧数据是坏数据
- **不要硬编码阈值** - 使用动态基线
- **不要孤立测试** - 测试关系太
