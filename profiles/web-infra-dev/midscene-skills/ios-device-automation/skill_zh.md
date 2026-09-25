# iOS设备自动化

> **关键规则 — 违反规则将中断工作流程：**
>
> 1. **切勿在后台运行场景命令。** 每个命令必须同步运行，以便您可以在决定下一步操作之前读取其输出（尤其是截图）。后台执行会破坏截图-分析-操作循环。
> 2. **一次只运行一个场景命令。** 等待前一个命令完成，读取截图，然后决定下一步操作。切勿将多个命令串联在一起。
> 3. **为每个命令留出足够的时间完成。** 场景命令涉及AI推理和屏幕交互，这可能比典型的shell命令花费更长的时间。典型的命令大约需要1分钟；复杂的`act`命令可能需要更长时间。
> 4. **始终在完成前报告任务结果。** 完成自动化任务后，您必须主动向用户总结结果——包括发现的关键数据、完成的操作、拍摄的截图以及任何相关发现。切勿在最后一个自动化步骤后默默结束；用户期望在单次交互中获得完整结果。

使用`npx -y @midscene/ios@1`自动化iOS设备。每个CLI命令都直接映射到MCP工具——您（AI代理）作为大脑，根据截图决定要采取哪些操作。

## `act`能做什么

在iOS的单个`act`调用中，Midscene可以点击、双击、长按、输入、清除文本、滚动、拖动项目、用两根手指缩放、按键，并使用系统导航（如主屏幕或应用切换器），同时从当前可见屏幕工作。

## 前置条件

Midscene需要具有强大视觉基础能力的模型。必须配置以下环境变量——既可以作为系统环境变量，也可以在当前工作目录中的`.env`文件中配置（Midscene会自动加载`.env`）：

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
# 如果使用OpenRouter，设置：
# MIDSCENE_MODEL_API_KEY="your-openrouter-api-key"
# MIDSCENE_MODEL_NAME="qwen/qwen3.5-plus"
# MIDSCENE_MODEL_BASE_URL="https://openrouter.ai/api/v1"
```

示例：豆包Seed 2.0 Lite

```bash
MIDSCENE_MODEL_API_KEY="your-doubao-api-key"
MIDSCENE_MODEL_NAME="doubao-seed-2-0-lite"
MIDSCENE_MODEL_BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
MIDSCENE_MODEL_FAMILY="doubao-seed"
```

常用模型：豆包Seed 2.0 Lite、Qwen 3.5、智谱GLM-4.6V、Gemini-3-Pro、Gemini-3-Flash。

如果未配置模型，请提示用户进行设置。有关支持的提供者，请参阅[模型配置](https://midscenejs.com/model-common-config)。

## 命令

### 连接到设备

```bash
npx -y @midscene/ios@1 connect
```

如果WebDriverAgent已经运行，并且会话是在Midscene外部创建的，请一起传递WDA端点和外部会话ID：

```bash
npx -y @midscene/ios@1 connect --wda-host 127.0.0.1 --wda-port 8100 --session-id <sessionId>
```

在后续命令中，如果您希望它们通过现有的WDA会话运行，请使用相同的`--wda-host`、`--wda-port`和`--session-id`选项。

### 启动应用、URL或深度链接

当您希望在任务其余部分之前从已知应用或路由开始时，使用内置启动功能。给出您拥有的最具体的靶标，例如bundle ID、Web URL、深度链接或电话/邮件链接。典型靶标包括`com.apple.Preferences`、`https://www.apple.com`、`myapp://profile/user/123`和`tel:+1234567890`。

### 发送直接设备请求

当任务需要比正常可见UI交互更底层的设备控制时，使用此命令：

```bash
npx -y @midscene/ios@1 runwdarequest --method GET --endpoint /wda/screen
```

这不会运行ADB命令。在iOS上，底层操作是对WebDriverAgent的HTTP请求，通常是`GET http://<wdaHost>:<wdaPort>/session/<sessionId>/wda/screen`。

### 拍摄截图

```bash
npx -y @midscene/ios@1 take_screenshot
```

拍摄截图后，读取保存的图像文件以了解当前屏幕状态，然后再决定下一步操作。

### 执行操作

使用`act`与设备交互并获取结果。它内部自动处理所有UI交互——点击、输入、滚动、滑动、等待和导航——因此您应该将复杂的高级任务作为一个整体给出，而不是将其拆分为小步骤。用自然语言描述**您想做什么以及期望的效果**：

```bash
# 具体指令
npx -y @midscene/ios@1 act --prompt "在搜索框中输入hello world并按Enter"
npx -y @midscene/ios@1 act --prompt "点击删除，然后在警告对话框中确认"

# 或目标驱动指令
npx -y @midscene/ios@1 act --prompt "打开设置，导航到Wi-Fi，告诉我已连接的网络名称"
```

### 断言当前屏幕状态

使用`assert`来验证当前屏幕是否满足自然语言条件。它不会执行UI操作；它会检查可见的屏幕状态，并且仅在断言为真时通过。用于验证、QA检查和`act`之后的最终状态验证。

