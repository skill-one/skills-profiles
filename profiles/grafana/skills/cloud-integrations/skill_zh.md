# Grafana Cloud 集成

Grafana Cloud 集成将云服务提供商的监控 API 连接到您的 Grafana 堆栈，而无需您自己运行导出器。托管的导出器会为您抓取云 API 并将指标推送到您的 Grafana Cloud 堆栈。

**支持的托管导出器：**
- **AWS CloudWatch** - 通过 YACE（Yet Another CloudWatch Exporter）抓取所有 CloudWatch 命名空间
- **Azure Monitor** - 通过 Azure Monitor API 抓取 Azure 资源指标
- **Confluent Cloud** - 通过 Confluent Metrics API 抓取 Kafka 集群指标
- **通用 HTTP 端点** - 身份验证后的任何 Prometheus 格式的 `/metrics` 端点

**AWS Firehose 接收器** - 消纳通过 Kinesis Firehose 推送的 CloudWatch 日志和指标流（近实时，延迟低于 API 抓取）。

---

## 第 1 步：导航到连接

在 Grafana Cloud 中：**连接 > 添加新连接**（或 `连接 > 云服务提供商`）。

可用路径：
- **AWS CloudWatch** - 托管导出器 + 可选 Firehose 接收器
- **Azure Monitor** - 托管导出器
- **Confluent Cloud** - 托管导出器
- **所有集成** - 包括 Linux、MySQL、Kubernetes 等的完整目录

---

## 第 2 步：AWS CloudWatch 集成

### 选项 A：托管导出器（轮询）

托管导出器每 60 秒抓取一次 CloudWatch API。延迟：约 1-5 分钟。

**必需的 IAM 权限（最小权限）：**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:GetMetricData",
        "cloudwatch:GetMetricStatistics",
        "cloudwatch:ListMetrics",
        "tag:GetResources",
        "ec2:DescribeInstances",
        "ec2:DescribeRegions"
      ],
      "Resource": "*"
    }
  ]
}
```

**设置步骤：**
1. 创建具有上述策略的 IAM 用户或角色
2. 生成访问密钥对（IAM 用户）或配置跨账户角色假设
3. 在 Grafana Cloud 中：连接 > AWS > 配置托管导出器
4. 输入：AWS 访问密钥 ID、密钥访问密钥、区域、要抓取的 CloudWatch 命名空间
5. Grafana 配置导出器并在 2-3 分钟内开始抓取

**支持的命名空间：** EC2、RDS、ELB/ALB、S3、Lambda、ECS、SQS、SNS、ElastiCache、
Kinesis、DynamoDB 以及 50 多个其他命名空间。

### 选项 B：AWS Firehose 接收器（流式传输）

通过 CloudWatch 指标流和 CloudWatch 日志订阅实现近实时指标和日志。

**架构：**
```
CloudWatch 指标流 → Kinesis Firehose → Grafana Cloud Firehose 接收器
CloudWatch 日志（订阅过滤器）→ Kinesis Firehose → Grafana Cloud Firehose 接收器
```

**设置：**

1. 在 Grafana Cloud 中：连接 > AWS > Firehose 接收器
2. Grafana 提供一个 HTTPS 端点 URL 和访问令牌
3. 在 AWS 中，创建一个 Kinesis Firehose 交付流：
   - 目标：HTTP 端点
   - 端点 URL：步骤 2 中的内容
   - 访问密钥：步骤 2 中的内容
   - 内容编码：GZIP
4. 创建一个指向 Firehose 流的 CloudWatch 指标流：
   - 输出格式：`OpenTelemetry 1.0`
   - 命名空间：选择或包含所有
5. 对于日志：添加一个指向 Firehose 流的 CloudWatch 日志订阅过滤器

**用于 Firehose 设置的 Terraform：**

```hcl
resource "aws_cloudwatch_metric_stream" "grafana_cloud" {
  name          = "grafana-cloud-metrics"
  role_arn      = aws_iam_role.firehose_role.arn
  firehose_arn  = aws_kinesis_firehose_delivery_stream.grafana.arn
  output_format = "opentelemetry1.0"

  # 可选地限制到特定命名空间
  # include_filter { namespace = "AWS/EC2" }
  # include_filter { namespace = "AWS/RDS" }
}

resource "aws_kinesis_firehose_delivery_stream" "grafana" {
  name        = "grafana-cloud-stream"
  destination = "http_endpoint"

  http_endpoint_configuration {
    url            = var.grafana_firehose_endpoint
    access_key     = var.grafana_firehose_access_key
    name           = "Grafana Cloud"
    content_encoding = "GZIP"

    s3_configuration {
      role_arn   = aws_iam_role.firehose_role.arn
      bucket_arn = aws_s3_bucket.firehose_backup.arn
    }
  }
}
```

---

## 第 3 步：Azure Monitor 集成

**必需的 Azure 权限：**

创建一个具有订阅上**监控读取者**角色的服务主体。

```bash
# 创建服务主体
az ad sp create-for-rbac --name grafana-cloud-monitoring \
  --role "Monitoring Reader" \
  --scopes /subscriptions/<SUBSCRIPTION_ID>

