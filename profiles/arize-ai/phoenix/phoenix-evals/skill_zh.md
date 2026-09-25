# Phoenix Evals

为 AI/LLM 应用构建评估器。先编写代码，再用 LLM 处理细微之处，通过人类验证。

## 快速参考

| 任务 | 文件 |
| ---- | ----- |
| 设置 | [setup-python](references/setup-python.md), [setup-typescript](references/setup-typescript.md) |
| 决定要评估什么 | [evaluators-overview](references/evaluators-overview.md) |
| 选择裁判模型 | [fundamentals-model-selection](references/fundamentals-model-selection.md) |
| 使用预构建的评估器 | [evaluators-pre-built](references/evaluators-pre-built.md) |
| 构建代码评估器 | [evaluators-code-python](references/evaluators-code-python.md), [evaluators-code-typescript](references/evaluators-code-typescript.md) |
| 构建LLM评估器 | [evaluators-llm-python](references/evaluators-llm-python.md), [evaluators-llm-typescript](references/evaluators-llm-typescript.md), [evaluators-custom-templates](references/evaluators-custom-templates.md) |
| 批量评估DataFrame | [evaluate-dataframe-python](references/evaluate-dataframe-python.md) |
| 运行实验 | [experiments-running-python](references/experiments-running-python.md), [experiments-running-typescript](references/experiments-running-typescript.md) |
| 在测试运行器（CI门禁）中运行评估 | [integrations-pytest](references/integrations-pytest.md), [integrations-vitest-jest](references/integrations-vitest-jest.md) |
| 创建数据集 | [experiments-datasets-python](references/experiments-datasets-python.md), [experiments-datasets-typescript](references/experiments-datasets-typescript.md) |
| 生成合成数据 | [experiments-synthetic-python](references/experiments-synthetic-python.md), [experiments-synthetic-typescript](references/experiments-synthetic-typescript.md) |
| 验证评估器准确性 | [validation](references/validation.md), [validation-evaluators-python](references/validation-evaluators-python.md), [validation-evaluators-typescript](references/validation-evaluators-typescript.md) |
| 导出跨度 | [observe-tracing-setup](references/observe-tracing-setup.md) |
| 编写跨度过滤器（`SpanQuery().where`） | [filter-expressions](references/filter-expressions.md) |
| 采样跟踪以供审查 | [observe-sampling-python](references/observe-sampling-python.md), [observe-sampling-typescript](references/observe-sampling-typescript.md) |
| 分析错误 | [error-analysis](references/error-analysis.md), [error-analysis-multi-turn](references/error-analysis-multi-turn.md), [axial-coding](references/axial-coding.md) |
| RAG评估 | [evaluators-rag](references/evaluators-rag.md) |
| 避免常见错误 | [common-mistakes-python](references/common-mistakes-python.md), [fundamentals-anti-patterns](references/fundamentals-anti-patterns.md) |
| 生产环境 | [production-overview](references/production-overview.md), [production-guardrails](references/production-guardrails.md), [production-continuous](references/production-continuous.md) |

## 工作流

**从零开始：**
[observe-tracing-setup](references/observe-tracing-setup.md) → [error-analysis](references/error-analysis.md) → [axial-coding](references/axial-coding.md) → [evaluators-overview](references/evaluators-overview.md)

**构建评估器：**
[fundamentals](references/fundamentals.md) → [common-mistakes-python](references/common-mistakes-python.md) → evaluators-{code|llm}-{python|typescript} → validation-evaluators-{python|typescript}

**RAG系统：**
[evaluators-rag](references/evaluators-rag.md) → evaluators-code-* (检索) → evaluators-llm-* (忠实度)

**CI门禁：**
evaluators-{code|llm}-{python|typescript} → integrations-{pytest|vitest-jest} → [production-continuous](references/production-continuous.md)

**生产环境：**
[production-overview](references/production-overview.md) → [production-guardrails](references/production-guardrails.md) → [production-continuous](references/production-continuous.md)

## 参考类别

| 前缀 | 描述 |
| ------ | ----------- |
| `fundamentals-*` | 类型、分数、反模式 |
| `observe-*` | 跟踪、采样 |
| `error-analysis-*` | 发现失败 |
| `axial-coding-*` | 分类失败 |
| `evaluators-*` | 代码、LLM、RAG评估器 |
| `experiments-*` | 数据集、运行实验 |
| `integrations-*` | 从测试运行器（pytest、Vitest、Jest）运行评估作为CI门禁 |
| `validation-*` | 通过人类标签验证评估器准确性 |
| `production-*` | CI/CD、监控 |

## 关键原则

| 原则 | 行动 |
| ------ | ------ |
| 首先进行错误分析 | 不能自动化未观察到的内容 |
| 定制优于通用 | 从失败中构建 |
| 先编写代码 | 确定性优先于LLM |
| 验证裁判 | TPR/TNR > 80% |
| 二元优于李克特 | 通过/失败，而非1-5分 |
| 不变量门禁，信号趋势 | `assert`/`expect`硬性不变量（CI红灯）；记录LLM裁判质量信号并门禁汇总（验收标准），而非每个案例 |
