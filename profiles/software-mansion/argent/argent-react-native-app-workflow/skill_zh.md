物理 iPhone (`kind: "device"`): Metro 调试和分析工具会拒绝它。使用模拟器。

## 1. 启动 React Native 应用

### 1.1 探索配置（强制执行 — 首先执行此操作）

**在运行命令之前**，从 `argent-environment-inspector` 子代理结果中读取项目的构建和运行配置。

不要默认使用 `npx react-native start` 或 `npx react-native run-ios`，而首先检查自定义脚本和工作流程。

**手动回退**（如果代理或工具不可用）：读取所有 `package.json` 脚本 — 查找自定义脚本，如 `start:local`、`start:dev`、`ios`、`build:ios`、风味等。自定义脚本优先于默认命令。还要检查 `metro.config.js` 以查找非默认端口或 watchFolders。对于 iOS 构建，优先打开 `.xcworkspace` 而不是 `.xcodeproj`（CocoaPods 生成工作区）。

**如果项目结构复杂，请在继续之前询问用户。**

**记住工作流程**：一旦你发现项目的构建/运行工作流程，将其保存到项目内存中，这样你就不需要每次都重新发现它。

**启动前检查清单**：

- [ ] 存在 `node_modules`（如果不存在：`npm install` 或 `yarn`）
- [ ] 对于 iOS：`ios/Podfile` 存在；如果 `ios/Pods` 缺失或过时，运行 `cd ios && pod install && cd ..`
- [ ] 默认端口上没有冲突的 Metro（见 1.2）

### 1.2 启动 Metro

1. 检查配置中找到的端口上是否已经运行 metro，如果是，则不要启动另一个服务器。参考第 2.1 点。

1. **如果项目存在自定义启动脚本**（例如 `npm run start:local`、`yarn start:dev`），请使用它。如果未定义自定义脚本，则回退到默认命令：

   ```bash
   npx react-native start
   ```

   可选：如果怀疑缓存问题，请使用 `npx react-native start --reset-cache`。

1. **验证 Metro 已准备就绪**：使用 `debugger-status` 工具。它返回 `status` 结果而不是错误：`status: "connected"` 或 `reason: "no_app_connected"` 都表示 Metro 已启动（应用程序尚未连接）；`reason: "metro_not_running"` 表示 Metro 无法访问 — 遵循结果的 `guidance`。

1. **具有风味或自定义配置的项目**：如果存在特定于项目的启动脚本（例如 `npm run start:local`），请使用它，并在运行应用程序之前启动 Metro。

### 1.3 运行应用程序

在**单独**的终端中（Metro 在第一个终端中保持运行）：

**如果项目存在自定义构建/运行脚本**（例如 `npm run ios`、`npm run android`、`yarn ios:debug`），请使用它。只有在未定义自定义脚本的情况下，才回退到以下默认值。

**明确传递目标设备** — 从 `list-devices`（见 `<device_selection_rule>`）中派生：

```bash
npx react-native run-ios --simulator="<name>"        # iOS（或 --udid <UDID>）
npx react-native run-android --deviceId=<adb-serial> # Android
```

**Android 仅限**：安装后，运行 `adb -s <serial> reverse tcp:8081 tcp:8081`，以便模拟器/设备可以访问主机上的 Metro。如果设备重新启动或 adb 停止，请重复此操作。

**代理检查清单**：

- [ ] Metro 已运行并显示“就绪”
- [ ] 从项目根目录运行命令
- [ ] 如果设备尚未启动：使用 iOS `udid` 或 Android `avdName` 使用 `boot-device`。参考 `argent-ios-simulator-setup` / `argent-android-emulator-setup` 技能。
- [ ] Android：`adb -s <serial> reverse tcp:8081 tcp:8081` 已完成。

---

## 2. 确保/调试 Metro

### 2.1 检查现有 Metro

在启动 Metro 之前，避免“端口已在使用”错误。默认检查端口为 :8081，从文档中推断端口：

```bash
lsof -i :PORT
```

