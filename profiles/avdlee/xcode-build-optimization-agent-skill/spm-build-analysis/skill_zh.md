# SPM 构建分析

当包结构、插件或依赖配置可能导致 Xcode 构建缓慢时，使用此技能。

## 核心规则

- 将包分析视为证据收集，而非替换依赖项的指令。
- 将包图问题与项目设置问题分开。
- 未经明确批准，不要重写包清单或依赖源。

## 需要检查的内容

- `Package.swift` 和 `Package.resolved`
- 本地包与远程包
- 包插件和构建工具的使用
- 二进制目标占用空间
- 依赖层叠、重复导入和潜在循环
- 显示包相关工作的构建日志或时间摘要

## 推荐前验证

在将任何本地包包含在推荐中之前，请验证它是否确实是项目依赖图的一部分。`Vendor/` 目录可能包含未链接到任何目标的包。

- 检查 `project.pbxproj` 中引用包路径的 `XCLocalSwiftPackageReference` 条目。
- 检查 `XCSwiftPackageProductDependency` 条目，以确认包的产品已链接到至少一个目标。
- 如果本地包存在于磁盘上但未在项目中引用，则不要将其包含在构建时推荐中。

当推荐分支跟踪依赖项的版本固定时：

- 使用辅助脚本一次性扫描所有分支固定的依赖项：
  ```bash
  python3 scripts/check_spm_pins.py --project App.xcodeproj
  ```
  这会检查每个分支固定包的 `git ls-remote --tags`，并报告哪些包有可用于固定的标签。
- 如果没有标签，建议固定到特定的提交修订哈希值以确保确定性。
- 注意哪些包是分支固定的，因为上游根本没有标签，而不是有标签但有意跟踪分支的包。

## 关注领域

- 包图形状以及更改触发下游工作的工作量
- 本地开发和 CI 期间的插件开销
- 清理环境中出现的检出或获取成本信号
- 强制重复模块构建的配置漂移
- 共享依赖项时使用不同宏或选项的包目标的潜在风险
- 依赖方向违规（功能相互依赖而不是依赖共享的较低层）
- 模块之间的循环依赖（将共享契约提取到协议模块中）
- 超大模块（200+ 文件）扩大增量重建范围
- 使用 `@_exported import` 的伞形模块创建隐藏依赖链
- 阻止构建并行性的接口/实现分离缺失
- 测试目标依赖于应用程序目标而不是正在测试的模块
- Swift 宏重建级联：大量使用 Swift 宏（例如，TCA、基于 swift-syntax 的库）可能导致微不足道的源代码更改级联到近乎完整的重建，因为宏扩展使下游模块失效
- 当没有预构建二进制文件可用时 `swift-syntax` 对所有架构进行构建，增加显著的清理构建开销
- 多平台构建倍增：添加次要平台目标（例如，watchOS）可能导致共享 SPM 包多次构建（例如，iOS arm64、iOS x86_64、watchOS arm64），倍增 `SwiftCompile`、`SwiftEmitModule` 和 `ScanDependencies` 任务

## 模块化 SDK 迁移注意事项

将依赖项从单体目标迁移到模块化多目标 SDK（例如，用单独的 Core、RUM、Logs、Trace 模块替换一个伞形库）不会自动减少构建时间。模块化目标会增加 `SwiftCompile`、`SwiftEmitModule` 和 `ScanDependencies` 任务的次数，因为每个目标必须独立编译、扫描和发出其模块。构建时间的权衡取决于项目的并行性余量以及实际需要多少模块化目标。

考虑模块化 SDK 迁移时：

- 比较 `SwiftCompile` 任务总数在迁移前后的变化。
- 在推荐迁移以加快构建速度之前，对两种配置进行基准测试。
- 如果动机是减少 API 表面（只导入你使用的部分），请注意构建时间可能保持不变或增加，同时导入卫生得到改善。
- 只有当项目当前编译它不需要的很大一部分单体 SDK，并且模块化替代方案可以完全跳过这些未使用的部分时，才推荐模块化 SDK 迁移以加快构建速度。

## 显式模块依赖角度

当同一模块在时间输出中多次出现时，调查是否不同的包或目标选项强制生成了额外的模块变体。统一选项通常比削减少量源代码更重要。

## 报告格式

对于每个发现，请包含：

- 证据
- 受影响的包或插件
- 可能的清理构建与增量构建影响
- 如果相关，CI 影响
- 估计影响
- 批准要求

如果主要问题与包无关，请通过阅读目标技能的 SKILL.md 并将其工作流程应用于相同的项目上下文，将问题转交给 [`xcode-project-analyzer`](../xcode-project-analyzer/SKILL.md) 或 [`xcode-compilation-analyzer`](../xcode-compilation-analyzer/SKILL.md)。

## 其他资源

- 有关详细的审计清单，请参阅 [references/spm-analysis-checks.md](references/spm-analysis-checks.md)
- 有关共享推荐结构，请参阅 [references/recommendation-format.md](references/recommendation-format.md)
- 有关源引用，请参阅 [references/build-optimization-sources.md](references/build-optimization-sources.md)
