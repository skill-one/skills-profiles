# Go 后端开发

构建生产级后端系统的全面技能，使用 Go 语言。掌握 goroutines、channels、web 服务器、数据库集成、微服务架构和可扩展、并发后端应用程序的部署模式。

## 使用此技能的场景

当您需要：

- 构建高性能的 web 服务器和 REST API
- 使用 gRPC 或 HTTP 开发微服务架构
- 使用 goroutines 和 channels 实现并发处理
- 创建需要高吞吐量的实时系统
- 构建具有连接池的数据库后端应用程序
- 开发用于容器化部署的云原生应用程序
- 编写性能关键的后端服务
- 构建具有服务发现功能的分布式系统
- 实现事件驱动架构
- 创建具有网络功能的 CLI 工具和系统实用程序
- 开发用于实时通信的 WebSocket 服务器
- 构建使用并发工作者的数据处理管道

**Go 在以下方面表现出色：**

- 网络编程和 HTTP 服务
- 使用轻量级 goroutines 进行并发处理
- 使用垃圾回收的系统级编程
- 跨平台编译
- 快速编译时间，实现快速开发
- 内置测试和基准测试

## 核心概念

### 1. Goroutines：轻量级并发

Goroutines 是由 Go 运行时管理的轻量级线程。它们支持以最小的开销进行并发执行。

**主要特征：**

- 非常轻量级（启动时栈大小约为 2KB）
- 由运行时 multiplex 到 OS 线程
- 可以同时运行数千或数百万个
- 通过集成调度器进行协作调度

**基本的 Goroutine 模式：**

```go
func main() {
    // 启动并发计算
    go expensiveComputation(x, y, z)
    anotherExpensiveComputation(a, b, c)
}
```

`go` 关键字启动一个新的 goroutine，允许 `expensiveComputation` 与 `anotherExpensiveComputation` 并发执行。这是 Go 并发模型的基础。

**常见用例：**

- 后台处理
- 并发 API 调用
- 并行数据处理
- 实时事件处理
- 服务器中的连接处理

### 2. Channels：安全通信

Channels 在 goroutines 之间提供类型安全的通信，在许多场景中无需显式锁。

**Channel 类型：**

```go
// 无缓冲 channel - 同步通信
ch := make(chan int)

// 缓冲 channel - 异步（最多缓冲大小）
ch := make(chan int, 100)

// 只读 channel
func receive(ch <-chan int) { /* ... */ }

// 只写 channel
func send(ch chan<- int) { /* ... */ }
```

**使用 Channels 进行同步：**

```go
func computeAndSend(ch chan int, x, y, z int) {
    ch <- expensiveComputation(x, y, z)
}

func main() {
    ch := make(chan int)
    go computeAndSend(ch, x, y, z)
    v2 := anotherExpensiveComputation(a, b, c)
    v1 := <-ch  // 阻塞直到结果可用
    fmt.Println(v1, v2)
}
```

此模式确保两个计算都完成后再继续，其中 channel 提供了通信和同步。

**Channel 模式：**

- 生产者-消费者
- 扇形-扇入
- 管道阶段
- 超时和取消
- 信号量和速率限制

### 3. Select 语句：Channel 多路复用

`select` 语句启用多个 channel 操作的多路复用，类似于用于 channel 的 switch。

**超时实现：**

```go
timeout := make(chan bool, 1)
go func() {
    time.Sleep(1 * time.Second)
    timeout <- true
}()

select {
case <-ch:
    // 从 ch 读取成功
case <-timeout:
    // 操作超时
}
```

**基于 Context 的取消：**

```go
select {
case result := <-resultCh:
    return result
case <-ctx.Done():
    return ctx.Err()
}
```

### 4. Context 包：请求范围值

`context.Context` 接口管理截止日期、取消信号和跨 API 边界的请求范围值。

**Context 接口：**

```go
type Context interface {
    // Done 返回一个当工作应该被取消时关闭的 channel
    Done() <-chan struct{}

    // Err 返回取消的原因
    Err() error

    // Deadline 返回工作应该被取消的时间
    Deadline() (deadline time.Time, ok bool)

    // Value 返回请求范围值
    Value(key any) any
}
```

**创建 Context：**

