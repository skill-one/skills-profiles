# 激活重计算

稳定文档：@docs/training/activation-recomputation.md
卡片：@skills/nemo-mbridge-perf-activation-recompute/card.yaml

<!-- 指导信息更新时间：2026-08-12。 -->

激活重计算（激活检查点）以在反向传播期间增加额外的正向工作为代价，换取更低的保留激活内存。有用的检查点边界取决于模型架构、注意力后端、并行性以及实际驱动每个秩峰的张量。

## 快速决策指南

1. 确认压力是真实的内存分配，而不是分配器碎片。在每个秩上比较 `max_memory_allocated()` 和 `max_memory_reserved()`。
2. 在工作负载适合时保持显式的无重计算控制。在选择性粒度下，`recompute_modules=[]` 是有效的且对此比较有用。
3. 从架构和观察到的峰值选择第一个边界：
   - **标准注意力**：`core_attn` 是常见的第一个候选。它在未融合的注意力生成分数/概率张量时最强。在 Transformer Engine 融合或 Flash Attention 的情况下，将其与 `[]` 进行比较，因为这些后端已经重新生成注意力内部。
   - **多Latent 注意力 (MLA)**：当扩展的 Q/K/V 投影占主导地位时，从 `mla_up_proj` 开始。仅在注意力核心状态仍然重要时才添加 `core_attn`。
   - **分组 MoE**：当专家中间激活占主导地位时，从 `moe_act` 开始；当规范输出是生成时，添加 `layernorm`。在考虑了额外的专家计算和通信开销后，才使用整个 `moe` 重计算。
   - **密集 FFN**：`mlp` 可以保存整个密集-MLP 激活区域，但它通常比窄输出丢弃边界消耗更多计算。
4. 一次改变一个标签。记录每个秩分配/保留的峰值以及稳态步长时间或吞吐量；不要从一个配方推断全局模块排名。
5. 仅当目标选择性边界无法使工作负载适合时，才使用全层重计算。全重计算具有最广泛的内存影响和最大的重放成本。
6. 将 CUDA 图、FP8、上下文并行通信和重叠特性视为兼容性约束，而不是事后想法。

Megatron Core 的 `cpu_offloading=True` 是 PCIe/NVLink 传输开销优于重放计算时的替代方案。它不能与激活重计算结合使用，并且与大于一的流水线并行性不兼容。

## 启用方式

### 选择性重计算

```python
cfg.model.recompute_granularity = "selective"
cfg.model.recompute_modules = ["core_attn"]  # 常见的标准注意力候选，不是通用默认值。
```

使用下面的决策表来替换或扩展 MLA、MoE、密集-MLP 或 GDN 工作负载的列表。

### 全层重计算

```python
cfg.model.recompute_granularity = "full"
cfg.model.recompute_method = "uniform"
cfg.model.recompute_num_layers = 1
```

- `uniform`：检查固定组的 `recompute_num_layers` transformer 层。
- `block`：在每个流水线阶段检查前 `recompute_num_layers` 层，并具有虚拟流水线感知的分布。

## 选择性模块决策表

当前固定的 Megatron Core 接受这些标签。开发分支可以添加特定于模型的标签，因此请针对确切的目标修订版进行验证，而不是跨分支复制列表。

