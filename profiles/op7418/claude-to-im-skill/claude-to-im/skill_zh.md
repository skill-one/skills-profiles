# Claude-to-IM 桥接技能

您正在管理 Claude-to-IM 桥接。
用户数据存储在 `~/.claude-to-im/`。

技能目录 (SKILL_DIR) 位于 `~/.claude/skills/claude-to-im`。
在 Codex 安装中，它可能位于 `~/.codex/skills/Claude-to-IM-skill`。
如果这两个路径都不存在，则回退到 Glob 模式 `**/skills/**/claude-to-im/SKILL.md` 或 `**/skills/**/Claude-to-IM-skill/SKILL.md` 并从结果中推导出根路径。

## 命令解析

将用户意图从 `$ARGUMENTS` 解析为以下子命令之一：

| 用户说（示例） | 子命令 |
|---|---|
| `setup`, `configure`, `配置`, `我想在飞书上用 Claude`, `帮我连接 Telegram`, `帮我接微信` | setup |
| `start`, `start bridge`, `启动`, `启动桥接` | start |
| `stop`, `stop bridge`, `停止`, `停止桥接` | stop |
| `status`, `bridge status`, `状态`, `运行状态`, `怎么看桥接的运行状态` | status |
| `logs`, `logs 200`, `查看日志`, `查看日志 200` | logs |
| `reconfigure`, `修改配置`, `帮我改一下 token`, `换个 bot` | reconfigure |
| `doctor`, `diagnose`, `诊断`, `挂了`, `没反应了`, `bot 没反应`, `出问题了` | doctor |

**歧义解析：`status` vs `doctor`** — 当用户只是想检查桥接是否在运行（信息性）时，使用 `status`。当用户报告问题或怀疑有故障（诊断性）时，使用 `doctor`。当不确定且用户描述了症状（例如，“没反应了”, “挂了”）时，优先选择 `doctor`。

为 `logs` 提取可选的数字参数（默认 50）。

在要求用户提供任何平台凭证之前，内部读取 `SKILL_DIR/references/setup-guides.md` 以了解每个凭证的位置。不要将完整指南提前展示给用户——只提及他们需要执行的特定下一步（例如，“前往 https://open.feishu.cn → 你的应用 → 凭证以找到 App ID”）。如果用户说不知道如何操作，则显示指南的相关部分。

## 运行时检测

在执行任何子命令之前，检测您正在运行的环境：

1. **Claude 代码** — `AskUserQuestion` 工具可用。使用它进行交互式设置向导。
2. **Codex / 其他** — `AskUserQuestion` 不可用。回退到非交互式指导：解释步骤，显示 `SKILL_DIR/config.env.example`，并要求用户手动创建 `~/.claude-to-im/config.env`。

您可以通过检查 `AskUserQuestion` 是否在您的可用工具列表中来测试这一点。

## 配置检查（适用于 `start`, `stop`, `status`, `logs`, `reconfigure`, `doctor`）

在执行 `setup` 之外的任何子命令之前，检查是否存在 `~/.claude-to-im/config.env`：

- **如果不存在：**
  - 在 Claude 代码中：告诉用户“未找到配置”并使用 `AskUserQuestion` 自动启动 `setup` 向导。
  - 在 Codex 中：告诉用户“未找到配置。请根据示例创建 `~/.claude-to-im/config.env`” 然后显示 `SKILL_DIR/config.env.example` 的内容并停止。不要尝试启动守护进程——没有 config.env，进程将在启动时崩溃并留下一个过时的 PID 文件，这将阻止未来的启动。
- **如果存在：** 继续执行请求的子命令。

## 子命令

### `setup`

运行交互式设置向导。此子命令需要 `AskUserQuestion`。如果不可用（Codex 环境），则显示 `SKILL_DIR/config.env.example` 的内容，并逐字段解释，并指导用户手动创建配置文件。

当 `AskUserQuestion` 可用时，逐个收集输入。每次回答后，将值确认回用户（仅显示最后 4 个字符以掩盖秘密），然后进入下一个问题。

**步骤 1 — 选择通道**

询问要启用哪些通道（telegram, discord, feishu, qq, weixin）。接受逗号分隔的输入。简要描述每个：
- **telegram** — 适合个人使用。流式预览，内联权限按钮。
- **discord** — 适合团队使用。服务器/频道/用户级访问控制。
- **feishu** (Lark) — 用于飞书/Lark 团队。流式卡片，工具进度，内联权限按钮。
- **qq** — QQ C2C 私聊仅限。无内联权限按钮，无流式预览。权限使用文本 `/perm ...` 命令。
- **weixin** — 微信扫码登录。单个链接账户仅限；新的登录将替换之前的登录。无内联权限按钮，无流式预览。权限使用文本 `/perm ...` 命令或快速 `1/2/3` 回复。语音消息仅使用微信自带的语音转文字文本；原始语音音频不会被桥接转录。

