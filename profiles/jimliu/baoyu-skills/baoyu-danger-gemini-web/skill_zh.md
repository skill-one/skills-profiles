# Gemini Web Client

通过 Gemini Web API 进行文本/图像生成。支持参考图像和多轮对话。

## 用户输入工具

当此技能提示用户时，请遵循以下工具选择规则（优先级顺序）：

1. **优先选择** 当前代理运行时暴露的内置用户输入工具 — 例如 `AskUserQuestion`、`request_user_input`、`clarify`、`ask_user` 或任何等效工具。
2. **降级处理**：如果不存在此类工具，则发出编号的纯文本消息，并要求用户回复选择的编号/答案以回答每个问题。
3. **批量处理**：如果工具支持每调用处理多个问题，则将所有适用问题合并为单个调用；如果仅支持单问题，则按优先级顺序逐个询问。

下方的具体 `AskUserQuestion` 引用仅为示例 — 在其他运行时中应替换为本地等效工具。

## 脚本目录

**重要提示**：所有脚本都位于此技能的 `scripts/` 子目录中。

**代理执行说明**：
1. 将此 `SKILL.md` 文件的目录路径确定为目标 `{baseDir}`。
2. 脚本路径 = `{baseDir}/scripts/<脚本名称>.ts`。
3. 解析 `${BUN_X}` 运行时：如果已安装 `bun` → `bun`；如果可用 `npx` → `npx -y bun`；否则建议安装 `bun`。
4. 将此文档中的所有 `{baseDir}` 和 `${BUN_X}` 替换为实际值。

**脚本参考**：
| 脚本 | 目的 |
|------|------|
| `scripts/main.ts` | 文本/图像生成的 CLI 入口 |
| `scripts/gemini-webapi/*` | `gemini_webapi` 的 TypeScript 端口（GeminiClient、类型、工具） |

## 同意检查（必填）

首次使用前，验证用户对逆向工程 API 使用的同意。

**同意文件位置**：
- macOS: `~/Library/Application Support/baoyu-skills/gemini-web/consent.json`
- Linux: `~/.local/share/baoyu-skills/gemini-web/consent.json`
- Windows: `%APPDATA%\baoyu-skills\gemini-web\consent.json`

**流程**：
1. 使用 `accepted: true` 和 `disclaimerVersion: "1.0"` 检查同意文件是否存在。
2. 如果存在有效同意 → 打印 `acceptedAt` 日期的警告，继续执行。
3. 如果无同意 → 显示免责声明，通过 `AskUserQuestion` 询问用户：
   - "是，我同意" → 使用 ISO 时间戳创建同意文件，继续执行。
   - "否，我拒绝" → 输出拒绝消息，停止执行。
4. 同意文件格式：`{"version":1,"accepted":true,"acceptedAt":"<ISO>","disclaimerVersion":"1.0"}`

---

## 偏好设置（EXTEND.md）

按优先级顺序检查 EXTEND.md — 第一个找到的规则生效：

| 优先级 | 路径 | 范围 |
|------|------|------|
| 1 | `.baoyu-skills/baoyu-danger-gemini-web/EXTEND.md` | 项目 |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-danger-gemini-web/EXTEND.md` | XDG |
| 3 | `$HOME/.baoyu-skills/baoyu-danger-gemini-web/EXTEND.md` | 用户主目录 |

如果没有找到，则使用默认值。

**EXTEND.md 支持**：默认模型、代理设置、自定义数据目录。

## 使用方法

```bash
# 文本生成
${BUN_X} {baseDir}/scripts/main.ts "您的提示"
${BUN_X} {baseDir}/scripts/main.ts --prompt "您的提示" --model gemini-3-flash

# 图像生成
${BUN_X} {baseDir}/scripts/main.ts --prompt "一只可爱的猫" --image cat.png
${BUN_X} {baseDir}/scripts/main.ts --promptfiles system.md content.md --image out.png

# 视觉输入（参考图像）
${BUN_X} {baseDir}/scripts/main.ts --prompt "描述这张图片" --reference image.png
${BUN_X} {baseDir}/scripts/main.ts --prompt "创建变体" --reference a.png --image out.png

# 多轮对话
${BUN_X} {baseDir}/scripts/main.ts "记住：42" --sessionId session-abc
${BUN_X} {baseDir}/scripts/main.ts "什么数字？" --sessionId session-abc

# JSON 输出
${BUN_X} {baseDir}/scripts/main.ts "你好" --json
```

## 选项

| 选项 | 描述 |
|------|------|
| `--prompt`, `-p` | 提示文本 |
| `--promptfiles` | 从文件读取提示（连接后） |
| `--model`, `-m` | 模型：gemini-3-pro（默认）、gemini-3-flash、gemini-3-flash-thinking、gemini-3.1-pro-preview |
| `--image [路径]` | 生成图像（默认：generated.png） |
| `--reference`, `--ref` | 视觉输入的参考图像 |
| `--sessionId` | 多轮对话的会话 ID |
| `--list-sessions` | 列出保存的会话 |
| `--json` | 以 JSON 格式输出 |
| `--login` | 刷新 Cookie 后退出 |
| `--cookie-path` | 自定义 Cookie 文件路径 |
| `--profile-dir` | Chrome 配置目录 |

## 模型

| 模型 | 描述 |
|------|------|
| `gemini-3-pro` | 默认，最新 3.0 Pro |
| `gemini-3-flash` | 快速，轻量级 3.0 Flash |
| `gemini-3-flash-thinking` | 3.0 Flash 带思考功能 |
| `gemini-3.1-pro-preview` | 3.1 Pro 预览（空头部，自动路由） |

## 认证

首次运行时将打开浏览器进行 Google 认证。Cookie 自动缓存。

当未设置显式配置目录时，Cookie 刷新可能会重用已运行的本地 Chrome/Chromium 调试会话，该会话绑定到标准用户数据目录。

设置 `--profile-dir` 或 `GEMINI_WEB_CHROME_PROFILE_DIR` 以强制使用专用配置目录并跳过现有会话重用。
这是一个最佳努力 CDP 会话重用路径，不是 Chrome 官方文档中描述的 Chrome DevTools MCP 基于提示的 `--autoConnect` 流程。

支持的浏览器（自动检测）：Chrome、Chrome Canary/Beta、Chromium、Edge。

强制刷新：`--login` 标志。覆盖浏览器：`GEMINI_WEB_CHROME_PATH` 环境变量。

## 环境变量

| 变量 | 描述 |
|------|------|
| `GEMINI_WEB_DATA_DIR` | 数据目录 |
| `GEMINI_WEB_COOKIE_PATH` | Cookie 文件路径 |
| `GEMINI_WEB_CHROME_PROFILE_DIR` | Chrome 配置目录 |
| `GEMINI_WEB_CHROME_PATH` | Chrome 可执行路径 |
| `HTTP_PROXY`, `HTTPS_PROXY` | Google 访问的代理（可在命令中直接设置） |

## 会话

会话文件存储在数据目录下的 `sessions/<id>.json` 中。

包含：`id`、`metadata`（Gemini 聊天状态）、`messages` 数组、时间戳。

## 扩展支持

通过 EXTEND.md 进行自定义配置。请参阅 **偏好设置** 部分以获取路径和支持的选项。
