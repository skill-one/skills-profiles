# 技能：子域名接管 — 检测与利用手册

> **AI 加载指令**：涵盖 CNAME/NS/MX 接管、按提供商指纹匹配、申领流程和防御监控。基础模型常将“存在 CNAME”与“可能接管”混淆——关键在于 CNAME 背后的资源是否未被申领且可申领。

## 0. 相关路由

- [ssrf-server-side-request-forgery](../ssrf-server-side-request-forgery/SKILL.md) 当子域名接管用于绕过信任 `*.target.com` 的 SSRF 允许列表时
- [cors-cross-origin-misconfiguration](../cors-cross-origin-misconfiguration/SKILL.md) 当 CORS 信任 `*.target.com` — 接管 → 完全跨域读取
- [xss-cross-site-scripting](../xss-cross-site-scripting/SKILL.md) 接管可在目标源下执行脚本（cookie 窃取、OAuth 重定向滥用）
- [http-host-header-attacks](../http-host-header-attacks/SKILL.md) 当 Host 路由导致子域名范围的缓存或认证问题时
- [web-cache-deception](../web-cache-deception/SKILL.md) 当被接管的子域名与主域名共享缓存时

---

## 1. 核心概念

子域名接管发生时：

1. `sub.target.com` 有 DNS 记录（CNAME、NS、A）指向外部服务
2. 外部资源已**不再配置**（删除的 S3 存储桶、移除的 Heroku 应用等）
3. 攻击者可以**注册/申领**该确切资源名称在提供商处
4. 攻击者现在控制 `sub.target.com` 下的内容

**影响**：cookie 窃取（父域名 cookies）、OAuth 令牌拦截、在可信域下的钓鱼、CORS 绕过、通过白名单子域名绕过 CSP。

---

## 2. 检测方法

### 2.1 CNAME 列举

```
1. 收集子域名（amass、subfinder、assetfinder、crt.sh、SecurityTrails）
2. 为每个解析 DNS：
   dig CNAME sub.target.com +short
3. 对每个 CNAME → 检查 CNAME 目标是否返回 NXDOMAIN 或提供商错误
4. 匹配错误响应与指纹表（第 3 节）
```

### 2.2 关键信号

| 信号 | 含义 |
|---|---|
| CNAME → `xxx.s3.amazonaws.com` + HTTP 404 "NoSuchBucket" | S3 存储桶已删除，可申领 |
| CNAME → `xxx.herokuapp.com` + "No such app" | Heroku 应用已删除 |
| CNAME → `xxx.github.io` + 404 "There isn't a GitHub Pages site here" | GitHub Pages 未申领 |
| CNAME 目标域名本身出现 NXDOMAIN | 目标域名过期或从未存在 |
| CNAME → 提供商但 HTTP 200 带默认停车页面 | 可能或不可能申领 — 验证 |

### 2.3 自动化工具

| 工具 | 目的 |
|---|---|
| `subjack` | 自动化 CNAME 接管检查 |
| `nuclei -t takeovers/` | Nuclei 接管检测模板 |
| `can-i-take-over-xyz` (GitHub) | 查阅哪些服务易受攻击的参考 |
| `dnsreaper` | 多提供商接管扫描器 |
| `subzy` | 快速子域名接管验证 |

---

## 3. 服务提供商指纹表

