# Megatron FSDP 功能

有关稳定背景和推荐级别的信息，请参阅：

- @docs/training/megatron-fsdp.md
- @skills/nemo-mbridge-perf-megatron-fsdp/card.yaml

## 启用方式

Bridge 中的最小 Megatron FSDP 覆盖：

```python
cfg.dist.use_megatron_fsdp = True
cfg.ddp.use_megatron_fsdp = True
cfg.ddp.data_parallel_sharding_strategy = "optim_grads_params"
cfg.ddp.average_in_collective = False
cfg.checkpoint.ckpt_format = "fsdp_dtensor"
```

示例配方修复：

```python
cfg = llama3_8b_pretrain_config()
cfg.dist.use_megatron_fsdp = True
cfg.ddp.use_megatron_fsdp = True
cfg.ddp.data_parallel_sharding_strategy = "optim_grads_params"
cfg.ddp.average_in_collective = False
cfg.checkpoint.ckpt_format = "fsdp_dtensor"
cfg.checkpoint.save = "/tmp/fsdp_ckpts"
cfg.checkpoint.load = None
```

性能测试注意事项：

```bash
python scripts/performance/launch.py --use_megatron_fsdp true
```

## 代码锚点

Bridge 配置定义：

```148:154:src/megatron/bridge/training/config.py
use_megatron_fsdp: bool = False
"""使用 Megatron 的全分片数据并行。不能与 use_torch_fsdp2 同时使用。"""

use_torch_fsdp2: bool = False
"""使用 torch FSDP2 实现。FSDP2 目前与流水线并行不兼容。
它仍然处于不稳定发布阶段，因此可能存在错误或其他潜在问题。"""
```

Bridge 验证：

```1533:1578:src/megatron/bridge/training/config.py
if self.dist.use_megatron_fsdp and self.dist.use_torch_fsdp2:
    raise ValueError(...)
...
assert not self.dist.use_tp_pp_dp_mapping, "use_tp_pp_dp_mapping 与 Megatron FSDP 不兼容"
...
assert self.checkpoint.ckpt_format == "fsdp_dtensor", (
    "Megatron FSDP 仅支持 fsdp_dtensor 检查点格式"
)
```

运行时包装器选择：

```217:243:src/megatron/bridge/models/common/unimodal.py
if use_megatron_fsdp:
    DP = FullyShardedDataParallel
elif use_torch_fsdp2:
    DP = TorchFullyShardedDataParallel
else:
    DP = DistributedDataParallel
...
DP(
    config=get_model_config(model_chunk),
    ddp_config=ddp_config,
    module=model_chunk,
    ...
    pg_collection=pg_collection,
)
```

性能测试覆盖：

```74:98:scripts/performance/utils/overrides.py
recipe.ddp.use_megatron_fsdp = True
recipe.ddp.data_parallel_sharding_strategy = "optim_grads_params"
recipe.ddp.keep_fp8_transpose_cache = False
recipe.ddp.average_in_collective = False
...
recipe.checkpoint.load = None
```

## 陷阱

1. 公共配方通常暴露 `use_megatron_fsdp`，但默认仍为 `ckpt_format="torch_dist"`。如果启用保存/加载，则切换到 `fsdp_dtensor`。
2. `use_torch_fsdp2` 存在，但在验证分支上，Bridge 在训练前仍然失败，因为 `_ddp_wrap` 传递了 `pg_collection`。
3. CPU 卸载仅在 `pipeline_model_parallel_size == 1` 且禁用激活重新计算时有效。
4. 上游警告称，FSDP 和 TP/CP 在 Hopper 及更早版本上可能需要不同的 `CUDA_DEVICE_MAX_CONNECTIONS` 设置。
5. Megatron FSDP 和 FSDP2 互斥。

## 验证

使用现有的 2-GPU 功能性冒烟测试：

```bash
CUDA_VISIBLE_DEVICES=0,1 uv run python -m torch.distributed.run --nproc_per_node=2 \
  -m pytest tests/functional_tests/training/test_megatron_fsdp.py::TestMegatronFSDP::test_fsdp_pretrain_basic -v -s
```

成功标准：

- Pytest 报告 `1 passed`
- 日志在最后迭代时显示有限损失
- 运行结束时不出现检查点格式断言
