# 协议逆向工程

用于安全研究、互操作性和调试的网络协议捕获、分析和文档记录的全面技术。

## 流量捕获

### Wireshark捕获

```bash
# 在特定接口上捕获
wireshark -i eth0 -k

# 使用过滤器捕获
wireshark -i eth0 -k -f "port 443"

# 捕获到文件
tshark -i eth0 -w capture.pcap

# 循环缓冲区捕获（轮换文件）
tshark -i eth0 -b filesize:100000 -b files:10 -w capture.pcap
```

### tcpdump捕获

```bash
# 基本捕获
tcpdump -i eth0 -w capture.pcap

# 带过滤器
tcpdump -i eth0 port 8080 -w capture.pcap

# 捕获特定字节
tcpdump -i eth0 -s 0 -w capture.pcap  # 完整数据包

# 实时显示
tcpdump -i eth0 -X port 80
```

### 中间人捕获

```bash
# mitmproxy用于HTTP/HTTPS
mitmproxy --mode transparent -p 8080

# SSL/TLS拦截
mitmproxy --mode transparent --ssl-insecure

# 导出到文件
mitmdump -w traffic.mitm

# Burp Suite
# 将浏览器代理配置为127.0.0.1:8080
```

## 协议分析

### Wireshark分析

```
# 显示过滤器
tcp.port == 8080
http.request.method == "POST"
ip.addr == 192.168.1.1
tcp.flags.syn == 1 && tcp.flags.ack == 0
frame contains "password"

# 跟踪流
右键单击 > 跟踪 > TCP流
右键单击 > 跟踪 > HTTP流

# 导出对象
文件 > 导出对象 > HTTP

# 解密
编辑 > 首选项 > 协议 > TLS
  - (预)-主密钥日志文件名
  - RSA密钥列表
```

### tshark分析

```bash
# 提取特定字段
tshark -r capture.pcap -T fields -e ip.src -e ip.dst -e tcp.port

# 统计信息
tshark -r capture.pcap -q -z conv,tcp
tshark -r capture.pcap -q -z endpoints,ip

# 过滤并提取
tshark -r capture.pcap -Y "http" -T json > http_traffic.json

# 协议层次结构
tshark -r capture.pcap -q -z io,phs
```

### Scapy用于自定义分析

```python
from scapy.all import *

# 读取pcap
packets = rdpcap("capture.pcap")

# 分析数据包
for pkt in packets:
    if pkt.haslayer(TCP):
        print(f"Src: {pkt[IP].src}:{pkt[TCP].sport}")
        print(f"Dst: {pkt[IP].dst}:{pkt[TCP].dport}")
        if pkt.haslayer(Raw):
            print(f"Data: {pkt[Raw].load[:50]}")

# 过滤数据包
http_packets = [p for p in packets if p.haslayer(TCP)
                and (p[TCP].sport == 80 or p[TCP].dport == 80)]

# 创建自定义数据包
pkt = IP(dst="target")/TCP(dport=80)/Raw(load="GET / HTTP/1.1\r\n")
send(pkt)
```

## 协议识别

### 常见协议特征

```
HTTP        - 开头为"HTTP/1."或"GET "或"POST "
TLS/SSL     - 记录层0x16 0x03
DNS         - UDP端口53，特定头部格式
SMB         - "SMB"特征码0xFF 0x53 0x4D 0x42
SSH         - "SSH-2.0"横幅
FTP         - "220 "响应，"USER "命令
SMTP        - "220 "横幅，"EHLO"命令
MySQL       - 0x00长度前缀，协议版本
PostgreSQL  - 0x00 0x00 0x00启动长度
Redis       - "*" RESP数组前缀
MongoDB     - BSON文档带特定头部
```

### 协议头部模式

```
+--------+--------+--------+--------+
|  魔数/特征码         |
+--------+--------+--------+--------+
|  版本       |  标志          |
+--------+--------+--------+--------+
|  长度        |  消息类型   |
+--------+--------+--------+--------+
|  序列号/会话ID     |
+--------+--------+--------+--------+
|  有效载荷...                       |
+--------+--------+--------+--------+
```

## 二进制协议分析

### 结构识别

