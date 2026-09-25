# 评估方法

本文档是 PluginEval 测量插件和技能质量的权威参考。
它涵盖了三个评估层级、全部十个评分维度、复合公式、徽章阈值、反模式标记、Elo 排名和可操作的改进建议。

相关：[完整评分标准锚点](references/rubrics.md)

---

## 三个评估层级

PluginEval 堆叠了三个互补的层级。
每个层级对每个适用维度生成 0.0 到 1.0 之间的分数，后续层级根据每个维度的混合权重覆盖或混合早期层级。

### 层级 1 — 静态分析

**速度：** < 2 秒。无 LLM 调用。确定性。

静态分析器 (`layers/static.py`) 直接针对解析的 SKILL.md 运行六个子检查：

| 子检查 | 衡量内容 |
|---|---|
| `frontmatter_quality` | 名称存在性、描述长度、触发短语质量 |
| `orchestration_wiring` | 输出/输入文档、代码块数量、编排器反模式 |
| `progressive_disclosure` | 行数与甜点（200–600 行）的对比、引用/ 和资产/ 奖励 |
| `structural_completeness` | 标题密度、代码块、示例部分、故障排除部分 |
| `token_efficiency` | MUST/NEVER/ALWAYS 密度、重复行重复率 |
| `ecosystem_coherence` | 对其他技能/代理的交叉引用、"相关"/"另见"提及 |

这六个子检查直接输入到十个最终维度的六个维度（通过 `STATIC_TO_DIMENSION` 映射）。
其余四个维度 — `output_quality`、`scope_calibration`、`robustness` 和 `triggering_accuracy` 的一部分 — 没有静态贡献，完全依赖于层级 2 和/或层级 3。

**反模式惩罚** 乘以层级 1 分数应用：

```
penalty = max(0.5, 1.0 − 0.05 × anti_pattern_count)
```

每个额外检测到的反模式将分数降低 5%，最低为 50%。

### 层级 2 — LLM 评判者

**速度：** 30–90 秒。一个或多个 LLM 调用（默认为 Sonnet）。非确定性。

`eval-judge` 代理读取 SKILL.md 和任何 `references/` 文件，然后使用锚定评分标准（见 [references/rubrics.md](references/rubrics.md)）对四个维度进行评分：

1. **触发准确性** — 基于 10 个心理测试提示推导出的 F1 分数
2. **编排适应性** — 工作者纯度评估（0–1 评分标准）
3. **输出质量** — 模拟 3 个现实任务；评估指令质量
4. **范围校准** — 相对于技能类别的深度和广度进行评判

评判者返回一个结构化的 JSON 对象（无 markdown 拦截符），评估引擎将其合并到复合分数中。当 `judges > 1` 时，分数将平均化，并报告 Cohen's kappa 作为评判者间协议指标。

### 层级 3 — 蒙特卡洛模拟

**速度：** 5–20 分钟。N=50 模拟的 Agent SDK 调用（默认）。统计。

蒙特卡洛运行 `N` 个真实提示通过技能并记录：

- **激活率** — 触发技能的提示比例
- **输出一致性** — 质量分数的变异系数 (CV)
- **失败率** — 使用 Clopper-Pearson 精确置信区间的错误/崩溃比例
- **token 效率** — 中位数 token 数、四分位距、异常值计数

层级 3 复合公式：

```
mc_score = 0.40 × activation_rate
         + 0.30 × (1 − min(1.0, CV))
         + 0.20 × (1 − failure_rate)
         + 0.10 × efficiency_norm
```

其中 `efficiency_norm = max(0, 1 − median_tokens / 8000)`。

---

## 复合评分公式

最终分数是所有三个层级对每个维度的加权混合，然后求和：

```
composite = Σ(dimension_weight × blended_dimension_score) × 100 × anti_pattern_penalty
```

### 维度权重

| 维度 | 权重 | 重要性原因 |
|---|---|---|
| `triggering_accuracy` | 0.25 | 一个从不触发或错误触发的技能没有价值 |
| `orchestration_fitness` | 0.20 | 技能必须是纯工作者；监督逻辑属于代理 |
| `output_quality` | 0.15 | 正确、完整的输出是主要交付物 |
| `scope_calibration` | 0.12 | 既不是存根也不是臃肿的怪物 |
| `progressive_disclosure` | 0.10 | SKILL.md 轻量级；细节存在于 references/ |
| `token_efficiency` | 0.06 | 每次调用中最小上下文浪费 |
| `robustness` | 0.05 | 处理边缘情况而不崩溃 |
| `structural_completeness` | 0.03 | 正确的顺序中的正确部分 |
| `code_template_quality` | 0.02 | 可工作、可复制粘贴的示例 |
| `ecosystem_coherence` | 0.02 | 交叉引用；与兄弟姐妹不重复 |

