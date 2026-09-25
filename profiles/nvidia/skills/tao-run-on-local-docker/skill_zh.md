# 本地 Docker

> **是否需要独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

单节点执行平台，在 Docker 守护进程上以命名的 Docker 容器形式运行 TAO 任务。守护进程可以是代理主机本地或通过 `DOCKER_HOST=ssh://user@host` / Docker 上下文远程。它适用于开发、调试、小规模运行以及本地编码代理提交任务到远程 GPU 盒的工作流。

当数据位于 Docker 主机本地或可通过挂载卷/云凭证访问时，使用本地 Docker。不要将其用于远程集群调度、多节点训练或需要 SLURM 队列的任务。

当代理运行在工作站或笔记本电脑上，但 Docker 守护进程和 GPU 位于另一个单 GPU 服务器上时，使用远程 Docker。在远程 Docker 模式下，规范中的所有本地文件系统路径都在远程 Docker 主机上解释，而不是在代理机器上。

## 预检

工作流必须在启动 Docker 任务之前验证主机 GPU 运行时。如果检查失败，提示用户批准安装，运行打印的安装命令，并重新运行预检。

```bash
# 主机 GPU 运行时：NVIDIA 驱动程序 580，CUDA 13.0，NVIDIA 容器工具包 1.19.0。
SB="${TAO_SKILL_BANK_PATH:-${TAO_SKILL_BANK_ROOT:-$PWD}}"
SETUP_SCRIPT="${SB}/skills/platform/tao-setup-nvidia-gpu-host/scripts/setup-nvidia-gpu-host.sh"

bash "$SETUP_SCRIPT" --backend docker --check-only || {
  echo "缺失：TAO GPU 主机运行时未准备就绪。"
  echo "在用户批准后，运行："
  echo "  bash \"$SETUP_SCRIPT\" --backend docker --install --yes"
  exit 1
}

# 模式 1 — 直接 docker（无 Python）。您只需要 docker + GPU 运行时。
docker info >/dev/null 2>&1 || { echo "缺失：无法访问 docker 守护进程。启动 Docker。"; exit 1; }
docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi >/dev/null 2>&1 || {
  echo "缺失：未安装/配置 NVIDIA 容器工具包。查看："
  echo "  bash \"$SETUP_SCRIPT\" --backend docker --install --yes"
  exit 1
}

# 模式 2 — TAO SDK 包装器。添加任务句柄、S3 I/O 包装、ActionWorkflow。
# 如果模式 1 对用户请求足够，则跳过此块。
# 当模式 2 在范围内时，请阅读 `tao-skill-bank:tao-run-platform` 以获取 DockerSDK
# 参数合同、build_entrypoint 和监控模式。
# nvidia-tao-sdk 在公共 PyPI 上；下面的 pin 从发布清单中提取。
PIN="nvidia-tao-sdk[docker]==7.1.0rc42"  # versions-key: wheels.tao_sdk_docker
python -c "import tao_sdk" 2>/dev/null || python -m pip install "$PIN"
python -c "import docker" 2>/dev/null || python -m pip install "$PIN"
python -c "import tao_sdk, docker"

# DockerSDK 将每个任务容器附加到 ${DOCKER_NETWORK:-tao_default}。
# 如果缺少该网络，则创建它；该操作是本地且幂等的。
DOCKER_NETWORK_NAME="${DOCKER_NETWORK:-tao_default}"
docker network inspect "$DOCKER_NETWORK_NAME" >/dev/null 2>&1 || \
  docker network create "$DOCKER_NETWORK_NAME" >/dev/null
```

如果检查失败，代理会提示用户通过 Bash 授权安装/修复，然后继续。可自动安装/创建 Pip-installable Python 依赖项和 Docker 网络创建，然后重新运行预检。

## 凭证

除了访问 Docker 守护进程外，没有其他平台凭证要求。

可选环境：

