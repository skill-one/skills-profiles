# Zod 最佳实践

适用于 TypeScript 应用的 Zod 综合模式验证指南。包含 8 个类别中的 43 条规则，按影响程度优先级排序，以指导自动化重构和代码生成。

## 应用时机

在以下情况参考这些指南：
- 编写新的 Zod 模式
- 在 parse() 和 safeParse() 之间选择
- 使用 z.infer 实现类型推断
- 处理用于用户反馈的验证错误
- 组合复杂的对象模式
- 使用精炼和转换
- 优化包大小和验证性能
- 审查 Zod 代码以符合最佳实践

## 按优先级划分的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 模式定义 | 关键 | `schema-` |
| 2 | 解析与验证 | 关键 | `parse-` |
| 3 | 类型推断 | 高 | `type-` |
| 4 | 错误处理 | 高 | `error-` |
| 5 | 对象模式 | 中高 | `object-` |
| 6 | 模式组合 | 中 | `compose-` |
| 7 | 精炼与转换 | 中 | `refine-` |
| 8 | 性能与包 | 低中 | `perf-` |

## 快速参考

### 1. 模式定义 (关键)

- `schema-use-primitives-correctly` - 为每种类型使用正确的原始模式
- `schema-use-unknown-not-any` - 使用 z.unknown() 而不是 z.any() 以确保类型安全
- `schema-avoid-optional-abuse` - 避免过度使用可选字段
- `schema-string-validations` - 在模式定义时应用字符串验证
- `schema-use-enums` - 使用枚举表示固定字符串值
- `schema-coercion-for-form-data` - 使用强制转换处理表单和查询数据

### 2. 解析与验证 (关键)

- `parse-use-safeparse` - 使用 safeParse() 处理用户输入
- `parse-async-for-async-refinements` - 使用 parseAsync 处理异步精炼
- `parse-handle-all-issues` - 处理所有验证问题而不仅仅是第一个
- `parse-validate-early` - 在系统边界处验证
- `parse-avoid-double-validation` - 避免对同一数据重复验证
- `parse-never-trust-json` - 不要信任 JSON.parse 的输出

### 3. 类型推断 (高)

- `type-use-z-infer` - 使用 z.infer 而不是手动类型
- `type-input-vs-output` - 区分 z.input 和 z.infer 用于转换
- `type-export-schemas-and-types` - 同时导出模式和推断类型
- `type-branded-types` - 使用标记类型确保领域安全
- `type-enable-strict-mode` - 启用 TypeScript 严格模式

### 4. 错误处理 (高)

- `error-custom-messages` - 提供自定义错误消息
- `error-use-flatten` - 使用 flatten() 处理表单错误显示
- `error-path-for-nested` - 使用 issue.path 处理嵌套错误位置
- `error-i18n` - 实现国际化错误消息
- `error-avoid-throwing-in-refine` - 在 refine 中返回 false 而不是抛出错误

### 5. 对象模式 (中高)

- `object-strict-vs-strip` - 在未知键上选择 strict() 或 strip()
- `object-partial-for-updates` - 使用 partial() 处理更新模式
- `object-pick-omit` - 使用 pick() 和 omit() 处理模式变体
- `object-extend-for-composition` - 使用 extend() 添加字段
- `object-optional-vs-nullable` - 区分 optional() 和 nullable()
- `object-discriminated-unions` - 使用区分联合来缩小类型

### 6. 模式组合 (中)

- `compose-shared-schemas` - 将共享模式提取为可重用模块
- `compose-intersection` - 使用 intersection() 处理类型组合
- `compose-lazy-recursive` - 使用 z.lazy() 处理递归模式
- `compose-preprocess` - 使用 preprocess() 处理数据标准化
- `compose-pipe` - 使用 pipe() 处理多阶段验证

### 7. 精炼与转换 (中)

- `refine-vs-superrefine` - 正确选择 refine() 和 superRefine()
- `refine-transform-coerce` - 区分 transform()、refine() 和 coerce()
- `refine-add-path` - 为精炼错误添加路径
- `refine-defaults` - 使用 default() 为可选字段提供默认值
- `refine-catch` - 使用 catch() 实现容错解析

### 8. 性能与包 (低中)

- `perf-cache-schemas` - 缓存模式实例
- `perf-zod-mini` - 在包敏感应用中使用 Zod Mini
- `perf-avoid-dynamic-creation` - 避免在热点路径动态创建模式
- `perf-lazy-loading` - 懒加载大型模式
- `perf-arrays` - 优化大型数组验证

## 如何使用

查阅单独的参考文件获取详细说明和代码示例：

- [部分定义](references/_sections.md) - 类别结构和影响级别
- [规则模板](assets/templates/_template.md) - 添加新规则的模板
- 单独规则：`references/{前缀}-{缩写}.md`

## 完整编译文档

包含所有规则展开的完整指南：`AGENTS.md`

## 相关技能

- 对于 React Hook Form 集成，参考 `react-hook-form` 技能
- 对于 API 客户端生成，参考 `orval` 技能

## 来源

- [Zod 官方文档](https://zod.dev/)
- [Zod v4 发布说明](https://zod.dev/v4)
- [Zod GitHub 仓库](https://github.com/colinhacks/zod)
- [Zod Mini](https://zod.dev/packages/mini)
- [Total TypeScript Zod 教程](https://www.totaltypescript.com/tutorials/zod)
