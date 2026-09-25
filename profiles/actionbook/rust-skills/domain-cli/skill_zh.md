# 命令行界面域

> **第 3 层：域约束**

## 域约束 → 设计影响

| 域规则 | 设计约束 | Rust 影响 |
|-------------|-------------------|------------------|
| 用户易用性 | 清晰的帮助信息、错误信息 | clap derive 宏 |
| 配置优先级 | 命令行 > 环境变量 > 文件 | 分层配置加载 |
| 退出代码 | 出错时非零 | Proper Result 处理 |
| 标准输出/标准错误 | 数据与错误区分 | eprintln! 用于错误 |
| 可中断性 | 处理 Ctrl+C | 信号处理 |

---

## 关键约束

### 用户通信

```
规则：错误输出到 stderr，数据输出到 stdout
原因：可管道化输出，脚本化能力
Rust：eprintln! 用于错误，println! 用于数据
```

### 配置优先级

```
规则：命令行参数 > 环境变量 > 配置文件 > 默认值
原因：用户预期，覆盖能力
Rust：使用 clap + figment/config 实现分层配置
```

### 退出代码

```
规则：任何错误都返回非零退出码
原因：脚本集成，自动化
Rust：main() -> Result<(), Error> 或显式 exit()
```

---

## 向下追踪 ↓

从约束到设计（第 2 层）：

```
"需要参数解析"
    ↓ m05-type-driven：为参数派生结构体
    ↓ clap：#[derive(Parser)]

"需要配置分层"
    ↓ m09-domain：配置作为域对象
    ↓ figment/config：分层来源

"需要进度显示"
    ↓ m12-lifecycle：进度条作为 RAII
    ↓ indicatif：ProgressBar
```

---

## 关键 Crate

| 目的 | Crate |
|---------|-------|
| 参数解析 | clap |
| 交互式提示 | dialoguer |
| 进度条 | indicatif |
| 带颜色的输出 | colored |
| 终端 UI | ratatui |
| 终端控制 | crossterm |
| 控制台工具 | console |

## 设计模式

| 模式 | 目的 | 实现 |
|---------|---------|----------------|
| Args 结构体 | 类型安全的参数 | `#[derive(Parser)]` |
| 子命令 | 命令层级 | `#[derive(Subcommand)]` |
| 配置层级 | 覆盖优先级 | 命令行 > 环境变量 > 文件 |
| 进度 | 用户反馈 | `ProgressBar::new(len)` |

## 代码模式：命令行结构

```rust
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "myapp", about = "我的命令行工具")]
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

| 错误 | 域违规 | 修复 |
|---------|-----------------|-----|
| 错误输出到 stdout | 破坏管道 | eprintln! |
| 无帮助文本 | 差的 UX | #[arg(help = "...")] |
| 错误时崩溃 | 坏的退出码 | Result + 正确处理 |
| 长操作无进度 | 用户不确定 | indicatif |

---

## 向第 1 层追踪

| 约束 | 第 2 层模式 | 第 1 层实现 |
|------------|-----------------|------------------------|
| 类型安全的参数 | 派生宏 | clap Parser |
| 错误处理 | Result 传播 | anyhow + 退出码 |
| 用户反馈 | 进度 RAII | indicatif ProgressBar |
| 配置优先级 | 构建者模式 | 分层来源 |

---

## 相关技能

| 当... | 查看 |
|------|-----|
| 错误处理 | m06-error-handling |
| 类型驱动参数 | m05-type-driven |
| 进度生命周期 | m12-lifecycle |
| 异步命令行 | m07-concurrency |
