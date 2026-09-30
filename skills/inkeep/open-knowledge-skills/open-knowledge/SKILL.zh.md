---
name: open-knowledge
description: 权威的 agent-runtime 合约，用于在 OpenKnowledge 项目内部工作——这是一个通过 MCP 暴露的 markdown-CRDT 知识库。在读取、列出、搜索、编辑或对项目中的任何 `.md` 或 `.mdx` 文件进行 lint 时使用，并在任何 `mcp__open-knowledge__*` 工具调用（`exec`、`search`、`write`、`edit`、`lint` 及其他）之前使用。由 `ok init` 安装，因此其存在意味着这是一个 OpenKnowledge 项目，并管理此处的所有 markdown 文件。涵盖读取/写入工具界面、基础和链接规则、文件夹/模板约定、实时浏览器预览，以及 OK 的 MCP 工具（而非原生文件工具）处理作用域内 markdown 的规则。
---

# OpenKnowledge — agent guidance

OpenKnowledge (OK) 是一个通过 MCP 暴露的 markdown-CRDT 协作平台。这项技能是 OK agent guidance 的唯一来源。以下每条规则都是必须遵守的，除非另有说明。**深度存在于 `references/*.md` 中——一级深度；在其任务出现时加载参考。**

> 技能版本跟踪 `@inkeep/open-knowledge-server`。`cat ~/.ok/skill-state.yml` 显示已安装的内容。`ok seed` 需要 `@inkeep/open-knowledge` >= 0.4.0；如果出现 `unknown command` 错误，请运行 `npm install -g @inkeep/open-knowledge`。

> **设置（尚未连接？）。** 如果客户端中不可用 `mcp__open-knowledge__*` 工具，则该项目未在此计算机上配置——请参阅 [`references/setup.md`](references/setup.md) 获取入门步骤（批准 `.mcp.json` → `ok start` CLI → 可选桌面应用）和官方快速入门。

## TL;DR — 90% 情况

1. **读取：** `exec("cat …")` 用于单个文档，`exec("ls -A …")` 用于目录（文件夹默认值 + 模板菜单），`exec("grep …")` 用于字面量，`search` 用于排序检索。仅在源代码（`.ts` / `.py` / …）上使用原生 `Read` / `Grep`，绝不在范围内的 `.md` / `.mdx` 上。
2. **写入：** `write({ document: { path, content } })` 用于新建或全量替换文档；`edit({ document: { path, find, replace } })` 用于正文查找替换；`edit({ document: { path, frontmatter } })` 用于 frontmatter 合并补丁（`null` 删除键）。`delete({ document })` 删除，`move({ from, to })` 移动/重命名。正文查找替换仅限正文。在每次内容写入时传递一行 `summary`（≤80 字符，用户界面结果）。
3. **预览/打开文档——首先确定你的一个界面（会话内仅一次）。** 在第一个匹配项处停止：**`OK_DESKTOP_TERMINAL` 或 `OK_HOSTED_AGENT` 设置** → 你已进入 OpenKnowledge（桌面终端/应用内 agent 面板）→ `ok open <name>`（切换用户当前正在查看的窗口）；切勿将 `localhost` URL 粘贴到此处回复中 · 应用内浏览器（Claude Code Desktop 的浏览器窗格、Cursor、Codex）→ `preview_url`，然后打开/导航到文档 · 否则纯 CLI → `ok open <name>`。`ok open <name>` 打开文档或文件夹（自动检测）；`--skill <name>` 用于技能。`previewUrl` 字段是路由 ID，**不是**你的打开机制。不要使用 `preview_screenshot` 确认编辑。完整 Step-0 过程 + 每个界面指南：`references/preview.md`。
4. **知识层：** 捕获来源（摄取）、综合发现（研究）、推广决策（整合）——流程，**不是**工具调用；没有 `ingest` 工具。摄取在此处进行（`references/ingest-and-sources.md`）；研究 + 整合随 `knowledge-base` 包提供。层模型 + 包：`references/starter-packs.md`。
5. **直接问题：** 纯粹的商业问题（"哪些客户…"、"我们关于…"）路由到 `search` / `exec` + 引用聊天答案——无需 "research" 关键词。仅在持久化、多文档且未覆盖时持久化，并*首先提供*。参见 `references/corpus-qa.md`。
6. **编写或改进技能**（"编写/制作/改进技能"、"将其转换为技能"）：停止并调用 **`/open-knowledge-write-skill`** 以确定范围（项目/全局）、合同、评估和安装。通过 `write({ skill })` 编写，而不是文档路径。技能是编辑器 `skills/` 目录下的真实文件夹（`.claude` · `.cursor` · `.codex` · `.github` · `.opencode` · `.pi` · `.agents`）：一个来源加管理副本/符号链接。**通过 `skills` 和 `edit({ skill })` 读取/编辑——它们路由到来源。** 切勿手动编辑非来源副本：管理副本从来源刷新；编辑一个副本会分叉并停止刷新。