# 输出：appId（客户端 ID）、password（客户端密钥）、tenant
```

**在 Grafana Cloud 中的设置：**
1. 连接 > Azure > 配置托管导出器
2. 输入：租户 ID、客户端 ID、客户端密钥、订阅 ID
3. 选择要监控的资源类型（虚拟机、App Services、AKS、SQL 等）
4. 导出器在 2-3 分钟内开始抓取

**支持的资源类型：** 虚拟机、App Service 计划、AKS、Azure SQL、CosmosDB、存储账户、事件中心、服务总线、应用网关等。

---

## 第 4 步：Confluent Cloud 集成

**必需的 Confluent API 凭据：**

1. 在 Confluent Cloud 中：**环境 > API 密钥**（或组织级别的 Cloud API 密钥）
2. 创建一个 **指标 API 密钥**（不是 Kafka API 密钥）并分配 `MetricsViewer` 角色
3. 记录 API 密钥和密钥

**在 Grafana Cloud 中的设置：**
1. 连接 > Confluent > 配置托管导出器
2. 输入：Confluent API Key、API Secret、环境 ID、集群 ID
3. 导出器每 60 秒抓取一次 Confluent Metrics API

**可用指标：** 消费者延迟、代理请求速率、分区计数、复制延迟、活动控制器计数、集群级健康指标。

---

## 第 5 步：验证集成是否正常工作

```bash
# 在 Grafana Explore 中检查 — 查询集成的作业标签
# 对于 AWS：
{job="integrations/cloudwatch"}

# 对于 Azure：
{job="integrations/azure-monitor"}

# 检查指标到达（替换为您的堆栈的 Prometheus 端点）
curl -s -H "Authorization: Bearer <USER>:<API_KEY>" \
  "https://prometheus-prod-XX-XX-X.grafana.net/api/prom/api/v1/labels" | \
  jq '.data | map(select(startswith("aws_") or startswith("azure_")))'
```

集成状态也可见于：**连接 > [集成名称] > 状态**

**集成健康指标：**
- `Last successful scrape` - 应在最后 2 分钟内
- `Series count` - 应为非零且稳定
- `Error rate` - 应为 0%

---

## 第 6 步：预构建的仪表板和警报

每个集成会自动安装一组预配置的仪表板和警报规则。

**查找已安装的仪表板：**
- 仪表板 > 浏览 > 以集成命名的文件夹（例如 "AWS CloudWatch"）

**查找已安装的警报规则：**
- 警报 > 警报规则 > 按数据源或文件夹筛选

**在不丢失更新的情况下修改：**
1. 不要直接编辑配置的仪表板（它们可能在更新时被覆盖）
2. 复制仪表板（仪表板设置 > 保存为副本）
3. 编辑副本

---

## 第 7 步：解决集成失败问题

**托管导出器未接收数据：**

```bash
# 通过 Grafana Cloud API 检查集成状态
curl -s -H "Authorization: Bearer <STACK_ID>:<API_TOKEN>" \
  "https://integrations-api.grafana.net/api/v1/integrations" | \
  jq '.integrations[] | {name, status, lastScrapeTime, errorMessage}'
```

**常见错误：**

| 错误 | 原因 | 解决方法 |
|---|---|---|
| `AccessDenied` (AWS) | IAM 策略缺少权限 | 向 IAM 策略添加所需操作 |
| `AuthorizationFailed` (Azure) | 服务主体缺少角色 | 在订阅上授予监控读取者角色 |
| `401 Unauthorized` (Confluent) | 错误的 API 凭据 | 重新输入凭据；确认指标 API 密钥（不是 Kafka 密钥） |
| `No metrics found` | 选择错误的命名空间/资源类型 | 在集成设置中添加命名空间 |
| `Scrape timeout` | 网络限制 | 确保Grafana Cloud的IP可以访问云服务提供商 API |

**AWS 特定：CloudWatch API 速率限制**

CloudWatch GetMetricData 有速率限制。如果您有大量资源，请启用指标流（选项 B）而不是 API 轮询，以避免限流。

---

## 第 8 步：通过指标过滤降低成本

托管导出器默认抓取所有指标。过滤以减少序列数和成本。

**AWS - 选择特定命名空间：**
在集成设置中，从“所有命名空间”切换到特定命名空间（例如仅 EC2、RDS）。

**AWS - 按资源标签过滤：**
```yaml
# 在导出器配置中添加标签过滤器
discovery:
  - type: AWS/EC2
    filters:
      - key: Environment
        values: ["production"]
```

**Azure - 选择特定资源类型：**
仅启用您实际有仪表板的资源类型。

**使用 Adaptive Metrics 汇总未使用的标签维度：**
参考 `grafana-cloud/adaptive-metrics` 技能。

---

## 参考

- [Grafana Cloud 连接文档](https://grafana.com/docs/grafana-cloud/monitor-infrastructure/integrations/)
- [AWS CloudWatch 集成](https://grafana.com/docs/grafana-cloud/monitor-infrastructure/integrations/integration-reference/integration-cloudwatch/)
- [Azure Monitor 集成](https://grafana.com/docs/grafana-cloud/monitor-infrastructure/integrations/integration-reference/integration-azure/)
- [YACE（Yet Another CloudWatch Exporter）](https://github.com/nerdswords/yet-another-cloudwatch-exporter)
- [CloudWatch 指标流](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Metric-Streams.html)