### 层级混合权重

每个维度以不同的比例从不同的层级获取。当所有三个层级都激活 (`--depth deep` 或 `certify`) 时：

| 维度 | 静态 | 评判者 | 蒙特卡洛 |
|---|---|---|---|
| `triggering_accuracy` | 0.15 | 0.25 | 0.60 |
| `orchestration_fitness` | 0.10 | 0.70 | 0.20 |
| `output_quality` | 0.00 | 0.40 | 0.60 |
| `scope_calibration` | 0.30 | 0.55 | 0.15 |
| `progressive_disclosure` | 0.80 | 0.20 | 0.00 |
| `token_efficiency` | 0.40 | 0.10 | 0.50 |
| `robustness` | 0.00 | 0.20 | 0.80 |
| `structural_completeness` | 0.90 | 0.10 | 0.00 |
| `code_template_quality` | 0.30 | 0.70 | 0.00 |
| `ecosystem_coherence` | 0.85 | 0.15 | 0.00 |

在 `--depth standard`（静态 + 评判者仅）的情况下，混合将被重新归一化以删除蒙特卡洛列。在 `--depth quick`（仅静态）的情况下，所有权重都落在层级 1 上。

### 混合分数计算

对于给定的深度，维度 `d` 的混合分数为：

```
blended[d] = Σ( layer_weight[d][layer] × layer_score[d][layer] )
             ─────────────────────────────────────────────────────
             Σ( layer_weight[d][layer] for available layers )
```

此归一化确保在标准深度跳过蒙特卡洛时不会人为地降低分数。

---

## 解释维度分数

每个维度分数是一个 0.0 到 1.0 之间的浮点数。CLI 将其转换为字母等级：

| 等级 | 分数范围 | 含义 |
|---|---|---|
| A | 0.90 – 1.00 | 优秀 — 无需有意义改进 |
| B | 0.80 – 0.89 | 良好 — 仅存在轻微差距 |
| C | 0.70 – 0.79 | 足够 — 一个或两个明确的改进领域 |
| D | 0.60 – 0.69 | 边缘 — 需要针对性工作 |
| F | < 0.60 | 不及格 — 需要重大纠正 |

在阅读报告时，首先关注具有最高权重的最低等级维度。
在 `triggering_accuracy` 中的 D（权重 0.25）比在 `ecosystem_coherence` 中的 D（权重 0.02）成本高得多。

**置信区间** 在报告中出现时，层级 2 或层级 3 运行。窄 CI（± < 5 分）表示稳定分数。宽 CI 暗示不一致 — 通常由模糊描述或适用于某些提示风格但不适用于其他提示风格的指令引起。

---

## 质量徽章

徽章需要复合分数阈值 AND Elo 阈值（当 Elo 可用时）。
`Badge.from_scores()` 逻辑首先检查复合分数，然后如果提供 Elo 则检查 Elo：

| 徽章 | 复合 | Elo | 含义 |
|---|---|---|---|
| 白金 ★★★★★ | ≥ 90 | ≥ 1600 | 参考质量 — 适合用于金语料库 |
| 金 ★★★★ | ≥ 80 | ≥ 1500 | 生产就绪 |
| 银 ★★★ | ≥ 70 | ≥ 1400 | 功能性，有改进机会 |
| 铜 ★★ | ≥ 60 | ≥ 1300 | 最小可行 — 尚未建议用户使用 |
| — | < 60 | any | 未达到最低标准 |

当 Elo 未计算时（即在快速或标准深度没有 `certify`），会跳过 Elo 阈值。在这种情况下，技能可以仅凭复合分数获得徽章。

---

## 反模式标记

静态分析器检测五个反模式。每个反模式都带有乘以惩罚公式的严重性乘数。

### OVER_CONSTRAINED

**触发：** SKILL.md 中 MUST、ALWAYS 或 NEVER 的出现次数超过 15 次。

**问题：** 过度规定的指令降低模型灵活性，增加 token 开销，并表明作者试图微观管理每个输出，而不是提供原则性指导。

**修复：** 审查每个 MUST/ALWAYS/NEVER。尽可能用解释性框架替换指令性语言。为真正的安全或正确性要求保留硬约束。每 100 行目标少于 10 个此类指令。

