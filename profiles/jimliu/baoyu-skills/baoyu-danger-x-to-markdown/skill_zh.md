# X 转换为 Markdown

将 X 内容转换为 Markdown：
- 推文/线程 → 带有 YAML 前置内容的 Markdown
- X 文章 → 完整内容提取

## 用户输入工具

当此技能提示用户时，请遵循以下工具选择规则（优先级顺序）：

1. **优先使用**当前代理运行时暴露的内置用户输入工具 — 例如，`AskUserQuestion`、`request_user_input`、`clarify`、`ask_user` 或任何等效工具。
2. **备用方案**：如果不存在此类工具，则发出编号的纯文本消息，并要求用户回复每个问题的选择编号/答案。
3. **批量处理**：如果工具支持每次调用多个问题，则将所有适用问题组合为单个调用；如果仅支持单个问题，则按优先级顺序逐个询问。

下方的具体 `AskUserQuestion` 引用仅为示例 — 在其他运行时中替换本地等效工具。

## 脚本目录

位于 `scripts/` 子目录中的脚本。

**路径解析**：
1. `{baseDir}` = 此 SKILL.md 的目录
2. 脚本路径 = `{baseDir}/scripts/main.ts`
3. 解析 `${BUN_X}` 运行时：如果已安装 `bun` → `bun`；如果可用 `npx` → `npx -y bun`；否则建议安装 bun

## 同意要求

**在进行任何转换之前**，检查并获取同意。

### 同意流程

**步骤 1**：检查同意文件

```bash
# macOS
cat ~/Library/Application\ Support/baoyu-skills/x-to-markdown/consent.json

# Linux
cat ~/.local/share/baoyu-skills/x-to-markdown/consent.json
```

**步骤 2**：如果 `accepted: true` 且 `disclaimerVersion: "1.0"` → 打印警告并继续：
```
Warning: 使用逆向工程的 X API。已接受于: <acceptedAt>
```

**步骤 3**：如果缺失或版本不匹配 → 显示免责声明：
```
免责声明

本工具使用逆向工程的 X API，非官方版本。

风险：
- 如果 X 更改 API 可能会失效
- 无保证或支持
- 可能导致账号限制
- 自行承担风险

接受条款并继续？
```

使用 `AskUserQuestion` 带选项： "是，我接受" | "否，我拒绝"

**步骤 4**：在同意 → 创建同意文件：
```json
{
  "version": 1,
  "accepted": true,
  "acceptedAt": "<ISO timestamp>",
  "disclaimerVersion": "1.0"
}
```

**步骤 5**：在拒绝 → 输出 "User declined. Exiting." 并停止。

## 偏好设置 (EXTEND.md)

按优先级顺序检查 EXTEND.md — 第一个找到的优先：

