# 模板创建

这项技能帮助代理创建和验证自定义的 `dotnet new` 模板。它指导从现有项目引导模板，并在发布前验证 `template.json` 文件是否存在创建问题。

## 何时使用

- 用户希望从现有的 .csproj 创建可重用的模板
- 用户希望在发布前验证他们正在创建的 template.json
- 用户正在从零开始设置 `.template.config/template.json`
- 用户希望将模板打包用于 NuGet 分发

## 不应使用的情况

- 用户希望查找或使用现有模板 — 路由到 `template-discovery` 或 `template-instantiation`
- 用户有与模板创建无关的 MSBuild 问题 — 路由到 `dotnet-msbuild` 插件

## 输入

| 输入 | 必填 | 描述 |
|-------|----------|-------------|
| 源项目路径 | 创建时 | 用于模板源的 .csproj 路径 |
| template.json 路径 | 验证时 | 用于验证的现有 template.json 路径 |
| 模板名称 | 创建时 | 模板的可读名称 |
| 短名称 | 推荐使用 | 用于 `dotnet new <shortname>` 使用的短名称 |

## 工作流程

### 改变答案的规则

使用这些结构，不要从其他模板功能中发明字段。

**交付请求的工件。** 当用户说 "显示"、"写入" 或 "给我内容" 时，即使您也将其写入磁盘，也要在最终响应中放入完整的 JSON/XML。永远不要编辑此技能的 `SKILL.md` 或插件文档，以替代为用户创建模板。仅在用户请求文件更改并且目标模板/项目存在时创建或修改模板文件。

| 需求 | 正确结构 | 永远不要使用 |
|------|-------------------|-----------|
| .csproj 中的条件 XML | 如 `<!--#if (database == "SqlServer") -->` 和 `<!--#endif -->` 等 XML 注释围绕完整元素 | 裸 `#if` 行，这会使 XML 无效 |
| 恢复生成的项目 | 恢复操作 `210D431B-A78B-4D2F-B762-4ED3E3EA9025`；使用 `primaryOutputs` 或包含源模板路径/通配符的 `args.files` | 恢复操作上的 `run-script` 字段，如 `executable` |
| 限制为 SDK 主机 | 一个 `host` 约束，其 `args` 是一个包含 `{ "hostname": "dotnetcli" }` 的数组；其可选的 `version` 限制主机/CLI 版本 | 使用主机 `version` 时，要求是活动的 SDK 版本、无效的主机 ID `dotnet-cli` 或不相关的 `pattern` / `value` 字段 |
| 限制活动的 SDK 版本 | 一个 `sdk-version` 约束，其 `args` 中包含 NuGet 版本/范围字符串 | 除非模板确实需要，否则机器特定的确切补丁 |
| 保留 CPM | 保持生成的 `PackageReference` 项无版本，并在模板自包含时打包拥有 `Directory.Packages.props` | 添加内联 `Version` 属性 |
| 打包模板 | 一个 `<PackageType>Template</PackageType>` 的 pack 项目，模板内容打包在 `content/` 下方 | 描述布局而不显示请求的项目文件 |

### 第 1 步：从现有项目引导

分析源 `.csproj` 并创建 `.template.config/template.json`：

1. 默认情况下将源项目复制到专用的模板源目录，保留原始项目未受影响。仅在用户明确要求那种布局时才原地修改原始项目。
2. 在模板源目录内创建 `.template.config`。
3. 生成 `template.json`，包含 `identity`（反向 DNS）、`name`、`shortName`、`sourceName`（用于替换的项目名称）、`classifications` 和 `tags`
4. 从源保留 — 通用 `dotnet new` 模板经常在这些方面出错，因此请验证每个都从原始 `.csproj` 转移过来：
   1. **SDK 类型** — `Microsoft.NET.Sdk`、`Microsoft.NET.Sdk.Web`、`Microsoft.NET.Sdk.Worker` 等
   2. **分析器/包引用元数据** — `PrivateAssets`、`IncludeAssets`、`ExcludeAssets`
   3. **`OutputType` 和其他关键属性** — `TreatWarningsAsErrors`、`Nullable`、`LangVersion`
   4. **CPM 参与** — 当存在 `Directory.Packages.props` 时，不使用内联 `Version` 属性
   5. **自定义构建属性/目标** 和 `Directory.Build.props` 约定
   6. **仓库约定** — 文件夹布局、命名、`global.json` SDK 固定