## 工具索引 — 21 个工具（路由器；MCP 工具描述包含每个工具的完整合同）

- **读取** — `exec`（主要；`cat`/`ls`/`grep`/… 在只读文件系统上，加 frontmatter/反向链接/历史增强；一个命令或一个管道，不是 shell），`search`（排序 BM25 + 新鲜度），`history`（文档版本），`links`（`kind: backlinks|forward|dead|orphans|hubs|suggest`，或一个数组用于一次调用），`skills`（搜索 + 读取：`query` → skills.sh；省略 `name` 列出管理（项目 + 全局）；`name` 读取一个——按 `name`+`scope`，不是路径），`config`（解析配置），`palette`（编写表单 + `html preview` 启动器 + 主题标记；`palette({ components })` 用于 JSX 模式），`preview_url`（按需预览 URL），`share_link`（GitHub-底层共享 URL；只读，没有 GitHub 远程会报错），`lint`（markdown-lint 违规：`document` 用于一个文档，省略用于项目；`fix: true` 与 `document` 一起自动修复可修复规则——归因，预览中实时；其余需要 `edit`/`write`），`audit`（一个报告中的所有 lint 违规 + 破坏性内部链接，按来源文件和行号；`path` 范围；用于链接验证，不要用 `links`；注意事项在 `references/linking.md` 中）。**读取 `ran` 在成功 `lint`/`audit` 结果上：一个未在 `ran` 中的家族未被检查，`[]` 表示未选择任何检查。**
- **写入** — 四个原生 CRUD 动词，多态处理 `document` / `folder` / `template` / `skill` / `asset`（精确传递一个目标，嵌套在其地址键下）：`write`（创建/覆盖；`write({ skill: {…} })` 将技能作为真实文件夹在项目的默认技能家目录下编写——立即生效，仅对该文件夹的 agent），`edit`（正文查找替换/frontmatter 合并补丁；无资产），`delete`，`move`（移动/重命名，重写引用者；技能也接受 `scope`/`toScope` 用于项目↔全局：历史重置，仅目的地级别可托管重新项目；其余在来源处删除，返回为 `droppedLocations`（成功：使用 `install` 重新添加））。输出镜像输入键；预览信封（`previewUrl`，`warning`）保持顶级。加 `install`（技能在哪里生活：`add`/`remove` 位置加性——编辑器 ID，`agents` 或自定义根；`mode` + `convert` 仅重新命名指定位置；`source` 移动真实文件夹。来源文件夹就是技能——没有 "卸载所有"；技能仅通过 `delete` 死亡），`import`（将技能目录获取到 `add` 的位置；脚本从不运行），`checkpoint`（命名版本），和 `restore_version`（回滚）。文件夹的前matter 是开放形状且仅限自身（不会级联）；模板是新文档的起点。
- **冲突** — `conflicts`（`kind: list|content`），`resolve_conflict`（从该冲突的 `resolutionOptions` 写入解决方案；仅对 `merge-native` 提交）。参见 `references/conflict-resolution.md`。

**在误用时自我纠正：** JSON Schema 无法表达的约束（"恰好一个目标"，"`find` 需要 `replace`"，正文-XOR-frontmatter）返回 `isError: true` 与一个单行纠正形状。读取它并使用该形状重试；不要猜测。

不在 OK MCP 中的工具（你的主机）：`preview_start`，`preview_screenshot`，`WebFetch`，`WebSearch`，原生 `Read` / `Grep` / `Glob` / `Edit`。STOP 规则控制你在范围内 markdown 上可以使用哪些工具。

