# Swift Charts

使用 Swift Charts 针对 iOS 26+ 构建 数据可视化。在 `Chart` 或 `Chart3D` 中组合标记，使用视图修饰符配置轴和刻度，并在数据需要时使用矢量图或 3D 图。

参见 [references/charts-patterns.md](references/charts-patterns.md) 获取扩展模式、3D 图表、无障碍访问和主题指南。

## 目录

- [工作流程](#workflow)
- [图表容器](#chart-container)
- [标记类型](#mark-types)
- [轴自定义](#axis-customization)
- [刻度配置](#scale-configuration)
- [前景样式和编码](#foreground-style-and-encoding)
- [选择 (iOS 17+)](#selection-ios-17)
- [可滚动的图表 (iOS 17+)](#scrollable-charts-ios-17)
- [注释](#annotations)
- [图例](#legend)
- [矢量图 (iOS 18+)](#vectorized-plots-ios-18)
- [3D 图表 (iOS 26+)](#3d-charts-ios-26)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 工作流程

### 1. 创建新图表

1. 将数据定义为 `Identifiable` 结构体或使用 `id:` 键路径。
2. 选择标记类型：`BarMark`、`LineMark`、`PointMark`、`AreaMark`、`RuleMark`、`RectangleMark`、`SectorMark` 或 `SurfacePlot`。
3. 将 2D 标记包裹在 `Chart` 中；仅对真实空间或表面数据使用 `Chart3D`。
4. 编码视觉通道：`.foregroundStyle(by:)`、`.symbol(by:)`、`.lineStyle(by:)`。
5. 使用 `.chartXAxis` / `.chartYAxis` 配置轴。
6. 使用 `.chartXScale(domain:)` / `.chartYScale(domain:)` 设置刻度域。
7. 根据需要添加选择、滚动或注释。
8. 对于 1000+ 个 2D 数据点，使用矢量图 (`BarPlot`、`LinePlot` 等)。
9. 渲染代表性的空、典型、密集、大文本、高对比度和 VoiceOver 状态；当存在选择和滚动时进行测试。
10. 如果编码、轴、选择或无障碍访问检查失败，请恢复数据样本，修复一个层，然后重新运行相同的矩阵，然后再添加装饰。

### 2. 审查现有图表代码

在判断标记选择之前，先确定数据语义。然后通过标记、刻度、轴、样式、选择和无障碍访问输出跟踪每个值；运行与新图表相同的验证矩阵。

## 图表容器

```swift
Chart(sales) { item in
    BarMark(x: .value("Month", item.month), y: .value("Revenue", item.revenue))
}
```

使用数据驱动初始化器进行单个集合。使用内容闭包进行混合标记或多个系列，并在元素不是 `Identifiable` 时传递 `id:`。加载 [references/charts-patterns.md](references/charts-patterns.md) 获取完整的混合系列、主题、无障碍访问和 3D 配方。

## 标记类型

### BarMark (iOS 16+)

```swift
// 垂直条形图
BarMark(x: .value("Month", item.month), y: .value("Sales", item.sales))

// 按类别堆叠（当相同的 x 映射到多个条形时自动堆叠）
BarMark(x: .value("Month", item.month), y: .value("Sales", item.sales))
    .foregroundStyle(by: .value("Product", item.product))

// 水平条形图
BarMark(x: .value("Sales", item.sales), y: .value("Month", item.month))

// 区间条形图（甘特图）
BarMark(
    xStart: .value("Start", item.start),
    xEnd: .value("End", item.end),
    y: .value("Task", item.task)
)
```

### LineMark (iOS 16+)

```swift
// 单线
LineMark(x: .value("Date", item.date), y: .value("Price", item.price))

// 多系列通过前景样式编码
LineMark(x: .value("Date", item.date), y: .value("Temp", item.temp))
    .foregroundStyle(by: .value("City", item.city))
    .interpolationMethod(.catmullRom)

// 多系列使用显式系列参数
LineMark(
    x: .value("Date", item.date),
    y: .value("Price", item.price),
    series: .value("Ticker", item.ticker)
)
```

### PointMark (iOS 16+)

```swift
PointMark(x: .value("Height", item.height), y: .value("Weight", item.weight))
    .foregroundStyle(by: .value("Species", item.species))
    .symbol(by: .value("Species", item.species))
    .symbolSize(100)
```

### AreaMark (iOS 16+)

```swift
// 堆叠区域
AreaMark(x: .value("Date", item.date), y: .value("Sales", item.sales))
    .foregroundStyle(by: .value("Category", item.category))

// 范围带
AreaMark(
    x: .value("Date", item.date),
    yStart: .value("Min", item.min),
    yEnd: .value("Max", item.max)
)
.opacity(0.3)
```

### RuleMark (iOS 16+)

```swift
RuleMark(y: .value("Target", 9000))
    .foregroundStyle(.red)
    .lineStyle(StrokeStyle(dash: [5, 3]))
    .annotation(position: .top, alignment: .leading) {
        Text("Target").font(.caption).foregroundStyle(.red)
    }
```

### RectangleMark (iOS 16+)

```swift
RectangleMark(x: .value("Hour", item.hour), y: .value("Day", item.day))
    .foregroundStyle(by: .value("Intensity", item.intensity))
```

### SectorMark (iOS 17+)
使用 `SectorMark` 仅用于严格正值的场景；在饼图或甜甜圈外过滤、聚合或解释零/负值。

```swift
// 饼图
Chart(data, id: \.name) { item in
    SectorMark(angle: .value("Sales", item.sales))
        .foregroundStyle(by: .value("Category", item.name))
}

// 甜甜圈图
Chart(data, id: \.name) { item in
    SectorMark(
        angle: .value("Sales", item.sales),
        innerRadius: .ratio(0.618),
        outerRadius: .inset(10),
        angularInset: 1
    )
    .cornerRadius(4)
    .foregroundStyle(by: .value("Category", item.name))
}
```

## 轴自定义

```swift
// 隐藏轴
.chartXAxis(.hidden)
.chartYAxis(.hidden)

// 自定义轴内容
.chartXAxis {
    AxisMarks(values: .stride(by: .month)) { value in
        AxisGridLine()
        AxisTick()
        AxisValueLabel(format: .dateTime.month(.abbreviated))
    }
}

// 多个 AxisMarks 组合（网格和标签使用不同的间隔）
.chartXAxis {
    AxisMarks(values: .stride(by: .day)) { _ in AxisGridLine() }
    AxisMarks(values: .stride(by: .week)) { _ in
        AxisTick()
        AxisValueLabel(format: .dateTime.week())
    }
}

// 轴标签（标题）
.chartXAxisLabel("Time", position: .bottom, alignment: .center)
.chartYAxisLabel("Revenue ($)", position: .leading, alignment: .center)
```

## 刻度配置

```swift
.chartYScale(domain: 0...100)                          // 显式数值域
.chartYScale(domain: .automatic(includesZero: true))   // 包含零
.chartYScale(domain: 1...10000, type: .log)            // 对数刻度
.chartXScale(domain: ["Mon", "Tue", "Wed", "Thu"])     // 分类排序
```

## 前景样式和编码

```swift
BarMark(...).foregroundStyle(.blue)                                    // 静态颜色
BarMark(...).foregroundStyle(by: .value("Category", item.category))   // 数据编码
AreaMark(...).foregroundStyle(                                         // 渐变
    .linearGradient(colors: [.blue, .cyan], startPoint: .bottom, endPoint: .top)
)
```

## 选择 (iOS 17+)

```swift
@State private var selectedDate: Date?
@State private var selectedRange: ClosedRange<Date>?
@State private var selectedAngle: Double?

// 点选择
Chart(data) { item in
    LineMark(x: .value("Date", item.date), y: .value("Value", item.value))
}
.chartXSelection(value: $selectedDate)

// 范围选择
.chartXSelection(range: $selectedRange)

// 角度选择绑定可绘制的角度值；从范围中推导出类别。
.chartAngleSelection(value: $selectedAngle)
```

## 可滚动的图表 (iOS 17+)

```swift
Chart(dailyData) { item in
    BarMark(x: .value("Date", item.date, unit: .day), y: .value("Steps", item.steps))
}
.chartScrollableAxes(.horizontal)
.chartXVisibleDomain(length: 3600 * 24 * 7) // 7 天可见
.chartScrollPosition(initialX: latestDate)
.chartScrollTargetBehavior(
    .valueAligned(matching: DateComponents(hour: 0), majorAlignment: .page)
)
```

## 注释

```swift
BarMark(x: .value("Month", item.month), y: .value("Sales", item.sales))
    .annotation(position: .top, alignment: .center, spacing: 4) {
        Text("\(item.sales, format: .number)").font(.caption2)
    }

// 溢出解决
.annotation(
    position: .top,
    overflowResolution: .init(x: .fit(to: .chart), y: .padScale)
) { Text("Label") }
```

## 图例

```swift
.chartLegend(.hidden)                                           // 隐藏
.chartLegend(position: .bottom, alignment: .center, spacing: 10) // 定位
.chartLegend(position: .bottom) {                                // 自定义
    HStack {
        ForEach(categories, id: \.self) { cat in
            Label(cat, systemImage: "circle.fill").font(.caption)
        }
    }
}
```

## 矢量图 (iOS 18+)

用于大型数据集（1000+ 个点）。接受整个集合或函数。

```swift
// 数据驱动
Chart {
    BarPlot(sales, x: .value("Month", \.month), y: .value("Revenue", \.revenue))
        .foregroundStyle(\.barColor)
}

// 函数绘图：y = f(x)
Chart {
    LinePlot(x: "x", y: "y", domain: -5...5) { x in sin(x) }
}

// 参数化：(x, y) = f(t)
Chart {
    LinePlot(x: "x", y: "y", t: "t", domain: 0...(2 * .pi)) { t in
        (x: cos(t), y: sin(t))
    }
}
```

在简单值修饰符之前应用基于 KeyPath 的修饰符：

```swift
BarPlot(data, x: .value("X", \.x), y: .value("Y", \.y))
    .foregroundStyle(\.color)    // KeyPath 优先
    .opacity(0.8)                // 值修饰符其次
```

## 3D 图表 (iOS 26+)

使用 `Chart3D` 仅用于真实 3D 数据或表面，而不是作为普通 2D 分类或时间序列图表的装饰性替代。`Chart3D` 接受 `SurfacePlot` 以及 `PointMark`、`RuleMark` 和 `RectangleMark` 的 3D 初始化器。

```swift
@State private var pose: Chart3DPose = .default

Chart3D {
    SurfacePlot(x: "x", y: "y", z: "z") { x, z in
        sin(2 * x) * cos(2 * z)
    }
    .foregroundStyle(.heightBased)
}
.chartXScale(domain: -2...2)
.chartYScale(domain: -1...1)
.chartZScale(domain: -2...2)
.chart3DPose($pose)
```

## 常见错误

### 1. 多线图表缺少系列参数

```swift
// 错误 -- 所有点连接成一条线
Chart {
    ForEach(allCities) { item in
        LineMark(x: .value("Date", item.date), y: .value("Temp", item.temp))
    }
}

// 正确 -- 每个城市有单独的线
Chart {
    ForEach(allCities) { item in
        LineMark(x: .value("Date", item.date), y: .value("Temp", item.temp))
            .foregroundStyle(by: .value("City", item.city))
    }
}
```

### 2. SectorMark 切片过多

```swift
// 错误 -- 20 个小切片难以阅读
Chart(twentyCategories, id: \.name) { item in
    SectorMark(angle: .value("Value", item.value))
}

// 正确 -- 分组为前 5 个 + "其他"
Chart(groupedData, id: \.name) { item in
    SectorMark(angle: .value("Value", item.value))
        .foregroundStyle(by: .value("Category", item.name))
}
```

### 3. 零基线重要时缺少刻度域

```swift
// 错误 -- 轴从 ~95 开始；小变化看起来很剧烈
Chart(data) {
    LineMark(x: .value("Day", $0.day), y: .value("Score", $0.score))
}

// 正确 -- 显式域以诚实的表示
Chart(data) {
    LineMark(x: .value("Day", $0.day), y: .value("Score", $0.score))
}
.chartYScale(domain: 0...100)
```

### 4. 静态前景样式覆盖数据编码

```swift
// 错误 -- 静态颜色覆盖按值编码
BarMark(x: .value("X", item.x), y: .value("Y", item.y))
    .foregroundStyle(by: .value("Category", item.category))
    .foregroundStyle(.blue)

// 正确 -- 仅使用数据编码
BarMark(x: .value("X", item.x), y: .value("Y", item.y))
    .foregroundStyle(by: .value("Category", item.category))
```

### 5. 10,000+ 个数据点的单个标记

```swift
// 错误 -- 创建 10,000 个标记视图；速度慢
Chart(largeDataset) { item in
    PointMark(x: .value("X", item.x), y: .value("Y", item.y))
}

// 正确 -- 矢量图 (iOS 18+)
Chart {
    PointPlot(largeDataset, x: .value("X", \.x), y: .value("Y", \.y))
}
```

### 6. 固定图表高度破坏 Dynamic Type

```swift
// 错误 -- 在大文本尺寸时剪切轴标签
Chart(data) { ... }
    .frame(height: 200)

// 正确 -- 适应尺寸
Chart(data) { ... }
    .frame(minHeight: 200, maxHeight: 400)
```

### 7. 矢量图上值修饰符后的 KeyPath 修饰符

```swift
// 错误 -- 编译器错误
BarPlot(data, x: .value("X", \.x), y: .value("Y", \.y))
    .opacity(0.8)
    .foregroundStyle(\.color)

// 正确 -- KeyPath 修饰符优先
BarPlot(data, x: .value("X", \.x), y: .value("Y", \.y))
    .foregroundStyle(\.color)
    .opacity(0.8)
```

### 8. 缺少无障碍访问标签

```swift
// 错误 -- VoiceOver 用户无法获取上下文
Chart(data) {
    BarMark(x: .value("Month", $0.month), y: .value("Sales", $0.sales))
}

// 正确 -- 添加每个标记的无障碍访问
Chart(data) { item in
    BarMark(x: .value("Month", item.month), y: .value("Sales", item.sales))
        .accessibilityLabel("\(item.month)")
        .accessibilityValue("\(item.sales) units sold")
}
```

### 9. 将角度选择视为类别选择

`chartAngleSelection(value:)` 绑定选中的可绘制角度值。对于饼图和甜甜圈图，在将其与类别标签进行比较之前，通过累积扇区范围映射该数值。

## 审查清单

- [ ] 数据模型使用 `Identifiable` 或图表使用 `id:` 键路径
- [ ] 标记类型与目标匹配（条形图=比较，线图=趋势，扇区图=比例）
- [ ] 多系列线图使用 `series:` 参数或 `.foregroundStyle(by:)`
- [ ] 轴配置了适当的标签、刻度和网格线
- [ ] 刻度域在零基线重要时显式设置
- [ ] 饼图/甜甜圈使用正值、5-7 个扇区以及 "其他" 分组
- [ ] 选择绑定类型与轴数据类型匹配（`Date?` 对于日期轴）
- [ ] 饼图/甜甜圈角度选择将数值角度值映射回类别
- [ ] 可滚动的图表设置了 `.chartXVisibleDomain(length:)` 以定义视口
- [ ] 矢量图用于超过 1000 个数据点的数据集
- [ ] 矢量图上 KeyPath 修饰符在值修饰符之前应用
- [ ] 仅在真实 3D 数据或表面时使用 `Chart3D`，并审查 z 刻度和姿态
- [ ] 为 VoiceOver 添加标记的无障碍访问标签
- [ ] 使用 Dynamic Type 和 Dark Mode 测试图表
- [ ] 图例可见且定位，或有意隐藏
- [ ] 确保图表数据模型类型是 Sendable；在 @MainActor 上更新图表数据

## 参考资料

- 扩展模式：[references/charts-patterns.md](references/charts-patterns.md)
- Apple 文档：[Swift Charts](https://sosumi.ai/documentation/charts)
- Apple 文档：[使用 Swift Charts 创建图表](https://sosumi.ai/documentation/charts/Creating-a-chart-using-Swift-Charts)
- Apple 文档：[Swift Charts 更新](https://sosumi.ai/documentation/updates/swiftcharts)
- Apple 文档：[Chart3D](https://sosumi.ai/documentation/charts/Chart3D)
- Apple 文档：[SurfacePlot](https://sosumi.ai/documentation/charts/SurfacePlot)
