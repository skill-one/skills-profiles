---
name: ios-accessibility
description: 构建和审核 SwiftUI、UIKit 和 AppKit 的可访问性，以支持 VoiceOver、Voice Control、Switch Control、全键盘访问、动态类型、焦点恢复、标签/特征/操作、导航、自定义旋钮、NSAccessibility、XCTest 检查、自适应系统偏好设置以及 App Store 可访问性声明。在实现可访问性 UI、修复可访问性审核、测试辅助技术行为或证明 App Store 可访问性营养标签时使用。
---

# iOS/macOS 可访问性 - SwiftUI、UIKit 和 AppKit

构建 SwiftUI、UIKit 和 AppKit 界面，使其在 VoiceOver、开关控制、语音控制、全键盘访问和自适应可访问性设置下保持可操作。

## 目录

- [核心原则](#核心原则)
- [VoiceOver 如何读取元素](#如何voiceover读取元素)
- [SwiftUI 可访问性修饰符](#swiftui可访问性修饰符)
- [焦点管理](#焦点管理)
- [动态类型](#动态类型)
- [自定义旋钮](#自定义旋钮)
- [系统可访问性偏好设置](#系统可访问性偏好设置)
- [装饰性内容](#装饰性内容)
- [语音控制](#语音控制)
- [开关控制](#开关控制)
- [全键盘访问](#全键盘访问)
- [辅助访问（iOS 18+）](#辅助访问ios-18)
- [UIKit 可访问性模式](#uikit可访问性模式)
- [AppKit 可访问性模式](#appkit可访问性模式)
- [可访问性自定义内容](#可访问性自定义内容)
- [App Store 可访问性营养标签](#app-store可访问性营养标签)
- [测试可访问性](#测试可访问性)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考文献](#参考文献)

---

## 核心原则

1. 优先使用语义系统控件；自定义控件必须暴露相同名称、角色、值、状态和操作。
2. 在辅助输入中保留所有任务：不要让手势、颜色、运动、悬停状态或视觉布局成为获取意义或操作的唯一途径。
3. 在导航、呈现、更新和关闭过程中保持焦点和遍历的意图性。
4. 让文本、布局、对比度、透明度和运动适应用户的可访问性设置。
5. 将 App Store 可访问性声明视为有证据支持的产品声明，而不是孤立的控件级别支持的摘要。

## VoiceOver 如何读取元素

VoiceOver 按照固定且不可配置的顺序读取元素属性：

**标签 -> 值 -> 特性 -> 提示**

设计您的标签、值和提示时，请考虑此读取顺序。

## SwiftUI 可访问性修饰符

有关详细的 SwiftUI 修饰符示例（标签、提示、特性、分组、自定义控件、可调整操作和自定义操作），请参阅 [参考文献/a11y-patterns.md](参考文献/a11y-patterns.md)。

## 焦点管理

焦点管理是大多数应用程序失败的地方。当 sheet、alert 或 popover 被关闭时，VoiceOver 焦点必须返回到触发它的元素。

本节是关于辅助技术的可访问性焦点。对于键盘焦点、方向焦点、`focusSection()`、场景聚焦值和 `UIFocusGuide`，请使用 `focus-engine` 技能。

审核元素顺序和分组在 [遍历顺序](#遍历顺序)；将键盘焦点机制路由到 `focus-engine`。

### `@AccessibilityFocusState`（iOS 15+）

`@AccessibilityFocusState` 是一个属性包装器，用于读取和写入当前的可访问性焦点。它使用 `Bool` 进行单目标焦点，或使用可选的 `Hashable` 枚举进行多目标焦点。

```swift
struct ContentView: View {
    @State private var showSheet = false
    @AccessibilityFocusState private var focusOnTrigger: Bool

    var body: some View {
        Button("打开设置") { showSheet = true }
            .accessibilityFocused($focusOnTrigger)
            .sheet(isPresented: $showSheet) {
                SettingsSheet()
                    .onDisappear {
                        // 稍微的延迟允许过渡完成后再移动焦点
                        Task { @MainActor in
                            try? await Task.sleep(for: .milliseconds(100))
                            focusOnTrigger = true
                        }
                    }
            }
    }
}
```

### 使用枚举进行多目标焦点

```swift
enum A11yFocus: Hashable {
    case nameField
    case emailField
    case submitButton
}

struct FormView: View {
    @AccessibilityFocusState private var focus: A11yFocus?

    var body: some View {
        Form {
            TextField("姓名", text: $name)
                .accessibilityFocused($focus, equals: .nameField)
            TextField("邮箱", text: $email)
                .accessibilityFocused($focus, equals: .emailField)
            Button("提交") { validate() }
                .accessibilityFocused($focus, equals: .submitButton)
        }
    }

    func validate() {
        if name.isEmpty {
            focus = .nameField // 将 VoiceOver 移动到无效的字段
        }
    }
}
```

### 自定义模态

自定义叠加视图需要 `.isModal` 特性来捕获 VoiceOver 焦点，并需要一个用于关闭的操作：

```swift
CustomDialog()
    .accessibilityAddTraits(.isModal)
    .accessibilityAction(.escape) { dismiss() }
```

作为模态合同的一部分测试关闭：用户必须能够使用相关的辅助技术逃生手势或键盘逃生路径关闭叠加视图，并且焦点应返回到触发器或下一个逻辑目标。

### UIKit 可访问性通知

在 UIKit 上下文中，如果您需要宣布更改或强制移动焦点：

```swift
// 宣布状态更改（例如，“项目已删除”，“上传完成”）
UIAccessibility.post(notification: .announcement, argument: "Upload complete")

// 局部屏幕更新——将焦点移动到特定元素
UIAccessibility.post(notification: .layoutChanged, argument: targetView)

// 全屏幕转换——将焦点移动到新屏幕
UIAccessibility.post(notification: .screenChanged, argument: newScreenView)
```

## 动态类型

使用系统文本样式缩放文本。缩放非文本尺寸：图标大小、间距、控件高度和自定义 hit-region 尺寸应使用 `@ScaledMetric(relativeTo:)` 在需要跟踪文本尺寸的地方。

有关动态类型和自适应布局示例，包括 `@ScaledMetric` 和最小点击目标模式，请参阅 [参考文献/a11y-patterns.md](参考文献/a11y-patterns.md)。

## 自定义旋钮

旋钮允许 VoiceOver 用户快速导航到特定类型的内容。为内容密集型屏幕添加自定义旋钮。有关完整的旋钮示例，请参阅 [参考文献/a11y-patterns.md](参考文献/a11y-patterns.md)。

## 系统可访问性偏好设置

始终尊重这些环境值：

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion
@Environment(\.accessibilityReduceTransparency) var reduceTransparency
@Environment(\.colorSchemeContrast) var contrast         // .standard 或 .increased
@Environment(\.legibilityWeight) var legibilityWeight    // .regular 或 .bold
```

### Reduce Motion

用交叉淡入或无动画替换基于运动的动画：

```swift
withAnimation(reduceMotion ? nil : .spring()) {
    showContent.toggle()
}
content.transition(reduceMotion ? .opacity : .slide)
```

审查每个移动过渡，包括行删除、数量更改、sheet 或结账呈现和模态关闭。在 Reduce Motion 下，用淡入、弹跳、视差、弹簧和大型空间过渡替换滑入、弹跳、视差、弹簧和大型空间过渡，用淡入、即时状态更改或无动画。

### Reduce Transparency、Increase Contrast、Bold Text

```swift
// 当透明度降低时使用实色背景
.background(reduceTransparency ? Color(.systemBackground) : Color(.systemBackground).opacity(0.85))

// 当对比度增加时使用更强颜色
.foregroundStyle(contrast == .increased ? .primary : .secondary)

// 当系统粗体文本启用时使用粗体
.fontWeight(legibilityWeight == .bold ? .bold : .regular)
```

## 装饰性内容

```swift
// 装饰性图像：对 VoiceOver 隐藏
Image(decorative: "background-pattern")
Image("visual-divider").accessibilityHidden(true)

// 文本旁边的图标：标签会自动处理
Label("设置", systemImage: "gear")

// 仅图标的按钮：必须有一个可访问性标签
Button(action: { }) {
    Image(systemName: "gear")
}
.accessibilityLabel("设置")
```

仅在图像除了相邻的可访问性文本外不添加任何信息时，才将其视为装饰性。如果它传达了产品变体、状态、图表点、用户生成的内容或另一个区分性细节，请提供有意义的描述，而不是隐藏它。

## 语音控制

语音控制依赖于可访问性标签来生成语音点击目标。如果标签缺失或不可以发音，语音控制无法定位元素。

- 每个交互式元素必须有一个可发音的可访问性标签（不能只有表情符号，不能只有符号）。
- 标签在可见屏幕内必须是唯一的——重复的标签会迫使用户使用覆盖编号来区分。
- 将 `accessibilityInputLabels` 视为针对长、笨拙、本地化、首字母缩略词密集或常用缩写语音标签的预先冻结可访问性工作；不要将其作为完善工作推迟。语音控制和全键盘访问使用这些。按重要性降序列出替代方案。
- 广泛应用 `accessibilityInputLabels` 到任何主要标签难以发音的可见目标，包括重复的行操作、数量控件、账户/设置链接、媒体控件和具有首字母缩略词或产品名称的本地化标签。
- 使用语音控制启用进行测试：说“显示名称”和“显示编号”以验证所有交互式元素都是可定位的。
- 对于语音控制审查，验证两个覆盖层：“显示名称”确认可发音标签，“显示编号”确认在名称缺失、重复或笨拙时，每个可见的交互式目标仍然可以到达。

有关 `accessibilityInputLabels` 示例和可发音标签指南，请参阅 [参考文献/a11y-patterns.md](参考文献/a11y-patterns.md)。

## 开关控制

开关控制按读取顺序依次扫描可访问性元素。正确的分组和自定义操作对于可用性至关重要。

- 使用 `.accessibilityElement(children: .combine)` 将相关内容分组以减少扫描停止次数。
- 每个扫描目标都应该是意义明确且可操作的。对 VoiceOver 隐藏的装饰性元素也隐藏在开关控制中。
- 开关控制用户无法执行滑动删除、长按或多指手势。将此类交互作为 `.accessibilityAction(named:)` 自定义操作公开——开关控制将其作为菜单呈现。
- 具有非标准 hit 区域的自定义控件应确保 `accessibilityFrame` 准确反映可点击区域（对于点扫描模式）。

有关自定义操作和分组示例，请参阅 [参考文献/a11y-patterns.md](参考文献/a11y-patterns.md)。

## 全键盘访问

全键盘访问（iOS/iPadOS 13.4+）允许用户使用硬件键盘导航和操作应用程序。

审核每个控件是否都可到达、标记、可见聚焦且无需触摸即可操作。将 Tab/方向焦点、`.focusable()`、`@FocusState`、`focusSection()`、场景聚焦值、tvOS 聚焦和 `UIFocusGuide` 实现路由到 `focus-engine`。

- 每个交互式元素都可以通过键盘到达和激活。
- 遍历顺序是逻辑的，不会捕获焦点。
- 聚焦指示器在所有对比度和文本大小设置下都保持可见。
- 仅手势行为具有键盘可操作的替代方案。
- 应用程序快捷方式不会覆盖系统定义的快捷方式，例如 Cmd+C、Cmd+V 或 Cmd+Tab。

有关全键盘访问审核检查，请参阅 [参考文献/a11y-patterns.md](参考文献/a11y-patterns.md)。

## 遍历顺序

元素顺序和分组必须遵循视觉和任务顺序，包括 VoiceOver 滑动顺序、开关控制扫描、语音控制覆盖层和全键盘访问审查。检查缺失或重复的标签、过多的行子元素、隐藏的自定义控件、焦点陷阱以及顺序与任务相悖的组。保持键盘或方向路由机制在 `focus-engine` 中。

## 辅助访问（iOS 18+）

辅助访问为认知障碍用户提供简化的界面。应用程序应支持此模式：

```swift
// 检查辅助访问是否启用（iOS 18+）
@Environment(\.accessibilityAssistiveAccessEnabled) var isAssistiveAccessEnabled

var body: some View {
    if isAssistiveAccessEnabled {
        SimplifiedContentView()
    } else {
        FullContentView()
    }
}
```

主要指南：
- 减少视觉复杂性：较少控件、较大的点击目标、更简单的导航
- 使用清晰、字面的语言作为标签和说明
- 最小化一次呈现的选择数量
- 在设置 > 可访问性 > 辅助访问中启用辅助访问进行测试

## UIKit 可访问性模式

对于自定义 UIKit 视图，请公开有意义的元素、标签、值、特性和操作；使用 `insert`/`remove` 修改特性；使自定义叠加视图成为模态的；并使用适当的通知、布局更改或屏幕更改。加载 [参考文献/a11y-patterns.md](参考文献/a11y-patterns.md) 获取完整的 UIKit 示例。

## AppKit 可访问性模式

优先使用标准 AppKit 控件。对于自定义 `NSView` 或虚拟元素，请公开正确的 `NSAccessibility` 角色、标签、值、操作和状态更改通知。加载 [参考文献/a11y-patterns.md](参考文献/a11y-patterns.md) 获取 `NSAccessibilityElement` 和自定义控件示例。

## 可访问性自定义内容

使用 `.accessibilityCustomContent` 为有用的次要事实提供信息，而不会增加滑动停止次数；为应自动读取的内容保留高重要性。有关 SwiftUI、UIKit 和 AppKit 示例，请参阅 [参考文献/a11y-patterns.md](参考文献/a11y-patterns.md)。

## App Store 可访问性营养标签

对于 App Store 可访问性营养标签、产品页面声明或 App Store Connect 可访问性答案，请阅读 [参考文献/nutrition-labels.md](参考文献/nutrition-labels.md)。

在推荐声明之前，要求用户提供证据，证明用户可以在相关设备类型上使用该功能完成所有常见任务。使用结构化的常见任务按可访问性功能矩阵，包括音频内容字幕（当音频内容字幕相关时）的媒体文本，并明确警告 App Store 可访问性答案必须保持准确，并且不得将其视为营销声明。

## 测试可访问性

### 手动测试

- **可访问性检查器**：审核标签、特性和对比度，针对模拟器和设备。
- **VoiceOver 测试**：在设置 > 可访问性 > VoiceOver 中启用。使用滑动手势导航每个屏幕。
- **语音控制测试**：在设置 > 可访问性 > 语音控制中启用。说“显示名称”和“显示编号”；名称验证可发音标签，而编号验证即使名称重复、缺失或笨拙，每个可见的交互式目标仍然可以到达。
- **全键盘访问测试**：在设置 > 可访问性 > 键盘 > 全键盘访问中启用。通过 Tab 键遍历每个屏幕，并验证所有交互式元素都获得焦点。
- **开关控制测试**：在设置 > 可访问性 > 开关控制中启用。验证扫描顺序是否逻辑，以及自定义操作是否为基于手势的交互呈现。
- **动态类型**：在设置 > 可访问性 > 显示和文本大小 > 较大文本中测试所有文本大小。

### 使用 XCTest 进行自动测试

使用稳定的可访问性标识符定位 `XCUIElement` 值，然后断言存在、启用/选中状态、有意义的标签/值，并在测试环境暴露焦点时断言 `hasFocus`。覆盖关闭焦点恢复、每个模态退出路径和手势替代方案。UI 自动化补充而不是取代 VoiceOver、语音控制、开关控制、键盘、动态类型、对比度、减少运动和减少透明度测试。加载 [参考文献/a11y-patterns.md](参考文献/a11y-patterns.md) 获取 XCTest 示例。

## 常见错误

| 错误 | 修复 |
|---|---|
| 特性分配覆盖行为 | 插入/移除 UIKit 特性或使用 SwiftUI 可访问性特性修饰符。 |
| 关闭时失去焦点 | 将可访问性焦点返回到触发者。 |
| 行创建过多的滑动停止点 | 故意组合相关的子项。 |
| 标签重复控件类型或省略图标含义 | 使用简洁、可发音的操作/名称；特性声明类型。 |
| 动作、文本大小、对比度或透明度是固定的 | 响应匹配的可访问性偏好和自适应文本样式。 |
| 目标太小或只有颜色 | 提供 44×44 目标加上文本、形状或图标语义。 |
| 自定义覆盖不是模态的 | 暴露模态语义、退出操作和恢复。 |

## 审查清单

对于每个常见任务，记录这些门控的证据：

- [ ] 语义：控件暴露简洁的名称、正确的角色/状态/值，以及装饰性、只有颜色、只有手势或可调整内容的替代方案。
- [ ] 导航：分组和遍历是故意的；模态暴露模态和退出行为；焦点返回到启动控件。
- [ ] 输入：Voice Control 名称是可发音且唯一的，显示名称/数字都有效，Switch Control 暴露手势替代方案，全键盘访问没有无法访问的控件、陷阱或覆盖的系统快捷键。
- [ ] 适应：动态类型、减少动作、减少透明度、增加对比度、粗体文本和 44x44 点目标在代表性布局和状态下得到验证。
- [ ] 自动化：XCTest 覆盖稳定的标识符、状态、可用焦点和每个模态退出路径，而不替代手动辅助技术测试。
- [ ] 并发：跨越隔离边界的可访问性值和通知有效负载是 `Sendable`。
- [ ] 声称：每个 App Store 可访问性声明都由每个声明的设备类型对应的完整常见任务证据矩阵支持。

## 参考

- [references/a11y-patterns.md](references/a11y-patterns.md) — SwiftUI 和 UIKit 修饰符示例、分组、自定义操作、旋钮、动态类型
- [references/nutrition-labels.md](references/nutrition-labels.md) — App Store 可访问性营养标签：当前类别及通过/失败标准
- [references/media-accessibility.md](references/media-accessibility.md) — 字幕、音频描述、AVMediaCharacteristic、SDH
