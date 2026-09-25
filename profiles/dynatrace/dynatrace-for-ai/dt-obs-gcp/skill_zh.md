# GCP 云基础设施

使用 Dynatrace Smartscape 和 DQL 监控和分析 GCP 资源。查询 GCP 服务，管理组织架构，审计安全态势，并跟踪 GCP 基础设施中的资源所有权。

## 何时使用此技能

当用户需要在 Dynatrace 中处理 GCP 资源时，请使用此技能。加载任务类型的参考文件：

| 任务 | 要加载的文件 |
|---|---|
| 库存和拓扑查询 | （无需加载额外文件 — 使用上述核心模式） |
| Compute Engine 实例、机器类型、IP 地址 | 加载 `references/compute-instances.md` |
| GKE 集群、节点池、Pod、部署、服务、RBAC | 加载 `references/kubernetes-gke.md` |
| Cloud Run 服务、版本、执行 | 加载 `references/serverless-containers.md` |
| VPC 网络、子网、路由、DNS 记录 | 加载 `references/networking-dns.md` |
| Pub/Sub 主题 | 加载 `references/messaging-pubsub.md` |
| IAM 服务账户、角色、Secret Manager | 加载 `references/iam-security.md` |
| 监控仪表板、日志记录、保存的查询 | 加载 `references/monitoring-logging.md` |
| GCP 项目、区域、组织架构 | 加载 `references/resource-management.md` |
| 资源所有权、GCP 标签、组织结构 | 加载 `references/resource-ownership.md` |

---

## 核心概念

### 实体类型

GCP 资源使用 `GCP_*` 前缀，并可以使用 `smartscapeNodes` 函数进行查询。所有 GCP 实体都会自动发现并在 Dynatrace Smartscape 中建模。

**计算：** `GCP_COMPUTE_GOOGLEAPIS_COM_INSTANCE`, `GCP_COMPUTE_GOOGLEAPIS_COM_ADDRESS`
**网络：** `GCP_COMPUTE_GOOGLEAPIS_COM_NETWORK`, `GCP_COMPUTE_GOOGLEAPIS_COM_SUBNETWORK`, `GCP_COMPUTE_GOOGLEAPIS_COM_ROUTE`, `GCP_DNS_GOOGLEAPIS_COM_RESOURCERECORDSET`
**Kubernetes (GKE)：** `GCP_K8S_IO_POD`, `GCP_K8S_IO_NODE`, `GCP_K8S_IO_SERVICE`, `GCP_K8S_IO_SERVICEACCOUNT`, `GCP_K8S_IO_PERSISTENTVOLUMECLAIM`, `GCP_APPS_K8S_IO_DEPLOYMENT`, `GCP_APPS_K8S_IO_STATEFULSET`, `GCP_CONTAINER_GOOGLEAPIS_COM_NODEPOOL`, `GCP_RBAC_AUTHORIZATION_K8S_IO_CLUSTERROLEBINDING`, `GCP_RBAC_AUTHORIZATION_K8S_IO_ROLEBINDING`
**无服务器：** `GCP_RUN_GOOGLEAPIS_COM_SERVICE`, `GCP_RUN_GOOGLEAPIS_COM_REVISION`, `GCP_RUN_GOOGLEAPIS_COM_EXECUTION`
**IAM & 安全：** `GCP_IAM_GOOGLEAPIS_COM_SERVICEACCOUNT`, `GCP_IAM_GOOGLEAPIS_COM_ROLE`, `GCP_SECRETMANAGER_GOOGLEAPIS_COM_SECRETVERSION`
**消息传递：** `GCP_PUBSUB_GOOGLEAPIS_COM_TOPIC`
**监控：** `GCP_MONITORING_GOOGLEAPIS_COM_DASHBOARD`, `GCP_LOGGING_GOOGLEAPIS_COM_SAVEDQUERY`
**基础设施：** `GCP_REGION`

### 常见 GCP 字段