```go
// 背景上下文 - 永不取消
ctx := context.Background()

// 带有取消的上下文
ctx, cancel := context.WithCancel(context.Background())
defer cancel()

// 带有超时的上下文
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

// 带有截止日期的上下文
deadline := time.Now().Add(10 * time.Second)
ctx, cancel := context.WithDeadline(context.Background(), deadline)
defer cancel()

// 带有值的上下文
ctx = context.WithValue(parentCtx, key, value)
```

**最佳实践：**

- 始终将 context 作为第一个参数传递：`func DoSomething(ctx context.Context, ...)` 
- 立即调用 `defer cancel()` 后创建可取消的上下文
- 在调用链中传递 context
- 在长时间运行的操作中检查 `ctx.Done()`
- 使用 context 值仅用于请求范围数据，而不是可选参数

### 5. WaitGroup：协调 Goroutines

`sync.WaitGroup` 等待一组 goroutines 完成。

**基本模式：**

```go
var wg sync.WaitGroup

for i := 0; i < 10; i++ {
    wg.Add(1)
    go func(id int) {
        defer wg.Done()
        // 执行工作
    }(i)
}

wg.Wait()  // 阻塞直到所有 goroutines 完成
```

**常见用例：**

- 等待并行任务
- 协调工作池
- 确保清理完成
- 同步关闭

### 6. Mutex：保护共享状态

当需要共享状态时，使用 `sync.Mutex` 或 `sync.RWMutex` 进行保护。

**Mutex 模式：**

```go
var (
    service   map[string]net.Addr
    serviceMu sync.Mutex
)

func RegisterService(name string, addr net.Addr) {
    serviceMu.Lock()
    defer serviceMu.Unlock()
    service[name] = addr
}

func LookupService(name string) net.Addr {
    serviceMu.Lock()
    defer serviceMu.Unlock()
    return service[name]
}
```

**RWMutex 用于读密集型工作负载：**

```go
var (
    cache   map[string]interface{}
    cacheMu sync.RWMutex
)

func Get(key string) interface{} {
    cacheMu.RLock()
    defer cacheMu.RUnlock()
    return cache[key]
}

func Set(key string, value interface{}) {
    cacheMu.Lock()
    defer cacheMu.Unlock()
    cache[key] = value
}
```

### 7. 并发 Web 服务器模式

Go 标准的并发连接处理模式：

```go
for {
    rw := l.Accept()
    conn := newConn(rw, handler)
    go conn.serve()  // 每个连接在它自己的 goroutine 中处理
}
```

每个接受的连接都在它自己的 goroutine 中处理，允许服务器有效地扩展到数千个并发连接。

## Web 服务器开发

### HTTP 服务器基础

**简单的 HTTP 服务器：**

```go
package main

import (
    "fmt"
    "net/http"
)

func main() {
    http.HandleFunc("/", handler)
    http.ListenAndServe("localhost:8080", nil)
}

func handler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprint(w, "Hello!")
}
```

### 请求处理模式

**处理程序函数：**

```go
func handler(w http.ResponseWriter, r *http.Request) {
    // 读取请求
    method := r.Method
    path := r.URL.Path
    query := r.URL.Query()

    // 写入响应
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusOK)
    fmt.Fprintf(w, `{"message": "success"}`)
}
```

**处理程序结构体：**

```go
type APIHandler struct {
    db     *sql.DB
    logger *log.Logger
}

func (h *APIHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    // 访问依赖项
    h.logger.Printf("Request: %s %s", r.Method, r.URL.Path)
    // 处理请求
}
```

### 中间件模式

**日志中间件：**

```go
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}

// 使用方式
http.Handle("/api/", loggingMiddleware(apiHandler))
```

**身份验证中间件：**

```go
func authMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := r.Header.Get("Authorization")
        if !isValidToken(token) {
            http.Error(w, "Unauthorized", http.StatusUnauthorized)
            return
        }
        next.ServeHTTP(w, r)
    })
}
```

**链式中间件：**

```go
handler := loggingMiddleware(authMiddleware(corsMiddleware(apiHandler)))
http.Handle("/api/", handler)
```

### HTTP 请求中的 Context

**带有 Context 的 HTTP 请求：**

```go
func handleSearch(w http.ResponseWriter, req *http.Request) {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    // 检查查询参数
    query := req.FormValue("q")
    if query == "" {
        http.Error(w, "missing query", http.StatusBadRequest)
        return
    }

    // 使用 Context 执行搜索
    results, err := performSearch(ctx, query)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }

    // 渲染结果
    renderTemplate(w, results)
}
```

