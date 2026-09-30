---
name: evaluation-methodology
description: PluginEval 质量评估方法，涵盖维度、评估标准和评分公式。在理解插件质量如何被衡量、解释特定维度上的低分、决定如何提高技能的触发准确度或编排适配性、为您的市场设置评分阈值，或向 Neon 等外部合作伙伴解释质量徽章时，请使用此技能。
---

# 评估方法

PluginEval 通过组合最多三个层级，对一项技能或插件进行 0 到 100 的评分。静态层级是一个代码风格检查工具。它速度快且结果确定，适用于检查结构。LLM 评判器和蒙特卡洛层级是实验性的，未通过与人类标签的验证，因此应将它们的数值视为粗略的信号。有关基于跟踪的评估程序，请参阅存储库根目录下的 `evals/README.md`。

评判标准锚点位于 [references/rubrics.md](references/rubrics.md)。每个反模式的修复方法以及每个维度的提示都位于 [references/improving-scores.md](references/improving-scores.md)。

## 评估深度

| 深度 | 层级 | 置信度标签 |
|---|---|---|
| `quick` | 静态 | 估计 |
| `standard`（`score` 的默认值） | 静态和评判器 | 评估 |
| `deep`（由 `certify` 使用） | 静态、评判器和蒙特卡洛（50 次运行） | 认证 |
| `thorough` | 静态、评判器和蒙特卡洛（100 次运行） | 认证+ |

标签命名的是运行了哪个深度，而不是与人类判断的对比。无论请求何种深度，插件目录都只获得静态层级。

## 静态层级（代码风格检查）

静态层级读取 SKILL.md 并不进行任何模型调用。它计算七个子分数，其中前六个为复合维度提供输入：

- `frontmatter_quality`（输入 `triggering_accuracy`）
- `orchestration_wiring`（输入 `orchestration_fitness`）
- `progressive_disclosure`、`structural_completeness`、`token_efficiency`、`ecosystem_coherence`
- `harness_portability`

`harness_portability` 没有映射到任何维度，因此它不会改变一项技能的复合分数。但它占静态层级自身分数的 6%。插件的分数由该层级分数构建，因此可移植性发现可能会略微降低插件的分数。其发现不计为反模式。

静态层级标记六个反模式：`OVER_CONSTRAINED`、`EMPTY_DESCRIPTION`、`MISSING_TRIGGER`、`BLOATED_SKILL`、`ORPHAN_REFERENCE` 和 `DEAD_CROSS_REF`。每个标记都会使分数降低 5%，最低降至 50%：

```text
penalty = max(0.5, 1.0 - 0.05 * anti_pattern_count)
```

报告为每个标记打印一个严重性级别，但惩罚计数标记并忽略严重性。

## LLM 评判器层级（实验性）

评判器层级进行四次模型调用，并返回 0 到 1 的四个整体评分：

- `triggering_accuracy`：Haiku 读取描述并编写 10 个测试提示，其中 5 个应触发，5 个不应触发。它预测每个提示的结果并报告自身的 F1 分数。没有东西检查这些预测是否与实际触发情况一致。
- `orchestration_fitness` 和 `scope_calibration`：Sonnet 根据五点量表对技能进行评分。
- `output_quality`：Sonnet 想象三个任务，并对其预期输出进行评分。

三个 Sonnet 调用只看到 SKILL.md 的前 3,000 个字符。只有一个评判器运行，因为没有任何东西读取 `judges` 设置。

## 蒙特卡洛层级（实验性）

Haiku 编写 15 个应触发技能的提示，该层级重复这些提示以达到 50 次运行（在 `thorough` 情况下为 100 次）。每次运行将 SKILL.md 文本和一个提示发送给模型，该层级记录四个指标：

- 激活率是任何非空回复的运行比例，因此它显示模型是否回答了，而不是技能是否应该触发。
- 输出质量是回复长度除以 500，最高为 1.0。
- 失败率是出错运行的比例。
- 令牌效率是 `1 - median_tokens / 8000`。

