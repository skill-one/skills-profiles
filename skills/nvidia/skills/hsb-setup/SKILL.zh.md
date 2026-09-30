---
name: hsb-setup
description: 克隆最新的NVIDIA Holoscan Sensor Bridge仓库，询问正在使用的支持的开发套件，根据平台配置主机，构建正确的演示容器，运行它，并通过ping 192.168.0.2来验证HSB连接性。用于Holoscan Sensor Bridge的设置、构建、容器启动和首次连接建立。
---

# Holoscan 传感器桥接演示环境搭建

当用户希望端到端地搭建 Holoscan 传感器桥接演示环境时，使用此技能。

此工作流具有副作用。切勿自动运行它。仅在用户明确调用时才运行它。

## 开始前 — 必须先完成的步骤（按顺序执行）

**步骤 1 — 读取环境变量。** 在做任何其他事情之前，检查这些变量并将它们的解析值打印给用户：

```
SSH_TARGET      远程开发套件登录（例如 nvidia@192.168.1.50）。如果未设置，请询问用户。
REMOTE_ROOT     远程工作目录（例如 /home/nvidia）。如果未设置，请询问用户。
REMOTE_SUDO     sudo / sudo -n / "" — 如果未设置，默认为 "sudo"。
REMOTE_SSH_OPTS 额外的 SSH 选项（可选）。
HSB_PLATFORM    平台提示 — 可能是空的；将根据硬件检测。
HSB_REPO        自定义仓库 URL — 默认为 https://github.com/nvidia-holoscan/holoscan-sensor-bridge.git
```

**SSH_TARGET 和 REMOTE_ROOT 是必需的。如果其中任何一个缺失，请停止并询问用户。**

**步骤 2 — 展示阶段计划。** 在采取任何行动之前，向用户展示此确切计划并等待确认：

```
HSB Setup — 阶段计划
  阶段 0：令牌预算预检查
  阶段 1：确认平台，设置 SSH，克隆仓库，学习用户指南
  阶段 2：主机先决条件检查和网络设置
  阶段 3：原生 CLI 构建（仅 AGX Thor — 其他平台将跳过此阶段）
  阶段 4：构建演示容器，运行它，ping 192.168.0.2，验证 FPGA 版本
  阶段 5：问题报告（带保存选项）
  阶段 6：停止应用程序，退出容器，将控制权交还给用户
```

**步骤 3 — 令牌预算预检查（阶段 0）。** 在任何 SSH 连接或开发套件更改之前运行此操作。有关完整过程的详细信息，请参阅 `## 令牌预算预检查` 部分。在预算检查通过之前，不要继续进入阶段 1。

## 说明

通过输入 `/hsb-setup [PLATFORM] [OPTIONS]` 调用此技能。该技能将交互式地引导每个阶段，并在做出更改之前提示用户确认。

## 此技能必须执行的任务

