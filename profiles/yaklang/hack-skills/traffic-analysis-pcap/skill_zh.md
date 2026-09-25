# 技能：流量分析与PCAP — 专家分析手册

> **AI 加载指令**：专家级流量分析与PCAP取证技术。涵盖PCAP修复、Wireshark核心过滤器、协议特定分析（HTTP、HTTPS/TLS、DNS、FTP、SMTP、USB HID、WiFi、ICMP）、数据提取（文件雕刻、凭证收集、隐蔽通道）、NetworkMiner以及tshark命令行分析。基础模型会遗漏USB键盘解码模式、DNS隧道检测启发式规则以及TLS解密工作流。

## 0. 相关路由

在深入之前，可以考虑加载：

- [内存取证-volatility](../memory-forensics-volatility/SKILL.md) 用于关联内存取证与网络流量
- [隐写术技术](../steganography-techniques/SKILL.md) 用于分析从流量捕获中提取的文件
- [网络协议攻击](../network-protocol-attacks/SKILL.md) 用于理解捕获中可见的攻击模式
- [反向shell技术](../reverse-shell-techniques/SKILL.md) 用于识别捕获中的shell流量

---

## 1. PCAP修复

```bash
pcapfix corrupted.pcap -o fixed.pcap           # 修复损坏的PCAP
# 奇数字节：d4c3b2a1=小端PCAP，a1b2c3d4=大端PCAP，0a0d0d0a=PCAPNG
editcap -F pcap capture.pcapng capture.pcap    # 转换pcapng→pcap
mergecap -w merged.pcap file1.pcap file2.pcap  # 合并捕获
```

---

## 2. Wireshark核心过滤器

### IP / 主机过滤器

```
ip.addr == 10.0.0.1                  # 源或目标
ip.src == 10.0.0.1                   # 仅源
ip.dst == 10.0.0.1                   # 仅目标
ip.addr == 10.0.0.0/24              # 子网
!(ip.addr == 10.0.0.1)              # 排除主机
```

### 协议过滤器

```
http                                  # 所有HTTP
dns                                   # 所有DNS
tcp                                   # 所有TCP
ftp                                   # 所有FTP
smtp                                  # 所有SMTP
tls                                   # 所有TLS/SSL
icmp                                  # 所有ICMP
arp                                   # 所有ARP
```

### TCP / 流

```
tcp.stream eq 5                       # 跟踪特定TCP流
tcp.port == 80                        # 80端口流量
tcp.flags.syn == 1 && tcp.flags.ack == 0   # SYN数据包（连接开始）
tcp.analysis.retransmission           # 重传数据包
tcp.len > 0                           # 带有效载荷的数据包
```

### HTTP

```
http.request.method == "POST"         # POST请求
http.request.method == "GET"          # GET请求
http.response.code == 200             # 成功响应
http.response.code >= 400             # 错误响应
http.request.uri contains "login"     # URI包含字符串
http.host contains "target.com"       # 特定主机
http.content_type contains "json"     # JSON响应
http.cookie contains "session"        # 会话cookie
http.request.full_uri                 # 显示完整URI（列）
```

### DNS

```
dns.qry.name contains "evil.com"     # 特定域名查询
dns.qry.type == 1                    # A记录
dns.qry.type == 28                   # AAAA记录
dns.qry.type == 16                   # TXT记录
dns.flags.response == 1              # 仅DNS响应
dns.resp.len > 100                   # 大型DNS响应
```

### TLS

```
tls.handshake.type == 1              # Client Hello
tls.handshake.type == 2              # Server Hello
tls.handshake.extensions.server_name  # SNI（主机名）
tls.handshake.type == 11             # 证书
```

### 内容搜索

```
frame contains "password"             # 原始字节中搜索
frame contains "flag{"                # CTF标志模式
tcp contains "admin"                  # 在TCP有效载荷中搜索
```

---

## 3. 协议分析

### HTTP — 跟踪流与提取

```
右键单击数据包 → 跟踪 → TCP流
# 显示完整的HTTP请求/响应对话

# 文件提取：
# 文件 → 导出对象 → HTTP → 保存全部

# 用于凭证搜索的有用过滤器：
http.request.method == "POST" && frame contains "password"
http.request.method == "POST" && frame contains "login"
http.authbasic                        # Basic认证（base64编码）
```

