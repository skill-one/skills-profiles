# 安全代码守护者

## 核心工作流程

1. **威胁模型** — 识别攻击面和威胁
2. **设计** — 规划安全控制措施
3. **实现** — 使用纵深防御编写安全代码；下方提供代码示例
4. **验证** — 使用明确的检查点测试安全控制措施（见下文）
5. **文档记录** — 记录安全决策

### 验证检查点

在每一步实现后，验证：

- **身份验证**：测试暴力破解保护（锁定/速率限制触发器）、会话固定抵抗、令牌过期以及无效凭证错误消息（不得泄露用户存在）
- **授权**：验证水平和垂直权限提升路径是否被阻断；使用属于不同角色/用户的令牌进行测试
- **输入处理**：确认拒绝SQL注入载荷（`' OR 1=1--`）；确认对XSS载荷（`<script>alert(1)</script>`）进行转义或拒绝
- **标头/CORS**：使用安全扫描器（例如，`curl -I`，Mozilla观测站）验证安全标头是否存在且CORS来源白名单正确

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时 |
|------|------|------|
| OWASP | `references/owasp-prevention.md` | OWASP Top 10模式 |
| 身份验证 | `references/authentication.md` | 密码哈希，JWT |
| 输入验证 | `references/input-validation.md` | Zod，SQL注入 |
| XSS/CSRF | `references/xss-csrf.md` | XSS预防，CSRF |
| 标头 | `references/security-headers.md` | Helmet，速率限制 |

## 限制条件

### 必须做
- 使用bcrypt/argon2哈希密码（绝不使用MD5/SHA-1/未加盐哈希）
- 使用参数化查询（绝不使用字符串插值的SQL）
- 在使用前验证和清理所有用户输入
- 在身份验证端点上实施速率限制
- 设置安全标头（CSP，HSTS，X-Frame-Options）
- 记录安全事件（失败的身份验证，权限提升尝试）
- 将密钥存储在环境变量或密钥管理器中（绝不存储在源代码中）

### 绝不做
- 以明文或可逆加密形式存储密码
- 在未验证的情况下信任用户输入
- 在日志或错误响应中暴露敏感数据
- 使用弱或已弃用的算法（MD5，SHA-1，DES，ECB模式）
- 在代码中硬编码密钥或凭证

## 代码示例

### 密码哈希（bcrypt）

```typescript
import bcrypt from 'bcrypt';

const SALT_ROUNDS = 12; // 最小值10；12平衡安全性和性能

export async function hashPassword(plaintext: string): Promise<string> {
  return bcrypt.hash(plaintext, SALT_ROUNDS);
}

export async function verifyPassword(plaintext: string, hash: string): Promise<boolean> {
  return bcrypt.compare(plaintext, hash);
}
```

### 参数化SQL查询（Node.js / pg）

```typescript
// 绝不使用：`SELECT * FROM users WHERE email = '${email}'`
// 始终使用：使用位置参数
import { Pool } from 'pg';
const pool = new Pool();

export async function getUserByEmail(email: string) {
  const { rows } = await pool.query(
    'SELECT id, email, role FROM users WHERE email = $1',
    [email]  // 分开传递值 — 绝不插值
  );
  return rows[0] ?? null;
}
```

### 使用Zod进行输入验证

```typescript
import { z } from 'zod';

const LoginSchema = z.object({
  email: z.string().email().max(254),
  password: z.string().min(8).max(128),
});

export function validateLoginInput(raw: unknown) {
  const result = LoginSchema.safeParse(raw);
  if (!result.success) {
    // 返回通用错误 — 绝不回显原始输入
    throw new Error('Invalid credentials format');
  }
  return result.data;
}
```

### JWT验证

```typescript
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET!; // 绝不硬编码

export function verifyToken(token: string): jwt.JwtPayload {
  // 如果过期、被篡改或算法错误则抛出
  const payload = jwt.verify(token, JWT_SECRET, {
    algorithms: ['HS256'],   // 明确白名单算法
    issuer: 'your-app',
    audience: 'your-app',
  });
  if (typeof payload === 'string') throw new Error('Invalid token payload');
  return payload;
}
```

### 保护端点 — 完整流程

```typescript
import express from 'express';
import rateLimit from 'express-rate-limit';
import helmet from 'helmet';

const app = express();
app.use(helmet()); // 设置CSP，HSTS，X-Frame-Options等
app.use(express.json({ limit: '10kb' })); // 限制有效载荷大小

const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15分钟
  max: 10,                   // 每个窗口每个IP 10次尝试
  standardHeaders: true,
  legacyHeaders: false,
});

app.post('/api/login', authLimiter, async (req, res) => {
  // 1. 验证输入
  const { email, password } = validateLoginInput(req.body);

  // 2. 身份验证 — 参数化查询，恒定时间比较
  const user = await getUserByEmail(email);
  if (!user || !(await verifyPassword(password, user.passwordHash))) {
    // 通用消息 — 不要透露邮箱是否存在
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  // 3. 授权 — 发放范围受限、短寿命令牌
  const token = jwt.sign(
    { sub: user.id, role: user.role },
    JWT_SECRET,
    { algorithm: 'HS256', expiresIn: '15m', issuer: 'your-app', audience: 'your-app' }
  );

  // 4. 安全响应 — 令牌在httpOnly cookie中，不在体中
  res.cookie('token', token, { httpOnly: true, secure: true, sameSite: 'strict' });
  return res.json({ message: 'Authenticated' });
});
```

## 输出模板

在实现安全功能时提供：
1. 安全实现代码
2. 安全注意事项
3. 配置要求（环境变量，标头）
4. 测试建议

## 知识参考

OWASP Top 10，bcrypt/argon2，JWT，OAuth 2.0，OIDC，CSP，CORS，速率限制，输入验证，输出编码，加密（AES，RSA），TLS，安全标头

[文档](https://jeffallan.github.io/claude-skills/skills/security/secure-code-guardian/)
