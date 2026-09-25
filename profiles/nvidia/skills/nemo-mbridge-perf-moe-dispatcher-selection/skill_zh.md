# MoE 分发器选择指南

稳定文档：@docs/training/moe-optimization.md
卡片：@skills/nemo-mbridge-perf-moe-dispatcher-selection/card.yaml

## 快速决策

### 按硬件

| 硬件 | 首选 | 原因 |
|---|---|---|
| H100 | DeepEP，如果安装了运行时包 | 在 Hopper 上跨节点 EP 的强默认选项 |
| B200 | DeepEP，如果安装了运行时包 | 除非有平台特定的 HybridEP 路径，否则是好的首选选项 |
| GB200 / GB300 NVL72 | HybridEP，如果安装了运行时包 | 最适合 NVLink 域感知分发和较低内存压力 |
| 未知或首次启动 | `alltoall` | 最容易的正确性和调试路径 |

### 按EP程度

| EP大小 | 指导 |
|---|---|
| 小EP | 分发器选择通常是次要的；从 `alltoall` 或 DeepEP 开始 |
| 中等EP | DeepEP 通常变得值得 |
| 大EP | 在 NVL72 系统上，HybridEP 通常是最佳目标 |

## 模型系列模式

| 工作负载 | 常见的最佳路径 | 备注 |
|---|---|---|
| DSV3 在大规模下 | GB200 或 GB300 上的 HybridEP，H100 上的 DeepEP | 随着EP和PP都增长，分发器选择变得更加重要 |
| Qwen3 235B | H100 上的 DeepEP，GB200 上的 HybridEP | HybridEP 通常在 GB200 上获胜，并且经常使用更少的内存 |
| Qwen3 30B | DeepEP | 较小的模型仍然受益，但绝对差距较小 |
| Qwen3-Next | BF16 中接近，FP8 或内存紧张运行中 HybridEP 更强 | 提醒测试，不要假设 |
| MoE VLMs | 先从简单开始，然后在 GB200 级系统上测试 HybridEP | 视觉工作负载对内存和主机开销都很敏感 |

## 圆整证据摘要

### 后端可用性门

在容器证明所选后端包可用之前，不要解释分发器时间。`--moe_flex_dispatcher_backend None` 选择标准的 `alltoall` 分发器，而 `deepep` 和 `hybridep` 选择 `moe_token_dispatcher_type="flex"`，然后在模型构建时需要它们相应的运行时包。如果 DeepEP 或 HybridEP 缺失，将导入失败记录为环境限制，并将 `alltoall` 视为该运行中唯一测量的正确性回退。

### Qwen3 30B A3B 在 H100 上

一个简短的 2026-05-17 H100 烟雾运行使用了 Qwen3 30B A3B BF16，16 个 GPU，EP=16，食谱的 Transformer Engine CUDA 图范围 (`moe_router`，`moe_preprocess`)，并且由于运行容器中的 Triton JIT 兼容性问题，`model.moe_permute_fusion=false`。`alltoall` 回退在预热后完成了五步，平均每步时间为 45.65 秒，预热后平均 TFLOP/s/GPU 为 132.9，最终损失 11.44050，峰值最大分配内存为 61.351 GB。DeepEP 和 HybridEP 在转储的配置中选择了请求的 flex 后端，但在第一次迭代之前就失败了，因为包没有安装。这证实了可用性门；它不是 H100 上 flex 分发器的吞吐量排名。

### DSV3 在 GB200 或 GB300 上

总体趋势比跟踪器中的任何单行都更重要：

- 纯 `alltoall` 通常是保守的基线
- 一旦 EP 通信变得可见，DeepEP 就会改善该基线
- HybridEP 在 NVL72 系统上增加了另一个步骤，尤其是在 CUDA 图、路由改进和 CPU 端清理已经就绪之后

实际上，堆栈通常从大约“十几 MFU”区域（未调优的基线）移动到“十几到二十几 MFU”区域（在完整的分发器和内核堆栈调优后）

### Qwen3 235B 在 GB200 上

对于 Qwen3 235B，实际顺序通常是：

