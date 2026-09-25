# Peekaboo

使用 Peekaboo 检查 macOS 界面，对预期目标进行操作，并验证结果。
下方的示例使用 v4 语法。检查 `peekaboo --version` 和已安装命令的 `--help`；对于旧版本，请参考该版本的帮助文档。

## OpenClaw Bridge

OpenClaw macOS 应用程序在启用计算机控制时托管 Peekaboo Bridge，其提供者是 Peekaboo，并且 Peekaboo Bridge 已启用。通过该主机运行时，请保留现有的 OpenClaw 套接字选择：

```bash
export PEEKABOO_BRIDGE_SOCKET="${PEEKABOO_BRIDGE_SOCKET:-$HOME/Library/Application Support/OpenClaw/bridge.sock}"
peekaboo bridge status --json
```

确认所选主机和套接字是预期的。保留明确的 `PEEKABOO_BRIDGE_SOCKET` 或 `--bridge-socket` 选择。如果所需主机不可用，请报告该结果；不要清除选择或切换计算机控制提供者以使命令成功。

权限属于执行操作的过程或 Bridge 主机。除非调用者具有所需权限，否则不要传递 `--no-remote`。

## 查找已安装的命令

使用 leaf help 查看标志和目标要求，而不是在命令之间复制标志。使用 root help 发现可用命令：

```bash
peekaboo --help
peekaboo app list --help
peekaboo see --help
peekaboo press --help
peekaboo drag --help
```

v4 移除了这些旧的命令根：

| 旧命令 | V4 命令                                               |
| ------ | ---------------------------------------------------- |
| `list apps` | `app list`                                               |
| `image`    | `see --no-elements` 用于没有元素检测的像素             |
| `hotkey`   | `press` 配合 `cmd+shift+t` 等和弦                   |
| `swipe`    | `drag --from … --to …`                                   |

对于其他操作，包括点击、输入、滚动以及管理窗口或菜单，请使用 `peekaboo <command> --help`。将命令选项放在 leaf 命令之后；`--json` 请求结构化输出。

## 检查、操作、验证

从应用程序清单和目标的新视图开始：

```bash
peekaboo app list --json
peekaboo see --app Safari --window-title "Example" --annotate \
  --path /tmp/peekaboo-example.png --json
```

在操作之前，请先读取返回的元素。将操作与预期的应用程序、窗口和新鲜快照保持一致；不要重用示例元素 ID。操作后，再次检查 UI 并确认请求的结果。当窗口更改或目标过时时，请刷新观察结果。

对于没有元素检测的截图：

```bash
peekaboo see --mode screen --screen-index 0 --no-elements --retina \
  --path /tmp/peekaboo-screen.png --json
```

原始键盘和弦需要显式的前台交互或 `press` 接受的新鲜精确窗口收据。拖动始终移动共享光标，并需要 `--foreground`。当授权前台交互时：

```bash
peekaboo press cmd+shift+t --app Safari --foreground --json
peekaboo drag --from 100,500 --to 100,200 --duration 800ms --foreground --json
```

使用当前观察的实际目标和坐标。优先使用显式的持续时间单位，如 `800ms`；请参考每个命令的帮助文档以了解其选项和前提条件。

## 故障排除

- 对于移除命令的错误，请使用已安装 CLI 指定的替换命令。
- 对于主机或权限失败，请检查所选主机的 `peekaboo bridge status --json` 和 `peekaboo permissions status --json`。
- 对于目标失败，请阅读 leaf help 并使用 `see` 获取新鲜的 UI 状态。
- 在 macOS 15+ 上，私密窗口选择提示与基础屏幕录制授权是分开的，即使 Bridge 权限正确也可能出现。
