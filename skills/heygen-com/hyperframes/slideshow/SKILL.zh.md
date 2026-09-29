---
name: slideshow
description: 撰写一个 HyperFrames 幻灯片——一个具有独立幻灯片、片段揭示、分支、热点导航和内置演讲者模式的演示文稿、提案演示文稿或交互式演示文稿，其中包含演讲者笔记；还可以将现有页面转换为演示文稿。输出是一个可导航的演示文稿，而不是渲染的 MP4。如果用户没有明确要求创建幻灯片，则在撰写前进行确认。不明确 → /hyperframes。
---

**插件安装：** 在设置或新鲜命令之前，当此技能位于 HyperFrames 插件内时，请遵循 [插件执行规则](../hyperframes/references/plugin-installation.md)。独立安装则保留下方的更新说明。

> **首先，保持此技能新鲜——在运行前与用户确认：** `npx hyperframes skills update slideshow`。当一切正常时，这是一个快速的无操作；否则，它将在您依赖它们之前刷新此技能及其依赖的核心域技能。

> **figma 源文件：** 如果牌组的内容或故事板来自 figma.com URL，请先运行 `/figma` — 如果源是场景帧条，则进行资源导出、品牌标记和故事板重建 — 然后从其输出构建。不要直接通过原始 MCP 工具驱动 Figma：那样会跳过 SVG 清理、`.media/manifest.jsonl` 起源和品牌标记 `var()` 绑定，因此后续品牌更改无法在不完整重新导入的情况下传播。

# 幻灯片制作合约

HyperFrames 幻灯片是一个标准的 HyperFrames 组合——场景、剪辑、GSAP 时间线——外加一个**JSON 岛**，它声明哪些场景是幻灯片以及它们如何连接。播放器的 `SlideshowController` 读取该岛并将连续的 GSAP 时间线转换为可离散导航的牌组。

**先阅读 `/hyperframes-core`** 了解基础组合合约（剪辑、轨道、`data-*` 属性、确定性规则）。此技能仅涵盖新内容：岛屿模式、幻灯片编写规则、片段、分支、验证和包装组件。

## 输出——可导航的牌组，而非线性 MP4

幻灯片的输出是**运行中的牌组**：使用 `hyperframes present <project-dir>`（或 Studio 呈现模式）提供它 — 播放器的 `SlideshowController` 读取岛屿并驱动导航、片段、分支和演示者模式。见**呈现和交接**下方。

**不要 `hyperframes render` 将幻灯片渲染为单个 MP4。** 牌组作为多个顶层场景组合（每个幻灯片一个 `data-composition-id`）编写，没有**主根组合**将它们包装，因此 `render` 仅解析**第一个**组合并发出**静默截断**的 MP4（例如，40 秒牌组的 6 秒）。线性主线路径导出（仅主幻灯片，分支序列除外）是**延迟**的 — 直到发货，支持的输出是实时的 `present` 牌组和每张幻灯片的 `snapshot` 静态图像。如果用户今天需要线性 MP4，请展示此限制，而不是将 `render` 指向牌组。

## 意图确认

如果用户明确要求幻灯片、幻灯片展示或 HyperFrames 幻灯片，请使用此技能。当请求通过 `/hyperframes` 到达时，意图层的分诊负责此确认 — 路由到此意味着已确认，因此不要重新询问；层的运行形状问题不适用（交付物是牌组，而不是渲染视频）。当存在 `BRIEF.md` 时，它会携带确认的意图——请阅读它。

如果技能从相邻请求（如“演示”、“提案牌组”、“牌组”、“交互式牌组”或“转换此页面”）触发，请在编写前暂停并框定选择，然后询问确认。简要解释 HyperFrames 幻灯片意味着一个可运行的牌组，具有离散幻灯片、内置导航和演示者模式、可编辑的演讲者笔记、共享媒体处理和在交接前验证。对于源页面转换，还提到目标是保留原始页面的视觉设计、交互、运动和媒体行为，同时将页面移动转换为幻灯片到幻灯片的过渡。

然后询问一个简短的确认问题：

> 你希望将其作为 HyperFrames 幻灯片吗？

在环境提供选择界面时使用是/否选择 UI；否则以纯文本形式提问。

