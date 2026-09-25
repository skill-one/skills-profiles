# LaTeX研究海报

## 概述

研究海报是科学交流中至关重要的媒介，适用于会议、研讨会和学术活动。这项技能提供全面的指导，帮助您使用LaTeX包创建专业且视觉吸引人的研究海报。生成具有适当布局、排版、配色方案和视觉层次结构的出版物质量海报。

## 何时使用此技能

当您需要：
- 为会议、研讨会或海报展示会创建研究海报
- 为大学活动或论文答辩设计学术海报
- 准备用于公众参与的研究可视化总结
- 将科学论文转换为海报格式
- 为研究小组或部门创建模板海报
- 设计符合特定会议尺寸要求的海报（A0、A1、36×48英寸等）
- 创建具有复杂多列布局的海报
- 在海报格式中整合图表、表格、公式和引用

## AI驱动的视觉元素生成

**标准工作流程：在创建LaTeX海报之前，使用AI生成所有主要视觉元素。**

这是创建视觉引人注目的海报的推荐方法：
1. 规划所有需要的视觉元素（标题、引言、方法、结果、结论）
2. 使用scientific-schematics或Nano Banana Pro生成每个元素
3. 在LaTeX模板中组装生成的图像
4. 在视觉元素周围添加文本内容

**目标：海报60-70%的区域应为AI生成的视觉元素，30-40%为文本。**

---

### 严格限制（不可超出）

这些是限制，不是指导方针。违反它们是导致海报失败的最常见原因。详细的推理、按图形类型划分的表格和示例在
[references/ai_graphics_for_posters.md](references/ai_graphics_for_posters.md) 中。

| 限制 | 限制 |
| --- | --- |
| 每个AI生成图形的元素数量 | **最多3-4个**（理想情况为3个） |
| 每个图形的单词数量 | **最多10个** |
| 每个图形的空白区域 | **至少50%**（60%更好） |
| 关键数字/指标 | **120pt+** |
| 标签 | **80pt+** |
| 海报上的正文 | **24pt+** |
| 内容区域（A0） | **最多5-6个** |
| 海报上的总单词数 | **300-800** |
| 图形宽度 | `0.85\linewidth`，永远不要使用 `1.0` |

每个图形提示必须包含：`POSTER FORMAT for A0`、明确的元素或单词数量（`ONLY 3 icons`，`3 words total`）、字体大小（`GIANT (120pt+)`）、`60% white space` 和观看距离（`readable from 10-12 feet`）。

**两个强制审查关卡。** 跳过任何一个都可能导致海报难以阅读：

- **生成之前** — 确认每个计划的图形包含3-4个元素、一条信息，少于10个单词，并且不是5个或更多步骤的工作流程。如果不是，请将其拆分为多个图形。
- **生成之后、组装之前** — 在25%缩放下打开每个图形。所有文本可读，4个或更少的元素，50%+的空白区域，2秒内可理解。任何失败都意味着重新生成或拆分。不要从失败的图形中组装海报。

总是失败的模式：`7-stage workflow`、`带有年度里程碑的时间线`、`一个图形中包含3个案例研究`、`比较5+种方法`、`包含所有层的架构`。将每个模式压缩为3个高级项目，或制作多个单独的图形。

**溢出是错误，不是警告。** 编译后，运行 `grep -i overfull poster.log` 并在100%缩放下检查所有四条边。参见
[references/compilation_and_quality_control.md](references/compilation_and_quality_control.md)。

## 科学示意图集成

有关创建示意图的详细指导，请参阅 **scientific-schematics** 技能文档。

**主要功能：**
- Nano Banana Pro自动生成、审查和改进图表
- 创建具有正确格式的出版物质量图像
- 确保可访问性（对色盲友好，高对比度）
- 支持复杂图形的迭代改进

---

## 核心功能

支持三种海报包——**beamerposter**（Beamer语法、机构主题）、**tikzposter**（现代、多彩、灵活）和**baposter**（结构化多列）。包比较、布局和网格系统、设计原则、标准尺寸、每个包的模板、图形和图像集成、配色方案、排版和二维码都在
[references/latex_poster_reference.md](references/latex_poster_reference.md) 中记录。

可重用的每节内容模式、可访问性要求和演示日指导在
[references/poster_patterns_and_presentation.md](references/poster_patterns_and_presentation.md) 中。

## 海报创建工作流程

### 阶段1：规划和内容开发

1. **确定海报要求**：
   - 会议尺寸规格（A0、36×48英寸等）
   - 方向（纵向与横向）
   - 提交截止日期和格式要求

2. **开发内容大纲**：
   - 确定核心信息1-3个
   - 选择关键图形（通常3-6个主要视觉）
   - 为每个部分起草简洁的文本（推荐使用项目符号）
   - 目标为300-800个单词

3. **选择LaTeX包**：
   - beamerposter：如果熟悉Beamer，需要机构主题
   - tikzposter：用于现代、多彩且灵活的设计
   - baposter：用于结构化、专业的多列布局

