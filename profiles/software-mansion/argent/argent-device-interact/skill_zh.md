## 统一工具界面

以下所有交互工具都接受一个 `udid` 参数，并根据其形状自动调度 iOS 或 Android（UUID → iOS 模拟器，`chromium-cdp-<port>` → Chromium (CDP) 应用，其他任何东西 → Android adb 串行）。你在每个平台上都使用相同的工具名称。

**Chromium (CDP) 应用** = 一个 Electron 应用程序或一个暴露 Chrome DevTools 协议端点的 Chromium 家族浏览器（Chrome/Brave/Edge）。相同的 describe/tap/keyboard/screenshot 界面驱动它，但滚动、标签页、cookie 和存储不同 — **在驱动 `chromium` 目标之前，请先阅读 `references/chromium.md`。**

## 1. 开始之前

如果你将模拟器任务委托给子代理，请确保它们具有 MCP 权限。

使用 `list-devices` 获取目标 ID。结果会标记有 `platform` (`ios`，`android`，或 `chromium`)；已启动/就绪的设备会首先出现。选择与您需要的平台匹配的第一个条目 — 如果没有就绪的，请使用 `udid`（iOS）、`avdName`（Android）或 `electronAppPath`（作为 `chromium` 设备启动 Electron 应用）。一个已经使用 CDP 端口运行的 Chromium 浏览器会直接显示出来 — 不需要 `boot-device`。查看 `argent-ios-simulator-setup` / `argent-android-emulator-setup` 以获取完整设置流程。

**在首次使用前加载工具模式。** Gesture 工具 (`gesture-tap`，`gesture-swipe`，`gesture-pinch`，`gesture-rotate`，`gesture-custom`) 可能会被延迟 — 它们的参数模式只有在获取时才会加载。始终使用 ToolSearch 来加载你计划使用的所有 gesture 工具的模式 **在** 调用它们之前。如果你跳过这一步，参数可能会被强制转换为字符串而不是数字，导致验证错误。

## 2. 最佳实践

1. **在点击之前，始终参考你的 argent.md 规则中的 tapping_rule**。
2. 在执行交互之前，考虑它们是否可以 **顺序调度** - 更多内容请查看 `run-sequence`。
3. **使用 `gesture-swipe` 进行列表/滚动**，而不是 `gesture-custom`，除非你需要非线性移动。在 Chromium 上使用 `gesture-scroll` 代替 — `gesture-swipe` 仅支持触摸。考虑你是否需要多次滑动，如果是，请使用 `run-sequence`。当滑动应该在结束前减速以实现精确移动时，传递 `momentum: false`。
4. **在键入之前，点击文本字段**，然后使用 `keyboard` 输入文本。
5. **坐标是标准化的** — 始终为 0.0–1.0，而不是像素。
6. **对于应用导航，使用每次操作后返回的元素树** (`--- Elements after action (describe) ---`)；只有在当前屏幕没有新鲜树可用时才调用 `describe`。它可以在无需应用重启的任何屏幕上工作。除非树未能暴露一个可靠的导航目标，否则不要从常规应用屏幕的截图像素上进行导航。仅在需要应用范围的 UIKit 属性 (`accessibilityIdentifier`，`viewClassName`) 时使用 `native-describe-screen`。

## 3. 打开应用

**永远不要通过点击主屏幕图标来导航到应用。** 使用 `launch-app` 或 `open-url` — 它们是即时且可靠的。

### launch-app — 通过 bundle ID

```json
{ "udid": "<UDID>", "bundleId": "com.apple.MobileSMS" }
```

常见 ID：`com.apple.MobileSMS`（信息），`com.apple.mobilesafari`（Safari），`com.apple.Preferences`（设置），`com.apple.Maps`，`com.apple.Photos`，`com.apple.mobilemail`，`com.apple.mobilenotes`，`com.apple.MobileAddressBook`（联系人）

### open-url — 通过 URL 方案

```json
{ "udid": "<UDID>", "url": "messages://" }
```

常见方案：`messages://`，`settings://`，`maps://?q=<query>`，`tel://<number>`，`mailto:<address>`，`https://...`（Safari）

## 4. 选择正确的工具

