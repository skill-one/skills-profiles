---
name: launch-nemo-rl
description: 用于通过 nrl-k8s CLI 在 Kubernetes 集群上启动、监控、停止和调试 NeMo-RL 方案的手册。涵盖临时与持久 RayCluster 模式、迭代运行以及调试卡住或失败的训练作业。
---

# launch-nemo-rl — 通过 nrl-k8s 在 Kubernetes 上运行 NeMo-RL 配方

这是位于 `infra/nrl_k8s/` 的 `nrl-k8s` CLI 的操作手册。当用户需要在 Kubernetes 集群上启动/迭代/调试 NeMo-RL 配方时，请遵循此手册。在采取行动之前，请验证当前状态（`kubectl`、`git log`、配方+基础设施文件）——集群是共享的，错误操作的代价很高。

## 1. 一个命令，两种模式

有一个顶级提交命令：**`nrl-k8s run`**。它有两种生命周期模式。

| 模式               | 调用方式        | 使用场景                                                                                                   | 集群之后？ |
| :----------------- | :-------------- | :------------------------------------------------------------------------------------------------------- | :--------- |
| 临时（默认）       | `nrl-k8s run`             | 一次性。KubeRay 应用 RayJob，运行，然后销毁集群。适用于大多数运行。                                      | 否（自动） |
| 长生命             | `nrl-k8s run --raycluster` | 开发循环。重用匹配的实时集群，如果不存在则应用，如果发生漂移则警告+重用（传递 `--recreate` 以替换）。然后提交守护进程和训练。迭代的首选。 | 是         |

询问：*我运行后需要这个集群吗？* 如果需要，请使用 `--raycluster`。否则使用默认值（临时）。

CLI 的其余部分是可观察性/分阶段控制：

| 命令                 | 目的                                                                                              |
| :------------------- | :----------------------------------------------------------------------------------------------- |
| `nrl-k8s check`       | 验证配方+基础设施对；可选地写入完全解析的清单（`-o`）。                                             |
| `nrl-k8s status`      | 每个角色的 RayCluster 状态，头 pod 阶段，工作 pod 阶段，守护进程作业状态。                               |
| `nrl-k8s cluster up/down/list/dashboard` | 独立于运行管理 RayClusters（例如，使用 `--dry-run` 渲染清单）。                               |
| `nrl-k8s job list/logs/stop` | 对已提交到角色集群的 Ray Jobs 进行可观察性。                                                     |
| `nrl-k8s logs`        | 无需提交 ID 即可尾随角色的 pod / 守护进程日志。                                                   |

## 2. 配方+基础设施对

每次启动都需要两个文件。使用 `--infra` 传递基础设施，而不是内联合并：

```
nrl-k8s run infra/nrl_k8s/examples/<recipe>.yaml \
  --infra infra/nrl_k8s/examples/<recipe>.<profile>.infra.yaml
```

- **配方**（例如 `qwen3_30b_math_8n_4gpu.yaml`）— NeMo-RL 配置：模型，GRPO/SFT 开关，`cluster.{gpus_per_node,num_nodes}`。使用 `defaults:` 从 `examples/configs/recipes/llm/...` 继承。
- **基础设施**（例如 `*.<profile>.infra.yaml`）— K8s/Ray 结构：命名空间，镜像，服务账户，`kuberay:` 下 RayCluster 规范，可选 `deployments:` 下 Deployments，`submit.submitter`，`launch.{mode,codeSource,codePath,entrypoint}`。对名称遵循 `<recipe>.<profile>[.prod].infra.yaml`，其中 `<profile>` 指定硬件目标（例如 `gb300`）。

示例对位于 `infra/nrl_k8s/examples/` — 阅读相邻文件以了解目标配置文件当前的标准。

## 3. 长生命模式标志

三个独立维度。`--mode` 是一个宏，它选择默认值；单独的标志可以覆盖它。

```
--mode interactive   → --submitter portForward  --code-source upload  (尾随日志)
--mode batch         → --submitter exec         --code-source image   (nohup 后返回)
```

