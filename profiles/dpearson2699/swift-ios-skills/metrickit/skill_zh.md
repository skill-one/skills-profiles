# MetricKit

使用 MetricKit 进行低开销的生产遥测，以补充本地 Instruments 和 Xcode Organizer 分析。在 iOS 和 iPadOS 27 上，优先使用 Swift 优先的 `MetricManager` 报告序列。仅在显式的 iOS 26 兼容性分支中保留 `MXMetricManager`。

> **Beta 敏感**：以下 iOS/iPadOS 27 界面基于 Apple 当前的 Beta 文档。由于此环境中无法获得 Xcode 27，因此尚未进行本地编译验证。发布前请重新检查链接的 Apple 文档并使用发布的 Xcode 27 SDK 进行编译。

在实现持久化摄取、详细报告分析或 iOS 26 兼容性路径时，加载 [MetricKit 扩展和兼容性模式](references/metrickit-patterns.md)。

## 目录

- [MetricManager 设置](#metricmanager-setup)
- [接收指标报告](#receiving-metric-reports)
- [接收诊断报告](#receiving-diagnostic-reports)
- [关键指标结果](#key-metric-results)
- [调用栈树](#call-stack-trees)
- [自定义 Signpost 指标](#custom-signpost-metrics)
- [持久化导出和上传](#durable-export-and-upload)
- [扩展启动测量](#extended-launch-measurement)
- [iOS 26 兼容性](#ios-26-compatibility)
- [Xcode Organizer](#xcode-organizer)
- [作用域边界](#scope-boundaries)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## MetricManager 设置

在应用启动时，创建并保留一个长生命周期的 `MetricManager`。为 `metricReports` 和 `diagnosticReports` 启动恰好一个消费者任务。

这两个属性都暴露了非抛出的 `AsyncSequence` 值：

- `metricReports: some AsyncSequence<MetricReport, Never>`
- `diagnosticReports: some AsyncSequence<DiagnosticReport, Never>`

Apple 文档说明，一个序列的并发消费者可以接收非确定性的子集。仅在单个消费者接收并持久化存储报告后才能分叉；延迟订阅可能会错过报告。

```swift
import MetricKit

@available(iOS 27.0, *)
final class MetricsService {
    private let manager = MetricManager()
    private var metricTask: Task<Void, Never>?
    private var diagnosticTask: Task<Void, Never>?

    func start(
        persistMetric: @escaping @Sendable (MetricReport) async -> Void,
        persistDiagnostic: @escaping @Sendable (DiagnosticReport) async -> Void
    ) {
        guard metricTask == nil, diagnosticTask == nil else { return }
        let manager = manager

        metricTask = Task {
            for await report in manager.metricReports {
                await persistMetric(report)
            }
        }

        diagnosticTask = Task {
            for await report in manager.diagnosticReports {
                await persistDiagnostic(report)
            }
        }
    }

    deinit {
        metricTask?.cancel()
        diagnosticTask?.cancel()
    }
}
```

持久化闭包是应用程序特定的。使用下面的持久化优先工作流程实现它们，而不是直接丢弃、仅记录或直接上传每个报告。如果需要状态范围指标，请使用文档中记录的 `init(enabledStateReportingDomains:)` 初始化器和所需域构建管理器。

## 接收指标报告

`MetricReport` 是 `Codable` 和 `Sendable`。它通过以下方式描述一个间隔：

- `timeRange: DateInterval`
- 可选的 `environment` 元数据
- `intervalEntries` 用于全日和更短间隔测量
- `stateEntries` 用于与应用程序状态相关联的测量

指标报告通常以每日的节奏到达。在提取单个结果之前持久化完整报告。

对于每日分析，读取记录的 `fullDayEntry` 并切换其 `MetricResult` 值：

```swift
let entry = report.intervalEntries.fullDayEntry

for result in entry.values {
    switch result {
    case .hangTime(let metric):
        analyzeHangTime(metric)
    case .peakMemory(let metric):
        analyzePeakMemory(metric)
    case .timeToFirstDraw(let metric):
        analyzeLaunch(metric)
    case .signpostInterval(let metric):
        analyzeSignpost(metric)
    @unknown default:
        preserveUnknownMetric(result)
    }
}
```

使用 `@unknown default`，以便 Beta 或未来的结果不会使摄取管道变得脆弱。即使当前应用程序不理解某个结果，也要保留原始编码报告。

## 接收诊断报告

`DiagnosticReport` 是 `Codable` 和 `Sendable`。它包含一个 `timeRange`、必需的 `environment` 元数据和一个 `DiagnosticResult`。

诊断是单个、基于事件的报告，旨在 MetricKit 生成时立即交付。不要假设每个崩溃、挂起或资源事件都会生成报告；系统采样和资格仍然适用。

持久化存储后，显式路由结果：

```swift
switch report.result {
case .crash(let diagnostic):
    analyzeCrash(diagnostic)
case .hang(let diagnostic):
    analyzeHang(diagnostic)
case .cpuException(let diagnostic):
    analyzeCPUException(diagnostic)
case .diskWriteException(let diagnostic):
    analyzeDiskWrites(diagnostic)
case .appLaunch(let diagnostic):
    analyzeLaunch(diagnostic)
case .memoryException(let diagnostic):
    analyzeMemory(diagnostic)
@unknown default:
    preserveUnknownDiagnostic(report)
}
```

iOS/iPadOS 27 诊断类型是 `CrashDiagnostic`、`HangDiagnostic`、`CPUExceptionDiagnostic`、`DiskWriteExceptionDiagnostic`、`AppLaunchDiagnostic` 和 `MemoryExceptionDiagnostic`。内存异常情况在 iOS 27 中是新的。

有用字段包括：

| 诊断 | 重要字段 |
|---|---|
| `CrashDiagnostic` | `callStackTree`、异常类型/代码/原因、信号、虚拟内存区域、终止类别/原因 |
| `HangDiagnostic` | `callStackTree`、`hangDuration` |
| `CPUExceptionDiagnostic` | `callStackTree`、`totalCPUTime`、`totalSampledTime` |
| `DiskWriteExceptionDiagnostic` | `callStackTree`、`totalBytesWritten` |
| `AppLaunchDiagnostic` | `callStackTree`、`launchDuration` |
| `MemoryExceptionDiagnostic` | `callStackTree` |

## 关键指标结果

选择一个小型遥测词汇，以匹配调查而不是导出每个结果。优先考虑相关类别：响应性和终止；运行时、CPU、内存、网络和存储；或启动、显示/GPU 和自定义间隔。

按应用版本和环境元数据聚合，比较分布而不是单个值，并将回归与发布相关联。避免将每日聚合视为单个用户操作的精确跟踪。

加载 [关键指标结果目录](references/metrickit-patterns.md#key-metric-result-catalog) 时，将精确的 `MetricResult` 案例映射到解析器或仪表板。

## 调用栈树

iOS 27 的 `CallStackTree` 替换了 `MXCallStackTree`。它是 `Codable` 和 `Sendable`，并暴露：

- `forEachFrame` 用于帧遍历
- `callStackThreads` 用于线程分析
- `binaryInfo` 用于图像和二进制元数据

在展平或符号化之前存储完整的诊断报告。保留二进制标识符和偏移量，以便服务器端符号化可以使用匹配的存档和 dSYMs。

## 自定义 Signpost 指标

通过管理器创建一个 OS 日志，然后使用 `mxSignpost` 进行开始/结束测量：

```swift
let log = manager.logHandle(category: "ImagePipeline")

mxSignpost(.begin, log: log, name: "Decode")
await decodeImage()
mxSignpost(.end, log: log, name: "Decode")
```

MetricKit 暴露的聚合作为 `MetricResult.signpostInterval`。不要在 `MetricReport` 上搜索 `signpostMetrics` 数组。

使用 `mxSignpost` 时需要 MetricKit 资源测量。Apple 文档说明，使用 `OSSignposter` 和 MetricKit 日志句柄创建的间隔不会填充 `mxSignpost` 提供的资源测量字段。

将高容量的本地跟踪与 MetricKit 聚合使用的稳定生产间隔分开。

## 持久化导出和上传

将报告交付视为至少一次摄取问题：

1. 使用 `JSONEncoder` 对完整的 `MetricReport` 或 `DiagnosticReport` 进行编码。
2. 原子地将字节入队到应用拥有的持久化输出箱中。
3. 记录报告类型、模式版本、应用版本和一个稳定的去重键。
4. 仅在入队成功后才确认本地处理。
5. 后续使用重试、退避、批处理和保留限制上传。
6. 仅在服务器接受后才标记输出箱项已上传。

```swift
let data = try JSONEncoder().encode(report)
try await durableOutbox.enqueue(data, kind: .metric)
```

`durableOutbox` 是应用拥有的抽象，不是 MetricKit API。不要在序列消费者中执行同步网络上传。

持久化本地存储是现代序列接收报告的恢复机制；不要使成功摄取依赖于假设的现代回填 API。

## 扩展启动测量

使用 `trackLaunchTask(id:onTrackingError:_:)` 在管理器上执行超出首次绘制时间的工作：

```swift
await manager.trackLaunchTask(
    id: "bootstrap-data",
    onTrackingError: { error in
        recordLaunchTrackingError(error)
    }
) {
    await bootstrapApplication()
}
```

该 API 是 `@MainActor`，并具有同步和异步重载。任务闭包的结果和抛出的错误传播到调用者；`MetricManager.LaunchTaskError` 通过 `onTrackingError` 报告，而不会中断跟踪的工作。结果作为 `MetricResult.extendedLaunch` 出现。

使用稳定的 `LaunchTaskID` 值，并仅跟踪启动关键工作。

## iOS 26 兼容性

对于仍然部署到 iOS 26 的应用，使用可用性边界：

- iOS/iPadOS 27：使用 `MetricManager` 并消费两个异步报告序列。
- iOS/iPadOS 26 和更早支持发布：使用 `MXMetricManager.shared`、`MXMetricManagerSubscriber` 和遗留有效载荷回调。

遗留 API 是唯一记录的具有 `pastPayloads` 和 `pastDiagnosticPayloads` 的分支。`MXMetricManager` 在 iOS 27 中已弃用，因此应通过可用性检查将其隔离，而不是将遗留有效载荷混合到现代管道中。

加载 [iOS 26 兼容性](references/metrickit-patterns.md#ios-26-compatibility) 以获取完整的订阅者、遗留 Signpost、过去有效载荷和扩展启动模式。

## Xcode Organizer

使用 Xcode Organizer 检查 Apple 汇聚的生产指标、挂起、崩溃和回归，然后再构建自定义后端。当产品需要自定义关联、保留、警报或与现有可观察性系统集成时，使用直接 MetricKit 摄取。

不要期望开发设备运行会重现生产报告的种群、节奏或聚合。

## 作用域边界

| 任务 | 使用替代方案 |
|---|---|
| 本地复现问题或记录详细跟踪 | `debugging-instruments` |
| 诊断保留对象或内存图路径 | `ios-memgraph-analysis` |
| 调整 SwiftUI 无效、身份或滚动代码 | `swiftui-performance` |
| 研究结构化 EnergyKit 影响数据 | `energykit` |
| 设计通用日志和 os_signpost 策略 | `swift-logging` |

MetricKit 识别生产症状和趋势。将实际代码修复路由到拥有受影响子系统的技能。

## 常见错误

| 错误 | 修正 |
|---|---|
| 直接在序列循环中上传 | 首先本地编码和入队；稍后异步上传。 |
| 假设每个诊断事件都会生成报告 | 将诊断视为采样的、系统生成的证据。 |
| 在 `MetricManager` 上寻找 `pastPayloads` | 仅在 iOS 26 的 `MXMetricManager` 分支中保留遗留回填。 |
| 仅解析已知的枚举情况 | 保留原始报告并使用 `@unknown default`。 |
| 在 iOS 27 分支中使用 `MXMetricManager.makeLogHandle` | 使用 `manager.logHandle(category:)`。 |
| 在 iOS 27 分支中使用成对的扩展/完成启动调用 | 使用 `trackLaunchTask`。 |
| 将 MetricKit 聚合视为本地跟踪 | 使用 Instruments 和 Signpost 复现。 |

## 审查清单

- [ ] iOS 27 分支在启动时使用一个保留的 `MetricManager` 和每个报告序列的一个消费者。
- [ ] 每个报告在分析或上传前都编码并持久化入队。
- [ ] 诊断和指标开关使用 `@unknown default`。
- [ ] 未知原始报告仍然是可恢复的。
- [ ] 符号化元数据和匹配的 dSYMs 被保留。
- [ ] 自定义间隔使用 `manager.logHandle(category:)` 和 `mxSignpost`。
- [ ] 扩展启动工作使用 `trackLaunchTask`。
- [ ] iOS 26 的 `MXMetricManager` 路径被可用性检查隔离。
- [ ] 生产聚合在适当的情况下会引导本地 Instruments 调查。
- [ ] iOS 27 Beta API 已重新检查并使用发布的 Xcode 27 SDK 编译。

## 参考资料

- [MetricManager](https://sosumi.ai/documentation/metrickit/metricmanager)
- [Metric 报告序列](https://sosumi.ai/documentation/metrickit/metricmanager/metricreports)
- [诊断报告序列](https://sosumi.ai/documentation/metrickit/metricmanager/diagnosticreports)
- [MetricReport](https://sosumi.ai/documentation/metrickit/metricreport)
- [DiagnosticReport](https://sosumi.ai/documentation/metrickit/diagnosticreport)
- [MetricResult](https://sosumi.ai/documentation/metrickit/metricresult)
- [DiagnosticResult](https://sosumi.ai/documentation/metrickit/diagnosticresult)
- [CallStackTree](https://sosumi.ai/documentation/metrickit/callstacktree)
- [使用 MetricKit 监控应用性能](https://sosumi.ai/documentation/metrickit/monitoring-app-performance-with-metrickit)
- [使用 MetricKit 分析应用性能](https://sosumi.ai/documentation/metrickit/analyzing-app-performance-with-metrickit)
- [iOS & iPadOS 27 发布说明](https://sosumi.ai/documentation/ios-ipados-release-notes/ios-ipados-27-release-notes)
- [MetricKit 新功能 (WWDC26)](https://sosumi.ai/videos/play/wwdc2026/222)
- [MetricKit 扩展和兼容性模式](references/metrickit-patterns.md)
