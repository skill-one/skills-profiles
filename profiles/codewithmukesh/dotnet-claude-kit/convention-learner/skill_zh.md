# 规范学习器

## 核心原则

1. **先观察后执行** — 在强制规范之前，必须先分析现有的代码库。一个包含 200 个 `internal sealed class` 处理器的项目不应再引入新的 `public class` 处理器。先检测，再匹配。
2. **项目规范优先于通用规则** — 如果项目使用 `*Service` 而不是 `*Handler`，即使工具包默认值不同，也应遵循项目的规范。显式的 `.editorconfig` 和 `Directory.Build.props` 规则始终优先。
3. **使用 MCP 工具进行分析** — `get_public_api` 揭示命名模式，`get_project_graph` 显示结构规范，`detect_antipatterns` 跟踪质量趋势。工具提供客观数据；文件读取提供确认。
4. **记录发现** — 在检测到规范后，建议将其添加到项目的 CLAUDE.md 中。未记录的规范会在原始开发人员离开时丢失。
5. **一致性优于完美** — 一个使用 `snake_case` 数据库列的项目比一个一半使用 `snake_case` 一半使用 `PascalCase` 的项目更好。匹配现有模式，即使另一种规范在理论上更优越。

## 模式

### 规范检测流程

系统分析以理解项目的编码规范。在加入现有项目或生成新代码之前运行此流程。

**步骤 1：项目结构分析**
```
→ get_project_graph
  检测：
  - 项目命名：PascalCase？点分隔？（MyApp.Domain vs Domain）
  - 层级组织：按层级（Domain/Application/Infrastructure）或按功能组织？
  - 测试项目命名：*.Tests, *.UnitTests, *.IntegrationTests？
  - 共享项目：Common/, Shared/, BuildingBlocks/？
```

**步骤 2：类型命名模式**
```
→ get_public_api (在 3-5 个跨不同层级的键类型上)
  检测：
  - 类修饰符：sealed？internal？internal sealed？
  - 接口前缀：I*（标准）或无前缀？
  - 后缀规范：Handler, Service, Repository, Validator, Endpoint？
  - 记录使用：用于 DTO？用于值对象？用于命令/查询？
  - 主构造函数使用：一致？选择性？
```

**步骤 3：文件夹结构模式**
扫描文件系统以寻找结构规范：
- 功能文件夹：`Features/{FeatureName}/` 将所有文件放在一起？
- 层级文件夹：`Controllers/`, `Services/`, `Repositories/` 分开？
- 共享模式：`Common/`, `Extensions/`, `Middleware/`？
- 配置位置：根目录？`Config/` 文件夹？`Infrastructure/`？

**步骤 4：配置检测**
检查显式的规范执行器：

```
→ 查找 Directory.Build.props
  - TreatWarningsAsErrors？
  - Nullable 全局启用？
  - ImplicitUsings？
  - AnalysisLevel？

→ 查找 .editorconfig
  - 命名规则：camelCase 字段？_前缀的私有成员？
  - 代码风格：var 偏好，表达式主体，using 位置

→ 查找 global.json
  - SDK 版本固定？
  - Roll-forward policy？
```

**步骤 5：构建规范总结**
将发现结果汇总为结构化摘要：

```markdown
## 检测到的规范

### 命名
- 类：`internal sealed class`（95% 的处理器/服务）
- 后缀：处理器以 `Handler` 结尾，验证器以 `Validator` 结尾
- 记录：用于 DTO 和命令/查询

### 结构
- 架构：垂直切片架构
- 功能：`Features/{Name}/` 将命令、处理器、验证器、端点放在一个文件中

### 代码风格
- 主构造函数：一致用于依赖注入
- Nullable：全局启用，无抑制（`!`）使用
- 命名空间作用域：100% 一致
```

按需添加类别：EF Core（配置、命名、迁移）、测试（框架、命名、固定件）等。

### 规范执行

在生成新代码或审查现有代码时应用检测到的规范。

**生成代码时：**
匹配每个检测到的模式：

```csharp
// 如果现有处理器是：internal sealed class + 主构造函数
// 生成匹配：
internal sealed class CreateProductHandler(AppDbContext db, TimeProvider clock)
{
    // 不是：public class CreateProductHandler
    // 不是：internal class CreateProductHandler (缺少 sealed)
}
```

```csharp
// 如果现有 DTO 是带 init 属性的记录
// 生成匹配：
public record ProductResponse(Guid Id, string Name, decimal Price);
// 不是：public class ProductResponse { public Guid Id { get; set; } }
```

**审查代码时：**
标记与检测到的规范偏差：

