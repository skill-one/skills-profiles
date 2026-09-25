# 科学可视化

在优化外观之前，构建保留科学意义的图表。将通用原则与过时的出版商规则分开，保留原始数据和转换，冗余使用颜色，并检查交付的文件而不是信任绘图默认值。

## 不可协商的护栏

- 不得修改、隐藏、虚构或选择性增强数据以改善图表。
- 保留原始表格/图像、排除项、缺失值代码、分析代码、归一化、分箱、图像调整和随机种子。
- 不要推断期刊要求。确定目标期刊、文章类型、图表类型和提交阶段；验证其实时官方指南。
- 不要声称调色板、DPI值、格式或自动报告使图表可访问或符合期刊要求。
- 不要在连接缺失观测值、抑制不方便的点、像细节增加一样上采样图像或调整坐标/双坐标以夸大结论的情况下保持沉默。
- 将交互式和静态输出作为不同的交付成果。交互式悬停不是标签、替代文本、键盘访问、可访问数据表或静态回退的替代品。

阅读`references/publication_guidelines.md`以获取欺骗性编码和完整性检查。仅在知道目标和阶段后阅读`references/journal_requirements.md`。

## 工作流程

### 1. 定义证据和目的地

记录：

- 受众和媒介：手稿、网络、幻灯片、海报、补充；
- 精确的出版商/期刊、文章类型、提交阶段和预期最终宽度；
- 变量语义、单位、样本/重复结构、缺失/删失值；
- 估计器和不确定性定义；
- 转换：过滤、聚合、归一化、平滑、分箱、图像处理；
- 源数据路径/标识符和输出可追溯性。

如果要求未知，则创建一个临时的通用图表，并将所有出版商选择标记为待验证。

### 2. 选择诚实的编码

优先考虑在公共尺度上的位置。编码前检查：

- **条形/区域**：通常包括零，因为长度/面积从基线测量。
- **点/线**：非零限制可以是有效的；显示上下文并披露中断。
- **不确定性**：命名SD、SE、CI、百分位数、后验或其他区间；说明`n`和复制单位。
- **原始观测值**：在可行时显示它们；不要让抖动掩盖类别/值。
- **缺失数据**：区分缺失、零、删失和排除；使用间隙或显式模型/插值样式。
- **区域/体积**：缩放区域/体积，而不是半径/直径；避免装饰性3D。
- **对数坐标**：标记基数/转换并声明如何处理零/负值。
- **分箱/平滑**：记录边缘、带宽/窗口、方法和敏感性。
- **归一化**：声明公式/参考，并在比较的面板中保持限制一致。
- **双坐标**：优先选择对齐的面板；如果不可避免，请说明单位并不要人为制造相关性。
- **图像**：保留原始图像，披露整幅图像调整，显示比例尺，并避免裁剪/擦除的背景。

### 3. 在设计时考虑可访问性，而不是事后

- 使用颜色加标记、线样式、阴影、直接标签或面板分隔。
- 根据数据语义选择定性、顺序、发散或循环颜色。
- 在渲染大小审计前景/背景对比度。
- 使缺失和超出范围值明确。
- 提供替代文本、复杂图表的较长描述以及网络交付的底层数据。
- 将WCAG 2.2视为网络指南：正常文本4.5:1，大文本3:1，图形对象理解所需的3:1；颜色不能是唯一的提示。适用性和例外情况很重要。

参见`references/color_palettes.md`。灰度屏幕很有用，但不是完整的色觉或可访问性测试。

### 4. 使用作用域样式实现

使用Matplotlib的面向对象API和临时样式上下文：

```python
import matplotlib.pyplot as plt

from style_presets import style_context

with style_context("default", palette_name="okabe_ito_on_white"):
    fig, ax = plt.subplots(
        figsize=(89 / 25.4, 60 / 25.4),
        layout="constrained",
    )
    ax.plot(x, y, marker="o", label="Observed")
    ax.set(xlabel="Time (hours)", ylabel="Response (unit)")
    ax.legend()
```

