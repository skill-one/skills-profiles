# AWS部署（CI/CD）

**最佳配合** [AWS MCP服务器](https://docs.aws.amazon.com/aws-mcp/) 使用，用于直接运行CLI命令和验证配置。所有指南同样适用于标准AWS CLI。

## 关键警告

**CodeConnections PENDING陷阱**：通过CLI/CloudFormation创建的连接会保持`PENDING`状态无限期——必须在AWS控制台完成OAuth。不存在仅API的路径。

**跨账户三重要求**：跨账户部署需要全部三个： (1) 授予目标账户的KMS密钥策略（使用密钥ID，而不是别名），(2) 目标账户的S3存储桶策略，(3) 具有信任策略的跨账户IAM角色。缺少任何一个都会导致模糊的`Access Denied`。

**CodeDeploy ApplicationStop使用上一个版本**：先前部署中损坏的停止脚本会阻止所有未来的部署。使停止脚本幂等（如果服务不存在则退出0）。使用`--ignore-application-stop-failures`解除阻止。

**CodeBuild VPC无NAT**：在无NAT网关的VPC子网中构建会无声地卡在`DOWNLOAD_SOURCE`。私有子网必须具有NAT网关或VPC端点。

**CodeConnections IAM**：API调用和IAM策略操作使用`codeconnections:`前缀。资源ARN必须完全匹配——新资源使用`codeconnections`前缀，现有资源可能使用`codestar-connections`前缀。如果有混合年龄的资源，请在资源中指定两者。

**UseConnection过于宽松**：`codeconnections:UseConnection`授予连接可以访问的所有仓库的访问权限。必须指定条件键（`codeconnections:FullRepositoryId`，`codeconnections:ProviderAction`，`codeconnections:BranchName`）将CodeBuild限制在所需的仓库。

## 这些服务如何组合

CodeConnections → CodeBuild → CodeDeploy，由CodePipeline编排。

| 层级 | 服务 | 角色 |
|-------|---------|------|
| 源代码 | CodeConnections | 认证到GitHub/GitLab/Bitbucket，交付代码 |
| 打包 | CodeArtifact | 私有包注册中心，从公共注册中心缓存依赖项 |
| 构建测试 | CodeBuild | 编译、测试、打包工件 |
| 部署 | CodeDeploy | 部署到EC2/ECS/Lambda，带流量切换策略 |
| 协调器 | CodePipeline | 链接阶段，管理转换，审批门 |

默认：V2管道类型带QUEUED执行模式。仅在执行完全独立时使用PARALLEL。

## 快速导航

| 您想... | 前往 |
|----------------|-------|
| 创建管道（V2，触发器，变量，模式） | [codepipeline.md](references/codepipeline.md) |
| 连接GitHub/GitLab/Bitbucket源 | [codeconnections.md](references/codeconnections.md) |
| 编写buildspec.yml / 配置构建 | [codebuild.md](references/codebuild.md) |
| 为构建设置私有包注册中心 | [codeartifact.md](references/codeartifact.md) |
| 配置部署策略（蓝绿，金丝雀） | [codedeploy.md](references/codedeploy.md) |
| 跨账户或跨区域部署 | [codepipeline.md](references/codepipeline.md) |
| 修复失败的管道、构建或部署 | [troubleshooting.md](references/troubleshooting.md) |

## 常见工作流

| 任务 | 操作 | 参考 |
|------|--------|-----------|
| 从GitHub到ECS的管道 | 创建连接 → CodeBuild Docker阶段 → CodeDeploy ECS蓝绿 | [codepipeline](references/codepipeline.md)，[codedeploy](references/codedeploy.md) |
| 管道在源处卡住 | 检查连接状态；如果PENDING，在AWS控制台完成OAuth | [troubleshooting](references/troubleshooting.md) |
| 构建超时 | 检查VPC/NAT，增加`timeoutInMinutes`，验证Docker特权模式 | [codebuild](references/codebuild.md) |
| 部署到另一个账户 | 配置KMS + S3存储桶策略 + 跨账户角色，将`RoleArn`添加到操作 | [codepipeline](references/codepipeline.md) |
| 回滚失败的部署 | 报警/失败时自动回滚；手动：`stop-deployment --auto-rollback-enabled` | [codedeploy](references/codedeploy.md) |
| Lambda金丝雀部署 | CodeBuild打包 → CodeDeploy Lambda带金丝雀流量切换 | [codedeploy](references/codedeploy.md) |

## 故障排除

| 错误/症状 | 原因 | 修复 |
|---------------|-------|-----|
| CodeBuild中的`YAML_FILE_ERROR` | buildspec中缺少或格式错误的`runtime-versions`（推荐用于标准镜像） | 在安装阶段添加`runtime-versions`块 |
| CodeDeploy上的`file already exists` | 无覆盖配置的重部署 | 设置`file_exists_behavior: OVERWRITE` |
| 管道触发器未触发 | 差异中的文件路径过滤器仅检查前100个文件 | 减少路径过滤器范围或合并更小的 |
| PARALLEL模式错误版本 | 事件和源操作之间的竞争 | 使用QUEUED模式以实现顺序一致性 |
| Docker: `Cannot connect to daemon` | 缺少特权模式 | 设置`privilegedMode: true` AND 在buildspec中启动dockerd |
| `CODEBUILD_CLONE_REF`权限错误 | CodeBuild角色缺少UseConnection | 将`codeconnections:UseConnection`添加到CodeBuild服务角色 |
| 部署从未完成 | 实例数量过高的最小健康主机 | 确保健康阈值 < 总实例数 |
| ECS部署卡住 | 新任务集上的健康检查失败 | 验证目标组健康检查路径/端口 |

## 安全

- 必须将密钥存储在Secrets Manager或Parameter Store中；通过CodeBuild `type: SECRETS_MANAGER`引用——绝对不能以明文形式嵌入buildspec
- 必须使用客户管理的KMS密钥进行跨账户工件加密（默认加密不支持跨账户）
- 应将CodeBuild/CodeDeploy服务角色限制为特定资源ARN；绝对不能对`s3:GetObject`或`kms:Decrypt`使用`*`
- 必须使用CodeConnections（而不是个人访问令牌）进行源连接；OAuth令牌无法自动轮换
- 参考[CodePipeline安全最佳实践](https://docs.aws.amazon.com/codepipeline/latest/userguide/security-best-practices.html)获取全面指导

## 未涵盖

| 主题 | 使用 |
|-------|-------------|
| CDK管道（`aws-cdk-lib/pipelines`） | `aws-cdk` |
| `sam deploy` / SAM CLI | `aws-serverless` |
| ECS服务部署配置（断路器，滚动参数） | `aws-containers` |
| GitHub Actions / GitLab CI | 第三方工具，未涵盖 |
