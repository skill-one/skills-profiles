# 桌面电脑自动化

> **关键规则 — 违反规则将导致工作流程中断：**
>
> 1. **切勿在后台运行场景中的命令。** 每个命令必须同步运行，以便你在决定下一步操作之前能够读取其输出（尤其是截图）。后台执行会破坏截图-分析-执行循环。
> 2. **一次只运行一个场景中的命令。** 等待前一个命令完成，读取截图，然后决定下一步操作。切勿将多个命令串联在一起。
> 3. **为每个命令留出足够的时间完成。** 场景中的命令涉及 AI 推理和屏幕交互，这可能比典型的 shell 命令花费更长的时间。典型的命令大约需要 1 分钟；复杂的 `act` 命令可能需要更长时间。
> 4. **始终在完成前报告任务结果。** 完成自动化任务后，你必须主动向用户总结结果——包括发现的关键数据、完成的操作、拍摄的截图以及任何相关发现。切勿在最后一个自动化步骤后默默结束；用户期望在单个交互中获得完整响应。
> 5. **仅最小化窗口，除非明确要求，否则切勿关闭它们。** 当你需要将窗口移开或使其不碍事时，请最小化它而不是关闭它。除非用户明确要求，否则不要关闭任何应用程序或窗口。

使用 `npx -y @midscene/computer@1` 控制你的桌面（macOS、Windows、Linux）。每个 CLI 命令都直接映射到 MCP 工具——你（AI 代理）作为大脑，决定要采取哪些操作，基于截图。

## `act` 能做什么

在桌面的单个 `act` 调用中，Midscene 可以移动鼠标、点击、双击、右击、拖动项目、输入或清除文本、滚动、按单个键或键盘快捷键，并在所选显示器的任何可见内容上进行多步骤交互。

## 前置条件

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

示例： Doubao Seed 2.0 Lite

```bash
MIDSCENE_MODEL_API_KEY="your-doubao-api-key"
MIDSCENE_MODEL_NAME="doubao-seed-2-0-lite"
MIDSCENE_MODEL_BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
MIDSCENE_MODEL_FAMILY="doubao-seed"
```

常用模型：Doubao Seed 2.0 Lite、Qwen 3.5、Zhipu GLM-4.6V、Gemini-3-Pro、Gemini-3-Flash。

