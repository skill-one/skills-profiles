# Unity Vivox — 语音与文本聊天

命名空间：`Unity.Services.Vivox` | 包：`com.unity.services.vivox`
配套包：`Unity.Services.Core`，`Unity.Services.Authentication`

Vivox v16+ 用单一的静态入口点 **`VivoxService.Instance`** 替换了 v4 的 `Client` / `ILoginSession` / `IChannelSession` 模型。所有操作——初始化、登录、频道加入、消息发送、静音——都通过它进行。**请勿**使用 v4 模式（`Client.Instance`，`AccountId`，`ChannelId`，`ILoginSession`，`UnityPurchasing.*` 等）；这些在 v16 中已不再使用。

## 文档映射

当具体细节存在差异时，使用 [Unity Vivox 精选文档映射](https://docs.unity.com/en-us/vivox-unity/llms.txt) 作为权威来源，用于主题、API 和错误代码。此技能及其引用定义了**如何**应用 SDK；该资源定义了**什么**被文档化。**切勿**向用户提及 `llms.txt` 文件名。如果无法访问，则将此技能的引用加上工作区中的已安装包（包管理器/源）视为事实依据。

## 详细引用

按需阅读——仅在你需要签名、事件细节或此文件中未包含的平台注意事项时。

- **初始化、登录和访问令牌：** [references/init-and-login.md](references/init-and-login.md)
- **语音频道（位置和非位置）：** [references/voice-channels.md](references/voice-channels.md)
- **文本聊天（频道消息和定向消息）：** [references/text-chat.md](references/text-chat.md)
- **事件、参与者和清理：** [references/events-and-participants.md](references/events-and-participants.md)
- **故障排除和平台说明：** [references/troubleshooting.md](references/troubleshooting.md)

## 初始化顺序（切勿跳过步骤）

正确的顺序是 **UGS 核心 → 认证登录 → Vivox 初始化 → Vivox 登录**。跳过或重新排序这些步骤会导致静默失败或抛出模糊的错误。

```csharp
using Unity.Services.Core;
using Unity.Services.Authentication;
using Unity.Services.Vivox;

async void Start()
{
    await UnityServices.InitializeAsync();
    await AuthenticationService.Instance.SignInAnonymouslyAsync();
    await VivoxService.Instance.InitializeAsync();
    // 在调用 LoginAsync 之前订阅事件（见下表）
    await VivoxService.Instance.LoginAsync(new LoginOptions { DisplayName = "Bob" });
}
```

- 调用 `VivoxService.Instance.InitializeAsync()` 两次会抛出 `5041 VxErrorAlreadyInitialized`。防止场景重新加载时的重复初始化。
- 如果未使用 Unity 认证（`AuthenticationService`），则玩家身份会回退到会话级 GUID——显示名称仍然有效，但你将失去跨会话身份。有关 Vivox 访问令牌（VAT）的替代方案，请参阅 [references/init-and-login.md](references/init-and-login.md)。

## 加入频道

Vivox 有三种加入方法，每种对应一种频道类型。所有方法都是异步的，但加入**通过 `ChannelJoined` 事件完成，而不是通过等待调用**——先订阅，再调用。

| 方法 | 目的 |
|---|---|
| `VivoxService.Instance.JoinGroupChannelAsync(name, ChatCapability, ChannelOptions?)` | 非位置（团队、队伍、大厅、公会） |
| `VivoxService.Instance.JoinEchoChannelAsync(name, ChatCapability, ChannelOptions?)` | 回音测试频道，将你自己的音频回放 |
| `VivoxService.Instance.JoinPositionalChannelAsync(name, ChatCapability, Channel3DProperties, ChannelOptions?)` | 由变换位置驱动的 3D 空间音频 |

`ChatCapability` 值：`TextOnly`，`AudioOnly`，`TextAndAudio`。

**限制：** 每个用户最多 10 个非位置频道；每个频道最多 200 个参与者。超出任一限制都会因 `20502 VxXmppServerErrorServiceUnavailable` 失败。对于 >200 个参与者的位置频道，请使用企业设置的“大型 3D 频道”。

使用 `VivoxService.Instance.LeaveChannelAsync(channelName)` 或 `LeaveAllChannelsAsync()` 退出。有关 `Channel3DProperties` 字段和 Android/iOS 上的麦克风权限处理，请参阅 [references/voice-channels.md](references/voice-channels.md)。

## 文本消息发送

**频道消息**（向 `TextOnly` 或 `TextAndAudio` 频道的所有参与者广播）：

- 发送：`VivoxService.Instance.SendChannelTextMessageAsync(string channelName, string message)`
- 接收：订阅 `VivoxService.Instance.ChannelMessageReceived` (`Action<VivoxMessage>`)

**定向消息**（点对点，无需频道）：

- 发送：`VivoxService.Instance.SendDirectTextMessageAsync(string playerId, string message)`
- 接收：订阅 `VivoxService.Instance.DirectedMessageReceived` (`Action<VivoxMessage>`)

**常见误解：** 发送方法为 `SendDirectTextMessageAsync`——**不是** `SendDirectedTextMessageAsync`。然而，事件**是** `DirectedMessageReceived`。注意这种不对称性。

`VivoxMessage` 字段：`ChannelName`（定向时为 null），`SenderDisplayName`，`SenderPlayerId`，`MessageText`，`ReceivedTime`，`Language`，`FromSelf`，`MessageId`。

编辑/删除 API（`EditChannelTextMessageAsync`，`DeleteChannelTextMessageAsync`，`EditDirectTextMessageAsync`，`DeleteDirectTextMessageAsync`）和历史记录（`GetChannelTextMessageHistoryAsync`，`GetDirectTextMessageHistoryAsync`）在 [references/text-chat.md](references/text-chat.md) 中涵盖。默认情况下，聊天记录保留期为 7 天。

## 必须订阅的事件

在执行相应异步调用**之前**订阅事件。`LoggedIn` 可能在重连时立即触发；`ChannelJoined` 在加入完成时触发。

| 调用 | 成功事件 | 失败/对应事件 |
|---|---|---|
| `LoginAsync()` | `LoggedIn` | `LoggedOut` |
| `JoinGroupChannelAsync()` / `JoinEchoChannelAsync()` / `JoinPositionalChannelAsync()` | `ChannelJoined(string channelName)` | `ChannelLeft(string channelName)` |
| — (任何已加入的频道) | `ParticipantAddedToChannel(VivoxParticipant)` | `ParticipantRemovedFromChannel(VivoxParticipant)` |
| `SendChannelTextMessageAsync()` (远程接收) | `ChannelMessageReceived(VivoxMessage)` | — |
| `SendDirectTextMessageAsync()` (远程接收) | `DirectedMessageReceived(VivoxMessage)` | — |

**始终在 `OnDestroy` / `OnDisable` 中取消订阅。** `VivoxService.Instance` 是一个持久的单例——在场景重新加载时，已销毁的 MonoBehaviours 上的事件处理程序会双重触发并导致 NRE。

每个参与者的事件（`ParticipantMuteStateChanged`，`ParticipantSpeechDetected`，`ParticipantAudioEnergyChanged`）存在于从 `ParticipantAddedToChannel` 接收到的 `VivoxParticipant` 实例上——**不是**在 `VivoxService.Instance` 上。请参阅 [references/events-and-participants.md](references/events-and-participants.md)。

## 访问令牌（简述）

默认路径使用 **UGS 认证**——Vivox 会自动从你的 UGS 项目中为 `AuthenticationService.Instance.SignInAnonymouslyAsync()`（或其他登录方法）完成后生成的访问令牌。**无需手动令牌代码**即可进行标准流程。

服务器端 Vivox 访问令牌（VAT）生成仅在您使用非 UGS 身份系统或需要频道级特权令牌（踢出、静音所有、转录）时才需要。请参阅文档映射的“访问令牌开发者指南”部分，以获取特定于语言的服务器示例。**切勿**在客户端嵌入 HMAC 签名密钥。

## 验证

在编写使用此包的代码后：

1. 验证项目是否无错误编译，且 `using Unity.Services.Vivox;` 解析。
2. 确认初始化顺序：`UnityServices.InitializeAsync` → `AuthenticationService.Instance.SignInAnonymouslyAsync` → `VivoxService.Instance.InitializeAsync` → `VivoxService.Instance.LoginAsync`。
3. 没有 v4 遗留模式：没有 `Client.Instance`，没有 `AccountId`，没有 `ChannelId`，没有 `ILoginSession`，没有 `IChannelSession`。所有访问都通过 `VivoxService.Instance`。
4. 代码消费的所有事件都在触发它们的异步调用**之前**订阅，并在 `OnDestroy` 中取消订阅。
5. 频道加入代码不会 `await` 加入调用，因为加入似乎已完成——它在 `ChannelJoined` 中反应。
6. 定向消息发送使用 `SendDirectTextMessageAsync`（**不是** `SendDirectedTextMessageAsync`）。定向消息接收使用 `DirectedMessageReceived`。
7. Android 构建在加入音频频道之前在运行时请求 `RECORD_AUDIO`；iOS 构建在 plist 中有 `NSMicrophoneUsageDescription`。
8. 客户端代码中未嵌入 HMAC 签名密钥或 Vivox `SECRET`/`APP_ID`——基于 VAT 的流程已记录，但已委托给服务器。
