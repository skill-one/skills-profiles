# 概述

此技能用于在本地硬件上对 Hugging Face Hub 上的模型进行评估。

它涵盖：
- 使用本地推理的 `inspect-ai`
- 使用本地推理的 `lighteval`
- 在 `vllm`、Hugging Face Transformers 和 `accelerate` 之间进行选择
- 烟雾测试、任务选择和后端回退策略

它**不包括**：
- Hugging Face Jobs 协调
- 模型卡或 `model-index` 编辑
- README 表格提取
- 人工分析导入
- `.eval_results` 生成或发布
- PR 创建或社区评估自动化

如果用户希望在 Hugging Face Jobs 上**远程运行相同的评估**，请将 `hugging-face-jobs` 技能传递给它，并传递此技能中的一个本地脚本。

如果用户希望将结果**发布到社区评估工作流**中，请在生成评估运行后停止，并将发布步骤交给 `~/code/community-evals`。

> 以下所有路径相对于包含此 `SKILL.md` 的目录。

# 何时使用哪个脚本

| 使用场景 | 脚本 |
|---|---|
| 通过推理提供程序在 Hub 模型上本地 `inspect-ai` 评估 | `scripts/inspect_eval_uv.py` |
| 使用 `vllm` 或 Transformers 在本地 GPU 上使用 `inspect-ai` 进行评估 | `scripts/inspect_vllm_uv.py` |
| 使用 `vllm` 或 `accelerate` 在本地 GPU 上使用 `lighteval` 进行评估 | `scripts/lighteval_vllm_uv.py` |
| 额外命令模式 | `examples/USAGE_EXAMPLES.md` |

# 前提条件

- 建议使用 `uv run` 进行本地执行。
- 为受限制的私有模型设置 `HF_TOKEN`。
- 对于本地 GPU 运行，在开始之前验证 GPU 访问权限：

```bash
uv --version
printenv HF_TOKEN >/dev/null
nvidia-smi
```

如果 `nvidia-smi` 不可用，则：
- 使用 `scripts/inspect_eval_uv.py` 进行较轻的提供程序支持的评估，或者
- 如果用户需要远程计算，则将任务交给 `hugging-face-jobs` 技能。

# 核心工作流程

1. 选择评估框架。
   - 当您需要显式任务控制和 inspect-native 流程时，使用 `inspect-ai`。
   - 当基准测试自然表示为 lighteval 任务字符串时，使用 `lighteval`，尤其是排行榜风格的任务。
2. 选择推理后端。
   - 对于支持架构的吞吐量，优先选择 `vllm`。
   - 作为兼容性回退，使用 Hugging Face Transformers (`--backend hf`) 或 `accelerate`。
3. 先进行烟雾测试。
   - `inspect-ai`：添加 `--limit 10` 或类似选项。
   - `lighteval`：添加 `--max-samples 10`。
4. 只有烟雾测试通过后才能扩展。
5. 如果用户需要远程执行，请将任务交给 `hugging-face-jobs` 并使用相同的脚本 + 参数。

# 快速入门

## 选项 A：使用本地推理提供程序路径的 inspect-ai

当模型已经由 Hugging Face 推理提供程序支持，并且您希望最低本地设置开销时，最佳选择。

```bash
uv run scripts/inspect_eval_uv.py \
  --model meta-llama/Llama-3.2-1B \
  --task mmlu \
  --limit 20
```

使用此路径时：
- 您希望进行快速的本地烟雾测试
- 您不需要直接 GPU 控制
- 任务已经在 `inspect-evals` 中存在

## 选项 B：本地 GPU 上的 inspect-ai

当您需要直接加载 Hub 模型、使用 `vllm` 或回退到 Transformers 以支持不支持的架构时，最佳选择。

本地 GPU：

```bash
uv run scripts/inspect_vllm_uv.py \
  --model meta-llama/Llama-3.2-1B \
  --task gsm8k \
  --limit 20
```

Transformers 回退：

```bash
uv run scripts/inspect_vllm_uv.py \
  --model microsoft/phi-2 \
  --task mmlu \
  --backend hf \
  --trust-remote-code \
  --limit 20
```

## 选项 C：本地 GPU 上的 lighteval

当任务自然表示为 `lighteval` 任务字符串时，最佳选择，尤其是 Open LLM 排行榜风格的基准测试。

本地 GPU：

```bash
uv run scripts/lighteval_vllm_uv.py \
  --model meta-llama/Llama-3.2-3B-Instruct \
  --tasks "leaderboard|mmlu|5,leaderboard|gsm8k|5" \
  --max-samples 20 \
  --use-chat-template
```

`accelerate` 回退：

```bash
uv run scripts/lighteval_vllm_uv.py \
  --model microsoft/phi-2 \
  --tasks "leaderboard|mmlu|5" \
  --backend accelerate \
  --trust-remote-code \
  --max-samples 20
```

# 远程执行边界

此技能有意在**本地执行和后端选择**处停止。

如果用户希望：
- 在 Hugging Face Jobs 上运行这些脚本
- 选择远程硬件
- 将密钥传递给远程作业
- 安排定期运行
- 查看/取消/监控作业

那么请切换到 **`hugging-face-jobs`** 技能，并将其传递给这些脚本中的一个加上所选参数。

# 任务选择

`inspect-ai` 示例：
- `mmlu`
- `gsm8k`
- `hellaswag`
- `arc_challenge`
- `truthfulqa`
- `winogrande`
- `humaneval`

`lighteval` 任务字符串使用 `suite|task|num_fewshot`：
- `leaderboard|mmlu|5`
- `leaderboard|gsm8k|5`
- `leaderboard|arc_challenge|25`
- `lighteval|hellaswag|0`

多个 `lighteval` 任务可以逗号分隔在 `--tasks` 中。

# 后端选择

- 优先选择 `inspect_vllm_uv.py --backend vllm` 以在支持架构的 GPU 推理上实现快速推理。
- 当 `vllm` 不支持模型时，使用 `inspect_vllm_uv.py --backend hf`。
- 优先选择 `lighteval_vllm_uv.py --backend vllm` 以在支持模型上的吞吐量。
- 使用 `lighteval_vllm_uv.py --backend accelerate` 作为兼容性回退。
- 当推理提供程序已经覆盖模型且您不需要直接 GPU 控制时，使用 `inspect_eval_uv.py`。

# 硬件建议

| 模型大小 | 建议的本地硬件 |
|---|---|
| `< 3B` | 消费级 GPU / Apple Silicon / 小型开发 GPU |
| `3B - 13B` | 更强的本地 GPU |
| `13B+` | 高内存本地 GPU 或将任务交给 `hugging-face-jobs` |

对于烟雾测试，优先选择更便宜的本地运行加上 `--limit` 或 `--max-samples`。

# 故障排除

- CUDA 或 vLLM 内存不足：
  - 减少 `--batch-size`
  - 减少 `--gpu-memory-utilization`
  - 为烟雾测试切换到较小的模型
  - 如有必要，将任务交给 `hugging-face-jobs`
- `vllm` 不支持模型：
  - 对于 `inspect-ai` 切换到 `--backend hf`
  - 对于 `lighteval` 切换到 `--backend accelerate`
- 受限制的私有仓库访问失败：
  - 验证 `HF_TOKEN`
- 需要自定义模型代码：
  - 添加 `--trust-remote-code`

# 示例

参见：
- `examples/USAGE_EXAMPLES.md` 以获取本地命令模式
- `scripts/inspect_eval_uv.py`
- `scripts/inspect_vllm_uv.py`
- `scripts/lighteval_vllm_uv.py`
