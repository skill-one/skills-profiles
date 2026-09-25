# CTF OSINT

OSINT CTF挑战的快速参考。每个技术在这里都有一个一行代码；有关详细信息，请参阅支持文件。

## 前置条件

**Python包（所有平台）：**
```bash
pip install shodan Pillow
```

**Linux（apt）：**
```bash
apt install whois dnsutils nmap libimage-exiftool-perl imagemagick curl
```

**macOS（Homebrew）：**
```bash
brew install whois bind nmap exiftool imagemagick curl
```

## 额外资源

- [social-media.md](social-media.md) - Twitter/X（用户ID、Snowflake时间戳、Nitter、memory.lol、Wayback CDX），Tumblr（博客检查、帖子JSON、头像），BlueSky搜索+API，Unicode同形异体字隐写术，Discord API，用户名OSINT（namechk、whatsmyname、Osint Industries），用户名元数据挖掘（邮政编码），平台误报，多平台链，Strava健身路线OSINT
- [geolocation-and-media.md](geolocation-and-media.md) - 图像分析，反向图像搜索（包括百度用于中国），Google Lens裁剪区域搜索，反射/镜像文本读取，地理位置技术（铁路标志、基础设施地图、MGRS），Google Plus Codes，EXIF/元数据，硬件识别，报纸存档，IP地理位置，Google街景全景匹配，What3Words微地标匹配，Google Maps众包照片验证，Overpass Turbo空间查询，音乐主题地标地理位置与密钥编码
- [web-and-dns.md](web-and-dns.md) - Google dorking（包括TBS图像过滤器），Google Docs/Sheets枚举，DNS侦察（TXT、区域传输），Wayback Machine，FEC研究，Tor中继查找，GitHub仓库分析，Telegram机器人调查，WHOIS调查（反向WHOIS、历史WHOIS、IP/ASN查找），通过nmap指纹识别检测假冒服务横幅

---

## 何时转向

- 如果你已经本地拥有文件或数据包，现在需要提取或雕刻，请切换到`/ctf-forensics`。
- 如果任务变成对实时HTTP服务的主动利用，请切换到`/ctf-web`。
- 如果你在进行归因时发现恶意软件样本、信标或可疑二进制文件，请切换到`/ctf-malware`。

## 快速启动命令

```bash
# DNS侦察
dig -t any target.com
dig -t txt target.com
dig axfr @ns.target.com target.com
whois target.com

# 图像元数据
exiftool image.jpg
identify -verbose image.jpg | head -30

# 网页存档
curl "https://web.archive.org/web/20230101*/target.com"

# 用户名查找
curl -s "https://whatsmyname.app/api/lookup?username=<user>"

# Shodan
shodan search "hostname:target.com"
shodan host <ip>
```

## 字符串识别

- 40个十六进制字符 -> SHA-1（Tor指纹）
- 64个十六进制字符 -> SHA-256
- 32个十六进制字符 -> MD5

## Twitter/X账户跟踪

- 持久性数字用户ID：`https://x.com/i/user/<id>`即使在重命名后也能正常工作。
- Snowflake时间戳：`(id >> 22) + 1288834974657` = Unix毫秒。
- Wayback CDX、Nitter、memory.lol用于历史数据。参见[social-media.md](social-media.md)。

## Tumblr调查

- 博客检查：`curl -sI`用于`x-tumblr-user`头部。头像在`/avatar/512`。参见[social-media.md](social-media.md)。

## 用户名OSINT

