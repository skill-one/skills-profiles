# 自动配方 — 配方索引与推荐

此技能索引所有已发布的配方，并帮助用户选择合适的起始配置、调整并行度，并避免常见陷阱。

## 如何使用此技能

1. 向用户询问：**模型名称/大小**、**GPU 数量与类型**、**训练目标**（预训练 / SFT / PEFT），以及**序列长度**（如果非默认值）。
2. 在下方的索引中查找最佳匹配的配方。
3. 推荐配方函数名称 + 入口点命令。
4. 提供调整建议（并行度调整、批处理调优、陷阱）。

## 首次回答检查清单

在推荐配方时，始终在长索引详情之前包含以下区别：

1. `src/megatron/bridge/recipes/` 下的 **库配方** 用于功能训练，并使用 `scripts/training/run_recipe.py`。
2. `src/megatron/bridge/perf_recipes/` 下的 **基准配方** 用于上限吞吐量基准测试。它们拥有自己的规范基准数据和设置，不应作为生产训练配方呈现。
3. 对于首次 Bridge 烟雾测试，推荐使用 `llama3_8b_pretrain_config` 并通过 `--dataset mock` 使用模拟数据。
4. 对于正常 SFT 推荐，选择微调预设，例如 `--dataset squad` 或 `--dataset tulu3`；对于预训练和模拟验证推荐，使用 `--dataset mock`。不要将仅预训练的 `mock` 预设与 SFT 或 PEFT 模式配对。
5. 在配方和数据集之后，提供所需的调整规则：TP 必须能整除 `num_key_value_heads`，保持 TP 在单个节点内（除非使用 NVL72 类级互连），当 TP > 1 时启用 SP，为长上下文配置 CP，DP 是隐式的，并在 OOM 时首先减少 `micro_batch_size`。
6. 说明每个建议的覆盖是否改变了收敛契约，还是仅改变了执行/性能映射。不要在不将其称为新实验的情况下，用收敛语义换取吞吐量。

## 配置层和变更控制

在推荐或调整配方之前，将训练语义与其硬件映射分开。

**收敛配置** 包括起始检查点和可训练参数；数据集/修订/分割/顺序/种子；分词器、掩码、截断和打包；序列长度；全局批处理和标记预算；目标值和损失系数；自然或强制 MoE 路由和标记丢弃策略；优化器、LR、调度、预热、beta、epsilon、权重衰减、剪裁和 dropout；算术和优化器状态精度；以及 PEFT 适配器设置。更改其中一项会创建一个新的收敛实验。

**执行/性能配置** 包括硬件数量和拓扑；TP/PP/VP/CP/EP/ETP/DP/SP；重新计算和卸载；分布式优化器/FSDP；通信重叠；融合和注意力后端；CUDA 图和编译；检查点 I/O；以及当路由策略不变时，通过所有对全、DeepEP 或 HybridEP 的 MoE 传输。这些设置应保持目标值和有效更新，尽管浮点数减少顺序可能产生小的数值漂移，但仍需验证。

将微批处理大小和梯度累积视为执行指纹。仅使用固定的全局批处理大小、全局批处理成员资格/顺序、标准化、优化器边界和标记预算进行调整，并为每个布局验证新的损失哨兵。打包、精度、强制 MoE 负载平衡、标记丢弃/容量以及路由器/辅助损失更改永远不会是仅性能旋钮。

将模拟数据、强制平衡、禁用正确性检查和仅计时调度视为仅基准的快捷方式。它们在 `perf_recipes` 中可能适用，但它们的损失和检查点不是收敛证据。

对于可比较的模型验证配方，在调整性能之前选择一个全组范围的收敛契约。在架构允许的情况下，保持相同的受约束数据选择、预处理、序列长度、全局批处理、优化器/调度、精度、种子、路由策略、优化器步长范围和已处理标记检查点。记录任何必要的模型特定偏差，并且不要将结果作为苹果对苹果的收敛证据呈现。来自不同架构或分词器的绝对损失不能直接排序；在相等的标记计数下比较稳定性和趋势。

当配方的批处理与选择的收敛契约不一致时，单独修改和验证库配方。声明的受约束验证协议可以明确地将相同的 LR、调度、序列和数据覆盖应用于全组，但不要仅仅为了提高吞吐量而进行一次性的收敛更改。相反，在优化拟合或吞吐量时，首先尝试 TP/PP/CP/EP、重新计算/卸载、调度器传输、重叠、融合和 CUDA 图。

