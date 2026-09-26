# HarmonyOS 设备自动化

> **关键规则 — 违反规则将中断工作流程：**
>
> 1. **切勿在后台运行场景命令。** 每个命令必须同步运行，以便您可以在决定下一步操作之前读取其输出（尤其是截图）。后台执行会破坏截图-分析-操作循环。
> 2. **一次只运行一个场景命令。** 等待前一个命令完成，读取截图，然后决定下一步操作。切勿将多个命令串联在一起。
> 3. **为每个命令留出足够的时间完成。** 场景命令涉及 AI 推理和屏幕交互，这可能比典型的 shell 命令更耗时。典型命令大约需要 1 分钟；复杂的 `act` 命令可能需要更长时间。

使用 `npx -y @midscene/harmony@1` 自动化 HarmonyOS NEXT 设备。每个 CLI 命令都直接映射到 MCP 工具 — 您（AI 代理）作为大脑，根据截图决定要执行哪些操作。

## `act` 能做什么

在 HarmonyOS 的单个 `act` 调用中，Midscene 可以点击、双击、长按、输入、清除文本、滚动、拖动项目、按键，并使用系统导航（如返回、主页或最近应用）来与当前可见屏幕进行交互。由于底层 HarmonyOS 自动化层未暴露多指输入，因此无法使用两指缩放。

## 前置条件

Midscene 需要具有强大视觉基础能力的模型。必须配置以下环境变量 — 既可以作为系统环境变量，也可以在当前工作目录中的 `.env` 文件中配置（Midscene 会自动加载 `.env`）：

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

