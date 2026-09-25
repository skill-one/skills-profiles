# Azure 合规性与安全审计

## 快速参考

| 属性 | 详情 |
|---|---|
| 最适用于 | 合规性扫描、安全审计、密钥保管库过期检查 |
| 主要功能 | 全面资源评估、密钥保管库过期监控 |
| MCP 工具 | azqr、订阅和资源组列表、密钥保管库项检查 |

## 前置条件

- 身份验证：用户通过 `az login` 登录 Azure
- 具有读取资源配置和密钥保管库元数据的权限

## 评估

| 评估 | 参考 |
|------------|-----------|
| 全面合规性 (azqr) | [references/azure-quick-review.md](references/azure-quick-review.md) |
| 密钥保管库过期 | [references/azure-keyvault-expiration-audit.md](references/azure-keyvault-expiration-audit.md) |
| 资源图查询 | [references/azure-resource-graph.md](references/azure-resource-graph.md) |

## MCP 工具

| 工具 | 目的 |
|------|---------|
| `mcp_azure_mcp_extension_azqr` | 运行 azqr 合规性扫描 |
| `mcp_azure_mcp_subscription_list` | 列出可用订阅 |
| `mcp_azure_mcp_group_list` | 列出资源组 |
| `keyvault_key_list` | 列出保管库中的所有密钥 |
| `keyvault_key_get` | 获取密钥详情，包括过期信息 |
| `keyvault_secret_list` | 列出保管库中的所有密钥 |
| `keyvault_secret_get` | 获取密钥详情，包括过期信息 |
| `keyvault_certificate_list` | 列出保管库中的所有证书 |
| `keyvault_certificate_get` | 获取证书详情，包括过期信息 |

## 评估工作流

1. 选择全面资源评估的范围（订阅或资源组）。
2. 运行 azqr 并捕获输出工件。
3. 分析扫描结果并总结发现和建议。
4. 查看密钥保管库过期监控输出，包括密钥、密钥和证书。
5. 对问题进行分类，并为每个发现提出修复或解决步骤。

### 优先级分类

| 优先级 | 指导 |
|---|---|
| 关键 | 需要立即修复高影响暴露 |
| 高 | 在几天内解决以降低风险 |
| 中 | 计划在下一个迭代中解决 |
| 低 | 在常规维护期间跟踪和修复 |

## 错误处理

| 错误 | 消息 | 修复 |
|---|---|---|
| 需要身份验证 | "请登录" | 运行 `az login` 并重试 |
| 访问被拒绝 | "禁止" | 确认权限并修复角色分配 |
| 缺失资源 | "未找到" | 验证订阅和资源组选择 |

## 最佳实践

- 定期（每周或每月）运行合规性扫描
- 长期跟踪发现并验证修复效果
- 将合规性报告与修复执行分离
- 记录并执行密钥保管库过期策略

## SDK 快速参考

对于程序化密钥保管库访问，请参阅精简的 SDK 指南：

- **密钥保管库 (Python)**：[Secrets/Keys/Certs](references/sdk/azure-keyvault-py.md)
- **密钥**：[TypeScript](references/sdk/azure-keyvault-secrets-ts.md) | [Rust](references/sdk/azure-keyvault-secrets-rust.md) | [Java](references/sdk/azure-security-keyvault-secrets-java.md)
- **密钥**：[.NET](references/sdk/azure-security-keyvault-keys-dotnet.md) | [Java](references/sdk/azure-security-keyvault-keys-java.md) | [TypeScript](references/sdk/azure-keyvault-keys-ts.md) | [Rust](references/sdk/azure-keyvault-keys-rust.md)
- **证书**：[Rust](references/sdk/azure-keyvault-certificates-rust.md)
