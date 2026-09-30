---
name: widgetkit
description: 实现、审查或改进 WidgetKit 组件和控件。在构建带有时间线提供者的主屏幕、锁屏、待机或 CarPlay 组件时使用；配置带有 AppIntentTimelineProvider 的可配置组件；使用 Button/Toggle 连接实现交互式组件或控制中心控件；WidgetKit 推送重新加载、刷新预算、深度链接、智能堆栈相关性、Liquid Glass/强调渲染、组件扩展设置、WidgetBundle、App Groups 和权限。
---

# WidgetKit

构建主屏幕小组件、锁屏小组件、控制中心控件，以及适用于 iOS 26+ 的 StandBy 或 CarPlay 小组件表面。

将相邻框架的指导范围限制在 WidgetKit 集成范围内。仅在它们直接连接到 WidgetKit 表面时包含 ActivityKit 和 App Intents；将完整生命周期、APNs 内容状态、Siri/快捷指令/Spotlight 或实体建模工作移交给同级的 `activitykit` 或 `app-intents` 技能。

有关时间线策略、基于推送的更新、Xcode 设置和高级模式，请参阅 [参考资料/widgetkit-advanced.md](references/widgetkit-advanced.md)。

## 目录

- [工作流](#workflow)
- [小组件协议和 WidgetBundle](#widget-protocol-and-widgetbundle)
- [配置类型](#configuration-types)
- [TimelineProvider](#timelineprovider)
- [AppIntentTimelineProvider](#appintenttimelineprovider)
- [小组件系列](#widget-families)
- [交互式小组件 (iOS 17+)](#interactive-widgets-ios-17)
- [ActivityConfiguration 交接](#activityconfiguration-handoff)
- [控制中心小组件 (iOS 18+)](#control-center-widgets-ios-18)
- [锁屏小组件](#lock-screen-widgets)
- [StandBy 模式](#standby-mode)
- [小组件 URL 处理和深度链接](#widget-url-handling-and-deep-links)
- [智能堆栈相关性](#smart-stack-relevance)
- [设计模式](#design-patterns)
- [iOS 26 新增功能](#ios-26-additions)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 工作流

### 1. 创建新的小组件

1. 在 Xcode 中添加一个小组件扩展目标（文件 > 新建 > 目标 > 小组件扩展）。
2. 启用 App Groups 以便在应用和小组件扩展之间共享数据。
3. 定义一个具有 `date` 属性和显示数据的 `TimelineEntry` 结构体。
4. 实现 `TimelineProvider`（静态）或 `AppIntentTimelineProvider`（可配置）。
5. 使用 SwiftUI 构建小组件视图，根据 `WidgetFamily` 适应布局。
6. 声明符合配置和支持的小组件系列的 `Widget` 协议结构体。
7. 在带有 `@main` 注解的 `WidgetBundle` 中注册所有小组件。

### 2. 集成相邻表面

1. 当应用具有 Live Activity 时，在小组件包中注册 `ActivityConfiguration`，但将 `ActivityAttributes`、请求/更新/结束、APNs `content-state` 和动态岛布局深度保留在 `activitykit` 中。
2. 将 `Button`、`Toggle`、`ControlWidgetButton` 和 `ControlWidgetToggle` 放置在 WidgetKit 视图或控件中，但将意图建模、实体、查询、Siri、快捷指令和 Spotlight 保留在 `app-intents` 中。

### 3. 添加控制中心控件

1. 为按钮重用 `AppIntent`/`OpenIntent`，为切换重用 `SetValueIntent`。
2. 在小组件包中创建 `ControlWidgetButton` 或 `ControlWidgetToggle`。
3. 使用 `StaticControlConfiguration` 或 `AppIntentControlConfiguration`。

### 4. 审查现有小组件代码

运行本文档末尾的审查清单。

## 小组件协议和 WidgetBundle

### 小组件

每个小组件都符合 `Widget` 协议，并从其 `body` 返回一个 `WidgetConfiguration`。

```swift
struct OrderStatusWidget: Widget {
    let kind: String = "OrderStatusWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: OrderProvider()) { entry in
            OrderWidgetView(entry: entry)
        }
        .configurationDisplayName("订单状态")
        .description("跟踪您的当前订单。")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}
```

### WidgetBundle

使用 `WidgetBundle` 从单个扩展中公开多个小组件。

```swift
@main
struct MyAppWidgets: WidgetBundle {
    var body: some Widget {
        OrderStatusWidget()
        FavoritesWidget()
        DeliveryActivityWidget()   // ActivityConfiguration 交接
        QuickActionControl()       // 控制中心
    }
}
```

## 配置类型

使用 `StaticConfiguration` 用于非可配置的小组件。使用 `AppIntentConfiguration`（推荐）用于与 `AppIntentTimelineProvider` 配对的可配置小组件。

```swift
// 静态
StaticConfiguration(kind: "MyWidget", provider: MyProvider()) { entry in
    MyWidgetView(entry: entry)
}
// 可配置
AppIntentConfiguration(kind: "ConfigWidget", intent: SelectCategoryIntent.self,
                       provider: CategoryProvider()) { entry in
    CategoryWidgetView(entry: entry)
}
```

### 共享修饰符

| 修饰符 | 目的 |
|---|---|
| `.configurationDisplayName(_:)` | 在小组件库中显示的名称 |
| `.description(_:)` | 在小组件库中显示的描述 |
| `.supportedFamilies(_:)` | `WidgetFamily` 值的数组 |
| `.supplementalActivityFamilies(_:)` | Live Activity 尺寸（`.small`，`.medium`） |

## TimelineProvider

用于静态（非可配置）的小组件。使用完成处理程序。三个必需方法：

```swift
struct WeatherProvider: TimelineProvider {
    typealias Entry = WeatherEntry

    func placeholder(in context: Context) -> WeatherEntry {
        WeatherEntry(date: .now, temperature: 72, condition: "晴朗")
    }

    func getSnapshot(in context: Context, completion: @escaping (WeatherEntry) -> Void) {
        let entry = context.isPreview
            ? placeholder(in: context)
            : WeatherEntry(date: .now, temperature: currentTemp, condition: currentCondition)
        completion(entry)
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<WeatherEntry>) -> Void) {
        Task {
            let weather = await WeatherService.shared.fetch()
            let entry = WeatherEntry(date: .now, temperature: weather.temp, condition: weather.condition)
            let nextUpdate = Calendar.current.date(byAdding: .hour, value: 1, to: .now)!
            completion(Timeline(entries: [entry], policy: .after(nextUpdate)))
        }
    }
}
```

## AppIntentTimelineProvider

用于可配置的小组件。原生使用 async/await。接收用户意图配置。

```swift
struct CategoryProvider: AppIntentTimelineProvider {
    typealias Entry = CategoryEntry
    typealias Intent = SelectCategoryIntent

    func placeholder(in context: Context) -> CategoryEntry {
        CategoryEntry(date: .now, categoryName: "示例", items: [])
    }

    func snapshot(for config: SelectCategoryIntent, in context: Context) async -> CategoryEntry {
        let items = await DataStore.shared.items(for: config.category)
        return CategoryEntry(date: .now, categoryName: config.category.name, items: items)
    }

    func timeline(for config: SelectCategoryIntent, in context: Context) async -> Timeline<CategoryEntry> {
        let items = await DataStore.shared.items(for: config.category)
        let entry = CategoryEntry(date: .now, categoryName: config.category.name, items: items)
        return Timeline(entries: [entry], policy: .atEnd)
    }
}
```

## 小组件系列

| 系列 | 平台 |
|---|---|
| `.systemSmall` | iOS、iPadOS、macOS、CarPlay (iOS 26+) |
| `.systemMedium` | iOS、iPadOS、macOS |
| `.systemLarge` | iOS、iPadOS、macOS |
| `.systemExtraLarge` | 仅 iPadOS |
| `.accessoryCircular` | iOS、watchOS |
| `.accessoryRectangular` | iOS、watchOS |
| `.accessoryInline` | iOS、watchOS |
| `.accessoryCorner` | 仅 watchOS |

根据系列调整布局，使用 `@Environment(\.widgetFamily)`：

```swift
@Environment(\.widgetFamily) var family

var body: some View {
    switch family {
    case .systemSmall: CompactView(entry: entry)
    case .systemMedium: DetailedView(entry: entry)
    case .accessoryCircular: CircularView(entry: entry)
    default: FullView(entry: entry)
    }
}
```

## 交互式小组件 (iOS 17+)

使用具有小组件扩展或共享代码中可用的意图类型的 `Button` 和 `Toggle`。WidgetKit 拥有视图布局；`app-intents` 拥有意图建模和行为。

```swift
struct InteractiveWidgetView: View {
    let entry: FavoriteEntry

    var body: some View {
        Button(intent: ToggleFavoriteIntent(itemID: entry.itemID)) {
            Image(systemName: entry.isFavorite ? "star.fill" : "star")
        }
    }
}
```

## ActivityConfiguration 交接

WidgetKit 在小组件扩展中注册 Live Activity 表面。保留此部分用于注册和渲染交接；使用 `activitykit` 用于 `ActivityAttributes`、生命周期、推送更新和完整的动态岛模式。

```swift
struct DeliveryActivityWidget: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: DeliveryAttributes.self) { context in
            DeliveryLiveActivityView(context: context)
        } dynamicIsland: { context in
            DeliveryDynamicIsland(context: context)
        }
    }
}
```

## 控制中心小组件 (iOS 18+)

WidgetKit 拥有控件配置、布局、类型、显示名称、推送处理程序和扩展注册。控件操作和值意图属于 `app-intents`。

```swift
struct OpenCameraControl: ControlWidget {
    var body: some ControlWidgetConfiguration {
        StaticControlConfiguration(kind: "OpenCamera") {
            ControlWidgetButton(action: OpenCameraIntent()) {
                Label("相机", systemImage: "camera.fill")
            }
        }
        .displayName("打开相机")
    }
}

struct FlashlightControl: ControlWidget {
    var body: some ControlWidgetConfiguration {
        StaticControlConfiguration(kind: "手电筒", provider: FlashlightValueProvider()) { value in
            ControlWidgetToggle(isOn: value, action: ToggleFlashlightIntent()) {
                Label("手电筒", systemImage: value ? "flashlight.on.fill" : "flashlight.off.fill")
            }
        }
        .displayName("手电筒")
    }
}
```

## 锁屏小组件

使用附件系列和 `AccessoryWidgetBackground`。

```swift
struct StepsWidget: Widget {
    let kind = "StepsWidget"
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: StepsProvider()) { entry in
            ZStack {
                AccessoryWidgetBackground()
                VStack {
                    Image(systemName: "figure.walk")
                    Text("\(entry.stepCount)").font(.headline)
                }
            }
        }
        .supportedFamilies([.accessoryCircular, .accessoryRectangular, .accessoryInline])
    }
}
```

## StandBy 模式

小型系统小组件可以出现在 StandBy 和 CarPlay 中。使用 `@Environment(\.widgetLocation)` 进行条件渲染：

```swift
@Environment(\.widgetLocation) var location
// location == .standBy, .homeScreen, .lockScreen, .carPlay, 等等。
```

## 小组件 URL 处理和深度链接

使用一个 `.widgetURL(_:)` 作为整个小组件的备用路由。仅当系列和布局支持时，使用 `Link` 进行有意的目标，包括 `.accessoryRectangular`、`.systemSmall` 和更大的系统小组件。对于小型小组件，优先考虑一个清晰的备用方案；除非视觉提示和点击区域保持明确，否则避免多个 `Link` 目标。

在层次结构中永远不会附加多个 `widgetURL` 修饰符。

## Smart Stack 相关性

在时间线条目上使用 `TimelineEntryRelevance(score:duration:)` 以便在 iPhone 和 iPad Smart Stack 中及时显示相关性。保持分数在一致的正面尺度上；零或更低表示不相关。

对于可配置的小组件，从应用端代码捐赠与用户操作或小组件参数对应的 App Intents，例如使用 `intent.donate()` 或 `IntentDonationManager`。保持 `AppEntity` 和 `EntityQuery` 设计在 `app-intents` 中。

在 watchOS 上，上下文相关性使用 `WidgetRelevance([WidgetRelevanceAttribute(...)])` 从提供者 `relevance()` 回调中使用。该路径不是 iPhone 或 iPad Smart Stacks 使用的路径。

## 设计模式

- **优先使用 `Gauge` 而不是手动弧线。** 使用 `.gaugeStyle(.accessoryCircular)` 用于锁屏圆形小组件，使用 `.linearCapacity` 用于主屏幕容量条。系统处理样式、无障碍访问和渲染模式适应。
- **使用 `.containerBackground(_:for: .widget)`（iOS 17+）用于小组件背景，而不是填充和背景修饰符。**
- **使用 `Canvas` 用于密集可视化**，如火花线或迷你条形图。由于整个小组件表面是一个单一的点击目标，因此缺少每个元素的访问性是可以接受的。
- **使时间线刷新与数据粒度匹配。** 预算是动态和机会主义的；安排有用的未来条目，避免不必要的重新加载，并使用 `Text(timerInterval:countsDown:)` 用于实时倒计时。加载高级参考资料以获取当前预算指导。

有关代码示例和每个模式详细指导，请参阅 [参考资料/widgetkit-advanced.md](references/widgetkit-advanced.md)。

## iOS 26 新增功能

### 液态玻璃支持

使用 `@Environment(\.widgetRenderingMode)`、`.widgetAccentable()` 和 `Image.widgetAccentedRenderingMode(_:)` 使小组件适应液态玻璃。在 `.vibrant` 中，系统将内容映射到材料样式，因此避免仅依赖原始颜色。

### 推送重新加载处理程序

小组件推送重新加载：
- 向小组件扩展目标添加推送通知功能。
- 将 `WidgetPushHandler` 类型保留在小组件扩展目标或链接到它的共享代码中，而不仅限于主应用目标。
- 使用 `.pushHandler(...)` 在小组件配置上注册处理程序。
- 不要使用用户通知注册来获取小组件推送令牌；WidgetKit 通过 `pushTokenDidChange(_:widgets:)` 供应令牌。
- 使用 `apns-push-type: widgets`、主题后缀 `.push-type.widgets` 和 `aps.content-changed`。
- 将推送视为预算内、机会主义的重新加载信号，而不是状态传递，也不是唯一的 freshness 模型。时间线、重新加载策略、共享存储或重新获取、应用触发的 `WidgetCenter` 重新加载仍然是备用路径。

控件推送重新加载：
- 使用 `.pushHandler(...)` 在 `ControlWidgetConfiguration` 上注册 `ControlPushHandler`。
- `pushTokensDidChange(controls:)` 接收 `[ControlInfo]`；从每个控件的 `pushInfo` 中读取令牌。
- 使用 `apns-push-type: controls`、主题后缀 `.push-type.controls` 和 `aps.content-changed`。

### CarPlay 小组件

在 iOS 26+ 的 CarPlay 中可以显示小型系统小组件。确保布局在一瞥中可读；点击和控制取决于车辆触摸支持，对于打开应用，还取决于 CarPlay 集成。

## 常见错误

1. **使用 IntentTimelineProvider 而不是 AppIntentTimelineProvider。**
   `IntentTimelineProvider` 是旧的基于 SiriKit Intents 的提供程序。优先使用与 App Intents 框架配合的 `AppIntentTimelineProvider` 用于新小组件。

2. **超出刷新预算。** 小组件有一个每日刷新限制。不要在每次微小数据变化时调用 `WidgetCenter.shared.reloadTimelines(ofKind:)`。批量更新并使用适当的 `TimelineReloadPolicy` 值。

3. **忘记 App Groups 用于共享数据。** 小组件扩展在单独的进程中运行。使用 `UserDefaults(suiteName:)` 或共享 App Group 容器用于小组件读取的数据。

4. **在 placeholder() 中执行网络调用。** `placeholder(in:)` 必须同步返回样本数据。使用 `getTimeline` 或 `timeline(for:in:)` 进行异步工作。

5. **将 WidgetKit 推送有效负载视为状态。** 小组件和控件推送是重新加载信号。在共享存储中持久化状态或在提供者中重新获取它。

6. **通过用户通知注册小组件推送。** 小组件推送令牌来自 WidgetKit 处理程序，而不是 `UNUserNotificationCenter`。

7. **将重逻辑放在小组件视图中。** 小组件视图在大小受限的进程中渲染。在时间线提供者中预计算数据，并通过条目传递显示就绪的值。

8. **忽略附件渲染模式。** 锁屏小组件在 `.vibrant` 或 `.accented` 模式下渲染，而不是 `.fullColor`。使用 `@Environment(\.widgetRenderingMode)` 进行测试，并避免仅依赖颜色。

9. **不在设备上测试。** StandBy、CarPlay 和附件渲染与模拟器差异很大。始终在物理硬件上验证。

## 审查清单

- [ ] 小部件扩展的目标具有与主应用匹配的应用组权限
- [ ] `@main` 位于 `WidgetBundle` 上，而不是单个小部件上
- [ ] `placeholder(in:)` 同步返回；`getSnapshot`/`snapshot(for:in:)` 在 `isPreview` 时快速
- [ ] 时间线刷新策略与更新频率匹配；`reloadTimelines(ofKind:)` 仅在数据变化时触发
- [ ] 布局根据 `WidgetFamily` 进行适配；在 `.vibrant` 模式下测试辅助小部件
- [ ] 交互式小部件仅使用可扩展的应用内意图，并通过 `Button`/`Toggle` 触发
- [ ] 使用一个 `.widgetURL(_:)` 备用方案；`Link` 子目标与应用家族匹配
- [ ] 小部件推送处理程序位于小部件扩展/共享代码中，并且不使用用户通知令牌注册
- [ ] 小部件/控制推送补充时间线和共享状态/重取备用方案
- [ ] 智能堆栈的相关性使用时间线相关性和应用侧意图捐赠（在有用时）
- [ ] Live Activity 生命周期和应用意图建模已移交给兄弟技能
- [ ] 控制使用 `StaticControlConfiguration`/`AppIntentControlConfiguration`
- [ ] 时间线条目和意图类型是 Sendable；已在设备上测试

## 参考

- 高级指南：[references/widgetkit-advanced.md](references/widgetkit-advanced.md)
- Apple 文档：[WidgetKit](https://sosumi.ai/documentation/widgetkit) | [保持小部件更新](https://sosumi.ai/documentation/widgetkit/keeping-a-widget-up-to-date) | [智能堆栈可见性](https://sosumi.ai/documentation/widgetkit/widget-suggestions-in-smart-stacks)
