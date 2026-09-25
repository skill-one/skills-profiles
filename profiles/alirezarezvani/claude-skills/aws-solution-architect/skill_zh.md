# AWS 解决方案架构师

为初创公司设计可扩展、高性价比的 AWS 架构，并提供基础设施即代码模板。

---

## 工作流程

### 第 1 步：收集需求

收集应用程序规格：

```
- 应用程序类型（Web 应用、移动后端、数据管道、SaaS）
- 预期用户数和每秒请求数
- 预算限制（月度支出上限）
- 团队规模和 AWS 经验水平
- 合规性要求（GDPR、HIPAA、SOC 2）
- 可用性要求（SLA、RPO/RTO）
```

### 第 2 步：设计架构

运行架构设计器以获取模式推荐：

```bash
python scripts/architecture_designer.py --input requirements.json
```

**示例输出：**

```json
{
  "recommended_pattern": "serverless_web",
  "service_stack": ["S3", "CloudFront", "API Gateway", "Lambda", "DynamoDB", "Cognito"],
  "estimated_monthly_cost_usd": 35,
  "pros": ["低运维开销", "按量付费", "自动扩展"],
  "cons": ["冷启动", "Lambda 15 分钟限制", "最终一致性"]
}
```

从推荐模式中选择：
- **无服务器 Web**：S3 + CloudFront + API Gateway + Lambda + DynamoDB
- **事件驱动微服务**：EventBridge + Lambda + SQS + Step Functions
- **三层架构**：ALB + ECS Fargate + Aurora + ElastiCache
- **GraphQL 后端**：AppSync + Lambda + DynamoDB + Cognito

有关详细模式规范的说明，请参阅 `references/architecture_patterns.md`。

**验证检查点：** 在继续第 3 步之前，确认推荐模式是否与团队的运维成熟度和合规性要求相匹配。

### 第 3 步：生成 IaC 模板

为所选模式创建基础设施即代码：

```bash
# 无服务器堆栈（CloudFormation）
python scripts/serverless_stack.py --app-name my-app --region us-east-1
```

**示例 CloudFormation YAML 输出（核心无服务器资源）：**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Parameters:
  AppName:
    Type: String
    Default: my-app

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: nodejs20.x
      MemorySize: 512
      Timeout: 30
      Environment:
        Variables:
          TABLE_NAME: !Ref DataTable
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref DataTable
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY

  DataTable:
    Type: AWS::DynamoDB::Table
    Properties:
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE
```

> 完整模板，包括 API Gateway、Cognito、IAM 角色和 CloudWatch 日志，由 `serverless_stack.py` 生成，并在 `references/architecture_patterns.md` 中提供。

**示例 CDK TypeScript 片段（三层模式）：**

```typescript
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as rds from 'aws-cdk-lib/aws-rds';

const vpc = new ec2.Vpc(this, 'AppVpc', { maxAzs: 2 });

const cluster = new ecs.Cluster(this, 'AppCluster', { vpc });

