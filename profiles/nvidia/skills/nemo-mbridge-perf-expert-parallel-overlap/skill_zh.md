# MoE 专家级并行重叠技能

## 参考文献

- 稳定文档：@docs/training/communication-overlap.md
- 结构化元数据：@skills/nemo-mbridge-perf-expert-parallel-overlap/card.yaml

## 它是什么

专家级并行（EP）重叠通过在专家 FFN 计算的同时运行，隐藏了 token 分发/合并 all-to-all 通信的成本。可选地，延迟的专家权重梯度计算（`delay_wgrad_compute`）通过将 wgrad 延迟到与下一层的正向重叠，提供额外的重叠。桥接支持两种调度器路径：

| 调度器 | 后端 | 使用场景 |
|---|---|---|
| `alltoall` | 标准 MoE all-to-all | 默认，最广泛的兼容性 |
| `flex` | DeepEP 或 HybridEP | 在 Ampere/Hopper/Blackwell 上获得更高的重叠 |

## 快速决策

当满足以下条件时使用 EP 重叠：

- 模型是 MoE 且 `EP > 1`
- 专家调度/合并通信是步骤时间的一个有意义的部分
- 你有内存空间并正在调整吞吐量

优先选择：

- 首次部署时使用 `alltoall` 调度器（更广泛的兼容性）
- 在支持的 GPU 上运行并寻求额外收益时使用 `flex` + DeepEP/HybridEP

避免使用 EP 重叠的情况：

- 启用了完整激活重新计算
- `moe_shared_expert_overlap` 已启用
- 运行仍在进行中，尚未达到正确性
- PyTorch < 2.6.0

预期结果：

- 如果 all-to-all 调度是一个明显的性能瓶颈，重叠可以产生适度的到有意义的加速
- 如果运行非常小，通信量少，或被其他时间墙主导，收益可能可以忽略不计

## 正确性优先 alltoall 基准测试

对于纯 EP 重叠隔离基准测试，保持 flex 调度器和延迟 wgrad 禁用。测量的形状是 Qwen3 MoE 30B-A3B SFT 在 16 个 H100 GPU 上：`EP=16`，`alltoall`，BF16，全局批处理大小 1024，禁用 CUDA 图，`moe_permute_fusion=false`，在迭代 3-8 之间测量。

对于纯重叠情况，使用以下覆盖：

```bash
--cuda_graph_impl none \
--moe_flex_dispatcher_backend None \
--moe_a2a_overlap false \
comm_overlap.overlap_moe_expert_parallel_comm=true \
comm_overlap.delay_wgrad_compute=false \
model.moe_shared_expert_overlap=false
```

对于此隔离测试不要使用 `--moe_a2a_overlap true`：性能测试辅助工具启用了 `overlap_moe_expert_parallel_comm` 和 `delay_wgrad_compute`，因此它不能隔离纯 EP 重叠。

来自该基准测试的稳定窗口计时：

| 案例 | 稳定平均值 | 相对值 |
|---|---:|---:|
| 无 EP 重叠 | 41.25s | 1.000x |
| EP 重叠 | 31.31s | 1.317x |
| EP 重叠加上 `delay_wgrad_compute` | 31.20s | 1.322x |

这是在节点间 all-to-all 形状上启用纯 EP 重叠的证据。它没有显示延迟 wgrad 的有意义独立收益，并且它没有验证融合的 MoE 排列，因为该路径在运行时堆栈中被禁用了。

## HybridEP 生产形状基准测试

2026-07-25 的受控 Qwen3 30B-A3B 预训练比较验证了纯 EP 重叠与生产 HybridEP 路径：

```text
硬件：16×H100
精度：BF16
序列：4096
并行性：TP1 / PP1 / CP1 / EP16
批处理：MBS1 / GBS1024
路由：强制平衡
调度器：flex + HybridEP
CUDA 图：Transformer Engine 范围 moe_router + moe_preprocess
延迟 wgrad：禁用
```

| 案例 | 稳定窗口 | 步骤时间 | 模型 TFLOPS/GPU |
|---|---:|---:|---:|
| 重叠关闭 | 迭代 5-20 | 24.7138s | 244.039 |
| 重叠开启，搜索运行 | 迭代 5-20 | 21.0725s | 286.208 |
| 重叠开启，独立验证 | 迭代 41-50 | 20.9920s | 287.305 |

独立运行将步骤时间减少了 15.059%，并将吞吐量提高了 17.729% 相对于复制的基线。损失是有限的，跳过和 NaN 迭代保持为零，rank-0 峰值分配内存为 62.166 GiB。

一个匹配的 Nsight Systems 比较捕获了每个案例中相同的 463,348 个 rank-0 内核。启用重叠将通信与 GEMM 和注意力从 9.079ms（通信时间的 0.11%）增加到 3,958.997ms（36.55%）。GPU 活动间隔并集从 22.821s 减少到 21.221s。

将其作为机制的证据，而不是通用的加速承诺。在仅纯 EP 重叠更改的情况下，保持调度器、路由、图范围、批处理形状、并行布局和运行时固定。

## 启用

### alltoall 调度器

