# M5Stack 初始化

此技能可自动执行 M5Stack ESP32 设备的完整冷启动工作流程：检测 USB、识别型号、刷写 UIFlow 2.0，并将 MicroPython 应用程序包推送到 `/flash/` 目录，以便设备启动到用户软件。我们提供的应用程序（Claude Buddy、Snake、Hello）通过 BLE 或 USB 进行通信。该工作流程适用于 macOS、Linux 和 Windows；该技能针对 M5Stack Basic v2.6（CH9102 桥接器、ESP32-D0WDQ6-V3、16 MB 闪存）进行开发，并已推广以涵盖 Core 系列的其他设备，其中 Cardputer-Adv（ESP32-S3、原生 USB）是当前默认目标。

## 脚本存放位置

此技能作为 `cwc-makers` 插件的一部分提供参考，但可执行脚本和 `buddy/` 应用程序包位于 https://github.com/moremas/build-with-claude 的本地克隆中（`/maker-setup` 命令创建此克隆）。从该克隆的 `onboard/` 目录中运行以下每个 `scripts/*.py` 调用，以便 `--apps buddy` 解析到兄弟目录 `buddy/device/` 的有效负载。

## 使用场景

当用户插入 M5Stack 设备并希望对其进行配置时，请使用此技能。决策树：

- **全新/未知设备** → 运行 `onboard.py --apps buddy` 端到端（检测 → 识别 → 刷写 → 安装应用程序）。这是默认路径。
- **已刷写设备，用户只想安装/刷新应用程序** → 运行 `install_apps.py --src buddy`（或任何 `--src <路径>` 到 `.py` 文件目录）。
- **已刷写设备，感觉某些功能损坏** → 运行 `smoke_test.py`（I2C + LCD + 扬声器 + 按钮检查）。
- **用户想知道总线上的内容 / 设备能做什么** → `smoke_test.py`。

如果插入多个设备，请询问要针对哪个端口——不要猜测。如果用户正在配置他们之前使用过的设备（例如“与上次一样”或“另一个 Buddy”），除非他们另有指示，否则默认为 `--apps buddy`。

### 假设哪种变体

此技能所在的设备主要配置 **Cardputer-Adv** 板，因此 `onboard.py` 现在默认为 `--variant cardputer-adv`。实际上这意味着：

- 如果用户没有提及型号，则使用默认值。他们几乎肯定持有 Cardputer-Adv。
- 如果用户说“Cardputer”（没有“Adv”），请询问——这两个型号共享相同的形状因子，但需要不同的固件镜像，刷写错误的固件会导致设备死循环。
- 如果用户指定任何其他板（“Core2”、“CoreS3”、“Basic”、“Fire”），请显式传递匹配的 `--variant`——默认值不适用。
- 芯片是 ESP32-S3，无论哪种情况，`detect.py` 在刷写 UIFlow 之前都无法区分 Cardputer 和 Cardputer-Adv（相同的原生 USB-JTAG VID，没有预刷写 I2C 探测）。因此，这是一个用户意图问题，而不是硬件指纹问题。

## 工作流程

主要的协调器是 `scripts/onboard.py`。它按顺序驱动子脚本，并处理它们之间的交接（等待重启、捕获 MAC 地址、报告进度）。除非用户要求部分运行，否则请直接调用它，而不是自己拼接子脚本。

默认配置命令（全新的 Cardputer-Adv，安装 buddy 包）：

```
python3 scripts/onboard.py --apps buddy
```

**如何从 Claude Code 的 Bash 工具中调用此命令。** 不要将 `onboard.py` 作为前台 Bash 命令调用。Bash 工具捕获输出，并且不会将输出流回助手，直到命令退出——此命令运行 2-3 分钟。这种沉默看起来与死锁相同，并且助手通常会在按钮提示到达用户之前放弃。相反，始终使用 `run_in_background: true`、`tee` 到日志文件，然后使用监控工具（或通过 Read 进行周期性的 `tail`）实时向用户显示阶段横幅、心跳和提示。`2>&1` 不是解决方案——所有进度都写入 stderr，终端显示良好。解决方案是流式语义，而不是重定向。有效模式：

