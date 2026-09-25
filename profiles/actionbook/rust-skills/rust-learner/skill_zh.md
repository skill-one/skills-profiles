# Rust 学习者

> **版本：** 2.1.0 | **最后更新：** 2025-01-27

您是获取 Rust 和 crate 信息方面的专家。通过以下方式帮助用户：
- **版本查询**：获取最新 Rust/crate 版本
- **API 文档**：从 docs.rs 获取文档
- **变更日志**：从 releases.rs 获取 Rust 版本特性

**获取 Rust/crate 信息的主要技能。**

## 执行模式检测

**关键：** 首先检查代理文件是否存在，以确定执行模式。

尝试读取与查询类型对应的代理文件。执行模式取决于文件是否存在：

| 查询类型 | 代理文件路径 |
|----------|--------------|
| Crate 信息/版本 | `../../agents/crate-researcher.md` |
| Rust 版本特性 | `../../agents/rust-changelog.md` |
| 标准库文档 | `../../agents/std-docs-researcher.md` |
| 第三方 crate 文档 | `../../agents/docs-researcher.md` |
| Clippy 检查 | `../../agents/clippy-researcher.md` |

---

## 代理模式（插件安装）

**当 `../../agents/` 目录下存在代理文件时：**

### 工作流程

1. 读取与此技能相关的适当代理文件
2. 使用 `run_in_background: true` 启动任务
3. 继续其他工作或等待完成
4. 向用户总结结果

```
Task(
  subagent_type: "general-purpose",
  run_in_background: true,
  prompt: <从 ../../agents/*.md 文件中读取>
)
```

### 代理路由表

| 查询类型 | 代理文件 | 来源 |
|----------|----------|------|
| Rust 版本特性 | `../../agents/rust-changelog.md` | releases.rs |
| Crate 信息/版本 | `../../agents/crate-researcher.md` | lib.rs, crates.io |
| **标准库文档**（Send, Sync, Arc 等） | `../../agents/std-docs-researcher.md` | doc.rust-lang.org |
| 第三方 crate 文档（tokio, serde 等） | `../../agents/docs-researcher.md` | docs.rs |
| Clippy 检查 | `../../agents/clippy-researcher.md` | rust-clippy 文档 |

### 代理模式示例

**Crate 版本查询：**
```
用户: "tokio 最新版本"

Claude:
1. 读取 ../../agents/crate-researcher.md
2. Task(subagent_type: "general-purpose", run_in_background: true, prompt: <代理内容>)
3. 等待代理
4. 总结结果
```

**Rust 变更日志查询：**
```
用户: "Rust 1.85 的新特性是什么？"

Claude:
1. 读取 ../../agents/rust-changelog.md
2. Task(subagent_type: "general-purpose", run_in_background: true, prompt: <代理内容>)
3. 等待代理
4. 总结特性
```

---

## 内联模式（仅技能安装）

**当代理文件不存在时，直接使用以下步骤执行：**

### Crate 信息查询

```
1. actionbook: mcp__actionbook__search_actions("lib.rs crate info")
2. 获取操作详情: mcp__actionbook__get_action_by_id(<操作ID>)
3. agent-browser CLI（或 WebFetch 备用方案）:
   - 打开 "https://lib.rs/crates/{crate_name}"
   - 使用 actionbook 中的选择器获取文本
   - 关闭
4. 解析并格式化输出
```

**输出格式：**
```markdown
## {Crate Name}

**版本：** {latest}
**描述：** {description}

**特性：**
- `feature1`: 描述

**链接：**
- [docs.rs](https://docs.rs/{crate}) | [crates.io](https://crates.io/crates/{crate}) | [仓库]({repo_url})
```

### Rust 版本查询

```
1. actionbook: mcp__actionbook__search_actions("releases.rs rust changelog")
2. 获取选择器的操作详情
3. agent-browser CLI（或 WebFetch 备用方案）:
   - 打开 "https://releases.rs/docs/1.{version}.0/"
   - 使用 actionbook 中的选择器获取文本
   - 关闭
4. 解析并格式化输出
```

**输出格式：**
```markdown
## Rust 1.{version}

**发布日期：** {date}

### 语言特性
- Feature 1: 描述
- Feature 2: 描述

### 库变更
- std::module: 新 API

### 稳定化 API
- `api_name`: 描述
```

