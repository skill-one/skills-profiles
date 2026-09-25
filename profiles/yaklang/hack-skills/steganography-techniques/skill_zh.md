# 技能：隐写术技术——专家分析操作手册

> **AI 加载指令**：专家级隐写术检测与提取技术。涵盖图像隐写术（最低有效位、PNG 数据块隐藏、JPEG DCT、EXIF 元数据、尺寸技巧、调色板操作）、音频隐写术（频谱图、最低有效位、双音多频信号、摩尔斯电码）、文件隐写术（多格式文件、binwalk、NTFS 附加数据流、Steghide）和文本隐写术（空白字符、零宽 Unicode、同形字）。基础模型缺乏基于文件类型的系统分析方法和特定工具的提取工作流。

## 0. 相关路由

在深入之前，请考虑加载：

- [流量分析 pcap](../traffic-analysis-pcap/SKILL.md) 用于在隐写术分析前从网络捕获中提取文件
- [内存取证 volatility](../memory-forensics-volatility/SKILL.md) 用于从内存转储中提取文件
- [古典密码分析](../classical-cipher-analysis/SKILL.md) 如果提取的隐藏数据进一步加密/编码

### 工具参考

当您需要时，也加载 [STEGO_TOOLS_GUIDE.md](./STEGO_TOOLS_GUIDE.md)：
- 工具安装说明和依赖项
- 每个隐写术工具的详细命令参考
- 特定文件类型的操作流程

---

## 1. 图像隐写术

### 最低有效位 (LSB)

LSB 将数据嵌入到像素颜色通道的最低有效位中。

```bash
# zsteg — PNG/BMP 的 LSB 分析
zsteg image.png                       # 自动检测所有 LSB 模式
zsteg image.png -a                    # 尝试所有已知方法
zsteg image.png -b 1                  # 提取第 1 位平面
zsteg image.png -E "b1,rgb,lsb,xy"   # 特定提取模式

# StegSolve (Java 图形界面)
java -jar StegSolve.jar
# 导航颜色平面：红色 0、绿色 0、蓝色 0 → 查找隐藏的图像/文本
# 数据提取器：指定位平面 + 字节顺序

# stegoveritas — 全面自动化分析
stegoveritas image.png
# 运行：exiftool、binwalk、zsteg、foremost、颜色平面提取
```

### PNG 特定

```bash
# pngcheck — 验证结构，查找隐藏数据块
pngcheck -v image.png

# 隐藏数据块：tEXt、zTXt（压缩文本）、iTXt（国际文本）
# 自定义/私有数据块可能包含隐藏数据

# CRC 与尺寸技巧
# 如果 CRC 与声明尺寸不匹配 → 图像被裁剪
# 修复：暴力破解正确宽/高 → 揭示隐藏的行/列
python3 -c "
import struct, zlib
with open('image.png','rb') as f:
    data = f.read()
# 检查 IHDR CRC 在偏移 29
ihdr = data[12:29]
for h in range(1,2000):
    for w in range(1,2000):
        new_ihdr = struct.pack('>II',w,h) + ihdr[8:]
        if zlib.crc32(b'IHDR'+new_ihdr) & 0xffffffff == struct.unpack('>I',data[29:33])[0]:
            print(f'Width: {w}, Height: {h}')
"

# APNG（动画 PNG）— 隐藏帧
# 使用 apngdis 提取所有帧：apngdis image.png
```

### JPEG 特定

```bash
# steghide — 从 JPEG 嵌入/提取（DCT 系数修改）
steghide extract -sf image.jpg                 # 提取（无密码）
steghide extract -sf image.jpg -p PASSWORD     # 使用密码提取
steghide info image.jpg                        # 检查是否嵌入数据

# stegcracker — 暴力破解 steghide 密码
stegcracker image.jpg wordlist.txt

# jsteg — JPEG LSB 隐写术
jsteg reveal image.jpg output.txt

# JPEG 结构分析
exiftool -v3 image.jpg       # 详细元数据 + 结构
jpegdump image.jpg           # 原始 JPEG 标记分析
```

### EXIF 元数据

