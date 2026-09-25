# 内存调优

稳定文档：@docs/parallelisms.md
卡片：@skills/nemo-mbridge-perf-memory-tuning/card.yaml

## 它是什么

训练期间 GPU OOM 失败通常源于内存**碎片化**，而非原始容量不足。PyTorch 的默认 CUDA 分配器会在分配之间留下不可用的间隙。最有效的修复方法是：

```bash
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```

这告诉 PyTorch 使用可扩展（非固定大小）的内存段，这会显著减少碎片化，并常常在不改变模型或并行性的情况下消除临界 OOM。

除了碎片化，实际峰值内存由以下因素决定：

- **参数 + 优化器状态内存** — 由 TP、PP、DP 分片（分布式优化器、FSDP）控制
- **激活内存** — 由激活重计算、序列长度、微批处理大小以及 PEFT 特定的收集输入保留控制
- **临时 / 工作空间内存** — CUDA 内核、NCCL 缓冲区、CUDA 图

配置规划时，在启动大型作业前使用 Bridge 理论估计器：

```python
from megatron.bridge.training.utils.theoretical_memory_utils import estimate_training_memory

estimate = estimate_training_memory(cfg, num_microbatches=num_microbatches)
```

估计器报告最繁忙的 GPU 片段，并将密集/嵌入、路由 MoE 专家和激活组件分开。它不包括分配器碎片化、CUDA/NCCL 工作空间、CUDA 图缓冲区、token 不平衡或调度器工作空间，因此需使用运行时内存指标验证最终配置。

## 快速决策

当训练运行 OOM 或接近内存限制时：

1. **首先设置 `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`。** 这会以零性能成本修复碎片化引起的 OOM。大多数 Slurm 启动模板已包含它。
2. **对于 LoRA 与序列并行，启用输入重新收集** (`LoRA(sequence_parallel_input_regather=True)`)。这会避免在每个符合条件的层中保留完整的收集 LoRA-A 输入；当 SP 禁用时无效。
3. **如果尚未启用，添加选择性激活重计算** (`recompute_modules=[core_attn]`)。参见 @skills/nemo-mbridge-perf-activation-recompute/SKILL.md。
4. **避免将 TP 增加作为内存修复方案** — 将 TP 倍增会大幅增加 NVLink 全归约量，并常常降低吞吐量（Llama3 70B 上 -28%）。
5. **避免以牺牲 DP 为代价增加 PP** — 将 DP 减半会加倍梯度累积步数，损害吞吐量（约 6%）。
6. 如果仍然 OOM，考虑 `mlp` 重计算。对大型密集模型（Llama3 70B）可节省 ~3 GB，但会降低 ~16% 的 GPU 利用率。
7. 当 PP > 1 时，CPU 卸载会被**阻塞**。

## 启用方式

### 可扩展段（推荐的第一步）

在启动作业的环境变量中设置：

```bash
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```

在 Slurm 脚本中，这通常与其他环境变量一起设置：

```bash
export CUDA_DEVICE_MAX_CONNECTIONS=1
export NVTE_ALLOW_NONDETERMINISTIC_ALGO=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```

无需模型配置更改。零吞吐量成本。

### 并行性调整大小

如果模型确实不适用（非碎片化），则调整并行性：

| 策略 | 内存影响 | 吞吐量成本 | 备注 |
|---|---|---|---|
| 增加 PP（保持 DP） | 每阶段每层更少 | 中等（如果 DP 减半，约 6%） | 仅当 GPU 数量允许时 |
| 增加 TP | 每个 GPU 参数更少 | 严重（70B 上 -28%） | 最后手段 |
| 分布式优化器 | 在 DP 排名间分片优化器状态 | ~1-2% | 推荐用于大型模型 |
| FSDP | 分片参数 + 梯度 + 优化器 | 变化 | 参见 @skills/nemo-mbridge-perf-megatron-fsdp/SKILL.md |

### 激活重计算

有关完整详细信息，请参阅 @skills/nemo-mbridge-perf-activation-recompute/SKILL.md。

### PEFT + 序列并行输入重新收集

对于具有序列并行的 `LoRA` 训练，符合条件的列并行 `linear_qkv` 和 `linear_fc1` 适配器消耗收集的 LayerNorm 输出。由于 LoRA-A 可训练，默认路径会保留完整的收集输入，直到反向传播以获取 LoRA-A 权重梯度。

在构建 PEFT 配置时启用输入重新收集：

```python
from megatron.bridge.peft.lora import LoRA

cfg.peft = LoRA(
    # 在此处保留配方现有的 LoRA 设置。
    sequence_parallel_input_regather=True,
)
```

使用此选项时，正向仍然会临时实现完整输入以进行 LoRA-A GEMM，但 MCore 自动求导仅保留其序列局部片段。反向异步再次收集完整输入，在可能时将集体操作与 dgrad 重叠，计算 LoRA-A 权重梯度，然后重用临时通信缓冲区。