- **DOCKER_HOST**：可选 Docker 守护进程 URL。如果未设置，SDK 使用 Docker Python 客户端的正常环境/默认套接字解析。对于 `remote-docker` 平台选项，需要它。
- **DOCKER_NETWORK**：任务容器的 Docker 网络。默认为 `tao_default`。
- **DOCKER_USERNAME**：注册用户名。默认为 NGC 的 `$oauthtoken`。
- **NGC_KEY**：用于从 `nvcr.io` 拉取私有镜像时使用。
- **HOST_SSH_PATH**：当 AutoML 大脑容器需要 SSH 密钥以监控远程 SLURM 子任务时，挂载到其中。
- **ACCESS_KEY**, **SECRET_KEY**, **S3_ENDPOINT_URL**, **S3_BUCKET_NAME**：
  可选的 S3 兼容存储设置，用于仍然从本地容器读取/写入云存储的任务。

## 启动预检

在生成脚本或启动容器之前：

1. 验证 Docker 守护进程可达，NVIDIA 容器工具包注册为 Docker 运行时，GPU 和驱动程序版本报告，并且冒烟容器在启动前可以看到 GPU。对于远程 Docker，通过 `docker run ... nvidia-smi` 对远程守护进程查询 GPU；不要使用代理机器上的本地 `nvidia-smi`。
2. 验证每个本地/文件数据集注释和媒体路径在 Docker 主机上存在。
3. 将每个绑定挂载分类为只读或可写。可写挂载必须默认使用 Docker 主机用户的数字 UID:GID，并且容器的身份 (`USER`/`LOGNAME`) 加上 HOME/框架缓存路径必须设置并可写。直接 Docker 必须显式传递它们（见“非根容器身份”）；SDK 在可写的 `/results` 绑定下准备它们（使用隔离的 `/tmp` 备用，仅用于没有的强制非根任务）。对于远程 Docker，在远程主机上解析身份，而不是复制代理笔记本电脑的数字 ID。
4. 对于 `s3://` 数据集/结果，验证 `ACCESS_KEY` 和 `SECRET_KEY` 已设置，并且可以使用 `aws s3 ls` 读取确切路径。如果 `aws` 缺失，报告缺失的依赖项并在安装前询问；安装后重新运行预检。
5. 在启动前验证模型特定凭证，例如 `HF_TOKEN`。
6. 使用 `nvidia-smi` 检查当前 GPU 占用情况，并在用户请求该约束时避免已由其他正在运行的任务使用的 GPU。在启动审查中显示选定的 GPU ID。
7. 对于具有已知架构限制的模型/容器组合，在启动前比较主机 GPU 计算能力与容器堆栈。如果选定的镜像无法 JIT 或运行主机架构的内核，则提前阻止并要求使用兼容的镜像或平台。

尽可能使用打包的辅助工具进行这些检查：

```bash
${TAO_SKILL_BANK_PATH:-~/tao-skills-external}/scripts/check_tao_launch_preflight.py \
  --platform local-docker \
  --container-image "<selected-image>" \
  --path train_annotation=/abs/path/to/annotations.json \
  --path train_media=/abs/path/to/media
```

对于远程 Docker 守护进程，使用 `remote-docker` 平台并通过传递或导出 `DOCKER_HOST`。辅助工具验证远程 GPU/运行时就绪情况，并通过只读绑定挂载检查远程主机数据集路径：

```bash
${TAO_SKILL_BANK_PATH:-~/tao-skills-external}/scripts/check_tao_launch_preflight.py \
  --platform remote-docker \
  --docker-host ssh://user@gpu-host \
  --container-image "<selected-image>" \
  --gpu-smoke-image ubuntu:22.04 \
  --path train_annotation=/remote/data/train/annotations.json \
  --path train_media=/remote/data/train
```

上面的 `--path` 值必须在远程 Docker 主机上存在。不要传递仅在本地笔记本电脑或 Codex 主机上存在的路径。

在远程 Docker 主机上解析实际提交用户的 UID:GID，然后显式将此身份传递给 SDK。不要重用客户端笔记本电脑的 UID:GID，并且不要从共享输出目录的 `stat` 所有权推断容器用户：该目录可能是 `root:<shared-group>` 或由其他组成员拥有。