**步骤 2 — 按通道收集 token**

为每个启用的通道逐个收集一个凭证。用一句话告诉用户在哪里找到每个值。只有在用户要求帮助或说不知道如何操作时才显示完整指南（来自 `SKILL_DIR/references/setup-guides.md`）：
- **Telegram**: Bot Token → 确认（掩码）→ Chat ID（查看指南了解如何获取）→ 确认 → 允许的用户 ID（可选）。**重要**：至少必须设置 Chat ID 或允许的用户 ID，否则机器人将拒绝所有消息。
- **Discord**: Bot Token → 确认（掩码）→ 允许的用户 ID → 允许的频道 ID（可选）→ 允许的公会 ID（可选）。**重要**：至少必须设置允许的用户 ID 或允许的频道 ID，否则机器人将拒绝所有消息（默认拒绝）。
- **Feishu**: App ID → 确认 → App Secret → 确认（掩码）→ 域（可选）→ 允许的用户 ID（可选）。收集凭证后，解释用户必须完成的两个阶段设置：
  - **阶段 1**（在启动桥接之前）：(A) 批量添加权限，(B) 启用机器人功能，(C) 发布第一个版本 + 管理员批准。这使得权限和机器人生效。
  - **阶段 2**（需要运行桥接）：(D) 运行 `/claude-to-im start`，(E) 配置事件 (`im.message.receive_v1`) 和回调 (`card.action.trigger`) 使用长连接模式，(F) 发布第二个版本 + 管理员批准。
  - **为什么是两个阶段**：Feishu 在保存事件订阅时验证 WebSocket 连接——如果桥接未运行，保存将失败。桥接需要已发布的权限才能连接。
  - 保持这一点为简短清单——只有在要求时才显示完整指南。
- **QQ**：收集两个必需字段，然后是可选字段：
  1. QQ App ID（必需）→ 确认
  2. QQ App Secret（必需）→ 确认（掩码）
  - 告诉用户：这两个值可以在 https://q.qq.com/qqbot/openclaw 找到
  3. 允许的用户 OpenIDs（可选，按 Enter 跳过）——注意：这是 `user_openid`，不是 QQ 号码。如果用户还没有 openid，可以留空。
  4. 图像启用（可选，默认为 true，按 Enter 跳过）——如果底层提供者不支持图像输入，设置为 false
  5. 最大图像大小 MB（可选，默认 20，按 Enter 跳过）
  - 提醒用户：QQ 第一个版本仅支持 C2C 私聊沙盒访问。无群组/频道支持，无内联按钮，无流式预览。
- **Weixin**：不要请求静态 token。相反：
  1. 告诉用户此通道使用扫码登录，而不是手动输入凭证。
  2. 运行 `cd SKILL_DIR && npm run weixin:login`
  3. 帮助程序将写入 `~/.claude-to-im/runtime/weixin-login.html` 并尝试自动在本地浏览器中打开它。
  4. 如果自动打开失败，告诉用户手动打开该 HTML 文件并用微信扫描二维码。
  5. 等待帮助程序报告成功，然后确认已将链接账户保存在本地。
  - 简要解释：链接的 Weixin 账户存储在 `~/.claude-to-im/data/weixin-accounts.json`。再次运行帮助程序将替换之前链接的账户。
  - 简要解释：`CTI_WEIXIN_MEDIA_ENABLED` 仅控制传入的图像/文件/视频下载。对于语音消息，桥接仅接受微信内置语音转文字返回的文本。如果微信不提供文本，桥接将回复错误而不是下载/转录原始音频。

**步骤 3 — 通用设置**

询问运行时、默认工作目录、模型和模式：
- **运行时**：`claude`（默认），`codex`，`auto`
  - `claude` — 使用 Claude Code CLI + Claude Agent SDK（需要安装 `claude` CLI）
  - `codex` — 使用 OpenAI Codex SDK（需要安装 `codex` CLI；通过 `codex auth login` 或 `OPENAI_API_KEY` 进行认证）
  - `auto` — 首先尝试 Claude，如果找不到 Claude CLI 则回退到 Codex
- **工作目录**：默认 `$CWD`
- **模型**（可选）：留空以继承运行时自己的默认模型。如果用户想覆盖，请要求他们输入模型名称。不要硬编码或建议特定的模型名称——可用模型会随时间变化。
- **模式**：`code`（默认），`plan`，`ask`

**步骤 4 — 写入配置并验证**

