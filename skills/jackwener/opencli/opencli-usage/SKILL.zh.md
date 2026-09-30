---
name: opencli-usage
description: 在任何 OpenCLI 会话开始时使用——这是 `opencli` 能做什么的顶层地图，如何发现适配器，哪些标志和输出格式是通用的，以及下一步要加载哪些专业技能。当代理询问“`opencli`能做什么？”或“我该如何找到正确的命令？”时，请指向这里。
---

# opencli-使用

OpenCLI 将网站和 Electron 桌面应用转换为统一的 `opencli <site> <command>` 界面，代理可以在无需屏幕抓取的情况下驱动。这项技能是导向层——一旦你知道你想做什么，就加载下面的一种专用技能。

## 主要功能

- **适配器命令** — `opencli <site> <command> [...]`。内置适配器位于 `clis/`，用户适配器位于 `~/.opencli/clis/`。每个适配器都由一个策略（`PUBLIC | COOKIE | INTERCEPT | UI | LOCAL`）支持，该策略会告诉你是否需要 Chrome 会话。
- **浏览器驱动** — `opencli browser *` 子命令（`open`, `state`, `click`, `type`, `select`, `find`, `extract`, `network`, …）用于在没有任何适配器覆盖任务时进行临时交互和抓取。参见 `opencli-browser`。
- **当前标签页绑定** — `opencli browser <session> bind` 将用户已经打开/登录的 Chrome 标签页附加到该浏览器会话。后续命令使用 `opencli browser <session> ...`。在使用它之前请先查看 `opencli-browser`；绑定的会话仍然会阻止标签页的更改。

## 安装

```bash
# npm 全局安装
npm install -g @jackwener/opencli          # 二进制文件：opencli，需要 Node >= 20.18.1
opencli doctor                              # 在进行浏览器依赖性工作之前运行（见下文）

# 从源代码安装
git clone git@github.com:jackwener/OpenCLI.git
cd OpenCLI && npm install
npx tsx src/main.ts <command>               # 相同的界面，无需全局安装
```

`opencli doctor` 打印结构化的 `DoctorReport`——守护进程状态、扩展连接、版本检查和实时浏览器连接探测。范围较窄：它诊断**浏览器桥接**（守护进程 + 扩展 + Chrome 连接）。`PUBLIC` / `LOCAL` 适配器、`opencli list`、`validate`、`verify` 和插件命令不需要它是绿色的——只有 `COOKIE` / `INTERCEPT` / `UI` 适配器和 `opencli browser *` 子命令需要。标志：`-v`（详细）。

## 不同命令类型的先决条件

