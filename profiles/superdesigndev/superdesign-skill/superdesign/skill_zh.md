Superdesign 帮助您寻找设计灵感，并在无限画布上生成或迭代设计草稿，提供多个领先的模型用于不同的设计任务和并排探索。当设计需要新的视觉资源时，它还可以提供图像和视频生成。

---

# 核心场景（该技能处理的内容）

1. **分析代码库以进行设计工作** — `superdesign init` 在 `.superdesign/init/` 中构建可重用的 UI 上下文；阅读 [INIT.md](references/INIT.md)。
2. **设计、重现或改进 UI** — 在画布上创建页面、功能、流程和新产品；阅读 [SUPERDESIGN.md](references/SUPERDESIGN.md)。
3. **选择和比较领先的模型** — 运行 `list-models`，选择适合任务的模型，或使用不同的模型探索独立方向。
4. **创建设计系统和可重用组件** — 建立视觉基础，提取模式，并设计连接的多页面体验。
5. **从实时网站或参考 URL 进行设计** — 提取并应用其设计语言；阅读 [WEBSITE.md](references/WEBSITE.md)。
6. **创建或导出演示文稿** — 规划可编辑的幻灯片大纲，在聊天中批准它，生成实际的演示文稿草稿，进行幻灯片安全的编辑，或在需要且支持时重建可编辑的 PPTX；阅读 [PRESENTATION.md](references/PRESENTATION.md)。
7. **创建图形** — 海报、封面、社交帖子、缩略图、传单和广告；阅读 [GRAPHIC.md](references/GRAPHIC.md)。
8. **生成辅助图像或视频** — 在适当的时候使用原生图像生成，或选择 Superdesign 的生成模型；阅读 [ASSET_GENERATION.md](references/ASSET_GENERATION.md)。
9. **继续或直接纠正现有工作** — 通过 [RESUME.md](references/RESUME.md) 继续保存的目标，或在直接编写是正确路径时使用 [design-with-your-model.md](references/design-with-your-model.md)。

继续草稿时，请遵循 [SUPERDESIGN.md](references/SUPERDESIGN.md) **迭代模式路由**：replace 替换所选方向的历史版本；branch 仅用于用户想要比较的替代方案。

# 第 0 步 — 环境预检（任何 CLI 步骤之前）

Superdesign 完全通过其 CLI 运行，因此您必须能够执行 shell 命令。在执行任何 CLI 验证之前，请首先确认此能力。

如果您在这个环境中无法运行 shell 命令（根本没有终端/执行工具），或者您的第一个 `npx --yes @superdesign/cli@latest` 预检尝试失败，因为命令执行本身不可用（启动器报告它无法运行命令 / 没有shell），则停止。不要继续重试或临时解决方法。告诉用户一次，并选择与您运行位置匹配的消息：

- **标准 ChatGPT 聊天，没有 Work 模式工具** — 使用确切副本，因为 Work 选项卡是修复方法：

  ```text
  Superdesign 插件不支持聊天。请切换到 Work 选项卡并将此提示粘贴其中以获得完整体验。
  ```

- **任何其他启动器**（一个 shell 不可用或禁用的编码代理） — 不要发送 ChatGPT 副本；没有可以切换的 Work 选项卡。明确说明 Superdesign 通过 shell 驱动其 CLI，此会话无法运行 shell 命令，并且他们可以在具有 shell 访问的会话中重新运行它或在 https://superdesign.dev 的 Web 应用中设计。

# 第 1 步 — 是否有代码库要分析？

两个入口路径。选择其中一个，在进行任何 init 或设计工作之前进行廉价、确定的检查。

**无有意义的代码库**（空工作区、草稿/沙盒目录、没有前端代码） — 当所有这些都成立时，将工作区视为“无代码库”：

