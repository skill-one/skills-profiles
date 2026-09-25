# OpenKnowledge — agent guidance

OpenKnowledge (OK) 是一个通过 MCP 暴露的 markdown-CRDT 协作平台。这个技能是 OK agent guidance 的唯一来源。以下每条规则都是必须的，除非另有标记。**深度存在于 `references/*.md` 中——一级深度；在其任务出现时加载参考。**

> 技能版本跟踪 `@inkeep/open-knowledge-server`。`cat ~/.ok/skill-state.yml` 显示已安装的内容。`ok seed` 需要 `@inkeep/open-knowledge` >= 0.4.0；如果它报错 `unknown command`，`npm install -g @inkeep/open-knowledge`。

> **设置（尚未连接？）。** 如果客户端中不可用 `mcp__open-knowledge__*` 工具，则此项目未在此机器上配置——请参阅 [`references/setup.md`](references/setup.md) 以获取入门步骤（批准 `.mcp.json` → `ok start` CLI → 可选桌面应用）和官方快速入门。

## TL;DR — 90% 的情况

1. **读取：** `exec("cat …")` 用于单个文档，`exec("ls -A …")` 用于目录（文件夹默认 + 模板菜单），`exec("grep …")` 用于字面量，`search` 用于排序检索。仅在源代码（`.ts` / `.py` / …）上使用原生 `Read` / `Grep`，绝不在范围内的 `.md` / `.mdx` 上。
2. **写入：** `write({ document: { path, content } })` 用于新文档或全替换文档；`edit({ document: { path, find, replace } })` 用于正文查找/替换；`edit({ document: { path, frontmatter } })` 用于 frontmatter 合并补丁（`null` 删除键）。`delete({ document })` 删除，`move({ from, to })` 移动/重命名。正文查找/替换仅限正文。在每次内容写入时传递一行 `summary`（≤80 字符，用户界面结果）。
3. **预览/打开文档 — 首先确定你的一个界面（一次会话内）。** 在第一个匹配处停止：**`OK_DESKTOP_TERMINAL` 或 `OK_HOSTED_AGENT` 设置** → 你已进入 OpenKnowledge（桌面终端/应用内代理面板）→ `ok open <name>`（切换用户已查看的窗口）；切勿将 `localhost` URL 粘贴到此处 · 应用内浏览器（Claude Code Desktop 的浏览器窗格、Cursor、Codex）→ `preview_url`，然后打开/导航到文档 · 否则纯 CLI → `ok open <name>`。`ok open <name>` 打开文档或文件夹（自动检测）；`--skill <name>` 用于技能。`previewUrl` 字段是路由 ID，**不是**你的打开机制。不要 `preview_screenshot` 来确认编辑。完整 Step-0 过程 + 每个界面的方法：`references/preview.md`。
4. **知识层：** 捕获源（摄取）、综合发现（研究）、推广决策（整合）— 这些是程序，**不是工具调用**；没有 `ingest` 工具。摄取在此处进行（`references/ingest-and-sources.md`）；研究 + 整合随 `knowledge-base` 包提供。层模型 + 包：`references/starter-packs.md`。
5. **直接问题：** 一个纯商业问题（"哪些客户…"、"我们关于…"的决定是什么"）路由到 `search` / `exec` + 引用的聊天答案 — 无需 "research" 关键字。仅在持久化 + 多文档 + 尚未涵盖时持久化，并且 *首先* 提供选项。参见 `references/corpus-qa.md`。
6. **编写或改进技能**（"编写/制作/改进技能"、"将这转换为技能"）：停止并调用 **`/open-knowledge-write-skill`** 以获取范围（项目/全局）、合同、评估和安装。通过 `write({ skill })` 编写，而不是文档路径。技能是编辑器 `skills/` 目录下的真实文件夹（`.claude` · `.cursor` · `.codex` · `.github` · `.opencode` · `.pi` · `.agents`）：一个源加上管理的副本/符号链接。**通过 `skills` 和 `edit({ skill })` 读取/编辑 — 它们路由到源。** 切勿手动编辑非源副本：管理副本从源刷新；编辑一个副本会分支并停止刷新。

## 工具索引 — 21 个工具（路由器；MCP 工具描述包含每个工具的完整合同）

