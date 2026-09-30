---
name: m5-onboard
description: 为刚插入的M5Stack ESP32设备（Cardputer、Cardputer-Adv、Core、CoreS3、Stick）提供端到端引导——检测USB连接，刷写UIFlow 2.0固件，并安装Claude Buddy MicroPython应用包。用户每次插入设备或需要刷写/配置/重置M5Stack或ESP32主板时，或输入“m5-onboard go”时均可使用。
---

# M5Stack 初始化

此技能可自动执行 M5Stack ESP32 设备的完整冷启动工作流程：检测 USB、识别型号、刷写 UIFlow 2.0，并将 MicroPython 应用程序包推送到 `/flash/` 目录，以便设备启动到用户软件。我们提供的应用程序（Claude Buddy、Snake、Hello）通过 BLE 或 USB 进行通信。该工作流程可在 macOS、Linux 和 Windows 上运行；该技能是基于 M5Stack Basic v2.6（CH9102 桥接器、ESP32-D0WDQ6-V3、16 MB 闪存）开发的，并已推广以涵盖 Core 系列，其中 Cardputer-Adv（ESP32-S3、原生 USB）是当前默认目标。

## 脚本存放位置

此技能作为 `cwc-makers` 插件的一部分提供，但可执行脚本和 `buddy/` 应用程序包位于 https://github.com/moremas/build-with-claude 的本地克隆中（`/maker-setup` 命令创建此克隆）。从该克隆的 `onboard/` 目录中运行每个 `scripts/*.py` 调用，以便 `--apps buddy` 解析到兄弟目录 `buddy/device/` 的有效负载。

## 使用场景

当用户插入 M5Stack 设备并希望对其进行配置时，请使用此技能。决策树如下：

- **全新/未知设备** → 运行 `onboard.py --apps buddy` 端到端（检测 → 识别 → 刷写 → 安装应用程序）。这是默认路径。
- **已刷写设备，用户只想安装/刷新应用程序** → 运行 `install_apps.py --src buddy`（或任何 `--src <路径>` 到 `.py` 文件目录）。
- **已刷写设备，感觉某些功能损坏** → 运行 `smoke_test.py`（I2C + LCD + 扬声器 + 按钮检查）。
- **用户想知道总线上的内容 / 设备能做什么** → `smoke_test.py`。

如果插入多个设备，请询问要针对哪个端口进行操作——不要猜测。如果用户正在配置他们之前使用过的设备（例如“与上次相同”或“另一个 Buddy”），除非他们另有说明，否则默认为 `--apps buddy`。

### 假设的变体

此技能所在的设备主要配置 **Cardputer-Adv** 板，因此 `onboard.py` 现在默认为 `--variant cardputer-adv`。实际上这意味着：

- 如果用户没有提及型号，则使用默认值。他们几乎肯定持有 Cardputer-Adv。
- 如果用户说“Cardputer”（没有“Adv”），请询问——这两个型号共享相同的形状因子，但需要不同的固件镜像，刷写错误的固件会导致设备循环重启。
- 如果用户指定任何其他板（“Core2”、“CoreS3”、“Basic”、“Fire”），请显式传递匹配的 `--variant`——默认值不适用。
- 无论哪种情况，芯片都是 ESP32-S3，并且 `detect.py` 在刷写 UIFlow 之前无法区分 Cardputer 和 Cardputer-Adv（相同的原生 USB-JTAG VID，没有预刷写 I2C 探测）。因此，这是一个用户意图问题，而不是硬件指纹问题。

## 工作流程

主要的协调器是 `scripts/onboard.py`。它按顺序驱动子脚本并处理它们之间的交接（等待重启、捕获 MAC 地址、报告进度）。除非用户要求部分运行，否则请直接调用它，而不是自己拼接子脚本。

默认的配置命令（全新的 Cardputer-Adv，安装 buddy 套件）：

```
python3 scripts/onboard.py --apps buddy
```

**如何从 Claude Code 的 Bash 工具中调用此命令。** 不要将 `onboard.py` 作为前台 Bash 命令调用。Bash 工具捕获输出，并且不会在命令退出后将输出流回助手——此命令运行 2–3 分钟。这种沉默看起来与挂起相同，并且助手通常会在按钮舞蹈提示到达用户之前放弃。相反，始终使用 `run_in_background: true`、`tee` 到日志文件，然后使用监视工具（或通过 Read 定期 `tail`）实时向用户显示阶段横幅、心跳和提示。`2>&1` 不是解决方案——所有进度都写入 stderr，终端显示良好。解决方案是流式语义，而不是重定向。有效模式：

