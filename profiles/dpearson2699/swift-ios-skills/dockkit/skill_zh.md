# DockKit

与电动相机支架和云台集成框架，通过旋转iPhone物理跟踪主体。DockKit处理电机控制、主体检测和构图，使相机应用无需额外代码即可获得360度全景和90度俯仰跟踪。应用可以覆盖系统跟踪以提供自定义观察结果、直接控制电机或调整构图。iOS 17+，Swift 6.3。

## 目录

- [设置](#设置)
- [发现配件](#发现配件)
- [系统跟踪](#系统跟踪)
- [自定义跟踪](#自定义跟踪)
- [构图和兴趣区域](#构图和兴趣区域)
- [电机控制](#电机控制)
- [动画](#动画)
- [跟踪状态和主体选择](#跟踪状态和主体选择)
- [配件事件](#配件事件)
- [电池监控](#电池监控)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 设置

导入DockKit：

```swift
import DockKit
```

DockKit需要一个物理的DockKit兼容配件和一个真实设备。模拟器无法连接到Dock硬件。

DockKit本身不需要特殊的权限或DockKit特定的Info.plist键。使用设备相机的相机应用仍然需要正常的相机隐私处理，包括`NSCameraUsageDescription`。该框架通过DockKit系统守护进程自动与配对的配件通信。

应用必须使用AVFoundation相机API。DockKit钩入相机管道以分析帧进行系统跟踪。

## 发现配件

使用`DockAccessoryManager.shared`观察Dock连接：

```swift
import DockKit

func observeAccessories() async throws {
    for await stateChange in try DockAccessoryManager.shared.accessoryStateChanges {
        switch stateChange.state {
        case .docked:
            guard let accessory = stateChange.accessory else { continue }
            // 配件已连接并准备就绪
            configureAccessory(accessory)
        case .undocked:
            // iPhone已从Dock中取出
            handleUndocked()
        @unknown default:
            break
        }
    }
}
```

`accessoryStateChanges`会发出`DockAccessory.StateChange`值，包含`state`、`accessory`和`trackingButtonEnabled`。使用`accessory.identifier`获取名称、类别和UUID；硬件详细信息可通过`firmwareVersion`和`hardwareModel`获取。

## 系统跟踪

系统跟踪是DockKit的默认模式。启用时，系统通过内置的ML推理分析相机帧，检测面部和身体，并驱动电机以使主体保持在画面中。任何使用AVFoundation相机API的应用都会自动受益。

### 启用或禁用

```swift
// 启用系统跟踪（默认）
try await DockAccessoryManager.shared.setSystemTrackingEnabled(true)

// 禁用系统跟踪以进行自定义控制
try await DockAccessoryManager.shared.setSystemTrackingEnabled(false)
```

系统跟踪状态不会在应用终止、重启或后台/前台转换时保持。每次应用需要特定值时，都应显式设置它。

### 点击选择主体

允许用户通过点击选择特定主体：

```swift
// 选择视频帧坐标中单位点的主体
try await accessory.selectSubject(at: CGPoint(x: 0.5, y: 0.5))

// 通过UUID选择特定主体
try await accessory.selectSubjects([subjectUUID])

// 清除选择（返回自动选择）
try await accessory.selectSubjects([])
```

## 自定义跟踪

使用自定义ML模型或Vision框架时，禁用系统跟踪并提供您自己的观察结果。

### 提供观察结果

从您的推理输出构建`DockAccessory.Observation`值，并在10-30 fps的速率下将其传递给配件：

```swift
import DockKit
import AVFoundation

func processFrame(
    _ sampleBuffer: CMSampleBuffer,
    accessory: DockAccessory,
    activeDevice: AVCaptureDevice
) async throws {
    let cameraInfo = DockAccessory.CameraInformation(
        captureDevice: activeDevice.deviceType,
        cameraPosition: activeDevice.position,
        orientation: .corrected,
        cameraIntrinsics: frameIntrinsics(from: sampleBuffer),
        referenceDimensions: frameDimensions(from: sampleBuffer)
    )

    let detection = try await detector.detect(sampleBuffer)
    let observationType: DockAccessory.Observation.ObservationType = switch detection.kind {
    case .face: .humanFace
    case .body: .humanBody
    case .object: .object
    }

    let observation = DockAccessory.Observation(
        identifier: detection.id,
        type: observationType,
        rect: detection.rect,       // 归一化，左下角原点
        faceYawAngle: detection.faceYawAngle
    )

    try await accessory.track([observation], cameraInformation: cameraInfo)
}
```

### 观察结果类型

在审查自定义跟踪时，明确选择仅支持`ObservationType`情况：`.humanFace`、`.humanBody`和`.object`。当可能检测到身体或物体时，不要仅回答`.humanFace`。

`rect`使用归一化坐标，左下角原点（与Vision框架相同的坐标系——无需转换）。

### 相机信息

`DockAccessory.CameraInformation`描述了活动相机；不要硬编码占位符设备、内参或帧大小值。当坐标已经相对于左下角时，将方向设置为`.corrected`。在审查答案中，拒绝不透明的可选`cameraInfo`占位符，并显示从活动`AVCaptureDevice`和当前`CMSampleBuffer`的构建。

Track变体也接受`[AVMetadataObject]`而不是观察结果。当DockKit应将观察结果或元数据与捕获的图像缓冲区组合时，使用`image: CVPixelBuffer`重载；在这些重载中，图像参数是必需的。

## 构图和兴趣区域

### 构图模式

控制系统如何构图跟踪的主体：

```swift
try await accessory.setFramingMode(.automatic) // 文档默认值
try await accessory.setFramingMode(.center)    // 显式选择模式
```

| 模式 | 行为 |
|---|---|
| `.automatic` | 文档默认值；系统决定最佳构图 |
| `.center` | 显式选择模式以使主体居中 |
| `.left` | 将主体构图在左侧三分之一 |
| `.right` | 将主体构图在右侧三分之一 |

默认系统行为通常将主要主体居中，但`.center`永远不会是默认模式；`.automatic`是。当图形叠加层占据部分画面时，使用`.left`或`.right`。

### 兴趣区域

将跟踪限制在视频帧的特定区域：

```swift
// 归一化坐标，原点在左上角
let squareRegion = CGRect(x: 0.25, y: 0.0, width: 0.5, height: 1.0)
try await accessory.setRegionOfInterest(squareRegion)
```

使用兴趣区域在非标准纵横比裁剪时（例如，用于会议的正方形视频）使主体保持在可见区域内。

## 电机控制

在直接控制电机之前禁用系统跟踪。

### 角速度

设置连续旋转速度，单位为每秒弧度：

```swift
import Spatial

// 向右摇动0.2 rad/s，向下倾斜0.1 rad/s
let velocity = Vector3D(x: 0.1, y: 0.2, z: 0.0)
try await accessory.setAngularVelocity(velocity)

// 停止所有运动
try await accessory.setAngularVelocity(Vector3D())
```

轴：
- `x` -- 倾斜（tilt）。正倾斜在iOS上向下。
- `y` -- 摇摆（yaw）。正摇摆向右。
- `z` -- 翻滚（如果硬件支持）。

### 设置方向

在指定持续时间内在特定位置移动：

```swift
let target = Vector3D(x: 0.0, y: 0.5, z: 0.0)  // Yaw 0.5 rad
let progress = try accessory.setOrientation(
    target,
    duration: .seconds(2),
    relative: false
)
```

也接受`Rotation3D`用于基于四元数的方向。设置`relative: true`以相对于当前位置移动。返回的`Progress`对象跟踪完成情况。

### 运动状态

监控配件的当前位置和速度：

```swift
for await state in try accessory.motionStates {
    let positions = state.angularPositions   // Vector3D
    let velocities = state.angularVelocities // Vector3D
    let time = state.timestamp
    if let error = state.error {
        // 电机错误发生
    }
}
```

### 设置限制

限制每个轴的运动范围和最大速度：

```swift
let yawLimit = try DockAccessory.Limits.Limit(
    positionRange: -1.0 ..< 1.0,   // 弧度
    maximumSpeed: 0.5               // rad/s
)
let limits = DockAccessory.Limits(yaw: yawLimit, pitch: nil, roll: nil)
try accessory.setLimits(limits)
```

## 动画

内置角色动画，使Dock表达性地移动：

```swift
// 动画前禁用系统跟踪
try await DockAccessoryManager.shared.setSystemTrackingEnabled(false)

let progress = try await accessory.animate(motion: .kapow)

// 等待完成
while !progress.isFinished && !progress.isCancelled {
    try await Task.sleep(for: .milliseconds(100))
}

// 恢复系统跟踪
try await DockAccessoryManager.shared.setSystemTrackingEnabled(true)
```

| 动画 | 效果 |
|---|---|
| `.yes` | 点头动作 |
| `.no` | 摇头动作 |
| `.wakeup` | 启动式动作 |
| `.kapow` | 戏剧性的摆动 |

动画从配件的当前位置开始，异步执行。完成后始终恢复跟踪状态。保持`animate(motion:)`和`setOrientation(_:duration:relative:)`调用不超过每秒两次；更高的调用率会抛出`.frameRateTooHigh`。

## 跟踪状态和主体选择

iOS 18+通过抛出`trackingStates`异步序列公开ML派生的跟踪信号。每个状态都有`time`和`trackedSubjects`（`.person`或`.object`）；person包括`identifier`、`rect`、`speakingConfidence`、`lookingAtCameraConfidence`和`saliencyRank`（排名较低更显著）。

```swift
if #available(iOS 18.0, *) {
    for await state in try accessory.trackingStates {
        var speaker: UUID?
        var engaged: UUID?
        var salient: (id: UUID, rank: Int)?
        for subject in state.trackedSubjects {
            switch subject {
            case .person(let person):
                let id = person.identifier, rect = person.rect
                let speaking = person.speakingConfidence
                let looking = person.lookingAtCameraConfidence
                let rank = person.saliencyRank
                updateSubjectOverlay(id: id, rect: rect)
                if let speaking, speaking > 0.7 { speaker = id }
                if let looking, looking > 0.7 { engaged = id }
                if let rank, salient == nil || rank < salient!.rank { salient = (id, rank) }
            case .object(let object):
                let id = object.identifier, rect = object.rect
                let rank = object.saliencyRank
                updateSubjectOverlay(id: id, rect: rect)
                if let rank, salient == nil || rank < salient!.rank { salient = (id, rank) }
            }
        }
        if let id = speaker ?? engaged ?? salient?.id { try await accessory.selectSubjects([id]) }
    }
}
```

使用`selectSubjects(_:)`通过UUID锁定跟踪；传递`[]`以返回自动选择。使用`speakingConfidence`为说话者，`lookingAtCameraConfidence`为参与，`rect`为叠加层，以及较低的`saliencyRank`值作为备用。
在审查答案中，在代码中消费`lookingAtCameraConfidence`和`rect`，而不仅仅是文字。

## 配件事件

Dock上的物理按钮通过抛出`accessoryEvents`异步序列（iOS 17.4+）触发事件：

```swift
if #available(iOS 17.4, *) {
    for await event in try accessory.accessoryEvents {
        switch event {
        case .cameraShutter: break
        case .cameraFlip: break
        case .cameraZoom(factor: let factor): break
        case .button(id: let id, pressed: let pressed): break
        @unknown default: break
        }
    }
}
```

第三方应用接收这些事件并通过AVFoundation实现行为。

## 电池监控

通过抛出`batteryStates`异步序列（iOS 18+）监控Dock的电池状态。Dock可以报告多个电池，每个电池通过`name`标识：

```swift
if #available(iOS 18.0, *) {
    var batteryRows: [String: (Double, DockAccessory.BatteryChargeState, Bool)] = [:]
    for await battery in try accessory.batteryStates {
        batteryRows[battery.name] = (battery.batteryLevel, battery.chargeState, battery.lowBattery)
    }
}
```

## 常见错误

### 不要：在禁用系统跟踪之前控制电机

```swift
// 错误——系统跟踪会与手动命令冲突
try await accessory.setAngularVelocity(velocity)

// 正确——首先禁用系统跟踪
try await DockAccessoryManager.shared.setSystemTrackingEnabled(false)
try await accessory.setAngularVelocity(velocity)
```

### 不要：假设跟踪状态在生命周期事件后保持

```swift
// 错误——在后台后状态可能已重置
func applicationDidBecomeActive() {
    // 假设自定义跟踪仍然活跃
}

// 正确——在前景中重新设置跟踪状态
func applicationDidBecomeActive() {
    Task {
        try await DockAccessoryManager.shared.setSystemTrackingEnabled(false)
    }
}
```

### 不要：在推荐速率外调用track()

```swift
// 错误——每秒调用一次太慢
try await accessory.track(observations, cameraInformation: cameraInfo)
// (调用频率为1 fps)

// 正确——以10-30 fps调用
// 钩入AVCaptureVideoDataOutputSampleBufferDelegate以进行每帧调用
```

### 不要：过度调用方向或动画

DockKit如果`animate(motion:)`或`setOrientation(_:duration:relative:)`每秒调用超过两次，会抛出`.frameRateTooHigh`。设置轨迹，观察其`Progress`，并避免紧密的命令循环。

### 不要：动画完成后忘记恢复跟踪

```swift
// 错误——跟踪在动画后保持禁用
try await DockAccessoryManager.shared.setSystemTrackingEnabled(false)
let progress = try await accessory.animate(motion: .kapow)

// 正确——在动画完成后恢复跟踪
try await DockAccessoryManager.shared.setSystemTrackingEnabled(false)
let progress = try await accessory.animate(motion: .kapow)
while !progress.isFinished && !progress.isCancelled {
    try await Task.sleep(for: .milliseconds(100))
}
try await DockAccessoryManager.shared.setSystemTrackingEnabled(true)
```

### 不要：在模拟器中使用DockKit

DockKit需要一个物理的DockKit兼容配件。在初始化时进行保护，并在没有配件时提供备用行为。

## 审查清单

- [ ] `import DockKit` 在需要的地方存在
- [ ] 订阅了`accessoryStateChanges`以检测Dock/Undock事件
- [ ] 处理了`.docked`和`.undocked`状态
- [ ] 在自定义跟踪或电机控制之前禁用系统跟踪
- [ ] 动画完成后恢复了系统跟踪
- [ ] 以10-30 fps提供自定义观察结果
- [ ] `animate`和`setOrientation`命令限制为每秒不超过两次
- [ ] 观察`rect`使用归一化坐标（左下角原点）
- [ ] 相机信息是直接从活动`AVCaptureDevice`和当前样本缓冲区构建的
- [ ] 观察结果类型选择名称`.humanFace`、`.humanBody`和`.object`
- [ ] 所有DockKit枚举的switch语句中处理了`@unknown default`
- [ ] 如果限制配件的运动范围，则设置了运动限制
- [ ] 应用返回到前景后重新应用跟踪状态
- [ ] `accessoryEvents`用`#available(iOS 17.4, *)`保护
- [ ] `trackingStates`和`batteryStates`用`#available(iOS 18.0, *)`保护
- [ ] 电池UI保留`BatteryState.name`以供多电池Dock
- [ ] 模拟器构建中没有任何DockKit代码路径执行

## 参考资料

- 扩展模式（Vision集成、服务架构、自定义动画）：[references/dockkit-patterns.md](references/dockkit-patterns.md)
- [DockKit框架](https://sosumi.ai/documentation/dockkit)
- [DockAccessoryManager](https://sosumi.ai/documentation/dockkit/dockaccessorymanager)
- [DockAccessory](https://sosumi.ai/documentation/dockkit/dockaccessory)
- [使用相机应用控制DockKit配件](https://sosumi.ai/documentation/dockkit/controlling-a-dockkit-accessory-using-your-camera-app)
- [在帧中跟踪自定义物体](https://sosumi.ai/documentation/dockkit/track-custom-objects-in-a-frame)
- [以编程方式修改旋转和定位行为](https://sosumi.ai/documentation/dockkit/modify-rotation-and-positioning-behavior-programmatically)
- [使用DockKit集成电动iPhone支架——WWDC23](https://sosumi.ai/videos/play/wwdc2023/10304/)
- [DockKit中的新功能——WWDC24](https://sosumi.ai/videos/play/wwdc2024/10164/)
