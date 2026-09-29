---
name: argent-device-interact
description: 使用argent MCP工具与iOS模拟器、Android模拟器或Chromium（CDP）应用进行交互。适用于点击UI元素、执行手势、滚动/滑动、输入文本、按下硬件按钮、启动应用、打开URL、截屏、等待元素出现或消失，或检查交互后的可见应用状态。不适用于TV目标。
---

## 统一工具界面

以下所有交互工具都接受一个 `udid` 参数，并根据其形状自动调度 iOS 或 Android（UUID → iOS 模拟器，`chromium-cdp-<端口>` → Chromium (CDP) 应用，其他任何东西 → Android adb 序列）。您在所有平台上都使用相同的工具名称。

**Chromium (CDP) 应用** = 一个 Electron 应用程序或一个暴露了 Chrome DevTools 协议端点的 Chromium 家族浏览器（Chrome/Brave/Edge）。相同的 describe/tap/keyboard/screenshot 界面驱动它，但滚动、标签页、cookie 和存储不同——**在驱动 `chromium` 目标之前，请阅读 `references/chromium.md`。**

## 1. 开始前

如果您将模拟器任务委托给子代理，请确保它们具有 MCP 权限。

使用 `list-devices` 获取目标 ID。结果会带有 `platform` 标签（`ios`、`android` 或 `chromium`）；已启动/就绪的设备会首先出现。选择与您需要的平台匹配的第一个条目——如果没有就绪的设备，请使用 `udid`（iOS）、`avdName`（Android）或 `electronAppPath`（作为 `chromium` 设备启动 Electron 应用程序）。一个已经使用 CDP 端口运行的 Chromium 浏览器会直接显示——不需要 `boot-device`。有关完整设置流程，请参阅 `argent-ios-simulator-setup` / `argent-android-emulator-setup`。

**在首次使用前加载工具模式。** 手势工具（`gesture-tap`、`gesture-swipe`、`gesture-pinch`、`gesture-rotate`、`gesture-custom`）可能会延迟——它们的参数模式只有在获取时才会加载。始终使用 ToolSearch 在调用任何它们之前加载您计划使用的所有手势工具的模式**。如果您跳过这一步，参数可能会被强制转换为字符串而不是数字，从而导致验证错误。

## 2. 最佳实践

1. **在点击之前，始终参考您的 `argent.md` 规则中的 `tapping_rule`。**
2. 在执行交互之前，考虑它们是否可以**按顺序调度**——更多内容请参阅 `run-sequence`。
3. **使用 `gesture-swipe` 进行列表/滚动**，而不是 `gesture-custom`，除非您需要非线性移动。在 Chromium 上使用 `gesture-scroll` 而不是 `gesture-swipe`——`gesture-swipe` 仅支持触摸。考虑您是否需要多次滑动，如果是，请使用 `run-sequence`。当滑动应该在结束前减速以实现精确移动时，传递 `momentum: false`。
4. **在键入之前点击文本字段**，然后使用 `keyboard` 输入文本。
5. **坐标是标准化的**——始终为 0.0–1.0，而不是像素。
6. **对于应用导航，使用每次操作后返回的元素树**（`--- Elements after action (describe) ---`）；仅在当前屏幕没有新鲜树可用时调用 `describe`。它适用于任何屏幕而无需重新启动应用。除非树未能暴露一个可靠的导航目标，否则不要从常规应用屏幕的截图像素进行导航。仅在您需要应用范围的 UIKit 属性（`accessibilityIdentifier`、`viewClassName`）时使用 `native-describe-screen`。

## 3. 打开应用

**切勿通过点击主屏幕图标导航到应用。** 使用 `launch-app` 或 `open-url`——它们是即时且可靠的。

### launch-app — 通过 bundle ID

```json
{ "udid": "<UDID>", "bundleId": "com.apple.MobileSMS" }
```

常见 ID：`com.apple.MobileSMS`（信息）、`com.apple.mobilesafari`（Safari）、`com.apple.Preferences`（设置）、`com.apple.Maps`、`com.apple.Photos`、`com.apple.mobilemail`、`com.apple.mobilenotes`、`com.apple.MobileAddressBook`（联系人）

### open-url — 通过 URL 方案

```json
{ "udid": "<UDID>", "url": "messages://" }
```

常见方案：`messages://`、`settings://`、`maps://?q=<query>`、`tel://<number>`、`mailto:<address>`、`https://...`（Safari）