---

## 入口点

### 库配方（功能训练）

```bash
# 使用模拟数据预训练
uv run python -m torch.distributed.run --nproc_per_node=8 scripts/training/run_recipe.py \
    --recipe <recipe_function_name> \
    --dataset mock

# 使用 SQuAD 进行 SFT
uv run python -m torch.distributed.run --nproc_per_node=8 scripts/training/run_recipe.py \
    --recipe <recipe_function_name> \
    --dataset squad

# 通过 CLI 覆盖任何字段
uv run python -m torch.distributed.run --nproc_per_node=8 scripts/training/run_recipe.py \
    --recipe llama3_8b_pretrain_config \
    --dataset mock \
    'model.tensor_model_parallel_size=2' \
    'train.global_batch_size=64'
```

### 基准配方（吞吐量基准测试）

```bash
./scripts/training/train.sh \
    --nodes 2 --gpus-per-node 8 \
    --account ACCOUNT --partition PARTITION --container-image IMAGE \
    --recipe qwen3_30b_a3b_pretrain_16gpu_h100_bf16_config \
    --mode pretrain
```

总 GPU 分配必须与配方名称中编码的数量匹配。用户选择节点形状，所选分区必须提供请求的硬件。启动器不会注入基准离线默认值或集群特定启动策略。使用 `--env NAME` 用于导出的离线或 NCCL 布局设置，并使用重复的 `--srun-arg=ARG` 选项用于 `srun`。通过目标集群集成配置 CPU/NUMA 包装和 Slurm 段大小，或在其兼容性策略需要时使用 `scripts/performance/setup_experiment.py`。统一的启动器支持精确导出的文本预训练、文本 SFT/PEFT、Qwen-VL 预训练和 Wan 预训练配方，并推断其前向步骤。文本 SFT/PEFT 文本基准配方保留扁平运行者的模拟数据默认值；Qwen-VL 和 Wan 保留其模型特定数据集。导出的基准 PEFT 配方是固定的 LoRA 配置；使用可配置的库配方进行 DoRA。尾随的 `KEY=VALUE` 覆盖被接受，但覆盖的基准配方不再代表其规范基准配置。使用 `scripts/performance/setup_experiment.py` 进行基于选择器的调用、数据集替换、拓扑调整和专用基准控制。

在使用这些进行任何超出吞吐量基准测试之前，请查看基准配方布局的重要注意事项。

---

## 基准配方布局

基准配方与库配方使用相同的 **Python 函数** 格式，但存在于专用于吞吐量基准测试的命名空间中：

- 基准配方位于 `src/megatron/bridge/perf_recipes/<family>/<hardware>/<model>.py`
- 每个基准配方是一个 **自包含的 Python 函数**（例如 `llama3_8b_pretrain_8gpu_h100_bf16_config()`）
- 配方名称编码模型、任务、GPU 数量、硬件、精度和可选变体
- `scripts/performance/utils/utils.py` 从扁平配方本身派生兼容性 `WorkloadBaseConfig` 视图
- 共享帮助：`_benchmark_common()`（50 次迭代、计时、TE 随机数）、`_perf_precision()`（bf16 / fp8_cs / fp8_mx / nvfp4）

**为什么是 Python 而不是 YAML？** 之前的基于 YAML 的方法存在问题：配方逻辑分布在多个间接层中，配置不是自包含的，两级管道使维护和调试变得困难。Python 函数是明确的、可搜索的和可组合的。

训练启动器根据完整的导出函数名称发现库和基准配方。五个遗留的重复名称选择基准定义；使用相应的通用别名进行这些功能工作负载。新的配方名称应在两个包中保持唯一。

---

## 配方索引（库与基准）

完整的按系列配方表——每个已发布的 **库** 配方（`src/megatron/bridge/recipes/`）和 **基准** 配方（`src/megatron/bridge/perf_recipes/`），以及并行度、最小 GPU 数量和硬件覆盖范围——保存在一个专用参考文件中，以使此技能保持简洁：

**→ 查看 [`references/recipe-index.md`](references/recipe-index.md)** — 库配方索引（Llama、Qwen2/2.5/3、Qwen3-MoE、Qwen3-Next、DeepSeek、GLM-4.5、Gemma、Nemotron、VLM、扩散）和基准配方索引（按硬件吞吐量配置）。

加载该文件以获取确切的配方函数名称或其默认并行度；下方的指南告诉您要查找哪个条目。