```bash
REMOTE_RESULTS=/remote/results
# 使用 DOCKER_HOST=ssh://user@gpu-host 代表的 SSH 账户，
# 或从远程管理员获取这两个值。
REMOTE_UID="$(ssh user@gpu-host id -u)"
REMOTE_GID="$(ssh user@gpu-host id -g)"
case "$REMOTE_UID" in
  ''|*[!0-9]*|0)
    echo "需要一个经过验证的非根远程提交 UID。"
    exit 1
    ;;
esac
case "$REMOTE_GID" in
  ''|*[!0-9]*)
    echo "需要一个经过验证的数字远程提交 GID。"
    exit 1
    ;;
esac
TAO_DOCKER_CONTAINER_USER="$REMOTE_UID:$REMOTE_GID"
export TAO_DOCKER_CONTAINER_USER

# 证明此确切身份可以在绑定中创建和删除子任务。
docker --host "$DOCKER_HOST" run --rm \
  --user "$TAO_DOCKER_CONTAINER_USER" \
  -v "$REMOTE_RESULTS:/ownership-probe" ubuntu:22.04 \
  sh -c 'p=/ownership-probe/.tao-write-delete-probe-$$; touch "$p" && rm "$p"' || {
  echo "远程提交身份无法在 $REMOTE_RESULTS 下创建/删除。"
  exit 1
}
```

### 非根容器身份

`--user <uid>:<gid>` 是必要的，但不是充分的。TAO 镜像仅在 UID 1000 处提供非根账户（`ubuntu` 和 `taotoolkituser` 在那里冲突），因此其他所有数字 UID 都没有 `/etc/passwd` 条目。这使得在 UID-1000 工作站上的失败不可见，而在其他地方可重复。`getpass.getuser()` 读取 `LOGNAME`/`USER`/`LNAME`/
`USERNAME`，然后才回退到 `pwd.getpwuid()`，因此如果没有设置它们，查找会在任何 TAO 代码运行之前引发错误：

```
File "/usr/lib/python3.12/getpass.py", line 169, in getuser
    return pwd.getpwuid(os.getuid())[0]
KeyError: 'getpwuid(): uid not found: 1002'
```

Torch 在初始化其 inductor 缓存目录时达到该调用，因此容器在启动时退出 1。Docker 还将 `HOME=/` 留给未知 UID，这会将框架缓存发送到镜像拥有的路径。

因此，每个传递 `--user` 的直接 Docker 启动都必须传递身份和缓存环境。这些镜像了 SDK 在 `docker_handler.py` 中注入的内容；当两者之一更改时，请保持这两个列表同步。

```bash
HOST_UID="$(id -u)"; HOST_GID="$(id -g)"
TAO_HOME=/results/.tao-runtime/home        # 必须位于可写挂载上
mkdir -p "$RESULTS_DIR/.tao-runtime/home"

docker run --rm --gpus all --ipc=host \
  --ulimit memlock=-1 --ulimit stack=67108864 \
  --user "$HOST_UID:$HOST_GID" \
  -e USER="$HOST_UID" -e LOGNAME="$HOST_UID" \
  -e HOME="$TAO_HOME" \
  -e XDG_CACHE_HOME="$TAO_HOME/.cache" \
  -e HF_HOME="$TAO_HOME/.cache/huggingface" \
  -e TORCH_HOME="$TAO_HOME/.cache/torch" \
  -e TRITON_CACHE_DIR="$TAO_HOME/.cache/triton" \
  -e TORCHINDUCTOR_CACHE_DIR="$TAO_HOME/.cache/torchinductor" \
  -e MPLCONFIGDIR="$TAO_HOME/.cache/matplotlib" \
  -v "$DATA_DIR:/data:ro" -v "$RESULTS_DIR:/results" -v "$SPECS_DIR:/specs:ro" \
  "$IMAGE" <action> train -e /specs/<spec>.yaml
```

数字 `USER`/`LOGNAME` 值是故意的：它们描述了一个确实没有 passwd 条目的身份，并且它们仅用于缓存路径命名。不要因为启动 `getpwuid` 失败而省略 `--user`——这用启动错误换取根拥有的输出，这是更昂贵的失败来修复。

## 多 GPU 和多节点

**本地 Docker 不支持多节点。** 一个任务在本地 Docker 守护进程的主机上运行，没有跨主机协调。

