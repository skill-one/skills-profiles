> **首先，保持此技能新鲜——在运行前与用户确认：** `npx hyperframes skills update motion-graphics`。当所有内容均为最新时，此操作是快速的空操作；否则，它会在您依赖该技能之前，刷新此技能及其依赖的核心领域技能。

> **figma 源**：如果用于构建的 Logo/资源/动画来自 figma.com 的 URL，请先运行 `/figma`——执行资源导出、品牌令牌，以及若图形为 Figma Motion 导入则进行 Motion→GSAP 转换——然后基于其输出进行构建。不要直接通过原始 MCP 工具驱动 Figma：那会跳过 SVG 消毒、`.media/manifest.jsonl` 来源信息，以及品牌令牌的 `var()` 绑定，因此稍后的品牌变更无法在不重新完整导入的情况下传播。

# motion-graphics — 分发入口

> **入口是 `/hyperframes`。** 此技能制作一种**简短、以设计为主导的无旁白动态图形**（动作为信息；约 10 秒以内，无旁白）。任何更长、带叙述，或多个场景的——或任何不确定的情况 → 先阅读 `/hyperframes`：意图层拥有所有路由决策。

此工作流**按设计实现自主性**——最多只向用户提出一个澄清性问题（`agents/director.md`），然后通过验证进行构建，无需中间审核。意图层（`/hyperframes` → `references/intent-interview.md`）无需运行形态问题直接路由至此处；分镜图和配套会话对如此短的片段贡献甚微。渲染仍然由用户控制：在检查和证明快照通过后，从 `../hyperframes/references/brief-contract.md` 询问标准问题"先预览，还是渲染？"。当存在 `BRIEF.md` 时，在导演提问之前阅读它。

**简短、以设计为主导的动态图形。** **以资源优先**：在设计镜头之前决定资源策略并获取真实素材——在此之前，然后围绕现有素材设计镜头，然后通过复用目录能力进行构图。所有产物存放于 `PROJECT_DIR = videos/<project-name>/`（在步骤 0 中创建）；以下所有路径均相对于该目录。

| 阶段    | 执行方式                                                             | 主要产物                                                 | 详细流程                 |
| -------- | --------------------------------------------------------------------- | --------------------------------------------------------- | ------------------------- |
| init     | Bash                                                                  | `hyperframes.json`                                         | 步骤 0                    |
| plan     | subagent — **决定是否需搜索？** + 分类 + 资源策略                   | `shot-plan.json`（草稿：类别、`asset_needs` 查询、简报） | `agents/director.md`（Part 1） |
| source ◇ | Bash — media-use 解析（**当 `asset_needs` 为空时跳过**）              | `assets/` + `assets/index.md`                             | `phases/source/guide.md` |
| design   | subagent — 围绕已解析资源设计镜头                                     | `shot-plan.json`（最终：区块（s）+ 布局 + 动效 + 位置） | `agents/director.md`（Part 2） |
| build    | subagent — 重用优先的构图                                             | `compositions/index.html`                                  | `agents/builder.md`       |
| verify   | Bash — `lint`、`check`、证明快照；失败时修复                        | `snapshots/contact-sheet.jpg`                              | 步骤 5                    |
| approve  | 询问预览或渲染；等待回答                                             | 明确的渲染批准                                             | 步骤 6                    |
| render   | Bash — `hyperframes render`（MP4，或 `--format webm/mov` 用于叠加层） | `renders/video.mp4` 或透明叠加层                            | 步骤 6                    |

`◇ source` 仅在所选类别声明了资源时运行。纯代码/文本类别（如 `kinetic-type`，大多数 `charts`/`stat`）的 `asset_needs: []`，直接从计划跳至设计。

## 类别 — 按搜索决策划分

`plan` 的**第一个决策是：此项目是否需要搜索？** 该分支将类别划分为两组；然后，具体的类别由此选择——对于搜索驱动的类别，**根据搜索返回的内容类型**进行选择。每个类别对应一个 `categories/<id>/module.md`（其规划 + 构建规则）；共享的动词语境位于 `references/motion-vocabulary.md`（→ `hyperframes-animation` 规则/蓝图 + 注册表区块）。

**表单类别 — 无需搜索；用户提供内容：**

| 类别         | 意图                                                                 | 依赖                                           |
| ------------ | --------------------------------------------------------------------- | ---------------------------------------------- |
| `kinetic-type` | 强有力的标语 / 引言 / 标题，以动作为先的文本                             | `caption-*` 区块 + 动画规则                     |
| `stat`       | 单个英雄数字 / 计数动画 + 圆环                                           | `apple-money-count` / `rules/{counting-dynamic-scale, stat-bars-and-fills}` |
| `charts`     | 从数据获取的柱状图 / 折线图 / 饼图 / 比赛 / 百分比                       | `data-chart` 区块                                |
| `logo-reveal` | Logo 闪现 / 品牌组合（用户 Logo）                                       | `logo-outro` / `rules/svg-path-draw`            |
| `lower-thirds` | 名称 / 标题栏、标注、社交叠加层                                           | `caption-*` + 注册表叠加区块                       |
| `maps`       | 地理动态——高亮区域、连接地点、缩放至位置（矢量车道，或烘焙底图车道）   | `us-map` / `world-map` 系列 + `bake-basemap.mjs` |