所有 GCP 实体都包含：
- `gcp.project.id` — GCP 项目标识符
- `gcp.region` — GCP 区域（例如，us-central1）
- `gcp.zone` — GCP 区域（例如，us-central1-a）
- `gcp.organization.id` — GCP 组织标识符
- `gcp.resource.name` — 资源名称
- `gcp.resource.type` — 资源类型标识符
- `gcp.asset.type` — GCP 资产类型
- `gcp.object` — 包含完整资源配置的 JSON 对象

### GCP 组织架构

GCP 资源按层次结构组织：
- **组织** — 顶级容器 (`gcp.organization.id`)
- **文件夹** — 组织内的逻辑分组
- **项目** — 资源容器 (`gcp.project.id`)
- **区域/区域** — 物理位置 (`gcp.region`, `gcp.zone`)

### 实体命名约定

GCP 实体类型遵循模式 `GCP_<SERVICE_API>_<RESOURCE>`：
- 服务 API 映射到 Google API 域（例如，`compute.googleapis.com` → `COMPUTE_GOOGLEAPIS_COM`）
- 资源是特定的资源类型（例如，`INSTANCE`, `NETWORK`）

示例：
- `GCP_COMPUTE_GOOGLEAPIS_COM_INSTANCE` — Compute Engine 虚拟机
- `GCP_K8S_IO_POD` — GKE Pod
- `GCP_RUN_GOOGLEAPIS_COM_SERVICE` — Cloud Run 服务

---

## 查询模式

所有 GCP 查询都基于四个核心模式。掌握这些模式，并根据任何实体类型进行调整。

### 模式 1：资源发现

按类型列出资源，按项目/区域/区域过滤，汇总计数：

```dql
smartscapeNodes "GCP_COMPUTE_GOOGLEAPIS_COM_INSTANCE"
| fields name, gcp.project.id, gcp.region, gcp.zone, gcp.resource.name
```

要列出所有 GCP 资源类型，请将替换为 `"GCP_*"` 并添加 `| summarize count = count(), by: {type} | sort count desc`。添加过滤器，如 `| filter gcp.project.id == "<PROJECT_ID>"` 或 `| filter gcp.region == "<REGION>"` 以缩小结果范围。

### 模式 2：配置解析

解析 `gcp.object` JSON 以获取详细配置字段：

```dql
smartscapeNodes "GCP_COMPUTE_GOOGLEAPIS_COM_INSTANCE"
| parse gcp.object, "JSON:gcpjson"
| fieldsAdd machineType = gcpjson[configuration][resource][machineType],
            status = gcpjson[configuration][resource][status]
| fields name, gcp.project.id, machineType, status
```

GCP 配置字段位于 `gcpjson[configuration][resource][...]` 下，用于主要资源属性，位于 `gcpjson[configuration][additionalAttributes][...]` 下，用于扩展属性。

### 模式 3：关系遍历

在资源之间跟踪关系：

```dql
smartscapeNodes "GCP_COMPUTE_GOOGLEAPIS_COM_INSTANCE"
| traverse "*", "GCP_COMPUTE_GOOGLEAPIS_COM_SUBNETWORK"
| fields name, gcp.project.id
```

GCP 实体在遍历时使用 `"*"` 作为关系名称，因为 GCP 实体没有命名关系类型。使用 `fieldsKeep` 在遍历中保留字段，并使用 `dt.traverse.history[-N]` 访问祖先字段。

### 模式 4：基于标签的所有权

按 GCP 标签对资源进行分组，以进行所有权和组织跟踪：

```dql
smartscapeNodes "GCP_*"
| filter isNotNull(`tags:gcp_labels`)
| fields name, gcp.project.id, `tags:gcp_labels`
```

GCP 标签通过 `tags:gcp_labels` 字段公开，必须使用反引号语法访问。将 `"GCP_*"` 替换为特定类型以缩小到一项服务。

---

## 参考指南

当上述核心模式需要服务特定调整时，加载参考文件以进行详细查询。

