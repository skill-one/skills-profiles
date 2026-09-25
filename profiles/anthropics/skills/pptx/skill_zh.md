# PPTX 创建、编辑与分析

`.pptx` 是一个 XML 文件的 ZIP 归档包。请根据任务选择方法：

| 任务 | 方法 |
|---|---|
| **创建** 新幻灯片套 | 编写一个 `pptxgenjs` 脚本 — 详见下方注意事项 |
| **编辑** 现有幻灯片套，或基于模板构建 | 解压 → 编辑 `ppt/slides/slideN.xml` → 打包 |
| **读取** 内容 | `markitdown deck.pptx`（每张幻灯片为一个块，位于 `<!-- Slide number: N -->` 标记下）；视觉网格：`python scripts/thumbnail.py deck.pptx` |

## 脚本

路径相对于本技能目录。其余均为普通 Python、`node` 或 shell。

| 脚本 | 功能 |
|---|---|
| `scripts/thumbnail.py deck.pptx [prefix]` | 每张幻灯片的标注网格，用于选择模板版式。仅支持 `.pptx`。传入 `prefix` — 默认为 `thumbnails`，会覆盖同目录下任何其他幻灯片套所做的网格 |
| `scripts/add_slide.py unpacked/ slide2.xml [--after slideN.xml]` | 复制幻灯片（或 `slideLayoutN.xml`），并完成所有包管理事务。也可直接接收 `.pptx` 并以 `-o out.pptx` 方式输出 |
| `scripts/clean.py unpacked/` | 删除不再被引用的幻灯片、媒体和关系。在 `<p:sldIdLst>` 确定后运行 **之后** 再运行 |
| `scripts/office/validate.py deck.pptx [--original src.pptx]` | 检查模式、关系、内容类型、图表和幻灯片；每次失败都会注明其修复方法。传入 `--original` 用于任何基于模板衍生的幻灯片套 — 它基于模板将模式检查作为基准，因此模板自身的 XSD 错误不会被视为你的问题 |
| `scripts/office/soffice.py --headless --convert-to pdf deck.pptx` | LibreOffice 封装 — 在沙盒中直接使用 `soffice` 会挂起 |

## 使用 pptxgenjs 创建 — 注意事项

`pptxgenjs` 已预装 — 不要先运行 `npm install`；直接编写脚本并 `require('pptxgenjs')`。仅当该 require 失败时：`npm install pptxgenjs`。模型了解该 API；以下为常见陷阱：