- **无输出** → 端口空闲；可以安全启动 Metro。
- **输出 PID** → 另一个进程正在使用该端口。

使用 `debugger-status` 工具检查该端口上的进程是否实际上是 Metro 服务器 — 它返回结构化结果而不是错误。`status: "connected"` 或 `reason: "no_app_connected"` → 该进程是 Metro。`reason: "metro_not_running"` 而 `lsof` 显示有监听器 → 该端口被**非** Metro 的进程占用；结果的 `detail` 字段显示了进程的响应（`Metro at port ... is not running (got: ...)`）。在这种情况下，询问用户是否可以杀死该进程。

要杀死 Metro 进程，请使用 `stop-metro` 工具（需要用户确认）。

### 2.2 确认正确的服务器连接

- **应用程序必须指向与运行 Metro 相同的主机/端口**。默认值：同一台机器，端口 8081。
- **iOS 模拟器**：默认使用 localhost；对于同一台机器的 Metro 无需额外配置。

**验证 Metro 是否可访问**：使用 `debugger-status` 工具。`reason: "metro_not_running"` 表示 Metro 在该端口上未响应 — 启动它（§2.1）；`"no_app_connected"` 表示 Metro 已响应但应用程序尚未连接（§2.3）。任何其他原因：遵循结果的 `guidance`（它本身并不能证明 Metro 已启动）。

### 2.3 重新加载应用程序（确保新捆绑包）

代码或配置更改后，应用程序必须加载新捆绑包：

| 方法      | 如何                                                                                               |
| ----------- | ------------------------------------------------------------------------------------------------- |
| 重新加载工具 | 使用 `debugger-reload-metro` 工具                                                              |
| 重新启动应用程序 | 使用 `restart-app` 工具，或在模拟器中杀死应用程序并运行 `npx react-native run-ios` 再次 |

**代理检查清单**：

- [ ] 只有一个 Metro 进程（端口上没有重复）
- [ ] Metro 就绪后启动应用程序
- [ ] 需要重新加载时：参考 2.3

---

## 3. 构建/安装/重试（React Native & iOS 本地）

### 3.1 构建失败时（例如 xcodebuild 退出代码 65）

**操作顺序（从简单到复杂）**：

1. 清理构建文件夹，然后重试构建命令
2. 清除缓存并重新安装依赖项：重置 Metro 缓存，`watchman watch-del-all`，删除 `node_modules` + 锁文件，`npm install`，然后 `cd ios && rm -rf build Pods Podfile.lock && pod install --repo-update`
3. CocoaPods 问题：`pod deintegrate` 然后 `pod install --repo-update`
4. 在 Xcode 中打开 `ios/*.xcworkspace` 以在报告导航器中查看详细错误

### 3.2 何时询问用户

**在 2-3 次构建或运行失败后，停止并询问用户指导。** 用户可能知道所需的 env 变量、Xcode 版本要求、自定义构建配置、单体仓库特定设置或所需的外部服务。

如果项目结构复杂且正确的构建方法不明显，**尽早询问用户**，而不是猜测。

### 3.3 保存构建工作流程以供以后使用

一旦你发现项目的正确构建/运行工作流程，**将其保存到项目内存中**。捕获：启动 Metro 的命令、构建/运行应用程序的命令以及任何所需的环境设置。

### 3.4 何时重新安装与刷新

| 情况                                             | 操作                                                                                |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------- |
| 仅更改 JS/React                                 | 使用 `debugger-reload-metro` 工具。无需重建。                                         |
| 本地代码或 `pod install` / 项目配置更改            | 重建：`npx react-native run-ios`（Metro 可以保持运行）。                         |
| `node_modules` 或 `package.json` 更改              | `npm install`，然后如果本地依赖项更改，运行 `cd ios && pod install`。然后重建。 |
| 应用程序需要从 .app 路径重新安装                 | 使用 `reinstall-app` 工具并传递 UDID、bundle ID 和 .app 路径。                         |
| 持久的本地构建错误                        | 全部清理 + 重新安装（上述步骤 2）。                                                |

### 3.5 设备控制