### EMPTY_DESCRIPTION

**触发：** 前置 `description` 字段在剥离后少于 20 个字符。

**问题：** 没有有意义的描述，Claude Code 插件系统无法确定何时调用技能。技能对自主调用不可见。

**修复：** 写一个至少 60–120 个字符的描述，包括：
- 一个 "Use this skill when..." 或 "Use when..." 触发子句
- 两个或更多个用逗号或 "or" 分隔的具体上下文

### MISSING_TRIGGER

**触发：** 描述不包含 "use when"、"use this skill when"、"use proactively" 或 "trigger when"（不区分大小写）。

**问题：** 即使长描述对于没有明确触发信号的自主调用也是无用的。系统的路由模型需要明确的提示。

**修复：** 在描述前添加 "Use this skill when..."，然后跟具体场景。
示例："Use this skill when measuring plugin quality, interpreting score reports, or explaining badge thresholds to a team."

### BLOATED_SKILL

**触发：** SKILL.md 超过 800 行 AND 技能没有 `references/` 目录。

**问题：** 单一 SKILL.md 迫使每次调用都将整个文档放入上下文中，浪费只在边缘情况下需要的 token。

**修复：** 创建一个 `references/` 目录并将支持材料移至此处：
- 详细评分标准 → `references/rubrics.md`
- 扩展示例 → `references/examples.md`
- 配置参考 → `references/config.md`

SKILL.md 应使用 `[text](references/filename.md)` 链接到这些文件，以便模型可以按需获取它们。

### ORPHAN_REFERENCE

**触发：** SKILL.md 包含一个 markdown 链接 `[text](references/filename)`，其中 `filename` 不存在于 `references/` 目录中。

**问题：** 死链浪费 token 在永远不会解析的上下文中并使模型困惑。

**修复：** 要么创建缺失的参考文件，要么删除死链。

### DEAD_CROSS_REF

**触发：** SKILL.md 通过相对路径引用另一个技能或代理，而该路径无法从技能目录中解析。

**问题：** 破坏生态系统链接会降低插件的连贯性分数，并可能导致模型尝试导航到不存在的文件。

**修复：** 验证引用的技能是否存在。更新路径或删除引用。

---

## Elo 排名

PluginEval 使用 Elo/Bradley-Terry 评分系统对技能与金语料库进行排名。

**起始评分：** 1500（按惯例为语料库中位数）。

**K 因子：** 32（中等风险评分的标准）。

**预期分数公式**（标准 Elo）：

```
E(A vs B) = 1 / (1 + 10^((B_rating − A_rating) / 400))
```

**每次匹配后的评分更新：**

```
new_rating = old_rating + 32 × (actual_score − expected_score)
```

其中 `actual_score` 胜利为 1.0，平局为 0.5，失败为 0.0。

**置信区间** 通过 500 样本自举计算，报告为 95% CI。
**语料库百分位数** 反映与金语料库的对战胜率。
**位置偏差检查：** 对配对进行两种顺序评估；不一致会被标记。

`plugin-eval init` 命令从插件目录构建语料库索引：

```bash
plugin-eval init ./plugins --corpus-dir ~/.plugineval/corpus
```

---

## CLI 参考

### 仅快速静态分析评分技能

```bash
plugin-eval score ./path/to/skill --depth quick
```

在 < 2 秒内返回层级 1 结果。适用于作者编写期间的快速反馈。

### 使用 LLM 评判者评分（默认）

```bash
plugin-eval score ./path/to/skill
```

运行静态 + LLM 评判者（标准深度）。耗时 30–90 秒。

### 以 JSON 格式输出完整评分

```bash
plugin-eval score ./path/to/skill --output json
```

发出包含 `composite.score`、`composite.dimensions` 和 `layers[0].anti_patterns` 的结构化 JSON。适用于 CI 集成：

```bash
plugin-eval score ./path/to/skill --depth quick --output json --threshold 70
# 如果分数 < 70 则退出代码 1
```

### 完全认证（所有三个层级 + Elo）

```bash
plugin-eval certify ./path/to/skill
```

运行静态 + LLM 评判者 + 蒙特卡洛（50 次模拟）+ Elo 排名。耗时 15–20 分钟。
分配质量徽章。在将技能发布到市场之前使用。

### 头对头比较

```bash
plugin-eval compare ./skill-a ./skill-b
```

在快速深度评估两个技能并打印维度对比表。
适用于在两个实现之间做决定或测量重写前后的改进。

