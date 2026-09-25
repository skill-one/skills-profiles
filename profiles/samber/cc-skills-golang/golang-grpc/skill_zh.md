**角色：** 你是一名 Go 分布式系统工程师。你为 gRPC 服务设计正确性和可操作性——适当的状态码、截止时间、拦截器和优雅关闭与快乐路径同样重要。

**模式：**

- **构建模式** — 从头开始实现新的 gRPC 服务器或客户端。
- **审查模式** — 审核现有的 gRPC 代码，查找正确性、安全性和可操作性问题。

**依赖项：**

- protoc: `brew install protobuf`
- protoc-gen-go: `go install google.golang.org/protobuf/cmd/protoc-gen-go@latest`
- protoc-gen-go-grpc: `go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest`

# Go gRPC 最佳实践

将 gRPC 视为纯传输层——将其与业务逻辑分离。官方 Go 实现是 `google.golang.org/grpc`。

这项技能并不详尽——请参考库文档和代码示例获取更多信息：

- 对于 Go 包文档、符号、版本、导入者和已知漏洞，→ 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能 (`godig`)，优先于 Context7 获取 Go 包事实。
- 要导航此库在你的代码中的使用（定义、调用位置、诊断），→ 查看 `samber/cc-skills-golang@golang-gopls` 技能 (`gopls`)。
- Context7 仍然是未在 pkg.go.dev 索引的文档的备用方案。

## 快速参考

| 关注点 | 包/工具 |
| --- | --- |
| 服务定义 | `protoc` 或 `buf` 与 `.proto` 文件 |
| 代码生成 | `protoc-gen-go`, `protoc-gen-go-grpc` |
| 错误处理 | `google.golang.org/grpc/status` 与 `codes` |
| 丰富错误详情 | `google.golang.org/genproto/googleapis/rpc/errdetails` |
| 拦截器 | `grpc.ChainUnaryInterceptor`, `grpc.ChainStreamInterceptor` |
| 中间件生态 | `github.com/grpc-ecosystem/go-grpc-middleware` |
| 测试 | `google.golang.org/grpc/test/bufconn` |
| TLS / mTLS | `google.golang.org/grpc/credentials` |
| 健康检查 | `google.golang.org/grpc/health` |

## Proto 文件组织

按领域组织，使用版本化目录（`proto/user/v1/`）。始终使用 `Request`/`Response` 包装消息——裸类型如 `string` 无法后续添加字段。使用 `buf generate` 或 `protoc` 生成。

[Proto & 代码生成参考](references/protoc-reference.md)

## 服务器实现

- 实现 health check 服务 (`grpc_health_v1`) — Kubernetes 探针需要它来确定就绪状态
- 使用拦截器处理横切关注点（日志记录、认证、恢复）——保持业务逻辑清晰
- 使用 `GracefulStop()` 并设置超时回退到 `Stop()` — 排空正在处理的 RPC，同时防止挂起
- 生产环境中禁用反射——它会暴露你的完整 API 表面

```go
srv := grpc.NewServer(
    grpc.ChainUnaryInterceptor(loggingInterceptor, recoveryInterceptor),
)
pb.RegisterUserServiceServer(srv, svc)
healthpb.RegisterHealthServer(srv, health.NewServer())

go srv.Serve(lis)

// 在关闭信号时：
stopped := make(chan struct{})
go func() { srv.GracefulStop(); close(stopped) }()
select {
case <-stopped:
case <-time.After(15 * time.Second):
    srv.Stop()
}
```

### 拦截器模式

```go
func loggingInterceptor(ctx context.Context, req any, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (any, error) {
    start := time.Now()
    resp, err := handler(ctx, req)
    log.Printf("method=%s duration=%s code=%s", info.FullMethod, time.Since(start), status.Code(err))
    return resp, err
}
```

## 客户端实现

- 重用连接——gRPC 在单个 HTTP/2 连接上多路复用 RPC；每个请求一个连接会浪费 TCP/TLS 握手
- 每次调用设置截止时间 (`context.WithTimeout`) — 没有截止时间，慢速上游会无限期挂起 goroutine
- 使用 `round_robin` 与 headless Kubernetes 服务通过 `dns:///` 方案
- 通过 `metadata.NewOutgoingContext` 传递元数据（认证令牌、跟踪 ID）

```go
conn, err := grpc.NewClient("dns:///user-service:50051",
    grpc.WithTransportCredentials(creds),
    grpc.WithDefaultServiceConfig(`{
        "loadBalancingPolicy": "round_robin",
        "methodConfig": [{
            "name": [{"service": ""}],
            "timeout": "5s",
            "retryPolicy": {
                "maxAttempts": 3,
                "initialBackoff": "0.1s",
                "maxBackoff": "1s",
                "backoffMultiplier": 2,
                "retryableStatusCodes": ["UNAVAILABLE"]
            }
        }]
    }`),
)
client := pb.NewUserServiceClient(conn)
```

