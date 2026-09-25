# MusicKit

搜索 Apple Music 目录，使用 `ApplicationMusicPlayer` 管理播放，检查订阅，并通过 `MPNowPlayingInfoCenter` 和 `MPRemoteCommandCenter` 发布正在播放的元数据。

## 目录

- [设置](#设置)
- [工作流](#工作流)
- [授权](#授权)
- [目录搜索](#目录搜索)
- [订阅检查](#订阅检查)
- [使用 ApplicationMusicPlayer 播放](#使用-applicationmusicplayer-播放)
- [队列管理](#队列管理)
- [正在播放的信息](#正在播放的信息)
- [远程命令中心](#远程命令中心)
- [常见错误](#常见错误)
- [审核清单](#审核清单)
- [参考资料](#参考资料)

## 工作流

1. 在调试代码之前，验证 MusicKit 应用服务、捆绑标识符、用途字符串和后台音频模式。
2. 请求授权，然后明确建模每个未授权状态。
3. 在排队播放之前，搜索或加载目录内容并检查 `MusicSubscription.current`。
4. 选择 `ApplicationMusicPlayer` 进行应用范围的播放；仅在应用拥有这些界面时才连接正在播放和远程命令。
5. 测试授权、拒绝、未订阅、离线、队列失败、中断和曲目更改状态。修复最小的失败层，恢复测试用例，并重新运行相同的状态矩阵。

## 设置

### 项目配置

1. 在 Apple 开发者门户中为应用显式捆绑标识符启用 **MusicKit App Service**，以便 MusicKit 可以自动生成开发者令牌。
2. 向 Info.plist 添加 `NSAppleMusicUsageDescription`，解释应用访问用户媒体库的原因。
3. 对于后台播放，将 `audio` 后台模式添加到 `UIBackgroundModes`。

### 导入

```swift
import MusicKit       // 目录、授权、播放
import MediaPlayer    // MPRemoteCommandCenter、MPNowPlayingInfoCenter
```

## 授权

在访问用户的音乐数据或播放 Apple Music 内容之前请求权限。`request()` 在需要时显示 Apple 的同意对话框；使用 `currentStatus` 读取当前设置而不提示。

```swift
func requestMusicAccess() async -> MusicAuthorization.Status {
    let status = await MusicAuthorization.request()
    switch status {
    case .authorized:
        // 完全访问 MusicKit API
        break
    case .denied, .restricted:
        // 指导用户在设置中启用
        break
    case .notDetermined:
        break
    @unknown default:
        break
    }
    return status
}

// 检查当前状态而不提示
let current = MusicAuthorization.currentStatus
```

## 目录搜索

使用 `MusicCatalogSearchRequest` 搜索 Apple Music 目录。目录查找可以获取 Apple Music 资源，但订阅目录内容的播放仍需受 `MusicSubscription.current.canPlayCatalogContent` 控制。

```swift
func searchCatalog(term: String) async throws -> MusicItemCollection<Song> {
    var request = MusicCatalogSearchRequest(term: term, types: [Song.self])
    request.limit = 25

    let response = try await request.response()
    return response.songs
}
```

### 显示结果

```swift
for song in songs {
    print("\(song.title) by \(song.artistName)")
    if let artwork = song.artwork {
        let url = artwork.url(width: 300, height: 300)
        // 从 url 加载 artwork
    }
}
```

## 订阅检查

在提供播放功能之前，检查用户是否拥有有效的 Apple Music 订阅。

```swift
func checkSubscription() async throws -> Bool {
    let subscription = try await MusicSubscription.current
    return subscription.canPlayCatalogContent
}

// 观察订阅更改
func observeSubscription() async {
    for await subscription in MusicSubscription.subscriptionUpdates {
        if subscription.canPlayCatalogContent {
            // 启用完整播放 UI
        } else {
            // 显示订阅提议
        }
    }
}
```

### 提供 Apple Music

当用户未订阅时，显示 Apple Music 订阅提议表单。首先检查 `canBecomeSubscriber`，当表单需要上下文元数据或加载错误处理时，传递 `MusicSubscriptionOffer.Options` 或 `onLoadCompletion`。

```swift
import MusicKit
import SwiftUI

struct MusicOfferView: View {
    @State private var showOffer = false

    var body: some View {
        Button("订阅 Apple Music") {
            Task {
                let subscription = try? await MusicSubscription.current
                showOffer = subscription?.canBecomeSubscriber == true
            }
        }
        .musicSubscriptionOffer(
            isPresented: $showOffer,
            options: .default,
            onLoadCompletion: { error in
                if let error {
                    // 在应用 UI 或诊断中显示加载错误。
                    print(error)
                }
            }
        )
    }
}
```

## 使用 ApplicationMusicPlayer 播放

`ApplicationMusicPlayer` 独立于 Music 应用播放 Apple Music 内容。它不会影响系统播放器的状态。

```swift
let player = ApplicationMusicPlayer.shared

func playSong(_ song: Song) async throws {
    player.queue = [song]
    try await player.play()
}

func pause() {
    player.pause()
}

func skipToNext() async throws {
    try await player.skipToNextEntry()
}
```

### 观察播放状态

```swift
func observePlayback() {
    // player.state 是一个 @Observable 属性
    let state = player.state
    switch state.playbackStatus {
    case .playing:
        break
    case .paused:
        break
    case .stopped, .interrupted, .seekingForward, .seekingBackward:
        break
    @unknown default:
        break
    }
}
```

## 队列管理

使用 `ApplicationMusicPlayer.Queue` 构建和操作播放队列。

```swift
// 使用多个项目初始化
func playAlbum(_ album: Album) async throws {
    player.queue = [album]
    try await player.play()
}

// 将歌曲追加到现有队列
func appendToQueue(_ songs: [Song]) async throws {
    try await player.queue.insert(songs, position: .tail)
}

// 插入歌曲以播放下一首
func playNext(_ song: Song) async throws {
    try await player.queue.insert(song, position: .afterCurrentEntry)
}
```

## 正在播放的信息

更新 `MPNowPlayingInfoCenter`，以便锁屏、控制中心和 CarPlay 显示当前曲目元数据。这对于播放自定义音频（非 MusicKit 源）至关重要。`ApplicationMusicPlayer` 会自动为 Apple Music 内容处理此操作。

```swift
import MediaPlayer

func updateNowPlaying(title: String, artist: String, duration: TimeInterval, elapsed: TimeInterval) {
    var info = [String: Any]()
    info[MPMediaItemPropertyTitle] = title
    info[MPMediaItemPropertyArtist] = artist
    info[MPMediaItemPropertyPlaybackDuration] = duration
    info[MPNowPlayingInfoPropertyElapsedPlaybackTime] = elapsed
    info[MPNowPlayingInfoPropertyPlaybackRate] = 1.0
    info[MPNowPlayingInfoPropertyMediaType] = MPNowPlayingInfoMediaType.audio.rawValue

    MPNowPlayingInfoCenter.default().nowPlayingInfo = info
}

func clearNowPlaying() {
    MPNowPlayingInfoCenter.default().nowPlayingInfo = nil
}
```

### 添加 artwork

```swift
func setArtwork(_ image: UIImage) {
    let artwork = MPMediaItemArtwork(boundsSize: image.size) { _ in image }
    var info = MPNowPlayingInfoCenter.default().nowPlayingInfo ?? [:]
    info[MPMediaItemPropertyArtwork] = artwork
    MPNowPlayingInfoCenter.default().nowPlayingInfo = info
}
```

## 远程命令中心

为 `MPRemoteCommandCenter` 注册处理程序，以响应用户锁屏控制、AirPods 点击手势和 CarPlay 按钮。

```swift
func setupRemoteCommands() {
    let center = MPRemoteCommandCenter.shared()

    center.playCommand.addTarget { _ in
        resumePlayback()
        return .success
    }

    center.pauseCommand.addTarget { _ in
        pausePlayback()
        return .success
    }

    center.nextTrackCommand.addTarget { _ in
        skipToNext()
        return .success
    }

    center.previousTrackCommand.addTarget { _ in
        skipToPrevious()
        return .success
    }

    // 禁用您不支持的命令
    center.seekForwardCommand.isEnabled = false
    center.seekBackwardCommand.isEnabled = false
}
```

### 滚动支持

```swift
func enableScrubbing() {
    let center = MPRemoteCommandCenter.shared()
    center.changePlaybackPositionCommand.addTarget { event in
        guard let positionEvent = event as? MPChangePlaybackPositionCommandEvent else {
            return .commandFailed
        }
        seek(to: positionEvent.positionTime)
        return .success
    }
}
```

## 常见错误

| 错误 | 修复 |
|---|---|
| 在配置 App Service 和用途字符串之前调试授权 | 首先验证服务、捆绑标识符和 `NSAppleMusicUsageDescription`。 |
| 在没有订阅门控的情况下排队目录内容 | 检查 `canPlayCatalogContent`；仅在 `canBecomeSubscriber` 时提供订阅。 |
| 使用 `SystemMusicPlayer` 进行应用拥有的播放 | 使用 `ApplicationMusicPlayer`；系统播放器会更改 Music 应用的全局队列。 |
| 一次发布正在播放的元数据 | 在曲目、持续时间、速率和已用时间更改时刷新它。 |
| 注册不支持的远程命令 | 禁用它们；支持的处理器必须执行操作并返回 `.success`。 |

## 审核清单

- [ ] 为应用的显式捆绑标识符启用了 MusicKit App Service
- [ ] 向 Info.plist 添加了 `NSAppleMusicUsageDescription`
- [ ] 在任何 MusicKit 访问之前调用了 `MusicAuthorization.request()`
- [ ] 在尝试目录播放之前检查了订阅
- [ ] 在显示订阅提议之前检查了 `canBecomeSubscriber`
- [ ] 在库写入之前检查了 `hasCloudLibraryEnabled`
- [ ] 使用了 `ApplicationMusicPlayer`（而不是 `SystemMusicPlayer`）进行应用范围的播放
- [ ] 如果音乐在后台播放，则启用了后台音频模式
- [ ] 在每个曲目更改时更新了正在播放的信息（对于自定义音频）
- [ ] 远程命令处理器在支持的命令上返回 `.success`
- [ ] 禁用了不支持的远程命令，`isEnabled = false`
- [ ] 为锁屏显示提供了正在播放的信息中的 artwork
- [ ] 定期更新已用播放时间以提高滚动精度
- [ ] 当用户没有 Apple Music 订阅时显示订阅提议

## 参考资料

- 扩展模式（SwiftUI 集成、流派浏览、播放列表管理）：[references/musickit-patterns.md](references/musickit-patterns.md)
- [MusicKit 框架](https://sosumi.ai/documentation/musickit)
- [使用自动开发者令牌生成 Apple Music API](https://sosumi.ai/documentation/musickit/using-automatic-token-generation-for-apple-music-api)
- [MusicAuthorization](https://sosumi.ai/documentation/musickit/musicauthorization)
- [ApplicationMusicPlayer](https://sosumi.ai/documentation/musickit/applicationmusicplayer)
- [MusicCatalogSearchRequest](https://sosumi.ai/documentation/musickit/musiccatalogsearchrequest)
- [MusicSubscription](https://sosumi.ai/documentation/musickit/musicsubscription)
- [canPlayCatalogContent](https://sosumi.ai/documentation/musickit/musicsubscription/canplaycatalogcontent)
- [canBecomeSubscriber](https://sosumi.ai/documentation/musickit/musicsubscription/canbecomesubscriber)
- [hasCloudLibraryEnabled](https://sosumi.ai/documentation/musickit/musicsubscription/hascloudlibraryenabled)
- [MusicCatalogChartsRequest 初始化器](https://sosumi.ai/documentation/musickit/musiccatalogchartsrequest/init(genre:kinds:types:))
- [musicSubscriptionOffer(isPresented:options:onLoadCompletion:)](https://sosumi.ai/documentation/swiftui/view/musicsubscriptionoffer(ispresented:options:onloadcompletion:))
- [MPRemoteCommandCenter](https://sosumi.ai/documentation/mediaplayer/mpremotecommandcenter)
- [MPNowPlayingInfoCenter](https://sosumi.ai/documentation/mediaplayer/mpnowplayinginfocenter)
- [NSAppleMusicUsageDescription](https://sosumi.ai/documentation/bundleresources/information-property-list/nsapplemusicusagedescription)