```python
cfg.comm_overlap.overlap_moe_expert_parallel_comm = True
cfg.comm_overlap.delay_wgrad_compute = False
cfg.model.moe_shared_expert_overlap = False

cfg.model.expert_model_parallel_size = 8
cfg.model.num_moe_experts = 64
cfg.model.moe_token_dispatcher_type = "alltoall"
cfg.model.bf16 = True
cfg.model.fp16 = False
```

仅在纯重叠路径已知工作且其额外的兼容性约束已检查后，才启用 `delay_wgrad_compute=True`。

### flex 调度器（DeepEP 或 HybridEP）

```python
from megatron.bridge.training.flex_dispatcher_backend import apply_flex_dispatcher_backend

cfg.comm_overlap.overlap_moe_expert_parallel_comm = True
cfg.comm_overlap.delay_wgrad_compute = False
cfg.model.moe_shared_expert_overlap = False

apply_flex_dispatcher_backend(cfg.model, moe_flex_dispatcher_backend="deepep")
# 或：apply_flex_dispatcher_backend(cfg.model, moe_flex_dispatcher_backend="hybridep")
```

首先基准测试纯 EP 重叠。仅在 CUDA 图和 TE 兼容性约束得到满足后，作为单独的 A/B 测试启用 `delay_wgrad_compute=True`。

## 兼容性和约束

- `expert_model_parallel_size > 1`
- `num_moe_experts > 1`
- `moe_token_dispatcher_type` 必须是 `"alltoall"` 或 `"flex"`
- `moe_shared_expert_overlap = False`
- 基础精度是 BF16 或 FP16
- PyTorch `>= 2.6.0`
- 如果 `PP > 1`，`virtual_pipeline_model_parallel_size` 必须设置
- `recompute_granularity != "full"`，`recompute_method = None`，`recompute_num_layers = None`
- `mtp_num_layers` 必须是 `None` 或 `1`
- `delay_wgrad_compute` 需要 `overlap_moe_expert_parallel_comm` 作为先决条件
- `delay_wgrad_compute` 与 `overlap_grad_reduce` 需要 TE >= 2.7.0
- `delay_wgrad_compute` 与 `gradient_accumulation_fusion` 需要 TE >= 2.7.0
- CUDA 图 `attn` 范围 + `delay_wgrad_compute` 需要 TE >= 2.12.0，`gradient_accumulation_fusion = True`，且无注意力偏差
- DeepEP：仅限 Ampere、Hopper、B200、B300 GPU
- HybridEP：Ampere、Hopper、B200、B300、GB200/GB300 配备 NVL72 的 GPU

## 最小工作配置

```python
cfg.comm_overlap.overlap_moe_expert_parallel_comm = True
cfg.comm_overlap.delay_wgrad_compute = False
cfg.model.expert_model_parallel_size = 4
cfg.model.num_moe_experts = 64
cfg.model.moe_token_dispatcher_type = "alltoall"
cfg.model.moe_shared_expert_overlap = False
cfg.model.bf16 = True
```

将其作为正确性优先的起点。仅在纯重叠路径已知工作后，才添加延迟 wgrad、flex 调度器和 CUDA 图交互。

## 最小可运行命令

性能测试框架示例在 Slurm 分配内。保持模型、并行性、调度器和运行时固定，仅更改两个重叠覆盖：

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

在分离纯 EP 重叠和延迟 wgrad 时不要使用 `--moe_a2a_overlap true`：性能测试框架辅助工具启用了 `overlap_moe_expert_parallel_comm` 和 `delay_wgrad_compute`。

单元测试验证：

```bash
uv run python -m pytest \
  tests/unit_tests/training/test_comm_overlap.py -k "moe" \
  tests/unit_tests/training/test_deepep.py -q
```

## 验证

### 单元测试

```bash
uv run python -m pytest \
  tests/unit_tests/training/test_comm_overlap.py \
  tests/unit_tests/training/test_deepep.py -q
```

### 日志检查

在成功使用 EP 重叠运行后：

1. 确认在 `CommOverlapConfig` 最终化期间没有断言错误
2. 确认 `overlap_moe_expert_parallel_comm` 在日志配置中显示为 `True`
3. 如果使用 flex 调度器，确认 `moe_token_dispatcher_type = "flex"` 和日志中的正确后端

### 成功标准

- 选择的调度器和重叠设置通过配置验证
- 训练运行完成且没有挂起或断言失败
- 目标工作负载的吞吐量提高或至少不下降
- 损失轨迹与基线匹配（重叠不应影响收敛）

### 性能分析解释

使用未分析的稳定窗口进行吞吐量验收结果。使用匹配的分析来解释机制：

1. 保持调度器、路由、图范围、批处理形状、并行布局和运行时固定
2. 在仅切换纯 EP 重叠时捕获相同的 rank 和稳定迭代
3. 为通信和计算内核构建间隔并集，然后测量它们的交集
4. 不要使用求和内核持续时间作为墙时间。即使暴露时间减少，并发内核可以在 SM 或带宽争用下运行更长时间
5. 用调度/合并 NVTX 范围、最终步骤时间、损失有限性、跳过/NaN 计数和峰值内存验证间隔结果

