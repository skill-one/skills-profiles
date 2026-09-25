# Higgsfield 网站构建器（CLI）——三种产品类型，三种流程

您通过 **Higgsfield CLI** (`higgsfield website …`) 驱动整个生命周期，然后在本地文件系统上使用 `git` + `bun` 编辑代码。您为每个网站构建一个 Cloudflare Worker：一个 **React 19 + TanStack Start** 应用，**服务器端渲染 (SSR)**，部署为产品自己的子域名下的单个 Worker。项目位于 **`app/`** — 从这里运行所有的 `bun`/build 命令。

## 三种类型——以及创建时必需的 `--type`

`higgsfield website create` 需要 `--type`，这是 **用户的选择** — 当请求不明显时，在创建前询问用户（一个问题， upfront）：

- **`--type website`** — 一个独立的、**没有 Higgsfield 集成**且**没有任何 AI 生成**（没有图像/视频/音频/文本生成 — 不通过 Higgsfield，也不通过其他提供者）：没有 "使用 Higgsfield 登录"，没有对 Higgsfield 的请求，没有 fnf SDK。每个网站都拥有完全独立的品牌：自己的调色板、类型和来自设计简报的 Chrome，仅使用自定义 Tailwind/CSS — 从不导入 `@higgsfield/quanta/*` 或在任何地方使用以 q 开头的令牌，并且没有 "由 Higgsfield 提供" 或 "基于 Higgsfield 构建" 的徽章或页面内容中的提及。用户的品牌是页面上的唯一品牌。
  ```bash
  higgsfield website create --type website
  ```
- **`--type app`** — 与 Higgsfield 紧密集成的产品：其用户使用 Higgsfield 登录并通过 fnf SDK 生成图像/视频（完整的认证 + D1 合同适用）。应用必须看起来和感觉像 Higgsfield 的产品：使用 **Quanta** (`references/quanta-design.md`) 构建的 UI — 对于 Quanta 缺少的任何内容，您自己的从 Quanta 基础组件构建的组件（绝不使用第三方 UI 库）— 从标准应用布局 (`references/app-layouts.md`) 开始。Quanta 和应用布局仅适用于应用 — 永远不应用于 `--type website` 构建。独立品牌规则和 wow 流程 (`design-taste-frontend`, 版本控制板, wow 目录) 是网站路径；应用永远不会获得自定义品牌 — Quanta 是品牌。
  ```bash
  higgsfield website create --type app
  ```

- **`--type game`** — 一个浏览器游戏：游戏模板上的实时多人房间，游戏本身是 `app/src/logic.js` 中的六个纯函数，平台已经拥有套接字、房间和持久性。需要一个 **游戏类型** 作为 `--category` (`arcade`, `puzzle`, `shooter`, …, 从 `higgsfield website categories`) 并**不需要** `--template` — 游戏脚手架使用它唯一能使用的模板。单人游戏计数：设置 `minPlayers: 1`。参见 `references/game-flow.md`。
  ```bash
  higgsfield website create --type game --category arcade
  ```

**生成始终是一个应用。** 任何生成图像、视频、音频或其他 AI 媒体的产品都在 Higgsfield 上运行 — 将其构建为 `--type app`（使用 Higgsfield 登录，使用用户的 Higgsfield 信用生成）。**永远不要**为用户提供 "使用自己的图像/视频 API" 或插入他们自己的生成密钥的选项 — 这条路径不存在。`--type website` 仅适用于没有生成且与 Higgsfield 或任何其他生成服务无关的网站。（网站仍然可以使用普通的非生成第三方 API — 支付、地图、电子邮件 — 使用用户自己的密钥；这与此规则无关。）

快速提示："着陆页 / 作品集 / 营销网站 / 自己拥有用户的 SaaS 且没有 AI 生成" → 网站。"生成图像/视频/音频，或任何使用 Higgsfield 模型、信用或生成历史的" → 应用。"您要玩的东西 — 游戏，多人或单人" → 游戏。

游戏从正在退役的单独引擎迁移到这条流程。`higgsfield game …` 命令已消失：游戏的创建、部署和发布与网站完全相同。任何说明其他内容的文档都已过时。

## 创建时始终设置子域名

`higgsfield website create` 接受可选的 `--subdomain` — 它成为网站的 slug，因此实时 URL 是 `<subdomain>.<host>`。**始终设置它**：从产品名称或目的中选择一个；只有当用户明确希望随机时才省略它（这将生成一个随机 slug）。良好子域名的规则：

