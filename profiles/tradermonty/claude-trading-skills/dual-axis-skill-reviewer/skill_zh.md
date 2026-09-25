# 双轴技能评审器

运行双轴评审器脚本并将报告保存到 `reports/`。

该脚本支持：
- 随机或固定技能选择
- 自动轴评分（可选执行测试）
- LLM 提示生成
- LLM JSON 评审合并（带加权最终分数）
- 通过 `--project-root` 进行跨项目评审
- 非评分显示 `skills-index.yaml` 生产验证声明

## 使用场景

- 需要 `skills/*/SKILL.md` 中单个技能的可重复评分。
- 最终分数低于 90 时需要改进项。
- 需要确定性和定性 LLM 代码/内容评审。
- 需要从命令行评审不同项目中的技能。

## 前置条件

- Python 3.9+
- `uv`（推荐——通过内联元数据自动解析 `pyyaml` 依赖）
- 测试：`uv sync --extra dev` 或目标项目中的等效命令
- LLM 轴合并：遵循 LLM 评审模式的 JSON 文件（见资源）

## 工作流程

根据您的上下文确定正确的脚本路径：

- **同一项目**：`skills/dual-axis-skill-reviewer/scripts/run_dual_axis_review.py`
- **全局安装**：`~/.claude/skills/dual-axis-skill-reviewer/scripts/run_dual_axis_review.py`

以下示例使用 `REVIEWER` 作为占位符。设置一次：

```bash
# 如果在同一项目评审：
REVIEWER=skills/dual-axis-skill-reviewer/scripts/run_dual_axis_review.py

# 如果评审其他项目（全局安装）：
REVIEWER=~/.claude/skills/dual-axis-skill-reviewer/scripts/run_dual_axis_review.py
```

### 第 1 步：运行自动轴 + 生成 LLM 提示

```bash
uv run "$REVIEWER" \
  --project-root . \
  --emit-llm-prompt \
  --output-dir reports/
```

当评审不同项目时，将 `--project-root` 指向该项目：

```bash
uv run "$REVIEWER" \
  --project-root /path/to/other/project \
  --emit-llm-prompt \
  --output-dir reports/
```

### 第 2 步：运行 LLM 评审
- 使用 `reports/skill_review_prompt_<skill>_<timestamp>.md` 中的生成提示文件。
- 要求 LLM 返回严格的 JSON 输出。
- 在 Claude Code 内运行时，让 Claude 担任协调者：读取生成的提示，生成 LLM 评审 JSON，并保存以供合并步骤使用。

### 第 3 步：合并自动 + LLM 轴

```bash
uv run "$REVIEWER" \
  --project-root . \
  --skill <skill-name> \
  --llm-review-json <path-to-llm-review.json> \
  --auto-weight 0.5 \
  --llm-weight 0.5 \
  --output-dir reports/
```

### 第 4 步：可选控制

- 为可重复性固定选择：`--skill <name>` 或 `--seed <int>`
- 一次性评审所有技能：`--all`
- 快速分诊时跳过测试：`--skip-tests`
- 更改报告位置：`--output-dir <dir>`
- 增加 `--auto-weight` 以进行更严格的确定性门控。
- 增加 `--llm-weight` 当定性/代码评审深度优先时。

## 输出

- `reports/skill_review_<skill>_<timestamp>.json`
- `reports/skill_review_<skill>_<timestamp>.md`
- `reports/skill_review_prompt_<skill>_<timestamp>.md`（当 `--emit-llm-prompt` 启用时）

当目标项目具有包含完整 `verification` 块的 `skills-index.yaml` 条目时，JSON
和 Markdown 报告还会显示其声明的轴、`not_verified` 间隙、不适用轴和
`all_applicable_axes_passed`。此部分仅用于信息展示。它不包含在自动/LLM/最终分数中，也不能替代实时高严重性问题检查。

## 全局安装

要从任何项目使用此技能，将其链接到 `~/.claude/skills/`：

```bash
ln -sfn /path/to/claude-trading-skills/skills/dual-axis-skill-reviewer \
  ~/.claude/skills/dual-axis-skill-reviewer
```

之后，Claude Code 将在所有项目中发现该技能，脚本可通过 `~/.claude/skills/dual-axis-skill-reviewer/scripts/run_dual_axis_review.py` 访问。

## 资源

- 自动轴分数元数据、工作流程覆盖率、执行安全性、工件存在性和测试健康状况。
- 自动轴检测 `knowledge_only` 技能并调整脚本/测试预期以避免不公平惩罚。
- LLM 轴分数深入内容质量（正确性、风险、缺失逻辑、可维护性）。
- 最终分数是加权平均值。
- 如果最终分数低于 90，需要改进项并列在 Markdown 报告中。
- 脚本：`skills/dual-axis-skill-reviewer/scripts/run_dual_axis_review.py`
- LLM 模式：`references/llm_review_schema.md`
- 评分标准：`references/scoring_rubric.md`
