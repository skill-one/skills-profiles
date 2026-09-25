# HSB 应用运行器

当用户希望在连接了 HSB 板的开发套件上发现、选择和运行 Holoscan 传感器桥示例应用程序时，使用此技能。

此技能假定开发套件已经设置好（SSH、演示容器已构建、主机已配置、板已连接）。如果设置未完成，请指示用户先运行 `/hsb-setup`。

此工作流在演示容器内运行应用程序。仅在用户明确调用时才运行它。

## 开始前 — 必须的门控（按顺序先做这些）

**门控 1 — 读取环境变量。** 在做任何其他事情之前，检查这些变量并打印其解析值给用户：

```
SSH_TARGET      远程开发套件登录（例如：nvidia@192.168.1.50）。如果未设置，请询问用户。
REMOTE_ROOT     远程工作目录（例如：/home/nvidia）。如果未设置，请询问用户。
REMOTE_SUDO     sudo / sudo -n / "" — 如果未设置，默认为 "sudo"。
REMOTE_SSH_OPTS 额外的 SSH 选项（可选）。
HSB_PLATFORM    平台提示（可选）。
```

**SSH_TARGET 和 REMOTE_ROOT 是必需的。如果任何一个缺失，就停止并询问用户。**

**门控 2 — 展示阶段计划并获取确认。** 在采取任何行动之前：

如果用户的请求已经包含平台、板类型和传感器，请 upfront 声明：
- 你将扫描 `examples/` 并根据用户的传感器类型和平台过滤应用程序
- 你将不会自动添加 `--headless` — 只有在用户明确请求时才会添加
- 如果用户指定了超时（例如，“60 秒超时”），你将使用该值作为看门狗超时
- 应用程序将通过 `docker run` 在演示容器内运行，使用 `python3` 运行基于 Python 的示例

展示阶段计划：

```
HSB App — 阶段计划
  阶段 0：验证板连接性和演示容器就绪
  阶段 1：发现用户设置并选择要运行的应用程序
  阶段 2：运行应用程序，并进行监控、故障分析和迭代调试
  阶段 3：生成会话报告（可选择保存）
```

然后明确询问：`是否继续执行阶段 0？[Y/n]` — 在用户确认之前，不要开始阶段 0。

**门控 3 — 快速路径检查。** 在用户在门控 2 中确认后，在执行任何阶段 0 命令之前运行此检查：

```bash
ssh -o BatchMode=yes $REMOTE_SSH_OPTS $SSH_TARGET \
  "grep _SESSION_VERIFIED /tmp/.claude_hsb_app_session/state.sh 2>/dev/null || echo 'no session'"
```

如果输出包含 `_SESSION_VERIFIED=true`，则跳过阶段 0 和阶段 1 设置发现 — 直接进入应用程序选择并通知用户。

## 此技能必须做的事情

1. 验证开发套件可通过 SSH 访问，HSB 板已连接且响应正常，演示容器可用。读取当前的 FPGA 版本和板身份。
2. 与用户交互，了解其具体设置 — 开发套件上的仓库位置、HSB 软件版本、板类型（Lattice 等）以及连接的传感器（例如，双 IMX274、VB1940）。然后扫描仓库的用户指南和 `examples/` 目录，以构建与用户设置兼容的应用程序列表。展示列表并让用户选择要运行的应用程序。
3. 在演示容器内运行选定的应用程序，监控输出，如果应用程序失败，则分析日志输出并引导用户进行调试 — 包括建议代码或环境编辑并重新运行应用程序。
4. 生成会话摘要报告 — 遇到的问题、应用的修复和结果。提供保存报告到文件的选项。

## Linux/Windows 友好的包装变量

重用来自 `hsb-setup` 和 `hsb-flash` 技能的相同环境变量：

- `SSH_TARGET` 用于远程登录目标（例如：`nvidia@agx-thor-host`）
- `REMOTE_ROOT` 用于远程工作目录
- `REMOTE_SUDO` 用于特权命令
- `REMOTE_SSH_OPTS` 用于额外的 SSH 选项
- `HSB_PLATFORM` 作为可选的平台提示

如果这些已设置，通知用户这些设置并使用它们，而无需重新询问。

在阶段 0 之前，打印解析的远程执行设置。

## 强制交互模式