`layout="constrained"`支持色条、嵌套GridSpec、子图和`subplot_mosaic`。不要调用`tight_layout()`；它禁用约束布局。

对于精确的物理尺寸，除非更改页面尺寸是故意的，否则不要使用`bbox_inches="tight"`。

#### 颜色归一化

```python
import matplotlib as mpl

norm = mpl.colors.TwoSlopeNorm(vmin=-2, vcenter=0, vmax=5)
cmap = mpl.colormaps["RdBu_r"].with_extremes(bad="#777777")
image = ax.imshow(values, norm=norm, cmap=cmap, interpolation="nearest")
fig.colorbar(image, ax=ax, label="Change (unit)")
```

仅在映射与科学意义匹配时使用`LogNorm`、`CenteredNorm`、`SymLogNorm`、`BoundaryNorm`或`TwoSlopeNorm`。

#### Seaborn

Seaborn 0.13.2使用当前的`errorbar` API：

```python
sns.lineplot(
    data=frame,
    x="time",
    y="response",
    hue="treatment",
    style="treatment",
    markers=True,
    errorbar=("ci", 95),
    n_boot=5000,
    seed=20260723,
    ax=ax,
)
```

轴级函数适合自定义Matplotlib布局；图表级函数创建自己的图表/面。不要像它们是稳定的API一样自定义Seaborn的内部艺术家列表。

#### Plotly

- 使用`write_html()`进行交互，使用`write_image()`/`plotly.io.write_images()`进行静态输出。
- Kaleido 1.3.0需要Chrome/Chromium；它不再捆绑Chrome。
- 当前静态格式：PNG、JPEG、WebP、SVG、PDF。EPS是Kaleido v0-only。
- 不要传递已弃用的`engine=`或使用Orca/`plotly.io.kaleido.scope`。
- `width`、`height`和`scale`控制像素；`scale=3`不是“300 DPI”。
- WebGL轨迹将光栅内容嵌入PDF/SVG。
- 完全离线导出需要在图表引用MathJax/topojson/tiles时使用本地外部资源。

### 5. 明确导出并记录可追溯性

```python
from figure_export import export_figure

report = export_figure(
    fig,
    "outputs/figure1",
    formats=["pdf", "png"],
    dpi=600,
    bbox_inches=None,  # 保留图表页面尺寸
    provenance={
        "raw_data": "data/source.csv",
        "transformations": ["predeclared QC filter", "group mean"],
        "uncertainty": "95% bootstrap CI; seed 20260723",
        "missing_data": "retained as gaps",
    },
    write_manifest=True,
)
```

导出器拒绝隐式覆盖，原子写入，保留嵌入光栅的矢量DPI，使用TIFF LZW，并且可以使用PDF/PS Type 42字体。它不验证科学内容或出版商接受。

对于可编辑字体：

- PDF/PS Type 42嵌入TrueType字体。
- `svg.fonttype="none"`保留文本可编辑/可搜索，但不会嵌入字体；外观取决于安装的字体。
- `svg.fonttype="path"`保留字形外观为路径，但会丢失可编辑/可搜索文本。

使用不透明的明确背景，除非需要透明度；混合到另一个背景会改变明显对比度。

### 6. 检查、比较和审查

1. 检查文件元数据。
2. 审计调色板对比度/灰度分离。
3. 与日期的出版商快照进行比较。
4. 在手稿/网络上下文中以最终大小查看。
5. 手动审查字体、嵌入光栅、裁剪、图例、比例尺、图像完整性、标题、替代文本和源数据。
6. 在上传前立即重新检查目标期刊页面。

## 固定快照

示例和烟雾测试使用截至2026-07-23当前的直接包固定：

```bash
uv run --isolated --no-project --python 3.13 \
  --with "matplotlib==3.11.1" \
  --with "seaborn==0.13.2" \
  --with "plotly==6.9.0" \
  --with "kaleido==1.3.0" \
  --with "pillow==12.3.0" \
  --with "pypdf==6.14.2" \
  python your_figure.py
```

