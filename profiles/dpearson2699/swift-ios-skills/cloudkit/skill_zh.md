# CloudKit

使用 CloudKit、iCloud key-value 存储 和 iCloud Drive 在设备之间同步数据。涵盖容器设置、记录 CRUD、查询、订阅、CKSyncEngine、SwiftData 集成、冲突解决和错误处理。

## 目录

- [容器和数据库设置](#容器和数据库设置)
- [工作流](#工作流)
- [CKRecord CRUD](#ckrecord-crud)
- [CKQuery](#ckquery)
- [CKSubscription](#cksubscription)
- [CKSyncEngine (iOS 17+)](#cksyncengine-ios-17)
- [SwiftData + CloudKit](#swiftdata--cloudkit)
- [NSUbiquitousKeyValueStore](#nsubiquitouskeyvaluestore)
- [iCloud Drive 文件同步](#icloud-drive-file-sync)
- [账户状态和错误处理](#账户状态和错误处理)
- [冲突解决](#冲突解决)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 工作流

1. 选择数据库范围和同步所有者；在写入记录之前，验证能力、容器、账户状态、模式和环境。
2. 使本地更改持久化，入队它，然后让订阅或 `CKSyncEngine` 驱动远程工作，而不是轮询。
3. 在成功应用后，持久化更改标记或同步引擎状态。
4. 测试离线编辑、部分失败、速率限制、标记过期、冲突、账户丢失、区域删除和重新启动。
5. 在失败时，分类 `CKError`，恢复受影响的 fixture 或队列项，应用文档中记录的重试/重置/合并操作，并重新运行相同的场景。在部分成功后，切勿盲目重新启动完整同步。

加载 [参考资料/cloudkit-patterns.md](参考资料/cloudkit-patterns.md) 以获取增量区域更改、共享、资产、批量操作和仪表板程序。

## 容器和数据库设置

在“签名与能力”中启用 iCloud + CloudKit。容器提供三个数据库：

| 数据库   | 范围   | 需要 iCloud | 存储配额   |
|----------|-------|------------|------------|
| 公开     | 所有用户 | 读取：否，写入：是 | 应用配额   |
| 私有     | 当前用户 | 是         | 用户配额   |
| 共享     | 共享记录 | 是         | 所有者配额 |

```swift
import CloudKit

let container = CKContainer.default()
// 或命名：CKContainer(identifier: "iCloud.com.example.app")

let publicDB  = container.publicCloudDatabase
let privateDB = container.privateCloudDatabase
let sharedDB  = container.sharedCloudDatabase
```

## CKRecord CRUD

记录是键值对。每条记录最大 1 MB（不包括 CKAsset 数据）。

```swift
// 创建
let record = CKRecord(recordType: "Note")
record["title"] = "Meeting Notes" as CKRecordValue
record["body"] = "Discussed Q3 roadmap" as CKRecordValue
record["createdAt"] = Date() as CKRecordValue
record["tags"] = ["work", "planning"] as CKRecordValue
let saved = try await privateDB.save(record)

// 通过 ID 获取
let recordID = CKRecord.ID(recordName: "unique-id-123")
let fetched = try await privateDB.record(for: recordID)

// 更新 -- 先获取，修改，然后保存
fetched["title"] = "Updated Title" as CKRecordValue
let updated = try await privateDB.save(fetched)

// 删除
try await privateDB.deleteRecord(withID: recordID)
```

### 自定义记录区域

应用程序在私有数据库中创建自定义区域。共享数据库公开其他用户与当前用户共享的区域。自定义区域支持原子提交、更改跟踪和共享；公共数据库不支持自定义区域。

```swift
let zoneID = CKRecordZone.ID(zoneName: "NotesZone")
let zone = CKRecordZone(zoneID: zoneID)
try await privateDB.save(zone)

let recordID = CKRecord.ID(recordName: UUID().uuidString, zoneID: zoneID)
let record = CKRecord(recordType: "Note", recordID: recordID)
```

## CKQuery

使用 NSPredicate 查询记录。支持：`==`，`!=`，`<`，`>`，`<=`，`>=`，`BEGINSWITH`，`CONTAINS`，`IN`，`AND`，`NOT`，`BETWEEN`，`distanceToLocation:fromLocation:`。

`CONTAINS` 测试列表成员，不包括使用 `self CONTAINS` 的标记化全文搜索。`BEGINSWITH` 是字符串前缀运算符；不支持运算符、键路径或字段类型在查询执行时失败。
对于每次加密审查，明确指出字段资格：加密值不能被查询或排序；`CKAsset` 默认加密；`CKRecord.Reference` 不能加密，因为 CloudKit 在服务器端需要它。

```swift
let predicate = NSPredicate(format: "title BEGINSWITH %@", "Meeting")
let query = CKQuery(recordType: "Note", predicate: predicate)
query.sortDescriptors = [NSSortDescriptor(key: "createdAt", ascending: false)]

let (results, _) = try await privateDB.records(matching: query)
for (_, result) in results {
    let record = try result.get()
    print(record["title"] as? String ?? "")
}

// 获取所有类型记录
let allQuery = CKQuery(recordType: "Note", predicate: NSPredicate(value: true))

// 全文搜索跨字符串字段
let searchQuery = CKQuery(
    recordType: "Note",
    predicate: NSPredicate(format: "self CONTAINS %@", "roadmap")
)

// 复合谓词
let compound = NSCompoundPredicate(andPredicateWithSubpredicates: [
    NSPredicate(format: "createdAt > %@", cutoffDate as NSDate),
    NSPredicate(format: "tags CONTAINS %@", "work")
])
```

## CKSubscription

订阅在记录服务器端更改时触发推送通知。当 CloudKit 启用时，CloudKit/Xcode 处理 APNs 授权；无需单独显式的 App ID 推送设置。静默/后台处理仍然需要后台模式 > 远程通知。

```swift
// 查询订阅 -- 匹配记录更改时触发
let subscription = CKQuerySubscription(
    recordType: "Note",
    predicate: NSPredicate(format: "tags CONTAINS %@", "urgent"),
    subscriptionID: "urgent-notes",
    options: [.firesOnRecordCreation, .firesOnRecordUpdate]
)
let notifInfo = CKSubscription.NotificationInfo()
notifInfo.shouldSendContentAvailable = true  // 静默推送
subscription.notificationInfo = notifInfo
try await privateDB.save(subscription)

// 数据库订阅 -- 任何数据库更改时触发
let dbSub = CKDatabaseSubscription(subscriptionID: "private-db-changes")
dbSub.notificationInfo = notifInfo
try await privateDB.save(dbSub)

// 记录区域订阅 -- 在区域内更改时触发
let zoneSub = CKRecordZoneSubscription(
    zoneID: CKRecordZone.ID(zoneName: "NotesZone"),
    subscriptionID: "notes-zone-changes"
)
zoneSub.notificationInfo = notifInfo
try await privateDB.save(zoneSub)
```

在 AppDelegate 中处理：

```swift
func application(
    _ application: UIApplication,
    didReceiveRemoteNotification userInfo: [AnyHashable: Any]
) async -> UIBackgroundFetchResult {
    let notification = CKNotification(fromRemoteNotificationDictionary: userInfo)
    guard notification?.subscriptionID == "private-db-changes" else { return .noData }
    // 使用 CKSyncEngine 或 CKFetchRecordZoneChangesOperation 获取更改
    return .newData
}
```

## CKSyncEngine (iOS 17+)

`CKSyncEngine` 是自定义模型数据同步的推荐方法。它处理计划、临时重试、更改标记和数据库订阅，但不处理特定于应用程序的保存失败：`CKError.serverRecordChanged` 从 `sentRecordZoneChanges.failedRecordSaves` 仍然需要自定义冲突解决和重新计划。自动同步时间不确定。需要 CloudKit 能力 + 远程通知；仅私有/共享数据库。

```swift
import CloudKit

final class SyncManager: CKSyncEngineDelegate {
    let syncEngine: CKSyncEngine

    init(container: CKContainer = .default()) {
        let config = CKSyncEngine.Configuration(
            database: container.privateCloudDatabase,
            stateSerialization: Self.loadState(),
            delegate: self
        )
        self.syncEngine = CKSyncEngine(config)
    }

    func handleEvent(_ event: CKSyncEngine.Event, syncEngine: CKSyncEngine) async {
        switch event {
        case .stateUpdate(let update):
            Self.saveState(update.stateSerialization)
        case .accountChange(let change):
            handleAccountChange(change)
        case .fetchedRecordZoneChanges(let changes):
            for mod in changes.modifications { processRemoteRecord(mod.record) }
            for del in changes.deletions { processRemoteDeletion(del.recordID) }
        case .sentRecordZoneChanges(let sent):
            for saved in sent.savedRecords { markSynced(saved) }
            for fail in sent.failedRecordSaves { handleSaveFailure(fail) }
        default: break
        }
    }

    func nextRecordZoneChangeBatch(
        _ context: CKSyncEngine.SendChangesContext,
        syncEngine: CKSyncEngine
    ) async -> CKSyncEngine.RecordZoneChangeBatch? {
        let pending = syncEngine.state.pendingRecordZoneChanges
            .filter { context.options.zoneIDs.contains($0) }
        return await CKSyncEngine.RecordZoneChangeBatch(
            pendingChanges: pending
        ) { recordID in self.recordToSend(for: recordID) }
    }
}

// 安排更改
let zoneID = CKRecordZone.ID(zoneName: "NotesZone")
let recordID = CKRecord.ID(recordName: noteID, zoneID: zoneID)
syncEngine.state.add(pendingRecordZoneChanges: [.saveRecord(recordID)])

// 触发立即同步（下拉刷新）
try await syncEngine.fetchChanges()
try await syncEngine.sendChanges()
```

**要点**：跨启动持久化 `stateSerialization`；引擎需要它才能从正确的更改标记恢复。

## SwiftData + CloudKit

`ModelConfiguration` 支持CloudKit同步。在 SwiftData CloudKit 实现或审查的每个地方，始终报告两个裁决：

- **模型兼容性**：没有 `#Unique` 或唯一约束，可选关系，没有 `.deny`，以及外部存储用于大型 `Data`。
- **模式发布**：在非生产构建中初始化开发模式，在 CloudKit 仪表板中验证它，在发布前提升它，在生产提升后仅添加模式；不要删除模型类型或更改现有属性。

```swift
import SwiftData

@Model
class Note {
    var title: String
    var body: String?
    var createdAt: Date?
    @Attribute(.externalStorage) var imageData: Data?

    init(title: String, body: String? = nil) {
        self.title = title
        self.body = body
        self.createdAt = Date()
    }
}

let config = ModelConfiguration(
    "Notes",
    cloudKitDatabase: .private("iCloud.com.example.app")
)
let container = try ModelContainer(for: Note.self, configurations: config)
```

## NSUbiquitousKeyValueStore

简单的键值同步。最多 1024 个键，1 MB 总计，每个值 1 MB。当 iCloud 不可用时存储在本地。

```swift
let kvStore = NSUbiquitousKeyValueStore.default

// 写入
kvStore.set("dark", forKey: "theme")
kvStore.set(14.0, forKey: "fontSize")
kvStore.set(true, forKey: "notificationsEnabled")
kvStore.synchronize()

// 读取
let theme = kvStore.string(forKey: "theme") ?? "system"

// 观察 外部更改
NotificationCenter.default.addObserver(
    forName: NSUbiquitousKeyValueStore.didChangeExternallyNotification,
    object: kvStore, queue: .main
) { notification in
    guard let userInfo = notification.userInfo,
          let reason = userInfo[NSUbiquitousKeyValueStoreChangeReasonKey] as? Int,
          let keys = userInfo[NSUbiquitousKeyValueStoreChangedKeysKey] as? [String]
    else { return }

    switch reason {
    case NSUbiquitousKeyValueStoreServerChange:
        for key in keys { applyRemoteChange(key: key) }
    case NSUbiquitousKeyValueStoreInitialSyncChange:
        reloadAllSettings()
    case NSUbiquitousKeyValueStoreQuotaViolationChange:
        handleQuotaExceeded()
    default: break
    }
}
```

## iCloud Drive 文件同步

使用 `FileManager` ubiquity API 进行文档级同步。在主线程之外调用 `url(forUbiquityContainerIdentifier:)` 和 `setUbiquitous`；`setUbiquitous` 执行协调文件工作并可能阻塞。如果应用程序正在显示文件，则在移动它之前配置一个活动文件呈现器。

```swift
Task.detached {
    guard let ubiquityURL = FileManager.default.url(
        forUbiquityContainerIdentifier: "iCloud.com.example.app"
    ) else { return }  // iCloud 不可用

    let docsURL = ubiquityURL.appendingPathComponent("Documents")
    try FileManager.default.createDirectory(at: docsURL, withIntermediateDirectories: true)
    let cloudURL = docsURL.appendingPathComponent("report.pdf")
    try FileManager.default.setUbiquitous(true, itemAt: localURL, destinationURL: cloudURL)
}
```

使用 `NSMetadataQuery` 监控文件，范围设置为
`NSMetadataQueryUbiquitousDocumentsScope` 或
`NSMetadataQueryUbiquitousDataScope`。

## 账户状态和错误处理

始终在同步前检查账户状态。监听 `.CKAccountChanged`。

```swift
func checkiCloudStatus() async throws -> CKAccountStatus {
    let status = try await CKContainer.default().accountStatus()
    switch status {
    case .available: return status
    case .noAccount: throw SyncError.noiCloudAccount
    case .restricted: throw SyncError.restricted
    case .temporarilyUnavailable: throw SyncError.temporarilyUnavailable
    case .couldNotDetermine: throw SyncError.unknown
    @unknown default: throw SyncError.unknown
    }
}
```

### CKError 处理

| 错误代码       | 策略   |
|---------------|--------|
| `.networkFailure`, `.networkUnavailable` | 网络恢复时排队重试 |
| `.serverRecordChanged` | 三向合并（见冲突解决） |
| `.requestRateLimited`, `.zoneBusy`, `.serviceUnavailable` | 在 `retryAfterSeconds` 后重试 |
| `.quotaExceeded` | 通知用户；减少数据使用 |
| `.notAuthenticated` | 提示 iCloud 登录 |
| `.partialFailure` | 每个项目检查 `partialErrorsByItemID` |
| `.changeTokenExpired` | 重置标记，重新获取所有更改 |
| `.userDeletedZone` | 重新创建区域并重新上传数据 |

```swift
func handleCloudKitError(_ error: Error) {
    guard let ckError = error as? CKError else { return }
    switch ckError.code {
    case .networkFailure, .networkUnavailable:
        scheduleRetryWhenOnline()
    case .serverRecordChanged:
        resolveConflict(ckError)
    case .requestRateLimited, .zoneBusy, .serviceUnavailable:
        let delay = ckError.retryAfterSeconds ?? 3.0
        scheduleRetry(after: delay)
    case .quotaExceeded:
        notifyUserStorageFull()
    case .partialFailure:
        if let partial = ckError.partialErrorsByItemID {
            for (_, itemError) in partial { handleCloudKitError(itemError) }
        }
    case .changeTokenExpired:
        resetChangeToken()
    case .userDeletedZone:
        recreateZoneAndResync()
    default: logError(ckError)
    }
}
```

## 冲突解决

当保存已在服务器端更改的记录时，CloudKit 返回 `.serverRecordChanged` 并附带三个记录版本。始终将更改合并到 `serverRecord` -- 它具有正确的更改标记。

```swift
func resolveConflict(_ error: CKError) {
    guard error.code == .serverRecordChanged,
          let ancestor = error.ancestorRecord,
          let client = error.clientRecord,
          let server = error.serverRecord
    else { return }

    // 将客户端更改合并到服务器记录
    for key in client.changedKeys() {
        if server[key] == ancestor[key] {
            server[key] = client[key]           // 服务器未更改，使用客户端
        } else if client[key] == ancestor[key] {
            // 客户端未更改，保留服务器（已在其中）
        } else {
            server[key] = mergeValues(          // 两者都更改，自定义合并
                ancestor: ancestor[key], client: client[key], server: server[key])
        }
    }

    Task { try await CKContainer.default().privateCloudDatabase.save(server) }
}
```

## 常见错误

| 错误   | 修复   |
|--------|--------|
| 没有账户门控同步 | 检查 `accountStatus()` 和模型 `.noAccount` 作为用户可见状态。 |
| 公共数据库中的个人数据 | 使用私有范围存储用户数据；公共范围是应用程序范围内容。 |
| 定时器轮询 | 使用数据库订阅或 `CKSyncEngine`。 |
| 节流限制后的立即重试 | 尊重 `retryAfterSeconds` 并保留挂起工作。 |
| 假设引擎解决冲突 | 三向合并 `failedRecordSaves`，然后重新安排保存。 |
| 每次获取都使用 nil 标记 | 持久化标记/状态；仅在文档中记录的过期路径上重置。 |

## 审查清单

- [ ] 在“签名与能力”中启用 iCloud + CloudKit 能力
- [ ] 在同步前检查账户状态；优雅处理 `.noAccount`
- [ ] 使用私有数据库存储用户数据；公共数据库仅用于共享内容
- [ ] 在私有数据库中创建自定义记录区域；从共享发现共享数据库区域
- [ ] 使用 `CKError.serverRecordChanged` 处理，合并到 `serverRecord`
- [ ] 网络故障排队重试；尊重 `retryAfterSeconds`
- [ ] 使用基于推送的同步的 `CKDatabaseSubscription` 或 `CKSyncEngine`；远程通知启用以进行后台交付
- [ ] 将更改标记持久化到磁盘；`changeTokenExpired` 重置并重新获取
- [] `.partialFailure` 错误按项目检查 `partialErrorsByItemID`
- [] `.userDeletedZone` 通过重新创建区域和重新同步处理
- [] SwiftData CloudKit 审查报告模型兼容性和模式发布：初始化/验证开发模式，发布前提升，生产更改仅添加
- [] 观察 `NSUbiquitousKeyValueStore.didChangeExternallyNotification`
- [] 加密审查指出 `CKRecord.Reference` 不能使用 `encryptedValues`，因为 CloudKit 在服务器端需要它；加密字段不能查询/排序；`CKAsset` 默认加密
- [] `CKSyncEngine` 状态序列化跨启动持久化（iOS 17+）

## 参考资料

- 参考 [参考资料/cloudkit-patterns.md](参考资料/cloudkit-patterns.md) 以获取增量同步、CKShare、区域、CKAsset 存储、批量操作和仪表板使用。
- [CloudKit 框架](https://sosumi.ai/documentation/cloudkit)
- [CKContainer](https://sosumi.ai/documentation/cloudkit/ckcontainer)
- [CKRecord](https://sosumi.ai/documentation/cloudkit/ckrecord)
- [CKQuery](https://sosumi.ai/documentation/cloudkit/ckquery)
- [CKSubscription](https://sosumi.ai/documentation/cloudkit/cksubscription)
- [CKSyncEngine](https://sosumi.ai/documentation/cloudkit/cksyncengine)
- [CKShare](https://sosumi.ai/documentation/cloudkit/ckshare)
- [CKError](https://sosumi.ai/documentation/cloudkit/ckerror)
- [NSUbiquitousKeyValueStore](https://sosumi.ai/documentation/foundation/nsubiquitouskeyvaluestore)
- [SwiftData CloudKit 同步](https://sosumi.ai/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
