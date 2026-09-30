---
name: pptx-html-fidelity-audit
description: 对 python-pptx 导出的内容进行审计，并与源 HTML 幻灯片进行对比，识别布局/内容差异（页脚溢出、内容被裁剪、斜体/强调格式丢失、样式丢失、间距错乱），并使用严格的页脚轨道 + 光标流布局规范重新导出。当用户有从 HTML 幻灯片生成的 .pptx 文件并要求对比/审计/验证/修复导出内容时，使用此技能——包括类似“比较 PPT 与 HTML”、“保真度审计”、“修复 PPTX”、“PPT 被裁剪”、“页脚重叠”、“PPTX 中缺少斜体”、“重新导出套件”、“PPTX-HTML-保真度审计”等请求，或任何需要验证或修复 python-pptx → HTML 轮换的场景。此外，当用户同时展示 deck.html 和 deck.pptx 并调试视觉差异时，也触发该技能。
---

# PPTX ↔ HTML 精度审计

一种可重复的工作流程，用于捕捉 `python-pptx` 导出在 HTML 源中无声漂移的方式，并通过一种布局规范来修复这些问题，以防止在下次传递中再次出现相同的回归。

## 该技能适用场景

用户拥有：

- 一个源 HTML 幻灯片演示文稿（通常是一个包含 `<section class="slide">` 块的单文件演示文稿）：

  ```html
  <section class="slide light">
    <div class="chrome">2026 · Q2 review</div>
    <span class="kicker">Pillar 03</span>
    <h2 class="h-xl">Shipping <em>velocity</em> doubled</h2>
    <p class="lead">…</p>
    <div class="foot">page 5 / 14</div>
  </section>
  ```

- 通过 python-pptx（或类似工具）从该演示文稿生成的 PPTX 文件。
- 对 PPTX 与 HTML 不匹配的怀疑（或可见证据），例如文本溢出到页脚、斜体字变得扁平、英雄幻灯片未居中、部分内容被裁剪、标签样式丢失。

如果用户只有这两种工件中的*一种*，则此技能尚不适用——首先生成缺失的一种，或要求用户提供。

## 为什么这很困难（以及为什么技能能帮助）

PPTX 是一个固定画布、绝对定位的媒介。HTML 是一个流式、基于布局的媒介。naive 的 python-pptx 导出将每个块固定在手动选择的 `(top, left)` 坐标上，这对于它是测试的第一个幻灯片有效，但对于其他内容高度不同的幻灯片则无声失败。结果是最常见的漂移模式：

1. **页脚溢出** — 内容的 `top + height` 越过了页脚行。
2. **画布外内容** — 最后一个块的底部超出 `7.5"`（16:9 画布）。
3. **斜体丢失** — HTML 中的 `<em>` 从未获得 `run.font.italic = True`。
4. **英雄幻灯片未居中** — 垂直堆叠的幻灯片使用 `MARGIN_TOP` 而不是计算中心。
5. **框边界侵入** — 文本可以适应，但*形状的边界框*过大，在视觉上越过了轨道。
6. **标签/样式丢失** — 带有颜色的 chrome 行、kicker 大写间距、衬线与无衬线字体的分配无声地回退到默认值。

这些问题中的每一个都是一个*布局规范*问题，而不是内容问题。一旦你采用规范，它们就会停止发生。

---

## 工作流程

审计分为五个步骤。不要跳过任何步骤——只有当审计产生一个真实的问题列表来驱动重新导出时，规范才有效。没有审计的修复过程往往会留下半个问题。

### 第 1 步 — 从 PPTX 提取真实情况

运行 `scripts/extract_pptx.py <path-to.pptx> > pptx_dump.json`。脚本遍历每个幻灯片上的每个形状，并导出文本、位置 (`top` / `left`)、大小 (`width` / `height`) 和每次运行时的排版（字体名称、大小 pt、粗体、斜体、颜色）。这是导出的*实际*状态——不要相信导出脚本的意图，要相信转储。

对于 14 张幻灯片的演示文稿，转储的大小约为 30–60 KB，并且是人类可读的。

### 第 2 步 — 遍历 HTML 结构

读取源 HTML 并枚举 `<section class="slide">` 块。对于每个块，注意：

- 幻灯片的主题 (`light` / `dark` / `hero light` / `hero dark`)。
- `chrome` 行文本（顶部元数据）。
- `kicker`（标题上方的小写大写眉毛）。
- 标题（h-hero / h-xl / 等）和任何副标题。
- 正文内容和任何结构化块（流程步骤、卡片、支柱、观察卡片）。
- `foot` 行（底部元数据）。
- 任何 `<em>` 或斜体样式的 span——斜体是无声回归。

将每个 HTML 幻灯片映射到 PPTX 幻灯片索引。对于遵循“幻灯片 1 = 封面，幻灯片 N = 结束”约定的演示文稿，映射是位置性的。

### 第 3 步 — 构建审计表

对于每个幻灯片，遍历转储中的形状并检查是否符合预期的布局规则。使用此精确的表格格式——严重性列决定了修复的优先级：

