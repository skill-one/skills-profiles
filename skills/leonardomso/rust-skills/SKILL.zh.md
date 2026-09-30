---
name: rust-skills
description: 265条规则的全面Rust编码规范，涵盖26个类别。在编写、审查或重构Rust代码时使用。包括所有权、错误处理、异步模式、并发、不安全代码、API设计、内存优化、性能、数值安全、转换、serde、模式匹配、宏、闭包、可观测性、测试以及常见反模式。使用/rust-skills调用。
---

# Rust 最佳实践

编写高质量、符合规范且高度优化的 Rust 代码的全面指南。包含 265 条规则，分为 26 个类别，按影响程度排序，以指导 LLM 在代码生成和重构方面的应用。适用于 Rust 1.96 版本（2024 年版）。

## 应用场景

在以下情况下参考这些指南：
- 编写新的 Rust 函数、结构体或模块
- 实现 错误处理 或 异步代码
- 编写 并发、并行 或 `unsafe` 代码
- 设计 库的公共 API
- 审查 代码的 所有权/借用 问题
- 优化 内存使用 或 减少分配
- 调整 热路径 的性能
- 重构 现有的 Rust 代码

## 按优先级排序的规则类别

| 优先级 | 类别 | 影响 | 前缀 | 规则数量 |
|--------|------|------|------|----------|
| 1 | 所有权 & 借用 | 关键 | `own-` | 12 |
| 2 | 错误处理 | 关键 | `err-` | 12 |
| 3 | 内存优化 | 关键 | `mem-` | 17 |
| 4 | 不安全代码 | 关键 | `unsafe-` | 7 |
| 5 | API 设计 | 高 | `api-` | 17 |
| 6 | 异步/等待 | 高 | `async-` | 18 |
| 7 | 并发 | 高 | `conc-` | 4 |
| 8 | 编译器优化 | 高 | `opt-` | 12 |
| 9 | 数值 & 算术安全 | 高 | `num-` | 5 |
| 10 | 类型安全 | 中 | `type-` | 13 |
| 11 | 特性 & 泛型设计 | 中 | `trait-` | 6 |
| 12 | 转换 | 中 | `conv-` | 3 |
| 13 | 常量 & 编译时 | 中 | `const-` | 4 |
| 14 | Serde | 中 | `serde-` | 8 |
| 15 | 模式匹配 | 中 | `pat-` | 5 |
| 16 | 宏 | 中 | `macro-` | 8 |
| 17 | 闭包 | 中 | `closure-` | 5 |
| 18 | 集合 | 中 | `coll-` | 4 |
| 19 | 命名规范 | 中 | `name-` | 16 |
| 20 | 测试 | 中 | `test-` | 15 |
| 21 | 文档 | 中 | `doc-` | 12 |
| 22 | 可观察性 | 中 | `obs-` | 7 |
| 23 | 性能模式 | 中 | `perf-` | 13 |
| 24 | 项目结构 | 低 | `proj-` | 14 |
| 25 | Clippy & Linting | 低 | `lint-` | 13 |
| 26 | 反模式 | 参考 | `anti-` | 15 |

---

## 快速参考

### 1. 所有权 & 借用 (关键)

- [`own-borrow-over-clone`](rules/own-borrow-over-clone.md) - 优先使用 `&T` 借用而非 `.clone()`
- [`own-slice-over-vec`](rules/own-slice-over-vec.md) - 接受 `&[T]` 而非 `&Vec<T>`，`&str` 而非 `&String`
- [`own-cow-conditional`](rules/own-cow-conditional.md) - 使用 `Cow<'a, T>` 进行条件所有权
- [`own-arc-shared`](rules/own-arc-shared.md) - 使用 `Arc<T>` 进行线程安全的共享所有权
- [`own-rc-single-thread`](rules/own-rc-single-thread.md) - 在单线程环境中使用 `Rc<T>` 进行共享所有权
- [`own-refcell-interior`](rules/own-refcell-interior.md) - 在单线程代码中使用 `RefCell<T>` 进行内部可变性
- [`own-mutex-interior`](rules/own-mutex-interior.md) - 在多线程中使用 `Mutex<T>` 进行内部可变性
- [`own-rwlock-readers`](rules/own-rwlock-readers.md) - 当读操作远多于写操作时使用 `RwLock<T>`
- [`own-copy-small`](rules/own-copy-small.md) - 为小型、简单类型实现 `Copy`
- [`own-clone-explicit`](rules/own-clone-explicit.md) - 对复制有明确成本的类型使用显式 `Clone`
- [`own-move-large`](rules/own-move-large.md) - 对大型类型进行移动而非复制；如果移动成本高，使用 `Box`
- [`own-lifetime-elision`](rules/own-lifetime-elision.md) - 依赖生命周期省略规则；仅在需要时显式添加生命周期

### 2. 错误处理 (关键)

