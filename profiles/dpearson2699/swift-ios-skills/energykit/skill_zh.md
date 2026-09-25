# EnergyKit

使用电网清洁度和成本指导来转移或减少受管理设备的负载。
为了获取受管理设备的洞察，请及时提交设备的实际负载事件。

> **Beta敏感。** 核心EnergyKit随iOS/iPadOS 26一起发布。iOS/iPadOS 27的`ElectricalLoadDevice`和面向家庭负载事件的体验为Beta版；在依赖这些API之前，请重新检查当前的Apple文档。

## 目录

- [设置](#设置)
- [核心概念](#核心概念)
- [查询电力指导](#查询电力指导)
- [使用指导值](#使用指导值)
- [能源场所](#能源场所)
- [提交负载事件](#提交负载事件)
- [电力洞察](#电力洞察)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 设置

### 授权和版本分离

| 运行时 | 负载事件设备API | 功能 |
|---|---|---|
| iOS/iPadOS 26.x | `deviceID:` 兼容初始化器 | EnergyKit |
| iOS/iPadOS 27+ Beta | 带有`device:`初始化器的`ElectricalLoadDevice` | EnergyKit；为家庭应用集成添加EnergyKit负载事件 |

所有EnergyKit的使用都需要`com.apple.developer.energykit`；在应用目标上启用EnergyKit功能。在iOS/iPadOS 27+上，仅在应用需要在家庭应用中获得设备名称、能源上下文、活动日志、历史图表或趋势通知时，才添加EnergyKit负载事件功能（`com.apple.developer.energykit.loadevents-experience`）。该家庭体验需要这两个功能。缺少权限可能会出现`EnergyKitError.permissionDenied`。

### 导入

```swift
import EnergyKit
```

**平台可用性：** 核心EnergyKit API适用于iOS/iPadOS 26.0+。一些洞察细分API，包括电网清洁度类别，适用于26.1+，需要可用性保护。Apple目前仅在美利坚合众国连续区域记录电力指导；处理`EnergyKitError.unsupportedRegion`。

## 核心概念

EnergyKit提供两个主要功能：

1. **电力指导** -- 时间加权的预测，告诉应用何时电力更清洁，并且当费率数据可用时，成本更低
2. **负载事件** -- 来自受管理设备（电动汽车充电器、暖通空调）的遥测数据，由请求指导的相同设备/应用提交，以便EnergyKit可以生成洞察

### 关键类型

| 类型 | 角色 |
|---|---|
| `ElectricityGuidance` | 带有权重时间间隔的预测数据 |
| `ElectricityGuidance.Service` | 获取指导数据的接口 |
| `ElectricityGuidance.Query` | 指定转移或减少操作的查询 |
| `ElectricityGuidance.Value` | 带有评分（0.0-1.0）的时间间隔 |
| `EnergyVenue` | 已注册用于能源管理的物理位置（家庭） |
| `ElectricVehicleLoadEvent` | 电动汽车充电器遥测的负载事件 |
| `ElectricHVACLoadEvent` | 暖通空调系统遥测的负载事件 |
| `ElectricalLoadDevice` | iOS/iPadOS 27+ Beta负载事件的设备标识 |
| `ElectricityInsightService` | 查询能源/运行时洞察的服务 |
| `ElectricityInsightRecord` | 历史能源或运行时数据，可选地按费率或26.1+电网清洁度细分 |
| `ElectricityInsightQuery` | 查询历史洞察数据的查询 |

### 建议的操作

| 操作 | 用例 |
|---|---|
| `.shift` | 可以将消费转移到不同时间的设备（电动汽车充电） |
| `.reduce` | 可以在不停止的情况下降低消费的设备（暖通空调回退） |

## 查询电力指导

使用`ElectricityGuidance.Service`为场所获取预测流。

```swift
import EnergyKit

func observeGuidance(venueID: UUID) async throws {
    let query = ElectricityGuidance.Query(suggestedAction: .shift)
    let service = ElectricityGuidance.sharedService

    let guidanceStream = service.guidance(using: query, at: venueID)

    for try await guidance in guidanceStream {
        print("指导令牌: \(guidance.guidanceToken)")
        print("时间间隔: \(guidance.interval)")
        print("场所: \(guidance.energyVenueID)")

        // 检查费率计划信息是否可用
        if guidance.options.contains(.guidanceIncorporatesRatePlan) {
            print("费率计划数据已包含")
        }
        if guidance.options.contains(.locationHasRatePlan) {
            print("位置有费率计划")
        }

        processGuidanceValues(guidance.values)
    }
}
```

## 使用指导值

每个`ElectricityGuidance.Value`包含一个时间间隔和0.0到1.0的评分。较低的评分表示使用电力的更好时间。

```swift
func processGuidanceValues(_ values: [ElectricityGuidance.Value]) {
    for value in values {
        let interval = value.interval
        let rating = value.rating  // 0.0（最佳）到1.0（最差）

        print("从 \(interval.start) 到 \(interval.end): 评分 \(rating)")
    }
}

// 找到充电的最佳时间
func bestChargingWindow(
    in values: [ElectricityGuidance.Value]
) -> ElectricityGuidance.Value? {
    values.min(by: { $0.rating < $1.rating })
}

// 找到所有低于阈值的“良好”窗口
func goodWindows(
    in values: [ElectricityGuidance.Value],
    threshold: Double = 0.3
) -> [ElectricityGuidance.Value] {
    values.filter { $0.rating <= threshold }
}
```

### 在SwiftUI中显示指导

```swift
import SwiftUI
import EnergyKit

struct GuidanceTimelineView: View {
    let values: [ElectricityGuidance.Value]

    var body: some View {
        List(values, id: \.interval.start) { value in
            HStack {
                VStack(alignment: .leading) {
                    Text(value.interval.start, style: .time)
                    Text(value.interval.end, style: .time)
                        .foregroundStyle(.secondary)
                }
                Spacer()
                RatingIndicator(rating: value.rating)
            }
        }
    }
}

struct RatingIndicator: View {
    let rating: Double

    var color: Color {
        if rating <= 0.3 { return .green }
        if rating <= 0.6 { return .yellow }
        return .red
    }

    var label: String {
        if rating <= 0.3 { return "良好" }
        if rating <= 0.6 { return "一般" }
        return "避免"
    }

    var body: some View {
        Text(label)
            .padding(.horizontal)
            .padding(.vertical)
            .background(color.opacity(0.2))
            .foregroundStyle(color)
            .clipShape(Capsule())
    }
}
```

## 能源场所

`EnergyVenue`表示已注册用于能源管理的物理位置。

```swift
// 列出所有场所
func listVenues() async throws -> [EnergyVenue] {
    try await EnergyVenue.venues()
}

// 通过ID获取特定场所
func getVenue(id: UUID) async throws -> EnergyVenue {
    try await EnergyVenue.venue(for: id)
}

// 获取与HomeKit家庭匹配的场所
func getVenueForHome(homeID: UUID) async throws -> EnergyVenue {
    try await EnergyVenue.venue(matchingHomeUniqueIdentifier: homeID)
}
```

### 场所属性

```swift
let venue = try await EnergyVenue.venue(for: venueID)
print("场所ID: \(venue.id)")
print("场所名称: \(venue.name)")
```

## 提交负载事件

向系统报告设备消费数据。这有助于系统生成电力洞察。请求电力指导的相同EnergyKit功能设备/应用必须使用EnergyKit返回的指导令牌提交相应的负载事件。不要编造令牌。

### 电动汽车充电器负载事件

```swift
func submitEVBeginEvent(
    at venue: EnergyVenue,
    guidanceToken: UUID,
    deviceID: String,
    deviceName: String
) async throws {
    let session = ElectricVehicleLoadEvent.Session(
        id: UUID(),
        state: .begin,
        guidanceState: ElectricVehicleLoadEvent.Session.GuidanceState(
            wasFollowingGuidance: true,
            guidanceToken: guidanceToken
        )
    )

    let measurement = ElectricVehicleLoadEvent.ElectricalMeasurement(
        stateOfCharge: 45,
        direction: .imported,
        power: Measurement(value: 0, unit: .kilowatts),
        energy: Measurement(value: 0, unit: .kilowattHours)
    )

    let event: ElectricVehicleLoadEvent
    if #available(iOS 27.0, iPadOS 27.0, *) {
        let device = ElectricalLoadDevice(
            id: deviceID,
            name: deviceName,
            type: .electricVehicle
        )
        event = ElectricVehicleLoadEvent(
            timestamp: Date(), measurement: measurement,
            session: session, device: device
        )
    } else {
        // iOS/iPadOS 26兼容性；在iOS 27 SDK中已弃用。
        event = ElectricVehicleLoadEvent(
            timestamp: Date(), measurement: measurement,
            session: session, deviceID: deviceID
        )
    }

    try await venue.submitEvents([event])
}
```

### 暖通空调负载事件

```swift
func submitHVACEvent(
    at venue: EnergyVenue,
    guidanceToken: UUID,
    stage: Int,
    deviceID: String,
    deviceName: String
) async throws {
    let session = ElectricHVACLoadEvent.Session(
        id: UUID(),
        state: .active,
        guidanceState: ElectricHVACLoadEvent.Session.GuidanceState(
            wasFollowingGuidance: true,
            guidanceToken: guidanceToken
        )
    )

    let measurement = ElectricHVACLoadEvent.ElectricalMeasurement(stage: stage)

    let event: ElectricHVACLoadEvent
    if #available(iOS 27.0, iPadOS 27.0, *) {
        let device = ElectricalLoadDevice(
            id: deviceID,
            name: deviceName,
            type: .hvac
        )
        event = ElectricHVACLoadEvent(
            timestamp: Date(), measurement: measurement,
            session: session, device: device
        )
    } else {
        // iOS/iPadOS 26兼容性；在iOS 27 SDK中已弃用。
        event = ElectricHVACLoadEvent(
            timestamp: Date(), measurement: measurement,
            session: session, deviceID: deviceID
        )
    }

    try await venue.submitEvents([event])
}
```

### 会话状态

| 状态 | 使用时机 |
|---|---|
| `.begin` | 设备开始消费电力 |
| `.active` | 设备正在积极消费（周期性更新） |
| `.end` | 设备停止消费电力 |

保留`.begin → .active → .end`并尽快提交事件，而不是批量长时间持有。对于电动汽车充电，使用零功率和能量的`.begin`，大约每15分钟加上重大变化提交`.active`，以及使用零功率和累积能量的`.end`。保留未确认的事件，并使用有界退避重试`EnergyKitError.rateLimitExceeded`。加载[电动汽车会话管理器](references/energykit-patterns.md#ev-charging-session-manager)或[HVAC控制管理器](references/energykit-patterns.md#hvac-control-manager)以进行设备特定的生命周期处理。

仅在iOS/iPadOS 27+上承诺家庭应用设备名称、能源上下文、活动日志、图表和趋势通知，当基础EnergyKit和EnergyKit负载事件功能都存在时。

## 电力洞察

使用`ElectricityInsightService`查询设备的歷史能源和运行时数据。空的`ElectricityInsightQuery.Options`选项集仅返回总计；它不会填充清洁度或费率细分。仅在UI需要这些细分时才请求`.cleanliness`和/或`.tariff`。不要用MetricKit应用功率指标替代EnergyKit洞察；EnergyKit洞察依赖于为受管理设备提交的EnergyKit负载事件。

从请求的范围选择洞察粒度。对于七天的视图，查询`.hourly`；仅在查询覆盖至少一个月的日历时使用`.daily`。

```swift
func queryEnergyInsights(deviceID: String, venueID: UUID) async throws {
    let sevenDaysAgo = Calendar.current.date(
        byAdding: .day,
        value: -7,
        to: Date()
    )!

    let query = ElectricityInsightQuery(
        options: [.cleanliness, .tariff],
        range: DateInterval(
            start: sevenDaysAgo,
            end: Date()
        ),
        granularity: .hourly,
        flowDirection: .imported
    )

    let service = ElectricityInsightService.shared
    let stream = try await service.energyInsights(
        forDeviceID: deviceID, using: query, atVenue: venueID
    )

    for await record in stream {
        if let total = record.totalEnergy { print("总计: \(total)") }

        if #available(iOS 26.1, iPadOS 26.1, *),
           let cleaner = record.dataByGridCleanliness?.cleaner {
            print("更清洁: \(cleaner)")
        }
    }
}
```

使用`runtimeInsights(forDeviceID:using:atVenue:)`代替能源获取运行时数据。粒度选项：`.hourly`，`.daily`，`.weekly`，`.monthly`，`.yearly`。选择与Apple的最小聚合窗口匹配的范围：至少为日历周的小时，至少为日历月的天，至少为六个月的周，以及至少为日历年的月或年。参见[references/energykit-patterns.md](references/energykit-patterns.md)获取完整的洞察示例。

## 常见错误

| 错误 | 修复 |
|---|---|
| 在设置之前查询 | 验证EnergyKit授权并处理`.permissionDenied`。 |
| 假设每个区域都有指导 | Apple目前仅在美利坚合众国连续区域记录指导；处理不支持区域和不可用场所/指导状态。 |
| 编造或丢弃指导令牌 | 在请求设备上持久化真实令牌，并使用该令牌与其负载事件一起提交。 |
| 发送孤立或延迟的负载样本 | 保留`.begin → .active → .end`，尽快提交，并保留事件直到提交成功。 |
| 使用`deviceID:`作为当前默认值 | 使用iOS/iPadOS 27+ `ElectricalLoadDevice`和`device:`；将`deviceID:`仅保留为26.x运行时分支。 |
| 使用硬编码的场所ID | 使用`EnergyVenue.venues()`发现场所，并选择预期的场所。 |

## 审查清单

- [ ] 基础EnergyKit功能存在；iOS/iPadOS 27+的家庭集成还具有EnergyKit负载事件
- [ ] 处理区域、权限、场所发现、不可用指导和服务错误
- [ ] 真实指导令牌保留在请求的设备/应用及其提交的负载事件中
- [ ] iOS/iPadOS 27+使用`ElectricalLoadDevice`/`device:`；`deviceID:`仅保留为26.x兼容性
- [ ] `.begin → .active → .end`事件遵循设备节奏，尽快提交，在失败时存活，并使用有界退避重试速率限制
- [ ] 正确解释评分/操作；洞察选项、可用性、粒度和最小范围与UI匹配
- [ ] 不用MetricKit遥测替代EnergyKit负载事件或洞察

## 参考资料

- 应用架构、电动汽车/暖通空调会话节奏、仪表板呈现、洞察、错误和场所发现的扩展工作流：
  [references/energykit-patterns.md](references/energykit-patterns.md)
- [EnergyKit框架](https://sosumi.ai/documentation/energykit)
- [ElectricityGuidance](https://sosumi.ai/documentation/energykit/electricityguidance)
- [ElectricityGuidance.Service](https://sosumi.ai/documentation/energykit/electricityguidance/service)
- [ElectricityGuidance.Query](https://sosumi.ai/documentation/energykit/electricityguidance/query)
- [ElectricityGuidance.Value](https://sosumi.ai/documentation/energykit/electricityguidance/value)
- [EnergyVenue](https://sosumi.ai/documentation/energykit/energyvenue)
- [ElectricalLoadDevice](https://sosumi.ai/documentation/energykit/electricalloaddevice)
- [ElectricVehicleLoadEvent](https://sosumi.ai/documentation/energykit/electricvehicleloadevent)
- [ElectricHVACLoadEvent](https://sosumi.ai/documentation/energykit/electrichvacloadevent)
- [ElectricityInsightService](https://sosumi.ai/documentation/energykit/electricityinsightservice)
- [ElectricityInsightRecord](https://sosumi.ai/documentation/energykit/electricityinsightrecord)
- [ElectricityInsightQuery](https://sosumi.ai/documentation/energykit/electricityinsightquery)
- [EnergyKitError](https://sosumi.ai/documentation/energykit/energykiterror)
- [EnergyKit授权](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.energykit)
- [EnergyKit LoadEvents授权](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.energykit.loadevents-experience)
- [为电动汽车提供充电历史](https://sosumi.ai/documentation/energykit/providing-informative-charging-history-for-electric-vehicles)
- [优化家庭电力使用](https://sosumi.ai/documentation/energykit/optimizing-home-electricity-usage)
