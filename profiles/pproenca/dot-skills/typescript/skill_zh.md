# TypeScript 最佳实践

TypeScript 应用程序的全面性能优化指南。包含 8 个类别中的 45 条规则，按影响程度排序，以指导自动化重构和代码生成。

## 应用时机

在以下情况下参考这些指南：
- 配置新项目或现有项目的 tsconfig.json
- 编写复杂的类型定义或泛型
- 优化 async/await 模式和数据获取
- 组织模块和管理导入
- 审查代码以进行编译或运行时性能分析

## 按优先级划分的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 类型系统性能 | 关键 | `type-` |
| 2 | 编译器配置 | 关键 | `tscfg-` |
| 3 | 异步模式 | 高 | `async-` |
| 4 | 模块组织 | 高 | `module-` |
| 5 | 类型安全模式 | 中高 | `safety-` |
| 6 | 内存管理 | 中 | `mem-` |
| 7 | 运行时优化 | 低中 | `runtime-` |
| 8 | 高级模式 | 低 | `advanced-` |

## 目录

1. [类型系统性能](references/_sections.md#1-type-system-performance) — **关键**
   - 1.1 [为导出的函数添加显式返回类型](references/type-explicit-return-types.md) — 关键 (声明 emit 速度提升 30-50%)
   - 1.2 [避免深层嵌套的泛型类型](references/type-avoid-deep-generics.md) — 关键 (防止指数级实例化成本)
   - 1.3 [避免大型联合类型](references/type-avoid-large-unions.md) — 关键 (二次 O(n²) 比较成本)
   - 1.4 [将条件类型提取到命名别名](references/type-extract-conditional-types.md) — 关键 (启用编译器缓存，防止重新评估)
   - 1.5 [限制类型递归深度](references/type-limit-recursion-depth.md) — 高 (适用时防止指数类型扩展)
   - 1.6 [优先使用接口而非类型交集](references/type-interfaces-over-intersections.md) — 关键 (类型解析速度提升 2-5 倍)
   - 1.7 [简化复杂映射类型](references/type-simplify-mapped-types.md) — 高 (适用时类型计算减少 50-80%)
2. [编译器配置](references/_sections.md#2-compiler-configuration) — **关键**
   - 2.1 [正确配置 include 和 exclude](references/tscfg-exclude-properly.md) — 关键 (防止扫描数千个不必要的文件)
   - 2.2 [启用增量编译](references/tscfg-enable-incremental.md) — 关键 (重建速度提升 50-90%)
   - 2.3 [为并行声明 emit 启用 isolatedDeclarations](references/tscfg-isolated-declarations.md) — 关键 (无需类型检查器即可并行生成 .d.ts)
   - 2.4 [为更快构建启用 skipLibCheck](references/tscfg-skip-lib-check.md) — 关键 (编译速度提升 20-40%)
   - 2.5 [为更快变体检查启用 strictFunctionTypes](references/tscfg-strict-function-types.md) — 关键 (启用优化的变体检查)
   - 2.6 [为 Node.js 原生 TypeScript 仅使用 erasableSyntaxOnly](references/tscfg-erasable-syntax-only.md) — 高 (防止 100% 的 Node.js 类型剥离运行时错误)
   - 2.7 [为单文件转译使用 isolatedModules](references/tscfg-isolate-modules.md) — 关键 (使用打包器时转译速度提升 80-90%)
   - 2.8 [为大型代码库使用项目引用](references/tscfg-project-references.md) — 关键 (增量构建速度提升 60-80%)
3. [异步模式](references/_sections.md#3-async-patterns) — **高**
   - 3.1 [为异步函数标注返回类型](references/async-explicit-return-types.md) — 高 (防止运行时错误，改进推断)
   - 3.2 [避免在循环中 await](references/async-avoid-loop-await.md) — 高 (N 次迭代 N 倍速度提升，10 个用户 = 10 倍改进)
   - 3.3 [避免不必要的 async/await](references/async-avoid-unnecessary-async.md) — 高 (消除琐碎的 Promise 包装并改进堆栈跟踪)
   - 3.4 [直到需要值时才 defer await](references/async-defer-await.md) — 高 (启用隐式并行化)
   - 3.5 [为独立操作使用 Promise.all](references/async-parallel-promises.md) — 高 (I/O 密集型代码改进 2-10 倍)
4. [模块组织](references/_sections.md#4-module-organization) — **高**
   - 4.1 [避免使用桶文件导入](references/module-avoid-barrel-imports.md) — 高 (导入成本 200-800ms，bundle 大小增加 30-50%)
   - 4.2 [避免循环依赖](references/module-avoid-circular-dependencies.md) — 高 (防止运行时未定义错误和编译缓慢)
   - 4.3 [控制 @types 包的包含](references/module-control-types-inclusion.md) — 高 (防止类型冲突并减少内存使用)
   - 4.4 [为大型模块使用动态导入](references/module-dynamic-imports.md) — 高 (初始 bundle 减少幅度 30-70%)
   - 4.5 [为类型使用类型仅导入](references/module-use-type-imports.md) — 高 (消除类型信息的运行时导入)
5. [类型安全模式](references/_sections.md#5-type-safety-patterns) — **中高**
   - 5.1 [启用 noUncheckedIndexedAccess](references/safety-no-unchecked-indexed-access.md) — 中高 (在编译时防止 100% 的未检查索引访问错误)
   - 5.2 [启用 strictNullChecks](references/safety-strict-null-checks.md) — 中高 (防止 null/undefined 运行时错误)
   - 5.3 [优先使用 unknown 而非 any](references/safety-prefer-unknown-over-any.md) — 中高 (强制类型缩小，防止运行时错误)
   - 5.4 [使用断言函数进行验证](references/safety-assertion-functions.md) — 中高 (验证样板代码减少 50-70%)
   - 5.5 [为字面量类型使用 const 断言](references/safety-const-assertions.md) — 中高 (保留字面量类型，启用更好的推断)
   - 5.6 [为联合类型使用穷尽检查](references/safety-exhaustive-checks.md) — 中高 (在编译时防止 100% 的遗漏案例错误)
   - 5.7 [使用类型守卫进行运行时类型检查](references/safety-use-type-guards.md) — 中高 (消除类型断言，在边界处捕获错误)
6. [内存管理](references/_sections.md#6-memory-management) — **中**
   - 6.1 [避免闭包内存泄漏](references/mem-avoid-closure-leaks.md) — 中 (防止长生命回调中的保留引用)
   - 6.2 [避免全局状态累积](references/mem-avoid-global-state.md) — 中 (防止无界内存增长)
   - 6.3 [清理事件监听器](references/mem-cleanup-event-listeners.md) — 中 (防止无界内存增长)
   - 6.4 [清除计时器和间隔](references/mem-clear-timers.md) — 中 (防止回调保留和重复执行)
   - 6.5 [使用 WeakMap 存储对象元数据](references/mem-use-weakmap-for-metadata.md) — 中 (防止内存泄漏，启用自动清理)
7. [运行时优化](references/_sections.md#7-runtime-optimization) — **低中**
   - 7.1 [在热循环中避免对象展开](references/runtime-avoid-object-spread-in-loops.md) — 低中 (减少 N 倍对象分配)
   - 7.2 [在循环中缓存属性访问](references/runtime-cache-property-access.md) — 低中 (在热路径中减少 N 倍属性查找)
   - 7.3 [优先使用原生数组方法而非 Lodash](references/runtime-prefer-array-methods.md) — 低中 (消除库开销，支持 tree-shaking)
   - 7.4 [使用 for-of 进行简单迭代](references/runtime-use-for-of-for-iteration.md) — 低中 (减少 30-50% 迭代样板代码)
   - 7.5 [使用现代字符串方法](references/runtime-use-string-methods.md) — 低中 (简单模式比正则快 2-5 倍)
   - 7.6 [使用 Set/Map 进行 O(1) 查找](references/runtime-use-set-for-lookups.md) — 低中 (每次查找从 O(n) 到 O(1))
8. [高级模式](references/_sections.md#8-advanced-patterns) — **低**
   - 8.1 [使用标记类型进行类型安全的 ID](references/advanced-branded-types.md) — 低 (防止混合不兼容的 ID 类型)
   - 8.2 [使用 satisfies 进行带推断的类型验证](references/advanced-satisfies-operator.md) — 低 (防止属性访问错误，实现 100% 自动补全精度)
   - 8.3 [使用模板字面量类型进行字符串模式](references/advanced-template-literal-types.md) — 低 (在编译时防止 100% 的字符串格式错误)

## 参考

1. [https://github.com/microsoft/TypeScript/wiki/Performance](https://github.com/microsoft/TypeScript/wiki/Performance)
2. [https://www.typescriptlang.org/docs/handbook/](https://www.typescriptlang.org/docs/handbook/)
3. [https://v8.dev/blog](https://v8.dev/blog)
4. [https://nodejs.org/en/learn/diagnostics/memory](https://nodejs.org/en/learn/diagnostics/memory)