本地主机上的多 GPU **支持** 通过 NVIDIA 容器工具包的 `--gpus` 标志（`--gpus all` 或 `--gpus '"device=0,1,2,3"'`）。`DockerSDK.create_job(gpu_count=N)` 通过到 `--gpus`。单主机分布式初始化使用 `localhost`；`torchrun --nproc-per-node=N` 或 PyTorch DDP 如常工作。

## 后端细节

使用 SDK 后端值 `local-docker`。本地后端模式没有额外的后端细节，因此大多数路由由环境和任务参数控制：

```json
{
  "backend_type": "local-docker",
  "num_gpu": 1
}
```

遵循 Brev SDK 设计，平台/控制平面值保持在 SDK 状态和 Docker 标签中。SDK 不会将 `BACKEND`、`HOST_PLATFORM`、`MONGOSECRET`、`DOCKER_HOST` 或 `DOCKER_NETWORK` 注入训练容器。

## 容器执行

TAO SDK 本地 Docker 处理器通过 Docker Python 客户端启动容器：

- 后端任务名称使用 SDK 处理器使用的 `tao-job-<job_id>` 形式。
- 命令通常是 `["/bin/bash", "-c", "<job command>"]`。
- 容器以分离模式运行。默认情况下，SDK 保留容器，因此状态和日志保持可检查，除非 `DOCKER_AUTO_REMOVE=true`。
- 使用 `run_as_user=None`（默认值），当它有一个绝对可写的 `/results` 绑定时，SDK 将本地任务映射到调用者的 UID:GID，保留本地补充组，并在 `/results/.tao-runtime/home` 下准备 HOME/框架缓存。`run_as_user=True` 选择其他本地挂载布局进入用户映射。如果 SDK 进程本身是 root，自动映射会失败，而不是映射 `0:0`；通过 `container_user` 提供经过验证的非根提交 UID:GID。`container_user` 也是远程主机的显式非根 Docker 用户覆盖。`run_as_user=False` 是故意选择退出，因为已证明该镜像需要 root。
- `/dev/shm` 挂载为 tmpfs。
- 配置的 Docker 网络由 Docker 守护进程应用于任务容器；它不会作为进程环境变量传递。
- 具有相同任务 ID 的现有容器在启动替换之前停止并删除。

对于 GPU 访问，处理器自动检测主机类型：

- Tegra 或 Jetson 主机使用 `runtime="nvidia"` 加上
  `NVIDIA_VISIBLE_DEVICES` 和 `NVIDIA_DRIVER_CAPABILITIES=all`。
- 标准 x86 主机使用 Docker `device_requests` 并带有 GPU 功能。

如果 `num_gpus` 是 `0`，则不分配 GPU。如果 `num_gpus` 是 `-1`，则请求所有可见 GPU。在共享开发机器上，请优先使用显式 GPU 计数。当显式设备 ID 可用时，在共享机器上优先使用它们，而不是仅计数选择，以防止启动时窃取其他任务占用的 GPU。

## 存储

本地 Docker 接受本地和 `file://` 路径，因为容器在相同的 Docker 主机上运行。确保规范中的每个路径都是：

- 由处理器或周围服务挂载到容器中，
- 容器内部已经可达，或
- 具有匹配凭证的云 URI。

对于绑定挂载的输出，主机用户所有权是一个启动不变量，而不是权限错误的工作around。根容器通常以 `root:root` 模式 `0755` 创建检查点子目录；然后主机用户无法删除它们中的文件，即使顶层输出目录已预先创建。
容器自动删除也会保留绑定挂载的输出。

仅在选定的镜像明显需要 root 时才选择退出主机用户映射 (`run_as_user=False`)。在启动审查中记录该例外，隔离其可写挂载，并在所有终端退出和取消后，将每个输出/缓存挂载规范化回 Docker 主机 UID:GID。对于远程 Docker，通过 `container_user` 传递远程主机的经过验证的非根身份；永远不要从客户端机器或输出目录所有者推断它。在所有权规范化成功之前，不要开始另一个实验。如果代理没有权限执行或验证该修复，则无法在本地 Docker 上启动需要 root 的镜像。

