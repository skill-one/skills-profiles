## 1. 前置条件

- **Android SDK Platform Tools** 位于 PATH 环境变量中 — 提供 `adb` 命令。
- **Android 模拟器** 位于 PATH 环境变量中 — 用于启动 AVDs。如果你只使用已运行的模拟器或物理设备，单独使用 `adb` 即可。
- 通过 Android Studio 或 `avdmanager create avd` 创建的 AVD。

使用 `adb version` 和 `emulator -list-avds` 进行验证。

## 2. 配置

1. **查找可用设备** — 调用 `list-devices` 并筛选出 `platform: "android"` 的条目。可用设备 (`state: "device"`) 优先显示。选择第一个 `serial`（例如 `emulator-5554`），除非用户指定了其他设备。
2. **启动设备（如需）** — 如果没有可用的 Android 设备，从同一调用中的 `avds` 列表使用 `boot-device` 并指定 `avdName: <name>`。该工具会透明地选择热启动或冷启动：它会探测 AVD 的 `default_boot` 快照，在可用时在严格的时间限制下恢复它，否则回退到完全冷启动。热路径通常需要 ~30 秒；冷路径需要 2–10 分钟。在任何阶段失败时，该工具会杀死它启动的模拟器进程，因此你的下一次调用将从干净的状态开始。
3. **Metro（用于 React Native）** — 一旦设备启动，运行 `adb -s <serial> reverse tcp:8081 tcp:8081` 以使设备能够从主机访问 Metro。如果设备重启，请重复此操作。

## 3. 使用设备

将 Android 序列号作为 `udid` 传递给统一交互工具 — `gesture-tap`、`gesture-swipe`、`describe`、`screenshot`、`launch-app`、`keyboard` 等。分发将根据 ID 形状自动进行。参考 `argent-device-interact` 以获取平台无关的交互工具，以及该技能底部的 Android 特定注意事项部分。

## 4. 注意事项

- **Android TV / leanback AVDs** 通过完全相同的流程启动（相同的 `boot-device` + `avdName`），但它们是 **基于焦点而非触摸的** — 不要在这些设备上使用 `gesture-tap`/`gesture-swipe`。`list-devices` 会将 leanback 设备标记为 `runtimeKind: "tv"`（通过系统功能列表检测，而非序列号 — TV AVD 的序列号看起来与手机一样）。当你看到 `runtimeKind: "tv"` 时，使用基于焦点的工具 (`describe` / `tv-remote` / `keyboard`) 以及 `argent-tv-interact` 技能（它涵盖 Android TV 以及 Apple TV，包括完整的 TV 设置流程）。
- 序列号是 `adb` 设备 ID。iOS UDIDs 和 Android 序列号不能互换，但你**无需**告知工具哪个平台 — 分发将自动进行。
- Android 上的 `describe` 返回比 iOS 更浅的树形结构（没有 `accessibility-service` 对应物），但涵盖了大多数 tap-target 发现。
- Android 上的 `reinstall-app` 总是使用 `-g` 安装，因此首次启动的运行时权限会预先授予。
- 要停止模拟器，从 shell 运行 `adb -s <serial> emu kill`（干净关闭）。**切勿**使用 `pkill -9`/`kill -9` 杀死 qemu — 强制杀死会留下脏的用户数据镜像，导致冷启动在执行恢复时挂起很长时间（失控写入，`boot_completed` 不会翻转）。如果镜像进入该状态，使用 `-wipe-data` 启动一次以重置它。
