# 开始使用 AWS Resilience Hub v2

## 概述

针对首次设置 Resilience Hub v2 的领域专业知识：策略、系统、用户旅程、服务、输入源和故障模式评估。

> 建议使用 AWS MCP 服务器执行此技能的 AWS API 调用，但它不是必需的——所有操作也直接通过 AWS CLI 工作。

## 守卫——此技能自己的文件存放位置（MCP 与本地安装）

在读取参考文件之前，确定此技能是如何加载的：

- **通过 AWS MCP `retrieve_skill` 工具加载：** 技能的参考文件不在本地文件系统中。通过 `retrieve_skill` 使用 `file` 参数获取每个文件（例如 `file="references/setup-procedure.md"`）——不要在本地 `file_read` 这些路径或搜索文件系统。
- **本地安装**（例如 `.kiro/skills/resilience-hub-getting-started/` 或 `~/.claude/skills/resilience-hub-getting-started/`）：使用此处显示的相对路径从本地技能目录读取参考文件。

这仅适用于技能自己的参考文件；始终在工作目录中读取和写入用户或会话数据，绝不要通过 `retrieve_skill`。

## 设置 Resilience Hub v2

要从头配置 Resilience Hub v2，请严格按照程序操作。
参见 [references/setup-procedure.md](references/setup-procedure.md)。

## 故障排除

### 评估卡在 IN_PROGRESS 状态

使用 `aws resiliencehubv2 list-failure-mode-assessments` 进行轮询。如果卡住超过 30 分钟，请检查 `errorCode` 字段——常见原因是跨账户角色上的 `INVALID_PERMISSIONS` 或 `CMK_ACCESS_DENIED`。

### 可实现性显示为 NOT_ACHIEVABLE

您的架构无法满足策略目标。在运行 FIS 实验之前修复基础设施——如果架构从根本上不足，测试将无济于事。

### 未发现资源

验证输入源是否正确：CFN 堆栈 ARN 存在，Terraform 状态文件可访问，EKS 集群位于指定区域，或资源标签与实际资源匹配。

## 安全注意事项

- **最小权限：** 将调用者角色限定为仅读取输入源中资源类型的发现；附加 AWS 管理的 `AWSResilienceHubAsssessmentExecutionPolicy`（AWS 用三个 s）或更严格的自定义策略。
- **静态加密 / 传输加密：** 建议为 Terraform 状态和评估报告使用 S3 存储桶，并使用服务器端加密（SSE-KMS）和强制通过 `aws:SecureTransport` 的桶策略进行 TLS。
- **条件密钥（混淆代理人）：** 在调用者角色的信任策略中添加 `aws:SourceAccount`（理想情况下 `aws:SourceArn` 限定为特定的 Resilience Hub 服务 ARN）条件，以便只有您的账户的 Resilience Hub 才能假定它。
- **限制评估暴露：** 限制谁可以调用 `start-failure-mode-assessment`（它读取基础设施状态）以及谁可以读取评估结果和报告——这些可能包含敏感的架构细节。
- **进一步阅读：** 参见 [AWS Resilience Hub 中的安全](https://docs.aws.amazon.com/resilience-hub/latest/userguide/security.html) 和 [IAM 最佳实践](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)（包括跨服务混淆代理人预防）。
