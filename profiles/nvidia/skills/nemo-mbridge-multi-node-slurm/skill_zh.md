# 多节点 Slurm

将单节点 `uv run python -m torch.distributed.run` 命令转换为支持 Enroot 容器的多节点 Slurm sbatch 脚本，并调试常见的多节点故障。

## 首次回答清单

在转换或调试 Bridge 多节点作业时，按以下顺序回答：

1. 优先为到达 `initialize.py` 的 Bridge 脚本使用 **srun-native** 启动模式：`#SBATCH --ntasks-per-node=8` 和直接的 `srun ... uv run python <script> ...` 启动。不要将这些作业包装在 `python -m torch.distributed.run` 中。
2. 说明 Bridge 在 `initialize.py` 分布式初始化期间从 SLURM 变量中派生 `RANK`、`WORLD_SIZE`、`LOCAL_RANK`、`MASTER_ADDR` 和 `MASTER_PORT`。
3. 要求共享路径和匹配的容器挂载，用于存储库、数据、日志、`HF_HOME`、`UV_CACHE_DIR` 和 `NEMO_HOME`。
4. 对于 NCCL 超时报告，在猜测之前先进行以下首次日志检查：
   - 在过滤警告/帧噪声时，grep 实际错误
   - 查看 `Failures:` 以找到第一个失败的排名和节点
   - grep `ncclUniqueId`、`timeout` 或 `crash on rank 0`

## 两种方法：srun-native 与 uv run torch.distributed

| 方法 | `ntasks-per-node` | 进程启动 | 适用于 |
|---|---|---|---|
| **srun-native**（推荐） | 8 | Slurm 在每个节点上启动 8 个任务 | 转换、推理、Bridge 脚本 |
| **uv run torch.distributed**（遗留） | 1 | `uv run python -m torch.distributed.run` 在每个节点上启动 8 个进程 | MLM pretrain_gpt.py |

**优先使用 srun-native** — 更简单，避免了 TRAIN_CMD 的 shell 转义问题。Megatron Bridge 通过 `common_utils.py` 辅助函数自动从 SLURM 环境变量（`SLURM_PROCID`、`SLURM_NTASKS`、`SLURM_LOCALID`、`SLURM_NODELIST`）中派生 `RANK`、`WORLD_SIZE`、`LOCAL_RANK`、`MASTER_ADDR`、`MASTER_PORT`（在 `initialize.py` 分布式初始化期间调用），因此您永远不需要手动设置它们。

## 集群环境

使用共享文件系统存储存储库、数据、日志、`HF_HOME`、`UV_CACHE_DIR` 和 `NEMO_HOME`。`NEMO_HOME` 不能使用容器本地默认值（`/root/.cache/nemo`），因为多节点 SFT/PEFT 作业在节点 0 上准备的打包序列数据必须对其他节点可见。

不要在 sbatch 模板和日志中包含凭证。通过调度程序环境或受限的密钥文件提供 `HF_TOKEN`、`GH_TOKEN` 和 `WANDB_API_KEY`，并且永远不要在脚本正文中硬编码令牌值。对于复制粘贴的环境和 sbatch 模板，请参阅 `references/templates.md`。

### 日志目录

```text
<SHARED_FS>/logs/<job_name>_<suffix>
```

## srun-native 方法（推荐）

Slurm 直接启动所有进程。没有 `torch.distributed.run`，没有 TRAIN_CMD 转义。

### SBATCH 头部

```bash
#SBATCH --job-name=<model>-<task>
#SBATCH --nodes=<NNODES>
#SBATCH --ntasks-per-node=8          # Slurm 在每个节点上启动 8 个任务
#SBATCH --gpus-per-node=8
#SBATCH --time=00:30:00
#SBATCH --account=<YOUR_ACCOUNT>
#SBATCH --partition=batch
#SBATCH --output=<SHARED_FS>/logs/<job_name>_%j.log
#SBATCH --exclusive
```

### 构建 和 启动

使用两阶段 `srun` 模式：首先运行单个进程的 `uv sync` 以填充共享缓存，然后启动完整的多节点作业。完整的复制粘贴版本位于 `references/templates.md` 中。

### srun-native 关键点

- 阶段 1 在单个节点/进程上运行一次 `uv sync`，将所有轮子构建到 Lustre 上的共享缓存中
- 阶段 2 的 `uv sync` 是一个快速无操作（所有内容都已缓存）——可以在所有排名上安全运行，无需睡眠保护
- `initialize.py` + `common_utils.py` 自动从 SLURM 环境变量设置 `RANK`、`WORLD_SIZE`、`LOCAL_RANK`、`MASTER_ADDR`、`MASTER_PORT`
- 在 sbatch 级别导出的环境变量（如 `HF_TOKEN`、`HF_HOME`、`UV_CACHE_DIR`）会被 srun 任务继承
- 参考：`examples/models/glm/glm_45v/slurm_sft.sh`、`examples/models/minimax/minimax_m2/slurm_conversion.sh`

