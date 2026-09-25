# 浏览器自动化

> **关键规则 — 违反规则将中断工作流程：**
>
> 1. **切勿在后台运行场景命令。** 每个命令必须同步运行，以便您可以在决定下一步操作之前读取其输出（尤其是截图）。后台执行会破坏截图-分析-操作循环。
> 2. **一次只运行一个场景命令。** 等待前一个命令完成，读取截图，然后决定下一步操作。切勿将多个命令串联在一起。
> 3. **为每个命令留出足够的时间完成。** 场景命令涉及 AI 推理和屏幕交互，这可能比典型的 shell 命令花费更长的时间。典型命令大约需要 1 分钟；复杂的 `act` 命令可能需要更长时间。
> 4. **始终在完成前报告任务结果。** 完成自动化任务后，您必须主动向用户总结结果——包括发现的关键数据、完成的操作、拍摄的截图以及任何相关发现。切勿在最后一个自动化步骤后默默结束；用户期望在单个交互中获得完整响应。

使用 `npx -y @midscene/web@1` 自动化网页浏览。默认情况下，它通过 Puppeteer 启动无头 Chrome，该 Chrome **在 CLI 调用之间持久存在**——命令之间不会丢失会话。还支持 **CDP 模式**和**桥接模式**以连接到现有的 Chrome 浏览器。

## `act` 能做什么

在浏览器中的单个 `act` 调用内，Midscene 可以点击、右键单击、双击、悬停、输入或清除文本、按键、滚动、拖动、长按，并根据当前可见的内容继续通过多步骤页面流程。当启用触摸输入时，它还可以处理触摸导向页面上滑动或捏合风格的交互。

## 何时使用

此技能有三种模式。根据用户的意图进行选择：

### 模式选择指南

