# 弹性

稳定文档：@docs/training/resiliency.md, @docs/training/checkpointing.md
卡片：@skills/nemo-mbridge-resiliency/card.yaml

## 使能

### 容错（仅限Slurm）

#### 选项1：NeMo Run插件（推荐）

```python
from megatron.bridge.recipes.run_plugins import FaultTolerancePlugin
import nemo_run as run

task = run.Script(...)
run_plugins = [
    FaultTolerancePlugin(
        enable_ft_package=True,
        calc_ft_timeouts=True,
        num_in_job_restarts=3,
        num_job_retries_on_failure=2,
        initial_rank_heartbeat_timeout=1800,
        rank_heartbeat_timeout=300,
    )
]
run.run(task, plugins=run_plugins, executor=executor)
```

| 插件参数 | 默认值 | 描述 |
|---|---|---|
| `num_in_job_restarts` | 3 | 同一作业内的最大重启次数 |
| `num_job_retries_on_failure` | 2 | 失败时最大新作业启动次数 |
| `initial_rank_heartbeat_timeout` | 1800 | 首次心跳超时（秒） |
| `rank_heartbeat_timeout` | 300 | 后续心跳超时（秒） |

#### 选项2：直接配置 + ft_launcher

```python
from megatron.bridge.training.config import FaultToleranceConfig

cfg.ft = FaultToleranceConfig(
    enable_ft_package=True,
    calc_ft_timeouts=True,
    simulate_fault=False,
    simulated_fault_type="random",
)
```

使用`ft_launcher`启动（不能使用`torchrun`）：

```bash
export GROUP_RANK=0  # 非Slurm环境需要
ft_launcher \
    --rdzv_backend=c10d --rdzv_endpoint=${MASTER_ADDR}:${MASTER_PORT} \
    --nnodes=${NUM_NODES} --nproc-per-node=${NUM_GPUS_PER_NODE} \
    --ft-rank_section_timeouts=setup:600,step:180,checkpointing:420 \
    --ft-rank_out_of_section_timeout=300 \
    your_training_script.py
```

| 配置参数 | 默认值 | 描述 |
|---|---|---|
| `enable_ft_package` | False | 启用容错 |
| `calc_ft_timeouts` | False | 自动计算最优超时 |
| `simulate_fault` | False | 启用故障模拟用于测试 |
| `simulated_fault_type` | `"random"` | `"rank_hung"`, `"rank_killed"`, 或 `"random"` |
| `simulated_fault_rank` | None | 特定rank故障（若为None则随机） |
| `simulated_fault_base_delay` | 0 | 模拟故障前的基本延迟 |

基于部分的超时监控独立覆盖设置、训练步骤、检查点和部分外超时。超时值在`calc_ft_timeouts=True`时保存到`ft_state.json`供后续运行使用。

### NVRx延迟检测

```python
from megatron.bridge.training.config import NVRxStragglerDetectionConfig

cfg.nvrx_straggler = NVRxStragglerDetectionConfig(
    enabled=True,
    report_time_interval=300.0,
    calc_relative_gpu_perf=True,
    calc_individual_gpu_perf=True,
    num_gpu_perf_scores_to_print=5,
    gpu_relative_perf_threshold=0.7,
    gpu_individual_perf_threshold=0.7,
    stop_if_detected=False,
    enable_logging=True,
)
```

| 参数 | 默认值 | 描述 |
|---|---|---|
| `enabled` | False | 启用延迟检测 |
| `report_time_interval` | 300.0 | 延迟检查间隔（秒） |
| `calc_relative_gpu_perf` | True | 相互比较rank性能 |
| `calc_individual_gpu_perf` | True | 跟踪每个rank随时间的性能退化 |
| `gpu_relative_perf_threshold` | 0.7 | 相对性能阈值（0-1） |
| `gpu_individual_perf_threshold` | 0.7 | 单独性能阈值（0-1） |
| `stop_if_detected` | False | 检测到延迟时终止训练 |
| `num_gpu_perf_scores_to_print` | 5 | 打印的最佳/最差分数数量 |
| `profiling_interval` | 1 | 检测器的分析间隔（秒） |