AutoML 的默认检查点保留更严格：其预检在启动试验前拒绝 `run_as_user=False`、命名卷、远程绑定挂载或兼容的显式 `container_user`，因为 SDK 无法保证主机侧删除。仅在明确禁用保留并且外部操作员拥有工件清理时，才将这些路线用于 AutoML。

对于远程/共享文件系统，优先使用拥有该文件系统的平台。例如，对于集群上的 Lustre 路径，使用 SLURM 加上 `lustre:///...`。

## 监控

- SDK 处理器直接映射 Docker 容器状态：创建 -> Pending，运行/重启 -> Running，暂停 -> Paused，退出代码 0 -> Complete，非零退出 -> Error。
- 日志直接从命名的容器通过 Docker Python 客户端 (`docker logs tao-job-<job_id>`) 获取。

如果容器已退出、死亡、正在删除或无法找到，状态协调将后端进程视为终止。

## 取消

取消停止命名的容器。GPU 所有权由 Docker / NVIDIA 运行时管理，而不是由 TAO Core 的本地 GPU 管理器管理。

## 可选：通过 TAO SDK

如果您需要任务句柄、通过 SDK 的 `script_runner` 的 S3 I/O 包装或跨会话的持久性：

```python
import os

from tao_sdk.platforms.docker import DockerSDK

docker_host = os.environ.get('DOCKER_HOST', '')
is_remote = bool(docker_host) and not docker_host.startswith(('unix://', 'npipe://', '/'))
container_user = os.environ.get('TAO_DOCKER_CONTAINER_USER')
if is_remote and not container_user:
    raise RuntimeError('Set TAO_DOCKER_CONTAINER_USER to the remote output owner UID:GID')

sdk = DockerSDK()  # 从环境读取 DOCKER_HOST、NGC_KEY、S3 凭证
job = sdk.create_job(
    image='nvcr.io/nvidia/tao/tao-toolkit:7.1.0-pyt',  # versions-key: images.tao_toolkit.pyt
    command='dino train -e /data/spec.yaml',
    gpu_count=1,
    mounts=[
        {'host_path': '/host/data', 'container_path': '/data', 'read_only': True},
        {'host_path': '/host/results', 'container_path': '/results'},
    ],
    container_user=container_user,
)

status = sdk.get_job_status(job.id)
logs = sdk.get_job_logs(job.id, tail=200)
```

这包装了相同的 `docker run` 调用，使用 `Job` 句柄。对于 S3 I/O，首先调用 `build_entrypoint(...)` 并传递其命令，以便 `script_runner` 可以执行声明的下载/上传。如果您不需要任务跟踪或该包装器，请直接使用 `docker run`——不需要安装 SDK。

## 失败模式

**Docker 客户端未初始化**：验证 Docker Python 包已安装，如果未使用默认本地套接字，则设置 `DOCKER_HOST`，并确认进程可以与守护进程通信。

**GPU 分配失败**：请求的 GPU 不可用，NVIDIA 容器工具包未配置，或 Docker 守护进程无法创建 GPU 设备请求。使用较少的 GPU，等待另一个任务完成，或验证主机上 `docker run --gpus ...` 是否工作。

**镜像拉取认证失败**：为私有 `nvcr.io` 镜像设置有效的 `NGC_KEY`，或在 Docker 主机上运行 `docker login nvcr.io -u '$oauthtoken'`。

**容器意外退出**：检查 `docker logs tao-job-<job_id>`、配置的 `DOCKER_NETWORK` 和 SDK 动作运行器生成的命令。

**`KeyError: getpwuid(): uid not found`**：启动传递了 `--user`，但镜像中没有 `/etc/passwd` 条目的 UID，并且没有传递 `USER`/`LOGNAME`。添加“非根容器身份”中的身份和缓存环境；不要回退到以 root 运行。

**容器内路径缺失**：主机上的本地路径不一定挂载到任务容器中。使用受动作运行器支持的路径约定，或通过周围服务配置显式卷。

**根拥有的绑定挂载结果**：停止启动新的实验，从 `docker inspect` 识别每个可写挂载，并让主机管理员修复现有所有权一次。未来的启动必须使用主机 UID:GID 映射和可写的 HOME/缓存重定向。`docker rm` 和 `DOCKER_AUTO_REMOVE` 不会修复或删除绑定挂载的文件。
