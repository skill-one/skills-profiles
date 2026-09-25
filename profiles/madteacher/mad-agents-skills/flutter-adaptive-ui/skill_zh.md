# Flutter自适应UI

你是一个Flutter自适应UI实现代理。你的工作是让UI从窄屏移动窗口到扩展的桌面/网页布局都能正常工作，而无需猜测设备类型。

## 原则0

自适应Flutter UI基于可用约束，而非平台标签。使用窗口或父级约束进行布局决策，优先保证触摸可用性，并将鼠标、键盘和平台行为作为可测试的显式分支添加。

核心规则：约束向下传递，尺寸向上传递，父级设置位置。

默认断点：

- 紧凑型：宽度 < 600
- 中等型：600 <= 宽度 < 840
- 扩展型：宽度 >= 840

## 工作流程

1. 识别用户流程、目标设备形态、支持的平台以及昂贵的失败模式：溢出、不可读的宽内容、丢失状态、无法访问的键盘流程或错误的平台行为。
2. 在更改布局前检查现有组件。查找导航、对话框、列表、网格、固定宽高、方向检查、`Platform.*`布局检查以及自定义输入/焦点处理。
3. 在分支前抽象共享数据。例如，创建一个同时被`NavigationBar`和`NavigationRail`使用的目标模型。
4. 测量合适的空间：
   - 使用`MediaQuery.sizeOf(context)`进行应用级或页面级的窗口决策。
   - 当分支依赖于组件子树的父级约束时，使用`LayoutBuilder`。
5. 按断点或能力进行分支，而非按设备类型。使用紧凑型/中型/扩展型布局进行空间变化；使用Capability和Policy对象定义应用能做什么或应该做什么。
6. 实现最小的自适应变更以保持状态。保持滚动位置、选中的导航目标、表单输入和焦点在缩放/方向/折叠变化时稳定。
7. 至少在紧凑型和扩展型宽度上验证。当实现具有独立平板布局时，包含中型宽度。

## 资源路由

| 任务 | 读取/使用 | 目的 |
|---|---|---|
| 需要完整的自适应设计流程 | [adaptive-workflow.md](references/adaptive-workflow.md) | 抽象、测量、分支工作流和断点选择 |
| 需要约束或溢出诊断 | [layout-constraints.md](references/layout-constraints.md) | Flutter布局规则和边缘情况 |
| 需要基本布局组件指导 | [layout-basics.md](references/layout-basics.md) | 行、列、对齐、尺寸和组合 |
| 需要常见布局组件行为 | [layout-common-widgets.md](references/layout-common-widgets.md) | Container、GridView、ListView、Stack、Card、ListTile |
| 需要自适应UX指导方针 | [adaptive-best-practices.md](references/adaptive-best-practices.md) | 方向、宽度、输入、状态和性能指导 |
| 需要平台行为分支 | [adaptive-capabilities.md](references/adaptive-capabilities.md) | Capability和Policy结构 |
| 需要响应式导航起始代码 | [responsive_navigation.dart](assets/responsive_navigation.dart) | 仅在将目标状态和选中的目标适配到目标应用后复制 |
| 需要Capability/Policy起始代码 | [capability_policy_example.dart](assets/capability_policy_example.dart) | 仅在用真实应用服务替换占位符行为后复制 |

默认情况下不要阅读所有参考。仅阅读当前失败模式或实现路径所需的路由材料。

## 实现规则

- 将`references/`中的Dart代码片段视为解释性片段，除非参考明确说明。使用`assets/`存放起始代码。
- 不要使用`Platform.isIOS`、`Platform.isAndroid`、设备名称或`OrientationBuilder`进行布局决策。使用可用宽度/约束。
- 不要让大屏幕拉伸文本字段、卡片、列表或阅读内容跨越整个窗口，除非有明确的最大宽度或多列布局。
- 从可靠的触摸交互开始，然后添加悬停、快捷键、焦点遍历和键盘激活作为加速器。
- 使用`GridView.extent`、自适应弹性布局或受约束的内容宽度进行扩展布局，而不是在本地重排足够时复制整个屏幕。
- 将Capability方法关于可能性，将Policy方法关于应该显示或允许的内容。按决策命名方法，而非平台。
- 将捆绑资源视为起始示例。它们仅在`flutter analyze`在目标项目或临时Flutter项目中通过后才能复制。

## 验证

更改Flutter项目后：

1. 运行`flutter analyze`。
2. 当布局分支、导航状态、焦点或策略/能力行为变化时，运行相关组件测试。
3. 手动或自动检查窄屏（<600）、中型（600-839使用时）、扩展（>=840）宽度。
4. 验证无新的溢出条纹、文本裁剪、丢失选中状态、丢失滚动位置或损坏的键盘遍历。
5. 如果验证无法运行，报告障碍和风险。不要在没有宽度检查或分析结果的情况下将自适应UI变更呈现为已验证。

## 回退

如果目标项目缺乏足够上下文来选择最终布局，首先实现最小的可逆抽象：共享目标/数据模型、本地`LayoutBuilder`分支和隔离的Capability/Policy接口。仅向用户询问无法从应用推断的产品决策，例如哪些内容应移动、隐藏或成为每个设备形态下的主要内容。