| 模式 | 何时使用 | 如何工作 |
|------|------------|-------------|
| **Puppeteer (默认)** | 用户想要浏览 URL、抓取数据、测试 UI —— 无需他们自己的浏览器 | 启动一个新的无头 Chrome，与用户的浏览器隔离 |
| **CDP 模式** | 用户说“连接到我的 Chrome”、“控制我的浏览器”、“CDP”、“远程调试”，或者想要操作他们现有的浏览器。也用于任务**隐式需要登录状态**的情况（例如，“检查我的订单”、“打开我的仪表板”、“查看我的账户”） | 通过 DevTools 协议连接到用户的 Chrome。需要启用远程调试 (`chrome://inspect` > “允许远程调试”）。不需要扩展 |
| **桥接模式** | 用户明确提到“桥接”、“扩展”，或者安装了 Midscene Chrome 扩展并希望使用它 | 通过 Midscene Chrome 扩展连接到用户的 Chrome |

**CDP 与桥接**：两者都控制用户的真实 Chrome，并保留登录会话。CDP 只需要一个 Chrome 设置切换；桥接需要一个安装在 Chrome 上的扩展。如果用户没有指定，请优先选择 **CDP 模式**，因为它有更少的先决条件。

### 预检查：检测可用的 CDP 目标

在使用 CDP 模式之前，运行快速预检查以验证 Chrome 的远程调试端口是否可达。这可以避免用户未启用远程调试时出现长时间超时。

```bash
# CDP 预检查（端口 9222，2 秒超时）—— 如果 Chrome 正在监听 DevTools，则返回“101”
curl -s --max-time 2 -o /dev/null -w "%{http_code}" -H "Upgrade: websocket" -H "Connection: Upgrade" -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" http://127.0.0.1:9222/devtools/browser
```

**如何使用预检查结果：**
- 返回 `101` → CDP 模式可用，使用 `--cdp`
- 失败（curl 退出 7 或 HTTP `000`）→ Chrome 未启用远程调试。使用 `--remote-debugging-port=9222` 启动 Chrome，等待 2-3 秒，然后重新运行预检查。如果仍然失败，则回退到 Puppeteer 模式（或如果安装了 Midscene Chrome 扩展，则使用桥接模式）。

> **桥接模式没有可用的预检查。** 尽管端口 3766 涉及其中，但 CLI 会启动桥接服务器（`npx ... --bridge connect` 打开 3766 本身）；扩展是**客户端**，它进行挂钩。在 CLI 运行之前检查 3766 总是返回空。直接运行 `--bridge connect`——它的第一行日志（`waiting for bridge to connect...` → `one client connected`）会告诉您扩展是否捕获到它。

## 先决条件

Midscene 需要具有强大视觉基础能力的模型。必须配置以下环境变量——要么作为系统环境变量，要么在当前工作目录中的 `.env` 文件中（Midscene 会自动加载 `.env`）：

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

如果未配置模型，请要求用户进行设置。有关支持提供者的信息，请参阅 [模型配置](https://midscenejs.com/model-common-config)。

## CDP 模式（连接到现有浏览器）

使用 CDP 模式控制用户现有的 Chrome 浏览器。默认的 CDP 端点是 `ws://127.0.0.1:9222/devtools/browser`（端口 9222 是 Chrome 的标准远程调试端口）。如果用户指定了不同的端口，请相应地替换 9222。

在每个命令中添加 `--cdp <ws-endpoint>`：

```bash
npx -y @midscene/web@1 connect --cdp ws://127.0.0.1:9222/devtools/browser --url https://example.com
npx -y @midscene/web@1 act --cdp ws://127.0.0.1:9222/devtools/browser --prompt "点击登录按钮并在电子邮件字段中填写 'user@example.com'"
npx -y @midscene/web@1 take_screenshot --cdp ws://127.0.0.1:9222/devtools/browser
npx -y @midscene/web@1 disconnect --cdp ws://127.0.0.1:9222/devtools/browser
```

### CDP 模式中的自定义 HTTP 标头

当用户需要在 CDP 模式下需要自定义请求标头时（例如，将请求路由到 PPE 环境），通过单独的 `--extra-http-header 'Name:Value'` 选项传递每个标头。重复该选项以发送多个标头。使用用户提供的确切标头名称和值；不要猜测环境名称或身份验证值。

```bash
npx -y @midscene/web@1 connect \
  --cdp ws://127.0.0.1:9222/devtools/browser \
  --extra-http-header 'x-use-ppe:1' \
  --extra-http-header 'x-tt-env:ppe_example' \
  --url https://example.com

npx -y @midscene/web@1 act \
  --cdp ws://127.0.0.1:9222/devtools/browser \
  --extra-http-header 'x-use-ppe:1' \
  --extra-http-header 'x-tt-env:ppe_example' \
  --prompt "点击登录按钮并在电子邮件字段中填写 'user@example.com'"
```

每个 CLI 命令都会创建一个新的 CDP 会话。在每个可能发出请求的 CDP 命令（包括 `connect`、`act` 和 `assert`）上重复每个需要的 `--extra-http-header 'Name:Value'` 选项。在第一个冒号处分割每个条目，因此值可能包含额外的冒号。标头在 `connect --url` 导航之前应用，因此初始文档请求包括它们。不要在任务摘要中打印标头值，并避免将敏感的身份验证值直接放入 shell 历史记录中。

### CDP 模式的重要注意事项

- 浏览器由外部管理——`disconnect` 释放连接，但**不会关闭浏览器**。CDP 模式中没有 `close` 命令。
- 在 CDP 模式下，`connect --url` 导航**现有的活动标签页**，而不是打开新标签页。
- 没有 `--url` 的 `connect` 附加到当前活动标签页，但不导航。
- 如果连接失败，请要求用户启用远程调试：在 Chrome 中打开 `chrome://inspect` 并打开“允许远程调试”。

## 桥接模式（通过 Chrome 扩展连接）

当用户明确提到“桥接”、“扩展”，或者安装了 Midscene Chrome 扩展时，请使用桥接模式。在每个命令中添加 `--bridge`：

```bash
npx -y @midscene/web@1 --bridge connect --url https://example.com
npx -y @midscene/web@1 --bridge act --prompt "点击登录按钮并在电子邮件字段中填写 'user@example.com'"
npx -y @midscene/web@1 --bridge take_screenshot
npx -y @midscene/web@1 --bridge disconnect
```

### 桥接模式的重要注意事项

- 用户必须打开 Chrome（或任何支持 Chrome 扩展的 Chromium 基于浏览器，例如 Edge、Arc、Dia），并安装并启用 Midscene 扩展。
- 从 Chrome Web Store 安装扩展：https://chromewebstore.google.com/detail/midscenejs/gbldofcpkknbggpkmbdaefngejllnief
- **握手方向**：**CLI 是服务器**（监听 `127.0.0.1:3766`）；**扩展是客户端**，它连接到它。扩展面板中显示的“Listening”状态意味着“准备好连接到 CLI”，而不是扩展本身打开了端口。实际上：首先运行 `--bridge connect`；扩展将在一秒或两秒内进行挂钩。
- **活动标签页必须是普通网页。** 扩展无法操作 `chrome://`、`chrome-extension://`、Chrome Web Store 或其他特权 URL。如果活动标签页是其中之一，CLI 将返回 `Cannot access a chrome:// URL`。要求用户切换到常规的 `http(s)://` 标签页后再重新连接。
- **文件上传权限**：桥接模式中的本地文件上传需要 Midscene 扩展的“允许访问文件 URL”权限。要求用户打开 `chrome://extensions`，找到 Midscene，点击“详细信息”，启用开关，然后切换回目标 `http(s)://` 标签页再重新连接。如果上传因权限或 `Not allowed` 错误而失败，请首先检查此设置。
- 没有 `--url` 的 `connect` 附加到当前活动标签页；`connect --url <href>` 导航该标签页。CLI 在桥接模式下不会打开新标签页。
- `disconnect` 仅关闭 CLI 端的桥接连接，**不会关闭浏览器或标签页**。
- 如果未安装扩展，请指导用户安装它，或者建议切换到 CDP 模式。
- 请参阅 [桥接模式文档](https://midscenejs.com/bridge-mode-by-chrome-extension.html)。

## 命令

### 连接到网页

```bash
npx -y @midscene/web@1 connect --url https://example.com
```

### 拍摄截图

```bash
npx -y @midscene/web@1 take_screenshot
```

在拍摄截图后，读取保存的图像文件以了解当前页面状态，然后再决定下一步操作。

### 执行操作

使用 `act` 与页面交互并获取结果。它内部自主处理所有 UI 交互——点击、输入、滚动、悬停、按键、滚动、拖动、长按，并根据当前可见的内容继续通过多步骤页面流程。当启用触摸输入时，它还可以处理触摸导向页面上滑动或捏合风格的交互。

### 上传文件

当提示 Midscene 上传文件时，`act` 需要显式的 `--file-chooser-allowed-dir`。使用包含测试用例的最小目录；不要授予项目根目录或主目录。在提示中通过相对于该目录的路径引用文件。

在桥接模式下，还确认 Midscene 扩展在 `chrome://extensions` > Midscene > “详细信息”中启用了“允许访问文件 URL”权限，并在从目标 `http(s)://` 标签页重新连接后更改开关。

```bash
npx -y @midscene/web@1 act \
  --file-chooser-allowed-dir ./fixtures \
  --prompt "点击上传按钮并上传 avatar.png"
```

### 断言当前页面状态

使用 `assert` 来验证当前页面是否满足自然语言条件。它不会执行 UI 操作；它会检查可见的页面状态，并且仅在断言为真时才会通过。用于验证、QA 检查和 `act` 后的最终状态验证。

```bash
npx -y @midscene/web@1 assert --prompt "有一个可见的登录按钮"
npx -y @midscene/web@1 assert --prompt "结账页面显示订单总额和一个支付按钮"
```

在 CDP 或桥接模式下，传递与其他命令相同的连接标志：

```bash
npx -y @midscene/web@1 assert --cdp ws://127.0.0.1:9222/devtools/browser --prompt "仪表板已加载"
npx -y @midscene/web@1 --bridge assert --prompt "个人资料页面显示用户的头像"
```

默认情况下，失败的断言会抛出 AI 生成的理由。传递 `--message` 以抛出自定义错误消息，这对于在 QA 和 CI 日志中展示预期结果很有用。

```bash
npx -y @midscene/web@1 assert \
  --prompt "结账页面显示订单确认" \
  --message "点击支付后应该确认订单"
```

当断言需要与参考图像（图标、标志、截图）进行比较时，传递 `--image` 用于 URL/路径，`--image-name` 用于其显示名称。每个 `--image` 可以是 http(s) 链接、`data:` URI 或本地文件路径。当需要附加多个图像时，请按匹配的顺序重复这两个标志。添加 `--convertHttpImage2Base64 true` 当模型无法直接访问 URL 时。需要 `@midscene/web@1.9.0+`。

```bash
npx -y @midscene/web@1 assert \
  --prompt "页面显示与参考图像相同的标志" \
  --image "https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png" \
  --image-name "logo" \
  --convertHttpImage2Base64 true

# 或使用本地文件
npx -y @midscene/web@1 assert \
  --prompt "可见的标题与提供的截图匹配" \
  --image "./fixtures/header.png" \
  --image-name "header"

# 多个参考图像——按顺序匹配 --image 和 --image-name
npx -y @midscene/web@1 assert \
  --prompt "页面显示标志和标题" \
  --image "./fixtures/logo.png"   --image-name "logo" \
  --image "./fixtures/header.png" --image-name "header"
```

### 录制和断言瞬时 UI

当要验证的状态可能在当前屏幕断言运行之前消失时，使用录制，例如吐司、加载横幅、动画或过渡。在专用交互式终端中运行录制器：

```bash
# 终端 1：保持此前台命令运行
npx -y @midscene/web@1 record start \
  --output ./submission-observation.json

# 终端 2，在终端 1 录制时
npx -y @midscene/web@1 act --prompt "点击提交按钮"

# 发送 Ctrl+C 到终端 1 并等待保存路径消息，然后断言
npx -y @midscene/web@1 assert \
  --record ./submission-observation.json \
  --prompt "提交期间出现了一个成功吐司"
```

将正常目标标志和 `--output` 传递给 `record start`，然后等待 `Recording. Press Ctrl+C to stop and save.` 将录制器作为前台进程保留在其终端中；切勿在 shell 中添加 `&`。手动执行交互或从第二个终端执行，发送 Ctrl+C 到录制器，并等待它打印保存路径之前进行断言。在 CDP 模式下，在 `record start`、操作和 `assert` 上重复 `--cdp ws://127.0.0.1:9222/devtools/browser`。在桥接模式下，前台录制器拥有单个桥接连接，因此请手动交互而不是启动第二个桥接 CLI 操作。

`record start` 上的可选捕获标志是 `--interval-ms`、`--max-frames` 和 `--watchdog-ms`；`--max-frames` 限制采样的帧数，而清单可能包含一个额外的最终代表性帧。默认情况下，watchdog 在五分钟后最终确定并保存录制，而 `--watchdog-ms 0` 禁用该安全限制。输出是一个 JSON 清单和一个相邻的 `<name>.frames` 图像目录，而不是编码视频或存档。清单包含相对的 JPEG/PNG 路径，但没有 base64 图像正文。保留或移动 JSON 文件和图像目录在一起，并将 JSON 路径传递给 `assert --record`。当仅当前页面很重要时，使用普通 `assert` 而不使用 `--record`。

### 使用参考图像进行精确定位

当用户提供截图、图标、标志或参考图像并希望进行精确的视觉匹配时，请优先使用 `tap --locate` 而不是通用的 `act --prompt`。将 `--locate` 作为 JSON 传递。`prompt` 描述目标，`images` 提供命名的参考图像，`convertHttpImage2Base64: true` 在图像 URL 可能无法直接被模型访问时很有用。

```bash
npx -y @midscene/web@1 tap --locate '{
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

断开与页面的连接但保持浏览器运行：

```bash
npx -y @midscene/web@1 disconnect
```

### 关闭浏览器

完成时完全关闭浏览器（Puppeteer 模式仅限）：

```bash
npx -y @midscene/web@1 close
```

### 消费报告文件

建议首先生成 HTML 报告供人类阅读。它包括按步骤执行的详细信息和每个操作的回放视频，这使得理解发生了什么以及解决问题变得更容易。

如果另一个技能或工具需要消费报告，请首先使用来自同一平台 CLI 包的 `report-tool` 进行转换。优先使用 Markdown 进行基于 LLM 的工作流。当报告需要程序处理时，使用 JSON。

```bash
npx -y @midscene/web@1 report-tool --action to-markdown --htmlPath ./midscene_run/report/.../index.html --outputDir ./output-markdown
npx -y @midscene/web@1 report-tool --action split --htmlPath ./midscene_run/report/.../index.html --outputDir ./output-data
```

## 工作流程模式

浏览器通过后台 Chrome 进程**跨 CLI 调用持久存在**。遵循此模式：

1. **连接**到 URL 以打开新标签页
2. **拍摄截图**以查看当前状态，确保页面已加载。
3. **执行操作**使用 `act` 执行所需操作或目标驱动指令。使用 `assert` 进行结果页面状态验证，或在瞬态状态工作流中在专用终端中保持 `record start --output ...` 运行，使用 Ctrl+C 停止它，然后使用 `assert --record`。
4. **关闭**浏览器完成时（或**断开连接**以保留它供以后使用）
5. **报告结果**——总结完成的工作，展示在任务过程中提取的关键发现和数据，并列出生成的文件（截图、日志等）及其路径

## 最佳实践

1. **始终首先连接**：在 `connect --url` 导航到目标 URL 之前进行任何交互。
2. **检查可见状态**：在导航或触发页面更改的操作之后，拍摄截图并读取它，然后再决定下一步操作。
3. **使用自然、具体的提示**：描述可见 UI 和预期结果，例如 `"点击蓝色的提交按钮在联系表单中"`，而不是 `"#submit"`。
4. **将相关的操作批量到一个单一的 `act` 命令中**：例如，填写电子邮件和密码字段，然后点击登录在一个提示中。当您需要检查中间状态时，使用单独的命令。
5. **选择正确的验证窗口**：使用 `assert --prompt "..."` 对于当前页面。对于吐司、横幅、动画或过渡，在专用交互式终端中运行 `record start --output ...`，执行交互，使用 Ctrl+C 停止录制，等待保存路径消息，然后将工件传递给 `assert --record`。
6. **当提供参考图像时，优先使用 `tap --locate`**：如果用户分享截图、图标或标志并希望精确的视觉目标，请使用 `tap --locate` 与多模式 `locate` JSON 对象（例如 `{ "prompt": "...", "images": [...] }`）而不是仅依赖 `act --prompt`。

**示例——下拉选择：**

```bash
npx -y @midscene/web@1 act --prompt "点击国家下拉列表并选择日本"
npx -y @midscene/web@1 take_screenshot
```

**示例——表单交互：**

```bash
npx -y @midscene/web@1 act --prompt "填写电子邮件字段为 'user@example.com' 和密码字段为 'pass123'，然后点击登录按钮"
npx -y @midscene/web@1 take_screenshot
```

## 提高精度（深度定位 / 深度思考）

两个可选的全局标志有助于 Midscene 在任务遇到困难时提高精度。将它们放在命令中的任何位置（子命令之前或之后）；一旦设置，相关的操作将默认使用它们，因此您不需要为每次调用传递参数。

- `--deep-locate` — 花费额外的视觉推理回合来精确定位目标元素。当操作与错误的位置交互时（位置漂移 / 偏移）使用它。它适用于每个定位元素的运算，包括 `tap --locate` 和 `act` 内部发生的定位。
- `--deep-think` — 使用更深入的推理计划 `act`（更丰富的上下文和子目标分解）。用于复杂的、多步骤的 `act` 指令；它仅影响规划。

两者都牺牲了一点速度来换取更好的结果，并且可以组合使用。

```bash
# 更精确的元素定位（也有助于 act 内部的定位）
npx -y @midscene/web@1 act --deep-locate --prompt "点击右上角工具栏中的微小的齿轮图标"

# 对复杂的、多步骤 act 进行更深入的规划
npx -y @midscene/web@1 act --deep-think --prompt "完成多步骤结账表单"

# 组合使用两者
npx -y @midscene/web@1 act --deep-locate --deep-think --prompt "打开设置菜单，进入首选项，并启用暗黑模式"
```

在 CDP 或桥接模式下，请保留您通常的 `--cdp` / `--bridge` 标志。
