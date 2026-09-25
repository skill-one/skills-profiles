# 边缘提示提取器

## 概述

将原始观测信号（`market_summary`、`anomalies`、`news_reactions`）转换为结构化的边缘提示。
这项技能是拆分工作流程的第一阶段：`观察 -> 摘要 -> 设计 -> 管道`。

## 使用场景

- 你希望将日常市场观察转换为可重用的提示对象。
- 你希望LLM生成的想法受当前异常/新闻上下文约束。
- 你需要一个干净的`hints.yaml`输入用于概念合成或自动检测。

## 前置条件

- Python 3.9+
- `PyYAML`
- 检测器运行的可选输入：
  - `market_summary.json`
  - `anomalies.json`
  - `news_reactions.csv` 或 `news_reactions.json`

## 输出

- `hints.yaml`文件，包含：
  - `hints`列表
  - 生成元数据
  - 规则/LLM提示计数

## 工作流程

1. 收集观测文件（`market_summary`、`anomalies`、可选的新闻反应）。
2. 运行`scripts/build_hints.py`生成确定性提示。
3. 可选地通过以下两种方法之一使用LLM想法增强提示：
   - a. `--llm-ideas-cmd` — 将数据传输到外部LLM CLI（子进程）。
   - b. `--llm-ideas-file PATH` — 从YAML文件加载预编写的提示（用于Claude Code工作流，其中Claude自己生成提示）。
4. 将`hints.yaml`传递给概念合成或自动检测。

注意：`--llm-ideas-cmd`和`--llm-ideas-file`是互斥的。

## 快速命令

仅基于规则（默认输出到`reports/edge_hint_extractor/hints.yaml`）：

```bash
python3 skills/edge-hint-extractor/scripts/build_hints.py \
  --market-summary /tmp/edge-auto/market_summary.json \
  --anomalies /tmp/edge-auto/anomalies.json \
  --news-reactions /tmp/news_reactions.csv \
  --as-of 2026-02-20 \
  --output-dir reports/
```

规则 + LLM增强（外部CLI）：

```bash
python3 skills/edge-hint-extractor/scripts/build_hints.py \
  --market-summary /tmp/edge-auto/market_summary.json \
  --anomalies /tmp/edge-auto/anomalies.json \
  --llm-ideas-cmd "python3 /path/to/llm_ideas_cli.py" \
  --output-dir reports/
```

规则 + LLM增强（预写文件，用于Claude Code）：

```bash
python3 skills/edge-hint-extractor/scripts/build_hints.py \
  --market-summary /tmp/edge-auto/market_summary.json \
  --anomalies /tmp/edge-auto/anomalies.json \
  --llm-ideas-file /tmp/llm_hints.yaml \
  --output-dir reports/
```

## 资源

- `skills/edge-hint-extractor/scripts/build_hints.py`
- `references/hints_schema.md`
