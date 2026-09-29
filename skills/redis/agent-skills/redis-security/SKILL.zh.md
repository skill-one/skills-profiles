---
name: redis-security
description: Redis 安全指南涵盖认证（requirepass 和 ACL 用户）、TLS、基于 ACL 的最小权限访问控制、通过 bind 和保护模式限制网络暴露、防火墙规则以及禁用危险命令。在将 Redis 部署到生产环境、为应用程序定义 ACL 用户、配置 TLS 连接、在防火墙后锁定 Redis 实例，或审计 Redis 部署以进行安全加固时使用。
---

# Redis 安全

为 Redis 进行生产环境加固：认证、基于 ACL 的访问控制以及网络暴露。将这三者结合使用——单独使用其中任何一项都会留下可被利用的漏洞。

## 何时应用

- 部署或审查用于生产环境的 Redis 实例。
- 设置超出共享密码的应用凭证。
- 对照安全清单审计 Redis 部署。
- 接收到扫描器报告的“Redis 暴露于互联网”结果。

## 1. 始终进行认证（并使用 TLS）

不要在不设置密码的情况下运行生产环境的 Redis。将认证与 TLS 结合使用，以便凭证和数据不会以明文形式传输。

```
# redis.conf
requirepass your-strong-password
tls-port 6380
tls-cert-file /path/to/redis.crt
tls-key-file  /path/to/redis.key
```

```python
r = redis.Redis(
    host="localhost",
    port=6380,
    password="your-strong-password",
    ssl=True,
    ssl_cert_reqs="required",
)
```

如果可以的话，使用 ACL 用户（下一节）代替单个 `requirepass`——`requirepass` 实际上是“默认用户”的快捷方式。

参见 [references/auth.md](references/auth.md)。

## 2. 使用 ACL 实现最小权限访问

共享密码的 `default` 用户适用于开发环境。对于生产环境，为每个应用程序分配一个专用的 ACL 用户，仅授予其实际需要的命令和键模式。

```
# 仅缓存读取器
ACL SETUSER app_readonly on >password ~cache:* +get +mget +scan

# 无法执行危险操作的写入器
ACL SETUSER app_writer   on >password ~*        +@all -@dangerous

# 管理员（谨慎使用，切勿用于应用流量）
ACL SETUSER admin        on >strong-password ~* +@all
```

有用的命令类别：

| 类别 | 覆盖范围 |
|---|---|
| `@read` | 读取命令 (`GET`, `MGET`, `HGET`, ...) |
| `@write` | 写入命令 (`SET`, `DEL`, `XADD`, ...) |
| `@dangerous` | `FLUSHALL`, `DEBUG`, `KEYS`, 等。 |
| `@admin` | 管理命令 |

如果应用凭证泄露，严格的 ACL 可以限制破坏范围——攻击者不能仅凭获取缓存读取器的密码就 `FLUSHALL` 你的数据库。

参见 [references/acls.md](references/acls.md)。

## 3. 限制网络访问

最常见的 Redis 漏洞是未设置密码的公网 Redis。通过三层防护来避免这种情况：

```
# redis.conf — 绑定到特定接口，保持受保护模式开启
bind 127.0.0.1 192.168.1.100
protected-mode yes
```

```bash
# 防火墙 — 仅允许应用子网
iptables -A INPUT -p tcp --dport 6379 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 6379 -j DROP
```

反模式：`bind 0.0.0.0` + `protected-mode no`——无保护地将 Redis 暴露给整个网络。

可选但推荐：重命名或禁用破坏性命令，以便受感染的客户端无法破坏数据库：

```
rename-command FLUSHALL ""
rename-command DEBUG ""
rename-command CONFIG ""
```

参见 [references/network.md](references/network.md)。

## 参考资料

- [Redis: 安全](https://redis.io/docs/latest/operate/oss_and_stack/management/security/)
- [Redis: ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/)
