# MoE 通信重叠

有关高层概述，请参阅：

- @docs/training/communication-overlap.md
- @skills/nemo-mbridge-perf-moe-comm-overlap/card.yaml

## 快速决策

当满足以下条件时使用 MoE 通信重叠：

- `EP > 1`
- token 分发或合并时间在性能分析中可见
- 运行已经正确，现在正在调整吞吐量

避免将其作为早期启动步骤开启。在调度器、路由模式和重新计算计划已经稳定后，更容易进行验证。

## 启用

```python
cfg.comm_overlap.overlap_moe_expert_parallel_comm = True

# 可选：延迟 wgrad 以实现额外的重叠
cfg.comm_overlap.delay_wgrad_compute = True

# 重要提示：在使用分发重叠时禁用共享专家重叠
cfg.model.moe_shared_expert_overlap = False
```

### 前置条件

- `expert_model_parallel_size > 1`
- `num_moe_experts > 1`
- `moe_token_dispatcher_type` 必须为 `"alltoall"` 或 `"flex"`
- 精度：BF16 或 FP16
- 如果使用 PP，VPP (`virtual_pipeline_model_parallel_size`) 必须设置（非 `None`）

### Flex 调度器激活

仅设置 `moe_flex_dispatcher_backend` **不会**激活 flex 调度。您还必须设置 `moe_token_dispatcher_type = "flex"`。

## 重新计算与 CUDA 图交互

- 全部重新计算不是重叠路径的良好伴侣。
- `delay_wgrad_compute` 如果 CUDA 图作用域包含注意力或 MoE 路由器工作，会添加进一步约束。
- 实践中，当启用重叠时，选择性重新计算是更安全的选择。

## 测量证据

### HybridEP 生产形状验证

2026-07-25 控制性 Qwen3 30B-A3B 预训练比较使用了 16 个 H100 GPU，BF16，序列长度 4096，`TP=1`，`PP=1`，`CP=1`，`EP=16`，`MBS=1`，`GBS=1024`，强制平衡路由，HybridEP，以及 Transformer Engine CUDA 图作用域 `moe_router` 和 `moe_preprocess`。唯一性能变化是纯 EP 重叠；延迟 wgrad 保持禁用。

| 案例 | 稳定窗口 | 步骤时间 | GPU 模型 TFLOPS |
|---|---:|---:|---:|
| EP 重叠关闭 | 迭代 5-20 | 24.7138s | 244.039 |
| EP 重叠开启，搜索运行 | 迭代 5-20 | 21.0725s | 286.208 |
| EP 重叠开启，独立验证 | 迭代 41-50 | 20.9920s | 287.305 |

独立结果将步骤时间缩短了 15.059%，并将吞吐量提高了 17.729%。损失保持有限，没有迭代被跳过或 NaN，rank-0 峰值分配内存为 62.166 GiB。

相同方法的 rank-0 Nsight Systems 比较在每个情况下捕获了 463,348 个内核：

| 性能指标 | 重叠关闭 | 重叠开启 |
|---|---:|---:|
| 与 GEMM/注意力并发通信 | 9.079ms | 3,958.997ms |
| 被计算隐藏的通信时间 | 0.11% | 36.55% |
| GPU 活动间隔并集 | 22.821s | 21.221s |
| HybridEP 调度-重排 NVTX | 4.253s | 1.767s |
| HybridEP 元数据预处理 NVTX | 3.109s | 0.670s |

这是直接证据表明收益来自隐藏暴露的 HybridEP 调度/合并工作，而不是改变调度器、路由、图作用域、批处理形状或并行布局。

### 正确性优先 alltoall 烟测

2026-05-18 当前主 H100 x16 烟测在 Qwen3 30B-A3B 模拟预训练中使用了 `EP=16`，`alltoall`，全局批处理大小 1024，禁用 CUDA 图，并且 `moe_permute_fusion=false`，因为 PyTorch 25.11 / TE / Triton 堆栈在先前的启动中在 Transformer Engine 熔合重排中失败。

