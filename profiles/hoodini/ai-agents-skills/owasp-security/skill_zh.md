# OWASP Top 10 安全

防止 Web 应用中的常见安全漏洞。

## OWASP Top 10 (2021)

| 序号 | 漏洞类型 | 预防措施 |
|---|---|---|
| A01 | 访问控制失效 | 合理的授权检查 |
| A02 | 密码学失效 | 强加密，安全存储 |
| A03 | 注入 | 输入验证，参数化查询 |
| A04 | 不安全设计 | 威胁建模，安全模式 |
| A05 | 安全配置错误 | 硬化配置，无默认值 |
| A06 | 易受攻击的组件 | 依赖项扫描，更新 |
| A07 | 身份验证失败 | 多因素认证，安全会话管理 |
| A08 | 数据完整性失败 | 输入验证，签名更新 |
| A09 | 日志记录失败 | 完整的审计日志 |
| A10 | SSRF | URL 验证，白名单 |

## A01：访问控制失效

### 预防模式
```typescript
// ❌ BAD：无授权检查
app.get('/api/users/:id', async (req, res) => {
  const user = await db.users.findById(req.params.id);
  res.json(user);
});

// ✅ GOOD：验证所有权
app.get('/api/users/:id', authenticate, async (req, res) => {
  const userId = req.params.id;
  
  // 用户只能访问自己的数据
  if (req.user.id !== userId && req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Forbidden' });
  }
  
  const user = await db.users.findById(userId);
  res.json(user);
});

// ✅ GOOD：基于角色的访问控制 (RBAC)
const requireRole = (...roles: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!roles.includes(req.user?.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
};

app.delete('/api/posts/:id', authenticate, requireRole('admin', 'moderator'), deletePost);
```

### 不安全的直接对象引用 (IDOR)
```typescript
// ❌ BAD：暴露可预测的 ID
GET /api/invoices/1001
GET /api/invoices/1002  // 可以枚举其他人的发票

// ✅ GOOD：使用 UUID + 所有权检查
app.get('/api/invoices/:id', authenticate, async (req, res) => {
  const invoice = await db.invoices.findOne({
    id: req.params.id,
    userId: req.user.id,  // 强制所有权
  });
  
  if (!invoice) {
    return res.status(404).json({ error: 'Not found' });
  }
  
  res.json(invoice);
});
```

## A02：密码学失效

### 密码哈希
```typescript
import bcrypt from 'bcrypt';
import crypto from 'crypto';

// ✅ 使用 bcrypt 哈希密码
const SALT_ROUNDS = 12;

async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}

// ✅ 安全令牌生成
function generateSecureToken(length = 32): string {
  return crypto.randomBytes(length).toString('hex');
}

// ✅ 加密敏感数据
const ALGORITHM = 'aes-256-gcm';
const KEY = crypto.scryptSync(process.env.ENCRYPTION_KEY!, 'salt', 32);

function encrypt(text: string): { encrypted: string; iv: string; tag: string } {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(ALGORITHM, KEY, iv);
  
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  
  return {
    encrypted,
    iv: iv.toString('hex'),
    tag: cipher.getAuthTag().toString('hex'),
  };
}

function decrypt(encrypted: string, iv: string, tag: string): string {
  const decipher = crypto.createDecipheriv(ALGORITHM, KEY, Buffer.from(iv, 'hex'));
  decipher.setAuthTag(Buffer.from(tag, 'hex'));
  
  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  
  return decrypted;
}
```

### 安全头部
```typescript
import helmet from 'helmet';

app.use(helmet());
app.use(helmet.hsts({ maxAge: 31536000, includeSubDomains: true }));
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'strict-dynamic'"],
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", 'data:', 'https:'],
    connectSrc: ["'self'"],
    fontSrc: ["'self'"],
    objectSrc: ["'none'"],
    frameAncestors: ["'none'"],
  },
}));
```

## A03：注入

### SQL 注入预防
```typescript
// ❌ BAD：字符串拼接
const query = `SELECT * FROM users WHERE email = '${email}'`;

// ✅ GOOD：参数化查询
// 使用 Prisma
const user = await prisma.user.findUnique({ where: { email } });

// 使用原始 SQL (参数化)
const user = await db.query('SELECT * FROM users WHERE email = $1', [email]);

// 使用 Knex
const user = await knex('users').where({ email }).first();
```