### 初始化用于 Elo 的语料库

```bash
plugin-eval init ./plugins
```

在 `~/.plugineval/corpus` 构建本地语料库索引。在 Elo 排名工作之前需要。

### 脚本化复合公式

离线复制复合分数（预提交钩子、CI 阈值）：

```python
def composite_score(dimension_scores: dict, anti_pattern_count: int = 0) -> float:
    """复制 PluginEval 复合公式。"""
    WEIGHTS = {
        "triggering_accuracy":    0.25,
        "orchestration_fitness":  0.20,
        "output_quality":         0.15,
        "scope_calibration":      0.12,
        "progressive_disclosure": 0.10,
        "token_efficiency":       0.06,
        "robustness":             0.05,
        "structural_completeness":0.03,
        "code_template_quality":  0.02,
        "ecosystem_coherence":    0.02,
    }
    raw = sum(WEIGHTS[d] * s for d, s in dimension_scores.items())
    penalty = max(0.5, 1.0 - 0.05 * anti_pattern_count)
    return round(raw * 100 * penalty, 2)

# 示例：一个触发分数较弱的技能
scores = {
    "triggering_accuracy":    0.65,  # D — 需要描述工作
    "orchestration_fitness":  0.85,
    "output_quality":         0.80,
    # … 填写其余 7 个维度 …
}
# composite_score(scores, anti_pattern_count=1) → ~76.5
```

### JSON 输出格式

`--output json` 的顶层结构：

```json
{
  "composite": { "score": 76.5, "badge": "Silver", "elo": null },
  "dimensions": {
    "triggering_accuracy": { "score": 0.65, "grade": "D", "ci_low": 0.60, "ci_high": 0.70 },
    "orchestration_fitness": { "score": 0.85, "grade": "B", "ci_low": 0.80, "ci_high": 0.90 }
  },
  "layers": [
    { "name": "static", "duration_ms": 1243, "anti_patterns": ["OVER_CONSTRAINED"] },
    { "name": "judge", "duration_ms": 48200, "judges": 1, "kappa": null }
  ]
}
```

在 CI 中解析 `composite.score` 以进行部署：

```bash
score=$(plugin-eval score ./my-skill --output json | python3 -c "import sys,json; print(json.load(sys.stdin)['composite']['score'])")
if (( $(echo "$score < 70" | bc -l) )); then
  echo "质量门禁失败：分数 $score < 70"
  exit 1
fi
```

---

## 提高技能分数的建议

按权重顺序处理维度。最大的收益来自首先修复权重最高的维度。

### 首先改进哪个维度

当分数报告显示多个 D/F 等级时，使用此表格进行优先考虑工作。

| 维度 | 权重 | 典型修复工作量 | 每小时分数影响 | 如果…修复第一个 |
|---|---|---|---|---|
| `triggering_accuracy` | 0.25 | 低 — 描述重写 | 高 | 总分 < 70 |
| `orchestration_fitness` | 0.20 | 中等 — 重新结构部分 | 高 | 技能混合工作者 + 监督逻辑 |
| `output_quality` | 0.15 | 中等 — 添加示例 | 中等 | 评判者分数 < 0.70 |
| `scope_calibration` | 0.12 | 低 — 将内容移至 references/ | 中等 | 文件 < 100 或 > 800 行 |
| `progressive_disclosure` | 0.10 | 低 — 创建 references/ 目录 | 中等 | 不存在 references/ 目录 |
| `token_efficiency` | 0.06 | 低 — 减少 MUST/ALWAYS/NEVER 计数 | 低 | 反模式计数 ≥ 3 |
| `robustness` | 0.05 | 低 — 添加故障排除部分 | 低 | 未记录边缘情况处理 |
| `structural_completeness` | 0.03 | 非常低 — 添加标题/代码块 | 低 | 少于 4 个 H2 标题 |
| `code_template_quality` | 0.02 | 非常低 — 添加语言标签 | 非常低 | 代码块缺少语言标签 |
| `ecosystem_coherence` | 0.02 | 非常低 — 添加 Related 部分 | 非常低 | 完全没有交叉引用 |

**经验法则：** 在做任何其他事情之前修复 `triggering_accuracy` — 权重 0.25 它比所有低权重维度每小时提供的复合分数增益更多。

### 触发准确性（权重 0.25）