## 错误处理

始终使用 `status.Error` 并指定特定代码返回 gRPC 错误——原始 `error` 会变成 `codes.Unknown`，告诉客户端无法采取任何行动。客户端使用代码决定重试、快速失败还是降级。

| 代码 | 使用场景 |
| --- | --- |
| `InvalidArgument` | 输入格式错误（缺少字段、格式错误） |
| `NotFound` | 实体不存在 |
| `AlreadyExists` | 创建失败，实体已存在 |
| `PermissionDenied` | 调用者没有权限 |
| `Unauthenticated` | 缺少或无效的令牌 |
| `FailedPrecondition` | 系统未处于所需状态 |
| `ResourceExhausted` | 超出速率限制或配额 |
| `Unavailable` | 暂时性问题，可以安全重试 |
| `Internal` | 预期外的错误 |
| `DeadlineExceeded` | 超时 |

```go
// ✗ 坏的——调用者得到 codes.Unknown，无法决定是否重试
return nil, fmt.Errorf("user not found")

// ✓ 好的——特定代码让客户端可以适当行动
if errors.Is(err, ErrNotFound) {
    return nil, status.Errorf(codes.NotFound, "user %q not found", req.UserId)
}
return nil, status.Errorf(codes.Internal, "lookup failed: %v", err)
```

对于字段级验证错误，通过 `status.WithDetails` 附加 `errdetails.BadRequest`。

## 流式传输

| 模式 | 用例 |
| --- | --- |
| 服务器流式传输 | 服务器发送序列（日志尾随、结果集） |
| 客户端流式传输 | 客户端发送序列，服务器一次响应（文件上传、批量） |
| 双向流式传输 | 双方独立发送（聊天、实时同步） |

优先使用流式传输而不是大型单个消息——避免每条消息的大小限制，并降低内存压力。

```go
func (s *server) ListUsers(req *pb.ListUsersRequest, stream pb.UserService_ListUsersServer) error {
    for _, u := range users {
        if err := stream.Send(u); err != nil {
            return err
        }
    }
    return nil
}
```

## 测试

使用 `bufconn` 进行内存连接，可以全面测试 gRPC 堆栈（序列化、拦截器、元数据），而无需网络开销。始终测试错误场景是否返回预期的 gRPC 状态代码。

[测试模式和示例](references/testing.md)

## 安全

- 生产环境中必须启用 TLS——凭证在元数据中传输
- 对于服务到服务的认证，使用 mTLS 或委托给服务网格（Istio、Linkerd）
- 对于用户认证，实现 `credentials.PerRPCCredentials` 并在认证拦截器中验证令牌
- 生产环境中应禁用反射，以防止 API 发现

## 性能

| 设置 | 目的 | 典型值 |
| --- | --- | --- |
| `keepalive.ServerParameters.Time` | 空闲连接的 ping 间隔 | 30s |
| `keepalive.ServerParameters.Timeout` | ping 确认超时 | 10s |
| `grpc.MaxRecvMsgSize` | 覆盖 4 MB 默认值以处理大型负载 | 16 MB |
| 连接池 | 高负载流式传输的多个连接 | 4 个连接 |

大多数服务不需要连接池——在添加复杂性之前进行性能分析。

## 常见错误

| 错误 | 修复 |
| --- | --- |
| 返回原始 `error` | 变成 `codes.Unknown`——客户端无法决定是否重试。使用 `status.Errorf` 并指定特定代码 |
| 客户端调用没有截止时间 | 慢速上游会无限期挂起。始终 `context.WithTimeout` |
| 每次请求新连接 | 浪费 TCP/TLS 握手。创建一次，重用——HTTP/2 多路复用 RPC |
| 生产环境中启用反射 | 允许攻击者枚举每个方法。仅在开发/测试环境中启用 |
| 使用 `codes.Internal` 处理所有错误 | 错误代码会破坏客户端重试逻辑。`Unavailable` 触发重试；`InvalidArgument` 不触发 |
| 使用裸类型作为 RPC 参数 | `string` 无法后续添加字段。包装消息允许向后兼容的演进 |
| 缺少 health check 服务 | Kubernetes 无法确定就绪状态，在部署期间杀死 pod |
| 忽略上下文取消 | 长操作在调用者放弃后继续。检查 `ctx.Err()` |

## 交叉引用

- → 查看 `samber/cc-skills-golang@golang-context` 技能以了解截止时间和取消模式
- → 查看 `samber/cc-skills-golang@golang-error-handling` 技能以了解 gRPC 错误到 Go 错误的映射
- → 查看 `samber/cc-skills-golang@golang-observability` 技能以了解 gRPC 拦截器（日志记录、跟踪、指标）
- → 查看 `samber/cc-skills-golang@golang-testing` 技能以了解使用 bufconn 的 gRPC 测试
