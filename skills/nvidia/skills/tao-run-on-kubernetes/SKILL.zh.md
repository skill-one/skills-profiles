---
name: tao-run-on-kubernetes
description: Kubernetes执行平台——将TAO容器作业作为k8s作业提交，并支持NVIDIA GPU调度；单节点使用单Pod，多节点分布式训练使用Indexed Jobs。适用于在安装了NVIDIA GPU Operator的EKS/GKE/AKS/本地集群上运行，或是在现有k8s原生ML平台上集成TAO时使用。
---

# Kubernetes

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

将 TAO 容器作业作为 Kubernetes Jobs 提交。适用于任何可通过 kubeconfig 访问的集群（EKS / GKE / AKS / 本地）或在集群内服务账户（在 Pod 内运行时）。

默认单节点；通过 `num_nodes > 1` 选择多节点分布式训练（使用 Indexed Job + 无头服务，见下文 [多节点分布式训练](#multi-node-training-distributed)）。

## 预检

三项检查：GPU 主机运行时就绪、可通过 `kubectl` 访问集群、存在 NVIDIA GPU Operator/设备插件。

```bash
# 0. GPU 节点主机运行时。
# 在每个自管理的 GPU 工作节点上运行或在节点镜像构建中运行。
# 仅在云提供商或 GPU Operator 策略拥有驱动程序/工具包生命周期的托管 GPU 节点上设置 TAO_K8S_SKIP_NODE_RUNTIME_CHECK=1。
if [ "${TAO_K8S_SKIP_NODE_RUNTIME_CHECK:-0}" != "1" ]; then
  TAO_SKILL_BANK_ROOT="${TAO_SKILL_BANK_ROOT:-$PWD}"
  SETUP_SCRIPT="${TAO_SKILL_BANK_ROOT}/skills/platform/tao-setup-nvidia-gpu-host/scripts/setup-nvidia-gpu-host.sh"

  bash "$SETUP_SCRIPT" --backend kubernetes --check-only || {
    echo "缺失：TAO Kubernetes GPU 节点运行时不就绪。"
    echo "对于自管理 GPU 节点，在用户批准后运行："
    echo "  bash \"$SETUP_SCRIPT\" --backend kubernetes --install --yes"
    echo "对于托管集群，验证节点镜像/GPU Operator 策略安装驱动程序 580 和工具包 1.19.0，然后设置 TAO_K8S_SKIP_NODE_RUNTIME_CHECK=1。"
    exit 1
  }
fi

# 1. 集群可访问（kubeconfig 或集群内服务账户）
command -v kubectl >/dev/null 2>&1 || {
  echo "缺失：kubectl 未在 PATH 中找到。安装 kubectl 以提交 Jobs。"
  exit 1
}
kubectl cluster-info >/dev/null 2>&1 || {
  echo "缺失：无法访问集群（kubeconfig 在 ~/.kube/config、\$KUBECONFIG 或 Pod 内服务账户）。"
  echo "为您的集群配置 kubectl，或设置 \$KUBECONFIG："
  echo "  EKS：aws eks update-kubeconfig --name <集群> --region <区域>"
  echo "  GKE：gcloud container clusters get-credentials <集群> --region <区域>"
  echo "  AKS：az aks get-credentials --resource-group <rg> --name <集群>"
  echo "  本地：minikube start   (见下文 '本地集群')"
  exit 1
}

# 2. NVIDIA GPU Operator 存在（软检查——警告，不失败）
gpu=$(kubectl get nodes -o jsonpath='{range .items[*]}{.status.allocatable.nvidia\.com/gpu}{"\n"}{end}' 2>/dev/null | grep -v '^$' | head -1)
if [ -z "$gpu" ] || [ "$gpu" = "0" ]; then
  echo "警告：此集群没有可分配的 nvidia.com/gpu。"
  echo "在提交 GPU 作业前安装 NVIDIA GPU Operator："
  echo "  https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/getting-started.html"
fi
```

GPU 节点运行时检查对于自管理节点是强制性的。对于客户端不在 GPU 工作节点上的托管集群，请验证提供商节点镜像或 GPU Operator 策略，而不是在客户端运行安装程序，并设置 `TAO_K8S_SKIP_NODE_RUNTIME_CHECK=1`。这里的 GPU 容量警告是软检查；`submit` 语句会重新检查可分配的 `nvidia.com/gpu` 并在应用清单前硬失败（没有组调度，因此太大的 Job 会永远处于 `Pending` 状态）。

## 凭证和配置

- **kubeconfig**（其中一个）：
  - `~/.kube/config` — 默认发现路径
  - `$KUBECONFIG` — 替代路径
  - 集群内服务账户 — 在 Pod 内运行时使用（无需 kubeconfig）
- **TAO_K8S_NAMESPACE**（可选）：作业提交的默认命名空间。默认为 `default`。
- **TAO_K8S_CONTEXT**（可选）：切换集群的 kubeconfig 上下文名称。
- **NGC_KEY**（可选）：用于 nvcr.io 镜像拉取。如果您已在目标命名空间预创建了镜像拉取密钥，请在渲染的清单的 `imagePullSecrets` 中引用其名称。
- **AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / S3_BUCKET_NAME / S3_ENDPOINT_URL**（可选）：用于 S3 数据集 I/O（存储层 C），通过每个作业的 Secret (`envFrom.secretRef`) 注入 Pod，永不内联。遗留 `ACCESS_KEY`/`SECRET_KEY` 由 `tao-data-io` 映射。

对于 Kubernetes 运行，不要请求 Brev 或 SLURM 凭证。仅在选定工作流使用 `s3://` 输入或输出时请求 S3 凭证，仅在需要特定模型凭证（如 `HF_TOKEN`）时请求模型特定凭证。在启动前，验证选定的命名空间可以创建 Jobs，数据集/结果路径从 Pod 中可见，PVC/挂载文件系统路径已证明已挂载到作业容器中；代理主机本地路径不足以证明。

## 执行——四个动词

`tao-run-on-kubernetes` 是一个平台 **消费者**：它通过 `kubectl` 运行 spec-bundle，仅修改作业记录。不需要 nvidia-tao-sdk，不需要 `tao_sdk` 导入——作业使用纯 `kubectl apply` 提交。
`$BANK` = `${TAO_SKILL_BANK_PATH}`。

### submit

1. **GPU 容量门禁——首先硬失败**（没有组调度 → 太大的 Job 会永远处于 `Pending` 状态）：
   ```bash
   ALLOC=$(kubectl get nodes -o jsonpath='{range .items[*]}{.status.allocatable.nvidia\.com/gpu}{"\n"}{end}' | awk '{s+=$1} END{print s+0}')
   [ "${ALLOC:-0}" -ge "$NUM_GPUS" ] || { echo "GPU 不足：需要 $NUM_GPUS，可分配 $ALLOC"; exit 1; }
   ```
2. **存储层**（通过 `tao-data-io`）：**A** = 挂载一个包含数据的绑定 PVC/NFS（授权挂载路径，不下载——空气间隙解决方案，以及打包模板所做的）；**C** = 临时：initContainer 从 S3 下载到共享 `emptyDir`，最后一步在 TTL 到期前将结果上传到 S3。

   **层 C 在 GPU 下载时占用 GPU。** Pod 为其整个生命周期保留 `nvidia.com/gpu`（包括 initContainers），因此大型层 C 下载——或首次 GB 级镜像拉取——会占用并可能被回收空闲 GPU 时间，就像在 SLURM 分配内拉取一样。当数据已存在于 PVC 上时，优先选择层 A；知情选择层 C，用于小输入。

   生产者动作请求可以声明多个挂载，包括重复源别名用于逻辑和嵌入的绝对路径。阅读 `references/action-request.md` 并使用其暂存映射加上打包渲染器。对于 `mode=config`，首先生成生产者的嵌套 spec，暂存该确切生成的文件，并将其传回渲染器，以便 Pod 接收一个经过验证的只读配置挂载。遗留的单根模板无法表示该合同。
3. **打开记录——生成 ID，绑定 `results_dir`，在启动前：**
   ```bash
   JOB_ID=$("$BANK/scripts/tao_job_record.py" open --platform kubernetes --image "$IMAGE" \
     --network-arch "$ARCH" --action "$ACTION" --storage-tier "$TIER" --results-dir "$RESULTS_DIR")
   ```
   `results_dir` 必须是 **挂载的（持久的）卷路径或 S3 前缀**——`ttlSecondsAfterFinished` 在作业结束后删除作业及其日志，因此后来无法从作业对象中恢复任何内容。
4. **渲染、门禁、应用并记录 RUNNING。** 对于生产者动作请求，请遵循 `references/action-request.md`；它负责后端名称规范化、条件 Secret 引用、原生 argv 渲染、服务器干跑，并将应用对象名称绑定到作业记录。对于简单的单根 spec-bundle，渲染 `templates/k8s/single-pod-job.yaml.tmpl`，运行 `redact_secrets.py lint` 加上 `kubectl apply --dry-run=server`，应用它，并标记记录为 `backend-ref=<namespace>/<实际对象名称>`。

跳过门禁或打开的提交没有 ID——因此无法启动。

### status

保留 `K8S_JOB_NAME` 从提交。在重新附加时，读取作业记录的 `backend_ref=<namespace>/<名称>` 并从该字段恢复这两个值；不要假设 Kubernetes 名称等于记录 ID。

```bash
kubectl get job "$K8S_JOB_NAME" -n "$NAMESPACE" \
  -o jsonpath='{.status.conditions[0].type} {.status.active} {.status.succeeded} {.status.failed}'
```

| kubectl 信号 | 词汇 |
|---|---|
| 没有 Pod 调度 | `PENDING` (`kubectl get pods -n "$NAMESPACE" -l job-name="$K8S_JOB_NAME"` → `ImagePullBackOff` / `Insufficient nvidia.com/gpu` 在 `message` 中) |
| `active` ≥ 1 | `RUNNING` |
| 条件 `Complete` | `COMPLETE` |
| 条件 `Failed` | `ERROR`（从 Pod 的终止原因分类——`OOMKilled` → `ERR_INFRA`） |
| 作业/Pod 未找到 | `UNKNOWN`（可能被 TTL 删除——作业记录是真相来源） |

### logs

```bash
kubectl logs -n "$NAMESPACE" -l "job-name=$K8S_JOB_NAME" --tail "${N:-200}"
```

### cancel

```bash
kubectl delete job "$K8S_JOB_NAME" -n "$NAMESPACE" --cascade=foreground
if [ -n "${CRED_SECRET:-}" ]; then
  kubectl delete secret "$CRED_SECRET" -n "$NAMESPACE" --ignore-not-found
fi
"$BANK/scripts/tao_job_record.py" mark "$JOB_ID" --state CANCELED --source agent
```

### 多节点（节点 > 1）

相同的四个动词，加上：

1. **版本门禁：** 需要 k8s ≥ 1.28 (`kubectl version -o json`)——Pod 主机名 `<job>-<index>`（PodIndexLabel）`MASTER_ADDR=<job>-0.<svc>` 解析到的需要它；在旧集群上 rank-0 在会晤时挂起。
2. **容量门禁 × 节点：** 除非可分配的 GPU ≥ `gpus_per_node × nodes`（没有组调度 → 部分启动会让 rank-0 永远等待）则硬失败。
3. **渲染 `templates/k8s/indexed-job.yaml.tmpl`**——无头服务 + Indexed Job + 会晤环境 (`WORLD_SIZE` = 节点数，`NODE_RANK` 来自 `JOB_COMPLETION_INDEX`，`MASTER_ADDR=<job>-0.<svc>`，`/dev/shm` 16Gi 以免 NCCL 悄然挂起）。`kubectl apply -f` 一起创建服务和作业；`cancel` 前景删除作业（Foreground）和服务。
4. **NCCL 探测首先**（像 SLURM）——一个 2 节点全归约，带超时；挂起时，设置集群 NCCL 环境并重新探测；缓存每个集群。

## 本地集群（开发、CI 和评估）

一个一次性 minikube/kind 集群锻炼了准入、四个动词、作业记录接线以及日志管道，而无需集群配额——这也是代理驱动评估应该为自己配置的。`kubectl` 和 `minikube` 是单个静态二进制文件，无需 root，因此非 root CI 容器可以自行安装它们。

两个先决条件使渲染的 Job 处于 `Pending` 状态，第一个掩盖了第二个：模板挂载的 PVC 必须存在（`persistentvolumeclaim "<name>" not found` 在任何 GPU 抱怨之前触发），然后一个请求在无 GPU 集群上 `nvidia.com/gpu` 报告 `Insufficient nvidia.com/gpu` 并永远等待。渲染 `NUM_GPUS=0` 用于生命周期仅运行，并说明 GPU 调度未验证；在 Linux GPU 主机上，`minikube start --driver=docker --gpus all` 将真实 GPU 传递过去，因此一个 GPU 盒子足以进行 GPU 真实的冒烟测试。

安装命令、驱动程序选择、容器/主机网络注意事项以及伪造设备插件中间选项：`references/local-cluster.md`。

## 容器 Shell

简单的单节点模板通过 `/bin/sh -c`（POSIX sh，存在于 busybox/distroless 以及 TAO 镜像中）调用其命令。对于生产者动作请求，args 模式命令及其参数是原生容器 argv；需要 shell 的生产者明确声明 shell 及其脚本。简单的 config 模式命令在 `{config_path}` 被替换后也变为原生 argv。生产者拥有的 config 命令本身是一个多行 shell 脚本，则保留为 `/bin/sh -c` 下面的原样；渲染器永远不会从配置值构建 shell 文本。

## GPU Operator 依赖

`submit` 语句拒绝在没有可分配 `nvidia.com/gpu` 的集群上启动 GPU 作业。对于自管理集群，首先在每个 GPU 工作节点上运行 `tao-setup-nvidia-gpu-host` 安装动作，或在节点镜像中烘焙相同的软件包集：

```bash
bash skills/platform/tao-setup-nvidia-gpu-host/scripts/setup-nvidia-gpu-host.sh --backend kubernetes --install --yes
```

然后安装 NVIDIA GPU Operator 或设备插件：

```bash
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update
helm install --wait gpu-operator -n gpu-operator --create-namespace nvidia/gpu-operator
```

完整指南：https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/getting-started.html

## 多节点训练（分布式）

设置 `num_nodes > 1`（见上文 [多节点（节点 > 1）](#multi-node-nodes--1) 动词步骤）以在 N 个 Pod 之间运行分布式训练。渲染 `templates/k8s/indexed-job.yaml.tmpl` 提供了：

1. 一个以作业命名的 **无头服务**（选择器：`job-name=<job-name>`，`clusterIP: None`，`publishNotReadyAddresses: true` 以便 Pod 在全部 Ready 之前可以会晤）。
2. 一个 `parallelism = completions = num_nodes`、`completionMode: Indexed` 的 **Indexed Job**。每个 Pod 都会自动注入 `JOB_COMPLETION_INDEX`（= 节点排名）。
3. 一个 **命令包装器**，在调用用户命令之前导出会晤环境变量。同时导出两种命名约定：

   | 环境变量 | 值 | 读取 |
   |---|---|---|
   | `WORLD_SIZE` | `num_nodes` | TAO PyTorch 容器的 `nvidia_tao_pytorch/core/entrypoint.py`（使用此表示 *节点数量*，尽管 PyTorch 自己的约定是 *总进程数*） |
   | `NUM_GPU_PER_NODE` | `gpu_count` | TAO PyTorch 容器的入口点 |
   | `NNODES` | `num_nodes` | `torchrun` 和 PyTorch 标准会晤 |
   | `NPROC_PER_NODE` | `gpu_count` | `torchrun` |
   | `NODE_RANK` | `$JOB_COMPLETION_INDEX` | 两者 |
   | `MASTER_ADDR` | `<job-name>-0.<job-name>`（Pod-0 的 DNS） | 两者 |
   | `MASTER_PORT` | `29500` | 两者（TAO 的默认值） |

   两种命名约定都设置，以便 TAO 入口点（`dino train` 等）和原始 `torchrun` 命令无需修改即可工作。

对于 TAO 入口点，容器读取 `spec.train.num_nodes` 和连接的环境变量——例如 `dino train -e /tmp/spec.yaml`，`gpu_count=8`，`num_nodes=4`（4 × 8 = 32 个 GPU 总计）。

对于基于原始 `torchrun` 的命令（非 TAO 容器），包装器调用：

```bash
torchrun --nnodes=$NNODES --nproc-per-node=$NPROC_PER_NODE --node-rank=$NODE_RANK \
  --master-addr=$MASTER_ADDR --master-port=$MASTER_PORT train.py
```

容量检查跨节点求和：`gpu_count × num_nodes` ≤ 集群的 `nvidia.com/gpu` 可分配量。

### 多节点所需的集群要求

- **k8s 1.28+** 对于 Indexed Job 中稳定的 Pod 主机名（`PodIndexLabel` 功能）是必需的。在旧集群上 `MASTER_ADDR=<job>-0.<svc>` DNS 查找失败。使用 `kubectl version` 验证。
- **Pod 间网络** 必须在端口 29500（PyTorch 默认；可通过 `MASTER_PORT` 环境变量配置）上开放。大多数 CNIs（Calico、Cilium、AWS VPC CNI）默认允许此操作；严格的 NetworkPolicies 必须放宽。
- 容器中的 **NCCL** 在 GPU 间通信；如果集群有多 NIC 节点或 RDMA，请在渲染的清单的容器 `env` 中设置 `NCCL_SOCKET_IFNAME` / `NCCL_IB_HCA`。

### 参考资料

- Kubernetes Indexed Job：<https://kubernetes.io/docs/concepts/workloads/controllers/job/#completion-mode>
- Indexed Job 用于批量 ML：<https://kubernetes.io/blog/2022/06/01/indexed-jobs-mpi/>
- PyTorch 分布式（环境变量会晤）：<https://pytorch.org/docs/stable/elastic/run.html>
- NCCL 网络调优（NCCL_SOCKET_IFNAME、NCCL_IB_HCA）：<https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html>

### Kubernetes Operator 替代方案

对于更复杂的拓扑（组调度、PyTorch 弹性/容错训练、MPI / Horovod、RDMA 设置），选择 Operator 而不是纯 Indexed Job：

- **MPI Operator** — <https://github.com/kubeflow/mpi-operator> — 用于 MPI / Horovod 工作负载。
- **Kubeflow Training Operator** (`PyTorchJob`, `TFJob`) — <https://www.kubeflow.org/docs/components/training/> — 用于具有内置重启逻辑的弹性 PyTorch 训练。
- **Volcano** — <https://volcano.sh/> — 集群调度、队列、公平份额。在共享的多租户集群中很有用。
- **Kueue** — <https://kueue.sigs.k8s.io/> — 任何上述任一系统之上的配额/队列层。

此技能的 Indexed Job 路径故意保持简单且无依赖性；如果您需要弹性重启或集群调度，请在这些之上添加一层，并通过操作员的 CRD 提交作业。

## 常见错误模式

**`No nvidia.com/gpu resources allocatable on the cluster`** — GPU Operator（或 NVIDIA Device Plugin）未安装。按照上述链接进行安装；使用 `kubectl get nodes -o jsonpath='{.items[*].status.allocatable}'` 进行验证。

**`ImagePullBackOff` / `ErrImagePull`** — 集群无法拉取镜像。对于 nvcr.io：在命名空间中预先创建一个 image-pull secret，并在渲染的清单中将它作为 pod 的 `imagePullSecrets` 进行引用：
将密钥通过标准输入传递 — `--docker-password=$NGC_KEY` 会将密钥放入
argv 中，它在主机进程表和 shell 历史记录中可见：
```bash
set -a; source /path/to/.env; set +a   # 如果已经导出则省略
kubectl create secret generic ngc-pull-secret -n tao-jobs \
  --type=kubernetes.io/dockerconfigjson \
  --from-file=.dockerconfigjson=/dev/stdin <<EOF
{"auths": {"nvcr.io": {"username": "\$oauthtoken", "password": "${NGC_KEY}"}}}
EOF
# 验证而不读取密钥：
kubectl get secret ngc-pull-secret -n tao-jobs >/dev/null && echo SECRET_OK
```

**Pod 永久处于 `Pending` 状态** — `kubectl describe pod -l job-name=$JOB_ID` 在 `Events` 中显示调度原因。常见原因：GPU 容量不足 (`Insufficient nvidia.com/gpu`)、没有与 pod 的 `nodeSelector` 匹配的节点、缺少 image-pull secret 或 PVC 挂载失败。

**`OOMKilled` (退出码 137)** — 容器超出内存。减小批处理大小、降低 max_length 或添加内存请求/限制，并选择更大的节点。

**`CredentialError: Could not authenticate to a Kubernetes cluster`** — kubeconfig 或集群内认证均未成功。运行 `kubectl get nodes` 验证您的配置，或将 `$KUBECONFIG` 设置为正确的路径。

## 此技能尚不支持的功能 (目前)

- **弹性 / 容错训练。** Indexed Job 的 `backoff_limit=0` — 失败会导致整个训练运行失败。对于弹性重启（例如，在节点故障后从检查点恢复），请改用 Kubeflow 的 `PyTorchJob` 操作员。
- **集群调度。** Indexed Job 的 pod 独立调度 — 没有全有或全无。如果只有部分 pod 可以调度，多节点训练将 *部分* 开始（rank-0 会等待同伴而挂起）。对于共享集群的全有或全无调度，请使用 Volcano 或 Kueue。
- **MPI / Horovod。** 使用 MPI Operator。此处的 Indexed Job 路径是 PyTorch-distributed 形式的（环境变量在 `MASTER_ADDR:MASTER_PORT` 上进行汇合）。
- **从 `$NGC_KEY` 自动创建 image-pull secrets。** 您需要在目标命名空间中预先创建 secret 并传递名称。K8s 命名空间规范差异很大，因此我们保持 secret 创建的显式性。
