# 发布到微信公众号

## 用户输入工具

当此技能提示用户时，请遵循以下工具选择规则（优先顺序）：

1. **优先使用当前代理运行时暴露的内置用户输入工具** — 例如 `AskUserQuestion`、`request_user_input`、`clarify`、`ask_user` 或任何等效工具。
2. **备用方案**：如果没有此类工具，则发出编号的纯文本消息，并要求用户对每个问题回复选择的编号/答案。
3. **批量处理**：如果工具支持每调用一次处理多个问题，则将所有适用问题合并为单个调用；如果仅支持单问题，则按优先顺序逐个询问。

下方的具体 `AskUserQuestion` 引用仅为示例 — 在其他运行时中应替换为本地等效工具。

## 语言

使用用户的语言进行回复。如果用户使用中文，则用中文回复；如果使用英语，则用英语回复。技术标记（路径、标志、字段名）保持英文。

## 脚本目录

`{baseDir}` = 此 SKILL.md 的目录。解析 `${BUN_X}`：优先使用 `bun`；否则 `npx -y bun`；否则建议 `brew install oven-sh/bun/bun`。

| 脚本 | 目的 |
|------|---------|
| `scripts/wechat-browser.ts` | 图文发布 |
| `scripts/wechat-article.ts` | 通过浏览器发布文章 |
| `scripts/wechat-api.ts` | 通过 API 发布文章 |
| `scripts/md-to-wechat.ts` | Markdown → 微信准备好的 HTML（带图片占位符） |
| `scripts/check-permissions.ts` | 验证环境和权限 |

## 偏好设置（EXTEND.md）

按顺序检查这些路径；第一个匹配项生效：

| 路径 | 范围 |
|------|-------|
| `.baoyu-skills/baoyu-post-to-wechat/EXTEND.md` | 项目 |
| `${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-post-to-wechat/EXTEND.md` | XDG |
| `$HOME/.baoyu-skills/baoyu-post-to-wechat/EXTEND.md` | 用户主目录 |

找到 → 读取、解析、应用。未找到 → 在进行任何其他操作之前运行首次设置（`references/config/first-time-setup.md`）。

**最小键**（不区分大小写，接受 `1/0` 或 `true/false`）：

| 键 | 默认值 | 映射 |
|-----|---------|---------|
| `default_author` | 空值 | `author` CLI/前文未提供时的备用值 |
| `need_open_comment` | `1` | `draft/add` 中的 `articles[].need_open_comment` |
| `only_fans_can_comment` | `0` | `draft/add` 中的 `articles[].only_fans_can_comment` |

**推荐的 EXTEND.md**：

```md
default_theme: default
default_color: blue
default_publish_method: browser
default_author: 宝玉
need_open_comment: 1
only_fans_can_comment: 0
chrome_profile_path: /path/to/chrome/profile

# 远程 API 发布（可选）— 仅当微信公众号的 IP 白名单排除了您的本地机器时设置。
# 见下方的“远程 API 方法”。
# remote_publish_host: server.example.com
# remote_publish_user: deploy
# remote_publish_port: 22
# remote_publish_identity_file: ~/.ssh/id_ed25519
# remote_publish_known_hosts_file: ~/.ssh/known_hosts
# remote_publish_strict_host_key_checking: accept-new
# remote_publish_connect_timeout: 10
# remote_publish_proxy_jump: bastion.example.com
```

原始的 `ssh` / `scp` 选项有意不支持；仅支持上述键。认证仅通过 SSH 密钥（不允许密码）。

**主题选项**：default、grace、simple、modern。**颜色预设**：blue、green、vermilion、yellow、purple、sky、rose、olive、black、gray、pink、red、orange（或十六进制值）。

**值优先级**：CLI 参数 → 前文 → EXTEND.md（账户级 → 全局）→ 技能默认值。

## 多账户支持

EXTEND.md 支持用于管理多个公众号的 `accounts:` 块。具有 2 个或更多条目时，工作流程会插入步骤 0.5 以提示选择账户（或根据 `default: true` 或 `--account <alias>` 自动选择）。

完整细节 — 兼容性规则、每个账户的键、凭证解析、每个账户的 Chrome 配置文件、CLI 使用方法 — 在 `references/multi-account.md` 中。

