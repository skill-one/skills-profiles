# iOS 调试代理

## 概述
使用 XcodeBuildMCP 在已启动的 iOS 模拟器上构建和运行当前项目方案，交互 UI 并捕获日志。优先使用 MCP 工具进行模拟器控制、日志记录和视图检查。

## 核心工作流程
除非用户要求更具体的操作，否则请按此顺序执行。

### 1) 发现已启动的模拟器
- 调用 `mcp__XcodeBuildMCP__list_sims` 并选择状态为 `Booted` 的模拟器。
- 如果没有已启动的模拟器，请提示用户启动一个（除非用户要求自动启动）。

### 2) 设置会话默认值
- 调用 `mcp__XcodeBuildMCP__session-set-defaults` 并传入：
  - 仓库使用的 `projectPath` 或 `workspacePath`
  - 当前应用的 `scheme`
  - 已启动设备的 `simulatorId`
  - 可选：`configuration: "Debug"`, `useLatestOS: true`

### 3) 构建 + 运行（按需）
- 调用 `mcp__XcodeBuildMCP__build_run_sim`。
- **如果构建失败**，检查错误输出并重试（可选使用 `preferXcodebuild: true`）或在尝试任何 UI 交互前升级至用户。
- **构建成功后**，通过调用 `mcp__XcodeBuildMCP__describe_ui` 或 `mcp__XcodeBuildMCP__screenshot` 验证应用是否已启动，然后再进行 UI 交互。
- 如果应用已构建且仅请求启动，使用 `mcp__XcodeBuildMCP__launch_app_sim`。
- 如果 bundle id 未知：
  1) `mcp__XcodeBuildMCP__get_sim_app_path`
  2) `mcp__XcodeBuildMCP__get_app_bundle_id`

## UI 交互与调试
在要求检查或交互运行中的应用时使用这些命令。

- **描述 UI**：在点击或滑动前调用 `mcp__XcodeBuildMCP__describe_ui`。
- **点击**：`mcp__XcodeBuildMCP__tap`（优先使用 `id` 或 `label`；仅在必要时使用坐标）。
- **输入**：在聚焦字段后调用 `mcp__XcodeBuildMCP__type_text`。
- **手势**：使用 `mcp__XcodeBuildMCP__gesture` 执行常见滚动和边缘滑动。
- **截图**：调用 `mcp__XcodeBuildMCP__screenshot` 进行视觉确认。

## 日志与控制台输出
- 启动日志：使用 `mcp__XcodeBuildMCP__start_sim_log_cap` 并传入应用 bundle id。
- 停止日志：调用 `mcp__XcodeBuildMCP__stop_sim_log_cap` 并总结重要行。
- 对于控制台输出，设置 `captureConsole: true` 并在需要时重新启动。

## 故障排除
- 如果构建失败，询问是否使用 `preferXcodebuild: true` 重试。
- 如果启动了错误的应用，请确认方案和 bundle id。
- 如果 UI 元素无法点击，在布局更改后重新运行 `describe_ui`。