| 提供商 | CNAME 模式 | 指纹（HTTP 响应） | 可申领？ |
|---|---|---|---|
| **AWS S3** | `*.s3.amazonaws.com` / `*.s3-website-*.amazonaws.com` | `NoSuchBucket` (404) | 是 — 创建匹配名称的存储桶 |
| **GitHub Pages** | `*.github.io` | `There isn't a GitHub Pages site here` (404) | 是 — 创建仓库 + 启用 Pages |
| **Heroku** | `*.herokuapp.com` / `*.herokudns.com` | `No such app` | 是 — 创建匹配名称的应用 |
| **Azure** | `*.azurewebsites.net` / `*.cloudapp.azure.com` / `*.trafficmanager.net` | 各种默认页面，NXDOMAIN | 是 — 注册匹配资源 |
| **Shopify** | `*.myshopify.com` | `Sorry, this shop is currently unavailable` | 是 — 创建商店，添加自定义域名 |
| **Fastly** | CNAME 指向 Fastly 边缘 | `Fastly error: unknown domain` | 是 — 将域名添加到 Fastly 服务 |
| **Pantheon** | `*.pantheonsite.io` | 带有 Pantheon 品牌的 `404 Site Not Found` | 是 |
| **Tumblr** | `*.tumblr.com` (自定义域名 CNAME) | `There's nothing here` / `Whatever you were looking for doesn't exist` | 是 |
| **WordPress.com** | CNAME 指向 `*.wordpress.com` | `Do you want to register` | 是 — 在 WP.com 中申领域名 |
| **Zendesk** | `*.zendesk.com` | `Help Center Closed` / Zendesk 品牌错误页面 | 是 — 创建匹配子域名 |
| **Unbounce** | `*.unbouncepages.com` | `The requested URL was not found` | 是 |
| **Ghost** | `*.ghost.io` | `404 Not Found` Ghost 错误 | 是 |
| **Surge.sh** | `*.surge.sh` | `project not found` | 是 |
| **Fly.io** | CNAME 指向 `*.fly.dev` | Fly.io 默认 404 | 是 |

---

## 4. 接管流程 — 常见提供商

### 4.1 AWS S3

```
1. 确认：curl -s http://sub.target.com → "NoSuchBucket"
2. 从 CNAME 提取存储桶名称（例如，sub.target.com.s3.amazonaws.com → 存储桶 = "sub.target.com"）
3. aws s3 mb s3://sub.target.com --region <region>
4. 上传 index.html 证明控制权
5. 启用静态网站托管
```

### 4.2 GitHub Pages

```
1. 确认：curl -s https://sub.target.com → "There isn't a GitHub Pages site here"
2. 创建 GitHub 仓库（任何名称）
3. 添加 CNAME 文件包含 "sub.target.com"
4. 在仓库设置中启用 GitHub Pages
5. 等待 DNS 传播（GitHub 验证 CNAME 匹配）
```

### 4.3 Heroku

```
1. 确认：curl -s http://sub.target.com → "No such app"
2. heroku create <从 CNAME 获取的 app-name>
3. heroku domains:add sub.target.com
4. 部署概念验证页面
```

---

## 5. NS 接管 — 高严重性

NS 接管比 CNAME 接管**危险得多**：你控制该区域的**所有 DNS 解析**。

### 如何发生

```
target.com NS → ns1.expireddomain.com
                 ↓
attacker 注册 expireddomain.com
                 ↓
attacker 现在控制 target.com 的所有 DNS
(A 记录、MX 记录、TXT 记录 — 所有内容)
```

### 检测

```
1. 列举 NS 记录：dig NS target.com +short
2. 检查每个 NS 域名：whois ns1.example.com → 域名是否过期或可用？
3. 也检查：dig A ns1.example.com → NXDOMAIN/SERVFAIL？
4. 子委托区域：检查特定于 sub.target.com 的 NS
```

### 影响

- 完全域名接管（托管任何内容、拦截邮件、通过 DNS-01 发出 TLS 证书）
- 从任何 CA 通过 DNS 挑战发出 DV 证书
- 修改 SPF/DKIM/DMARC → 发送认证邮件作为 target

---

## 6. MX 接管 — 邮件拦截

当 MX 记录指向已停用的邮件服务时：

```
target.com MX → mail.deadservice.com (服务已停用)
```

如果攻击者可以申领 `mail.deadservice.com` 或邮件租户：
- 接收密码重置邮件
- 拦截敏感通信
- 可能重置使用基于邮件认证的账户

### 常见场景

过期 Google Workspace / Microsoft 365 租户 → MX 仍指向 Google/Microsoft → 攻击者创建新租户并申领该域名。