这是一种内存与通信的权衡，而非传统激活检查点：不会重新运行 LayerNorm、注意力、MLP 或 LoRA GEMM。预期会有一些吞吐量下降，且受益于保留的符合条件的 LoRA-A 激活量增加。当序列并行禁用时，此选项无效。

### CPU 卸载

```python
cfg.model.cpu_offloading = True
```

**与 PP > 1 不兼容。** 仅在 `pipeline_model_parallel_size = 1` 时可用。

## 关于 VPP 的说明

虚拟流水线并行（VPP）主要是一种**吞吐量**优化，通过交错较小的模型块来减少流水线气泡开销。它对峰值内存的影响最小——更改 VPP 不会显著改变 GPU 上的总激活、参数或优化器内存。

在早期实验中，我们将 OOM 修复归因于 VPP 调整（VPP 5→10）。实际修复是 `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`，它消除了内存碎片化。VPP=10 的运行实际上使用了略多**峰值内存**（60.2 GB vs 58.8 GB），但由于可扩展段防止了碎片化，因此没有 OOM。

VPP 应用于减少流水线气泡（参见 @docs/parallelisms.md），而非作为内存修复。

## 兼容性和限制

- `expandable_segments:True` 与 `--use-nccl-ub`（NCCL 用户缓冲区注册）不兼容。参见 Megatron-FSDP 文档。
- 使用 `expandable_segments:True` 时，设置 `NCCL_GRAPH_REGISTER=0`（在 Blackwell 之前 GPU 上必需，并由 MCore `CudaGraphManager` 强制）。
- CPU 卸载需要 `pipeline_model_parallel_size = 1`。
- 分布式优化器需要在优化器配置中设置 `use_distributed_optimizer = True`。
- `sequence_parallel_input_regather` 仅适用于符合条件的非专家列并行 LoRA-A 投影。行并行适配器、专家适配器、TP=1、CUDA 图、CPU 激活卸载以及重叠的全层或选择性 MLP 激活重计算会回退到现有路径。

## 测量结果

Llama3 70B SFT 在 32x H100 80GB 上，FP8（当前扩展）：

- 基线：TP=4，PP=4，VPP=5，DP=2，MBS=1，GBS=32，seq_len=4096
- 金色 GPU 利用率：709.93 TFLOP/s/GPU
- 回归阈值：5%

### 策略比较：为减少内存而调整并行性

| 实验 | TP | PP | VPP | DP | TFLOP/s/GPU | vs 金色 | 峰值内存 (GB) | 结果 |
|---|---|---|---|---|---|---|---|---|
| 基线 | 4 | 4 | 5 | 2 | ~704 | -0.8% | 58.8 | OOM（碎片化） |
| 更多 PP | 4 | 8 | 5 | 1 | 668.0 | -5.9% | 53.2 | 边缘性能 |
| 更多 TP | 8 | 4 | 5 | 1 | 508.7 | -28.4% | 50.2 | 严重回归 |
| 基线 + 可扩展段 | 4 | 4 | 5 | 2 | ~704 | -0.8% | ~59 | **通过** |

关键要点：

- **`expandable_segments:True` 是赢家。** 基线 OOM 是由内存碎片化引起的，而非容量不足。设置此环境变量消除了 OOM，且零吞吐量成本，无需并行性更改。
- **PP=8 内存有效但损失 DP**（2→1），意味着每批 32 次梯度累积，这会降低吞吐量约 6%。
- **TP=8 是灾难性的**（-28%），因为 TP 倍增会按比例增加 NVLink 全归约通信量，且 DP=1 意味着无微批处理重叠。

### CPU 卸载：被阻塞

| 实验 | offload_layers | 结果 |
|---|---|---|
| Exp 4 | 2 | 不兼容（PP > 1） |
| Exp 5 | 4 | 不兼容（PP > 1） |
| Exp 6 | 6 | 不兼容（PP > 1） |

`ValueError: Currently there is no support for Pipeline parallelism with CPU
offloading.` 此方法对任何使用 PP > 1 的模型都被阻塞。

### 激活重计算：昂贵的替代方案

选择性激活重计算使用 `mlp` 节省了 ~3 GB 峰值内存，但在此工作负载上成本约为 ~16% 的 GPU 利用率。有关完整结果，请参阅
@skills/nemo-mbridge-perf-activation-recompute/SKILL.md。

### LoRA + SP 输入重新收集

SQuAD 实际检查点 H100 训练显示，在所有测试配置中峰值内存更低，且吞吐量成本取决于工作负载：

| 模型/配置 | 基线峰值 | 输入重新收集峰值 | 节省内存 | 吞吐量变化 |
|---|---:|---:|---:|---:|
| Qwen3-8B, TP2, seq 8192 | 47.545 GB | 42.814 GB | 4.731 GB (10.0%) | -6.74% |
| Qwen3-30B-A3B, TP4/EP4 | 29.890 GB | 28.321 GB | 1.569 GB (5.2%) | -2.89% |
| GPT-OSS-120B, TP2/EP8 | 52.185 GB | 51.371 GB | 0.814 GB (1.6%) | -0.34% |

