# Rstest 最佳实践

在设置、编写或审查 Rstest 项目时，请遵循这些规则。

## 工作流程

- 在编辑前，检查现有的包管理器、依赖策略、模块模式、构建配置、测试布局和框架约定。
- 添加 `@rstest/core`，一个包本地的测试脚本，以及一个扩展名与包的模块模式匹配的配置文件。
- 仅当这样做降低维护成本且保持兼容性时，才重用现有的构建配置。适配器是可选的；当适配器集成不兼容或成本不成比例时，使用独立的 Rstest 配置，并明确重现已需要的别名、插件、定义、环境和外部依赖。
- 故意配置测试发现、环境和设置文件。除非空测试集是一个预期和记录的状态，否则不要启用 `passWithNoTests`。
- 使用 `rstest list` 验证测试发现，然后运行聚焦测试、完整套件以及项目现有的构建或类型检查命令。

## 配置和环境

- 使用 `@rstest/core` 中的 `defineConfig` 和与包的模块模式兼容的配置文件扩展名。
- 优先选择从 `@rstest/core` 的显式导入，而不是 `globals: true`。
- 使用 `setupFiles` 用于共享匹配器和清理；使用 `plugins`、`resolve` 或 `source` 仅在必要时用于普通构建集成和低级 `tools`。
- 当包的测试布局是非标准时，显式设置 `include`；不要假设默认的发现模式。
- 使用 `node` 用于服务器/SSR 测试，`happy-dom` 或 `jsdom` 用于模拟 DOM 测试，以及浏览器模式用于真实浏览器行为；显式安装选定的环境包。
- 对于 React 或 Vue 组件测试，注册匹配的构建插件，使用相应的 Testing Library，并在设置文件中集中匹配器扩展和清理。
- 仅当环境或配置确实不同时，才使用多个测试项目；将全局选项（如报告器、覆盖率、池、隔离和 bail）保持在根目录。

## 测试编写

- 优先选择验证一个公共行为的较小测试；有意使用 `.skip` 或 `.todo`，并永远不要提交 `.only`。
- 将测试 API 和测试文件保持在与项目相同的模块系统中；不要在没有验证运行时和打包器行为的情况下混合 ESM/CJS 假设。
- 优先选择 `await expect(promise).resolves...` 和 `.rejects...`，而不是可能遗漏断言的 `try/catch` 模式。
- 仅用于小工具使用 `includeSource`，用 `import.meta.rstest` 保护和生产构建中将它定义为 `false`。

## Mocking

- 使用 `rs.fn()` 用于函数，`rs.spyOn()` 用于对象方法，以及 `rs.mock()` 工厂用于模块；模拟外部边界，而不是测试主题。
- 根据（在测试之间）是否需要恢复调用、实现或原始方法，选择 `clearMocks`、`resetMocks` 或 `restoreMocks`。
- 选择与模块系统匹配的模块模拟 API；在评估测试模块之前，验证确切请求字符串并注册提升的/静态模拟。
- 模块模拟替换运行时行为，但并不一定从 Rspack 构建图中移除真实依赖。仅当构建仍然遍历不想要的或不可用的依赖时，才使用别名或范围狭小的外部依赖，并验证运行时外部化格式。

## Snapshots 和 coverage

- 保持快照小且确定性：使用内联快照用于短输出，文件快照用于大结构化输出，使用序列化器用于路径或不稳定数据。审查每个更新。
- 使用 `--coverage` 或 `coverage.enabled` 启用覆盖率。
- 选择安装的 Rstest 版本支持的覆盖率提供程序，并显式添加其包；不要在不检查项目需求的情况下复制 V8 或 Istanbul 提供程序选择。
- 在添加阈值之前故意设置 `coverage.include`；为人类和 CI 工件分别选择报告器。

## 运行和 CI

- 使用 `rstest` 进行单次运行；`rstest run` 是一个可选的显式等效项。仅用于本地开发使用 `rstest --watch` 或 `rstest watch`。
- 使用 `rstest list` 验证发现，使用位置过滤器或 `-t` 进行聚焦运行，使用 `-u` 进行有意快照更新，使用 `-c` 进行非默认配置。
- 在 CI 中，永远不要使用监视模式。当分发测试时使用分片和 blob 报告以及 `rstest merge-reports`；当 CI 系统需要机器可读结果时使用 JUnit。
- 如果通过测试日志太嘈杂，可以考虑 `silent: 'passed-only'`；在诊断设置或运行时输出时暂时禁用它。

## First-line debugging

- 从聚焦的可复现和 `--reporter=verbose` 开始；使用 `--printConsoleTrace` 用于嘈杂或不清晰的控制台输出。
- 使用 `DEBUG=rstest` 并检查 `dist/.rstest-temp/.rsbuild/` 以验证最终的 Rstest/Rsbuild/Rspack 配置和生成的构建输出。
- 使用 Rstest VS Code 扩展或 JavaScript 调试终端使用断点进行运行时失败。
- 使用 `rstest-debugging` 进行系统性的启动、构建、运行时、日志记录、内存或性能诊断。

## 文档

- 要获取最新的 Rstest 文档，请阅读 https://rstest.rs/llms.txt