- **提交者**：`portForward` 使用 `kubectl port-forward` + Ray Job SDK（获得 `submission_id`，仪表板跟踪）。`exec` 使用 `kubectl exec` + `nohup` 在头 pod 上（没有提交 ID；驱动程序在仪表板中显示为 `type=DRIVER`）。
- **代码源**：`upload` 从笔记本电脑的阶段一个工作目录（Ray 100 MiB 限制）。`image` / `lustre` 期望代码在 pod 的文件系统上——与 `--code-path`（通常为 `/opt/nemo-rl`）配对，它是标准基础设施示例中共享文件系统 PVC 挂载的子路径。
- **等待**：`--wait` 尾随日志直到终端；`--no-wait` 一旦驱动程序运行就返回。

其他仅限长生命周期的标志：

- `--replace` — 在提交新作业之前停止任何正在运行的训练 / 守护进程作业（将守护进程提交 ID 后缀为时间戳，以便 Ray 接受重新提交）。
- `--recreate` — 删除并重新应用 RayCluster，其实时规范已从渲染的清单中漂移（默认是警告+重用）。
- `--skip-daemons` — 启动所有声明的集群，但仅提交训练。在 gym/generation 已经健康的解耦合配方上使用。

注意：在基础设施中，如果入口点执行 `cd /opt/nemo-rl`（或另一个镜像内 / Lustre 路径）并从那里加载配方，**`--code-source upload` 不会覆盖 pod 上的配方**——上传的工作目录位于 `/tmp/ray/...`，但入口点 `cd` 到其他地方。要实际测试本地配方更改，请将您的编辑同步到挂载到 pod 的共享文件系统，或在入口点中切换 Hydra 覆盖。

## 4. 临时模式标志（`--rayjob`）

当 `--rayjob` 设置时，`run` 分支到 RayJob 代码路径。相关标志：

- `--rayjob-name NAME` — RayJob 元数据名称（默认为训练集群名称）。
- `--shutdown / --no-shutdown` — 默认 `true`：KubeRay 在 Ray Job 达到终端状态后删除 RayCluster。
- `--ttl SECONDS` — 默认 3600s：运行完成后保留 RayJob 对象一段时间，以便进行事后分析日志访问。
- `--wait / --no-wait` — 默认 `wait`：轮询 `jobDeploymentStatus` 直到 Complete/Failed。`--no-wait` 一旦 RayJob 应用就返回。
- `--timeout SECONDS` — 默认 86400s（24h）：限制 `--wait` 轮询。
- `--dry-run` — 渲染 RayJob 清单并打印它；不应用。

`--replace` / `--recreate` / `--skip-daemons` 在 `--rayjob` 模式下被静默忽略（KubeRay 拥有生命周期）。

## 5. 不触摸共享文件系统的情况下迭代配置

当 pod 文件系统上的配方对您的实验具有错误值时，使用入口点上的 Hydra 覆盖而不是分支配方。模式：

```yaml
entrypoint: |
  set -eu
  cd /opt/nemo-rl
  RUN_ID="\${RAY_JOB_SUBMISSION_ID:-\${NRL_K8S_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)}}"
  python -u examples/run_grpo.py \
    --config infra/nrl_k8s/examples/<recipe>.yaml \
    logger.wandb_enabled=true \
    logger.wandb.project=<project> \
    "logger.wandb.name=<run-name>-\${RUN_ID}"
```

**转义 `${…}`** 使用反斜杠。OmegaConf 否则将其解释为插值，并在 shell 风格的 `${VAR:-default}` 上出错。`RUN_ID` 解析为 `RAY_JOB_SUBMISSION_ID`（由 KubeRay 在 rayjob 模式中注入）→ `NRL_K8S_RUN_ID`（由 CLI 在长生命周期模式中注入）→ 本地时间戳——因此名称在两种路径上是唯一的。

## 6. 每个配置文件的问题（硬件+调度器+DRA）

