# CPU卸载

## 参考文献

- 稳定文档：@docs/training/cpu-offloading.md
- 结构化元数据：@skills/nemo-mbridge-perf-cpu-offloading/card.yaml

## 它是什么

两种独立机制将数据从GPU内存移动到CPU内存：

| 机制 | 配置命名空间 | 卸载内容 | PP限制 |
|---|---|---|---|
| 激活卸载 | `model.cpu_offloading*` | 每个Transformer层的激活（可选地包括权重） | PP必须为1 |
| 优化器卸载 | `optimizer.optimizer_cpu_offload` | 通过`HybridDeviceOptimizer`的Adam优化器状态（动量+方差） | 无 |

## 快速决策

| 情况 | 建议 |
|---|---|
| 大型MoE模型（30B+），需要PP > 1 | 优化器卸载 — 激活卸载受PP=1限制 |
| 小型/中型模型，PP=1适用，激活内存占主导 | 激活卸载 |
| 希望可调节内存-速度权衡 | 带有分数`optimizer_offload_fraction`的优化器卸载 |
| 吞吐量是首要任务 | 不要启用 — 卸载始终会增加开销 |
| 需要CUDA图 | 仅优化器卸载 — 激活卸载不兼容 |
| 内存压力适中 | 以25–50%分数进行优化器卸载以获得最佳效率 |

## 启用

### 优化器CPU卸载（推荐用于大型模型）

```python
cfg.optimizer.optimizer_cpu_offload = True
cfg.optimizer.optimizer_offload_fraction = 1.0
cfg.optimizer.overlap_cpu_optimizer_d2h_h2d = True
```

CLI覆盖：

```bash
optimizer.optimizer_cpu_offload=True \
optimizer.optimizer_offload_fraction=0.5 \
optimizer.overlap_cpu_optimizer_d2h_h2d=True
```

### 激活CPU卸载（仅限小型/中型模型）

```python
cfg.model.cpu_offloading = True
cfg.model.cpu_offloading_num_layers = 16
cfg.model.cpu_offloading_activations = True
cfg.model.cpu_offloading_weights = False

cfg.model.pipeline_model_parallel_size = 1
cfg.model.recompute_granularity = None
cfg.model.cuda_graph_impl = "none"
```

## 配置参数参考

### 优化器卸载

| 参数 | 默认值 | 描述 |
|-----------|---------|-------------|
| `optimizer_cpu_offload` | `False` | 主开关 |
| `optimizer_offload_fraction` | `0.0` | CPU上的优化器状态分数（0.0–1.0） |
| `overlap_cpu_optimizer_d2h_h2d` | `False` | 将GPU↔CPU传输与计算重叠 |
| `use_torch_optimizer_for_cpu_offload` | `False` | 使用`torch.optim`而不是融合优化器 |

### 激活卸载

| 参数 | 默认值 | 描述 |
|-----------|---------|-------------|
| `cpu_offloading` | `False` | 主开关 |
| `cpu_offloading_num_layers` | `0` | 要卸载的Transformer层数（0到num_layers-1） |
| `cpu_offloading_activations` | `True` | 卸载激活 |
| `cpu_offloading_weights` | `False` | 卸载权重 |
| `cpu_offloading_double_buffering` | `False` | 在重新加载时跨层使用双缓冲 |

## 兼容性和限制

### 激活卸载

- `pipeline_model_parallel_size`必须为1
- `recompute_granularity`必须为`None`
- 不能与`fine_grained_activation_offloading`结合使用
- 不能与CUDA图结合使用
- `cpu_offloading_num_layers`必须在`[0, num_layers-1)`范围内

### 优化器卸载

- 需要`use_distributed_optimizer = True`（大多数配方中的默认值）
- 无PP、重新计算或CUDA图限制
- `optimizer_offload_fraction`必须在`[0.0, 1.0]`范围内

### 实际：大型MoE模型

对于Qwen3-30B-A3B和类似的大型MoE模型，激活卸载被阻塞。PP=1的限制意味着每个GPU持有所有48层；模型权重+优化器状态（~70 GB）单独超过H100 80 GB容量。

## 最小可运行命令

```bash
uv run python scripts/training/run_recipe.py \
  --recipe qwen3_30b_a3b_pretrain_config \
  optimizer.optimizer_cpu_offload=True \
  optimizer.optimizer_offload_fraction=0.5 \
  train.train_iters=20 \
  train.global_batch_size=8 \
  train.micro_batch_size=1
```

## 验证

### 单元测试

```bash
uv run python -m pytest \
  tests/unit_tests/models/test_gpt_full_te_layer_autocast_spec.py -k "cpu_offload" \
  tests/unit_tests/peft/test_utils.py -k "cpu_offload" -q
```

