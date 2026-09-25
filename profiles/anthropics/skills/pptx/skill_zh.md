# PPTX 创建、编辑和分析

`.pptx` 是一个包含 XML 文件的 ZIP 压缩包。根据任务选择你的方法：

| 任务 | 方法 |
|---|---|
| **创建** 新演示文稿 | 编写 `pptxgenjs` 脚本 — 下方有注意事项 |
| **编辑** 现有演示文稿，或从模板构建 | 解压 → 编辑 `ppt/slides/slideN.xml` → 压缩 |
| **读取** 内容 | `markitdown deck.pptx` (每个幻灯片在 `<!-- Slide number: N -->` 标记下为一块内容)；视觉网格：`python scripts/thumbnail.py deck.pptx` |

## 脚本

路径相对于此技能的目录。其他都是普通的 Python、`node` 或 shell。

| 脚本 | 它的作用 |
|---|---|
| `scripts/thumbnail.py deck.pptx [prefix]` | 每个幻灯片的标记网格，用于选择模板布局。仅限 `.pptx`。传递 `prefix` — 它默认为 `thumbnails`，会覆盖同一目录中其他演示文稿的网格 |
| `scripts/add_slide.py unpacked/ slide2.xml [--after slideN.xml]` | 复制幻灯片（或 `slideLayoutN.xml`）并处理所有包的元数据。也接受 `.pptx` 直接使用 `-o out.pptx` |
| `scripts/clean.py unpacked/` | 删除不再引用的幻灯片、媒体和关系。在 `<p:sldIdLst>` 最终确定后运行 |
| `scripts/office/validate.py deck.pptx [--original src.pptx]` | 模式、关系、内容类型、图表和幻灯片检查；每个失败都命名其修复方法。传递 `--original` 用于任何模板派生的演示文稿 — 它将模式检查与模板基线，因此模板自身的 XSD 错误不会显示为你的错误 |
| `scripts/office/soffice.py --headless --convert-to pdf deck.pptx` | LibreOffice 包装器 — 纯 `soffice` 在此沙盒中挂起 |

## 使用 pptxgenjs 创建 — 注意事项

`pptxgenjs` 预装 — 不要先运行 `npm install`；直接编写脚本并 `require('pptxgenjs')`。只有在 `require` 失败时才：`npm install pptxgenjs`。模型知道 API；这些是脚手架：

