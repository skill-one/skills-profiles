## 平台无关性

物理 iPhone (`kind: "device"`): 首先读取 `argent-ios-device-interact`。`launch-app` 之前必须执行；当应用处于后台时 `describe` 会失败。

交互工具名称在 iOS 和 Android 上是相同的 — `gesture-tap`、`gesture-swipe`、`describe`、`screenshot`、`launch-app` 等 — 工具服务器会根据你传递的 `udid` 自动调度（UUID 形式指向 iOS，adb 序列号指向 Android）。

**在测试前，确定要测试的设备。** 调用 `list-devices` 并遵循 `<device_selection_rule>`：优先选择任何平台上的运行设备；

一旦选择平台，每个平台的设置技能将接管：

| 平台   | 设置技能                     | 使用 `list-devices` 找到设备时                                           |
| ------ | --------------------------- | ------------------------------------------------------------------------ |
| iOS    | `argent-ios-simulator-setup` | `boot-device` 使用 `udid`（如果设备未启动）                               |
| Android | `argent-android-emulator-setup` | `boot-device` 使用 `avdName`（如果设备未就绪）                             |

## 1. 工作流

所有交互都通过 argent MCP 工具进行。确保模拟器/模拟器在开始前就绪。

对于修改可见 UI 的实现任务，此工作流也可以作为视觉验收路径。

1. **基线截图**：调用 `screenshot` 查看当前 UI 状态。对于视觉回归比较或 UI 变更验证，在 `scale: 1.0`、`includeImageInContext: false` 下捕获基线，并在编辑前尽可能保留返回的 `path`。
2. **定位目标**：在点击前，使用发现工具获取元素坐标：
   - **React Native 应用**：使用 `debugger-component-tree` — 它返回组件名称和 (tap: x,y) 坐标。这是在任一平台上对 RN 应用的首选工具。要使用它，请解决 `argent-react-native-app-workflow` 技能进行设置；在 Android 上，您还必须运行 `adb -s <serial> reverse tcp:8081 tcp:8081` 以便 Metro 可从设备访问。
   - **标准应用屏幕和内应用模态**：使用 `describe`。在 iOS 上它返回 AX 树（AX 为空时回退到原生开发工具）；在 Android 上它返回与 DescribeNode 形状相同的 uiautomator 树。
   - **权限提示 / 系统模态覆盖**：首先尝试 `describe`。只有在覆盖不可靠地暴露时才回退到 `screenshot`。当应用引发自己的权限对话框时，在此处回答它 — 那是测试的实际流程。要将提示 _移出_ 流（启动前预授/拒、重新启用用户已拒绝的权限或重置以使对话框重新出现），请在设置期间使用 `argent-settings-permissions` 技能，而不是与对话框交互。
   - **回退**：使用 `screenshot` 估计所需组件的位置，然后在操作后立即验证。