---

## uv run torch.distributed 方法（遗留）

当脚本需要 `torch.distributed.run`（例如，MLM pretrain_gpt.py）或当 Bridge 的 `initialize.py` 不在调用路径中时使用。

### 1. 添加 SBATCH 头部

```bash
#SBATCH --job-name=<model>-<framework>
#SBATCH --nodes=<NNODES>
#SBATCH --ntasks-per-node=1          # 始终为 1 — torchrun 处理每个节点的启动
#SBATCH --gpus-per-node=8
#SBATCH --time=00:30:00
#SBATCH --account=<YOUR_ACCOUNT>
#SBATCH --partition=batch
#SBATCH --output=<SHARED_FS>/logs/<job_name>_%j.log
#SBATCH --exclusive
```

**关键**：`--ntasks-per-node=1`，不是 8。`uv run python -m torch.distributed.run --nproc_per_node=8` 在每个节点上启动 8 个进程。使用 `ntasks-per-node=8` 会导致端口冲突（每个节点 8 个任务 x 8 进程 = 每个节点 64 个）。

### 2. 转换为多节点

替换单节点：

```bash
uv run python -m torch.distributed.run --nproc_per_node=8 \
  <script> <args>
```

为多节点（在 `TRAIN_CMD` 字符串内）：

```bash
uv run python -m torch.distributed.run \
  --nproc_per_node=8 \
  --nnodes=\${SLURM_JOB_NUM_NODES} \
  --node_rank=\${SLURM_NODEID} \
  <script> <args>
```

`MASTER_ADDR` 和 `MASTER_PORT` 由 `initialize.py` / `common_utils.py` 自动从 SLURM 环境变量派生 — 无需设置它们。

### 3. 包装在 TRAIN_CMD + 两阶段 srun

使用相同的两阶段模式：首先运行单个进程的 srun 以预热 uv 缓存，然后运行完整作业。

在容器内设置运行时变量，但不要将令牌值注入到长 `bash -c` 字符串中。通过调度程序或在工作开始前源一个受限的密钥文件来导出凭证。保持 `HF_HOME`、`UV_CACHE_DIR` 和 `NEMO_HOME` 在共享存储上。

### 4. 启动（两阶段）

使用 `references/templates.md` 中的两阶段启动模板，并保持 `#SBATCH --ntasks-per-node=1` 用于此遗留方法。

### 5. （可选）添加损失提取尾部

```bash
echo "======================================"
echo "Done. Losses:"
echo "======================================"
grep -E "iteration\s+" "$LOGDIR/<prefix>_${SLURM_JOB_ID}.log" | grep -iE "lm loss|reduced_train_loss" | head -25
```

---

## 交互式 GPU 分配（`salloc` + `srun`）

对于临时测试（推理、转换调试），始终遵循以下 3 个步骤：

### 第 1 步：分配节点

```bash
salloc --account <YOUR_ACCOUNT> -N 1 \
  -J <YOUR_ACCOUNT>-debug \
  -p interactive --gpus-per-node=8 -t 240
```

### 第 2 步：启动容器 shell

```bash
srun --mpi=pmix --no-kill \
  --container-image $CONTAINER_IMAGE \
  --container-mounts $CONTAINER_MOUNTS \
  --account <YOUR_ACCOUNT> -N 1 \
  -J <YOUR_ACCOUNT>-debug \
  --no-container-mount-home --gpus-per-node=8 \
  -p interactive --pty bash
```

### 第 3 步：在容器内设置环境

```bash
export GH_TOKEN=<YOUR_GITHUB_TOKEN>
wandb login <YOUR_WANDB_KEY>
export HF_TOKEN=<YOUR_HF_TOKEN>
export HF_HOME=<SHARED_FS>/HF_HOME
export UV_CACHE_DIR="<SHARED_FS>/uv_cache"
export NEMO_HOME="<SHARED_FS>/cache/nemo"
uv sync
```

然后使用 `uv run` 运行命令（使用同步的虚拟环境）：

```bash
uv run python -m torch.distributed.run --nproc_per_node=8 \
  examples/conversion/hf_to_megatron_generate_text.py \
  --hf_model_path <org>/<model> --prompt "What is AI?" --max_new_tokens 50 --ep 8
```

**交互式分配的陷阱**：

