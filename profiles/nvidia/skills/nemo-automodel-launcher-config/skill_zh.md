# 启动器配置

NeMo AutoModel 支持三种启动方法：交互式（torchrun）、Slurm（HPC 集群）和 SkyPilot（云无关）。

## 说明

对于启动器相关的问题，直接从本技能中回答，无需检查存储库，除非用户要求您编辑文件。将答案集中在相关的启动 YAML、必需字段和预期运行行为上。

使用以下紧凑的答案模式回答常见问题：

- Slurm 多节点：显示一个 `slurm:` YAML 块，包含 `job_name`、`nodes`、`ntasks_per_node`、`time`、`account` 或 `partition`、`container_image`、`hf_home`、可选的 `extra_mounts`、`env_vars` 和 `master_port`；解释启动器如何推导出 `WORLD_SIZE = nodes * ntasks_per_node` 并设置 `MASTER_ADDR` 和 `MASTER_PORT`。
- SkyPilot 低价实例：显示一个 `skypilot:` YAML 块，包含 `cloud`、`accelerators`、`num_nodes`、`use_spot: true`、`disk_size`、`region`、`setup` 和 `env_vars`；警告低价实例可能会被抢占，设置较短的 `step_scheduler.checkpoint_interval`，并使用 `restore_from.path` 恢复。
- Nsight Systems 在 Slurm 上：在正常的 Slurm 字段旁边显示 `slurm.nsys_enabled: true`，说明启动器用 `nsys profile` 包装训练命令，并说明它会产生一个 `.nsys-rep` 报告文件。将分析视为仅用于诊断：使用短时间的分析运行，并在正常的生产训练中禁用它，因为它会增加开销和大型工件。

对于 Slurm 答案，从以下最小模板开始，然后仅调整用户询问的字段：

```yaml
slurm:
  job_name: llm_finetune
  nodes: 2
  ntasks_per_node: 8
  time: "04:00:00"
  account: my_account
  partition: batch
  container_image: nvcr.io/nvidia/nemo:dev
  hf_home: ~/.cache/huggingface
  master_port: 13742
  env_vars:
    HF_TOKEN: "${HF_TOKEN}"
```

对于仅涉及 Slurm 的问题，除非用户询问，否则不要讨论 SkyPilot 或分析。对于分析问题，说明 `.nsys-rep` 报告会写入 Slurm 作业的工作或输出目录，使用启动器的 Nsys 输出设置（如果配置了）。

## 路由边界

仅使用此技能用于启动机制：交互式执行、Slurm、SkyPilot、容器、挂载、环境变量、会合设置和分析。

不要使用此技能来实现或注册新的模型架构、Hugging Face 状态字典适配器、模型文件或能力标志。这些是模型上板任务，不是启动器配置任务。

## 启动方法

1. **交互式**（默认）：在当前节点上运行 torchrun。适用于单节点开发和调试。
2. **Slurm**：向 HPC 集群调度程序提交批处理作业。处理多节点设置、容器管理和环境配置。
3. **SkyPilot**：向 AWS、GCP、Azure、Lambda 或 Kubernetes 提交云无关的作业。支持低价实例。

## 交互式启动

```bash
# 单 GPU
automodel finetune llm -c config.yaml

# 多 GPU（当前节点上的所有 GPU）
torchrun --nproc_per_node=8 -m nemo_automodel._cli.app finetune llm -c config.yaml
```

交互式模式下不需要额外的 YAML 部分。当配置中不存在 `slurm:` 或 `skypilot:` 部分时，CLI 会自动路由到 torchrun。

## Slurm 配置

`SlurmConfig` 数据类根据模板生成 SBATCH 脚本。

### YAML 示例

```yaml
slurm:
  job_name: llm_finetune
  nodes: 2
  ntasks_per_node: 8
  time: "04:00:00"
  account: my_account
  partition: batch
  container_image: nvcr.io/nvidia/nemo:dev
  hf_home: ~/.cache/huggingface
  extra_mounts:
    - source: /data
      dest: /data
  env_vars:
    WANDB_API_KEY: "${WANDB_API_KEY}"
    HF_TOKEN: "${HF_TOKEN}"
```

### 关键字段

