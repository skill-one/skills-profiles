**角色设定：** 你是一位 Go 工程师，将配置视为分层系统。标志（flag）优先于环境变量（env），环境变量优先于文件，文件优先于默认值——并且你为每个键绑定，使得所有四个层级都可以通过一个 API 访问。

# 使用 spf13/viper 在 Go 中实现分层配置

Viper 按照固定的优先级顺序从多个来源解析配置值。它没有用户界面——它不定义命令或标志。它的任务是回答“当前键 X 的值是什么？”通过从最高优先级到最低优先级遍历其来源层级。

**官方资源：**

- [pkg.go.dev/github.com/spf13/viper](https://pkg.go.dev/github.com/spf13/viper)
- [github.com/spf13/viper](https://github.com/spf13/viper)

这项技能并不详尽——请参考库文档和代码示例以获取更多信息：

- 对于 Go 包文档、符号、版本、导入者和已知漏洞，→ 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能（`godig`），优先于 Context7 以获取 Go 包事实。
- 要导航此库在你的代码中的使用（定义、调用位置、诊断），→ 查看 `samber/cc-skills-golang@golang-gopls` 技能（`gopls`）。
- Context7 仍然是一个后备选项，用于在 pkg.go.dev 上未索引的文档。

```bash
go get github.com/spf13/viper@latest
```

## Viper 与 Cobra 的比较

Cobra 拥有命令树——子命令、标志、参数验证、补全。Viper 拥有配置解析——它通过遍历其来源层级回答“键 X 的值是什么？”而没有自己的用户界面：它纯粹是一个键值解析器。

- **单独使用 Cobra** — 仅标志的 CLI。
- **单独使用 Viper** — 配置文件守护进程。
- **两者结合** — 通过 `PersistentPreRunE` 绑定标志（`BindPFlag`）。

→ 查看 `samber/cc-skills-golang@golang-spf13-cobra` 以获取此集成的 Cobra 部分。

## 优先级管道

Viper 通过按此顺序遍历来源解析键（第一个设置的值将胜出）：

```
1. 显式 Set()      — viper.Set("key", val)    最高优先级
2. 标志                — 绑定的 pflag.Flag
3. 环境变量             — BindEnv / AutomaticEnv
4. 配置文件             — ReadInConfig / MergeInConfig
5. KV 远程             — etcd / Consul
6. 默认                — viper.SetDefault("key", val)   最低优先级
```

此管道是固定的且不能重新排序。理解它可防止大多数 Viper 错误：一个“应该”来自配置文件的键可能会被环境变量或带有默认值的标志所覆盖。

## 来源和配置文件

```go
viper.SetConfigName("config")
viper.AddConfigPath("$HOME/.myapp")
if err := viper.ReadInConfig(); err != nil {
    var notFound *viper.ConfigFileNotFoundError
    if !errors.As(err, &notFound) {
        return fmt.Errorf("reading config: %w", err) // 仅传播真实错误
    }
}
```

`ConfigFileNotFoundError` 必须优雅地处理——配置文件通常是可选的。来自缺失文件的未处理错误会导致程序崩溃，而程序在仅使用标志或环境变量时完全有效。

对于支持格式（JSON、TOML、YAML、HCL、INI、properties）、`MergeInConfig` 和远程 KV，请参阅 [sources-and-formats.md](references/sources-and-formats.md)。

## 环境变量绑定和键替换器

这是 Viper 中最高错误密度区域。必须将所有三个设置连接在一起——缺少任何一个都会导致嵌套键解析失败：

```go
// ✓ 良好——在启动时将所有三个连接在一起
viper.SetEnvPrefix("MYAPP")                             // 防止冲突：PORT → MYAPP_PORT
viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))  // database.host → MYAPP_DATABASE_HOST
viper.AutomaticEnv()

// ✗ 不良——没有 SetEnvKeyReplacer，Viper 会查找 MYAPP_DATABASE.HOST（点被保留）
```

对于 `BindEnv`、`AllowEmptyEnv` 和环境变量与默认值交互，请参阅 [binding-and-env.md](references/binding-and-env.md)。

## 标志绑定（Cobra 的接口）

在 `init()` 或 `PersistentPreRunE` 中绑定 Cobra 标志到 Viper——绝不能在 `RunE` 中绑定（配置加载在 `PersistentPreRunE` 中已经运行在 `RunE` 之前，因此 `RunE` 中设置的绑定会被忽略）：

```go
func init() {
    rootCmd.PersistentFlags().Int("port", 8080, "listen port")
    viper.BindPFlag("port", rootCmd.PersistentFlags().Lookup("port"))
    // viper.BindPFlags(cmd.Flags()) — 一次性绑定整个 FlagSet
}
```

对于 `AllowEmptyEnv` 和标志/环境变量交互的详细信息，请参阅 [binding-and-env.md](references/binding-and-env.md)。

## 解析到结构体

`viper.Unmarshal` 使用 `mapstructure` 将解析的配置映射到结构体：

```go
type Config struct {
    Port     int `mapstructure:"port"`
    Database struct {
        MaxConn int `mapstructure:"max_conn"` // 显式标签：mapstructure 不会将下划线转换为驼峰式
    } `mapstructure:"database"`
}
var cfg Config
viper.Unmarshal(&cfg)
```

**始终使用 `mapstructure` 标签**——隐式映射对嵌套结构和下划线命名的字段很脆弱。优先使用 `UnmarshalKey("database", &dbCfg)` 而不是 `Sub("database").Unmarshal`——它避免了 `Sub` 在键缺失时所需的空值检查。

对于 `time.Duration` / `net.IP` / 切片解码器和自定义 `DecodeHook` 注册，请参阅 [unmarshal.md](references/unmarshal.md)。

## 子树

`viper.Sub("database")` 返回一个新的 `*viper.Viper`，其作用域为前缀，或者**如果键不存在则为 nil**——在调用结果上的方法之前始终进行 nil 检查。优先使用 `UnmarshalKey("database", &dbCfg)`，它可以完全避免 nil 风险。

## 热重载

```go
viper.WatchConfig()
viper.OnConfigChange(func(e fsnotify.Event) { /* 重新应用更改的值 */ })
```

`WatchConfig` 使用 fsnotify 并监视 inode，因此通过重命名原子写入的编辑器（vim、neovim）会替换 inode，回调可能不会触发。使用 `echo >> config.yaml` 而不是编辑器保存来测试热重载。对于线程安全的重载模式，请参阅 [watch-and-reload.md](references/watch-and-reload.md)。

## 测试隔离

**绝不要在测试中使用全局 viper**——状态会跨测试用例泄漏。为每个测试使用 `viper.New()` 以确保每个实例都是隔离的：

```go
v := viper.New()
v.SetConfigFile("testdata/config.yaml")
require.NoError(t, v.ReadInConfig())
```

对于 `t.Setenv` 交互和 `Reset()` 限制，请参阅 [testing-and-isolation.md](references/testing-and-isolation.md)。

## 最佳实践

1. **一起设置前缀 + 键替换器 + AutomaticEnv**——缺少任何一个会导致嵌套环境键无声不解析（`database.host` → `DATABASE.HOST` 而不是 `DATABASE_HOST`）。
2. **优雅地处理 `ConfigFileNotFoundError`**——缺失的配置文件不应导致仅使用标志和环境变量的服务崩溃。
3. **始终在配置结构体上使用 `mapstructure` 标签**——隐式映射会无声地忽略嵌套和下划线命名的字段。
4. **在测试中使用 `viper.New()`，绝不要使用全局**——全局会跨测试运行累积状态；每个测试的实例都是隔离的。
5. **在 `Execute()` 之前绑定标志**——在 `RunE` 中绑定太晚了；Cobra 在 `RunE` 运行之前解析标志。

## 常见错误

| 错误 | 为什么失败 | 修复 |
| --- | --- | --- |
| `AutomaticEnv` 而没有 `SetEnvKeyReplacer` | `database.host` 查找 `MYAPP_DATABASE.HOST`（点被保留）——永远不会匹配 | 在 `AutomaticEnv` 之前添加 `SetEnvKeyReplacer(strings.NewReplacer(".", "_"))` |
| 结构体字段没有 `mapstructure` 标签 | 无声地忽略嵌套和下划线命名的字段 | 为每个字段添加 `mapstructure:"key_name"` |
| 在测试中使用全局 viper | 一个测试的状态会污染下一个测试，导致顺序不稳定 | 每个测试创建 `viper.New()` |
| 缺失 `ConfigFileNotFoundError` 检查 | 缺失的配置文件会导致应该仅使用标志/环境变量运行的服务崩溃 | `errors.As(err, &notFound)` — 仅传播非未找到错误 |

## 进一步阅读

- [sources-and-formats.md](references/sources-and-formats.md) — 支持的文件格式、多路径搜索、`MergeInConfig`、远程 KV（etcd/Consul）
- [binding-and-env.md](references/binding-and-env.md) — `BindEnv`、`AutomaticEnv`、`SetEnvPrefix`、`SetEnvKeyReplacer`、`AllowEmptyEnv`、时间规则
- [unmarshal.md](references/unmarshal.md) — `Unmarshal`、`UnmarshalKey`、`mapstructure` 标签、自定义 `DecodeHooks`（Duration、IP、切片）
- [watch-and-reload.md](references/watch-and-reload.md) — `WatchConfig`、`OnConfigChange`、fsnotify 陷阱、原子重命名陷阱、线程安全模式
- [testing-and-isolation.md](references/testing-and-isolation.md) — 每个测试使用 `viper.New()`、`t.Setenv` 交互、`Reset()` 限制、快照/恢复

## 跨参考

- → 查看 `samber/cc-skills-golang@golang-cli` 技能以获取一般 CLI 架构——项目布局、退出代码、信号处理、cobra+viper 集成
- → 查看 `samber/cc-skills-golang@golang-spf13-cobra` 技能以获取此集成的 Cobra 部分（标志定义和绑定）
- → 查看 `samber/cc-skills-golang@golang-testing` 技能以获取一般 Go 测试模式

如果你在 spf13/viper 中遇到错误或意外行为，请打开问题 <https://github.com/spf13/viper/issues>。
