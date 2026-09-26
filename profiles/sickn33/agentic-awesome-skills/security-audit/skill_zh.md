# 安全审计工作流包

## 概述

适用于 Web 应用、API 和基础设施的全面安全审计工作流。该包协调渗透测试、漏洞评估、安全扫描和修复等技能。

## 何时使用此工作流

当您需要执行以下操作时，请使用此工作流：
- 对 Web 应用进行安全审计
- 测试 API 安全性
- 进行渗透测试
- 扫描漏洞
- 加强应用安全
- 合规性安全评估

## 工作流阶段

### 阶段 1：侦察

#### 需要调用的技能
- `scanning-tools` - 安全扫描
- `shodan-reconnaissance` - Shodan 搜索
- `top-web-vulnerabilities` - OWASP Top 10

#### 操作
1. 确定目标范围
2. 收集情报
3. 绘制攻击面
4. 识别技术
5. 记录发现结果

#### 复制粘贴提示
```
使用 @scanning-tools 执行初始侦察
```

```
使用 @shodan-reconnaissance 查找暴露的服务
```

### 阶段 2：漏洞扫描

#### 需要调用的技能
- `vulnerability-scanner` - 漏洞分析
- `security-scanning-security-sast` - 静态分析
- `security-scanning-security-dependencies` - 依赖扫描

#### 操作
1. 运行自动扫描器
2. 执行静态分析
3. 扫描依赖项
4. 识别配置错误
5. 记录漏洞

#### 复制粘贴提示
```
使用 @vulnerability-scanner 扫描 OWASP Top 10 漏洞
```

```
使用 @security-scanning-security-dependencies 审计依赖项
```

### 阶段 3：Web 应用测试

#### 需要调用的技能
- `top-web-vulnerabilities` - OWASP 漏洞
- `sql-injection-testing` - SQL 注入
- `xss-html-injection` - XSS 测试
- `broken-authentication` - 身份验证测试
- `idor-testing` - IDOR 测试
- `file-path-traversal` - 路径遍历
- `burp-suite-testing` - Burp Suite 测试

#### 操作
1. 测试注入缺陷
2. 测试身份验证机制
3. 测试会话管理
4. 测试访问控制
5. 测试输入验证
6. 测试安全头

#### 复制粘贴提示
```
使用 @sql-injection-testing 测试 SQL 注入漏洞
```

```
使用 @xss-html-injection 测试跨站脚本
```

```
使用 @broken-authentication 测试身份验证安全
```

### 阶段 4：API 安全测试

#### 需要调用的技能
- `api-fuzzing-bug-bounty` - API 混淆
- `api-security-best-practices` - API 安全

#### 操作
1. 列举 API 端点
2. 测试身份验证/授权
3. 测试速率限制
4. 测试输入验证
5. 测试错误处理
6. 记录 API 漏洞

#### 复制粘贴提示
```
使用 @api-fuzzing-bug-bounty 混淆 API 端点
```

### 阶段 5：渗透测试

#### 需要调用的技能
- `pentest-commands` - 渗透测试命令
- `pentest-checklist` - 渗透测试规划
- `ethical-hacking-methodology` - 道德黑客
- `metasploit-framework` - Metasploit

#### 操作
1. 规划渗透测试
2. 执行攻击场景
3. 利用漏洞
4. 记录概念验证
5. 评估影响

#### 复制粘贴提示
```
使用 @pentest-checklist 规划渗透测试
```

```
使用 @pentest-commands 执行渗透测试
```

### 阶段 6：安全加固

#### 需要调用的技能
- `security-scanning-security-hardening` - 安全加固
- `auth-implementation-patterns` - 身份验证
- `api-security-best-practices` - API 安全

#### 操作
1. 实施安全控制
2. 配置安全头
3. 设置身份验证
4. 实施授权
5. 配置日志记录
6. 应用补丁

#### 复制粘贴提示
```
使用 @security-scanning-security-hardening 加固应用安全
```

### 阶段 7：报告

#### 需要调用的技能
- `reporting-standards` - 安全报告

#### 操作
1. 记录发现结果
2. 评估风险等级
3. 提供修复步骤
4. 创建执行摘要
5. 生成技术报告

## 安全测试清单

### OWASP Top 10
- [ ] 注入（SQL、NoSQL、OS、LDAP）
- [ ] 身份验证失效
- [ ] 敏感数据暴露
- [ ] XML 外部实体 (XXE)
- [ ] 访问控制失效
- [ ] 安全配置错误
- [ ] 跨站脚本 (XSS)
- [ ] 不安全的反序列化
- [ ] 使用已知漏洞的组件
- [ ] 日志和监控不足

### API 安全
- [ ] 身份验证机制
- [ ] 授权检查
- [ ] 速率限制
- [ ] 输入验证
- [ ] 错误处理
- [ ] 安全头

## 质量门禁

- [ ] 所有计划测试已执行
- [ ] 漏洞已记录
- [ ] 概念验证已捕获
- [ ] 风险评估已完成
- [ ] 修复步骤已提供
- [ ] 报告已生成

## 相关工作流包

- `development` - 安全开发实践
- `wordpress` - WordPress 安全
- `cloud-devops` - 云安全
- `testing-qa` - 安全测试

## 限制
- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