- **在添加幻灯片前设置 `pres.layout`。** 默认画布为 `LAYOUT_16x9` = **10" × 5.625"**，并非 13.3" 宽。超出边界的坐标会被写入，而非被限制 — 形状只是不会出现在幻灯片上。（`LAYOUT_WIDE` 为 13.3" × 7.5"。）
- **十六进制颜色：永远不要用 `#`，不要用 8 位数字。** 使用 `color: "FF0000"`。`"#FF0000"` 和将透明度内置进十六进制（`"00000020"`）**都会损坏文件**。如需透明度：在填充和图片上使用 `transparency: 0-100`，在阴影上使用 `opacity: 0.0-1.0` — 两者在对方上会被静默忽略。
- **pptxgenjs 会原地修改选项对象**（首次使用时将值转换为 EMU）。永远不要在两个 `add*` 调用间共享同一个 `shadow`/选项对象 — 每次都要构建一个新的。
- **阴影 `offset` 必须 ≥ 0** — 负偏移会损坏文件。要向上投射阴影，请使用 `angle: 270` 配合正偏移。
- **`letterSpacing` 会被静默忽略** — 真正的选项是 `charSpacing`。
- **列表：** 每个项目都设置 `bullet: true`，永远不要用字面量 `•`（会渲染双 bullets）。除最后一个数组项外，每个项都设置 `breakLine: true`。为项目符号段落之间加空行，使用 `paraSpaceAfter`，而不是 `lineSpacing`（会产生很大的间距）。
- **每个输出文件只用一个 `new pptxgen()`** — 永远不要复用实例。
- **`rectRadius` 仅对 `ROUNDED_RECTANGLE` 有效，** 而非 `RECTANGLE`。
- **不支持渐变填充** — 请改用渐变图片作为背景。
- **文本框内置内部填充** — 当文本必须与某个形状、线条或图标在同 x 位置对齐时，总是设置 `margin: 0`。
- **演讲者备注通过 `slide.addNotes("...")`** 放入（每张幻灯片一行纯文本），永远不要放在幻灯片上的文本框内。
- **保持图表原生。** 使用 `addChart()` 处理 PowerPoint 能制表的全部内容（传递 `{type, data, options}` 数组用于组合类型）。库未暴露的 PowerPoint 原生功能（趋势线、误差棒），请自行计算额外系列或后处理生成的 OOXML — 不要回退到渲染图片。仅当 PowerPoint 没有原生形式的图表类型（Sankey、网络、和弦）才以图片形式放入。
- **默认图表渲染为裸图** — 无标题、无数据标签、日期调色板。设置 `showTitle` + `title`、`showValue: true` + `dataLabelPosition`、`chartColors: [...]`（来自你的调色板），并静默边框（`catAxisLabelColor`/`valAxisLabelColor`、`valGridLine: { color, size }`、`catGridLine: { style: "none" }`、单系列时 `showLegend: false`）。
- **在堆叠条形或柱状图表上，`dataLabelPosition` 必须为 `ctr`、`inEnd` 或 `inBase`。** `outEnd` **会损坏文件**。
- **使用 `secondaryValAxis`/`secondaryCatAxis` 的组合系列** 需要在图表选项上同时设置 `valAxes` 和 `catAxes`，各有两条记录。如果不设置，pptxgenjs 会写入从未声明的轴 *id*，而 PowerPoint **会丢弃该图表**并报告文件损坏。只提供 `valAxes` 是不够的。
- **在 `writeFile()` 之后，运行 `python scripts/office/validate.py deck.pptx`。** 它会报告上述两种图表故障以及 PowerPoint 拒绝打开的其他幻灯片 XML 缺陷，并为每个问题注明修复方法。在生成器中修复，而不是手动编辑打包后的 XML。
- **永远不要重新排序 `<p:presentation>` 的子元素。** pptxgenjs 会在 `<p:sldIdLst>` 后立即写入 `<p:notesMasterIdLst>`，并将两个母版都指向同一主题部件。PowerPoint 对此很满意 — 移动该元素会使同一套幻灯片变得无法打开。
- **图标：** 将 `react-icons` 渲染为 SVG（`ReactDOMServer.renderToStaticMarkup`），用 `sharp` 在 ≥256px 处光栅化，并通过 `addImage({ data: "image/png;base64," + buf.toString("base64") })` 插入 — `image/png;base64,` 前缀是必需的（`react-icons`、`react`、`react-dom` 和 `sharp` 已预装 — 若 require 失败则运行 `npm install react-icons react react-dom sharp`）。

## 编辑现有幻灯片套与模板

