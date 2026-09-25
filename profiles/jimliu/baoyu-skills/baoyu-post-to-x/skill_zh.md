# 发布到 X (Twitter)

通过真实的 Chrome 浏览器发布文本、图片、视频和长文到 X。

在 Codex 中，不要混淆这些浏览器路径：
- **Codex Chrome 插件 / `@chrome` / Chrome 扩展**：使用捆绑的 `chrome:Chrome` 技能及其 Node REPL 浏览器客户端。每当用户说 "Codex Chrome 插件"、"Codex 自带的 Chrome 插件"、"@chrome" 或类似内容时，都需要使用此模式。
- **Chrome 计算机使用**：仅在用户要求计算机使用或未声明 Chrome 插件偏好且计算机使用可用时，使用 `mcp__computer_use__.*` 针对可见的 Google Chrome UI。
- **CDP 脚本模式**：仅在选定的模式不可用或用户明确要求 CDP/脚本模式时使用。

## 脚本目录

**重要提示**：所有脚本都位于此技能的 `scripts/` 子目录中。

**代理执行说明**：
1. 将此 `SKILL.md` 文件的目录路径确定为 `{baseDir}`。
2. 脚本路径 = `{baseDir}/scripts/<script-name>.ts`。
3. 将此文档中的所有 `{baseDir}` 替换为实际路径。
4. 解析 `${BUN_X}` 运行时：如果已安装 `bun` → `bun`；如果 `npx` 可用 → `npx -y bun`；否则建议安装 bun。

**脚本参考**：
| 脚本 | 目的 |
|------|------|
| `scripts/x-browser.ts` | 常规发布（文本 + 图片），CDP 回退 |
| `scripts/x-video.ts` | 视频发布（文本 + 视频），CDP 回退 |
| `scripts/x-quote.ts` | 带评论的引用推文，CDP 回退 |
| `scripts/x-article.ts` | 长文发布（Markdown），CDP 回退 |
| `scripts/md-to-html.ts` | Markdown → HTML 转换 |
| `scripts/copy-to-clipboard.ts` | 复制内容到剪贴板 |
| `scripts/paste-from-clipboard.ts` | 发送真实的粘贴按键 |
| `scripts/check-paste-permissions.ts` | 验证环境和权限 |

## 执行模式选择（必选）

在与 X 交互之前，选择一个执行模式：

1. 如果用户明确要求 Codex Chrome 插件、`@chrome`、Chrome 扩展或 "Codex 自带的 Chrome 插件"，使用 **Codex Chrome 插件模式**。不要首先调用计算机使用。
2. 如果用户明确要求 Chrome 计算机使用，使用 **Chrome 计算机使用模式**。不要在没有告知用户并获取批准的情况下回退到 CDP、Playwright、应用内浏览器或 Chrome 插件。
3. 如果用户明确要求 CDP/脚本模式，使用 **CDP 脚本模式**。
4. 否则，优先使用 **Chrome 计算机使用模式**。对于 Markdown **X 文章**（本地内容图片），使用经过测试的 X 编辑器流程：从工具栏 (`插入` -> `媒体` -> 对话框图标按钮 `添加照片或视频`) 中插入每个正文图片到其占位符，然后删除占位符文本。仅在选定的浏览器控制模式不可用或 UI 上传/选择流程不可靠时使用 CDP 脚本模式。

永远不要使用应用内浏览器进行 X 发布工作流。

## Codex Chrome 插件模式

当用户请求 Codex Chrome 插件、`@chrome` 或 Chrome 扩展路径时，使用此模式。这使用用户的真实 Chrome 配置文件并通过捆绑的 Chrome 插件进行 X 登录，而不是计算机使用和 CDP。

**设置**
1. 在进行浏览器工作之前加载 `chrome:Chrome` 技能。
2. 如果 Node REPL `js` 工具尚未可见，使用 `tool_search` 查找 `node_repl js`。
3. 按照Chrome技能指定的方式初始化 Chrome 浏览器客户端，然后运行一个轻量级调用，例如 `browser.user.openTabs()` 以验证扩展连接。
4. 如果第一个轻量级调用失败，等待 2 秒后重试一次。如果仍然失败，请遵循 Chrome 技能的扩展检查和恢复步骤。如果检查通过但通信仍然失败，请在打开新的 Chrome 窗口之前询问用户。不要无声地切换到计算机使用或 CDP。

