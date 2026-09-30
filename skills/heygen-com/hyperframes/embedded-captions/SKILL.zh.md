---
name: embedded-captions
description: 为现有的单人访谈视频添加字幕或标题，无需编辑素材。适用于纯文本字幕、嵌入主体后的电影感字幕、VFX字幕、“炸/特效/酷炫字幕”或35式目录中的命名身份。通过视觉身份而非后端引擎进行路由。静音的`anchor`轨道为默认设置；仅当用户明确要求全电影感处理时，才嵌入每个字。工作流端到端在本地运行，包括转录和主体抠像；在应用多镜头素材前进行分割。
---

**插件安装：** 在设置或新鲜命令之前，当此技能位于 HyperFrames 插件内部时，请遵循 [插件执行规则](../hyperframes/references/plugin-installation.md)。独立安装则保留以下更新说明。

> **首先，保持此技能新鲜——在运行前与用户确认：** `npx hyperframes skills update embedded-captions`。当一切正常时，这是一个快速的无操作；否则，它将在您依赖它们之前刷新此技能及其依赖的核心域技能。

# 嵌入式字幕

**一个目录，一开始就选取** ([CATALOG.md](CATALOG.md) — 35 个身份；其背后的引擎是后端细节）。**标准**（默认）构建一个干净的逐字**轨道**（位于主体下方的字幕框承载大部分文本）+ 一个**嵌入**高潮合成到主体在场景峰值后面的背景中。**电影感**是纯粹的嵌入——没有轨道，每个字幕都合成在主体后面（英雄字体、累积、遮挡作为效果）。**主题**是一个完整的主题构成——主体范式×英雄场景×前特效×板式反应，从注册表 ([themes/README.md](themes/README.md)) 中合成：`ordnance` `terminal` `neonsign` `stardust` `stomp`。大多数解释性/旁白是**标准**；**嵌入是稀缺的、应得的巅峰**——嵌入每个字是常见的错误；主题适用于 VFX 级别的请求（“炸”、“特效”、“像 AE 做的”）。

---

## 运行时先决条件

插件安装使用捆绑的、通过清单固定的 CLI 进行抠像、转录和渲染；不需要源代码检出。本地预览和字幕测量辅助工具也需要 Sharp、Puppeteer（带其 Chromium 浏览器）和 GSAP。在**字幕项目**中安装这些，而不是在只读插件内部：

```bash
npm install --prefix <project> --save-dev --save-exact sharp@0.35.3 puppeteer@25.8.0 gsap@3.15.0
```

保留项目的锁文件。如果这些依赖项已经存在，请使用其锁定版本，而不是覆盖它们。Bash 和 FFmpeg/ffprobe 必须在 PATH 上。抠像和转录可能在首次使用时下载自己的模型。

渲染等待 CLI 成功退出后再进行合成。旧的 `HF_TIMEOUT_S` shell 狗哨不再使用：一个大的部分文件并不能证明渲染已完成。一个显式的 built-checkout 参数或 `HYPERFRAMES_ROOT` 选择贡献者 CLI 而不是插件固定。通过 CLI/终端正常取消卡住的渲染；字幕辅助工具不会强制杀死或从进程快照中恢复渲染。

## 操作流程（TL;DR）

通过 `/hyperframes` 路由，意图层仅确认输入（哪个片段）并**宣布**身份选择为延迟请求——短名单需要探测到的片段，所以它保持在下面的步骤 1 中；层的运行形状问题不适用（片段未受影响，没有故事板需要审查）。当存在 `BRIEF.md` 时，它会携带确认的输入和任何用户笔记——首先阅读它。

下面的创作文本很长；**管道本身很短**——所有确定性内容都是计算或编译的，从未手写：

1. **决策门**（拒绝坏片段）→ **从 [CATALOG.md](CATALOG.md) 中选择一个身份**（35 个身份；引擎/编译器通过查找确定——从不显示模式/类别问题）
2. `hyperframes init`（如果项目目录已经存在视频在里面则跳过它——`matte.cjs`/`transcribe.cjs` 将目录中的任何视频作为源.mp4）→ **`bash scripts/prepare.sh <project>`**（抠像 ∥ 转录 ∥ 音频包络并行，然后安全区域 v2 与场景调色板/光学/照明——一个命令，没有遗漏）
3. **创作一个小型 JSON 的选择**（首先读取 `safe-zones.json`）：电影感 → `plan.json` → `fill-timings.cjs` → `fit-fonts.cjs` → `make-composition.cjs`；主题 → `theme.json` → `make-theme.cjs`（轨道/面板/诗/接管范式；`anchor` 是安静的轨道默认值）
4. **视觉 QA**：`node scripts/preview-frames.cjs <project>` → 忠实合成预览，每个帧约 2 秒（无需渲染）。在支付渲染前检查 § 视觉 QA。
5. `render-and-composite.sh` → 门（时间/遮挡+英雄/溢出/交接）→ `final.mp4`

人们容易忽略的承重规则：

- **轨道（默认）+ 嵌入（提升）。** `drop`（填充，未显示）/ `rail`（逐字下三分之一字幕，在前方，承载大部分文本）/ `embed`（一个高峰词合成在主体后面）。**标准模式两者都做**，仅嵌入高峰词。见 **§ 字幕模型**。
- **视频保持未受影响（标准/电影感；**主题模式的 PLATE 预算是唯一认可的例外**——注册门控反应节拍（充电暗淡、打击、摇晃、颗粒）定义每个主题 DNA 并在抠像合成后应用，因此主体+文本+板式作为一个帧移动）**——字幕是唯一添加的东西；抠像只是允许主体遮挡嵌入轨道。永远不要调色/重色/扫描线片段。
- 两本规则书：**轨道 → [references/rail.md](references/rail.md)**（薄），**嵌入工艺 → [references/composition-craft.md](references/composition-craft.md)**（丰富，仅嵌入）。按需浏览。

---

## 字幕模型——轨道 + 嵌入

每个口语短语是以下三种之一：

|           | 内容                                             | 如何显示                                                                                                                                                    |
| --------- | ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **drop**  | 填充——嗯/呃、卡顿、自我纠正                       | 未显示                                                                                                                                                         |
| **rail**  | 默认——普通口语内容（逐字）                       | 干净的下三分之一字幕，**在前方**，可读。一个冲击词可以得到一个内联 `emphasis` 高亮（强调色/活动词弹出）——它保持在轨道上。 |
| **embed** | 一个提升的高潮——头条节拍                          | 一个大字合成 **在主体后面**（抠像遮挡），设计进入+退出                                                                        |

**轨道承载大部分文本；嵌入是稀缺的、应得的巅峰。** 稀缺性是**按节拍/块，而不是按片段**：≤1 英雄每个块（思想），永远不会两个同时可见，≥ 英雄窗口之间的一个节拍空气（编译器在 0.6 秒以下发出警告）。短片段 → 通常 1-2；长解释 → 约 每个部分一个。在多个英雄中，**最大创作的那个是 APEX**（它独自获得完整的锁定嵌入+宽度调整）；较小的那些是 **次要的高潮**，作为超大的强调线（前景、阻尼运动）骑在它们的列上——不是每个节拍都需要抠像展示，这正是保持巅峰成为事件的原因。嵌入每个字仍然是常见的错误。

轨道表面身份构建正好是这个（轨道 = `rail.html`，嵌入 = `index.html` 中的高潮）。列流身份放弃轨道并制作所有嵌入样式——仅推荐它们用于情绪重于逐字请求，绝不用于解释性/旁白，其中单词必须可读（CATALOG.md 按身份编码此内容）。

---

## 第 0 步——从目录中选取一个身份

**一个前端，三个后端引擎。** 用户从 [CATALOG.md](CATALOG.md)（35 条目：10 经典 + 25 主题）中选择一个 IDENTITY；引擎、编译器和创作文件通过从目录行查找确定。**永远不要将“标准 vs 电影感 vs 主题”作为问题**——这些都是后端名称（即使有多个引擎，产品也有一个 UX）。目录编码了所有路由需要的内容：读取表面、声音、推荐给、场景需求、真正接近对的邻接性笔记（响亮↔ordnance、霓虹灯↔neonsign、奶油↔stardust）。

身份选择是一个**偏好门**（`../hyperframes/references/brief-contract.md` § 1）：在自主模式（“让我惊喜”/“为我决定”）下，自己从短名单中选择并说明为什么选择，而不是询问。

程序：探测片段 → 从目录中短名单 2-3 个身份 → 推荐一个并说明为什么 → **用户选择**（自主模式：你选择，说明为什么）→ 创作该身份的文件。身份是引擎锁定的（不能跨组合；打开一个是验证事件——见 dna/README.md）。

**在创作之前始终展示你的推荐并让用户选择。** 不要无声默认。

（完整的身份表存在于 [CATALOG.md](CATALOG.md) — 单一事实来源，用于路由。下面的引擎文档描述了每个后端的创作合同。）

**CATALOG.md 是这里的完整答案空间：这个工作流不会搜索 HyperFrames 组件注册表。** 组合工作流在创作命名查找之前运行 `npx hyperframes catalog`；这个必须不运行。它的引擎是锁定的编译器，消费 `cinematic.json` / `theme.json` 并自行发出组合，所以一个注册表项——包含的 `caption-*` 块——没有什么可以挂载进去。注册表块在设计的画布上样式化文本；这个技能通过抠像将字幕烧入某人的片段中。当没有身份符合请求时，说清楚并选择最近的，而不是超出目录。

**推荐启发式方法**：使用 [CATALOG.md](CATALOG.md) 中的“短名单启发式方法”——它们是身份级别的（例如，“炸”短名单 ordnance/stomp/terminal/loud 并按 WHAT 应该爆炸选择），而不是类别级别的。不确定 → `anchor`。

- **电影感** → 写 `plan.json` 为锁定模板，由 `make-composition.cjs` 编译。
- **主题** → 阅读 [themes/README.md](themes/README.md)，创作 `theme.json`，运行 `scripts/render-theme.sh`（编译 + 渲染 + 板式反应 → **final_fx.mp4**）。

---

## 决策门——首先运行

在两种模式之前探测视频并对场景进行分类。

```bash
ffprobe <video.mp4>                    # 规格
ffmpeg -ss <t> -i <video.mp4> -vframes 1 sample.png   # 在 20/50/80% 处
```

读取样本。如果拒绝：

- 多个说话者 / 硬切（分割并渲染每个镜头，或者拒绝）
- 没有人主体（这个技能是用于谈话头）
- 3 秒以下，**没有语音**，或者脸从未清晰可见——`transcribe.cjs` 在音频接近静默时发出警告（Whisper 在静默上想象“谢谢。”等词）；**注意它并拒绝**，而不是字幕虚构的词
- **源已经带有烧入的字幕/字幕/重文本图形**——添加第二个字幕系统冲突，并且片段保持未受影响（不覆盖/修复）。烧入的文本通常只出现在片段中间：采样 **1fps 联系表** (`ffmpeg -i in.mp4 -vf "fps=1,scale=160:-1,tile=10x5" sheet.png`)，不要相信 3 个点帧。
- **转录是垃圾**——非母语/重口音语音可以转录成自信的胡言乱语。在创作前阅读 `transcript.json`；如果它不能解析为语言，尝试 `WHISPER_MODEL=medium` 一次，否则拒绝（逐字轨道的虚构词比没有字幕更糟）。
- 忙碌手持快速运动（抠像闪烁）

### 预飞行探测（不花钱，防止最坏的失败）

1. **镜头切探测。** 在 20%、50%、80% 处采样帧。如果一个不同的主体/场景出现，**在切之前修剪片段**。
2. **信箱/柱状探测。** 第一帧上有黑条吗？计算安全内容矩形并将字幕放置在其内部。
3. **亮度探测。** 采样字幕区域的平均亮度——`低于 60` → 淡色文本按原样读取，`60-180` → 添加字形遮罩，`180+` → 不透明文本+遮罩（从不裸露亮色文本）。**电影模板是奶油+`screen` 并且锁定**——使用这个探测来挑选一个合适的身份（亮场景 → `ink`，或透明轨道 `anchor` 主题），永远不要重新着色一个。
4. **身份推荐由语气（你推荐；用户选择——见第 0 步 + CATALOG.md）。** 解释性/访谈/必须读的词 → 轨道/面板表面身份；诗意/社交/“电影感” → 列流身份按注册；“炸 / 特效 / VFX”/命名世界 → 主题身份。不确定 → `anchor`（字可读，场景安全）——但展示一个短名单并让用户选择。

---

## 管道——5 步

```
1. hyperframes init <project> --non-interactive --video <video.mp4> --skill=embedded-captions
2. bash scripts/prepare.sh <project>       # matte ∥ transcribe (并行) → safe-zones. 一个命令。
                                           #   → frames_fg/ transcript.json safe-zones.json
3. [AGENT 步骤——唯一的创作步骤] 创作一个小型 JSON；见下面按模式
   电影感：创作 plan.json → node scripts/fill-timings.cjs → fit-fonts.cjs → make-composition.cjs
   主题：     创作 theme.json → bash scripts/render-theme.sh <project>   (编译 + 渲染 + 板式 fx)
4. node scripts/preview-frames.cjs <project>   # ~2s/帧合成预览 → § 视觉 QA（渲染前）
5. bash scripts/render-and-composite.sh <project>  # 门 → final.mp4 + history/ 快照
   (主题模式：跳过步骤 3b/5 — render-theme.sh 已经运行编译 + render-and-composite
    + _postfx.sh；交付是 final_fx.mp4，final.mp4 是预板式反应)
```

步骤 1 的 `init` 检查已安装的技能与 GitHub 上的最新版本，如果任何技能过时，则更新全局集。

步骤 3 因模式而异：

### 步骤 3 — 电影感模式（纯粹嵌入）

1. **首先读取 `safe-zones.json`。** 解说平面进入 **`zones.hugLeft`/`hugRight`** — 干净的条带紧挨着轮廓（文本远离身体读起来像漂浮的，不是嵌入的；远角是备用，不是默认的）。英雄默认为 `heroAnchor`/`heroBands.best`（在主体上居中，~30–55% 遮挡）。`recommendation:"fg"` 将解说移到前面以提高可读性；**只要 `heroBands.feasible`，英雄就保持嵌入** — 英雄-fg 是最后的手段。
2. **DNA 是你在步骤 0 中选择的身份**（CATALOG.md）——不要在这里重新打开选择。将其与场景进行核对（亮英雄带亮度 > 150 需要 `ink`；完整的挑选指南存在于目录中，涵盖所有十个，包括霓虹灯/故障/铬/速度）。说明你的选择+原因；用户决定。DNA 锁定类型调色板/混合/运动+英雄三幕；安全区域 v2 (`palette`/`optics`/`lighting`) 自动参数化到这个场景。
3. **创作 `<project>/cinematic.json`** — `"dna": "<name>"` + 思想块，不是原始组：每个块=单词行（在子句边界分组 2-5）+ 它堆叠的平面+每行 `css`（大小/重量/样式仅——不位置）+ 至多一条标记 `"hero": true`（推广词；`"text"` 用于显示形式）。模式：`scripts/make-cinematic.cjs` 头部。
4. **编译**：`node scripts/make-cinematic.cjs <project>` — 降低块→plan.json→index.html。为你生成的：转录序列时间、块内累积、块间翻页、**英雄锁定**（英雄块的前上下文、英雄和后上下文作为 ONE 绑定组合居中在主体上——阅读顺序从上到下=说话顺序按构造；上下文浮现在前面，英雄嵌入在后面=深度三明治；一个质量规则保持英雄主导其上下文），高峰/次要英雄分割，**按构造的阅读顺序**，前景按安全区域。然后通常运行门。_(直接手写 plan.json 保持可能为设计块无法表达——然后运行 `fill-timings.cjs` + `fit-fonts.cjs` + `make-composition.cjs` 自己。)_

1. **通过内容注册选择主题DNA**（每个 `themes/<name>.json` 包含 `voice` + `when`）。声明你的选择及原因；由用户决定。
2. **作者 `<project>/theme.json`** — `dna`, `lines`（逐字，转录顺序；每个1-5个词 — 对于 `takeover` 每行是一个CARD），`minors`（强调词），`hero:{match}`（高潮词/短语；将其从 `lines` 中排除用于嵌入片段，保留用于内联片段和面板+编辑）。
3. **渲染**：`bash scripts/render-theme.sh <project>` — 编译（编译时逐字完整性门禁），渲染两层，合成，应用版面反应 → `final_fx.mp4`。在编译和渲染之间使用 `preview-frames.cjs` 进行视觉QA。

---

## 视觉QA — 渲染前预览

`node scripts/preview-frames.cjs <project> [t…]` 在约2秒内合成**忠实预览帧**（在搜索时间快照的标题层 + 真实视频帧 + 蒙版遮挡 + 轨道覆盖 = 最终合成在该时刻的样子）。默认样本 = 每组/高潮窗口。完整渲染需要分钟 — 永远不要用它来**发现**布局问题。

对照列表检查预览 (`<project>/preview/sheet.png`) — 这些是几何门禁**无法**捕获的失败：

1. **泛白** — 亮文本覆盖在明亮区域（窗口/标志/天空）：难以阅读 → 移动平面或更改DNA/模式（明亮场景 → `ink`）。
2. **文本叠文** — 标题覆盖场景本身的文本/图形，或两个标题组冲突。
3. **阅读顺序** — 屏幕上的垂直顺序必须与说话顺序匹配；主角不能位于后期词语下方。
4. **主角存在** — 高潮应该很大且明显在主体后面（约30-55%遮挡），而不是边距中的浮动标签。
5. **平衡** — 一个连贯的列/带，不是零散的碎片；边距呼吸；没有裁剪。

然后是 **5个正面检查** 在 [references/reference-bar.md](references/reference-bar.md)（海报测试 · 谨慎测试 · 一瞥层次 · 场景握手 · 死空气审计） — 失败列表阻止渲染损坏；正面列表使其**设计**。通过时发货。

**新鲜眼睛审查（推荐用于任何面向用户的内容）**：你对自己的布局有确认偏见。如果你能生成一个子代理，只给它预览表单 + 这个检查清单，并要求每帧的PASS/FIX裁决（“对照5点检查清单审查这些标题预览；回答PASS或具体修复每帧”）。在 `plan.json / theme.json` 中应用修复，重新编译，重新预览 — 每个循环只需几秒钟。预览通过后渲染一次。

---

## DNA注册 — 十种视觉语言（取代模板目录）

两种模式都从 **[dna/](dna/README.md)** 绘制 — 十种艺术指导的视觉语言，**按场景参数化**（从镜头采样强调，沿测量光方向接触阴影，深度匹配模糊，RMS耦合英雄振幅）：

| DNA             | 注册       | 场景适配                                       | 语音                                                                                              |
| --------------- | -------------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| **cream**       | premium-warm   | 暗色/中暖场景                            | Inter + 暖奶油 + 屏幕；发光的英雄出现（电影奶油的继承者）                 |
| **ink**         | premium        | **亮场景（luma > 150）**                  | 近黑色乘法 — 印刷在墙上；明亮场景的答案                            |
| **editorial**   | editorial-luxe | 反思 / 时尚 / 诗意                | Bodoni Moda，小写斜体英雄 — 杂志优雅                                             |
| **keynote**     | tech-premium   | 产品 / 发布                                | 不透明白色 Inter 800，死中心静止                                                      |
| **documentary** | formal         | 采访 / 严肃                             | 烧入揭示，无英雄 — 庄重就是风格                                                   |
| **loud**        | loud           | 热潮 / 运动 / 社交                           | Anton + 场景采样强调，单单元猛击 + 涟漪；身体在前面宣布 (`bodyLayer: fg`) |
| **neon**        | loud-neon      | 霓虹黑 / 夜生活 / 科技黑（暗场景）      | 电动青色标志，点火闪烁，英雄像标志一样启动                            |
| **glitch**      | loud-neon      | 数字 / 黑客 / AI                           | RGB分裂回声在着陆时粘在一起；机器打击节奏                               |
| **chrome**      | loud-luxe      | Y2K / 时尚科技 / 音乐                      | 液体金属渐变英雄 + 持续一次扫过                                             |
| **velocity**    | loud-sport     | 运动 / 汽车 / 健身                          | 每个词沿着其运动矢量到达（条纹+倾斜），英雄带有速度轨迹            |

通过 `safe-zones.json` (`heroAnchor.bandLuma`, `palette.temperature`) × 内容注册选择 — [dna/README.md](dna/README.md) 有决策规则。作者：`cinematic.json` 拿到 `"dna": "<name>"`。

引擎从DNA生成**英雄三幕**（无需作者）：共显标题变暗（铺垫）→ 每个字母随着说话响亮度逐字进入（冲击）→ 呼吸+发光直到退出（余韵）。

（遗留：`plan.template:"cinematic-cream"` 自动映射到 `dna:"cream"`。退役的54模板库存档在此存储库外，不随技能分发；`_motion.md` 保留在技能内作为运动动词参考目录。）

---

## 美学决策 — 调性 × 镜头 × 平台（输入到目录短选，不是第二个路由器）

在3个轴上对片段进行分类并将结果输入到CATALOG.md的短选 — 本节本身不会选择模式/引擎：

**调性**（内容有什么感觉？）

- documentary | conversational | energetic | poetic | keynote | investigative | music-video

**镜头**（什么构图？）

- 特写（头+肩） | 中景（躯干+) | 全景（全身+) | 切割蒙太奇（混合镜头）

