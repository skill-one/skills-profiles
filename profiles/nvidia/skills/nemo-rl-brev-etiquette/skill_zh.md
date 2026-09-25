# Brev 礼仪

以 `/home/ubuntu/RL` 为源代码检出目录，以 `/ephemeral` 为生成实验状态的临时存储。保持代码库精简、可复现且易于检查。在启动任何高成本操作前，将庞大的运行输出移至 `/ephemeral`。

## 存储规则

- 将代码编辑、小型配置更改、已提交的实验假设和简洁的可复现性记录保存在 `/home/ubuntu/RL` 下。
- 将生成的实验资源保存在 `/ephemeral` 下，包括检查点、运行日志、Ray 临时目录、W&B 离线文件、分析器跟踪、评估转储、部署样本和每个实验的工件。
- 将可复用的缓存保存在每个用户共享的 `/ephemeral` 缓存根目录下，而不是每个实验下。这包括 Hugging Face 模型、数据集缓存、PyTorch 缓存、Triton 缓存、`uv` 缓存和 pip 缓存。
- 在启动任何活动或长时间运行任务前，使用 `df -h /home/ubuntu/RL /ephemeral` 检查空间容量，如果 `/ephemeral` 缺失或几乎已满，则避免启动。
- 创建活动根目录，例如 `/ephemeral/nemo-rl/${USER:-ubuntu}/nemo-rl-auto-research/<活动>`，并为每个实验使用一个子目录。
- 不要在 git 检出中留下大文件、缓存目录或生成输出。如果某个工具默认使用代码库，则在运行前覆盖其输出/缓存路径。

## 环境密钥

- 将 `/home/ubuntu/RL/.env` 视为本地密钥存储。它可能包含 `WANDB_API_KEY`、`HF_TOKEN` 或 `HUGGING_FACE_HUB_TOKEN` 等密钥。
- 在任何可能需要外部认证的运行前，如果存在 `/home/ubuntu/RL/.env`，则加载它。永远不要打印、`cat`、记录、提交或总结密钥值。
- 如果 `/home/ubuntu/RL/.env` 不存在，或在加载后仍缺少必要密钥，则提醒用户在启动认证任务前向该文件添加所需密钥。

```bash
if [ -f /home/ubuntu/RL/.env ]; then
  set -a
  . /home/ubuntu/RL/.env
  set +a
else
  echo "Missing /home/ubuntu/RL/.env; add required keys such as WANDB_API_KEY or HF_TOKEN before authenticated runs."
fi
```

## 自动研究模式

使用 `nemo-rl-auto-research` 时，将 git 记账保存在代码库中，并将大量证据保存在 `/ephemeral`。

```bash
if [ -f /home/ubuntu/RL/.env ]; then
  set -a
  . /home/ubuntu/RL/.env
  set +a
fi

BREV_ROOT=/ephemeral/nemo-rl/${USER:-ubuntu}
CACHE_ROOT=$BREV_ROOT/cache
CAMPAIGN_ROOT=$BREV_ROOT/nemo-rl-auto-research/<活动>
EXP_DIR=$CAMPAIGN_ROOT/<实验>
mkdir -p "$EXP_DIR"/{logs,checkpoints,artifacts,ray,tmp,wandb}
mkdir -p "$CACHE_ROOT"/{huggingface,torch,triton,uv,pip,xdg,wandb}

export HF_HOME=$CACHE_ROOT/huggingface
export HF_HUB_CACHE=$HF_HOME/hub
export HF_DATASETS_CACHE=$HF_HOME/datasets
export TRANSFORMERS_CACHE=$HF_HOME/transformers
export TORCH_HOME=$CACHE_ROOT/torch
export TRITON_CACHE_DIR=$CACHE_ROOT/triton
export UV_CACHE_DIR=$CACHE_ROOT/uv
export PIP_CACHE_DIR=$CACHE_ROOT/pip
export XDG_CACHE_HOME=$CACHE_ROOT/xdg
export WANDB_CACHE_DIR=$CACHE_ROOT/wandb
export RAY_TMPDIR=$EXP_DIR/ray
export TMPDIR=$EXP_DIR/tmp
export WANDB_DIR=$EXP_DIR/wandb
```

将 `/ephemeral` 的绝对路径记录在 nemo-rl-auto-research TSV 字段中，用于日志路径、检查点路径、工件、共享缓存根目录和命令。如果 TSV 本身可能变得很大，则将完整 TSV 存储在 `/ephemeral` 中，并在代码库中保留一个小的指针文件或摘要。

## 启动检查清单

- 首先检查磁盘空间：`df -h /home/ubuntu/RL /ephemeral`。
- 在编辑配方或启动任务前，选择一个唯一的 `/ephemeral` 运行根目录。
- 在实验之间复用共享缓存根目录，例如 `/ephemeral/nemo-rl/${USER:-ubuntu}/cache`，除非运行任务明确要求干净缓存。
- 覆盖配方输出路径、日志器路径、检查点路径和临时路径，使其指向实验目录。
- 覆盖缓存路径，使其指向共享缓存根目录。
- 将 stdout/stderr 流到 `$EXP_DIR/logs/run.log` 或 `/ephemeral` 下的等效文件。
- 在长时间运行任务期间，使用 `df -h /ephemeral` 定期检查磁盘空间，如果卷空间接近耗尽，则优雅停止。
- 最后，在代码库中总结重要指标和路径；不要将庞大的工件复制回 `/home/ubuntu/RL`。

## 清理

- 仅清理属于当前活动或实验的文件。
- 优先修剪 `/ephemeral/nemo-rl/...` 下命名的实验目录；永远不要在没有明确指令的情况下删除共享缓存或另一个用户的运行目录。
- 在清理 `/ephemeral` 后，在代码库中保留足够的小型元数据，以便重新生成结果。
