# GKE 存储

本参考指南涵盖 GKE 集群的存储配置，包括持久磁盘、文件存储和云存储集成。

> **MCP 工具:** `apply_k8s_manifest`, `get_k8s_resource`, `describe_k8s_resource`, `get_cluster`

## 金路径存储默认配置

金路径 Autopilot 配置启用以下 CSI 驱动：

| 驱动          | 金路径       | 访问模式     | 用例             |
| --------------- | ----------------- | --------------- | -------------------- |
| Compute Engine  | 启用（默认） | ReadWriteOnce   | 块存储用于    |
: 持久磁盘 :                   :                 : 数据库，           :
: CSI             :                   :                 : 单 Pod 工作负载 :
| Google Cloud    | 启用           | ReadWriteMany   | 共享 NFS 用于       |
: 文件存储 CSI   :                   :                 : 多 Pod 访问     :
| Cloud Storage   | 启用           | ReadWriteMany / | 挂载 GCS 桶为     |
: FUSE CSI        :                   : ReadOnlyMany    | 卷              :
| Parallelstore   | 启用           | ReadWriteMany   | 高性能     |
: CSI             :                   :                 : 并行文件系统 :
| 启动磁盘类型  | `pd-balanced`     | N/A             | 节点启动磁盘      |

## StorageClasses

### 默认 StorageClasses

GKE 提供内置的 StorageClasses：

StorageClass   | 磁盘类型             | 用例
-------------- | --------------------- | ------------------------------
`standard-rwo` | `pd-standard`         | 高性价比，低 IOPS
`premium-rwo`  | `pd-ssd`              | 高 IOPS，数据库
`standard-rwx` | 文件存储（基础 HDD） | 共享 NFS
`premium-rwx`  | 文件存储（基础 SSD） | 共享 NFS，更高性能

### 自定义 StorageClass

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-regional
provisioner: pd.csi.storage.gke.io
parameters:
  type: pd-ssd
  replication-type: regional-pd    # 跨 2 个区域复制
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true         # 生产环境始终启用
```

## PersistentVolumeClaims

### 块存储（ReadWriteOnce）

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: database-pvc
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: premium-rwo
  resources:
    requests:
      storage: 100Gi
```

### 共享文件存储（通过文件存储的 ReadWriteMany）

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: shared-data
spec:
  accessModes:
  - ReadWriteMany
  storageClassName: standard-rwx
  resources:
    requests:
      storage: 1Ti    # 文件存储基础层最小为 1 TiB
```

### GCS 桶挂载（云存储 FUSE）

无需 PVC 即将 GCS 桶挂载为卷：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gcs-reader
  annotations:
    gke-gcsfuse/volumes: "true"
spec:
  containers:
  - name: reader
    image: busybox
    command: ["ls", "/data"]
    volumeMounts:
    - name: gcs-bucket
      mountPath: /data
  volumes:
  - name: gcs-bucket
    csi:
      driver: gcsfuse.csi.storage.gke.io
      readOnly: true
      volumeAttributes:
        bucketName: <BUCKET_NAME>
```

> 需要工作负载身份验证，以便 Pod 的服务账户对桶具有 `storage.objectViewer` 权限。

## 卷扩展

如果 StorageClass 上设置了 `allowVolumeExpansion: true`，则通过更新 PVC 来调整大小：

```bash
# kubectl
kubectl patch pvc <PVC_NAME> -p '{"spec":{"resources":{"requests":{"storage":"200Gi"}}}}'
```

```
# MCP（推荐）
patch_k8s_resource(parent="...", resourceType="persistentvolumeclaim", name="<PVC_NAME>",
  patch='{"spec":{"resources":{"requests":{"storage":"200Gi"}}}}')
```

Kubernetes 会自动调整文件系统大小。

## 最佳实践

1.  **始终启用卷扩展**：在所有 StorageClasses 上设置 `allowVolumeExpansion: true`
2.  **生产环境使用区域 PD**：`replication-type: regional-pd` 跨 2 个区域复制以实现高可用性
3.  **使用 `WaitForFirstConsumer`**：确保 PV 在与 Pod 相同的区域中配置
4.  **选择合适的磁盘类型**：`pd-ssd` 用于数据库，`pd-balanced`（金路径默认值）用于通用用途，`pd-standard` 用于冷存储
5.  **使用文件存储进行共享访问**：当多个 Pod 需要读写相同文件时
6.  **使用 GCS FUSE 进行数据管道**：直接挂载桶用于机器学习训练数据、日志等
7.  **备份 PVC**：使用 GKE 备份（参见 `gke-backup-dr` 技能）来保护持久数据
