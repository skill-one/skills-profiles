# OWASP 安全检查

针对 Web 应用和 REST API 的全面安全审计模式。包含 5 个类别中的 20 条规则，涵盖 OWASP Top 10 和常见的 Web 漏洞。

## 适用场景

在以下情况下使用此技能：

- 审计代码库中的安全漏洞
- 审查用户提供的文件或文件夹中的安全问题
- 检查身份验证/授权实现
- 评估 REST API 安全性
- 评估数据保护措施
- 审查配置和部署设置
- 生产部署前
- 添加处理敏感数据的新功能后

## 如何使用此技能

1. **识别应用类型** - Web 应用、REST API、SPA、SSR 或混合类型
2. **按优先级扫描** - 先从 CRITICAL 规则开始，然后是 HIGH，然后是 MEDIUM
3. **审查相关规则文件** - 从 @rules/ 目录加载特定规则
4. **报告发现结果** - 注明严重性、文件位置和影响
5. **提供修复建议** - 给出具体的代码示例用于修复

## 审计工作流程

### 第 1 步：按优先级系统审查

按优先级逐个审查类别：

1. **CRITICAL**：身份验证 & 授权、数据保护、输入/输出安全
2. **HIGH**：配置 & 标头
3. **MEDIUM**：API & 监控

### 第 2 步：生成报告

以以下格式报告发现结果：

- **严重性**：CRITICAL | HIGH | MEDIUM | LOW
- **类别**：规则名称
- **文件**：路径和行号
- **问题**：错误内容
- **影响**：安全后果
- **修复**：修复的代码示例

## 规则摘要

### 身份验证 & 授权 (CRITICAL)

#### broken-access-control - @rules/broken-access-control.md

检查缺少授权、IDOR、权限提升。

```typescript
// 不好：无授权检查
async function getUser(req: Request): Promise<Response> {
  let url = new URL(req.url);
  let userId = url.searchParams.get("id");
  let user = await db.user.findUnique({ where: { id: userId } });
  return new Response(JSON.stringify(user));
}

// 好：验证所有权
async function getUser(req: Request): Promise<Response> {
  let session = await getSession(req);
  let url = new URL(req.url);
  let userId = url.searchParams.get("id");

  if (session.userId !== userId && !session.isAdmin) {
    return new Response("Forbidden", { status: 403 });
  }

  let user = await db.user.findUnique({ where: { id: userId } });
  return new Response(JSON.stringify(user));
}
```

#### authentication-failures - @rules/authentication-failures.md

检查弱身份验证、缺少 MFA、会话问题。

```typescript
// 不好：弱密码检查
if (password.length >= 6) {
  /* allow */
}

// 好：强密码要求
function validatePassword(password: string) {
  if (password.length < 12) return false;
  if (!/[A-Z]/.test(password)) return false;
  if (!/[a-z]/.test(password)) return false;
  if (!/[0-9]/.test(password)) return false;
  if (!/[^A-Za-z0-9]/.test(password)) return false;
  return true;
}
```

### 数据保护 (CRITICAL)

#### cryptographic-failures - @rules/cryptographic-failures.md

检查弱加密、明文存储、不良哈希。

```typescript
// 不好：MD5 用于密码
let hash = crypto.createHash("md5").update(password).digest("hex");

// 好：bcrypt 带盐
let hash = await bcrypt(password, 12);
```

#### sensitive-data-exposure - @rules/sensitive-data-exposure.md

检查日志/响应中的 PII、错误消息泄露信息。

```typescript
// 不好：暴露敏感数据
return new Response(JSON.stringify(user)); // 包含密码哈希、电子邮件等

// 好：仅返回所需字段
return new Response(
  JSON.stringify({
    id: user.id,
    username: user.username,
    displayName: user.displayName,
  }),
);
```

#### data-integrity-failures - @rules/data-integrity-failures.md

检查无签名数据、不安全的反序列化。

