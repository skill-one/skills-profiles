# TP / DP / PP 通信重叠技能

有关稳定的背景和推荐级别，请参阅：

- @docs/training/communication-overlap.md

## 启用

最小桥接覆盖：

```python
from megatron.bridge.training.comm_overlap import CommOverlapConfig

cfg.model.tensor_model_parallel_size = 4
cfg.model.sequence_parallel = True
cfg.model.pipeline_model_parallel_size = 4
cfg.model.virtual_pipeline_model_parallel_size = 2

cfg.comm_overlap = CommOverlapConfig(
    tp_comm_overlap=True,
)

cfg.ddp.use_distributed_optimizer = True
cfg.ddp.overlap_grad_reduce = True
cfg.ddp.overlap_param_gather = True
```

可选的 TP 预设：

```python
from megatron.bridge.training.comm_overlap import userbuffers_bf16_h100_h12288_tp4_mbs1_seqlen2048

cfg.comm_overlap.tp_comm_overlap_cfg = userbuffers_bf16_h100_h12288_tp4_mbs1_seqlen2048
```

精度调节旋钮属于混合精度：

```python
cfg.mixed_precision.grad_reduce_in_fp32 = False
cfg.mixed_precision.fp8_param_gather = False
```

## 代码锚点

桥接重叠门控：

```439:449:src/megatron/bridge/training/comm_overlap.py
if self.user_comm_overlap_cfg.tp_comm_overlap is True:
    if model_cfg.tensor_model_parallel_size < 2:
        ...
    elif not model_cfg.sequence_parallel:
        ...
    elif not HAVE_TE:
        ...
```

PP 重叠选择：

```451:458:src/megatron/bridge/training/comm_overlap.py
if model_cfg.pipeline_model_parallel_size > 1:
    if vp_size > 1:
        comm_overlap_cfg.overlap_p2p_comm = True
        comm_overlap_cfg.batch_p2p_comm = False
    else:
        comm_overlap_cfg.overlap_p2p_comm = False
        comm_overlap_cfg.batch_p2p_comm = True
```

DP 重叠默认值：

```572:579:src/megatron/bridge/training/comm_overlap.py
if self.data_parallel_size > 1:
    comm_overlap_cfg.bucket_size = 128 * 1024 * 1024
    comm_overlap_cfg.overlap_grad_reduce = True
    comm_overlap_cfg.overlap_param_gather = True
```

启动时环境调节：

```570:609:src/megatron/bridge/recipes/run_plugins.py
executor.env_vars["CUDA_DEVICE_MAX_CONNECTIONS"] = str(cuda_device_max_connections)
...
executor.env_vars["NVTE_FWD_LAYERNORM_SM_MARGIN"] = str(self.layernorm_sm_margin)
executor.env_vars["NVTE_BWD_LAYERNORM_SM_MARGIN"] = str(self.layernorm_sm_margin)
```

## 陷阱

1. 如果 `sequence_parallel=False` 或 Transformer Engine 不可用，TP 重叠会静默禁用自身。
2. PP 重叠并非在所有 PP 情况下都启用。桥接仅在 `PP > 1` 且 `VPP > 1` 时自动选择 `overlap_p2p_comm=True`。
3. `bucket_size` 是一个参数计数旋钮，而不是字节大小旋钮。
4. `grad_reduce_in_fp32` 和 `fp8_param_gather` 应通过混合精度设置，而不是作为独立的 DDP 调节首先设置。
5. `CUDA_DEVICE_MAX_CONNECTIONS` 和 LayerNorm SM 边距是启动时插件设置，不是 `CommOverlapConfig` 字段。

## 验证

首先使用已提交的重叠单元覆盖率：

```bash
uv run python -m pytest tests/unit_tests/training/test_comm_overlap.py -q
```

如果 `nemo_run` 可用，可选的第二次检查：

```bash
uv run python -m pytest tests/unit_tests/recipes/test_run_plugins.py -q
```

成功标准：

- 第一个命令报告 `26 passed`
- 第二个命令在未跳过时验证插件拥有的环境接线
