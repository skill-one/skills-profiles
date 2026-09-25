# Rust符号分析器

通过检查Rust代码库中的符号来分析项目结构。

## 使用方法

```
/rust-symbol-analyzer [file.rs] [--type struct|trait|fn|mod]
```

**示例：**
- `/rust-symbol-analyzer` - 分析整个项目
- `/rust-symbol-analyzer src/lib.rs` - 分析单个文件
- `/rust-symbol-analyzer --type trait` - 列出项目中的所有特性

## LSP操作

### 1. 文档符号（单个文件）

获取文件中的所有符号及其层次结构。

```
LSP(
  operation: "documentSymbol",
  filePath: "src/lib.rs",
  line: 1,
  character: 1
)
```

**返回：** 模块、结构体、函数等的嵌套结构

### 2. 工作区符号（整个项目）

跨工作区搜索符号。

```
LSP(
  operation: "workspaceSymbol",
  filePath: "src/lib.rs",
  line: 1,
  character: 1
)
```

**注意：** 查询隐含在操作上下文中

## 工作流程

```
用户: "这个项目的结构是什么？"
    │
    ▼
[1] 查找所有Rust文件
    Glob("**/*.rs")
    │
    ▼
[2] 从每个关键文件获取符号
    LSP(documentSymbol) for lib.rs, main.rs
    │
    ▼
[3] 按类型分类
    │
    ▼
[4] 生成结构可视化
```

## 输出格式

### 项目概述

```
## 项目结构: my-project

### 模块
├── src/
│   ├── lib.rs (根)
│   ├── config/
│   │   ├── mod.rs
│   │   └── parser.rs
│   ├── handlers/
│   │   ├── mod.rs
│   │   ├── auth.rs
│   │   └── api.rs
│   └── models/
│       ├── mod.rs
│       ├── user.rs
│       └── order.rs
└── tests/
    └── integration.rs
```

### 按符号类型

```
## 按类型分类的符号

### 结构体 (12)
| 名称 | 位置 | 字段 | 派生 |
|------|------|------|------|
| Config | src/config.rs:10 | 5 | Debug, Clone |
| User | src/models/user.rs:8 | 4 | Debug, Serialize |
| Order | src/models/order.rs:15 | 6 | Debug, Serialize |
| ... | | | |

### 特性 (4)
| 名称 | 位置 | 方法 | 实现 |
|------|------|------|------|
| Handler | src/handlers/mod.rs:5 | 3 | AuthHandler, ApiHandler |
| Repository | src/db/mod.rs:12 | 5 | UserRepo, OrderRepo |
| ... | | | |

### 函数 (25)
| 名称 | 位置 | 可见性 | 异步 |
|------|------|--------|------|
| main | src/main.rs:10 | pub | 是 |
| parse_config | src/config.rs:45 | pub | 否 |
| ... | | | |

### 枚举 (6)
| 名称 | 位置 | 变体 |
|------|------|------|
| Error | src/error.rs:5 | 8 |
| Status | src/models/order.rs:5 | 4 |
| ... | | |
```

### 单文件分析

```
## src/handlers/auth.rs

### 符号层次结构

mod auth
├── struct AuthHandler
│   ├── 字段: config: Config
│   ├── 字段: db: Pool
│   └── 实现 AuthHandler
│       ├── 函数 new(config, db) -> Self
│       ├── 函数 authenticate(&self, token) -> Result<User>
│       └── 函数 refresh_token(&self, user) -> Result<Token>
├── struct Token
│   ├── 字段: value: String
│   └── 字段: expires: DateTime
├── enum AuthError
│   ├── InvalidToken
│   ├── Expired
│   └── Unauthorized
└── 实现 Handler for AuthHandler
    ├── 函数 handle(&self, req) -> Response
    └── 函数 name(&self) -> &str
```

## 分析功能

### 复杂度指标

```
## 复杂度分析

| 文件 | 结构体 | 函数 | 行数 | 复杂度 |
|------|--------|------|------|--------|
| src/handlers/auth.rs | 2 | 8 | 150 | 中等 |
| src/models/user.rs | 3 | 12 | 200 | 高 |
| src/config.rs | 1 | 3 | 50 | 低 |

**热点：** 复杂度高的文件可能需要重构
- src/handlers/api.rs (15个函数, 300行)
```

### 依赖分析

```
## 内部依赖

auth.rs
├── 从: config.rs, models/user.rs, db/mod.rs 导入
└── 被: main.rs, handlers/mod.rs 导入

user.rs
├── 从: (无 - 叶模块)
└── 被: auth.rs, api.rs, tests/ 导入
```

## 符号类型

| 类型 | 图标 | LSP类型 |
|------|------|--------|
| 模块 | 📦 | 模块 |
| 结构体 | 🏗️ | 结构体 |
| 枚举 | 🔢 | 枚举 |
| 特性 | 📜 | 接口 |
| 函数 | ⚡ | 函数 |
| 方法 | 🔧 | 方法 |
| 常量 | 🔒 | 常量 |
| 字段 | 📎 | 字段 |

## 常见查询

| 用户输入 | 分析 |
|---------|------|
| "这个项目中有哪些结构体？" | workspaceSymbol + 过滤 |
| "显示 src/lib.rs 结构" | documentSymbol |
| "查找所有异步函数" | workspaceSymbol + 异步过滤 |
| "列出公共API" | documentSymbol + pub过滤 |

## 相关技能

| 当... | 查看 |
|------|------|
| 导航到符号 | rust-code-navigator |
| 调用关系 | rust-call-graph |
| 特性实现 | rust-trait-explorer |
| 安全重构 | rust-refactor-helper |
