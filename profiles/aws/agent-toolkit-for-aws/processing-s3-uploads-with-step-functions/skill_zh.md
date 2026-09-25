# Step Functions 工作流：将 S3 上传路由到 Lambda 或 Fargate

## 概述

此技能使用 AWS CLI 部署一个事件驱动的流程。当文件上传到 S3 存储桶时，EventBridge 触发 Step Functions 状态机。状态机检查文件大小，并将处理路由到 Lambda 函数（文件 ≤ 6 MB）或 Fargate 任务（文件 > 6 MB）。

架构包括：

- 启用了 EventBridge 通知的 S3 存储桶
- 触发 Step Functions 的 S3 对象创建 EventBridge 规则
- 具有路由 Choice 状态的 Step Functions 状态机
- 用于处理小文件的 Lambda 函数
- 用于处理大文件的 ECS Fargate 任务
- 具有两个子网、互联网网关和安全组的 VPC
- 用于 Fargate 容器镜像的 ECR 仓库
- 用于 Lambda、Step Functions 和 ECS 任务的 IAM 角色范围

使用此技能的情况：

- 您需要根据文件大小使用不同的计算资源来处理 S3 上传
- 您需要一个可以处理大小文件的服务器less工作流
- 您需要使用 Lambda 和 Fargate 的 Step Functions 协调

不使用此技能的情况：

- 所有文件都足够小，可以直接使用 S3 → Lambda
- 您需要实时流处理（使用 Kinesis）
- 您不需要基于文件大小的路由

## 前置条件

1. **AWS CLI v2** — 已安装和配置。使用 `aws sts get-caller-identity` 进行验证。
2. **Python 3.12** — 用于 Lambda 函数运行时。
3. **Docker** — 用于构建和推送 Fargate 容器镜像。

## 参数

- bucket_name (必需): S3 存储桶的名称（全局唯一，小写，3-63 个字符）
- region (必需): 所有资源的 AWS 区域
- ecr_repo_name (必需): ECR 仓库的名称
- state_machine_name (必需): Step Functions 状态机的名称
- kms_key_arn (可选): 用于 CloudWatch 日志加密的 KMS 密钥的 ARN。如果未提供，请使用 `aws kms create-key --description "Key for CloudWatch Logs encryption" --region {region}` 创建一个。

参数获取约束：

- 您必须在单个提示中 upfront 请求所有必需参数
- 您必须支持多种输入方法（直接输入、文件路径、URL）
- 您必须在继续之前确认已成功获取所有参数
- 您必须验证 bucket_name 是否遵循 S3 命名规则

## 步骤

### 步骤 0：验证依赖项

约束：

- 您必须验证以下工具可用：aws-cli、python3 (3.12+)、docker
- 您必须使用清晰的提示告知用户任何缺失的工具
- 您必须询问用户是否希望在缺失工具的情况下继续
- 您必须尊重客户在任何时刻中止的决定
- 您必须向客户解释正在执行哪个步骤、为什么以及正在调用哪个工具

### 步骤 1：获取 AWS 账户 ID

约束：

- 您必须使用 `aws sts get-caller-identity --query 'Account' --output text` 获取账户 ID
- 您必须将结果存储为 {account_id}，用于后续所有步骤
- 如果凭证未配置，则必须中止

### 步骤 2：获取默认 VPC 和网络

约束：

- 您必须使用以下命令获取默认 VPC ID：
  `aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text --region {region}`
- 如果不存在默认 VPC，请告知用户他们必须使用 `aws ec2 create-default-vpc --region {region}` 创建一个，或手动提供 VPC ID
- 您必须从默认 VPC 获取两个子网 ID：
  `aws ec2 describe-subnets --filters Name=vpc-id,Values={vpc_id} --query 'Subnets[0:2].SubnetId' --output text --region {region}`
- 您必须在默认 VPC 中创建一个安全组：
  `aws ec2 create-security-group --group-name fargate-sg --description "用于 Fargate 任务的 安全组" --vpc-id {vpc_id} --region {region}`