**基于 Context 的 HTTP 请求：**

```go
func httpDo(ctx context.Context, req *http.Request,
            f func(*http.Response, error) error) error {
    c := &http.Client{}

    // 在 goroutine 中运行请求
    ch := make(chan error, 1)
    go func() {
        ch <- f(c.Do(req))
    }()

    // 等待完成或取消
    select {
    case <-ctx.Done():
        <-ch  // 等待 f 返回
        return ctx.Err()
    case err := <-ch:
        return err
    }
}
```

### 路由模式

**自定义路由器：**

```go
type Router struct {
    routes map[string]http.HandlerFunc
}

func (r *Router) Handle(pattern string, handler http.HandlerFunc) {
    r.routes[pattern] = handler
}

func (r *Router) ServeHTTP(w http.ResponseWriter, req *http.Request) {
    if handler, ok := r.routes[req.URL.Path]; ok {
        handler(w, req)
    } else {
        http.NotFound(w, req)
    }
}
```

**RESTful API 结构：**

```go
// GET /api/users
func listUsers(w http.ResponseWriter, r *http.Request) { /* ... */ }

// GET /api/users/:id
func getUser(w http.ResponseWriter, r *http.Request) { /* ... */ }

// POST /api/users
func createUser(w http.ResponseWriter, r *http.Request) { /* ... */ }

// PUT /api/users/:id
func updateUser(w http.ResponseWriter, r *http.Request) { /* ... */ }

// DELETE /api/users/:id
func deleteUser(w http.ResponseWriter, r *http.Request) { /* ... */ }
```

## 并发模式

### 1. Pipeline 模式

Pipeline 通过 channel 连接的多个阶段处理数据。

**生成器阶段：**

```go
func gen(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
        close(out)
    }()
    return out
}
```

**处理阶段：**

```go
func sq(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            out <- n * n
        }
        close(out)
    }()
    return out
}
```

**Pipeline 使用：**

```go
func main() {
    // 设置 up pipeline
    c := gen(2, 3)
    out := sq(c)

    // 消费输出
    for n := range out {
        fmt.Println(n)  // 4 then 9
    }
}
```

**带缓冲的生成器（无需 goroutine）：**

```go
func gen(nums ...int) <-chan int {
    out := make(chan int, len(nums))
    for _, n := range nums {
        out <- n
    }
    close(out)
    return out
}
```

### 2. Fan-Out/Fan-In 模式

将工作分配给多个工作者并合并结果。

**Fan-Out：多个工作者：**

```go
func main() {
    in := gen(2, 3, 4, 5)

    // Fan out: 将工作分配给两个 goroutine
    c1 := sq(in)
    c2 := sq(in)

    // Fan in: 合并结果
    for n := range merge(c1, c2) {
        fmt.Println(n)
    }
}
```

**合并函数（Fan-In）：**

```go
func merge(cs ...<-chan int) <-chan int {
    var wg sync.WaitGroup
    out := make(chan int)

    // 为每个输入 channel 启动输出 goroutine
    output := func(c <-chan int) {
        for n := range c {
            out <- n
        }
        wg.Done()
    }

    wg.Add(len(cs))
    for _, c := range cs {
        go output(c)
    }

    // 关闭 out 一旦所有输出完成
    go func() {
        wg.Wait()
        close(out)
    }()
    return out
}
```

### 3. 显式取消模式

**使用 Done Channel 进行取消：**

```go
func sq(done <-chan struct{}, in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            select {
            case out <- n * n:
            case <-done:
                return
            }
        }
    }()
    return out
}
```

**广播取消：**

```go
func main() {
    done := make(chan struct{})
    defer close(done)  // 广播给所有 goroutine

    in := gen(done, 2, 3, 4)
    c1 := sq(done, in)
    c2 := sq(done, in)

    // 处理部分结果
    out := merge(done, c1, c2)
    fmt.Println(<-out)

    // done 在返回时关闭，取消所有 pipeline 阶段
}
```

**带取消的合并：**

```go
func merge(done <-chan struct{}, cs ...<-chan int) <-chan int {
    var wg sync.WaitGroup
    out := make(chan int)

    output := func(c <-chan int) {
        defer wg.Done()
        for n := range c {
            select {
            case out <- n:
            case <-done:
                return
            }
        }
    }

    wg.Add(len(cs))
    for _, c := range cs {
        go output(c)
    }

    go func() {
        wg.Wait()
        close(out)
    }()
    return out
}
```

