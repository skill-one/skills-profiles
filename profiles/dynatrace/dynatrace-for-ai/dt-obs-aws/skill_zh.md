# AWS 云基础设施

使用 Dynatrace Smartscape 和 DQL 监控和分析 AWS 资源。查询 AWS 服务，优化成本，管理安全，并规划 AWS 基础设施的容量。

## 何时使用此技能

当用户需要在 Dynatrace 中处理 AWS 资源时，使用此技能。加载任务类型的参考文件：

- **清单**："显示 us-east-1 中的所有 EC2 实例"
- **网络**："查找 VPC vpc-abc123 中的所有资源"
- **数据库**："列出所有启用 Multi-AZ 的 RDS 实例"
- **无服务器**："显示具有 VPC 访问权限的 Lambda 函数"
- **成本**："查找未附加的 EBS 卷以节省成本"
- **安全**："识别公开可访问的数据库"
- **合规性**："查找缺少环境标签的资源"
- **容量**："分析子网 IP 利用率"
- **故障排除**："通过目标组将负载均衡器映射到实例"
- **问题分析**："此 AWS 问题之前发生了什么变化？" / "哪些事件影响了此资源？"
- **工作负载上下文**："此实例是否位于负载均衡器后面，是否在 EKS 集群中，还是由 ECS 管理？"
- **事件**："AWS 中是否有任何最近的事件影响此资源？"

---

## 核心概念

### 实体类型

AWS 资源使用 `AWS_*` 前缀，并可以使用 `smartscapeNodes` 函数进行查询。所有 AWS 实体都会自动在 Dynatrace Smartscape 中发现和建模。

**计算**：`AWS_EC2_INSTANCE`, `AWS_LAMBDA_FUNCTION`, `AWS_ECS_CLUSTER`, `AWS_ECS_SERVICE`, `AWS_EKS_CLUSTER`
**网络**：`AWS_EC2_VPC`, `AWS_EC2_SUBNET`, `AWS_EC2_SECURITYGROUP`, `AWS_EC2_NATGATEWAY`, `AWS_EC2_VPCENDPOINT`
**数据库**：`AWS_RDS_DBINSTANCE`, `AWS_RDS_DBCLUSTER`, `AWS_DYNAMODB_TABLE`, `AWS_ELASTICACHE_CACHECLUSTER`
**存储**：`AWS_S3_BUCKET`, `AWS_EC2_VOLUME`, `AWS_EFS_FILESYSTEM`
**负载均衡**：`AWS_ELASTICLOADBALANCINGV2_LOADBALANCER`, `AWS_ELASTICLOADBALANCINGV2_TARGETGROUP`
**消息传递**：`AWS_SQS_QUEUE`, `AWS_SNS_TOPIC`, `AWS_EVENTS_EVENTBUS`, `AWS_MSK_CLUSTER`

### 常见 AWS 字段

所有 AWS 实体都包含：
- `aws.account.id` - AWS 账户标识符
- `aws.region` - AWS 区域（例如，us-east-1）
- `aws.resource.id` - 唯一资源标识符
- `aws.resource.name` - 资源名称
- `aws.arn` - Amazon Resource Name
- `aws.vpc.id` - VPC 标识符（适用于附加到 VPC 的资源）
- `aws.subnet.id` - 子网标识符
- `aws.availability_zone` - 可用区
- `aws.security_group.id` - 安全组 ID（数组）
- `tags` - 资源标签（使用 `tags[TagName]`）

### 日志和 Bizevents 上的 AWS 字段

AWS 发起的 **日志**（`fetch logs`）包含这些字段，无需探索：
- `aws.region`, `aws.account.id`, `aws.service`, `aws.log_group`, `aws.log_stream`
- 以及标准日志字段：`content`, `loglevel`, `timestamp`, `k8s.*`, `dt.smartscape.*`

AWS 发起的 **bizevents**（`fetch bizevents`）包含：
- `aws.region`, `aws.account.id`, `event.type`, `event.provider`

使用 `filter isNotNull(aws.region)` 将范围限定为 AWS 发起的记录。

### 关系类型

AWS 实体使用以下关系类型：
- `is_attached_to` - 排他性连接（例如，卷连接到实例）
- `uses` - 依赖关系（例如，实例使用安全组）
- `runs_on` - 垂直关系（例如，实例运行在 AZ 上）
- `is_part_of` - 组成关系（例如，实例在集群中）
- `belongs_to` - 聚合关系（例如，服务属于集群）
- `balances` - 负载均衡（例如，目标组均衡实例）
- `balanced_by` - 反向负载均衡关系（例如，负载均衡器由目标组均衡）