### HTTPS / TLS解密

```bash
# 方法1：SSLKEYLOGFILE（来自浏览器的预主密钥）
# 在打开浏览器之前设置环境变量：
export SSLKEYLOGFILE=/tmp/sslkeys.log
firefox https://target.com

# Wireshark：编辑 → 首选项 → 协议 → TLS
# → (预)-主密钥日志文件名：/tmp/sslkeys.log

# 方法2：服务器私钥（仅限RSA密钥交换）
# Wireshark：编辑 → 首选项 → 协议 → TLS → RSA密钥列表
# → 添加：IP、端口、协议、密钥文件(.pem)
```

### DNS — 隧道检测

```bash
# DNS隧道的指示器：
# 1. 异常长的子域名（>30个字符）
# 2. 高量的TXT记录查询/响应
# 3. 持续查询同一域名的模式
# 4. 类Base32/Base64的子域名字符串
# 5. 单个主机的高查询频率

# Wireshark对可疑DNS的过滤器：
dns.qry.name.len > 50                # 长查询名称
dns.qry.type == 16                   # TXT记录（隧道常用）
dns.resp.len > 512                   # 大型DNS响应

# tshark提取：
tshark -r capture.pcap -Y "dns.qry.type==16" -T fields -e dns.qry.name
```

### FTP — 凭证与文件提取

```bash
# FTP凭证（明文）
# 过滤器：ftp.request.command == "USER" || ftp.request.command == "PASS"

# FTP文件传输重建：
# FTP使用单独的数据通道（通常端口20或动态）
# 跟踪数据连接的TCP流以提取文件

# tshark：
tshark -r capture.pcap -Y "ftp.request.command==USER || ftp.request.command==PASS" -T fields -e ftp.request.arg
```

### SMTP — 邮件内容提取

```bash
# 跟踪TCP流 → MAIL FROM/RCPT TO/DATA部分
# 附件：MIME中的base64 → 解码Content-Transfer-Encoding块
# 过滤器：
smtp.req.command == "AUTH"            # 认证（通常base64）
smtp contains "Content-Disposition: attachment"   # 附件
```

### USB — 键盘HID捕获解码

```bash
# USB HID键盘流量：8字节数据的中断传输
# 过滤器：usb.transfer_type == 0x01

# 提取按键：
tshark -r usb.pcap -Y "usb.capdata && usb.data_len == 8" -T fields -e usb.capdata > keystrokes.txt

# HID键盘布局：byte[0]=修饰符，byte[2]=键码
# 0x04=a..0x1d=z，0x1e=1..0x27=0，0x28=Enter，0x2c=空格
# 使用Python/在线HID解码器将键码→文本
```

### WiFi — WPA握手

```bash
# 捕获：airodump-ng --bssid AP_MAC -w capture wlan0mon
# 转换+破解：hcxpcapngtool -o hash.hc22000 capture.pcap
hashcat -m 22000 hash.hc22000 wordlist.txt
# 解密检测：wlan.fc.type_subtype == 0x0c
```

### ICMP — 数据外泄

```bash
# ICMP有效载荷分析
# 正常ping：32或64字节的模式数据
# 外泄：ICMP有效载荷中有意义的数据

# 过滤器：
icmp && data.len > 48                 # 异常ICMP有效载荷大小
icmp.type == 8                        # 回显请求

# 提取ICMP有效载荷：
tshark -r capture.pcap -Y "icmp.type==8" -T fields -e data.data
```

---

## 4. 数据提取

### 文件雕刻

```bash
# Wireshark：文件 → 导出对象
# 支持：HTTP、SMB、TFTP、IMF（电子邮件）、DICOM

# 从重组流手动：
# 跟踪TCP流 → 显示为原始 → 另存为

# binwalk在导出的流数据上
binwalk -e exported_stream.bin
foremost -i exported_stream.bin -o carved/
```

### 凭证收集

