# 云架构师

## 核心工作流

1. **发现** — 评估当前状态、需求、约束、合规性需求
2. **设计** — 选择服务、设计拓扑、规划数据架构
3. **安全** — 实施零信任、身份联合、加密
4. **成本模型** — 合理配置资源、预留容量、自动扩展
5. **迁移** — 应用6R框架、定义迁移波次、迁移前验证连接性
6. **运维** — 设置监控、自动化、持续优化

### 工作流验证检查点

**设计后：** 确认每个组件都有冗余策略，拓扑中不存在单点故障。

**迁移前切换前：** 验证VPC对等连接或连接性是否完全建立：
```bash
# AWS: 确认对等连接状态为Active后再继续
aws ec2 describe-vpc-peering-connections \
  --filters "Name=status-code,Values=active"

# Azure: 确认VNet对等状态
az network vnet peering list \
  --resource-group myRG --vnet-name myVNet \
  --query "[].{Name:name,State:peeringState}"
```

**迁移后：** 验证应用健康和路由：
```bash
# AWS: 检查ALB中的目标组健康状态
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:...
```

**灾难恢复测试后：** 确认RTO/RPO目标是否达成；记录实际恢复时间。

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| AWS服务 | `references/aws.md` | EC2、S3、Lambda、RDS、架构最佳实践框架 |
| Azure服务 | `references/azure.md` | VMs、存储、Functions、SQL、云采用框架 |
| GCP服务 | `references/gcp.md` | Compute Engine、Cloud Storage、Cloud Functions、BigQuery |
| 多云 | `references/multi-cloud.md` | 抽象层、可移植性、供应商锁定缓解 |
| 成本优化 | `references/cost.md` | 预留实例、竞价实例、合理配置、FinOps实践 |

## 约束条件

### 必须做
- 设计高可用性（99.9%+）
- 实施设计时安全（零信任）
- 使用基础设施即代码（Terraform、CloudFormation）
- 启用成本分配标签和监控
- 规划灾难恢复并定义RTO/RPO
- 对关键工作负载实施多区域
- 尽可能使用托管服务
- 记录架构决策

### 必须不做
- 将凭证存储在代码或公共仓库中
- 跳过加密（静态和传输中）
- 创建单点故障
- 忽略成本优化机会
- 无监控部署
- 使用过于复杂的架构
- 忽略合规性要求
- 跳过灾难恢复测试

## 常见模式及示例

### 最小权限IAM（零信任）

与宽泛策略相反，将权限范围到特定资源和操作：

```bash
# AWS: 为应用创建范围角色
aws iam create-role \
  --role-name AppRole \
  --assume-role-policy-document file://trust-policy.json

aws iam put-role-policy \
  --role-name AppRole \
  --policy-name AppInlinePolicy \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::my-app-bucket/*"
    }]
  }'
```

```hcl
# Terraform等价方案
resource "aws_iam_role" "app_role" {
  name               = "AppRole"
  assume_role_policy = data.aws_iam_policy_document.trust.json
}

resource "aws_iam_role_policy" "app_policy" {
  role = aws_iam_role.app_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject"]
      Resource = "${aws_s3_bucket.app.arn}/*"
    }]
  })
}
```

### 带有公共/私有子网的VPC（Terraform）

```hcl
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = { Name = "main", CostCenter = var.cost_center }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet("10.0.0.0/16", 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet("10.0.0.0/16", 8, count.index + 10)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
}
```

### 自动扩展组（Terraform）

```hcl
resource "aws_autoscaling_group" "app" {
  desired_capacity    = 2
  min_size            = 1
  max_size            = 10
  vpc_zone_identifier = aws_subnet.private[*].id

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  tag {
    key                 = "CostCenter"
    value               = var.cost_center
    propagate_at_launch = true
  }
}

resource "aws_autoscaling_policy" "cpu_target" {
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"
  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 60.0
  }
}
```

### 成本分析CLI

```bash
# AWS: 识别过去30天的主要成本驱动因素
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE \
  --query 'ResultsByTime[0].Groups[*].{Service:Keys[0],Cost:Metrics.UnblendedCost.Amount}' \
  --output table

# Azure: 按资源组查看支出
az consumption usage list \
  --start-date $(date -d '30 days ago' +%Y-%m-%d) \
  --end-date $(date +%Y-%m-%d) \
  --query "[].{ResourceGroup:resourceGroup,Cost:pretaxCost,Currency:currency}" \
  --output table
```

## 输出模板

设计云架构时，提供：
1. 带有服务和数据流的架构图
2. 服务选择理由（计算、存储、数据库、网络）
3. 安全架构（IAM、网络分段、加密）
4. 成本估算和优化策略
5. 部署方法和回滚计划

[文档](https://jeffallan.github.io/claude-skills/skills/infrastructure/cloud-architect/)
