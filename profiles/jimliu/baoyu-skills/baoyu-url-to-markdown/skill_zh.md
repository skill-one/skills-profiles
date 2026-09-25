# URL转换为Markdown

使用`baoyu-fetch` CLI（Chrome CDP + 特定站点适配器）获取任意URL，并将其转换为干净的Markdown格式。

## 用户输入工具

当此技能提示用户时，请遵循以下工具选择规则（优先级顺序）：

1. **优先使用**当前代理运行时暴露的**内置用户输入工具** — 例如，`AskUserQuestion`、`request_user_input`、`clarify`、`ask_user`或任何等效工具。
2. **降级处理**：如果没有此类工具，则发出编号的纯文本消息，并要求用户回复所选的数字/答案以回答每个问题。
3. **批量处理**：如果该工具支持每次调用多个问题，则将所有适用问题合并为单个调用；如果仅支持单个问题，则按优先级顺序逐个询问。

下方的具体`AskUserQuestion`引用仅为示例 — 在其他运行时中替换本地等效工具。

## CLI配置

**重要提示**：CLI源代码已包含在`{baseDir}/scripts/lib`中。`scripts/package.json`仅安装第三方运行时依赖项。

**代理执行说明**：
1. 确定此`SKILL.md`文件的目录路径作为`{baseDir}`。
2. 解析`${BUN}`运行时：如果已安装`bun` → `bun`；否则建议安装Bun。
3. 如果`{baseDir}/scripts/node_modules`不存在，则运行`${BUN} install --cwd {baseDir}/scripts`。
4. `${READER}` = `{baseDir}/scripts/baoyu-fetch`。
5. 将此文档中的所有`${READER}`替换为解析后的值。

## 偏好设置（EXTEND.md）

按优先级顺序检查EXTEND.md — 第一个找到的设置将生效：

| 优先级 | 路径 | 范围 |
|--------|------|-------|
| 1 | `.baoyu-skills/baoyu-url-to-markdown/EXTEND.md` | 项目 |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-url-to-markdown/EXTEND.md` | XDG |
| 3 | `$HOME/.baoyu-skills/baoyu-url-to-markdown/EXTEND.md` | 用户主目录 |

| 结果 | 操作 |
|------|------|
| 找到 | 读取、解析、应用设置 |
| 未找到 | **必须**运行首次设置（见下文） — 不要静默创建默认值 |

**EXTEND.md支持**：默认下载媒体、默认输出目录。

### 首次设置 ⛔ 阻塞

当EXTEND.md未找到时，您**必须**使用`AskUserQuestion`收集偏好设置，然后再创建EXTEND.md。**永远不要**使用静默默认值创建EXTEND.md。生成过程**阻塞**，直到设置完成。将所有三个问题批量合并为单个调用：

- **Q1 — 媒体**（标题"媒体"）："如何处理页面中的图片和视频？"
  - "每次询问（推荐）" — 每次保存后提示
  - "始终下载" — 下载到本地`imgs/`和`videos/`
  - "从不下载" — 保持远程URL
- **Q2 — 输出**（标题"输出"）："默认输出目录？"
  - "url-to-markdown（推荐）" — 保存到`./url-to-markdown/{domain}/{slug}.md`
  - 用户可以选择"其他"并输入自定义路径
- **Q3 — 保存**（标题"保存"）："偏好设置保存位置？"
  - "用户（推荐）" — `~/.baoyu-skills/`（所有项目）
  - "项目" — `.baoyu-skills/`（仅此项目）

回答后，写入EXTEND.md，确认"偏好设置保存到[path]"，然后继续。

完整模板：[references/config/first-time-setup.md](references/config/first-time-setup.md)。

### 支持的键

| 键 | 默认值 | 值 | 描述 |
|------|--------|------|------|
| `download_media` | `ask` | `ask` / `1` / `0` | `ask` = 每次提示，`1` = 始终，`0` = 从不 |
| `default_output_dir` | 空值 | 路径或空值 | 默认输出目录（空值 = `./url-to-markdown/` |

**EXTEND.md → CLI映射**：

| EXTEND.md键 | CLI参数 | 备注 |
|------------|--------|------|
| `download_media: 1` | `--download-media` | 需要`--output`设置 |
| `default_output_dir: ./posts/` | 代理构造`--output ./posts/{domain}/{slug}.md` | 代理生成路径，不是直接标志 |

**值优先级**：CLI参数 → EXTEND.md → 技能默认值。

## 使用方法

```bash
# 默认：无头捕获，Markdown输出到stdout
${READER} <url>