每个提示都应触发，因此该层级永远不会检查技能是否保持在无关请求之外。该层级的 JSON 包含其自身指标的 Wilson、bootstrap 和 Clopper-Pearson 区间。复合 `ci_lower` 和 `ci_upper` 字段始终为 null。

## 复合分数

首先，对于每个维度，引擎混合存在的层级分数，并对这些层级的混合权重进行重新归一化。其次，它对加权维度分数求和，并对具有分数的维度进行维度权重的重新归一化。第三，它将总和乘以 100 并乘以反模式惩罚。

| 维度 | 权重 | 静态 | 评判器 | 蒙特卡洛 |
|---|---|---|---|---|
| `triggering_accuracy` | 0.25 | 0.15 | 0.25 | 0.60 |
| `orchestration_fitness` | 0.20 | 0.10 | 0.70 | 无 |
| `output_quality` | 0.15 | 无 | 0.40 | 0.60 |
| `scope_calibration` | 0.12 | 无 | 0.55 | 无 |
| `progressive_disclosure` | 0.10 | 0.80 | 无 | 无 |
| `token_efficiency` | 0.06 | 0.40 | 无 | 0.50 |
| `robustness` | 0.05 | 无 | 无 | 0.80 |
| `structural_completeness` | 0.03 | 0.90 | 无 | 无 |
| `code_template_quality` | 0.02 | 无 | 无 | 无 |
| `ecosystem_coherence` | 0.02 | 0.85 | 无 | 无 |

当层级为维度生成分数时，单元格会读取 "none"，即使 `LAYER_BLENDS` 列出了权重。没有层级生成 `code_template_quality`，因此它始终未测量。对于插件目录，复合分数是插件技能和代理的静态层级的平均分数乘以 100，再乘以插件的反模式计数惩罚。

## 徽章和等级

徽章仅来自复合分数。白金需要至少 90 分，黄金至少 80 分，白银至少 70 分，青铜至少 60 分。`Badge.from_scores` 接受一个 Elo 评分，但没有命令计算它。插件级别的徽章（包括每周 CI 报告中的徽章）仅来自静态层级。在 `standard` 深度或更深的技能级别徽章也包括实验层级。

每个测量的维度在 0 到 100 的量表上获得一个字母等级，从 97 分的 A+ 降至 60 分的 D-，60 分以下为 F。

## 使用方法

```bash
plugin-eval score ./path/to/skill --depth quick     # 仅静态代码风格检查
plugin-eval score ./path/to/skill                   # 静态和评判器
plugin-eval certify ./path/to/skill                 # 深度
plugin-eval compare ./skill-a ./skill-b             # 默认为快速深度
plugin-eval score ./path/to/skill --depth quick --output json --threshold 70
```

在 `standard` 深度或更深时，`score`、`certify` 和 `compare` 会向标准错误打印一条关于评判器和蒙特卡洛层级是实验性的注释。对于插件目录，CLI 会打印一条警告，说明仅运行静态层级。使用 `--threshold` 时，当复合分数低于该值时，命令会退出并返回代码 1。`plugin-eval init` 会写入语料库索引，但没有其他命令会读取它。

## 示例

以下是 JSON 输出的简略示例。脚本可以从其中读取 `composite.score`：

```json
{
  "layers": [{"layer": "static", "score": 0.75, "sub_scores": {}, "anti_patterns": []}],
  "composite": {"score": 76.9, "ci_lower": null, "ci_upper": null, "badge": "silver",
                "confidence_label": "Estimated", "dimensions": []},
  "elo": null
}
```

## 故障排除

- 当添加内容后分数下降时，检查 JSON 中的 `layers[0].anti_patterns`。
- 如果在快速深度下 `triggering_accuracy` 低，请向描述中添加触发短语，例如 "Use this skill when"，后面跟着几个逗号分隔的上下文。
- 评判器分数在运行之间会变化，因为模型每次都会编写新的测试提示和任务。使用静态层级进行您希望重复的比较。
- 如果标准错误显示评判器无法测量某些维度，请使用 `uv sync --extra llm` 安装 LLM 扩展。

## 相关

`eval-judge` 代理在 Claude Code 内对四个评判器维度进行评分，而 `eval-orchestrator` 代理运行 CLI 并合并结果。
