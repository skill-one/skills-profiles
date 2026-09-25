# Kubernetes

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

将 TAO 容器作业作为 Kubernetes Jobs 提交。适用于任何可通过 kubeconfig 访问的集群（EKS / GKE / AKS / 本地）或在集群内服务账户（在 Pod 内运行时）。

默认单节点；通过 `num_nodes > 1` 选择多节点分布式训练（使用 Indexed Job + 无头服务，见下文 [多节点分布式训练](#multi-node-training-distributed)）。

## 预检

三个检查：GPU 主机运行时准备就绪、可通过 `kubectl` 访问集群、GPU Operator/设备插件存在。

```bash
# 0. GPU 节点主机运行时。
# 在每个自管理的 GPU 工作节点上运行此命令或在节点镜像构建中运行。
# 仅在使用的托管 GPU 节点（其驱动程序/工具包生命周期由云提供商或 GPU Operator 策略拥有）时才设置 TAO_K8S_SKIP_NODE_RUNTIME_CHECK=1。
if [ "${TAO_K8S_SKIP_NODE_RUNTIME_CHECK:-0}" != "1" ]; then
  TAO_SKILL_BANK_ROOT="${TAO_SKILL_BANK_ROOT:-$PWD}"
  SETUP_SCRIPT="${TAO_SKILL_BANK_ROOT}/skills/platform/tao-setup-nvidia-gpu-host/scripts/setup-nvidia-gpu-host.sh"

  bash "$SETUP_SCRIPT" --backend kubernetes --check-only || {
    echo "缺失：TAO Kubernetes GPU 节点运行时未就绪。"
    echo "对于自管理的 GPU 节点，在用户批准后运行："
    echo "  bash \"$SETUP_SCRIPT\" --backend kubernetes --install --yes"
    echo "对于托管集群，验证节点镜像/GPU Operator 策略安装了驱动 580 和工具包 1.19.0，然后设置 TAO_K8S_SKIP_NODE_RUNTIME_CHECK=1。"
    exit 1
  }
fi

# 1. 集群可访问（kubeconfig 或集群内服务账户）
command -v kubectl >/dev/null 2>&1 || {
  echo "缺失：kubectl 未在 PATH 中找到。安装 kubectl 以提交 Jobs。"
  exit 1
}
kubectl cluster-info >/dev/null 2>&1 || {
  echo "缺失：无可访问的集群（kubeconfig 在 ~/.kube/config、\$KUBECONFIG 或 Pod 内服务账户）。"
  echo "为您的集群配置 kubectl，或设置 \$KUBECONFIG："
  echo "  EKS: aws eks update-kubeconfig --name <集群> --region <区域>"
  echo "  GKE: gcloud container clusters get-credentials <集群> --region <区域>"
  echo "  AKS: az aks get-credentials --resource-group <rg> --name <集群>"
  echo "  本地: minikube start   (见下文 '本地集群')"
  exit 1
}

# 2. NVIDIA GPU Operator 存在（软检查——警告，不失败）
gpu=$(kubectl get nodes -o jsonpath='{range .items[*]}{.status.allocatable.nvidia\.com/gpu}{"\n"}{end}' 2>/dev/null | grep -v '^$' | head -1)
if [ -z "$gpu" ] || [ "$gpu" = "0" ]; then
  echo "警告：此集群上没有可分配的 nvidia.com/gpu。"
  echo "在提交 GPU 作业前安装 NVIDIA GPU Operator："
  echo "  https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/getting-started.html"
fi
```

GPU 节点运行时检查对于自管理节点是必需的。对于客户端不在 GPU 工作节点上的托管集群，请验证提供商节点镜像或 GPU Operator 策略，并设置 `TAO_K8S_SKIP_NODE_RUNTIME_CHECK=1` 而不是在客户端运行安装程序。这里的 GPU 容量警告是软检查；`submit` 语句会在应用清单前重新检查可分配的 `nvidia.com/gpu` 并硬失败（没有 gang scheduling，因此太大的 Job 会永远处于 `Pending` 状态）。

## 凭证与配置

- **Kubeconfig**（之一）：
  - `~/.kube/config` — 默认发现路径
  - `$KUBECONFIG` — 替代路径
  - 集群内服务账户 — 在 Pod 内运行时使用（无需 kubeconfig）
- **TAO_K8S_NAMESPACE**（可选）：作业提交的默认命名空间。默认为 `default`。
- **TAO_K8S_CONTEXT**（可选）：切换集群的 kubeconfig 上下文名称。
- **NGC_KEY**（可选）：用于 nvcr.io 镜像拉取。如果您已在目标命名空间预创建了镜像拉取密钥，请在渲染的清单的 `imagePullSecrets` 中引用其名称。
- **AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / S3_BUCKET_NAME / S3_ENDPOINT_URL**（可选）：用于 S3 数据集 I/O（存储层 C），通过每个作业的 Secret (`envFrom.secretRef`) 注入 Pod，永不内联。遗留 `ACCESS_KEY`/`SECRET_KEY` 由 `tao-data-io` 映射。

对于 Kubernetes 运行，不要请求 Brev 或 SLURM 凭证。仅在选定的工作流使用 `s3://` 输入或输出时请求 S3 凭证，仅在选定的模型需要时请求特定于模型的凭证，例如 `HF_TOKEN`。在启动前，验证选定的命名空间可以创建 Jobs，数据集/结果路径从 Pod 中可见，PVC/挂载文件系统路径已证明已挂载到作业容器中；代理主机本地路径不足以证明。

## 执行——四个动词

`tao-run-on-kubernetes` 是一个平台 **消费者**：它通过 `kubectl` 运行 spec-bundle，仅修改作业记录。不需要 nvidia-tao-sdk，不需要 `tao_sdk` 导入——作业使用纯 `kubectl apply` 提交。
`$BANK` = `${TAO_SKILL_BANK_PATH}`。

### submit

1. **GPU 容量门禁——首先硬失败**（没有 gang scheduling → 太大的 Job 会永远处于 `Pending` 状态）：
   ```bash
   ALLOC=$(kubectl get nodes -o jsonpath='{range .items[*]}{.status.allocatable.nvidia\.com/gpu}{"\n"}{end}' | awk '{s+=$1} END{print s+0}')
   [ "${ALLOC:-0}" -ge "$NUM_GPUS" ] || { echo "GPU 不足：需要 $NUM_GPUS，可分配 $ALLOC"; exit 1; }
   ```
2. **存储层**（通过 `tao-data-io`）：**A** = 挂载包含数据的 bound PVC/NFS（授权挂载路径，不下载——空气间隙解决方案，且打包模板也这样做）；**C** = 临时：initContainer 从 S3 拉取到共享 `emptyDir`，最后一步在 TTL 到期前将结果上传到 S3。

   **层 C 在 GPU 下载时保留 GPU。** Pod 为其整个生命周期保留 `nvidia.com/gpu`（包括 initContainers），因此大型层 C 拉取——或首次 1GB+ 图像拉取——会计费并可能被 reaper 空闲 GPU 时间，就像在 SLURM 分配内拉取一样。当数据已经在 PVC 上时，请选择层 A；知情地选择层 C，用于小输入。

   生产者动作请求可以声明多个挂载，包括重复源别名用于逻辑和嵌入的绝对路径。阅读 `references/action-request.md` 并使用其暂存映射加上打包渲染器。对于 `mode=config`，首先生成生产者的嵌套 spec，暂存该确切生成的文件，并将其传回渲染器，以便 Pod 接收一个经过验证的只读配置挂载。遗留的单根模板无法表示该合同。
3. **打开记录——生成 ID，绑定 `results_dir`，在启动前：**
   ```bash
   JOB_ID=$("$BANK/scripts/tao_job_record.py" open --platform kubernetes --image "$IMAGE" \
     --network-arch "$ARCH" --action "$ACTION" --storage-tier "$TIER" --results-dir "$RESULTS_DIR")
   ```
   `results_dir` 必须是 **挂载的（持久的）卷路径或 S3 前缀**——`ttlSecondsAfterFinished` 在作业结束后删除作业及其日志，因此稍后无法从作业对象中恢复任何内容。
4. **渲染、门禁、应用，并记录 RUNNING。** 对于生产者动作请求，请遵循 `references/action-request.md`；它负责后端名称规范化、条件 Secret 引用、原生 argv 渲染、服务器干运行，并将应用对象名称绑定到作业记录。对于简单的单根 spec-bundle，渲染 `templates/k8s/single-pod-job.yaml.tmpl`，运行 `redact_secrets.py lint` 加上 `kubectl apply --dry-run=server`，应用它，并标记记录为 `backend-ref=<namespace>/<实际对象名称>`。

跳过门禁或打开的提交没有 ID——因此它无法启动。

### status

保留 `K8S_JOB_NAME` 从提交。在重新附加时，读取作业记录的 `backend_ref=<namespace>/<name>` 并从该字段恢复这两个值；不要假设 Kubernetes 名称等于记录 ID。

```bash
kubectl get job "$K8S_JOB_NAME" -n "$NAMESPACE" \
  -o jsonpath='{.status.conditions[0].type} {.status.active} {.status.succeeded} {.status.failed}'
```

| kubectl 信号 | 词汇 |
|---|---|
| 没有 Pod 被调度 | `PENDING` (`kubectl get pods -n "$NAMESPACE" -l job-name="$K8S_JOB_NAME"` → `ImagePullBackOff` / `Insufficient nvidia.com/gpu` 在 `message` 中) |
| `active` ≥ 1 | `RUNNING` |
| 条件 `Complete` | `COMPLETE` |
| 条件 `Failed` | `ERROR`（从 Pod 的终止原因分类——`OOMKilled` → `ERR_INFRA`) |
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