### 阶段2：生成视觉元素（AI驱动）

**关键点：生成简单的图形，内容最少。每个图形=一条信息。**

**内容限制：**
- 每个图形最多4-5个元素
- 每个图形最多15个单词
- 至少50%的空白区域
- 巨大的字体（标签80pt+，关键数字120pt+）

1. **创建图形目录**：
   ```bash
   mkdir -p figures
   ```

2. **生成简单的视觉元素**：
   ```bash
   # 引言 - 仅3个图标/元素
   python scripts/generate_schematic.py "POSTER FORMAT for A0. SIMPLE visual with ONLY 3 elements: [icon1] [icon2] [icon3]. ONE word labels (80pt+). 50% white space. Readable from 8 feet." -o figures/intro.png
   
   # 方法 - 最多4个步骤
   python scripts/generate_schematic.py "POSTER FORMAT for A0. SIMPLE flowchart with ONLY 4 boxes: STEP1 → STEP2 → STEP3 → STEP4. GIANT labels (100pt+). 50% white space. NO sub-steps." -o figures/methods.png
   
   # 结果 - 仅3个条形/比较
   python scripts/generate_schematic.py "POSTER FORMAT for A0. SIMPLE chart with ONLY 3 bars. GIANT percentages ON bars (120pt+). NO axis, NO legend. 50% white space." -o figures/results.png
   
   # 结论 - 精确3个项目，巨大数字
   python scripts/generate_schematic.py "POSTER FORMAT for A0. EXACTLY 3 key findings: '[NUMBER]' (150pt) '[LABEL]' (60pt) for each. 50% white space. NO other text." -o figures/conclusions.png
   ```

3. **审查生成的图形 - 检查溢出：**
   - **在25%缩放下查看**：所有文本仍然可读吗？
   - **计数元素**：超过5个？→ 重新生成更简单的
   - **检查空白区域**：少于40%？→ 在提示中添加 "60% white space"
   - **字体太小？**：添加 "EVEN LARGER" 或增加pt大小
   - **仍然溢出？**：减少为3个元素而不是4-5个

### 阶段3：设计和布局

1. **选择或创建模板**：
   - 从 `assets/` 中的提供模板开始
   - 自定义配色方案以匹配品牌
   - 配置页面大小和方向

2. **设计布局结构**：
   - 规划列结构（2、3或4列）
   - 规划内容流（通常从左到右，从上到下）
   - 为标题分配空间（10-15%）、内容（70-80%）、页脚（5-10%）

3. **设置排版**：
   - 配置不同层级级别的字体大小
   - 确保24pt以上的正文最小字体
   - 测试从4-6英尺的距离的可读性

### 阶段4：内容集成

1. **创建海报标题**：
   - 标题（简洁、描述性、10-15个单词）
   - 作者和所属机构
   - 机构标志（高分辨率）
   - 如果需要，会议标志

2. **集成AI生成的图形**：
   - 将所有来自阶段2的图形添加到适当的部分
   - 使用 `\includegraphics` 进行适当的大小调整
   - 确保图形主导每个部分（视觉元素优先，文本其次）
   - 在块中居中图形以增强视觉冲击力

3. **添加最小的支持性文本**：
   - 保持文本最小且可扫描（总共300-800个单词）
   - 使用项目符号，而不是段落
   - 使用主动语态
   - 文本应补充图形，而不是重复图形

4. **添加补充元素**：
   - 用于补充材料的二维码
   - 参考文献（仅引用关键论文，典型5-10篇）
   - 联系信息和致谢

### 阶段5：改进和测试

1. **审查和迭代**：
   - 检查拼写和错误
   - 验证所有图形都是高分辨率的
   - 确保格式一致
   - 确认配色方案协调

2. **测试可读性**：
   - 在25%比例下打印并从2-3英尺处阅读（模拟从8-12英尺处阅读海报）
   - 在不同显示器上检查颜色
   - 验证二维码功能正常
   - 请同事审查

3. **优化打印**：
   - 将所有字体嵌入PDF
   - 验证图像分辨率
   - 检查PDF大小要求
   - 如果需要，包含出血区域

### 阶段6：编译和交付

1. **编译最终PDF**：
   ```bash
   pdflatex poster.tex
   # 或为更好的字体支持：
   lualatex poster.tex
   ```

2. **验证输出质量**：
   - 检查所有元素是否可见且位置正确
   - 在100%缩放下检查图形质量
   - 验证颜色符合预期
   - 确认PDF在不同查看器中正确打开

3. **准备打印**：
   - 如果需要，导出为PDF/X-1a
   - 保存备份副本
   - 首先在普通纸上打印测试
   - 在截止日期前2-3天订购专业打印

4. **创建补充材料**：
   - 保存PNG/JPG版本用于社交媒体
   - 创建传单版本（8.5×11英寸摘要）
   - 准备用于通过电子邮件共享的数字版本

