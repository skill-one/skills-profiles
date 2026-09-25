# WeatherKit

使用 `WeatherService` 获取当前天气状况、小时预报和每日预报、天气警报和历史统计数据。显示所需的 Apple Weather 归因信息。

## 目录

- [设置](#设置)
- [获取当前天气](#获取当前天气)
- [预报](#预报)
- [天气警报](#天气警报)
- [选择性查询](#选择性查询)
- [上下文查询](#上下文查询)
- [归因信息](#归因信息)
- [可用性](#可用性)
- [常见错误](#常见错误)
- [审核清单](#审核清单)
- [参考资料](#参考资料)

## 设置

### 项目配置

1. 在 Xcode 中启用 **WeatherKit** 功能（添加权限）
2. 在 Apple 开发者门户中为您的 App ID 启用 WeatherKit
3. 如果使用设备位置，请将 `NSLocationWhenInUseUsageDescription` 添加到 Info.plist
4. WeatherKit 需要 Apple 开发者计划的有效会员资格

### 导入

```swift
import WeatherKit
import CoreLocation
```

### 创建服务

使用共享单例或创建实例。`WeatherService` 符合 `Sendable`；将应用缓存和 UI 状态分别隔离。

```swift
let weatherService = WeatherService.shared
// 或
let weatherService = WeatherService()
```

## 获取当前天气

获取某个位置的当前天气状况。返回包含所有可用数据集的 `Weather` 对象。

WeatherKit 温度是 `Measurement<UnitTemperature>` 值；使用 `.formatted()` 显示它们，以便单位和数字格式遵循用户的区域设置。

```swift
func fetchCurrentWeather(for location: CLLocation) async throws -> CurrentWeather {
    let weather = try await weatherService.weather(for: location)
    return weather.currentWeather
}

// 使用结果
func displayCurrent(_ current: CurrentWeather) {
    let temp = current.temperature  // Measurement<UnitTemperature>
    let condition = current.condition  // WeatherCondition 枚举
    let symbol = current.symbolName  // SF Symbol 名称
    let humidity = current.humidity  // Double (0-1)
    let wind = current.wind  // Wind (速度、方向、阵风)
    let uvIndex = current.uvIndex  // UVIndex

    print("\(condition): \(temp.formatted())")
}
```

## 预报

### 小时预报

默认情况下，从当前小时开始返回 25 个连续的小时。

```swift
func fetchHourlyForecast(for location: CLLocation) async throws -> Forecast<HourWeather> {
    let weather = try await weatherService.weather(for: location)
    return weather.hourlyForecast
}

// 遍历小时
for hour in hourlyForecast {
    print("\(hour.date): \(hour.temperature.formatted()), \(hour.condition)")
}
```

### 每日预报

默认情况下，从当前天开始返回 10 个连续的天。

```swift
func fetchDailyForecast(for location: CLLocation) async throws -> Forecast<DayWeather> {
    let weather = try await weatherService.weather(for: location)
    return weather.dailyForecast
}

// 遍历天
for day in dailyForecast {
    print("\(day.date): \(day.lowTemperature.formatted()) - \(day.highTemperature.formatted())")
    print("  条件: \(day.condition), 降水概率: \(day.precipitationChance)")
}
```

### 自定义日期范围

使用 `WeatherQuery` 请求特定日期范围的预报。

每日和小时日期范围查询使用包含的 `startDate` 和排他的 `endDate`。它们可以包含自 2021 年 8 月 1 日起的历史数据。预报可提供未来最多 10 天的数据；每个请求最多返回 10 个每日预报天或约 240 个小时预报。

```swift
func fetchExtendedForecast(for location: CLLocation) async throws -> Forecast<DayWeather> {
    let startDate = Date.now
    let endDate = Calendar.current.date(byAdding: .day, value: 10, to: startDate)!

    let forecast = try await weatherService.weather(
        for: location,
        including: .daily(startDate: startDate, endDate: endDate)
    )
    return forecast
}
```

对于明天特定的指导，请求本地明天的日期间隔，而不是使用分钟预报：

```swift
func fetchTomorrowForecast(for location: CLLocation) async throws -> Forecast<DayWeather> {
    let calendar = Calendar.current
    let tomorrow = calendar.startOfDay(
        for: calendar.date(byAdding: .day, value: 1, to: .now)!
    )
    let dayAfterTomorrow = calendar.date(byAdding: .day, value: 1, to: tomorrow)!

    return try await weatherService.weather(
        for: location,
        including: .daily(startDate: tomorrow, endDate: dayAfterTomorrow)
    )
}
```

## 天气警报

获取某个位置的活动天气警报。警报包括严重程度、摘要和受影响区域。

```swift
func fetchAlerts(for location: CLLocation) async throws -> [WeatherAlert]? {
    let weather = try await weatherService.weather(for: location)
    return weather.weatherAlerts
}

// 处理警报
if let alerts = weatherAlerts {
    for alert in alerts {
        print("警报: \(alert.summary)")
        print("严重程度: \(alert.severity)")
        print("区域: \(alert.region ?? "未知区域")")
        print("详情: \(alert.detailsURL)") // 非可选且归因信息必需
    }
}
```

对于警报仪表板，在讨论支持检查时明确指定 `WeatherAvailability`：它仅暴露 `alertAvailability` 和 `minuteAvailability`，而不是当前、小时或每日天气的广泛支持矩阵。

## 选择性查询

仅获取您需要的数据集，以最小化 API 使用和响应大小。每个 `WeatherQuery` 类型映射到一个数据集。

### 单个数据集

```swift
let current = try await weatherService.weather(
    for: location,
    including: .current
)
// current 是 CurrentWeather
```

### 多个数据集

```swift
let (current, hourly, daily) = try await weatherService.weather(
    for: location,
    including: .current, .hourly, .daily
)
// current: CurrentWeather, hourly: Forecast<HourWeather>, daily: Forecast<DayWeather>
```

### 分钟预报

在有限区域可用。返回下一小时分钟粒度的降水预报。

```swift
let minuteForecast = try await weatherService.weather(
    for: location,
    including: .minute
)
// minuteForecast: Forecast<MinuteWeather>? (如果不可用则为 nil)
```

### 可用的查询类型

| 查询 | 返回类型 | 描述 |
|---|---|---|
| `.current` | `CurrentWeather` | 当前观测条件 |
| `.hourly` | `Forecast<HourWeather>` | 从当前小时开始的 25 小时 |
| `.daily` | `Forecast<DayWeather>` | 从今天开始的 10 天 |
| `.minute` | `Forecast<MinuteWeather>?` | 下一小时降水 (有限区域) |
| `.alerts` | `[WeatherAlert]?` | 活动天气警报 |
| `.availability` | `WeatherAvailability` | 仅警报和分钟预报的可用性 |
| `.changes` | `WeatherChanges?` | 即将发生的显著天气变化 (iOS 18+) |
| `.historicalComparisons` | `HistoricalComparisons?` | 当前天气与历史平均值的比较 (iOS 18+) |

## 上下文查询

对于 iOS 18+ 上的“明天异常”或“什么正在变化？”功能，请求可选的 `.changes` 和 `.historicalComparisons` 结果：第一个报告即将发生的显著变化，第二个提供历史背景。

```swift
let (changes, comparisons) = try await weatherService.weather(
    for: location,
    including: .changes, .historicalComparisons
)
```

历史摘要和统计数据使用 `WeatherService` 方法，而不是 `WeatherQuery`。加载 [参考资料/weatherkit-patterns.md](references/weatherkit-patterns.md) 了解它们的元组顺序、API 和特定于统计数据的属性。

## 归因信息

Apple 要求使用 WeatherKit 的应用显示归因信息。这是一个法律要求。

### 获取归因信息

```swift
func fetchAttribution() async throws -> WeatherAttribution {
    return try await weatherService.attribution
}
```

加载 [参考资料/weatherkit-patterns.md](references/weatherkit-patterns.md) 了解完整的 SwiftUI 归因视图和缓存集成。

### 归因属性

| 属性 | 使用 |
|---|---|
| `combinedMarkLightURL` | 用于浅色背景的 Apple Weather 标记 |
| `combinedMarkDarkURL` | 用于深色背景的 Apple Weather 标记 |
| `squareMarkURL` | 方形 Apple Weather 徽标 |
| `legalPageURL` | 法律归因网页的 URL |
| `legalAttributionText` | 当无法显示网页视图时的文本替代 |
| `serviceName` | 天气数据提供者名称 |

## 可用性

检查某个位置是否有天气警报或分钟预报数据可用。`WeatherAvailability` 仅报告警报和分钟可用性；其他数据集（如当前天气）预计对地理位置是支持的。

```swift
func checkAvailability(for location: CLLocation) async throws {
    let availability = try await weatherService.weather(
        for: location,
        including: .availability
    )

    // 检查特定数据集的可用性
    if availability.alertAvailability == .available {
        // 安全获取警报
    }

    if availability.minuteAvailability == .available {
        // 此区域有分钟预报
    }
}
```

## 常见错误

### 不要：未显示 Apple Weather 归因信息就发布应用

无论 WeatherKit 数据何时出现，都要显示适当的 Apple Weather 标记并链接 `legalPageURL`；仅在无法显示法律页面时使用 `legalAttributionText`。

### 不要：当您只需要当前条件时获取所有数据集

每个数据集查询都会消耗您的 API 配额。使用 [选择性查询](#选择性查询) 中显示的查询，并仅获取 UI 显示的内容。

### 不要：忽略分钟预报不可用的情况

分钟预报在不支持的区域是可选的。检查可用性并处理 `nil` 结果，而不是强制解包它。

### 不要：忘记 WeatherKit 权限

未启用权限，`WeatherService` 调用将在运行时抛出。

```swift
// 错误：未配置 WeatherKit 权限
let weather = try await weatherService.weather(for: location) // 抛出

// 正确：在 Xcode 签名与权限中启用 WeatherKit
// 并在 Apple 开发者门户中为您的 App ID 启用
```

### 不要：未缓存就重复请求

WeatherKit 模型包括 `metadata.expirationDate`。在到期之前缓存响应，而不是发明固定的间隔或在每次视图出现时获取。让模型或缓存拥有 `loadIfNeeded`；完整的 actor 模式在 [参考资料/weatherkit-patterns.md](references/weatherkit-patterns.md#caching-strategy) 中。

## 审核清单

- [ ] Xcode 和 Apple 开发者门户中启用了 WeatherKit 功能
- [ ] 拥有有效的 Apple 开发者计划会员资格（WeatherKit 需要）
- [ ] 在天气数据出现的位置显示了 Apple Weather 归因信息
- [ ] 归因标记使用了正确的颜色方案变体（浅色/深色）
- [ ] 链接了法律归因页面或显示了 `legalAttributionText`
- [ ] 仅获取了需要的 `WeatherQuery` 数据集（在不需要时不要使用完整的 `weather(for:)`）
- [ ] 将分钟预报作为可选处理（在不支持的区域为 nil）
- [ ] 在迭代前检查天气警报是否为 nil
- [ ] 警报详情链接使用非可选的 `detailsURL`；可选的 `region` 是 nil 安全的
- [ ] 响应缓存直到每个模型的 `metadata.expirationDate`
- [ ] 使用 `WeatherAvailability` 检查警报/分钟可用性，而不是作为广泛的支持矩阵
- [ ] 在将 `CLLocation` 传递给服务之前请求位置权限
- [ ] 使用 `Measurement.formatted()` 为区域格式化温度和测量值

## 参考资料

- 扩展模式（SwiftUI 仪表板、图表集成、历史统计数据）：[参考资料/weatherkit-patterns.md](references/weatherkit-patterns.md)
- [WeatherKit 框架](https://sosumi.ai/documentation/weatherkit)
- [WeatherService](https://sosumi.ai/documentation/weatherkit/weatherservice)
- [WeatherAttribution](https://sosumi.ai/documentation/weatherkit/weatherattribution)
- [WeatherQuery](https://sosumi.ai/documentation/weatherkit/weatherquery)
- [WeatherQuery.daily(startDate:endDate:)](https://sosumi.ai/documentation/weatherkit/weatherquery/daily(startdate:enddate:))
- [WeatherQuery.hourly(startDate:endDate:)](https://sosumi.ai/documentation/weatherkit/weatherquery/hourly(startdate:enddate:))
- [CurrentWeather](https://sosumi.ai/documentation/weatherkit/currentweather)
- [CurrentWeather.temperature](https://sosumi.ai/documentation/weatherkit/currentweather/temperature)
- [Measurement.formatted()](https://sosumi.ai/documentation/foundation/measurement/formatted())
- [Forecast](https://sosumi.ai/documentation/weatherkit/forecast)
- [HourWeather](https://sosumi.ai/documentation/weatherkit/hourweather)
- [DayWeather](https://sosumi.ai/documentation/weatherkit/dayweather)
- [WeatherAlert](https://sosumi.ai/documentation/weatherkit/weatheralert)
- [WeatherAvailability](https://sosumi.ai/documentation/weatherkit/weatheravailability)
- [WeatherMetadata.expirationDate](https://sosumi.ai/documentation/weatherkit/weathermetadata/expirationdate)
- [WeatherQuery.changes](https://sosumi.ai/documentation/weatherkit/weatherquery/changes)
- [WeatherQuery.historicalComparisons](https://sosumi.ai/documentation/weatherkit/weatherquery/historicalcomparisons)
- [WeatherKit 更新](https://sosumi.ai/documentation/updates/weatherkit)
- [为今天的天气带来上下文](https://sosumi.ai/videos/play/wwdc2024/10067)
- [使用 WeatherKit 获取天气预报](https://sosumi.ai/documentation/weatherkit/fetching_weather_forecasts_with_weatherkit)