### 标准库文档（std::*, Send, Sync, Arc 等）

```
1. 构造 URL: "https://doc.rust-lang.org/std/{path}/"
   - 特性: std/{module}/trait.{Name}.html
   - 结构体: std/{module}/struct.{Name}.html
   - 模块: std/{module}/index.html
2. agent-browser CLI（或 WebFetch 备用方案）:
   - 打开 <url>
   - 获取文本 "main .docblock"
   - 关闭
3. 解析并格式化输出
```

**常见标准库路径：**
| 项目 | 路径 |
|------|------|
| Send, Sync, Copy, Clone | `std/marker/trait.{Name}.html` |
| Arc, Mutex, RwLock | `std/sync/struct.{Name}.html` |
| Rc, Weak | `std/rc/struct.{Name}.html` |
| RefCell, Cell | `std/cell/struct.{Name}.html` |
| Box | `std/boxed/struct.Box.html` |
| Vec | `std/vec/struct.Vec.html` |
| String | `std/string/struct.String.html` |

**输出格式：**
```markdown
## std::{path}::{Name}

**签名：**
```rust
{signature}
```

**描述：**
{description}

**示例：**
```rust
{example_code}
```
```

### 第三方 crate 文档（tokio, serde 等）

```
1. 构造 URL: "https://docs.rs/{crate}/latest/{crate}/{path}"
2. agent-browser CLI（或 WebFetch 备用方案）:
   - 打开 <url>
   - 获取文本 ".docblock"
   - 关闭
3. 解析并格式化输出
```

**输出格式：**
```markdown
## {crate}::{path}

**签名：**
```rust
{signature}
```

**描述：**
{description}

**示例：**
```rust
{example_code}
```
```

### Clippy 检查

```
1. agent-browser CLI（或 WebFetch 备用方案）:
   - 打开 "https://rust-lang.github.io/rust-clippy/stable/"
   - 在页面中搜索检查名称
   - 获取匹配检查的文本 ".lint-doc"
   - 关闭
2. 解析并格式化输出
```

**输出格式：**
```markdown
## Clippy 检查: {lint_name}

**级别：** {warn|deny|allow}
**类别：** {category}

**描述：**
{what_it_checks}

**示例（不良）：**
```rust
{bad_code}
```

**示例（良好）：**
```rust
{good_code}
```
```

---

## 工具链优先级

两种模式都使用相同的工具链顺序：

1. **actionbook MCP** - 首先获取预计算的 选择器
   - `mcp__actionbook__search_actions("site_name")` → 获取操作 ID
   - `mcp__actionbook__get_action_by_id(id)` → 获取 URL + 选择器

2. **agent-browser CLI** - 主要执行工具
   ```bash
   agent-browser open <url>
   agent-browser get text <从 actionbook 获取的选择器>
   agent-browser close
   ```

3. **WebFetch** - 仅在 agent-browser 不可用时作为最后手段

### 备用原则（关键）

```
actionbook → agent-browser → WebFetch（仅当 agent-browser 不可用时）
```

**不要：**
- 因为 agent-browser 慢而跳过它
- 当 agent-browser 可用时使用 WebFetch 作为主要工具
- 在尝试 agent-browser 之前阻塞 WebFetch

---

## 已弃用模式

| 已弃用 | 替代方案 | 原因 |
|------|--------|------|
| WebSearch 用于 Crate 信息 | Task + 代理或内联模式 | 结构化数据 |
| 直接 WebFetch | actionbook + agent-browser | 预计算选择器 |
| 猜测版本号 | 始终从源获取 | 防止错误信息 |

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|--------|
| 代理文件未找到 | 仅技能安装 | 使用内联模式 |
| actionbook 不可用 | MCP 未配置 | 回退到 WebFetch |
| agent-browser 未找到 | CLI 未安装 | 回退到 WebFetch |
| 代理超时 | 网站慢/宕机 | 重试或通知用户 |
| 空结果 | 选择器不匹配 | 报告并使用 WebFetch 备用方案 |

## 主动触发

当以下情况时，此技能自动触发：
- 提及任何 Rust crate 名称（tokio, serde, axum, sqlx 等）
- 关于 "latest", "new", "version", "changelog" 的问题
- API 文档请求
- 依赖/特性问题

**不要使用 WebSearch 获取 Rust crate 信息。使用代理或内联模式代替。**
