# Xcode 构建基准测试

使用此技能在任何人尝试优化构建时间之前，生成可重复的 Xcode 构建基线。

## 核心规则

- 在推荐更改之前进行测量。
- 分别捕获干净和增量构建。
- 在多次运行中保持命令、目标、配置、方案和预热规则的一致性。
- 将带时间戳的 JSON 工具写入 `.build-benchmark/`。
- 不要将项目文件作为基准测试的一部分进行更改。

## 需要收集的输入

确认或推断：

- 工作区或项目路径
- 方案
- 配置
- 目标
- 用户是否需要模拟器或设备编号
- 是否需要自定义 `DerivedData` 路径

如果项目同时具有干净构建和增量构建的痛点，则对两者进行基准测试。这是默认行为。

## 工作树注意事项

在 git 工作树中基准测试时，SPM 包含 `exclude:` 路径引用 git 忽略的目录（例如，`__Snapshots__`）会导致 `xcodebuild -resolvePackageDependencies` 失败。在运行任何构建之前创建这些缺失的目录。

## 默认工作流程

1. 规范化构建命令并记录所有影响缓存或模块重用的标志。
2. 如有必要，运行一次预热构建以验证命令是否成功。
3. 运行 3 次干净构建。
4. 如果检测到 `COMPILATION_CACHE_ENABLE_CACHING = YES`，则运行 3 次缓存干净构建。这些测量带有预热编译缓存的干净构建时间——分支切换、拉取更改或 Clean Build Folder 的现实场景。脚本通过构建一次以预热缓存，然后在每次测量运行之前删除 DerivedData（但不删除编译缓存）来自动处理此操作。传递 `--no-cached-clean` 以跳过。
5. 运行 3 次零更改构建（在成功构建后立即立即构建且未进行编辑）。这测量固定的开销底线：依赖计算、项目描述传输、构建描述创建、脚本阶段、代码签名和验证。如果零更改构建花费超过几秒钟，则表示存在可避免的每次构建开销。使用默认的 `benchmark_builds.py` 调用（不带 `--touch-file` 标志）。
6. 可选地运行 3 次增量构建，并使用文件触摸来测量真实的编辑-重建循环。使用 `--touch-file path/to/SomeFile.swift` 在每次构建之前触摸一个代表性的源文件。
7. 将原始结果和摘要保存到 `.build-benchmark/`。
8. 报告中位数和分布，而不仅仅是单次最快的运行。

## 推荐的命令路径

尽可能使用共享辅助脚本：

```bash
python3 scripts/benchmark_builds.py \
  --workspace App.xcworkspace \
  --scheme MyApp \
  --configuration Debug \
  --destination "platform=iOS Simulator,name=iPhone 16" \
  --output-dir .build-benchmark
```

如果您无法使用辅助脚本，请运行等效的 `xcodebuild` 命令并保留原始输出。

## 必须的输出

返回：

- 干净构建的中位数、最小值、最大值
- 缓存干净构建的中位数、最小值、最大值（当 `COMPILATION_CACHE_ENABLE_CACHING` 启用时）
- 零更改构建的中位数、最小值、最大值（固定的开销底线）
- 增量构建的中位数、最小值、最大值（如果使用了 `--touch-file`）
- 最大的时间总结类别
- 可能影响比较的环境详细信息
- 保存工具的路径

如果结果嘈杂，请说明并建议在更稳定的情况下重新运行。

## 停止时机

如果用户仅要求基准测试，则在测量后停止。如果他们需要优化指导，请通过读取其 SKILL.md 并将其工作流程应用于相同的项目上下文，将工具传递给相关专家：

- [`xcode-compilation-analyzer`](../xcode-compilation-analyzer/SKILL.md)
- [`xcode-project-analyzer`](../xcode-project-analyzer/SKILL.md)
- [`spm-build-analysis`](../spm-build-analysis/SKILL.md)
- [`xcode-build-orchestrator`](../xcode-build-orchestrator/SKILL.md) 用于完整编排

## 额外资源

- 关于基准测试合同，请参阅 [references/benchmarking-workflow.md](references/benchmarking-workflow.md)
- 关于共享工具格式，请参阅 [references/benchmark-artifacts.md](references/benchmark-artifacts.md)
- 关于 JSON 架构，请参阅 [schemas/build-benchmark.schema.json](schemas/build-benchmark.schema.json)
