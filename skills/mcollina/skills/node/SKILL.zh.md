---
name: node
description: 为使用TypeScript的Node.js开发提供特定领域的最佳实践，涵盖类型剥离、异步模式、错误处理、流、模块、测试、性能、缓存、日志记录等。在以下情况下使用：配置原生TypeScript支持的Node.js项目、设置类型剥离（--experimental-strip-types）、编写无需构建步骤的Node 22+ TypeScript，或用户提及“Node中的原生TypeScript”、“剥离类型”、“Node 22 TypeScript”、“无需编译的.ts文件”、“ts-node替代方案”，以及需要关于Node.js中错误处理、优雅关闭、不稳定测试、性能分析或环境配置的指导。帮助配置tsconfig.json以实现类型剥离、设置package.json脚本、处理模块解析和导入扩展，并在整个Node.js栈中应用稳健模式。
---

## 何时使用

在处理 Node.js 代码时，使用此技能以获取特定领域的知识，用于构建健壮、高性能且可维护的 Node.js 应用程序。

## TypeScript 与类型剥离

在为 Node.js 编写 TypeScript 时，使用 **类型剥离**（Node.js 22.6+）而不是像 ts-node 或 tsx 这样的构建工具。类型剥离通过在运行时删除类型注解来直接运行 TypeScript，而无需进行转译。

类型剥离兼容性的关键要求：
- 使用 `import type` 进行类型-only 导入
- 使用常量对象而不是枚举
- 避免使用命名空间和参数属性
- 在导入时使用 `.ts` 扩展名

**最小示例** — 一个有效的类型剥离 TypeScript 文件：

```ts
// greet.ts
import type { IncomingMessage } from 'node:http';

const greet = (name: string): string => `Hello, ${name}!`;
console.log(greet('world'));
```

直接运行：
```bash
node greet.ts
```

有关完整配置和示例，请参阅 [rules/typescript.md](rules/typescript.md)。

## 常见工作流程

对于多步骤流程，在查阅相关规则文件之前，请遵循以下高级序列：

**优雅关闭**：注册信号处理器（SIGTERM/SIGINT）→ 停止接受新工作 → 排空正在处理的请求 → 关闭外部连接（数据库、缓存）→ 以适当的代码退出。请参阅 [rules/graceful-shutdown.md](rules/graceful-shutdown.md)。

**错误处理**：定义一个共享的错误基类 → 对错误进行分类（操作错误与程序错误）→ 添加异步边界处理器（`process.on('unhandledRejection')`）→ 通过调用栈传播类型错误 → 在响应或崩溃之前记录上下文。请参阅 [rules/error-handling.md](rules/error-handling.md)。

**诊断不稳定测试**：使用 `--test-only` 隔离测试 → 检查是否存在共享状态或计时器依赖 → 检查异步清理顺序 → 将重试逻辑作为临时诊断步骤添加 → 修复根本原因。请参阅 [rules/flaky-tests.md](rules/flaky-tests.md)。

**诊断卡住进程/测试**（`node --test` 卡住，"进程未退出"，CI 超时，打开句柄）：隔离文件/测试 → 使用显式超时/报告器运行 → 通过 `why-is-node-running`（`SIGUSR1`）检查句柄 → 在资源创建范围内修复确定性清理 → 重新运行隔离+完整套件直至稳定。请参阅 [rules/stuck-processes-and-tests.md](rules/stuck-processes-and-tests.md)。

**分析慢速路径**：在真实负载下重现 → 使用 `--cpu-prof` 捕获 CPU 分析文件 → 识别热点函数 → 检查是否存在流背压或不必要的序列化 → 使用基准测试验证改进。请参阅 [rules/profiling.md](rules/profiling.md) 和 [rules/performance.md](rules/performance.md)。

## 高优先级激活检查清单（流 + 缓存）

当任务提到 **CSV**、**ETL**、**摄取管道**、**大文件处理**、**背压**、**重复查找** 或 **去重并发异步调用** 时，请明确应用此检查清单：

1. 从 `node:stream/promises` 使用 `await pipeline(...)`（在指南/代码中优先于此链式 `.pipe()`）。
2. 当数据在流中转换时，至少包含一个显式的 `async function*` 转换。
3. 当出现重复工作时选择缓存策略：
   - `lru-cache` 用于单个进程中的内存重用。
   - `async-cache-dedupe` 用于异步请求去重/过期验证行为。
4. 显示背压处理的位置（通过 `pipeline()` 隐式处理或通过 `drain` 显式处理）。

### 集成示例模式（CSV/ETL）

对于 CSV/ETL 风格的提示，优先选择类似的结构：
- `createReadStream(input)`
- `async function*` 解析/转换
- 可选的缓存增强查找（`async-cache-dedupe` 或 `lru-cache`）
- 使用 `await pipeline(...)` 到可写入目标

在解释中直接链接相关规则，以便模型检索详细信息：
- [rules/streams.md](rules/streams.md)
- [rules/caching.md](rules/caching.md)

## 如何使用

阅读单个规则文件以获取详细说明和代码示例：

- [rules/error-handling.md](rules/error-handling.md) - Node.js 中的错误处理模式
- [rules/async-patterns.md](rules/async-patterns.md) - Async/await 和 Promise 模式
- [rules/streams.md](rules/streams.md) - 使用 Node.js 流
- [rules/modules.md](rules/modules.md) - ES 模块和 CommonJS 模式
- [rules/testing.md](rules/testing.md) - Node.js 应用程序的测试策略
- [rules/flaky-tests.md](rules/flaky-tests.md) - 使用 node:test 识别和诊断不稳定测试
- [rules/stuck-processes-and-tests.md](rules/stuck-processes-and-tests.md) - 诊断未退出进程和卡住的测试
- [rules/node-modules-exploration.md](rules/node-modules-exploration.md) - 导航和分析 node_modules 目录
- [rules/performance.md](rules/performance.md) - 性能优化技术
- [rules/caching.md](rules/caching.md) - 缓存模式和库
- [rules/profiling.md](rules/profiling.md) - 分析和基准测试工具
- [rules/logging.md](rules/logging.md) - 日志记录和调试模式
- [rules/environment.md](rules/environment.md) - 环境配置和密钥管理
- [rules/graceful-shutdown.md](rules/graceful-shutdown.md) - 优雅关闭和信号处理
- [rules/typescript.md](rules/typescript.md) - Node.js 中的 TypeScript 配置和类型剥离
