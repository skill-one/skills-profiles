# 并行策略选择技巧

有关每种并行类型的稳定背景知识，请参阅：

- @docs/parallelisms.md
- @skills/nemo-mbridge-perf-parallelism-strategies/card.yaml

## 按模型大小决策

### 密集模型

| 模型大小 | GPU数量 | 推荐起始点 |
|---|---|---|
| < 1B | 1-8 | 仅DP |
| 1-10B | 8-16 | TP=2-4 + DP |
| 10-70B | 16-64 | TP=4-8 + PP=2-4 + DP |
| 70-175B | 64-256 | TP=8 + PP=4-8 + DP |
| 175-500B | 256-1024 | TP=8 + PP=8-16 + CP=2 + DP |

### MoE模型

MoE并行与密集模型不同。由于每个token只有部分参数是活跃的，TP通常可以保持在1或2——活跃的参数分片已经可以适应单个GPU。EP是主要的扩展维度，PP处理跨节点的层分布。

| 模型（总数/活跃） | TP | PP | EP | 备注 |
|---|---|---|---|---|
| OLMoE 7B / 1B | 1 | 1 | 8 | 仅EP，适合单个节点 |
| Moonlight 16B / 3B | 2 | 1 | 8 | 小TP用于共享层 |
| DeepSeek-V2 236B / 21B | 1 | 4 | 32 | 完全没有TP |
| GLM-4.5 Air 106B / 12B | 1 | 4 | 8 | 完全没有TP |
| Qwen3 30B-A3B | 4 | 2 | 4 | |
| GLM-4.5 355B / 32B | 2 | 8 | 16 | |
| Qwen3 235B-A22B | 4 | 16 | 8 | 预训练时CP=2 |
| DeepSeek-V3 671B / 37B | 2 | 16 | 64 | TP=2，不是8 |
| Kimi-K2 1T | 2 | 16 | 32 | |

关键模式：

- TP的大小由**活跃**参数决定，而不是总参数。一个671B的MoE模型，如果只有37B活跃参数，需要的TP远少于一个70B的密集模型。
- EP随专家数量扩展。常见：EP = num_experts 或 num_experts / experts_per_gpu。
- PP处理深度。大型MoE模型在节点间使用PP=8-16。
- ETP（专家张量并行）很少使用。Llama 4是一个例外（ETP=4）。

这些都是起点，不是硬性规则。始终分析第一次迭代的内存和通信情况以验证。

## 按硬件拓扑决策

单节点使用NVLink：

```python
cfg.model.tensor_model_parallel_size = 8
```

多节点使用InfiniBand：

```python
cfg.model.tensor_model_parallel_size = 8
cfg.model.pipeline_model_parallel_size = N
```

有限网络（以太网）：

```python
cfg.model.tensor_model_parallel_size = 4
cfg.model.pipeline_model_parallel_size = M
```

稳定规则是：保持TP在单个NVLink域内。使用PP或DP进行跨节点扩展。跨节点的TP几乎总是性能损失。

## 按序列长度决策

| 序列长度 | 建议 |
|---|---|
| < 2K | 标准TP + PP + DP |
| 2K-8K | 添加SP (`sequence_parallel=True`) |
| 8K-32K | 添加CP=2 |
| 32K+ | 添加CP=4-8，考虑`a2a+p2p`用于大型CP |

## 组合并行启用

3D并行（TP + PP + DP）：

```python
cfg.model.tensor_model_parallel_size = 4
cfg.model.pipeline_model_parallel_size = 4
cfg.model.sequence_parallel = True
```

4D并行（TP + PP + CP + DP）：

```python
cfg.model.tensor_model_parallel_size = 8
cfg.model.pipeline_model_parallel_size = 8
cfg.model.context_parallel_size = 2
cfg.model.sequence_parallel = True
```

MoE使用EP + PP（例如DeepSeek-V2 236B在128个GPU上）：

```python
cfg.model.tensor_model_parallel_size = 1
cfg.model.pipeline_model_parallel_size = 4
cfg.model.expert_model_parallel_size = 32
cfg.model.sequence_parallel = False
```

MoE使用小TP + PP + EP（例如DeepSeek-V3 671B在256个GPU上）：

```python
cfg.model.tensor_model_parallel_size = 2
cfg.model.pipeline_model_parallel_size = 16
cfg.model.expert_model_parallel_size = 64
cfg.model.sequence_parallel = True
```

DP大小始终是隐式的：

```
data_parallel_size = world_size / (TP * PP * CP)        # 密集路径
expert_data_parallel_size = world_size / (PP * EP * ETP) # MoE路径
```

## 最小GPU数量

运行配置所需的**最小**GPU数量（即`DP=1`，`EDP=1`）**不是**所有并行维度乘积。密集路径使用`TP*CP`-网格，MoE路径使用`EP*ETP`-网格，在每个PP阶段，这两个网格共享相同的GPU集——它们重叠，而不是相乘。只有PP阶段相乘（它们是模型的独立切片）。所以：

```
min_gpus = PP * max(TP * CP, EP * ETP)
```

**常见简化（错误）**：`PP * TP * CP * EP * ETP`。这会过度分配GPU，并在许多README和slurm尺寸表中出现。不要传播它。