## 预检查（可选）

首次使用前，建议执行环境检查（用户可以跳过）：

```bash
${BUN_X} {baseDir}/scripts/check-permissions.ts
```

检查项：Chrome、配置文件隔离、Bun、辅助功能、剪贴板、粘贴按键、API 凭证、Chrome 冲突。

| 检查失败 | 解决方法 |
|-------------|-----|
| Chrome | 安装 Chrome 或设置 `WECHAT_BROWSER_CHROME_PATH` |
| 配置文件目录 | 位于 `baoyu-skills/chrome-profile` 的共享配置文件 |
| Bun 运行时 | `brew install oven-sh/bun/bun` 或 `npm install -g bun` |
| 辅助功能（macOS） | 系统设置 → 隐私与安全 → 辅助功能 → 启用终端应用 |
| 剪贴板复制 | 确保 Swift/AppKit（macOS: `xcode-select --install`） |
| 粘贴按键（Linux） | 安装 `xdotool`（X11）或 `ydotool`（Wayland） |
| API 凭证 | 按照步骤 2 中的引导设置，或在 `.baoyu-skills/.env` 中设置 |

## 图文发布（图文）

带有多张图片（最多 9 张）的简短发布：

```bash
${BUN_X} {baseDir}/scripts/wechat-browser.ts --markdown article.md --images ./images/
${BUN_X} {baseDir}/scripts/wechat-browser.ts --title "标题" --content "内容" --image img.png --submit
```

详情：`references/image-text-posting.md`。

## 文章发布工作流程（文章）

```
- [ ] 步骤 0：加载偏好设置（EXTEND.md）
- [ ] 步骤 0.5：解析账户（仅多账户情况 — 见 references/multi-account.md）
- [ ] 步骤 1：确定输入类型
- [ ] 步骤 2：选择方法并配置凭证
- [ ] 步骤 3：解析主题/颜色并验证元数据
- [ ] 步骤 4：发布到微信公众号
- [ ] 步骤 5：报告完成
```

### 步骤 0：加载偏好设置

检查并加载 EXTEND.md（见上文的“偏好设置”）。如果未找到，则在提出任何其他问题之前完成首次设置。解析并缓存供后续步骤使用：`default_theme`、`default_color`、`default_author`、`need_open_comment`、`only_fans_can_comment`。

### 步骤 1：确定输入类型

| 输入 | 检测 | 下一步 |
|-------|-----------|------|
| HTML 文件 | 路径以 `.html` 结尾，文件存在 | 跳至步骤 3 |
| Markdown 文件 | 路径以 `.md` 结尾，文件存在 | 步骤 2 |
| 纯文本 | 不是文件路径，或文件不存在 | 保存为 Markdown，然后步骤 2 |

**纯文本处理**：

1. 生成 slug（前 2-4 个有意义的单词，kebab-case；将中文翻译为英文作为 slug）。
2. 保存到 `post-to-wechat/YYYY-MM-DD/<slug>.md`（如果需要，则创建目录）。
3. 继续作为 Markdown 文件处理。

### 步骤 2：选择发布方法和配置

除非 EXTEND.md 或 CLI 中指定了方法，否则询问方法：

| 方法 | 速度 | 需要项 |
|--------|-------|----------|
| `api`（推荐） | 快速 | API 凭证（本地 IP 白名单） |
| `browser` | 慢速 | Chrome + 登录会话 |
| `remote-api` | 快速 | API 凭证 + 一个可通过 SSH 访问的服务器，其 IP 在微信公众号白名单上 |

**选择 API + 缺少凭证** → 按照每个 `references/api-setup.md` 的引导设置（写入到 `.baoyu-skills/.env`）。

**`remote-api` 方法**：微信公众号的“公众号设置 → IP 白名单”通常将 API 访问限制为一个或两个固定的 IP。如果您的本地机器的 IP 不在白名单上，但云服务器的 IP 在，则使用 `remote-api`：所有 Markdown 渲染、图片处理、草稿组装和 HTML 重写仍在本地进行，而仅将出站 HTTPS 调用（token、uploadimg、add_material、draft/add）通过 SSH SOCKS5 动态端口转发（`ssh -N -D`）隧道传输，因此微信公众号看到的是远程服务器作为源 IP。不会将文件写入远程主机；`AppSecret` 从未离开本地进程。只需要远程主机的 `sshd` 和出站网络 — 不需要 Python，不需要代理进程。见下方的“远程 API 方法”。