- [`err-thiserror-lib`](rules/err-thiserror-lib.md) - 使用 `thiserror` 作为库的错误类型
- [`err-anyhow-app`](rules/err-anyhow-app.md) - 使用 `anyhow` 进行应用错误处理
- [`err-result-over-panic`](rules/err-result-over-panic.md) - 对可恢复的错误返回 `Result<T, E>` 而非抛出异常
- [`err-context-chain`](rules/err-context-chain.md) - 使用 `.context()` 或 `.with_context()` 添加上下文
- [`err-no-unwrap-prod`](rules/err-no-unwrap-prod.md) - 在生产代码中避免 `unwrap()`；使用 `?`、`expect()` 或处理错误
- [`err-expect-bugs-only`](rules/err-expect-bugs-only.md) - 仅在表示 Bug 的不变式中使用 `expect()`，而非用户错误
- [`err-question-mark`](rules/err-question-mark.md) - 使用 `?` 运算符进行干净的错误传播
- [`err-from-impl`](rules/err-from-impl.md) - 实现 `From<E>` 以支持错误转换并启用 `?` 运算符
- [`err-source-chain`](rules/err-source-chain.md) - 使用 `#[source]` 或 `source()` 方法保留错误链
- [`err-lowercase-msg`](rules/err-lowercase-msg.md) - 将错误消息以小写开头，无尾随标点
- [`err-doc-errors`](rules/err-doc-errors.md) - 在文档注释的 `# Errors` 部分记录错误条件
- [`err-custom-type`](rules/err-custom-type.md) - 为特定领域失败定义自定义错误类型

### 3. 内存优化 (关键)

- [`mem-with-capacity`](rules/mem-with-capacity.md) - 在已知大小的情况下使用 `with_capacity()`
- [`mem-smallvec`](rules/mem-smallvec.md) - 使用 `SmallVec` 用于通常较小的集合
- [`mem-arrayvec`](rules/mem-arrayvec.md) - 使用 `ArrayVec<T, N>` 用于固定容量的集合，永不堆分配
- [`mem-box-large-variant`](rules/mem-box-large-variant.md) - 将大型枚举变体装箱以减少枚举的整体大小
- [`mem-boxed-slice`](rules/mem-boxed-slice.md) - 使用 `Box<[T]>` 而非 `Vec<T>` 用于固定大小的堆数据
- [`mem-thinvec`](rules/mem-thinvec.md) - 使用 `ThinVec<T>` 用于具有最小开销的可空集合
- [`mem-clone-from`](rules/mem-clone-from.md) - 使用 `clone_from()` 在重复克隆时重用分配
- [`mem-reuse-collections`](rules/mem-reuse-collections.md) - 在循环中清空并重用集合，而非创建新集合
- [`mem-avoid-format`](rules/mem-avoid-format.md) - 当字符串字面量可用时避免 `format!()` 
- [`mem-write-over-format`](rules/mem-write-over-format.md) - 使用 `write!()` 将数据写入现有缓冲区，而非 `format!()` 分配
- [`mem-arena-allocator`](rules/mem-arena-allocator.md) - 使用内存分配器进行批量分配
- [`mem-zero-copy`](rules/mem-zero-copy.md) - 使用切片和 `Bytes` 的零拷贝模式
- [`mem-compact-string`](rules/mem-compact-string.md) - 使用紧凑字符串类型进行内存受限的字符串存储
- [`mem-smaller-integers`](rules/mem-smaller-integers.md) - 使用适当大小的整数以减少内存占用
- [`mem-assert-type-size`](rules/mem-assert-type-size.md) - 使用静态断言来防止类型大小意外增长
- [`mem-take-replace`](rules/mem-take-replace.md) - 使用 `mem::take` / `mem::replace` 从 `&mut` 中移动值而不克隆
- [`mem-drop-order`](rules/mem-drop-order.md) - 了解并控制析构顺序：结构体字段从上到下析构，局部变量反向

### 4. 不安全代码 (关键)

- [`unsafe-safety-comment`](rules/unsafe-safety-comment.md) - 在每个 `unsafe` 块上方编写 `// SAFETY:` 注释，并在每个 `unsafe fn` 中添加 `# Safety` 部分
- [`unsafe-minimize-scope`](rules/unsafe-minimize-scope.md) - 将 `unsafe` 块保持尽可能小——仅标记需要不安全操作的代码，而非周围的代码
- [`unsafe-miri-ci`](rules/unsafe-miri-ci.md) - 在 CI 中对每个包含 `unsafe` 代码的 crate 运行 `cargo miri test`
- [`unsafe-maybeuninit`](rules/unsafe-maybeuninit.md) - 使用 `MaybeUninit<T>` 处理未初始化的内存；对具有有效不变式的类型，永不使用 `mem::uninitialized()` 或 `mem::zeroed()`
- [`unsafe-extern-block`](rules/unsafe-extern-block.md) - 在 Rust 2024 中，将 `extern` 块包裹在 `unsafe extern { }` 中，并标注每个项为 `safe` 或 `unsafe`
- [`unsafe-send-sync-manual`](rules/unsafe-send-sync-manual.md) - 记录手动实现 `Send` 或 `Sync` 时的不变式；优先让编译器自动推导
- [`unsafe-no-mangle-unsafe`](rules/unsafe-no-mangle-unsafe.md) - 在 Rust 2024 中，使用 `#[unsafe(no_mangle)]`、`#[unsafe(export_name = "...")]` 和 `#[unsafe(link_section = "...")]`，而非裸属性形式

### 5. API 设计 (高)

