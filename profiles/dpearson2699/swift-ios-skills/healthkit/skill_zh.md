# HealthKit

从 Apple Health store 读取和写入健康与健身数据。涵盖授权、查询、写入样本、后台交付和锻炼会话。目标 Swift 6.3 / iOS 26+。

## 目录

- [设置和可用性](#设置和可用性)
- [授权](#授权)
- [读取数据：样本查询](#读取数据样本查询)
- [读取数据：统计查询](#读取数据统计查询)
- [读取数据：统计集合查询](#读取数据统计集合查询)
- [写入数据](#写入数据)
- [后台交付](#后台交付)
- [锻炼会话](#锻炼会话)
- [常见数据类型](#常见数据类型)
- [HKUnit 参考](#hkunit参考)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 设置和可用性

### 项目配置

1. 在 Xcode 中启用 HealthKit 功能（添加权限）
2. 向 Info.plist 添加 `NSHealthShareUsageDescription`（读取）和 `NSHealthUpdateUsageDescription`（写入）
3. 对于后台交付，启用“后台交付”子功能

### 可用性检查

在调用其他 HealthKit API 之前，始终检查可用性。健康数据在 iOS、watchOS、visionOS、iPadOS 17+ 以及在 Vision Pro 上运行的 iOS 应用中可用。在 iPadOS 16 或更早版本上不可用，并且可能受设备管理策略限制。

```swift
import HealthKit

guard HKHealthStore.isHealthDataAvailable() else {
    // 此设备上的健康数据不可用或受限。
    return
}

let healthStore = HKHealthStore()
```

创建一个 `HKHealthStore` 实例并在整个应用中重用它。它是线程安全的。如果 HealthKit 是可选的，请检查 Xcode 生成的 `UIRequiredDeviceCapabilities` `healthkit` 条目，以避免无意中排除不支持的设备。

## 授权

仅请求您的应用真正需要的类型。App Review 拒绝过度请求的应用。

```swift
func requestAuthorization() async throws {
    let typesToShare: Set<HKSampleType> = [
        HKQuantityType(.stepCount),
        HKQuantityType(.activeEnergyBurned)
    ]

    let typesToRead: Set<HKObjectType> = [
        HKQuantityType(.stepCount),
        HKQuantityType(.heartRate),
        HKQuantityType(.activeEnergyBurned),
        HKCharacteristicType(.dateOfBirth)
    ]

    try await healthStore.requestAuthorization(
        toShare: typesToShare,
        read: typesToRead
    )
}
```

### 检查授权状态

`authorizationStatus(for:)` 报告写入/共享授权。HealthKit 不会透露读取权限是否被授予或拒绝。如果用户拒绝读取访问，查询将只返回您的应用成功保存的样本，这可能看起来是空或部分数据。

```swift
let status = healthStore.authorizationStatus(
    for: HKQuantityType(.stepCount)
)

switch status {
case .notDetermined:
    // 尚未请求 -- 安全调用 requestAuthorization
    break
case .sharingAuthorized:
    // 用户授予写入访问权限
    break
case .sharingDenied:
    // 用户拒绝写入访问（读取拒绝与“无数据”无法区分）
    break
@unknown default:
    break
}
```

## 读取数据：样本查询

使用 `HKSampleQueryDescriptor`（异步/等待）进行一次性读取。优先选择描述符而不是较旧的基于回调的 `HKSampleQuery`。

```swift
func fetchRecentHeartRates() async throws -> [HKQuantitySample] {
    let heartRateType = HKQuantityType(.heartRate)

    let descriptor = HKSampleQueryDescriptor(
        predicates: [.quantitySample(type: heartRateType)],
        sortDescriptors: [SortDescriptor(\.endDate, order: .reverse)],
        limit: 20
    )

    let results = try await descriptor.result(for: healthStore)
    return results
}

// 从样本中提取值：
for sample in results {
    let bpm = sample.quantity.doubleValue(
        for: HKUnit.count().unitDivided(by: .minute())
    )
    print("\(bpm) bpm at \(sample.endDate)")
}
```

## 读取数据：统计查询

使用 `HKStatisticsQueryDescriptor` 获取聚合的单值统计（总和、平均值、最小值、最大值）。

```swift
func fetchTodayStepCount() async throws -> Double? {
    let calendar = Calendar.current
    let startOfDay = calendar.startOfDay(for: Date())
    let endOfDay = calendar.date(byAdding: .day, value: 1, to: startOfDay)!

    let predicate = HKQuery.predicateForSamples(
        withStart: startOfDay, end: endOfDay
    )
    let stepType = HKQuantityType(.stepCount)
    let samplePredicate = HKSamplePredicate.quantitySample(
        type: stepType, predicate: predicate
    )

    let query = HKStatisticsQueryDescriptor(
        predicate: samplePredicate,
        options: .cumulativeSum
    )

    let result = try await query.result(for: healthStore)
    return result?.sumQuantity()?.doubleValue(for: .count())
}
```

**按数据类型选项：**
- 累计类型（步数、卡路里）：`.cumulativeSum`
- 离散类型（心率、体重）：`.discreteAverage`, `.discreteMin`, `.discreteMax`

## 读取数据：统计集合查询

使用 `HKStatisticsCollectionQueryDescriptor` 将时间序列数据按间隔分组——非常适合图表。

```swift
func fetchDailySteps(forLast days: Int) async throws -> [(date: Date, steps: Double)] {
    let calendar = Calendar.current
    let endDate = calendar.startOfDay(
        for: calendar.date(byAdding: .day, value: 1, to: Date())!
    )
    let startDate = calendar.date(byAdding: .day, value: -days, to: endDate)!

    let predicate = HKQuery.predicateForSamples(
        withStart: startDate, end: endDate
    )
    let stepType = HKQuantityType(.stepCount)
    let samplePredicate = HKSamplePredicate.quantitySample(
        type: stepType, predicate: predicate
    )

    let query = HKStatisticsCollectionQueryDescriptor(
        predicate: samplePredicate,
        options: .cumulativeSum,
        anchorDate: endDate,
        intervalComponents: DateComponents(day: 1)
    )

    let collection = try await query.result(for: healthStore)
    var dailySteps: [(date: Date, steps: Double)] = []

    collection.statisticsCollection.enumerateStatistics(
        from: startDate, to: endDate
    ) { statistics, _ in
        let steps = statistics.sumQuantity()?
            .doubleValue(for: .count()) ?? 0
        dailySteps.append((date: statistics.startDate, steps: steps))
    }

    return dailySteps
}
```

### 长时间运行的集合查询

使用 `results(for:)`（复数）获取 `AsyncSequence`，它会随着新数据到达而发出更新：

```swift
let updateStream = query.results(for: healthStore)

Task {
    for try await result in updateStream {
        // result.statisticsCollection 包含更新后的数据
    }
}
```

## 写入数据

创建 `HKQuantitySample` 对象并将它们保存到存储中。

```swift
func saveSteps(count: Double, start: Date, end: Date) async throws {
    let stepType = HKQuantityType(.stepCount)
    let quantity = HKQuantity(unit: .count(), doubleValue: count)

    let sample = HKQuantitySample(
        type: stepType,
        quantity: quantity,
        start: start,
        end: end
    )

    try await healthStore.save(sample)
}
```

将 `try await healthStore.save(sample)` 返回视为保存成功门；只有在成功后报告成功或推进应用状态。失败时，显示错误并纠正已知的授权、类型、单位、持续时间或输入问题，然后再构建另一个样本。有界查询或在 Health 应用中的检查作为需要持久化证据的集成测试检查很有用，但不是每次保存后的强制性生产读取。

您的应用只能删除它自己创建的样本。来自其他应用或 Apple Watch 的样本是只读的。

## 后台交付

注册以接收后台更新，以便当新数据到达时您的应用被启动。需要后台交付权限。

```swift
func enableStepCountBackgroundDelivery() async throws {
    let stepType = HKQuantityType(.stepCount)

    try await healthStore.enableBackgroundDelivery(
        for: stepType,
        frequency: .hourly
    )
}
```

**与 `HKObserverQuery` 配对** 处理通知。始终调用完成处理程序：

```swift
let observerQuery = HKObserverQuery(
    sampleType: HKQuantityType(.stepCount),
    predicate: nil
) { query, completionHandler, error in
    defer { completionHandler() }  // 必须调用以表示完成
    guard error == nil else { return }
    // 获取新数据，更新 UI 等
}
healthStore.execute(observerQuery)
```

**频率：** `.immediate`, `.hourly`, `.daily`, `.weekly`

在应用启动时设置观察者查询，然后为同一样本类型调用一次 `enableBackgroundDelivery`。系统会持久化注册，最多按请求的频率唤醒应用一次，并对某些类型（如 iOS 上的每小时步数交付）执行更严格的限制。后台交付在模拟器上不受支持；在设备上测试它。

## 锻炼会话

使用 `HKWorkoutSession` 和 `HKLiveWorkoutBuilder` 跟踪实时锻炼。
`HKWorkoutSession` 在 iOS/iPadOS 17+、visionOS 1+ 和 watchOS 2+ 上可用。
`HKLiveWorkoutBuilder` 在 iOS/iPadOS 26+ 和 watchOS 5+ 上可用，因此如果支持较旧的 iOS/iPadOS 版本，请限制实时构建器代码。

在 iPhone 和 iPad 上，实时心率收集需要配对的外部心率传感器。Apple Watch 会话可以收集高频心率数据。对于锁定的 iPhone 锻炼，在 Lock Screen 上显示健康指标之前，请计划系统的锻炼数据访问流程。

```swift
func startWorkout() async throws {
    let configuration = HKWorkoutConfiguration()
    configuration.activityType = .running
    configuration.locationType = .outdoor

    let session = try HKWorkoutSession(
        healthStore: healthStore,
        configuration: configuration
    )
    session.delegate = self

    let builder = session.associatedWorkoutBuilder()
    builder.dataSource = HKLiveWorkoutDataSource(
        healthStore: healthStore,
        workoutConfiguration: configuration
    )

    session.startActivity(with: Date())
    try await builder.beginCollection(at: Date())
}

// 请求拆除；从代理的 `.stopped` 过渡中最终确定。
session.stopActivity(with: Date())
```

在请求停止后不要立即调用 `endCollection` 和 `finishWorkout`。等待会话代理的 `.stopped` 过渡，然后等待 `builder.endCollection(at:)` 后跟 `builder.finishWorkout()`。只有在两个操作都返回后，才报告锻炼已保存并清除会话状态。处理每个抛出的错误，不要盲目重复拆除。当设备锁定时，成功的 `finishWorkout()` 可能返回没有锻炼对象，所以 `nil` 结果本身不是失败。

有关完整的锻炼生命周期管理，包括暂停/恢复、代理处理和多设备镜像，请参阅 [参考资料/healthkit-patterns.md](references/healthkit-patterns.md)。

## 常见数据类型

### HKQuantityTypeIdentifier

| 标识符 | 类别 | 单位 |
|---|---|---|
| `.stepCount` | 健身 | `.count()` |
| `.distanceWalkingRunning` | 健身 | `.meter()` |
| `.activeEnergyBurned` | 健身 | `.kilocalorie()` |
| `.basalEnergyBurned` | 健身 | `.kilocalorie()` |
| `.heartRate` | 生命体征 | `.count()/.minute()` |
| `.restingHeartRate` | 生命体征 | `.count()/.minute()` |
| `.oxygenSaturation` | 生命体征 | `.percent()` |
| `.bodyMass` | 身体 | `.gramUnit(with: .kilo)` |
| `.bodyMassIndex` | 身体 | `.count()` |
| `.height` | 身体 | `.meter()` |
| `.bodyFatPercentage` | 身体 | `.percent()` |
| `.bloodGlucose` | 实验室 | `.gramUnit(with: .milli).unitDivided(by: .literUnit(with: .deci))` |

### HKCategoryTypeIdentifier

常见分类类型：`.sleepAnalysis`, `.mindfulSession`, `.appleStandHour`

### HKCharacteristicType

只读用户特征包括 `.dateOfBirth`, `.biologicalSex`, `.bloodType`, `.fitzpatrickSkinType`, `.wheelchairUse` 和 `.activityMoveMode`。

## HKUnit 参考

```swift
// 基本单位
HKUnit.count()                              // 步数，计数
HKUnit.meter()                              // 距离
HKUnit.mile()                               // 距离（英制）
HKUnit.kilocalorie()                        // 能量
HKUnit.joule(with: .kilo)                   // 能量（SI）
HKUnit.gramUnit(with: .kilo)                // 质量（kg）
HKUnit.pound()                              // 质量（英制）
HKUnit.percent()                            // 百分比

// 复合单位
HKUnit.count().unitDivided(by: .minute())   // 心率（bpm）
HKUnit.meter().unitDivided(by: .second())   // 速度（m/s）

// 前缀单位
HKUnit.gramUnit(with: .milli)               // 毫克
HKUnit.literUnit(with: .deci)               // 分升
```

## 常见错误

1. **过度请求数据类型。** 仅请求功能实际使用的读取/写入类型；广泛的 HealthKit 权限表是 App Review 风险。
2. **将读取授权视为写入授权。** 您可以在保存之前检查 `.sharingAuthorized`，但读取拒绝受隐私保护，并看起来像仅属于应用的所有者、空或部分结果。
3. **跳过 `isHealthDataAvailable()`。** 在 HealthKit 访问之前检查，并处理不可用或受限的存储，而不会崩溃。
4. **使用回调查询为新异步代码。** 优先选择异步描述符进行一次性读取和统计，并将广泛查询保持在主角色之外。
5. **忘记观察者完成处理程序。** 始终调用处理程序；遗漏的完成可能会延迟或停止未来的后台交付。
6. **假设 `.immediate` 意味着立即。** 后台交付受系统限制，必须在设备上测试。
7. **使用累计统计来处理离散值。** 将统计选项与数据类型匹配：累计总和用于步数/能量，离散平均值/最小值/最大值用于心率、体重和类似样本。

## 审查清单

- [ ] 在任何 HealthKit 访问之前检查 `HKHealthStore.isHealthDataAvailable()`
- [ ] 仅请求授权中必要的类型
- [ ] Info.plist 包含 `NSHealthShareUsageDescription` 和/或 `NSHealthUpdateUsageDescription`
- [ ] HealthKit 功能在 Xcode 项目中启用
- [ ] 在保存之前检查写入授权；处理读取拒绝作为部分或空查询结果
- [ ] 重用单个 `HKHealthStore` 实例（而不是每个查询创建）
- [ ] 使用异步查询描述符而不是基于回调的查询
- [ ] 重查询不阻塞主线程
- [ ] 统计选项与数据类型匹配（累计与离散）
- [ ] 后台交付与应用启动的 `HKObserverQuery` 设置配对，并调用 `completionHandler`
- [ ] 如果使用 `enableBackgroundDelivery`，则启用后台交付权限
- [ ] 在设备上测试后台交付，并考虑频率限制
- [ ] 锻炼停止在代理的 `.stopped` 过渡之前等待 `endCollection` 和 `finishWorkout`；只有在成功最终化后才清除状态
- [ ] 处理锻炼 API 的可用性和实时心率传感器要求
- [ ] 删除操作仅针对应用先前保存的对象

## 参考资料

- 扩展模式（锻炼、锚定查询、SwiftUI 集成）：[参考资料/healthkit-patterns.md](references/healthkit-patterns.md)
- [HealthKit 框架](https://sosumi.ai/documentation/healthkit)
- [HKHealthStore](https://sosumi.ai/documentation/healthkit/hkhealthstore)
- [HKSampleQueryDescriptor](https://sosumi.ai/documentation/healthkit/hksamplequerydescriptor)
- [HKStatisticsQueryDescriptor](https://sosumi.ai/documentation/healthkit/hkstatisticsquerydescriptor)
- [HKStatisticsCollectionQueryDescriptor](https://sosumi.ai/documentation/healthkit/hkstatisticscollectionquerydescriptor)
- [HKWorkoutSession](https://sosumi.ai/documentation/healthkit/hkworkoutsession)
- [HKLiveWorkoutBuilder](https://sosumi.ai/documentation/healthkit/hkliveworkoutbuilder)
- [设置 HealthKit](https://sosumi.ai/documentation/healthkit/setting-up-healthkit)
- [授权访问健康数据](https://sosumi.ai/documentation/healthkit/authorizing-access-to-health-data)
- [配置 HealthKit 访问](https://sosumi.ai/documentation/xcode/configuring-healthkit-access)
