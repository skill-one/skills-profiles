# NeMo AutoModel 中的分布式训练

## 目的

NeMo AutoModel 使用 PyTorch 原生的分布式训练。
所有并行操作都通过一个 `MeshContext` 对象进行协调，该对象包含设备网格、策略配置和轴名称。
<!-- NVSkills 目录签名请求在 PR #2937（2026-07-31）之后。 -->

## 说明

对于概念性的分布式训练问题，直接从本技能中的快速模式中回答，而无需检查存储库。从策略选择开始，然后仅列出与问题相关的 YAML 字段和约束。

使用直接动作动词在最终答案中：推荐策略、显示最小的 YAML、说明尺寸约束，并命名不支持的策略。除非用户询问，否则不要讨论模型上载、配方、Slurm、SkyPilot 或检查点。

## 示例

### 大型多节点模型的 TP + PP

推荐 `strategy: fsdp2`。提及 `tp_size`、`pp_size`、`cp_size`、`ep_size` 以及 `pipeline` 子配置。说明 `dp_size` 由 `world_size / (tp_size * pp_size * cp_size)` 推断。

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

推荐 `strategy: fsdp2` 并设置 `ep_size > 1`。说明这会创建一个单独的 `moe_mesh`；在相关情况下包含 `moe` 子配置；说明 `ep_size` 必须能整除 `dp_size * cp_size`。不要推荐 `megatron_fsdp` 或 `ddp`。

```yaml
distributed:
  strategy: fsdp2
  ep_size: 8
  moe:
    reshard_after_forward: false
```

### MegatronFSDP 限制

对于流水线并行、专家并行和 `sequence_parallel` 说“不”。推荐使用 `fsdp2` 进行 PP、EP 或 `sequence_parallel`；说明 DDP 仅支持简单的数据并行。

## 策略选择

有三个策略可用，通过 `distributed.strategy` YAML 键选择：

| 策略 | YAML 值 | 适用于 |
|---|---|---|
| FSDP2 | `fsdp2` | 通用使用，推荐默认值。支持 TP、PP、CP、EP、HSDP。 |
| MegatronFSDP | `megatron_fsdp` | NVIDIA Megatron 风格的 FSDP。不支持 PP、不支持 EP、不支持 `sequence_parallel`。 |
| DDP | `ddp` | 仅支持简单的数据并行。不支持 TP、PP、CP 或 EP。 |

决策树：

- 单个 GPU：不需要分布式配置（FSDP2Manager 在 `world_size=1` 时跳过并行化）。
- 单个节点多 GPU：`fsdp2`（默认）。仅在需要最简单设置时使用 `ddp`。
- 多节点：使用适当的 TP/PP 尺寸的 `fsdp2`。
- 带专家并行的 MoE 模型：`fsdp2` 并设置 `ep_size > 1`（创建一个单独的 `moe_mesh`）。
- 大型模型（70B+）：`fsdp2` 并使用 PP + TP。
- 长序列（8K+）：添加 CP（`cp_size > 1`）。

在回答策略选择问题时，首先说明选择的 `distributed.strategy`，然后枚举用户必须设置的 YAML 字段。

快速 TP + PP 答案：

- 使用 `strategy: fsdp2`；当需要流水线并行时，不要使用 `megatron_fsdp`。
- 设置 `tp_size` 用于张量并行，设置 `pp_size` 用于流水线并行。
- 添加 `pipeline:` 子配置，包含 `pp_schedule` 和 `pp_microbatch_size`。
- 不设置或设置 `dp_size` 为 `none`；它被推断为 `world_size / (tp_size * pp_size * cp_size)`。
- 尽可能将 TP 保留在快速节点内域中，并使用 PP 跨模型深度进行 70B+ 模型。

快速 MoE 专家并行答案：

