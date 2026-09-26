## 何时使用

当您需要执行以下操作时，请使用此技能：
- 在 Fastify 应用中实现或调试 OAuth 2.0/2.1 流
- 验证令牌、配置 PKCE 或设置刷新令牌轮换
- 使用访问控制中间件保护 Fastify 路由和插件
- 解决 RFC 合规性问题或识别安全反模式

---

## 分步指南：Fastify 中的授权码 + PKCE

### 1. 安装依赖项

```bash
npm install @fastify/oauth2 @fastify/cookie @fastify/session fastify-plugin
```

### 2. 注册 OAuth 插件

```typescript
// plugins/oauth.ts
import fp from 'fastify-plugin'
import oauth2, { OAuth2Namespace } from '@fastify/oauth2'
import { FastifyInstance } from 'fastify'

export default fp(async function (fastify: FastifyInstance) {
  fastify.register(oauth2, {
    name: 'oauth2',
    scope: ['openid', 'profile', 'email'],
    credentials: {
      client: {
        id: process.env.CLIENT_ID!,
        secret: process.env.CLIENT_SECRET!,
      },
      auth: {
        authorizeHost: process.env.AUTH_SERVER!,
        authorizePath: '/authorize',
        tokenHost: process.env.AUTH_SERVER!,
        tokenPath: '/token',
      },
    },
    startRedirectPath: '/login',
    callbackUri: process.env.CALLBACK_URI!,
    pkce: 'S256',               // RFC 7636 — 公共客户端始终使用
    generateStateFunction: (req) => req.session.state = crypto.randomUUID(),
    checkStateFunction: (req, callback) =>
      req.query.state === req.session.state ? callback() : callback(new Error('State mismatch')),
  })
})
```

**验证检查点：** 在继续之前，确认 `callbackUri` 与授权服务器中注册的重定向 URI 完全匹配（RFC 6749 §3.1.2）。

### 3. 处理回调并交换代码

```typescript
// routes/auth.ts
import { FastifyInstance } from 'fastify'

export default async function authRoutes(fastify: FastifyInstance) {
  fastify.get('/login/callback', async (request, reply) => {
    // @fastify/oauth2 自动验证 state 并交换代码
    const tokenResponse = await fastify.oauth2.getAccessTokenFromAuthorizationCodeFlow(request)

    // 仅存储所需信息；切勿记录原始令牌
    request.session.set('accessToken', tokenResponse.token.access_token)
    request.session.set('refreshToken', tokenResponse.token.refresh_token)

    return reply.redirect('/')
  })

  fastify.get('/logout', async (request, reply) => {
    await request.session.destroy()
    return reply.redirect('/')
  })
}
```

### 4. JWT 验证中间件（令牌自省钩子）

```typescript
// hooks/verifyToken.ts
import { FastifyRequest, FastifyReply } from 'fastify'
import jwt from '@fastify/jwt'

export async function verifyToken(request: FastifyRequest, reply: FastifyReply) {
  try {
    await request.jwtVerify()
    // 验证必需的声明（RFC 7519）
    const payload = request.user as Record<string, unknown>
    const now = Math.floor(Date.now() / 1000)

    if (typeof payload.exp === 'number' && payload.exp < now)
      return reply.code(401).send({ error: 'token_expired' })

    if (payload.iss !== process.env.EXPECTED_ISSUER)
      return reply.code(401).send({ error: 'invalid_issuer' })

    if (payload.aud !== process.env.EXPECTED_AUDIENCE)
      return reply.code(401).send({ error: 'invalid_audience' })

  } catch (err) {
    return reply.code(401).send({ error: 'invalid_token', error_description: (err as Error).message })
  }
}
```

**验证检查点：**
- 每次请求都验证 `exp`、`iss`、`aud` 和 `sub` — 切勿跳过（RFC 7519 §4）
- 使用 `fastify.jwt.verify`（非对称 RS256/ES256）而不是 HS256，用于第三方服务器颁发的令牌

### 5. 保护路由

```typescript
// routes/api.ts
import { FastifyInstance } from 'fastify'
import { verifyToken } from '../hooks/verifyToken'

export default async function apiRoutes(fastify: FastifyInstance) {
  fastify.addHook('onRequest', verifyToken)   // 应用于此作用域中的所有路由

  fastify.get('/me', {
    schema: {
      response: { 200: { type: 'object', properties: { sub: { type: 'string' } } } },
    },
  }, async (request) => {
    const user = request.user as { sub: string }
    return { sub: user.sub }
  })
}
```

### 6. 刷新令牌轮换

```typescript
async function refreshAccessToken(fastify: FastifyInstance, refreshToken: string) {
  const newToken = await fastify.oauth2.getNewAccessTokenUsingRefreshTokenFlow({ refresh_token: refreshToken })

  // 如果使用轮换，始终替换存储的刷新令牌（RFC 6749 §10.4）
  return {
    accessToken: newToken.token.access_token,
    refreshToken: newToken.token.refresh_token ?? refreshToken,
  }
}
```

---

## 安全检查清单

| 要求 | RFC 参考 |
|---|---|
| 验证重定向 URI 对应白名单 | RFC 6749 §3.1.2 |
| 所有公共客户端使用 PKCE (S256) | RFC 7636 §4.2 |
| 验证 `state` 以防止 CSRF | RFC 6749 §10.12 |
| 每次请求验证 `iss`、`aud`、`exp` | RFC 7519 §4 |
| 每次使用轮换刷新令牌 | RFC 6749 §10.4 |
| 到处使用 HTTPS；拒绝 HTTP 重定向 URI | RFC 6749 §3.1.2.1 |
| 限制令牌端点的速率 | OAuth 2.1 §7 |

---

## 常见反模式

- **将令牌存储在 localStorage 中** — 使用 `HttpOnly`、`Secure`、`SameSite=Strict` cookie 代替
- **跳过受众验证** — 允许令牌跨服务重用
- **使用隐式流** — OAuth 2.1 已弃用；使用授权码 + PKCE
- **在浏览器应用中接受 `response_type=token`** — URL 片段中的令牌在日志/引用器中泄露
- **对第三方令牌使用对称签名 (HS256)** — 使用 RS256/ES256 和 JWKS 端点

---

## 进一步实现参考

- 查看 `DEVICE_FLOW.md` 了解设备授权流实现（RFC 8628）
- 查看 `TOKEN_VALIDATION.md` 了解 JWKS 轮换、缓存策略和 opaque 令牌自省
- 查看 `CLIENT_CREDENTIALS.md` 了解机器到机器服务认证模式
- 查看 `MOBILE_OAUTH.md` 了解原生/移动应用流（RFC 8252）和自定义 URI 方案