最小示例：
```json
{
  "$schema": "http://json.schemastore.org/template",
  "author": "MyOrg",
  "classifications": ["Library"],
  "identity": "MyOrg.Templates.MyLib",
  "name": "My Library Template",
  "shortName": "mylib",
  "sourceName": "MyLib",
  "tags": { "language": "C#", "type": "project" }
}
```

**必须输出 — 不要停留在最小桩。** 为实际源项目编写完整的 `.template.config/template.json`，然后发出简短的 **约定保留** 确认，以便用户可以看到没有内容被无声地遗漏。这种转移是此技能的全部价值；一个丢失这些的通用 `dotnet new` 模板，这就是为什么创建与手写桩绑定在一起的原因。

| 源 `.csproj` 设置 | 转移过来？ | 如何 |
|--------------------------|---------------|-----|
| SDK (`Microsoft.NET.Sdk.*`) | ✅ | 模板内容 `.csproj` 使用相同的 SDK |
| `TreatWarningsAsErrors` / `Nullable` / `LangVersion` | ✅ | 原封不动地保留在模板 `.csproj` 中 |
| PackageReference `PrivateAssets` / `IncludeAssets` / `ExcludeAssets` | ✅ | 保留每个引用的元数据 |
| CPM (`Directory.Packages.props` 存在) | ✅ | `ManagePackageVersionsCentrally` 保持启用，并且不发出内联 `Version` 属性 |

标记您有意省略的任何行，并附上原因 — 永远不要使其隐含。

### 第 2 步：验证 template.json

使用 **template-validation** 技能验证生成的 `template.json`（它拥有完整的规则集 — 必填字段、身份格式、保留的 shortName 冲突、参数数据类型、后操作、约束和标签）。

验证内容的快速总结：
- **必填字段** — `identity`、`name` 和 `shortName` 必须存在。
- **shortName 冲突** — 避免与 `dotnet new` 子命令冲突的名称。从安装的 SDK 的 `dotnet new --help` 的 `Commands:` 部分读取权威集，并且不要硬编码它（它可以在版本之间更改）；当前 SDK 的说明示例是 `install`、`uninstall`、`update`、`list`、`search`、`details`、`create`。冲突发生是因为 `dotnet new <name>` 会被解析为同名子命令。顶级 `dotnet` 动词如 `build`、`run`、`test` 和 `publish` 不冲突。运行 `dotnet new list` 以确认名称未被占用。
- **参数、后操作、标签** — 参考模板验证以获取完整规则，包括有效数据类型列表。

### 第 3 步：完善模板

根据验证结果和用户需求：

1. **添加参数**，包含适当的类型（字符串、布尔值、选择），默认值和描述
2. **添加条件内容**，使用文件类型的有效语法。在 XML 中使用模板指令在 XML 注释内，而不是裸预处理器行：

   ```xml
   <!--#if (database == "SqlServer") -->
   <PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" />
   <!--#endif -->
   <!--#if (database == "Postgres") -->
   <PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" />
   <!--#endif -->
   ```
3. **配置后操作**，用于解决方案添加、恢复或自定义脚本
4. **设置约束**，限制模板支持哪些 SDK 或工作负载
5. **添加分类** 和标签以提高可发现性

对于恢复后操作，当项目路径已知时，优先使用 `primaryOutputs`：

```json
"primaryOutputs": [{ "path": "MyProject.csproj" }],
"postActions": [{
  "description": "恢复 NuGet 包。",
  "manualInstructions": [{ "text": "运行 'dotnet restore'。" }],
  "actionId": "210D431B-A78B-4D2F-B762-4ED3E3EA9025",
  "continueOnError": true
}]
```