结果是方向性的，而不是发布级别的：

- 无 EP 重叠：迭代 3-8 的稳态平均时间为 41.25s
- EP 重叠：迭代 3-8 的稳态平均时间为 31.31s
- EP 重叠加上 `delay_wgrad_compute`：迭代 3-8 的稳态平均时间为 31.20s

将其视为 EP 重叠可以帮助节点间 `alltoall` MoE 形状在通信暴露时的证据。它不是延迟 wgrad 是独立收益的证据，也不验证熔合重排路径。一个更早的 2026-05-16 在相同形状上的短烟测显示了相同模式。

## 代码锚点

- 重叠验证：`src/megatron/bridge/training/comm_overlap.py`
- Flex 调度器后端：`src/megatron/bridge/training/flex_dispatcher_backend.py`
- 配置：`src/megatron/bridge/training/config.py`
- 单元测试：`tests/unit_tests/training/test_comm_overlap.py`
- DeepEP 测试：`tests/unit_tests/training/test_deepep.py`

## 陷阱

1. **共享专家重叠冲突**：`moe_shared_expert_overlap` 和 `overlap_moe_expert_parallel_comm` 可能冲突。在使用分发重叠路径时禁用共享专家重叠。

2. **无 VPP 的 PP**：当流水线并行性激活时，MoE 重叠需要 VPP。没有它，重叠调度无法正确交错。

3. **Flex != 后端标志**：`moe_flex_dispatcher_backend="deepep"` 单独如果 `moe_token_dispatcher_type` 仍然是 `"alltoall"` 则什么也不做。

4. **保守配方默认值**：大多数公共配方禁用 MoE 重叠。您需要通过覆盖显式启用它。

5. **性能收益取决于工作负载**：当分发通信已经是步骤时间可见切片时，重叠帮助最大。它不保证每个小型或负载较轻的 EP 运行都有帮助。

6. **总和内核时间不是墙上时间**：并发内核可能运行更长时间，因为它们争抢 SM 或带宽，所以重叠可能会增加每个流的内核总和持续时间，同时减少暴露的间隔并集和端到端步骤时间。

## 验证

在初始化期间查找与重叠相关的日志消息。`comm_overlap.py` 中的通信重叠验证如果前置条件未满足会引发错误，因此干净的启动确认该功能已激活。

对于短性能测试烟测，保持命令形状明确，一次只改变一个重叠旋钮：

```bash
uv run python scripts/performance/run_script.py \
  -m qwen \
  -mr qwen3_30b_a3b \
  --task pretrain \
  -g h100 \
  -c bf16 \
  -ng 16 \
  -gn 8 \
  --max_steps 8 \
  --cuda_graph_impl none \
  --moe_flex_dispatcher_backend None \
  --moe_a2a_overlap false \
  --tokenizer_type NullTokenizer \
  comm_overlap.overlap_moe_expert_parallel_comm=true \
  comm_overlap.delay_wgrad_compute=false \
  model.moe_shared_expert_overlap=false
```

如果熔合 MoE 重排在启动期间失败，添加 `model.moe_permute_fusion=false` 以将重叠时间与运行时堆栈验证分离，然后使用匹配的生产容器重新测试。

对于性能验证，使用未分析的稳态窗口作为接受指标。使用匹配的 Nsight A/B 建立因果关系：

1. 保持调度器、路由、CUDA 图、批处理形状、并行性和运行时固定。
2. 仅切换 `overlap_moe_expert_parallel_comm`；第一个隔离保持 `delay_wgrad_compute=false`。
3. 比较通信和计算间隔并集及其交集，而不仅仅是总和内核持续时间。
4. 报告稳态步骤时间、模型 GPU TFLOPS、损失有限性、跳过/NaN 迭代和峰值分配内存。

_最后签名刷新：2026-08-03。_
