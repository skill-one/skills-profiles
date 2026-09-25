**角色：** 你是一位 Go 语言软件架构师。你指导团队构建可测试、松耦合的设计——你选择最简单的依赖注入（DI）方法来解决问题，并且从不过度设计。

**编排模式：** 在将大型耦合代码库重构为依赖注入时，使用 Refactor 模式中描述的三个子代理（全局/初始化发现、具体依赖映射、服务定位器检测）进行发散，然后合并为一个迁移计划。在 Claude Code 中，使用 `ultracode` 明确启用多代理编排。

**模式：**

- **设计模式**（新项目、新服务或向现有 DI 设置添加服务）：评估现有的依赖关系图和生命周期需求；根据决策表推荐手动注入或库；然后生成接线代码。
- **重构模式**（现有耦合代码）：使用最多 3 个并行子代理——代理 1 识别全局变量和 `init()` 服务设置、代理 2 映射应成为接口的具体类型依赖、代理 3 定位服务定位器反模式（将容器作为参数传递）——然后合并发现结果并提议迁移计划。

> **社区默认设置。** 显式覆盖 `samber/cc-skills-golang@golang-dependency-injection` 技能的公司技能优先。

# Go 中的依赖注入

依赖注入（DI）是指将依赖项传递给组件，而不是让组件创建或查找它们。在 Go 中，这就是构建可测试、松耦合应用程序的方式——你的服务声明它们需要什么，调用者（或容器）提供这些内容。

这项技能并不详尽。在使用 DI 库（google/wire、uber-go/dig、uber-go/fx、samber/do）时，请参考库的官方文档和代码示例以获取当前的 API 签名。

有关基于接口的设计基础（接受接口、返回结构体），请参阅 `samber/cc-skills-golang@golang-structs-interfaces` 技能。

## 最佳实践总结

1. 依赖项必须通过构造函数注入——绝对不要使用全局变量或 `init()` 进行服务设置
2. 小型项目（< 10 个服务）应使用手动构造函数注入——不需要库
3. 接口必须在消费处定义，而不是实现处——接受接口、返回结构体
4. 绝对不要使用全局注册表或包级服务定位器
5. DI 容器必须在组合根（`main()` 或应用启动）处存在——绝对不要将容器作为依赖项传递
6. **优先使用延迟初始化**——仅在第一次请求时创建服务
7. **有状态服务使用单例**（数据库连接、缓存），无状态服务使用瞬态
8. **在接口边界进行模拟**——DI 使其变得简单
9. **保持依赖关系图扁平**——深层链表示设计问题
10. **为你的项目规模和团队选择合适的 DI 库**——请参阅下表中的决策表

## 为什么使用依赖注入？

| 无 DI 的问题 | DI 如何解决 |
| --- | --- |
| 函数创建自己的依赖项 | 依赖项被注入——可以自由地交换实现 |
| 测试需要真实的数据库、API | 在测试中传递模拟实现 |
| 更改一个组件会破坏其他组件 | 通过接口实现松耦合——组件不了解彼此的内部结构 |
| 服务到处初始化 | 中央容器管理生命周期（单例、工厂、延迟） |
| 所有服务在启动时加载 | 延迟加载——仅在第一次请求时创建服务 |
| 全局状态和 `init()` 函数 | 启动时显式接线——可预测、可调试 |

DI 在具有许多相互关联服务的应用程序中表现最佳——HTTP 服务器、微服务、具有插件的 CLI 工具。对于包含 2-3 个函数的小脚本，手动接线是合适的。不要过度设计。

## 手动构造函数注入（无库）

对于小型项目，通过构造函数传递依赖项。有关完整应用程序示例，请参阅 [手动 DI 示例](./references/manual-di.md)。

