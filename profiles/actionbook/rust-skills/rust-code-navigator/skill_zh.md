# Rust 代码导航器

使用语言服务器协议高效导航大型 Rust 代码库。

## 使用方法

```
/rust-code-navigator <符号> [在文件.rs:行号]
```

**示例：**
- `/rust-code-navigator parse_config` - 查找 parse_config 的定义
- `/rust-code-navigator MyStruct 在 src/lib.rs:42` - 从特定位置导航

## LSP 操作

### 1. 跳转到定义

查找符号定义的位置。

```
LSP(
  operation: "goToDefinition",
  filePath: "src/main.rs",
  line: 25,
  character: 10
)
```

**使用场景：**
- 用户询问 "X 在哪里定义？"
- 用户想理解某个类型/函数
- Ctrl+点击等效操作

### 2. 查找引用

查找符号的所有使用位置。

```
LSP(
  operation: "findReferences",
  filePath: "src/lib.rs",
  line: 15,
  character: 8
)
```

**使用场景：**
- 用户询问 "谁在使用 X？"
- 重构/重命名之前
- 理解变更影响

### 3. 悬停信息

获取符号的类型和文档。

```
LSP(
  operation: "hover",
  filePath: "src/main.rs",
  line: 30,
  character: 15
)
```

**使用场景：**
- 用户询问 "X 的类型是什么？"
- 用户需要文档
- 快速类型检查

## 工作流程

```
用户: "Config 结构体在哪里定义？"
    │
    ▼
[1] 在工作区搜索 "Config"
    LSP(operation: "workspaceSymbol", ...)
    │
    ▼
[2] 如果有多个结果，要求用户澄清
    │
    ▼
[3] 跳转到定义
    LSP(operation: "goToDefinition", ...)
    │
    ▼
[4] 显示文件路径和上下文
    读取周围代码获取上下文
```

## 输出格式

### 找到定义

```
## Config (结构体)

**定义于：** `src/config.rs:15`

​```rust
#[derive(Debug, Clone)]
pub struct Config {
    pub name: String,
    pub port: u16,
    pub debug: bool,
}
​```

**文档：** 应用服务器配置。
```

### 找到引用

```
## 对 `Config` 的引用 (共 5 个)

| 位置 | 上下文 |
|------|--------|
| src/main.rs:10 | `let config = Config::load()?;` |
| src/server.rs:25 | `fn new(config: Config) -> Self` |
| src/server.rs:42 | `self.config.port` |
| src/tests.rs:15 | `Config::default()` |
| src/cli.rs:8 | `config: Option<Config>` |
```

## 常见模式

| 用户说法 | LSP 操作 |
|----------|----------|
| "X 在哪里定义？" | goToDefinition |
| "谁在使用 X？" | findReferences |
| "X 的类型是什么？" | hover |
| "查找所有结构体" | workspaceSymbol |
| "这个文件有什么内容？" | documentSymbol |

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| "没有 LSP 服务器" | rust-analyzer 未运行 | 建议：`rustup component add rust-analyzer` |
| "符号未找到" | 拼写错误或不在作用域内 | 先使用 workspaceSymbol 搜索 |
| "多个定义" | 泛型或宏 | 显示所有结果并让用户选择 |

## 相关技能

| 场景 | 相关工具 |
|------|----------|
| 调用关系 | rust-call-graph |
| 项目结构 | rust-symbol-analyzer |
| 特性实现 | rust-trait-explorer |
| 安全重构 | rust-refactor-helper |
