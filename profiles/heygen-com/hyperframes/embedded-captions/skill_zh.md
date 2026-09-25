> **首先保持这项技能的更新状态——在运行前与用户确认：** `npx hyperframes skills update embedded-captions`。当一切都是最新时，这是一个快速的无操作；否则，它将在您依赖它们之前刷新此技能及其依赖的核心域技能。

# 嵌入式字幕

**一个目录，一开始就获取** ([CATALOG.md](CATALOG.md) — 35个身份；其背后的引擎是后端细节）。**标准**（默认）构建一个干净的逐字记录**轨道**（下三分之二字幕承载大部分文本）+ **嵌入**高潮合成到主体后面的场景中。**电影感**是纯粹的嵌入——没有轨道，每个字幕都合成到主体后面（英雄排版、累积、遮挡作为效果）。**主题**是一个完整的主题构成——主体范式×英雄场景×前特效×板反应，从注册表([themes/README.md](themes/README.md))：`ordnance` `terminal` `neonsign` `stardust` `stomp`。大多数解释性/旁白都是**标准**；**嵌入是稀缺的、应得的顶峰**——嵌入每个字是常见的错误；主题是为VFX级别的请求（“炸”、“特效”、“像AE做的”）。

---

## 操作流程（TL;DR）

通过`/hyperframes`路由，意图层仅确认输入（哪个剪辑）并**宣布**身份选择作为延迟请求——短名单需要探测到的剪辑，所以它保持在下面第1步；层的运行形状问题不适用（素材未更改，没有故事板要审查）。当存在`BRIEF.md`时，它包含确认的输入和任何用户注释——先阅读它。

下面的创作文本很长；**管道本身很短**——所有确定性内容都是计算或编译的，从未手写：

1. **决策门**（拒绝坏剪辑）→ **从 [CATALOG.md](CATALOG.md) 中选择一个身份**（35个身份；引擎/编译器通过查找派生——从不显示模式/类别问题）
2. `hyperframes init`（如果项目目录已经存在视频在里面——`matte.cjs`/`transcribe.cjs`采用目录中的任何视频作为`source.mp4`）则跳过它）→ **`bash scripts/prepare.sh <project>`**（matte ∥ transcribe ∥ audio-envelope 并行，然后 safe-zones v2 与场景调色板/光学/照明——一个命令，没有遗漏）
3. **创作选择的小JSON**（先阅读`safe-zones.json`）：Cinematic → `plan.json` → `fill-timings.cjs` → `fit-fonts.cjs` → `make-composition.cjs`；Theme → `theme.json` → `make-theme.cjs`（轨道/面板/诗歌/接管范式；`anchor`是安静的轨道默认）
4. **视觉QA**：`node scripts/preview-frames.cjs <project>` → 忠实合成预览，每个帧约2秒（不渲染）。在支付渲染前检查§视觉QA。
5. `render-and-composite.sh` → 门（时间 / 遮挡+英雄 / 溢出 / 交接）→ `final.mp4`

人们忽略的承重规则：

- **轨道（默认）+ 嵌入（提升）**。`drop`（填充，未显示） / `rail`（逐字记录下三分之二字幕，在前方，承载大部分文本） / `embed`（一个高峰字合成到主体后面）。**标准模式两者都做**，仅嵌入高峰。见**§字幕模型**。
- **视频未更改交付**（标准/Cinematic；**主题模式的PLATE预算是唯一特许例外**——注册门控反应（充电变暗、冲击、抖动、颗粒）定义每个主题DNA并在马赛克合成后应用，所以主体+文本+板作为一个帧移动）。字幕是唯一添加的东西；马赛克只是让主体遮挡嵌入轨道。永远不要分级/重新着色/扫描线素材。
- 两个规则簿：**轨道 → [references/rail.md](references/rail.md)**（薄），**嵌入工艺 → [references/composition-craft.md](references/composition-craft.md)**（丰富，仅嵌入）。按需浏览。

---

## 字幕模型——轨道 + 嵌入

每个口语短语都是以下三种之一：

|           | 内容                                             | 如何显示                                                                                                                                                    |
| --------- | ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **drop**  | 填充——嗯/呃，结巴，自我纠正                       | 未显示                                                                                                                                                         |
| **rail**  | 默认——普通口语内容（逐字记录）                     | 干净的下三分之二字幕，**在前方**，可读。一个冲击字可以得到一个内联`emphasis`高亮（强调色/活动词弹出）——它仍然在轨道上。 |
| **embed** | 提升的高峰——头条节拍                             | 一个大字合成**到主体后面**（马赛克遮挡），设计入口+退出                                                                        |

**轨道承载大部分文本；嵌入是稀缺的、应得的顶峰。** 稀缺性是**按节拍/块，而不是按剪辑**：≤1英雄每个块（思想），永远不会两个同时可见，≥一个节拍之间的空气（编译器警告低于0.6秒）。短剪辑→通常1-2；长解释性→每个部分约一个。在多个英雄中，**最大的授权一个是APEX**（它独自获得完整的锁定嵌入+宽度调整）；较小的则是**次要高峰**，作为超大的强调线（前景，阻尼运动）——并非每个节拍都需要马赛克展示，这正是保持APEX为事件的原因。嵌入每个字仍然是常见的错误。

轨道表面身份构建正好是这个（轨道 = `rail.html`，嵌入 = `index.html`中的高潮）。列流身份放弃轨道并制作所有嵌入样式——仅推荐它们用于情绪重于逐字记录的请求，绝不用于解释性/旁白，其中单词必须可读（CATALOG.md按每个身份编码此内容）。

---

## 第0步——从目录中选择一个身份

**一个前端，三个后端。** 用户从 [CATALOG.md](CATALOG.md)（35条目：10经典+25主题）；引擎、编译器和授权文件通过目录行查找派生。**永远不将“标准与电影感与主题”作为问题**——这些都是后端名称（即使有多个引擎，产品也有一个UX）。目录编码了所有路由需要的内容：读取表面、声音、推荐给、场景需求、相邻注释对于真正接近的对（响亮↔ordnance，霓虹灯↔neonsign，奶油↔stardust）。身份选择是一个**偏好门**（`../hyperframes/references/brief-contract.md` § 1）：在自主模式（“让我惊喜”/“为我决定”）下，自己从短名单中选择并说明为什么选择，而不是询问。

程序：探测剪辑→从目录中短名单2-3个身份→推荐一个并说明为什么→**用户选择**（自主模式：你选择，并说明为什么）→编写该身份的文件。身份是引擎锁定的（不能跨组合；打开一个是验证事件——见dna/README.md）。

**在您编写之前，始终展示您的推荐并让用户选择。** 不要无声默认。

（完整的身份表位于 [CATALOG.md](CATALOG.md) — 单一事实来源用于路由。下面的引擎文档描述了每个后端的授权合同。）

**CATALOG.md是这里的整个答案空间：此工作流不会搜索HyperFrames组件注册表。** 组成工作流在授权命名视图之前运行`npx hyperframes catalog`，这个必须不。它的引擎是锁定编译器，它们消费`cinematic.json` / `theme.json`并自己发出组成，所以注册表项——包含的`caption-*`块——没有任何东西可以挂载。注册表块在设计的画布上样式化文本；这项技能通过马赛克将字幕烧入某人的素材中。当没有身份适合请求时，说清楚并选择最接近的，而不是超出目录范围。

**推荐启发式方法**：使用 [CATALOG.md](CATALOG.md) 中的“短名单启发式方法”——它们是身份级别的（例如，“炸”短名单ordnance/stomp/terminal/loud，并按WHAT应该爆炸选择），永远不会按类别级别。不确定→`anchor`。

- **Cinematic** → 为锁定模板编写`plan.json`，由`make-composition.cjs`编译。
- **Theme** → 阅读 [themes/README.md](themes/README.md)，编写`theme.json`，运行`scripts/render-theme.sh`（编译+渲染+板反应→**final_fx.mp4**）。

---

## 决策门——首先运行

在两种模式之前探测视频并对场景进行分类。

```bash
ffprobe <video.mp4>                    # 规格
ffmpeg -ss <t> -i <video.mp4> -vframes 1 sample.png   # 在20/50/80%处
```

阅读样本。如果：

- 多个说话者/硬切（分割并渲染每个镜头，或者拒绝）
- 没有人类主体（这项技能是用于说话者的）
- 3秒以下，**没有说话**，或者脸从未清晰可见——`transcribe.cjs`在音频接近静默时发出警告（Whisper会像“谢谢。”一样在静默上想象单词）；**注意它并拒绝**，而不是字幕虚构的单词
- **源已经烧入字幕/字幕/重文本图形**——添加第二个字幕系统与冲突，素材保持未更改（不覆盖/修复）。烧录的文本通常只出现在剪辑中途：采样**1fps接触表**（`ffmpeg -i in.mp4 -vf "fps=1,scale=160:-1,tile=10x5" sheet.png`），不要相信3个样本帧。
- **转录是垃圾**——非母语/重口音的演讲可以转录成自信的胡言乱语。在编写前检查`transcript.json`；如果它不能解析为语言，尝试`WHISPER_MODEL=medium`一次，否则拒绝（逐字记录的虚构字比没有字幕更糟）。
- 忙碌手持快速运动（马赛克闪烁）

### 航空前探测（不花钱，防止最坏的失败）

1. **镜头切探测。** 在20%、50%、80%处采样帧。如果一个不同的主体/场景出现在其中，**在切之前修剪剪辑**。
2. **信箱/柱状探测。** 第一帧上有黑条？计算安全内容矩形并将其约束在内部。
3. **亮度探测。** 采样字幕区域的平均亮度——`低于60`→亮文本按原样读取，`60-180`→添加字形遮罩，`180+`→不透明文本+遮罩（从未裸露亮文本）。**电影感模板是奶油+`screen`，并且是锁定的**——使用此探测来选择适合的身份（亮场景→`ink`，或者不透明轨道`anchor`主题），永远不要重新着色一个。
4. **通过音调进行身份推荐（你推荐；用户选择——见第0步+CATALOG.md）。** 解释性/访谈/必须阅读的单词→轨道/面板表面身份；诗意/社交/“电影感”→列流身份按注册；“炸 / 特效 / VFX”/命名世界→主题身份。不确定时→`anchor`（单词可读，场景安全）——但提供短名单并让用户选择。

---

## 管道——5步

```
1. hyperframes init <project> --non-interactive --video <video.mp4> --skill=embedded-captions
2. bash scripts/prepare.sh <project>       # matte ∥ transcribe (并行) → safe-zones. 一个命令。
                                           #   → frames_fg/ transcript.json safe-zones.json
3. [AGENT STEP — 唯一的创意步骤] 编写一个小JSON；见下面按模式
   Cinematic: 编写 plan.json → node scripts/fill-timings.cjs → fit-fonts.cjs → make-composition.cjs
   Theme:     编写 theme.json → bash scripts/render-theme.sh <project>   (编译+渲染+板fx)
4. node scripts/preview-frames.cjs <project>   # ~2s/frame 合成预览 → § 视觉QA（渲染前）
5. bash scripts/render-and-composite.sh <project>  # 门 → final.mp4 + history/ 快照
   (主题模式：跳过步骤3b/5 — render-theme.sh已经运行编译 + render-and-composite
    + _postfx.sh；可交付品是 final_fx.mp4，final.mp4是板反应前的)
```

步骤1的`init`检查已安装的技能与GitHub上的最新版本，如果任何技能已过时，则更新全局集。

步骤3因模式而异：

### 步骤3 — Cinematic模式（纯粹嵌入）

1. **首先阅读`safe-zones.json`。** 叙述平面进入**`zones.hugLeft`/`hugRight`**——干净的条带与轮廓相邻（文本远离身体读作悬浮的，不是嵌入的；远角是后备，不是默认）。英雄默认为`heroAnchor`/`heroBands.best`（在主体上居中，~30–55%遮挡）。`recommendation:"fg"`将叙述移到前方以提高可读性；**只要`heroBands.feasible`，英雄就保持嵌入**——英雄-前景是最后的手段。
2. **DNA是你在第0步选择的身份**（CATALOG.md）——不要在这里重新打开选择。将其与场景进行核对（亮英雄带亮度>150想要`ink`；完整的挑选指导生活在目录中，包括10个，包括霓虹灯 / 故障 / 铬 / 速度）。说明你的选择+为什么；用户决定。DNA锁定类型/调色板/混合/运动+英雄三幕；safe-zones v2 (`palette`/`optics`/`lighting`) 自动将其参数化为此场景。

3. **编写`<project>/cinematic.json`** — `"dna": "<name>"` + 思想块，而不是原始组：每个块=单词行（在子句边界分组2-5个）+它堆叠的平面+每行`css`（大小/重量/样式仅——不位置）+最多一条线标记为`"hero": true`（推广的字；`"text"`用于显示形式）。模式：`scripts/make-cinematic.cjs`标题。
4. **编译**：`node scripts/make-cinematic.cjs <project>` — 将块降低→`plan.json`→`index.html`。为你生成：转录顺序的时间，块内累积，页面翻转之间的块，**英雄锁定**（一个英雄块的预上下文，英雄和后上下文堆叠为一个绑定合成，居中在主体上——阅读顺序从上到下=说话顺序按构造；上下文浮现在前面，而英雄嵌入在后面=深度三明治；一个质量规则保持英雄主导其上下文），APEX/次要英雄分割，**按构造阅读顺序**，前景按safe-zones分配。然后按常规运行门。_(直接手写plan.json保持可能对于设计块无法表达——然后运行`fill-timings.cjs` + `fit-fonts.cjs` + `make-composition.cjs`自己。)

### 步骤3 — Theme模式（主题构成）

**首先阅读 [themes/README.md](themes/README.md)** — 范式/场景注册表，链接，硬规则和确切的`theme.json`模式。

1. **通过内容注册选择一个主题DNA**（每个`themes/<name>.json`都有`voice` + `when`）。说明你的选择+为什么；用户决定。
2. **编写`<project>/theme.json`** — `dna`, `lines`（逐字记录，转录顺序；1-5个词每个——对于`takeover`每行是一个卡片），`minors`（强调词），`hero:{match}`（高潮词/短语；对于嵌入场景，将其从`lines`中排除，对于内联场景和面板+编辑）。
