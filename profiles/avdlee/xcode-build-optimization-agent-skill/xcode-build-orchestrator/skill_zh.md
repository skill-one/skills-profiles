# Xcode 构建协调器

将此技能用作端到端 Xcode 构建优化工作的推荐首选入口。

## 不可协商的规则

- 墙上时间构建（开发者等待的时间）是主要的成功指标。每个推荐都必须说明其对开发者实际等待时间的预期影响。
- 以推荐模式启动。
- 在进行更改之前进行基准测试。
- 未经开发者明确批准，不得修改项目文件、源文件、包或脚本。
- 保留每个推荐的证据链。
- 批准更改后重新进行基准测试，并报告墙上时间差值。

## 两阶段工作流程

协调设计为两个由开发者评审分隔的独立阶段。

### 第一阶段 -- 分析（仅推荐）

以代理模式运行此阶段，因为代理需要执行构建、运行基准测试脚本、写入基准测试工件并生成优化报告。但是，将第一阶段视为**仅推荐**：不要修改任何项目文件、源文件、包或构建设置。在此阶段中，代理创建的唯一文件是基准测试工件和 `.build-benchmark/` 内的优化计划。

1. 收集构建目标上下文：工作区或项目、方案、配置、目标以及当前的痛点。当同时存在 `.xcworkspace` 和 `.xcodeproj` 时，优先选择 `.xcodeproj`，除非工作区包含构建所需的子项目。如果工作区引用外部项目，则如果这些项目未检出，可能会失败。
2. 运行 `xcode-build-benchmark` 以建立基线，如果没有新鲜的基准测试。基准测试脚本自动检测 `COMPILATION_CACHE_ENABLE_CACHING = YES` 并包括缓存清理构建，这些构建测量了现实的开发者体验（热缓存）。如果构建失败编译，请检查 `git log` 以查找最近的可构建提交。在 worktree 中工作时，从功能分支中挑选目标构建修复以达到可构建状态是可接受的。如果 SPM 包在其 `exclude:` 路径中引用 git 忽略的目录（例如 `__Snapshots__`），则在构建之前创建这些目录——worktree 不包含 git 忽略的内容，否则 `xcodebuild -resolvePackageDependencies` 将崩溃。
3. 验证基准测试工件具有非空的 `timing_summary_categories`。如果为空，则时间总结解析器可能已失败——重新解析原始日志或手动检查它们。如果 `COMPILATION_CACHE_ENABLE_CACHING` 已启用，请验证工件是否包含 `cached_clean` 运行。
   - **基准测试置信度检查**：对于每种构建类型（清理、缓存清理、增量），比较最小值和最大值。如果差值（最大值 - 最小值）超过中位数的 20%，请将基准测试标记为具有高方差，并建议在得出结论之前运行额外的重复（5 次以上）。高方差使得难以区分真实的改进和噪声。应用更改后，只有在更改后的中位数落在基线的最小值-最大值范围之外时，才声称有改进。
4. 如果增量构建是主要的痛点，并且 Xcode 16.4+ 可用，请建议开发者启用 **任务回溯**（方案编辑器 > 构建选项卡 > 构建调试 > “任务回溯”）。这揭示了每个任务重新运行的原因，这对于诊断意外的重新规划或输入失效至关重要。在分析中包含任何任务回溯证据。
5. 确定编译任务是否可能阻塞墙上时间进度或仅消耗并行 CPU 时间。将所有时间总结类别的秒数总和与墙上时间中位数进行比较：如果总和是中位数的 2 倍以上，则大部分工作是并行化的，编译热点修复不太可能减少等待时间。如果 `SwiftCompile`、`CompileC`、`SwiftEmitModule` 或 `Planning Swift 模块` 在时间总结中占主导地位**并且**可能位于关键路径上，请运行 `diagnose_compilation.py` 以捕获类型检查热点。如果它们是并行化的，仍然运行诊断，但将发现标记为“并行效率改进”而不是“构建时间改进”。
6. 运行适合证据的专家分析，通过阅读每个技能的 SKILL.md 并应用其工作流程：
   - [`xcode-compilation-analyzer`](../xcode-compilation-analyzer/SKILL.md)
   - [`xcode-project-analyzer`](../xcode-project-analyzer/SKILL.md)
   - [`spm-build-analysis`](../spm-build-analysis/SKILL.md)
7. 将发现结果合并到一个优先级排序的改进计划中。
8. 使用 `generate_optimization_report.py` 生成 Markdown 优化报告，并将其保存到 `.build-benchmark/optimization-plan.md`。此报告包括构建设置审核、时间分析、优先级排序的建议和批准清单。
9. 停止并向开发者展示计划以供评审。

开发者评审 `.build-benchmark/optimization-plan.md`，检查他们希望实施的建议的批准框，然后触发第二阶段。

### 第二阶段 -- 执行和验证（代理模式）

在开发者评审并批准了计划中的建议后，以代理模式运行此阶段。将所有实施工作委托给 [`xcode-build-fixer`](../xcode-build-fixer/SKILL.md)，通过阅读其 SKILL.md 并应用其工作流程。

10. 读取 `.build-benchmark/optimization-plan.md` 并从批准清单中识别批准的项目。
11. 将其交给 `xcode-build-fixer` 并附带批准的计划。修复器应用每个批准的更改，验证编译并重新进行基准测试。
12. 将验证结果附加到优化计划：更改后的中位数、绝对值和百分比差值以及置信度说明。
13. 报告前后结果以及任何剩余的后续机会。

