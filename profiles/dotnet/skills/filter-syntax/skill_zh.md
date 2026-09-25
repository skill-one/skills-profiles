# 测试过滤器语法参考

过滤器语法取决于**平台**和**测试框架**。

## VSTest 过滤器 (MSTest, xUnit v2, NUnit on VSTest)

```bash
dotnet test --filter <EXPRESSION>
```

表达式语法：`<属性><运算符><值>[|&<表达式>]`

**运算符：**

| 运算符 | 含义 |
|----------|---------|
| `=` | 精确匹配 |
| `!=` | 不精确匹配 |
| `~` | 包含 |
| `!~` | 不包含 |

**组合器：`|` (OR), `&` (AND)。括号用于分组：`(A|B)&C`

**框架支持的属性：**

| 框架 | 属性 |
|-----------|-----------|
| MSTest | `FullyQualifiedName`, `Name`, `ClassName`, `Priority`, `TestCategory` |
| xUnit | `FullyQualifiedName`, `DisplayName`, `Traits` |
| NUnit | `FullyQualifiedName`, `Name`, `Priority`, `TestCategory` |

没有运算符的表达式被视为 `FullyQualifiedName~<值>`。

**示例 (VSTest)：**

```bash
# 运行名称包含 "LoginTest" 的测试
dotnet test --filter "Name~LoginTest"

# 运行特定的测试类
dotnet test --filter "ClassName=MyNamespace.MyTestClass"

# 运行特定类别的测试
dotnet test --filter "TestCategory=Integration"

# 排除特定类别
dotnet test --filter "TestCategory!=Slow"

# 组合：类 AND 类别
dotnet test --filter "ClassName=MyNamespace.MyTestClass&TestCategory=Unit"

# 两个类中的任意一个
dotnet test --filter "ClassName=MyNamespace.ClassA|ClassName=MyNamespace.ClassB"
```

## MTP 过滤器 — MSTest 和 NUnit

MSTest 和 NUnit on MTP 使用与 VSTest 相同的 `--filter` 语法（相同的属性、运算符和组合器）。唯一区别在于如何传递标志：

```bash
# .NET SDK 8/9 (在 -- 之后)
dotnet test -- --filter "Name~LoginTest"

# .NET SDK 10+ (直接)
dotnet test --filter "Name~LoginTest"
```

## MTP 过滤器 — xUnit (v3)

MTP 上的 xUnit v3 使用框架特定的过滤标志，而不是通用的 `--filter` 表达式：

| 标志 | 描述 |
|------|-------------|
| `--filter-class "name"` | 运行给定类中的所有测试 |
| `--filter-not-class "name"` | 排除给定类中的所有测试 |
| `--filter-method "name"` | 运行特定的测试方法 |
| `--filter-not-method "name"` | 排除特定的测试方法 |
| `--filter-namespace "name"` | 运行命名空间中的所有测试 |
| `--filter-not-namespace "name"` | 排除命名空间中的所有测试 |
| `--filter-trait "name=value"` | 运行具有匹配特性的测试 |
| `--filter-not-trait "name=value"` | 排除具有匹配特性的测试 |

可以使用单个标志指定多个值：`--filter-class Foo Bar`。

```bash
# .NET SDK 8/9
dotnet test -- --filter-class "MyNamespace.LoginTests"

# .NET SDK 10+
dotnet test --filter-class "MyNamespace.LoginTests"

# 组合：命名空间 + 特性
dotnet test --filter-namespace "MyApp.Tests.Integration" --filter-trait "Category=Smoke"
```

### xUnit v3 查询过滤语言

对于复杂表达式，使用 `--filter-query` 并使用路径段语法：

```text
/<assemblyFilter>/<namespaceFilter>/<classFilter>/<methodFilter>[traitName=traitValue]
```

每个段匹配：程序集名称、命名空间、类名、方法名。在任意段中使用 `*` 表示“匹配所有”。文档：<https://xunit.net/docs/query-filter-language>

```shell
# xUnit.net v3 MTP — 使用查询语言 (程序集/命名空间/类/方法[特性])
dotnet test -- --filter-query "/*/*/*IntegrationTests*/*[Category=Smoke]"
```

## MTP 过滤器 — TUnit

TUnit 使用 `--treenode-filter` 并使用基于路径的语法：

```text
--treenode-filter "/<Assembly>/<Namespace>/<ClassName>/<TestName>"
```

通配符 (`*`) 支持在任意段中使用。过滤运算符可以附加到测试名称以进行基于属性的过滤。

| 运算符 | 含义 |
|----------|---------|
| `*` | 通配符匹配 |
| `=` | 精确属性匹配 (例如，`[Category=Unit]`) |
| `!=` | 排除属性值 |
| `&` | AND (组合条件) |
| `\|` | OR (在段内，需要括号) |

**示例 (TUnit)：**

```bash
# 类中的所有测试
dotnet run --treenode-filter "/*/*/LoginTests/*"

# 特定的测试
dotnet run --treenode-filter "/*/*/*/AcceptCookiesTest"

# 通过命名空间前缀 (通配符)
dotnet run --treenode-filter "/*/MyProject.Tests.Api*/*/*"

# 通过自定义属性
dotnet run --treenode-filter "/*/*/*/*[Category=Smoke]"

# 通过属性排除
dotnet run --treenode-filter "/*/*/*/*[Category!=Slow]"

# 跨类的 OR
dotnet run --treenode-filter "/*/*/(LoginTests)|(SignupTests)/*"

# 组合：命名空间 + 属性
dotnet run --treenode-filter "/*/MyProject.Tests.Integration/*/*/*[Priority=Critical]"
```

## VSTest → MTP 过滤器转换 (用于迁移)

**MSTest、NUnit 和 xUnit.net v2 (使用 `YTest.MTP.XUnit2`)**：VSTest `--filter` 语法在 VSTest 和 MTP 上完全相同。无需更改。

**xUnit.net v3 (原生 MTP)**：xUnit.net v3 不支持 MTP 上的 VSTest `--filter` 语法。使用 xUnit.net v3 的原生选项转换过滤器：

| VSTest `--filter` 语法 | xUnit.net v3 MTP 等价项 | 备注 |
|---|---|---|
| `FullyQualifiedName~ClassName` | `--filter-class *ClassName*` | 需要通配符进行子字符串匹配 |
| `FullyQualifiedName=Ns.Class.Method` | `--filter-method Ns.Class.Method` | 精确匹配完全限定方法 |
| `Name=MethodName` | `--filter-method *MethodName*` | 通配符用于子字符串匹配 |
| `Category=Value` (特性) | `--filter-trait "Category=Value"` | 通过特性名称/值对过滤 |
| 复杂表达式 | `--filter-query "expr"` | 使用 xUnit.net 查询过滤语言 (见上文) |
