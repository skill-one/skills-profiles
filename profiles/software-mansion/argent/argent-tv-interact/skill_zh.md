# Argent TV (Apple TV + Android TV + Fire TV)

## 关键注意事项

- 电视是**基于焦点而非触控的**。通过 `describe` + `tv-remote` + `keyboard` 来驱动每个交互；切勿使用 `gesture-*` / 坐标点击——它们在任何电视平台上都不适用。
- **在导航前始终使用 `describe`** 以找到光标和目标——切勿从截图猜测焦点。光标是聚焦的元素；在 **Vega** 上，工具包通常将 `focused` 设置为 `false` 并将高亮项标记为 `[selected]`，因此当没有报告 `[focused]` 时，应将 `[selected]` 视为光标。

## 导航循环

1. `describe` — 找到光标和目标（返回聚焦元素 + 所有可聚焦元素，而非点击树）。
2. `tv-remote` — 将焦点移向目标。优先使用 **单个** 调用，路径以 `select` 结尾，例如 `{button:["down","right","select"]}`；从框架中计算行/列来构建路径。
3. 再次使用 `describe` 确认。如果失败，重复。

## 工具

- `describe {udid}` — 聚焦视图：聚焦元素 / `[selected]` 元素 + 带标签和标准化框架的可聚焦元素。在导航前后调用。空树 → 参考各平台说明。
- `tv-remote {udid, button}` — D-pad / 遥控器。`button` 是一个键 **或一个完整路径**（在一个调用中运行）。键：`up`/`down`/`left`/`right`, `select`, `back`, `menu`, `home`, `playPause`, 以及媒体键 `rewind`/`fastForward`/`next`/`previous`/`volumeUp`/`volumeDown`/`mute`。单个：`{button:"down"}`；重复：`{button:"down", repeat:3}`；路径：`{button:["up","right","select"]}`。
- `keyboard {udid, text}` — 在聚焦字段中输入（先用 `tv-remote` 聚焦）。一个调用携带 `text` 或 `key`，不能同时使用——要输入然后按一个键，在一个 `run-sequence` 中发送两个 `keyboard` 步骤。命名 `key` 按压（例如 `{key:"enter"}`）在 Vega 上有效；在 Apple TV / Android TV 上使用 `tv-remote` 移动焦点。
- `launch-app` / `restart-app` / `reinstall-app {udid, bundleId}` — `bundleId` 来自应用清单。Vega `reinstall-app` 需要 `appPath` = 一个 `.vpkg`。
- `screenshot {udid, scale?}` — Apple TV 通过 `xcrun simctl io`（降采样）；Android TV / Vega 主机端通过 `adb` / `screencap`。

## 各平台说明

### Apple TV (tvOS 模拟器)

