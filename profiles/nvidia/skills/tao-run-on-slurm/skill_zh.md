# SLURM

> **是否为独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

用于由 SLURM 管理的集群的远程 GPU 计算平台。作业从启动主机通过 SSH 提交给登录节点，在共享文件系统上暂存，使用 `sbatch` 提交，并使用 `srun` 容器支持执行。

## 使用场景

当用户可以访问受管理的 GPU 集群、共享 Lustre 存储和调度器拥有的 GPU 分配时，使用 SLURM。不要使用 SLURM 用于仅存在于代理机器上的本地文件；数据和输出必须可以从集群访问。

## 预检 + SSH

确认 `SLURM_USER` 和 `SLURM_HOSTNAME` 已导出，并且密码 SSH 到登录主机工作 (`ssh -o BatchMode=yes`)。
启动主机需要 `ssh`，而不是本地 `sbatch`、`srun`、Enroot 或 Lustre 挂载。在选定的远程登录/计算框架上预检调度器、Pyxis、Enroot 和共享存储依赖项。特定于模型的检查器可以通过 SSH stdin 从安装的技能流式传输；不要暂存 ad-hoc 源补丁或将启动主机视为 SLURM 框架。
对于私有的 `nvcr.io` 镜像，在集群上每对（集群，用户）安装一次 `~/.config/enroot/.credentials`：Pyxis/Enroot 不会从作业环境读取 `NGC_KEY`，并且如果没有持久凭证，授权保护的拉取会在作业启动时以“无法处理 JSON 输入”失败。通过 `printf | ssh` heredoc 安装它，以便 `NGC_KEY` 值永远不会出现在 shell 历史记录、中间文件或聊天输出中；永远不要 `cat`/`echo` 该值。

如果预检检查失败，代理会提示用户通过 Bash 授权安装/修复。可 pip 安装的 Python 要求是例外：自动安装它们，然后重新运行预检。

有关完整的预检脚本、enroot 凭证 heredoc、先决条件密钥设置（密钥对、`ssh-copy-id`、`known_hosts`、容器密钥挂载、2FA 处理）和 SSH 失败修复提示，请参阅 `references/slurm-ssh-credentials.md`。

## 执行 — 四个动词

`tao-run-on-slurm` 是一个平台 **消费者**：它在 `ssh + sbatch/squeue/sacct/scancel` 上运行 spec-bundle，仅修改作业记录。存储是 **A 级**（Lustre）— 数据集在提交之前暂存到共享路径，并通过 Pyxis 读取；永远不要在分配内获取 S3（调度器空闲超时会杀死 GPU 空闲作业并计费浪费的时间）。`$BANK` = `${TAO_SKILL_BANK_PATH}`；`$LOGIN` = 解析的 `SLURM_HOSTNAME`。

### 提交

1. **重用已暂存的 — 永远不要重做（A 级）：**
   - *镜像:* `@@IMAGE@@` 是一个 Lustre `.sqsh` — **如果存在，重用一个现有的** (`ssh $LOGIN ls <sqsh>`)；只有如果缺失，才使用 `enroot import` 一次性转换（按名称缓存 — 见 `references/slurm-container-execution.md`）。
   - *数据集:* **确认它已经在 Lustre 上** (`ssh $LOGIN test -e …`) 并引用那些路径；`tao-data-io` 仅暂存一个不存在的辅助输入 — 永远不要重新暂存现有数据，并且永远不要在分配内暂存训练集。
   然后在 Lustre 上的 `<job_dir>/specs/spec.yaml` 处编写 spec，使用那些路径。
2. **凭证 → 侧车（永远不要内联）：** 如果运行需要会话凭证（例如 `HF_TOKEN`），将它们写入 Lustre 上的模式-600 侧车，并让模板在退出时销毁它；NGC 镜像拉取使用一次性 `~/.config/enroot/.credentials`（见 `references/slurm-ssh-credentials.md`），而不是作业环境：
   ```bash
   set -a; source /path/to/.env; set +a   # 如果已经导出，则省略
   printf 'export HF_TOKEN=%s\n' "$HF_TOKEN" | ssh $LOGIN "umask 077; cat > <job_dir>/job_$JOB_ID.env"
   ```