```
# 启动（后台、tee 日志）：
python3 scripts/onboard.py --apps buddy 2>&1 | tee /tmp/m5-onboard.log

# 监视（突出显示关键事件，而不会淹没字节进度垃圾信息）：
tail -f /tmp/m5-onboard.log | grep -E --line-buffered \
  "^====|heartbeat|Heads up|Enter download mode|download mode!|rebooted into UIFlow|Manual reset|DONE|ERROR|Error|Traceback|FAIL|failed|No USB|not detected|Attempt [0-9]|Device already in download|Download mode port|Post-flash port|Waiting for device"
```

### 向用户传达物理步骤（必需）

刷写阶段**在没有手动按键操作的原生 USB 板上无法继续**——没有软件路径。当监控日志显示 `Enter download mode`（或脚本在 FLASH 阶段似乎在等待时），您必须停止并告诉用户在 **Cardputer 的背面**，用自己的话，在继续之前执行以下操作：

1. 按住并**保持** **G0** 按钮
2. 在按住 G0 的同时，短暂按住并释放 **RST** 按钮
3. 继续按住 G0 大约一秒钟，然后释放它
4. 屏幕应完全变暗——这意味着下载模式已激活

如果设备重启进入 UIFlow 而不是变暗，请告诉用户 G0 释放得太早，并让他们按住更长时间。不要继续，不要重试脚本，也不要尝试软件解决方案，直到用户确认屏幕变暗——否则刷写将不会开始。对于任何后续的 `Manual reset` 提示，也适用相同的物理步骤：传达物理步骤并等待用户。

直接在终端中运行 `onboard.py` 的用户（不是通过 Claude Code）将看到所有实时输出——那里不需要任何更改。

如果省略 `--port`，`detect.py` 在所有三个操作系统上选择最可能的候选者：原生 USB ESP32-S3（macOS 上的 `/dev/cu.usbmodem*`、Linux 上的 `/dev/ttyACM*`、Windows 上的 `COMx`），或旧板上的 CH9102/CP210x UART 桥接器。蓝牙串行端口被过滤掉。如果存在多个候选者，它会询问。

已知的应用程序名称 `buddy` 解析到此仓库中的 `buddy/device/` 目录（自定义启动器 + Hello + Claude Buddy BLE 客户端 + Snake）。任何其他 `--apps` 值都被视为文件系统路径。

要跳过重新刷写并仅将（或刷新）应用程序推送到已配置的设备：

```
python3 scripts/install_apps.py --port <PORT> --src buddy
```

其中 `<PORT>` 是 `detect.py` 在上次完整运行中打印的任何内容——例如 `/dev/cu.usbmodem1101`、`/dev/ttyACM0` 或 `COM3`。

### 阶段

1. **检测** (`detect.py`) — 列出串行端口，过滤为 USB-UART 桥接器（CH9102 商户 `0x1A86`、Silabs CP210x `0x10C4`、FTDI `0x0403`）或 ESP32-S3 原生 USB-JTAG 接口（`0x303A`）。使用 esptool 探测以确认芯片。端口名称因操作系统而异（macOS 上的 `/dev/cu.usbmodem*`、Linux 上的 `/dev/ttyACM*`/`ttyUSB*`、Windows 上的 `COMx`），但 pyserial 会抽象这些差异。
2. **识别** (`detect.py`) — 除了端口发现外，`detect.py` 在 UIFlow 上时读取工厂测试分区签名，并扫描 I2C，并与 `references/hardware_signatures.md` 进行交叉引用，以建议正确的固件变体（Basic-16MB、Core2、CoreS3、Cardputer-Adv 等）。用户界面变体选择通过 `onboard.py --variant` 进行；没有单独的 `detect.py --identify` 标志。
3. **获取固件** (`fetch_firmware.py`) — 查询 M5Burner 清单 API 并将适当的 UIFlow 2.0 二进制文件下载到系统临时目录。在运行之间缓存——随时清除缓存都是安全的，它只是重新下载。
4. **刷写** (`flash.py`) — `esptool write_flash 0x0 <image>` 在 UART 桥接器上以 460800 波特率运行，在原生 USB S3 设备上以 115200 波特率和 `--no-stub` 运行。921600 在 CH9102 桥接器上会间歇性失败——不要增加它。原生 USB 刷写可能会在擦除过程中间歇性抛出 `Lost connection, retrying`；esptool 会恢复。刷写后的 `watchdog-reset` 拆卸步骤即使刷写本身成功也可能失败——`flash.py` 解析 esptool 的 stdout，在出现 `Hash of data verified` 时将此特定失败模式视为非致命，并且 `onboard.py` 会回退到 `flash.native_reset()`，如果需要，则进行手动-RESET 指导。
5. **安装应用程序**（可选，`install_apps.py`）— 将源目录中的每个 `.py` 从粘贴模式 REPL 上传到 `/flash/`，然后通过 `repl_reset` 重启（DTR/RTS 在原生 USB 上是无操作的——不要尝试它）。源布局：根 `*.py` → `/flash/`，`apps/*.py` → `/flash/apps/`（UIFlow 的默认启动器扫描该目录）。当捆绑包发送根 `main.py` 时，`install_apps.py` 还会设置 NVS `boot_option=2`，以便 UIFlow 自己的启动器不会运行，我们的 `main.py` 会接管启动流程——这对 ESP32-S3 上的 BLE 使用应用程序至关重要（见下文注意事项）。
6. **烟雾测试**（可选，`smoke_test.py`）— I2C 扫描、LCD 测试图案、扬声器哔哔声、按钮读取。