每个基础设施 YAML 都编码了一个硬件/调度器配置文件。`infra/nrl_k8s/examples/` 中的具体示例是它们目标的权威配置文件——在编写新文件之前，请阅读相邻的基础设施文件。通常变化的事项：

- **每个节点的 GPU**（例如 4 vs 8）— 必须与配方中的 `cluster.gpus_per_node` 匹配，否则工作节点保持 `Pending`。
- **节点选择器** — 头 pod 通常落在仅 CPU 的节点池上；GPU 工作节点匹配 `nvidia.com/gpu.product` 或节点组标签。
- **调度器** — KAI（`schedulerName: kai-scheduler` + `kai.scheduler/queue` 标签）使用拓扑注解（`kai.scheduler/topology`，`kai.scheduler/topology-required-placement`）将工作节点成群地调度到一个 clique 中。没有它，pod 可能落在不同的机架上，NVLink/RoCE 不会跨越它们。
- **DRA 声明** — ComputeDomain + RoCE 通过引用 `ResourceClaimTemplate` 的 `resourceClaims` 进行连接。CLI 在工作 pod 规范包含 DRA 声明引用时自动创建/删除这些——无需手动设置。
- **密钥** — 总是使用 `secretKeyRef`（`wandb-api-key`，镜像拉取密钥）。永远不要嵌入。
- **共享文件系统挂载** — 通常挂载两次 Lustre PVC：一次在代码路径（例如 `/opt/nemo-rl` 使用用户范围的 `subPath`），一次在工作区根（例如 `/mnt/rl-workspace`）用于数据集、HF 缓存和检查点。

在应用基础设施之前，请验证目标命名空间中是否存在先决条件：

```bash
kubectl get pvc <workspace-pvc>
kubectl get secret <wandb-secret> <image-pull-secret>
kubectl get sa <service-account>
```

## 7. 端到端工作流

### 7a. 新鲜的一次性运行（rayjob）
```bash
# 从 NeMo-RL 仓库根目录：
nrl-k8s check <recipe> --infra <infra>                               # 首先验证
nrl-k8s run <recipe> --infra <infra> --rayjob --dry-run              # 渲染 RayJob 清单
nrl-k8s run <recipe> --infra <infra> --rayjob --no-wait              # 应用，快速返回
```

观察状态+拆除（即使您的笔记本电脑断开连接，它也有效，因为 KubeRay 拥有生命周期）：
```bash
kubectl get rayjob -n default <name> -w
kubectl get raycluster -n default                                    # 空表示拆除成功
```

### 7b. 开发循环（长生命）
```bash
nrl-k8s run <recipe> --infra <infra> --run-id $(date +%Y%m%d-%H%M%S)
# 配方中的编辑？只需重新运行——重用实时集群。
# Pod 规范更改？添加 --recreate 以删除+重新应用。
# 解耦合配方中 gym/gen 已经健康？--skip-daemons。
```

### 7c. 首次解耦合启动
```bash
nrl-k8s run <recipe> --infra <disagg-infra> --mode batch --code-source image
```

### 7d. 集群生命周期管理
```bash
nrl-k8s cluster up   <recipe> --infra <infra> --target kuberay.training --wait
nrl-k8s cluster up   <recipe> --infra <infra> --target kuberay.training --dry-run   # 渲染清单
nrl-k8s cluster down <recipe> --infra <infra> --target kuberay.training --wait
nrl-k8s cluster down <recipe> --infra <infra>                                       # 销毁所有
nrl-k8s cluster list -n default
nrl-k8s cluster dashboard <cluster-name>                                  # port-forward + 浏览器
```

### 7e. 部署（例如 nemo-skills 沙盒）
```bash
# 仅启动部署
nrl-k8s cluster up <recipe> --infra <infra> --target deployments.nemo_skills
# 仅拆除部署
nrl-k8s cluster down <recipe> --infra <infra> --target deployments.nemo_skills
# 拆除所有（RayClusters + Deployments）
nrl-k8s cluster down <recipe> --infra <infra>
```

