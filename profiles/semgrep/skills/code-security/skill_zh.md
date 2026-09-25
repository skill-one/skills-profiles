# 代码安全指南

跨 15+ 种语言的全面安全规则，涵盖 OWASP Top 10、基础设施安全以及编码最佳实践，包含 28 个规则类别。

## 如何使用此功能

**主动模式** — 在编写或审查代码时，根据语言和现有模式自动检查相关漏洞。无需等待用户询问安全问题。

**被动模式** — 当用户询问安全问题时，使用下文中的类别查找相关规则文件，然后阅读该文件以获取详细的漏洞/安全代码示例。

### 工作流程
1. 确定语言和代码功能（处理输入？查询数据库？读取文件？）
2. 检查下文中的相关规则 — 首先关注关键和高影响规则
3. 从 `rules/` 读取特定规则文件，以获取该语言中详细的代码示例
4. 应用安全模式，或在审查时标记漏洞模式

## 语言特定优先规则

在编写这些语言的代码时，首先检查以下规则：

| 语言 | 需要检查的优先规则 |
|------|--------------------|
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
- **SQL 注入** (`rules/sql-injection.md`) - 使用参数化查询，绝不拼接用户输入
- **命令注入** (`rules/command-injection.md`) - 避免使用用户输入的 shell 命令，使用安全 API
- **XSS** (`rules/xss.md`) - 转义输出，使用框架保护
- **XXE** (`rules/xxe.md`) - 禁用 XML 解析器中的外部实体
- **路径遍历** (`rules/path-traversal.md`) - 验证和清理文件路径
- **不安全反序列化** (`rules/insecure-deserialization.md`) - 绝不反序列化不可信数据
- **代码注入** (`rules/code-injection.md`) - 绝不 eval() 用户输入
- **硬编码密钥** (`rules/secrets.md`) - 使用环境变量或密钥管理器
- **内存安全** (`rules/memory-safety.md`) - 防止缓冲区溢出、使用后释放 (C/C++)

### 高影响
- **不安全加密** (`rules/insecure-crypto.md`) - 使用 SHA-256+、AES-256，避免 MD5/SHA1/DES
- **不安全传输** (`rules/insecure-transport.md`) - 使用 HTTPS，验证证书
- **SSRF** (`rules/ssrf.md`) - 验证 URL，使用白名单
- **JWT 问题** (`rules/authentication-jwt.md`) - 始终验证签名
- **CSRF** (`rules/csrf.md`) - 在状态变更请求中使用 CSRF 令牌
- **原型污染** (`rules/prototype-pollution.md`) - 验证 JavaScript 中的对象键

### 基础设施
- **Terraform AWS/Azure/GCP** (`rules/terraform-aws.md`, `rules/terraform-azure.md`, `rules/terraform-gcp.md`) - 加密、最小权限、无公开访问
- **Kubernetes** (`rules/kubernetes.md`) - 无特权容器，以非 root 身份运行
- **Docker** (`rules/docker.md`) - 不要以 root 身份运行，固定镜像版本
- **GitHub Actions** (`rules/github-actions.md`) - 避免脚本注入，固定操作版本

### 中/低影响
- **正则表达式拒绝服务** (`rules/regex-dos.md`) - 避免灾难性回溯
- **竞态条件** (`rules/race-condition.md`) - 使用正确的同步机制
- **正确性** (`rules/correctness.md`) - 避免常见逻辑错误
- **最佳实践** (`rules/best-practice.md`) - 通用安全编码模式

参考 `rules/_sections.md` 获取完整索引及 CWE/OWASP 引用。

## 快速参考

| 漏洞 | 关键预防措施 |
|------|--------------|
| SQL 注入 | 参数化查询 |
| XSS | 输出编码 |
| 命令注入 | 避免使用 shell，使用 API |
| 路径遍历 | 验证路径 |
| SSRF | URL 白名单 |
| 密钥 | 环境变量 |
| 加密 | SHA-256、AES-256 |
