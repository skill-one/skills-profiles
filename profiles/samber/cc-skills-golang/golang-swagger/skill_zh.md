**角色：** 你是一个 Go API 文档工程师。你将文档视为一份合同——准确的、完整的注释可以防止集成错误，并使 Swagger UI 成为 API 消费者的权威来源。

**模式：**

- **构建** — 向新或现有的 Go 项目添加 Swagger：设置工具链、注释处理器、生成文档、连接 UI 端点。
- **审计** — 审查现有的 swagger 注释，确保其完整性、正确性和安全覆盖范围。

**依赖项：**

- swag: `go install github.com/swaggo/swag/cmd/swag@latest`

## 设置

启动 Swagger UI 的三个步骤：

```bash
swag init                        # 生成 docs/ 目录，包含 docs.go、swagger.json、swagger.yaml
swag init -g cmd/api/main.go     # 如果通用信息不在 main.go 中
swag fmt                         # 格式化注释（类似于 go fmt）
```

导入 `docs` 包以注册规范。使用空导入仅连接 UI；使用命名导入当你还需要在运行时覆盖 `docs.SwaggerInfo` 时：

```go
import _ "yourmodule/docs"          // 空的：注册规范，无标识符
import docs "yourmodule/docs"       // 命名的：在覆盖 SwaggerInfo 时使用
```

连接 UI 端点——选择你的框架：

```go
// Gin
r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

// Echo
e.GET("/swagger/*", echoSwagger.WrapHandler)

// Fiber
app.Get("/swagger/*", fiberSwagger.WrapHandler(swaggerFiles.Handler))

// net/http
mux.Handle("/swagger/", httpSwagger.Handler(swaggerFiles.Handler))

// Chi
r.Get("/swagger/*", httpSwagger.Handler(swaggerFiles.Handler))
```

在 `/swagger/index.html` 访问 UI。

对于动态主机/基本路径（多环境），使用命名导入并在服务前覆盖：

```go
import docs "yourmodule/docs"

docs.SwaggerInfo.Host     = os.Getenv("API_HOST")
docs.SwaggerInfo.BasePath = "/api/v1"
```

[完整的 CLI 参考](references/swag-cli.md)

## 通用 API 信息

放在 `main.go`（或通过 `-g` 传递的文件）。这些注释定义了顶层规范：

```go
// @title           我的 API
// @version         1.0
// @description     API 的简短描述。
// @host            localhost:8080
// @BasePath        /api/v1
// @schemes         http https

// @contact.name    API 支持
// @contact.email   support@example.com
// @license.name    Apache 2.0

// @securityDefinitions.apikey Bearer
// @in header
// @name Authorization
// @description 类型为 "Bearer"，后跟一个空格和 JWT 令牌。
```

## 操作注释

注释每个处理器函数。标准文档注释 (`// FuncName godoc`) 必须位于 swag 注释之前——它为 `swag fmt` 锚定了缩进。

```go
// ShowAccount godoc
// @Summary      根据 ID 获取账户
// @Description  返回给定 ID 的账户详细信息。
// @Tags         账户
// @Accept       json
// @Produce      json
// @Param        id      path  int  true  "账户 ID"
// @Param        filter  query string false "可选的搜索过滤器"
// @Success      200  {object}  model.Account
// @Success      204  "无内容"
// @Failure      400  {object}  api.ErrorResponse
// @Failure      404  {object}  api.ErrorResponse
// @Router       /accounts/{id} [get]
// @Security     Bearer
func ShowAccount(c *gin.Context) {}
```

**@Param** 格式：`@Param <name> <in> <type> <required> "<description>" [attributes]`

| `<in>`     | 用法                                |
| ---------- | ------------------------------------ |
| `path`     | URL 路径段 (`/users/{id}`)     |
| `query`    | URL 查询字符串 (`?filter=x`)       |
| `body`     | 请求体——类型必须为结构体 |
| `header`   | HTTP 头部                          |
| `formData` | 多部分/表单字段                 |

`@Param` 的可选属性：`default(v)`、`minimum(n)`、`maximum(n)`、`minLength(n)`、`maxLength(n)`、`Enums(a,b,c)`、`example(v)`、`collectionFormat(multi)`。

**@Success/@Failure** 格式：`@Success <code> {<kind>} <type> "<description>"`

| `<kind>`             | 当...时             |
| -------------------- | ---------------- |
| `{object}`           | 单个结构体    |
| `{array}`            | 结构体切片 |
| `string` / `integer` | 基本类型        |

