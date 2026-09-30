---
name: nemo-automodel-distributed-training
description: NeMo AutoModel 中选择和配置分布式训练策略的指南，包括 FSDP2、Megatron FSDP、DDP 和并行设置。
---

# NeMo AutoModel 中的分布式训练

## 目的

NeMo AutoModel 使用 PyTorch 原生的分布式训练。
所有并行操作都通过一个 `MeshContext` 对象进行协调，该对象包含设备网格、策略配置和轴名称。
<!-- NVSkills 目录签名请求在 PR #2937 (2026-07-31) 之后进行。 -->

## 说明

对于概念性的分布式训练问题，直接从本技能中的快速模式进行回答，而无需检查存储库。
从策略选择开始，然后仅列出与问题相关的 YAML 字段和约束。

在最终答案中使用直接动作动词：推荐策略、显示最小的 YAML、说明规模约束，并命名不支持的策略。
除非用户询问，否则不要讨论模型上载、配方、Slurm、SkyPilot 或检查点。

## 示例

### 大型多节点模型的 TP + PP

推荐 `strategy: fsdp2`。提及 `tp_size`、`pp_size`、`cp_size`、`ep_size` 以及 `pipeline` 子配置。
说明 `dp_size` 由 `world_size / (tp_size * pp_size * cp_size)` 推断。

```yaml
distributed:
  strategy: fsdp2
  tp_size: 8
  pp_size: 4
  cp_size: 1
  ep_size: 1
  pipeline:
    pp_schedule: interleaved1f1b
    pp_microbatch_size: 1
```

### MoE 专家并行

推荐 `strategy: fsdp2` 并设置 `ep_size > 1`。说明这会创建一个单独的 `moe_mesh`；在相关情况下包含 `moe` 子配置；说明 `ep_size` 必须能整除 `dp_size * cp_size`。
不要推荐 `megatron_fsdp` 或 `ddp`。

```yaml
distributed:
  strategy: fsdp2
  ep_size: 8
  moe:
    reshard_after_forward: false
```

### MegatronFSDP 限制

对于流水线并行、专家并行和 `sequence_parallel` 说“不”。
对于 PP、EP 或 `sequence_parallel` 推荐 `fsdp2`；提及 DDP 仅支持简单的数据并行。

## 策略选择

三种策略可用，通过 `distributed.strategy` YAML 键选择：

| 策略 | YAML 值 | 适用于 |
|---|---|---|
| FSDP2 | `fsdp2` | 通用，推荐默认值。支持 TP、PP、CP、EP、HSDP。 |
| MegatronFSDP | `megatron_fsdp` | NVIDIA Megatron 风格的 FSDP。不支持 PP、EP、sequence_parallel。 |
| DDP | `ddp` | 仅支持简单的数据并行。不支持 TP、PP、CP 或 EP。 |

决策树：

- 单个 GPU：不需要分布式配置（FSDP2Manager 在 `world_size=1` 时跳过并行化）。
- 单个节点多 GPU：`fsdp2`（默认）。仅在您需要最简单的设置时使用 `ddp`。
- 多节点：带适当 TP/PP 尺寸的 `fsdp2`。
- 带专家并行的 MoE 模型：`fsdp2` 并设置 `ep_size > 1`（创建一个单独的 `moe_mesh`）。
- 大型模型（70B+）：带 PP + TP 的 `fsdp2`。
- 长序列（8K+）：添加 CP (`cp_size > 1`)。

在回答策略选择问题时，首先说明选择的 `distributed.strategy`，然后枚举用户必须设置的 YAML 字段。

快速 TP + PP 回答：

- 使用 `strategy: fsdp2`；当需要流水线并行时，不要使用 `megatron_fsdp`。
- 设置 `tp_size` 用于张量并行，设置 `pp_size` 用于流水线并行。
- 添加一个 `pipeline:` 子配置，包含 `pp_schedule` 和 `pp_microbatch_size`。
- 不设置或设置 `dp_size` 为 `none`；它被推断为 `world_size / (tp_size * pp_size * cp_size)`。
- 尽可能将 TP 保留在快速 intra-node 域内，并使用 PP 跨模型深度进行 70B+ 模型。

快速 MoE 专家并行回答：

