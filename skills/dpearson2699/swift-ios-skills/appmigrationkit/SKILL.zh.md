---
name: appmigrationkit
description: 使用 AppMigrationKit 将应用数据迁移到或从其他平台。在实施系统协调的 iOS 和 Android 或其他平台之间的单次迁移、构建 AppMigrationExtension、使用 ResourcesArchiver 打包可传输资源、在目标设备上导入资源、报告导入进度、处理迁移错误和应用组清理、检查 MigrationStatus 或使用 AppMigrationTester 测试迁移代码时使用。
---

# AppMigrationKit

一次性跨平台数据传输用于应用资源。使应用能够在设备设置或引导过程中将数据导出到或从另一个平台（例如 Android）导入。AppMigrationKit API 是 iOS 26.0+/iPadOS 26.0+；数据容器权限是 iOS 26.1+/iPadOS 26.1+/Mac Catalyst 26.1+。Swift 6.3。

> **Beta敏感。** AppMigrationKit 是 iOS 26 中的新功能，可能在正式版发布前发生变化。在依赖特定 API 细节之前，请重新检查当前的 Apple 文档。

AppMigrationKit 使用应用扩展模型。系统协调设备之间的传输。应用提供一个符合导出和导入协议的扩展，系统在适当的时间调用该扩展。应用本身永远不会管理设备之间的网络连接。

## 内容