- 从 `strategy: fsdp2` 和 `ep_size > 1` 开始。
- 仅当 `ep_size > 1` 时包含 `moe:` 子配置；它映射到 `MoEParallelizerConfig`。
- 除了主 `device_mesh` 外，还会为专家并行创建一个单独的 `moe_mesh`。
- 不要推荐 `megatron_fsdp` 或 `ddp` 用于专家并行；`megatron_fsdp` 没有支持 EP。
- 在完成 MoE EP 答案之前，明确说明 `ep_size` 必须能整除 `dp_size * cp_size`，并且 `megatron_fsdp` 不支持 EP、PP 或 `sequence_parallel`。

## YAML 配置结构

配方 YAML 中的 `distributed` 部分直接映射到 `recipes/_dist_utils.py` 中的 `parse_distributed_section()`：

```yaml
distributed:
  strategy: fsdp2           # fsdp2 | megatron_fsdp | ddp
  dp_size: none             # 自动计算自 world_size / (tp * pp * cp)
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
        -> parallelize_fn                   -> MoE 并行化器（如果 ep_size > 1）或 PP 包装器
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

这会自动计算 `dp_size = world_size` 并通过 DTensor 基于的分片在每个 transformer 块上应用 `fully_shard()`。

### 带张量并行的 FSDP2

将 TP 保留在单个 NVLink 域内（通常是一个节点）：

```yaml
distributed:
  strategy: fsdp2
  tp_size: 4        # 2、4 或 8 -- 必须能整除每个节点的 GPU 数量
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

模型必须具有 `_pp_plan` 属性（在 HF 模型类上设置），以便 `AutoPipeline` 知道如何将层拆分到各个阶段。没有 `_pp_plan` 的模型不兼容 PP。

### 带HSDP（混合分片数据并行）的 FSDP2

节点内全分片 + 通过 2D DeviceMesh 进行的跨节点复制：

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

FSDP2 默认将梯度同步延迟到最终微批次，以实现通信重叠：

```yaml
distributed:
  defer_fsdp_grad_sync: true   # 默认
```

### 混合精度

FSDP2Config 默认通过 `MixedPrecisionPolicy(param_dtype=bf16, reduce_dtype=bf16, output_dtype=bf16, cast_forward_inputs=True)` 为所有三个精度旋钮设置 bfloat16。通过 Python API 覆盖：

```python
from torch.distributed.fsdp import MixedPrecisionPolicy
config = FSDP2Config(
    mp_policy=MixedPrecisionPolicy(param_dtype=torch.float16, reduce_dtype=torch.float32),
)
```

## 流水线并行

### 要求

1. 模型类必须定义 `_pp_plan`（一个将模块 FQNs 映射到阶段的字典）。
2. `pp_size > 1` 在分布式部分中。
3. 一个包含调度和微批次大小的 `pipeline` 子配置。

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

- SDPA（Flash Attention 或 Efficient Attention 后端）或 Transformer Engine 注意力。SDPBackend.MATH 与 DTensor 不兼容。
- 注意力掩码会自动剥离；`is_causal=True` 通过 `attach_context_parallel_hooks()` 注册的前向预钩设置。

### 工作原理

1. 模型分片后，`apply_model_infrastructure()` 在每个模型部分（对于非 TE 模型）调用 `attach_context_parallel_hooks()`。
2. 在每个训练步骤中，`make_cp_batch_and_ctx()` 创建一个 CP 上下文管理器，沿序列维度分片批次并设置 `torch.distributed.tensor.experimental.context_parallel`。
3. 对于 TE 注意力模型，`make_cp_batch_for_te()` 使用 THD 格式并使用 TE 的 `thd_get_partitioned_indices` 进行分片。

### 带序列打包的 CP

CP 可以与打包序列一起工作。`packed_sequence_size` 必须能被 `cp_size` 整除。使用 TE 时，通过 `_shard_thd_chunk_for_te()` 每个块进行分片。

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

设置 `ep_size > 1` 以在 GPU 上分布专家。这会创建一个与主 `device_mesh` 并列的单独的 `moe_mesh`：

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

尽管其名称如此，`megatron_fsdp` 并不支持专家并行（`ep_size > 1`）、流水线并行（`pp_size > 1`）或 `sequence_parallel`。使用 `fsdp2` 获取这些功能。