**平台**（在哪里播放？）

- 9:16 竖屏（TikTok/IG/Shorts） | 16:9 横屏（YouTube/网络） | 1:1 方形 | 广播导出

在 [references/direction-catalog.md § 分类矩阵](references/direction-catalog.md) 中交叉参考方向语言 — 然后返回到 [CATALOG.md](CATALOG.md) 短选身份（该矩阵提供了短选信息；目录是唯一的路由表面）。

## 组合工艺（嵌入轨道） — 嵌入前阅读

完整的 **嵌入轨道** 播放手册在 **[references/composition-craft.md](references/composition-craft.md)**：转录角色注释，短语分组，平面 & 干净区锚定，区域连贯性，高潮突出 & 可读性，边缘呼吸，遮挡三步判断，累积/持久。它管理一个_推广_短语如何坐入场景 — 在作者任何嵌入（Cinematic `plan.json` 或 Standard `index.html`）前阅读它。默认**轨道**轨道有自己的、更简单的规范 → **[references/rail.md](references/rail.md)**。

---

## 共享知识

| 文档                                                                      | 什么                                                                                                                               |
| ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| [references/rail.md](references/rail.md)                                 | **轨道轨道** — 标准下三分之二的标题规范（默认；承载大部分文本）。                                          |
| [references/composition-craft.md](references/composition-craft.md)       | **嵌入轨道手册** — 分组，平面，高潮突出，遮挡判断，累积/持久。嵌入前阅读。 |
| [dna/README.md](dna/README.md)                                           | **DNA注册** — 十种场景参数化视觉语言；如何选择。                                                      |
| [references/reference-bar.md](references/reference-bar.md)               | **品味条** — 每个注册的世界级参考 + 5个正面检查。                                                   |
| [references/aesthetic-principles.md](references/aesthetic-principles.md) | **18条规则。** 胜过Veed AI的品味。首先阅读。                                                                               |
| [references/motion-vocabulary.md](references/motion-vocabulary.md)       | 10个命名运动原语 + 调性→时间查找                                                                                    |
| [references/direction-catalog.md](references/direction-catalog.md)       | 10个可上船的美学 + 调性×镜头×平台矩阵                                                                               |
| [references/anti-patterns.md](references/anti-patterns.md)               | 已锁定的错误（CoreML，字母间距重排，等）                                                                      |
| [references/scene-types.md](references/scene-types.md)                   | 当墙壁表面可用时（4个条件）                                                                                       |
| [references/layout-heuristics.md](references/layout-heuristics.md)       | 平面定位，干净区选择，皇冠3个条件， pillarbox数学                                                        |
| [references/typography-presets.md](references/typography-presets.md)     | 字体大小 × 列宽矩阵（起点）                                                                                  |
| [references/caption-grouping.md](references/caption-grouping.md)         | 词→组规则（暂停，句子边界）                                                                                   |
| [references/failure-modes.md](references/failure-modes.md)               | 开发者常见错误的长尾                                                                                                           |
| [references/bespoke-vs-presets.md](references/bespoke-vs-presets.md)     | 为什么预设有时会失败；克隆并微调模式                                                                                |