### NoSQL 注入预防
```typescript
// ❌ BAD：查询中直接使用用户输入
const user = await User.findOne({ username: req.body.username });
// 攻击：{ "username": { "$gt": "" } } 返回第一个用户

// ✅ GOOD：验证输入类型
import { z } from 'zod';

const loginSchema = z.object({
  username: z.string().min(3).max(50),
  password: z.string().min(8),
});

app.post('/login', async (req, res) => {
  const { username, password } = loginSchema.parse(req.body);
  const user = await User.findOne({ username: String(username) });
  // ...
});
```

### 命令注入预防
```typescript
import { execFile } from 'child_process';

// ❌ BAD：Shell 注入
exec(`convert ${userInput} output.png`);  // userInput: "; rm -rf /"

// ✅ GOOD：使用 execFile 与数组参数
execFile('convert', [userInput, 'output.png'], (error, stdout) => {
  // 安全 - 参数不会被 Shell 解释
});

// ✅ GOOD：验证和清理
const allowedFormats = ['png', 'jpg', 'gif'];
if (!allowedFormats.includes(format)) {
  throw new Error('Invalid format');
}
```

## A04：不安全设计

### 速率限制
```typescript
import rateLimit from 'express-rate-limit';

// 一般速率限制
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 100, // 每个窗口 100 个请求
  standardHeaders: true,
  legacyHeaders: false,
});

// 身份验证端点的严格限制
const authLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 小时
  max: 5, // 5 次失败尝试
  skipSuccessfulRequests: true,
});

app.use('/api/', limiter);
app.use('/api/auth/', authLimiter);
```

### 输入验证
```typescript
import { z } from 'zod';

const userSchema = z.object({
  email: z.string().email(),
  password: z.string()
    .min(8)
    .regex(/[A-Z]/, 'Must contain uppercase')
    .regex(/[a-z]/, 'Must contain lowercase')
    .regex(/[0-9]/, 'Must contain number')
    .regex(/[^A-Za-z0-9]/, 'Must contain special character'),
  age: z.number().int().min(13).max(120),
  role: z.enum(['user', 'admin']).default('user'),
});

app.post('/api/users', async (req, res) => {
  try {
    const data = userSchema.parse(req.body);
    // 验证后的数据可以安全使用
  } catch (error) {
    if (error instanceof z.ZodError) {
      return res.status(400).json({ errors: error.errors });
    }
    throw error;
  }
});
```

## A05：安全配置错误

### 环境配置
```typescript
// ✅ 生产环境中不暴露堆栈跟踪
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err.stack); // 用于调试的日志
  
  res.status(500).json({
    error: process.env.NODE_ENV === 'production' 
      ? 'Internal server error' 
      : err.message,
  });
});

// ✅ 禁用敏感头部
app.disable('x-powered-by');

// ✅ 安全的 Cookie 配置
app.use(session({
  secret: process.env.SESSION_SECRET!,
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    sameSite: 'strict',
    maxAge: 24 * 60 * 60 * 1000, // 24 小时
  },
  resave: false,
  saveUninitialized: false,
}));
```

## A06：易受攻击的组件

### 依赖项扫描
```bash
# 检查漏洞
npm audit
npm audit fix

# 使用 Snyk 进行更深入的扫描
npx snyk test
npx snyk monitor

# 保持依赖项更新
npx npm-check-updates -u
```

```json
// package.json - 使用确切版本或范围
{
  "dependencies": {
    "express": "^4.18.0",  // 允许小版本更新
    "lodash": "4.17.21"    // 确切版本
  },
  "overrides": {
    "vulnerable-package": "^2.0.0"  // 强制安全版本
  }
}
```

## A07：身份验证失败

### 安全会话管理
```typescript
import jwt from 'jsonwebtoken';

// ✅ 带短有效期的 JWT + 刷新令牌
function generateTokens(userId: string) {
  const accessToken = jwt.sign(
    { userId },
    process.env.JWT_SECRET!,
    { expiresIn: '15m' }  // 短生命周期
  );
  
  const refreshToken = jwt.sign(
    { userId, type: 'refresh' },
    process.env.JWT_REFRESH_SECRET!,
    { expiresIn: '7d' }
  );
  
  return { accessToken, refreshToken };
}

// ✅ 安全密码重置
async function initiatePasswordReset(email: string) {
  const user = await db.users.findByEmail(email);
  if (!user) return; // 不要暴露如果邮箱存在
  
  const token = crypto.randomBytes(32).toString('hex');
  const hashedToken = crypto.createHash('sha256').update(token).digest('hex');
  
  await db.passwordResets.create({
    userId: user.id,
    token: hashedToken,
    expiresAt: new Date(Date.now() + 60 * 60 * 1000), // 1 小时
  });
  
  await sendEmail(email, `Reset link: /reset?token=${token}`);
}
```