## 优先级规则

目标是减少开发者等待构建完成的时间。

1. 确定开发者的主要痛点（清理构建、增量构建或两者）以及测量的墙上时间中位数。
2. 确定可能**阻塞**墙上时间进度的事物：
   - 如果所有时间总结类别的秒数总和是中位数的 2 倍以上，则大部分工作是并行化的。编译热点修复不太可能减少等待时间。
   - 如果单个串行类别（例如 `PhaseScriptExecution`、`CompileAssetCatalog`、`CodeSign`）占墙上时间的大比例，那就是真正的瓶颈。
   - 如果 `Planning Swift 模块` 或 `SwiftEmitModule` 在增量构建中占主导地位，则原因是无效化或模块大小，而不是单个文件编译速度。
3. 根据可能的墙上时间节省对建议进行排序，而不是累积任务减少。
4. 除非证据表明它们位于关键路径上，否则源级编译修复不应优先于项目/图/配置修复。

优先考虑可测量、可逆、低风险的更改。

## 建议影响语言

向开发者提出的每个建议都必须包含以下影响声明之一：

- “预计将您的[清理/增量]构建减少约 X 秒。”
- “减少了并行编译工作，但不太可能减少您的构建等待时间，因为其他任务同样耗时。”
- “对等待时间的影响不确定——应用后重新进行基准测试以确认。”
- “预计不会提高等待时间。好处是[确定性构建/更快的分支切换/减少 CI 成本]。”
- 对于 `COMPILATION_CACHE_ENABLE_CACHING` 特别： “在测试项目中测量到清理构建速度加快 5-14%。在真实工作流程中，缓存在构建之间持续存在——分支切换、拉取更改和具有持久 DerivedData 的 CI——收益会累积。”

永远不要引用累积任务时间节省作为头条影响。如果更改减少了 5 秒的并行编译工作，但另一个同样长的任务仍在运行，开发者的等待时间不会改变。

## 批准门

在实施任何东西之前，展示一个简短的批准列表，其中包括：

- 建议名称
- 预计等待时间影响（使用上述影响语言）
- 证据摘要
- 受影响的文件或设置
- 变更的风险是低、中还是高

等待开发者的明确批准。

## 批准后的执行

批准后，委托给 `xcode-build-fixer`：

- 修复器仅实施批准的项目
- 变更原子性地应用并保持作用域
- 任何与原始建议计划偏差都应记录
- 修复器使用相同的基准测试合同重新进行基准测试

## 最终报告

以纯语言开头墙上时间结果，例如：“您的清理构建现在需要 82 秒（之前是 86 秒）——快了 4 秒。” 然后包括：

- 基线清理和增量墙上时间中位数
- 更改后的清理和增量墙上时间中位数
- 绝对和百分比墙上时间差值
- 发生了什么更改
- 故意保留未更改的内容
- 如果噪声导致无法得出强结论，则包含置信度说明——如果基准测试方差很高（最小值到最大值的差值超过中位数的 20%），请明确说明，而不是将嘈杂数字作为确定性改进或回归呈现
- 如果累积任务指标改善了但墙上时间没有，请明确说明：“编译工作负载减少，但构建等待时间没有改善。当 Xcode 将这些任务与其他同样长的工 作并行运行时，这是预期的。”
- 一个可以粘贴到社区结果行的链接，以及一个打开 PR 的链接（见报告模板）

## 推荐的命令路径

### 基准测试

```bash
python3 scripts/benchmark_builds.py \
  --project App.xcodeproj \
  --scheme MyApp \
  --configuration Debug \
  --destination "platform=iOS Simulator,name=iPhone 16" \
  --output-dir .build-benchmark
```

对于 macOS 应用程序使用 `--destination "platform=macOS"`。对于 watchOS 使用 `--destination "platform=watchOS Simulator,name=Apple Watch Series 10"`。对于 tvOS 使用 `--destination "platform=tvOS Simulator,name=Apple TV"`。省略 `--destination` 以使用方案的默认值。

要测量真实的增量构建（文件触摸重建）而不是零更改构建，添加 `--touch-file path/to/SomeFile.swift`。

### 编译诊断

```bash
python3 scripts/diagnose_compilation.py \
  --project App.xcodeproj \
  --scheme MyApp \
  --configuration Debug \
  --destination "platform=iOS Simulator,name=iPhone 16" \
  --threshold 100 \
  --output-dir .build-benchmark
```

### 优化报告

```bash
python3 scripts/generate_optimization_report.py \
  --benchmark .build-benchmark/<artifact>.json \
  --project-path App.xcodeproj \
  --diagnostics .build-benchmark/<diagnostics>.json \
  --output .build-benchmark/optimization-plan.md
```

## 额外资源

- 对于报告模板，请参阅 [references/orchestration-report-template.md](references/orchestration-report-template.md)
- 对于基准测试工件要求，请参阅 [references/benchmark-artifacts.md](references/benchmark-artifacts.md)
- 对于建议格式，请参阅 [references/recommendation-format.md](references/recommendation-format.md)
- 对于构建设置最佳实践，请参阅 [references/build-settings-best-practices.md](references/build-settings-best-practices.md)
