这项技能通过比较精良、高质量的生产级 SwiftUI 应用与糟糕构建的应用，来编码设计原则。这里的模式代表了什么让一个应用感觉“正确”，而另一个应用的边距、间距和文本大小却感觉“不对”的原因。

在构建或修改 SwiftUI 界面、WidgetKit 小部件或任何原生 Apple UI 时，请始终应用这些原则。

## 核心理念

**节制胜于装饰。** 每个像素都必须有其价值。一个精良的应用使用更少的颜色、更少的字体大小、更少的间距值和更少的文字——但它们使用得一致。过度设计视觉元素（自定义渐变、装饰性边框、定制分隔符）会产生视觉噪音。原生组件和系统颜色则创造和谐。

**注意力是稀缺的。** 保持 UI 文本比你认为需要的更短。优先考虑一个清晰的标题和一个紧凑的辅助区块，而不是在标题、副标题、正文和页脚中重复解释。如果一个屏幕需要理由，把它放在一个有目的的地方，而不是分散在整页。

---

## 1. 间距系统：使用一致的网格

**关键**：使用基于 4 基础/8 基础的网格的间距值。永远不要使用任意值。

### 允许的间距值
```
4, 8, 12, 16, 20, 24, 32, 40, 48
```

### 不好（任意值导致视觉不和谐）
```swift
// 错误 - 这些数字之间没有关系
.padding(.bottom, 26)
.padding(.bottom, 34)
.padding(.bottom, 36)
HStack(spacing: 18)
.padding(14)
```

### 好（来自一致网格的值）
```swift
// 正确 - 眼睛可以跟随的预测节奏
.padding(.horizontal, 20)
.padding(.top, 8)
Spacer().frame(height: 32)
HStack(spacing: 4)  // 或 8, 12, 16
.padding(.vertical, 12)
.padding(.horizontal, 16)
```

### 标准填充分配
- **外部内容填充**：水平 16-20pt
- **主要部分之间**：垂直 24-32pt
- **分组组件内部**：4-12pt
- **卡片/行内部填充**：垂直 12-16pt，水平 16pt

---

## 2. 字体排版：通过权重而非仅大小建立层次

### 原则
使用**更少的字体大小**和**清晰的权重区分**。较大尺寸使用较轻的权重；较小尺寸使用中等/常规的权重。这创造了精致感，而不是视觉混乱。

### 推荐的字体比例（适用于数据导向的应用）
| 角色 | 大小 | 权重 | 备注 |
|------|------|------|------|
| 英雄数字 | 36-42pt | `.light` | 大但视觉上轻——优雅，不笨重 |
| 次要统计数据 | 20-24pt | `.light` | 与英雄相同的权重系列，但更小 |
| 正文/切换标签 | 15pt | `.regular` | 标准的 iOS 正文大小 |
| 章节标题（大写） | 11pt | `.medium` | 带有字距/字母间距 |
| 摘要/副标题 | 11-13pt | `.regular` | 次要信息 |

### 不好（太多大小，权重不一致）
```swift
// 错误 - 7 种不同的尺寸，没有明确的系统
.font(.system(size: 60, weight: .ultraLight))   // 英雄
.font(.system(size: 44, weight: .regular))        // 统计数据（太接近英雄）
.font(.system(size: 31, weight: .ultraLight))     // 百分号符号（奇怪的比率）
.font(.system(size: 18, weight: .regular))        // 标签（切换太大）
.font(.system(size: 14, weight: .regular))        // 标题
.font(.system(size: 13, weight: .regular))        // 另一个标题
.font(.system(size: 12, weight: .regular))        // 按钮（太小，难以阅读）
```

### 好（清晰的层次，更少尺寸）
```swift
// 正确 - 5 种尺寸，每个都有明确的目的
.font(.system(size: 42, weight: .light, design: .monospaced))    // 英雄
.font(.system(size: 24, weight: .light, design: .monospaced))    // 统计值
.font(.system(size: 15, weight: .regular, design: .monospaced))  // 正文
.font(.system(size: 14, weight: .regular, design: .monospaced))  // 次要
.font(.system(size: 11, weight: .medium, design: .monospaced))   // 标签
```

