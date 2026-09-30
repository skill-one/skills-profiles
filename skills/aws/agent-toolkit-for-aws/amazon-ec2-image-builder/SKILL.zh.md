---
name: amazon-ec2-image-builder
description: 使用 EC2 Image Builder 创建和自动化自定义镜像构建 - 支持 Linux、Windows 和 macOS AMI 以及容器镜像，并将它们上传至 ECR。涵盖构建 IAM 角色配置、Amazon 管理和自定义组件、镜像配方、基础设施和分发配置（启动模板、SSM 参数、其他区域）、一次性构建、用于黄金 AMI 自动化和操作系统补丁的周期性计划管道、自定义镜像工作流以及诊断构建失败。适用于使用 Image Builder 创建、自动化或调度 AMI 或容器镜像构建，或在调试构建失败时使用。不适用于从现有 AMI 启动实例、AMI 生命周期/退役或一般 EC2 队列管理。
---

# Amazon EC2 Image Builder

## 概述

使用 EC2 Image Builder 构建自定义 AMI 和容器镜像的专业知识——从构建 IAM 角色到配方、管道、分发和故障排除。

**最佳搭配** [AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/)——推荐用于沙盒执行和审计日志记录。所有指南也适用于标准 AWS CLI 访问。

## 安全边界——此技能自身文件存放的位置（MCP 与本地安装）

此技能有两种加载方式，它们从不同的位置解析技能自身的捆绑文件。在阅读参考或运行脚本之前，请确定技能是如何加载的：

- **通过 AWS MCP `retrieve_skill` 工具加载**：技能未安装在本地文件系统中。您必须通过带有 `file` 参数的 `retrieve_skill`（例如 `file="references/creating-images.md"`）获取每个参考或脚本，并使用返回的内容。不要在本地 `file_read` 这些路径——它们在磁盘上不存在。
- **本地安装**（例如 `.kiro/skills/amazon-ec2-image-builder/` 或 `~/.claude/skills/amazon-ec2-image-builder/`）：使用相对路径从本地技能目录读取文件。

此区别仅适用于技能自身的捆绑文件。用户数据和会话工件始终从用户的工作目录读取和写入。切勿通过 `retrieve_skill` 获取或写入用户数据。

## 首个决策：一次性镜像还是周期性管道

在创建任何内容之前先问这个问题——它将改变您要构建的内容。

| 用户想要 | 执行此操作 |
|---|---|
| 一次一个自定义 AMI | 按照 [creating-images.md](references/creating-images.md) 通过步骤 7a：使用配方和基础设施配置的 `create-image`——无需管道。 |
| 一个始终保持当前的黄金 AMI（定期重建以获取基础镜像更新和补丁） | 镜像管道：按照 [creating-images.md](references/creating-images.md)——计划是 `create-image-pipeline` 调用的部分（步骤 7b）。 |

## 相关技能——请改为此路由

| 使用此技能 | 当请求关于 |
|---|---|
| **launching-ec2-instance-with-best-practices** | 从用户已有的 AMI 启动实例 |
| **setting-up-ec2-instance-profiles** | 实例配置文件（此技能创建的构建 IAM 角色除外） |
| **aws-compute** | AMI 共享、退役和生命周期管理；一般 EC2 舰队问题 |

**不在此涵盖**：AMI 生命周期/退役（通过上表路由）和 VM/ISO 镜像导入和导出（直接遵循 AWS 文档）。

## 路由（本技能中的参考）

在回答之前，请阅读匹配的参考。确切的命令、故障修复和平台要求都存在于参考中——从一般知识回答 Image Builder 问题是代理如何微妙地出错的方式。

