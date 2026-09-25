# 安全审计技能

## 目的
全面的代码库安全扫描和漏洞检测。包括输入验证、路径遍历防护、CVE检测和安全编码模式强制执行。

## 触发时机
- 身份验证实现
- 授权逻辑
- 支付处理
- 用户数据处理
- API端点创建
- 文件上传处理
- 数据库查询
- 外部API集成

## 跳过时机
- 对公共数据的只读操作
- 内部开发工具
- 静态文档
- 样式更改

## 命令

### 全量安全扫描
对代码库执行全面的安全分析

```bash
npx @claude-flow/cli security scan --depth full
```

**示例:**
```bash
npx @claude-flow/cli security scan --depth full --output security-report.json
```

### 输入验证检查
检查输入验证问题

```bash
npx @claude-flow/cli security scan --check input-validation
```

**示例:**
```bash
npx @claude-flow/cli security scan --check input-validation --path ./src/api
```

### 路径遍历检查
检查路径遍历漏洞

```bash
npx @claude-flow/cli security scan --check path-traversal
```

### SQL注入检查
检查SQL注入漏洞

```bash
npx @claude-flow/cli security scan --check sql-injection
```

### XSS检查
检查跨站脚本漏洞

```bash
npx @claude-flow/cli security scan --check xss
```

### CVE扫描
扫描依赖项中的已知CVE

```bash
npx @claude-flow/cli security cve --scan
```

**示例:**
```bash
npx @claude-flow/cli security cve --scan --severity high
```

### 安全审计报告
生成完整的安全审计报告

```bash
npx @claude-flow/cli security audit --report
```

**示例:**
```bash
npx @claude-flow/cli security audit --report --format markdown --output SECURITY.md
```

### 威胁建模
执行威胁建模分析

```bash
npx @claude-flow/cli security threats --analyze
```

### 验证密钥
检查硬编码的密钥

```bash
npx @claude-flow/cli security validate --check secrets
```

## 脚本

| 脚本 | 路径 | 描述 |
|------|------|------|
| `security-scan` | `.agents/scripts/security-scan.sh` | 运行全量安全扫描流程 |
| `cve-remediate` | `.agents/scripts/cve-remediate.sh` | 自动修复已知CVE |

## 参考

| 文档 | 路径 | 描述 |
|------|------|------|
| `Security Checklist` | `docs/security-checklist.md` | 安全审查清单 |
| `OWASP Guide` | `docs/owasp-top10.md` | OWASP Top 10缓解指南 |

## 最佳实践
1. 开始前检查内存中的现有模式
2. 使用分层拓扑进行协调
3. 完成后存储成功的模式
4. 记录任何新的学习成果