---

## 推荐决策树

```text
用户想训练模型
│
├─ 知道模型名称？
│   ├─ 是 → 在 references/recipe-index.md 中查找
│   │   ├─ 是否有适合其大小 + 模式的配方？ → 直接使用
│   │   └─ 没有确切匹配？ → 使用最接近的大小，调整并行度
│   └─ 否 → 询问模型名称、大小和 HF 模型 ID
│
├─ 训练目标是什么？
│   ├─ 预训练 → 使用 *_pretrain_config
│   ├─ SFT（完整微调） → 使用 *_sft_config
│   └─ PEFT（LoRA/DoRA） → 使用 *_peft_config（最低 GPU 要求）
│
├─ 需要多少 GPU？
│   ├─ 1 GPU → 仅 PEFT 配方可用（TP=1, PP=1）
│   ├─ 8 GPU（1 个节点） → 大多数 8B–16B 模型，小 MoE（EP=8）
│   ├─ 16–64 GPU → 70B 密集型，中等 MoE
│   └─ 128+ GPU → 405B+，大 MoE（DeepSeek V3、Kimi K2）
│
├─ 想要吞吐量基准测试？
│   ├─ 是 → 使用基准配方（src/megatron/bridge/perf_recipes/）
│   │   ├─ 精确导出配方 → scripts/training/train.sh --recipe <exact function name>
│   │   └─ 选择器/专用工作流 → scripts/performance/setup_experiment.py
│   └─ 否 → 使用库配方（scripts/training/run_recipe.py）
│
└─ 长上下文？
    ├─ > 8K → 需要 CP（上下文并行），检查 *_16k / *_64k / *_128k 变体
    └─ ≤ 8K → 默认配方可用
```

---

## 调整建议（当推荐时）

### 并行度调整规则

当用户的 GPU 数量与配方默认值不同时：

1. **TP 必须能整除 `num_key_value_heads`**（GQA 约束）。例如，如果 `num_key_value_heads=8`，有效 TP = {1, 2, 4, 8}。
2. **TP 应保持在单个节点内**（NVLink）。TP > 8 需要跨节点的 NVLink（例如，GB200 NVL72）。
3. **PP 添加流水线气泡。** 最小化 PP；仅在 TP 单独无法容纳模型时增加。使用 VP（虚拟流水线）来减轻气泡开销。
4. **EP 不减少密集层内存。** 仅专家参数与 EP 分片。共享注意力/嵌入被复制。对于“MoE 时 OOM”，首先增加 EP，而不是 TP。
5. **SP 应在 TP > 1 时为 True。** 它消除了冗余激活副本，并且基本上是免费的。
6. **CP 需要所有对全或环形注意力。** 检查 `cp_comm_type`。对于 GQA 模型，`a2a+p2p` 分层 CP 允许 CP > num_kv_heads。
7. **密集和专家网格重叠。** 不要将 TP 和 EP 相乘。最小的 MoE 世界大小是 `PP × max(TP × CP, EP × ETP)`。密集 DP 是 `world_size / (TP × PP × CP)`，专家 EDP 是 `world_size / (PP × EP × ETP)`；这两个商必须为整数，并且专家数量必须能被 EP 整除。

### 批处理大小调优

- 从配方的 `micro_batch_size` 开始。如果 OOM，减少到 1。
- `global_batch_size` 决定学习动态。按 DP 缩放：`GBS = micro_batch_size × DP × gradient_accumulation_steps`。
- 对于 MoE，`micro_batch_size=1` 在规模上是典型的。

### 常见陷阱警告

