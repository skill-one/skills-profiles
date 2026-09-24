# HyperFrames Registry

注册表提供可通过 `hyperframes add <name>` 安装的复用块和组件。

- **Blocks** — 独立子组合（拥有自身尺寸、时长、时间轴）。通过 `data-composition-src` 包含在宿主组合中。
- **Components** — 效果代码片段（无自身尺寸）。直接粘贴到宿主组合的 HTML 中。

## 快速参考

```bash
hyperframes add data-chart              # 安装一个块
hyperframes add grain-overlay           # 安装一个组件
hyperframes add captions                # 安装所有标记为 captions 的块
hyperframes add shimmer-sweep --dir .   # 针对特定项目
hyperframes add data-chart --json       # 机器可读输出
hyperframes add data-chart --no-clipboard  # 跳过剪贴板（CI/无头环境）
```

安装后，CLI 会打印所写入的文件以及需要粘贴到宿主组合的代码片段。该片段仅为起点——在连接块时，您需要添加 `data-composition-id`（必须与块的内部组合 ID 匹配）、`data-start` 和 `data-track-index` 属性。

位置参数首先解析为精确的项目名称。如果无匹配项且值为标签，则命令安装所有带有该标签的块。注册表依赖项在安装请求的项目之前安装。`hyperframes add` 仅用于块和组件；如需示例，请使用 `hyperframes init <dir> --example <name>` 替代。

## 安装位置

块默认安装到 `compositions/<name>.html`。组件默认安装到 `compositions/components/<name>.html`。

这些路径可在 `hyperframes.json` 中配置：

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

有关完整详情，请参阅 [install-locations.md](./references/install-locations.md)。

## 连接块

块是独立组合——通过 `data-composition-src` 在您的宿主 `index.html` 中包含它们：

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

- `data-composition-src` — 块 HTML 文件的路径
- `data-composition-id` — 必须与块的内部 ID 匹配
- `data-start` — 块在宿主时间轴中出现时的时间（秒）
- `data-duration` — 块的播放时长
- `data-width` / `data-height` — 块画布尺寸
- `data-track-index` — 层级排序（数值越大越靠前）

有关完整详情，请参阅 [wiring-blocks.md](./references/wiring-blocks.md)。

## 连接组件

组件是代码片段——将其 HTML 粘贴到组合的标记中，将其 CSS 粘贴到样式中，将其 JS 粘贴到脚本中（如有）：

1. 读取已安装的文件（例如 `compositions/components/grain-overlay.html`）
2. 将 HTML 元素复制到组合的 `<div data-composition-id="...">` 中
3. 将 `<style>` 代码块复制到组合的样式中
4. 将任何 `<script>` 内容复制到组合的脚本中（在时间轴代码之前）
5. 如果组件暴露 GSAP 时间轴集成（见代码片段中的注释块），则将相关调用添加到您的时间轴中

有关完整详情，请参阅 [wiring-components.md](./references/wiring-components.md)。

## 发现

使用 CLI 作为主要的发现入口。**先按意图搜索，再浏览：** 注册表中的项目数量远超肉眼扫描的范围，因此列出来并按名称或标签匹配是缓慢的路径，且在作者用词与您的用词不一致时就会失败。

```bash
# 根据 beat 应实现的功能对完整目录进行排序
npx hyperframes catalog --query "reveal a headline one line at a time"
npx hyperframes add caption-clip-wipe
```

搜索在本地进行，不会发送任何数据。默认情况下，它根据与项目名称、标题和描述共享的词汇进行排序，因此只能找到复用您所用词汇的项目；使用 `--on-device` 则按含义排序，但需要一次性下载模型。使用 `--json` 时，封装中会标识哪些层级的搜索有结果，因此请检查该信息而非假定有排序结果。

