# PermissionKit

请求家长或监护人的许可来修改孩子的通讯规则。PermissionKit 创建通讯安全体验，让孩子可以请求对父母设定的通讯限制进行例外处理。

PermissionKit 通讯体验仅通过 iMessage 提供。
用于家长/监护人审批流程，不作为通用应用内联系人许可、内容审核或聊天安全框架使用。

## 内容

- [可用性和设置](#可用性和设置)
- [核心概念](#核心概念)
- [检查通讯限制](#检查通讯限制)
- [创建许可问题](#创建许可问题)
- [使用 AskCenter 请求许可](#使用-askcenter-请求许可)
- [使用 PermissionButton 集成 SwiftUI](#使用-permissionbutton-集成-swiftui)
- [处理响应](#处理响应)
- [重要应用更新主题](#重要应用更新主题)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 可用性和设置

导入 `PermissionKit`。不要自行创建 PermissionKit 许可权键；在添加签名要求之前，请验证当前的 Apple 文档和 Xcode 功能。

```swift
import PermissionKit
```

使用此集中版本矩阵，并验证其与当前 SDK 一致：

| 等级 | API | iOS/iPadOS/Mac Catalyst/macOS/visionOS |
|---|---|---|
| 核心 | 主题、句柄、问题、响应、选项、`CommunicationLimits` | 26.0+ |
| 错误 | `AskError` | 26.1+ |
| 显示 | `AskCenter`、询问/响应序列、`PermissionButton`、重要更新主题 | 26.2+ |

## 核心概念

PermissionKit 管理以下流程：

1. 孩子在应用中遇到通讯限制
2. 应用创建一个描述请求的 `PermissionQuestion`
3. 系统向孩子展示问题，让孩子发送给父母
4. 父母审查并批准或拒绝请求
5. 应用收到包含父母决定的 `PermissionResponse`

### 关键类型

| 类型 | 角色 |
|---|---|
| `AskCenter` | 管理许可请求和响应的单例 |
| `PermissionQuestion` | 描述正在请求的许可 |
| `PermissionResponse` | 父母的决定（批准或拒绝） |
| `PermissionChoice` | 具体答案（批准/拒绝） |
| `PermissionButton` | 触发许可流程的 SwiftUI 按钮 |
| `CommunicationTopic` | 通讯相关许可请求的主题 |
| `CommunicationHandle` | 电话号码、电子邮件或自定义标识符 |
| `CommunicationLimits` | 检查系统是否已知的通讯句柄 |
| `SignificantAppUpdateTopic` | 重要应用更新许可请求的主题 |

## 检查通讯限制

使用 `CommunicationLimits.current` 检查系统是否已知道应用的一个通讯句柄。这不是一个“通讯限制是否启用？”的探测。如果限制未启用，`AskCenter.shared.ask(_:in:)` 会抛出 `AskError.communicationLimitsNotEnabled`；在请求时处理该路径。

`knownHandles(in:)` 也需要调用应用具有非空的、非空的捆绑标识符。修正的代码应在调用它之前检查 `Bundle.main.bundleIdentifier`。

```swift
import PermissionKit

func needsPermissionPrompt(for handle: CommunicationHandle) async -> Bool {
    let limits = CommunicationLimits.current
    let isKnown = await limits.isKnownHandle(handle)
    return !isKnown
}

// 一次性检查多个句柄。
func filterKnownHandles(_ handles: Set<CommunicationHandle>) async -> Set<CommunicationHandle> {
    guard Bundle.main.bundleIdentifier?.isEmpty == false else { return [] }

    let limits = CommunicationLimits.current
    return await limits.knownHandles(in: handles)
}
```

### 创建通讯句柄

```swift
let phoneHandle = CommunicationHandle(
    value: "+1234567890",
    kind: .phoneNumber
)

let emailHandle = CommunicationHandle(
    value: "friend@example.com",
    kind: .emailAddress
)

let customHandle = CommunicationHandle(
    value: "user123",
    kind: .custom
)
```

## 创建许可问题

使用联系人信息和通讯动作类型构建 `PermissionQuestion`。

```swift
// 单个联系人的问题
let handle = CommunicationHandle(value: "+1234567890", kind: .phoneNumber)
let question = PermissionQuestion<CommunicationTopic>(handle: handle)

// 多个联系人的问题
let handles = [
    CommunicationHandle(value: "+1234567890", kind: .phoneNumber),
    CommunicationHandle(value: "friend@example.com", kind: .emailAddress)
]
let multiQuestion = PermissionQuestion<CommunicationTopic>(handles: handles)
```

### 使用 CommunicationTopic 与个人信息

提供显示名称和头像，以提供更丰富的许可提示。

```swift
let personInfo = CommunicationTopic.PersonInformation(
    handle: CommunicationHandle(value: "+1234567890", kind: .phoneNumber),
    nameComponents: {
        var name = PersonNameComponents()
        name.givenName = "Alex"
        name.familyName = "Smith"
        return name
    }(),
    avatarImage: nil
)

let topic = CommunicationTopic(
    personInformation: [personInfo],
    actions: [.message, .audioCall]
)

let question = PermissionQuestion<CommunicationTopic>(communicationTopic: topic)
```

### 通讯动作

| 动作 | 描述 |
|---|---|
| `.message` | 文本消息 |
| `.audioCall` | 语音通话 |
| `.videoCall` | 视频通话 |
| `.call` | 通用通话 |
| `.chat` | 聊天通讯 |
| `.follow` | 关注用户 |
| `.beFollowed` | 允许被关注 |
| `.friend` | 好友请求 |
| `.connect` | 连接请求 |
| `.communicate` | 通用通讯 |

## 使用 AskCenter 请求许可

使用 `AskCenter.shared` 请求让孩子将许可问题发送给父母或监护人。异步 `ask` 调用启动发送流程；父母的决定稍后通过 `responses(for:)` 到达。如果孩子取消发送流程，系统不会为该问题发送 `PermissionResponse`。

```swift
import PermissionKit

func requestPermission(
    for question: PermissionQuestion<CommunicationTopic>,
    in viewController: UIViewController
) async {
    do {
        try await AskCenter.shared.ask(question, in: viewController)
        // 问题发送流程已启动；单独等待 responses(for:)。
    } catch let error as AskError {
        switch error {
        case .communicationLimitsNotEnabled:
            // 通讯限制未激活 -- 继续正常应用流程。
            break
        case .contactSyncNotSetup:
            // 联系人同步未配置
            break
        case .invalidQuestion:
            // 问题格式不正确
            break
        case .notAvailable:
            // PermissionKit 在此设备上不可用
            break
        case .systemError(let underlying):
            print("系统错误: \(underlying)")
        case .unknown:
            break
        @unknown default:
            break
        }
    }
}
```

## 使用 PermissionButton 集成 SwiftUI

`PermissionButton` 是一个 SwiftUI 视图，当点击时触发许可流程。它使用与 `AskCenter` 相同的响应模型：观察响应并建模待处理/已取消状态，而不是假设每次点击都会产生父母的决定。

```swift
import SwiftUI
import PermissionKit

struct ContactPermissionView: View {
    let handle = CommunicationHandle(value: "+1234567890", kind: .phoneNumber)

    var body: some View {
        let question = PermissionQuestion<CommunicationTopic>(handle: handle)

        PermissionButton(question: question) {
            Label("请求消息", systemImage: "message")
        }
    }
}
```

对于更丰富的 SwiftUI 流程、自定义主题和长期管理器，请参阅 [references/permissionkit-patterns.md](references/permissionkit-patterns.md)。

## 处理响应

异步监听许可响应。通过 `question.id` 跟踪待处理问题，并给 UI 提供重试或过期路径，因为孩子可以取消 iMessage 发送流程而不会产生响应。
当结合已知句柄检查与响应处理时，从 `knownHandles(in:)` 转移捆绑标识符的守卫。

```swift
enum PermissionRequestState {
    case pending, approved, denied, expired
}

var requestStates: [UUID: PermissionRequestState] = [:]

func expireIfStillPending(_ id: UUID) {
    guard requestStates[id] == .pending else { return }
    requestStates[id] = .expired
    // 重新启用请求或显示重试/已取消 UI。
}

func observeResponses() async {
    let responses = AskCenter.shared.responses(for: CommunicationTopic.self)

    for await response in responses {
        let choice = response.choice
        let question = response.question

        switch choice.answer {
        case .approval:
            // 父母批准 -- 启用通讯
            requestStates[question.id] = .approved
            print("批准主题: \(question.topic)")
        case .denial:
            // 父母拒绝 -- 保持限制
            requestStates[question.id] = .denied
            print("拒绝")
        @unknown default:
            break
        }
    }
}
```

### PermissionChoice 属性

```swift
let choice: PermissionChoice = response.choice
print("答案: \(choice.answer)")  // .approval 或 .denial
print("选择 ID: \(choice.id)")
print("标题: \(choice.title)")

// 便利静态常量
let approved = PermissionChoice.approve
let declined = PermissionChoice.decline
```

## 重要应用更新主题

请求需要父母批准的重要应用更新。您的应用根据适用法规确定什么构成重要更新，并应咨询合格的法律顾问进行合规解释。
使用简洁、易懂的描述，明确说明父母批准的具体变更。

```swift
let updateTopic = SignificantAppUpdateTopic(
    description: "此更新添加多人聊天功能"
)

let question = PermissionQuestion<SignificantAppUpdateTopic>(
    significantAppUpdateTopic: updateTopic
)

// 展示问题
try await AskCenter.shared.ask(question, in: viewController)
requestStates[question.id] = .pending
scheduleExpiration(for: question.id)

// 监听响应
for await response in AskCenter.shared.responses(for: SignificantAppUpdateTopic.self) {
    switch response.choice.answer {
    case .approval:
        // 继续更新
        requestStates[response.question.id] = .approved
    case .denial:
        // 跳过更新
        requestStates[response.question.id] = .denied
    @unknown default:
        break
    }
}

// 如果在您的待处理窗口到期之前没有收到响应，请保持更新受阻或提供重试。孩子取消不会产生拒绝响应。
```

## 常见错误

| 错误 | 修复 |
|---|---|
| 已知句柄查找被视为限制启用的证明 | 将 ask 操作中的 `.communicationLimitsNotEnabled` 作为未配置的正常路径处理。 |
| `AskError` 被合并为一个消息 | 区分限制禁用、联系人同步、无效问题、不可用、系统和其他未知情况。 |
| 问题没有句柄或个人信息 | 在展示之前至少验证一个有意义的通讯目标。 |
| Ask 是一次性操作 | 观察响应和待处理状态，同时允许孩子取消/放弃。 |
| 使用了已弃用的 `CommunicationLimitsButton` | 使用 `PermissionButton`。 |

## 审查清单

- [ ] 在选择 PermissionKit 之前理解 iMessage 仅路由
- [ ] 将集中可用性矩阵应用于使用中的每个 API
- [ ] 使用正确的 `Kind`（电话、电子邮件、自定义）创建 `CommunicationHandle`
- [ ] 在 `knownHandles(in:)` 之前，已创建非空的、非空的捆绑标识符
- [ ] 个人信息包括用于清晰许可提示的名称组件
- [ ] 通讯动作与应用的实际通讯能力匹配
- [ ] 响应处理在主线程更新 UI
- [ ] 错误状态向用户提供明确指导

## 参考资料

- 扩展模式（响应处理、多主题、UIKit）：[references/permissionkit-patterns.md](references/permissionkit-patterns.md)
- [PermissionKit 框架](https://sosumi.ai/documentation/permissionkit)
- [AskCenter](https://sosumi.ai/documentation/permissionkit/askcenter)
- [PermissionQuestion](https://sosumi.ai/documentation/permissionkit/permissionquestion)
- [PermissionButton](https://sosumi.ai/documentation/permissionkit/permissionbutton)
- [PermissionResponse](https://sosumi.ai/documentation/permissionkit/permissionresponse)
- [CommunicationTopic](https://sosumi.ai/documentation/permissionkit/communicationtopic)
- [CommunicationHandle](https://sosumi.ai/documentation/permissionkit/communicationhandle)
- [CommunicationLimits](https://sosumi.ai/documentation/permissionkit/communicationlimits)
- [SignificantAppUpdateTopic](https://sosumi.ai/documentation/permissionkit/significantappupdatetopic)
- [AskError](https://sosumi.ai/documentation/permissionkit/askerror)
- [创建通讯体验](https://sosumi.ai/documentation/permissionkit/creating-a-communication-experience)
