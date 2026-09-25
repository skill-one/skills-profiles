# SensorKit

选择精确的 `SRSensor` 并验证其单独的可用性。使用
CoreMotion 进行常规运动/活动功能，使用 HealthKit 进行健康记录和锻炼。

## 目录

- [概述和要求](#概述和要求)
- [权限](#权限)
- [Info.plist 配置](#infoplist-配置)
- [授权](#授权)
- [可用传感器](#可用传感器)
- [SRSensorReader](#srsensorreader)
- [录制和获取数据](#录制和获取数据)
- [SRDevice](#srdevice)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 概述和要求

SensorKit 使研究应用程序能够跨 iPhone 和 Apple Watch 录制和获取传感器数据。该框架需要：

1. **苹果批准的研究** -- 在
   [researchandcare.org](https://www.researchandcare.org/resources/accessing-sensorkit-data/) 提交提案。
2. **SensorKit 权限** -- 苹果仅对批准的研究授予 `com.apple.developer.sensorkit.reader.allow`。
3. **手动配置文件** -- Xcode 需要一个带有 SensorKit 功能的明确 App ID。
4. **用户授权** -- 系统显示 Research Sensor & Usage Data 表格，用户按传感器批准。
5. **延迟检索** -- 围绕规范
   [数据保留期](#数据保留期) 设计获取时间。

应用程序可以访问活跃传感器的最多 7 天的先前录制数据。

## 权限

将 SensorKit 读取权限添加到 `.entitlements` 文件。仅列出苹果为研究批准的传感器。常见的权限值包括：

```xml
<key>com.apple.developer.sensorkit.reader.allow</key>
<array>
    <string>ambient-light-sensor</string>
    <string>motion-accelerometer</string>
    <string>device-usage</string>
    <string>keyboard-metrics</string>
</array>
```

选择精确的权限字符串和 `NSSensorKitUsageDetail` 键时加载
[权限和使用详情目录](references/sensorkit-patterns.md#权限和使用详情目录)。对照其各自的 `SRSensor` 页面重新检查专业传感器。

对于手动签名，将代码签名权限设置为权限文件，代码签名标识设置为 `Apple Developer`，代码签名样式设置为 `Manual`，配置文件设置为带有 SensorKit 功能的明确配置文件。

## Info.plist 配置

需要三个键：

```xml
<!-- 在授权表格中显示的研究目的 -->
<key>NSSensorKitUsageDescription</key>
<string>本研究监测活动模式以进行睡眠研究。</string>

<!-- 链接到您研究的隐私政策 -->
<key>NSSensorKitPrivacyPolicyURL</key>
<string>https://example.com/privacy-policy</string>

<!-- 每个传感器的使用说明 -->
<key>NSSensorKitUsageDetail</key>
<dict>
    <key>SRSensorUsageMotion</key>
    <dict>
        <key>Description</key>
        <string>在研究期间测量身体活动水平。</string>
        <key>Required</key>
        <true/>
    </dict>
    <key>SRSensorUsageAmbientLightSensor</key>
    <dict>
        <key>Description</key>
        <string>记录环境光以评估睡眠环境。</string>
    </dict>
</dict>
```

如果 `Required` 为 `true` 且用户拒绝该传感器，系统会警告他们研究需要它并提供重新考虑的机会。

为每个请求的传感器使用精确的使用详情字典。映射上述运动和环境光示例之外的传感器时加载
[权限和使用详情目录](references/sensorkit-patterns.md#权限和使用详情目录)。

## 授权

请求您的研究所需的传感器的授权。系统在第一次请求时显示 Research Sensor & Usage Data 表格。

```swift
import SensorKit

let reader = SRSensorReader(sensor: .ambientLightSensor)

// 一次性请求多个传感器的授权
SRSensorReader.requestAuthorization(
    sensors: [.ambientLightSensor, .accelerometer, .keyboardMetrics]
) { error in
    if let error {
        print("授权请求失败: \(error)")
    }
}
```

使用一个状态处理程序既用于初始检查也用于委托更改：

```swift
private func applyAuthorizationStatus(
    _ status: SRAuthorizationStatus,
    to reader: SRSensorReader
) {
    switch status {
    case .authorized:
        reader.startRecording()
    case .denied:
        reader.stopRecording()
        // 指导用户前往设置 > 隐私 > 研究传感器和使用数据。
    case .notDetermined:
        break // 首先请求授权。
    @unknown default:
        break
    }
}

applyAuthorizationStatus(reader.authorizationStatus, to: reader)

func sensorReader(_ reader: SRSensorReader, didChange authorizationStatus: SRAuthorizationStatus) {
    applyAuthorizationStatus(authorizationStatus, to: reader)
}
```

## 可用传感器

加载
[传感器目录](references/sensorkit-patterns.md#传感器目录) 以将每个 `SRSensor` 映射到其样本类型。仅请求为研究批准的传感器，并重新检查选定传感器的可用性和使用详情键。

## SRSensorReader

`SRSensorReader` 是访问传感器数据的中心类。每个实例从单个传感器读取。

```swift
import SensorKit

// 为一个传感器创建一个读取器
let lightReader = SRSensorReader(sensor: .ambientLightSensor)
let keyboardReader = SRSensorReader(sensor: .keyboardMetrics)

// 分配委托以接收回调
lightReader.delegate = self
keyboardReader.delegate = self
```

读取器通过 `SRSensorReaderDelegate` 进行通信。连接完整的授权、录制、设备获取和样本获取生命周期时加载
[委托方法目录](references/sensorkit-patterns.md#委托方法目录)。

## 录制和获取数据

### 开始和停止录制

```swift
// 开始录制 -- 只要任何应用程序持有股份，传感器就会保持活跃
reader.startRecording()

// 停止录制 -- 框架在没有任何应用程序或系统进程使用它时停用传感器
reader.stopRecording()
```

### 获取数据

构建一个具有时间范围和目标设备的 `SRFetchRequest`，然后将其传递给读取器：

```swift
let request = SRFetchRequest()
request.device = SRDevice.current
request.from = SRAbsoluteTime(CFAbsoluteTimeGetCurrent() - 86400 * 2)  // 2 天前
request.to = SRAbsoluteTime.current()

reader.fetch(request)
```

通过委托接收结果：

```swift
func sensorReader(
    _ reader: SRSensorReader,
    fetching request: SRFetchRequest,
    didFetchResult result: SRFetchResult<AnyObject>
) -> Bool {
    let timestamp = result.timestamp

    switch reader.sensor {
    case .ambientLightSensor:
        if let sample = result.sample as? SRAmbientLightSample {
            let lux = sample.lux
            let chromaticity = sample.chromaticity
            let placement = sample.placement
            processSample(lux: lux, chromaticity: chromaticity, at: timestamp)
        }
    case .keyboardMetrics:
        if let sample = result.sample as? SRKeyboardMetrics {
            let words = sample.totalWords
            let speed = sample.typingSpeed
            processKeyboard(words: words, speed: speed, at: timestamp)
        }
    case .deviceUsageReport:
        if let sample = result.sample as? SRDeviceUsageReport {
            let wakes = sample.totalScreenWakes
            let unlocks = sample.totalUnlocks
            processUsage(wakes: wakes, unlocks: unlocks, at: timestamp)
        }
    default:
        break
    }

    return true  // 返回 true 以继续接收结果
}

func sensorReader(_ reader: SRSensorReader, didCompleteFetch request: SRFetchRequest) {
    print("获取完成: \(reader.sensor)")
}

func sensorReader(
    _ reader: SRSensorReader,
    fetching request: SRFetchRequest,
    failedWithError error: any Error
) {
    print("获取失败: \(error)")
}
```

将 `result.sample` 转换为读取器传感器的样本形状。某些流返回每个结果一个对象，而录制的运动、ECG、PPG 和环境压力流可以返回记录样本的数组。

### 数据保留期

SensorKit 对新录制的数据施加 **24 小时保留期**。时间范围与该保留期重叠的获取请求将返回无结果。围绕此延迟设计数据收集工作流。

## SRDevice

`SRDevice` 识别传感器样本的硬件来源。使用它来区分来自 iPhone 的数据与来自 Apple Watch 的数据。

```swift
// 获取当前设备
let currentDevice = SRDevice.current
print("型号: \(currentDevice.model)")
print("系统: \(currentDevice.systemName) \(currentDevice.systemVersion)")

// 获取传感器所有可用设备
reader.fetchDevices()
```

通过委托处理获取的设备：

```swift
func sensorReader(_ reader: SRSensorReader, didFetch devices: [SRDevice]) {
    for device in devices {
        let request = SRFetchRequest()
        request.device = device
        request.from = SRAbsoluteTime(CFAbsoluteTimeGetCurrent() - 86400)
        request.to = SRAbsoluteTime.current()
        reader.fetch(request)
    }
}

func sensorReader(_ reader: SRSensorReader, fetchDevicesDidFailWithError error: any Error) {
    print("获取设备失败: \(error)")
}
```

### SRDevice 属性

| 属性 | 类型 | 描述 |
|---|---|---|
| `model` | `String` | 用户定义的设备名称 |
| `name` | `String` | 框架定义的设备名称 |
| `systemName` | `String` | 操作系统名称 (iOS, watchOS) |
| `systemVersion` | `String` | 操作系统版本 |
| `productType` | `String` | 硬件标识符 |
| `current` | `SRDevice` | 运行设备的类属性 |

## 常见错误

### 不要：在没有权限的情况下尝试使用 SensorKit

在构建生产读取器之前，获取苹果的研究批准、传感器特定的权限值和匹配的手动配置文件。

### 不要：期望立即访问数据

应用
[数据保留期](#数据保留期)；与保留期重叠的获取不是证明录制失败的证据。

### 不要：忘记在获取之前设置委托

在 `startRecording()` 或 `fetch(_:)` 之前分配委托；结果和失败通过委托回调到达。

### 不要：跳过每个请求传感器的 Info.plist 使用详情

为每个请求的传感器添加精确的
[Info.plist 配置](#infoplist-配置) 使用详情条目。

### 不要：忽略 SRError 代码

至少区分 `.invalidEntitlement`、`.noAuthorization`、`.dataInaccessible`、`.fetchRequestInvalid`、`.promptDeclined` 和未知未来代码。加载
[完整委托实现](references/sensorkit-patterns.md#完整委托实现) 以获取完整的 switch 和回调连接。

## 审查清单

- [ ] 在开发之前有苹果批准的研究
- [ ] `com.apple.developer.sensorkit.reader.allow` 权限仅列出所需的传感器
- [ ] 带有明确 App ID 和 SensorKit 功能的手动配置文件
- [ ] Info.plist 中的 `NSSensorKitUsageDescription` 清晰的研究目的
- [ ] Info.plist 中的 `NSSensorKitPrivacyPolicyURL` 有效的隐私政策 URL
- [ ] 每个请求传感器的 `NSSensorKitUsageDetail` 条目
- [ ] `Required` 键根据必要与可选传感器设置适当
- [ ] 在录制之前请求授权，在获取之前检查状态
- [ ] 在调用 `startRecording()` 或 `fetch(_:)` 之前分配委托
- [ ] 获取请求时间范围考虑 24 小时数据保留期
- [ ] 在所有失败委托方法中处理 `SRError` 代码
- [ ] 使用 `fetchDevices()` 在获取之前发现可用设备
- [ ] 数据收集完成时调用 `stopRecording()`
- [] `sensorReader(_:fetching:didFetchResult:)` 返回 `true` 以继续或 `false` 以停止

## 参考资料

- 扩展模式（委托连接、多传感器管理器、样本类型详情）：[references/sensorkit-patterns.md](references/sensorkit-patterns.md)
- [SensorKit 框架](https://sosumi.ai/documentation/sensorkit)
- [SRSensorReader](https://sosumi.ai/documentation/sensorkit/srsensorreader)
- [SRSensor](https://sosumi.ai/documentation/sensorkit/srsensor)
- [SRDevice](https://sosumi.ai/documentation/sensorkit/srdevice)
- [SRFetchRequest](https://sosumi.ai/documentation/sensorkit/srfetchrequest)
- [为传感器读取配置您的项目](https://sosumi.ai/documentation/sensorkit/configuring-your-project-for-sensor-reading)
- [com.apple.developer.sensorkit.reader.allow](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.sensorkit.reader.allow)
