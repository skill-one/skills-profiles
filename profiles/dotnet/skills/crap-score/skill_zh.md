# CRAP 分数分析

计算 .NET 方法的 CRAP（变更风险反模式）分数，以识别既复杂又测试不足的代码。

## 背景

CRAP 分数将 **圈复杂度** 和 **代码覆盖率** 结合为一个单一指标：

$$\text{CRAP}(m) = \text{comp}(m)^2 \times (1 - \text{cov}(m))^3 + \text{comp}(m)$$

其中：

- $\text{comp}(m)$ = 方法 $m$ 的圈复杂度
- $\text{cov}(m)$ = 方法 $m$ 的代码覆盖率比率（0.0 到 1.0）

| CRAP 分数 | 风险等级 | 解释 |
|------------|------------|----------------|
| < 5        | 低        | 简单且测试充分 |
| 5 到 < 15  | 中等   | 大多数代码可接受 |
| 15 到 30   | 高       | 需要更多测试或简化 |
| > 30       | 危险   | 紧急重构并增加覆盖率 |

一个 100% 覆盖率的方法的 CRAP = 复杂度（最小值）。一个 0% 覆盖率的方法的 CRAP = 复杂度^2 + 复杂度。

## 使用场景

- 用户希望评估哪些方法由于低覆盖率和高复杂度而存在风险
- 用户要求特定方法、类或文件的 CRAP 分数
- 用户希望根据覆盖率和复杂度的风险，在命名方法、类或文件中确定下一步要测试的内容
- 用户希望评估测试质量，而不仅仅是简单的覆盖率百分比

## 不适用场景

- 用户只想运行测试（使用 `run-tests` 技能）
- 用户想编写新测试（使用 `code-testing-agent`）
- 用户只想获得覆盖率百分比而不进行复杂度分析
- 用户希望进行项目范围的覆盖率/CRAP 分析或优先级（使用 `coverage-analysis`）

## 输入

| 输入 | 必填 | 描述 |
|-------|----------|-------------|
| 目标范围 | 是 | 要分析的方法名、类名或文件路径 |
| 测试项目路径 | 否 | 测试项目的路径。默认为在解决方案中查找测试项目。 |
| 源项目路径 | 否 | 分析的源项目路径 |

## 工作流程

### 第 1 步：收集代码覆盖率数据

如果还没有覆盖率数据，请先对测试项目进行分类。对于 SDK 风格的项目，运行 `dotnet test` 并收集覆盖率。对于经典非 SDK 项目（`ToolsVersion`、显式编译项或 `packages.config`），仅使用仓库提供的覆盖率命令，该命令应输出 Cobertura。如果不存在，请请求 Cobertura XML 并停止；不要迁移项目或注入 SDK 风格的覆盖率包。CRAP 分数始终需要真实的覆盖率数据。

检查测试项目的 `.csproj` 文件以查找覆盖率包，然后运行相应的命令：

| 覆盖率包 | 命令 | 输出位置 |
|---|---|---|
| `coverlet.collector` | `dotnet test --collect:"XPlat Code Coverage" --results-directory ./TestResults` | 通常位于 `TestResults/<guid>/coverage.cobertura.xml`。在结果目录下递归搜索（例如，`TestResults/**/coverage.cobertura.xml`）或使用用户提供的任何显式覆盖率路径。 |
| `Microsoft.Testing.Extensions.CodeCoverage` (.NET 9) | `dotnet test -- --coverage --coverage-output-format cobertura --coverage-output ./TestResults` | `--coverage-output` 路径 |
| `Microsoft.Testing.Extensions.CodeCoverage` (.NET 10+) | `dotnet test --coverage --coverage-output-format cobertura --coverage-output ./TestResults` | `--coverage-output` 路径 |

#### 永远不要估算覆盖率

**估算的覆盖率会产生错误的 CRAP 分数，这比没有答案更糟糕。**
对于没有仓库覆盖率命令或现有报告的经典项目，请在此处停止并请求 Cobertura；不要使用任何收集回退。

对于 SDK 风格的项目，如果第一个命令未生成 Cobertura XML，请在放弃之前按此顺序尝试收集列表：

1. 仅对于 SDK 风格的项目，如果未引用提供程序，请添加提供程序：
   `dotnet add <test.csproj> package coverlet.collector`，然后重新运行。永远不要使用此回退来处理 `packages.config` 或经典非 SDK 项目。
2. 使用独立收集器，即使测试主机或共享程序集阻止进程内收集器时也能工作：
   `dotnet tool install --global dotnet-coverage` 然后
   `dotnet-coverage collect -f cobertura -o coverage.cobertura.xml "dotnet test <test.csproj>"`。

对于任何项目类型，如果已经存在真实的二进制 `.coverage` 报告，请使用 ReportGenerator 转换或总结现有数据：

3. 转换现有报告：
   `dotnet tool install --global dotnet-reportgenerator-globaltool` 然后
   `reportgenerator -reports:<file> -targetdir:cov -reporttypes:Cobertura`。
4. 测试失败但仍在运行？覆盖率是从执行的测试中收集的——继续使用该数据并注意失败情况。

