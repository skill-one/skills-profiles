# Azure 合规与安全审计

## 快速参考

| Property | Details |
|---|---|
| 适用于 | 合规扫描、安全审计、Key Vault 过期检查 |
| 主要功能 | 综合资源评估、Key Vault 过期监控 |
| MCP 工具 | azqr、订阅与资源组列表、Key Vault 项目检查 |

## 前提条件

- 认证：用户已通过 `az login` 登录 Azure
- 具备读取资源配置和 Key Vault 元数据的权限

## 评估

| 评估 | 参考 |
|------------|-----------|
| 全面合规 (azqr) | [references/azure-quick-review.md](references/azure-quick-review.md) |
| Key Vault 过期 | [references/azure-keyvault-expiration-audit.md](references/azure-keyvault-expiration-audit.md) |
| 资源图查询 | [references/azure-resource-graph.md](references/azure-resource-graph.md) |

## MCP 工具

| 工具 | 用途 |
|------|---------|
| `mcp_azure_mcp_extension_azqr` | 运行 azqr 合规扫描 |
| `mcp_azure_mcp_subscription_list` | 列出可用订阅 |
| `mcp_azure_mcp_group_list` | 列出资源组 |
| `keyvault_key_list` | 列出密钥库中的所有密钥 |
| `keyvault_key_get` | 获取密钥详情（包括过期时间） |
| `keyvault_secret_list` | 列出密钥库中的所有密钥（Secrets） |
| `keyvault_secret_get` | 获取密钥（Secrets）详情（包括过期时间） |
| `keyvault_certificate_list` | 列出密钥库中的所有证书 |
| `keyvault_certificate_get` | 获取证书详情（包括过期时间） |

## 评估流程

1. 为综合资源评估选择范围（订阅或资源组）。
2. 运行 azqr 并捕获输出产物。
3. 分析扫描结果，总结发现与建议。
4. 审查密钥、密钥（Secrets）和证书的 Key Vault 过期监控输出。
5. 对问题进行分类，并为每项发现提出修复或处理步骤。

### 优先级分类

| 优先级 | 指导 |
|---|---|
| 严重 | 存在高影响暴露风险，需立即进行修复 |
| 高 | 需在数日内解决以降低风险 |
| 中 | 计划在下个迭代中解决 |
| 低 | 在日常维护中跟踪并修复 |

## 错误处理

| 错误 | 消息 | 修复方法 |
|---|---|---|
| 需要认证 | "请登录" | 运行 `az login` 后重试 |
| 访问被拒 | "禁止" | 确认权限并修复角色分配 |
| 资源缺失 | "未找到" | 验证订阅和资源组的选择 |

## 最佳实践

- 按固定周期（每周或每月）运行合规扫描
- 跟踪发现情况，并验证修复有效性
- 将合规报告与修复执行分开处理
- 记录并执行 Key Vault 过期策略

## SDK 快速参考

针对程序化访问 Key Vault，请参阅精简版的 SDK 指南：

- **Key Vault (Python)**：[Secrets/Keys/Certs](references/sdk/azure-keyvault-py.md)
- **Secrets**：[TypeScript](references/sdk/azure-keyvault-secrets-ts.md) | [Rust](references/sdk/azure-keyvault-secrets-rust.md) | [Java](references/sdk/azure-security-keyvault-secrets-java.md)
- **Keys**：[.NET](references/sdk/azure-security-keyvault-keys-dotnet.md) | [Java](references/sdk/azure-security-keyvault-keys-java.md) | [TypeScript](references/sdk/azure-keyvault-keys-ts.md) | [Rust](references/sdk/azure-keyvault-keys-rust.md)
- **Certificates**：[Rust](references/sdk/azure-keyvault-certificates-rust.md)
