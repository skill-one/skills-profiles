# Kanchi 股息美国税务会计

## 概述

为股息投资者应用实用的美国税务工作流程，同时保持决策可审计性。
专注于账户配置和分类，而非替代法律/税务建议。

## 使用场景

在以下情况下使用此技能：
- 需要进行美国股息税务分类规划（合格与普通假设）。
- 在年终税务规划前进行持有期检查。
- 股票/房地产投资信托基金(REIT)/商业开发公司(BDC)/有限合伙企业(MLP)收入持有账户的决策。
- 标准化的年度股息税务备忘录格式。

## 前置条件

准备持有级输入：
- `ticker`
- `instrument_type`
- `account_type`
- `hold_days_in_window`（如果可用）

使用 `references/input-schema.md` 中的确切 JSON 合约和示例。

为确定性输出工件，提供 JSON 输入并运行：

```bash
python3 skills/kanchi-dividend-us-tax-accounting/scripts/build_tax_planning_sheet.py \
  --input /path/to/tax_input.json \
  --output-dir reports/
```

## 安全准则

始终明确说明：税务结果取决于个人事实和司法管辖区。
将此技能视为规划支持，然后将最终申报决策升级给税务专业人士。

## 工作流程

### 1) 对每个分配流进行分类

对于每个持有，将预期现金流分类为：
- 潜在合格股息。
- 普通股息/非合格分配。
- 在适用情况下 REIT/BDC 特定分配成分。

使用 `references/qualified-dividend-checklist.md`
进行持有期和分类检查。

### 2) 验证持有期资格假设

对于潜在合格处理：
- 检查除息日期窗口。
- 检查测量窗口中所需的最低持有天数。
- 标记有失败持有期要求风险的头寸。

如果数据不完整，将状态标记为 `ASSUMPTION-REQUIRED`。

### 3) 映射到申报字段

将规划假设映射到预期的税务表格桶：
- 普通股息总额。
- 合格股息子集。
- 报告时单独的 REIT 相关成分。

使用一致的表格术语，以便年终对账简单明了。

### 4) 构建账户位置建议

使用 `references/account-location-matrix.md` 根据税务配置放置
资产：
- 对于可能保持合格为主的持有，使用应税账户。
- 对于较高普通收入风格的分配，使用税收优惠账户。

当约束冲突（流动性、策略、集中度）时，明确解释权衡。

### 5) 生成年度规划备忘录

使用 `references/annual-tax-memo-template.md` 并包括：
- 使用的假设。
- 分配分类摘要。
- 采取的放置行动。
- 需要会计师/税务顾问审查的开放项目。

## 输出

始终输出：
1. 持有级分配分类表。
2. 带有理由的账户位置建议表。
3. 未解决税务假设风险清单。
4. 可选的 `skills/kanchi-dividend-us-tax-accounting/scripts/build_tax_planning_sheet.py` 生成的工件。

## 节奏

使用最低节奏：
- 年度（60 分钟）：完整的税务规划备忘录与账户位置审查。
- 季度（15 分钟）：刷新近期收购的持有期状态。
- 临时：在重大头寸变化、REIT/BDC 添加或 `kanchi-dividend-review-monitor` 触发的审查后重新运行。

## 多技能交接

- 从 `kanchi-dividend-sop` 接收候选和持有列表。
- 从 `kanchi-dividend-review-monitor` 接收风险事件上下文（`WARN/REVIEW`）。
- 在新条目之前将账户位置约束返回给 `kanchi-dividend-sop`。

## 资源

- `skills/kanchi-dividend-us-tax-accounting/scripts/build_tax_planning_sheet.py`: 税务规划表生成器。
- `skills/kanchi-dividend-us-tax-accounting/scripts/tests/test_build_tax_planning_sheet.py`: 税务规划输出的测试。
- `references/qualified-dividend-checklist.md`: 分类和持有期检查。
- `references/account-location-matrix.md`: 按账户类型和工具的放置矩阵。
- `references/annual-tax-memo-template.md`: 可重用的备忘录结构。
