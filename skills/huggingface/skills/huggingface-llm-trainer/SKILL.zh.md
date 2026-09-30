---
name: huggingface-llm-trainer
description: 使用TRL（Transformer强化学习）或Unsloth，通过Hugging Face Jobs基础设施来训练或微调语言和视觉模型。涵盖SFT、DPO、GRPO和奖励模型训练方法，并提供GGUF转换以支持本地部署。包含关于TRL Jobs包、遵循PEP 723格式的UV脚本、数据集准备与验证、硬件选择、成本估算、Trackio监控、Hub认证、模型选择/排行榜以及模型持久化的指导。适用于涉及云GPU训练、GGUF转换，或用户提及在Hugging Face Jobs上训练但无本地GPU设置的任务。
---

# 在 Hugging Face Jobs 上进行 TRL 训练

## 概述

使用 TRL（Transformer 强化学习）在完全托管的 Hugging Face 基础设施上训练语言模型。无需本地 GPU 设置——模型在云端 GPU 上训练，结果会自动保存到 Hugging Face Hub。

**TRL 提供多种训练方法：**
- **SFT**（监督微调）- 标准指令微调
- **DPO**（直接偏好优化）- 从偏好数据中实现对齐
- **GRPO**（组相对策略优化）- 在线强化学习训练
- **奖励模型** - 训练用于 RLHF 的奖励模型

**有关 TRL 方法的详细文档：**
```python
hf_doc_search("your query", product="trl")
hf_doc_fetch("https://huggingface.co/docs/trl/sft_trainer")  # SFT
hf_doc_fetch("https://huggingface.co/docs/trl/dpo_trainer")  # DPO
# etc.
```

**另见：** `references/training_methods.md`，其中包含方法概览和选择指南

## 何时使用此技能

当用户希望：
- 在云端 GPU 上微调语言模型，而无需本地基础设施
- 使用 TRL 方法（SFT、DPO、GRPO 等）进行训练
- 在 Hugging Face Jobs 基础设施上运行训练作业
- 将训练好的模型转换为 GGUF 以进行本地部署（Ollama、LM Studio、llama.cpp）
- 确保训练好的模型永久保存到 Hub
- 使用具有优化默认值的现代工作流程

### 何时使用 Unsloth

当使用 **Unsloth** (`references/unsloth.md`) 而不是标准 TRL 时：
- **GPU 内存有限** - Unsloth 使用约 60% 更少的 VRAM
- **速度重要** - Unsloth 快约 2 倍
- 训练 **大型模型（>13B）** - 内存效率至关重要
- 训练 **视觉语言模型（VLMs）** - Unsloth 支持 `FastVisionModel`

参见 `references/unsloth.md` 获取完整的 Unsloth 文档，以及 `scripts/unsloth_sft_example.py` 获取可投入生产的训练脚本。

## 关键指令

在协助训练作业时：

1. **始终使用 `hf_jobs()` MCP 工具** - 使用 `hf_jobs("uv", {...})` 提交作业，而不是 bash `trl-jobs` 命令。`script` 参数接受 Python 代码直接。除非用户明确要求，否则**不要**保存到本地文件。将脚本内容作为字符串传递给 `hf_jobs()`。如果用户要求“训练模型”、“微调”或类似请求，**必须**立即创建训练脚本并使用 `hf_jobs()` 提交作业。

2. **始终包含 Trackio** - 每个训练脚本都应包含 Trackio 以进行实时监控。使用 `scripts/` 中的示例脚本作为模板。

3. **提交作业后提供作业详情** - 提交后，提供作业 ID、监控 URL、预计时间，并说明用户可以稍后请求状态检查。

4. **使用示例脚本作为模板** - 参考 `scripts/train_sft_example.py`、`scripts/train_dpo_example.py` 等作为起点。

## 本地脚本执行

仓库脚本使用 PEP 723 内联依赖项。使用 `uv run` 运行它们：
```bash
uv run scripts/estimate_cost.py --help
uv run scripts/dataset_inspector.py --help
```

