# macOS 开发专家

面向 macOS 应用开发的全面指导。此技能聚合了针对 macOS 开发不同方面的专业模块。

## 此技能何时激活

当用户：
- 询问 macOS 开发最佳实践
- 需要对 macOS/Swift 项目进行代码审查
- 需要 SwiftUI、SwiftData 或 AppKit 的帮助
- 正在实现 macOS 26（Tahoe）功能
- 需要 HIG 对 UI/UX 进行审查
- 需要 macOS 应用的架构指导

## 可用模块

根据用户需求，读取相关的模块文件：

### coding-best-practices/
Swift 6+ 代码质量和现代编程范式。
- `swift-language.md` - 现代 Swift 模式
- `modern-concurrency.md` - async/await、actors、Sendable
- `data-persistence.md` - SwiftData、UserDefaults、Keychain
- `code-organization.md` - 项目结构和模块化
- `architecture-principles.md` - 清洁架构模式

### architecture-patterns/
软件设计和架构。
- `solid-detailed.md` - 基于 Swift 示例的 SOLID 原则
- `design-patterns.md` - 常见设计模式
- `modular-design.md` - 模块化架构方法

### swiftdata-architecture/
SwiftData 深入探讨。
- `schema-design.md` - 模型设计和关系
- `query-patterns.md` - 高效查询和谓词
- `performance.md` - 优化技术

### macos-tahoe-apis/
macOS 26 特定功能。
- `tahoe-features.md` - 新的 macOS 26 功能
- `apple-intelligence.md` - AI/ML 集成
- `mlx-framework.md` - 基于 MLX 的设备端 ML
- `continuity.md` - 跨设备功能
- `xcode16.md` - Xcode 16 工具和功能

### macos-capabilities/
平台集成。
- `sandboxing.md` - 应用沙盒和权限
- 系统集成功能

### appkit-swiftui-bridge/
混合开发。
- `nsviewrepresentable.md` - 包装 AppKit 视图
- 框架之间的状态管理

### ui-review-tahoe/
macOS 26 的 UI/UX 审查。
- 液态玻璃设计系统
- HIG 合规性检查
- 可访问性审查

### app-planner/
项目规划和分析。
- 新应用架构规划
- 现有应用审计

## 如何使用

1. 从用户问题中识别其需求
2. 从子目录中读取相关的模块文件
3. 将指导应用于其特定上下文
4. 需要时参考 Apple 文档

## 示例工作流程

**用户询问 SwiftData 性能：**
1. 读取 `swiftdata-architecture/performance.md`
2. 如有必要，读取 `swiftdata-architecture/query-patterns.md`
3. 将建议应用于其代码
