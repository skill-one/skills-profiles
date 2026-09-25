**角色：** 你是一位 Go CLI 工程师。你构建的工具能让 Unix shell 感觉原生，具有可组合性、可脚本化和自动化下的可预测性。

**模式：**

- **构建** — 从零创建一个新的 CLI：按顺序遵循项目结构、根命令设置、标志绑定和版本嵌入部分。
- **扩展** — 向现有的 CLI 添加子命令、标志或补全：首先阅读当前的命令树，然后根据现有结构应用一致的变化。
- **审查** — 审核现有 CLI 的正确性：检查常见错误表，验证 `SilenceUsage`/`SilenceErrors`、标志到 Viper 的绑定、退出码和 stdout/stderr 的规范。

# Go CLI 最佳实践

将 Cobra + Viper 作为 Go CLI 应用的默认技术栈。Cobra 提供命令/子命令/标志结构，Viper 处理来自文件、环境变量和标志的配置，并自动分层。这个组合驱动了 kubectl、docker、gh、hugo 以及大多数生产环境下的 Go CLI。

使用 Cobra 或 Viper 时，参考库的官方文档和代码示例以获取当前的 API 签名。

对于简单的单用途工具，没有子命令且标志较少，stdlib `flag` 足够。

## 快速参考

| 关注点             | 包/工具                       |
| ------------------- | ------------------------------------ |
| 命令 & 标志    | `github.com/spf13/cobra`             |
| 配置       | `github.com/spf13/viper`             |
| 标志解析        | `github.com/spf13/pflag` (通过 Cobra) |
| 带颜色的输出      | `github.com/fatih/color`             |
| 表格输出        | `github.com/olekukonko/tablewriter`  |
| 交互式提示 | `github.com/charmbracelet/bubbletea` |
| 版本注入   | `go build -ldflags`                  |
| 发布        | `goreleaser`                         |

## 项目结构

在 `cmd/myapp/` 中组织 CLI 命令，每个命令一个文件。保持 `main.go` 最小 — 它只调用 `Execute()`。

```
myapp/
├── cmd/
│   └── myapp/
│       ├── main.go              # 包名 main，只调用 Execute()
│       ├── root.go              # 根命令 + Viper 初始化
│       ├── serve.go             # "serve" 子命令
│       ├── migrate.go           # "migrate" 子命令
│       └── version.go           # "version" 子命令
├── go.mod
└── go.sum
```

`main.go` 应保持最小 — 查看 [assets/examples/main.go](assets/examples/main.go)。

## 根命令设置

根命令初始化 Viper 配置并通过 `PersistentPreRunE` 设置全局行为。查看 [assets/examples/root.go](assets/examples/root.go)。

要点：

- `SilenceUsage: true` 必须设置 — 防止每次错误时打印完整的使用文本
- `SilenceErrors: true` 必须设置 — 允许你控制错误输出格式
- `PersistentPreRunE` 在每个子命令之前运行，因此配置始终被初始化
- 日志输出到 stderr，输出到 stdout

## 子命令

通过在 `cmd/myapp/` 中创建单独的文件并在 `init()` 中注册它们来添加子命令。查看 [assets/examples/serve.go](assets/examples/serve.go) 获取包含命令组的完整子命令示例。

## 标志

查看 [assets/examples/flags.go](assets/examples/flags.go) 获取所有标志模式：

### 持久化 vs 本地

- **持久化** 标志被所有子命令继承（例如，`--config`）
- **本地** 标志仅适用于定义它们的命令（例如，`--port`）

### 必填标志

使用 `MarkFlagRequired`、`MarkFlagsMutuallyExclusive` 和 `MarkFlagsOneRequired` 进行标志约束。

### 使用 RegisterFlagCompletionFunc 进行标志验证

为标志值提供补全建议。

### 始终将标志绑定到 Viper

这确保 `viper.GetInt("port")` 返回标志值、环境变量 `MYAPP_PORT` 或配置文件值 — 优先级最高的值。

## 参数验证

Cobra 提供内置验证器用于位置参数。查看 [assets/examples/args.go](assets/examples/args.go) 获取内置和自定义验证示例。

| 验证器                   | 描述                          |
| --------------------------- | ------------------------------------ |
| `cobra.NoArgs`              | 如果提供任何参数则失败           |
| `cobra.ExactArgs(n)`        | 需要恰好 n 个参数              |
| `cobra.MinimumNArgs(n)`     | 至少需要 n 个参数             |
| `cobra.MaximumNArgs(n)`     | 允许最多 n 个参数                |
| `cobra.RangeArgs(min, max)` | 需要在 min 和 max 之间         |
| `cobra.ExactValidArgs(n)`   | 恰好 n 个参数，必须在 ValidArgs |

## 使用 Viper 进行配置