### 字体设计一致性
选择一种字体设计并在所有地方使用——应用和 Widget：
```swift
// 如果使用等宽字体，则在所有地方使用
design: .monospaced  // 应用视图、Widget、锁屏——所有它们

// 永远不要在应用和 Widget 之间混合设计
// 不好：应用中使用 .monospaced，锁屏 Widget 中使用 .rounded
```

### 字距（跟踪）
最多使用 2 个值，并且仅在大小写标签上使用：
```swift
.tracking(1.5)  // 章节标签："NOTIFICATIONS", "DAY", "LEFT"
.tracking(3)    // 导航/工具栏标题
```

**永远不要使用 3 个或更多不同的跟踪值**，如 `kerning(4)`、`kerning(4.5)`、`kerning(5)`——这些差异难以察觉，但不一致会在潜意识中体现出来。

### 标识符的数字格式化
年份和其他固定标识符不应使用区域分组。
```swift
// 正确 - 稳定、非分组的标识符文本
Text(String(year))                  // "2026"
Text(year, format: .number.grouping(.never))

// 错误 - 区域分组可能会渲染 "2,026"
Text("\(year)")
```

---

## 3. 颜色：系统语义颜色胜过硬编码值

### 原则
使用 SwiftUI 的语义颜色系统。它自动处理浅色/深色模式、可访问性，并看起来原生。硬编码颜色和手动不透明度值会产生维护噩梦，并看起来不自然。

### 不好（硬编码白色和十几个不透明度值）
```swift
// 错误 - 无法维护，不适应浅色模式
Color.black.ignoresSafeArea()           // 强制深色
Color.white.opacity(0.08)               // 环形背景
Color.white.opacity(0.09)               // 分隔符
Color.white.opacity(0.3)                // 年份文本
Color.white.opacity(0.32)               // 统计标签
Color.white.opacity(0.42)               // 百分号符号
Color.white.opacity(0.44)               // 切换色调
Color.white.opacity(0.72)               // 按钮文本
Color.white.opacity(0.88)               // 切换标签
Color.white.opacity(0.9)                // 统计值
Color.white.opacity(0.94)               // 环形填充
```

### 好（语义系统颜色）
```swift
// 正确 - 自动适应，看起来原生，易于维护
Color(.systemBackground)                 // 主要背景
Color(.secondarySystemBackground)        // 卡片/组背景
Color(.separator)                        // 分隔符（可选不透明度）
Color.primary                            // 主要文本和 UI 元素
.foregroundStyle(.secondary)              // 次要文本
.foregroundStyle(.tertiary)               // 标签、摘要
```

### 当你需要不透明度时
限制为 2-3 个值，并有明确的目的：
```swift
.opacity(0.15)  // 微妙的背景描边
.opacity(0.3)   // 分隔符线
// 就这些。如果你需要更多，你可能是在硬编码语义颜色可以处理的东西。
```

---

## 4. 组件尺寸：按比例，不要过大

### 进度环/圆形指示器
```swift
// 应用主视图：200x200，细描边
.frame(width: 200, height: 200)
Circle().stroke(..., lineWidth: 3)

// Widget（systemSmall）：90x90，相同的描边
.frame(width: 90, height: 90)
Circle().stroke(..., lineWidth: 3)

// 错误：过大的环，描边不一致
.frame(width: 260, height: 260)    // 太大，主导屏幕
Circle().stroke(..., lineWidth: 9)  // 背景
Circle().stroke(..., lineWidth: 8)  // 填充——为什么描边与背景不同？
```

### 描边宽度一致性
**始终对相同元素的背景和前景描边使用相同的 lineWidth：**
```swift
// 正确
Circle().stroke(background, lineWidth: 3)
Circle().trim(from: 0, to: fraction).stroke(fill, lineWidth: 3)

// 错误 - 创建视觉错位
Circle().stroke(background, lineWidth: 9)
Circle().trim(from: 0, to: fraction).stroke(fill, lineWidth: 8)
```