### AWS 指标键命名约定

Dynatrace 使用此模式摄取 AWS CloudWatch 指标：

```
cloud.aws.<service>.<MetricName>.By.<DimensionName>
```

`<service>` 是小写的 AWS 服务名称，`<MetricName>` 是 CloudWatch 指标名称（保留大小写），`<DimensionName>` 是 CloudWatch 维度。

示例：`cloud.aws.ec2.CPUUtilization.By.InstanceId`, `cloud.aws.lambda.Invocations.By.FunctionName`, `cloud.aws.rds.CPUUtilization.By.DBInstanceIdentifier`

使用 `timeseries` 而不是 `fetch` 来获取这些指标。按 `dt.smartscape_source.id` 分组以按实体拆分。

→ 参考 [references/metrics-performance.md](references/metrics-performance.md) 获取按服务划分的完整指标目录和 DQL 查询模板。

---

## 关键工作流

### 1. AWS 资源发现

按类型获取所有 AWS 资源：

```dql
smartscapeNodes "AWS_*"
| summarize count = count(), by: {type}
| sort count desc
```

按账户和区域过滤：

```dql
smartscapeNodes "AWS_*"
| filter aws.account.id == "123456789012" and aws.region == "us-east-1"
| fields type, name, aws.resource.id
```

使用标签进行过滤：

```dql
smartscapeNodes "AWS_*"
| filter tags[Environment] == "production"
| summarize count = count(), by: {type, aws.region}
```

→ 完整资源清单模式，参考 [references/resource-management.md](references/resource-management.md)

### 2. VPC 网络分析

列出所有 VPC：

```dql
smartscapeNodes "AWS_EC2_VPC"
| fields name, aws.account.id, aws.region, aws.vpc.id
```

查找 VPC 中的资源：

```dql
smartscapeNodes "AWS_*"
| filter aws.vpc.id == "vpc-0be61db7c5d2d1bd1"
| summarize resource_count = count(), by: {type, aws.subnet.id}
| sort resource_count desc
```

分析安全组使用情况：

```dql
smartscapeNodes "AWS_EC2_INSTANCE"
| filter contains(aws.security_group.id, "sg-abc123")
| fields name, aws.resource.id, aws.vpc.id, aws.subnet.id
```

→ VPC 网络参考 [references/vpc-networking-security.md](references/vpc-networking-security.md)  
→ 安全组模式参考 [references/security-compliance.md](references/security-compliance.md)

### 3. 数据库监控

列出所有 RDS 实例：

```dql
smartscapeNodes "AWS_RDS_DBINSTANCE"
| fields name, aws.account.id, aws.region, aws.vpc.id, aws.availability_zone
```

查找 Multi-AZ 数据库：

```dql
smartscapeNodes "AWS_RDS_DBINSTANCE"
| parse aws.object, "JSON:awsjson"
| fieldsAdd multiAZ = awsjson[configuration][multiAZ]
| filter multiAZ == true
| fields name, aws.resource.id, aws.region
```

按引擎类型分组：

```dql
smartscapeNodes "AWS_RDS_DBINSTANCE"
| parse aws.object, "JSON:awsjson"
| fieldsAdd engine = awsjson[configuration][engine]
| summarize db_count = count(), by: {engine, aws.region}
| sort db_count desc
```

→ 数据库监控参考 [references/database-monitoring.md](references/database-monitoring.md)

### 4. 无服务器和容器工作负载

列出 Lambda 函数：

```dql
smartscapeNodes "AWS_LAMBDA_FUNCTION"
| fields name, aws.account.id, aws.region, aws.vpc.id
```

查找集群中的 ECS 服务：

```dql
smartscapeNodes "AWS_ECS_SERVICE"
| traverse "belongs_to", "AWS_ECS_CLUSTER"
| fields name, aws.resource.id, aws.region
```

列出 EKS 集群：

```dql
smartscapeNodes "AWS_EKS_CLUSTER"
| fields name, aws.account.id, aws.region, aws.vpc.id
```

→ 无服务器参考 [references/serverless-containers.md](references/serverless-containers.md)  
→ 容器参考 [references/serverless-containers.md](references/serverless-containers.md)

### 5. 负载均衡器拓扑

完整的负载均衡器到实例映射：

