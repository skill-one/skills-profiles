# CUDA 图

稳定文档：@docs/training/cuda-graphs.md
卡片：@skills/nemo-mbridge-perf-cuda-graphs/card.yaml

<!-- NVSkills CI 刷新：2026-06-15。无指令变更。 -->

## 它是什么

CUDA 图一次性捕获 GPU 操作并最小化主机驱动程序开销进行重放。桥接支持两种实现：

| `cuda_graph_impl` | 机制 | 范围支持 |
|---|---|---|
| `"local"` | MCore `FullCudaGraphWrapper` 包装整个前向+反向 | `full_iteration` |
| `"transformer_engine"` | TE `make_graphed_callables()` 每层 | `attn`, `mlp`, `moe`, `moe_router`, `moe_preprocess`, `mamba` |

## 快速决策

对于大多数训练工作负载，从 TE 范围图开始，然后在同一调度器、布局和容器上验证重放时间与即时执行：

- 密集模型：`attn`，然后可选 `mlp`
- 无丢弃 MoE：`attn moe_router moe_preprocess`
- VLM：相同的无丢弃-MoE 范围，但仅在真实数据路径稳定后使用

仅在您明确需要全迭代捕获并且可以满足更严格约束时使用 `local` + `full_iteration`。

对于重计算密集型工作负载：

- TE 范围图与选择性重计算自然配合
- 全重计算通常将您推向 `local` 全迭代图或完全放弃图

相关文档：

- @docs/training/cuda-graphs.md
- @docs/training/activation-recomputation.md

## 启用

### 本地全迭代图

```python
cfg.model.cuda_graph_impl = "local"
cfg.model.cuda_graph_scope = ["full_iteration"]
cfg.model.cuda_graph_warmup_steps = 3
cfg.model.use_te_rng_tracker = True
cfg.rng.te_rng_tracker = True
cfg.rerun_state_machine.check_for_nan_in_loss = False
cfg.ddp.check_for_nan_in_grad = False
```

### TE 范围图（密集模型）

```python
cfg.model.cuda_graph_impl = "transformer_engine"
cfg.model.cuda_graph_scope = ["attn"]           # 或 ["attn", "mlp"]
cfg.model.cuda_graph_warmup_steps = 3
cfg.model.use_te_rng_tracker = True
cfg.rng.te_rng_tracker = True
```

### TE 范围图（MoE 模型）

```python
cfg.model.cuda_graph_impl = "transformer_engine"
cfg.model.cuda_graph_scope = ["attn", "moe_router", "moe_preprocess"]
cfg.model.cuda_graph_warmup_steps = 3
cfg.model.use_te_rng_tracker = True
cfg.rng.te_rng_tracker = True
```

### 性能测试套件 CLI

```bash
uv run python scripts/performance/run_script.py \
  -m qwen \
  -mr qwen3_30b_a3b \
  --task pretrain \
  -g h100 \
  -c bf16 \
  -ng 16 \
  --cuda_graph_impl transformer_engine \
  --cuda_graph_scope attn,moe_router,moe_preprocess \
  ...
```

有效的 CLI 值位于 `scripts/performance/argument_parser.py`：

- `VALID_CUDA_GRAPH_IMPLS`: `["none", "local", "transformer_engine"]`
- `VALID_CUDA_GRAPH_SCOPES`: `["full_iteration", "attn", "mlp", "moe", "moe_router", "moe_preprocess", "mamba"]`

性能测试套件使用逗号分隔的 `--cuda_graph_scope` 值，并在 `--cuda_graph_impl` 不是 `none` 时自动启用 `model.use_te_rng_tracker` 加 `rng.te_rng_tracker`。

### 必须的约束

- `use_te_rng_tracker = True`（在 `gpt_provider.py` 中强制执行）
- 仅当 `cuda_graph_impl = "local"` 时使用 `full_iteration` 范围
- `full_iteration` 范围需要 `check_for_nan_in_loss = False`
- 不要组合 `moe` 范围和 `moe_router` 范围
- 张量形状必须是静态（固定的序列长度，固定的微批次大小）
- MoE 令牌无丢弃路由将图范围限制为密集模块
- 使用 `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` 时，设置
  `NCCL_GRAPH_REGISTER=0`（MCore 在架构 < sm_100 的本地实现上强制执行；
  TE 实现无条件断言）
- CPU 卸载与 CUDA 图不兼容
- `moe_preprocess` 范围需要 `moe_router` 范围也已设置

### 实际启动顺序

1. 首先稳定即时执行运行。
2. 修复序列长度和微批次大小。
3. 启用最窄的有用图范围。
4. 确认重放处于活动状态并且内存仍然可接受。
5. 在预热和捕获后比较即时执行与图重放迭代；不包括捕获步骤在稳态计时中。
6. 只有这样才可扩大范围或与重叠功能结合。