| 错误 | 原因 | 修复 |
|---|---|---|
| `Cannot find GPU specification` | 缺少 `--gpus-per-node` | 在 `salloc` 和 `srun` 中始终包含 `--gpus-per-node=8` |
| `invalid partition specified: pool0` | 分区名称错误 | 使用 `interactive` 用于交互式，`batch` 用于 sbatch。检查：`sinfo --summarize` |
| `Invalid account or account/partition combination` | 账户没有可用的分区 | 检查组合：`sacctmgr -nP show assoc where user=$USER format=account,partition` |
| `Unable to create step for job... Requested node configuration is not available` | `-w <node>` 与分配冲突 | 移除 `-w` 标志 — HF 缓存位于共享文件系统上，可以从任何节点访问 |
| `uv: command not found` 在容器内 | 容器没有预安装 `uv` | 使用预安装 `uv` 的容器，或 `pip install uv` |
| `No space left on device` 在 `uv` 或 `pip` 时 | 容器的 `/root/.cache/` 已满 | 重定向：`export UV_CACHE_DIR=<SHARED_FS>/uv_cache` |
| `ModuleNotFoundError: No module named 'megatron.core.activations'` | 容器预安装的 megatron-core 与本地 `3rdparty/Megatron-LM` 冲突 | 本地安装：`pip install -e 3rdparty/Megatron-LM --no-deps --no-build-isolation` |

---

## 调试多节点故障

### 快速诊断

按顺序检查日志中的这些模式：

```bash
# 1. 查找实际错误（过滤噪声）
grep -a 'Error\|OOM\|CUDA out of memory\|FAILED\|Killed' job.log \
  | grep -v 'UserWarning\|AllocatorConfig\|transformer_engine\|frame\|srun: error'

# 2. 检查哪个排名首先崩溃
grep -a 'Failures:' -A 20 job.log | head -25

# 3. 检查 NCCL 超时
grep -a 'ncclUniqueId\|timeout\|crash on rank 0' job.log | head -5
```

### 调试清单

当多节点作业失败时：

1. **检查退出代码**：1 = Python 错误，9 = OOM 被杀死，143 = SIGTERM（超时或级联）
2. **找到第一个失败**：哪个任务/节点首先崩溃？其他任务作为级联收到 SIGTERM (143)
3. **grep 实际错误**：过滤掉 UserWarnings、NCCL 帧转储
4. **专门检查排名 0**：大多数保存/导出错误发生在排名 0
5. **验证 EP 大小**：对于 MoE 模型，确保 `num_experts / EP` 在 GPU 内存中留有空间
6. **首先尝试交互式**：使用 `salloc -N 2 -p interactive` 比 sbatch 队列更快地迭代

### NCCL 在 `dist.barrier()` 处超时 — "crash on rank 0"

**症状**：节点 2+ 上的所有排名显示：
```text
[rank8] 正在设置 NCCL 通信器并从 [0] 获取 ncclUniqueId
... 等待 600000ms 后超时
这可能表示在排名 0 上发生了一个应用程序崩溃
```

**根本原因**（按顺序检查）：

| 原因 | 如何验证 | 修复 |
|---|---|---|
| `save_artifacts` 在排名 0 挂起 | 错误在 `save_hf_weights` → `dist.barrier()` | 增加超时：`init_process_group("nccl", timeout=timedelta(minutes=60))` |
| 自定义模型代码中的 `ImportError` | `grep ImportError job.log` | 在 `save_artifacts` 中捕获 `ImportError`（见下文） |
| 排名 0 导出时 OOM | `grep 'OutOfMemory' job.log` | 增加 EP 或节点 |
| 节点间网络问题 | 仅在跨节点排名上出现错误 | 检查 `sinfo`，尝试不同节点 |

**`save_artifacts` 问题**：当 `trust_remote_code=True` 时，排名 0 运行 `save_artifacts()`（下载分词器、配置、自定义建模代码）而其他所有排名直接跳转到 `dist.barrier()`。如果 `save_artifacts` 运行缓慢或崩溃，其他排名会超时。

**修复 `save_artifacts` 中的 ImportError**（`hf_pretrained/base.py`）：
```python
# 改为：
except OSError:
    pass
# 为：
except (OSError, ImportError):
    pass
```

### MoE 模型 OOM

**症状**：`torch.OutOfMemoryError: CUDA out of memory` 在模型加载或前向传递期间。

**关键洞察**：TP 不减少专家内存。只有 EP 将专家分布在 GPU 上。

**尺寸公式**：
```text
experts_per_gpu = num_experts / EP
expert_memory_gb ≈ experts_per_gpu * expert_params * 2 / 1e9  (bf16)
total_per_gpu ≈ expert_memory_gb + attention_memory_gb + kv_cache_gb
```

**MiniMax-M2 示例**（256 个专家，~230GB fp8 → ~460GB bf16）：

| 配置 | 节点 | GPU | 专家/GPU | 结果 |
|---|---|---|---|---|
| TP=2, EP=4 | 1 | 8 | 64 | OOM（专家太多） |
| TP=2, EP=8 | 2 | 16 | 32 | roundtrip（仅权重）工作，OOM 对于推理 |
| TP=1, EP=16 | 2 | 16 | 16 | 推理工作 |
| TP=2, EP=32 | 8 | 64 | 8 | 训练舒适 |