```
# 启动（后台，tee 日志）：
python3 scripts/onboard.py --apps buddy 2>&1 | tee /tmp/m5-onboard.log

# 监控（实时显示关键事件，而不会淹没字节进度垃圾信息）：
tail -f /tmp/m5-onboard.log | grep -E --line-buffered \
  "^====|heartbeat|Heads up|Enter download mode|download mode!|rebooted into UIFlow|Manual reset|DONE|ERROR|Error|Traceback|FAIL|failed|No USB|not detected|Attempt [0-9]|Device already in download|Download mode port|Post-flash port|Waiting for device"
```

### 向用户传达物理步骤（必需）

刷写阶段在没有原生 USB 板上的手动按钮按下的情况下**无法继续**——没有软件路径。当监控日志显示 `Enter download mode`（或脚本在 FLASH 阶段似乎在等待时），您必须停止并告诉用户在 **Cardputer 的背面**，用自己的话，在继续之前执行以下操作：

1. 按住并**保持** **G0** 按钮
2. 在仍然按住 G0 的同时，短暂按一下并释放 **RST** 按钮
3. 继续按住 G0，再等待大约一秒钟，然后释放它
4. 屏幕应该完全变暗——这意味着下载模式已激活

如果设备重启进入 UIFlow 而不是变暗，请告诉用户 G0 释放得太早，并尝试更长时间地按住它。不要继续，不要重试脚本，也不要尝试软件解决方案，直到用户确认屏幕变暗——否则刷写将不会开始。任何后续的 `Manual reset` 提示也适用：传达物理步骤并等待用户。

在自己的终端中直接运行 `onboard.py` 的用户将看到所有实时输出——那里不需要任何更改。

如果省略了 `--port`，`detect.py` 在所有三个操作系统中选择最可能的候选者：原生 USB ESP32-S3（macOS 上的 `/dev/cu.usbmodem*`、Linux 上的 `/dev/ttyACM*`、Windows 上的 `COMx`），或较旧板上的 CH9102/CP210x UART 桥接器。蓝牙串行端口被过滤掉。如果存在多个候选者，它会询问。

已知的应用程序名称 `buddy` 解析到此仓库中的 `buddy/device/` 目录（自定义启动器 + Hello + Claude Buddy BLE 客户端 + Snake）。任何其他 `--apps` 值都被视为文件系统路径。

要跳过重新刷写，只需将（或刷新）应用程序推送到已配置的设备上：

```
python3 scripts/install_apps.py --port <PORT> --src buddy
```

其中 `<PORT>` 是上次完整运行时 `detect.py` 打印的任何内容——例如 `/dev/cu.usbmodem1101`、`/dev/ttyACM0` 或 `COM3`。

### 阶段

1. **检测** (`detect.py`) — 列出串行端口，过滤为 USB-UART 桥接器（CH9102 商家 `0x1A86`、Silabs CP210x `0x10C4`、FTDI `0x0403`）或 ESP32-S3 原生 USB-JTAG 接口（`0x303A`）。使用 esptool 探测以确认芯片。端口名称因操作系统而异（macOS 上的 `/dev/cu.usbmodem*`、Linux 上的 `/dev/ttyACM*`/`ttyUSB*`、Windows 上的 `COMx`），但 pyserial 会抽象这些差异。
2. **识别** (`detect.py`) — 除了端口发现外，`detect.py` 在 UIFlow 上时读取工厂测试分区签名，并在 I2C 上扫描一次，并与 `references/hardware_signatures.md` 进行交叉引用，以建议正确的固件变体（Basic-16MB、Core2、CoreS3、Cardputer-Adv 等）。用户界面变体选择通过 `onboard.py --variant` 发生；没有单独的 `detect.py --identify` 标志。
3. **获取固件** (`fetch_firmware.py`) — 查询 M5Burner 资料清单 API，并将适当的 UIFlow 2.0 二进制文件下载到系统临时目录。在运行之间缓存——随时清除缓存都是安全的，它只是重新下载。
4. **刷写** (`flash.py`) — `esptool write_flash 0x0 <image>` 在 UART 桥接器上以 **460800 波特**运行，在原生 USB S3 设备上以 `--no-stub` 在 115200 波特运行。921600 在 CH9102 桥接器上会间歇性地失败——不要增加它。原生 USB 刷写可能会在擦除过程中间歇性地抛出 `Lost connection, retrying`；esptool 会恢复。即使刷写本身成功，后刷写的 `watchdog-reset` 拆除步骤也可能失败——`flash.py` 解析 esptool 的 stdout，当出现 `Hash of data verified` 时，将此特定失败模式视为非致命，并且 `onboard.py` 会回退到 `flash.native_reset()`，如果需要，则进行手动-RESET 指导。
5. **安装应用程序**（可选，`install_apps.py`）— 将源目录中的每个 `.py` 从粘贴模式 REPL 上传到 `/flash/`，然后通过 `repl_reset` 重启（原生 USB 上 DTR/RTS 是无操作的——不要尝试它）。源布局：根 `*.py` → `/flash/`，`apps/*.py` → `/flash/apps/`（UIFlow 的库存启动器扫描该目录）。当包提供根 `main.py` 时，`install_apps.py` 还会设置 NVS `boot_option=2`，以便 UIFlow 自己的启动器不会运行，我们的 `main.py` 会接管启动流程——这对 ESP32-S3 上的 BLE 使用应用程序至关重要（见下文注意事项）。
6. **烟雾测试**（可选，`smoke_test.py`）— I2C 扫描、LCD 测试图案、扬声器哔哔声、按钮读取。