### 1. Worker Pool 模式

**固定数量的工作者：**

```go
func handle(queue chan *Request) {
    for r := range queue {
        process(r)
    }
}

func Serve(clientRequests chan *Request, quit chan bool) {
    // 启动处理程序
    for i := 0; i < MaxOutstanding; i++ {
        go handle(clientRequests)
    }
    <-quit  // 等待退出
}
```

**信号量模式：**

```go
var sem = make(chan int, MaxOutstanding)

func handle(r *Request) {
    sem <- 1        // 获取
    process(r)
    <-sem           // 释放
}

func Serve(queue chan *Request) {
    for req := range queue {
        sem <- 1  // 在创建 goroutine 之前获取
        go func() {
            process(req)
            <-sem  // 释放
        }()
    }
}
```

**限制 Goroutine 创建：**

```go
func Serve(queue chan *Request) {
    for req := range queue {
        sem <- 1  // 在创建 goroutine 之前获取
        go func() {
            process(req)
            <-sem  // 释放
        }()
    }
}
```

### 2. Query Racing 模式

并发查询多个源并返回第一个结果：

```go
func Query(conns []Conn, query string) Result {
    ch := make(chan Result)
    for _, conn := range conns {
        go func(c Conn) {
            select {
            case ch <- c.DoQuery(query):
            default:
            }
        }(conn)
    }
    return <-ch
}
```

### 3. 并行处理示例

**串行 MD5 计算：**

```go
func MD5All(root string) (map[string][md5.Size]byte, error) {
    m := make(map[string][md5.Size]byte)
    err := filepath.Walk(root, func(path string, info os.FileInfo, err error) {
        if err != nil {
            return err
        }
        if !info.Mode().IsRegular() {
            return nil
        }
        data, err := ioutil.ReadFile(path)
        if err != nil {
            return err
        }
        m[path] = md5.Sum(data)
        return nil
    })
    return m, err
}
```

**并行 MD5 使用 Pipeline：**

```go
type result struct {
    path string
    sum  [md5.Size]byte
    err  error
}

func sumFiles(done <-chan struct{}, root string) (<-chan result, <-chan error) {
    c := make(chan result)
    errc := make(chan error, 1)

    go func() {
        defer close(c)
        err := filepath.Walk(root, func(path string, info os.FileInfo, err error) {
            if err != nil {
                return err
            }
            if !info.Mode().IsRegular() {
                return nil
            }

            // 为每个文件启动 goroutine
            go func() {
                data, err := ioutil.ReadFile(path)
                select {
                case c <- result{path, md5.Sum(data), err}:
                case <-done:
                }
            }()

            // 检查早期取消
            select {
            case <-done:
                return errors.New("walk canceled")
            default:
                return nil
            }
        }

        select {
        case errc <- err:
        case <-done:
        }
    }()
    return c, errc
}

func MD5All(root string) (map[string][md5.Size]byte, error) {
    done := make(chan struct{})
    defer close(done)

    c, errc := sumFiles(done, root)

    m := make(map[string][md5.Size]byte)
    for r := range c {
        if r.err != nil {
            return nil, r.err
        }
        m[r.path] = r.sum
    }

    if err := <-errc; err != nil {
        return nil, err
    }
    return m, nil
}
```

### 4. Leaky Buffer 模式

高效的缓冲区重用：

```go
var freeList = make(chan *Buffer, 100)

func server() {
    for {
        b := <-serverChan  // 等待工作
        process(b)

        // 尝试重用缓冲区
        select {
        case freeList <- b:
            // 缓冲区在 free list 中
        default:
            // free list 满载，GC 将回收
        }
    }
}
```

## 数据库集成

### 连接管理

**数据库连接池：**

```go
import "database/sql"

func initDB(dataSourceName string) (*sql.DB, error) {
    db, err := sql.Open("postgres", dataSourceName)
    if err != nil {
        return nil, err
    }

    // 配置连接池
    db.SetMaxOpenConns(25)
    db.SetMaxIdleConns(5)
    db.SetConnMaxLifetime(5 * time.Minute)
    db.SetConnMaxIdleTime(10 * time.Minute)

    // 验证连接
    if err := db.Ping(); err != nil {
        return nil, err
    }

    return db, nil
}
```