```python
# 二进制协议中的常见模式

# 长度前缀消息
struct Message {
    uint32_t length;      # 消息总长度
    uint16_t msg_type;    # 消息类型标识符
    uint8_t  flags;       # 标志/选项
    uint8_t  reserved;    # 填充/对齐
    uint8_t  payload[];   # 可变长度有效载荷
};

# 类型-长度-值(TLV)
struct TLV {
    uint8_t  type;        # 字段类型
    uint16_t length;      # 字段长度
    uint8_t  value[];     # 字段数据
};

# 固定头部+可变有效载荷
struct Packet {
    uint8_t  magic[4];    # "ABCD"特征码
    uint32_t version;
    uint32_t payload_len;
    uint32_t checksum;    # CRC32或类似
    uint8_t  payload[];
};
```

### Python协议解析器

```python
import struct
from dataclasses import dataclass

@dataclass
class MessageHeader:
    magic: bytes
    version: int
    msg_type: int
    length: int

    @classmethod
    def from_bytes(cls, data: bytes):
        magic, version, msg_type, length = struct.unpack(
            ">4sHHI", data[:12]
        )
        return cls(magic, version, msg_type, length)

def parse_messages(data: bytes):
    offset = 0
    messages = []

    while offset < len(data):
        header = MessageHeader.from_bytes(data[offset:])
        payload = data[offset+12:offset+12+header.length]
        messages.append((header, payload))
        offset += 12 + header.length

    return messages

# 解析TLV结构
def parse_tlv(data: bytes):
    fields = []
    offset = 0

    while offset < len(data):
        field_type = data[offset]
        length = struct.unpack(">H", data[offset+1:offset+3])[0]
        value = data[offset+3:offset+3+length]
        fields.append((field_type, value))
        offset += 3 + length

    return fields
```

### 十六进制转储分析

```python
def hexdump(data: bytes, width: int = 16):
    """格式化二进制数据为十六进制转储."""
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(
            chr(b) if 32 <= b < 127 else '.'
            for b in chunk
        )
        lines.append(f'{i:08x}  {hex_part:<{width*3}}  {ascii_part}')
    return '\n'.join(lines)

# 示例输出:
# 00000000  48 54 54 50 2f 31 2e 31  20 32 30 30 20 4f 4b 0d  HTTP/1.1 200 OK.
# 00000010  0a 43 6f 6e 74 65 6e 74  2d 54 79 70 65 3a 20 74  .Content-Type: t
```

## 加密分析

### 识别加密

```python
# 熵分析 - 高熵表明加密/压缩
import math
from collections import Counter

def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counter = Counter(data)
    probs = [count / len(data) for count in counter.values()]
    return -sum(p * math.log2(p) for p in probs)

# 熵阈值:
# < 6.0: 可能是明文或结构化数据
# 6.0-7.5: 可能是压缩
# > 7.5: 可能是加密或随机

# 常见加密指示器
# - 高且均匀的熵
# - 无明显结构或模式
# - 长度通常是块大小的倍数(16为AES)
# - 可能的IV在开头(16字节为AES-CBC)
```

### TLS分析

```bash
# 提取TLS元数据
tshark -r capture.pcap -Y "ssl.handshake" \
    -T fields -e ip.src -e ssl.handshake.ciphersuite

# JA3指纹(客户端)
tshark -r capture.pcap -Y "ssl.handshake.type == 1" \
    -T fields -e ssl.handshake.ja3

# JA3S指纹(服务器)
tshark -r capture.pcap -Y "ssl.handshake.type == 2" \
    -T fields -e ssl.handshake.ja3s

# 证书提取
tshark -r capture.pcap -Y "ssl.handshake.certificate" \
    -T fields -e x509sat.printableString
```

### 解密方法

```bash
# 主密钥日志(浏览器)
export SSLKEYLOGFILE=/tmp/keys.log

# 配置Wireshark
# 编辑 > 首选项 > 协议 > TLS
# (预)-主密钥日志文件名: /tmp/keys.log

# 使用私钥解密(如果可用)
# 仅适用于RSA密钥交换
# 编辑 > 首选项 > 协议 > TLS > RSA密钥列表
```

## 自定义协议文档

### 协议规范模板

```markdown
# 协议名称规范

## 概述

协议目的和设计的简要描述。

## 传输

- 层级: TCP/UDP
- 端口: XXXX
- 加密: TLS 1.2+

## 消息格式

### 头部(12字节)

| 偏移 | 大小 | 字段   | 描述             |
|------|------|--------|------------------|
| 0    | 4    | Magic  | 0x50524F54("PROT") |
| 4    | 2    | Version | 协议版本(1)      |
| 6    | 2    | Type   | 消息类型标识符   |
| 8    | 4    | Length | 有效载荷长度(字节) |

### 消息类型

| 类型 | 名称     | 描述             |
|------|---------|------------------|
| 0x01 | HELLO   | 连接初始化      |
| 0x02 | HELLO_ACK | 连接接受        |
| 0x03 | DATA    | 应用数据        |
| 0x04 | CLOSE   | 连接终止        |

### 类型0x01: HELLO

| 偏移 | 大小 | 字段      | 描述              |
|------|------|----------|-------------------|
| 0    | 4    | ClientID | 唯一客户端标识符 |
| 4    | 2    | Flags    | 连接标志         |
| 6    | var  | Extensions | TLV编码的扩展     |

## 状态机
```

