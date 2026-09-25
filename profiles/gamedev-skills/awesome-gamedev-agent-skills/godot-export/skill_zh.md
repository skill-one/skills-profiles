# Godot 导出与构建 (4.x)

通过导出预设和命令行将项目转换为可运行的平台构建，并处理 Web/专用服务器的注意事项。目标为 **Godot 4.7**。

## 使用场景

- 在生成可发布构建时使用：安装导出模板、创建/编辑导出预设、从编辑器或无头 CLI (CI) 导出，或排查 Web (HTML5) 和专用服务器导出的问题。

**不使用场景**：商店发布流程 → `steam-publish`/`itch-publish`；服务器的网络代码 → `godot-multiplayer` (这项技能涵盖无头构建)。

## 核心工作流程

1. **安装与引擎版本匹配的导出模板**：编辑器菜单 > *管理导出模板* (下载)，或离线安装 `.tpz`。版本必须与编辑器完全一致。
2. **在 *项目 > 导出* 中添加导出预设**：选择平台 (Windows 桌面版、macOS、Linux、Web、Android、iOS)，设置导出路径、图标、功能以及资源包含/排除过滤器。预设保存在 `export_presets.cfg`。
3. **从编辑器导出**：使用 *导出项目* (发布) 或 *导出 PCK/ZIP*。
4. **或使用 CLI 无头导出**：用于自动化/CI，使用 `--export-release "<预设名称>" <输出路径>`。
5. **按平台**：Web 需要跨域隔离 (COOP/COEP) 用于线程；Android 需要 SDK/密钥库；macOS/iOS 需要签名用于分发。
6. **在发货前在目标平台进行冒烟测试** — 导出的构建使用 `res://` 只读；写入 `user://`。

## 模式

### 1. 无头 CLI 导出 (适合 CI)

```bash
# 预设名称必须与 *项目 > 导出* 中完全一致 (引号)。
# 从项目目录运行 (project.godot 所在目录)。
godot --headless --export-release "Windows Desktop" build/windows/game.exe
godot --headless --export-release "Linux/X11"       build/linux/game.x86_64
godot --headless --export-release "Web"             build/web/index.html

# 调试构建 (包含调试符号 / 远程调试)：
godot --headless --export-debug "Windows Desktop" build/windows/game_debug.exe

# 仅导出数据包 (无可执行文件)：
godot --headless --export-pack "Linux/X11" build/game.pck
```

### 2. 无头运行项目 (专用服务器 / 测试)

```bash
# 无窗口/GPU — 用于服务器构建或自动化运行。
godot --headless --path . res://server_main.tscn
# 在 N 次主循环迭代 (帧，非秒) 后退出 — 无头冒烟测试很方便：
godot --headless --path . --quit-after 600
```

### 3. 在运行时检测构建上下文

```gdscript
func _ready() -> void:
    if OS.has_feature("dedicated_server") or DisplayServer.get_name() == "headless":
        _start_server_only()          # 在无头服务器上跳过渲染/UI
    if OS.has_feature("web"):
        _apply_web_tweaks()
    # 自定义功能标签 (每个预设添加) 也可查询：
    # if OS.has_feature("demo"): limit_content()
```

### 4. 选择在导出后仍然存在的写入路径

```gdscript
# res:// 在导出游戏中是只读的。始终写入 user://。
func save_path() -> String:
    return "user://savegame.tres"     # 解析到 OS 应用数据目录

func _ready() -> void:
    print(OS.get_user_data_dir())     # user:// 实际所在位置
```

## 陷阱

- **"未找到导出模板"。** 模板必须与编辑器版本完全匹配 (包括 beta/rc)。升级 Godot 后通过 *管理导出模板* 重新下载。
- **CLI 中的预设名称不匹配。** `--export-release "Windows"` 失败如果预设名称为 `"Windows Desktop"`。名称对大小写和空格敏感；引号。
- **Web 构建显示空白页 / 线程错误。** 使用线程的 HTML5 构建需要服务器发送 `Cross-Origin-Opener-Policy: same-origin` 和 `Cross-Origin-Embedder-Policy: require-corp` (跨域隔离用于 `SharedArrayBuffer`)。必须通过 HTTP(S) 提供，不能作为 `file://` 打开。itch.io 有 "SharedArrayBuffer 支持" 开关。
- **在导出中运行时写入 `res://` 失败** (只读，打包)。使用 `user://`。
- **构建中缺少资源。** 非资源文件 (例如外部 `.json`, `.txt`) 不会自动包含 — 通过预设的 *资源 > 导出非资源文件过滤器* 添加 (例如 `*.json`)。
- **Android 导出需要配置**：编辑器设置中的 Android SDK/JDK 路径、调试或发布 **密钥库**，以及网络游戏所需的 `INTERNET` 权限。
- **macOS/iOS 分发需要签名/认证**；未签名的 macOS 应用会被 Gatekeeper 阻止。
- **调试与发布。** `--export-debug` 启用远程调试和调试检查；发布 `--export-release`。

## 参考

- 关于 `export_presets.cfg` 结构、所有有用的 CLI 标志、自定义功能标签、PCK/扩展补丁、加密以及按平台设置 (Android 密钥库、macOS 签名、Web 标头)，请阅读 `references/presets-and-cli.md`。

## 相关技能

- `godot-multiplayer` — 你无头导出的专用服务器代码。
- `steam-publish` / `itch-publish` — 将构建交给玩家。
- `prototype-fast` / `game-jam` — 快速 Web/桌面构建用于分享。