- [`api-builder-pattern`](rules/api-builder-pattern.md) - 使用 构建者模式 处理复杂构建
- [`api-builder-must-use`](rules/api-builder-must-use.md) - 使用 `#[must_use]` 标记构建者方法以防止静默释放
- [`api-newtype-safety`](rules/api-newtype-safety.md) - 使用新类型防止混合语义不同的值
- [`api-typestate`](rules/api-typestate.md) - 使用类型状态模式将状态机不变式编码在类型系统中
- [`api-sealed-trait`](rules/api-sealed-trait.md) - 使用密封特性防止外部实现，同时允许使用
- [`api-extension-trait`](rules/api-extension-trait.md) - 使用扩展特性为外部类型添加方法
- [`api-parse-dont-validate`](rules/api-parse-dont-validate.md) - 在边界处解析到已验证的类型
- [`api-impl-into`](rules/api-impl-into.md) - 接受 `impl Into<T>` 以实现灵活的 API，实现 `From<T>` 进行转换
- [`api-impl-asref`](rules/api-impl-asref.md) - 当你只需要借用内部数据时使用 `AsRef<T>`
- [`api-must-use`](rules/api-must-use.md) - 当忽略结果可能是 Bug 时，使用 `#[must_use]` 标记类型和函数
- [`api-non-exhaustive`](rules/api-non-exhaustive.md) - 对公共枚举和结构体使用 `#[non_exhaustive]` 以实现向前兼容
- [`api-from-not-into`](rules/api-from-not-into.md) - 实现 `From<T>` 而非 `Into<U>`——From 会自动提供 Into
- [`api-default-impl`](rules/api-default-impl.md) - 对具有合理默认值的类型实现 `Default`
- [`api-common-traits`](rules/api-common-traits.md) - 对公共类型实现标准特性（Debug、Clone、PartialEq 等）
- [`api-serde-optional`](rules/api-serde-optional.md) - 将 serde 作为特性标志，而非库 crate 的硬依赖
- [`api-impl-fromiterator`](rules/api-impl-fromiterator.md) - 对集合类型实现 `FromIterator` 和 `Extend`，以及所有三种引用形式的 `IntoIterator`
- [`api-operator-overload`](rules/api-operator-overload.md) - 仅在语义自然且不令人意外时重载运算符

### 6. 异步/等待 (高)

- [`async-tokio-runtime`](rules/async-tokio-runtime.md) - 根据你的工作负载适当配置 Tokio 运行时
- [`async-no-lock-await`](rules/async-no-lock-await.md) - 永远不要在 `.await` 跨越 `Mutex`/`RwLock`
- [`async-spawn-blocking`](rules/async-spawn-blocking.md) - 使用 `spawn_blocking` 处理 CPU 密集型工作
- [`async-tokio-fs`](rules/async-tokio-fs.md) - 在异步代码中使用 `tokio::fs` 而非 `std::fs`
- [`async-cancellation-token`](rules/async-cancellation-token.md) - 使用 `CancellationToken` 进行优雅关闭和任务取消
- [`async-join-parallel`](rules/async-join-parallel.md) - 使用 `join!` 或 `try_join!` 处理并发独立的 Future
- [`async-try-join`](rules/async-try-join.md) - 使用 `try_join!` 处理并发可能失败的操作，并在出错时提前返回
- [`async-select-racing`](rules/async-select-racing.md) - 使用 `select!` 处理竞争 Future 并处理第一个完成的
- [`async-bounded-channel`](rules/async-bounded-channel.md) - 使用有界通道应用背压并防止无界内存增长
- [`async-mpsc-queue`](rules/async-mpsc-queue.md) - 使用 `mpsc` 通道在任务间进行异步消息队列
- [`async-broadcast-pubsub`](rules/async-broadcast-pubsub.md) - 使用 `broadcast` 通道进行发布/订阅，所有订阅者接收所有消息
- [`async-watch-latest`](rules/async-watch-latest.md) - 使用 `watch` 通道与多个观察者共享最新值
- [`async-oneshot-response`](rules/async-oneshot-response.md) - 使用 `oneshot` 通道处理请求/响应模式
- [`async-joinset-structured`](rules/async-joinset-structured.md) - 使用 `JoinSet` 管理动态的已启动任务集合
- [`async-clone-before-await`](rules/async-clone-before-await.md) - 在 `.await` 点之前克隆 Arc/Rc 数据，避免跨挂起点持有引用
- [`async-fn-in-trait`](rules/async-fn-in-trait.md) - 在特性中使用原生 `async fn`（稳定版 1.75），而非 `async_trait` 宏
- [`async-async-fn-bounds`](rules/async-async-fn-bounds.md) - 使用 `AsyncFn`/`AsyncFnMut`/`AsyncFnOnce` 约束，而非 `F: Fn() -> Fut, Fut: Future`
- [`async-cancel-safety`](rules/async-cancel-safety.md) - 确保在 `tokio::select!` 分支中使用的 Future 是可取消的

### 7. 并发 (高)

- [`conc-rayon-par-iter`](rules/conc-rayon-par-iter.md) - 使用 rayon 的 `par_iter()` 进行 CPU 密集型数据并行
- [`conc-scoped-threads`](rules/conc-scoped-threads.md) - 使用 `std::thread::scope` 跨线程借用栈数据
- [`conc-atomic-ordering`](rules/conc-atomic-ordering.md) - 对每个原子操作使用最弱的正确内存 `Ordering`
- [`conc-thread-local`](rules/conc-thread-local.md) - 优先使用 `thread_local!` 与 `Cell`/`RefCell` 而非 `static mut`

### 8. 编译器优化 (高)

