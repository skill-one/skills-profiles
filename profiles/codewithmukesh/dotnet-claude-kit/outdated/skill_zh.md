# /outdated

## 什么是

一个三层依赖健康报告：

1. **库存** — 每个项目中的 `PackageReference`，包含 TFMs 和中心化包管理意识，通过 `get_nuget_packages` MCP 工具（无需网络，令牌消耗少）。
2. **陈旧性 + 漏洞** — 当前版本与最新稳定版本对比，以及已知 CVE，通过 `dotnet` CLI。
3. **许可证筛查** — 标记已迁移至商业许可证的包，以便 `dotnet outdated --upgrade` 不会在无声中改变您的法律地位。

输出是一个优先级排序的表格 — 漏洞优先，许可证陷阱其次，陈旧性最后 — 每行附带推荐操作。

## 何时使用

- "检查过时包"、"包审计"、"依赖健康"
- 在 .NET 版本升级前（与 `/migrate` Flow B 配对）
- 继承不熟悉的代码库后
- Dependabot/NuGet 审计警告出现，您想了解完整情况
- 在长期项目中定期执行 — 每季度是一个好的节奏

## 如何使用

**步骤 1：库存（MCP，无需网络）**

```
get_nuget_packages()                          -- 整个解决方案
get_nuget_packages(projectFilter: "Api")      -- 或单个项目
```

返回每个项目的 `{Name, TargetFramework, Cpm, Packages: [{Id, Version}]}`。
注意 `Cpm: true` — 更新应属于 `Directory.Packages.props`，而不是 csproj。在此期间标记跨项目的混合 TFMs。

**步骤 2：陈旧性与漏洞（CLI）**

```bash
dotnet list package --outdated
dotnet list package --vulnerable --include-transitive
```

两者都需要先成功还原。如果还原失败，请在审计前修复 — 破损的锁定状态会使版本输出不可靠。

**步骤 3：许可证筛查**

将库存与已知的商业迁移（`knowledge/package-recommendations.md` 中的完整理由）进行对比：

| 包名 | 商业起始版本 | 免费替代品 |
|---|---|---|
| MediatR | 13+ (Lucky Penny, RPL) | `Mediator` (martinothamar) — 源生成，MIT |
| MassTransit | 9+ (v8 Apache，补丁截至 2026 年后 EOL) | Wolverine 6.x，或短期停留在 v8 |
| FluentAssertions | 8+ (v7 保持 Apache，冻结) | xUnit 内置 `Assert` (kit 默认)，Shouldly，AwesomeAssertions |
| AutoMapper | 15+ (Lucky Penny) | 手动映射 (kit 默认) 或 Mapperly (MIT) |

当项目处于免费主版本，而一个简单的 "更新所有" 会跨越边界时，会触发许可证标记 — 这就是此步骤存在的目的。

**步骤 4：报告**

一个优先级排序的表格：

| 优先级 | 含义 | 操作 |
|---|---|---|
| VULNERABLE | 当前版本存在已知 CVE | 立即更新，测试，部署 |
| LICENSE | 下一个主版本跨越商业边界 | 保持在边界以下或计划迁移 |
| MAJOR | 落在主版本之后（可能存在破坏性变更） | 逐个更新，先查看发布说明 |
| MINOR/PATCH | 常规漂移 | 批量打补丁；主版本逐个 |

**步骤 5：执行（可选）**

提供通过 `/migrate` Flow C 执行更新的选项 — 逐个包，每次 `dotnet build && dotnet test` 之间执行。永远不要批量主版本更新：批量失败无法归因。

### 使用的 MCP 工具

- `get_nuget_packages` — 库存，CPM 检测，TFM 审计
- `get_diagnostics` — 验证更新后解决方案是否仍能干净编译

## 示例

```
用户: /outdated

Claude: 正在库存包（get_nuget_packages）...
  3 个项目，CPM 启用（Directory.Packages.props），所有 net10.0。

  检查版本和 CVE...

  | 包名                  | 当前 | 最新  | 优先级   | 操作                          |
  |--------------------------|---------|---------|------------|---------------------------------|
  | System.Text.Json (传递) | 10.0.2  | 10.0.10 | VULNERABLE | 立即更新 (CVE-2026-XXXX)      |
  | MassTransit              | 8.3.0   | 9.1.2   | LICENSE    | v9 是商业的。停留在 v8    |
  |                          |         |         |            | (EOL 截至 2026) 或计划 Wolverine|
  | Serilog.AspNetCore       | 9.0.0   | 10.0.0  | MAJOR      | 单独更新，检查接收器兼容性 |
  | FluentValidation         | 12.0.1  | 12.1.1  | PATCH      | 与其他补丁一起批量更新        |

  1 个漏洞，1 个许可证陷阱，1 个主版本，1 个补丁。
  要我通过 /migrate Flow C 应用这些吗？
```

## 相关

- `/migrate` — Flow C 执行此报告推荐的更新
- `knowledge/package-recommendations.md` — 审核的包 + 许可证详情
- `knowledge/mediatr-to-mediator-migration.md` — MediatR 逐步退出指南
- `/verify` — 应用更新后的完整管道
