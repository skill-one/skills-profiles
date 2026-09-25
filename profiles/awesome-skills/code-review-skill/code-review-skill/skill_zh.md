# 代码审查技巧

通过建设性反馈、系统分析和协作改进，将代码审查从守门转变为知识共享。

## 使用此技巧的场景

- 审查拉取请求和代码变更
- 为团队建立代码审查标准
- 通过审查指导初级开发者
- 进行架构审查
- 创建审查清单和指南
- 提升团队协作
- 缩短代码审查周期
- 维持代码质量标准

## 核心原则

### 1. 审查心态

**代码审查的目标：**
- 发现错误和边界情况
- 确保代码可维护性
- 跨团队共享知识
- 强制执行编码标准
- 改进设计和架构
- 建立团队文化

**不是目标：**
- 展示知识
- 吹毛求疵格式（使用代码格式化工具）
- 不必要的阻碍进度
- 按自己的喜好重写

### 2. 高效的反馈

**好的反馈应该是：**
- 具体且可操作
- 教育性而非评判性
- 聚焦于代码而非个人
- 平衡（也要表扬好的工作）
- 优先级（关键问题与锦上添花）

```markdown
❌ 差： "这是错的。"
✅ 好： "当多个用户同时访问时，这可能导致竞态条件。这里考虑使用互斥锁。"

❌ 差： "你为什么不用X模式？"
✅ 好： "你考虑过仓库模式吗？这将使测试更容易。这里有一个示例：[链接]"

❌ 差： "重命名这个变量。"
✅ 好： "[小问题] 考虑使用`userCount`代替`uc`以提高清晰度。如果不介意，可以继续使用。"
```

### 3. 审查范围

**需要审查的内容：**
- 逻辑正确性和边界情况
- 安全漏洞
- 性能影响
- 测试覆盖和质量
- 错误处理
- 文档和注释
- API设计和命名
- 架构适配性

**无需手动审查的内容：**
- 代码格式（使用Prettier、Black等）
- 导入组织
- 代码检查警告
- 简单拼写错误

## 审查流程

### 第一阶段：背景收集（2-3分钟）

在深入代码前，了解：
1. 阅读拉取请求描述和关联问题
2. 检查拉取请求大小（>400行？要求拆分）
3. 审查CI/CD状态（测试通过吗？）
4. 理解业务需求
5. 记录任何相关的架构决策

> 对于大差异，通过[`scripts/pr-analyzer.py`](scripts/pr-analyzer.py) (`git diff main...HEAD | python scripts/pr-analyzer.py`) 将差异传递给分析器，在阅读前进行复杂度分类并获取建议的审查方法。

### 第二阶段：高层审查（5-10分钟）

1. **架构与设计** - 解决方案是否适合问题？
   - 对于重大变更，参考[架构审查指南](reference/architecture-review-guide.md)
   - 检查：SOLID原则、耦合/内聚、反模式
2. **性能评估** - 是否存在性能问题？
   - 对于性能关键代码，参考[性能审查指南](reference/performance-review-guide.md)
   - 检查：算法复杂度、N+1查询、内存使用
3. **文件组织** - 新文件是否放在正确位置？
4. **测试策略** - 是否有测试覆盖边界情况？

### 第三阶段：逐行审查（10-20分钟）

对每个文件检查：
- **逻辑与正确性** - 边界情况、计算错误、空值检查、竞态条件
- **安全** - 输入验证、注入风险、XSS、敏感数据
- **性能** - N+1查询、不必要的循环、内存泄漏
- **可维护性** - 清晰命名、单一职责、注释
- **复用** - 在接受新代码前，搜索可替代现有工具/辅助函数的代码。检查相邻文件和共享模块中的类似模式。参考[通用质量指南](reference/code-quality-universal.md)了解参数蔓延、泄漏抽象、嵌套条件、字符串类型代码、TOCTOU和无操作更新等反模式。

