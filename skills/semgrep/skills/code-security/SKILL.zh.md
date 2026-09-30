---
name: code-security
description: 编写安全代码的安全指南。在编写代码、审查代码漏洞或询问安全编码实践（如“检查SQL注入”或“审查安全性”）时使用。重要提示：在编写或审查任何处理用户输入、身份验证、文件操作、数据库查询、网络请求、加密或基础设施配置（Terraform、Kubernetes、Docker、GitHub Actions）的代码时，请始终参考此技能——即使用户没有明确提及安全性。在用户要求“审查我的代码”、“检查此处的错误”或“这是安全的吗”时也使用。
---

# 代码安全指南

跨 15+ 种语言的全面安全规则，涵盖 OWASP Top 10、基础设施安全和编码最佳实践，包含 28 个规则类别。

## 如何使用此技能

**主动模式** — 在编写或审查代码时，根据语言和模式自动检查相关漏洞。无需等待用户询问安全问题。

**被动模式** — 当用户询问安全问题时，使用下文中的类别查找相关规则文件，然后阅读该文件以获取详细的有漏洞/安全代码示例。

### 工作流程
1. 确定语言和代码功能（处理输入？查询数据库？读取文件？）
2. 检查下文中的相关规则——首先关注关键和高影响规则
3. 从 `rules/` 中读取特定规则文件，以获取该语言中的详细代码示例
4. 应用安全模式，或在审查时标记有漏洞的模式

## 语言特定优先规则

在用这些语言编写代码时，首先检查这些规则：

| 语言 | 需要检查的优先规则 |
|----------|------------------------|
| **Python** | SQL 注入、命令注入、路径遍历、代码注入、SSRF、不安全加密 |
| **JavaScript/TypeScript** | XSS、原型污染、代码注入、不安全传输、CSRF |
| **Java** | SQL 注入、XXE、不安全反序列化、不安全加密、SSRF |
| **Go** | SQL 注入、命令注入、路径遍历、不安全传输 |
| **C/C++** | 内存安全、不安全函数、命令注入、路径遍历 |
| **Ruby** | SQL 注入、命令注入、代码注入、不安全反序列化 |
| **PHP** | SQL 注入、XSS、命令注入、代码注入、路径遍历 |
| **HCL/YAML** | Terraform (AWS/Azure/GCP)、Kubernetes、Docker、GitHub Actions |

## 类别

### 关键影响
- **SQL 注入** (`rules/sql-injection.md`) - 使用参数化查询，永远不要连接用户输入
- **命令注入** (`rules/command-injection.md`) - 避免使用用户输入的 shell 命令，使用安全 API
- **XSS** (`rules/xss.md`) - 转义输出，使用框架保护
- **XXE** (`rules/xxe.md`) - 禁用 XML 解析器中的外部实体
- **路径遍历** (`rules/path-traversal.md`) - 验证和清理文件路径
- **不安全反序列化** (`rules/insecure-deserialization.md`) - 永远不要反序列化不可信数据
- **代码注入** (`rules/code-injection.md`) - 永远不要 `eval()` 用户输入
- **硬编码密钥** (`rules/secrets.md`) - 使用环境变量或密钥管理器
- **内存安全** (`rules/memory-safety.md`) - 防止缓冲区溢出、使用后释放 (C/C++)

### 高影响
- **不安全加密** (`rules/insecure-crypto.md`) - 使用 SHA-256+、AES-256，避免 MD5/SHA1/DES
- **不安全传输** (`rules/insecure-transport.md`) - 使用 HTTPS，验证证书
- **SSRF** (`rules/ssrf.md`) - 验证 URL，使用白名单
- **JWT 问题** (`rules/authentication-jwt.md`) - 始终验证签名
- **CSRF** (`rules/csrf.md`) - 在状态改变请求上使用 CSRF 令牌
- **原型污染** (`rules/prototype-pollution.md`) - 验证 JavaScript 中的对象键

### 基础设施
- **Terraform AWS/Azure/GCP** (`rules/terraform-aws.md`, `rules/terraform-azure.md`, `rules/terraform-gcp.md`) - 加密、最小权限、无公共访问
- **Kubernetes** (`rules/kubernetes.md`) - 无特权容器，以非 root 身份运行
- **Docker** (`rules/docker.md`) - 不要以 root 身份运行，固定镜像版本
- **GitHub Actions** (`rules/github-actions.md`) - 避免脚本注入，固定操作版本

### 中/低影响
- **正则表达式拒绝服务** (`rules/regex-dos.md`) - 避免灾难性回溯
- **竞态条件** (`rules/race-condition.md`) - 使用适当的同步
- **正确性** (`rules/correctness.md`) - 避免常见逻辑错误
- **最佳实践** (`rules/best-practice.md`) - 通用安全编码模式

参考 `rules/_sections.md` 获取完整索引和 CWE/OWASP 引用。

## 快速参考

| 漏洞 | 关键预防措施 |
|--------------|----------------|
| SQL 注入 | 参数化查询 |
| XSS | 输出编码 |
| 命令注入 | 避免使用 shell，使用 API |
| 路径遍历 | 验证路径 |
| SSRF | URL 白名单 |
| 密钥 | 环境变量 |
| 加密 | SHA-256、AES-256 |
