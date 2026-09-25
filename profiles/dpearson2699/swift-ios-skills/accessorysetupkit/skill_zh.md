# AccessorySetupKit

使用 iOS 18+ 系统选择器进行隐私保护的蓝牙/Wi-Fi 外设发现和授权，然后将通信交给 CoreBluetooth 或 NetworkExtension。

## 内容

- [设置和权限](#设置和权限)
- [发现描述符](#发现描述符)
- [显示选择器](#显示选择器)
- [事件处理](#事件处理)
- [蓝牙外设](#蓝牙外设)
- [Wi-Fi 外设](#wi-fi 外设)
- [从 CoreBluetooth 迁移](#从 corebluetooth 迁移)
- [常见错误](#常见错误)
- [检查清单](#检查清单)
- [参考资料](#参考资料)

## 设置和权限

### Info.plist 配置

将以下键添加到应用的 Info.plist 中：

| 键 | 类型 | 目的 |
|---|---|---|
| `NSAccessorySetupSupports` | `[String]` | 必须的。包含 `Bluetooth` 和/或 `WiFi` 的数组 |
| `NSAccessorySetupBluetoothServices` | `[String]` | 应用发现的服务 UUID（蓝牙） |
| `NSAccessorySetupBluetoothNames` | `[String]` | 要匹配的蓝牙名称或子字符串 |
| `NSAccessorySetupBluetoothCompanyIdentifiers` | `[String]` | 两字节的蓝牙公司标识符 |

蓝牙特定键必须与 `ASDiscoveryDescriptor` 中使用的值匹配。如果应用使用 Info.plist 中未声明的标识符、名称或服务，则在 AccessorySetupKit 发现期间应用会崩溃。对于 Wi-Fi 外设，在 `NSAccessorySetupSupports` 中包含 `WiFi` 并匹配描述符的 SSID 规则。

### 无需蓝牙权限

当应用声明 `NSAccessorySetupSupports` 包含 `Bluetooth` 时，创建 `CBCentralManager` 将不再触发系统蓝牙权限对话框。只有当应用通过 AccessorySetupKit 至少配对一个外设时，中央管理器的状态才会变为 `poweredOn`。

## 发现描述符

`ASDiscoveryDescriptor` 定义查找外设的匹配标准。系统将扫描结果与描述符中的所有规则进行匹配，以筛选出目标外设。

### 蓝牙描述符

```swift
import AccessorySetupKit
import CoreBluetooth

var descriptor = ASDiscoveryDescriptor()
descriptor.bluetoothServiceUUID = CBUUID(string: "12345678-1234-1234-1234-123456789ABC")
descriptor.bluetoothNameSubstring = "MyDevice"
descriptor.bluetoothRange = .immediate  // 仅附近设备
```

蓝牙描述符至少需要一个 `bluetoothCompanyIdentifier` 或 `bluetoothServiceUUID`。根据需要添加更精确的匹配器：

- `bluetoothNameSubstring` 与公司标识符或服务 UUID
- `bluetoothManufacturerDataBlob` 和 `bluetoothManufacturerDataMask` 与公司标识符；blob 和 mask 必须具有相同的长度
- `bluetoothServiceDataBlob` 和 `bluetoothServiceDataMask` 与服务 UUID；blob 和 mask 必须具有相同的长度

### Wi-Fi 描述符

```swift
var descriptor = ASDiscoveryDescriptor()
descriptor.ssid = "MyAccessory-Network"
// 或者使用前缀：
// descriptor.ssidPrefix = "MyAccessory-"
```

提供 `ssid` 或 `ssidPrefix`，不能同时提供。如果两者都设置，应用会崩溃。`ssidPrefix` 必须具有非零长度。

### 蓝牙范围

控制发现所需的物理距离：

| 值 | 行为 |
|---|---|
| `.default` | 标准蓝牙范围 |
| `.immediate` | 仅附近物理外设 |

### 支持选项

在描述符上设置 `supportedOptions` 来声明外设的功能：

```swift
descriptor.supportedOptions = [.bluetoothPairingLE, .bluetoothTransportBridging]
```

| 选项 | 目的 |
|---|---|
| `.bluetoothPairingLE` | BLE 配对支持 |
| `.bluetoothTransportBridging` | 蓝牙传输桥接 |
| `.bluetoothHID` | 蓝牙 HID 设备 |

## 显示选择器

### 创建会话

创建并激活 `ASAccessorySession` 来管理发现生命周期。在读取 `session.accessories` 或显示选择器之前，等待 `.activated`：

```swift
import AccessorySetupKit

final class AccessoryManager {
    private let session = ASAccessorySession()

    func start() {
        session.activate(on: .main) { [weak self] event in
            self?.handleEvent(event)
        }
    }

    private func handleEvent(_ event: ASAccessoryEvent) {
        switch event.eventType {
        case .activated:
            // 会话就绪。检查 session.accessories 以获取之前配对的外设。
            break
        case .accessoryAdded:
            guard let accessory = event.accessory else { return }
            handleAccessoryAdded(accessory)
        case .accessoryChanged:
            // 外设属性更改（例如，设置中更新显示名称）
            break
        case .accessoryRemoved:
            // 用户或应用移除外设
            break
        case .invalidated:
            // 会话失效，无法重用
            break
        @unknown default:
            break
        }
    }
}
```

### 显示选择器

创建具有名称、产品图片和发现描述符的 `ASPickerDisplayItem` 实例，然后将它们传递给激活的会话：

```swift
func showAccessoryPicker() {
    var descriptor = ASDiscoveryDescriptor()
    descriptor.bluetoothServiceUUID = CBUUID(string: "ABCD1234-0000-1000-8000-00805F9B34FB")

    guard let image = UIImage(named: "my-accessory") else { return }

    let item = ASPickerDisplayItem(
        name: "My Bluetooth Accessory",
        productImage: image,
        descriptor: descriptor
    )

    session.showPicker(for: [item]) { error in
        if let error {
            print("Picker failed: \(error.localizedDescription)")
        }
    }
}
```

选择器在单独的系统进程中运行。它将每个匹配的外设显示为单独的项目。当多个外设匹配给定的描述符时，选择器会创建水平轮播。

### 设置选项

根据显示项目配置选择器行为：

```swift
var item = ASPickerDisplayItem(
    name: "My Accessory",
    productImage: image,
    descriptor: descriptor
)
item.setupOptions = [.rename, .confirmAuthorization]
```

| 选项 | 效果 |
|---|---|
| `.rename` | 允许在设置过程中重命名外设 |
| `.confirmAuthorization` | 在设置之前显示授权确认 |
| `.finishInApp` | 指示配对后设置继续在应用中 |

### 产品图片

选择器在 180x120 点容器中显示图片。最佳实践：

- 使用适用于所有屏幕比例的高分辨率图片
- 使用透明背景以正确显示亮/暗模式
- 调整透明边框作为填充以控制外设的显示大小
- 在亮模式和暗模式下测试

## 事件处理

### 事件类型

会话通过事件处理程序传递 `ASAccessoryEvent` 对象：

| 事件 | 当...时 |
|---|---|
| `.activated` | 会话处于活动状态，查询 `session.accessories` |
| `.accessoryAdded` | 用户在选择器中选择外设 |
| `.accessoryChanged` | 外设属性更新（例如，重命名） |
| `.accessoryRemoved` | 外设从系统中移除 |
| `.invalidated` | 会话失效，创建新的会话 |
| `.migrationComplete` | 遗留外设迁移完成 |
| `.pickerDidPresent` | 选择器出现在屏幕上 |
| `.pickerDidDismiss` | 选择器被关闭 |
| `.pickerSetupBridging` | 传输桥接设置正在进行中 |
| `.pickerSetupPairing` | 蓝牙配对正在进行中 |
| `.pickerSetupFailed` | 设置失败 |
| `.pickerSetupRename` | 用户正在重命名外设 |
| `.accessoryDiscovered` | 发现新外设（自定义过滤模式） |

### 协调选择器关闭

当用户选择外设时，`.accessoryAdded` 在 `.pickerDidDismiss` 之前触发。要在选择器关闭后显示自定义设置界面，请在第一个事件中存储外设，并在关闭后处理它：

```swift
private var pendingAccessory: ASAccessory?

private func handleEvent(_ event: ASAccessoryEvent) {
    switch event.eventType {
    case .accessoryAdded:
        pendingAccessory = event.accessory
    case .pickerDidDismiss:
        if let accessory = pendingAccessory {
            pendingAccessory = nil
            beginCustomSetup(accessory)
        }
    @unknown default:
        break
    }
}
```

## 蓝牙外设

通过选择器添加外设后，使用 CoreBluetooth 进行通信。`ASAccessory` 上的 `bluetoothIdentifier` 映射到 `CBPeripheral`。

```swift
import CoreBluetooth

func handleAccessoryAdded(_ accessory: ASAccessory) {
    guard let btIdentifier = accessory.bluetoothIdentifier else { return }

    // 创建 CBCentralManager — 不显示蓝牙权限提示
    let centralManager = CBCentralManager(delegate: self, queue: nil)

    // 接通后，检索外设
    let peripherals = centralManager.retrievePeripherals(
        withIdentifiers: [btIdentifier]
    )
    guard let peripheral = peripherals.first else { return }
    centralManager.connect(peripheral, options: nil)
}
```

要点：

- `CBCentralManager` 状态仅在应用配对外设时变为 `.poweredOn`
- 使用 `scanForPeripherals(withServices:)` 扫描返回仅通过 AccessorySetupKit 配配的外设
- 使用 AccessorySetupKit 时无需 `NSBluetoothAlwaysUsageDescription`

## Wi-Fi 外设

对于 Wi-Fi 外设，`ASAccessory` 上的 `ssid` 标识网络。使用 NetworkExtension 的 `NEHotspotConfiguration` 加入它：

```swift
import NetworkExtension

func handleWiFiAccessoryAdded(_ accessory: ASAccessory) {
    guard let ssid = accessory.ssid else { return }

    let configuration = NEHotspotConfiguration(ssid: ssid)
    NEHotspotConfigurationManager.shared.apply(configuration) { error in
        if let error {
            print("Wi-Fi 加入失败: \(error.localizedDescription)")
        }
    }
}
```

由于外设通过 AccessorySetupKit 发现，加入网络不会触发标准 Wi-Fi 访问提示。

## 从 CoreBluetooth 迁移

使用现有 CoreBluetooth 授权外设的应用可以通过 `ASMigrationDisplayItem` 将它们迁移到 AccessorySetupKit。这是一个一次性操作，用于在新系统中注册已知外设。

```swift
func migrateExistingAccessories() {
    guard let image = UIImage(named: "my-accessory") else { return }

    var descriptor = ASDiscoveryDescriptor()
    descriptor.bluetoothServiceUUID = CBUUID(string: "ABCD1234-0000-1000-8000-00805F9B34FB")

    let migrationItem = ASMigrationDisplayItem(
        name: "My Accessory",
        productImage: image,
        descriptor: descriptor
    )
    // 从 CoreBluetooth 设置外设标识符
    migrationItem.peripheralIdentifier = existingPeripheralUUID

    // 对于 Wi-Fi 外设：
    // migrationItem.hotspotSSID = "MyAccessory-WiFi"

    session.showPicker(for: [migrationItem]) { error in
        if let error {
            print("迁移失败: \(error.localizedDescription)")
        }
    }
}
```

迁移规则：

- 如果 `showPicker` 仅包含迁移项，系统将显示信息页面而不是发现选择器
- 如果迁移项与常规显示项混合，仅在发现并设置新外设时进行迁移
- 迁移完成前不要初始化 `CBCentralManager` — 这样会导致错误并使选择器无法显示
- 迁移完成时，会话接收 `.migrationComplete`

## 常见错误

| 错误 | 修复 |
|---|---|
| 描述符标识符未从 Info.plist 中提供 | 在显示选择器之前声明每个蓝牙服务、名称和公司标识符。 |
| 同时设置了 `ssid` 和 `ssidPrefix` | 选择精确的匹配策略。 |
| CoreBluetooth 在迁移完成前启动 | 等待 `.migrationComplete`，然后创建 `CBCentralManager`。 |
| 选择器没有明确的用户意图出现 | 仅从用户操作中显示它。 |
| 重复使用失效的会话 | 创建、激活并保留新的 `ASAccessorySession`。 |

## 检查清单

- [ ] `NSAccessorySetupSupports` 添加到 Info.plist 并包含 `Bluetooth` 和/或 `WiFi`
- [ ] 在调用 `showPicker` 之前激活会话
- [ ] 事件处理程序使用 `[weak self]` 避免保留循环
- [ ] 处理所有 `ASAccessoryEventType` 案例包括 `@unknown default`
- [ ] 产品图片使用透明背景和适当的分辨率
- [ ] 使用 `ASAccessory` 中的 `bluetoothIdentifier` 或 `ssid` 在设置后连接
- [ ] 处理外设移除事件以清理应用状态

## 参考资料

- 扩展模式（自定义过滤、批量设置、移除处理、错误恢复）：[references/accessorysetupkit-patterns.md](references/accessorysetupkit-patterns.md)
- [AccessorySetupKit 框架](https://sosumi.ai/documentation/accessorysetupkit)
- [ASAccessorySession](https://sosumi.ai/documentation/accessorysetupkit/asaccessorysession)
- [ASDiscoveryDescriptor](https://sosumi.ai/documentation/accessorysetupkit/asdiscoverydescriptor)
- [ASPickerDisplayItem](https://sosumi.ai/documentation/accessorysetupkit/aspickerdisplayitem)
- [ASAccessory](https://sosumi.ai/documentation/accessorysetupkit/asaccessory)
- [ASAccessoryEvent](https://sosumi.ai/documentation/accessorysetupkit/asaccessoryevent)
- [ASMigrationDisplayItem](https://sosumi.ai/documentation/accessorysetupkit/asmigrationdisplayitem)
- [发现和配置外设](https://sosumi.ai/documentation/accessorysetupkit/discovering-and-configuring-accessories)
- [设置和授权蓝牙外设](https://sosumi.ai/documentation/accessorysetupkit/setting-up-and-authorizing-a-bluetooth-accessory)
- [Meet AccessorySetupKit — WWDC24](https://sosumi.ai/videos/play/wwdc2024/10203/)