- 没有 `.superdesign/init/` 文件已经存在，并且
- 没有包含前端依赖的依赖清单（没有 `package.json`，或者 `package.json` 的依赖不包含前端框架/UI 库 — react、vue、svelte、angular、next、nuxt、astro 等），并且
- 没有找到前端源代码（快速扫描 `.tsx`/`.jsx`/`.vue`/`.svelte` 文件，任何 `.html`/`.css` 文件，例如根 `index.html` + `style.css`，或具有 UI 文件的 `src/`/`app/`/`components/` 目录，结果为空）。

→ 完全跳过 repo init。不要“分析”空的沙盒，也不要要求用户指向他们没有的 repo。相反，通过对话首先收集设计上下文：询问他们想要构建什么，目标受众/平台、风格/品牌偏好，以及任何参考设计或灵感。然后通过 [SUPERDESIGN.md](references/SUPERDESIGN.md) 中的 **BRAND NEW PROJECT** 路径进行设计。

**有实际代码库**（任何前端代码，或现有的 `.superdesign/init/`） — 在设计之前，repo init 必须至少完成一次。通过 Step 1.5 重用有效的初始化目标；仅在 init 不完整或无法使用热状态时运行完整分析。

**例外 — 独立提取**：如果任务仅是从网站的 DNA 提取或从 URL 设置/刷新 `design-system.md`（`extract-website` → `design-system.md`，没有设计生成；阅读 [WEBSITE.md](references/WEBSITE.md) 了解配方），则无需 repo init — 提取外部网站的风格不需要分析用户的代码库。在为现有代码库的 UI 生成设计之前（重现/重新设计现有页面），init 仍然是必需的。

**例外 — 图形**：海报/营销资产（场景 7）即使在实际代码库中也跳过 init — 简报包含风格，并且 init 的输出的大部分（组件、布局、路由、页面）对固定画布艺术品没有影响。图形简报回合询问艺术品是否应与此 repo 的产品保持一致（[GRAPHIC.md](references/GRAPHIC.md) Step 1）；只有“是”才会拉入设计系统/品牌上下文 — 仅当上下文不存在时才运行 init。

**例外 — 演示文稿**：幻灯片演示文稿（场景 6）默认跳过 UI repo init，因为路由、组件和页面依赖树对幻灯片创建没有帮助。遵循 [PRESENTATION.md](references/PRESENTATION.md)。当用户想要具有品牌的产品演示文稿时，使用与产品相关的文档、设计系统上下文和品牌资产；仅在需要匹配代码库品牌且尚未存在可用的品牌/主题上下文时运行 init。

**例外 — 图像/视频生成**：一个独立的生成资产（场景 8）即使在实际代码库中也跳过 init。阅读 [ASSET_GENERATION.md](references/ASSET_GENERATION.md)，并收集请求的资产实际需要的项目、品牌、参考或目标上下文。如果资产是更广泛的 UI、演示文稿或图形设计任务的一部分，请遵循该任务的正常 init/简报路径，并在需要新视觉时仅使用资产生成。

# 第 1.5 步 — 在重新发现之前继续（实际代码库 UI 路径）

在读取 init 艺术品或源文件之前，检查 `.superdesign/resume.json` 以查找请求的路由/功能。匹配的目标默认为 [RESUME.md](references/RESUME.md)，无论用户是否说“继续”、“更改”、“重新设计”或只给出直接指令，例如“使仪表板更暗”。意图措辞永远不会决定热路由与冷路由。

首先应用保存的目标的信任/结构检查。一个安全、结构有效的目标会重用保存的项目、草稿、组件记录、设计方向和精确的 `--context-file` 束：匹配的哈希值进入热继续，而冲突值进入增量刷新，无需冷重新发现。如果请求需要代码理解，而活动草稿元数据没有捕获，请使用 RESUME.md 的目标上下文扩展规则；不要重新运行完整发现，而仅仅是为了理解该请求。

仅在以下情况下使用冷路径：没有保存的条目覆盖请求的目标，用户明确要求从头开始从真实基准，状态不安全/结构无效，或目标修复确定它已经过时，无法通过增量修复。新的代理会话、不同的措辞或指纹不匹配永远不会强制冷路由。