| 优先级 | 路径 | 范围 |
|--------|------|-------|
| 1 | `.baoyu-skills/baoyu-danger-x-to-markdown/EXTEND.md` | 项目 |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-danger-x-to-markdown/EXTEND.md` | XDG |
| 3 | `$HOME/.baoyu-skills/baoyu-danger-x-to-markdown/EXTEND.md` | 用户主目录 |

| 结果 | 操作 |
|------|------|
| 找到 | 读取、解析、应用设置 |
| 未找到 | **必须**运行首次设置（见下文） — 不要静默创建默认值 |

**EXTEND.md 支持**：默认下载媒体、默认输出目录。

### 首次设置 (BLOCKING)

**关键**：当 EXTEND.md 未找到时，你**必须使用 `AskUserQuestion`** 在创建 EXTEND.md 之前询问用户他们的偏好。**永远不要**在询问前用默认值创建 EXTEND.md。这是一个**阻塞**操作 — 在设置完成前**不要**进行任何转换。

使用 `AskUserQuestion` 在**一次调用**中包含所有问题：

**问题 1** — 标题: "媒体"，问题: "如何处理推文中的图片和视频？"
- "每次询问（推荐）" — 保存 Markdown 后，询问是否下载媒体
- "始终下载" — 始终下载媒体到本地 imgs/ 和 videos/ 目录
- "从不下载" — 在 Markdown 中保留原始远程 URL

**问题 2** — 标题: "输出"，问题: "默认输出目录？"
- "x-to-markdown (推荐)" — 保存到 ./x-to-markdown/{username}/{tweet-id}.md
- (用户可以选择 "其他" 来输入自定义路径)

**问题 3** — 标题: "保存"，问题: "在哪里保存偏好设置？"
- "用户 (推荐)" — ~/.baoyu-skills/（所有项目）
- "项目" — .baoyu-skills/（仅此项目）

用户回答后，在选定位置创建 EXTEND.md，确认 "偏好设置保存到 [路径]"，然后继续。

完整参考：[references/config/first-time-setup.md](references/config/first-time-setup.md)

### 支持的键

| 键 | 默认值 | 值 | 描述 |
|----|--------|-----|------|
| `download_media` | `ask` | `ask` / `1` / `0` | `ask` = 每次提示，`1` = 始终下载，`0` = 从不 |
| `default_output_dir` | 空值 | 路径或空值 | 默认输出目录（空值 = `./x-to-markdown/` |

**值优先级**：
1. 命令行参数 (`--download-media`, `-o`)
2. EXTEND.md
3. 技能默认值

## 使用方法

```bash
${BUN_X} {baseDir}/scripts/main.ts <url>
${BUN_X} {baseDir}/scripts/main.ts <url> -o output.md
${BUN_X} {baseDir}/scripts/main.ts <url> --download-media
${BUN_X} {baseDir}/scripts/main.ts <url> --json
```

## 选项

| 选项 | 描述 |
|------|------|
| `<url>` | 推文或文章 URL |
| `-o <path>` | 输出路径 |
| `--json` | JSON 输出 |
| `--download-media` | 下载图片/视频资源到本地 `imgs/` 和 `videos/`，并重写 Markdown 链接到本地相对路径 |
| `--login` | 仅刷新 Cookie |

## 支持的 URL

- `https://x.com/<user>/status/<id>`
- `https://twitter.com/<user>/status/<id>`
- `https://x.com/i/article/<id>`

## 输出

```markdown
---
url: "https://x.com/user/status/123"
author: "Name (@user)"
tweetCount: 3
coverImage: "https://pbs.twimg.com/media/example.jpg"
---

内容...
```

**文件结构**：`x-to-markdown/{username}/{tweet-id}/{content-slug}.md`

当 `--download-media` 启用时：
- 图片保存到 Markdown 文件旁边的 `imgs/`
- 视频保存到 Markdown 文件旁边的 `videos/`
- Markdown 媒体链接重写为本地相对路径

## 媒体下载工作流

基于 EXTEND.md 中的 `download_media` 设置：

| 设置 | 行为 |
|------|------|
| `1` (始终) | 使用 `--download-media` 标志运行脚本 |
| `0` (从不) | 不使用 `--download-media` 标志运行脚本 |
| `ask` (默认) | 遵循以下每次询问流程 |

### 每次询问流程

1. 运行脚本**不带** `--download-media` → 保存 Markdown
2. 检查保存的 Markdown 中的远程媒体 URL（图片/视频链接中的 `https://`）
3. **如果未找到远程媒体** → 完成，无需提示
4. **如果找到远程媒体** → 使用 `AskUserQuestion`：
   - 标题: "媒体"，问题: "下载 N 张图片/视频到本地文件？"
   - "是" — 下载到本地目录
   - "否" — 保留远程 URL
5. 如果用户确认 → 再次运行脚本**带** `--download-media`（用本地化链接覆盖 Markdown）

## 认证

1. **环境变量**（推荐）：`X_AUTH_TOKEN`、`X_CT0`
2. **Chrome 登录**（备用）：自动打开 Chrome，本地缓存 Cookie

## 扩展支持

通过 EXTEND.md 进行自定义配置。参见**偏好设置**部分了解路径和支持的选项。