0. **在任何远程命令或开发套件配置更改之前运行强制性的令牌预算预检查。** 估计完成所有设置阶段所需的令牌数，使用最佳可用的 Claude Code/账户使用机制检查用户的剩余订阅计划使用情况，将估计值和结果显示给用户，如果可用预算不足或无法验证，则停止。
1. 提示用户确认开发套件已连接到 Holoscan 传感器桥接，并且所有设备都已通电，并且有到外部世界的活动网络连接，并且开发套件已安装正确的操作系统版本。如果所有配置参数都已知，请查看仓库用户指南，并绘制一个从开发套件到传感器的图，让用户确认这是他们拥有的设置。
2. 一旦用户确认设置已准备好，如果用户是从外部计算机运行 claude 技能，则建立到开发套件的 SSH 连接。如果 claude 直接安装在开发套件上，可以跳过此步骤。
3. 通过在开发套件上运行 `cat /sys/class/dmi/id/product_name` 并使用产品名到平台的映射（见“主机平台自动检测”部分）将结果与 `HSB_PLATFORM` 环境变量进行比较，以验证主机开发套件平台。如果命令返回一个与 `HSB_PLATFORM` 不同的已知非空平台名称，或者 `HSB_PLATFORM` 为空，则更新 `HSB_PLATFORM` 以匹配检测到的平台，并提醒用户关于此更改。如果命令返回空或失败，并且 `HSB_PLATFORM` 已设置，则保持现有值。
4. 从最新的 `main` 分支克隆或刷新 GitHub 仓库。默认情况下这是公共的 `nvidia-holoscan/holoscan-sensor-bridge` 仓库，但用户可以通过 `HSB_REPO` 环境变量或 `--repo <URL>` 命令行标志覆盖它为自定义仓库 URL。如果仓库是 SSH 仓库，如果没有设置 SSH 密钥，则提醒用户并提供设置 SSH 密钥的说明。
5. 如果开发套件/平台不明确，请询问用户他们想要使用哪个开发套件/平台。
6. 在克隆仓库的根目录下，学习和理解 `docs/user_guide` 中的用户指南，了解如何为每个开发套件和操作系统设置主机环境、演示容器、在容器内和容器外运行应用程序（如适用）以及刷新 FPGA。
7. 将该平台映射到正确的主机设置和容器构建模式，并确保根据用户指南说明正确配置主机设置，修复并添加任何缺失的配置或提示用户如何修复。
8. 构建演示容器。
9. 运行演示容器。
10. 验证到 `192.168.0.2` 的连接。如果到板的连接失败，请提示用户可能需要不同的 IP 地址。
11. 读取寄存器 0x80 以验证 FPGA 版本。如果传感器上的 FPGA 版本与开发套件上的 hsb 主机软件不匹配，建议用户使用 hsb-flash-skill 将板刷新到正确的 FPGA 版本。
12. 分阶段报告进度，清楚地解释失败原因，并在放弃之前尝试安全的修复措施。
13. 对于遇到的每个问题，创建一个报告，指定问题是什么以及如何克服它。
14. 允许用户将最终报告导出到一个 md 文件。
15. 完成设置后，停止任何正在运行的应用程序并退出容器，将控制权交给用户，在终端窗口的仓库主目录上。

## 支持的平台和构建映射

除非仓库或工作树中的当前文档明确说明否则使用以下映射：

- **IGX Orin with dGPU OS/configuration** → 使用 `sh docker/build.sh --dgpu` 构建
- **IGX Orin iGPU** → 使用 `sh docker/build.sh --igpu` 构建
- **AGX Orin** → 使用 `sh docker/build.sh --igpu` 构建
- **AGX Thor** → 使用 `sh docker/build.sh --igpu` 构建
- **DGX Spark** → 使用 `sh docker/build.sh --igpu` 构建

如果用户只说“IGX Orin”，请明确询问它是 **iGPU** 还是 **dGPU OS/configuration**。

## 主机平台自动检测

在阶段 1（建立 SSH 后或在本地运行时）通过读取 DMI 产品名并与其 `HSB_PLATFORM` 环境变量进行比较来验证实际开发套件硬件。

### 产品名到平台的映射

下表将已知的 `/sys/class/dmi/id/product_name` 值映射到支持的 `HSB_PLATFORM` 值。使用**不区分大小写的子字符串**搜索进行匹配 — 产品名可能包含附加文本（例如，“Developer Kit”，版本号）。

| `product_name` 包含（不区分大小写） | 映射的 `HSB_PLATFORM` | 备注 |
|---|---|---|
| `IGX Orin` | `IGX Orin` | 如果尚未知道，仍然需要询问 iGPU 与 dGPU |
| `AGX Orin` | `AGX Orin` | |
| `AGX Thor` | `AGX Thor` | |
| `DGX Spark` | `DGX Spark` | |

如果产品名不匹配任何已知模式，将其视为**未识别**，并转到步骤 5 中的手动平台问题。

### 检测和协调逻辑

在开发套件上运行以下命令（在阶段 1 SSH 她文档内或本地）：

