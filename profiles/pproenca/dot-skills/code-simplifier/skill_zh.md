# 社区代码简化最佳实践

面向AI代理和大型语言模型的全面代码简化指南。包含8个类别中的47条规则，按影响程度从关键（上下文发现、行为保留）到渐进式（语言惯用法）进行优先级排序。每条规则都包含详细说明、对比错误与正确实现的现实世界示例以及具体影响指标。

## 核心原则

1. **先理解上下文**：在做出任何更改前，先理解项目规范
2. **保留行为**：改变代码的写法，绝不改变其功能
3. **范围纪律**：专注于最近修改的代码，保持差异小
4. **清晰优先于简洁**：明确、可读的代码优于巧妙的单行代码

## 适用场景

在以下情况参考这些指南：
- 简化或清理最近修改的代码
- 减少嵌套、复杂度或重复
- 改进命名和可读性
- 应用特定语言的惯用法
- 审查代码以发现可维护性问题

## 按优先级划分的规则类别

| 优先级 | 类别 | 影响 | 前缀 | 规则数量 |
|--------|------|------|------|----------|
| 1 | 上下文发现 | 关键 | `ctx-` | 4 |
| 2 | 行为保留 | 关键 | `behave-` | 6 |
| 3 | 范围管理 | 高 | `scope-` | 5 |
| 4 | 控制流简化 | 高 | `flow-` | 9 |
| 5 | 命名与清晰度 | 中高 | `name-` | 6 |
| 6 | 重复减少 | 中 | `dup-` | 5 |
| 7 | 废弃代码消除 | 中 | `dead-` | 5 |
| 8 | 语言惯用法 | 低中 | `idiom-` | 7 |

## 快速参考

### 1. 上下文发现（关键）

- [`ctx-read-claude-md`](references/ctx-read-claude-md.md) - 简化前必须始终阅读CLAUDE.md
- [`ctx-detect-lint-config`](references/ctx-detect-lint-config.md) - 检查代码检查和格式化配置
- [`ctx-follow-existing-patterns`](references/ctx-follow-existing-patterns.md) - 在文件和项目中匹配现有代码风格
- [`ctx-project-over-generic`](references/ctx-project-over-generic.md) - 项目规范优先于通用最佳实践

### 2. 行为保留（关键）

- [`behave-preserve-outputs`](references/behave-preserve-outputs.md) - 保留所有返回值和输出
- [`behave-preserve-errors`](references/behave-preserve-errors.md) - 保留错误消息、类型和处理方式
- [`behave-preserve-api`](references/behave-preserve-api.md) - 保留公共函数签名和类型
- [`behave-preserve-side-effects`](references/behave-preserve-side-effects.md) - 保留副作用（日志记录、I/O、状态变更）
- [`behave-no-semantics-change`](references/behave-no-semantics-change.md) - 禁止细微的语义变更
- [`behave-verify-before-commit`](references/behave-verify-before-commit.md) - 在最终确定前验证行为保留

### 3. 范围管理（高）

- [`scope-recent-code-only`](references/scope-recent-code-only.md) - 仅关注最近修改的代码
- [`scope-minimal-diff`](references/scope-minimal-diff.md) - 保持更改小且易于审查
- [`scope-no-unrelated-refactors`](references/scope-no-unrelated-refactors.md) - 不进行无关的重构
- [`scope-no-global-rewrites`](references/scope-no-global-rewrites.md) - 避免全局重写和架构变更
- [`scope-respect-boundaries`](references/scope-respect-boundaries.md) - 尊重模块和组件边界

### 4. 控制流简化（高）

- [`flow-early-return`](references/flow-early-return.md) - 使用提前返回减少嵌套
- [`flow-guard-clauses`](references/flow-guard-clauses.md) - 使用守卫语句进行前置条件检查
- [`flow-no-nested-ternaries`](references/flow-no-nested-ternaries.md) - 绝不使用嵌套的三元运算符
- [`flow-explicit-over-dense`](references/flow-explicit-over-dense.md) - 优先使用显式控制流而非密集表达式
- [`flow-flatten-nesting`](references/flow-flatten-nesting.md) - 将深层嵌套展平至最多2-3层
- [`flow-single-responsibility`](references/flow-single-responsibility.md) - 每个代码块只做一件事
- [`flow-positive-conditions`](references/flow-positive-conditions.md) - 优先使用正向条件而非双重否定
- [`flow-optional-chaining`](references/flow-optional-chaining.md) - 使用可选链和空值合并运算符
- [`flow-boolean-simplification`](references/flow-boolean-simplification.md) - 简化布尔表达式

