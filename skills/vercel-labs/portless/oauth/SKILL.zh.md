---
name: oauth
description: 配置 OAuth 提供商（如 Google、Apple、Microsoft、Facebook、GitHub 等）以与无端口本地开发 URL 配合使用。在设置 OAuth 重定向 URI、修复 "redirect_uri_mismatch" 或 "invalid redirect" 错误、为本地开发配置登录提供商，或当提供商拒绝 .localhost 子域时使用。触发条件包括 "OAuth 无端口无法工作"、"重定向 URI 不匹配"、"Google/Apple/Microsoft 本地登录失败"、"为本地开发配置 OAuth"，或任何涉及无端口域的 OAuth 回调 URL 的任务。
---

# 使用 Portless 进行 OAuth

OAuth 提供商会对重定向 URI 进行域名规则验证。`.localhost` 子域名在大多数提供商那里都会失败，因为它们不在公共后缀列表中，或者被明确阻止。Portless 通过 `--tld` 参数解决了这个问题，可以在真实有效的域名上运行应用。

## 问题

当 portless 使用默认的 `.localhost` TLD 时，OAuth 提供商会拒绝像 `http://myapp.localhost:1355/callback` 这样的重定向 URI：

| 提供商  | `localhost` | `.localhost` 子域名 | 原因                         |
| ------- | ---------- | ------------------ | ---------------------------- |
| Google  | 允许       | 拒绝               | 不在其捆绑的 PSL 中         |
| Apple  | 拒绝       | 拒绝               | 完全没有 localhost          |
| Microsoft | 允许       | 允许               | 对 localhost 处理宽松       |
| Facebook | 允许       | 变化               | 必须精确注册每个 URI        |
| GitHub  | 允许       | 允许               | 宽松                         |

Google 和 Apple 最严格。Microsoft 和 GitHub 对 localhost 更宽松。

## 解决方法

使用有效的 TLD，以便重定向 URI 通过提供商的验证：

```bash
portless proxy start --tld dev
portless myapp next dev
# -> https://myapp.dev
```

公共后缀列表中的任何 TLD 都可以工作：`.dev`、`.app`、`.com`、`.io` 等。

### 使用你拥有的域名

像 `.dev` 这样的裸 TLD 意味着 `myapp.dev` 可能会与真实域名冲突。在受你控制的域名下使用多段 TLD，这样应用名称保持干净，域名结构存在于 TLD 中：

```bash
portless proxy start --tld local.yourcompany.dev
portless myapp next dev
# -> https://myapp.local.yourcompany.dev
```

这确保了没有出站流量到达你不拥有的地址。对于团队，设置一个通配符 DNS 记录（`*.local.yourcompany.dev -> 127.0.0.1`），这样每个开发者都可以无需 `/etc/hosts` 就解析，并且每个开发者在提供商控制台中共享相同的重定向 URI。

## 提供商设置

### Google

