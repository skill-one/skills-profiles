# Go 并发模式

Go 并发的生产模式，包括协程、通道、同步原语和上下文管理。

## 何时使用此技能

- 构建并发 Go 应用程序
- 实现工作池和管道
- 管理协程生命周期
- 使用通道进行通信
- 调试竞态条件
- 实现优雅关闭

## 核心概念

### 1. Go 并发原语

| 原语         | 目的                          |
| ------------ | ----------------------------- |
| `goroutine`  | 轻量级并发执行               |
| `channel`    | 协程间通信                   |
| `select`     | 多路复用通道操作             |
| `sync.Mutex` | 互斥锁                       |
| `sync.WaitGroup` | 等待协程完成                 |
| `context.Context` | 取消和截止日期               |

### 2. Go 并发箴言

```
不要通过共享内存来通信；
通过通信来共享内存。
```

## 快速入门

```go
package main

import (
    "context"
    "fmt"
    "sync"
    "time"
)

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    results := make(chan string, 10)
    var wg sync.WaitGroup

    // 启动工作协程
    for i := 0; i < 3; i++ {
        wg.Add(1)
        go worker(ctx, i, results, &wg)
    }

    // 完成时关闭结果通道
    go func() {
        wg.Wait()
        close(results)
    }()

    // 收集结果
    for result := range results {
        fmt.Println(result)
    }
}

func worker(ctx context.Context, id int, results chan<- string, wg *sync.WaitGroup) {
    defer wg.Done()

    select {
    case <-ctx.Done():
        return
    case results <- fmt.Sprintf("Worker %d done", id):
    }
}
```

## 详细模式和示例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 最佳实践

### 应该做

- **使用 context** - 用于取消和截止日期
- **从发送端关闭通道** - 仅从发送端关闭
- **使用 errgroup** - 用于带错误的并发操作
- **缓冲通道** - 当你知道数量时
- **优先使用通道** - 而不是互斥锁

### 不应该做

- **不要泄露协程** - 始终要有退出路径
- **不要从接收端关闭** - 会引发 panic
- **不要使用共享内存** - 除非必要
- **不要忽略 context 取消** - 检查 ctx.Done()
- **不要使用 time.Sleep 进行同步** - 使用正确的原语