| 操作            | 工具                | 备注                                                             |
| -------------- | ------------------- | ----------------------------------------------------------------- |
| 多个操作        | `run-sequence`      | 在一次调用中批量步骤（无需中间截图）                             |
| 打开应用       | `launch-app`        | **始终 — 永远不要点击主屏幕图标**                              |
| 重启应用       | `restart-app`       | 通过 bundle ID 终止并重新启动                                   |
| 打开 URL/方案   | `open-url`          | 网页，深度链接，URL 方案                                        |
| 单击            | `gesture-tap`       | 按钮，链接，复选框                                                |
| 滚动/滑动      | `gesture-swipe`     | 直线滚动或滑动                                                   |
| 滚动 (Chromium) | `gesture-scroll`    | 基于滚轮；delta 是窗口分数，正的 deltaY = 向下                 |
| 拖动 (Chromium) | `gesture-drag`      | 滑块，拖放，文本选择                                            |
| 长按            | `gesture-custom`    | 上下文菜单，拖动开始                                             |
| 拖放            | `gesture-custom`    | 复杂的拖动交互                                                 |
| 捏合/缩放      | `gesture-pinch`     | 两指捏合，自动插值                                             |
| 旋转            | `gesture-rotate`    | 两指旋转，自动插值                                             |
| 自定义手势      | `gesture-custom`    | 任意的触摸序列，可选插值                                       |
| 硬件键          | `button`            | 主屏幕，返回，电源，音量，应用切换，actionButton                 |
| 输入文本        | `keyboard`          | 每个平台。每次调用文本或一个命名的键，永远不两者兼有            |
| 粘贴文本        | `paste`             | 仅在用户会粘贴的地方（OTP 代码，长链接）。模拟器/模拟器仅限     |
| 旋转设备        | `rotate`            | 方向变化                                                     |
| 摇动设备        | `shake`             | 摇动处理程序（模拟器/模拟器仅限），撤销键入提示，RN 开发菜单    |
| 等待 UI         | `await-ui-element`  | 阻塞直到元素可见/隐藏/存在/包含文本                           |
| 等待空闲        | `await-screen-idle` | 阻塞直到非空屏幕树停止变化                                     |

## 5. 查找点击目标

**重要。** 在执行操作后移动到不同屏幕或不知道组件的坐标时，**始终** 首先执行正确的发现。

| 应用类型                          | 发现工具            | 它返回的内容                                                                                                                                                                                                                                     |
| --------------------------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 目标应用发现                      | `describe`          | 当前设备屏幕的可访问性元素树（iOS AX-service，Android uiautomator，或 Chromium DOM 遍历器）与标准化框架坐标。适用于任何应用，系统对话框和主屏幕 — 无需应用重启或 `bundleId` 要求 |
| React Native                      | `debugger-component-tree` | React 组件树，包含名称、文本、testID，以及（tap: x,y）                                                                                                                                                                                           |
| 应用范围的本地                    | `native-describe-screen`  | 低级应用范围的访问性元素，包含标准化和原始坐标；需要 `bundleId`                                                                                                                                                |
| 权限 / 系统模态覆盖层             | `describe`                | `describe` 自动检测系统对话框并返回带有点击坐标的对话框按钮。如果 `describe` 没有暴露控件，则仅当 `describe` 没有暴露控件时才回退到 `screenshot`                                                                          |
| 最终视觉回退                     | `screenshot`              | 仅当发现工具无法可靠地检查当前 UI 时才使用。不要从截图推导出常规的应用内导航目标                                                                                                              |

在您已经有一个候选点后，指向后续的本地诊断：

- `native-user-interactable-view-at-point`: 在已知的原始 iOS 点上会接收触摸的最深层本地视图；需要 `bundleId`
- `native-view-at-point`: 在已知的原始 iOS 点上最深的可见本地视图；需要 `bundleId`

### 如果 `describe` 工具失败

阅读确切的错误并选择与它匹配的操作：

- 错误提到 `ax-service` 不可用或守护进程启动失败：
  ax-service 守护进程无法启动。检查模拟器是否已启动。使用 `screenshot` 作为临时回退，或者如果应用注入了本地开发工具，则使用 `native-describe-screen` 并显式传递 `bundleId`。
- `describe` 返回一个空元素列表：
  屏幕可能为空，正在加载，或显示没有可访问性标签的内容。使用 `screenshot` 查看可见内容，然后在内容加载后重试。
- `describe` 成功但对于 React Native 应用来说不够详细：
  下一步使用 `debugger-component-tree`。
- 您需要应用范围的检查，具有完整的 UIKit 属性 (`accessibilityIdentifier`，`viewClassName`)：
  使用 `native-describe-screen` 并显式传递 `bundleId`。这需要本地开发工具（dylib）注入。