**一般规则**
- 使用 Chrome 插件的 `browser.tabs.*`、`tab.playwright.*`、`tab.cua.*` 和文件选择器 API 进行 X UI 操作。
- 允许使用 Shell 命令进行 Markdown 预处理和富 HTML 剪贴板准备。对于 X 文章正文图片，不要依赖图片剪贴板粘贴；使用编辑器的 `插入` -> `媒体` 上传流程。
- 如果文件上传失败并显示 `Not allowed`，请告知用户：`要启用文件上传，请前往 Chrome 的 `chrome://extensions`，在 Codex 扩展下点击 `Details`，并启用 "Allow access to file URLs"。详情请参阅 https://developers.openai.com/codex/app/chrome-extension#upload-files`。
- 如果 Chrome 插件报告 `native pipe is closed`，在 2 秒后重试轻量级浏览器调用，然后运行 Chrome 技能健康检查。如果 Chrome 正在运行、扩展已启用且原生主机清单正确，请询问权限以打开新的 Chrome 窗口并重试。不要通过损坏的管道持续发送浏览器操作。
- 在当前对话中未经用户明确最终确认，永远不要点击 `发布`、`发布` 或任何外部可见的提交操作。

**X 文章**
1. 转换 Markdown 并保留图片映射：
   ```bash
   ${BUN_X} {baseDir}/scripts/md-to-html.ts article.md --save-html /tmp/x-article-body.html > /tmp/x-article.json
   ```
2. 读取 JSON 输出中的 `title`、`coverImage` 和 `contentImages`（`placeholder` → `localPath`）。
3. 在 `https://x.com/compose/articles` 打开或创建文章草稿。
4. 使用 Chrome 插件的文件选择器流程上传封面。如果上传被扩展权限阻止，请停止并报告上述确切权限修复步骤。
5. 填写标题，然后复制富 HTML：
   ```bash
   ${BUN_X} {baseDir}/scripts/copy-to-clipboard.ts html --file /tmp/x-article-body.html
   ```
6. 使用 Chrome 插件通过真实粘贴按键粘贴到文章正文。在 macOS 上使用 `Meta+V`。
7. 验证编辑器文本包含文章正文和 `XIMGPH_` 占位符。不要依赖 `tab.clipboard.readText()` 作为 Shell 剪贴板写入后系统剪贴板的证明；如有必要，可通过 `pbpaste` 在 macOS 上验证。
8. 对于 `contentImages` 中的每个占位符按顺序：
   - 定位可见的占位符文本（例如 `XIMGPH_3`）并点击它以设置插入点。
   - 打开工具栏 `插入` 下拉菜单，选择 `媒体`，然后点击模态框的图标按钮，其 `aria-label` 标记为 `Add photos or video`。
   - 使用文件选择器选择该图片的 `localPath`。
   - 等待图片块出现且任何上传活动完成。
   - 如果占位符 `XIMGPH_N` 仍然位于插入的图片上方，请首先选择该占位符并按 `Delete`。如果 `Delete` 失败且选中的文本确认是占位符，请使用 `Backspace`。
   - 验证该 `XIMGPH_N` 的占位符计数为 `0`。
9. 打开预览并验证标题、封面、正文、链接和图片。
10. 在点击 `发布` 之前，请求明确的确认。

## 偏好设置 (EXTEND.md)

按优先级顺序检查 EXTEND.md — 第一个找到的优先：
| 优先级 | 路径 | 范围 |
|-------|------|------|
| 1 | `.baoyu-skills/baoyu-post-to-x/EXTEND.md` | 项目 |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-post-to-x/EXTEND.md` | XDG |
| 3 | `$HOME/.baoyu-skills/baoyu-post-to-x/EXTEND.md` | 用户主目录 |

如果没有找到，则使用默认值。

**EXTEND.md 支持**：默认 Chrome 配置文件

## 前置条件

- Google Chrome 或 Chromium
- `bun` 运行时
- 首次运行：手动登录 X（会话保存）

## 预飞行检查（可选）

首次使用前，建议运行环境检查。如果用户选择跳过，可以跳过。

```bash
${BUN_X} {baseDir}/scripts/check-paste-permissions.ts
```

检查项：Chrome、配置文件隔离、Bun、可访问性、剪贴板、粘贴按键、Chrome 冲突。

**如果任何检查失败**，按项目提供修复指导：

| 检查项 | 修复 |
|-------|------|
| Chrome | 安装 Chrome 或设置 `X_BROWSER_CHROME_PATH` 环境变量 |
| 配置文件目录 | 位于 `baoyu-skills/chrome-profile` 的共享配置文件（见 CLAUDE.md Chrome 配置文件部分） |
| Bun 运行时 | macOS: `brew install oven-sh/bun/bun` 或 `npm install -g bun` |
| 可访问性 (macOS) | 系统设置 → 隐私与安全 → 可访问性 → 启用终端应用 |
| 剪贴板复制 | 确保 Swift/AppKit 可用（macOS Xcode CLI 工具：`xcode-select --install`） |
| 粘贴按键 (macOS) | 与可访问性修复相同 |
| 粘贴按键 (Linux) | 安装 `xdotool` (X11) 或 `ydotool` (Wayland) |

## 参考

- **常规发布**：有关手动工作流、故障排除和技术细节，请参阅 `references/regular-posts.md`。
- **X 文章**：有关长文发布指南，请参阅 `references/articles.md`。

---

## Chrome 计算机使用模式

当用户明确要求 Chrome 计算机使用，或未声明 Chrome 插件偏好且 Codex 可以通过计算机使用控制 `Google Chrome` 时，使用此模式。这使用用户的现有 Chrome 窗口、Cookie、登录、扩展和 X 会话。

**一般规则**：
- 每个控制 Chrome 的助手回合开始时，调用 `get_app_state` 针对的是 `Google Chrome`。
- 优先使用元素索引操作；仅在编辑器文本选择或拖动选择时使用坐标。
- 在此模式下，除非用户批准模式更改，否则不要使用应用内浏览器、Chrome 插件、Playwright 或 CDP 进行 X UI 操作。
- 在当前对话中未经用户明确最终确认，永远不要点击 `发布`、`发布` 或任何外部可见的提交操作。

**常规发布**：
1. 打开或导航 Chrome 到 `https://x.com/compose/post`。
2. 使用计算机使用在作曲家中输入发布文本。
3. 对于每个图片，运行：
   ```bash
   ${BUN_X} {baseDir}/scripts/copy-to-clipboard.ts image /绝对路径/to/image.png
   ```