- 您必须配置安全组出站规则，仅允许 HTTPS 和 DNS 出站。首先撤销默认的允许所有出站规则：
  `aws ec2 revoke-security-group-egress --group-id {sg_id} --ip-permissions IpProtocol=-1,IpRanges='[{CidrIp=0.0.0.0/0}]' --region {region}`
  然后添加范围规则：
  `aws ec2 authorize-security-group-egress --group-id {sg_id} --protocol tcp --port 443 --cidr 0.0.0.0/0 --region {region}` 和
  `aws ec2 authorize-security-group-egress --group-id {sg_id} --protocol udp --port 53 --cidr 0.0.0.0/0 --region {region}`
- 您必须推荐为生产工作负载配置 S3 和 CloudWatch Logs 的 VPC 端点，以避免互联网路由流量并消除对广泛出站规则的需求
- 您必须捕获 {vpc_id}、{subnet1_id}、{subnet2_id} 和 {sg_id}，用于后续步骤

### 步骤 3：创建 ECR 仓库

约束：

- 您必须使用以下命令创建仓库：
  `aws ecr create-repository --repository-name {ecr_repo_name} --region {region}`
- 您必须从响应中捕获 repositoryUri

### 步骤 4：构建和推送容器镜像

约束：

- 您必须通过运行 `docker --version` 验证 Docker 是否已安装。如果 Docker 未安装，请指示用户从 https://docs.docker.com/get-docker/ 安装，并在可用之前中止
- 您必须使用 ECR 对 Docker 进行身份验证：
  `aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {account_id}.dkr.ecr.{region}.amazonaws.com`
- Dockerfile 和处理器代码位于 `scripts/Dockerfile` 和 `scripts/fargate_processor.py`
- 您必须从脚本目录构建和推送镜像：

  ```
  cd scripts
  docker build --platform linux/amd64 -t {ecr_repo_name} .
  docker tag {ecr_repo_name}:latest {account_id}.dkr.ecr.{region}.amazonaws.com/{ecr_repo_name}:latest
  docker push {account_id}.dkr.ecr.{region}.amazonaws.com/{ecr_repo_name}:latest
  cd ..
  ```

### 步骤 5：创建 IAM 角色

遵循 `references/iam-roles.md` 中的详细说明来创建所有 IAM 角色（Lambda、ECS 任务执行、ECS 任务、Step Functions 和 EventBridge 角色）。

- 您必须等待至少 10 秒钟以进行 IAM 角色传播

### 步骤 6：创建 Lambda 函数

约束：

- 函数代码位于 `scripts/lambda_function.py`
- 您必须在打包和创建函数之前位于技能根目录
- 您必须使用以下命令打包：
  `python3 -c "import zipfile,io; z=io.BytesIO(); f=zipfile.ZipFile(z,'w'); f.writestr('lambda_function.py', open('scripts/lambda_function.py').read()); f.close(); open('/tmp/lambda_function.zip','wb').write(z.getvalue())"`
- 您必须使用以下命令创建函数：

  ```
  aws lambda create-function \
      --function-name sfn-file-processor \
      --runtime python3.12 \
      --handler lambda_function.lambda_handler \
      --role arn:aws:iam::{account_id}:role/sfn-lambda-role \
      --zip-file fileb:///tmp/lambda_function.zip \
      --timeout 60 \
      --architectures x86_64 \
      --region {region}
  ```

- 您必须使用以下命令验证函数是否已创建：
  `aws lambda get-function --function-name sfn-file-processor --region {region}`

### 步骤 7：创建 CloudWatch 日志组

约束：

- 您必须为 Fargate 创建日志组：
  `aws logs create-log-group --log-group-name /StepFunctionFargateTask --region {region}`
- 您必须使用 KMS 密钥对日志组进行加密：
  `aws logs associate-kms-key --log-group-name /StepFunctionFargateTask --kms-key-arn {kms_key_arn} --region {region}`

### 步骤 8：创建 ECS 集群和任务定义

遵循 `references/ecs-task-definition.md` 中的详细说明来创建 ECS 集群并注册 Fargate 任务定义。

- 您必须从响应中捕获任务定义 ARN

