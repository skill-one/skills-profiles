---
name: ctf-forensics
description: 提供数字取证和信号分析技术，用于CTF挑战。在分析磁盘映像、内存转储、事件日志、网络捕获、加密货币交易、隐写术、PDF分析、Windows注册表、Volatility、PCAP、Docker映像、核心转储、侧信道功率轨迹、DTMF音频频谱图、数据包时间分析、CD音频光盘映像，或恢复已删除文件和凭据时使用。
---

# CTF 取证与区块链

数字取证 CTF 挑战的快速参考。此处每项技术仅用一句话概括；详细说明请见对应的支持文件。

## 先决条件

**Python 包（所有平台）：**
```bash
pip install volatility3 Pillow numpy matplotlib
```

**Linux（apt）：**
```bash
apt install binwalk foremost libimage-exiftool-perl tshark sleuthkit \
  ffmpeg steghide testdisk john pcapfix
```

**macOS（Homebrew）：**
```bash
brew install binwalk exiftool wireshark sleuthkit ffmpeg \
  testdisk john-jumbo
```

**Ruby gems（所有平台）：**
```bash
gem install zsteg
```

## 附加资源

- [3d-printing.md](3d-printing.md) - 3D 打印取证（PrusaSlicer 二进制 G-code、QOIF、heatshrink）
- [windows.md](windows.md) - Windows 取证（注册表、SAM、事件日志、回收站、NTFS 替代数据流、USN 日志、PowerShell 历史记录、Defender MPLog、WMI 持久化、Amcache）
- [network.md](network.md) - 网络取证基础（tcpdump、TLS/SSL keylog 解密、从 coredump 中提取 TLS 主密钥、Wireshark、PCAP、端口扫描、SMB3 解密、5G/NR 协议、WordPress 侦察、凭据、USB HID 电报、BCD 编码、HTTP 文件上传外泄、通过时间戳排序重组分割归档）
- [network-advanced.md](network-advanced.md) - 高级网络取证（数据包间隔时序编码、NTLMv2 哈希破解、TCP 标志隐蔽信道、DNS 末字节隐写术、DNS 尾随字节二进制编码、带 XOR + ZIP 和 mDNS 密钥的多层 PCAP、Brotli 解压缩炸弹接缝分析、通过 LSARPC 进行 SMB RID 回收、Timeroasting MS-SNTP 哈希提取、dnscat2 重组、RADIUS 共享密钥破解、RC4 流识别、ICMP 有效载荷字节轮换、ICMP ping 时延隐蔽信道）
- [peripheral-capture.md](peripheral-capture.md) - USB/HID/蓝牙外设流量重构（USB HID 鼠标/触控笔绘图恢复、USB HID 键盘捕获解码、USB 键盘 LED 摩尔斯电码外泄、USB HID 键盘方向键导航跟踪、蓝牙 RFCOMM 数据包重组）
- [disk-and-memory.md](disk-and-memory.md) - 核心磁盘/内存取证（Volatility、磁盘挂载/雕刻、VM/OVA/VMDK、VMware 快照、GIMP 原始内存转储目视检查、coredump、Windows KAPE 分诊、PowerShell 勒索软件、Android 取证、Docker 容器取证、云存储取证、BSON 重构、TrueCrypt/VeraCrypt 挂载）
- [disk-advanced.md](disk-advanced.md) - 高级磁盘与内存技术（已删除分区、ZFS 取证、GPT GUID 编码、VMDK 稀疏解析、内存转储字符串雕刻、勒索软件密钥恢复、WordPerfect 宏 XOR、minidump ISO 9660 恢复、APFS 快照恢复、RAID 5 XOR 恢复、HFS+ 资源叉恢复、Kyoto Cabinet 哈希 DB 取证、SQLite 编辑历史重构）
- [disk-recovery.md](disk-recovery.md) - 磁盘恢复与提取模式（LUKS 主密钥恢复、PRNG 时间戳种子暴力破解、VBA 宏二进制恢复、FemtoZip 解压缩、XFS 文件系统重构、tar 重复条目提取、嵌套 matryoshka 文件系统提取、通过空字节交错进行反雕刻、BTRFS 子卷/快照恢复、FAT16 空闲空间数据恢复、通过 Sleuth Kit fls/icat 恢复 FAT16 已删除文件、通过 fsck 恢复 ext2 孤立 inode、损坏的 ZIP 头修复）
- [steganography.md](steganography.md) - 通用隐写术（二进制边框隐写、PDF 多层隐写、SVG 关键帧、PNG 重排、文件叠加、GIF 帧差摩尔斯电码、GZSteg + spammimic、电子表格频率恢复、Kitty 终端图形协议解码、ANSI 转义序列隐写、自动立体图求解、两层字节+行交错、多流视频容器隐写、渐进式 PNG 分层 XOR 解密、从弯曲反射重建二维码）
- [stego-image.md](stego-image.md) - 图像特定隐写术（JPEG 未使用的 DQT 表 LSB、BMP 位平面二维码提取、图像拼图重组、F5 JPEG DCT 比率检测、PNG 未使用调色板条目隐写、二维码瓦片重构、基于种子的像素置换 + 多位平面二维码、JPEG 缩略图像素到文本映射、带像素过滤的条件 LSB、JPEG 松弛空间、最近邻插值隐写、RGB 奇偶隐写）
- [stego-advanced.md](stego-advanced.md) - 高级隐写术第 1 部分：音频与信号技术（FFT 频域、DTMF 音频、SSTV+LSB、DotCode 条形码、自定义频率双音键盘、多轨音频差分减法、跨信道多位 LSB、音频 FFT 音符、音频元数据八进制编码、嵌套 tar 空白编码、带密码破解的 DeepSound 音频隐写、音频波形二进制编码、音频频谱图隐藏二维码）
- [stego-advanced-2.md](stego-advanced-2.md) - 高级隐写术第 2 部分：视频、图像变换及特定格式技术（视频帧累加、反转音频、视频帧平均、JPEG XL TOC 置换隐写、Arnold 猫图解扰、高分辨率 SSTV 自定义 FM 解调、MJPEG FFD9 尾随字节隐写、EXIF zlib + Stegano 像素模式、PDF xref 隐蔽信道、ANSI 转义码隐写、逐像素 ECB 去重）
- [linux-forensics.md](linux-forensics.md) - Linux/应用取证（日志分析、Docker 镜像取证、攻击链、浏览器凭据、Firefox 历史记录、TFTP、TLS 弱 RSA、USB 音频、Git 目录恢复、KeePass v4 破解、Git reflog/fsck squash 恢复、浏览器痕迹分析（Chrome/Chromium/Firefox 历史记录、Cookie、下载、本地存储、会话恢复）、通过字节暴力修复损坏的 git blob、VBA 宏 Excel 单元格数据提取为 ELF 二进制、通过 pyrasite 恢复 Python 内存中的源代码）
- [signals-and-hardware.md](signals-and-hardware.md) - 带解码代码的硬件信号解码（VGA 帧解析、HDMI TMDS 符号解码、DisplayPort 8b/10b + LFSR 解扰器）、旅行者金唱片音频、Saleae Logic 2 UART 解码、Flipper Zero .sub 文件、侧信道功率分析（DPA）、键盘声学侧信道、CD 音频光盘镜像隐写（CIRC 解交错 + 螺旋渲染）、视频中 caps-lock LED 摩尔斯电码、Linux input_event 键盘记录器转储解析、WAV 音频中的串行 UART、USB MIDI Launchpad 网格重构