## 并行性尺寸指南

### 密集模型

| 模型大小 | TP | PP | CP | 策略 |
|---|---|---|---|---|
| < 3B | 1 | 1 | 1 | FSDP2（仅 DP） |
| 3-13B | 2-4 | 1 | 1 | FSDP2 + TP |
| 13-70B | 4-8 | 2-4 | 1 | FSDP2 + TP + PP |
| 70B+ | 8 | 4-8 | 1 | FSDP2 + TP + PP |
| 任何 + 长序列（8K+） | 如上 | 如上 | 2-8 | 添加 CP |

### MoE 模型

MoE 模型比具有相似总参数数量的密集模型需要更少的 TP，因为每个标记只有一部分参数是活跃的。EP 是主要的扩展维度：

| 模型 | TP | PP | EP | 备注 |
|---|---|---|---|---|
| 小型 MoE（<10B 总计） | 1 | 1 | 8 | 仅 EP |
| 中型 MoE（10-30B 总计） | 1-2 | 1 | 8 | 小型 TP 用于共享层 |
| 大型 MoE（100B+ 总计） | 1-2 | 4+ | 8-64 | PP 用于深度，EP 用于专家 |

### 硬件拓扑规则

- TP 必须保留在单个 NVLink 域内（一个节点，通常 8 个 GPU）。
- 使用 PP 或 DP 进行跨节点扩展。
- 跨 InfiniBand 的 TP 会严重降低吞吐量。

## 程序化 API（from_pretrained / from_config）

不使用 YAML 配方时，通过 Python 配置分布式训练：

```python
from nemo_automodel.components.distributed import (
    DistributedSetup,
    FSDP2Config,
    ParallelismSizes,
    initialize_distributed,
)

dist_env = initialize_distributed("nccl")
distributed_setup = DistributedSetup.build(
    strategy=FSDP2Config(sequence_parallel=True),
    parallelism_sizes=ParallelismSizes(tp_size=2),
    activation_checkpointing=True,
    world_size=dist_env.world_size,
)
```

或直接传递到 `from_pretrained`：

```python
from nemo_automodel import NeMoAutoModelForCausalLM

model = NeMoAutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-1B",
    distributed_setup=distributed_setup,
)
```

## 代码锚点

策略配置数据类：

```
components/distributed/config.py
    FSDP2Config       -- sequence_parallel, tp_plan, mp_policy, offload_policy,
                         activation_checkpointing, defer_fsdp_grad_sync
    MegatronFSDPConfig -- zero_dp_strategy, overlap_grad_reduce, overlap_param_gather, 等
    DDPConfig          -- activation_checkpointing 仅用
```

网格上下文（并行性的单一来源）：

```
components/distributed/mesh.py
    MeshContext  -- device_mesh, moe_mesh
                    属性：tp_size, pp_size, cp_size, ep_size, dp_size, dp_replicate_size
    MeshAxisName -- PP, DP, DP_REPLICATE, DP_SHARD, DP_SHARD_CP, DP_CP, CP, TP, EP, EP_SHARD
```

网格上下文和原始网格创建：

```
components/distributed/config.py
    DistributedSetup.build()      -- 从策略 + 并行性构建 MeshContext
components/distributed/mesh_utils.py
    _create_device_meshes()       -- 路由到 FSDP2/MegatronFSDP/DDP 原始网格创建
    _create_fsdp2_device_mesh()   -- 形状 (pp, dp_replicate, dp_shard, cp, tp) + 扁平化子网格
    _create_megatron_fsdp_device_mesh() -- 形状 (dp, cp, tp)
```

分布式管理器：

```
components/distributed/fsdp2.py          -- FSDP2Manager.parallelize()
components/distributed/megatron_fsdp.py  -- MegatronFSDPManager.parallelize()
components/distributed/ddp.py            -- DDPManager
```

流水线并行：