- 像任何 iOS 模拟器一样启动 (`boot-device`)；AX + HID 守护进程在第一个 `describe` / `tv-remote` 时自动启动（第一个调用可能需要几秒钟）。在第一个 `describe` 之前给 RN bundle 几秒钟来渲染。
- 媒体传输 / 音量键被**拒绝**——模拟器的 HID 守护进程忽略它们（它们在 Android TV / Vega 上工作）。
- 开发版本：`open-url {udid, url:"<scheme>://expo-development-client/?url=http%3A%2F%2F<HOST_IP>%3A8081"}` (`<HOST_IP>` = 你的 Mac 的局域网 IP，在启动器上显示）。

### Android TV (leanback 模拟器)

- 像任何模拟器一样启动 leanback AVD —— 参考 `argent-android-emulator-setup`。
- **`describe` 可能在一个有可见瓦片的屏幕上报告零可聚焦元素**：许多 `react-native-tvos` 屏幕使用 RN 自身的聚焦引擎，对操作系统可访问性树不可见。`describe` 自动回退到完整 UI 树（并在提示中说明）；`tv-remote` 仍然移动焦点，因此盲目驱动 + `screenshot` 确认。
- 开发版本：`adb -s <serial> reverse tcp:8081 tcp:8081`，深度链接 `<pkg>://expo-development-client/?url=http%3A%2F%2F10.0.2.2%3A8081`，用 `adb shell input keyevent KEYCODE_DPAD_CENTER` 关闭第一个 dev-menu（不是 Back —— Back 退出应用）。

### Fire TV (Vega / VVD)

- `list-devices` 显示一个 `serial`（用作 `udid`）和一个 `vvdImage`。`boot-device {vvdImage}`（例如 `"tv"`) 启动单个 SDK 管理的 VVD；如果已运行则跳过。
- **用 `vega virtual-device stop` 在你的 shell 中停止 VVD**。CLI 仅跟踪它在前台启动的 VVD，因此它可能报告“未运行”为通过 `boot-device` 启动的一个；要重启那个，使用 `boot-device {vvdImage, force:true}`（停止然后重启）。
- 空的 `describe` 树 → `restart-app`（自动化工具包在启动时附加），然后重试。输入被忽略 → 在 VVD 中启用开发者模式：`vsm developer-mode enable`。
- 编辑 `node_modules` 对 Release 构建无效——只有 Debug `.vpkg` 构建加载可修补的 JS。
- 性能分析 / 崩溃 → `amazon-devices-buildertools-mcp` 服务器 (`analyze_perfetto_traces`, `get_app_hot_functions`, `symbolicate_acr`)；文档通过其 `search_documentation` 工具获取。

## 常见陷阱

- **`launch-app` / `restart-app` 后立即为空焦点** 是启动/加载窗口——`describe` 内部重试；在冷启动上等待 ~2-3s 并重试。
- 将手机/平板 (`runtimeKind: "mobile"`) udid 传递给 `tv-remote` 会失败，并显示清晰的 "tvOS-only" / "Android-TV-only" 错误——从 `list-devices` 选择电视目标。

## 快速刷新 (开发版本)

需要 Debug 构建加 Metro 运行。argent 仅连接到 Metro——自己启动 Metro 并端口转发（任何平台）。Metro 固定在 **:8081**。

- **Apple TV / Android TV**：使用上述开发版本深度链接；`npm start` 用于 Metro。
- **Vega**：构建/安装 Debug `.vpkg` (`vega device install-app -p <path>`), `npm start`, `vega device start-port-forwarding --port 8081 --forward false`, 然后使用 `vega device launch-app -a <appId>`。确认 `http://localhost:8081/json/list` 显示 `Hermes React Native` 目标；`.tsx` 编辑后热重载。

## JS 运行时调试 (Vega)

一旦相同的 Debug 构建加 Metro 设置就绪，JS 运行时工具在 Vega VVD 上工作：`debugger-connect`, `debugger-status`, `debugger-evaluate`, `debugger-log-registry`（控制台日志），`view-network-logs`, 和 `view-network-request-details`。用 `debugger-status` 验证：当未连接时，它返回状态结果而非错误——`status: "connected"` 表示设置有效；`status: "not_connected"` 携带 `reason` 和 `guidance`（例如 `metro_not_running` → Metro 本身未启动）。Vega 特定：在 `no_app_connected`，检查 `vega device start-port-forwarding` **在**重新启动应用之前——设备→主机转发通常是原因，通用指导无法知道。参考 `argent-metro-debugger` 技能。

Vega 的 React Native 分叉了 RN 0.72 并提供遗留的 Hermes 检查器，因此有三点与 iOS / Android 不同：

- `debugger-component-tree`, `debugger-inspect-element`, `debugger-reload-metro` 和 `react-profiler-*` / `profiler-*` 工具**不受支持**。组件树和检查元素被硬阻止：它们需要 `Runtime.addBinding`，Hermes 承认但从未安装。其余的只是未在遗留检查器上验证。使用 `describe` 查找屏幕结构；由于组件工具被封锁，组件 `file:line` 追踪在 Vega 上无路径。
- `debugger-status` 报告 `isNewDebugger: false`。
- `projectRoot` 为空（RN 0.72 的 Metro 不发送项目根头），因此针对项目根的路径解析返回无位置。