```bash
# exiftool — 全面元数据提取
exiftool image.jpg
exiftool -b -ThumbnailImage image.jpg > thumb.jpg   # 提取缩略图
exiftool -all= image.jpg                             # 移除所有元数据

# EXIF 字段中的隐藏数据（注释、艺术家、版权等）
exiftool -Comment image.jpg
exiftool -UserComment image.jpg
strings image.jpg | grep -i "flag\|key\|secret"
```

### 调色板基于（GIF）

```bash
# GIF 色彩表操作 — 数据按调色板顺序存储
gifsicle -I image.gif                    # 信息
gifsicle --color-info image.gif          # 调色板详情
# 检查动画帧：convert -coalesce image.gif frame_%d.png
```

---

## 2. 音频隐写术

### 频谱图分析

```bash
# Sonic Visualiser — 最佳频谱图查看工具
# 图层 → 添加频谱图 → 查找视觉模式（文本/图像）

# Audacity
# 分析 → 绘制频谱
# 选择音频 → 切换视图为频谱图

# sox 用于命令行频谱图生成
sox audio.wav -n spectrogram -o spectro.png
```

### 音频 LSB

```bash
# DeepSound — 在音频中隐藏/提取文件（Windows）
# 图形工具：打开音频文件 → 提取隐藏文件

# WavSteg — WAV 文件的 LSB
python3 WavSteg.py -r -i audio.wav -o output.txt -n 1   # 提取 1 LSB
python3 WavSteg.py -r -i audio.wav -o output.txt -n 2   # 提取 2 LSB
```

### 双音多频信号 / 摩尔斯电码

```bash
# 双音多频信号解码器（电话音调）
multimon-ng -t wav -a DTMF audio.wav

# 摩尔斯电码
# Audacity → 视觉检查开/关模式
# 在线解码器或手动：.- = A, -... = B, 等。

# SSTV（慢扫描电视）— 音频中的图像
qsstv                    # 图形解码器
# 或：RX-SSTV（Windows）
```

### WAV 头部操作

```bash
# 检查 WAV 音频数据后的附加数据
# WAV 数据块大小与实际文件大小
python3 -c "
import wave
w = wave.open('audio.wav','rb')
print(f'Frames: {w.getnframes()}, Channels: {w.getnchannels()}, Width: {w.getsampwidth()}')
expected = w.getnframes() * w.getnchannels() * w.getsampwidth() + 44  # 44 = WAV 头部
import os
actual = os.path.getsize('audio.wav')
if actual > expected:
    print(f'Extra data: {actual - expected} bytes appended')
"
```

---

## 3. 文件隐写术

### 多格式文件

一个同时符合两种或多种格式的文件。

```bash
# 检测：使用多个工具检查文件
file suspicious_file
xxd suspicious_file | head          # 检查魔数
binwalk suspicious_file             # 查找嵌入文件

# 常见多格式文件：PDF+ZIP、JPEG+ZIP、JPEG+RAR、PNG+ZIP
# 尝试在图像文件上解压缩：
unzip image.jpg -d extracted/
7z x image.jpg -oextracted/
```

### 附加 / 嵌入数据

```bash
# binwalk — 扫描嵌入文件和数据
binwalk image.png                   # 扫描
binwalk -e image.png                # 提取嵌入文件
binwalk --dd='.*' image.png         # 提取所有内容

# foremost — 文件雕刻
foremost -i suspicious_file -o output_dir/

# dd — 手动提取
# 如果 binwalk 显示嵌入 ZIP 在偏移 0x1234：
dd if=suspicious_file bs=1 skip=$((0x1234)) of=extracted.zip
```

### NTFS 附加数据流 (ADS)

```cmd
:: 列出 ADS（Windows）
dir /r file.txt
Get-Item file.txt -Stream *

:: 读取隐藏流
more < file.txt:hidden_stream
Get-Content file.txt -Stream hidden_stream

:: 创建 ADS（用于测试）
echo "hidden data" > file.txt:secret
```

### Steghide 暴力破解

```bash
# stegcracker — 对 steghide 密码进行字典攻击
stegcracker image.jpg /usr/share/wordlists/rockyou.txt

# stegseek — 更快的替代方案
stegseek image.jpg /usr/share/wordlists/rockyou.txt
# stegseek 比 stegcracker 快约 10000 倍
```

---