### 第四阶段：总结与决策（2-3分钟）

1. 总结关键问题
2. 突出优点
3. 做出明确决策：
   - ✅ 批准
   - 💬 评论（小建议）
   - 🔄 要求修改（必须解决）
4. 如有复杂问题，提供结对编程支持

## 审查技巧

### 技巧1：清单法

使用清单进行一致审查。参考[安全审查指南](reference/security-review-guide.md)获取全面的安全清单。

### 技巧2：提问法

不要直接指出问题，而是提问：

```markdown
❌ "如果列表为空就会失败。"
✅ "如果`items`是空数组会怎样？"

❌ "这里需要错误处理。"
✅ "如果API调用失败应该如何处理？"
```

### 技巧3：建议而非命令

使用协作性语言：

```markdown
❌ "你必须改为使用async/await"
✅ "建议：async/await可能使代码更易读。你觉得呢？"

❌ "提取这段逻辑到函数中"
✅ "这段逻辑出现在3处。提取它有意义吗？"
```

### 技巧4：区分严重性

使用标签表示优先级：

- 🔴 `[blocking]` - 必须解决才能合并
- 🟡 `[important]` - 应该解决，如有分歧可讨论
- 🟢 `[nit]` - 可选，不阻塞
- 💡 `[suggestion]` - 值得考虑的替代方案
- 📚 `[learning]` - 教育性评论，无需行动
- 🎉 `[praise]` - 做得好，继续保持！

**严重性级别：** 🔴 / 🟡 / 🟢 是本技巧中所有指南使用的三个严重性级别——🔴阻止合并，🟡应解决，🟢可选。其余标记（💡 / 📚 / 🎉）是非阻塞注释。

## 语言特定指南

根据审查的代码语言，查阅对应的详细指南：

| 语言/框架 | 参考文件 | 关键主题 |
|----------|----------|----------|
| **React** | [React Guide](reference/react.md) | Hooks, useEffect, React 19 Actions, RSC, Suspense, TanStack Query v5 |
| **Vue 3** | [Vue Guide](reference/vue.md) | Composition API, 响应性系统, Props/Emits, Watchers, Composables |
| **Angular 17+** | [Angular Guide](reference/angular.md) | Signals, Standalone, RxJS, Zoneless, 模板优化, 测试, 路由守卫, HttpInterceptor |
| **Rust** | [Rust Guide](reference/rust.md) | 所有权/借用, Unsafe 审查, 异步代码, 取消安全性, 错误处理 |
| **TypeScript** | [TypeScript Guide](reference/typescript.md) | 类型安全, async/await, 不可变性, 测试, 模块解析, TS 5.x |
| **Python** | [Python Guide](reference/python.md) | 可变默认参数, 异常处理, 类属性 |
| **Django / DRF** | [Django Guide](reference/django.md) | 安全审查, N+1 查询, Serializer 反模式, ViewSet, 异步视图 |
| **FastAPI** | [FastAPI Guide](reference/fastapi.md) | Depends, Pydantic v2 validation, async correctness, sessions/N+1, auth vs authorization, test-driven verification |
| **Java** | [Java Guide](reference/java.md) | Java 17/21 新特性, Spring Boot 3, 虚拟线程, Stream/Optional |
| **Java 8 / Legacy** | [Java 8 Guide](reference/java8.md) | Java 8, Spring Boot 2, javax.*, Stream/Optional, java.time, CompletableFuture |
| **PHP** | [PHP Guide](reference/php.md) | PHP 8.x type system, PDO, security review, Composer, PHPUnit/PHPStan |
| **Ruby / Rails** | [Ruby Guide](reference/ruby.md) | Ruby 语义, Rails 8, Active Record, Active Job, 安全, 测试 |
| **C# / .NET** | [C# Guide](reference/csharp.md) | C# 12 特性, 异步编程, EF Core 性能, ASP.NET Core, LINQ |
| **Go** | [Go Guide](reference/go.md) | 错误处理, goroutine/channel, context, 接口设计 |
| **Kotlin / Android** | [Kotlin Guide](reference/kotlin.md) | 协程, Flow, Jetpack Compose, 空安全, 内存泄漏, 架构模式 |
| **Swift / SwiftUI** | [Swift Guide](reference/swift.md) | Optionals, Swift Concurrency, Sendable/actors, SwiftUI property wrappers, 值类型与引用类型, API设计 |
| **Dart / Flutter** | [Dart Guide](reference/dart.md) | Widget rebuilds, const constructors, null safety, isolates, async in build, Riverpod/Bloc, platform channels, keys, disposal |
| **NestJS** | [NestJS Guide](reference/nestjs.md) | 依赖注入, 分层架构, DTO 验证, Guard/Interceptor, 循环依赖 |
| **Svelte / SvelteKit** | [Svelte Guide](reference/svelte.md) | Runes, Load 函数, Form Actions, Store 迁移, SSR/CSR 边界 |
| **C** | [C Guide](reference/c.md) | 指针/缓冲区, 内存安全, UB, 安全编码, 可移植性, 测试 |
| **C++** | [C++ Guide](reference/cpp.md) | RAII, 智能指针, C++20/23, constexpr, 测试 |
| **Zig** | [Zig Guide](reference/zig.md) | Allocators, error unions, defer/errdefer, comptime, C interop |
| **CSS/Less/Sass** | [CSS Guide](reference/css-less-sass.md) | 变量规范, !important, 性能优化, 响应式, 兼容性 |
| **Qt** | [Qt Guide](reference/qt.md) | 对象模型, 信号/槽, Model/View, QML, Qt6 迁移, 测试 |

