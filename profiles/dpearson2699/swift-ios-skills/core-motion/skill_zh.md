# CoreMotion

使用 CoreMotion 读取设备运动、计步器/活动、海拔、耳机、批量运动和浸没传感器。适用范围：Swift 6.3，iOS 26+。

## 目录

- [设置](#设置)
- [CMMotionManager: 传感器数据](#cmmotionmanager-sensor-data)
- [处理后的设备运动](#processed-device-motion)
- [CMPedometer: 步数和距离数据](#cmpedometer-step-and-distance-data)
- [CMMotionActivityManager: 活动识别](#cmmotionactivitymanager-activity-recognition)
- [CMAltimeter: 海拔数据](#cmaltimeter-altitude-data)
- [更新间隔和电池](#update-intervals-and-battery)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 设置

### Info.plist

在 Info.plist 中添加 `NSMotionUsageDescription`，并使用面向用户的字符串解释为什么您的应用需要运动数据。如果没有这个键，应用在首次访问时会崩溃。

```xml
<key>NSMotionUsageDescription</key>
<string>此应用使用运动数据来跟踪您的活动。</string>
```

### 授权

当 API 暴露 `authorizationStatus()` 或 `authorizationStatus` 属性时（例如 `CMPedometer`、`CMMotionActivityManager`、`CMAltimeter`、耳机运动、批量传感器和浸没），请使用匹配的管理器的 `authorizationStatus()` 或 `authorizationStatus` 属性。原始 `CMMotionManager` 加速度计/陀螺仪/设备运动流没有明确的授权请求 API；仍然发送使用字符串并处理从启动/更新回调中返回的错误。

```swift
import CoreMotion

let status = CMMotionActivityManager.authorizationStatus()
switch status {
case .notDetermined:
    // 首次使用时将提示
    break
case .authorized:
    break
case .restricted, .denied:
    // 引导用户到设置
    break
@unknown default:
    break
}
```

## CMMotionManager: 传感器数据

每个应用创建**一个** `CMMotionManager`。多个实例会降低传感器更新速率。

```swift
import CoreMotion

let motionManager = CMMotionManager()
```

### 加速度计更新

```swift
guard motionManager.isAccelerometerAvailable else { return }

motionManager.accelerometerUpdateInterval = 1.0 / 60.0  // 60 Hz

motionManager.startAccelerometerUpdates(to: .main) { data, error in
    guard let acceleration = data?.acceleration else { return }
    print("x: \(acceleration.x), y: \(acceleration.y), z: \(acceleration.z)")
}

// 完成时：
motionManager.stopAccelerometerUpdates()
```

### 陀螺仪更新

```swift
guard motionManager.isGyroAvailable else { return }

motionManager.gyroUpdateInterval = 1.0 / 60.0

motionManager.startGyroUpdates(to: .main) { data, error in
    guard let rotationRate = data?.rotationRate else { return }
    print("x: \(rotationRate.x), y: \(rotationRate.y), z: \(rotationRate.z)")
}

motionManager.stopGyroUpdates()
```

### 轮询模式（游戏）

对于游戏，无需处理程序启动更新，并在每帧轮询最新样本：

```swift
motionManager.startAccelerometerUpdates()

// 在您的游戏循环/显示链接中：
if let data = motionManager.accelerometerData {
    let tilt = data.acceleration.x
    // 根据倾斜移动玩家
}
```

## 处理后的设备运动

设备运动将加速度计、陀螺仪和磁力计融合为一个 `CMDeviceMotion` 对象，包含姿态、用户加速度（已去除重力）、旋转速率和校准磁场。

在提供设备运动指导时，请在代码片段中显示运行时帧检查，而不是硬编码一个校正的、磁北或真北帧。当首选帧不可用时，回退到 `.xArbitraryZVertical`。

```swift
guard motionManager.isDeviceMotionAvailable else { return }

let availableFrames = CMMotionManager.availableAttitudeReferenceFrames()
let frame: CMAttitudeReferenceFrame = availableFrames.contains(.xArbitraryCorrectedZVertical)
    ? .xArbitraryCorrectedZVertical
    : .xArbitraryZVertical

motionManager.deviceMotionUpdateInterval = 1.0 / 60.0

motionManager.startDeviceMotionUpdates(
    using: frame,
    to: .main
) { motion, error in
    guard let motion else { return }

    let attitude = motion.attitude       // roll, pitch, yaw
    let userAccel = motion.userAcceleration
    let gravity = motion.gravity
    let heading = motion.heading         // 相对于当前帧的角度

    print("Pitch: \(attitude.pitch), Roll: \(attitude.roll)")
}

motionManager.stopDeviceMotionUpdates()
```

### 姿态参考帧

对于简单的倾斜控制，使用 `.xArbitraryZVertical` 或 `.xArbitraryCorrectedZVertical`；它们避免了磁力计/位置依赖。在请求校正的、磁北或真北帧之前，请调用 `CMMotionManager.availableAttitudeReferenceFrames()` 并回退到可用的帧。

| 帧 | 用例 |
|---|---|
| `.xArbitraryZVertical` | 默认。Z 垂直，X 在开始时任意。大多数游戏。 |
| `.xArbitraryCorrectedZVertical` | 与上述相同，随时间校正陀螺仪漂移。 |
| `.xMagneticNorthZVertical` | X 指向磁北。需要磁力计。 |
| `.xTrueNorthZVertical` | X 指向真北。需要磁力计 + 位置。 |

使用前检查可用帧：

```swift
let available = CMMotionManager.availableAttitudeReferenceFrames()
if available.contains(.xTrueNorthZVertical) {
    // 安全使用真北
}
```

## CMPedometer: 步数和距离数据

`CMPedometer` 提供步数、距离、配速、步频和楼层计数。

```swift
let pedometer = CMPedometer()

guard CMPedometer.isStepCountingAvailable() else { return }

// 历史查询
pedometer.queryPedometerData(
    from: Calendar.current.startOfDay(for: Date()),
    to: Date()
) { data, error in
    guard let data else { return }
    print("今日步数: \(data.numberOfSteps)")
    print("距离: \(data.distance?.doubleValue ?? 0) 米")
    print("上升楼层: \(data.floorsAscended?.intValue ?? 0)")
}

// 实时更新
pedometer.startUpdates(from: Date()) { data, error in
    guard let data else { return }
    print("步数: \(data.numberOfSteps)")
}

// 完成时停止
pedometer.stopUpdates()
```

### 可用性检查

| 方法 | 检查内容 |
|---|---|
| `isStepCountingAvailable()` | 步数计数硬件 |
| `isDistanceAvailable()` | 距离估计 |
| `isFloorCountingAvailable()` | 气压计用于楼层 |
| `isPaceAvailable()` | 配速数据 |
| `isCadenceAvailable()` | 步频数据 |

## CMMotionActivityManager: 活动识别

检测用户是否静止、行走、跑步、骑行或处于交通工具中。

```swift
let activityManager = CMMotionActivityManager()

guard CMMotionActivityManager.isActivityAvailable() else { return }

// 实时活动更新
activityManager.startActivityUpdates(to: .main) { activity in
    guard let activity else { return }

    if activity.walking {
        print("行走 (置信度: \(activity.confidence.rawValue))")
    } else if activity.running {
        print("跑步")
    } else if activity.automotive {
        print("在交通工具中")
    } else if activity.cycling {
        print("骑行")
    } else if activity.stationary {
        print("静止")
    }
}

activityManager.stopActivityUpdates()
```

### 历史活动查询

```swift
let yesterday = Calendar.current.date(byAdding: .day, value: -1, to: Date())!

activityManager.queryActivityStarting(
    from: yesterday,
    to: Date(),
    to: .main
) { activities, error in
    guard let activities else { return }
    for activity in activities {
        print("\(activity.startDate): walking=\(activity.walking)")
    }
}
```

## CMAltimeter: 海拔数据

气压计访问由 `NSMotionUsageDescription` 覆盖；通过不可用数据和更新处理程序错误处理拒绝的运动访问。

```swift
let altimeter = CMAltimeter()

guard CMAltimeter.isRelativeAltitudeAvailable() else { return }

altimeter.startRelativeAltitudeUpdates(to: .main) { data, error in
    guard let data else { return }
    print("相对海拔: \(data.relativeAltitude) 米")
    print("气压: \(data.pressure) kPa")
}

altimeter.stopRelativeAltitudeUpdates()
```

绝对海拔是相对于海平面的海拔，而不是基于 GPS 的海拔。首先检查可用性。绝对海拔仅在支持硬件上可用，例如 iPhone 12 或更新版本，以及 Apple Watch Series 6、Apple Watch SE 或更新版本。

```swift
guard CMAltimeter.isAbsoluteAltitudeAvailable() else { return }

altimeter.startAbsoluteAltitudeUpdates(to: .main) { data, error in
    guard let data else { return }
    print("海拔: \(data.altitude)m, 精度: \(data.accuracy)m")
}

altimeter.stopAbsoluteAltitudeUpdates()
```

## 更新间隔和电池

| 间隔 | Hz | 用例 | 电池影响 |
|---|---|---|---|
| `1.0 / 10.0` | 10 | UI 方向 | 低 |
| `1.0 / 30.0` | 30 | 休闲游戏 | 中等 |
| `1.0 / 60.0` | 60 | 动作游戏 | 高 |
| `1.0 / 100.0` | 100 | 最大速率（iPhone） | 非常高 |

使用满足您需求的最低频率。不要假设跨设备固定最大样本速率。对于高频运动训练，在支持的情况下使用 `CMBatchedSensorManager`，并读取其报告的 `accelerometerDataFrequency` 或 `deviceMotionDataFrequency`，而不是分配这些只读属性。

## 常见错误

### 不要：创建多个 CMMotionManager 实例

保留一个应用级别的 `CMMotionManager`；竞争实例会降低更新速率。

### 不要：跳过传感器可用性检查

在启动每个传感器流之前立即应用匹配的 `is...Available` 门。

### 不要：忘记停止更新

在对应的生命周期或任务取消路径中，为每个启动配对相应的停止。

### 不要：使用不必要的更新速率

选择满足交互的最低速率，并将 [更新间隔和电池](#update-intervals-and-battery) 表作为起点。

### 不要：假设所有 CMMotionActivity 属性都是互斥的

```swift
// 错误 -- 只检查一个属性
if activity.walking { handleWalking() }

// 正确 -- 多个可以同时为真；检查置信度
if activity.walking && activity.confidence == .high {
    handleWalking()
} else if activity.automotive && activity.confidence != .low {
    handleDriving()
}
```

## 审查清单

- [ ] Info.plist 中包含 `NSMotionUsageDescription`，并有清晰的解释
- [ ] 应用程序跨共享一个 `CMMotionManager` 实例
- [ ] 在启动更新之前检查传感器可用性 (`isAccelerometerAvailable` 等)
- [ ] 在计步器/活动 API 之前检查授权状态
- [ ] 将更新间隔设置为最低可接受频率
- [ ] 在生命周期对应物中为所有 `start*Updates` 调用匹配 `stop*Updates`
- [ ] 处理程序派发到适当的队列（不要因重处理阻塞主队列）
- [ ] 在执行活动类型之前检查 `CMMotionActivity.confidence`
- [ ] 更新处理程序中检查错误参数
- [ ] 设备运动代码片段在请求特定姿态帧之前调用 `CMMotionManager.availableAttitudeReferenceFrames()`
- [ ] 根据实际需求选择姿态参考帧（不要不必要地默认为真北）

## 参考资料

- 扩展模式（SwiftUI 集成、批量传感器管理器、耳机运动、水浸没）：[references/motion-patterns.md](references/motion-patterns.md)
- [CoreMotion 框架](https://sosumi.ai/documentation/coremotion)
- [CMMotionManager](https://sosumi.ai/documentation/coremotion/cmmotionmanager)
- [CMPedometer](https://sosumi.ai/documentation/coremotion/cmpedometer)
- [CMMotionActivityManager](https://sosumi.ai/documentation/coremotion/cmmotionactivitymanager)
- [CMDeviceMotion](https://sosumi.ai/documentation/coremotion/cmdevicemotion)
- [CMAltimeter](https://sosumi.ai/documentation/coremotion/cmaltimeter)
- [CMAbsoluteAltitudeData](https://sosumi.ai/documentation/coremotion/cmabsolutealtitudedata)
- [CMBatchedSensorManager](https://sosumi.ai/documentation/coremotion/cmbatchedsensormanager)
- [CMHeadphoneMotionManager](https://sosumi.ai/documentation/coremotion/cmheadphonemotionmanager)
- [CMWaterSubmersionManager](https://sosumi.ai/documentation/coremotion/cmwatersubmersionmanager)
- [访问浸没数据](https://sosumi.ai/documentation/coremotion/accessing-submersion-data)
- [获取处理后的设备运动数据](https://sosumi.ai/documentation/coremotion/getting-processed-device-motion-data)