## 4. 文本隐写术

### 空白字符编码

```bash
# 制表符和空格编码二进制（制表符=1，空格=0 或反之）
# stegsnow — 空白字符隐写术
stegsnow -C message.txt                # 提取隐藏消息
stegsnow -C -p PASSWORD message.txt    # 使用密码提取

# 手动检测：
cat -A file.txt | head     # 显示制表符 (^I) 和行尾 ($)
xxd file.txt | grep "09 20\|20 09"    # 查找制表符/空格模式
```

### 零宽字符

```bash
# 使用 Unicode 不可见字符进行编码：
# U+200B（零宽空格）、U+200C（零宽非间距连字符）、U+200D（零宽连字符）、U+FEFF（字节顺序标记）

# 检测：
python3 -c "
text = open('message.txt','r').read()
hidden = [c for c in text if ord(c) in [0x200b, 0x200c, 0x200d, 0xfeff]]
print(f'Found {len(hidden)} zero-width characters')
binary = ''.join('0' if ord(c)==0x200b else '1' for c in hidden)
# 将二进制转换为 ASCII
"

# 在线工具：holloway.nz/steg、Unicode 隐写术解码器
```

### 同形字替换

```bash
# 来自不同 Unicode 块的视觉上相同的字符
# 例如，拉丁 'a' (U+0061) 与西里尔 'а' (U+0430)

# 检测：
python3 -c "
text = open('message.txt','r').read()
for i, c in enumerate(text):
    if ord(c) > 127:
        print(f'Position {i}: char={c} ord={ord(c)} name={__import__(\"unicodedata\").name(c,\"?\")}')
"
```

---

## 5. 决策树

```
怀疑隐藏数据 — 文件类型是什么？
│
├── 图像 (PNG/BMP)？
│   ├── 检查元数据：exiftool (§1 EXIF)
│   ├── 检查结构：pngcheck、binwalk (§1 PNG)
│   ├── LSB 分析：zsteg、StegSolve (§1 LSB)
│   ├── 检查尺寸与 CRC：高度/宽度暴力破解 (§1 PNG)
│   ├── 检查附加数据：binwalk -e (§3)
│   └── 尝试作为多格式文件：unzip/7z (§3)
│
├── 图像 (JPEG)？
│   ├── 检查元数据：exiftool (§1 EXIF)
│   ├── 尝试 steghide：steghide extract (§1 JPEG)
│   │   └── 密码保护？→ stegseek 暴力破解 (§3)
│   ├── 尝试 jsteg：jsteg reveal (§1 JPEG)
│   ├── 检查附加数据：binwalk -e (§3)
│   └── 检查缩略图：exiftool -b -ThumbnailImage (§1 EXIF)
│
├── 图像 (GIF)？
│   ├── 检查帧：提取所有动画帧 (§1 调色板)
│   ├── 检查调色板：gifsicle --color-info (§1 调色板)
│   └── 检查附加数据：binwalk -e (§3)
│
├── 音频 (WAV/MP3/FLAC)？
│   ├── 频谱图：Sonic Visualiser / Audacity (§2)
│   ├── LSB：WavSteg (§2)
│   ├── 双音多频信号：multimon-ng (§2)
│   ├── 摩尔斯电码：手动或解码器 (§2)
│   ├── SSTV：qsstv (§2)
│   └── 检查文件大小与预期：头部分析 (§2)
│
├── 文本文件？
│   ├── 检查空白字符：cat -A、stegsnow (§4)
│   ├── 检查零宽字符：Unicode 分析 (§4)
│   ├── 检查同形字：非 ASCII 检测 (§4)
│   └── 检查编码：多种 Base 解码
│
├── 任何文件类型？
│   ├── strings：strings -n 8 file | grep -i "flag\|key\|pass"
│   ├── binwalk：binwalk -e file (嵌入文件) (§3)
│   ├── file：file suspicious_file (真实类型)
│   ├── xxd：检查魔数，比较头部
│   └── NTFS？→ 检查 ADS：dir /r (§3)
│
└── 需要密码/密码短语？
    ├── steghide → stegseek / stegcracker (§3)
    ├── 检查挑战描述中的提示
    └── 尝试常见密码：密码、文件名、挑战名
```
