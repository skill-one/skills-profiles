---
name: audioaccessorykit
description: 支持通过AudioAccessoryKit自动切换配对的第三方蓝牙耳机或耳塞。在以下情况使用：当伴侣应用注册音频配件、应用扩展报告佩戴/移除位置或连接源设备变化，或需要处理配件控制设备功能与错误时。不应用于一般AVAudioSession路由、蓝牙传输或初始配件配对。
---

# 音频配件套件

支持自动音频切换和第三方音频配件的智能音频路由输入。使配套应用能够向系统注册音频配件配置，并使应用扩展能够报告放置和连接源的变化，以帮助系统切换音频输出。支持 iOS 26.4+ / iPadOS 26.4+。

> **注意：** AudioAccessoryKit 是 iOS 26.4 中的新功能。在依赖特定 API 细节之前，请先重新检查当前的 Apple 文档。

AudioAccessoryKit 基于AccessorySetupKit 构建。配件必须首先通过AccessorySetupKit 进行配对，然后才能注册音频功能。中心类型是 `AccessoryControlDevice`，它注册来自容器应用的 `Configuration`，并从应用扩展中应用持续的配置更新。

## 内容

- [设置](#设置)
- [会话管理](#会话管理)
- [音频切换](#音频切换)
- [设备放置](#设备放置)
- [连接的音频源](#连接的音频源)
- [功能发现](#功能发现)
- [错误处理](#错误处理)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 设置

### 前置条件

1. 使用 AccessorySetupKit 通过蓝牙配对配件。这将生成一个 `ASAccessory` 对象。
2. 在容器应用和扩展中按需导入框架：

```swift
import AccessorySetupKit
import AudioAccessoryKit
```

### 框架可用性

| 平台 | 最低版本 |
|---|---|
| iOS | 26.4+ |
| iPadOS | 26.4+ |

在当前的 Xcode 26.6 工具链中，AudioAccessoryKit 存在于设备 SDK 中，但不在 iPhone 模拟器 26.5 SDK 中。为此目标使用物理设备目标。如果其余应用必须为模拟器构建，请隔离目标成员资格或使用 `#if canImport(AudioAccessoryKit)` 包围导入和实现，并提供模拟器桩。

## 会话管理

### 注册配件

通过 AccessorySetupKit 配对后，从容器应用通过传递一个描述配件支持的功能和任何初始状态的 `AccessoryControlDevice.Configuration` 来注册配件：

```swift
let accessory: ASAccessory  // 从 AccessorySetupKit 配对获得

let configuration = AccessoryControlDevice.Configuration(
    devicePlacement: .offHead,
    deviceCapabilities: [.audioSwitching, .placement]
)

try await AccessoryControlDevice.register(accessory, configuration)
```

注册会激活指定的功能，并给系统提供参与音频路由决策所需的配置。

### 获取当前配置

在应用扩展中，使用静态 `current(for:)` 方法访问设备的当前配置：

```swift
let device = try AccessoryControlDevice.current(for: accessory)
let currentConfig = device.configuration
```

这将返回与配对的 `ASAccessory` 关联的 `AccessoryControlDevice` 实例。设备同时暴露 `accessory` 引用和当前 `configuration`。Apple 将 `current(for:)` 标记为仅限应用扩展。

### 更新配置

在应用扩展中，使用 `update(_:)` 将配置更改推送到系统：

```swift
let device = try AccessoryControlDevice.current(for: accessory)
var config = device.configuration

config.devicePlacement = .onHead
try await device.update(config)
```

将其视为受限制的写入工作流：确认注册声明了功能，复制并修改 `device.configuration`，然后 `try await update(_:)`。该方法不返回配置值；只有在调用成功后才更新应用侧镜像。失败时，请使用 [错误处理](#错误处理) 中的处置方式。Apple 将 `update(_:)` 标记为仅限应用扩展。

## 音频切换

自动音频切换允许系统根据放置和连接源智能地将音频输出路由到正确的设备。

### 启用音频切换

在上述规范注册流程中声明 `.audioSwitching`。仅在配件可以报告持续的放置变化时，才包含 `.placement` 和初始放置。

### 功能

自动切换通常使用这些 `AccessoryControlDevice.Capabilities`：

| 功能 | 目的 |
|---|---|
| `.audioSwitching` | 设备支持自动音频切换 |
| `.placement` | 设备可以报告其物理放置 |

按需组合功能。除非配件可以持续向系统更新真实的放置状态，否则不要声明 `.placement`。

## 设备放置

从应用扩展报告配件的物理位置，以帮助系统做出路由决策。每当配件检测到位置变化时，请更新放置。

### 放置值

`AccessoryControlDevice.Placement` 定义了四个情况：

| 放置 | 含义 |
|---|---|
| `.inEar` | 配件已放置在耳中（例如，耳塞） |
| `.onHead` | 配件在头上（例如，头带耳机） |
| `.overTheEar` | 配件在耳上（例如，头戴式耳机） |
| `.offHead` | 配件未被佩戴 |

### 更新放置

```swift
config.devicePlacement = .inEar
```

在上述规范当前→复制→更新序列中应用此突变。

常见转换：

- 用户戴上配件时，从 `.offHead` 到 `.onHead` 或 `.inEar`
- 从 `.onHead` 或 `.inEar` 到 `.offHead` 时移除
- 及时更新每个检测到的变化，以实现响应式音频路由

## 连接的音频源

对于可以同时连接到多个蓝牙设备的配件，从应用扩展中通知系统哪些设备已连接。这允许系统从正确的源路由音频。

### 设置音频源标识符

将连接的设备的蓝牙地址作为 `Data` 提供：

```swift
let primaryBTAddress = Data([0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC])
config.primaryAudioSourceDeviceIdentifier = primaryBTAddress

let secondaryBTAddress = Data([0xAB, 0xCD, 0xEF, 0x01, 0x23, 0x45])
config.secondaryAudioSourceDeviceIdentifier = secondaryBTAddress
```

在蓝牙连接状态发生变化（新设备连接，现有设备断开连接）时更新这些标识符，然后调用规范的 `update(_:)` 序列。

### 配置属性

自动切换使用这些配置字段：

| 属性 | 类型 | 目的 |
|---|---|---|
| `deviceCapabilities` | `Capabilities` | 声明的设备功能 |
| `devicePlacement` | `Placement?` | 当前物理放置 |
| `primaryAudioSourceDeviceIdentifier` | `Data?` | 主要连接的蓝牙设备地址 |
| `secondaryAudioSourceDeviceIdentifier` | `Data?` | 次要连接的蓝牙设备地址 |

## 功能发现

### 查询功能

在应用扩展中，通过其配置检查设备的声明功能：

```swift
let device = try AccessoryControlDevice.current(for: accessory)
let caps = device.configuration.deviceCapabilities

if caps.contains(.audioSwitching) {
    // 设备支持自动音频切换
}

if caps.contains(.placement) {
    // 设备报告物理放置
}
```

### 检查放置

读取当前放置以确定配件是否正在佩戴：

```swift
let device = try AccessoryControlDevice.current(for: accessory)

if let placement = device.configuration.devicePlacement {
    switch placement {
    case .inEar, .onHead, .overTheEar:
        // 配件正在佩戴
        break
    case .offHead:
        // 配件未被佩戴
        break
    @unknown default:
        break
    }
}
```

## 错误处理

`AccessoryControlDevice.Error` 涵盖注册和更新期间的失败情况：

| 错误 | 原因 |
|---|---|
| `.accessoryNotCapable` | 配件不支持请求的功能 |
| `.invalidRequest` | 请求参数无效 |
| `.invalidated` | 设备注册已被失效 |
| `.unknown` | 发生了未指定的错误 |

处理注册和更新调用的错误：

```swift
let configuration = AccessoryControlDevice.Configuration(
    devicePlacement: .offHead,
    deviceCapabilities: [.audioSwitching, .placement]
)

do {
    try await AccessoryControlDevice.register(accessory, configuration)
} catch let error as AccessoryControlDevice.Error {
    switch error {
    case .accessoryNotCapable:
        // 配件硬件不支持请求的功能
        break
    case .invalidRequest:
        // 检查注册参数
        break
    case .invalidated:
        // 再次协调容器应用的注册
        break
    case .unknown:
        // 记录、暴露或传播；Apple 不将此分类为暂时性错误
        throw error
    @unknown default:
        throw error
    }
}
```

不要推断 `.invalidated` 或 `.unknown` 是暂时性的。正确处理无效功能或请求参数，丢弃失效的句柄并通知容器应用重新评估注册，以及暴露未指定的错误。加载 [错误恢复模式](references/audioaccessorykit-patterns.md#error-recovery-patterns) 以获取完整的处置和失效交接。

## 常见错误

### 不要：在通过 AccessorySetupKit 配对之前注册

仅注册 AccessorySetupKit 配对返回的 `ASAccessory`。

### 不要：在未更新放置的情况下声明放置功能

如果注册声明了 `.placement`，扩展必须在每个检测到的转换上使用规范更新序列更新放置。

### 不要：忽略多设备配件的连接状态变化

每当蓝牙连接发生变化时，请清除或替换主要和次要源标识符；过时的标识符会降低切换的准确性。

### 不要：忘记处理失效错误

```swift
// 错误——忽略失效，继续使用过时的设备引用
try await device.update(config)  // 抛出 .invalidated，未处理

// 正确——丢弃句柄，并让容器重新评估注册
do {
    try await device.update(config)
} catch AccessoryControlDevice.Error.invalidated {
    await notifyContainerAppToReevaluateRegistration(accessory)
}
```

## 审查清单

- [ ] 在 AudioAccessoryKit 注册之前通过 AccessorySetupKit 配对配件
- [ ] 导入了 `AccessorySetupKit` 和 `AudioAccessoryKit`
- [ ] 容器应用调用 `register(_: _:)` 并传递 `AccessoryControlDevice.Configuration`
- [ ] 应用扩展调用 `current(for:)` 和 `update(_:)`
- [ ] 注册配置中的功能与实际硬件支持匹配
- [ ] 更新仅触及注册期间声明的功能字段
- [ ] `.placement` 功能伴随着持续的放置更新
- [ ] 放置转换（头上有/头下）及时报告
- [ ] 音频源设备标识符在蓝牙连接变化时更新
- [ ] 处理所有 `AccessoryControlDevice.Error` 情况，包括 `@unknown default`
- [ ] `update(_:)` 调用使用 `try await` 并处理错误
- [ ] 失效的设备引用触发容器应用注册恢复
- [ ] 部署目标设置为 iOS 26.4+ 或 iPadOS 26.4+

## 参考资料

- 扩展模式（注册流程、放置监控、多设备协调）：[references/audioaccessorykit-patterns.md](references/audioaccessorykit-patterns.md)
- [AudioAccessoryKit 框架](https://sosumi.ai/documentation/audioaccessorykit)
- [支持自动音频切换](https://sosumi.ai/documentation/audioaccessorykit/supporting-automatic-audio-switching)
- [AccessoryControlDevice](https://sosumi.ai/documentation/audioaccessorykit/accessorycontroldevice)
- [AccessoryControlDevice 注册](https://sosumi.ai/documentation/audioaccessorykit/accessorycontroldevice/register%28_%3A_%3A%29)
- [AccessoryControlDevice 查找](https://sosumi.ai/documentation/audioaccessorykit/accessorycontroldevice/current%28for%3A%29)
- [AccessoryControlDevice 更新](https://sosumi.ai/documentation/audioaccessorykit/accessorycontroldevice/update%28_%3A%29)
- [AccessoryControlDevice.Configuration](https://sosumi.ai/documentation/audioaccessorykit/accessorycontroldevice/configuration-swift.struct)
- [AccessoryControlDevice.Capabilities](https://sosumi.ai/documentation/audioaccessorykit/accessorycontroldevice/capabilities)
- [AccessoryControlDevice.Placement](https://sosumi.ai/documentation/audioaccessorykit/accessorycontroldevice/placement)
- [AccessorySetupKit 框架](https://sosumi.ai/documentation/accessorysetupkit)（配对的先决条件）