### 5. 命名与清晰度（中高）

- [`name-intention-revealing`](references/name-intention-revealing.md) - 使用意图明确的命名
- [`name-nouns-for-data`](references/name-nouns-for-data.md) - 数据使用名词，动作使用动词
- [`name-avoid-abbreviations`](references/name-avoid-abbreviations.md) - 避免晦涩的缩写
- [`name-consistent-vocabulary`](references/name-consistent-vocabulary.md) - 全程使用一致的词汇
- [`name-avoid-generic`](references/name-avoid-generic.md) - 避免通用名称
- [`name-string-interpolation`](references/name-string-interpolation.md) - 优先使用字符串插值而非连接

### 6. 重复减少（中）

- [`dup-rule-of-three`](references/dup-rule-of-three.md) - 应用三重规则
- [`dup-no-single-use-helpers`](references/dup-no-single-use-helpers.md) - 避免单次使用的辅助函数
- [`dup-extract-for-clarity`](references/dup-extract-for-clarity.md) - 仅在提升清晰度时提取
- [`dup-avoid-over-abstraction`](references/dup-avoid-over-abstraction.md) - 优先重复而非过早抽象
- [`dup-data-driven`](references/dup-data-driven.md) - 使用数据驱动模式而非重复条件判断

### 7. 废弃代码消除（中）

- [`dead-remove-unused`](references/dead-remove-unused.md) - 删除未使用的代码片段
- [`dead-delete-not-comment`](references/dead-delete-not-comment.md) - 删除代码而非注释掉
- [`dead-remove-obvious-comments`](references/dead-remove-obvious-comments.md) - 删除陈述明显的注释
- [`dead-keep-why-comments`](references/dead-keep-why-comments.md) - 保留解释原因的注释
- [`dead-remove-todo-fixme`](references/dead-remove-todo-fixme.md) - 删除过时的TODO/FIXME注释

### 8. 语言惯用法（低中）

- [`idiom-ts-strict-types`](references/idiom-ts-strict-types.md) - TypeScript中使用严格类型而非any
- [`idiom-ts-const-assertions`](references/idiom-ts-const-assertions.md) - TypeScript使用const断言和readonly
- [`idiom-rust-question-mark`](references/idiom-rust-question-mark.md) - Rust中使用?进行错误传播
- [`idiom-rust-iterator-chains`](references/idiom-rust-iterator-chains.md) - Rust中在更清晰时使用迭代器链
- [`idiom-python-comprehensions`](references/idiom-python-comprehensions.md) - Python中使用列表/集合推导式进行简单转换
- [`idiom-go-error-handling`](references/idiom-go-error-handling.md) - Go中立即处理错误
- [`idiom-prefer-language-builtins`](references/idiom-prefer-language-builtins.md) - 优先使用语言和标准库内置功能

## 工作流程

1. **发现上下文**：阅读CLAUDE.md、代码检查配置、检查现有模式
2. **确定范围**：除非要求扩展，否则专注于最近修改的代码
3. **应用转换**：按优先级顺序（关键优先）使用规则
4. **验证行为**：确保输出、错误和副作用保持完全一致
5. **保持差异最小**：小范围、聚焦的变更，易于审查

## 如何使用

查阅单个参考文件获取详细说明和代码示例：

- [章节定义](references/_sections.md) - 类别结构和影响等级
- [规则模板](assets/templates/_template.md) - 添加新规则的模板

## 参考文件

| 文件 | 描述 |
|------|------|
| [references/_sections.md](references/_sections.md) | 类别定义和排序 |
| [assets/templates/_template.md](assets/templates/_template.md) | 新规则的模板 |
| [metadata.json](metadata.json) | 版本和参考信息 |
