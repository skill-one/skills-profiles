Vitest 是一个由 Vite 驱动的下一代测试框架。它提供了与 Jest 兼容的 API，并内置原生 ESM、TypeScript 和 JSX 支持。Vitest 与您的 Vite 应用程序共享相同的配置、转换器、解析器和插件。

**主要特性：**

- Vite 原生：使用 Vite 的转换管道，实现类似 HMR 的快速测试更新
- Jest 兼容：可替换大多数 Jest 测试套件
- 智能监听模式：根据模块依赖图仅重新运行受影响的测试
- 无需配置的原生 ESM、TypeScript、JSX 支持
- 多线程工作线程，实现并行测试执行
- 通过 V8 或 Istanbul 内置代码覆盖率
- 快照测试、模拟和监视工具

> 本技能基于 Vitest 3.x 版本，生成于 2026-01-28。

## 核心

| 主题         | 描述                                                         | 参考                                    |
| ------------ | --------------------------------------------------------------- | -------------------------------------------- |
| 配置         | Vitest 和 Vite 配置集成，defineConfig 的使用                  | [core-config](references/core-config.md)     |
| CLI           | 命令行界面，命令和选项                                        | [core-cli](references/core-cli.md)           |
| 测试 API      | test/it 函数，skip、only、concurrent 等修饰符                 | [core-test-api](references/core-test-api.md) |
| Describe API  | describe/suite 用于分组测试和嵌套套件                         | [core-describe](references/core-describe.md) |
| Expect API    | 使用 toBe、toEqual、匹配器和非对称匹配器的断言                 | [core-expect](references/core-expect.md)     |
| 钩子         | beforeEach、afterEach、beforeAll、afterAll、aroundEach          | [core-hooks](references/core-hooks.md)       |

## 特性

| 主题        | 描述                                                         | 参考                                                  |
| ------------ | -------------------------------------------------------------- | ---------------------------------------------------------- |
| 模拟      | 使用 vi 工具模拟函数、模块、计时器和日期                     | [features-mocking](references/features-mocking.md)         |
| 快照    | 使用 toMatchSnapshot 和内联快照进行快照测试                   | [features-snapshots](references/features-snapshots.md)     |
| 覆盖率     | 使用 V8 或 Istanbul 提供商的代码覆盖率                       | [features-coverage](references/features-coverage.md)       |
| 测试上下文 | 测试固定装置，context.expect，test.extend 用于自定义固定装置 | [features-context](references/features-context.md)         |
| 并发  | 并发测试，并行执行，分片                                   | [features-concurrency](references/features-concurrency.md) |
| 过滤    | 按名称、文件模式、标签过滤测试                               | [features-filtering](references/features-filtering.md)     |

## 高级

| 主题        | 描述                                             | 参考                                                    |
| ------------ | ------------------------------------------------------- | ------------------------------------------------------------ |
| Vi 工具 | vi 辅助工具：mock、spyOn、伪造计时器、hoisted、waitFor   | [advanced-vi](references/advanced-vi.md)                     |
| 环境 | 测试环境：node、jsdom、happy-dom、自定义               | [advanced-environments](references/advanced-environments.md) |
| 类型测试 | 使用 expectTypeOf 和 assertType 进行类型级测试     | [advanced-type-testing](references/advanced-type-testing.md) |
| 项目     | 多项目工作区，每个项目使用不同的配置                 | [advanced-projects](references/advanced-projects.md)         |