- 从 `strategy: fsdp2` 和 `ep_size > 1` 开始。
- 仅当 `ep_size > 1` 时包含 `moe:` 子配置；它映射到 `MoEParallelizerConfig`。
- 除了主 `device_mesh` 外，还期望一个单独的 `moe_mesh` 用于专家并行。
- 不要推荐 `megatron_fsdp` 或 `ddp` 用于专家并行；`megatron_fsdp` 没有对 EP 的支持。
- 在完成 MoE EP 回答之前，明确说明 `ep_size` 必须能整除 `dp_size * cp_size`，并且 `megatron_fsdp` 不支持 EP、PP 或 `sequence_parallel`。

## YAML 配置结构

配方 YAML 中的 `distributed` 部分直接映射到 `recipes/_dist_utils.py` 中的 `parse_distributed_section()`：

```yaml
distributed:
  strategy: fsdp2           # fsdp2 | megatron_fsdp | ddp
  dp_size: none             # 从 world_size / (tp * pp * cp) 自动计算
  dp_replicate_size: none   # FSDP2 仅用，用于 HSDP
  tp_size: 1
  pp_size: 1
  cp_size: 1
  ep_size: 1

  # 策略特定标志（转发到策略数据类）：
  sequence_parallel: false
  activation_checkpointing: false
  defer_fsdp_grad_sync: true   # FSDP2 仅用

  # 子配置（可选）：
  pipeline:
    pp_schedule: 1f1b
    pp_microbatch_size: 1
    # ... 查看 PipelineConfig 字段

  moe:
    reshard_after_forward: false
    # ... 查看 MoEParallelizerConfig 字段
```

`dp_size` 始终被推断：

```
dp_size = world_size / (tp_size * pp_size * cp_size)
```

## 基础设施流程

```
initialize_distributed()                       [components/distributed/init_utils.py]
    -> 初始化 torch.distributed process group 并返回 DistInfo
YAML distributed section + DistInfo.world_size
    -> parse_distributed_section()          [recipes/_dist_utils.py]
    -> create_distributed_setup_from_config()              [recipes/_dist_utils.py]
        -> DistributedSetup.build()         [components/distributed/config.py]
    -> instantiate_infrastructure()         [_transformers/infrastructure.py]
        -> _instantiate_distributed()       -> FSDP2Manager / MegatronFSDPManager / DDPManager
        -> _instantiate_pipeline()          -> AutoPipeline (如果 pp_size > 1)
        -> parallelize_fn                   -> MoE 并行器（如果 ep_size > 1）或 PP 包装器
    -> apply_model_infrastructure()         [_transformers/infrastructure.py]
        -> _shard_pp() 或 _shard_ep_fsdp()  (对模型应用分片)
```

## FSDP2 配置

### 基本FSDP2（仅数据并行）

```yaml
distributed:
  strategy: fsdp2
  tp_size: 1
  cp_size: 1
```

这会自动计算 `dp_size = world_size` 并通过 DTensor 基于的分片对每个 transformer 块应用 `fully_shard()`。

### 带张量并行的 FSDP2

将 TP 保留在单个 NVLink 域内（通常是一个节点）：

```yaml
distributed:
  strategy: fsdp2
  tp_size: 4        # 2、4 或 8 -- 必须能整除每个节点的 GPU 数
  sequence_parallel: true
```

TP 计划根据模型类型自动选择。如果需要，可以通过 Python API 传递自定义计划：

```python
config = FSDP2Config(sequence_parallel=True, tp_plan=my_custom_plan)
```

### 带流水线并行的 FSDP2

```yaml
distributed:
  strategy: fsdp2
  pp_size: 2
  pipeline:
    pp_schedule: interleaved1f1b   # 1f1b、gpipe、interleaved_1f1b 等
    pp_microbatch_size: 4
    scale_grads_in_schedule: false
```

模型必须有 `_pp_plan` 属性（在 HF 模型类上设置），以便 `AutoPipeline` 知道如何将层拆分到各个阶段。没有 `_pp_plan` 的模型与 PP 不兼容。

### 带HSDP（混合分片数据并行）的 FSDP2

节点内全分片 + 跨节点通过 2D DeviceMesh 的复制：

```yaml
distributed:
  strategy: fsdp2
  dp_replicate_size: 2   # 必须能整除 dp_size
```

