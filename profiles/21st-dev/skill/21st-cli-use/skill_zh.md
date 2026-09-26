# 21st CLI — 从终端查找、安装和生成

`21st` CLI (`npx @21st-dev/cli`, 二进制文件 `21st`) 是 21st.dev 目录的命令行界面。先搜索，安装适合的，只有在没有匹配项时才手动编写 UI。要**发布**你自己的组件/主题/模板，使用 `21st-registry` 功能；要发布一个项目的设计作为主题，使用 `21st-design-sync`。

## 认证 (只需执行一次)

两种可互换的凭证，都作为 API 密钥发送：

1. **登录会话** — `npx @21st-dev/cli login` 会打开浏览器并将一个令牌保存到 `~/.config/21st/auth.json`。最适合交互式/开发机器。
2. **API 密钥** — 来自 **https://21st.dev/mcp** (或 **https://21st.dev/settings/api-keys**) 的 `21st_sk_…`。通过 `--api-key <key>` 或环境变量 `TWENTYFIRST_TOKEN` / `API_KEY_21ST` 传递。最适合 CI。

`21st whoami` 显示已登录的账户；`21st usage` 显示检索层级/配额和 `21st AI 生成` 状态，而不是 AI 信用额度。要获取结构化状态，请使用 MCP `get_usage.aiGenerationEnabled` 或 CLI 1.17.1+ `21st usage --json`。缺失或未知状态不会授予 AI 访问权限。`21st logout` 会清除保存的登录信息。

## 计量

元数据 (搜索、预览、主题的 CSS) 是**免费**的。检索组件**代码** (`21st get`，安装) 有免费每日配额；Builder 包含无限检索。托管 21st AI 需要单独的 AI 访问权限并消耗 AI 信用额度。基础 Builder 已关闭 AI。在选择生成之前检查 `21st usage`：当 AI 没有明确启用时，搜索和检索代码，然后用你自己的编码代理进行适配。不要在收到 `ai_subscription_required` 拒绝生成的情况下重试，直到 AI 访问权限启用。

---

## 查找

```bash
# 搜索所有内容 (组件 + 主题 + 模板)
21st search "定价表" --limit 10
21st search 按钮 --type c        # 仅组件 (c | theme | template)
21st search 暗色 --type theme
# 过滤器: --tag <slug> --color <bucket> --sort <s> --free|--paid
#          --author <username> --mine --liked   --json 用于机器输出
```

**在手动编写组件之前始终搜索** — 一个接近的匹配项通常比从头开始构建更快安装和适配。

## Logo

```bash
21st logo discord            # 搜索品牌 + UI SVG Logo (免费，无需登录)
21st logo "next js" --limit 5 --json
```

将每个 Logo 的名称和 SVG URL 打印出来，可以直接 curl 到项目中。使用 open svgl.app 库；在所有计划中都免费且不计量。

## 拉取代码

```bash
# 打印组件的代码 + 示例 (通过搜索的 ID)
21st get 143 [--json]

# 打印主题的 CSS (通过 `search --type theme` 的主题 ID)
21st theme <id> [--json]
```

## 安装

```bash
# 将组件安装到当前项目 (shadcn 底层实现)
21st add <user>/<slug>            # 例如 21st add shadcn/button
21st add @<team>/<slug>           # 从团队库
# --print 以输出 shadcn 命令而不是执行它
```

`21st add` 解析注册项，将其写入 `components/ui/<slug>.tsx`，并使用项目的包管理器安装 npm 依赖。公共/未列出项也适用于 stock shadcn：
`npx shadcn@latest add "https://21st.dev/r/<user>/<slug>"`。

## 生成

当目录中没有适合的项且 `21st usage` 明确报告 AI 生成已启用时，使用托管 21st AI 绘制草图，并从终端进行迭代。这个循环 (`21st generate` → `generation` → `iterate` → `take`) 存在于 **`21st-ai`** 功能中。在关闭 AI 的情况下，本地适配目录代码：

```bash
21st generate "一个带有月度/年度切换的玻璃状定价部分"
```

打开预览；从此处你可以编辑任何变体并拉取其代码。有关完整的生成/迭代/抓取代码流程和计量的详细信息，请参阅 `21st-ai` 功能。

---

## 收藏夹、团队 & MCP 配置

```bash
21st bookmarks [--type component|theme|template]
21st bookmark <id> --type <kind> [--remove]     # 心形图标 / 取消心形图标
21st lists                          # 你的收藏夹列表
21st list <listId>

21st teams                          # 你的团队
21st team <teamId>                  # 一个团队的库
21st team-components <teamId> [--library <id>]

21st init --client cursor|claude|codex|vscode|devin [--write]      # 写入 MCP 配置
21st install-skill                  # 全局安装 21st 功能
```
