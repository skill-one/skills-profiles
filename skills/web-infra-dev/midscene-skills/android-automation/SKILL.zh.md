---
name: android-device-automation
description: '使用 Midscene 进行视觉驱动的安卓设备自动化。完全基于截图运行——无需 DOM 或可访问性标签。可交互屏幕上所有可见元素，无论技术栈如何。通过 ADB 使用自然语言命令控制安卓设备。执行点击、滑动、文本输入、应用启动、截图等操作。


  触发关键词：android, phone, mobile app, tap, swipe, install app, open app on phone, android device, mobile automation, adb, launch app, mobile screen, test android app, verify mobile app, QA on phone, check the app on android, test on device, see if the app works on phone, end-to-end test on android, visual verification on mobile


  由 Midscene.js (https://midscenejs.com) 驱动'
---

# 安卓设备自动化

> **关键规则 — 违反将导致工作流程中断：**
>
> 1. **切勿在后台执行场景命令。** 每个命令必须同步运行，以便在决定下一步操作之前读取其输出（尤其是截图）。后台执行会破坏截图-分析-执行循环。
> 2. **一次只运行一个场景命令。** 等待前一个命令完成，读取截图，然后决定下一步操作。切勿将多个命令串联在一起。
> 3. **为每个命令留出足够的时间完成。** 场景命令涉及 AI 推理和屏幕交互，这可能比典型的 shell 命令耗时更长。典型命令大约需要 1 分钟；复杂的 `act` 命令可能需要更长时间。
> 4. **完成自动化任务前始终报告结果。** 完成自动化任务后，你必须主动向用户总结结果——包括发现的关键数据、完成的操作、拍摄的截图以及任何相关发现。切勿在最后一个自动化步骤后默默结束；用户期望在单次交互中获得完整响应。

使用 `npx -y @midscene/android@1` 自动化安卓设备。每个 CLI 命令都直接映射到 MCP 工具——你（AI 代理）作为大脑，根据截图决定要执行哪些操作。

## `act` 能做什么

在安卓的单个 `act` 调用中，Midscene 可以点击、双击、长按、输入、清除文本、任意方向滚动或滑动、下拉刷新、拖拽项目、用两根手指缩放、按键、使用系统导航（如返回、主页或最近应用）等，所有操作都基于当前可见屏幕。

## 前置条件

Midscene 需要具有强大视觉定位能力的模型。必须配置以下环境变量——既可以是系统环境变量，也可以是当前工作目录中的 `.env` 文件（Midscene 会自动加载 `.env`）：

```bash
MIDSCENE_MODEL_API_KEY="your-api-key"
MIDSCENE_MODEL_NAME="model-name"
MIDSCENE_MODEL_BASE_URL="https://..."
MIDSCENE_MODEL_FAMILY="family-identifier"
```

示例：Gemini (Gemini-3-Flash)

```bash
MIDSCENE_MODEL_API_KEY="your-google-api-key"
MIDSCENE_MODEL_NAME="gemini-3-flash"
MIDSCENE_MODEL_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
MIDSCENE_MODEL_FAMILY="gemini"
```

示例：Qwen 3.5

```bash
MIDSCENE_MODEL_API_KEY="your-aliyun-api-key"
MIDSCENE_MODEL_NAME="qwen3.5-plus"
MIDSCENE_MODEL_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
MIDSCENE_MODEL_FAMILY="qwen3.5"
MIDSCENE_MODEL_REASONING_ENABLED="false"
# 如果使用 OpenRouter，设置：
# MIDSCENE_MODEL_API_KEY="your-openrouter-api-key"
# MIDSCENE_MODEL_NAME="qwen/qwen3.5-plus"
# MIDSCENE_MODEL_BASE_URL="https://openrouter.ai/api/v1"
```

示例：豆包 Seed 2.0 Lite

```bash
MIDSCENE_MODEL_API_KEY="your-doubao-api-key"
MIDSCENE_MODEL_NAME="doubao-seed-2-0-lite"
MIDSCENE_MODEL_BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
MIDSCENE_MODEL_FAMILY="doubao-seed"
```

常用模型：豆包 Seed 2.0 Lite、Qwen 3.5、智谱 GLM-4.6V、Gemini-3-Pro、Gemini-3-Flash。

如果未配置模型，请提示用户进行设置。有关支持的提供者，请参阅 [模型配置](https://midscenejs.com/model-common-config)。

## 命令

### 常用安卓 CLI 标志

在创建或使用安卓代理的命令（如 `connect`、`take_screenshot`、`act`、`assert` 和 `tap`）上使用这些标志：

- `--device-id <id>`：从 `adb devices` 选择特定的安卓设备。
- `--use-scrcpy`：启用 scrcpy 加速截图。当正常截图捕获缓慢或不稳定时使用此标志。由于 CLI 调用是无状态的，请在每个需要基于 scrcpy 的截图的安卓 Midscene 命令中传递此标志。

### 连接设备

```bash
npx -y @midscene/android@1 connect
npx -y @midscene/android@1 connect --device-id emulator-5554
npx -y @midscene/android@1 connect --device-id emulator-5554 --use-scrcpy
```

### 启动应用或 URL

当您希望在执行其余任务之前获得确定性起始点时，使用专用启动步骤：

```bash
npx -y @midscene/android@1 launch --uri https://www.ebay.com
npx -y @midscene/android@1 launch --uri com.android.settings
npx -y @midscene/android@1 launch --uri com.android.settings/.Settings
```

### 运行原始安卓 Shell 命令

当任务需要比可见 UI 交互更底层的设备控制时使用此命令：

```bash
npx -y @midscene/android@1 runadbshell --command "dumpsys battery"
```

这会被转发到连接设备的 `adb shell`。在实践中，底层命令是 `adb -s <deviceId> shell dumpsys battery`，并且某些环境可能还会包含默认 ADB 服务器端口，例如 `adb -P 5037 -s <deviceId> shell dumpsys battery`。

### 拍摄截图

```bash
npx -y @midscene/android@1 take_screenshot
npx -y @midscene/android@1 take_screenshot --device-id emulator-5554 --use-scrcpy
```

拍摄截图后，读取保存的图像文件以了解当前屏幕状态，然后再决定下一步操作。

### 执行操作

使用 `act` 与设备交互并获取结果。它内部自主处理所有 UI 交互——点击、输入、滚动、滑动、等待和导航——因此你应该将复杂的高级任务作为一个整体给出，而不是将其拆分为小步骤。用自然语言描述**你想做什么以及期望的效果**：

```bash
# 具体指令
npx -y @midscene/android@1 act --prompt "在搜索框中输入 hello world 并按 Enter"
npx -y @midscene/android@1 act --prompt "长按消息气泡并在弹出菜单中点击 Delete"
npx -y @midscene/android@1 act --device-id emulator-5554 --use-scrcpy --prompt "在搜索框中输入 hello world 并按 Enter"

# 或目标驱动指令
npx -y @midscene/android@1 act --prompt "打开设置并导航到 Wi-Fi 设置，告诉我已连接的网络名称"
```

### 断言当前屏幕状态

使用 `assert` 来验证当前屏幕是否满足自然语言条件。它不执行 UI 操作；它检查可见屏幕状态，并且仅在断言为真时通过。用于验证、QA 检查以及 `act` 后的最终状态验证。

```bash
npx -y @midscene/android@1 assert --prompt "有一个登录按钮可见"
npx -y @midscene/android@1 assert --prompt "设置屏幕显示 Wi-Fi 和蓝牙选项"
npx -y @midscene/android@1 assert --device-id emulator-5554 --prompt "应用显示成功登录消息"
npx -y @midscene/android@1 assert --device-id emulator-5554 --use-scrcpy --prompt "应用显示成功登录消息"
```

默认情况下，失败的断言会抛出 AI 生成的理由。传递 `--message` 以抛出自定义错误消息，这对于在 QA 和 CI 日志中展示预期结果很有用。

```bash
npx -y @midscene/android@1 assert \
  --prompt "订单确认屏幕可见" \
  --message "点击支付后订单应被确认"
```

当断言需要与参考图像（图标、标志、截图）进行比较时，传递 `--image` 用于 URL/路径，`--image-name` 用于其显示名称。每个 `--image` 可以是 http(s) 链接、`data:` URI 或本地文件路径。当需要附加多个图像时，请按匹配顺序重复这两个标志。添加 `--convertHttpImage2Base64 true` 当模型无法直接访问 URL 时。需要 `@midscene/android@1.9.0+`。

```bash
npx -y @midscene/android@1 assert \
  --prompt "可见的应用图标与提供的参考图像匹配" \
  --image "https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png" \
  --image-name "icon" \
  --convertHttpImage2Base64 true

# 或使用本地文件
npx -y @midscene/android@1 assert \
  --prompt "屏幕上的标题与本地截图匹配" \
  --image "./fixtures/header.png" \
  --image-name "header"

# 多个参考图像——按顺序配对 `--image` 和 `--image-name`
npx -y @midscene/android@1 assert \
  --prompt "屏幕显示应用图标和标题" \
  --image "./fixtures/icon.png"   --image-name "icon" \
  --image "./fixtures/header.png" --image-name "header"
```

### 录制并断言瞬时 UI

当要验证的状态可能在当前屏幕断言运行之前消失时（例如 Toast、加载横幅、动画或过渡），使用录制：

```bash
# 终端 1：保持此前台命令运行
npx -y @midscene/android@1 record start \
  --device-id emulator-5554 --use-scrcpy \
  --output ./submission-observation.json

# 终端 2，在终端 1 录制时
npx -y @midscene/android@1 act --device-id emulator-5554 \
  --prompt "点击提交按钮"

# 发送 Ctrl+C 到终端 1 并等待保存路径消息，然后断言
npx -y @midscene/android@1 assert --device-id emulator-5554 \
  --record ./submission-observation.json \
  --prompt "提交期间出现成功 Toast"
```

将目标标志、捕获标志和 `--output` 传递给 `record start`，然后等待 `Recording. Press Ctrl+C to stop and save.` 将录制器作为其专用终端中的前台进程；切勿添加 shell `&`。手动执行交互或从第二个终端执行，发送 Ctrl+C 到录制器，并等待它打印保存路径之前再断言。`--use-scrcpy` 提供更快的连续帧源；没有它，录制会回退到周期性截图。可选捕获标志是 `--interval-ms`、`--max-frames` 和 `--watchdog-ms`；`--max-frames` 限制采样帧，并且清单可能包含一个额外的最终代表性帧。默认情况下，watchdog 在五分钟后最终确定并保存录制，而 `--watchdog-ms 0` 禁用该安全限制。输出是一个 JSON 清单和一个相邻的 `<name>.frames` 图像目录，不是编码视频或存档。清单包含相对 JPEG/PNG 路径和没有 base64 图像主体。将 JSON 文件和图像目录一起保留或移动，并将 JSON 路径传递给 `assert --record`。当仅当前屏幕重要时，使用普通 `assert` 而不使用 `--record`。

### 使用参考图像进行精确定位

当用户提供截图、图标、标志或参考图像并希望精确匹配视觉时，请优先使用 `tap --locate` 而不是通用的 `act --prompt`。将 `--locate` 传递为 JSON。`prompt` 描述目标，`images` 提供命名的参考图像，`convertHttpImage2Base64: true` 在图像 URL 可能无法直接被模型访问时很有用。

```bash
npx -y @midscene/android@1 tap --locate '{
  "prompt": "点击包含图像的区域",
  "images": [
    {
      "name": "目标图像",
      "url": "https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png"
    }
  ],
  "convertHttpImage2Base64": true
}'
```

相同的 `locate` JSON 形状也适用于接受 `locate` 参数的其他命令。

### 断开连接

```bash
npx -y @midscene/android@1 disconnect
```

### 消费报告文件

推荐首先为人类阅读生成的 HTML 报告。它包括每一步执行细节和每个操作的回放视频，这使得理解发生了什么以及解决问题变得更容易。

如果另一个技能或工具需要消费报告，请先用同一平台 CLI 包中的 `report-tool` 进行转换。对于基于 LLM 的工作流程，请优先使用 Markdown。当报告需要程序化处理时使用 JSON。

```bash
npx -y @midscene/android@1 report-tool --action to-markdown --htmlPath ./midscene_run/report/.../index.html --outputDir ./output-markdown
npx -y @midscene/android@1 report-tool --action split --htmlPath ./midscene_run/report/.../index.html --outputDir ./output-data
```

## 工作流程模式

由于 CLI 命令在调用之间是无状态的，请遵循此模式：

1. **连接**以建立会话
2. **启动目标应用并拍摄截图**以查看当前状态，确保应用已启动并显示在屏幕上。
3. **执行操作**使用 `act` 执行所需操作或目标驱动指令。使用 `assert` 对结果屏幕状态进行验证，或在瞬时状态工作流程期间在专用终端中保持 `record start --output ...` 运行，用 Ctrl+C 停止录制，然后使用 `assert --record`。
4. **断开连接**完成时
5. **报告结果**——总结完成的工作，展示任务期间提取的关键发现和数据，并列出任何生成的文件（截图、日志等）及其路径

## 最佳实践

1. **在使用此技能前将目标应用置于前台**：为了最佳效率，使用 ADB（例如 `adb shell am start -n <package/activity>`）**在**调用任何场景命令之前启动应用。然后拍摄截图以确认应用确实处于前台。只有在视觉确认后，你才能使用此技能进行 UI 自动化。ADB 命令比使用 midscene 导航和打开应用要快得多。
2. **关于 UI 元素要具体**：不要使用模糊的描述，提供清晰、具体的细节。说 `"右侧的 Wi-Fi 开关"` 而不是 `"开关"`。
3. **尽可能描述位置**：通过描述位置（例如，`"右上角的搜索图标"`，`"列表中的第三项"`）来帮助定位元素。
4. **切勿在后台运行**：每个场景命令必须同步运行——后台执行会破坏截图-分析-执行循环。
5. **将相关操作批量到单个 `act` 命令中**：当在同一个应用内执行连续操作时，将它们合并为一个 `act` 提示，而不是拆分为单独的命令。例如，"打开设置，点击 Wi-Fi 并将其打开" 应该是一个 `act` 调用，而不是三个。这减少了往返次数，避免了不必要的截图-分析周期，并且速度更快。
6. **当截图捕获需要加速时使用 scrcpy**：当正常安卓截图缓慢、不稳定或被环境阻塞时，向每个相关命令添加 `--use-scrcpy`。
7. **选择正确的验证窗口**：使用 `assert --prompt "..."` 对当前屏幕。对于 Toast、横幅、动画或过渡，在专用终端中运行 `record start --output ...`，执行交互，用 Ctrl+C 停止录制，等待保存路径消息，然后将工件传递给 `assert --record`。
8. **完成自动化任务后始终报告结果**：完成自动化任务后，你必须主动向用户展示结果，不要等待他们询问。这包括：(1) 用户原始问题的答案或请求任务的成果，(2) 执行期间提取或观察的关键数据，(3) 截图和其他生成文件及其路径，(4) 执行步骤的简要总结。切勿在最后一个自动化命令后默默结束——用户期望在单次交互中获得完整结果。
9. **当提供参考图像时优先使用 `tap --locate`**：如果用户分享截图、图标或标志并希望精确匹配视觉目标，请使用 `tap --locate` 与多模态 `locate` JSON 对象（如 `{ "prompt": "...", "images": [...] }`）而不是仅依赖 `act --prompt`。

**示例——弹出菜单交互：**

```bash
npx -y @midscene/android@1 act --prompt "长按消息气泡并在弹出菜单中点击 Delete"
npx -y @midscene/android@1 take_screenshot
```

**示例——表单交互：**

```bash
npx -y @midscene/android@1 act --prompt "在用户名字段中填写 'testuser'，在密码字段中填写 'pass123'，然后点击登录按钮"
npx -y @midscene/android@1 take_screenshot
```

## 提高精度（深度定位 / 深度思考）

两个可选的全局标志有助于 Midscene 在处理任务时遇到困难。将它们放在命令中的任何位置（子命令之前或之后）；一旦设置，相关的操作将默认使用它们，因此您无需为每次调用传递参数。

- `--deep-locate` — 花费额外的视觉推理轮次来精确定位目标元素。当操作与错误的位置交互时（位置漂移/偏移）使用它。它适用于所有定位元素的操作，包括 `tap --locate` 和 `act` 内部发生的定位。
- `--deep-think` — 使用更深入的推理来规划 `act`（更丰富的上下文和子目标分解）。用于复杂的、多步骤的 `act` 指令；它只影响规划。

两者都牺牲了一点速度以换取更好的结果，并且可以组合使用。

```bash
# 更精确的元素定位（也有助于 act 的内部定位）
npx -y @midscene/android@1 act --deep-locate --prompt "点击右上角的小溢出（⋮）图标"

# 复杂、多步骤 act 的更深入规划
npx -y @midscene/android@1 act --deep-think --prompt "打开设置，进入 Wi-Fi，并连接到名为 Office 的网络"

# 组合使用两者
npx -y @midscene/android@1 act --deep-locate --deep-think --prompt "填写注册表单并点击提交"
```

## 故障排除

| 问题 | 解决方案 |
|---|---|
| **ADB 未找到** | 安装 Android SDK Platform Tools：`brew install android-platform-tools`（macOS）或从 [developer.android.com](https://developer.android.com/tools/releases/platform-tools) 下载。 |
| **设备未列出** | 检查 USB 连接，确保在开发者选项中启用 USB 调试，并运行 `adb devices`。 |
| **设备显示“未授权”** | 解锁设备并接受 USB 调试授权提示。然后再次运行 `adb devices`。 |
| **设备显示“离线”** | 断开并重新连接 USB 线缆。运行 `adb kill-server && adb start-server`。 |
| **命令超时** | 设备屏幕可能关闭或锁定。使用 `adb shell input keyevent KEYCODE_WAKEUP` 唤醒设备并解锁它。 |
| **API 密钥错误** | 检查 `.env` 文件是否包含 `MIDSCENE_MODEL_API_KEY=<your-key>`。参见 [模型配置](https://midscenejs.com/zh/model-common-config.html)。 |
| **`@midscene/*` 依赖版本过时** | 使用 `npm ls @midscene/android @midscene/core @midscene/shared`（或 `pnpm why @midscene/android`）检查本地版本。使用 `npm view @midscene/android version`、`npm view @midscene/core version` 和 `npm view @midscene/shared version` 与最新版本进行比较。按需升级 (`npm i @midscene/android@latest @midscene/core@latest @midscene/shared@latest`)。 |
| **目标设备错误** | 如果连接了多个设备，请使用 `--device-id <id>` 标志。 |
| **截图缓慢或不稳定** | 在 Android Midscene 命令中添加 `--use-scrcpy` 以启用 scrcpy 加速截图。 |
