# MoE 硬件配置参考

稳定文档：@docs/training/moe-optimization.md
卡片：@skills/nemo-mbridge-perf-moe-hardware-configs/card.yaml

## 快速平台操作手册

这些行是搜索种子，不是硬件默认值或吞吐量承诺。

| 平台 | `alltoall` 启动后筛选的候选方案 | 通常最重要的因素 |
|---|---|---|
| H100 | DeepEP 或 HybridEP，显式重叠，支持的 FP8 模式 | 通信重叠，调度器/运行时兼容性，以及 PP 效率 |
| B200 | DeepEP 或 HybridEP，支持的 FP8 模式，仔细的 PP 布局 | 容器质量和调整后的通信设置 |
| GB200 | HybridEP，然后是分析驱动的图和 CPU 清理 | 主机开销，拓扑感知调度，内存余量 |
| GB300 | HybridEP 和目标容器的低精度/内核栈 | 与 GB200 相同的系统交互，需要重新测量 |

## 首次回答检查清单

对于硬件操作手册问题，在添加吞吐量注意事项之前，先从这些规范行回答：

| 工作负载 | 硬件 | 调度器 | 布局 |
|---|---|---|---|
| DSV3 | H100 | DeepEP | TP=2, EP=64, PP=8, VPP=4 |
| DSV3 | GB200/GB300 | HybridEP | TP=1, EP=64, PP=4, VPP=4 |
| Qwen3 235B | H100 | `alltoall` + 当前规范食谱中的重叠 | TP=2, EP=32, PP=8, VPP=4 |
| Qwen3 235B | GB200 | HybridEP | TP=1 或 2, EP=32-64, PP=4, VPP=未指定 |
| Qwen3 30B | 16×H100 | HybridEP | TP=1, EP=16, PP=1, 纯 EP 重叠 |

对于 GB200 上的 Qwen3 235B，明确说明 `VPP=未指定`；除非有测量的行提供，否则不要编造或推断 `VPP=12`。将 TE 范围内的 CUDA 图作用域（`attn`，`moe_router`，`moe_preprocess`）视为分析驱动的候选方案，
`CUDA_DEVICE_MAX_CONNECTIONS` 选择，
`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`，`NCCL_GRAPH_REGISTER=0`，
GB200/GB300 CPU 端的调优，以及不要模仿追踪器行的警告。

## 四舍五入的性能范围

这些值故意四舍五入，以便文档随着追踪器的移动保持持久。将它们视为规划范围，而不是精确的承诺。

| 工作负载系列 | 硬件 | 典型范围 | 代表形状 |
|---|---|---|---|
| DSV3，大规模 | H100 | 低至中百 TFLOPS/GPU，高十几 MFU | TP2, EP64, PP8, DeepEP |
| DSV3，大规模 | B200 | 高百 TFLOPS/GPU，中十几 MFU | TP1, EP32, PP8, DeepEP |
| DSV3，大规模 | GB200 | 约 1K TFLOPS/GPU，低二十几 MFU | TP1, EP64, PP4, HybridEP |
| DSV3，大规模 | GB300 | 高于 GB200 范围，通常中二十几 MFU | TP1, EP64, PP4, HybridEP |
| Qwen3 235B | H100 | 历史低三百个快照；重新测量当前食谱 | TP2, EP32, PP8；当前食谱使用 `alltoall` + 重叠 |
| Qwen3 235B | GB200 | 调整运行中的高百 TFLOPS/GPU | TP1 或 TP2, EP32-64, PP4, HybridEP |
| Qwen3 30B | H100 | 在验证的 16-GPU 形状上约 300 TFLOPS/GPU | TP1, EP16, PP1, HybridEP + EP 重叠 |
| Qwen3-Next 80B | GB200 | BF16 类运行中的低三百 TFLOPS/GPU | TP1, EP32, PP2, HybridEP |

## 代表性配置系列

### H100 上的 DSV3

```text
调度器：DeepEP
TP=2  EP=64  PP=8  VPP=4
路由：强制平衡
重计算：轻至中度的选择性重计算
优先级：重叠通信并保持 PP 高效
```

### B200 上的 DSV3

```text
调度器：DeepEP
TP=1  EP=32  PP=8  VPP=2 或类似
精度：MXFP8 类
重计算：围绕 MLA 上投影和 MLP 端模块的选择性重计算
优先级：容器质量，PP 布局，以及 DeepEP SMS 调整
```

