---
name: core-bluetooth
description: 使用 Core Bluetooth 构建直接的蓝牙低功耗工作流程。在实现 BLE 中心或外围 GATT 通信、使用 CBCentralManager 扫描或连接、发现服务和特征、使用 CBPeripheral 读取/写入/订阅、使用 CBPeripheralManager 发布本地服务、处理蓝牙授权、背景 BLE 模式、状态恢复、写入流控制或基于 CBUUID 的工作流程时使用。对于需要保护隐私的配件设置/选择流程，请先使用 accessorysetupkit，设置完成后返回此处进行 GATT 通信。
---

# 核心蓝牙

扫描、连接并与蓝牙低功耗（BLE）设备进行数据交换。
涵盖中心角色（扫描和连接到外围设备）、外围角色（广播服务）、后台模式和状态恢复。
使用 `accessorysetupkit` 进行隐私保护的外设发现和设置；使用此技能进行直接 Core Bluetooth GATT 通信。

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

Core Bluetooth 没有显式的权限请求 API。添加 `NSBluetoothAlwaysUsageDescription`，在应用准备好蓝牙访问时创建管理器，然后检查 `manager.authorization` 和 `manager.state`。
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

扫描特定的服务 UUID 以节省电量。将 `nil` 传递给发现所有外围设备（不推荐在生产环境中使用）。

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

实现 `CBPeripheralDelegate` 以遍历服务/特征树。

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

使用 `CBPeripheralManager` 发布本地设备的服