### 查询模式

**单行查询：**

```go
func getUser(db *sql.DB, userID int) (*User, error) {
    user := &User{}
    err := db.QueryRow(
        "SELECT id, name, email FROM users WHERE id = $1",
        userID,
    ).Scan(&user.ID, &user.Name, &user.Email)

    if err == sql.ErrNoRows {
        return nil, fmt.Errorf("user not found")
    }
    if err != nil {
        return nil, err
    }

    return user, nil
}
```

**多行查询：**

```go
func listUsers(db *sql.DB) ([]*User, error) {
    rows, err := db.Query("SELECT id, name, email FROM users")
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var users []*User
    for rows.Next() {
        user := &User{}
        if err := rows.Scan(&user.ID, &user.Name, &user.Email); err != nil {
            return nil, err
        }
        users = append(users, user)
    }

    if err := rows.Err(); err != nil {
        return nil, err
    }

    return users, nil
}
```

**使用 Context 插入/更新：**

```go
func createUser(ctx context.Context, db *sql.DB, user *User) error {
    query := "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING id"
    err := db.QueryRowContext(ctx, query, user.Name, user.Email).Scan(&user.ID)
    return err
}
```

### 事务处理

```go
func transferFunds(ctx context.Context, db *sql.DB, from, to int, amount decimal.Decimal) error {
    tx, err := db.BeginTx(ctx, nil)
    if err != nil {
        return err
    }
    defer tx.Rollback()  // 如果不提交，则回滚

    // 从账户借出
    _, err = tx.ExecContext(ctx,
        "UPDATE accounts SET balance = balance - $1 WHERE id = $2",
        amount, from)
    if err != nil {
        return err
    }

    // 账户贷入
    _, err = tx.ExecContext(ctx,
        "UPDATE accounts SET balance = balance + $1 WHERE id = $2",
        amount, to)
    if err != nil {
        return err
    }

    return tx.Commit()
}
```

### 预处理语句

```go
func insertUsers(db *sql.DB, users []*User) error {
    stmt, err := db.Prepare("INSERT INTO users (name, email) VALUES ($1, $2)")
    if err != nil {
        return err
    }
    defer stmt.Close()

    for _, user := range users {
        _, err := stmt.Exec(user.Name, user.Email)
        if err != nil {
            return err
        }
    }

    return nil
}
```

## 错误处理

### 自定义错误类型

```go
type ValidationError struct {
    Field string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

// 使用示例
if email == "" {
    return &ValidationError{Field: "email", Message: "required"}
}
```

### 错误包装

```go
import "fmt"

func processData(data []byte) error {
    err := validateData(data)
    if err != nil {
        return fmt.Errorf("process data: %w", err)
    }
    return nil
}

// 错误解包
if errors.Is(err, ErrValidation) {
    // 处理验证错误
}

if errors.As(err, &validationErr) {
    // 访问 ValidationError 字段
}
```

### Sentinel 错误

```go
var (
    ErrNotFound = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
    ErrInvalidInput = errors.New("invalid input")
)

// 使用示例
if errors.Is(err, ErrNotFound) {
    http.Error(w, "Resource not found", http.StatusNotFound)
}
```

## 测试

### 单元测试

```go
func TestGetUser(t *testing.T) {
    db := setupTestDB(t)
    defer db.Close()

    user, err := getUser(db, 1)
    if err != nil {
        t.Fatalf("getUser failed: %v", err)
    }

    if user.Name != "John Doe" {
        t.Errorf("expected name John Doe, got %s", user.Name)
    }
}
```

### 表驱动测试

```go
func TestValidateEmail(t *testing.T) {
    tests := []struct {
        name    string
        email   string
        wantErr bool
    }{
        {"valid email", "user@example.com", false},
        {"missing @", "userexample.com", true},
        {"empty string", "", true},
        {"missing domain", "user@", true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := validateEmail(tt.email)
            if (err != nil) != tt.wantErr {
                t.Errorf("validateEmail(%q) error = %v, wantErr %v",
                    tt.email, err, tt.wantErr)
            }
        }
    }
}
```

### 基准测试

```go
func BenchmarkConcurrentMap(b *testing.B) {
    m := make(map[string]int)
    var mu sync.Mutex

    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            mu.Lock()
            m["key"]++
            mu.Unlock()
        }
    }
}
```

### HTTP 处理程序测试