### 步骤 3：解析主题/颜色并验证元数据

1. **主题**：CLI `--theme` → EXTEND.md `default_theme` → `default`（第一个匹配项生效；如果已解析，则不询问）。
2. **颜色**：CLI `--color` → EXTEND.md `default_color` → 跳过（主题默认值适用）。
3. **验证元数据**（Markdown 的前文，HTML 的元标签）：

| 字段 | 缺失时 → |
|-------|-----------|
| 标题 | 询问，或按 Enter 自动生成自内容 |
| 摘要 | 前文 `description` → `summary` → 询问或自动生成 |
| 作者 | CLI `--author` → 前文 `author` → EXTEND.md `default_author` |
| 来源 URL | CLI `--source-url` → 前文 `sourceUrl`/`contentSourceUrl`/`content_source_url` |

自动生成：标题 = 第一个 H1/H2 或第一句话；摘要 = 第一段，截断到 120 个字符。

4. **封面图片**（API `article_type=news` 所需）：CLI `--cover` → 前文（`coverImage` / `featureImage` / `cover` / `image`）→ `imgs/cover.png` → 第一个内联图片 → 如果仍然缺失，则请求一个。

### 步骤 4：发布

**重要 — 不要预先将 Markdown 转换为 HTML。** 发布脚本将内部处理转换，并且两种方法渲染图片的方式不同：API 为上传渲染 `<img>` 标签，浏览器使用占位符进行粘贴替换。传递预转换的 HTML 会破坏其中一种方法。

**Markdown 引用默认值**：对于 Markdown 输入，普通外部链接默认转换为底部引用。仅当用户明确希望保留内联链接时，才使用 `--no-cite`。现有 HTML 输入保持原样。

**API 方法**（接受 `.md` 或 `.html`）：

```bash
${BUN_X} {baseDir}/scripts/wechat-api.ts <文件> --theme <主题> [--color <颜色>] [--title <标题>] [--summary <摘要>] [--author <作者>] [--cover <封面路径>] [--source-url <URL>] [--no-cite]
```

即使它是 `default` 也必须传递 `--theme`。仅当用户明确设置或 EXTEND.md 设置时才传递 `--color`。

**远程 API 方法**（相同脚本，增加 `--remote`）：

```bash
${BUN_X} {baseDir}/scripts/wechat-api.ts <文件> --theme <主题> --remote [--remote-host <主机>] [--remote-user <用户>] [--remote-port <端口>] [--remote-identity-file <路径>] [--remote-known-hosts-file <路径>] [--remote-strict-host-key-checking yes|no|accept-new] [--remote-connect-timeout <秒>] [--remote-proxy-jump <规范>]
```

任何 `--remote-*` 标志都表示 `--remote`。CLI 值优先于账户级然后是全局 `remote_publish_*` 键来自 EXTEND.md。设置 `default_publish_method: remote-api` 也可以启用远程模式，而无需 `--remote`。

**`draft/add` 负载规则**：
- 端点：`POST https://api.weixin.qq.com/cgi-bin/draft/add?access_token=ACCESS_TOKEN`
- `article_type`：`news`（默认）或 `newspic`
- 对于 `news`，包括 `thumb_media_id`（需要封面）
- 始终包括 `need_open_comment`（默认 `1`）和 `only_fans_can_comment`（默认 `0`）在请求正文中，即使 CLI 没有暴露它们
- 对于 `news`，可选地包括 `content_source_url`（原始文章 URL，显示为“阅读原文”链接，最大 1KB）。通过 `--source-url` CLI 标志或前文 `sourceUrl`/`contentSourceUrl`/`content_source_url` 提供

**浏览器方法**（接受 `--markdown` 或 `--html`）：