- [架构概述](#architecture-overview)
- [设置和权限](#setup-and-entitlements)
- [应用迁移扩展](#app-migration-extension)
- [导出资源](#exporting-resources)
- [导入资源](#importing-resources)
- [迁移状态](#migration-status)
- [进度跟踪](#progress-tracking)
- [测试](#testing)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 架构概述

AppMigrationKit 通过三层运行：

1. **应用扩展** -- 系统在迁移过程中调用的符合 `AppMigrationExtension` 类型的扩展。它处理数据导出和导入。
2. **系统协调** -- 操作系统管理设备到设备的会话、传输和调度。扩展不会控制其运行时间。
3. **包含应用** -- 迁移完成后，应用在首次启动时检查 `MigrationStatus.importStatus` 以确定是否发生了迁移以及是否成功。

关键类型：

| 类型 | 角色 |
|---|---|
| `AppMigrationExtension` | 应用扩展入口点的协议 |
| `ResourcesExportingWithOptions` | 通过归档器导出文件的协议 |
| `ResourcesExporting` | 简化导出协议（无自定义选项） |
| `ResourcesImporting` | 在目标设备上导入文件的协议 |
| `ResourcesArchiver` | 将文件流到导出归档 |
| `MigrationDataContainer` | 访问包含应用的 数据目录 |
| `MigrationStatus` | 从包含应用检查导入结果 |
| `MigrationPlatform` | 识别另一台设备的平台（例如 `.android`） |
| `MigrationAppIdentifier` | 通过商店和捆绑 ID 识别源应用 |
| `AppMigrationTester` | 用于验证导出/导入逻辑的测试专用角色 |

## 设置和权限

### 权限

应用扩展需要 `com.apple.developer.app-migration.data-container-access` 权限。其值是一个包含包含应用的捆绑 ID 的单元素字符串数组：

```xml
<key>com.apple.developer.app-migration.data-container-access</key>
<array>
    <string>com.example.myapp</string>
</array>
```

没有其他值是有效的。此权限在导出期间授予扩展对包含应用的 数据容器的读取访问权限，在导入期间授予写入访问权限。该权限本身在 iOS 26.1+、iPadOS 26.1+ 和 Mac Catalyst 26.1+ 上可用，即使核心 AppMigrationKit API 在 iOS 26.0+ 和 iPadOS 26.0+ 上可用。

### 扩展目标

在 Xcode 项目中添加一个新的应用扩展目标。该扩展符合一个或多个迁移协议（`ResourcesExportingWithOptions`、`ResourcesExporting`、`ResourcesImporting`）。

## 应用迁移扩展

扩展入口点符合 `AppMigrationExtension`。在迁移过程中，系统会阻止启动包含应用及其其他扩展，以确保独占数据访问。

### 访问数据容器

扩展通过 `appContainer` 访问包含应用的文件：

```swift
import AppMigrationKit

struct MyMigrationExtension: ResourcesExporting {
    var resourcesSizeEstimate: Int { estimateTotalExportSize() }
    var resourcesVersion: String { "1.0" }
    var resourcesCompressible: Bool { true }

    func exportResources(
        to archiver: sending ResourcesArchiver,
        request: MigrationRequest
    ) async throws {
        let container = appContainer

        // container.bundleIdentifier     -- 应用的捆绑 ID
        // container.containerRootDirectory -- 应用容器的根目录
        // container.documentsDirectory    -- Documents/
        // container.applicationSupportDirectory -- Application Support/
    }
}
```

`MigrationDataContainer` 提供 `containerRootDirectory`、`documentsDirectory` 和 `applicationSupportDirectory` 作为指向包含应用的沙盒的 `URL` 值。

## 导出资源

符合 `ResourcesExportingWithOptions`（或 `ResourcesExporting` 用于无自定义选项）以打包文件用于传输。系统会调用 `exportResources(to:request:)` 并提供一个 `ResourcesArchiver` 和一个 `MigrationRequestWithOptions`。

### 声明导出属性

```swift
struct MyMigrationExtension: ResourcesExportingWithOptions {
    typealias OptionsType = MigrationDefaultSupportedOptions

    var resourcesSizeEstimate: Int {
        // 返回导出数据的估计总字节数
        calculateExportSize()
    }

    var resourcesVersion: String {
        "1.0"
    }

    var resourcesCompressible: Bool {
        true  // 允许系统在传输过程中压缩
    }
}
```

- `resourcesSizeEstimate` -- 估计总字节数。系统使用此值用于进度 UI 和可用空间检查。
- `resourcesVersion` -- 格式版本字符串。导入端接收此值以处理版本化数据格式。
- `resourcesCompressible` -- 当 `true` 时，归档器可以在传输过程中压缩文件。

### 实现导出

```swift
func exportResources(
    to archiver: sending ResourcesArchiver,
    request: MigrationRequestWithOptions<MigrationDefaultSupportedOptions>
) async throws {
    let docsDir = appContainer.documentsDirectory

    // 如有需要，检查目标平台
    if request.destinationPlatform == .android {
        // 平台特定的导出逻辑
    }

    // 一次添加一个文件 -- 保持连续进度
    let userDataURL = docsDir.appending(path: "user_data.json")
    try await archiver.appendItem(at: userDataURL)

    // 使用自定义归档路径添加
    let settingsURL = docsDir.appending(path: "settings.plist")
    try await archiver.appendItem(at: settingsURL, pathInArchive: "preferences/settings.plist")

    // 添加一个目录
    let photosDir = docsDir.appending(path: "photos")
    try await archiver.appendItem(at: photosDir, pathInArchive: "media/photos")
}
```

归档器会增量流式传输文件。重复调用 `appendItem(at:pathInArchive:)` 每次资源准备好时。如果扩展似乎卡住，系统可能会终止扩展，因此避免在追加调用之间出现长时间间隔。

### 取消

`ResourcesArchiver` 通过抛出取消错误自动处理任务取消。不要捕获这些错误——这样做会导致系统终止扩展。

### 迁移平台

`MigrationRequestWithOptions` 将 `destinationPlatform` 暴露为 `MigrationPlatform` 值。使用此值来定制导出的数据：

```swift
if request.destinationPlatform == .android {
    // 导出 Android 应用期望的格式
}
```

`MigrationPlatform` 提供 `.android` 作为静态常量。自定义平台可以使用 `MigrationPlatform("customPlatform")` 创建。

## 导入资源

符合 `ResourcesImporting` 以在目标设备上接收传输的文件。系统在应用安装后但在应用可启动之前调用 `importResources(at:request:)`。

```swift
struct MyMigrationExtension: ResourcesImporting {
    func importResources(
        at importedDataURL: URL,
        request: ResourcesImportRequest
    ) async throws {
        let sourceVersion = request.sourceVersion
        let sourceApp = request.sourceAppIdentifier

        // sourceApp.platform        -- 例如，.android
        // sourceApp.bundleIdentifier -- 源应用的捆绑 ID
        // sourceApp.storeIdentifier  -- 例如，.googlePlay

        // 将导入的文件复制到应用容器
        let docsDir = appContainer.documentsDirectory

        let userData = importedDataURL.appending(path: "user_data.json")
        if FileManager.default.fileExists(atPath: userData.path()) {
            try FileManager.default.copyItem(
                at: userData,
                to: docsDir.appending(path: "user_data.json")
            )
        }
    }
}
```

### 导入期间错误处理

导入错误时，系统会清除包含应用的数据容器以防止部分状态。但是应用组容器不会被清除。导入实现应在写入导入内容之前清除任何应用组容器：

```swift
func importResources(
    at url: URL,
    request: ResourcesImportRequest
) async throws {
    // 首先清除共享应用组数据
    let groupURL = FileManager.default.containerURL(
        forSecurityApplicationGroupIdentifier: "group.com.example.myapp"
    )
    if let groupURL {
        try? FileManager.default.removeItem(at: groupURL.appending(path: "shared_data"))
    }

    // 然后导入
    try await performImport(from: url)
}
```

### 源应用标识符

`ResourcesImportRequest` 提供 `sourceAppIdentifier` 作为具有三个属性的 `MigrationAppIdentifier`：

- `platform` -- 源设备的平台（例如 `.android`）
- `bundleIdentifier` -- 源应用的捆绑标识符
- `storeIdentifier` -- 应用商店（例如 `.googlePlay`）

## 迁移状态

迁移完成后，包含应用在首次启动时检查结果：

```swift
import AppMigrationKit

func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
) -> Bool {
    if let status = MigrationStatus.importStatus {
        switch status {
        case .success:
            showMigrationSuccessUI()
            MigrationStatus.clearImportStatus()
        case .failure(let error):
            showMigrationFailureUI(error: error)
            MigrationStatus.clearImportStatus()
        }
    }
    return true
}
```

- `MigrationStatus.importStatus` 如果没有发生迁移则为 `nil`。
- 处理结果后调用 `clearImportStatus()` 以防止在后续启动时显示通知。
- 枚举有两个情况：`.success` 和 `.failure(any Error)`。

## 进度跟踪

导入端通过 `resourcesImportProgress` 暴露一个 `Progress` 对象。系统使用此对象向用户显示传输进度。在导入期间逐步更新 `completedUnitCount`：

```swift
struct MyMigrationExtension: ResourcesImporting {
    private let importProgress = Progress(totalUnitCount: 100)

    var resourcesImportProgress: Progress { importProgress }

    func importResources(
        at importedDataURL: URL,
        request: ResourcesImportRequest
    ) async throws {
        let files = try FileManager.default.contentsOfDirectory(
            at: importedDataURL, includingPropertiesForKeys: nil
        )
        let increment = Int64(100 / max(files.count, 1))
        for file in files {
            try processFile(file)
            importProgress.completedUnitCount += increment
        }
        importProgress.completedUnitCount = 100
    }
}
```

## 测试

`AppMigrationTester` 是由包含应用托管的单元测试中用于验证迁移逻辑的测试专用角色。不要在生产环境中使用它。

```swift
import Testing
import AppMigrationKit

@Test func testExportImportRoundTrip() async throws {
    let tester = try await AppMigrationTester(platform: .android)

    // 导出
    let result = try await tester.exportController.exportResources(
        request: nil, progress: nil
    )
    #expect(result.exportProperties.uncompressedBytes > 0)

    // 导入导出的数据
    try await tester.importController.importResources(
        from: result.extractedResourcesURL,
        importRequest: nil, progress: nil
    )
    try await tester.importController.registerImportCompletion(with: .success)
}
```

结果上的 `DeviceToDeviceExportProperties` 暴露 `uncompressedBytes`、`compressedBytes`（如果不可压缩则为 `nil`）、`sizeEstimate` 和 `version`。

有关其他测试模式的更多信息，请参阅 [参考资料/appmigrationkit-patterns.md](references/appmigrationkit-patterns.md)。

## 常见错误

### 不要：捕获来自 ResourcesArchiver 的取消错误

```swift
// 错误 -- 如果取消被忽略，系统会终止扩展
func exportResources(to archiver: sending ResourcesArchiver, request: ...) async throws {
    do {
        try await archiver.appendItem(at: fileURL)
    } catch is CancellationError {
        // 忽略取消错误会导致终止
    }
}

// 正确 -- 让取消传播
func exportResources(to archiver: sending ResourcesArchiver, request: ...) async throws {
    try await archiver.appendItem(at: fileURL)
}
```

### 不要：在 archiver append 调用之间留出长时间间隔

```swift
// 错误 -- 系统可能会认为扩展卡住并终止它
func exportResources(to archiver: sending ResourcesArchiver, request: ...) async throws {
    let allFiles = gatherAllFiles()  // 需要 30 秒
    for file in allFiles {
        try await archiver.appendItem(at: file)
    }
}

// 正确 -- 交错文件准备和归档
func exportResources(to archiver: sending ResourcesArchiver, request: ...) async throws {
    for file in knownFilePaths() {
        try await archiver.appendItem(at: file)
    }
}
```

### 不要：在导出期间将文件转换为中间格式

```swift
// 错误 -- 可能会耗尽磁盘空间以创建临时副本
func exportResources(to archiver: sending ResourcesArchiver, request: ...) async throws {
    let converted = try convertToJSON(originalDatabase)  // 磁盘使用量翻倍
    try await archiver.appendItem(at: converted)
}

// 正确 -- 原样导出文件，如果需要，在导入端转换
func exportResources(to archiver: sending ResourcesArchiver, request: ...) async throws {
    try await archiver.appendItem(at: originalDatabase)
}
```

### 不要：在导入错误恢复期间忽略应用组容器

```swift
// 错误 -- 系统在错误时清除应用容器但不清除应用组
func importResources(at url: URL, request: ResourcesImportRequest) async throws {
    try writeToAppGroup(data)
    try writeToAppContainer(data)  // 如果这个抛出异常，应用组有陈旧数据
}

// 正确 -- 在导入之前清除应用组数据
func importResources(at url: URL, request: ResourcesImportRequest) async throws {
    try clearAppGroupData()
    try writeToAppGroup(data)
    try writeToAppContainer(data)
}
```

### 不要：处理导入状态后忘记清除

```swift
// 错误 -- 迁移 UI 每次启动都会显示
if let status = MigrationStatus.importStatus {
    showMigrationResult(status)
    // 缺少 clearImportStatus()
}

// 正确
if let status = MigrationStatus.importStatus {
    showMigrationResult(status)
    MigrationStatus.clearImportStatus()
}
```

## 审查清单

- [ ] 添加了具有 `com.apple.developer.app-migration.data-container-access` 项权的扩展目标
- [ ] 项权数组包含且仅包含一个字符串：包含应用的捆绑标识符
- [ ] 扩展符合 `ResourcesExportingWithOptions` 或 `ResourcesExporting` 以进行导出
- [ ] 扩展符合 `ResourcesImporting` 以进行导入
- [ ] `resourcesSizeEstimate` 返回合理的字节估计
- [ ] `resourcesVersion` 已设置，并在导入时检查格式兼容性
- [ ] 导出调用 `appendItem` 时逐步进行，无长时间暂停
- [ ] 来自 `ResourcesArchiver` 的取消错误未被捕获
- [ ] 导入在写入新数据前清除应用组容器
- [ ] 包含应用在首次启动时检查 `MigrationStatus.importStatus`
- [ ] 处理迁移结果后调用 `clearImportStatus()`
- [ ] `AppMigrationTester` 用于单元测试以验证导出和导入
- [ ] 文件按原样导出，导出端无中间格式转换
- [ ] 导入请求中的 `sourceVersion` 用于处理版本化数据格式

## 参考文献

- 扩展模式（组合扩展、版本化迁移、文件枚举、错误恢复）：[references/appmigrationkit-patterns.md](references/appmigrationkit-patterns.md)
- [AppMigrationKit 框架](https://sosumi.ai/documentation/appmigrationkit)
- [AppMigrationExtension](https://sosumi.ai/documentation/appmigrationkit/appmigrationextension)
- [ResourcesExportingWithOptions](https://sosumi.ai/documentation/appmigrationkit/resourcesexportingwithoptions)
- [ResourcesImporting](https://sosumi.ai/documentation/appmigrationkit/resourcesimporting)
- [ResourcesArchiver](https://sosumi.ai/documentation/appmigrationkit/resourcesarchiver)
- [MigrationStatus](https://sosumi.ai/documentation/appmigrationkit/migrationstatus)
- [MigrationDataContainer](https://sosumi.ai/documentation/appmigrationkit/migrationdatacontainer)
- [AppMigrationTester](https://sosumi.ai/documentation/appmigrationkit/appmigrationtester)
- [数据容器项权](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.app-migration.data-container-access)