| 操作                     | 工具/命令                                                                                                                                                                                             |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 列出设备               | `list-devices` 工具（iOS + Android）                                                                                                                                                                        |
| 启动 iOS 模拟器      | `boot-device` 工具与 `udid`                                                                                                                                                                             |
| 启动 Android 模拟器   | `boot-device` 工具与 `avdName`                                                                                                                                                                          |
| 启动应用程序              | `launch-app` 工具（传递设备 id + bundle id / package name）                                                                                                                                              |
| 重新启动应用程序             | `restart-app` 工具（传递设备 id + bundle id / package name）                                                                                                                                             |
| 打开 URL / 深链接     | `open-url` 工具（传递设备 id + URL）                                                                                                                                                                     |
| 旋转设备              | `rotate` 工具                                                                                                                                                                                              |
| 停止模拟器服务器      | `stop-simulator-server` 工具（iOS UDID 或 Android 序列 — 一个设备）                                                                                                                                     |
| 停止所有模拟器服务器 | `stop-all-simulator-servers` 工具 — 传递 `devices: [...]` 以将拆除范围限制为此会话的设备（未范围化的调用也会拆除其他代理的设备；仅用于机器范围的清理） |

有关完整模拟器设置工作流程，请参阅 `argent-ios-simulator-setup` 技能。

---

## 4. 应用中的运行时问题

### 4.1 查找位置

| 问题类型                      | 工具/在哪里查找                                                                                                                                                                                                                                              |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **JavaScript 错误/日志**      | 使用 `debugger-log-registry` 获取摘要和日志文件路径，然后 `Grep` 搜索。如果它返回 `status: "not_connected"`，则不会返回日志文件 — 遵循其 `guidance` 以首先重新连接。                                                               |
| **React 组件层次结构**     | 使用 `debugger-component-tree` 工具获取文本树，或使用 `debugger-inspect-element` 在特定逻辑像素坐标处（不是标准化 0-1）。                                                                                                                     |
| **应用程序的视觉状态**       | 使用 `screenshot` 工具捕获当前屏幕，但优先使用 `describe` 或 `debugger-component-tree` 进行实际导航和目标发现。如果权限提示或系统拥有的模态覆盖层无法可靠地显示，则回退到 `screenshot`。 |
| **在应用程序中评估 JS**        | 使用 `debugger-evaluate` 工具在应用程序的运行时运行 JavaScript。                                                                                                                                                                                              |
| **本地崩溃/本地堆栈** | `npx react-native log-ios` 或 iOS 模拟器：调试 → 打开系统日志。                                                                                                                                                                                             |
| **构建/运行配置**          | `metro.config.js`、`babel.config.js`、`package.json` 脚本、`ios/Podfile`。                                                                                                                                                                                      |

有关全面的 Metro 调试工作流程（组件检查、控制台日志、JS 评估），请参阅 `argent-metro-debugger` 技能。

### 4.2 JS 控制台日志（日志注册）

日志写入磁盘上的平面日志文件 `~/.argent/tmp/`。使用 **日志注册 → grep** 模式，而不是内联读取日志。

有关完整工作流程、平面条目格式和 grep 示例，请参阅 `argent-metro-debugger` 技能 §5。

### 4.3 默认情况下不要尝试在 React Native 应用程序中使用 DevMenu。

使用 argent 工具。

---

## 5. 测试应用程序

检查 `argent-environment-inspector` 结果中的测试命令。对于具有自动屏幕截图验证的交互式 UI 测试，使用 `argent-test-ui-flow` 技能。

- **单元测试**：在 `package.json` 中查找 Jest（`"test": "jest"`，`jest` 配置）。运行：`npm test` 或 `yarn test`。
- **E2E**：查找 `.detoxrc.js` 或类似配置，或其他 E2E 配置。依赖项：`detox`、`detox-cli`，对于 iOS 通常 `applesimutils`。
- **可见 UI 更改**：使用 `argent-test-ui-flow` 进行手动 QA。对于 `screenshot-diff` 规则和参数，请遵循 `argent-screenshot-diff` 技能。在稳定之前/之后使用它进行屏幕截图以添加有意义的像素可见证据。
- **UI 流程测试**：对于具有自动屏幕截图验证的交互式 UI 测试，请参阅 `argent-test-ui-flow` 技能。

