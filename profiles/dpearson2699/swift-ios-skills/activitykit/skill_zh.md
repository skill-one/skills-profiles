# ActivityKit

ActivityKit 拥有在锁屏和动态岛（Dynamic Island）上显示的实时、可一瞥的 Live Activities。普通的日历小部件属于 `widgetkit`，通用的 APNs 设置属于 `push-notifications`；ActivityKit 拥有 Live Activity 的生命周期和有效载荷契约。`aps.content-state` 必须解码为精确的 `ActivityAttributes.ContentState` 结构，包括任何协调的自定义日期/范围编码。现代 `ActivityContent` 生命周期示例需要 iOS 16.2+，除非另有说明。

有关推送有效载荷格式、并发活动、状态观察和测试的完整代码模式，请参阅 [references/activitykit-patterns.md](references/activitykit-patterns.md)。

## 内容

- [工作流](#workflow)
- [ActivityAttributes 定义](#activityattributes-definition)
- [Activity 生命周期](#activity-lifecycle)
- [锁屏展示](#lock-screen-presentation)
- [动态岛](#dynamic-island)
- [推送更新](#push-to-update)
- [近期新增](#recent-additions)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 工作流

### 1. 创建新的 Live Activity

1. 验证主机应用能力，并确保 `NSSupportsLiveActivities = YES`。
2. 定义 `ActivityAttributes.ContentState`；编码和解码一个与服务器有效载荷契约匹配的代表性测试用例。
3. 创建 `ActivityConfiguration` 并预览锁屏和动态岛状态，包括过时和最终内容。
4. 检查 `ActivityAuthorizationInfo.areActivitiesEnabled`，然后请求并观察活动生命周期。
5. 执行本地更新和每个最终结束路径。
6. 对于远程更新，在向服务器注册旋转更新或推送启动令牌之前，验证完整的参考有效载荷。

### 2. 审查现有的 Live Activity 代码

在本文档的末尾运行审查清单。

## ActivityAttributes 定义

定义静态数据（在活动生命周期中不可变）和动态 `ContentState`（随每次更新而变化）。保持 `ContentState` 小，因为整个结构在每次更新和推送有效载荷时都会序列化。

```swift
import ActivityKit

struct DeliveryAttributes: ActivityAttributes {
    // 静态 -- 在活动创建时设置一次，永不改变
    var orderNumber: Int
    var restaurantName: String

    // 动态 -- 在活动生命周期中更新
    struct ContentState: Codable, Hashable {
        var driverName: String
        var estimatedDeliveryTime: ClosedRange<Date>
        var currentStep: DeliveryStep
    }
}

enum DeliveryStep: String, Codable, Hashable, CaseIterable {
    case confirmed, preparing, pickedUp, delivering, delivered

    var icon: String {
        switch self {
        case .confirmed: "checkmark.circle"
        case .preparing: "frying.pan"
        case .pickedUp: "bag.fill"
        case .delivering: "box.truck.fill"
        case .delivered: "house.fill"
        }
    }
}
```

### 过期日期

在 `ActivityContent` 上设置 `staleDate`，以告诉系统内容何时过时。系统在该日期后将 `context.isStale` 设置为 `true`；在您的视图中显示回退 UI（例如，“正在更新...”）。

```swift
let content = ActivityContent(
    state: state,
    staleDate: Date().addingTimeInterval(300), // 5分钟后过期
    relevanceScore: 75
)
```

## Activity 生命周期

### 启动

使用 `Activity.request` 创建和显示 Live Activity。将 `.token` 作为 `pushType` 传递以通过 APNs 启用远程更新。此处显示的 `ActivityContent` 请求需要 iOS 16.2+。

```swift
let attributes = DeliveryAttributes(orderNumber: 42, restaurantName: "Pizza Place")
let state = DeliveryAttributes.ContentState(
    driverName: "Alex",
    estimatedDeliveryTime: Date()...Date().addingTimeInterval(1800),
    currentStep: .preparing
)
let content = ActivityContent(state: state, staleDate: nil, relevanceScore: 75)

do {
    let activity = try Activity.request(
        attributes: attributes,
        content: content,
        pushType: .token
    )
    print("启动活动: \(activity.id)")
} catch {
    print("启动活动失败: \(error)")
}
```

### 更新

从应用中更新动态内容状态。使用 `AlertConfiguration` 在更新时触发可见横幅和声音。

```swift
let updatedState = DeliveryAttributes.ContentState(
    driverName: "Alex",
    estimatedDeliveryTime: Date()...Date().addingTimeInterval(600),
    currentStep: .delivering
)
let updatedContent = ActivityContent(
    state: updatedState,
    staleDate: Date().addingTimeInterval(300),
    relevanceScore: 90
)

// 静默更新
await activity.update(updatedContent)

// 带有警报的更新
await activity.update(updatedContent, alertConfiguration: AlertConfiguration(
    title: "订单更新",
    body: "您的司机就在附近！",
    sound: .default
))
```

### 结束

在跟踪事件完成时结束活动。选择退出策略以控制已结束活动在锁屏上停留的时间。

```swift
let finalState = DeliveryAttributes.ContentState(
    driverName: "Alex",
    estimatedDeliveryTime: Date()...Date(),
    currentStep: .delivered
)
let finalContent = ActivityContent(state: finalState, staleDate: nil, relevanceScore: 0)

// 系统决定移除时间（最多4小时）
await activity.end(finalContent, dismissalPolicy: .default)

// 立即移除
await activity.end(finalContent, dismissalPolicy: .immediate)

// 在特定时间后移除（最多从现在开始4小时）
await activity.end(finalContent, dismissalPolicy: .after(Date().addingTimeInterval(3600)))
```

始终在所有终端代码路径上结束活动——成功、用户/应用取消、注销/会话停止、不可恢复的应用错误和终端服务器故障。如果服务器表示跟踪事件无法继续或准确表示，请应用或发送最终终端状态并结束活动，而不是留下过时的进度可见。在审查持续时间声明时，要区分活动生命周期（最多8小时，除非应用或用户提前结束）、系统结束的锁屏存在（最多4小时额外时间，总共12小时）和应用结束的 `.default` 退出停留（结束后的最多4小时）。

## 锁屏展示

锁屏是主要的 Live Activity 显示表面。所有 iOS 16.1+ 设备都在这里显示 Live Activities。首先设计此布局，然后在可用的情况下适应动态岛。

```swift
struct DeliveryActivityWidget: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: DeliveryAttributes.self) { context in
            VStack(alignment: .leading) {
                Text(context.attributes.restaurantName).font(.headline)

                if context.isStale {
                    Label("正在更新...", systemImage: "arrow.trianglehead.2.clockwise")
                        .foregroundStyle(.secondary)
                } else {
                    Text(timerInterval: context.state.estimatedDeliveryTime, countsDown: true)
                        .monospacedDigit()
                }
            }
            .padding()
        } dynamicIsland: { context in
            DynamicIsland {
                DynamicIslandExpandedRegion(.center) {
                    Text(context.attributes.restaurantName).font(.headline)
                }
                DynamicIslandExpandedRegion(.trailing) {
                    Text(timerInterval: context.state.estimatedDeliveryTime, countsDown: true)
                }
            } compactLeading: {
                Image(systemName: "box.truck.fill")
            } compactTrailing: {
                Text(timerInterval: context.state.estimatedDeliveryTime, countsDown: true)
            } minimal: {
                Image(systemName: "box.truck.fill")
            }
        }
    }
}
```

### 补充活动系列

锁屏展示的垂直空间有限。避免高度超过大约 160 点的布局。在 iOS 18+ 上，当您提供超出默认值的自适应布局时，使用 `supplementalActivityFamilies`：`.medium` 用于 iOS/macOS Live Activity 尺寸，`.small` 用于 watchOS Live Activity 尺寸。

```swift
ActivityConfiguration(for: DeliveryAttributes.self) { context in
    // 锁屏内容
} dynamicIsland: { context in
    // 动态岛
}
.supplementalActivityFamilies([.medium, .small])
```

## 动态岛

动态岛展示仅在包含动态岛的设备上出现。设计所有三种模式，但由于并非所有设备都有动态岛，因此将锁屏视为主要表面。

### 紧凑型（左侧 + 右侧）

当单个 Live Activity 占用动态岛紧凑空间时使用。空间极其有限——仅显示最关键的信息。

| 区域 | 用途 |
|---|---|
| `compactLeading` | 图标或微小的标签，用于识别活动 |
| `compactTrailing` | 一个关键值（计时器、分数、状态） |

### 最小型

当多个 Live Activity 竞争空间时显示。只有一个活动获得最小槽位。显示单个图标或符号。

### 扩展区域

当用户长按动态岛时显示。

| 区域 | 位置 |
|---|---|
| `.leading` | TrueDepth 相机左侧；向下包裹 |
| `.trailing` | TrueDepth 相机右侧；向下包裹 |
| `.center` | 相机正下方 |
| `.bottom` | 所有其他区域下方 |

### 关键线色调

对动态岛边框应用微妙的色调：

```swift
DynamicIsland { /* expanded */ }
    compactLeading: { /* ... */ }
    compactTrailing: { /* ... */ }
    minimal: { /* ... */ }
    .keylineTint(.blue)
```

## 推送更新

推送更新通过 APNs 发送 Live Activity 更新，比从应用轮询更高效，并且在应用挂起时也能工作，但受 APNs 交付、优先级、预算和速率限制的影响。

### 设置

启动活动时将 `.token` 作为 `pushType` 传递，然后将每个活动的更新令牌转发到您的服务器。更新令牌可以旋转，因此观察 `activity.pushTokenUpdates` 并重新注册每个发出的令牌：

```swift
let activity = try Activity.request(
    attributes: attributes,
    content: content,
    pushType: .token
)

// 观察令牌变化——令牌可以旋转
Task {
    for await token in activity.pushTokenUpdates {
        let tokenString = token.map { String(format: "%02x", $0) }.joined()
        try await ServerAPI.shared.registerActivityToken(
            tokenString, activityID: activity.id
        )
    }
}
```

### APNs 有效载荷格式

向 APNs 发送 HTTP/2 POST 请求，包含以下标头和 JSON 正文：

**必需的设备令牌 HTTP 标头:**
- `apns-push-type: liveactivity`
- `apns-topic: <bundle-id>.push-type.liveactivity`
- `apns-priority: 5`（低优先级）或 `10`（立即，计入预算）

`aps.alert` 有效载荷控制可见警报/横幅/声音行为；仅优先级本身不会创建警报。

将 `timestamp`、`event` 和完整的 `content-state` 放在 `aps` 中。根据 [Push-to-Update 有效载荷格式](references/activitykit-patterns.md#push-to-update-server-payload-format) 中的完整示例验证更新、结束和推送启动正文，包括精确的 `Codable` 日期/范围表示。

### 推送启动

在没有应用运行的情况下远程启动 Live Activity（iOS 17.2+）。推送启动令牌是 ActivityKit 特有的令牌，来自 `Activity<Attributes>.pushToStartTokenUpdates`；它们与普通的 App/设备 APNs 令牌和每个活动更新令牌不同：

```swift
Task {
    for await token in Activity<DeliveryAttributes>.pushToStartTokenUpdates {
        let tokenString = token.map { String(format: "%02x", $0) }.joined()
        try await ServerAPI.shared.registerPushToStartToken(tokenString)
    }
}
```

### 频繁推送更新

在 Info.plist 中添加 `NSSupportsLiveActivitiesFrequentUpdates = YES` 以增加系统管理的推送更新预算。当节奏很重要时，检查 `ActivityAuthorizationInfo.frequentPushesEnabled` 并观察 `frequentPushEnablementUpdates`；Apple 不保证固定的更新速率。

## 近期新增

### 计划的 Live Activity（iOS 26+）

计划 Live Activity 在未来时间启动。系统自动启动活动，无需应用在前台。用于具有已知启动时间的事件（体育比赛、航班、计划配送）。

```swift
let scheduledDate = Calendar.current.date(
    from: DateComponents(year: 2026, month: 3, day: 15, hour: 19, minute: 0)
)!

let activity = try Activity.request(
    attributes: attributes,
    content: content,
    pushType: .token,
    style: .standard,
    alertConfiguration: AlertConfiguration(
        title: "比赛即将开始",
        body: "实时比分已准备好。",
        sound: .default
    ),
    start: scheduledDate
)
```

### ActivityStyle（iOS 18+ 请求参数）

使用 iOS 18+ 的 `style:` 请求参数选择持久行为。使用 `.standard` 用于持久 Live Activity，如配送、乘车、体育比分、计时器和航班/状态板。仅当您需要短命的扩展动态岛展示时使用 `.transient`；当用户锁定设备、折叠或缩小扩展展示、离开应用或执行其他工作（在动态岛之外）时，它可以自动结束。

```swift
let activity = try Activity.request(
    attributes: attributes,
    content: content,
    pushType: .token,
    style: .standard
)
```

### 配对的 Mac & CarPlay（iOS 26+）

Live Activity 可以出现在配对的 Mac 和 CarPlay 主屏幕上。不需要额外的 ActivityKit API，但请验证紧凑布局；Live Activity 中的按钮和开关在 CarPlay 中不会执行操作。

### 基于通道的推送（iOS 18+）

使用 APNs 创建的通道 ID 同时向许多 Live Activity 广播更新。在 Xcode 外启用广播功能，在服务器上创建通道，然后使用 `.channel(channelID)` 订阅。通道推送更新或结束 Live Activity；它们不会启动它们。使用 `apns-channel-id` 和过期时间进行通道推送，而不是上面示例中的设备令牌 `apns-topic`。

```swift
let activity = try Activity.request(
    attributes: attributes, content: content,
    pushType: .channel(channelIDFromServer)
)
```

## 常见错误

**不要**在紧凑展示中放置过多内容——它非常小。
**要**在紧凑的左侧/右侧展示中仅显示最关键的信息（图标 + 一个值）。

**不要**从应用中过于频繁地更新 Live Activity（耗电）。
**要**使用推送更新进行服务器驱动的更新。将应用侧更新限制为用户操作。

**不要**在事件达到任何终端状态时忘记结束活动。
**要**在成功、取消、注销、不可恢复的错误和终端服务器故障时结束活动。泄漏的活动会让用户感到沮丧。

**不要**假设每个设备都有动态岛。
**要**将锁屏设计为首要表面；动态岛是补充的。

**不要**在 ActivityAttributes 中存储敏感信息（在锁屏上可见）。
**要**将敏感数据保存在应用中，并仅显示安全显示的摘要。

**不要**忘记处理过期日期。
**要**在视图中检查 `context.isStale` 并显示回退 UI（“正在更新...”或类似）。

**不要**忽略推送令牌旋转。令牌可以随时更改。
**要**使用 `activity.pushTokenUpdates` 异步序列并在每次发射时重新注册。

**不要**忘记 `NSSupportsLiveActivities` Info.plist 键。
**要**在主机应用的 Info.plist 中添加 `NSSupportsLiveActivities = YES`（不是扩展）。

**不要**使用基于 `contentState` 的过时 API 进行请求/更新/结束。
**要**使用 `ActivityContent` 进行所有生命周期调用。

**不要**直接从 Live Activity 视图中获取网络数据或位置。
**要**在应用或服务器中预先计算显示值，并通过 ActivityKit 更新或推送传递它们。

## 审查清单

- [ ] `ActivityAttributes` 定义了静态属性和 `ContentState`
- [ ] 主机应用 Info.plist 中的 `NSSupportsLiveActivities = YES`
- [ ] 活动使用 `ActivityContent`（不是过时的 contentState API）
- [ ] 活动在所有终端路径上结束（成功、错误、取消、注销、终端服务器故障）
- [ ] ActivityKit 生命周期和锁屏/动态岛 Live Activity 表面与普通的 Home Screen/时间线小部件工作分离
- [ ] 锁屏布局（主要 Live Activity 表面）处理 `context.isStale`
- [ ] 动态岛紧凑型、扩展型和最小型实现，并带有锁屏回退
- [ ] 推送更新令牌通过 `activity.pushTokenUpdates` 转发到服务器
- [ ] 推送启动令牌通过 `Activity<Attributes>.pushToStartTokenUpdates` 收集
- [ ] 推送启动有效载荷包括必需的 `alert`
- [ ] `content-state` JSON 与实际的 `ContentState` `Codable` 形状匹配，包括协调的日期/范围编码
- [ ] 审查区分 8 小时活动生命周期、12 小时系统结束的锁屏存在和 4 小时应用结束的 `.default` 停留
- [ ] 在启动前检查 `ActivityAuthorizationInfo`
- [ ] 在假设高节奏推送前检查 `frequentPushesEnabled`
- [ ] 内容状态保持小（每次更新时序列化）
- [ ] iOS 18+ 的可用性保护 `style:`, `.channel` 和补充系列
- [ ] iOS 18+ 的 `style:` 选择是合理的：`.standard` 用于持久 Live Activity，`.transient` 仅用于短命的扩展动态岛展示
- [ ] ActivityKit 推送优先级和 `aps.alert` 行为分别处理
- [ ] Live Activity 视图避免直接网络/位置工作
- [ ] 在设备上测试推送交付和动态岛行为

## 参考资料

- 请参阅 [references/activitykit-patterns.md](references/activitykit-patterns.md) 获取模式和代码示例