- 您已经有一个候选点，并希望确认实际接收触摸的内容：
  使用 `native-user-interactable-view-at-point`。当您想要视觉最深层的视图而不是命中测试目标时，使用 `native-view-at-point`。

## 6. 工具使用

### gesture-tap — 在一个点上单击

```json
{ "udid": "<UDID>", "x": 0.5, "y": 0.5 }
```

坐标：`0.0` = 左/上，`1.0` = 右/下。

在 React Native 应用中靠近屏幕底部的位置单击之前，检查“打开调试器以查看警告”横幅是否可见 — 单击它们会中断调试器连接。如果存在，则使用 X 图标关闭它们。

### gesture-swipe — 直线手势

```json
{ "udid": "<UDID>", "fromX": 0.5, "fromY": 0.7, "toX": 0.5, "toY": 0.3 }
```

向上滑动 (`fromY > toY`) = 向下滚动内容。默认持续时间：300ms。可选：`"durationMs": 500` 用于更慢的滑动。

`"momentum"` 默认为 `true`（自然的甩动滑动）。传递 `"momentum": false` 用于无动力的滑动：手指在结束点减速，几乎没有甩动。它需要至少 150ms 的 `durationMs`，低于此值将被拒绝。

### gesture-pinch — 两指捏合

```json
{ "udid": "<UDID>", "centerX": 0.5, "centerY": 0.5, "startDistance": 0.2, "endDistance": 0.6 }
```

所有值都是标准化的 0.0–1.0（屏幕的分数，而不是像素）— 与所有其他手势工具相同。`startDistance: 0.2` 表示手指开始时相距屏幕 20%；`endDistance: 0.6` 表示它们结束时相距屏幕 60%。`startDistance < endDistance` = 捏出（放大）。`startDistance > endDistance` = 捏入（缩小）。默认值：`angle: 0`（水平），`durationMs: 300`。可选：`"angle": 90` 用于垂直轴，`"durationMs": 500` 用于更慢的捏合，`"endCenterX"`/`"endCenterY"` 允许质心在手势过程中漂移到新的中心（省略 = 固定中心）。

### gesture-rotate — 两指旋转

```json
{
  "udid": "<UDID>",
  "centerX": 0.5,
  "centerY": 0.5,
  "radius": 0.15,
  "startAngle": 0,
  "endAngle": 90
}
```

所有位置和半径都是标准化的 0.0–1.0（屏幕的分数，而不是像素）。`radius: 0.15` 表示每个手指距离中心 15% 的屏幕。`endAngle > startAngle` = 顺时针。默认持续时间：300ms。可选：`"durationMs": 500` 用于更慢的旋转，以及 `"radiusX"`/`"radiusY"`（屏幕宽度的分数；给出两者 — 它们覆盖 `radius`）与 `radiusX·width = radiusY·height` 以实现物理圆形轨道 — 单个 `radius` 在非方形屏幕上绘制物理椭圆，将轻微的捏合与旋转结合在一起。

### gesture-custom — 自定义触摸序列

对于长按、拖放和其他复杂序列，请参阅 `references/gesture-examples.md`。设置 `"interpolate": 10` 以自动生成关键帧之间的平滑中间 Move 事件。

### button — 硬件按钮按下

```json
{ "udid": "<UDID>", "button": "home" }
```

值：`home`，`back`，`power`，`volumeUp`，`volumeDown`，`appSwitch`，`actionButton`

### keyboard — 输入文本或按下特殊键

```json
{ "udid": "<UDID>", "text": "search query" }
```

每次调用执行一个操作。`text` 和 `key` 互斥，并且同时携带两者的调用将被拒绝，不会输入任何文本。要键入然后提交，在一个 `run-sequence` 中发送两个 `keyboard` 步骤（§ 8）— `{ "text": "search query" }`，然后 `{ "key": "enter" }`。两个单独的调用做相同的工作，但会多一个往返。

特殊键：`enter`，`escape`，`backspace`，`tab`，`space`，`arrow-up`，`arrow-down`，`arrow-left`，`arrow-right`，`f1`–`f12`。可选：`"delayMs": 100` 在按键之间（默认 50ms） — 应用于 iOS 模拟器和 Chromium；它在 Android 手机/平板上被忽略（通过 `adb input text` 输入，没有每键节奏），在 Vega 上被忽略，在 TV 目标上被忽略。

**输入秘密。** 要输入凭证而不让其明文进入您的上下文、转录或日志，请在 `text` 中使用一个秘密占位符（在 `keyboard`，`paste`，`run-sequence` 键盘步骤和流程 `type` 步骤中有效）：