## 4. 选择正确的工具

| 操作            | 工具                | 备注                                                             |
| ----------------- | ------------------- | ----------------------------------------------------------------- |
| 多个操作        | `run-sequence`      | 在一次调用中批量执行步骤（无需中间截图）             |
| 打开应用       | `launch-app`        | **始终——切勿点击主屏幕图标**                          |
| 重新启动应用    | `restart-app`       | 通过 bundle ID 终止并重新启动                               |
| 打开 URL/方案   | `open-url`          | 网页、深度链接、URL 方案                                |
| 单击            | `gesture-tap`       | 按钮、链接、复选框                                        |
| 滚动/滑动      | `gesture-swipe`     | 直线滚动或滑动                                     |
| 滚动 (Chromium) | `gesture-scroll`    | 基于滚轮；delta 是窗口分数，正的 deltaY = 向下  |
| 拖动 (Chromium) | `gesture-drag`      | 滑块、拖放、文本选择                            |
| 长按            | `gesture-custom`    | 上下文菜单、拖动开始                                         |
| 拖放            | `gesture-custom`    | 复杂的拖动交互                                         |
| 捏合/缩放        | `gesture-pinch`     | 两指捏合，自动插值                          |
| 旋转            | `gesture-rotate`    | 两指旋转，自动插值                       |
| 自定义手势    | `gesture-custom`    | 任意的触摸序列，可选插值                 |
| 硬件键          | `button`            | 主屏幕、返回、电源、音量、应用切换、actionButton                |
| 输入文本         | `keyboard`          | 每个平台。每次调用文本或一个命名键，切勿两者兼有        |
| 粘贴文本        | `paste`             | 仅在用户会粘贴的地方（OTP 码、长链接）。模拟器/模拟器仅 |
| 旋转设备         | `rotate`            | 方向变化                                               |
| 折叠设备         | `fold`              | 可折叠 iOS 模拟器：关闭 / 半开 / 打开，或一个角度    |
| 摇动设备         | `shake`             | 摇动处理器（模拟器/模拟器仅），撤销键入提示，RN 开发菜单    |
| 等待 UI         | `await-ui-element`  | 阻塞直到元素可见/隐藏/存在/包含文本     |
| 等待空闲         | `await-screen-idle` | 阻塞直到非空屏幕树停止变化                |

## 5. 查找点击目标

**重要。** 在执行操作后移动到不同屏幕或不知道组件的坐标时，**始终**执行正确的发现。

| 应用类型                          | 发现工具            | 它返回的内容                                                                                                                                                                                                                                     |
| --------------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 目标应用发现              | `describe`                | 当前设备屏幕的可访问性元素树（iOS AX-service、Android uiautomator 或 Chromium DOM 遍历器）带有标准化框架坐标。适用于任何应用、系统对话框和主屏幕——无需应用重新启动或 `bundleId` 要求 |
| React Native                      | `debugger-component-tree` | React 组件树，包含名称、文本、testID 和（tap: x,y）                                                                                                                                                                                       |
| 应用范围的本地                 | `native-describe-screen`  | 低级应用范围的可访问性元素，带有标准化和原始坐标；需要 `bundleId`                                                                                                                                                |
| 权限 / 系统模态覆盖             | `describe`                | `describe` 自动检测系统对话框并返回带有点击坐标的对话框按钮。如果 `describe` 未暴露控件，则仅当 `describe` 无法可靠地检查当前 UI 时才回退到 `screenshot`                                                                          |
| 最终视觉回退             | `screenshot`              | 仅当发现工具无法可靠地检查当前 UI 时使用。不要从截图推导出常规的应用内导航目标                                                                                                              |

在您已经有一个候选点后，指向后续的本地诊断：

- `native-user-interactable-view-at-point`: 在已知的原始 iOS 点上会接收触摸的最深层本地视图；需要 `bundleId`
- `native-view-at-point`: 在已知的原始 iOS 点上最深的可见本地视图；需要 `bundleId`

### 如果 `describe` 工具失败

阅读确切的错误并选择与它匹配的操作：

- 错误提到 `ax-service` 不可用或守护进程启动失败：
  ax-service 守护进程无法启动。检查模拟器是否已启动。使用 `screenshot` 作为临时回退，或者如果应用注入了本地开发工具，则使用 `native-describe-screen` 并带有显式的 `bundleId`。