1. `alltoall` 用于初始启动
2. 如果你想一个熟悉的调优路径，DeepEP
3. GB200 上的 HybridEP 以获得最强的稳态结果

HybridEP 在此工作负载上通常比 `alltoall` 稍快，并且通常具有明显更好的内存余量。

### Qwen3-Next 在 GB200 上

这个系列是一个很好的提醒，分发器胜利是依赖于工作负载的：

- 在 BF16 中，`alltoall` 和 HybridEP 可以很接近
- 在 FP8 或内存受限设置中，HybridEP 往往看起来更好
- 管道布局和分组 GEMM 变化几乎与分发器本身一样重要

## 调整参数

### DeepEP

通过设置 `moe_token_dispatcher_type="flex"` 和 `moe_flex_dispatcher_backend="deepep"` 选择 DeepEP。

```bash
--moe-deepep-num-sms 20
```

调整分配给 DeepEP 通信内核的 SM 数（默认 20）。最佳值取决于工作负载和 EP 程度。
首先确认目标容器中 DeepEP 包的导入；缺少包会在模型构建期间失败，在出现任何分发器时间之前。

### HybridEP

通过设置 `moe_token_dispatcher_type="flex"` 和 `moe_flex_dispatcher_backend="hybridep"` 选择 HybridEP。

```bash
--moe-hybridep-num-sms 16
```

调整分配给 HybridEP 通信的 SM 数（默认 16）。性能 harness 使用 32 用于 HybridEP 工作负载。在目标硬件上扫描 16 到 32。将 `NUM_OF_HYBRID_EP_RANKS_PER_NVLINK_DOMAIN` 设置为匹配部署的 NVLink 域大小。如果它与实际拓扑不匹配，性能有时甚至正确性都会受到影响。
首先确认目标容器中 HybridEP 包的导入；缺少包会在模型构建期间失败，在出现任何分发器时间之前。

### 路由模式

```bash
--moe-router-force-load-balancing
```

对于性能基准测试，强制平衡路由是更安全的默认值。它在大型基准测试中通常优于无丢弃路由，并使结果在不同分发器后端之间更具可比性。

## 关键交互

| 功能 | 交互 |
|---|---|
| CUDA 图 | 与 `attn moe_router moe_preprocess` 在无丢弃 MoE 上最佳配合 |
| EP 重叠 | 当分发器时间在后台调优后仍然可见时有助于 |
| FP8 | 通常会增加通信和主机开销的相对重要性 |
| CPU 亲和力 | 在 GB200 或 GB300 上可能与分发器选择一样重要 |
| 管道布局 | 差的 PP 或 VPP 布局可能会消除分发器收益 |

## 每个何时使用

### `alltoall`

- 首次正确性启动
- 小 EP 配置
- 调试通信回归

### DeepEP

- Hopper 或 B200 部署
- 跨节点 EP 在分析中明显可见
- 你想在测试 HybridEP 之前有一个成熟的中间步骤

### HybridEP

- GB200 或 GB300 NVL72 系统
- 大 EP 程度
- 除了吞吐量外，内存余量也很重要

## 陷阱

1. **不要在不同堆栈上比较分发器**：容器、路由模式、PP 布局和 CUDA 图范围可能移动结果与分发器一样多。

2. **HybridEP 对拓扑敏感**：在为其设计的硬件之外，它不是普遍的胜利。

3. **两个分发器都需要 SM 调整**：默认 `moe_deepep_num_sms` (20) 和 `moe_hybridep_num_sms` (16) 是合理的起点，但很少是最佳值。

4. **强制平衡和无丢弃不是可互换的基线**：在比较分发器后端时保持路由模式固定。

5. **内存和吞吐量可能通过模型不同地权衡**：Qwen3 风格的运行可能显示较小的速度差异，但仍然证明 HybridEP 对内存余量是合理的。

6. **后端导入失败不是性能数据**：如果容器中缺少 DeepEP 或 HybridEP，不要将其失败的作业与完成的 `alltoall` 作业进行比较。首先修复环境，然后重新运行相同的堆栈。