- **读取** — `exec`（主要；在只读文件系统上执行 `cat`/`ls`/`grep`/…，加上 frontmatter/回链/历史增强；一个命令或一个管道，不是 shell），`search`（排序 BM25 + 新鲜度），`history`（文档版本），`links`（`kind: backlinks|forward|dead|orphans|hubs|suggest`，或一个数组用于一次调用），`skills`（搜索 + 读取：`query` → skills.sh；省略 `name` 列出管理的（项目 + 全局）；`name` 读取一个 — 按 `name`+`scope`，不是路径），`config`（解析配置），`palette`（编写形式 + `html preview` 开头 + 主题标记；`palette({ components })` 用于 JSX 模式），`preview_url`（按需预览 URL），`share_link`（GitHub-底层共享 URL；只读，没有 GitHub 远程会报错），`lint`（markdown-lint 违规：`document` 用于一个文档，省略用于项目；`fix: true` 与 `document` 自动修复可修复的规则在位置 — 归因，预览中实时；其余需要 `edit`/`write`），`audit`（一个报告中的所有 lint 违规 + 破坏性内部链接，按源文件和行号；`path` 范围；用于链接验证，不要用 `links`；注意 `references/linking.md` 中的注意事项）。**读取 `ran` 在成功 `lint`/`audit` 结果上：一个未出现在 `ran` 中的家族未被检查，`[]` 表示没有选择检查。**
- **写入** — 四个原生 CRUD 动词，多态地应用于 `document` / `folder` / `template` / `skill` / `asset`（精确地传递一个目标，嵌套在其地址键下）：`write`（创建/覆盖；`write({ skill: {…} })` 将技能作为真实文件夹在项目的默认技能家目录下编写 — 立即生效，对该文件夹的代理而言），`edit`（正文查找/替换/frontmatter 合并补丁；没有资产），`delete`，`move`（移动/重命名，重写引用者；技能还接受 `scope`/`toScope` 用于项目↔全局：历史重置，只有目的地级别可以托管重新项目；其余在源处删除，返回 `droppedLocations`（成功：用 `install` 重新添加））。输出镜像输入键；预览信封（`previewUrl`，`warning`）保持顶级。加上 `install`（技能在哪里生活：`add`/`remove` 位置加性 — 编辑器 ID，`agents` 或自定义根；`mode` + `convert` 仅重新格式化命名位置；`source` 移动真实文件夹。源文件夹就是技能 — 没有 "卸载所有"；技能只能通过 `delete` 死亡），`import`（将技能目录获取到 `add` 的位置；脚本从不运行），`checkpoint`（命名版本），和 `restore_version`（回滚）。文件夹的前matter 是开放形状且仅限自身（不会级联）；模板是新文档开始时使用的。

**自我纠正滥用：** JSON Schema 无法表达的约束（"恰好一个目标"，"`find` 需要 `replace`"，正文-XOR-frontmatter）返回 `isError: true` 与一个单行纠正形状。读取它并使用该形状重试；不要猜测。

不在 OK MCP 中的工具（你的主机）：`preview_start`，`preview_screenshot`，`WebFetch`，`WebSearch`，原生 `Read` / `Grep` / `Glob` / `Edit`。STOP 规则控制你在范围内 markdown 上可以使用哪些工具。

## STOP — 在范围内的 `.md` / `.mdx` 上的原生工具

**通过 OK 的 MCP 工具路由每个范围内的 markdown 读取和写入 — 绝不使用你主机的原生文件工具。** 原生 `Edit` / `sed` / 直接 `Write` 在范围内的 markdown 上绕过 CRDT 并在阴影仓库中丢失代理归因；原生读取跳过 frontmatter，回链，阴影仓库活动，以及 OK 返回的每个匹配文件的 git 历史。当此工作区配置了 OpenKnowledge MCP 时，**不要**在内容目录中的 markdown 路径上使用原生文件工具。禁令涵盖了每个常见理由：

