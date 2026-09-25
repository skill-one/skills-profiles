# CTF取证与区块链

快速参考手册，用于取证CTF挑战。每种技术都有一行代码；有关详细信息，请参阅支持文件。

## 前置条件

**Python包（所有平台）：**
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

## 其他资源

- [3d-printing.md](3d-printing.md) - 3D打印取证（PrusaSlicer二进制G-code，QOIF，热缩）
- [windows.md](windows.md) - Windows取证（注册表，SAM，事件日志，回收站，NTFS替代数据流，USN日志，PowerShell历史记录，Defender MPLog，WMI持久化，Amcache）
- [network.md](network.md) - 网络取证基础（tcpdump，TLS/SSL密钥日志解密，从转储中提取TLS主密钥，Wireshark，PCAP，端口扫描，SMB3解密，5G/NR协议，WordPress侦察，凭证，USB HID速记，BCD编码，HTTP文件上传外泄，通过时间戳排序的分割存档重组）
- [network-advanced.md](network-advanced.md) - 高级网络取证（数据包间隔时间编码，NTLMv2哈希破解，TCP标志隐蔽通道，DNS最后字节隐写术，DNS尾随字节二进制编码，多层PCAP与XOR + ZIP和mDNS密钥，Brotli解压缩炸弹接缝分析，通过LSARPC的SMB RID循环，Timeroasting MS-SNTP哈希提取，dnscat2重组，RADIUS共享密钥破解，RC4流识别，ICMP有效载荷字节旋转，ICMP ping时间延迟隐蔽通道）
- [peripheral-capture.md](peripheral-capture.md) - USB/HID/蓝牙外设流量重建（USB HID鼠标/笔绘画恢复，USB HID键盘捕获解码，USB键盘LED摩斯密码外泄，USB HID键盘箭头键导航跟踪，Bluetooth RFCOMM数据包重组）
- [disk-and-memory.md](disk-and-memory.md) - 核心磁盘/内存取证（Volatility，磁盘挂载/雕刻，VM/OVA/VMDK，VMware快照，GIMP原始内存转储视觉检查，转储，Windows KAPE筛选，PowerShell勒索软件，Android取证，Docker容器取证，云存储取证，BSON重建，TrueCrypt/VeraCrypt挂载）
- [disk-advanced.md](disk-advanced.md) - 高级磁盘和内存技术（已删除分区，ZFS取证，GPT GUID编码，VMDK稀疏解析，内存转储字符串雕刻，勒索软件密钥恢复，WordPerfect宏XOR，minidump ISO 9660恢复，APFS快照恢复，RAID 5 XOR恢复，HFS+资源分叉恢复，Kyoto Cabinet哈希数据库取证，SQLite编辑历史重建）
- [disk-recovery.md](disk-recovery.md) - 磁盘恢复和提取模式（LUKS主密钥恢复，PRNG时间戳种子暴力破解，VBA宏二进制恢复，FemtoZip解压缩，XFS文件系统重建，tar重复条目提取，嵌套套娃式文件系统提取，通过空字节交错进行反雕刻，BTRFS子卷/快照恢复，FAT16空闲空间数据恢复，通过Sleuth Kit fls/icat的FAT16已删除文件恢复，ext2孤儿inode恢复通过fsck，损坏的ZIP标题修复）
- [steganography.md](steganography.md) - 通用隐写术（二进制边界隐写术，PDF多层隐写术，SVG关键帧，PNG重排序，文件叠加，GIF帧差异摩斯密码，GZSteg + spammimic，电子表格频率恢复，Kitty终端图形协议解码，ANSI转义序列隐写术，自动立体图解法，双层字节+行交错，多流视频容器隐写术，渐进式PNG分层XOR解密，从弯曲反射中重建二维码）
- [stego-image.md](stego-image.md) - 针对图像的隐写术（JPEG未使用的DQT表LSB，BMP位平面QR提取，图像拼图重组，F5 JPEG DCT比率检测，PNG未使用的调色板条目隐写术，QR码瓦片重建，基于种子的像素置换+多位平面QR，JPEG缩略图像素到文本映射，条件LSB与像素过滤，JPEG slack空间，最近邻插值隐写术，RGB奇偶校验隐写术）
- [stego-advanced.md](stego-advanced.md) - 高级隐写术第一部分：音频和信号技术（FFT频域，DTMF音频，SSTV+LSB，DotCode条形码，自定义频率双音调键盘，多轨音频差分减法，跨通道多比特LSB，音频FFT音乐音符，音频元数据八进制编码，嵌套tar空白编码，DeepSound音频隐写术与密码破解，音频波形二进制编码，音频频谱图隐藏QR）
- [stego-advanced-2.md](stego-advanced-2.md) - 高级隐写术第二部分：视频，图像变换和格式特定技术（视频帧累积，反向音频，视频帧平均，JPEG XL TOC重排序隐写术，阿诺德的猫映射解密，高分辨率SSTV自定义FM解调，MJPEG FFD9尾随字节隐写术，EXIF zlib + Stegano像素模式，PDF xref隐蔽通道，ANSI转义代码隐写术，逐像素ECB去重）
- [linux-forensics.md](linux-forensics.md) - Linux/应用程序取证（日志分析，Docker镜像取证，攻击链，浏览器凭证，Firefox历史记录，TFTP，TLS弱RSA，USB音频，Git目录恢复，KeePass v4破解，Git reflog/fsck挤压恢复，浏览器证据分析（Chrome/Chromium/Firefox历史记录，cookies，下载，本地存储，会话恢复），损坏的git blob修复通过字节暴力破解，VBA宏Excel单元格数据到ELF二进制提取，Python内存中源恢复通过pyrasite）
- [signals-and-hardware.md](signals-and-hardware.md) - 硬件信号解码（VGA帧解析，HDMI TMDS符号解码，DisplayPort 8b/10b + LFSR解密器），Voyager Golden Record音频，Saleae Logic 2 UART解码，Flipper Zero .sub文件，侧信道功率分析（DPA），键盘声学侧信道，CD音频光盘映像隐写术（CIRC解复用+螺旋渲染），caps-lock LED摩斯密码从视频中，Linux input_event键记录解析，从WAV音频中获取串行UART，USB MIDI Launchpad网格重建）

---

## 何时转向

- 如果你恢复了一个加密的blob，而难题变成了RSA、AES或格点工作，请切换到`/ctf-crypto`。
- 如果证据确实指向恶意软件准备阶段，信标配置提取或打包样本，请切换到`/ctf-malware`。
- 如果该证据是一个Web应用程序备份或API转储，而剩余的问题是应用程序逻辑，请切换到`/ctf-web`。
- 如果取证证据实际上是编码谜题，隐写术技巧或特殊格式而不是真正的取证，请切换到`/ctf-misc`。
- 如果你需要追踪基础设施，归因参与者或调查来自取证发现的公共记录，请切换到`/ctf-osint`。
- 如果恢复的文