| 陷阱 | 症状 | 修复 |
|------|------|------|
| TP > num_kv_heads | 故障："TP 必须能整除 num_query_groups" | 将 TP 减少为 num_kv_heads 的除数 |
| PP 而无 VP | 吞吐量差（大气泡） | 设置 `virtual_pipeline_model_parallel_size` |
| EP 对于大 MoE 太低 | 专家参数 OOM | 增加 EP；每个专家位于 EP/num_experts 排名上 |
| CUDA 图 + 打包序列 | 异常："CUDA 图仅接受 Tensor 输入" | 禁用打包或使用 `local` 全迭代图 |
| CUDA 图 + 全重新计算 | 异常："仅在全迭代 CUDA 图上使用完整重新计算" | 禁用重新计算或切换到 `local` 实现 |
| `use_te_rng_tracker` 未设置 | 启用 CUDA 图时在提供者初始化时出现异常 | 设置 `cfg.model.use_te_rng_tracker = True` 和 `cfg.rng.te_rng_tracker = True` |
| FSDP + TP > 1 在 H100 上 | 可能的通信瓶颈 | 在 H100 上优先选择 FSDP with TP=1 或 TP=2；FSDP 在 GB/B 系列上表现优异 |
| 无 CP 的长上下文 | 激活 OOM | 增加 CP=2/4/8；使用 `*_16k`、`*_64k` 或 `*_128k` 配方变体 |
| MoE `overlap_grad_reduce` 在 H100 上 | 可能会损害吞吐量（许多 H100 预设中为 False） | 设置 `overlap_grad_reduce=False` 用于 H100 上的 MoE |
| VLM SFT 缺少图像数据 | 运行但产生垃圾 | 提供实际的多模态数据集或使用模拟 VLM 数据 |
| Qwen35-VL MoE FSDP | 仅在 Blackwell 上测试 | 可能不适用于 H100；先验证 |

### 配方覆盖示例

```bash
# 将 Llama3 8B 从 2 个 GPU 扩展到 8 个 GPU（增加 DP）
uv run python -m torch.distributed.run --nproc_per_node=8 scripts/training/run_recipe.py \
    --recipe llama3_8b_pretrain_config \
    --dataset mock

# 运行原生 4-GPU Qwen3-MoE 30B PEFT 拓扑
uv run python -m torch.distributed.run --nproc_per_node=4 scripts/training/run_recipe.py \
    --recipe qwen3_30b_a3b_peft_config \
    --dataset tulu3

# 向现有配方添加长上下文
uv run python -m torch.distributed.run --nproc_per_node=8 scripts/training/run_recipe.py \
    --recipe llama3_8b_pretrain_config \
    --dataset mock \
    'model.seq_length=32768' \
    'model.context_parallel_size=4'

# 在任何配方上启用 CUDA 图
uv run python -m torch.distributed.run --nproc_per_node=8 scripts/training/run_recipe.py \
    --recipe qwen3_30b_a3b_pretrain_config \
    --dataset mock \
    'model.cuda_graph_impl=transformer_engine' \
    'model.cuda_graph_scope=[attn,moe_router,moe_preprocess]' \
    'model.use_te_rng_tracker=True' \
    'rng.te_rng_tracker=True'
```

---

## 快速参考：哪种配方适合我的情况？

| 我想... | 从...开始 | 需要的 GPU |
|---|---|---|
| 首次尝试 Bridge | `llama3_8b_pretrain_config` + 模拟数据 | 2 |
| 微调 7-8B 模型 | `llama3_8b_sft_config` 或 `qwen3_8b_sft_config` | 2–4 |
| 1 个 GPU 上的 LoRA | `llama3_8b_peft_config` 或 `qwen3_8b_peft_config` | 1 |
| 训练密集 70B | `llama3_70b_pretrain_config` | 32–64 |
| 训练小 MoE | `qwen3_30b_a3b_pretrain_config` | 16 |
| 训练大 MoE（235B+） | `qwen3_235b_a22b_pretrain_config` | 256–512 |
| 基准测试文本预训练吞吐量 | 通过 `train.sh --recipe <exact name>` 使用基准配方 | 精确编码的数量 |
| 长上下文训练 | `llama3_8b_128k_pretrain_config` 或添加 CP 覆盖 | 16+ |
| VLM 微调 | `qwen3_vl_8b_sft_config` 或 `gemma3_vl_*_sft_config` | 4–8 |
| 扩散训练 | `wan_1_3B_pretrain_config` 或 `flux_12b_pretrain_config` | 8 |

---

## 代码锚点

| 什么 | 路径 |
|------|------|
| 库配方根 | `src/megatron/bridge/recipes/` |
| 配方 `__init__.py`（所有导出） | `src/megatron/bridge/recipes/__init__.py` |
| 常用配方帮助 | `src/megatron/bridge/recipes/common.py` |
| 训练入口点 | `scripts/training/run_recipe.py` |
| 训练 Slurm 启动器 | `scripts/training/train.sh` |
| 基准配方根 | `src/megatron/bridge/perf_recipes/` |
| 基准兼容性启动器 | `scripts/performance/setup_experiment.py` |
| 基准配方帮助 | `scripts/performance/utils/utils.py` |
| 基准覆盖 | `scripts/performance/utils/overrides.py` |

_最后签名刷新：2026-08-03_