## 前提条件检查清单

开始任何训练作业之前，请验证：

### ✅ **账户与认证**
- Hugging Face 账户，具有 [Pro](https://hf.co/pro)、[Team](https://hf.co/enterprise) 或 [Enterprise](https://hf.co/enterprise) 计划（Jobs 需要付费计划）
- 已认证登录：使用 `hf_whoami()` 检查
- **用于 Hub 推送的 HF_TOKEN** ⚠️ 关键 - 训练环境是暂时的，必须推送到 Hub，否则所有训练结果都会丢失
- 令牌必须具有写权限
- **必须在作业配置中传递 `secrets={"HF_TOKEN": "$HF_TOKEN"}`** 以使令牌可用（`$HF_TOKEN` 语法引用您实际的令牌值）

### ✅ **数据集要求**
- 数据集必须存在于 Hub 上或可通过 `datasets.load_dataset()` 加载
- 格式必须与训练方法匹配（SFT：“messages”/文本/提示-完成；DPO：选择/拒绝；GRPO：仅提示）
- **在 GPU 训练之前始终验证未知数据集** 以防止格式失败（见下文数据集验证部分）
- 大小适合硬件（Demo：50-100 个示例在 t4-small 上；生产：1K-10K+ 在 a10g-large/a100-large 上）

### ⚠️ **关键设置**
- **超时必须超过预期训练时间** - 默认 30 分钟对于大多数训练来说太短了。建议最小值：1-2 小时。如果超时超过，作业将失败并丢失所有进度。
- **必须启用 Hub 推送** - 配置：`push_to_hub=True`，`hub_model_id="username/model-name"`；作业：`secrets={"HF_TOKEN": "$HF_TOKEN"}`

## 异步作业指南

**⚠️ 重要提示：** 训练作业是异步运行的，可能需要数小时

### 需要采取的行动

**当用户请求训练时：**
1. **创建训练脚本**，包含 Trackio（使用 `scripts/train_sft_example.py` 作为模板）
2. **立即提交**，使用 `hf_jobs()` MCP 工具，并将脚本内容内联传递——除非用户要求保存到文件
3. **报告提交结果**，包括作业 ID、监控 URL 和预计时间
4. **等待用户** 请求状态检查——不要自动轮询

### 基本规则
- **作业在后台运行** - 提交后立即返回；训练独立继续
- **初始日志延迟** - 可能需要 30-60 秒才能出现日志
- **用户检查状态** - 等待用户请求状态更新
- **避免轮询** - 仅在用户请求时查看日志；提供监控链接

### 提交后

**提供给用户：**
- ✅ 作业 ID 和监控 URL
- ✅ 预计完成时间
- ✅ Trackio 仪表板 URL
- ✅ 注意用户可以稍后请求状态检查

**示例响应：**
```
✅ 作业提交成功！

作业 ID：abc123xyz
监控：https://huggingface.co/jobs/username/abc123xyz

预计时间：约 2 小时
估计成本：约 $10

作业在后台运行。准备好时请问我检查状态/日志！
```

## 快速入门：三种方法

**💡 示范提示：** 对于较小的 GPU（t4-small），为快速演示省略 `eval_dataset` 和 `eval_strategy` 可以节省约 40% 的内存。您仍然会看到训练损失和学习进度。

### 序列长度配置

**TRL 配置类使用 `max_length`（而不是 `max_seq_length`）来控制分词后的序列长度：**

```python
# ✅ 正确 - 如果您需要设置序列长度
SFTConfig(max_length=512)   # 将序列截断为 512 个标记
DPOConfig(max_length=2048)  # 更长的上下文（2048 个标记）

# ❌ 错误 - 此参数不存在
SFTConfig(max_seq_length=512)  # TypeError!
```

**默认行为：** `max_length=1024`（从右侧截断）。这对大多数训练有效。

**何时覆盖：**
- **更长的上下文**：设置更高（例如，`max_length=2048`）
- **内存限制**：设置更低（例如，`max_length=512`）
- **视觉模型**：设置 `max_length=None`（防止切割图像标记）

**通常您不需要设置此参数**——下面的示例使用合理的默认值。

### 方法 1：UV 脚本（推荐——默认选择）

UV 脚本使用 PEP 723 内联依赖项，用于干净、自包含的训练。**这是 Claude Code 的主要方法。**

```python
hf_jobs("uv", {
    "script": """
# /// script
# dependencies = ["trl>=0.12.0", "peft>=0.7.0", "trackio"]
# ///

from datasets import load_dataset
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig
import trackio

dataset = load_dataset("trl-lib/Capybara", split="train")

# 创建用于监控的训练/评估拆分
dataset_split = dataset.train_test_split(test_size=0.1, seed=42)

trainer = SFTTrainer(
    model="Qwen/Qwen2.5-0.5B",
    train_dataset=dataset_split["train"],
    eval_dataset=dataset_split["test"],
    peft_config=LoraConfig(r=16, lora_alpha=32),
    args=SFTConfig(
        output_dir="my-model",
        push_to_hub=True,
        hub_model_id="username/my-model",
        num_train_epochs=3,
        eval_strategy="steps",
        eval_steps=50,
        report_to="trackio",
        project="meaningful_prject_name", # 用于训练名称（trackio）的项目名称
        run_name="meaningful_run_name",   # 描述特定训练运行的描述性名称（trackio）
    )
)

trainer.train()
trainer.push_to_hub()
""",
    "flavor": "a10g-large",
    "timeout": "2h",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"}
})
```

**优点：** 直接使用 MCP 工具，代码干净，内联声明依赖项（PEP 723），无需保存文件，完全控制
**何时使用：** Claude Code 中所有训练任务的默认选择，自定义训练逻辑，任何需要 `hf_jobs()` 的场景

#### 使用脚本

⚠️ **重要提示：** `script` 参数接受内联代码（如上所示）或 URL。**本地文件路径无效。**

**为什么本地路径无效：**
作业在隔离的 Docker 容器中运行，无法访问您的本地文件系统。脚本必须：
- 内联代码（推荐用于自定义训练）
- 公开可访问的 URL
- 私有仓库 URL（使用 HF_TOKEN）

**常见错误：**
```python
# ❌ 所有这些都会失败
hf_jobs("uv", {"script": "train.py"})
hf_jobs("uv", {"script": "./scripts/train.py"})
hf_jobs("uv", {"script": "/path/to/train.py"})
```

**正确方法：**
```python
# ✅ 内联代码（推荐）
hf_jobs("uv", {"script": "# /// script\n# dependencies = [...]\n# ///\n\n<your code>"})

# ✅ 从 Hugging Face Hub
hf_jobs("uv", {"script": "https://huggingface.co/user/repo/resolve/main/train.py"})

# ✅ 从 GitHub
hf_jobs("uv", {"script": "https://raw.githubusercontent.com/user/repo/main/train.py"})

# ✅ 从 Gist
hf_jobs("uv", {"script": "https://gist.githubusercontent.com/user/id/raw/train.py"})
```

**要使用本地脚本：** 首先上传到 HF Hub：
```bash
hf repos create my-training-scripts --type model
hf upload my-training-scripts ./train.py train.py
# 使用：https://huggingface.co/USERNAME/my-training-scripts/resolve/main/train.py
```

### 方法 2：TRL 维护脚本（官方示例）

TRL 提供了经过实战检验的所有方法的脚本。可以从 URL 运行：

```python
hf_jobs("uv", {
    "script": "https://github.com/huggingface/trl/blob/main/trl/scripts/sft.py",
    "script_args": [
        "--model_name_or_path", "Qwen/Qwen2.5-0.5B",
        "--dataset_name", "trl-lib/Capybara",
        "--output_dir", "my-model",
        "--push_to_hub",
        "--hub_model_id", "username/my-model"
    ],
    "flavor": "a10g-large",
    "timeout": "2h",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"}
})
```

**优点：** 无需编写代码，由 TRL 团队维护，经过生产测试
**何时使用：** 标准 TRL 训练，快速实验，不需要自定义代码
**可用：** 脚本可在 https://github.com/huggingface/trl/tree/main/examples/scripts 中找到

### 在 Hub 上查找更多 UV 脚本

`uv-scripts` 组织提供了存储在 Hugging Face Hub 上的即用型 UV 脚本：

```python
# 发现可用的 UV 脚本集合
dataset_search({"author": "uv-scripts", "sort": "downloads", "limit": 20})

# 探索特定集合
hub_repo_details(["uv-scripts/classification"], repo_type="dataset", include_readme=True)
```

**热门集合：** ocr、classification、synthetic-data、vllm、dataset-creation

### 方法 3：HF Jobs CLI（直接终端命令）

当 `hf_jobs()` MCP 工具不可用时，直接使用 `hf jobs` CLI。

**⚠️ 关键：CLI 语法规则**

```bash
# ✅ 正确语法 - 标志在脚本 URL 之前
hf jobs uv run --flavor a10g-large --timeout 2h --secrets HF_TOKEN "https://example.com/train.py"

# ❌ 错误 - "run uv" 而不是 "uv run"
hf jobs run uv "https://example.com/train.py" --flavor a10g-large

# ❌ 错误 - 标志在脚本 URL 之后（将被忽略！）
hf jobs uv run "https://example.com/train.py" --flavor a10g-large

# ❌ 错误 - "--secret" 而不是 "--secrets"（复数）
hf jobs uv run --secret HF_TOKEN "https://example.com/train.py"
```

**关键语法规则：**
1. 命令顺序是 `hf jobs uv run`（不是 `hf jobs run uv`）
2. 所有标志（`--flavor`、`--timeout`、`--secrets`）必须位于脚本 URL 之前
3. 使用 `--secrets`（复数），而不是 `--secret`
4. 脚本 URL 必须是最后一个位置参数

**完整 CLI 示例：**
```bash
hf jobs uv run \
  --flavor a10g-large \
  --timeout 2h \
  --secrets HF_TOKEN \
  "https://huggingface.co/user/repo/resolve/main/train.py"
```

**通过 CLI 检查作业状态：**
```bash
hf jobs ps                        # 列出所有作业
hf jobs logs <job-id>             # 查看日志
hf jobs inspect <job-id>          # 作业详情
hf jobs cancel <job-id>           # 取消作业
```

### 方法 4：TRL Jobs 包（简化训练）

`trl-jobs` 包提供优化的默认值和一行式训练。

```bash
uvx trl-jobs sft \
  --model_name Qwen/Qwen2.5-0.5B \
  --dataset_name trl-lib/Capybara
```

**优点：** 预配置设置，自动 Trackio 集成，自动 Hub 推送，一行式命令
**何时使用：** 直接在终端工作的用户（不是 Claude Code 环境），快速本地实验
**仓库：** https://github.com/huggingface/trl-jobs

⚠️ **在 Claude Code 环境中，当可用时，请优先使用 `hf_jobs()` MCP 工具（方法 1）。**

## 硬件选择

| 模型大小 | 推荐硬件 | 成本（约/小时） | 用例 |
|----------|----------|----------------|------|
| <1B 参数 | `t4-small` | ~$0.75 | 示范、仅用于快速测试，无需评估步骤 |
| 1-3B 参数 | `t4-medium`、`l4x1` | ~$1.50-2.50 | 开发 |
| 3-7B 参数 | `a10g-small`、`a10g-large` | ~$3.50-5.00 | 生产训练 |
| 7-13B 参数 | `a10g-large`、`a100-large` | ~$5-10 | 大型模型（使用 LoRA） |
| 13B+ 参数 | `a100-large`、`a10g-largex2` | ~$10-20 | 非常大型（使用 LoRA） |

**GPU 品种：** cpu-basic/upgrade/performance/xl、t4-small/medium、l4x1/x4、a10g-small/large/largex2/largex4、a100-large、h100/h100x8

**指南：**
- 使用 **LoRA/PEFT** 训练 >7B 的模型以减少内存
- 多 GPU 自动由 TRL/Accelerate 管理
- 使用较小硬件进行测试

**参见：** `references/hardware_guide.md` 获取详细规格

## 关键：保存结果到 Hub

**⚠️ 暂时的环境——必须推送到 Hub**

作业环境是临时的。所有文件在作业结束时都会被删除。如果模型没有推送到 Hub，**所有训练结果都会丢失**。

### 必要配置

**在训练脚本/配置中：**
```python
SFTConfig(
    push_to_hub=True,
    hub_model_id="username/model-name",  # 必须指定
    hub_strategy="every_save",  # 可选：推送检查点
)
```

**在作业提交中：**
```python
{
    "secrets": {"HF_TOKEN": "$HF_TOKEN"}  # 启用认证
}
```

### 验证检查清单

提交之前：
- [ ] `push_to_hub=True` 在配置中设置
- [ ] `hub_model_id` 包含用户名/仓库名
- [ ] `secrets` 参数包含 HF_TOKEN
- [ ] 用户具有目标仓库的写权限

**参见：** `references/hub_saving.md` 获取详细故障排除信息

## 超时管理

**⚠️ 默认：30 分钟——对于训练来说太短了**

### 设置超时

```python
{
    "timeout": "2h"   # 2 小时（格式：“90m”、“2h”、“1.5h”，或作为整数的秒数）
}
```

### 超时指南

| 场景 | 推荐值 | 备注 |
|------|--------|------|
| 快速演示（50-100 个示例） | 10-30 分钟 | 验证设置 |
| 开发训练 | 1-2 小时 | 小数据集 |
| 生产（3-7B 模型） | 4-6 小时 | 全数据集 |
| 大型模型与 LoRA | 3-6 小时 | 取决于数据集 |

**始终添加 20-30% 的缓冲**，以应对模型/数据集加载、检查点保存、Hub 推送操作和网络延迟。

**超时时：** 作业立即被终止，所有未保存的进度都会丢失，必须从头开始

## 选择基础模型（模型选择）

**根据任务类型或基准结果识别要训练的模型。**

使用 `scripts/hf_benchmarks.py` 识别特定任务的顶级性能模型。这有助于用户选择一个模型作为训练的基础，同时考虑大小和硬件限制。

```bash
# 获取基准命令的帮助：
uv run scripts/hf_benchmarks.py --help
```

### 示例 -- 选择OCR基础模型
```bash
# 搜索包含名称中包含文本 `ocr` 的基准测试
uv run scripts/hf_benchmarks.py search --query ocr

# 获取 allenai/olmOCR-bench 基准测试的排名排行榜
uv run scripts/hf_benchmarks.py leaderboard allenai/olmOCR-bench
```

## 成本估算

**在规划具有已知参数的工作时提供成本估算。** 使用 `scripts/estimate_cost.py`：

```bash
uv run scripts/estimate_cost.py \
  --model meta-llama/Llama-2-7b-hf \
  --dataset trl-lib/Capybara \
  --hardware a10g-large \
  --dataset-size 16000 \
  --epochs 3
```

输出包括预估时间、成本、建议的超时（带缓冲）和优化建议。

**何时提供：** 用户规划工作，询问成本/时间，选择硬件，工作将运行 >1 小时或成本 >$5

## 示例训练脚本

**包含所有最佳实践的生产就绪模板：**

加载这些脚本以正确地：

- **`scripts/train_sft_example.py`** - 使用 Trackio、LoRA、检查点的完整 SFT 训练
- **`scripts/train_dpo_example.py`** - 用于偏好学习的 DPO 训练
- **`scripts/train_grpo_example.py`** - 用于在线 RL 的 GRPO 训练

这些脚本展示了正确的 Hub 保存、Trackio 集成、检查点管理和优化参数。将它们的内容内联传递给 `hf_jobs()` 或用作自定义脚本的模板。

## 监控和跟踪

**Trackio** 提供实时指标可视化。查看 `references/trackio_guide.md` 获取完整的设置指南。

**要点：**
- 将 `trackio` 添加到依赖项
- 使用 `report_to="trackio" and run_name="meaningful_name"` 配置训练器

### Trackio 配置默认值

**除非用户指定否则使用合理的默认值。** 在使用 Trackio 生成训练脚本时：

**默认配置：**
- **空间 ID**： `{username}/trackio`（使用 "trackio" 作为默认空间名称）
- **运行命名**：除非另有指定，否则以用户能识别的方式命名运行（例如，描述任务、模型或目的）
- **配置**：保持最小化 - 仅包含超参数和模型/数据集信息
- **项目名称**：使用项目名称将运行与特定项目关联

**用户覆盖：** 如果用户请求特定的 trackio 配置（自定义空间、运行命名、分组或附加配置），请应用他们的偏好而不是默认值。

这对于管理具有相同配置的多个工作或保持训练脚本可移植性很有用。

查看 `references/trackio_guide.md` 获取包括为实验分组运行的完整文档。

### 检查工作状态

```python
# 列出所有工作
hf_jobs("ps")

# 检查特定工作
hf_jobs("inspect", {"job_id": "your-job-id"})

# 查看日志
hf_jobs("logs", {"job_id": "your-job-id"})
```

**记住：** 等待用户请求状态检查。避免重复轮询。

## 数据集验证

**在启动 GPU 训练之前验证数据集格式，以防止培训失败的首要原因：格式不匹配。**

### 为什么验证

- 50%+ 的培训失败是由于数据集格式问题
- DPO 特别严格：要求确切的列名（`prompt`、`chosen`、`rejected`）
- 失败的 GPU 工作浪费 $1-10 和 30-60 分钟
- CPU 上的验证成本约为 $0.01，耗时 <1 分钟

### 何时验证

**始终验证：**
- 未知或自定义数据集
- DPO 训练（关键 - 90% 的数据集需要映射）
- 任何未明确 TRL 兼容的数据集

**跳过验证已知 TRL 数据集：**
- `trl-lib/ultrachat_200k`、`trl-lib/Capybara`、`HuggingFaceH4/ultrachat_200k` 等

### 使用方法

```python
hf_jobs("uv", {
    "script": "https://huggingface.co/datasets/mcp-tools/skills/raw/main/dataset_inspector.py",
    "script_args": ["--dataset", "username/dataset-name", "--split", "train"]
})
```

该脚本速度很快，通常将同步完成。

### 阅读结果

输出显示每个训练方法的兼容性：

- **`✓ READY`** - 数据集兼容，可直接使用
- **`✗ NEEDS MAPPING`** - 兼容但需要预处理（提供映射代码）
- **`✗ INCOMPATIBLE`** - 不能用于此方法

当需要映射时，输出包括一个 **"MAPPING CODE"** 部分和可复制粘贴的 Python 代码。

### 示例工作流程

```python
# 1. 检查数据集（成本 ~$0.01，CPU 上 <1 分钟）
hf_jobs("uv", {
    "script": "https://huggingface.co/datasets/mcp-tools/skills/raw/main/dataset_inspector.py",
    "script_args": ["--dataset", "argilla/distilabel-math-preference-dpo", "--split", "train"]
})

# 2. 检查输出标记：
#    ✓ READY → 继续培训
#    ✗ NEEDS MAPPING → 应用下方映射代码
#    ✗ INCOMPATIBLE → 选择不同的方法/数据集

# 3. 如果需要映射，培训前应用：
def format_for_dpo(example):
    return {
        'prompt': example['instruction'],
        'chosen': example['chosen_response'],
        'rejected': example['rejected_response'],
    }
dataset = dataset.map(format_for_dpo, remove_columns=dataset.column_names)

# 4. 带着信心启动培训工作
```

### 常见场景：DPO 格式不匹配

大多数 DPO 数据集使用非标准列名。示例：

```
数据集有：instruction、chosen_response、rejected_response
DPO 需要：prompt、chosen、rejected
```

验证器检测到此问题并提供精确的映射代码来修复它。

## 将模型转换为 GGUF

培训后，将模型转换为 **GGUF 格式** 以用于 llama.cpp、Ollama、LM Studio 和其他本地推理工具。

**什么是 GGUF：**
- 专为 llama.cpp 的 CPU/GPU 推理优化
- 支持量化（4 位、5 位、8 位）以减小模型大小
- 兼容 Ollama、LM Studio、Jan、GPT4All、llama.cpp
- 7B 模型通常为 2-8GB（未量化为 14GB）

**何时转换：**
- 使用 Ollama 或 LM Studio 本地运行模型
- 使用量化减小模型大小
- 部署到边缘设备
- 分享模型用于本地优先使用

**查看：** `references/gguf_conversion.md` 获取完整的转换指南，包括生产就绪的转换脚本、量化选项、硬件要求、使用示例和故障排除。

**快速转换：**
```python
hf_jobs("uv", {
    "script": "<see references/gguf_conversion.md for complete script>",
    "flavor": "a10g-large",
    "timeout": "45m",
    "secrets": {"HF_TOKEN": "$HF_TOKEN"},
    "env": {
        "ADAPTER_MODEL": "username/my-finetuned-model",
        "BASE_MODEL": "Qwen/Qwen2.5-0.5B",
        "OUTPUT_REPO": "username/my-model-gguf"
    }
})
```

## 常见培训模式

查看 `references/training_patterns.md` 获取详细示例，包括：
- 快速演示（5-10 分钟）
- 带检查点的生产
- 多 GPU 训练
- DPO 训练（偏好学习）
- GRPO 训练（在线 RL）

## 常见失败模式

### 内存不足 (OOM)

**修复（按顺序尝试）：**
1. 减小批处理大小：`per_device_train_batch_size=1`，增加 `gradient_accumulation_steps=8`。有效批处理大小是 `per_device_train_batch_size` x `gradient_accumulation_steps`。为最佳性能，保持有效批处理大小接近 128。
2. 启用：`gradient_checkpointing=True`
3. 升级硬件：t4-small → l4x1，a10g-small → a10g-large 等。

### 数据集格式错误

**修复：**
1. 首先使用数据集检查器验证：
   ```bash
   uv run https://huggingface.co/datasets/mcp-tools/skills/raw/main/dataset_inspector.py \
     --dataset name --split train
   ```
2. 检查输出兼容性标记（✓ READY、✗ NEEDS MAPPING、✗ INCOMPATIBLE）
3. 如有必要，应用检查器输出中的映射代码

### 工作超时

**修复：**
1. 检查日志以获取实际运行时间：`hf_jobs("logs", {"job_id": "..."})`
2. 增加带缓冲的超时：`"timeout": "3h"`（增加预估时间的 30%）
3. 或者减少培训：降低 `num_train_epochs`，使用较小的数据集，启用 `max_steps`
4. 保存检查点：`save_strategy="steps"`，`save_steps=500`，`hub_strategy="every_save"`

**注意：** 默认 30 分钟不足以进行实际培训。最小 1-2 小时。

### Hub 推送失败

**修复：**
1. 添加到工作：`secrets={"HF_TOKEN": "$HF_TOKEN"}`
2. 添加到配置：`push_to_hub=True`，`hub_model_id="username/model-name"`
3. 验证认证：`mcp__huggingface__hf_whoami()`
4. 检查令牌具有写权限且存储库存在（或设置 `hub_private_repo=True`）

### 缺少依赖项

**修复：**
添加到 PEP 723 标头：
```python
# /// script
# dependencies = ["trl>=0.12.0", "peft>=0.7.0", "trackio", "missing-package"]
# ///
```

## 故障排除

**常见问题：**
- 工作超时 → 增加超时，减少 epoch/数据集，使用较小模型/LoRA
- 模型未保存到 Hub → 检查 `push_to_hub=True`、`hub_model_id`、`secrets=HF_TOKEN`
- 内存不足 (OOM) → 减小批处理大小，增加梯度累积，启用 LoRA，使用较大 GPU
- 数据集格式错误 → 使用数据集检查器验证（见数据集验证部分）
- 导入/模块错误 → 添加 PEP 723 标头包含依赖项，验证格式
- 认证错误 → 检查 `mcp__huggingface__hf_whoami()`、令牌权限、secrets 参数

**查看：** `references/troubleshooting.md` 获取完整的故障排除指南

## 资源

### 参考（在此技能中）
- `references/training_methods.md` - SFT、DPO、GRPO、KTO、PPO、奖励建模概述
- `references/training_patterns.md` - 常见培训模式和示例
- `references/unsloth.md` - Unsloth 用于快速 VLM 训练（速度提升 ~2x，VRAM 减少 60%）
- `references/gguf_conversion.md` - 完整 GGUF 转换指南
- `references/trackio_guide.md` - Trackio 监控设置
- `references/hardware_guide.md` - 硬件规格和选择
- `references/hub_saving.md` - Hub 认证故障排除
- `references/troubleshooting.md` - 常见问题和解决方案
- `references/local_training_macos.md` - macOS 上的本地培训

### 脚本（在此技能中）
- `scripts/train_sft_example.py` - 生产 SFT 模板
- `scripts/train_dpo_example.py` - 生产 DPO 模板
- `scripts/train_grpo_example.py` - 生产 GRPO 模板
- `scripts/unsloth_sft_example.py` - Unsloth 文本 LLM 训练模板（更快，VRAM 更少）
- `scripts/estimate_cost.py` - 估算时间和成本（在适当时候提供）
- `scripts/convert_to_gguf.py` - 完整 GGUF 转换脚本
- `scripts/hf_benchmarks.py` - 按任务、别名或自由文本搜索基准测试结果和排行榜

### 外部脚本
- [数据集检查器](https://huggingface.co/datasets/mcp-tools/skills/raw/main/dataset_inspector.py) - 在培训前验证数据集格式（通过 `uv run` 或 `hf_jobs` 使用）

### 外部链接
- [TRL 文档](https://huggingface.co/docs/trl)
- [TRL 工作培训指南](https://huggingface.co/docs/trl/en/jobs_training)
- [TRL 工作软件包](https://github.com/huggingface/trl-jobs)
- [HF 工作文档](https://huggingface.co/docs/huggingface_hub/guides/jobs)
- [TRL 示例脚本](https://github.com/huggingface/trl/tree/main/examples/scripts)
- [UV 脚本指南](https://docs.astral.sh/uv/guides/scripts/)
- [UV 脚本组织](https://huggingface.co/uv-scripts)

## 关键要点

1. **内联提交脚本** - `script` 参数接受 Python 代码直接；无需保存文件除非用户请求
2. **工作是异步的** - 不要等待/轮询；让用户准备好时检查
3. **始终设置超时** - 默认 30 分钟不足够；建议最小 1-2 小时
4. **始终启用 Hub 推送** - 环境是短暂的；不推送，所有结果将丢失
5. **包含 Trackio** - 使用示例脚本作为实时监控的模板
6. **提供成本估算** - 当参数已知时，使用 `scripts/estimate_cost.py`
7. **使用 UV 脚本（方法 1）** - 默认使用 `hf_jobs("uv", {...})` 与内联脚本；TRL 维护的脚本用于标准培训；避免在 Claude Code 中使用 bash `trl-jobs` 命令
8. **使用 hf_doc_fetch/hf_doc_search 获取最新 TRL 文档**
9. **在培训前验证数据集格式** 使用数据集检查器（见数据集验证部分）
10. **选择合适的硬件** 用于模型大小；对于 >7B 的模型使用 LoRA