```bash
npx -y @midscene/ios@1 assert --prompt "有一个登录按钮可见"
npx -y @midscene/ios@1 assert --prompt "设置屏幕显示Wi-Fi和蓝牙选项"
```

默认情况下，失败的断言会抛出AI生成的理由。传递`--message`以抛出自定义错误消息，这对于在QA和CI日志中展示预期结果很有用。

```bash
npx -y @midscene/ios@1 assert \
  --prompt "订单确认屏幕可见" \
  --message "点击支付后应该确认订单"
```

当断言需要与参考图像（图标、标志、截图）进行比较时，传递`--image`用于URL/路径，传递`--image-name`用于其显示名称。每个`--image`可以是一个http(s)链接、`data:` URI或本地文件路径。当需要附加多个图像时，请按匹配顺序重复这两个标志。当模型无法直接访问URL时，添加`--convertHttpImage2Base64 true`。需要`@midscene/ios@1.9.0+`。

```bash
npx -y @midscene/ios@1 assert \
  --prompt "可见的应用图标与提供的参考图像匹配" \
  --image "https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png" \
  --image-name "icon" \
  --convertHttpImage2Base64 true

# 或使用本地文件
npx -y @midscene/ios@1 assert \
  --prompt "屏幕上的标题与本地截图匹配" \
  --image "./fixtures/header.png" \
  --image-name "header"

# 多个参考图像——按顺序匹配`--image`和`--image-name`
npx -y @midscene/ios@1 assert \
  --prompt "屏幕显示应用图标和标题" \
  --image "./fixtures/icon.png"   --image-name "icon" \
  --image "./fixtures/header.png" --image-name "header"
```

### 录制并断言瞬时UI

当要验证的状态可能在当前屏幕断言运行之前消失时，使用录制，例如toast、加载横幅、动画或过渡：

```bash
# 终端1：保持此前台命令运行
npx -y @midscene/ios@1 record start --device-id <udid> \
  --output ./submission-observation.json

# 终端2，在终端1录制时
npx -y @midscene/ios@1 act --device-id <udid> \
  --prompt "点击提交按钮"

# 发送Ctrl+C到终端1并等待保存路径消息，然后断言
npx -y @midscene/ios@1 assert --device-id <udid> \
  --record ./submission-observation.json \
  --prompt "提交期间出现成功toast"
```

将目标标志、捕获标志和`--output`传递给`record start`，然后等待`Recording. Press Ctrl+C to stop and save.` 将录制器作为前台进程保存在其专用终端中；切勿添加shell `&`。手动执行交互或从第二个终端执行，发送Ctrl+C到录制器，并等待它打印保存路径之前再断言。录制在启用时使用WDA MJPEG帧源，否则回退到定期截图。可选捕获标志是`--interval-ms`、`--max-frames`和`--watchdog-ms`；`--max-frames`限制采样帧数，清单可能包含一个额外的最终代表性帧。默认情况下，watchdog在五分钟后最终确定并保存录制，而`--watchdog-ms 0`禁用该安全限制。输出是一个JSON清单和一个相邻的`<name>.frames`图像目录，不是编码视频或存档。清单包含相对JPEG/PNG路径，没有base64图像主体。将JSON文件和图像目录一起保留或移动，并将JSON路径传递给`assert --record`。当只关心当前屏幕时，使用普通`assert`而不带`--record`。

### 使用参考图像进行精确定位

当用户提供截图、图标、标志或参考图像并希望进行精确视觉匹配时，请优先使用`tap --locate`而不是通用的`act --prompt`。将`--locate`作为JSON传递。`prompt`描述目标，`images`提供命名的参考图像，`convertHttpImage2Base64: true`在图像URL可能无法直接被模型访问时很有用。