**经验法则**：
- Roundtrip（仅权重）：可以每个 GPU 使用更多专家（~60GB 模型参数 OK）
- 推理（前向传递 + KV 缓存）：需要更多空间（最大 ~40GB 模型参数）
- 训练（激活 + 优化器）：需要更多空间（最大 ~30GB 模型参数）

### `ModuleNotFoundError: No module named 'megatron.core.tensor_parallel'`

**原因**：容器预安装的 megatron-core 与本地 `3rdparty/Megatron-LM` 冲突。

**修复**：在运行前添加 `uv sync`：
```bash
CMD="if [ \"\$SLURM_LOCALID\" -eq 0 ]; then uv sync; else sleep 10; fi && "
CMD="${CMD}uv run --no-sync python <script> <args>"
```

### Roundtrip 中的 FP8 权重不匹配

**症状**：Roundtrip 完成，但所有专家权重显示 ❌，并引发 `ValueError: Weight mismatch detected`。

**原因**：原始 HF 权重是 FP8，Megatron 存储为 BF16。导出的权重是 BF16。比较原始 FP8 超出 `atol=1e-1`。

**FP8 模型这是预期的**。转换是正确的；比较容差不足以弥补 FP8→BF16 的精度差距。

### `WORLD_SIZE` 未使用 srun 设置

**症状**：脚本退出，提示 "必须使用 torchrun 启动"。

**原因**：脚本检查 `os.environ.get("WORLD_SIZE")`，torchrun 设置但 srun 不设置。

**修复**：也检查 `SLURM_NTASKS`：
```python
if os.environ.get("WORLD_SIZE") is None and os.environ.get("SLURM_NTASKS") is None:
    sys.exit(1)
```

Bridge 的 `common_utils.py` 辅助函数（由 `initialize.py` 调用）从 SLURM 填充环境变量：
```python
if "RANK" not in os.environ:
    os.environ["RANK"] = str(get_rank_safe())          # 使用 SLURM_PROCID
if "WORLD_SIZE" not in os.environ:
    os.environ["WORLD_SIZE"] = str(get_world_size_safe())  # 使用 SLURM_NTASKS
if "MASTER_ADDR" not in os.environ:
    os.environ["MASTER_ADDR"] = get_master_addr_safe()     # 解析 SLURM_NODELIST
if "MASTER_PORT" not in os.environ:
    os.environ["MASTER_PORT"] = str(get_master_port_safe()) # 从 SLURM_JOB_ID 导出
```

---

## 关键陷阱

1. **两阶段 srun 用于 `uv sync`**：首先运行单个进程的 srun 以预热缓存，然后运行完整的多节点 srun。第二个 `uv sync` 是一个快速无操作，因为所有内容都已缓存在共享文件系统上。

2. **`--no-container-mount-home` 是一个 `srun` 标志，不是 `#SBATCH` 指令**。

3. **TRAIN_CMD 内部的转义**：由于 `TRAIN_CMD` 是一个双引号字符串，转义内部 `$` 以便 Slurm 变量在运行时展开（而不是 sbatch 时间）：
   - `\${SLURM_PROCID}`、`\${SLURM_JOB_NUM_NODES}`、`\${SLURM_NODEID}`
   - 主机端变量（如 `$GH_TOKEN`、`$LOGDIR`、`$WORKDIR`）在 sbatch 时间展开 — 无需转义。

4. **Bridge `rm -rf nemo_experiments`**：在训练前添加，以避免陈旧的检查点自动恢复。

5. **MLM 需要 PYTHONPATH**：对于 pretrain_gpt.py 脚本，在 TRAIN_CMD 中添加：
   ```bash
   PYTHONPATH=${WORKDIR}/3rdparty/Megatron-LM:\${PYTHONPATH:-} \
   ```

6. **节点数量启发式**：总 GPU = `NNODES * 8`。必须满足：`TP * PP * EP * DP >= total_GPUs` 其中 `DP = total_GPUs / (TP * PP * EP)`。

7. **多节点 SFT 中的 `NEMO_HOME` 在共享文件系统上**：默认 nemo 缓存（`/root/.cache/nemo`）是容器本地的。多节点 SFT 使用打包序列时，一个节点上准备的 `.npy` 文件对其他节点不可见。设置 `export NEMO_HOME=<SHARED_FS>/cache/nemo` 以共享打包数据。不这样设置，其他节点上的排名会因 `TypeError: 'NoneType' object is not an iterator` 而失败。

## 完整模板和命令体

对于可复制的 sbatch 框架和 Bridge/MLM 特定的 `TRAIN_CMD` 正文，请阅读
[references/templates.md](references/templates.md)。