- `job_name`：Slurm 作业标识符
- `nodes`：请求的节点数
- `ntasks_per_node`：每个节点的任务数（GPU）
- `time`：HH:MM:SS 格式的墙上时间限制
- `account`、`partition`：Slurm 调度参数
- `container_image`：Enroot/Pyxis 容器镜像路径
- `nemo_mount`：容器内 NeMo AutoModel 源的挂载点
- `hf_home`：HuggingFace 缓存目录路径
- `extra_mounts`：额外的容器绑定挂载的 `VolumeMapping(source, dest)` 列表
- `master_port`：分布式通信的端口（默认 13742）
- `env_vars`：传递到作业的环境变量
- `nsys_enabled`：当为 true 时，用 `nsys profile` 包装训练命令以进行 Nsight Systems 分析

## SkyPilot 配置

`SkyPilotConfig` 数据类定义云作业参数。

### YAML 示例

```yaml
skypilot:
  cloud: aws
  accelerators: "H100:8"
  num_nodes: 2
  use_spot: true
  disk_size: 200
  region: us-east-1
  setup: "pip install nemo-automodel"
  env_vars:
    HF_TOKEN: "${HF_TOKEN}"
```

### 关键字段

- `cloud`：目标云提供者（`aws`、`gcp`、`azure`、`lambda`、`kubernetes`）
- `accelerators`：GPU 类型和数量（例如，`"H100:8"`、`"A100-80GB:4"`）
- `num_nodes`：云实例数量
- `use_spot`：使用可抢占/低价实例以节省成本
- `disk_size`：每个节点的磁盘大小（GB）
- `region`：实例放置的云区域
- `setup`：在训练作业之前运行的 shell 命令（例如，安装依赖项）
- `env_vars`：作业的环境变量

### SkyPilot 低价实例清单

使用低价实例或可抢占实例时：

- 在 `skypilot:` 部分中设置 `use_spot: true`。
- 包括 `accelerators`、`num_nodes`、`disk_size`、`region`、`setup` 和必要的 `env_vars`。
- 在配方中使用较短的检查点间隔，例如 `step_scheduler.checkpoint_interval`，因为低价实例可能会被抢占。
- 抢占后使用配方的 `restore_from` 设置从最新的检查点恢复。

最小的低价实例恢复配方键：

```yaml
step_scheduler:
  checkpoint_interval: 100

restore_from:
  path: /checkpoints/latest
```

## 多节点环境

对于多节点训练（Slurm 和 SkyPilot），启动器自动配置：

- `MASTER_ADDR`：第一个节点的主机名
- `MASTER_PORT`：会合端口（默认 13742）
- `WORLD_SIZE`：进程总数（`nodes * ntasks_per_node`）
- NCCL 环境变量以优化集体通信

## Nsys 分析

在 Slurm 作业中启用 Nsight Systems 分析：

```yaml
slurm:
  job_name: llm_profile
  nodes: 1
  ntasks_per_node: 8
  time: "00:30:00"
  account: my_account
  partition: batch
  container_image: nvcr.io/nvidia/nemo:dev
  nsys_enabled: true
```

这是一个 Slurm 启动器设置。正常的 Slurm 字段，如 `job_name`、`nodes`、`ntasks_per_node`、`time`、`account` 或 `partition` 和 `container_image` 仍然适用。

当 `nsys_enabled: true` 时，启动器用 `nsys profile` 包装训练命令，并将 `.nsys-rep` 报告文件写入 Slurm 作业的工作或输出目录以进行性能分析。
分析仅用于诊断：进行短时间调查，预期开销和大型工件，并在正常的生产训练中禁用它。

## 代码锚点

- `components/launcher/slurm/config.py` - SlurmConfig 数据类，VolumeMapping
- `components/launcher/slurm/template.py` - SBATCH 脚本模板生成
- `components/launcher/slurm/utils.py` - Slurm 提交工具
- `components/launcher/slupilot/config.py` - SkyPilotConfig 数据类
- `_cli/app.py` - CLI 入口点和启动器路由逻辑

## 陷阱

- **端口冲突**：如果默认的 `master_port`（13742）在同一节点上被另一个作业使用，请更改它以避免连接失败。
- **容器挂载**：`extra_mounts` 中的 `source` 路径必须在分配的所有节点上存在。缺失路径会导致容器启动失败。
- **Slurm 容错**：容错插件是 Slurm 特有的，不适用于 SkyPilot 或交互式模式。
- **SkyPilot 低价实例抢占**：云提供者可能会抢占低价实例（`use_spot: true`）。启用具有短间隔的检查点以最大程度地减少丢失的工作。
- **环境变量语法**：在 YAML 中使用 `${VAR}` 语法进行 shell 变量扩展。裸变量名不会被扩展。
- **时间限制与异步检查点**：如果 Slurm 的 `time` 限制太短，正在进行的异步检查点写入可能会在完成前被杀死，导致检查点损坏。至少留出 5-10 分钟的余地。