```bash
npx -y @midscene/ios@1 tap --locate '{
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

相同的`locate` JSON形状也适用于接受`locate`参数的其他命令。

### 断开连接

```bash
npx -y @midscene/ios@1 disconnect
```

### 消费报告文件

建议首先使用生成的HTML报告供人类阅读。它包括按步骤执行的详细信息和每个操作的回放视频，这使得理解发生了什么以及解决问题变得更容易。

如果另一个技能或工具需要消费报告，请首先使用来自同一平台CLI包的`report-tool`将其转换。对于基于LLM的工作流程，请优先使用Markdown。当报告需要以编程方式处理时，请使用JSON。

```bash
npx -y @midscene/ios@1 report-tool --action to-markdown --htmlPath ./midscene_run/report/.../index.html --outputDir ./output-markdown
npx -y @midscene/ios@1 report-tool --action split --htmlPath ./midscene_run/report/.../index.html --outputDir ./output-data
```

## 工作流程模式

由于CLI命令在调用之间是无状态的，请遵循此模式：

1. **连接**以建立会话
2. **启动目标应用并拍摄截图**以查看当前状态，确保应用已启动并在屏幕上可见。
3. **执行操作**使用`act`执行所需操作或目标驱动指令。使用`assert`进行结果屏幕状态验证，或在瞬时状态工作流程期间在专用终端中保持`record start --output ...`运行，用Ctrl+C停止，然后使用`assert --record`。
4. **断开连接**当完成时
5. **报告结果**——总结所完成的工作，展示任务期间提取的关键发现和数据，并列出任何生成的文件（截图、日志等）及其路径

## 最佳实践

1. **明确UI元素**：不要使用模糊描述，提供清晰、具体的细节。说`"右上角的设置图标"`而不是`"图标"`。
2. **尽可能描述位置**：通过描述其位置来帮助定位元素（例如，`"右上角的搜索图标"`，`"列表中的第三项"`）。
3. **切勿在后台运行**：每个场景命令必须同步运行——后台执行会破坏截图-分析-操作循环。
4. **将相关操作批量合并到单个`act`命令中**：当在同一个应用内执行连续操作时，将它们合并为一个`act`提示，而不是拆分为单独的命令。例如，"打开设置，点击Wi-Fi，并检查已连接的网络"应该是一个`act`调用，而不是三个。这减少了往返次数，避免了不必要的截图-分析周期，并且速度更快。
5. **选择正确的验证窗口**：使用`assert --prompt "..."`进行当前屏幕。对于toast、横幅、动画或过渡，在专用终端中运行`record start --output ...`，执行交互，用Ctrl+C停止录制，等待保存路径消息，然后将工件传递给`assert --record`。
6. **完成自动化任务后始终报告结果**：在完成自动化任务后，您必须主动向用户展示结果，而无需等待他们提问。这包括：(1) 用户原始问题的答案或请求任务的成果，(2) 执行期间提取或观察的关键数据，(3) 截图和其他生成的文件及其路径，(4) 采取步骤的简要总结。切勿在最后一个自动化命令后默默结束——用户期望在单次交互中获得完整结果。
7. **当提供参考图像时优先使用`tap --locate`**：如果用户分享截图、图标或标志并希望精确视觉目标，请使用`tap --locate`与多模态`locate` JSON对象（例如`{ "prompt": "...", "images": [...] }`）而不是仅依赖`act --prompt`。

**示例——警告对话框交互：**

```bash
npx -y @midscene/ios@1 act --prompt "点击删除按钮并在警告对话框中确认"
npx -y @midscene/ios@1 take_screenshot
```

**示例——表单交互：**

```bash
npx -y @midscene/ios@1 act --prompt "在用户名字段中输入'testuser'，在密码字段中输入'pass123'，然后点击登录按钮"
npx -y @midscene/ios@1 take_screenshot
```

## 提高精度（深度定位/深度思考）

当Midscene难以处理任务时，两个可选的全局标志会提供帮助。将它们放在命令中的任何位置（子命令之前或之后）；一旦设置，相关操作将默认使用它们，因此您不需要为每次调用传递参数。

- `--deep-locate`——花费额外的视觉推理轮次来精确定位目标元素。当操作与错误位置交互（位置漂移/偏移）时使用它。它适用于每个定位元素的操作，包括`tap --locate`和`act`内部的定位。
- `--deep-think`——使用更深层次的推理计划`act`（更丰富的上下文和子目标分解）。用于复杂的、多步骤的`act`指令；它只影响规划。

两者都牺牲了一点速度来换取更好的结果，并且可以组合使用。

```bash
# 更精确的元素定位（也有助于act的内部定位）
npx -y @midscene/ios@1 act --deep-locate --prompt "点击左上角的小返回箭头"

# 复杂、多步骤act的深度规划
npx -y @midscene/ios@1 act --deep-think --prompt "完成多步骤注册表单并提交"

# 组合使用
npx -y @midscene/ios@1 act --deep-locate --deep-think --prompt "打开设置，导航到显示和亮度，并开启暗黑模式"
```

## 故障排除

### WebDriverAgent未运行
**症状**：连接拒绝或超时错误。
**解决方案**：
- 确保WebDriverAgent已安装在设备上并运行。
- 如果另一个工具创建了WDA会话，请显式传递会话ID，并加上匹配的`--wda-host`和`--wda-port`。
- 请参阅[https://midscenejs.com/usage-ios.html](https://midscenejs.com/ios-getting-started.html)获取设置说明。

### 设备未找到
**症状**：未检测到设备或连接错误。
**解决方案**：
- 确保设备通过USB连接并被信任。

### API密钥问题
**症状**：身份验证或模型错误。
**解决方案**：
- 检查`.env`文件是否包含`MIDSCENE_MODEL_API_KEY=<your-key>`。
- 请参阅https://midscenejs.com/zh/model-common-config.html获取详细信息。

### `@midscene/*`依赖版本过时
**症状**：意外行为、缺失功能或版本不匹配错误。
**解决方案**：
- 检查本地版本：`npm ls @midscene/ios @midscene/core @midscene/shared`（或`pnpm why @midscene/ios`）。
- 检查最新版本：`npm view @midscene/ios version`，`npm view @midscene/core version`，`npm view @midscene/shared version`。
- 升级依赖：`npm i @midscene/ios@latest @midscene/core@latest @midscene/shared@latest`。