**始终用英文查询，无论视频的语言是什么。** 目录以英文编写，两个层级均以这种方式索引（设备端模型也仅支持英文）。其他语言脚本的查询无法产生可搜索的词汇，因此将返回空结果。这在日文或中文项目中容易出错——当简报、字幕和旁白都使用该语言，且查询自然地遵循该语境时。如果查询返回 `No searchable words in query`，这是遵循本规则的结果，而非组件缺失，也不值得报告缺口。

可安装性在排序之后应用，而非排序之前：向量携带但本注册表无法服务的名称会被从结果中剔除并计入 `dropped`，因此非零的 `dropped` 意味着两者属于不同版本。有关离线层级、同意门槛以及如何刷新过期的索引，请参阅 `/hyperframes-cli`。

如需替代搜索进行浏览或过滤：

```bash
npx hyperframes catalog
npx hyperframes catalog --type block
npx hyperframes catalog --type component
npx hyperframes catalog --type block --tag social
npx hyperframes catalog --json
npx hyperframes catalog --human-friendly
```

常规表格和 `--json` 模式仅列出匹配项；使用 `hyperframes add <name>` 安装选定的名称。`--human-friendly` 会打开交互式选择器并立即安装选定的项目。在 CI 或代理工作流中，建议优先使用 `--json` 后跟明确的 `add`。

### 报告目录中没有的内容

当搜索结果返回且其中没有任何内容能完成所需工作时，在手写该动作之前要明确指出：

```bash
npx hyperframes feedback --search-miss "<你运行的查询>" --wanted "<你需要的动作>" --tier on-device
```

`catalog --query` 会为你预先填充该行并打印，`--json` 则以 `report_gap` 形式携带——因此一旦你判定没有合适的内容，该信息已到手。

**无论哪个层级，只要结果中没有内容能完成任务，都要报告。** 不要等待设备端层级给出回答：它需要经过同意的 33 MB 下载，因此代理运行默认处于 `words` 层级，除非明确选择加入，基于 `on-device` 的门槛会使几乎所有的报告失效。`--tier` 值会随报告一同携带，以便在读取时，词汇缺失与含义缺失能够区分开来。描述你期望的效果，而非你想象中对应的项目名称：返回的是值得构建的动作列表，报告命名一个不存在的项目则毫无意义。这是唯一会将查询发送到任何地方的路径，这正是它作为单独的、有意的命令而非由搜索自行执行的原因。它不带评分，也永远不会进入评分指标。

这是目录的全部需求信号。跳过它意味着你遇到的缺口将改用安装计数来猜测，而这无法看到任何人都无法安装的动作。

如果 CLI 无法访问配置的注册表，请作为后备方案检查原始清单：

```bash
curl -s https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry/registry.json
```

CLI 无法访问的注册表**不会**为发现清空目录：在重新验证失败时，先前获取的清单仍会继续服务，直至超过其 24 小时刷新窗口，因此 `catalog` 和 `catalog --query` 仍会列出并基于磁盘上的最后一份副本进行排序。

**即使是为昨天安装的项目，`add` 仍需要网络。** 仅缓存清单；项目的实际文件每次安装时都会获取。因此离线时可以搜索，也可以查看项目是什么，但安装时会因文件获取失败。不要向用户承诺可离线安装。

每个项目的 `registry-item.json` 包含：名称、类型、标题、描述、标签、尺寸（仅块）、时长（仅块）和文件列表。

有关按类型或标签过滤的详情，请参阅 [discovery.md](./references/discovery.md)。

## 贡献新的块或组件

要编写新的注册表项目（字幕样式、VFX 块、转场、低三栏或可复用组件）并以上游 PR 的形式发布——而非安装已有的项目——请遵循 [contributing.md](./references/contributing.md) 中的完整流程：想法 → 脚手架 → 构建 → 验证 → 预览 → 发布。复制粘贴的起始模板（字幕 / VFX / 组件 / `registry-item.json`）位于 [templates.md](./references/templates.md)。
