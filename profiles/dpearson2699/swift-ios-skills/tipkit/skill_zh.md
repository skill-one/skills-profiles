# TipKit

使用 TipKit 来处理小的、上下文相关的功能发现时刻：内联提示、弹出提示、规则门控教育以及轻量级引导标记。保留通用的 SwiftUI 架构、导航、布局以及在首次运行时较长的引导流程在它们的同级技能中，除非 TipKit 的呈现是核心问题。

## 内容

- [可用性](#可用性)
- [配置 TipKit](#配置-tipkit)
- [设计良好的提示](#设计良好的提示)
- [定义提示](#定义提示)
- [呈现提示](#呈现提示)
- [规则和事件](#规则和事件)
- [选项和失效](#选项和失效)
- [操作和样式](#操作和样式)
- [提示组](#提示组)
- [测试](#测试)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 可用性

TipKit 的核心 `Tip`、`TipView`、`popoverTip`、规则、事件、选项和测试覆盖在 iOS 17+、iPadOS 17+、macOS 14+、tvOS 17+、watchOS 10+ 和 visionOS 1+ 上可用。

显式地门控较新的 API：

| API | 可用性 | 使用 |
| --- | --- | --- |
| `TipGroup` | iOS 18+ | 分组或序列提示；应用 [提示组](#提示组) 的决策。 |
| `.cloudKitContainer(...)` | iOS 18+ | 跨设备同步提示状态、参数、事件和显示次数。 |
| `MaxDisplayDuration` | iOS 18+ | 在累积显示时间后自动失效。 |
| `resetEligibility()` | iOS 26+ | 在不重置数据存储的情况下，使先前失效的提示再次生效。 |

## 配置 TipKit

在应用程序初始化期间调用一次 `Tips.configure(_:)`，在可以显示任何提示之前。不要从视图的 `onAppear` 或 `.task` 中配置 TipKit。

```swift
import SwiftUI
import TipKit

@main
struct MyApp: App {
    init() {
        do {
            try Tips.configure([
                .datastoreLocation(.applicationDefault),
                .displayFrequency(.daily)
            ])
        } catch {
            assertionFailure("TipKit 配置失败: \(error)")
        }
    }

    var body: some Scene {
        WindowGroup { ContentView() }
    }
}
```

仅在应用程序和扩展或应用程序组成员有意共享提示状态时使用 `.datastoreLocation(.groupContainer(identifier:))`。在应用程序组成员之间保持选项设置的一致性，因为 TipKit 与提示记录一起持久化选项状态。

### 云同步

仅在 iOS 18 及更高版本上使用云同步。启用 iCloud + 云同步并设置背景模式 > 远程通知，然后传递一个容器：

```swift
try Tips.configure([
    .cloudKitContainer(.named("iCloud.com.example.app.tips"))
])
```

优先使用带有 `.tips` 后缀的专用容器。`.automatic` 在存在时使用第一个命名的 `.tips` 容器，然后回退到主容器。

## 设计良好的提示

提示是小的、短暂的辅助。使用它们来处理人们可以在几步简单操作中理解和尝试的功能。如果流程需要长篇解释、多个屏幕或关键的安全/错误信息，则使用教程、警报、内联警告或引导流程。

遵循与 HIG 对齐的默认值：

- 保持标题简短、直接、以行动为导向。
- 使用一到两句话；避免促销或不相关的文本。
- 将提示放置在它们解释的功能附近。
- 当隐藏附近的 UI 会中断任务时，优先使用内联提示。
- 当保留当前布局很重要并且提示可以指向特定控件时，优先使用弹出提示。
- 使用规则和显示频率，以便只有目标受众看到每个提示。
- 当弹出提示已经指向该图标时，避免在提示中重复图标。

## 定义提示

`Tip` 符合 `Identifiable` 和 `Sendable`。至少提供 `title`；仅在它们改进功能发现时刻时添加 `message`、`image`、`actions`、`rules`、`options` 和 `id`。

```swift
import TipKit

struct FavoriteTip: Tip {
    var title: Text { Text("保存到收藏夹") }
    var message: Text? { Text("点击心形图标以快速访问项目。") }
    var image: Image? { Image(systemName: "heart.fill") }
}
```

默认情况下，TipKit 使用提示类型名称作为 `id`。为可重用的提示覆盖 `id`，其持久化状态应根据内容变化：

```swift
struct NewItemTip: Tip {
    let itemID: Item.ID

    var id: String { "NewItemTip-\(itemID)" }
    var title: Text { Text("有新项目可用") }
}
```

使用稳定、具体的标识符。不要从暂时的文本或不可靠的排序中派生 ID。

## 呈现提示

使用 `TipView` 用于内联提示：

```swift
let favoriteTip = FavoriteTip()

VStack {
    TipView(favoriteTip, arrowEdge: .bottom)
    ItemListView()
}
```

当提示应指向控件时，使用 `.popoverTip`：

```swift
Button {
    toggleFavorite()
    favoriteTip.invalidate(reason: .actionPerformed)
} label: {
    Image(systemName: "heart")
}
.popoverTip(favoriteTip, arrowEdge: .top)
```

## 规则和事件

规则是按 AND 组合的。只有当每个规则都通过时，提示才会变得有资格。

使用 `@Parameter` 用于持久化的应用程序状态：

```swift
struct FavoriteTip: Tip {
    @Parameter static var hasSeenList = false

    var title: Text { Text("保存到收藏夹") }

    var rules: [Rule] {
        #Rule(Self.$hasSeenList) { $0 == true }
    }
}
```

使用 `Tips.Event` 用于重复的用户操作。默认情况下，TipKit 查询最近的 1000 次捐赠，因此请保持事件规则有边界和目的性。

```swift
struct ShortcutTip: Tip {
    static let manualSaveEvent = Tips.Event(id: "manualSave")

    var title: Text { Text("更快保存") }

    var rules: [Rule] {
        #Rule(Self.manualSaveEvent) {
            $0.donations.donatedWithin(.week).count >= 3
        }
    }
}

ShortcutTip.manualSaveEvent.sendDonation()
```

对于更丰富的事件规则，定义 `Tips.Event<DonationInfo>`，其中 `DonationInfo: Codable, Sendable`。保持捐赠有效负载小。

当多个提示使用相同的事件时，将相关的事件定义分组在共享的命名空间中；事件 ID 是持久化边界，因此冲突可能会造成资格混乱。

## 选项和失效

谨慎使用选项；频率和失效规则是提示持久化行为的一部分。

```swift
struct DailyTip: Tip {
    var title: Text { Text("尝试过滤器") }

    var options: [any TipOption] {
        MaxDisplayCount(3)
        IgnoresDisplayFrequency(false)
    }
}
```

`MaxDisplayDuration` 是 iOS 18+。它计算累积显示时间，并且在有最小连续显示持续时间后才会发生自动失效。当应用程序知道教授的操作或有序步骤已完成时，不要将其用作显式 `invalidate(reason:)` 的替代品。

当用户执行发现的操作或提示不再相关时，调用 `invalidate(reason:)`。失效是永久性的，直到数据存储被重置，或在 iOS 26+ 上特定提示调用 `await resetEligibility()`。

```swift
favoriteTip.invalidate(reason: .actionPerformed)
```

使用 `.tipClosed` 用于显式关闭，以及 `.displayCountExceeded` 或 `.displayDurationExceeded` 仅在描述自动失效结果时使用。

## 操作和样式

当用户需要直接路线到设置、更多信息或设置流程时，添加 `Action` 按钮。

```swift
struct FeatureTip: Tip {
    var title: Text { Text("尝试新编辑器") }

    var actions: [Action] {
        Action(id: "open-editor", title: "打开编辑器")
        Action(id: "learn-more", title: "了解更多")
    }
}

TipView(FeatureTip()) { action in
    switch action.id {
    case "open-editor":
        openEditor()
    case "learn-more":
        showHelp()
    default:
        break
    }
}
```

对于自定义外观，优先使用 `TipViewStyle.Configuration` 值而不是直接从具体的提示实例读取。这保留了应用于 `TipView` 的标签、处理程序和修饰符。

```swift
struct CompactTipStyle: TipViewStyle {
    func makeBody(configuration: Configuration) -> some View {
        HStack(alignment: .top) {
            configuration.image?
            VStack(alignment: .leading) {
                configuration.title?
                configuration.message?
                ForEach(configuration.actions) { action in
                    Button(action: action.handler) {
                        action.label()
                    }
                }
            }
        }
        .padding()
    }
}
```

## 提示组

`TipGroup` 是 iOS 18+。将组存储在 SwiftUI 状态中，以便可观察的组对象跨视图更新持久化。在审查 `TipGroup(.ordered)` 计划的每个时刻，明确区分默认优先级和有序序列：`TipGroup` 默认为 `.firstAvailable`，而 `TipGroup(.ordered)` 是必需的，因为每个后续提示都必须等待所有先前的提示失效。

```swift
struct OnboardingView: View {
    @State private var tips = TipGroup(.ordered) {
        WelcomeTip()
        SearchTip()
        FilterTip()
    }

    var body: some View {
        VStack {
            TipView(tips.currentTip)
            ContentView()
        }
    }
}
```

`MaxDisplayDuration` 可以限制显示时间，但它不是有序组的排序机制。当相同的组跨越多个控件时，强制转换 `currentTip`：

```swift
Button("搜索") { openSearch() }
    .popoverTip(tips.currentTip as? SearchTip)
```

## 测试

仅在调试/测试代码中使用测试覆盖，并在 `Tips.configure(_:)` 之前应用它们。

```swift
#if DEBUG
if ProcessInfo.processInfo.arguments.contains("--reset-tips") {
    try? Tips.resetDatastore()
}
if ProcessInfo.processInfo.arguments.contains("--show-all-tips") {
    Tips.showAllTipsForTesting()
}
#endif

try Tips.configure()
```

内置启动参数也是可用的：

- `-com.apple.TipKit.ResetDatastore 1`
- `-com.apple.TipKit.ShowAllTips 1`
- `-com.apple.TipKit.ShowTips TipTypeA,TipTypeB`
- `-com.apple.TipKit.HideAllTips 1`

测试覆盖的优先级是特定的显示、特定的隐藏、显示所有、然后隐藏所有。`Tips.resetDatastore()` 必须在 `Tips.configure(_:)` 之前运行。

## 常见错误

### 不要：从视图配置 TipKit

在应用程序初始化期间配置。视图级别的配置可能与提示显示竞争，还可能触发数据存储已配置错误。

### 不要：将 iOS 18+ API 作为 iOS 17 指导呈现

门控 `TipGroup`、云同步和 `MaxDisplayDuration`。对于组优先级，应用标准的 [提示组](#提示组) 决策。

### 不要：使用提示进行关键信息

提示是可关闭的，用于教育。使用警报、确认、内联警告或阻塞 UI 来处理安全、错误、数据丢失和必需步骤。

### 不要：发布测试覆盖

`showAllTipsForTesting()` 和相关覆盖绕过规则和频率限制。将它们保留在 `#if DEBUG`、测试方案参数或仅限 UI 测试的启动参数后面。

### 不要：使用不稳定的可重用提示 ID

提示 ID 拥有持久化。如果可重用提示的 ID 意外更改，用户可能会看到重复或过时的教育。

## 审查清单

- [ ] `Tips.configure(_:)` 在提示显示之前在应用程序初始化期间运行一次。
- [ ] `Tips.resetDatastore()` 仅在配置之前运行，并且仅用于测试/调试。
- [ ] iOS 18+ 和 iOS 26+ 的 TipKit API 有可用性门控或回退指导。
- [ ] 提示文本简短、上下文相关、以行动为导向，并且不是促销性的。
- [ ] 内联与弹出呈现与周围的 UI 流匹配。
- [ ] 规则针对目标受众，并且在首次启动时不显示每个提示。
- [ ] 事件 ID 是稳定的，在共享时命名空间化，并且捐赠有效负载很小。
- [ ] 可重用提示使用稳定的内容派生值覆盖 `id`。
- [ ] 提示在用户执行教授的操作时失效。
- [ ] `TipGroup` 保持 `@State` 并遵循提示组优先级决策。
- [ ] 云同步使用 iCloud + 云同步、远程通知，并在适当的时候使用专用容器。
- [ ] 自定义样式使用 `configuration` 值并调用 `action.label()`。
- [ ] 测试覆盖是调试/测试专用的，并且永远不会在生产中激活。

## 参考资料

- 阅读 [references/tipkit-patterns.md](references/tipkit-patterns.md) 以获取完整的实现模式：自定义样式、带捐赠值的事件规则、TipGroup 排序、云同步/应用程序组持久化、可重用 ID、预览和测试启动策略。
- Apple TipKit 文档：https://sosumi.ai/documentation/tipkit
- Apple `Tips.configure(_:)`：https://sosumi.ai/documentation/tipkit/tips/configure(_:)
- Apple `TipGroup`：https://sosumi.ai/documentation/tipkit/tipgroup
- Apple HIG "提供帮助"：https://sosumi.ai/design/human-interface-guidelines/offering-help
- WWDC24 "使用 TipKit 自定义功能发现"：https://sosumi.ai/videos/play/wwdc2024/10070
- WWDC23 "使用 TipKit 使功能可发现"：https://sosumi.ai/videos/play/wwdc2023/10229