## 代码锚点

### 桥接配置和验证

```1524:1531:src/megatron/bridge/training/config.py
        # CUDA 图范围验证：使用 full_iteration 图时必须禁用 check_for_nan_in_loss
        if self.model.cuda_graph_impl == "local" and CudaGraphScope.full_iteration in self.model.cuda_graph_scope:
            assert not self.rerun_state_machine.check_for_nan_in_loss, (
                "check_for_nan_in_loss 必须在使用 full_iteration CUDA 图时禁用。 "
                "设置 rerun_state_machine.check_for_nan_in_loss=False."
            )
        if self.model.cuda_graph_impl == "none":
            self.model.cuda_graph_scope = []
```

### TE RNG 追踪器要求

```213:216:src/megatron/bridge/models/gpt_provider.py
        if self.cuda_graph_impl != "none":
            assert getattr(self, "use_te_rng_tracker", False), (
                "Transformer 引擎的 RNG 追踪器对于 cudagraphs 是必需的，它可以通过 "
                "设置 use_te_rng_tracker=True 启用。"
```

### 训练循环中的图创建和捕获

```231:255:src/megatron/bridge/training/train.py
    # 捕获 CUDA 图。
    cuda_graph_helper = None
    if model_config.cuda_graph_impl == "transformer_engine":
        cuda_graph_helper = TECudaGraphHelper(...)
    # ...
    if config.model.cuda_graph_impl == "local" and CudaGraphScope.full_iteration in config.model.cuda_graph_scope:
        forward_backward_func = FullCudaGraphWrapper(
            forward_backward_func, cuda_graph_warmup_steps=config.model.cuda_graph_warmup_steps
        )
```

### 预热后的 TE 图捕获

```338:350:src/megatron/bridge/training/train.py
        # 预热后捕获 CUDA 图。
        if (
            model_config.cuda_graph_impl == "transformer_engine"
            and cuda_graph_helper is not None
            and not cuda_graph_helper.graphs_created()
            and global_state.train_state.step - start_iteration == model_config.cuda_graph_warmup_steps
        ):
            if model_config.cuda_graph_warmup_steps > 0 and should_toggle_forward_pre_hook:
                disable_forward_pre_hook(model, param_sync=False)
            cuda_graph_helper.create_cudagraphs()
            if model_config.cuda_graph_warmup_steps > 0 and should_toggle_forward_pre_hook:
                enable_forward_pre_hook(model)
                cuda_graph_helper.cuda_graph_set_manual_hooks()
```

### RNG 初始化

```199:206:src/megatron/bridge/training/initialize.py
        _set_random_seed(
            rng_config.seed,
            rng_config.data_parallel_random_init,
            rng_config.te_rng_tracker,
            rng_config.inference_rng_tracker,
            use_cudagraphable_rng=(model_config.cuda_graph_impl != "none"),
            pg_collection=pg_collection,
        )
```

### 延迟 wgrad + CUDA 图交互

```522:555:src/megatron/bridge/training/comm_overlap.py
            cuda_graph_scope = getattr(model_cfg, "cuda_graph_scope", []) or []
            # ... 范围解析 ...
            if wgrad_in_graph_scope:
                assert is_te_min_version("2.12.0"), ...
                assert model_cfg.gradient_accumulation_fusion, ...
                if attn_scope_enabled:
                    assert not model_cfg.add_bias_linear and not model_cfg.add_qkv_bias, ...
```

### Perf harness 覆盖辅助程序

```102:124:scripts/performance/utils/overrides.py
def _set_cuda_graph_overrides(
    recipe, cuda_graph_impl=None, cuda_graph_scope=None
):
    # 设置 impl、scope，并自动启用 te_rng_tracker
```

### 图清理

```1414:1441:src/megatron/bridge/training/train.py
def _delete_cuda_graphs(cuda_graph_helper):
    # 删除 FullCudaGraphWrapper 和 TE 图对象以释放 NCCL 缓冲区
```

### MCore 类（在 3rdparty/Megatron-LM）

- `CudaGraphManager`：`megatron/core/transformer/cuda_graphs.py`
- `TECudaGraphHelper`：`megatron/core/transformer/cuda_graphs.py`
- `FullCudaGraphWrapper`：`megatron/core/full_cuda_graph.py`
- `CudaGraphScope` 枚举：`megatron/core/transformer/enums.py`

### 正面配方锚点

- `src/megatron/bridge/perf_recipes/deepseek/gb300/deepseek_v3.py`
- `src/megatron/bridge/perf_recipes/qwen/gb300/qwen3_moe.py`
- `src/megatron/bridge/perf_recipes/gpt_oss/gb300/gpt_oss.py`

### 测试

