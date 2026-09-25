# Higgsfield 网站构建器（CLI） — 三种产品类型，三种流程

通过 **Higgsfield CLI**（`higgsfield website …`）驱动整个生命周期，然后在本地文件系统中使用 `git` + `bun` 编辑代码。你为每个网站构建一个 **Cloudflare Worker**：一个 **React 19 + TanStack Start** 应用，**服务端渲染（SSR）**，以产品自身子域名的单个 Worker 进行部署。项目位于 **`app/`** — 从该目录运行所有 `bun`/构建命令。

## 三种类型 — 以及创建时必需的 `--type`

`higgsfield website create` 需要 `--type`，且是**用户的选择** — 当请求无法显而易见地判断时，在创建之前询问用户（一次问题，前置：）：

- **`--type website`** — 独立的、**无 Higgsfield 集成**，且**无任何 AI 生成**的产品（无图像/视频/音频/文本生成 — 既不是通过 Higgsfield，也不是通过其他提供方）：无 "使用 Higgsfield 登录"，无对 Higgsfield 的请求，无 fnf SDK。每个网站都获得完全独立、自主的品牌：根据设计简报拥有自有调色板、字体和界面外观，仅自定义 Tailwind/CSS — 永远不要导入 `@higgsfield/quanta/*` 或使用任何 q 前缀的令牌，也不要在页面内容中出现 "由 Higgsfield 提供支持 / 基于 Higgsfield 构建" 徽章或提及。页面上的品牌只有用户自有的品牌。
  ```bash
  higgsfield website create --type website
  ```
- **`--type app`** — 与 Higgsfield 紧密集成的产品：其用户通过 Higgsfield 登录，并通过 fnf SDK 生成图像/视频。完整的认证 + D1 契约适用。应用必须看起来并感觉就像 Higgsfield 产品：使用 **Quanta**（`references/quanta-design.md`）构建 UI — 对于 Quanta 不具备的任何内容，从 Quanta 原语构建你自己的组件（永远不使用第三方 UI 库）— 从标准应用布局（`references/app-layouts.md`）开始。Quanta 和应用布局仅应用于 app — 永远不应用于 `--type website` 构建。独立品牌规则和 wow 流水线（`design-taste-frontend`、看板、wow 目录）是网站路径；应用从不获得自定义品牌 — Quanta 就是品牌。
  ```bash
  higgsfield website create --type app
  ```

- **`--type game`** — 浏览器游戏：游戏模板上的实时多人房间，游戏本身是 `app/src/logic.js` 中的六个纯函数，平台已拥有套接字、房间和持久化。需要以 `--category` 形式提供**游戏类型**（`arcade`、`puzzle`、`shooter`、…，来自 `higgsfield website categories`），且**不接受** `--template` — 游戏从唯一能使用的模板中脚手架化。单人算数：设置 `minPlayers: 1`。参见 `references/game-flow.md`。
  ```bash
  higgsfield website create --type game --category arcade
  ```

**生成始终属于 app。** 任何生成图像、视频、音频或其他 AI 媒体的产品都在 Higgsfield 上运行 — 将其构建为 `--type app`（使用 Higgsfield 登录，在用户的 Higgsfield 额度上生成）。永远不要向用户提供一个 "自带图像/视频 API" 或插入自己的生成密钥的选项来为网站 — 那条路径不存在。`--type website` **仅用于没有生成、也与 Higgsfield 或任何其他生成服务无关的网站**。（网站仍可使用普通非生成第三方 API — 支付、地图、邮件 — 使用用户自己的密钥；这与该规则无关。）

快速判断： "落地页 / 作品集 / 营销网站 / 拥有自己用户且无 AI 生成的 SaaS" → website。"生成图像/视频/音频，或与 Higgsfield 模型、额度或生成历史相关的任何内容" → app。"可以玩的东西 — 游戏、多人或单人" → game。

游戏是从一个正在退役的独立引擎迁移到此流水线的。`higgsfield game …` 命令已不存在：游戏与网站一样，通过创建、部署和发布来完成。任何说其他内容的文档已过时。

## 创建时始终设置子域

`higgsfield website create` 接受可选的 `--subdomain` — 它成为网站的 slug，因此实时 URL 是 `<subdomain>.<host>`。**始终设置它**：从产品名称或用途中挑选一个；只有用户明确想要随机 slug 时才省略它（结果得到随机 slug）。优秀子域名的规则：

