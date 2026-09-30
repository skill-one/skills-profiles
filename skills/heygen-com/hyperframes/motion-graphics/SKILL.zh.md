---
name: motion-graphics
description: 一个以设计为导向的短动画图形，其中运动本身就是信息——动态文字排版、数据计数、图表/数据可视化、标志特效/品牌组合、底部字幕/标题/社交覆盖层、动画地图（突出区域、连接地点、缩放到位置）、动画推文/新闻文章/标题、网页/UI动画（滚动、光标、标题）、或将真实图像的几何形状融入图表。通常在10秒以内（最长约30秒），无旁白或真人表演；渲染为MP4或透明覆盖层。更长时间/有旁白/多场景→/general-video。不明确→/hyperframes。
---

**插件安装：** 在设置或新鲜度命令之前，当此技能位于 HyperFrames 插件内时，请遵循 [插件执行规则](../hyperframes/references/plugin-installation.md)。独立安装则保留下方的更新说明。

> **首先，保持此技能新鲜——在运行前与用户确认：** `npx hyperframes skills update motion-graphics`。当一切正常时，这是一个快速的无操作；否则，它将在您依赖它们之前刷新此技能及其依赖的核心域技能。

> **figma 源文件：** 如果要构建的标志/资源/动画来自 figma.com URL，请先运行 `/figma` — 资源导出、品牌标记以及 Motion→GSAP 翻译（如果图形是 Figma Motion 导入的），然后从其输出构建。不要通过原始 MCP 工具直接驱动 Figma：那样会跳过 SVG 清理、`.media/manifest.jsonl` 起源以及品牌标记 `var()` 绑定，因此，稍后的品牌更改无法在不完全重新导入的情况下传播。

# motion-graphics — 分发入口

> **正门是 `/hyperframes`。** 此技能制作一个 **短小、以设计为主导、无旁白的动态图形**（动态是信息；~10 秒以内，无旁白）。任何更长的、有旁白的或多场景的——或任何不确定的情况 → 首先阅读 `/hyperframes`：意图层控制每条路线的决策。

此工作流是 **按设计自主的** — 最多一个问题 (`agents/director.md`) 进行澄清，然后通过验证进行构建，无需中间审查。意图层 (`/hyperframes` → `references/intent-interview.md`) 直接路由到此处，无需运行形状问题；故事板和配套会话对此类短小的作品帮助不大。渲染仍然由用户控制：在检查和预览快照通过后，从 `../hyperframes/references/brief-contract.md` 中询问标准的“预览优先，还是渲染？”问题。当存在 `BRIEF.md` 时，在导演的问题之前阅读它。

一个短小、以设计为主导的动态图形。**资源优先**：在设计镜头之前决定资源策略并获取真实材料，然后围绕已有资源设计镜头，然后通过复用目录功能进行编排。所有工件都存放在 `PROJECT_DIR = videos/<project-name>/`（在步骤 0 中创建）；所有下方的路径都相对于它。

| 阶段    | 执行                                                         | 主要工件                                           | 详细流程             |
| ------- | ------------------------------------------------------------ | -------------------------------------------------- | ------------------- |
| init    | Bash                                                          | `hyperframes.json`                                | 步骤 0              |
| plan    | subagent — **决定是否搜索？** + 分类 + 资源策略             | `shot-plan.json` (草稿：类别、`asset_needs` 查询、简报) | `agents/director.md` (第 1 部分) |
| source ◇ | Bash — 媒体使用解析 (**如果 `asset_needs` 为空则跳过**)     | `assets/` + `assets/index.md`                     | `phases/source/guide.md` |
| design   | subagent — 围绕解析的资源设计镜头                           | `shot-plan.json` (最终：块 + 布局 + 动态 + 位置)     | `agents/director.md` (第 2 部分) |
| build    | subagent — 首次复用编排                                       | `compositions/index.html`                         | `agents/builder.md`   |
| verify   | Bash — `lint`、`check`、预览快照；失败时修复                | `snapshots/contact-sheet.jpg`                     | 步骤 5              |
| approve  | 询问预览还是渲染；等待答案                                  | 显式的渲染批准                                     | 步骤 6              |
| render   | Bash — `hyperframes render` (MP4，或 `--format webm/mov` 用于叠加) | `renders/video.mp4` 或透明叠加                     | 步骤 6              |

`◇ source` 仅在所选类别声明资源时运行。纯代码/文本类别（例如 `kinetic-type`、大多数 `charts`/`stat`）有 `asset_needs: []` 并直接从计划跳转到设计。

## 类别 — 根据搜索决定进行划分

`plan` 的 **第一个决定是：是否需要搜索？** 这个分支将类别分为两组；然后选择具体的类别——对于搜索驱动的，**由搜索返回的内容类型决定**。每个类别是一个 `categories/<id>/module.md`（其计划 + 构建规则）；共享的动态词汇表位于 `references/motion-vocabulary.md`（→ `hyperframes-animation` 规则/蓝图 + 注册块）。

**形式类别——无需搜索；用户提供内容：**