- [`opt-inline-small`](rules/opt-inline-small.md) - 对小型热函数使用 `#[inline]`
- [`opt-inline-always-rare`](rules/opt-inline-always-rare.md) - 稀有使用 `#[inline(always)]`——仅用于通过分析证明的关键热路径
- [`opt-inline-never-cold`](rules/opt-inline-never-cold.md) - 对错误路径和很少执行的代码使用 `#[inline(never)]` 和 `#[cold]`
- [`opt-cold-unlikely`](rules/opt-cold-unlikely.md) - 使用 `#[cold]` 标记不太可能的代码路径以帮助编译器优化
- [`opt-likely-hint`](rules/opt-likely-hint.md) - 使用代码结构提示可能分支；在 nightly 版本上使用内联函数
- [`opt-lto-release`](rules/opt-lto-release.md) - 在发布构建中启用 LTO
- [`opt-codegen-units`](rules/opt-codegen-units.md) - 在发布构建中设置 `codegen-units = 1` 以实现最大优化
- [`opt-pgo-profile`](rules/opt-pgo-profile.md) - 使用 Profile-Guided Optimization (PGO) 实现最大性能
- [`opt-target-cpu`](rules/opt-target-cpu.md) - 使用 `target-cpu=native` 在已知部署目标上实现最大性能
- [`opt-bounds-check`](rules/opt-bounds-check.md) - 在热路径中使用迭代器和模式消除边界检查
- [`opt-simd-portable`](rules/opt-simd-portable.md) - 使用可移植的 SIMD 进行跨架构的向量化操作
- [`opt-cache-friendly`](rules/opt-cache-friendly.md) - 组织数据以实现缓存友好的访问模式

### 9. 数值 & 算术安全 (高)

- [`num-overflow-explicit`](rules/num-overflow-explicit.md) - 明确处理整数溢出：`checked_`/`saturating_`/`wrapping_`/`overflowing_`
- [`num-cast-try-from`](rules/num-cast-try-from.md) - 避免 `as` 进行窄化转换；使用 `From` 进行扩展转换，`TryFrom` 进行窄化转换
- [`num-float-compare`](rules/num-float-compare.md) - 不要用 `==` 比较浮点数；使用容差，`total_cmp` 用于排序
- [`num-saturating-clamp`](rules/num-saturating-clamp.md) - 使用 `clamp` 和饱和算术绑定值
- [`num-nonzero`](rules/num-nonzero.md) - 使用 `NonZero*` 类型禁止零并解锁特殊优化

### 10. 类型安全 (中)

- [`type-newtype-ids`](rules/type-newtype-ids.md) - 用新类型包装 ID：`UserId(u64)`
- [`type-newtype-validated`](rules/type-newtype-validated.md) - 使用新类型在构造时强制执行验证
- [`type-enum-states`](rules/type-enum-states.md) - 使用枚举表示互斥状态
- [`type-option-nullable`](rules/type-option-nullable.md) - 使用 `Option<T>` 表示可能不存在的值
- [`type-result-fallible`](rules/type-result-fallible.md) - 使用 `Result<T, E>` 表示可能失败的运算
- [`type-phantom-marker`](rules/type-phantom-marker.md) - 使用 `PhantomData` 在不产生运行时成本的情况下表达类型关系
- [`type-never-diverge`](rules/type-never-diverge.md) - 对于永远不会返回的函数，使用 `!`（非类型）标记
- [`type-generic-bounds`](rules/type-generic-bounds.md) - 仅在需要时添加特征边界，优先使用 where 子句以提高可读性
- [`type-no-stringly`](rules/type-no-stringly.md) - 避免字符串类型 API；使用枚举、新类型或验证类型
- [`type-repr-transparent`](rules/type-repr-transparent.md) - 在 FFI 上下文中使用 `#[repr(transparent)]` 包装新类型
- [`type-deref-coercion`](rules/type-deref-coercion.md) - 仅对智能指针和透明包装器类型实现 `Deref`/`DerefMut`
- [`type-display-vs-debug`](rules/type-display-vs-debug.md) - 使用 `Display` 表示面向用户的输出，使用 `Debug` 表示诊断信息；永远不要交换它们
- [`type-numeric-fmt`](rules/type-numeric-fmt.md) - 对数值新类型实现 `LowerHex`、`UpperHex`、`Octal` 和 `Binary`

### 11. 特征与泛型设计 (中等)

- [`trait-associated-type-vs-generic`](rules/trait-associated-type-vs-generic.md) - 当每个实现恰好有一个输出类型时使用关联类型；当类型可以为许多输入类型实现该特征时使用泛型参数
- [`trait-blanket-impl`](rules/trait-blanket-impl.md) - 使用 `impl<T: Bound> Trait for T` 的通用实现，为所有满足约束的类型提供行为
- [`trait-coherence-newtype`](rules/trait-coherence-newtype.md) - 尊重孤儿规则；将外部类型包装在新类型中，在外部类型上实现外部的特征
- [`trait-default-methods`](rules/trait-default-methods.md) - 通过少量必需方法和基于它们构建的默认方法定义特征
- [`trait-dyn-vs-generic`](rules/trait-dyn-vs-generic.md) - 故意选择静态派发（泛型 / `impl Trait`）与动态派发（`dyn Trait`）
- [`trait-object-safety`](rules/trait-object-safety.md) - 当需要 `dyn Trait` 时，保持特征动态兼容（对象安全）

### 12. 转换 (中等)

- [`conv-tryfrom-fallible`](rules/conv-tryfrom-fallible.md) - 对于可能失败的转换实现 `TryFrom`，而不是使用自定义转换函数
- [`conv-fromstr-parsing`](rules/conv-fromstr-parsing.md) - 实现 `FromStr` 以启用 `str::parse` 进行字符串到类型的转换
- [`conv-asmut-mutable`](rules/conv-asmut-mutable.md) - 接受 `impl AsMut<T>` 以进行灵活的可变借用输入，而不是具体的可变引用

### 13. 常量与编译时 (中等)

- [`const-block`](rules/const-block.md) - 使用内联 `const { }` 块进行编译时评估和断言
- [`const-fn`](rules/const-fn.md) - 当函数可以在编译时运行时，将其声明为 `const fn`
- [`const-generics`](rules/const-generics.md) - 使用 const 泛型 `<const N: usize>` 对值进行参数化
- [`const-vs-static`](rules/const-vs-static.md) - 使用 `const` 表示内联值，使用 `static` 表示单地址实例

