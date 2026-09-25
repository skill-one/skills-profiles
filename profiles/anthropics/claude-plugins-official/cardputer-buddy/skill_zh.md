# Cardputer Buddy 应用程序包

本地 `build-with-claude` 克隆中的 `buddy/` 目录是 MicroPython 有效载荷，`m5-onboard` 会将其安装到 `/flash/` 上。在克隆的目录中工作。

## 设备布局

```
/flash/
├── main.py              启动器菜单（替换 UIFlow 的启动流程）
├── buddy_*.py           共享库（BLE、UI、状态、协议、字符）
├── burst_frames.py      精灵帧
└── apps/
    ├── claude_buddy.py  BLE 客户端 → Claude 桌面的硬件助手
    ├── hello_cardputer.py
    └── snake.py
```

`main.py` 在启动时扫描 `/flash/apps/` 并将每个 `.py` 文件列为主要菜单项。将文件放入 `buddy/device/apps/` 目录，推送后，它将在下次启动时出现。

## 添加应用程序

参考 `buddy/device/apps/hello_cardputer.py` — 最小的键盘轮询、字体和退出约定示例。然后推送而不重新刷写：

```bash
python3 onboard/scripts/install_apps.py --port <PORT> --src buddy
```

`<PORT>` 是 `detect.py` 最后运行报告的端口（例如 `/dev/cu.usbmodem1101`、`/dev/ttyACM0`、`COM3`）。

## 开发循环工具 (`buddy/scripts/`)

```bash
# 通过 USB-串行推送文件子集
python3 buddy/scripts/push.py --port <PORT> --files apps/snake.py

# 查看设备日志
python3 buddy/scripts/tail_serial.py --port <PORT>

# 单次 REPL 执行
python3 buddy/scripts/repl_run.py --port <PORT> --script "import os; print(os.listdir('/flash'))"
```