## 严重注意事项（脚本中已包含——不要质疑）

这些是脚本已经正确处理的事情，但如果用户要求你“手动运行 esptool”或类似操作，不要覆盖它们：

- **原生 USB ESP32-S3 板（Cardputer、Cardputer-Adv、CoreS3）需要物理 BtnG0+BtnRST 舞蹈进入下载模式。** 没有软件路径。芯片没有 DTR/RTS 桥接器，所以 esptool 或 pyserial 不会将其放入 ROM 引导程序——用户必须通过硬件按钮在复位脉冲期间将 GPIO0 低。在 Cardputer-Adv 上，两个按钮（BtnG0 和 BtnRST）都在设备的**背面**——小、平贴、通常用指甲最容易按下。`onboard.py:_wait_for_download_port` 在运行时提示 FLASH 阶段进行此操作：*按住并保持 BtnG0，短暂按住并释放 BtnRST，先释放 BtnRST，继续按住 BtnG0 大约一秒钟，然后释放 BtnG0，屏幕应完全变暗。* 如果设备重启进入 UIFlow 而不是变暗，请告诉用户 G0 释放得太早——指导会重试并告诉用户按住更长时间。不要尝试用 `esptool --before default_reset` 或 pyserial 的 DTR/RTS 自动化此操作；两者在原生 USB 上都是无操作的（引脚未连接到 EN），添加它们只会隐藏真实提示。
- **在刷写期间不要拔下设备。** 特别是在原生 USB 上。刷写期间断开连接会使内部闪存处于不一致状态。掩膜 ROM 通常在之后仍然可达（在背面单独按 BtnG0，或执行完整的 BtnG0+BtnRST 舞蹈），所以恢复只是重新运行 `m5-onboard go`——它是幂等的，并且会重新进入下载模式、重新刷写、重新推送应用程序。不要恐慌，不要开始拆开外壳；掩膜 ROM 在硅中，只要 USB PHY 完好无损，即使闪存损坏也能存活。
- **UART 桥接器的波特率是 460800，原生 USB 的 `--no-stub` 波特率是 115200。** 任何一方都不是 921600。CH9102 桥接器在 921600 时会失去同步（不是理论上的——它确实会失败）。原生 USB 的 stub 波特率提升路径在刷写期间会抛出“Lost connection”；115200 无 stub 反而会更快，因为它永远不会失败。
- **NVS 写入必须使用 `set_str`，而不是 `set_blob`** *(与 `install_apps.py` 的 `boot_option` 设置相关)*。UIFlow 启动调用 `nvs.get_str()`，ESP-IDF 将 blob 和字符串条目分开标记。blob 标记的键返回 `ESP_ERR_NVS_NOT_FOUND` 到 `get_str`，并且设备会循环重启。如果先前的尝试写入 blob，请在 `set_str` 之前调用 `nvs.erase_key(name)`。
- **REPL 多行块需要粘贴模式。** 逐行发送 `try:`/`except:` 会使 REPL 永远积累缩进。使用 Ctrl-E 进入粘贴模式，发送块，Ctrl-D 执行。`mpy_repl.py` 会包装此操作。
- **硬重置是 DTR=False、RTS=True、100ms、RTS=False——但仅在 UART-bridge 设备上。** 在原生 USB ESP32-S3 板上，DTR/RTS 线未连接到 EN/GPIO0，所以这个脉冲是无声的无操作。使用 `mpy_repl.repl_reset()`（通过 REPL 发送 `machine.reset()`）在这些设备上进行安装后的重启——`install_apps.py` 已经这样做了。如果你绕过 `install_apps.py` 并拼接自己的流程，不要在 usbmodem 端口上尝试 DTR/RTS 并期望重启；文件会保存在磁盘上，但旧代码仍然在运行。这个问题曾经让我们遇到回归问题。
- **空闲堆调试循环是正常的。** UIFlow 2.0 在配对屏幕上等待时打印 asyncio 诊断信息。不要将其解释为挂起。
- **Cardputer-Adv（ESP32-S3）BLE 外设需要 NVS `boot_option=2` + 自定义 `main.py`。** UIFlow 的默认 `boot_option=1` 会启动一个后台 Flow 配对 BLE 广播，这会卡住 NimBLE 控制器——后续用户代码中的 `gap_advertise(adv_data=...)` 调用会因“内存容量超出”错误（OSError(-519)）而失败，无论有效载荷形状如何，设备最终会使用空 AD 字段进行广播，iOS 和桌面 Claude Buddy 应用会过滤掉这些字段。捆绑包的 `main.py` 位于 `/flash/`，接管启动流程（在 `/flash/apps/` 上显示简单菜单），永远不会接触 BLE 本身，并保留控制器供用户选择的应用程序使用。`install_apps.py` 现在会在捆绑包发送根 `main.py` 时自动设置 `boot_option=2`——不要回归这种行为。

