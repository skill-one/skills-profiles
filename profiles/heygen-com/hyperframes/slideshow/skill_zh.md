> **首先，保持该 skill 的新鲜度——在运行之前与用户确认：** `npx hyperframes skills update slideshow`。当所有内容都最新时，这是一个快速的无操作；否则，它会在依赖它之前刷新该 skill 及其核心领域 skill。

> **figma 来源**：如果幻灯片的內容或分镜来自 figma.com 的 URL，请先运行 `/figma` —— 导出资源、品牌标识符（brand tokens）以及分镜重建（如果是场景帧的条带）——然后基于其输出进行构建。不要通过原始 MCP 工具直接驱动 Figma：这会导致跳过 SVG 净化、`.media/manifest.jsonl` 溯源，以及品牌标识符 `var()` 绑定，因此稍后的品牌变更无法在完整重新导入前传播。

# 演示文稿（Slideshow）创作契约

HyperFrames 演示文稿是一个正常的 HyperFrames 组合 —— 场景、片段（clips）、GSAP 时间线 —— 并包含一种额外成分：一个**JSON 岛屿**（JSON island），它声明哪些场景是幻灯片以及如何连接。播放器的 `SlideshowController` 读取该岛屿，并将连续的 GSAP 时间线转换为离散、可导航的演示文稿。

**首先阅读 `/hyperframes-core`**，了解基础组合契约（片段、轨道、`data-*` 属性、确定性规则）。该 skill 仅涵盖新增内容：岛屿模式、幻灯片编写规则、片段、分支、校验，以及包装组件。

## 输出 —— 可导航的演示文稿，而非线性 MP4

演示文稿的输出是**运行中的演示文稿**：使用 `hyperframes present <project-dir>`（或 Studio present 模式）提供它 —— 播放器的 `SlideshowController` 读取岛屿并驱动导航、片段、分支和演示者模式。请参阅下方的**呈现与交接**。

**不要**将演示文稿通过 `hyperframes render` 渲染为单一的 MP4。演示文稿作为多个顶层场景组合（每页幻灯片一个 `data-composition-id`）编写，**没有**将它们包裹在一起的母根组合（master-root composition），因此 `render` 仅解析**第一**个组合并输出一个**静默截断**的 MP4（例如，40 秒的演示文稿只输出 6 秒）。线性主线导出（仅主线幻灯片，排除分支序列）被**推迟** —— 在它发布前，支持的输出是实时的 `present` 演示文稿和每页幻灯片的 `snapshot` 静态图。如果用户需要线性 MP4，请展示这一限制，而不是将 `render` 指向演示文稿。

## 意图确认

如果用户明确要求创建演示文稿、幻灯片展示，或 HyperFrames 演示文稿，则按本 skill 执行。当请求通过 `/hyperframes` 到达时，意图层的分诊（triage）负责此确认 —— 路由到此意味着已确认，因此不要重新询问；该层的运行形态问题不适用（交付物是演示文稿，而非渲染视频）。若存在 `BRIEF.md`，其中包含已确认的意图，请读取它。

如果 skill 从相邻请求（如“演示”、“演示文稿/路演”、“演示稿”、“交互式演示稿”，或“转换此页面”）触发，请在编写前暂停，并在询问确认前阐明选择。简要说明 HyperFrames 演示文稿意味着一个可运行的演示文稿，具有离散幻灯片、内置导航和演示者模式、可编辑的演讲者备注、共享媒体处理，以及交接前的校验。对于源页面转换，还提及目标是保留原始页面的视觉设计、交互、动效和媒体行为，同时将页面移动转化为幻灯片间过渡。

然后提出简短的确认问题：

> 你是要将其作为 HyperFrames 演示文稿吗？

若环境提供选项，请使用是/否选项 UI；否则以纯文本询问该问题。

