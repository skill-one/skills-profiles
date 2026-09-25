# 云成本优化

跨 AWS、Azure、GCP 和 OCI 优化云成本的策略和模式。

## 目的

实施系统化的成本优化策略，以降低云支出，同时保持性能和可靠性。

## 适用场景

- 降低云支出
- 合理配置资源
- 实施成本治理
- 优化多云成本
- 满足预算限制

## 成本优化框架

### 1. 可见性

- 实施成本分配标签
- 使用云成本管理工具
- 设置预算警报
- 创建成本仪表板

### 2. 合理配置资源

- 分析资源利用率
- 缩小超额配置的资源
- 使用自动扩展
- 删除闲置资源

### 3. 定价模型

- 使用预留容量
- 利用竞价/可中断实例
- 实施节省计划
- 使用承诺使用折扣

### 4. 架构优化

- 使用托管服务
- 实施缓存
- 优化数据传输
- 使用生命周期策略

## AWS 成本优化

### 预留实例

```
节省：相比按需付费可节省 30-72%
期限：1 年或 3 年
支付方式：全部/部分/无预付费
灵活性：标准或可转换
```

### 节省计划

```
计算节省计划：可节省 66%
EC2 实例节省计划：可节省 72%
适用范围：EC2、Fargate、Lambda
跨：实例系列、区域、操作系统
```

### 竞价实例

```
节省：相比按需付费可节省高达 90%
适用场景：批处理任务、CI/CD、无状态工作负载
风险：2 分钟中断通知
策略：与按需付费混合使用以提高弹性
```

### S3 成本优化

```hcl
resource "aws_s3_bucket_lifecycle_configuration" "example" {
  bucket = aws_s3_bucket.example.id

  rule {
    id     = "transition-to-ia"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}
```

## Azure 成本优化

### 预留虚拟机实例

- 1 年或 3 年期限
- 可节省高达 72%
- 灵活配置
- 可交换

### Azure 混合使用权益

- 使用现有的 Windows Server 许可证
- 使用 RI 可节省高达 80%
- 适用于 Windows 和 SQL Server

### Azure Advisor 建议

- 合理配置虚拟机
- 删除未使用的资源
- 使用预留容量
- 优化存储

## GCP 成本优化

### 承诺使用折扣

- 1 年或 3 年承诺
- 可节省高达 57%
- 适用范围：vCPUs 和内存
- 基于资源或基于支出

### 持续使用折扣

- 自动折扣
- 运行实例可节省高达 30%
- 无需承诺
- 适用范围：Compute Engine、GKE

### 可中断虚拟机

- 可节省高达 80%
- 最大运行时间 24 小时
- 适用于批处理工作负载

## OCI 成本优化

### 灵活形状

- 独立扩展 OCPUs 和内存
- 使实例大小与工作负载需求匹配
- 减少固定虚拟机形状的浪费容量

### 承诺和预算

- 使用年度承诺以实现可预测支出
- 设置包含警报的区间级预算
- 使用 OCI 成本分析跟踪月度预测

### 可中断容量

- 使用可中断实例处理批处理和短暂工作负载
- 保持具有中断容忍性的自动扩展组
- 与标准容量混合使用以支持关键服务

## 标签策略

### AWS 标签

```hcl
locals {
  common_tags = {
    Environment = "production"
    Project     = "my-project"
    CostCenter  = "engineering"
    Owner       = "team@example.com"
    ManagedBy   = "terraform"
  }
}

resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t3.medium"

  tags = merge(
    local.common_tags,
    {
      Name = "web-server"
    }
  )
}
```

**参考：** 查看 `references/tagging-standards.md`

## 成本监控

### 预算警报

```hcl
# AWS 预算
resource "aws_budgets_budget" "monthly" {
  name              = "monthly-budget"
  budget_type       = "COST"
  limit_amount      = "1000"
  limit_unit        = "USD"
  time_period_start = "2024-01-01_00:00"
  time_unit         = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = ["team@example.com"]
  }
}
```

### 成本异常检测

- AWS 成本异常检测
- Azure 成本管理警报
- GCP 预算警报
- OCI 预算和成本分析

## 架构模式

### 模式 1：无服务器优先

- 使用 Lambda/Functions 处理事件驱动
- 仅按执行时间付费
- 包含自动扩展
- 无闲置成本

### 模式 2：合理配置数据库

```
开发：t3.small RDS
测试：t3.large RDS
生产：r6g.2xlarge RDS 带读副本
```

### 模式 3：多层存储

```
热数据：S3 Standard
温数据：S3 Standard-IA（30 天）
冷数据：S3 Glacier（90 天）
归档：S3 Deep Archive（365 天）
```

### 模式 4：自动扩展

```hcl
resource "aws_autoscaling_policy" "scale_up" {
  name                   = "scale-up"
  scaling_adjustment     = 2
  adjustment_type        = "ChangeInCapacity"
  cooldown              = 300
  autoscaling_group_name = aws_autoscaling_group.main.name
}

resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "60"
  statistic           = "Average"
  threshold           = "80"
  alarm_actions       = [aws_autoscaling_policy.scale_up.arn]
}
```

## 成本优化检查清单

- [ ] 实施成本分配标签
- [ ] 删除未使用的资源（EBS、EIPs、快照）
- [ ] 根据利用率合理配置实例
- [ ] 使用预留容量处理稳定工作负载
- [ ] 实施自动扩展
- [ ] 优化存储类别
- [ ] 使用生命周期策略
- [ ] 启用成本异常检测
- [ ] 设置预算警报
- [ ] 每周审查成本
- [ ] 使用竞价/可中断实例
- [ ] 优化数据传输成本
- [ ] 实施缓存层
- [ ] 使用托管服务
- [ ] 持续监控和优化

## 工具

- **AWS：** Cost Explorer、Cost Anomaly Detection、Compute Optimizer
- **Azure：** Cost Management、Advisor
- **GCP：** Cost Management、Recommender
- **OCI：** Cost Analysis、Budgets、Cloud Advisor
- **多云：** CloudHealth、Cloudability、Kubecost

## 相关技能

- `terraform-module-library` - 用于资源配置
- `multi-cloud-architecture` - 用于云选择