- `describe` 返回一个空元素列表：
  屏幕可能为空、正在加载或显示没有可访问性标签的内容。使用 `screenshot` 查看可见内容，然后在内容加载后重试。
- `describe` 成功但不足以 React Native 应用：
  使用 `debugger-component-tree` 下一步。
- 您需要应用范围的检查，带有完整的 UIKit 属性（`accessibilityIdentifier`、`viewClassName`）：
  使用带有显式 `bundleId` 的 `native-describe-screen`。这需要本地开发工具（dylib）注入。
- 您已经有一个候选点，并希望确认实际会接收触摸：
  使用 `native-user-interactable-view-at-point`。当您想要视觉最深视图而不是命中测试目标时，使用 `native-view-at-point`。

## 6. 工具使用

### gesture-tap — 在一个点单击

```json
{ "udid": "<UDID>", "x": 0.5, "y": 0.5 }
```

坐标：`0.0` = 左/上，`1.0` = 右/下。

在 React Native 应用程序中靠近屏幕底部的位置单击之前，请检查“打开调试器以查看警告”横幅是否可见——点击它们会中断调试器连接。如果存在，请使用 X 图标关闭它们。

### gesture-swipe — 直线手势

```json
{ "udid": "<UDID>", "fromX": 0.5, "fromY": 0.7, "toX": 0.5, "toY": 0.3 }
```

向上滑动（`fromY > toY`）= 向下滚动内容。默认持续时间：300ms。可选：`"durationMs": 500` 用于更慢的滑动。

`"momentum"` 默认为 `true`（自然的甩动滑动）。传递 `"momentum": false` 用于无动力的滑动：手指在结束点减速，几乎没有甩动。它需要 `durationMs` 至少为 150，低于此值将被拒绝。

### gesture-pinch — 两指捏合

```json
{ "udid": "<UDID>", "centerX": 0.5, "centerY": 0.5, "startDistance": 0.2, "endDistance": 0.6 }
```

所有值都是标准化的 0.0–1.0（屏幕的分数，而不是像素）——与其他所有手势工具相同。`startDistance: 0.2` 表示手指开始时屏幕间隔为 20%；`endDistance: 0.6` 表示它们结束时屏幕间隔为 60%。`startDistance < endDistance` = 捏出（放大）。`startDistance > endDistance` = 捏入（缩小）。默认值：`angle: 0`（水平），`durationMs: 300`。可选：`"angle": 90` 用于垂直轴，`"durationMs": 500` 用于更慢的捏合，`"endCenterX"`/`"endCenterY"` 允许质心在手势期间漂移到新的中心（省略 = 固定中心）。

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

所有位置和半径都是标准化的 0.0–1.0（屏幕的分数，而不是像素）。`radius: 0.15` 表示每个手指距离中心为屏幕的 15%。`endAngle > startAngle` = 顺时针。默认持续时间：300ms。可选：`"durationMs": 500` 用于更慢的旋转，以及 `"radiusX"`/`"radiusY"`（屏幕宽度/高度的分数；给出两者——它们覆盖 `radius`）与 `radiusX·width = radiusY·height` 用于物理圆形轨道——单个 `radius` 在非方形屏幕上绘制物理椭圆，将轻微的捏合与旋转结合在一起。

### gesture-custom — 自定义触摸序列

对于长按、拖放和其他复杂序列，请参阅 `references/gesture-examples.md`。设置 `"interpolate": 10` 以自动生成关键帧之间的平滑中间 Move 事件。

### button — 硬件按钮按下

```json
{ "udid": "<UDID>", "button": "home" }
```

值：`home`、`back`、`power`、`volumeUp`、`volumeDown`、`appSwitch`、`actionButton`

### keyboard — 输入文本或按下特殊键

```json
{ "udid": "<UDID>", "text": "search query" }
```

一次调用执行一次操作。`text` 和 `key` 互斥，并且同时携带两者的调用将被拒绝，且不会输入任何文本。要键入然后提交，在一个 `run-sequence`（§ 8）中发送两个 `keyboard` 步骤——`{ "text": "search query" }`，然后 `{ "key": "enter" }`。两个单独的调用执行相同的工作，但会多一个往返。

特殊键：`enter`、`escape`、`backspace`、`tab`、`space`、`arrow-up`、`arrow-down`、`arrow-left`、`arrow-right`、`f1`–`f12`。可选：`"delayMs": 100` 在按键之间（默认 50ms）——适用于 iOS 模拟器和 Chromium；它被 Android 手机/平板电脑忽略（通过 `adb input text` 输入，没有每个键的节奏）、Vega 和电视目标。

