# 应用意图 (iOS 26+)

实现、审查和扩展应用意图，以向Siri、快捷指令、Spotlight、小组件、控制中心和Apple Intelligence暴露应用功能。

## 目录

- [筛选工作流](#筛选工作流)
- [AppIntent 协议](#appintent-协议)
- [`@Parameter`](#parameter)
- [AppEntity](#appentity)
- [EntityQuery (4 种变体)](#entityquery-4-variants)
- [AppEnum](#appenum)
- [AppShortcutsProvider](#appshortcutsprovider)
- [系统界面集成](#系统界面集成)
- [iOS 26 新增功能](#ios-26-新增功能)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 筛选工作流

### 第 1 步：选择操作、边界和界面

从 1-3 个用户希望应用外执行的有价值操作开始，而不是从应用的屏幕层次结构开始。每个操作记录一行设计：用户目标；内联结果或应用目的地；共享域操作；参数和实体查询；确认/身份验证；目标界面和协议。使用一个明确的运行时路由进行应用转接，而不是通过意图分散导航副作用。

然后选择适合该操作的系统功能和协议：

| 界面 | 协议 | 自 iOS 版本 |
|---|---|---|
| Siri / 快捷指令 | `AppIntent` | iOS 16 |
| 可配置小组件 | `WidgetConfigurationIntent` | iOS 17 |
| 控制中心 | `ControlConfigurationIntent` | iOS 18 |
| Spotlight 搜索 | `IndexedEntity` | iOS 18 |
| Apple Intelligence | `@AppIntent(schema:)` | iOS 18 |
| 交互式片段 | `SnippetIntent` | iOS 26 |
| 视觉智能 | `IntentValueQuery` | iOS 26 |

### 第 2 步：定义数据模型

- 优先使用 `AppEntity` 影子模型来暴露应用数据给系统。
- 创建 `AppEnum` 类型用于固定参数选项。
- 选择合适的 `EntityQuery` 变体用于解析。
- 使用 `IndexedEntity` 和 `indexingKey` 元数据标记可搜索实体。

### 第 3 步：实现意图

- 遵循 `AppIntent`（或特定子协议）。
- 声明 `@Parameter` 属性用于所有面向用户的输入。
- 实现 `perform() async throws -> some IntentResult`。
- 添加 `parameterSummary` 用于快捷指令 UI。
- 通过 `AppShortcutsProvider` 注册短语。

### 第 4 步：验证

- 在目标系统界面中构建并运行，以确认发现、参数解析、取消、确认、身份验证、结果渲染和应用转接。
- 如果某个步骤失败，重置测试用例，修复最小的意图/实体/查询边界，并从同一界面重新运行相同的操作，然后再添加其他操作。
- 使用 Xcode 中的意图预览测试 Siri 短语。
- 确认 `IndexedEntity` 实例被索引在命名的 Spotlight 索引中。
- 检查 `WidgetConfigurationIntent` 意图的组态。

## AppIntent 协议

系统通过 `init()` 实例化结构体，设置参数，然后调用 `perform()`。声明 `title` 和 `parameterSummary` 用于快捷指令 UI。

```swift
struct OrderSoupIntent: AppIntent {
    static var title: LocalizedStringResource = "点汤"
    static var description = IntentDescription("点一份汤。")

    @Parameter(title: "汤") var soup: SoupEntity
    @Parameter(title: "数量", default: 1) var quantity: Int

    static var parameterSummary: some ParameterSummary {
        Summary("点 \(\.$soup)") { \.$quantity }
    }

    func perform() async throws -> some IntentResult {
        try await OrderService.shared.place(soup: soup.id, quantity: quantity)
        return .result(dialog: "已点 \(quantity) 份 \(soup.name)。")
    }
}
```

可选成员：`description` (`IntentDescription`)、`openAppWhenRun` (`Bool`)、`isDiscoverable` (`Bool`)、`authenticationPolicy` (`IntentAuthenticationPolicy`)。

## `@Parameter`

使用 `@Parameter` 声明每个面向用户的输入。非可选参数是必需的；系统在需要时请求值。默认值预填充一个有用的值。可选参数不会自动请求，因此当意图无法在没有值的情况下继续时，在 `perform()` 中请求它们。

```swift
// 必需的；系统在需要时请求值
@Parameter(title: "数量")
var count: Int

// 必需的且预填充
@Parameter(title: "数量", default: 1)
var count: Int

// 可选的；如果需要，请自己请求
@Parameter(title: "数量")
var count: Int?
```

### 支持的值类型

基本类型：`Bool`、`Int`、`Double`、`String`、`Duration`、`Date`、`Decimal`、`Measurement` 和 `URL`。集合：支持元素类型的 `Array` 和 `Set`。框架：`IntentPerson`、`IntentFile`。自定义：任何 `AppEntity` 或 `AppEnum`。

### 常见的初始化器模式

```swift
// 基本用法
@Parameter(title: "名称")
var name: String

// 带默认值
@Parameter(title: "数量", default: 5)
var count: Int

// 数值滑块
@Parameter(title: "音量", controlStyle: .slider, inclusiveRange: (0, 100))
var volume: Int

// 选项提供者（动态列表）
@Parameter(title: "类别", optionsProvider: CategoryOptionsProvider())
var category: Category

// 带内容类型的文件
@Parameter(title: "文档", supportedContentTypes: [.pdf, .plainText])
var document: IntentFile

// 带单位的测量值
@Parameter(title: "距离", defaultUnit: .miles, supportsNegativeNumbers: false)
var distance: Measurement<UnitLength>
```

有关所有初始化器变体，请参阅 [参考资料/appintents-advanced.md](references/appintents-advanced.md)。

## AppEntity

优先使用与应用数据镜像的影子模型，并仅暴露系统界面字段。当模型轻量、稳定且适用于 App Intents 生命周期时，允许直接模型遵循。

```swift
struct SoupEntity: AppEntity {
    static let defaultQuery = SoupEntityQuery()
    static var typeDisplayRepresentation: TypeDisplayRepresentation = "汤"
    var id: String

    @Property(title: "名称") var name: String
    @Property(title: "价格") var price: Double

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(name)", subtitle: "$\(String(format: "%.2f", price))")
    }

    init(from soup: Soup) {
        self.id = soup.id; self.name = soup.name; self.price = soup.price
    }
}
```

必需：`id`、`defaultQuery`（静态）、`displayRepresentation`、`typeDisplayRepresentation`（静态）。使用 `@Property(title:)` 标记属性以用于过滤/排序。没有 `@Property` 的属性保持内部。

## EntityQuery (4 种变体)

### 1. EntityQuery (基础 -- 通过 ID 解析)

```swift
struct SoupEntityQuery: EntityQuery {
    func entities(for identifiers: [String]) async throws -> [SoupEntity] {
        SoupStore.shared.soups.filter { identifiers.contains($0.id) }.map { SoupEntity(from: $0) }
    }
    func suggestedEntities() async throws -> [SoupEntity] {
        SoupStore.shared.featured.map { SoupEntity(from: $0) }
    }
}
```

### 2. EntityStringQuery (自由文本搜索)

```swift
struct SoupStringQuery: EntityStringQuery {
    func entities(matching string: String) async throws -> [SoupEntity] {
        SoupStore.shared.search(string).map { SoupEntity(from: $0) }
    }
    func entities(for identifiers: [String]) async throws -> [SoupEntity] {
        SoupStore.shared.soups.filter { identifiers.contains($0.id) }.map { SoupEntity(from: $0) }
    }
}
```

### 3. EnumerableEntityQuery (有限集合)

```swift
struct AllSoupsQuery: EnumerableEntityQuery {
    func allEntities() async throws -> [SoupEntity] {
        SoupStore.shared.allSoups.map { SoupEntity(from: $0) }
    }
    func entities(for identifiers: [String]) async throws -> [SoupEntity] {
        SoupStore.shared.soups.filter { identifiers.contains($0.id) }.map { SoupEntity(from: $0) }
    }
}
```

### 4. UniqueAppEntityQuery (单例，iOS 18+)

用于单例实体，如应用设置。

```swift
struct AppSettingsEntity: UniqueAppEntity {
    static let defaultQuery = AppSettingsQuery()
    static var typeDisplayRepresentation: TypeDisplayRepresentation = "设置"
    var displayRepresentation: DisplayRepresentation { "应用设置" }

    var id: String { "app-settings" }
}

struct AppSettingsQuery: UniqueAppEntityQuery {
    func uniqueEntity() async throws -> AppSettingsEntity {
        AppSettingsEntity()
    }
}
```

有关 `EntityPropertyQuery`（带过滤/排序支持）的信息，请参阅 [参考资料/appintents-advanced.md](references/appintents-advanced.md)。

当一个参数决定另一个参数的有效实体选项时，在查询或选项提供者中使用 `@IntentParameterDependency`。高级参考涵盖了空上游情况和有意默认值。

## AppEnum

定义可选择的固定值集。`RawValue` 必须遵循 `LosslessStringConvertible`；优先使用 `String` 原始值以获得可读、稳定的标识符。

```swift
enum SoupSize: String, AppEnum {
    case small, medium, large

    static var typeDisplayRepresentation: TypeDisplayRepresentation = "大小"

    static var caseDisplayRepresentations: [SoupSize: DisplayRepresentation] = [
        .small: "小",
        .medium: "中",
        .large: "大"
    ]
}
```

```swift
// 有效，但在保存的快捷指令和 URL 表示中不太可读
enum Priority: Int, AppEnum {
    case low = 1, medium = 2, high = 3
}

// 优先
enum Priority: String, AppEnum {
    case low, medium, high
    // ...
}
```

## AppShortcutsProvider

注册预构建的快捷指令，它们无需用户配置即可在 Siri 和快捷指令应用中显示。

```swift
struct MyAppShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: OrderSoupIntent(),
            phrases: [
                "在 \(.applicationName) 中点 \(\.$soup)",
                "从 \(.applicationName) 获取汤"
            ],
            shortTitle: "点汤",
            systemImageName: "cup.and.saucer"
        )
    }

    static var shortcutTileColor: ShortcutTileColor = .navy
}
```

### 短语规则

- 每个短语必须包含 `\(.applicationName)`。
- 短语可以引用参数：`\(\.$soup)`。
- 当动态选项值更改时，调用 `updateAppShortcutParameters()`。
- 使用 `negativePhrases` 来防止 Siri 的错误激活。

## 系统界面集成

在实现 Siri 捐赠/预测、交互式小组件、控制中心配置/操作分离或 Spotlight `IndexedEntity` 索引时，请阅读 [参考资料/system-surfaces.md](references/system-surfaces.md)。

## iOS 26 新增功能

### SnippetIntent

在系统 UI 中显示交互式片段：

```swift
struct OrderStatusSnippet: SnippetIntent {
    static var title: LocalizedStringResource = "订单状态"
    func perform() async throws -> some IntentResult & ShowsSnippetView {
        let status = await OrderTracker.currentStatus()
        return .result(view: OrderStatusSnippetView(status: status))
    }
}

struct CheckOrderStatusIntent: AppIntent {
    static var title: LocalizedStringResource = "检查订单状态"
    func perform() async throws -> some IntentResult & ShowsSnippetIntent {
        .result(snippetIntent: OrderStatusSnippet())
    }
}
```

系统可能会多次调用 `perform()`，包括片段按钮或切换操作后；保持 `SnippetIntent.perform()` 无副作用，并在调用操作意图或单独的按钮/切换操作中进行突变。仅片段的意图除非 `isDiscoverable` 为 `true`，否则不会在快捷指令或 Spotlight 中发现。

### IntentValueQuery (视觉智能)

```swift
@available(iOS 26, *)
@UnionValue
enum ShoppingVisualResult {
    case product(ProductEntity)
    case store(StoreEntity)
}

@available(iOS 26, *)
struct ShoppingVisualQuery: IntentValueQuery {
    func values(for input: SemanticContentDescriptor) async throws -> [ShoppingVisualResult] {
        try Task.checkCancellation()
        async let productMatches = ProductStore.shared.matches(
            labels: input.labels,
            pixelBuffer: input.pixelBuffer,
            limit: 5
        )
        async let storeMatches = StoreStore.shared.matches(
            labels: input.labels,
            pixelBuffer: input.pixelBuffer,
            limit: 3
        )
        let ranked = await rank(productMatches, storeMatches)
        return Array(ranked.prefix(8))
    }
}
```

只能有一个 `IntentValueQuery` 接收 `SemanticContentDescriptor`；当必须返回多个应用实体类型时，使用 `@UnionValue`。将 `labels` 视为高级英语描述符，而不是详尽的同义词或应用分类；当可用时，将它们与 `pixelBuffer` 结合使用。返回小、排序、取消友好的结果，并提供 `OpenIntent`、URL 表示或在应用内搜索转接以获取更多结果。不要在 App Intents 查询中实现相机捕获、Vision `VN*` 请求、条形码分类或 Spotlight 索引；调用现有的有界应用搜索或图像匹配服务，并在可能超出系统 UI 预算时使用显式的结果限制和超时。

## 常见错误

1. **通过 AppEntity 暴露过多应用模型状态。** 优先使用具有稳定持久 ID 和仅系统界面属性的专用影子模型。

2. **短语中缺少 `\(.applicationName)`。** 每个 `AppShortcut` 短语必须包含应用名称标记。Siri 使用它进行消歧。

3. **将可选的 `@Parameter` 视为必需的。** 可选参数不会自动请求；当意图无法在没有值的情况下继续时，调用 `requestValue` / `needsValueError`。

   ```swift
   // 可选的，因此如果需要，请自己请求
   @Parameter(title: "数量")
   var count: Int?
   ```

4. **使用不稳定的 AppEnum 原始值。** `Int` 是有效的，但 `String` 原始值通常更清晰，用于持久化和 URL 表示。

5. **忘记 `suggestedEntities()`。** 没有它，快捷指令选择器将显示无默认值。

6. **在 `entities(for:)` 中抛出缺失实体。** 跳过缺失的实体。

7. **过时的 Spotlight 索引。** 使用命名的 `CSSearchableIndex` 重新索引实体。

8. **缺少 `typeDisplayRepresentation`。** `AppEntity` 和 `AppEnum` 都需要它。

9. **使用已弃用的 `@Assistant*` 模式宏。** 使用 `@AppIntent(schema:)`、`@AppEntity(schema:)` 和 `@AppEnum(schema:)`。

10. **阻塞或副作用的 `perform()`。** 使用 `await` 进行 I/O；保持 `SnippetIntent.perform()` 无副作用，因为系统可能会重新运行它。

11. **未经保护地从系统界面修改敏感状态。** 对于门锁、灯光、购买和删除等操作，使用确认和/或身份验证。

## 审查清单

- [ ] 每个 `AppIntent` 都有描述性的 `title`（动词+名词，首字母大写）
- [ ] 必选的 `@Parameter` 值是非可选的；可选值在需要时才请求
- [ ] `AppEntity` 类型暴露稳定的 ID 和仅系统界面属性
- [ ] `AppEntity` 有 `displayRepresentation` 和 `typeDisplayRepresentation`
- [ ] `EntityQuery.entities(for:)` 跳过缺失的 ID；`suggestedEntities()` 已实现
- [ ] 依赖的选项使用 `@IntentParameterDependency`；`defaultResult()` 仅在存在真正有用的默认值时存在
- [ ] `AppEnum` 优先使用稳定的 `String` 原始值和 `caseDisplayRepresentations`
- [ ] `AppShortcutsProvider` 短语包含 `\(.applicationName)`；`parameterSummary` 已定义
- [ ] `IndexedEntity` 属性使用 key-path `indexingKey` 值，实体已索引
- [ ] 控制中心意图遵循 `ControlConfigurationIntent`；小组件意图遵循 `WidgetConfigurationIntent`；无默认值的控制参数是可选的
- [ ] 敏感的 App Intents 在修改状态之前请求确认和/或身份验证
- [ ] 视觉智能 `IntentValueQuery` 使用 `SemanticContentDescriptor`、有界结果、打开路径和 iOS 26 的可用性
- [ ] 没有 `@AssistantIntent` / `@AssistantEntity` / `@AssistantEnum` 模式宏
- [ ] `perform()` 使用 async/await（无阻塞）；运行在预期的隔离上下文中；意图类型是 `Sendable`

## 参考资料

- 阅读 [参考资料/system-surfaces.md](references/system-surfaces.md) 了解 Siri、小组件、控制中心和 Spotlight 的集成模式。
- 查看 [参考资料/appintents-advanced.md](references/appintents-advanced.md) 了解 `@Parameter` 变体、`EntityPropertyQuery`、助手模式、焦点过滤器、SiriKit 迁移、错误处理、确认流程、身份验证、URL 可表示类型和 Spotlight 索引详细信息。