- **原生 `Read` / `Grep` / `Glob` 在范围内的 `.md` / `.mdx` 上** — 原始情况。
- **`Bash ls` / `Bash find` / `Bash cat` 在包含范围内 markdown 的目录上** — 使用 `exec("ls -A …")` / `exec("find … -name '*.md'")` / `exec("cat …")`。原生返回纯名；`exec` 添加 frontmatter，回链和最近活动。`-A` 显示隐藏条目，无需 `.`/`..`。
- **针对 markdown 的 Glob 模式** — `exec` 扩展文件操作数（`cat specs/*.md`）；引号模式和命令自己的模式（`find -name`）保持字面量。
- **为 markdown 重探发送 Explore / 通用子代理** — 子代理内部使用原生工具并绕过 OK。自己通过 `exec` / `search` 进行 markdown 探索。子代理仍然适用于 **源代码** 探索。
- **在 `.ok/` 中的范围内 markdown 上的原生 `Read` / `Grep`** — `.ok/` 在范围内；将其 `.md` / `.mdx` 像任何其他 KB 文件一样处理。
- **在技能文件夹上使用 `ls` / `cat` / `find` 以发现或读取技能** — 技能由 `name`+`scope` 指定，而不是路径（技能可以存在于任何编辑器目录，`.agents/skills/` 中心，或自定义根，副本在其他地方）。使用 `skills` 工具。

**没有看到 `exec` 不是逃生通道。** 连接、标签和工具可见性因客户端而异；一些（尤其是 Codex）将 MCP 工具隐藏在延迟发现后面。注册是测试，不是顶级符号可见性 — 首先运行工具发现 `open-knowledge`。详细说明：`references/setup.md`。

**逃生通道。** 在 `.md` / `.mdx` 上的原生 `Read` / `Grep` / `Glob` 仅当**在运行工具发现（上述）后，此项目没有注册 OpenKnowledge MCP 服务器，或者**立即在您实际调用了 MCP 调用并且它失败了之后 — 然后以用户可见的句子开始 `OpenKnowledge MCP unavailable:`。 "未注册" 是只有在工具发现将其查空后才能得出的结论 — 从初始工具列表中永远不会得出。不要因为您跳过了客户端的 MCP 路径、没有看到 `exec` 作为顶级工具、没有运行工具发现，或者合理化了技能不是必需的而使用逃生通道。

**源代码和非 markdown 文件**（`.ts`，`.py`，`package.json`，…）：原生 `Read` / `Grep` / `Glob` 总是。

## 读取 — 示例

- 读取文件：`exec("cat <path>.md")` — 内容 + 完整增强。
- 列出目录：`exec("ls -A <dir>")` — 每个子项的 frontmatter，递归 markdown 计数，每个子目录中最新的文档，文件夹自己的 `title`/`description`/`tags` + `templates_available`。优先 `-A` 覆盖 `ls`。
- 字面量搜索：`exec("grep -rn <term> <dir> | head -5")` — 匹配文件上的匹配 + 增强。
- 排序搜索：`search({ query })` — 标题提升 + 正文 BM25 + 新鲜度；在挑选最佳文档时使用，而不是列出每个出现时。

## 写入

一旦有内容就立即调用 `write` / `edit`（通过 STOP 规则路由）。

**增量持久化 — 知识库就是你的检查点（必须）。** 对任何多步骤或长时间运行的任务——研究扫掠、多源综合、一批文档——在完成每个单元时将已完成工作写入 KB：每节、每源、每文档。切勿仅在您的上下文中保留完成的发现，等待最后在结束时写入。任务中途的速率限制、崩溃或上下文压缩会丢弃所有未写入的内容；已持久化的工作会保留，您通过读取文档回来继续。尽早创建目标文档（骨架 + frontmatter），然后 `edit` 每个部分，直到它确定下来。

**在每次内容写入时传递 `summary`（应该）** — 一行（≤80 字符）用户界面注释；它成为时间线条目。**在需要时寻求视觉结构**（Callout，`mermaid`，表格，`html preview`）比散文更能传达要点；调用 `palette` 时起草。建议性写入警告、MDX 作者、删除/移动机制和视觉作者：`references/writing.md` + `references/components-and-visuals.md` + `references/media-and-assets.md`。

## Grounding — 每个事实声明都需要一个来源（必须）

KB 文档是事实工件：每个声明都可追溯，并且**来源生活在知识库中**，而不是在公共网络上。