**输入秘密。** 要在不将明文输入您的上下文、转录或日志的情况下输入凭证，请在 `text` 中使用一个秘密占位符（在 `keyboard`、`paste`、`run-sequence` 键盘步骤和流 `type` 步骤中有效）：

```json
{ "udid": "<UDID>", "text": "{{secret:APP_PASSWORD}}" }
```

值从哪里读取，以及使用占位符的规则——包括不要在之后截图该字段——在 `references/secrets.md` 中。在键入任何凭证之前阅读它。

### paste — 将文本粘贴到聚焦的字段

```json
{ "udid": "<UDID>", "text": "482913" }
```

将 `text` 放在设备的剪贴板（主机剪贴板不受影响）并触发平台的粘贴快捷方式。iOS 模拟器和 Android 模拟器仅；电视目标、物理设备、Chromium 和 Vega 被拒绝。

`paste` 不是更快的 `keyboard`。`keyboard` 像用户一样键入并保持每个文本输入的默认值——一个搜索查询、登录、表单字段。只有在真实用户会粘贴的地方才使用 `paste`：2FA / OTP 码从另一个应用复制、长链接或令牌，或测试应用如何处理粘贴输入。它还携带 `keyboard` 在给定平台上无法键入的内容（多行文本、Android 上的非 ASCII），但这本身不是粘贴的理由——询问用户是否会粘贴。

首先点击字段以便它获得焦点；在没有聚焦字段的情况下粘贴是无声的，就像 `keyboard` 一样。`text` 接受与 `keyboard` 相同的 `{{secret:<NAME>}}` 占位符，具有相同的自动截图跳过。

### rotate — 改变方向

```json
{ "udid": "<UDID>", "orientation": "LandscapeLeft" }
```

值：`Portrait`、`LandscapeLeft`、`LandscapeRight`、`PortraitUpsideDown`

在展开的折叠模拟器上，该值设置设备的方向，而不是 UI。`Portrait` 提供横向 UI。`LandscapeLeft` 提供纵向 UI。

### fold — 折叠或展开折叠模拟器

```json
{ "udid": "<UDID>", "posture": "open" }
```

给出 `posture`（`closed`、`half-open` 或 `open`）或 `angle`（0–180）。不要同时给出两者。

仅在折叠 iOS 模拟器上使用 `fold`。`list-devices` 将其标记为 `foldable: true`，例如 iPhone Duo。其他设备会拒绝此调用。

关闭时，盖板面板显示 UI。半开和全开时，内面板显示 UI。所有工具使用活动面板（显示 UI 的面板），即使在 argent 外部进行折叠也是如此。`fold` 返回时，设备接受输入，因此下一次点击会落在该处。这对于 `run-sequence` 的下一步也适用。

规则：

- 坐标随面板变化。在点击之前，请读取 `fold` 结果中的元素树，或再次运行 `describe`。不要使用折叠前的框架。
- 屏幕截图大小随面板变化。为每个姿势保留一个屏幕截图差异基线。
- 展开时，UI 为横屏。屏幕截图显示 UI 旋转了 90 度，`describe` 框架使用相同的轴，就像在旋转的 iPhone 上一样。
- 在两个不是 0 或 180 度的角度之间折叠可以保持当前面板。结果命名活动面板。要更改面板，请折叠到 `closed` 或 `open`。
- 在手势之间折叠，而不是在手势期间。手势保持在它开始的面板上。
- 如果 argent 找不到活动面板，它将使用盖板面板。工具结果会带有 `warning`，屏幕截图差异摘要会带有 `panel:` 行。拍一张屏幕截图以查看设备显示的内容，然后执行警告给出的检查。

### await-ui-element — 阻塞直到 UI 元素达到状态

**永远不要在循环中轮询 `screenshot`/`describe` 来等待某事。** 使用 `await-ui-element`：它在服务器端阻塞，读取与 `describe` 相同的同一树。它按设计没有裸计时器模式——对于简单的暂停，请使用您自己的 harness sleep。

```json
{ "udid": "<UDID>", "condition": "visible", "selector": { "text": "Continue" } }
```

工具自己的描述包含条件、选择器匹配、默认值和返回形状。它没有告诉你的：