| 模块 | 检查点边界 | 测试时机 | 主要成本或注意事项 |
|---|---|---|---|
| `core_attn` | 核心注意力 | 标准注意力，特别是保留注意力中间件的未融合后端 | 重放注意力。在 TE 融合/Flash Attention 时，增量节省可能很小；上下文并行性可以重放注意力通信。 |
| `mla_up_proj` | MLA Q/KV 上投影加上 RoPE 区域 | 保留扩展 Q/K/V 张量的 MLA 模型 | 重放 MLA 扩展路径。它是 `core_attn` 的一个独特、潜在的附加边界。 |
| `layernorm` | 输入和预-MLP 规范化输出 | 规范化输出对峰值有实质性贡献，通常与 MoE 或 MLA 边界一起出现 | 通常较窄，但节省取决于隐藏大小、序列长度和哪些图路径处于活动状态。 |
| `moe_act` | 分组专家 FC1 和 FC2 之间的激活输出 | 分组 MoE 专家中间激活占主导地位 | 窄输出丢弃检查点。它不会重放调度、FC1 或 FC2，但有 FP8 延迟缩放限制。 |
| `mlp` | 整个密集 MLP | 在用更窄的边界耗尽后，密集层占主导地位 | 重放完整的密集 MLP。它对 MLP 是 MoE 的层没有影响。 |
| `moe` | 整个 MoE 前向 | 必须丢弃一个广泛的 MoE 区域才能使工作负载适合 | 重放路由、调度/组合通信、专家和共享专家工作。它与专家并行重叠不兼容。 |
| `shared_experts` | 非重叠共享专家 MLP | 共享专家是一个独特的实质性峰值 | 重放共享专家 MLP，并且与共享专家重叠无效。外层 `moe` 已经移除了其原始前向保存，但嵌套仍然可以改变瞬态反向重放峰值。 |
| `gdn_norm_out` | GDN 门控规范化输出 | 保留此输出的 GDN/混合模型 | 重放规范化和其 HP 到 CP 全对全路径。 |

例如，DeepSeek V4 配置只能在其所需的 Megatron Core 开发分支上使用模型特定的 `mhc` 标签。它不是固定修订版的可移植标签，因此不包含在上述表格中。

常见的性能配置因此分为几种模式，而不是一个通用列表：

- 标准 Transformer 配方通常使用 `core_attn`；
- MLA 配方通常使用 `mla_up_proj`，有时与 `mlp` 一起使用；
- 分组-MoE 配方通常使用 `moe_act` 或 `layernorm` 加上 `moe_act`；
- 压力更高的 MoE 配方有时使用更广泛的组合，如 `moe` 加上 `layernorm`。

这些是候选模式，不是排序保证。峰值归因和匹配测量决定最终列表。

## 测量契约

对于每个候选，捕获：

- 精确的 Bridge 和 Megatron Core 修订版；
- 模型、序列长度、微/全局批大小、精度、注意力后端和并行性；
- 精确的 `recompute_granularity`、模块列表、方法和层数；
- 每个秩的 `max_memory_allocated()` 和 `max_memory_reserved()`；
- 热身后的稳态步长时间或吞吐量；
- 适合任务的简短收敛或数值健康检查。

使用匹配的无重计算控制，并一次改变一个重计算选择。来自不同作业、后端或并行布局的峰值内存不是模块排名基准。

不要仅仅因为比控制前进得更远就认为候选成功。运行优化器状态初始化和多个稳态步骤：选择性重计算可以将内存墙从正向移动到梯度同步或优化器，而不会使工作负载变得可行。

## 匹配 H100 证据：Moonlight 16B

2026-08-12 的短期研究使用了确切的 Bridge 修订版
`600d069b824dd5ce50367a311a5a3244478faf22` 和 Megatron Core 修订版
`24bad8e677d22625d86ef2a54c9506b6e4992c93`。Moonlight 16B BF16 预训练配方在 8 个 H100 80GB GPU 上运行，序列长度 4096，MBS=1，GBS=4，TP=2，PP=1，CP=1，EP=8，使用模拟数据，并运行 20 步。该模型混合了一个密集层和 26 个 MLA+MoE 层。每一行只改变了
`recompute_modules`；所有 20 个损失都是有限的，没有跳过或 NaN 迭代。

峰值分配内存是迭代 2 后报告的最大优化器值。时间和吞吐量是迭代 11--20 的平均值。

