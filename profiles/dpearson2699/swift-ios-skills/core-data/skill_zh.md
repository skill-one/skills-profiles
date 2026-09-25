# 核心数据

为未采用 SwiftData 的应用程序使用 Core Data 构建和维护数据持久性。涵盖堆栈设置、并发、批量操作、NSFetchedResultsController、持久历史记录跟踪、分阶段迁移和测试。

## 目录

- [堆栈设置](#堆栈设置)
- [并发和线程](#并发和线程)
- [NSFetchedResultsController](#nsfetchedresultscontroller)
- [批量操作](#批量操作)
- [持久历史记录跟踪](#持久历史记录跟踪)
- [分阶段迁移](#分阶段迁移)
- [组合属性](#组合属性)
- [SwiftData 边界](#swiftdata-boundary)
- [测试](#测试)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 堆栈设置

`NSPersistentContainer` 封装了 Core Data 堆栈。

文档：[NSPersistentContainer](https://sosumi.ai/documentation/coredata/nspersistentcontainer)

```swift
import CoreData

final class CoreDataStack: @unchecked Sendable {
    static let shared = CoreDataStack()

    let container: NSPersistentContainer

    private init() {
        container = NSPersistentContainer(name: "MyAppModel")
        container.loadPersistentStores { _, error in
            if let error { fatalError("Core Data store failed: \(error)") }
        }
        container.viewContext.automaticallyMergesChangesFromParent = true
        container.viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
    }

    var viewContext: NSManagedObjectContext { container.viewContext }

    func newBackgroundContext() -> NSManagedObjectContext {
        container.newBackgroundContext()
    }
}
```

对于 CloudKit 同步，请使用 `NSPersistentCloudKitContainer`。

## 并发和线程

Core Data 上下文绑定到队列。`viewContext` 在主队列上；后台上下文在私有队列上运行。

文档：[NSManagedObjectContext](https://sosumi.ai/documentation/coredata/nsmanagedobjectcontext)

**规则：**
- 访问上下文时，始终使用 `perform(_:)` 或 `performAndWait(_:)`。
- 不要跨上下文或线程边界传递 `NSManagedObject` 实例。传递 `NSManagedObjectID` 并重新获取。
- 将 `automaticallyMergesChangesFromParent = true` 设置在 `viewContext` 上。

```swift
// 在后台上下文中写入
func updateTrip(id: NSManagedObjectID, newName: String) async throws {
    let context = CoreDataStack.shared.newBackgroundContext()
    try await context.perform {
        guard let trip = try context.existingObject(with: id) as? CDTrip else {
            throw PersistenceError.notFound
        }
        trip.name = newName
        try context.save()
    }
}
```

### Swift 并发集成

`NSManagedObjectContext.perform(_:)` 有一个 `async throws` 重载 (iOS 15+)。避免将 `NSManagedObject` 子类标记为 `Sendable`。

```swift
func importItems(_ records: [ItemRecord]) async throws {
    let context = CoreDataStack.shared.newBackgroundContext()
    try await context.perform {
        for record in records {
            let item = CDItem(context: context)
            item.id = record.id
            item.title = record.title
        }
        try context.save()
    }
    // 保存完成后，如果配置了，viewContext 会自动合并
}
```

**不要在托管对象上使用 `@unchecked Sendable`。** 如果需要跨边界通信，传递 `objectID` (它是 `Sendable`) 并重新获取：

```swift
let objectID = trip.objectID  // Sendable
Task.detached {
    let bgContext = CoreDataStack.shared.newBackgroundContext()
    try await bgContext.perform {
        let trip = try bgContext.existingObject(with: objectID) as! CDTrip
        trip.isFavorite = true
        try bgContext.save()
    }
}
```

## NSFetchedResultsController

高效地从 Core Data 查询请求驱动 `UITableView` / `UICollectionView`，具有内置的变化跟踪和可选的缓存。

文档：[NSFetchedResultsController](https://sosumi.ai/documentation/coredata/nsfetchedresultscontroller)

```swift
import CoreData
import UIKit

class TripsViewController: UITableViewController, NSFetchedResultsControllerDelegate {

    private lazy var fetchedResultsController: NSFetchedResultsController<CDTrip> = {
        let request: NSFetchRequest<CDTrip> = CDTrip.fetchRequest()
        request.sortDescriptors = [
            NSSortDescriptor(keyPath: \CDTrip.startDate, ascending: false)
        ]
        request.fetchBatchSize = 20

        let controller = NSFetchedResultsController(
            fetchRequest: request,
            managedObjectContext: CoreDataStack.shared.viewContext,
            sectionNameKeyPath: nil,
            cacheName: "TripsCache"
        )
        controller.delegate = self
        return controller
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        try? fetchedResultsController.performFetch()
    }

    // MARK: - UITableViewDataSource

    override func numberOfSections(in tableView: UITableView) -> Int {
        fetchedResultsController.sections?.count ?? 0
    }

    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        fetchedResultsController.sections?[section].numberOfObjects ?? 0
    }

    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "TripCell", for: indexPath)
        let trip = fetchedResultsController.object(at: indexPath)
        cell.textLabel?.text = trip.name
        return cell
    }

    // MARK: - NSFetchedResultsControllerDelegate (diffable)

    func controller(
        _ controller: NSFetchedResultsController<any NSFetchRequestResult>,
        didChangeContentWith snapshot: NSDiffableDataSourceSnapshotReference
    ) {
        let snapshot = snapshot as NSDiffableDataSourceSnapshot<String, NSManagedObjectID>
        dataSource.apply(snapshot, animatingDifferences: true)
    }
}
```

**要点：**
- 查询请求 **必须** 至少有一个排序描述符。
- 在更改查询请求谓词或排序描述符之前，调用 `deleteCache(withName:)`。
- 可用 iOS 13+ 的 diffable 快照委托方法 (`didChangeContentWith:`)，优先于旧的每次变化回调。
- 上下文 `reset()` 后，再次调用 `performFetch()`。

## 批量操作

批量操作在 SQL 级别执行，绕过托管对象上下文。它们速度快，但不会自动触发上下文通知。

### NSBatchInsertRequest (iOS 13+)

文档：[NSBatchInsertRequest](https://sosumi.ai/documentation/coredata/nsbatchinsertrequest)

```swift
func batchImport(_ records: [[String: Any]]) async throws {
    let context = CoreDataStack.shared.newBackgroundContext()
    try await context.perform {
        let request = NSBatchInsertRequest(
            entity: CDTrip.entity(),
            objects: records
        )
        request.resultType = .objectIDs
        let result = try context.execute(request) as? NSBatchInsertResult
        if let ids = result?.result as? [NSManagedObjectID] {
            NSManagedObjectContext.mergeChanges(
                fromRemoteContextSave: [NSInsertedObjectsKey: ids],
                into: [CoreDataStack.shared.viewContext]
            )
        }
    }
}
```

### NSBatchDeleteRequest (iOS 9+)

文档：[NSBatchDeleteRequest](https://sosumi.ai/documentation/coredata/nsbatchdeleterequest)

```swift
func deleteOldTrips(before cutoff: Date) async throws {
    let context = CoreDataStack.shared.newBackgroundContext()
    try await context.perform {
        let fetchRequest: NSFetchRequest<NSFetchRequestResult> = CDTrip.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "endDate < %@", cutoff as NSDate)
        let request = NSBatchDeleteRequest(fetchRequest: fetchRequest)
        request.resultType = .resultTypeObjectIDs
        let result = try context.execute(request) as? NSBatchDeleteResult
        if let ids = result?.result as? [NSManagedObjectID] {
            NSManagedObjectContext.mergeChanges(
                fromRemoteContextSave: [NSDeletedObjectsKey: ids],
                into: [CoreDataStack.shared.viewContext]
            )
        }
    }
}
```

### NSBatchUpdateRequest (iOS 8+)

```swift
func markAllTripsAsNotFavorite() async throws {
    let context = CoreDataStack.shared.newBackgroundContext()
    try await context.perform {
        let request = NSBatchUpdateRequest(entity: CDTrip.entity())
        request.propertiesToUpdate = ["isFavorite": false]
        request.resultType = .updatedObjectIDsResultType
        let result = try context.execute(request) as? NSBatchUpdateResult
        if let ids = result?.result as? [NSManagedObjectID] {
            NSManagedObjectContext.mergeChanges(
                fromRemoteContextSave: [NSUpdatedObjectsKey: ids],
                into: [CoreDataStack.shared.viewContext]
            )
        }
    }
}
```

**批量操作后，始终将更改合并到相关上下文中。** 批量删除不会强制执行 Deny 删除规则。

对于破坏性或可重试的批量工作，使用证明循环：预检谓词和预期计数，执行具有对象 ID 结果类型，将 ID 合并到活动上下文中，重新获取，并断言后置条件。失败时，在重试之前恢复干净的固定装置或证明操作是幂等的；永远不要盲目重新运行部分完成的批量。

## 持久历史记录跟踪

跨目标（应用程序、扩展、小部件）和进程跟踪存储级更改。核心工作流程是：

文档：[NSPersistentHistoryChangeRequest](https://sosumi.ai/documentation/coredata/nspersistenthistorychangerequest)

1. 在加载存储之前启用持久历史记录和远程更改通知。
2. 在目标持久令牌后观察更改并获取事务。
3. 将事务通知合并到活动上下文中，然后持久化新令牌。
4. 仅清除每个相关消费者已处理的更改历史记录。

实现存储选项、观察者、令牌持久化、合并循环或清除策略时，加载 [persistent-history.md](references/persistent-history.md)。

## 分阶段迁移

`NSStagedMigrationManager` (iOS 17+) 通过有序的轻量级或自定义阶段序列化模式迁移。阶段输入使用编译的模型版本校验和，而不是模型名称。支持低于 iOS 17 系统的应用程序需要轻量级迁移或映射模型路径。

文档：[NSStagedMigrationManager](https://sosumi.ai/documentation/coredata/nsstagedmigrationmanager)

构建有序阶段、模型引用、自定义处理程序和持久存储选项时，加载 [staged-migration.md](references/staged-migration.md)。

## 组合属性

iOS 17+ 支持组合属性：实体上的子属性组，它们作为一个逻辑单元起作用。在模型编辑器中定义它们，通过向其添加复合类型属性并在其下嵌套子属性。

文档：[NSCompositeAttributeDescription](https://sosumi.ai/documentation/coredata/nscompositeattributedescription)

组合属性在 SwiftData 共存场景中映射到 `Codable` 结构体。

## SwiftData 边界

使用 `swiftdata` 技巧实现 Core Data + SwiftData 共存或迁移。在交接之前，保留这些 Core Data 边界：

- SwiftData 必须指向现有的持久存储 URL，当它打算共享或迁移 Core Data 数据时。
- 共享持久化数据必须在 Core Data 模型和 SwiftData `@Model` 类之间保持实体名称、属性名称、类型和模式兼容。
- 映射重命名的持久化属性，使用 SwiftData `@Attribute(originalName:)`。

## 测试

### 内存存储用于测试

```swift
import CoreData
import Testing

struct CoreDataTests {
    func makeTestContainer() throws -> NSPersistentContainer {
        let container = NSPersistentContainer(name: "MyAppModel")
        let description = NSPersistentStoreDescription()
        description.type = NSInMemoryStoreType
        container.persistentStoreDescriptions = [description]

        var loadError: Error?
        container.loadPersistentStores { _, error in loadError = error }
        if let loadError { throw loadError }
        return container
    }

    @Test func createAndFetchTrip() throws {
        let container = try makeTestContainer()
        let context = container.viewContext

        let trip = CDTrip(context: context)
        trip.name = "Test Trip"
        trip.startDate = .now
        try context.save()

        let request: NSFetchRequest<CDTrip> = CDTrip.fetchRequest()
        let trips = try context.fetch(request)
        #expect(trips.count == 1)
        #expect(trips.first?.name == "Test Trip")
    }
}
```

**技巧：**
- 跨测试共享 `NSManagedObjectModel` 实例，以避免“重复实体”警告。
- 使用单个共享模型一次加载：

```swift
private let sharedModel: NSManagedObjectModel = {
    let url = Bundle.main.url(forResource: "MyAppModel", withExtension: "momd")!
    return NSManagedObjectModel(contentsOf: url)!
}()

func makeTestContainer() throws -> NSPersistentContainer {
    let container = NSPersistentContainer(name: "MyAppModel",
                                          managedObjectModel: sharedModel)
    // ... 配置内存存储
}
```

## 常见错误

| 错误 | 修复 |
|------|------|
| 跨线程传递 `NSManagedObject` | 传递 `objectID` 并在目标上下文中重新获取 |
| 忘记合并批量操作结果 | 调用 `mergeChanges(fromRemoteContextSave:into:)` |
| 未检查 `hasChanges` 就调用 `save()` | 首先使用 `context.hasChanges` 进行保护 |
| 使用已弃用的 `init(concurrencyType:)` 限制类型 | 使用 `.privateQueueConcurrencyType` 或 `.mainQueueConcurrencyType` |
| 未在 `viewContext` 上设置 `mergePolicy` | 设置 `NSMergeByPropertyObjectTrumpMergePolicy` 以避免冲突崩溃 |
| 在没有删除缓存的情况下，在活动的 `NSFetchedResultsController` 上修改查询请求 | 首先调用 `deleteCache(withName:)` 或使用 `cacheName: nil` |
| 批量删除忽略 Deny 删除规则 | 批量删除绕过删除规则；手动验证 |
| 将 `NSManagedObject` 标记为 `@unchecked Sendable` | 不要这样做。传递 `objectID` 而不是 |
| 在共存期间将 SwiftData 指向一个全新的存储 | 当 SwiftData 应该共享或迁移 Core Data 数据时，使用现有的存储 URL 和兼容的模式 |

## 审查清单

- [ ] `NSPersistentContainer` 一次性初始化并共享
- [ ] `viewContext` 仅在主队列上使用；后台上下文用于写入
- [ ] 所有离队列上下文访问都使用 `perform(_:)` 或 `performAndWait(_:)` 包装
- [ ] `automaticallyMergesChangesFromParent` 在 `viewContext` 上设置
- [ ] `mergePolicy` 在 `viewContext` 上设置以防止冲突崩溃
- [ ] 批量操作结果合并到相关上下文
- [ ] `NSFetchedResultsController` 查询请求具有排序描述符
- [ ] 多目标应用程序启用了持久历史记录跟踪
- [ ] Core Data + SwiftData 交接保留了存储 URL、模式兼容性、实体/属性名称和重命名映射
- [ ] 测试使用内存存储和共享 `NSManagedObjectModel`
- [ ] 没有 `NSManagedObject` 实例跨线程边界传递

## 参考资料

- [跨目标和进程的持久历史记录](references/persistent-history.md)
- [分阶段轻量级和自定义迁移](references/staged-migration.md)
- Apple 文档：[Core Data](https://sosumi.ai/documentation/coredata) | [NSPersistentContainer](https://sosumi.ai/documentation/coredata/nspersistentcontainer) | [NSFetchedResultsController](https://sosumi.ai/documentation/coredata/nsfetchedresultscontroller) | [NSStagedMigrationManager](https://sosumi.ai/documentation/coredata/nsstagedmigrationmanager)