在用户说“是”之前不要实现幻灯片。如果他们说不，请停止使用此技能——阅读 `/hyperframes` 并让意图层重新路由。此确认是一个**路由决策**，而不是偏好门——根据 `../hyperframes/references/brief-contract.md` § 1，它会在自主模式下存活（“让我惊喜”不会跳过它）：构建错误交付类型是质量故障，而不是创意选择。

---

## 两个部分

### 1. 场景——以正常方式声明

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

分支幻灯片（仅通过热点可达，不包括在主线中）声明方式完全相同——它们仅出现在岛屿的 `slideSequences` 条目中，而不是主 `slides` 数组中。

### 2. JSON 岛——每个组合一个脚本块

向组合 HTML 添加**恰好一个** `<script type="application/hyperframes-slideshow+json">` 块。它包含所有幻灯片元数据：

```html
<script type="application/hyperframes-slideshow+json">
  {
    "slides": [...],
    "slideSequences": [...]
  }
</script>
```

岛屿是幻灯片顺序、笔记、片段保持点、热点和分支序列的唯一真实来源。将其保持在 `<body>` 顶部附近，在场景 div 之前，以便轻松找到。

不要将幻灯片清单隐藏在备用 `<script type="application/json">` 块加上运行时代码创建岛屿后面。`present` 命令静态读取组合 HTML 并期望真实的 `application/hyperframes-slideshow+json` 岛屿已经存在。

---

## 模式

### `SlideshowManifest`（顶层岛屿对象）

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
  "notes": "先展示痛点，而不是公司。",
  "fragments": [3.5, 5.2, 7.0],
  "hotspots": [
    /* SlideHotspot[] */
  ],

  "ttsScript": null,
  "ttsAudioUrl": null,
  "ttsDurationMs": null
}
```

| 字段                                       | 必填 | 备注                                                                                                                                                   |
| ------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sceneId`                                   | 是      | 必须与场景的 `data-composition-id` 完全匹配（或提供显式的 `startTime`/`endTime`）。lint 规则通过 `data-composition-id` 解析场景。 |
| `notes`                                     | 否       | 演示者专用的文本。永远不会展示给观众。                                                                                                       |
| `fragments`                                 | 否       | 滑片 `[start, end]` 范围内的绝对时间（秒）数组——见片段下方。                                                                                     |
| `hotspots`                                  | 否       | 触发分支的交互式覆盖层——见分支下方。                                                                                                               |
| `startTime`                                 | 否       | 可选。覆盖匹配场景的时间边界；默认为场景的起止时间。                                                                                              |
| `endTime`                                   | 否       | 可选。覆盖匹配场景的时间边界；默认为场景的起止时间。                                                                                              |
| `ttsScript`, `ttsAudioUrl`, `ttsDurationMs` | 否       | **保留。** 模式字段存在，但 TTS 播放尚未连接。除非您正在为未来构建预填充，否则请省略。                                                             |

### `SlideHotspot`

```json
{
  "id": "h1",
  "label": "我们是如何计算这个的？",
  "target": "market-deep-dive",
  "region": { "x": 60, "y": 10, "w": 35, "h": 20 }
}
```

| 字段    | 必填 | 备注                                                                                                                           |
| -------- | -------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `id`     | 是      | 在幻灯片内唯一。                                                                                                                |
| `label`  | 是      | 向观众展示的提示/按钮文本。                                                                                                      |
| `target` | 是      | 必须与 `slideSequences` 中的 `SlideSequence.id` 匹配。                                                                            |
| `region` | 否       | 幻灯片百分比边界框：`{x, y, w, h}` 在 `0–100`。省略将热点渲染为全幻灯片标记按钮。 |

### `SlideSequence`

```json
{
  "id": "market-deep-dive",
  "label": "市场规模方法论",
  "slides": [{ "sceneId": "mkt-1" }, { "sceneId": "mkt-2" }]
}
```

序列内的 `slides` 使用与主线相同的 `SlideRef` 形状。片段和嵌套热点都是允许的。

---

## 幻灯片编写规则

这些都是硬约束，不是建议。违反规则的幻灯片在审查者看到时会被直接替换。

