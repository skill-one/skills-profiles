# 在 SLURM 上运行 Megatron-LM

## 先回答常量

对于纯文本 SLURM 设置问题，在完整脚本之前先回答这些常量：

- 从对所有节点可见的共享工作树路径提交；在脚本中启动训练前 `cd` 到该路径。
- 每个节点使用一个 `srun` 任务，并使用 `uv run python -m torch.distributed.run` 启动工作进程，而不是裸 `torchrun`。
- 从 `scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n1` 设置 `MASTER_ADDR`，设置 `MASTER_PORT`、`NNODES=${SLURM_NNODES}`、`GPUS_PER_NODE=<GPUS_PER_NODE>`，以及 `WORLD_SIZE=$((NNODES * GPUS_PER_NODE))`。
- 将 `--nnodes`、`--nproc-per-node`、`--node-rank`、`--master-addr` 和 `--master-port` 传递给 `torch.distributed.run`。
- `CUDA_DEVICE_MAX_CONNECTIONS`：预 Blackwell Hopper/Ampere 且 TP>1 或 CP>1 的非 FSDP 使用 `1`；Blackwell/GB200 不需要它；Torch-FSDP2 或 Megatron-FSDP 必须不使用 `1`；`overlap_moe_expert_parallel_comm` 使用 `32`。

## 前置条件

- 具有向 GPU 分区提交权限的 SLURM 集群登录。
- 在分配的所有节点都可见的文件系统中检出 Megatron-LM（NFS、Lustre 或类似系统）。所有节点必须能够访问代码、数据、检查点和输出的相同路径。
- 安装了 `uv`；在提交前，在工作树上运行一次 `uv sync --extra training --extra dev`（或 `--extra lts`），以便 `.venv` 被实例化并对所有节点可见。

## 最小 sbatch 脚本

在工作树中保存为 `run_megatron.slurm`：

```bash
#!/bin/bash
#SBATCH --job-name=megatron
#SBATCH --account=<SLURM_ACCOUNT>
#SBATCH --partition=<SLURM_PARTITION>
#SBATCH --nodes=<NODES>
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=<GPUS_PER_NODE>
#SBATCH --time=<HH:MM:SS>
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

set -euo pipefail
cd <MEGATRON_WORKTREE>

export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n1)
export MASTER_PORT=${MASTER_PORT:-29500}
export NNODES=${SLURM_NNODES}
export GPUS_PER_NODE=<GPUS_PER_NODE>
export WORLD_SIZE=$((NNODES * GPUS_PER_NODE))

# 仅当您的配置需要时才显式设置 CUDA_DEVICE_MAX_CONNECTIONS
# （见下文部分）。预 Blackwell 且 TP>1 或 CP>1 的示例（非 FSDP）：
#   export CUDA_DEVICE_MAX_CONNECTIONS=1

srun --ntasks=${NNODES} --ntasks-per-node=1 bash -c '
  # NODE_RANK 来自 SLURM_NODEID，每个节点一个任务。
  NODE_RANK=${SLURM_NODEID}
  uv run python -m torch.distributed.run \
    --nnodes='"${NNODES}"' \
    --nproc-per-node='"${GPUS_PER_NODE}"' \
    --node-rank=${NODE_RANK} \
    --master-addr='"${MASTER_ADDR}"' \
    --master-port='"${MASTER_PORT}"' \
    pretrain_gpt.py \
      <MEGATRON_ARGS>
'
```

提交：

```bash
mkdir -p logs && JOB_ID=$(sbatch --parsable run_megatron.slurm)
echo "已提交 ${JOB_ID}"
```

## 多节点规则

- 从您打算运行的工作树提交，或在脚本中 `cd` 到它。所有节点必须能够访问共享文件系统（NFS、Lustre 或类似系统）上的相同路径——节点本地路径对其他排名不可见。
- 在所有节点上使用一个 `torchrun` 工作进程组；不要启动独立的单节点作业。
- `--nproc-per-node` 应等于每个节点可见的 GPU 数量。
- 将检查点、tensorboard 数据和结构化日志写入共享存储。

## CUDA_DEVICE_MAX_CONNECTIONS

正确的值取决于您的硬件和并行模式。不要无条件地导出它：

- **预 Blackwell (Hopper, Ampere) 且 TP>1 或 CP>1，非 FSDP**：设置为 `1`。相关代码路径会对此断言——如果它不是 `1`，您会得到一个断言错误，而不是静默死锁。
- **Blackwell**：不需要；设置它没有效果。
- **Torch-FSDP2 或 Megatron-FSDP**：必须不等于 `1`。保留环境变量未设置，或设置为大于 `1` 的值。
- **`overlap_moe_expert_parallel_comm` 启用**：设置为 `32`。

当您的配置需要时，在 sbatch 脚本中显式设置它。

## 容器

许多站点在容器内运行 Megatron-LM（某些集群上的 enroot/pyxis，其他集群上的 singularity）。如果您这样做，由 `uv` 管理的 `.venv` 必须位于容器内可见的路径上，并且容器镜像必须提供仓库期望的 CUDA / NCCL / torch 版本（见 `docker/.ngc_version.dev` 和 `.ngc_version.lts`）。上述骨架保持不变；用调度器的容器标志（`--container-image=…`、`--container-mounts=…` 等）包装 `srun` 调用。

## 监控和收集

```bash
squeue -j "$JOB_ID" -o "%.10i %.8T %.10M %.6D %R"
sacct -j "$JOB_ID" --format=JobID,State,ExitCode,Elapsed
scancel "$JOB_ID"
```

如果您的训练脚本写入结果工件（来自排名 0 的 JSON 指标文件、最终检查点等），轮询工件而不是仅等待 `squeue` 状态。有用的输出通常在 SLURM 标记作业完成之前出现，轮询工件允许您在工件到达时立即取消作业，而不是保留分配直到超时。

## 故障诊断

扫描每个排名的 stderr，而不仅仅是排名 0 的。最早的非 NCCL Python 追溯通常是根本原因；其他排名上的后续 NCCL 超时是第一个崩溃的下游症状。

快速分类：

- **OOM**：记录排名、阶段（前向 / 反向 / 优化器）、批处理大小、序列长度、并行性（TP/DP/CP/PP）以及调整前的峰值内存。
- **形状 / 可除性错误**：检查 `WORLD_SIZE = TP × DP × CP × PP` 和头计数可除性（`num_attention_heads % TP == 0`）。
- **导入错误**：错误的工作树、缺少 `uv sync` 或陈旧的 `PYTHONPATH`。在启动前确认 `cd <MEGATRON_WORKTREE>`。
- **NCCL 失败** 且没有 Python 追溯：验证分配、端口可达性、`MASTER_ADDR` 解析以及跨排名的命令一致性。

## 常见陷阱

- 提交前忘记 `uv sync`。如果 venv 缺失，每个作业都会在 `srun` 内部重建它，每个作业耗时数分钟。
- 将日志写入作业退出时消失的节点本地路径。始终写入共享文件系统。
- 盲目设置 `CUDA_DEVICE_MAX_CONNECTIONS=1`。正确的值取决于硬件和并行模式（见上述专用部分）。设置为 `1` 与 FSDP 会导致不同问题；在 Blackwell 上它没有效果；在预 Blackwell 且 TP>1 或 CP>1（非 FSDP）上代码断言，不会死锁。
- 使用裸 `torchrun` 而不是 `uv run python -m torch.distributed.run`。裸 `torchrun` 可能通过一个看不到 venv 包的 python 解释器分发，具体取决于 venv 的设置方式。
