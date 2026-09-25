# 技能集成测试器

## 概述

通过依次执行每个步骤来验证在 CLAUDE.md 中定义的多技能工作流（日常市场监控、每周策略回顾、盈利动能交易等）。检查跨技能数据契约，验证步骤 N 的输出与步骤 N+1 的输入之间的 JSON 架构兼容性，验证文件命名规范，并报告中断的交接。支持使用合成数据集的干运行模式。

## 使用场景

- 在 CLAUDE.md 中添加或修改多技能工作流后
- 修改技能输出格式（JSON 架构、文件命名）后
- 在发布新技能以验证管道兼容性之前
- 调试连续工作流步骤之间中断的交接时
- 作为触及技能脚本拉取请求的 CI 预检查

## 前置条件

- Python 3.9+
- 无需 API 密钥
- 无需第三方 Python 包（仅使用标准库）

## 工作流

### 第 1 步：运行集成验证

对项目的 CLAUDE.md 执行验证脚本：

```bash
python3 skills/skill-integration-tester/scripts/validate_workflows.py \
  --output-dir reports/
```

这将解析多技能工作流部分中所有 `**Workflow Name:**` 块，将每个步骤的显示名称解析为技能目录，并验证其存在性、契约和命名。

### 第 2 步：验证特定工作流

通过名称子字符串定位单个工作流：

```bash
python3 skills/skill-integration-tester/scripts/validate_workflows.py \
  --workflow "Earnings Momentum" \
  --output-dir reports/
```

### 第 3 步：使用合成数据集进行干运行

为每个技能的预期输出创建合成数据集 JSON 文件，并在无真实数据的情况下验证契约兼容性：

```bash
python3 skills/skill-integration-tester/scripts/validate_workflows.py \
  --dry-run \
  --output-dir reports/
```

数据集文件将写入 `reports/fixtures/` 并带有 `_fixture` 标志。

### 第 4 步：查看结果

打开生成的 Markdown 报告以获取人类可读的摘要，或解析 JSON 报告以供程序化使用。每个工作流将显示：
- 步骤级的技能存在性检查
- 交接契约验证（通过 / 失败 / 不适用）
- 文件命名规范违规
- 整体工作流状态（有效 / 中断 / 警告）

### 第 5 步：修复中断的交接

对于每个 `失败` 交接，请验证：
1. 生产者技能的输出包含所有必需字段
2. 消费者技能的输入参数接受生产者的输出格式
3. 生产者输出和消费者输入之间的文件命名模式一致

## 输出格式

### JSON 报告

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-03-01T12:00:00+00:00",
  "dry_run": false,
  "summary": {
    "total_workflows": 8,
    "valid": 6,
    "broken": 1,
    "warnings": 1
  },
  "workflows": [
    {
      "workflow": "Daily Market Monitoring",
      "step_count": 4,
      "status": "valid",
      "steps": [...],
      "handoffs": [...],
      "naming_violations": []
    }
  ]
}
```

### Markdown 报告

按工作流分区的结构化报告，显示步骤验证、交接状态和命名违规。

报告将保存到 `reports/`，文件名格式为 `integration_test_YYYY-MM-DD_HHMMSS.{json,md}`。

## 资源

- `scripts/validate_workflows.py` -- 主验证脚本
- `references/workflow_contracts.md` -- 契约定义和交接模式

## 核心原则

1. 无需 API 密钥 -- 所有验证均为本地离线操作
2. 非破坏性 -- 仅读取 SKILL.md 和 CLAUDE.md，从不修改技能
3. 确定性 -- 相同输入始终产生相同的验证结果