**首先阅读美学原则和方向目录。** 一切其他都是实现细节。

---

## 非协商项

- **脸部必须永远不会连续100%覆盖** — 每0.3秒窗口，脸部bbox ≥30%未覆盖。
- **WCAG对比度** — 最终渲染检查；如果失败，修复调色板。
- **确定性** — 没有 `Math.random()`，没有 `Date.now()`，没有 `repeat:-1`。
- **永远不要对视频进行分级/重新着色。** 镜头未经修改地发送 — 标题是唯一的添加。没有全帧扫描线 / 双色调 / 暗化 / 轮廓。neon-noir/CRT纹理属于_标题元素内_，而不是整个帧。
- **对于访谈/解释，优先使用轨道。** 不要嵌入整个转录 — 大部分文本是轨道；只嵌入高峰。嵌入所有内容是默认错误。
- **嵌入是稀缺的+间隔的。** ≤1嵌入每句/节奏，永远不会相邻或共显，≥一个节奏间隔，最多一个 `apex`。高潮 = 每个节奏高峰，**不是**“整个片段的唯一回报”。
- **Matte = 人（超帧 `remove-background`，u2net_human_seg，Apache-2.0）。** 意图上的人体分割，但不是外科手术：薄的偏移家具（麦克风臂）通常被排除 — 标题渲染在其上，在人物后面 — 而靠近主体的显着物体（望远镜，桌面装置）仍然可以泄漏到matte并遮挡标题。主体持有的物体（产品，手机）可能会间歇性地消失，让标题在前面通过。**永远不要假设**：在放置英雄前，在2-3个时间戳处采样 `frames_fg/`，并优先选择远离任何泄漏家具的英雄位置（`heroAnchor` 可以被泄漏扭曲 — 与 `frames_bg` 交叉检查）。
- **safe-zones是 PROP-BLIND — 每个你使用的带都要肉眼检查。** 带宽/heroBands评分_主体_遮挡 + luma：一个麦克风，望远镜或屏幕坐在“干净”区域内是看不见的（并且一个泄漏到matte的道具会扭曲 `heroAnchor.centerXPct` 离开人物）。在作者前，提取你打算使用的每个带的**一帧**；如果道具在那里，测量其bbox并移动/缩小平面。两个真实案例干净地发货，因为代理确实这样做了。（自动道具显着性是一个已知差距；区域的 `peakLuma` 只能捕获_移动_的明亮物体。）
- **标题保持在帧内。** Cinematic模式硬限制帧溢出；Standard模式运行 `check-overflow.cjs` 作为警告（有意溢出是唯一例外 — 阅读警告）。
- **每个标题 ≥ 0.5秒在屏幕上** — 更短 = 难以阅读。
- **词时间必须与 transcript.json 在80ms内匹配** — 标题在节奏500ms后触发会破坏场景幻觉。Cinematic运行 `check-timing.cjs --strict` 在渲染前（通过 `render-and-composite.sh`）；THEME模式在编译时强制相同的节奏（make-theme的顺序转录匹配器 + 逐字完整性门禁 — 漂移是编译错误）。永远不要将多个转录词打包成一个条目（例如 `"FUTURE OF"` 或 `IT` + 换行 + `ALL` 堆叠用一个开始/结束） — 第二个词会继承第一个的timestamp并提前触发。将它们分成单独的词条目，即使你想将它们放在同一视觉行上（使用CSS `white-space` / 自然换行而不是 `<br>`）。支持创意替换，其中标题文本 ≠ 转录（例如 `"15%"` 替换 `"fifteen percent"`） — 在 `CREATIVE_SUBS` 内 `check-timing.cjs` 中注册它们。
- **组窗口必须包含它们的词** — `group.in ≤ min(word.start)` 和 `group.out ≥ max(word.end)` 对每个组。如果 `group.in` 晚于词的开始，词会被静默延迟，直到容器挂载（我们已发货过800ms延迟错误）。验证器强制执行此规则。
- **没有两个标题组可以在时间和屏幕区域都重叠** — 重叠在时间上的标题会创建文本叠文堆积。选项： (a) **空间分离** — 将每个组放置在非重叠的垂直带中，以便它们可以共存（记忆墙级联风格）；(b) **交接** — 将较早组的 `out` ≤ 较晚组的 `in`，以便只有一个在屏幕上；(c) **故意的分层排版** — 在其中一个组上添加 `"allow_overlap": true` 以静默验证器。验证器根据其CSS估计每个组的垂直bbox并标记冲突。默认选择 (a) — 它是让cinematic-cream感觉像诗积累，而不是字幕轨道替换自己的东西。

