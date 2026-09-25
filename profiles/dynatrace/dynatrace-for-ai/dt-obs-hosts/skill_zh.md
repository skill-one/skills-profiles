# 基础设施主机技能

监控和管理主机及进程基础设施，包括CPU、内存、磁盘、网络和技术清单。

## 何时使用此技能

当用户需要执行以下操作时，请使用此技能：

- **清单**："显示AWS us-east-1中所有Linux主机"
- **代理清单**："哪些主机运行FULL_STACK、INFRASTRUCTURE或DISCOVERY模式？" / "显示OneAgent版本分布"
- **监控**："哪些主机CPU使用率高？"
- **故障排除**："哪些进程消耗了最多的内存？"
- **发现**："生产环境中运行哪些数据库？"
- **规划**："跟踪Kubernetes版本分布以进行升级规划"
- **成本**："按成本中心计算基础设施成本"
- **安全**："查找所有在端口22上监听进程"
- **合规性**："识别运行EOL Java版本的主机"
- **质量**："检查AWS主机的数据完整性"
- **优化**："根据利用率查找右置大小候选对象"

---
> **需要跨源连接**：如果查询必须将主机数据与日志或其他遥测源（例如"显示具有其IP地址的Linux主机日志"）组合 → 在编写查询之前，请先阅读`dt-dql-essentials/references/smartscape-topology-navigation.md`。

---

## 核心概念

### 实体
- **HOST** - 物理或虚拟机（云或本地）
- **PROCESS** - 运行中的进程和进程组
- **CONTAINER** - Kubernetes容器
- **NETWORK_INTERFACE** - 主机网络接口
- **DISK** - 主机磁盘卷

### 指标类别
1. **主机指标** - `dt.host.cpu.*`, `dt.host.memory.*`, `dt.host.disk.*`, `dt.host.net.*`
2. **进程指标** - `dt.process.cpu.*`, `dt.process.memory.*`, `dt.process.io.*`, `dt.process.network.*`
3. **清单** - 操作系统类型、云提供商、技术堆栈、版本
4. **成本** - `dt.cost.costcenter`, `dt.cost.product`
5. **质量** - 元数据完整性、版本合规性

### 警报阈值
- **CPU/内存/磁盘**：80%警告，90%严重
- **网络**：>70%高，>85%饱和
- **磁盘延迟**：>20ms瓶颈
- **网络错误**：丢包率>1%，错误率>0.1%
- **交换**：>30%警告，>50%严重

---

## 关键工作流

### 1. 主机发现和分类

发现主机，按操作系统/云分类，清单资源。

```dql
smartscapeNodes "HOST"
| fieldsAdd os.type, cloud.provider, host.logical.cpu.cores, host.physical.memory
| summarize host_count = count(), by: {os.type, cloud.provider}
| sort host_count desc
```

**操作系统类型**：`LINUX`, `WINDOWS`, `AIX`, `SOLARIS`, `ZOS`

