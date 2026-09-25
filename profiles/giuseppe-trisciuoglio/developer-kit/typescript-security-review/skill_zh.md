# TypeScript 安全审查

## 概述

针对 TypeScript/Node.js 应用的安全审查。评估代码是否符合 OWASP Top 10、框架特定模式和生产就绪标准。发现的问题按严重程度（关键、高、中、低）分类，并提供修复示例。将深度分析委托给 `typescript-security-expert` 代理。

## 使用场景

- 对 TypeScript/Node.js 代码库进行安全审计
- 审查身份验证和授权实现（JWT、OAuth2、Passport.js）
- 检查常见漏洞（XSS、注入、CSRF、路径遍历）
- 验证输入验证和清理逻辑
- 审查依赖安全（npm audit、已知 CVE）
- 检查密钥管理和环境变量处理
- 评估 API 安全（速率限制、CORS、安全头）
- 审查 Express、NestJS 或 Next.js 安全配置
- 部署到生产环境前或代码重大变更后
- 合规性检查（GDPR、HIPAA、SOC2 数据处理要求）

## 指南

1. **确定范围**：确定哪些文件和模块在审查范围内。优先考虑身份验证、授权、数据处理、API 端点和配置文件。使用 `grep` 查找安全敏感模式（`eval`、`exec`、`innerHTML`、密码处理、JWT 操作）。

   **检查点**：在继续之前，验证至少识别了 3 个安全敏感文件/模块。

2. **检查身份验证和授权**：审查 JWT 实现（签名算法、过期时间、刷新令牌）、OAuth2/OIDC 集成、会话管理、密码哈希（bcrypt/argon2）和双因素认证。验证受保护路由强制执行身份验证。

   **检查点**：使用 `grep` 确认所有路由处理器都应用了身份验证守卫或中间件。

3. **扫描注入漏洞**：检查数据库查询中的 SQL/NoSQL 注入、`exec`/`spawn` 中的命令注入、模板注入和 LDAP 注入。验证参数化查询和输入验证。

   **检查点**：使用 `grep` 确认所有数据库查询都使用参数化——不使用字符串连接与用户输入。

4. **审查输入验证**：检查使用 Zod、Joi 或 class-validator 验证 API 输入。验证模式完整性——正确的类型约束、长度限制、格式验证。检查验证绕过路径。

   **检查点**：验证所有公共 API 端点都有相应的验证模式。

5. **评估 XSS 防范**：审查 React 组件的 `dangerouslySetInnerHTML` 使用情况，检查内容安全策略头，验证用户生成内容的 HTML 清理。参见 `references/xss-prevention.md` 获取详细模式。

   **检查点**：使用 `grep` 确认任何 `dangerouslySetInnerHTML` 使用都有通过 DOMPurify 或等效工具进行清理。

6. **检查密钥管理**：扫描硬编码凭证、API 密钥、源代码中的密钥。验证 `.env` 文件被 gitignore，通过正确的管理服务访问密钥。

   **检查点**：运行 `grep -r "password\|secret\|api.*key\|token" --include="*.ts"` 来识别代码中的潜在密钥。

7. **审查依赖安全**：运行 `npm audit` 或检查 `package-lock.json` 中的已知漏洞。识别有 CVE 的过时依赖项。检查不必要的依赖项。

   **检查点**：验证 `npm audit` 结果已审查并解决了关键漏洞。

8. **评估安全头和配置**：检查 helmet.js 或手动配置的安全头。审查 CORS 策略、速率限制、HTTPS 强制执行、Cookie 安全标志（HttpOnly、Secure、SameSite）和 CSP。参见 `references/security-headers.md` 获取配置示例。

   **检查点**：使用 `grep` 确认全局应用了 helmet 或等效安全头。

9. **生成安全报告**：生成结构化报告，包含按严重程度分类的发现、修复指南和代码示例，以及安全态势摘要。

   **反馈循环**：如果发现关键或高漏洞，在最终确定前重新扫描相关模块以查找类似模式。使用 `grep` 确认是否存在相同的漏洞模式。

## 示例

### JWT 安全审查