## 跨领域指南

适用于所有代码审查的语言无关模式：

| 主题 | 参考文件 | 关键主题 |
|------|----------|----------|
| **架构审查** | [架构审查指南](reference/architecture-review-guide.md) | SOLID, 反模式, 耦合/内聚, 依赖方向 |
| **性能审查** | [性能审查指南](reference/performance-review-guide.md) | Web Vitals, N+1, 算法复杂度, 内存泄漏, 缓存 |
| **安全审查** | [安全审查指南](reference/security-review-guide.md) | SQLi, XSS, CSRF, SSRF, IDOR, 命令注入, 跨语言示例 |
| **通用质量** | [通用质量指南](reference/code-quality-universal.md) | 复用审计, 参数蔓延, 泄漏抽象, 嵌套条件, 字符串类型代码, TOCTOU, 无操作更新, 冗余状态 |
| **常见错误** | [常见错误清单](reference/common-bugs-checklist.md) | 语言特定错误模式, 常见陷阱 |
| **SQL注入预防** | [SQL注入指南](reference/cross-cutting/sql-injection-prevention.md) | 参数化查询, ORM 安全, 6种语言, 动态标识符, 检测 |
| **XSS预防** | [XSS预防指南](reference/cross-cutting/xss-prevention.md) | 输出编码, CSP, 5个框架, 输入验证与编码, 检测 |
| **N+1查询** | [N+1查询指南](reference/cross-cutting/n-plus-one-queries.md) | 懒加载, 批量获取, DataLoader, 5种语言, 检测 |
| **错误处理** | [错误处理指南](reference/cross-cutting/error-handling-principles.md) | 快速失败, 错误层级, 7种语言, 反模式, 日志记录 |
| **异步与并发** | [并发指南](reference/cross-cutting/async-concurrency-patterns.md) | Goroutines, async/await, actors, 结构化并发, 7种语言 |
| **审查最佳实践** | [代码审查最佳实践](reference/code-review-best-practices.md) | 沟通, 审查者心态, 给出反馈, 严重性标签 |

## 其他资源

- [PR审查模板](assets/pr-review-template.md) - PR审查评论模板
- [审查清单](assets/review-checklist.md) - 快速参考清单
