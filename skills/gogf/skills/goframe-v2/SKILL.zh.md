---
name: goframe-v2
description: GoFrame v2 开发技能。仅在目标 Go 项目使用或明确采用 GoFrame v2 时使用：最近的 go.mod 文件需要 github.com/gogf/gf/v2，现有的 Go 文件导入 github.com/gogf/gf/v2 或任何 github.com/gogf/gf/v2/... 组件包，或用户要求使用 GoFrame 进行脚手架搭建、迁移或构建。适用于基于 GoFrame 的 Go 工作类型，如 API/控制器/服务、中间件、路由/配置、ORM/DAO/DO 实体/数据库操作、gf CLI/代码生成、HTTP/gRPC 服务以及微服务规范。不适用于无 GoFrame 证据的通用 Go 项目、仅前端工作、Shell 脚本或不相关的基础设施任务。
---

# 关键规范

## 项目开发标准
- 对于完整项目（HTTP/微服务），安装GoFrame CLI并使用`gf init`创建项目脚手架。详情请参阅[项目创建 - init](./references/开发工具/项目创建-init.md)。
- 自动生成的代码文件（dao、do、entity）**必须**禁止手动创建或修改，这是GoFrame的规范。
- 除非明确要求，**不要**使用`logic/`目录进行业务逻辑。直接在`service/`目录中实现业务逻辑。
- 参考完整项目示例：
  - HTTP服务最佳实践：[user-http-service](./examples/practices/user-http-service)
  - gRPC服务最佳实践：[user-grpc-service](./examples/practices/user-grpc-service)

## 组件使用标准
- 在创建新方法或变量之前，检查是否已存在于其他地方并重用现有实现。
- 使用`gerror`组件进行所有错误处理，以确保完整的堆栈跟踪以实现可追溯性。
- 在探索新组件时，优先使用GoFrame内置组件并参考示例中的最佳实践代码。
- **数据库操作**必须使用DO对象（`internal/model/do/`），**绝对不要**使用`g.Map`或`map[string]interface{}`。DO结构体的字段是`interface{}`；未设置的字段保持`nil`，ORM会自动忽略：
  ```go
  // 良好 - 使用DO对象
  dao.Users.Ctx(ctx).Where(cols.Id, id).Data(do.User{Uid: uid}).Update()

  // 良好 - 条件字段，未设置的字段为nil并被忽略
  data := do.User{}
  if password != "" { data.PasswordHash = hash }
  if isAdmin != nil { data.IsAdmin = *isAdmin }
  dao.Users.Ctx(ctx).Where(cols.Id, id).Data(data).Update()

  // 良好 - 使用gdb.Raw显式将列设置为NULL
  dao.Instances.Ctx(ctx).Where(cols.Id, id).Data(do.Instance{IdleSince: gdb.Raw("NULL")}).Update()

  // 不良 - 绝对不要在数据库操作中使用g.Map
  dao.Users.Ctx(ctx).Data(g.Map{cols.Uid: uid}).Update()
  ```
## 代码风格标准
- **变量声明**：当定义多个变量时，使用`var`块将它们分组以获得更好的对齐和可读性：
  ```go
  // 良好 - 对齐且整洁
  var (
      authSvc       *auth.Service
      bizCtxSvc     *bizctx.Service
      k8sSvc        *svcK8s.Service
      notebookSvc   *notebook.Service
      middlewareSvc *middleware.Service
  )

  // 避免 - 分散声明
  authSvc := auth.New()
  bizCtxSvc := bizctx.New()
  k8sSvc := svcK8s.New()
  ```
- 当你在同一作用域中有3个或更多相关的变量声明时，应用此模式。

## 软删除与时间维护

GoFrame提供**自动**软删除和时间维护功能。当表包含`created_at`、`updated_at`或`deleted_at`字段时，ORM会自动处理这些字段。

### 自动时间字段

| 字段       | 自动行为          |
|------------|-------------------|
| `created_at` | 在`Insert/InsertAndGetId`时自动写入，之后不再修改 |
| `updated_at` | 在`Insert/Update/Save`时自动写入 |
| `deleted_at` | 在`Delete`（软删除）时自动写入，在查询时自动过滤 |

### 关键规则

**1. 绝对不要**手动设置时间字段 - GoFrame会自动处理这些字段：
```go
// 错误 - 冗余的手动时间设置
dao.User.Ctx(ctx).Data(do.User{
    Name:      "john",
    CreatedAt: gtime.Now(),  // 冗余！框架会自动处理
    UpdatedAt: gtime.Now(),  // 冗余！框架会自动处理
}).Insert()

// 正确 - 让框架处理时间字段
dao.User.Ctx(ctx).Data(do.User{
    Name: "john",
}).Insert()
```

**2. 绝对不要**手动添加`WhereNull(cols.DeletedAt)` - GoFrame会自动添加软删除过滤：
```go
// 错误 - 冗余的软删除条件
dao.User.Ctx(ctx).
    Where(do.User{Status: 1}).
    WhereNull(cols.DeletedAt).  // 冗余！框架会自动添加此条件
    Scan(&list)

// 正确 - 框架自动添加deleted_at IS NULL
dao.User.Ctx(ctx).
    Where(do.User{Status: 1}).
    Scan(&list)
```

**3. 使用`Delete()`进行软删除** - 框架会转换为`UPDATE SET deleted_at = NOW()`：
```go
// 正确 - 使用Delete()，框架处理软删除
dao.User.Ctx(ctx).Where(do.User{Id: id}).Delete()
// 实际SQL: UPDATE `sys_user` SET `deleted_at`=NOW() WHERE `id`=?

// 错误 - 手动Update并设置deleted_at
dao.User.Ctx(ctx).
    Where(do.User{Id: id}).
    Data(do.User{DeletedAt: gtime.Now()}).  // 冗余！
    Update()
```

### 字段类型支持

`deleted_at`字段支持多种类型：
- **DateTime/Timestamp**：默认，存储删除时间
- **Integer**：存储Unix时间戳（秒）
- **Boolean**：存储0/1表示删除状态

### 配置（可选）

时间字段名称可以在`config.yaml`中自定义：
```yaml
database:
  default:
    createdAt: "created_at"   # 自定义字段名称
    updatedAt: "updated_at"
    deletedAt: "deleted_at"
    timeMaintainDisabled: false  # 设置为true以禁用此功能
```

# GoFrame文档
完整的GoFrame开发资源，涵盖组件设计、使用、最佳实践和注意事项：[GoFrame文档](./references/README.MD)

# GoFrame代码示例
丰富的实用代码示例，涵盖HTTP服务、gRPC服务和各种项目类型：[GoFrame示例](./examples/README.MD)