### 5.2 运行测试（典型）

如果用户的意图不明确（运行现有测试、编写新测试或查找缺失的覆盖率），请在继续之前澄清。

- **Jest**：`npm test` 或 `npx jest`。
- **Detox（示例）**：
  - 构建：`detox build --configuration ios.sim.release`（或调试）。
  - 运行：`detox test --configuration ios.sim.release`。
  - 确保模拟器已启动且未被其他进程使用。

### 5.3 代理测试检查清单

- [ ] 读取 `package.json` 和测试配置（Jest、Detox 等）。
- [ ] 如果 E2E：确认模拟器/设备和构建配置。
- [ ] 如果不清楚：澄清是否使用现有工作流程或编写新测试。

---

## 快速参考：工具和命令

| 目标                         | 工具/命令                                                                                                                           |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 检查端口 8081              | `lsof -i :8081`                                                                                                                          |
| 杀死 Metro                   | `stop-metro` 工具                                                                                                                        |
| 启动 Metro                  | `npx react-native start`                                                                                                                 |
| 启动 Metro（重置缓存）    | `npx react-native start --reset-cache`                                                                                                   |
| 运行 iOS 应用                  | `npx react-native run-ios`                                                                                                               |
| 运行 Android 应用              | `npx react-native run-android`                                                                                                           |
| 列出设备                 | `list-devices` 工具（iOS + Android）                                                                                                      |
| 启动设备                | `boot-device` 工具（传递 `udid` 对于 iOS 或 `avdName` 对于 Android）                                                                        |
| 拍摄屏幕截图              | `screenshot` 工具                                                                                                                        |
| 比较可见 UI 更改   | `screenshot-diff` 工具；遵循 `argent-screenshot-diff` 技能以进行基线/当前捕获选择                                   |
| 描述屏幕（a11y 树）  | `describe` 工具用于正常应用程序屏幕和应用程序内模态；仅在权限/系统覆盖层无法可靠地显示时才使用 `screenshot` |
| 读取 JS 控制台日志         | `debugger-log-registry` 工具                                                                                                             |
| 重新加载 JS 捆绑包             | `debugger-reload-metro` 工具                                                                                                             |
| 检查 Metro 状态           | `debugger-status` 工具                                                                                                                   |
| 检查 React 组件树             | `debugger-component-tree` 工具                                                                                                           |
| 在应用程序中运行 JS                | `debugger-evaluate` 工具                                                                                                                 |
| iOS 本地日志              | `npx react-native log-ios`                                                                                                               |
| Android 本地日志          | `npx react-native log-android` 或 `adb -s <serial> logcat`                                                                               |
| 清理 + 重新安装（核弹）  | 见 §3.1 步骤 3                                                                                                                          |

---

## 相关技能

| 技能                           | 何时使用                                                                                                                                              |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `argent-ios-simulator-setup`    | 初始 iOS 模拟器启动和连接设置                                                                                                                                  |
| `argent-android-emulator-setup` | 初始 Android 模拟器启动和连接设置                                                                                                                               |
| `argent-device-interact`        | 点击、滑动、输入、硬件按钮、模拟器/模拟器上的手势                                                                           |
| `argent-metro-debugger`         | JS 运行时 CDP 调试（iOS / Android 上的 Metro；四个移植的工具也驱动 Chromium/CDP 应用程序）：组件检查、控制台日志、JS 评估 |
| `argent-react-native-profiler`  | 分析性能、查找重新渲染问题、CPU 热点                                                                                            |
| `argent-test-ui-flow`           | 具有自动屏幕截图验证的交互式 UI 测试                                                                                                                          |

在运行测试之前询问用户：确认测试套件（单元、E2E 或两者）、是否使用现有 CI 命令，以及他们是否希望您运行现有测试、编写新测试或自行探索测试用例。