---

## 何时转换方向

- 如果你恢复了加密数据块，且难点在于 RSA、AES 或格运算，请切换到 `/ctf-crypto`。
- 如果证据确实指向恶意软件准备、信标配置提取或打包样本，请切换到 `/ctf-malware`。
- 如果工件是 Web 应用备份或 API 转储，且剩余问题是应用逻辑，请切换到 `/ctf-web`。
- 如果取证证据实际上是编码谜题、隐写术技巧或深奥格式，而非真正的取证，请切换到 `/ctf-misc`。
- 如果你需要追踪基础设施、归因行动者或根据取证结果调查公开记录，请切换到 `/ctf-osint`。
- 如果恢复的工件是需要反汇编和分析的编译二进制文件或固件，请切换到 `/ctf-reverse`。

## 快速开始命令

```bash
# 文件分析
file suspicious_file
exiftool suspicious_file     # 元数据
binwalk suspicious_file      # 嵌入文件
strings -n 8 suspicious_file
hexdump -C suspicious_file | head  # 检查魔术字节

# 磁盘取证
sudo mount -o loop,ro image.dd /mnt/evidence
fls -r image.dd              # 列出文件
photorec image.dd            # 雕刻已删除的文件

# 内存取证（Volatility 3）
vol -f memory.dmp windows.info
vol -f memory.dmp windows.pslist
vol -f memory.dmp windows.filescan
```

查看 [disk-and-memory.md](disk-and-memory.md) 了解完整的 Volatility 插件参考、VM 取证和 coredump 分析。

## 日志分析

```bash
grep -iE "(flag|part|piece|fragment)" server.log     # 标志碎片
grep "FLAGPART" server.log | sed 's/.*FLAGPART: //' | uniq | tr -d '\n'  # 重构
sort logfile.log | uniq -c | sort -rn | head         # 查找异常
```

查看 [linux-forensics.md](linux-forensics.md) 了解 Linux 攻击链分析和 Docker 镜像取证。

## Windows 事件日志 (.evtx)

**关键事件 ID：**
- 1001 - Bugcheck/重启
- 1102 - 审计日志已清除
- 4720 - 用户账户创建
- 4781 - 账户重命名

**RDP 会话 ID（TerminalServices-LocalSessionManager）：**
- 21 - 会话登录成功
- 24 - 会话断开
- 1149 - RDP 身份验证成功（RemoteConnectionManager，包含源 IP）

```python
import Evtx.Evtx as evtx
with evtx.Evtx("Security.evtx") as log:
    for record in log.records():
        print(record.xml())
```

查看 [windows.md](windows.md) 了解完整的事件 ID 表、注册表分析、SAM 解析、USN 日志和反取证检测。