4. 使用计算机使用粘贴（macOS 上 `super+v`，Windows/Linux 上 `control+v`），然后等待 X 完成媒体上传。
5. 在点击 `发布` 之前，请求确认。

**视频发布**：
1. 打开或导航 Chrome 到 `https://x.com/compose/post`。
2. 在作曲家中输入发布文本。
3. 使用可见的媒体上传/文件选择器 UI 附加视频。
4. 等待上传和处理完成。
5. 在点击 `发布` 之前，请求确认。

**引用推文**：
1. 在 Chrome 中打开推文 URL。
2. 使用可见的引用/转发 UI 选择引用。
3. 输入评论。
4. 在点击 `发布` 之前，请求确认。

**X 文章**：
1. 转换 Markdown 并保留图片映射：
   ```bash
   ${BUN_X} {baseDir}/scripts/md-to-html.ts article.md --save-html /tmp/x-article-body.html > /tmp/x-article.json
   ```
2. 读取 JSON 输出中的 `title`、`coverImage` 和 `contentImages`（`placeholder` → `localPath`）。
3. 在 Chrome 中打开 `https://x.com/compose/articles`，创建或打开草稿，如果存在则上传封面，并填写标题。
4. 将富 HTML 复制到剪贴板：
   ```bash
   ${BUN_X} {baseDir}/scripts/copy-to-clipboard.ts html --file /tmp/x-article-body.html
   ```
5. 使用计算机使用粘贴到文章正文。
6. 对于 `contentImages` 中的每个占位符按顺序：
   - 定位精确的可见占位符文本（例如 `XIMGPH_3`）并点击它以设置插入点。
   - 打开工具栏 `插入` 下拉菜单，选择 `媒体`，然后点击模态框的图标按钮，其 `aria-label` 标记为 `Add photos or video`。
   - 使用原生文件选择器选择该图片的 `localPath`。
   - 等待图片块出现且任何上传活动完成。
   - 如果占位符 `XIMGPH_N` 仍然位于插入的图片上方，请首先选择该占位符并按 `Delete`。如果 `Delete` 失败且选中的文本确认是占位符，请使用 `Backspace`。
7. 验证没有 `XIMGPH_` 占位符剩余且预期图片出现。
8. 打开预览并验证标题、封面、正文、链接和图片。
9. 在点击 `发布` 之前，请求明确的确认。

如果计算机使用选择、工具栏上传或文件选择器控制变得不可靠，请停止并报告障碍，而不是无声地切换到 Chrome 插件或 CDP。

---

## CDP 脚本模式（回退）

仅在选定的浏览器控制模式不可用、不可靠或明确不请求时，使用下面的脚本部分。这些脚本通过 CDP 启动或重用真实的 Chrome 实例，并保持浏览器打开以供审查。

除非用户明确要求 Codex Chrome 插件或 Chrome 计算机使用，并且用户在解释障碍后批准回退，否则不要使用 CDP 脚本模式。

---

## 发布类型选择

除非用户明确指定发布类型：
- **纯文本** + 在 10,000 个字符以内 → **常规发布**（高级会员支持最多 10,000 个字符，非高级会员：280）
- **Markdown 文件** (.md) → **X 文章**

## 常规发布

```bash
${BUN_X} {baseDir}/scripts/x-browser.ts "Hello!" --image ./photo.png
```