- **标题是一个完整的句子声明，而不是标签。** 写“SMBs 每周花费 14 小时在手动排程上”而不是“排程问题”。如果忽略视觉效果，句子应该可以独立存在。
- **每张幻灯片一个想法 + 一个视觉。** 如果您想添加第二个要点集群或第二个图表，请拆分幻灯片。
- **先展示重点。** 最强的点放在第一位——在幻灯片和牌组顺序中。投资者从左到右、从上到下阅读，并且会停止。
- **仅从下到上市场规模。** 永远不要写“$50B TAM”而不展示计算过程。从单位经济开始构建：账户 × ACV，或交易 × 抽成率。
- **字体最小 30pt 等效。** 在 1920×1080 下，标题是 72–96px；正文是 48px。任何观众必须阅读的文本都不应低于 40px。
- **在手动构建任何命名视觉之前，先在实时目录中搜索。** 对于幻灯片需要的每个外观、效果、图表、处理或过渡——“CRT 扫描线”、“故障”、“条形图竞赛”、“闪烁扫描”、“终端窗口”——运行 `npx hyperframes catalog --query "<纯英文的视觉>" --json` 并阅读顶部结果，然后再编写幻灯片的剪辑。搜索**不需要安装任何东西**：没有项目，没有先前的 `add`，没有账户。它按顺序排列托管注册表中的所有内容（~400 个块和组件）从任何目录。`npx hyperframes add <name>` 将块的源代码放入牌组，您可以在其中就地自定义。在从源页面移植时，这尤其适用：真实的块胜过简化近似，移植规则禁止使用。

1. 玩家进入一个碎片化的幻灯片——直接跳转到 `fragments[0]` 并停留在那里。
2. 用户点击下一页（或 →）——控制器跳转到 `fragments[1]` 并停留在那里。
3. 在最后一个碎片之后，下一页会跳转到下一个幻灯片。
4. 一个没有碎片的幻灯片会在幻灯片内部的静止帧进入，通常是它的中点，而不是正好在 `slide.end`。

碎片时间必须落在 `[start, end]` 范围内（包括上下边界）。lint 规则只拒绝范围外的碎片（`time < start` 或 `time > end`）。

碎片时间是**绝对的时间轴位置**——与 `data-start` 相同的坐标空间——不是相对于场景开始的位置偏移。

导航是搜索驱动的，不是播放驱动的。控制器不会为了在碎片之间移动而开始播放；每个导航命令都是确定性的跳转到目标保持时间。设计碎片状态，使其在目标时间轴时间时是正确的。

---

## 分支：热点和幻灯片序列

分支幻灯片是同一组合时间轴上的真实场景。它们仅在 `slideSequences` 下列出，并从主线导航中排除——玩家只有在热点触发时才会访问它们。

**导航模型：**

- 点击热点将 `{sequenceId, slideIndex: 0}` 压入导航栈并进入分支的第一个幻灯片。
- **back()** 弹出栈并返回到精确的父幻灯片（包含热点的那个幻灯片）。
- **backToMain()** 清除整个栈并返回到根幻灯片。
- 面包屑根据栈渲染：`Main deck › Market sizing methodology › Slide 2`。
- 分支内的幻灯片计数器仅限于该序列（`1 of 2`，而不是主 deck 总数）。

**需要避免的事项：**

- 不要将分支场景 ID 添加到主 `slides` 数组中。它们必须仅在 `slideSequences` 条目中出现。lint 规则会标记重叠。
- 分支场景包含在连续时间轴中，因此一个简单的线性视频导出会包含它们。导出只读取主线幻灯片（延迟；在规范中标记）。

---

## 示例：一个包含碎片和分支的 3 幻灯片 deck

### 场景 HTML (骨架)

