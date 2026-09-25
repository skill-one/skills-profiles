# 安全审查技能

这项技能确保所有代码遵循安全最佳实践，并识别潜在的漏洞。

## 详细指南

在执行此技能之前，请阅读[详细指南](references/detailed-guide.md)。它保留了完整流程和参考材料。将其安全要求、先决条件和验证需求视为强制性要求。对于专注工作，加载相关部分；对于端到端工作，完整阅读指南。

## 何时使用
- 实现认证或授权
- 处理用户输入或文件上传
- 创建新的 API 端点
- 处理密钥或凭证
- 实现支付功能
- 存储或传输敏感数据
- 集成第三方 API

## 安全检查清单

### 1. 密钥管理

#### ❌ 绝对不要这样做
```typescript
const leakedToken = "[redacted API key]"  // 硬编码密钥
const dbCredential = "[redacted password]" // 源代码中
```

#### ✅ 始终这样做
```typescript
const apiKey = process.env.OPENAI_API_KEY
const dbUrl = process.env.DATABASE_URL

// 验证密钥是否存在
if (!apiKey) {
  throw new Error('OPENAI_API_KEY 未配置')
}
```

#### 验证步骤
- [ ] 无硬编码的 API 密钥、令牌或密码
- [ ] 所有密钥存储在环境变量中
- [ ] `.env.local` 在 .gitignore 中
- [ ] 无密钥存储在 git 历史记录中
- [ ] 生产密钥存储在托管平台（Vercel、Railway）

### 2. 输入验证

#### 始终验证用户输入
```typescript
import { z } from 'zod'

// 定义验证模式
const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  age: z.number().int().min(0).max(150)
})

// 验证后再处理
export async function createUser(input: unknown) {
  try {
    const validated = CreateUserSchema.parse(input)
    return await db.users.create(validated)
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { success: false, errors: error.errors }
    }
    throw error
  }
}
```

#### 文件上传验证
```typescript
function validateFileUpload(file: File) {
  // 大小检查（最大 5MB）
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    throw new Error('文件过大（最大 5MB）')
  }

  // 类型检查
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    throw new Error('无效的文件类型')
  }

  // 扩展名检查
  const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif']
  const extension = file.name.toLowerCase().match(/\.[^.]+$/)?.[0]
  if (!extension || !allowedExtensions.includes(extension)) {
    throw new Error('无效的文件扩展名')
  }

  return true
}
```

#### 验证步骤
- [ ] 所有用户输入使用模式验证
- [ ] 文件上传限制（大小、类型、扩展名）
- [ ] 查询中不直接使用用户输入
- [ ] 白名单验证（非黑名单）
- [ ] 错误消息不泄露敏感信息

### 3. SQL 注入防护

#### ❌ 绝对不要拼接 SQL
```typescript
// 危险 - SQL 注入漏洞
const query = `SELECT * FROM users WHERE email = '${userEmail}'`
await db.query(query)
```

#### ✅ 始终使用参数化查询
```typescript
// 安全 - 参数化查询
const { data } = await supabase
  .from('users')
  .select('*')
  .eq('email', userEmail)

// 或使用原始 SQL
await db.query(
  'SELECT * FROM users WHERE email = $1',
  [userEmail]
)
```

#### 验证步骤
- [ ] 所有数据库查询使用参数化查询
- [ ] SQL 中无字符串拼接
- [ ] 正确使用 ORM/查询构建器
- [ ] Supabase 查询正确清理

### 4. 认证与授权

#### JWT 令牌处理
```typescript
// ❌ 错误：localStorage（易受 XSS 攻击）
localStorage.setItem('token', token)

// ✅ 正确：httpOnly cookie
res.setHeader('Set-Cookie',
  `token=${token}; HttpOnly; Secure; SameSite=Strict; Max-Age=3600`)
```

#### 授权检查
```typescript
export async function deleteUser(userId: string, requesterId: string) {
  // 始终先验证授权
  const requester = await db.users.findUnique({
    where: { id: requesterId }
  })

  if (requester.role !== 'admin') {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 403 }
    )
  }

  // 继续执行删除
  await db.users.delete({ where: { id: userId } })
}
```

#### 行级安全（Supabase）
```sql
-- 在所有表中启用 RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 用户只能查看自己的数据
CREATE POLICY "Users view own data"
  ON users FOR SELECT
  USING (auth.uid() = id);

-- 用户只能更新自己的数据
CREATE POLICY "Users update own data"
  ON users FOR UPDATE
  USING (auth.uid() = id);
```

#### 验证步骤
- [ ] 令牌存储在 httpOnly cookie（非 localStorage）
- [ ] 敏感操作前进行授权检查
- [ ] Supabase 中启用行级安全
- [ ] 实现基于角色的访问控制
- [ ] 会话管理安全

### 5. XSS 防护

#### 清理 HTML
```typescript
import DOMPurify from 'isomorphic-dompurify'

// 始终清理用户提供的 HTML
function renderUserContent(html: string) {
  const clean = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p'],
    ALLOWED_ATTR: []
  })
  return <div dangerouslySetInnerHTML={{ __html: clean }} />
}
```

#### 内容安全策略
```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: `
      default-src 'self';
      script-src 'self' 'unsafe-eval' 'unsafe-inline';
      style-src 'self' 'unsafe-inline';
      img-src 'self' data: https:;
      font-src 'self';
      connect-src 'self' https://api.example.com;
    `.replace(/\s{2,}/g, ' ').trim()
  }
]
```