如果未配置模型，请提示用户进行设置。有关受支持的提供者，请参阅 [模型配置](https://midscenejs.com/model-common-config)。

## HDC 设置

HDC（HarmonyOS 设备连接器）必须已安装并可访问。常见设置：

- 通过 [DevEco Studio](https://developer.huawei.com/consumer/cn/deveco-studio/) 安装
- 或设置 `HDC_HOME` 环境变量指向 HDC 目录

验证 HDC 是否正常工作：

```bash
hdc version
hdc list targets
```

## 命令

### 连接设备

```bash
npx -y @midscene/harmony@1 connect
npx -y @midscene/harmony@1 connect --deviceId 0123456789ABCDEF
```

### 启动应用或 URL

当您希望在执行其他任务之前获得确定性起始点时，使用专用启动步骤：

```bash
npx -y @midscene/harmony@1 launch --uri com.huawei.hmos.settings
npx -y @midscene/harmony@1 launch --uri com.huawei.hmos.camera
npx -y @midscene/harmony@1 launch --uri https://www.example.com
```

### 运行原始 HarmonyOS Shell 命令

当任务需要较低级别的设备控制，而无法最好地表示为可见 UI 交互时，使用此命令：

```bash
npx -y @midscene/harmony@1 runhdcshell --command "hidumper -s RenderService -a screen"
```

这会被转发到连接设备的 `hdc shell`。实际上，底层命令是 `hdc -t <deviceId> shell hidumper -s RenderService -a screen`。

### 拍摄截图

```bash
npx -y @midscene/harmony@1 take_screenshot
```

拍摄截图后，读取保存的图像文件以了解当前屏幕状态，然后再决定下一步操作。

### 执行操作

使用 `act` 与设备交互并获取结果。它自动处理所有 UI 交互，因此您应该将其作为整体复杂的、高级的任务提供，而不是将其拆分为小步骤。用自然语言描述**您想要做什么以及期望的效果**：

```bash
# 具体指令
npx -y @midscene/harmony@1 act --prompt "在搜索框中输入 hello world 并按 Enter"
npx -y @midscene/harmony@1 act --prompt "长按消息气泡并在弹出菜单中点击删除"

# 或目标驱动指令
npx -y @midscene/harmony@1 act --prompt "打开设置，导航到 Wi-Fi 设置，告诉我已连接的网络名称"
```

### 断言当前屏幕状态

使用 `assert` 来验证当前屏幕是否满足自然语言条件。它不会执行 UI 操作；它会检查可见的屏幕状态，并且仅在断言为真时通过。用于验证、QA 检查和 `act` 后的最终状态验证。

```bash
npx -y @midscene/harmony@1 assert --prompt "有一个登录按钮可见"
npx -y @midscene/harmony@1 assert --prompt "设置屏幕显示 Wi-Fi 和蓝牙选项"
npx -y @midscene/harmony@1 assert --deviceId 0123456789ABCDEF --prompt "应用显示成功登录消息"
```

默认情况下，失败的断言会抛出 AI 生成的理由。传递 `--message` 以抛出自定义错误消息，这对于在 QA 和 CI 日志中展示预期结果非常有用。

```bash
npx -y @midscene/harmony@1 assert \
  --prompt "订单确认屏幕可见" \
  --message "点击支付后订单应被确认"
```

当断言需要与参考图像（图标、标志、截图）进行比较时，传递 `--image` 用于 URL/路径，`--image-name` 用于其显示名称。每个 `--image` 可以是 http(s) 链接、`data:` URI 或本地文件路径。当需要附加多个图像时，请按匹配顺序重复这两个标志。当模型无法直接访问 URL 时，添加 `--convertHttpImage2Base64 true`。需要 `@midscene/harmony@1.9.0+`。

```bash
npx -y @midscene/harmony@1 assert \
  --prompt "可见的应用图标与提供的参考图像匹配" \
  --image "https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png" \
  --image-name "icon" \
  --convertHttpImage2Base64 true

# 或使用本地文件
npx -y @midscene/harmony@1 assert \
  --prompt "屏幕上的标题与本地截图匹配" \
  --image "./fixtures/header.png" \
  --image-name "header"

# 多个参考图像 — 按顺序配对 `--image` 和 `--image-name`
npx -y @midscene/harmony@1 assert \
  --prompt "屏幕显示应用图标和标题" \
  --image "./fixtures/icon.png"   --image-name "icon" \
  --image "./fixtures/header.png" --image-name "header"
```

### 录制并断言瞬时 UI

当要验证的状态可能在当前屏幕断言运行之前消失时，使用录制，例如吐司、加载横幅、动画或过渡：

```bash
# 终端 1：保持此前台命令运行
npx -y @midscene/harmony@1 record start \
  --device-id 0123456789ABCDEF \
  --output ./submission-observation.json

# 终端 2，同时终端 1 录制
npx -y @midscene/harmony@1 act --device-id 0123456789ABCDEF \
  --prompt "点击提交按钮"

# 发送 Ctrl+C 到终端 1 并等待保存路径消息，然后断言
npx -y @midscene/harmony@1 assert --device-id 0123456789ABCDEF \
  --record ./submission-observation.json \
  --prompt "提交期间出现成功吐司"
```

将目标标志、捕获标志和 `--output` 传递给 `record start`，然后等待 `Recording. Press Ctrl+C to stop and save.` 将记录器作为前台进程保存在其专用终端中；切勿添加 shell `&`。手动或从第二个终端执行交互，发送 Ctrl+C 到记录器，并等待它打印保存路径之前再进行断言。HarmonyOS 录制使用周期性截图。可选捕获标志是 `--interval-ms`、`--max-frames` 和 `--watchdog-ms`；`--max-frames` 限制采样帧数，清单可能包含一个额外的最终代表性帧。默认情况下，watchdog 在五分钟后最终确定并保存录制，而 `--watchdog-ms 0` 禁用该安全限制。输出是一个 JSON 清单和一个相邻的 `<name>.frames` 图像目录，不是编码视频或存档。清单包含相对 JPEG/PNG 路径，没有 base64 图像主体。保留或移动 JSON 文件和图像目录，并将 JSON 路径传递给 `assert --record`。当仅当前屏幕重要时，使用普通 `assert` 而不是 `--record`。

### 使用参考图像进行精确定位

当用户提供截图、图标、标志或参考图像并希望进行精确视觉匹配时，请优先使用 `tap --locate` 而不是通用的 `act --prompt`。将 `--locate` 作为 JSON 传递。`prompt` 描述目标，`images` 提供命名的参考图像，`convertHttpImage2Base64: true` 在图像 URL 可能无法直接被模型访问时很有用。

```bash
npx -y @midscene/harmony@1 tap --locate '{
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
npx -y @midscene/harmony@1 disconnect
```

### 消费报告文件

建议首先将生成的 HTML 报告用于人类阅读。它包含每一步执行细节和每个操作的回放视频，这使得理解发生了什么以及解决问题变得更容易。

如果另一个技能或工具需要消费报告，请首先使用来自同一平台 CLI 包的 `report-tool` 进行转换。对于基于 LLM 的工作流程，请优先使用 Markdown。当报告需要程序化处理时，请使用 JSON。

```bash
npx -y @midscene/harmony@1 report-tool --action to-markdown --htmlPath ./midscene_run/report/.../index.html --outputDir ./output-markdown
npx -y @midscene/harmony@1 report-tool --action split --htmlPath ./midscene_run/report/.../index.html --outputDir ./output-data
```

## 工作流程模式

由于 CLI 命令在调用之间是无状态的，请遵循此模式：

1. **连接**以建立会话
2. **启动目标应用并拍摄截图**以查看当前状态，确保应用已启动并显示在屏幕上。
3. **执行操作**使用 `act` 执行所需操作或目标驱动指令。使用 `assert` 进行结果屏幕状态验证，或在瞬时状态工作流程期间在专用终端中保持 `record start --output ...` 运行，用 Ctrl+C 停止它，然后使用 `assert --record`。
4. **断开连接**完成时

## 最佳实践

1. **在交互之前将目标应用带到前台**：连接后，使用专用启动器（例如，`npx -y @midscene/harmony@1 launch --uri <bundleName>`），然后拍摄截图以确认应用实际上在前台。不要使用猜测的能能力名称调用 `aa start`，因为 HarmonyOS 应用可能声明不同的入口能力。只有在视觉确认后，您才能使用此技能进行 UI 自动化。
2. **具体说明 UI 元素**：不要使用模糊描述，提供清晰、具体的细节。说 `"右侧的 Wi-Fi 开关"` 而不是 `"开关"`。
3. **尽可能描述位置**：通过描述其位置（例如，`"右上角的搜索图标"`，`"列表中的第三项"`）来帮助定位元素。
4. **切勿在后台运行**：每个场景命令必须同步运行 — 后台执行会破坏截图-分析-操作循环。
5. **将相关的操作批量到单个 `act` 命令中**：当在同一个应用中执行连续操作时，将它们合并为一个 `act` 提示，而不是拆分为单独的命令。例如，"打开设置，点击 Wi-Fi 并将其打开" 应该是一个 `act` 调用，而不是三个。这减少了往返次数，避免了不必要的截图-分析周期，并且速度更快。
6. **选择正确的验证窗口**：使用 `assert --prompt "..."` 用于当前屏幕。对于吐司、横幅、动画或过渡，在专用终端中运行 `record start --output ...`，执行交互，用 Ctrl+C 停止录制，等待保存路径消息，然后将工件传递给 `assert --record`。
7. **完成自动化任务后总结报告文件**：完成自动化任务后，收集并总结所有报告文件（截图、日志、输出文件等）供用户使用。提供清晰的总结，说明完成了什么，生成了哪些文件，以及它们的位置，使用户可以轻松查看结果。
8. **当提供参考图像时，优先使用 `tap --locate`**：如果用户分享截图、图标或标志并希望进行精确视觉匹配，请使用 `tap --locate` 与多模态 `locate` JSON 对象（例如 `{ "prompt": "...", "images": [...] }`）而不是仅依赖 `act --prompt`。

**示例 — 应用启动和交互**：

```bash
npx -y @midscene/harmony@1 connect
npx -y @midscene/harmony@1 launch --uri com.huawei.hmos.settings
npx -y @midscene/harmony@1 take_screenshot
npx -y @midscene/harmony@1 act --prompt "滚动设置列表并点击 About device"
npx -y @midscene/harmony@1 take_screenshot
npx -y @midscene/harmony@1 disconnect
```

**示例 — 表单交互**：

```bash
npx -y @midscene/harmony@1 act --prompt "在用户名字段中输入 'testuser'，在密码字段中输入 'pass123'，然后点击登录按钮"
npx -y @midscene/harmony@1 take_screenshot
```

## 常见 HarmonyOS Bundle 名称

| 应用 | Bundle 名称 |
|-----|-------------|
| 设置 | com.huawei.hmos.settings |
| 相机 | com.huawei.hmos.camera |
| 相册 | com.huawei.hmos.photos |
| 日历 | com.huawei.hmos.calendar |
| 时钟 | com.huawei.hmos.clock |
| 计算器 | com.huawei.hmos.calculator |
| 浏览器 | com.huawei.hmos.browser |
| 天气 | com.huawei.hmos.weather |

## 提高精度（深度定位 / 深度思考）

当 Midscene 在任务中遇到困难时，这两个可选的全局标志会提供帮助。将它们放在命令中的任何位置（子命令之前或之后）；一旦设置，相关操作会默认使用它们，因此您不需要为每次调用传递参数。

- `--deep-locate` — 花费额外的视觉推理轮次来精确定位目标元素。当操作与错误的位置交互（位置漂移/偏移）时使用它。它适用于每个定位元素的运算，包括 `tap --locate` 和 `act` 内部发生的定位。
- `--deep-think` — 使用更深层次的推理计划 `act`（更丰富的上下文和子目标分解）。用于复杂的、多步骤的 `act` 指令；它只影响规划。

两者都牺牲了一点速度以换取更好的结果，并且可以组合使用。

```bash
# 更精确的元素定位（也有助于 act 的内部定位）
npx -y @midscene/harmony@1 act --deep-locate --prompt "点击左上角的小返回箭头"

# 更深入的规划，用于复杂的、多步骤的 act
npx -y @midscene/harmony@1 act --deep-think --prompt "滚动设置列表，打开 About device，并找到系统版本"

# 组合使用
npx -y @midscene/harmony@1 act --deep-locate --deep-think --prompt "打开设置，进入 Wi-Fi 并将其打开"
```

## 故障排除

| 问题 | 解决方案 |
|---|---|
| **HDC 未找到** | 通过 DevEco Studio 安装或设置 `HDC_HOME` 环境变量。 |
| **未列出设备** | 检查 USB 连接，确保在开发者选项中启用了 USB 调试，并运行 `hdc list targets`。 |
| **命令超时** | 设备屏幕可能关闭或锁定。唤醒设备并解锁它。 |
| **API 密钥错误** | 检查 `.env` 文件是否包含 `MIDSCENE_MODEL_API_KEY=<your-key>`。参见 [模型配置](https://midscenejs.com/zh/model-common-config.html)。 |
| **`@midscene/*` 依赖版本过时** | 使用 `npm ls @midscene/harmony @midscene/core @midscene/shared`（或 `pnpm why @midscene/harmony`）检查本地版本。通过 `npm view @midscene/harmony version`、`npm view @midscene/core version` 和 `npm view @midscene/shared version` 与最新版本进行比较。如有需要，升级：`npm i @midscene/harmony@latest @midscene/core@latest @midscene/shared@latest`。 |
| **目标设备错误** | 如果连接了多个设备，请在 `connect` 命令中使用 `--deviceId <id>` 标志。 |