### 14. Serde (中等)

- [`serde-rename-all`](rules/serde-rename-all.md) - 使用 `#[serde(rename_all = ...)]` 与外部命名约定匹配
- [`serde-default-compat`](rules/serde-default-compat.md) - 使用 `#[serde(default)]` 表示可选字段和向后兼容的字段
- [`serde-skip-empty`](rules/serde-skip-empty.md) - 使用 `skip_serializing_if` 跳过空字段
- [`serde-flatten`](rules/serde-flatten.md) - 使用 `#[serde(flatten)]` 内联嵌套结构或捕获额外键
- [`serde-enum-representation`](rules/serde-enum-representation.md) - 故意选择枚举标记：外部标记、内部标记、相邻标记或无标记
- [`serde-deny-unknown-fields`](rules/serde-deny-unknown-fields.md) - 使用 `#[serde(deny_unknown_fields)]` 拒绝意外的键
- [`serde-custom-with`](rules/serde-custom-with.md) - 使用 `with` / `serialize_with` / `deserialize_with` 自定义字段的（反）序列化
- [`serde-try-from-validate`](rules/serde-try-from-validate.md) - 使用 `#[serde(try_from = "Raw")]` 在反序列化时进行验证

### 15. 模式匹配 (中等)

- [`pat-let-else`](rules/pat-let-else.md) - 使用 `let ... else` 进行早期返回的模式提取
- [`pat-matches-macro`](rules/pat-matches-macro.md) - 使用 `matches!()` 进行布尔模式测试
- [`pat-if-let-chains`](rules/pat-if-let-chains.md) - 使用 `if let` 链组合模式绑定和条件
- [`pat-exhaustive-enum`](rules/pat-exhaustive-enum.md) - 逐一匹配拥有的枚举；避免使用 `_` 捕获所有情况，这会隐藏新的变体
- [`pat-at-bindings`](rules/pat-at-bindings.md) - 使用 `@` 绑定在匹配模式时捕获值

### 16. 宏 (中等)

- [`macro-prefer-functions`](rules/macro-prefer-functions.md) - 只有当函数或泛型无法表达时才使用宏
- [`macro-rules-hygiene`](rules/macro-rules-hygiene.md) - 依赖 `macro_rules!` 的清洁性，并使用 `$crate` 引用你的 crate 中的项
- [`macro-fragment-specifiers`](rules/macro-fragment-specifiers.md) - 在可能的情况下使用精确的片段指定符，而不是原始的 `:tt`
- [`macro-export-crate-path`](rules/macro-export-crate-path.md) - 使用 `#[macro_export]` 和干净的导入路径导出声明性宏
- [`macro-private-helpers`](rules/macro-private-helpers.md) - 使用 `#[doc(hidden)] pub mod __private` 隐藏宏生成的辅助项
- [`macro-proc-two-crate`](rules/macro-proc-two-crate.md) - 将过程宏放在专门的 `proc-macro = true` crate 中，并从接口重新导出
- [`macro-proc-syn-quote`](rules/macro-proc-syn-quote.md) - 使用 `syn`、`quote` 和 `proc-macro2` 构建过程宏
- [`macro-proc-error-spans`](rules/macro-proc-error-spans.md) - 将过程宏错误报告为跨编译错误，而不是通过恐慌

### 17. 闭包 (中等)

- [`closure-fn-trait-bounds`](rules/closure-fn-trait-bounds.md) - 要求回调需要的最宽松的 `Fn` 特征（`FnOnce` ⊇ `FnMut` ⊇ `Fn`）
- [`closure-impl-fn-return`](rules/closure-impl-fn-return.md) - 将闭包作为 `impl Fn`/`FnMut`/`FnOnce` 返回，而不是 `Box<dyn Fn>`
- [`closure-move-capture`](rules/closure-move-capture.md) - 对于超出当前作用域的闭包，使用 `move`；在 `move` 之前克隆以保留原始闭包
- [`closure-static-vs-dyn`](rules/closure-static-vs-dyn.md) - 对于热回调，接受 `impl Fn`（泛型）；使用 `&dyn Fn`/`Box<dyn Fn>` 以减少代码大小或存储它们
- [`closure-disjoint-capture`](rules/closure-disjoint-capture.md) - 仅捕获你使用的部分；依赖 2021 年版的离散闭包捕获

### 18. 集合 (中等)

- [`coll-binaryheap`](rules/coll-binaryheap.md) - 使用 `BinaryHeap` 作为优先队列或重复最大值提取
- [`coll-map-choice`](rules/coll-map-choice.md) - 根据访问模式选择映射：`HashMap`（快速、无序）、`BTreeMap`（排序 / 范围查询）、`IndexMap`（插入顺序）
- [`coll-seq-choice`](rules/coll-seq-choice.md) - 默认使用 `Vec`；对于队列/双端队列行为使用 `VecDeque`；避免使用 `LinkedList`
- [`coll-set-membership`](rules/coll-set-membership.md) - 使用 `HashSet`/`BTreeSet` 进行成员资格测试和去重，而不是线性 `Vec::contains`

### 19. 命名约定 (中等)