Viper 按照以下顺序解析配置值（从高到低优先级）：

1. **CLI 标志**（显式用户输入）
2. **环境变量**（部署配置）
3. **配置文件**（持久化设置）
4. **默认值**（代码中设置）

查看 [assets/examples/config.go](assets/examples/config.go) 获取完整的 Viper 集成，包括结构反序列化和配置文件监视。

### 示例配置文件 (.myapp.yaml)

```yaml
port: 8080
host: localhost
log-level: info
database:
  dsn: postgres://localhost:5432/myapp
  max-conn: 25
```

在上述设置中，所有这些都是等价的：

- 标志：`--port 9090`
- 环境变量：`MYAPP_PORT=9090`
- 配置文件：`port: 9090`

## 版本和构建信息

版本应在编译时使用 `ldflags` 嵌入。查看 [assets/examples/version.go](assets/examples/version.go) 获取版本命令和构建说明。

## 退出码

退出码必须遵循 Unix 惯例：

| 代码  | 含义           | 使用场景                               |
| ----- | ----------------- | ----------------------------------------- |
| 0     | 成功           | 操作正常完成                          |
| 1     | 一般错误     | 运行时失败                           |
| 2     | 使用错误       | 无效标志或参数                |
| 64-78 | BSD sysexits      | 特定错误类别                 |
| 126   | 无法执行    | 权限被拒绝                         |
| 127   | 命令未找到 | 缺少依赖                        |
| 128+N | 信号 N          | 被信号终止（例如，130 = SIGINT） |

查看 [assets/examples/exit_codes.go](assets/examples/exit_codes.go) 获取将错误映射到退出码的模式。

## I/O 模式

查看 [assets/examples/output.go](assets/examples/output.go) 获取所有 I/O 模式：

- **stdout vs stderr**：绝对不要将诊断输出写入 stdout — stdout 用于程序输出（可管道），stderr 用于日志/错误/诊断
- **检测管道 vs 终端**：检查 `os.ModeCharDevice` 在 stdout 上
- **机器可读输出**：支持 `--output` 标志以获取表格/JSON/纯文本格式
- **颜色**：使用 `fatih/color`，当输出不是终端时自动禁用

## 信号处理

信号处理必须使用 `signal.NotifyContext` 将取消通过上下文传播。查看 [assets/examples/signal.go](assets/examples/signal.go) 获取优雅的 HTTP 服务器关闭。

## Shell 补全

Cobra 自动为 bash、zsh、fish 和 PowerShell 生成补全。查看 [assets/examples/completion.go](assets/examples/completion.go) 获取补全命令和自定义标志/参数补全。

## 测试 CLI 命令

通过程序执行命令并捕获输出来测试命令。查看 [assets/examples/cli_test.go](assets/examples/cli_test.go)。

在命令中使用 `cmd.OutOrStdout()` 和 `cmd.ErrOrStderr()`（而不是 `os.Stdout` / `os.Stderr`），以便在测试中捕获输出。

## 常见错误

| 错误 | 修复 |
| --- | --- |
| 直接写入 `os.Stdout` | 测试无法捕获输出。使用 `cmd.OutOrStdout()`，测试可以重定向到缓冲区 |
| 在 `RunE` 中调用 `os.Exit()` | Cobra 的错误处理、延迟函数和清理代码不会运行。返回错误，让 `main()` 决定 |
| 未将标志绑定到 Viper | 标志无法通过环境/配置进行配置。为每个可配置的标志调用 `viper.BindPFlag` |
| 缺少 `viper.SetEnvPrefix` | `PORT` 与其他工具冲突。使用前缀（`MYAPP_PORT`）为环境变量命名空间化 |
| 向 stdout 写日志 | Unix 管道链 stdout — 日志会破坏下一个程序的 数据流。日志写入 stderr |
| 每次错误都打印使用信息 | 每次错误都显示完整帮助文本是噪音。设置 `SilenceUsage: true`，将完整使用信息保留在 `--help` |
| 需要配置文件 | 没有配置文件的用戶会崩溃。忽略 `viper.ConfigFileNotFoundError` — 配置应该是可选的 |
| 未使用 `PersistentPreRunE` | 配置初始化必须在任何子命令之前发生。使用根的 `PersistentPreRunE` |
| 硬编码版本字符串 | 版本与标签不同步。通过构建时的 git 标签从 `ldflags` 注入 |
| 未支持 `--output` 格式 | 脚本无法解析人类可读的输出。添加 JSON/表格/纯文本以供机器消费 |

## 相关技能

查看 `samber/cc-skills-golang@golang-project-layout`、`samber/cc-skills-golang@golang-dependency-injection`、`samber/cc-skills-golang@golang-testing`、`samber/cc-skills-golang@golang-design-patterns` 技能。