```bash
${BUN_X} {baseDir}/scripts/wechat-article.ts --markdown <markdown_file> --theme <主题> [--color <颜色>] [--no-cite]
${BUN_X} {baseDir}/scripts/wechat-article.ts --html <html_file>
```

### 步骤 5：完成报告

```
微信公众号发布完成！

输入：[类型] - [路径]
方法：[API | 浏览器]
主题：[主题] [如果设置了颜色]
文章：
• 标题：[标题]
• 摘要：[摘要]
• 图片：[N] 内联
• 评论：[开放/关闭]，[粉丝限定/全部]    ← 仅 API 方法

结果：
✓ 草稿保存到微信公众号
• media_id：[media_id]                         ← 仅 API 方法

下一步（API）：
→ 管理草稿：https://mp.weixin.qq.com (登录后进入「内容管理」→「草稿箱」)

创建的文件：
[• post-to-wechat/YYYY-MM-DD/slug.md (如果纯文本输入)]
[• slug.html (转换后)]
```

## 功能比较

| 功能 | 图文 | 文章（API） | 文章（远程 API） | 文章（浏览器） |
|---------|:---:|:---:|:---:|:---:|
| 纯文本输入 | ✗ | ✓ | ✓ | ✓ |
| HTML 输入 | ✗ | ✓ | ✓ | ✓ |
| Markdown 输入 | 标题/内容 | ✓ | ✓ | ✓ |
| 多张图片 | ✓ (最多 9 张) | ✓ (内联) | ✓ (内联) | ✓ (内联) |
| 主题 | ✗ | ✓ | ✓ | ✓ |
| 自动生成元数据 | ✗ | ✓ | ✓ | ✓ |
| 默认封面备用 (`imgs/cover.png`) | ✗ | ✓ | ✓ | ✗ |
| 评论控制 | ✗ | ✓ | ✓ | ✗ |
| 需要 Chrome | ✓ | ✗ | ✗ | ✓ |
| 需要 API 凭证 | ✗ | ✓ | ✓ | ✗ |
| 需要 SSH 可达的带白名单 IP 服务器 | ✗ | ✗ | ✓ | ✗ |
| 速度 | 中等 | 快速 | 快速 | 慢速 |

## 故障排除

| 问题 | 解决方法 |
|-------|-----|
| 缺少 API 凭证 | 按照步骤 2 中的引导设置 |
| 访问 token 错误 | 验证凭证有效且未过期 |
| 浏览器未登录 | 首次运行时打开浏览器 — 扫描二维码登录。设置 `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` 以通过 Telegram 接收二维码图像 |
| Chrome 未找到 | 设置 `WECHAT_BROWSER_CHROME_PATH` |
| 标题/摘要缺失 | 使用自动生成或手动提供 |
| 没有封面图片 | 添加前文封面或将 `imgs/cover.png` 放在文章目录中 |
| 评论默认值错误 | 检查 EXTEND.md 中的 `need_open_comment` / `only_fans_can_comment` |
| 粘贴失败 | 检查系统剪贴板权限 |
| `Remote publish host is required` | 设置 `--remote-host` 或 EXTEND.md 中的 `remote_publish_host` |
| `SOCKS proxy on 127.0.0.1:… not ready` | SSH 无法启动隧道 — 检查密钥、主机、`StrictHostKeyChecking` 或使用 `--remote-connect-timeout` |
| `ssh exited early` 在远程发布期间 | 验证用户可以非交互式地 `ssh` 到服务器；如果连接慢，则提高 `--remote-connect-timeout` |
| 远程 API 调用返回 `errcode 40164`（无效 IP） | 远程服务器的出站 IP 不在微信公众号的白名单上；在“公众号设置 → IP 白名单”中添加它 |

## 参考

| 文件 | 内容 |
|------|---------|
| `references/image-text-posting.md` | 图文参数，自动压缩 |
| `references/article-posting.md` | 文章主题，图片处理 |
| `references/multi-account.md` | 多账户兼容性，凭证，Chrome 配置文件，CLI |
| `references/api-setup.md` | 引导凭证设置 |
| `references/config/first-time-setup.md` | 首次 EXTEND.md 设置 |

## 扩展支持

通过 EXTEND.md 进行自定义配置。见“偏好设置”中的路径和受支持选项。