| 用户需求 | 阅读 |
|---|---|
| 端到端创建镜像或管道：角色、组件、配方、基础设施、计划、补丁、扫描、链接 | [creating-images.md](references/creating-images.md) |
| 获取所需的输出 AMI：启动模板、SSM 参数（服务链接角色仅在 `/imagebuilder/` 下写入）、其他区域 | [distribution-options.md](references/distribution-options.md) |
| 构建失败、挂起或 Image Builder API 调用出错 | [troubleshooting.md](references/troubleshooting.md) |
| Windows（退出 3010 重启）、macOS（需要专用主机）、容器镜像到 ECR（额外的构建角色策略） | [other-image-types.md](references/other-image-types.md) |
| 自定义镜像工作流（高级——始终需要执行角色） | [custom-workflows.md](references/custom-workflows.md) |

参考文件包含特定的 ARN、Amazon 管理的资源名称和服务默认值——当精确度很重要时，请与 AWS 文档确认。

## 安全边界（每个工作流）

- 引用包含空格的 CLI 过滤值时请加引号：`--filters "name=name,values=Amazon Linux 2023 x86"`。未加引号的空格会导致 CLI 解析错误。
- 使用每个创建调用返回的确切 ARN——切勿手动构造 ARN。
- 对于“最新”基础镜像，使用带有 `x.x.x` 通配符的 Amazon 管理镜像 ARN，或在没有管理镜像时使用 `ssm:` 参数引用。切勿列出版本并按字符串排序——列表不是 semver-排序的。
- 确保基础镜像、每个组件的二进制文件和基础设施实例类型架构一致。Image Builder 在创建时不会对此进行验证；不匹配仅在组件运行时构建中途失败。
- 对于组件故障，根本原因位于 CloudWatch 日志组 `/aws/imagebuilder/<image-name>`（默认开启；如果配置了也位于 S3 日志中）——绝不在 API 状态中。参见 [troubleshooting.md](references/troubleshooting.md)。
- 为在构建中途重启，请以代码 `194`（Linux）或 `3010`（Windows）退出步骤。构建将在重启后重新运行该步骤——而不是下一个步骤——因此请用标记文件保护它。一个纯重启命令会失败该步骤。
- 如果用户描述的资源对 `get-image`/`get-image-pipeline` 不可见，请说找不到它并检查正在使用的区域和凭证——然后根据用户的描述继续故障排除；失败的查找不是资源不存在的证明。
- 分发原生处理启动模板和 SSM 发布 (`launchTemplateConfigurations`, `ssmParameterConfigurations`)——切勿添加 Lambda 粘合或手动启动模板版本以进行 AMI 传播。
- 默认为：Amazon Linux 2023 基础镜像、IMDSv2 必须使用 (`instanceMetadataOptions httpTokens=required`)、基础设施配置中至少有两个实例类型。S3 构建日志记录是可选的——CloudWatch 日志记录始终开启。
- 在编写组件 YAML 之前检查 Amazon 管理组件 (`aws imagebuilder list-components --owner Amazon`)。常见的需求（AWS CLI、OS 更新、CloudWatch 代理、STIG 硬化）已经涵盖。

## 安全注意事项

上述默认值是安全态势：构建实例必须使用 IMDSv2、无入站安全组规则、最低权限构建 IAM 角色（AMI 构建的两个管理策略加上工作流需要的范围权限）、组件或日志中无密钥，以及具有阻止公共访问的日志桶。构建日志捕获完整的命令输出，可能包含敏感材料；CloudWatch Logs 默认对存储的日志进行加密，建议为每个 `/aws/imagebuilder/...` 日志组（`aws logs associate-kms-key`）关联一个客户管理的 KMS 密钥。为审计和操作可见性，请在账户中启用 CloudTrail，以便记录 Image Builder API 调用，并配置 EventBridge 规则或 CloudWatch 闹钟在构建失败时（来源 `aws.imagebuilder`，详细信息类型 `EC2 Image Builder Image State Change`）以便配置错误配置和未经授权的更改能够及时暴露。每个构建的通知由 SNS 主题选项（creating-images.md 步骤 6）涵盖——也请在此主题上使用客户管理的密钥。偏离这些应该是明确用户决策。参考：[EC2 Image Builder 安全最佳实践](https://docs.aws.amazon.com/imagebuilder/latest/userguide/security-best-practices.html)。