如果未配置模型，请提示用户进行设置。有关受支持的提供者的信息，请参阅 [模型配置](https://midscenejs.com/model-common-config)。

## 命令

### 连接到桌面

```bash
npx -y @midscene/computer@1 connect
npx -y @midscene/computer@1 connect --displayId <id>
```

### 通过 RDP 连接

使用 RDP 模式来驱动 **远程 Windows 桌面** 而不是本地计算机。提供 `--host` 会将 `connect` 切换到 RDP 并通过 `@midscene/computer` 随附的 RDP 帮助二进制文件路由所有后续命令（`act`、`tap`、`take_screenshot`、`assert`、`disconnect`）。本地鼠标/键盘**不会**被操作。

最小示例：

```bash
npx -y @midscene/computer@1 connect \
  --host rdp.example.com \
  --username Administrator \
  --password "$RDP_PASSWORD"
```

`connect` 的所有 RDP 选项（当设置 `--host` 时激活 RDP 模式；其他标志是可选的）：

- `--host <fqdn-or-ip>` — RDP 主机。进入 RDP 模式时需要。
- `--port <number>` — RDP 端口（默认 `3389`）。
- `--username <user>` — RDP 用户账户。
- `--password <secret>` — RDP 密码。最好从环境变量、密钥管理器或交互式提示中读取；切勿将其粘贴到共享脚本中。
- `--domain <domain>` — Active Directory / NTLM 域。
- `--security-protocol <auto|tls|nla|rdp>` — 安全协议协商。默认为 `auto`。
- `--ignore-certificate` — 跳过 TLS 证书验证。仅用于信任的开发主机，具有自签名证书。
- `--admin-session` — 连接到管理员/控制台会话（相当于 `mstsc /admin`）。
- `--desktop-width <px>` 和 `--desktop-height <px>` — **请求**特定的远程桌面分辨率。实际大小是 RDP 服务器协商回的大小；例如，针对将 `1280x720` 固定为主机的请求 `1024x768` 将最终得到 `1280x720`。连接后，使用 `listdisplays --host ... --username ... --password ...` 确认协商的大小。

特定于 RDP 模式的注意事项：

- `--displayId` 和 `--headless` 在 RDP 模式下**会被忽略**。连接的 RDP 会话始终暴露一个虚拟显示，其大小由服务器协商决定。
- 存在两个不同的显示列表命令，行为不同——选择正确的命令：
  - `list_displays`（带下划线，平台工具）——仅枚举**本地**物理显示。不接受 RDP 标志。RDP 连接后无用处。
  - `listdisplays`（不带下划线，操作工具）——接受与 `connect`/`take_screenshot`/等相同的 RDP 标志。在 RDP 模式下，它返回协商的虚拟显示，例如 `[{ "id": "...", "name": "RDP 10.70.86.26:3389 (1280x720)", "primary": true }]`。使用此命令来验证实际分辨率。
- RDP 传输使用内置在 `@midscene/computer` 中的原生帮助二进制文件。如果你看到 `RDP helper binary not found` 错误，你的安装中可能缺少可选的 `bin/<platform>/rdp-helper`——重新安装软件包或解压一个新鲜的 tarball。
- 将 RDP 凭据视为密钥：不要将包含 `--password` 的 `.env` 文件提交到存储库；最好在当前 shell 中使用 `export RDP_PASSWORD=...` 并将其引用为 `--password "$RDP_PASSWORD"`。
- **延迟预期**：每个 CLI 调用都是一个全新的 node 进程，因此每个命令都会重新建立 RDP 会话。大致预算：
  - `connect` / `take_screenshot` / `keyboardpress` / `scroll`：~5 秒（node 启动 + RDP TLS+NLA 握手 + 第一帧）。
  - `act` / `assert` / `tap --locate`：~5 秒 + AI 推理 + 任何计划的子操作；典型交互的端到端时间预期为 8–20 秒。
  - RDP 握手本身约为 700 毫秒；其余是 CLI 形式的不可避免冷启动成本。
- **连接失败诊断**：当 `connect` 失败时，stderr 的第一行是可操作的错误（例如 `connect_failed: Failed to connect to RDP server: ERRCONNECT_LOGON_FAILURE: Logon failed.`）。后续的堆栈跟踪是诊断噪音——读取第一行，然后检查凭据/网络。常见的 `ERRCONNECT_*` 原因：
  - `LOGON_FAILURE` — 用户名/密码/域错误。
  - `CONNECT_TRANSPORT_FAILED` — 主机无法访问或 RDP 端口被阻止。使用 `nc -zv <host> 3389` 进行验证。
  - `TLS_CONNECT_FAILED` — TLS 握手被拒绝。对于自签名的开发主机，尝试 `--ignore-certificate`，或者固定 `--security-protocol nla`。

连接 `--host ...` 成功后，其余工作流（`act`、`tap --locate`、`assert`、`take_screenshot`、`listdisplays`、`report-tool`、`disconnect`）与本地模式相同——只需记得将相同的 `--host`/`--username`/`--password`/`--ignore-certificate` 标志传递给每个后续命令，因为每个 CLI 调用都是无状态的并重新连接。

### 列出显示

```bash
npx -y @midscene/computer@1 list_displays
```

### 拍摄截图

```bash
npx -y @midscene/computer@1 take_screenshot
```

拍摄截图后，读取保存的图像文件以了解当前屏幕状态，在决定下一步操作之前。

### 执行操作

使用 `act` 与电脑交互并获取结果。它自动处理所有 UI 交互，内部点击、输入、滚动、等待和导航——因此你应该将复杂的高级任务作为一个整体给出，而不是将其拆分为小步骤。用自然语言描述**你想做什么以及期望的效果**：

```bash
# 具体指令
npx -y @midscene/computer@1 act --prompt "在搜索框中输入 hello world 并按 Enter"
npx -y @midscene/computer@1 act --prompt "将文件图标拖到废纸篓"

# 或目标驱动指令
npx -y @midscene/computer@1 act --prompt "使用 Chrome 浏览器搜索上海的天气，告诉我结果"
```

### 断言当前屏幕状态

使用 `assert` 来验证当前屏幕是否满足自然语言条件。它不执行 UI 操作；它检查可见的屏幕状态，并且仅在断言为真时通过。用于验证、QA 检查以及 `act` 完成后的最终状态验证。

```bash
npx -y @midscene/computer@1 assert --prompt "有一个登录按钮可见"
npx -y @midscene/computer@1 assert --prompt "活动窗口显示保存确认消息"
npx -y @midscene/computer@1 assert --displayId 1 --prompt "文件选择器已打开"
```

默认情况下，失败的断言会抛出 AI 生成的理由。传递 `--message` 以抛出自定义错误消息，这对于在 QA 和 CI 日志中展示预期结果非常有用。

```bash
npx -y @midscene/computer@1 assert \
  --prompt "导出完成对话框可见" \
  --message "点击保存后应该完成导出"
```

当断言需要与参考图像（图标、标志、截图）进行比较时，传递 `--image` 用于 URL/路径，`--image-name` 用于其显示名称。每个 `--image` 可以是 http(s) 链接、`data:` URI 或本地文件路径。当你需要附加多个图像时，请按匹配的顺序重复这两个标志。当模型无法直接访问 URL 时，添加 `--convertHttpImage2Base64 true`。需要 `@midscene/computer@1.9.0+`。

```bash
npx -y @midscene/computer@1 assert \
  --prompt "活动窗口与提供的参考截图匹配" \
  --image "https://example.com/reference.png" \
  --image-name "reference" \
  --convertHttpImage2Base64 true

# 或使用本地文件
npx -y @midscene/computer@1 assert \
  --prompt "可见图标与提供的标志匹配" \
  --image "./fixtures/logo.png" \
  --image-name "logo"

# 多个参考图像——按顺序配对 `--image` 和 `--image-name`
npx -y @midscene/computer@1 assert \
  --prompt "活动窗口与图标和标志都匹配" \
  --image "./fixtures/icon.png" --image-name "icon" \
  --image "./fixtures/logo.png" --image-name "logo"
```

### 使用参考图像进行精确定位

当用户提供一个截图、图标、标志或参考图像，并希望进行精确的视觉匹配时，请优先使用 `tap --locate` 而不是通用的 `act --prompt`。将 `--locate` 作为 JSON 传递。`prompt` 描述目标，`images` 提供命名的参考图像，`convertHttpImage2Base64: true` 在图像 URL 可能无法被模型直接访问时很有用。

```bash
npx -y @midscene/computer@1 tap --locate '{
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
npx -y @midscene/computer@1 disconnect
```

### 消费报告文件

建议首先使用 HTML 报告供人类阅读。它包括每一步执行细节和每个操作的回放视频，这使得理解发生的事情和解决问题变得更容易。

如果另一个技能或工具需要消费报告，请首先使用同一平台 CLI 软件包中的 `report-tool` 进行转换。对于基于 LLM 的工作流，请优先使用 Markdown。当报告需要被程序处理时，请使用 JSON。

```bash
npx -y @midscene/computer@1 report-tool --action to-markdown --htmlPath ./midscene_run/report/.../index.html --outputDir ./output-markdown
npx -y @midscene/computer@1 report-tool --action split --htmlPath ./midscene_run/report/.../index.html --outputDir ./output-data
```

## 工作流模式

由于 CLI 命令在调用之间是无状态的，请遵循此模式：

1. **连接**以建立会话
2. **健康检查**——观察 `connect` 命令的输出。如果 `connect` 已经执行了健康检查（截图和鼠标移动测试），则不需要额外的检查。如果 `connect` 没有执行健康检查，请手动执行一个：拍摄截图并验证它成功，然后移动鼠标到随机位置（`act --prompt "将鼠标移动到随机位置"`）并验证它成功。如果任何步骤失败，请在继续之前停止并解决问题。只有在两个检查都无错误地通过后，才能继续下一步。

3. **启动目标应用程序并拍摄截图**以查看当前状态，确保应用程序已启动并显示在屏幕上。
4. **使用 `act` 执行操作**以执行所需操作或目标驱动指令，并在需要验证结果屏幕状态时使用 `assert`。
5. **完成时断开连接**
6. **报告结果**——总结所完成的工作，展示任务期间提取或观察的关键发现和数据，并列出生成的文件（截图、日志等）及其路径

## 最佳实践

1. **始终先运行健康检查**：连接后，观察 `connect` 命令的输出。如果 `connect` 已经执行了健康检查（截图和鼠标移动测试），则不需要额外的检查。如果它没有，请手动执行一个：拍摄截图并移动鼠标到随机位置。两者都必须成功（无错误）才能继续任何进一步的操作。这可以尽早捕获环境问题。
2. **在使用此技能之前将目标应用程序带到前台**：为了最佳效率，使用其他方式（例如 macOS 上的 `open -a <AppName>`，Windows 上的 `start <AppName>`）**在**调用任何场景命令之前将应用程序带到前台。然后拍摄截图以确认应用程序实际上在前台。只有在视觉确认后，你才能继续使用此技能进行 UI 自动化。避免通过 midscene 使用 Spotlight、开始菜单搜索或其他基于启动器的操作——它们涉及临时 UI、多个 AI 推理步骤，并且速度明显较慢。
3. **关于 UI 元素要具体**：不要使用模糊的描述，提供清晰、具体的细节。说 `"左上角黄色最小化按钮在 Safari 窗口中"` 而不是 `"按钮"`。
4. **尽可能描述位置**：通过描述其位置来帮助定位元素（例如 `"菜单栏右上角的图标"`，`"左侧边栏中的第三项"`）。
5. **切勿在后台运行**：每个场景命令必须同步运行——后台执行会破坏截图-分析-执行循环。
6. **检查多个显示器**：如果你启动了应用程序但无法在截图中看到它，应用程序窗口可能已打开在不同的显示器上。使用 `list_displays` 检查可用显示器。你有两个选择：要么将应用程序窗口移动到当前显示器，要么使用 `connect --displayId <id>` 切换到应用程序所在的显示器。
7. **将相关的操作批量到一个单独的 `act` 命令中**：在同一个应用程序内执行连续操作时，将它们合并为一个 `act` 提示，而不是拆分为单独的命令。例如，"搜索 X，点击第一个结果，然后滚动以查看更多详细信息" 应该是一个单一的 `act` 调用，而不是三个。这减少了往返次数，避免了不必要的截图-分析周期，并且速度明显更快。
8. **在 macOS 上运行前设置 `PATH`**：在 macOS 上，如果 `PATH` 不完整，某些命令（例如 `system_profiler`）可能找不到。在运行任何 midscene 命令之前，请确保 `PATH` 包括标准系统目录：
   ```bash
   export PATH="/usr/sbin:/usr/bin:/bin:/sbin:$PATH"
   ```
   这可以防止由于缺少系统实用程序而导致的截图失败。
9. **使用 `assert` 进行验证**：当目标是确认屏幕状态为真时，使用 `assert --prompt "..."` 而不是 `act` 提示。保持断言可观察且具体，例如 `"保存对话框已打开"` 或 `"导出完成消息可见"`。
10. **完成时始终报告结果**：完成自动化任务后，你必须主动向用户展示结果，不要等待他们提问。这包括： (1) 用户原始问题的答案或请求任务的成果， (2) 执行期间提取或观察的关键数据， (3) 截图和其他生成的文件及其路径， (4) 采取步骤的简要总结。**不要**在最后一个自动化命令后默默结束——用户期望在单个交互中获得完整结果。
11. **当提供参考图像时，优先使用 `tap --locate`**：如果用户分享截图、图标或标志并希望进行精确的视觉匹配，请使用 `tap --locate` 与多模态的 `locate` JSON 对象（例如 `{ "prompt": "...", "images": [...] }`）而不是仅依赖 `act --prompt`。

**示例——上下文菜单交互：**

```bash
npx -y @midscene/computer@1 act --prompt "右击文件图标并从上下文菜单中选择删除"
npx -y @midscene/computer@1 take_screenshot
```

**示例——下拉菜单：**

```bash
npx -y @midscene/computer@1 act --prompt "打开文件菜单并点击新建窗口"
npx -y @midscene/computer@1 take_screenshot
```

## 提高精度（深度定位 / 深度思考）

当 Midscene 在任务中遇到困难时，有两个可选的全局标志有助于提高效果。将它们放在命令中的任何位置（子命令之前或之后）；一旦设置，相关的操作将默认使用它们，因此你不需要为每次调用传递参数。

- `--deep-locate` — 花费额外的视觉推理轮次来精确定位目标元素。当操作与错误的位置交互（位置漂移/偏移）时使用它。它适用于每个定位元素的操作，包括 `tap --locate` 和 `act` 内部发生的定位。
- `--deep-think` — 使用更深入的推理来规划 `act`（更丰富的上下文和子目标分解）。用于复杂的、多步骤的 `act` 指令；它仅影响规划。

两者都牺牲了一点速度来换取更好的结果，并且可以组合使用。

```bash
# 更精确的元素定位（也有助于 act 内部的定位）
npx -y @midscene/computer@1 act --deep-locate --prompt "点击窗口左上角的微小红色关闭按钮"

# 复杂的、多步骤 act 的深度规划
npx -y @midscene/computer@1 act --deep-think --prompt "打开导出对话框，选择 PDF，并保存到桌面"

# 组合使用两者
npx -y @midscene/computer@1 act --deep-locate --deep-think --prompt "打开偏好设置并切换到高级选项卡"
```

## 故障排除

### macOS：无访问权限的辅助功能
你的终端应用程序没有辅助功能访问权限：
1. 打开 **系统设置 > 隐私与安全 > 辅助功能**
2. 添加你的终端应用程序并启用它
3. 授予权限后重启你的终端应用程序

### macOS：找不到 Xcode 命令行工具
```bash
xcode-select --install
```

### API 密钥未设置
检查 `.env` 文件是否包含 `MIDSCENE_MODEL_API_KEY=<your-key>`。

### macOS：使用 `system_profiler` 拍摄截图失败，找不到
如果 `take_screenshot` 因错误（例如 `system_profiler: command not found`）而失败，`PATH` 环境变量可能不完整。通过运行以下命令修复它：
```bash
export PATH="/usr/sbin:/usr/bin:/bin:/sbin:$PATH"
```
然后重试截图命令。

### macOS：截图返回黑屏
如果 `take_screenshot` 返回完全黑色的图像，Mac 可能处于**锁定状态**（例如屏幕处于登录/锁定窗口）。这是一个系统级限制——macOS 禁止在会话锁定时捕获屏幕内容，因此应用程序级别没有解决方法。

**推荐修复方案**：使用**屏幕保护程序**而不是锁定屏幕。屏幕保护程序保持用户会话活动且未锁定，允许正常捕获屏幕。

1. 打开 **系统设置 > 锁定屏幕**
2. 将 "屏幕保护程序开始或显示器关闭后需要密码" 设置为更长的延迟（或关闭此设置以在自动化期间禁用密码）
3. 可选地，配置屏幕保护程序，在 **系统设置 > 屏幕保护程序** 下，以便显示器在非活动后仍然变暗，而不会锁定

### AI 无法找到元素
1. 拍摄截图以验证元素实际上可见
2. 使用更具体的描述（包括颜色、位置、周围文本）
3. 确保元素没有被另一个窗口遮挡

### `@midscene/*` 依赖版本过时
- 检查本地版本：`npm ls @midscene/computer @midscene/core @midscene/shared`（或 `pnpm why @midscene/computer`）。
- 检查最新版本：`npm view @midscene/computer version`, `npm view @midscene/core version`, `npm view @midscene/shared version`.
- 升级依赖：`npm i @midscene/computer@latest @midscene/core@latest @midscene/shared@latest`.
