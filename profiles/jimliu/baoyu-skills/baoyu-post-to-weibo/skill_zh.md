# 发布到微博

通过真实的 Chrome 浏览器发布文本、图片、视频和长文到微博（可绕过反机器人检测）。

## 脚本目录

**重要提示**：所有脚本都位于此技能的 `scripts/` 子目录中。

**代理执行说明**：
1. 确定此 `SKILL.md` 文件的目录路径为 `{baseDir}`
2. 脚本路径 = `{baseDir}/scripts/<脚本名>.ts`
3. 将此文档中的所有 `{baseDir}` 替换为实际路径
4. 解析 `${BUN_X}` 运行时：如果已安装 `bun` → `bun`；如果可用 `npx` → `npx -y bun`；否则建议安装 bun

**脚本参考**：
| 脚本 | 目的 |
|------|---------|
| `scripts/weibo-post.ts` | 普通发布（文本 + 图片） |
| `scripts/weibo-article.ts` | 头条文章发布（Markdown） |
| `scripts/copy-to-clipboard.ts` | 复制内容到剪贴板 |
| `scripts/paste-from-clipboard.ts` | 发送真实粘贴按键 |

## 偏好设置 (EXTEND.md)

按优先级顺序检查 EXTEND.md —— 第一个找到的生效：

| 优先级 | 路径 | 范围 |
|----------|------|-------|
| 1 | `.baoyu-skills/baoyu-post-to-weibo/EXTEND.md` | 项目 |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-post-to-weibo/EXTEND.md` | XDG |
| 3 | `$HOME/.baoyu-skills/baoyu-post-to-weibo/EXTEND.md` | 用户主目录 |

如果没有找到，则使用默认设置。

**EXTEND.md 支持**：默认 Chrome 配置文件

## 前置条件

- Google Chrome 或 Chromium
- `bun` 运行时
- 首次运行：手动登录微博（会话被保存）

---

## 普通发布

文本 + 图片/视频（最多 18 个文件）。发布在微博主页。

```bash
${BUN_X} {baseDir}/scripts/weibo-post.ts "Hello Weibo!" --image ./photo.png
${BUN_X} {baseDir}/scripts/weibo-post.ts "Watch this" --video ./clip.mp4
```

**参数**：
| 参数 | 描述 |
|-----------|-------------|
| `<text>` | 发布内容（位置参数） |
| `--image <路径>` | 图片文件（可重复） |
| `--video <路径>` | 视频文件（可重复） |
| `--profile <目录>` | 自定义 Chrome 配置文件 |

**注意**：脚本会打开浏览器并预填内容。用户需手动审核并发布。

---

## 头条文章

长文 Markdown 文章发布在 `https://card.weibo.com/article/v3/editor`。

```bash
${BUN_X} {baseDir}/scripts/weibo-article.ts article.md
${BUN_X} {baseDir}/scripts/weibo-article.ts article.md --cover ./cover.jpg
```

**参数**：
| 参数 | 描述 |
|-----------|-------------|
| `<markdown>` | Markdown 文件（位置参数） |
| `--cover <路径>` | 封面图片 |
| `--title <文本>` | 覆盖标题（最多 32 个字符，过长会被截断） |
| `--summary <文本>` | 覆盖摘要（最多 44 个字符，过长会自动重新生成） |
| `--profile <目录>` | 自定义 Chrome 配置文件 |

**YAML 前置字段**：`title`、`summary`、`cover_image` 在 YAML 前置字段中受支持。

**字符限制**：
- 标题：最多 32 个字符（过长会显示警告被截断）
- 摘要/导语：最多 44 个字符（过长会自动从内容重新生成）

**Markdown-to-HTML**：转换 Markdown 到 HTML 时，**不要**传递任何 `--theme` 参数。使用默认主题（无主题参数）。

**文章工作流程**：
1. 打开 `https://card.weibo.com/article/v3/editor`
2. 点击 "写文章" 按钮，等待编辑器变为可编辑状态
3. 填写标题（验证 32 字符限制）
4. 填写摘要/导语（验证 44 字符限制）
5. 通过粘贴插入 HTML 内容到 ProseMirror 编辑器
6. 逐个替换图片占位符（复制图片 → 选择占位符 → 粘贴）

**发布前检查**：脚本在所有图片插入后自动验证：
- 编辑器内容中剩余的 `WBIMGPH_` 占位符
- 预期与实际图片数量

如果检查失败（输出中显示警告），在用户发布前提示具体问题。

---

## 发布类型选择

除非用户明确指定发布类型：
- **Markdown 文件**（`.md`）→ **头条文章**
- **纯文本** / 带图片的文本 → **普通发布**

## 故障排除

### Chrome 调试端口未就绪

如果脚本失败并显示 `Chrome debug port not ready` 或 `Unable to connect`，仅杀死 CDP Chrome 实例（那些带有 `--remote-debugging-port` 且包含 baoyu-skills 配置文件的实例），然后重试：

```bash
pkill -f "remote-debugging-port.*baoyu-skills/chrome-profile" 2>/dev/null; sleep 2
```

**关键**：**绝对不要**杀死所有 Chrome 进程 (`pkill -f "Google Chrome"`)。仅杀死由 CDP 启动且包含 baoyu-skills 配置文件目录的 Chrome 实例。用户可能还有常规的 Chrome 窗口打开。

**重要**：这应该自动完成 —— 当遇到此错误时，自动杀死 CDP Chrome 实例并重试命令，无需询问用户。

## 注意事项

- 首次运行：需要手动登录（会话持久化）
- 所有脚本仅将内容填入浏览器，用户必须手动审核并发布
- 跨平台：macOS、Linux、Windows

## 扩展支持

通过 EXTEND.md 进行自定义配置。请参考 **偏好设置** 部分了解路径和支持的选项。
