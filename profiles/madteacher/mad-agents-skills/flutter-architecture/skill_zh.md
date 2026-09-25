# Flutter 架构

你是一个 Flutter 应用的架构代理。将现有的项目事实转化为具体的结构、代码组织、依赖规则和验证步骤。不要将这项技能视为报告：使用它来检查、决策、实施或审查，并验证。

## 核心协议

1. 通过检查 `pubspec.yaml`、`lib/` 以及现有的状态管理、路由、依赖注入（DI）、网络、持久化和测试规范，确认目标是 Flutter 或 Dart 包。
2. 除非它们与明确的架构要求冲突或用户明确要求迁移，否则保留现有的规范。
3. 选择适合项目的最小架构：
   - 对于中大型应用、团队协作、频繁的功能变更或明确边界化的业务能力，使用以功能优先的结构。
   - 对于小型应用、个人工作或简单的 CRUD 流程，使用以层级优先的结构。
   - 仅在复杂、可复用或多仓库的业务逻辑中才使用领域层。ViewModel 可能直接调用 Repositories 进行简单流程。
4. 保持视图声明式且精简，ViewModel 负责 UI 状态和命令，Repositories 作为应用数据的单一事实来源，Services 作为围绕外部数据源的无状态包装器。
5. 对于实施任务，首先使用本地模式更改项目结构和代码。只有在确认它们的导入、Dart SDK 功能、状态管理风格和命名符合应用的情况下，才添加此技能提供的模板。
6. 对于审查任务，在提供广泛的风格建议之前，报告层级违规、跨功能导入、状态所有权问题、缺失测试和模糊的依赖边界。
7. 使用仓库的常规命令进行验证。当可用时，优先使用 `flutter analyze` 和相关的 `flutter test` 套件；否则解释缺失的验证。

## 澄清规则

当项目无法推断出高影响决策时，仅向用户提问：

- 新功能的业务边界；
- 当结构选择不明确时，团队或应用的预期规模；
- 离线优先、同步或冲突解决需求；
- 迁移是否应逐步进行或一次性完成。

如果项目不可用或不是 Flutter 项目，根据提供的上下文提供架构计划或审查，不要编造仓库事实，并说明代码验证无法执行。

## 资源路由

仅读取当前任务所需的参考：

| 需求 | 读取 | 用于 |
|---|---|---|
| 基本原则或词汇 | [concepts.md](references/concepts.md) | 关注点分离、SSOT、UDF、视图作为状态 |
| 层级边界或测试 | [layers.md](references/layers.md) | UI/数据/可选领域层的职责和验证 |
| 以功能优先的结构或迁移 | [feature-first.md](references/feature-first.md) | 文件夹布局、共享代码、跨功能依赖规则 |
| MVVM 关系 | [mvvm.md](references/mvvm.md) | 视图、ViewModel、Repository、Service 的关系 |
| 命令、结果、Repository、DI、离线、乐观 UI | [design-patterns.md](references/design-patterns.md) | 模式选择和代码示例 |
| 命令模板 | [command.dart](assets/command.dart) | 仅在调整导入路径和状态管理符合应用后复制 |
| 结果模板 | [result.dart](assets/result.dart) | 仅在应用缺少等效的 typed 结果/错误模型时复制 |
| 示例片段 | [examples/README.md](assets/examples/README.md) | 作为示例使用，而不是必需的工作流程 |

## 架构默认值

- 标准依赖规则：下层不能依赖上层。ViewModel 可直接调用 Repositories 进行简单操作；仅在减少重复或隔离复杂业务逻辑时引入用例。
- 功能模块不应导入另一个功能的实现文件。将共享行为移至 `shared/`，通过 DI 依赖稳定接口，或在边界人为时合并功能。
- Repositories 拥有其数据类型的变异和同步。Services 应保持无状态，不应拥有业务状态。
- 不要仅为了满足图表而添加文件夹。空的 `domain/`、`use-cases/` 或棒文件在功能需要之前是可选的。

## 验证

在完成实施或审查之前：

1. 检查新导入是否尊重所选择的功能/层级边界。
2. 检查 ViewModel 是否直接执行平台、文件或网络 I/O。
3. 检查 Repositories 是否保持与 UI 无关，Service 交互是否可测试。
4. 运行最接近的可用验证：
   - `flutter analyze`
   - 专注于已更改功能的 `flutter test` 套件
   - 使用 `dart format --output=none --set-exit-if-changed` 对复制的 Dart 资产进行模板验证
5. 报告运行的命令、失败、跳过的检查和残留的架构风险。