### 列表行和切换行
```swift
// 正确 - 自然尺寸，适当的填充
Toggle(isOn: $value) {
    Text(title)
        .font(.system(size: 15, weight: .regular, design: .monospaced))
}
.padding(.horizontal, 16)
.padding(.vertical, 12)

// 错误 - 固定过大的高度
HStack {
    Text(label)
        .font(.system(size: 18))   // 切换标签太大
    Spacer()
    Toggle("", isOn: $isOn)
        .labelsHidden()             // 为什么隐藏标签？正确使用 Toggle
}
.frame(height: 70)                  // 太高
```

---

## 5. 分组内容 & 卡片：使用系统模式

### 不好（过度设计的自定义卡片）
```swift
// 错误 - 自定义渐变、叠加边框、巨大的圆角半径
VStack { ... }
    .padding(.vertical, 4)              // 太紧
    .background(
        RoundedRectangle(cornerRadius: 22)   // 太圆
            .fill(LinearGradient(            // 不必要的渐变
                colors: [Color(white: 0.10), Color(white: 0.085)],
                startPoint: .topLeading, endPoint: .bottomTrailing
            ))
    )
    .overlay(
        RoundedRectangle(cornerRadius: 22)
            .stroke(Color.white.opacity(0.08), lineWidth: 1)  // 装饰性边框
    )
```

### 好（原生的分组样式）
```swift
// 正确 - 简单、原生，在浅色和深色模式下都有效
VStack(spacing: 0) {
    row1
    Divider().padding(.leading, 16)
    row2
    Divider().padding(.leading, 16)
    row3
}
.background(Color(.secondarySystemBackground))
.clipShape(.rect(cornerRadius: 10))
```

### 分组内容的关键规则
- **圆角半径**：卡片/组的 10pt（匹配 iOS 系统样式）。永远不要 22pt+。
- **分隔符**：使用系统的 `Divider()` 并带有 `.padding(.leading, 16)` 以实现 iOS 标准的嵌入。永远不要构建自定义分隔符结构。
- **卡片填充**：垂直 12-16pt，水平 16pt。永远不要垂直 4pt。
- **背景**：`Color(.secondarySystemBackground)`——标准卡片永远不要自定义渐变。

---

## 6. 导航：使用 NavigationStack

```swift
// 正确 - 正确的导航，带有最小的工具栏
NavigationStack {
    ScrollView {
        content
    }
    .toolbar {
        ToolbarItem(placement: .principal) {
            Text("Title")
                .font(.system(size: 13, weight: .medium, design: .monospaced))
                .tracking(3)
                .foregroundStyle(.tertiary)
        }
    }
    .navigationBarTitleDisplayMode(.inline)
}

// 错误 - 没有导航结构，只是一个 ZStack
ZStack {
    Color.black.ignoresSafeArea()
    ScrollView {
        VStack {
            Text("2026").font(...) // 手动放置的“标题”
            content
        }
    }
}
```

---

## 7. WidgetKit：使用原生组件

### 圆形锁屏小部件
```swift
// 正确 - 使用 Gauge，它是为此目的专门设计的
Gauge(value: entry.fraction) {
    Text("")
} currentValueLabel: {
    Text("\(Int(entry.percentage))%")
        .font(.system(size: 12, weight: .medium, design: .monospaced))
}
.gaugeStyle(.accessoryCircular)
.containerBackground(.fill.tertiary, for: .widget)

// 错误 - 锁屏手动绘制圆形
ZStack {
    Circle().stroke(Color.primary.opacity(0.18), lineWidth: 4)
    Circle().trim(from: 0, to: progress).stroke(...)
    Text(percentText)
        .font(.system(size: 14, weight: .bold, design: .rounded)) // 错误的字体设计！
}
```