```bash
DETECTED_PRODUCT=""
if [ -f /sys/class/dmi/id/product_name ]; then
  DETECTED_PRODUCT=$(cat /sys/class/dmi/id/product_name 2>/dev/null | tr -d '\n')
fi

DETECTED_PLATFORM=""
if echo "$DETECTED_PRODUCT" | grep -qi "IGX Orin"; then
  DETECTED_PLATFORM="IGX Orin"
elif echo "$DETECTED_PRODUCT" | grep -qi "AGX Orin"; then
  DETECTED_PLATFORM="AGX Orin"
elif echo "$DETECTED_PRODUCT" | grep -qi "AGX Thor"; then
  DETECTED_PLATFORM="AGX Thor"
elif echo "$DETECTED_PRODUCT" | grep -qi "DGX Spark"; then
  DETECTED_PLATFORM="DGX Spark"
fi

echo "DETECTED_PRODUCT=$DETECTED_PRODUCT"
echo "DETECTED_PLATFORM=$DETECTED_PLATFORM"
echo "HSB_PLATFORM=${HSB_PLATFORM:-}"
```

收集输出后，应用以下协调规则：

1. **`DETECTED_PLATFORM` 非空且 `HSB_PLATFORM` 为空** → 将 `HSB_PLATFORM` 设置为 `DETECTED_PLATFORM`。提醒用户：
   ```
   从硬件自动检测平台：<DETECTED_PLATFORM> (product_name: <DETECTED_PRODUCT>)。
   HSB_PLATFORM 未设置 — 更新为 "<DETECTED_PLATFORM>"。
   ```

2. **`DETECTED_PLATFORM` 非空且与 `HSB_PLATFORM` 不同** → 使用 `DETECTED_PLATFORM` 覆盖 `HSB_PLATFORM`。提醒用户：
   ```
   警告：硬件报告 "<DETECTED_PLATFORM>" (product_name: <DETECTED_PRODUCT>)，
   但 HSB_PLATFORM 设置为 "<HSB_PLATFORM>"。
   更新 HSB_PLATFORM 以匹配检测到的硬件："<DETECTED_PLATFORM>"。
   ```

3. **`DETECTED_PLATFORM` 非空且与 `HSB_PLATFORM` 匹配** → 无需更改。确认：
   ```
   平台验证：<HSB_PLATFORM> 与硬件匹配 (product_name: <DETECTED_PRODUCT>)。
   ```

4. **`DETECTED_PLATFORM` 为空**（文件缺失、不可读或未识别的产品名）**且 `HSB_PLATFORM` 已设置** → 保持现有的 `HSB_PLATFORM`。警告：
   ```
   无法从硬件自动检测平台 (product_name: "<DETECTED_PRODUCT>")。
   保持现有的 HSB_PLATFORM: "<HSB_PLATFORM>"。
   ```

5. **`DETECTED_PLATFORM` 和 `HSB_PLATFORM` 都为空** → 转到步骤 5 中的手动平台问题。

协调后，在远程会话状态文件中持久化更新的 `HSB_PLATFORM`，以便后续阶段使用正确的值。

## Linux/Windows 友好的包装变量

当此技能从 Linux/Windows 使用本地 Claude Code 会话并通过 SSH 执行时，如果存在这些环境变量，请优先使用它们：

- `SSH_TARGET` 用于远程登录目标，例如 `nvidia@agx-thor-host`
- `REMOTE_ROOT` 用于远程工作目录，其中应存放仓库
- `REMOTE_SUDO` 用于特权命令。接受 `sudo`、`sudo -n` 或空字符串
- `REMOTE_SSH_OPTS` 用于额外的 SSH 选项
- `HSB_PLATFORM` 作为可选的平台提示
- `HSB_REPO` 用于自定义 GitHub 仓库 URL 以克隆（例如 `https://github.com/myorg/my-hsb-fork.git`）。如果未设置，默认为 `https://github.com/nvidia-holoscan/holoscan-sensor-bridge.git`

如果设置了这些，请通知用户这些设置并使用它们，除非用户明确覆盖它们。

在阶段 1 之前，打印您将使用的解析远程执行设置，如果需要，可以隐藏秘密。

## 强制交互模式

在做出任何更改之前，显示来自上述步骤 2 的阶段计划。对于非 Thor 平台，跳过阶段 3。

然后一次执行一个阶段。

**在每个非最终阶段（阶段 0–5）之后：**

1. 显示阶段摘要。详细级别取决于 `--verbose` 模式（见“详细模式”部分）：
   - **详细模式**：完整输出 + 详细状态块（阶段名称、运行内容、结果、下一步操作）。
   - **简洁**（默认）：带突出显示问题的要点式摘要。