```go
func TestHandler(t *testing.T) {
    req := httptest.NewRequest("GET", "/api/users", nil)
    w := httptest.NewRecorder()

    handler(w, req)

    resp := w.Result()
    if resp.StatusCode != http.StatusOK {
        t.Errorf("expected status 200, got %d", resp.StatusCode)
    }

    body, _ := ioutil.ReadAll(resp.Body)
    // 断言内容
}
```

## 生产模式

### 调用关闭

```go
func main() {
    srv := &http.Server{
        Addr:    ":8080",
        Handler: router,
    }

    // 在 goroutine 中启动服务器
    go func() {
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("listen: %s\n", err)
        }
    }

    // 等待中断信号
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit
    log.Println("Shutting down server...")
    <-quit
    log.Println("Server exited")
}
```

### 配置管理

```go
type Config struct {
    ServerPort  int           `env:"PORT" envDefault:"8080"`
    DBHost      string        `env:"DB_HOST" envDefault:"localhost"`
    DBPort      int           `env:"DB_PORT" envDefault:"5432"`
    LogLevel    string        `env:"LOG_LEVEL" envDefault:"info"`
    Timeout     time.Duration `env:"TIMEOUT" envDefault:"30s"`
}

func loadConfig() (*Config, error) {
    cfg := &Config{}
    if err := env.Parse(cfg); err != nil {
        return nil, err
    }
    return cfg, nil
}
```

### 结构化日志记录

```go
import "log/slog"

func setupLogger() *slog.Logger {
    return slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
        Level: slog.LevelInfo,
    })
}
}

func handler(w http.ResponseWriter, r *http.Request) {
    logger := slog.With(
        "method", r.Method,
        "path", r.URL.Path,
        "remote", r.RemoteAddr,
    )

    logger.Info("handling request")

    // 处理请求

    logger.Info("request completed", "status", 200)
}
```

### 健康检查

```go
func healthHandler(db *sql.DB) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        // 检查数据库
        if err := db.Ping(); err != nil {
            w.WriteHeader(http.StatusServiceUnavailable)
            json.NewEncoder(w).Encode(map[string]string{
                "status": "unhealthy",
                "error": err.Error(),
            })
            return
        }

        // 检查其他依赖项...

        w.WriteHeader(http.StatusOK)
        json.NewEncoder(w).Encode(map[string]string{
                "status": "healthy",
        })
    }
}
```

### 速率限制

```go
import "golang.org/x/time/rate"

func rateLimitMiddleware(limiter *rate.Limiter) func(http.Handler) http.Handler {
    return func(w http.ResponseWriter, r *http.Request) {
        if !limiter.Allow() {
            http.Error(w, "Too Many Requests", http.StatusTooManyRequests)
            return
        }
        next.ServeHTTP(w, r)
    }
}

// 使用示例
limiter := rate.NewLimiter(rate.Limit(10), 20)  // 10 req/sec, 爆发 20
    handler := rateLimitMiddleware(limiter)(apiHandler)
```

### 恐慌恢复

```go
func safelyDo(work *Work) {
    defer func() {
        if err := recover(); err != nil {
            log.Println("work failed:", err)
        }
    }()
}

func server(workChan <-chan *Work) {
    for work := range workChan {
        go safelyDo(work)
    }
}
```

## 微服务模式

### 服务结构

```go
type UserService struct {
    db     *sql.DB
    cache  *redis.Client
    logger *slog.Logger
}

func NewUserService(db *sql.DB, cache *redis.Client, logger *slog.Logger) *UserService {
    return &UserService{
        db:     db,
        cache:  cache,
        logger: logger,
    }
}

func (s *UserService) GetUser(ctx context.Context, userID string) (*User, error) {
    // 检查缓存首先
    if user, err := s.getFromCache(ctx, userID); err == nil {
        return user, nil
    }

    // 查询数据库
    user, err := s.getFromDB(ctx, userID)
    if err != nil {
        return nil, err
    }

    // 更新缓存
    go s.updateCache(context.Background(), user)

    return user, nil
}
```

### gRPC 服务

```go
type server struct {
    pb.UnimplementedUserServiceServer
    db *sql.DB
}

func (s *server) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.User, error) {
        user := &pb.User{}
        err := s.db.QueryRowContext(ctx,
            "SELECT id, name, email FROM users WHERE id = $1",
            req.GetId(),
        ).Scan(&user.Id, &user.Name, &user.Email)

        if err != nil {
            return nil, status.Errorf(codes.NotFound, "user not found")
        }
        return user, nil
    }
}
```