```dql
smartscapeNodes "AWS_ELASTICLOADBALANCINGV2_LOADBALANCER"
| parse aws.object, "JSON:awsjson"
| fieldsAdd dnsName = awsjson[configuration][dnsName], scheme = awsjson[configuration][scheme]
| filter scheme == "internet-facing"
| traverse "balanced_by", "AWS_ELASTICLOADBALANCINGV2_TARGETGROUP", direction:backward, fieldsKeep:{dnsName, id}
| fieldsAdd targetGroupName = aws.resource.name
| traverse "balances", "AWS_EC2_INSTANCE", fieldsKeep: {targetGroupName, id}
| fieldsAdd loadBalancerDnsName = dt.traverse.history[-2][dnsName],
            loadBalancerId = dt.traverse.history[-2][id],
            targetGroupId = dt.traverse.history[-1][id]
```

→ 负载均衡参考 [references/load-balancing-api.md](references/load-balancing-api.md)

### 6. 成本优化

查找未附加的 EBS 卷：

```dql
smartscapeNodes "AWS_EC2_VOLUME"
| parse aws.object, "JSON:awsjson"
| fieldsAdd state = awsjson[configuration][state]
| filter state == "available"
| fields name, aws.resource.id, aws.availability_zone, aws.account.id
```

按类型分析 EBS 成本：

```dql
smartscapeNodes "AWS_EC2_VOLUME"
| parse aws.object, "JSON:awsjson"
| fieldsAdd volumeType = awsjson[configuration][volumeType],
            size = awsjson[configuration][size],
            state = awsjson[configuration][state]
| summarize total_volumes = count(), total_size_gb = sum(size), by: {volumeType, state}
| sort total_size_gb desc
```

→ 成本优化参考 [references/cost-optimization.md](references/cost-optimization.md)

### 7. 安全和合规性

查找公开可访问的数据库：

```dql
smartscapeNodes "AWS_RDS_DBINSTANCE"
| parse aws.object, "JSON:awsjson"
| fieldsAdd publiclyAccessible = awsjson[configuration][publiclyAccessible]
| filter publiclyAccessible == true
| fields name, aws.resource.id, aws.vpc.id, aws.account.id
```

安全组影响范围：

```dql
smartscapeNodes "AWS_EC2_INSTANCE"
| traverse "uses", "AWS_EC2_SECURITYGROUP"
| summarize instance_count = count(), by: {aws.resource.name, aws.vpc.id}
| sort instance_count desc
| limit 20
```

→ 安全参考 [references/security-compliance.md](references/security-compliance.md)

### 8. 资源所有权和标签

查找未标记的资源：

```dql
smartscapeNodes "AWS_*"
| filter isNull(tags)
| fields type, name, aws.resource.id, aws.account.id, aws.region
```

按成本中心分配成本：

```dql
smartscapeNodes "AWS_*"
| filter isNotNull(tags[CostCenter])
| summarize resource_count = count(), by: {tags[CostCenter], type}
| sort resource_count desc
```

→ 资源所有权参考 [references/resource-ownership.md](references/resource-ownership.md)

---

## 常见查询模式

| 模式 | 模板 |
|---------|----------|
| **发现** | `smartscapeNodes "AWS_*" \| fieldsAdd <attrs> \| filter <cond> \| summarize <agg>` |
| **配置解析** | `smartscapeNodes "AWS_<T>" \| parse aws.object, "JSON:awsjson" \| fieldsAdd f = awsjson[configuration][field]` |
| **遍历** | `smartscapeNodes "AWS_<SRC>" \| traverse "<rel>", "AWS_<TGT>"` |
| **多类型** | `smartscapeNodes "AWS_T1", "AWS_T2" \| filter <cond> \| summarize count(), by: {type}` |

---


## 最佳实践

### 查询优化
1. 早期按账户和区域过滤
2. 使用特定实体类型（尽可能避免 `"AWS_*"` 通配符）
3. 使用 `| limit N` 限制结果以进行探索
4. 在访问嵌套字段之前使用 `isNotNull()` 检查

### 配置解析
1. 始终使用 JSON 解析器解析 `aws.object`：`parse aws.object, "JSON:awsjson"`
2. 使用一致的字段命名：`fieldsAdd configField = awsjson[configuration][field]`
3. 解析后检查空值
4. 使用 `toString()` 处理复杂的嵌套对象

### 安全字段
1. 安全组 ID 是数组 - 使用 `contains()` 或 `expand`
2. 解析 `aws.object` 以获取详细的安全上下文
3. 检查 `publiclyAccessible`, `storageEncrypted` 和类似标志
4. 验证 IAM 角色假设

### 标签策略
1. 使用 `tags[TagName]` 按特定标签值过滤
2. `tags` 是 JSON 对象，不是数组 — 使用 `isNull(tags)` 查找未标记的资源，**永远**不要使用 `arraySize(tags)`
3. 使用 `isNull(tags[TagName])` 查找缺少特定标签的资源
4. 实施一致的标签命名约定
5. 使用汇总操作跟踪标签覆盖率