```html
<body style="margin: 0">
  <script type="application/hyperframes-slideshow+json">
    {
      "slides": [
        {
          "sceneId": "hook",
          "notes": "以统计数据开头。在 40B 的数字上暂停。"
        },
        {
          "sceneId": "problem",
          "notes": "一次一个地逐步介绍每个痛点。",
          "fragments": [11.0, 15.0],
          "hotspots": [
            {
              "id": "h1",
              "label": "40B 这个数字从何而来？",
              "target": "market-detail",
              "region": { "x": 55, "y": 60, "w": 40, "h": 20 }
            }
          ]
        },
        {
          "sceneId": "solution",
          "notes": "一句话：我们做什么以及为谁服务。"
        }
      ],
      "slideSequences": [
        {
          "id": "market-detail",
          "label": "Market sizing methodology",
          "slides": [{ "sceneId": "mkt-math", "notes": "自下而上：2.3M SMBs × $17k ACV." }]
        }
      ]
    }
  </script>

  <!-- 幻灯片 1 — hook -->
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
        SMBs 每年因手动排程损失 40B 美元
      </h1>
    </section>
  </div>

  <!-- 幻灯片 2 — problem (3 个碎片) -->
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
        运营商无法弥补的三个差距
      </h2>
      <p id="pain-1" style="font-size: 48px; color: #ccc; opacity: 0; font-family: sans-serif">
        未出席成本占预订收入的 23%
      </p>
      <p id="pain-2" style="font-size: 48px; color: #ccc; opacity: 0; font-family: sans-serif">
        手动提醒每周每人耗时 4 小时
      </p>
      <p id="pain-3" style="font-size: 48px; color: #ccc; opacity: 0; font-family: sans-serif">
        重新排程的摩擦导致 40% 的客户流失
      </p>
    </section>
  </div>

  <!-- 幻灯片 3 — solution -->
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
        Acme 为服务型 SMB 自动排程——90 天内未出席率下降 80%
      </h2>
    </section>
  </div>

  <!-- 分支幻灯片 — 从主线导航中排除 -->
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

    // 幻灯片 2 碎片进入动画
    gsap.registerPlugin(); // 在使用前加载任何插件

    const tl = gsap.timeline({ paused: true });
    window.__timelines["problem"] = tl;

    // 插入位置是绝对组合时间轴时间（与 data-start / 碎片值相同）。
    tl.from("#pain-1", { opacity: 0, y: 20, duration: 0.4 }, 11.0);
    tl.from("#pain-2", { opacity: 0, y: 20, duration: 0.4 }, 15.0);
    // pain-3 停留在幻灯片末尾
    tl.from("#pain-3", { opacity: 0, y: 20, duration: 0.4 }, 13.0);
  </script>
</body>
```

### 示例中的关键点

- 岛屿 `sceneId` 值（`"hook"`, `"problem"`, `"solution"`, `"mkt-math"`）与场景 div 上的 `data-composition-id` 值完全匹配。
- `mkt-math` 仅出现在 `slideSequences` 中——它永远不会在顶层 `slides` 数组中。
- 碎片时间（`11.0`, `15.0`）在 `problem` 场景的 `[6, 21]` 范围内（时间是绝对组合时间轴位置）。
- 热点 `region`（`x: 55, y: 60, w: 40, h: 20`）在问题幻灯片的右下象限定位可点击区域。
- GSAP 时间轴注册在 `window.__timelines` 上并处于暂停状态——HyperFrames 引擎驱动播放；不要在构造时调用 `.play()`。

---

## 包装组件

在任何嵌入上下文中，将组合用 `<hyperframes-slideshow>` 包裹 `<hyperframes-player>`：

```html
<hyperframes-slideshow>
  <hyperframes-player src="deck.html"></hyperframes-player>
</hyperframes-slideshow>
```

`<hyperframes-slideshow>` 提供导航界面（Present, Prev / Next, 计数器，当 `sound` 存在时全局静音，全屏），键盘处理（← / →, Space / Backspace，以及 P 用于 Present），触摸滑动和热点覆盖。

slideshow 自动在挂载时为每个内部 `<hyperframes-player>` 设置 `interactive` 属性，因此可点击控件、链接、原生媒体控件和组合 iframe 内的自定义播放器按预期接收指针事件。（在 slideshow 包装器外，你必须手动在 `<hyperframes-player>` 上添加 `interactive`——播放器默认在 iframe 上为 `pointer-events: none`，以防止点击播放器主机被劫持为切换时间轴播放。）。

**演示者模式：** 使用 slideshow 导航胶囊中的内置 Present 图标按钮，或按 P。它调用 `window.open('?mode=audience')` 以全屏显示观众标签页；原始标签页成为演示者视图（当前幻灯片减少，下一页预览，笔记，经过时间计时器）。两个标签页通过 `BroadcastChannel('hf-slideshow:' + location.pathname)` 同步。不要添加自定义的 `#present-btn`、固定位置按钮或包装器特定的 Present 样式。共享组件拥有控制条，在 `?mode=audience` 时隐藏 Present，并支持 P 作为键盘快捷键。