```
| 幻灯片 | 问题 | 严重性 |
|---|---|---|
| 1 cover | meta-row 底端 6.95" 覆盖 footer (6.7") | 🔴 |
| 5 checklist | row B 步骤描述底端 7.2" 切到 footer | 🔴 |
| 8 3E | 收束段落直接坐在 footer 起点 | 🔴 |
| 9 on-day | step 描述底端刚好碰 footer，无安全距 | 🟠 |
| 多处 | em (Playfair italic) 未保留 | 🟡 |
```

严重性标准：

- 🔴 **严重** — 内容被裁剪、文本不可见、页脚重叠、画布外。必须修复。
- 🟠 **高** — 内容可见但视觉层次结构破坏、无呼吸空间、英雄未居中。应修复。
- 🟡 **中等** — 斜体/em 丢失、字体回退错误、颜色漂移。在此传递中修复。
- 🟢 **低** — 轻微的间距/对齐、亚像素偏移。记录但不要阻止。

表格后，写一个简短的根因部分：90% 的问题通常来自 2–3 个系统性原因（例如“未强制执行页脚轨道”、“英雄堆叠固定在 MARGIN_TOP 而不是居中”、“斜体从未传播”）。命名系统性原因会使重新导出脚本更小且更正确。

### 第 4 步 — 使用页脚轨道 + 光标流布局规范重新导出

这是承重技术。参见 `references/layout-discipline.md` 获取完整规则；摘要：

**在开始时一次定义整个演示文稿的轨道：**

```python
from pptx.util import Inches

CANVAS_W       = Inches(13.333)   # 16:9
CANVAS_H       = Inches(7.5)
MARGIN_X       = Inches(0.6)
MARGIN_TOP     = Inches(0.5)
CONTENT_MAX_Y  = Inches(6.70)     # 内容区域中的任何内容都不能跨越此线
FOOTER_TOP     = Inches(6.85)     # 页脚行固定在此处，边缘对齐
```

> **自定义轨道。** 上述默认值适用于 16:9 画布和细页脚。如果您的设计系统使用更宽的页脚或 4:3 画布，请在导出脚本中覆盖这些常量，并通过 `--content-max-y` / `--canvas-h` / `--canvas-w` 将相同的值传递给 `verify_layout.py`。参见 `references/layout-discipline.md` §1 获取完整常量表。

**使用光标而不是固定每个块在绝对 y 位置的内容块：**

```python
class Cursor:
    """沿幻灯片向下移动；拒绝跨越页脚轨道。"""
    def __init__(self, y_start, cap=CONTENT_MAX_Y):
        self.y = y_start
        self.cap = cap
    def take(self, h, gap=Inches(0.12)):  # ~1 行空白，14pt；根据设计系统调整/收紧
        top = self.y
        self.y = top + h + gap
        if self.y > self.cap:
            raise OverflowError(
                f"cursor at {self.y} exceeds footer rail {self.cap}; "
                f"reduce block height or split slide"
            )
        return top
```

对于每个幻灯片，实例化 `Cursor(MARGIN_TOP)` 并对按阅读顺序的每个块调用 `take(height)`。如果任何块会跨越轨道，幻灯片将拒绝渲染，因此溢出会变成响亮的构建错误，而不是无声的视觉错误。

**英雄（垂直居中）幻灯片使用预算而不是光标：**

```python
def hero_layout(blocks):
    """blocks = 按阅读顺序的 (height, gap_after) 元组列表。"""
    total = sum(h + g for h, g in blocks)
    y_start = (CANVAS_H - total) / 2
    return Cursor(y_start)
```

这一改变解决了“英雄幻灯片内容粘在顶部”的最常见英雄缺陷。

**将框高度紧缩以适应文本+最小填充。** PowerPoint 在形状重叠时会显示形状边界（选择环、Z-顺序冲突），并且过大的框即使在内部文本没有溢出时也会在视觉上跨越页脚轨道。根据文本指标+~0.05" 填充计算框高度，而不是从慷慨的包装器计算。

**明确保留斜体 / em：**

```python
def add_run(p, text, font, size_pt, italic=False, bold=False, color=None):
    r = p.add_run()
    r.text = text
    r.font.name = font
    r.font.size = Pt(size_pt)
    r.font.italic = italic
    r.font.bold = bold
    if color:
        r.font.color.rgb = color
    return r
```

在遍历 HTML 时，检测 `<em>` / `<i>` / 内联样式 `font-style: italic` 并传递 `italic=True`。使用 EN 衬线字体（Playfair Display、Source Serif 或回退到 Georgia）来显示斜体文本——CJK 衬线通常没有斜体，如果尝试斜体化它，看起来会损坏。

对于布局轨道无法捕获的更深层次的字体问题——变字体陷阱，PowerPoint 无声地切换到 Calibri / Microsoft JhengHei，缺少 `<a:ea>` 插槽导致 CJK 运行回退，汉字的假斜体——请阅读 `references/font-discipline.md`。那里的五层覆盖了 `verify_layout.py` 无法看到的一切。