| `opencli list` 上的策略标签 | 它需要什么 |
|--------------------------|-----------|
| `PUBLIC` | 什么也不需要——纯 HTTP，不需要浏览器。 |
| `COOKIE` | 已登录目标网站的 Chrome + 从 [Chrome 网上应用店](https://chromewebstore.google.com/detail/opencli/ildkmabpimmkaediidaifkhjpohdnifk) 安装的 **OpenCLI** 扩展。命令从你的实时会话中捕获凭证——无需重新登录。 |
| `INTERCEPT` | 与 COOKIE 相同， plus opencli 打开一个自动化窗口来捕获一个已签名请求。 |
| `UI` | 与 COOKIE 相同，完整的 DOM 交互。 |
| `LOCAL` | 无需浏览器；与本地/开发端点通信。 |

Electron 桌面应用（cursor、codex、chatwise、discord-app、doubao-app、antigravity、chatgpt-app）通过 CDP 对运行的应用进行路由——与登录的浏览器相同的无 Cookie 流程。在调用之前确保应用正在运行。

## 查找已安装的内容——不要阅读此文件，运行一个命令

```bash
opencli list                    # 表格，按网站分组
opencli list -f json            # 机器可读；管道到 jq 或你的代理
opencli list | grep -i twitter  # 查找特定网站的命令
opencli <site> --help           # 查看该网站的命令 + 标志
opencli <site> <command> --help # 查看位置参数和特定命令的标志
```

不要将适配器列表硬编码——有 100 多个网站，数量每周都在变化。`opencli list -f json` 是真相来源；它为每个命令发出一个条目，包含 `{site, name, aliases, description, strategy, browser, args, columns, ...}`。对于代理来说，这总是比在文档中grep更好。

在具有高变化性的认证网站上回退到原始 `opencli browser` 命令之前，检查是否已经有网站适配器公开了工作流程。例如，ChatGPT 网页有用于对话读取和 Deep Research 结果提取的高级命令；使用 `opencli chatgpt --help` 或 `opencli list -f json` 查找当前界面。

## 通用标志（适用于每个适配器命令）

| 标志 | 效果 |
|------|------|
| `-f, --format <fmt>` | `table`（TTY 中的默认值）· `yaml`（非 TTY 中的默认值）· `json`· `plain`· `md`· `csv`。当你想要特定的形状时显式传递；代理几乎总是想要 `-f json`。 |
| `-v, --verbose` | 失败时的调试日志 + 堆栈跟踪；还设置了 `OPENCLI_VERBOSE=1` 为进程。 |

特定命令的标志（`--limit`, `--tab`, `--filter`, …）不是通用的——请参阅 `<site> <command> --help`。

## 输出格式

- `json` — 美化打印，2 空格缩进。代理的默认选择。
- `plain` — 为聊天式命令打印单个主要字段（`response`/`content`/`text`/`value`）。适用于管道到另一个工具。
- `yaml` — 输出不是 TTY 且 `-f` 没有显式指定时的回退。
- `table` — 带颜色编码，按网站分组；供人类使用。
- `md`, `csv` — 直观的表格输出。

一些命令通过 `cmd.defaultFormat` 覆盖默认值（例如，聊天命令默认为 `plain`），所以不要假设而不阅读 `--help`。

## 环境变量

| 变量 | 默认值 | 目的 |
|------|--------|------|
| `OPENCLI_BROWSER_CONNECT_TIMEOUT` | `45` | 等待浏览器桥接的秒数。 |
| `OPENCLI_BROWSER_COMMAND_TIMEOUT` | `60` | 每个命令的超时时间。 |
| `OPENCLI_CDP_ENDPOINT` | — | 手动 CDP 端点覆盖（开发 / 远程 Chrome / Electron）。 |
| `OPENCLI_CACHE_DIR` | `~/.opencli/cache` | 网络捕获 + 浏览器状态缓存。 |
| `OPENCLI_WINDOW` | 命令特定 | `foreground` 或 `background` 浏览器窗口模式。 |
| `OPENCLI_VERBOSE` | `false` | 详细日志记录（也由 `-v` 触发）。 |

## 自我修复

当适配器命令因为网站更改（选择器漂移、API 旋转、响应模式更改）而失败时，使用 `--trace retain-on-failure` 重新运行。错误包包括一个指向 `summary.md` 的 `trace` 块；仅修复该摘要中的 `adapterSourcePath` 并重试。最多 3 次修复轮次。完整流程在 `opencli-autofix` 中。

## 编写自己的适配器

双路径存储：

- **私有**：`~/.opencli/clis/<site>/<command>.js`——没有构建步骤，热可用，不在公共包中可见。
- **公共 / PR**：`clis/<site>/<command>.js`——用于上游贡献；需要构建。

脚手架和验证：

```bash
opencli browser init <site>/<command>   # 生成骨架
opencli validate [target]               # 加载的注册表语义检查（描述、域、管道步骤名称、func|pipeline|_lazy 存在、参数重复）——无网络，无浏览器
opencli verify [target] [--smoke]       # 使用合成参数运行命令
opencli browser verify <site>/<command> # 桥接内的端到端冒烟测试
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

## Shell 补全

```bash
opencli completion bash   # 也：zsh、fish
# -> 标准输出上的脚本；根据你的 Shell 的约定进行 source 或保存
```

## 下一步去哪里

| 如果你即将… | 加载这个技能 |
|----------------|----------------|
| 驱动实时浏览器临时（没有适配器可用，或原型设计） | `opencli-browser` |
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
- 不要在失败的适配器无声地回退到手工制作的 `fetch`——`--trace retain-on-failure` 给你浏览器证据和适配器源路径。首先这样做。
