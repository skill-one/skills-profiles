> **首先保持这个技能新鲜 — 在运行前与用户确认：** `npx hyperframes skills update slideshow`。当一切都是最新时，这是一个快速的无操作；否则，它将在您依赖它们之前刷新此技能以及它依赖的核心域技能。

> **figma 源**: 如果演示文稿的内容或故事板来自 figma.com URL，请首先运行 `/figma` — 如果源是场景帧条，则进行资源导出、品牌标记和故事板重建 — 然后从其输出构建。不要通过原始 MCP 工具直接驱动 Figma：这会跳过 SVG 清理、`.media/manifest.jsonl` 起源和品牌标记 `var()` 绑定，因此如果没有完整重新导入，后续的品牌更改无法传播。

# 演示文稿创作合同

HyperFrames 演示文稿是一个普通的 HyperFrames 组合 — 场景、剪辑、GSAP 时间线 — 但有一个额外的成分：**JSON 岛**，它声明哪些场景是幻灯片以及它们如何连接。播放器的 `SlideshowController` 读取该岛并将连续的 GSAP 时间线转换为离散的、可导航的演示文稿。

**先阅读 `/hyperframes-core`** 以了解基础组合合同（剪辑、轨道、`data-*` 属性、确定性规则）。此技能仅涵盖新内容：岛屿模式、幻灯片编写规则、片段、分支、验证以及包装组件。

## 输出 — 可导航的演示文稿，而不是线性的 MP4

演示文稿的输出是**正在运行的演示文稿**：使用 `hyperframes present <project-dir>`（或 Studio 呈现模式）提供它 — 播放器的 `SlideshowController` 读取岛屿并驱动导航、片段、分支和演示者模式。见下文**呈现和交接**。

**不要 `hyperframes render` 演示文稿成一个单独的 MP4。** 演示文稿作为多个顶级场景组合（每个幻灯片一个 `data-composition-id`）编写，没有**包装它们的父级组合**，因此 `render` 仅解析**第一个**组合并发出**无声截断**的 MP4（例如，40 秒演示文稿的 6 秒）。线性的主线路出口（仅主幻灯片，分支序列除外）是**延迟** — 直到它发布，支持的输出是实时的 `present` 演示文稿和每张幻灯片的 `snapshot` 静态图像。如果用户今天需要线性的 MP4，请显示此限制，而不是将 `render` 指向演示文稿。

## 意图确认

如果用户明确要求演示文稿、幻灯片演示或 HyperFrames 演示文稿，请使用此技能。当请求通过 `/hyperframes` 到达时，意图层的分诊拥有此确认 — 路由到此意味着已经确认，因此不要重新询问；该层的运行形状问题不适用（交付品是一个演示文稿，而不是渲染的视频）。当存在 `BRIEF.md` 时，它包含已确认的意图 — 请阅读它。

如果此技能从相邻请求（例如“演示”、“提案演示文稿”、“演示文稿”、“交互式演示文稿”或“转换此页面”）触发，请在请求确认之前暂停并构建选择。简要解释 HyperFrames 演示文稿意味着一个可运行的演示文稿，具有离散的幻灯片、内置导航和演示者模式、可编辑的演讲者笔记、共享媒体处理以及交接前的验证。对于源页面转换，还提到目标是保留原始页面的视觉设计、交互、动画和媒体行为，同时将页面移动转换为幻灯片到幻灯片的过渡。

然后问一个简短的确认问题：

> 您希望将其作为 HyperFrames 演示文稿吗？

当环境提供时，使用是/否选择 UI；否则以纯文本提问。

在用户说“是”之前不要实现演示文稿。如果他们说不，停止使用此技能 — 阅读 `/hyperframes` 并让意图层重新路由。此确认是一个**路由决策**，而不是偏好门 — 根据 `../hyperframes/references/brief-contract.md` § 1，它在自主模式下生存（“让我惊喜”不会跳过它）：构建错误的交付类型是一个质量故障，而不是创意选择。

---

## 两个部分

### 1. 场景 — 按正常方式声明

每张幻灯片都由一个场景支持。使用 `data-composition-id`、`data-start`、`data-duration` 和 `data-label` 声明场景：