```typescript
// 不好：信任无签名的 JWT
let decoded = JSON.parse(atob(token.split(".")[1]));
if (decoded.isAdmin) {
  /* grant access */
}

// 好：验证签名
let payload = await verifyJWT(token, secret);
```

#### secrets-management - @rules/secrets-management.md

检查硬编码的密钥、暴露的环境变量。

```typescript
// 不好：硬编码密钥
const API_KEY = "sk_live_a1b2c3d4e5f6";

// 好：环境变量
let API_KEY = process.env.API_KEY;
if (!API_KEY) throw new Error("API_KEY 未配置");
```

### 输入/输出安全 (CRITICAL)

#### injection-attacks - @rules/injection-attacks.md

检查 SQL、XSS、NoSQL、命令、路径遍历注入。

```typescript
// 不好：SQL 注入
let query = `SELECT * FROM users WHERE email = '${email}'`;

// 好：参数化查询
let user = await db.user.findUnique({ where: { email } });
```

#### ssrf-attacks - @rules/ssrf-attacks.md

检查未验证的 URL、内部网络访问。

```typescript
// 不好：获取用户提供的 URL
let url = await req.json().then((d) => d.url);
let response = await fetch(url);

// 好：验证白名单
const ALLOWED_DOMAINS = ["api.example.com", "cdn.example.com"];
let url = new URL(await req.json().then((d) => d.url));
if (!ALLOWED_DOMAINS.includes(url.hostname)) {
  return new Response("Invalid URL", { status: 400 });
}
```

#### file-upload-security - @rules/file-upload-security.md

检查无限制上传、MIME 验证。

```typescript
// 不好：无文件类型验证
let file = await req.formData().then((fd) => fd.get("file"));
await writeFile(`./uploads/${file.name}`, file);

// 好：验证类型和扩展名
const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];
const ALLOWED_EXTS = [".jpg", ".jpeg", ".png", ".webp"];
let file = await req.formData().then((fd) => fd.get("file") as File);

if (!ALLOWED_TYPES.includes(file.type)) {
  return new Response("Invalid file type", { status: 400 });
}
```

#### redirect-validation - @rules/redirect-validation.md

检查开放重定向、未验证的重定向 URL。

```typescript
// 不好：未验证重定向
let returnUrl = new URL(req.url).searchParams.get("return");
return Response.redirect(returnUrl);

// 好：验证重定向 URL
let returnUrl = new URL(req.url).searchParams.get("return");
let allowed = ["/dashboard", "/profile", "/settings"];
if (!allowed.includes(returnUrl)) {
  return Response.redirect("/");
}
```

### 配置 & 标头 (HIGH)

#### insecure-design - @rules/insecure-design.md

检查架构中的安全反模式。

```typescript
// 不好：安全通过混淆
let isAdmin = req.headers.get("x-admin-secret") === "admin123";

// 好：适当的基于角色的访问控制
let session = await getSession(req);
let isAdmin = await db.user
  .findUnique({
    where: { id: session.userId },
  })
  .then((u) => u.role === "ADMIN");
```

#### security-misconfiguration - @rules/security-misconfiguration.md

检查默认配置、调试模式、错误处理。

```typescript
// 不好：暴露堆栈跟踪
catch (error) {
  return new Response(error.stack, { status: 500 });
}

// 好：通用错误消息
catch (error) {
  console.error(error); // 仅服务器端记录
  return new Response("Internal server error", { status: 500 });
}
```

#### security-headers - @rules/security-headers.md

检查 CSP、HSTS、X-Frame-Options 等。

```typescript
// 不好：无安全标头
return new Response(html);

// 好：设置安全标头
return new Response(html, {
  headers: {
    "Content-Security-Policy": "default-src 'self'",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  },
});
```

#### cors-configuration - @rules/cors-configuration.md

检查过于宽松的 CORS。

```typescript
// 不好：带凭证的通配符
headers.set("Access-Control-Allow-Origin", "*");
headers.set("Access-Control-Allow-Credentials", "true");

// 好：特定来源
let allowedOrigins = ["https://app.example.com"];
let origin = req.headers.get("origin");
if (origin && allowedOrigins.includes(origin)) {
  headers.set("Access-Control-Allow-Origin", origin);
}
```