### 服务发现

```go
type ServiceRegistry struct {
    services map[string][]string
    mu       sync.RWMutex
}

func (r *ServiceRegistry) Register(name, addr string) {
    r.mu.Lock()
    defer r.mu.Unlock()
    r.services[name] = append(r.services[name], addr)
}

func (r *ServiceRegistry) Discover(name string) (string, error) {
    r.mu.RLock()
    defer r.mu.RUnlock()

    addrs := r.services[name]
    if len(addrs) == 0 {
        return "", fmt.Errorf("service %s not found", name)
    }

    // 简单的轮询
    return addrs[rand.Intn(len(addrs))], nil
}
```

### Circuit Breaker

```go
type CircuitBreaker struct {
    maxFailures int
    timeout     time.Duration
    failures    int
    lastFailure time.Time
    state       string  // closed, open, half-open
    mu          sync.Mutex
}

func (cb *CircuitBreaker) Call(fn func() error) error {
    cb.mu.Lock()

    if cb.state == "open" {
        if time.Since(cb.lastFailure) > cb.timeout {
            cb.state = "half-open"
        } else {
            cb.mu.Unlock()
            return errors.New("circuit breaker open")
        }
    }

    cb.mu.Unlock()

    err := fn()

    cb.mu.Lock()
    defer cb.mu.Unlock()

    if err != nil {
        cb.failures++
        cb.lastFailure = time.Now()
        if cb.failures >= cb.maxFailures {
            cb.state = "open"
        }
    }
    return err
}
```

## 最佳实践

### 1. Goroutine 管理

- 始终考虑 goroutine 的生命周期和清理
- 使用 context 进行取消传播
- 避免 goroutine 泄漏，确保所有 goroutine 都可以退出
- 慎慎使用循环中的闭包 - 明确传递值

**反模式：**
```go
for _, v := range values {
    go func() {
        fmt.Println(v)  // 所有 goroutines 共享相同的 v
    }()
}
```

**正确：**
```go
for _, v := range values {
    go func(val string) {
        fmt.Println(val)  // 每个 goroutine 获取自己的副本
    }(v)
}
```

### 2. Channel 最佳实践

- 从发送者关闭 channel，而不是接收者
- 使用缓冲 channel 以防止 goroutine 泄漏
- 考虑使用 `select` 与 `default` 用于非阻塞操作
- 记住：发送到已关闭的 channel 会 panic，接收返回零值

### 3. 错误处理

- 返回错误，不要恐慌（除非是真正异常的情况）
- 使用 `fmt.Errorf("%w", err)` 包装错误以提供上下文
- 使用自定义错误类型进行程序化处理
- 记录错误时提供足够的上下文

### 4. 性能

- 使用 `sync.Pool` 进行频繁分配的对象
- 在优化之前进行基准测试：`go test -bench . -cpuprofile=cpu.prof`
- 考虑使用 `sync.Map` 进行并发 map 访问模式
- 使用缓冲 channel 以已知容量
- 避免在热点路径中不必要的分配

### 5. 代码组织

```
project/
├── cmd/
│   └── server/
│       └── main.go          # 应用程序入口点
├── internal/
│   ├── api/                 # HTTP 处理程序
│   ├── service/             # 业务逻辑
│   ├── repository/          # 数据访问
│   └── middleware/          # HTTP 中间件
├── pkg/
│   └── utils/               # 公共实用程序
├── migrations/              # 数据库迁移
├── config/                  # 配置文件
└── docker/                  # Docker 文件
```

### 6. 安全性

- 验证所有输入
- 使用预处理语句执行 SQL 查询
- 实现速率限制
- 在生产中使用 HTTPS
- 清理发送给客户端的错误消息
- 使用 context 超时防止资源耗尽
- 实现适当的身份验证和授权

### 7. 测试

- 写表驱动测试
- 使用 `t.Helper()` 用于测试辅助函数
- 模拟外部依赖项
- 使用 `httptest` 进行 HTTP 处理程序测试
- 为性能关键代码编写基准测试
- 目标是业务逻辑的测试覆盖率 >80%

## 常见陷阱

### 1. 竞态条件