**在 Google Meet / Zoom 上演示（屏幕共享）：** 共享观众界面，在自己的屏幕上保留演示者视图。

- **Google Meet（或任何 Chrome 内共享）：** Present → 在 Meet 中选择 **共享屏幕 → 一个标签页** → 选择观众标签页 → 切换回演示者标签页。Chrome 会保留捕获的标签页进行渲染，即使后台运行，动画和幻灯片导航也保持活跃。**不要**共享 "一个窗口" 或 "整个屏幕"——完全覆盖的窗口会停止渲染（观众看到冻结的幻灯片），整个屏幕会暴露你的笔记。
- **Zoom（桌面应用）：** 将观众标签页拖出成为自己的窗口并共享该窗口。Zoom 通过操作系统捕获，因此如果观众窗口完全被覆盖，它会冻结——使用第二个显示器，或保持观众窗口的一小部分在演示者视图后面可见。

演示者驱动的媒体播放有一个自动播放策略限制：`BroadcastChannel` 可以同步意图、时间和状态，但它不能将演示者的用户激活传递给观众标签页。共享 slideshow 播放器镜像原生媒体事件，并首先以静音方式开始远程观众播放；只有在静音 `media.play()` 被拒绝或如果 deck 特意要求可听观众播放时，才回退到独立的 harness 的观众解锁行为。不要在拒绝播放后持续应用远程 `timeupdate` 消息，否则观众将无声地跳转到视频。

演示者笔记在演示者视图中可编辑。编辑内容存储在 `localStorage` 中，每个 deck 和幻灯片分层覆盖组合文件中的注释，而不重写组合文件。不要在 deck 中添加一次性笔记编辑脚本；依赖共享 slideshow 播放器行为。如果独立的/自定义包装器确实需要在共享播放器外部实现此功能，请使用 `skills/slideshow/references/standalone-harness.md` 中的确定性存储片段。

### 幻灯片退出时的媒体清理

slideshow 控制器拥有幻灯片退出时的媒体清理。当导航切换幻灯片或序列时，它会调用 `hyperframes-player.stopMedia()` 在进入下一个幻灯片之前。该命令：

- 向 iframe 运行时发布 `stop-media`，停止 WebAudio 并暂停原生 `<video>` / `<audio>` 元素；
- 直接暂停同源 iframe 媒体作为后备；以及
- 暂停从 iframe 媒体继承的父框架代理。

同幻灯片碎片导航**不会**停止媒体。全局/deck 级别的父音频，例如通过 `audio-src` 连接的背景音轨，不会被当作幻灯片媒体处理。

不要添加用于正常媒体播放器的每幻灯片清理脚本。在组合中保留幻灯片视频/音频为正常媒体；仅在播放器应保留可听原生视频音频而不是将其视为无声视觉媒体时，才使用 `data-has-audio="true"`。

如果源页面有附加到媒体的自定义控件或可视化效果，这些控件必须监听与 slideshow 播放器停止和静音相同的原生元素。由幻灯片退出、演示者同步、原生控件、自定义控件或全局静音按钮引起的暂停都应通过媒体事件更新可见的自定义 UI，而不是通过并行状态。

在实现直接 iframe 后备清理时，将 iframe 媒体视为跨域 DOM。不要用父页面的 `el instanceof HTMLMediaElement` 测试 iframe 节点；在真实浏览器中返回 false。使用 `el.ownerDocument.defaultView.HTMLMediaElement`（或等效的标签/鸭型守卫）在设置 `muted` 或调用 `pause()` 之前。

### 全局导航静音

当 `<hyperframes-slideshow sound>` 渲染导航静音按钮时，该按钮是页面的全局静音控制。它必须静音：

- 子 `<hyperframes-player>` 实例，包括同源 iframe 媒体；
- 顶级页面 `<audio>` / `<video>` 元素；以及
- 包装器拥有的 SFX/全局 `Audio` 对象通过 `hf-sound` 事件。

不要在组合内添加第二个静音按钮。如果包装器脚本创建了未附加到 DOM 的 `new Audio(...)` 对象，它必须监听 `hf-sound` 并在每个对象上设置 `clip.muted = detail.muted`，而不仅仅是跳过未来的播放。