- [whatsmyname.app](https://whatsmyname.app)（741+网站），[namechk.com](https://namechk.com)。注意平台误报。参见[social-media.md](social-media.md)。

## 图像分析 & 反向图像搜索

- Google Lens（裁剪到感兴趣区域），Google Images，TinEye，Yandex（人脸）。检查角落以查找视觉隐写术。Twitter删除EXIF。参见[geolocation-and-media.md](geolocation-and-media.md)。
- **裁剪区域搜索：**隔离独特元素（商店标志、建筑立面）并通过Google Lens搜索，以获得比全场景搜索更好的结果。参见[geolocation-and-media.md](geolocation-and-media.md)。
- **反射文本：**水平翻转镜像/反射文本（水、玻璃）；用引号搜索部分文本。参见[geolocation-and-media.md](geolocation-and-media.md)。

## 地理位置信息

- 铁路标志、基础设施地图（OpenRailwayMap、OpenInfraMap）、排除法。参见[geolocation-and-media.md](geolocation-and-media.md)。
- **街景全景匹配：**特征提取+多度量图像相似性排名，与候选全景进行对比。当挑战图像是街景照片的裁剪时很有用。参见[geolocation-and-media.md](geolocation-and-media.md)。
- **道路标志OCR：**从方向标志（城镇名称、路线编号）中提取文本，以精确定位道路走廊。驾驶侧+标志样式+脚本识别国家。参见[geolocation-and-media.md](geolocation-and-media.md)。
- **建筑 + 品牌识别：**苏联后混凝土=俄罗斯/独联体；知名企业→搜索位置/分支机构→与海岸线/地形交叉引用。参见[geolocation-and-media.md](geolocation-and-media.md)。
- **音乐主题地标地理位置：**全球多个音乐相关地标的照片；每个地标产生一个钢琴键编号编码一个标志字符。首先识别所有位置，然后解码密钥序列。参见[geolocation-and-media.md](geolocation-and-media.md)。

## MGRS坐标

- 网格格式"4V FH 246 677"->在线转换器->纬度/经度->Google Maps。参见[geolocation-and-media.md](geolocation-and-media.md)。

## Google Plus Codes

- 格式`XXXX+XXX`（字符：`23456789CFGHJMPQRVWX`）。在Google Maps上放置一个标记→Plus Code出现在详细信息中。免费，无需API密钥。参见[geolocation-and-media.md](geolocation-and-media.md)。

## 元数据提取

```bash
exiftool image.jpg           # EXIF数据
pdfinfo document.pdf         # PDF元数据
mediainfo video.mp4          # 视频元数据
```

## Google Dorking

```text
site:example.com filetype:pdf
intitle:"index of" password
```

**图像TBS过滤器：**将`tbs=itp:face`附加到Google图像URL以仅过滤人脸（删除标志/横幅）。参见[web-and-dns.md](web-and-dns.md)。

## Google Docs/Sheets

- 尝试`/export?format=csv`，`/pub`，`/gviz/tq?tqx=out:csv`，`/htmlview`。参见[web-and-dns.md](web-and-dns.md)。

## DNS侦察

```bash
dig -t txt subdomain.ctf.domain.com
dig axfr @ns.domain.com domain.com  # 区域传输
```

始终检查CTF域的TXT、CNAME、MX。参见[web-and-dns.md](web-and-dns.md)。

## Tor中继查找

- `https://metrics.torproject.org/rs.html#simple/<FINGERPRINT>` -- 检查家族，按"首次出现"排序。参见[web-and-dns.md](web-and-dns.md)。

## GitHub仓库分析

- 通过`gh api`检查问题评论、PR审查、提交消息、维基编辑。参见[web-and-dns.md](web-and-dns.md)。

## Telegram机器人调查

- 在浏览器历史记录中查找机器人引用，通过`/start`交互，回答验证问题。参见[web-and-dns.md](web-and-dns.md)。

## FEC政治捐款研究

- FEC.gov用于委员会收据；501(c)(4)组织掩盖原始资助者。参见[web-and-dns.md](web-and-dns.md)。

## IP地理位置

```bash
curl "http://ip-api.com/json/103.150.68.150"
```

参见[geolocation-and-media.md](geolocation-and-media.md)。

## Unicode同形异体字隐写术

**模式：**来自不同区块（西里尔、希腊、数学）的视觉上相同的Unicode字符在社交媒体帖子中编码二进制数据。ASCII=0，同形异体字=1。将位分组为字节以获取标志。参见[social-media.md](social-media.md#unicode-homoglyph-steganography-on-bluesky-metactf-2026)。

## BlueSky公共API

无需认证。端点：`public.api.bsky.app/xrpc/app.bsky.feed.searchPosts?q=...`，`app.bsky.actor.searchActors`，`app.bsky.feed.getAuthorFeed`。检查所有对官方帖子的回复。参见[social-media.md](social-media.md#unicode-homoglyph-steganography-on-bluesky-metactf-2026)。

## 假冒服务横幅检测

**模式：**在标准服务端口（22/SSH、80/HTTP）上出现开放端口，但运行假冒服务。`nmap -sV`或`nc host port`在横幅中显示标志。永远不要单独信任端口号——始终指纹识别服务。参见[web-and-dns.md](web-and-dns.md#fake-service-banner-detection-via-fingerprinting-metactf-flash-2026)。

## Shodan SSH指纹查找

通过SSH主机密钥指纹搜索Shodan以识别服务器：`shodan search "fingerprint:AA:BB:CC:..."`。参见[web-and-dns.md](web-and-dns.md#shodan-ssh-fingerprint-lookup-ekoparty-ctf-2016)。

## 游戏平台OSINT

跨游戏平台（Steam、Xbox、PSN、MMO）查找用户名，以获取角色资料、活动和关联账户。参见[social-media.md](social-media.md#gaming-platform-osint--mmo-character-lookup-csaw-ctf-2016)。

## 资源

- **Shodan** - 连接到互联网的设备
- **Censys** - 证书和主机搜索
- **VirusTotal** - 文件/URL声誉
- **WHOIS** - 域名注册
- **Wayback Machine** - 历史快照