**问题：**
```go
var service map[string]net.Addr

    func RegisterService(name string, addr net.Addr {
        service[name] = addr  // 竞态条件
    }

func LookupService(name string) net.Addr {
        return service[name]  // 竞态条件
    }
```

**解决方案：**
```go
var (
    service   map[string]net.Addr
    serviceMu sync.Mutex
)

func RegisterService(name string, addr net.Addr) {
    serviceMu.Lock()
    defer serviceMu.Unlock()
    service[name] = addr
}
```

### 2. Goroutine 泄漏

**问题:**
```go
func process() {
    ch := make(chan int)
    go func() {
        ch <- expensive()  // 阻塞永远 - 没有接收者
    }()
    // 返回没有读取 ch
}
```

**解决方案:**
```go
func process() {
    ch := make(chan int, 1)  // 缓冲 channel
    go func() {
        ch <- expensive()  // 不会阻塞
    }()
}
```

### 3. 未关闭 Channel

接收者需要知道何时没有更多值发送：

```go
func gen(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)  // 重要：当完成时关闭
    }()
    return out
}
```

### 4. 无缓冲 Channel 阻塞

```go
// 这将导致死锁
ch := make(chan int)
ch <- 1  // 永远阻塞 - 没有接收者
```

使用缓冲 channel 或分离 goroutine。

### 5. 未同步的 Channel 操作

```go
c := make(chan struct{})

// 竞态条件
go func() { c <- struct{}{} }()
close(c)
```

确保具有 happens-before 关系，使用适当的同步。

## 资源和参考

### 官方文档

- Go 文档：https://go.dev/doc/
- Effective Go：https://go.dev/doc/effective_go
- Go 博客：https://go.dev/blog/
- Go by Example：https://gobyexample.com/
- Context Package：https://go.dev/blog/context
- Share Memory By Communicating: https://go.dev/blog/codelab-share

### 并发资源

- Go Concurrency Patterns：https://go.dev/blog/pipelines
- Context Package：https://go.dev/blog/context
- Share Memory By Communicating: https://go.dev/blog/codelab-share

### 标准库

- net/http：https://pkg.go.dev/net/http
- database/sql：https://pkg.go.dev/database/sql
- context：https://pkg.go.dev/context
- sync：https://pkg.go.dev/sync

### 工具

- Race Detector：`go test -race`
- Profiler：`go tool pprof`
- Benchmarking：`go test -bench . -cpuprofile=cpu.prof`
- Static Analysis：`go vet`, `staticcheck`

### 常见陷阱

### 1. 竞态条件

**问题:**
```go
var service map[string]net.Addr

    func RegisterService(name string, addr net.Addr {
        service[name] = addr  // 竞态条件
    }

func LookupService(name string) net.Addr {
        return service[name]  // 竞态条件
    }
```

**解决方案:**
```go
var (
    service   map[string]net.Addr
    serviceMu sync.Mutex
)

func RegisterService(name string, addr net.Addr) {
    serviceMu.Lock()
    defer serviceMu.Unlock()
    service[name] = addr
}
```

### 2. Goroutine 泄漏

**问题:**
```go
func process() {
    ch := make(chan int)
    go func() {
        ch <- expensive()  // 阻塞永远 - 没有接收者
    }()
    // 返回没有读取 ch
}
```

**解决方案:**
```go
func process() {
    ch := make(chan int, 1)  // 缓冲 channel
    go func() {
        ch <- expensive()  // 不会阻塞
    }()
}
```

### 3. 未关闭 Channel

接收者需要知道何时没有更多值发送：

```go
func gen(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)  // 重要：当完成时关闭
    }()
    return out
}
```

### 4. 无缓冲 Channel 阻塞

```go
// 这将导致死锁
ch := make(chan int)
ch <- 1  // 永远阻塞 - 没有接收者
```

使用缓冲 channel 或分离 goroutine。

### 5. 未同步的 Channel 操作

```go
c := make(chan struct{})

// 竞态条件
go func() { c <- struct{}{} }()
close(c)
```

确保具有 happens-before 关系，使用适当的同步。

---

**技能版本**: 1.0.0
**最后更新**: 2025 年 10 月
**技能类别**: 后端开发，系统编程，并发编程
**先决条件**: 基本编程知识，理解 HTTP，熟悉命令行
**推荐下一个技能**: docker-deployment, kubernetes-orchestration, grpc-microservices
```