```typescript
// ❌ 关键：弱 JWT 配置
import jwt from 'jsonwebtoken';

const SECRET = 'mysecret123'; // 硬编码弱密钥

function generateToken(user: User) {
  return jwt.sign({ id: user.id, role: user.role }, SECRET);
  // 缺少过期时间、弱密钥、未指定算法
}

// ✅ 安全：正确的 JWT 配置
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET || JWT_SECRET.length < 32) {
  throw new Error('JWT_SECRET 必须设置且至少 32 个字符');
}

function generateToken(user: User): string {
  return jwt.sign(
    { sub: user.id }, // 最小化声明，不含敏感数据
    JWT_SECRET,
    {
      algorithm: 'HS256',
      expiresIn: '15m',
      issuer: 'my-app',
      audience: 'my-app-client',
    }
  );
}

function verifyToken(token: string): JwtPayload {
  return jwt.verify(token, JWT_SECRET, {
    algorithms: ['HS256'], // 限制接受的算法
    issuer: 'my-app',
    audience: 'my-app-client',
  }) as JwtPayload;
}
```

### SQL 注入防范

```typescript
// ❌ 关键：SQL 注入漏洞
async function findUser(email: string) {
  const result = await db.query(
    `SELECT * FROM users WHERE email = '${email}'`
  );
  return result.rows[0];
}

// ✅ 安全：参数化查询
async function findUser(email: string) {
  const result = await db.query(
    'SELECT id, name, email FROM users WHERE email = $1',
    [email]
  );
  return result.rows[0];
}

// ✅ 安全：类型安全的 ORM 查询（Drizzle 示例）
async function findUser(email: string) {
  return db.select({
    id: users.id,
    name: users.name,
    email: users.email,
  })
  .from(users)
  .where(eq(users.email, email))
  .limit(1);
}
```

参见 `references/xss-prevention.md` 获取 XSS 模式和 `references/security-headers.md` 获取安全头配置。

## 审查输出格式

按以下结构组织所有安全审查发现：

### 1. 安全态势摘要
整体安全评估分数（1-10）以及关键观察结果和风险级别。

### 2. 关键漏洞（立即行动）
可被利用以危害系统、窃取数据或导致未授权访问的问题。

### 3. 高优先级（30 天内解决）
安全配置错误、缺失保护或需要近期修复的漏洞。

### 4. 中优先级（90 天内解决）
降低安全态势但具有缓解因素或有限可利用性的问题。

### 5. 低优先级（下一周期）
安全改进、硬化建议和纵深防御增强。

### 6. 积极安全观察
认可的良好实现安全模式和做法。

### 7. 修复路线图
按优先级排序的行动项，包含最关键修复的代码示例。

## 最佳实践

- 在 API 边界验证所有输入——不要单独信任客户端验证
- 使用参数化查询或 ORM——不要将用户输入连接到查询
- 将密钥存储在环境变量或密钥管理器中——不要存储在源代码中
- 对数据库账户、API 密钥和 IAM 角色应用最小权限原则
- 启用安全头（helmet.js）并将 CORS 限制为已知来源
- 对所有面向公众的端点实施速率限制
- 使用 bcrypt 或 argon2 哈希密码——不要使用 MD5/SHA 哈希密码
- 设置 Cookie 标志：`HttpOnly`、`Secure`、`SameSite=Strict`
- 在 CI 管道中使用 `npm audit` 捕获依赖漏洞
- 记录安全事件（失败登录、权限拒绝）而不记录敏感数据

## 限制和警告

- 安全审查不能替代专业的渗透测试
- 专注于代码级漏洞——基础设施安全不在范围内
- 尊重项目框架——提供特定框架的修复指南
- 不要记录、打印或暴露发现的密钥——仅报告其位置
- 依赖漏洞应评估实际可利用性，而不仅仅是存在
- 安全建议必须实用——考虑实施工作量与风险降低的权衡

## 参考

参见 `references/` 目录中的详细安全文档：
- `references/owasp-typescript.md` — OWASP Top 10 映射到 TypeScript/Node.js 模式
- `references/common-vulnerabilities.md` — 常见漏洞模式和修复
- `references/dependency-security.md` — 依赖扫描和供应链安全
- `references/xss-prevention.md` — React 和服务器端的 XSS 防范模式
- `references/security-headers.md` — 安全头和 CORS 配置示例
- `references/input-validation.md` — 使用 Zod 和 class-validator 的输入验证模式
