# Xcode 项目分析器

使用此技能来处理那些仅通过修改源代码难以解决的项目和目标级别的构建低效问题。

## 核心规则

- 默认以建议优先。
- 修改项目文件、方案或构建设置前，需要明确批准。
- 优先考虑与时间总结、构建日志或项目配置证据相关的可测量发现。
- 区分仅调试时的问题与仅发布时的问题。

## 需要审查的内容

- 方案构建顺序和目标依赖关系
- 与 [构建设置最佳实践](references/build-settings-best-practices.md) 相比，调试与发布构建设置的差异
- 运行脚本阶段和依赖分析设置
- 派生数据波动或明显无效的自定义步骤
- 并行化机会
- 显式的模块依赖设置和模块映射的可用性
- 构建时间总结中“规划 Swift 模块”的时间 -- 如果它主导增量构建，则怀疑意外的输入修改或与宏相关的无效化
- 资源目录的编译时间，特别是在具有大型或多个目录的目标中
- 构建时间总结中 `ExtractAppIntentsMetadata` 的时间 -- 如果此阶段消耗大量时间，则记录为 `xcode-behavior`（报告成本和影响，但除非有明确的 Apple 指导，否则不要建议仓库本地优化）
- 无变更构建开销 -- 如果无操作重建超过几秒钟，则调查固定成本阶段（脚本执行、codesign、验证、CopySwiftLibs）
- CocoaPods 使用情况 -- 如果存在 `Podfile` 或 `Pods.xcodeproj`，则 CocoaPods 已弃用；建议迁移到 SPM，并不要尝试 CocoaPods 特定的优化（参见 [项目审计检查.md](references/project-audit-checks.md)）
- 任务回溯（Xcode 16.4+：方案编辑器 > 构建 > 构建调试）以诊断任务为何在增量构建中意外重新运行

## 构建设置最佳实践审计

每个项目审计都应包括一个构建设置清单，比较项目的调试和发布配置与 [构建设置最佳实践](references/build-settings-best-practices.md) 中推荐值的差异。使用对勾/叉号指示器（`[x]`/`[ ]`）呈现结果。范围严格限于构建性能 -- 不要标记语言迁移设置，如 `SWIFT_STRICT_CONCURRENCY` 或 `SWIFT_UPCOMING_FEATURE_*`。

## Apple 推荐检查

在每次审计中审查以下项目：

- 目标依赖关系准确且不缺失或不膨胀
- 方案按依赖关系顺序构建
- 运行脚本声明输入和输出
- 当脚本具有许多输入或输出时使用 `.xcfilelist` 文件
- 在自定义框架或库应暴露模块映射的地方启用 `DEFINES_MODULE`
- 头文件足够自包含，可用于模块映射
- 对于应共享模块的目标，显式模块依赖设置应保持一致

## 典型改进点

- 跳过仅在发布时才有意义的调试时脚本
- 添加缺失的脚本保护或依赖分析元数据
- 移除方案中意外的串行瓶颈
- 对齐导致不必要模块变体的构建设置
- 修复强制进行比必要范围更广的重建的陈旧项目结构
- 识别修改文件时间戳而不更改内容、无声地使构建输入无效并强制模块重新规划的 linters 或 formatters
- 将大型资源目录拆分为跨目标的单独资源包以并行化编译
- 使用任务回溯来精确定位触发不必要增量工作的确切输入变更

## 报告格式

对于每个问题，包括：

- 证据
- 可能的影响范围
- 为什么它影响干净构建、增量构建或两者
- 预计影响
- 批准要求

如果证据指向包图或构建插件，则通过阅读其 `SKILL.md` 并将其工作流程应用于相同的项目上下文，将其移交给 [`spm-build-analysis`](../spm-build-analysis/SKILL.md)。

## 额外资源

- 有关详细的审计清单，请参阅 [references/project-audit-checks.md](references/project-audit-checks.md)
- 有关构建设置最佳实践，请参阅 [references/build-settings-best-practices.md](references/build-settings-best-practices.md)
- 有关共享建议结构，请参阅 [references/recommendation-format.md](references/recommendation-format.md)
- 有关 Apple 对齐的源摘要，请参阅 [references/build-optimization-sources.md](references/build-optimization-sources.md)