**参数**：
| 参数 | 描述 |
|------|------|
| `<text>` | 发布内容（位置参数） |
| `--image <path>` | 图片文件（可重复，最多 4 个） |
| `--profile <dir>` | 自定义 Chrome 配置文件 |

**注意**：脚本打开浏览器并预填内容。用户手动审查和发布。

**Codex 模式说明**：如果用户明确请求 Codex Chrome 插件，使用 **Codex Chrome 插件模式**。否则，如果启用 Chrome 计算机使用，使用 **Chrome 计算机使用模式**，而不是运行 `x-browser.ts`。

---

## 视频发布

文本 + 视频文件。

```bash
${BUN_X} {baseDir}/scripts/x-video.ts "Check this out!" --video ./clip.mp4
```

**参数**：
| 参数 | 描述 |
|------|------|
| `<text>` | 发布内容（位置参数） |
| `--video <path>` | 视频文件（MP4、MOV、WebM） |
| `--profile <dir>` | 自定义 Chrome 配置文件 |

**注意**：脚本打开浏览器并预填内容。用户手动审查和发布。

**Codex 模式说明**：如果用户明确请求 Codex Chrome 插件，使用 **Codex Chrome 插件模式**。否则，如果启用 Chrome 计算机使用，使用 **Chrome 计算机使用模式**，而不是运行 `x-video.ts`。

**限制**：常规 140 秒最大，高级会员 60 分钟。处理时间：30-60 秒。

---

## 引用推文

引用现有推文并添加评论。

```bash
${BUN_X} {baseDir}/scripts/x-quote.ts https://x.com/user/status/123 "Great insight!"
```

**参数**：
| 参数 | 描述 |
|------|------|
| `<tweet-url>` | 引用 URL（位置参数） |
| `<comment>` | 评论文本（位置参数，可选） |
| `--profile <dir>` | 自定义 Chrome 配置文件 |

**注意**：脚本打开浏览器并预填内容。用户手动审查和发布。

**Codex 模式说明**：如果用户明确请求 Codex Chrome 插件，使用 **Codex Chrome 插件模式**。否则，如果启用 Chrome 计算机使用，使用 **Chrome 计算机使用模式**，而不是运行 `x-quote.ts`。

---

## X 文章

长文 Markdown 文件（需要 X 高级会员）。

```bash
${BUN_X} {baseDir}/scripts/x-article.ts article.md
${BUN_X} {baseDir}/scripts/x-article.ts article.md --cover ./cover.jpg
```

**参数**：
| 参数 | 描述 |
|------|------|
| `<markdown>` | Markdown 文件（位置参数） |
| `--cover <path>` | 封面图片 |
| `--title <text>` | 覆盖标题 |

**前文**：YAML 前文支持 `title`、`cover_image`。

**Codex 模式说明**：如果用户明确请求 Codex Chrome 插件，请遵循上述 **Codex Chrome 插件模式**。如果用户明确请求 Chrome 计算机使用，请遵循 **Chrome 计算机使用模式**。否则，优先使用 Chrome 计算机使用；对于 Markdown 文章的本地内容图片，在使用工具栏 `插入` -> `媒体` 图片上传工作流之前，回退到 `x-article.ts` 在 **CDP 脚本模式**。

**CDP 回退说明**：脚本打开浏览器并预填文章。除非使用 `--submit`，否则用户手动审查和发布。

**发布安全**：除非用户明确确认最终公开发布操作，否则不要使用 `--submit` 或点击 `发布`。

**发布后检查**：脚本在所有图片插入后自动验证：
- 编辑器内容中剩余的 `XIMGPH_` 占位符
- 预期与实际图片数量

如果检查失败（输出中的警告），请在发布前向用户报告具体问题。

---

## 故障排除

### Chrome 调试端口未就绪

仅 CDP 回退：如果脚本失败并显示 `Chrome debug port not ready` 或 `Unable to connect`，请首先杀死现有的 Chrome CDP 实例，然后重试：

```bash
pkill -f "Chrome.*remote-debugging-port" 2>/dev/null; pkill -f "Chromium.*remote-debugging-port" 2>/dev/null; sleep 2
```

**重要**：这应该是自动完成的 — 当遇到此错误时，杀死 Chrome CDP 实例并重试命令，而无需询问用户。

## 注意事项

- 首次运行：需要手动登录（会话持久）
- 在 Codex Chrome 插件模式和 Chrome 计算机使用模式中，使用用户的现有 Chrome 会话，不要启动单独的 CDP 配置文件
- CDP 脚本默认情况下仅将内容填充到浏览器；用户必须审查和发布，除非明确使用 `--submit`
- 跨平台：macOS、Linux、Windows

## 扩展支持

通过 EXTEND.md 进行自定义配置。有关路径和支持选项，请参阅 **偏好设置** 部分。