约束：`dp_replicate_size < dp_size`（纯复制而不分片不被 FSDP2 支持）。

### 激活检查点

通过在反向传播期间重新计算激活来用计算换取内存：

```yaml
distributed:
  activation_checkpointing: true
```

这是一个模型构建/训练行为标志，而不是网格拓扑。密集策略从策略配置中读取它；EP/MoE 路径将配方级标志直接传递到模型基础设施。

### 梯度同步延迟

FSDP2 默认将梯度同步延迟到最终微批次以实现通信重叠：

```yaml
distributed:
  defer_fsdp_grad_sync: true   # 默认
```

### 混合精度

FSDP2Config 通过 `MixedPrecisionPolicy(param_dtype=bf16, reduce_dtype=bf16, output_dtype=bf16,
cast_forward_inputs=True)` 默认为所有三个精度旋钮使用 bfloat16。通过 Python API 覆盖：

```python
from torch.distributed.fsdp import MixedPrecisionPolicy
config = FSDP2Config(
    mp_policy=MixedPrecisionPolicy(param_dtype=torch.float16, reduce_dtype=torch.float32),
)
```

## 流水线并行

### 要求

1. 模型类必须定义 `_pp_plan`（一个将模块 FQNs 映射到阶段的字典）。
2. `pp_size > 1` 在分布式部分。
3. 一个带有调度和微批次大小的 `pipeline` 子配置。

### 支持的调度

定义在 `PipelineConfig.pp_schedule` 中：

- `1f1b`（单前向单后向，默认）
- `gpipe`
- `interleaved_1f1b` / `interleaved1f1b`
- `looped_bfs`
- `dfs`
- `v_schedule`
- `zero_bubble`

### 示例（8B 模型在 8 个 GPU 上，PP=2 + DP=4）

```yaml
distributed:
  strategy: fsdp2
  pp_size: 2

  pipeline:
    pp_schedule: interleaved1f1b
    pp_microbatch_size: 4
    scale_grads_in_schedule: false

checkpoint:
  model_save_format: safetensors
  save_consolidated: final
```

### 工作原理

`AutoPipeline.build()` 调用 `pipeline_model()`，该函数使用模型的 `_pp_plan` 将模型拆分为阶段，创建 `PipelineStage` 对象，并构建调度。在训练期间，`schedule.step()` 驱动通过流水线的前向和后向。

## 上下文并行

使用 CP 进行长序列（8K+）。CP 在序列维度上作为 DTensors 分片 Q/K/V。

### 配置

```yaml
distributed:
  strategy: fsdp2
  cp_size: 2   # 或 4、8
```

### 要求

- SDPA（Flash Attention 或 Efficient Attention 后端）或 Transformer Engine 注意力。
  SDPBackend.MATH 与 DTensor 不兼容。
- 注意力掩码会自动剥离；`is_causal=True` 通过 `attach_context_parallel_hooks()` 注册的前向预挂钩设置。

### 工作原理

1. 模型分片后，`apply_model_infrastructure()` 调用每个模型部分的 `attach_context_parallel_hooks()`（对于非 TE 模型）。
2. 在每个训练步骤中，`make_cp_batch_and_ctx()` 创建一个 CP 上下文管理器，沿序列维度分片批次并设置 `torch.distributed.tensor.experimental.context_parallel`。
3. 对于 TE 注意力模型，`make_cp_batch_for_te()` 使用 THD 格式和 TE 的 `thd_get_partitioned_indices` 进行分片。

### 带序列打包的 CP

CP 与打包序列一起工作。`packed_sequence_size` 必须能被 `cp_size` 整除。使用 TE 时，通过 `_shard_thd_chunk_for_te()` 每个块进行分片。

## 序列打包

将多个序列打包为单个训练样本以提高效率。

### 配置

```yaml
packed_sequence:
  packed_sequence_size: 4096   # 0 = 禁用

step_scheduler:
  local_batch_size: 1          # 必须为 1 以用于打包序列
```

当 `packed_sequence_size > 0` 时，数据集组合器将序列打包到该长度。`local_batch_size` 必须为 1，因为每个“样本”已经是一个打包的批次。

## MoE 分布式训练

### 专家并行

设置 `ep_size > 1` 以在 GPU 间分布专家。这会创建一个与主 `device_mesh` 并列的单独 `moe_mesh`：

