# TRL 在 Hugging Face Jobs 上的训练

## 概述

使用 TRL（Transformer 强化学习）在完全托管的 Hugging Face 基础设施上训练语言模型。无需本地 GPU 配置——模型在云端 GPU 上训练，结果自动保存到 Hugging Face Hub。

**TRL 提供多种训练方法：**
- **SFT**（监督微调）- 标准指令调优
- **DPO**（直接偏好优化）- 基于偏好数据的对齐
- **GRPO**（组相对策略优化）- 在线强化学习训练
- **奖励建模** - 训练用于 RLHF 的奖励模型

**TRL 方法的详细文档：**
```python
hf_doc_search("your query", product="trl")
hf_doc_fetch("https://huggingface.co/docs/trl/sft_trainer")  # SFT
hf_doc_fetch("https://huggingface.co/docs/trl/dpo_trainer")  # DPO
# 等等
```

**另请参阅：** `references/training_methods.md` 了解方法概览和选择指南

## 何时使用此技能

当用户希望执行以下操作时，使用此技能：
- 在云端 GPU 上微调语言模型而无需本地基础设施
- 使用 TRL 方法（SFT、DPO、GRPO 等）进行训练
- 在 Hugging Face Jobs 基础设施上运行训练任务
- 将训练好的模型转换为 GGUF 格式以便本地部署（Ollama、LM Studio、llama.cpp）
- 确保训练好的模型永久保存到 Hub
- 使用优化的默认设置实现现代化工作流

### 何时使用 Unsloth

在以下情况下，使用 **Unsloth**（`references/unsloth.md`）替代标准 TRL：
- **GPU 内存有限** - Unsloth 可使用约 60% 更少的 VRAM
- **速度优先** - Unsloth 速度快约 2 倍
- 训练**大模型（>13B）** - 内存效率至关重要
- 训练**视觉语言模型（VLM）** - Unsloth 支持 `FastVisionModel`

完整 Unsloth 文档请参阅 `references/unsloth.md`，生产就绪的训练脚本请参阅 `scripts/unsloth_sft_example.py`。

## 关键指令

在协助训练任务时：

1. **始终使用 `hf_jobs()` MCP 工具** - 使用 `hf_jobs("uv", {...})` 提交任务，而非 bash `trl-jobs` 命令。`script` 参数直接接受 Python 代码。除非用户明确要求，否则不要保存到本地文件。将脚本内容作为字符串传递给 `hf_jobs()`。如果用户要求"训练模型"、"微调"或类似请求，必须立即创建训练脚本并使用 `hf_jobs()` 提交任务。

2. **始终包含 Trackio** - 每个训练脚本都应包含 Trackio 以进行实时监控。使用 `scripts/` 中的示例脚本作为模板。

3. **提交后提供任务详情** - 提交后，提供任务 ID、监控 URL、预计时间，并注明用户之后可以请求状态检查。

4. **使用示例脚本作为模板** - 参考 `scripts/train_sft_example.py`、`scripts/train_dpo_example.py` 等作为起点。

## 本地脚本执行

仓库脚本使用 PEP 723 内联依赖。使用 `uv run` 运行：
```bash
uv run scripts/estimate_cost.py --help
uv run scripts/dataset_inspector.py --help
```

## 前置条件清单

在启动任何训练任务之前，请确认：

