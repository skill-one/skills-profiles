# 屏幕截图捕获

每次都遵循以下保存位置规则：

1) 如果用户指定了路径，则保存到该路径。
2) 如果用户没有指定路径就要求截图，则保存到操作系统默认的截图位置。
3) 如果 Codex 需要截图进行自检，则保存到临时目录。

## 工具优先级

- 当可用时，优先使用特定于工具的截图功能（例如：为 Figma 文件使用 Figma MCP/skill，或为浏览器和 Electron 应用使用 Playwright/agent-browser 工具）。
- 当明确要求进行全系统桌面捕获，或特定工具无法满足需求时，使用此技能。
- 否则，将此技能视为没有更好集成捕获工具的桌面应用的默认选项。

## macOS 权限预检查（减少重复提示）

在 macOS 上，捕获窗口/应用之前运行一次预检查辅助程序。它会检查
屏幕录制权限，解释为什么需要它，并在一个地方请求它。

辅助程序将 Swift 的模块缓存路由到 `$TMPDIR/codex-swift-module-cache`，以避免额外的沙盒模块缓存提示。

```bash
bash <path-to-skill>/scripts/ensure_macos_permissions.sh
```

为了避免多次沙盒批准提示，当可能时，将预检查 + 捕获合并为一条命令：

```bash
bash <path-to-skill>/scripts/ensure_macos_permissions.sh && \
python3 <path-to-skill>/scripts/take_screenshot.py --app "Codex"
```

对于 Codex 检查运行，将输出保存在临时目录：

```bash
bash <path-to-skill>/scripts/ensure_macos_permissions.sh && \
python3 <path-to-skill>/scripts/take_screenshot.py --app "<App>" --mode temp
```

使用捆绑的脚本以避免重新推导特定于 OS 的命令。

## macOS 和 Linux（Python 辅助程序）

从仓库根目录运行辅助程序：

```bash
python3 <path-to-skill>/scripts/take_screenshot.py
```

常见模式：

- 默认位置（用户要求“一个截图”）：

```bash
python3 <path-to-skill>/scripts/take_screenshot.py
```

- 临时位置（Codex 视觉检查）：

```bash
python3 <path-to-skill>/scripts/take_screenshot.py --mode temp
```

- 明确位置（用户提供了路径或文件名）：

```bash
python3 <path-to-skill>/scripts/take_screenshot.py --path output/screen.png
```

- 通过应用名称捕获应用/窗口（仅限 macOS；子字符串匹配也可以；捕获所有匹配的窗口）：

```bash
python3 <path-to-skill>/scripts/take_screenshot.py --app "Codex"
```

- 应用内特定窗口标题（仅限 macOS）：

```bash
python3 <path-to-skill>/scripts/take_screenshot.py --app "Codex" --window-name "Settings"
```

- 捕获前列出匹配的窗口 ID（仅限 macOS）：

```bash
python3 <path-to-skill>/scripts/take_screenshot.py --list-windows --app "Codex"
```

- 像素区域（x,y,w,h）：

```bash
python3 <path-to-skill>/scripts/take_screenshot.py --mode temp --region 100,200,800,600
```

- 聚焦/活动窗口（仅捕获最前面的窗口；使用 `--app` 捕获所有窗口）：

```bash
python3 <path-to-skill>/scripts/take_screenshot.py --mode temp --active-window
```

- 特定窗口 ID（在 macOS 上使用 `--list-windows` 发现 ID）：

```bash
python3 <path-to-skill>/scripts/take_screenshot.py --window-id 12345
```

脚本每次捕获打印一个路径。当多个窗口或显示器匹配时，它打印多个路径（每行一个），并添加后缀如 `-w<windowId>` 或 `-d<display>`。使用图像查看工具按顺序查看每个路径，并且仅在需要或被要求时才操作图像。

### 工作流示例

- “查看 <App> 并告诉我你看到了什么”：捕获到临时目录，然后按顺序查看每个打印的路径。

```bash
bash <path-to-skill>/scripts/ensure_macos_permissions.sh && \
python3 <path-to-skill>/scripts/take_screenshot.py --app "<App>" --mode temp
```