**搜索驱动的类别 — 先搜索，然后按内容类型动画**（RWA 路径）：

| 返回内容   | 类别         | 动画                                                 |
| ---------- | ------------ | ---------------------------------------------------- |
| webpage / link | `webpage` | webpage / UI 动画（滚动、显现、光标、标注）         |
| news article | `news`     | 标题显现 + 来源卡片 + 关键事实标注                   |
| tweet      | `tweet`     | 动画推文卡片                                         |
| image / entity | `asset-fusion` | 资源的几何**转化为**图表（RWA 同构融合） |

构建顺序：逐个进行，覆盖优先（粗略即可）。`kinetic-type` 从原型移植而来；其余类别依次推进。

## 前提条件

macOS Apple Silicon 或 Linux x64。系统工具：`brew install node ffmpeg`。`npx hyperframes doctor` 一次。macOS GPU 渲染：`export PRODUCER_BROWSER_GPU_MODE=hardware`。

可选密钥（未设置时使用本地回退）——仅由通过 media-use 获取/生成资源的类别需要：

| 密钥                                 | 用途                                       | 回退                              |
| ------------------------------------- | ------------------------------------------ | --------------------------------- |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | 图像生成（media-use resolve）             | 跳过生成 / 仅搜索                 |
| (asset_scout / search providers)     | `webpage`/`news`/`tweet` + `asset-fusion` 真实资源搜索 | 类别降级为无资源   |

## 流程

### 步骤 0 — 初始化

cwd 是代理工作区根目录；所有产物存放于 `PROJECT_DIR = videos/<project-name>/` 之下。`<project-name>`：使用用户给定的目录，否则从意图中取一个简短的 kebab-case 名称（`<subject>-motion`）。不是工作区基名或时间戳。

仅在 `$PROJECT_DIR/hyperframes.json` 不存在时：

```bash
PROJECT_DIR="${MOTION_GRAPHICS_DIR:-videos/<project-name>"}
mkdir -p "$(dirname "$PROJECT_DIR")"
npx hyperframes init "$PROJECT_DIR" --non-interactive --example=blank --skill=motion-graphics
```

`init` 将已安装的技能与 GitHub 上的最新版本进行比较，如果有任何技能过期，则更新全局集。

**约束：** 不要在 workspace 根目录执行 `hyperframes init`；不要在工作目录内嵌套另一个 `hyperframes/`；每个 Bash 命令（主代理 + 子代理）都是一个 `(cd "$PROJECT_DIR" && ...)` 子 shell——切勿使用裸 `cd`。

### 步骤 1 — Plan（子代理：导演 Part 1）

派遣一个子代理。prompt = 完整的 `agents/director.md` + `## Dispatch context`（`SKILL_DIR` / `PROJECT_DIR` / 用户请求 / `Schema: <SKILL_DIR>/references/shot-plan-ir.md`）。它必须：

1. **决策：此项目是否需要搜索？**（第一个分支）
   - **否** → 选择一个**表单类别**（kinetic-type / stat / charts / logo-reveal / lower-thirds）；内容由用户提供；`asset_needs: []`。
   - **是** → 在 `asset_needs[]` 中发出一个**搜索计划**（news / web / tweet / image；两极查询）。具体的**搜索驱动类别**（webpage / news / tweet / asset-fusion）由步骤 2 返回的内容类型确认，并在步骤 3 中定稿。
2. 编写一份草稿 `shot-plan.json`（信封 + 所选表单类别**或**搜索意图 + `asset_needs` + 一段镜头简报）。Schema: `references/shot-plan-ir.md`。

验证：`[ -s "$PROJECT_DIR/shot-plan.json" ] && echo ok || echo missing`。

### 步骤 2 — Source ◇（Bash：media-use，条件执行）

如果 `shot-plan.json.asset_needs` 非空，则解析资源（搜索 / 生成 / 获取 → 冻结的项目本地路径 + 台账）。参见 `phases/source/guide.md`（封装 `media-use resolve`；搜索驱动的类别使用 news/web/tweet/image 搜索）。如果 `asset_needs` 为空，**跳至步骤 3**。

```bash
# illustrative — 参见 phases/source/guide.md
(cd "$PROJECT_DIR" && node <SKILL_DIR>/phases/source/resolve.mjs --plan ./shot-plan.json --out ./assets)
```

