---
name: signing-in-to-aws
description: 通过 `aws login` 获取 AWS 凭证以访问 CLI/SDK。当开发者需要为本地开发向 AWS 进行身份验证、因凭证缺失或过期导致 AWS 操作失败，或有人询问如何设置 AWS 访问权限时，该功能会被激活。触发条件包括："设置 AWS"、"配置 AWS"、"aws login"、"获取凭证"、"身份验证"、"会话过期"、"令牌过期"、"无凭证"、"AccessDeniedException"（在未配置凭证的情况下）。
---

# 登录 — 获取 CLI/SDK 凭证

帮助开发者使用 `aws login` 获取 AWS 凭证进行本地开发。这提供了短期、自动轮换的凭证，每 15 分钟刷新一次，最多有效期为 12 小时。

**重要提示：**

- 您必须在用户的本地 shell 中运行 `aws login` 和 `aws --version` —— 不能通过 MCP/API 工具运行。
- 您必须在运行 `aws login` 之前征得用户的确认。不要告诉用户自行运行命令 —— 询问您是否应该运行它（例如，“准备好让我运行 `aws login` 吗？”或“我是否应该继续执行 `aws login`？”）。在继续之前等待他们的回复。

## 前置条件

`aws login` 命令需要 **AWS CLI 版本 2.32.0 或更高版本**。

检查已安装的版本：

```bash
aws --version
```

如果 CLI 未安装或版本低于 2.32.0，请告知用户并询问他们是否希望安装/更新（将他们链接到 [AWS CLI 安装指南](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)），或者他们是否希望在没有此技能的指导下继续。如果他们选择不升级，请按照正常方式响应用户的原始请求，不使用此技能。

## 流程

### 先提出建议

在您的第一个回复中，始终告诉用户 `aws login` 是解决方案 —— 解释它提供短期、自动轮换的凭证，并且需要 AWS CLI 2.32.0 或更高版本。不要停留在“让我检查您的 CLI 版本” —— 直接提出修复措施，以便用户知道后续步骤，然后描述您在调用它之前将运行的前置条件检查。

### 前置条件检查（在请求确认前静默运行）

通过本地 shell 运行这些命令以说明您的计划。报告您发现的内容，但不要将建议基于用户提供的输出：

1. `aws --version` — 确认 CLI 是 2.32.0 或更高版本。如果未安装或太旧，请将用户指向 [AWS CLI 安装指南](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) 并停止。
2. `aws sts get-caller-identity` — 检查当前凭证。
   - **成功**：向用户显示他们的 Account 和 Arn。询问是否要保留这些凭证或设置不同的凭证。如果他们想切换，建议 `aws login --profile <name>` 以免覆盖现有的默认配置。
   - **失败**（缺失或过期）：在默认配置文件上继续执行 `aws login`。
3. *(仅在步骤 2 成功且用户希望使用不同凭证时)* `aws configure list` — 如果 `access_key` 以 `AKIA` 开头，解释长期访问密钥安全性较低（永不过期，作为明文保存在磁盘上，如果泄露则提供无限访问权限），而 `aws login` 提供每 15 分钟自动轮换的短期凭证，自动过期且无需手动轮换。

### 确认并运行 aws login

一旦前置条件明确，请专门请求用户对 `aws login` 调用的确认 —— 仅限此处。不要告诉用户自行运行命令；询问您是否应该运行它（例如，“准备好让我运行 `aws login` 吗？”或“我是否应该继续执行 `aws login --profile staging`？”）。等待他们的回复，然后运行 `aws login`（或 `aws login --profile <name>`）。

### 验证

`aws login` 完成后，运行 `aws sts get-caller-identity`（如果使用了 `--profile` 则带上）以确认成功。如果使用了命名的配置文件，请提醒用户传递 `--profile` 或设置 `AWS_PROFILE`。

## 错误处理

### "command not found" 或版本太旧

CLI 未安装或版本低于 2.32.0。请将用户引导至安装或更新：[AWS CLI 安装指南](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)。

### 浏览器无法打开

建议使用 `aws login --remote`，它提供跨设备认证的 URL 和代码（例如，在使用远程服务器且没有浏览器时）。

### 登录后出现权限错误

IAM 身份需要附加 `SignInLocalDevelopmentAccess` 管理策略（附加到用户、角色或组）。根用户不需要它。请告知用户请求他们的管理员添加它，或者如果他们具有 IAM 权限，则自行附加。

### GovCloud 或中国区域

`aws login` 在 AWS GovCloud (US) 或 AWS 中国区域不可用。不要主动提及此例外情况 —— 仅当用户明确表示他们位于这些分区时才相关。

## 具有 `aws sso login` 工作流的用户

如果用户提到 `aws sso login` 或具有现有的 SSO 配置，请 **不要** 将他们重定向到 `aws login`。这些是针对不同情况的命令：

- `aws sso login` 适用于其组织已配置 AWS IAM Identity Center (SSO) 的用户。他们有指向 SSO 启动 URL 的 `~/.aws/config` 中的配置文件。尊重他们已建立的工作流程。
- 如果他们的 `aws sso login` 失败，请在其上下文中帮助他们排查：过期 SSO 会话、撤销授权、缓存令牌问题（`~/.aws/sso/cache/`）或 Identity Center 配置更改。

## 回退到 `aws configure`

在您的初始回复中或作为表格行与 `aws login` 一起提及 **不要** `aws configure`。仅在以下情况下提供它作为替代方案：

1. 用户明确拒绝 `aws login` 或要求其他方案
2. 用户声明他们位于 GovCloud 或中国区域（`aws login` 不可用）

提供时，解释长期访问密钥安全性较低：它们以明文形式保存在磁盘上，不会自动过期，如果泄露则提供无限访问权限。

## 不应使用此技能的情况

- 用户正在设置 CI/CD 凭证 —— 他们需要 IAM 角色或 OIDC 联邦，而不是 `aws login`

## 关键点

- 不要过早进行故障排除 —— 保持初始回复简单，仅在出现错误时才处理
- `aws login` 适用于根用户、IAM 用户和 IAM 联邦

## 其他资源

- [通过 AWS CLI 登录](https://docs.aws.amazon.com/signin/latest/userguide/command-line-sign-in.html)
- [安装或更新 AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [SignInLocalDevelopmentAccess 管理策略](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/SignInLocalDevelopmentAccess.html)
- [IAM 安全最佳实践](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