- “Figma 的设计与实现不匹配”：首先使用 Figma MCP/skill 捕获设计，然后使用此技能（通常捕获到临时目录）捕获运行的应用并比较原始截图，在任何操作之前。

### 多显示器行为

- 在 macOS 上，全屏捕获在多个显示器连接时为每个显示器保存一个文件。
- 在 Linux 和 Windows 上，全屏捕获使用虚拟桌面（所有显示器在一个图像中）；当需要时使用 `--region` 隔离单个显示器。

### Linux 前提条件和选择逻辑

辅助程序自动选择第一个可用的工具：

1) `scrot`
2) `gnome-screenshot`
3) ImageMagick `import`

如果没有可用，则提示用户安装其中一个并重试。

区域协调需要 `scrot` 或 ImageMagick `import`。

`--app`、`--window-name` 和 `--list-windows` 仅限 macOS。在 Linux 上，使用
`--active-window` 或在可用时提供 `--window-id`。

## Windows（PowerShell 辅助程序）

运行 PowerShell 辅助程序：

```powershell
powershell -ExecutionPolicy Bypass -File <path-to-skill>/scripts/take_screenshot.ps1
```

常见模式：

- 默认位置：

```powershell
powershell -ExecutionPolicy Bypass -File <path-to-skill>/scripts/take_screenshot.ps1
```

- 临时位置（Codex 视觉检查）：

```powershell
powershell -ExecutionPolicy Bypass -File <path-to-skill>/scripts/take_screenshot.ps1 -Mode temp
```

- 明确路径：

```powershell
powershell -ExecutionPolicy Bypass -File <path-to-skill>/scripts/take_screenshot.ps1 -Path "C:\Temp\screen.png"
```

- 像素区域（x,y,w,h）：

```powershell
powershell -ExecutionPolicy Bypass -File <path-to-skill>/scripts/take_screenshot.ps1 -Mode temp -Region 100,200,800,600
```

- 活动窗口（首先要求用户聚焦它）：

```powershell
powershell -ExecutionPolicy Bypass -File <path-to-skill>/scripts/take_screenshot.ps1 -Mode temp -ActiveWindow
```

- 特定窗口句柄（仅当提供时）：

```powershell
powershell -ExecutionPolicy Bypass -File <path-to-skill>/scripts/take_screenshot.ps1 -WindowHandle 123456
```

## 直接 OS 命令（备用方案）

当无法运行辅助程序时使用这些命令。

### macOS

- 全屏到特定路径：

```bash
screencapture -x output/screen.png
```

- 像素区域：

```bash
screencapture -x -R100,200,800,600 output/region.png
```

- 特定窗口 ID：

```bash
screencapture -x -l12345 output/window.png
```

- 交互式选择或窗口选择：

```bash
screencapture -x -i output/interactive.png
```

### Linux

- 全屏：

```bash
scrot output/screen.png
```

```bash
gnome-screenshot -f output/screen.png
```

```bash
import -window root output/screen.png
```

- 像素区域：

```bash
scrot -a 100,200,800,600 output/region.png
```

```bash
import -window root -crop 800x600+100+200 output/region.png
```

- 活动窗口：

```bash
scrot -u output/window.png
```

```bash
gnome-screenshot -w -f output/window.png
```

## 错误处理

- 在 macOS 上，首先运行 `bash <path-to-skill>/scripts/ensure_macos_permissions.sh` 请求屏幕录制权限。
- 如果看到“沙盒中阻止屏幕捕获检查”、“无法从显示器创建图像”或在沙盒运行中遇到 Swift `ModuleCache` 权限错误，请以提升权限重新运行命令。
- 如果 macOS 应用/窗口捕获没有匹配项，运行 `--list-windows --app "AppName"` 并重试，使用 `--window-id`，并确保应用在屏幕上可见。
- 如果 Linux 区域/窗口捕获失败，使用 `command -v scrot`、`command -v gnome-screenshot` 和 `command -v import` 检查工具可用性。
- 如果保存到操作系统默认位置在沙盒中因权限错误失败，请以提升权限重新运行命令。
- 始终在响应中报告保存的文件路径。
