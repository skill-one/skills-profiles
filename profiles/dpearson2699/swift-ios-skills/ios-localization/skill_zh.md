# iOS 本地化与国际化

使用字符串目录、现代字符串类型、区域设置感知格式化和从右到左布局来本地化 Apple 平台应用程序。

## 目录

- [字符串目录和生成的符号](#string-catalogs-and-generated-symbols)
- [字符串类型 -- 决策指南](#string-types-decision-guide)
- [本地化字符串中的字符串插值](#string-interpolation-in-localized-strings)
- [复数形式](#pluralization)
- [FormatStyle -- 区域设置感知格式化](#formatstyle-locale-aware-formatting)
- [从右到左 (RTL) 布局](#right-to-left-rtl-layout)
- [常见错误](#common-mistakes)
- [本地化审查清单](#review-checklist)
- [参考资料](#references)

## 字符串目录和生成的符号

字符串目录是 Xcode 15+ 的新本地化工作的推荐工作流程。它们将可本地化字符串、复数规则和设备变体保存在 Xcode 管理的 JSON 文件中，并配有可视化编辑器。在迁移过程中，遗留的 `.strings` 和 `.stringsdict` 文件可以共存，但新的 Swift 和 SwiftUI 代码应默认使用字符串目录。

**自动提取的工作原理：**

Xcode 在每次构建时扫描以下模式：

```swift
// SwiftUI -- 自动提取 (LocalizedStringKey)
Text("Welcome back")              // key: "Welcome back"
Label("Settings", systemImage: "gear")
Button("Save") { }
Toggle("Dark Mode", isOn: $dark)

// 编程式 -- 自动提取
String(localized: "No items found")
LocalizedStringResource("Order placed")

// 纯字符串：不提取或本地化
let msg = "Hello"
```

Xcode 会自动将发现的键添加到字符串目录中。在编辑器中将翻译标记为 Needs Review、Translated 或 Stale。

有关详细的字符串目录工作流程、迁移和测试策略，请参阅 [参考资料/string-catalogs.md](references/string-catalogs.md)。

生成的符号是 Xcode 26 在字符串目录之上的类型化访问层；它们不会改变目录在 Xcode 15 中的可用性。

**启用：** 构建设置 > 本地化 > 生成字符串目录符号 → `是`（在新的 Xcode 26 项目中默认启用）。需要目录格式版本 `1.1`。

**工作流程：** 通过字符串目录编辑器中的 (+) 按钮手动添加键——手动键默认启用 **生成 Swift 符号** 复选框。自动提取的键也可以通过 Refactor > Convert Strings to Symbols 选择加入。使用稳定的手动键用于生成的符号字符串。避免使用源复制派生的键用于 API 面向的字符串，因为措辞编辑可能会重命名生成的标识符并导致调用点混乱。

```swift
// 从 "room_available" 键生成 Localizable.xcstrings
Text(.roomAvailable)

// 参数化键 "landmarks_count" 使用 %1$(count)lld
Text(.landmarksCount(count: 42))

// 非默认表 "Booking.xcstrings"
Text(.Booking.confirmBookingCta)
```

Xcode 通过将键驼峰化来派生符号名称：`settings.notifications.toggle` → `.settingsNotificationsToggle`。您可以通过 Refactor > Convert Strings to Symbols 将现有的提取字符串转换为符号（可逆）。

生成的符号是 `internal`。对于跨模块访问，请创建一个公共包装扩展。对于更重的多模块设置，请使用 [xcstrings-tool](https://github.com/liamnichols/xcstrings-tool)。

有关完整的生成符号参考资料——提取状态、符号派生规则和跨模块模式，请参阅 [参考资料/string-catalogs.md](references/string-catalogs.md)。

## 字符串类型 -- 决策指南

| 上下文 | 类型 | 原因 |
|---|---|---|
| SwiftUI 视图文本 | `LocalizedStringKey` (隐式) | SwiftUI 执行查找 |
| 视图模型、服务和错误 | `String(localized:)` | 现在解析为 `String` |
| App Intents、小部件和延迟系统 UI | `LocalizedStringResource` | 在显示时携带本地化信息 |
| 非用户可见的日志和分析 | 纯 `String` | 无需本地化 |

### LocalizedStringKey (SwiftUI 默认)

SwiftUI 视图接受 `LocalizedStringKey` 作为其文本参数。字符串字面量会被隐式转换——无需额外工作。

```swift
Text("Welcome back")
Button("Delete") { deleteItem() }
```

在将字符串直接传递给 SwiftUI 视图初始化器时使用 `LocalizedStringKey`。在大多数情况下，不要手动构造 `LocalizedStringKey`。

### String(localized:) -- 现代 `NSLocalizedString` 替代方案

用于 SwiftUI 视图初始化器之外的任何本地化字符串。返回一个纯 `String`。字面量/插值初始化器在 iOS 15+ 中可用；解析 `LocalizedStringResource` 在 iOS 16+ 中可用。

```swift
let title = String(localized: "Welcome back")
let msg = String(localized: "error.network",
                 defaultValue: "Check your internet connection")
```

对于 Swift 包本地化失败，在捆绑包调试之前，请使用此显式资源清单回答：
1. `Package.swift` 声明了 `defaultLocalization`。
2. 目标 `resources` 列表处理了目录位置，例如 `.process("Resources")`。
3. `Localizable.xcstrings` 实际位于该处理的目标资源路径中。
只有通过这些步骤后，才能使用 `bundle: .module` 或 `Text(..., bundle: .module)` 进行查找调试。

现有的 `NSLocalizedString` 字面量键仍然可以通过 Xcode 工具导出或迁移，但新的 Swift 代码应优先使用 `String(localized:)`、SwiftUI 字面量、`LocalizedStringResource` 或生成的符号。

### LocalizedStringResource -- 无需解析即可传递本地化信息

当字符串必须作为本地化值传递以供后续解析时使用，特别是对于 App Intents、小部件、通知、生成的本地化符号和直接接受 `LocalizedStringResource` 的系统 API。当代码需要立即获取解析后的字符串时，请使用 `String(localized:)`。在 iOS 16+ 中可用。

```swift
struct OrderCoffeeIntent: AppIntent {
    static var title: LocalizedStringResource = "Order Coffee"
}

func showAlert(title: LocalizedStringResource, message: LocalizedStringResource) {
    let resolved = String(localized: title)
}
```

## 本地化字符串中的字符串插值

本地化字符串中的插值值成为位置参数，翻译人员可以重新排序。

```swift
// 英语: "Welcome, Alice! You have 3 new messages."
// 德语: "Willkommen, Alice! Sie haben 3 neue Nachrichten."
// 日语: "Alice さん、新しいメッセージが 3 件あります。"
let text = String(localized: "Welcome, \(name)! You have \(count) new messages.")
```

在字符串目录中，这会显示为带有 `%@` 和 `%lld` 占位符，翻译人员可以重新排序：
- 英语: `"Welcome, %@! You have %lld new messages."`
- 日语: `"%@さん、新しいメッセージが%lld件あります。"`

**类型安全的插值**（优先于格式说明符）：
```swift
// 插值提供类型安全性
String(localized: "Score: \(score, format: .number)")
String(localized: "Due: \(date, format: .dateTime.month().day().year())")
```

## 复数形式

字符串目录原生处理复数形式——无需 `.stringsdict` XML。

### 字符串目录中的设置

当本地化字符串包含整数插值时，Xcode 会检测到它并在字符串目录编辑器中提供复数变体。为每个 CLDR 复数类别提供翻译：

| 类别 | 英语示例 | 阿拉伯语示例 |
|------|----------|--------------|
| zero | (未使用) | 0 项 |
| one | 1 项 | 1 项 |
| two | (未使用) | 2 项（双数） |
| few | (未使用) | 3-10 项 |
| many | (未使用) | 11-99 项 |
| other | 2+ 项 | 100+ 项 |

英语只使用 `one` 和 `other`。阿拉伯语使用所有六个。始终提供 `other` 作为后备。

```swift
// 代码 -- 单个插值触发复数支持
Text("\(unreadCount) unread messages")

// 字符串目录条目（英语）：
//   one:   "%lld unread message"
//   other: "%lld unread messages"
```

### 设备变体

字符串目录支持特定设备的文本（iPhone 与 iPad 与 Mac）：

```swift
// 在字符串目录编辑器中，为键启用 "按设备变化"
// iPhone: "Tap to continue"
// iPad:   "Tap or click to continue"
// Mac:    "Click to continue"
```

当附近单词必须根据值的数量或性别进行屈折时，请使用 Foundation 的自动语法一致标记。保留完整的屈折短语供翻译人员使用；请参阅 [自动语法一致](https://sosumi.ai/documentation/foundation/automatic-grammar-agreement)。

## FormatStyle -- 区域设置感知格式化

不要硬编码用户可见的格式。使用 `FormatStyle` 并在对比鲜明的区域设置（如 `en_US`、`de_DE`、`ar_SA` 和 `ja_JP`）下测试输出。

`ios-localization` 拥有 `FormatStyle` 指导，当问题是区域设置感知的用户可见显示时，包括数字、日期、货币、单位、名称、列表、日历、分隔符和区域设置预览/测试。对于自定义 `FormatStyle`、`ParseableFormatStyle`、解析、`Date.IntervalFormatStyle`、`URL.FormatStyle` 或可重用格式器 API 设计，请路由到 `swift-formatstyle`；将 `ios-localization` 建议保留为区域设置风险和测试，除非明确请求实现。

### 日期

```swift
let now = Date.now

// 预设样式
now.formatted(date: .long, time: .shortened)
// 美国: "January 15, 2026 at 3:30 PM"
// 德国: "15. Januar 2026 um 15:30"
// 日本: "2026年1月15日 15:30"

// 基于组件
now.formatted(.dateTime.month(.wide).day().year())
// 美国: "January 15, 2026"

// 在 SwiftUI 中
Text(now, format: .dateTime.month().day().year())
```

### 数字

```swift
let count = 1234567
count.formatted()                     // "1,234,567" (美国) / "1.234.567" (德国)
count.formatted(.number.precision(.fractionLength(2)))
count.formatted(.percent)             // 对于 0.85 -> "85%" (美国) / "85 %" (法国)

// 货币
let price = Decimal(29.99)
price.formatted(.currency(code: "USD"))  // "$29.99" (美国) / "29,99 $US" (法国)
price.formatted(.currency(code: "EUR"))  // "29,99 EUR" (德国)
```

### 测量

```swift
let distance = Measurement(value: 5, unit: UnitLength.kilometers)
distance.formatted(.measurement(width: .wide))
// 美国: "3.1 英里" (自动转换!) / 德国: "5 Kilometer"

let temp = Measurement(value: 22, unit: UnitTemperature.celsius)
temp.formatted(.measurement(width: .abbreviated))
// 美国: "72 F" (自动转换!) / 法国: "22 C"
```

加载 [参考资料/formatstyle-locale.md](references/formatstyle-locale.md) 以获取持续时间、名称、列表、自定义样式、变体矩阵和更深的 RTL 测试。

## 从右到左 (RTL) 布局

SwiftUI 自动镜像 RTL 语言（阿拉伯语、希伯来语、乌尔都语、波斯语）的布局。大多数视图无需更改。

### SwiftUI 自动镜像的内容

- `HStack` 子项反转顺序
- `.leading` / `.trailing` 对齐和填充交换位置
- `NavigationStack` 返回按钮移至 trailing 边缘
- `List` 揭示指示器翻转
- 文本对齐遵循阅读方向

### 需要手动注意的内容

```swift
// 在预览中测试 RTL
MyView()
    .environment(\.layoutDirection, .rightToLeft)
    .environment(\.locale, Locale(identifier: "ar"))

// 应该镜像的图像（方向箭头、进度指示器）
Image(systemName: "chevron.right")
    .flipsForRightToLeftLayoutDirection(true)

// 不应该镜像的图像：标志、照片、时钟、音符

// 强制 LTR 用于特定内容（电话号码、代码）
Text("+1 (555) 123-4567")
    .environment(\.layoutDirection, .leftToRight)
```

### 布局规则

- **要** 使用 `.leading` / `.trailing`——它们会自动镜像 RTL
- **不要** 使用 `.left` / `.right`——它们是固定的，会破坏 RTL
- **要** 使用 `HStack` / `VStack`——它们尊重布局方向
- **不要** 使用绝对 `offset(x:)` 用于方向定位

## 常见错误

### 不要：使用固定宽度布局
```swift
// 错误 -- 德语文本比英语长约 30%
Text(title).frame(width: 120)
```

### 要：使用灵活布局
```swift
// 正确
Text(title).fixedSize(horizontal: false, vertical: true)
// 或使用可以容纳扩展的 VStack/包装
```

### 不要：跳过伪本地化测试
仅在英语中测试会隐藏截断、布局和 RTL 错误。

### 要：至少使用德语（长）和阿拉伯语（RTL）进行测试
使用 Xcode 方案设置来覆盖应用程序语言，而无需更改设备区域设置。

## 审查清单

- [ ] 所有用户可见的字符串都使用本地化 (`LocalizedStringKey` 在 SwiftUI 或 `String(localized:)`)
- [ ] 不要对用户可见文本进行字符串连接
- [ ] 日期和数字使用 `FormatStyle`，而不是硬编码格式
- [ ] 复数形式通过字符串目录复数变体处理（如果可能，不要手动 if/else）
- [ ] 布局使用 `.leading` / `.trailing`，而不是 `.left` / `.right`
- [ ] 使用长文本（德语）和 RTL（阿拉伯语）测试 UI
- [ ] 字符串目录包含所有目标语言
- [ ] 需要RTL镜像的图像使用 `.flipsForRightToLeftLayoutDirection(true)`
- [ ] App Intents 和小部件使用 `LocalizedStringResource`
- [ ] 新代码中不要使用 `NSLocalizedString`
- [ ] 为模糊键提供注释（为翻译人员提供上下文）
- [ ] 使用 `@ScaledMetric` 用于必须与 Dynamic Type 一起缩放的间距
- [ ] 货币格式使用显式货币代码，而不是区域设置默认值
- [ ] 进行伪本地化测试（带重音、RTL、双长度）
- [ ] 手动管理的键使用稳定的符号样式名称，而不是英文文本作为键
- [ ] 为具有手动管理键的目标启用生成字符串目录符号
- [ ] 确保本地化字符串类型是 Sendable；使用 @MainActor 进行区域设置更改的 UI 更新

## 参考资料

- FormatStyle 模式：[参考资料/formatstyle-locale.md](references/formatstyle-locale.md)
- 字符串目录指南：[参考资料/string-catalogs.md](references/string-catalogs.md)