- **NTFS 替代数据流（ADS）：** 通过命名 NTFS 流附加到文件的隐藏数据。对 `dir`/资源管理器不可见。使用 `fls -r image.dd | grep ":"` 检测，使用 `icat` 提取。参见 [windows.md](windows.md#ntfs-alternate-data-streams)。

## 当日志被清除时

如果攻击者清除了事件日志，请使用这些替代来源：
1. **USN 日志（$J）** - 文件操作时间线（MFT 引用、时间戳、原因）
2. **SAM 注册表** - 根据键 last_modified 时间戳的账户创建
3. **PowerShell 历史记录** - ConsoleHost_history.txt（USN DATA_EXTEND = 命令计时）
4. **Defender MPLog** - 包含威胁检测和 ASR 事件的独立日志
5. **Prefetch** - 程序执行证据
6. **用户配置文件创建** - 首次登录时间（配置文件目录在 USN 日志中）

查看 [windows.md](windows.md) 了解详细的解析代码和反取证检测清单。

## 隐写术

```bash
steghide extract -sf image.jpg -p ""
zsteg image.png              # PNG/BMP 分析
stegsolve                    # 目视分析
```

- **二进制边框隐写：** 1px 图像边框中的黑白像素按顺时针方向编码位
- **FFT 频域：** 图像数据隐藏在 2D FFT 幅度谱中；尝试使用 `np.fft.fft2` 可视化
- **DTMF 音频：** 电话音编码数据；使用 `multimon-ng -a DTMF` 解码
- **多层 PDF：** 检查隐藏注释、EOF 后数据、与关键词进行 XOR、最终层 ROT18
- **SSTV + LSB：** SSTV 信号可能是红鲱鱼；使用 `stegolsb` 检查音频样本的 2 位 LSB
- **SVG 关键帧：** 动画 `keyTimes`/`values` 属性通过填充颜色交替编码二进制/摩尔斯
- **PNG 块重排：** 修复块顺序：IHDR → 辅助 → IDAT（按顺序） → IEND
- **文件叠加：** 检查 IEND 之后的追加归档，其魔术字节被覆盖
- **APNG 帧提取：** 动画 PNG 有多个帧；使用 `apngdis` 提取或解析 `fdAT`/`fcTL` 块。参见 [steganography.md](steganography.md#apng-animated-png-frame-extraction-icectf-2016)。
- **PNG 高度/CRC 操纵：** 修改 IHDR 高度字段，暴力搜索直至 CRC 匹配以揭示隐藏行。参见 [steganography.md](steganography.md#png-heightcrc-manipulation-for-hidden-content-h4ckit-ctf-2016)。
- **像素坐标链隐写：** 链表遍历，其中 R=数据字节，G/B=下一像素坐标。参见 [stego-image.md](stego-image.md#pixel-coordinate-chain-steganography-h4ckit-ctf-2016)。
- **AVI 帧差分：** 对连续视频帧进行 XOR，揭示像素差异中的隐藏数据。参见 [stego-image.md](stego-image.md#avi-frame-differential-pixel-steganography-h4ckit-ctf-2016)。

- **自定义频率 DTMF：** 非标准双音频率；首先生成频谱图（`ffmpeg -i audio -lavfi showspectrumpic`），将自定义网格映射到键盘数字，解码可变长度 ASCII
- **JPEG DQT LSB：** 未使用的量化表（ID 2、3）承载 LSB 编码的数据；通过 `Image.open().quantization` 访问，并从每个 64 个值中提取位 0
- **多轨音频减法：** MKV/视频中有两个几乎相同的音轨；`sox -m a0.wav "|sox a1.wav -p vol -1" diff.wav` 取消共享内容，标志出现在差分信号的频谱图中（5-12 kHz 频段）
- **数据包间隔时序：** 具有两个不同间隔值（例如，10ms/100ms）的相同数据包编码二进制；按接口过滤，计算包间增量，阈值化为位

查看 [steganography.md](steganography.md)、[stego-advanced.md](stego-advanced.md) 和 [stego-advanced-2.md](stego-advanced-2.md) 了解完整的代码示例和解码工作流。

## PDF 分析

```bash
exiftool document.pdf        # 元数据（通常隐藏标志！）
pdftotext document.pdf -     # 提取文本
strings document.pdf | grep -i flag
binwalk document.pdf         # 嵌入文件
```

**高级 PDF 隐写（Nullcon 2026 rdctd）：** 六种技术 -- 不可见文本分隔符、带转义花括号的 URI 注释、模糊图像上的 Wiener 反卷积、矢量矩形二维码、压缩对象流（`mutool clean -d`）、文档元数据字段。

查看 [steganography.md](steganography.md) 了解完整的 PDF 隐写技术和代码。

## 磁盘 / VM / 内存取证

```bash
# 磁盘镜像
sudo mount -o loop,ro image.dd /mnt/evidence
fls -r image.dd && photorec image.dd

# VM 镜像（OVA/VMDK）
tar -xvf machine.ova
7z x disk.vmdk -oextracted "Windows/System32/config/SAM" -r

# 内存（Volatility 3）
vol -f memory.dmp windows.pslist
vol -f memory.dmp windows.cmdline
vol -f memory.dmp windows.netscan
vol -f memory.dmp windows.dumpfiles --physaddr <addr>

# 字符串雕刻
strings -a -n 6 memdump.bin | grep -E "FLAG|SSH_CLIENT|SESSION_KEY"

# Coredump
gdb -c core.dump  # info registers, x/100x $rsp, 查找 "flag"
```

查看 [disk-and-memory.md](disk-and-memory.md) 了解完整的 Volatility 插件参考、VM 取证和 VMware 快照。查看 [disk-advanced.md](disk-advanced.md) 了解已删除分区恢复、ZFS 取证和勒索软件分析。

## Windows 密码哈希

```bash
# 使用 impacket 提取，使用 hashcat -m 1000 破解
python -c "from impacket.examples.secretsdump import *; SAMHashes('SAM', LocalOperations('SYSTEM').getBootKey()).dump()"
```

查看 [windows.md](windows.md) 了解 SAM 详细信息，以及 [network-advanced.md](network-advanced.md) 了解从 PCAP 中破解 NTLMv2。

## 比特币追踪

- 使用 mempool.space API：`https://mempool.space/api/tx/<TXID>`
- **剥皮链：** 始终跟随较大的输出；四舍五入的金额表示剥皮

## 不常见的文件魔术字节

| 魔术字节 | 格式 | 扩展名 | 备注 |
|-------|--------|-----------|-------|
| `OggS` | Ogg 容器 | `.ogg` | 音频/视频 |
| `RIFF` | RIFF 容器 | `.wav`,`.avi` | 检查子格式 |
| `%PDF` | PDF | `.pdf` | 检查元数据和嵌入对象 |
| `GCDE` | PrusaSlicer 二进制 G-code | `.g`, `.bgcode` | 参见 3d-printing.md |

## 常见标志位置

- PDF 元数据字段（作者、标题、关键字）
- 图像 EXIF 数据
- 已删除文件（回收站 `$R` 文件）
- 注册表值
- 浏览器历史记录
- 日志文件碎片
- 内存字符串

## WMI 持久化分析

**模式（Backchimney）：** 恶意软件使用 WMI 事件订阅进行持久化（MITRE T1546.003）。

```bash
python PyWMIPersistenceFinder.py OBJECTS.DATA
```

- 查找 FilterToConsumerBindings 以及 CommandLineEventConsumer
- 消费者命令中 Base64 编码的 PowerShell
- 由系统事件（登录、定时器）触发的事件过滤器

查看 [windows.md](windows.md) 了解 WMI 存储库分析详情。

## 网络取证快速参考

- **TFTP netascii:** 二进制传输损坏；使用 `data.replace(b'\r\n', b'\n').replace(b'\r\x00', b'\r')` 修复
- **TLS密钥日志解密:** 将SSLKEYLOGFILE或RSA私钥导入Wireshark (编辑 → 首选项 → 协议 → TLS)
- **TLS弱RSA:** 提取证书，分解模数，使用 `rsatool` 生成私钥，添加到Wireshark
- **USB音频:** 使用 `tshark -e usb.iso.data` 提取同步数据，在Audacity中导入为原始PCM
- **NTLMv2从PCAP:** 从NTLMSSP_AUTH中提取服务器挑战 + NTProofStr + 数据块，进行暴力破解
- **WPA/WEP WiFi解密:** `aircrack-ng -w wordlist capture.pcap` 破解WPA握手；WEP使用足够的IVs即可破解。参见 [network.md](network.md#wpawep-wifi-decryption-from-pcap-defcamp-ctf-2016)。
- **PCAP修复:** `pcapfix -d corrupted.pcap` 修复损坏的PCAP头部/校验和，以便Wireshark加载。参见 [network.md](network.md#corrupted-pcap-repair-with-pcapfix-csaw-ctf-2016)。
- **USB HID键盘解码:** 从USB捕获中提取8字节的HID报告；字节2 = 键码，字节0 = 修饰符 (Shift)。参见 [peripheral-capture.md](peripheral-capture.md#usb-hid-keyboard-capture-decoding-ekoparty-ctf-2016)。
- **dnscat2重组:** 解码十六进制/基32子域名标签，去除9字节的dnscat2头部，去重重传，重组载荷。参见 [network-advanced.md](network-advanced.md#dnscat2-traffic-reassembly-from-dns-pcap-bsidessf-2017)。
- **USB键盘LED窃取:** 主机到设备的HID SET_REPORT数据包切换Caps Lock LED。时间编码摩斯电码。参见 [peripheral-capture.md](peripheral-capture.md#usb-keyboard-led-morse-code-exfiltration-bitsctf-2017)。

参见 [network.md](network.md) 了解SMB3解密、凭证提取，以及 [linux-forensics.md](linux-forensics.md) 了解完整的TLS/TFTP/USB工作流程。

## 浏览器取证

- **Chrome/Edge:** 使用DPAPI主密钥，通过AES-GCM解密 `Login Data` SQLite
- **Firefox:** 查询 `places.sqlite` -- `SELECT url FROM moz_places WHERE url LIKE '%flag%'`

参见 [linux-forensics.md](linux-forensics.md) 了解完整的浏览器凭证解密代码。

## 其他技术快速参考

- **Docker镜像取证：** 配置JSON在清理后仍然保留所有`RUN`命令。使用`tar xf app.tar`然后检查配置数据块。参见[linux-forensics.md](linux-forensics.md)。
- **Linux攻击链：** 检查`auth.log`、`.bash_history`、最近的可执行文件、PCAP。参见[linux-forensics.md](linux-forensics.md)。
- **RAID 5 XOR恢复：** 3盘RAID 5中的两盘 → 逐字节XOR以恢复第三盘：`bytes(a ^ b for a, b in zip(disk1, disk3))`。参见[disk-advanced.md](disk-advanced.md#raid-5-disk-recovery-via-xor-crypto-cat)。
- **GIMP原始内存转储可视化检查：** 当Volatility失败时，以原始RGB数据在显示器宽度(~1920)下打开`.dmp`文件；滚动查找用户桌面的帧缓冲区截图。参见[disk-and-memory.md](disk-and-memory.md#gimp-raw-memory-dump-visual-inspection-inshack-2018)。
- **Kyoto Cabinet哈希数据库取证：** 通过插入顺序探测键并二进制差异来恢复KC哈希数据库中的键顺序，找到每个哈希槽被哪个键覆盖。参见[disk-advanced.md](disk-advanced.md#kyoto-cabinet-hash-database-forensics-via-incremental-key-insertion-asis-ctf-2018)。
- **PowerShell勒索软件：** 从minidump中提取脚本，找到AES密钥，解密SMTP附件。参见[disk-and-memory.md](disk-and-memory.md)。
- **Linux勒索软件+内存转储：** 如果Volatility不可靠，通过原始内存候选扫描和魔法字节验证恢复AES密钥；重新干净地提取zip以避免遗漏文件/假阴性。参见[disk-advanced.md](disk-advanced.md)。
- **已删除分区：** `testdisk`或`kpartx -av`。参见[disk-advanced.md](disk-advanced.md)。
- **ZFS取证：** 重建标签、Fletcher4校验和、PBKDF2破解。参见[disk-advanced.md](disk-advanced.md)。
- **BSON重建：** 从原始字节重新组装BSON（二进制JSON）文档；使用`bson` Python库解析。参见[disk-and-memory.md](disk-and-memory.md#bson-binary-json-format-reconstruction-icectf-2016)。
- **TrueCrypt挂载：** 使用已知密码挂载TrueCrypt/VeraCrypt卷，使用`veracrypt --mount`或`cryptsetup open --type tcrypt`。参见[disk-and-memory.md](disk-and-memory.md#truecrypt--veracrypt-volume-mounting-grehack-ctf-2016)。
- **硬件信号：** VGA/HDMI TMDS/DisplayPort、Voyager音频、Saleae UART解码、Flipper Zero。参见[signals-and-hardware.md](signals-and-hardware.md)。
- **Caps-lock LED摩斯电码从视频：** 使用OpenCV跟踪安全摄像头帧中的caps-lock LED像素；开/关持续时间编码摩斯电码（短=点，长=划）。参见[signals-and-hardware.md](signals-and-hardware.md#caps-lock-led-morse-code-extraction-from-video-stem-ctf-2018)。
- **I2C协议解码：** 解码I2C总线捕获（SDA/SCL线）以从EEPROM或传感器通信中提取数据。参见[signals-and-hardware.md](signals-and-hardware.md#i2c-bus-protocol-decoding-ekoparty-ctf-2016)。
- **穿孔卡片OCR：** 通过将孔位置映射到字符使用标准编码网格来解码IBM-29穿孔卡片图像。参见[signals-and-hardware.md](signals-and-hardware.md#ibm-29-punched-card-ocr-ekoparty-ctf-2016)。
- **USB HID鼠标绘制：** 按绘制模式渲染相对HID移动为位图；分离模式，跳过笔抬起，缩放5-8倍。参见[peripheral-capture.md](peripheral-capture.md#usb-hid-mousepen-drawing-recovery-ehax-2026)。
- **侧信道功率分析：** 多维功率轨迹（位置×猜测×轨迹×样本）。平均轨迹，找到最大方差的样本，选择在泄漏点具有最大功率的猜测。参见[signals-and-hardware.md](signals-and-hardware.md)。
- **数据包间隔计时：** 二进制数据编码为PCAP中的数据包间延迟。两个间隔值=两个位值。参见[网络-高级.md](网络-高级.md)。
- **BMP位平面QR：** 每个RGB通道提取0-2个位平面，使用NumPy；隐藏的QR通常在位1（不是位0）。参见[stego-image.md](stego-image.md#bmp-bitplane-qr-code-extraction--steghide-bypass-ctf-2025)。
- **图像拼图重组：** 边缘匹配像素差异，贪婪放置在网格中。参见[stego-image.md](stego-image.md#image-jigsaw-puzzle-reassembly-via-edge-matching-bypass-ctf-2025)。
- **DeepSound音频隐写与密码破解：** 使用`deepsound2john.py`提取哈希，使用John破解，从WAV检索隐藏文件；始终检查频谱图和DeepSound。参见[stego-高级.md](stego-高级.md#deepsound-audio-steganography-with-password-cracking-inshack-2018)。
- **从弯曲反射重建QR码：** 手动从视频中玻璃球反射重建QR码；翻转、去畸变、使用已知明文前缀修复早期字节，高ECC纠正其余部分。参见[隐写术.md](隐写术.md#qr-code-reconstruction-from-curved-glass-reflection-in-video-plaidctf-2018)。
- **音频FFT音符：** 主导频率→音符名称（A-G）拼写单词。参见[stego-高级.md](stego-高级.md)。
- **音频元数据八进制：** Exiftool注释使用下划线分隔的八进制数字→解码为ASCII/base64。参见[stego-高级.md](stego-高级.md)。
- **G-code可视化：** 侧投影（XZ/YZ）显示文本。参见[3d打印.md](3d打印.md)。
- **Git目录恢复：** `gitdumper.sh`用于暴露的`.git`目录。参见[linux-forensics.md](linux-forensics.md)。
- **KeePass v4破解：** 标准`keepass2john`缺乏v4/Argon2支持；使用`ivanmrsulja/keepass2john`分支或`keepass4brute`。使用`cewl`生成单词列表。参见[linux-forensics.md](linux-forensics.md)。
- **跨通道多比特LSB：** 每个RGB通道的不同位位置（R[0]、G[1]、B[2]）编码隐藏数据。参见[stego-高级.md](stego-高级.md)。
- **F5 JPEG DCT检测：** ±1与±2 AC系数的比率从~3:1降至~1:1，F5；稀疏图像需要±2/±3的次要指标。参见[stego-image.md](stego-image.md#f5-jpeg-dct-coefficient-ratio-detection-apoorvctf-2026)。
- **PNG未使用调色板隐写：** 未使用的PLTE条目（未由像素引用）在红色通道值中携带隐藏数据。参见[stego-image.md](stego-image.md#png-unused-palette-entry-steganography-apoorvctf-2026)。
- **键盘声学侧信道：** 键盘敲击音频的MFCC特征+对标记参考的KNN分类。10ms窗口捕获冲击瞬态。参见[signals-and-hardware.md](signals-and-hardware.md)。
- **TCP标志隐蔽信道：** 6个TCP标志位（FIN/SYN/RST/PSH/ACK/URG）=值0-63，编码base64字符。在一致目的端口上的无意义标志组合=隐蔽数据。参见[网络-高级.md](网络-高级.md)。
- **Brotli解压缩炸弹接缝：** 压缩炸弹有重复块；标志在接缝处打破模式。比较相邻块以找到不连续性，仅解压缩该区域。参见[网络-高级.md](网络-高级.md)。
- **Git reflog/fsck挤压恢复：** `git rebase --squash`留下孤儿对象可通过`git fsck --unreachable --no-reflogs`恢复。参见[linux-forensics.md](linux-forensics.md)。
- **DNS尾部字节二进制：** DNS查询结构后附加的额外字节（`0x30`/`0x31`）编码二进制位；8位MSB优先的块→ASCII。参见[网络-高级.md](网络-高级.md)。
- **假TLS+mDNS密钥+可打印性合并：** 伪装成TLS的TCP流隐藏ZIP；从mDNS TXT记录获取XOR密钥；通过选择可打印字符合并两个解密数组。参见[网络-高级.md](网络-高级.md)。
- **基于种子的像素置换隐写：** 确定性像素洗牌（使用已知种子的Fisher-Yates）+从Y通道提取多比特平面交错LSB→隐藏QR码。参见[stego-image.md](stego-image.md#seed-based-pixel-permutation--multi-bitplane-qr-l3m0nctf-2025)。
- **BTRFS快照恢复：** 删除的文件在BTRFS快照/备用子卷中持续存在。`mount -o subvol=@backup`访问历史副本。参见[磁盘恢复.md](磁盘恢复.md#btrfs-subvolumesnapshot-recovery-bsidessf-2026)。
- **JPEG XL TOC置换：** JXL的渐进式TOC置换控制部分解码期间瓦片收敛顺序。在增加的偏移量处截断，测量哪些瓦片首先收敛→收敛顺序编码标志。参见[stego-高级-2.md](stego-高级-2.md#jpeg-xl-toc-permutation-steganography-bsidessf-2026)。
- **Kitty终端图形：** `ESC_G`协议在base64块中嵌入zlib压缩的RGB图像数据。剥离转义序列，连接，解压缩，重建。参见[隐写术.md](隐写术.md#kitty-terminal-graphics-protocol-decoding-bsidessf-2026)。
- **ANSI转义序列隐写：** 标志文本交错在ANSI颜色代码和盲文字符之间。渲染时不可见；通过剥离转义序列和非ASCII提取。参见[隐写术.md](隐写术.md#ansi-escape-sequence-steganography-in-terminal-art-bsidessf-2026)。
- **自动立体图解：** 重复层，差异混合，水平移动~100px以显示隐藏的3D文本。参见[隐写术.md](隐写术.md#autostereogram--magic-eye-solving-bsidessf-2026)。
- **双层字节+行交错：** 两个文件字节交错，然后扫描行交错。首先解交错奇偶字节（有效图像），然后奇偶行。参见[隐写术.md](隐写术.md#two-layer-byteline-interleaving-bsidessf-2026)。
- **SMB RID循环：** 客户端认证+LSARPC `LsaLookupSids`使用递增RID枚举AD账户。参见[网络-高级.md](网络-高级.md#smb-rid-recycling-via-lsarpc-midnight-2026)。
- **Timeroasting (MS-SNTP)：** 带机器RID的NTP请求从DC提取HMAC-MD5哈希；使用hashcat -m 31300破解。参见[网络-高级.md](网络-高级.md#timeroasting--ms-sntp-hash-extraction-midnight-2026)。
- **Android取证：** 使用`adb pull`提取APK，使用`apktool`分析，检查`shared_prefs/`和`/data/data/<package>/`中的SQLite数据库。参见[磁盘和内存.md](磁盘和内存.md#android-forensics)。
- **Docker容器取证：** `docker save`导出分层tar；删除的文件保留在早期层中。`docker history --no-trunc`揭示构建秘密。参见[磁盘和内存.md](磁盘和内存.md#container-forensics-docker)。
- **云存储取证：** S3/GCP/Azure版本控制保留删除的对象。`list-object-versions`恢复删除标志。参见[磁盘和内存.md](磁盘和内存.md#cloud-storage-forensics-aws-s3--gcp--azure)。
- **APFS快照恢复：** 写时复制文件系统在快照中保留历史文件状态；使用`icat`与不同的XID块偏移读取跨事务ID的inode。参见[磁盘-高级.md](磁盘-高级.md#apfs-snapshot-historical-file-recovery-srdnlenctf-2026)。
- **Windows KAPE分类：** 预收集的文物ZIP；从PowerShell历史→Amcache→MFT→注册表 hive开始。参见[磁盘和内存.md](磁盘和内存.md#windows-kape-triage-analysis-utctf-2026)。
- **WordPerfect宏XOR：** `.wcm`文件包含嵌入加密数据的宏；XOR公式`(a+b)-2*(a&b)`=按位XOR。参见[磁盘-高级.md](磁盘-高级.md#wordperfect-macro-xor-extraction-srdnlenctf-2026)。
- **从coredump提取TLS主密钥：** 在coredump中搜索会话ID（来自Wireshark握手）；将其之前的48字节读为主密钥。创建Wireshark预主密钥日志文件。参见[网络.md](网络.md#tls-master-key-extraction-from-coredump-plaidctf-2014)。
- **损坏的git blob修复：** 单字节损坏改变SHA-1；对每个字节位置（256 × 文件大小）进行暴力破解，使用`git hash-object`验证。参见[linux-forensics.md](linux-forensics.md#corrupted-git-blob-repair-via-byte-brute-force-csaw-ctf-2015)。
- **从PCAP重新组装分割存档：** 同样大小的HTTP传输文件，MD5哈希名称是存档片段；按Apache目录列表时间戳排序，连接，从TCP聊天流中提取密码。参见[网络.md](网络.md#split-archive-reassembly-from-http-transfers-asis-ctf-finals-2013)。
- **视频帧累积：** 视频中在各个位置闪烁图像；组合所有帧（逐像素最大值）揭示隐藏的QR码或图像。参见[stego-高级-2.md](stego-高级-2.md#video-frame-accumulation-for-hidden-image-asis-ctf-finals-2013)。
- **反转音频：** 听起来像反向播放的语音的混乱音频；`sox audio.wav reversed.wav reverse`或Audacity效果→反转揭示隐藏消息。参见[stego-高级-2.md](stego-高级-2.md#reversed-audio-hidden-message-asis-ctf-finals-2013)。
- **多流视频容器隐写：** MP4/MKV具有多个视频流；默认流是红鲱鱼，标志在次级流中。`ffprobe -hide_banner file.mp4`枚举，`ffmpeg -i file.mp4 -map 0:1 -frames:v 1 flag.jpg`提取。参见[隐写术.md](隐写术.md#multi-stream-video-container-steganography-bsidessf-2026)。
- **FAT16空闲空间恢复：** FAT16文件系统中隐藏在未分配簇中的标志。解析FAT表，枚举空闲簇（条目=0x0000），读取数据区域。参见[磁盘恢复.md](磁盘恢复.md#fat16-free-space-data-recovery-bsidessf-2026)。
- **FAT16已删除文件恢复（fls/icat）：** FAT删除用`0xE5`替换目录条目的第一个字节，但数据仍然存在。`fls -r -d image.img`列出已删除条目，`icat image.img <inode>`按inode恢复。参见[磁盘恢复.md](磁盘恢复.md#fat16-deleted-file-recovery-via-sleuth-kit-metactf-flash-2026)。
- **Ext2孤儿inode恢复：** 删除的文件留下孤儿inode；`e2fsck -y disk.img`重新连接到`/lost+found`。也使用`debugfs` `lsdel`或`icat`。参见[磁盘恢复.md](磁盘恢复.md#ext2-orphaned-inode-recovery-via-fsck-bsidessf-2026)。
- **Linux input_event键盘记录器解析：** 24字节`struct input_event`二进制转储；过滤`type==1`（EV_KEY），`value==1`（按下），通过`input-event-codes.h`映射键码。参见[signals-and-hardware.md](signals-and-hardware.md#linux-input_event-keylogger-dump-parsing-pwn2win-2016)。
- **VBA宏单元格数据到二进制：** Excel单元格中的数值；VBA `CByte((val-78)/3)`转换为ELF字节。在Python中重新实现，切勿运行宏。参见[linux-forensics.md](linux-forensics.md#vba-macro-forensics---excel-cell-data-to-elf-binary-sharif-ctf-2016)。
- **RGB奇偶校验隐写：** 每个像素的R+G+B求和；偶数=白色，奇数=黑色渲染隐藏的二进制位图。参见[stego-image.md](stego-image.md#rgb-parity-steganography-break-in-2016)。
- **隐藏PDF对象：** 未引用的内容流对象不在`/Kids`数组中。添加到`/Kids`，增加`/Count`，重新渲染。参见[网络-高级.md](网络-高级.md#unreferenced-pdf-objects-with-hidden-pages-sharifctf-7-2016)。
- **Arnold的猫映射解密：** 对方形图像进行周期性混沌变换；迭代正向映射直到原始重现。周期除以`3*N`。参见[stego-高级-2.md](stego-高级-2.md#arnolds-cat-map-image-descrambling-nuit-du-hack-2017)。
- **Python内存中源恢复：** 附加`pyrasite-shell`到正在运行的Python进程，使用`uncompyle6`（Python <=3.8）或`pycdc`（Python 3.9+）反编译`func_code`对象，转储`globals()`以获取秘密。参见[linux-forensics.md](linux-forensics.md#python-in-memory-source-recovery-via-pyrasite-insomnihack-2017)。
- **HFS+资源分叉恢复：** HFS+资源分叉中隐藏的数据对`binwalk`/`foremost`不可见；使用HFSExplorer + 010 Editor HFS模板提取扩展记录。参见[磁盘-高级.md](磁盘-高级.md#hfs-resource-fork-hidden-binary-recovery-confidence-ctf-2017)。
- **从WAV音频中UART串行：** 音频中的方波编码UART串行数据；确定波特率，解析起始/停止位，解码LSB优先字节帧。参见[signals-and-hardware.md](signals-and-hardware.md#serial-uart-data-decoding-from-wav-audio-easyctf-2017)。
- **高分辨率SSTV解调：** 标准SSTV解码器在高采样率录制上失败；使用`arccos`+微分进行手动FM解调。参见[stego-高级-2.md](stego-高级-2.md#high-resolution-sstv-custom-fm-demodulation-plaidctf-2017)。
- **损坏的 ZIP 头修复**：修复本地文件头（偏移量 26）和中目录（偏移量 28）中的文件名长度字段；备用方案：在候选偏移量处暴力破解原始 deflate。参见 [disk-recovery.md](disk-recovery.md#corrupted-zip-repair-via-header-field-manipulation-plaidctf-2017)。
- **SQLite 编辑历史重建**：从 SQLite 差异表中重播插入/删除差异，以重建文档在每一中间状态；旗帜可能已被输入然后删除。参见 [disk-advanced.md](disk-advanced.md#sqlite-edit-history-reconstruction-from-diff-table-google-ctf-2017)。
- **MJPEG FFD9 尾随字节隐写**：MJPEG 帧中 JPEG EOI 标记（FFD9）后的额外字节创建了不可见的隐蔽通道；在 FFD8 处分割，提取 FFD9 后数据。参见 [stego-advanced-2.md](stego-advanced-2.md#mjpeg-extra-bytes-after-ffd9-steganography-polictf-2017)。
- **USB MIDI Launchpad 网格重建**：USB PCAP 中的 MIDI Note On/Off 映射到 8x8 Launchpad 网格（`key = row*16 + col`）；从按键序列中重建视觉模式。参见 [signals-and-hardware.md](signals-and-hardware.md#usb-midi-launchpad-traffic-reconstruction-sthack-2017)。

## 通过 LSARPC 的 SMB RID 回收 (Midnight 2026)

通过分析 Guest 身份验证后的 LSARPC `LsaLookupSids` 调用中顺序 RID 的 AD 账户从 PCAP 中枚举。过滤条件：`dcerpc.cn_bind_to_str contains lsarpc`。

参见 [network-advanced.md](network-advanced.md#smb-rid-recycling-via-lsarpc-midnight-2026) 了解完整的 RPC 调用序列和 Wireshark 过滤器。

## Timeroasting / MS-SNTP 哈希提取 (Midnight 2026)

通过发送使用机器账户 RID 的 NTP 请求，从 MS-SNTP 响应中提取可破解的 HMAC-MD5 哈希。使用 `hashcat -m 31300` 进行破解。

```bash
# 提取 NTP 负载，转换为 hashcat 格式，破解
tshark -r capture.pcapng -Y "ntp && ip.src == <DC_IP>" -T fields -e udp.payload
hashcat -m 31300 -a 0 -O hashes.txt rockyou.txt --username
```

参见 [network-advanced.md](network-advanced.md#timeroasting--ms-sntp-hash-extraction-midnight-2026) 了解负载解析脚本和完整攻击链。

## PCAP 中的 HTTP 提取

**快速路径**：`tshark --export-objects http,/tmp/objects` 立即提取上传的文件。检查多部分 POST 上传、不寻常的 User-Agent 字符串和提取的文件（带有旗帜文本的图像）。参见 [network.md](network.md#http-file-upload-exfiltration-in-pcap-metactf-2026)。

## 常见编码

```bash
echo "base64string" | base64 -d
echo "hexstring" | xxd -r -p
# ROT13: tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

**ROT18**：字母 ROT13 + 数字 ROT5。多阶段取证中的常见最终层。参见 [linux-forensics.md](linux-forensics.md) 了解实现。
