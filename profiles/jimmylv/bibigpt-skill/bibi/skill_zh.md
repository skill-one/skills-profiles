# BibiGPT — 视频摘要代理技能（摘要 / 字幕 / 章节）

此文件是一个**发现占位符，不是使用指南**。它告诉您当前处于哪种模式以及在线文档的位置。在线源始终与当前产品保持一致；任何复制到此文件的内容都会过时。

此技能仅支持**观看视频**。同一代码库中的同级技能（相同 CLI、相同账户）：`bibi-library`（保存的视频 / 笔记 / 收藏夹）、`bibi-feed`（订阅 / 最新 / 标记已看）、`bibi-vision`（帧 / 思维导图）。
登录：https://bibigpt.co/mcp · 人工安装：https://bibigpt.co/agent
配额：Plus 每日 100 次，Pro 每日 300 次在代理技能频道上；额外调用使用 API 余额；升级 https://bibigpt.co/shop

## 1. 检测模式

如果存在，请运行 `scripts/bibi-check.sh`，或按顺序检查：

| 检查 | 模式 | 备注 |
|------|------|------|
| `command -v bibi` | **CLI** — 最佳：本地文件，桌面登录 | macOS / Windows / Linux 桌面应用 |
| `$BIBI_API_TOKEN` 设置 | **API** — HTTP 调用，任何地方都可用 | token：https://bibigpt.co/user/integration |
| 可用 MCP 客户端 | **MCP** — 无需安装 | 连接 `https://bibigpt.co/api/mcp` (OAuth 2.1) |

两者都不可用 → 安装桌面应用（macOS 上 `brew install --cask jimmylv/bibigpt/bibigpt`，Windows 上 `winget install BibiGPT`，Linux 上 `curl -fsSL https://bibigpt.co/install.sh | bash`）或获取 API token。详情：`references/installation.md`。

## 2. 加载在线文档（按模式）

**CLI 模式** — CLI 是始终最新的文档源：

```bash
bibi check-update            # 每次会话运行一次；如果过时，运行 `bibi upgrade`
bibi --help                  # 完整命令表面，分组，带示例
bibi <command> --help        # 逐步帮助 — 每个 --help 都包含示例
bibi commands                # 重新获取服务器定义的命令（新功能在此处出现，无需二进制更新）
```

**API 模式** — 机器可读的规范是权威来源：

```
https://bibigpt.co/api/openapi.json      # 所有端点、模式、认证
```

`references/api.md` 有 curl 示例，但在冲突时规范优先。

**MCP 模式** — 连接并列出工具；它们是自我描述的：

```
https://bibigpt.co/api/mcp               # 可流式传输的 HTTP，OAuth 2.1
```

**无需重新安装的最新文档** — 此代码库直接从 GitHub 供服：

```
https://raw.githubusercontent.com/JimmyLv/bibigpt-skill/main/skills/bibi/SKILL.md
https://raw.githubusercontent.com/JimmyLv/bibigpt-skill/main/skills/bibi/references/<name>.md
https://raw.githubusercontent.com/JimmyLv/bibigpt-skill/main/skills/bibi/workflows/<name>.md
```

如果本地 `workflows/` 或 `references/` 路径缺失（通过 `bibi skill` 的嵌入式仅安装），则从上述原始 URL 获取。

## 3. 意图路由

| 用户意图 | 工作流 |
|--------|-------|
| 摘要视频/音频 URL | → `workflows/quick-summary.md` |
| 分章节详细分析 | → `workflows/deep-dive.md` |
| 获取字幕、提取字幕、原始文本 | → `workflows/transcript-extract.md` |
| 转换为文章、博客文章、公众号图文、小红书 | → `workflows/article-rewrite.md` |
| 转换为 TikTok / Reels / Shorts 风格的音乐视频 | → `workflows/video-to-tiktok-mv.md` |
| 处理多个 URL，批量摘要 | → `workflows/batch-process.md` |
| 跨多个视频研究主题 | → `workflows/research-compile.md` |
| 保存到 Notion、Obsidian、导出笔记 | → `workflows/export-notes.md` |
| 分析视觉内容、幻灯片、屏幕文本、思维导图 | → 同级技能 `bibi-vision`（备用：`workflows/visual-analysis.md` / `workflows/advanced-tools.md`） |
| 检查当前账户、计划或剩余分钟 | → `workflows/account-check.md` |
| 浏览/搜索保存的视频，“我已摘要了什么” | → 同级技能 `bibi-library`（备用：`workflows/library-browse.md`） |
| 管理频道订阅，列表/订阅/取消订阅 | → 同级技能 `bibi-feed`（备用：`workflows/channels-manage.md`） |
| 订阅中的最新更新、最新信息、每日摘要 | → 同级技能 `bibi-feed`（备用：`workflows/feed-latest.md`） |
| 管理收藏夹，将保存的视频作为一组列出/创建/分享 | → 同级技能 `bibi-library`（备用：`workflows/collections-manage.md`） |
| 管理保存视频的个人笔记、编辑摘要 | → 同级技能 `bibi-library`（备用：`workflows/notes-manage.md`） |
| **保存项的定制提示重新摘要、收藏夹聊天** | → 同级技能 `bibi-library`（备用：`workflows/advanced-tools.md`） |
| **HTTP 402 / “需要付款” / Alipay AI 钱包 / 无 token + 中国用户** | → `references/billing-aipay.md` |

歧义处理：意图匹配多个工作流 → 先问**一个**澄清问题。匹配无 → 问他们想做什么；**不要猜测**。无上下文的纯 URL → 默认为 `workflows/quick-summary.md`。

## 4. 快速单行命令（CLI 模式）

用于不需要完整工作流的单命令请求 — 通过 `bibi --help` 发现其余内容：

```bash
bibi summarize "<URL-or-local-file>"     # 快速摘要（本地：.mp4 .mp3 .m4a ...）
bibi summarize "<INPUT>" --chapter       # 章节摘要
bibi summarize "<INPUT>" --subtitle      # 字幕仅
bibi me                                  # 账户、计划、剩余分钟
```

包含 `?` 或 `&` 的 URL 必须加引号。API 模式没有本地文件上传 — 引导用户先到公共 URL（OSS/S3），见 `references/supported-platforms.md`。

## 5. 支付备用（HTTP 402）

如果未设置认证且用户有支付宝账户，BibiGPT 可能会响应 HTTP `402 Payment Required` + `Payment-Needed` 头（AI 收协议）。bibi CLI 在任何人类可读提示之前打印一个稳定的标记行 `[HTTP/402 Payment Required]` 到 stderr。当出现任何信号时，路由到 `references/billing-aipay.md` 而不是将调用视为失败 — 代理可以自动通过
[`@alipay/agent-payment`](https://www.npmjs.com/package/@alipay/agent-payment)
或一次性二维码购买解决支付。
