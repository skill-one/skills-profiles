> **首先，保持这项技能的时效性——在运行前与用户确认：** `npx hyperframes skills update motion-graphics`。当一切都是最新时，这是一个快速的无操作；否则，在依赖它们之前，将刷新这项技能及其依赖的核心领域技能。

> **figma 源文件**：如果构建的标志/资源/动画来自 figma.com URL，请先运行 `/figma` — 资源导出、品牌标记，以及如果图形是 Figma Motion 导入，则 Motion→GSAP 翻译 — 然后从其输出构建。不要通过原始 MCP 工具直接驱动 Figma：那样会跳过 SVG 清理、`.media/manifest.jsonl` 起源，以及品牌标记 `var()` 绑定，因此，稍后的品牌更改无法在不完全重新导入的情况下传播。

# motion-graphics — 分发入口

> **正门是 `/hyperframes`。** 这项技能制作一个 **短、以设计为导向、无旁白的动态图形**（动态是信息；~10秒以内，无旁白）。任何更长的、有旁白的或多场景的 — 或任何不确定性 → 首先阅读 `/hyperframes`：意图层拥有每条路线的决策权。

这个工作流程是 **按设计自主运行的** — 最多一个问题 (`agents/director.md`) 进行澄清，然后通过验证进行构建，无需中间审查。意图层 (`/hyperframes` → `references/intent-interview.md`) 直接路由到这里，无需运行形状问题；故事板和配套会议对这个如此短的片段贡献不大。渲染仍然是用户控制的：在检查和预览快照通过后，从 `../hyperframes/references/brief-contract.md` 中询问标准的“先预览还是渲染？”问题。当存在 `BRIEF.md` 时，在导演的问题之前阅读它。

一个短的设计导向动态图形。**资产优先**：在设计镜头之前决定资产策略并获取真实材料，然后围绕已有的内容设计镜头，然后通过重用目录功能进行编排。所有工件都存放在 `PROJECT_DIR = videos/<project-name>/`（在步骤 0 中创建）；所有以下路径都是相对于它的。

| 阶段    | 执行                                                         | 主要工件                                           | 详细流程                 |
| ------- | ------------------------------------------------------------ | -------------------------------------------------- | ----------------------- |
| init    | Bash                                                          | `hyperframes.json`                                | 步骤 0                  |
| plan    | subagent — **决定是否搜索？** + 分类 + 资产策略             | `shot-plan.json` (草稿：类别、`asset_needs` 查询、简介) | `agents/director.md` (第一部分) |
| source ◇ | Bash — 媒体使用解析 (**如果 `asset_needs` 为空则跳过**)     | `assets/` + `assets/index.md`                     | `phases/source/guide.md` |
| design  | subagent — 围绕解析的资产进行镜头设计                         | `shot-plan.json` (最终：块 + 布局 + 动态 + 位置)     | `agents/director.md` (第二部分) |
| build   | subagent — 重用优先的编排                                     | `compositions/index.html`                          | `agents/builder.md`      |
| verify  | Bash — `lint`、`check`、预览快照；失败时修复                 | `snapshots/contact-sheet.jpg`                      | 步骤 5                  |
| approve | 提问预览还是渲染；等待答案                                  | 明确的渲染批准                                       | 步骤 6                  |
| render  | Bash — `hyperframes render` (MP4，或 `--format webm/mov` 用于叠加) | `renders/video.mp4` 或透明叠加                     | 步骤 6                  |

`◇ source` 仅在所选类别声明资产时运行。纯代码/文本类别（例如 `kinetic-type`、大多数 `charts`/`stat`）有 `asset_needs: []` 并直接从计划跳转到设计。

## 类别 — 根据搜索决定进行划分

`plan` 的 **第一个决定是：是否需要搜索？** 这个分支将类别分为两组；然后选择具体的类别 — 对于搜索驱动的，**由搜索返回的内容类型决定**。每个类别是一个 `categories/<id>/module.md`（其规划 + 构建规则）；共享的动态词汇表位于 `references/motion-vocabulary.md`（→ `hyperframes-animation` 规则/蓝图 + 注册块）。

**形式类别 — 无需搜索；用户提供内容：**

| 类别       | 意图                                                                                                         | 倾向于                                                                    |
| ---------- | ------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| `kinetic-type` | 断言的行 / 引语 / 标题，动态优先文本                                                                 | `caption-*` 块 + 动画规则                                                |
| `stat`      | 单个英雄数字 / 计数器 + 环                                                                                   | `apple-money-count` / `rules/{counting-dynamic-scale, stat-bars-and-fills}` |
| `charts`    | 条形图 / 线形图 / 饼图 / 比赛 / 来自数据的百分比                                                                   | `data-chart` 块                                                          |
| `logo-reveal` | 标志刺激 / 品牌锁定（用户标志）                                                                               | `logo-outro` / `rules/svg-path-draw`                                      |
| `lower-thirds` | 名称 / 标题条，注释，社交覆盖层                                                                               | `caption-*` + 注册覆盖块                                                  |
| `maps`      | 地理动态 — 突出显示区域，连接地点，缩放到位置（矢量车道，或烘焙的底图车道）                                           | `us-map` / `world-map` 系列 + `bake-basemap.mjs`                          |