## 配置后（用户在设备上看到的内容）

一旦 `m5-onboard go` 在 `DONE` 横幅完成后结束，设备就可以自行使用了：

- **电源。** 滑动 Cardputer-Adv 右边缘的开关打开它。同一个开关用于关闭它。板子断开连接时运行其内部的 LiPo 电池；USB-C 为其充电。
- **启动。** 短暂的启动日志滚动，然后自动出现启动器菜单。菜单列出了 `/flash/apps/` 中的每个 `.py` 以及顶级 `/flash/*.py` 条目。
- **导航。** 箭头键（或键盘的轨迹点样式光标键）滚动菜单；Enter 启动高亮的应用程序；ESC 从应用程序中返回到启动器。
- **事件 WiFi 自动连接。** 捆绑包的 `main.py` 在每次启动时连接到硬编码的事件 WiFi（SSID `cardputer`），并在启动器菜单出现之前在 LCD 上显示结果。凭据存储在 `buddy/device/wifi_event.py` 中；连接是尽力而为的，即使连接失败，启动器也会继续。如果您在事件外使用此捆绑包，请编辑 `wifi_event.py` 或从 `main.py` 中删除 `_connect_wifi_with_splash()` 调用。
- **BLE 上的 Claude Buddy。** 仅第一次：在 Claude 桌面上，**帮助 → 故障排除 → 启用开发者工具**（一次性，跨启动持久）。然后 **开发者菜单 → 硬件 Buddy → 连接**。BLE 不论 WiFi 状态如何都有效——链接到 Claude.app 是本地链接。
- **回到 UIFlow。** 捆绑包仅发送 `/flash/` 中的 `main.py`（没有替换 `boot.py`），因此默认的 UIFlow `boot.py` 从未被触摸，并且没有 `boot_uiflow.py` 备份可以恢复。通过设备 REPL 删除我们的 `main.py`：`os.remove('/flash/main.py')` 后跟 `machine.reset()` 进行还原。下次启动时，默认的启动器接管。要完全重新开始，包括固件，请重新运行此技能而不带 `--apps`。

## 文件

- `scripts/onboard.py` — 主要协调器
- `scripts/detect.py` — 端口发现 + 芯片 ID
- `scripts/fetch_firmware.py` — M5Burner API + 下载
- `scripts/flash.py` — esptool 包装器
- `scripts/install_apps.py` — 通过粘贴模式 REPL 将 `.py` 文件目录推送到 `/flash/`；在覆盖之前备份 `boot.py` 为 `boot_uiflow.py`；当捆绑包发送根 `main.py` 时，还会写入 `boot_option` NVS 键
- `scripts/smoke_test.py` — I2C + LCD + 扬声器 + 按钮
- `scripts/mpy_repl.py` — 共享串行/REPL 辅助程序（粘贴模式、硬重置、启动日志捕获）
- `references/hardware_signatures.md` — 芯片 + I2C 指纹 → 型号 → 固件
- `references/uiflow2_nvs.md` — NVS 键参考，包括类型和失败模式

