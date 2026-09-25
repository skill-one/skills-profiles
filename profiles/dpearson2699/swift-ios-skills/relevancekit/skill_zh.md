# RelevanceKit

提供设备端的上下文线索，以提高小部件在 Apple Watch 智能堆栈中的可见性。RelevanceKit 通过时间、位置、健身状态、睡眠计划或连接的硬件告诉系统小部件何时相关。支持 Swift 6.3 / watchOS 26+。

> **Beta敏感。** 在做出 RelevanceKit 可用性或行为方面的强有力声明之前，请重新检查 Apple 文档。

有关完整的相关小部件、时间线提供者、分组、预览和权限模式，请参阅 [references/relevancekit-patterns.md](references/relevancekit-patterns.md)。

## 目录

- [概述](#概述)
- [设置](#设置)
- [相关性提供者](#相关性提供者)
- [边界路由](#边界路由)
- [基于时间的相关性](#基于时间的相关性)
- [基于位置的相关性](#基于位置的相关性)
- [健身和睡眠相关性](#健身和睡眠相关性)
- [硬件相关性](#硬件相关性)
- [组合信号](#组合信号)
- [小部件集成](#小部件集成)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 概述

watchOS 使用两种机制来确定小部件在智能堆栈中的相关性：

1. **时间线提供者相关性** -- 在现有的 `AppIntentTimelineProvider` 上实现 `relevance()` 以将 `RelevantContext` 线索附加到时间线条目。跨平台可用；仅 watchOS 处理数据。
2. **相关小部件** -- 使用 `RelevanceConfiguration` 与 `RelevanceEntriesProvider` 来构建完全由相关性线索驱动的小部件。系统为每个相关条目创建单独的智能堆栈卡片。仅 watchOS 26+。

当小部件始终有数据要显示且相关性是补充时，选择时间线提供者。当小部件仅在条件匹配时出现，或应同时出现多个卡片时（例如，多个即将到来的日历事件），选择相关小部件。

### 关键类型

| 类型 | 模块 | 角色 |
|---|---|---|
| `RelevantContext` | RelevanceKit | 上下文线索（日期、位置、健身、睡眠、硬件） |
| `WidgetRelevance` | WidgetKit | 小部件类型的关联性属性集合 |
| `WidgetRelevanceAttribute` | WidgetKit | 将小部件配置与 `RelevantContext` 配对 |
| `WidgetRelevanceGroup` | WidgetKit | 控制智能堆栈中的分组行为 |
| `RelevanceConfiguration` | WidgetKit | 由相关性线索驱动的小部件配置（watchOS 26+） |
| `RelevanceEntriesProvider` | WidgetKit | 为相关性配置的小部件提供条目（watchOS 26+） |
| `RelevanceEntry` | WidgetKit | 渲染一个相关小部件卡片所需的数据（watchOS 26+） |

`RelevanceConfiguration`、`RelevanceEntriesProvider` 和 `RelevanceEntry` 是 WidgetKit API。仅在它们是 watchOS 相关小部件工作流程的一部分并暴露 RelevanceKit 线索时，才将它们保留在此技能的作用域内。

## 设置

### 导入

```swift
import RelevanceKit
import WidgetKit
```

### 平台可用性

`RelevantContext` 跨平台声明（iOS 17+、watchOS 10+），但 **RelevanceKit 功能仅在 watchOS 上生效**。在其他平台上调用 API 没有任何效果。时间线提供者的 `relevance()` 在 iOS 18+、macOS 15+、visionOS 26+ 和 watchOS 11+ 上可用以共享提供者代码。`RelevanceConfiguration`、`RelevanceEntriesProvider` 和 `RelevanceEntry` 仅 watchOS 26+。

### 权限

某些相关性线索需要授权或目标设置：

| 线索 | 需要的权限 |
|---|---|
| `.location(inferred:)` | 包含应用请求位置访问；小部件扩展声明 `NSWidgetWantsLocation` |
| `.location(_:)` (CLRegion) | 包含应用请求位置访问；小部件扩展声明 `NSWidgetWantsLocation` |
| `.location(category:)` | 包含应用请求位置访问；小部件扩展声明 `NSWidgetWantsLocation` |
| `.fitness(.workoutActive)` | HealthKit 访问 `HKWorkoutType` |
| `.fitness(.activityRingsIncomplete)` | HealthKit 访问 `appleExerciseTime`、`appleMoveTime` 和 `appleStandTime` |
| `.sleep(_:)` | HealthKit `sleepAnalysis` 权限 |
| `.hardware(headphones:)` | 无 |
| `.date(...)` | 无 |

将位置目的字符串添加到包含应用的 `Info.plist` 中，而不仅仅是小部件扩展。在代码中，在依赖位置线索之前检查 `CLLocationManager.isAuthorizedForWidgetUpdates`。对于健身和睡眠线索，启用 HealthKit 并在提供相关性的应用和小部件扩展目标中请求确切的读取类型。

## 相关性提供者

### 选项 1：具有相关性的时间线提供者

向现有的 `AppIntentTimelineProvider` 添加一个 `relevance()` 方法。这种方法在 iOS 和 watchOS 之间共享代码，同时添加了 watchOS 智能堆栈智能。

```swift
struct MyProvider: AppIntentTimelineProvider {
    // ... 快照、时间线、占位符 ...

    func relevance() async -> WidgetRelevance<MyWidgetIntent> {
        let attributes = events.map { event in
            let context = RelevantContext.date(
                from: event.startDate,
                to: event.endDate
            )
            return WidgetRelevanceAttribute(
                configuration: MyWidgetIntent(event: event),
                context: context
            )
        }
        return WidgetRelevance(attributes)
    }
}
```

### 选项 2：RelevanceEntriesProvider（watchOS 26+）

构建一个仅在条件匹配时出现的小部件。系统调用 `relevance()` 来学习小部件何时重要，然后调用 `entry()` 以获取匹配的配置以获取渲染数据。

```swift
@available(watchOS 26.0, *)
struct MyRelevanceProvider: RelevanceEntriesProvider {
    func relevance() async -> WidgetRelevance<MyWidgetIntent> {
        let attributes = events.map { event in
            WidgetRelevanceAttribute(
                configuration: MyWidgetIntent(event: event),
                context: RelevantContext.date(event.date, kind: .scheduled)
            )
        }
        return WidgetRelevance(attributes)
    }

    func entry(
        configuration: MyWidgetIntent,
        context: Context
    ) async throws -> MyRelevanceEntry {
        if context.isPreview {
            return .preview
        }
        return MyRelevanceEntry(event: configuration.event)
    }

    func placeholder(context: Context) -> MyRelevanceEntry {
        .placeholder
    }
}
```

## 边界路由

当功能混合小部件、位置、健身和智能堆栈相关性时，保持 RelevanceKit 聚焦于 `RelevantContext`、`WidgetRelevanceAttribute`、提供者 `relevance()`、`RelevantIntentManager`、相关小部件转接以及相关性线索的权限。将时间线、重新加载预算、家族、渲染、APNs 小部件推送、实时活动和小部件控件路由到 WidgetKit；将 `HKWorkoutSession`、`HKLiveWorkoutBuilder`、`HKWorkoutRoute`、查询、活动环/睡眠数据以及授权 UX 路由到 HealthKit；将 `MKLocalSearch`、`MKLocalSearchCompleter`、`MKDirections`、地理编码、授权、区域、地理围栏和位置数据路由到 MapKit/CoreLocation。

## 基于时间的相关性

时间线索告诉系统小部件在特定时刻或周围相关。

### 单个日期

```swift
RelevantContext.date(eventDate)
```

### 带有类型的日期

`DateKind` 提供有关时间相关性的性质的附加提示：

| 类型 | 用途 |
|---|---|
| `.default` | 一般时间相关性 |
| `.scheduled` | 计划事件（会议、航班） |
| `.informational` | 与时间相关的信息（天气预报） |

```swift
RelevantContext.date(meetingStart, kind: .scheduled)
```

### 日期范围

```swift
// 使用 from/to
RelevantContext.date(from: startDate, to: endDate)

// 使用 DateInterval
RelevantContext.date(interval: dateInterval, kind: .scheduled)

// 使用 ClosedRange
RelevantContext.date(range: startDate...endDate, kind: .default)
```

## 基于位置的相关性

### 推断位置

系统根据一个人的日常习惯推断某些位置。不需要坐标。

```swift
RelevantContext.location(inferred: .home)
RelevantContext.location(inferred: .work)
RelevantContext.location(inferred: .school)
RelevantContext.location(inferred: .commute)
```

应用 [权限](#permissions) 表中的位置行，并在返回线索之前检查 `CLLocationManager.isAuthorizedForWidgetUpdates`。

### 特定区域

```swift
import CoreLocation

let region = CLCircularRegion(
    center: CLLocationCoordinate2D(latitude: 37.3349, longitude: -122.0090),
    radius: 500,
    identifier: "apple-park"
)
RelevantContext.location(region)
```

### 要点兴趣类别（26.0+ SDKs）

指示在任何给定类别的位置附近的相关性。如果类别不受支持，则返回 `nil`。工厂在 Apple 平台 26.0+ 的 SDK 上可用，但 RelevanceKit 线索仍然仅影响 watchOS 上的智能堆栈行为。

```swift
import MapKit

if let context = RelevantContext.location(category: .beach) {
    // 小部件在人在海滩附近时始终相关
}
```

## 健身和睡眠相关性

### 健身

```swift
// 活动环未完成时相关
RelevantContext.fitness(.activityRingsIncomplete)

// 活动期间健身时相关
RelevantContext.fitness(.workoutActive)
```

应用 [权限](#permissions) 中的确切健身映射。

### 睡眠

```swift
// 睡前相关
RelevantContext.sleep(.bedtime)

// 起床时相关
RelevantContext.sleep(.wakeup)
```

应用 [权限](#permissions) 中的睡眠映射。

## 硬件相关性

```swift
// 连接耳机时相关
RelevantContext.hardware(headphones: .connected)
```

无需特殊权限。

## 组合信号

在 `WidgetRelevance` 数组中返回多个 `WidgetRelevanceAttribute` 值，以使小部件在多个不同条件下相关。

```swift
func relevance() async -> WidgetRelevance<MyIntent> {
    var attributes: [WidgetRelevanceAttribute<MyIntent>] = []

    // 早晨通勤时相关
    attributes.append(
        WidgetRelevanceAttribute(
            configuration: MyIntent(mode: .commute),
            context: .location(inferred: .commute)
        )
    )

    // 在工作场所时相关
    attributes.append(
        WidgetRelevanceAttribute(
            configuration: MyIntent(mode: .work),
            context: .location(inferred: .work)
        )
    )

    // 在计划事件周围相关
    for event in upcomingEvents {
        attributes.append(
            WidgetRelevanceAttribute(
                configuration: MyIntent(eventID: event.id),
                context: .date(event.date, kind: .scheduled)
            )
        )
    }

    return WidgetRelevance(attributes)
}
```

**顺序很重要。** 返回相关性属性按优先级排序。系统可能只使用提供的部分相关性。

## 小部件集成

### 使用 RelevanceConfiguration 的相关小部件

```swift
@available(watchOS 26, *)
struct MyRelevantWidget: Widget {
    var body: some WidgetConfiguration {
        RelevanceConfiguration(
            kind: "com.example.relevant-events",
            provider: MyRelevanceProvider()
        ) { entry in
            EventWidgetView(entry: entry)
        }
        .configurationDisplayName("Events")
        .description("当相关时显示即将到来的事件")
    }
}
```

### 与时间线小部件关联

当时间线小部件和相关小部件显示相同数据时，使用 `.associatedKind(_:)` 防止重复卡片。当它们被建议时，系统会用相关小部件卡片替换时间线小部件卡片。

```swift
RelevanceConfiguration(
    kind: "com.example.relevant-events",
    provider: MyRelevanceProvider()
) { entry in
    EventWidgetView(entry: entry)
}
.associatedKind("com.example.timeline-events")
```

### 分组

`WidgetRelevanceGroup` 控制系统如何在智能堆栈中对小部件进行分组。

```swift
// 拒绝默认的每个应用分组，以便每张卡片独立显示
WidgetRelevanceAttribute(
    configuration: intent,
    group: .ungrouped
)

// 命名组——组内一次只出现一个小部件
WidgetRelevanceAttribute(
    configuration: intent,
    group: .named("weather-alerts")
)

// 默认系统分组
WidgetRelevanceAttribute(
    configuration: intent,
    group: .automatic
)
```

### RelevantIntent（时间线提供者路径）

使用时间线提供者时，还更新 `RelevantIntentManager`，以便系统在时间线刷新之间具有相关性数据。

```swift
import AppIntents

func updateRelevantIntents() async {
    let intents = events.map { event in
        RelevantIntent(
            MyWidgetIntent(event: event),
            widgetKind: "com.example.events",
            relevance: RelevantContext.date(from: event.start, to: event.end)
        )
    }
    try? await RelevantIntentManager.shared.updateRelevantIntents(intents)
}
```

每当相关性数据发生变化时调用此方法——不仅在时间线刷新期间。

### 预览相关小部件

使用 [Preview Recipes](references/relevancekit-patterns.md#preview-recipes) 中的条目、相关性配置和完整提供者配方。在手表上启用 WidgetKit 开发者模式，测试授予和拒绝的权限，并在物理 Apple Watch 上完成；参见 [测试技巧](references/relevancekit-patterns.md#testing-tips)。

## 常见错误

- **使用 RelevanceKit API 期望 iOS 行为。** API 在所有平台上编译，但仅在 watchOS 上生效。
- **重复智能堆栈卡片。** 当为相同数据提供时间线小部件和相关小部件时，使用 `.associatedKind(_:)` 防止重复。
- **未调用 `updateRelevantIntents`。** 使用时间线提供者时，仅在 `timeline()` 内调用此方法意味着系统在刷新之间具有过时的相关性数据。每当数据变化时更新。
- **忽略 `location(category:)` 的 nil。** 此工厂返回可选值。并非所有 `MKPointOfInterestCategory` 值都受支持。

## 审查清单

- [ ] 路由：RelevanceKit 仅在 watchOS 上生效，而 WidgetKit、HealthKit、MapKit 和 CoreLocation 实现保持在兄弟作用域内。
- [ ] 信号：上下文与数据模型匹配，属性按优先级排序，并且每个线索都使用权限表中的确切设置。
- [ ] 提供者：条目、占位符、相关性、预览路径都存在；位置类别可选值和 Widget 更新授权都得到处理。
- [ ] 协调：`.associatedKind(_:)` 防止重复卡片，并且 `updateRelevantIntents` 在时间线提供者数据变化时运行。
- [ ] 测试：已启用开发者模式，并且预览涵盖了显示尺寸以及授予和拒绝的权限状态。

## 参考资料

- [references/relevancekit-patterns.md](references/relevancekit-patterns.md) -- 扩展模式、完整提供者实现、权限处理和分组策略
- [RelevanceKit 文档](https://sosumi.ai/documentation/relevancekit)
- [RelevantContext](https://sosumi.ai/documentation/relevancekit/relevantcontext)
- [提高小部件在智能堆栈中的可见性](https://sosumi.ai/documentation/widgetkit/widget-suggestions-in-smart-stacks)
- [RelevanceConfiguration](https://sosumi.ai/documentation/widgetkit/relevanceconfiguration)
- [RelevanceEntriesProvider](https://sosumi.ai/documentation/widgetkit/relevanceentriesprovider)
- [watchOS 26 的新功能（WWDC25 会话 334）](https://sosumi.ai/videos/play/wwdc2025/334/)