- [`name-types-camel`](rules/name-types-camel.md) - 使用 `UpperCamelCase` 命名类型、特征和枚举
- [`name-variants-camel`](rules/name-variants-camel.md) - 使用 `UpperCamelCase` 命名枚举变体
- [`name-funcs-snake`](rules/name-funcs-snake.md) - 使用 `snake_case` 命名函数、方法、变量和模块
- [`name-consts-screaming`](rules/name-consts-screaming.md) - 使用 `SCREAMING_SNAKE_CASE` 命名常量和静态变量
- [`name-lifetime-short`](rules/name-lifetime-short.md) - 使用简短、传统的生命周期名称：`'a`，`'b`，`'de`，`'src`
- [`name-type-param-single`](rules/name-type-param-single.md) - 使用单个大写字母作为类型参数：`T`，`E`，`K`，`V`
- [`name-as-free`](rules/name-as-free.md) - `as_` 前缀：自由引用转换
- [`name-to-expensive`](rules/name-to-expensive.md) - 使用 `to_` 前缀表示昂贵的转换，这些转换会分配或计算
- [`name-into-ownership`](rules/name-into-ownership.md) - 使用 `into_` 前缀表示消耗所有权的转换
- [`name-no-get-prefix`](rules/name-no-get-prefix.md) - 对于简单的获取器，省略 `get_` 前缀
- [`name-is-has-bool`](rules/name-is-has-bool.md) - 使用 `is_`，`has_`，`can_`，`should_` 前缀表示返回布尔值的函数
- [`name-iter-convention`](rules/name-iter-convention.md) - 使用 `iter`/`iter_mut`/`into_iter` 作为迭代器方法
- [`name-iter-method`](rules/name-iter-method.md) - 一致地命名迭代器方法 `iter()`，`iter_mut()` 和 `into_iter()`
- [`name-iter-type-match`](rules/name-iter-type-match.md) - 迭代器类型命名与源方法匹配
- [`name-acronym-word`](rules/name-acronym-word.md) - 在标识符中将缩写视为单词：`HttpServer`，而不是 `HTTPServer`
- [`name-crate-no-rs`](rules/name-crate-no-rs.md) - 不要在 crate 名称后缀 `-rs` 或 `-rust`

### 20. 测试 (中等)

- [`test-cfg-test-module`](rules/test-cfg-test-module.md) - 在每个模块中，将单元测试放在 `#[cfg(test)] mod tests { }` 中
- [`test-use-super`](rules/test-use-super.md) - 在测试模块中使用 `use super::*;` 访问父模块项
- [`test-integration-dir`](rules/test-integration-dir.md) - 将集成测试放在 `tests/` 目录中
- [`test-descriptive-names`](rules/test-descriptive-names.md) - 使用描述性的测试名称，说明正在测试的内容
- [`test-arrange-act-assert`](rules/test-arrange-act-assert.md) - 使用清晰的 Arrange、Act、Assert 部分组织测试
- [`test-proptest-properties`](rules/test-proptest-properties.md) - 使用 proptest 进行基于属性的测试
- [`test-mockall-mocking`](rules/test-mockall-mocking.md) - 使用 mockall 进行特征模拟
- [`test-mock-traits`](rules/test-mock-traits.md) - 使用特征表示依赖项以在测试中启用模拟
- [`test-fixture-raii`](rules/test-fixture-raii.md) - 使用 RAII 模式（Drop 特征）进行自动测试清理
- [`test-tokio-async`](rules/test-tokio-async.md) - 使用 `#[tokio::test]` 进行异步测试
- [`test-should-panic`](rules/test-should-panic.md) - 使用 `#[should_panic]` 测试代码是否按预期恐慌
- [`test-criterion-bench`](rules/test-criterion-bench.md) - 使用 `criterion` 进行基准测试
- [`test-doctest-examples`](rules/test-doctest-examples.md) - 将文档示例保留为可执行的 doctests
- [`test-loom-concurrency`](rules/test-loom-concurrency.md) - 使用 `loom` 消耗测试无锁和并发代码
- [`test-snapshot-testing`](rules/test-snapshot-testing.md) - 使用快照测试（insta）进行复杂或序列化输出

### 21. 文档 (中等)

- [`doc-all-public`](rules/doc-all-public.md) - 使用 `///` doc 注释记录所有公共项
- [`doc-module-inner`](rules/doc-module-inner.md) - 使用 `//!` 记录模块级文档
- [`doc-examples-section`](rules/doc-examples-section.md) - 包括 `# Examples` 并包含可运行的代码
- [`doc-errors-section`](rules/doc-errors-section.md) - 包括 `# Errors` 部分以表示可能失败的函数
- [`doc-panics-section`](rules/doc-panics-section.md) - 包括 `# Panics` 部分以表示可能恐慌的函数
- [`doc-safety-section`](rules/doc-safety-section.md) - 包括 `# Safety` 部分以表示不安全的函数
- [`doc-question-mark`](rules/doc-question-mark.md) - 在示例中使用 `?`，而不是 `.unwrap()`
- [`doc-hidden-setup`](rules/doc-hidden-setup.md) - 使用 `# ` 前缀隐藏示例设置代码
- [`doc-intra-links`](rules/doc-intra-links.md) - 使用文档内链接引用类型和项
- [`doc-link-types`](rules/doc-link-types.md) - 使用文档内链接连接相关类型和函数
- [`doc-cargo-metadata`](rules/doc-cargo-metadata.md) - 填写 `Cargo.toml` 元数据以发布 crate
- [`doc-crate-readme`](rules/doc-crate-readme.md) - 使用 `#![doc = include_str!("../README.md")]` 统一 README 和 crate 根文档

### 22. 可观察性 (中等)