| 选择性模块 | 峰值分配 (GB) | 步长时间 (ms) | TFLOP/s/GPU | 分配与 `[]` 对比 | 时间与 `[]` 对比 |
|---|---:|---:|---:|---:|---:|
| `[]` | 36.618 | 457.18 | 77.50 | 控制 | 控制 |
| `core_attn` | 36.614 | 474.80 | 74.44 | -0.01% | +3.85% |
| `mla_up_proj` | 35.902 | 480.89 | 73.72 | -1.96% | +5.19% |
| `mla_up_proj`, `mlp` | 35.917 | 496.73 | 71.50 | -1.91% | +8.65% |
| `moe_act` | 35.941 | 466.26 | 75.50 | -1.85% | +1.99% |
| `layernorm`, `moe_act` | 35.949 | 506.53 | 70.27 | -1.83% | +10.79% |

对于这个确切的工作负载，`moe_act` 是最好的第一个边界：它几乎与 `mla_up_proj` 一样多地恢复了分配内存，但重放成本更低。如果它的大约 39 MB 额外减少很重要，`mla_up_proj` 是下一个候选。将 `mlp` 添加到 `mla_up_proj` 或将 `layernorm` 添加到 `moe_act` 没有改善观察到的峰值，并且使步骤变慢。显式的 `core_attn` 增加了成本，但在融合注意力下没有实质性的内存收益。

最大保留内存保持在 40 GB 左右，并且没有单调下降。这是分配器缓存，而不是相反的证据：本研究的边界选择基于分配内存和成功的端到端步骤。

## 匹配 H100 证据：Nemotron 3 Nano

相同的 2026-08-12 研究 使用了原生 16-H100 BF16 性能配方用于 52 层混合 Mamba/融合注意力 MoE 模型。匹配的短期运行配置使用了序列长度 8192，MBS=1，GBS=16，TP=1，PP=1，CP=1，EP=8，DP=16，专家-DP=2，HybridEP，分组 GEMM，TE CUDA 图用于注意力和 Mamba，模拟数据，并运行 12 步。每个行只改变了 `recompute_modules`。

| 选择性模块 | 结果 | 秩 0 测量峰值 | 失败或稳态证据 |
|---|---|---:|---|
| `[]` | OOM 在迭代 1 后 | 迭代 1 后 66.297 GB | 迭代 2 MoE 路由器分配失败；热秩大约有 72.9 GiB 分配。 |
| `core_attn` | OOM 在迭代 1 中 | 不具可比性 | 分组专家线性分配失败；显式注意力重计算并没有使融合注意力工作负载变得可行。 |
| `moe_act` | OOM 在迭代 1 后 | 迭代 1 后 62.103 GB | 在匹配的检查点处比控制低 4.194 GB (6.33%)，但迭代 2 的输出投影仍然需要 2 GiB。 |
| `layernorm`, `moe_act` | OOM 在迭代 1 中 | 不具可比性 | 输出投影仍然需要 2 GiB；CUDA 图的私有池是实质性的。 |
| `moe` | 完成 12 步 | 迭代 2 后 64.653 GB | 迭代 7--12 上的 657.42 ms 和 277.72 TFLOP/s/GPU。 |
| `moe`, `layernorm` | 完成 12 步 | 迭代 2 后 63.639 GB | 迭代 7--12 上的 677.62 ms 和 270.62 TFLOP/s/GPU。 |

两个成功的行都有有限的损失，没有跳过或 NaN 迭代。
对于这个确切的能力限制配方，全-`moe` 重计算是最小测试的通过边界。添加 `layernorm` 恢复了 1.014 GB (1.57%) 的秩 0 峰值，但步长时间提高了 3.07%，因此当需要这种裕度时，配方的更广泛组合是合理的。窄 `moe_act` 产生了真实的激活缓解，但并没有使整个训练步骤变得可行。

探索性的原生 8-H100 布局在序列长度 4096 时甚至在 FP32 优化器状态初始化时也失败。这是优化器容量，而不是选择性边界吞吐量基线；不使用这些运行的计时比较。

