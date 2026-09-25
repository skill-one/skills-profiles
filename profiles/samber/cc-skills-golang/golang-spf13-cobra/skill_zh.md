**角色设定：** 你是一位 Go CLI 工程师，正在构建让 Unix shell 感觉原生的命令树。你首先设计用户界面，然后为正确的钩子连接行为。

**模式：**

- **构建** — 从头开始创建新的 CLI：按顺序遵循命令树设置、钩子连接和标志部分。
- **扩展** — 向现有 CLI 添加子命令、标志或补全：首先读取当前的命令树，然后根据现有结构应用更改。
- **审查** — 审核现有的 CLI：检查常见错误表，验证 `RunE` 使用情况、`OutOrStdout()`、钩子链顺序和参数验证。

# 使用 spf13/cobra 构建 Go 中的 CLI 命令树

Cobra 是 Go CLI 应用的事实标准。它提供命令/子命令树、标志解析（通过 `pflag`）、参数验证、shell 补全生成和文档生成。它**不**处理配置层叠——那是 viper 的工作。

**官方资源：**

- [pkg.go.dev/github.com/spf13/cobra](https://pkg.go.dev/github.com/spf13/cobra)
- [github.com/spf13/cobra](https://github.com/spf13/cobra)
- [cobra.dev](https://cobra.dev)

这项技能并不详尽——请参考库文档和代码示例以获取更多信息：

- 对于 Go 包文档、符号、版本、导入者和已知漏洞，→ 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能（`godig`），优先于 Context7 以获取 Go 包事实。
- 要导航此库在你的代码中的使用（定义、调用位置、诊断），→ 查看 `samber/cc-skills-golang@golang-gopls` 技能（`gopls`）。
- Context7 仍然是未在 pkg.go.dev 上索引的文档的回退选项。

```bash
go get github.com/spf13/cobra@latest
```

## Cobra vs. viper

这些库执行的是根本不同的事情，并且可以独立使用。

| 关注点 | cobra | viper |
| --- | --- | --- |
| 拥有 | 命令树、标志、参数验证、补全 | 配置值解析 |
| 面向用户？ | 是——子命令、标志、帮助文本 | 否——纯粹是键值解析器 |
| 没有另一个？ | 是——仅需要标志的 CLI 只需要 cobra | 是——仅读取 YAML + 环境的守护进程只需要 viper |
| 集成缝隙 | 通过 `BindPFlag` 将 `pflag.Flag` 传递给 viper | 将 cobra 标志视为最高优先级层 |

**单独使用 cobra** 当你的二进制文件接受标志和参数，但不需要配置文件或环境解析时。**单独使用 viper** 当你有一个长时间运行的服务从 YAML + 环境读取配置且没有 CLI 子命令时。当你需要两者时使用——在根命令的 `PersistentPreRunE` 上绑定。

→ 查看 `samber/cc-skills-golang@golang-spf13-viper` 以获取此集成的 viper 部分。

## 命令树

每个 cobra CLI 都有一个根命令和零个或多个通过 `AddCommand` 注册的子命令。根命令的名称是二进制文件的名称。

```go
var rootCmd = &cobra.Command{
    Use:          "myapp",
    Short:        "一句话摘要",
    SilenceUsage: true,  // ✓ 防止每次错误时出现使用墙
    SilenceErrors: true, // ✓ 允许你控制错误输出格式
}
```

使用 `AddGroup` 在帮助输出中标记子命令——在引用它们的 `AddCommand` 调用之前注册组；cobra 不会事后分配组。

## Run\* 系列

Cobra 命令有五个按顺序执行的运行钩子：

```
PersistentPreRunE → PreRunE → RunE → PostRunE → PersistentPostRunE
```

始终使用 `*E` 变体——非 `E` 形式的变体不能返回错误。关键规则：

- 根命令上的 `PersistentPreRunE` 在**每个**子命令之前运行——用于配置初始化和身份验证检查。
- 子命令的 `PersistentPreRunE` **完全替换**父命令的——如果你需要两者，请显式调用父命令。
- `PostRunE` 仅在 `RunE` 成功时运行。

有关完整生命周期和继承规则，请参阅 [commands-and-args.md](references/commands-and-args.md)。

## 参数验证器

Cobra 在 `RunE` 运行之前验证位置参数。不要在 `RunE` 中编写 `len(args)` 检查——那样会绕过 cobra 的标准错误消息和参数计数跟踪。

内置：`NoArgs`、`ExactArgs(n)`、`MinimumNArgs(n)`、`MaximumNArgs(n)`、`RangeArgs(min,max)`、`OnlyValidArgs`、`ExactValidArgs(n)`。使用 `MatchAll(v1, v2)` 组合。自定义验证器：`func(cmd *cobra.Command, args []string) error`。

有关完整的验证器集、示例和 `MatchAll` 模式，请参阅 [commands-and-args.md](references/commands-and-args.md)。

## 标志入门

Cobra 将标志解析委托给 `pflag`。**持久标志**（`PersistentFlags()`）被所有子命令继承；**本地标志**（`Flags()`）仅适用于声明它们的命令。

```go
rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "配置文件路径") // 被所有子命令继承
serveCmd.Flags().IntVar(&port, "port", 8080, "监听端口")                     // 仅 serveCmd 的本地
serveCmd.MarkFlagRequired("port")
serveCmd.MarkFlagsMutuallyExclusive("json", "yaml")
```

有关 pflag 类型、自定义标志值、标志组和 viper 绑定，请参阅 [flags.md](references/flags.md)。

## 补全入门

Cobra 自动生成 shell 补全。通过以下方式扩展它们：

- **`ValidArgs []string`** — 静态位置参数补全。
- **`ValidArgsFunction`** — 动态：`func(cmd, args, toComplete string) ([]string, ShellCompDirective)`。返回 `ShellCompDirectiveNoFileComp` 以抑制文件回退。
- **`RegisterFlagCompletionFunc(name, fn)`** — 标志值补全。

有关 `ShellCompDirective` 值、注解和测试，请参阅 [completions.md](references/completions.md)。

## 测试命令

通过程序执行方式测试命令。**永远不要直接使用 `os.Stdout` / `os.Stderr`** 在命令处理程序中——使用 `cmd.OutOrStdout()` / `cmd.ErrOrStderr()` 以便测试可以重定向输出。

```go
func TestServeCmd(t *testing.T) {
    buf := new(bytes.Buffer)
    rootCmd.SetOut(buf)
    rootCmd.SetArgs([]string{"serve", "--port", "9090"})
    require.NoError(t, rootCmd.Execute())
    assert.Contains(t, buf.String(), "listening on :9090")
}
```

Cobra 在 `Execute()` 调用之间累积标志状态——为每个测试构建一个全新的命令树。有关隔离模式、黄金文件和测试补全，请参阅 [testing.md](references/testing.md)。

## 最佳实践

1. **始终使用 `RunE`，不要使用 `Run`** — `Run` 不能返回错误；唯一的退出方式是 `os.Exit` 或 panic，绕过 defer。
2. **将配置初始化放在 `PersistentPreRunE`** — 它在所有子命令之前运行；viper 绑定和身份验证检查的正确位置。
3. **使用 `Args` 而不是在 `RunE` 中验证位置参数** — `Args` 提供了 cobra 的标准错误消息；`MatchAll` 组合验证器。
4. **对所有输出使用 `cmd.OutOrStdout()` / `cmd.ErrOrStderr()`** — 直接 `os.Stdout` 写入无法被测试捕获。
5. **为每个测试重新创建命令树** — cobra 在同一实例的 `Execute()` 调用之间累积标志状态。

## 常见错误

| 错误 | 为什么失败 | 修复 |
| --- | --- | --- |
| 使用 `Run` 而不是 `RunE` | 不能返回错误——唯一的退出方式是 `os.Exit` 或 panic，绕过 defer | 使用 `RunE` — 返回错误，让 cobra 处理退出 |
| 在 `RunE` 中编写 `len(args)` 检查 | 绕过 cobra 的标准错误消息（“接受 1 个参数，收到 2 个”） | 在命令上声明 `Args: cobra.ExactArgs(1)` |
| 直接写入 `os.Stdout` | 测试无法捕获输出——os 级别的文件句柄无法重定向 | 使用 `cmd.OutOrStdout()` / `cmd.ErrOrStderr()` |
| 子命令的 `PersistentPreRunE` 悄然丢弃父命令的 | cobra 不链式——子命令完全替换父命令的钩子 | 在子命令的钩子中调用 `parent.PersistentPreRunE(cmd, args)` |
| 在测试中重用根命令 | cobra 累积标志状态；第二个 `Execute()` 看到第一个的标志 | 为每个测试构建一个全新的命令树 |

## 进一步阅读

- [commands-and-args.md](references/commands-and-args.md) — 完整的 PreRun\*/PostRun\* 链，每个 Args 验证器，PersistentPreRunE 继承规则
- [flags.md](references/flags.md) — pflag 类型，必须/互斥/一个必须组，自定义值类型，viper 绑定
- [completions.md](references/completions.md) — ShellCompDirective 集合，基于注解的补全，测试补全
- [generators.md](references/generators.md) — man 页面，markdown，YAML，RST 文档生成；`cobra-cli` 模板生成器
- [testing.md](references/testing.md) — 隔离模式，黄金文件，测试补全，表格驱动命令测试

## 跨参考

- → 查看 `samber/cc-skills-golang@golang-cli` 技能以获取通用 CLI 架构——项目布局，退出代码，信号处理，I/O 模式
- → 查看 `samber/cc-skills-golang@golang-spf13-viper` 技能以获取与 cobra 一起使用的配置层叠（标志 → 环境 → 文件 → 默认优先级）
- → 查看 `samber/cc-skills-golang@golang-testing` 技能以获取通用 Go 测试模式

如果你在 spf13/cobra 中遇到错误或意外行为，请 <https://github.com/spf13/cobra/issues> 打开问题。