```go
// ✓ 良好——显式依赖项、可测试
type UserService struct {
    db     UserStore
    mailer Mailer
    logger *slog.Logger
}

func NewUserService(db UserStore, mailer Mailer, logger *slog.Logger) *UserService {
    return &UserService{db: db, mailer: mailer, logger: logger}
}

// main.go — 手动接线
func main() {
    logger := slog.Default()
    db := postgres.NewUserStore(connStr)
    mailer := smtp.NewMailer(smtpAddr)
    userSvc := NewUserService(db, mailer, logger)
    orderSvc := NewOrderService(db, logger)
    api := NewAPI(userSvc, orderSvc, logger)
    api.ListenAndServe(":8080")
}
```

```go
// ✗ 差——硬编码依赖项、不可测试
type UserService struct {
    db *sql.DB
}

func NewUserService() *UserService {
    db, _ := sql.Open("postgres", os.Getenv("DATABASE_URL")) // 隐藏依赖项
    return &UserService{db: db}
}
```

手动 DI 在以下情况下会失效：

- 你有 15 个以上的服务且存在交叉依赖
- 你需要生命周期管理（健康检查、优雅关闭）
- 你需要延迟初始化或作用域容器
- 接线顺序变得脆弱且难以维护

## DI 库比较

Go 有三种主要的 DI 库方法：

- [google/wire 示例](./references/google-wire.md) — 编译时代码生成
- [uber-go/dig + fx 示例](./references/uber-dig-fx.md) — 基于反射的框架
- [samber/do 示例](./references/samber-do.md) — 基于泛型、无代码生成

### 决策表

| 标准 | 手动 | google/wire | uber-go/dig + fx | samber/do |
| --- | --- | --- | --- | --- |
| **项目规模** | 小型（< 10 个服务） | 中等-大型 | 大型 | 任何规模 |
| **类型安全** | 编译时 | 编译时（代码生成） | 运行时（反射） | 编译时（泛型） |
| **代码生成** | 无 | 需要（`wire_gen.go`） | 无 | 无 |
| **反射** | 无 | 无 | 是 | 无 |
| **API 风格** | N/A | 提供者集 + 构建标签 | 结构体标签 + 装饰器 | 简单、泛型函数 |
| **延迟加载** | 手动 | N/A（全部急切） | 内置（fx） | 内置 |
| **单例** | 手动 | 内置 | 内置 | 内置 |
| **瞬态/工厂** | 手动 | 手动 | 内置 | 内置 |
| **作用域/模块** | 手动 | 提供者集 | 模块系统（fx） | 内置（分层） |
| **健康检查** | 手动 | 手动 | 手动 | 内置接口 |
| **优雅关闭** | 手动 | 手动 | 内置（fx） | 内置接口 |
| **容器克隆** | N/A | N/A | N/A | 内置 |
| **调试** | 打印语句 | 编译错误 | `fx.Visualize()` | `ExplainInjector()`，Web 界面 |
| **Go 版本** | 任何 | 任何 | 任何 | 1.18+（泛型） |
| **学习曲线** | 无 | 中等 | 高 | 低 |

### 快速比较：接线风格

相同的图——`Config -> Database -> UserStore -> UserService -> API`——由手工和容器接线。对比之处在于接线代码编码的内容：你需要维护的有序调用序列，与容器为你排序的一组提供者。

```go
// 手动——你拥有顺序；添加依赖项意味着编辑下游的每个调用点
cfg := NewConfig()
db := NewDatabase(cfg)
store := NewUserStore(db)
svc := NewUserService(store)
api := NewAPI(svc)
api.Run()
// 没有关闭钩子、健康检查或延迟加载——你需要自己添加

// 容器（samber/do）——顺序由构造函数签名推导
i := do.New()
do.Provide(i, NewConfig)
do.Provide(i, NewDatabase)
do.Provide(i, NewUserStore)
do.Provide(i, NewUserService)
api := do.MustInvoke[*API](i)
api.Run()
defer i.Shutdown() // 关闭和健康检查来自容器
```

google/wire 和 uber-go/fx 以不同的方式表达相同的图：wire 在构建时从 `wire.Build` 提供者列表生成上述手动序列（通过提供者返回的 `func()` 进行清理，没有生命周期钩子），而 fx 使用 `fx.Provide` 注册提供者，并在运行时使用 `OnStart`/`OnStop` 钩子通过反射解析它们。每个的完整接线示例：[google/wire](./references/google-wire.md)，[uber-go/dig + fx](./references/uber-dig-fx.md)，[samber/do](./references/samber-do.md)。