| 文件 | 覆盖率 |
|---|---|
| `tests/unit_tests/training/test_config.py` | `full_iteration` NaN-检查约束 |
| `tests/unit_tests/training/test_comm_overlap.py` | `delay_wgrad` + CUDA 图交互 |
| `tests/unit_tests/models/test_gpt_full_te_layer_autocast_spec.py` | 使用 CUDA 图的 TE autocast |
| `tests/functional_tests/test_groups/recipes/test_llama_recipes_pretrain_cuda_graphs.py` | 端到端本地和 TE 图冒烟测试 |
| `tests/unit_tests/recipes/kimi/test_kimi_k2.py` | TE + CUDA 图配方配置 |
| `tests/unit_tests/recipes/gpt/test_gpt3_175b.py` | TE + CUDA 图配方配置 |
| `tests/unit_tests/recipes/qwen_vl/test_qwen25_vl_recipes.py` | VLM CUDA 图设置 |

## 陷阱

1. **TE RNG 追踪器是强制的**：未设置 `use_te_rng_tracker=True` 和 `rng.te_rng_tracker=True` 而设置 `cuda_graph_impl` 将在提供程序中断言。

2. **`full_iteration` 需要禁用 NaN 检查**：整个前向+反向被捕获，因此损失 NaN 检查不能检查中间值。

3. **MoE 范围限制**：`moe` 范围和 `moe_router` 范围是互斥的。无丢弃 MoE 只能图 `moe_router` 和 `moe_preprocess`，不能完整专家调度。

4. **内存开销**：CUDA 图在整个图的生命周期中固定所有中间缓冲区（无内存重用）。TE 范围图增加几 GB；全迭代图可增加峰值内存 1.5–2×。`PP > 1` 会放大开销，因为每个阶段都持有自己的图。

5. **延迟 wgrad 交互**：当 `delay_wgrad_compute=True` 且注意力或 MoE 路由器在 `cuda_graph_scope` 中时，将应用附加约束：TE >= 2.12.0, `gradient_accumulation_fusion=True`，且无注意力偏差。

6. **可变长度序列会破坏图**：步骤之间序列长度必须保持恒定。如果需要打包，请使用填充打包序列。

7. **图清理是必需的**：CUDA 图对象持有 NCCL 缓冲区引用。桥接在训练结束时的 `_delete_cuda_graphs()` 中处理此问题，但早期退出必须显式调用它。

8. **较旧的 GPU 架构**：在计算能力 < 10.0（Blackwell 之前）的 GPU 上，使用 `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` 时设置 `NCCL_GRAPH_REGISTER=0`。在 MCore `CudaGraphManager`（cuda_graphs.py:1428）和 `TECudaGraphHelper`（cuda_graphs.py:1697）中强制执行。TE 实现无条件断言，无论架构如何。

9. **与 CPU 卸载不兼容**：CUDA 图不能与 CPU 卸载一起使用。在 MCore `transformer_config.py:1907` 中强制执行。

10. **MoE 重计算 + moe_router 范围**：当使用 `cuda_graph_impl = "transformer_engine"` 时，MoE 重计算与 `moe_router` CUDA 图范围不兼容。在 MCore `transformer_config.py:1977` 中强制执行。

11. **层级重计算需要 `full_iteration` 范围**：使用 `recompute_granularity="full"` 与 `recompute_num_layers`（重计算 N 个完整 Transformer 层）与 TE 范围图不兼容。MCore 称此为“全”粒度，尽管您在选择多少层——名称指的是重计算完整层，而不是完整模型。任何 TE 范围（`attn`、`mlp`、`moe_router` 等）都会断言：`AssertionError: full recompute 只能与全迭代 CUDA 图支持。` 这通常影响默认使用 TE 范围图的 FP8 配置（例如 `LLAMA3_70B_SFT_CONFIG_H100_FP8_CS_V1` 使用 `cuda_graph_impl="transformer_engine"`，`cuda_graph_scope="mlp"`）。修复：使用子模块重计算（`recompute_granularity="selective"` + `recompute_modules`），禁用 CUDA 图，或切换到 `local` + `full_iteration`。在 MCore `transformer_config.py:2001-2005` 中强制执行。另见 @skills/nemo-mbridge-perf-activation-recompute/SKILL.md。

12. **基准数字是工作负载特定的**：图胜利通常在主机开销可见时才是真实的，但确切收益取决于批形状、PP 深度、重计算、调度器后端以及即时执行基线是否已优化。

13. **成功的捕获不是加速保证**：在 2026-05-18，Qwen3 30B A3B H100 BF16 预训练使用全对全调度器成功捕获了 TE 范围的 `attn,moe_router,moe_preprocess` 图（48 个可图层，秩 0 上约 `6.9 s` 捕获时间），但重放迭代 5-8 平均 `42.00 s` 对比 `41.36 s` 的即时执行。将范围图视为启动候选并针对目标堆栈进行验证。