### 会话中的首次运行（无先验验证）

当没有有效的会话状态时，显示完整的阶段计划：

- 阶段 0：验证板连接性和演示容器就绪
- 阶段 1：发现用户设置并选择要运行的应用程序
- 阶段 2：运行应用程序，并进行监控、故障分析和迭代调试
- 阶段 3：生成会话报告（可选择保存）

然后逐个执行阶段。

### 同一会话中的后续运行（快速路径）

当会话状态文件（`/tmp/.claude_hsb_app_session/state.sh`）存在**并且**包含 `_SESSION_VERIFIED=true` 时，该技能跳过阶段 0 和阶段 1 设置发现，因为连接性和硬件已经验证。相反，通知用户并直接跳转到应用程序选择：

```
会话已验证 — 跳过连接检查。
  SSH 目标：$SSH_TARGET
  板：HSB Lattice | FPGA：XXXX
  平台：AGX Thor | HSB 版本：X.X.X
  传感器：双 IMX274

直接进行应用程序选择。
```

然后执行：
- 阶段 1 步骤 2–3 仅（扫描示例、展示应用程序列表、用户选择应用程序）
- 阶段 2：运行应用程序
- 阶段 3：会话报告

### 何时从头开始重新运行阶段 0

当以下情况发生时，必须重新运行阶段 0（忽略快速路径）：

1. **新会话**：远程主机上不存在会话状态文件，或者启动了新的 Claude Code 会话。
2. **执行失败提示连接丢失**：如果阶段 2 失败并出现指示板或开发套件无法访问的症状（ping 失败、SSH 超时、容器启动失败、`No such device` 错误），请从会话状态中清除 `_SESSION_VERIFIED` 并在重试之前重新运行阶段 0。
3. **用户明确请求**：如果用户说“重新验证”、“重新开始”、“从头开始运行”或调用 `/hsb-app --full`，请从头开始运行阶段 0。

