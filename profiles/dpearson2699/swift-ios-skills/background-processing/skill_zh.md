# 后台处理

使用 BackgroundTasks 框架、后台 URLSession 和后台推送通知在 iOS 上注册、调度和执行后台工作。

## 目录

- [Info.plist 配置](#infoplist-配置)
- [BGTaskScheduler 注册](#bgtaskscheduler-注册)
- [BGAppRefreshTask 模式](#bgapprefreshtask-模式)
- [BGProcessingTask 模式](#bgprocessingtask-模式)
- [BGContinuedProcessingTask (iOS 26+)](#bgcontinuedprocessingtask-ios-26)
- [后台 URLSession 下载](#background-urlsession-downloads)
- [后台推送触发器](#background-push-triggers)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## Info.plist 配置

每个任务标识符 **必须** 在 `Info.plist` 下的 `BGTaskSchedulerPermittedIdentifiers` 中声明，否则 `submit(_:)` 会抛出 `BGTaskScheduler.Error.Code.notPermitted`。

```xml
<key>BGTaskSchedulerPermittedIdentifiers</key>
<array>
    <string>com.example.app.refresh</string>
    <string>com.example.app.db-cleanup</string>
    <string>com.example.app.export.*</string>
</array>
```

同时启用所需的 `UIBackgroundModes`：

```xml
<key>UIBackgroundModes</key>
<array>
    <string>fetch</string>       <!-- BGAppRefreshTask 所需 -->
    <string>processing</string>  <!-- BGProcessingTask 所需 -->
</array>
```

在 Xcode 中：目标 > 签名与能力 > 后台模式 > 启用 "后台获取" 和 "后台处理"。

## BGTaskScheduler 注册

在应用启动完成 **之前** 注册处理程序。在 UIKit 中，在 `application(_:didFinishLaunchingWithOptions:)` 中注册；在 SwiftUI 中，在 `App.init()` 中注册。

### UIKit 注册

```swift
import BackgroundTasks

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: "com.example.app.refresh",
            using: nil  // nil = 默认后台队列
        ) { task in
            self.handleAppRefresh(task: task as! BGAppRefreshTask)
        }

        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: "com.example.app.db-cleanup",
            using: nil
        ) { task in
            self.handleDatabaseCleanup(task: task as! BGProcessingTask)
        }

        return true
    }
}
```

### SwiftUI 注册

```swift
import SwiftUI
import BackgroundTasks

@main
struct MyApp: App {
    init() {
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: "com.example.app.refresh",
            using: nil
        ) { task in
            BackgroundTaskManager.shared.handleAppRefresh(
                task: task as! BGAppRefreshTask
            )
        }
    }

    var body: some Scene {
        WindowGroup { ContentView() }
    }
}
```

## BGAppRefreshTask 模式

用于获取少量数据更新的短时任务（约 30 秒）。系统决定启动时间；`earliestBeginDate` 仅是下限提示。

```swift
func scheduleAppRefresh() {
    let request = BGAppRefreshTaskRequest(
        identifier: "com.example.app.refresh"
    )
    request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)
    do {
        try BGTaskScheduler.shared.submit(request)
    } catch {
        print("无法安排应用刷新: \(error)")
    }
}

func handleAppRefresh(task: BGAppRefreshTask) {
    // 在执行工作之前安排下一次刷新
    scheduleAppRefresh()

    let fetchTask = Task {
        do {
            let data = try await APIClient.shared.fetchLatestFeed()
            await FeedStore.shared.update(with: data)
            task.setTaskCompleted(success: true)
        } catch {
            task.setTaskCompleted(success: false)
        }
    }

    // 关键：处理过期 -- 系统随时可能撤销时间
    task.expirationHandler = {
        fetchTask.cancel()
        task.setTaskCompleted(success: false)
    }
}
```

## BGProcessingTask 模式

用于维护、数据处理或清理的长时任务（分钟级）。它们在设备空闲时运行，可能需要外部电源；相同的 `earliestBeginDate` 下限规则适用。

```swift
func scheduleProcessingTask() {
    let request = BGProcessingTaskRequest(
        identifier: "com.example.app.db-cleanup"
    )
    request.requiresNetworkConnectivity = false
    request.requiresExternalPower = true
    request.earliestBeginDate = Date(timeIntervalSinceNow: 60 * 60)
    do {
        try BGTaskScheduler.shared.submit(request)
    } catch {
        print("无法安排处理任务: \(error)")
    }
}

func handleDatabaseCleanup(task: BGProcessingTask) {
    scheduleProcessingTask()

    let cleanupTask = Task {
        do {
            try await DatabaseManager.shared.purgeExpiredRecords()
            try await DatabaseManager.shared.rebuildIndexes()
            task.setTaskCompleted(success: true)
        } catch {
            task.setTaskCompleted(success: false)
        }
    }

    task.expirationHandler = {
        cleanupTask.cancel()
        task.setTaskCompleted(success: false)
    }
}
```

## BGContinuedProcessingTask (iOS 26+)

由用户操作在前台启动的任务，在后台继续运行。系统通过 Live Activity 显示进度。符合 `ProgressReporting`。

**可用性：** iOS 26.0+、iPadOS 26.0+

与 `BGAppRefreshTask` 和 `BGProcessingTask` 不同，此任务从前台立即启动。在资源压力下，系统可能会终止它，优先考虑报告最小进度任务。设置 `expirationHandler` 以处理用户或系统取消，取消进行中的工作，并在报告完成之前清理部分输出。

```swift
import BackgroundTasks

func startExport() {
    // 在应用启动时注册任务处理程序，而不是在这里。
    // BGTaskScheduler 要求在应用启动完成前注册。
    let jobID = UUID().uuidString
    let request = BGContinuedProcessingTaskRequest(
        identifier: "com.example.app.export.\(jobID)",
        title: "导出照片",
        subtitle: "处理 247 项"
    )
    // 使用允许的基础通配符标识符：com.example.app.export.*
    // earliestBeginDate 对持续处理请求被忽略。
    // .queue：如果不能立即运行，立即开始
    // .fail：如果不能立即运行，提交失败
    request.strategy = .queue

    do {
        try BGTaskScheduler.shared.submit(request)
    } catch {
        print("无法提交持续处理任务: \(error)")
    }
}

func performExport(task: BGContinuedProcessingTask) async {
    let items = await PhotoLibrary.shared.itemsToExport()
    let progress = task.progress
    progress.totalUnitCount = Int64(items.count)

    for (index, item) in items.enumerated() {
        if Task.isCancelled { break }

        await PhotoExporter.shared.export(item)
        progress.completedUnitCount = Int64(index + 1)

        // 更新用户界面标题/副标题
        task.updateTitle(
            "导出照片",
            subtitle: "\(index + 1) of \(items.count) complete"
        )
    }

    task.setTaskCompleted(success: !Task.isCancelled)
}
```

对于 GPU 工作，检查支持并启用后台 GPU 访问 (`com.apple.developer.background-tasks.continued-processing.gpu`)：

```swift
let supported = BGTaskScheduler.supportedResources
if supported.contains(.gpu) {
    request.requiredResources = .gpu
}
```

## 后台 URLSession 下载

使用 `URLSessionConfiguration.background` 进行下载，即使应用被挂起或终止后仍能继续。系统处理进程外的传输。

```swift
class DownloadManager: NSObject, URLSessionDownloadDelegate {
    static let shared = DownloadManager()

    private lazy var session: URLSession = {
        let config = URLSessionConfiguration.background(
            withIdentifier: "com.example.app.background-download"
        )
        config.isDiscretionary = true
        config.sessionSendsLaunchEvents = true
        return URLSession(configuration: config, delegate: self, delegateQueue: nil)
    }()

    func startDownload(from url: URL) {
        let task = session.downloadTask(with: url)
        task.earliestBeginDate = Date(timeIntervalSinceNow: 60)
        task.resume()
    }

    func urlSession(
        _ session: URLSession,
        downloadTask: URLSessionDownloadTask,
        didFinishDownloadingTo location: URL
    ) {
        // 在此方法返回前将文件从临时目录移动
        let dest = FileManager.default.urls(
            for: .documentDirectory, in: .userDomainMask
        )[0].appendingPathComponent("download.dat")
        try? FileManager.default.moveItem(at: location, to: dest)
    }

    func urlSession(
        _ session: URLSession,
        task: URLSessionTask,
        didCompleteWithError error: (any Error)?
    ) {
        if let error { print("下载失败: \(error)") }
    }
}
```

处理应用重启 — 存储并调用系统完成处理程序：

```swift
// 在 AppDelegate 中：
func application(
    _ application: UIApplication,
    handleEventsForBackgroundURLSession identifier: String,
    completionHandler: @escaping () -> Void
) {
    backgroundSessionCompletionHandler = completionHandler
}

// 在 URLSessionDelegate 中 — 当事件完成时调用存储的处理程序：
func urlSessionDidFinishEvents(forBackgroundURLSession session: URLSession) {
    Task { @MainActor in
        self.backgroundSessionCompletionHandler?()
        self.backgroundSessionCompletionHandler = nil
    }
}
```

## 后台推送触发器

静默推送通知会短暂唤醒应用以获取新内容。在推送负载中设置 `content-available: 1`。

```json
{ "aps": { "content-available": 1 }, "custom-data": "new-messages" }
```

使用 `apns-push-type: background` 和 `apns-priority: 5` 发送 APNs 请求。后台推送交付是低优先级且不保证的；保持发送频率较低，通常每小时不超过两到三次。

在 AppDelegate 中处理：

```swift
func application(
    _ application: UIApplication,
    didReceiveRemoteNotification userInfo: [AnyHashable: Any],
    fetchCompletionHandler completionHandler:
        @escaping (UIBackgroundFetchResult) -> Void
) {
    Task {
        do {
            let hasNew = try await MessageStore.shared.fetchNewMessages()
            completionHandler(hasNew ? .newData : .noData)
        } catch {
            completionHandler(.failed)
        }
    }
}
```

在后台模式中启用 "远程通知" 并注册：

```swift
UIApplication.shared.registerForRemoteNotifications()
```

## 常见错误

### 1. 缺少 Info.plist 标识符

```swift
// 不要：提交标识符不在 BGTaskSchedulerPermittedIdentifiers 中的任务
let request = BGAppRefreshTaskRequest(identifier: "com.example.app.refresh")
try BGTaskScheduler.shared.submit(request)  // 抛出 .notPermitted

// 要：将每个标识符添加到 Info.plist BGTaskSchedulerPermittedIdentifiers
// <string>com.example.app.refresh</string>
```

### 2. 未调用 setTaskCompleted(success:)

使用上述规范的应用刷新或处理处理程序：每个成功、失败和取消路径都精确报告一次完成。

### 3. 忽略过期处理程序

使用相同的规范处理程序来取消进行中的工作并从 `expirationHandler` 报告失败。

### 4. 调度过于频繁

调度部分拥有下限规则。避免分钟级刷新请求；系统仍然选择实际启动时间。

### 5. 过度依赖后台时间

```swift
// 不要：启动一个 10 分钟的操作，假设它会完成
func handleRefresh(task: BGAppRefreshTask) {
    Task { await tenMinuteSync() }
}

// 要：设计可增量且可取消的工作
func handleRefresh(task: BGAppRefreshTask) {
    let work = Task {
        for batch in batches {
            try Task.checkCancellation()
            await processBatch(batch)
            await saveBatchProgress(batch)
        }
        task.setTaskCompleted(success: true)
    }
    task.expirationHandler = {
        work.cancel()
        task.setTaskCompleted(success: false)
    }
}
```

## 审查清单

- [ ] 所有任务标识符列在 `BGTaskSchedulerPermittedIdentifiers`
- [ ] 所需的 `UIBackgroundModes` 启用 (`fetch`, `processing`)
- [ ] 任务在应用启动完成前注册
- [ ] 每个代码路径调用 `setTaskCompleted(success:)`
- [ ] 设置 `expirationHandler` 并取消进行中的工作
- [ ] 在处理程序中安排下一个任务（重新调度模式）
- [ ] `earliestBeginDate` 使用合理的时间间隔并视为提示
- [ ] 后台 URLSession 使用代理（而不是异步/闭包）
- [ ] 后台 URLSession 在 `didFinishDownloadingTo` 中返回前移动文件
- [ ] `handleEventsForBackgroundURLSession` 存储并调用完成处理程序
- [ ] 后台推送负载包含 `content-available: 1`
- [ ] 后台推送 APNs 请求使用 `apns-push-type: background` 和 `apns-priority: 5`
- [ ] `fetchCompletionHandler` 及时调用并使用正确结果
- [ ] BGContinuedProcessingTask 通过 `ProgressReporting` 报告进度
- [ ] 工作是增量且可取消的 (`Task.checkCancellation()`)
- [ ] 任务处理程序中没有阻塞同步工作

## 参考资料

- 参考 [references/background-task-patterns.md](references/background-task-patterns.md) 获取扩展模式、后台 URLSession 边缘情况、使用模拟启动进行调试以及后台推送最佳实践。
- [BGTaskScheduler](https://sosumi.ai/documentation/backgroundtasks/bgtaskscheduler)
- [BGAppRefreshTask](https://sosumi.ai/documentation/backgroundtasks/bgapprefreshtask)
- [BGProcessingTask](https://sosumi.ai/documentation/backgroundtasks/bgprocessingtask)
- [BGContinuedProcessingTask](https://sosumi.ai/documentation/backgroundtasks/bgcontinuedprocessingtask) (iOS 26+)
- [BGContinuedProcessingTaskRequest](https://sosumi.ai/documentation/backgroundtasks/bgcontinuedprocessingtaskrequest) (iOS 26+)
- [使用后台任务更新应用](https://sosumi.ai/documentation/uikit/using-background-tasks-to-update-your-app)
- [在 iOS 和 iPadOS 上执行长时间运行的任务](https://sosumi.ai/documentation/backgroundtasks/performing-long-running-tasks-on-ios-and-ipados)