```yaml
distributed:
  strategy: fsdp2
  ep_size: 8
  activation_checkpointing: true
```

`moe_mesh` 的形状是 `(pp_size, ep_shard_size, ep_size)`，维度名称为 `("pp", "ep_shard", "ep")`。

约束：`dp_cp_size`（= `dp_size * cp_size`）必须能被 `ep_size` 整除。

### MoE 子配置

```yaml
distributed:
  strategy: fsdp2
  ep_size: 8
  activation_checkpointing: true

  moe:
    reshard_after_forward: false
    ignore_router_for_ac: false
    wrap_outer_model: true
```

`moe` 子部分映射到 `MoEParallelizerConfig`，并且仅在 `ep_size > 1` 时实例化。

### 完整 MoE 示例（Qwen3-30B-A3B 在 8 个 GPU 上）

```yaml
distributed:
  strategy: fsdp2
  tp_size: 1
  cp_size: 1
  pp_size: 1
  ep_size: 8
  sequence_parallel: false
  activation_checkpointing: true
```

### MegatronFSDP 限制

尽管其名称如此，`megatron_fsdp` 并不支持专家并行 (`ep_size > 1`)、流水线并行 (`pp_size > 1`) 或 `sequence_parallel`。对于这些功能，请使用 `fsdp2`。

```
_transformers/infrastructure.py
    instantiate_infrastructure()    -- 配置对象 -> 运行时对象
    apply_model_infrastructure()    -- 对模型应用分片、PEFT、检查点
    _shard_pp()                     -- 流水线并行路径
    _shard_ep_fsdp()                -- EP + FSDP路径（非PP）
```

YAML解析：

```
recipes/_dist_utils.py
    parse_distributed_section()  -- YAML字典 -> 带有类型的配置+大小
    create_distributed_setup_from_config()  -- 配置适配器：解析+创建DistributedSetup；不初始化进程组
```

MoE配置：

```
components/distributed/config.py
    MoEParallelizerConfig  -- reshard_after_forward, ignore_router_for_ac, wrap_outer_model, 等
components/moe/config.py
    MoEConfig              -- n_routed_experts, n_activated_experts, score_func, 等
```

## 陷阱

1. **跨节点的TP会降低吞吐量。** 始终将TP保持在单个NVLink域内。使用PP或DP进行跨节点扩展。

2. **PP需要在模型类上具有`_pp_plan`。** 并非所有HF模型都有这个。启用PP前请检查`validate_hf_model_for_pipeline_support()`。

3. **PP气泡会降低GPU利用率。** 使用交错调度（`interleaved_1f1b`）和较小的微批次来减少气泡时间。

4. **FSDP2需要DTensor感知的状态字典保存。** 使用`safetensors`配合`save_consolidated: final`进行最终HF导出，或使用`save_consolidated: false`加上生成的`model/consolidate.sh`辅助脚本进行离线导出。

5. **CP需要兼容的注意力机制。** 仅支持SDPA（Flash Attention或高效注意力）或TE注意力。`SDPBackend.MATH`与DTensor不兼容。

6. **MoE EP大小必须能整除`dp_size * cp_size`。** 设备网格创建会断言`dp_cp_size % ep_size == 0`。

7. **MegatronFSDP比FSDP2限制更多。** 它不支持PP（`pp_size > 1`）、EP（`ep_size > 1`）或`sequence_parallel`。`MeshContext`验证会在这些组合上引发错误。

8. **DDP仅支持数据并行性。** 不支持TP、PP、CP、EP或HSDP。任何这些组合都会引发验证错误。

9. **激活检查点会增加计算量。** 它通过反向传播期间重新计算激活来节省内存，但会增加约30%的计算开销。

10. **混合精度策略必须符合模型预期。** 默认的bfloat16策略适用于大多数模型。FP16模型可能需要自定义的`MixedPrecisionPolicy`。

11. **使用CP时，`packed_sequence_size`必须能被`cp_size`整除**。

12. **`dp_replicate_size`是FSDP2独有。** 使用`megatron_fsdp`或`ddp`传递它时会引发`ValueError`。

## 验证

运行能测试所需策略的最小配方。成功意味着退出码为0、有限损失、无NCCL超时，且日志输出匹配预期的TP/PP/CP/EP大小。