- **在添加幻灯片之前设置 `pres.layout`。** 默认画布是 `LAYOUT_16x9` = **10" × 5.625"**，不是 13.3" 宽。超出边缘的坐标会被写入，不会被裁剪 — 形状只是不在幻灯片上。 (`LAYOUT_WIDE` 是 13.3" × 7.5"。)
- **十六进制颜色：永远不要 `#`，永远不要 8 位。** `color: "FF0000"`。`"#FF0000"` 和十六进制中嵌入的 alpha (`"00000020"`) **都会损坏文件**。对于透明度：`transparency: 0-100` 用于填充和图像，`opacity: 0.0-1.0` 用于阴影 — 每个都会在另一个上被静默忽略。
- **pptxgenjs 会原地修改选项对象**（第一次使用时将值转换为 EMU）。永远不要在两个 `add*` 调用之间共享一个 `shadow`/选项对象 — 每次都构建一个新对象。
- **阴影 `offset` 必须≥ 0** — 负偏移会损坏文件。要向上投射阴影，请使用 `angle: 270` 和正偏移。
- **`letterSpacing` 被静默忽略** — 真正的选项是 `charSpacing`。
- **列表：** 每个项目上 `bullet: true`，永远不要字面量 `•`（会渲染双项目）。在每个数组项目上（最后一个除外）设置 `breakLine: true`。使用 `paraSpaceAfter` 而不是 `lineSpacing` 空白项目符号段落（会产生巨大间隙）。
- **每个输出文件一个 `new pptxgen()`** — 永远不要重用实例。
- **`rectRadius` 仅适用于 `ROUNDED_RECTANGLE`**，不适用于 `RECTANGLE`。
- **不支持渐变填充** — 用渐变图像作为背景代替。
- **文本框有内置的内部填充** — 每次文本必须与形状、线条或图标对齐时，设置 `margin: 0`。
- **演讲者笔记放在 `slide.addNotes("...")`**（纯文本，每个幻灯片一次），永远不要放在幻灯片上的文本框中。
- **保持图表原生。** 使用 `addChart()` 用于 PowerPoint 可以图表的所有内容（为组合传递 `{type, data, options}`）。对于库不暴露的 PowerPoint 原生功能（趋势线、误差线），自己计算额外的系列或后处理生成的 OOXML — 不要退回到渲染的图像。只有 PowerPoint 没有原生形式的图表类型（Sankey、网络、和弦）才作为图像输入。
- **默认图表渲染为空** — 没有标题，没有数据标签，日期调色板。设置 `showTitle` + `title`，`showValue: true` + `dataLabelPosition`，`chartColors: [...]` 从你的调色板，并静默化框架 (`catAxisLabelColor`/`valAxisLabelColor`，`valGridLine: { color, size }`，`catGridLine: { style: "none" }`，单系列为 `showLegend: false`）。
- **在堆叠条形图或柱状图中，`dataLabelPosition` 必须是 `ctr`，`inEnd` 或 `inBase`。** `outEnd` **会损坏文件**。
- **使用 `secondaryValAxis`/`secondaryCatAxis` 的组合系列需要图表选项中的 `valAxes` 和 `catAxes`，每个两个条目。** 没有，pptxgenjs 会写入 PowerPoint 从未声明的轴 *id*，并且 PowerPoint **会丢弃该图表** 并报告文件损坏。只提供 `valAxes` 不够。
- **在 `writeFile()` 后，运行 `python scripts/office/validate.py deck.pptx`。** 它报告上述两个图表错误以及 PowerPoint 拒绝的幻灯片-XML 缺陷，并命名每个修复方法。在你的生成器中修复它们，而不是手动编辑打包的 XML。
- **永远不要重新排序 `<p:presentation>` 的子元素。** pptxgenjs 在 `<p:sldIdLst>` 后立即写入 `<p:notesMasterIdLst>` 并将两个主模板指向一个主题部分。PowerPoint 欢快地读取它 — 移动元素，相同的演示文稿变得无法打开。
- **图标：** 渲染 `react-icons` 到 SVG (`ReactDOMServer.renderToStaticMarkup`)，使用 `sharp` 以 ≥256px 光栅化，并通过 `addImage({ data: "image/png;base64," + buf.toString("base64") })` 插入 — 需要 `image/png;base64,` 前缀 (`react-icons`、`react`、`react-dom` 和 `sharp` 预装 — 只有 `require` 失败时才 `npm install react-icons react react-dom sharp`）。

## 编辑现有演示文稿和模板

首先选择布局：`python scripts/thumbnail.py template.pptx template-thumbs` 写出每个幻灯片的标记网格并打印创建的文件 — `template-thumbs.jpg`，超过 12 张幻灯片后分割为 `template-thumbs-N.jpg`。**始终传递第二个参数，以演示文稿命名。** 它默认为 `thumbnails`，因此同一目录中两个演示文稿的网格会被静默覆盖 — 第一个演示文稿的网格 simply 消失（仅模板分析 — 视觉质量保证需要从 [转换为图像](#converting-to-images) 的全分辨率渲染；它只接受 `.pptx`，因此先将 `.potx` 复制为 `.pptx` 名称）。使用它与 `markitdown` 将每个内容部分映射到模板幻灯片，并更改布局 — 不要将所有部分放在相同的标题和项目符号幻灯片上。

```bash
python3 -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall('unpacked')" deck.pptx
python scripts/add_slide.py unpacked/ slide2.xml --after slide2.xml   # 复制幻灯片（或 slideLayoutN.xml）；打印新幻灯片的路径
# 重新排序 / 删除幻灯片 = 编辑 `ppt/presentation.xml` 中的 `<p:sldIdLst>`
python scripts/clean.py unpacked/                                     # 删除后：删除孤儿幻灯片、媒体、rels
# 在 `ppt/slides/slideN.xml` 中编辑幻灯片内容
(cd unpacked && rm -f ../out.pptx && zip -Xr ../out.pptx .)           # 从内部目录压缩；首先删除或保留已删除的部分
python scripts/office/validate.py out.pptx --original deck.pptx
```

- **在编辑任何幻灯片内容之前完成所有结构工作 — 添加、删除、重新排序。** `add_slide.py` 精确复制幻灯片文件，因此在你编辑后复制编辑后的内容；并且 `clean.py` 会删除 `<p:sldIdLst>` 中缺失的任何幻灯片，包括你刚刚编写的。
- **永远不要手动复制幻灯片文件** — `add_slide.py` 执行新幻灯片需要的所有注册，并报告它创建了什么 (`Created ppt/slides/slide17.xml from slide2.xml`)。它也直接在文件上工作：`add_slide.py deck.pptx slide2.xml -o out.pptx` — **传递 `-o`，否则它会原地重写输入的演示文稿。** 复制的幻灯片仍然引用其来源的图表/SmartArt/嵌入对象部分，而不是克隆它们，因此编辑一个幻灯片的图表会改变另一个幻灯片。
- **如果你使用 `python-pptx`**，有三个东西它不会做：复制幻灯片（它的唯一入口点是 `add_slide(layout)`），通过 `text_frame.text = "..."` 保留格式（那会将段落折叠为单个未加修饰的运行 — 而分配 `run.text`），或读取大多数模板艺术使用的 SVG/EMF (`add_picture` 抛出 `UnidentifiedImageError`）。
- 遗留的 `.ppt` 必须先转换：`python scripts/office/soffice.py --headless --convert-to pptx file.ppt`。`.potx` 模板解压和打包完全相同 — 在输出上保留 `.potx` 扩展名。
- 要重用模板图标或图像，复制包含它的幻灯片或布局。

填充模板时：

- 如果你编写 XML 转换，使用 `defusedxml.minidom` 解析 — 通过 `xml.etree.ElementTree` 循环 OOXML 会重写命名空间前缀并损坏演示文稿。
- **模板插槽≠源项目。** 如果模板显示 4 个团队成员而你只有 3 个，请删除第 4 个成员的整个组（图像 + 文本框），而不是只删除其文本 — 然后在质量保证中检查孤儿视觉元素。
- 每个 `<a:p>` 对应一个列表项 — 永远不要将项目连接到一个段落中。复制兄弟 `<a:pPr>` 以保留间距，并在标题、节标题和内联标签（`Status:`，`Owner:`）的 `<a:rPr>` 上放置 `b="1"`。
- 让项目符号从布局继承；只添加 `<a:buChar>`，`<a:buAutoNum>`（编号）或 `<a:buNone>` 来覆盖 — 永远不要在文本中使用字面量 `•`。
- 带有前导或尾随空格的文本需要在它的 `<a:t>` 上设置 `xml:space="preserve"`。

## 设计建议

**不要创建无聊的幻灯片。** 白色背景上的纯项目符号不会吸引任何人。考虑此列表中的每个幻灯片的设计想法。

### 开始之前

- **选择一个内容相关的鲜明调色板**：调色板应该感觉是为这个主题设计的。如果你的颜色交换到完全不同的演示文稿中仍然“有效”，那么你做的选择不够具体。
- **主导权而非平等**：一种颜色应该主导（60-70% 视觉权重），1-2 个支持色调和一个鲜明的强调色。永远不要给所有颜色相同的权重。
- **明暗对比**：标题和结论幻灯片使用深色背景，内容使用浅色（“三明治”结构）。或者坚持整个深色以获得高级感。
- **坚持一个视觉主题**：选择一个独特的元素并重复它 — 圆角图像框架、彩色圆圈中的图标。贯穿每一张幻灯片。**不要使用颜色条或强调条纹作为你的主题**（见避免列表）。

### 调色板

选择与你的主题匹配的颜色 — 不要默认使用通用蓝色。使用这些调色板作为灵感：

| 主题 | 主要 | 次要 | 强调 |
|-------|---------|-----------|--------|
| **午夜执行** | `1E2761`（海军蓝） | `CADCFC`（冰蓝色） | `FFFFFF`（白色） |
| **森林与苔藓** | `2C5F2D`（森林） | `97BC62`（苔藓） | `F5F5F5`（奶油色） |
| **珊瑚能量** | `F96167`（珊瑚） | `F9E795`（金色） | `2F3C7E`（海军蓝） |
| **温暖陶土** | `B85042`（陶土） | `E7E8D1`（沙子） | `A7BEAE`（鼠尾草） |
| **海洋渐变** | `065A82`（深蓝色） | `1C7293`（蓝绿色） | `21295C`（午夜） |
| **煤灰简约** | `36454F`（煤灰） | `F2F2F2`（浅灰色） | `212121`（黑色） |
| **蓝绿色信任** | `028090`（蓝绿色） | `00A896`（海藻绿） | `02C39A`（薄荷绿） |
| **浆果与奶油** | `6D2E46`（浆果） | `A26769`（尘埃玫瑰） | `ECE2D0`（奶油色） |
| **鼠尾草平静** | `84B59F`（鼠尾草） | `69A297`（桉树） | `50808E`（板岩） |
| **樱桃大胆** | `990011`（樱桃） | `FCF6F5`（浅灰色） | `2F3C7E`（海军蓝） |

### 每张幻灯片

**每张幻灯片需要一个视觉元素** — 图像、图表、图标或形状。纯文本幻灯片是容易被遗忘的。

**布局选项：**
- 两列（文本在左侧，插图在右侧）
- 图标 + 文本行（图标在彩色圆圈中，粗体标题，下方为描述）
- 2x2 或 2x3 网格（一侧为图像，另一侧为内容块网格）
- 半出血图像（左侧或右侧全宽）与内容叠加

**数据展示：**
- 大型统计调用（60-72pt 大号数字，下方为小标签）
- 比较列（之前/之后，优缺点，并排选项）
- 时间线或流程（编号步骤，箭头）

**视觉润色：**
- 在节标题旁边放置小彩色圆圈中的图标
- 使用斜体强调文本来突出关键统计数据或标语

### 字体

**你写入 .pptx 的字体名称由用户的 PowerPoint 渲染，而不是由此环境渲染。** 你的视觉质量保证通过 LibreOffice 渲染，它用自己没有的字体替换 — 对于某些字体，替换字体的宽度不同，因此你的质量保证预览可能会显示文本溢出（或适合），而实际演示文稿不会。为了保持你的质量保证值得信赖：

- **安全字体**（在质量保证中按真实宽度渲染，并随 Office 提供）：**Arial、Calibri、Cambria、Times New Roman、Courier New、Bookman Old Style、Century Schoolbook**。用于正文文本和任何对齐很重要的地方。
- **具有个性的标题**：将安全列表中的衬线标题（Cambria、Bookman Old Style、Century Schoolbook）与安全列表的无衬线正文（Calibri 或 Arial）配对。你获得视觉对比，而不会放弃可靠的溢出检查。
- **如果用户要求安全列表之外的字体**（例如 Georgia 或 Trebuchet MS）：在用户要求的地方使用它，但为这些容器提供额外的松弛（~10%），并且不要信任该字体的质量保证文本对齐 — 该字体的预览是近似的。如果用户没有指定，优先为正文文本使用安全列表字体。
- **质量保证不可靠的字体**（替换字体宽度不同 — 溢出检查可能出错）：Georgia、Trebuchet MS、Impact、Arial Black、Garamond、Consolas、Palatino Linotype。Calibri Light 替换因环境而异；视为质量保证不可靠。适合标题/强调，不要信任这些字体的质量保证文本对齐。
- **永远不要默认使用 Aptos** — Office 的 2023 年后默认字体在此处没有兼容的替换，并且缺少旧版 Office 安装中，因此它在两端都不可靠。

| 元素 | 大小 |
|---------|------|
| 幻灯片标题 | 36-44pt 粗体 |
| 节标题 | 20-24pt 粗体 |
| 正文文本 | 14-16pt |
| 捕述 | 10-12pt 淡色 |

### 间距

- 最小边距 0.5"
- 内容块之间 0.3-0.5"
- 留出呼吸空间 — 不要填满每一英寸

### 避免（常见错误）

- **不要重复相同的布局** — 在幻灯片上更改列、卡片和调用
- **不要居中文本** — 左对齐段落和列表；只居中标题
- **不要节省大小对比** — 标题需要 36pt+ 才能从 14-16pt 正文突出
- **不要默认使用蓝色** — 选择与特定主题匹配的颜色
- **不要随机混合间距** — 选择 0.3" 或 0.5" 间隙并始终一致使用
- **不要只样式化一张幻灯片而让其他幻灯片保持空白** — 全部坚持或保持简单
- **不要创建纯文本幻灯片** — 添加图像、图标、图表或视觉元素；避免纯标题 + 项目符号
- **不要忘记文本框填充** — 当对齐线条或形状与文本边缘时，在文本框上设置 `margin: 0` 或将形状偏移以解释填充
- **不要使用低对比度元素** — 图标和文本都需要与背景强对比；避免浅色背景上的浅色文本或深色背景上的深色文本
- **绝对不要在标题下方添加装饰线** — 这些是 AI 生成的幻灯片的标志；使用空白或背景颜色代替
- **绝对不要添加装饰色条或强调条纹** — 这包括：跨越幻灯片宽度的页眉/页脚条、垂直边框条纹、卡片或内容块边缘的细强调条纹，以及“单边边框”在矩形上。这些看起来像 AI 生成的填充。如果你想把卡片区分开来，使用微妙的背景色调、阴影或图标 — 而不是边缘条纹。
- **不要默认使用奶油色/米色背景** — 如果未指定背景，使用白色 (`FFFFFF`) 或用户的品牌调色板；避免暖中性默认值，如 `F5F5DC`、`FAF0E6`、`FAEBD7`、`FFF8E1`
- **不要发送溢出形状的文本** — 如果文本不适应，减小字体大小、跨幻灯片分割或扩大容器；永远不要留下内容被截断或溢出边界

## 质量保证（必需）

你的第一次渲染通常有几个真实问题 — 重叠、溢出、错位。找到并修复这些问题，只重新渲染你更改的幻灯片，然后停止。

### 内容质量保证

```bash
markitdown output.pptx
```

检查是否有缺失的内容、拼写错误、顺序错误。

**使用模板时，检查是否有剩余的占位符文本：**

```bash
markitdown output.pptx | grep -iE "\bx{3,}\b|lorem|ipsum|\bTODO|\[insert|this.*(page|slide).*layout"
```

如果 grep 返回结果，在宣布成功之前修复它们。

### 文件质量保证（必需）

```bash
python scripts/office/validate.py output.pptx                      # 从头开始构建
python scripts/office/validate.py output.pptx --original src.pptx  # 从模板构建
```

**如果演示文稿来自模板，始终传递 `--original`。** 模板本身可能包含 XSD 拒绝的部分，因此纯运行可以报告你从未造成的失败 — 并且真实的回归可能隐藏在它们之中。`--original` 将模式和幻灯片检查与模板基线，抑制模板已经有的错误。结构检查 — 关系、内容类型、图表 — 忽略 `--original` 并报告模板继承的问题，无论是否传递，所以根据自己的价值阅读它们。pptxgenjs 发射 PowerPoint 拒绝打开的图表 XML，而每个其他工具都接受：python-pptx 打开这些演示文稿，LibreOffice 渲染它们，XSD 通过它们。每个失败都命名其修复方法。在生成器中修复它们并重新构建。**

### 视觉质量保证

将幻灯片转换为图像（见 [转换为图像](#converting-to-images)）并检查每一个。在盯着生成代码后，你倾向于看到你期望的而不是渲染的，因此要新鲜地查看图像（如果你有子代理，这很好用）。要查找用户可见的缺陷：

- **文本溢出或文本在框或幻灯片边界处被截断 — 首先检查这个。** 它是最常见的缺陷，并且总是用户可见的。（对于预览器渲染不可靠的字体，预览是近似的：信任你留下的 ~10% 松弛，而不是它的实际适应情况。）
- 重叠元素（文本通过形状，线条通过文字，堆叠元素）
- 源引用或页脚与上方内容冲突
- 元素太近（< 0.3" 间隙）或卡片/节几乎接触
- 不均匀的间隙（一个地方有大片空白区域，另一个地方拥挤）
- 边缘与幻灯片边缘不足 (< 0.5")
- 列或类似元素对齐不一致
- 低对比度文本（例如，浅灰色文本在奶油色背景上）
- 模板装饰定位错误后文本替换 — 例如，标题下划线定位为一条线，但替换的标题换行到两条线
- 低对比度图标（例如，深色图标在深色背景上没有对比圆圈）
- 文本框太窄导致过度换行
- 剩余占位符内容

## 转换为图像

将演示文稿转换为单个幻灯片图像以进行视觉检查：

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
rm -f slide-*.jpg
pdftoppm -jpeg -r 150 output.pdf slide
ls -1 "$PWD"/slide-*.jpg
```

**将上面打印的绝对路径直接传递给查看工具。** `rm` 清除先前的运行图像。`pdftoppm` 基于页数零填充：`slide-1.jpg` 用于少于 10 张幻灯片的演示文稿，`slide-01.jpg` 用于 10-99 张，`slide-001.jpg` 用于 100 张以上。

**修复后，重新运行上述四个命令** — PDF 必须从编辑的 `.pptx` 重新生成，然后 `pdftoppm` 才能反映你的更改。

## 依赖项

`pptxgenjs` (npm, 预装 — 只有 `require('pptxgenjs')` 失败时才安装) · `markitdown[pptx]`, `Pillow`, `defusedxml`, `lxml` (pip — 文本转储，缩略图，清理，验证) · LibreOffice (`soffice`, 通过 `scripts/office/soffice.py` 自动配置为沙盒环境) · `pdftoppm` (Poppler)
