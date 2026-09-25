# JWT 安全

您是 JSON Web Token (JWT) 安全实现的专家。在处理用于身份验证和授权的 JWT 时，请遵循以下指南。

## 核心原则

- JWT 本身并不安全 - 安全性取决于实现方式
- 始终在服务器端验证令牌，即使是内部服务
- 在可能的情况下使用非对称签名（RS256、ES256）
- 保持令牌短期有效并实现适当的刷新机制
- 不要在 JWT 载荷中存储敏感数据

## 令牌结构

JWT 由三个部分组成：头部、载荷和签名。

```
头部.载荷.签名
```

### 头部最佳实践

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "用于密钥轮换的密钥标识符"
}
```

- 始终包含 `kid`（密钥 ID）以支持密钥轮换
- 明确使用 `typ: "JWT"`
- 绝不接受 `alg: "none"`

### 载荷最佳实践

```json
{
  "iss": "https://auth.example.com",
  "sub": "用户 UUID",
  "aud": "https://api.example.com",
  "exp": 1704067200,
  "iat": 1704063600,
  "nbf": 1704063600,
  "jti": "唯一令牌 ID"
}
```

必需声明：
- `iss`（发行者）：谁创建了令牌
- `sub`（主题）：令牌代表谁
- `aud`（观众）：令牌针对谁
- `exp`（过期）：令牌何时过期
- `iat`（发行时间）：令牌何时创建

推荐声明：
- `nbf`（不早于）：令牌在此时间之前无效
- `jti`（JWT ID）：用于令牌吊销的唯一标识符

## 签名算法选择

### 推荐：非对称算法

```javascript
// RS256 - RSA with SHA-256（最广泛支持）
// ES256 - ECDSA with P-256 and SHA-256（较小的密钥）
// EdDSA - Edwards-curve 数字签名算法（最安全）

const ALLOWED_ALGORITHMS = ['RS256', 'ES256', 'EdDSA'];
```

### 当需要对称算法时

```javascript
// HS256 - HMAC with SHA-256
// 仅使用强密钥（最小 256 位 / 32 字节）
const secret = crypto.randomBytes(64).toString('hex');
```

## 令牌创建

### 使用 RS256（推荐）

```javascript
const jwt = require('jsonwebtoken');
const fs = require('fs');

const privateKey = fs.readFileSync('private.pem');

function createToken(userId, roles) {
  const payload = {
    sub: userId,
    roles: roles,
    // 保持自定义声明最小化
  };

  const options = {
    algorithm: 'RS256',
    expiresIn: '15m', // 短期访问令牌
    issuer: 'https://auth.example.com',
    audience: 'https://api.example.com',
    keyid: '当前密钥 ID',
  };

  return jwt.sign(payload, privateKey, options);
}
```

### 令牌生命周期指南

```javascript
const TOKEN_LIFETIMES = {
  accessToken: '15m',      // 最大 15 分钟
  refreshToken: '7d',      // 7 天轮换
  idToken: '1h',           // 1 小时
  passwordReset: '15m',    // 15 分钟
  emailVerification: '24h', // 24 小时
};
```

## 令牌验证

### 完整验证示例

```javascript
const jwt = require('jsonwebtoken');
const jwksClient = require('jwks-rsa');

// 用于获取公钥的 JWKS 客户端
const client = jwksClient({
  jwksUri: 'https://auth.example.com/.well-known/jwks.json',
  cache: true,
  cacheMaxAge: 600000, // 10 分钟
  rateLimit: true,
  jwksRequestsPerMinute: 10,
});

async function validateToken(token) {
  // 1. 解码头部但不验证以获取 kid
  const decoded = jwt.decode(token, { complete: true });

  if (!decoded) {
    throw new Error('无效的令牌格式');
  }

  // 2. 验证算法是否在白名单中
  if (!ALLOWED_ALGORITHMS.includes(decoded.header.alg)) {
    throw new Error(`算法 ${decoded.header.alg} 不允许`);
  }

  // 3. 获取签名密钥
  const key = await client.getSigningKey(decoded.header.kid);
  const publicKey = key.getPublicKey();

  // 4. 验证签名和声明
  const verified = jwt.verify(token, publicKey, {
    algorithms: ALLOWED_ALGORITHMS, // 算法白名单
    issuer: 'https://auth.example.com',
    audience: 'https://api.example.com',
    clockTolerance: 30, // 30 秒时钟偏差容差
  });

  return verified;
}
```

### 验证检查清单

```javascript
function validateTokenClaims(decoded) {
  const now = Math.floor(Date.now() / 1000);

  // 1. 检查过期时间
  if (decoded.exp && decoded.exp < now) {
    throw new Error('令牌已过期');
  }

  // 2. 检查不早于时间
  if (decoded.nbf && decoded.nbf > now) {
    throw new Error('令牌尚未有效');
  }

  // 3. 检查发行者
  if (decoded.iss !== EXPECTED_ISSUER) {
    throw new Error('无效的发行者');
  }

  // 4. 检查观众
  const audiences = Array.isArray(decoded.aud) ? decoded.aud : [decoded.aud];
  if (!audiences.includes(EXPECTED_AUDIENCE)) {
    throw new Error('无效的观众');
  }

  // 5. 检查必需声明是否存在
  if (!decoded.sub) {
    throw new Error('缺少主题声明');
  }

  return true;
}
```

## 需要预防的安全漏洞

### 1. 算法混淆攻击

```javascript
// 错误：接受任何算法
jwt.verify(token, secret); // 易受攻击！

