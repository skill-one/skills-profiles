# AlarmKit

可以安排醒目的闹钟和倒计时计时器，当闹钟响起时，它们会显示在锁屏、动态岛、StandBy 和配对的 Apple Watch 上。AlarmKit 需要 iOS 26+ / iPadOS 26+。闹钟可以打破专注模式和静音模式。

AlarmKit 使用 ActivityKit 数据模型为其 Live Activity，但触发警报是系统管理的闹钟 UI，而不是通用的自定义通知 UI 界面。自定义 UI 仅属于由 Widget Extension 渲染的倒计时和暂停的 Live Activity 状态，这些状态使用与安排时相同的 `AlarmAttributes<Metadata>` 和 `AlarmPresentationState`。

有关包括授权、安排、倒计时计时器、静音处理和 Widget 设置的完整代码模式，请参阅 [references/alarmkit-patterns.md](references/alarmkit-patterns.md)。

```swift
import AlarmKit
```

## 目录

- [工作流程](#workflow)
- [授权](#authorization)
- [闹钟与计时器的选择](#alarm-vs-timer-decision)
- [安排闹钟](#scheduling-alarms)
- [倒计时计时器](#countdown-timers)
- [闹钟状态](#alarm-states)
- [AlarmAttributes 和 AlarmPresentation](#alarmattributes-and-alarmpresentation)
- [AlarmButton](#alarmbutton)
- [Live Activity 集成](#live-activity-integration)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 工作流程

### 1. 创建新的闹钟或计时器

1. 在 Info.plist 中添加 `NSAlarmKitUsageDescription`，并使用用户可见的字符串。
2. 当应用可以解释其价值时，使用 `AlarmManager.shared.requestAuthorization()` 请求授权，或处理首次安排的系统提示。
3. 如果授权是 `.denied` 或不是 `.authorized`，则显示恢复 UI 而不是安排。
4. 配置 `AlarmPresentation`（警报、倒计时、暂停状态）。
5. 创建 `AlarmAttributes`，包含呈现、可选元数据和着色颜色。
6. 构建 `AlarmManager.AlarmConfiguration` (.alarm 或 .timer)。
7. 使用 `AlarmManager.shared.schedule(id:configuration:)` 安排。
8. 观察 `alarmManager.alarmUpdates` 并确认安排的 ID 达到预期状态。
9. 如果使用倒计时，添加一个 Widget Extension 目标，并使用 `ActivityConfiguration`，其类型与相同的 `AlarmAttributes<Metadata>`。

### 2. 审查现有闹钟代码

在本文档末尾运行审查清单。

## 授权

AlarmKit 需要用户授权。当应用可以解释其价值时，尽早请求授权，或者在首次安排时让 AlarmKit 自动提示。如果授权在明确提示或自动提示后未获授予，则不会安排闹钟，也不会提醒。

```swift
let manager = AlarmKit.shared

// 明确请求授权
let state = try await manager.requestAuthorization()
guard state == .authorized else { return }

// 同步检查当前状态
let current = manager.authorizationState // .authorized, .denied, .notDetermined

// 观察授权变化
for await state in manager.authorizationUpdates {
    switch state {
    case .authorized: print("闹钟已启用")
    case .denied:     print("闹钟已禁用")
    case .notDetermined: break
    @unknown default: break
    }
}
```

## 闹钟与计时器的选择

| 功能 | 闹钟 (`.alarm`) | 计时器 (`.timer`) |
|---|---|---|
| 触发时间 | 特定时间（安排） | 经过一段时间后触发 |
| 倒计时 UI | 可选 | 总是显示 |
| 重复 | 是（每周几天） | 否 |
| 用例 | 唤醒、安排提醒 | 烹饪、锻炼间隔 |

当在时钟时间触发时，使用 `.alarm(schedule:...)`。当在现在之后经过一段时间触发时，使用 `.timer(duration:...)`。

## 安排闹钟

### Alarm.Schedule

使用 `.fixed(date)` 用于一次性绝对日期，或使用 `.relative` 用于本地时钟时间，并带有 `.never` 或 `.weekly` 重复。加载 [重复闹钟模式](references/alarmkit-patterns.md#recurring-alarm-patterns) 以获取每日、工作日、周末和固定日期变体。

### 安排和配置

```swift
let id = UUID()

let alert = AlarmPresentation.Alert(
    title: "起床",
    secondaryButton: AlarmButton(
        text: "静音", textColor: .white, systemImageName: "bell.slash"
    ),
    secondaryButtonBehavior: .countdown
)
let presentation = AlarmPresentation(alert: alert)
struct EmptyAlarmMetadata: AlarmMetadata {}
let attributes = AlarmAttributes<EmptyAlarmMetadata>(
    presentation: presentation,
    metadata: nil,
    tintColor: .indigo
)

let snooze = Alarm.CountdownDuration(preAlert: nil, postAlert: 300)
let configuration = AlarmManager.AlarmConfiguration(
    countdownDuration: snooze,
    schedule: .relative(.init(
        time: .init(hour: 7, minute: 0),
        repeats: .never
    )),
    attributes: attributes,
    sound: .default
)

let alarm = try await AlarmManager.shared.schedule(
    id: id,
    configuration: configuration
)
```

对于需要授权的函数和带有元数据的变体，加载 [完整的闹钟安排流程](references/alarmkit-patterns.md#complete-alarm-scheduling-flow)。

`stopIntent` 和 `secondaryIntent` 默认为 `nil`。省略 `stopIntent` 以使用 AlarmKit 的标准系统停止行为；仅在停止必须运行应用清理、自定义停止行为或其他副作用时提供它。省略 `secondaryIntent` 以用于普通的静音/重复，并使用 `secondaryButtonBehavior: .countdown` 和 `Alarm.CountdownDuration.postAlert`；仅在 `.custom` 二次行为或应用清理/自定义行为时提供它。

### 闹钟状态转换

```text
cancel(id:)
    |
scheduled --> countdown --> alerting
    |             |             |
    |         pause(id:)    stop(id:) / countdown(id:)
    |             |
    |         paused ----> countdown (via resume(id:))
    |
cancel(id:) 完全从系统中移除
```

- `cancel(id:)` -- 完全移除闹钟，包括重复闹钟
- `pause(id:)` -- 暂停倒计时闹钟；在其他状态中抛出
- `resume(id:)` -- 恢复暂停的闹钟；在其他状态中抛出
- `stop(id:)` -- 停止闹钟；一次性闹钟被移除，重复闹钟重新安排
- `countdown(id:)` -- 从警报状态重新开始倒计时（静音）；在其他状态中抛出

## 倒计时计时器

计时器在经过一段时间后触发，并始终显示倒计时 UI。使用 `Alarm.CountdownDuration` 控制预警报和后警报的持续时间。

### CountdownDuration

`Alarm.CountdownDuration` 控制可见的倒计时阶段：

- `preAlert` -- 在闹钟响起前倒计时的秒数（主要的倒计时）
- `postAlert` -- 闹钟响起后重复/静音倒计时的秒数

加载 [完整的倒计时计时器流程](references/alarmkit-patterns.md#complete-countdown-timer-flow) 以获取计时器工厂、暂停/恢复呈现、元数据和安排门。

## 闹钟状态

每个 `Alarm` 都有一个 `state` 属性，反映其当前生命周期位置。

| 状态 | 含义 |
|---|---|
| `.scheduled` | 安排好，准备在适当时间提醒 |
| `.countdown` | 积极倒计时（计时器或预警报阶段） |
| `.paused` | 由用户或应用暂停倒计时 |
| `.alerting` | 闹钟正在响起 -- 正在播放声音，UI 醒目 |

### 观察状态变化

`AlarmManager.shared.alarms` 是一个抛出获取器，用于当前守护进程快照。使用 `try`，或者将启动刷新包装在 `do/catch` 中，然后再依赖快照。

观察 `alarmUpdates` 而不是维护独立的生命周期。加载 [使用异步序列观察状态](references/alarmkit-patterns.md#state-observation-with-async-sequences) 以获取完整的商店和刷新循环。

从 `alarmUpdates` 中消失的闹钟不再使用 AlarmKit 安排。当您需要区分触发的、取消的和重新安排的闹钟时，请与应用的持久化 ID 进行比较。

## AlarmAttributes 和 AlarmPresentation

`AlarmAttributes` 符合 `ActivityAttributes`，并定义闹钟的 Live Activity 的静态数据。它是一个泛型类型，其 `Metadata` 类型符合 `AlarmMetadata`，它继承自 `Decodable`、`Encodable`、`Hashable` 和 `Sendable`。`metadata` 值本身是可选的，默认为 `nil`。

`AlarmPresentation` 提供所需的警报内容和可选的倒计时/暂停内容。系统渲染警报 UI；Widget Extension 可以使用相同的属性和呈现状态自定义倒计时和暂停的 Live Activity 视图。保持元数据轻量级，当它不必要时使用 `nil`，并与 Widget Extension 共享其类型。

### AlarmPresentationState

`AlarmPresentationState` 是闹钟 Live Activity 的系统管理的 `ContentState`。它包含闹钟 ID 和一个 `Mode` 枚举：

- `.alert(Alert)` -- 闹钟正在响起，包括安排时间
- `.countdown(Countdown)` -- 积极倒计时，包括触发日期和持续时间
- `.paused(Paused)` -- 倒计时暂停，包括已用和总持续时间

Widget Extension 读取 `AlarmPresentationState.mode` 以决定在非警报状态下在动态岛和锁屏上渲染哪个 UI。

## AlarmButton

`AlarmButton` 定义闹钟操作的文本、颜色和符号。上面的代表性安排示例显示了一个标准的静音按钮。

### Secondary Button Behavior

警报 UI 上的次要按钮有两种行为：

| 行为 | 效果 |
|---|---|
| `.countdown` | 使用 `postAlert` 持续时间重新开始倒计时（静音） |
| `.custom` | 触发 `secondaryIntent`（例如，打开应用） |

## Live Activity 集成

AlarmKit 闹钟在闹钟响起时作为 Live Activity 显示在锁屏、动态岛、StandBy 和配对的 Apple Watch 上。系统管理警报 UI。对于倒计时和暂停状态，添加一个 Widget Extension 目标，其 `ActivityConfiguration` 使用与安排闹钟时相同的 `AlarmAttributes<Metadata>` 类型。

如果您的闹钟使用倒计时呈现，则预期有一个 Widget Extension。将轻量级的元数据类型提供给应用和 Widget Extension。如果没有扩展，闹钟可能会意外被关闭或无法提醒，尽管在设备重启后第一次解锁之前的有限情况下，系统仍然可以显示备用倒计时 UI。

| 工作 | 所有者 |
|---|---|
| 授权、安排/状态、呈现、声音、系统闹钟操作 | AlarmKit |
| 主屏幕/智能堆栈 Widget、家族、时间线、重新加载 | `widgetkit` |
| 非警报 Live Activity 生命周期、令牌、远程内容状态 | `activitykit` |
| APNs、通知类别/操作、自定义通知 UI | `push-notifications` |

AlarmKit 的警报在锁屏、动态岛、StandBy 和配对的 Apple Watch 上由系统渲染；只有倒计时/暂停状态使用 Widget Extension。

对于设置，命名 Apple 文档中的 `NSAlarmKitUsageDescription` 和 `AlarmManager` 授权。除非当前 Apple 源文档中记录了它们，否则不要要求不支持的 AlarmKit 设置键或 `com.apple.developer.alarmkit`。加载 [Live Activity Widget Extension for Alarms](references/alarmkit-patterns.md#live-activity-widget-extension-for-alarms) 以获取完整的共享属性 Widget 实现。

## 常见错误

| 错误 | 修正 |
|---|---|
| 缺少使用字符串或授权门 | 添加 `NSAlarmKitUsageDescription`；在安排前处理拒绝 |
| 使用计时器进行重复 | 使用带有 `.weekly([...])` 的闹钟 |
| 应用拥有的状态替换 `alarmUpdates` | 观察系统序列并按 ID 调整 |
| 添加了用于标准停止/静音的 Intent | 除非清理/自定义行为需要，否则省略它们 |
| 大型 `AlarmMetadata` 有效负载 | 保持轻量级元数据或通过 ID 引用应用数据 |
| 已弃用的 `stopButton` 初始化器 | 使用 `init(title:secondaryButton:secondaryButtonBehavior:)` |

## 审查清单

- [ ] 设置和授权门在不支持的自定义权限键下通过
- [ ] 闹钟/计时器选择、呈现、元数据、Intent、静音持续时间和色调有效
- [ ] 安排的 ID 保留并通过 `alarmUpdates` 调整；操作错误得到处理
- [ ] 倒计时使用共享的 Widget Extension 属性和呈现状态
- [ ] 系统管理的警报 UI 和相邻技能所有权遵循路由表
- [ ] 声音、振动、停止/静音和状态变化通过设备测试

## 参考资料

- 模式和代码：[references/alarmkit-patterns.md](references/alarmkit-patterns.md)
- Apple 文档：[AlarmKit](https://sosumi.ai/documentation/alarmkit) |
  [AlarmManager](https://sosumi.ai/documentation/alarmkit/alarmmanager) |
  [AlarmAttributes](https://sosumi.ai/documentation/alarmkit/alarmattributes) |
  [安排闹钟](https://sosumi.ai/documentation/alarmkit/scheduling-an-alarm-with-alarmkit)