有关完整的确认协议，请参阅下方的 [## 阶段门控](#phase-gate--user-confirmation-between-phases)。

如果出现故障，请**不要**只是堆砌原始日志。总结：

- 失败的确切命令
- 可能的根本原因
- 推荐的安全操作
- 问题是否阻塞

## 阶段详情

有关每个阶段的详细步骤说明，请参阅 [references/phase-details.md](references/phase-details.md)。

## 执行规则

### SSH heredoc 模式

使用与 `hsb-setup` 和 `hsb-flash` 相同的持久 SSH 会话模型。每个阶段作为一个 SSH heredoc 块运行：

```bash
ssh -o BatchMode=yes $REMOTE_SSH_OPTS $SSH_TARGET bash -s <<'REMOTE'
set -e

# 从上一个阶段恢复状态
source /tmp/.claude_hsb_app_session/state.sh 2>/dev/null || true
cd "${_CLAUDE_CWD:-__REMOTE_ROOT__}"

# 阶段命令
echo "=== 阶段 N: 描述 ==="
command1
command2

# 保存状态以供下一阶段使用（如果已设置，则保留 _SESSION_VERIFIED）
_PREV_VERIFIED="${_SESSION_VERIFIED:-}"
mkdir -p /tmp/.claude_hsb_app_session
{
  echo "export _CLAUDE_CWD=\"$(pwd)\""
  echo "export PATH=\"$PATH\""
  echo "export REPO_DIR=\"$REPO_DIR\""
  echo "export VERSION=\"$VERSION\""
  echo "export HSB_PLATFORM=\"$HSB_PLATFORM\""
  echo "export BOARD_TYPE=\"$BOARD_TYPE\""
  echo "export SENSORS=\"$SENSORS\""
  echo "export FPGA_VERSION=\"$FPGA_VERSION\""
  echo "export SELECTED_APP=\"$SELECTED_APP\""
  echo "export APP_OPTIONS=\"$APP_OPTIONS\""
  echo "export APP_TIMEOUT=\"$APP_TIMEOUT\""
  [ "$_PREV_VERIFIED" = "true" ] && echo "export _SESSION_VERIFIED=true"
} > /tmp/.claude_hsb_app_session/state.sh
REMOTE
```

将 `__REMOTE_ROOT__` 替换为 `$REMOTE_ROOT` 的字面值，当组合 heredoc 时。

### 应用程序容器使用

应用程序命令在演示容器内运行。使用命名容器的分离模式。

对于具有 `--timeout` 的应用程序，使用看门狗模式。对于无限运行的应用程序，流式传输日志并等待用户请求停止。

### 应用程序容器后清理

每次运行应用程序后，停止并删除容器。有关清理模式，请参阅 [references/phase-details.md](references/phase-details.md)。

### 会话拆除

在阶段 3（或在停止工作流的任何失败情况下）后：

```bash
docker ps --filter "name=hsb_app_" --format '{{.Names}}' | xargs -r docker stop -t 2 2>/dev/null || true
ssh -o BatchMode=yes $REMOTE_SSH_OPTS $SSH_TARGET "rm -rf /tmp/.claude_hsb_app_session"
```

## 阶段门控 — 阶段之间的用户确认

完成每个阶段（阶段 0–2）后，**始终提示用户在启动下一个阶段之前进行确认**。

**例外**：当 `--y`（自动批准模式）处于活动状态时，会跳过阶段门控。请参阅“自动批准模式 (`--y`)”部分。

```
是否继续执行阶段 <N+1> (<阶段描述>)？ [Y/n]
```

### 用户响应处理

此技能中的所有提示都需要明确的键入响应。**永远不要将空白或仅 Enter 的输入视为选择** — 而是重新提示用户。

- **"y"**, **"yes"**, **"Y"**, **"ok"**, **"go"**, **"continue"**, **"next"** → 进入下一个阶段。
- **"n"**, **"no"**, **"stop"**, **"abort"** → 停止执行。打印：
  ```
  应用工作流在阶段 N 后暂停。
  您可以通过重新调用技能来恢复。
  ```
  然后运行会话拆除。
- **任何其他文本** → 视为关于当前阶段的问题或指令。回答它，然后重新提示。
- **"retry"** → 重新执行当前阶段，再次显示摘要，然后重新提示。

### 例外

- **阶段 3**（会话报告）是最终阶段 — 如果用户想要运行另一个应用程序，则不要提示它。显示报告并提供保存选项。
- **如果阶段失败**且无法恢复，请停止并报告清楚。

## 内置帮助 (`--help`)

如果 `$ARGUMENTS` 包含 `--help` 或 `-h`，请打印以下内容并停止：

```
HSB 应用运行器技能

用法
  /hsb-app [选项]

选项
  --help, -h        显示此帮助消息并退出
  --verbose         显示每个阶段的完整原始输出
  --y               自动批准所有阶段门控（跳过阶段之间的用户确认
                    会直接运行整个工作流，无需在阶段之间等待用户确认。
                    不推荐这样做 — 在继续之前会显示确认警告。所有输出都
                    保存到带时间戳的日志文件中。
  --timeout N       设置应用程序运行时间（秒）（默认：无超时，
                    应用程序运行直到用户请求停止）
  --full            强制从头开始进行阶段 0 的完整验证，即使会话已经验证

环境变量（调用技能之前设置）
  SSH_TARGET        远程登录目标（例如：ubuntu@10.0.0.1）
  REMOTE_ROOT       远程工作目录
  REMOTE_SUDO       特权提升：'sudo'、'sudo -n' 或 ''
  REMOTE_SSH_OPTS   额外的 SSH 选项
  HSB_PLATFORM      平台提示
  HSB_REPO_DIR      REMOTE_ROOT 下仓库目录名称（默认：holoscan-sensor-bridge）
                    示例：HSB_REPO_DIR=hololink → 仓库位于 $REMOTE_ROOT/hololink

工作流阶段
  阶段 0   验证板连接性和演示容器就绪
            （在同一会话中重复运行时跳过）
  阶段 1   发现用户设置，扫描示例，选择应用程序
            （在重复运行时跳过设置发现）
  阶段 2   运行应用程序，并进行监控和迭代调试
  阶段 3   生成并可选择保存会话报告

示例
  /hsb-app
  /hsb-app --verbose
  /hsb-app --timeout 60
  /hsb-app --timeout 30 --verbose
  /hsb-app --y
  /hsb-app --y --timeout 120
  /hsb-app --full
  /hsb-app --help
```

## 调用示例

- `/hsb-app`
- `/hsb-app --verbose`
- `/hsb-app --timeout 60`
- `/hsb-app --timeout 30 --verbose`
- `/hsb-app --y`
- `/hsb-app --y --timeout 120`
- `/hsb-app --full`
- `/hsb-app --full --verbose`
- `/hsb-app --help`

## 详细模式 (`--verbose`)

该技能支持 `--verbose` 标志：

### 检测标志

检查 `$ARGUMENTS`（斜杠命令后的文本）是否包含任何：`--help` / `-h`、`--verbose`、`--y`、`--timeout N` 或 `--full`（不区分大小写）。在进一步解析之前，从参数中删除所有标志（及其值）。

当 `--full` 存在时，忽略缓存的会话状态并从头开始运行阶段 0。

### 详细模式（当设置时）

- 显示每个 SSH 命令的完整原始输出
- 内联显示完整应用程序输出（所有 stdout/stderr）
- 显示详细的阶段状态块

### 简洁模式（默认，无 `--verbose`）

- 在每个阶段后显示要点式摘要
- 抑制原始命令输出
- 显示关键应用程序输出行（启动、错误、摘要），但不显示每个帧日志
- 使用 4 行格式显示问题（症状、原因、解决方案、阻塞）

## 自动批准模式 (`--y`)

该技能支持 `--y` 标志，可跳过所有阶段门控，并从开始到结束直接运行整个工作流，无需在阶段之间等待用户确认。这**不推荐**用于正常使用。

### 确认警告

当 `--y` 检测到时，显示警告并询问用户确认：

```
⚠  警告：已启用自动批准模式 (--y)。

这不推荐使用。所有阶段门控将被跳过，整个
工作流将在无需在阶段之间暂停等待您的确认的情况下运行。

您将无法查看中间结果、提问或
在阶段之间中止。所有输出都将保存到带时间戳的日志文件中。

注意：在自动批准模式下，阶段 1 中的应用程序选择仍然
需要您的输入（您必须选择要运行的应用程序），但应用程序将
使用默认设置自动运行。阶段 2 中的调试迭代将被跳过 — 应用程序运行一次
并报告结果。
```

- 如果用户响应为 **"yes"**（精确匹配，不区分大小写）→ 启用自动批准模式。
- 任何其他响应 → 取消自动批准模式并交互式运行。

### 当 `--y` 处于活动状态时的行为

1. **阶段门控被跳过**。
2. **应用程序选择仍然需要用户输入** — 用户必须选择要运行的应用程序。
3. **使用默认应用程序设置自动运行** — 跳过“默认与自定义”提示，应用程序使用其默认选项运行。
4. **超时默认为 30 秒**，如果命令行中未指定 `--timeout`（以避免无限挂起）。
5. **调试迭代被跳过** — 如果应用程序在阶段 2 中失败，则记录失败，但不会执行交互式调试。工作流直接进入报告。
6. **日志文件**：启动时创建，名为 `hsb-app-log-YYYY-MM-DD-HHMMSS.md`，位于 `$REMOTE_ROOT/` 或当前目录。
7. **阶段摘要仍然实时显示**。
8. **如果失败且阻塞，则停止工作流**。

### 与其他标志的组合

- `--y --verbose`：自动批准并显示完整原始输出。
- `--y --timeout N`：自动批准并设置固定的应用程序运行时间。
- `--y` 单独：自动批准并显示简洁输出且无超时（在自动批准模式下，应用程序默认运行 30 秒以避免无限挂起）。

## 超时处理 (`--timeout`)

该技能支持 `--timeout N` 标志，其中 N 是应用程序运行时间的秒数。

### 检测标志

在 `$ARGUMENTS` 中匹配 `--timeout` 后跟空格分隔的整数。示例：`--timeout 60`。

### 行为

- **当设置**：应用程序运行恰好 N 秒，然后通过 `docker stop` 停止。在此窗口内收集的输出显示给用户。
- **未设置（交互模式）**：应用程序运行直到用户请求停止。通知用户如何请求停止。
- **未设置（自动批准模式）**：应用程序默认运行 30 秒以防止无限挂起。

### 验证

- N 必须是正整数
- 最小值：5 秒
- 最大值：3600 秒（1 小时）
- 如果无效，请显示错误并要求用户提供有效的超时
