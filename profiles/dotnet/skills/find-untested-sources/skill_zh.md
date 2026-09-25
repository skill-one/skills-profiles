# 查找未测试的源文件

## 目的

覆盖率工具回答的是“哪些行被执行了？”——它们需要一个绿色的构建和一次通过的测试运行，在一个真实仓库中，这需要几分钟到几十分钟。这个技能回答的问题是不同的，成本也低得多：

> “哪些源文件没有测试文件引用它们声明的任何类型/符号？”

这就是代理在编写新测试之前要问的问题——并且可以通过解析源文件在几秒钟内静态地回答，**无需构建、无需依赖解析、无需编译**。输出是一个确定性的测试配对映射，允许代理在首先读取整个代码库之前选择下一个要测试的文件。

## 两个引擎——选择一个

这个技能提供了两个可互换的分析器，它们具有兼容的 JSON 合约：

| 引擎 | 脚本 | 使用场景 |
|------|------|----------|
| **Roslyn (C#)** | `scripts/Find-UntestedSources.cs` | 仓库是 **仅限 .NET** 的。使用 Roslyn 语法 API 解析每个 `.cs` 文件，并进行严格的 **命名空间消歧**，因此在重复的短名称（如 `Settings` 或 `Context`）上更准确。 |
| **tree-sitter (多语言)** | `scripts/find_untested_sources.py` | 仓库**不完全是 C#**，或者你想在 C#、Python、TypeScript/JavaScript、Go、Java、Rust、Ruby、Kotlin、Swift、PowerShell 和 C++ 之间使用一个工具。 |

对于仅限 .NET 的仓库，**优先选择 Roslyn 引擎**——其感知命名空间的配对优于多语言引擎的标识符重叠。

## 必需的工作流程

1. 使用调用者指定的最窄仓库或包根目录。当请求标识子目录时，不要扫描父工作区。
2. 执行一次适当的分析器。不要用手动 globbing、文件名匹配或视觉检查来替换分析器执行。对于多语言分析，当答案必须区分已配对源和未配对源时，请传递 `--include-tested`。
   “仅静态配对”禁止编译目标仓库并运行其测试；它不禁止启动此技能的仅解析分析器。当调用者也说明“不要构建”时，请简要说明这种区别。
   将分析器依赖项视为环境先决条件：不要安装包、尝试错误的引擎、构建仓库，或在分析器调用失败时回退到手动扫描。相反，请报告先决条件失败。
3. 基于分析器的 JSON。保留其配对/未配对分类和建议的相对路径；不要猜测不同的路径。
4. 当调用者命名了子目录时，将分析器相对路径前缀添加到该子目录，以便报告的路径是工作区相对的。
5. 报告请求的结果以及静态配对覆盖的注意事项。不要附加构建、包安装、测试运行或覆盖率命令。当存在配对源时，命名其覆盖的测试文件，以便未配对分类是可审计的。

## 使用场景

- 用户询问“我应该根据源配对在哪里添加测试？”、“哪些文件没有测试？”、“查找未配对的源文件”或“给我一个静态测试差距列表”。
- 在调用测试生成代理之前，以生成源配对工作列表。
- 生成测试后，以验证每个新测试文件都与源文件配对。
- 列举“弱配对”的源文件（只有一个引用测试）以进行后续深度检查。

## 不应使用场景

- **行/分支覆盖率**——使用 `coverage-analysis`。
- **基于真实覆盖率数据的优先级**——使用 `coverage-analysis`。
- **CRAP 分数/风险热点**——使用 `coverage-analysis`。
- **现有测试是否强大？**——使用 `test-gap-analysis`（变异推理）或 `assertion-quality`。

## Roslyn 引擎 (C#)

### 先决条件

- 支持基于文件的应用的 .NET SDK (`dotnet run script.cs`)。在仓库的 `global.json` 中固定（SDK 11 预览或更高版本）。
- 除了首次运行时对 `Microsoft.CodeAnalysis.CSharp` 的初始 NuGet 还原之外，无需互联网访问。

### 使用方法

```powershell
# 从技能文件夹
dotnet run scripts/Find-UntestedSources.cs -- <仓库根目录> [--top N]

# 保存报告
dotnet run scripts/Find-UntestedSources.cs -- <仓库根目录> > pairing.json

# 迭代未测试列表，按最高 API 表面排序
$report = Get-Content pairing.json | ConvertFrom-Json
$report.untested | Select-Object -First 10 source, decl_count, suggested_test_path
```

诊断信息输出到 stderr；JSON 输出到 stdout。

### 输出模式

```jsonc
{
  "repo": "<绝对路径>",
  "elapsed_ms": 8883,
  "counts": {
    "source_files": 3036,
    "test_files": 867,
    "untested_files": 1852,
    "paired_files": 1184
  },
  "untested": [
    {
      "source": "src/Foo/Bar.cs",
      "decl_count": 8,            // 文件中类型声明的数量
      "suggested_test_path":      // 在发现的测试项目中镜像源路径
        "tests/Foo.Tests/Bar/BarTests.cs"
    }
  ],
  "source_to_tests": {
    "src/Foo/Baz.cs": [
      "tests/Foo.Tests/BazTests.cs",
      "tests/Foo.IntegrationTests/Scenarios/BazScenarios.cs"
    ]
  }
}
```

### 工作原理

1. **文件发现**——递归遍历，排除 `bin/`、`obj/`、`node_modules/`、`.git/`、`.vs/`、`packages/` 和任何点开头的子目录。跳过生成文件（`.g.cs`、`.Designer.cs`、`.AssemblyInfo.cs`）。
2. **测试与源分类**——向上遍历到最近的 `.csproj`，如果项目名称以 `.Tests`、`.Test`、`.UnitTests`、`.IntegrationTests`、`.E2E`、`.EndToEnd`、`.Spec`、`.Specs` 结尾，或者内容引用 `Microsoft.NET.Test.Sdk`、`MSTest.Sdk`、`Microsoft.Testing.Platform`、`xunit`、`NUnit`、`TUnit` 或 `<IsTestProject>true</IsTestProject>`，则将其标记为测试项目。
3. **源索引（并行）**——使用 `CSharpSyntaxTree.ParseText`（仅语法，不编译）解析每个源文件；记录每个 `BaseTypeDeclarationSyntax` / `DelegateDeclarationSyntax` 作为 `(ShortName, EnclosingNamespace, FilePath)`。
4. **测试扫描（并行）**——解析每个测试文件，收集 `using` 指令 + 包含命名空间，遍历每个 `IdentifierToken`，在短名索引中查找它，并**严格消歧**：标识符只有在声明的命名空间匹配测试文件的 `using` 指令、包含命名空间或它们的前缀之一时才会被分配。这避免了像 `Settings` 或 `Context` 这样的常见名称与每个项目匹配的噪声。
5. **配对与建议**——反转成 `source → [tests]`。从 `<ProjectReference>` 条目构建生产到测试项目映射；对于每个未测试的源，将其在项目中的相对路径镜像到引用的测试项目下以建议路径。
6. **JSON 发射**——按声明数量降序排列，然后按字母顺序排列。

## Polyglot 引擎 (tree-sitter)

### 先决条件

- Python 3.10+。
- `pip install tree-sitter-language-pack`（单个自包含的轮子，捆绑了 300 多种语言的解析器和高级 `process()` API）。无需原生构建，无需按语言安装语法。

### 使用方法

```powershell
# 从技能文件夹
python scripts/find_untested_sources.py <仓库根目录>

# 限制到一种语言（可重复）
python scripts/find_untested_sources.py <仓库根目录> --lang python --lang typescript

# 截断报告（按声明 API 表面排序的前 20）
python scripts/find_untested_sources.py <仓库根目录> --limit-untested 20 > pairing.json

# 迭代，按最高 API 表面排序
$report = Get-Content pairing.json | ConvertFrom-Json
$report.untested_sources | Select-Object -First 10 path, declaration_count, suggested_test_path
```

传递 `--include-tested` 以额外发出 `tested_sources`（默认省略以保持 LLM 消费的有效载荷小）。诊断信息输出到 stderr；JSON 输出到 stdout。

### 输出模式

```jsonc
{
  "repo_root": "<绝对路径>",
  "summary": {
    "source_files": 3138,
    "test_files": 761,
    "tested_source_files": 1419,
    "untested_source_files": 1719,
    "orphan_test_files": 15,
    "languages": ["csharp"]
  },
  "untested_sources": [
    {
      "path": "src/Foo/Bar.cs",
      "language": "csharp",
      "declaration_count": 8,
      "declarations": ["Bar", "BarOptions", "IBar", "..."],
      "suggested_test_path": "src/Foo/BarTests.cs"
    }
  ],
  "orphan_tests": [
    { "path": "tests/SomeIntegrationTest.cs", "language": "csharp" }
  ]
}
```

### 工作原理

1. **文件发现**——递归遍历，排除常见的构建/供应商目录（`bin`、`obj`、`node_modules`、`target`、`dist`、`build`、`vendor`、`__pycache__`、`.venv`、`.git`、…）和生成文件（`.d.ts`、`.g.cs`、`.Designer.cs`、`_pb2.py`、`*.min.js`、`AssemblyInfo.cs`、…）。
2. **语言检测**——`detect_language_from_path` 将扩展名映射到支持的语言；未知扩展名将被跳过。
3. **测试与源分类**——按语言路径启发式：

   | 语言 | 测试规则 |
   |---|---|
   | Python | 路径包含 `tests/`/`test/`；或文件名以 `test_` 开头或以 `_test.py` 结尾；或 `conftest.py`。 |
   | JS/TS/TSX | 路径包含 `__tests__`、`tests`、`test`、`spec`、`e2e`；或文件名包含 `.test.`/`.spec.`。 |
   | Go | 文件名以 `_test.go` 结尾。 |
   | Java | 路径包含 `test`/`tests`；或文件名以 `Test.java`/`Tests.java` 结尾。 |
   | Rust | 路径包含 `tests/`/`benches/`. |
   | C# | 路径包含 `tests/`；或项目段以 `.Tests`/`.Test`/`.UnitTests`/`.IntegrationTests` 结尾；或文件名以 `Tests`/`Test` 结尾。 |
   | Ruby | 路径包含 `spec/`/`test/`；或文件名以 `_spec.rb`/`_test.rb` 结尾。 |
   | Kotlin | 路径包含 `test/`/`tests/`/`spec/`；或文件名以 `Test.kt`/`Tests.kt`/`Spec.kt` 结尾。 |
   | Swift | 路径包含 `test/`/`tests/`/`uitests/`/`integrationtests/`（不区分大小写）；或文件名以 `Test.swift`/`Tests.swift` 结尾。 |
   | PowerShell | 路径包含 `test/`/`tests/`/`pester/`；或文件名以 `.Tests.ps1`/`.Test.ps1` 结尾。 |
   | C++ | 路径包含 `test/`/`tests/`/`testing/`；或文件名以 `test_` 开头或以 `_test.cpp`/`_tests.cpp` 结尾。 |

4. **按文件提取**——`process(text, ProcessConfig(structure, imports, symbols))` 返回声明的项、原始导入语句和扁平声明的名称列表。
5. **配对**——对于每个测试文件，联合**导入解析**（按语言，例如 Python `from pkg.mod import x` → `pkg/mod.py`；Java `import a.b.C;` → `a/b/C.java`；C# `using` 是命名空间而非文件，所以无操作）与**标识符重叠**（单词状标记，长度 ≥ 4，与声明名称匹配）。
6. **JSON 发射**——`untested_sources` 按声明数量降序排列。

## 限制（对代理要诚实）

两个引擎都是静态的、仅解析启发式方法，它们在精度上稍作牺牲，以换取比覆盖率低几个数量级的成本。已知差距：

- **反射 / DI 解析的类型** 仅通过字符串名称或容器解析引用不会被检测到——类型的短名称从未出现在测试源中。
- **扩展方法** 作为实例方法调用（C#）：声明静态类的名称未命名，因此其文件未被归功。
- **`var`、目标类型 `new()`、模式匹配** 失去类型标记；通常文件级联合仍然可以通过其他引用捕获它。
- **短标识符名称**（多语言，< 4 个字符）被丢弃，以避免在 `id`、`db`、`Tag` 等名称上产生噪声配对。
- **单仓库路径别名**（TS 路径映射、Java module-info）未解析；后缀匹配回退可能会选择错误的源，如果两个文件共享尾随路径段。

对于这些情况，请在代理已经筛选的未配对候选者上运行实际覆盖率 (`coverage-analysis`)。

始终将最终结果标记为静态配对启发式，而不是行或分支覆盖率的证据。即使每个请求的源文件都有明显的匹配或缺失测试，也要包含这一注意事项。

## 代理应消费的输出

- `untested[*].source` / `untested_sources[*].path` — 选择下一个要测试的源文件（按声明数量降序排列）。
- `*.suggested_test_path` — 新测试文件的即插即用目标；Roslyn 引擎尊重已经 `<ProjectReference>` 源项目的测试项目，因此不需要 `dotnet sln add`。多语言引擎可能会在无法发现测试根时建议同位测试。当源兄弟已经配对时，其测试目录是既定惯例，必须为缺失的兄弟重用，而不是回退到源同位。
- `source_to_tests` (Roslyn) / `--include-tested` `tested_sources` (polyglot) — 验证新编写的测试文件是否在目标源列表中。
- `orphan_tests` (polyglot) — 没有引用任何同语言源文件的测试；对筛选过时或仅集成测试有用。