# Init：Repo 分析（实际代码库路径）

当实际代码库存在（根据 Step 1，并且没有 Step 1 例外适用）且 init 未完成时，您必须自动执行：

1. 创建 `.superdesign/init/` 目录
2. 阅读 [INIT.md](references/INIT.md)
3. 按其说明分析代码库并编写上下文文件

**Init 完成测试（一个可决定的规则，用于所有地方）**：init 只有在以下所有六个命名文件都存在且非空时才完成。缺少其中任何一个文件，或包含空的文件（例如中断的 init）的目录不是完整的 — 重新运行完整的 init，它将重新生成所有六个；覆盖现有文件是预期且可以的。

不要要求用户手动执行此操作 — 直接执行即可。

# Init 文件（冷/过时上下文路径）

对于目标的第一设计，或 [RESUME.md](references/RESUME.md) 确定保存的上下文已过时/不可用时，在收集目标上下文之前，读取所有六个文件：

- `components.md` — 具有完整源代码的共享 UI 原语
- `layouts.md` — 共享布局组件（导航、侧边栏、页眉、页脚）
- `routes.md` — 页面/路由映射
- `theme.md` — 设计令牌、CSS 变量、Tailwind 配置
- `pages.md` — 页面组件依赖树（每个页面需要的文件）
- `extractable-components.md` — 可以作为可重用 DraftComponents 提取的组件

在有效的热继续中，只需检查所有六个文件是否存在且非空 — 不要读取其内容。重用目标保存的上下文束；仅在 [RESUME.md](references/RESUME.md) 明确触发目标上下文扩展时，才读取狭义选择的原生文件。

**当为现有页面进行冷设计时**：首先检查 `pages.md` 以查找页面的依赖树 — 候选的 `--context-file` 文件集。在 [SUPERDESIGN.md](references/SUPERDESIGN.md) 中应用 PAYLOAD BUDGET 规则，以防止 400。然后还添加 globals.css 令牌、tailwind.config 和 design-system.md。根据 [RESUME.md](references/RESUME.md) 持久化最终选择。

# Superdesign CLI（任何命令之前必须使用）

**重要**：按需使用 `npx --yes @superdesign/cli@latest` 运行 CLI。开始每个会话时使用基本命令 — 它就是预检。

1. 预检一次：
   ```
   npx --yes @superdesign/cli@latest
   ```
   基本命令一次性验证所有内容：CLI 是否运行、`auth:` 状态行（`authenticated as team "…"` 与 `not authenticated — run superdesign login`）、以及最近的项目列表。在有效的热继续中，直接使用保存的 `projectId`/`activeDraftId`。否则，在决定是否重用现有项目或 `create-project` 时，读取最近项目列表；`fetch-design-nodes --project-id <id>` 是在持久化恢复状态不可用或被拒绝时恢复草稿 ID 的备用方法。

2. 如果 `auth:` 行说不认证，立即运行登录，在执行任何真实命令之前：
   ```
   npx --yes @superdesign/cli@latest login
   ```
   等待登录成功完成后再继续。

3. 使用相同的 `npx --yes @superdesign/cli@latest` 前缀运行预期命令。会话仍然可能在流程中过期 — 按照失败块处理后续的 auth/login 错误。

> **永远不要假设用户已经登录** — 而是读取预检的 `auth:` 行，而不是猜测或用真实命令探测。

## 当命令失败

- **Auth/login 错误**（CLI 运行但拒绝了会话）：运行 `login`（上述），然后重试预期命令一次。如果登录本身失败（无头/无浏览器认证、过期流、用户拒绝），明确告诉用户并停止 — 不要继续重试或临时解决。
- **`extract-website` 失败或超时**（它可以需要 ~60–120 秒）：重试一次。如果仍然失败，建议在不进行提取的情况下继续（从对话/现有设计系统设计）而不是阻塞。
- **一般规则**：最多重试一次失败的命令。如果 `create-design-draft` 或 `iterate-design-draft` 仍然失败，继续通过 [design-with-your-model.md](references/design-with-your-model.md)；否则报告失败并停止。

