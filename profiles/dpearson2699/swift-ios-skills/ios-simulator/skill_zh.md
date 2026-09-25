# iOS 模拟器

当您需要完整的命令表格、JSON 解析、隐私/状态栏值、Logger 过滤器设置或启动恢复命令时，请加载 [simctl 命令参考](references/simctl-commands.md)。

## 内容

- [设备生命周期](#device-lifecycle)
- [应用安装和启动](#app-install-and-launch)
- [测试工作流](#testing-workflows)
- [截图和视频录制](#screenshot-and-video-recording)
- [日志流](#log-streaming)
- [编译时模拟器检测](#compile-time-simulator-detection)
- [模拟器限制](#simulator-limitations)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考](#references)

## 设备生命周期

### 列出设备和运行时

```bash
# 列出所有可用的模拟器并按运行时分组
xcrun simctl list devices available

# 列出已安装的运行时
xcrun simctl list runtimes

# 仅列出已启动的设备
xcrun simctl list devices booted

# JSON 输出用于脚本
xcrun simctl list -j devices available
```

解析 JSON 输出来以编程方式查找特定设备。有关 `jq` 解析示例，请参阅 [references/simctl-commands.md](references/simctl-commands.md)。

### 创建设备

```bash
# 查找可用的设备类型和运行时
xcrun simctl list devicetypes
xcrun simctl list runtimes

# 创建设备 — 返回新的 UDID
xcrun simctl create "我的测试手机" "iPhone 16 Pro" "com.apple.CoreSimulator.SimRuntime.iOS-18-4"
```

此技能中示例中的设备类型和运行时标识符是说明性的。运行 `simctl list devicetypes` 和 `simctl list runtimes` 以查找您的系统上可用的标识符。

使用返回的 UDID 进行后续命令。

### 启动、关闭、擦除、删除

```bash
# 启动特定设备
xcrun simctl boot <UDID>

# 如果需要，启动并等待设备准备就绪
xcrun simctl bootstatus <UDID> -b

# 关闭正在运行的设备
xcrun simctl shutdown <UDID>

# 工厂重置 — 删除所有数据，保留设备
xcrun simctl erase <UDID>

# 删除特定设备
xcrun simctl delete <UDID>

# 删除当前 Xcode 中不可用的所有设备
xcrun simctl delete unavailable

# 关闭所有设备
xcrun simctl shutdown all
```

当只有一个模拟器运行时，使用 `booted` 作为 UDID 的简写：

```bash
xcrun simctl shutdown booted
```

如果多个模拟器已启动，`booted` 会非确定性地选择其中一个。在运行并行模拟器时，请优先使用明确的 UDID。

在脚本和 CI 中，`xcrun simctl bootstatus <UDID> -b` 是安装、启动、推送或位置命令之前的规范启动和就绪门。

## 应用安装和启动

### 安装应用

```bash
# 首先为模拟器构建
xcodebuild build \
    -scheme MyApp \
    -destination 'platform=iOS Simulator,name=iPhone 16 Pro' \
    -derivedDataPath build/

# 启动并等待 SpringBoard/服务就绪后再安装
xcrun simctl bootstatus <UDID> -b

# 安装 .app 套件
xcrun simctl install <UDID> build/Build/Products/Debug-iphonesimulator/MyApp.app
```

路径必须指向为模拟器架构构建的 `.app` 目录，而不是 `.ipa` 文件。

### 启动和终止

```bash
# 通过 bundle ID 启动
xcrun simctl launch booted com.example.MyApp

# 启动并将 stdout/stderr 流到终端
xcrun simctl launch --console booted com.example.MyApp

# 传递启动参数
xcrun simctl launch booted com.example.MyApp --reset-onboarding -AppleLanguages "(fr)"

# 终止正在运行的应用
xcrun simctl terminate booted com.example.MyApp
```

`--console` 对于调试很有用 — 它将 `print()` 和 `os_log` 输出直接显示在终端中。

### 应用容器路径

```bash
# 应用套件位置
xcrun simctl get_app_container booted com.example.MyApp app

# 数据容器（Documents、Library、tmp）
xcrun simctl get_app_container booted com.example.MyApp data

# 共享应用组容器
xcrun simctl get_app_container booted com.example.MyApp group.com.example.shared
```

## 测试工作流

### 推送通知模拟

创建一个 JSON 负载文件：

```json
{
    "aps": {
        "alert": {
            "title": "新消息",
            "body": "你收到了来自 Alice 的新消息"
        },
        "badge": 3,
        "sound": "default"
    },
    "customKey": "customValue"
}
```

将其发送到模拟器：

```bash
# 从文件发送推送负载
xcrun simctl push booted com.example.MyApp payload.json

# 从标准输入管道负载
echo '{"aps":{"alert":"快速测试"}}' | xcrun simctl push booted com.example.MyApp -
```

此测试本地负载处理和通知 UI，而不是 APNs 交付。

### 位置模拟

```bash
# 设置固定坐标（纬度、经度）
xcrun simctl location booted set 37.3349,-122.0090

# 列出可用的预定义场景
xcrun simctl location booted list

# 运行预定义场景
xcrun simctl location booted run "City Run"

# 跟随自定义命令行航点
xcrun simctl location booted start --speed=15 --interval=1 \
    37.3349,-122.0090 37.3317,-122.0307

# 从标准输入读取航点，每行一个 "lat,lon" 对
printf "37.3349,-122.0090\n37.3317,-122.0307\n" | \
    xcrun simctl location booted start --distance=100 -

# 清除模拟位置
xcrun simctl location booted clear
```

使用 `set` 用于一个坐标，`run` 用于预定义场景名称，`start` 用于自定义航点路线。命令边界很重要：`simctl location run` 接受内置场景名称（例如，"City Run"、"Freeway Drive"），而不是 GPX 文件路径；`simctl location start` 是自定义坐标航点的命令行路径。使用 Xcode 的 Debug > Simulate Location 菜单用于 GPX 路线。

位置模拟会影响已启动设备上使用 Core Location 的所有应用。完成时清除位置，以避免意外的测试结果。

### 隐私权限

```bash
# 授予权限
xcrun simctl privacy booted grant photos com.example.MyApp

# 撤销权限
xcrun simctl privacy booted revoke microphone com.example.MyApp

# 重置应用的权限
xcrun simctl privacy booted reset all com.example.MyApp
```

常见服务名称：`photos`、`microphone`、`contacts`、`calendar`、`reminders`、`location`、`location-always`、`motion`、`siri`。有关完整列表，请参阅 [references/simctl-commands.md](references/simctl-commands.md)。

在 CI 中预先授予权限可避免系统权限对话框阻止自动测试运行，但它可能会掩盖缺少使用描述键。保留所需的 Info.plist 隐私字符串，并仍然测试正常提示流程。

### 深链接和 URL

```bash
# 打开 URL（触发通用链接或自定义 URL 方案）
xcrun simctl openurl booted "https://example.com/product/123"

# 自定义 URL 方案
xcrun simctl openurl booted "myapp://settings/notifications"
```

对于通用链接，必须配置应用关联的域名权限。模拟器使用域的 `apple-app-site-association` 文件。

### 状态栏覆盖

```bash
# 设置干净的状态栏用于截图
xcrun simctl status_bar booted override \
    --time "9:41" \
    --batteryState charged \
    --batteryLevel 100 \
    --cellularMode active \
    --cellularBars 4 \
    --wifiBars 3 \
    --operatorName ""

# 清除所有覆盖
xcrun simctl status_bar booted clear
```

使用状态栏覆盖来生成一致的 App Store 截图。捕获后始终清除覆盖，以避免混淆其他测试。

## 截图和视频录制

```bash
# 捕获截图
xcrun simctl io booted screenshot screenshot.png

# 录制视频（按 Ctrl+C 停止）
xcrun simctl io booted recordVideo recording.mov

# 带有特定显示掩码的截图
xcrun simctl io booted screenshot --mask black screenshot.png
```

`--mask` 选项：`ignored`（默认，无掩码）、`alpha`（透明角落）、`black`（黑色角落）。当捕获显示设备形状的截图时，使用 `alpha` 或 `black`。`alpha` 掩码仅适用于截图 — 视频录制回退到 `black`。

视频录制会持续进行，直到进程收到 SIGINT（Ctrl+C）。只有在停止后才会保存录制 — 使用 SIGKILL 杀死进程会丢失文件。

## 日志流

### 基本日志流

```bash
# 流式传输所有调试级别及以上的日志
xcrun simctl spawn booted log stream --level debug

# 按子系统过滤
xcrun simctl spawn booted log stream --level debug \
    --predicate 'subsystem == "com.example.app"'

# 按子系统和类别过滤
xcrun simctl spawn booted log stream --level debug \
    --predicate 'subsystem == "com.example.app" AND category == "networking"'

# 按进程名称过滤
xcrun simctl spawn booted log stream \
    --predicate 'process == "MyApp"'
```

加载 [Logger 和过滤流](references/simctl-commands.md#logger-and-filtered-streaming)
当定义 `Logger` 子系统/类别并匹配 `log stream` 谓词时。

## 编译时模拟器检测

使用 `#if targetEnvironment(simulator)` 排除在模拟器中无法运行的代码：

```swift
func registerForPush() {
    #if targetEnvironment(simulator)
    logger.info("跳过 APNs 注册 — 在模拟器中运行")
    #else
    UIApplication.shared.registerForRemoteNotifications()
    #endif
}
```

通过环境变量进行运行时检测：

```swift
var isSimulator: Bool {
    ProcessInfo.processInfo.environment["SIMULATOR_DEVICE_NAME"] != nil
}
```

优先使用编译时检查 (`#if targetEnvironment(simulator)`) 而不是运行时检查。编译器完全删除排除的代码，防止因不可用符号导致的链接器错误。

## 模拟器限制

使用此表格作为权威分类。一个受支持的触发器或代理并不建立真实设备的保真度。

| 功能 | 模拟器支持 |
|------|-----------|
| APNs 推送交付 | 否 — 使用 `simctl push` 进行本地模拟 |
| 性能保真度 | 相对而言 — 模拟器不适用于 CPU/处理性能、网络速度、图形/Metal、内存带宽、帧时间、内存压力、Jetsam、着色器正确性或热行为；在硬件上验证性能敏感的工作 |
| Metal GPU 家族一致性 | 部分一致 — 模拟器使用主机 Mac GPU，而不是设备 GPU；某些着色器和限制不同 |
| 摄像头硬件 | 否 — 使用照片库注入或模拟 `AVCaptureSession` |
| 音频输入/麦克风 | 无通用应用音频输入；可以从模拟器菜单激活 Siri |
| 安全区域 | 否 — `kSecAttrTokenIDSecureEnclave` 操作失败 |
| 应用验证 (DCAppAttestService) | 否 — `isSupported` 返回 `false` |
| DockKit 电机控制 | 否 — 无物理配件连接 |
| 加速计/陀螺仪 | 无运动传感器支持；使用真实设备进行运动相关行为 |
| 气压计 | 否 |
| NFC (Core NFC) | 否 |
| 蓝牙 (Core Bluetooth) | 否 — 使用真实设备进行 BLE 测试 |
| CarPlay 显示模拟 | 通过模拟器的外部显示器/CarPlay 选项支持；仍然在车辆或设备设置中验证 |
| Face ID / Touch ID 硬件 | 无硬件 — 在模拟器的 Features > Face ID / Touch ID 菜单中使用 |
| 内存警告、位置变化、手动 iCloud 同步触发 | 通过模拟器菜单或 `simctl` 支持；手动同步可以测试应用回调处理 |
| 自动 iCloud 传播和冲突 | 需要真实账户/设备的硬件，通知触发同步、后台交付、冲突和账户/设备状态差异 |
| 蜂窝网络条件 | 否 — 在 Mac 上使用 Network Link Conditioner |

## 常见错误

### 不要：在脚本中硬编码模拟器 UDID

当模拟器被删除和重新创建时，UDID 会改变。硬编码的值会在其他机器和 CI 中失效。

```bash
# 错误 — 硬编码 UDID
xcrun simctl boot "A1B2C3D4-E5F6-7890-ABCD-EF1234567890"

# 正确 — 通过名称和运行时查找
UDID=$(xcrun simctl list -j devices available | \
    jq -r '.devices["com.apple.CoreSimulator.SimRuntime.iOS-18-4"][] | select(.name == "iPhone 16 Pro") | .udid')
xcrun simctl boot "$UDID"

# 正确 — 当一个模拟器运行时使用 "booted"
xcrun simctl install booted MyApp.app
```

### 不要：在关闭的模拟器上安装或启动

`simctl install` 和 `simctl launch` 需要一个已启动的设备。它们在关闭的设备上会静默失败或显示无帮助的错误。

```bash
# 错误 — 设备未启动
xcrun simctl install <UDID> MyApp.app  # 失败

# 正确 — 如果需要，启动并等待就绪，然后安装
xcrun simctl bootstatus <UDID> -b
xcrun simctl install <UDID> MyApp.app
xcrun simctl launch <UDID> com.example.MyApp
```

### 不要：在 CI 中留下僵尸模拟器运行

每个已启动的模拟器都会消耗内存和 CPU。创建模拟器而不进行清理的 CI 管道会积累僵尸设备。

```bash
# 错误 — CI 脚本创建并启动但从未清理
xcrun simctl create "CI Phone" "iPhone 16 Pro" "com.apple.CoreSimulator.SimRuntime.iOS-18-4"
xcrun simctl boot "$UDID"
# ... 测试运行，管道退出 ...

# 正确 — 在 CI 拆卸过程中始终清理
cleanup() {
    xcrun simctl shutdown all
    xcrun simctl delete "$UDID"
}
trap cleanup EXIT
```

### 不要：在卡住的模拟器上反复尝试启动

卡在“启动中”状态的模拟器不会通过重试 `boot` 来恢复。底层的 CoreSimulator 状态已损坏。

```bash
# 错误 — 在卡住的设备上重试循环
xcrun simctl boot "$UDID"  # "Unable to boot device in current state: Booting"
xcrun simctl boot "$UDID"  # 相同错误，永远

# 正确 — 关闭、擦除并重试
xcrun simctl shutdown "$UDID"
xcrun simctl erase "$UDID"
xcrun simctl boot "$UDID"

# 如果失败，则完全重置 CoreSimulator
xcrun simctl shutdown all
xcrun simctl erase all
# 最后手段：rm -rf ~/Library/Developer/CoreSimulator/Caches
```

## 审查清单

- [ ] 使用明确的设备类型和运行时标识符创建模拟器设备
- [ ] 脚本使用 `booted` 或从 JSON 输出解析的 UDID，而不是硬编码值
- [ ] 在开发过程中通过 `simctl push` 测试推送通知负载
- [ ] 在发布前在真实设备上验证推送通知交付
- [ ] 当需要时，使用固定坐标、预定义场景和自定义航点测试位置模拟
- [ ] 在 CI 中预先授予权限，以避免阻止对话框
- [ ] 在模拟器中不可用的 API 围绕 `#if targetEnvironment(simulator)` 保护
- [ ] 捕获截图后清除状态栏覆盖
- [ ] CI 管道在拆卸中关闭并删除模拟器
- [ ] 使用子系统/类别谓词配置日志流，以便进行有针对性的调试
- [ ] 在调试期间使用应用容器路径检查沙盒数据

## 参考

- [在模拟器或设备上运行您的应用](https://sosumi.ai/documentation/xcode/running-your-app-in-simulator-or-on-a-device)
- [下载和安装附加的 Xcode 组件](https://sosumi.ai/documentation/xcode/installing-additional-simulator-runtimes)
- [在模拟器中测试与在硬件设备上测试](https://sosumi.ai/documentation/xcode/testing-in-simulator-versus-testing-on-hardware-devices)
- [在模拟器中测试复杂的硬件设备场景](https://sosumi.ai/documentation/xcode/testing-complex-hardware-device-scenarios-in-simulator)
- [模拟外部显示器或 CarPlay](https://sosumi.ai/documentation/xcode/simulating-an-external-display-or-carplay)
- simctl 命令参考：[references/simctl-commands.md](references/simctl-commands.md)
