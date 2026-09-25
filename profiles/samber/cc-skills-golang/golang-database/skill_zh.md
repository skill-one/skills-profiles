**角色设定：** 你是一位 Go 后端工程师，编写安全、明确且可观察的数据库代码。你将 SQL 视为一门一等语言——不使用 ORM，不使用魔法——并在边界处捕获数据完整性问题，而不是在应用程序深处。

**模式：**

- **编写模式**——生成新的仓库函数、查询辅助工具或事务包装器：遵循技能的顺序指令；在生成新代码之前，启动一个后台代理来在代码库中 grep 现有的查询模式和命名约定。
- **审查/调试模式**——审计或调试现有的数据库代码：使用一个子代理并行扫描缺少 `rows.Close()`、未参数化的查询、缺少上下文传播和缺失的错误检查，同时阅读业务逻辑。

> **社区默认值。** 一项明确覆盖 `samber/cc-skills-golang@golang-database` 技能的公司技能优先。

# Go 数据库最佳实践

Go 的 `database/sql` 为数据库访问提供了坚实的基础。在它之上使用 `sqlx` 或 `pgx` 以提高易用性——绝不使用 ORM。

在使用 sqlx 或 pgx 时，参考库的官方文档和代码示例以获取当前的 API 签名。

## 最佳实践摘要

1. **使用 sqlx 或 pgx，不使用 ORM** — ORM 隐藏了 SQL，生成了不可预测的查询，并使调试更困难
2. 查询必须使用参数化占位符——绝对不要将用户输入串联到 SQL 字符串中
3. 上下文必须传递给所有数据库操作——使用 `*Context` 方法变体（`QueryContext`、`ExecContext`、`GetContext`）
4. `sql.ErrNoRows` 必须显式处理——使用 `errors.Is` 区分“未找到”与真实错误
5. 迭代后必须关闭 Rows——`defer rows.Close()` 立即放在 `QueryContext` 调用之后
6. 绝不使用 `db.Query` 对于不返回行的语句——`Query` 返回 `*Rows`，必须关闭；如果你忘记，连接会泄漏回连接池。使用 `db.Exec` 代替
7. **使用事务进行多语句操作**——将相关的写入包裹在 `BeginTxx`/`Commit` 中
8. **使用 `SELECT ... FOR UPDATE`** 当读取你打算修改的数据时——防止竞态条件
9. **在默认的 READ COMMITTED 不足时设置自定义隔离级别**（例如，财务操作使用可序列化）
10. **使用指针字段（`*string`、`*int`）或 `sql.NullXxx` 类型处理 NULLable 列**
11. 连接池必须配置——`SetMaxOpenConns`、`SetMaxIdleConns`、`SetConnMaxLifetime`、`SetConnMaxIdleTime`
12. **使用外部工具进行迁移**——golang-migrate 或 Flyway，绝不手写或 AI 生成的迁移 SQL
13. **以合理的批量大小进行批量操作**——不是逐行（太多往返），也不是一次百万条（锁定和内存）
14. **绝不创建或修改数据库模式**——在玩具数据上看起来正确的模式在真实生产负载下可能导致热点、锁定争用或缺失索引。模式设计需要理解数据量、访问模式和生产约束，而 AI 没有这些理解
15. **避免隐藏的 SQL 功能**——不要在应用程序代码中依赖触发器、视图、物化视图、存储过程或行级安全

## 库选择

| 库 | 适用于 | 结构扫描 | PostgreSQL 特有 |
|---|---|---|---|
| `database/sql` | 可移植性、最小依赖 | 手动 `Scan` | 否 |
| `sqlx` | 多数据库项目 | `StructScan` | 否 |
| `pgx` | PostgreSQL（30-50% 更快） | `pgx.RowToStructByName` | 是（COPY、LISTEN、数组） |
| GORM/ent | **避免** | 魔术 | 抽象 |

**为什么不使用 ORM：**

- 不可预测的查询生成——N+1 问题，你在代码中看不到
- 魔术钩子和回调（BeforeCreate、AfterUpdate）使调试更困难
- 模式迁移与应用程序代码耦合
- 学习 ORM API 比学习 SQL 更难，并且抽象会泄漏

## 参数化查询

```go
// ✗ 非常糟糕——SQL 注入漏洞
query := fmt.Sprintf("SELECT * FROM users WHERE email = '%s'", email)

// ✓ 良好——参数化（PostgreSQL）
var user User
err := db.GetContext(ctx, &user, "SELECT id, name, email FROM users WHERE email = $1", email)

// ✓ 良好——参数化（MySQL）
err := db.GetContext(ctx, &user, "SELECT id, name, email FROM users WHERE email = ?", email)
```

### 动态 IN 子句

```go
query, args, err := sqlx.In("SELECT * FROM users WHERE id IN (?)", ids)
if err != nil {
    return fmt.Errorf("构建 IN 子句：%w", err)
}
query = db.Rebind(query) // 调整占位符以适应你的驱动
err = db.SelectContext(ctx, &users, query, args...)
```

### 动态列名

永远不要从用户输入中插值列名。使用白名单：

```go
allowed := map[string]bool{"name": true, "email": true, "created_at": true}
if !allowed[sortCol] {
    return fmt.Errorf("无效的排序列：%s", sortCol)
}
query := fmt.Sprintf("SELECT id, name, email FROM users ORDER BY %s", sortCol)
```

有关更多防止注入的模式，请参阅 `samber/cc-skills-golang@golang-security` 技能。

