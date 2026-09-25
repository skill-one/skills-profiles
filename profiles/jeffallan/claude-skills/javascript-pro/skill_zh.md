# JavaScript Pro

## 何时使用此技能

- 构建纯 JavaScript 应用程序
- 实现 async/await 模式和 Promise 处理
- 使用现代模块系统（ESM/CJS）
- 优化浏览器性能和内存使用
- 开发 Node.js 后端服务
- 实现 Web Workers、Service Workers 或浏览器 API

## 核心工作流

1. **分析需求** — 查看 `package.json`、模块系统、Node 版本、浏览器目标；确认 `.js`/`.mjs`/`.cjs` 规范
2. **设计架构** — 规划模块、异步流程和错误处理策略
3. **实现** — 使用 ES2023+ 代码并采用正确的模式和优化
4. **验证** — 运行 linter (`eslint --fix`)；如果 linter 失败，修复所有报告的问题并重新运行。使用 DevTools 或 `--inspect` 检查内存泄漏，验证打包大小；如果发现内存泄漏，解决它们后再继续
5. **测试** — 使用 Jest 编写全面测试，覆盖率达到 85%+；如果覆盖率不足，添加缺失用例并重新运行。确认没有未处理的 Promise rejections

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| 现代语法 | `references/modern-syntax.md` | ES2023+ 特性、可选链、私有字段 |
| 异步模式 | `references/async-patterns.md` | Promises、async/await、错误处理、事件循环 |
| 模块 | `references/modules.md` | ESM 与 CJS、动态导入、package.json exports |
| 浏览器 API | `references/browser-apis.md` | Fetch、Web Workers、存储、IntersectionObserver |
| Node 核心知识 | `references/node-essentials.md` | fs/promises、流、EventEmitter、worker threads |

## 限制

### 必须

- 仅使用 ES2023+ 特性
- 使用 `X | null` 或 `X | undefined` 模式
- 使用可选链 (`?.`) 和空值合并 (`??`)
- 使用 async/await 进行所有异步操作
- 新项目使用 ESM (`import`/`export`)
- 使用 try/catch 实现正确的错误处理
- 为复杂函数添加 JSDoc 注释
- 遵循函数式编程原则

### 禁止

- 使用 `var`（始终使用 `const` 或 `let`）
- 使用回调模式（优先使用 Promises）
- 在同一模块中混合 CommonJS 和 ESM
- 忽略内存泄漏或性能问题
- 在异步函数中跳过错误处理
- 在 Node.js 中使用同步 I/O
- 修改函数参数
- 在浏览器中创建阻塞操作

## 关键模式示例

### Async/Await 错误处理

```js
// ✅ 正确 — 明确处理异步错误
async function fetchUser(id) {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (err) {
    console.error("fetchUser 失败:", err);
    return null;
  }
}

// ❌ 错误 — 未处理的 rejection，没有 null 防护
async function fetchUser(id) {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}
```

### 可选链 & 空值合并

```js
// ✅ 正确
const city = user?.address?.city ?? "Unknown";

// ❌ 错误 — 如果 address 是 undefined 会抛出异常
const city = user.address.city || "Unknown";
```

### ESM 模块结构

```js
// ✅ 正确 — 命名导出，库不使用默认导出
// utils/math.mjs
export const add = (a, b) => a + b;
export const multiply = (a, b) => a * b;

// consumer.mjs
import { add } from "./utils/math.mjs";

// ❌ 错误 — 混合 require() 与 ESM
const { add } = require("./utils/math.mjs");
```

### 避免 var / 优先使用 const

```js
// ✅ 正确
const MAX_RETRIES = 3;
let attempts = 0;

// ❌ 错误
var MAX_RETRIES = 3;
var attempts = 0;
```

## 输出模板

实现 JavaScript 特性时提供：

1. 模块文件，包含干净的导出
2. 测试文件，包含全面覆盖率
3. 公共 API 的 JSDoc 文档
4. 所用模式的简要说明

[文档](https://jeffallan.github.io/claude-skills/skills/language/javascript-pro/)
