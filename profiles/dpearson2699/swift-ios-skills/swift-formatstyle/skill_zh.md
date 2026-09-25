# Swift FormatStyle

使用 Foundation 的类型安全的 `FormatStyle` API 进行面向用户的显示，并在必须接受相同约定的输入时使用 `ParseableFormatStyle`。将字符串目录、复数形式、本地化文本、捆绑包和 RTL 布局路由到 `ios-localization`；即使没有文本被翻译，格式化仍然需要区域设置审查。

## 内容

- [工作流程](#workflow)
- [快速参考](#quick-reference)
- [选择和可用性](#selection-and-availability)
- [解析](#parsing)
- [SwiftUI 集成](#swiftui-integration)
- [自定义 FormatStyle](#custom-formatstyle)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 工作流程

1. 识别值的语义类型以及输出是仅用于显示还是必须通过解析进行往返。
2. 选择最窄的内置样式，并保持用户的当前区域设置，除非线格式明确要求另一个区域设置。
3. 使用代表性区域设置（如 `en_US`、`de_DE`、`ar_SA` 和 `ja_JP`）渲染确切的 UI。
4. 检查分隔符、数字系统、日历、货币和单位约定、文本方向和布局。
5. 如果输出或解析失败，请修复样式或周围的文本，恢复输入固定内容，并重新运行相同的区域设置矩阵。

当实现需要具体修饰符、日期间隔、相对日期、持续时间模式、测量值、名称、列表、字节计数或 URL 组件控制时，加载 [FormatStyle 菜单](references/formatstyle-recipes.md)。

## 快速参考

| 值 | 默认样式 | 重要约束 |
|---|---|---|
| `Int`、`Double` | `.number` | 仅按需配置精度、舍入、分组、符号或表示法。 |
| `Decimal` | `.number`、`.percent`、`.currency(code:)` | 优先用于精确的小数显示和解析。 |
| 货币 | `.currency(code:)` | 传递 ISO 4217 代码；切勿硬编码符号。 |
| 百分比 | `.percent` | 确认输入是分数（`0.85`）还是整数百分比（`85`）。 |
| `Date` | `.dateTime`、`.relative`、`.interval` | 相对输出通常应独立存在，而不是嵌入句子中。 |
| `Duration` | `.time(pattern:)`、`.units(allowed:width:)` | 需要 iOS 16+；选择紧凑时钟输出与标记单位。 |
| `Measurement` | `.measurement(width:usage:)` | `usage:` 控制区域设置感知转换策略。 |
| `PersonNameComponents` | `.name(style:)` | 不要手动连接名称部分。 |
| 集合 | `.list(type:width:)` | 让区域设置规则选择分隔符和连接词。 |
| 字节计数 | `.byteCount(style:)` | 故意选择文件、内存、十进制或二进制语义。 |
| `URL` | `.url` | 需要 iOS 16+；查询、端口和片段是可选的显示组件。 |

## 选择和可用性

- 优先使用 `FormatStyle` 而不是遗留的 `NumberFormatter`、`DateFormatter`、`DateComponentsFormatter` 和手动插值，用于新的 iOS 15+ 代码。
- `Duration` 格式样式和 `URL.FormatStyle` 需要 iOS 16+。
- `Date.AnchoredRelativeFormatStyle` 需要 iOS 18+，并相对于固定锚点而不是当前时刻进行格式化。
- 对于正常 UI，请省略 `.locale(...)`，以便样式继承用户的区域设置。仅当用于显式协议或测试固定内容时，才使用固定区域设置。
- 将相对日期输出视为独立文本，除非整个句子围绕它进行了本地化。

文档：[FormatStyle](https://sosumi.ai/documentation/foundation/formatstyle)

## 解析

当用户编辑或导入格式化值时，使用匹配的解析样式：

```swift
let style = Decimal.FormatStyle.Currency(code: "USD")
    .locale(Locale(identifier: "en_US"))

let value = try Decimal("$3,500.63", format: style)
let display = value.formatted(style)
```

上面的固定区域设置是适当的，仅仅是因为输入合同明确为 `en_US`。对于正常 UI 输入，使用用户的区域设置，并使用代表性十进制分隔符、货币位置、日历和数字系统测试往返。

## SwiftUI 集成

优先使用 `Text(_:format:)`，以便 SwiftUI 拥有格式化的值：

```swift
Text(price, format: .currency(code: currencyCode))
Text(date, format: .dateTime.month().day().year())
Text(duration, format: .units(allowed: [.minutes, .seconds]))
```

对于每个面向用户的格式化 `Text`，在区域设置矩阵中预览或测试确切的屏幕。使用 `Text(.now, style: .timer)`、`Text(.now, style: .relative)` 或 `Text(timerInterval:)` 用于实时更新的时间显示，而不是手动安排字符串刷新。

## 自定义 FormatStyle

仅在内置组合无法表达领域约定时创建自定义样式。`FormatStyle` 继承自 `Codable` 和 `Hashable`；将样式作为可重用值，仅在输入必须往返时添加 `ParseableFormatStyle`。

```swift
struct AbbreviatedCountStyle: FormatStyle {
    func format(_ value: Int) -> String {
        switch value {
        case ..<1_000: "\(value)"
        case 1_000..<1_000_000: String(format: "%.1fK", Double(value) / 1_000)
        default: String(format: "%.1fM", Double(value) / 1_000_000)
        }
    }
}

extension FormatStyle where Self == AbbreviatedCountStyle {
    static var abbreviatedCount: Self { .init() }
}
```

自定义样式仍然需要区域设置和无障碍审查；紧凑的英文后缀可能不适合每个区域设置。

## 常见错误

| 错误 | 修复 |
|---|---|
| 视图代码中的手动格式化或遗留格式器分配 | 使用匹配的 `FormatStyle` 和 `Text(_:format:)`。 |
| 硬编码货币符号或区域设置 | 传递 ISO 货币代码并继承用户区域设置，除非合同另有说明。 |
| 二进制浮点数用于精确小数输入 | 使用 `Decimal.FormatStyle` 及其匹配的解析策略。 |
| 假设 `URL.formatted()` 保留每个组件 | 仅当这些组件应显示时，才选择 `.port(.always)`、`.query(.always)` 或 `.fragment(.always)`。 |
| 相对日期输出嵌入在更大的句子中 | 保持其独立或本地化整个句子。 |
| 用于散文的时钟样式持续时间 | 使用 `.units(allowed:width:)` 用于标记输出。 |
| 测量转换留隐式 | 选择适用于 UI 的 `usage:`。 |
| 单区域设置快速检查 | 在代表性区域设置中运行相同的精确屏幕固定内容，并修复/重新运行失败。 |

## 审查清单

- [ ] 识别了语义值类型和显示与解析要求
- [ ] 在可以表达约定时使用内置 `FormatStyle`
- [ ] iOS 16+ 和 iOS 18+ API 的可用性受限制
- [ ] 货币使用 ISO 4217 代码；精确小数值使用 `Decimal`
- [ ] 继承用户区域设置，除非协议明确固定
- [ ] 相对日期文本独立存在或整个句子被本地化
- [ ] URL 组件和测量 `usage:` 是故意的
- [ ] SwiftUI 使用 `Text(_:format:)` 用于格式化值
- [ ] 确切的渲染 UI 和解析往返通过代表性区域设置矩阵

## 参考资料

- 详细菜单和修饰符：[references/formatstyle-recipes.md](references/formatstyle-recipes.md)
- Apple 文档：[FormatStyle](https://sosumi.ai/documentation/foundation/formatstyle) · [ParseableFormatStyle](https://sosumi.ai/documentation/foundation/parseableformatstyle) · [Date.FormatStyle](https://sosumi.ai/documentation/foundation/date/formatstyle) · [Duration.TimeFormatStyle](https://sosumi.ai/documentation/swift/duration/timeformatstyle) · [URL.FormatStyle](https://sosumi.ai/documentation/foundation/url/formatstyle)