### 预占

#### 插件（Slurm）

```python
from megatron.bridge.recipes.run_plugins import PreemptionPlugin

plugins = [
    PreemptionPlugin(
        preempt_time=60,
        enable_exit_handler=True,
        enable_exit_handler_for_data_loader=False,
    )
]
```

| 插件参数 | 默认值 | 描述 |
|---|---|---|
| `preempt_time` | 60 | 超过作业限制前的秒数发送信号 |
| `enable_exit_handler` | True | 在训练中启用信号处理器 |
| `enable_exit_handler_for_data_loader` | False | 为数据加载器工作进程启用 |

#### 直接配置

```python
import signal
cfg.train.exit_signal_handler = True
cfg.train.exit_signal = signal.SIGTERM
cfg.train.exit_signal_handler_for_dataloader = False
```

### 重启状态机（实验性）

```python
from megatron.bridge.training.config import RerunStateMachineConfig

cfg.rerun_state_machine = RerunStateMachineConfig(
    rerun_mode="validate_results",
    check_for_nan_in_loss=True,
    check_for_spiky_loss=False,
    spiky_loss_factor=10.0,
)
```

| 参数 | 默认值 | 描述 |
|---|---|---|
| `rerun_mode` | `"disabled"` | `"disabled"`, `"validate_results"`, `"report_determinism_stats"` |
| `check_for_nan_in_loss` | True | 检查损失中的NaN |
| `check_for_spiky_loss` | False | 检查意外大的损失 |
| `spiky_loss_factor` | 10.0 | 损失如果 > factor * 最大观测值（对大模型增加） |

退出代码：16 = 恢复以消除歧义，17 = 验证失败。

### 进程内重启（实验性）

```python
from megatron.bridge.training.config import InProcessRestartConfig

cfg.inprocess_restart = InProcessRestartConfig(
    enabled=True,
    granularity="node",
    soft_timeout=60.0,
    hard_timeout=90.0,
)
```

| 参数 | 默认值 | 描述 |
|---|---|---|
| `enabled` | False | 启用进程内重启 |
| `active_world_size` | None | 执行工作负载的rank（其余为热储备） |
| `granularity` | `"node"` | `"node"` 或 `"rank"` 重启粒度 |
| `max_iterations` | None | 最大重启尝试次数（None = 无限） |
| `soft_timeout` | 60.0 | 检测GIL释放的挂起（秒） |
| `hard_timeout` | 90.0 | 强制终止挂起的rank（秒） |
| `heartbeat_interval` | 30.0 | 心跳间隔（秒） |
| `heartbeat_timeout` | 60.0 | 缺失心跳超时（秒） |
| `barrier_timeout` | 120.0 | 分布式屏障超时（秒） |
| `completion_timeout` | 120.0 | 完成屏障超时（秒） |
| `empty_cuda_cache` | True | 重启时清除CUDA缓存 |
| `max_rank_faults` | None | 最大rank故障前终止 |
| `monitor_process_logdir` | None | 监控日志目录 |

需要的环境变量：

```bash
export TORCH_CPP_LOG_LEVEL=error
export TORCH_NCCL_RETHROW_CUDA_ERRORS=0
export NCCL_NVLS_ENABLE=0
```

PyTorch NCCL看门狗超时必须超过`hard_timeout`。NeMo-Run的Slurm执行器不受支持；直接使用`srun --kill-on-bad-exit=0`启动。

### 异步检查点保存

```python
cfg.checkpoint.async_save = True
cfg.checkpoint.ckpt_format = "torch_dist"
```

### 本地检查点（NVRx）

```python
cfg.checkpoint.non_persistent_local_ckpt_dir = "/local/scratch/ckpt"
cfg.checkpoint.non_persistent_local_ckpt_algo = "fully_parallel"
```

## 代码锚点

### 容错
- 配置：`src/megatron/bridge/training/config.py` — `FaultToleranceConfig`
- 运行时：`src/megatron/bridge/training/fault_tolerance.py`
- 插件：`src/megatron/bridge/recipes/run_plugins.py` — `FaultTolerancePlugin`
- 性能插件：`scripts/performance/nemo-mbridge-resiliency_plugins.py`
- 测试：`tests/unit_tests/training/test_fault_tolerance.py`
- 示例：`examples/training_features/nemo-mbridge-resiliency/fault_tolerance/`