**搜索驱动类别 — 先搜索，然后根据内容类型进行动画**（RWA 路径）：

| 返回内容   | 类别       | 动画                                                      |
| ---------- | ---------- | ---------------------------------------------------------- |
| 网页 / 链接 | `webpage`  | 网页 / UI 动画（滚动、揭示、光标、注释）                      |
| 新闻文章   | `news`     | 标题揭示 + 来源卡片 + 关键事实注释                          |
| 推文       | `tweet`    | 动态推文卡片                                                |
| 图像 / 实体 | `asset-fusion` | 资产的几何形状 _成为_ 图表（RWA 象征性融合）                 |

构建顺序：一次一个，覆盖优先（粗糙即可）。`kinetic-type` 从原型移植；其余的按顺序进行。

## 前置条件

macOS Apple Silicon 或 Linux x64。系统工具：`brew install node ffmpeg`。`npx hyperframes doctor` 运行一次。macOS GPU 渲染：`export PRODUCER_BROWSER_GPU_MODE=hardware`。

可选键（如果未设置则使用本地回退）— 仅由从计划/生成资产 via media-use 的类别需要：

| 键                                 | 用于                                                    | 回退                        |
| ---------------------------------- | ------------------------------------------------------- | --------------------------- |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | 图像生成（media-use resolve）                            | 跳过生成 / 搜索仅            |
| (asset_scout / 搜索提供者)        | `webpage`/`news`/`tweet` + `asset-fusion` 真实资产搜索 | 类别降级为无资产            |

## 流程

### 步骤 0 — 初始化

cwd 是代理工作区根；在 `PROJECT_DIR = videos/<project-name>/` 下编写所有工件。`<project-name>`：使用用户提供的目录，否则从意图中获取一个短的小写破折号名称（`<subject>-motion`）。不是工作区的基本名称或时间戳。

仅当 `$PROJECT_DIR/hyperframes.json` 不存在时：

```bash
PROJECT_DIR="${MOTION_GRAPHICS_DIR:-videos/<project-name>}"
mkdir -p "$(dirname "$PROJECT_DIR")"
npx hyperframes init "$PROJECT_DIR" --non-interactive --example=blank --skill=motion-graphics
```

`init` 检查已安装的技能与 GitHub 上的最新版本，如果有任何过时的技能，则更新全局集。

**约束**：在工作区根目录中永不 `hyperframes init`；永不将另一个 `hyperframes/` 嵌套在 `PROJECT_DIR` 中；每个 Bash 命令（主代理 + 子代理）都是一个 `(cd "$PROJECT_DIR" && ...)` 子 shell — 永不使用裸 `cd`。

### 步骤 1 — 计划（子代理：导演第一部分）

分发一个子代理。prompt = 完整 `agents/director.md` + `## 分发上下文` (`SKILL_DIR` / `PROJECT_DIR` / 用户的请求 / `Schema: <SKILL_DIR>/references/shot-plan-ir.md`)。它必须：

1. **决定：是否需要搜索？**（第一个分支）
   - **否** → 选择一个 **形式类别**（kinetic-type / stat / charts / logo-reveal / lower-thirds）；内容是用户提供的；`asset_needs: []`。
   - **是** → 发出一个 **搜索计划** 到 `asset_needs[]`（新闻 / 网络 / 推文 / 图像；两极查询）。具体的 **搜索驱动类别**（网页 / 新闻 / 推文 / asset-fusion）由步骤 2 中返回的内容类型确认，并在步骤 3 中最终确定。
2. 编写草稿 `shot-plan.json`（信封 + 选择的形式类别 _或_ 搜索意图 + `asset_needs` + 一段镜头简介）。Schema：`references/shot-plan-ir.md`。

验证：`[ -s "$PROJECT_DIR/shot-plan.json" ] && echo ok || echo missing`。

### 步骤 2 — 源 ◇（Bash：媒体使用，条件）

如果 `shot-plan.json.asset_needs` 非空，解析资产（搜索 / 生成 / 获取 → 冻结的项目本地路径 + 账户）。参见 `phases/source/guide.md`（包装 `media-use resolve`；搜索驱动类别使用新闻/网络/推文/图像搜索）。如果 `asset_needs` 为空，**跳转到步骤 3**。

```bash
# 说明性 — 参见 phases/source/guide.md
(cd "$PROJECT_DIR" && node <SKILL_DIR>/phases/source/resolve.mjs --plan ./shot-plan.json --out ./assets)
```

