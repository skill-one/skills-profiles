# 修复错误

修复 warp Rust 代码库中的编译错误、代码风格检查问题和测试失败。

## 概述

此功能有助于解决开发过程中遇到的常见问题，包括：
- 编译错误（未使用的导入、类型不匹配等）
- 代码风格检查失败（clippy 警告）
- 格式化违规
- 特定于 WASM 的错误
- 测试失败

使用最窄的有用命令修复报告的失败。不要将有针对性的修复转换为重复的完整工作区验证。

## 完整的预提交检查

仅在用户、任务或批准的规范明确要求时运行完整的预提交检查：

```bash
./script/presubmit
```

这会运行格式化检查、代码风格检查和所有测试。它有意比默认实现工作流程更广泛、更昂贵。

### 单独检查

在调试特定问题时单独运行检查：

**Rust 格式化：**
```bash
cargo fmt -- --check
```

**Clippy（完整工作区）：**
```bash
cargo clippy --workspace --all-targets --tests -- -D warnings
```

**WASM Clippy：**
```bash
cargo clippy --target wasm32-unknown-unknown --profile release-wasm-debug_assertions --no-deps
```

**Objective-C/C/C++ 格式化：**
```bash
./script/run-clang-format.py -r --extensions 'c,h,cpp,m' ./crates/warpui/src/ ./app/src/
```

**所有测试：**
```bash
cargo nextest run --no-fail-fast --workspace --exclude command-signatures-v2
cargo nextest run -p warp_completer --features v2
```

**文档测试：**
```bash
cargo test --doc
```

## 运行特定测试

**单个包：**
```bash
cargo nextest run -p <package_name>
```

**按测试名称过滤：**
```bash
cargo nextest run -E 'test(<substring>)'
```

**特定包带过滤：**
```bash
cargo nextest run -p <package_name> -E 'test(<substring>)'
```

**带输出（不捕获）：**
```bash
cargo nextest run -p <package> --nocapture
```

## 常见错误类型

### 未使用的导入
删除编译器识别的未使用 `use` 语句。

### 未使用的常量
删除定义但未使用的常量。

### 未知的导入
为未定义的类型添加正确的 `use` 语句。搜索代码库以找到正确的模块路径。

### 类型不匹配
更新函数调用以传递正确类型的参数。常见修复方法：
- 当期望 `&str` 时，使用 `.as_str()` 而不是 `.clone()`
- 当需要引用时，使用 `&value`
- 当期望 `String` 但提供了 `&str` 时，使用 `.to_string()`

### 结构体字段变更
当结构体添加/删除字段时，更新所有构造或解构它的地方：
- 结构体初始化
- 模式匹配（`match`、`if let`）
- 解构赋值

### 函数签名变更
当函数添加新参数时，更新所有调用位置以提供新参数：
- 对于 `bool` 参数：根据上下文传递 `true` 或 `false`
- 对于 `Option<T>` 参数：默认传递 `None` 或在需要时传递 `Some(value)`

### 枚举变体变更
当添加新枚举变体时，更新穷尽性 `match` 语句：
- 添加新的匹配分支并适当处理
- 模仿类似变体的实现模式

### 不正确的特质实现
修复返回错误类型或不满足特质约束的特质实现。

### 特定于 WASM 的错误

WASM 构建（`wasm32-unknown-unknown` 目标）不支持文件系统操作。使用文件系统 API 的代码必须通过 `local_fs` 特性标志进行控制。

**常见的 WASM 错误：**
- 仅在非 WASM 构建中使用的代码的未使用代码警告
- 仅在 `local_fs` 可用时相关的未使用代码
- 需要文件系统访问的测试

**修复方法：**

**将测试限制在 `local_fs`：**
```rust
#[test]
#[cfg(feature = "local_fs")]
fn test_find_git_repo_with_worktree() {
    // 使用文件系统操作的测试
}
```

**为仅在 `local_fs` 启用时使用的类型有条件地允许未使用代码：**
```rust
#[cfg_attr(not(feature = "local_fs"), allow(dead_code))]
#[derive(Clone, EnumDiscriminants, Serialize)]
pub enum ExampleType {
    // 仅在 local_fs 启用时使用的变体
    Variant1,
    Variant2,
    Variant3,
}
```

WASM 错误是通过运行以下命令发现的：

```bash
cargo clippy --target wasm32-unknown-unknown --profile release-wasm-debug_assertions --no-deps
```

## 最佳实践

**修复前：**
- 阅读完整错误信息以了解根本原因
- 检查多个错误是否相关（修复一个可能解决其他问题）
- 对于特质/类型错误，验证预期的类型与实际类型是否一致
- 对于 WASM 错误，检查代码是否需要通过 `local_fs` 控制

**修复时：**
- 当有多个问题时，一次修复一种错误类型
- 当有助于解决编译器错误时，运行最小的适用 `cargo check`；不要在没有相关代码更改的情况下重复广泛检查
- 对于 WASM 错误，运行 WASM clippy 以验证修复
- 对于复杂更改，修复后运行相关测试

**修复后：**
- 运行相关的 `cargo nextest` 测试并修复代码直到通过
- 运行适用的 Clippy 调用并修复其发现；仅在修复实质性改变行为时才返回受影响的测试
- 所有其他代码更改完成后，运行一次 `./script/format`
- 格式化后不要重新运行测试或 Clippy，除非明确要求
- 如果仅修复了格式化失败且未进行行为性代码更改，仅重新运行格式化器