### 延迟检测
- 配置：`src/megatron/bridge/training/config.py` — `NVRxStragglerDetectionConfig`
- 运行时：`src/megatron/bridge/training/nvrx_straggler.py`
- 训练循环：`src/megatron/bridge/training/train.py` — `check_nvrx_straggler_detection`
- 测试：`tests/unit_tests/training/test_nvrx_straggler.py`, `tests/functional_tests/training/test_nvrx_straggler.py`
- 示例：`examples/training_features/nemo-mbridge-resiliency/straggler_detection/`

### 进程内重启
- 配置：`src/megatron/bridge/training/config.py` — `InProcessRestartConfig`
- 运行时：`src/megatron/bridge/training/inprocess_restart.py`
- 入口点：`src/megatron/bridge/training/pretrain.py` — `maybe_wrap_for_inprocess_restart`
- 测试：`tests/unit_tests/training/test_inprocess_restart.py`, `tests/functional_tests/training/test_inprocess_restart.py`

### 预占
- 插件：`src/megatron/bridge/recipes/run_plugins.py` — `PreemptionPlugin`
- 信号处理器：`src/megatron/bridge/training/utils/sig_utils.py`
- 测试：`tests/unit_tests/recipes/test_run_plugins.py`

### 重启状态机
- 配置：`src/megatron/bridge/training/config.py` — `RerunStateMachineConfig`
- 初始化：`src/megatron/bridge/training/initialize.py` — `init_rerun_state`

### 检查点
- 异步保存：`src/megatron/bridge/training/checkpointing.py` — `schedule_async_save`
- 本地ckpt：`src/megatron/bridge/training/checkpointing.py` — `LocalCheckpointManager`
- 测试：`tests/functional_tests/training/test_local_checkpointing.py`

## 陷阱

1. **ft_launcher，不是torchrun**：直接`FaultToleranceConfig`需要`ft_launcher`。使用`torchrun`会静默禁用FT。对于非Slurm，设置`GROUP_RANK=0`。

2. **异步保存需要torch_dist**：`async_save=True`仅适用于`ckpt_format="torch_dist"`。其他格式会静默失败或报错。

3. **IPR + NeMo-Run**：进程内重启与NeMo-Run或Slurm预占插件不兼容。需要特定的PyTorch/NCCL版本和环境变量。

4. **NVRx vs 旧版延迟检测**：存在两个检测器。使用NVRx（`nvrx_straggler`）；不要同时启用两者。

5. **stop_if_detected默认值**：NVRx记录但默认不停止训练。设置`stop_if_detected=True`以自动终止。

6. **NCCL看门狗 vs hard_timeout**：对于IPR，NCCL看门狗超时必须超过`hard_timeout`，否则PyTorch会在恢复前终止进程。

7. **重启状态机是alpha**：使用`check_for_nan_in_loss=True`进行NaN检测，但不要依赖完整的重启工作流。

## 验证

### 容错
```bash
./examples/training_features/nemo-mbridge-resiliency/fault_tolerance/run_fault_tolerance.sh
./examples/training_features/nemo-mbridge-resiliency/fault_tolerance/run_fault_tolerance.sh --simulate-fault
```
查找`[FaultTolerance]` / `[RankMonitorServer]`日志行中的部分超时。模拟故障应触发从检查点重启。

### 延迟检测
```bash
uv run python -m torch.distributed.run --nproc_per_node=2 \
    examples/training_features/nemo-mbridge-resiliency/straggler_detection/straggler_detection_example.py
```
查找包含每个rank分数的`GPU相对性能`和`GPU单独性能`报告。

### 异步检查点
在日志中查找`Scheduling async checkpoint save`。训练迭代应继续，同时检查点文件正在写入。

### 进程内重启
```bash
pytest tests/functional_tests/training/test_inprocess_restart.py -v
```
需要兼容的PyTorch/NCCL版本。