# 保存到文件
${READER} <url> --output article.md

# 保存并下载媒体
${READER} <url> --output article.md --download-media

# 等待交互（登录/CAPTCHA）— 自动检测并继续
${READER} <url> --wait-for interaction --output article.md

# 等待交互 — 手动控制（按Enter继续）
${READER} <url> --wait-for force --output article.md

# JSON输出
${READER} <url> --format json --output article.json

# 强制特定适配器
${READER} <url> --adapter youtube --output transcript.md
```

## 选项

| 选项 | 描述 |
|------|------|
| `<url>` | 要获取的URL |
| `--output <path>` | 输出文件路径（默认：stdout） |
| `--format <type>` | 输出格式：`markdown`（默认）或`json` |
| `--json` | `--format json`的简写 |
| `--adapter <name>` | 强制适配器：`x`、`youtube`、`hn`或`generic`（默认：自动检测） |
| `--headless` | 强制无头Chrome（无可见窗口） |
| `--wait-for <mode>` | 交互等待模式：`none`（默认）、`interaction`或`force` |
| `--wait-for-interaction` | `--wait-for interaction`的别名 |
| `--wait-for-login` | `--wait-for interaction`的别名 |
| `--timeout <ms>` | 页面加载超时（默认：30000） |
| `--interaction-timeout <ms>` | 登录/CAPTCHA等待超时（默认：600000 = 10分钟） |
| `--interaction-poll-interval <ms>` | 交互检查的轮询间隔（默认：1500） |
| `--download-media` | 下载图片/视频到本地`imgs/`和`videos/`，重写Markdown链接。需要`--output` |
| `--media-dir <dir>` | 下载媒体的基目录（默认：与`--output`目录相同） |
| `--cdp-url <url>` | 重用现有的Chrome DevTools Protocol端点 |
| `--browser-path <path>` | 自定义Chrome/Chromium二进制文件路径 |
| `--chrome-profile-dir <path>` | Chrome用户数据目录（默认：`BAOYU_CHROME_PROFILE_DIR`环境变量或`./baoyu-skills/chrome-profile`） |
| `--debug-dir <dir>` | 写入调试文件（document.json、markdown.md、page.html、network.json） |

## 代理质量门

**关键**：将默认无头捕获视为临时方案。某些网站在无头模式下渲染不同，可能无声地返回低质量内容而不会触发CLI失败。

每次无头运行后，检查保存的Markdown。参见[references/quality-gate.md](references/quality-gate.md)获取完整检查清单、恢复工作流程和捕获模式表。每当运行看起来可疑或用户询问登录/CAPTCHA处理时，请阅读。

## 输出路径生成

代理必须构造输出文件路径 — `baoyu-fetch`不会自动生成路径。

**算法**：
1. 从EXTEND.md的`default_output_dir`或默认`./url-to-markdown/`确定基目录。
2. 从URL提取域名（例如，`example.com`）。
3. 从URL路径或页面标题生成slug（连字符形式，2-6个词）。
4. 构建：`{base_dir}/{domain}/{slug}/{slug}.md` — 每个URL都有自己的目录，以便媒体文件保持隔离。
5. 冲突解决：追加时间戳`{slug}-YYYYMMDD-HHMMSS/{slug}-YYYYMMDD-HHMMSS.md`。

将构造的路径传递给`--output`。媒体文件（`--download-media`）保存到Markdown文件旁边的子目录中，保持每个URL的资产自包含。

## 适配器与媒体

参见[references/adapters.md](references/adapters.md)获取适配器目录（X、YouTube、Hacker News、通用），每个适配器的说明、媒体下载流程（`ask` / 始终 / 从不）和JSON输出模式。在回答适配器特定问题或处理媒体提示之前，请阅读。

## 环境变量

| 变量 | 描述 |
|------|------|
| `BAOYU_CHROME_PROFILE_DIR` | Chrome用户数据目录（也可以使用`--chrome-profile-dir`） |

**故障排除**：Chrome未找到 → 使用`--browser-path`。超时 → 增加`--timeout`。登录/CAPTCHA → `--wait-for interaction`。调试 → `--debug-dir`以检查捕获的HTML和网络日志。

## 扩展支持

通过EXTEND.md进行自定义配置。参见上述**偏好设置**部分中的路径和支持的键。
