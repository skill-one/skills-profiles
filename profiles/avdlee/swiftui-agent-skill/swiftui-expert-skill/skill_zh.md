# SwiftUI 专家技能

## 操作规范

- 将每种 `View` 类型视为一个失效边界：仅为其提供它所读取的数据，并将频繁变化的依赖项保持在受影响的最小子树附近
- 编写、审查或迁移 API 使用时，搜索 `references/latest-apis.md`；仅查找与任务相关的 API
- 用现代等效项替换已弃用的 API。在功能开发期间，标记软弃用的 API 并保留它们（参见 `references/soft-deprecation.md`）
- 优先使用 SwiftUI 原生 API 而不是 UIKit/AppKit 桥接，除非桥接是必要的
- 关注正确性和性能；不要强制执行特定的架构（MVVM、VIPER 等）
- 鼓励将业务逻辑与视图分离以提高可测试性，但不强制规定如何实现
- 遵循 Apple 的人机界面指南和 API 设计模式
- 仅在用户明确要求时采用 Liquid Glass（参见 `references/liquid-glass.md`）
- 将性能优化作为建议，而不是要求
- 使用 `#available` 门控并提供合理的回退方案，用于版本特定的 API
- 对于布局和渲染输入，读取 SwiftUI 视图消费它的最近值；不要用进程全局屏幕状态进行替换

## 任务工作流程

### 审查现有的 SwiftUI 代码
- 阅读要审查的代码并确定哪些主题适用
- 标记已弃用的 API（与 `references/latest-apis.md` 进行比较）；替换硬弃用的 API，并标记软弃用的 API 而不重写，除非用户要求迁移
- 对每个相关主题运行下方的主题路由器
- 验证 `#available` 门控和版本特定功能的回退路径
- 对于广泛的代码库审查，首先确定较小的关注区域并逐个呈现；如果用户请求全代码库审查，将其分为 TODO 列表

### 改进现有的 SwiftUI 代码
- 根据主题路由器主题审计当前实现
- 用 `references/latest-apis.md` 中的现代等效项替换硬弃用的 API；在功能开发期间标记软弃用的 API 并不重写
- 重构热点路径以减少不必要的状态更新
- 将复杂的视图体提取到单独的子视图中
- 当遇到 `UIImage(data:)` 时建议图像下采样（可选优化，参见 `references/image-optimization.md`）

### 实现新的 SwiftUI 功能
- 首先设计数据流：识别拥有的状态与注入的状态
- 为最佳差异化结构视图（早期提取子视图）
- 应用正确的动画模式（隐式与显式、过渡）
- 对所有可点击元素使用 `Button`；添加可访问性分组和标签
- 使用 `#available` 门控版本特定的 API 并提供回退方案

### 记录新的 Instruments 跟踪
当用户要求“记录跟踪”、“分析应用”、“捕获会话”等时触发。完整参考：`references/trace-recording.md`。

1. **确认目标** — 附加到正在运行的应用、启动应用或记录所有进程？如果用户没有说明，请询问。在有用时列出连接的设备：
   ```bash
   python3 "${SKILL_DIR}/scripts/record_trace.py" --list-devices
   ```
2. **根据目标类型选择模板** — SwiftUI 模板在任何**真实设备**上填充 SwiftUI 行：物理 iOS/iPadOS 设备**或主机 Mac**。唯一的例外是**iOS 模拟器**，其中 SwiftUI 行为空——在这种情况下切换到 `--template "Time Profiler"`（仍然提供 Time Profiler + Hangs + Animation Hitches）。始终检查 `--list-devices`：`simulators` 类型 → `Time Profiler`；`devices` 类型（真实设备和主机 Mac）→ 默认 `SwiftUI`。完整决策表在 `references/trace-recording.md`。
3. **开始记录**。对于用户说“我会告诉您何时完成”的代理驱动会话，在后台启动并使用停止文件：
   ```bash
   python3 "${SKILL_DIR}/scripts/record_trace.py" \
       --device "<name|udid>" --attach "<AppName>" \
       --stop-file /tmp/stop-trace --output ~/Desktop/session.trace
   ```
   对于交互式会话，只需告诉用户完成时按 Ctrl+C。
4. **发送停止信号** — 当用户说他们已完成应用操作时，`touch /tmp/stop-trace`。脚本干净地 SIGINT xctrace 并等待最多 60 秒完成。
5. **分析** 生成的跟踪（流程到下方的“跟踪驱动改进”工作流程）。

### 跟踪驱动改进（Instruments `.trace` 提供）
每当用户的请求引用 `.trace` 文件时触发。一个目标 SwiftUI 源文件是**可选**的——如果提供，引用特定行；如果没有，根据跟踪已经揭示的视图名称和符号建议要查看的位置。

完整参考：`references/trace-analysis.md`。组合模式的摘要：

1. **限定分析范围**。问自己：用户想要整个跟踪，还是一个切片？
   - "关注 X / 在 X 之后 / 在 X 和 Y 之间 / 在 X 期间" → **首先解析一个窗口**（见步骤 2）。
   - 没有范围提示 → 分析整个跟踪。
2. **解析窗口（如果用户已范围）**。解析器暴露两种发现模式：
   ```bash
   # 查找一个标记了感兴趣区域开始/结束的日志：
   python3 "${SKILL_DIR}/scripts/analyze_trace.py" --trace <path> \
       --list-logs --log-message-contains "loaded feed" --log-limit 5
   # 或者列出 os_signpost 间隔（成对的开始/结束），可按名称过滤：
   python3 "${SKILL_DIR}/scripts/analyze_trace.py" --trace <path> \
       --list-signposts --signpost-name-contains "ImageDecode"
   ```
   两种模式都接受 `--window START_MS:END_MS` 来范围发现。选择与用户描述匹配的 `time_ms`（用于日志）或 `start_ms`/`end_ms`（用于 signposts）。构建一个窗口，如 `--window 10400:11700`。