### 步骤 9：创建 S3 存储桶并配置 EventBridge 通知

约束：

- 您必须使用以下命令创建存储桶：
  `aws s3api create-bucket --bucket {bucket_name} --region {region} --create-bucket-configuration LocationConstraint={region}`
- 如果区域是 us-east-1，则必须不包含 `--create-bucket-configuration`
- 您必须启用存储桶的 EventBridge 通知：
  `aws s3api put-bucket-notification-configuration --bucket {bucket_name} --notification-configuration '{"EventBridgeConfiguration": {}}' --region {region}`
- 您必须启用存储桶的默认加密：
  `aws s3api put-bucket-encryption --bucket {bucket_name} --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"aws:kms"}}]}' --region {region}`

### 步骤 10：创建 Step Functions 状态机

约束：

- 状态机定义位于 `scripts/statemachine.asl.json`
- 您必须创建一个工作副本并替换所有占位符：

  ```
  sed -e 's|${LambdaFunction}|arn:aws:lambda:{region}:{account_id}:function:sfn-file-processor|g' \
      -e 's|${Cluster}|arn:aws:ecs:{region}:{account_id}:cluster/sfn-cluster|g' \
      -e 's|${TaskDefinition}|{task_definition_arn}|g' \
      -e 's|${Subnet1}|{subnet1_id}|g' \
      -e 's|${Subnet2}|{subnet2_id}|g' \
      -e 's|${SecurityGroup}|{sg_id}|g' \
      scripts/statemachine.asl.json > /tmp/statemachine.asl.json
  ```

- 您必须使用以下命令创建状态机：

  ```
  aws stepfunctions create-state-machine \
      --name {state_machine_name} \
      --definition file:///tmp/statemachine.asl.json \
      --role-arn arn:aws:iam::{account_id}:role/sfn-state-machine-role \
      --type STANDARD \
      --region {region}
  ```

- 您必须从响应中捕获 stateMachineArn

### 步骤 11：创建 EventBridge 规则

约束：

- 您必须创建一个 EventBridge 规则以在 S3 对象创建时触发：

  ```
  aws events put-rule \
      --name s3-to-stepfunctions \
      --event-pattern '{
        "source": ["aws.s3"],
        "detail-type": ["Object Created"],
        "detail": {
          "bucket": {
            "name": ["{bucket_name}"]
          }
        }
      }' \
      --region {region}
  ```

- 您必须将状态机添加为目标：

  ```
  aws events put-targets \
      --rule s3-to-stepfunctions \
      --targets '[{
        "Id": "StepFunctionsTarget",
        "Arn": "{state_machine_arn}",
        "RoleArn": "arn:aws:iam::{account_id}:role/sfn-eventbridge-role"
      }]' \
      --region {region}
  ```

### 步骤 12：配置监控

约束：

- 您必须为失败的 EventBridge 调用创建死信队列：
  `aws sqs create-queue --queue-name s3-to-stepfunctions-dlq --region {region}`
- 您必须更新 EventBridge 目标以附加死信队列：

  ```
  aws events put-targets \
      --rule s3-to-stepfunctions \
      --targets '[{
        "Id": "StepFunctionsTarget",
        "Arn": "{state_machine_arn}",
        "RoleArn": "arn:aws:iam::{account_id}:role/sfn-eventbridge-role",
        "DeadLetterConfig": {
          "Arn": "arn:aws:sqs:{region}:{account_id}:s3-to-stepfunctions-dlq"
        }
      }]' \
      --region {region}
  ```

- 您必须为 Step Functions 执行失败创建 CloudWatch 报警：
  `aws cloudwatch put-metric-alarm --alarm-name sfn-execution-failures --metric-name ExecutionsFailed --namespace AWS/States --statistic Sum --period 300 --threshold 1 --comparison-operator GreaterThanOrEqualToThreshold --evaluation-periods 1 --dimensions Name=StateMachineArn,Value={state_machine_arn} --region {region}`

### 步骤 13：验证

约束：

