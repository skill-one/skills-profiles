# Rust 最佳实践

在编写或审查 Rust 代码时，请遵循这些指南。基于 Apollo GraphQL 的 [Rust 最佳实践手册](https://github.com/apollographql/rust-best-practices)。

## 最佳实践参考

在审查之前，请熟悉 Apollo 的 Rust 最佳实践。同时阅读所有相关的章节。在提供反馈时，参考以下文件：

- [第一章 - 编码风格和惯用法](references/chapter_01.md)：借用 vs 克隆，Copy 特性，Option/Result 处理，迭代器，注释，何时提取函数（重复 vs 错误抽象）
- [第二章 - Clippy 和 Linting](references/chapter_02.md)：Clippy 配置，重要 Lint，工作区 Lint 设置
- [第三章 - 性能思维](references/chapter_03.md)：性能分析，避免冗余克隆，栈 vs 堆，零成本抽象
- [第四章 - 错误处理](references/chapter_04.md)：Result vs panic，thiserror vs anyhow，错误层次结构
- [第五章 - 自动化测试](references/chapter_05.md)：测试命名，每个测试一个断言，快照测试
- [第六章 - 泛型与分发](references/chapter_06.md)：静态 vs 动态分发，trait 对象
- [第七章 - 类型状态模式](references/chapter_07.md)：编译时状态安全，何时使用
- [第八章 - 注释 vs 文档](references/chapter_08.md)：何时注释，doc 注释，rustdoc
- [第九章 - 理解指针](references/chapter_09.md)：线程安全，Send/Sync，指针类型

## 快速参考

### 借用 & 所有权
- 除非需要所有权转移，否则优先使用 `&T` 而不是 `.clone()`
- 在函数参数中使用 `&str` 而不是 `String`，`&[T]` 而不是 `Vec<T>`
- 小型 `Copy` 类型（≤24 字节）可以按值传递
- 当所有权不明确时使用 `Cow<'_, T>`

### 错误处理
- 对于可能失败的操作返回 `Result<T, E>`；生产环境中避免使用 `panic!`
- 测试外不要使用 `unwrap()`/`expect()`
- 使用 `thiserror` 处理库错误，`anyhow` 仅用于二进制程序
- 优先使用 `?` 操作符而不是 match 链进行错误传播

### 性能
- 始终使用 `--release` 标志进行性能分析
- 运行 `cargo clippy -- -D clippy::perf` 获取性能提示
- 循环中避免克隆；对于 Copy 类型使用 `.iter()` 而不是 `.into_iter()`
- 优先使用迭代器而不是手动循环；避免中间 `.collect()` 调用

### Linting
定期运行：`cargo clippy --all-targets --all-features --locked -- -D warnings`

需要关注的 Lint：
- `redundant_clone` - 不必要的克隆
- `large_enum_variant` - 过大的变体（考虑装箱）
- `needless_collect` - 过早的收集

使用 `#[expect(clippy::lint)]` 而不是 `#[allow(...)]` 并附带说明性注释。

### 测试
- 描述性命名测试：`process_should_return_error_when_input_empty()`
- 尽可能每个测试一个断言
- 使用 doc 测试 (`///`) 展示公共 API 示例
- 考虑使用 `cargo insta` 进行快照测试生成输出

### 泛型 & 分发
- 对于性能关键代码优先使用泛型（静态分发）
- 仅在需要异构集合时使用 `dyn Trait`
- 在 API 边界装箱，而不是内部

### 类型状态模式
在类型系统中编码有效状态，以在编译时捕获无效操作：
```rust
struct Connection<State> { /* ... */ _state: PhantomData<State> }
struct Disconnected;
struct Connected;

impl Connection<Connected> {
    fn send(&self, data: &[u8]) { /* 只有连接状态可以发送 */ }
}
```

### 文档
- `//` 注释解释 *为什么*（安全性，解决方案，设计理由）
- `///` doc 注释解释 *什么* 和 *如何* 用于公共 API
- 每个 `TODO` 需要一个关联的 issue：`// TODO(#42): ...`
- 为库启用 `#![deny(missing_docs)]`