#### 验证步骤
- [ ] 清理用户提供的 HTML
- [ ] 配置 CSP 头
- [ ] 无未验证的动态内容渲染
- [ ] 使用 React 的内置 XSS 防护

### 6. CSRF 防护

#### CSRF 令牌
```typescript
import { csrf } from '@/lib/csrf'

export async function POST(request: Request) {
  const token = request.headers.get('X-CSRF-Token')

  if (!csrf.verify(token)) {
    return NextResponse.json(
      { error: '无效的 CSRF 令牌' },
      { status: 403 }
    )
  }

  // 处理请求
}
```

#### SameSite cookie
```typescript
res.setHeader('Set-Cookie',
  `session=${sessionId}; HttpOnly; Secure; SameSite=Strict`)
```

#### 验证步骤
- [ ] 状态变更操作有 CSRF 令牌
- [ ] 所有 cookie 设置 SameSite=Strict
- [ ] 实现双重提交 cookie 模式

### 7. 速率限制

#### API 速率限制
```typescript
import rateLimit from 'express-rate-limit'

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 100, // 每个窗口 100 个请求
  message: '请求过多'
})

// 应用于路由
app.use('/api/', limiter)
```

#### 费用操作
```typescript
// 搜索操作使用激进速率限制
const searchLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 分钟
  max: 10, // 每分钟 10 个请求
  message: '搜索请求过多'
})

app.use('/api/search', searchLimiter)
```

#### 验证步骤
- [ ] 所有 API 端点有速率限制
- [ ] 费用操作有更严格的限制
- [ ] 基于 IP 的速率限制
- [ ] 基于用户的速率限制（认证）

### 8. 敏感数据暴露

#### 日志记录
```typescript
// ❌ 错误：记录敏感数据
console.log('User login:', { email, password })
console.log('Payment:', { cardNumber, cvv })

// ✅ 正确：清理敏感数据
console.log('User login:', { email, userId })
console.log('Payment:', { last4: card.last4, userId })
```

#### 错误消息
```typescript
// ❌ 错误：泄露内部细节
catch (error) {
  return NextResponse.json(
    { error: error.message, stack: error.stack },
    { status: 500 }
  )
}

// ✅ 正确：通用错误消息
catch (error) {
  console.error('Internal error:', error)
  return NextResponse.json(
    { error: '发生错误，请重试' },
    { status: 500 }
  )
}
```

#### 验证步骤
- [ ] 日志中无密码、令牌或密钥
- [ ] 错误消息对用户通用
- [ ] 服务器日志中记录详细错误
- [ ] 不向用户暴露堆栈跟踪

### 9. 区块链安全（Solana）

#### 钱包验证
```typescript
import { verify } from '@solana/web3.js'

async function verifyWalletOwnership(
  publicKey: string,
  signature: string,
  message: string
) {
  try {
    const isValid = verify(
      Buffer.from(message),
      Buffer.from(signature, 'base64'),
      Buffer.from(publicKey, 'base64')
    )
    return isValid
  } catch (error) {
    return false
  }
}
```

#### 交易验证
```typescript
async function verifyTransaction(transaction: Transaction) {
  // 验证接收方
  if (transaction.to !== expectedRecipient) {
    throw new Error('无效的接收方')
  }

  // 验证金额
  if (transaction.amount > maxAmount) {
    throw new Error('金额超出限制')
  }

  // 验证用户余额足够
  const balance = await getBalance(transaction.from)
  if (balance < transaction.amount) {
    throw new Error('余额不足')
  }

  return true
}
```

#### 验证步骤
- [ ] 钱包签名验证
- [ ] 交易详情验证
- [ ] 交易前检查余额
- [ ] 无盲交易签名

### 10. 依赖安全

#### 定期更新
```bash
# 检查漏洞
npm audit

# 自动修复可修复问题
npm audit fix

# 更新依赖
npm update

# 检查过时的包
npm outdated
```

#### 锁文件
```bash
# 始终提交锁文件
git add package-lock.json

# 在 CI/CD 中使用以实现可重复构建
npm ci  # 而不是 npm install
```

#### 验证步骤
- [ ] 依赖更新到最新版本
- [ ] 无已知漏洞（npm audit clean）
- [ ] 提交锁文件
- [ ] GitHub 上启用 Dependabot
- [ ] 定期进行安全更新

## 安全测试

### 自动化安全测试
```typescript
// 测试认证
test('requires authentication', async () => {
  const response = await fetch('/api/protected')
  expect(response.status).toBe(401)
})

// 测试授权
test('requires admin role', async () => {
  const response = await fetch('/api/admin', {
    headers: { Authorization: `Bearer ${userToken}` }
  })
  expect(response.status).toBe(403)
})

// 测试输入验证
test('rejects invalid input', async () => {
  const response = await fetch('/api/users', {
    method: 'POST',
    body: JSON.stringify({ email: 'not-an-email' })
  })
  expect(response.status).toBe(400)
})

// 测试速率限制
test('enforces rate limits', async () => {
  const requests = Array(101).fill(null).map(() =>
    fetch('/api/endpoint')
  )

  const responses = await Promise.all(requests)
  const tooManyRequests = responses.filter(r => r.status === 429)

  expect(tooManyRequests.length).toBeGreaterThan(0)
})
```

## 限制
- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家审查的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