注意力与MoE并行的解耦（密集路径和专家路径使用不同的网格形状共享相同的PP阶段GPU）的细节在
[Pangu Ultra MoE (arXiv:2504.14960)](https://arxiv.org/pdf/2504.14960)中有详细说明。

### 示例

| 配置 | 错误 (PP·TP·CP·EP·ETP) | 正确 (PP·max(TP·CP, EP·ETP)) |
|---|---|---|
| PP=1, TP=2, CP=1, EP=8, ETP=1 | 16 | **8** (1节点) |
| PP=1, TP=4, CP=1, EP=8, ETP=1 | 32 | **8** (max(4, 8)) |
| PP=1, TP=2, CP=2, EP=8, ETP=1 | 32 | **8** (max(4, 8)) |
| PP=1, TP=2, CP=4, EP=8, ETP=1 | 64 | **8** (max(8, 8)) |
| PP=2, TP=2, CP=1, EP=8, ETP=1 | 32 | **16** (2 · max(2, 8)) |
| PP=1, TP=2, CP=1, EP=4, ETP=2 | 16 | **8** (max(2, 8)) |

### 超过最小规模的扩展

增加GPU扩展`DP`和/或`EDP`（`world_size`必须同时满足这两个方程）。在`min_gpus`时，较大网格侧的DP（或EDP）= 1，较小侧吸收剩余部分。

示例——TP=2, CP=1, EP=8, ETP=1, PP=1：

- **8 GPUs** (`min_gpus`)：密集`DP = 8/2 = 4`，MoE `EDP = 8/8 = 1`
- **16 GPUs**：密集`DP = 8`，MoE `EDP = 2` → 2×全局批次
- **32 GPUs**：密集`DP = 16`，MoE `EDP = 4` → 4×全局批次

在调整slurm脚本时，根据`min_gpus`（或其倍数以通过DP/EDP实现更高吞吐量）计算`--nodes`。

在回答MoE规模提示时，包含此清单：

- 使用请求值计算`min_gpus = PP * max(TP * CP, EP * ETP)`
- 明确拒绝错误的`PP * TP * CP * EP * ETP`完整乘积
- 给出两个DP公式：密集`world_size / (TP * PP * CP)`和MoE `world_size / (PP * EP * ETP)`
- 提及TP拓扑、SP、CP可整除性以及长序列CP指导

## 内存估计

无并行（70B模型，FP16）：

```
参数：       140 GB
梯度：        140 GB
优化器状态： 280 GB (Adam)
激活值：       48 GB (batch=1, seq=4K)
总计：            608 GB
```

使用TP=4, PP=4, DP=4（64个GPU）：

```
参数：        8.75 GB/每GPU
梯度：         8.75 GB/每GPU
优化器状态： 17.50 GB/每GPU
激活值：       3.00 GB/每GPU
总计：        ~38    GB/每GPU
```

## 代码锚点

在模型提供者中设置并行维度：

```66:81:docs/parallelisms.md
model_config = GPTModelProvider(
    tensor_model_parallel_size=2,
    # ...其他模型参数
)
```

DP大小计算：

```424:436:docs/parallelisms.md
data_parallel_size = world_size / (tensor_model_parallel_size × pipeline_model_parallel_size × context_parallel_size)
```

桥接初始化将并行性引入进程组：

```618:628:src/megatron/bridge/training/initialize.py
parallel_state.initialize_model_parallel(
    tensor_model_parallel_size=model_config.tensor_model_parallel_size,
    pipeline_model_parallel_size=model_config.pipeline_model_parallel_size,
    ...
    context_parallel_size=model_config.context_parallel_size,
    hierarchical_context_parallel_sizes=model_config.hierarchical_context_parallel_sizes,
    expert_model_parallel_size=model_config.expert_model_parallel_size,
    ...
)
```

## 陷阱

1. 跨节点的TP会破坏吞吐量。始终将TP保持在单个NVLink域内。

2. 无交错功能的PP会产生大的流水线气泡。尽可能使用`virtual_pipeline_model_parallel_size`。

3. SP需要`tensor_model_parallel_size > 1`。单独启用SP而不启用TP是配置错误。

4. CP需要`seq_length % (2 * context_parallel_size) == 0`。

5. EP仅用于MoE模型。在密集模型上设置`expert_model_parallel_size`是无操作或错误。

6. 上述模型大小到并行性的表格是一个起始启发式。始终分析第一次迭代以检查内存和通信。

7. `CUDA_DEVICE_MAX_CONNECTIONS`和相关环境变量与重叠设置相互作用。参见@skills/nemo-mbridge-perf-tp-dp-comm-overlap/SKILL.md。

8. MoE配置的最小GPU数量是`PP * max(TP*CP, EP*ETP)`，而不是所有维度的乘积。密集`TP*CP`-网格和MoE `EP*ETP`-网格在每个PP阶段共享相同的GPU。参见上述“最小GPU数量”部分。

## 验证

使用具有覆盖并行性的最小可用配方进行快速合理性检查，以确保组合并行正确初始化：

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 uv run python -m torch.distributed.run --nproc_per_node=4 \
  scripts/training/run_recipe.py \
  --recipe llama32_1b_pretrain_config \
  model.tensor_model_parallel_size=2 \
  model.pipeline_model_parallel_size=2 \
  model.sequence_parallel=True \
  train.train_iters=3 train.global_batch_size=8 train.micro_batch_size=1 \
  scheduler.lr_warmup_iters=0 \
  validation.eval_iters=0 validation.eval_interval=0 \
  checkpoint.save_interval=0 \
  logger.log_interval=1
```

成功标准：

- 退出码0
- 迭代3处的有限损失（例如`lm loss: 1.003808E+01`）
- 日志显示TP=2 PP=2 DP=1布局，4个rank
