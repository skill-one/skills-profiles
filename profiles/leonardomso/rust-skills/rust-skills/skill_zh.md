# Rust 最佳实践

一份编写高质量、符合规范且高度优化的 Rust 代码的全面指南。包含 265 条规则，分为 26 个类别，按影响程度排序，以指导大型语言模型在代码生成和重构中的使用。适用于 Rust 1.96 版本（2024 年版）。

## 应用场景

在以下情况下参考这些指南：
- 编写新的 Rust 函数、结构体或模块
- 实现错误处理或异步代码
- 编写并发、并行或 `unsafe` 代码
- 设计库的公共 API
- 审查代码的所有权/借用问题
- 优化内存使用或减少分配
- 调整热点路径的性能
- 重构现有的 Rust 代码

## 按优先级排序的规则类别

| 优先级 | 类别 | 影响 | 前缀 | 规则数量 |
|--------|------|------|------|-------|
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
| 25 | Clippy & 代码检查 | 低 | `lint-` | 13 |
| 26 | 反模式 | 参考 | `anti-` | 15 |

---

## 推荐的 Cargo.toml 设置

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
opt-level = 3  # 开发环境中优化依赖项
```

---

## 使用方法

此技能提供规则标识符，以便快速参考。在生成或审查 Rust 代码时：

1. **根据任务类型检查相关类别**
2. **应用具有匹配前缀的规则**
3. **优先级：关键 > 高 > 中 > 低**
4. **阅读 `rules/` 中的规则文件以获取详细示例**

### 按任务应用规则

| 任务 | 主要类别 |
|------|-------------------|
| 新函数 | `own-`, `err-`, `name-`, `pat-` |
| 新结构体/API | `api-`, `type-`, `conv-`, `doc-` |
| 异步代码 | `async-`, `own-` |
| 并发 / 并行 | `conc-`, `async-`, `own-` |
| 不安全代码 | `unsafe-`, `type-`, `test-` |
| 错误处理 | `err-`, `api-`, `pat-` |
| 类型转换 | `conv-`, `api-` |
| 序列化 (serde) | `serde-`, `type-`, `api-` |
| 数值 / 算术 | `num-`, `type-` |
| 宏 / 代码生成 | `macro-`, `anti-` |
| 闭包 / 回调 | `closure-`, `type-` |
| 日志 / 可观察性 | `obs-`, `err-` |
| 内存优化 | `mem-`, `own-`, `perf-` |
| 性能调优 | `opt-`, `mem-`, `perf-` |
| 代码审查 | `anti-`, `lint-` |

---

## 来源与归属

此技能是对官方 Rust 指导、知名书籍和广泛使用的 crate 中的模式进行独立综合的结果。它与 Rust 项目或任何 crate 作者没有关联，文本和代码示例均为原创。

**官方 Rust 文档**
- [Rust 参考](https://doc.rust-lang.org/reference/)
- [Rust API 指南](https://rust-lang.github.io/api-guidelines/)
- [Rustonomicon](https://doc.rust-lang.org/nomicon/)（不安全代码）
- [Rust 2024 版本指南](https://doc.rust-lang.org/edition-guide/rust-2024/)
- [Cargo 书籍](https://doc.rust-lang.org/cargo/)
- [标准库文档](https://doc.rust-lang.org/std/) 和 [发布说明](https://doc.rust-lang.org/releases.html)

**书籍 & 指南**
- [Rust 性能书籍](https://nnethercote.github.io/perf-book/) — Nicholas Nethercote
- [Rust 设计模式](https://rust-unofficial.github.io/patterns/) — rust-unofficial
- [Rust 原子与锁](https://marabos.nl/atomics/) — Mara Bos
- [Effective Rust](https://effective-rust.com/) — David Drysdale

**工具**
- [Clippy 代码检查文档](https://rust-lang.github.io/rust-clippy/)
- [Miri](https://github.com/rust-lang/miri)

**研究过的现实世界代码库以获取惯用法**
- ripgrep, tokio, serde, clap, polars, axum, cargo, hyper, bevy, rayon, 以及 dtolnay 的 crates（thiserror, anyhow, syn）

本项目采用 MIT 许可证。引用的上游材料保留其自身许可（官方 Rust 文档和 API 指南采用 MIT / Apache-2.0 双重许可）。