优雅降级：如果搜索/提供者不可用，类别回退为无资源（在 `context.log` 中注明）。

### 步骤 3 — Design（子代理：导演 Part 2）

派遣一个子代理（prompt = `agents/director.md` Part 2 + 分派上下文，包括如果步骤 2 运行则已解析的 `assets/index.md` + `catalog-map.md`）。围绕可用资源**设计镜头**：选择目录区块 + `hyperframes-animation` 规则/蓝图、布局、动效、节拍，以及（对于 `asset-fusion`）`element_positions` + 吸管调色板。定稿 `shot-plan.json`（`content.block` + `content.customize` + 各类别内容）。

### 步骤 4 — Build（子代理：Builder，重用优先）

派遣一个子代理。prompt = 完整的 `agents/builder.md` + 分派上下文（`shot-plan.json`、`catalog-map.md`、该类别的 `module.md`、`references/motion-vocabulary.md`、`references/builder-contract.md`）。**重用优先**：`npx hyperframes add <block>` + 原地定制；仅在缺失部分 + asset-fusion 功能上手工编写。输出 `compositions/index.html`，符合 HF 契约（在 `window.__timelines` 上暂停的 GSAP 时间轴，`class="clip"` + 稳定 id，`tl.seek(0)`，确定性）。

### 步骤 5 — Verify（Bash → 失败时派遣修复子代理）

```bash
(cd "$PROJECT_DIR" && npx hyperframes lint .)
(cd "$PROJECT_DIR" && npx hyperframes check .)
(cd "$PROJECT_DIR" && npx hyperframes snapshot --at <proof-times>)
```

选择证明时间，以展示开屏状态、标志性动作和最终停留。继续之前检查生成的联系表或快照表。在 `lint`、`check` 或快照失败时，派遣修复子代理（`agents/finalize.md`）进行一次原地修复轮次，然后重新运行失败的门控。切勿仅为掩盖缺陷而改变固定时长。

### 步骤 6 — 批准与渲染（Bash）

询问一个问题："先预览，还是渲染？" 如果用户选择预览，打开 Studio 并在修订后回到同一批准门控：

```bash
(cd "$PROJECT_DIR" && npx hyperframes preview --background)
```

仅在收到明确的渲染回答后渲染：

```bash
(cd "$PROJECT_DIR" && npx hyperframes render . --skill=motion-graphics -q high -o ./renders/video.mp4)
# 透明叠加层变体：--format webm  (或 mov)
```

验证输出存在、非空，并具有预期的时长。最终交付说明所述产物、实际时长、构图或帧 id、证明时间，以及检查过的联系表或快照表。标志位于 `/hyperframes-cli` → `references/preview-render.md`。

## 恢复表

| 状态                                                    | 从……继续              |
| -------------------------------------------------------- | -------------------------- |
| 无 `shot-plan.json`                                      | 步骤 1（规划）              |
| `shot-plan.json` 有 `asset_needs`，无 `assets/`         | 步骤 2（来源）            |
| `shot-plan.json` 已定稿，无 `compositions/index.html`     | 步骤 3/4（设计+构建）      |
| `compositions/index.html` 存在，无证明快照              | 步骤 5（验证）            |
| 检查与证明快照通过，无批准的渲染                        | 步骤 6（批准）            |
| 已批准的渲染存在                                           | 验证输出，然后报告         |

## 设计说明（维护者——执行无需阅读此部分）

- **资产优先的合理性**：获取资源是前置步骤，并指导镜头设计（RWA 流程：分析 → 搜索 → 审查 → 构图）。搜索驱动的类别（`webpage`/`news`/`tweet`）和 `asset-fusion` 都依赖 media-use 搜索（news/web/tweet/image），这是 media-use 文档记录的 RWA 谱系。
- **重用优先**：生态系统内 LLM 生成模板的对应物是"组合目录区块 + `hyperframes-animation` 规则"。HF 暂停的 GSAP 时间轴 ≙ Remotion 的 `useCurrentFrame`。
- **类别模块契约**：一个 `categories/<id>/module.md`（规划 + 构建），共享 `references/motion-vocabulary.md`（+ 可选评估）。添加类别 = 删除该文件夹 + 在 `agents/director.md` 中注册其分类器行 + 在 `catalog-map.md` 中添加其行；阶段流程不受影响。
- **目录结构：**
  ```
  videos/<project-name>/
    hyperframes.json  context.log
    shot-plan.json            # the IR (Director 输出)
    assets/  assets/index.md  # media-use 输出（如有来源资源）
    compositions/index.html   # Builder 输出
    renders/video.mp4
  ```
- **注册**：在 `hyperframes` 路由器——添加"以设计为主导的短动态图形"意图 + 工作流描述；从 `/general-video` 中划出 motion-graphics 触发器；添加反向 Do-NOT-use 边。参见 `motion-graphics-genre.md` §5-7。