### Multi-node (nodes > 1)

相同的四个动词，加上：

1. **版本门禁：** 需要 k8s ≥ 1.28 (`kubectl version -o json`) — Pod 主机名 `<job>-<index>`（PodIndexLabel）`MASTER_ADDR=<job>-0.<svc>` 解析到的需要它；在旧集群上 rank-0 在会晤时挂起。
2. **容量门禁 × 节点：** 除非可分配的 GPU ≥ `gpus_per_node × nodes` 硬失败（没有 gang scheduling → 部分启动会留下 rank-0 等待永远）。
3. **渲染 `templates/k8s/indexed-job.yaml.tmpl`** — 无头服务 + Indexed Job + 会晤环境 (`WORLD_SIZE` = 节点数，`NODE_RANK` 来自 `JOB_COMPLETION_INDEX`，`MASTER_ADDR=<job>-0.<svc>`，`/dev/shm` 16Gi 以免 NCCL 悄无声息地挂起)。`kubectl apply -f` 一起创建服务和作业；`cancel` 删除作业（前台）和服务。
4. **NCCL 探测首先**（像 SLURM）——一个 2 节点 all-reduce 带超时；挂起时，设置集群 NCCL 环境并重新探测；缓存每个集群。

## 本地集群（开发、CI 和评估）