| 参考 | 加载时机 | 关键内容 |
|---|---|---|
| [compute-instances.md](references/compute-instances.md) | Compute Engine 虚拟机、机器类型、IP 地址、磁盘 | 实例库存、机器类型分布、状态检查 |
| [kubernetes-gke.md](references/kubernetes-gke.md) | GKE 集群、节点池、Pod、部署、服务、RBAC | 集群拓扑、工作负载分布、RBAC 绑定 |
| [serverless-containers.md](references/serverless-containers.md) | Cloud Run 服务、版本、执行 | 服务库存、版本跟踪、执行分析 |
| [networking-dns.md](references/networking-dns.md) | VPC 网络、子网、路由、DNS 记录 | 网络拓扑、子网分析、路由表、DNS 记录集 |
| [messaging-pubsub.md](references/messaging-pubsub.md) | Pub/Sub 主题 | 主题库存、消息传递拓扑 |
| [iam-security.md](references/iam-security.md) | IAM 服务账户、角色、Secret Manager | 服务账户审计、角色分析、密钥版本跟踪 |
| [monitoring-logging.md](references/monitoring-logging.md) | 监控仪表板、日志记录、保存的查询 | 仪表板库存、保存的查询分析 |
| [resource-management.md](references/resource-management.md) | GCP 项目、区域、组织架构 | 项目库存、区域分布、层次结构映射 |
| [resource-ownership.md](references/resource-ownership.md) | 资源所有权、GCP 标签、组织结构 | 基于标签的分组、项目级摘要、成本分摊 |

---

## 最佳实践

### 配置解析
1. 始终使用 JSON 解析器解析 `gcp.object`：`parse gcp.object, "JSON:gcpjson"`
2. 通过 `gcpjson[configuration][resource][...]` 访问主要资源属性
3. 通过 `gcpjson[configuration][additionalAttributes][...]` 访问扩展属性
4. 解析后使用 `isNotNull()` 检查空值

### GCP 层次结构
1. 组织 → 文件夹 → 项目 → 区域/区域
2. 使用 `gcp.project.id` 作为主要范围过滤器
3. 使用 `gcp.organization.id` 进行跨项目查询
4. 使用 `gcp.region` 和 `gcp.zone` 进行基于位置的分析

### 实体命名
1. 实体类型遵循 `GCP_<SERVICE_API>_<RESOURCE>` 格式
2. 服务 API 映射到 Google API 域，用下划线替换点和连字符
3. 尽量使用特定实体类型（避免使用 `"GCP_*"` 通配符）

### 标签
1. GCP 标签必须使用反引号语法访问：`` `tags:gcp_labels` ``
2. 使用 `isNotNull(`tags:gcp_labels`)` 进行基于标签的过滤
3. 使用汇总操作跟踪标签覆盖率

### 关系遍历
1. 使用 `"*"` 作为关系名称 — GCP 实体没有命名关系类型
2. 使用 `fieldsKeep` 在遍历中保留重要字段
3. 使用 `dt.traverse.history[-N]` 访问遍历历史
4. 复杂拓扑可能需要多次遍历操作

---

## 限制和说明

### Smartscape 限制
- Smartscape 数据反映最近的扫描；GCP 变更和 Dynatrace 可见性之间可能存在延迟
- 并非所有 GCP 服务都表示为实体类型
- 某些配置字段可能为空，具体取决于资源设置
- 资源发现取决于 GCP 集成配置

### GCP 特定说明
- GCP 标签必须使用反引号语法访问：`` `tags:gcp_labels` ``
- GCP 实体使用 `"*"` 进行关系遍历（没有命名关系类型）
- GCP 对象配置需要使用 `parse gcp.object, "JSON:gcpjson"` 解析
- 配置字段位于 `gcpjson[configuration][resource][...]` 下（与 AWS 模式不同）

### 一般提示
- 早期按项目和区域过滤以提高性能
- 使用 `isNotNull()` 和 `isNull()` 进行优雅的空值处理
- 结合项目和区域过滤器用于大型环境
- 使用 `countDistinct()` 获取唯一资源计数
- 在探索过程中使用 `| limit N` 限制结果