1. 前往 [Google Cloud Console > Credentials](https://console.cloud.google.com/apis/credentials)
2. 创建或编辑 OAuth 2.0 客户端 ID（Web 应用）
3. 将 portless 域名添加到 **授权的 JavaScript 原点**：`https://myapp.dev`
4. 将回调添加到 **授权的重定向 URI**：`https://myapp.dev/api/auth/callback/google`

Google 根据公共后缀列表验证域名。域名必须以受识别的 TLD 结尾。`.localhost` 子域名会通过这个检查；`.dev`、`.app`、`.com` 等。都会通过。

HTTPS 对于 `.dev` 和 `.app` 是必需的（HSTS 预加载）。Portless 通过 `--https` 自动处理这一点。

### Apple

Apple Sign In 完全不允许 `localhost` 或 IP 地址。

1. 前往 [Apple Developer > Certificates, Identifiers & Profiles](https://developer.apple.com/account/resources)
2. 注册一个服务 ID
3. 配置 Apple Sign In，将 portless 域名作为 **返回 URL** 添加：`https://myapp.dev/api/auth/callback/apple`

域名必须是一个真实、公开可解析的域名。由于 portless 将域名映射到本地 127.0.0.1，浏览器可以解析它，但 Apple 的服务器端验证可能要求域名公开解析。如果 Apple 拒绝域名，为你的开发子域名添加一个指向 127.0.0.1 的公共 DNS A 记录。

### Microsoft (Entra / Azure AD)

1. 前往 [Azure Portal > 应用注册](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps)
2. 创建或编辑应用注册
3. 在 **身份验证** 下添加一个 **Web** 重定向 URI：`https://myapp.dev/api/auth/callback/azure-ad`

Microsoft 允许开发中使用 `http://localhost` 任何端口。它还接受大多数情况下的 `.localhost` 子域名。使用 portless 配合自定义 TLD 仍然建议跨提供商保持一致性。

### Facebook (Meta)

1. 前往 [Meta for Developers > App Dashboard](https://developers.facebook.com/apps/)
2. 在 **Facebook Login > 设置** 下，将 portless URL 添加到 **有效的 OAuth 重定向 URI**：`https://myapp.dev/api/auth/callback/facebook`

Facebook 要求每个重定向 URI 必须精确注册（不允许通配符）。严格模式（默认启用）强制精确匹配。

### GitHub

1. 前往 [GitHub Developer Settings > OAuth Apps](https://github.com/settings/developers)
2. 设置 **授权回调 URL**：`https://myapp.dev/api/auth/callback/github`

GitHub 对 localhost 和子域名持宽松态度。自定义 TLD 不是必需的，但可以保持设置的一致性。

## 认证库配置

### NextAuth / Auth.js

将 `NEXTAUTH_URL` 设置为匹配 portless 域名：

```env
NEXTAUTH_URL=https://myapp.dev
```

NextAuth 使用这个来构建回调 URL。如果没有它，回调可能会使用 `localhost` 并导致不匹配。

### Passport.js

在每个策略中将 `callbackURL` 设置为使用 portless 域名：

```js
new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  callbackURL: process.env.BASE_URL + "/auth/google/callback",
});
```

将 `BASE_URL=https://myapp.dev` 设置在你的环境中。

### 通用 / 手动

读取 portless 注入到子进程中的 `PORTLESS_URL` 环境变量：

```js
const baseUrl = process.env.PORTLESS_URL || "http://localhost:3000";
const callbackUrl = `${baseUrl}/auth/callback`;
```

## 故障排除

### "redirect_uri_mismatch" 或 "invalid redirect URI"

OAuth 流中发送的重定向 URI 与提供商注册的不匹配。检查：

1. 提供商注册的重定向 URI 与 portless 域名完全匹配（协议、主机、路径）
2. `NEXTAUTH_URL` 或等效项设置为 portless URL（不是 `localhost`）
3. 代理以正确的 TLD 运行（使用 `portless list` 验证）

### 提供商要求 HTTPS

`.dev` 和 `.app` TLD 是 HSTS 预加载的，所以浏览器强制使用 HTTPS。启动代理：

```bash
portless proxy start --tld dev
```

Portless 默认在 443 端口上使用 HTTPS（自动使用 sudo 提升权限）。运行 `portless trust` 将本地 CA 添加到你的系统信任存储中，并消除浏览器警告。

### Apple 拒绝域名

Apple 可能要求域名公开解析。为你的开发子域名添加一个指向 `127.0.0.1` 的 DNS A 记录：

```
myapp.local.yourcompany.dev  A  127.0.0.1
```

或者使用通配符：`*.local.yourcompany.dev  A  127.0.0.1`。

### 登录后回调到错误的 URL

认证库正在从 `localhost` 而不是 portless 域名构建回调 URL。设置适当的环境变量：

- **NextAuth**：`NEXTAUTH_URL=https://myapp.dev`
- **Auth.js v5**：`AUTH_URL=https://myapp.dev`
- **手动**：`PORTLESS_URL` 会自动注入；将其用作基础 URL

## 示例

查看 [`examples/google-oauth`](../../examples/google-oauth) 以获取一个完整的 Next.js + NextAuth + Google OAuth 使用 `--tld dev` 的示例。