const db = new rds.ServerlessCluster(this, 'AppDb', {
  engine: rds.DatabaseClusterEngine.auroraPostgres({
    version: rds.AuroraPostgresEngineVersion.VER_15_2,
  }),
  vpc,
  scaling: { minCapacity: 0.5, maxCapacity: 4 },
});
```

### 第 4 步：审查成本

分析估计成本和优化机会：

```bash
python scripts/cost_optimizer.py --resources current_setup.json --monthly-spend 2000
```

**示例输出：**

```json
{
  "current_monthly_usd": 2000,
  "recommendations": [
    { "action": "调整 RDS db.r5.2xlarge 至 db.r5.large", "savings_usd": 420, "priority": "高" },
    { "action": "购买 1 年计算节省计划，利用率 40%”，"savings_usd": 310, "priority": "高" },
    { "action": "将 S3 对象 >90 天迁移至 Glacier Instant Retrieval", "savings_usd": 85, "priority": "中" }
  ],
  "total_potential_savings_usd": 815
}
```

输出包括：
- 按服务划分的月度成本明细
- 调整建议
- 节省计划机会
- 潜在月度节省

### 第 5 步：部署

部署生成的基础设施：

```bash
# CloudFormation
aws cloudformation create-stack \
  --stack-name my-app-stack \
  --template-body file://template.yaml \
  --capabilities CAPABILITY_IAM

# CDK
cdk deploy

# Terraform
terraform init && terraform apply
```

### 第 6 步：验证和处理故障

验证部署并设置监控：

```bash
# 检查堆栈状态
aws cloudformation describe-stacks --stack-name my-app-stack

# 设置 CloudWatch 闹钟
aws cloudwatch put-metric-alarm --alarm-name high-errors ...
```

**如果堆栈创建失败：**

1. 检查失败原因：
   ```bash
   aws cloudformation describe-stack-events \
     --stack-name my-app-stack \
     --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`]'
   ```
2. 查看 Lambda 或 ECS 错误的 CloudWatch 日志。
3. 修复模板或资源配置。
4. 在重试前删除失败堆栈：
   ```bash
   aws cloudformation delete-stack --stack-name my-app-stack
   # 等待删除
   aws cloudformation wait stack-delete-complete --stack-name my-app-stack
   # 重新部署
   aws cloudformation create-stack ...
   ```

**常见失败原因：**
- IAM 权限错误 → 验证 `--capabilities CAPABILITY_IAM` 和角色信任策略
- 资源限制超出 → 通过服务配额控制台申请配额增加
- 无效模板语法 → 在部署前运行 `aws cloudformation validate-template --template-body file://template.yaml`

---

## 工具

### architecture_designer.py

根据需求生成架构模式。

```bash
python scripts/architecture_designer.py --input requirements.json --output design.json
```

**输入：** 包含应用类型、规模、预算、合规性需求的 JSON
**输出：** 推荐模式、服务堆栈、成本估计、优缺点

### serverless_stack.py

创建无服务器 CloudFormation 模板。

```bash
python scripts/serverless_stack.py --app-name my-app --region us-east-1
```

**输出：** 生产就绪的 CloudFormation YAML，包含：
- API Gateway + Lambda
- DynamoDB 表
- Cognito 用户池
- 最小权限 IAM 角色
- CloudWatch 日志

### cost_optimizer.py

分析成本并推荐优化。

```bash
python scripts/cost_optimizer.py --resources inventory.json --monthly-spend 5000
```

**输出：** 建议包括：
- 空闲资源清理
- 实例调整大小
- 保留容量购买
- 存储层迁移
- NAT 网关替代方案

---

## 快速入门

### MVP 架构（< $100/月）

```
询问："为具有 1000 用户的移动应用设计无服务器 MVP 后端"

结果：
- Lambda + API Gateway 用于 API
- DynamoDB 按量付费用于数据
- Cognito 用于身份验证
- S3 + CloudFront 用于静态资源
- 估计：$20-50/月
```

### 扩展架构（$500-2000/月）

```
询问："为具有 50k 用户的 SaaS 平台设计可扩展架构"

结果：
- ECS Fargate 用于容器化 API
- Aurora 无服务器用于关系数据
- ElastiCache 用于会话缓存
- CloudFront 用于 CDN
- CodePipeline 用于 CI/CD
- 多 AZ 部署
```

### 成本优化

```
询问："优化我的 AWS 设置以降低成本 30%。当前支出：$3000/月"

提供：当前资源清单（EC2、RDS、S3 等）

结果：
- 空闲资源识别
- 调整大小建议
- 节省计划分析
- 存储生命周期策略
- 目标节省：$900/月
```

### IaC 生成

```
询问："为三层 Web 应用生成 CloudFormation，支持自动扩展"

结果：
- 带有公网/私网的 VPC
- ALB 带 HTTPS
- ECS Fargate 带自动扩展
- Aurora 带读副本
- 安全组 IAM 角色
```

---

## 输入需求

为架构设计提供以下详细信息：

| 需求 | 描述 | 示例 |
|-------------|-------------|---------|
| 应用程序类型 | 你正在构建什么 | SaaS 平台、移动后端 |
| 预期规模 | 用户数、每秒请求数 | 10k 用户、100 RPS |
| 预算 | AWS 月度上限 | $500/月最大 |
| 团队背景 | 规模、AWS 经验 | 3 名开发人员、中级 |
| 合规性 | 监管需求 | HIPAA、GDPR、SOC 2 |
| 可用性 | 上市要求 | 99.9% SLA、1 小时 RPO |

**JSON 格式：**

```json
{
  "application_type": "saas_platform",
  "expected_users": 10000,
  "requests_per_second": 100,
  "budget_monthly_usd": 500,
  "team_size": 3,
  "aws_experience": "intermediate",
  "compliance": ["SOC2"],
  "availability_sla": "99.9%"
}
```

---

## 输出格式

### 架构设计

- 带有合理性的模式推荐
- 服务堆栈图（ASCII）
- 月度成本估计和权衡

### IaC 模板

- **CloudFormation YAML**：生产就绪的 SAM/CFN 模板
- **CDK TypeScript**：类型安全的基建代码
- **Terraform HCL**：多云兼容配置

### 成本分析

- 按服务划分的当前支出明细和优化建议
- 优先行动列表（高/中/低）和实施清单

---

## 参考文档

| 文档 | 内容 |
|----------|----------|
| `references/architecture_patterns.md` | 6 种模式：无服务器、微服务、三层、数据处理、GraphQL、多区域 |
| `references/service_selection.md` | 计算、数据库、存储、消息的决策矩阵 |
| `references/best_practices.md` | 无服务器设计、成本优化、安全加固、可扩展性 |
