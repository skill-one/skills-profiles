# GroupActivities / SharePlay

使用 GroupActivities 框架构建共享实时体验。SharePlay 通过 FaceTime、信息、AirDrop 和附近 visionOS 共享连接人们，同步媒体播放、应用程序状态或自定义数据。

## 内容

- [设置](#设置)
- [定义 GroupActivity](#定义-groupactivity)
- [会话生命周期](#会话生命周期)
- [发送和接收消息](#发送和接收消息)
- [协调媒体播放](#协调媒体播放)
- [从您的应用程序启动 SharePlay](#从您的应用程序启动-shareplay)
- [GroupSessionJournal：文件传输](#groupsessionjournal文件传输)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 设置

### 能力

在 Xcode 中将 **Group Activities** 能力添加到应用程序目标。Xcode 添加所需的授权并更新配置文件：

```xml
<key>com.apple.developer.group-session</key>
<true/>
```

仅针对应用程序目标进行此配置。Group Activities 在小部件、扩展或 App Clips 中不可用。

### 检查资格

```swift
import GroupActivities

let observer = GroupStateObserver()

// 检查 FaceTime 通话或信息对话是否处于活动状态
if observer.isEligibleForGroupSession {
    showSharePlayButton()
}
```

反应式地观察变化：

```swift
for await isEligible in observer.$isEligibleForGroupSession.values {
    showSharePlayButton(isEligible)
}
```

## 定义 GroupActivity

遵守 `GroupActivity` 并提供元数据：

```swift
import GroupActivities

struct WatchTogetherActivity: GroupActivity {
    let movieID: String
    let movieTitle: String

    var metadata: GroupActivityMetadata {
        var meta = GroupActivityMetadata()
        meta.title = movieTitle
        meta.type = .watchTogether
        meta.fallbackURL = URL(string: "https://example.com/movie/\(movieID)")!
        return meta
    }
}
```

### 活动类型

| 类型 | 用例 |
|---|---|
| `.generic` | 自定义活动的默认值 |
| `.watchTogether` | 视频播放 |
| `.listenTogether` | 音频播放 |
| `.createTogether` | 协作创建（绘画、编辑） |
| `.exploreTogether` | 共享浏览、计划或探索 |
| `.learnTogether` | 共享学习或学习 |
| `.readTogether` | 共享阅读 |
| `.shopTogether` | 共享购物 |
| `.workoutTogether` | 共享健身课程 |

`GroupActivity` 是 `Codable`；存储的活动数据必须是可编码的。仅当使用 SwiftUI `ShareLink`、AirDrop 的 SharePlay 或 AppKit/UIKit 分享表时才添加 `Transferable`。保持有效负载最小：使用标识符或 URL 而不是大量数据。

## 会话生命周期

### 监听会话

设置一个长时间运行的任务，在另一个参与者启动活动时接收会话：

```swift
@Observable
@MainActor
final class SharePlayManager {
    private var session: GroupSession<WatchTogetherActivity>?
    private var messenger: GroupSessionMessenger?
    private var sessionTasks: [Task<Void, Never>] = []

    func observeSessions() {
        Task {
            for await session in WatchTogetherActivity.sessions() {
                self.configureSession(session)
            }
        }
    }

    private func configureSession(
        _ session: GroupSession<WatchTogetherActivity>
    ) {
        self.session = session
        self.messenger = GroupSessionMessenger(session: session)

        // 观察会话状态变化
        let stateTask = Task {
            for await state in session.$state.values {
                handleState(state)
            }
        }
        sessionTasks.append(stateTask)

        // 观察参与者变化
        let participantTask = Task {
            for await participants in session.$activeParticipants.values {
                handleParticipants(participants)
            }
        }
        sessionTasks.append(participantTask)

        // 加入会话
        session.join()
    }

    private func cleanUp() {
        sessionTasks.forEach { $0.cancel() }
        sessionTasks.removeAll()
        session = nil
        messenger = nil
    }
}
```

### 会话状态

| 状态 | 描述 |
|---|---|
| `.waiting` | 会话存在，但本地参与者尚未加入 |
| `.joined` | 本地参与者正在积极参与会话 |
| `.invalidated(reason:)` | 会话结束（检查原因以获取详细信息） |

### 处理状态变化

```swift
private func handleState(_ state: GroupSession<WatchTogetherActivity>.State) {
    switch state {
    case .waiting:
        print("等待加入")
    case .joined:
        print("已加入会话")
        loadActivity(session?.activity)
    case .invalidated(let reason):
        print("会话结束：\(reason)")
        cleanUp()
    @unknown default:
        break
    }
}

private func handleParticipants(_ participants: Set<Participant>) {
    print("活跃参与者：\(participants.count)")
}
```

### 离开和结束

```swift
// 离开会话（其他参与者继续）
session?.leave()

// 为所有参与者结束会话
session?.end()
```

## 发送和接收消息

使用 `GroupSessionMessenger` 在参与者之间同步小而时间敏感的应用程序状态。

### 定义消息

消息必须是 `Codable`；每个消息必须小于 256 KB。

```swift
struct SyncMessage: Codable {
    let action: String
    let timestamp: Date
    let data: [String: String]
}
```

### 发送

```swift
func sendSync(_ message: SyncMessage) async throws {
    guard let messenger else { return }

    try await messenger.send(message, to: .all)
}

// 发送给特定参与者
try await messenger.send(message, to: .only(participant))
```

### 接收

```swift
func observeMessages() {
    guard let messenger else { return }

    Task {
        for await (message, context) in messenger.messages(of: SyncMessage.self) {
            let sender = context.source
            handleReceivedMessage(message, from: sender)
        }
    }
}
```

### 传输模式

```swift
// 可靠（默认）-- 检查并重试关键状态
let reliableMessenger = GroupSessionMessenger(
    session: session,
    deliveryMode: .reliable
)

// 不可靠 -- 更低延迟，无传输保证
let unreliableMessenger = GroupSessionMessenger(
    session: session,
    deliveryMode: .unreliable
)
```

使用 `.reliable` 用于状态更改操作，如选择或轮次。使用 `.unreliable` 用于高频临时数据，如光标位置、绘画笔触和反应。

## 协调媒体播放

对于视频/音频，使用 `AVPlaybackCoordinator` 与 `AVPlayer`：

```swift
import AVFoundation
import GroupActivities

func configurePlayback(
    session: GroupSession<WatchTogetherActivity>,
    player: AVPlayer
) {
    // 将播放器的协调器连接到会话
    let coordinator = player.playbackCoordinator
    coordinator.coordinateWithSession(session)
}
```

连接后，AVFoundation 同步播放/暂停、跳转、速率、播放速度和时间。不要将 AVPlayer 传输字段放入 messenger 消息或快照中，包括晚加入者的快照；仅使用自定义消息用于播放之外的状态。

## 从您的应用程序启动 SharePlay

### 使用 GroupActivitySharingController (UIKit)

```swift
import GroupActivities
import UIKit

func startSharePlay() async throws {
    let activity = WatchTogetherActivity(
        movieID: "123",
        movieTitle: "Great Movie"
    )

    switch await activity.prepareForActivation() {
    case .activationPreferred:
        // 活动对话处于活动状态，用户选择共享。
        _ = try await activity.activate()

    case .activationDisabled:
        // 用户选择本地播放，或共享不可用。
        startLocalExperience()

    case .cancelled:
        break

    @unknown default:
        break
    }
}
```

当没有对话处于活动状态时（即 `isEligibleForGroupSession` 为 false），使用 `GroupActivitySharingController` 让用户先选择联系人：

```swift
let controller = try GroupActivitySharingController(activity)
present(controller, animated: true)
```

使用 `shareplay` SF Symbol 自定义控件。将 `GroupActivityMetadata` 视为发现副本：简洁的标题、副标题、图像和类型与入口点一致。保持兄弟域：GameKit 拥有身份验证、匹配、排行榜、成就和语音/聊天；TabletopKit 拥有座位、板设备、空间放置、轮次、规则和权威桌面状态；AVKit 拥有播放 UI。SharePlay 拥有邀请、生命周期、参与者和协调交接。参见 [参考资料/shareplay-patterns.md](references/shareplay-patterns.md) 以获取 SwiftUI `ShareLink`、AirDrop 和直接激活模式。

## GroupSessionJournal：文件传输

对于较大、非时间敏感的附件，使用 `GroupSessionJournal` 而不是 `GroupSessionMessenger`。Journal 项目必须遵守 `Transferable`，对晚加入者可用，并限制为 100 MB。它需要 iOS/iPadOS/tvOS 17+、macOS 14+ 或 visionOS 1+。对于较大/受保护的资源，共享指针或清单，并使用服务器存储或应用程序管理的文件传输。

```swift
import GroupActivities

let journal = GroupSessionJournal(session: session)

// 上传 Transferable 文件或数据项
let attachment = try await journal.add(sharedImageItem)

// 观察传入的附件
Task {
    for await attachments in journal.attachments {
        for attachment in attachments {
            let data = try await attachment.load(Data.self)
            handleReceivedFile(data)
        }
    }
}
```

## 常见错误

### 不要：忘记调用 session.join()

配置存储的会话、messenger 和观察者，然后调用 `join()`。会话生命周期中的典型长时间运行的管理器显示了所需的顺序。

### 不要：忘记离开或结束会话

```swift
// 错误 -- 用户导航后会话仍然存活
func viewDidDisappear() {
    // 无操作 -- 会话泄漏
}

// 正确 -- 当视图被关闭时离开
func viewDidDisappear() {
    session?.leave()
    session = nil
    messenger = nil
}
```

### 不要：假设所有参与者都具有相同的状态

```swift
// 错误 -- 在处理晚加入者之前广播状态
func onJoin() {
    // 新参与者不知道当前状态是什么
}

// 正确 -- 向新参与者发送完整状态
func handleParticipants(_ participants: Set<Participant>) {
    let newParticipants = participants.subtracting(knownParticipants)
    for participant in newParticipants {
        Task {
            try await messenger?.send(currentState, to: .only(participant))
        }
    }
    knownParticipants = participants
}
```

### 不要：使用 SharePlay 传输用于大型/受保护的资源

```swift
// 错误 -- messenger 是小而时间敏感的；journal 是 Transferable 且 <=100 MB
let imageData = try Data(contentsOf: imageURL)     // 300 KB
try await messenger.send(imageData, to: .all)      // 太大
// 正确 -- journal 附件最多 100 MB；否则共享指针/清单
let journal = GroupSessionJournal(session: session)
try await journal.add(sharedImageItem)
// 较大/受保护的资源：服务器存储或应用程序管理的文件传输
```

### 不要：为媒体播放发送冗余消息

```swift
// 错误 -- 使用 AVPlayer 时手动同步播放/暂停
func play() {
    player.play()
    try await messenger.send(PlayMessage(), to: .all)
}

// 正确 -- 让 AVPlaybackCoordinator 处理
player.playbackCoordinator.coordinateWithSession(session)
player.play()  // 自动同步到所有参与者
```

### 不要：在视图重新创建时观察会话

在长时间运行的管理器中拥有 `sessions()` 监听器，而不是可重新创建的视图。使用上面显示的管理器生命周期，并在失效时取消其子任务。

## 审查清单

- [ ] 仅将 Group Activities 能力添加到应用程序目标
- [ ] `GroupActivity` 结构是 `Codable`，具有有意义的元数据
- [ ] 当使用 `ShareLink`、AirDrop 或分享表时添加 `Transferable` 实现
- [ ] 在长时间运行的对象中观察 `sessions()`（不是 SwiftUI 视图主体）
- [ ] 在接收并配置会话后调用 `session.join()`
- [ ] 当用户导航或关闭时调用 `session.leave()`
- [ ] `GroupSessionMessenger` 消息保持在 256 KB 以下，并具有适当的 `deliveryMode`
- [ ] 晚加入的参与者连接时接收当前状态
- [ ] 观察 `$state` 和 `$activeParticipants` 发布者以获取生命周期变化
- [ ] 使用 `GroupSessionJournal` 用于非时间敏感的 `Transferable` 附件
- [ ] 使用 `AVPlaybackCoordinator` 用于媒体同步（不是手动消息）
- [ ] 在显示 SharePlay UI 之前检查 `GroupStateObserver.isEligibleForGroupSession`
- [ ] 当没有对话处于活动状态时使用 `GroupActivitySharingController`
- [ ] 处理会话失效，清理 messenger、journal 和任务

## 参考资料

- 扩展模式（SwiftUI 共享、协作画布、空间 Personas）：[参考资料/shareplay-patterns.md](references/shareplay-patterns.md)
- [配置 Group Activities](https://sosumi.ai/documentation/xcode/configuring-group-activities)
- [GroupActivities 框架](https://sosumi.ai/documentation/groupactivities)
- [GroupActivity 协议](https://sosumi.ai/documentation/groupactivities/groupactivity)
- [GroupSession](https://sosumi.ai/documentation/groupactivities/groupsession)
- [GroupSessionMessenger](https://sosumi.ai/documentation/groupactivities/groupsessionmessenger)
- [GroupSessionJournal](https://sosumi.ai/documentation/groupactivities/groupsessionjournal)
- [GroupStateObserver](https://sosumi.ai/documentation/groupactivities/groupstateobserver)
- [GroupActivitySharingController](https://sosumi.ai/documentation/groupactivities/groupactivitysharingcontroller-ybcy)
- [定义您应用程序的 SharePlay 活动](https://sosumi.ai/documentation/groupactivities/defining-your-apps-shareplay-activities)
- [从您应用程序的 UI 中显示 SharePlay 活动](https://sosumi.ai/documentation/groupactivities/promoting-shareplay-activities-from-your-apps-ui)
- [在 SharePlay 活动期间同步数据](https://sosumi.ai/documentation/groupactivities/synchronizing-data-during-a-shareplay-activity)
- [支持协调媒体播放](https://sosumi.ai/documentation/avfoundation/supporting-coordinated-media-playback)
- [SharePlay HIG](https://sosumi.ai/design/human-interface-guidelines/shareplay)