如果所有路径都失败，**报告无法收集覆盖率，显示您尝试的命令及其错误，然后停止。** 如果有用，请单独报告复杂度，但永远不要发布基于假设的覆盖率百分比得出的 CRAP 数。

在使用报告之前，请验证它是否可以解析，是否至少包含一个类和方法，以及是否包含请求的目标。空报告或省略目标的报告是失败的收集或过滤，而不是 0% 覆盖率。在可能的情况下重新生成覆盖率；否则，不发布 CRAP 分数而停止。

如果用户提供了现有报告，请说明它没有被重新生成。除非通过在此分析中运行仓库的覆盖率命令来建立其来源，否则不要描述其数据为当前。

### 第 2 步：计算圈复杂度

优先使用来自仓库提供的代码指标报告的每个方法的机器生成的复杂度，或者当该报告映射到当前源时使用 Cobertura 方法的 `complexity` 属性。Microsoft.CodeAnalysis.Metrics 可以通过 `msbuild /t:Metrics` 生成方法级别的 `CyclomaticComplexity` 数据，但在未经用户批准的情况下不要添加该包或修改项目。

如果不存在机器生成的指标，请分析当前目标源，并将结果标记为手动复杂度计数。计算以下决策点（每个决策点都会将基础复杂度 1 增加到 1）：

| 结构 | 示例 |
|-----------|---------|
| `if` | `if (x > 0)` |
| `else if` | `else if (y < 0)` |
| `case`（每个） | `case 1:` |
| `for` | `for (int i = 0; ...)` |
| `foreach` | `foreach (var item in list)` |
| `while` | `while (running)` |
| `do...while` | `do { } while (cond)` |
| `catch`（每个） | `catch (Exception ex)` |
| `&&` | `if (a && b)` |
| `\|\|`（OR） | `if (a \|\| b)` |
| `??` | `value ?? fallback` |
| `?.` | `obj?.Method()` |
| `? :`（三元） | `x > 0 ? a : b` |
| 模式匹配臂 | `x is > 0 and < 10` |

每个方法的基准复杂度为 1。每个决策点增加 1。

在手动计数时，请阅读源文件，按结构逐个分解，并不要使用源注释作为证据。如果报告的复杂度属性与当前源计数不一致，请报告冲突，并且不要将任何结果 CRAP 分数作为权威发布。

### 第 3 步：从 Cobertura XML 中提取每个方法的覆盖率

解析 Cobertura XML 以查找目标 `<class>` 元素下每个方法的 `line-rate` 属性。如果 `line-rate` 在方法级别不可用，则从 `<lines>` 元素计算它：

$$\text{cov}(m) = \frac{\text{有命中行的数量} > 0}{\text{总行数}}$$

Cobertura 中的方法名可能与源不同（异步方法、lambda）。当名称不一致时，按行范围匹配。

当 `line-rate` 和 `<lines>` 都存在时，重新计算命中比率并进行比较。仅允许正常报告舍入（一个百分点）；如果它们差异更大，则报告自相矛盾。重新生成它或报告冲突并停止计算 CRAP。永远不要在沉默中选择产生预期分数的值。

### 第 4 步：计算 CRAP 分数

对于范围内的每个方法，应用公式：

$$\text{CRAP}(m) = \text{comp}(m)^2 \times (1 - \text{cov}(m))^3 + \text{comp}(m)$$

使用计算器或脚本进行算术运算并显示替换的复杂度和覆盖率。不要在脑海中计算公式。

### 第 5 步：展示结果

展示一个排序表（最高 CRAP 优先）：

```text
| 方法                          | 复杂度 | 覆盖率 | CRAP 分数 | 风险     |
|---------------------------------|------------|----------|------------|----------|
| OrderService.ProcessOrder       | 10         | 45%      | 26.6       | 高     |
| OrderService.ValidateItems      | 8          | 90%      | 8.1        | 中等   |
| OrderService.CalculateTotal     | 3          | 100%     | 3.0        | 低     |
```

包括：

- **摘要**：分析的总方法数，每个风险类别中的方法数量
- **主要违规者**：CRAP > 30 的方法，以及具体建议
- **快速收益**：复杂度高但微小覆盖率改进会显著降低分数的方法

### 第 6 步：提供可操作的推荐

对于高 CRAP 分数的方法，建议一个或两个：

1. **添加测试**——识别未覆盖的分支并建议具体的测试用例
2. **降低复杂度**——建议对深层嵌套逻辑进行提取方法重构

计算 **需要增加的覆盖率** 以将方法的 CRAP 分数降至 15 以下：

$$\text{cov}_{\text{needed}} = 1 - \left(\frac{15 - \text{comp}}{\text{comp}^2}\right)^{1/3}$$

此公式仅适用于 comp < 15。当 comp >= 15 时，100% 覆盖率的最小可能 CRAP 分数是 comp 本身，这已经达到或超过阈值。在这种情况下，**仅靠覆盖率无法将 CRAP 分数降至阈值以下**——必须首先重构方法以降低其圈复杂度。

报告此为： "要将 `ProcessOrder`（复杂度 10）的 CRAP 降至 15 以下，请将覆盖率从 45% 增加到超过 63.2%（报告为整数百分比时至少为 64%）。" 对于复杂度本身超过阈值的方