3. **运行主要分析**（带或不带 `--window`）：
   ```bash
   python3 "${SKILL_DIR}/scripts/analyze_trace.py" --trace <path> \
       --json-only --top 10 [--window START_MS:END_MS]
   ```
4. **使用 `references/trace-analysis.md` 进行解释** — 关键诊断：
   - 每个关联中的 `main_running_coverage_pct`（<25% = 阻塞；≥75% = CPU 约束）。
   - `swiftui-causes.top_sources` 揭示更新持续发生的原因——高边缘计数的源（如 `UserDefaultObserver.send()`）或宽 `EnvironmentWriter` 条目是结构失效错误。修复一个通常会使许多下游热点视图折叠。
5. **当特定视图显示为昂贵时，询问是谁使其失效**。使用 `--fanin-for "<view name>"` 获取驱动更新的源节点排名列表。
6. **可选地基于源**。如果用户指向了一个文件，请阅读它并匹配视图名称/用户代码符号与标识符。如果没有，根据 SwiftUI 报告的视图名称建议要打开的文件。
7. **返回一个优先级计划**。引用证据（覆盖率 %、热点符号、重叠视图、日志时间戳、原因图边缘）并将每个建议路由到主题路由器参考。
8. 仅在用户要求编辑时才编辑代码。

### 主题路由器

咨询与当前任务相关的每个主题的参考文件：

| 主题 | 参考 |
|------|------|
| 状态管理 | `references/state-management.md` |
| 环境和 `@Entry` | `references/environment-patterns.md` |
| 视图组合 | `references/view-structure.md` |
| 视图修饰符和身份 | `references/modifier-patterns.md` |
| 性能 | `references/performance-patterns.md` |
| 列表和 ForEach | `references/list-patterns.md` |
| 可调整布局、安全区域、排列和保留区域 | `references/layout-best-practices.md` |
| iPhone Duo 表单行为 | `references/iphone-duo.md` |
| 底部sheet和导航 | `references/sheet-navigation-patterns.md` |
| ScrollView、滚动位置和滚动几何 | `references/scroll-patterns.md` |
| 聚焦管理 | `references/focus-patterns.md` |
| 动画（基础） | `references/animation-basics.md` |
| 动画（过渡） | `references/animation-transitions.md` |
| 动画（高级） | `references/animation-advanced.md` |
| 可访问性 | `references/accessibility-patterns.md` |
| Swift Charts | `references/charts.md` |
| Charts 可访问性 | `references/charts-accessibility.md` |
| 图像优化和显示比例 | `references/image-optimization.md` |
| 工具栏 | `references/toolbar-patterns.md` |
| 基于文档的应用 | `references/document-apps.md` |
| WebKit | `references/webkit-integration.md` |
| 样式文本编辑 | `references/styled-text-editing.md` |
| Liquid Glass (iOS 26+) | `references/liquid-glass.md` |
| macOS 场景 | `references/macos-scenes.md` |
| macOS 窗口样式 | `references/macos-window-styling.md` |
| macOS 视图 | `references/macos-views.md` |
| 文本模式 | `references/text-patterns.md` |
| 本地化 | `references/localization.md` |
| 已弃用 API 查找 | `references/latest-apis.md` |
| 处理软弃用的 API | `references/soft-deprecation.md` |
| 预览 | `references/previews.md` |
| Instruments 跟踪分析 | `references/trace-analysis.md` |
| Instruments 跟踪记录 | `references/trace-recording.md` |

## 正确性检查清单

这些都是硬规则——违反规则总是错误：

- [ ] `@State` 属性是 `private`
- [ ] `@Binding` 仅在子视图修改父状态时使用
- [ ] 更改父拥有的输入不是存储为 `@State`/`@StateObject`；有意状态种子作为一次性文档
- [ ] `@StateObject` 用于视图拥有的对象；`@ObservedObject` 用于注入的
- [ ] iOS 17+：`@State` 与 `@Observable`；`@Bindable` 用于需要绑定的注入观察对象
- [ ] `ForEach` 使用稳定身份（从不 `.indices`/`\.offset`；id 生存期长于视图且不衍生自可变内容）
- [ ] 每个 `ForEach` 元素具有恒定数量的视图；`List` 行是一元
- [ ] 没有存储在自定义 `@Environment`/`@FocusedValue` 键中的闭包
- [ ] 自定义 `@Entry` 默认值是稳定的（没有 `Model()`/`Date()`/`UUID()` 表达式）
- [ ] SwiftUI 显示比例来自 `@Environment(\.displayScale)`，而不是全局屏幕状态
- [ ] 安全区域内容不会重复应用 `GeometryProxy.safeAreaInsets`
- [ ] `.animation(_:value:)` 始终包括 `value` 参数
- [ ] `@FocusState` 属性是 `private`
- [ ] 在 `.focusable()` 视图的点击手势处理程序中没有冗余的 `@FocusState` 写入
- [ ] 版本特定的 API 使用 `#available` 门控并具有合理的回退方案
- [ ] `import Charts` 存在于使用图表类型的文件中
- [ ] 预览使用自包含的模拟数据；不依赖实时服务或网络
