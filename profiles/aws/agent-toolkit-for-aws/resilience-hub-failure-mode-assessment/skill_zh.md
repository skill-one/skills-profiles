# 失效模式评估

## 概述

运行 Resilience Hub v2 失效模式评估的领域专业知识，解释评估结果，按严重程度和可实现性进行分诊，并推动修复。

> 建议使用 AWS MCP 服务器执行此技能的 AWS API 调用，但它不是必需的——所有操作也可以直接通过 AWS CLI 执行。

## 守卫——此技能的文件存放位置（MCP 与本地安装）

在读取参考文件之前，确定此技能是如何加载的：

- **通过 AWS MCP `retrieve_skill` 工具加载：** 技能的参考文件不在本地文件系统中。通过 `retrieve_skill` 并使用 `file` 参数获取每个文件（例如 `file="references/assessment-workflow.md"`）——不要在本地 `file_read` 这些路径或搜索文件系统。
- **本地安装**（例如 `.kiro/skills/resilience-hub-failure-mode-assessment/` 或 `~/.claude/skills/resilience-hub-failure-mode-assessment/`）：使用此处显示的相对路径从本地技能目录读取参考文件。

这仅适用于技能自身的参考文件；始终在工作目录中读取和写入用户或会话数据，绝不要通过 `retrieve_skill`。

## 运行和解释评估

要运行评估和分诊结果，请严格按照程序执行。
参见 [references/assessment-workflow.md](references/assessment-workflow.md)。

## 故障排除

### 评估失败，错误信息为 INVALID_PERMISSIONS

服务的权限模型（invokerRoleName / crossAccountRoles）无法访问资源。验证调用者角色（以及任何跨账户角色）是否可以在所有配置的区域中描述资源。

### 发现过多——从何处开始？

按发现严重程度排序，最高优先级为（HIGH，然后是 MEDIUM，然后是 LOW）。对于 HIGH 严重程度的发现，检查服务的可实现性，针对相关的策略组件（从 `get-service` / `list-failure-mode-assessments`）：NOT_ACHIEVABLE 表示在测试之前必须更改架构；ACHIEVABLE 表示通过 FIS 实验验证修复。MEDIUM 发现：在本轮中计划修复；LOW 发现：跟踪但不要阻止（参见 [references/assessment-workflow.md](references/assessment-workflow.md) 第 5 步中的优先级矩阵）。

### AI 生成的服务函数不正确

更新它们：`aws resiliencehubv2 update-service-function` 以重命名或更改关键性（没有服务函数 "type" 参数）。通过调用 `create-service-function-resources` 并使用所需资源集重新分配资源（有关服务函数操作的详细信息，请参见 [references/assessment-workflow.md](references/assessment-workflow.md)）。

## 安全注意事项

- **最小权限：** 调用者角色应仅限于读取仅限于服务输入源中的资源类型的发现；避免授予超出评估所需的访问权限。
- **加密和访问控制：** 建议用于报告输出的 S3 存储桶具有服务器端加密（SSE-S3 或 SSE-KMS）并阻止公共访问——评估报告可能包含敏感的架构详细信息。如果存储桶策略授予 Resilience Hub 服务主体写入访问权限，请使用 `aws:SourceArn` / `aws:SourceAccount` 条件键进行范围限制，以防止混淆代理写入。
- **进一步阅读：** 请参阅 [AWS Resilience Hub 中的安全](https://docs.aws.amazon.com/resilience-hub/latest/userguide/security.html) 和 [AWS Well-Architected 安全支柱](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html) 以保护评估输出和 IAM 配置。