#### csrf-protection - @rules/csrf-protection.md

检查 CSRF 令牌、SameSite cookie。

```typescript
// 不好：无 CSRF 保护
let cookies = parseCookies(req.headers.get("cookie"));
let session = await getSession(cookies.sessionId);

// 好：SameSite cookie + 令牌验证
return new Response("OK", {
  headers: {
    "Set-Cookie": "session=abc; SameSite=Strict; Secure; HttpOnly",
  },
});
```

#### session-security - @rules/session-security.md

检查 cookie 标志、JWT 问题、令牌存储。

```typescript
// 不好：不安全的 cookie
return new Response("OK", {
  headers: { "Set-Cookie": "session=abc123" },
});

// 好：带所有标志的安全 cookie
return new Response("OK", {
  headers: {
    "Set-Cookie":
      "session=abc123; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=3600",
  },
});
```

### API & 监控 (MEDIUM-HIGH)

#### api-security - @rules/api-security.md

检查 REST API 漏洞、批量赋值。

```typescript
// 不好：批量赋值漏洞
let userData = await req.json();
await db.user.update({ where: { id }, data: userData });

// 好：显式允许字段
let { displayName, bio } = await req.json();
await db.user.update({
  where: { id },
  data: { displayName, bio }, // 仅允许字段
});
```

#### rate-limiting - @rules/rate-limiting.md

检查缺少速率限制、暴力破解预防。

```typescript
// 不好：无速率限制
async function login(req: Request): Promise<Response> {
  let { email, password } = await req.json();
  // 允许无限登录尝试
}

// 好：速率限制
let ip = req.headers.get("x-forwarded-for");
let { success } = await ratelimit.limit(ip);
if (!success) {
  return new Response("Too many requests", { status: 429 });
}
```

#### logging-monitoring - @rules/logging-monitoring.md

检查日志不足、日志中的敏感数据。

```typescript
// 不好：记录敏感数据
console.log("User login:", { email, password, ssn });

// 好：记录事件而不记录敏感数据
console.log("User login attempt", {
  email,
  ip: req.headers.get("x-forwarded-for"),
  timestamp: new Date().toISOString(),
});
```

#### vulnerable-dependencies - @rules/vulnerable-dependencies.md

检查过时的包、已知 CVE。

```bash
# 不好：无依赖检查
npm install

# 好：定期审计
npm audit
npm audit fix
```

## 常见漏洞模式

快速参考要查找的模式：

- **无验证的用户输入**：`req.json()` → 立即使用
- **缺少认证检查**：无授权中间件的路线
- **硬编码密钥**：包含 "password"、"secret"、"key" 的字符串
- **SQL 注入**：查询中的字符串连接
- **XSS**：`dangerouslySetInnerHTML`, `.innerHTML`
- **弱加密**：`md5`, `sha1` 用于密码
- **缺少标头**：无 CSP、HSTS 或安全标头
- **CORS 通配符**：`Access-Control-Allow-Origin: *` 带凭证
- **不安全的 cookie**：缺少 Secure、HttpOnly、SameSite 标志
- **路径遍历**：未验证的用户输入在文件路径中

## 严重性快速参考

**立即修复 (CRITICAL)：**

- SQL/XSS/命令注入
- 敏感端点缺少身份验证
- 代码中硬编码的密钥
- 明文密码存储
- IDOR 漏洞

**尽快修复 (HIGH)：**

- 缺少 CSRF 保护
- 弱密码要求
- 缺少安全标头
- 过于宽松的 CORS
- 不安全的会话管理

**可能时修复 (MEDIUM)：**

- 缺少速率限制
- 不完整的日志
- 过时的依赖（无已知漏洞）
- 非关键字段缺少输入验证

**改进 (LOW)：**

- 缺少可选的安全标头
- 非生产环境的详细错误消息
- 不理想的加密参数
