---
name: reconciler-logic
description: 为 grafana-app-sdk 应用实现 reconcilers 和 watchers —— 编写 `TypedReconciler[*MyKind]` 的 reconcile 函数，应用基于生成的跳过模式，通过 `resource.UpdateObject` 进行冲突安全的状态更新，配置 `BasicReconcileOptions`（命名空间、标签/字段过滤器、终结器管理），使用 `Watcher` 进行事件式处理，reconcile `UnmanagedKinds`（您的应用不拥有的资源），并将所有内容注册在 `app.go` 中。在编写 reconciler、实现 reconcile 循环、添加异步业务逻辑、处理创建/更新/删除事件、处理资源状态变化、使用 `RequeueAfter` 调度周期性重同步、在 Watcher 和 Reconciler 之间进行选择，或将要控制器连接到 `app.go` 时使用 —— 即使用户说“处理这个资源”、“处理 X 事件”或“编写控制器”而没有提及“reconciler”。
---

# Reconciler 逻辑

Reconciler 是 grafana-app-sdk 应用程序的异步业务逻辑层。SDK 在资源创建、更新或删除时将 reconcile 事件入队；reconciler 观察当前状态并驱动系统向期望状态发展。

## 常见工作流程

### 端到端实现新的 reconciler

```bash
# 1. 为独立应用程序生成 operator 框架
grafana-app-sdk project component add operator

# 2. 实现 ReconcileFunc — 参见 § TypedReconciler 部分了解模式

# 3. 在 app.go 中注册 reconciler（参见 references/registration.md）

# 4. 生成、构建并验证其运行
grafana-app-sdk generate
go build ./...
go run ./cmd/operator   # tail logs — 当你使用 kubectl-apply 创建资源时，reconcile 条目应该会出现
```

如果 operator 启动但创建资源时没有触发 reconcile 事件：
- 检查 `BasicReconcileOptions.Namespace` 是否与资源的命名空间匹配
- 检查 `BasicReconcileOptions.LabelFilters` / `FieldSelectors` — 大多数 "无事件" 问题都是过滤器不匹配（使用 `kubectl get <resource> -o yaml` 查看标签）
- 确认 reconciler 已附加到正确的（最新）版本 kind

## TypedReconciler — 推荐模式

`operator.TypedReconciler` 处理类型断言并提供强类型的 `ReconcileFunc`：

```go
type MyKindReconciler struct {
    operator.TypedReconciler[*v1alpha1.MyKind]
    client resource.Client
}

func NewMyKindReconciler(client resource.Client) *MyKindReconciler {
    r := &MyKindReconciler{client: client}
    r.ReconcileFunc = r.reconcile  // 连接类型化的函数
    return r
}

func (r *MyKindReconciler) reconcile(
    ctx context.Context,
    req operator.TypedReconcileRequest[*v1alpha1.MyKind],
) (operator.ReconcileResult, error) {
    obj := req.Object

    // 如果已在此代中 reconcile，则跳过
    if obj.GetGeneration() == obj.Status.LastObservedGeneration &&
       req.Action != operator.ReconcileActionDeleted {
        return operator.ReconcileResult{}, nil
    }

    log := logging.FromContext(ctx).With("name", obj.GetName(), "namespace", obj.GetNamespace())
    log.Info("reconciling", "action", operator.ResourceActionFromReconcileAction(req.Action))

    if req.Action == operator.ReconcileActionDeleted {
        return operator.ReconcileResult{}, nil
    }

    // ... 业务逻辑 ...

    // 原子状态更新 — 参见 § 状态更新部分
    _, err := resource.UpdateObject(ctx, r.client, obj.GetStaticMetadata().Identifier(),
        func(obj *v1alpha1.MyKind, _ bool) (*v1alpha1.MyKind, error) {
            obj.Status.LastObservedGeneration = obj.GetGeneration()
            obj.Status.State = "Ready"
            return obj, nil
        },
        resource.UpdateOptions{Subresource: "status"},
    )
    return operator.ReconcileResult{}, err
}
```

`ReconcileAction` 值：`ReconcileActionCreated`、`ReconcileActionUpdated`、`ReconcileActionDeleted`、`ReconcileActionResynced`。

延迟重新入队（例如轮询外部系统）：

```go
return operator.ReconcileResult{RequeueAfter: 10 * time.Second}, nil
```

## 使用 `resource.UpdateObject` 进行状态更新

始终使用 `resource.UpdateObject` 进行状态写入 — 它在应用更新函数之前获取最新版本，避免多个 reconcile 事件竞争时出现 `409 Conflict` 错误：

```go
_, err := resource.UpdateObject(ctx, r.client, identifier,
    func(obj *v1alpha1.MyKind, exists bool) (*v1alpha1.MyKind, error) {
        obj.Status.LastObservedGeneration = obj.GetGeneration()
        obj.Status.State = "Ready"
        obj.Status.Message = ""
        return obj, nil
    },
    resource.UpdateOptions{Subresource: "status"},
)
```

**不要** 使用 `client.Update` 进行状态更新 — 它发送完整对象并与用户所做的 spec 更改竞争。

## 基于代的跳过

在 reconcile 函数顶部检查 `LastObservedGeneration` 以避免重新处理未更改的资源：

```go
if obj.GetGeneration() == obj.Status.LastObservedGeneration {
    return operator.ReconcileResult{}, nil
}
```

## `ReconcileOptions`

通过 `AppManagedKind` 条目的 `BasicReconcileOptions` 控制informer行为：

```go
{
    Kind:       mykindv1alpha1.MyKindKind(),
    Reconciler: reconciler,
    ReconcileOptions: simple.BasicReconcileOptions{
        Namespace:      "my-namespace",          // 监控一个命名空间；默认是所有
        LabelFilters:   []string{"env=prod"},    // 仅 reconcile 匹配的资源
        FieldSelectors: []string{"status.phase=Running"},
        UsePlain:       false,                   // false = 包装在 OpinionatedReconciler 中（默认；管理 finalizers）
    },
},
```

`UsePlain: false`（默认值）将你的 reconciler 包装在 `OpinionatedReconciler` 中，它自动管理 finalizers，因此 SDK 可以保证干净删除。

## 参考

- [`references/watchers.md`](references/watchers.md) — `Watcher` 替代方案（事件式 Add/Update/Delete 回调）+ watcher 与 reconciler 的决策矩阵
- [`references/unmanaged-kinds.md`](references/unmanaged-kinds.md) — `UnmanagedKinds` 用于 reconciling 应用程序不拥有的资源，包含 `UseOpinionated: false` 指导和常见失败模式
- [`references/registration.md`](references/registration.md) — 完整的 `app.go` 连接（客户端设置、多版本注册、`ValidateManifest`）+ 常见失败模式

## 外部资源

- [grafana-app-sdk GitHub](https://github.com/grafana/grafana-app-sdk)
- [operator 包文档](https://pkg.go.dev/github.com/grafana/grafana-app-sdk/operator)
