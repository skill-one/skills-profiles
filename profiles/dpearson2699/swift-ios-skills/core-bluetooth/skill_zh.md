# 核心蓝牙

扫描、连接并与蓝牙低功耗（BLE）设备进行数据交换。
涵盖中心角色（扫描和连接到外围设备）、外围角色（广播服务）、后台模式和状态恢复。
使用 `accessorysetupkit` 进行隐私保护的配件发现和设置；使用此技能进行直接 Core Bluetooth GATT 通信。

## 内容

- [设置](#设置)
- [中心角色：扫描](#中心角色扫描)
- [中心角色：连接](#中心角色连接)
- [发现服务和特征](#发现服务和特征)
- [读取、写入和通知](#读取写入和通知)
- [外围角色：广播](#外围角色广播)
- [后台 BLE](#后台-ble)
- [状态恢复](#状态恢复)
- [常见错误](#常见错误)
- [复习清单](#复习清单)
- [参考资料](#参考资料)

## 设置

### Info.plist 键

| 键 | 目的 |
|---|---|
| `NSBluetoothAlwaysUsageDescription` | 必须的。解释为什么应用使用蓝牙 |
| `UIBackgroundModes` with `bluetooth-central` | 后台扫描和连接 |
| `UIBackgroundModes` with `bluetooth-peripheral` | 后台广播 |

### 蓝牙授权

Core Bluetooth 没有明确的权限请求 API。添加
`NSBluetoothAlwaysUsageDescription`，在应用准备好蓝牙访问时创建管理器，然后检查 `manager.authorization` 和 `manager.state`。
将 `.denied` 和 `.restricted` 视为最终状态，直到用户更改设置；在扫描、连接、广播或发布服务之前等待 `.poweredOn`。

## 中心角色：扫描

### 创建中心管理器

始终在扫描之前等待 `poweredOn` 状态。

```swift
import CoreBluetooth

final class BluetoothManager: NSObject, CBCentralManagerDelegate {
    private var centralManager: CBCentralManager!
    private var discoveredPeripheral: CBPeripheral?

    override init() {
        super.init()
        centralManager = CBCentralManager(delegate: self, queue: nil)
    }

    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        guard central.state == .poweredOn else { return }
        startScanning()
    }
}
```

### 扫描外围设备

扫描特定服务 UUID 以节省电量。将 `nil` 传递给发现所有外围设备（不推荐在生产环境中使用）。

```swift
let heartRateServiceUUID = CBUUID(string: "180D")

func startScanning() {
    centralManager.scanForPeripherals(
        withServices: [heartRateServiceUUID],
        options: [CBCentralManagerScanOptionAllowDuplicatesKey: false]
    )
}

func centralManager(
    _ central: CBCentralManager,
    didDiscover peripheral: CBPeripheral,
    advertisementData: [String: Any],
    rssi RSSI: NSNumber
) {
    guard RSSI.intValue > -70 else { return } // 过滤弱信号

    // 重要提示：保留外围设备——否则它将被释放
    discoveredPeripheral = peripheral
    centralManager.stopScan()
    centralManager.connect(peripheral, options: nil)
}
```

## 中心角色：连接

```swift
func centralManager(
    _ central: CBCentralManager,
    didConnect peripheral: CBPeripheral
) {
    peripheral.delegate = self
    peripheral.discoverServices([heartRateServiceUUID])
}

func centralManager(
    _ central: CBCentralManager,
    didDisconnectPeripheral peripheral: CBPeripheral,
    timestamp: CFAbsoluteTime,
    isReconnecting: Bool,
    error: Error?
) {
    if isReconnecting {
        // 系统正在自动重连
        return
    }
    // 处理断开连接——可选地重连
    discoveredPeripheral = nil
}
```

## 发现服务和特征

实现 `CBPeripheralDelegate` 来遍历服务/特征树。

```swift
extension BluetoothManager: CBPeripheralDelegate {
    func peripheral(
        _ peripheral: CBPeripheral,
        didDiscoverServices error: Error?
    ) {
        guard let services = peripheral.services else { return }
        for service in services {
            peripheral.discoverCharacteristics(nil, for: service)
        }
    }

    func peripheral(
        _ peripheral: CBPeripheral,
        didDiscoverCharacteristicsFor service: CBService,
        error: Error?
    ) {
        guard let characteristics = service.characteristics else { return }
        for characteristic in characteristics {
            if characteristic.properties.contains(.notify) {
                peripheral.setNotifyValue(true, for: characteristic)
            }
            if characteristic.properties.contains(.read) {
                peripheral.readValue(for: characteristic)
            }
        }
    }
}
```

## 读取、写入和通知

### 读取值

```swift
func peripheral(
    _ peripheral: CBPeripheral,
    didUpdateValueFor characteristic: CBCharacteristic,
    error: Error?
) {
    guard let data = characteristic.value else { return }

    switch characteristic.uuid {
    case CBUUID(string: "2A37"):
        if let heartRate = parseHeartRate(data) {
            print("心率: \(heartRate) bpm")
        }
    case CBUUID(string: "2A19"):
        let batteryLevel = data.first.map { Int($0) } ?? 0
        print("电量: \(batteryLevel)%")
    default:
        break
    }
}

private func parseHeartRate(_ data: Data) -> Int? {
    guard data.count >= 2 else { return nil }
    let flags = data[0]
    let is16Bit = (flags & 0x01) != 0
    if is16Bit {
        guard data.count >= 3 else { return nil }
        return Int(data[1]) | (Int(data[2]) << 8)
    } else {
        return Int(data[1])
    }
}
```

### 写入值

```swift
func writeValue(_ data: Data, to characteristic: CBCharacteristic,
                on peripheral: CBPeripheral,
                preferResponse: Bool = true) {
    let type: CBCharacteristicWriteType
    if preferResponse, characteristic.properties.contains(.write) {
        type = .withResponse
    } else if characteristic.properties.contains(.writeWithoutResponse),
              peripheral.canSendWriteWithoutResponse {
        type = .withoutResponse
    } else if characteristic.properties.contains(.write) {
        type = .withResponse
    } else {
        return
    }

    guard data.count <= peripheral.maximumWriteValueLength(for: type) else { return }
    peripheral.writeValue(data, for: characteristic, type: type)
}

// .withResponse 写入的确认回调。
func peripheral(
    _ peripheral: CBPeripheral,
    didWriteValueFor characteristic: CBCharacteristic,
    error: Error?
) {
    if let error {
        print("写入失败: \(error.localizedDescription)")
    }
}

// 在这里恢复挂起的 .withoutResponse 写入。
func peripheralIsReady(toSendWriteWithoutResponse peripheral: CBPeripheral) {}
```

### 订阅通知

```swift
// 订阅
peripheral.setNotifyValue(true, for: characteristic)

// 取消订阅
peripheral.setNotifyValue(false, for: characteristic)

// 确认
func peripheral(
    _ peripheral: CBPeripheral,
    didUpdateNotificationStateFor characteristic: CBCharacteristic,
    error: Error?
) {
    if characteristic.isNotifying {
        print("现在接收 \(characteristic.uuid) 的通知")
    }
}
```

## 外围角色：广播

使用 `CBPeripheralManager` 发布本地设备的服務。

```swift
final class BLEPeripheralManager: NSObject, CBPeripheralManagerDelegate {
    private var peripheralManager: CBPeripheralManager!
    private let serviceUUID = CBUUID(string: "12345678-1234-1234-1234-123456789ABC")
    private let charUUID = CBUUID(string: "12345678-1234-1234-1234-123456789ABD")

    override init() {
        super.init()
        peripheralManager = CBPeripheralManager(delegate: self, queue: nil)
    }

    func peripheralManagerDidUpdateState(_ peripheral: CBPeripheralManager) {
        guard peripheral.state == .poweredOn else { return }
        setupService()
    }

    private func setupService() {
        let characteristic = CBMutableCharacteristic(
            type: charUUID,
            properties: [.read, .notify],
            value: nil,
            permissions: [.readable]
        )

        let service = CBMutableService(type: serviceUUID, primary: true)
        service.characteristics = [characteristic]
        peripheralManager.add(service)
    }

    func peripheralManager(
        _ peripheral: CBPeripheralManager,
        didAdd service: CBService,
        error: Error?
    ) {
        guard error == nil else { return }
        peripheralManager.startAdvertising([
            CBAdvertisementDataServiceUUIDsKey: [serviceUUID],
            CBAdvertisementDataLocalNameKey: "MyDevice"
        ])
    }
}
```

## 后台 BLE

### 后台中心模式

将 `bluetooth-central` 添加到 `UIBackgroundModes`。在后台：

- 扫描必须指定一个或多个服务 UUID；`nil` 扫描仅在前景中有效
- 扫描选项，包括 `CBCentralManagerScanOptionAllowDuplicatesKey`，不起作用

### 后台外围模式

将 `bluetooth-peripheral` 添加到 `UIBackgroundModes`。在后台：

- 没有此模式，发布的服务内容在挂起时被禁用
- 本地名称不会被广播
- 服务 UUID 移动到溢出区域，需要显式服务扫描

## 状态恢复

状态恢复允许系统在应用终止并重新启动以处理 BLE 事件时重新创建您的中心或外围管理器。

### 中心管理器状态恢复

```swift
// 1. 使用恢复标识符创建
centralManager = CBCentralManager(
    delegate: self,
    queue: nil,
    options: [CBCentralManagerOptionRestoreIdentifierKey: "myCentral"]
)

// 2. 实现恢复委托方法
func centralManager(
    _ central: CBCentralManager,
    willRestoreState dict: [String: Any]
) {
    if let peripherals = dict[CBCentralManagerRestoredStatePeripheralsKey]
        as? [CBPeripheral] {
        for peripheral in peripherals {
            // 重新分配委托并保留
            peripheral.delegate = self
            discoveredPeripheral = peripheral
        }
    }
    let restoredServices = dict[CBCentralManagerRestoredStateScanServicesKey]
        as? [CBUUID]
    let restoredOptions = dict[CBCentralManagerRestoredStateScanOptionsKey]
        as? [String: Any]
    // 如果仍然需要，使用 restoredServices/restoredOptions 继续扫描。
}
```

### 外围管理器状态恢复

```swift
peripheralManager = CBPeripheralManager(
    delegate: self,
    queue: nil,
    options: [CBPeripheralManagerOptionRestoreIdentifierKey: "myPeripheral"]
)

func peripheralManager(
    _ peripheral: CBPeripheralManager,
    willRestoreState dict: [String: Any]
) {
    let services = dict[CBPeripheralManagerRestoredStateServicesKey]
        as? [CBMutableService]
    let advertisement = dict[CBPeripheralManagerRestoredStateAdvertisementDataKey]
        as? [String: Any]
    // 根据需要将应用状态恢复到保留的服务/广告。
}
```

## 常见错误

| 错误 | 修复 |
|---|---|
| 在 `.poweredOn` 之前扫描/连接 | 从 `centralManagerDidUpdateState` 开始 BLE 工作。 |
| 未保留发现的外围设备 | 通过连接和发现保留强引用。 |
| 生产扫描传递 `nil` 服务 | 通过服务 UUID 过滤功能需要的。 |
| 在 `didConnect` 之前开始服务发现 | 仅从委托回调中前进，并处理失败/断开连接路径。 |
| 写入忽略特征属性或有效载荷限制 | 选择支持的写入类型，尊重 `maximumWriteValueLength`，并在 `canSendWriteWithoutResponse` 上限制 `.withoutResponse`。 |

## 复习清单

- [ ] `NSBluetoothAlwaysUsageDescription` 添加到 Info.plist
- [ ] 所有 BLE 操作在 `centralManagerDidUpdateState` 返回 `.poweredOn` 时进行
- [ ] 使用强引用保留发现的外围设备
- [ ] 生产扫描使用特定服务 UUID（不是 `nil`）
- [ ] 在调用 `discoverServices` 之前设置 `CBPeripheralDelegate`
- [ ] 在读取/写入/通知之前检查特征属性
- [ ] 写入有效载荷保持在 `maximumWriteValueLength(for:)` 内
- [ ] `.withoutResponse` 写入尊重 `canSendWriteWithoutResponse`
- [ ] 如果需要，添加后台模式 (`bluetooth-central` 或 `bluetooth-peripheral`)
- [ ] 如果应用需要重新启动以处理 BLE 事件的支持，设置状态恢复标识符
- [ ] 使用状态恢复时实现 `willRestoreState` 委托方法
- [ ] 扫描发现目标外围设备后停止扫描
- [ ] 处理断开连接，可选地使用自动重连逻辑
- [ ] 写入类型匹配特征属性（`.withResponse` vs `.withoutResponse`）

## 参考资料

- 扩展模式（重连策略、数据解析、SwiftUI 集成）：[references/ble-patterns.md](references/ble-patterns.md)
- [Core Bluetooth 框架](https://sosumi.ai/documentation/corebluetooth)
- [CBCentralManager](https://sosumi.ai/documentation/corebluetooth/cbcentralmanager)
- [CBPeripheral](https://sosumi.ai/documentation/corebluetooth/cbperipheral)
- [CBPeripheralManager](https://sosumi.ai/documentation/corebluetooth/cbperipheralmanager)
- [CBService](https://sosumi.ai/documentation/corebluetooth/cbservice)
- [CBCharacteristic](https://sosumi.ai/documentation/corebluetooth/cbcharacteristic)
- [CBUUID](https://sosumi.ai/documentation/corebluetooth/cbuuid)
- [CBCentralManagerDelegate](https://sosumi.ai/documentation/corebluetooth/cbcentralmanagerdelegate)
- [CBPeripheralDelegate](https://sosumi.ai/documentation/corebluetooth/cbperipheraldelegate)
- [NSBluetoothAlwaysUsageDescription](https://sosumi.ai/documentation/bundleresources/information-property-list/nsbluetoothalwaysusagedescription)
- [CBManagerAuthorization](https://sosumi.ai/documentation/corebluetooth/cbmanagerauthorization)
- [scanForPeripherals(withServices:options:)](https://sosumi.ai/documentation/corebluetooth/cbcentralmanager/scanforperipherals(withservices:options:))
- [startAdvertising(_:)](https://sosumi.ai/documentation/corebluetooth/cbperipheralmanager/startadvertising(_:))
- [writeValue(_:for:type:)](https://sosumi.ai/documentation/corebluetooth/cbperipheral/writevalue(_:for:type:))
- [maximumWriteValueLength(for:)](https://sosumi.ai/documentation/corebluetooth/cbperipheral/maximumwritevaluelength(for:))
- [canSendWriteWithoutResponse](https://sosumi.ai/documentation/corebluetooth/cbperipheral/cansendwritewithoutresponse)
- [配置后台执行模式](https://sosumi.ai/documentation/xcode/configuring-background-execution-modes)