### ✅ **账户与认证**
- 具有 [Pro](https://hf.co/pro)、[Team](https://hf.co/enterprise) 或 [Enterprise](https://hf.co/enterprise) 套餐的 Hugging Face 账户（Jobs 需要付费套餐）
- 已认证登录：使用 `hf_whoami()` 检查
- **HF_TOKEN 用于 Hub 推送** ⚠️ 关键 - 训练环境是临时的，必须推送到 Hub，否则所有训练结果都会丢失
- Token 必须具有写入权限
- **必须在任务配置中传递 `secrets={"HF_TOKEN": "$HF_TOKEN"}`** 以使 token 可用（`$HF_TOKEN` 语法引用你的实际 token 值）

### ✅ **数据集要求**
- 数据集必须存在于 Hub 或可通过 `datasets.load_dataset()` 加载
- 格式必须与训练方法匹配（SFT："messages"/文本/提示-完成；DPO：chosen/rejected；GRPO：仅提示）
- **始终验证未知数据集** 再进行 GPU 训练，以防止格式失败（见下文数据集验证部分）
- 大小适合硬件（演示：t4-small 上 50-100 个示例；生产：a10g-large/a100-large 上 1K-10K+）

### ⚠️ **关键设置**
- **超时时间必须超过预期训练时间** - 默认 30 分钟对大多数训练来说太短。最低建议：1-2 小时。如果超过超时时间，任务将失败并丢失所有进度。
- **必须启用 Hub 推送** - 配置：`push_to_hub=True`，`hub_model_id="username/model-name"`；任务：`secrets={"HF_TOKEN": "$HF_TOKEN"}`

## 异步任务指南

**⚠️ 重要：训练任务异步运行，可能需要数小时**

### 所需操作

**当用户请求训练时：**
1. **创建训练脚本**，包含 Trackio（使用 `scripts/train_sft_example.py` 作为模板）
2. **立即提交**，使用 `hf_jobs()` MCP 工具，脚本内容内联传入 - 除非用户要求，否则不保存到文件
3. **报告提交**，包含任务 ID、监控 URL 和预计时间
4. **等待用户** 请求状态检查 - 不要自动轮询

### 基本规则
- **任务在后台运行** - 提交后立即返回；训练独立继续
- **初始日志有延迟** - 日志可能需要 30-60 秒才显示
- **用户检查状态** - 等待用户请求状态更新
- **避免轮询** - 仅在用户请求时检查日志；提供监控链接代替

### 提交后

**向用户提供：**
- ✅ 任务 ID 和监控 URL
- ✅ 预计完成时间
- ✅ Trackio 仪表板 URL
- ✅ 注明用户之后可以请求状态检查

**示例回复：**
```
✅ 任务提交成功！

任务 ID: abc123xyz
监控: https://huggingface.co/jobs/username/abc123xyz

预计时间: 约 2 小时
预估费用: 约 $10

任务正在后台运行。准备好后随时让我检查状态/日志！
```

## 快速开始：三种方法

**💡 演示提示：** 对于小 GPU（t4-small）上的快速演示，省略 `eval_dataset` 和 `eval_strategy` 可节省约 40% 内存。你仍然可以看到训练损失和学习进度。

### 序列长度配置

**TRL 配置类使用 `max_length`（而非 `max_seq_length`）** 来控制分词后的序列长度：

```python
# ✅ 正确 - 如果需要设置序列长度
SFTConfig(max_length=512)   # 将序列截断为 512 个 token
DPOConfig(max_length=2048)  # 更长的上下文（2048 个 token）

# ❌ 错误 - 此参数不存在
SFTConfig(max_seq_length=512)  # TypeError!
```

**默认行为：** `max_length=1024`（从右侧截断）。这对大多数训练效果很好。

**何时覆盖：**
- **更长上下文**：设置更高值（例如 `max_length=2048`）
- **内存受限**：设置更低值（例如 `max_length=512`）
- **视觉模型**：设置 `max_length=None`（防止截断图像 token）

**通常你完全不需要设置此参数** - 以下示例使用合理的默认值。

### 方法 1：UV 脚本（推荐——默认选择）

UV 脚本使用 PEP 723 内联依赖，实现简洁、自包含的训练。**这是 Claude Code 的主要方法。**

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

# 创建训练/评估分割用于监控
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
        project="meaningful_prject_name", # 训练名称的项目名（trackio）
        run_name="meaningful_run_name",   # 特定训练运行的描述性名称（trackio）
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

**优点：** 直接使用 MCP 工具，代码整洁，依赖内联声明（PEP 723），无需保存文件，完全可控
**使用场景：** Claude Code 中所有训练任务的默认选择、自定义训练逻辑、任何需要 `hf_jobs()` 的场景

#### 使用脚本

⚠️ **重要：** `script` 参数接受内联代码（如上文所示）或 URL。**本地文件路径不起作用。**

**为什么本地路径不起作用：**
任务在隔离的 Docker 容器中运行，无法访问你的本地文件系统。脚本必须是：
- 内联代码（自定义训练推荐）
- 公开可访问的 URL
- 私有仓库 URL（配合 HF_TOKEN）

**常见错误：**
```python
# ❌ 以下都会失败
hf_jobs("uv", {"script": "train.py"})
hf_jobs("uv", {"script": "./scripts/train.py"})
hf_jobs("uv", {"script": "/path/to/train.py"})
```

**正确方法：**
```python
# ✅ 内联代码（推荐）
hf_jobs("uv", {"script": "# /// script\n# dependencies = [...]\n# ///\n\n<your code>"})

# ✅ 来自 Hugging Face Hub
hf_jobs("uv", {"script": "https://huggingface.co/user/repo/resolve/main/train.py"})

# ✅ 来自 GitHub
hf_jobs("uv", {"script": "https://raw.githubusercontent.com/user/repo/main/train.py"})

# ✅ 来自 Gist
hf_jobs("uv", {"script": "https://gist.githubusercontent.com/user/id/raw/train.py"})
```

**使用本地脚本：** 先上传到 HF Hub：
```bash
hf repos create my-training-scripts --type model
hf upload my-training-scripts ./train.py train.py
# 使用: https://huggingface.co/USERNAME/my-training-scripts/resolve/main/train.py
```

### 方法 2：TRL 维护的脚本（官方示例）

TRL 为所有方法提供经过实战检验的脚本。可从 URL 运行：

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

**优点：** 无需编写代码，由 TRL 团队维护，经过生产环境测试
**使用场景：** 标准 TRL 训练、快速实验、不需要自定义代码
**获取方式：** 脚本可从 https://github.com/huggingface/trl/tree/main/examples/scripts 获取

### 在 Hub 上查找更多 UV 脚本

`uv-scripts` 组织提供即开即用的 UV 脚本，以数据集形式存储在 Hugging Face Hub 上：

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

# ❌ 错误 - 使用 "run uv" 而非 "uv run"
hf jobs run uv "https://example.com/train.py" --flavor a10g-large

# ❌ 错误 - 标志在脚本 URL 之后（将被忽略！）
hf jobs uv run "https://example.com/train.py" --flavor a10g-large

# ❌ 错误 - 使用 "--secret" 而非 "--secrets"（复数）
hf jobs uv run --secret HF_TOKEN "https://example.com/train.py"
```

**关键语法规则：**
1. 命令顺序为 `hf jobs uv run`（而非 `hf jobs run uv`）
2. 所有标志（`--flavor`、`--timeout`、`--secrets`）必须在脚本 URL 之前
3. 使用 `--secrets`（复数），而非 `--secret`
4. 脚本 URL 必须是最后一个位置参数

**完整 CLI 示例：**
```bash
hf jobs uv run \
  --flavor a10g-large \
  --timeout 2h \
  --secrets HF_TOKEN \
  "https://huggingface.co/user/repo/resolve/main/train.py"
```

**通过 CLI 检查任务状态：**
```bash
hf jobs ps                        # 列出所有任务
hf jobs logs <job-id>             # 查看日志
hf jobs inspect <job-id>          # 任务详情
hf jobs cancel <job-id>           # 取消任务
```

### 方法 4：TRL Jobs 包（简化训练）

`trl-jobs` 包提供优化的默认设置和单行训练。

```bash
uvx trl-jobs sft \
  --model_name Qwen/Qwen2.5-0.5B \
  --dataset_name trl-lib/Capybara

```

**优点：** 预配置设置、自动 Trackio 集成、自动 Hub 推送、单行命令
**使用场景：** 用户直接在终端中工作（非 Claude Code 上下文）、快速本地实验
**仓库：** https://github.com/huggingface/trl-jobs

⚠️ **在 Claude Code 上下文中，优先使用 `hf_jobs()` MCP 工具（方法 1）。**

## 硬件选择

| 模型大小 | 推荐硬件 | 成本（约/小时） | 使用场景 |
|------------|---------------------|------------------|----------|
| <1B 参数 | `t4-small` | ~$0.75 | 演示、无评估步骤的快速测试 |
| 1-3B 参数 | `t4-medium`、`l4x1` | ~$1.50-2.50 | 开发 |
| 3-7B 参数 | `a10g-small`、`a10g-large` | ~$3.50-5.00 | 生产训练 |
| 7-13B 参数 | `a10g-large`、`a100-large` | ~$5-10 | 大模型（使用 LoRA） |
| 13B+ 参数 | `a100-large`、`a10g-largex2` | ~$10-20 | 超大模型（使用 LoRA） |

**GPU 规格：** cpu-basic/upgrade/performance/xl, t4-small/medium, l4x1/x4, a10g-small/large/largex2/largex4, a100-large, h100/h100x8

**指南：**
- 模型 >7B 时使用 **LoRA/PEFT** 以减少内存
- 多 GPU 由 TRL/Accelerate 自动处理
- 使用较小硬件进行测试

**参见：** `references/hardware_guide.md` 了解详细规格

## 关键：保存结果到 Hub

**⚠️ 临时环境——必须推送到 HUB**

Jobs 环境是临时的。任务结束后所有文件都会被删除。如果模型未推送到 Hub，**所有训练结果都会丢失**。

### 必需配置

**在训练脚本/配置中：**
```python
SFTConfig(
    push_to_hub=True,
    hub_model_id="username/model-name",  # 必须指定
    hub_strategy="every_save",  # 可选：推送检查点
)
```

**在任务提交中：**
```python
{
    "secrets": {"HF_TOKEN": "$HF_TOKEN"}  # 启用认证
}
```

### 验证清单

提交前：
- [ ] 配置中已设置 `push_to_hub=True`
- [ ] `hub_model_id` 包含 username/repo-name
- [ ] `secrets` 参数包含 HF_TOKEN
- [ ] 用户对目标仓库具有写入权限

**参见：** `references/hub_saving.md` 了解详细故障排除

## 超时管理

**⚠️ 默认：30 分钟——对训练来说太短**

### 设置超时

```python
{
    "timeout": "2h"   # 2 小时（格式："90m"、"2h"、"1.5h" 或秒数整数）
}
```

### 超时指南

| 场景 | 建议值 | 备注 |
|----------|-------------|-------|
| 快速演示（50-100 个示例） | 10-30 分钟 | 验证配置 |
| 开发训练 | 1-2 小时 | 小数据集 |
| 生产（3-7B 模型） | 4-6 小时 | 完整数据集 |
| 大模型配合 LoRA | 3-6 小时 | 取决于数据集 |

**始终预留 20-30% 的缓冲**，用于模型/数据集加载、检查点保存、Hub 推送操作和网络延迟。

**超时后：** 任务立即终止，所有未保存的进度丢失，必须从头开始。

## 选择基础模型（模型选择）

**根据任务类型或基准测试结果确定要训练的模型。**

使用 `scripts/hf_benchmarks.py` 识别特定任务中表现最佳的模型。这有助于用户选择训练的基础模型，同时考虑大小和硬件约束。

```bash
# 获取基准命令的帮助：
uv run scripts/hf_benchmarks.py --help
```

### 示例 —— 选择 OCR 基础模型
```bash
# 搜索名称包含 `ocr` 文本的基准
uv run scripts/hf_benchmarks.py search --query ocr

# 获取 allenai/olmOCR-bench 基准的排名排行榜
uv run scripts/hf_benchmarks.py leaderboard allenai/olmOCR-bench
```

## 费用估算

**在计划已知参数的任务时，主动提供费用估算。** 使用 `scripts/estimate_cost.py`：

```bash
uv run scripts/estimate_cost.py \
  --model meta-llama/Llama-2-7b-hf \
  --dataset trl-lib/Capybara \
  --hardware a10g-large \
  --dataset-size 16000 \
  --epochs 3
```

输出包含预估时间、费用、建议的超时时间（含缓冲）和优化建议。

**何时提供：** 用户正在规划任务、询问费用/时间、选择硬件、任务运行将超过 1 小时或费用超过 $5

## 示例训练脚本

**生产就绪模板，包含所有最佳实践：**

正确加载这些脚本：

- **`scripts/train_sft_example.py`** - 完整 SFT 训练，含 Trackio、LoRA、检查点
- **`scripts/train_dpo_example.py`** - 偏好学习的 DPO 训练
- **`scripts/train_grpo_example.py`** - 在线强化学习的 GRPO 训练

这些脚本展示了正确的 Hub 保存、Trackio 集成、检查点管理和优化参数。将其内容内联传递给 `hf_jobs()` 或用作自定义脚本的模板。

## 监控与追踪

**Trackio** 提供实时指标可视化。完整设置指南请参阅 `references/trackio_guide.md`。

**要点：**
- 在依赖项中添加 `trackio`
- 配置训练器使用 `report_to="trackio" and run_name="meaningful_name"`

### Trackio 配置默认值

**除非用户另行指定，否则使用合理的默认值。** 生成包含 Trackio 的训练脚本时：

**默认配置：**
- **Space ID**：`{username}/trackio`（使用 "trackio" 作为默认 space 名称）
- **运行命名**：除非另有指定，以用户可识别的方式命名运行（例如描述任务、模型或用途）
- **配置**：保持最小化 - 仅包含超参数和模型/数据集信息
- **项目名称**：使用项目名称将运行与特定项目关联

**用户覆盖：** 如果用户请求特定的 trackio 配置（自定义 space、运行命名、分组或额外配置），则应用用户偏好而非默认值。

这在管理具有相同配置的多个任务或保持训练脚本可移植性时非常有用。

完整文档请参阅 `references/trackio_guide.md`，包括运行分组用于实验。

### 检查任务状态

```python
# 列出所有任务
hf_jobs("ps")

# 检查特定任务
hf_jobs("inspect", {"job_id": "your-job-id"})

# 查看日志
hf_jobs("logs", {"job_id": "your-job-id"})
```

**注意：** 等待用户请求状态检查。避免重复轮询。

## 数据集验证

**在启动 GPU 训练之前验证数据集格式，以防止训练失败的首要原因：格式不匹配。**

### 为什么验证

- 50% 以上的训练失败源于数据集格式问题
- DPO 尤其严格：需要精确的列名（`prompt`、`chosen`、`rejected`）
- 失败的 GPU 任务浪费 $1-10 和 30-60 分钟
- CPU 验证费用约 $0.01，耗时不到 1 分钟

### 何时验证

**始终验证以下情况：**
- 未知或自定义数据集
- DPO 训练（关键 - 90% 的数据集需要映射）
- 任何未明确兼容 TRL 的数据集

**以下已知 TRL 数据集可跳过验证：**
- `trl-lib/ultrachat_200k`、`trl-lib/Capybara`、`HuggingFaceH4/ultrachat_200k` 等

### 使用方式

```python
hf_jobs("uv", {
    "script": "https://huggingface.co/datasets/mcp-tools/skills/raw/main/dataset_inspector.py",
    "script_args": ["--dataset", "username/dataset-name", "--split", "train"]
})
```

该脚本运行快速，通常同步完成。

### 读取结果

输出显示每种训练方法的兼容性：

- **`✓ READY`** - 数据集兼容，可直接使用
- **`✗ NEEDS MAPPING`** - 兼容但需要预处理（提供映射代码）
- **`✗ INCOMPATIBLE`** - 不能用于此方法

当需要映射时，输出包含 **"MAPPING CODE"** 部分，提供可直接复制粘贴的 Python 代码。

### 示例工作流

```python
# 1. 检查数据集（费用约 $0.01，CPU 上 <1 分钟）
hf_jobs("uv", {
    "script": "https://huggingface.co/datasets/mcp-tools/skills/raw/main/dataset_inspector.py",
    "script_args": ["--dataset", "argilla/distilabel-math-preference-dpo", "--split", "train"]
})

# 2. 检查输出标记：
#    ✓ READY → 继续训练
#    ✗ NEEDS MAPPING → 应用下方映射代码
#    ✗ INCOMPATIBLE → 选择不同方法/数据集

# 3. 如果需要映射，训练前应用：
def format_for_dpo(example):
    return {
        'prompt': example['instruction'],
        'chosen': example['chosen_response'],
        'rejected': example['rejected_response'],
    }
dataset = dataset.map(format_for_dpo, remove_columns=dataset.column_names)

# 4. 放心启动训练任务
```

### 常见场景：DPO 格式不匹配

大多数 DPO 数据集使用非标准列名。示例：

```
数据集包含: instruction, chosen_response, rejected_response
DPO 期望: prompt, chosen, rejected
```

验证器会检测到此问题并提供精确的映射代码来修复。

## 将模型转换为 GGUF

训练完成后，将模型转换为 **GGUF 格式**，以便与 llama.cpp、Ollama、LM Studio 和其他本地推理工具配合使用。

**GGUF 是什么：**
- 为 llama.cpp 的 CPU/GPU 推理优化
- 支持量化（4-bit、5-bit、8-bit）以减少模型大小
- 兼容 Ollama、LM Studio、Jan、GPT4All、llama.cpp
- 7B 模型通常为 2-8GB（未量化为 14GB）

**何时转换：**
- 在本地使用 Ollama 或 LM Studio 运行模型
- 通过量化减少模型大小
- 部署到边缘设备
- 共享模型用于本地优先使用

**参见：** `references/gguf_conversion.md` 了解完整转换指南，包括生产就绪的转换脚本、量化选项、硬件要求、使用示例和故障排除。

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

## 常见训练模式

详见 `references/training_patterns.md`，包含以下示例：
- 快速演示（5-10 分钟）
- 带检查点的生产训练
- 多 GPU 训练
- DPO 训练（偏好学习）
- GRPO 训练（在线强化学习）

## 常见故障模式

### 内存不足（OOM）

**修复方法（按顺序尝试）：**
1. 减小批大小：`per_device_train_batch_size=1`，增大 `gradient_accumulation_steps=8`。有效批大小 = `per_device_train_batch_size` × `gradient_accumulation_steps`。为获得最佳性能，保持有效批大小接近 128。
2. 启用：`gradient_checkpointing=True`
3. 升级硬件：t4-small → l4x1，a10g-small → a10g-large 等。

### 数据集格式错误

**修复方法：**
1. 先使用数据集检查器验证：
   ```bash
   uv run https://huggingface.co/datasets/mcp-tools/skills/raw/main/dataset_inspector.py \
     --dataset name --split train
   ```
2. 检查输出中的兼容性标记（✓ READY、✗ NEEDS MAPPING、✗ INCOMPATIBLE）
3. 如有需要，应用检查器输出中的映射代码

### 任务超时

**修复方法：**
1. 检查日志中的实际运行时间：`hf_jobs("logs", {"job_id": "..."})`
2. 增加超时并预留缓冲：`"timeout": "3h"`（在预估时间基础上增加 30%）
3. 或减少训练：降低 `num_train_epochs`、使用更小的数据集、启用 `max_steps`
4. 保存检查点：`save_strategy="steps"`、`save_steps=500`、`hub_strategy="every_save"`

**注意：** 默认 30 分钟不足以进行实际训练。最低 1-2 小时。

### Hub 推送失败

**修复方法：**
1. 添加到任务：`secrets={"HF_TOKEN": "$HF_TOKEN"}`
2. 添加到配置：`push_to_hub=True`、`hub_model_id="username/model-name"`
3. 验证认证：`mcp__huggingface__hf_whoami()`
4. 检查 token 具有写入权限且仓库存在（或设置 `hub_private_repo=True`）

### 缺少依赖

**修复方法：**
添加到 PEP 723 头部：
```python
# /// script
# dependencies = ["trl>=0.12.0", "peft>=0.7.0", "trackio", "missing-package"]
# ///
```

## 故障排除

**常见问题：**
- 任务超时 → 增加超时、减少 epoch/数据集、使用更小模型/LoRA
- 模型未保存到 Hub → 检查 push_to_hub=True、hub_model_id、secrets=HF_TOKEN
- 内存不足（OOM）→ 减小批大小、增加梯度累积、启用 LoRA、使用更大 GPU
- 数据集格式错误 → 使用数据集检查器验证（见数据集验证部分）
- 导入/模块错误 → 添加包含依赖的 PEP 723 头部，验证格式
- 认证错误 → 检查 `mcp__huggingface__hf_whoami()`、token 权限、secrets 参数

**参见：** `references/troubleshooting.md` 了解完整故障排除指南

## 资源

### 参考文档（本技能内）
- `references/training_methods.md` - SFT、DPO、GRPO、KTO、PPO、奖励建模概览
- `references/training_patterns.md` - 常见训练模式和示例
- `references/unsloth.md` - Unsloth 快速 VLM 训练（~2x 速度，60% 更少 VRAM）
- `references/gguf_conversion.md` - 完整 GGUF 转换指南
- `references/trackio_guide.md` - Trackio 监控设置
- `references/hardware_guide.md` - 硬件规格和选择
- `references/hub_saving.md` - Hub 认证故障排除
- `references/troubleshooting.md` - 常见问题和解决方案
- `references/local_training_macos.md` - macOS 本地训练

### 脚本（本技能内）
- `scripts/train_sft_example.py` - 生产 SFT 模板
- `scripts/train_dpo_example.py` - 生产 DPO 模板
- `scripts/train_grpo_example.py` - 生产 GRPO 模板
- `scripts/unsloth_sft_example.py` - Unsloth 文本 LLM 训练模板（更快，更少 VRAM）
- `scripts/estimate_cost.py` - 估算时间和费用（适时提供）
- `scripts/convert_to_gguf.py` - 完整 GGUF 转换脚本
- `scripts/hf_benchmarks.py` - 按任务、别名或自由文本搜索基准结果和排行榜。

### 外部脚本
- [Dataset Inspector](https://huggingface.co/datasets/mcp-tools/skills/raw/main/dataset_inspector.py) - 训练前验证数据集格式（通过 `uv run` 或 `hf_jobs` 使用）

### 外部链接
- [TRL 文档](https://huggingface.co/docs/trl)
- [TRL Jobs 训练指南](https://huggingface.co/docs/trl/en/jobs_training)
- [TRL Jobs 包](https://github.com/huggingface/trl-jobs)
- [HF Jobs 文档](https://huggingface.co/docs/huggingface_hub/guides/jobs)
- [TRL 示例脚本](https://github.com/huggingface/trl/tree/main/examples/scripts)
- [UV 脚本指南](https://docs.astral.sh/uv/guides/scripts/)
- [UV Scripts 组织](https://huggingface.co/uv-scripts)

## 要点总结

1. **内联提交脚本** - `script` 参数直接接受 Python 代码；除非用户要求，否则无需保存文件
2. **任务是异步的** - 不要等待/轮询；让用户准备好时再检查
3. **始终设置超时** - 默认 30 分钟不够；建议最低 1-2 小时
4. **始终启用 Hub 推送** - 环境是临时的；不推送则所有结果丢失
5. **包含 Trackio** - 使用示例脚本作为模板进行实时监控
6. **提供费用估算** - 参数已知时，使用 `scripts/estimate_cost.py`
7. **使用 UV 脚本（方法 1）** - 默认使用 `hf_jobs("uv", {...})` 配合内联脚本；标准训练使用 TRL 维护的脚本；在 Claude Code 中避免 bash `trl-jobs` 命令
8. **使用 hf_doc_fetch/hf_doc_search** 获取最新 TRL 文档
9. **训练前验证数据集格式**，使用数据集检查器（见数据集验证部分）
10. **根据模型大小选择合适的硬件**；模型 >7B 时使用 LoRA
