# opencli-使用

OpenCLI 将任何网站、Electron 桌面应用或外部 CLI 转换为一个统一的 `opencli <site> <command>` 界面，使代理无需屏幕抓取即可驱动。这项技能是导向层——一旦你知道你想做什么，加载下面的一种专业技能即可。

## 三个支柱

- **适配器命令** — `opencli <site> <command> [...]`。内置适配器位于 `clis/`，用户适配器位于 `~/.opencli/clis/`。每个适配器都由一个策略（`PUBLIC | COOKIE | INTERCEPT | UI | LOCAL`）支持，该策略会告诉你是否需要 Chrome 会话。
- **浏览器驱动** — `opencli browser *` 子命令（`open`, `state`, `click`, `type`, `select`, `find`, `extract`, `network`, …）用于临时交互和抓取，当没有适配器覆盖任务时。参见 `opencli-browser`。
- **当前标签页绑定** — `opencli browser <session> bind` 将用户已经打开/登录的 Chrome 标签页附加到该浏览器会话。后续命令使用 `opencli browser <session> ...`。在使用它之前，请先查看 `opencli-browser`；绑定的会话仍然会阻塞标签页修改。
- **外部 CLI 透传** — `opencli gh`, `opencli docker`, `opencli vercel`, 等。通过 `opencli external install <name>`（从 `external-clis.yaml` 自动安装）或 `opencli external register <name>`（使用自己的）进行管理。

## 安装

```bash
# npm 全局安装
npm install -g @jackwener/opencli          # 二进制文件：opencli，需要 Node >= 21
opencli doctor                              # 在进行依赖浏览器的操作之前运行（见下文）

# 从源代码安装
git clone git@github.com:jackwener/OpenCLI.git
cd OpenCLI && npm install
npx tsx src/main.ts <command>               # 相同的界面，无需全局安装
```

`opencli doctor` 打印结构化的 `DoctorReport`——守护进程状态、扩展连接、版本检查和实时浏览器连接探测。范围较窄：它诊断**浏览器桥接**（守护进程 + 扩展 + Chrome 线路）。`PUBLIC` / `LOCAL` 适配器、`opencli list`、`validate`、`verify`、插件命令和外部 CLI 透传不需要它是绿色的——只有 `COOKIE` / `INTERCEPT` / `UI` 适配器和 `opencli browser *` 子命令需要。标志：`-v`（详细）。

## 按命令类型划分的先决条件

