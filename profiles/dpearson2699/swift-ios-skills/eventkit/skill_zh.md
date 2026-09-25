# EventKit

使用 EventKit 进行日历和提醒事项的授权、CRUD 操作、重复规则、闹钟以及系统编辑器。

## 目录

- [可用性](#可用性)
- [设置](#设置)
- [授权](#授权)
- [创建事件](#创建事件)
- [获取事件](#获取事件)
- [提醒事项](#提醒事项)
- [重复规则](#重复规则)
- [闹钟](#闹钟)
- [EventKitUI 控制器](#eventkitui-控制器)
- [观察变更](#观察变更)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 可用性

- **iOS 17+:** 使用细粒度的完整/仅写入请求方法；遗留 `requestAccess(to:)` 不再提示并抛出。系统事件编辑器可以在没有应用日历访问权限的情况下创建事件。对于 iOS 10–16，保护这些 API，使用遗留请求加上 `NSCalendarsUsageDescription` /
  `NSRemindersUsageDescription`；EventKitUI 可能还需要 `NSContactsUsageDescription`。
- **iOS 26+:** 具有类型的 `EKEventStore.EventStoreChanged` / `.changed` 消息在守卫后面可用。为早期系统保留 `EKEventStoreChanged`。

## 设置

### Info.plist 键

添加在 [授权](#授权) 中选择的访问路径的使用描述。不要仅仅为了简化设置路径而请求更广泛的访问权限。

无授权的系统编辑器路径不需要日历使用字符串。直接写入需要写入或完整访问；读取需要完整访问。提醒事项只有完整访问。

### 事件存储

创建一个 `EKEventStore` 实例并重用它。不要混合来自不同事件存储的对象。

```swift
import EventKit

let eventStore = EKEventStore()
```

## 授权

请求与功能匹配的最窄访问权限。应用 [可用性](#可用性) 中的版本请求路径。

| 键 | 访问级别 |
|---|---|
| `NSCalendarsFullAccessUsageDescription` | 读取 + 写入事件 |
| `NSCalendarsWriteOnlyAccessUsageDescription` | 直接写入事件创建 |
| `NSRemindersFullAccessUsageDescription` | 读取 + 写入提醒事项 |

### 事件的完整访问

当应用需要读取、编辑、删除或获取日历事件时，调用 `try await eventStore.requestFullAccessToEvents()`。

### 事件仅写入访问

当您的应用仅创建事件（例如，保存预订）而不需要读取现有事件时使用。

调用 `try await eventStore.requestWriteOnlyAccessToEvents()`，在直接 EventKit 写入之前，不使用 `EKEventEditViewController`。

仅写入访问可以创建事件，但不能获取日历或事件，包括应用创建的事件。使用完整访问进行后续查询、验证、修改或同步。

### 提醒事项的完整访问

在读取、创建、编辑或删除提醒事项之前，调用 `try await eventStore.requestFullAccessToReminders()`。

### 检查授权状态

在使用之前，使用 `EKEventStore.authorizationStatus(for: .event)` 或 `.reminder`。处理 `.notDetermined`，`.fullAccess`，`.writeOnly`，`.restricted`，`.denied` 和 `@unknown default`；只有 `.fullAccess` 支持事件/提醒事项读取。

## 创建事件

```swift
func createEvent(
    title: String,
    startDate: Date,
    endDate: Date,
    calendar: EKCalendar? = nil
) throws {
    let event = EKEvent(eventStore: eventStore)
    event.title = title
    event.startDate = startDate
    event.endDate = endDate
    event.calendar = calendar ?? eventStore.defaultCalendarForNewEvents

    try eventStore.save(event, span: .thisEvent)
}
```

### 设置特定日历

```swift
// 列出可写的日历
let calendars = eventStore.calendars(for: .event)
    .filter { $0.allowsContentModifications }

// 使用第一个可写的日历，或默认日历
let targetCalendar = calendars.first ?? eventStore.defaultCalendarForNewEvents
event.calendar = targetCalendar
```

### 添加结构化位置

```swift
import CoreLocation

let location = EKStructuredLocation(title: "Apple Park")
location.geoLocation = CLLocation(latitude: 37.3349, longitude: -122.0090)
event.structuredLocation = location
```

## 获取事件

在 [授权](#授权) 中的完整访问门之后，使用日期范围谓词查询事件。`events(matching:)` 方法返回在范围内展开的重复事件的实例。事件谓词限制为四年范围，并且 `events(matching:)` /
`enumerateEvents(matching:using:)` 是同步的，并且只返回已提交的事件。

```swift
func fetchEvents(from start: Date, to end: Date) -> [EKEvent] {
    let predicate = eventStore.predicateForEvents(
        withStart: start,
        end: end,
        calendars: nil  // nil = 所有日历
    )
    return eventStore.events(matching: predicate)
        .sorted { $0.startDate < $1.startDate }
}
```

### 通过标识符获取单个事件

```swift
if let event = eventStore.event(withIdentifier: savedEventID) {
    print(event.title ?? "无标题")
}
```

## 提醒事项

### 创建提醒事项

```swift
func createReminder(title: String, dueDate: Date) throws {
    let reminder = EKReminder(eventStore: eventStore)
    reminder.title = title
    reminder.calendar = eventStore.defaultCalendarForNewReminders()

    let dueDateComponents = Calendar.current.dateComponents(
        [.year, .month, .day, .hour, .minute],
        from: dueDate
    )
    reminder.dueDateComponents = dueDateComponents

    try eventStore.save(reminder, commit: true)
}
```

### 获取提醒事项

提醒事项获取是异步的，并通过完成处理程序返回。

```swift
func fetchIncompleteReminders() async -> [EKReminder] {
    let predicate = eventStore.predicateForIncompleteReminders(
        withDueDateStarting: nil,
        ending: nil,
        calendars: nil
    )

    return await withCheckedContinuation { continuation in
        eventStore.fetchReminders(matching: predicate) { reminders in
            continuation.resume(returning: reminders ?? [])
        }
    }
}
```

### 完成提醒事项

```swift
func completeReminder(_ reminder: EKReminder) throws {
    reminder.isCompleted = true
    try eventStore.save(reminder, commit: true)
}
```

## 重复规则

使用 `EKRecurrenceRule` 创建重复事件或提醒事项。

### 简单重复

```swift
// 每周一次，无限期
let weeklyRule = EKRecurrenceRule(
    recurrenceWith: .weekly,
    interval: 1,
    end: nil
)
event.addRecurrenceRule(weeklyRule)

// 每 2 周一次，10 次后结束
let biweeklyRule = EKRecurrenceRule(
    recurrenceWith: .weekly,
    interval: 2,
    end: EKRecurrenceEnd(occurrenceCount: 10)
)

// 每月一次，在特定日期结束
let monthlyRule = EKRecurrenceRule(
    recurrenceWith: .monthly,
    interval: 1,
    end: EKRecurrenceEnd(end: endDate)
)
```

### 复杂重复

```swift
// 每周一和周三
let days = [
    EKRecurrenceDayOfWeek(.monday),
    EKRecurrenceDayOfWeek(.wednesday)
]

let complexRule = EKRecurrenceRule(
    recurrenceWith: .weekly,
    interval: 1,
    daysOfTheWeek: days,
    daysOfTheMonth: nil,
    monthsOfTheYear: nil,
    weeksOfTheYear: nil,
    daysOfTheYear: nil,
    setPositions: nil,
    end: nil
)
event.addRecurrenceRule(complexRule)
```

### 编辑重复事件

在将更改保存到重复事件时，指定跨度：

```swift
// 仅更改此实例
try eventStore.save(event, span: .thisEvent)

// 更改此实例和所有后续实例
try eventStore.save(event, span: .futureEvents)
```

## 闹钟

将闹钟附加到事件或提醒事项以触发通知。

```swift
// 15 分钟前
let alarm = EKAlarm(relativeOffset: -15 * 60)
event.addAlarm(alarm)

// 在绝对日期
let absoluteAlarm = EKAlarm(absoluteDate: alertDate)
event.addAlarm(absoluteAlarm)
```

对于提醒事项地理围栏，将 `EKStructuredLocation` 和 `.enter` / `.leave` 接近性放在 `EKAlarm` 上，然后将其添加到提醒事项。有关完整的基于位置的提醒事项模式，请参阅
[参考资料/eventkit-patterns.md](references/eventkit-patterns.md)。

## EventKitUI 控制器

### EKEventEditViewController — 创建/编辑事件

显示系统事件编辑器以创建或编辑事件。

在 [可用性](#可用性) 中的无授权路径上，编辑器以进程外运行，并具有自己的日历访问权限。不要检查关闭的控制器以了解保存的内容；仅使用单独的完整访问重新获取。

```swift
import EventKitUI

class EventEditorCoordinator: NSObject, EKEventEditViewDelegate {
    let eventStore = EKEventStore()

    func presentEditor(from viewController: UIViewController) {
        let editor = EKEventEditViewController()
        editor.eventStore = eventStore
        editor.editViewDelegate = self
        viewController.present(editor, animated: true)
    }

    func eventEditViewController(
        _ controller: EKEventEditViewController,
        didCompleteWith action: EKEventEditViewAction
    ) {
        switch action {
        case .saved:
            // 事件已保存
            break
        case .canceled:
            break
        case .deleted:
            break
        @unknown default:
            break
        }
        controller.dismiss(animated: true)
    }
}
```

### EKEventViewController — 查看事件

```swift
import EventKitUI

let viewer = EKEventViewController()
viewer.event = existingEvent
viewer.allowsEditing = true
navigationController?.pushViewController(viewer, animated: true)
```

### EKCalendarChooser — 选择日历

`EKCalendarChooser` 需要写入或完整日历访问权限。在仅写入的应用中，选择器行为仅限于可写日历，并且只允许选择单个可写日历。

```swift
let chooser = EKCalendarChooser(
    selectionStyle: .multiple,
    displayStyle: .allCalendars,
    entityType: .event,
    eventStore: eventStore
)
chooser.showsDoneButton = true
chooser.showsCancelButton = true
chooser.delegate = self
present(UINavigationController(rootViewController: chooser), animated: true)
```

## 观察变更

注册 `EKEventStoreChanged` 通知，以便在事件在您的应用外部修改时（例如，由日历应用或同步）同步您的 UI。

```swift
NotificationCenter.default.addObserver(
    forName: .EKEventStoreChanged,
    object: eventStore,
    queue: .main
) { [weak self] _ in
    self?.refreshEvents()
}
```

收到此通知后始终重新获取事件。之前获取的 `EKEvent`，`EKReminder` 和 `EKCalendar` 对象可能已过时。通知在主线程上发布。

## 常见错误

### 不要：在当前系统上使用遗留的 requestAccess(to:)

```swift
// 错误：在当前系统上使用遗留请求 API
eventStore.requestAccess(to: .event) { granted, error in }

// 正确：使用细粒度的异步方法
let granted = try await eventStore.requestFullAccessToEvents()
```

仅在 [可用性](#可用性) 的兼容性回退中保留它。

### 不要：将事件保存到只读日历

```swift
// 错误：无检查 — 如果日历是只读的，将抛出
event.calendar = someCalendar
try eventStore.save(event, span: .thisEvent)

// 正确：验证日历允许修改
guard someCalendar.allowsContentModifications else {
    event.calendar = eventStore.defaultCalendarForNewEvents
    return
}
event.calendar = someCalendar
try eventStore.save(event, span: .thisEvent)
```

### 不要：创建事件时忽略时区

```swift
// 错误：对于旅行用户，事件显示在错误的时间
event.startDate = Date()
event.endDate = Date().addingTimeInterval(3600)

// 正确：为位置特定事件显式设置时区
event.timeZone = TimeZone(identifier: "America/New_York")
event.startDate = startDate
event.endDate = endDate
```

### 不要：忘记提交批量保存

```swift
// 错误：更改从未持久化
try eventStore.save(event1, span: .thisEvent, commit: false)
try eventStore.save(event2, span: .thisEvent, commit: false)
// 缺少 commit！

// 正确：批量后提交
try eventStore.save(event1, span: .thisEvent, commit: false)
try eventStore.save(event2, span: .thisEvent, commit: false)
try eventStore.commit()
```

### 不要：混合来自不同事件存储的 EKObjects

```swift
// 错误：从 storeA 获取事件，保存到 storeB
let event = storeA.event(withIdentifier: id)!
try storeB.save(event, span: .thisEvent) // 未定义行为

// 正确：在整个过程中使用相同的存储
let event = eventStore.event(withIdentifier: id)!
try eventStore.save(event, span: .thisEvent)
```

## 审查清单

- [ ] 为日历和/或提醒事项添加了正确的 `Info.plist` 使用描述键
- [ ] 授权遵循 [可用性](#可用性) 中的版本拆分
- [ ] 仅使用仅写入日历访问权限进行直接事件创建，而不是事件/日历读取
- [ ] 在获取或保存之前检查授权状态
- [ ] 在任何事件或提醒事项获取之前需要完整访问
- [ ] 跨应用重用单个 `EKEventStore` 实例
- [ ] 事件保存到可写日历（检查 `allowsContentModifications`）
- [ ] 重复事件保存指定正确的 `EKSpan` (`.thisEvent` vs `.futureEvents`)
- [ ] 批量保存验证可写日历，使用 `commit: false` 阶段，
      调用抛出 `commit()`，在失败时 `reset()` 未保存状态，丢弃
      每个失效的 `EKObject`，然后重试前重新获取或重建
- [ ] 观察 `EKEventStoreChanged` 通知以刷新过时数据
- [ ] 变更观察使用经典的通知或 [可用性](#可用性) 中的受保护的类型消息
- [ ] 为位置特定事件显式设置时区
- [ ] EKObjects 不共享到不同的事件存储实例
- [ ] EventKitUI 代表在完成回调中关闭控制器

## 参考资料

- 扩展模式（SwiftUI 包装器、谓词查询、批量操作）：[参考资料/eventkit-patterns.md](references/eventkit-patterns.md)
- [EventKit 框架](https://sosumi.ai/documentation/eventkit)
- [EKEventStore](https://sosumi.ai/documentation/eventkit/ekeventstore)
- [EKEvent](https://sosumi.ai/documentation/eventkit/ekevent)
- [EKReminder](https://sosumi.ai/documentation/eventkit/ekreminder)
- [EKRecurrenceRule](https://sosumi.ai/documentation/eventkit/ekrecurrencerule)
- [EKCalendar](https://sosumi.ai/documentation/eventkit/ekcalendar)
- [EventKit UI](https://sosumi.ai/documentation/eventkitui)
- [EKEventEditViewController](https://sosumi.ai/documentation/eventkitui/ekeventeditviewcontroller)
- [EKCalendarChooser](https://sosumi.ai/documentation/eventkitui/ekcalendarchooser)
- [访问事件存储](https://sosumi.ai/documentation/eventkit/accessing-the-event-store)
- [创建重复事件](https://sosumi.ai/documentation/eventkit/creating-a-recurring-event)