infra YAML 中的 `deployments:` 部分声明了与 RayClusters 一起管理的 Kubernetes Deployments。CLI 从顶级基础设施键中修补图像、`imagePullSecrets` 和 `serviceAccountName`（与 RayClusters 相同）。部署与集群启动并行启动——没有顺序依赖。

## 8. 监控运行

```bash
# 状态
nrl-k8s status <recipe> --infra <infra>
kubectl get rayjob,raycluster -n default

# 跟随驱动程序
nrl-k8s job list <recipe> --infra <infra> --role training
nrl-k8s job logs <run-id> <recipe> --infra <infra> --role training -f
```

当 `nrl-k8s job logs -f` 子进程死亡（`kubectl port-forward` i/o 超时约 15 分钟空闲）时，只需重新运行它。训练作业继续进行。

要获取终端作业（SUCCEEDED/FAILED）或通过仪表板 API 获取 RayJob 的驱动程序日志：
```bash
RC=$(kubectl get rayjob -n default <rayjob-name> -o jsonpath='{.status.rayClusterName}')
kubectl port-forward -n default svc/${RC}-head-svc 18266:8265 &
curl -s http://localhost:18266/api/jobs/                              # 列出作业，找到 submission_id
curl -s "http://localhost:18266/api/jobs/<submission_id>/logs"        # 完整驱动程序日志
```

`type=DRIVER` 与 `submission_id=null` 意味着 exec 提交运行（没有仪表板日志端点——使用 `nrl-k8s job logs`）。`type=SUBMISSION` 设置 `submission_id` 并工作 `/api/jobs/<id>/logs`。

Wandb URL 出现在驱动程序日志中的第一次 `wandb.init` 调用；grep `grep -oE 'https://wandb\.ai/[A-Za-z0-9_./-]+'`。

## 9. 停止操作

| 要停止的                   | 命令                                                                          |
| :------------------------ | :----------------------------------------------------------------------------- |
| 单个训练运行               | `nrl-k8s job stop <run-id> <recipe> --infra <infra> --role training`             |
| 一个集群上所有运行的 Ray 作业（+ 提交新作业） | `nrl-k8s run <recipe> --infra <infra> --replace`                         |
| 一个长生命 RayCluster      | `nrl-k8s cluster down <recipe> --infra <infra> --target kuberay.training --wait` |
| 一个 RayJob（临时）         | `kubectl delete rayjob <name> -n default` — 仅当 `shutdownAfterJobFinishes` 没有触发 |

在删除共享基础设施之前确认。`cluster down` 在其他人集群上的代价很高。

## 10. 验证 RayJob 拆除

在 `run --rayjob` 以 `--shutdown`（默认）完成时，KubeRay 应该删除 RayCluster：

```bash
kubectl get rayjob   -n default <rayjob-name>                        # jobDeploymentStatus = Complete
kubectl get raycluster -n default | grep <rayjob-name>               # 无输出 = 已拆除
```

RayJob 对象本身在 `--ttl` 秒内保留（默认 3600s），因此您仍然可以获取日志。

## 11. 常见陷阱

