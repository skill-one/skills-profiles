# 创建 Oracle 到 PostgreSQL 的主迁移计划

分析 .NET 解决方案，对每个项目进行 Oracle→PostgreSQL 迁移资格分类，并编写一个下游代理和技能可以解析的结构化计划。

## 工作流

```
进度：
- [ ] 第 1 步：发现解决方案中的项目
- [ ] 第 2 步：分类每个项目
- [ ] 第 3 步：用户确认
- [ ] 第 4 步：编写计划文件
```

**第 1 步：发现项目**

在工作区根目录中找到解决方案文件（它具有 `.sln` 或 `.slnx` 扩展名）（如果存在多个，请询问用户）。解析它以提取所有 `.csproj` 项目引用。对于每个项目，记录其名称、路径和类型（类库、Web API、控制台、测试等）。

**第 2 步：分类每个项目**

扫描每个非测试项目以查找 Oracle 指示：

- NuGet 引用：`Oracle.ManagedDataAccess`、`Oracle.EntityFrameworkCore`（检查 `.csproj` 和 `packages.config`）
- 配置条目：`appsettings.json`、`web.config`、`app.config` 中的 Oracle 连接字符串
- 代码使用：`OracleConnection`、`OracleCommand`、`OracleDataReader`
- 在 `.github/oracle-to-postgres-migration/DDL/Oracle/` 下查找 DDL 跨引用（如果存在）

为每个项目分配一个分类：

| 分类 | 含义 |
|---|---|
| **MIGRATE** | 存在需要转换的 Oracle 交互 |
| **SKIP** | 无 Oracle 指示（仅 UI、共享工具等） |
| **ALREADY_MIGRATED** | 存在 `-postgres` 或 `.Postgres` 副本且似乎已处理 |
| **TEST_PROJECT** | 测试项目；由测试工作流处理 |

**第 3 步：用户确认**

展示分类列表。允许用户调整分类或迁移顺序，然后最终确定。

**第 4 步：编写计划文件**

保存到：`.github/oracle-to-postgres-migration/Reports/MasterMigrationPlan.md`

使用此模板——下游消费者依赖于结构：

````markdown
# 主迁移计划

**解决方案：** {解决方案文件名}
**解决方案根目录：** {REPOSITORY_ROOT}
**创建时间：** {timestamp}
**最后更新时间：** {timestamp}

## DDL 资产

**位置：** {DDL 资产路径，例如 `.github/oracle-to-postgres-migration/DDL/`}
**使用外部工具：** {是 / 否} — {如果是，请命名工具（例如 `ora2pg`），并注意第 4 步（模式 & DDL 迁移）可以跳过；PostgreSQL DDL 资产已存在。}

## 解决方案摘要

| 指标 | 数量 |
|--------|-------|
| 解决方案中的项目总数 | {n} |
| 需要迁移的项目 | {n} |
| 已迁移的项目 | {n} |
| 跳过项目（无 Oracle 使用） | {n} |
| 测试项目（单独处理） | {n} |

## 项目清单

| # | 项目名称 | 路径 | 分类 | 备注 |
|---|---|---|---|---|
| 1 | {name} | {相对路径} | MIGRATE | {notes} |
| 2 | {name} | {相对路径} | SKIP | 无 Oracle 依赖 |

## 迁移顺序

1. **{ProjectName}** — {理由，例如 "核心数据访问库；其他项目依赖于它。"}
2. **{ProjectName}** — {理由}
````

按顺序排列项目，以便共享/基础库在依赖它们的库之前迁移。