一个一次性 minikube/kind 集群练习准入、四个动词、作业记录接线、日志管道，而无需集群配额——并且是代理驱动评估应该为自己配置的。`kubectl` 和 `minikube` 是单个静态二进制文件，无需 root，因此非 root CI 容器可以自行安装它们。

两个先决条件使渲染的作业 `Pending`，并且第一个掩盖了第二个：模板挂载的 PVC 必须存在（`persistentvolumeclaim "<name>" not found` 在任何 GPU 抱怨之前触发），然后请求在无 GPU 集群上 `nvidia.com/gpu` 报告 `Insufficient nvidia.com/gpu` 并等待永远。渲染 `NUM_GPUS=0` 用于生命周期仅运行，并说明 GPU 调度未验证；在 Linux GPU 主机上，`minikube start --driver=docker --gpus all` 将真实 GPU 传递，因此一个 GPU 盒子足以用于 GPU 真实的烟雾测试。

安装命令、驱动程序选择、容器/主机网络注意事项以及伪造设备插件中间选项：`references/local-cluster.md`。

## 容器 Shell

简单的单节点模板通过 `/bin/sh -c` 调用其命令（POSIX sh，存在于 busybox/distroless 以及 TAO 镜像中）。对于生产者动作请求，args 模式命令及其参数是原生容器 argv；需要 shell 的生产者明确声明 shell 及其脚本。简单的 config 模式命令在 `{config_path}` 被替换后也变为原生 argv。生产者拥有的 config 命令本身是一个多行 shell 脚本，则保留为 `/bin/sh -c` 下；渲染器永远不会从 config 值构建 shell 文本。