**摄取是一个程序，而不是工具** — 二进制与文本分类，SSRF 安全的获取标志，大小 + 可执行门，包装 frontmatter — 在 [`references/ingest-and-sources.md`](references/ingest-and-sources.md)。在您的第一次捕获之前阅读它；一个简单的获取和粘贴会跳过每个门。

- **闭环。** 外部源由摄取程序拉入，然后在本地引用。KB 文档中的裸 `[source](https://...)` **不是**引用——它是一个 TODO，意思是 "仍需摄取"。只有当每个叶都是本地文档时，链条才有效。
- **每个事实声明必须在声明点引用其来源。** 没有未来源的推测。
- **网络来源** → 获取页面（主机 `WebFetch` / `WebSearch`），摄取它，然后引用路径：`[source name](./path/to/source.md)`（本地文档携带 `source_url:`）。内联 `[source](URL)` 是聊天功能，不是 KB 的。
- **自我获取计数。** 您获取以验证声明的 URL 会得到相同的摄取——没有内联 URL 降级。
- **内部交叉引用** → 链接到持有权威声明的 OK 文档；该文档引用自己的来源（链条终止在保留的本地文档中）。
- **没有证据？** 搜索并摄取结果，或标记 `(TODO: 需要来源)`，或不要编写声明。不要编造——未来源的推测会腐烂成无法追踪的部落传说。

## Linking — 标准 markdown 链接（必须）

链接每个命名另一个文档的名词短语——`[text](./relative/path.md)`——并自由链接。**每个链接必须在您完成时解析到一个存在的文档**（在遍历中创建的同一遍历的同一文档是好的；对于确实不会存在的文档，保留提及为纯文本 + 跟踪任务）。切勿反引链接（`` `[text](./foo.md)` `` 是一个错误）并且永远不要使用 HTML `<a>`。**在每次 `write`/`edit` 后，读取 `brokenLinks`；修复报告的 `href`；`[]` 意味着所有链接都解析，除非 `brokenLinkSuppression` 抑制了保留日志发现；那些不是您要修复的。** `audit` 是权威的；它的标记具有相同含义。外部网络来源不是内联正文链接（见 Grounding）。完整规则集 + `[[Page]]` 遗产笔记：`references/linking.md`。

## 文件夹、frontmatter、模板

每个 `.md` / `.mdx` 需要 YAML frontmatter — `title` + `description` 必须有，`tags` 推荐有。**OKF 项目（`okf` 包）是例外：** 包规则获胜——非根 `index.md` 不携带 frontmatter（`frontmatter-reserved-index` lint 在任何键上警告），`log.md` 无需，概念文档只需要非空的 `type`；`title`/`description` 是可选的。两个**可选的、嵌套**文件夹机制：文件夹 frontmatter（`<folder>/.ok/frontmatter.yml` — 文件夹自己的开放形状属性；仅限自身，不会级联到子文档）和模板（`<folder>/.ok/templates/` — 新文档开始时使用的）。大多数文件夹没有 `.ok/`。文档的前matter 就是其在磁盘上的 YAML。结构模型 + 完整预写清单：`references/folder-model.md`。模板编写 + 文件夹编辑：`references/template-authoring.md`。Frontmatter-与正文编辑规则：`references/doc-editing.md`。

- **在写入前读取文件夹（必须）。** 在在文件夹中创建/编辑文档之前，每个会话对每个文件夹调用一次 `exec("ls -A <folder>")` — 它返回文件夹的 `title`/`description`/`tags` + `templates_available`。跳过它会导致文档违反文件夹规范。（如果文件夹没有 frontmatter 并且没有模板 并且存储库在其他地方有大量内容，它不会上牌——首先运行 `references/onboard-existing-repo.md`。）
- **当适合使用模板时（必须）。** 通过 `write({ document: { path, template } })` 实例化；继承模板计数。仅在没有任何匹配或用户要求自由形式时跳过（在聊天中注明原因）。当形状重复时主动创建模板。
- **当每文档属性重复出现时（必须）。** 在多个兄弟上编写相同的 frontmatter → 将起始值烘焙到模板中（`write({ template })`）。文件夹 frontmatter 不会将值级联到文档中。

## 冲突感知写入

