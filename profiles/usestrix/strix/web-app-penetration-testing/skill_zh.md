# 对 Web 应用进行渗透测试

使用 Strix 的自主代理对正在运行的 Web 应用进行黑盒（以及可选的源码辅助）渗透测试。每个报告的发现都会通过可工作的漏洞利用进行验证，因此没有基于签名的误报需要筛选。

安装、LLM 设置、所有 CLI 标志以及托管云替代方案都在 **penetration-testing-with-strix** 技能中涵盖——如果目标不是正在运行的 Web 应用，或者 `strix --version` 失败，请阅读它。对于没有 Docker 和没有 LLM 密钥的运行，相同的二进制文件驱动托管平台：`strix cloud login`，然后 `strix cloud scans start ...`（详情在 **managed-pentesting-with-strix**）。这个技能是针对 Web 应用的特定工作流程。

## 1. 确认授权和范围

在运行任何操作之前，需要建立：

- **目标是谁的**（或者他们是否有明确的授权进行测试）。切勿在没有依据的情况下对第三方网站进行渗透测试。
- **哪个环境。** 优先选择 staging 而不是 production；代理会发送真实的漏洞利用载荷，并会创建/修改数据。
- **超出范围的路径**——支付流程、批量邮件端点、管理员破坏性操作、第三方 SSO 提供商。
- **凭证。** 大多数真实漏洞都隐藏在登录之后。如果没有测试账户，代理只会看到营销表面。

与其猜测，不如询问缺失的内容。

## 2. 运行扫描

```bash
strix -n -t https://staging.example.com --max-budget 20 \
  --instruction "测试账户: qa@example.com / <密码>。在范围内的路径: /app/*, /api/*. 不要触碰 /billing 或发送邮件。专注于两个种子组织之间的访问控制。"
```

对 Web 应用特别重要的注意事项：

- **通过 `--instruction` 提供凭证**（或 `--instruction-file` 用于任何长文本），包括如何登录，如果流程不寻常（魔法链接、SSO、免 MFA 的测试用户）。
- **两个账户比一个更好。** 多租户 IDOR 和破坏性访问控制漏洞——始终是 Web 应用中影响最高的类别——只有在代理可以尝试跨账户访问时才能被证明。
- **在有源码时添加仓库以进行白盒深度分析**：`-t https://github.com/org/app -t https://staging.example.com`（或本地路径）。源码访问会显著提高业务逻辑和授权缺陷的覆盖范围。
- **本地主机有效。** 指向 `http://host.docker.internal:3000`（Docker Desktop），以便沙盒可以访问主机上的开发服务器。
- `--scan-mode quick` 用于快速开发循环扫描，`standard`（约 30 分钟）用于正常审查，`deep` 用于预发布保证。始终设置 `--max-budget`。

对于没有 Docker/LLM 密钥的托管运行，或者当用户想要可分享的仪表板和审计人员准备的 PDF 时，可以使用 **managed-pentesting-with-strix** 中的云路径——相同的引擎，相同的结果。

## 3. 审查结果

首先阅读 `strix_runs/<run>/penetration_test_report.md`，然后查看 `vulnerabilities/` 中的每个发现文件。每个文件都包含 PoC——在向用户报告之前，请自行重新运行以确认。

退出代码：`0` 表示在分析范围内没有验证的漏洞，`2` 表示发现漏洞，`1` 表示致命错误。`0` 并不是完整覆盖的证明——如果预算或轮次限制被达到，扫描会提前结束，因此请在调用应用干净之前检查 `run.json` 状态和成本与 `--max-budget`。

## 4. 修复和验证

将发现交给 **fix-security-vulnerabilities-with-strix** 技能：修复根本原因，然后对同一目标重新运行 Strix 以证明漏洞利用不再工作。重新测试是唯一可靠的确认修复是否落地的方法。

为了在每次更改时而不是一次测试应用，请使用 **ci-security-scanning-with-strix** 将 Strix 集成到 CI 中。
