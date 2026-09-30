---
name: run
description: 一个一次性生命周期命令，在一个调用中串联 init → baseline → spawn → eval → merge。当用户运行 /hub:run 或要求执行完整的 AgentHub 竞赛端到端时使用。
---

# /hub:run — 单次生命周期

使用一条命令运行完整的 AgentHub 生命周期：初始化、捕获基线、生成代理、评估结果并合并胜者。

## 使用方法

```
/hub:run --task "减少 p50 延迟" --agents 3 \
  --eval "pytest bench.py --json" --metric p50_ms --direction lower \
  --template optimizer

/hub:run --task "重构认证模块" --agents 2 --template refactorer

/hub:run --task "覆盖未测试的工具" --agents 3 \
  --eval "pytest --cov=utils --cov-report=json" --metric coverage_pct --direction higher \
  --template test-writer

/hub:run --task "为春季促销活动撰写 3 个电子邮件主题行" --agents 3 --judge
```

## 参数

| 参数 | 必填 | 描述 |
|-------|------|------|
| `--task` | 是 | 代理的任务描述 |
| `--agents` | 否 | 并行代理的数量（默认：3） |
| `--eval` | 否 | 用于测量结果的评估命令（在 LLM 判定模式下可跳过） |
| `--metric` | 否 | 从评估输出中提取的指标名称（如果提供 `--eval` 则必需） |
| `--direction` | 否 | `lower` 或 `higher` — 哪个方向更好（如果提供 `--metric` 则必需） |
| `--template` | 否 | 代理模板：`optimizer`、`refactorer`、`test-writer`、`bug-fixer` |

## 功能说明

按顺序执行以下步骤：

### 第 1 步：初始化

使用提供的参数运行 `/hub:hub-init`：

```bash
python {skill_path}/scripts/hub_init.py \
  --task "{task}" --agents {N} \
  [--eval "{eval_cmd}"] [--metric {metric}] [--direction {direction}]
```

向用户显示会话 ID。

### 第 2 步：捕获基线

如果提供了 `--eval`：

1. 在当前工作目录中运行评估命令
2. 从标准输出中提取指标值
3. 显示：`基线捕获：{metric} = {value}`
4. 将 `baseline: {value}` 添加到 `.agenthub/sessions/{session-id}/config.yaml`

如果没有提供 `--eval`，则跳过此步骤。

### 第 3 步：生成代理

使用会话 ID 运行 `/hub:spawn`。

如果提供了 `--template`，则使用 `../agenthub/references/agent-templates.md` 中的模板调度提示，而不是默认的调度提示。将评估命令、指标和基线传递给模板变量。

使用多个 Agent 工具调用（真正的并行性）在单个消息中启动所有代理。

### 第 4 步：等待和监控

生成代理后，通知用户代理正在运行。当所有代理完成（Agent 工具返回结果）时：

1. 显示每个代理工作的简要摘要
2. 继续评估

### 第 5 步：评估

使用会话 ID 运行 `/hub:eval`：

- 如果提供了 `--eval`：使用 `result_ranker.py` 进行基于指标的排名
- 如果没有 `--eval`：LLM 判定模式（协调员读取差异并排名）

如果捕获了基线，将 `--baseline {value}` 传递给 `result_ranker.py` 以显示增量。

显示排名结果表。

### 第 6 步：确认和合并

向用户展示结果并请求确认：

```
Agent-2 是胜者（128ms，比基线高 52ms）。
合并 agent-2 的分支？ [Y/n]
```

如果确认，运行 `/hub:merge`。如果拒绝，通知用户他们可以：

- `/hub:merge --agent agent-{N}` 来选择不同的胜者
- `/hub:eval --judge` 重新使用 LLM 判定进行评估
- 手动检查分支

## 关键规则

- **顺序执行** — 每个步骤都依赖于前一个步骤
- **失败即停止** — 如果任何步骤失败，报告错误并停止
- **用户确认合并** — 不要在不询问的情况下自动合并
- **模板是可选的** — 没有 `--template`，代理使用 `/hub:spawn` 的默认调度提示