`doc-in-conflict` 会冻结写入；`stale-external-write` 表示恢复时遗漏了磁盘。使用 `conflicts` 来检测这两种情况，而不是 `exec`；请参阅 `references/conflict-resolution.md`。`concurrent-overwrite-refused` 不是冲突状态：等待其约束并重试，或使用 `append`/`prepend`/`edit`。

## 反模式 — 最常见的违规行为

| 任务 | 不要 | 应该 |
| --- | --- | --- |
| 列出/查找/读取 Markdown | `Bash: ls`/`Glob: **/*.md`/`读取: foo.md` | `exec("ls -A …")` / `exec("find …")` / `exec("cat …")` |
| 探索一个 Markdown 丰富的目录 | `Agent(Explore)`（绕过 OK） | `exec`/`search` 自己 |
| 引用另一个文档 | `` `[text](./p.md)` ``（反引号内）或 HTML `<a>` | `[text](./p.md)` |
| 嵌入图片 | `<img>`，一个 `localhost`/`preview_url` URL，热链接 | 本地保存 + `![有意义的 alt](./path)` |
| 知识库文档中的事实陈述 | 没有引用的散文，或内联 `[src](https://…)` | 消化来源 (`references/ingest-and-sources.md`)，引用本地路径 |
| 确认编辑已应用 | `preview_screenshot` / 验证循环 | 相信 CRDT 工具的响应 |
| 删除 Markdown 文档 | `Bash: rm` / 本地删除 | `delete({ document })` (`checkpoint()` 首先如果风险高) |
| 在不熟悉的文件夹中写入 | 直接写入 `write` | 首先执行 `exec("ls -A <folder>")` |

完整表格：`references/anti-patterns.md`。

## 知识层级 — 知识库工作最常见的形态

三种反复出现的实践，不是工具调用 — 每种都是一个完整的程序，作为技能指导交付。

| 层级 | 当... | 程序 |
| --- | --- | --- |
| **ingest** | 保留一个共享的 URL/PDF/文件原样，或你获取了一个 URL 来为断言提供依据（二进制来源保留，不抓取）。 | `references/ingest-and-sources.md` — 此处交付，§Grounding 依赖于它 |
| **research** | 调查 / 比较 / 综合来源 → `状态: 暂定` 文章 + `来源:`。 | `/research-with-sources` 技能 |
| **consolidate** | 做出决定 → 具有约束来源的 `supersedes:` 链的权威来源。 | `/consolidate-notes` 技能 |

研究和整合随 `ok seed --pack knowledge-base` 到来。**没有那个包你就没有这些程序** — 不要自己编造一个；作为普通的基于依据的 `write` 做工作，或提供种子的机会 (`ok seed --pack knowledge-base --dry-run` 显示它会添加什么)。

不要无声地链接：让用户驱动摄入 → 研究 → 整合，并且一个程序的 STOP 门控会覆盖会话级别的“不要询问”提示。在任何更改知识库内容的回合后，检查 `log.md` 并遵循其合同 (`references/cadence-and-logs.md`)。交错多文档批处理，以便预览显示叙事进度。

引导一个已有内容的仓库：`references/onboard-existing-repo.md`。层级模型 + 包：`references/starter-packs.md`。

## 超出此技能的能力

OK 做的比此技能描述的更多，并且在版本之间会变化。未涵盖的内容？阅读而不是猜测：

- **文档** — <https://openknowledge.ai/docs>
- **来源** — <https://github.com/inkeep/open-knowledge>

## 服务器生命周期

如果 `write` / `edit` 返回 `"Hocuspocus 服务器未运行"`，运行 `ok start`（通过 Bash）并重试。永远不要回退到本地的 `Edit` / `Write` 来处理范围内的 Markdown。

## 范围回顾

OK 查找在解析的 `content.dir`（运行时：`config({ key: 'content.dir' })`）下的文档；`.gitignore` 和 `.okignore`（在根或任何文件夹深度）定义排除项。**`content.dir` 下每个未排除的 `.md` / `.mdx` 都是 OpenKnowledge 文档** — 包括在 `specs/`，`reports/`，`docs/` 下。文件夹元数据 + 模板在嵌套的 `<文件夹>/.ok/` 中，而不是在 `.ok/config.yml` 中。**在 git 工作树中工作？** 将工作树的绝对路径作为 `cwd` 在你的 OK 工具调用中一次性传递 — 它会持续整个会话，因此读取、写入和预览都针对该工作树。