### 成功标准

- 选择的卸载模式通过配置验证
- 训练完成时没有OOM或NCCL错误
- 损失与未卸载的基线匹配（最大差值 < 0.001）
- 内存使用按卸载分数成比例下降

## 代码锚点

### MCore激活卸载限制

```1296:1310:3rdparty/Megatron-LM/megatron/core/transformer/transformer_config.py
        if self.cpu_offloading and (
            self.cpu_offloading_num_layers < 0 or self.cpu_offloading_num_layers >= self.num_layers
        ):
            raise ValueError(...)

        if self.cpu_offloading and self.pipeline_model_parallel_size > 1:
            raise ValueError(
                "Currently there is no support for Pipeline parallelism with CPU offloading"
            )

        if self.cpu_offloading and self.recompute_granularity is not None:
            raise ValueError(
                "CPU offloading does not work when activation recomputation is enabled"
            )
```

### MCore CUDA图不兼容

```1943:1944:3rdparty/Megatron-LM/megatron/core/transformer/transformer_config.py
            if self.cpu_offloading:
                raise ValueError("CUDA graphs not supported with CPU offloading.")
```

### MCore细粒度卸载互斥

```1427:1430:3rdparty/Megatron-LM/megatron/core/transformer/transformer_config.py
        if self.fine_grained_activation_offloading:
            assert (
                not self.cpu_offloading
            ), "fine_grained_activation_offloading cannot be enabled with cpu_offloading."
```

### MCore HybridDeviceOptimizer实例化

```480:518:3rdparty/Megatron-LM/megatron/core/optimizer/__init__.py
        if config.optimizer_cpu_offload:
            # ... setup cpu/gpu optimizer classes ...
            optimizer = HybridDeviceOptimizer(
                param_groups,
                offload_fraction=config.optimizer_offload_fraction,
                cpu_optimizer_cls=cpu_optimizer_cls,
                gpu_optimizer_cls=gpu_optimizer_cls,
                overlap_cpu_optimizer_d2h_h2d=config.overlap_cpu_optimizer_d2h_h2d,
                pin_cpu_grads=config.pin_cpu_grads,
                pin_cpu_params=config.pin_cpu_params,
            )
```

### Bridge CUDA图保护

```232:234:src/megatron/bridge/models/gpt_full_te_layer_autocast_spec.py
        assert not config.cpu_offloading and config.recompute_granularity is None, "Cudagraphs not supported"
```

### Bridge PEFT中的激活卸载

```621:631:src/megatron/bridge/peft/utils.py
        if self.config.cpu_offloading and self.config.cpu_offloading_activations:
            x.activation_offloading = True
        x, _ = self.linear_in(x)
        x = self.activation(x)
        if self.config.cpu_offloading and self.config.cpu_offloading_activations:
            x.activation_offloading = True
        x, _ = self.linear_out(x)
```

## 故障诊断

| 症状 | 可能原因 | 如何确认 | 修复 |
|---|---|---|---|
| `Currently there is no support for Pipeline parallelism with CPU offloading` | 激活卸载 + PP > 1 | 检查`pipeline_model_parallel_size` | 设置PP=1或使用优化器卸载 |
| `CPU offloading does not work when activation recomputation is enabled` | 激活卸载 + 重新计算 | 检查`recompute_granularity` | 设置`recompute_granularity=null` |
| `fine_grained_activation_offloading cannot be enabled with cpu_offloading` | 两种卸载模式都启用 | 检查两个标志 | 使用其中一个或另一个 |
| `CUDA graphs not supported with CPU offloading` | CUDA图 + 激活卸载 | 检查`cuda_graph_impl` | 设置`cuda_graph_impl="none"` |
| 激活卸载OOM | 模型太大无法用于PP=1 | 检查分配的内存与80 GB | 使用PP > 1的优化器卸载 |
| 极端减速（>4x） | 100%优化器卸载，CPU Adam瓶颈 | 比较不同分数的迭代时间 | 减少分数或启用`overlap_cpu_optimizer_d2h_h2d` |
| 部分优化器卸载OOM | 此配置的卸载不足 | 在不同分数下检查内存 | 增加分数或添加PP |

## 已知限制

- 激活卸载需要PP=1，使其不适用于需要流水线并行的大型模型（30B+ MoE）。
- 优化器卸载吞吐量惩罚随线性增长（25%时~1.9x，100%时~4.2x对于Qwen3-30B-A3B）。
- D2H/H2D重叠仅提供~7%的加速，因为CPU Adam计算是主要瓶颈。
- `fine_grained_activation_offloading`是另一种模块级方法，可与PP > 1一起使用，但不能与层级`cpu_offloading`结合使用。