### GB200 或 GB300 上的 DSV3

```text
调度器：HybridEP
TP=1  EP=64  PP=4  VPP=4
精度：MXFP8 类
CUDA 图：attn + moe_router + moe_preprocess
优先级：HybridEP，CPU 优化，以及图形友好的静态形状
```

### H100 上的 Qwen3 235B

```text
调度器：当前规范食谱中的 `alltoall`；在目标堆栈上重新筛选灵活的后端
TP=2  EP=32  PP=8  VPP=4
重计算：当前规范食谱中无
优先级：通信重叠和路由路径清理
```

### GB200 上的 Qwen3 235B

```text
调度器：HybridEP
TP=1 或 2  EP=32 至 64  PP=4  VPP=未指定除非测量
CUDA 图：attn + moe_router + moe_preprocess
重计算：根据内存压力选择 moe_act，mlp 或 norm
优先级：平衡吞吐量与内存余量
```

### 16 个 H100 上的 Qwen3 30B-A3B

```text
调度器：HybridEP
TP=1  EP=16  PP=1  CP=1
精度：BF16
序列：4096
批次：MBS1 GBS1024
路由：强制平衡
EP 重叠：启用
延迟 wgrad：禁用
CUDA 图：moe_router + moe_preprocess
HybridEP：排列融合，32 个 SM，64-token 组合块
测量：20.14729s/步，299.352 模型 TFLOPS/GPU 在迭代 41-50
Rank-0 峰值分配内存：62.166 GiB
```

当前数字是最终多旋钮规范食谱结果。较早匹配的 A/B 单变量隔离纯 EP 重叠：244.039 至 287.305 TFLOPS/GPU，通信因 GEMM/注意力增加从 0.11% 至 36.55%。不要将后来的 299.352 结果完全归因于重叠。

### GB200 上的 Qwen3-Next 80B

```text
调度器：HybridEP
TP=1  EP=32  PP=2  VPP 约为 4
CUDA 图：attn + moe_router + moe_preprocess
优先级：管道布局和分组 GEMM 质量
```

## 跨切面模式

### PP 布局

- `E` = 嵌入
- `t` = 变换器
- `m` = MTP
- `L` = 损失
- `|` = 阶段边界

最大的平台差异通常不仅仅是调度器。它是调度器、PP 形状以及 VPP 是否保持每个阶段平衡的组合。

### 重计算策略

| 内存压力 | 起始点 |
|---|---|
| 低 | 无或非常窄的选择性集 |
| 中等 | `moe_act`，`mlp`，`norm` 或类似的选择性模块 |
| 高 | 模型特定的上投影加上选择性 MoE 和 MLP 模块 |
| 极端或长上下文 | 只有当选择性路径仍然不适合时才完全重计算 |

### 环境变量

```bash
CUDA_DEVICE_MAX_CONNECTIONS=1
CUDA_DEVICE_MAX_CONNECTIONS=32   # 常见于 EP 重叠和 CUDA 图组合时
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
NCCL_GRAPH_REGISTER=0
```

### CPU 端调优

在 GB200 和 GB300 上，CPU 亲和性和通用主机开销清理几乎与调度器交换一样重要。将它们视为一级调优工作，而不是事后想法。

## 陷阱

1. **不要模仿追踪器行**：获胜的配置通常取决于路由模式、容器和 PP 布局，与硬件名称一样重要。

2. **容器质量很重要**：大型回归可能来自软件堆栈而不是模型食谱。

3. **VPP 必须有意为之**：一个糟糕的 VPP 分割可能会抹去更好的调度器的收益。

4. **比较绝对吞吐量，而不仅仅是 MFU**：在 BF16、FP8 和其他精度模式之间切换时，MFU 可能会误导。

5. **强制平衡路由仅限于基准测试**：它可以控制路由差异，但它会改变语义。在 A/B 内保持路由固定，并单独验证自然路由以用于训练接受。

6. **不要将调度器表视为硬平台规则**：HybridEP 是经过验证的 16×H100 Qwen3 30B 形状的获胜者，而当前的 256×H100 Qwen3 235B 食谱使用 `alltoall`。在产品容器中基准测试后端兼容性和吞吐量。

7. **分离筛选、因果关系和接受**：短运行会拒绝薄弱的候选方案，匹配的单变量 A/B 会解释机制，50 步的最终运行会验证完整的获胜者。

_最后签名更新：2026-08-03_。
