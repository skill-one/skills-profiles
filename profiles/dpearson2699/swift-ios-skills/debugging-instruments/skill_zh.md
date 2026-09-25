# 调试与工具

在此处保留交互式图形和 Instruments 紧急处理。将详细的 `.memgraph` 命令行所有权/增长分析以及 ETTrace 工作路由到其专注的技能。

## 内容

- [LLDB 调试](#lldb-debugging)
- [内存调试](#memory-debugging)
- [卡顿诊断](#hang-diagnostics)
- [构建失败紧急处理](#build-failure-triage)
- [Instruments 概述](#instruments-overview)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## LLDB 调试

从一个小而可重复的工作流程开始：

1. 在 Debug 构建中重现，并在最窄的有用断点处停止。
2. 不执行代码的情况下检查局部变量，然后捕获当前堆栈。
3. 移动到相关的帧或线程并验证失败状态。
4. 只有当不良转换仍然不清楚时才添加条件或监视点。

```text
(lldb) br set -f ViewModel.swift -l 42     # 在文件和行处停止
(lldb) v myLocal                           # 不执行代码的情况下检查
(lldb) po myObject                         # 当需要时使用 debugDescription
(lldb) bt all                              # 捕获每个线程的回溯
(lldb) frame select 3                      # 检查相关的帧
(lldb) br modify 1 -c "count > 10"         # 窄化嘈杂的断点
(lldb) w set v self.score                  # 在意外的写入时停止
```

当您只需要局部变量的值时，使用 `v` 而不是 `po` —— 它不会执行代码并且不能触发副作用。表达式求值可能会执行或改变程序状态，硬件监视点很少，因此要谨慎使用。

加载 [参考资料/lldb-patterns.md](references/lldb-patterns.md) 获取完整的检查、断点/日志点、表达式、监视点、线程导航和符号断点命令表。

## 内存调试

### 内存图形调试器工作流程

1. 在 Debug 配置下运行应用程序。
2. 重现可疑的内存泄漏（导航到屏幕，然后返回）。
3. 在 Xcode 的调试栏中点击 **内存图形** 按钮。
4. 查找紫色的警告图标——这些图标表示泄漏的对象。
5. 选择一个泄漏的对象以查看其引用图形和回溯。

在运行之前启用 **Malloc 堆栈日志记录**（方案 > 诊断），以便内存图形显示分配回溯。

### 常见的循环引用模式

**闭包强引用 self：**

```swift
// 泄漏——闭包持有对 self 的强引用
class ProfileViewModel {
    var onUpdate: (() -> Void)?

    func startObserving() {
        onUpdate = {
            self.refresh()  // 对 self 的强引用
        }
    }
}

// 修复——使用 [weak self]
func startObserving() {
    onUpdate = { [weak self] in
        self?.refresh()
    }
}
```

**强代理引用：**

```swift
// 泄漏——强代理创建循环
protocol DataDelegate: AnyObject {
    func didUpdate()
}

class DataManager {
    var delegate: DataDelegate?  // 应该是弱引用
}

// 修复——弱代理
class DataManager {
    weak var delegate: DataDelegate?
}
```

**定时器保留目标：**

```swift
// 泄漏——Timer.scheduledTimer 保留其目标
timer = Timer.scheduledTimer(
    timeInterval: 1.0, target: self,
    selector: #selector(tick), userInfo: nil, repeats: true
)

// 修复——使用基于闭包的 API 并使用 [weak self]
timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
    self?.tick()
}
```

### Instruments：分配和泄漏

- **分配模板**：跟踪内存随时间增长。使用“标记生成”功能来隔离在用户操作之间（例如，打开/关闭屏幕）创建的分配。
- **泄漏模板**：检测泄漏的分配，包括进程无法再访问的隔离循环引用。与分配一起运行以获得完整图景。
- 按应用程序的模块名称过滤以排除系统分配。

对于泄漏或内存增长紧急处理，搭配使用这些工具：在重现步骤之前和之后使用分配的 **标记生成** 来证明保留的增长，然后使用内存图形调试器检查对象所有权并使用 Malloc 堆栈日志记录恢复分配调用堆栈。

### Malloc 堆栈日志记录

在方案 > 运行 > 诊断 > Malloc 堆栈日志记录中启用。这将记录分配回溯，以便内存图形调试器、分配工具和导出的 `.memgraph` 文件可以显示对象创建的位置。

```bash
# 从 Xcode 或 Instruments 检查导出的内存图形
leaks MyApp.memgraph
```

## 卡顿诊断

### 识别主线程卡顿

对于离散交互，延迟小于 100 毫秒通常不太明显。Apple 开发者工具通常报告主运行循环繁忙时间超过 250 毫秒，但报告阈值不是产品目标：几百毫秒仍然可能感觉无响应。常见的检测工具：

- **线程检查器**（Xcode 诊断）：警告非主线程的 UI 调用
- **线程性能检查器**：在调试时报告优先级反转
- **设备上的卡顿检测**：开发者设置报告设备使用中的卡顿
- **时间分析器 / CPU 分析器 / Hitches**：分析可重现的卡顿
- **os_signpost** 和 `OSSignposter`：为 Instruments 标记间隔
- **MetricKit** 卡顿诊断：生产环境卡顿检测（见 `HangDiagnostic` 和 iOS 26 兼容性 `metrickit` 技能）

```swift
import os

let signposter = OSSignposter(subsystem: "com.example.app", category: "DataLoad")

func loadData() async {
    let state = signposter.beginInterval("loadData")
    let result = await fetchFromNetwork()
    signposter.endInterval("loadData", state)
    process(result)
}
```

### 使用时间分析器

1. 产品 > 分析（Cmd+I）以启动 Instruments。
2. 选择 **时间分析器** 模板。
3. 在重现慢交互时记录。
4. 关注主线程——按“权重”排序以找到热点路径。
5. 检查“隐藏系统库”以仅查看您的代码。
6. 双击一个重帧以跳转到源代码。

### 常见卡顿原因

| 原因 | 症状 | 修复 |
|-------|---------|-----|
| 主线程上的同步 I/O | 网络/文件读取阻塞 UI | 移动到 `Task { }` 或后台协程 |
| 锁竞争 | 主线程等待后台工作持有的锁 | 使用协程或减少锁范围 |
| 布局过度处理 | 重复的 `layoutSubviews` 调用 | 批量布局更改，避免强制布局 |
| 解析大型 JSON | 数据加载期间 UI 冻结 | 在后台线程解析 |
| 同步图像解码 | 图像密集型列表的滚动卡顿 | 使用 `AsyncImage` 或在主线程外解码 |

## 构建失败紧急处理

### 读取编译器诊断

- 从 **第一个** 错误开始——后续错误通常是级联的。
- 在构建日志中搜索错误代码（例如，`error: cannot convert`）。
- 使用报告导航器（Cmd+9）查看带有时间戳的完整构建日志。

### SPM 依赖解析

```text
# 常见：版本冲突
error: Dependencies could not be resolved because root depends on 'Package' 1.0.0..<2.0.0

# 修复：检查 Package.resolved 并更新版本范围
# 如有需要重置包缓存：
rm -rf ~/Library/Caches/org.swift.swiftpm
rm -rf .build
swift package resolve
```

### 模块未找到/链接器错误

| 错误 | 检查 |
|-------|-------|
| `No such module 'Foo'` | 目标成员资格、导入路径、框架搜索路径 |
| `Undefined symbol` | 链接阶段缺少框架、错误的架构 |
| `duplicate symbol` | 两个目标定义相同符号；检查 ObjC 命名冲突 |

首先检查的构建设置：
- `FRAMEWORK_SEARCH_PATHS`
- `OTHER_LDFLAGS`
- `SWIFT_INCLUDE_PATHS`
- `BUILD_LIBRARY_FOR_DISTRIBUTION`（用于 XCFrameworks）

## Instruments 概述

### 模板选择指南

| 模板 | 使用场景 |
|----------|----------|
| **时间分析器** | CPU 过高、UI 感觉慢、需要找到热点代码路径 |
| **分配** | 内存随时间增长、需要跟踪对象生命周期 |
| **泄漏** | 疑似循环引用或遗弃对象 |
| **网络** | 检查 HTTP 请求/响应时间和有效负载 |
| **SwiftUI** | 分析视图体评估和更新频率 |
| **动画卡顿 / Core Animation Instruments** | 帧丢失、卡顿、混合和提交/渲染工作 |
| **电源分析器** | 电池消耗、热压力、后台能量影响 |
| **文件活动** | 过度磁盘 I/O、慢速文件操作 |
| **系统跟踪** | 线程调度、系统调用、虚拟内存故障 |

### xctrace CLI 用于 CI 分析

```bash
# 从命令行记录跟踪
xcrun xctrace record --device "My iPhone" \
    --template "Time Profiler" \
    --instrument "Allocations" \
    --output profile.trace \
    --launch -- /path/to/MyApp.app

# 将跟踪数据导出为 XML 以进行自动分析
xcrun xctrace export --input profile.trace --xpath '/trace-toc/run/data/table'

# 列出可用的模板
xcrun xctrace list templates

# 列出连接的设备
xcrun xctrace list devices
```

每个记录使用一个 `--template`；使用 `--instrument` 添加额外的仪器。在 CI 管道中使用 `xctrace` 自动捕获性能回归。比较构建之间的导出指标。

## 常见错误

### 不要：使用 print() 进行调试而不是 os.Logger

使用 `Logger` 进行级别、隐私元数据和子系统/类别过滤；`.debug` 仍然保存在内存中，并且在发布构建中不会持久化。

```swift
// 错误——无结构化且无法按子系统/类别过滤
print("user tapped button, state: \(viewModel.state)")
print("network response: \(data)")

// 正确——结构化日志记录使用 Logger
import os

let logger = Logger(subsystem: "com.example.app", category: "UI")

logger.debug("Button tapped, state: \(viewModel.state, privacy: .public)")
logger.info("Network response received, bytes: \(data.count)")
```

### 不要：在内存调试之前忘记启用 Malloc 堆栈日志记录

```swift
// 错误——在打开内存图形之前未启用 Malloc 堆栈日志记录
// 结果：可见泄漏对象但没有分配回溯

// 正确——在运行之前启用：
// 方案 > 运行 > 诊断 > 勾选 "Malloc 堆栈日志记录: 所有分配"
// 然后运行，重现泄漏，并打开内存图形
```

### 不要：在调试优化代码时期望完整的变量可见性

```swift
// 错误——使用 Debug 构建进行调试，使用 Release 构建进行调试
// Debug 构建：额外的运行时检查会扭曲性能测量
// Release 构建：变量显示为 "<optimized out>" 在调试器中

// 正确方法：
// 调试：使用 Debug 配置（完整符号，无优化）
// 分析：使用 Release 配置（真实的性能）
```

### 不要：在没有任何条件断点的情况下每次循环迭代都停止

```swift
// 错误——在循环内的行上设置断点，停止 10,000 次
for item in items {
    process(item)  // 在此处断点会停止每个项目
}

// 正确——使用条件断点：
// (lldb) br set -f MyFile.swift -l 42 -c "item.id == targetID"
// 或者在 Xcode 中：右键单击断点 > 编辑 > 添加条件
```

### 不要：忽略 Thread Sanitizer 警告

Thread Sanitizer (TSan) 警告表示可能仅在偶尔崩溃的数据竞争。除非您已隔离工具问题，否则应将它们视为真正的错误。

```swift
// 错误——忽略关于并发访问的 TSan 警告
var cache: [String: Data] = [:]  // 从多个线程访问

// 正确——保护共享可变状态
actor CacheActor {
    var cache: [String: Data] = [:]

    func get(_ key: String) -> Data? { cache[key] }
    func set(_ key: String, _ value: Data) { cache[key] = value }
}
```

启用 TSan：方案 > 运行 > 诊断 > Thread Sanitizer。对于 iOS、iPadOS、tvOS、visionOS 和 watchOS 应用，在模拟器中运行 TSan；Apple 仅为 64 位 macOS 应用文档化设备支持。

## 审查清单

- [ ] 使用 `os.Logger` 而不是 `print()` 进行诊断输出
- [ ] 内存图形调试器在 dismiss/dealloc 流程后检查
- [ ] 委托声明为 `weak var` 以防止循环引用
- [ ] 闭包作为属性存储使用 `[weak self]` 捕获列表
- [ ] 定时器使用基于闭包的 API 并使用 `[weak self]`
- [ ] 在模拟器测试方案中启用 Thread Sanitizer 进行竞争条件诊断
- [ ] 主线程上没有同步 I/O 或重计算
- [ ] 使用 Release 构建运行时间分析器以获取性能基线
- [ ] 构建失败从构建日志中的第一个错误进行紧急处理
- [ ] 使用 `OSSignposter` 进行自定义性能间隔
- [ ] 使用条件断点进行循环/集合调试

## 参考资料

- [日志记录（统一日志系统）](https://sosumi.ai/documentation/os/logging)
- [Logger](https://sosumi.ai/documentation/os/logger)
- [OSSignposter](https://sosumi.ai/documentation/os/ossignposter)
- [从代码生成日志消息](https://sosumi.ai/documentation/os/generating-log-messages-from-your-code)
- [记录性能数据（signposts）](https://sosumi.ai/documentation/os/recording-performance-data)
- [早期诊断内存、线程和崩溃问题](https://sosumi.ai/documentation/xcode/diagnosing-memory-thread-and-crash-issues-early)
- [数据竞争](https://sosumi.ai/documentation/xcode/data-races)
- [减少应用程序的内存使用](https://sosumi.ai/documentation/xcode/reducing-your-app-s-memory-use)
- [使用 Instruments 分析应用程序](https://developer.apple.com/tutorials/instruments)
- [提高应用程序响应性](https://sosumi.ai/documentation/xcode/improving-app-responsiveness)
- [分析应用程序的电池使用情况](https://sosumi.ai/documentation/xcode/analyzing-your-app-s-battery-use)
- [分析已发布应用程序的性能](https://sosumi.ai/documentation/xcode/analyzing-the-performance-of-your-shipping-app)
- LLDB 命令参考：[参考资料/lldb-patterns.md](references/lldb-patterns.md)
- Instruments 模板指南：[参考资料/instruments-guide.md](references/instruments-guide.md)