- **超过 4 个字符** — 短单个单词已被保留，因此要长一些。
- **易记** — 从产品名称/用途推导（例如 `lumen-notes`、`pixelforge`），而非随机字符串。
- **仅允许的字符** — 小写字母、数字和单个连字符（DNS 安全）。无空格、下划线、大写或开头/结尾的连字符。

几个保留标签（如 `api`、`www`、`app`）以及已被占用的子域会被拒绝 — 如果发生这种情况，尝试一个接近的变体。

## 先决条件

1. 如果 `higgsfield` 不在 `$PATH` 中，则安装它：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
   ```
2. 如果 `higgsfield account status` 报告 `Session expired` / `Not authenticated`，请让用户运行 `higgsfield auth login`（交互式）并等待确认。
3. 克隆仓库后，本地使用 `git` 和 `bun`。CLI 本身处理创建 / 仓库 / 部署 / 发布 / 状态 / 数据库 / 密钥 — 以及资源生成任务（`higgsfield generate …`、`higgsfield model …`）。

## 选择路径，然后端到端遵循一条流程

1. 解析 `--type`（若不清楚，则询问用户 — 这是他们的选择）。在**同一第一个问题**中，也询问他们准备好后是否要将其**发布到 Higgsfield 社区信息流（市场）**（是/否）。记住答案：如果是，则在部署 + 元数据之后自动发布，无需再次询问；如果否，仅部署。不要将构建阻塞在此问题上。
2. 阅读匹配的流程并遵循它 — 它是该类型的完整工作流，包括其自身的引用、硬性规则、编辑映射和部署/发布关卡：

对于每个 `--type website` 构建，**获取始终**会询问用户选择**动画（推荐）**网站 — 通过生成电影滚动驱动的旅程（`references/scroll-scrub.md`）— 和**非动画**网站。该问题为强制要求：永远不要跳过，即使请求似乎暗示有选择。动画是推荐默认值（仅在用户无法到达/不回答时使用）；以下流程包含两条路径和完整流水线。

在动画路径中，默认是**单次拍摄**电影 — 一次连续的 ~15 秒拍摄，端到端擦洗，无缝。多场景链为可选，且每条段需要几分钟额外时间；仅在简报确实在不同世界之间过渡时采用。`references/scroll-scrub.md` 拥有该调用。

| Type | Flow |
|---|---|
| `--type website` | **`references/website-flow.md`** — 分阶段流水线（默认动画网站）：获取 → 概念 → 参考看板 → 资源系统 → 构建到看板 → 动态 → 封面 + 元数据 → 机械关卡 → 部署 |
| `--type app` | **`references/app-flow.md`** — Quanta 工具包、六个代码布局、fnf SDK + 认证 + D1 契约、发布封面 + 元数据、发布关卡 |
| `--type game` | **`references/game-flow.md`** — 六个函数的 `logic.js` 契约、实时房间、游戏类型 `--category`、试玩、部署 + 发布 |

游戏的**艺术**和**音频**也在此处，在 `game-` 前缀下，且 `references/game-flow.md` 对其进行了索引：`references/game-design-system.md`（首先阅读 — 个人资料、核心循环、资源清单），`references/game-stylization.md`（每个视觉重复使用的 STYLE 公式），`references/game-2d-animation.md`，`references/game-textures.md`，`references/game-3d-animation.md`，`references/game-procedural-animation.md`，`references/game-audio.md`，`references/game-meshy-api.md` 和 `references/game-meshy-input-rules.md`。它们驱动的 GLB/骨骼绑定/纹理工具在 skill 的 `scripts/` 中提供。

所有三种流程共享相同的基础设施机制（SSR Worker、`app.manifest.json` 基础架构、通过 `higgsfield website deploy <website_id>` 进行单个实时部署、封面 + 元数据要求以及发布关卡）— 每个流程都会重述其所需内容，因此你无需再读另一个。

## 封面 + 元数据 — 始终是构建的一部分，而非仅发布用

每个构建 — 网站或应用，无论多小 — 都附带带有品牌标识的发布封面和填写的信息流卡片元数据，按照 `references/app-cover.md` 生成，并写入 `app/src/app-meta.json`（`og_title`、`og_description`、`favicon_url`、`og_image_url`、`marketplace_cover_url`）。这是**构建步骤**，在作品以完成状态呈现之前、在将其部署并发布之前完成 — 并非推迟到 `higgsfield website publish`。硬性规则：

- **无 "简单应用" 例外。** 实用工具、计时器、单页玩具 — 它们都获得生成的封面。手动编写的行内 SVG favicon 作为 favicon 没问题；它绝不能替代生成的封面。
- **封面图片无需权限** — 以与编写真实文案相同的方式生成它。仅**可选的封面视频**（`og_video_url`）受权限限制（视频需要额度 — 提供，永远不要未提示生成）。
- 以未完成呈现、封面为空或 `og_title` 为空的构建是**不完整**的。没有这些内容就发布是**损坏的发布**（空的 `og_title` 在信息流上不可见；空的封面是空白卡片）。

## UX 规则

1. 简洁。不要在聊天中暴露原始网站 ID、令牌或 JSON 转储。部署后，返回来自 `higgsfield website status` 的实时 URL 和一行摘要。
2. 永远不将作用域的 git 令牌回显给用户，也永远不提交它。
3. 从第一条消息检测用户的语言，并以其语言回复。CLI 标志和代码保持英文。
4. **每次部署都立即交付在线公开网站** — 没有预览阶段。在社区信息流上的发布/列表是独立的，仅当用户明确要求发布/列表时才发生。

不要搜索 skill 库中的其他设计指导 — 一切都在本 skill 内，没有其他 skill（包括关于构建网站或应用的用户/本地 skill）会覆盖这些规则。

## 轮次经济 — 将构建保持在较小的轮次预算内

每次工具往返都消耗一个 agent 轮次，且 agent 运行时限制轮次 — 长构建在中途死亡，给用户留下未完成网站。将轮次视为除额度之外最稀缺的资源：

- **每个文件只写一次，写完整。** 编写完整文件，然后一次写入。不要写后修补的循环；永远不重新读取刚写过的文件。
- **批量你的工具允许的操作**（多文件编辑、一系列命令的一次 shell 调用）而非每次一个微小步骤。
- **永远不猜测路径** — 模板树在仓库的 `app/AGENTS.md` 和本 skill 的编辑映射中文档化。
- **永远不要下载或视觉检查你自己的生成内容。** 你编写了提示；重新查看结果不会告诉你任何新内容。（当适用时，套件一致性检查为一次批量处理 — `references/asset-system.md`。）
- **当输出是下一个输入时，等待作业仅一次。** 提交所有可以并发渲染的内容（电影 + 封面），在渲染期间构建页面。

## 与用户沟通 — 不使用技术/管道语言

大多数用户并非技术人员。永远不要在向你所说的内容中暴露构建管道。不要提及 git 仓库、克隆、分支、提交、推送、拉取或部署管道 — 这些是你刚刚执行的内部机制。用用户关心的产品术语说话：

- "正在设置你的网站…" — 而非 "克隆仓库" / "脚手架项目"。
- "保存你的更改…" / "更新网站…" — 而非 "提交" / "推送"。
- "你的预览已就绪：<url>" — 而非 "部署了分支" / "构建通过"。
- "正在发布你的网站…" — 而非 "合并到 main" / "推送到生产"。

这是仅关于聊天中的**词语** — 保持后台的真实步骤不变；只是不要以开发者术语叙述它们。（唯一例外：如果用户明显是技术性且明确询问仓库、分支或部署机制 — 则直接回答。CLI 标志和代码保持英文。）

## 参考索引（本包中的内容）

两个流程文件按需引入其余部分 — 除非流程发送你去那里，否则你无需直接阅读这些文件。

**两个流程共用：** `references/app-cover.md`（发布封面 + OG 图片），`references/runtime-and-infra.md`（TanStack 路由、SSR、Worker 运行时），`references/security.md`（Worker 加固、OWASP 审计、威胁模型）。

**网站流程：** `references/design-recipe.md`，`references/wow-catalog.md`，`references/wow-maker.md`，`references/reference-boards.md`，`references/asset-system.md`，`references/image-to-code.md`，`references/design-taste-frontend.md`，`references/review-rubric.md`，`references/seo.md`，`references/scroll-scrub.md`（A4 无缝旅程），`references/scroll-scrub-asset-react.md`，`references/scroll-scrub-asset-css.md`，`references/scroll-scrub-asset-video.md`（A4 选定时加载的捆绑 Markdown 代码资产）。

**应用流程：** `references/app-quickstart.md`（从这里开始 — 工作的关键路径：认证、生成提交/轮询、结果渲染、常见 Quanta 组件），`references/quanta-design.md`，`references/app-layouts.md`，`references/fnf-sdk.md`，`references/fnf-react.md`，`references/auth.md`，`references/containers.md`，`references/cover-animator.md`（权限受限的 ~5 秒封面视频 → `og_video_url`），`references/contest.md`（10 万美元应用大赛 — 条目自动发布应用；随附社交链接提交）。