[INIT] --HELLO--> [WAIT_ACK] --HELLO_ACK--> [CONNECTED]
|
DATA/DATA
|
[CLOSED] <--CLOSE--+

```

## 示例
### 连接建立
```

Client -> Server: HELLO (ClientID=0x12345678)
Server -> Client: HELLO_ACK (Status=OK)
Client -> Server: DATA (payload)

```

```

### Wireshark解密器(Lua)

```lua
-- custom_protocol.lua
local proto = Proto("custom", "自定义协议")

-- 定义字段
local f_magic = ProtoField.string("custom.magic", "魔数")
local f_version = ProtoField.uint16("custom.version", "版本")
local f_type = ProtoField.uint16("custom.type", "类型")
local f_length = ProtoField.uint32("custom.length", "长度")
local f_payload = ProtoField.bytes("custom.payload", "有效载荷")

proto.fields = { f_magic, f_version, f_type, f_length, f_payload }

-- 消息类型名称
local msg_types = {
    [0x01] = "HELLO",
    [0x02] = "HELLO_ACK",
    [0x03] = "DATA",
    [0x04] = "CLOSE"
}

function proto.dissector(buffer, pinfo, tree)
    pinfo.cols.protocol = "CUSTOM"

    local subtree = tree:add(proto, buffer())

    -- 解析头部
    subtree:add(f_magic, buffer(0, 4))
    subtree:add(f_version, buffer(4, 2))

    local msg_type = buffer(6, 2):uint()
    subtree:add(f_type, buffer(6, 2)):append_text(
        " (" .. (msg_types[msg_type] or "未知") .. ")"
    )

    local length = buffer(8, 4):uint()
    subtree:add(f_length, buffer(8, 4))

    if length > 0 then
        subtree:add(f_payload, buffer(12, length))
    end
end

-- 注册TCP端口
local tcp_table = DissectorTable.get("tcp.port")
tcp_table:add(8888, proto)
```

## 活动测试

### Boofuzz模糊测试

```python
from boofuzz import *

def main():
    session = Session(
        target=Target(
            connection=TCPSocketConnection("target", 8888)
        )
    )

    # 定义协议结构
    s_initialize("HELLO")
    s_static(b"\x50\x52\x4f\x54")  # 魔数
    s_word(1, name="version")       # 版本
    s_word(0x01, name="type")       # 类型(HELLO)
    s_size("payload", length=4)     # 长度字段
    s_block_start("payload")
    s_dword(0x12345678, name="client_id")
    s_word(0, name="flags")
    s_block_end()

    session.connect(s_get("HELLO"))
    session.fuzz()

if __name__ == "__main__":
    main()
```

### 重放和修改

```python
from scapy.all import *

# 重放捕获的流量
packets = rdpcap("capture.pcap")
for pkt in packets:
    if pkt.haslayer(TCP) and pkt[TCP].dport == 8888:
        send(pkt)

# 修改并重放
for pkt in packets:
    if pkt.haslayer(Raw):
        # 修改有效载荷
        original = pkt[Raw].load
        modified = original.replace(b"client", b"CLIENT")
        pkt[Raw].load = modified
        # 重新计算校验和
        del pkt[IP].chksum
        del pkt[TCP].chksum
        send(pkt)
```

## 最佳实践

### 分析工作流程

1. **捕获流量**：多个会话，不同场景
2. **识别边界**：消息开始/结束标记
3. **映射结构**：固定头部，可变有效载荷
4. **识别字段**：比较多个样本
5. **文档格式**：创建规范
6. **验证理解**：实现解析器/生成器
7. **测试边界情况**：模糊测试，边界条件

### 常见模式

- 消息开头处的魔数/特征码
- 版本字段用于兼容性
- 长度字段(通常在可变数据前)
- 类型/操作字段用于消息识别
- 序列号用于排序
- 校验和/CRC用于完整性
- 时间戳用于计时
- 会话/连接标识符