优雅降级：如果搜索/提供者不可用，类别会降级为无资产（在 `context.log` 中记录）。

### 步骤 3 — 设计（子代理：导演第二部分）

分发一个子代理（prompt = `agents/director.md` 第二部分 + 分发上下文，包括如果步骤 2 运行了 `assets/index.md` + `catalog-map.md`）。它围绕可用的资产设计镜头：选择目录块 + `hyperframes-animation` 规则/蓝图，布局，动态，节拍，以及对于 `asset-fusion` 的 `element_positions` + 吸管调色板。最终确定 `shot-plan.json` (`content.block` + `content.customize` + 每个类别的内容）。

### 步骤 4 — 构建（子代理：构建器，重用优先）

分发一个子代理。prompt = 完整 `agents/builder.md` + 分发上下文 (`shot-plan.json`、`catalog-map.md`、类别的 `module.md`、`references/motion-vocabulary.md`、`references/builder-contract.md`)。**重用优先**：`npx hyperframes add <block>` + 原地自定义；仅手写差距 + asset-fusion 适配性。输出 `compositions/index.html` 尊重 HF 合同（暂停的 GSAP 时间线 ≈ Remotion 的 `useCurrentFrame`）。

### 步骤 5 — 验证（Bash → 失败时修复子代理）

```bash
(cd "$PROJECT_DIR" && npx hyperframes lint .)
(cd "$PROJECT_DIR" && npx hyperframes check .)
(cd "$PROJECT_DIR" && npx hyperframes snapshot --at <proof-times>)
```

选择显示开头状态、标志性动作和最终保持的预览时间。在继续之前检查生成的联系表或快照表。在 `lint`、`check` 或快照失败时，分发修复子代理 (`agents/finalize.md`) 进行一次原地修复，然后重新运行失败的网关。永不仅仅为了隐藏缺陷而更改固定持续时间。

### 步骤 6 — 批准和渲染（Bash）

问一个问题：“预览还是渲染？”如果用户选择预览，打开 Studio 并在修订后返回到相同的批准网关：

```bash
(cd "$PROJECT_DIR" && npx hyperframes preview --background)
```

仅在对渲染给出明确答案后渲染：

```bash
(cd "$PROJECT_DIR" && npx hyperframes render . --skill=motion-graphics -q high -o ./renders/video.mp4)
# 透明叠加变体：--format webm （或 mov）
```

验证输出是否存在、非空、并具有预期持续时间。最终交付物命名工件、实际持续时间、编排或帧 ID、预览时间，以及检查的联系表或快照表。标志位于 `/hyperframes-cli` → `references/preview-render.md`。

## 恢复表

| 状态                                                    | 继续从              |
| -------------------------------------------------------- | -------------------------- |
| 没有 `shot-plan.json`                                      | 步骤 1 (计划)              |
| `shot-plan.json` 有 `asset_needs`，没有 `assets/`         | 步骤 2 (源)            |
| `shot-plan.json` 最终，没有 `compositions/index.html`     | 步骤 3/4 (设计+构建)    |
| `compositions/index.html` 存在，预览快照不存在            | 步骤 5 (验证)            |
| 检查和预览快照通过，没有批准的渲染                      | 步骤 6 (批准)          |
| 批准的渲染存在                                   | 验证输出，然后报告      |

## 设计说明（维护者 — 执行不读取此内容）

- **资产优先的合理性**：源是前置的，并告知镜头设计（RWA 流程：分析 → 搜索 → 审查 → 编排）。搜索驱动类别（`webpage`/`news`/`tweet`）和 `asset-fusion` 都依赖于媒体使用搜索（新闻/网络/推文/图像），这是媒体使用文档的 RWA 血缘。
- **重用优先**：生态系统内类似 LLM 生成的模板是“编排目录块 + `hyperframes-animation` 规则”。HF 的暂停 GSAP 时间线 ≈ Remotion 的 `useCurrentFrame`。
- **类别模块合同**：一个 `categories/<id>/module.md`（规划 + 构建），共享 `references/motion-vocabulary.md`（+ 可选评估）。添加类别 = 删除文件夹 + 在 `agents/director.md` 中注册其分类器行 + 在 `catalog-map.md` 中注册其行；阶段管道不受影响。
- **目录结构**：
  ```
  videos/<project-name>/
    hyperframes.json  context.log
    shot-plan.json            # IR (导演输出)
    assets/  assets/index.md  # media-use 输出 (如果源)
    compositions/index.html   # 构建器输出
    renders/video.mp4
  ```
- **注册**：在 `hyperframes` 路由器 — 添加“设计导向短动态图形”意图 + 工作流程描述；从 `/general-video` 中切割动态图形触发器。添加反向不使用边。参见 `motion-graphics-genre.md` §5-7。
