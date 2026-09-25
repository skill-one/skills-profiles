# 入场控制

入场控制拦截资源创建/更新请求，在它们持久化之前进行处理。在 grafana-app-sdk 中有两种类型：

- **验证** — 接受或拒绝请求；不能修改资源
- **变异** — 在资源持久化之前修改资源（例如设置默认值，规范化字段）

无论应用作为独立操作者运行还是作为 `grafana/apps` 的一部分运行，应用的业务逻辑对于入场控制都是相同的。唯一的区别是运行时：独立应用启动自己的 webhook 服务器；`grafana/apps` 应用将入场控制自动注册为 Kubernetes 插件。

## 获取存根

对于独立应用，如果 `pkg/app/app.go` 还不存在，可以使用以下命令生成一个存根应用：

```bash
grafana-app-sdk project component add operator
```

这会创建一个 scaffolded `simple.App`，可以在其中为 `ManagedKinds` 中的每种类型添加入场控制处理器。

## 验证器接口

```go
// 为您想要验证的每种类型实现此接口
type Validator interface {
    Validate(ctx context.Context, request *app.AdmissionRequest) error
}
```

- 返回 `nil` 以接受请求
- 返回错误以拒绝请求（错误消息将返回给 API 调用者）
- `app.AdmissionRequest` 提供对传入对象和操作类型的访问
- 您可以使用 `k8s.NewAdmissionError(err error, statusCode int, reason string)`（来自 `"github.com/grafana/grafana-app-sdk/k8s"`）来更好地控制返回的错误信息

### 验证器示例

```go
type MyKindValidator struct{}

func (v *MyKindValidator) Validate(ctx context.Context, req *app.AdmissionRequest) error {
    obj, ok := req.Object.(*v1.MyKind)
    if !ok {
        return fmt.Errorf("admission request object was of invalid type %T (expected *v1.MyKind)", req.Object)
    }

    // 验证 spec 字段
    if obj.Spec.Title == "" {
        return fmt.Errorf("spec.title is required")
    }

    if obj.Spec.Count < 0 {
        return fmt.Errorf("spec.count must be non-negative, got %d", obj.Spec.Count)
    }

    // 区分创建和更新
    if req.Action == resource.AdmissionActionUpdate && req.OldObject != nil {
        old, ok := req.OldObject.(*v1.MyKind)
        if !ok {
            return fmt.Errorf("admission request old object was of invalid type %T (expected *v1.MyKind)", req.OldObject)
        }
        if old.Spec.Title != obj.Spec.Title {
            return fmt.Errorf("spec.title is immutable after creation")
        }
    }

    return nil
}
```

## 变异入场控制（变异器）

```go
// 实现此接口以在持久化前变异资源
type Mutator interface {
    Mutate(ctx context.Context, request *app.AdmissionRequest) (*app.MutatingResponse, error)
}
```

- 返回一个 `MutatingResponse`，其中包含（可选修改的）对象
- 返回错误以完全拒绝请求
- 最佳实践是拒绝来自验证器的请求，而不是变异器

### 变异处理器示例

```go
type MyKindMutator struct{}

func (m *MyKindMutator) Mutate(
    ctx context.Context,
    req *app.AdmissionRequest,
) (*app.MutatingResponse, error) {
    obj, ok := req.Object.(*v1.MyKind)
    if !ok {
        return nil, fmt.Errorf("admission request object was of invalid type %T (expected *v1.MyKind)", req.Object)
    }

    // 创建时设置默认值
    if req.Action == resource.AdmissionActionCreate {
        if obj.Spec.Description == "" {
            obj.Spec.Description = "No description provided"
        }
    }

    return &app.MutatingResponse{UpdatedObject: obj}, nil
}
```

## 注册入场控制处理器

在构建应用时，在 `pkg/app/app.go` 中注册验证器和变异器：

```go
func New(cfg app.Config) (app.App, error) {
    cfg.KubeConfig.APIPath = "/apis"
    a, err := simple.NewApp(simple.AppConfig{
        ManagedKinds: []simple.AppManagedKind{
            {
                Kind:      v1.MyKindKind(),
                Validator: &MyKindValidator{},
                Mutator:   &MyKindMutator{},
            },
        },
    })
    if err != nil {
      return nil, fmt.Errorf("error creating app: %w", err)
    }
    if err = a.ValidateManifest(cfg.ManifestData); err != nil {
        return nil, fmt.Errorf("app manifest validation failed: %w", err)
    }
    return a, nil
}
```

请注意，变异和验证也必须在类型的 CUE 定义中启用（`mutation.operations` 和 `validation.operations` 字段）——有关详细信息，请参阅 `cue-kind-definition` 技能。

## 入场请求字段

`app.AdmissionRequest` 上可用的关键字段：

| 字段 | 类型 | 描述 |
|-------|------|-------------|
| `Object` | `resource.Object` | 传入的资源（解码后） |
| `OldObject` | `resource.Object` | 先前状态（仅在更新操作中） |
| `Action` | `resource.AdmissionAction` | `AdmissionActionCreate`、`AdmissionActionUpdate`、`AdmissionActionDelete`、`AdmissionActionConnect` |
| `UserInfo` | `resource.AdmissionUserInfo` | 发出请求的用户 |
| `Kind` | `string` | `Object` 的类型 |
| `Group` | `string` | `Object` 的 API 组 |
| `Version` | `string` | `Object` 的 API 版本 |

## 验证模式

常见的实现模式：

```go
// 不可变性检查
if req.Action == resource.AdmissionActionUpdate && old.Spec.ImmutableField != obj.Spec.ImmutableField {
    return fmt.Errorf("spec.immutableField cannot be changed after creation")
}

// 跨字段验证
if obj.Spec.StartTime.After(obj.Spec.EndTime) {
    return fmt.Errorf("spec.startTime must be before spec.endTime")
}

// 引用验证（例如检查引用的资源是否存在）
if _, err := v.client.Get(ctx, resource.Identifier{Name: obj.Spec.RefName, Namespace: obj.Namespace}); err != nil {
    return fmt.Errorf("referenced resource %q not found", obj.Spec.RefName)
}
```

## 部署差异

| 模式 | 入场控制运行时 |
|------|------------------|
| 独立操作者 | 应用启动 webhook 服务器；Kubernetes 将入场控制请求路由到它 |
| `grafana/apps` | 入场控制处理器自动注册为 Kubernetes 进程内插件——无需单独服务器 |

在这两种情况下，处理器代码本身是相同的。

## 资源

- [grafana-app-sdk GitHub](https://github.com/grafana/grafana-app-sdk)
- [app 包文档](https://pkg.go.dev/github.com/grafana/grafana-app-sdk/app)