## 代码锚点

### 桥接重叠验证

```470:505:src/megatron/bridge/training/comm_overlap.py
if self.user_comm_overlap_cfg.overlap_moe_expert_parallel_comm is True:
    assert model_cfg.expert_model_parallel_size > 1, ...
    assert model_cfg.num_moe_experts > 1, ...
    assert model_cfg.moe_token_dispatcher_type in ["alltoall", "flex"], ...
    assert model_cfg.bf16 or model_cfg.fp16, ...
    assert is_torch_min_version("2.6.0"), ...
    # ... PP + VPP 检查，重新计算检查，共享专家重叠检查 ...
```

### 延迟 wgrad 验证

```507:557:src/megatron/bridge/training/comm_overlap.py
if self.user_comm_overlap_cfg.delay_wgrad_compute is True:
    # TE 版本检查用于 overlap_grad_reduce 和 gradient_accumulation_fusion
    # 延迟 wgrad 的 CUDA 图范围验证
    assert overlap_moe_expert_parallel_comm, ...
```

### Flex 调度器激活

```27:72:src/megatron/bridge/training/flex_dispatcher_backend.py
def apply_flex_dispatcher_backend(...):
    # DeepEP / HybridEP 的 GPU 架构检查
    model_config.moe_token_dispatcher_type = "flex"
    model_config.moe_flex_dispatcher_backend = moe_flex_dispatcher_backend
    model_config.moe_shared_expert_overlap = False
```

### 性能测试框架覆盖

```149:156:scripts/performance/utils/overrides.py
def _set_moe_a2a_overlap_overrides(recipe, moe_a2a_overlap=False):
    if moe_a2a_overlap:
        recipe.comm_overlap.overlap_moe_expert_parallel_comm = True
        recipe.comm_overlap.delay_wgrad_compute = True
        recipe.model.moe_shared_expert_overlap = False
```

### 测试

| 文件 | 覆盖率 |
|---|---|
| `tests/unit_tests/training/test_comm_overlap.py` | EP 重叠验证、延迟 wgrad、CUDA 图 + wgrad 交互 |
| `tests/unit_tests/training/test_deepep.py` | DeepEP/HybridEP 辅助激活和 GPU 门控 |

## 故障诊断

| 症状 | 可能原因 | 如何确认 | 修复 |
|---|---|---|---|
| 断言 `expert_model_parallel_size > 1` | EP 未配置 | 检查 `expert_model_parallel_size` | 设置 EP > 1 |
| 断言 `moe_token_dispatcher_type` | 错误的调度器 | 检查调度器类型 | 使用 `"alltoall"` 或 `"flex"` |
| 断言 BF16/FP16 | 错误的精度 | 检查 `bf16` 和 `fp16` | 设置 `bf16 = True` |
| 训练期间挂起 | PyTorch < 2.6 | 检查 PyTorch 版本 | 升级到 >= 2.6.0 |
| 断言 `virtual_pipeline_model_parallel_size` | PP > 1 而无 VPP | 检查 PP 和 VPP 配置 | PP > 1 时设置 VPP |
| 断言 `recompute_granularity` | 全局重新计算启用 | 检查重新计算设置 | 禁用全局重新计算 |
| 断言 `overlap_moe_expert_parallel_comm required` | 延迟 wgrad 而无 EP 重叠 | 检查 `delay_wgrad_compute` 而无重叠 | 首先启用 EP 重叠 |
| 断言 `gradient_accumulation_fusion` | CUDA 图 + 延迟 wgrad | 检查图范围 + wgrad 设置 | 启用 `gradient_accumulation_fusion` |
| 断言注意力偏差 | CUDA 图 attn + 延迟 wgrad + 偏差 | 检查 `add_bias_linear` / `add_qkv_bias` | 禁用注意力偏差 |
| flex 调度器未提供吞吐量增益 | `apply_flex_dispatcher_backend` 未调用 | 检查日志中的 `moe_token_dispatcher_type` | 调用 `apply_flex_dispatcher_backend(...)` |
| DeepEP/HybridEP 沉默跳过 | 不支持的 GPU | 检查警告日志 | 在 Ampere/Hopper/Blackwell 上运行 |
| 重叠后求和内核时间增加 | 预期的并发争用或回归 | 比较间隔并集、通信/计算交集和未分析的步骤时间 | 从暴露的墙时间判断重叠，而不是每个流的求和持续时间 |

## 已知限制

- 单独设置 `moe_flex_dispatcher_backend` 并不会激活 flex 调度器 — 你必须调用 `apply_flex_dispatcher_backend(...)`。
- 公共配方通常保守，默认情况下禁用 MoE 重叠。
- 存在受控端到端和性能证据，针对一个 Qwen3 30B-A3B HybridEP H100 形状；在将其推广到另一个模型、调度器、拓扑、精度或批处理形状之前，重复匹配的 A/B 测试。
- MoE 重叠和共享专家重叠是互斥的。
- CUDA 图加上延迟 wgrad 是一个多约束路径，需要仔细的 TE 版本和范围验证。

_最后签名更新：2026-08-03_。
