# AVKit

基于 AVFoundation 构建的高级媒体播放 UI。提供系统标准的视频播放器、画中画、AirPlay 路由、传输控制以及字幕/标题显示。目标 Swift 6.3 / iOS 26+。

## 目录

- [设置](#设置)
- [AVPlayerViewController](#avplayerviewcontroller)
- [SwiftUI VideoPlayer](#swiftui-videoplayer)
- [画中画](#picture-in-picture)
- [AirPlay](#airplay)
- [传输控制和播放速度](#transport-controls-and-playback-speed)
- [字幕和闭路标题](#subtitles-and-closed-captions)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 设置

### 音频会话配置

当支持后台音频、AirPlay 或 PiP 时，播放应用需要音频会话类别和匹配的后台模式。

1. 启用后台模式 > 音频、AirPlay 和画中画（`UIBackgroundModes` 中的 `audio` 值）
2. 将音频会话类别设置为 `.playback`
3. 延迟 `setActive(true)` 直到播放开始，以免过早中断其他音频

```swift
import AVFoundation

func configureAudioSessionForPlayback() {
    let session = AVAudioSession.sharedInstance()
    do {
        try session.setCategory(.playback, mode: .moviePlayback)
    } catch {
        print("Audio session category failed: \(error)")
    }
}

func activateAudioSessionWhenPlaybackBegins() {
    do {
        try AVAudioSession.sharedInstance().setActive(true)
    } catch {
        print("Audio session activation failed: \(error)")
    }
}
```

### 导入

```swift
import AVKit          // AVPlayerViewController, VideoPlayer, PiP
import AVFoundation   // AVPlayer, AVPlayerItem, AVAsset
```

## AVPlayerViewController

`AVPlayerViewController` 是标准的 UIKit 播放器。它提供系统播放控制、PiP、AirPlay、字幕和帧分析，无需额外配置。不要子类化它。

### 基本展示（全屏）

```swift
import AVKit

func presentPlayer(from viewController: UIViewController, url: URL) {
    let player = AVPlayer(url: url)
    let playerVC = AVPlayerViewController()
    playerVC.player = player

    viewController.present(playerVC, animated: true) {
        player.play()
    }
}
```

### 内联（嵌入）播放

将 `AVPlayerViewController` 作为子视图控制器添加以进行内联播放。调用 `addChild`，添加约束视图，然后调用 `didMove(toParent:)`。

```swift
func embedPlayer(in parent: UIViewController, container: UIView, url: URL) {
    let playerVC = AVPlayerViewController()
    playerVC.player = AVPlayer(url: url)

    parent.addChild(playerVC)
    container.addSubview(playerVC.view)
    playerVC.view.translatesAutoresizingMaskIntoConstraints = false
    NSLayoutConstraint.activate([
        playerVC.view.leadingAnchor.constraint(equalTo: container.leadingAnchor),
        playerVC.view.trailingAnchor.constraint(equalTo: container.trailingAnchor),
        playerVC.view.topAnchor.constraint(equalTo: container.topAnchor),
        playerVC.view.bottomAnchor.constraint(equalTo: container.bottomAnchor)
    ])
    playerVC.didMove(toParent: parent)
}
```

### 关键属性

```swift
playerVC.showsPlaybackControls = true                    // 显示/隐藏系统控制
playerVC.videoGravity = .resizeAspect                    // .resizeAspectFill 以裁剪
playerVC.entersFullScreenWhenPlaybackBegins = false
playerVC.exitsFullScreenWhenPlaybackEnds = true
playerVC.updatesNowPlayingInfoCenter = true              // 自动更新 MPNowPlayingInfoCenter
```

使用 `contentOverlayView` 在视频和传输控制之间添加非交互式视图（水印、标志）。

### 代理

采用 `AVPlayerViewControllerDelegate` 以响应全屏转换、PiP 生命周期事件、插播播放和媒体选择更改。使用过渡协调器的 `animate(alongsideTransition:completion:)` 以同步您的 UI 与全屏动画。

### 显示就绪

在显示播放器之前观察 `isReadyForDisplay` 以避免黑屏：

```swift
let observation = playerVC.observe(\.isReadyForDisplay) { observed, _ in
    if observed.isReadyForDisplay {
        // 安全显示播放器视图
    }
}
```

## SwiftUI VideoPlayer

`VideoPlayer` SwiftUI 视图封装了 AVKit 的播放 UI。

### 基本用法

```swift
import SwiftUI
import AVKit

struct PlayerView: View {
    @State private var player: AVPlayer?

    var body: some View {
        Group {
            if let player {
                VideoPlayer(player: player)
                    .frame(height: 300)
            } else {
                ProgressView()
            }
        }
        .task {
            let url = URL(string: "https://example.com/video.m3u8")!
            player = AVPlayer(url: url)
        }
    }
}
```

### 视频叠加

在视频内容和系统播放控制之间添加 SwiftUI 叠加。叠加可以是交互式的，但它只接收系统控制未处理的系统事件。

```swift
VideoPlayer(player: player) {
    VStack {
        Spacer()
        HStack {
            Image("logo")
                .resizable()
                .frame(width: 40, height: 40)
                .padding()
            Spacer()
        }
    }
}
```

### UIKit 宿主以进行高级控制

`VideoPlayer` 暴露了 `AVPlayerViewController` 的所有属性。对于 PiP 配置、代理回调或播放速度控制，将 `AVPlayerViewController` 包裹在 `UIViewControllerRepresentable` 中。有关完整模式，请参阅 [参考资料/avkit-patterns.md](references/avkit-patterns.md)。

## 画中画

PiP 允许用户在使用其他应用时在浮动窗口中观看视频。`AVPlayerViewController` 一旦应用配置、设备支持 PiP 以及当前 `AVPlayerItem` 是在 `AVPlayer` 兼容格式中可播放的视频内容，就会自动支持 PiP。纯音频项、不支持的容器/编解码器或未准备好显示视频的项即使在应用和设备设置正确时也会使 PiP 不可用。对于自定义播放器 UI，请直接使用 `AVPictureInPictureController`。

### 前置条件

1. 音频会话类别设置为 `.playback`（参见 [设置](#设置)）
2. 后台模式 > 音频、AirPlay 和画中画已启用
3. 准备好的 `AVPlayerItem` 包含可播放的视频媒体，而不是纯音频内容
4. 当前播放上下文允许 PiP；对于自定义播放器，观察 `isPictureInPicturePossible`

### 标准播放器 PiP

PiP 在 `AVPlayerViewController` 中默认启用。控制自动激活和内联到 PiP 的转换：

```swift
let playerVC = AVPlayerViewController()
playerVC.player = player

// PiP 默认启用；设置为 false 以禁用
playerVC.allowsPictureInPicturePlayback = true

// 应用后台时自动启动 PiP（对于内联/非全屏播放器）
playerVC.canStartPictureInPictureAutomaticallyFromInline = true
```

### 当 PiP 停止时恢复 UI

当用户在 PiP 中点击恢复按钮时，实现代理方法以重新展示您的播放器。调用完成处理程序并传入 `true` 以指示系统完成恢复动画。

```swift
func playerViewController(
    _ playerViewController: AVPlayerViewController,
    restoreUserInterfaceForPictureInPictureStopWithCompletionHandler completionHandler: @escaping (Bool) -> Void
) {
    // 重新展示或重新嵌入播放器视图控制器
    present(playerViewController, animated: false) {
        completionHandler(true)
    }
}
```

### 自定义播放器 PiP

对于自定义播放器 UI，使用 `AVPictureInPictureController` 并使用 `AVPlayerLayer` 或样本缓冲区内容源。在创建 PiP UI 之前检查设备支持，然后在当前播放上下文中启动 PiP 之前检查控制器的 `isPictureInPicturePossible`。有关完整自定义播放器和样本缓冲区 PiP 模式，请参阅 [参考资料/avkit-patterns.md](references/avkit-patterns.md)。

```swift
guard AVPictureInPictureController.isPictureInPictureSupported() else { return }
let pipController = AVPictureInPictureController(playerLayer: playerLayer)
pipController.delegate = self
pipController.canStartPictureInPictureAutomaticallyFromInline = true

// 从用户的 PiP 按钮动作调用此方法，永远不要自动调用。
if pipController.isPictureInPicturePossible {
    pipController.startPictureInPicture()
}
```

### 广告期间的线性播放

插播中断可以来自媒体流/清单，AVFoundation 通过 `AVPlayerItem.interstitialTimeRanges` 暴露，也可以来自应用拥有的 `AVPlayerInterstitialEventController` 安排。iOS 上不要直接分配 `interstitialTimeRanges`。仅使用 `requiresLinearPlayback` 防止在必需的广告或法律段期间快进：

```swift
// 在广告期间
playerVC.requiresLinearPlayback = true

// 广告完成后
playerVC.requiresLinearPlayback = false
```

## AirPlay

当应用配置、媒体、路由和设备支持允许外部播放时，`AVPlayerViewController` 会自动支持 AirPlay。使用标准播放器时无需额外代码。当有 AirPlay 兼容设备时，系统会在传输控制中显示 AirPlay 按钮。

### AVRoutePickerView

在播放器 UI 外部添加一个独立的 AirPlay 路由选择器按钮：

```swift
import AVKit

func addRoutePicker(to containerView: UIView) {
    let routePicker = AVRoutePickerView(frame: CGRect(x: 0, y: 0, width: 44, height: 44))
    routePicker.activeTintColor = .systemBlue
    routePicker.prioritizesVideoDevices = true  // 首先显示视频兼容路由
    containerView.addSubview(routePicker)
}
```

### 外部播放

`AVPlayer` 默认允许外部播放。为 AirPlay 留意它，或在代码的其他部分可能禁用它时显式设置它：

```swift
player.allowsExternalPlayback = true
```

仅当您希望播放器在外部屏幕模式活动时自动切换到外部播放时，才设置 `usesExternalPlaybackWhileExternalScreenIsActive`。

## 传输控制和播放速度

### 自定义播放速度

在播放器 UI 中提供用户可选的播放速度：

```swift
let playerVC = AVPlayerViewController()
playerVC.speeds = [
    AVPlaybackSpeed(rate: 0.5, localizedName: "半速"),
    AVPlaybackSpeed(rate: 1.0, localizedName: "正常"),
    AVPlaybackSpeed(rate: 1.5, localizedName: "1.5x"),
    AVPlaybackSpeed(rate: 2.0, localizedName: "双速")
]
```

使用 `AVPlaybackSpeed.systemDefaultSpeeds` 恢复默认速度选项。

### 跳过和快进

在 iOS 上，使用标准传输控制和 `AVPlayer.seek(...)` 进行自定义应用控制。`AVPlayerViewController` 跳过行为 API（如 `isSkipForwardEnabled`、`isSkipBackwardEnabled` 和 `skippingBehavior`）专注于 tvOS；在 iOS 播放器实现中保持它们。

### Now Playing 集成

`AVPlayerViewController` 默认自动更新 `MPNowPlayingInfoCenter`。如果您手动管理 Now Playing 信息，请禁用此功能：

```swift
playerVC.updatesNowPlayingInfoCenter = false
```

## 字幕和闭路标题

当媒体包含适当的文本轨道时，AVKit 会自动处理字幕和闭路标题显示。用户在设置 > 无障碍 > 字幕和标题中控制字幕偏好。

### 程序性选择

```swift
let asset = player.currentItem?.asset

if let group = try await asset?.loadMediaSelectionGroup(for: .legible),
   let english = group.options.first(where: { option in
       option.locale?.language.languageCode?.identifier == "en"
   }) {
    player.currentItem?.select(english, in: group)
}
```

`allowedSubtitleOptionLanguages`、`requiresFullSubtitles` 和 `AVPlayerViewControllerDelegate` 媒体选择回调仅限 tvOS。对于 iOS，加载资产 `.legible` 媒体选择组，并在应用需要默认值时在 `AVPlayerItem` 上选择一个选项。

### 在 HLS 中提供字幕轨道

字幕和闭路标题嵌入在 HLS 清单中。AVKit 从 `AVMediaSelectionGroup` 在 `AVAsset` 上读取它们。对于本地文件，使用已包含可读字幕或闭路标题轨道的媒体，或在用 AVKit 展示它之前将那些轨道制作到可播放资产中。

## 常见错误

### 不要：子类化 AVPlayerViewController

苹果明确表示这不受支持。它可能导致未来 OS 版本的未定义行为或崩溃。

```swift
// 错误
class MyPlayerVC: AVPlayerViewController { } // 不受支持

// 正确：使用组合和代理
let playerVC = AVPlayerViewController()
playerVC.delegate = coordinator
```

### 不要：为 PiP 忘记音频会话配置

PiP 和后台播放依赖于播放音频会话类别和音频、AirPlay 和画中画后台模式。

```swift
// 错误：默认音频会话
let playerVC = AVPlayerViewController()
playerVC.player = player // PiP 不会工作

// 正确：配置类别，然后在播放开始时激活
try AVAudioSession.sharedInstance().setCategory(.playback, mode: .moviePlayback)
try AVAudioSession.sharedInstance().setActive(true)
let playerVC = AVPlayerViewController()
playerVC.player = player
```

### 不要：忘记 PiP 恢复代理或其完成处理程序

没有 `restoreUserInterfaceForPictureInPictureStopWithCompletionHandler`，系统无法将用户返回到您的播放器。不调用 `completionHandler(true)` 会将系统置于不一致状态。

```swift
// 错误：没有代理方法或缺少完成处理程序调用
// 用户在 PiP 中点击恢复 -> 什么也不发生或动画挂起

// 正确
func playerViewController(
    _ playerViewController: AVPlayerViewController,
    restoreUserInterfaceForPictureInPictureStopWithCompletionHandler completionHandler: @escaping (Bool) -> Void
) {
    present(playerViewController, animated: false) {
        completionHandler(true)
    }
}
```

### 不要：在 SwiftUI 视图的 init 中创建 AVPlayer

提前创建播放器会导致性能问题。SwiftUI 可能会多次重新创建视图。

```swift
// 错误：在每次视图 init 中创建
struct PlayerView: View {
    let player = AVPlayer(url: videoURL) // 在每次视图评估时重新创建

    var body: some View { VideoPlayer(player: player) }
}

// 正确：使用 @State 并延迟创建
struct PlayerView: View {
    @State private var player: AVPlayer?

    var body: some View {
        VideoPlayer(player: player)
            .task { player = AVPlayer(url: videoURL) }
    }
}
```

## 审查清单

- [ ] 音频会话类别设置为 `.playback` 并带有 `mode: .moviePlayback`
- [ ] 音频会话激活延迟到播放开始
- [ ] 音频、AirPlay 和画中画后台模式添加到 `UIBackgroundModes`
- [ ] `AVPlayerViewController` 没有被子类化
- [ ] 使用支持的视频媒体测试 PiP，而不仅仅是应用/设备设置
- [ ] PiP 恢复代理方法已实现并调用 `completionHandler(true)`
- [ ] 自定义 PiP 检查设备支持和当前 `isPictureInPicturePossible`
- [ ] 自定义 PiP 仅从明确用户交互启动
- [ ] SwiftUI 中 `AVPlayer` 延迟到 `.task`（不要提前创建）
- [ ] 为内联播放器设置 `canStartPictureInPictureAutomaticallyFromInline`
- [ ] 仅在必需的广告/法律段期间切换 `requiresLinearPlayback`
- [ ] iOS 专用的跳过 API 没有用于 iOS 传输控制
- [ ] 外部播放没有被意外禁用，而 AirPlay 是必需的
- [ ] 使用实际媒体轨道测试字幕选择
- [ ] 适当设置视频重力（`.resizeAspect` vs `.resizeAspectFill`）
- [ ] 在显示播放器视图之前观察 `isReadyForDisplay`
- [ ] 网络流内容（HLS 失败、超时）的错误处理

## 参考资料

- 高级模式（自定义播放器 UI、插播、后台播放、错误处理）：[参考资料/avkit-patterns.md](references/avkit-patterns.md)
- [AVKit 框架](https://sosumi.ai/documentation/avkit)
- [AVPlayerViewController](https://sosumi.ai/documentation/avkit/avplayerviewcontroller)
- [VideoPlayer (SwiftUI)](https://sosumi.ai/documentation/avkit/videoplayer)
- [AVPictureInPictureController](https://sosumi.ai/documentation/avkit/avpictureinpicturecontroller)
- [AVRoutePickerView](https://sosumi.ai/documentation/avkit/avroutepickerview)
- [AVPlaybackSpeed](https://sosumi.ai/documentation/avkit/avplaybackspeed)
- [为媒体播放配置您的应用](https://sosumi.ai/documentation/avfoundation/configuring-your-app-for-media-playback)
- [在标准播放器中采用 Picture in Picture](https://sosumi.ai/documentation/avkit/adopting-picture-in-picture-in-a-standard-player)
- [在标准用户界面中播放视频内容](https://sosumi.ai/documentation/avkit/playing-video-content-in-a-standard-user-interface)