```json
{ "udid": "<UDID>", "text": "{{secret:APP_PASSWORD}}" }
```

值从哪里读取，以及使用占位符的规则（包括不截图该字段）在 `references/secrets.md` 中。在键入任何凭证之前，请阅读它。

### paste — 将文本粘贴到聚焦的字段

```json
{ "udid": "<UDID>", "text": "482913" }
```

将 `text` 放在设备的剪贴板（主机剪贴板不受影响）并触发平台的粘贴快捷方式。iOS 模拟器和 Android 模拟器仅限；TV 目标，物理设备，Chromium 和 Vega 被拒绝。

`paste` **不是** 更快的 `keyboard`。`keyboard` 像用户一样键入，并且是每个文本输入的默认值 — 搜索查询，登录，表单字段。仅在真实用户会粘贴的地方使用 `paste`：从另一个应用复制的 2FA / OTP 代码，长链接或令牌，或测试应用如何处理粘贴输入。它还携带 `keyboard` 在特定平台上无法键入的内容（多行文本，Android 上的非 ASCII），但这本身不是粘贴的理由 — 询问用户是否会粘贴。

首先点击字段以便它获得焦点；在没有聚焦字段的情况下粘贴是静默无操作的，就像 `keyboard` 一样。`text` 接受与 `keyboard` 相同的 `{{secret:<NAME>}}` 占位符，规则也相同，会自动跳过截图。

### rotate — 改变方向

```json
{ "udid": "<UDID>", "orientation": "LandscapeLeft" }
```

值：`Portrait`，`LandscapeLeft`，`LandscapeRight`，`PortraitUpsideDown`

### await-ui-element — 阻塞直到 UI 元素达到状态

**永远不要在循环中轮询 `screenshot`/`describe` 以等待某事。** 使用 `await-ui-element`：它在服务器端阻塞相同的树 `describe` 读取。它没有裸计时器模式 — 对于简单的暂停，使用您自己的 harness 睡眠。

```json
{ "udid": "<UDID>", "condition": "visible", "selector": { "text": "Continue" } }
```

该工具自己的描述包含条件、选择器匹配、默认值和返回形状。它不会告诉您：

- 一个成功的 `hidden` 检查可能立即成功，但它的 `note` 说选择器根本未匹配任何内容。将其视为失败的检查并修复选择器；不要将其读作“元素消失了”。
- `describe` 打印的合成 `ROOT` 容器永远不会匹配，因此像 `role` 这样的 `AXGroup`/`html` 不会轻易“匹配屏幕”。
- 为了消除松散的选择器歧义，将 `role` 固定到文本角色，如 `StaticText` — 那将跳过同名的按钮。
- 在 `text` 超时的情况下，`note` 引用了检查实际读取的元素的文本，因此您可以看到它落在哪个匹配上。

### await-screen-idle — 阻塞直到屏幕停止变化

在启动/导航后使用，并在原始点击之前使用，当早期绘制的元素可能仍在移动时：

```json
{ "udid": "<UDID>", "timeoutMs": 3000, "minStableMs": 250 }
```

在本地 iOS、Android 和 Chromium 上，该工具等待非空的 `describe` 树停止变化。仅在 `settled: true` 时继续。将其与特定于目标的 `await-ui-element` 配对；静止并不能识别屏幕。

仅用于实时诊断。不要记录它或将其放入 `run-sequence`。流程使用 `await: { idle: true }`，它也比较像素。这个实时工具可以在呈现层动画期间返回。

---

## 7. 截图

仅在以下情况下使用显式的 `screenshot` 工具：

- 您需要在任何操作之前获取初始屏幕状态。
- 您即将编辑可见 UI 并需要在更改之前获取基线捕获。
- 自动附加的截图显示过渡帧或加载帧。
- 您需要额外的上下文。
- 您希望在延迟后检查状态（例如，等待网络响应）。
- 出现权限对话框、系统警报或本地模态覆盖层，并且 `describe` 没有暴露可靠的导航目标。

当使用 `screenshot` 进行权限或本地模态导航时：

- 不要因为模态可见就切换到截图驱动的导航。在常规应用屏幕和应用内模态中，请继续使用 `describe`。
- 优先选择明显的居中警报按钮，如 `Allow`，`OK`，`Don't Allow`，`Not Now`，或 `Continue`。
- 一次点击一个控件，并在做任何其他事情之前检查返回的自动截图。
- 模态关闭后，返回正常的发现方式，使用 `describe`，`native-describe-screen` 或 `debugger-component-tree`。