- **HyperFrames CLI：** 插件安装使用捆绑的 manifest-pinned 启动器。源代码贡献者可以通过 `HYPERFRAMES_ROOT`、技能的源代码树或 `~/Downloads/hyperframes` 使用构建好的 checkout (`packages/cli/dist/cli.js`)。
- **以 Node.js 优先；通过 `uvx` 提供 Python 两个接触点（无需手动安装）：** 转录通过 `uvx` 运行 WhisperX（单词级别的计时；根据技能 §transcription 回退），而 Theme 的 `drawon` 部件在编译时设置 `python3 scripts/gen-stroke-path.py`。其他所有内容都在 hyperframes 已经提供的工具链上运行：matting 通过 hyperframes CLI 的 **`remove-background`**（u2net_human_seg；权重一次性自动下载，约 168 MB，到 `~/.cache/hyperframes/`），图像/alpha 计算 via **`sharp`**，布局/遮挡/溢出 via **`puppeteer`**，以及 **`ffmpeg`**。按照上述 **运行时先决条件** 中描述的方式在标题项目中安装 Sharp、Puppeteer 和 GSAP。助手会首先检查该项目，并为源代码贡献者保留 checkout 依赖项查找。
- **转录 = 通过 `uvx` 的 WhisperX**（单词级别的计时 + 对齐；无需手动安装 — `transcribe.cjs` 驱动 `uvx whisperx`）。如果存在，则回退到现有的单词级别 `transcript.json`。
- **源视频** — `matte.cjs` / `transcribe.cjs` 自动解析 `source.mp4`（或全局搜索片段 / 读取 `hyperframes.json`），因此 `hyperframes init --video X.mp4` 无需手动重命名。
- **fps** — `matte.cjs` 以源码的原始速率提取并记录 `matte.fps`；`render-and-composite.sh` 使用该值，以便 matting 保持帧对齐。
- Matting 权重未捆绑：`matte.cjs` 调用 hyperframes CLI 的 `remove-background`，该命令一次性下载 u2net_human_seg (~168 MB，Apache-2.0) 到 `~/.cache/hyperframes/background-removal/models/`。首次在全新机器上准备时需要网络下载这一个文件。

如果缺少硬依赖项，请停止并提示用户 — 不要静默跳过步骤。