这里同样适用跨域规则：全局静音必须通过子框架的 DOM 域传递给 iframe `<video>` / `<audio>` 元素。在一个 DOM 域中通过传递单元测试并不够；在浏览器中验证点击导航静音按钮后实际 iframe 媒体元素报告 `muted: true`。

`hyperframes present` 从 `packages/player/dist` 提供构建的捆绑包。在更改播放器或 slideshow 界面行为后，在 `packages/player` 中运行 `bun run build` 并重启演示服务器，然后才能在浏览器中测试。

---

## 独立运行 slideshow（过渡方案）

**持久解决方案**是引擎托管：`hyperframes preview --slideshow` / studio 演示模式将组合在真实的 HyperFrames 引擎上托管，该引擎驱动搜索时间轴、拥有手势帧，并从组合中读取岛屿。这条路径即将到来；一旦发布，请优先使用它。

在此之前，独立演示（通过浏览器中的裸播放器捆绑包打开的组合，没有引擎）需要三个差距的工作绕过：组合必须暴露一个可搜索的根时间轴，岛屿必须复制到包装器中，包装器拥有的 SFX/全局音频应存在于父框架中。这些模式记录在：

```
skills/slideshow/references/standalone-harness.md
```

不要将这些模式视为神圣模型——它们仅存在以填补引擎托管路径落地前的差距。

## 交接

对于公共或面向用户的 slideshow 项目，根 `index.html` 应该是一个可运行的 slideshow 入口点。在浏览器中打开它应该显示 slideshow 导航并响应 Next/Prev；它不应该只暴露原始组合并要求用户了解 Studio 或内部包装器文件。如果原始 HyperFrames 组合必须为 CLI 兼容性保持分离，请将其放在子目录中，例如 `composition/index.html`，并让脚本/命令指向该目录。

直接打开的包装器必须依赖 `<hyperframes-slideshow>` 渲染的内置 Present 图标按钮。不要添加定制的 `#present-btn`、固定位置按钮或包装器特定的 Present 样式。共享组件拥有控制条，在 `?mode=audience` 时隐藏 Present，并支持 P 作为键盘快捷键。

在交接前验证直接打开路径。如果 `file://` 浏览器限制破坏了 iframe 媒体、本地脚本或同源播放器访问，使用自包含包装器或让交接命令启动本地服务器并打开工作 URL；不要让 `index.html` 处于损坏或模糊的状态。

对于完成的 slideshow deck，主要的面向用户下一步是演示者模式，而不是 Studio。运行或提供：

```bash
npx hyperframes present <project-dir>
```

工作室/`预览`功能可用于编辑一个演示文稿，但它并不是一个清晰明确的最终目的地。如果你为演示文稿项目创建一个`package.json`，其中原始演示文稿位于`composition/`目录下，请将默认的可执行脚本设置为启动演示者模式：

```json
{
  "scripts": {
    "dev": "npx hyperframes present ./composition",
    "studio": "npx hyperframes preview ./composition --background"
  }
}
```

在交接时，请包含命令打印的本地演示者URL，以及最简短的说明：“点击演示，或按P键，以打开观众标签页。”如果用户将通过Google Meet或Zoom进行演示，请传递上述“演示”部分中的屏幕共享指南（在Meet中共享观众标签页；在Zoom中拖出一个观众窗口）。如果用户要求你启动服务器，请保持服务器运行。

---

## 验证

在创建或编辑演示文稿后，运行：

```bash
npx hyperframes lint
```

然后运行运行时验证：

```bash
npx hyperframes check
```

将lint错误和验证`StaticGuard`契约消息视为阻断点，即使命令成功退出也是如此。修复文件并重新运行，直到lint报告`0 error(s)`且验证报告无运行时错误。

演示文稿lint规则检查：

- 每个`slide.sceneId`解析到一个存在的场景（通过`data-composition-id`）。
- 每个`hotspot.target`引用一个已定义的`slideSequence` ID。
- 片段时间位于每个幻灯片的`[start, end]`范围内。
- 没有两个主线幻灯片在时间上重叠。

在预览前修复所有违规。一个失败的lint的演示文稿在播放器中无法正确解析。