## 结构扫描和 NULLable 列

使用 `db:"column_name"` 标签为 sqlx，使用 `pgx.CollectRows` 与 `pgx.RowToStructByName` 为 pgx。使用指针字段（`*string`、`*time.Time`）处理 NULLable 列——它们与扫描和 JSON 反序列化都工作良好。有关所有方法的示例，请参阅 [扫描参考](./references/scanning.md)。

## 错误处理

```go
func GetUser(id string) (*User, error) {
    var user User

    err := db.GetContext(ctx, &user, "SELECT id, name FROM users WHERE id = $1", id)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, ErrUserNotFound // 翻译为领域错误
        }
        return nil, fmt.Errorf("查询用户 %s：%w", id, err)
    }

    return &user, nil
}
```

或：

```go
func GetUser(id string) (u *User, exists bool, err error) {
    var user User

    err := db.GetContext(ctx, &user, "SELECT id, name FROM users WHERE id = $1", id)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, false, nil // “没有用户”不是技术错误，而是领域错误
        }
        return nil, false, fmt.Errorf("查询用户 %s：%w", id, err)
    }

    return &user, true, nil
}
```

### 始终关闭 Rows

```go
rows, err := db.QueryContext(ctx, "SELECT id, name FROM users")
if err != nil {
    return fmt.Errorf("查询用户：%w", err)
}
defer rows.Close() // 防止连接泄漏

for rows.Next() {
    // ...
}
if err := rows.Err(); err != nil { // 迭代后始终检查
    return fmt.Errorf("迭代用户：%w", err)
}
```

### 常见的数据库错误模式

| 错误 | 如何检测 | 操作 |
|---|---|---|
| 行未找到 | `errors.Is(err, sql.ErrNoRows)` | 返回领域错误 |
| 唯一约束 | 检查驱动程序特定的错误代码 | 返回冲突错误 |
| 连接被拒绝 | `err != nil` 在 `db.PingContext` 上 | 快速失败、记录、带退避重试 |
| 序列化失败 | PostgreSQL 错误代码 `40001` | 重试整个事务 |
| 上下文被取消 | `errors.Is(err, context.Canceled)` | 停止处理，传播 |

## 上下文传播

始终使用 `*Context` 方法变体传播截止日期和取消：

```go
// ✗ 坏的——没有上下文，查询在客户端断开连接之前运行至完成
db.Query("SELECT ...")

// ✓ 良好——尊重上下文取消和超时
db.QueryContext(ctx, "SELECT ...")
```

有关上下文模式的深入内容，请参阅 `samber/cc-skills-golang@golang-context` 技能。

## 事务、隔离级别和锁定

有关事务模式、隔离级别、`SELECT FOR UPDATE` 和锁定变体，请参阅 [事务](./references/transactions.md)。

## 连接池

```go
db.SetMaxOpenConns(25)              // 限制总连接数
db.SetMaxIdleConns(10)              // 保持热连接就绪
db.SetConnMaxLifetime(5 * time.Minute)  // 回收过时的连接
db.SetConnMaxIdleTime(1 * time.Minute)  // 更快地关闭空闲连接
```

有关尺寸指导公式，请参阅 [数据库性能](./references/performance.md)。

## 迁移

使用外部迁移工具。模式更改需要人类审查，理解数据量、现有索引、外键和生产约束。

推荐工具：

- [golang-migrate](https://github.com/golang-migrate/migrate) — 命令行 + Go 库，支持所有主要数据库
- [Flyway](https://flywaydb.org/) — 基于 JVM，在企业环境中广泛使用
- [Atlas](https://atlasgo.io/) — 现代、声明式模式管理

迁移 SQL 应由人类编写和审查，版本控制在源代码管理中，并通过 CI/CD 管道应用。

## 避免隐藏的 SQL 功能

不要在应用程序代码中依赖触发器、视图、物化视图、存储过程或行级安全——它们会创建不可见的副作用，并使调试不可能。保持 SQL 在 Go 中显式可见，以便可以测试和版本控制。

## 模式创建

**此技能不涵盖模式创建。** AI 生成的模式通常微妙地错误——缺少索引、错误的列类型、不良的规范化或缺失约束。模式设计需要理解数据量、访问模式、查询配置文件和业务约束。使用专用数据库工具和人类审查。

## 深入探讨

- **[事务](./references/transactions.md)** — 事务边界、隔离级别、死锁预防、`SELECT FOR UPDATE`
- **[测试数据库代码](./references/testing.md)** — 模拟连接、使用容器进行集成测试、固定装置、模式设置/删除
- **[数据库性能](./references/performance.md)** — 连接池尺寸、批量处理、索引策略、查询优化
- **[结构扫描](./references/scanning.md)** — 结构标签、NULLable 列处理、JSON 反序列化模式

## 跨参考

- → 参见 `samber/cc-skills-golang@golang-security` 技能以获取 SQL 注入预防模式
- → 参见 `samber/cc-skills-golang@golang-context` 技能以获取数据库操作中的上下文传播
- → 参见 `samber/cc-skills-golang@golang-error-handling` 技能以获取数据库错误包装模式
- → 参见 `samber/cc-skills-golang@golang-testing` 技能以获取数据库集成测试模式

## 参考

- [database/sql 教程](https://go.dev/doc/database/)
- [sqlx](https://github.com/jmoiron/sqlx)
- [pgx](https://github.com/jackc/pgx)
- [golang-migrate](https://github.com/golang-migrate/migrate)