---

## 7. 通配符 DNS 风险

如果 `*.target.com` 有指向可申领服务的通配符 CNAME：
- **每个**未定义的子域名都易受攻击
- `anything.target.com` 可以被接管
- 大幅增加攻击面

检测：`dig A random1234567.target.com` — 如果解析，则存在通配符。

---

## 8. 检测与利用决策树

```
发现子域名（sub.target.com）？
├── 解析 DNS 记录
│   ├── 有 CNAME 指向外部服务？
│   │   ├── HTTP 响应匹配已知指纹？（第 3 节）
│   │   │   ├── 是 → 尝试在提供商处申领（第 4 节）
│   │   │   │   ├── 申领成功 → 接管确认
│   │   │   │   └── 申领失败（名称保留、区域锁定）→ 记录，尝试变体
│   │   │   └── 否 → 服务活跃，无接管
│   │   └── CNAME 目标 NXDOMAIN？
│   │       ├── 目标是可注册域名？ → 注册它 → 完全控制
│   │       └── 目标是活跃提供商的子域名 → 检查提供商申领流程
│   │
│   ├── 有 NS 记录 → 外部名称服务器？
│   │   ├── NS 域名过期/可用？ → 注册 → 完全区域接管
│   │   └── NS 域名活跃 → 无接管
│   │
│   ├── 有 MX → 外部邮件服务？
│   │   ├── 邮件服务已停用/可申领？ → 申领租户 → 邮件拦截
│   │   └── 活跃邮件服务 → 无接管
│   │
│   └── 有 A 记录 → IP 地址？
│       ├── IP 属于弹性云（AWS EIP、Azure、GCP）？
│       │   ├── IP 未分配？ → 申领 IP → 托管内容
│       │   └── IP 分配给其他客户 → 无接管
│       └── IP 属于专用服务器 → 无接管
│
└── 接管后影响评估
    ├── 与父域名共享 cookies？ → 会话劫持
    ├── CORS 信任 *.target.com？ → 跨域数据窃取
    ├── CSP 白名单 *.target.com？ → 通过被接管子域名执行 XSS
    ├── OAuth redirect_uri 允许 sub.target.com？ → 令牌窃取
    └── 可为 sub.target.com 发出 TLS 证书？ → 完全 MITM
```

---

## 9. 防御与修复

| 行动 | 优先级 |
|---|---|
| 资源停用时删除 DNS 记录 | 关键 |
| 监控 CNAME 目标返回 NXDOMAIN 响应 | 高 |
| 使用 DNS 监控工具（SecurityTrails、DNSHistory） | 高 |
| 删除 DNS 记录前申领/保留资源名称 | 高 |
| 审计 NS 委托 — 确保 NS 域名被拥有和续订 | 关键 |
| 避免指向第三方服务的通配符 CNAME | 中 |
| 实施证书透明度监控 | 中 |

---

## 10. 技巧笔记 — AI 模型遗漏的内容

1. **CNAME ≠ 接管**：指向 S3 的 CNAME 返回 403（存储桶存在，私有）**不**易受攻击。只有 `NoSuchBucket` (404) 才是。
2. **AWS S3 区域重要**：存储桶名称是全局的，但网站端点是区域的。尝试匹配 CNAME 中的区域。
3. **GitHub Pages 验证**：GitHub 添加了域名验证 — org-verified 域名不能被他人申领。检查目标是否使用此功能。
4. **边缘情况**：某些提供商（例如，Cloudfront）需要特定的分发配置，而不仅仅是域名申领。
5. **二级接管**：`sub.target.com CNAME → other.target.com CNAME → dead-service.com` — 必须完全遵循链。
6. **SPF 子域名接管**：如果 SPF 包括 `include:sub.target.com` 且你接管了 `sub.target.com`，你可以修改其 SPF TXT 记录以授权你的邮件服务器 → 发送伪造的 `target.com` 邮件。