### 跨模型结论

这些测量没有定义一个排名。Moonlight 使用空控制适配，并偏爱窄 `moe_act`；Nemotron 需要全 `moe` 重计算；历史密集 Llama 证据发现全 `mlp` 重放成本高昂且缺乏空控制。因此，正确的第一个候选是最窄的由架构和峰值暗示的边界，仅在窄选择不通过完整步骤时才进行更广泛的重放。

## 兼容性和验证

### 配置语义

- `recompute_granularity="selective"` 使用 `recompute_modules`；空列表被接受为显式控制。
- `recompute_granularity="full"` 使用 `recompute_method` 和 `recompute_num_layers`；选择性标签不适用。
- 全重计算优先于选择性模块选择，而不是与它们组合。
- 未知标签会导致 Megatron Core 验证失败。标签可能在开发分支上不同，因此请使用确切修订版的 `TransformerConfig` 验证器作为事实来源。

### 注意力后端和上下文并行性

- TE 融合和 Flash Attention 已经使用内部重新生成。显式的 `core_attn` 可能仍然改变保留的输入/输出，但它必须在匹配的 `[]` 比较中证明其价值。
- 在上下文并行性下，注意力检查点可以重放通信以及计算。在测量记录中包含 CP 大小和拓扑。

### MoE 限制

- 全-`moe` 重计算与专家并行重叠不兼容，因为反向重放会重复重叠的调度/通信区域。
- `shared_experts` 重计算与共享专家重叠不兼容。
- `moe_act` 适用于分组-GEMM 专家，并且当只需要丢弃专家激活时是更窄的选择。
- `mlp` 针对密集 MLP，并在 MoE 层上无操作；混合密集/MoE 模型仍然可以通过其密集层受益。

### FP8 限制

- `moe_act` 和 `layernorm` 重计算不支持 FP8 延迟缩放，并需要兼容的 Transformer Engine 版本。
- 吸收的 MLA 路径有额外的 FP8/FP4 限制。在选择 `mla_up_proj` 之前，请验证确切的模型/提供者路径。

### CUDA 图

- 仅当检查点的模块完全位于或完全位于选定的图范围内时，选择性重计算才有效。跨越图边界的检查点边界无效。
- 捕获/热身可以绕过检查点包装器，因此请验证最终图范围和重放路径，而不是假设急性能会延续。
- 使用 CUDA 图的全重计算需要在固定的 Megatron Core 中设置 `cuda_graph_impl="full_iteration"`。否则禁用 CUDA 图；作用域/本地图捕获不能在此处替代全迭代捕获。

## 历史测量：背景，而非模块排名

来自 Bridge PR #3107 的历史 H100 测量使用了 32 个 H100 80GB GPU 上的 Llama 3 70B SFT，FP8 当前缩放，序列长度 4096，微批大小 1，全局批大小 32，TP=4，PP=4，VPP=5，DP=2：

| 配置 | TFLOP/s/GPU | 峰值内存 |
|---|---:|---:|
| 该运行中的 `core_attn` 基线 | ~704 | 58.8 GB (秩 0 OOM) |
| `mlp` | 593.6 | 55.6 GB |
| `mlp` + `core_attn` | 586.8 | 55.6 GB |
| `core_attn` + `layernorm` | ~702 | 59.6 GB (秩 0 OOM) |
| PR 上下文中记录的黄金吞吐量 | 709.93 | 不是配对的模块仅比较 |

此证据的局限性：

- 它没有包含匹配的无重计算行；
- 黄金行不是模块仅比较；
- 测量覆盖一个密集 Llama 工作负载，而不是 MLA 或 MoE；
- 表格仅支持本地内存/吞吐量权衡，不得用于排名所有重计算标签。

## 代码锚点