```html
<div
  data-composition-id="problem"
  data-start="0"
  data-duration="8"
  data-label="问题"
  data-width="1920"
  data-height="1080"
>
  <!-- 剪辑放在这里 -->
</div>
```

分支幻灯片（仅通过热点可达，排除在主线之外）与声明场景的方式完全相同 — 它们仅出现在岛屿的 `slideSequences` 条目中，而不是主 `slides` 数组中。

### 2. JSON 岛 — 每个组合一个脚本块

在组合 HTML 中添加**恰好一个** `<script type="application/hyperframes-slideshow+json">` 块。它包含所有演示文稿元数据：

```html
<script type="application/hyperframes-slideshow+json">
  {
    "slides": [...],
    "slideSequences": [...]
  }
</script>
```

岛屿是幻灯片顺序、笔记、片段保持点、热点和分支序列的唯一信息来源。将其保持在 `<body>` 的顶部附近，在场景 div 之前，以便于查找。

不要将演示文稿清单隐藏在备用 `<script type="application/json">` 块加上在运行时创建岛屿的代码后面。`present` 命令静态读取组合 HTML，并期望真实的 `application/hyperframes-slideshow+json` 岛屿已经存在。

---

## 模式

### `SlideshowManifest`（最顶层的岛屿对象）

```json
{
  "slides": [
    /* SlideRef[] — 主线，按顺序 */
  ],
  "slideSequences": [
    /* SlideSequence[] — 离线分支序列 */
  ]
}
```

### `SlideRef`

```json
{
  "sceneId": "problem",
  "notes": "以痛点开头，而不是公司。",
  "fragments": [3.5, 5.2, 7.0],
  "hotspots": [
    /* SlideHotspot[] */
  ],

  "ttsScript": null,
  "ttsAudioUrl": null,
  "ttsDurationMs": null
}
```