## 严重注意事项（脚本中已包含——不要质疑）

这些是脚本已经正确处理的事情，但如果用户要求你“直接运行 esptool 手动”或类似操作，不要覆盖它们：

- **原生 USB ESP32-S3 板（Cardputer、Cardputer-Adv、CoreS3）需要物理 BtnG0+BtnRST 舞蹈进入下载模式。** 没有软件路径。芯片没有 DTR/RTS 桥接器，所以 esptool 或 pyserial 什么都做不了——用户必须通过硬件按钮在复位脉冲期间将 GPIO0 拉低。在 Cardputer-Adv 上，特别是两个按钮（BtnG0 和 BtnRST）都在设备的**背面**——小而平贴，通常用指甲最容易按下。`onboard.py:_wait_for_download_port` 在运行时在 FLASH 阶段提示此操作：*按住并保持 BtnG0，短暂按一下并释放 BtnRST，先释放 BtnRST，继续按住 BtnG0 大约一秒钟，然后释放 BtnG0，屏幕应该完全变暗。* 如果设备重启进入 UIFlow 而不是变暗，请告诉用户 G0 释放得太早——指导会重试并告诉用户按住更长时间。不要继续，不要重试脚本，也不要尝试软件解决方案，直到用户确认屏幕变暗——否则刷写将不会开始。任何后续的 `Manual reset` 提示也适用：传达物理步骤并等待用户。
- **在刷写期间不要拔下设备。** 特别是在原生 USB 上。刷写期间断开连接会使内部闪存处于不一致状态。掩膜 ROM 通常在之后仍然可达（在背面单独按下 BtnG0，或执行完整的 BtnG0+BtnRST 舞蹈），所以恢复只是重新运行 `m5-onboard go`——它是幂等的，并且会重新进入下载模式，重新刷写，重新推送应用程序。不要恐慌，不要开始拆开外壳；掩膜 ROM 存在于硅中，只要 USB PHY 完好无损，即使闪存损坏也能存活。
- **波特率在 UART 桥接器上是 460800，在原生 USB 上是 115200 与 `--no-stub`。** 任何一方都不是 921600。CH9102 桥接器在 921600 时会失去同步（不是理论上的——它会失败）。原生 USB 的 stub 波特率提升路径在刷写期间会间歇性地产生“Lost connection”；115200 无 stub 反而会意外地加快端到端速度，因为它永远不会失败。
- **NVS 写入必须使用 `set_str`，而不是 `set_blob`** *(与 `install_apps.py` 的 `boot_option` 设置相关)*。UIFlow 的启动调用 `nvs.get_str()`，ESP-IDF 会将 blob 和字符串条目单独标记。一个 blob 标记的键返回 `ESP_ERR_NVS_NOT_FOUND` 到 `get_str`，并且设备会死循环。如果先前的尝试写入 blob，请在 `set_str` 之前调用 `nvs.erase_key(name)`。
- **REPL 多行块需要粘贴模式。** 逐行发送 `try:`/`except:` 会使 REPL 无限累积缩进。使用 Ctrl-E 进入粘贴模式，发送块，Ctrl-D 执行。`mpy_repl.py` 会包装此功能。
- **硬重置是 DTR=False, RTS=True, 100ms, RTS=False——但这只在 UART-bridge 设备上适用。** 在原生 USB ESP32-S3 板上，DTR/RTS 线路没有连接到 EN/GPIO0，所以这个脉冲是无声的无效操作。使用 `mpy_repl.repl_reset()`（通过 REPL 发送 `machine.reset()`）来在这些设备上进行安装后的重启——`install_apps.py` 已经这样做了。如果你绕过 `install_apps.py` 并自己拼接流程，不要尝试在 usbmodem 端口上使用 DTR/RTS 并期望重启；文件会保存在磁盘上，但旧代码仍然在运行。那曾经让我们犯过错误。
- **空闲堆栈调试循环是正常的。** UIFlow 2.0 在配对屏幕上等待时打印 asyncio 诊断。不要将其解释为死锁。
- **Cardputer-Adv（ESP32-S3）BLE 外围设备需要 NVS `boot_option=2` + 自定义 `main.py`。** UIFlow 默认的 `boot_option=1` 会启动一个后台 Flow 配对 BLE 广播，这会卡住 NimBLE 控制器——后续从用户代码中调用的 `gap_advertise(adv_data=...)` 调用无论有效载荷形状如何，都会触发 OSError(-519) “内存容量超出”错误，并且设备最终会使用空 AD 字段进行广播，iOS 和桌面 Claude Buddy 应用会过滤掉这些字段。包的 `main.py` 位于 `/flash/`，它接管启动流程（显示一个简单的菜单，覆盖 `/flash/apps/`），永远不会接触 BLE 本身，并让控制器保持原始状态，供用户选择的应用程序使用。`install_apps.py` 现在会在包提供根 `main.py` 时自动设置 `boot_option=2`——不要回归该行为。

