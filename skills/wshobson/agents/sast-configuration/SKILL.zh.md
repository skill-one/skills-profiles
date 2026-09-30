---
name: sast-configuration
description: 配置静态应用安全测试（SAST）工具，用于自动检测应用程序代码中的漏洞。在设置安全扫描、实施DevSecOps实践或自动化代码漏洞检测时使用。
---

# 静态应用安全测试（SAST）配置

静态应用安全测试（SAST）工具的设置、配置和自定义规则创建，以实现跨多种编程语言的综合安全扫描。

## 概述

本技能提供有关设置和配置SAST工具（包括Semgrep、SonarQube和CodeQL）的全面指导。当您需要以下功能时，请使用此技能：

- 在CI/CD管道中设置SAST扫描
- 为您的代码库创建自定义安全规则
- 配置质量门禁和合规策略
- 优化扫描性能并减少误报
- 集成多个SAST工具以实现纵深防御

## 核心功能

### 1. Semgrep配置

- 基于模式匹配的自定义规则创建
- 针对特定语言的安全规则（Python、JavaScript、Go、Java等）
- CI/CD集成（GitHub Actions、GitLab CI、Jenkins）
- 误报调整和规则优化
- 组织策略执行

### 2. SonarQube设置

- 质量门禁配置
- 安全热点分析
- 代码覆盖率和技术债务跟踪
- 针对特定语言的定制质量配置文件
- 与LDAP/SAML的企业集成

### 3. CodeQL分析

- GitHub高级安全集成
- 自定义查询开发
- 漏洞变体分析
- 安全研究工作流
- SARIF结果处理

## 快速入门

### 初始评估

1. 确定代码库中的主要编程语言
2. 确定合规要求（PCI-DSS、SOC 2等）
3. 根据语言支持和集成需求选择SAST工具
4. 查看基线扫描以了解当前安全状况

### 基本设置

```bash
# Semgrep快速入门
pip install semgrep
semgrep --config=auto --error

# 使用Docker的SonarQube
docker run -d --name sonarqube -p 9000:9000 sonarqube:10.8-community

# CodeQL CLI设置
gh extension install github/gh-codeql
codeql database create mydb --language=python
```

## 集成模式

### CI/CD管道集成

```yaml
# GitHub Actions示例
- name: 运行Semgrep
  uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/security-audit
      p/owasp-top-ten
```

### 提交前钩子

```bash
# .pre-commit-config.yaml
- repo: https://github.com/returntocorp/semgrep
  rev: v1.45.0
  hooks:
    - id: semgrep
      args: ['--config=auto', '--error']
```

## 最佳实践

1. **从基线开始**
   - 运行初始扫描以建立安全基线
   - 优先处理关键和高严重性发现
   - 创建修复路线图

2. **渐进式采用**
   - 从安全相关的规则开始
   - 逐步添加代码质量规则
   - 仅对关键问题实施阻断

3. **误报管理**
   - 记录合法的抑制项
   - 为已知安全模式创建允许列表
   - 定期审查被抑制的发现

4. **性能优化**
   - 排除测试文件和生成代码
   - 对大型代码库使用增量扫描
   - 在CI/CD中缓存扫描结果

5. **团队赋能**
   - 为开发人员提供安全培训
   - 创建内部文档以记录常见模式
   - 建立安全专家计划

## 常见用例

### 新项目设置

```bash
./scripts/run-sast.sh --setup --language python --tools semgrep,sonarqube
```

### 自定义规则开发

```yaml
# 参考文档/semgrep-rules.md获取详细示例
rules:
  - id: hardcoded-jwt-secret
    pattern: jwt.encode($DATA, "...", ...)
    message: JWT密钥不应硬编码
    severity: ERROR
```

### 合规扫描

```bash
# PCI-DSS聚焦扫描
semgrep --config p/pci-dss --json -o pci-scan-results.json
```

## 故障排除

### 高误报率

- 审查和调整规则灵敏度
- 添加路径过滤器以排除测试文件
- 对嘈杂模式使用nostmt元数据
- 创建组织特定的规则例外

### 性能问题

- 启用增量扫描
- 跨模块并行化扫描
- 优化规则模式以提高效率
- 缓存依赖项和扫描结果

### 集成失败

- 验证API令牌和凭证
- 检查网络连接和代理设置
- 审查SARIF输出格式兼容性
- 验证CI/CD运行器权限

## 相关技能

- [STRIDE分析模式](../stride-analysis-patterns/SKILL.md)
- [威胁缓解映射](../threat-mitigation-mapping/SKILL.md)

## 工具对比

| 工具      | 适合场景                 | 语言支持 | 成本            | 集成   |
| --------- | ------------------------ | ---------------- | --------------- | ------------- |
| Semgrep   | 自定义规则、快速扫描     | 30+语言    | 免费/企业版     | 优秀     |
| SonarQube | 代码质量+安全            | 25+语言    | 免费/商业版     | 良好          |
| CodeQL    | 深度分析、研究          | 10+语言    | 免费（开源）      | GitHub原生 |

## 下一步

1. 完成初始SAST工具设置
2. 运行基线安全扫描
3. 为组织特定模式创建自定义规则
4. 集成到CI/CD管道
5. 建立安全门禁策略
6. 对开发团队进行发现和修复培训
