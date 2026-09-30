---
name: hyperframes-registry
description: 搜索、安装并将注册块和组件连接到 HyperFrames 组合中。在构建任何命名视觉元素之前使用——无论是简报、用户还是故事板命名了外观、效果、处理方式或过渡效果，如 CRT 扫描线、故障、色差、胶片颗粒、闪烁扫描、图表、代码或终端窗口、地图或五彩纸屑爆发——因为大约 400 个托管项目已经涵盖了其中许多，并且搜索会以未安装任何内容、无项目和无账户的方式对所有项目进行排名。此外，在运行 HyperFrames 添加或 HyperFrames 目录时使用，安装一个项目或所有匹配标签的块，将已安装的项目连接到 index.html，或处理 hyperframes.json。涵盖发现、安装位置、块子组合连接、组件片段合并，以及编写新块或组件以向上游贡献（想法→脚手架→验证→PR）。
---

**插件安装：** 在设置或新鲜度命令之前，当此技能位于 HyperFrames 插件内时，请遵循 [插件执行规则](../hyperframes/references/plugin-installation.md)。独立安装保留以下更新说明。

# HyperFrames 注册中心

注册中心提供可重用的模块和组件，可通过 `hyperframes add <name>` 安装。

- **模块** — 独立子组合（拥有自己的尺寸、持续时间、时间轴）。通过在宿主组合中使用 `data-composition-src` 包含。
- **组件** — 特效片段（没有自己的尺寸）。直接粘贴到宿主组合的 HTML 中。

## 快速参考

```bash
hyperframes add data-chart              # 安装一个模块
hyperframes add grain-overlay           # 安装一个组件
hyperframes add captions                # 安装所有标记为 captions 的模块
hyperframes add shimmer-sweep --dir .   # 针对特定项目
hyperframes add data-chart --json       # 机器可读输出
hyperframes add data-chart --no-clipboard  # 跳过剪贴板 (CI/无头)
```

安装后，CLI 会打印出已写入的文件以及粘贴到宿主组合中的代码片段。该代码片段是一个起点 — 当连接模块时，您需要添加 `data-composition-id`（必须与模块的内部组合 ID 匹配）、`data-start` 和 `data-track-index` 属性。

位置值首先解析为确切的项目名称。如果没有匹配的项目且值为标签，则命令会安装所有具有该标签的模块。注册中心依赖项会在请求的项目之前安装。`hyperframes add` 仅适用于模块和组件；对于示例，请使用 `hyperframes init <dir> --example <name>`。

## 安装位置

模块默认安装到 `compositions/<name>.html`。组件默认安装到 `compositions/components/<name>.html`。

这些路径在 `hyperframes.json` 中可配置：

```json
{
  "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
  "paths": {
    "blocks": "compositions",
    "components": "compositions/components",
    "assets": "assets"
  }
}
```

有关详细信息，请参阅 [install-locations.md](./references/install-locations.md)。

## 连接模块

模块是独立的组合 — 通过在您的宿主 `index.html` 中使用 `data-composition-src` 包含它们：

```html
<div
  data-composition-id="data-chart"
  data-composition-src="compositions/data-chart.html"
  data-start="2"
  data-duration="15"
  data-track-index="1"
  data-width="1920"
  data-height="1080"
></div>
```

关键属性：

- `data-composition-src` — 模块 HTML 文件的路径
- `data-composition-id` — 必须与模块的内部 ID 匹配
- `data-start` — 模块在宿主时间轴上出现的时间（秒）
- `data-duration` — 模块播放的时长
- `data-width` / `data-height` — 模块画布尺寸
- `data-track-index` — 图层顺序（数值越高 = 越靠前）

有关详细信息，请参阅 [wiring-blocks.md](./references/wiring-blocks.md)。

## 连接组件

组件是片段 — 将其 HTML 粘贴到组合的标记中，其 CSS 粘贴到样式块中，其 JS（如有）粘贴到脚本中：

1. 读取安装的文件（例如，`compositions/components/grain-overlay.html`）
2. 将 HTML 元素复制到组合的 `<div data-composition-id="...">` 中
3. 将 `<style>` 块复制到组合的样式
4. 将任何 `<script>` 内容复制到组合的脚本（在时间轴代码之前）
5. 如果组件提供 GSAP 时间轴集成（请参阅片段中的注释块），请将这些调用添加到时间轴

有关详细信息，请参阅 [wiring-components.md](./references/wiring-components.md)。

## 发现

使用 CLI 作为主要发现界面。**在浏览之前按意图搜索：** 注册中心包含比您肉眼扫描更多的项目，因此按名称或标签列出它们并匹配是缓慢的路径，并且当作者的措辞与您的不同时，它会失败。