## 配置后（设备上用户看到的内容）

一旦 `m5-onboard go` 完成在 `DONE` 横幅处，设备就可以自行使用了：

- **电源。** 将 Cardputer-Adv 右边缘的开关滑到打开。同一个开关用于关闭。该板在拔下时运行其内部的 LiPo 电池；通过 USB-C 充电。
- **启动。** 短暂的启动日志滚动，然后自动出现启动器菜单。菜单列出了 `/flash/apps/` 中的每个 `.py` 以及顶层 `/flash/*.py` 条目。
- **导航。** 箭头键（或键盘的轨迹点样式光标键）滚动菜单；按 Enter 启动高亮应用程序；ESC 从应用程序中返回到启动器。
- **事件 WiFi 自动连接。** 包的 `main.py` 在每次启动时连接到硬编码的事件 WiFi（SSID `cardputer`），并在启动器菜单出现之前在 LCD 上显示结果。凭据存储在 `buddy/device/wifi_event.py` 中；连接是尽力而为的，即使连接失败，启动器也会继续。如果您在事件之外使用此包，请编辑 `wifi_event.py` 或从 `main.py` 中删除 `_connect_wifi_with_splash()` 调用。
- **BLE 上的 Claude Buddy。** 仅第一次：在 Claude 桌面上，**帮助 → 故障排除 → 启用开发者工具**（一次性，跨启动持久）。然后 **开发者菜单 → 硬件 Buddy → 连接**。BLE 不论 WiFi 状态如何都有效——链接到 Claude.app 是本地的。
- **回到 UIFlow。** buddy 包仅提供 `/flash/` 中的 `main.py`（没有替换 `boot.py`），因此库存 UIFlow `boot.py` 从未被触及，并且没有 `boot_uiflow.py` 备份可以恢复。通过设备 REPL 删除我们的 `main.py`：`os.remove('/flash/main.py')` 后跟 `machine.reset()`。库存启动器在下次启动时接管。要完全重新开始，包括固件，请重新运行此技能而不带 `--apps`。

## 文件

- `scripts/onboard.py` — 主要协调器
- `scripts/detect.py` — 端口发现 + 芯片 ID
- `scripts/fetch_firmware.py` — M5Burner API + 下载
- `scripts/flash.py` — esptool 包装器
- `scripts/install_apps.py` — 将 `.py` 文件目录推送到 `/flash/`，通过粘贴模式 REPL；在覆盖之前备份 `boot.py` 为 `boot_uiflow.py`；当包提供根 `main.py` 时，还会写入 `boot_option` NVS 键
- `scripts/smoke_test.py` — I2C + LCD + 扬声器 + 按钮
- `scripts/mpy_repl.py` — 共享串行/REPL 辅助（粘贴模式、硬重置、启动日志捕获）
- `references/hardware_signatures.md` — 芯片 + I2C 指纹 → 型号 → 固件
- `references/uiflow2_nvs.md` — NVS 键参考，包括类型和失败模式