3. **打开记录 — 创造 id，在启动之前绑定 `results_dir` 在 Lustre 上：**
   ```bash
   JOB_ID=$("$BANK/scripts/tao_job_record.py" open --platform slurm --image "$IMAGE" \
     --network-arch "$ARCH" --action "$ACTION" --storage-tier A --results-root "$SLURM_BASE_RESULTS_DIR")
   ```
4. **消费可选的模型生命周期。** 如果经过验证的 spec-bundle 有 `execution`，则在将分布式意图映射到原生 SLURM/Pyxis 的同时保留其顺序和语义。仅暂存其 checksum 封闭的 `supporting_files`。完整的通用生命周期和暂存合同在 `references/slurm-container-execution.md` 中。
5. **渲染** `templates/slurm/singlenode.sbatch.tmpl` — 替换每个 `@@<NAME>@@` (`JOB_NAME=$JOB_ID`，`NUM_GPUS`，`CPUS_PER_TASK`，`TIME`，`LOG_DIR`，`IMAGE`，`CONTAINER_MOUNTS=<RUNTIME_SUPPLIED_MOUNTS>`，`COMMAND=<bundle command reading the shared-storage spec>`，`SBATCH_EXTRA=` 账户/分区行，`ENV_FILE=` 侧车路径或空，`EXTRA_ENV=` 任何集群 NCCL 调整）→ `<job_dir>/sbatch/job_$JOB_ID.sbatch`。
   **在提交之前进行 Lint + 语法检查：** `redact_secrets.py lint <sbatch>` 必须通过，并且 `bash -n <sbatch>` 必须成功。
6. **提交 + 记录 RUNNING:**
   ```bash
   SLURM_ID=$(ssh $LOGIN "sbatch --parsable <job_dir>/sbatch/job_$JOB_ID.sbatch")
   "$BANK/scripts/tao_job_record.py" mark "$JOB_ID" --state RUNNING --backend-ref "$SLURM_ID"
   ```

一个跳过门或打开的提交没有 id — 所以它不能启动。

### 状态

```bash
# sacct 注释状态（“由 12345 取消”）并将其截断为默认列宽，所以取消的作业在返回时读取为“CANCELLED+”并且与下表中的任何内容都不匹配 — 报告未知而不是 CANCELED。
# 放宽列，取第一个单词，删除截断标记。
st=$(ssh $LOGIN "sacct -j $SLURM_ID -X -n -o State%30" | awk '{print $1}' | tr -d '+')
# (在作业仍然是 PENDING 时使用 squeue；sacct 在提交后短暂延迟)
```

| SLURM 状态 | 词汇 |
|---|---|
| `PENDING` | `PENDING` |
| `RUNNING` / `COMPLETING` | `RUNNING` |
| `COMPLETED` | `COMPLETE`（确认 `results_dir` 中的 `status.json`） |
| `FAILED` / `TIMEOUT` / `OUT_OF_MEMORY` | `ERROR`（基础设施与程序分类 → 重试，M6） |
| `NODE_FAIL` / `BOOT_FAIL` | `ERROR`，`err_class=ERR_INFRA` (`--requeue` 重新排队这些） |
| `CANCELLED` / `PREEMPTED` / `REVOKED` | `CANCELED` |
| (未找到) | `UNKNOWN` |

原生子状态位于转换 `message` 中。在选定的间隔内轮询；长时间的队列等待是正常的 — 不要在经过的时间后停止。

### 日志

```bash
ssh $LOGIN "tail -n ${N:-200} <log_dir>/$JOB_ID-$SLURM_ID/main.out"   # SLURM 自动创建 %x-%j 子目录
```

### 取消

```bash
ssh $LOGIN "scancel $SLURM_ID"
"$BANK/scripts/tao_job_record.py" mark "$JOB_ID" --state CANCELED --source agent
```

将已终止的 SLURM 作业视为成功的取消。

### 多节点（节点 > 1）

相同的四个动词，提交时有三个补充：

1. **渲染 `templates/slurm/multinode.sbatch.tmpl`** 而不是单节点的一个 — 它是严格的超集（添加 `--nodes` / `--wait-all-nodes` + 会晤块）。`WORLD_SIZE` 是 **节点数**（TAO 的误称）；永远不要将其更改为全局排名计数。
2. **NCCL 探测首先** — 在实际作业之前，运行一个廉价的 2 节点 all-reduce (`scripts/nccl_allreduce_probe.py` 在容器下的 torchrun) ~120s 超时。在调用 torchrun 之前，保留 TAO 会晤值作为 `TAO_NODE_COUNT=$WORLD_SIZE`，
   `TAO_GPUS_PER_NODE=$NUM_GPU_PER_NODE`，和 `TAO_NODE_RANK=$SLURM_PROCID`；torchrun 会用全局进程计数覆盖其标准的 `WORLD_SIZE`。`NCCL_PROBE_OK` → 继续。
   **超时**（集体挂起）
   → 在 `EXTRA_ENV` 中设置集群的 NCCL 调整并重新探测 — 在 CS-OCI-ORD 上是 `export NCCL_P2P_DISABLE=1`（节点间 P2P 挂起），通常与 `NCCL_SOCKET_IFNAME=eth0` / `NCCL_IB_DISABLE=1`。**为每个集群缓存工作环境**以便后续作业跳过探测。在 `gpus_per_node > 1` 上设置门 — 单个节点上的 2+ GPU 会触发 P2P 挂起。
3. A 级 Lustre、侧车凭证、记录和 lint 不变。

### Cosmos 后端护栏

在渲染 Cosmos 命令之前阅读 [`references/cosmos-slurm-guardrails.md`](references/cosmos-slurm-guardrails.md)。
它定义了镜像暂存、规划器材料化、框架和 Cosmos-RL 启动合同、工作/运行时要求以及退出/状态处理。

## 存储

使用共享文件系统 URI，而不是本地或 `file://` 路径；`tao-core` 拒绝远程后端用于本地/file 路径。

- `lustre:///absolute/path` 用于 Lustre 上的用户提供的数据集。
- `slurm://` 路径可能出现在微服务元数据中，并且在容器启动之前转换为 Lustre 路径。

接受数据集根（模型技能将它们映射到所需文件）或直接 spec-key 路径。在 SSH 成功后和生成脚本之前，从登录主机测试每个所需数据集路径；如果失败，停止并要求更正路径或暂存数据，而不是生成在第一个训练作业中失败的脚本。有关根与直接 spec 模式、后端细节和结果目录默认值，请参阅 `references/slurm-ssh-credentials.md`。

## 容器执行

`tao-core` 通过 Pyxis/Enroot 运行 TAO 容器：

1. 在 `<job_dir>/specs`、`<job_dir>/env` 和 `<job_dir>/meta` 下暂存紧凑的 JSON 文件用于 spec、环境和云元数据。
2. 在 GPU 作业之前将 Docker 镜像转换为缓存的 SQSH 镜像，使用 `srun -n1 -p <conversion_partition> enroot import`。这是一个按图像的一次性成本，而不是可选的优化 — 见 *从 GPU 分配获取图像* 下方。
3. 在 `<job_dir>/sbatch/job_<job_id>.sbatch` 下编写 sbatch 脚本。
4. 提交 `sbatch --export=ALL <script>`。
5. 使用 `srun --container-image=<image> --container-mounts=<RUNTIME_SUPPLIED_MOUNTS>` 运行容器。

接受的图像格式：`/path/to/image.sqsh`，`registry#image:tag`，`docker://registry#image:tag`，以及普通的 `registry/image:tag`（在需要时转换为 Pyxis 形式）。SQSH 转换按图像名称缓存；对于 `:latest` 图像，除非启用 `force_reconvert_latest`，否则会重用缓存的 SQSH。

### 从 GPU 分配获取图像

**GPU 从分配开始时就是你的，不是从计算开始时。** 作业在训练之前所做的任何操作 — 拉取注册表图像、转换它、获取数据集 — 都在空闲的 GPU 上运行，这些 GPU 正在计费并且可见于集群的 GPU 空闲收割者。第一次 TAO 拉取加上 Enroot 转换需要几分钟的空闲 GPU 时间，这足够长以至于可能被杀死并且足够昂贵。

因此，图像必须在 GPU 作业开始时已经是一个本地 `.sqsh`。直接将 `docker://` 或 `registry#image:tag` URI 传递给 `srun --container-image=` 会使 Pyxis 在分配内拉取和转换 — 这正是陷阱。在 CPU 分区上转换一次，然后将每个后续作业指向生成的文件：

```bash
# 每个图像一次，在 CPU 上 — 不消耗 GPU 时间。
ssh $LOGIN "test -e <sqsh>" || \
  ssh $LOGIN "srun --chdir=/tmp -n1 -c4 --mem=7200M \
    -p <cpu_partition> -t <minutes> \
    bash -c 'set -Eeuo pipefail
      export TMPDIR=/tmp
      export ENROOT_TEMP_PATH=/tmp/enroot-tao-\${SLURM_JOB_ID}
      export SLURM_ENROOT_TEMP_PATH=\${ENROOT_TEMP_PATH}
      mkdir -p \"\${ENROOT_TEMP_PATH}\"
      cd /tmp
      enroot import -o <sqsh> docker://<registry>#<image>:<tag>'"

# 每个GPU作业都引用文件，而不是注册表。
srun --container-image=<sqsh> ...
```

相同的规则适用于数据：在提交之前暂存到 Lustre（A 级）而不是在分配内获取。

CS-OCI-ORD 转换使用 `cpu_long`，4 个 CPU，7200M 内存，无独占节点，节点本地 Enroot 临时路径，以及至少 120 分钟。执行参考记录了证据和 `QOSGrpMemLimit` 恢复合同。

部分转换是自我检测的：SQSH 由 `hsqs` 魔法验证，因此一个截断的文件会被拒绝而不是被默默地使用。转换运行一次，然后按图像名称缓存。

**转换失败绝不能回退到注册表图像。** 诱人的恢复 — 将 `docker://…` 传递给 `srun` 并让 Pyxis 处理它 — 将拉取放回 GPU 分配内，这正是转换存在要避免的成本，并且它是在已经出问题的时候发生的。将失败或截断的转换视为致命：在 CPU 分区上修复它并重新提交。

诊断：如果作业意外地缓慢产生输出，请检查 `--container-image=` 实际接收了什么。那里有一个注册表 URI — 而不是 `.sqsh` 路径 — 意味着拉取发生在 GPU 上。

## 监控和取消

- 调度器状态来自存储的 SLURM 作业 id 通过 `squeue`/`sacct`；TAO 终端状态来自共享结果文件夹中的 `status.json`。
- 在聊天监控启用时，保持按请求的间隔轮询任何非终端作业 (`PENDING`，`RUNNING` 或其他)。不要在固定经过的时间后停止，例如 30 分钟；在共享 GPU 分区上长时间的队列等待是正常的。
- 在聊天监控启用时，不要在非终端 SLURM 作业上发送最终响应。最终响应是脱离动作；仅在用户要求脱离/停止或作业达到终端状态时使用它。
- 日志通过 SSH 从
  `<job_dir>/slurm-logs/<slurm_job_name>-<slurm_job_id>/main.out` 和 `.err` 读取。
- 通过 SSH 查找 `backend_details.slurm_metadata.slurm_job_id` 并运行 `scancel <slurm_job_id>`。将缺失或已终止的作业视为成功的取消。

状态映射：

- `PENDING` -> `Pending`
- `RUNNING` or `COMPLETING` -> `Running`
- `COMPLETED` -> 检查 `status.json`
- `FAILED`, `BOOT_FAIL`, `DEADLINE`, `OUT_OF_MEMORY`, `NODE_FAIL` -> 如果日志匹配可重试的基础设施模式，则重试，否则 `Error`
- `CANCELLED`, `PREEMPTED`, `REVOKED` -> `Canceled`
- `TIMEOUT` -> `Error`
- `SUSPENDED`, `STOPPED` -> `Running`（仍然由调度器拥有并且可能恢复；原生子状态位于转换消息中 — 与 docker `paused` 的约定相同）

## 必需的输入

在 SLURM 接收中请求这些；有关完整的凭证列表、微服务模式键和默认值，请参阅 `references/slurm-ssh-credentials.md`。

- **SLURM_USER**（必需）：登录节点的 SSH 用户名。
- **SLURM_HOSTNAME**（必需）：用于故障转移的逗号分隔登录主机名。
- **SLURM_PARTITION**（必需）：用于 GPU 提交的分区列表。打包默认 `polar,polar3,polar4,grizzly`，视为 4 小时队列。
- **SSH_KEY_PATH**（首选，预期在启动之前）：用于非交互式公钥认证的私钥。在修复中首先请求此内容；优先于 `SSH_AUTH_SOCK` 代理套接字回退。
- **SLURM_BASE_RESULTS_DIR**（可选）：共享文件系统路径；默认为在运行时提供并验证的共享存储根。
- **SLURM_ACCOUNT**（通常由站点策略要求）：`#SBATCH --account` 的账户。

除非用户表示他们的站点需要账户、想要自定义结果根或工作流无法在没有覆盖默认值的情况下进行，否则不要在初始接收中请求 `SLURM_ACCOUNT` 或 `SLURM_BASE_RESULTS_DIR`。

## 资源默认值

来自 `tao-core` 的默认值：

- `num_nodes`: 1
- `num_gpus`: 4
- `max_num_gpus_per_node`: 8
- `cpus_per_task`: 16
- `time_hours`: 4
- `timeout_hours`: 3.8
- `max_time_hours`: 4
- `container_mounts`: 运行时提供的显式源到目标挂载
- `use_requeue`: true
- `use_sqsh`: true

启动器必须使用打包的 4 小时墙和 3.8 小时子超时默认值，永远不要 12 小时。如果用户提供更长的 `SLURM_TIME_HOURS`，请在提交之前验证所选分区是否支持它。对于打包的默认分区列表 `polar,polar3,polar4,grizzly`，拒绝请求超过 4 小时，并且仅在用户实际上想要更长的墙时间时才请求不同的分区。

在或高于 `max_num_gpus_per_node`，分配独占节点，并从总 GPU 推导它们的数量。

## 多节点和重试

对于多节点作业 (`num_nodes > 1`)，渲染的
`templates/slurm/multinode.sbatch.tmpl` 设置了 sbatch 指令并导出了 PyTorch 分布式会晤环境变量：`WORLD_SIZE`，`NUM_GPU_PER_NODE`，`NODE_RANK`，`MASTER_ADDR` 和 `MASTER_PORT`（29500）。TAO 入口点读取 `WORLD_SIZE` + `NUM_GPU_PER_NODE` 并内部构建 torchrun。Cosmos-RL 对控制器、策略和滚动工人有特殊的角色处理。有关 `### Multi-node (nodes > 1)` 提交子部分的 NCCL-probe 门和每个集群环境缓存的详细信息，请参阅上文。

**使用 Lustre，而不是 S3，用于 SLURM 作业输入。** GPU 分配从作业派送开始时就开始，所以顶部的脚本中长时间的 `s3://` 下载会烧掉分配，可能会因为 GPU 空闲而被杀死，无论是否计费。首先将训练数据暂存到共享文件系统，然后将其作为 `lustre:///...` 引用。S3/HF/NGC 预取适用于小的辅助输入（检查点、配置），而不是训练数据集。K8s/Brev 不共享此调度器空闲约束。

在基础设施故障 (`NODE_FAIL`，`BOOT_FAIL`，NCCL 传输超时，CUDA 驱动初始化失败，GPU/IB 链路断开，OOM-killer 节点回收，Xid 错误），从日志中分类基础设施与程序，并在重新提交暂存的工作负载（M6）之前创建一个新的重试记录 `--retry-of`。普通的训练失败立即出现，所以一个损坏的 spec 不会消耗重试预算。`#SBATCH --requeue` 默认通过 `SLURM_USE_REQUEUE=true` 启用，所以 SLURM 本身会在 `NODE_FAIL` 或抢占之前重新排队作业，任何代理级别的重新提交之前；工作负载合同（例如 Cosmos）可能需要 `--no-requeue`。

将空的 `sbatch --parsable` 响应或 SSH 断开连接视为模糊：通过确切的作业名称进行协调，永远不要盲目提交，并验证继承的节点排除。参考的执行指南定义了完整决策表。有关 `references/slurm-container-execution.md` 的完整多节点环境变量/sbatch 指令细节和表格、集群要求、完整的 Lustre-not-S3 规则以及故障模式清单。

## 参考

- `references/slurm-ssh-credentials.md` — 预检脚本、SSH/密钥设置、enroot 凭证、完整凭证列表、后端细节、存储规则、SSH 修复提示。
- `references/slurm-container-execution.md` — 容器执行步骤、监控、状态映射、取消、多节点细节、Lustre-not-S3、重试、故障模式。
- `references/slurm-preflight-storage.md` — 扩展预检/存储笔记。
- `references/cosmos-slurm-guardrails.md` — Cosmos 框架和 Cosmos-RL 启动和状态护栏。
- `references/detailed-guide.md` — 分割参考的导航地图。
