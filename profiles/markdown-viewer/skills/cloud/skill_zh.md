# 云架构图生成器

**快速入门：** 选择云服务提供商 → 声明模板图标 → 分组到 VPC/区域区域 → 使用箭头语法连接 → 用 ` ```plantuml ` 分隔符包裹。

> ⚠️ **重要提示：** 始终使用 ` ```plantuml ` 或 ` ```puml ` 代码分隔符。绝对不要使用 ` ```text ` — 它将不会渲染为图表。

## 关键规则

- 每个图表以 `@startuml` 开头并以 `@enduml` 结尾
- 使用 `left to right direction` 用于典型云架构（数据流从左→右）
- 使用 `mxgraph.*` 模板语法表示云服务图标
- 默认颜色自动应用 — 你不需要指定 `fillColor` 或 `strokeColor`
- 使用 `rectangle "VPC" { ... }` 或 `package "Region" { ... }` 表示云容器
- 使用 `cloud "Name" { ... }` 表示云边界形状
- 有向流使用 `-->`，异步/事件驱动流使用 `..>`（虚线）

**完整模板参考：** 查看可用图标 9500+ 的 [stencils/README.md](../uml/stencils/README.md)。

## Mxgraph 模板语法

```
mxgraph.<provider>.<icon> "Label" as <alias>
```

### 常见云模板系列

| 系列 | 前缀 | 典型图标 |
|------|------|----------|
| AWS | `mxgraph.aws4.*` | `lambda_function`, `ec2`, `rds_instance`, `s3`, `api_gateway`, `cloudfront`, `dynamodb` |
| Azure | `mxgraph.azure.*` | `virtual_machine`, `azure_load_balancer`, `sql_database`, `azure_active_directory`, `storage` |
| GCP | `mxgraph.gcp2.*` | `compute_engine_2`, `cloud`, `process`, `repository`, `cloud_monitoring` |
| 阿里云 | `mxgraph.alibaba_cloud.*` | `ecs_elastic_compute_service`, `slb_server_load_balancer_01`, `polardb`, `oss_object_storage_service` |
| IBM | `mxgraph.ibm_cloud.*` | `ibm-cloud--kubernetes-service`, `load-balancer--application`, `database--postgresql` |
| Kubernetes | `mxgraph.kubernetes.*` | `pod`, `svc`, `deploy`, `ing`, `sts`, `pvc`, `cm`, `secret` |
| OpenStack | `mxgraph.openstack.*` | `nova_server`, `neutron_router`, `cinder_volume`, `swift_container` |

### 连接类型

| 语法 | 含义 | 用例 |
|------|------|------|
| `A --> B` | 实线箭头 | 同步 API 调用/数据流 |
| `A ..> B` | 虚线箭头 | 异步事件/触发/复制 |
| `A -- B` | 实线，无箭头 | 物理/双向连接 |
| `A --> B : "label"` | 带标签的连接 | 描述数据流 |

### 快速示例

```plantuml
@startuml
left to right direction
mxgraph.aws4.users "用户" as users
mxgraph.aws4.cloudfront "云前端" as cf
mxgraph.aws4.application_load_balancer "应用负载均衡器" as alb

rectangle "VPC" {
  mxgraph.aws4.ec2 "EC2" as ec2
  mxgraph.aws4.rds_instance "RDS" as rds
}

users --> cf
cf --> alb
alb --> ec2
ec2 --> rds
@enduml
```

## 云架构类型

| 类型 | 目的 | 关键模板 | 示例 |
|------|------|----------|------|
| AWS | 亚马逊云服务 | `mxgraph.aws4.*` | [aws-basic.md](examples/aws-basic.md) |
| AWS 无服务器 | 事件驱动无服务器 | `mxgraph.aws4.*` | [aws-serverless.md](examples/aws-serverless.md) |
| Azure | 微软 Azure | `mxgraph.azure.*` | [azure-hybrid-network.md](examples/azure-hybrid-network.md) |
| GCP | 谷歌云平台 | `mxgraph.gcp2.*` | [gcp-log-processing.md](examples/gcp-log-processing.md) |
| 阿里云 | 阿里云 | `mxgraph.alibaba_cloud.*` | [alibaba-web-app.md](examples/alibaba-web-app.md) |
| IBM 云 | IBM 云 | `mxgraph.ibm_cloud.*` | [ibm-kubernetes.md](examples/ibm-kubernetes.md) |
| Kubernetes | 容器编排 | `mxgraph.kubernetes.*` | [kubernetes-microservices.md](examples/kubernetes-microservices.md) |
| OpenStack | 私有云 | `mxgraph.openstack.*` | [openstack-basic.md](examples/openstack-basic.md) |