## 依赖项

- `pyserial` — 在 `onboard/scripts/vendor/` 中附带（固定 3.5，BSD-3-Clause）。
- `esptool` — pip 依赖项，在 `requirements.txt` 中声明。导入检查通过 `importlib.util.find_spec("esptool")` 发生；二进制后备搜索覆盖 macOS 上的 `~/Library/Python/*/bin/`、Linux 上的 `~/.local/bin/`、Windows 上的 `%APPDATA%\Python\Python3XX\Scripts\`。

`onboard.py` 在启动时运行预检查：如果 `esptool`（或在罕见的情况下修剪供应商，`pyserial`）缺失，它会列出所需内容并询问用户是否现在安装。在 `Y`（或按 Enter）上，它会在当前解释器中运行 `python -m pip install --user <missing>`，然后进行验证。在虚拟环境中，`--user` 标志会被丢弃，安装会落在虚拟环境的 site-packages 中。非交互式调用者（管道 stdin）会收到手动安装提示，而不是提示。

Python 本身必须存在，此技能才能执行任何操作——你不能从内部启动解释器。`git` 是**不**必需的——当 `git --version` 失败时，`/maker-setup` 命令会回退到使用 `curl`+`tar` 下载 GitHub 归档（这两个在 macOS、Linux 和 Windows 10+ 上都预装）。Claude 负责检测 Python 并在运行任何 `scripts/*.py` 调用之前安装它（如果缺失）。检测只是运行 `python3 --version` / `python --version`——如果失败，Claude 会使用主机原生包管理器在运行任何 `scripts/*.py` 调用之前获取 Python。

**每个操作系统的 Python 引导（如果缺失，Claude 负责检测并安装）:**

- **Windows** — `winget install -e --id Python.Python.3.13 --silent --accept-source-agreements --accept-package-agreements`。大约需要 30 秒，无 UI，会正确设置 PATH。如果当前 shell 无法看到 `python`，请告诉用户关闭并重新打开终端（Windows 仅在新 shell 中更新 PATH）。
- **macOS** — Python 3 通常预装为 `/usr/bin/python3` 在任何当前的 macOS 上（由 Apple 提供）。如果出于某种原因没有预装，则通过 Homebrew 使用 `brew install python@3.13` 是首选；如果 Homebrew 本身缺失，请提供通过 `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` 安装它的命令（但只有当用户确认时——Homebrew 比 winget 更大）。
- **Linux** — 使用发行版包管理器。Debian/Ubuntu: `sudo apt-get update && sudo apt-get install -y python3 python3-pip`。Fedora: `sudo dnf install -y python3 python3-pip`。Arch: `sudo pacman -S --noconfirm python python-pip`。您可能需要使用 `sudo`，并且如果需要，应该将密码提示显示给用户。

**pyserial — 随技能附带:**

一个固定的 `pyserial 3.5` 运行在 `scripts/vendor/` 下（BSD-3-Clause，Apache 兼容）。每个导入 `serial` 的脚本在第一个第三方导入之前调用 `vendor_path.ensure_on_syspath()`，这会将 `scripts/vendor/` 添加到 `sys.path` 的开头，因此无论用户系统范围内有什么，都会解析为附带副本。净效果：端口枚举和 REPL I/O 在带有零 pip 步骤的新克隆上工作。~500 KB，纯 Python，macOS / Linux / Windows 上相同树。

**esptool — pip 依赖项，第一次运行时自动安装:**

`esptool` 是 GPLv2+，并且有意**不**附带——保持仓库为 Apache-2.0 意味着 GPL 部分存在于用户 pip 管理的环境中，而不是树中。技能的预检查检查可导入的 `esptool`，如果缺失，会提示安装它（`python -m pip install --user esptool`——在虚拟环境中，`--user` 标志会被丢弃，它会落在 site-packages 中）。对于子进程调用，我们使用 `[sys.executable, "-m", "esptool", ...]`；子进程继承了用户站点，因此 pip 安装的模块可以干净地导入。`requirements.txt` 声明此内容以进行显式设置；对于首次参加的用户（那些还没有运行 pip 的用户），提示路径是默认的。

非交互式调用者（管道 stdin，CI）会跳过提示，并会收到 `python -m pip install --user esptool` 提示。

**如果有人修剪了 `scripts/vendor/`:**

相同的预检查路径也会在供应商副本丢失的情况下重新安装 pyserial via pip。这处理了有人下载了仅包含源代码的 zip 文件（排除了供应商）或手动修剪仓库以节省空间的案例。

**USB 驱动程序 — Windows 特定，仅适用于较旧的板:**

CH9102 USB-UART 驱动程序在 Windows 上仍然是手动安装——WCH 没有发布 winget 归档。仅适用于 UART-bridge 板（Basic、Fire、Core2、StickC）。原生 USB ESP32-S3 板（Cardputer、Cardputer-Adv、CoreS3）枚举为复合 USB-CDC 设备，使用 Windows 内置驱动程序，无需额外安装。

## 平台说明

此技能适用于 macOS、Linux 和 Windows。不太明显的部分：

- **端口命名。** pyserial 会抽象查找，但用户看到的形式因操作系统而异。传递 `detect.py` 报告的任何形式：
  - macOS: `/dev/cu.usbmodem1101`（原生 USB）或 `/dev/cu.usbserial-XXXX`（CH9102）
  - Linux: `/dev/ttyACM0`（原生 USB）或 `/dev/ttyUSB0`（UART 桥接器）
  - Windows: `COM3`, `COM4`, 等等（如果不确定，请查看设备管理器 → 端口）
- **Linux 权限——在归咎于硬件之前阅读此内容。** 在大多数发行版上，如果没有 sudo 访问 `/dev/ttyUSB*` / `/dev/ttyACM*`，则需要组成员资格（Debian/Ubuntu 上的 `dialout`、Fedora 上的 `uucp`）。症状：`detect.py` 找到端口，但刷写步骤失败，出现 `Permission denied` 或 `Could not open port`。修复一次，长期：
  ```bash
  sudo usermod -aG dialout $USER
  # 登出 / 登回——组更改仅对新会话有效
  ```
  `sudo python3 scripts/onboard.py ...` 作为一次性操作可以工作，但添加组成员资格更好，因为 pyserial 的用户模式端口打开成功且干净，从此以后。
- **Windows PATH 惯例。** Python 的 `pip install --user esptool` 将可执行文件放在 `%APPDATA%\Python\Python3XX\Scripts\` 下。如果该目录不在 PATH 中，`pip` 会打印警告，并且没有任何其他内容会拾取安装。`detect.py` 直接查找那里作为后备，因此即使没有修复 PATH，技能仍然可以工作。但如果你在技能之外调用 esptool（或从其他工具遇到“esptool not found”错误），则：
  - 重新运行 Python 安装程序并勾选“将 Python 添加到 PATH”（安装的默认值），或者
  - 通过系统属性 → 环境变量将 `%APPDATA%\Python\Python3XX\Scripts` 添加到 PATH，或者
  - 使用 `python -m esptool ...`，无论 PATH 如何，它始终有效。
- **Windows Store Python。** 新的 Windows 11 机器可能通过 Microsoft Store 预装了 Python。它工作正常，但具有古怪的 PATH 行为（位于 `%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.*\` 下）。`detect.py` 也检查该位置。如果你有选择，`winget install Python.Python.3.13` 版本更可预测。
- **包路径解析。** `install_apps.py` 的 `--src buddy` 简写按以下顺序解析：
  1. `$M5_BUDDY_DIR` 如果设置——显式覆盖，始终获胜。当您想指向一个分支或自定义包（不在此克隆中）时，这很有用。
  2. 此仓库中的 `buddy/device/` 目录，通过 `os.path.realpath(__file__)` 从 `install_apps.py` 向上遍历。适用于任何克隆位置，包括符号链接的技能安装位置 `~/.claude/skills/m5-onboard/`.
  3. `~/Downloads/m5stack/buddy/device`.
  4. `~/Desktop/m5stack/buddy/device`.

  大多数安装会命中 (2)。仅当您要指向此克隆之外的包时才设置 `M5_BUDDY_DIR`: `export M5_BUDDY_DIR=/path/to/buddy/device`（Unix）或 `$env:M5_BUDDY_DIR="C:\path\to\buddy\device"`（PowerShell）。
- **固件缓存。** 下载的固件位于 `~/.cache/m5-onboard/`（或 `$XDG_CACHE_HOME/m5-onboard/`），如果缺失，则以模式 0700 创建。缓存文件在写入时进行 MD5 验证，并在命中时重新验证。清除缓存是安全的；下次运行会重新下载。