## 与其他技能的集成

此技能与以下技能有效集成：
- **Scientific Schematics**：关键——用于生成所有海报图形和流程图
- **Generate Image / Nano Banana Pro**：用于风格化图形、概念插图和总结视觉
- **Scientific Writing**：用于从论文中开发海报内容
- **Literature Review**：用于 contextualizing 研究
- **Data Analysis**：用于创建结果图形和图表

**推荐工作流程**：始终在创建LaTeX海报之前使用 scientific-schematics 和 generate-image 技能生成所有视觉元素。

## 常见陷阱避免

**AI生成图形错误（最常见）：**
- ❌ 一个图形中元素过多（10+个）→ 最多保留3-5个
- ❌ AI图形中的文字太小 → 指定 "GIANT (100pt+)" 或 "HUGE (150pt+)"
- ❌ 提示中细节过多 → 使用 "SIMPLE" 和 "ONLY X elements"
- ❌ 未指定空白区域 → 在每个提示中添加 "50% white space"
- ❌ 复杂流程图8+步 → 最多4-5步
- ❌ 比较图表6+项 → 最多3项
- ❌ 关键发现5+指标 → 仅显示前3个

**修复AI图形溢出：**
如果您的AI生成图形溢出或文字太小：
1. 在提示中添加 "SIMPLER" 或 "ONLY 3 elements"
2. 增加字体大小： "150pt+" 而不是 "80pt+"
3. 添加 "60% white space" 而不是 "50%"
4. 移除子细节： "NO sub-steps", "NO axis labels", "NO legend"
5. 重新生成，元素更少

**设计错误：**
- ❌ 文字过多（超过1000个单词）
- ❌ 字体太小（正文小于24pt）
- ❌ 低对比度配色方案
- ❌ 杂乱的布局，无空白区域
- ❌ 各部分风格不一致
- ❌ 图像质量差或像素化

**内容错误：**
- ❌ 没有清晰的故事或信息
- ❌ 研究问题或目标过多
- ❌ 过度使用术语，无定义
- ❌ 结果缺乏背景或解释
- ❌ 缺少作者联系信息

**技术错误：**
- ❌ 会议要求尺寸错误
- ❌ RGB颜色发送给CMYK打印机（颜色偏移）
- ❌ 字体未嵌入PDF
- ❌ 文件大小太大，无法通过提交门户
- ❌ 二维码太小或未测试

**最佳实践：**
- ✅ 生成简单的AI图形，最多3-5个元素
- ✅ 使用巨大的字体（100pt+）用于图形中的关键数字
- ✅ 每个AI提示指定 "50% white space"
- ✅ 精确遵循会议尺寸规格
- ✅ 在最终打印前在缩放比例下打印测试
- ✅ 使用高对比度、可访问的配色方案
- ✅ 保持文本最小且高度可扫描
- ✅ 包含清晰的联系信息和二维码
- ✅ 仔细校对（错误在海报上会被放大！）

## 包安装

确保安装了所需的LaTeX包：

```bash
# 对于TeX Live（Linux/Mac）
tlmgr install beamerposter tikzposter baposter

# 对于MiKTeX（Windows）
# 包通常在首次使用时自动安装

# 其他推荐包
tlmgr install qrcode graphics xcolor tcolorbox subcaption
```

## 脚本和自动化

在 `scripts/` 目录中提供辅助脚本：

- `review_poster.sh`：海报审查和验证
- `generate_schematic.py`：生成科学图表和示意图

## 参考文献

- [references/ai_graphics_for_posters.md](references/ai_graphics_for_posters.md)：完整的AI图形规则、按类型限制、提示示例和审查关卡。
- [references/latex_poster_reference.md](references/latex_poster_reference.md)：包、布局、设计、尺寸、模板、图形、配色方案、排版、二维码。
- [references/compilation_and_quality_control.md](references/compilation_and_quality_control.md)：编译引擎和完整的预打印质量控制程序。
- [references/poster_patterns_and_presentation.md](references/poster_patterns_and_presentation.md)：内容模式、可访问性、演示技巧。
- [references/latex_poster_packages.md](references/latex_poster_packages.md)：beamerposter、tikzposter和baposter的详细比较和示例。
- [references/poster_layout_design.md](references/poster_layout_design.md)：布局原则、网格系统和视觉流。
- [references/poster_design_principles.md](references/poster_design_principles.md)：排版、色彩理论、视觉层次结构和可访问性。
- [references/poster_content_guide.md](references/poster_content_guide.md)：内容组织、写作风格和各部分指导。

## 模板

`assets/` 目录中提供可即用海报模板：

- beamerposter模板（经典、现代、多彩）
- tikzposter模板（默认、射线、波浪、信封）
- baposter模板（纵向、横向、简约）
- 各学科示例海报
- 配色方案定义和机构模板

加载这些模板并根据您的研究和会议要求进行自定义。