## 命令示例

始终使用完整的按需运行器前缀，例如：

```bash
npx --yes @superdesign/cli@latest create-project --title "X"
```

完整调用位于其使用位置 — [SUPERDESIGN.md](references/SUPERDESIGN.md) 中的 SOP 和 [GRAPHIC.md](references/GRAPHIC.md) 中的图形步骤；标志集来自 `<command> --help`，而 [SUPERDESIGN.md](references/SUPERDESIGN.md) 中的 COMMAND CONTRACT 涵盖了帮助遗漏的陷阱。

CLI 默认为代理优化的输出（紧凑 TOON 加 `help[]` 下一步提示）；仅在需要完整机器可读负载时才添加 `--json`。

# 揭示画布 URL

每个项目/草稿命令的默认输出包括一个 `canvas:` 链接（项目画布，`https://superdesign.dev/teams/<teamId>/projects/<projectId>`）和对于草稿的 `preview:` 链接（`https://superdesign.dev/preview/draft/<draftId>`）。从命令输出中读取这些 — 不要手动构建它们（ID 是服务器生成的）。

创建项目或设计草稿后，以及在自然的审查时刻（在 `iterate-design-draft` 或 `execute-flow-pages` 之后），将 `canvas` URL 作为可点击的链接提供给用户，并邀请他们打开它以查看设计流入并留下反馈。在画布 URL 中添加 `?live=1` 会打开实时视图，草稿将按生成顺序出现。

## 浏览器选择

`create-project` 默认自动在用户浏览器中打开画布。保留它，并告诉用户画布已打开（使用 `canvas` URL 作为可点击的链接）。仅在没有任何用户界面浏览器时（CI、无头）传递 `--no-open`。

# 图像和本地资源

生成之前，仅清点用户附加的图像或为该目标选择的狭义相关本地资源。遵循 [SUPERDESIGN.md](references/SUPERDESIGN.md) **资源目的路由**：临时截图/参考进入画布参考节点；标志、字体和可重用的身份图像进入品牌资产；最终内容图像保留在项目内容中。使用返回的节点 ID 或品牌资产键与 `--reference-id` 一起传递，以便 `create`、`iterate` 和流程生成接收实际像素。当任何源组件或请求的设计具有标志位置时，强制执行 SUPERDESIGN.md 的 **Logo 不变**：必须有一个可用的适当品牌资产标志在显眼位置渲染，包括在可重用组件内；永远不要用首字母、表情符号、通用标记、虚构的 SVG 或纯文本代替。对于粘贴的直接公共图像 URL 或网站参考，阅读 [WEBSITE.md](references/WEBSITE.md)，并通过相同的上传流程仅实现选定的视觉。永远不要批量上传仓库，也永远不要将本地文件系统路径放入草稿 HTML 中。

# 生成后：提供进一步的机会

始终以简短、热情的后续跟进结束，提供进一步的机会（在所有表面上）。问一个带有 2 到 3 个具体选项的问题，这些选项针对您刚刚制作的内容，而不是一个通用列表。例如：尝试不同的英雄图像或关键视觉方向，尝试替代布局或构图，或生成一些更多变体或资产想法作为惊喜。只有在用户选择后才会生成，因为每次生成都会消耗积分。

（图形会得到一个专门的视觉自我审查，然后再进行此关闭 — [GRAPHIC.md](references/GRAPHIC.md) Step 5。UI 草稿由用户在画布上审查。）

# 工作原理

阅读 [SUPERDESIGN.md](references/SUPERDESIGN.md)，然后按照其说明操作。

对于图像或视频生成请求，阅读 [ASSET_GENERATION.md](references/ASSET_GENERATION.md)。加载上面链接的其他场景特定参考，当这些场景适用时。
