# 物理iPhone交互

仅适用于物理iPhone。`argent-device-interact` 仍然适用于此处未列出的所有内容。

## 合同

- 观察（Observation）永远不会改变屏幕；变异（mutation）可能会。`describe` 和 `await-ui-element` 在后台目标上失败，而不是将其重新带到前台；`await-screen-idle` 会返回 `settled: false` 而没有任何原因。在 `button home` 后一秒内的第一个 `describe` 可能仍然会返回旧的树；再次描述。手势（Gestures）和 `keyboard` 会将其重新带到前台并返回 `reactivated: true`；在下一步之前重新描述。

- `launch-app`、`open-url` 和 `restart-app` 将应用置于自动化状态；`reinstall-app` 会清除它；工具服务器重启会忘记它：再次启动。

- 每个工具的描述都说明了其自身的硬件限制（命名按键、`gesture-custom` 形状、按钮、边缘滑动、点击次数）。受限制的工具会以 `not supported on ios device` 的形式失败：修复方法在下面列表中，而不是错误信息中。

## 硬件上的工具

- 仅存在以下工具：`list-devices`、`launch-app`、`restart-app`、`reinstall-app`、`open-url`、`describe`、`screenshot`、`screenshot-diff`、`gesture-tap`、`gesture-swipe`、`gesture-custom`、`button`（`home`、`volumeUp`、`volumeDown`、在具有该按钮的型号上的 `actionButton`）、`keyboard`、`await-ui-element`、`await-screen-idle`、`run-sequence`、流程工具、`stop-simulator-server` 和 `stop-all-simulator-servers`（会话结束）。其他所有设备工具都会以 `not supported on ios device` 失败。

- 没有两指手势、`rotate`、`shake`、`paste`、`settings-permissions`、屏幕录制、`debugger-*`、`react-profiler-*`、`native-profiler-*`、`native-*`、`boot-device`：通过点击和拖动驱动应用的缩放和旋转UI，用手移动手机，通过 `keyboard` 输入，在手机的设置中更改权限，并在模拟器上进行调试、分析或录制。

- `gesture-swipe`：`durationMs` 设置拖动速度，而不是时间；`momentum:false` 仅在结束时休息 300 ms，没有阻尼。`open-url` https 会进入 Safari，永远不会进入拥有该链接的应用：传递 `bundleId`。