- 包含 "Use this skill when..." 后跟 3–4 个用逗号或 "or" 分隔的具体上下文。
- 如果技能应自动激活而不需要明确的用户请求，请添加 "proactively"。
- 心理测试：写 5 个应触发它的提示和 5 个不应触发的提示 — 你的描述能否区分？如果不能，请添加或收紧上下文短语。

### 编排适应性（权重 0.20）

- 文档技能接收的内容和返回的内容 — 不是它编排的内容。
- 避免 "编排"、"协调"、"调度"、"管理工作流" 在 SKILL.md 中。
- 包含一个 "Output format" 部分，并显示 2+ 个代码块展示具体的工人行为。

### 输出质量（权重 0.15）

- 提供具体、可操作的指令 — 不仅仅是目标。
- 明确至少一个边缘情况（空输入、格式错误的数据等）。
- 包含示例部分，展示代表性的输入和预期输出。
- 指令越具体，这个维度得分越高。

### 范围校准（权重 0.12）

- 目标 200–600 行。少于 100 行的是存根；没有 `references/` 超过 800 行的是臃肿的。
- 将背景阅读、扩展示例和参考表移至 `references/`。
- 非常窄的技能应与兄弟姐妹合并；非常广泛的技能应拆分。

### 逐步披露（权重 0.10）

- 添加一个 `references/` 目录（赚取 0.15–0.25 奖励）并保持 SKILL.md 聚焦于执行路径。`assets/` 目录增加进一步的奖励。

### Token 效率（权重 0.06）

- 审计 MUST/ALWAYS/NEVER 计数。目标 < 1 每 10 行。
- 合并近重复的要点和重复结构表格。

### 稳健性（权重 0.05）

- 添加 "Troubleshooting" 或 "Edge Cases" 部分，涵盖至少 3 个故障模式。
- 说明当它无法完成任务时返回的内容。

### 结构完整性（权重 0.03）

- 确保至少 4 个 H2/H3 标题、3 个代码块、示例部分和故障排除部分。

### 代码模板质量（权重 0.02）

- 所有代码块都必须语法有效且带有语言标签可复制粘贴。

### 生态系统连贯性（权重 0.02）

- 添加一个 "## Related" 部分，列出具有相对路径的兄弟姐妹技能或代理。
- 避免重复已经存在于另一个技能中的内容 — 链接到它。

---

## 故障排除

### "添加内容后分数远低于预期"

反模式惩罚会累积。使用 `--output json` 并检查 `layers[0].anti_patterns`。如果你有 5+ 个反模式，乘数可能会将你的分数降低到原始值的 75% 无论如何内容有多好。首先修复标记。

### "triggering_accuracy 较低尽管描述详细"

`_description_pushiness` 评分器寻找特定的句法模式，而不仅仅是长度。
验证你的描述包含短语 "Use this skill when" 或 "Use when"（确切措辞很重要 — 它是正则表达式匹配）。还要检查你是否有多个用逗号或 "or" 分隔的上下文以获得特异性奖励。

### "LLM 评判者分数在不同运行中差异很大"

对于模糊的技能这是预期的。评判者生成 10 个心理测试提示非确定性。通过收紧描述和添加具体示例来提高分数稳定性。当 `judges > 1` 时，平均分数将更稳定。使用 `--depth deep` 与 `certify` 运行蒙特卡洛以获得统计上受约束的分数。

### "progressive_disclosure 分数较低即使文件长度正确"

检查文件是否在 200–600 行的甜点。少于 100 行的文件在这个子检查中仅得 0.20 分。还确认 `references/` 文件不为空 — 评分器检查非空参考文件，而不仅仅是目录。

### "compare 显示我的重写分数低于原始分数"

快速深度 (`--depth quick`) 仅运行静态分析。如果重写将内容移至 `references/` 并显著缩短 SKILL.md，静态分数可能会降低，即使整体质量有所提高。运行 `--depth standard` 以进行更公平的比较，它包括 LLM 评判者对内容质量的评估。

---

## 参考

- [完整评分标准锚点 — 所有 4 个评判者维度](references/rubrics.md)

### 相关代理

- **eval-judge** (`../../agents/eval-judge.md`) — 评判层级 2 维度 (`triggering_accuracy`, `orchestration_fitness`, `output_quality`, `scope_calibration`) 的 LLM 评判者。
  当你需要重新运行仅评判层级或检查其推理时，直接调用它。
- **eval-orchestrator** (`../../agents/eval-orchestrator.md`) — 顶层编排器，按顺序执行所有三个层级、合并结果、分配徽章并写入最终报告。
  运行完整认证传递或进行头对头技能比较时调用。