### 矩形锁屏小部件
```swift
// 正确 - 使用 Gauge 并带有 linearCapacity
VStack(alignment: .leading, spacing: 4) {
    HStack {
        Text(year).font(.system(size: 13, weight: .semibold, design: .monospaced))
        Spacer()
        Text(percentage).font(.system(size: 13, weight: .medium, design: .monospaced))
            .foregroundStyle(.secondary)
    }
    Gauge(value: fraction) { Text("") }
        .gaugeStyle(.linearCapacity)
        .tint(.primary)
    HStack {
        Spacer()
        Text("\(dayOfYear)/\(totalDays)")
            .font(.system(size: 11, weight: .regular, design: .monospaced))
            .foregroundStyle(.secondary)
    }
}
.containerBackground(.fill.tertiary, for: .widget)

// 错误 - 自定义 GeometryReader 进度条
GeometryReader { proxy in
    ZStack(alignment: .leading) {
        RoundedRectangle(cornerRadius: 2).fill(Color.primary.opacity(0.16))
        RoundedRectangle(cornerRadius: 2).fill(Color.primary)
            .frame(width: max(2, proxy.size.width * progress))
    }
}
.frame(height: 6)
```

### 小部件背景
```swift
// 正确
.containerBackground(.fill.tertiary, for: .widget)

// 错误 - 硬编码颜色
.containerBackground(.black, for: .widget)
```

### 小部件系列覆盖
支持所有相关系列——不要跳过常见的系列：
```swift
.supportedFamilies([
    .accessoryCircular,      // 锁屏圆形
    .accessoryRectangular,   // 锁屏矩形
    .accessoryInline,        // 锁屏内联文本
    .systemSmall,            // 主屏幕小
    .systemMedium,           // 主屏幕中
    .systemLarge,            // 主屏幕大
])
```

### 跨系列视觉一致性
中号和大型主屏幕小部件应共享一致的结构布局：
- 标题：左侧年份，右侧百分比
- 中间：进度条
- 底部：右对齐的 `day/total`

除非有硬尺寸限制，否则不要为每个系列重新发明层次结构。

始终在主屏幕小部件中包含明确内部填充，以避免在圆角边缘附近剪切：
```swift
.padding(.horizontal, 12)
.padding(.vertical, 12)
```

### 小部件内存预算（硬限制）
小部件扩展有紧张的内存预算（通常在 30 MB 左右）。密集的视觉化可能会因为嵌套视图太多而被 `EXC_RESOURCE` 杀死。

```swift
// 正确 - 一次绘制密集点网格
Canvas { context, size in
    // 在这里绘制 365/366 个点
}

// 错误 - 数百个嵌套子视图（高内存开销）
LazyVGrid(columns: columns) {
    ForEach(1...366, id: \.self) { day in
        ZStack { Circle(); partialFillLayer }
    }
}
```

### 时间线刷新（匹配数据粒度）
```swift
// 正确 - 在午夜刷新，用于每日数据
let tomorrow = calendar.startOfDay(for: calendar.date(byAdding: .day, value: 1, to: now)!)
Timeline(entries: [entry], policy: .after(tomorrow))

// 正确 - 定期刷新，用于依赖于时间段的百分比/部分填充
let refresh = Calendar.current.date(byAdding: .minute, value: 15, to: now)!
Timeline(entries: [entry], policy: .after(refresh))

// 错误 - 每分钟刷新，用于静态每日数据
let tooFrequent = Calendar.current.date(byAdding: .minute, value: 1, to: now)!
Timeline(entries: [entry], policy: .after(tooFrequent))
```

---

## 8. 交互元素

### 切换
```swift
// 正确 - 使用 Toggle 并使用其内置标签，使用单个强调色进行色调
Toggle(isOn: $value) {
    Text(title)
        .font(.system(size: 15, weight: .regular, design: .monospaced))
}
.tint(.green)

// 错误 - 隐藏标签，使用手动 HStack 布局
HStack {
    Text(label).font(.system(size: 18))
    Spacer()
    Toggle("", isOn: $isOn)
        .labelsHidden()
        .tint(Color.white.opacity(0.44))  // 低对比度色调
}
```