| 类别         | 意图                                                                                                         | 依赖于                                                                    |
| ------------ | -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `kinetic-type` | 断言的行 / 引语 / 标题，动态优先文本                                                                 | `caption-*` 块 + 动态规则                                                    |
| `stat`         | 单个英雄数字 / 计数器 + 环                                                                                   | `apple-money-count` / `rules/{counting-dynamic-scale, stat-bars-and-fills}` |
| `charts`       | 条形图 / 线形图 / 饼图 / 比赛 / 来自数据的百分比                                                                   | `data-chart` 块                                                          |
| `logo-reveal`  | 标志刺激 / 品牌锁定（用户标志）                                                                                | `logo-outro` / `rules/svg-path-draw`                                        |
| `lower-thirds` | 名称 / 标题条，注释，社交覆盖层                                                                               | `caption-*` + 注册覆盖块                                                     |
| `maps`         | 地理动态——突出显示区域，连接地点，缩放到位置（矢量车道，或烘焙的底图车道）                                           | `us-map` / `world-map` 系列 + `bake-basemap.mjs`                          |

**搜索驱动类别——先搜索，然后根据内容类型进行动画**（RWA 路径）：

| 返回内容   | 类别         | 动画                                                      |
| ---------- | ------------ | -------------------------------------------------------------- |
| 网页 / 链接 | `webpage`      | 网页 / UI 动态（滚动、揭示、光标、注释）                      |
| 新闻文章     | `news`         | 标题揭示 + 来源卡片 + 关键事实注释                          |
| 推文            | `tweet`        | 动态推文卡片                                                |
| 图像 / 实体   | `asset-fusion` | 资源的几何形状 _成为_ 图表（RWA 叙事融合）                     |

构建顺序：一次一个，覆盖优先（粗糙即可）。`kinetic-type` 从原型移植；其余的按顺序进行。

## 前置条件

macOS Apple Silicon 或 Linux x64。系统工具：`brew install node ffmpeg`。`npx hyperframes doctor` 运行一次。macOS GPU 渲染：`export PRODUCER_BROWSER_GPU_MODE=hardware`。

可选键（如果未设置则使用本地回退）——仅由从计划/生成资源中获取资产的类别需要：

| 键                                 | 用于                                                    | 回退                        |
| ----------------------------------- | ----------------------------------------------------------- | ------------------------------- |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | 图像生成（媒体使用解析）                        | 跳过生成 / 仅搜索             |
| (asset_scout / 搜索提供者)    | `webpage`/`news`/`tweet` + `asset-fusion` 实际资产搜索 | 类别降级为无资产             |

## 流程

### 步骤 0 — 初始化

cwd 是代理工作区根；在 `PROJECT_DIR = videos/<project-name>/` 下编写所有工件。`<project-name>`：使用用户提供的目录，否则从意图中获取一个短小的连字符命名（`<subject>-motion`）。不是工作区的基本名称或时间戳。

仅当 `$PROJECT_DIR/hyperframes.json` 不存在时：

```bash
PROJECT_DIR="${MOTION_GRAPHICS_DIR:-videos/<project-name>}"
mkdir -p "$(dirname "$PROJECT_DIR")"
npx hyperframes init "$PROJECT_DIR" --non-interactive --example=blank --skill=motion-graphics
```

`init` 检查已安装的技能与 GitHub 上的最新版本，如果有任何技能过时，则更新全局集。

**约束：** 在工作区根目录中永不 `hyperframes init`；永不将另一个 `hyperframes/` 嵌套在 `PROJECT_DIR` 中；每个 Bash 命令（主代理 + 子代理）都是一个 `(cd "$PROJECT_DIR" && ...)` 子壳——永不使用裸 `cd`。

### 步骤 1 — 计划（子代理：导演第 1 部分）

分发一个子代理。prompt = 完整的 `agents/director.md` + `## 分发上下文` (`SKILL_DIR` / `PROJECT_DIR` / 用户的请求 / `Schema: <SKILL_DIR>/references/shot-plan-ir.md`)。它必须：

1. **决定：是否需要搜索？**（第一个分支）
   - **否** → 选择一个 **形式类别**（kinetic-type / stat / charts / logo-reveal / lower-thirds）；内容由用户提供；`asset_needs: []`。
   - **是** → 发出一个 **搜索计划** 到 `asset_needs[]`（新闻 / 网络 / 推文 / 图像；双极查询）。具体的 **搜索驱动类别**（webpage / news / tweet / asset-fusion）由步骤 2 返回的内容类型确认，并在步骤 3 中最终确定。
2. 编写草稿 `shot-plan.json`（信封 + 选择的形式类别 _或_ 搜索意图 + `asset_needs` + 一段镜头简报）。Schema: `references/shot-plan-ir.md`。

验证：`[ -s "$PROJECT_DIR/shot-plan.json" ] && echo ok || echo missing`。

### 步骤 2 — 资源 ◇（Bash：媒体使用，条件）

如果 `shot-plan.json.asset_needs` 非空，解析资源（搜索 / 生成 / 获取 → 冻结的项目本地路径 + 账本）。参见 `phases/source/guide.md`（包装 `media-use resolve`；搜索驱动的类别使用新闻/网络/推文/图像搜索）。如果 `asset_needs` 为空，**跳转到步骤 3**。