- [`obs-tracing-over-log`](rules/obs-tracing-over-log.md) - 使用 `tracing` 进行结构化、带跨度感知的诊断，而不是 `println!` 或裸 `log`
- [`obs-library-facade`](rules/obs-library-facade.md) - 库通过 tracing/log 接口发出，从不安装订阅者
- [`obs-structured-fields`](rules/obs-structured-fields.md) - 记录结构化键值字段，而不是将值插入到消息字符串中
- [`obs-instrument-spans`](rules/obs-instrument-spans.md) - 使用 `#[tracing::instrument]` 和跨度将上下文附加到异步任务和请求
- [`obs-levels-filter`](rules/obs-levels-filter.md) - 有意义地使用日志级别，并使用 `EnvFilter` / `RUST_LOG` 进行过滤
- [`obs-error-chain`](rules/obs-error-chain.md) - 记录错误及其完整来源链，并确保每个错误只记录一次
- [`obs-no-sensitive-data`](rules/obs-no-sensitive-data.md) - 永远不要记录秘密或 PII；对其进行编辑或跳过

### 23. 性能模式 (中等)

- [`perf-iter-over-index`](rules/perf-iter-over-index.md) - 优先使用迭代器而不是手动索引
- [`perf-iter-lazy`](rules/perf-iter-lazy.md) - 保持迭代器惰性，仅在需要时收集
- [`perf-collect-once`](rules/perf-collect-once.md) - 不要收集中间迭代器
- [`perf-entry-api`](rules/perf-entry-api.md) - 使用入口 API 进行映射插入或更新
- [`perf-drain-reuse`](rules/perf-drain-reuse.md) - 使用 drain 重用分配
- [`perf-extend-batch`](rules/perf-extend-batch.md) - 使用 extend 进行批量插入
- [`perf-chain-avoid`](rules/perf-chain-avoid.md) - 在热循环中避免链
- [`perf-collect-into`](rules/perf-collect-into.md) - 使用 collect_into 以重用容器
- [`perf-black-box-bench`](rules/perf-black-box-bench.md) - 在基准测试中使用 black_box
- [`perf-release-profile`](rules/perf-release-profile.md) - 优化发布配置文件设置
- [`perf-profile-first`](rules/perf-profile-first.md) - 在优化之前进行性能分析
- [`perf-ahash`](rules/perf-ahash.md) - 当不需要 DoS 防护时，使用更快的哈希器（`ahash` / `FxHashMap`）
- [`perf-io-buffering`](rules/perf-io-buffering.md) - 将 `Read`/`Write` 包装在 `BufReader`/`BufWriter` 中进行许多小操作

### 24. 项目结构 (低)

- [`proj-lib-main-split`](rules/proj-lib-main-split.md) - 保持 `main.rs` 最小，逻辑在 `lib.rs` 中
- [`proj-mod-by-feature`](rules/proj-mod-by-feature.md) - 按特性组织模块，而非类型
- [`proj-flat-small`](rules/proj-flat-small.md) - 保持小型项目扁平化
- [`proj-mod-rs-dir`](rules/proj-mod-rs-dir.md) - 使用 `mod.rs` 处理多文件模块
- [`proj-pub-crate-internal`](rules/proj-pub-crate-internal.md) - 使用 `pub(crate)` 处理内部 API
- [`proj-pub-super-parent`](rules/proj-pub-super-parent.md) - 使用 `pub(super)` 处理仅父级可见性
- [`proj-pub-use-reexport`](rules/proj-pub-use-reexport.md) - 使用 `pub use` 清洁公共 API
- [`proj-prelude-module`](rules/proj-prelude-module.md) - 为常用导入创建预置模块
- [`proj-bin-dir`](rules/proj-bin-dir.md) - 将多个二进制文件放在 `src/bin/`
- [`proj-workspace-large`](rules/proj-workspace-large.md) - 使用工作区处理大型项目
- [`proj-workspace-deps`](rules/proj-workspace-deps.md) - 使用工作区依赖继承确保 crate 间版本一致性
- [`proj-feature-additive`](rules/proj-feature-additive.md) - 设计 Cargo 特性为严格可叠加
- [`proj-msrv-declare`](rules/proj-msrv-declare.md) - 在 `Cargo.toml` 中声明 `rust-version` (MSRV) 并在 CI 中测试
- [`proj-build-rs-minimal`](rules/proj-build-rs-minimal.md) - 保持 `build.rs` 最小、确定性和幂等性

### 25. Clippy & Linting (LOW)

- [`lint-deny-correctness`](rules/lint-deny-correctness.md) - `#![deny(clippy::correctness)]`
- [`lint-warn-suspicious`](rules/lint-warn-suspicious.md) - 启用 `clippy::suspicious` 捕获可能存在的 bug
- [`lint-warn-style`](rules/lint-warn-style.md) - 启用 `clippy::style` 确保代码符合 idiomatic Rust
- [`lint-warn-complexity`](rules/lint-warn-complexity.md) - 启用 `clippy::complexity` 简化代码
- [`lint-warn-perf`](rules/lint-warn-perf.md) - 启用 `clippy::perf` 提升性能
- [`lint-pedantic-selective`](rules/lint-pedantic-selective.md) - 选择性启用 `clippy::pedantic`
- [`lint-missing-docs`](rules/lint-missing-docs.md) - 对公共项缺失文档发出警告
- [`lint-unsafe-doc`](rules/lint-unsafe-doc.md) - 要求 unsafe 块必须有文档
- [`lint-cargo-metadata`](rules/lint-cargo-metadata.md) - 对已发布的 crate 启用 `clippy::cargo`
- [`lint-rustfmt-check`](rules/lint-rustfmt-check.md) - 在 CI 中运行 `cargo fmt --check`
- [`lint-workspace-lints`](rules/lint-workspace-lints.md) - 在工作区级别配置 lints 以确保一致性
- [`lint-cfg-check`](rules/lint-cfg-check.md) - 启用 `unexpected_cfgs` 并声明已知 cfg 以捕获特性门控拼写错误
- [`lint-clippy-nursery-selected`](rules/lint-clippy-nursery-selected.md) - 选择性启用高价值的 `clippy::nursery` lints，而非整个分组