### 互斥选项
当选项是互斥的（例如，每日/每周/每月的节奏）时，使用一个选定的值，而不是多个切换。

```swift
// 正确 - 单一事实来源
enum Cadence: String, CaseIterable { case daily, weekly, monthly }
@State private var cadence: Cadence = .daily

ForEach(Cadence.allCases, id: \.rawValue) { option in
    Button {
        cadence = option
    } label: {
        HStack {
            Image(systemName: cadence == option ? "checkmark.circle.fill" : "circle")
            Text(option.rawValue.capitalized)
        }
    }
}

// 正确 - 当内容共享时，使用一个预览操作
Button("Preview") { sendPreview() }

// 错误 - 独立切换允许矛盾状态
Toggle("Daily", isOn: $daily)
Toggle("Weekly", isOn: $weekly)
Toggle("Monthly", isOn: $monthly)
```

### 更改数字的动画过渡
```swift
// 添加到任何显示更改数值的 Text
Text(String(format: "%.2f", percentage))
    .contentTransition(.numericText())
```

---

## 9. 交互编辑器：集中几何和状态

交互编辑器（拼贴、裁剪、画布、媒体框架工具、布局选择器）比普通表单需要更严格的状态和布局纪律。

### 展示状态
从有效载荷状态呈现编辑器流程，而不是从单独的 `Bool` 加上独立管理的数据。

```swift
// 正确 - 仅在有效载荷存在时呈现
@State private var activeCropRequest: CropRequest?

.sheet(item: $activeCropRequest) { request in
    CropEditor(request: request)
}

// 错误 - 底层数据准备好之前，工具栏就可以打开
@State private var showCropEditor = false
@State private var selectedImage: UIImage?

.sheet(isPresented: $showCropEditor) {
    if let selectedImage { CropEditor(image: selectedImage) }
}
```

### 共享几何模型
如果应用预览可以平移/缩放/裁剪/布局，稍后导出结果，请使用一个共享的几何模型，用于预览和渲染。

```swift
// 正确 - 一个用于边界和变换的事实来源
let normalized = EditorGeometry.normalizedAdjustment(adjustment, imageSize: image.size, slotSize: slotSize)
let drawRect = EditorGeometry.drawRect(for: image.size, in: slotRect, adjustment: adjustment)

// 错误 - 预览和导出各自发明自己的数学
let previewOffset = ...
let exportOffset = ...
```

如果用户可以缩放足够以显示背景，那么这必须是共享几何模型的一个有意部分，而不是编辑器唯一的例外。

### 手势协调
点击、长按拖动和捏合不是独立的功能。在 SwiftUI 中，除非你明确建模它们之间的关系，否则它们会竞争。

- 使用单个交互状态来表示活动的瓦片/卡片/画布项。
- 确定哪个手势具有优先级，哪些应该同时运行。
- 故意重置临时手势状态，当选择更改时。
- 优先考虑一个连贯的状态机，而不是分散的绑定到单个手势的布尔值。

### 固定编辑器布局
如果屏幕不能滚动，请使用几个命名的区域自上而下预算垂直空间：
- 头部
- 画布阶段
- 设置区域
- 底部工具栏

将这种尺寸数学放在一个地方。不要让每个子视图发明自己的高度。

### 自定义标题和安全区域
如果你用自定义标题替换了系统导航栏：
- 明确说明父级是否已经尊重安全区域。
- 不要反射性地添加 `safeAreaInsets.top`；重复计算会导致明显的空白空间。
- 保持自定义标题紧凑。它们应该感觉像导航铬，而不是完整的内容部分。

### 设置界面
当编辑器有几种配置模式（`布局`、`边框`、`比例`、`背景`等）时，一次显示一个活动的设置界面，而不是在屏幕上堆叠每个控件。

这使画布在视觉上占主导地位，并使每个控件组更容易理解。