// 正确：白名单允许的算法
jwt.verify(token, key, { algorithms: ['RS256'] });
```

### 2. 无算法攻击

```javascript
// 始终拒绝 'none' 算法
if (decoded.header.alg === 'none' || decoded.header.alg.toLowerCase() === 'none') {
  throw new Error('不允许算法 none');
}
```

### 3. 密钥混淆（RS256 vs HS256）

```javascript
// 使用非对称密钥时，绝不允许对称算法
const ASYMMETRIC_ONLY = ['RS256', 'RS384', 'RS512', 'ES256', 'ES384', 'ES512', 'EdDSA'];

jwt.verify(token, publicKey, { algorithms: ASYMMETRIC_ONLY });
```

### 4. 弱 HMAC 密钥

```javascript
// HS256 的最小 256 位（32 字节）密钥
// HS384 的最小 384 位（48 字节）密钥
// HS512 的最小 512 位（64 字节）密钥

function generateHmacSecret(algorithm) {
  const bits = parseInt(algorithm.slice(2)); // HS256 -> 256
  const bytes = bits / 8;
  return crypto.randomBytes(Math.max(bytes, 32)).toString('hex');
}
```

## 令牌存储

### 浏览器存储安全

```javascript
// 最佳：HttpOnly cookie（需要后端支持）
// 后端设置：
res.cookie('access_token', token, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict',
  maxAge: 900000, // 15 分钟
});

// 可接受：内存中（刷新时丢失）
let accessToken = null;
function setToken(token) {
  accessToken = token;
}

// 避免：localStorage（易受 XSS 攻击）
// 避免：用于敏感令牌的 sessionStorage
```

### 令牌传输

```javascript
// 始终使用 Authorization 头部
fetch('/api/resource', {
  headers: {
    Authorization: `Bearer ${accessToken}`,
  },
});

// 绝不将令牌放在 URL 中（会被记录、缓存、历史记录可见）
// 错误：/api/resource?token=eyJ...
```

## 刷新令牌实现

```javascript
// 刷新令牌应该：
// 1. 安全存储（HttpOnly cookie 或安全后端存储）
// 2. 每次使用时轮换
// 3. 如果可能，绑定到客户端

async function refreshAccessToken(refreshToken) {
  // 验证刷新令牌
  const decoded = await validateRefreshToken(refreshToken);

  // 检查令牌是否已被吊销
  const isRevoked = await checkTokenRevocation(decoded.jti);
  if (isRevoked) {
    throw new Error('刷新令牌已被吊销');
  }

  // 生成新令牌
  const newAccessToken = createAccessToken(decoded.sub);
  const newRefreshToken = createRefreshToken(decoded.sub);

  // 吊销旧刷新令牌（轮换）
  await revokeToken(decoded.jti);

  return { accessToken: newAccessToken, refreshToken: newRefreshToken };
}
```

## 令牌吊销

```javascript
// 维护一个吊销列表以实现早期令牌无效化
const revokedTokens = new Set(); // 生产环境中使用 Redis

function revokeToken(jti) {
  revokedTokens.add(jti);
}

function isTokenRevoked(jti) {
  return revokedTokens.has(jti);
}

// 在验证中包含吊销检查
async function validateToken(token) {
  const decoded = jwt.verify(token, key, options);

  if (decoded.jti && isTokenRevoked(decoded.jti)) {
    throw new Error('令牌已被吊销');
  }

  return decoded;
}
```

## 密钥轮换

```javascript
// 在轮换期间支持多个密钥
const keyStore = {
  'key-2024-01': { /* 当前密钥 */ },
  'key-2023-12': { /* 旧密钥，仍然有效 */ },
};

// JWKS 端点应公开所有有效的公钥
app.get('/.well-known/jwks.json', (req, res) => {
  const keys = Object.entries(keyStore).map(([kid, key]) => ({
    kid,
    kty: 'RSA',
    use: 'sig',
    alg: 'RS256',
    n: key.publicKey.n,
    e: key.publicKey.e,
  }));

  res.json({ keys });
});
```

## Express 中间件示例

```javascript
const expressJwt = require('express-jwt');
const jwksRsa = require('jwks-rsa');

const jwtMiddleware = expressJwt({
  secret: jwksRsa.expressJwtSecret({
    cache: true,
    rateLimit: true,
    jwksRequestsPerMinute: 5,
    jwksUri: 'https://auth.example.com/.well-known/jwks.json',
  }),
  audience: 'https://api.example.com',
  issuer: 'https://auth.example.com',
  algorithms: ['RS256'],
});

// 受保护的路由
app.get('/api/protected', jwtMiddleware, (req, res) => {
  // req.auth 包含解码后的令牌
  res.json({ user: req.auth.sub });
});
```

## 测试

```javascript
describe('JWT 验证', () => {
  it('应该拒绝过期的令牌', async () => {
    const expiredToken = createToken({ exp: Math.floor(Date.now() / 1000) - 3600 });
    await expect(validateToken(expiredToken)).rejects.toThrow('expired');
  });

  it('应该拒绝具有错误发行者的令牌', async () => {
    const wrongIssuer = createToken({ iss: 'https://evil.com' });
    await expect(validateToken(wrongIssuer)).rejects.toThrow('issuer');
  });

  it('应该拒绝 none 算法', async () => {
    const noneAlg = 'eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxMjM0NTY3ODkwIn0.';
    await expect(validateToken(noneAlg)).rejects.toThrow('algorithm');
  });
});
```

## 常见反模式

1. 使用 JWT 进行会话管理（Web 应用程序应优先使用服务器端会话）
2. 在 JWT 载荷中存储敏感数据（它只是编码，不是加密）
3. 不验证所有声明
4. 使用弱或硬编码的密钥
5. 不实现令牌过期
6. 在未验证的情况下信任算法头部
7. 不实现刷新令牌轮换
8. 记录完整令牌
