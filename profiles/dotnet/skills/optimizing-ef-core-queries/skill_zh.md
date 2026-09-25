# 优化 EF Core 查询

诊断和修复缓慢的 Entity Framework Core (EF Core) 查询。从生成的 SQL/日志开始，应用最小的更改以消除瓶颈，并通过重新阅读 SQL 和查询计数来确认修复。优先考虑减少往返次数、重复行、扫描或每次调用转换成本的更改，而不是微优化。一次应用一个更改并重新测量。

## 何时使用

- EF Core 查询缓慢或发出的 SQL 语句远多于预期
- 相同的查询每行重复一次（N+1 / 懒加载）
- 多个集合 `Include` 导致行爆炸或重复
- 深页随着 `Skip` 增长而变慢，或批量更新加载行只是为了修改它们
- 过滤/排序查询即使列已索引也会扫描，或过滤/排序列没有支持索引
- 热门、频繁执行的查询在每次调用时都支付 EF Core 的 LINQ-转换成本

## 何时不用

- **代码使用 Dapper 或原始 ADO.NET，而不是 EF Core。** 直接回答 SQL/索引/查询计划问题；不要引入 `DbContext` 或推荐 `AsNoTracking`、`Include`、`AsSplitQuery` 或其他 EF Core API。

## 首先：捕获生成的 SQL

你无法优化你看不到的东西。在更改任何内容之前打开命令日志并阅读 SQL 和查询计数：

```csharp
optionsBuilder.LogTo(Console.WriteLine, LogLevel.Information);
// 或在 appsettings.json 中设置 "Microsoft.EntityFrameworkCore.Database.Command": "Information"
```

使用 `.TagWith("...")` 标记查询，以便在日志中找到它。在每次更改前后，计算慢速操作运行多少个语句，以及每个语句返回多少行。

## 修复方法

### 保持谓词可索引——永远不要将索引列包装在函数中

当索引列在比较的一侧**裸露**时，索引才能被使用。将其包装在函数或算术运算中——`CreatedAt.Year == y`、`CreatedAt.Date == d`、`ToLower(Name) == n`、`Price * 1.1 > x`，或前导通配符 `LIKE '%foo'`——会强制执行每行的计算，索引无法满足，因此即使存在索引，查询也会**扫描整个表**。添加另一个索引不会改变任何东西。重写谓词，使列保持裸露，通常作为半开范围：

```csharp
// 非可索引用：为每一行计算函数 → 全表扫描
db.Logs.Where(l => l.CreatedAt.Year == year);

// 可索引用：裸列与常量比较 → 索引查找
var start = new DateTime(year, 1, 1);
db.Logs.Where(l => l.CreatedAt >= start && l.CreatedAt < start.AddYears(1));
```

相同的规则涵盖几种常见情况：

- **不区分大小写的文本** — 比较存储的规范化列，而不是 `ToLower(...)`/`ToUpper(...)`。
- **计算表达式** — 与预计算的常量比较，而不是 `column * k > x`。
- **将列转换为另一种类型** — 对 `column.ToString()`（例如匹配数字或日期的*文本形式*，`total.ToString().StartsWith(p)`）对每一行应用函数，通常无法完全转换为 SQL，强制客户端评估并将整个表加载到内存中。用实际的比较或范围过滤类型列。
- **子字符串搜索** — `name.Contains(term)` 变为无法索引的未锚定 `LIKE '%term%'` 并扫描表；带尾随通配符的前缀 (`name.StartsWith(term)` → `'term%'`) 可以索引。当前缀匹配可接受时锚定搜索——这会改变匹配的行，因此请先确认行为——并在大型表上使用全文索引后实现真正的子字符串或模糊搜索。

**验证：** 计划显示查找/索引而不是扫描，持续时间减少。如果列确实没有索引，添加一个（见下文），但在谓词可索引之前。

### 编译热、频繁执行的查询

在一个非常热路径上，该路径在重复使用的上下文中数千次运行*相同的*查询形状，EF Core 每次调用都会重新解析 LINQ 表达式树并探测其查询缓存。当查询已经最小（索引查找或小型投影）并且只读调整（如 `AsNoTracking`）没有帮助时，每次调用的转换是剩余成本。使用 `EF.CompileQuery` / `EF.CompileAsyncQuery` 一次性编译查询，并重用委托：

```csharp
private static readonly Func<AppDbContext, int, ProductListItem> GetProduct =
    EF.CompileQuery((AppDbContext db, int id) =>
        db.Products.Where(p => p.Id == id)
                   .Select(p => new ProductListItem(p.Id, p.Name, p.Price))
                   .First());

public ProductListItem Lookup(AppDbContext db, int id) => GetProduct(db, id);
```

委托是 `static`（编译一次）并接受 `DbContext` 加上每个参数作为参数。用于执行非常高频的单个查询形状的端点或循环；它对一次性查询无效。

**验证：** 热循环的平均时间减少，结果相同。

### 移除 N+1 和避免懒加载

每行重复相同的 `SELECT`（在循环内部访问的导航）是 N+1。在一次往返中加载相关数据——使用 `Select` 投影聚合，或使用 `Include` 激烈加载：

```csharp
var summaries = await db.Orders
    .Select(o => new OrderSummary(o.Id, o.Items.Count, o.Items.Sum(i => i.Price)))
    .ToListAsync();
```