- 一个成功的 `hidden` 检查可能是错误的——它的 `note` 然后说选择器根本匹配不到任何东西。将其视为失败的检查并修复选择器；不要将其理解为“元素消失了”。
- `describe` 打印的合成 `ROOT` 容器永远不会被匹配，所以像 `AXGroup`/`html` 这样的角色不会简单地“匹配屏幕”。
- 为了消除模糊的选择器，将 `role` 固定到文本角色，如 `StaticText`——这将跳过同名的按钮。
- 在 `text` 超时的情况下，`note` 引用了检查实际读取的元素的文本，所以你可以看到它匹配了哪个。

### await-screen-idle — 阻塞直到屏幕停止变化

在启动/导航之后和原始点击之前使用，当早期绘制的元素可能仍在移动时：

```json
{ "udid": "<UDID>", "timeoutMs": 3000, "minStableMs": 250 }
```

在本地 iOS、Android 和 Chromium 上，工具等待非空的 `describe` 树停止变化。只有当 `settled: true` 时才继续。将它与特定目标的 `await-ui-element` 配对；静止并不能识别屏幕。

仅用于实时诊断。不要记录它或将其放入 `run-sequence`。流程使用 `await: { idle: true }`，它还会比较像素。这个实时工具可以在呈现层动画期间返回。

---

## 7. 屏幕截图

仅在以下情况下使用显式的 `screenshot` 工具：

- 您需要任何操作之前的初始屏幕状态。
- 您即将编辑可见 UI 并需要在更改之前进行基线捕获。
- 自动附加的屏幕截图显示过渡或加载帧。
- 您需要额外的上下文。
- 您希望在延迟后检查状态（例如，等待网络响应）。
- 权限对话框、系统警报或原生模态覆盖层可见，而 `describe` 没有暴露可靠的靶标。

当使用 `screenshot` 进行权限或原生模态导航时：

- 不要因为模态可见就切换到基于屏幕截图的导航。在常规应用屏幕和应用内模态中，继续使用 `describe`。
- 优先选择明显居中的警报按钮，如 `Allow`、`OK`、`Don't Allow`、`Not Now` 或 `Continue`。
- 一次点击一个控件，并在做任何其他事情之前检查返回的自动屏幕截图。
- 模态被关闭后，使用 `describe`、`native-describe-screen` 或 `debugger-component-tree` 返回正常发现。

> **优先选择对话框而不是设置工具。** 当应用触发自己的权限提示时，在这里回答它是真实用户的路径——这样做。只有在您无法通过应用到达更改时才使用 `settings-permissions` 工具：在应用请求之前预先授权/拒绝权限，重新启用用户已经拒绝的一个（iOS 不会重新提示），或重置它以便提示重新出现。参见 `argent-settings-permissions` 技能。

可选的旋转参数：`{ "udid": "<UDID>", "rotation": "LandscapeLeft" }`——旋转捕获而不改变模拟器方向。

屏幕截图默认情况下会缩小（原始分辨率的 30%）以减小上下文大小。使用正常缩小的屏幕截图进行 UI 上下文和状态检查。`scale` 接受从 0.01 到 1.0 的值，但不要使用 `scale: 1.0` 作为一般的可读性或点击辅助。

仅在保存用于比较的基线/当前 PNG 文件时使用全分辨率屏幕截图。在这种情况下，抑制图像块，以便全尺寸 PNG 不会被加载到代理上下文中：

```json
{ "udid": "<UDID>", "scale": 1.0, "includeImageInContext": false }
```

对于视觉回归检查、屏幕截图前后比较以及详细的 `screenshot-diff` 参数指导，请使用 `argent-screenshot-diff` 技能。保持此技能专注于设备交互机制和屏幕截图捕获。

### 故障排除

| 问题                 | 解决方案                                                      |
| ----------------------- | ------------------------------------------------------------- |
| 屏幕截图超时    | 通过 `stop-simulator-server` 工具重启模拟器服务器             |
| 没有启动的 iOS 模拟器 | 使用 iOS `udid` 调用 `boot-device`                           |
| 没有准备好的 Android 设备 | 使用 `avdName` 调用 `boot-device`                             |

---

## 8. 使用 `run-sequence` 进行操作序列化

使用 `run-sequence` 将多个交互步骤批量处理为**单个工具调用**。只返回一张屏幕截图——在所有步骤完成后返回。

**不要**在任何步骤依赖于观察先前步骤结果的任何时候使用 `run-sequence`。