3. **交互**：执行操作 (`gesture-tap`、`gesture-swipe`、`keyboard`、`button`、...） — 您将自动收到截图。
4. **验证**：检查返回的截图以获取预期结果。如果它显示加载/过渡状态，优先使用 `await-ui-element`（预期元素 `visible`，或旋转器 `hidden`）阻塞等待其稳定，而不是猜测延迟 — 但仅当您有一个可以信任的 (`text`/`identifier`/`role`) 选择器，该选择器已知屏幕具有或您在先前的 `describe` 中看到时；猜测的只会超时。否则使用固定短等待。根据断言的内容选择证据：
   - **视觉**（布局、间距、颜色、排版、图像/图标渲染、裁剪、溢出、文本渲染）：优先使用步骤 1 捕获的基线与 `screenshot-diff` 进行比较 — 它会暴露自动截图可能遗漏的像素可见变化。只有在没有稳定基线时才回退到对自动截图进行视觉检查。
   - **结构**（导航状态、元素存在、可访问性标签/值、选择、层次结构、路由）：使用 `describe`、`debugger-component-tree` 或 `native-describe-screen` 进行验证。
   - **运行时 / 日志 / 网络**（控制台错误、API 调用、持久化、时间）：使用 `view-network-logs`、`debugger-log-registry`、`debugger-evaluate` 或目标测试进行验证。注意 `debugger-log-registry` 在调试器无法访问时返回 `{ status: "not_connected", reason, guidance }` 并没有日志文件 — 这不是关于应用的证据；遵循其 `guidance` 重新连接，然后重新验证。
   - **混合**：为每个相关类别收集证据。
   - 报告综合判断：预期行为、观察行为、使用的证据以及任何请求视觉差异的阻塞项。
5. **重复** 每个流程步骤。

## 2. 模板

```
目标：测试 [功能名称]

步骤：
1. 分类预期结果：视觉 / 结构 / 运行时日志网络 / 混合 → 选择证据
2. [导航 / 点击 / 输入以到达稳定的可比较起始点] → 验证自动截图
3. screenshot { scale: 1.0, includeImageInContext: false } → 当需要视觉或混合证据进行 diff 时保存基线路径
4. [执行要测试的操作] → 验证自动截图
5. 在请求时或当可比较图像提供有用的视觉证据时使用 screenshot-diff
6. 报告：通过 / 失败，结合适用的视觉、结构、运行时/日志/网络证据
```

## 3. 示例

### 登录流程

```
1. screenshot → 查看登录屏幕
2. gesture-tap { x: 0.5, y: 0.4 }  → 点击邮箱字段
3. keyboard { text: "user@example.com" }
4. gesture-tap { x: 0.5, y: 0.55 } → 点击密码字段
5. keyboard { text: "{{secret:APP_PASSWORD}}" }
6. gesture-tap { x: 0.5, y: 0.7 }  → 点击登录按钮
7. screenshot → 验证主页出现
```

> **凭证**：不要输入明文凭证 — 在 `keyboard` 中使用 `{{secret:<NAME>}}` 占位符，服务器端解析，因此值永远不会进入代理上下文。它来自 `ARGENT_SECRET_<NAME>` 环境变量或项目中的 `.argent/secrets.env` 文件（项目中的 `~/.argent/secrets.env` 或项目中以 `ARGENT_SECRET_` 开头的键在 `.env` / `.env.local` 中）。如果名称未定义，失败会列出可用名称和它检查的每个路径 — 请用户将其添加到其中一个文件（立即生效）而不是将秘密粘贴到对话中。不要编造凭证或将秘密值回显到报告或保存文件中。

### 滚动和导航

```
1. screenshot → 查看顶部的列表
2. gesture-swipe { fromY: 0.7, toY: 0.3 } → 向下滚动
3. gesture-tap 可见位置的项目 → 验证自动截图
4. screenshot → 验证详情视图打开
5. button { button: "back" }
6. screenshot → 验证返回到列表
```

### 视觉行为检查

```
1. 将预期结果分类为视觉或混合。
2. 导航到稳定的起始状态。
3. screenshot { scale: 1.0, includeImageInContext: false } → 保存基线路径。
4. describe / debugger-component-tree → 找到控件并使用其返回的点击坐标。
5. gesture-tap → 执行要测试的视觉行为。
6. screenshot-diff { baselinePath, captureCurrent: true, udid, outputDir } → 检查可见变化或稳定性。
7. describe / debugger-component-tree → 如果相关，验证选中状态、标签、路由或属性。
8. 报告来自预期行为、视觉检查、diff 摘要和结构证据的综合判断。
```

### 等待加载旋转器

```
1. gesture-tap { x: 0.5, y: 0.7 } → 触发获取数据的行为
2. screenshot → 加载旋转器正在显示
3. await-ui-element { condition: hidden, selector: { text: "Loading" } } → 阻塞直到获取完成且旋转器消失
4. describe / screenshot → 验证渲染的内容
```

---

## 4. 恢复模式

- 如果屏幕处于过渡中或正在加载：使用 `await-ui-element` 阻塞直到它稳定（等待目标元素为 `visible`，或旋转器/占位符为 `hidden`），而不是盲目的固定延迟，然后重新检查。只有在没有可靠元素标记过渡时才回退到固定等待 + `screenshot`。
- 如果点击未命中目标：重新运行发现工具 (`describe` / `debugger-component-tree`)，使用新坐标重试一次。
- 如果权限对话框或模态可见：首先重新运行 `describe`。仅在覆盖不可靠地暴露时保持截图驱动导航，然后一旦它被关闭就切换回 `describe` / `debugger-component-tree`。
- 如果在相同坐标处点击失败两次：停止，重新发现，如果元素未找到则报告。
- 如果一个**保存的流程**在 `flow-execute` 回放期间失败（而不是上述实时测试步骤）：遵循 `argent-create-flow` 的 [诊断回放失败](../argent-create-flow/references/reliability-and-recovery.md#diagnose-a-replay-failure) — 分类失败，检查实际屏幕，修复最小的合理单元，然后回放整个流程。

## 小贴士

- **等待 UI，不要轮询。** 当一个步骤需要屏幕先改变时，用 `await-ui-element`（阻塞直到元素 `visible`/`hidden` 或包含 `text`）来控制它，而不是使用固定睡眠的重复 `screenshot` 调用。参见 `argent-device-interact` 的 `await-ui-element` 部分。
- **使用 `gesture-custom` 进行长按** 上下文菜单（800ms 按住）。
- **清晰报告**：说明你预期什么，你看到了什么，以及判断。
- **权限模态**：首先尝试 `describe`。仅作为回退使用 `screenshot`，一次点击一个可见按钮，并在继续前使用返回的截图进行验证。
- **记录以供回放**：如果一个测试流程可能重复，使用 `argent-create-flow` 技能将其记录为 `.yaml` 脚本。这允许您稍后使用单个 `flow-execute` 调用回放整个序列，而不是手动重新运行每个步骤。

## 相关技能

| 技能                              | 使用场景                                              |
| ---------------------------------- | -------------------------------------------------------- |
| `argent-device-interact`           | 点击、滑动、输入的工具使用 (iOS + Android)              |
| `argent-screenshot-diff`           | 视觉回归和 before/after 截图比较                      |
| `argent-ios-simulator-setup`       | 启动和连接 iOS 模拟器                                  |
| `argent-android-emulator-setup`    | 启动和连接 Android 模拟器                             |
| `argent-react-native-app-workflow` | 启动应用、Metro、构建问题                            |
| `argent-metro-debugger`            | 控制台日志、JS 评估、组件检查                        |
| `argent-create-flow`               | 记录测试序列为可回放的流程                          |