所有运行都有有限的损失，且没有跳过或 NaN 迭代。双排名 BF16 和 FP32 检查在输出、输入梯度、LoRA-A 和 LoRA-B 梯度以及双微批处理融合 `main_grad` 累积方面与基线匹配。

## 代码锚点

### LoRA 序列并行输入重新收集

```text
src/megatron/bridge/peft/lora.py
    LoRA.sequence_parallel_input_regather

src/megatron/bridge/peft/utils.py
    ParallelLinearAdapter._sequence_parallel_input_regather_eligibility()
    ParallelLinearAdapter.forward()
```

### CPU 卸载 PP 不兼容（MCore）

```1303:1306:3rdparty/Megatron-LM/megatron/core/transformer/transformer_config.py
        if self.cpu_offloading and self.pipeline_model_parallel_size > 1:
            raise ValueError(
                "Currently there is no support for Pipeline parallelism with CPU offloading"
            )
```

### VPP 配置和层可分性验证（MCore）

```1581:1592:3rdparty/Megatron-LM/megatron/core/transformer/transformer_config.py
            if pipeline_parallel_size and self.virtual_pipeline_model_parallel_size is not None:
                num_layers_per_middle_pipeline_rank = num_layers // pipeline_parallel_size
                if (
                    not num_layers_per_middle_pipeline_rank
                    % self.virtual_pipeline_model_parallel_size
                    == 0
                ):
                    raise ValueError(
                        f"number of layers on each middle pipeline rank:"
                        f"{num_layers_per_middle_pipeline_rank} must be divisible by virtual"
                        f"pipeline parallel degree {self.virtual_pipeline_model_parallel_size}"
                    )
```

### 并行性文档关于交错流水线调度

```116:124:docs/parallelisms.md
为最小化流水线气泡，每个 GPU 上的计算可以分成多个层子集（称为模型块），而不是单个连续块。通过设置 `virtual_pipeline_model_parallel_size` 启用此功能：

model_config = GPTModelProvider(
    pipeline_model_parallel_size=4,
    virtual_pipeline_model_parallel_size=2,  # 每个流水线阶段 2 个模型块
    # ... 其他模型参数
)
```

## 失败诊断

| 症状 | 原因 | 确认 | 修复 |
|---|---|---|---|
| 单个排名 OOM 但其他排名有空间 | 内存碎片化 | 检查是否设置 `expandable_segments:True` | 设置 `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` |
| 即使已设置 `expandable_segments` 也 OOM | 真正的容量限制 | 使用 `nvidia-smi` 检查参数/优化器内存 | 增加 PP，使用分布式优化器，或添加重计算 |
| 启动前估计内存超过 GPU 容量 | 模型状态或激活确实太大 | 运行 `estimate_training_memory` 并检查最大组件 | 在启动前调整 PP/TP/CP/EP，分布式优化器，或重计算 |
| LoRA + SP 保留意外高的激活内存 | 完整收集的 LoRA-A 输入直到反向传播才释放 | 检查是否启用 `cfg.peft.sequence_parallel_input_regather` 且目标符合资格 | 设置 `LoRA(sequence_parallel_input_regather=True)`；验证回退约束 |
| `ValueError: PP + CPU offloading` | 使用 PP > 1 的 cpu_offloading | 检查 PP 配置 | 禁用 CPU 卸载或设置 PP=1 |
| `RuntimeError` 与 `--use-nccl-ub` + 可扩展段 | NCCL UB 与可扩展分配器不兼容 | 检查环境变量 | 移除 `expandable_segments:True` 或禁用 `--use-nccl-ub` |

## 已知限制

- 当 PP > 1 时，CPU 卸载被阻塞
- 并行性调整大小（TP/PP）通常有显著的吞吐量成本
- 理论估计器基于公式，不能替代运行时分析或 CUDA 内存报告
- LoRA 输入重新收集不涵盖行并行或专家适配器，且当符合条件的 LoRA-A 激活主导内存时可能无显著益处

## 验证

快速检查 `expandable_segments:True` 是否激活：

```python
import os
assert "expandable_segments:True" in os.environ.get("PYTORCH_CUDA_ALLOC_CONF", "")
```

对于 Slurm 作业，在启动脚本中训练命令之前验证环境变量已导出。

对于 LoRA + SP 输入重新收集，运行聚焦配置测试和实际双排名 MCore 反向奇偶校验测试：

```bash
uv run python -m pytest \
  tests/unit_tests/peft/test_utils.py -k "sequence_parallel_input_regather" \
  tests/unit_tests/peft/test_lora.py -k "sequence_parallel_input_regather"

uv run python -m torch.distributed.run --nproc_per_node=2 -m pytest \
  tests/unit_tests/peft/test_lora_sp_input_regather_distributed.py
```
