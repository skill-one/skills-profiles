# OpenKnowledge — 它是什么以及如何安装

OpenKnowledge (OK) 是一个基于 markdown-CRDT 的协作平台。它将一个 `.md` / `.mdx` 文件目录转换成一个实时的多写者知识库：代理和人类实时编辑相同的文档，每次更改都会被归属，浏览器预览会实时渲染更改。

这项技能涵盖了 **发现、安装和打开 OpenKnowledge 文件** — 包括不属于项目的单个文件（见下文 *在项目外打开文件*）。它 **不** 包含项目内的读写运行时合约（原生文件工具的 STOP 规则、基础和链接规则、MCP 路由表） — 这些会单独作为由 `ok init` 安装的项目本地技能（见下文 *在项目内工作*）。

## 在仓库上安装 OpenKnowledge

从仓库根目录运行 `ok init`：

```bash
npx @inkeep/open-knowledge init
# 或者，在全局安装后：
npm install -g @inkeep/open-knowledge
ok init
```

`ok init` 是唯一的设置动词。它：

- 搭建 `.ok/` 目录（项目配置 — `content.dir` 默认为 `.`）；
- 将 OpenKnowledge MCP 服务器连接到这台机器上检测到的编码代理 — 使用 `--no-mcp` 跳过；
- 将 **项目本地运行时技能** 安装到每个检测到的代理的技能目录（`<agent-dir>/skills/open-knowledge/`）中，以便在这个仓库中工作的代理获得完整的读写合约。OK 只会写入已经存在的代理目录 — 它从不创建一个，所以对于未使用的代理没有任何显示，并且当发现没有时，`ok init` 会这样说明；
- 确保项目有一个 `.git/`。

随时重新运行 `ok init` 以刷新连接和技能到已安装的 CLI 版本。

## 与协作者共享 OpenKnowledge 项目

一个 OK 项目会随其仓库一起移动。要共享一个项目：

1. 提交 `.ok/` 目录以及 `ok init` 创建的任何项目本地 `<agent-dir>/skills/open-knowledge/` 目录，以及你的 `.md` 内容。
2. 协作者克隆仓库并运行一次 `ok init` — 这会在他们的机器上注册 MCP 服务器并刷新项目技能。
3. 使用 `ok start` 启动编辑器 + 预览（或在 OK 桌面应用中打开项目）。

一旦两个写作者对相同的内容目录打开了项目，协作就是实时的。

## `ok cowork` — Claude Chat & Cowork

`ok init` 的编辑器连接不会到达 Claude Chat 或 Cowork — 这些会读取 Claude 桌面应用内的单独技能列表。运行 `ok cowork` 来构建 `openknowledge.skill` 并打开 Claude 桌面应用，以便用户可以上传它（自定义 → 技能 → + → 创建技能 → 上传技能）。

## OK 桌面应用

OK 桌面应用是独立的 macOS 应用（`@inkeep/open-knowledge-desktop`）。它捆绑了自己的 CLI，将项目作为编辑器 + 预览窗口打开，并在每次启动时保持项目的 MCP 连接和技能最新。从发布页面下载 DMGs。

## 在项目外打开文件

OpenKnowledge 可以打开一个 **不属于** OK 项目的单个 markdown 文件 — 一个松散的 `.md` / `.mdx`，**或者一个位于未经过 `ok init` 初始化的常规仓库/文件夹中的文件**。它在一次性会话（操作系统临时目录中的临时项目）中打开，与在项目内获得的相同实时预览。

**永远不要运行 `ok init` 只是为了查看或打开一个文件。** `ok init` 将一个仓库转换为一个共享的 OpenKnowledge 项目；它不是打开一个文件的先决条件。打开文件不需要项目、`.ok/` 或已经运行的服务器 — 以下每个路径都会自行启动会话。

当被要求打开或预览此类文件时，**根据你实际拥有的查看界面来决定** — 检查工具，而不是主机名。只有在你确实有一个浏览器时才打开浏览器标签；永远不要在一个没有浏览器的主机上弹出一个浏览器标签。

- **你有一个应用内/内置的浏览器**（Claude Code Desktop 的浏览器窗格、Cursor、Codex 以及类似应用） — 这是默认设置：调用 **`preview_url` MCP 工具**，将 `file` 设置为绝对路径（它会找到或按需启动会话，并返回一个完整的 `url`），然后 **立即在你的应用内浏览器中打开那个 `url`**。"打开它" 意味着导航你的浏览器 — 不要只是打印 URL 并停止。这也是在安装了 OK 桌面应用时唯一可以查看浏览器的方式（`ok open` 优先使用桌面应用）。只从 `preview_url` 获取 URL — 永远不要通过 `ok ps` / `ok status` / `ok start` 或猜测端口来寻找它。
- **没有应用内浏览器**（纯标准输入输出 CLI） — 运行 `ok open /abs/path/to/file.md`：如果安装了桌面应用，它会打开桌面应用，否则会打开浏览器，并自行启动会话。不要强迫用户打开他们没有请求的浏览器标签；`ok open` 是这里的正确默认设置。如果 `ok` 不在 PATH 中，`npx @inkeep/open-knowledge open /abs/path/to/file.md` 会做同样的事情。

如果这个主机没有将 OK MCP 服务器连接起来，就没有 `preview_url` 可以调用 — 使用上述 `ok open` 路径。不要手动重建 `preview_url` 所做的工作（自己启动 `ok mcp`，从 `ok ps` 中抓取端口）。

给出绝对路径。`ok open` 会打印它为该路径解析的绝对项目根，并且当解析的根位于另一个项目内时，也会命名包含它的项目。阅读那行内容，而不是假设你得到了哪个项目。

要自己命名项目，请传递 `--project <dir>`。它在任何出现的地方都会得到尊重：`--project <dir>` 或 `--project=<dir>`，在路径之前或之后，有或没有 `.md` 扩展名。如果它无法得到尊重，命令会以非零状态退出并说明原因，所以你永远不需要第二个命令来知道它在哪里落地，也永远不需要停止服务器来纠正它。

重新打开同一个文件会落在同一个会话上。永远不要构造或猜测 URL — 使用 `preview_url` 返回的那个。

## OK 还能做什么

这项技能没有枚举 OK 的功能，并且它们在版本之间会发生变化。当被问及 OK 是否支持某功能时，请阅读而不是猜测：

- **文档** — <https://openknowledge.ai/docs>
- **源代码** — <https://github.com/inkeep/open-knowledge>

## 在项目内工作 — 使用项目本地技能，而不是这个

**不要** 使用这项技能来执行 OpenKnowledge 读取或写入。运行时合约 — 在范围内 markdown 的原生文件工具的 STOP 规则、预览附加握手、基础和链接规则、MCP 工具路由表 — 存在于一个 **单独的项目本地技能** 中，该技能会在每次 `ok init` 运行时安装到每个检测到的代理的技能目录（`<agent-dir>/skills/open-knowledge/SKILL.md`）中。

如果用户正在一个有 `.ok/` 目录的项目内编辑 markdown，而这项发现技能是加载的唯一 OpenKnowledge 技能，则项目本地技能缺失（仓库从未 `ok init` 过，或者技能目录没有被提交）。建议用户运行 `ok init` 来安装它。

## 了解更多

- 运行 `ok --help` 获取完整命令列表。
