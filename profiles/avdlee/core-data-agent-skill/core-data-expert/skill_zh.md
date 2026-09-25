# 核心数据专家

为构建**正确**、**高性能**的核心数据堆栈和修复常见崩溃提供快速、面向生产环境的指导。

## 代理行为契约（请遵循这些规则）

1. 当建议取决于可用性时（例如 iOS 14+/17+ 功能等），确定操作系统/部署目标。
2. 在提出修复建议之前，识别上下文类型：**视图上下文（UI）**与**后台上下文（重负载）**。
3. 推荐使用 `NSManagedObjectID` 进行跨上下文/跨任务通信；**切勿跨上下文传递 `NSManagedObject` 实例**。
4. 在可能的情况下，优先选择轻量级迁移；对于复杂变更，使用分阶段迁移（iOS 17+）。
5. 当建议批量操作时，验证持久历史记录跟踪是否启用（通常需要 UI 更新）。
6. 对于 CloudKit 集成，提醒开发者**生产模式架构是不可变的**。
7. 尽量少参考 WWDC/外部资源；优先使用此技能的 `references/` 目录。

## 初步 60 秒（分诊模板）

- **明确目标**：设置、错误修复、迁移、性能、CloudKit？
- **收集最少信息**：
  - 平台 + 部署目标
  - 存储类型（SQLite / 内存）以及 CloudKit 是否启用
  - 涉及的上下文（视图 vs 后台）以及是否使用 Swift Concurrency
  - 精确的错误信息 + 堆栈跟踪/日志
- **立即分支**：
  - 线程/崩溃 → 专注于上下文限制 + `NSManagedObjectID` 传递
  - 迁移错误 → 确定模型版本 + 迁移策略
  - 批量操作未更新 UI → 持久历史记录跟踪 + 合并管道

## 路由图（快速选择正确的参考）

- **堆栈设置 / 合并策略 / 上下文** → `references/stack-setup.md`
- **保存模式** → `references/saving.md`
- **获取请求 / 列表更新 / 聚合** → `references/fetch-requests.md`
- **传统线程（perform/performAndWait, 对象 ID）** → `references/threading.md`
- **Swift Concurrency（async/await, 演员模型, Sendable, DAOs）** → `references/concurrency.md`
- **批量插入/删除/更新** → `references/batch-operations.md`
- **持久历史记录跟踪 + “批量操作未更新 UI”** → `references/persistent-history.md`
- **模型配置（约束、验证、派生/复合、可转换）** → `references/model-configuration.md`
- **架构迁移（轻量级/分阶段/延迟）** → `references/migration.md`
- **CloudKit 集成 & 调试** → `references/cloudkit-integration.md`
- **性能分析 & 内存** → `references/performance.md`
- **测试模式** → `references/testing.md`
- **术语** → `references/glossary.md`

## 常见错误 → 下一步最佳操作

- **“未能为 NSEntityDescription 找到唯一匹配”** → `references/testing.md`（共享 `NSManagedObjectModel`）
- **`NSPersistentStoreIncompatibleVersionHashError`** → `references/migration.md`（版本控制 + 迁移）
- **跨上下文/线程异常**（例如从错误上下文删除/更新）→ `references/threading.md`和/或`references/concurrency.md`（使用 `NSManagedObjectID`）
- **围绕核心数据的 Sendable / 演员隔离警告** → `references/concurrency.md`（不要用 `@unchecked Sendable` “掩盖”）
- **`NSMergeConflict` / 约束违规** → `references/model-configuration.md` + `references/stack-setup.md`（约束 + 合并策略）
- **批量操作未更新 UI** → `references/persistent-history.md` + `references/batch-operations.md`
- **CloudKit 架构/同步问题** → `references/cloudkit-integration.md`
- **获取期间内存增长** → `references/performance.md` + `references/fetch-requests.md`

## 验证清单（更改核心数据代码时）

- 确认上下文与工作匹配（视图 vs 后台）。
- 确保 `NSManagedObject` 实例不会跨上下文传递；改用 `NSManagedObjectID`。
- 如果使用批量操作，确认持久历史记录跟踪 + 合并管道。
- 如果使用约束，确认合并策略和冲突解决策略。
- 如果与性能相关，使用 Instruments 进行分析并验证获取批处理/限制。

## 参考文件

- `references/_index.md`（导航）
- `references/stack-setup.md`
- `references/saving.md`
- `references/fetch-requests.md`
- `references/threading.md`
- `references/concurrency.md`
- `references/batch-operations.md`
- `references/persistent-history.md`
- `references/model-configuration.md`
- `references/migration.md`
- `references/cloudkit-integration.md`
- `references/performance.md`
- `references/testing.md`
- `references/glossary.md`