优先考虑投影或 `Include` 而不是懒加载：懒加载是 N+1 的主要原因，并强制同步 I/O。在服务器应用程序中，不要启用 `Microsoft.EntityFrameworkCore.Proxies` 或将导航标记为 `virtual` 以进行懒加载。

**验证：** 无论行数如何，查询计数固定且较小。

### 分割多个集合 `Include`

在一个查询中包含两个或多个集合导航会乘以行（笛卡尔积）并重复父数据。使用 `AsSplitQuery()` 以便每个集合在自己的语句中加载；在唯一键上添加 `OrderBy` 以便行拼接在一起：

```csharp
db.Blogs.Include(b => b.Posts).Include(b => b.Contributors).AsSplitQuery();
```

**验证：** 每个语句的行数急剧下降，总持续时间有所改善。

### 过滤和分页；优先考虑键集而不是偏移量

用 `Where` 限制大型结果集，并使用**键集（查找）**分页而不是 `Skip`/`Take`，后者在深页上仍然扫描并丢弃跳过的行：

```csharp
db.Orders.Where(o => o.Id > lastSeenId).OrderBy(o => o.Id).Take(pageSize);
```

按唯一、稳定、索引的键排序（如果排序列不是唯一的，请添加平局断开）。键集分页通过*上次看到的键*而不是页码，因此它会改变方法的输入；当固定签名排除了原地切换时，仍然标记深偏移扫描并推荐键集。

**验证：** 页面延迟从早期到深页大致保持不变。

### 添加缺失的索引

将过滤器移入 SQL 或使谓词可索引会停止*客户端*的浪费，但列没有索引的 `WHERE` 或 `ORDER BY` 仍然在数据库内部扫描整个表——然后频繁运行的查询在每次调用时都会重新扫描它。因此，单独从查询重写中审计索引覆盖范围：对于每个查询，检查其过滤和排序列是否由索引支持。实体键和外键按约定索引，但其他列——状态标志、状态/枚举字段、时间戳、名称——通常**没有**，除非模型配置了它。当热查询在未索引列上过滤或排序时，建议添加索引并明确说明，即使重写的查询已经返回正确的行：索引是代码更改本身无法提供的单独修复。 （如果谓词不可索引，请先修复它——新索引无法帮助由列上的函数引起的扫描。）

如果 EF Core 拥有架构，请在模型中添加索引并迁移：

```csharp
modelBuilder.Entity<Order>()
    .HasIndex(o => new { o.CustomerId, o.CreatedAt }); // 等价列优先，然后范围/排序
```

然后使用 `dotnet ef migrations add ...` 创建迁移。**不要**使用 `dotnet ef database update`（或任何等效写入数据库的操作）而未经明确用户批准——应用迁移会修改数据库，因此添加迁移，向用户展示，让他们在审查后运行更新。如果 EF Core 没有拥有架构，建议向管理数据库的人提出相同的索引。不要过度索引——每个索引都会减慢写入速度。

**验证：** 计划使用查找/索引而不是扫描。

### 基于集合的批量更新和删除

用 `ExecuteUpdateAsync`/`ExecuteDeleteAsync`（EF Core 7+）替换加载-修改-`SaveChanges` 循环——一个语句，没有实体材料化：

```csharp
await db.Products.Where(p => p.LastSoldDate < cutoff)
    .ExecuteUpdateAsync(s => s.SetProperty(p => p.IsActive, false));
```

这些绕过更改跟踪器和 EF 端的级联行为——显式应用相关更改。

**验证：** 一个带有 `WHERE` 的单个 `UPDATE`/`DELETE`，没有前面的 `SELECT`。

## 常见陷阱

| 陷阱 | 修复 |
|------|------|
| 将索引列包装在 `.Year`/`.Date`/`ToLower`/算术运算中 | 重写为对裸列的可索引范围/比较 |
| 为非可索引谓词上的扫描添加索引 | 先修复谓词；索引在列变为裸露之前无法帮助 |
| 将过滤器重写为 SQL 但在未索引列上保留热查询 | 服务器端扫描仍然是一个扫描——建议在过滤/排序列上添加索引 |
| 编译仅在偶尔运行的查询 | 仅编译真正热、高频的查询形状 |
| 懒加载（代理/`virtual` 导航）导致 N+1 和强制同步 I/O | 激烈加载 (`Include`) 或投影；保持查询异步 |
| `ToList()`/`AsEnumerable()` 在 `Where`/`Select` 之前 | 保持查询 `IQueryable` 以便过滤/投影在 SQL 中运行 |

## 参考

- [高效查询 — EF Core](https://learn.microsoft.com/zh-cn/ef/core/performance/efficient-querying)
- [编译查询 — EF Core](https://learn.microsoft.com/zh-cn/ef/core/performance/advanced-performance-topics#compiled-queries)
- [高效更新 (ExecuteUpdate/ExecuteDelete) — EF Core](https://learn.microsoft.com/zh-cn/ef/core/performance/efficient-updating)
- [单查询与分查询](https://learn.microsoft.com/zh-cn/ef/core/querying/single-split-queries)
- [分页](https://learn.microsoft.com/zh-cn/ef/core/querying/pagination)
- [索引](https://learn.microsoft.com/zh-cn/ef/core/modeling/indexes)