**不要**在用户确认前实现演示文稿。若用户说否，则停止使用本 skill —— 阅读 `/hyperframes` 并让意图层重新路由。此确认是**路由决策**，而非偏好门控 —— 根据 `../hyperframes/references/brief-contract.md` § 1，它在自主模式下依然有效（“让我惊喜”不会跳过它）：构建错误的交付物类型是质量失败，而非创意选择。

---

## 两部分内容

### 1. 场景 —— 以常规方式声明

每页幻灯片由一个场景支持。使用 `data-composition-id`、`data-start`、`data-duration` 和 `data-label` 声明场景：

```html
<div
  data-composition-id="problem"
  data-start="0"
  data-duration="8"
  data-label="The problem"
  data-width="1920"
  data-height="1080"
>
  <!-- clips 在此处 -->
</div>
```

分支幻灯片（只能通过热区触发，排除在主线外）以完全相同的方式声明 —— 它们仅在岛屿的 `slideSequences` 条目中出现，而不在主线 `slides` 数组中。

### 2. JSON 岛屿 —— 每个组合一个脚本块

在组合的 HTML 中添加**恰好一个** `<script type="application/hyperframes-slideshow+json">` 块。它包含所有演示文稿元数据：

```html
<script type="application/hyperframes-slideshow+json">
  {
    "slides": [...],
    "slideSequences": [...]
  }
</script>
```

岛屿是幻灯片顺序、备注、片段停驻点、热区 and 分支序列的**唯一事实来源**。将其放在 `<body>` 的顶部附近，在场景 div 之前，以便容易查找。

**不要**将演示文稿清单藏在额外的 `<script type="application/json">` 块与运行时代码后面，后者创建岛屿。`present` 命令静态读取组合 HTML，并期望真正的 `application/hyperframes-slideshow+json` 岛屿已经存在。

---

## 模式（Schema）

### `SlideshowManifest`（岛屿顶层对象）

```json
{
  "slides": [
    /* SlideRef[] — 主线，按顺序 */
  ],
  "slideSequences": [
    /* SlideSequence[] — 线下分支序列 */
  ]
}
```

### `SlideRef`

