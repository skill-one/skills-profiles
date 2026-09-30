---
name: domain-cli
description: 在构建命令行工具时使用。关键词：命令行界面（CLI）、命令行、终端、clap、structopt、参数解析、子命令、交互式、文本用户界面（TUI）、ratatui、crossterm、indicatif、进度条、彩色输出、shell自动补全、配置文件、环境变量、命令行、终端应用、参数解析
---

# CLI 领域

> **第 3 层：领域约束**

## 领域约束 → 设计影响

| 领域规则 | 设计约束 | Rust 影响 |
|-------------|-------------------|------------------|
| 用户易用性 | 清晰的帮助信息、错误提示 | clap 派生宏 |
| 配置优先级 | CLI > 环境变量 > 文件 | 分层配置加载 |
| 退出码 | 出错时返回非零值 | 正确的 Result 处理 |
| 标准输出/标准错误 | 数据与错误分离 | 使用 eprintln! 输出错误 |
| 可中断性 | 处理 Ctrl+C | 信号处理 |

---

## 关键约束

### 用户通信

```
规则：错误输出到 stderr，数据输出到 stdout
原因：支持管道传输、可脚本化
Rust：错误使用 eprintln!，数据使用 println!
```

### 配置优先级

```
规则：CLI 参数 > 环境变量 > 配置文件 > 默认值
原因：符合用户预期、支持覆盖
Rust：使用 clap + figment/config 实现分层配置
```

### 退出码

```
规则：任何错误都返回非零值
原因：脚本集成、自动化
Rust：main() -> Result<(), Error> 或显式 exit()
```

---

## 向下追溯 ↓

从约束到设计（第 2 层）：

```
“需要参数解析”
    ↓ m05-type-driven：为参数派生结构体
    ↓ clap：#[derive(Parser)]

“需要配置分层”
    ↓ m09-domain：将配置视为领域对象
    ↓ figment/config：分层数据源

“需要进度显示”
    ↓ m12-lifecycle：进度条作为 RAII
    ↓ indicatif：ProgressBar
```

---

## 关键 crate

| 用途 | Crate |
|---------|-------|
| 参数解析 | clap |
| 交互式提示 | dialoguer |
| 进度条 | indicatif |
| 彩色输出 | colored |
| 终端 UI | ratatui |
| 终端控制 | crossterm |
| 控制台工具 | console |

## 设计模式

| 模式 | 用途 | 实现 |
|---------|---------|----------------|
| 参数结构体 | 类型安全的参数 | `#[derive(Parser)]` |
| 子命令 | 命令层级 | `#[derive(Subcommand)]` |
| 配置层 | 覆盖优先级 | CLI > env > file |
| 进度 | 用户反馈 | `ProgressBar::new(len)` |

## 代码模式：CLI 结构

```rust
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "myapp", about = "My CLI tool")]
struct Cli {
    /// 启用详细输出
    #[arg(short, long)]
    verbose: bool,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// 初始化新项目
    Init { name: String },
    /// 运行应用程序
    Run {
        #[arg(short, long)]
        port: Option<u16>,
    },
}

fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();
    match cli.command {
        Commands::Init { name } => init_project(&name)?,
        Commands::Run { port } => run_server(port.unwrap_or(8080))?,
    }
    Ok(())
}
```

---

## 常见错误

| 错误 | 领域违规 | 修复方法 |
|---------|-----------------|-----|
| 错误输出到 stdout | 破坏管道功能 | eprintln! |
| 无帮助文本 | 用户体验差 | #[arg(help = "...")] |
| 出错时 panic | 退出码不当 | Result + 正确处理 |
| 长操作无进度提示 | 用户状态不明 | indicatif |

---

## 追溯至第 1 层

| 约束 | 第 2 层模式 | 第 1 层实现 |
|------------|-----------------|------------------------|
| 类型安全参数 | 派生宏 | clap Parser |
| 错误处理 | Result 传播 | anyhow + 退出码 |
| 用户反馈 | 进度 RAII | indicatif ProgressBar |
| 配置优先级 | 建造者模式 | 分层数据源 |

---

## 相关技能

| 场景 | 参见 |
|------|-----|
| 错误处理 | m06-error-handling |
| 类型驱动参数 | m05-type-driven |
| 进度生命周期 | m12-lifecycle |
| 异步 CLI | m07-concurrency |