先选择版式：`python scripts/thumbnail.py template.pptx template-thumbs` 会写出每张幻灯片的标注网格并打印其创建的文件 — `template-thumbs.jpg`，超过 12 张幻灯片时拆分为 `template-thumbs-N.jpg`。**始终传入第二个参数，以幻灯片套名命名。** 默认为 `thumbnails`，因此一个目录下对两套幻灯片进行缩略图处理会静默覆盖彼此的网格 — 第一套幻灯片的会被删掉（仅模板分析 — 视觉 QA 需要 [转换为图片](#converting-to-images) 中的全分辨率渲染；它仅接受 `.pptx`，所以先将 `.potx` 复制为 `.pptx` 文件名）。

```bash
python3 -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall('unpacked')" deck.pptx
python scripts/add_slide.py unpacked/ slide2.xml --after slide2.xml   # 复制幻灯片（或 slideLayoutN.xml）；打印新幻灯片的路径
# 调整 / 删除幻灯片 = 编辑 <p:sldIdLst> 中的元素
python scripts/clean.py unpacked/                                     # 删除后：移除悬空幻灯片、媒体、关系
# 编辑幻灯片内容：编辑 ppt/slides/slideN.xml
(cd unpacked && rm -f ../out.pptx && zip -Xr ../out.pptx .)           # 在目录内部打包；先 rm 或已删除的部分会保留
python scripts/office/validate.py out.pptx --original deck.pptx
```

- **所有结构性工作 — 添加、删除、调整顺序 — 必须在编辑任何幻灯片内容之前完成。** `add_slide.py` 逐字复制幻灯片文件，因此在你编辑后复制会克隆已编辑内容；且 `clean.py` 会删除 `<p:sldIdLst>` 中不存在的幻灯片，包括你刚刚写入的那个。
- **永远不要手动复制幻灯片文件** — `add_slide.py` 会完成新幻灯片所需的所有注册，并报告其产物（`Created ppt/slides/slide17.xml from slide2.xml`）。它也可直接处理文件：`add_slide.py deck.pptx slide2.xml -o out.pptx` — **必须传入 `-o`，否则它会原地重写输入幻灯片套。** 复制的幻灯片仍**引用**其源部分的图表/SmartArt/嵌入对象，而非克隆它们，因此编辑其中一个幻灯片的图表会改变另一个。
- **如果使用 `python-pptx`**，有三件事它不会做到：复制幻灯片（其唯一入口是 `add_slide(layout)`）、通过 `text_frame.text = "..."` 保留格式（那会将段落折叠为单个无样式运行 — 改用 `run.text`）、或读取模板艺术使用的 SVG/EMF（`add_picture` 会引发 `UnidentifiedImageError`）。
- 旧版 `.ppt` 必须先转换：`python scripts/office/soffice.py --headless --convert-to pptx file.ppt`。`.potx` 模板解压与打包方式相同 — 在输出中保留 `.potx` 扩展名。
- 重用模板图标或图片时，复制已包含该图标或图片的幻灯片或版式。

填写模板时：

- 若脚本执行 XML 转换，请使用 `defusedxml.minidom` 解析 — 通过 `xml.etree.ElementTree` 在 OOXML 上往返会重写命名空间前缀并损坏幻灯片套。
- **模板插槽 ≠ 源项目。** 若模板显示 4 名团队成员而你只有 3 名，删除第 4 名成员的整组（图片 + 文本框），而不仅仅是其文本 — 然后检查是否有孤立视觉效果进行 QA。
- 每个列表项一个 `<a:p>` — 切勿将项目拼接进单个段落。复制兄弟 `<a:pPr>` 以保留间距，并在标题、章节标题和行内标签（`Status:`、`Owner:`）的 `<a:rPr>` 上设置 `b="1"`。
- 让 bullets 继承自版式；仅添加 `<a:buChar>`、`<a:buAutoNum>`（编号）或 `<a:buNone>` 以覆盖 — 切勿在文本中使用字面量 `•`。
- 带有前导或尾随空格的文本需要在其 `<a:t>` 上设置 `xml:space="preserve"`。

## 设计思路

**不要创建枯燥的幻灯片。** 白底上只有普通项目符号不会给人留下深刻印象。为每张幻灯片考虑以下清单中的想法。

### 开始之前

- **选择与内容相关的鲜明、内容驱动的调色板：** 调色板应感觉是为 **本主题** 设计的。如果把这些颜色换到完全不同的话题上仍然"适用"，说明你没有选择得足够具体。
- **以主导色优先，而非平均化：** 一种颜色应占据 60-70% 的视觉权重，配 1-2 种辅助色调和一种鲜明的强调色。切勿让所有颜色处于同等权重。
- **明暗对比：** 标题和结论幻灯片用深色背景，内容幻灯片用浅色背景（"三明治"结构）。或全程采用深色以营造高级感。
- **确定视觉主题：** 选取一个独特的元素并贯穿每一张幻灯片 — 圆角图片框、彩色圆圈中的图标。**不要使用色条或强调条作为主题**（见避免清单）。

### 调色板

选择与主题相符的颜色 — 不要默认使用通用蓝色。使用以下调色板作为灵感：

| 主题 | 主色 | 次色 | 强调色 |
|-------|-------|-----------|--------|
| **Midnight Executive** | `1E2761`（海军蓝） | `CADCFC`（冰蓝） | `FFFFFF`（白色） |
| **Forest & Moss** | `2C5F2D`（森林绿） | `97BC62`（苔藓绿） | `F5F5F5`（米色） |
| **Coral Energy** | `F96167`（珊瑚红） | `F9E795`（金色） | `2F3C7E`（海军蓝） |
| **Warm Terracotta** | `B85042`（陶土红） | `E7E8D1`（沙色） | `A7BEAE`（鼠尾草绿） |
| **Ocean Gradient** | `065A82`（深蓝） | `1C7293`（青色） | `21295C`（午夜色） |
| **Charcoal Minimal** | `36454F`（炭灰） | `F2F2F2`（浅灰白） | `212121`（黑色） |
| **Teal Trust** | `028090`（青色） | `00A896`（海绿） | `02C39A`（薄荷绿） |
| **Berry & Cream** | `6D2E46`（莓果红） | `A26769`（灰玫瑰） | `ECE2D0`（米色） |
| **Sage Calm** | `84B59F`（鼠尾草绿） | `69A297`（桉树绿） | `50808E`（石板灰） |
| **Cherry Bold** | `990011`（樱桃红） | `FCF6F5`（浅灰白） | `2F3C7E`（海军蓝） |

### 每张幻灯片

**每张幻灯片都需要一个视觉元素** — 图片、图表、图标或形状。纯文本幻灯片会让人过目即忘。

**版式选项：**
- 两列（左侧文本，右侧插图）
- 图标 + 文本行（图标位于彩色圆圈中，加粗标题，标题下方描述）
- 2×2 或 2×3 网格（一侧图片，另一侧内容块网格）
- 半出血图片（左侧或右侧整边）配内容叠加

**数据展示：**
- 大号统计数字突出（60-72pt 大数字，下方小标签）
- 对比列（前后、优缺点、并排选项）
- 时间线或流程（编号步骤、箭头）

**视觉润色：**
- 章节标题旁配以小彩色圆圈中的图标
- 关键数据或标语使用斜体强调文字

### 排版

**写入 `.pptx` 的字体由用户的 PowerPoint 渲染，而非本环境。** 视觉 QA 通过 LibreOffice 渲染，LibreOffice 会替换它没有的字体 — 某些字体替换后的宽度不同，因此 QA 预览可能显示文本溢出（或适配）而与实际幻灯片不同。为保持 QA 可信：

- **安全字体**（QA *和* 随 Office 一起携带时均按真实宽度渲染）：**Arial、Calibri、Cambria、Times New Roman、Courier New、Bookman Old Style、Century Schoolbook**。用于正文及任何对适配有要求的元素。
- **零 QA 风险的个性标题：** 搭配安全列表中的衬线标题（Cambria、Bookman Old Style、Century Schoolbook）与安全列表中的无衬线正文（Calibri 或 Arial）。获得视觉对比，同时放弃可靠的溢出检查。
- **若用户要求使用安全列表之外的字体**（例如 Georgia 或 Trebuchet MS）：在用户要求的位置使用，但将容器尺寸留出约 10% 的余量，**不要信任**这些元素的 QA 文本适配 — 该字体的预览是近似值。若用户未指定，正文优先使用安全列表字体。
- **QA 不可靠字体**（替换字体宽度不同 — 溢出检查可能错误）：Georgia、Trebuchet MS、Impact、Arial Black、Garamond、Consolas、Palatino Linotype。Calibri Light 替换因环境而异；视为 QA 不可靠。适用于标题/强调，留有余量即可；不要信任这些元素的 QA 文本适配。
- **永远不要默认使用 Aptos** — Office 2023 年后默认字体在此处无度量兼容替换字体，且在旧版 Office 安装中缺失，因此在两端均不可靠。

| 元素 | 尺寸 |
|---------|-------|
| 幻灯片标题 | 36-44pt 粗体 |
| 章节标题 | 20-24pt 粗体 |
| 正文 | 14-16pt |
| 说明文字 | 10-12pt 弱化 |

### 间距

- 0.5" 最小边距
- 内容块之间 0.3-0.5" 间距
- 预留呼吸空间 — 不要填满每一寸

### 避免（常见错误）

- **不要重复相同版式** — 跨幻灯片变化列、卡片和突出显示
- **不要居中正文** — 左对齐段落和列表；仅居中标题
- **不要吝啬尺寸对比** — 标题需 36pt 及以上以从 14-16pt 正文中突出
- **不要默认使用蓝色** — 选择反映特定主题的颜色
- **不要随机混合间距** — 选择 0.3" 或 0.5" 间隙并保持一致使用
- **不要只修改一张幻灯片的样式而让其他保持平淡** — 全程完全投入或保持简洁一致
- **不要创建纯文本幻灯片** — 添加图片、图标、图表或视觉元素；避免仅标题 + 项目符号
- **不要忘记文本框填充** — 当需要对齐线条或形状与文本边缘时，为文本框设置 `margin: 0` 或将形状偏移以补偿填充
- **不要使用低对比度元素** — 图标和文本都需要与背景有强对比；避免浅色文字配浅色背景或深色文字配深色背景
- **绝对不要在使用标题下方使用强调线** — 这是 AI 生成幻灯片的标志；改用留白或背景色
- **绝对不要添加装饰性色条或强调条纹** — 包括：横跨幻灯片宽度的页眉/页脚条、幻灯片一侧的垂直侧边条纹、卡片或内容块边缘的细强调条纹，以及矩形上的"单侧边框"。这些会被视为 AI 生成的填充内容。若要将卡片与背景区分，使用 subtle 背景色调、投影或图标 — 而非边缘条纹。
- **不要默认使用米色/米白背景** — 未指定背景时，使用白色（`FFFFFF`）或用户品牌调色板；避免 `F5F5DC`、`FAF0E6`、`FAEBD7`、`FFF8E1` 等暖中性默认值
- **不要交付超出形状的文本** — 若文本不合适，缩小字号、分到多页或增大容器；切勿留内容被截断或溢出边界

## QA（必需）

首次渲染通常会有几个实际问题 — 重叠、溢出、不对齐。找出并修复，仅重新渲染你修改的幻灯片，然后停止。

### 内容 QA

```bash
markitdown output.pptx
```

检查是否存在缺失内容、拼写错误、顺序错误。

**使用模板时，检查是否存在残留占位符文本：**

```bash
markitdown output.pptx | grep -iE "\bx{3,}\b|lorem|ipsum|\bTODO|\[insert|this.*(page|slide).*layout"
```

若 grep 返回结果，在宣布成功前修复。

### 文件 QA（必需）

```bash
python scripts/office/validate.py output.pptx                      # 从零构建
python scripts/office/validate.py output.pptx --original src.pptx  # 基于模板构建
```

**若幻灯片套来自模板，始终传入 `--original`。** 模板本身可能包含 XSD 拒绝的部件，因此直接运行可能报告从未由你导致的问题 — 而真正的回归可能会混在其中。`--original` 基于模板对模式检查和幻灯片检查进行基准，抑制模板自身已存在的问题。结构检查 — 关系、内容类型、图表 — 忽略 `--original`，因此无论是否有该参数，都会报告模板继承的问题，请单独阅读这些结果。

pptxgenjs 生成的图表 XML 会被 PowerPoint 拒绝打开，且其他工具都能接受：`python-pptx` 能打开这些幻灯片套、LibreOffice 能渲染它们、XSD 能通过它们。每次失败都会注明修复方法。请在生成器中修复并重新构建。

### 视觉 QA

转换为图片以进行视觉检查（见 [转换为图片](#converting-to-images)）并逐一检查。盯着生成代码看时，你倾向于看到自己预期而非实际渲染的结果，因此要**新鲜地**查看图片（若你有子代理，用子代理做此工作效果很好）。需查找的用户可见缺陷：

- **文本溢出或在框或幻灯片边界处被截断 — 首先检查此问题。** 这是最常见的缺陷，且总是用户可见。（对于 QA 中渲染不可靠的字体，预览为近似值：信任你留出的约 10% 余量，而非其表面的适配情况。）
- 元素重叠（文本穿入形状、线条穿过文字、堆叠元素）
- 来源引用或页脚与上方内容碰撞
- 元素间距过近（< 0.3" 间隙）或卡片/章节几乎接触
- 间距不均（某处大片空区，另一处拥挤）
- 距幻灯片边缘间距不足（< 0.5"）
- 列或类似元素不对齐一致
- 低对比度文本（例如，浅灰文字配米色背景）
- 模板装饰在文本替换后位置错位 — 例如，为单行标题定位的标题下划线，但替换后标题换行成两行
- 低对比度图标（例如，深色图标配深色背景且无对比圆圈）
- 文本框过窄导致过度换行
- 残留占位符内容

## 转换为图片

将演示文稿转换为单张幻灯片图片以进行视觉检查：

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
rm -f slide-*.jpg
pdftoppm -jpeg -r 150 output.pdf slide
ls -1 "$PWD"/slide-*.jpg
```

**直接将上方打印的绝对路径作为查看工具参数传入。** `rm` 清除先前运行残留的图片。`pdftoppm` 根据页数进行零填充：10 页以内为 `slide-1.jpg`，10-99 页为 `slide-01.jpg`，100 页及以上为 `slide-001.jpg`。

**修复后，重新运行上述全部四个命令** — PDF 必须从编辑后的 `.pptx` 重新生成，之后 `pdftoppm` 才能反映你的修改。

## 依赖

`pptxgenjs`（npm，已预装 — 仅在 `require('pptxgenjs')` 失败时安装） · `markitdown[pptx]`、`Pillow`、`defusedxml`、`lxml`（pip — 文本转储、缩略图、clean、validate） · LibreOffice（`soffice`，通过 `scripts/office/soffice.py` 为沙盒环境自动配置） · `pdftoppm`（Poppler）