2. **提示用户** `Proceed to Phase <N+1>? [Y/n]` 同时指定阶段 N+1 是什么，并在继续之前等待确认（见“阶段门”部分）。

如果某项操作失败，请不要只是堆砌原始日志。总结：

- 失败的确切命令
- 可能的根本原因
- 你将尝试的下一个安全修复
- 修复是否成功

## 令牌预算预检查

### 阶段 0 - 令牌预算预检查

此阶段是强制性的，必须在任何 SSH 连接、仓库克隆、包/配置检查、容器构建、重启或开发套件设置更改之前运行。

1. **估计完整运行令牌预算**，不仅限于下一个阶段。以下值是保守的启发式算法，不是测量的历史使用情况。将它们视为初始安全预算，一旦有测量的令牌使用情况可用，就根据实际 `/hsb-setup` 运行日志进行优化：
   - 为 IGX Orin、AGX Orin 或 DGX Spark 的完整设置运行预留至少 **280,000 个令牌**。
   - 为 AGX Thor 预留至少 **340,000 个令牌**，因为原生构建和 SIPL/FuSa 检查增加了更多阶段和故障排除。
   - 当预期 `--verbose`、自定义仓库处理、SSH 密钥修复、重启恢复或额外故障排除时，增加 **60,000 个令牌**。
   - 如果平台尚未知道，请使用较大的估计值。

2. **检查剩余使用情况**，使用当前订阅计划的最佳可用 Claude Code/账户使用源。当可用时，优先使用机器可读或产品提供的使用数据。如果无法提供可靠的 使用源，请询问用户从 Claude Code 账户或计划 UI 提供他们当前的剩余使用量/配额。

   当由于无法自我验证使用情况而询问用户时，请按此确切顺序呈现选项，以便安全停止选项首先出现：
   1. **我无法验证 — 停止**：用户无法确定剩余使用量。在阶段 1 之前停止。
   2. **我有 < {estimate} 可用 — 停止**：用户检查了他们的计划/账户 UI 并确认剩余预算少于估计值。在阶段 1 之前停止。
   3. **我有 ≥ {estimate} 可用 — 继续**：用户检查了他们的计划/账户 UI 并确认至少有估计的预算可用。继续到阶段 1。
   4. **输入一些内容**：将其视为问题或自由形式指令，回答它，然后重新提示相同的有序选项。

   不要将继续选项放在第一位。用户必须有意跳过停止选项才能选择继续。

3. **在继续之前向用户显示结果**：

   ```text
   令牌预算预检查
   - 估计的 /hsb-setup 运行所需令牌数：<estimate>
   - 估计基础：保守启发式算法；从实际运行日志中优化
   - 包含安全裕度：<margin>
   - 剩余计划使用量：<available or "unverified">
   - 结果：通过 / 失败
   ```

4. **在预算不足或无法验证时停止**：
   - 如果剩余使用量低于估计值，则在阶段 1 之前停止，并解释该技能拒绝启动，因为它可能在修改开发套件设置时耗尽令牌。
   - 如果无法验证剩余使用量，则在阶段 1 之前停止，并询问用户开始新的会话、升级/刷新使用量或提供可验证的剩余使用量。
   - `--y` 必须不能绕过此预检查。

## 缺少时需要询问的平台问题

只问最少的必要问题：

1. 您使用哪个平台？
   - IGX Orin iGPU
   - IGX Orin dGPU
   - AGX Orin
   - AGX Thor
   - DGX Spark
2. HSB 板是否已物理连接并通电？
3. 您是否可以接受需要 `sudo` 进行网络和 Docker 设置的命令？

如果用户已经提供了任何这些，请不要再次询问。

## 可用脚本

| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/hsb_phase_runner.sh` | 结构化 shell 执行，每个阶段带时间戳日志 | `<phase_name> <command>` |

使用 `run_script(scripts/hsb_phase_runner.sh, <phase_name>, <command>)` 运行阶段步骤以自动记录。

## 阶段详情

有关完整分步阶段说明、输出样式、详细模式行为、自动批准模式、阶段门规则和持久 SSH 会话模型的详细信息，请参阅 [references/phase-details.md](references/phase-details.md)。

## 恢复剧本

在适用的情况下按顺序尝试这些修复：

1. 如果失败看起来是暂时的，重新运行失败命令一次。
2. 修复缺失的先决条件（`git-lfs`、Docker 访问、`xhost`、网络路由）。
3. 刷新仓库状态和 LFS 内容。
4. 仅重新运行失败的阶段，而不是整个工作流。
5. 如果仍然受阻，请提供简洁的诊断和用户可以复制粘贴的命令列表。

## 此技能中的支持文件

- 请参阅 [docs/platform-mapping.md](docs/platform-mapping.md) 以获取此技能使用的权威构建和主机设置摘要。
- 请参阅 [docs/failure-playbook.md](docs/failure-playbook.md) 以获取常见的修复逻辑。
- 当您想要结构化 shell 执行和时间戳日志时，使用 [scripts/hsb_phase_runner.sh](scripts/hsb_phase_runner.sh) 作为辅助。

## 内置帮助 (`--help`)

如果 `$ARGUMENTS` 包含 `--help` 或 `-h`，**不要运行工作流**。相反，按原文打印以下帮助文本并停止：

Holoscan 传感器桥接 — 演示设置技能

使用方法
  /hsb-setup [平台] [选项]

平台（可选 — 如果省略将提示输入）
  AGX Orin          NVIDIA Jetson AGX Orin (iGPU, 使用 --igpu 构建)
  AGX Thor          NVIDIA Jetson AGX Thor (iGPU, 使用 --igpu 构建)
  IGX Orin iGPU     NVIDIA IGX Orin iGPU 配置 (使用 --igpu 构建)
  IGX Orin dGPU     NVIDIA IGX Orin 配备独立 GPU (使用 --dgpu 构建)
  DGX Spark         NVIDIA DGX Spark (iGPU, 使用 --igpu 构建)

选项
  --help, -h        显示此帮助信息并退出
  --verbose         显示每个阶段的完整原始命令输出
                    （默认是简洁的要点摘要）
  --y               自动批准所有阶段门（跳过阶段之间的用户确认
                    。不推荐 — 在继续之前会显示确认警告。所有输出都
                    保存到带时间戳的日志文件中。
  --repo <URL>      克隆自定义 GitHub 仓库，而不是默认的
                    nvidia-holoscan/holoscan-sensor-bridge。
                    也可以通过 HSB_REPO 环境变量设置。
                    优先级：--repo 标志 > HSB_REPO 环境变量 > 默认仓库

环境变量（在调用技能之前设置）
  SSH_TARGET        远程登录目标（例如 ubuntu@10.0.0.1）
  REMOTE_ROOT       仓库克隆和构建的远程工作目录
  REMOTE_SUDO       权限提升：'sudo'、'sudo -n' 或 ''
  REMOTE_SSH_OPTS   额外的 SSH 选项（例如 -o ServerAliveInterval=30）
  HSB_PLATFORM      平台提示（与上面 PLATFORM 列表中的值相同）
  HSB_REPO          自定义 GitHub 仓库 URL（被 --repo 标志覆盖）

工作流程阶段
  阶段 0   令牌预算预检；验证是否有足够的计划使用量以完成完整运行
  阶段 1   确认平台、克隆仓库并学习用户指南
  阶段 2   主机先决条件检查和网络设置
  阶段 3   CLI 工具的原生构建（仅 AGX Thor，否则跳过）
  阶段 4   构建、运行演示容器并验证连接性
  阶段 5   生成问题报告，可选择导出到文件
  阶段 6   停止应用程序、退出容器、交由用户接管

  技能会在每个阶段之间提示确认。

示例
  /hsb-setup AGX Thor
  /hsb-setup AGX Thor --verbose
  /hsb-setup AGX Thor --y
  /hsb-setup IGX Orin dGPU --repo https://github.com/myorg/my-fork.git
  /hsb-setup --help

打印帮助文本后，不要进行任何阶段或询问任何问题。

参见 [内置帮助 (`--help`)](#内置帮助---help) 中的 `示例` 部分了解调用示例。

当 `$ARGUMENTS` 包含平台时，使用它而不是再次询问。在解析平台名称之前，从参数中移除 `--verbose`、`--y`、`--repo <URL>` 和 `--help`。