### 多因素认证
```typescript
import { authenticator } from 'otplib';
import QRCode from 'qrcode';

// 设置 TOTP
async function setupMFA(userId: string) {
  const secret = authenticator.generateSecret();
  const otpauth = authenticator.keyuri(userId, 'MyApp', secret);
  const qrCode = await QRCode.toDataURL(otpauth);
  
  await db.users.update(userId, { mfaSecret: encrypt(secret) });
  
  return { qrCode, secret };
}

// 验证 TOTP
function verifyMFA(token: string, secret: string): boolean {
  return authenticator.verify({ token, secret });
}
```

## A08：XSS 预防

```typescript
// ✅ React 默认自动转义
const UserProfile = ({ user }) => (
  <div>{user.name}</div>  // 安全 - 自动转义
);

// ⚠️ 危险 - 尽量避免
<div dangerouslySetInnerHTML={{ __html: sanitizedHtml }} />

// ✅ 如果需要，清理 HTML
import DOMPurify from 'dompurify';

const sanitizedHtml = DOMPurify.sanitize(userHtml, {
  ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a'],
  ALLOWED_ATTR: ['href'],
});

// ✅ 内容安全策略
app.use(helmet.contentSecurityPolicy({
  directives: {
    scriptSrc: ["'self'"],  // 无内联脚本
    styleSrc: ["'self'", "'unsafe-inline'"],
  },
}));
```

## A09：日志记录与监控

```typescript
import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
});

// ✅ 记录安全事件
function logSecurityEvent(event: string, details: object) {
  logger.warn({
    type: 'security',
    event,
    ...details,
    timestamp: new Date().toISOString(),
  });
}

// 使用
logSecurityEvent('failed_login', { email, ip: req.ip, userAgent: req.headers['user-agent'] });
logSecurityEvent('access_denied', { userId, resource, action });
logSecurityEvent('suspicious_activity', { userId, pattern: 'rapid_requests' });
```

## A10：SSRF 预防

```typescript
import { URL } from 'url';

// ✅ 对允许列表进行验证的 URL
const ALLOWED_HOSTS = ['api.example.com', 'cdn.example.com'];

function isAllowedUrl(urlString: string): boolean {
  try {
    const url = new URL(urlString);
    
    // 阻止私有 IP
    const privatePatterns = [
      /^localhost$/i,
      /^127\./,
      /^10\./,
      /^172\.(1[6-9]|2[0-9]|3[01])\./,
      /^192\.168\./,
      /^0\./,
      /^169\.254\./,  // 链路本地
    ];
    
    if (privatePatterns.some(p => p.test(url.hostname))) {
      return false;
    }
    
    // 检查允许列表
    return ALLOWED_HOSTS.includes(url.hostname);
  } catch {
    return false;
  }
}

app.post('/api/fetch-url', async (req, res) => {
  const { url } = req.body;
  
  if (!isAllowedUrl(url)) {
    return res.status(400).json({ error: 'URL not allowed' });
  }
  
  const response = await fetch(url);
  // ...
});
```

## 安全检查清单

```markdown
## 部署前检查清单

### 身份验证
- [ ] 密码使用 bcrypt 哈希 (成本 ≥ 12)
- [ ] JWT 令牌有短有效期
- [ ] 会话 Cookie 是 httpOnly、secure、sameSite
- [ ] 身份验证端点有速率限制

### 授权
- [ ] 所有端点都有身份验证检查
- [ ] RBAC 正确实现
- [ ] 无 IDOR 漏洞

### 输入/输出
- [ ] 所有输入使用 Zod/Joi 验证
- [ ] SQL 查询参数化
- [ ] 防止 XSS (CSP、转义)
- [ ] 文件上传验证和沙盒化

### 基础设施
- [ ] 强制 HTTPS
- [ ] 配置安全头部
- [ ] 依赖项审计
- [ ] 密钥在环境变量中

### 监控
- [ ] 记录安全事件
- [ ] 启用错误监控
- [ ] 配置警报
```

## 资源

- **OWASP Top 10**: https://owasp.org/Top10/
- **OWASP 技巧表**: https://cheatsheetseries.owasp.org/
- **Node.js 安全**: https://nodejs.org/en/docs/guides/security/
- **Snyk**: https://snyk.io/