- 选择性标签验证和跨功能检查：`3rdparty/Megatron-LM/megatron/core/transformer/transformer_config.py`
- 检查点实现：`3rdparty/Megatron-LM/megatron/core/tensor_parallel/random.py`
- 标准注意力检查点边界：`3rdparty/Megatron-LM/megatron/core/transformer/attention.py`
- MLA 上投影边界：`3rdparty/Megatron-LM/megatron/core/transformer/multi_latent_attention.py`
- Layernorm、密集-MLP 和外层-MoE 位置：`3rdparty/Megatron-LM/megatron/core/transformer/transformer_layer.py`
- 分组专家激活边界：`3rdparty/Megatron-LM/megatron/core/transformer/moe/experts.py`
- 共享专家和全-MoE 路径：`3rdparty/Megatron-LM/megatron/core/transformer/moe/moe_layer.py`
- GDN 规范化边界：`3rdparty/Megatron-LM/megatron/core/ssm/gated_delta_net/gdn.py`

## 故障诊断

| 症状 | 可能原因 | 下一步操作 |
|---|---|---|
| `core_attn` 几乎没有或没有峰值减少 | 融合/Flash 注意力已经重新生成昂贵的内部，或者峰值在别处 | 与 `[]` 对比，归因峰值，然后测试架构特定的边界，例如 `mla_up_proj` 或 `moe_act`。 |
| MLA 在 `core_attn` 后仍然 OOM | 扩展的 Q/K/V 投影张量，而不是注意力核心张量，占主导地位 | 测试 `mla_up_proj`；仅在匹配证据支持时才添加 `core_attn`。 |
| MoE 峰值仍然很高 | 专家中间或规范输出占主导地位 | 测试 `moe_act`，然后 `layernorm`；在需要更广泛压力时保留全 `moe`。 |
| 专家重叠验证失败 | 全-`moe` 或 `shared_experts` 重计算与重叠冲突 | 保持重叠并使用兼容的内部边界，或禁用重叠并重新测量整个配置。 |
| 一个选定的标签没有可测量的效果 | 该模块在测量层上不存在或未激活，或者图捕获绕过了包装器 | 检查提供者/层混合和最终图范围；例如，`mlp` 在纯 MoE 层上无效。 |
| 全重计算加上 CUDA 图断言 | 图实现不是全迭代 | 设置 `cuda_graph_impl="full_iteration"` 或禁用 CUDA 图。 |
| 保留内存很高但分配内存稳定 | 分配器碎片或缓存 | 在添加重计算之前尝试 `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`。 |
| 启用重计算后 OOM 移动到不同秩 | 流水线/虚拟流水线层分布改变了瓶颈 | 比较每个秩峰值，并调整全块/统一放置或选择性边界以适应实际热阶段。 |
| 一个候选前进得更远但仍然 OOM | 重计算将峰值移动到梯度同步或优化器状态初始化 | 将改变的失败阶段记录为诊断证据，但在调用通过之前需要优化器初始化和多个稳态步骤。 |

## 已知局限性

- 模块列表不能跨模型系列、注意力后端、并行布局或 Megatron Core 修订版移植。
- 当边界重叠或嵌套时，内存节省是非线性的；加法算术不可靠。
- 全重计算改变了 RNG 执行路径；dropout 工作负载需要数值/收敛检查。
- 激活重计算不解决参数、优化器状态或分配器碎片压力。
- 正确的结果是最小测量的重放成本，可以满足每个秩内存目标，而不是最长的模块列表。

## 进一步阅读

- `docs/performance-guide.md`
- `skills/nemo-mbridge-perf-memory-tuning/SKILL.md`
- `skills/nemo-mbridge-perf-cuda-graphs/SKILL.md`
- `skills/nemo-mbridge-perf-cpu-offloading/SKILL.md`
- Megatron Core 激活重计算指南：<https://docs.nvidia.com/megatron-core/developer-guide/latest/api-guide/index.html>
