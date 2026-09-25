# Vitest 最佳实践

Vitest 测试框架的全面性能优化和最佳实践指南。包含 8 个类别中的 44 条规则，按影响程度排序，以指导测试编写、重构和代码审查。

## 应用场景

在以下情况下参考这些指南：
- 编写新的 Vitest 测试
- 调试不稳定或缓慢的测试
- 配置测试设置
- 审查 PR 中的测试代码
- 从 Jest 迁移到 Vitest
- 优化 CI/CD 测试性能

## 按优先级排序的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 异步模式 | CRITICAL | `async-` |
| 2 | 测试设置与隔离 | CRITICAL | `setup-` |
| 3 | 模拟模式 | HIGH | `mock-` |
| 4 | 性能 | HIGH | `perf-` |
| 5 | 快照测试 | MEDIUM | `snap-` |
| 6 | 环境 | MEDIUM | `env-` |
| 7 | 断言 | LOW-MEDIUM | `assert-` |
| 8 | 测试组织 | LOW | `org-` |

## 快速参考

### 1. 异步模式 (CRITICAL)

- `async-await-assertions` - 等待异步断言以防止误报
- `async-return-promises` - 从测试函数返回 Promise
- `async-fake-timers` - 使用假计时器处理依赖时间的代码
- `async-waitfor-polling` - 使用 `vi.waitFor` 处理异步条件
- `async-concurrent-expect` - 在并发测试中使用测试上下文 expect
- `async-act-wrapper` - 等待用户事件以避免 act 警告
- `async-error-handling` - 正确测试异步错误处理

### 2. 测试设置与隔离 (CRITICAL)

- `setup-beforeeach-cleanup` - 在 `afterEach` 钩子中清理状态
- `setup-restore-mocks` - 每个测试后恢复模拟
- `setup-avoid-shared-state` - 避免测试间共享可变状态
- `setup-beforeall-expensive` - 使用 `beforeAll` 进行昂贵的单次设置
- `setup-reset-modules` - 测试模块状态时重置模块
- `setup-test-factories` - 使用测试工厂处理复杂测试数据

### 3. 模拟模式 (HIGH)

- `mock-vi-mock-hoisting` - 理解 `vi.mock` 的提升行为
- `mock-spyon-vs-mock` - 合理选择 `vi.spyOn` 和 `vi.mock`
- `mock-implementation-not-value` - 使用 `mockImplementation` 处理动态模拟
- `mock-msw-network` - 使用 MSW 模拟网络请求
- `mock-avoid-overmocking` - 避免过度模拟
- `mock-type-safety` - 在模拟中保持类型安全
- `mock-clear-between-tests` - 测试间清除模拟状态

### 4. 性能 (HIGH)

- `perf-pool-selection` - 选择合适的池以提升性能
- `perf-disable-isolation` - 在安全时禁用测试隔离
- `perf-happy-dom` - 可能时使用 happy-dom 而非 jsdom
- `perf-sharding` - 使用分片进行 CI 并行化
- `perf-run-mode-ci` - 在 CI 环境中使用运行模式
- `perf-bail-fast-fail` - 在 CI 中使用 bail 快速失败

### 5. 快照测试 (MEDIUM)

- `snap-inline-over-file` - 小值优先使用内联快照
- `snap-avoid-large` - 避免大型快照
- `snap-stable-serialization` - 确保快照序列化稳定
- `snap-review-updates` - 提交前审查快照更新
- `snap-describe-intent` - 描述性地命名快照测试

### 6. 环境 (MEDIUM)

- `env-per-file-override` - 需要时按文件覆盖环境变量
- `env-setup-files` - 使用设置文件进行全局配置
- `env-globals-config` - 一致配置全局变量
- `env-browser-api-mocking` - 模拟测试环境中不可用的浏览器 API

### 7. 断言 (LOW-MEDIUM)

- `assert-specific-matchers` - 使用特定匹配器而非通用匹配器
- `assert-edge-cases` - 测试边界和特殊情况
- `assert-one-assertion-concept` - 每个测试测试一个概念
- `assert-expect-assertions` - 使用 `expect.assertions` 处理异步测试
- `assert-toequal-vs-tobe` - 正确选择 `toBe` 和 `toEqual`

### 8. 测试组织 (LOW)

- `org-file-colocation` - 测试文件与源文件放在一起
- `org-describe-nesting` - 使用 `describe` 块进行逻辑分组
- `org-test-naming` - 编写描述性的测试名称
- `org-test-skip-only` - 合理使用 `skip` 和 `only`

## 如何使用

查阅单独的参考文件获取详细说明和代码示例：

- [部分定义](references/_sections.md) - 类别结构和影响级别
- [规则模板](assets/templates/_template.md) - 添加新规则的模板
- [async-await-assertions](references/async-await-assertions.md) - 示例规则文件
- [mock-vi-mock-hoisting](references/mock-vi-mock-hoisting.md) - 示例规则文件

## 相关技能

- 关于 TDD 方法论，参考 `test-tdd` 技能
- 关于使用 MSW 模拟 API，参考 `test-msw` 技能
- 关于 TypeScript 测试模式，参考 `typescript` 技能

## 完整编译文档

获取包含所有规则展开的完整指南：`AGENTS.md`