### 第 5 步 — 导出后验证

在写入新的 `.pptx` 后，运行 `scripts/verify_layout.py <path-to.pptx>`。脚本：

- 遍历每个幻灯片上的每个形状。
- 断言内容形状的 `top + height ≤ CONTENT_MAX_Y`（页脚/页码形状允许在轨道下方）。
- 断言所有形状的 `top + height ≤ CANVAS_H`（无画布外）。
- 断言 `left + width ≤ CANVAS_W` 和 `left ≥ 0`。
- 报告违规为单个块：幻灯片索引、形状名称、观察到的底部、轨道。

零违规是“此重新导出可发布”的门槛。不要声称审计已修复，除非运行验证器——人眼会忽略 1–2 mm 的溢出，而脚本不会。

---

## 输出到用户

在步骤 5 通过后，报告：

1. **审计表** — 步骤 3 的表格。
2. **根因** — 1 段关于系统性解释的段落。
3. **修复列表** — 简洁的列表，说明更改了什么以及为什么（例如，“英雄幻灯片切换到预算居中”，“所有内容块通过 Cursor 路由”，“em 运行明确斜体”）。
4. **验证** — “N 张幻灯片 0 轨道违规，文件大小 X KB”。
5. **路径** — 重新导出 `.pptx` 的绝对路径。

用户阅读的原因有两个：确认可见错误已修复，并信任系统性修复是正确的。两者都要覆盖。

---

## 预装资源

- `scripts/extract_pptx.py` — 将每个幻灯片上的每个形状作为 JSON 转储。在审计之前运行。**重要：** 还要在*原始*导出上运行以比较，以及在*重新导出*上运行以确认。
- `scripts/verify_layout.py` — 导出后轨道检查器。在违规时返回非零退出码，因此如果需要，它可以嵌入到 CI 管道中。
- `references/layout-discipline.md` — 完整的页脚轨道 + 光标流规则集，每个常见幻灯片类型（英雄、内容、流程、两列、观察网格）的代码片段。
- `references/font-discipline.md` — 五层字体审计：映射、存在、变字体与静态陷阱、三个 XML 语言插槽（`latin` / `ea` / `cs`）、CJK 与拉丁斜体交互。
- `references/audit-table-template.md` — 可复制粘贴的表格模板，包含严重性图例。

在以下情况下阅读参考：

- 演示文稿包含技能.md 覆盖范围之外的幻灯片类型（多列仪表板、嵌入图像、图表）→ `layout-discipline.md`。
- 审计显示 🟡 字体问题——斜体丢失、CJK 回退、XML 中出现意外的 `Calibri` / `Microsoft JhengHei` → `font-discipline.md`。
- 您想将审计表直接放入报告或 markdown 交付物 → `audit-table-template.md`。

---

## 需要避免的反模式

- **在不命名系统性原因的情况下单独修复单个幻灯片。** 如果您通过将幻灯片 5 的块降低 0.2" 来修复它，您很快就会回到修复幻灯片 9、11 和 14。找到导致所有四个问题的规则。
- **信任原始导出脚本的意图。** 始终对实际文件运行提取器。意图与现实之间的漂移是错误。
- **因为“PowerPoint 预览看起来很好”而跳过验证。** 预览抗锯齿隐藏了 1–2 mm 的溢出。脚本不会。
- **在没有任何斜体传统的脚本中斜体化。** CJK、阿拉伯语、希伯来语、天城文、泰语和高棉语在强制 `italic=True` 时都会产生合成倾斜，结果看起来机械变形。仅对主要脚本支持斜体的运行进行斜体化——拉丁语、西里尔语、希腊语。参见 `references/font-discipline.md` Layer 5 获取实现模式。
- **使用 `MARGIN_TOP` 对英雄幻灯片。** 英雄幻灯片需要*预算居中*，而不是顶部锚定。这是最常见的英雄缺陷，也是最容易修复的。

---

## 为什么基于几何验证，而不是视觉差异

此技能的早期版本依赖于视觉差异——通过 Keynote 渲染 .pptx → PDF → PNG，通过 Chrome 无头模式截图 HTML，使用 `magick` 并排拼接。它有效，但有三个尖锐的缺点：

- **平台锁定。** Keynote AppleScript 仅限 macOS；`magick` 和字体发现命令跨操作系统不同；Linux 上的 CI 管道无法重现该链。
- **不精确。** 1-2 mm 的溢出会在 PNG 预览中通过抗锯齿隐藏。人眼会忽略它；脚本会作为硬数字违规捕获它。
- **设置成本。** 每个贡献者都需要在能够审计之前安装完整的图形工具链。几何检查只需要 `python-pptx`。

基于几何的验证放弃了视觉差异擅长的一件事：捕获形状位置正确但渲染的字符看起来错误的情况（字体回退、字距错误、缺失的粗细）。当出现这种情况时，回退到手动截图审查——`references/font-discipline.md` 中的五层审计涵盖了大多数潜在原因。
