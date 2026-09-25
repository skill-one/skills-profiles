# 多账户弹性中心 v2 设置

## 概述

针对弹性中心 v2 进行配置，以便从中心账户评估多个 AWS 账户中的服务。本技能中使用的所有 CLI 命令都使用 **`aws resiliencehubv2`** 命名空间——弹性中心 **v2** API 界面——这与传统的 `aws resiliencehub` (v1) 命令（`service: [resiliencehub, ...]` 元数据标记服务系列，而不是 CLI 命名空间）是不同的。弹性中心 v2 支持两种互补的多账户机制：(1) **AWS Organizations 集成**——管理账户启用受信任访问，创建服务关联角色，并指定一个 **委托管理员** 账户用于组织范围的策略管理和可见性；(2) **按服务跨账户权限模型**——中心账户中的调用者角色在成员账户中假设跨账户角色，用于按服务资源发现。本技能配置 (2)； Organizations 集成 (1) 是单独设置的（管理账户+控制台——见下文）。

> 建议使用 AWS MCP 服务器执行此技能的 AWS API 调用，但它不是必需的——所有操作也直接与 AWS CLI 工作。

## 守卫——此技能自身文件的位置（MCP 与本地安装）

在读取参考文件之前，确定此技能是如何加载的：

- **通过 AWS MCP `retrieve_skill` 工具加载**：技能的参考文件不在本地文件系统中。通过 `retrieve_skill` 使用 `file` 参数获取每个文件（例如 `file="references/multi-account-procedure.md"`）——不要在本地 `file_read` 这些路径或搜索文件系统。
- **本地安装**（例如 `.kiro/skills/resilience-hub-multi-account/` 或 `~/.claude/skills/resilience-hub-multi-account/`）：使用此处显示的相对路径从本地技能目录读取参考文件。

这仅适用于技能自身的参考文件；始终在工作目录中读取和写入用户或会话数据，绝不要通过 `retrieve_skill`。

## 集中化多账户评估的工作原理

根据您的目标使用两种路径：

> **决策规则（首先阅读）**：要运行跨账户弹性评估——即从中心账户评估位于成员账户中的工作负载/资源（常见的请求，包括类似 *"跨组织的集中化弹性管理"* 或 *"集中评估账户"* 的措辞）——请使用 **按服务跨账户权限模型**（下方路径 2）：调用者角色 + 跨账户角色 + `create-service --permission-model`。**不要使用或推荐 `aws organizations register-delegated-administrator`（或任何委托管理员注册）作为跨账户评估的设置步骤。** Organizations 委托管理员集成（路径 1）是一个 *单独的、可选* 功能，仅限于组织范围的 **策略管理和可见性**——它不是设置或运行跨账户评估的方式。仅在请求明确涉及组织范围的策略治理时才遵循路径 1，而不是评估。

- **组织范围治理**（集中化策略、跨账户可见性）：使用 **AWS Organizations 集成**。从 **管理账户** 启用弹性中心的受信任访问，创建服务关联角色，并 **注册一个委托管理员** 账户。这是通过 Organizations 受信任访问 + 弹性中心控制台完成的——**没有 `resiliencehubv2` `register-delegated-administrator` CLI 操作**。委托管理员然后选择一个主页区域，用于聚合组织级数据。有关 AWS 文档页面 *设置 Organizations 集成*。
- **按服务跨账户资源发现**（评估资源跨账户的服务）：为每个服务注册 **按服务跨账户权限模型**——中心账户中的调用者角色加上每个成员账户的跨账户角色 ARN。**本技能的步骤配置此路径。** 使用以下命令格式：

```
aws resiliencehubv2 create-service --name {service} --regions {regions} \
  --permission-model '{"invokerRoleName":"ResilienceHubAssessmentRole","crossAccountRoles":[{"crossAccountRoleArn":"arn:aws:iam::{member_account_id}:role/ResilienceHubAccess","externalId":"{external_id}"}]}'
```

> `externalId` 是一个共享密钥，用于防御混淆代理攻击——生成一个密码学随机值，并将其存储在 AWS Secrets Manager 或 SSM Parameter Store（SecureString）；永远不要将其提交到源代码控制或嵌入模板而不使用动态的 `{{resolve:secretsmanager:...}}` 引用，并确保它不会以明文形式出现在 CI/CD 日志或基础设施即代码输出中（使用 CloudFormation `NoEcho` 参数并在管道日志中对其进行遮罩）。

跨账户角色（在成员账户中）信任中心账户的调用者角色。您可以配置每个服务的多个跨账户角色 ARN——`resiliencehubv2` API 强制最大值（例如 5），因此 **请从 API/模型验证接受的限制，而不是假设固定数量**。注意：此按服务模型独立于上述 Organizations 集成——`resiliencehubv2` CLI 中没有 `register-delegated-administrator` 操作；组织范围的委托管理员注册是通过 AWS Organizations 受信任访问和弹性中心控制台完成的，而不是 `resiliencehubv2` API 调用。

## 配置多账户设置

要设置跨账户评估，请严格按照程序进行。
参见 [references/multi-account-procedure.md](references/multi-account-procedure.md)。

## 故障排除

### 跨账户评估失败，出现 AccessDenied

验证：(1) 权限模型中的跨账户角色 ARN 完全匹配，(2) 跨账户角色的信任策略允许中心账户的调用者角色假设它，(3) 如果配置了，externalId 匹配。

### 在成员账户中没有发现资源

确认跨账户角色对范围内的资源类型（CloudFormation、EC2、RDS 等）具有读取权限，并且输入源指向正确区域的合法资源。

### 寻找委托管理员设置

弹性中心 v2 **确实** 支持与委托管理员进行 AWS Organizations 集成，用于组织范围的策略管理和可见性——但它通过 **管理账户** 通过 Organizations 受信任访问 + 弹性中心控制台配置（创建服务关联角色，然后注册委托管理员），**而不是**通过 `resiliencehubv2` CLI 操作（没有 `register-delegated-administrator` API）。要评估一个 *单个服务*，其资源跨账户，请使用本技能中的按服务跨账户权限模型。两者是互补的。

## 安全注意事项

- **最小权限和只读**：将成员账户的跨账户角色范围限制为只读发现权限（`cloudformation:Describe*`、`ec2:Describe*`、`rds:Describe*` 等），而不是写/修改操作。
- **狭义范围跨账户信任**：在可能的情况下，仅信任特定的中心调用者角色 ARN，而不是整个账户。
- **启用日志记录和监控**：确保在中心和成员账户中启用 AWS CloudTrail 以记录跨账户 `sts:AssumeRole` 调用，并对针对跨账户角色的失败或意外 AssumeRole 尝试触发警报。
- **进一步阅读**：参见 [IAM 最佳实践](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)、[混淆代理问题](https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html) 和 [AWS 弹性中心中的安全性](https://docs.aws.amazon.com/resilience-hub/latest/userguide/security.html) 以获取跨账户加固指南。