- **OmegaConf 插值** 在配方/基础设施 YAML 中消耗 `${VAR}`。使用 `\${VAR}` 转义 shell 变量，以便 OmegaConf 将它们原封不动地传递给 pod shell。
- **Megatron 优化器配置** 不携带 `foreach` / `fused`。覆盖，如 `~policy.optimizer.kwargs.foreach ~policy.optimizer.kwargs.fused`（对于 DTensor 配置有效），在 Megatron 配方上中断。为 Megatron 删除它们。
- **DTensor vs Megatron** — MoE 配方通常使用 `megatron_cfg.enabled=true`；确保 `dtensor_cfg.enabled=false` 在继承的默认值中。
- **共享文件系统 vs git 分歧** — `codeSource: image|lustre` 从 pod 文件系统读取。如果您的本地编辑不在 pod 挂载的共享文件系统中，运行测试的是磁盘版本，而不是您的版本。要么通过辅助 pod 同步（头 pod exec 通常被阻塞），要么通过 Hydra 标志覆盖。
- **临时存储 + readinessProbe** 由 kuberay/CDI webhooks 在 pod 应用时注入。不要将它们添加到内联 RayCluster 规范中。
- **节点污点** 因集群而异。`tolerations: [{operator: Exists}]` 在工作节点上是防御性的，值得保留。
- **仪表板空白页面** — Ray 2.52 默认将仪表板资产安装为符号链接；`nrl-k8s cluster dashboard <name>` 自动重新安装 `ray[default] --link-mode=copy` 来修复它。在图像中烘焙 `ENV UV_LINK_MODE=copy` 以避免这种情况。
- **`kubectl exec` 通常被阻塞** 在自动化中——使用 `kubectl get ... -o yaml`，`kubectl logs`，`kubectl port-forward` + Ray 仪表板 API 绕过。

## 12. 将运行称为“完成”之前的检查清单

在报告启动成功之前，请验证：

1. `kubectl get rayjob/raycluster -n default` 显示预期的对象。
2. `nrl-k8s job list`（或 `curl /api/jobs/`）显示作业处于 `RUNNING` / `SUCCEEDED` 状态。
3. 驱动程序日志包含 `wandb.ai/<project>/runs/<id>`（如果启用了 wandb）——与用户分享 URL。
4. 至少出现一行 `Processed prompts: 100%`（确认生成已连接）。
5. 对于 `--rayjob` 模式仅：在 `jobDeploymentStatus=Complete` 之后，确认 `kubectl get raycluster | grep <name>` 为空（拆除工作正常）。

## 13. 开发 pod

`nrl-k8s dev` 管理集群上的一个轻量级 CPU pod，用于代码同步、调试以及从集群内部运行 `kubectl`/`nrl-k8s`。

```bash
# 一次性操作：配置密钥（HF 令牌、wandb、SSH 密钥、rclone）
nrl-k8s dev setup-secrets --ssh-key ~/.ssh/id_rsa --add-rclone

# 创建 Pod 并进入执行（幂等操作——复用现有 Pod）
nrl-k8s dev connect

# 切换镜像（必须先停止——镜像变更会有警告，但不会自动应用）
nrl-k8s dev stop
nrl-k8s dev connect --image nvcr.io/nvidian/nemo-rl:v0.7.0

# 拆除
nrl-k8s dev stop
```

开发 Pod 的说明：
- 运行在仅限 CPU 的节点上（与 GPU 节点具有反亲和性）
- 将共享的 `rl-workspace` PVC 挂载到 `/mnt/rl-workspace`
- 将 `USER` 环境变量设置为 `nrl-k8s` 用户名（因此即使以 root 用户运行，`$USER` 和 `getpass.getuser()` 也能正常工作）
- 在首次启动时安装 `kubectl`、`rclone`（如果已配置）
- 通过用户专属的 K8s Secret，使用 `envFrom` 注入 SSH 密钥和令牌

Pod 的 `default` 服务账户需要在命名空间中具有 `edit` RoleBinding，`kubectl` 才能在内部正常工作。如果缺失，`dev connect` 会检查此项并打印所需的 YAML。

## 14. 仓库中的代码位置

- CLI 代码：`infra/nrl_k8s/src/nrl_k8s/`（`cli.py`、`orchestrate.py`、`manifest.py`、`rayjob.py`、`k8s.py`、`submitters/`、`schema.py`）。
- 测试：`infra/nrl_k8s/tests/unit/`——在 `infra/nrl_k8s/` 目录下使用 `uv run --extra test pytest -x -q` 运行。
- 配方和基础设施示例：`infra/nrl_k8s/examples/`。
- 此工具封装的基础配方：`examples/configs/recipes/llm/…` 和 `examples/nemo_gym/…`。