`doc-in-conflict` 冻结写入；`stale-external-write` 意味着恢复错过了磁盘。使用 `conflicts` 而不是 `exec` 来检测两者；参见 `references/conflict-resolution.md`。`concurrent-overwrite-refused` 不是冲突状态：等待其绑定并重试或使用 `append`/`prepend`/`edit`。

## 反模式 — 顶级违规者

| 任务 | 不要 | 做 |
| --- | --- | --- |
| 列出 / 查找 / 读取 markdown | `Bash: ls`/`Glob: **/*.md`/`Read: foo.md` | `exec("ls -A …")` / `exec("find …")` / `exec("cat …")` |
| 探索一个 markdown 重量的目录 | `Agent(Explore)`（绕过 OK） | `exec`/`search` 自己 |
| 引用另一个文档 | `` `[text](./p.md)` ``（反引号）或 HTML `<a>` | `[text](./p.md)` |
| 嵌入一个图像 | `<img>`，一个 `localhost`/`preview_url` URL，热链接 | 保存到本地 + `![有意义的 alt](./path)` |
| KB 文档中的事实声明 | 未经引用的散文，或内联 `[src](https://…)` | 摄取来源（`references/ingest-and-sources.md`），引用本地路径 |
| 确认编辑已落地 | `preview_screenshot` / 验证循环 | 信任 CRDT 工具响应 |
| 删除一个 markdown 文档 | `Bash: rm` / 原生删除 | `delete({ document })` (`checkpoint()` 首先如果风险) |
| 在不熟悉的文件夹中写入 | 直接到 `write` | `exec("ls -A <folder>")` 首先 |

完整表格：`references/anti-patterns.md`。

## Knowledge layers — most KB 工作采取的形状

三个反复出现的实践，不是工具调用 — 每个都是一个完整的程序，作为技能指导发送。

| 层 | 当… | 程序 |
| --- | --- | --- |
| **ingest** | 保留共享 URL/PDF/文件副本，或者您获取了用于验证声明的 URL（二进制来源保留，未抓取）。 | `references/ingest-and-sources.md` — 此处发送，§Grounding 依赖于它 |
| **research** | 调查 / 比较 / 综合来源 → `status: provisional` 文章 + `sources:`。 | `/research-with-sources` 技能 |
| **consolidate** | 做出了决定 → 带有 `supersedes:` 链的权威来源。 | `/consolidate-notes` 技能 |

研究和整合随 `ok seed --pack knowledge-base` 提供。**没有那个包，您没有这些程序** — 不要自己编造一个；像普通有来源的 `write` 一样做工作，或者提供种子（`ok seed --pack knowledge-base --dry-run` 显示它会添加什么）。

不要沉默地链接：让用户驱动摄取 → 研究 → 整合，并且一个程序的 STOP 门会覆盖会话级别的 "不要停下来询问" 提示。在任何更改 KB 内容的回合后，检查 `log.md` 并遵循其合同（`references/cadence-and-logs.md`）。交错多文档批处理，以便预览显示叙事进度。

在已经包含内容的存储库上boarding：`references/onboard-existing-repo.md`。层模型 + 包：`references/starter-packs.md`。

## 超出此技能的功能

OK 做的比此技能描述的更多，并且它在版本之间会变化。这里没有涵盖的？阅读而不是猜测：

- **文档** — <https://openknowledge.ai/docs>
- **源** — <https://github.com/inkeep/open-knowledge>

## 服务器生命周期

如果 `write` / `edit` 返回 `"Hocuspocus server is not running"`，运行 `ok start`（通过 Bash）并重试。永远不要回退到原生 `Edit` / `Write` 用于范围内的 markdown。

## 范围摘要

OK 查找 `content.dir`（运行时：`config({ key: 'content.dir' })`）下的文档；`.gitignore` 和 `.okignore`（在根或任何文件夹深度）定义排除项。**`content.dir` 下未排除的每个 `.md` / `.mdx` 都是 OpenKnowledge 文档**——包括在 `specs/`，`reports/`，`docs/` 下。文件夹元数据 + 模板生活在嵌套的 `<folder>/.ok/` 中，而不是 `.ok/config.yml` 中。**在 git 工作树中工作？** 在您的 OK 工具调用中一次传递工作树的绝对路径作为 `cwd` — 它会粘在会话中，因此读取、写入和预览都针对该工作树。