这是一个日期的直接依赖快照，不是传递锁定。使用项目的uv锁定进行精确重放；这项技能有意不提供依赖锁定。

## 嵌套CLI

所有辅助工具都是确定性的、无网络的、有界的、在相关情况下拒绝符号输入/目标，并且除非明确指定`--force`，否则拒绝覆盖。

### 检查光栅/矢量元数据

```bash
uv run --isolated --no-project --python 3.13 \
  --with "pillow==12.3.0" \
  python scripts/image_metadata.py figure.tiff \
  --format tiff --mode RGB --min-dpi 300 --target-width-mm 85 \
  --alpha-policy forbid
```

支持光栅图像（Pillow）、SVG、PDF（pypdf）和EPS/PS。报告尺寸、DPI/有效DPI、模式、alpha、ICC存在、压缩、页面大小和保守的第一页PDF字体资源。它不会检查矢量容器中的每个嵌入光栅。

### 审计调色板对比度和灰度

```bash
uv run --isolated --no-project --python 3.13 \
  python scripts/palette_audit.py \
  --palette okabe_ito_on_white \
  --background FFFFFF \
  --role graphical
```

报告精确的WCAG sRGB对比度以及成对CIE L*灰度筛选。灰度阈值是一个启发式算法，不是标准。

### 规划/屏幕出版商导出

```bash
uv run --isolated --no-project --python 3.13 \
  python scripts/export_plan.py \
  --publisher nature \
  --figure-type combination \
  --width single \
  --phase final
```

添加`--input figure.pdf`以屏幕机器可读属性。配置文件是2026-07-23访问的官方源快照，不是自动合规规则。

### 预览样式

```bash
uv run --isolated --no-project --python 3.13 \
  --with "matplotlib==3.11.1" \
  python scripts/style_preview.py \
  --output outputs/style-preview \
  --style default \
  --palette okabe_ito_on_white \
  --formats png,svg
```

### 检查/写入样式和烟雾测试导出

```bash
uv run --isolated --no-project --python 3.13 \
  python scripts/style_presets.py --list
uv run --isolated --no-project --python 3.13 \
  python scripts/style_presets.py --show nature
uv run --isolated --no-project --python 3.13 \
  --with "matplotlib==3.11.1" \
  python scripts/figure_export.py --demo outputs/export-smoke --manifest
```

## 资产

- `assets/publication.mplstyle`：通用打印起始点。
- `assets/nature.mplstyle`：日期的旗舰Nature视觉起始点，不是合规预设。
- `assets/presentation.mplstyle`：较大的投影显示样式。
- `assets/color_palettes.py`：可导入的Okabe-Ito和Paul Tol值及其元数据。
- `assets/publisher_profiles.json`：日期的机器可读规划快照。

Matplotlib样式文件在十六进制颜色中省略`#`，因为`#`在`.mplstyle`解析中开始注释。

## 参考文献

- `references/publication_guidelines.md`：完整性、欺骗性编码、可访问性、静态/交互式输出。
- `references/color_palettes.md`：调色板语义、精确值、WCAG对比度、灰度注意事项、颜色管理。
- `references/journal_requirements.md`：特定阶段的官方出版商快照。
- `references/matplotlib_examples.md`：当前可运行的Matplotlib/Seaborn/Plotly模式。
- `references/sources.md`：官方URL、日期、版本和研究基础。

## 最终审查清单

- [ ] 保留原始数据/图像和转换代码。
- [ ] 明确缺失值、排除项、分箱、归一化和不确定性。
- [ ] 基线、尺度、限制和区域/体积编码是诚实的。
- [ ] 颜色是冗余的，渲染对比度已审查。
- [ ] 图表在适用时有可访问的描述/数据替代方案。
- [ ] 检查导出后的物理尺寸、DPI、格式、字体、透明度和文件大小。
- [ ] 验证了精确的期刊和阶段的出版商规则。
- [ ] 没有将自动报告作为科学、可访问性或合规认证呈现。
