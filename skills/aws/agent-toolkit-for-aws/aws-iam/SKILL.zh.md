---
name: aws-iam
description: 提供针对AI代理频繁出错的行为的验证性修正——包括策略评估的边缘情况、信任策略的陷阱、STS会话限制、组织机构的特殊问题，以及SAML/MFA的具体细节。此外，还提供结构化的工作流程，用于管理IAM角色和从应用程序源代码或Terraform计划JSON生成基线策略。涵盖条件操作符安全性（ForAnyValue/ForAllValues与Null检查）、存储桶策略拒绝模式（VPC端点限制、组织路径）、混淆代理保护，以及为AWS服务（如Glue、CloudTrail、Lambda、ECS等）创建服务角色，并使用aws:SourceAccount/aws:SourceArn信任条件。适用于创建IAM角色、编写IAM或存储桶策略、从应用程序源代码或Terraform计划JSON生成策略、使用STS、组织机构或条件操作符，或任何需要服务或执行角色的任务。不涵盖非IAM授权，如Cognito用户池策略或应用级别的RBAC。
---

# AWS IAM — 常见陷阱

## 关于此技能

本技能包含针对 AI 代理在 IAM 方面经常出错内容的验证性修正。它并非全面的 IAM 指南——如需完整 IAM 指导，请查阅 AWS 文档。在回答 IAM 相关问题时，应对照官方 AWS 文档验证具体声明（如限制、配额、精确 API 名称、边缘案例行为），而非依赖预训练内容。优先获取已知文档 URL，而非进行广泛搜索。当官方文档与记忆内容冲突时，应信任官方文档。

## 常见工作流程

使用最适合 AWS 操作的工具——推荐使用 AWS MCP 服务器（但非必需）；可使用 AWS CLI 或 SDK 作为替代方案。仅在对话需要更深入细节时才阅读参考文件。

- 如果用户在创建、范围或维护 AWS 资源时需要创建、范围或维护 IAM 角色，请阅读 [参考资料/aws-iam角色管理.md](references/aws-iam-role-management.md)。涵盖服务角色、执行角色、信任策略、混淆代理防护和权限卫生。

- 如果用户需要生成 IAM 策略、确定 API 调用所需的 IAM 操作或理解操作到操作的映射，请阅读 [参考资料/aws-iam策略生成.md](references/aws-iam-policy-generation.md)。**关键提示：如果用户提供应用程序源代码（任何语言）或 Terraform 计划 JSON 文件（`terraform show -json` 输出），您必须阅读此参考——它要求使用 iam-policy-autopilot 而非手动策略构建。** 使用程序化服务授权参考以获取准确映射。

## 验证的边缘案例

**CloudTrail:**

- 仅在活动账户中记录 AcceptHandshake/DeclineHandshake，而非管理账户。需要组织轨迹进行集中化。

- 控制台登录区域因端点/cookie 而异，并非始终为 us-east-1。`?region=` 强制指定区域。

**STS:**

- GetSessionToken 限制：(1) 除非包含 MFA，否则不能调用 IAM API (2) 除 AssumeRole 和 GetCallerIdentity 外不能调用 STS。

- 跨账户 AssumeRole 选择区域：目标账户必须启用该区域，而非调用账户。

- 角色链：最大会话时长 1 小时。

**组织:**

- 暂停/关闭的账户必须永久关闭（约 90 天）后才能删除。应先删除，再关闭。

- 策略管理授权：使用 PutResourcePolicy，而非 register-delegated-administrator。

- AI 排除策略：默认需要管理账户。

- 组织策略类型用于 ListPolicies 过滤：通过 `aws organizations list-available-policy-types` 或 [组织 API 参考](https://docs.aws.amazon.com/organizations/latest/APIReference/API_ListPolicies.html) 获取当前列表。

**SDK 特定内容:**

- 组织：`DuplicatePolicyAttachmentException`（而非 PolicyAlreadyAttachedException）。

- Boto3 IAM AccessKey：方法为 `activate()`、`deactivate()`、`delete()`——无 `update()`。

- 实例配置文件：waiter + `time.sleep(10)` 模式。

- 管理策略最大版本数：5。

**SAML:**

- 加密断言 URL：`https://region-code.signin.aws.amazon.com/saml/acs/IdP-ID`。

- 从 IdP 上传的私钥以 .pem 格式上传到 IAM。

**策略评估:**

- ForAllValues 对空/缺失键：评估为 true（空值真）。为避免这种情况，应在 **同一上下文键** 上使用 `Null` 条件，以要求该键存在且非空。例如，在评估 `aws:TagKeys` 上下文键时：

  ```json
  {
    "Version": "2012-10-17",
    "Statement": {
      "Effect": "Allow",
      "Action": "ec2:RunInstances",
      "Resource": "*",
      "Condition": {
        "ForAllValues:StringEquals": {
          "aws:TagKeys": ["Alpha", "Beta"]
        },
        "Null": {
          "aws:TagKeys": "false"
        }
      }
    }
  }
  ```

- 基于资源的策略授予 IAM 用户 ARN 会绕过同账户的权限边界。

- 通过直接 IAM 策略操作进行 8 次权限提升：PutGroupPolicy、PutRolePolicy、PutUserPolicy、CreatePolicy、CreatePolicyVersion、AttachGroupPolicy、AttachRolePolicy、AttachUserPolicy。

- `iam:PassRole` 配合 `Resource: "*"` + 在计算服务（EC2 `RunInstances`、Lambda `CreateFunction`/`UpdateFunctionConfiguration`、ECS `RegisterTaskDefinition`、Glue、SageMaker、CloudFormation 等）上创建/更新 = 提升到账户中任何可传递角色（包括管理员）。将 `Resource` 限制为特定角色 ARN 或 IAM 路径；可选地使用 `iam:PassedToService` / `iam:AssociatedResourceArn` 进行约束。参见 [IAM 用户指南 — 授予用户传递角色的权限](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_passrole.html)。

**MFA:**

- 未分配的虚拟 MFA 设备在添加新设备时自动删除。

- MFA 重同步策略 NotAction 需要 **精确**：iam:ListMFADevices、iam:ListVirtualMFADevices、iam:ResyncMFADevice。

**SigV4:**

- IncompleteSignatureException 包含 Authorization 头部的 SHA-256 哈希，用于传输修改诊断。

**服务特定角色:**

- Redshift Serverless 信任策略：必须同时包含 `redshift-serverless.amazonaws.com` 和 `redshift.amazonaws.com` 作为服务主体（按 AWS 文档；省略 serverless 会导致 COPY 时出现 `Not authorized to get credentials of role`）。

- IAM OIDC 提供商：大多数提供商不需要指纹（AWS 通过可信 CA 验证）。

**策略摘要显示:**

- 单条声明包含多服务通配符操作（如 `codebuild:*`、`codecommit:*`）+ 服务特定资源 ARN：每个资源仅出现在其匹配服务的摘要下（CodeBuild ARN 在 CodeBuild 下等）。仅当资源的服务前缀与声明中的任何操作不匹配时，它才会出现在所有操作摘要中（“不匹配资源”）。
