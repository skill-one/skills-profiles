# HomeKit

控制智能家居配件并配置 Matter 设备。HomeKit 管理
家庭/房间/配件模型、操作集和触发器。MatterSupport 处理设备配置到您的生态系统中。

## 内容

- [设置](#设置)
- [HomeKit 数据模型](#homekit-数据模型)
- [管理配件](#管理配件)
- [读取和写入特征](#读取和写入特征)
- [操作集和触发器](#操作集和触发器)
- [Matter 配置](#matter-配置)
- [MatterAddDeviceExtensionRequestHandler](#matteradddeviceextensionrequesthandler)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 设置

### HomeKit 配置

1. 在 Xcode 中启用 **HomeKit** 功能（签名与能力）
2. 向 Info.plist 添加 `NSHomeKitUsageDescription`：

```xml
<key>NSHomeKitUsageDescription</key>
<string>此应用控制您的智能家居配件。</string>
```

### MatterSupport 配置

用于将 Matter 配置到您自己的生态系统中：

1. 添加一个 **MatterSupport 扩展** 目标，并将其主类设置为
   `MatterAddDeviceExtensionRequestHandler` 子类
2. 添加 `_matter._tcp`、`_matterc._udp` 和
   `_matterd._udp` 的 `NSBonjourServices` 条目
3. 仅当调用者以编程方式提供 Matter 配置有效负载时，才添加
   `com.apple.developer.matter.allow-setup-payload`

### 框架边界

| 需要 | 框架 |
|---|---|
| 家庭、房间、配件、特征、操作、触发器 | HomeKit |
| 将 Matter 配置到应用生态系统中 | MatterSupport |
| 选择并授权附近的蓝牙或 Wi-Fi 配件 | AccessorySetupKit |
| 选择后交换蓝牙 GATT 数据 | CoreBluetooth |
| 选择后加入或配置配件的 Wi-Fi 网络 | NetworkExtension |

## HomeKit 数据模型

HomeKit 以层次结构组织智能家居自动化：

```text
HMHomeManager
  -> HMHome (一个或多个)
       -> HMRoom (家庭中的房间)
            -> HMAccessory (房间中的设备)
                 -> HMService (功能：灯光、恒温器等)
                      -> HMCharacteristic (可读/可写的值)
       -> HMZone (房间的组)
       -> HMActionSet (分组操作)
       -> HMTrigger (基于时间或事件的触发器)
```

### 初始化家庭管理器

创建一个 `HMHomeManager` 并实现代理以知道何时数据已加载。HomeKit 异步加载——在代理触发之前不要访问 `homes`。

```swift
import HomeKit

final class HomeStore: NSObject, HMHomeManagerDelegate {
    let homeManager = HMHomeManager()

    override init() {
        super.init()
        homeManager.delegate = self
    }

    func homeManagerDidUpdateHomes(_ manager: HMHomeManager) {
        // 现在可以安全地访问 manager.homes
        let homes = manager.homes
        let primaryHome = manager.primaryHome
        print("加载了 \(homes.count) 个家庭")
    }

    func homeManager(
        _ manager: HMHomeManager,
        didUpdate status: HMHomeManagerAuthorizationStatus
    ) {
        if status.contains(.authorized) {
            print("HomeKit 访问已授权")
        }
    }
}
```

### 访问房间

```swift
guard let home = homeManager.primaryHome else { return }

let rooms = home.rooms
let kitchen = rooms.first { $0.name == "Kitchen" }

// 未分配到特定房间的配件的房间
let defaultRoom = home.roomForEntireHome()
```

## 管理配件

### 发现和添加配件

在添加配件之前使用 [框架边界](#框架边界) 表；在此技能中仅 HomeKit/MatterSupport 工作继续。

```swift
// 系统界面用于配件发现
home.addAndSetupAccessories { error in
    if let error {
        print("设置失败：\(error)")
    }
}
```

### 列出配件和服务

```swift
for accessory in home.accessories {
    print("\(accessory.name) 在 \(accessory.room?.name ?? "未分配")")

    for service in accessory.services {
        print("  服务：\(service.serviceType)")

        for characteristic in service.characteristics {
            print("    \(characteristic.characteristicType)：\(characteristic.value ?? "nil")")
        }
    }
}
```

### 将配件移动到房间

```swift
guard let accessory = home.accessories.first,
      let bedroom = home.rooms.first(where: { $0.name == "Bedroom" }) else { return }

home.assignAccessory(accessory, to: bedroom) { error in
    if let error {
        print("移动配件失败：\(error)")
    }
}
```

## 读取和写入特征

### 读取值

```swift
let characteristic: HMCharacteristic = // 从服务中获取

characteristic.readValue { error in
    guard error == nil else { return }
    if let value = characteristic.value as? Bool {
        print("电源状态：\(value)")
    }
}
```

### 写入值

```swift
// 打开灯光
characteristic.writeValue(true) { error in
    if let error {
        print("写入失败：\(error)")
    }
}
```

### 观察变化

启用通知以获取实时更新：

```swift
characteristic.enableNotification(true) { error in
    guard error == nil else { return }
}

// 在 HMAccessoryDelegate 中：
func accessory(
    _ accessory: HMAccessory,
    service: HMService,
    didUpdateValueFor characteristic: HMCharacteristic
) {
    print("更新：\(characteristic.value ?? "nil")")
}
```

## 操作集和触发器

### 创建操作集

`HMActionSet` 将一起执行的特性写入分组：

```swift
home.addActionSet(withName: "晚安") { actionSet, error in
    guard let actionSet, error == nil else { return }

    // 关闭客厅灯光
    let lightChar = livingRoomLight.powerCharacteristic
    let action = HMCharacteristicWriteAction(
        characteristic: lightChar,
        targetValue: false as NSCopying
    )
    actionSet.addAction(action) { error in
        guard error == nil else { return }
        print("操作已添加到晚安场景")
    }
}
```

### 执行操作集

```swift
home.executeActionSet(actionSet) { error in
    if let error {
        print("执行失败：\(error)")
    }
}
```

### 创建定时触发器

```swift
var timeOfDay = DateComponents()
timeOfDay.hour = 22
timeOfDay.minute = 30

let firstFireDate = Calendar.current.nextDate(
    after: Date(),
    matching: timeOfDay,
    matchingPolicy: .nextTime
)!

let trigger = HMTimerTrigger(
    name: "夜间",
    fireDate: firstFireDate,
    recurrence: DateComponents(day: 1)  // 在 firstFireDate 后每天重复
)

home.addTrigger(trigger) { error in
    guard error == nil else { return }

    // 将操作集附加到触发器
    trigger.addActionSet(goodNightActionSet) { error in
        guard error == nil else { return }

        trigger.enable(true) { error in
            print("触发器启用：\(error == nil)")
        }
    }
}
```

### 创建事件触发器

```swift
let motionDetected = HMCharacteristicEvent(
    characteristic: motionSensorCharacteristic,
    triggerValue: true as NSCopying
)

let eventTrigger = HMEventTrigger(
    name: "运动灯光",
    events: [motionDetected],
    predicate: nil
)

home.addTrigger(eventTrigger) { error in
    // 如上添加操作集
}
```

## Matter 配置

使用 `MatterAddDeviceRequest` 将 Matter 设备配置到您的生态系统中。
这与 `HMHome` 家庭自动化模型是分开的；它处理 Matter 设置流程并调用您的 MatterSupport 扩展。

### 基本配置

```swift
import MatterSupport

func addMatterDevice() async throws {
    guard MatterAddDeviceRequest.isSupported else {
        print("此设备不支持 Matter")
        return
    }

    let topology = MatterAddDeviceRequest.Topology(
        ecosystemName: "我的智能家居",
        homes: [
            MatterAddDeviceRequest.Home(displayName: "主屋")
        ]
    )

    let request = MatterAddDeviceRequest(
        topology: topology,
        setupPayload: nil,
        showing: .allDevices
    )

    // 显示设备配对系统界面
    try await request.perform()
}
```

当直接提供设置码时，导入 Matter 并将一个
`MTRSetupPayload` 作为 `setupPayload` 传递；这是需要设置-有效负载权限的情况。

### 过滤设备

```swift
// 仅显示来自特定供应商的设备
let criteria = MatterAddDeviceRequest.DeviceCriteria.vendorID(0x1234)

let request = MatterAddDeviceRequest(
    topology: topology,
    setupPayload: nil,
    showing: criteria
)
```

使用 `.all([.vendorID(...), .not(.productID(...))])` 或
使用 `.any(...)` 当任何一个标准就足够时组合标准。

## MatterAddDeviceExtensionRequestHandler

为完整的生态系统支持，创建一个 MatterSupport 扩展。该扩展处理配置回调。重写所需的方法，但不要从这些重写中调用 `super`。
加载完整的 [高级 Matter 扩展处理器](references/matter-commissioning.md#advanced-matter-extension-handler)
用于凭证验证、房间选择、配置、配置和网络关联覆盖。

## 常见错误

| 错误 | 修复 |
|---|---|
| 在代理更新之前读取家庭 | 创建一个管理器，设置其代理，并等待 `homeManagerDidUpdateHomes`。 |
| 使用 HomeKit 设置进行 Matter 生态系统配置 | 使用 `MatterAddDeviceRequest` 加上配置的 MatterSupport 扩展。 |
| Matter 配置不完整 | 仅在适用时验证主处理器、Bonjour 服务和设置-有效负载权限。 |
| 多个 `HMHomeManager` 实例加载数据库 | 共享一个保留的管理器/存储。 |
| 写入特征时忽略元数据 | 在写入之前检查权限、格式、最小/最大/步长和允许值。 |

## 审查清单

- [ ] Xcode 中启用了 HomeKit 功能
- [ ] Info.plist 中存在 `NSHomeKitUsageDescription`
- [ ] 应用程序跨多个实例共享一个 `HMHomeManager` 实例
- [ ] 实现了 `HMHomeManagerDelegate`；在 `homeManagerDidUpdateHomes` 之前不访问 homes
- [ ] 在家庭上设置了 `HMHomeDelegate` 以接收配件和房间更改
- [ ] 在配件上设置了 `HMAccessoryDelegate` 以接收特征更新
- [ ] 在写入值之前检查特征元数据
- [ ] 所有完成处理程序中都进行了错误处理
- [ ] 配置了 MatterSupport 扩展目标和主处理器
- [] 添加了 Matter 发现 `NSBonjourServices` 条目
- [] 仅在提供设置码时使用
   `com.apple.developer.matter.allow-setup-payload`
- [] 在执行请求之前检查 `MatterAddDeviceRequest.isSupported`
- [] Matter 扩展处理器实现了
   `commissionDevice(in:onboardingPayload:commissioningID:)`
- [] 在发货前使用 HomeKit Accessory Simulator 测试操作集
- [] 创建后启用触发器 (`trigger.enable(true)`) 

## 参考资料

- 扩展模式（Matter 扩展、代理连接、SwiftUI）：[references/matter-commissioning.md](references/matter-commissioning.md)
- [HomeKit 框架](https://sosumi.ai/documentation/homekit)
- [HMHomeManager](https://sosumi.ai/documentation/homekit/hmhomemanager)
- [HMHome](https://sosumi.ai/documentation/homekit/hmhome)
- [HMAccessory](https://sosumi.ai/documentation/homekit/hmaccessory)
- [HMRoom](https://sosumi.ai/documentation/homekit/hmroom)
- [HMActionSet](https://sosumi.ai/documentation/homekit/hmactionset)
- [HMTrigger](https://sosumi.ai/documentation/homekit/hmtrigger)
- [MatterSupport 框架](https://sosumi.ai/documentation/mattersupport)
- [MatterAddDeviceRequest](https://sosumi.ai/documentation/mattersupport/matteradddevicerequest)
- [MatterAddDeviceExtensionRequestHandler](https://sosumi.ai/documentation/mattersupport/matteradddeviceextensionrequesthandler)
- [在您的应用中启用 HomeKit](https://sosumi.ai/documentation/homekit/enabling-homekit-in-your-app)
- [将 Matter 支持添加到您的生态系统](https://sosumi.ai/documentation/mattersupport/adding-matter-support-to-your-ecosystem)