1. 显示一个最终汇总表，其中包含所有设置（秘密掩码到最后 4 个字符）
2. 要求用户确认后再写入
3. 使用 Bash 创建目录结构：`mkdir -p ~/.claude-to-im/{data,logs,runtime,data/messages}`
4. 使用 Write 创建 `~/.claude-to-im/config.env`，其中包含所有设置以 KEY=VALUE 格式
5. 使用 Bash 设置权限：`chmod 600 ~/.claude-to-im/config.env`
6. 验证 token——阅读 `SKILL_DIR/references/token-validation.md` 以了解每个平台的精确命令和预期响应。这可以捕获拼写错误和错误的凭证，在用户尝试启动守护进程之前。对于 Weixin，成功的扫码登录已视为验证。
7. 报告结果，使用汇总表。如果任何验证失败，解释可能是什么问题以及如何修复。
8. 成功后，告诉用户："设置完成！运行 `/claude-to-im start` 以启动桥接。"

### `start`

**预检查**：验证 `~/.claude-to-im/config.env` 是否存在（见“配置检查”部分）。没有它，守护进程将立即崩溃并留下一个过时的 PID 文件。

运行：`bash "SKILL_DIR/scripts/daemon.sh" start`

将输出显示给用户。如果失败，告诉用户：
- 运行 `doctor` 进行诊断：`/claude-to-im doctor`
- 检查最近的日志：`/claude-to-im logs`

### `stop`

运行：`bash "SKILL_DIR/scripts/daemon.sh" stop`

### `status`

运行：`bash "SKILL_DIR/scripts/daemon.sh" status`

### `logs`

从参数中提取可选的行数 N（默认 50）。
运行：`bash "SKILL_DIR/scripts/daemon.sh" logs N`

### `reconfigure`

1. 从 `~/.claude-to-im/config.env` 读取当前配置
2. 以清晰的表格格式显示当前设置，所有秘密掩码（仅显示最后 4 个字符）
3. 使用 AskUserQuestion 询问用户想更改什么
4. 收集新值时，告诉用户在哪里找到值；只有在他们要求帮助时才显示来自 `SKILL_DIR/references/setup-guides.md` 的完整指南
5. 原子更新配置文件（写入临时文件，重命名）
6. 重新验证任何更改的 token
7. 提醒用户："运行 `/claude-to-im stop` 然后 `/claude-to-im start` 以应用更改。"

如果用户在 `reconfigure` 期间想切换 Weixin 账户，再次运行 `cd SKILL_DIR && npm run weixin:login`。每次成功的扫描将替换之前链接的本地账户。

### `doctor`

运行：`bash "SKILL_DIR/scripts/doctor.sh"`

显示结果并建议任何失败的修复。常见修复：
- SDK cli.js 缺失 → `cd SKILL_DIR && npm install`
- dist/daemon.mjs 过期 → `cd SKILL_DIR && npm run build`
- 配置缺失 → 运行 `setup`
- Weixin 账户缺失/过期 → `cd SKILL_DIR && npm run weixin:login`
- Weixin 语音消息报告缺少语音转文字 → 启用微信自带的语音转录并重新发送；桥接不转录原始语音音频

对于更复杂的问题（消息未收到，权限超时，高内存，过时的 PID 文件），请阅读 `SKILL_DIR/references/troubleshooting.md` 以获取详细的诊断步骤。

**Feishu 升级说明**：如果用户从此技能的旧版本升级，并且 Feishu 返回权限错误（例如，流式卡片不工作，输入指示器失败，权限按钮无响应），根本原因是 Feishu 后端缺少权限或回调。请用户参考 `SKILL_DIR/references/setup-guides.md` 中的“从旧版本升级”部分——他们需要添加新的范围 (`cardkit:card:write`, `cardkit:card:read`, `im:message:update`, `im:message.reactions:read`, `im:message.reactions:write_only`)，添加 `card.action.trigger` 回调，并重新发布应用。升级需要两个发布周期，因为添加回调需要活动的 WebSocket 连接（桥接必须运行）。

## 注意事项

- 输出中始终掩码秘密（仅显示最后 4 个字符）——用户经常在错误报告中分享终端输出，因此暴露的 token 将构成安全事件。
- 在启动守护进程之前始终检查 config.env——没有它，进程将在启动时崩溃并留下一个过时的 PID 文件，这将阻止未来的启动（需要手动清理）。
- 守护进程作为由平台监督器管理的后台 Node.js 进程运行（macOS 上的 launchd，Linux 上的 setsid，Windows 上的 WinSW/NSSM）。
- 配置持久化在 `~/.claude-to-im/config.env`——跨会话持久化。