```json
{
  "sceneId": "problem",
  "notes": "以痛点开场，而非公司。",
  "fragments": [3.5, 5.2, 7.0],
  "hotspots": [
    /* SlideHotspot[] */
  ],

  "ttsScript": null,
  "ttsAudioUrl": null,
  "ttsDurationMs": null
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `sceneId` | 是 | 必须与场景的 `data-composition-id` 完全匹配（或提供显式的 `startTime`/`endTime`）。校验规则通过 `data-composition-id` 解析场景。 |
| `notes` | 否 | 仅演示者使用。绝不向观众显示。 |
| `fragments` | 否 | 幻灯片 `[start, end]` 范围内的数组时间（秒）—— 见下文 Fragments。 |
| `hotspots` | 否 | 触发分支的交互覆盖层 —— 见下文 Branching。 |
| `startTime` | 否 | 可选。覆盖匹配场景的时间范围；默认为场景的 start/end。 |
| `endTime` | 否 | 可选。覆盖匹配场景的时间范围；默认为场景的 start/end。 |
| `ttsScript`、`ttsAudioUrl`、`ttsDurationMs` | 否 | **保留字段**。模式字段存在，但尚未接入 TTS 播放。除非为未来构建预填充，否则省略。 |

### `SlideHotspot`

```json
{
  "id": "h1",
  "label": "我们是如何计算这个的？",
  "target": "market-deep-dive",
  "region": { "x": 60, "y": 10, "w": 35, "h": 20 }
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | 是 | 在幻灯片内唯一。 |
| `label` | 是 | 向观众显示的工具提示 / 按钮文本。 |
| `target` | 是 | 必须匹配 `slideSequences` 中定义的 `SlideSequence.id`。 |
| `region` | 否 | 相对于幻灯片边界框的百分比：`{x, y, w, h}`，取值范围 0–100。省略时，热点渲染为全幻灯片带标签的按钮。 |

### `SlideSequence`

```json
{
  "id": "market-deep-dive",
  "label": "市场规模方法论",
  "slides": [{ "sceneId": "mkt-1" }, { "sceneId": "mkt-2" }]
}
```

`slideSequences` 中序列内的 `slides` 使用与主线相同的 `SlideRef` 形状。允许包含片段和嵌套热区。

---

## 幻灯片编写规则

这些是**硬性约束**，而非建议。违反这些约束的幻灯片将在评审时被直接替换。

- **标题是完整句子的主张，而非标签。** 编写“SMBs 每周在手动排期上浪费 14 小时”，而非“排期问题”。如果忽略视觉，该句子应能独立成立。
- **每页幻灯片一个想法 + 一个视觉。** 若你倾向于添加第二个要点簇或第二个图表，请拆分该页。
- **以结论先行。** 最强观点放在第一——在幻灯片和演示文稿顺序中均如此。投资者从左到右、从上到下阅读，他们会在某处停下来。
- **仅底部向上的市场规模（bottom-up market sizing）**。除非展示计算过程，否则绝不写“$50B TAM”。从单位经济（unit economics）向上构建：账户 × ACV，或交易 × 抽成比例（take-rate）。
- **字体最小 30pt 等价。** 在 1920×1080 分辨率下，标题为 72–96px；正文为 48px。任何观众必须阅读的文本，绝不低于 40px。
- **在构建任何具名视觉之前，先搜索实时目录。** 每页幻灯片需要的任何视觉效果、效果、图表、处理方式或过渡——“CRT 扫描线”、“glitch”、“柱状图竞速”、“ shimmer sweep”、“终端窗口” —— 运行 `npx hyperframes catalog --query "<视觉，用通俗英语描述>" --json` 并阅读顶部结果，再编写幻灯片片段。搜索**无需安装任何内容**：无需项目、无需先前的 `add`、无需账号。它从任意目录排名整个托管注册表（约 400 个块和组件）。`npx hyperframes add <名称>` 将块的源文件放入演示文稿，你可以在其中就地自定义它。将源页面转换为幻灯片时，此规则以更强力度适用：真实块优于转换规则禁止的简化近似。

## 源页面转换

将现有页面转换为演示文稿时，源保真度是契约的一部分。除非用户明确要求重新设计，否则不要用简化的近似替代源页面特有的组件。

- 尽可能保留原始页面的视觉设计、动效语言、交互行为、媒体行为和展示功能。当演示文稿系统支持演示者模式时，包含使用共享可编辑备注行为编写的演讲者备注，而非演示文稿特定的实现。
- 尽可能精确地从源 DOM/CSS/JS 移植机械视觉：自定义播放器、canvas 可视化器、时间线、播放头、轨道（stems）、扩展圆圈、悬停状态以及其他交互细节应在转换后得以保留。
- 将原生的 `<video>` / `<audio>` 元素视为任何自定义媒体外壳、canvas 可视化器、波形、节拍网格或播放头的**事实来源**。接入源的媒体事件（`play`、`pause`、`timeupdate`、`seeking`、`seeked`、`ended`、`ratechange`、`volumechange`）并从 `media.currentTime` 派生视觉状态；不要运行与实际操作播放可能漂移的独立计时器。
- 每个带有 `src` 的复制 `<video>` 或 `<audio>` 在通过 lint 之前，必须已有 HyperFrames 计时属性：`data-start` 和 `data-duration`，以及当应保持可听原声音频时 `data-has-audio="true"`。使用幻灯片的特定时间范围作为幻灯片内媒体；对于用户控制的证据视频，若可能从多个聚焦幻灯片播放，则使用演示文稿级的范围。不要在原声媒体上保留 `preload="none"`；使用 `metadata` 或 `auto`。
- 在验证前解析源字体令牌。若保留源的自定义字体，添加 `@font-face` 规则以支持本地/捕获的字体文件。若使用系统回退，将分词声明（如 `font-family: var(--f-body)`）替换为具体且渲染安全的堆栈，如 `system-ui, sans-serif` 或 `ui-monospace, monospace`；不要将 `var(...)` 作为字体族值保留。
- 审计源页面中异常页面移动行为，特别是由滚动、滚轮、触摸、哈希状态、调整大小或 `requestAnimationFrame` 循环驱动的行为。将固定视口上带有平移/缩放“世界”层的视差、固定面板、水平滚动条、滚动擦洗时间线、章节吸附和缩放至元素摄像机作为源行为处理。滚动通常是源的过渡触发器，因此通过提取其进度停驻点、缓动和摄像机/焦点状态来保留过渡，然后在演示文稿导航中通过时间线位置、片段或可复用播放器/框架钩子重新托管该动效。独立包装器跳转至幻灯片停驻点的仍需显式的导航摄像机过渡钩子；单独计算每页幻灯片摄像机变换不足以解决问题。不要在幻灯片内模拟字面的页面滚动向下过渡；观众应感受到从一个焦点点到另一个焦点点的摄像机移动/缩放，而非看到网页被滚动。保持每页幻灯片间摄像机移动连续：避免在源在同一边界处可见地进行 x/y 方向反转或缩放时，中途设置倒退的中间路线停驻点。在落地前晃动过渡比更简单的直接焦点移动更差。
- 保留源媒体的裁剪语义。将截图、推文/社交帖子、产品 UI 捕获、图表、文档、代码、排行榜以及任何带有可读文本的图片视为内容证据，而非装饰媒体：在稳定框架内使用源的宽高比（`height: auto`）或 `object-fit: contain`。仅在源本身裁剪，或用于故意装饰/背景/电影感缩略图时，使用 `object-fit: cover`。将此类捕获适配到幻灯片后，检查所有四个边缘是否有被截断的文本、标志、控件或字幕；在有意义内容上有可见裁剪是 bug，除非源本身裁剪过。
- 若某行为是演示文稿通用的，则放入播放器/控制器或可复用 skill 片段中。不要用一个一次性的演示文稿脚本解决它。
- 堆叠的场景帧绝不能阻塞活动幻灯片上的交互。隐藏的帧需要视觉隐藏和事件门控同时满足：

```css
.scene-frame {
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}

.scene-frame.is-active {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}
```

若可见性由命令式驱动，则在可见性控制器中同时设置所有三个属性（`opacity`、`visibility` 和 `pointerEvents`）。仅 `opacity: 0` 仍会留下一个不可见层，可能吞没点击。

---

## 片段（Fragments）：在幻灯片内揭示停驻点

片段是幻灯片 `[start, end]` 范围内绝对的组合时间线时间（秒），控制器应在该处保持揭示状态。

**工作原理：**

1. 播放器进入片段幻灯片 —— 直接跳转到 `fragments[0]` 并保持驻留。
2. 用户按 Next（或 →）—— 控制器跳转到 `fragments[1]` 并保持驻留。
3. 最后一个片段之后，Next 推进到下一页幻灯片。
4. 没有片段的幻灯片在幻灯片内的静止帧进入，通常在其中点，而非正好在 `slide.end`。

片段时间必须落在 `[start, end]`（含两端边界）内。lint 规则仅拒绝超出该范围（`time < start` 或 `time > end`）的片段。

片段时间是**绝对的组合时间线位置** —— 与 `data-start` 相同的坐标空间 —— 而非相对于场景起始的偏移。

导航由 seek（跳转）驱动，而非播放驱动。控制器从不仅为在片段间移动而启动播放；每次导航命令都是确定性跳转到目标停驻时间。请设计片段状态，使其在目标时间线时间处正确。

---

## 分支：热区与幻灯片序列

分支幻灯片是组合时间线中的真实场景。它们仅在 `slideSequences` 下列出，并排除在主线导航之外 —— 播放器不会在热点触发之前访问它们。

**导航模型：**

- 点击热点将 `{sequenceId, slideIndex: 0}` 压入导航栈，并进入分支的第一页幻灯片。
- **back()** 弹出栈并返回至精确的上层幻灯片（即放置热区的那页幻灯片）。
- **backToMain()** 清除整个栈并返回至根幻灯片。
- 面包屑渲染自栈：`主线演示文稿 › 市场规模方法论 › 第 2 页`。
- 分支内的幻灯片计数器以该序列为范围（`1 of 2`，而非主线总页数）。

**应避免的做法：**

- 不要将分支场景 ID 加入主线 `slides` 数组。它们必须仅出现在 `slideSequences` 条目内。lint 规则标记重叠。
- 分支场景包含在连续时间线中，因此朴素的线性视频导出会包含它们。导出仅读取主线幻灯片（推迟；在规范中标记）。

---

## 示例：3 页演示文稿，带片段和分支

### 场景 HTML（骨架）

```html
<body style="margin: 0">
  <script type="application/hyperframes-slideshow+json">
    {
      "slides": [
        {
          "sceneId": "hook",
          "notes": "以数据开场。在 $40B 数字上暂停。"
        },
        {
          "sceneId": "problem",
          "notes": "逐一走查每个痛点。",
          "fragments": [11.0, 15.0],
          "hotspots": [
            {
              "id": "h1",
              "label": "这个 $40B 数字来自哪里？",
              "target": "market-detail",
              "region": { "x": 55, "y": 60, "w": 40, "h": 20 }
            }
          ]
        },
        {
          "sceneId": "solution",
          "notes": "一句话：我们做什么，面向谁。"
        }
      ],
      "slideSequences": [
        {
          "id": "market-detail",
          "label": "市场规模方法论",
          "slides": [{ "sceneId": "mkt-math", "notes": "自下而上：2.3M SMBs × $17k ACV。" }]
        }
      ]
    }
  </script>

  <!-- Slide 1 — hook -->
  <div
    data-composition-id="hook"
    data-start="0"
    data-duration="6"
    data-label="The hook"
    data-width="1920"
    data-height="1080"
    style="position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #0a0a0a"
  >
    <section
      class="clip"
      data-start="0"
      data-duration="6"
      data-track-index="1"
      style="position: absolute; inset: 0; display: grid; place-items: center"
    >
      <h1 id="hook-headline" style="font-size: 80px; color: #fff; font-family: sans-serif">
        SMBs 因手动排期每年损失 $40B
      </h1>
    </section>
  </div>

  <!-- Slide 2 — problem（3 个片段） -->
  <div
    data-composition-id="problem"
    data-start="6"
    data-duration="15"
    data-label="The problem"
    data-width="1920"
    data-height="1080"
    style="position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #0a0a0a"
  >
    <section
      class="clip"
      data-start="6"
      data-duration="15"
      data-track-index="1"
      style="position: absolute; inset: 0; padding: 120px 160px; box-sizing: border-box"
    >
      <h2 id="pain-headline" style="font-size: 64px; color: #fff; font-family: sans-serif">
         operators 无法关闭的三个缺口
      </h2>
      <p id="pain-1" style="font-size: 48px; color: #ccc; opacity: 0; font-family: sans-serif">
        No-shows 消耗了 23% 的已订收入
      </p>
      <p id="pain-2" style="font-size: 48px; color: #ccc; opacity: 0; font-family: sans-serif">
        手动提醒：每位员工每周耗时 4h
      </p>
      <p id="pain-3" style="font-size: 48px; color: #ccc; opacity: 0; font-family: sans-serif">
        Rescheduling 摩擦导致 40% 的流失
      </p>
    </section>
  </div>

  <!-- Slide 3 — solution -->
  <div
    data-composition-id="solution"
    data-start="21"
    data-duration="8"
    data-label="The solution"
    data-width="1920"
    data-height="1080"
    style="position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #0a0a0a"
  >
    <section
      class="clip"
      data-start="21"
      data-duration="8"
      data-track-index="1"
      style="position: absolute; inset: 0; display: grid; place-items: center"
    >
      <h2 id="solution-headline" style="font-size: 72px; color: #fff; font-family: sans-serif">
        Acme 为服务类 SMBs 自动化排期 —— 90 天内 No-shows 降低 80%
      </h2>
    </section>
  </div>

  <!-- 分支幻灯片 —— 排除在主线之外 -->
  <div
    data-composition-id="mkt-math"
    data-start="29"
    data-duration="7"
    data-label="Market math"
    data-width="1920"
    data-height="1080"
    style="position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #111"
  >
    <section
      class="clip"
      data-start="29"
      data-duration="7"
      data-track-index="1"
      style="position: absolute; inset: 0; display: grid; place-items: center"
    >
      <p id="mkt-formula" style="font-size: 56px; color: #fff; font-family: sans-serif">
        2.3M SMBs × $17k ACV = $39B 可服务市场
      </p>
    </section>
  </div>

  <script>
    window.__timelines = window.__timelines || {};

    // Slide 2 片段进入动画
    gsap.registerPlugin(); // 使用前注册任何插件

    const tl = gsap.timeline({ paused: true });
    window.__timelines["problem"] = tl;

    // 插入位置是绝对的组合时间线时间（与 data-start / 片段值一致）。
    tl.from("#pain-1", { opacity: 0, y: 20, duration: 0.4 }, 11.0);
    tl.from("#pain-2", { opacity: 0, y: 20, duration: 0.4 }, 15.0);
    // pain-3 在时间线末尾出现
    tl.from("#pain-3", { opacity: 0, y: 20, duration: 0.4 }, 13.0);
  </script>
</body>
```

### 示例关键点

- 岛屿 `sceneId` 值（`"hook"`、`"problem"`、`"solution"`、`"mkt-math"`）与场景 div 的 `data-composition-id` 值完全匹配。
- `mkt-math` 仅出现在 `slideSequences` 中 —— 它从不出现在顶层 `slides` 数组中。
- 片段时间（`11.0`、`15.0`）落在 `problem` 场景的 `[6, 21]` 范围内（时间为绝对的组合时间线位置）。
- 热区 `region`（`x: 55, y: 60, w: 40, h: 20`）将可点击区域定位在 problem 幻灯片的右下象限。
- GSAP 时间线注册到 `window.__timelines` 并处于暂停状态 —— HyperFrames 引擎驱动播放；在构造时不要调用 `.play()`。

---

## 包装组件

在任何嵌入上下文中，用 `<hyperframes-slideshow>` 包裹 `<hyperframes-player>`：

```html
<hyperframes-slideshow>
  <hyperframes-player src="deck.html"></hyperframes-player>
</hyperframes-slideshow>
```

`<hyperframes-slideshow>` 提供导航外壳（Present、上一页/下一页、计数器、存在 `sound` 时的全局静音、全屏）、键盘处理（← / →、Space / Backspace，以及 P 键用于 Present）、触摸滑动，以及热点覆盖层。

`<hyperframes-slideshow>` 在挂载时自动为每个内部 `<hyperframes-player>` 设置 `interactive` 属性，因此演示文稿内的可点击控件、链接、原声媒体控件和自定义播放器能按预期接收指针事件。（在演示文稿包装器之外，必须在 `<hyperframes-player>` 上手动添加 `interactive` —— 播放器默认为 iframe 设置 `pointer-events: none`，否则点击播放器宿主会被劫持为切换时间线播放。）

**演示者模式：** 使用幻灯片导航胶囊中的内置 Present 图标按钮，或按 P 键。它会调用 `window.open('?mode=audience')` 以打开全屏观众标签页；原始标签页变为演示者视图（当前幻灯片缩小、下一页预览、备注、已用计时器）。两个标签页通过 `BroadcastChannel('hf-slideshow:' + location.pathname)` 同步。**不要**添加自定义包装层级的 Present 按钮；共享组件拥有其位置、图标、样式和观众模式隐藏。

**在 Google Meet / Zoom 上进行演示（屏幕共享）：** 共享 _audience_ 表面，将演示者视图保持在您自己的屏幕上。

- **Google Meet（或任何在 Chrome 中的共享）：** Present → 在 Meet 中选择**共享屏幕 → A 标签** → 选择观众标签页 → 切换回演示者标签页。Chrome 在后台时保持捕获的标签页渲染，因此动画和幻灯片导航保持激活。**不要**共享“A 窗口”或“整个屏幕”——完全被覆盖的窗口会停止渲染（对观众而言幻灯片冻结），且整个屏幕会暴露您的备注。
- **Zoom（桌面应用）：** 将观众标签页拖到其独立窗口中并共享该窗口。Zoom 通过操作系统捕获，因此若观众窗口被完全覆盖则会冻结 —— 使用第二块显示器，或在演示者视图后方保留观众窗口的一丝可见区域。

演示者驱动的媒体播放有自动播放策略约束：`BroadcastChannel` 可以同步意图、时间和状态，但无法将演示者的用户激活传输给观众标签页。共享幻灯片播放器镜像原声媒体事件，并先以静音启动远程观众播放；仅在 `media.play()` 被拒绝为静音，或演示文稿明确需要可听观众播放时，才回退到独立框架的观众解锁行为。**不要**在播放被拒绝后继续应用远程 `timeupdate` 消息，否则观众将无声地在视频中跳转而不播放。

演示者备注可在演示者视图中编辑。编辑存储在按演示文稿和幻灯片划分的 `localStorage` 中，叠加在清单备注之上，而不重写组合文件。**不要**为演示文稿添加一次性备注编辑脚本；依赖共享幻灯片播放器的行为。若独立/自定义包装器确实需要在共享播放器之外实现此功能，请使用 `skills/slideshow/references/standalone-harness.md` 中的确定性存储片段。

### 幻灯片退出时的媒体清理

幻灯片控制器拥有幻灯片退出时的媒体清理。当导航更改幻灯片或序列时，它在进入下一页幻灯片前调用 `hyperframes-player.stopMedia()`。该命令：

- 向 iframe 运行时发送 `stop-media`，该命令停止 WebAudio 并暂停原生的 `<video>` / `<audio>` 元素；
- 作为回退方案，直接暂停同源 iframe 媒体；
- 暂停从 iframe 媒体采用的父帧代理。

**同页幻灯片的片段导航不会停止媒体。** 全局/演示文稿级的父音频，如通过 `audio-src` 接入的背景轨道，不被视为幻灯片媒体。

**不要**为普通媒体播放器添加每页幻灯片清理脚本。保持幻灯片视频/音频为组合中的普通媒体；仅在播放器应保留可听原声视频音频而非将其视为无声视觉媒体时，使用 `data-has-audio="true"`。

若源页面将自定义控件或可视化器附加到媒体，这些控件必须监听幻灯片播放器停止和静音的原生元素。由幻灯片退出、演示者同步、原声控件、自定义控件或全局静音按钮触发的暂停，都应通过媒体事件更新可见的自定义 UI，而非通过并行状态。

在实现直接 iframe 回退清理时，将 iframe 媒体视为跨域 DOM。**不要**使用父页面的 `el instanceof HTMLMediaElement` 测试 iframe 节点；在真实浏览器中这返回 false。使用 `el.ownerDocument.defaultView.HTMLMediaElement`（或等效的标签/鸭子类型守卫）在设置 `muted` 或调用 `pause()` 之前。

`hyperframes present` 从 `packages/player/dist` 提供构建好的包。在更改播放器或幻灯片外壳行为后，在 `packages/player` 中运行 `bun run build`，并在浏览器中测试前重启 present 服务器。

---

## 独立运行演示文稿（过渡方案）

**持久的解决方案**是引擎托管：`hyperframes preview --slideshow` / Studio present 模式将组合通过真实的 HyperFrames 引擎托管，引擎驱动 seek 时间线、拥有手势帧，并从组合中读取岛屿。该路径即将到来；一旦发布，请优先使用它。

在此之前，独立演示（通过裸播放器包在浏览器中打开的组合，无引擎）需要解决三个缺口：组合必须暴露可 seek 的根时间线，岛屿必须复制到包装器中，包装器拥有的 SFX/全局音频应位于父帧中。这些模式记录在：

```
skills/slideshow/references/standalone-harness.md
```

**不要**将此处列出的模式视为受祝福的模型 —— 它们仅用于在引擎托管路径落地前的过渡。

## 交接

对于公开的或面向用户的演示文稿项目，根 `index.html` 应为可运行的演示文稿入口。在浏览器中打开时，应显示幻灯片导航并响应 Next/Prev；不应仅暴露原始组合且要求用户了解 Studio 或内部包装文件。若原始 HyperFrames 组合必须为 CLI 兼容性保持独立，则将其放在如 `composition/index.html` 的子目录中，并将脚本/命令指向该目录。

直接打开包装器必须依赖 `<hyperframes-slideshow>` 渲染的内置 Present 图标按钮。**不要**添加定制的 `#present-btn`、固定位置按钮或包装特有的 Present 样式。共享组件拥有控制栏、在 `?mode=audience` 下隐藏 Present，并支持 P 作为键盘快捷键。

在交接前验证直接打开路径。若 `file://` 浏览器限制破坏 iframe 媒体、本地脚本或同源播放器访问，则使用自包含包装器或让交接命令启动本地服务器并打开工作 URL；**不要**在 `index.html` 处于损坏或模糊状态时交接。

对于已完成演示文稿的演示文稿，主要的面向用户的下一步是演示者模式，而非 Studio。运行或提供：

```bash
npx hyperframes present <project-dir>
```

Studio/`preview` 对编辑组合有用，但不是演示文稿用户的明确最终目的地。若为演示文稿项目创建 `package.json`，且原始组合位于 `composition/` 中，请让默认运行脚本启动演示者模式：

```json
{
  "scripts": {
    "dev": "npx hyperframes present ./composition",
    "studio": "npx hyperframes preview ./composition --background"
  }
}
```

在交接时，包含命令打印的本地演示者 URL 和最少指令："点击 Present，或按 P 键，以打开观众标签页。" 若用户将要在 Google Meet 或 Zoom 上演示，也传递上方 Presenting 部分中的屏幕共享指导（在 Meet 中共享观众标签页；在 Zoom 中拖出观众窗口）。若用户要求你启动服务器，请保持服务器运行。

---

## 校验

编写或编辑演示文稿组合后，运行：

```bash
npx hyperframes lint
```

然后运行运行时校验：

```bash
npx hyperframes check
```

将 lint 错误和校验 `StaticGuard` 契约消息视为阻塞性，即使命令成功退出。修复文件并重新运行，直到 lint 报告 `0 error(s)` 且校验报告无运行时错误。

幻灯片 lint 规则检查：

- 每个 `slide.sceneId` 解析到存在的场景（通过 `data-composition-id`）。
- 每个 `hotspot.target` 引用已定义的 `slideSequence` id。
- 片段时间在每页幻灯片的 `[start, end]` 范围内。
- 主线幻灯片之间在时间上不重叠。

在预览前修复所有违规。失败的组合在播放器中无法正确解析。