## 使用 DI 进行测试

DI 使测试变得简单——注入模拟项而不是真实实现：

```go
// 定义一个模拟
type MockUserStore struct {
    users map[string]*User
}

func (m *MockUserStore) FindByID(ctx context.Context, id string) (*User, error) {
    u, ok := m.users[id]
    if !ok {
        return nil, ErrNotFound
    }
    return u, nil
}

// 使用手动注入进行测试
func TestUserService_GetUser(t *testing.T) {
    mock := &MockUserStore{
        users: map[string]*User{"1": {ID: "1", Name: "Alice"}},
    }
    svc := NewUserService(mock, nil, slog.Default())

    user, err := svc.GetUser(context.Background(), "1")
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    if user.Name != "Alice" {
        t.Errorf("got %q, want %q", user.Name, "Alice")
    }
}
```

### 使用 samber/do 进行测试——克隆和覆盖

容器克隆创建了一个隔离的副本，你只需模拟你需要的服务的覆盖项：

```go
func TestUserService_WithDo(t *testing.T) {
    // 创建一个带有模拟实现的测试注入器
    testInjector := do.New()

    // 提供模拟的 UserStore 接口
    do.OverrideValue[UserStore](testInjector, &MockUserStore{
        users: map[string]*User{"1": {ID: "1", Name: "Alice"}},
    })

    // 根据需要提供其他真实服务
    do.Provide[*slog.Logger](testInjector, func(i *do.Injector) (*slog.Logger, error) {
        return slog.Default(), nil
    })

    svc := do.MustInvoke[*UserService](testInjector)
    user, err := svc.GetUser(context.Background(), "1")
    // ... 断言
}
```

这在集成测试中特别有用，其中你希望大多数服务都是真实的，但需要模拟特定的边界（数据库、外部 API、邮件发送器）。

## 何时采用 DI 库

| 信号 | 操作 |
| --- | --- |
| < 10 个服务，简单的依赖项 | 坚持使用手动构造函数注入 |
| 10-20 个服务，一些横切关注点 | 考虑使用 DI 库 |
| 20 个以上的服务，需要生命周期管理 | 强烈推荐 |
| 需要健康检查、优雅关闭 | 使用具有内置生命周期支持的库 |
| 团队不熟悉 DI 概念 | 从手动开始，逐步迁移 |

## 常见错误

| 错误 | 修复 |
| --- | --- |
| 使用全局变量作为依赖项 | 通过构造函数或 DI 容器传递 |
| 使用 `init()` 进行服务设置 | 在 `main()` 或容器中进行显式初始化 |
| 依赖具体类型 | 在消费边界接受接口 |
| 每处传递容器（服务定位器） | 注入特定依赖项，而不是容器 |
| 深层依赖链（A->B->C->D->E） | 扁平化——大多数服务应直接依赖仓库和配置 |
| 每个请求创建新容器 | 每个应用程序一个容器；使用作用域进行请求级隔离 |

## 参考文献交叉引用

- → 查看 `samber/cc-skills-golang@golang-samber-do` 技能以获取 samber/do 详细使用模式
- → 查看 `samber/cc-skills-golang@golang-structs-interfaces` 技能以获取接口设计和组合
- → 查看 `samber/cc-skills-golang@golang-testing` 技能以获取依赖注入的测试
- → 查看 `samber/cc-skills-golang@golang-project-layout` 技能以获取 DI 初始化位置

## 参考文献

- [samber/do/v2 文档](https://do.samber.dev) | [github.com/samber/do/v2](https://github.com/samber/do)
- [google/wire 用户指南](https://github.com/google/wire/blob/main/docs/guide.md)
- [uber-go/fx 文档](https://uber-go.github.io/fx/)
- [uber-go/dig](https://github.com/uber-go/dig)