### 用例

- "滚动到底部"、"滚动到顶部"、"滚动直到 X" -> 序列化 3-5 次滚动
- 表单交互、"清除并重新输入字段" -> 三次点击以选择所有，然后输入新值
- "提交表单" → 按顺序填写所有字段，然后点击提交
- "返回到 X" → 定义用于导航的点击序列

### `run-sequence` 内部允许的工具

`gesture-tap`, `gesture-swipe`, `gesture-scroll`, `gesture-drag`, `gesture-custom`, `gesture-pinch`, `gesture-rotate`, `button`, `keyboard`, `paste`, `rotate`, `shake`, `fold`, `tv-remote`, `await-ui-element`

`udid` 是共享的——**不要**在每个步骤的 `args` 中包含它。每个步骤的可选 `delayMs`（默认 100ms）。

添加一个 `await-ui-element` 步骤来控制屏幕转换后的后续点击（例如，点击 → 等待下一个屏幕的按钮 → 点击它）。如果其条件在超时之前**没有**满足，则序列化在该步骤停止，并且后续步骤**不会**运行——因此，一个时机不当的点击不能针对一个从未稳定的屏幕。

### 示例

向下滚动三次：

```json
{
  "udid": "<UDID>",
  "steps": [
    { "tool": "gesture-swipe", "args": { "fromX": 0.5, "fromY": 0.7, "toX": 0.5, "toY": 0.3 } },
    { "tool": "gesture-swipe", "args": { "fromX": 0.5, "fromY": 0.7, "toX": 0.5, "toY": 0.3 } },
    { "tool": "gesture-swipe", "args": { "fromX": 0.5, "fromY": 0.7, "toX": 0.5, "toY": 0.3 } }
  ]
}
```

向聚焦的字段中输入并提交。这是混合文本和键的唯一方法，因为一个 `keyboard` 调用不能同时携带两者：

```json
{
  "udid": "<UDID>",
  "steps": [
    { "tool": "keyboard", "args": { "text": "hello world" } },
    { "tool": "keyboard", "args": { "key": "enter" } }
  ]
}
```

点击一个已知按钮，然后向下滚动：

```json
{
  "udid": "<UDID>",
  "steps": [
    { "tool": "gesture-tap", "args": { "x": 0.5, "y": 0.15 } },
    {
      "tool": "gesture-swipe",
      "args": { "fromX": 0.5, "fromY": 0.7, "toX": 0.5, "toY": 0.3 },
      "delayMs": 300
    }
  ]
}
```

点击，等待下一个屏幕，然后对其采取行动——`await-ui-element` 步骤**控制**了它之后的点击：

```json
{
  "udid": "<UDID>",
  "steps": [
    { "tool": "gesture-tap", "args": { "x": 0.5, "y": 0.9 } },
    {
      "tool": "await-ui-element",
      "args": { "condition": "visible", "selector": { "text": "Continue" } }
    },
    { "tool": "gesture-tap", "args": { "x": 0.5, "y": 0.5 } }
  ]
}
```

当步骤依赖于屏幕转换时，优先选择这个而不是固定的 `delayMs`：它适应实际加载时间，如果条件在超时之前没有满足，序列化**在那里停止**，以便下一个点击不能针对一个从未稳定的屏幕。

在第一个错误（或未满足的 `await-ui-element` 条件）处停止并返回部分结果。

---

## 9. 平台特定说明

### Android

- **Metro reachability**：在 RN 应用启动之前，在设备上运行 `adb reverse tcp:8081 tcp:8081`，否则 Metro 将无法从设备访问。参见 `argent-metro-debugger` 以获取完整工作流程。如果设备重新启动，请重新运行。
- **首次启动权限提示**：Android 上的 `reinstall-app` 总是使用 `-g` 安装，因此运行时权限在首次启动时预先授予——无需传递标志。
- **锁定屏幕/安全表面**：如果 `describe` 无法捕获（锁屏、DRM、Play Integrity），则会抛出一个清晰的错误。解锁设备或回退到 `screenshot`。
- **APK 与 `.app` 在 `reinstall-app` 中**：在 Android 上传递 `.apk` 绝对路径；在 iOS 上传递 `.app` 目录。

### Chromium

参见 `references/chromium.md` — 标签、Cookie/存储。

### iOS

_(目前还没有收集到 iOS 特有的陷阱——当它们出现时添加)_