> **优先选择对话框而不是设置工具。** 当应用触发其自己的权限提示时，在这里回答它是真实用户的路径 — 做到这一点。仅在您无法通过应用到达更改时才使用 `settings-permissions` 工具：在应用请求之前预先授权/拒绝权限，重新启用用户已经拒绝的一个（iOS 不会重新提示），或重置它以使提示重新出现。查看 `argent-settings-permissions` 技能。

可选的旋转参数：`{ "udid": "<UDID>", "rotation": "LandscapeLeft" }` — 旋转捕获而不改变模拟器方向。

截图默认情况下会被缩小（原始分辨率的 30%）以减小上下文大小。使用正常缩小的截图进行 UI 上下文和状态检查。`scale` 接受 0.01 到 1.0 的值，但不要使用 `scale: 1.0` 作为通用可读性或点击辅助。

仅在保存基线/当前 PNG 文件以进行比较时才使用全分辨率截图。在这种情况下，抑制图像块，因此不会将全尺寸 PNG 加载到代理上下文中：

```json
{ "udid": "<UDID>", "scale": 1.0, "includeImageInContext": false }
```

对于视觉回归检查，以及 `screenshot-diff` 参数的详细指导，请使用 `argent-screenshot-diff` 技能。保持此技能专注于设备交互机制和截图捕获。

### 故障排除

| 问题                 | 解决方案                                                      |
| -------------------- | ------------------------------------------------------------- |
| 截图超时            | 使用 `stop-simulator-server` 工具重启模拟器服务器             |
| 没有就绪的 iOS 模拟器 | 使用 iOS `udid` 调用 `boot-device`                           |
| 没有就绪的 Android 设备 | 使用 `avdName` 调用 `boot-device`                             |

---

## 8. 使用 `run-sequence` 进行操作序列化

使用 `run-sequence` 将多个交互步骤批量到 **单个工具调用** 中。只返回一个截图 — 所有步骤完成后返回。

**不要** 在任何步骤依赖于观察先前步骤结果的任何时候使用 `run-sequence`。

### 用例

- “滚动到底部”，“滚动到顶部”，“滚动直到 X” -> 序列 3-5 次滚动
- 表单交互，清除并重新键入字段 -> 三次点击以选择所有，然后键入新值
- “提交表单” → 按顺序填充所有字段，然后点击提交
- “返回到 X” → 定义用于导航的点击序列

### 允许在 `run-sequence` 内部的工具

`gesture-tap`，`gesture-swipe`，`gesture-scroll`，`gesture-drag`，`gesture-custom`，`gesture-pinch`，`gesture-rotate`，`button`，`keyboard`，`paste`，`rotate`，`shake`，`tv-remote`，`await-ui-element`

`udid` 是共享的 — **不要** 在每个步骤的 `args` 中包含它。可选 `delayMs` 每个步骤（默认 100ms）。

添加一个 `await-ui-element` 步骤来控制屏幕转换后的后续点击（例如，点击 → 等待下一个屏幕的按钮 → 点击它）。如果其条件在超时之前**未**满足，则序列将在该步骤停止，并且后续步骤**不会**运行 — 因此，一个时间错误的点击不能针对一个从未就绪的屏幕。

在第一个错误（或未满足的 `await-ui-element` 条件）处停止并返回部分结果。

---

## 9. 平台特定说明

### Android

- **Metro reachability**: 在 RN 应用启动之前，在设备上运行 `adb reverse tcp:8081 tcp:8081`，否则 Metro 将无法从设备访问。查看 `argent-metro-debugger` 以获取完整工作流程。如果设备重启，请重新运行。
- **首次启动权限提示**: Android 上的 `reinstall-app` 始终使用 `-g` 安装，因此首次启动时运行时权限会预先授予 — 无需传递标志。
- **锁定屏幕 / 安全表面**: 如果 `describe` 无法捕获（锁屏，DRM，Play Integrity），则会抛出一个清晰的错误。解锁设备或回退到 `screenshot`。
- **APK vs .app in `reinstall-app`**: 在 Android 上传递 `.apk` 绝对路径；在 iOS 上传递 `.app` 目录。

### Chromium

查看 `references/chromium.md` — 标签页，cookie/storage。

### iOS

_(目前还没有收集 iOS 特有的陷阱 — 随着它们的出现，请添加它们)_