- 您必须使用一个小于 6 MB 的小文件来验证 Lambda 处理：

  ```
  echo 'test data' > /tmp/small-file.txt
  aws s3 cp /tmp/small-file.txt s3://{bucket_name}/small-file.txt --region {region}
  ```

- 您必须等待 15 秒然后检查 Step Functions 执行：
  `aws stepfunctions list-executions --state-machine-arn {state_machine_arn} --region {region}`
- 您必须验证执行成功并路由到 Lambda
- 您必须提供所有创建资源的摘要，包括：VPC ID、子网 ID、安全组 ID、ECR 仓库 URI、ECS 集群 ARN、任务定义 ARN、Lambda 函数 ARN、状态机 ARN、存储桶名称和 EventBridge 规则名称

## 故障排除

### EventBridge 规则未触发

- 验证存储桶上是否启用了 EventBridge 通知：`aws s3api get-bucket-notification-configuration --bucket {bucket_name}`
- 验证规则是否存在：`aws events describe-rule --name s3-to-stepfunctions --region {region}`
- 检查目标是否具有正确的状态机 ARN 和角色

### Step Functions 在 Fargate 任务执行失败

- 验证 ECR 中是否存在容器镜像：`aws ecr describe-images --repository-name {ecr_repo_name} --region {region}`
- 检查子网是否具有互联网访问权限（带有 IGW 的路由表）
- 验证安全组允许出站流量
- 检查 CloudWatch Logs 中的 `/StepFunctionFargateTask`

### Lambda 调用失败

- 检查 CloudWatch Logs：`aws logs tail /aws/lambda/sfn-file-processor --region {region}`
- 验证 Step Functions 角色具有 `lambda:InvokeFunction` 权限

### IAM PassRole 错误

- Step Functions 角色必须对 ECS 执行角色和任务角色 ARN 都具有 `iam:PassRole` 权限

### Fargate 任务卡在 PROVISIONING 状态

- 验证子网是否启用了自动分配公网 IP
- 验证互联网网关是否已连接并且路由表具有 0.0.0.0/0 路由

## 安全注意事项

- 具有公网 IP 的 Fargate 任务暴露于互联网。撤销默认的允许所有出站规则并配置范围出站：`aws ec2 revoke-security-group-egress --group-id {sg_id} --ip-permissions IpProtocol=-1,IpRanges='[{CidrIp=0.0.0.0/0}]` 然后添加 `aws ec2 authorize-security-group-egress --group-id {sg_id} --protocol tcp --port 443 --cidr 0.0.0.0/0` 和 `aws ec2 authorize-security-group-egress --group-id {sg_id} --protocol udp --port 53 --cidr 0.0.0.0/0`。对于生产环境，请考虑使用 VPC 端点而不是互联网路由流量来访问 S3 和 CloudWatch Logs。
- 在将容器镜像推送到 ECR 之前扫描漏洞。使用以下命令启用 ECR 图像扫描：`aws ecr put-image-scanning-configuration --repository-name {ecr_repo_name} --image-scanning-configuration scanOnPush=true --region {region}`
- 使用 IAM 角色进行凭证 — 不要在容器代码中硬编码访问密钥。
- 为 S3 存储桶启用存储加密：`aws s3api put-bucket-encryption --bucket {bucket_name} --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"aws:kms"}}]}'`
- 为 Fargate 容器日志启用 CloudWatch Logs 加密：`aws logs associate-kms-key --log-group-name /StepFunctionFargateTask --kms-key-arn <KMS_KEY_ARN>`
- 在 EventBridge 规则上为失败调用配置死信队列
- 为 Step Functions 执行失败设置 CloudWatch 报警以实现运营可见性

## 版本信息

- **AWS CLI**: 2.x
- **Python 运行时**: 3.12
- **最后验证**: 2026-04-27

## 其他资源

- [Step Functions 开发者指南](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html)
- [EventBridge S3 事件](https://docs.aws.amazon.com/AmazonS3/latest/userguide/EventBridge.html)
- [Fargate 任务定义](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html)
- [ECR 推送镜像](https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html)
- [Step Functions Fargate 集成](https://docs.aws.amazon.com/step-functions/latest/dg/connect-ecs.html)
