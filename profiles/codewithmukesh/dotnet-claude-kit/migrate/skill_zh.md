# /migrate

## 什么是

针对三种变更类型的单一迁移工作流，以 EF Core 模式迁移为主要流程：

1. **EF Core 模式** — 审查待处理的模型变更，生成描述性命名的迁移，审查 SQL 以评估数据丢失和锁定风险，并使用文档化的回滚路径应用。
2. **.NET 版本升级** — 分阶段 TFM/SDK/包升级，每个阶段进行验证。
3. **NuGet 更新** — 逐个包增量更新，确保问题可追溯。

共享原则：应用前验证，始终有回滚计划，每步后测试，每个迁移一个逻辑变更。

## 何时使用

- 修改实体类、DbContext 配置或关系后
- "添加迁移"、"更新数据库"、"创建迁移"、"新建表"、"重命名列"
- 生成供 DBA 审查的 SQL 脚本时
- "升级到 .NET 10"、"版本升级"、"升级 .NET"
- "升级 nuget"、"更新包"、"依赖更新"、"漏洞包警报"

## 如何操作

首先分类请求：模式变更 → 流程 A；框架升级 → 流程 B；包更新 → 流程 C。然后按该流程端到端执行。

### 流程 A：EF Core 模式迁移（主要）

**步骤 1：评估当前状态**

```bash
dotnet ef migrations list --project <InfraProject> --startup-project <ApiProject>
```

检查待处理的迁移和未捕获的模型变更。

**步骤 2：审查模型变更**

使用 MCP 工具而非阅读整个文件：

```
find_symbol(name: entity or DbSet)        -- 定位变更的实体
get_type_hierarchy(typeName: entity)      -- 检查 TPH/TPT/TPC 继承变更
find_references(symbolName: property)     -- 评估下游查询影响
```

确认变更是一个逻辑单元。如果不是，拆分为多个迁移 — 混合迁移使回滚成为全有或全无。

**步骤 3：生成迁移**

命名描述变更而非实体：`Add|Remove|Rename|Modify` + `WhatChanged`。

```bash
# GOOD
dotnet ef migrations add AddOrderShippingAddress --project <Infra> --startup-project <Api>
# BAD — 命名实体而非变更
dotnet ef migrations add Order
```

**步骤 4：审查生成的 SQL**

`database update` 没有干跑标志 — 通过生成幂等脚本并阅读预览：

```bash
dotnet ef migrations script --idempotent --project <Infra> --startup-project <Api>
```

标记并报告：
- **DROP COLUMN / DROP TABLE** — 确认数据丢失是故意的
- **ALTER COLUMN** 类型变更 — 检查精度损失或截断
- **ALTER 大表** — 警告锁定时长
- **新增非空列** — 需为现有行提供默认值

如果数据必须通过重命名/重类型保留，使用多步骤迁移和原始 SQL：

```csharp
protected override void Up(MigrationBuilder migrationBuilder)
{
    migrationBuilder.AddColumn<string>("ContactEmail", "Customers", nullable: true);
    migrationBuilder.Sql("UPDATE \"Customers\" SET \"ContactEmail\" = \"Email\"");
    migrationBuilder.AlterColumn<string>("ContactEmail", "Customers", nullable: false);
    migrationBuilder.DropColumn("Email", "Customers");
}
```

**步骤 5：应用并验证**

```bash
dotnet ef database update --project <Infra> --startup-project <Api>
dotnet build && dotnet test   # 集成测试捕获模式不匹配
```

**步骤 6：文档化回滚**

```bash
dotnet ef database update <PreviousMigrationName> --project <Infra> --startup-project <Api>
dotnet ef migrations remove --project <Infra> --startup-project <Api>   # 如果从代码回滚
```

不要修改已应用的迁移 — 创建新的。

### 流程 B：.NET 版本升级

1. **评估** — `get_project_graph` 列出所有 TFM；标记混合版本。
2. **预检** — 所有测试通过，无待处理 EF 迁移，依赖项检查目标版本兼容性，创建专用分支（分支就是回滚计划）。
3. **更新 `global.json`** — SDK 版本带 `"rollForward": "latestMinor"`。
4. **更新 TFM** — `.csproj` 或 `Directory.Build.props` 中的 `<TargetFramework>net10.0</TargetFramework>` 和 `<LangVersion>14</LangVersion>`。
5. **更新包** — `dotnet outdated --upgrade Major --include Microsoft.*`，然后构建和修复。
6. **采用新特性** — 根据 `knowledge/dotnet-whats-new.md`：`TimeProvider`、`HybridCache`、主构造函数、集合表达式。
7. **验证** — `dotnet build`、`dotnet test`、`dotnet format --verify-no-changes`。

### 流程 C：NuGet 包更新

1. **审计** — `dotnet list package --outdated` 和 `dotnet list package --vulnerable`。漏洞包紧急：更新、测试、部署。
2. **分类** — 补丁（批量安全）、次要（逐个）、主要（逐个，先读发布说明）。
3. **增量更新** — 一个包，然后 `dotnet build && dotnet test` 再下一个。批量更新使失败不可追溯。
4. **检查适配性** — 在添加新包前参考 `knowledge/package-recommendations.md`；优先使用内置 .NET 替代方案。移除 MediatR（商业许可 v13）？遵循 `knowledge/mediatr-to-mediator-migration.md` 中的分步指南。
5. **回滚** — git 回滚包更新；不要降级其他包来补偿。

### MCP 工具使用

- `find_symbol` / `find_references` — 定位实体，评估模式变更影响
- `get_type_hierarchy` — 实体继承（TPH/TPT/TPC）
- `get_project_graph` — 版本升级前 TFM 审计
- `get_diagnostics` — 迁移生成或升级后捕获警告

## 示例

```
用户: /migrate

Claude: 检查迁移状态...
  最后应用: 20250710_AddOrderTable
  检测到模型变更: Order 实体新增 ShippingAddress 属性。

  创建迁移: AddOrderShippingAddress
  审查 SQL (dotnet ef migrations script --idempotent)...
  - ALTER TABLE "Orders" ADD "ShippingStreet" text NULL
  - ALTER TABLE "Orders" ADD "ShippingCity" text NULL
  无数据丢失。无锁定风险。安全应用。

  应用迁移... 完成。构建：绿色。测试：34/34 通过。

  回滚（如需）:
  dotnet ef database update AddOrderTable --project src/Infrastructure --startup-project src/Api
```

## 相关

- `ef-core` — 实体配置、查询模式、迁移内部机制
- `/verify` — 迁移工作后的完整验证流程
- `/checkpoint` — 在风险迁移前提交安全状态
