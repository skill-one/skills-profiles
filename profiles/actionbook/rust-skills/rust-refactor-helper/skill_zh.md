# Rust 重构助手

执行安全的重构，并具有全面的影響分析。

## 使用方法

```
/rust-refactor-helper <操作> <目标> [--dry-run]
```

**操作：**
- `rename <旧名> <新名>` - 重命名符号
- `extract-fn <选择范围>` - 提取到函数
- `inline <函数>` - 内联函数
- `move <符号> <目标模块>` - 移动到模块

**示例：**
- `/rust-refactor-helper rename parse_config load_config`
- `/rust-refactor-helper extract-fn src/main.rs:20-35`
- `/rust-refactor-helper move UserService src/services/`

## 使用的 LSP 操作

### 重构前的分析

```
# 在重命名前查找所有引用
LSP(
  operation: "findReferences",
  filePath: "src/lib.rs",
  line: 25,
  character: 8
)

# 获取符号信息
LSP(
  operation: "hover",
  filePath: "src/lib.rs",
  line: 25,
  character: 8
)

# 检查移动操作中的调用层次结构
LSP(
  operation: "incomingCalls",
  filePath: "src/lib.rs",
  line: 25,
  character: 8
)
```

## 重构工作流

### 1. 重命名符号

```
用户: "将 parse_config 重命名为 load_config"
    │
    ▼
[1] 查找符号定义
    LSP(goToDefinition)
    │
    ▼
[2] 查找所有引用
    LSP(findReferences)
    │
    ▼
[3] 按文件分类
    │
    ▼
[4] 检查冲突
    - 'load_config' 是否已被使用？
    - 是否有宏生成的使用？
    │
    ▼
[5] 显示影響分析 (--dry-run)
    │
    ▼
[6] 使用编辑工具应用更改
```

**输出：**

```
## 重命名：parse_config → load_config

### 影響分析

**定义位置：** src/config.rs:25
**找到的引用：** 8

| 文件 | 行号 | 上下文 | 变更 |
|------|------|---------|------|
| src/config.rs | 25 | `pub fn parse_config(` | 定义 |
| src/config.rs | 45 | `parse_config(path)?` | 调用 |
| src/main.rs | 12 | `config::parse_config` | 导入 |
| src/main.rs | 30 | `let cfg = parse_config(` | 调用 |
| src/lib.rs | 8 | `pub use config::parse_config` | 重新导出 |
| tests/config_test.rs | 15 | `parse_config("test.toml")` | 测试 |
| tests/config_test.rs | 25 | `parse_config("")` | 测试 |
| docs/api.md | 42 | `parse_config` | 文档 |

### 潜在问题

⚠️ **文档引用：** docs/api.md:42 可能需要手动更新
⚠️ **重新导出：** src/lib.rs:8 - 公共 API 变更

### 继续？
- [x] --dry-run (仅预览)
- [ ] 应用更改
```

### 2. 提取函数

```
用户: "将 main.rs 中的 20-35 行提取到函数"
    │
    ▼
[1] 读取选定的代码块
    │
    ▼
[2] 分析变量
    - 哪些是输入？(在代码块中使用但未在块中定义)
    - 哪些是输出？(在块中定义并在块后使用)
    - 哪些是局部变量？(在块中定义且仅在块中使用)
    │
    ▼
[3] 确定函数签名
    │
    ▼
[4] 检查早期返回、循环等
    │
    ▼
[5] 生成提取的函数
    │
    ▼
[6] 用调用替换原始代码
```

**输出：**

```
## 提取函数：src/main.rs:20-35

### 选定的代码
​```rust
let file = File::open(&path)?;
let mut contents = String::new();
file.read_to_string(&mut contents)?;
let config: Config = toml::from_str(&contents)?;
validate_config(&config)?;
​```

### 分析

**输入：** path: &Path
**输出：** config: Config
**副作用：** 文件 I/O，可能返回错误

### 提取的函数

​```rust
fn load_and_validate_config(path: &Path) -> Result<Config> {
    let file = File::open(path)?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    let config: Config = toml::from_str(&contents)?;
    validate_config(&config)?;
    Ok(config)
}
​```

### 替换

​```rust
let config = load_and_validate_config(&path)?;
​```
```

### 3. 移动符号

```
用户: "将 UserService 移动到 src/services/"
    │
    ▼
[1] 查找符号及其所有依赖项
    │
    ▼
[2] 查找所有引用（调用者）
    LSP(findReferences)
    │
    ▼
[3] 分析需要的导入变更
    │
    ▼
[4] 检查循环依赖
    │
    ▼
[5] 生成移动计划
```

**输出：**

```
## 移动：UserService → src/services/user.rs

### 当前位置
src/handlers/auth.rs:50-120

### 依赖项（将一起移动）
- struct UserService (50-80)
- impl UserService (82-120)
- const DEFAULT_TIMEOUT (48)

### 需要的导入变更

| 文件 | 当前 | 新 |
|------|------|----|
| src/main.rs | `use handlers::auth::UserService` | `use services::user::UserService` |
| src/handlers/api.rs | `use super::auth::UserService` | `use crate::services::user::UserService` |
| tests/auth_test.rs | `use crate::handlers::auth::UserService` | `use crate::services::user::UserService` |

### 新的文件结构

​```
src/
├── services/
│   ├── mod.rs (NEW - 添加 `pub mod user;`)
│   └── user.rs (NEW - UserService 移动到这里)
├── handlers/
│   └── auth.rs (UserService 已移除)
​```

### 循环依赖检查
✅ 未检测到循环依赖
```

## 安全检查

| 检查 | 目的 |
|------|------|
| 引用完整性 | 确保找到所有使用 |
| 名称冲突 | 检测同名的现有符号 |
| 可见性变更 | 如果 pub/private 范围变更则警告 |
| 宏生成的代码 | 警告宏中的代码 |
| 文档 | 标记提及符号的文档注释 |
| 测试覆盖率 | 显示受影响的测试 |

## Dry Run 模式

始终首先使用 `--dry-run` 预览更改：

```
/rust-refactor-helper rename old_name new_name --dry-run
```

这会显示所有更改但不会应用它们。

## 相关技能

| 当... | 查看 |
|------|------|
| 导航到符号 | rust-code-navigator |
| 理解调用流程 | rust-call-graph |
| 项目结构 | rust-symbol-analyzer |
| 特质实现 | rust-trait-explorer |