```
⚠️ 规范违规：CreateOrderHandler 是 `public class` 但项目规范
   是 `internal sealed class`（在 12/12 现有处理器中检测到）。
   更改为：internal sealed class CreateOrderHandler
```

**建议执行规则：**
检测到规范后，建议 `.editorconfig` 规则自动执行它们：

```ini
# 基于检测到的规范建议的 .editorconfig 规则
dotnet_diagnostic.CA1852.severity = warning           # 封装内部类型
csharp_style_namespace_declarations = file_scoped:warning
csharp_style_prefer_primary_constructors = true:suggestion
# 如果检测到，添加 dotnet_naming_rule 条目用于私有字段前缀 (_camelCase)
```

### 反模式跟踪

使用 `detect_antipatterns` 跨会话跟踪重复出现的质量问题。

**定期检查：**
```
→ detect_antipatterns (范围：解决方案)
  跟踪：
  - 是否相同模式重复出现？（DateTime.Now 不断出现）
  - 是否出现新模式？（新模块中的 new HttpClient）
  - 数量趋势上升或下降？
```

**优先级：**
```
| 反模式 | 数量 | 趋势 | 优先级 |
|-------|------|------|--------|
| DateTime.Now | 12 | ↑ +3 | 高 — 添加到 CLAUDE.md 规范 |
| async void | 1 | → 相同 | 中 — 一次性修复 |
| new HttpClient | 0 | ↓ -2 | 低 — 已在修复 |
```

当模式重复出现时，将显式规则添加到 CLAUDE.md：
```markdown
## 规范
- **绝不使用 DateTime.Now** — 使用 TimeProvider.GetUtcNow()（12 次违规，正在修复）
```

## 反模式

### 未检测即执行

```
# BAD — 在具有自身规范的项目上强制工具包默认值
"All handlers should be internal sealed class"
# 但这个项目使用 public class 并实现接口进行测试
```

```
# GOOD — 先检测，再遵循现有规范
→ get_public_api 揭示：8/8 处理器是 `public class` 实现 `IHandler<T>`
"This project uses public handlers with interfaces. 匹配该规范。"
```

### 覆盖显式项目规则

```
# BAD — 因为工具包不同而忽略 .editorconfig
# .editorconfig 说：csharp_style_expression_bodied_methods = false
# 但仍然生成表达式主体方法
```

```
# GOOD — .editorconfig 和 Directory.Build.props 始终优先
"您的 .editorconfig 禁用表达式主体方法。
我将使用块主体方法以匹配您的项目设置。"
```

### 将通用规范应用于非传统项目

```
# BAD — 在 VSA 项目上强制 Clean Architecture 命名
"You need a Services/ 文件夹和 Repositories/ 文件夹"
# 但这个项目使用功能文件夹并将所有文件放在一起
```

```
# GOOD — 匹配项目的组织规范
"This project 使用功能文件夹。我将添加新功能
在 Features/Shipping/ 并将所有相关文件放在一起。"
```

### 无证据记录规范

```
# BAD — 基于读取一个文件得出的 "规范"
"规范：到处使用 var"（在一个方法中看到 var）
```

```
# GOOD — 仅记录在多个文件中确认的模式
→ get_public_api 在 5 个类型上：100% 使用显式类型用于非明显情况
"规范：对于非明显情况（如方法返回）使用显式类型，
对于明显情况（如 new MyClass()）使用 var。跨 5 个文件确认。"
```

## 决策指南

| 场景 | 操作 | 工具 |
|------|------|------|
| 加入现有项目 | 运行完整规范检测流程 | get_project_graph, get_public_api |
| 生成新代码 | 首先检查检测到的规范 | 先前检测结果 |
| 审查代码 | 标记规范偏差 | get_public_api + 比较 |
| 规范冲突（工具包 vs 项目） | **项目优先** | — |
| 规范冲突（团队分歧） | 记录两者，建议 .editorconfig | — |
| 未检测到规范 | 使用工具包默认值，记录它们 | architecture-advisor 技能 |
| 重复出现的反模式 | 添加到 CLAUDE.md 规范 | detect_antipatterns |
| 新团队成员入职 | 运行检测，生成规范文档 | 完整检测流程 |
| .editorconfig 存在 | 信任它，不要覆盖 | 读取 .editorconfig |
| 无 .editorconfig | 建议基于检测到的模式创建一个 | 检测 + 生成 |
| 模式出现一次 | 通过 `instinct-system` 技能以 0.3 置信度创建直觉 | instinct-system |
| 模式确认 3 次以上 | 直觉自动提升到 0.7，建议添加到 CLAUDE.md | instinct-system |