```
components/distributed/pipelining/config.py        -- PipelineConfig 数据类
components/distributed/pipelining/autopipeline.py  -- AutoPipeline 协调器
components/distributed/pipelining/functional.py    -- pipeline_model(), 调度创建
components/distributed/pipelining/hf_utils.py      -- PP 的 HF 模型验证
```

上下文并行：

```
components/distributed/context_parallel/utils.py
    make_cp_batch_and_ctx()            -- 创建 CP 上下文管理器 + 分片批次
    create_context_parallel_ctx()      -- 包装 torch.distributed.tensor.experimental.context_parallel
    attach_context_parallel_hooks()    -- 剥离注意力掩码，设置 is_causal=True
    make_cp_batch_for_te()             -- TE 特定的 CP 批次分片（THD 格式）
```

基础设施协调：

```
_transformers/infrastructure.py
    instantiate_infrastructure()    -- 配置对象 -> 运行时对象
    apply_model_infrastructure()    -- 对模型应用分片、PEFT、检查点
    _shard_pp()                     -- 流水线并行路径
    _shard_ep_fsdp()                -- EP + FSDP 路径（非 PP）
```

YAML 解析：

```
recipes/_dist_utils.py
    parse_distributed_section()  -- YAML 字典 -> 类型化配置 + 尺寸
    create_distributed_setup_from_config()  -- 配方适配器：解析 + 创建 DistributedSetup；不初始化 process group
```

MoE 配置：

```
components/distributed/config.py
    MoEParallelizerConfig  -- reshard_after_forward, ignore_router_for_ac, wrap_outer_model, 等
components/moe/config.py
    MoEConfig              -- n_routed_experts, n_activated_experts, score_func, 等
```

## 陷阱

1. **跨节点的 TP 毁坏吞吐量。** 始终将 TP 保留在单个 NVLink 域内。使用 PP 或 DP 进行跨节点扩展。

2. **PP 需要在模型类上定义 `_pp_plan`。** 并非所有 HF 模型都有这个。在启用 PP 之前检查 `validate_hf_model_for_pipeline_support()`。

3. **PP 泡沫降低 GPU 利用率。** 使用交错调度（`interleaved_1f1b`）和较小的微批次来减少泡沫时间。

4. **FSDP2 需要DTensor感知的状态字典保存。** 使用 `safetensors` 并设置 `save_consolidated: final` 进行最终的 HF 导出，或 `save_consolidated: false` 加上生成的 `model/consolidate.sh` 辅助程序进行离线导出。

5. **CP 需要兼容的注意力。** 仅 SDPA（Flash Attention 或 Efficient Attention）或 TE 注意力。`SDPBackend.MATH` 与 DTensor 不兼容。

6. **MoE EP 大小必须能整除 `dp_size * cp_size`。** 设备网格创建断言 `dp_cp_size % ep_size == 0`。

7. **MegatronFSDP 比较于 FSDP2 限制更多。** 它不支持 PP (`pp_size > 1`)、EP (`ep_size > 1`) 或 `sequence_parallel`。在这些组合上，`MeshContext` 验证会引发错误。

8. **DDP 支持的数据并行之外什么都没有。** 没有 TP、PP、CP、EP 或 HSDP。在任何这些上，验证会引发错误。

9. **激活检查点增加计算。** 它通过反向传播重新计算激活来节省内存，但增加了约 30% 的计算开销。

10. **混合精度策略必须匹配模型预期。** 默认的 bfloat16 策略适用于大多数模型。FP16 模型可能需要自定义的 `MixedPrecisionPolicy`。

11. **`packed_sequence_size` 在使用 CP 与打包序列时必须能被 `cp_size` 整除。**

12. **`dp_replicate_size` 仅用于 FSDP2。** 将它传递给 `megatron_fsdp` 或 `ddp` 会引发 `ValueError`。

## 验证

运行执行请求策略的最小配方。成功意味着退出代码为 0、有限损失、没有 NCCL 超时，并且日志输出与预期的 TP/PP/CP/EP 尺寸匹配。