## 依赖项

- `pyserial` — 在 `onboard/scripts/vendor/serial/` 中打包（固定 3.5，BSD-3-Clause）。
- `esptool` — pip 依赖项，在 `requirements.txt` 中声明。导入检查通过 `importlib.util.find_spec("esptool")` 进行；二进制回退搜索涵盖 macOS 上的 `~/Library/Python/*/bin/`、Linux 上的 `~/.local/bin/`、Windows 上的 `%APPDATA%\Python\Python3XX\Scripts\`。

`onboard.py` 在启动时会运行一项预检：如果缺少 `esptool`（或在罕见的剔除供应商依赖的情况下缺少 `pyserial`），它会列出所需内容并询问用户是否现在安装。选择 `Y`（或按回车）时，它会在当前解释器中运行 `python -m pip install --user <missing>`，然后进行验证。在虚拟环境内部，会省略 `--user` 标志，以便将安装到虚拟环境的 site-packages 中。非交互式调用者（通过管道传入的标准输入）将收到手动安装提示，而不是交互式提示。

Python 本身必须存在，该技能才能执行任何操作——无法从解释器内部自举解释器。`git` **并非**必需——当 `git --version` 失败时，`/maker-setup` 命令会回退到使用 `curl`+`tar` 下载 GitHub tarball（macOS、Linux 和 Windows 10+ 上均预装了这两个工具）。Claude 负责在运行任何 `scripts/*.py` 调用**之前**检测 Python 并在缺失时安装它。检测只需运行 `python3 --version` / `python --version`——如果失败，Claude 会在其他任何操作之前使用宿主机的原生包管理器获取 Python。

**各操作系统的 Python 引导（若缺失，由 Claude 负责）：**

- **Windows** — `winget install -e --id Python.Python.3.13 --silent --accept-source-agreements --accept-package-agreements`。耗时约 30 秒，无界面，并能正确设置 PATH。如果当前 shell 在此后无法看到 `python`，请告知用户关闭并重新打开终端（Windows 仅在新的 shell 中更新 PATH）。
- **macOS** — Python 3 通常已预安装在任何当前 macOS 的 `/usr/bin/python3` 中（由 Apple 提供）。如果因某种原因缺失，通过 Homebrew 运行 `brew install python@3.13` 是首选方案；如果 Homebrew 本身缺失，可以提供通过 `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` 安装它（但仅在用户确认时——Homebrew 比 winget 涉及更大的承诺）。
- **Linux** — 使用发行版的包管理器。Debian/Ubuntu：`sudo apt-get update && sudo apt-get install -y python3 python3-pip`。Fedora：`sudo dnf install -y python3 python3-pip`。Arch：`sudo pacman -S --noconfirm python python-pip`。您可能需要使用 sudo，如果需要，应向用户显示密码提示。

**pyserial — 随技能捆绑提供：**

一个锁定版本的 `pyserial 3.5` 包含在 `scripts/vendor/` 下（BSD-3-Clause，与 Apache 兼容）。每个导入 `serial` 的脚本都会在第一次第三方导入之前调用 `vendor_path.ensure_on_syspath()`，这将把 `scripts/vendor/` 添加到 `sys.path` 的前部，因此无论用户系统范围内安装了什么，供应商版本都能正确解析。净效果：在新鲜克隆上，端口枚举和 REPL I/O 可以零 pip 步骤工作。约 500 KB，纯 Python，在 macOS / Linux / Windows 上使用相同的代码树。

**esptool — pip 依赖项，首次运行时自动安装：**

`esptool` 采用 GPLv2+ 许可，有意**未**进行供应商捆绑——保持仓库干净的 Apache-2.0 意味着 GPL 部分位于用户的 pip 管理环境中，而非代码树内。该技能的预检会检查可导入的 `esptool`，如果缺失，则提示安装它（`python -m pip install --user esptool` — 在虚拟环境内部省略 `--user` 以便安装到 site-packages）。对于子进程调用，我们使用 `[sys.executable, "-m", "esptool", ...]`；子进程继承用户站点，因此 pip 安装的模块可以干净地导入。`requirements.txt` 声明了此依赖项用于显式设置；提示路径是尚未运行 pip 的初次参与者的默认设置。

非交互式调用者（通过管道传入的标准输入、CI）会跳过提示，并收到 `python -m pip install --user esptool` 的提示。

**如果某人剔除了 `scripts/vendor/` 的备用方案：**

相同的预检路径也会在供应商副本丢失时通过 pip 重新安装 pyserial。这处理了某人下载了排除 vendor 的纯源代码 zip，或手动精简仓库以节省空间的情况。

**USB 驱动程序 — 仅限 Windows，仅适用于旧板：**

CH9102 USB-UART 驱动程序在 Windows 上仍需手动安装 — WCH 未发布 winget 清单。仅适用于 UART 桥接板（Basic、Fire、Core2、StickC）。原生 USB 的 ESP32-S3 板（Cardputer、Cardputer-Adv、CoreS3）作为复合 USB-CDC 设备枚举，使用 Windows 内置驱动程序，无需额外安装。

## 平台说明

该技能在 macOS、Linux 和 Windows 上运行。一些不明显之处：

- **端口命名。** pyserial 抽象了查找过程，但用户看到的每种操作系统看起来不同。传递 `detect.py` 报告的任何形式：
  - macOS：`/dev/cu.usbmodem1101`（原生 USB）或 `/dev/cu.usbserial-XXXX`（CH9102）
  - Linux：`/dev/ttyACM0`（原生 USB）或 `/dev/ttyUSB0`（UART 桥接）
  - Windows：`COM3`、`COM4` 等（如果不确定，请参见设备管理器 → 端口）
- **Linux 权限 — 在责怪硬件之前请阅读此内容。** 在大多数发行版上，在没有 sudo 的情况下访问 `/dev/ttyUSB*` / `/dev/ttyACM*` 需要组成员资格（Debian/Ubuntu/Arch 上的 `dialout`，Fedora 上的 `uucp`）。症状：`detect.py` 找到端口，但刷写步骤因 `Permission denied` 或 `Could not open port` 失败。长期一次性修复：
  ```bash
  sudo usermod -aG dialout $USER
  # 注销 / 重新登录 — 组更改仅对新会话生效
  ```
  `sudo python3 scripts/onboard.py ...` 可作为一次性措施使用，但添加组成员资格严格来说更好，因为从此以后 pyserial 在用户模式下打开端口的操作将成功完成。
- **Windows PATH 陷阱。** Python 的 `pip install --user esptool` 将可执行文件放置在 `%APPDATA%\Python\Python3XX\Scripts\` 中。如果该目录不在 PATH 中，`pip` 会打印警告，其他工具无法拾取该安装。`detect.py` 会直接在此处查找作为后备，因此即使未修复 PATH，技能仍会工作。但如果您在技能外部调用 esptool（或从其他工具遇到“esptool not found”错误），请执行以下操作之一：
  - 重新运行 Python 安装程序并勾选“将 Python 添加到 PATH”（安装默认设置），或
  - 通过系统属性 → 环境变量将 `%APPDATA%\Python\Python3XX\Scripts` 添加到 PATH，或
  - 使用 `python -m esptool ...`，无论 PATH 如何，此命令始终有效。
- **Windows 商店 Python。** 较新的 Windows 11 机器可能通过 Microsoft 商店预装了 Python。它有效但具有奇特的 PATH 行为（位于 `%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.*\` 下）。`detect.py` 也会检查该位置。如果有选择，`winget install Python.Python.3.13` 版本更可预测。
- **捆绑路径解析。** `install_apps.py` 的 `--src buddy` 简写按以下顺序解析：
  1. 如果设置了 `$M5_BUDDY_DIR` — 显式覆盖，始终优先。当您想要指向此克隆中不存在的分叉或自定义捆绑包时很有用。
  2. 此仓库内的 `buddy/device/` 目录，通过 `os.path.realpath(__file__)` 从 `install_apps.py` 向上遍历找到。适用于任何克隆位置，包括符号链接的技能安装 `~/.claude/skills/m5-onboard/`。
  3. `~/Downloads/m5stack/buddy/device`。
  4. `~/Desktop/m5stack/buddy/device`。

  大多数安装命中 (2)。仅在指向此克隆之外的捆绑包的罕见情况下设置 `M5_BUDDY_DIR`：`export M5_BUDDY_DIR=/path/to/buddy/device`（Unix）或 `$env:M5_BUDDY_DIR="C:\path\to\buddy\device"`（PowerShell）。
- **固件缓存。** 下载的固件位于 `~/.cache/m5-onboard/`（或 `$XDG_CACHE_HOME/m5-onboard/`），如果缺失则以 0700 模式创建。缓存文件在写入时进行 MD5 验证，并在命中时重新验证。清除缓存是安全的；下次运行时会重新下载。