→ 对于云特定属性，请参阅[references/inventory-discovery.md](#cloud-specific-attributes)

### 2. 资源利用率监控

跨主机监控CPU、内存、磁盘、网络。

```dql
timeseries {
  cpu = avg(dt.host.cpu.usage),
  memory = avg(dt.host.memory.usage),
  disk = avg(dt.host.disk.used.percent)
}, by: {dt.smartscape.host}
| fieldsAdd host_name = getNodeName(dt.smartscape.host)
| filter arrayAvg(cpu) > 80 or arrayAvg(memory) > 80
| sort arrayAvg(cpu) desc
```

**高利用率阈值**：80%警告，90%严重

**关键CPU指标**：
- `dt.host.cpu.usage` — 总CPU利用率（0-100%）
- `dt.host.cpu.idle` — CPU空闲时间（利用率的倒数；用于异常检测）
- `dt.host.cpu.user` — 用户模式下CPU时间
- `dt.host.cpu.system` — 内核模式下CPU时间
- `dt.host.cpu.iowait` — CPU等待I/O（仅Linux）

→ 对于详细CPU分析，请参阅[references/host-metrics.md](references/host-metrics.md#cpu-monitoring)  
→ 对于内存分解，请参阅[references/host-metrics.md](references/host-metrics.md#memory-monitoring)

#### 磁盘可用空间 — 查找磁盘可用空间最多/最少的主机

```dql
timeseries disk_used_pct = avg(dt.host.disk.used.percent), by: {dt.smartscape.host}
| fieldsAdd host_name = getNodeName(dt.smartscape.host)
| fieldsAdd avg_disk_used = arrayAvg(disk_used_pct),
    free_pct = 100 - arrayAvg(disk_used_pct)
| sort free_pct desc
| limit 10
```

### 3. 进程资源分析

在进程级别识别顶级资源消耗者。

```dql
timeseries {
  cpu = avg(dt.process.cpu.usage),
  memory = avg(dt.process.memory.usage)
}, by: {dt.smartscape.process}
| fieldsAdd process_name = getNodeName(dt.smartscape.process)
| filter arrayAvg(cpu) > 50
| sort arrayAvg(cpu) desc
| limit 20
```

→ 对于进程I/O分析，请参阅[references/process-monitoring.md](references/process-monitoring.md#process-io)  
→ 对于进程网络指标，请参阅[references/process-monitoring.md](references/process-monitoring.md#process-network)

### 4. 技术堆栈清单

发现和跟踪软件技术和版本。

```dql
smartscapeNodes "PROCESS"
| fieldsAdd process.software_technologies
| expand tech = process.software_technologies
| fieldsAdd tech_type = tech[type], tech_version = tech[version]
| summarize process_count = count(), by: {tech_type, tech_version}
| sort process_count desc
```

**常见技术**：Java、Node.js、Python、.NET、数据库、Web服务器、消息系统

→ 对于版本合规性检查，请参阅[references/inventory-discovery.md](references/inventory-discovery.md#technology-inventory)

### 5. 通过端口进行服务发现

将监听端口映射到服务，用于安全和清单。

```dql
smartscapeNodes "PROCESS"
| fieldsAdd process.listen_ports, dt.process_group.detected_name
| filter isNotNull(process.listen_ports) and arraySize(process.listen_ports) > 0
| expand listen_port = process.listen_ports
| summarize process_count = count(), by: {listen_port, dt.process_group.detected_name}
| sort toLong(listen_port) asc
| limit 50
```

**知名端口**：80（HTTP）、443（HTTPS）、22（SSH）、3306（MySQL）、5432（PostgreSQL）

→ 对于全面端口映射，请参阅[references/inventory-discovery.md](references/inventory-discovery.md#port-discovery)

### 6. 容器和Kubernetes监控

跟踪容器分布和K8s工作负载类型。

```dql
smartscapeNodes "CONTAINER"
| fieldsAdd k8s.cluster.name, k8s.namespace.name, k8s.workload.kind
| summarize container_count = count(), by: {k8s.cluster.name, k8s.workload.kind}
| sort k8s.cluster.name, container_count desc
```

**工作负载类型**：`deployment`、`daemonset`、`statefulset`、`job`、`cronjob`

**注意**：容器镜像名称/版本在smartscape中不可用。

→ 对于K8s版本跟踪，请参阅[references/container-monitoring.md](references/container-monitoring.md#kubernetes-versions)  
→ 对于容器生命周期，请参阅[references/container-monitoring.md](references/container-monitoring.md#container-inventory)

### 7. 成本归因和成本分摊

按成本中心计算基础设施成本。

```dql
smartscapeNodes "HOST"
| fieldsAdd dt.cost.costcenter, host.logical.cpu.cores, host.physical.memory
| filter isNotNull(dt.cost.costcenter)
| fieldsAdd memory_gb = toDouble(host.physical.memory) / 1024 / 1024 / 1024
| summarize 
    host_count = count(),
    total_cores = sum(toLong(host.logical.cpu.cores)),
    total_memory_gb = sum(memory_gb),
    by: {dt.cost.costcenter}
| sort total_cores desc
```

→ 对于产品级成本跟踪，请参阅[references/inventory-discovery.md](references/inventory-discovery.md#cost-attribution)

### 8. 基础设施健康关联

关联主机和进程指标，进行跨层分析。

```dql
timeseries {
  host_cpu = avg(dt.host.cpu.usage),
  host_memory = avg(dt.host.memory.usage),
  process_cpu = avg(dt.process.cpu.usage)
}, by: {dt.smartscape.host, dt.smartscape.process}
| fieldsAdd
    host_name = getNodeName(dt.smartscape.host),
    process_name = getNodeName(dt.smartscape.process)
| filter arrayAvg(host_cpu) > 70
| sort arrayAvg(host_cpu) desc
```

**健康评分**：任何资源>90%为严重，>80%为警告

→ 对于多资源饱和检测，请参阅[references/host-metrics.md](references/host-metrics.md#resource-saturation)

### 9. OneAgent清单

按OneAgent监控模式、版本或云区域计数和列出主机。

**ONEAGENT实体**：OneAgent是一个单独的smartscape实体类型（`smartscapeNodes "ONEAGENT"`）。通过`monitors`边（边运行ONEAGENT → HOST，因此HOST→ONEAGENT为`direction: backward`）访问它。

**关键ONEAGENT字段**：
- `dt.agent.monitoring_mode` — 监控覆盖级别：`FULL_STACK` / `INFRASTRUCTURE` / `DISCOVERY`
- `dt.agent.module.version` — 安装版本字符串，例如`1.347.0.20260809-172428`

**按监控模式计数**：

```dql
smartscapeNodes "HOST"
| traverse edgeTypes: {monitors}, targetTypes: {ONEAGENT}, direction: backward
| fieldsAdd oa_mode = `dt.agent.monitoring_mode`
| summarize host_count = count(), by: {oa_mode}
| sort host_count desc
```

**按代理版本计数**：

```dql
smartscapeNodes "HOST"
| traverse edgeTypes: {monitors}, targetTypes: {ONEAGENT}, direction: backward
| fieldsAdd oa_version = `dt.agent.module.version`
| summarize host_count = count(), by: {oa_version}
| sort host_count desc
```

**组合：模式 + 版本**（用于升级规划）：

```dql
smartscapeNodes "HOST"
| traverse edgeTypes: {monitors}, targetTypes: {ONEAGENT}, direction: backward
| fieldsAdd oa_mode = `dt.agent.monitoring_mode`, oa_version = `dt.agent.module.version`
| summarize host_count = count(), by: {oa_mode, oa_version}
| sort host_count desc
```

**监控模式**：`FULL_STACK`（完整代码级监控+基础设施）、`INFRASTRUCTURE`（仅基础设施指标，无代码级监控）、`DISCOVERY`（拓扑发现和基本主机监控）

→ 对于按模式/版本列出主机，请参阅[references/inventory-discovery.md](references/inventory-discovery.md#oneagent-inventory)

---

## 响应构建

当用户要求数据检索或DQL查询（例如"显示按CPU排名的顶级主机"）时，**在响应中包含DQL查询**以及结果。用户希望看到并重用查询——它不仅是获取结果的手段，更是交付物。

当用户要求分析（异常检测、预测、估计未来主机指标）时，分析结果才是交付物。专注于清晰地呈现发现：
- **优先考虑指标级发现**，而不是数据收集工件。如果分析工具报告数据空白以及实际异常，请首先呈现用户询问的指标行为，并将空白仅作为补充上下文提及。
- **包含主机名称**（而不仅仅是ID），使用`getNodeName(dt.smartscape.host)`或`get-entity-name`工具。
- **说明分析的时间范围**和使用的工具/参数。

---

## 分析工作流

主机指标查询通常作为分析工具（异常检测、预测、季节性分析）的输入。此技能有助于构建正确的DQL查询；实际分析由专用工具执行。

### 异常检测和模式分析

当用户询问"异常行为"、"异常"、"峰值"或"突然变化"在主机指标时，工作流程是：

1. **使用此技能的模式构建timeseries查询**
2. **将其传递给适当的分析工具**（异常检测器、新颖性检测）

**选择检测器之间的差异**：
- **`adaptive-anomaly-detector`** — 当用户询问*幅度*时使用："峰值"、"急剧变化"、"值超过正常值"、"突然跳跃"。它回答"该指标是否跨越了意外的阈值？"并报告警报持续时间和峰值值。
- **`timeseries-novelty-detection`** — 当用户询问*行为变化*时使用："异常模式"、"某事发生了变化"、"趋势"、"新行为"。它回答"信号的形状是否发生了变化？"，而不暗示跨越了特定的阈值。

**异常结果响应格式**：包含主机**名称**（通过`getNodeName(dt.smartscape.host)`或`get-entity-name`解析）和主机**实体ID** alongside时间戳和值。
仅实体ID对用户来说是不透明的；名称单独使用则无法进行后续查询。

**新颖性类型选择规则**：在使用新颖性检测时，默认将`analysisNoveltyType`设置为仅`[SPIKE, CHANGE_IN_VALUES, TREND_IN_VALUES]`。
**排除**`GAP_WITH_MISSING_VALUES`和`CHANGE_IN_MISSING_VALUES`，除非用户明确要求关于数据空白或监控覆盖率。数据空白是基础设施问题，不是指标行为异常——在用户询问CPU或内存模式时报告它们是不正确的。

分析工具的查询应使用简单的`timeseries`格式，具有单个聚合指标和适当的时间范围：

```dql
timeseries avg(dt.host.cpu.idle), by: {dt.smartscape.host}
```

```dql
timeseries avg(dt.host.memory.usage), by: {dt.smartscape.host}
```

避免添加过滤器或字段转换以减少数据——分析工具在完整timeseries数据上工作最佳。

### 预测

当用户要求"预测"、"预测"或"估计未来"主机指标时：

1. **使用具有足够历史数据的timeseries查询**（例如，7d用于短期，30d用于长期预测）
2. **将其传递给预测工具**并指定所需的预测范围

**预测范围**（预测多远）和历史窗口（模型训练使用多少过去数据）是独立的。像"预测未来2小时"这样的请求将范围设置为2h——它什么也没说关于回溯。无论预测范围多短，始终使用至少7天的历史数据。训练数据点太少会导致预测模型失败并回退到原始历史值。

```dql
timeseries avg(dt.host.cpu.usage), by: {dt.smartscape.host}
```

### 季节性检测

当用户询问"季节性"、"每周模式"或"重复行为"时：

1. **使用较长时间范围**（至少14d用于每周，30d+用于每月）
2. **将其传递给季节性基线异常检测器**

**季节性分析结果响应格式**：在呈现结果时，包括：
- 是否检测到季节性异常（是/否）
- 分析时间范围和参数
- 对于每个受影响的主机：主机名称（而不仅仅是ID）、违规时间戳、违规计数、基线值与实际值、以及上限/下限
- 如果涉及多个主机，按主机组织结果

### 范围边界 — 服务级与主机级指标

此技能仅涵盖**主机和进程基础设施指标**。如果用户询问服务级指标（请求率、响应时间、错误率、每分钟服务调用次数、吞吐量），请使用`dt-obs-services`——即使问题涉及这些指标的预测或异常检测。

**重定向到`dt-obs-services**："每分钟服务调用次数"、"请求率"、"按服务响应时间"、"按端点错误率"、"服务吞吐量预测"。

---

## 常见查询模式

### 模式1：Smartscape发现
使用`smartscapeNodes`发现和分类实体。
```dql-template
smartscapeNodes "HOST"
| fieldsAdd <attributes>
| filter <conditions>
| summarize <aggregations>
```

### 模式2：Timeseries性能
使用`timeseries`分析指标随时间变化。
```dql-template
timeseries metric = avg(dt.host.<metric>), by: {dt.smartscape.host}
| fieldsAdd <calculations>
| filter <thresholds>
```

### 模式3：跨层关联
关联主机和进程指标。
```dql
timeseries {
  host_cpu = avg(dt.host.cpu.usage),
  process_cpu = avg(dt.process.cpu.usage)
}, by: {dt.smartscape.host, dt.smartscape.process}
```

### 模式4：使用查找进行实体丰富
使用实体属性丰富数据。在`lookup`之后，使用`lookup.`前缀引用字段。
```dql
timeseries cpu = avg(dt.host.cpu.usage), by: {dt.smartscape.host}
| lookup [
    smartscapeNodes HOST
    | fields id, cpuCores, memoryTotal
  ], sourceField:dt.smartscape.host, lookupField:id
| fieldsAdd cores = lookup.cpuCores, mem_gb = lookup.memoryTotal / 1024 / 1024 / 1024
```

---

## 标签和元数据

### 重要说明
- 通用`tags`字段在smartscape查询中**未填充**
- 使用特定标签字段：`tags:azure[*]`, `tags:environment`
- 使用自定义元数据：`host.custom.metadata[*]`

### 可用标签
- **Azure标签**：`tags:azure[dt_owner_team]`, `tags:azure[dt_cloudcost_capability]`
- **环境**：`tags:environment`
- **自定义元数据**：`host.custom.metadata[OperatorVersion]`, `host.custom.metadata[Cluster]`
- **成本**：`dt.cost.costcenter`, `dt.cost.product`

→ 对于完整标签参考，请参阅[references/inventory-discovery.md](references/inventory-discovery.md#tags-and-metadata)

---

## 云特定属性

### AWS
- `cloud.provider == "aws"`
- `aws.region`, `aws.availability_zone`, `aws.account.id`
- `aws.resource.id`, `aws.resource.name`
- `aws.state`（运行、停止、终止）

### Azure
- `cloud.provider == "azure"`
- `azure.location`, `azure.subscription`, `azure.resource.group`
- `azure.status`, `azure.provisioning_state`
- `azure.resource.sku.name`（VM大小）

### GCP
- `cloud.provider == "gcp"`
- `gcp.region`, `gcp.zone`, `gcp.location`
- `gcp.project.id`（注意：两个点）
- `gcp.resource.type`（例如`gce_instance`），`gcp.asset.type`（例如`compute.googleapis.com/Instance`）

### Kubernetes
- `k8s.cluster.name`, `k8s.cluster.uid`
- `k8s.namespace.name`, `k8s.node.name`, `k8s.pod.name`
- `k8s.workload.name`, `k8s.workload.kind`

→ 对于多云分析，请参阅[references/inventory-discovery.md](references/inventory-discovery.md#multi-cloud-hosts)

---

## 最佳实践

1. 使用百分位数（p95, p99）进行延迟；`max()`用于限制；`avg()`用于趋势
2. 设置多级阈值（警告80%，严重90%）
3. 在管道早期过滤；使用`| limit N`限制结果
4. 在丰富之前聚合
5. 使用`getNodeName(dt.smartscape.host)`获取人类可读的主机名称；`getNodeName(dt.smartscape.process)`获取进程
6. 将字节转换为GB：`/ 1024 / 1024 / 1024`；使用`round(value, decimals: 1)`进行舍入

**时间窗口**：实时：5-15分钟 | 趋势：1-7天 | 容量规划：30-90天

### 限制
- `dt.host.cpu.iowait` 仅在Linux上可用
- 通用`tags`字段在smartscape中**未填充**（使用特定标签命名空间）
- 容器镜像名称在smartscape中**不可用**

---

## 故障排除

| 问题 | 原因 | 解决方案 |
|-------|-------|----------|
| 未返回主机从`smartscapeNodes "HOST"` | 缺少时间范围或OneAgent未部署 | 验证OneAgent已安装；向查询添加时间范围 |
| `tags`字段始终为空 | 通用`tags`在smartscape中未填充 | 使用特定标签命名空间：`tags:azure[*]`, `tags:environment`, `dt.cost.costcenter` |
| 内存值以字节为单位难以阅读 | 原始指标单位为字节 | 除以`1024 / 1024 / 1024`，并使用`round(value, decimals: 1)` |
| `dt.host.cpu.iowait`返回无数据 | 指标仅Linux可用 | 检查`os.type`；iowait在Windows、AIX、Solaris上不可用 |
| 容器镜像名称缺失 | 在smartscape中不可用 | 使用`k8s.object`解析获取镜像详细信息；请参阅dt-obs-kubernetes技能 |
| `process.software_technologies`为空 | 进程未由深度代码级监控监控 | 验证OneAgent深度监控已启用以监控进程组 |
| `dt.agent.monitoring_mode`始终为空 | 字段名称使用下划线，而不是点 | 使用`dt.agent.monitoring_mode`；`dt.agent.monitoring.mode`（点）始终返回null |
| `gcp.project.id`始终为空 | 使用了错误的字段名称 | GCP项目使用两个点：`gcp.project.id`不是下划线，`gcp.project_id`始终返回null |

---

## 何时加载参考

此技能使用**渐进式披露**。从这里开始80%的用例。当需要详细规范时加载参考文件。

### 加载host-metrics.md时：
- 分析CPU组件分解（用户、系统、iowait、steal）
- 调查内存压力和交换使用
- 故障排除磁盘I/O延迟
- 诊断网络数据包丢失或错误

### 加载process-monitoring.md时：
- 分析进程级I/O模式
- 调查TCP连接质量
- 检测资源耗尽（文件描述符、线程）
- 跟踪GC挂起时间

### 加载container-monitoring.md时：
- 分析容器生命周期和流失
- 跟踪Kubernetes版本分布
- 管理OneAgent操作员版本
- 规划K8s集群升级

### 加载inventory-discovery.md时：
- 通过端口发现进行安全审计
- 实施成本归因和成本分摊
- 验证数据质量和元数据完整性
- 管理多云基础设施
- 列出或按OneAgent模式/版本过滤主机

---

## 参考

- [host-metrics.md](references/host-metrics.md) - 详细主机CPU、内存、磁盘和网络监控
- [process-monitoring.md](references/process-monitoring.md) - 进程级CPU、内存、I/O和网络分析
- [container-monitoring.md](references/container-monitoring.md) - 容器清单、Kubernetes版本和操作员管理
- [inventory-discovery.md](references/inventory-discovery.md) - 主机/进程发现、技术清单、成本归因和数据质量

---
