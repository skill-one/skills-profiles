---
name: browser-automation
description: '使用 Midscene 实现基于视觉的浏览器自动化。该工具从截图运行——无需 DOM 或可访问性标签。


  在无头 Puppeteer 中运行——不会接管用户的鼠标或键盘。

  同时支持 CDP 模式和 Bridge 模式，可连接到现有的 Chrome 浏览器。


  当用户需要以下功能时，请使用此技能：

  - 浏览、导航或打开网页

  - 从网站抓取、提取或收集数据

  - 填写表单、上传本地文件、点击按钮或与网页元素交互

  - 验证、校验、测试或进行前端 UI 行为的 QA

  - 对网页进行截图

  - 自动化多步骤的网页工作流

  - 测试刚构建的内容，查看其在浏览器中是否正常工作

  - 通过 CDP、DevTools 协议或远程调试连接到 Chrome

  - 连接到用户的 Chrome 浏览器，控制我的浏览器，操作我的 Chrome


  由 Midscene.js (https://midscenejs.com) 驱动'
---

# 浏览器自动化

> **关键规则 — 违反规则将导致工作流程中断：**
>
> 1. **切勿在后台执行场景命令。** 每个命令必须同步运行，以便您可以在决定下一步操作之前读取其输出（尤其是截图）。后台执行会破坏截图-分析-执行循环。
> 2. **一次只执行一个场景命令。** 等待前一个命令完成，读取截图，然后决定下一步操作。切勿将多个命令串联在一起。
> 3. **为每个命令留出足够的时间完成。** 场景命令涉及 AI 推理和屏幕交互，这可能比典型的 shell 命令更耗时。典型命令大约需要 1 分钟；复杂的 `act` 命令可能需要更长时间。
> 4. **在完成之前始终报告任务结果。** 完成自动化任务后，您必须主动向用户总结结果——包括发现的关键数据、完成的操作、拍摄的截图以及任何相关发现。切勿在最后一个自动化步骤后默默结束；用户期望在单个交互中获得完整响应。

使用 `npx -y @midscene/web@1` 自动化网页浏览。默认情况下，它通过 Puppeteer 启动无头 Chrome，该 Chrome **跨 CLI 调用持久化**——命令之间不会丢失会话。还支持 **CDP 模式**和**桥接模式**以连接到现有的 Chrome 浏览器。

## `act` 能做什么

在浏览器中的单个 `act` 调用内，Midscene 可以点击、右键点击、双击、悬停、输入或清除文本、按键、滚动、拖动、长按，并根据当前可见的内容继续通过多步骤页面流程。当启用触摸输入时，它还可以处理触摸导向页面上的滑动或捏合式交互。

## 何时使用

此技能有三种模式。根据用户的意图进行选择：

### 模式选择指南

| 模式 | 何时使用 | 如何工作 |
|------|------------|-------------|
| **Puppeteer（默认）** | 用户想浏览 URL、抓取数据、测试 UI —— 无需他们自己的浏览器 | 启动一个新的无头 Chrome，与用户的浏览器隔离 |
| **CDP 模式** | 用户说“连接到我的 Chrome”、“控制我的浏览器”、“CDP”、“远程调试”，或想操作他们现有的浏览器。还用于任务**隐式需要登录状态**的情况（例如，“检查我的订单”、“打开我的仪表板”、“查看我的账户”） | 通过 DevTools 协议连接到用户的 Chrome。需要启用远程调试（`chrome://inspect` > “允许远程调试”）。不需要扩展 |
| **桥接模式** | 用户明确提到“桥接”、“扩展”，或已安装 Midscene Chrome 扩展并希望使用它 | 通过 Midscene Chrome 扩展连接到用户的 Chrome |

**CDP 与桥接**：两者都控制用户的真实 Chrome 并保留登录会话。CDP 只需要切换 Chrome 设置；桥接需要安装 Chrome 扩展。如果用户没有指定，优先选择 **CDP 模式**，因为它前提条件较少。

### 预检：检测可用的 CDP 目标

在使用 CDP 模式之前，运行快速预检以验证 Chrome 的远程调试端口是否可达。这避免了用户未启用远程调试时出现长时间超时。

```bash
# CDP 预检（端口 9222，2 秒超时）—— 如果 Chrome 正在监听 DevTools，则返回“101”
curl -s --max-time 2 -o /dev/null -w "%{http_code}" -H "Upgrade: websocket" -H "Connection: Upgrade" -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" http://127.0.0.1:9222/devtools/browser
```

**如何使用预检结果：**
- 返回 `101` → CDP 模式可用，使用 `--cdp`
- 失败（curl 退出码 7 或 HTTP `000`）→ Chrome 未启用远程调试。使用 `--remote-debugging-port=9222` 启动 Chrome，等待 2-3 秒，然后重新运行预检。如果仍然失败，则回退到 Puppeteer 模式（或如果 Midscene Chrome 扩展已安装，则使用桥接模式）。

> **桥接模式没有可用的预检。** 尽管端口 3766 参与，但桥接服务器由 CLI **启动**（`npx ... --bridge connect` 本身打开 3766）；扩展是**客户端**，用于挂钩。在 CLI 运行之前检查 3766 总是返回空。直接运行 `--bridge connect` —— 其第一行日志（`waiting for bridge to connect...` → `one client connected`）会告诉您扩展是否捕获到它。

## 前提条件

Midscene 需要具有强大视觉基础能力的模型。必须配置以下环境变量——要么作为系统环境变量，要么在当前工作目录中的 `.env` 文件中（Midscene 会自动加载 `.env`）：

```bash
MIDSCENE_MODEL_API_KEY="your-api-key"
MIDSCENE_MODEL_NAME="model-name"
MIDSCENE_MODEL_BASE_URL="https://..."
MIDSCENE_MODEL_FAMILY="family-identifier"
```

示例：Gemini（Gemini-3-Flash）

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

如果模型未配置，请要求用户进行设置。有关支持的提供者，请参阅 [模型配置](https://midscenejs.com/model-common-config)。

## CDP 模式（连接到现有浏览器）

使用 CDP 模式控制用户的现有 Chrome 浏览器。默认的 CDP 端点是 `ws://127.0.0.1:9222/devtools/browser`（端口 9222 是 Chrome 的标准远程调试端口）。如果用户指定了不同的端口，请相应地替换 9222。

在每个命令中添加 `--cdp <ws-endpoint>`：

```bash
npx -y @midscene/web@1 connect --cdp ws://127.0.0.1:9222/devtools/browser --url https://example.com
npx -y @midscene/web@1 act --cdp ws://127.0.0.1:9222/devtools/browser --prompt "点击登录按钮，并将电子邮件字段填写为 'user@example.com'"
npx -y @midscene/web@1 take_screenshot --cdp ws://127.0.0.1:9222/devtools/browser
npx -y @midscene/web@1 disconnect --cdp ws://127.0.0.1:9222/devtools/browser
```

### CDP 模式中的自定义 HTTP 头部

当用户需要在 CDP 模式下需要自定义请求头部时（例如，将请求路由到 PPE 环境），通过单独的 `--extra-http-header 'Name:Value'` 选项传递每个头部。重复该选项以发送多个头部。使用用户提供的确切头部名称和值；不要猜测环境名称或认证值。

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
  --prompt "点击登录按钮"
```

每个 CLI 命令创建一个新的 CDP 会话。在每个可能发出请求的 CDP 命令（包括 `connect`、`act` 和 `assert`）中重复每个需要的 `--extra-http-header 'Name:Value'` 选项。在 `connect --url` 导航之前应用头部，因此初始文档请求包括它们。不要在任务摘要中打印头部值，并避免将敏感的认证值直接放入 shell 历史记录中。

### CDP 模式的重要注意事项

- 浏览器由外部管理——`disconnect` 释放连接，但**不会关闭浏览器**。CDP 模式下没有 `close` 命令。
- 在 CDP 模式下，`connect --url` 导航**现有的活动标签**，而不是打开新标签。
- 没有 `--url` 的 `connect` 附加到当前活动标签，但不导航。
- 如果连接失败，请要求用户启用远程调试：在 Chrome 中打开 `chrome://inspect` 并打开“允许远程调试”。

## 桥接模式（通过 Chrome 扩展连接）

当用户明确提到“桥接”、“扩展”，或已安装 Midscene Chrome 扩展时，使用桥接模式。在每个命令中添加 `--bridge`：

```bash
npx -y @midscene/web@1 --bridge connect --url https://example.com
npx -y @midscene/web@1 --bridge act --prompt "点击登录按钮"
npx -y @midscene/web@1 --bridge take_screenshot
npx -y @midscene/web@1 --bridge disconnect
```

### 桥接模式的重要注意事项

- 用户必须打开 Chrome（或任何支持 Chrome 扩展的 Chromium 基于浏览器，例如 Edge、Arc、Dia），并安装并启用 Midscene 扩展。
- 从 Chrome Web Store 安装扩展：https://chromewebstore.google.com/detail/midscenejs/gbldofcpkknbggpkmbdaefngejllnief
- **握手方向**：CLI 是**服务器**（监听 `127.0.0.1:3766`）；扩展是**客户端**，连接到它。“扩展面板中显示的监听”状态意味着“准备连接到 CLI”，而不是扩展本身打开了端口。实际上：先启动 `--bridge connect`；扩展将在一秒或两秒内连接。
- **活动标签必须是普通网页。** 扩展无法操作 `chrome://`、`chrome-extension://`、Chrome Web Store 或其他特权 URL。如果活动标签是其中之一，CLI 将返回 `Cannot access a chrome:// URL`。要求用户切换到常规的 `http(s)://` 标签后再重新连接。
- **文件上传权限**：桥接模式中的本地文件上传需要 Midscene 扩展的“允许访问文件 URL”权限。要求用户打开 `chrome://extensions`，找到 Midscene，点击“详细信息”，启用开关，然后切换回目标 `http(s)://` 标签再重新连接。如果上传因权限或 `Not allowed` 错误失败，请先检查此设置。
- `connect` 没有 `--url` 附加到当前活动标签；`connect --url <href>` 导航该标签。CLI 在桥接模式下不会打开新标签。
- `disconnect` 仅关闭 CLI 端的桥接连接，**不会关闭浏览器或标签**。
- 如果扩展未安装，请指导用户安装它，或建议切换到 CDP 模式。
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

拍摄截图后，读取保存的图像文件以了解当前页面状态，然后再决定下一步操作。

### 执行操作

使用 `act` 与页面交互并获取结果。它内部自主处理所有 UI 交互——点击、输入、滚动、悬停、等待和导航——因此您应该将复杂的高级任务作为一个整体给出，而不是将其分解为小步骤。用自然语言描述**您想做什么以及期望的效果**：

```bash
# 具体指令
npx -y @midscene/web@1 act --prompt "点击登录按钮，并将电子邮件字段填写为 'user@example.com'"
npx -y @midscene/web@1 act --prompt "向下滚动并点击提交按钮"

# 或目标驱动指令
npx -y @midscene/web@1 act --prompt "点击国家下拉菜单并选择日本"
```

### 上传文件

当提示 Midscene 上传文件时，`act` 需要显式的 `--file-chooser-allowed-dir`。使用包含测试用例的最小目录；不要授予项目根目录或主目录。在提示中通过相对于该目录的路径引用文件。

在桥接模式下，还确认 Midscene 扩展在 `chrome://extensions` > Midscene > “详细信息”中启用了“允许访问文件 URL”权限，并在更改开关后从目标 `http(s)://` 标签重新连接。

```bash
npx -y @midscene/web@1 act \
  --file-chooser-allowed-dir ./fixtures \
  --prompt "点击上传按钮并上传 avatar.png"
```

### 断言当前页面状态

使用 `assert` 来验证当前页面是否满足自然语言条件。它不执行 UI 操作；它检查可见的页面状态，并且仅在断言为真时通过。用于验证、QA 检查和 `act` 后的最终状态验证。

```bash
npx -y @midscene/web@1 assert --prompt "有一个可见的登录按钮"
npx -y @midscene/web@1 assert --prompt "结账页面显示订单总额和支付按钮"
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

当断言需要与参考图像（图标、标志、截图）进行比较时，传递 `--image` 用于 URL/路径，`--image-name` 用于其显示名称。每个 `--image` 可以是 http(s) 链接、`data:` URI 或本地文件路径。当需要按顺序附加多个图像时，请重复这两个标志。添加 `--convertHttpImage2Base64 true` 当模型无法直接访问 URL 时。需要 `@midscene/web@1.9.0+`。

```bash
npx -y @midscene/web@1 assert \
  --prompt "页面显示与参考图像相同的标志" \
  --image "https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png" \
  --image-name "logo" \
  --convertHttpImage2Base64 true

# 或使用本地文件
npx -y @midscene/web@1 assert \
  --prompt "可见的页头与提供的截图匹配" \
  --image "./fixtures/header.png" \
  --image-name "header"

# 多个参考图像——按顺序配对 --image 和 --image-name
npx -y @midscene/web@1 assert \
  --prompt "页面显示标志和页头" \
  --image "./fixtures/logo.png"   --image-name "logo" \
  --image "./fixtures/header.png" --image-name "header"
```

### 录制并断言瞬时 UI

当要验证的状态可能在当前屏幕断言运行之前消失时（例如，提示、加载横幅、动画或过渡），使用录制。在专用交互式终端中运行录制器：

```bash
# 终端 1：保持此前台命令运行
npx -y @midscene/web@1 record start \
  --output ./submission-observation.json

# 终端 2，在终端 1 录制时
npx -y @midscene/web@1 act --prompt "点击提交按钮"

# 发送 Ctrl+C 到终端 1 并等待保存路径消息，然后断言
npx -y @midscene/web@1 assert \
  --record ./submission-observation.json \
  --prompt "提交期间出现成功提示"
```

将正常目标标志和 `--output` 传递给 `record start`，然后等待 `Recording. Press Ctrl+C to stop and save.` 保持录制器在其终端中作为前台进程；切勿在 shell 中添加 `&`。手动执行交互或从第二个终端执行，发送 Ctrl+C 到录制器，并等待它打印保存路径后再断言。在 CDP 模式下，在 `record start`、操作和 `assert` 中重复 `--cdp ws://127.0.0.1:9222/devtools/browser`。在桥接模式下，前台录制器拥有单个桥接连接，因此手动交互而不是启动第二个桥接 CLI 操作。

可选的 `record start` 捕获标志有 `--interval-ms`、`--max-frames` 和 `--watchdog-ms`；`--max-frames` 限制采样帧数，清单文件可能包含一个额外的最终代表性帧。默认情况下，watchdog 在五分钟后最终确定并保存录制内容，而 `--watchdog-ms 0` 会禁用这个安全限制。输出是一个 JSON 清单文件和一个相邻的 `<name>.frames` 图片目录，而不是一个编码视频或归档文件。清单文件包含相对的 JPEG/PNG 路径，没有 base64 编码的图像内容。将 JSON 文件和图像目录一起保留或移动，并将 JSON 路径传递给 `assert --record`。当只关心当前页面时，使用普通的 `assert` 而不使用 `--record`。

### 使用参考图像进行精确定位

当用户提供屏幕截图、图标、标志或参考图像并希望获得精确的视觉匹配时，优先选择 `tap --locate` 而不是通用的 `act --prompt`。将 `--locate` 作为 JSON 传递。`prompt` 描述目标，`images` 提供命名的参考图像，`convertHttpImage2Base64: true` 在图像 URL 可能无法直接被模型访问时很有用。

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

相同的 `locate` JSON 结构也适用于其他接受 `locate` 参数的命令。

### 断开连接

断开与页面的连接但保持浏览器运行：

```bash
npx -y @midscene/web@1 disconnect
```

### 关闭浏览器

完成时完全关闭浏览器（仅限 Puppeteer 模式）：

```bash
npx -y @midscene/web@1 close
```

### 消耗报告文件

推荐首先生成 HTML 报告供人类阅读。它包含每一步的执行细节和每个操作的回放视频，这使得理解发生了什么以及解决问题变得更容易。

如果另一个技能或工具需要消耗报告，首先使用同一平台 CLI 包中的 `report-tool` 将其转换。对于基于 LLM 的工作流程，优先选择 Markdown。当报告需要程序化处理时使用 JSON。

```bash
npx -y @midscene/web@1 report-tool --action to-markdown --htmlPath ./midscene_run/report/.../index.html --outputDir ./output-markdown
npx -y @midscene/web@1 report-tool --action split --htmlPath ./midscene_run/report/.../index.html --outputDir ./output-data
```

## 工作流模式

浏览器通过后台 Chrome 进程**跨 CLI 调用持久化**。遵循此模式：

1. **连接**到 URL 以打开新标签页
2. **截取屏幕截图**以查看当前状态，确保页面已加载。
3. **执行操作**使用 `act` 执行所需操作或目标驱动指令。使用 `assert` 验证结果页面状态，或在瞬态状态工作流期间在专用终端中保持 `record start --output ...` 运行，使用 Ctrl+C 停止，然后使用 `assert --record`。
4. **关闭**浏览器（或**断开连接**以备后续使用）
5. **报告结果**——总结完成的工作，展示任务期间提取的关键发现和数据，并列出生成的文件（屏幕截图、日志等）及其路径

## 最佳实践

1. **始终首先连接**：在任何交互之前使用 `connect --url` 导航到目标 URL。
2. **检查可见状态**：在导航或触发页面更改的操作之后，在决定下一步之前截取屏幕截图并阅读。
3. **使用自然、具体的提示**：描述可见的 UI 和期望的结果，例如 `"点击蓝色提交按钮"`，而不是选择器 `"#submit"`。
4. **将相关的操作批量到一个 `act` 命令中**：例如，填写电子邮件和密码字段，然后点击登录。当需要检查中间状态时使用单独的命令。
5. **选择正确的验证窗口**：使用 `assert --prompt "..."` 验证当前页面。对于提示、横幅、动画或过渡，在专用终端中运行 `record start --output ...`，执行交互，使用 Ctrl+C 停止录制，等待保存路径消息，然后将工件传递给 `assert --record`。
6. **当提供参考图像时优先使用 `tap --locate`**：如果用户分享屏幕截图、图标或标志并希望精确的视觉目标，使用 `tap --locate` 并配合多模态的 `locate` JSON 对象（例如 `{ "prompt": "...", "images": [...] }`）而不是仅依赖 `act --prompt`。

**示例 — 下拉选择：**

```bash
npx -y @midscene/web@1 act --prompt "点击国家下拉菜单并选择日本"
npx -y @midscene/web@1 take_screenshot
```

**示例 — 表单交互：**

```bash
npx -y @midscene/web@1 act --prompt "填写电子邮件字段为'user@example.com'，密码字段为'pass123'，然后点击登录按钮"
npx -y @midscene/web@1 take_screenshot
```

## 提高精度（深度定位 / 深度思考）

当 Midscene 在执行任务时遇到困难，有两个可选的全局标志可以帮助。将它们放在命令中的任何位置（子命令之前或之后）；一旦设置，相关的操作将默认使用它们，因此你不需要为每次调用传递参数。

- `--deep-locate` — 额外进行一轮视觉推理以精确定位目标元素。当操作与错误的位置交互时（位置漂移 / 偏移）使用它。它适用于所有定位元素的操作，包括 `tap --locate` 和 `act` 内部发生的定位。
- `--deep-think` — 使用更深入的推理规划 `act`（更丰富的上下文和子目标分解）。用于复杂的、多步骤的 `act` 指令；它只影响规划。

两者都牺牲了一点速度以换取更好的结果，并且可以组合使用。

```bash
# 更精确的元素定位（也有助于 act 内部的定位）
npx -y @midscene/web@1 act --deep-locate --prompt "点击右上角工具栏中的小齿轮图标"

# 复杂、多步骤 act 的深度规划
npx -y @midscene/web@1 act --deep-think --prompt "完成多步骤结账表单"

# 组合使用
npx -y @midscene/web@1 act --deep-locate --deep-think --prompt "打开设置菜单，进入偏好设置，并启用暗黑模式"
```

在 CDP 或 Bridge 模式下，将你通常的 `--cdp` / `--bridge` 标志与这些一起保留。

## 故障排除

### 连接失败
- 确保系统上安装了 Chrome/Chromium（Puppeteer 默认下载自己的）。
- 检查没有防火墙阻止本地 Chrome 调试端口。

### API 键错误
- 检查 `.env` 文件是否包含 `MIDSCENE_MODEL_API_KEY=<your-key>`。
- 验证密钥是否对配置的模型提供者有效。

### 超时
- 网页可能需要时间加载。连接后，在交互之前截取屏幕截图以验证就绪状态。
- 对于慢速页面，在步骤之间稍作等待。

### `@midscene/*` 依赖版本过时
- 检查本地版本：`npm ls @midscene/web @midscene/core @midscene/shared`（或 `pnpm why @midscene/web`）。
- 检查最新版本：`npm view @midscene/web version`，`npm view @midscene/core version`，`npm view @midscene/shared version`。
- 升级依赖：`npm i @midscene/web@latest @midscene/core@latest @midscene/shared@latest`。

### 屏幕截图未显示
- 屏幕截图路径是本地文件的绝对路径。使用阅读工具查看它。
