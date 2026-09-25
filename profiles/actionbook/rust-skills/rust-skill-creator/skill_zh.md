# Rust技能创建器

> **版本:** 2.1.0 | **最后更新:** 2025-01-27
>
> 为Rust crate和std库文档创建动态技能。

## 使用场景

此技能处理创建技能的请求：
- 第三方crate（tokio、serde、axum等）
- Rust标准库（std::sync、std::marker等）
- 任何Rust文档URL

## 执行模式检测

**关键：检查相关命令/技能是否可用。**

此技能依赖于：
- `/create-llms-for-skills`命令
- `/create-skills-via-llms`命令

---

## 代理模式（插件安装）

**当上述命令可用（完整插件安装）时：**

### 工作流程

#### 1. 识别目标

| 用户请求 | 目标类型 | URL模式 |
|----------|----------|----------|
| "创建tokio技能" | 第三方crate | `docs.rs/tokio/latest/tokio/` |
| "创建Send特征技能" | 标准库 | `doc.rust-lang.org/std/marker/trait.Send.html` |
| "从URL创建技能" + URL | 自定义URL | 用户提供的URL |

#### 2. 执行命令

使用`/create-llms-for-skills`命令：

```
/create-llms-for-skills <url> [要求]
```

**示例：**

```bash
# 对于第三方crate
/create-llms-for-skills https://docs.rs/tokio/latest/tokio/

# 对于标准库
/create-llms-for-skills https://doc.rust-lang.org/std/marker/trait.Send.html

# 带有特定要求
/create-llms-for-skills https://docs.rs/axum/latest/axum/ "专注于路由和提取器"
```

#### 3. 随后进行技能创建

生成llms.txt后，使用：

```
/create-skills-via-llms <crate_name> <llms_path> [版本]
```

---

## 内联模式（仅技能安装）

**当上述命令不可用时，手动创建技能：**

### 第一步：识别目标并构建URL

| 目标 | URL模板 |
|------|----------|
| Crate概述 | `https://docs.rs/{crate}/latest/{crate}/` |
| Crate模块 | `https://docs.rs/{crate}/latest/{crate}/{module}/` |
| Std特征 | `https://doc.rust-lang.org/std/{module}/trait.{Name}.html` |
| Std结构 | `https://doc.rust-lang.org/std/{module}/struct.{Name}.html` |
| Std模块 | `https://doc.rust-lang.org/std/{module}/index.html` |

### 第二步：获取文档

```bash
# 使用agent-browser CLI
agent-browser open "<documentation_url>"
agent-browser get text ".docblock"
agent-browser close
```

**或使用WebFetch回退：**
```
WebFetch("<documentation_url>", "提取API文档，包括类型、函数和示例")
```

### 第三步：创建技能目录

```bash
mkdir -p ~/.claude/skills/{crate_name}
mkdir -p ~/.claude/skills/{crate_name}/references
```

### 第四步：生成SKILL.md

使用此模板创建`~/.claude/skills/{crate_name}/SKILL.md`：

```markdown
---
name: {crate_name}
description: "文档化{crate_name} crate。关键词: {keywords}"
---

# {Crate Name}

> **版本:** {version} | **来源:** docs.rs

## 概述

{从文档中提取的简短描述}

## 关键类型

### {Type1}
{描述和使用方式}

### {Type2}
{描述和使用方式}

## 常见模式

{从文档中提取的使用模式}

## 示例

```rust
{来自文档的示例代码}
```

## 文档

- `./references/overview.md` - 主要概述
- `./references/{module}.md` - 模块文档

## 链接

- [docs.rs](https://docs.rs/{crate})
- [crates.io](https://crates.io/crates/{crate})
```

### 第五步：生成参考文件

为每个主要模块或类型创建参考文件：

```bash
# 获取并保存模块文档
agent-browser open "https://docs.rs/{crate}/latest/{crate}/{module}/"
agent-browser get text ".docblock" > ~/.claude/skills/{crate_name}/references/{module}.md
agent-browser close
```

### 第六步：验证技能

```bash
# 检查技能结构
ls -la ~/.claude/skills/{crate_name}/
cat ~/.claude/skills/{crate_name}/SKILL.md
```

---

## URL构建辅助工具

| 目标 | URL模板 |
|------|----------|
| Crate概述 | `https://docs.rs/{crate}/latest/{crate}/` |
| Crate模块 | `https://docs.rs/{crate}/latest/{crate}/{module}/` |
| Std特征 | `https://doc.rust-lang.org/std/{module}/trait.{Name}.html` |
| Std结构 | `https://doc.rust-lang.org/std/{module}/struct.{Name}.html` |
| Std模块 | `https://doc.rust-lang.org/std/{module}/index.html` |

## 常见标准库路径

| 项目 | 路径 |
|------|------|
| Send、Sync、Copy、Clone | `std/marker/trait.{Name}.html` |
| Arc、Mutex、RwLock | `std/sync/struct.{Name}.html` |
| Rc、Weak | `std/rc/struct.{Name}.html` |
| RefCell、Cell | `std/cell/struct.{Name}.html` |
| Box | `std/boxed/struct.Box.html` |
| Vec | `std/vec/struct.Vec.html` |
| String | `std/string/struct.String.html` |
| Option | `std/option/enum.Option.html` |
| Result | `std/result/enum.Result.html` |

---

## 示例交互

### 示例1：创建Crate技能（代理模式）

```
用户: "创建一个tokio的动态技能"

Claude:
1. 识别：第三方crate "tokio"
2. 执行：/create-llms-for-skills https://docs.rs/tokio/latest/tokio/
3. 等待llms.txt生成
4. 执行：/create-skills-via-llms tokio ~/tmp/{timestamp}-tokio-llms.txt
```

### 示例2：创建Crate技能（内联模式）

```
用户: "创建一个tokio的动态技能"

Claude:
1. 识别：第三方crate "tokio"
2. 获取：agent-browser open "https://docs.rs/tokio/latest/tokio/"
3. 提取文档
4. 创建：~/.claude/skills/tokio/SKILL.md
5. 创建：~/.claude/skills/tokio/references/
6. 为关键模块（sync、task、runtime等）保存参考文件
```

### 示例3：创建标准库技能

```
用户: "为Send和Sync特征创建技能"

Claude:
1. 识别：标准库特征
2. (代理模式) 执行：/create-llms-for-skills https://doc.rust-lang.org/std/marker/trait.Send.html https://doc.rust-lang.org/std/marker/trait.Sync.html
   (内联模式) 获取每个URL，手动创建技能
3. 完成技能创建
```

---

## 禁止事项

- 不要使用`best-skill-creator`进行Rust相关技能创建
- 不要在未验证的情况下猜测文档URL
- 不要跳过文档获取步骤

## 输出位置

所有生成的技能保存到：`~/.claude/skills/`

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 命令未找到 | 技能仅安装 | 使用内联模式 |
| URL未找到 | 无效的crate/module | 验证crate是否存在于crates.io |
| 空文档 | API变更 | 使用替代选择器 |
| 权限被拒绝 | 目录问题 | 检查`~/.claude/skills/`权限 |
