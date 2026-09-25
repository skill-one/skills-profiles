# SwiftData

使用 Swift 6.3 在 iOS 26+ 应用中持久化、查询和管理结构化数据。

## 目录

- [模型定义](#模型定义)
- [ModelContainer 设置](#modelcontainer-设置)
- [CloudKit 同步](#cloudkit-同步)
- [CRUD 操作](#crud-操作)
- [`@Query` in SwiftUI](#query-in-swiftui)
- [#Predicate](#predicate)
- [FetchDescriptor](#fetchdescriptor)
- [模式版本控制和迁移](#模式版本控制和迁移)
- [Core Data 共存边界](#core-data-coexistence-boundary)
- [并发 (`@ModelActor`)](#并发-modelactor)
- [SwiftUI 集成](#swiftui-integration)
- [常见错误](#常见错误)
- [审查清单](#review-checklist)
- [参考资料](#参考资料)

## 模型定义

将 `@Model` 应用于**类**（而不是结构体）。它会合成 `PersistentModel` 协议。模型实例保持上下文/Actor 绑定；跨 Actor 传递它们的 `PersistentIdentifier`，而不是实例。

```swift
@Model
class Trip {
    var name: String
    var destination: String
    var startDate: Date
    var endDate: Date
    var isFavorite: Bool = false
    @Attribute(.externalStorage) var imageData: Data?
    @Relationship(deleteRule: .cascade, inverse: \LivingAccommodation.trip)
    var accommodation: LivingAccommodation?
    @Transient var isSelected: Bool = false  // 始终提供默认值

    init(name: String, destination: String, startDate: Date, endDate: Date) {
        self.name = name; self.destination = destination
        self.startDate = startDate; self.endDate = endDate
    }
}
```

**`@Attribute` 选项**: `.externalStorage`, `.unique`, `.spotlight`, `.allowsCloudEncryption`, `.preserveValueOnDeletion`, `.ephemeral`, `.transformable(by:)`。重命名: `@Attribute(originalName: "old_name")`。

**`@Relationship`**: `deleteRule:` `.cascade`/`.nullify`(默认)/`.deny`/`.noAction`。指定 `inverse:` 以确保可靠行为。单向（iOS 18+）: `inverse: nil`。

**#Unique (iOS 18+)**: `#Unique<Person>([\.firstName, \.lastName])` -- 复合唯一性。

**继承 (iOS 26+)**: `@Model class BusinessTrip: Trip { var company: String }`。

支持的类型: `Bool`, `Int`/`UInt` 变体, `Float`, `Double`, `String`, `Date`, `Data`, `URL`, `UUID`, `Decimal`, `Array`, `Dictionary`, `Set`, `Codable` 枚举, `Codable` 结构体和其他兼容的 `Codable` 值类型，以及指向 `@Model` 类型的关系。

## ModelContainer 设置

```swift
// 基本用法
let container = try ModelContainer(for: Trip.self, LivingAccommodation.self)

// 配置用法
let config = ModelConfiguration("Store", isStoredInMemoryOnly: false,
    groupContainer: .identifier("group.com.example.app"),
    cloudKitDatabase: .private("iCloud.com.example.app"))
let container = try ModelContainer(for: Trip.self, configurations: config)

// 带迁移计划
let container = try ModelContainer(for: SchemaV2.Trip.self,
    migrationPlan: TripMigrationPlan.self)

// 内存中（预览/测试）
let container = try ModelContainer(for: Trip.self,
    configurations: ModelConfiguration(isStoredInMemoryOnly: true))
```

## CloudKit 同步

`ModelConfiguration(..., cloudKitDatabase:)` 将 SwiftData 存储选项配置为自动 CloudKit 同步，但应用权限仍然控制同步。

对于任何 SwiftData CloudKit 设置或模式审查任务，在模式发现之前包含一个单独的**功能**评审：

- **功能**: Xcode 目标具有 iCloud 功能，CloudKit 已启用，并选择了预期容器，加上远程通知 > 远程通知。如果没有这些权限，即使设置了 `cloudKitDatabase`，自动同步也不会完全配置。
- **模式兼容性**: 没有 `@Attribute(.unique)` 或 `#Unique`；关系是可选的，在需要时具有明确的逆关系，并避免 `.deny`；大型 `Data` 使用 `@Attribute(.externalStorage)`。
- **标量属性**: 不要为了 CloudKit 而使每个标量可选。当初始值、默认值或迁移提供有效值时，保持必需的标量非可选。
- **模式发布**: 仅在非生产构建中初始化开发模式，在 CloudKit 控制台中验证它，在发布前提升，并将生产更改视为仅增量更改。

## CRUD 操作

对于破坏性批处理和迁移，首先在可丢弃的副本上运行确切的谓词或版本跳转，并记录受影响的标识符/计数。使用显式事务/保存语义执行，重新获取，并验证值、关系、计数和不变量。失败时，修复谓词/模式并恢复纯净的固定装置再重试；切勿盲目重放破坏性操作。

```swift
// 创建
let trip = Trip(name: "Summer", destination: "Paris", startDate: .now, endDate: .now + 86400*7)
modelContext.insert(trip)
try modelContext.save()  // 或依赖自动保存

// 读取
let trips = try modelContext.fetch(FetchDescriptor<Trip>(
    predicate: #Predicate { $0.destination == "Paris" },
    sortBy: [SortDescriptor(\.startDate)]))

// 更新 -- 直接修改属性；自动保存处理持久化
trip.destination = "Rome"

// 删除
modelContext.delete(trip)
try modelContext.delete(model: Trip.self, where: #Predicate { $0.isFavorite == false })

// 事务（原子）
try modelContext.transaction {
    modelContext.insert(trip); trip.isFavorite = true
}
```

## `@Query` in SwiftUI

```swift
struct TripListView: View {
    @Query(filter: #Predicate<Trip> { $0.isFavorite == true },
           sort: \.startDate, order: .reverse)
    private var favorites: [Trip]

    var body: some View { List(favorites) { trip in Text(trip.name) } }
}

// 动态查询通过初始化
struct SearchView: View {
    @Query private var trips: [Trip]
    init(search: String) {
        _trips = Query(filter: #Predicate<Trip> { trip in
            search.isEmpty || trip.name.localizedStandardContains(search)
        }, sort: [SortDescriptor(\.name)])
    }
    var body: some View { List(trips) { trip in Text(trip.name) } }
}

// FetchDescriptor 查询
struct RecentView: View {
    static var desc: FetchDescriptor<Trip> {
        var d = FetchDescriptor<Trip>(sortBy: [SortDescriptor(\.startDate)])
        d.fetchLimit = 5; return d
    }
    @Query(RecentView.desc) private var recent: [Trip]
    var body: some View { List(recent) { trip in Text(trip.name) } }
}
```

## #Predicate

```swift
#Predicate<Trip> { $0.destination.localizedStandardContains("paris") }  // String
let now = Date()
#Predicate<Trip> { $0.startDate > now }                                 // Date
#Predicate<Trip> { $0.isFavorite && $0.destination != "Unknown" }       // 复合
#Predicate<Trip> { $0.accommodation?.name != nil }                      // 可选
#Predicate<Trip> { $0.tags.contains { $0.name == "adventure" } }        // 集合
```

支持: `==`, `!=`, `<`, `<=`, `>`, `>=`, `&&`, `||`, `!`, `contains()`, `allSatisfy()`, `filter()`, `starts(with:)`, `localizedStandardContains()`, `caseInsensitiveCompare()`, 算术, 条件表达式, 可选链和绑定, 空值合并, 类型转换。**避免**: 循环, 嵌套声明, 修改, 和任意不支持的调用方法。

## FetchDescriptor

```swift
var d = FetchDescriptor<Trip>(predicate: ..., sortBy: [...])
d.fetchLimit = 20; d.fetchOffset = 0
d.includePendingChanges = true
d.propertiesToFetch = [\.name, \.startDate]
d.relationshipKeyPathsForPrefetching = [\.accommodation]
let trips = try modelContext.fetch(d)
let count = try modelContext.fetchCount(d)
let ids = try modelContext.fetchIdentifiers(d)
try modelContext.enumerate(d, batchSize: 1000) { trip in trip.isProcessed = true }
```

## 模式版本控制和迁移

```swift
enum SchemaV1: VersionedSchema {
    static var versionIdentifier = Schema.Version(1, 0, 0)
    static var models: [any PersistentModel.Type] { [Trip.self] }
    @Model class Trip { var name: String; init(name: String) { self.name = name } }
}

enum SchemaV2: VersionedSchema {
    static var versionIdentifier = Schema.Version(2, 0, 0)
    static var models: [any PersistentModel.Type] { [Trip.self] }
    @Model class Trip {
        var name: String; var startDate: Date?  // 新属性
        init(name: String) { self.name = name }
    }
}

enum TripMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] { [SchemaV1.self, SchemaV2.self] }
    static var stages: [MigrationStage] { [migrateV1toV2] }
    static let migrateV1toV2 = MigrationStage.lightweight(
        fromVersion: SchemaV1.self, toVersion: SchemaV2.self)
}

// 自定义迁移用于数据转换
static let migrateV2toV3 = MigrationStage.custom(
    fromVersion: SchemaV2.self, toVersion: SchemaV3.self,
    willMigrate: nil,
    didMigrate: { context in
        let trips = try context.fetch(FetchDescriptor<SchemaV3.Trip>())
        for trip in trips { trip.displayName = trip.name.capitalized }
        try context.save()
    })
```

轻量级处理: 添加可选/默认属性, 重命名 (`originalName`), 删除属性, 添加模型类型。
验证阶段列表涵盖所有支持的版本跳转，然后迁移每个旧存储的新副本，并在发布前断言迁移后的数据。

## Core Data 共存边界

在需要将 SwiftData 与现有 Core Data 存储一起运行或随时间将 Core Data 屏幕迁移到 SwiftData 时使用此技巧。保持纯 Core Data 堆栈设置, `NSManagedObjectContext`, `NSFetchRequest`, 和批量 Core Data 操作在兄弟 `core-data` 技巧中。

对于共存，在详细的迁移建议之前提供边界指导：

- 将 SwiftData 和 Core Data 指向相同的 SQLite 存储URL。
- 在 SwiftData `@Model` 定义中匹配 Core Data 实体名称、属性名称、类型和关系形状。
- 使用 `@Attribute(originalName:)` 对于 SwiftData 属性，其持久化的 Core Data 名称与 Swift 名称不同。
- 不要同时从两个堆栈写入相同的实体；在迁移期间为每个实体分配一个堆栈作为写入者。

## 并发 (`@ModelActor`)

```swift
@ModelActor
actor DataHandler {
    func importTrips(_ records: [TripRecord]) throws {
        for r in records {
            modelContext.insert(Trip(name: r.name, destination: r.dest,
                                    startDate: r.start, endDate: r.end))
        }
        try modelContext.save()  // 在 @ModelActor 中始终显式保存
    }

    func process(tripID: PersistentIdentifier) throws {
        guard let trip = self[tripID, as: Trip.self] else { return }
        trip.isProcessed = true; try modelContext.save()
    }
}

let handler = DataHandler(modelContainer: container)
try await handler.importTrips(records)
```

**规则**: `ModelContainer` 是 `Sendable`。`ModelContext` 不是 -- 在其创建的 Actor 上使用。跨边界传递 `PersistentIdentifier` (Sendable)。切勿跨 Actor 传递 `@Model` 对象。

## SwiftUI 集成

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup { ContentView() }
            .modelContainer(for: [Trip.self, LivingAccommodation.self])
    }
}

struct DetailView: View {
    @Environment(\.modelContext) private var modelContext
    let trip: Trip
    var body: some View {
        Text(trip.name)
        Button("Delete") { modelContext.delete(trip) }
    }
}

#Preview {
    let config = ModelConfiguration(isStoredInMemoryOnly: true)
    let container = try! ModelContainer(for: Trip.self, configurations: config)
    container.mainContext.insert(Trip(name: "Preview", destination: "London",
        startDate: .now, endDate: .now + 86400))
    return TripListView().modelContainer(container)
}
```

## 常见错误

**1. `@Model` 在结构体上** -- 使用类。`@Model` 需要引用语义。

**2. `@Transient` 而没有默认值** -- 始终提供默认值: `@Transient var x: Bool = false`。

**3. 缺少 .modelContainer** -- 没有 container 在视图层次结构中，`@Query` 返回空。

**4. 跨 Actor 传递模型对象**:
```swift
// 错误: await handler.process(trip: trip)
// 正确: await handler.process(tripID: trip.persistentModelID)
```

**5. ModelContext 在错误的 Actor 上**:
```swift
// 错误: Task.detached { context.fetch(...) }
// 正确: 使用 @ModelActor 进行后台工作
```

**6. 不支持的 #Predicate 表达式**:
```swift
// 错误: #Predicate<Trip> { $0.name.uppercased() == "PARIS" }
// 正确: #Predicate<Trip> { $0.name.localizedStandardContains("paris") }
```

**7. #Predicate 中的流程控制**:
```swift
// 错误: #Predicate<Trip> { for tag in $0.tags { ... } }
// 正确: #Predicate<Trip> { $0.tags.contains { $0.name == "x" } }
```

**8. `@ModelActor` 中没有保存** -- 始终显式调用 `try modelContext.save()`。

**9. ObservableObject 与 `@Model`** -- 从不使用 `ObservableObject`/`@Published`。`@Model` 生成 `Observable`。在视图中使用 `@Query`。

**10. 无默认值的非可选关系**:
```swift
// 错误: var accommodation: LivingAccommodation  // reconstitution 时崩溃
// 正确: var accommodation: LivingAccommodation?
```

**11. 无逆关系的级联** -- 指定 `inverse:` 以确保级联删除的可靠行为。

**12. DispatchQueue 用于后台数据工作**:
```swift
// 错误: DispatchQueue.global().async { ModelContext(container).fetch(...) }
// 正确: @ModelActor actor Handler { func fetch() throws { ... } }
```

## 审查清单

- [ ] 每个 `@Model` 是一个具有指定初始值的类
- [ ] 所有 `@Transient` 属性都有默认值
- [ ] 关系指定 `deleteRule` 和 `inverse`
- [ ] `.modelContainer` 在场景/根视图级别附加
- [ ] `@Query` 用于 SwiftUI 中的反应式数据显示
- [ ] `#Predicate` 仅使用支持的运算符
- [ ] 后台工作使用 `@ModelActor`
- [ ] 跨 Actor 边界使用 `PersistentIdentifier`
- [ ] 模式更改具有 `VersionedSchema` + `SchemaMigrationPlan`
- [ ] 大型数据使用 `@Attribute(.externalStorage)`
- [ ] CloudKit 模型避免唯一性，使用可选关系，避免 `.deny`，并且不要全面使标量可选
- [ ] CloudKit 同步具有 iCloud + CloudKit，远程通知，以及生产模式发布检查
- [ ] `@ModelActor` 方法中显式 `save()`
- [ ] 预览使用 `ModelConfiguration(isStoredInMemoryOnly: true)`
- [ ] 从 SwiftUI 视图访问的 `@Model` 类在 `@MainActor` 上通过 `@ModelActor` 或 MainActor 隔离

## 参考资料

- [references/swiftdata-advanced.md](references/swiftdata-advanced.md) — 自定义数据存储，历史跟踪，CloudKit，复合属性，模型继承，撤销/重做，性能
- [references/swiftdata-queries.md](references/swiftdata-queries.md) — `@Query` 变体，FetchDescriptor 深入，分节查询，动态查询，后台获取
- [references/core-data-coexistence.md](references/core-data-coexistence.md) — Core Data + SwiftData 共存和迁移边界
- [references/predicate-pitfalls.md](references/predicate-pitfalls.md) — #Predicate 运行时崩溃，不支持的表达式，安全模式
- [references/indexing.md](references/indexing.md) — #Index 宏，复合索引，何时索引，迁移