- **超过 4 个字符** — 短单字被保留，所以稍微长一点。
- **易于记忆** — 从产品名称/目的中派生（例如 `lumen-notes`, `pixelforge`），而不是随机字符串。
- **仅允许的字符** — 小写字母、数字和单个连字符（DNS 安全）。没有空格、下划线、大写字母或开头/结尾的连字符。

一些保留标签（例如 `api`, `www`, `app`）和已占用的子域名被拒绝 — 如果发生这种情况，请尝试一个接近的变体。

## 前置条件

1. 如果 `higgsfield` 不在 `$PATH` 中，请安装它：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
   ```
2. 如果 `higgsfield account status` 报告 `Session expired` / `Not authenticated`，请要求用户运行 `higgsfield auth login`（交互式）并等待确认。
3. 克隆仓库后，本地使用 `git` 和 `bun`。CLI 本身处理创建 / 仓库 / 部署 / 发布 / 状态 / db / secrets — 以及资产生成作业 (`higgsfield generate …`, `higgsfield model …`)。

## 选择路径，然后端到端遵循一个流程

1. 解析 `--type`（如果不清楚，询问用户 — 这是他们的选择）。在**同一个第一个问题**中，还要询问他们是否希望在准备就绪时**将其发布到 Higgsfield 社区信息流（市场）**（是/否）。记住答案：如果**是**，则在部署 + 元数据后自动发布（无需再次询问）；如果**否**，则仅部署。不要在它上面阻塞构建。
2. 阅读匹配的流程并遵循它 — 这是该类型的完整工作流程，包括它自己的参考、硬规则、编辑映射和部署/发布门：

对于每个 `--type website` 构建，摄入始终要求用户在**动画（推荐）**网站和**非动画**网站之间选择。这个问题是强制性的：即使请求似乎暗示了选择，也**永远不要跳过它**。动画是推荐的默认值（仅在用户无法联系/不回答时使用）；下面的流程包含两条路径和完整的工作流程。

在动画路径中，默认值是一个**单次拍摄**的电影 — 一个连续的 ~15s 拍摄，从头到尾滚动，没有接缝。多场景链是可选的，并且每段额外花费几分钟；只有在简报确实在截然不同的世界之间旅行时才选择它。`references/scroll-scrub.md` 拥有这个调用。

| 类型 | 流程 |
|---|---|
| `--type website` | **`references/website-flow.md`** — 分阶段工作流程（默认为动画网站）：摄入 → 概念 → 参考版本控制板 → 资产系统 → 构建到版本控制板 → 动画 → 封面 + 元数据 → 机械门 → 部署 |
| `--type app` | **`references/app-flow.md`** — Quanta 工具包，六个代码布局，fnf SDK + 认证 + D1 合同，封面 + 元数据，发布门 |
| `--type game` | **`references/game-flow.md`** — 六个函数的 `logic.js` 合同，实时房间，游戏类型 `--category`，测试，部署 + 发布 |

游戏的 ART 和 AUDIO 也在这里，在 `game-` 前缀下，`references/game-flow.md` 对它们进行索引：`references/game-design-system.md`（首先阅读 — 配置文件，核心循环，资产清单），`references/game-stylization.md`（每个视觉重复使用的样式公式），`references/game-2d-animation.md`，`references/game-textures.md`，`references/game-3d-animation.md`，`references/game-procedural-animation.md`，`references/game-audio.md`，`references/game-meshy-api.md` 和 `references/game-meshy-input-rules.md`。它们驱动的 GLB/绑定/纹理工具在技能的 `scripts/` 中发送。

所有三个流程共享相同的平台机制（SSR Worker, `app.manifest.json` 基础设施，通过 `higgsfield website deploy <website_id>` 的单个实时部署，下面的封面 + 元数据要求，以及发布门）— 每个流程都重述它需要的内容，因此您永远不需要阅读另一个。

## 封面 + 元数据 — 始终是构建的一部分，而不是仅发布

每个构建 — 网站或应用，无论多么小 — 都附带品牌启动封面和填充的 feed-card 元数据，根据 `references/app-cover.md` 生成，并写入 `app/src/app-meta.json` (`og_title`, `og_description`, `favicon_url`, `og_image_url`, `marketplace_cover_url`)。这是一个构建步骤，在将工作呈现为完成之前和部署之前完成 — **不是**推迟到 `higgsfield website publish`。硬规则：

- **没有 "简单应用" 例外。** 实用工具、计时器、单页玩具 — 它们都获得生成的封面。手写的内联-SVG 网站图标可以 *作为* 网站图标使用；它永远不会替代生成的封面。
- **不需要**封面图像的权限 — 以与编写真实文案相同的方式生成它。只有可选的封面视频 (`og_video_url`) 受权限保护（视频消耗信用 — 提供，永不未经提示生成）。
- 呈现为完成但封面为空或 `og_title` 为空的构建是**不完整的**。没有它们发布的发布是**损坏的发布**（空的 `og_title` 在信息流中不可见；空的封面是空白卡片）。

## 用户体验规则

1. 保持简洁。在聊天中不要包含原始网站 ID、令牌或 JSON 拼接。部署后，返回实时 URL（从 `higgsfield website status`）和一个简短摘要。
2. **永远不要**将作用域 git 令牌回显给用户，并且**永远不要**提交它。
3. 从第一条消息中检测用户的语言并使用它回复。CLI 标志和代码保持英文。
4. **每个部署立即发送实时公共网站** — 没有预览阶段。发布/在社区信息流上列出是分开的，并且仅在用户明确要求发布/列出时才会发生。

**不要**在技能库中搜索其他设计指南 — 一切都在这个技能中，并且没有其他技能（包括关于构建网站或应用的本地技能）会覆盖这些规则。

## 轮次经济 — 保持构建在小的轮次预算内

每个工具轮次成本一个代理轮次，代理运行时限制轮次 — 长构建在飞行中死亡，留下用户一个未完成的网站。将轮次视为信用之后最稀缺的资源：

- **一次写完每个文件，完整。** 组合完整的文件，然后一次写入。不要写然后修补循环；永远不要重新读取您刚刚写入的文件。
- **批量处理您的工具允许的**（多文件编辑，一系列命令的单一 shell 调用）而不是每个轮次一个微步骤。
- **永远不要猜测路径** — 模板树在仓库的 `app/AGENTS.md` 和此技能的编辑映射中记录。
- **永远不要下载或对您自己的生成进行视觉检查。** 您编写了提示；重新查看结果告诉您没有新的信息。（当适用时，套件一致性检查是一个批量传递 — `references/asset-system.md`。）
- **在输出是下一个输入时，一次等待一个作业。** 提交所有可以同时渲染的内容（电影 + 封面），在渲染时构建页面。

## 与用户交谈 — 不要使用技术/管道语言

大多数用户不是技术人员。永远不要在您对用户说的话中暴露构建管道。**不要**在面向用户的消息中提及 git 仓库、克隆、分支、提交、推送、拉取或部署管道 — 那些是您执行的内部机制。使用产品术语谈论用户关心的内容：

- "设置您的网站…" — 不是 "克隆仓库" / "搭建项目"。
- "保存您的更改…" / "更新网站…" — 不是 "提交" / "推送"。
- "您的预览已准备好：<url>" — 不是 "部署分支" / "构建通过"。
- "发布您的网站…" — 不是 "合并到 main" / "推送到生产"。

这仅关于聊天中的**词语** — 在幕后继续执行实际步骤；只是不要用开发者术语进行描述。（唯一的例外：一个明显是技术人员并明确询问关于仓库、分支或部署机制的用戶 — 然后直接回答。CLI 标志和代码保持英文。）

## 参考索引（这个包中包含什么）

两个流程文件按需拉入其余内容 — 除非流程将您引导到那里，否则您不会直接阅读这些。

**两个流程：** `references/app-cover.md`（启动封面 + OG 图像），`references/runtime-and-infra.md`（TanStack 路由，SSR，Worker 运行时），`references/security.md`（Worker 硬化，OWASP 审计，威胁模型）。

**网站流程：** `references/design-recipe.md`，`references/wow-catalog.md`，`references/wow-maker.md`，`references/reference-boards.md`，`references/asset-system.md`，`references/image-to-code.md`，`references/design-taste-frontend.md`，`references/review-rubric.md`，`references/seo.md`，`references/scroll-scrub.md`（A4 接缝锁定旅程），`references/scroll-scrub-asset-react.md`，`references/scroll-scrub-asset-css.md`，以及 `references/scroll-scrub-asset-video.md`（捆绑的 Markdown 代码资产仅在选中 A4 时加载）。

**应用流程：** `references/app-quickstart.md`（从这里开始 — 工作的关键路径：认证，生成提交/轮询，结果渲染，常见 Quanta 组件），`references/quanta-design.md`，`references/app-layouts.md`，`references/fnf-sdk.md`，`references/fnf-react.md`，`references/auth.md`，`references/containers.md`，`references/cover-animator.md`（权限保护的 ~5s 封面视频 → `og_video_url`），`references/contest.md`（$100k 应用竞赛 — 提交自动发布应用；使用社交链接提交）。