## GPU Operator 依赖

`submit` 语句拒绝在没有可分配的 `nvidia.com/gpu` 的集群上启动 GPU 作业。对于自管理集群，首先在每个 GPU 工作节点上运行 `tao-setup-nvidia-gpu-host` 安装动作，或将要安装的相同软件包集烘焙到节点镜像中：

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

设置 `num_nodes > 1`（见上文 [多节点 (nodes > 1)](#multi-node-nodes--1) 语句步骤）以在 N 个 Pod 之间运行分布式训练。渲染 `templates/k8s/indexed-job.yaml.tmpl` 提供了：

1. 一个 **无头服务**，以作业命名（选择器：`job-name=<job-name>`，`clusterIP: None`，`publishNotReadyAddresses: true` 以便 Pod 在全部 Ready 之前可以会晤）。
2. 一个 **Indexed Job**，`parallelism = completions = num_nodes`，`completionMode: Indexed`。每个 Pod 都会自动注入 `JOB_COMPLETION_INDEX` 由 k8s（= 节点排名）。
3. 一个 **命令包装器**，在调用用户命令之前导出会晤环境变量。同时导出两种命名约定：

   | 环境变量 | 值 | 读取 |
   |---|---|---|
   | `WORLD_SIZE` | `num_nodes` | TAO PyTorch 容器的 `nvidia_tao_pytorch/core/entrypoint.py`（使用此表示 *节点数*，即使 PyTorch 自己的约定是 *总进程*） |
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

### 多节点集群要求

- **k8s 1.28+** 是为了在 Indexed Jobs 中稳定 Pod 主机名（`PodIndexLabel` 功能）所必需的。在旧集群上 `MASTER_ADDR=<job>-0.<svc>` DNS 查找失败。使用 `kubectl version` 验证。
- **Pod 间网络** 必须在端口 29500（PyTorch 默认；可通过 `MASTER_PORT` 环境变量配置）上开放。大多数 CNIs（Calico、Cilium、AWS VPC CNI）默认允许此操作；严格的 NetworkPolicies 必须放宽。
- **容器内的 NCCL** 通过 GPU 通信 GPU；如果集群有 multi-NIC 节点或 RDMA，请在容器的 `env` 中设置 `NCCL_SOCKET_IFNAME` / `NCCL_IB_HCA`。

### 参考阅读

- Kubernetes Indexed Job: <https://kubernetes.io/docs/concepts/workloads/controllers/job/#completion-mode>
- Indexed Job 用于批量 ML: <https://kubernetes.io/blog/2022/06/01/indexed-jobs-mpi/>
- PyTorch 分布式（环境变量会晤）：<https://pytorch.org/docs/stable/elastic/run.html>
- NCCL 网络调优（NCCL_SOCKET_IFNAME, NCCL_IB_HCA）：<https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html>

### Kubernetes operator 替代方案

对于更复杂的拓扑（gang scheduling、PyTorch 弹性 / 容错训练、MPI / Horovod、RDMA 设置），选择 operator 而不是纯 Indexed Job：

- **MPI Operator** — <https://github.com/kubeflow/mpi-operator> — 用于 MPI / Horovod 工作负载。
- **Kubeflow Training Operator** (`PyTorchJob`, `TFJob`) — <https://www.kubeflow.org/docs/components/training/> — 用于具有内置重启逻辑的弹性 PyTorch 训练。
- **Volcano** — <https://volcano.sh/> — gang scheduling、队列、公平份额。在共享多租户集群中很有用。
- **Kueue** — <https://kueue.sigs.k8s.io/> — 任何上述之上的配额/队列层。

此技能的 Indexed Job 路径有意简单且无依赖；如果您需要弹性重启或 gang scheduling，在顶部添加其中一个，并通过 operator 的 CRD 提交作业。

## 常见错误模式

**`集群上没有可分配的 nvidia.com/gpu 资源`** — GPU Operator（或 NVIDIA 设备插件）未安装。按照上面的链接安装；使用 `kubectl get nodes -o jsonpath='{.items[*].status.allocatable}'` 验证。

**`ImagePullBackOff` / `ErrImagePull`** — 集群无法拉取图像。对于 nvcr.io：在命名空间中预创建一个图像拉取密钥，并在渲染的清单中作为 Pod 的 `imagePullSecrets` 引用它：
将密钥通过 stdin 传递——`--docker-password=$NGC_KEY` 会将密钥放入 argv，它在主机进程表和 shell 历史记录中可见：
```bash
set -a; source /path/to/.env; set +a   # 如果已经导出则省略
kubectl create secret generic ngc-pull-secret -n tao-jobs \
  --type=kubernetes.io/dockerconfigjson \
  --from-file=.dockerconfigjson=/dev/stdin <<EOF
{"auths": {"nvcr.io": {"username": "\$oauthtoken", "password": "${NGC_KEY}"}}}
EOF
# 无需读取密钥即可验证：
kubectl get secret ngc-pull-secret -n tao-jobs >/dev/null && echo SECRET_OK
```

**Pod 永远处于 `Pending` 状态** — `kubectl describe pod -l job-name=$JOB_ID` 显示调度原因在 `Events` 中。常见原因：GPU 容量不足 (`Insufficient nvidia.com/gpu`)、没有节点匹配 Pod 的 `nodeSelector`、缺少图像拉取密钥或 PVC 挂载失败。

**`OOMKilled` (exit 137)** — 容器超出内存。减小批处理大小、降低 max_length 或添加内存请求/限制并目标更大的节点。

**`CredentialError: Could not authenticate to a Kubernetes cluster`** — kubeconfig 和集群内认证均未成功。运行 `kubectl get nodes` 验证您的配置，或设置 `$KUBECONFIG` 为正确的路径。

## 此技能尚不支持（未来）

- **弹性 / 容错训练。** Indexed Job 有 `backoff_limit=0` — 失败会导致整个训练运行失败。对于弹性重启（例如，在节点死亡后从检查点恢复），请使用 Kubeflow 的 `PyTorchJob` operator。
- **Gang scheduling。** Indexed Job Pods 独立调度——没有 all-or-nothing。如果只有一些 Pod 可以调度，多节点训练会 *部分* 启动（rank-0 将等待同伴）。对于共享集群上的 all-or-nothing 调度，请使用 Volcano 或 Kueue。
- **MPI / Horovod。** 使用 MPI Operator。此处的 Indexed Job 路径是 PyTorch 分布式形状（在 `MASTER_ADDR:MASTER_PORT` 上的环境变量会晤）。
- **从 `$NGC_KEY` 自动创建图像拉取密钥。** 您在目标命名空间中预创建密钥，并传递其名称。K8s 命名空间约定差异很大，因此我们保持密钥创建明确。
