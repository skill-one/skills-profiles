# 层级上下文并行技能

该技能涵盖层级上下文并行性：使用 `cp_comm_type="a2a+p2p"` 并通过 `hierarchical_context_parallel_sizes` 进行配置的嵌套上下文并行处理组。

关于层级CP是什么、何时使用以及决策树（`a2a+p2p` vs 纯 `a2a` vs `p2p`），请参阅：

- @docs/training/hierarchical-context-parallel.md
- @skills/nemo-mbridge-perf-hierarchical-context-parallel/card.yaml

## 启用方式

最小化桥接器覆盖：

```python
cfg.model.context_parallel_size = 4
cfg.model.cp_comm_type = "a2a+p2p"
cfg.model.hierarchical_context_parallel_sizes = [2, 2]
cfg.dist.use_decentralized_pg = False
```

所需约束条件：

- `prod(hierarchical_context_parallel_sizes) == context_parallel_size`
- `seq_length % (2 * context_parallel_size) == 0`
- Transformer Engine `>= 1.12.0`

## 代码锚点

上游配置和验证：

```45:54:3rdparty/Megatron-LM/megatron/core/model_parallel_config.py
context_parallel_size: int = 1
"""将网络输入沿序列维度在GPU排名之间进行拆分。"""

hierarchical_context_parallel_sizes: Optional[list[int]] = None
"""层级上下文并行的程度。用户应提供一个列表来指定不同层级的尺寸。以a2a+p2p cp通信类型为例，它包含两个层级的组，因此列表的第一个值表示a2a通信类型的组大小，第二个值表示p2p通信类型的组大小。"""
```

```428:433:3rdparty/Megatron-LM/megatron/training/arguments.py
if args.hierarchical_context_parallel_sizes:
    from numpy import prod
    assert args.context_parallel_size == prod(args.hierarchical_context_parallel_sizes)
if "a2a+p2p" in args.cp_comm_type:
    assert args.hierarchical_context_parallel_sizes is not None, \
    "--hierarchical-context-parallel-sizes must be set when a2a+p2p is used in cp comm"
```

桥接器MPU路径：

```613:648:src/megatron/bridge/training/initialize.py
parallel_state.initialize_model_parallel(
    ...
    context_parallel_size=model_config.context_parallel_size,
    hierarchical_context_parallel_sizes=model_config.hierarchical_context_parallel_sizes,
    ...
)
...
return ProcessGroupCollection.use_mpu_process_groups()
```

桥接器去中心化-PG路径：

```503:524:src/megatron/bridge/training/initialize.py
pg_collection = ProcessGroupCollection(
    ...
    cp=cp_pg,
    tp_cp=tp_cp_pg,
    hcp=None,
    ep=ep_pg,
    ...
)
```

## 实现映射

上述代码锚点显示了配置声明和参数验证。

### 验证（MCore）

`TransformerConfig.__post_init__` 强制要求 `a2a+p2p` 需要HCP尺寸，并且乘积与CP匹配。

### 进程组创建

`parallel_state.initialize_model_parallel` 在提供HCP尺寸时通过 `create_hierarchical_groups` 创建层级CP子组。桥接器目前通过MPU支持的 `ProcessGroupCollection` 获取这些组。

### TE集成

`TEDotProductAttention` 在使用 `a2a+p2p` 时将层级组传递给Transformer Engine。需要 **Transformer Engine >= 1.12.0**。

## 陷阱

1. **桥接器HCP目前仅支持MPU**：如果 `use_decentralized_pg=True`，桥接器初始化扁平CP组并将HCP未设置。
2. **目前没有检查入的桥接器配方**直接执行HCP。
3. **单GPU负载辅助工具**清除 `hierarchical_context_parallel_sizes`。
4. **在旧版本栈上静默损坏训练**：如果你使用 `a2a+p2p` 而未设置 `hierarchical_context_parallel_sizes`，MCore现在会断言。旧版本会静默禁用CP通信，因此每个排名仅关注其本地块，并产生具有损坏梯度的虚假高吞吐量。
5. **乘积必须匹配**：`prod(hierarchical_context_parallel_sizes)` 必须精确等于 `context_parallel_size`。不匹配会触发断言。
6. **在日志中验证**：查找进程组初始化输出。你应该看到 `HIERARCHICAL_CONTEXT_PARALLEL_GROUPS` 被创建。如果你只看到 `CONTEXT_PARALLEL_GROUP`，HCP未激活。

## 验证

目前还没有专门针对HCP的桥接器端到端测试（参见 @skills/nemo-mbridge-perf-hierarchical-context-parallel/card.yaml
`follow_up_validation`）。请使用现有的单元测试和日志检查代替。

运行去中心化-PG单元测试以确认扁平CP行为是否保持：

```bash
uv run python -m pytest tests/unit_tests/training/test_decentralized_pg.py -q
```

对于手动烟雾测试，使用小型配方和 `cp_comm_type=a2a+p2p` 加上 `hierarchical_context_parallel_sizes=[2,2]` 启动4-GPU运行：

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 uv run python -m torch.distributed.run --nproc_per_node=4 \
  scripts/training/run_recipe.py \
  --recipe llama32_1b_pretrain_config \
  model.context_parallel_size=4 \
  model.cp_comm_type=a2a+p2p \
  "model.hierarchical_context_parallel_sizes=[2,2]" \
  train.train_iters=2
```

成功标准：

- 日志显示 `HIERARCHICAL_CONTEXT_PARALLEL_GROUPS` 被创建
- 训练至少完成一步且无错误
- 如果你只看到 `CONTEXT_PARALLEL_GROUP`，HCP未激活