```bash
# 明文：ftp || telnet || http.authbasic || smtp || pop || imap
# NTLM：ntlmssp.auth.username → 从NTLMSSP消息中提取挑战/响应
# 哈希格式：user::domain:challenge:NTProofStr:blob → hashcat -m 5600
```

### 隐蔽通道检测

指示器：DNS具有长子域名、ICMP具有大有效载荷、HTTP具有编码头部、定期信标间隔（C2）。使用`tshark -q -z io,stat,1`和`-z conv,tcp`进行统计异常检测。

---

## 5. NETWORKMINER

```bash
# 自动PCAP分析：sudo apt install networkminer
# 打开PCAP → 自动提取：文件、图像、凭证、会话、DNS
# 文件选项卡：从HTTP/SMB/FTP雕刻的文件 | 凭证选项卡：明文凭证
```

---

## 6. TSHARK命令行分析

```bash
tshark -r capture.pcap -Y "http.request" -T fields -e http.host -e http.request.uri
tshark -r capture.pcap -Y "dns.flags.response==0" -T fields -e dns.qry.name | sort -u
tshark -r capture.pcap -Y "http.request.method==POST" -T fields -e http.file_data
tshark -r capture.pcap -q -z io,stat,1                # I/O图
tshark -r capture.pcap -q -z conv,tcp                  # TCP对话
tshark -r capture.pcap -q -z endpoints,ip              # IP端点
tshark -r capture.pcap -q -z io,phs                    # 协议层次
tshark -r capture.pcap -q -z follow,tcp,ascii,0        # 跟踪流0
tshark -r capture.pcap --export-objects http,/tmp/exported/
```

---

## 7. 决策树

```
PCAP文件用于分析
│
├── 文件无法打开？
│   ├── 检查魔数：xxd | head (§1)
│   ├── 修复：pcapfix (§1)
│   └── 转换：editcap pcapng→pcap (§1)
│
├── 捕获中有什么内容？（快速概览）
│   ├── tshark -q -z io,phs (协议层次) (§6)
│   ├── tshark -q -z conv,tcp (对话) (§6)
│   └── tshark -q -z endpoints,ip (端点) (§6)
│
├── HTTP流量？
│   ├── 导出对象：文件 → 导出对象 → HTTP (§4)
│   ├── 凭证搜索：POST + password/login过滤器 (§3)
│   ├── 跟踪流：有趣的请求/响应对 (§3)
│   └── 加密（HTTPS）？→ 需要SSLKEYLOGFILE或RSA密钥 (§3)
│
├── DNS流量？
│   ├── 长子域名？→ DNS隧道 (§3)
│   ├── 高TXT记录量？→ DNS外泄 (§3)
│   ├── 提取所有查询：tshark -Y dns -T fields -e dns.qry.name (§6)
│   └── DNS重绑定？→ 检查交替A记录响应
│
├── FTP / Telnet / SMTP？
│   ├── 提取凭证（明文） (§3)
│   ├── 重建文件传输（跟踪数据流） (§3)
│   └── 邮件内容和附件（base64解码） (§3)
│
├── USB流量？
│   ├── 键盘HID → 解码按键 (§3)
│   ├── 存储 → 提取传输的文件
│   └── 检查transfer_type和数据_len字段
│
├── WiFi流量？
│   ├── WPA握手 → 使用hashcat破解 (§3)
│   ├── 解密帧 → 检测攻击 (§3)
│   └── 探针请求 → 设备指纹识别
│
├── ICMP流量？
│   ├── 大/可变有效载荷 → 数据外泄 (§3)
│   ├── 定期模式 → ICMP隧道 (§3)
│   └── 提取有效载荷：tshark -Y icmp -T fields -e data.data
│
├── 可疑模式？
│   ├── 定期信标间隔 → C2通信 (§4)
│   ├── 异常端口/协议组合 → 隐蔽通道 (§4)
│   ├── 高量到单个外部IP → 数据外泄 (§4)
│   └── 无SNI的加密流量 → 可疑隧道
│
└── 需要自动提取？
    ├── NetworkMiner用于文件/凭证/图像 (§5)
    ├── tshark --export-objects用于HTTP/SMB文件 (§6)
    └── binwalk/foremost在导出流上 (§4)
```