### 26. Anti-patterns (REFERENCE)

- [`anti-unwrap-abuse`](rules/anti-unwrap-abuse.md) - 生产代码中避免使用 `.unwrap()`
- [`anti-expect-lazy`](rules/anti-expect-lazy.md) - 可恢复的错误避免使用 `expect`
- [`anti-clone-excessive`](rules/anti-clone-excessive.md) - 当借用可用时避免克隆
- [`anti-lock-across-await`](rules/anti-lock-across-await.md) - 避免在 `await` 点持有锁
- [`anti-string-for-str`](rules/anti-string-for-str.md) - 当 `&str` 可用时避免接受 `&String`
- [`anti-vec-for-slice`](rules/anti-vec-for-slice.md) - 当 `&[T]` 可用时避免接受 `&Vec<T>`
- [`anti-index-over-iter`](rules/anti-index-over-iter.md) - 迭代器可用时避免使用索引
- [`anti-panic-expected`](rules/anti-panic-expected.md) - 避免在可恢复的错误上触发 panic
- [`anti-empty-catch`](rules/anti-empty-catch.md) - 避免静默忽略错误
- [`anti-over-abstraction`](rules/anti-over-abstraction.md) - 避免过度泛化
- [`anti-premature-optimize`](rules/anti-premature-optimize.md) - 在分析性能前避免优化
- [`anti-type-erasure`](rules/anti-type-erasure.md) - 当 `impl Trait` 可用时避免使用 `Box<dyn Trait>`
- [`anti-format-hot-path`](rules/anti-format-hot-path.md) - 热路径避免使用 `format!`
- [`anti-collect-intermediate`](rules/anti-collect-intermediate.md) - 避免收集中间迭代器
- [`anti-stringly-typed`](rules/anti-stringly-typed.md) - 在可使用枚举或 newtype 的地方避免使用字符串

---

## Recommended Cargo.toml Settings

```toml
[profile.release]
opt-level = 3
lto = "fat"
codegen-units = 1
panic = "abort"
strip = true

[profile.bench]
inherits = "release"
debug = true
strip = false

[profile.dev]
opt-level = 0
debug = true

[profile.dev.package."*"]
opt-level = 3  # 开发环境中优化依赖
```

---

## How to Use

此技能提供规则标识符以供快速参考。在生成或审查 Rust 代码时：

1. **根据任务类型检查相关类别**
2. **应用匹配前缀的规则**
3. **优先级：CRITICAL > HIGH > MEDIUM > LOW**
4. **阅读 `rules/` 中的规则文件以获取详细示例**

### 按任务应用规则

| 任务 | 主要类别 |
|------|----------|
| 新函数 | `own-`, `err-`, `name-`, `pat-` |
| 新结构/API | `api-`, `type-`, `conv-`, `doc-` |
| 异步代码 | `async-`, `own-` |
| 并发 / 并行 | `conc-`, `async-`, `own-` |
| 不安全代码 | `unsafe-`, `type-`, `test-` |
| 错误处理 | `err-`, `api-`, `pat-` |
| 类型转换 | `conv-`, `api-` |
| 序列化 (serde) | `serde-`, `type-`, `api-` |
| 数值 / 算术 | `num-`, `type-` |
| 宏 / 代码生成 | `macro-`, `anti-` |
| 闭包 / 回调 | `closure-`, `type-` |
| 日志 / 可观测性 | `obs-`, `err-` |
| 内存优化 | `mem-`, `own-`, `perf-` |
| 性能调优 | `opt-`, `mem-`, `perf-` |
| 代码审查 | `anti-`, `lint-` |

---

## Sources & Attribution

此技能是官方 Rust 指南、知名书籍和广泛使用的 crate 中的模式独立综合。它未与 Rust 项目或任何 crate 作者关联，文本和代码示例均为原创。

**官方 Rust 文档**
- [The Rust Reference](https://doc.rust-lang.org/reference/)
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [The Rustonomicon](https://doc.rust-lang.org/nomicon/) (不安全代码)
- [Rust 2024 Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2024/)
- [The Cargo Book](https://doc.rust-lang.org/cargo/)
- [Standard library docs](https://doc.rust-lang.org/std/) 和 [release notes](https://doc.rust-lang.org/releases.html)

**书籍 & 指南**
- [The Rust Performance Book](https://nnethercote.github.io/perf-book/) — Nicholas Nethercote
- [Rust Design Patterns](https://rust-unofficial.github.io/patterns/) — rust-unofficial
- [Rust Atomics and Locks](https://marabos.nl/atomics/) — Mara Bos
- [Effective Rust](https://effective-rust.com/) — David Drysdale

**工具**
- [Clippy lint 文档](https://rust-lang.github.io/rust-clippy/)
- [Miri](https://github.com/rust-lang/miri)

**用于学习 idioms 的真实代码库**
- ripgrep, tokio, serde, clap, polars, axum, cargo, hyper, bevy, rayon, 以及 dtolnay 的 crates (thiserror, anyhow, syn)

本项目采用 MIT 许可证。引用的上游材料保留其自身许可（官方 Rust 文档和 API Guidelines 采用 MIT / Apache-2.0 双重许可）。