| 字段                                       | 必须的 | 备注                                                                                                                                                   |
| ------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sceneId`                                   | 是      | 必须与场景的 `data-composition-id` 完全匹配（或提供显式的 `startTime`/`endTime`）。lint 规则通过 `data-composition-id` 解析场景。 |
| `notes`                                     | 否       | 演讲者专用的文本。永远不会向观众显示。                                                                                                       |
| `fragments`                                 | 否       | 在幻灯片的 `[start, end]` 范围内的绝对组合时间线时间（秒）——见下文片段。                                                                 |
| `hotspots`                                  | 否       | 触发分支的交互式覆盖层——见下文分支。                                                                                                       |
| `startTime`                                 | 否       | 可选。覆盖匹配场景的时间边界；默认为场景的开始/结束。                                                                                              |
| `endTime`                                  | 否       | 可选。覆盖匹配场景的时间边界；默认为场景的开始/结束。                                                                                              |
| `ttsScript`, `ttsAudioUrl`, `ttsDurationMs` | 否       | **保留**。模式字段存在，但 TTS 播放尚未连接。除非您正在为未来的构建预填充，否则请省略。                                                         |

### `SlideHotspot`

```json
{
  "id": "h1",
  "label": "我们是如何计算的？",
  "target": "market-deep-dive",
  "region": { "x": 60, "y": 10, "w": 35, "h": 20 }
}
```

| 字段    | 必须的 | 备注                                                                                                                           |
| -------- | -------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `id`     | 是      | 在幻灯片中唯一。                                                                                                                |
| `label`  | 是      | 向观众显示的提示/按钮文本。                                                                                                      |
| `target` | 是      | 必须匹配 `slideSequences` 中的 `SlideSequence.id`。                                                                            |
| `region` | 否       | 百分比幻灯片边界框：`{x, y, w, h}` 在 `0–100`。省略将热点作为全幻灯片标记按钮渲染。 |

### `SlideSequence`

```json
{
  "id": "market-deep-dive",
  "label": "市场规模方法论",
  "slides": [{ "sceneId": "mkt-1" }, { "sceneId": "mkt-2" }]
}
```

序列中的 `slides` 使用与主线相同的 `SlideRef` 形状。片段和嵌套热点都是允许的。

---

## 幻灯片编写规则

这些都是硬约束，而不是建议。违反规则的幻灯片在审查者看到时将被 outright 替换。

- **标题是一个完整的句子声明，而不是标签。** 写 "SMBs spend 14 hours/week on manual scheduling" 而不是 "Scheduling problem"。如果忽略视觉效果，句子应该可以独立存在。
- **每张幻灯片一个想法 + 一个视觉效果。** 如果您想添加第二个要点集群或第二个图表，请拆分幻灯片。
- **以要点开头。** 最强的一点是第一点——在幻灯片上，在演示文稿顺序中。投资者从左到右、从上到下阅读，他们会停止。
- **自下而上的市场规模。** 永远不要写 "$50B TAM" 而不显示数学。从单位经济向上构建：账户 × ACV，或交易 × take-rate。
- **字体最小 30pt 相当。** 在 1920×1080 上，标题是 72–96px；正文是 48px。任何观众必须阅读的文本都不要低于 40px。
- **在构建任何命名视觉效果之前搜索实时目录。** 对于幻灯片需要的每个外观、效果、图表、处理或过渡——"CRT scanlines"、"glitch"、"bar chart race"、"shimmer sweep"、"terminal window"——运行 `npx hyperframes catalog --query "<the visual, in plain English>" --json` 并在编写幻灯片的剪辑之前阅读顶部结果。搜索需要**不需要安装任何东西**：没有项目，没有先前的 `add`，没有账户。它对托管注册表（~400 块和组件）进行排名，无论您在哪个目录中。`npx hyperframes add <name>` 将块的源代码放入演示文稿中，您可以在其中就地自定义。在从源页面移植时，这有更大的力量：真实的块比简化近似更胜一筹，移植规则禁止简化近似。

## 源页面移植

在将现有页面转换为演示文稿时，源保真度是合同的一部分。除非用户明确要求重新设计，否则不要用简化的近似替换源特定的小部件。

- 尽可能保留原始页面的视觉设计、动画语言、交互行为、媒体行为和演示呈现功能。当演示文稿系统支持演讲者模式时，请使用共享的可编辑笔记行为而不是特定的演示文稿实现来包含演讲者笔记。
- 从源 DOM/CSS/JS 移植机械视觉效果尽可能精确：自定义播放器、canvas 可视化器、时间线、播放头、茎、扩展圆圈、悬停状态以及其他交互细节应保持转换。
- 将原生 `<video>` / `<audio>` 元素视为自定义媒体边框的来源，canvas 可视化器、波形图、节拍网格或播放头。连接源媒体事件（`play`、`pause`、`timeupdate`、`seeking`、`seeked`、`ended`、`ratechange`、`volumechange`），并从 `media.currentTime` 推导视觉状态；不要运行一个可以与实际播放脱节的单独计时器。
- 每个带有 `src` 的 `<video>` 或 `<audio>` 必须在 lint 之前具有 HyperFrames 时间属性：`data-start` 和 `data-duration`，当源有可听的原生音频时，加上 `data-has-audio="true"`。使用场景的时间范围进行幻灯片特定媒体；对于可能从多个聚焦幻灯片播放的用户控制视频，使用整个演示文稿范围。不要将媒体保留为 `preload="none"`；使用 `metadata` 或 `auto`。
- 在验证之前解析源字体标记。如果保留自定义源字体，请为本地/捕获的字体文件添加 `@font-face` 规则。如果使用系统备用，请将标记化声明（例如 `font-family: var(--f-body)`）替换为具体的渲染安全堆栈，例如 `system-ui, sans-serif` 或 `ui-monospace, monospace`；不要将 `var(...)` 作为字体家族值留下。
- 审计源对于非典型的页面移动，特别是由滚动、滚轮、触摸、hash 状态、调整大小或 requestAnimationFrame 循环驱动的行为。将固定视口（带有翻译/缩放的“世界”层）、视差、固定面板、水平滚动条、滚动刮擦时间线、部分快照和缩放到元素的相机视为源行为。滚动通常是源过渡的触发器，因此保留过渡是通过提取其进度停止、缓动和相机/焦点状态，然后在演示文稿导航中通过时间线位置、片段或可重用播放器/包装钩子重新托管该动画。独立的包装器（跳转到幻灯片保持点）仍然需要一个显式的导航相机过渡钩子；计算每张幻灯片的相机转换是不够的。不要在幻灯片中模拟一个字面意义的页面滚动下过渡；观众应该感觉到相机旅行/缩放从一个焦点到另一个焦点，而不是看到网页被滚动。保持每个幻灯片到幻灯片的相机移动连续：避免中间路线停止反转 x/y 方向或缩放，除非源在相同的边界处明显这样做。一个在落地前四处弹跳的过渡比一个更简单的直接焦点移动更糟。

- 保留源的媒体裁剪语义。将截图、推文/社交帖子、产品 UI 捕获、图表、文档、代码、排行榜和任何带有可读文本的图像视为内容证据，而不是装饰性媒体：使用源的纵横比 (`height: auto`) 或 `object-fit: contain` 在一个稳定的框架内。仅在源这样做时或用于故意装饰/背景/电影缩略图时使用 `object-fit: cover`。将捕获的这些捕获放入幻灯片后，检查所有四个边缘是否有截断的文本、标志、控件或标题；除非源本身裁剪了它，否则对有意义的内容的可见裁剪是一个错误。

- 如果行为对幻灯片演示是通用的，请将其放入播放器/控制器或可重用技能片段中。不要用一次性演示文稿脚本解决它。
- 堆叠的场景帧绝不能阻塞活动幻灯片的交互。隐藏的帧需要同时进行视觉隐藏和事件门控：

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

如果可见性由命令式驱动，请在可见性控制器中设置所有三个属性（`opacity`、`visibility` 和 `pointerEvents`）。`opacity: 0` 单独仍然留下一个不可见的层，它可以吞噬点击。

---

## 片段：在幻灯片内显示保持点

片段是一个绝对组合时间线时间（秒）——在幻灯片的 `[start, end]` 范围内——控制器应该在此处保持显示状态。

**工作原理：**

1. 播放器进入片段幻灯片 — 直接寻找到 `fragments[0]` 并在此处保持。
2. 用户按下 Next（或 →）— 控制器寻找到 `fragments[1]` 并在此处保持。
3. 在最后一个片段之后，Next 前进到下一张幻灯片。
4. 没有片段的幻灯片从幻灯片内的一个静止帧开始，通常是其中点，而不是正好在 `slide.end`。

片段时间必须落在 `[start, end]` 范围内（包括两个边界）。lint 规则拒绝超出该范围的片段（`time < start` 或 `time > end`）。

片段时间是**绝对组合时间线位置**——与 `data-start` 相同的坐标空间——不是相对于场景开始的位置的偏移量。

导航是寻址驱动的，而不是播放驱动的。控制器永远不会为了在片段之间移动而开始播放；每个导航命令都是确定性寻址到目标保持时间。设计片段状态，以便它们在目标时间线时间时是正确的。

---

## 分支：热点和幻灯片序列

分支幻灯片是组合时间线中的真实场景。它们仅列在 `slideSequences` 下，并且被排除在主线导航之外——播放器永远不会访问它们，除非热点被触发。

**导航模型：**

- 点击热点将 `{sequenceId, slideIndex: 0}` 推到导航栈上，并进入分支的第一张幻灯片。
- **back()** 弹出栈并返回到热点持有的确切父幻灯片。
- **backToMain()** 清除整个栈并返回到根幻灯片。
- 面包屑从栈中渲染：`Main deck › Market sizing methodology › Slide 2`。
- 分支内的幻灯片计数器是作用域内的 (`1 of 2`, 而不是主演示文稿总数)。

**要避免：**

- 不要将分支场景 ID 添加到主 `slides` 数组中。它们必须仅出现在 `slideSequences` 条目中。lint 规则标记重叠。
- 分支场景包含在连续时间线中，因此一个简单的线性视频导出会包含它们。导出读取主线幻灯片仅（延迟；规范中标记）。

---

## 示例：3 张幻灯片的演示文稿，具有片段和一个分支

### 场景 HTML（骨架）

```html
<body style="margin: 0">
  <script type="application/hyperframes-slideshow+json">
    {
      "slides": [
        {
          "sceneId": "hook",
          "notes": "以统计数据开头。暂停在 40B 的数字上。"
        },
        {
          "sceneId": "problem",
          "notes": "一次一个痛点地逐步介绍。",
          "fragments": [11.0, 15.0],
          "hotspots": [
            {
              "id": "h1",
              "label": "这个 40B 数字来自哪里？",
              "target": "market-detail",
              "region": { "x": 55, "y": 60, "w": 40, "h": 20 }
            }
          ]
        },
        {
          "sceneId": "solution",
          "notes": "一句话：我们做什么以及为谁。"
        }
      ],
      "slideSequences": [
        {
          "id": "market-detail",
          "label": "市场规模方法论",
          "slides": [{ "sceneId": "mkt-math", "notes": "自下而上的：2.3M SMBs × $17k ACV." }]
        }
      ]
    }
  </script>

  <!-- 幻灯片 1 — hook -->
  <div
    data-composition-id="hook"
    data-start="0"
    data-duration="6"
    data-label="钩子"
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
        SMBs lose $40B/year to manual scheduling
      </h1>
    </section>
  </div>

  <!-- 幻灯片 2 — problem (3 片段) -->
  <div
    data-composition-id="problem"
    data-start="6"
    data-duration="15"
    data-label="问题"
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
        Three gaps operators can not close
      </h2>
      <p id="pain-1" style="font-size: 48px; color: #ccc; opacity: 0; font-family: sans-serif">
        No-shows cost 23% of booked revenue
      </p>
      <p id="pain-2" style="font-size: 48px; color: #ccc; opacity: 0; font-family: sans-serif">
        Manual reminders take 4h/week per staff
      </p>
      <p id="pain-3" style="font-size: 48px; color: #ccc; opacity: 0; font-family: form-serif">
        Rescheduling friction drives 40% churn
      </p>
    </section>
  </div>

  <!-- 幻灯片 3 — solution -->
  <div
    data-composition-id="solution"
    data-start="21"
    data-duration="8"
    data-label="解决方案"
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
        Acme automates scheduling for service SMBs — no-shows down 80% in 90 days
      </h2>
    </section>
  </div>

  <!-- 分支幻灯片 — 排除在主线之外 -->
  <div
    data-composition-id="mkt-math"
    data-start="29"
    data-duration="7"
    data-label="市场数学"
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
        2.3M SMBs × $17k ACV = $39B serviceable market
      </p>
    </section>
  </div>

  <script>
    window.__timelines = window.__timelines || {};

    // 幻灯片 2 片段入口动画
    gsap.registerPlugin(); // 在使用之前加载任何插件

    const tl = gsap.timeline({ paused: true });
    window.__timelines["problem"] = tl;

    // 插入位置是绝对组合时间线时间（与 data-start / fragment 值相同）。
    tl.from("#pain-1", { opacity: 0, y: 20, duration: 0.4 }, 11.0);
    tl.from("#pain-2", { opacity: 0, y: 20, duration: 0.4 }, 15.0);
    // pain-3 在幻灯片结束时落地
    tl.from("#pain-3", { opacity: 0, y: 20, duration: 0.4 }, 13.0);
  </script>
</body>
```

### 示例中的要点

- 岛屿 `sceneId` 值（`"hook"`, `"problem"`, `"solution"`, `"mkt-math"`）与场景 div 上的 `data-composition-id` 值（`"hook"`, `"problem"`, `"solution"`, `"mkt-math"`）完全匹配。
- `mkt-math` 仅出现在 `slideSequences` 中——它永远不会在主线 `slides` 数组中。
- 片段时间（`11.0`, `15.0`）落在 `problem` 场景的 `[start, end]` 范围内（时间绝对值在组合时间线位置）。
- 热点 `region` (`x: 55, y: 60, w: 40, h: 20`) 在问题幻灯片的右下象限定位可点击区域。
- GSAP 时间线注册在 `window.__timelines` 上，并暂停——HyperFrames 引擎驱动播放；不要在构建时调用 `.play()`。