```bash
# 说明性 — 参见 phases/source/guide.md
(cd "$PROJECT_DIR" && node <SKILL_DIR>/phases/source/resolve.mjs --plan ./shot-plan.json --out ./assets)
```

优雅降级：如果搜索/提供者不可用，类别会降级为无资产（在 `context.log` 中记录）。

### 步骤 3 — 设计（子代理：导演第 2 部分）

分发一个子代理（prompt = `agents/director.md` 第 2 部分 + 分发上下文，包括步骤 2 运行时解析的 `assets/index.md` + `catalog-map.md`）。它围绕可用的资源设计镜头：选择目录块 + `hyperframes-animation` 规则/蓝图、布局、动态、节拍，以及（对于 `asset-fusion`）`element_positions` + 吸管调色板。最终确定 `shot-plan.json` (`content.block` + `content.customize` + 每个类别的内容）。

### 步骤 4 — 构建（子代理：构建器，首次复用）

分发一个子代理。prompt = 完整的 `agents/builder.md` + 分发上下文 (`shot-plan.json`、`catalog-map.md`、类别的 `module.md`、`references/motion-vocabulary.md`、`references/builder-contract.md`)。**首次复用**：`npx hyperframes add <block>` + 就地自定义；仅手写差距 + 资源融合的适配性。输出 `compositions/index.html` 尊重 HF 合同（暂停的 GSAP 时间线 ≈ Remotion 的 `useCurrentFrame`）。

### 步骤 5 — 验证（Bash → 失败时修复子代理）

```bash
(cd "$PROJECT_DIR" && npx hyperframes lint .)
(cd "$PROJECT_DIR" && npx hyperframes check .)
(cd "$PROJECT_DIR" && npx hyperframes snapshot --at <proof-times>)
```

选择显示开篇状态、标志性动作和最终保持的预览时间。在继续之前检查生成的联系表或快照表。在 `lint`、`check` 或快照失败时，分发修复子代理 (`agents/finalize.md`) 进行一次就地修复，然后重新运行失败的网关。永不仅仅为了隐藏缺陷而更改固定时长。

### 步骤 6 — 批准和渲染（Bash）

问一个问题：“预览优先，还是渲染？”如果用户选择预览，打开 Studio 并在修订后返回到相同的批准网关：

```bash
(cd "$PROJECT_DIR" && npx hyperframes preview --background)
```

仅在对显式渲染回答后渲染：

```bash
(cd "$PROJECT_DIR" && npx hyperframes render . --skill=motion-graphics -q high -o ./renders/video.mp4)
# 透明叠加变体：--format webm  (或 mov)
```

验证输出存在、非空且具有预期时长。最终交付物命名工件、实际时长、编排或帧 ID、预览时间，以及检查的联系表或快照表。标志位于 `/hyperframes-cli` → `references/preview-render.md`。

## 恢复表

| 状态                                                    | 继续从              |
| -------------------------------------------------------- | -------------------------- |
| 没有 `shot-plan.json`                                      | 步骤 1 (计划)              |
| `shot-plan.json` 有 `asset_needs`，没有 `assets/`         | 步骤 2 (资源)            |
| `shot-plan.json` 最终，没有 `compositions/index.html`     | 步骤 3/4 (设计+构建)    |
| `compositions/index.html` 存在，预览快照不存在            | 步骤 5 (验证)            |
| 检查和预览快照通过，没有批准的渲染                      | 步骤 6 (批准)          |
| 批准的渲染存在                                   | 验证输出，然后报告 |

## 设计说明（维护者——执行不读取此内容）

- **资源优先的合理性：** 资源获取是前置的，并指导镜头设计（RWA 流程：分析 → 搜索 → 审查 → 编排）。搜索驱动的类别 (`webpage`/`news`/`tweet`) 和 `asset-fusion` 都依赖于媒体使用搜索（新闻/网络/推文/图像），这是媒体使用文档中记录的 RWA 血缘。
- **首次复用：** 生态系统中类似 LLM 生成的模板是“编排目录块 + `hyperframes-animation` 规则”。HF 的暂停 GSAP 时间线 ≈ Remotion 的 `useCurrentFrame`。
- **类别模块合同：** 一个 `categories/<id>/module.md`（计划 + 构建），共享 `references/motion-vocabulary.md` (+ 可选评估)。添加类别 = 删除文件夹 + 在 `agents/director.md` 中注册其分类行 + 在 `catalog-map.md` 中注册其行；阶段管道不受影响。
- **目录结构：**
  ```
  videos/<project-name>/
    hyperframes.json  context.log
    shot-plan.json            # IR (导演输出)
    assets/  assets/index.md  # 媒体使用输出 (如果资源获取)
    compositions/index.html   # 构建器输出
    renders/video.mp4
  ```
- **注册：** 在 `hyperframes` 路由器中——添加“设计主导的短动态图形”意图 + 工作流描述；从 `/general-video` 中切割出动态图形触发器；添加反向不使用边。参见 `motion-graphics-genre.md` §5-7.
