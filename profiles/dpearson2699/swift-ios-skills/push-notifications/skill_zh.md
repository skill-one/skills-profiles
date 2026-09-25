# 推送通知

使用 `UserNotifications` 和 APNs 在 iOS/macOS 上实现、审查和调试本地和远程通知。涵盖权限流程、令牌注册、有效载荷结构、前台处理、通知操作、分组和丰富通知。目标为 iOS 26+ 和 Swift 6.3，向后兼容至 iOS 16（除非另有说明）。

保持相邻域分离：Live Activity `content-state` 有效载荷应属于 `activitykit`；PushKit/VoIP 电话推送应属于 `callkit`；App Clip 短暂通知设置应属于 `app-clips`；静默推送后的长时间运行或计划性后台工作应属于 `background-processing`。

## 目录

- [审查反馈](#审查反馈)
- [权限流程](#权限流程)
- [APNs 注册](#apns注册)
- [本地通知](#本地通知)
- [远程通知有效载荷](#远程通知有效载荷)
- [通知处理](#通知处理)
- [通知操作和类别](#通知操作和类别)
- [通知分组](#通知分组)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 审查反馈

在审查有缺陷的通知提案时，明确指出违反的契约。APNs 令牌审查必须说明令牌注册独立于警报授权，在每次 `didRegister` 回调中上传，避免本地缓存作为事实的逻辑，永远不要假设令牌长度，并将模拟器注册失败视为预期情况，同时注明 `.apns` 文件或 `simctl push` 可以模拟投递。后台推送审查必须说明仅使用 `content-available`，`apns-push-type: background`，`apns-priority: 5`，远程通知后台模式，低优先级，节流，不保证，不是每几分钟一次，以及有界定的 `didReceiveRemoteNotification` 返回正确的 `UIBackgroundFetchResult`。丰富通知审查必须说明服务扩展需要 `mutable-content: 1` 加上警报有效载荷，静默推送不会触发它们，附件是系统验证和存储的磁盘文件，密钥使用 Keychain 共享，而 App Groups 用于共享文件/UserDefaults，通信通知需要能力 + `NSUserActivityTypes` + `INInteraction` 捐赠 + `content.updating(from:)`，并且每个服务扩展路径包括附件/下载失败和 `serviceExtensionTimeWillExpire()` 必须精确调用一次内容处理程序，使用原始、最佳尝试或更新内容。

## 权限流程

在计划或显示用户可见的警报、声音或徽章之前请求通知授权。系统提示只会出现一次；后续调用将返回存储的决策。APNs 令牌注册是分开的：当应用需要设备令牌时，即使用户未授予警报授权，也调用 `registerForRemoteNotifications()`。

```swift
import UserNotifications

@MainActor
func requestNotificationPermission() async -> Bool {
    let center = UNUserNotificationCenter.current()
    do {
        let granted = try await center.requestAuthorization(
            options: [.alert, .sound, .badge]
        )
        return granted
    } catch {
        print("Authorization request failed: \(error)")
        return false
    }
}
```

### 检查当前状态

在假设权限之前始终检查状态。用户可以随时更改设置。

```swift
@MainActor
func checkNotificationStatus() async -> UNAuthorizationStatus {
    let settings = await UNUserNotificationCenter.current().notificationSettings()
    return settings.authorizationStatus
    // .notDetermined, .denied, .authorized, .provisional, .ephemeral
}
```

### 暂定通知

暂定通知会安静地投递到通知中心，不会打扰用户。用户可以选择保留或关闭它们。用于引导流程，在请求完整权限之前展示价值。

```swift
// 安静投递——不会向用户显示权限提示
try await center.requestAuthorization(options: [.alert, .sound, .badge, .provisional])
```

### 关键警报

关键警报绕过勿扰模式和静音开关。需要 Apple 提供的特殊权限（通过开发者门户申请）。仅用于健康、安全或安全场景。

```swift
// 需要 com.apple.developer.usernotifications.critical-alerts 权限
try await center.requestAuthorization(
    options: [.alert, .sound, .badge, .criticalAlert]
)
```

### 处理拒绝权限

当用户拒绝通知时，使用 `UIApplication.openSettingsURLString` 引导他们到设置。不要重复提示或烦扰。

## APNs 注册

使用 `UIApplicationDelegateAdaptor` 在 SwiftUI 应用中接收设备令牌。AppDelegate 回调是接收 APNs 令牌的唯一方式。

```swift
@main
struct MyApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

class AppDelegate: NSObject, UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil
    ) -> Bool {
        UNUserNotificationCenter.current().delegate = NotificationDelegate.shared
        return true
    }

    func application(
        _ application: UIApplication,
        didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
    ) {
        let token = deviceToken.map { String(format: "%02x", $0) }.joined()
        print("APNs token: \(token)")
        // 将令牌发送到您的服务器
        Task { await TokenService.shared.upload(token: token) }
    }

    func application(
        _ application: UIApplication,
        didFailToRegisterForRemoteNotificationsWithError error: Error
    ) {
        print("APNs registration failed: \(error.localizedDescription)")
        // 模拟器可以模拟推送，但它不会注册到 APNs。
    }
}
```

### 注册顺序

在启动时配置代理和类别。然后根据上下文请求用户通知授权以显示可见通知，并在应用需要设备令牌时注册到 APNs。不要以 `.authorized` 为条件锁定 APNs 注册；如果没有警报授权，远程通知将安静地投递。

```swift
@MainActor
func configureNotifications() async {
    let center = UNUserNotificationCenter.current()
    let settings = await center.notificationSettings()

    if settings.authorizationStatus == .notDetermined {
        _ = await requestNotificationPermission()
    }

    // 需要 APNs 令牌投递和静默远程通知。
    UIApplication.shared.registerForRemoteNotifications()
}
```

### 令牌处理

设备令牌会变化。每次 `didRegisterForRemoteNotificationsWithDeviceToken` 触发时都重新发送令牌到您的服务器，而不仅仅是第一次。不要将令牌本地持久化作为事实来源或假设固定的令牌长度。

## 本地通知

直接从设备安排通知，无需服务器。适用于提醒、计时器和基于位置的通知。

### 创建内容

```swift
let content = UNMutableNotificationContent()
content.title = "锻炼提醒"
content.subtitle = "该活动了"
content.body = "您有一个在 15 分钟后安排的锻炼。"
content.sound = .default
content.badge = NSNumber(value: 1)
content.userInfo = ["workoutId": "abc123"]
content.threadIdentifier = "workouts"  // 在通知中心分组
```

### 触发类型

```swift
// 在时间间隔后触发（重复的最小间隔为 60 秒）
let timeTrigger = UNTimeIntervalNotificationTrigger(timeInterval: 300, repeats: false)

// 在特定日期/时间触发
var dateComponents = DateComponents()
dateComponents.hour = 8
dateComponents.minute = 30
let calendarTrigger = UNCalendarNotificationTrigger(
    dateMatching: dateComponents, repeats: true  // 每天早上 8:30
)

// 进入地理区域时触发
let region = CLCircularRegion(
    center: CLLocationCoordinate2D(latitude: 37.33, longitude: -122.01),
    radius: 100,
    identifier: "gym"
)
region.notifyOnEntry = true
region.notifyOnExit = false
let locationTrigger = UNLocationNotificationTrigger(region: region, repeats: false)
// 至少需要 "当使用中" 的位置权限
```

### 安排和管理

```swift
let request = UNNotificationRequest(
    identifier: "workout-reminder-abc123",
    content: content,
    trigger: timeTrigger
)

let center = UNUserNotificationCenter.current()
try await center.add(request)

// 移除特定待处理通知
center.removePendingNotificationRequests(withIdentifiers: ["workout-reminder-abc123"])

// 移除所有待处理
center.removeAllPendingNotificationRequests()

// 从通知中心移除已投递通知
center.removeDeliveredNotifications(withIdentifiers: ["workout-reminder-abc123"])
center.removeAllDeliveredNotifications()

// 列出所有待处理请求
let pending = await center.pendingNotificationRequests()
```

## 远程通知有效载荷

### 标准APNs有效载荷

```json
{
    "aps": {
        "alert": {
            "title": "新消息",
            "subtitle": "来自 Alice",
            "body": "嘿，你有空一起吃午饭吗？"
        },
        "badge": 3,
        "sound": "default",
        "thread-id": "chat-alice",
        "category": "MESSAGE_CATEGORY"
    },
    "messageId": "msg-789",
    "senderId": "user-alice"
}
```

### 静默/后台推送

设置 `content-available: 1`，不包含警报、声音或徽章。需要 "后台模式 > 远程通知" 加上 APNs 标头 `apns-push-type: background` 和 `apns-priority: 5`。系统将这些视为低优先级、节流且不保证；不要每几分钟发送一次或依赖它们以保持即时新鲜。在 `didReceiveRemoteNotification` 中进行有界定的工作并迅速返回 `UIBackgroundFetchResult`，在后台执行窗口内。

```json
{
    "aps": {
        "content-available": 1
    },
    "updateType": "new-data"
}
```

在 AppDelegate 中处理：
```swift
func application(
    _ application: UIApplication,
    didReceiveRemoteNotification userInfo: [AnyHashable: Any]
) async -> UIBackgroundFetchResult {
    guard let updateType = userInfo["updateType"] as? String else {
        return .noData
    }
    do {
        try await DataSyncService.shared.sync(trigger: updateType)
        return .newData
    } catch {
        return .failed
    }
}
```

### 可变内容

设置 `mutable-content: 1` 加上警报字典，允许通知服务扩展在显示之前修改远程通知。静默推送不会触发服务扩展。使用服务扩展进行有界定的工作，例如下载支持的磁盘附件、解密显示文本或配置通信通知；在成功、失败和超时路径上调用内容处理程序。对于通信通知，启用能力，添加 `NSUserActivityTypes`，捐赠 `INInteraction`，然后调用 `content.updating(from:)`。

```json
{
    "aps": {
        "alert": { "title": "照片", "body": "Alice 发送了一张照片" },
        "mutable-content": 1
    },
    "imageUrl": "https://example.com/photo.jpg"
}
```

### 本地化通知

使用本地化键，以便通知显示在用户的语言中：

```json
{
    "aps": {
        "alert": {
            "title-loc-key": "NEW_MESSAGE_TITLE",
            "loc-key": "NEW_MESSAGE_BODY",
            "loc-args": ["Alice"]
        }
    }
}
```

## 通知处理

### UNUserNotificationCenterDelegate

实现代理以控制前台显示并处理用户点击。尽可能早地设置代理——在 `application(_:didFinishLaunchingWithOptions:)` 或 `App.init` 中。

```swift
@MainActor
final class NotificationDelegate: NSObject, UNUserNotificationCenterDelegate {
    static let shared = NotificationDelegate()

    // 当应用在前台时通知到达时调用
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification
    ) async -> UNNotificationPresentationOptions {
        // 返回要显示的呈现元素
        // 没有这个，前台通知将被安静地抑制
        return [.banner, .sound, .badge]
    }

    // 当用户点击通知时调用
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse
    ) async {
        let userInfo = response.notification.request.content.userInfo
        let actionIdentifier = response.actionIdentifier

        switch actionIdentifier {
        case UNNotificationDefaultActionIdentifier:
            // 用户点击了通知正文
            await handleNotificationTap(userInfo: userInfo)
        case UNNotificationDismissActionIdentifier:
            // 用户关闭了通知
            break
        default:
            // 点击了自定义操作按钮
            await handleCustomAction(actionIdentifier, userInfo: userInfo)
        }
    }
}
```

### 从通知中跳转链接

使用共享的 `@Observable` 路由器将通知点击路由到正确的屏幕。代理写入待处理的目的地；SwiftUI 视图观察并消费它。

```swift
@Observable @MainActor
final class DeepLinkRouter {
    static let shared = DeepLinkRouter()

    var pendingDestination: AppDestination?
}

// 在 NotificationDelegate 中：
func handleNotificationTap(userInfo: [AnyHashable: Any]) async {
    guard let id = userInfo["messageId"] as? String else { return }
    DeepLinkRouter.shared.pendingDestination = .chat(id: id)
}

// 在 SwiftUI 中——观察并消费：
.onChange(of: router.pendingDestination) { _, destination in
    if let destination {
        path.append(destination)
        router.pendingDestination = nil
    }
}
```

有关完整的跳转链接处理程序（包括标签切换），请参阅 [references/notification-patterns.md](references/notification-patterns.md)。

## 通知操作和类别

定义作为通知上按钮出现的交互式操作。在启动时注册类别。

### 定义类别和操作

```swift
func registerNotificationCategories() {
    let replyAction = UNTextInputNotificationAction(
        identifier: "REPLY_ACTION",
        title: "回复",
        options: [],
        textInputButtonTitle: "发送",
        textInputPlaceholder: "输入回复..."
    )

    let likeAction = UNNotificationAction(
        identifier: "LIKE_ACTION",
        title: "喜欢",
        options: []
    )

    let deleteAction = UNNotificationAction(
        identifier: "DELETE_ACTION",
        title: "删除",
        options: [.destructive, .authenticationRequired]
    )

    let messageCategory = UNNotificationCategory(
        identifier: "MESSAGE_CATEGORY",
        actions: [replyAction, likeAction, deleteAction],
        intentIdentifiers: [],
        options: [.customDismissAction]  // 关闭时也触发 didReceive
    )

    UNUserNotificationCenter.current().setNotificationCategories([messageCategory])
}
```

### 处理操作响应

```swift
func handleCustomAction(_ identifier: String, userInfo: [AnyHashable: Any]) async {
    switch identifier {
    case "REPLY_ACTION":
        // 响应是 UNTextInputNotificationResponse，用于文本输入操作
        break
    case "LIKE_ACTION":
        guard let messageId = userInfo["messageId"] as? String else { return }
        await MessageService.shared.likeMessage(id: messageId)
    case "DELETE_ACTION":
        guard let messageId = userInfo["messageId"] as? String else { return }
        await MessageService.shared.deleteMessage(id: messageId)
    default:
        break
    }
}
```

操作选项：
- `.authenticationRequired` -- 设备必须解锁才能执行操作
- `.destructive` -- 以红色显示；用于删除/移除操作
- `.foreground` -- 点击时启动应用至前台

## 通知分组

使用 `threadIdentifier`（或 APNs 有效载荷中的 `thread-id`）将相关通知分组。每个唯一的线程在通知中心成为单独的组。

```swift
content.threadIdentifier = "chat-alice"  // Alice 的所有消息分组在一起
content.summaryArgument = "Alice"
content.summaryArgumentCount = 3         // "Alice 还有 3 条更多通知"
```

在类别中自定义摘要格式字符串：

```swift
let category = UNNotificationCategory(
    identifier: "MESSAGE_CATEGORY",
    actions: [replyAction],
    intentIdentifiers: [],
    categorySummaryFormat: "%u more messages from %@",
    options: []
)
```

## 常见错误

**不要**：当应用需要静默推送或服务器令牌绑定时，以警报授权状态锁定 APNs 令牌注册。
**要**：请求警报/声音/徽章的授权，并在需要设备令牌时注册到 APNs。
**不要**：使用 `String(data: deviceToken, encoding: .utf8)` 转换设备令牌。
**要**：使用十六进制：`deviceToken.map { String(format: "%02x", $0) }.joined()`。
**不要**：承诺每几分钟一次的静默刷新或即时后台投递。
**要**：说明后台推送是低优先级、节流、不保证，实际上每小时限制几个，并且需要有界定的 `didReceiveRemoteNotification` 工作返回正确的 `UIBackgroundFetchResult`。
**不要**：期望静默推送运行通知服务扩展，或未调用其内容处理程序的扩展。
**要**：使用 `mutable-content: 1` 加上警报有效载荷，支持的磁盘附件由系统验证和存储，密钥使用 Keychain 共享，而 App Groups 用于共享文件/UserDefaults，通信通知需要能力 + `NSUserActivityTypes` + `INInteraction` 捐赠 + `content.updating(from:)`，并在每个成功、失败和超时路径上使用原始或最佳尝试内容。
**不要**：忘记前台处理。没有 `willPresent`，通知将被安静地抑制。
**要**：实现 `willPresent` 并返回 `.banner`，`.sound`，`.badge`。
**不要**：设置代理太晚或未使用 AppDelegate adaptors 从 SwiftUI 视图注册。
**要**：在 `App.init` 中设置代理；使用 `UIApplicationDelegateAdaptor` 进行 APNs。
**不要**：仅在令牌“更改”时上传 APNs 令牌或假设固定的令牌长度。**要**：在每次 `didRegister` 回调时上传，并将令牌视为十六进制转换的不可见数据。
**不要**：将 Live Activity、VoIP 或 App Clip 特定的通知规则放在这里。**要**：将它们路由到 `activitykit`，`callkit` 和 `app-clips`。

## 审查清单

- [ ] 在可见警报/声音/徽章之前请求授权；处理拒绝情况（设置链接）
- [ ] APNs 注册未因警报授权状态错误地阻止
- [ ] 设备令牌转换为十六进制，每次回调时上传，并且不将其视为本地缓存或固定长度的常量
- [ ] 在 `App.init` 或 `application(_:didFinishLaunching:)` 中设置 `UNUserNotificationCenterDelegate`
- [ ] 实现 `willPresent`（前台）和 `didReceive`（点击）
- [ ] 如果需要交互式通知，则在启动时注册类别/操作
- [ ] 静默推送使用 `content-available: 1`，无警报/声音/徽章，`apns-push-type: background`，`apns-priority: 5`，后台模式 > 远程通知，节流注意事项，以及正确的 `UIBackgroundFetchResult`

## 参考资料
- [references/notification-patterns.md](references/notification-patterns.md) — AppDelegate 设置、APNs 回调、深度链接路由器、静默推送、调试
- [references/rich-notifications.md](references/rich-notifications.md) — 服务扩展、内容扩展、附件、通信通知
- Apple 文档：[APNs 注册](https://sosumi.ai/documentation/usernotifications/registering-your-app-with-apns)，[权限](https://sosumi.ai/documentation/usernotifications/asking-permission-to-use-notifications)，[有效载荷](https://sosumi.ai/documentation/usernotifications/generating-a-remote-notification)，[后台推送](https://sosumi.ai/documentation/usernotifications/pushing-background-updates-to-your-app)