```bash
# 将整个目录与应该执行的操作进行排名
npx hyperframes catalog --query "一次一行地显示一个标题"
npx hyperframes add caption-clip-wipe
```

搜索是本地的，不会发送任何内容。默认情况下，它根据与项目名称、标题和描述共享的词汇进行排名，因此它只会找到重用您用词的项目；`--on-device` 通过一次性模型下载按含义进行排名。使用 `--json` 时，会显示哪些包名被排名，因此请检查它而不是假设发生了排名。

**始终使用英语进行查询，无论视频是什么语言。** 目录是用英语编写的，并且两种排名方式都是按这种方式索引它的（离线模型也是英语的）。使用其他脚本进行查询将不会产生可搜索的术语，并且会返回任何内容。在日语或中文项目中，这很容易出错，其中简报、字幕和旁白都是用那种语言编写的，查询自然也是：用英语描述动作，然后在视频需要的任何语言中编写屏幕上的文本。如果查询返回 `No searchable words in query`，那是因为这个规则，而不是缺少组件，不值得提交差距报告。

排名是在可安装性之后应用的，而不是之前：一个向量携带但此注册中心无法提供名称会被从结果中删除并计入 `dropped`，因此非零的 `dropped` 表示两者是不同的版本。有关详细信息，请参阅 `/hyperframes-cli` 中的离线排名、同意门和如何刷新过时的索引。

要浏览或过滤而不是搜索：

```bash
npx hyperframes catalog
npx hyperframes catalog --type block
npx hyperframes catalog --type component
npx hyperframes catalog --type block --tag social
npx hyperframes catalog --json
npx hyperframes catalog --human-friendly
```

正常表格和 `--json` 模式仅列出匹配项；使用 `hyperframes add <name>` 安装选定的名称。`--human-friendly` 打开交互式选择器并立即安装选定的项目。在 CI 或代理工作流中，请优先使用 `--json` 后跟显式的 `add`。

### 报告目录中缺少的内容

当搜索返回且其中没有任何内容执行工作时，在您手动编写动作之前说明：

```bash
npx hyperframes feedback --search-miss "<您运行的查询>" --wanted "<您需要的动作>" --tier on-device
```

`catalog --query` 会为您打印此行并预填充，而 `--json` 会将其作为 `report_gap` 带走 — 因此在您决定没有任何匹配项时，它已经在手头。

**无论在哪种排名方式下，当结果中没有任何内容执行工作时，都要报告。** 不要等待离线排名方式回答：它需要 33 MB 的同意下载，因此除非它明确选择加入，否则代理运行是 `words`；在 `on-device` 上设置门会几乎沉默每个报告。`--tier` 值会一起传递，因此当读取时，词汇缺失与含义缺失是可区分的。描述您想要的效果，而不是您想象的项名称：返回的是一组值得构建的动作，而命名不存在的项不会教您任何东西。这是唯一发送查询的路径，这也是为什么它是一个独立的故意命令，而不是搜索自己做的事情。它不携带评分，也永远不会出现在评分指标中。

这是目录的整个需求信号。跳过它意味着您遇到的差距会根据安装计数进行猜测，而安装计数无法看到无人可以安装的动作。

如果 CLI 无法访问配置的注册中心，请将原始清单作为备用进行检查：

```bash
curl -s https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry/registry.json
```

CLI 无法访问的注册中心**不会**使目录为**发现**空：以前获取的清单在重新验证失败时仍会在其 24 小时刷新窗口内提供服务，因此 `catalog` 和 `catalog --query` 仍然会列出并针对磁盘上的最后一个副本进行排名。

**即使对于您昨天安装的项目，`add` 仍然需要网络。** 只有清单被缓存；项目的实际文件在每次安装时都会获取。因此，离线时您可以搜索，并且可以看到一个项目的样子，但安装它会在文件获取时失败。不要向用户承诺离线安装。

每个项目的 `registry-item.json` 包含：名称、类型、标题、描述、标签、尺寸（仅限模块）、持续时间（仅限模块）和文件列表。

有关按类型和标签进行过滤的详细信息，请参阅 [discovery.md](./references/discovery.md)。

## 贡献新的模块或组件

要编写一个新的注册中心项目（字幕样式、VFX 模块、过渡、低 thirds 或可重用组件）并将其作为上游 PR 发送（而不是安装现有的项目）— 请遵循 [contributing.md](./references/contributing.md) 中的完整想法 → 框架 → 构建 → 验证 → 预览 → 发送工作流。字幕 / VFX / 组件 / `registry-item.json` 的启动模板在 [templates.md](./references/templates.md) 中。