| `opencli list` 上的策略标签 | 它需要什么 |
|--------------------------------|---------------|
| `PUBLIC` | 什么也不需要——纯 HTTP，不需要浏览器。 |
| `COOKIE` | 已登录目标网站的 Chrome + 从 [Chrome Web Store](https://chromewebstore.google.com/detail/opencli/ildkmabpimmkaediidaifkhjpohdnifk) 安装的 **OpenCLI** 扩展。命令从你的实时会话中捕获凭证——无需重新登录。 |
| `INTERCEPT` | 与 COOKIE 相同，加上 opencli 打开自动化窗口以捕获一个已签署的请求。 |
| `UI` | 与 COOKIE 相同，完整的 DOM 交互。 |
| `LOCAL` | 不需要浏览器；与本地/开发端点通信。 |

Electron 桌面应用（cursor、codex、chatwise、discord-app、doubao-app、antigravity、chatgpt-app）通过 CDP 对运行的应用进行路由——与登录的浏览器相同的无 Cookie 流程。在调用之前确保应用正在运行。

## 发现已安装的内容——不要阅读此文件，运行一个命令

```bash
opencli list                    # 表格，按网站分组
opencli list -f json            # 机器可读；管道到 jq 或你的代理
opencli list | grep -i twitter  # 查找特定网站的命令
opencli <site> --help           # 查看该网站的命令 + 标志
opencli <site> <command> --help # 查看位置参数和特定命令的标志
```

不要硬编码适配器列表——有 100 多个网站，数量每周都在变化。`opencli list -f json` 是真相来源；它为每个命令发出一个条目，包含 `{site, name, aliases, description, strategy, browser, args, columns, ...}`。对于代理来说，这总是比在文档中grep更好。

在高变化的认证网站上，在回退到原始 `opencli browser` 命令之前，检查是否已经有网站适配器公开了工作流程。例如，ChatGPT 网页有用于对话读取和 Deep Research 结果提取的高级命令；使用 `opencli chatgpt --help` 或 `opencli list -f json` 发现当前界面。

## 通用标志（适用于每个适配器命令）

| 标志 | 效果 |
|------|--------|
| `-f, --format <fmt>` | `table`（TTY 中的默认值）· `yaml`（非 TTY 中的默认值）· `json`· `plain`· `md`· `csv`。当你想要特定的形状时显式传递；代理几乎总是想要 `-f json`。 |
| `-v, --verbose` | 调试日志 + 失败时的堆栈跟踪；还设置了 `OPENCLI_VERBOSE=1` 为进程。 |

特定命令的标志（`--limit`, `--tab`, `--filter`, …）不是通用的——请参阅 `<site> <command> --help`。

## 输出格式

- `json` — 美化打印，2 空格缩进。代理的默认选择。
- `plain` — 为聊天式命令打印单个主要字段（`response`/`content`/`text`/`value`）。适用于管道到另一个工具。
- `yaml` — 输出不是 TTY 且 `-f` 没有显式指定时的回退。
- `table` — 带颜色编码，按网站分组；供人类使用。
- `md`, `csv` — 直观的表格输出。

一些命令通过 `cmd.defaultFormat` 覆盖默认值（例如，聊天命令默认为 `plain`），所以不要假设，除非阅读 `--help`。

## 环境变量

| 变量 | 默认值 | 目的 |
|----------|---------|---------|
| `OPENCLI_BROWSER_CONNECT_TIMEOUT` | `45` | 等待浏览器桥接的秒数。 |
| `OPENCLI_BROWSER_COMMAND_TIMEOUT` | `60` | 每个命令的超时时间。 |
| `OPENCLI_CDP_ENDPOINT` | — | 手动 CDP 端点覆盖（开发 / 远程 Chrome / Electron）。 |
| `OPENCLI_CACHE_DIR` | `~/.opencli/cache` | 网络捕获 + 浏览器状态缓存。 |
| `OPENCLI_WINDOW` | 命令特定 | `foreground` 或 `background` 浏览器窗口模式。 |
| `OPENCLI_VERBOSE` | `false` | 详细日志记录（也由 `-v` 触发）。 |

## 自我修复

当适配器命令因为网站变化（选择器漂移、API 旋转、响应模式变化）而失败时，使用 `--trace retain-on-failure` 重新运行。错误包包括一个指向 `summary.md` 的 `trace` 块；从该摘要中修补 `adapterSourcePath` 并重试。最多 3 次修复轮次。完整流程在 `opencli-autofix` 中。

## 编写自己的适配器

两路径存储：

- **私有**：`~/.opencli/clis/<site>/<command>.js`——没有构建步骤，热可用，不在公共包中可见。
- **公共 / PR**：`clis/<site>/<command>.js`——用于上游贡献；需要构建。

脚手架和验证：

```bash
opencli browser init <site>/<command>   # 生成骨架
opencli validate [target]               # 对加载的注册表进行语义检查（描述、域、管道步骤名称、func|pipeline|_lazy 存在、参数重复）——无网络，无浏览器
opencli verify [target] [--smoke]       # 使用合成参数运行命令
opencli browser verify <site>/<command> # 桥接器内的端到端冒烟测试
```

适配器只导入 `@jackwener/opencli/registry` 和 `@jackwener/opencli/errors`。`columns` 必须与 `func` 返回的对象的键 1:1 对齐（在名称和顺序上）。有关完整工作流程，请参阅 `opencli-adapter-author`。

## 插件

插件是从 git 拉取的第三方扩展，与主适配器注册表分开：

```bash
opencli plugin install github:user/repo    # 安装
opencli plugin list [-f json]              # 查看已安装的
opencli plugin update [name] | --all       # 保持当前
opencli plugin uninstall <name>
opencli plugin create <name>               # 搭建一个新的插件
```

## 外部 CLI 透传

包装外部命令行工具，以便你可以通过相同的 `opencli …` 入口点发现 + 调用它们：

```bash
opencli external install gh    # 通过 brew/apt/npm 根据 external-clis.yaml 自动安装
opencli external register my-tool \
    --binary my-tool \
    --install "npm i -g my-tool" \
    --desc "我的内部 CLI"
opencli external list
opencli gh pr list --limit 5   # 透传；stdio 被继承，退出代码被传播
opencli docker ps
```

内置条目位于 `src/external-clis.yaml`；用户覆盖和添加位于 `~/.opencli/external-clis.yaml`。通常提供：`gh`, `docker`, `vercel`, `lark-cli`, `longbridge`, `dws`, `wecom-cli`, `obsidian`, `ntn`, `tg(tg-cli)`, `discord(discord-cli)`, `wx(wx-cli)`。

一些官方 CLI 使用 shell 脚本安装程序而不是无 shell 的包管理器命令。没有 `install` 配置的条目，例如 `ntn`，必须在透传使用之前从其主页手动安装。

## Shell 补全

```bash
opencli completion bash   # 也：zsh, fish
# -> 标准输出上的脚本；根据你的 shell 的约定进行 source 或保存
```

## 下一步去哪里

| 如果你即将… | 加载这个技能 |
|---------------------|-----------------|
| 临时驱动实时浏览器（没有适配器可用，或原型设计） | `opencli-browser` |
| 编写新的适配器，或向现有网站添加命令 | `opencli-adapter-author` |
| 在命令失败后修复损坏的适配器 | `opencli-autofix` |
| 将搜索 / 查找 / 研究请求路由到正确的适配器 | `smart-search` |

## 曾经存在的命令

以下是在 PR #1094 合并中移除的——不要尝试调用它们：

- `opencli explore <url>` — 被 `opencli browser network` + `opencli browser find` 用于实时 API 发现，以及 `opencli-adapter-author` 工作流用于捕获取代。
- `opencli record <url>` — 移除；手动捕获现在位于 `opencli browser network --detail`。
- `opencli web read` / `opencli desktop *` 作为顶级组——合并到各自的适配器（`opencli web read` 仍然是 `web` 适配器的 `read` 命令，但没有独立的 `web` / `desktop` 顶级组命令）。

## 不要

- 不要将此技能的命令列表粘贴到你的计划中；它会腐烂。在任务开始时调用 `opencli list -f json` 代替。
- 不要假设每个适配器都需要浏览器——策略 `PUBLIC` 和 `LOCAL` 不需要。检查 `strategy` 字段。
- 不要在适配器失败时无声地回退到手工制作的 `fetch`——`--trace retain-on-failure` 给你浏览器证据和适配器源路径。首先做那件事。