---

## 限制和说明

### Smartscape 限制
- AWS 对象配置需要使用 `parse aws.object, "JSON:awsjson"` 解析
- AWS 指标作为 Dynatrace 指标使用 `cloud.aws.*` 命名约定（参考 [AWS 指标命名约定](#aws-metric-naming-convention)）
- 资源发现取决于 AWS 集成配置
- 标签同步可能有轻微延迟

### 关系遍历
- 使用 `direction:backward` 进行反向关系（例如，目标组 → 负载均衡器）
- 使用 `fieldsKeep` 在遍历过程中保留重要字段
- 使用 `dt.traverse.history[-N]` 访问遍历历史
- 复杂拓扑可能需要多个遍历操作

### 一般建议
- 使用 `getNodeName()` 获取人类可读的资源名称
- 使用 `isNotNull()` 和 `isNull()` 优雅地处理空值
- 结合区域和账户过滤器用于大型环境
- 使用 `countDistinct()` 获取唯一资源计数

---

## 何时加载参考

此技能使用 **渐进式披露**。对于 80% 的用例，从这里开始。当需要详细规范时，加载参考文件。

### 加载 vpc-networking-security.md 当：
- 分析 VPC 拓扑和连接性
- 调查安全组配置
- 按安全组查找资源
- 排查网络接口问题

### 加载 database-monitoring.md 当：
- 管理 RDS 实例和集群
- 分析数据库引擎分布
- 检查 Multi-AZ 配置
- 监控缓存集群

### 加载 serverless-containers.md 当：
- 处理 Lambda 函数
- 分析 ECS/EKS 部署
- 调查容器网络
- 规划无服务器迁移

### 加载 load-balancing-api.md 当：
- 映射负载均衡器拓扑
- 分析目标组健康
- 使用 API Gateway
- 配置 CloudFront

### 加载 messaging-event-streaming.md 当：
- 管理 SQS 队列和 SNS 主题
- 分析 EventBridge 事件总线
- 使用 Kinesis 或 MSK
- 监控 Step Functions

### 加载 resource-management.md 当：
- 进行资源审计
- 分析标签合规性
- 查找未附加的资源
- 规划区域分布

### 加载 cost-optimization.md 当：
- 识别节省成本的机会
- 分析存储成本
- 查找未使用的资源
- 优化实例类型

### 加载 capacity-planning.md 当：
- 规划容量扩展
- 分析资源利用率
- 监控子网 IP 利用率
- 调整自动扩展组大小

### 加载 security-compliance.md 当：
- 进行安全审计
- 检查加密状态
- 分析 IAM 角色
- 查找公开资源

### 加载 resource-ownership.md 当：
- 实施成本分摊
- 跟踪资源所有权
- 按团队分配成本
- 管理多账户环境

### 加载 events.md 当：
- 调查问题之前或期间发生了什么变化
- 检查最近的 CloudFormation 堆栈部署
- 审查 AWS Auto Scaling 活动（扩展/缩减）
- 检查影响资源的 AWS Health 服务事件

### 加载 workload-detection.md 当：
- 确定 EC2 实例的编排方式（ECS, EKS, Batch, ASG, 独立）
- 跟随依赖于工作负载模式的解决方案路径
- 理解实例故障的影响范围

---

## 参考

- [vpc-networking-security.md](references/vpc-networking-security.md) - VPC 基础设施、安全组和网络连接
- [database-monitoring.md](references/database-monitoring.md) - RDS、DynamoDB、ElastiCache 和 Redshift 监控
- [serverless-containers.md](references/serverless-containers.md) - Lambda、ECS、EKS 和 App Runner 工作负载
- [load-balancing-api.md](references/load-balancing-api.md) - 负载均衡器、API Gateway 和 CloudFront
- [messaging-event-streaming.md](references/messaging-event-streaming.md) - SQS、SNS、EventBridge、Kinesis 和 MSK
- [resource-management.md](references/resource-management.md) - 资源清单和生命周期管理
- [cost-optimization.md](references/cost-optimization.md) - 成本节省和支出优化
- [capacity-planning.md](references/capacity-planning.md) - 容量分析和增长规划
- [security-compliance.md](references/security-compliance.md) - 安全配置和合规性监控
- [resource-ownership.md](references/resource-ownership.md) - 成本分配和所有权跟踪
- [events.md](references/events.md) - AWS AutoScaling、Health 和 CloudFormation 事件用于问题时间线分析
- [workload-detection.md](references/workload-detection.md) - 确定如何编排 EC2 实例（LB、ASG、ECS、EKS、Batch）