**泛型**（swag v2）：`@Success 200 {object} api.Response[model.User]`

**嵌套组合**：`@Success 200 {object} api.Response{data=model.User}`

## 安全定义

在 API 级别（在 main.go 中）一次性定义，通过 `@Security` 每个端点应用。

```go
// Bearer / JWT
// @securityDefinitions.apikey Bearer
// @in header
// @name Authorization

// API 密钥在头部
// @securityDefinitions.apikey ApiKeyAuth
// @in header
// @name X-API-Key

// Basic 认证
// @securityDefinitions.basic BasicAuth

// OAuth2 授权码
// @securityDefinitions.oauth2.authorizationCode OAuth2
// @authorizationUrl https://example.com/oauth/authorize
// @tokenUrl https://example.com/oauth/token
// @scope.read 读取权限
// @scope.write 写入权限
```

应用于端点：

```go
// @Security Bearer
// @Security OAuth2[read, write]
// @Security BasicAuth && ApiKeyAuth   // AND — 两者都必需
```

## 结构体标签

在不改变 Go 类型的情况下丰富模型：

```go
type CreateUserRequest struct {
    Name   string `json:"name" example:"Jane Doe" minLength:"2" maxLength:"100"`
    Role   string `json:"role" enums:"admin,user,guest" example:"user"`
    Age    int    `json:"age" minimum:"18" maximum:"120"`
    Avatar []byte `json:"avatar" swaggertype:"string" format:"base64"`
    Secret string `json:"-" swaggerignore:"true"`  // 排除文档
}
```

| 标签 | 目的 |
| --- | --- |
| `example` | 示例值在 Swagger UI 中显示 |
| `enums` | 允许值，逗号分隔 |
| `swaggertype` | 覆盖检测到的类型（例如，`"primitive,integer"` 用于 `time.Time`） |
| `swaggerignore:"true"` | 从生成的模式中排除字段 |
| `extensions` | 添加 OpenAPI 扩展：`extensions:"x-nullable,x-deprecated=true"` |

## 常见错误

| 错误 | 为什么会破坏 | 修复 |
| --- | --- | --- |
| 缺少 `_ "yourmodule/docs"` 导入 | 模式未注册；UI 加载为空 | 在 main.go 或服务器初始化中添加空导入 |
| 代码更改后 `docs/` 过期 | 文档与实现脱节；消费者获得错误的模式 | 每次注释更改后重新运行 `swag init` |
| `@Param body` 使用基本类型 | swag 无法从 `string` 推导模式；生成失败 | 始终使用命名的结构体作为 body 参数 |
| 保护路由上没有 `@Security` | Swagger UI 显示没有锁图标；测试者发送未认证的请求 | 对每个认证端点应用 `@Security` |
| 通用信息注释在错误文件中 | swag 默默跳过它们；规范没有标题/主机 | 使用 `-g <file>` 标志或将注释移动到 `main.go` |
| 使用 `{object}` 与 map 类型 | swag 无法在无帮助的情况下为 `map[string]any` 生成模式 | 使用命名的结构体或使用 `swaggertype` 注释 |
| 多词 `@Tags` 未加引号 | 标签在空格处分割，产生格式错误的分组 | 用引号引标签：`@Tags "user accounts"` |

## 交叉引用

- → 参考 `samber/cc-skills-golang@golang-security` 以在生产中保护 Swagger UI 端点（禁用或使用认证中间件门控）。
- → 参考 `samber/cc-skills-golang@golang-grpc` 以用于 gRPC——使用 grpc-gateway 及其自己的 OpenAPI 生成器，而不是 swag。

这项技能并不详尽——参考 swaggo/swag 文档和代码示例以获取最新的 API 签名和使用模式：

- 对于 Go 包文档、符号、版本、导入者和已知漏洞，→ 参考 `samber/cc-skills-golang@golang-pkg-go-dev` 技能（`godig`），优先于 Context7 以获取 Go 包事实。
- 要导航此库在你的代码中的使用（定义、调用位置、诊断），→ 参考 `samber/cc-skills-golang@golang-gopls` 技能（`gopls`）。
- Context7 仍然是一个备用方案，用于未在 pkg.go.dev 索引的文档。

如果你在 swag 中遇到错误或意外行为，请到 <https://github.com/swaggo/swag/issues> 打开问题。
