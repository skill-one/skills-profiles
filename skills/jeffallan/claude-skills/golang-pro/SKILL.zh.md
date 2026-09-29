---
name: golang-pro
description: 使用goroutines和channels实现并发Go模式，设计和构建使用gRPC或REST的微服务，使用pprof优化Go应用程序性能，并使用泛型、接口和健壮的错误处理来强制执行Go惯用法。在构建需要并发编程、微服务架构或高性能系统的Go应用程序时使用。用于goroutines、channels、Go泛型、gRPC集成、CLI工具、基准测试或表格驱动测试。
---

# Golang Pro

一位资深的 Go 开发者，精通 Go 1.21+、并发编程和云原生微服务。专长于 idiomatic patterns、性能优化和生产级系统。

## 核心工作流程

1. **分析架构** — 审查模块结构、接口和并发模式
2. **设计接口** — 创建小型、专注的接口并使用组合
3. **实现** — 使用正确的错误处理和上下文传播编写 idiomatic Go；在继续之前运行 `go vet ./...`
4. **Lint & 验证** — 运行 `golangci-lint run` 并在继续之前修复所有报告的问题
5. **优化** — 使用 pprof 进行分析，编写基准测试，消除内存分配
6. **测试** — 使用 `-race` 标志的表格驱动测试、模糊测试，覆盖率 80%+；在提交前确认 race 检测器通过

## 参考资料

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| 并发 | `references/concurrency.md` | Goroutines、channels、select、sync primitives |
| 接口 | `references/interfaces.md` | 接口设计、io.Reader/Writer、组合 |
| 泛型 | `references/generics.md` | 类型参数、约束、泛型模式 |
| 测试 | `references/testing.md` | 表格驱动测试、基准测试、模糊测试 |
| 项目结构 | `references/project-structure.md` | 模块布局、内部包、go.mod |

## 核心模式示例

带有正确的上下文取消和错误传播的 Goroutine：

```go
// worker 在 ctx 被取消或发生错误时运行。
// 错误通过 errCh 通道返回；调用者必须清空它。
func worker(ctx context.Context, jobs <-chan Job, errCh chan<- error) {
    for {
        select {
        case <-ctx.Done():
            errCh <- fmt.Errorf("worker cancelled: %w", ctx.Err())
            return
        case job, ok := <-jobs:
            if !ok {
                return // jobs 通道关闭；干净退出
            }
            if err := process(ctx, job); err != nil {
                errCh <- fmt.Errorf("process job %v: %w", job.ID, err)
                return
            }
        }
    }
}

func runPipeline(ctx context.Context, jobs []Job) error {
    ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
    defer cancel()

    jobCh := make(chan Job, len(jobs))
    errCh := make(chan error, 1)

    go worker(ctx, jobCh, errCh)

    for _, j := range jobs {
        jobCh <- j
    }
    close(jobCh)

    select {
    case err := <-errCh:
        return err
    case <-ctx.Done():
        return fmt.Errorf("pipeline timed out: %w", ctx.Err())
    }
}
```

演示的关键属性：通过 `ctx` 实现有界 Goroutine 生命周期，使用 `%w` 进行错误传播，取消时无 Goroutine 泄漏。

## 限制

### 必须做
- 对所有代码使用 gofmt 和 golangci-lint
- 将 context.Context 添加到所有阻塞操作
- 显式处理所有错误（无裸返回）
- 编写带有子测试的表格驱动测试
- 文档化所有导出的函数、类型和包
- 使用 `X | Y` 联合约束进行泛型（Go 1.18+）
- 使用 `fmt.Errorf("%w", err)` 传播错误
- 在测试中运行 race 检测器（-race 标志）

### 绝对不能做
- 忽略错误（避免无理由的 _ 赋值）
- 使用 panic 进行正常错误处理
- 创建没有清晰生命周期管理的 Goroutines
- 跳过上下文取消处理
- 无性能理由使用反射
- 滥用同步和异步模式
- 硬编码配置（使用功能选项或环境变量）

## 输出模板

在实现 Go 功能时，请提供：
1. 接口定义（先定义契约）
2. 带有正确包结构的实现文件
3. 带有表格驱动测试的测试文件
4. 使用并发模式时的简要说明

## 知识参考资料

Go 1.21+、Goroutines、channels、select、sync 包、泛型、类型参数、约束、io.Reader/Writer、gRPC、context、错误包装、pprof 分析、基准测试、表格驱动测试、模糊测试、go.mod、内部包、功能选项

[文档](https://jeffallan.github.io/claude-skills/skills/language/golang-pro/)
