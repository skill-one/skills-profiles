# GKE 批处理与 HPC 工作负载

本指南涵盖在 GKE 上运行批处理和高性能计算 (HPC) 工作负载。

> **MCP 工具:** `apply_k8s_manifest`, `get_k8s_resource`, `describe_k8s_resource`, `get_k8s_logs`, `delete_k8s_resource`, `list_k8s_events`

## 使用场景

- 运行批处理数据处理管道
- HPC 仿真（CFD、分子动力学、金融建模）
- 大规模并行计算（MPI、MapReduce）
- 机器学习训练作业
- CI/CD 构建农场

## GKE 上的批处理

### Kubernetes Jobs

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: batch-job
spec:
  parallelism: 10
  completions: 100
  backoffLimit: 3
  template:
    spec:
      containers:
      - name: worker
        image: <IMAGE>
        resources:
          requests:
            cpu: "1"
            memory: "2Gi"
      restartPolicy: Never
```

### JobSet（用于复杂的多作业工作流）

黄金路径启用 JobSet 监控（`JOBSET` 在监控配置中）。

```yaml
apiVersion: jobset.x-k8s.io/v1alpha2
kind: JobSet
metadata:
  name: training-job
spec:
  replicatedJobs:
  - name: workers
    replicas: 4
    template:
      spec:
        parallelism: 1
        completions: 1
        template:
          spec:
            containers:
            - name: worker
              image: <IMAGE>
              resources:
                requests:
                  cpu: "4"
                  memory: "8Gi"
```

### Kueue（作业队列）

Kueue 管理批处理工作负载的作业调度和资源分配：

```bash
# 安装 Kueue
kubectl apply --server-side -f https://github.com/kubernetes-sigs/kueue/releases/latest/download/manifests.yaml
```

```yaml
# 定义 ClusterQueue
apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
  name: batch-queue
spec:
  namespaceSelector: {}
  resourceGroups:
  - coveredResources: ["cpu", "memory"]
    flavors:
    - name: default
      resources:
      - name: "cpu"
        nominalQuota: 100
      - name: "memory"
        nominalQuota: "200Gi"
---
# 允许命名空间使用队列
apiVersion: kueue.x-k8s.io/v1beta1
kind: LocalQueue
metadata:
  name: batch-local
  namespace: batch-jobs
spec:
  clusterQueue: batch-queue
```

## GKE 上的 HPC

### Compact Placement（低延迟网络）

对于需要低延迟节点间通信的紧密耦合 HPC 工作负载：

```bash
# 标准集群：创建具有紧凑放置的节点池
gcloud container node-pools create hpc-pool \
  --cluster <CLUSTER_NAME> --region <REGION> \
  --machine-type c3-standard-44 \
  --placement-type COMPACT \
  --num-nodes 8 \
  --enable-autoscaling --min-nodes 0 --max-nodes 16 \
  --quiet
```

### MPI 工作负载

使用 MPI Operator 处理基于 MPI 的 HPC 应用程序：

```bash
# 安装 MPI Operator
kubectl apply -f https://raw.githubusercontent.com/kubeflow/mpi-operator/master/deploy/v2beta1/mpi-operator.yaml
```

```yaml
apiVersion: kubeflow.org/v2beta1
kind: MPIJob
metadata:
  name: hpc-simulation
spec:
  slotsPerWorker: 4
  mpiReplicaSpecs:
    Launcher:
      replicas: 1
      template:
        spec:
          containers:
          - name: launcher
            image: <MPI_IMAGE>
            command: ["mpirun", "-np", "32", "./simulation"]
            resources:
              requests:
                cpu: "1"
                memory: "2Gi"
              limits:
                cpu: "2"
                memory: "4Gi"
    Worker:
      replicas: 8
      template:
        spec:
          containers:
          - name: worker
            image: <MPI_IMAGE>
            resources:
              requests:
                cpu: "4"
                memory: "8Gi"
              limits:
                cpu: "8"
                memory: "16Gi"
```

## 批处理/HPC 成本优化

### 批处理 Spot VM

批处理工作负载是 Spot VM 的理想候选（可中断、可检查点）。
使用具有 Spot 优先级的 ComputeClass 并使用 `activeMigration` 在可用时返回到 Spot。有关 Spot-with-fallback 模式的详细信息，请参阅 `gke-compute-classes` 技能。

### Scale-to-Zero

对于批处理集群，允许节点池在没有作业运行时扩展到零：

- Autopilot（黄金路径）：自动，在没有 Pod 调度时节点扩展到零
- 标准：在批处理节点池上设置 `--min-nodes 0`

## 最佳实践与生产指南

- **资源配额**：始终为所有批处理/HPC 配置文件指定资源请求和限制（CPU、内存，以及可选 GPU/TPU）。这对于 Kueue 入口、自动扩展和防止集群资源饥饿至关重要。
- **TPU/Spot 集群维护**：对于在 Spot VM/TPU 上运行的长时间运行的 AI 训练，建议使用 **GKE 维护排除** 在活动训练窗口期间阻止自动集群升级/重启，以最大程度地减少不必要的抢占。
- **MPI 工作负载**：使用 **Kubeflow Training Operator** 通过 `MPIJob` 自定义资源编排分布式 MPI 应用程序。
- **Kueue & JobSet**：使用 **Kueue** 进行多租户作业队列和公平共享；使用 **JobSet** 进行多组件紧密耦合工作负载。
- **弹性**：始终为作业设置 `backoffLimit`，并实现应用程序级别的检查点（例如，使用 Orbax 或 PyTorch 检查点）以在 Spot VM 抢占时生存。