如果需要 `args.files`，其路径在重命名之前与 **源模板** 匹配，例如 `"files": ["**/*.csproj"]`。解释这种区别。

### 第 4 步：本地测试模板

对于从现有项目创建的请求，此步骤是必需的而不是可选的：
安装编写的模板，运行干运行，在临时输出文件夹中实例化它，并构建生成的项目。报告每个观察到的结果；仅检查 `template.json` 不能证明可重用模板工作正常。

```bash
dotnet new install ./path/to/template/root
dotnet new mylib --name TestProject --dry-run
dotnet new mylib --name TestProject --output ./test-output
dotnet build ./test-output/TestProject
```

当请求打包时，包括完整的 pack 项目，而不仅仅是目录树：

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <PackageId>Contoso.ProjectTemplates</PackageId>
    <PackageType>Template</PackageType>
    <TargetFramework>net8.0</TargetFramework>
    <IncludeBuildOutput>false</IncludeBuildOutput>
    <NoWarn>$(NoWarn);NU5128</NoWarn>
  </PropertyGroup>
  <ItemGroup>
    <Compile Remove="**\*" />
    <Content Include="templates\**\*" Pack="true" PackagePath="content\" />
  </ItemGroup>
</Project>
```

pack 项目的目标框架仅适用于内容打包项目；它不会重新目标 `templates/` 内的项目。除非打包项目本身使用新的构建功能，否则优先使用广泛支持的受支持框架。

对于自包含的 CPM 模板，打包的 `Directory.Packages.props` 必须包含 `<ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>`，并且每个无版本的 `PackageReference` 都必须有匹配的 `PackageVersion`。将 props 文件保持在预期的生成仓库根目录；不要在项目附近放置一个副本，那里它会更改查找。

## 验证

- [ ] `template.json` 通过手动验证，无错误
- [ ] 模板身份和 shortName 是唯一的且有意义的
- [ ] 所有参数都有描述和适当的默认值
- [ ] 模板可以成功安装、干运行和实例化
- [ ] 创建的项目使用 `dotnet build` 清洁构建
- [ ] 条件内容对于所有参数组合都产生正确的输出
- [ ] XML 模板指令被包裹在 XML 注释中，并且生成的项目可以解析
- [ ] 主机约束使用 `args[].hostname`；恢复操作使用 `primaryOutputs` 或 `args.files`

## 常见陷阱

| 陷阱 | 解决方案 |
|---------|----------|
| 身份格式问题 | 使用反向 DNS 格式（例如，`MyOrg.Templates.WebApi`）。避免空格或特殊字符。 |
| ShortName 与 CLI 命令冲突 | 避免与 `dotnet new` 子命令匹配的名称；从 `dotnet new --help` 读取实时集，并且不要硬编码它（说明示例：`install`、`uninstall`、`update`、`list`、`search`、`details`、`create`）。顶级动词如 `build`/`run`/`test`/`publish` 是可以的。运行 `dotnet new list` 看看名称是否已被占用。 |
| 缺少参数描述 | 每个参数都应该有 `description` 和 `displayName` 以提高可发现性。 |
| 未测试所有参数组合 | 使用 `dotnet new <template> --dry-run` 并用不同的参数值来验证条件内容是否正确工作。 |
| 模板中硬编码版本 | 使用 `sourceName` 替换项目名称，并考虑参数化框架版本。 |
| 未设置分类 | 添加适当的 `classifications`（例如，`["Web", "API"]`）以提高模板可发现性。 |
| 重复使用来自不同约束或后操作的字段 | 遵循精确的架构：`host.args[].hostname`，并恢复 `args.files` 而不是 `run-script` 字段。 |

## 更多信息

- [dotnet new 的自定义模板](https://learn.microsoft.com/dotnet/core/tools/custom-templates) — 官方创建指南
- [template.json 参考](https://github.com/dotnet/templating/wiki/Reference-for-template.json) — 完整架构参考
- [模板引擎 Wiki](https://github.com/dotnet/templating/wiki) — 模板引擎内部结构
